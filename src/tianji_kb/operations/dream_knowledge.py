"""Research-only cultural scene retrieval, using the existing reviewed model/RAG."""
import hashlib
import json
import re

from ..knowledge_index import iter_phase1_chunks
from ..rag_context import verified_reviewed_index, ref_key, RetrievalUnavailable
from ..resolver import EvidenceResolver, ROOT

VARIANT = 'traditional_chinese_dream'
_UNRESOLVED_NARRATION = re.compile(
    r'没有|没|不曾|未曾|并未|不是|未发生|差点|险些|好像|似乎|可能|如果|假如|害怕|担心|会被|听说|讲述|说|电影|小说')
_REPORTED_CONTEXT = re.compile(r'听说|讲述|说|电影|小说|故事|视频')
_OTHER_SUBJECT = re.compile(r'别人|他人|有人|人家|他|她|朋友|哥哥|弟弟|姐姐|妹妹|爸爸|妈妈|父亲|母亲')
_OTHER_ANIMAL = re.compile(r'狗|犬|猫|虎|狼|龙|鱼|鸟|熊|狮|狐狸|兔|马|牛|羊|猪')
_CHASE = re.compile(r'蛇[^，,。.!！？?；;\n]{0,12}(?:追我|追着我)')
_LATER_BITE = re.compile(r'(?:后来|然后|接着)(?:它)?咬了我(?:的(?:手|脚))?(?:了)?

# Conservative first-person phrasing for the ten already-reviewed scenes.
_SCENE_PARAPHRASES = {
 'dream.term.snake': (r'(?:一条|那条)?蛇(?:突然)?咬(?:了)?(?:我|我的(?:手|脚|腿|胳膊))',),
 'dream.term.water': (r'(?:我|自己)(?:在|身处)水(?:里|中)(?:感到)?(?:很)?自在',),
 'dream.term.fire': (r'(?:我|自己)(?:站在|坐在|身处|待在)火(?:里|中)',),
 'dream.term.flying': (r'(?:我|自己)飞(?:到|上)(?:了)?天(?:上)?',),
 'dream.term.falling': (r'(?:我|自己)(?:掉|跌|坠)(?:进|入|到)(?:了)?井(?:里|中)?',),
 'dream.term.dragon': (r'(?:我|自己)(?:骑|乘)(?:着|上)?(?:一条)?龙(?:潜入|进入|钻进|飞入)(?:了)?(?:水里|水中|河里|湖里)',),
 'dream.term.fish': (r'(?:一群|很多|许多|成群的)鱼(?:在|于)(?:水里|水中|池塘里|河里|湖里)(?:游来游去|游动|游)',),
 'dream.term.house': (r'(?:我的|我家的)(?:房子|房屋|住宅)(?:正在|在)?(?:翻新|翻修|重新装修)',),
 'dream.term.family': (r'(?:我的兄弟|我兄弟|我的两个兄弟)(?:在)?(?:互相)?(?:打架|打斗)',),
 'dream.term.money': (r'(?:我|自己)(?:捡到|拾到|捡起)(?:了)?(?:一张|一叠|一些)?(?:纸币|钞票|钱|硬币)',),
}
_SCENE_PARAPHRASES = {key: tuple(re.compile(p) for p in patterns)
                      for key, patterns in _SCENE_PARAPHRASES.items()}


def _narrative_clauses(text):
    clauses = []
    reported = False
    for match in re.finditer(r'[^，,。.!！？?；;\n]+', text):
        clause = match.group()
        if _REPORTED_CONTEXT.search(clause):
            reported = True
        elif re.search(r'(?:我|自己)(?:又)?梦见', clause):
            reported = False
        clauses.append({'text':clause, 'start':match.start(), 'end':match.end(),
                        'reported_context':reported})
    return clauses


def _affirmed(clauses, index):
    clause = clauses[index]
    if clause['reported_context'] or _UNRESOLVED_NARRATION.search(clause['text']):
        return False
    if _OTHER_SUBJECT.search(clause['text']):
        return False
    if index + 1 < len(clauses) and re.match(
            r'\s*(?:但|但是|可是|其实|不过)?(?:并)?(?:没发生|没有发生|未发生|只是想象)',
            clauses[index+1]['text']):
        return False
    return True


def _span(clause, quote=None):
    if quote is None:
        return {key:clause[key] for key in ('start','end','text')}
    start = clause['start'] + clause['text'].index(quote)
    return {'start':start, 'end':start+len(quote), 'text':quote}


def _scene_matches(term_id, attrs, clauses):
    matches = []
    for index, clause in enumerate(clauses):
        if not _affirmed(clauses, index):
            continue
        for alias in attrs['scene_aliases']:
            if alias in clause['text']:
                if term_id == 'dream.term.snake' and alias.startswith('被'):
                    prefix = clause['text'].split(alias,1)[0].strip()
                    if not re.fullmatch(r'(?:(?:我)?梦见)?(?:我|自己)?',prefix):
                        continue
                matches.append({'method':'literal_reviewed_scene_alias', 'alias':alias,
                                'input_spans':[_span(clause,alias)]})
        if not any(alias in clause['text'] for alias in attrs['scene_aliases']):
            for pattern in _SCENE_PARAPHRASES.get(term_id, ()):
                match = pattern.search(clause['text'])
                if match:
                    matches.append({'method':'bounded_reviewed_scene_paraphrase',
                                    'alias':None, 'input_spans':[_span(clause,match.group())]})
                    break
        # Only this reviewed snake-bite scene has a bounded two-clause pattern.
        # It never supplies a separate meaning for water or being chased.
        if (term_id == 'dream.term.snake' and index > 0
                and _LATER_BITE.fullmatch(clause['text'].strip())
                and _affirmed(clauses, index-1)):
            previous = clauses[index-1]
            if (previous['text'].count('蛇') == 1 and _CHASE.search(previous['text'])
                    and not _OTHER_ANIMAL.search(previous['text'])
                    and not re.search(r'群蛇|几条蛇|多条蛇|两条蛇|还有|另外|和|与',previous['text'])):
                matches.append({'method':'bounded_adjacent_snake_chase_then_self_bite',
                                'alias':None, 'input_spans':[_span(previous),_span(clause)]})
    return matches


def _narrative_observations(clauses):
    observations = []
    for index, clause in enumerate(clauses):
        if _affirmed(clauses,index) and _CHASE.search(clause['text']):
            observations.append({'action':'being_chased', 'subject':'dreamer',
                'input_spans':[_span(clause)], 'status':'input_observation_only',
                'reviewed_interpretation_available':False, 'evidence_ids':[]})
    return observations

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
    clauses = _narrative_clauses(dream_text)
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
        input_matches = _scene_matches(term_id, attrs, clauses)
        scene_hits = list(dict.fromkeys(hit['alias'] for hit in input_matches if hit['alias']))
        if not input_matches:
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
                           'scene_alias_hits': scene_hits, 'input_matches': input_matches, 'rule_id': rule['id'],
                           'match_kind': 'reviewed_cultural_scene_retrieval',
                           **{key: attrs[key] for key in ('source', 'locator', 'original_text_short_quote',
                               'interpretation', 'interpretation_type', 'limitations', 'confidence', 'cultural_context')},
                           'evidence_level': row['metadata']['evidence_level'], 'evidence_ids': ids,
                           'personal_prediction': False})
        retrieved.append({'id': row['id'], 'entity_id': term_id,
                          'canonical_path': row['metadata']['canonical_path'], 'evidence_ids': ids})
    return {'domain': 'dream', 'variant': variant, 'mode': 'research',
            'status': 'reviewed_interpretation_candidates' if candidates else 'no_reviewed_interpretation',
            'entities': entities, 'matched_interpretations': candidates,
            'interpretation_candidates': candidates, 'narrative_observations': _narrative_observations(clauses),
            'evidence': evidence, 'retrieval': retrieved,
            'retrieval_method': 'bounded_scene_match_and_reviewed_rag',
            'chart_generated': False, 'public_enabled': False, 'ai_enabled': False,
            'limitations': [f"仅审核 {len(policy['reviewed_term_ids'])} 个具体传统梦场景；有限句式识别不是完整自然语言理解。",
                            '否定、假设、间接叙述或语义不清时保守不采纳；同一实体不等于同一梦义。',
                            '仅支持固定审核场景的第一人称有限同义句及单蛇追我后紧邻咬我；不作一般指代推理或组合释义。',
                            '被追只是输入动作观察，不生成文化解释；未命中不调用 LLM。']}
)
# Split only when a new explicit first-person dream follows a disclaimed or
# reported clause. Splitting positive clauses could turn a later retraction
# ("但我梦见其实没发生") into a false positive, so do not do that.
_CONTRAST_NEW_SELF_DREAM = re.compile(
    r'(?:但是|可是|不过|然而|但|却)(?=(?:我|自己)(?:又)?梦见|梦见(?:我|自己))')

# Conservative first-person phrasing for the ten already-reviewed scenes.
_SCENE_PARAPHRASES = {
 'dream.term.snake': (r'(?:一条|那条)?蛇(?:突然)?咬(?:了)?(?:我|我的(?:手|脚|腿|胳膊))',),
 'dream.term.water': (r'(?:我|自己)(?:在|身处)水(?:里|中)(?:感到)?(?:很)?自在',),
 'dream.term.fire': (r'(?:我|自己)(?:站在|坐在|身处|待在)火(?:里|中)',),
 'dream.term.flying': (r'(?:我|自己)飞(?:到|上)(?:了)?天(?:上)?',),
 'dream.term.falling': (r'(?:我|自己)(?:掉|跌|坠)(?:进|入|到)(?:了)?井(?:里|中)?',),
 'dream.term.dragon': (r'(?:我|自己)(?:骑|乘)(?:着|上)?(?:一条)?龙(?:潜入|进入|钻进|飞入)(?:了)?(?:水里|水中|河里|湖里)',),
 'dream.term.fish': (r'(?:一群|很多|许多|成群的)鱼(?:在|于)(?:水里|水中|池塘里|河里|湖里)(?:游来游去|游动|游)',),
 'dream.term.house': (r'(?:我的|我家的)(?:房子|房屋|住宅)(?:正在|在)?(?:翻新|翻修|重新装修)',),
 'dream.term.family': (r'(?:我的兄弟|我兄弟|我的两个兄弟)(?:在)?(?:互相)?(?:打架|打斗)',),
 'dream.term.money': (r'(?:我|自己)(?:捡到|拾到|捡起)(?:了)?(?:一张|一叠|一些)?(?:纸币|钞票|钱|硬币)',),
}
_SCENE_PARAPHRASES = {key: tuple(re.compile(p) for p in patterns)
                      for key, patterns in _SCENE_PARAPHRASES.items()}


def _narrative_clauses(text):
    clauses = []
    reported = False
    for match in re.finditer(r'[^，,。.!！？?；;\n]+', text):
        clause = match.group()
        if _REPORTED_CONTEXT.search(clause):
            reported = True
        elif re.search(r'(?:我|自己)(?:又)?梦见', clause):
            reported = False
        clauses.append({'text':clause, 'start':match.start(), 'end':match.end(),
                        'reported_context':reported})
    return clauses


def _affirmed(clauses, index):
    clause = clauses[index]
    if clause['reported_context'] or _UNRESOLVED_NARRATION.search(clause['text']):
        return False
    if _OTHER_SUBJECT.search(clause['text']):
        return False
    if index + 1 < len(clauses) and re.match(
            r'\s*(?:但|但是|可是|其实|不过)?(?:并)?(?:没发生|没有发生|未发生|只是想象)',
            clauses[index+1]['text']):
        return False
    return True


def _span(clause, quote=None):
    if quote is None:
        return {key:clause[key] for key in ('start','end','text')}
    start = clause['start'] + clause['text'].index(quote)
    return {'start':start, 'end':start+len(quote), 'text':quote}


def _scene_matches(term_id, attrs, clauses):
    matches = []
    for index, clause in enumerate(clauses):
        if not _affirmed(clauses, index):
            continue
        for alias in attrs['scene_aliases']:
            if alias in clause['text']:
                if term_id == 'dream.term.snake' and alias.startswith('被'):
                    prefix = clause['text'].split(alias,1)[0].strip()
                    if not re.fullmatch(r'(?:(?:我)?梦见)?(?:我|自己)?',prefix):
                        continue
                matches.append({'method':'literal_reviewed_scene_alias', 'alias':alias,
                                'input_spans':[_span(clause,alias)]})
        if not any(alias in clause['text'] for alias in attrs['scene_aliases']):
            for pattern in _SCENE_PARAPHRASES.get(term_id, ()):
                match = pattern.search(clause['text'])
                if match:
                    matches.append({'method':'bounded_reviewed_scene_paraphrase',
                                    'alias':None, 'input_spans':[_span(clause,match.group())]})
                    break
        # Only this reviewed snake-bite scene has a bounded two-clause pattern.
        # It never supplies a separate meaning for water or being chased.
        if (term_id == 'dream.term.snake' and index > 0
                and _LATER_BITE.fullmatch(clause['text'].strip())
                and _affirmed(clauses, index-1)):
            previous = clauses[index-1]
            if (previous['text'].count('蛇') == 1 and _CHASE.search(previous['text'])
                    and not _OTHER_ANIMAL.search(previous['text'])
                    and not re.search(r'群蛇|几条蛇|多条蛇|两条蛇|还有|另外|和|与',previous['text'])):
                matches.append({'method':'bounded_adjacent_snake_chase_then_self_bite',
                                'alias':None, 'input_spans':[_span(previous),_span(clause)]})
    return matches


def _narrative_observations(clauses):
    observations = []
    for index, clause in enumerate(clauses):
        if _affirmed(clauses,index) and _CHASE.search(clause['text']):
            observations.append({'action':'being_chased', 'subject':'dreamer',
                'input_spans':[_span(clause)], 'status':'input_observation_only',
                'reviewed_interpretation_available':False, 'evidence_ids':[]})
    return observations

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
    clauses = _narrative_clauses(dream_text)
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
        input_matches = _scene_matches(term_id, attrs, clauses)
        scene_hits = list(dict.fromkeys(hit['alias'] for hit in input_matches if hit['alias']))
        if not input_matches:
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
                           'scene_alias_hits': scene_hits, 'input_matches': input_matches, 'rule_id': rule['id'],
                           'match_kind': 'reviewed_cultural_scene_retrieval',
                           **{key: attrs[key] for key in ('source', 'locator', 'original_text_short_quote',
                               'interpretation', 'interpretation_type', 'limitations', 'confidence', 'cultural_context')},
                           'evidence_level': row['metadata']['evidence_level'], 'evidence_ids': ids,
                           'personal_prediction': False})
        retrieved.append({'id': row['id'], 'entity_id': term_id,
                          'canonical_path': row['metadata']['canonical_path'], 'evidence_ids': ids})
    return {'domain': 'dream', 'variant': variant, 'mode': 'research',
            'status': 'reviewed_interpretation_candidates' if candidates else 'no_reviewed_interpretation',
            'entities': entities, 'matched_interpretations': candidates,
            'interpretation_candidates': candidates, 'narrative_observations': _narrative_observations(clauses),
            'evidence': evidence, 'retrieval': retrieved,
            'retrieval_method': 'bounded_scene_match_and_reviewed_rag',
            'chart_generated': False, 'public_enabled': False, 'ai_enabled': False,
            'limitations': [f"仅审核 {len(policy['reviewed_term_ids'])} 个具体传统梦场景；有限句式识别不是完整自然语言理解。",
                            '否定、假设、间接叙述或语义不清时保守不采纳；同一实体不等于同一梦义。',
                            '仅支持固定审核场景的第一人称有限同义句及单蛇追我后紧邻咬我；不作一般指代推理或组合释义。',
                            '被追只是输入动作观察，不生成文化解释；未命中不调用 LLM。']}
