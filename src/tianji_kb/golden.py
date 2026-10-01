"""Fixed expected chart facts, independent of execution-time output generation."""
import importlib
from pathlib import Path
from .knowledge import read_json
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[2]

def assert_subset(actual,expected,path='$'):
    if isinstance(expected,dict):
        if not isinstance(actual,dict):
            raise AssertionError(f'{path}: expected object')
        for key,value in expected.items():
            if key not in actual:
                raise AssertionError(f'{path}.{key}: missing')
            assert_subset(actual[key],value,path+'.'+key)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(actual)!=len(expected):
            raise AssertionError(f'{path}: list length mismatch')
        for i,(a,e) in enumerate(zip(actual,expected)):
            assert_subset(a,e,f'{path}[{i}]')
    elif actual!=expected:
        raise AssertionError(f'{path}: {actual!r} != {expected!r}')

def run_cases(root=ROOT,domain=None):
    results=[];seen=set()
    schema=read_json(Path(root)/"schemas/knowledge/phase2-golden.schema.json")
    for path in sorted((Path(root)/'data/canonical').glob('*/phase2_golden.json')):
        obj=read_json(path);Draft202012Validator(schema).validate(obj)
        if domain and obj['domain']!=domain:
            continue
        provider=obj['provider']
        from .engine import PROVIDERS
        contract=read_json(path.parent/'phase2_execution.json')
        if obj['domain']!=path.parent.name or provider!=PROVIDERS[obj['domain']] or provider!=contract['provider']:
            raise ValueError('Golden domain/provider mismatch')
        if not provider.startswith('tianji_kb.operations.'):
            raise ValueError('Unregistered golden provider')
        module,name=provider.rsplit('.',1);function=getattr(importlib.import_module(module),name)
        for case in obj['cases']:
            if case['id'] in seen or case['variant']!=contract['variant']:
                raise ValueError('Duplicate Golden ID or variant mismatch')
            seen.add(case['id'])
            execution=function(**case['input'])
            if execution['domain']!=obj['domain'] or execution['variant']!=case['variant']:
                raise ValueError('Golden execution variant mismatch')
            assert_subset(execution['result'],case['expected'])
            if not execution['trace'] or not execution['evidence']:
                raise AssertionError('Golden execution lacks trace/evidence')
            results.append({'id':case['id'],'domain':obj['domain'],'variant':execution['variant'],'passed':True,'rule_ids':[step['rule_id'] for step in execution['trace']]})
    return results
