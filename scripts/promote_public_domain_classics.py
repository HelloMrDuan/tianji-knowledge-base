#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "data/quarantine/public_domain_snapshots"
MANIFEST = json.loads((ROOT / "config/public_domain_manifest.json").read_text(encoding="utf-8"))
SUMMARY = json.loads((SNAP / "_sync_summary.json").read_text(encoding="utf-8"))

def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def parse_angle_markers(text: str) -> list[dict]:
    matches = list(re.finditer(r"[《【]([^》】\n]{2,60})[》】]", text))
    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = re.sub(r"\s+", "", match.group(1)).strip()
        body = clean_text(text[start:end])
        if len(body) >= 8:
            sections.append({"id": len(sections) + 1, "title": title, "text": body})
    return sections

QIONGTONG_HEADER = re.compile(
    r"^(?:五行总论|论[木火土金水甲乙丙丁戊己庚辛壬癸]{1,4}|"
    r"三[春夏秋冬][甲乙丙丁戊己庚辛壬癸][木火土金水](?:总论)?|"
    r"(?:正|二|三|四|五|六|七|八|九|十|十一|十二)月"
    r"[甲乙丙丁戊己庚辛壬癸][木火土金水])[：:]?$"
)

def parse_qiongtong(text: str) -> list[dict]:
    sections = []
    current_title = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_lines
        if current_title is None:
            return
        body = clean_text("\n".join(current_lines))
        if len(body) >= 8:
            sections.append({"id": len(sections) + 1, "title": current_title, "text": body})
        current_lines = []

    for line in text.replace("\r", "").split("\n"):
        stripped = line.strip()
        if QIONGTONG_HEADER.match(stripped):
            flush()
            current_title = re.sub(r"[：:]$", "", stripped)
        elif current_title is not None:
            current_lines.append(line)
    flush()
    return sections

CHINESE_NUM = "一二三四五六七八九十百"

def parse_ditiansui(text: str) -> list[dict]:
    """Split 滴天髓阐微 into the 34 通神论 and 29 六亲论 topics."""
    lines = [line.strip() for line in text.replace("\r", "").split("\n")]
    try:
        start = lines.index("通神论")
    except ValueError as exc:
        raise SystemExit("ditiansui: body marker 通神论 not found") from exc

    numbered = re.compile(rf"^([{CHINESE_NUM}]+)[、\s]+(.{{1,24}})$")
    sections: list[dict] = []
    group = ""
    current_title: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_lines
        if current_title is None:
            return
        body = clean_text("\n".join(current_lines))
        if len(body) >= 8:
            sections.append({
                "id": len(sections) + 1,
                "title": f"{group}·{current_title}",
                "group": group,
                "text": body,
            })
        current_lines = []

    for line in lines[start:]:
        if line in {"通神论", "六亲论"}:
            flush()
            current_title = None
            group = line
            continue
        match = numbered.match(line)
        if match:
            flush()
            current_title = f"{match.group(1)}、{match.group(2).strip()}"
            continue
        if current_title is not None:
            current_lines.append(line)
    flush()
    return sections

SANMING_VOLUME_RE = re.compile(
    rf"钦定四库全书\s+三命通(?:会|防)卷([{CHINESE_NUM}]+)\s+明\s*万民英\s*撰"
)

def parse_sanming(text: str) -> list[dict]:
    """Preserve 三命通会 as twelve volume-level canonical sections."""
    matches = list(SANMING_VOLUME_RE.finditer(text))
    if len(matches) != 12:
        raise SystemExit(f"sanming: expected 12 volume starts, got {len(matches)}")
    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        body = re.sub(r"<子部,[^>]+>", "", body)
        body = re.sub(
            rf"\n\s*三命通(?:会|防)卷[{CHINESE_NUM}]+\s*$",
            "",
            body,
        )
        body = clean_text(body)
        if len(body) >= 100:
            sections.append({
                "id": len(sections) + 1,
                "title": f"卷{match.group(1)}",
                "volume": match.group(1),
                "text": body,
            })
    return sections

PARSERS = {
    "angle_markers": parse_angle_markers,
    "qiongtong_headings": parse_qiongtong,
    "ditiansui_sections": parse_ditiansui,
    "sanming_volumes": parse_sanming,
}

thresholds = {
    "yuanhai_ziping": {"min_sections": 180, "min_chars": 55000},
    "qiongtong_baojian": {"min_sections": 95, "min_chars": 30000},
    "ditiansui_chanwei": {"min_sections": 63, "min_chars": 120000},
    "sanming_tonghui": {"min_sections": 12, "min_chars": 450000},
}

promoted = []
for group in MANIFEST["sources"]:
    source_id = group["source_id"]
    for work in group.get("works", []):
        if work.get("promotion") != "canonical":
            continue
        work_id = work["id"]
        parser_name = work.get("parser")
        parser = PARSERS.get(parser_name)
        if not parser:
            raise SystemExit(f"no parser for canonical public-domain work: {work_id}/{parser_name}")

        row = SUMMARY["works"].get(work_id)
        if not row or row.get("status") != "ok":
            raise SystemExit(f"snapshot missing or failed: {work_id}")

        snapshot = ROOT / row["snapshot_path"]
        text = snapshot.read_text(encoding="utf-8")
        corrections_applied = []
        for correction in work.get("collation_corrections", []):
            before = correction["from"]
            after = correction["to"]
            count = text.count(before)
            if count != 1:
                raise SystemExit(
                    f"{work_id}: correction token must occur exactly once: {before!r}, got {count}"
                )
            text = text.replace(before, after, 1)
            corrections_applied.append({
                "from": before,
                "to": after,
                "evidence": correction.get("evidence"),
            })

        replacement_chars = len(re.findall(r"[□�]", text))
        if replacement_chars:
            raise SystemExit(f"{work_id}: unresolved replacement chars={replacement_chars}")

        sections = parser(text)
        total_chars = sum(len(x["text"]) for x in sections)
        guard = thresholds.get(work_id, {})
        if len(sections) < guard.get("min_sections", 1):
            raise SystemExit(f"{work_id}: too few sections: {len(sections)}")
        if total_chars < guard.get("min_chars", 1):
            raise SystemExit(f"{work_id}: text unexpectedly short: {total_chars}")

        out = {
            "schema_version": "0.2",
            "domain": work["domain"],
            "corpus": work["title"],
            "source_level": "L0-public-domain-classic",
            "section_count": len(sections),
            "provenance": {
                "repo": row["repo"],
                "path": row["source_path"],
                "commit": row["commit"],
                "license_policy": "PUBLIC_DOMAIN_EXTRACT_ONLY",
            },
            "cleaning": {
                "replacement_chars": replacement_chars,
                "parser": parser_name,
                "snapshot_sha256": row["sha256"],
                "wording_policy": (
                    "Whitespace normalized; wording otherwise preserved except explicitly "
                    "recorded collation corrections."
                ),
                "collation_corrections": corrections_applied,
            },
            "sections": sections,
        }
        output = ROOT / work["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        promoted.append({
            "id": work_id,
            "output": output.relative_to(ROOT).as_posix(),
            "sections": len(sections),
            "chars": total_chars,
            "commit": row["commit"],
            "collation_corrections": len(corrections_applied),
        })

print(json.dumps({"promoted": promoted}, ensure_ascii=False, indent=2))
