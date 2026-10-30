"""TJ-018-B 公开结构测试：三命卷二《论三刑》校勘记续册与扩登记。

本模块（``bazi_sanming_juan2_sanxing_collation``）是 TJ-018-A 首建
校勘记注册表的同表续册、纯数据登记、零计算逻辑；本测试只钉登记
形制与校勘红线（字段完备、等级口径、confirmed 依据门槛、未决项
reading=None、suspected 只此一处、名目异文 conflict 并列不裁定、
概念衔接与裁定代码现状一致、018-A 注册表 44 条逐字不动），不验证
任何三刑判定（不存在此种代码路径）。引文与校勘记对快照的逐字
复核在密封专项 ``tests/test_tj018b_sanming_sanxing_sealed.py``
（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018b_sanming_sanxing.json").read_text(
        encoding="utf-8"))
GOLDEN_A = json.loads(
    (ROOT / "tests" / "golden_tj018a_sanming_juan2.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
SECTION = (71874, 74856)


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [name for name, obj in inspect.getmembers(cj)
                 if inspect.isfunction(obj)]
        self.assertEqual(funcs, [])

    def test_same_register_as_018a(self) -> None:
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         cja.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         "sanming-juan2-collation-register-v1")
        self.assertEqual(cj.COLLATION_TASK, "TJ-018-B")

    def test_module_matches_golden(self) -> None:
        for attr, key in (("COLLATION_SECTIONS", "sections"),
                          ("COLLATION_QUOTES", "quotes"),
                          ("COLLATION_NOTES", "collation_notes"),
                          ("SANXING_NAMING_VARIANTS", "naming_variants"),
                          ("THREE_PUNISHMENTS_CONCEPT_LINKAGE",
                           "concept_linkage"),
                          ("SEALED_ASSET_RECONCILIATION",
                           "sealed_asset_reconciliation")):
            self.assertEqual(
                json.loads(json.dumps(getattr(cj, attr),
                                      ensure_ascii=False)),
                GOLDEN[key], attr)
        self.assertEqual(GOLDEN["register_id"], cj.COLLATION_REGISTER_ID)

    def test_section_registered(self) -> None:
        self.assertEqual(len(cj.COLLATION_SECTIONS), 1)
        sec = cj.COLLATION_SECTIONS[0]
        self.assertEqual(sec["section_id"], "sanming.juan2.sanxing")
        self.assertEqual(sec["locator"],
                         {"char_start": 71874, "char_end": 74856})
        self.assertEqual((sec["pua_count"], sec["fang_count"]), (8, 5))
        parts = {p["part_id"]: p for p in sec["parts"]}
        self.assertEqual(parts["sanxing_exposition"]["locator"],
                         {"char_start": 71874, "char_end": 74035})
        self.assertEqual(parts["chongji_subsection"]["locator"],
                         {"char_start": 74035, "char_end": 74856})


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 35)
        ids = [n["id"] for n in cj.COLLATION_NOTES]
        self.assertEqual(len(ids), len(set(ids)))
        for note in cj.COLLATION_NOTES:
            self.assertTrue(self.REQUIRED <= set(note), note["id"])
            self.assertEqual(note["section_id"],
                             "sanming.juan2.sanxing", note["id"])
            self.assertTrue(SECTION[0] <= note["char_offset"] < SECTION[1],
                            note["id"])
            self.assertIn(note["reading_status"], STATUSES, note["id"])
            self.assertIn(note["disposition"], DISPOSITIONS, note["id"])
            self.assertIn(note["usable_grade"], GRADES, note["id"])
            self.assertTrue(note["basis"], note["id"])
            for basis in note["basis"]:
                self.assertIn(basis["kind"], BASIS_KINDS, note["id"])
                self.assertTrue(basis["witness"], note["id"])
                self.assertTrue(basis["quote_short"], note["id"])
            self.assertIn(note["snapshot_glyph"], note["context_short"],
                          note["id"])
            centre = note["context_short"][14]
            self.assertEqual(centre, note["snapshot_glyph"], note["id"])

    def test_confirmed_requires_two_anchors(self) -> None:
        for note in cj.COLLATION_NOTES:
            if note["reading_status"] == "confirmed":
                strong = [b for b in note["basis"]
                          if b["kind"] in ("witness",
                                           "same_section_corroboration")]
                self.assertGreaterEqual(len(strong), 2, note["id"])
                self.assertIsNotNone(note["reading"], note["id"])

    def test_unresolved_and_suspected_sets(self) -> None:
        unresolved = [n for n in cj.COLLATION_NOTES
                      if n["reading_status"] == "unresolved"]
        self.assertEqual([n["id"] for n in unresolved],
                         ["smxing-anomaly-71984"])
        for note in unresolved:
            self.assertIsNone(note["reading"], note["id"])
            self.assertEqual(note["disposition"], "unresolved", note["id"])
            self.assertIsNone(note["usable_grade"], note["id"])
        suspected = [n for n in cj.COLLATION_NOTES
                     if n["reading_status"] == "suspected"]
        self.assertEqual([n["id"] for n in suspected],
                         ["smxing-zuo-72374"])
        self.assertEqual(suspected[0]["reading"], "故")

    def test_readings_have_no_pua(self) -> None:
        for note in cj.COLLATION_NOTES:
            if note["reading"] is not None:
                self.assertFalse(any(_is_pua(c) for c in note["reading"]),
                                 note["id"])

    def test_counts_by_class(self) -> None:
        notes = cj.COLLATION_NOTES
        by_prefix: dict[str, list] = {}
        for n in notes:
            by_prefix.setdefault(n["id"].split("-")[1], []).append(n)
        self.assertEqual(len(by_prefix["pua"]), 8)
        self.assertTrue(all(n["reading_status"] == "confirmed"
                            for n in by_prefix["pua"]))
        pua_readings = [n["reading"] for n in by_prefix["pua"]]
        self.assertEqual(pua_readings.count("带"), 6)
        self.assertEqual(pua_readings.count("惨"), 1)
        self.assertEqual(pua_readings.count("玄"), 1)
        self.assertEqual(len(by_prefix["fang"]), 5)
        fang_readings = [n["reading"] for n in by_prefix["fang"]]
        self.assertEqual(sorted(fang_readings),
                         sorted(["㓙", "㓙", "䘮", "䘮", "㸔"]))
        # 防的多源汇定性：5 处定字分属 3 个互不相干的原字，无全局替换
        self.assertEqual(len(set(fang_readings)), 3)
        self.assertEqual(len(by_prefix["shu"]), 8)
        self.assertTrue(all(n["reading"] == "戌"
                            and n["reading_status"] == "confirmed"
                            for n in by_prefix["shu"]))
        self.assertEqual(len(by_prefix["ji"]), 9)
        ji_corrected = [n for n in by_prefix["ji"]
                        if n["disposition"] == "corrected"]
        self.assertEqual({n["id"] for n in ji_corrected},
                         {"smxing-ji-74019", "smxing-ji-74674"})
        self.assertTrue(all(n["reading"] == "巳" for n in ji_corrected))
        self.assertEqual(len(by_prefix["yi"]), 2)
        self.assertTrue(all(n["disposition"] == "genuine"
                            for n in by_prefix["yi"]))
        by_status = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 23, "contextual": 10,
                                     "suspected": 1, "unresolved": 1})


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_section(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 11)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            self.assertEqual(
                len(quote["quote"]), loc["char_end"] - loc["char_start"],
                quote["id"])
            self.assertTrue(SECTION[0] <= loc["char_start"]
                            and loc["char_end"] <= SECTION[1], quote["id"])

    def test_mapped_quotes_reference_notes(self) -> None:
        notes = {n["id"]: n for n in cj.COLLATION_NOTES}
        for quote in cj.COLLATION_QUOTES:
            refs = quote.get("collation_refs")
            if not refs:
                self.assertNotIn("mapped_reading", quote, quote["id"])
                continue
            self.assertIn("mapped_reading", quote, quote["id"])
            self.assertNotEqual(quote["mapped_reading"], quote["quote"],
                                quote["id"])
            for ref in refs:
                self.assertIn(ref, notes, ref)
                self.assertIsNotNone(notes[ref]["reading"], ref)

    def test_no_quote_contains_unresolved_or_suspected_glyphs(self) -> None:
        for quote in cj.COLLATION_QUOTES:
            self.assertNotIn("卯寅子", quote["quote"], quote["id"])
            self.assertNotIn("做曰", quote["quote"], quote["id"])
            self.assertNotIn("□", quote["quote"], quote["id"])

    def test_enumeration_quotes_present(self) -> None:
        by_id = {q["id"]: q for q in cj.COLLATION_QUOTES}
        for qid in ("sm3.enum_opening", "sm3.enum_group4_partial",
                    "sm3.summary_groups", "sm3.counting_method",
                    "sm3.wuen_core", "sm3.zixing_definition",
                    "sm3.sanche_variant", "sm3.houyue_bracket",
                    "sm3.chong_definition", "sm3.polu_poma"):
            self.assertIn(qid, by_id)
        self.assertIn("巳", by_id["sm3.houyue_bracket"]["mapped_reading"])
        self.assertIn("马在巳",
                      by_id["sm3.polu_poma"]["mapped_reading"])


class VariantsAndLinkageTest(unittest.TestCase):
    def test_naming_variants_conflict_unadjudicated(self) -> None:
        variants = cj.SANXING_NAMING_VARIANTS
        self.assertEqual(variants["status"], "conflict")
        self.assertIsNone(variants["adjudication"])
        main = variants["main_exposition"]
        self.assertEqual(main["无恩"], "寅巳申")
        self.assertEqual(main["恃势"], "丑戌未")
        branches = {b["branch_id"]: b for b in variants["alternatives"]}
        sanche = branches["sanche-yilan"]["claim"]
        # 三车一览与正文恰好反置两名
        self.assertEqual(sanche["恃势"], main["无恩"])
        self.assertEqual(sanche["无恩"], main["恃势"])
        quote_ids = {q["id"] for q in cj.COLLATION_QUOTES}
        for branch in variants["alternatives"]:
            for ref in branch["evidence_quotes"]:
                self.assertIn(ref, quote_ids)
        for ref in main["evidence_quotes"]:
            self.assertIn(ref, quote_ids)

    def test_concept_linkage_matches_code(self) -> None:
        linkage = cj.THREE_PUNISHMENTS_CONCEPT_LINKAGE
        self.assertEqual(linkage["concept_id"],
                         "bazi.concept.conflict_three_punishments")
        self.assertFalse(linkage["adjudication_semantics_changed"])
        existing = linkage["existing_adjudication"]
        self.assertEqual(existing["status"], "unresolved")
        self.assertFalse(existing["blocking"])
        self.assertEqual(existing["reason"],
                         "not_applied_in_explicit_ren_school")
        # 衔接登记必须与裁定代码的现状逐字一致（防漂移）
        code = (ROOT / "src" / "tianji_kb" / "bazi_adjudication.py") \
            .read_text(encoding="utf-8")
        self.assertIn("bazi.concept.conflict_three_punishments", code)
        self.assertIn("not_applied_in_explicit_ren_school", code)
        roots = (ROOT / "src" / "tianji_kb" / "bazi_root_conditions.py") \
            .read_text(encoding="utf-8")
        self.assertIn("bazi.concept.conflict_three_punishments", roots)

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-029", "ocr-454", "ocr-103"])
        self.assertEqual(rec["ocr_candidates_in_window"], 11)
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class Register018ARegressionTest(unittest.TestCase):
    def test_018a_register_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(
            json.loads(json.dumps(cja.COLLATION_NOTES,
                                  ensure_ascii=False)),
            GOLDEN_A["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(cja.COLLATION_QUOTES,
                                  ensure_ascii=False)),
            GOLDEN_A["quotes"])
        ids_a = {n["id"] for n in cja.COLLATION_NOTES}
        ids_b = {n["id"] for n in cj.COLLATION_NOTES}
        self.assertFalse(ids_a & ids_b)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论三刑", "71874", "74856", "TJ-018-B",
                       "conflict_three_punishments"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
