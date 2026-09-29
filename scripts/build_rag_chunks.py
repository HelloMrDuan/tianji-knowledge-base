#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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

    # Tarot: one card / spread per chunk.
    if path.name == "rws_cn_v1.json":
        for card in obj["cards"]:
            text = f"{card['name_cn']} / {card['name_en']}\n正位：{card['upright']}\n逆位：{card['reversed']}"
            add(domain, "tarot_card", f"card:{card['id']}", text, obj, path, {"card_id": card["id"], "arcana_type": card["arcana_type"]})
        for spread in obj["spreads"]:
            text = f"{spread['name']}，{spread['cards_num']}张牌。位置：{dump_text(spread['representations'])}"
            add(domain, "tarot_spread", f"spread:{spread['name']}", text, obj, path, {"spread": spread["name"]})
        continue

    # Catalog/bibliography files: one record per work.
    if obj.get("source_level") == "bibliography" and isinstance(obj.get("records"), list):
        for i, rec in enumerate(obj["records"]):
            add(domain, "bibliography", f"bib:{i}:{rec.get('title','')}", dump_text(rec), obj, path, {"title": rec.get("title"), "author": rec.get("author"), "era": rec.get("era")})
        continue

    # Generic canonical file: preserve the entire structured object as a retrievable chunk.
    add(domain, str(topic), "document", dump_text(obj), obj, path)

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
