"""TJ-012.3 Slice D 前置（渊海逐节登记·第三组）的公开结构测试：财组三节登记。

本模块（``bazi_yuanhai_cai``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（三节整节登记形制、缺字登记完整性、
引文窗避缺字、转手复核逐句在案、引用关系不重复登记、未登记
相关节逐项有理由、禁止 determination 语义键、禁止财富预测
口径字段），不验证任何财格判定（不存在此种代码路径）。引文
逐字等值与快照复核在密封专项
``tests/test_tj012_yuanhai_cai_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cai as yh

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_cai.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
    "wealth_prediction", "wealth_verdict", "income_prediction",
    "fortune_score", "rich_or_poor",
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
        self.assertEqual(yh.YUANHAI_CAI_SECTIONS, GOLDEN["sections"])
        self.assertEqual(yh.YUANHAI_CAI_QUOTES, GOLDEN["quotes"])
        self.assertEqual(yh.YUANHAI_CAI_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(yh.YUANHAI_CAI_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(yh.YUANHAI_CAI_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(yh.YUANHAI_CAI_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(yh.YUANHAI_CAI_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(yh.YUANHAI_CAI_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(yh.YUANHAI_CAI_NOTES, GOLDEN["notes"])
        self.assertEqual(yh.YUANHAI_CAI_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(yh, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(yh, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_three_sections_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_CAI_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.zhengcai",
                                     "yuanhai.piancai",
                                     "yuanhai.jiecai"})
        zc = secs["yuanhai.zhengcai"]
        self.assertEqual(zc["registration_mode"], "full_section")
        self.assertEqual(zc["locator"], {"char_start": 8183,
                                         "char_end": 9330})
        self.assertEqual(len(zc["full_text"]), 1147)
        self.assertTrue(zc["full_text"].startswith("《论 正 财》"))
        pc = secs["yuanhai.piancai"]
        self.assertEqual(pc["registration_mode"], "full_section")
        self.assertEqual(pc["locator"], {"char_start": 9330,
                                         "char_end": 9703})
        self.assertEqual(len(pc["full_text"]), 373)
        # snapshot header of the piancai part lacks the opening 《
        self.assertTrue(pc["full_text"].startswith("论 偏 财》"))
        jc = secs["yuanhai.jiecai"]
        self.assertEqual(jc["registration_mode"], "full_section")
        self.assertEqual(jc["locator"], {"char_start": 14566,
                                         "char_end": 14796})
        self.assertEqual(len(jc["full_text"]), 230)
        self.assertTrue(jc["full_text"].startswith("《论 劫 财》"))

    def test_sections_adjacency(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_CAI_SECTIONS}
        self.assertEqual(secs["yuanhai.zhengcai"]["locator"]["char_end"],
                         secs["yuanhai.piancai"]
                         ["locator"]["char_start"])
        # piancai finally abuts the zhengguan-registered 正官论 at 9703
        self.assertEqual(
            secs["yuanhai.piancai"]["locator"]["char_end"], 9703)

    def test_all_quotes_inside_their_sections(self) -> None:
        spans = {"yuanhai.zhengcai": (8183, 9330),
                 "yuanhai.piancai": (9330, 9703),
                 "yuanhai.jiecai": (14566, 14796)}
        for q in (yh.YUANHAI_CAI_QUOTES
                  + yh.YUANHAI_CAI_CONTEXT_QUOTES):
            a, b = spans[q["source_section_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"], a, q["id"])
            self.assertLessEqual(q["locator"]["char_end"], b, q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_counts_per_section(self) -> None:
        zc = [q for q in yh.YUANHAI_CAI_QUOTES
              if q["source_section_id"] == "yuanhai.zhengcai"]
        pc = [q for q in yh.YUANHAI_CAI_QUOTES
              if q["source_section_id"] == "yuanhai.piancai"]
        jc = [q for q in yh.YUANHAI_CAI_QUOTES
              if q["source_section_id"] == "yuanhai.jiecai"]
        self.assertEqual(len(zc), 25)
        self.assertEqual(len(pc), 12)
        self.assertEqual(len(jc), 9)


class GapRegisterTest(unittest.TestCase):
    def test_three_gaps_registered_unresolved(self) -> None:
        gaps = yh.YUANHAI_CAI_GAP_REGISTER
        self.assertEqual(len(gaps), 3)
        self.assertEqual([g["position"] for g in gaps],
                         [8197, 9344, 9522])
        for g in gaps:
            self.assertEqual(g["status"], "placeholder_unresolved")
            self.assertIsNone(g["reading"])
            self.assertEqual(g["char"], "?")
            self.assertIn("?", g["context"])

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_CAI_SECTIONS}
        found = {}
        for sid, s in secs.items():
            base = s["locator"]["char_start"]
            found[sid] = [base + i for i, c in enumerate(s["full_text"])
                          if c == "?"]
        self.assertEqual(found["yuanhai.zhengcai"], [8197])
        self.assertEqual(found["yuanhai.piancai"], [9344, 9522])
        self.assertEqual(found["yuanhai.jiecai"], [])
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_CAI_GAP_REGISTER)
        self.assertEqual(registered, [8197, 9344, 9522])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in yh.YUANHAI_CAI_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quotes_carry_their_gaps(self) -> None:
        self.assertEqual(len(yh.YUANHAI_CAI_CONTEXT_QUOTES), 3)
        for cq in yh.YUANHAI_CAI_CONTEXT_QUOTES:
            self.assertTrue(cq["not_for_operative_reading"])
            positions = [g["position"]
                         for g in yh.YUANHAI_CAI_GAP_REGISTER
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
        for q in yh.YUANHAI_CAI_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in yh.YUANHAI_CAI_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 26)
        by_id = {q["id"]: q for q in yh.YUANHAI_CAI_QUOTES}
        # strength gate exemplars
        for pid in ("yh.zc_enjoyment_condition", "yh.zc_preferences",
                    "yh.zc_wealth_generates_officer",
                    "yh.pc_balance_officer_luck",
                    "yh.pc_strong_weak_officer_luck"):
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
        # non-strength gate exemplars （得时得地/空亡三合/比劫争夺）
        for pid in ("yh.zc_timely", "yh.zc_noble_pattern",
                    "yh.pc_exposure", "yh.jc_seizure_mechanism"):
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)

    def test_routing_review_records_conclusion(self) -> None:
        review = yh.YUANHAI_CAI_ROUTING_REVIEW
        self.assertIn("身旺", review["conclusion_consistent_with_readiness"])
        self.assertIn("比劫争夺", review["conclusion_consistent_with_readiness"])
        self.assertIn("官星", review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("正官", review["comparison_with_prior_groups"])
        self.assertIn("七杀", review["comparison_with_prior_groups"])
        # special discipline: no wealth-prediction framing anywhere
        self.assertIn("财富预测", review["non_operative_excluded"])


class CrossReferenceTest(unittest.TestCase):
    def test_five_cross_references_reference_only(self) -> None:
        refs = yh.YUANHAI_CAI_CROSS_REFERENCES
        self.assertEqual(len(refs), 5)
        targets = {(r["target_module"], r["target_quote_id"])
                   for r in refs}
        self.assertEqual(targets, {
            ("bazi_yuanhai_qisha", "yh.qs_definition"),
            ("bazi_yuanhai_qisha", "yh.qs_blade_and_wealth"),
            ("bazi_yuanhai_zhengguan", "yh.ys_guangui_sheng"),
            ("bazi_yuanhai_zhengguan", "yh.ys_yongguan_buxian"),
            ("bazi_yuanhai_zhengguan", "yh.zg_luck_observation")})
        for r in refs:
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = yh.YUANHAI_CAI_UNREGISTERED_RELATED
        self.assertEqual(len(items), 3)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {"论倒食", "论食神", "财组相邻诗诀诸首"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_wealth_prediction_semantics(
            self) -> None:
        data = [yh.YUANHAI_CAI_SECTIONS, yh.YUANHAI_CAI_QUOTES,
                yh.YUANHAI_CAI_CONTEXT_QUOTES,
                yh.YUANHAI_CAI_GAP_REGISTER,
                yh.YUANHAI_CAI_GLYPH_NOTES,
                yh.YUANHAI_CAI_CROSS_REFERENCES,
                yh.YUANHAI_CAI_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", yh.YUANHAI_CAI_NOTES[0])
        # R7 wealth-prediction ban is registered in the notes
        self.assertTrue(any(n.startswith("R7 财富预测禁区")
                            for n in yh.YUANHAI_CAI_NOTES))
        self.assertIn("不得用于财富预测", yh.YUANHAI_CAI_LIMITATIONS[-1])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(yh.YUANHAI_CAI_GLYPH_NOTES), 4)
        for note in yh.YUANHAI_CAI_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (yh.YUANHAI_CAI_QUOTES
                  + yh.YUANHAI_CAI_CONTEXT_QUOTES):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
