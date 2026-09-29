#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def load_json(path: str):
    return json.loads(read_text(path))


def write_json(path: str, obj) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: str, rows: list[dict]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")


def source_commit(source_id: str) -> str | None:
    path = ROOT / "data/state/source_state.json"
    if not path.exists():
        return None
    state = json.loads(path.read_text(encoding="utf-8"))
    return (state.get("sources", {}).get(source_id) or {}).get("head_sha")


def split_long(text: str, max_chars: int = 1100) -> list[str]:
    units = [x for x in re.split(r"(?<=[。！？；\n])", text) if x]
    out, buf = [], ""
    for unit in units:
        if len(unit) > max_chars:
            if buf.strip():
                out.append(buf.strip())
                buf = ""
            for i in range(0, len(unit), max_chars):
                part = unit[i:i + max_chars].strip()
                if part:
                    out.append(part)
            continue
        if buf and len(buf) + len(unit) > max_chars:
            out.append(buf.strip())
            buf = unit
        else:
            buf += unit
    if buf.strip():
        out.append(buf.strip())
    return out


def chunk_document(text: str, max_chars: int = 1100, assembled_max: int = 1200) -> list[str]:
    pieces: list[str] = []
    for paragraph in [x.strip() for x in re.split(r"\n\s*\n+", text.strip()) if x.strip()]:
        pieces.extend(split_long(paragraph, max_chars=max_chars))
    chunks, buf = [], ""
    for piece in pieces:
        candidate = f"{buf}\n\n{piece}" if buf else piece
        if buf and len(candidate) > assembled_max:
            chunks.append(buf.strip())
            buf = piece
        else:
            buf = candidate
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def split_markdown(text: str, max_chars: int = 1100) -> list[dict]:
    sections, title, buf = [], "", []

    def flush():
        nonlocal buf
        body = "\n".join(buf).strip()
        if body:
            sections.append({"title": title, "text": body})
        buf = []

    for line in text.splitlines():
        match = re.match(r"^(#{1,4})\s+(.+)", line)
        if match:
            flush()
            title = match.group(2).strip()
            buf.append(line)
        else:
            buf.append(line)
    flush()

    out: list[dict] = []
    for section in sections:
        if len(section["text"]) <= max_chars:
            out.append(section)
            continue
        for part in split_long(section["text"], max_chars=max_chars):
            out.append({"title": section["title"], "text": part})
    return out


def ts_object_body(content: str, name: str) -> str:
    marker = f"export const {name}"
    start = content.find(marker)
    if start < 0:
        raise RuntimeError(f"missing TypeScript marker: {name}")
    open_pos = content.find("{", start)
    close_pos = content.find("\n};", open_pos)
    if open_pos < 0 or close_pos < 0:
        raise RuntimeError(f"malformed TypeScript object: {name}")
    return content[open_pos + 1:close_pos]


def parse_ts_string_map(body: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in body.splitlines():
        m = re.match(r'^\s*"([^"]+)":\s*"([^"]*)",?\s*$', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def parse_ts_array_map(body: str) -> dict[str, list[str]]:
    keys = list(re.finditer(r'^\s*"([^"]+)":\s*\[', body, flags=re.M))
    out: dict[str, list[str]] = {}
    for i, match in enumerate(keys):
        end = keys[i + 1].start() if i + 1 < len(keys) else len(body)
        block = body[match.start():end]
        out[match.group(1)] = [
            m.group(1)
            for m in re.finditer(r'^\s*"([^"]*)",?\s*$', block, flags=re.M)
        ]
    return out


def rebuild_yijing() -> dict:
    seed = load_json("data/canonical/seed.json")
    taibu = read_text("data/upstream/taibu-core/hexagrams.ts")
    judgments = parse_ts_string_map(ts_object_body(taibu, "GUA_CI"))
    images = parse_ts_string_map(ts_object_body(taibu, "XIANG_CI"))
    lines = parse_ts_array_map(ts_object_body(taibu, "YAO_CI"))
    aliases = {"天山遁": "天山遯"}
    taibu_commit = source_commit("taibu")

    items = []
    for no, name, full_name, upper, lower in seed["hexagrams"]:
        source_name = aliases.get(full_name, full_name)
        item = {
            "id": f"yijing.hexagram.{no:02d}",
            "king_wen_no": no,
            "name": name,
            "full_name": full_name,
            "source_name": source_name,
            "upper": upper,
            "lower": lower,
            "judgment": judgments.get(source_name),
            "great_image": images.get(source_name),
            "lines": lines.get(source_name, []),
            "provenance": {
                "repo": "hhszzzz/taibu",
                "path": "packages/core/src/data/hexagrams.ts",
                "commit": taibu_commit,
                "license": "MIT (packages/core)",
            },
            "text_classification": "classical text in an explicitly MIT-licensed subpackage",
        }
        if not item["judgment"] or not item["great_image"] or len(item["lines"]) != 6:
            raise RuntimeError(f"incomplete Zhouyi item: {no} {full_name}")
        items.append(item)

    if len(items) != 64 or sum(len(x["lines"]) for x in items) != 384:
        raise RuntimeError("Zhouyi completeness invariant failed")

    write_json("data/canonical/classics/yijing/zhouyi-64.json", {
        "schema_version": "0.2", "work": "周易经文核心",
        "hexagram_count": 64, "line_count": 384, "aliases": aliases, "items": items,
    })

    bagua = load_json("data/upstream/godcong-yi/bagua.json")
    god_commit = source_commit("godcong-yi")
    trigrams = [{
        "id": f"yijing.trigram.{x['name']}", "name": x["name"], "symbol": x["symbol"],
        "xian_tian_num": x.get("xian_tian_num"), "hou_tian_num": x.get("hou_tian_num"),
        "mnemonic": x.get("symbol_name"), "wuxing": x.get("wuxing"), "image": x.get("image"),
        "attribute": x.get("property"), "direction": x.get("direction"), "family": x.get("person"),
        "body": x.get("body"), "season": x.get("season"),
        "provenance": {"repo": "godcong/yi", "path": "data/bagua.json", "commit": god_commit, "license": "MIT"},
    } for x in bagua]
    if len(trigrams) != 8:
        raise RuntimeError(f"expected 8 trigrams, got {len(trigrams)}")
    write_json("data/canonical/yijing/trigrams.json", {"schema_version": "0.2", "items": trigrams})

    god_gua = load_json("data/upstream/godcong-yi/gua.json")
    tuan_xiang = [{
        "id": f"yijing.hexagram.{int(x['xu']):02d}", "king_wen_no": int(x["xu"]),
        "name": x.get("gua_name"), "full_name": x.get("ming"), "symbol": x.get("gua_symbol"),
        "upper": x.get("shang_ming"), "lower": x.get("xia_ming"),
        "tuan": x.get("tuan_text"), "da_xiang": x.get("xiang_text"),
        "provenance": {"repo": "godcong/yi", "path": "data/gua.json", "commit": god_commit, "license": "MIT"},
        "note": "Only classical Tuan/Xiang fields promoted; modern fortune interpretation fields intentionally excluded.",
    } for x in god_gua]
    if len(tuan_xiang) != 64:
        raise RuntimeError(f"expected 64 godcong gua rows, got {len(tuan_xiang)}")
    write_json("data/canonical/yijing/tuan-xiang.json", {"schema_version": "0.2", "items": tuan_xiang})

    wenyan_entries = load_json("data/upstream/godcong-yi/wenyan.json")
    wenyan = {
        "schema_version": "0.2", "domain": "yijing", "layer": "L0", "work": "文言传",
        "entries": wenyan_entries,
        "provenance": {"repo": "godcong/yi", "path": "data/wenyan.json", "commit": god_commit, "license": "MIT"},
    }
    write_json("data/canonical/classics/yijing/wenyan.json", wenyan)

    rows: list[dict] = []
    for x in trigrams:
        rows.append({
            "id": x["id"], "domain": "yijing", "layer": "L1", "topic": "八卦", "title": x["name"],
            "text": f"{x['name']}{x['symbol']}；象={x['image']}；五行={x['wuxing']}；属性={x['attribute']}；后天方位={x['direction']}；先天数={x['xian_tian_num']}；后天数={x['hou_tian_num']}",
            "provenance": x["provenance"],
        })
    tuan_by_no = {x["king_wen_no"]: x for x in tuan_xiang}
    for x in items:
        rows.append({
            "id": f"{x['id']}.core", "domain": "yijing", "layer": "L0", "topic": "卦辞/大象",
            "title": f"{x['king_wen_no']}.{x['full_name']}",
            "text": f"卦辞：{x['judgment']}\n大象：{x['great_image']}", "provenance": x["provenance"],
        })
        tx = tuan_by_no.get(x["king_wen_no"])
        if tx and tx.get("tuan"):
            rows.append({
                "id": f"{x['id']}.tuan", "domain": "yijing", "layer": "L0", "topic": "彖传",
                "title": f"{x['king_wen_no']}.{x['full_name']} 彖传",
                "text": tx["tuan"], "provenance": tx["provenance"],
            })
        for i, line in enumerate(x["lines"], 1):
            rows.append({
                "id": f"{x['id']}.line.{i}", "domain": "yijing", "layer": "L0", "topic": "爻辞",
                "title": f"{x['king_wen_no']}.{x['full_name']} 第{i}爻",
                "hexagram_no": x["king_wen_no"], "line_no": i, "text": line, "provenance": x["provenance"],
            })
    for group in wenyan["entries"]:
        for i, entry in enumerate(group.get("entries", []), 1):
            rows.append({
                "id": f"yijing.wenyan.{group.get('index', 'unknown')}.{i:02d}",
                "domain": "yijing", "layer": "L0", "topic": "文言传",
                "title": entry.get("title"), "text": entry.get("text"), "provenance": wenyan["provenance"],
            })
    write_jsonl("data/index/yijing-core.jsonl", rows)

    fundgao_path = ROOT / "data/upstream/fundgao-zhouyi/README.md"
    crosscheck_count = 0
    if fundgao_path.exists():
        raw = fundgao_path.read_text(encoding="utf-8").replace("\r", "")
        parts = [p.strip() for p in re.split(r"(?=^# 第[^\n]{1,12}卦)", raw, flags=re.M)
                 if re.search(r"^# 第[^\n]{1,12}卦", p, flags=re.M)]
        if len(parts) != 64:
            raise RuntimeError(f"fundgao crosscheck expected 64 sections, got {len(parts)}")
        fundgao_commit = source_commit("fundgao-zhouyi")
        cross_rows = [{
            "id": f"yijing.fundgao.section.{i:02d}", "domain": "yijing", "layer": "L0",
            "topic": "卦章整段（含彖/象/小象）", "king_wen_no": i,
            "title": part.splitlines()[0].lstrip("#").strip(), "text": part,
            "source_repo": "fundgao/DAO_DE_JING", "source_path": "周易/README.md",
            "source_commit": fundgao_commit, "license": "MIT", "use": "cross_validation_and_small_image_retrieval",
        } for i, part in enumerate(parts, 1)]
        write_jsonl("data/index/yijing-crosscheck-sections.jsonl", cross_rows)
        crosscheck_count = len(cross_rows)

    return {"hexagrams": 64, "lines": 384, "trigrams": 8, "yijing_index_rows": len(rows), "crosscheck_sections": crosscheck_count}


def rebuild_yizhuan_supplement() -> dict:
    specs = [
        ("系辞", "data/canonical/classics/yijing/系辞.md", "md/系辞.md"),
        ("说卦", "data/canonical/classics/yijing/说卦.md", "md/说卦.md"),
        ("序卦", "data/canonical/classics/yijing/序卦.md", "md/序卦.md"),
        ("杂卦", "data/canonical/classics/yijing/杂卦.md", "md/杂卦.md"),
    ]
    commit = source_commit("open-iching-classics")
    works, rows = [], []
    for work, path, source_path in specs:
        raw = read_text(path).strip()
        body = re.sub(r"^#\\s+[^\\n]+\\n+", "", raw, count=1).strip()
        sections = []
        if work == "系辞":
            pieces = re.split(r"^##\\s+(上|下)\\s*$", body, flags=re.M)
            if len(pieces) >= 5:
                sections = [
                    {"part": "上", "text": pieces[2].strip()},
                    {"part": "下", "text": pieces[4].strip()},
                ]
        if not sections:
            sections = [{"part": None, "text": body}]

        works.append({
            "work": work,
            "source_repo": "john-walks-slow/open-iching",
            "source_path": source_path,
            "source_commit": commit,
            "license": "Public Domain classical text; transport repository has no LICENSE",
            "sections": sections,
        })

        n = 0
        for section in sections:
            for chunk in chunk_document(section["text"], max_chars=1000, assembled_max=1100):
                n += 1
                rows.append({
                    "id": f"yijing.yizhuan.{work}.{n:03d}",
                    "domain": "yijing", "layer": "L0", "topic": work,
                    "part": section["part"], "chunk_no": n, "text": chunk,
                    "source_repo": "john-walks-slow/open-iching",
                    "source_path": source_path, "source_commit": commit,
                    "license": "Public Domain classical text",
                    "provenance_note": "Ancient text only; repository code/content outside these public-domain files is not reused.",
                })

    write_json("data/canonical/classics/yijing/yizhuan-supplement.json", {
        "schema_version": "0.1",
        "works": works,
        "note": "Supplements the separately stored 彖传/象传/文言 data with 系辞、说卦、序卦、杂卦.",
    })
    write_jsonl("data/index/yijing-yizhuan.jsonl", rows)
    return {"yizhuan_works": len(works), "yizhuan_index_rows": len(rows)}


def rebuild_liuyao_classics() -> dict:
    specs = [
        ("data/canonical/classics/liuyao/卜筮正宗.txt", "liuyao.bushizhengzong", "卜筮正宗", "data/卜筮正宗_ctext公有领域全文.txt"),
        ("data/canonical/classics/liuyao/增删卜易.txt", "liuyao.zengshanbuyi", "增删卜易", "data/增删卜易_ctext公有领域全文.txt"),
    ]
    commit = source_commit("liuyao-engine")
    rows, catalog = [], []
    for path, doc_id, title, source_path in specs:
        raw = read_text(path).strip()
        chunks = chunk_document(raw)
        for i, chunk in enumerate(chunks, 1):
            rows.append({
                "id": f"{doc_id}.chunk.{i:04d}", "domain": "liuyao", "layer": "L0",
                "title": title, "chunk_no": i, "text": chunk,
                "source_repo": "yaomancy/liuyao-engine", "source_path": source_path,
                "source_commit": commit, "license": "Public Domain classical text",
                "provenance": "ctext.org via audited Apache-2.0 source repository",
            })
        catalog.append({
            "doc_id": doc_id, "title": title, "char_count": len(raw), "chunk_count": len(chunks),
            "min_chunk_chars": min(map(len, chunks)), "max_chunk_chars": max(map(len, chunks)),
            "source_repo": "yaomancy/liuyao-engine", "source_path": source_path, "source_commit": commit,
        })
    write_jsonl("data/index/liuyao-classics.jsonl", rows)
    write_json("data/canonical/classics/liuyao/catalog.json", {
        "schema_version": "0.3", "chunking": {"target_chars": 1100, "max_assembled_chars": 1200}, "documents": catalog,
    })
    return {"classic_chunks": len(rows), "documents": len(catalog)}


def rebuild_bazi() -> dict:
    files = [
        ("classical-texts.md", "bazi.classical_summaries", "L2"),
        ("dayun-rules.md", "bazi.dayun", "L1"), ("shensha-table.md", "bazi.shensha", "L1"),
        ("shichen-table.md", "bazi.shichen", "L1"), ("wuxing-tables.md", "bazi.wuxing_tables", "L1"),
    ]
    commit = source_commit("bazi-skill")
    rows = []
    for filename, doc_id, layer in files:
        for i, chunk in enumerate(split_markdown(read_text(f"data/upstream/bazi-skill/{filename}")), 1):
            rows.append({
                "id": f"{doc_id}.chunk.{i:03d}", "domain": "bazi", "layer": layer,
                "topic": chunk["title"] or doc_id, "chunk_no": i, "text": chunk["text"],
                "source_repo": "jinchenma94/bazi-skill", "source_path": f"references/{filename}",
                "source_commit": commit, "license": "MIT",
                "note": "Modern structured summary of classics; not a verbatim classical edition."
                        if doc_id == "bazi.classical_summaries" else "Structured rule/table source.",
            })
    write_jsonl("data/index/bazi-rules.jsonl", rows)
    return {"bazi_rows": len(rows)}


def normalize_json_entries(obj) -> list:
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return [{"key": k, "value": v} for k, v in obj.items()]
    return [{"value": obj}]


def rebuild_rule_indexes() -> dict:
    liu_rows = []
    engine_commit = source_commit("liuyao-engine")
    for name, path in [
        ("najia_tables", "data/upstream/liuyao-engine/yigram-najia-tables.json"),
        ("glossary", "data/upstream/liuyao-engine/liuyao-glossary.json"),
    ]:
        for i, value in enumerate(normalize_json_entries(load_json(path)), 1):
            liu_rows.append({
                "id": f"liuyao.{name}.{i:03d}", "domain": "liuyao", "layer": "L1", "topic": name,
                "text": json.dumps(value, ensure_ascii=False, indent=2),
                "source_repo": "yaomancy/liuyao-engine", "source_commit": engine_commit, "license": "Apache-2.0",
            })
    steward_commit = source_commit("metaphysics-steward")
    for key, filename in [("najia_rules", "liuyao_najia.md"), ("lost_items", "liuyao_lost_items.md")]:
        for i, chunk in enumerate(split_markdown(read_text(f"data/upstream/metaphysics-steward/{filename}")), 1):
            liu_rows.append({
                "id": f"liuyao.{key}.{i:03d}", "domain": "liuyao", "layer": "L1",
                "topic": chunk["title"] or key, "text": chunk["text"],
                "source_repo": "superzhang21/metaphysics-steward", "source_path": f"references/{filename}",
                "source_commit": steward_commit, "license": "MIT",
            })
    write_jsonl("data/index/liuyao-rules.jsonl", liu_rows)

    mei_rows = [{
        "id": f"meihua.rules.{i:03d}", "domain": "meihua", "layer": "L1",
        "topic": chunk["title"] or "梅花易数", "text": chunk["text"],
        "source_repo": "superzhang21/metaphysics-steward", "source_path": "references/meihua_notes.md",
        "source_commit": steward_commit, "license": "MIT",
    } for i, chunk in enumerate(split_markdown(read_text("data/upstream/metaphysics-steward/meihua_notes.md")), 1)]
    write_jsonl("data/index/meihua-rules.jsonl", mei_rows)

    hehun_rows = [{
        "id": f"yinyuan.hehun.{i:03d}", "domain": "yinyuan", "layer": "L1",
        "topic": chunk["title"] or "合婚", "text": chunk["text"],
        "source_repo": "superzhang21/metaphysics-steward", "source_path": "references/hehun_rules.md",
        "source_commit": steward_commit, "license": "MIT",
    } for i, chunk in enumerate(split_markdown(read_text("data/upstream/metaphysics-steward/hehun_rules.md")), 1)]
    write_jsonl("data/index/yinyuan-rules.jsonl", hehun_rows)
    return {"liuyao_rule_rows": len(liu_rows), "meihua_rule_rows": len(mei_rows), "yinyuan_rule_rows": len(hehun_rows)}


def main() -> None:
    stats = {}
    stats.update(rebuild_yijing())
    stats.update(rebuild_yizhuan_supplement())
    stats.update(rebuild_liuyao_classics())
    stats.update(rebuild_bazi())
    stats.update(rebuild_rule_indexes())
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
