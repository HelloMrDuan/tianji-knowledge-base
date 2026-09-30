#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def is_private_use(ch: str) -> bool:
    cp = ord(ch)
    return (
        0xE000 <= cp <= 0xF8FF
        or 0xF0000 <= cp <= 0xFFFFD
        or 0x100000 <= cp <= 0x10FFFD
    )


def private_use_counts(text: str) -> Counter[str]:
    return Counter(ch for ch in text if is_private_use(ch))


parser = argparse.ArgumentParser(
    description="Apply confirmed Sanming Tonghui PUA collation mappings."
)
parser.add_argument("source")
parser.add_argument("mapping")
parser.add_argument("--output")
parser.add_argument("--report")
parser.add_argument(
    "--allow-unresolved",
    action="store_true",
    help="Permit writing a partial result outside data/canonical while unresolved PUA remain.",
)
args = parser.parse_args()

source_path = Path(args.source)
mapping_path = Path(args.mapping)
text = source_path.read_text(encoding="utf-8")
spec = json.loads(mapping_path.read_text(encoding="utf-8"))

seen: set[str] = set()
applied: list[dict] = []

# Uniform mappings: one PUA codepoint always represents the same replacement.
for row in spec.get("mappings", []):
    if row.get("status") != "confirmed":
        continue
    glyph = row.get("glyph", "")
    replacement = row.get("replacement", "")
    codepoint = row.get("codepoint")
    if len(glyph) != 1 or not is_private_use(glyph):
        raise SystemExit(f"invalid PUA glyph mapping: {codepoint}")
    if codepoint != f"U+{ord(glyph):04X}":
        raise SystemExit(f"codepoint/glyph mismatch: {codepoint}")
    if glyph in seen:
        raise SystemExit(f"duplicate mapping for {codepoint}")
    seen.add(glyph)
    if not replacement or any(is_private_use(ch) for ch in replacement):
        raise SystemExit(f"invalid replacement for {codepoint}")
    expected = int(row.get("count", -1))
    actual = text.count(glyph)
    if actual != expected:
        raise SystemExit(
            f"source drift for {codepoint}: expected {expected} occurrences, found {actual}"
        )
    text = text.replace(glyph, replacement)
    applied.append({
        "codepoint": codepoint,
        "mode": "uniform",
        "replacement": replacement,
        "count": actual,
    })

# Contextual mappings: the same source PUA codepoint was reused for different
# intended glyphs. Each rule is anchored by an exact, unique source substring.
for row in spec.get("contextual_mappings", []):
    if row.get("status") != "confirmed":
        continue
    glyph = row.get("glyph", "")
    codepoint = row.get("codepoint")
    if len(glyph) != 1 or not is_private_use(glyph):
        raise SystemExit(f"invalid contextual PUA glyph mapping: {codepoint}")
    if codepoint != f"U+{ord(glyph):04X}":
        raise SystemExit(f"contextual codepoint/glyph mismatch: {codepoint}")
    if glyph in seen:
        raise SystemExit(f"duplicate uniform/contextual mapping for {codepoint}")
    seen.add(glyph)

    expected = int(row.get("count", -1))
    actual_before = text.count(glyph)
    if actual_before != expected:
        raise SystemExit(
            f"source drift for contextual {codepoint}: expected {expected} occurrences, found {actual_before}"
        )

    resolved = 0
    rules = row.get("replacements", [])
    if not rules:
        raise SystemExit(f"contextual mapping has no replacement rules: {codepoint}")
    for index, rule in enumerate(rules, start=1):
        old = rule.get("old", "")
        new = rule.get("new", "")
        rule_count = int(rule.get("count", -1))
        if not old or not new:
            raise SystemExit(f"invalid contextual rule {codepoint}#{index}")
        if any(is_private_use(ch) for ch in new):
            raise SystemExit(f"contextual replacement still contains PUA: {codepoint}#{index}")
        if old.count(glyph) != rule_count:
            raise SystemExit(
                f"contextual rule count mismatch {codepoint}#{index}: "
                f"old anchor contains {old.count(glyph)} PUA glyphs, declared {rule_count}"
            )
        matches = text.count(old)
        if matches != 1:
            raise SystemExit(
                f"contextual anchor drift {codepoint}#{index}: expected one exact anchor, found {matches}"
            )
        text = text.replace(old, new, 1)
        resolved += rule_count

    if resolved != expected:
        raise SystemExit(
            f"contextual replacement total mismatch for {codepoint}: "
            f"expected {expected}, resolved {resolved}"
        )
    if glyph in text:
        raise SystemExit(f"contextual mapping left unresolved occurrences for {codepoint}")
    applied.append({
        "codepoint": codepoint,
        "mode": "contextual",
        "replacement_rules": len(rules),
        "count": resolved,
    })

remaining = private_use_counts(text)
report = {
    "source": source_path.as_posix(),
    "mapping": mapping_path.as_posix(),
    "applied_mappings": len(applied),
    "applied_occurrences": sum(x["count"] for x in applied),
    "contextual_mappings": sum(1 for x in applied if x["mode"] == "contextual"),
    "remaining_unique_codepoints": len(remaining),
    "remaining_occurrences": sum(remaining.values()),
    "remaining": [
        {
            "glyph": glyph,
            "codepoint": f"U+{ord(glyph):04X}",
            "count": count,
        }
        for glyph, count in sorted(remaining.items(), key=lambda x: (-x[1], ord(x[0])))
    ],
}
rendered_report = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
if args.report:
    Path(args.report).write_text(rendered_report, encoding="utf-8")
else:
    print(rendered_report, end="")

if args.output:
    output_path = Path(args.output)
    canonical_target = "data/canonical/" in output_path.as_posix()
    if remaining and canonical_target:
        raise SystemExit("refusing to write unresolved PUA into data/canonical")
    if remaining and not args.allow_unresolved:
        raise SystemExit(
            "unresolved PUA remain; pass --allow-unresolved only for quarantine/intermediate output"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

raise SystemExit(2 if remaining and not args.allow_unresolved else 0)
