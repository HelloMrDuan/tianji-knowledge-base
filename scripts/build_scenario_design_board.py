#!/usr/bin/env python3
"""Refresh embedded, fixed design data in the standalone offline HTML board."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def build():
    registry=ROOT/'config/scenarios/registry.json';prototypes=ROOT/'config/scenarios/prototypes.json'
    r=read(registry);p=read(prototypes)
    # Omit raw chart runs/trace from the public-facing mock; retain necessary quotations.
    rows=[]
    for row in p['prototypes']:
        output={k:v for k,v in row['output_example'].items() if k!='computed_engine_runs'}
        rows.append({**row,'output_example':output})
    data={'registry_sha256':hashlib.sha256(registry.read_bytes()).hexdigest(),
          'prototypes_sha256':hashlib.sha256(prototypes.read_bytes()).hexdigest(),
          'scenarios':r['scenarios'],'prototypes':rows}
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    path=ROOT/'docs/scenarios/prototype.html';html=path.read_text(encoding='utf-8')
    html,count=re.subn(r'(<script id="scenario-data" type="application/json">).*?(</script>)',
                      lambda m:m[1]+payload+m[2],html,flags=re.S)
    if count!=1:raise ValueError('Expected one standalone design data block')
    path.write_text(html,encoding='utf-8',newline='\n')
    print('Offline design board refreshed; no scenario, provider or history API invoked')

if __name__=='__main__':build()
