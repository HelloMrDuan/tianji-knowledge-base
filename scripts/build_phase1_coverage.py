#!/usr/bin/env python3
"""Write coverage or check all committed counts, documentation and domain status."""
import argparse
import json
from pathlib import Path

from tianji_kb.coverage import build_coverage, markdown_coverage

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build_coverage(ROOT)
    target = ROOT / 'data/coverage/phase1.json'
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    docs = ROOT / 'docs/COVERAGE.md'
    before = docs.read_text()
    block = markdown_coverage(report)
    start = '<!-- PHASE1_COVERAGE_START -->'
    end = '<!-- PHASE1_COVERAGE_END -->'
    if start in before:
        prefix, rest = before.split(start, 1)
        _, suffix = rest.split(end, 1)
        updated = prefix + block.rstrip('\n') + suffix
    else:
        updated = before.rstrip() + '\n\n' + block
    registry_path = ROOT / 'config/domain_registry.json'
    registry = json.loads(registry_path.read_text())
    statuses = {d['domain']: d['status'] for d in report['domains']}
    registry_changed = any(d['status'] != statuses[d['id']] for d in registry['domains'])
    for domain in registry['domains']:
        domain['status'] = statuses[domain['id']]
    if args.check:
        if not target.exists() or target.read_text() != rendered or updated != before or registry_changed:
            raise SystemExit('Coverage artifact/docs/domain statuses drift; run build_phase1_coverage.py')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered)
        docs.write_text(updated)
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    print('Phase 1 coverage verified: ' + ', '.join(f"{d['domain']}={d['status']}" for d in report['domains']))

if __name__ == '__main__':
    main()
