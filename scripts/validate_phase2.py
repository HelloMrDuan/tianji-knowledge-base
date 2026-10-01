#!/usr/bin/env python3
"""Check executable bindings and run fixed expected facts before counting validation."""
import importlib
from pathlib import Path
from jsonschema import Draft202012Validator
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.engine import PROVIDERS

ROOT=Path(__file__).resolve().parents[1]

def validate():
    resolver=EvidenceResolver(ROOT)
    schema=read_json(ROOT/'schemas/knowledge/execution.schema.json')
    passed={c['id']:c for c in run_cases(ROOT)}
    seen=set();n=0
    for domain,contract in resolver.contracts.items():
        Draft202012Validator(schema).validate(contract)
        module,name=contract['provider'].rsplit('.',1)
        if contract['provider']!=PROVIDERS[domain] or not callable(getattr(importlib.import_module(module),name)):
            raise ValueError('Unknown execution provider')
        for rule in contract['rules']:
            if rule['id'] in seen or rule['domain']!=domain or rule['variant']!=contract['variant']:
                raise ValueError('Duplicate rule or execution domain/variant mismatch')
            seen.add(rule['id'])
            resolver.resolve(rule['id'],contract['variant'])
            if rule['validation_status']=='validated':
                if not (ROOT/rule['regression_test']).is_file():raise ValueError('Missing regression test')
                if not all(g in passed and passed[g]['domain']==domain and passed[g]['variant']==contract['variant'] for g in rule['golden_case_ids']):
                    raise ValueError('Golden validation variant mismatch')
                if not any(rule['id'] in passed[g]['rule_ids'] for g in rule['golden_case_ids']):
                    raise ValueError('No golden exercises this execution rule')
                n+=1
    print(f'Phase 2: {len(seen)} execution rules, {n} validated, {len(passed)} golden cases passed')

if __name__=='__main__':validate()
