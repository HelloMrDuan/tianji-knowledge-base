#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
seed_path = ROOT / "data/canonical/seed.json"
seed = json.loads(seed_path.read_text(encoding="utf-8"))

index = {
    "schema_version": seed["schema_version"],
    "content_sha256": hashlib.sha256(seed_path.read_bytes()).hexdigest(),
    "domains": {
        "foundations": {
            "wuxing": len(seed["wuxing"]),
            "heavenly_stems": len(seed["heavenly_stems"]),
            "earthly_branches": len(seed["earthly_branches"]),
        },
        "yijing": {
            "trigrams": len(seed["trigrams"]),
            "hexagrams": len(seed["hexagrams"]),
        },
        "liuyao": {
            "najia_trigrams": len(seed["liuyao"]["najia"]),
            "rules": ["yao_values","six_relatives","six_spirits_start"],
        },
    },
}
build = ROOT / "build"
build.mkdir(exist_ok=True)
(build / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(index, ensure_ascii=False))
