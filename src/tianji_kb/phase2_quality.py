"""Fail closed on supplementary citations, source independence and fixture contracts."""
from jsonschema import Draft202012Validator
from .knowledge import read_json,source_text

def validate_evidence(resolver):
    schema=read_json(resolver.root/'schemas/knowledge/phase2-evidence.schema.json')
    seen=set();records=[]
    for path in sorted((resolver.root/'data/canonical').glob('*/phase2_evidence.json')):
        obj=read_json(path);Draft202012Validator(schema).validate(obj)
        domain=obj['domain']
        if path.parent.name!=domain or domain not in resolver.contracts:
            raise ValueError('Supplementary evidence domain mismatch')
        for classic in obj.get('classics',[]):
            if classic['domain']!=domain or not classic['id'].startswith(domain+'.classic.'):
                raise ValueError('Supplementary classic domain mismatch')
            source=resolver.sources[classic['source_id']]
            if source['kind']!='classical' or source['evidence_level']=='D':
                raise ValueError('Implementation cannot become a classical book')
        for ref in obj['records']:
            if ref['id'] in seen or not ref['id'].startswith(domain+'.evidence.'):
                raise ValueError('Duplicate or cross-domain supplementary evidence')
            seen.add(ref['id'])
            source=resolver.sources[ref['source_id']]
            if source['kind']!='classical' or source['evidence_level']=='D' or ref['original_text'] not in source_text(resolver.root,source):
                raise ValueError('Unreviewed or unverifiable supplementary evidence')
            if ref['classic_id'] in resolver.entities:
                collection,classic=resolver.entities[ref['classic_id']]
                if collection!='classics':raise ValueError('Evidence points to a non-classic')
            else:classic=resolver.supplementary_classics[ref['classic_id']]
            if classic['domain']!=domain:raise ValueError('Cross-domain classic citation')
            primary=resolver.sources[classic['source_id']]
            if ref['source_id']!=classic['source_id'] and (source['repository'],source['path'],source['commit'])!=(primary['repository'],primary['path'],primary['commit']):
                raise ValueError('Unreviewed source-to-classic relationship')
            for rule_id in ref['rule_ids']:
                rule=resolver.rule(rule_id)
                if rule['domain']!=domain or ref['variants']!=[rule['variant']]:
                    raise ValueError('Supplementary citation variant mismatch')
            records.append(ref)
    return records

def validate_source_audit(resolver,audit=None):
    audit=audit or read_json(resolver.root/'config/phase2_source_audit.json')
    rows=audit['lineages'];by_id={r['source_id']:r for r in rows}
    if len(rows)!=len(by_id) or set(by_id)!=set(resolver.sources):
        raise ValueError('Source lineage audit must cover each registered source exactly once')
    origins={}
    for sid,row in by_id.items():
        source=resolver.sources[sid]
        origin=(source['repository'],source['path'])
        if origin in origins and origins[origin]!=row['lineage_group']:
            raise ValueError('Same original cannot count as independent lineages')
        origins[origin]=row['lineage_group']
        expected='D' if source['kind']=='implementation' else 'C'
        # This release has no scanned bibliographic proof; an upgrade needs a new reviewed proof contract.
        if row['edition_status']!='unverified' or row['authority_status']!='unverified' or row['grade_ceiling']!=expected:
            raise ValueError('No verified independent-edition proof registered in this release')
        if source['evidence_level'] not in (expected,'D'):
            raise ValueError('A/B source promotion requires independently reviewed bibliographic proof')
    for item in audit['claim_comparisons']:
        resolver.rule(item['rule_id'])
        if len(item['citations'])<2:raise ValueError('Comparison needs at least two citations')
        for ref in item['citations']:
            source=resolver.sources[ref['source_id']]
            if source['kind']!='classical' or ref['original_text'] not in source_text(resolver.root,source):
                raise ValueError('Unverifiable comparison citation')
        if item['assessment']!='C' or item['independence_status']!='unverified' or item['independent_source_count']!=0:
            raise ValueError('Unverified comparisons cannot vote as independent evidence')
    return audit
