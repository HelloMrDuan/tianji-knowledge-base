#!/usr/bin/env python3
"""Live HTTP readiness smoke; default checks never call a model."""
import argparse,json,urllib.request
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base-url',default='http://127.0.0.1:8000')
a=p.parse_args();base=a.base_url.rstrip('/')
def request(path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as response:return json.load(response)
health=request('/health')
if health['engine']!='ready' or not health['rag_ready']:raise SystemExit('Reviewed runtime and RAG must be ready')
capabilities=request('/api/v1/capabilities')
if {row['domain'] for row in capabilities['domains']}!={'liuyao','qimen','liuren','ziwei','fengshui','yijing'}:
    raise SystemExit('Six-domain capability contract mismatch')
for row in capabilities['domains']:
    body={**row['example'],'explain':False}
    result=request('/api/v1/execute',body)
    if result!=request('/api/v1/execute',body):raise SystemExit('Deterministic HTTP result changed')
    if result['variant']!=body['variant'] or result['explanation_status']!='disabled' or not result['evidence']:
        raise SystemExit('Execution contract mismatch')
    print(row['domain'],result['variant'],'passed')
if '/api/v1/execute' not in request('/openapi.json')['paths']:raise SystemExit('OpenAPI missing execution endpoint')
print('Health, six-domain HTTP execution, RAG readiness and OpenAPI passed; no model invoked')
