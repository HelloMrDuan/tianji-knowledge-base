"""TJ-018-A 公开结构测试：三命卷二两节校勘记注册表与扩登记。

本模块（``bazi_sanming_juan2_collation``）是纯数据登记、零计算逻辑；
本测试只钉登记形制与校勘红线（校勘记字段完备、等级口径、confirmed
依据门槛、未决项 reading=None、丁长生 conflict 两说齐备不裁定、
十干覆盖齐全、密封资产对账在案），不验证任何旺衰计算（不存在此种
代码路径）。引文与校勘记对快照的逐字复核在密封专项
``tests/test_tj018a_sanming_juan2_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cj

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
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


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [name for name, obj in inspect.getmembers(cj)
                 if inspect.isfunction(obj)]
        self.assertEqual(funcs, [])

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_QUOTES, ensure_ascii=False)),
            GOLDEN["quotes"])
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_NOTES, ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(cj.STEM_COVERAGE, ensure_ascii=False)),
            GOLDEN["stem_coverage"])
        self.assertEqual(
            json.loads(json.dumps(cj.DING_CHANGSHENG_CONFLICT,
                                  ensure_ascii=False)),
            GOLDEN["ding_changsheng_conflict"])

    def test_sections_registered(self) -> None:
        secs = {s["section_id"]: s for s in cj.COLLATION_SECTIONS}
        s1 = secs["sanming.juan2.tiangan_yinyang_shengsi"]
        self.assertEqual(s1["locator"],
                         {"char_start": 38890, "char_end": 43082})
        self.assertEqual((s1["pua_count"], s1["fang_count"]), (4, 10))
        parts = {p["part_id"]: p for p in s1["parts"]}
        self.assertEqual(parts["debate_quotations"]["status"],
                         "archived_not_evidence")
        s2 = secs["sanming.juan2.wuxing_wangxiang_jisheng"]
        self.assertEqual(s2["locator"],
                         {"char_start": 54894, "char_end": 55673})
        self.assertEqual((s2["pua_count"], s2["fang_count"]), (0, 1))


class CollationNoteFormTest(unittest.TestCase):
    REQUIRED = {"id", "section_id", "char_offset", "context_short",
                "snapshot_glyph", "reading", "reading_status",
                "disposition", "basis", "usable_grade", "note"}

    def test_every_note_has_required_fields(self) -> None:
        self.assertEqual(len(cj.COLLATION_NOTES), 44)
        ids = [n["id"] for n in cj.COLLATION_NOTES]
        self.assertEqual(len(ids), len(set(ids)))
        for note in cj.COLLATION_NOTES:
            self.assertTrue(self.REQUIRED <= set(note), note["id"])
            self.assertIn(note["reading_status"], STATUSES, note["id"])
            self.assertIn(note["disposition"], DISPOSITIONS, note["id"])
            self.assertIn(note["usable_grade"], GRADES, note["id"])
            self.assertTrue(note["basis"], note["id"])
            for basis in note["basis"]:
                self.assertIn(basis["kind"], BASIS_KINDS, note["id"])
                self.assertTrue(basis["witness"], note["id"])
                self.assertTrue(basis["quote_short"], note["id"])
            # 登记的原字必须出现在所登记的语境中
            self.assertIn(note["snapshot_glyph"], note["context_short"],
                          note["id"])
            # 定位偏移处的字即语境中心字（±14 窗口）
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

    def test_unresolved_has_no_reading(self) -> None:
        unresolved = [n for n in cj.COLLATION_NOTES
                      if n["reading_status"] == "unresolved"]
        self.assertEqual({n["id"] for n in unresolved},
                         {"sm2-si-39688", "sm2-gap-42148"})
        for note in unresolved:
            self.assertIsNone(note["reading"], note["id"])
            self.assertEqual(note["disposition"], "unresolved", note["id"])

    def test_readings_have_no_pua(self) -> None:
        for note in cj.COLLATION_NOTES:
            if note["reading"] is not None:
                self.assertFalse(any(_is_pua(c) for c in note["reading"]),
                                 note["id"])

    def test_counts_by_class(self) -> None:
        notes = cj.COLLATION_NOTES
        pua = [n for n in notes if n["id"].startswith("sm2-pua-")]
        fang = [n for n in notes if n["id"].startswith("sm2-fang-")]
        self.assertEqual(len(pua), 4)
        self.assertTrue(all(n["reading_status"] == "confirmed"
                            for n in pua))
        self.assertEqual(len(fang), 11)
        genuine = [n for n in fang if n["disposition"] == "genuine"]
        self.assertEqual([n["id"] for n in genuine], ["sm2-fang-41370"])
        corrected = [n for n in fang if n["disposition"] == "corrected"]
        self.assertEqual(len(corrected), 10)
        # 防的多源汇定性：校定字两两互不相干，不得存在全局替换
        readings = {n["reading"] for n in corrected}
        self.assertGreaterEqual(len(readings), 7)
        by_status = {}
        for n in notes:
            by_status[n["reading_status"]] = \
                by_status.get(n["reading_status"], 0) + 1
        self.assertEqual(by_status, {"confirmed": 25, "contextual": 14,
                                     "suspected": 3, "unresolved": 2})

    def test_fire_scout_named_corrections_present(self) -> None:
        by_id = {n["id"]: n for n in cj.COLLATION_NOTES}
        self.assertEqual(by_id["sm2-ji-39571"]["reading"], "巳")
        self.assertEqual(by_id["sm2-yi-40755"]["reading"], "巳")
        for nid in ("sm2-ji-39571", "sm2-yi-40755"):
            self.assertEqual(by_id[nid]["reading_status"], "confirmed")


class QuoteFormTest(unittest.TestCase):
    def test_quotes_have_locators_inside_sections(self) -> None:
        s1 = (38890, 43082)
        s2 = (54894, 55673)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            self.assertEqual(
                len(quote["quote"]), loc["char_end"] - loc["char_start"],
                quote["id"])
            if quote["source_id"] == "bazi.source.sanmingtonghui" and \
                    quote["source_section_id"] and \
                    "renyuan" not in quote["source_section_id"]:
                window = s2 if "wangxiang" in quote["source_section_id"] \
                    else s1
                self.assertTrue(window[0] <= loc["char_start"]
                                and loc["char_end"] <= window[1],
                                quote["id"])

    def test_fire_line_quotes_present(self) -> None:
        by_id = {q["id"]: q for q in cj.COLLATION_QUOTES}
        for qid in ("sm2.bing_lu", "sm2.bing_shengsi", "sm2.ding_lu",
                    "sm2.ding_shengsi", "sm2.summary_bracket",
                    "sm2.gong_sequence", "sm2.tiyao"):
            self.assertIn(qid, by_id)
        self.assertIn("sm2-ji-39571",
                      by_id["sm2.bing_lu"]["collation_refs"])

    def test_no_quote_contains_unresolved_glyphs(self) -> None:
        for quote in cj.COLLATION_QUOTES:
            self.assertNotIn("□", quote["quote"], quote["id"])


class ConflictAndCoverageTest(unittest.TestCase):
    def test_ding_conflict_two_branches_unadjudicated(self) -> None:
        conflict = cj.DING_CHANGSHENG_CONFLICT
        self.assertEqual(conflict["status"], "conflict")
        self.assertIsNone(conflict["adjudication"])
        branches = {b["branch_id"]: b for b in conflict["branches"]}
        self.assertEqual(branches["ding-sheng-you"]["reading"], "酉")
        self.assertEqual(branches["ding-sheng-yin"]["reading"], "寅")
        refs = {e["quote_ref"] for b in conflict["branches"]
                for e in b["evidence"]}
        self.assertTrue({"sm2.ding_shengsi", "sf.nanyue_ding",
                         "sf.sisheng"} <= refs)

    def test_stem_coverage_complete(self) -> None:
        self.assertEqual([r["stem"] for r in cj.STEM_COVERAGE],
                         list("甲乙丙丁戊己庚辛壬癸"))
        self.assertEqual(cj.STEM_COVERAGE_CONCLUSION["missing_stems"], [])
        for row in cj.STEM_COVERAGE:
            for kind in ("lu", "sheng", "si"):
                self.assertTrue(row[kind]["reading"], row["stem"])

    def test_root_table_assessment_partial(self) -> None:
        self.assertEqual(cj.ROOT_TABLE_ASSESSMENT["verdict"], "partial")
        facts = {f["fact_id"]: f for f in cj.CORROBORATION_FACTS}
        self.assertEqual(facts["no-diwang-sentence"]["status"], "absent")
        self.assertEqual(facts["bing-ku-agreement"]["status"],
                         "agreed_with_scope_limit")
        self.assertEqual(facts["bing-jue-single_source"]["status"],
                         "single_source")

    def test_sealed_reconciliation_recorded(self) -> None:
        rec = cj.SEALED_ASSET_RECONCILIATION
        self.assertEqual(len(rec["in_window_entries"]), 5)
        self.assertEqual(rec["zero_match_total"], 66)
        self.assertEqual(rec["zero_match_in_window"], 0)


class ScopeRegistrationTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)

    def test_scope_fragments_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论天干阴阳生死", "38890", "论五行旺相休囚死并寄生十二宫",
                       "TJ-018-A", "sm2-ji-39571"):
            self.assertIn(needle, sanming)
        shenfeng = by_id["bazi.source.shenfeng"]["review_scope"]
        for needle in ("十干禄", "TJ-018-A", "丁火长生于酉"):
            self.assertIn(needle, shenfeng)


if __name__ == "__main__":
    unittest.main()
