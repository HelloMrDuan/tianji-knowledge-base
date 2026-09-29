#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.retrieval import RagIndex

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--domain")
parser.add_argument("--topic")
parser.add_argument("--school")
parser.add_argument("--ruleset")
parser.add_argument("--limit", type=int, default=10)
parser.add_argument("--rebuild", action="store_true")
args = parser.parse_args()

index_path = ROOT / "build/rag_chunks.jsonl"
if args.rebuild or not index_path.exists():
    subprocess.run([sys.executable, str(ROOT / "scripts/build_rag_chunks.py")], check=True)

index = RagIndex(index_path)
rows = index.search(
    args.query,
    domain=args.domain,
    topic=args.topic,
    school=args.school,
    ruleset=args.ruleset,
    limit=args.limit,
)
print(json.dumps(rows, ensure_ascii=False, indent=2))
