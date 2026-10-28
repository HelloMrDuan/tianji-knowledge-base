"""TJ-018-H 密封快照专项：三命 66 条零匹配订正归因登记册。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：对机上
密封资产逐项复核归因证据——(1) 由快照原文重算 603 条订正的
出现次数，66 条零匹配集合与登记册逐条一致；(2) 每条登记的
位点窗口与 old 串逐字 diff == 登记 diffs（含长锚摘要以密封
JSON 原文核对 SHA256/首尾）；(3) 以仓库脚本语义复放 PUA 阶段
（逐位溯源），41 条 missing_glyph_context 的 old 串在 PUA 后
文本恰 1 次且每处差异的码位/读法与登记一致，25 条
chain_dependency 在 PUA 后文本为 0 次；(4) 按
``apply_sanming_text_collation.py`` 全规则文件序复放文本阶段，
603 条全量可应用，链式条目的每个登记材料依赖经全量消融证明
必要（去掉该依赖则该条于自身轮次不可应用）；(5) 既有校勘记
三册（卷二 160 条、卷五 151 条、卷六 72 条）逐字不动、来源
普查（101 条，C 95 / D 6）与 review_scope 新增段落钉值。
本专项只复核归因，不应用任何订正。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cjf
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as cjg
from tianji_kb import bazi_sanming_zero_match_attribution as zm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
TEXT_SPEC = json.loads(
    (SNAPSHOT_DIR / "sanming_text_collation.json").read_text(
        encoding="utf-8"))
PUA_SPEC = json.loads(
    (SNAPSHOT_DIR / "sanming_pua_collation.json").read_text(
        encoding="utf-8"))
ROWS = TEXT_SPEC["corrections"]
ROW_BY_ID = {r["id"]: r for r in ROWS}
ENTRIES = {e["correction_id"]: e for e in zm.ZERO_MATCH_ENTRIES}


def _text() -> str:
    return (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes().decode("utf-8")


def _is_pua(ch: str) -> bool:
    cp = ord(ch)
    return (0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD
            or 0x100000 <= cp <= 0x10FFFD)


def _apply_pua(text: str):
    """Mirror scripts/apply_pua_collation.py semantics; return
    (pua_text, provenance) with provenance[i] = None or
    ('uniform', codepoint) / ('contextual', codepoint, rule_index)."""
    prov: list = [None] * len(text)
    chars = list(text)
    for row in PUA_SPEC.get("mappings", []):
        if row.get("status") != "confirmed":
            continue
        glyph, rep = row["glyph"], row["replacement"]
        assert text.count(glyph) == int(row["count"]), row["codepoint"]
        for i, ch in enumerate(chars):
            if ch == glyph:
                chars[i] = rep
                prov[i] = ("uniform", row["codepoint"])
    for row in PUA_SPEC.get("contextual_mappings", []):
        if row.get("status") != "confirmed":
            continue
        for ri, rule in enumerate(row.get("replacements", [])):
            old, new = rule["old"], rule["new"]
            cur = "".join(chars)
            assert cur.count(old) == 1, (row["codepoint"], ri)
            i = cur.find(old)
            for k in range(len(old)):
                if old[k] != new[k]:
                    chars[i + k] = new[k]
                    prov[i + k] = ("contextual", row["codepoint"], ri)
    return "".join(chars), prov


def _applicable(text: str, row: dict) -> bool:
    if text.count(row["old"]) != 1:
        return False
    if text.count(row["new"]) and not row.get("allow_existing_target", False):
        return False
    return True


def _replay(pua_text: str, skip=frozenset(), stop_at: str | None = None):
    """File-order application under the script's rules.
    Returns (applied_ids, applicable_at_turn) where the latter maps
    stop_at's id to its applicability when reached."""
    text = pua_text
    applied: set[str] = set()
    at_turn: dict[str, bool] = {}
    for row in ROWS:
        rid = row["id"]
        if rid == stop_at:
            at_turn[rid] = _applicable(text, row)
            break
        if rid in skip:
            continue
        if _applicable(text, row):
            text = text.replace(row["old"], row["new"], 1)
            applied.add(rid)
    return applied, at_turn


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        meta = zm.ATTRIBUTION_SNAPSHOTS["sanming_tonghui.txt"]
        raw = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])


class ZeroMatchRecomputeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _text()

    def test_zero_set_recomputed_equals_register(self) -> None:
        self.assertEqual(len(ROWS), 603)
        counts = {r["id"]: self.text.count(r["old"]) for r in ROWS}
        zero = {rid for rid, c in counts.items() if c == 0}
        once = {rid for rid, c in counts.items() if c == 1}
        self.assertEqual(zero, set(ENTRIES))
        self.assertEqual(len(zero), 66)
        self.assertEqual(len(once), 537)
        base = zm.PIPELINE_BASELINE["text_collation"]
        self.assertEqual(base["zero_match_in_snapshot"], len(zero))
        self.assertEqual(base["exact_once_in_snapshot"], len(once))

    def test_register_matches_sealed_entries(self) -> None:
        for cid, e in ENTRIES.items():
            row = ROW_BY_ID[cid]
            self.assertEqual(e["sealed_status"], row["status"])
            for key in ("old", "new"):
                sealed = row[key]
                digest = e[key + "_digest"]
                self.assertEqual(digest["length"], len(sealed), cid)
                self.assertEqual(
                    digest["sha256"],
                    hashlib.sha256(sealed.encode("utf-8")).hexdigest(), cid)
                self.assertEqual(digest["head"], sealed[:24], cid)
                self.assertEqual(digest["tail"], sealed[-24:], cid)
                if e[key] is not None:
                    self.assertEqual(e[key], sealed, cid)

    def test_sites_and_diffs_pin_to_snapshot(self) -> None:
        for cid, e in ENTRIES.items():
            old = ROW_BY_ID[cid]["old"]
            s, en = e["site"]["char_start"], e["site"]["char_end"]
            window = self.text[s:en]
            self.assertEqual(len(window), len(old), cid)
            expected = [{"offset": i, "snapshot_char": window[i],
                         "old_char": old[i]}
                        for i in range(len(old)) if window[i] != old[i]]
            actual = [{"offset": d["offset"],
                       "snapshot_char": d["snapshot_char"],
                       "old_char": d["old_char"]} for d in e["diffs"]]
            self.assertEqual(actual, expected, cid)
            for d in e["diffs"]:
                if _is_pua(d["snapshot_char"]):
                    self.assertEqual(
                        d["snapshot_codepoint"],
                        "U+%04X" % ord(d["snapshot_char"]), cid)
                else:
                    self.assertIsNone(d["snapshot_codepoint"], cid)


class PuaStageAttributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _text()
        cls.pua_text, cls.prov = _apply_pua(cls.text)

    def test_pua_stage_fully_resolves(self) -> None:
        remaining = sum(1 for ch in self.pua_text if _is_pua(ch))
        self.assertEqual(remaining, 0)
        base = zm.PIPELINE_BASELINE["pua_stage"]
        self.assertEqual(base["occurrences_applied"], 524)
        self.assertEqual(base["remaining_after"], remaining)

    def test_categories_match_mechanical_split(self) -> None:
        for cid, e in ENTRIES.items():
            cnt = self.pua_text.count(ROW_BY_ID[cid]["old"])
            if e["category"] == "missing_glyph_context":
                self.assertEqual(cnt, 1, cid)
            elif e["category"] == "chain_dependency":
                self.assertEqual(cnt, 0, cid)
            else:  # pragma: no cover - register has no other categories
                self.fail(cid)

    def test_pua_entries_pin_to_provenance(self) -> None:
        for cid, e in ENTRIES.items():
            if e["category"] != "missing_glyph_context":
                continue
            old = ROW_BY_ID[cid]["old"]
            s = e["site"]["char_start"]
            self.assertEqual(self.pua_text[s:s + len(old)], old, cid)
            for d in e["diffs"]:
                tag = self.prov[s + d["offset"]]
                self.assertIsNotNone(tag, cid)
                if tag[0] == "uniform":
                    self.assertEqual(d["explained_by"],
                                     "pua_mapping:%s" % tag[1], cid)
                else:
                    self.assertEqual(
                        d["explained_by"],
                        "pua_contextual:%s#%d" % (tag[1], tag[2]), cid)
                self.assertEqual(self.pua_text[s + d["offset"]],
                                 d["old_char"], cid)


class ChainReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pua_text, _ = _apply_pua(_text())

    def test_full_replay_applies_all_603(self) -> None:
        applied, _ = _replay(self.pua_text)
        self.assertEqual(len(applied), 603)
        self.assertEqual(applied, {r["id"] for r in ROWS})
        base = zm.PIPELINE_BASELINE
        self.assertEqual(base["staged_replay"]["applied"], len(applied))
        # 全量应用后文本长度与残余防字数（工作本口径，非 canonical）
        text = self.pua_text
        for row in ROWS:
            text = text.replace(row["old"], row["new"], 1)
        self.assertEqual(len(text), base["staged_replay"]["final_text_chars"])
        self.assertEqual(text.count("防"),
                         base["fang"]["remaining_after_full_application"])
        self.assertEqual(sum(1 for ch in text if _is_pua(ch)), 0)

    def test_chain_dependencies_are_necessary(self) -> None:
        for cid, e in ENTRIES.items():
            if e["category"] != "chain_dependency":
                continue
            _, at_turn = _replay(self.pua_text, stop_at=cid)
            self.assertTrue(at_turn[cid], cid)
            for dep in e["dependencies"]["corrections"]:
                _, at_turn = _replay(self.pua_text, skip={dep},
                                     stop_at=cid)
                self.assertFalse(at_turn[cid], (cid, dep))


class RegistrationCensusTest(unittest.TestCase):
    def test_source_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        grades: dict[str, int] = {}
        for source in SOURCES:
            grade = source["evidence_level"]
            grades[grade] = grades.get(grade, 0) + 1
        self.assertEqual(grades, {"C": 95, "D": 6})

    def test_review_scope_additions_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("TJ-018-H", "sanming-zero-match-attribution-register-v1",
                       "66 条零匹配", "missing_glyph_context 41",
                       "chain_dependency 25", "残余防 769"):
            self.assertIn(needle, sanming, needle)

    def test_previous_registers_still_pinned(self) -> None:
        for mod, expected in ((cja, 44), (cjb, 35), (cjc, 81), (cjd, 43),
                              (cjf, 108), (cjg, 72)):
            self.assertEqual(len(mod.COLLATION_NOTES), expected)


if __name__ == "__main__":
    unittest.main()
