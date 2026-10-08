"""Provider-second Jie interval tests: actual calendar, no mocked term times."""
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from tianji_kb.bazi_annual_reference import _li_chun_of
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance, JIE_NAMES
from tianji_kb.calendar import calendar
from tianji_kb.engine import execute

CHINA = ZoneInfo("Asia/Shanghai")
BIRTH = "2000-01-07T12:00:00+08:00"


class DayunJieDistanceTests(unittest.TestCase):
    def _call(self, when=BIRTH, direction="forward"):
        return execute("bazi", {
            "value": when,
            "dayun_sequence_direction": direction,
            "dayun_jie_distance": True,
            "dayun_sequence_count": 3,
        }, allow_research=True)

    def test_real_prev_and_next_jie_for_both_directions(self):
        ahead = self._call()
        backward = self._call(direction="backward")
        for out in (ahead, backward):
            result = out["result"]["dayun_sequence_research"]
            d = result["jie_distance"]
            birth = datetime.fromisoformat(d["birth_local_datetime"])
            prev_at = datetime.fromisoformat(d["previous_jie"]["at"])
            next_at = datetime.fromisoformat(d["next_jie"]["at"])
            self.assertTrue(prev_at <= birth < next_at)
            self.assertLess((next_at - prev_at), timedelta(days=40))
            self.assertIn(d["previous_jie"]["name"], JIE_NAMES)
            self.assertIn(d["next_jie"]["name"], JIE_NAMES)
            self.assertEqual(calendar(prev_at)["month_ganzhi"], d["birth_month_ganzhi"])
            self.assertEqual(calendar(next_at - timedelta(seconds=1))["month_ganzhi"],
                             d["birth_month_ganzhi"])
            self.assertNotEqual(calendar(next_at)["month_ganzhi"], d["birth_month_ganzhi"])
            self.assertEqual(d["elapsed_seconds"],
                             d["elapsed_whole_days"] * 86400 +
                             d["remaining_seconds_after_whole_days"])
            self.assertIsNone(d["start_age"])
            self.assertIsNone(d["handover_datetime"])
            self.assertIsNone(d["conversion_to_start_age"])
            self.assertEqual(d["dayun_conversion_rule_review_status"], "unreviewed")
            self.assertFalse(d["astronomical_precision_independently_verified"])
            self.assertFalse(result["public_enabled"])
            self.assertFalse(out["interpretation_contract"]["ai_may_explain"])
            self.assertEqual(len(out["result"]["dayun_sequence_research"]["rows"]), 3)
            self.assertFalse(any(s["rule_id"].startswith("bazi.phase2.dayun")
                                 for s in out["trace"]))
        forward_dist = ahead["result"]["dayun_sequence_research"]["jie_distance"]
        back_dist = backward["result"]["dayun_sequence_research"]["jie_distance"]
        self.assertEqual(forward_dist["selected_jie"], forward_dist["next_jie"])
        self.assertEqual(back_dist["selected_jie"], back_dist["previous_jie"])
        self.assertEqual(
            forward_dist["elapsed_seconds"] + back_dist["elapsed_seconds"],
            int((datetime.fromisoformat(forward_dist["next_jie"]["at"]) -
                 datetime.fromisoformat(back_dist["previous_jie"]["at"])).total_seconds()))

    def test_lichun_before_at_after_second_and_zero_boundary(self):
        at = _li_chun_of(2025)
        before = at - timedelta(seconds=1)
        after = at + timedelta(seconds=1)
        pre = self._call(before.isoformat(), "forward")["result"]["dayun_sequence_research"]["jie_distance"]
        exact_back = self._call(at.isoformat(), "backward")["result"]["dayun_sequence_research"]["jie_distance"]
        after_back = self._call(after.isoformat(), "backward")["result"]["dayun_sequence_research"]["jie_distance"]
        self.assertEqual(pre["selected_jie"]["name"], "立春")
        self.assertEqual(pre["selected_jie"]["at"], at.isoformat())
        self.assertEqual(pre["elapsed_seconds"], 1)
        self.assertEqual(exact_back["selected_jie"]["name"], "立春")
        self.assertEqual(exact_back["elapsed_seconds"], 0)
        self.assertTrue(exact_back["zero_distance"])
        self.assertEqual(after_back["elapsed_seconds"], 1)
        self.assertEqual(exact_back["previous_jie"]["at"], at.isoformat())
        self.assertNotEqual(pre["birth_month_ganzhi"], exact_back["birth_month_ganzhi"])

    def test_same_instant_different_input_timezone(self):
        local = datetime.fromisoformat(BIRTH)
        utc = local.astimezone(timezone.utc)
        first = self._call(local.isoformat())["result"]["dayun_sequence_research"]["jie_distance"]
        second = self._call(utc.isoformat())["result"]["dayun_sequence_research"]["jie_distance"]
        self.assertEqual(first, second)

    def test_reject_without_birth_true_bool_or_direction(self):
        for params in (
            {"value": BIRTH, "dayun_jie_distance": True},
            {"dayun_jie_distance": True, "dayun_sequence_direction": "forward",
             "year_ganzhi": "庚辰", "month_ganzhi": "己丑", "day_ganzhi": "甲子", "hour_ganzhi": "庚午"},
            {"value": BIRTH, "dayun_sequence_direction": "forward", "dayun_jie_distance": False},
            {"value": BIRTH, "dayun_sequence_direction": "forward", "dayun_jie_distance": "yes"},
        ):
            with self.subTest(params=params), self.assertRaises(ValueError):
                execute("bazi", params, allow_research=True)
        with self.assertRaisesRegex(ValueError, "explicit research mode"):
            execute("bazi", {"value": BIRTH, "dayun_sequence_direction": "forward",
                             "dayun_jie_distance": True})

    def test_reject_invalid_births_and_wrong_expected_month(self):
        good_month = calendar(BIRTH)["month_ganzhi"]
        for birth in ("2000-01-07T12:00:00", "2000-01-07T12:00:00.123+08:00",
                      "1900-01-07T12:00:00+08:00", "2099-12-07T12:00:00+08:00",
                      "not-a-date", None):
            with self.subTest(birth=birth), self.assertRaises(ValueError):
                adjacent_jie_distance(birth, "forward", expected_month_ganzhi=good_month)
        with self.assertRaisesRegex(ValueError, "disagrees"):
            adjacent_jie_distance(BIRTH, "forward", expected_month_ganzhi="甲寅")
        with self.assertRaises(ValueError):
            adjacent_jie_distance(BIRTH, "reverse", expected_month_ganzhi=good_month)
        original = execute("bazi", {"value": BIRTH})
        self.assertNotIn("dayun_sequence_research", original["result"])
        self.assertNotIn("research_only", original)


if __name__ == "__main__":
    unittest.main()
