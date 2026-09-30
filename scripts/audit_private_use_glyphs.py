#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("--output")
parser.add_argument("--contexts", type=int, default=3)
args = parser.parse_args()

path = Path(args.path)
text = path.read_text(encoding="utf-8")
rows: dict[str, dict] = {}

for index, ch in enumerate(text):
    cp = ord(ch)
    if not (
        0xE000 <= cp <= 0xF8FF
        or 0xF0000 <= cp <= 0xFFFFD
        or 0x100000 <= cp <= 0x10FFFD
    ):
        continue
    row = rows.setdefault(ch, {
        "glyph": ch,
        "codepoint": f"U+{cp:04X}",
        "count": 0,
        "contexts": [],
    })
    row["count"] += 1
    if len(row["contexts"]) < args.contexts:
        context = text[max(0, index - 45): index + 46]
        row["contexts"].append(" ".join(context.split()))

payload = {
    "path": path.as_posix(),
    "total_private_use_chars": sum(x["count"] for x in rows.values()),
    "unique_private_use_chars": len(rows),
    "glyphs": sorted(rows.values(), key=lambda x: (-x["count"], x["codepoint"])),
}
rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
if args.output:
    Path(args.output).write_text(rendered, encoding="utf-8")
else:
    print(rendered, end="")

raise SystemExit(1 if rows else 0)
