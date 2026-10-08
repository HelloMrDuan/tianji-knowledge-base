"""Real calendar integration for optional, explicitly NON-adjudicated age simulation."""
import unittest
from datetime import datetime, timedelta, timezone
from fractions import Fraction

from tianji_kb.bazi_annual_reference import _li_chun_of
from tianji_kb.bazi_dayun_simulation import (
    VARIANT, GREGORIAN_MEAN_YEAR_SECONDS, THREE_DAYS_SECONDS,
    _half_up_fraction, simulate_dayun_age_and_timeline,
)
from tianji_kb.engine import execute


def research(value="2000-01-07T12:00:00+08:00", direction="forward", **more):
    return execute("bazi", {
        "value": value, "dayun_sequence_direction": direction,
        "dayun_jie_distance": True, "dayun_age_simulation": VARIANT, **more,
    }, allow_research=True)


class DayunAgeSimulationResearchTests(unittest.TestCase):
    def test_live_birth_forward_and_reverse_have_reproducible_simulated_dates(self):
        for direction in ("forward", "backward"):
            with self.subTest(direction=direction):
                output = research(direction=direction)
                dayun = output["result"]["dayun_sequence_research"]
                measure = dayun["jie_distance"]
                sim = dayun["age_simulation"]
                birth = datetime.fromisoformat(measure["birth_local_datetime"])
                exact = Fraction(measure["elapsed_seconds"], THREE_DAYS_SECONDS)
                self.assertEqual(sim["age_years_exact"], {
                    "numerator": exact.numerator, "denominator": exact.denominator})
                self.assertEqual(sim["simulated_first_offset_seconds"],
                                 _half_up_fraction(exact * GREGORIAN_MEAN_YEAR_SECONDS))
                self.assertEqual(len(sim["timeline"]), 8)
                self.assertFalse(sim["actual_start_age_adjudicated"])
                self.assertFalse(sim["verified_handover_dates_calculated"])
                self.assertFalse(sim["classical_method_reviewed"])
                self.assertFalse(sim["public_enabled"])
                self.assertFalse(sim["ai_enabled"])
                self.assertFalse(output["interpretation_contract"]["ai_may_explain"])
                first = datetime.fromisoformat(sim["timeline"][0]["simulated_start"])
                self.assertEqual(first.astimezone(timezone.utc) - birth.astimezone(timezone.utc),
                                 timedelta(seconds=sim["simulated_first_offset_seconds"]))
                for i, item in enumerate(sim["timeline"]):
                    original = dayun["rows"][i]
                    self.assertEqual(item["candidate_ganzhi"], original["candidate_ganzhi"])
                    self.assertEqual(item["ten_god_relative_to_natal_day_stem"],
                                     original["ten_god_relative_to_natal_day_stem"])
                    self.assertEqual(item["period_index"], i+1)
                    self.assertFalse(item["is_verified_handover_date"])
                    self.assertIsNone(item["luck_assessment"])
                    a = datetime.fromisoformat(item["simulated_start"])
                    b = datetime.fromisoformat(item["simulated_end_exclusive"])
                    self.assertEqual(b.astimezone(timezone.utc) -
                                     a.astimezone(timezone.utc),
                                     timedelta(seconds=10 * GREGORIAN_MEAN_YEAR_SECONDS))
                    if i:
                        self.assertEqual(a, datetime.fromisoformat(
                            sim["timeline"][i-1]["simulated_end_exclusive"]))
                    self.assertIsNone(original["start_date"])
                    self.assertIsNone(original["end_date"])
                    self.assertIsNone(original["start_age"])
                self.assertIsNone(measure["start_age"])
                self.assertIsNone(measure["handover_datetime"])
                self.assertFalse(any(t["rule_id"].startswith("bazi.phase2.dayun")
                                     for t in output["trace"]))
                self.assertEqual(output, research(direction=direction))

    def test_exact_fraction_and_rounding_no_binary_float(self):
        self.assertEqual(_half_up_fraction(Fraction(1, 2)), 1)
        self.assertEqual(_half_up_fraction(Fraction(3, 2)), 2)
        self.assertEqual(_half_up_fraction(Fraction(1, 3)), 0)
        self.assertEqual(GREGORIAN_MEAN_YEAR_SECONDS, 31556952)
        self.assertEqual(_half_up_fraction(
            Fraction(THREE_DAYS_SECONDS, THREE_DAYS_SECONDS) *
            GREGORIAN_MEAN_YEAR_SECONDS), GREGORIAN_MEAN_YEAR_SECONDS)

    def test_birth_timezone_equivalence_and_explicit_limit(self):
        birth = datetime.fromisoformat("2000-01-07T12:00:00+08:00")
        alt = birth.astimezone(timezone.utc).isoformat()
        a = research(value=birth.isoformat(), dayun_sequence_count=3)
        b = research(value=alt, dayun_sequence_count=3)
        self.assertEqual(a["result"]["dayun_sequence_research"]["age_simulation"],
                         b["result"]["dayun_sequence_research"]["age_simulation"])
        self.assertEqual(len(a["result"]["dayun_sequence_research"]["age_simulation"]["timeline"]), 3)

    def test_lunar_lichun_zero_distance_must_refuse_simulation(self):
        instant = _li_chun_of(2025).isoformat()
        # The measured Jie distance itself remains available for research,
        # but zero-distance start-age conventions are unresolved.
        baseline = execute("bazi", {"value": instant,
            "dayun_sequence_direction": "backward", "dayun_jie_distance": True},
            allow_research=True)
        self.assertTrue(baseline["result"]["dayun_sequence_research"]["jie_distance"]["zero_distance"])
        with self.assertRaisesRegex(ValueError, "Zero or invalid Jie distance"):
            research(value=instant, direction="backward")

    def test_no_implicit_variant_or_gateway_bypass(self):
        base = {"value": "2000-01-07T12:00:00+08:00",
                "dayun_sequence_direction": "forward", "dayun_jie_distance": True}
        plain = execute("bazi", base, allow_research=True)
        self.assertNotIn("age_simulation", plain["result"]["dayun_sequence_research"])
        for options in (
            {**base, "dayun_age_simulation": VARIANT},
            {**base, "dayun_age_simulation": "arbitrary"},
            {**base, "dayun_age_simulation": True},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                execute("bazi", options, allow_research=False)
        for options in (
            {**base, "dayun_age_simulation": "arbitrary"},
            {**base, "dayun_age_simulation": True},
            {**base, "dayun_age_simulation": None},
            {"value": base["value"], "dayun_age_simulation": VARIANT},
            {"value": base["value"], "dayun_sequence_direction": "forward",
             "dayun_age_simulation": VARIANT},
            {"year_ganzhi": "庚辰", "month_ganzhi": "己丑", "day_ganzhi": "甲子",
             "hour_ganzhi": "庚午", "dayun_sequence_direction": "forward",
             "dayun_age_simulation": VARIANT, "dayun_jie_distance": True},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                execute("bazi", options, allow_research=True)
        self.assertNotIn("dayun_sequence_research", execute("bazi", {
            "value": base["value"]}, allow_research=False)["result"])

    def test_both_year_boundary_and_simulation_maintain_distinct_scopes(self):
        out = research(annual_boundary_years=[2024, 2025], dayun_sequence_count=2)
        self.assertEqual(len(out["result"]["annual_li_chun_boundaries"]["rows"]), 2)
        self.assertEqual(len(out["result"]["dayun_sequence_research"]["age_simulation"]["timeline"]), 2)
        self.assertFalse(out["interpretation_contract"]["ai_may_explain"])


if __name__ == "__main__":
    unittest.main()
