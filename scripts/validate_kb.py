#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
canonical = ROOT / "data/canonical"
seed = json.loads((canonical / "seed.json").read_text(encoding="utf-8"))
registry = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
zhouyi = json.loads((canonical / "yijing/zhouyi_classic_core.json").read_text(encoding="utf-8"))
bazi_foundations = json.loads((canonical / "bazi/foundations_v1.json").read_text(encoding="utf-8"))
dayun = json.loads((canonical / "bazi/dayun_v1.json").read_text(encoding="utf-8"))
shensha = json.loads((canonical / "bazi/shensha_v1.json").read_text(encoding="utf-8"))
liuyao = json.loads((canonical / "liuyao/najia_v1.json").read_text(encoding="utf-8"))
meihua = json.loads((canonical / "meihua/rules_v1.json").read_text(encoding="utf-8"))

errors = []

def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

check(len(seed.get("wuxing", [])) == 5, "seed.wuxing must contain 5 elements")
check(len(seed.get("heavenly_stems", [])) == 10, "seed.heavenly_stems must contain 10 stems")
check(len(seed.get("earthly_branches", [])) == 12, "seed.earthly_branches must contain 12 branches")
check(len(seed.get("trigrams", [])) == 8, "seed.trigrams must contain 8 trigrams")
check(len(seed.get("hexagrams", [])) == 64, "seed.hexagrams must contain 64 hexagrams")
check(len({x[0] for x in seed.get("hexagrams", [])}) == 64, "seed hexagram numbers must be unique")

records = zhouyi.get("records", [])
check(len(records) == 64, "Zhouyi classic corpus must contain 64 hexagrams")
check({x["number"] for x in records} == set(range(1, 65)), "Zhouyi classic corpus numbers must be 1..64")
line_count = sum(len(x.get("lines", [])) for x in records)
check(line_count >= 384, "Zhouyi classic corpus must contain at least 384 line texts")
check(all(x.get("judgment") for x in records), "every Zhouyi hexagram must have a judgment")
check(all(x.get("image") for x in records), "every Zhouyi hexagram must have an image text")

check(len(bazi_foundations.get("heavenly_stems", [])) == 10, "Bazi foundations must have 10 stems")
check(len(bazi_foundations.get("hidden_stems", {})) == 12, "Bazi foundations must have 12 hidden-stem entries")
check(len(dayun.get("direction_rules", [])) == 4, "Dayun must define 4 direction rules")
check(len(shensha.get("items", [])) >= 20, "Shensha rules must contain at least 20 items")
check(len(liuyao.get("najia", {})) == 8, "Liuyao Najia must contain 8 pure trigrams")
check(meihua.get("ruleset") == "classic-implementation-v1", "Meihua ruleset id mismatch")

valid_policies = {"ALLOW","REFERENCE_ONLY","PUBLIC_DOMAIN_EXTRACT_ONLY","NON_COMMERCIAL","COPYLEFT","QUARANTINE"}
check(len({x["repo"] for x in registry}) == len(registry), "duplicate source repositories")
for source in registry:
    check(source["license_policy"] in valid_policies, f"invalid license policy: {source['repo']}")
    if source.get("license_spdx") is None and source["license_policy"] == "ALLOW":
        errors.append(f"unlicensed source cannot be ALLOW: {source['repo']}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(
    f"Knowledge base validation passed: {len(registry)} sources, "
    f"64 Zhouyi hexagrams, {line_count} line texts, "
    f"{len(shensha['items'])} shensha rules."
)
