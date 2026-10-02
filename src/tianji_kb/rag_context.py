"""Reuse lexical RAG with a release-built Canonical-only, rule-bound corpus."""
import hashlib,json
from pathlib import Path
from .knowledge_index import iter_phase1_chunks
from .retrieval import RagIndex
from .resolver import EvidenceResolver,ROOT
from .runtime_catalog import load_catalog

class RetrievalUnavailable(ValueError):pass

def reviewed_rows(resolver):
    rows=list(iter_phase1_chunks(resolver.root,model=resolver.model))
    for ref in resolver.supplementary_records:
        domain=ref['id'].split('.')[0]
        rows.append({'id':hashlib.sha256(ref['id'].encode()).hexdigest()[:24],
            'text':ref['chapter_title']+'\n'+ref['original_text'],
            'metadata':{'model':'phase2-evidence','entity_id':ref['id'],'domain':domain,
                'topic':'knowledge_section','canonical_path':f'data/canonical/{domain}/phase2_evidence.json',
                'execution_rule_ids':ref['rule_ids'],'variants':ref['variants'],
                'source_refs':[{'source_id':ref['source_id'],'section_id':ref['id'],'original_text':ref['original_text']}]}})
    return rows

def write_reviewed_index(resolver):
    rows=reviewed_rows(resolver)
    content=''.join(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n' for row in rows).encode()
    path=resolver.root/'build/production_rag.jsonl';path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    tmp.write_bytes(content);tmp.replace(path)
    return hashlib.sha256(content).hexdigest()

def ref_key(ref):return (ref['source_id'],ref['section_id'],ref['original_text'])

class CanonicalRetriever:
    def __init__(self,root=ROOT):self.root=Path(root)
    def retrieve(self,raw,limit=6):
        resolver=EvidenceResolver(self.root)
        payload=load_catalog(self.root);path=self.root/'build/production_rag.jsonl'
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=payload.get('retrieval_index_sha256'):
            raise RetrievalUnavailable('Reviewed Canonical RAG index missing or stale')
        contract=resolver.contracts[raw['domain']]
        if raw['variant']!=contract['variant']:raise RetrievalUnavailable('Retrieval variant mismatch')
        rule_ids={step['rule_id'] for step in raw['trace']}
        legacy={rid for rule in contract['rules'] if rule['id'] in rule_ids for rid in rule['phase1_rule_refs']}
        permitted=legacy|{ref['section_id'] for ref in raw['evidence'].values()}
        evidence_keys={}
        for evidence_id,ref in raw['evidence'].items():evidence_keys.setdefault(ref_key(ref),[]).append(evidence_id)
        trusted={row['id']:row for row in reviewed_rows(resolver)}
        index=RagIndex(path);output={}
        queries=[resolver.rule(rid)['name'] for rid in sorted(legacy)]
        queries.extend(ref['chapter_title'] for ref in resolver.supplementary_records if rule_ids.intersection(ref['rule_ids']))
        for query in dict.fromkeys(queries):
            for row in index.search(query,domain=raw['domain'],limit=40):
                if row['id'] in output:continue
                expected=trusted.get(row['id']);meta=row.get('metadata',{})
                if expected is None or meta!=expected['metadata'] or meta['entity_id'] not in permitted:continue
                if not meta['canonical_path'].startswith(f"data/canonical/{raw['domain']}/"):continue
                if meta.get('variants') and raw['variant'] not in meta['variants']:continue
                if meta.get('execution_rule_ids') and not rule_ids.intersection(meta['execution_rule_ids']):continue
                refs=meta['source_refs']
                if any(ref_key(ref) not in evidence_keys for ref in refs):continue
                ids=sorted({eid for ref in refs for eid in evidence_keys[ref_key(ref)]})
                # Only classical quotes are passed, never old partial operations or untrusted index text.
                output[row['id']]={'id':row['id'],'entity_id':meta['entity_id'],'domain':raw['domain'],
                    'variant':raw['variant'],'source_variant':meta.get('variant'),
                    'text':'\n'.join(ref['original_text'] for ref in refs),'evidence_ids':ids,
                    'scope':'contextual classical quotation; not permission to recompute the chart'}
                if len(output)>=limit:return list(output.values())
                break
        return list(output.values())
