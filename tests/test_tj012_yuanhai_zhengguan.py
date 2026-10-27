"""TJ-012.3 Slice D 前置（渊海逐节登记）的公开结构测试：正官组三节登记。

本模块（``bazi_yuanhai_zhengguan``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（三节登记形制、缺字登记完整性、引文窗
避缺字、转手复核逐句在案、既有 s055–s059 窗口在册、印綬跳过段
逐段有理由、禁止 determination 语义键），不验证任何正官格判定
（不存在此种代码路径）。引文逐字等值与快照复核在密封专项
``tests/test_tj012_yuanhai_zhengguan_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_zhengguan as yh

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_zhengguan.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
}


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


class MirrorTest(unittest.TestCase):
    def test_module_mirrors_golden(self) -> None:
        self.assertEqual(yh.YUANHAI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(yh.YUANHAI_SECTIONS, GOLDEN["sections"])
        self.assertEqual(yh.YUANHAI_ZHENGGUAN_QUOTES, GOLDEN["quotes"])
        self.assertEqual(yh.YUANHAI_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(yh.YUANHAI_GAP_REGISTER, GOLDEN["gap_register"])
        self.assertEqual(yh.YUANHAI_GLYPH_NOTES, GOLDEN["glyph_notes"])
        self.assertEqual(yh.YUANHAI_LEGACY_WINDOWS,
                         GOLDEN["legacy_windows"])
        self.assertEqual(yh.YINSHOU_SKIPPED_WINDOWS,
                         GOLDEN["yinshou_skipped_windows"])
        self.assertEqual(yh.OPERATIVE_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(yh.YUANHAI_ZHENGGUAN_NOTES, GOLDEN["notes"])
        self.assertEqual(yh.YUANHAI_ZHENGGUAN_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(yh, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(yh, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_three_sections_registered(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.zhengguan",
                                     "yuanhai.guansha_hunza",
                                     "yuanhai.yinshou"})
        zg = secs["yuanhai.zhengguan"]
        self.assertEqual(zg["registration_mode"], "full_section")
        self.assertEqual(zg["locator"], {"char_start": 9703,
                                         "char_end": 10321})
        self.assertEqual(len(zg["full_text"]), 618)
        gs = secs["yuanhai.guansha_hunza"]
        self.assertEqual(gs["registration_mode"], "full_section")
        self.assertEqual(gs["locator"], {"char_start": 12400,
                                         "char_end": 12506})
        self.assertEqual(len(gs["full_text"]), 106)
        ys = secs["yuanhai.yinshou"]
        self.assertEqual(ys["registration_mode"], "relevant_windows_only")
        self.assertEqual(ys["locator"], {"char_start": 12506,
                                          "char_end": 13494})
        self.assertIsNone(ys["full_text"])

    def test_full_texts_inside_section_locators(self) -> None:
        for s in yh.YUANHAI_SECTIONS:
            if s["full_text"] is not None:
                span = (s["locator"]["char_end"]
                        - s["locator"]["char_start"])
                self.assertEqual(len(s["full_text"]), span, s["section_id"])
                self.assertTrue(s["full_text"].startswith("《"),
                                s["section_id"])

    def test_yinshou_new_windows_all_inside_section(self) -> None:
        ys_quotes = [q for q in yh.YUANHAI_ZHENGGUAN_QUOTES
                     if q["source_section_id"] == "yuanhai.yinshou"]
        self.assertEqual(len(ys_quotes), 7)
        for q in ys_quotes:
            self.assertGreaterEqual(q["locator"]["char_start"], 12506)
            self.assertLessEqual(q["locator"]["char_end"], 13494)
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_yinshou_skipped_windows_have_reasons(self) -> None:
        self.assertEqual(len(yh.YINSHOU_SKIPPED_WINDOWS), 12)
        for w in yh.YINSHOU_SKIPPED_WINDOWS:
            self.assertTrue(w["reason"])
            self.assertGreaterEqual(w["locator"]["char_start"], 12506)
            self.assertLessEqual(w["locator"]["char_end"], 13494)
        # skipped windows must not overlap the newly registered windows
        new_spans = [(q["locator"]["char_start"], q["locator"]["char_end"])
                     for q in yh.YUANHAI_ZHENGGUAN_QUOTES
                     if q["source_section_id"] == "yuanhai.yinshou"]
        legacy_spans = [(w["locator"]["char_start"],
                         w["locator"]["char_end"])
                        for w in yh.YUANHAI_LEGACY_WINDOWS
                        if 12506 <= w["locator"]["char_start"] < 13494]
        for w in yh.YINSHOU_SKIPPED_WINDOWS:
            a, b = w["locator"]["char_start"], w["locator"]["char_end"]
            for c, d in new_spans + legacy_spans:
                self.assertFalse(a < d and c < b,
                                 f"skipped window overlaps quote: {w}")


class GapRegisterTest(unittest.TestCase):
    def test_five_gaps_registered_unresolved(self) -> None:
        gaps = yh.YUANHAI_GAP_REGISTER
        self.assertEqual(len(gaps), 5)
        self.assertEqual([g["position"] for g in gaps],
                         [9873, 9879, 9947, 12518, 12557])
        for g in gaps:
            self.assertEqual(g["status"], "placeholder_unresolved")
            self.assertIsNone(g["reading"])
            self.assertEqual(g["char"], "?")
            self.assertIn("?", g["context"])
        zg = [g for g in gaps
              if g["source_section_id"] == "yuanhai.zhengguan"]
        ys = [g for g in gaps
              if g["source_section_id"] == "yuanhai.yinshou"]
        self.assertEqual(len(zg), 3)
        self.assertEqual(len(ys), 2)

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_SECTIONS}
        zg_text = secs["yuanhai.zhengguan"]["full_text"]
        self.assertEqual(zg_text.count("?"), 3)
        gs_text = secs["yuanhai.guansha_hunza"]["full_text"]
        self.assertEqual(gs_text.count("?"), 0)
        # absolute positions of the ? chars inside the registered full text
        base = secs["yuanhai.zhengguan"]["locator"]["char_start"]
        found = [base + i for i, c in enumerate(zg_text) if c == "?"]
        self.assertEqual(found, [9873, 9879, 9947])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in yh.YUANHAI_ZHENGGUAN_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quotes_carry_their_gaps(self) -> None:
        for cq in yh.YUANHAI_CONTEXT_QUOTES:
            self.assertTrue(cq["not_for_operative_reading"])
            positions = [g["position"] for g in yh.YUANHAI_GAP_REGISTER
                         if cq["locator"]["char_start"]
                         <= g["position"] < cq["locator"]["char_end"]]
            self.assertEqual(sorted(positions),
                             sorted(cq["contains_gap_positions"]),
                             cq["id"])
            for p in cq["contains_gap_positions"]:
                off = p - cq["locator"]["char_start"]
                self.assertEqual(cq["quote"][off], "?")


class RoutingReviewTest(unittest.TestCase):
    def test_every_operative_quote_has_routing_fields(self) -> None:
        for q in yh.YUANHAI_ZHENGGUAN_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                self.assertIsNotNone(q["routed_through_strength"],
                                     q["id"])

    def test_formation_side_all_routed_through_strength(self) -> None:
        by_id = {q["id"]: q for q in yh.YUANHAI_ZHENGGUAN_QUOTES}
        for pid in ("yh.zg_qingzhong", "yh.zg_xi_shenwang",
                    "yh.zg_shenwang_fa", "yh.zg_duo", "yh.zg_zhonghe"):
            self.assertTrue(by_id[pid]["operative"], pid)
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
        legacy = {w["id"]: w for w in yh.YUANHAI_LEGACY_WINDOWS}
        self.assertTrue(
            legacy["yh.legacy_s056"]["routed_through_strength"])

    def test_breaking_side_routed_through_fact_layers_not_strength(
            self) -> None:
        by_id = {q["id"]: q for q in yh.YUANHAI_ZHENGGUAN_QUOTES}
        for pid in ("yh.zg_taboo_xingchong", "yh.zg_jia_mixed",
                    "yh.gs_example_zhifu"):
            self.assertTrue(by_id[pid]["operative"], pid)
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)

    def test_routing_review_records_conclusion_and_refinement(
            self) -> None:
        review = yh.OPERATIVE_ROUTING_REVIEW
        self.assertIn("身旺", review["conclusion_consistent_with_readiness"])
        self.assertIn("不精确", review["refinement_disclosed"])
        self.assertIn("三刑", review["refinement_disclosed"])
        self.assertIn("None", review["determination_consequence"])


class LegacyWindowsTest(unittest.TestCase):
    def test_five_legacy_windows_present(self) -> None:
        legacy = {w["source_section_id"]: w
                  for w in yh.YUANHAI_LEGACY_WINDOWS}
        self.assertEqual(set(legacy),
                         {f"bazi.section.s{n}" for n in
                          ("055", "056", "057", "058", "059")})
        expected = {"bazi.section.s055": (10124, 10147),
                    "bazi.section.s056": (10149, 10224),
                    "bazi.section.s057": (12841, 12897),
                    "bazi.section.s058": (13012, 13031),
                    "bazi.section.s059": (12746, 12806)}
        for sid, (a, b) in expected.items():
            w = legacy[sid]
            self.assertEqual(w["locator"],
                             {"char_start": a, "char_end": b}, sid)
            self.assertEqual(b - a, len(w["quote"]), sid)
            self.assertTrue(w["pre_existing"], sid)

    def test_legacy_windows_inside_new_sections(self) -> None:
        # s055/s056 windows fall inside the fully registered 正官论;
        # their text must appear verbatim in the registered full text.
        secs = {s["section_id"]: s for s in yh.YUANHAI_SECTIONS}
        zg_text = secs["yuanhai.zhengguan"]["full_text"]
        base = secs["yuanhai.zhengguan"]["locator"]["char_start"]
        for w in yh.YUANHAI_LEGACY_WINDOWS:
            a = w["locator"]["char_start"]
            if base <= a < base + len(zg_text):
                off = a - base
                self.assertEqual(
                    zg_text[off:off + len(w["quote"])], w["quote"],
                    w["id"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_semantics_anywhere(self) -> None:
        data = [yh.YUANHAI_SECTIONS, yh.YUANHAI_ZHENGGUAN_QUOTES,
                yh.YUANHAI_CONTEXT_QUOTES, yh.YUANHAI_GAP_REGISTER,
                yh.YUANHAI_GLYPH_NOTES, yh.YUANHAI_LEGACY_WINDOWS,
                yh.YINSHOU_SKIPPED_WINDOWS]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定",
                      yh.YUANHAI_ZHENGGUAN_NOTES[0])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(yh.YUANHAI_GLYPH_NOTES), 4)
        for note in yh.YUANHAI_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (yh.YUANHAI_ZHENGGUAN_QUOTES
                  + yh.YUANHAI_CONTEXT_QUOTES
                  + yh.YUANHAI_LEGACY_WINDOWS):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
