#!/usr/bin/env python3
"""Count fixed validated bindings separately from deduplicated legacy rule scopes."""
import json
from collections import Counter
from pathlib import Path
from tianji_kb.knowledge import read_json
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.golden import run_cases

def coverage():
    resolver=EvidenceResolver();root=resolver.root
    cases=run_cases(root);by_case={c['id']:c for c in cases}
    legacy={eid:e for eid,(kind,e) in resolver.entities.items() if kind=='rules'}
    original=Counter(r['execution_status'] for r in legacy.values())
    validated_legacy=set();execution_rules={}
    for contract in resolver.contracts.values():
        for rule in contract['rules']:
            execution_rules[rule['id']]=rule
            if rule['validation_status']=='validated' and any(rule['id'] in by_case[g]['rule_ids'] for g in rule['golden_case_ids']):
                validated_legacy.update(rid for rid in rule['phase1_rule_refs'] if legacy[rid]['execution_status']=='executable')
    promoted=set()
    for item in read_json(root/'config/phase2_rule_promotions.json')['promotions']:
        rid=item['phase1_rule_id']
        if rid in promoted or legacy[rid]['execution_status']!='partially_structured':
            raise ValueError('Only unique previously partial rules may be promoted in execution view')
        for execution_id in item['execution_rule_ids']:
            rule=execution_rules[execution_id]
            if rid not in rule['phase1_rule_refs'] or item['variant']!=rule['variant'] or rule['validation_status']!='validated':
                raise ValueError('Promotion lacks validated variant-specific binding')
        promoted.add(rid);validated_legacy.add(rid)
    effective=dict(original);effective['executable']+=len(promoted);effective['partially_structured']-=len(promoted)
    levels=Counter(s['evidence_level'] for s in resolver.sources.values())
    audit=read_json(root/'config/phase2_source_audit.json')
    domains={}
    for domain,contract in resolver.contracts.items():
        domains[domain]={'variant':contract['variant'],'executable_bindings':len(contract['rules']),
            'validated_bindings':sum(r['validation_status']=='validated' for r in contract['rules']),
            'golden_cases':sum(c['domain']==domain for c in cases),'scope':contract.get('scope',''),
            'unresolved':contract.get('unresolved',[])}
    return {'baseline_commit':'bca1036','source_grades':{g:levels[g] for g in 'ABCD'},
        'phase1_preserved_status':dict(original),'effective_scoped_status':effective,
        'newly_promoted_legacy_scopes':len(promoted),'validated_legacy_scopes':len(validated_legacy),
        'phase2_executable_bindings':len(execution_rules),'phase2_validated_bindings':sum(r['validation_status']=='validated' for r in execution_rules.values()),
        'golden_cases':len(cases),'cross_work_comparisons':len(audit['claim_comparisons']),
        'verified_independent_evidence_groups':0,'supplementary_reviewed_quotes':len(resolver.supplementary_records),
        'domains':domains,'quarantine_auto_promotion':False,'ai_core_computation':False}

if __name__=='__main__':
    output=coverage();p=Path('build/phase2_coverage.json');p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(output,ensure_ascii=False,indent=2))
