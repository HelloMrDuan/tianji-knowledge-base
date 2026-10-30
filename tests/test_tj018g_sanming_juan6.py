"""TJ-018-G 公开结构测试：三命卷六方局/八象组校勘续册。

本模块（``bazi_sanming_juan6_fangju_baxiang_collation``）是逐条
校勘记注册表在卷六的首册（新建 register
``sanming-juan6-collation-register-v1``，同一形制、同一字段与
等级口径），纯数据登记、零计算逻辑；本测试只钉登记形制与校勘
红线（字段完备、等级口径、confirmed 依据门槛、防四种定字谱、
巳字干支槽位全量分判、方局支组与既有执行事实对应面登记、八象
与从化象 presence 接口登记、018-A/B/C/D/F 注册表
44+35+81+43+108 条逐字不动、三命校勘记累计 383 条），不验证
任何方局入格或八象判定（不存在此种代码路径）。引文与校勘记
对快照的逐字复核在密封专项
``tests/test_tj018g_sanming_juan6_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cjf
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as cj

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018g_sanming_juan6.json").read_text(
        encoding="utf-8"))
GOLDEN_F = json.loads(
    (ROOT / "tests" / "golden_tj018f_sanming_juan5.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

STATUSES = {"confirmed", "contextual", "suspected", "unresolved"}
DISPOSITIONS = {"corrected", "genuine", "unresolved"}
GRADES = {"Q1", "Q2", "Q3", None}
BASIS_KINDS = {"witness", "sealed_asset", "same_section_corroboration",
               "context"}
SECTIONS = {"sanming.juan6.quzhi": (204089, 204236),
            "sanming.juan6.yanshang": (204236, 204349),
            "sanming.juan6.congge": (204349, 204476),
            "sanming.juan6.runxia": (204476, 204631),
            "sanming.juan6.jiashe": (204631, 204836),
            "sanming.juan6.fanxiang": (212467, 212729),
            "sanming.juan6.zhaoxiang": (212729, 212991),
            "sanming.juan6.guixiang": (212991, 213270),
            "sanming.juan6.fuxiang": (213270, 213485),
            "sanming.juan6.shuxiang": (213485, 213815),
            "sanming.juan6.leixiang": (213815, 214129),
            "sanming.juan6.congxiang": (214129, 214516),
            "sanming.juan6.huaxiang": (214516, 214948)}


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
        # 卷六首册：新建分册 register，与卷二/卷五两册并列、互不相同
        self.assertEqual(cj.COLLATION_REGISTER_ID,
                         "sanming-juan6-collation-register-v1")
        self.assertNotEqual(cj.COLLATION_REGISTER_ID,
                            cja.COLLATION_REGISTER_ID)
        self.assertNotEqual(cj.COLLATION_REGISTER_ID,
                            cjd.COLLATION_REGISTER_ID)
        self.assertEqual(cj.COLLATION_TASK, "TJ-018-G")

    def test_module_matches_golden(self) -> None:
        for attr, key in (("COLLATION_SECTIONS", "sections"),
                          ("COLLATION_QUOTES", "quotes"),
                          ("COLLATION_NOTES", "collation_notes"),
                          ("SI_GLYPH_DISPOSITION", "si_glyph_disposition"),
                          ("FANGJU_BAXIANG_FACT_LINKAGE", "fact_linkage"),
                          ("TRANSMISSION_NOTES", "transmission_notes"),
                          ("SEALED_ASSET_RECONCILIATION",
                           "sealed_asset_reconciliation")):
            self.assertEqual(_dump(getattr(cj, attr)), GOLDEN[key], attr)
        self.assertEqual(GOLDEN["register_id"], cj.COLLATION_REGISTER_ID)

    def test_sections_registered(self) -> None:
        self.assertEqual(len(cj.COLLATION_SECTIONS), 13)
        for sec in cj.COLLATION_SECTIONS:
            self.assertEqual(sec["locator"],
                             {"char_start": SECTIONS[sec["section_id"]][0],
                              "char_end": SECTIONS[sec["section_id"]][1]},
                             sec["section_id"])
            self.assertEqual(sec["volume"], "卷六")
            self.assertEqual(sec["school_attribution"], "三命通会体系")
            self.assertEqual(sec["title_snapshot"], sec["title_normalized"])
        counts = {s["section_id"]: (s["pua_count"], s["fang_count"])
                  for s in cj.COLLATION_SECTIONS}
        self.assertEqual(counts, {
            "sanming.juan6.quzhi": (0, 0), "sanming.juan6.yanshang": (0, 0),
            "sanming.juan6.congge": (0, 0), "sanming.juan6.runxia": (0, 3),
            "sanming.juan6.jiashe": (0, 2), "sanming.juan6.fanxiang": (0, 0),
            "sanming.juan6.zhaoxiang": (0, 0),
            "sanming.juan6.guixiang": (1, 1), "sanming.juan6.fuxiang": (0, 0),
            "sanming.juan6.shuxiang": (0, 2), "sanming.juan6.leixiang": (0, 2),
            "sanming.juan6.congxiang": (0, 3),
            "sanming.juan6.huaxiang": (2, 2)})
        # 两组组界与审源钉值一致：方局组 747 字、八象组 2481 字
        fj = [s for s in cj.COLLATION_SECTIONS
              if s["locator"]["char_start"] < 210000]
        bx = [s for s in cj.COLLATION_SECTIONS
              if s["locator"]["char_start"] > 210000]
        self.assertEqual((fj[0]["locator"]["char_start"],
                          fj[-1]["locator"]["char_end"]), (204089, 204836))
        self.assertEqual((bx[0]["locator"]["char_start"],
                          bx[-1]["locator"]["char_end"]), (212467, 214948))


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 72)
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
        self.assertEqual(len(by_prefix["pua"]), 3)
        self.assertEqual(
            sorted(n["snapshot_codepoint"] for n in by_prefix["pua"]),
            ["U+EA20", "U+EA20", "U+EEA6"])
        self.assertEqual(len(by_prefix["fang"]), 15)
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
        # 防多源汇再实证：14 处定字分属四种互不相干的原字
        self.assertEqual(spectrum, {"㑹": 7, "㸔": 4, "㐫": 2, "㣲": 1})
        self.assertEqual(genuine_fang, 1)
        self.assertEqual(len(by_prefix["si"]), 9)
        for n in by_prefix["si"]:
            # 干名/藏干名槽读己是读法登记（两谱系见证同作巳）
            self.assertEqual(n["reading"], "己")
            self.assertEqual(n["reading_status"], "contextual")
            self.assertEqual(n["disposition"], "corrected")
        self.assertEqual(len(by_prefix["ji"]), 13)
        ji_corr = [n for n in by_prefix["ji"]
                   if n["disposition"] == "corrected"]
        self.assertEqual(len(ji_corr), 3)
        for n in ji_corr:
            # 支组名槽「己酉丑」读巳：巳/己互讹在本组亦有其例
            self.assertEqual(n["reading"], "巳")
            self.assertEqual(n["reading_status"], "contextual")
        self.assertEqual(len(by_prefix["xu"]), 32)
        self.assertTrue(all(n["disposition"] == "genuine"
                            and n["reading"] == "戌"
                            for n in by_prefix["xu"]))
        by_status: dict[str, int] = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 17, "contextual": 55})
        by_disp: dict[str, int] = {}
        for n in notes:
            by_disp[n["disposition"]] = by_disp.get(n["disposition"], 0) + 1
        self.assertEqual(by_disp, {"corrected": 29, "genuine": 43})


class SiPartitionTest(unittest.TestCase):
    def test_si_partition_matches_notes(self) -> None:
        part = cj.SI_GLYPH_DISPOSITION
        stem = part["stem_slot_offsets"]
        branch = part["branch_slot_offsets"]
        self.assertEqual(len(stem), 9)
        self.assertEqual(len(branch), 29)
        self.assertFalse(set(stem) & set(branch))
        si_offsets = sorted(n["char_offset"] for n in cj.COLLATION_NOTES
                            if n["id"].split("-")[1] == "si")
        self.assertEqual(stem, si_offsets)
        # 两类合计 = 两组窗口内「巳」全量 38 处
        self.assertEqual(len(stem) + len(branch), 38)


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_sections(self) -> None:
        self.assertEqual(len(cj.COLLATION_QUOTES), 31)
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
        self.assertEqual(mapped, 16)


class LinkageTransmissionReconciliationTest(unittest.TestCase):
    def test_fangju_correspondence_recorded(self) -> None:
        linkage = cj.FANGJU_BAXIANG_FACT_LINKAGE
        self.assertFalse(linkage["adjudication_semantics_changed"])
        corr = linkage["fangju_group_correspondence"]
        self.assertEqual([c["text_group"] for c in corr],
                         [["亥", "卯", "未"], ["寅", "午", "戌"],
                          ["巳", "酉", "丑"], ["申", "子", "辰"],
                          ["辰", "戌", "丑", "未"]])
        self.assertIn("triple_harmony", corr[0]["executed_fact"])
        self.assertIn("directional_meeting", corr[0]["executed_fact"])
        # 稼穑四季支组在执行事实层无对应组：缺口如实登记
        self.assertIn("无对应组事实", corr[4]["executed_fact"])
        core = (ROOT / "src" / "tianji_kb" / "bazi_core.py") \
            .read_text(encoding="utf-8")
        self.assertIn("branch_triple_harmonies", core)
        self.assertIn("directional_meetings", core)
        self.assertIn("presence", linkage["baxiang_interface"])
        self.assertIn("unresolved", linkage["baxiang_interface"])

    def test_transmission_notes_recorded(self) -> None:
        ids = [t["id"] for t in cj.TRANSMISSION_NOTES]
        self.assertEqual(ids, ["congge-ji-witness-divergence",
                               "guixiang-pua-mikko-image-glyph",
                               "fang-variant-style",
                               "glyph-variant-style"])
        for entry in cj.TRANSMISSION_NOTES:
            self.assertTrue(entry["statement"], entry["id"])

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(rec["text_collation_in_window"],
                         ["ocr-248", "ocr-521"])
        self.assertEqual(rec["ocr_candidates_in_window"], 13)
        self.assertEqual(rec["pua_mapping_codepoints_in_window"],
                         ["U+EA20", "U+EEA6"])
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class PreviousRegistersRegressionTest(unittest.TestCase):
    def test_previous_registers_untouched(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(len(cjc.COLLATION_NOTES), 81)
        self.assertEqual(len(cjd.COLLATION_NOTES), 43)
        self.assertEqual(len(cjf.COLLATION_NOTES), 108)
        self.assertEqual(_dump(cjf.COLLATION_NOTES),
                         GOLDEN_F["collation_notes"])
        id_sets = [{n["id"] for n in mod.COLLATION_NOTES}
                   for mod in (cja, cjb, cjc, cjd, cjf, cj)]
        for i in range(len(id_sets)):
            for j in range(i + 1, len(id_sets)):
                self.assertFalse(id_sets[i] & id_sets[j])
        # 三命校勘记累计 44 + 35 + 81 + 43 + 108 + 72 = 383 条
        self.assertEqual(len(set().union(*id_sets)), 383)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("曲直", "稼穑", "返象", "化象", "204089", "214948",
                       "TJ-018-G", "383 条"):
            self.assertIn(needle, sanming)


if __name__ == "__main__":
    unittest.main()
