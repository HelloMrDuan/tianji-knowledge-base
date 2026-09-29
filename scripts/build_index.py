#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/canonical"

files = []
domain_counts = {}
for path in sorted(CANONICAL.rglob("*.json")):
    rel = path.relative_to(ROOT).as_posix()
    if "/batches/" in rel:
        continue
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        continue
    domain = obj.get("domain") or ("foundations" if path.name == "seed.json" else path.parent.name)
    domain_counts[domain] = domain_counts.get(domain, 0) + 1
    files.append({
        "path": rel,
        "domain": domain,
        "schema_version": obj.get("schema_version"),
        "source_level": obj.get("source_level"),
        "ruleset": obj.get("ruleset"),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    })

zhouyi = json.loads((CANONICAL / "yijing/zhouyi_classic_core.json").read_text(encoding="utf-8"))
index = {
    "schema_version": "0.2",
    "canonical_file_count": len(files),
    "domain_file_counts": domain_counts,
    "zhouyi": {
        "hexagrams": len(zhouyi["records"]),
        "line_texts": sum(len(x["lines"]) for x in zhouyi["records"]),
    },
    "files": files,
}

build_dir = ROOT / "build"
build_dir.mkdir(exist_ok=True)
(build_dir / "catalog.json").write_text(json.dumps(index, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(index, ensure_ascii=False))
