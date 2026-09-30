#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def is_private_use(ch: str) -> bool:
    cp = ord(ch)
    return (
        0xE000 <= cp <= 0xF8FF
        or 0xF0000 <= cp <= 0xFFFFD
        or 0x100000 <= cp <= 0x10FFFD
    )


parser = argparse.ArgumentParser(
    description="Apply confirmed context-anchored non-PUA text corrections to Sanming Tonghui."
)
parser.add_argument("source")
parser.add_argument("mapping")
parser.add_argument("--output")
parser.add_argument("--report")
args = parser.parse_args()

source_path = Path(args.source)
mapping_path = Path(args.mapping)
text = source_path.read_text(encoding="utf-8")
spec = json.loads(mapping_path.read_text(encoding="utf-8"))

applied: list[dict] = []
seen_ids: set[str] = set()
for row in spec.get("corrections", []):
    if row.get("status") != "confirmed":
        continue
    correction_id = row.get("id")
    old = row.get("old", "")
    new = row.get("new", "")
    if not correction_id or correction_id in seen_ids:
        raise SystemExit(f"invalid or duplicate correction id: {correction_id!r}")
    seen_ids.add(correction_id)
    if not old or not new or old == new:
        raise SystemExit(f"invalid text correction: {correction_id}")
    if any(is_private_use(ch) for ch in old + new):
        raise SystemExit(
            f"text correction must operate after PUA collation and contain no PUA: {correction_id}"
        )
    actual = text.count(old)
    if actual != 1:
        raise SystemExit(
            f"text anchor drift for {correction_id}: expected one exact anchor, found {actual}"
        )
    if text.count(new):
        raise SystemExit(
            f"text correction target already exists before applying {correction_id}; "
            "anchor may be stale or over-broad"
        )
    text = text.replace(old, new, 1)
    applied.append({"id": correction_id, "old": old, "new": new})

remaining_pua = sum(1 for ch in text if is_private_use(ch))
report = {
    "source": source_path.as_posix(),
    "mapping": mapping_path.as_posix(),
    "confirmed_corrections": sum(
        1 for row in spec.get("corrections", []) if row.get("status") == "confirmed"
    ),
    "applied_corrections": len(applied),
    "remaining_private_use_chars": remaining_pua,
    "review_status": spec.get("summary", {}).get("review_status"),
    "canonical_ready": bool(spec.get("summary", {}).get("canonical_ready")),
    "applied": applied,
}
rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
if args.report:
    Path(args.report).write_text(rendered, encoding="utf-8")
else:
    print(rendered, end="")

if args.output:
    output_path = Path(args.output)
    if "data/canonical/" in output_path.as_posix() and not report["canonical_ready"]:
        raise SystemExit(
            "refusing canonical output while Sanming text-quality review is still in progress"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
