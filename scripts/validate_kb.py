#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
seed = json.loads((ROOT / "data/canonical/seed.json").read_text(encoding="utf-8"))
registry = json.loads((ROOT / "config/source_registry.json").read_text(encoding="utf-8"))["sources"]

errors = []
if len(seed.get("wuxing", [])) != 5:
    errors.append("wuxing must contain 5 elements")
if len(seed.get("heavenly_stems", [])) != 10:
    errors.append("heavenly_stems must contain 10 stems")
if len(seed.get("earthly_branches", [])) != 12:
    errors.append("earthly_branches must contain 12 branches")
if len(seed.get("trigrams", [])) != 8:
    errors.append("trigrams must contain 8 trigrams")
if len(seed.get("hexagrams", [])) != 64:
    errors.append("hexagrams must contain 64 hexagrams")
if len({x[0] for x in seed.get("hexagrams", [])}) != 64:
    errors.append("hexagram King Wen numbers must be unique")
if len(seed.get("liuyao", {}).get("najia", {})) != 8:
    errors.append("liuyao.najia must contain 8 pure trigrams")

valid_policies = {"ALLOW","REFERENCE_ONLY","PUBLIC_DOMAIN_EXTRACT_ONLY","NON_COMMERCIAL","COPYLEFT","QUARANTINE"}
if len({x["repo"] for x in registry}) != len(registry):
    errors.append("duplicate source repositories")
for source in registry:
    if source["license_policy"] not in valid_policies:
        errors.append(f"invalid license policy: {source['repo']}")
    if source.get("license_spdx") is None and source["license_policy"] == "ALLOW":
        errors.append(f"unlicensed source cannot be ALLOW: {source['repo']}")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)

print(f"Knowledge base validation passed: {len(registry)} sources, 64 hexagrams.")
