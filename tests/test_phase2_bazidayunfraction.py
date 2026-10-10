"""Real pinned Jie boundaries and exact symbolic Dayun ratio (never dated age)."""
import copy
import unittest
from datetime import timedelta, timezone

from tianji_kb.bazi_annual_reference import _li_chun_of
from tianji_kb.bazi_dayun_age_fraction import (
    VARIANT, THREE_DAYS, exact_three_day_ratio,
)
from tianji_kb.engine import execute

BIRTH = "2000-01-07T12:00:00+08:00"


def research(value=BIRTH, direction="forward", **extra):
    return execute("bazi", {"value": value,
                           "dayun_sequence_direction": direction,
                           "dayun_jie_distance": True,
                           "dayun_age_fraction": VARIANT, **extra},
                   allow_research=True)


class DayunExactFractionTests(unittest.TestCase):
    def test_pinned_provider_ratio_reproduces_real_forward_backward_seconds(self):
        for direction in ("forward", "backward"):
            with self.subTest(direction=direction):
                out = research(direction=direction)
                rows = out["result"]["dayun_sequence_research"]
                measure = rows["jie_distance"]
                ratio = rows["age_fraction_research"]
                self.assertEqual(ratio["elapsed_seconds"], measure["elapsed_seconds"])
                self.assertEqual(ratio["distance_components"]["days"] * 86400
                                 + ratio["distance_components"]["hours"] * 3600
                                 + ratio["distance_components"]["minutes"] * 60
                                 + ratio["distance_components"]["seconds"],
                                 measure["elapsed_seconds"])
                numerator = ratio["symbolic_three_day_year_ratio"]["numerator"]
                denominator = ratio["symbolic_three_day_year_ratio"]["denominator"]
                self.assertEqual(numerator * THREE_DAYS,
                                 denominator * measure["elapsed_seconds"])
                self.assertIsNone(ratio["start_age"])
                self.assertIsNone(ratio["handover_datetime"])
                self.assertFalse(ratio["public_enabled"])
                self.assertFalse(ratio["ai_enabled"])
                self.assertFalse(out["interpretation_contract"]["ai_may_explain"])
                self.assertEqual(ratio, exact_three_day_ratio(measure))

    def test_lichun_one_second_and_zero_boundary_does_not_assert_zero_start_age(self):
        exact = _li_chun_of(2025)
        before = research(value=(exact-timedelta(seconds=1)).isoformat())
        after = research(value=(exact+timedelta(seconds=1)).isoformat(),
                         direction="backward")
        for out in (before, after):
            ratio = out["result"]["dayun_sequence_research"]["age_fraction_research"]
            self.assertEqual(ratio["elapsed_seconds"], 1)
            self.assertEqual(ratio["symbolic_three_day_year_ratio"],
                             {"numerator": 1, "denominator": THREE_DAYS})
            self.assertEqual(ratio["distance_components"],
                             {"days": 0, "hours": 0, "minutes": 0, "seconds": 1})
        exact_back = research(value=exact.isoformat(), direction="backward")
        zero = exact_back["result"]["dayun_sequence_research"]["age_fraction_research"]
        self.assertTrue(zero["zero_distance"])
        self.assertIsNone(zero["symbolic_three_day_year_ratio"])
        self.assertIsNone(zero["symbolic_ratio_decimal_8_places"])
        self.assertEqual(zero["age_conversion_status"],
                         "zero_jie_boundary_convention_unreviewed")
        self.assertIsNone(zero["start_age"])

    def test_birth_timezone_equivalence_and_no_implicit_production(self):
        local = _li_chun_of(2025) + timedelta(seconds=10)
        original = research(value=local.isoformat(), direction="backward")
        alternate = research(value=local.astimezone(timezone.utc).isoformat(),
                             direction="backward")
        self.assertEqual(original["result"]["dayun_sequence_research"]["age_fraction_research"],
                         alternate["result"]["dayun_sequence_research"]["age_fraction_research"])
        plain = execute("bazi", {"value": BIRTH})
        self.assertNotIn("dayun_sequence_research", plain["result"])
        without_fraction = execute("bazi", {"value": BIRTH,
            "dayun_sequence_direction": "forward", "dayun_jie_distance": True},
            allow_research=True)
        self.assertNotIn("age_fraction_research",
                         without_fraction["result"]["dayun_sequence_research"])

    def test_reject_missing_mode_or_invalid_variant_and_inputs(self):
        base = {"value": BIRTH, "dayun_sequence_direction": "forward",
                "dayun_jie_distance": True, "dayun_age_fraction": VARIANT}
        with self.assertRaisesRegex(ValueError, "research mode"):
            execute("bazi", base)
        for params in (
            {**base, "dayun_age_fraction": True},
            {**base, "dayun_age_fraction": "invented"},
            {**base, "dayun_age_fraction": None},
            {k:v for k,v in base.items() if k != "dayun_jie_distance"},
            {k:v for k,v in base.items() if k != "value"},
            {k:v for k,v in base.items() if k != "dayun_sequence_direction"},
        ):
            with self.subTest(params=params), self.assertRaises(ValueError):
                execute("bazi", params, allow_research=True)

    def test_plausible_but_forged_calendar_measurement_is_rejected(self):
        # The values below are syntactically valid, and some can be made
        # internally self-consistent, but cannot be authenticated against the
        # original pinned Jie provider.
        original = research()["result"]["dayun_sequence_research"]["jie_distance"]
        forged = (
            lambda d: d.__setitem__("birth_month_ganzhi",
                                    "甲子" if d["birth_month_ganzhi"] != "甲子" else "乙丑"),
            lambda d: d["previous_jie"].__setitem__(
                "name", "立春" if d["previous_jie"]["name"] != "立春" else "惊蛰"),
            lambda d: d.__setitem__("public_enabled", True),
            lambda d: d.__setitem__("ai_enabled", True),
            lambda d: d.__setitem__("start_age", 3),
            lambda d: d.__setitem__("handover_datetime", "2002-01-01T00:00:00+08:00"),
            lambda d: d.__setitem__("astronomical_precision_independently_verified", True),
            lambda d: d.__setitem__("direction_origin", "inferred"),
        )
        for index, change in enumerate(forged):
            with self.subTest(index=index), self.assertRaises(ValueError):
                value = copy.deepcopy(original)
                change(value)
                exact_three_day_ratio(value)
        # An untouched live provider measurement remains valid.
        self.assertEqual(exact_three_day_ratio(original)["elapsed_seconds"],
                         original["elapsed_seconds"])

    def test_tampered_measurements_are_rejected_even_if_metadata_still_says_reviewed(self):
        real = research()["result"]["dayun_sequence_research"]["jie_distance"]
        mutations = (
            lambda d: d.__setitem__("elapsed_seconds", d["elapsed_seconds"] + 1),
            lambda d: d.__setitem__("elapsed_whole_days", -1),
            lambda d: d.__setitem__("zero_distance", True),
            lambda d: d.__setitem__("direction", "backward"),
            lambda d: d.__setitem__("selected_jie", d["previous_jie"]),
            lambda d: d.__setitem__("calendar_provider", "another-library"),
            lambda d: d.__setitem__("dayun_conversion_rule_review_status", "approved"),
            lambda d: d.__setitem__("birth_month_ganzhi", "not-ganzhi"),
            lambda d: d.__setitem__("previous_jie", d["next_jie"]),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                copied = copy.deepcopy(real)
                mutate(copied)
                exact_three_day_ratio(copied)


if __name__ == "__main__":
    unittest.main()
