#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from tianji_kb.knowledge_index import iter_phase1_chunks

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/canonical"
OUT = ROOT / "build/rag_chunks.jsonl"

def stable_id(parts: list[str]) -> str:
    raw = "::".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def dump_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def split_text_chunks(text: str, max_chars: int = 2600) -> list[str]:
    """Split long classical sections without changing canonical text."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []

    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for paragraph in [x for x in text.split("\n") if x.strip()]:
        paragraph = paragraph.strip()
        if len(paragraph) > max_chars:
            if buf:
                chunks.append("\n".join(buf).strip())
                buf, size = [], 0
            for start in range(0, len(paragraph), max_chars):
                chunks.append(paragraph[start:start + max_chars])
            continue
        added = len(paragraph) + (1 if buf else 0)
        if buf and size + added > max_chars:
            chunks.append("\n".join(buf).strip())
            buf, size = [], 0
        buf.append(paragraph)
        size += added
    if buf:
        chunks.append("\n".join(buf).strip())
    return [x for x in chunks if x]

def source_meta(obj: dict) -> dict:
    p = obj.get("provenance") or {}
    if "repo" in p:
        return {
            "repo": p.get("repo"),
            "path": p.get("path"),
            "commit": p.get("commit") or p.get("upstream_commit"),
        }
    primary = p.get("primary") or {}
    return {
        "repo": primary.get("repo"),
        "path": primary.get("path"),
        "commit": primary.get("commit"),
    }

chunks: list[dict] = []

def add(domain: str, topic: str, key: str, text: str, obj: dict, path: Path, extra: dict | None = None):
    text = text.strip()
    if not text:
        return
    rel = path.relative_to(ROOT).as_posix()
    meta = {
        "domain": domain,
        "topic": topic,
        "source_level": obj.get("source_level"),
        "ruleset": obj.get("ruleset"),
        "school": obj.get("school"),
        "license": obj.get("license"),
        "canonical_path": rel,
        **source_meta(obj),
    }
    if extra:
        meta.update(extra)
    chunks.append({
        "id": stable_id([rel, key]),
        "text": text,
        "metadata": meta,
    })

for path in sorted(CANONICAL.rglob("*.json")):
    if "/batches/" in path.as_posix() or path.name == "seed.json":
        continue
    obj = json.loads(path.read_text(encoding="utf-8"))
    domain = obj.get("domain") or path.parent.name
    topic = obj.get("topic") or obj.get("corpus") or obj.get("ruleset") or path.stem

    # Reviewed Phase 1 entities are emitted separately with resolved citations.
    if obj.get("model") == "phase1-knowledge":
        continue

    # Zhouyi 64 hexagrams.
    if path.name == "zhouyi_classic_core.json":
        for rec in obj["records"]:
            base = f"{rec['number']} {rec['full_name']}\n卦辞：{rec['judgment']}\n大象：{rec.get('image','')}"
            add(domain, "hexagram", str(rec["number"]), base, obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"]})
            for line in rec.get("lines", []):
                add(domain, "hexagram_line", f"{rec['number']}:{line['position']}", f"{rec['full_name']} {line['position']}：{line['text']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"], "line": line["position"]})
            if rec.get("special_use"):
                s = rec["special_use"]
                add(domain, "hexagram_special_use", f"{rec['number']}:{s['position']}", f"{rec['full_name']} {s['position']}：{s['text']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"], "line": s["position"]})
        continue

    # Tuan / Xiang / Wenyan.
    if path.name == "tuan_xiang_wenyan_v1.json":
        for rec in obj["records"]:
            add(domain, "tuan", f"{rec['number']}:tuan", f"{rec['full_name']}《彖》：{rec['tuan']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"]})
            add(domain, "great_image", f"{rec['number']}:xiang", f"{rec['full_name']}《大象》：{rec['great_image']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"]})
            for line in rec.get("line_images", []):
                add(domain, "line_image", f"{rec['number']}:xiang:{line['position']}", f"{rec['full_name']} {line['position']}《小象》：{line['text']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"], "line": line["position"]})
            if rec.get("wenyan"):
                add(domain, "wenyan", f"{rec['number']}:wenyan", f"{rec['full_name']}《文言》：{rec['wenyan']}", obj, path, {"hexagram_number": rec["number"], "hexagram": rec["full_name"]})
        continue

    # Ten Wings long-form text: keep one section per file; embedding layer may chunk further.
    if "/ten_wings/" in path.as_posix():
        text = obj.get("normalized_text") or obj.get("text") or ""
        add(domain, "ten_wings", obj.get("section", path.stem), text, obj, path, {"section": obj.get("section")})
        continue

    # Public-domain classical corpora: split very long volumes/chapters into retrieval-size chunks.
    if obj.get("source_level") == "L0-public-domain-classic" and isinstance(obj.get("sections"), list):
        for section in obj["sections"]:
            title = section.get("title") or f"section-{section.get('id')}"
            parts = split_text_chunks(section.get("text", ""))
            for part_no, part in enumerate(parts, start=1):
                suffix = f" · {part_no}/{len(parts)}" if len(parts) > 1 else ""
                add(
                    domain,
                    "classic_section",
                    f"section:{section.get('id')}:{title}:part:{part_no}",
                    f"{obj.get('corpus','')} · {title}{suffix}\n{part}",
                    obj,
                    path,
                    {
                        "corpus": obj.get("corpus"),
                        "section_id": section.get("id"),
                        "section_title": title,
                        "part": part_no,
                        "part_count": len(parts),
                    },
                )
        continue

    # Fengshui 24 mountains: one sector per chunk for degree/name lookup.
    if path.name == "twenty_four_mountains_v1.json":
        for rec in obj.get("records", []):
            wrap = "跨0度" if rec.get("wraps_zero") else ""
            text_value = (
                f"二十四山 {rec['mountain']}山 {rec['compass_label']} {rec['direction']} "
                f"中心{rec['center_degrees']}° 范围{rec['start_degrees']}°至{rec['end_degrees']}° {wrap} "
                f"类型{rec['type']} 五行{rec['element']} "
                f"对宫{rec['opposite']['mountain']}山({rec['opposite']['compass_label']})"
            )
            add(
                domain,
                "twenty_four_mountain",
                f"mountain:{rec['index']}:{rec['mountain']}",
                text_value,
                obj,
                path,
                {
                    "mountain": rec["mountain"],
                    "compass_label": rec["compass_label"],
                    "center_degrees": rec["center_degrees"],
                },
            )
        continue

    # Tarot: one card / spread per chunk.
    if path.name == "rws_cn_v1.json":
        for card in obj["cards"]:
            text = f"{card['name_cn']} / {card['name_en']}\n正位：{card['upright']}\n逆位：{card['reversed']}"
            add(domain, "tarot_card", f"card:{card['id']}", text, obj, path, {"card_id": card["id"], "arcana_type": card["arcana_type"]})
        for spread in obj["spreads"]:
            text = f"{spread['name']}，{spread['cards_num']}张牌。位置：{dump_text(spread['representations'])}"
            add(domain, "tarot_spread", f"spread:{spread['name']}", text, obj, path, {"spread": spread["name"]})
        continue

    # Daliuren/Taiyi deterministic rules: split by top-level rule section so
    # retrieval can answer a specific algorithm question without dragging the entire engine contract.
    if path.name == "rules_v1.json" and domain in {"liuren", "taiyi"}:
        skip = {"schema_version", "domain", "ruleset", "source_level", "license", "provenance"}
        labels = {
            "liuren": {
                "inputs": "输入",
                "month_general_by_solar_terms": "月将",
                "stem_lodging": "十干寄宫",
                "earth_sky_plate": "天地盘",
                "four_lessons": "四课",
                "three_transmissions": "三传",
                "branch_relations": "地支关系",
                "day_night": "昼夜",
                "heavenly_generals": "十二天将",
                "output_contract": "输出契约",
            },
            "taiyi": {
                "calculation_modes": "计法模式",
                "classical_methods": "古法公式",
                "accumulated_number": "积数",
                "board_number": "局式",
                "taiyi_palace": "太乙落宫",
                "luoshu_outer_order": "洛书外八宫",
                "eight_doors": "八门",
                "sixteen_palaces": "十六宫",
                "principal_calculations": "主客定算",
                "core_output": "核心输出",
                "extended_layers": "扩展层",
                "output_invariant": "输出约束",
            },
        }
        for key, value in obj.items():
            if key in skip:
                continue
            label = labels.get(domain, {}).get(key, key)
            add(
                domain,
                f"{domain}_rule",
                f"rule:{key}",
                f"{label}（{key}）：{dump_text(value)}",
                obj,
                path,
                {"rule_section": key, "rule_label": label},
            )
        continue

    # Catalog/bibliography files: one record per work.
    if obj.get("source_level") == "bibliography" and isinstance(obj.get("records"), list):
        for i, rec in enumerate(obj["records"]):
            add(domain, "bibliography", f"bib:{i}:{rec.get('title','')}", dump_text(rec), obj, path, {"title": rec.get("title"), "author": rec.get("author"), "era": rec.get("era")})
        continue

    # Generic canonical file: preserve the entire structured object as a retrievable chunk.
    add(domain, str(topic), "document", dump_text(obj), obj, path)

chunks.extend(iter_phase1_chunks(ROOT))

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8") as f:
    for row in chunks:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

summary = {}
for row in chunks:
    d = row["metadata"]["domain"]
    summary[d] = summary.get(d, 0) + 1

print(json.dumps({
    "chunk_count": len(chunks),
    "domain_counts": dict(sorted(summary.items())),
    "output": OUT.relative_to(ROOT).as_posix(),
}, ensure_ascii=False, indent=2))
