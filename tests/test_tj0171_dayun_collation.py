"""TJ-017.1 七项优先校勘清单收尾批公开结构测试（审源编号 018-B）。

本模块（``bazi_dayun_collation``）是纯数据登记、零计算逻辑；本测试
只钉登记形制与校勘红线（校勘记字段完备、等级口径、confirmed 依据
门槛、逐项销项三态齐备、#6 限制维持、见证可得性核查在案、两
Source 的 review_scope 追加段落与来源普查不变），不验证任何大运
计算（不在本批范围，TJ-017.1 既有测试覆盖）。引文与校勘记对快照
的逐字复核在密封专项 ``tests/test_tj0171_dayun_collation_sealed.py``
（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_dayun_collation as dc

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0171_dayun_collation.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
FINAL_STATUSES = {"closed", "formalized", "restriction_maintained"}


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [name for name, obj in inspect.getmembers(dc)
                 if inspect.isfunction(obj)]
        self.assertEqual(funcs, [])

    def test_module_matches_golden(self) -> None:
        self.assertEqual(dc.COLLATION_REGISTER_ID, GOLDEN["register_id"])
        self.assertEqual(
            json.loads(json.dumps(dc.COLLATION_SECTIONS,
                                  ensure_ascii=False)),
            GOLDEN["sections"])
        self.assertEqual(
            json.loads(json.dumps(dc.COLLATION_QUOTES,
                                  ensure_ascii=False)),
            GOLDEN["quotes"])
        self.assertEqual(
            json.loads(json.dumps(dc.COLLATION_NOTES,
                                  ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(dc.ITEM_DISPOSITIONS,
                                  ensure_ascii=False)),
            GOLDEN["item_dispositions"])
        self.assertEqual(
            json.loads(json.dumps(dc.WITNESS_AVAILABILITY_SHENFENG,
                                  ensure_ascii=False)),
            GOLDEN["witness_availability_shenfeng"])

    def test_sections_registered(self) -> None:
        secs = {s["section_id"]: s for s in dc.COLLATION_SECTIONS}
        self.assertEqual(set(secs), {
            "sanming.juan2.lun_dayun", "sanming.juan11.luoluozi_fu",
            "shenfeng.qi_dayun_fa"})
        self.assertEqual(secs["sanming.juan2.lun_dayun"]["locator"],
                         {"char_start": 58457, "char_end": 59198})
        self.assertEqual(secs["shenfeng.qi_dayun_fa"]["locator"],
                         {"char_start": 85001, "char_end": 85246})


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(dc.COLLATION_NOTES), 13)
        ids = [n["id"] for n in dc.COLLATION_NOTES]
        self.assertEqual(len(ids), len(set(ids)))
        for note in dc.COLLATION_NOTES:
            self.assertTrue(self.REQUIRED <= set(note), note["id"])
            self.assertIn(note["reading_status"], STATUSES, note["id"])
            self.assertIn(note["disposition"], DISPOSITIONS, note["id"])
            self.assertIn(note["usable_grade"], GRADES, note["id"])
            self.assertTrue(note["basis"], note["id"])
            for basis in note["basis"]:
                self.assertIn(basis["kind"], BASIS_KINDS, note["id"])
                self.assertTrue(basis["witness"], note["id"])
                self.assertTrue(basis["quote_short"], note["id"])

    def test_confirmed_notes_have_two_independent_basis(self) -> None:
        for note in dc.COLLATION_NOTES:
            if note["reading_status"] == "confirmed":
                self.assertGreaterEqual(len(note["basis"]), 2,
                                        note["id"])
                kinds = {b["kind"] for b in note["basis"]}
                self.assertTrue(
                    "witness" in kinds or "sealed_asset" in kinds,
                    note["id"])

    def test_genuine_notes_keep_snapshot_glyph(self) -> None:
        genuine = [n for n in dc.COLLATION_NOTES
                   if n["disposition"] == "genuine"]
        self.assertEqual({n["id"] for n in genuine},
                         {"dy-genuine-58888", "dy-genuine-58834",
                          "dy-genuine-408791"})
        for note in genuine:
            self.assertEqual(note["reading"], note["snapshot_glyph"],
                             note["id"])

    def test_item6_proposals_not_adopted(self) -> None:
        props = {n["id"]: n for n in dc.COLLATION_NOTES
                 if n["id"].startswith("sf-prop-")}
        self.assertEqual(set(props), {"sf-prop-85107", "sf-prop-85108",
                                      "sf-prop-85086"})
        for note in props.values():
            # 字面禁用维持：无可用等级，状态不得为 confirmed
            self.assertIsNone(note["usable_grade"], note["id"])
            self.assertNotEqual(note["reading_status"], "confirmed",
                                note["id"])
            self.assertIn("禁用维持", note["note"], note["id"])


class ItemDispositionTest(unittest.TestCase):
    def test_seven_items_with_three_final_states(self) -> None:
        items = {d["item"]: d for d in dc.ITEM_DISPOSITIONS}
        self.assertEqual(set(items), {1, 2, 3, 4, 5, 6, 7})
        for d in items.values():
            self.assertIn(d["final_status"], FINAL_STATUSES, d["item"])
        self.assertEqual(
            {i for i, d in items.items() if d["final_status"] == "closed"},
            {1, 2, 3, 5})
        self.assertEqual(
            {i for i, d in items.items()
             if d["final_status"] == "formalized"}, {4, 7})
        self.assertEqual(items[6]["final_status"],
                         "restriction_maintained")
        self.assertIn("禁用维持", items[6]["restriction_after"])

    def test_shenfeng_witness_availability_recorded(self) -> None:
        avail = dc.WITNESS_AVAILABILITY_SHENFENG
        self.assertFalse(avail["kanripo"]["available"])
        self.assertEqual(len(avail["web_transcriptions"]), 3)
        self.assertIn("同一数字谱系", avail["lineage_assessment"])
        self.assertIn("维持限制", avail["conclusion"])


class QuoteFormTest(unittest.TestCase):
    def test_transform_quotes_have_mapped_reading(self) -> None:
        for quote in dc.COLLATION_QUOTES:
            if quote.get("collation_refs"):
                self.assertIn("mapped_reading", quote, quote["id"])
            if quote.get("note_refs"):
                # 传本同文/提案类引文不得带校定读法
                self.assertNotIn("mapped_reading", quote, quote["id"])

    def test_note_refs_resolve(self) -> None:
        note_ids = {n["id"] for n in dc.COLLATION_NOTES}
        for quote in dc.COLLATION_QUOTES:
            for ref in quote.get("collation_refs", []) + \
                    quote.get("note_refs", []):
                self.assertIn(ref, note_ids, quote["id"])


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
        for needle in ("dayun-collation-register-v1", "KR3g0042",
                       "传本本文", "正式流程复核"):
            self.assertIn(needle, sanming, needle)
        shenfeng = by_id["bazi.source.shenfeng"]["review_scope"]
        for needle in ("dayun-collation-register-v1", "同一数字谱系",
                       "字面禁用维持", "三五十五"):
            self.assertIn(needle, shenfeng, needle)


if __name__ == "__main__":
    unittest.main()
