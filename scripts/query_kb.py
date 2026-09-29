#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tianji_kb.search import KnowledgeBase

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--domain")
parser.add_argument("--hexagram", action="store_true")
parser.add_argument("--limit", type=int, default=20)
args = parser.parse_args()

kb = KnowledgeBase(ROOT)
if args.hexagram:
    result = kb.get_hexagram(args.query)
else:
    result = kb.search(args.query, domain=args.domain, limit=args.limit)
print(json.dumps(result, ensure_ascii=False, indent=2))
