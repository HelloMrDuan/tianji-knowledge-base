"""TJ-012.3 Slice D 前置（渊海逐节登记·第七组）的公开结构测试：从格组一节登记。

本模块（``bazi_yuanhai_cong``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（一节整节登记形制、节题实测与韵文体
在案、无缺字对账、转手复核逐句在案、滴天髓交叉引用只引用不
重复登记、未登记散见形态逐项有理由、从格未裁定纪律、禁止
determination 语义键、禁止生死/祸福/寿夭/刑伤预测口径字段），
不验证任何从杀格/从财格判定（不存在此种代码路径）。引文逐字
等值、覆盖扫描与快照复核在密封专项
``tests/test_tj012_yuanhai_cong_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cong as cg

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_cong.json").read_text(
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
        self.assertEqual(cg.YUANHAI_SNAPSHOT, GOLDEN["snapshot"])
        self.assertEqual(cg.YUANHAI_CONG_DITIANSUI_SNAPSHOT,
                         GOLDEN["ditiansui_snapshot"])
        self.assertEqual(cg.YUANHAI_CONG_SECTIONS, GOLDEN["sections"])
        self.assertEqual(cg.YUANHAI_CONG_QUOTES, GOLDEN["quotes"])
        self.assertEqual(cg.YUANHAI_CONG_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(cg.YUANHAI_CONG_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(cg.YUANHAI_CONG_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(cg.YUANHAI_CONG_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(cg.YUANHAI_CONG_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(cg.YUANHAI_CONG_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(cg.YUANHAI_CONG_NOTES, GOLDEN["notes"])
        self.assertEqual(cg.YUANHAI_CONG_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(cg, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(cg, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_one_section_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in cg.YUANHAI_CONG_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.qiming_congsha"})
        s = secs["yuanhai.qiming_congsha"]
        self.assertEqual(s["title"], "弃命从杀论")
        self.assertEqual(s["registration_mode"], "full_section")
        self.assertEqual(s["locator"], {"char_start": 54055,
                                        "char_end": 54359})
        self.assertEqual(len(s["full_text"]), 304)
        self.assertTrue(s["full_text"].startswith("《弃 命 从 杀 论》"))
        # verse form and the measured title are on record
        self.assertIn("四言韵文体", s["note"])
        self.assertIn("非《论弃命从杀》", s["note"])
        # the section covers 从财 as well as 从杀 despite its title
        self.assertIn("兼论从财", s["note"])

    def test_all_quotes_inside_the_section(self) -> None:
        for q in cg.YUANHAI_CONG_QUOTES:
            self.assertEqual(q["source_section_id"],
                             "yuanhai.qiming_congsha")
            self.assertGreaterEqual(q["locator"]["char_start"], 54055,
                                    q["id"])
            self.assertLessEqual(q["locator"]["char_end"], 54359,
                                 q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_count(self) -> None:
        self.assertEqual(len(cg.YUANHAI_CONG_QUOTES), 15)


class GapRegisterTest(unittest.TestCase):
    def test_no_gaps_in_section(self) -> None:
        self.assertEqual(cg.YUANHAI_CONG_GAP_REGISTER, [])
        self.assertEqual(cg.YUANHAI_CONG_CONTEXT_QUOTES, [])
        s = cg.YUANHAI_CONG_SECTIONS[0]
        self.assertNotIn("?", s["full_text"])
        for q in cg.YUANHAI_CONG_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])
        # the zero-gap finding itself is on record
        self.assertTrue(any(n.startswith("R2 缺字对账")
                            for n in cg.YUANHAI_CONG_NOTES))


class RoutingReviewTest(unittest.TestCase):
    def test_every_operative_quote_has_routing_fields(self) -> None:
        for q in cg.YUANHAI_CONG_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in cg.YUANHAI_CONG_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 15)
        by_id = {q["id"]: q for q in cg.YUANHAI_CONG_QUOTES}
        # the only explicit-身弱 sentence is strength-marked
        self.assertTrue(
            by_id["yh.cg_wu_ji_hai_month"]["routed_through_strength"])
        # the two general rules route through the assembly gate
        for pid in ("yh.cg_follow_wealth_rule",
                    "yh.cg_follow_killing_rule"):
            other = " ".join(by_id[pid]["routed_through_other"])
            self.assertIn("会局门", other, pid)
        # root-fact gate exemplars
        for pid in ("yh.cg_bing_shen_month",
                    "yh.cg_cross_rules_root_negation"):
            other = " ".join(by_id[pid]["routed_through_other"])
            self.assertIn("无根事实门", other, pid)

    def test_routing_review_records_conclusion(self) -> None:
        review = cg.YUANHAI_CONG_ROUTING_REVIEW
        self.assertIn("无根事实门",
                      review["conclusion_consistent_with_readiness"])
        self.assertIn("旺衰极端档门",
                      review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("三书三层", review["comparison_with_prior_groups"])
        self.assertIn("命殞无猜", review["non_operative_excluded"])


class CrossReferenceTest(unittest.TestCase):
    def test_three_cross_references_reference_only(self) -> None:
        refs = cg.YUANHAI_CONG_CROSS_REFERENCES
        self.assertEqual(len(refs), 3)
        targets = {(r["target_module"], r["target_quote_id"])
                   for r in refs}
        self.assertEqual(targets, {
            ("bazi_fire_morphology", "dt.guli_def"),
            ("bazi_fire_morphology", "dt.congwang_def"),
            ("bazi_fire_morphology", "dt.congqiang_def")})
        layers = {r["target_quote_id"]: r["target_layer"] for r in refs}
        self.assertEqual(layers["dt.guli_def"], "原注")
        self.assertEqual(layers["dt.congwang_def"], "任氏曰")
        self.assertEqual(layers["dt.congqiang_def"], "任氏曰")
        for r in refs:
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertEqual(r["target_source_id"],
                             "bazi.source.ditiansui-spouse")
            self.assertEqual(r["target_snapshot_file"],
                             "ditiansui_chanwei.txt")
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = cg.YUANHAI_CONG_UNREGISTERED_RELATED
        self.assertEqual(len(items), 5)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {
            "《四言独步》末句（弃命从财格）",
            "《挈要捷驰玄妙诀》从格散句群",
            "从化散见诸节（无从化专节）",
            "专旺类散见（无专旺/从旺/从强专节）",
            "《五言独步》（紧邻后节）"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)
        congge = next(i for i in items
                      if i["section_id"] == "yuanhai.conghua_scattered")
        self.assertIn("从革", congge["reason"])
        self.assertIn("P-D2", congge["reason"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_prediction_semantics(self) -> None:
        data = [cg.YUANHAI_CONG_SECTIONS, cg.YUANHAI_CONG_QUOTES,
                cg.YUANHAI_CONG_CONTEXT_QUOTES,
                cg.YUANHAI_CONG_GAP_REGISTER,
                cg.YUANHAI_CONG_GLYPH_NOTES,
                cg.YUANHAI_CONG_CROSS_REFERENCES,
                cg.YUANHAI_CONG_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", cg.YUANHAI_CONG_NOTES[0])
        self.assertTrue(any(n.startswith("R5 散见纪律")
                            for n in cg.YUANHAI_CONG_NOTES))
        self.assertTrue(any(n.startswith("R6 从格未裁定纪律")
                            for n in cg.YUANHAI_CONG_NOTES))
        self.assertTrue(any(n.startswith("R7 生死/祸福禁区")
                            for n in cg.YUANHAI_CONG_NOTES))
        self.assertIn("不得用于生死、祸福、寿夭",
                      cg.YUANHAI_CONG_LIMITATIONS[-1])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(cg.YUANHAI_CONG_GLYPH_NOTES), 2)
        for note in cg.YUANHAI_CONG_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])
            self.assertIn(note["status"],
                          {"semantic_doubt_preserved",
                           "archaic_form_preserved"})
        yun = next(g for g in cg.YUANHAI_CONG_GLYPH_NOTES
                   if g["id"] == "cg-glyph-01")
        self.assertEqual(yun["char"], "殞")
        self.assertEqual(yun["position"], 54352)

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in cg.YUANHAI_CONG_QUOTES:
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
