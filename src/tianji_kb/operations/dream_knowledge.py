"""Research-only cultural scene retrieval, using the existing reviewed model/RAG."""
import hashlib
import json
import re

from ..knowledge_index import iter_phase1_chunks
from ..rag_context import verified_reviewed_index, ref_key, RetrievalUnavailable
from ..resolver import EvidenceResolver, ROOT

VARIANT = 'traditional_chinese_dream'
_UNRESOLVED_NARRATION = re.compile(
    r'没有|没|不曾|未曾|并未|不是|差点|险些|好像|似乎|可能|如果|假如|听说|说|电影|小说')


def retrieve(dream_text, *, variant=VARIANT, root=ROOT):
    if variant != VARIANT:
        raise ValueError('Modern psychology and other dream variants are not reviewed')
    if not isinstance(dream_text, str) or not dream_text.strip():
        raise ValueError('Expected a nonempty dream narrative')
    resolver = EvidenceResolver(root)
    policy = resolver.entities['dream.concept.traditional_variant_v1'][1]['attributes']
    index = verified_reviewed_index(resolver)
    trusted = {row['id']: row for row in iter_phase1_chunks(resolver.root, resolver.model)
               if row['metadata']['domain'] == 'dream'}
    clauses = re.split(r'[，,。.!！？?；;\n]', dream_text)
    entities, candidates, evidence, retrieved = [], [], {}, []
    for term_id in policy['reviewed_term_ids']:
        collection, term = resolver.entities[term_id]
        attrs = term['attributes']
        if collection != 'terms' or term['domain'] != 'dream' or term['variant'] != variant:
            raise RetrievalUnavailable('Unreviewed dream term variant')
        aliases = list(dict.fromkeys(attrs['entity_aliases'] + attrs['scene_aliases']))
        mentions = [alias for alias in aliases if alias in dream_text]
        if mentions:
            entities.append({'term_id': term_id, 'symbol': attrs['symbol'],
                             'entity': attrs['entity'], 'mentions': mentions,
                             'status': 'literal_mentions_only'})
        scene_hits = [alias for alias in attrs['scene_aliases']
                      if any(alias in clause and not _UNRESOLVED_NARRATION.search(clause)
                             for clause in clauses)]
        if not scene_hits:
            continue
        rule = resolver.rule(attrs['rule_id'])
        if rule['domain'] != 'dream' or rule['variant'] != variant or term_id not in rule['term_refs']:
            raise RetrievalUnavailable('Unreviewed scene-to-rule relationship')
        if (rule['result']['interpretation_candidate'] != attrs['interpretation']
                or rule['result']['interpretation_type'] != variant
                or rule['result']['personal_prediction'] is not False):
            raise RetrievalUnavailable('Dream candidate differs from reviewed cultural rule')
        rows = index.search(term['name'], domain='dream', topic='knowledge_term', limit=40)
        row = next((r for r in rows if r['metadata'].get('entity_id') == term_id), None)
        if row is None:
            continue
        if {key: row[key] for key in ('id', 'text', 'metadata')} != trusted.get(row['id']):
            raise RetrievalUnavailable('Dream retrieval differs from reviewed Canonical term')
        refs = resolver.resolve(rule['id'], variant)
        if {ref_key(r) for r in refs} != {ref_key(r) for r in row['metadata']['source_refs']}:
            raise RetrievalUnavailable('Dream scene evidence does not match reviewed retrieval')
        ids = []
        for ref in refs:
            eid = hashlib.sha256(json.dumps(ref, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
            evidence[eid] = ref
            ids.append(eid)
        candidates.append({'term_id': term_id, 'symbol': attrs['symbol'], 'scene': attrs['scene'],
                           'scene_alias_hits': scene_hits, 'rule_id': rule['id'],
                           'match_kind': 'reviewed_cultural_scene_retrieval',
                           **{key: attrs[key] for key in ('source', 'locator', 'original_text_short_quote',
                               'interpretation', 'interpretation_type', 'limitations', 'confidence', 'cultural_context')},
                           'evidence_level': row['metadata']['evidence_level'], 'evidence_ids': ids,
                           'personal_prediction': False})
        retrieved.append({'id': row['id'], 'entity_id': term_id,
                          'canonical_path': row['metadata']['canonical_path'], 'evidence_ids': ids})
    return {'domain': 'dream', 'variant': variant, 'mode': 'research',
            'status': 'reviewed_interpretation_candidates' if candidates else 'no_reviewed_interpretation',
            'entities': entities, 'interpretation_candidates': candidates,
            'evidence': evidence, 'retrieval': retrieved,
            'retrieval_method': 'literal_scene_alias_and_reviewed_rag',
            'chart_generated': False, 'public_enabled': False, 'ai_enabled': False,
            'limitations': ['仅审核五个具体传统梦场景；字面识别不是完整自然语言理解。',
                            '否定、假设、间接叙述或语义不清时保守不采纳；同一实体不等于同一梦义。',
                            '未命中返回 no_reviewed_interpretation，不调用 LLM；文化解释不证明现实预测。']}
