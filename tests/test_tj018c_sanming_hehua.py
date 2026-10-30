"""TJ-018-C 公开结构测试：三命卷二合化组三节校勘记续册与扩登记。

本模块（``bazi_sanming_juan2_hehua_collation``）是 TJ-018-A 首建
校勘记注册表的同表续册、纯数据登记、零计算逻辑；本测试只钉登记
形制与校勘红线（字段完备、等级口径、confirmed 依据门槛、巳字
干支槽位全量处置表、合化条件分歧 conflict 并列不裁定、逐月表
完整性数据、与既有五合事实层的衔接登记与代码现状一致、018-A
44 条与 018-B 35 条注册表逐字不动），不验证任何合化判定
（不存在此种代码路径）。引文与校勘记对快照的逐字复核在密封
专项 ``tests/test_tj018c_sanming_hehua_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cj
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018c_sanming_hehua.json").read_text(
        encoding="utf-8"))
GOLDEN_A = json.loads(
    (ROOT / "tests" / "golden_tj018a_sanming_juan2.json").read_text(
        encoding="utf-8"))
GOLDEN_B = json.loads(
    (ROOT / "tests" / "golden_tj018b_sanming_sanxing.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
SECTIONS = {"sanming.juan2.shiganhe": (64208, 65956),
            "sanming.juan2.shiganhuaqi": (65956, 67592),
            "sanming.juan2.zhuyuehengkan": (67592, 68359)}


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


def _dump(obj) -> object:
    return json.loads(json.dumps(obj, ensure_ascii=False))


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [name for name, obj in inspect.getmembers(cj)
                 if inspect.isfunction(obj)]
        self.assertEqual(funcs, [])

    def test_same_register_as_018a_018b(self) -> None:
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         cja.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         cjb.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         "sanming-juan2-collation-register-v1")
        self.assertEqual(cj.COLLATION_TASK, "TJ-018-C")

    def test_module_matches_golden(self) -> None:
        for attr, key in (("COLLATION_SECTIONS", "sections"),
                          ("COLLATION_QUOTES", "quotes"),
                          ("COLLATION_NOTES", "collation_notes"),
                          ("SI_GLYPH_DISPOSITION", "si_glyph_disposition"),
                          ("HEHUA_CONDITION_VARIANTS",
                           "condition_variants"),
                          ("HENGKAN_TABLE_INTEGRITY",
                           "hengkan_table_integrity"),
                          ("HEHUA_FACT_LINKAGE", "fact_linkage"),
                          ("SEALED_ASSET_RECONCILIATION",
                           "sealed_asset_reconciliation")):
            self.assertEqual(_dump(getattr(cj, attr)), GOLDEN[key], attr)
        self.assertEqual(GOLDEN["register_id"], cj.COLLATION_REGISTER_ID)

    def test_sections_registered(self) -> None:
        self.assertEqual(len(cj.COLLATION_SECTIONS), 3)
        for sec in cj.COLLATION_SECTIONS:
            self.assertEqual(sec["locator"],
                             {"char_start": SECTIONS[sec["section_id"]][0],
                              "char_end": SECTIONS[sec["section_id"]][1]},
                             sec["section_id"])
            self.assertEqual(len(sec["parts"]), 1)
            self.assertEqual(sec["school_attribution"], "三命通会体系")
        counts = {s["section_id"]: (s["pua_count"], s["fang_count"])
                  for s in cj.COLLATION_SECTIONS}
        self.assertEqual(counts, {"sanming.juan2.shiganhe": (5, 3),
                                  "sanming.juan2.shiganhuaqi": (1, 0),
                                  "sanming.juan2.zhuyuehengkan": (0, 0)})


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 81)
        ids = [n["id"] for n in cj.COLLATION_NOTES]
        self.assertEqual(len(ids), len(set(ids)))
        for note in cj.COLLATION_NOTES:
            self.assertTrue(self.REQUIRED <= set(note), note["id"])
            bounds = SECTIONS[note["section_id"]]
            self.assertTrue(bounds[0] <= note["char_offset"] < bounds[1],
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

    def test_no_unresolved_or_suspected_in_this_batch(self) -> None:
        # 本组文本最干净：81 条全数定读或真义落账，未决/suspected 为零
        # （拿不准者将按 unresolved 登记，此处钉住当前事实）。
        statuses = {n["reading_status"] for n in cj.COLLATION_NOTES}
        self.assertEqual(statuses, {"confirmed", "contextual"})
        for note in cj.COLLATION_NOTES:
            self.assertIsNotNone(note["reading"], note["id"])

    def test_readings_have_no_pua(self) -> None:
        for note in cj.COLLATION_NOTES:
            self.assertFalse(any(_is_pua(c) for c in note["reading"]),
                             note["id"])

    def test_counts_by_class(self) -> None:
        notes = cj.COLLATION_NOTES
        by_prefix: dict[str, list] = {}
        for n in notes:
            by_prefix.setdefault(n["id"].split("-")[1], []).append(n)
        self.assertEqual(len(by_prefix["pua"]), 6)
        pua_readings = sorted(n["reading"] for n in by_prefix["pua"])
        self.assertEqual(pua_readings, sorted(["瓜", "扬", "淫", "紧", "紧", "玄"]))
        self.assertEqual(len(by_prefix["fang"]), 3)
        self.assertTrue(all(n["reading"] == "㑹"
                            for n in by_prefix["fang"]))
        self.assertEqual(len(by_prefix["shu"]), 14)
        shu_readings = [n["reading"] for n in by_prefix["shu"]]
        self.assertEqual(shu_readings.count("戌"), 12)
        self.assertEqual(shu_readings.count("戊"), 2)
        self.assertEqual(len(by_prefix["xu"]), 1)
        self.assertEqual(by_prefix["xu"][0]["reading"], "戊")
        self.assertEqual(len(by_prefix["ji"]), 7)
        ji_corrected = [n for n in by_prefix["ji"]
                        if n["disposition"] == "corrected"]
        self.assertEqual(len(ji_corrected), 2)
        self.assertTrue(all(n["reading"] == "巳" for n in ji_corrected))
        ji_genuine = [n for n in by_prefix["ji"]
                      if n["disposition"] == "genuine"]
        self.assertEqual(len(ji_genuine), 5)
        self.assertEqual(len(by_prefix["yi"]), 7)
        yi_corrected = [n for n in by_prefix["yi"]
                        if n["disposition"] == "corrected"]
        self.assertEqual(len(yi_corrected), 5)
        self.assertTrue(all(n["reading"] == "己" for n in yi_corrected))
        self.assertEqual(len(by_prefix["si"]), 42)
        self.assertTrue(all(n["reading"] == "己"
                            and n["reading_status"] == "confirmed"
                            for n in by_prefix["si"]))
        self.assertEqual(len(by_prefix["jia"]), 1)
        self.assertEqual(by_prefix["jia"][0]["disposition"], "genuine")
        by_status = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 73, "contextual": 8})


class SiPartitionTest(unittest.TestCase):
    def test_si_partition_matches_notes(self) -> None:
        part = cj.SI_GLYPH_DISPOSITION
        stem = part["stem_slot_offsets"]
        branch = part["branch_slot_offsets"]
        self.assertEqual(len(stem), 42)
        self.assertEqual(len(branch), 40)
        self.assertFalse(set(stem) & set(branch))
        si_offsets = sorted(n["char_offset"] for n in cj.COLLATION_NOTES
                            if n["id"].split("-")[1] == "si")
        self.assertEqual(stem, si_offsets)


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_sections(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 34)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            self.assertEqual(
                len(quote["quote"]), loc["char_end"] - loc["char_start"],
                quote["id"])
            bounds = SECTIONS[quote["source_section_id"]]
            self.assertTrue(bounds[0] <= loc["char_start"]
                            and loc["char_end"] <= bounds[1], quote["id"])
            self.assertEqual(quote["school_attribution"], "三命通会体系")
            self.assertTrue(quote["text_layer"], quote["id"])

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


class VariantsIntegrityLinkageTest(unittest.TestCase):
    def test_condition_variants_conflict_unadjudicated(self) -> None:
        variants = cj.HEHUA_CONDITION_VARIANTS
        self.assertEqual(variants["status"], "conflict")
        self.assertIsNone(variants["adjudication"])
        branches = {b["branch_id"] for b in variants["branches"]}
        self.assertEqual(branches, {"prose-month-conditions",
                                    "general-wangqi-condition",
                                    "erzehua-and-duhua",
                                    "monthly-table-states"})
        quote_ids = {q["id"] for q in cj.COLLATION_QUOTES}
        for branch in variants["branches"]:
            for ref in branch["evidence_quotes"]:
                self.assertIn(ref, quote_ids)
            self.assertEqual(branch["school_attribution"], "三命通会体系")
        tokens = variants["unresolved_tokens"]
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0]["token"], "丙")
        self.assertEqual(tokens[0]["status"], "unresolved_parse")

    def test_divergence_pinned(self) -> None:
        div = cj.HEHUA_CONDITION_VARIANTS["branches"][3]["divergence"]
        self.assertEqual(div["甲巳"]["table_transform_months"],
                         [7, 9, 11, 12])
        self.assertEqual(div["甲巳"]["prose_required_but_table_not_transform"],
                         [3, 5, 6])
        self.assertEqual(div["甲巳"]["table_transform_but_prose_not_required"],
                         [7, 11])
        self.assertEqual(div["甲巳"]["table_other_element_months"], [10])
        self.assertEqual(div["乙庚"]["prose_required_but_table_not_transform"],
                         [4, 8])
        self.assertEqual(div["戊癸"]["table_transform_months"],
                         [1, 2, 3, 4, 9, 12])
        self.assertEqual(div["戊癸"]["prose_required_but_table_not_transform"],
                         [5])
        self.assertEqual(div["丁壬"]["table_other_element_months"], [4, 5, 9])

    def test_hengkan_integrity(self) -> None:
        integ = cj.HENGKAN_TABLE_INTEGRITY
        self.assertEqual(integ["cell_count"], 120)
        self.assertEqual(len(integ["rows"]), 10)
        for row, states in integ["grid"].items():
            self.assertEqual(len(states), 12, row)
        self.assertIsNone(integ["grid"]["辰戌丑未"][7])
        kinds = {a["kind"] for a in integ["anomalies"]}
        self.assertEqual(kinds, {"missing_state", "dittography",
                                 "state_vocabulary"})
        self.assertEqual([b["header_offset"] for b in integ["blocks"]],
                         [67603, 67792, 67981, 68169])

    def test_fact_linkage_matches_code(self) -> None:
        linkage = cj.HEHUA_FACT_LINKAGE
        self.assertEqual(linkage["fact_rule_id"],
                         "bazi.phase2.stem_five_combinations")
        self.assertFalse(linkage["adjudication_semantics_changed"])
        self.assertTrue(
            linkage["existing_fact_layer"]["pair_roster_matches_sections"])
        core = (ROOT / "src" / "tianji_kb" / "bazi_core.py") \
            .read_text(encoding="utf-8")
        self.assertIn("stem_five_combinations", core)
        self.assertIn("stem_combinations", core)
        cond = (ROOT / "src" / "tianji_kb" / "bazi_action_conditions.py") \
            .read_text(encoding="utf-8")
        self.assertIn("transformation_status", cond)
        self.assertIn("'unresolved'", cond)
        pat = (ROOT / "src" / "tianji_kb" / "bazi_pattern.py") \
            .read_text(encoding="utf-8")
        self.assertIn("actual_harmony_transformation", pat)

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-095", "ocr-096", "ocr-102"])
        self.assertEqual(rec["ocr_candidates_in_window"], 4)
        self.assertEqual(rec["pua_mapping_codepoints_in_window"],
                         ["U+E898", "U+EF6E", "U+EC93", "U+E645", "U+EA20"])
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class RegisterPreviousBatchesRegressionTest(unittest.TestCase):
    def test_018a_018b_registers_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(_dump(cja.COLLATION_NOTES),
                         GOLDEN_A["collation_notes"])
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(_dump(cjb.COLLATION_NOTES),
                         GOLDEN_B["collation_notes"])
        ids_a = {n["id"] for n in cja.COLLATION_NOTES}
        ids_b = {n["id"] for n in cjb.COLLATION_NOTES}
        ids_c = {n["id"] for n in cj.COLLATION_NOTES}
        self.assertFalse(ids_a & ids_b)
        self.assertFalse(ids_a & ids_c)
        self.assertFalse(ids_b & ids_c)
        # 注册表累计 44 + 35 + 81 = 160 条
        self.assertEqual(len(ids_a | ids_b | ids_c), 160)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论十干合", "论十干化气", "逐月横看理化之象",
                       "64208", "68359", "TJ-018-C",
                       "stem_five_combinations"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
