"""TJ-012.3 Slice D 前置（渊海逐节登记·第六组）的公开结构测试：禄刃组两节登记。

本模块（``bazi_yuanhai_luren``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（两节整节登记形制、阳刃节界订正、
缺字逐处落账且引文窗避缺字、含缺字段只以 context 形登记、
转手复核逐句在案、引用关系只引用不重复登记、未登记相关节
逐项有理由、禄无专节事实在案、禁止 determination 语义键、
禁止祸福/刑伤/生死/境遇预测口径字段），不验证任何阳刃格/
日刃格/禄格判定（不存在此种代码路径）。引文逐字等值、覆盖
扫描与快照复核在密封专项 ``tests/test_tj012_yuanhai_luren_sealed.py``
（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_luren as lr

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_luren.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
    "health_prediction", "health_verdict", "lifespan_prediction",
    "longevity_verdict", "fortune_score", "wealth_prediction",
    "kinship_prediction", "disaster_prediction", "death_prediction",
    "injury_prediction",
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
        self.assertEqual(lr.YUANHAI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(lr.YUANHAI_LUREN_SECTIONS, GOLDEN["sections"])
        self.assertEqual(lr.YUANHAI_LUREN_QUOTES, GOLDEN["quotes"])
        self.assertEqual(lr.YUANHAI_LUREN_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(lr.YUANHAI_LUREN_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(lr.YUANHAI_LUREN_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(lr.YUANHAI_LUREN_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(lr.YUANHAI_LUREN_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(lr.YUANHAI_LUREN_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(lr.YUANHAI_LUREN_NOTES, GOLDEN["notes"])
        self.assertEqual(lr.YUANHAI_LUREN_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(lr, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(lr, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_two_sections_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in lr.YUANHAI_LUREN_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.yangren",
                                     "yuanhai.riren"})
        yr = secs["yuanhai.yangren"]
        self.assertEqual(yr["registration_mode"], "full_section")
        self.assertEqual(yr["locator"], {"char_start": 14796,
                                         "char_end": 15439})
        self.assertEqual(len(yr["full_text"]), 643)
        self.assertTrue(yr["full_text"].startswith("《论 阳 刃》"))
        # boundary correction over the qisha title-scan span is on record
        self.assertIn("15176", yr["note"])
        rr = secs["yuanhai.riren"]
        self.assertEqual(rr["registration_mode"], "full_section")
        self.assertEqual(rr["locator"], {"char_start": 15752,
                                         "char_end": 16116})
        self.assertEqual(len(rr["full_text"]), 364)
        self.assertTrue(rr["full_text"].startswith("《论 日 刃》"))

    def test_all_quotes_inside_their_sections(self) -> None:
        spans = {"yuanhai.yangren": (14796, 15439),
                 "yuanhai.riren": (15752, 16116)}
        for q in (lr.YUANHAI_LUREN_QUOTES
                  + lr.YUANHAI_LUREN_CONTEXT_QUOTES):
            a, b = spans[q["source_section_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"], a, q["id"])
            self.assertLessEqual(q["locator"]["char_end"], b, q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_counts_per_section(self) -> None:
        yr = [q for q in lr.YUANHAI_LUREN_QUOTES
              if q["source_section_id"] == "yuanhai.yangren"]
        rr = [q for q in lr.YUANHAI_LUREN_QUOTES
              if q["source_section_id"] == "yuanhai.riren"]
        self.assertEqual(len(yr), 12)
        self.assertEqual(len(rr), 8)


class GapRegisterTest(unittest.TestCase):
    def test_one_gap_new_unresolved(self) -> None:
        gaps = lr.YUANHAI_LUREN_GAP_REGISTER
        self.assertEqual(len(gaps), 1)
        g = gaps[0]
        self.assertEqual(g["id"], "lr-gap-01")
        self.assertEqual(g["position"], 14875)
        self.assertEqual(g["status"], "placeholder_unresolved")
        self.assertIsNone(g["reading"])
        self.assertEqual(g["char"], "?")
        self.assertIn("?", g["context"])
        self.assertEqual(g["source_section_id"], "yuanhai.yangren")

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in lr.YUANHAI_LUREN_SECTIONS}
        found = {}
        for sid, s in secs.items():
            base = s["locator"]["char_start"]
            found[sid] = [base + i for i, c in enumerate(s["full_text"])
                          if c == "?"]
        self.assertEqual(found["yuanhai.yangren"], [14875])
        self.assertEqual(found["yuanhai.riren"], [])
        registered = sorted(g["position"]
                            for g in lr.YUANHAI_LUREN_GAP_REGISTER)
        self.assertEqual(registered, [14875])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in lr.YUANHAI_LUREN_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quote_carries_the_gap(self) -> None:
        self.assertEqual(len(lr.YUANHAI_LUREN_CONTEXT_QUOTES), 1)
        cq = lr.YUANHAI_LUREN_CONTEXT_QUOTES[0]
        self.assertTrue(cq["not_for_operative_reading"])
        self.assertEqual(cq["contains_gap_positions"], [14875])
        off = 14875 - cq["locator"]["char_start"]
        self.assertEqual(cq["quote"][off], "?")


class RoutingReviewTest(unittest.TestCase):
    def test_every_operative_quote_has_routing_fields(self) -> None:
        for q in lr.YUANHAI_LUREN_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in lr.YUANHAI_LUREN_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 9)
        by_id = {q["id"]: q for q in lr.YUANHAI_LUREN_QUOTES}
        # strength-marked exemplars （身旺/身弱明文条件）
        for pid in ("yh.yr_blade_killing_strength",
                    "yh.yr_no_killing_luck_wealth",
                    "yh.rr_body_strong_remove"):
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)
        # effect / chain / scope gate exemplars
        for pid in ("yh.yr_preferences", "yh.rr_same_method",
                    "yh.rr_avoidance_rules"):
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)

    def test_routing_review_records_conclusion(self) -> None:
        review = lr.YUANHAI_LUREN_ROUTING_REVIEW
        self.assertIn("制刃效力门",
                      review["conclusion_consistent_with_readiness"])
        self.assertIn("禄前一位",
                      review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("七杀组", review["comparison_with_prior_groups"])
        self.assertIn("投水而死", review["non_operative_excluded"])


class CrossReferenceTest(unittest.TestCase):
    def test_eight_cross_references_reference_only(self) -> None:
        refs = lr.YUANHAI_LUREN_CROSS_REFERENCES
        self.assertEqual(len(refs), 8)
        targets = {(r["target_module"], r["target_quote_id"])
                   for r in refs}
        self.assertEqual(targets, {
            ("bazi_yuanhai_qisha", "yh.qs_definition"),
            ("bazi_yuanhai_qisha", "yh.qs_blade_and_wealth"),
            ("bazi_yuanhai_qisha", "yh.qs_day_killing"),
            ("bazi_yuanhai_qisha", "yh.qs_hour_no_fear"),
            ("bazi_yuanhai_zhengguan", "yh.zg_jia_mixed"),
            ("bazi_yuanhai_cai", "yh.jc_definition"),
            ("bazi_yuanhai_cai", "yh.zc_example_4"),
            ("bazi_yuanhai_cai", "yh.pc_classic_quote")})
        for r in refs:
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = lr.YUANHAI_LUREN_UNREGISTERED_RELATED
        self.assertEqual(len(items), 3)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {
            "阳刃日刃诗诀八首",
            "神煞四节（论日贵/论日德/论魁罡/论金神）",
            "禄散见诸节（无《论禄》专节）"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)
        lu = next(i for i in items
                  if i["section_id"] == "yuanhai.lu_scattered")
        self.assertIn("建禄 5 见", lu["reason"])
        self.assertIn("归禄 20 见", lu["reason"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_prediction_semantics(self) -> None:
        data = [lr.YUANHAI_LUREN_SECTIONS, lr.YUANHAI_LUREN_QUOTES,
                lr.YUANHAI_LUREN_CONTEXT_QUOTES,
                lr.YUANHAI_LUREN_GAP_REGISTER,
                lr.YUANHAI_LUREN_GLYPH_NOTES,
                lr.YUANHAI_LUREN_CROSS_REFERENCES,
                lr.YUANHAI_LUREN_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", lr.YUANHAI_LUREN_NOTES[0])
        # R5 boundary correction / R6 no-lu-section / R7 disaster ban
        self.assertTrue(any(n.startswith("R5 节界订正纪律")
                            for n in lr.YUANHAI_LUREN_NOTES))
        self.assertTrue(any(n.startswith("R6 禄无专节纪律")
                            for n in lr.YUANHAI_LUREN_NOTES))
        self.assertTrue(any(n.startswith("R7 祸福/刑伤/生死禁区")
                            for n in lr.YUANHAI_LUREN_NOTES))
        self.assertIn("不得用于祸福、刑伤、生死",
                      lr.YUANHAI_LUREN_LIMITATIONS[-1])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(lr.YUANHAI_LUREN_GLYPH_NOTES), 3)
        for note in lr.YUANHAI_LUREN_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])
            self.assertIn(note["status"],
                          {"semantic_doubt_preserved",
                           "example_placeholder_preserved"})
        xx = next(g for g in lr.YUANHAI_LUREN_GLYPH_NOTES
                  if g["id"] == "lr-glyph-01")
        self.assertEqual(xx["char"], "X")
        self.assertEqual(xx["status"], "example_placeholder_preserved")

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (lr.YUANHAI_LUREN_QUOTES
                  + lr.YUANHAI_LUREN_CONTEXT_QUOTES):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
