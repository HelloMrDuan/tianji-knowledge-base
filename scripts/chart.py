#!/usr/bin/env python3
"""JSON CLI for deterministic chart → RuleMatch → Evidence → explanation context."""
import argparse,json,sys
from tianji_kb.engine import execute,PROVIDERS
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('domain',choices=PROVIDERS)
p.add_argument('--input-json',required=True,help='JSON object; use - to read stdin')
p.add_argument('--variant')
p.add_argument('--research',action='store_true',help='Explicit research gateway for unverified period epochs')
a=p.parse_args()
try:
    value=json.load(sys.stdin) if a.input_json=='-' else json.loads(a.input_json)
    print(json.dumps(execute(a.domain,value,a.variant,allow_research=a.research),ensure_ascii=False,indent=2))
except (ValueError,TypeError) as error:
    p.exit(2,f'Invalid chart request: {error}\n')
