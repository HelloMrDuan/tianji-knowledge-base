"""TJ-018-D 公开结构测试：三命卷五去留组三节校勘记首册与扩登记。

本模块（``bazi_sanming_juan5_quliu_collation``）是逐条校勘记注册表
在卷五的首册（register ``sanming-juan5-collation-register-v1``），
与 TJ-018-A 首建的卷二注册表同一形制、同一字段与等级口径，纯
数据登记、零计算逻辑；本测试只钉登记形制与校勘红线（字段完备、
等级口径、confirmed 依据门槛、巳字干支槽位全量分判、与既有代码
unresolved 口径的衔接登记逐字一致、018-A/B/C 卷二注册表
44+35+81 条逐字不动、三命校勘记累计 203 条），不验证任何去留/
混杂/从煞判定（不存在此种代码路径）。引文与校勘记对快照的逐字
复核在密封专项 ``tests/test_tj018d_sanming_juan5_sealed.py``
（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cj

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018d_sanming_juan5.json").read_text(
        encoding="utf-8"))
GOLDEN_A = json.loads(
    (ROOT / "tests" / "golden_tj018a_sanming_juan2.json").read_text(
        encoding="utf-8"))
GOLDEN_B = json.loads(
    (ROOT / "tests" / "golden_tj018b_sanming_sanxing.json").read_text(
        encoding="utf-8"))
GOLDEN_C = json.loads(
    (ROOT / "tests" / "golden_tj018c_sanming_hehua.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
SECTIONS = {"sanming.juan5.congsa": (158219, 158504),
            "sanming.juan5.guansha-hunza": (158695, 158885),
            "sanming.juan5.guansha-quliu": (159245, 161329)}


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


def _dump(obj) -> object:
    return json.loads(json.dumps(obj, ensure_ascii=False))


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [name for name, obj in inspect.getmembers(cj)
                 if inspect.isfunction(obj)]
        self.assertEqual(funcs, [])

    def test_register_family_and_task(self) -> None:
        # 卷五首册：同形制、按卷分册；卷二注册表 id 三批一致且不动
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         "sanming-juan5-collation-register-v1")
        self.assertEqual(cja.COLLATION_REGISTER_ID,
                         "sanming-juan2-collation-register-v1")
        self.assertEqual(cjb.COLLATION_REGISTER_ID,
                         cja.COLLATION_REGISTER_ID)
        self.assertEqual(cjc.COLLATION_REGISTER_ID,
                         cja.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_TASK, "TJ-018-D")

    def test_module_matches_golden(self) -> None:
        for attr, key in (("COLLATION_SECTIONS", "sections"),
                          ("COLLATION_QUOTES", "quotes"),
                          ("COLLATION_NOTES", "collation_notes"),
                          ("SI_GLYPH_DISPOSITION", "si_glyph_disposition"),
                          ("QULIU_FACT_LINKAGE", "fact_linkage"),
                          ("TRANSMISSION_NOTES", "transmission_notes"),
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
            self.assertEqual(sec["volume"], "卷五")
            self.assertEqual(sec["school_attribution"], "三命通会体系")
        counts = {s["section_id"]: (s["pua_count"], s["fang_count"])
                  for s in cj.COLLATION_SECTIONS}
        self.assertEqual(counts,
                         {"sanming.juan5.congsa": (1, 5),
                          "sanming.juan5.guansha-hunza": (0, 2),
                          "sanming.juan5.guansha-quliu": (0, 16)})
        quliu = cj.COLLATION_SECTIONS[2]
        # 快照节题含讹字「防」逐字保留，校定题读「留」
        self.assertEqual(quliu["title_snapshot"], "官煞去防并官鬼互变杂论")
        self.assertEqual(quliu["title_normalized"],
                         "官煞去留并官鬼互变杂论")


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 43)
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
        # 本批 43 条全数定读或真义/异文落账，未决/suspected 为零
        # （拿不准者将按 unresolved 登记，此处钉住当前事实；
        # 柱名列「见甲巳」之巳的句读未审属解析层，不作字形未决，
        # 其处置见 SI_GLYPH_DISPOSITION 的 transmitted_list_offsets）。
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
        self.assertEqual(len(by_prefix["pua"]), 1)
        self.assertEqual(by_prefix["pua"][0]["reading"], "玄")
        self.assertEqual(by_prefix["pua"][0]["snapshot_codepoint"],
                         "U+EA20")
        self.assertEqual(len(by_prefix["fang"]), 23)
        spectrum: dict[str, int] = {}
        for n in by_prefix["fang"]:
            self.assertEqual(n["reading_status"], "confirmed")
            self.assertEqual(n["disposition"], "corrected")
            spectrum[n["reading"]] = spectrum.get(n["reading"], 0) + 1
        # 防多源汇再实证：23 处定字分属九种互不相干的原字
        self.assertEqual(spectrum, {"㑹": 5, "㽞": 3, "㓙": 8, "㸔": 2,
                                    "㦯": 1, "㫖": 1, "㓕": 1, "㸃": 1,
                                    "䘮": 1})
        self.assertEqual(len(by_prefix["si"]), 8)
        for n in by_prefix["si"]:
            # 干名槽读己是读法登记（传本三谱系同作巳），故为
            # contextual 而非见证字形订正的 confirmed
            self.assertEqual(n["reading"], "己")
            self.assertEqual(n["reading_status"], "contextual")
            self.assertEqual(n["disposition"], "corrected")
        self.assertEqual(len(by_prefix["ji"]), 7)
        self.assertTrue(all(n["disposition"] == "genuine"
                            and n["reading"] == "己"
                            for n in by_prefix["ji"]))
        self.assertEqual(len(by_prefix["yi"]), 1)
        self.assertEqual(by_prefix["yi"][0]["disposition"], "genuine")
        self.assertEqual(len(by_prefix["xu"]), 2)
        self.assertTrue(all(n["disposition"] == "genuine"
                            and n["reading"] == "戌"
                            for n in by_prefix["xu"]))
        self.assertEqual(len(by_prefix["bian"]), 1)
        bian = by_prefix["bian"][0]
        self.assertEqual(bian["snapshot_glyph"], "仿")
        self.assertEqual(bian["reading"], "仿")
        self.assertEqual(bian["disposition"], "genuine")
        by_status: dict[str, int] = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 24, "contextual": 19})
        by_disp: dict[str, int] = {}
        for n in notes:
            by_disp[n["disposition"]] = by_disp.get(n["disposition"], 0) + 1
        self.assertEqual(by_disp, {"corrected": 32, "genuine": 11})


class SiPartitionTest(unittest.TestCase):
    def test_si_partition_matches_notes(self) -> None:
        part = cj.SI_GLYPH_DISPOSITION
        stem = part["stem_slot_offsets"]
        branch = part["branch_slot_offsets"]
        listed = part["transmitted_list_offsets"]
        self.assertEqual(len(stem), 8)
        self.assertEqual(len(branch), 6)
        self.assertEqual(len(listed), 3)
        self.assertFalse(set(stem) & set(branch))
        self.assertFalse(set(stem) & set(listed))
        self.assertFalse(set(branch) & set(listed))
        si_offsets = sorted(n["char_offset"] for n in cj.COLLATION_NOTES
                            if n["id"].split("-")[1] == "si")
        self.assertEqual(stem, si_offsets)
        # 三类合计 = 本组窗口内「巳」全量 17 处
        self.assertEqual(len(stem) + len(branch) + len(listed), 17)


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_sections(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 27)
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
        mapped = 0
        for quote in cj.COLLATION_QUOTES:
            refs = quote.get("collation_refs")
            if not refs:
                self.assertNotIn("mapped_reading", quote, quote["id"])
                continue
            mapped += 1
            self.assertIn("mapped_reading", quote, quote["id"])
            self.assertNotEqual(quote["mapped_reading"], quote["quote"],
                                quote["id"])
            for ref in refs:
                self.assertIn(ref, notes, ref)
                self.assertIsNotNone(notes[ref]["reading"], ref)
        self.assertEqual(mapped, 17)


class LinkageTransmissionReconciliationTest(unittest.TestCase):
    def test_fact_linkage_matches_code(self) -> None:
        linkage = cj.QULIU_FACT_LINKAGE
        self.assertFalse(linkage["adjudication_semantics_changed"])
        self.assertEqual(
            linkage["registered_material"]["section_ids"],
            ["sanming.juan5.congsa", "sanming.juan5.guansha-hunza",
             "sanming.juan5.guansha-quliu"])
        pat = (ROOT / "src" / "tianji_kb" / "bazi_pattern.py") \
            .read_text(encoding="utf-8")
        self.assertIn("family_specific_competing_conditions", pat)
        self.assertIn("官杀去留/混杂", pat)
        self.assertIn("'unresolved'", pat)
        cov = (ROOT / "src" / "tianji_kb" / "product_coverage.py") \
            .read_text(encoding="utf-8")
        self.assertIn("官杀去留", cov)

    def test_transmission_notes_recorded(self) -> None:
        ids = [t["id"] for t in cj.TRANSMISSION_NOTES]
        self.assertEqual(ids, ["hunza-front-paragraph-recension",
                               "quliu-title-witness-form",
                               "glyph-variant-style"])
        for entry in cj.TRANSMISSION_NOTES:
            self.assertTrue(entry["statement"], entry["id"])

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-042", "ocr-198", "ocr-199", "ocr-200",
                          "ocr-201", "ocr-202", "ocr-447", "ocr-458",
                          "ocr-459", "ocr-460", "ocr-496"])
        self.assertEqual(rec["ocr_candidates_in_window"], 11)
        self.assertEqual(rec["pua_mapping_codepoints_in_window"],
                         ["U+EA20"])
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class PreviousRegistersRegressionTest(unittest.TestCase):
    def test_018abc_registers_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(_dump(cja.COLLATION_NOTES),
                         GOLDEN_A["collation_notes"])
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(_dump(cjb.COLLATION_NOTES),
                         GOLDEN_B["collation_notes"])
        self.assertEqual(len(cjc.COLLATION_NOTES), 81)
        self.assertEqual(_dump(cjc.COLLATION_NOTES),
                         GOLDEN_C["collation_notes"])
        id_sets = [{n["id"] for n in mod.COLLATION_NOTES}
                   for mod in (cja, cjb, cjc, cj)]
        for i in range(len(id_sets)):
            for j in range(i + 1, len(id_sets)):
                self.assertFalse(id_sets[i] & id_sets[j])
        # 三命校勘记累计 44 + 35 + 81 + 43 = 203 条
        self.assertEqual(len(set().union(*id_sets)), 203)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("弃命从煞", "官煞混杂", "官煞去留并官鬼互变杂论",
                       "158219", "161329", "TJ-018-D",
                       "sanming-juan5-collation-register-v1"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
