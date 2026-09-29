#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
canonical = ROOT / "data/canonical"

def load(rel: str):
    return json.loads((canonical / rel).read_text(encoding="utf-8"))

seed = load("seed.json")
zhouyi = load("yijing/zhouyi_classic_core.json")
bazi_foundations = load("bazi/foundations_v1.json")
dayun = load("bazi/dayun_v1.json")
shensha = load("bazi/shensha_v1.json")
liuyao = load("liuyao/najia_v1.json")
meihua = load("meihua/rules_v1.json")
ziwei = load("ziwei/iztro_rules_v1.json")
qimen = load("qimen/qfdk_maoshan_v1.json")
liuren_catalog = load("liuren/classics_catalog_v1.json")
taiyi_catalog = load("taiyi/classics_catalog_v1.json")

registry = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]
ingestion = json.loads((ROOT / "config/ingestion_manifest.json").read_text(encoding="utf-8"))

errors: list[str] = []

def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

# Foundations
check(len(seed.get("wuxing", [])) == 5, "seed.wuxing must contain 5 elements")
check(len(seed.get("heavenly_stems", [])) == 10, "seed.heavenly_stems must contain 10 stems")
check(len(seed.get("earthly_branches", [])) == 12, "seed.earthly_branches must contain 12 branches")
check(len(seed.get("trigrams", [])) == 8, "seed.trigrams must contain 8 trigrams")
check(len(seed.get("hexagrams", [])) == 64, "seed.hexagrams must contain 64 hexagrams")
check(len({x[0] for x in seed.get("hexagrams", [])}) == 64, "seed hexagram numbers must be unique")

# Zhouyi core
records = zhouyi.get("records", [])
check(len(records) == 64, "Zhouyi classic corpus must contain 64 hexagrams")
check({x["number"] for x in records} == set(range(1, 65)), "Zhouyi classic corpus numbers must be 1..64")
line_count = sum(len(x.get("lines", [])) for x in records)
check(line_count >= 384, "Zhouyi classic corpus must contain at least 384 line texts")
check(all(x.get("judgment") for x in records), "every Zhouyi hexagram must have a judgment")
check(all(x.get("image") for x in records), "every Zhouyi hexagram must have an image text")

# Ten Wings general appendices
ten_wings = {
    name: load(f"yijing/ten_wings/{name}.json")
    for name in ("xici_shang", "xici_xia", "shuogua", "xugua", "zagua")
}
min_lengths = {"xici_shang": 2500, "xici_xia": 2500, "shuogua": 1000, "xugua": 1000, "zagua": 350}
for name, obj in ten_wings.items():
    text = obj.get("normalized_text", "")
    check(obj.get("source_level") == "L0-public-domain-classic", f"{name} must be L0 classic")
    check(len(text) >= min_lengths[name], f"{name} text unexpectedly short")
    check("□" not in text and "�" not in text, f"{name} contains unresolved replacement characters")
    check(obj.get("provenance", {}).get("primary", {}).get("commit"), f"{name} lacks pinned source commit")

# Bazi / Liuyao / Meihua
check(len(bazi_foundations.get("heavenly_stems", [])) == 10, "Bazi foundations must have 10 stems")
check(len(bazi_foundations.get("hidden_stems", {})) == 12, "Bazi foundations must have 12 hidden-stem entries")
check(len(dayun.get("direction_rules", [])) == 4, "Dayun must define 4 direction rules")
check(len(shensha.get("items", [])) >= 20, "Shensha rules must contain at least 20 items")
check(len(liuyao.get("najia", {})) == 8, "Liuyao Najia must contain 8 pure trigrams")
check(meihua.get("ruleset") == "classic-implementation-v1", "Meihua ruleset id mismatch")

# Ziwei
check(len(ziwei.get("palaces", [])) == 12, "Ziwei must contain 12 palaces")
check(len(ziwei.get("major_stars", [])) == 14, "Ziwei must contain 14 major stars")
four = ziwei.get("four_transformations", {})
check(len(four) == 10, "Ziwei four-transformations must cover 10 heavenly stems")
check(all(len(v) == 4 for v in four.values()), "every Ziwei stem must map to 4 transformations")

# Qimen
check(len(qimen.get("nine_palaces", {})) == 9, "Qimen must contain 9 palaces")
check(len(qimen.get("nine_stars", {})) == 9, "Qimen must contain 9 stars")
check(len(qimen.get("eight_doors", {})) == 8, "Qimen must contain 8 doors")
check(len(qimen.get("eight_deities", [])) == 8, "Qimen must contain 8 deities")
check(len(qimen.get("solar_term_bureaus", [])) == 24, "Qimen bureau table must contain 24 solar terms")
check(len(qimen.get("canonical_terms", {}).get("san_qi", [])) == 3, "Qimen sanqi must contain 3 stems")
check(len(qimen.get("canonical_terms", {}).get("liu_yi", [])) == 6, "Qimen liuyi must contain 6 stems")

# Daliuren / Taiyi bibliography
check(liuren_catalog.get("record_count", 0) >= 120, "Daliuren bibliography unexpectedly small")
check(taiyi_catalog.get("record_count", 0) >= 90, "Taiyi bibliography unexpectedly small")

# Licensing and ingestion guardrails
valid_policies = {"ALLOW","REFERENCE_ONLY","PUBLIC_DOMAIN_EXTRACT_ONLY","NON_COMMERCIAL","COPYLEFT","QUARANTINE"}
check(len({x["repo"] for x in registry}) == len(registry), "duplicate source repositories")
by_id = {x["id"]: x for x in registry}
check(len(by_id) == len(registry), "duplicate source ids")
for source in registry:
    check(source["license_policy"] in valid_policies, f"invalid license policy: {source['repo']}")
    if source.get("license_spdx") is None and source["license_policy"] == "ALLOW":
        errors.append(f"unlicensed source cannot be ALLOW: {source['repo']}")

for entry in ingestion.get("sources", []):
    source = by_id.get(entry["source_id"])
    check(source is not None, f"ingestion manifest references unknown source: {entry['source_id']}")
    if source:
        check(source["license_policy"] == "ALLOW", f"auto-ingestion source is not ALLOW: {source['repo']}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(
    f"Knowledge base validation passed: {len(registry)} sources; "
    f"Zhouyi=64 hexagrams/{line_count} lines/5 Ten-Wings sections; "
    f"Bazi shensha={len(shensha['items'])}; Ziwei=14 major stars; "
    f"Qimen=9 palaces/24 solar-term bureaus; "
    f"Daliuren bibliography={liuren_catalog['record_count']}; "
    f"Taiyi bibliography={taiyi_catalog['record_count']}."
)
