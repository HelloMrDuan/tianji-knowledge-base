"""Fixed research candidate cases; not promoted Phase2 Dayun Golden evidence."""
import unittest

from tianji_kb.bazi_dayun_sequence import candidate_sequence
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

NATAL = ("庚辰", "己丑", "甲子", "庚午")
NATAL_INPUT = dict(zip(
    ("year_ganzhi", "month_ganzhi", "day_ganzhi", "hour_ganzhi"), NATAL))


class DayunSequenceResearchTests(unittest.TestCase):
    def test_forward_fixed_candidates_with_ten_gods(self):
        out = chart(*NATAL, dayun_sequence_direction="forward", dayun_sequence_count=3)
        result = out["result"]["dayun_sequence_research"]
        self.assertEqual(result["source_month_ganzhi"], "己丑")
        self.assertEqual(result["natal_day_master"], "甲")
        self.assertEqual([
            (r["period_index"], r["candidate_ganzhi"], r["ten_god_relative_to_natal_day_stem"])
            for r in result["rows"]
        ], [
            (1, "庚寅", "七杀"),
            (2, "辛卯", "正官"),
            (3, "壬辰", "偏印"),
        ])
        self.assertEqual(result["source_fact_ref"], "#/trace/0/output/ganzhi/1")
        self.assertEqual(out["trace"][0]["output"]["ganzhi"][1], "己丑")
        self.assertTrue(out["trace"][0]["evidence_ids"])
        self.assertFalse(result["classical_evidence_for_dayun_sequence_approved"])
        self.assertEqual(result["dayun_sequence_policy_review_status"], "unreviewed")
        self.assertTrue(out["research_only"])
        self.assertFalse(out["interpretation_contract"]["ai_may_explain"])

    def test_backward_fixed_candidates_and_wraparound(self):
        backward = chart(*NATAL, dayun_sequence_direction="backward", dayun_sequence_count=3)
        self.assertEqual([
            (r["candidate_ganzhi"], r["ten_god_relative_to_natal_day_stem"])
            for r in backward["result"]["dayun_sequence_research"]["rows"]
        ], [("戊子", "偏财"), ("丁亥", "伤官"), ("丙戌", "食神")])
        forward_wrap = candidate_sequence("癸亥", "甲", direction="forward", periods=2)
        backward_wrap = candidate_sequence("甲子", "甲", direction="backward", periods=2)
        self.assertEqual([r["candidate_ganzhi"] for r in forward_wrap["rows"]], ["甲子", "乙丑"])
        self.assertEqual([r["candidate_ganzhi"] for r in backward_wrap["rows"]], ["癸亥", "壬戌"])

    def test_undated_research_rows_do_not_predict_anything(self):
        out = execute("bazi", {**NATAL_INPUT, "dayun_sequence_direction": "forward"},
                      allow_research=True)
        research = out["result"]["dayun_sequence_research"]
        self.assertEqual(len(research["rows"]), 8)
        self.assertFalse(research["start_age_calculated"])
        self.assertFalse(research["handover_dates_calculated"])
        self.assertFalse(research["direction_from_natal_attributes_calculated"])
        self.assertFalse(research["jie_boundary_method_adjudicated"])
        self.assertFalse(research["start_age_conversion_adjudicated"])
        self.assertFalse(research["public_enabled"])
        self.assertFalse(research["ai_enabled"])
        for row in research["rows"]:
            for key in ("start_date", "end_date", "start_age", "end_age",
                        "natal_interaction", "luck_assessment"):
                self.assertIsNone(row[key])
        self.assertFalse(any(s["rule_id"].startswith("bazi.phase2.dayun")
                             for s in out["trace"]))
        self.assertEqual(out, execute("bazi", {**NATAL_INPUT,
                            "dayun_sequence_direction": "forward"}, allow_research=True))

    def test_gateway_research_only_for_manual_and_datetime(self):
        for inputs in ({**NATAL_INPUT, "dayun_sequence_direction": "forward"},
                       {"value": "2000-01-07T12:00:00+08:00",
                        "dayun_sequence_direction": "backward"}):
            with self.assertRaisesRegex(ValueError, "explicit research mode"):
                execute("bazi", inputs)
            result = execute("bazi", inputs, allow_research=True)
            self.assertEqual(result["mode"], "research")
            self.assertTrue(result["research_only"])
            self.assertIn("dayun_sequence_research", result["result"])
        with self.assertRaisesRegex(ValueError, "explicit research mode"):
            execute("bazi", {**NATAL_INPUT, "dayun_sequence_count": 3})

    def test_default_production_unchanged_and_no_implicit_direction(self):
        plain = chart(*NATAL)
        self.assertNotIn("dayun_sequence_research", plain["result"])
        self.assertNotIn("research_only", plain)
        self.assertEqual(plain["result"]["production_scope"],
                         "四柱、日主、十神、藏干结构事实")
        self.assertEqual(len(plain["trace"]), 3)
        with self.assertRaisesRegex(ValueError, "requires explicit"):
            chart(*NATAL, dayun_sequence_count=3)

    def test_fail_closed_invalid_direction_count_and_stem(self):
        for direction in ("顺", "reverse", "", 1, True, None, []):
            with self.subTest(direction=direction), self.assertRaises(ValueError):
                candidate_sequence("己丑", "甲", direction=direction)
        for count in (0, 13, -1, True, 3.0, "3", [], None):
            with self.subTest(count=count), self.assertRaises(ValueError):
                candidate_sequence("己丑", "甲", direction="forward", periods=count)
        for month in ("甲丑", "not-a-pillar", None):
            with self.subTest(month=month), self.assertRaises(ValueError):
                candidate_sequence(month, "甲", direction="forward")
        with self.assertRaises(ValueError):
            candidate_sequence("己丑", "X", direction="forward")
        with self.assertRaises(ValueError):
            chart(*NATAL, dayun_sequence_direction="forward", dayun_sequence_count=13)
        with self.assertRaises(ValueError):
            chart(*NATAL, dayun_sequence_direction="forward", dayun_sequence_count=True)


if __name__ == "__main__":
    unittest.main()
