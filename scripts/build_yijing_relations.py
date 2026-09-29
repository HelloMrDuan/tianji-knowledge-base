#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
seed = json.loads((ROOT / "data/canonical/seed.json").read_text(encoding="utf-8"))
tri = {x["name"]: x["binary_bottom_to_top"] for x in seed["trigrams"]}
lookup = {}
for h in seed["hexagrams"]:
    number, short, full, upper, lower = h
    bits = tri[lower] + tri[upper]
    lookup[bits] = {
        "number": number, "short_name": short, "full_name": full,
        "upper": upper, "lower": lower, "binary_bottom_to_top": bits,
    }

records = []
for h in seed["hexagrams"]:
    number, short, full, upper, lower = h
    bits = tri[lower] + tri[upper]
    opposite = "".join("0" if b == "1" else "1" for b in bits)
    reversed_bits = bits[::-1]
    nuclear = bits[1:4] + bits[2:5]
    changes = []
    for line in range(6):
        changed = list(bits)
        changed[line] = "0" if changed[line] == "1" else "1"
        cbits = "".join(changed)
        changes.append({"line": line + 1, "binary_bottom_to_top": cbits, "target": lookup[cbits]})
    records.append({
        "number": number, "short_name": short, "full_name": full,
        "upper_trigram": upper, "lower_trigram": lower, "binary_bottom_to_top": bits,
        "opposite": lookup[opposite], "reversed": lookup[reversed_bits],
        "nuclear": lookup[nuclear], "line_changes": changes,
    })

out = {
    "schema_version": "0.1", "domain": "yijing", "topic": "hexagram_relations",
    "derivation": "Deterministically derived from lower/upper trigram binary forms; line order is bottom-to-top.",
    "records": records,
}
path = ROOT / "data/canonical/yijing/hexagram_relations_v1.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"generated {len(records)} hexagram relation records")
