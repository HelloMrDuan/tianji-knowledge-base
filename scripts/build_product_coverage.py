#!/usr/bin/env python3
"""Generate or verify product reports through the existing knowledge/RAG workflow."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import runpy
from tianji_kb.product_coverage import build_product_coverage, markdown_report

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    # Rebuild with the original chunk builder, rather than another RAG algorithm.
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(str(ROOT / 'scripts/build_rag_chunks.py'), run_name='__main__')
    rows = [json.loads(line) for line in (ROOT / 'build/rag_chunks.jsonl').read_text(encoding='utf-8').splitlines() if line]
    report = build_product_coverage(ROOT, rag_rows=rows)
    outputs = {ROOT / 'data/product/knowledge_coverage.json': json.dumps(report, ensure_ascii=False, indent=2) + '\n',
               ROOT / 'docs/product/KNOWLEDGE_GAPS.md': markdown_report(report)}
    for path, text in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != text:
                raise SystemExit('Product coverage drift: run scripts/build_product_coverage.py')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
    print(f'Product coverage verified: {len(report)-1} products; 0 public explanations authorized')


if __name__ == '__main__':
    main()
