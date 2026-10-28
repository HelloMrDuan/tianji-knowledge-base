"""TJ-012.3 Slice D 前置（渊海逐节登记·第二组）的公开结构测试：七杀组两节登记。

本模块（``bazi_yuanhai_qisha``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（两节整节登记形制、缺字登记完整性、
引文窗避缺字、转手复核逐句在案、引用关系不重复登记、未登记
相关节逐项有理由、禁止 determination 语义键），不验证任何
七杀格判定（不存在此种代码路径）。引文逐字等值与快照复核在
密封专项 ``tests/test_tj012_yuanhai_qisha_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_qisha as yh

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_qisha.json").read_text(
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
        self.assertEqual(yh.YUANHAI_QISHA_SECTIONS, GOLDEN["sections"])
        self.assertEqual(yh.YUANHAI_QISHA_QUOTES, GOLDEN["quotes"])
        self.assertEqual(yh.YUANHAI_QISHA_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(yh.YUANHAI_QISHA_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(yh.YUANHAI_QISHA_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(yh.YUANHAI_QISHA_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(yh.YUANHAI_QISHA_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(yh.YUANHAI_QISHA_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(yh.YUANHAI_QISHA_NOTES, GOLDEN["notes"])
        self.assertEqual(yh.YUANHAI_QISHA_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(yh, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(yh, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_two_sections_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_QISHA_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.qisha",
                                     "yuanhai.guangxing_taiguo"})
        qs = secs["yuanhai.qisha"]
        self.assertEqual(qs["registration_mode"], "full_section")
        self.assertEqual(qs["locator"], {"char_start": 11627,
                                         "char_end": 12285})
        self.assertEqual(len(qs["full_text"]), 658)
        self.assertTrue(qs["full_text"].startswith("《论 七 杀》"))
        gt = secs["yuanhai.guangxing_taiguo"]
        self.assertEqual(gt["registration_mode"], "full_section")
        self.assertEqual(gt["locator"], {"char_start": 12285,
                                         "char_end": 12400})
        self.assertEqual(len(gt["full_text"]), 115)
        self.assertTrue(gt["full_text"].startswith("《论 官 星 太 过》"))

    def test_sections_are_adjacent_and_abut_registered_guansha(
            self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_QISHA_SECTIONS}
        self.assertEqual(secs["yuanhai.qisha"]["locator"]["char_end"],
                         secs["yuanhai.guangxing_taiguo"]
                         ["locator"]["char_start"])
        # 官星太过 finally abuts the zhengguan-registered 官杀混杂 at 12400
        self.assertEqual(
            secs["yuanhai.guangxing_taiguo"]["locator"]["char_end"],
            12400)

    def test_all_quotes_inside_their_sections(self) -> None:
        spans = {"yuanhai.qisha": (11627, 12285),
                 "yuanhai.guangxing_taiguo": (12285, 12400)}
        for q in (yh.YUANHAI_QISHA_QUOTES
                  + yh.YUANHAI_QISHA_CONTEXT_QUOTES):
            a, b = spans[q["source_section_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"], a, q["id"])
            self.assertLessEqual(q["locator"]["char_end"], b, q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_counts_per_section(self) -> None:
        qs = [q for q in yh.YUANHAI_QISHA_QUOTES
              if q["source_section_id"] == "yuanhai.qisha"]
        gt = [q for q in yh.YUANHAI_QISHA_QUOTES
              if q["source_section_id"] == "yuanhai.guangxing_taiguo"]
        self.assertEqual(len(qs), 18)
        self.assertEqual(len(gt), 3)


class GapRegisterTest(unittest.TestCase):
    def test_two_gaps_registered_unresolved(self) -> None:
        gaps = yh.YUANHAI_QISHA_GAP_REGISTER
        self.assertEqual(len(gaps), 2)
        self.assertEqual([g["position"] for g in gaps], [11702, 11955])
        for g in gaps:
            self.assertEqual(g["status"], "placeholder_unresolved")
            self.assertIsNone(g["reading"])
            self.assertEqual(g["char"], "?")
            self.assertEqual(g["source_section_id"], "yuanhai.qisha")
            self.assertIn("?", g["context"])

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_QISHA_SECTIONS}
        qs_text = secs["yuanhai.qisha"]["full_text"]
        self.assertEqual(qs_text.count("?"), 2)
        gt_text = secs["yuanhai.guangxing_taiguo"]["full_text"]
        self.assertEqual(gt_text.count("?"), 0)
        base = secs["yuanhai.qisha"]["locator"]["char_start"]
        found = [base + i for i, c in enumerate(qs_text) if c == "?"]
        self.assertEqual(found, [11702, 11955])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in yh.YUANHAI_QISHA_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quotes_carry_their_gaps(self) -> None:
        self.assertEqual(len(yh.YUANHAI_QISHA_CONTEXT_QUOTES), 2)
        for cq in yh.YUANHAI_QISHA_CONTEXT_QUOTES:
            self.assertTrue(cq["not_for_operative_reading"])
            positions = [g["position"]
                         for g in yh.YUANHAI_QISHA_GAP_REGISTER
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
        for q in yh.YUANHAI_QISHA_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in yh.YUANHAI_QISHA_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 12)
        by_id = {q["id"]: q for q in yh.YUANHAI_QISHA_QUOTES}
        # strength gate exemplars
        for pid in ("yh.qs_naming", "yh.qs_hour_killing",
                    "yh.qs_day_killing"):
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
        # control-effect gate exemplars (not strength)
        for pid in ("yh.qs_control_moderation", "yh.qs_control_present",
                    "yh.gt_clear", "yh.gt_hidden"):
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)
        # combination gate exemplar
        self.assertTrue(
            by_id["yh.qs_jia_example_control"].get("routed_through_other"))

    def test_routing_review_records_conclusion(self) -> None:
        review = yh.YUANHAI_QISHA_ROUTING_REVIEW
        self.assertIn("身旺", review["conclusion_consistent_with_readiness"])
        self.assertIn("制伏", review["conclusion_consistent_with_readiness"])
        self.assertIn("合杀", review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("正官", review["comparison_with_zhengguan"])


class CrossReferenceTest(unittest.TestCase):
    def test_four_cross_references_reference_only(self) -> None:
        refs = yh.YUANHAI_QISHA_CROSS_REFERENCES
        self.assertEqual(len(refs), 4)
        targets = {r["target_quote_id"] for r in refs}
        self.assertEqual(targets, {"yh.gs_example_zhifu",
                                   "yh.zg_jia_mixed",
                                   "yh.ys_example_guanyin_2",
                                   "yh.legacy_s055"})
        for r in refs:
            self.assertEqual(r["target_module"],
                             "bazi_yuanhai_zhengguan")
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = yh.YUANHAI_QISHA_UNREGISTERED_RELATED
        self.assertEqual(len(items), 3)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {"弃命从杀论", "论阳刃", "官杀相关诗诀诸首"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)


class DisciplineTest(unittest.TestCase):
    def test_no_determination_semantics_anywhere(self) -> None:
        data = [yh.YUANHAI_QISHA_SECTIONS, yh.YUANHAI_QISHA_QUOTES,
                yh.YUANHAI_QISHA_CONTEXT_QUOTES,
                yh.YUANHAI_QISHA_GAP_REGISTER,
                yh.YUANHAI_QISHA_GLYPH_NOTES,
                yh.YUANHAI_QISHA_CROSS_REFERENCES,
                yh.YUANHAI_QISHA_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", yh.YUANHAI_QISHA_NOTES[0])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(yh.YUANHAI_QISHA_GLYPH_NOTES), 3)
        for note in yh.YUANHAI_QISHA_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (yh.YUANHAI_QISHA_QUOTES
                  + yh.YUANHAI_QISHA_CONTEXT_QUOTES):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
