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
    description="Apply only confirmed Sanming Tonghui PUA collation mappings."
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
        "replacement": replacement,
        "count": actual,
    })

remaining = private_use_counts(text)
report = {
    "source": source_path.as_posix(),
    "mapping": mapping_path.as_posix(),
    "applied_mappings": len(applied),
    "applied_occurrences": sum(x["count"] for x in applied),
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
