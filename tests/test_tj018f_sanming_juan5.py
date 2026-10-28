"""TJ-018-F 公开结构测试：三命卷五杂气/阳刃组校勘续册。

本模块（``bazi_sanming_juan5_zaqi_yangren_collation``）是逐条
校勘记注册表在卷五的续册（与 TJ-018-D 共用 register
``sanming-juan5-collation-register-v1``，同一形制、同一字段与
等级口径），纯数据登记、零计算逻辑；本测试只钉登记形制与校勘
红线（字段完备、等级口径、confirmed 依据门槛、防九种定字谱、
巳字干支槽位全量分判、与 Slice A 刃表/Slice B 杂气材料的衔接
登记逐字一致、018-A/B/C/D 注册表 44+35+81+43 条逐字不动、
三命校勘记累计 311 条），不验证任何杂气/阳刃判定（不存在此种
代码路径）。引文与校勘记对快照的逐字复核在密封专项
``tests/test_tj018f_sanming_juan5_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pat_mod
from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cj

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018f_sanming_juan5.json").read_text(
        encoding="utf-8"))
GOLDEN_D = json.loads(
    (ROOT / "tests" / "golden_tj018d_sanming_juan5.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
SECTIONS = {"sanming.juan5.zaqi": (170743, 172958),
            "sanming.juan5.yangren": (180874, 184328)}


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
        # 卷五续册：与 018-D 共用同一 register id，不新建分册
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         "sanming-juan5-collation-register-v1")
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         cjd.COLLATION_REGISTER_ID)
        self.assertEqual(cjd.COLLATION_TASK, "TJ-018-D")
        self.assertEqual(cj.COLLATION_TASK, "TJ-018-F")

    def test_module_matches_golden(self) -> None:
        for attr, key in (("COLLATION_SECTIONS", "sections"),
                          ("COLLATION_QUOTES", "quotes"),
                          ("COLLATION_NOTES", "collation_notes"),
                          ("SI_GLYPH_DISPOSITION", "si_glyph_disposition"),
                          ("ZAQI_YANGREN_FACT_LINKAGE", "fact_linkage"),
                          ("TRANSMISSION_NOTES", "transmission_notes"),
                          ("SEALED_ASSET_RECONCILIATION",
                           "sealed_asset_reconciliation")):
            self.assertEqual(_dump(getattr(cj, attr)), GOLDEN[key], attr)
        self.assertEqual(GOLDEN["register_id"], cj.COLLATION_REGISTER_ID)

    def test_sections_registered(self) -> None:
        self.assertEqual(len(cj.COLLATION_SECTIONS), 2)
        for sec in cj.COLLATION_SECTIONS:
            self.assertEqual(sec["locator"],
                             {"char_start": SECTIONS[sec["section_id"]][0],
                              "char_end": SECTIONS[sec["section_id"]][1]},
                             sec["section_id"])
            self.assertEqual(sec["volume"], "卷五")
            self.assertEqual(sec["school_attribution"], "三命通会体系")
        counts = {s["section_id"]: (s["pua_count"], s["fang_count"])
                  for s in cj.COLLATION_SECTIONS}
        self.assertEqual(counts, {"sanming.juan5.zaqi": (1, 7),
                                  "sanming.juan5.yangren": (8, 42)})
        yangren = cj.COLLATION_SECTIONS[1]
        # 快照节题含 PUA 与讹字「防」逐字保留，校定题读「参㸔」
        self.assertEqual(yangren["title_snapshot"],
                         "论阳刃【前论羊刄煞与此\ueb07防】")
        self.assertEqual(yangren["title_normalized"],
                         "论阳刃【前论羊刄煞与此参㸔】")
        zaqi = cj.COLLATION_SECTIONS[0]
        self.assertEqual([p["part_id"] for p in zaqi["parts"]],
                         ["zaqi_exposition", "zaqi_muyun_appendix"])


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 108)
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
        self.assertEqual(len(by_prefix["pua"]), 9)
        self.assertEqual(
            sorted(n["snapshot_codepoint"] for n in by_prefix["pua"]),
            ["U+E8AA", "U+EA20", "U+EA20", "U+EA85", "U+EA85", "U+EA85",
             "U+EA85", "U+EB07", "U+EE25"])
        self.assertEqual(len(by_prefix["fang"]), 49)
        spectrum: dict[str, int] = {}
        genuine_fang = 0
        for n in by_prefix["fang"]:
            if n["disposition"] == "genuine":
                genuine_fang += 1
                self.assertEqual(n["reading"], "防")
                continue
            self.assertEqual(n["reading_status"], "confirmed")
            self.assertEqual(n["disposition"], "corrected")
            spectrum[n["reading"]] = spectrum.get(n["reading"], 0) + 1
        # 防多源汇再实证：47 处定字分属九种互不相干的原字
        self.assertEqual(spectrum, {"㓙": 29, "㑹": 6, "㫁": 3, "㸔": 3,
                                    "䕶": 2, "䕃": 1, "㓜": 1, "㐫": 1,
                                    "䑕": 1})
        self.assertEqual(genuine_fang, 2)
        self.assertEqual(len(by_prefix["si"]), 15)
        for n in by_prefix["si"]:
            # 干名槽读己是读法登记（传本三谱系同作巳）
            self.assertEqual(n["reading"], "己")
            self.assertEqual(n["reading_status"], "contextual")
            self.assertEqual(n["disposition"], "corrected")
        self.assertEqual(len(by_prefix["ji"]), 12)
        ji_corr = [n for n in by_prefix["ji"]
                   if n["disposition"] == "corrected"]
        self.assertEqual(len(ji_corr), 2)
        for n in ji_corr:
            # 支名槽「己中」读巳：巳/己互讹双向各见其例
            self.assertEqual(n["reading"], "巳")
            self.assertEqual(n["reading_status"], "contextual")
        self.assertEqual(len(by_prefix["yi"]), 2)
        self.assertTrue(all(n["disposition"] == "genuine"
                            for n in by_prefix["yi"]))
        self.assertEqual(len(by_prefix["xu"]), 21)
        self.assertTrue(all(n["disposition"] == "genuine"
                            and n["reading"] == "戌"
                            for n in by_prefix["xu"]))
        by_status: dict[str, int] = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 56, "contextual": 52})
        by_disp: dict[str, int] = {}
        for n in notes:
            by_disp[n["disposition"]] = by_disp.get(n["disposition"], 0) + 1
        self.assertEqual(by_disp, {"corrected": 73, "genuine": 35})


class SiPartitionTest(unittest.TestCase):
    def test_si_partition_matches_notes(self) -> None:
        part = cj.SI_GLYPH_DISPOSITION
        stem = part["stem_slot_offsets"]
        branch = part["branch_slot_offsets"]
        self.assertEqual(len(stem), 15)
        self.assertEqual(len(branch), 8)
        self.assertFalse(set(stem) & set(branch))
        si_offsets = sorted(n["char_offset"] for n in cj.COLLATION_NOTES
                            if n["id"].split("-")[1] == "si")
        self.assertEqual(stem, si_offsets)
        # 两类合计 = 两节窗口内「巳」全量 23 处
        self.assertEqual(len(stem) + len(branch), 23)


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_sections(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 39)
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
        self.assertEqual(mapped, 33)


class LinkageTransmissionReconciliationTest(unittest.TestCase):
    def test_slice_a_blade_table_consistent(self) -> None:
        linkage = cj.ZAQI_YANGREN_FACT_LINKAGE
        self.assertFalse(linkage["adjudication_semantics_changed"])
        # Slice A 刃表五项与本节刃位逐项相符（代码逐字钉住）
        self.assertEqual(pat_mod.REN_BRANCH,
                         {"甲": "卯", "丙": "午", "戊": "午", "庚": "酉",
                          "壬": "子"})
        luren = {q["id"]: q for q in pat_mod.LUREN_QUOTES}
        ours = {q["id"]: q for q in cj.COLLATION_QUOTES}
        # 本批登记引文与 Slice A 已登记引文逐字同一、locator 同一
        self.assertEqual(ours["yr.gangju"]["quote"],
                         luren["sanming.ren_doctrine"]["quote"])
        self.assertEqual(ours["yr.gangju"]["locator"],
                         luren["sanming.ren_doctrine"]["locator"])
        self.assertEqual(ours["yr.ren_positions"]["quote"],
                         luren["sanming.ren_positions"]["quote"])
        self.assertEqual(ours["yr.ren_positions"]["locator"],
                         luren["sanming.ren_positions"]["locator"])
        self.assertIn("一致", linkage["slice_a_consistency"])

    def test_slice_b_overlap_recorded(self) -> None:
        linkage = cj.ZAQI_YANGREN_FACT_LINKAGE
        # Slice B 三命两案窗口与本节窗口互不重叠
        for start, end in ((192131, 192174), (245030, 245081),
                           (33161, 33313)):
            self.assertFalse(170743 <= start and end <= 172958)
        self.assertIn("互不重叠", linkage["slice_b_overlap"])
        cov = (ROOT / "src" / "tianji_kb" / "product_coverage.py") \
            .read_text(encoding="utf-8")
        self.assertIn("禄刃杂气", cov)

    def test_transmission_notes_recorded(self) -> None:
        ids = [t["id"] for t in cj.TRANSMISSION_NOTES]
        self.assertEqual(ids, ["yangren-title-pua-witness-divergence",
                               "yangren-witness-juan-division",
                               "ji-zhong-xutu-transmitted",
                               "glyph-variant-style"])
        for entry in cj.TRANSMISSION_NOTES:
            self.assertTrue(entry["statement"], entry["id"])

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-211", "ocr-212", "ocr-213", "ocr-222",
                          "ocr-223", "ocr-224", "ocr-225", "ocr-227",
                          "ocr-228", "ocr-449", "ocr-502", "ocr-504",
                          "ocr-505", "ocr-506", "ocr-507", "ocr-508",
                          "ocr-509"])
        self.assertEqual(rec["ocr_candidates_in_window"], 23)
        self.assertEqual(rec["pua_mapping_codepoints_in_window"],
                         ["U+E8AA", "U+EA20", "U+EA85", "U+EB07", "U+EE25"])
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class PreviousRegistersRegressionTest(unittest.TestCase):
    def test_previous_registers_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(len(cjc.COLLATION_NOTES), 81)
        self.assertEqual(len(cjd.COLLATION_NOTES), 43)
        self.assertEqual(_dump(cjd.COLLATION_NOTES),
                         GOLDEN_D["collation_notes"])
        id_sets = [{n["id"] for n in mod.COLLATION_NOTES}
                   for mod in (cja, cjb, cjc, cjd, cj)]
        for i in range(len(id_sets)):
            for j in range(i + 1, len(id_sets)):
                self.assertFalse(id_sets[i] & id_sets[j])
        # 三命校勘记累计 44 + 35 + 81 + 43 + 108 = 311 条
        self.assertEqual(len(set().union(*id_sets)), 311)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论杂气", "论阳刃", "170743", "180874", "184328",
                       "TJ-018-F", "311 条"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
