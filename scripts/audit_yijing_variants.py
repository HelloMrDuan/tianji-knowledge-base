#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_jsonl(path: str):
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines() if line.strip()]


VARIANTS = str.maketrans({
    "遯": "遁", "說": "说", "兌": "兑", "爲": "为", "見": "见", "無": "无",
    "與": "与", "後": "后", "來": "来", "萬": "万", "國": "国", "貞": "贞",
    "亨": "亨", "乾": "乾", "坤": "坤"
})


def norm(text: str | None) -> str:
    if not text:
        return ""
    text = text.translate(VARIANTS)
    return re.sub(r"[\\s，。；：、“”‘’《》！？,.!?;:（）()【】\[\]·—-]", "", text)


zhouyi = load_json("data/canonical/classics/yijing/zhouyi-64.json")["items"]
tuan = {x["king_wen_no"]: x for x in load_json("data/canonical/yijing/tuan-xiang.json")["items"]}
cross = {x["king_wen_no"]: x for x in load_jsonl("data/index/yijing-crosscheck-sections.jsonl")}

checks = []
summary = {"judgment": 0, "great_image": 0, "line": 0, "tuan": 0}
matched = {"judgment": 0, "great_image": 0, "line": 0, "tuan": 0}

for item in zhouyi:
    no = item["king_wen_no"]
    section = cross.get(no, {}).get("text", "")
    section_n = norm(section)

    def record(kind: str, label: str, expected: str | None):
        summary[kind] += 1
        ok = bool(expected) and norm(expected) in section_n
        matched[kind] += int(ok)
        if not ok:
            checks.append({
                "hexagram_no": no,
                "hexagram": item["full_name"],
                "kind": kind,
                "label": label,
                "canonical_text": expected,
                "crosscheck_source": "fundgao/DAO_DE_JING",
                "crosscheck_path": "周易/README.md",
                "status": "VARIANT_OR_NOT_FOUND",
                "action": "REVIEW_ONLY_DO_NOT_AUTO_OVERWRITE",
            })

    record("judgment", "卦辞", item["judgment"])
    record("great_image", "大象", item["great_image"])
    for i, line in enumerate(item["lines"], 1):
        record("line", f"第{i}爻", line)
    tx = tuan.get(no, {})
    record("tuan", "彖传", tx.get("tuan"))

# Separate primary-vs-secondary structured comparison for 大象.
structured_variants = []
for item in zhouyi:
    no = item["king_wen_no"]
    second = tuan.get(no, {})
    if norm(item.get("great_image")) != norm(second.get("da_xiang")):
        structured_variants.append({
            "hexagram_no": no,
            "hexagram": item["full_name"],
            "kind": "great_image_structured_variant",
            "primary": item.get("great_image"),
            "secondary": second.get("da_xiang"),
            "primary_source": item.get("provenance"),
            "secondary_source": second.get("provenance"),
            "action": "REVIEW_ONLY_DO_NOT_AUTO_OVERWRITE",
        })

report = {
    "schema_version": "0.1",
    "policy": "Cross-source differences are evidence for review, never automatic canonical replacement.",
    "sources": {
        "primary": "hhszzzz/taibu packages/core (MIT)",
        "secondary_structured": "godcong/yi (MIT)",
        "secondary_full_section": "fundgao/DAO_DE_JING 周易/README.md (MIT)",
    },
    "coverage": summary,
    "matched_by_normalized_containment": matched,
    "variant_or_not_found_count": len(checks),
    "structured_great_image_variant_count": len(structured_variants),
    "variants": checks,
    "structured_variants": structured_variants,
}
out = ROOT / "data/audit/yijing_crosscheck.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "coverage": summary,
    "matched": matched,
    "variants": len(checks),
    "structured_great_image_variants": len(structured_variants),
}, ensure_ascii=False))
