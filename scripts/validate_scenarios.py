#!/usr/bin/env python3
"""Validate unreleased design assets; no scenario execution or model calls."""
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
import re

from jsonschema import Draft202012Validator
from tianji_kb.engine import PROVIDERS
from tianji_kb.resolver import EvidenceResolver

ROOT=Path(__file__).resolve().parents[1]
CORE_IDS={'daily_fortune','weekly_fortune','monthly_fortune','annual_fortune','romance',
          'career_wealth','compatibility','one_question','dream','life_overview'}
SECTIONS=('comprehensive_index','current_trend','key_times','favorable_factors','risk_reminders','classical_basis','uncertainty')

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)
def pointer(value,path):
    require(isinstance(path,str) and path.startswith('/'),'Invalid design fact pointer')
    for part in path[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value

def validate_design(root=ROOT,*,registry=None,prototypes=None,check_board=True):
    root=Path(root);registry=registry if registry is not None else read(root/'config/scenarios/registry.json')
    prototypes=prototypes if prototypes is not None else read(root/'config/scenarios/prototypes.json')
    Draft202012Validator(read(root/'schemas/scenarios/registry.schema.json')).validate(registry)
    snapshot=read(root/'config/scenarios/capability_snapshot.json')
    for path,expected in snapshot['source_hashes'].items():
        require((root/path).resolve().is_relative_to(root.resolve()),'Unsafe audit path')
        require(sha(root/path)==expected,'Capability baseline changed; review snapshot explicitly')
    resolver=EvidenceResolver(root,review_sources=True)
    require(set(resolver.contracts)==set(PROVIDERS),'Registered provider audit mismatch')
    engines={e['engine_id']:e for e in snapshot['engines']}
    require(set(engines)==set(PROVIDERS)|{'bazi'},'Seven underlying domains must be preserved')
    require(not engines['bazi']['registered'] and engines['bazi']['variant'] is None and not engines['bazi']['rules'],'Missing Bazi must not be invented')
    for domain,c in resolver.contracts.items():
        require(engines[domain]['registered'] and engines[domain]['variant']==c['variant'] and engines[domain]['provider']==c['provider'],'Audited provider/variant mismatch')
        require({r['rule_id'] for r in engines[domain]['rules']}=={r['id'] for r in c['rules']},'Audited rules mismatch')
        for rule in engines[domain]['rules']:
            actual=[{'source_id':e['source_id'],'section_id':e['section_id'],'grade':e['evidence_level'],
                     'quote_sha256':hashlib.sha256(e['original_text'].encode()).hexdigest()}
                    for e in resolver.resolve(rule['rule_id'],c['variant'])]
            require(rule['evidence']==actual,'Audited evidence or grade differs from reviewed resolver')
    require(snapshot['execution_rules']==37 and snapshot['golden_cases']==28,'Audit count drift')
    require(snapshot['source_grades']==dict(Counter(s['evidence_level'] for s in resolver.sources.values())),'Audited source grades changed')
    require(snapshot['ai']['quality_qualified'] is False and snapshot['ai']['production_enabled'] is False,'AI audit cannot grant release')
    require(snapshot['scenario_api_implemented'] is False and snapshot['history_api_implemented'] is False,'Design does not implement APIs')
    ids=[s['scenario_id'] for s in registry['scenarios']]
    require(set(ids)==CORE_IDS and len(ids)==len(set(ids)),'Core scenario IDs differ')
    entries=[e['entry_id'] for s in registry['scenarios'] for e in s['entries']]
    require(len(entries)==11 and len(set(entries))==11,'Eleven unique frontend entries required')
    require({'career','wealth'}<=set(entries),'Both career and wealth entries required')
    for s in registry['scenarios']:
        require(not s['scenario_rules'] and not s['evidence']['scenario_conclusion_refs'],'Structural rules cannot become scenario conclusions')
        for dep in s['dependencies']:
            require(dep['engine_id'] in engines,'Scenario depends on nonexistent engine')
            e=engines[dep['engine_id']]
            require(dep['registered']==e['registered'] and dep['variant']==e['variant'],'Scenario variant/availability differs from audited engine')
            require(set(dep['rule_ids'])<={r['rule_id'] for r in e['rules']},'Scenario invents execution rules')
            require('fengshui.phase2.relative_period' not in dep['rule_ids'],'Research epochs cannot enter production scenario plans')
        for ref in s['evidence']['existing_structural_refs']:
            match=re.fullmatch(r'config/scenarios/capability_snapshot.json#/engines/(\d+)/rules/(\d+)',ref['audit_ref'])
            require(match is not None,'Invalid audit evidence pointer')
            e=snapshot['engines'][int(match[1])];rule=e['rules'][int(match[2])]
            require(e['engine_id']==ref['engine_id'] and rule['rule_id']==ref['rule_id'],'Evidence pointer binds unrelated rule')
            require(ref['grades']==sorted({v['grade'] for v in rule['evidence']}),'Evidence grade cannot be promoted by scenario')
    require(prototypes['artifact_kind']=='design_only' and prototypes['timezone']=='Asia/Shanghai','Prototype release/timezone mismatch')
    rows=prototypes['prototypes'];require(len(rows)==10 and {p['scenario_id'] for p in rows}==CORE_IDS,'Ten input/output prototypes required')
    for p in rows:
        out=p['output_example'];require(out['scenario_id']==p['scenario_id'],'Prototype scenario mismatch')
        require(out['generated_by']=='design_fixture' and out['history']['record_created'] is False,'Prototype cannot claim live report/history')
        require(out['ai']['status']=='disabled' and out['ai']['explanation'] is None and not out['ai']['quality_qualified'],'Unqualified scenario AI must remain disabled')
        require(all(k in out for k in SECTIONS),'Missing aggregate report section')
        for key in ('comprehensive_index','current_trend','key_times','favorable_factors'):
            require(out[key]['value'] is None and not out[key]['items'] and out[key]['status']=='unavailable','Unverified score/trend/time/favorable factor invented')
        require(out['status'] in ('blocked','structural_preview'),'Design prototype cannot claim completed prediction')
        for run in out['computed_engine_runs']:
            require(run['engine_id'] in PROVIDERS and run['variant']==resolver.contracts[run['engine_id']]['variant'],'Prototype run invents engine/variant')
            require(digest(run['result'])==run['result_sha256'],'Fixed structural sample was altered')
            require(run['provenance']['execution_and_calendar_code_matches_baseline'] is True,'Missing actual sample provenance')
            allowed={r['id'] for r in resolver.contracts[run['engine_id']]['rules']}
            require(all(r['rule_id'] in allowed for r in run['rule_matches']),'Prototype invents matched rule')
        for fact in out['facts']:
            require(len(out['computed_engine_runs'])==1,'Sample facts need an unambiguous run')
            run=out['computed_engine_runs'][0]
            require(pointer(run['result'],fact['fact_ref'])==fact['value'],'Prototype prose fact differs from executed result')
            matched={r['rule_id'] for r in run['rule_matches'] if r['matched']}
            require(set(fact['rule_ids'])<=matched,'Prototype fact binds unmatched rule')
        for e in out['classical_basis']['items']:
            refs=resolver.resolve(e['rule_id'],e['variant'])
            require(any(all(e[k]==r[k] for k in ('source_id','section_id','original_text','evidence_level')) for r in refs),'Prototype quote/grade lacks audited evidence')
        if p['scenario_id']=='dream':require(not out['computed_engine_runs'],'Dream must not fake a deterministic chart')
        if p['scenario_id']=='compatibility':
            require(set(p['input_example']['participants'])=={'a','b'},'Two participant inputs required')
            pair=out['comparison'];require(pair['score'] is None and pair['status']=='unavailable','Legacy pairing score cannot be promoted')
            require(all(d['a'] is None and d['b'] is None and d['relation'] is None for d in pair['dimensions']),'Unimplemented pair results invented')
        if p['scenario_id'] in ('daily_fortune','weekly_fortune','monthly_fortune','annual_fortune'):
            period=out['history']['period'];start=datetime.fromisoformat(period['civil_start']);end=datetime.fromisoformat(period['civil_end_exclusive'])
            require(start<end and start.utcoffset().total_seconds()==28800 and end.utcoffset().total_seconds()==28800,'Invalid domestic history period')
            require(period['timezone']=='Asia/Shanghai','History timezone must remain domestic')
    manifest=read(root/'config/public_domain_manifest.json')
    sanming=next(b for r in manifest['sources'] for b in r['works'] if b['id']=='sanming_tonghui')
    require(sanming['promotion']=='quarantine_only' and sanming['quality_blockers']['canonical_ready'] is False,'Sanming isolation changed')
    require(sanming['quality_blockers']['remaining_unique_private_use_chars']==0 and sanming['quality_blockers']['remaining_private_use_chars']==0,'PUA completion regressed')
    require(not (root/'data/canonical/classics/bazi/sanming_tonghui_v1.json').exists(),'Sanming must not be promoted')
    if check_board:
        html=(root/'docs/scenarios/prototype.html').read_text(encoding='utf-8')
        data=json.loads(re.search(r'<script id="scenario-data" type="application/json">(.*?)</script>',html,re.S)[1])
        require(data['registry_sha256']==sha(root/'config/scenarios/registry.json') and data['prototypes_sha256']==sha(root/'config/scenarios/prototypes.json'),'Design board is stale; rebuild it')
        require(data['scenarios']==registry['scenarios'],'Design board scenario data differs from registry')
        expected=[{**p,'output_example':{k:v for k,v in p['output_example'].items() if k!='computed_engine_runs'}} for p in rows]
        require(data['prototypes']==expected,'Design board fixed report differs from prototypes')
    return {'scenarios':10,'frontend_entries':11,'execution_rules':37,'golden_cases':28,'ai_enabled':False,'scenario_runtime_implemented':False}

if __name__=='__main__':
    print(json.dumps(validate_design(),ensure_ascii=False))
