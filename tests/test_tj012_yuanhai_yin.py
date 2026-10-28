"""TJ-012.3 Slice D 前置（渊海逐节登记·第四组）的公开结构测试：印组两节登记。

本模块（``bazi_yuanhai_yin``）是纯数据证据登记、零计算逻辑；
本测试只钉登记结构与红线（两节整节登记形制、《论印綬》补全
纪律——正官组 7 窗与 s057–s059 只登记引用关系、未登记 12 段
补登在案、缺字沿正官组登记按节归属、引文窗避缺字、转手复核
逐句在案、未登记相关节逐项有理由、禁止 determination 语义
键、禁止健康/寿命预测口径字段），不验证任何印格判定（不存
在此种代码路径）。引文逐字等值、覆盖扫描与快照复核在密封
专项 ``tests/test_tj012_yuanhai_yin_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_yin as yh

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_yuanhai_yin.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "pattern_established", "verdict",
    "useful_god", "success_failure", "purity",
    "真格", "假格", "成格", "破格", "清浊", "用神",
    "health_prediction", "health_verdict", "lifespan_prediction",
    "longevity_verdict", "fortune_score",
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
        self.assertEqual(yh.YUANHAI_YIN_SECTIONS, GOLDEN["sections"])
        self.assertEqual(yh.YUANHAI_YIN_QUOTES, GOLDEN["quotes"])
        self.assertEqual(yh.YUANHAI_YIN_CONTEXT_QUOTES,
                         GOLDEN["context_quotes"])
        self.assertEqual(yh.YUANHAI_YIN_GAP_REGISTER,
                         GOLDEN["gap_register"])
        self.assertEqual(yh.YUANHAI_YIN_GLYPH_NOTES,
                         GOLDEN["glyph_notes"])
        self.assertEqual(yh.YUANHAI_YIN_CROSS_REFERENCES,
                         GOLDEN["cross_references"])
        self.assertEqual(yh.YUANHAI_YIN_UNREGISTERED_RELATED,
                         GOLDEN["unregistered_related"])
        self.assertEqual(yh.YUANHAI_YIN_ROUTING_REVIEW,
                         GOLDEN["routing_review"])
        self.assertEqual(yh.YUANHAI_YIN_NOTES, GOLDEN["notes"])
        self.assertEqual(yh.YUANHAI_YIN_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(yh, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(yh, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class SectionRegistrationTest(unittest.TestCase):
    def test_two_sections_registered_full(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_YIN_SECTIONS}
        self.assertEqual(set(secs), {"yuanhai.yinshou",
                                     "yuanhai.daoshi"})
        ys = secs["yuanhai.yinshou"]
        self.assertEqual(ys["registration_mode"], "full_section")
        self.assertEqual(ys["locator"], {"char_start": 12506,
                                         "char_end": 13494})
        self.assertEqual(len(ys["full_text"]), 988)
        # snapshot header of yinshou lacks the opening 《
        self.assertTrue(ys["full_text"].startswith("论 印 綬》"))
        ds = secs["yuanhai.daoshi"]
        self.assertEqual(ds["registration_mode"], "full_section")
        self.assertEqual(ds["locator"], {"char_start": 14119,
                                         "char_end": 14566})
        self.assertEqual(len(ds["full_text"]), 447)
        self.assertTrue(ds["full_text"].startswith("《论 倒 食》"))

    def test_all_quotes_inside_their_sections(self) -> None:
        spans = {"yuanhai.yinshou": (12506, 13494),
                 "yuanhai.daoshi": (14119, 14566)}
        for q in (yh.YUANHAI_YIN_QUOTES
                  + yh.YUANHAI_YIN_CONTEXT_QUOTES):
            a, b = spans[q["source_section_id"]]
            self.assertGreaterEqual(q["locator"]["char_start"], a, q["id"])
            self.assertLessEqual(q["locator"]["char_end"], b, q["id"])
            self.assertEqual(
                q["locator"]["char_end"] - q["locator"]["char_start"],
                len(q["quote"]), q["id"])

    def test_quote_counts_per_section(self) -> None:
        ys = [q for q in yh.YUANHAI_YIN_QUOTES
              if q["source_section_id"] == "yuanhai.yinshou"]
        ds = [q for q in yh.YUANHAI_YIN_QUOTES
              if q["source_section_id"] == "yuanhai.daoshi"]
        self.assertEqual(len(ys), 16)
        self.assertEqual(len(ds), 8)

    def test_twelve_skipped_segments_now_registered(self) -> None:
        # every quote carried over from a zhengguan-skipped segment
        # names its skipped-list ordinal in its note
        carried = [q for q in yh.YUANHAI_YIN_QUOTES
                   if "跳过清单第" in q["note"]]
        ordinals = set()
        for q in carried:
            for n in range(1, 13):
                if f"跳过清单第 {n} 段" in q["note"]:
                    ordinals.add(n)
        self.assertEqual(ordinals, set(range(1, 13)))


class GapRegisterTest(unittest.TestCase):
    def test_two_gaps_pre_existing_unresolved(self) -> None:
        gaps = yh.YUANHAI_YIN_GAP_REGISTER
        self.assertEqual(len(gaps), 2)
        self.assertEqual([g["id"] for g in gaps],
                         ["yh-gap-04", "yh-gap-05"])
        self.assertEqual([g["position"] for g in gaps], [12518, 12557])
        for g in gaps:
            self.assertEqual(g["status"], "placeholder_unresolved")
            self.assertIsNone(g["reading"])
            self.assertEqual(g["char"], "?")
            self.assertIn("?", g["context"])
            # registered by the zhengguan batch; this batch only
            # re-files them under their section, content unchanged
            self.assertTrue(g["pre_existing"])
            self.assertEqual(g["registered_in"],
                             "bazi_yuanhai_zhengguan")

    def test_gap_counts_match_full_texts(self) -> None:
        secs = {s["section_id"]: s for s in yh.YUANHAI_YIN_SECTIONS}
        found = {}
        for sid, s in secs.items():
            base = s["locator"]["char_start"]
            found[sid] = [base + i for i, c in enumerate(s["full_text"])
                          if c == "?"]
        self.assertEqual(found["yuanhai.yinshou"], [12518, 12557])
        self.assertEqual(found["yuanhai.daoshi"], [])
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_YIN_GAP_REGISTER)
        self.assertEqual(registered, [12518, 12557])

    def test_no_quote_window_contains_gap_char(self) -> None:
        for q in yh.YUANHAI_YIN_QUOTES:
            self.assertNotIn("?", q["quote"], q["id"])
            self.assertNotIn("？", q["quote"], q["id"])

    def test_context_quotes_carry_their_gaps(self) -> None:
        self.assertEqual(len(yh.YUANHAI_YIN_CONTEXT_QUOTES), 2)
        for cq in yh.YUANHAI_YIN_CONTEXT_QUOTES:
            self.assertTrue(cq["not_for_operative_reading"])
            positions = [g["position"]
                         for g in yh.YUANHAI_YIN_GAP_REGISTER
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
        for q in yh.YUANHAI_YIN_QUOTES:
            self.assertIn("operative", q)
            self.assertIn("routed_through_strength", q)
            if q["operative"]:
                routed = (q["routed_through_strength"]
                          or q.get("routed_through_other"))
                self.assertTrue(routed, q["id"])

    def test_operative_count_and_gates(self) -> None:
        ops = [q for q in yh.YUANHAI_YIN_QUOTES if q["operative"]]
        self.assertEqual(len(ops), 9)
        by_id = {q["id"]: q for q in yh.YUANHAI_YIN_QUOTES}
        # strength-marked exemplars （财旺强度判断， along s057)
        for pid in ("yh.yn_wealth_floods",
                    "yh.yn_wealth_arrives_floods"):
            self.assertTrue(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)
        # effect / stage / counting gate exemplars
        for pid in ("yh.yn_more_is_upper", "yh.yn_jia_seal_taboo",
                    "yh.yn_month_hour_position", "yh.ds_taboo",
                    "yh.ds_mechanism", "yh.ds_killing_control"):
            self.assertFalse(by_id[pid]["routed_through_strength"], pid)
            self.assertTrue(by_id[pid].get("routed_through_other"), pid)

    def test_routing_review_records_conclusion(self) -> None:
        review = yh.YUANHAI_YIN_ROUTING_REVIEW
        self.assertIn("财破印", review["conclusion_consistent_with_readiness"])
        self.assertIn("夺食", review["conclusion_consistent_with_readiness"])
        self.assertIn("制杀", review["conclusion_consistent_with_readiness"])
        self.assertIn("None", review["determination_consequence"])
        self.assertIn("正官", review["comparison_with_prior_groups"])
        self.assertIn("七杀", review["comparison_with_prior_groups"])
        self.assertIn("财组", review["comparison_with_prior_groups"])
        # special discipline: no health/lifespan-prediction framing
        self.assertIn("健康", review["non_operative_excluded"])
        self.assertIn("寿命", review["non_operative_excluded"])


class CrossReferenceTest(unittest.TestCase):
    def test_ten_cross_references_reference_only(self) -> None:
        refs = yh.YUANHAI_YIN_CROSS_REFERENCES
        self.assertEqual(len(refs), 10)
        targets = {(r["target_module"], r["target_quote_id"])
                   for r in refs}
        self.assertEqual(targets, {
            ("bazi_yuanhai_zhengguan", "yh.ys_jingyue"),
            ("bazi_yuanhai_zhengguan", "yh.ys_guangui_sheng"),
            ("bazi_yuanhai_zhengguan", "yh.ys_guangui_duo_yanzhi"),
            ("bazi_yuanhai_zhengguan", "yh.ys_guanyin_liangquan"),
            ("bazi_yuanhai_zhengguan", "yh.ys_yongguan_buxian"),
            ("bazi_yuanhai_zhengguan", "yh.ys_example_guanyin_1"),
            ("bazi_yuanhai_zhengguan", "yh.ys_example_guanyin_2"),
            ("bazi_yuanhai_zhengguan", "yh.legacy_s057"),
            ("bazi_yuanhai_zhengguan", "yh.legacy_s058"),
            ("bazi_yuanhai_zhengguan", "yh.legacy_s059")})
        for r in refs:
            # reference only: no quote text is re-registered here
            self.assertNotIn("quote", r)
            self.assertTrue(r["relation"])

    def test_unregistered_related_have_reasons(self) -> None:
        items = yh.YUANHAI_YIN_UNREGISTERED_RELATED
        self.assertEqual(len(items), 2)
        titles = {i["title"] for i in items}
        self.assertEqual(titles, {"印綬节后诗诀十六首", "论食神"})
        for i in items:
            self.assertTrue(i["reason"])
            span = (i["locator"]["char_end"]
                    - i["locator"]["char_start"])
            self.assertGreater(span, 0)


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_prediction_semantics(self) -> None:
        data = [yh.YUANHAI_YIN_SECTIONS, yh.YUANHAI_YIN_QUOTES,
                yh.YUANHAI_YIN_CONTEXT_QUOTES,
                yh.YUANHAI_YIN_GAP_REGISTER,
                yh.YUANHAI_YIN_GLYPH_NOTES,
                yh.YUANHAI_YIN_CROSS_REFERENCES,
                yh.YUANHAI_YIN_UNREGISTERED_RELATED]
        for blob in data:
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)
        self.assertIn("登记≠可裁定", yh.YUANHAI_YIN_NOTES[0])
        # R7 health/lifespan ban is registered in the notes
        self.assertTrue(any(n.startswith("R7 健康/寿命禁区")
                            for n in yh.YUANHAI_YIN_NOTES))
        self.assertIn("不得用于健康、寿命",
                      yh.YUANHAI_YIN_LIMITATIONS[-1])

    def test_glyph_notes_all_unresolved_or_preserved(self) -> None:
        self.assertEqual(len(yh.YUANHAI_YIN_GLYPH_NOTES), 5)
        for note in yh.YUANHAI_YIN_GLYPH_NOTES:
            self.assertIsNone(note["mapped_reading"], note["id"])

    def test_all_quote_records_well_formed(self) -> None:
        seen = set()
        for q in (yh.YUANHAI_YIN_QUOTES
                  + yh.YUANHAI_YIN_CONTEXT_QUOTES):
            self.assertNotIn(q["id"], seen)
            seen.add(q["id"])
            self.assertEqual(q["source_id"], "bazi.source.yuanhai")
            loc = q["locator"]
            self.assertEqual(loc["char_end"] - loc["char_start"],
                             len(q["quote"]), q["id"])
            self.assertTrue(q["quote"], q["id"])


if __name__ == "__main__":
    unittest.main()
