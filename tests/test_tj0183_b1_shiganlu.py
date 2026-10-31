"""TJ-018.3-B1 公开专项：三命通会卷三《论十干禄》018 形制登记。

登记对象：新册 ``sanming-juan3-collation-register-v1``
（``bazi_sanming_juan3_collation``）：卷三《论十干禄》一节
（快照 S0 字符 [74911, 77454)，2,543 字，主文 + 金轝附论两
part）、校勘记 56 条、引文 30 条。本批纯登记：不建 Canonical
节、不翻转 pattern-route-luren、不写规则/判定代码、
determination 零变化。本文件只核对登记数据本身的形制与内部
一致性（与快照逐字复核在密封专项 test_tj0183_b1_shiganlu_sealed
中完成，公开 CI 不执行密封专项）。
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pat_mod
from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan3_collation as cj
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cje
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as cjf

ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads(
(ROOT / "config" / "knowledge_sources.json").read_text(
encoding="utf-8"))["sources"]
GOLDEN = json.loads(
(ROOT / "tests" / "golden_tj0183_b1_shiganlu.json").read_text(
encoding="utf-8"))

SECTION = (74911, 77454)
STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
"context"}


def _dump(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


class ModuleFormTest(unittest.TestCase):
    def test_module_matches_golden(self) -> None:
        for attr, key in (
        ("COLLATION_SECTIONS", "sections"),
        ("COLLATION_QUOTES", "quotes"),
        ("COLLATION_NOTES", "collation_notes"),
        ("SI_GLYPH_DISPOSITION", "si_glyph_disposition"),
        ("SHIGANLU_FACT_LINKAGE", "fact_linkage"),
        ("TRANSMISSION_NOTES", "transmission_notes"),
        ("SEALED_ASSET_RECONCILIATION",
        "sealed_asset_reconciliation")):
            self.assertEqual(_dump(getattr(cj, attr)), _dump(GOLDEN[key]),
        attr)
        self.assertEqual(GOLDEN["register_id"], cj.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_TASK, "TJ-018.3-B1")

    def test_snapshot_registry_matches_precedent(self) -> None:
        meta = cj.COLLATION_SNAPSHOTS["sanming_tonghui.txt"]
        self.assertEqual(meta["sha256"],
        "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc"
        "111e62b59378010c86")
        self.assertEqual(meta["bytes"], 1342659)
        self.assertEqual(meta["chars"], 461157)

    def test_section_registered(self) -> None:
        self.assertEqual(len(cj.COLLATION_SECTIONS), 1)
        sec = cj.COLLATION_SECTIONS[0]
        self.assertEqual(sec["section_id"], "sanming.juan3.shiganlu")
        self.assertEqual(sec["locator"],
        {"char_start": SECTION[0], "char_end": SECTION[1]})
        self.assertEqual(sec["volume"], "卷三")
        self.assertEqual(sec["school_attribution"], "三命通会体系")
        self.assertEqual(sec["pua_count"], 2)
        self.assertEqual(sec["fang_count"], 16)
        # 节题自注附论结构，快照原字逐字保留（无 PUA、无讹字）
        self.assertEqual(sec["title_snapshot"],
        "论十干禄")
        self.assertEqual(sec["title_normalized"], sec["title_snapshot"])
        self.assertEqual(
        [(p["part_id"], p["locator"]["char_start"],
        p["locator"]["char_end"]) for p in sec["parts"]],
        [("shiganlu_exposition", 74911, 77214),
        ("jinyu_appendix", 77214, 77454)])
        
        
class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 56)
        ids = [n["id"] for n in cj.COLLATION_NOTES]
        self.assertEqual(len(ids), len(set(ids)))
        for note in cj.COLLATION_NOTES:
            self.assertTrue(self.REQUIRED <= set(note), note["id"])
            self.assertEqual(note["section_id"], "sanming.juan3.shiganlu")
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
                         ["sgl-fang-76988"])
        for note in unresolved:
            self.assertIsNone(note["reading"], note["id"])
            self.assertEqual(note["disposition"], "unresolved", note["id"])
            self.assertIsNone(note["usable_grade"], note["id"])
        suspected = [n for n in cj.COLLATION_NOTES
                     if n["reading_status"] == "suspected"]
        self.assertEqual([n["id"] for n in suspected], ["sgl-ji-76212"])
        for note in suspected:
            self.assertEqual(note["reading"], "巳", note["id"])
            self.assertEqual(note["usable_grade"], "Q3", note["id"])

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
        self.assertEqual(len(by_prefix["pua"]), 2)
        self.assertEqual(
            sorted(n["snapshot_codepoint"] for n in by_prefix["pua"]),
            ["U+EA20", "U+EAC0"])
        self.assertTrue(all(n["reading_status"] == "confirmed"
                            and n["disposition"] == "corrected"
                            for n in by_prefix["pua"]))
        self.assertEqual(len(by_prefix["fang"]), 16)
        spectrum: dict[str, int] = {}
        for n in by_prefix["fang"]:
            if n["disposition"] == "unresolved":
                self.assertEqual(n["id"], "sgl-fang-76988")
                continue
            self.assertEqual(n["reading_status"], "confirmed")
            self.assertEqual(n["disposition"], "corrected")
            self.assertEqual(n["usable_grade"], "Q1")
            spectrum[n["reading"]] = spectrum.get(n["reading"], 0) + 1
        # 防多源汇讹再实证：15 处定字分属四种互不相干的原字
        self.assertEqual(spectrum, {"㓙": 1, "㐫": 11, "㑹": 2, "㫖": 1})
        self.assertEqual(len(by_prefix["ji"]), 23)
        ji_corr = [n for n in by_prefix["ji"]
                   if n["disposition"] == "corrected"]
        self.assertEqual(sorted(n["char_offset"] for n in ji_corr),
                         [74974, 75028, 75034, 75233, 75319, 76025,
                          76212, 76661, 76829])
        self.assertTrue(all(n["reading"] == "巳" for n in ji_corr))
        ji_genuine = [n for n in by_prefix["ji"]
                      if n["disposition"] == "genuine"]
        self.assertEqual(len(ji_genuine), 14)
        self.assertTrue(all(n["reading"] == "己"
                            and n["reading_status"] == "contextual"
                            for n in ji_genuine))
        self.assertEqual(len(by_prefix["yi"]), 2)
        yi = {n["char_offset"]: n for n in by_prefix["yi"]}
        self.assertEqual(yi[76644]["disposition"], "corrected")
        self.assertEqual(yi[76644]["reading_status"], "contextual")
        self.assertEqual(yi[76644]["reading"], "巳")
        self.assertEqual(yi[76744]["disposition"], "genuine")
        self.assertEqual(len(by_prefix["si"]), 1)
        self.assertEqual(by_prefix["si"][0]["char_offset"], 75035)
        self.assertEqual(by_prefix["si"][0]["reading"], "己")
        self.assertEqual(by_prefix["si"][0]["reading_status"], "confirmed")
        self.assertEqual(len(by_prefix["xu"]), 12)
        self.assertTrue(all(n["disposition"] == "genuine"
                            and n["reading"] == "戌"
                            for n in by_prefix["xu"]))
        by_status: dict[str, int] = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 26, "contextual": 28,
                                     "suspected": 1, "unresolved": 1})
        by_disp: dict[str, int] = {}
        for n in notes:
            by_disp[n["disposition"]] = by_disp.get(n["disposition"], 0) + 1
        self.assertEqual(by_disp, {"corrected": 28, "genuine": 27,
                                   "unresolved": 1})


class SiPartitionTest(unittest.TestCase):
    def test_si_partition_matches_notes(self) -> None:
        part = cj.SI_GLYPH_DISPOSITION
        stem = part["stem_slot_offsets"]
        branch = part["branch_slot_offsets"]
        self.assertEqual(stem, [75035])
        self.assertEqual(len(branch), 17)
        self.assertFalse(set(stem) & set(branch))
        si_offsets = sorted(n["char_offset"] for n in cj.COLLATION_NOTES
                            if n["id"].split("-")[1] == "si")
        self.assertEqual(stem, si_offsets)
        # 两类合计 = 本节窗口内「巳」全量 18 处
        self.assertEqual(len(stem) + len(branch), 18)


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_section(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 30)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            self.assertEqual(
                len(quote["quote"]), loc["char_end"] - loc["char_start"],
                quote["id"])
            self.assertEqual(quote["source_section_id"],
                             "sanming.juan3.shiganlu")
            self.assertTrue(SECTION[0] <= loc["char_start"]
                            and loc["char_end"] <= SECTION[1], quote["id"])
            self.assertIn(quote["part_id"],
                          ("shiganlu_exposition", "jinyu_appendix"),
                          quote["id"])

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
        self.assertEqual(mapped, 18)

    def test_definition_quote_is_slice_a_sentence(self) -> None:
        ours = {q["id"]: q for q in cj.COLLATION_QUOTES}
        self.assertEqual(ours["sgl.definition"]["quote"],
                         "甲禄寅乙禄卯庚禄申辛禄酉壬禄亥癸禄子丙禄己丁禄午"
                         "戊寄己巳寄午谓己午乃火旺之乡子随母得禄之义")
        self.assertEqual(ours["sgl.definition"]["mapped_reading"],
                         "甲禄寅乙禄卯庚禄申辛禄酉壬禄亥癸禄子丙禄巳丁禄午"
                         "戊寄巳己寄午谓己午乃火旺之乡子随母得禄之义")
        self.assertEqual(ours["sgl.definition"]["collation_refs"],
                         ["sgl-ji-75028", "sgl-ji-75034", "sgl-si-75035"])


class LinkageTransmissionReconciliationTest(unittest.TestCase):
    def test_slice_a_linkage_consistent_no_duplicate(self) -> None:
        linkage = cj.SHIGANLU_FACT_LINKAGE
        self.assertFalse(linkage["adjudication_semantics_changed"])
        refs = {r["code_module"]: r
                for r in linkage["existing_code_references"]}
        self.assertEqual(refs["src/tianji_kb/bazi_pattern.py"]["status"],
                         "consistent")
        self.assertEqual(refs["src/tianji_kb/bazi_earth_roots.py"]["status"],
                         "consistent")
        # pattern-route-luren 联合翻转属 B-2，本批维持 pending
        self.assertEqual(
            refs["src/tianji_kb/bazi_registration_governance.py"]["status"],
            "unresolved")
        # Slice A 禄表与本节定义句读法（LU_BRANCH）逐项钉住
        self.assertEqual(pat_mod.LU_BRANCH,
                         {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
                          "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
                          "壬": "亥", "癸": "子"})
        luren = {q["id"]: q for q in pat_mod.LUREN_QUOTES}
        ours = {q["id"]: q for q in cj.COLLATION_QUOTES}
        # 同一定义句：逐字同一、locator 同一，本批承接绑定不重复登记
        self.assertEqual(ours["sgl.definition"]["quote"],
                         luren["sanming.lu_sentence"]["quote"])
        self.assertEqual(ours["sgl.definition"]["locator"],
                         luren["sanming.lu_sentence"]["locator"])
        self.assertIn("逐字一致", linkage["slice_a_consistency"])

    def test_transmission_notes_recorded(self) -> None:
        ids = [t["id"] for t in cj.TRANSMISSION_NOTES]
        self.assertEqual(ids, ["shiganlu-title-appendix-structure",
                               "shiganlu-slice-a-window-relation",
                               "glyph-variant-style"])
        for entry in cj.TRANSMISSION_NOTES:
            self.assertTrue(entry["statement"], entry["id"])

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-104", "ocr-105", "ocr-106", "ocr-108",
                          "ocr-109", "ocr-110", "ocr-111", "ocr-112",
                          "ocr-113", "ocr-137", "ocr-478"])
        self.assertEqual(rec["ocr_candidates_in_window"], 3)
        self.assertEqual(rec["pua_mapping_codepoints_in_window"],
                         ["U+EA20", "U+EAC0"])
        self.assertEqual(rec["s0_s3_diff_in_window"], 17)
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)
        # P2 残余防处置册 seq 47 衔接：本节唯一残余防位点的注记在册
        fang_unresolved = [n for n in cj.COLLATION_NOTES
                           if n["id"] == "sgl-fang-76988"][0]
        self.assertIn("seq 47", fang_unresolved["note"])
        self.assertIn("deferred_no_witness", fang_unresolved["note"])
        self.assertIn("seq 47", rec["note"])


class PreviousRegistersRegressionTest(unittest.TestCase):
    def test_previous_registers_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(len(cjc.COLLATION_NOTES), 81)
        self.assertEqual(len(cjd.COLLATION_NOTES), 43)
        self.assertEqual(len(cje.COLLATION_NOTES), 108)
        self.assertEqual(len(cjf.COLLATION_NOTES), 72)
        id_sets = [{n["id"] for n in mod.COLLATION_NOTES}
                   for mod in (cja, cjb, cjc, cjd, cje, cjf, cj)]
        for i in range(len(id_sets)):
            for j in range(i + 1, len(id_sets)):
                self.assertFalse(id_sets[i] & id_sets[j])
        # 三命校勘记累计 44 + 35 + 81 + 43 + 108 + 72 + 56 = 439 条
        self.assertEqual(len(set().union(*id_sets)), 439)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # 本批不新增 Source：登记表维持 102 条（C:96 / D:6）
        self.assertEqual(len(SOURCES), 102)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论十干禄", "74911", "77454", "TJ-018.3-B1",
                       "439 条"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
