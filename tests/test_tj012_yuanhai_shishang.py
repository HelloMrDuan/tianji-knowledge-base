"""TJ-012.3 Slice D 前置（渊海逐节登记·第五组）的公开结构测试：食伤组两节登记。

本模块（``bazi_yuanhai_shishang``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（两节整节登记形制、缺字逐处落账且
引文窗避缺字、含缺字段只以 context 形登记、转手复核逐句在案、
引用关系只引用不重复登记、未登记相关节逐项有理由、禁止
determination 语义键、禁止健康/寿命/六亲/财富预测口径字段），
不验证任何食神格/伤官格判定（不存在此种代码路径）。引文逐字
等值、覆盖扫描与快照复核在密封专项
``tests/test_tj012_yuanhai_shishang_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_shishang as ss

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_shishang.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
    "health_prediction", "health_verdict", "lifespan_prediction",
    "longevity_verdict", "fortune_score", "wealth_prediction",
    "kinship_prediction",
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
        self.assertEqual(ss.YUANHAI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(ss.YUANHAI_SHISHANG_SECTIONS,
                         GOLDEN["sections"])
        self.assertEqual(ss.YUANHAI_SHISHANG_QUOTES, GOLDEN["quotes"])
        self.assertEqual(ss.YUANHAI_SHISHANG_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(ss.YUANHAI_SHISHANG_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(ss.YUANHAI_SHISHANG_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(ss.YUANHAI_SHISHANG_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(ss.YUANHAI_SHISHANG_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(ss.YUANHAI_SHISHANG_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(ss.YUANHAI_SHISHANG_NOTES, GOLDEN["notes"])
        self.assertEqual(ss.YUANHAI_SHISHANG_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(ss, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(ss, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_two_sections_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in ss.YUANHAI_SHISHANG_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.shangguan",
                                     "yuanhai.shishen"})
        sw = secs["yuanhai.shangguan"]
        self.assertEqual(sw["registration_mode"], "full_section")
        self.assertEqual(sw["locator"], {"char_start": 6086,
                                         "char_end": 6932})
        self.assertEqual(len(sw["full_text"]), 846)
        self.assertTrue(sw["full_text"].startswith("《论 伤 官》"))
        sg = secs["yuanhai.shishen"]
        self.assertEqual(sg["registration_mode"], "full_section")
        self.assertEqual(sg["locator"], {"char_start": 7622,
                                         "char_end": 7948})
        self.assertEqual(len(sg["full_text"]), 326)
        self.assertTrue(sg["full_text"].startswith("《论 食 神》"))

    def test_all_quotes_inside_their_sections(self) -> None:
        spans = {"yuanhai.shangguan": (6086, 6932),
                 "yuanhai.shishen": (7622, 7948)}
        for q in (ss.YUANHAI_SHISHANG_QUOTES
                  + ss.YUANHAI_SHISHANG_CONTEXT_QUOTES):
            a, b = spans[q["source_section_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"], a, q["id"])
            self.assertLessEqual(q["locator"]["char_end"], b, q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_counts_per_section(self) -> None:
        sw = [q for q in ss.YUANHAI_SHISHANG_QUOTES
              if q["source_section_id"] == "yuanhai.shangguan"]
        sg = [q for q in ss.YUANHAI_SHISHANG_QUOTES
              if q["source_section_id"] == "yuanhai.shishen"]
        self.assertEqual(len(sw), 29)
        self.assertEqual(len(sg), 8)


class GapRegisterTest(unittest.TestCase):
    def test_one_gap_new_unresolved(self) -> None:
        gaps = ss.YUANHAI_SHISHANG_GAP_REGISTER
        self.assertEqual(len(gaps), 1)
        g = gaps[0]
        self.assertEqual(g["id"], "ss-gap-01")
        self.assertEqual(g["position"], 7667)
        self.assertEqual(g["status"], "placeholder_unresolved")
        self.assertIsNone(g["reading"])
        self.assertEqual(g["char"], "?")
        self.assertIn("?", g["context"])
        self.assertEqual(g["source_section_id"], "yuanhai.shishen")

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in ss.YUANHAI_SHISHANG_SECTIONS}
        found = {}
        for sid, s in secs.items():
            base = s["locator"]["char_start"]
            found[sid] = [base + i for i, c in enumerate(s["full_text"])
                          if c == "?"]
        self.assertEqual(found["yuanhai.shangguan"], [])
        self.assertEqual(found["yuanhai.shishen"], [7667])
        registered = sorted(g["position"]
                            for g in ss.YUANHAI_SHISHANG_GAP_REGISTER)
        self.assertEqual(registered, [7667])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in ss.YUANHAI_SHISHANG_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quote_carries_the_gap(self) -> None:
        self.assertEqual(len(ss.YUANHAI_SHISHANG_CONTEXT_QUOTES), 1)
        cq = ss.YUANHAI_SHISHANG_CONTEXT_QUOTES[0]
        self.assertTrue(cq["not_for_operative_reading"])
        self.assertEqual(cq["contains_gap_positions"], [7667])
        off = 7667 - cq["locator"]["char_start"]
        self.assertEqual(cq["quote"][off], "?")


class RoutingReviewTest(unittest.TestCase):
    def test_every_operative_quote_has_routing_fields(self) -> None:
        for q in ss.YUANHAI_SHISHANG_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in ss.YUANHAI_SHISHANG_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 19)
        by_id = {q["id"]: q for q in ss.YUANHAI_SHISHANG_QUOTES}
        # strength-marked exemplars （身旺/身弱明文条件）
        for pid in ("yh.sw_month_command_noble",
                    "yh.sw_seal_exhausted_weak",
                    "yh.sw_jia_officer_rule",
                    "yh.ss_body_strong_seal_taboo"):
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)
        # degree / effect / counting gate exemplars
        for pid in ("yh.sw_exhaust_core", "yh.sw_pattern_no_officer",
                    "yh.ss_taboo_wealth_growth", "yh.ss_single_position"):
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)

    def test_routing_review_records_conclusion(self) -> None:
        review = ss.YUANHAI_SHISHANG_ROUTING_REVIEW
        self.assertIn("伤尽", review["conclusion_consistent_with_readiness"])
        self.assertIn("伤官见官",
                      review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("正官", review["comparison_with_prior_groups"])
        self.assertIn("七杀", review["comparison_with_prior_groups"])
        self.assertIn("财组", review["comparison_with_prior_groups"])
        self.assertIn("印组", review["comparison_with_prior_groups"])
        # special discipline: efficacy claims are not endorsements,
        # and no kinship/health/lifespan framing is produced
        self.assertIn("其验如神", review["non_operative_excluded"])
        self.assertIn("背书", review["non_operative_excluded"])
        self.assertIn("六亲", review["non_operative_excluded"])


class CrossReferenceTest(unittest.TestCase):
    def test_seven_cross_references_reference_only(self) -> None:
        refs = ss.YUANHAI_SHISHANG_CROSS_REFERENCES
        self.assertEqual(len(refs), 7)
        targets = {(r["target_module"], r["target_quote_id"])
                   for r in refs}
        self.assertEqual(targets, {
            ("bazi_yuanhai_zhengguan", "yh.zg_luck_shangguan"),
            ("bazi_yuanhai_zhengguan", "yh.zg_luck_observation"),
            ("bazi_yuanhai_zhengguan", "yh.zg_shenwang_fa"),
            ("bazi_yuanhai_cai", "yh.zc_shangguan_jiancai"),
            ("bazi_yuanhai_yin", "yh.yn_jia_seal_taboo"),
            ("bazi_yuanhai_yin", "yh.ds_taboo"),
            ("bazi_yuanhai_yin", "yh.ds_mechanism")})
        for r in refs:
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = ss.YUANHAI_SHISHANG_UNREGISTERED_RELATED
        self.assertEqual(len(items), 3)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {"伤官节后诗诀七首", "伤官说",
                                  "食神节后诗诀六首"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_prediction_semantics(self) -> None:
        data = [ss.YUANHAI_SHISHANG_SECTIONS, ss.YUANHAI_SHISHANG_QUOTES,
                ss.YUANHAI_SHISHANG_CONTEXT_QUOTES,
                ss.YUANHAI_SHISHANG_GAP_REGISTER,
                ss.YUANHAI_SHISHANG_GLYPH_NOTES,
                ss.YUANHAI_SHISHANG_CROSS_REFERENCES,
                ss.YUANHAI_SHISHANG_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", ss.YUANHAI_SHISHANG_NOTES[0])
        # R7 health/lifespan/kinship/wealth ban is registered
        self.assertTrue(any(n.startswith("R7 健康/寿命/六亲/财富禁区")
                            for n in ss.YUANHAI_SHISHANG_NOTES))
        self.assertIn("不得用于健康、寿命",
                      ss.YUANHAI_SHISHANG_LIMITATIONS[-1])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(ss.YUANHAI_SHISHANG_GLYPH_NOTES), 2)
        for note in ss.YUANHAI_SHISHANG_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])
            self.assertEqual(note["status"], "semantic_doubt_preserved")

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (ss.YUANHAI_SHISHANG_QUOTES
                  + ss.YUANHAI_SHISHANG_CONTEXT_QUOTES):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
