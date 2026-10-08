"""Real historical-role opt-in direction and Dayun end-to-end gateway tests."""
import unittest

from tianji_kb.bazi_dayun_direction import VARIANT, YANG_STEMS, traditional_direction
from tianji_kb.bazi_dayun_simulation import VARIANT as AGE_SIM_VARIANT
from tianji_kb.engine import execute

NATAL = {"year_ganzhi": "庚辰", "month_ganzhi": "己丑",
         "day_ganzhi": "甲子", "hour_ganzhi": "庚午"}
BIRTH = "2000-01-07T12:00:00+08:00"


class DayunTraditionalDirectionResearchTests(unittest.TestCase):
    def test_four_historical_cases_are_calculated_not_unintentionally_inferred(self):
        cases = [
            ("庚辰", "male", "yang", "forward", "庚寅"),
            ("庚辰", "female", "yang", "backward", "戊子"),
            ("辛巳", "male", "yin", "backward", "戊子"),
            ("辛巳", "female", "yin", "forward", "庚寅"),
        ]
        for year, role, polarity, direction, first in cases:
            with self.subTest(year=year, role=role):
                input_data = {**NATAL, "year_ganzhi": year,
                              "traditional_role": role, "dayun_direction_policy": VARIANT,
                              "dayun_sequence_count": 3}
                output = execute("bazi", input_data, allow_research=True)
                research = output["result"]["dayun_sequence_research"]
                selector = research["direction_research"]
                self.assertEqual(selector["year_stem_polarity"], polarity)
                self.assertEqual(selector["direction"], direction)
                self.assertEqual(research["direction"], direction)
                self.assertEqual(research["rows"][0]["candidate_ganzhi"], first)
                self.assertEqual(selector["traditional_role"], role)
                self.assertEqual(selector["traditional_role_selection"],
                                 "explicit_historical_category_not_inferred_identity")
                self.assertTrue(research["direction_from_natal_attributes_calculated"])
                self.assertEqual(research["direction_origin"],
                                 "opt_in_traditional_year_stem_role_candidate")
                self.assertFalse(selector["classical_direction_evidence_approved"])
                self.assertIsNone(selector["direction_rule_match"])
                self.assertFalse(research["public_enabled"])
                self.assertFalse(research["ai_enabled"])
                self.assertFalse(output["interpretation_contract"]["ai_may_explain"])
                self.assertNotIn("age_simulation", research)
                self.assertNotIn("jie_distance", research)
                self.assertEqual(len(research["rows"]), 3)
                self.assertEqual(output, execute("bazi", input_data, allow_research=True))
                self.assertFalse(any(t["rule_id"].startswith("bazi.phase2.dayun")
                                     for t in output["trace"]))

    def test_real_birth_drives_integrated_jie_age_and_timeline(self):
        for role in ("male", "female"):
            inputs = {"value": BIRTH, "traditional_role": role,
                      "dayun_direction_policy": VARIANT, "dayun_jie_distance": True,
                      "dayun_age_simulation": AGE_SIM_VARIANT, "dayun_sequence_count": 4}
            result = execute("bazi", inputs, allow_research=True)
            cal = result["input_calendar"]
            research = result["result"]["dayun_sequence_research"]
            polarity = "yang" if cal["year_ganzhi"][0] in YANG_STEMS else "yin"
            forward = (polarity == "yang") == (role == "male")
            self.assertEqual(research["direction"], "forward" if forward else "backward")
            self.assertEqual(research["direction_research"]["year_ganzhi"],
                             cal["year_ganzhi"])
            self.assertEqual(research["jie_distance"]["direction"],
                             research["direction"])
            self.assertEqual(len(research["age_simulation"]["timeline"]), 4)
            self.assertEqual(research["jie_distance"]["selected_jie"],
                             research["jie_distance"]["next_jie"] if forward
                             else research["jie_distance"]["previous_jie"])
            self.assertFalse(research["age_simulation"]["verified_handover_dates_calculated"])
            self.assertFalse(research["direction_research"]["classical_direction_evidence_approved"])
            self.assertIsNone(research["rows"][0]["start_age"])
            self.assertIsNone(research["rows"][0]["start_date"])

    def test_no_unrequested_direction_and_gateway_production_is_unchanged(self):
        base = {**NATAL, "traditional_role": "male"}
        no_policy = execute("bazi", base)
        self.assertNotIn("dayun_sequence_research", no_policy["result"])
        with self.assertRaisesRegex(ValueError, "research mode"):
            execute("bazi", {**base, "dayun_direction_policy": VARIANT})
        with self.assertRaises(ValueError):
            execute("bazi", {"value": BIRTH, "traditional_role": "female",
                             "dayun_direction_policy": VARIANT,
                             "dayun_jie_distance": True, "dayun_age_simulation": AGE_SIM_VARIANT})
        self.assertTrue(execute("bazi", {**base, "dayun_direction_policy": VARIANT},
                                allow_research=True)["research_only"])

    def test_reject_ambiguous_role_or_direction_and_bad_policy(self):
        base = {**NATAL, "dayun_direction_policy": VARIANT}
        invalid = [
            {**base},
            {**base, "traditional_role": "other"},
            {**base, "traditional_role": "未知"},
            {**base, "traditional_role": True},
            {**base, "traditional_role": None},
            {**base, "traditional_role": "male", "dayun_sequence_direction": "backward"},
            {**base, "traditional_role": "male", "dayun_direction_policy": "auto"},
            {**base, "traditional_role": "male", "dayun_direction_policy": True},
        ]
        for params in invalid:
            with self.subTest(params=params), self.assertRaises(ValueError):
                execute("bazi", params, allow_research=True)
        for year in ("甲丑", "bad", "", None, 123):
            with self.subTest(year=year), self.assertRaises(ValueError):
                traditional_direction(year, traditional_role="male")
        for role in ("other", None, 1, True, "", [], {}):
            with self.subTest(role=role), self.assertRaises(ValueError):
                traditional_direction("庚辰", traditional_role=role)

    def test_explicit_manual_direction_is_not_reinterpreted_as_role_direction(self):
        output = execute("bazi", {**NATAL, "traditional_role": "female",
                           "dayun_sequence_direction": "forward"}, allow_research=True)
        research = output["result"]["dayun_sequence_research"]
        self.assertEqual(research["direction"], "forward")
        self.assertEqual(research["direction_origin"], "explicit_caller_selection_only")
        self.assertFalse(research["direction_from_natal_attributes_calculated"])
        self.assertNotIn("direction_research", research)


if __name__ == "__main__":
    unittest.main()
