"""TJ-031.6 regression: solar-term attribution is instant-frame, not
birthplace-wall-frame.

Verified defect (tj0316-verify/report.md, production-API probes against
independent sxtwl/JPL anchors): calendar_for_zone fed birthplace wall-time
fields to lunar-python, whose jieqi table is a China-baseline wall-time
table, so year/month pillar attribution flipped at
(provider term wall reading - birthplace offset) instead of the true term
instant -- an error window of |8h - birthplace offset| at every jie
(Tokyo ~1h, London 7-8h, Los Angeles 15-16h). solar_term_started_at
spliced the birthplace offset onto the China wall reading and mislabelled
the term instant by exactly (8h - offset) on UTC readback.

Expected values below are the verification report's INDEPENDENT
derivations (term attribution by UTC instant vs sxtwl term instants;
year/month stems-branches by first-principles cycle arithmetic; day
pillars cross-checked by day-count arithmetic and sxtwl date functions;
hour pillars by day-stem clock arithmetic). They are NOT outputs of the
code under test. Day/hour expectations are identical before and after
the fix (F-1 local frame, 144/144 verified); year/month/solar_term/
started_at expectations are the ones the old code got wrong.

Public-CI safe: lunar-python + zoneinfo + production calendar modules
only, same partition as test_tz_birth_calendar.py.
"""

import unittest
from datetime import datetime, timezone

from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.engine import prepare_inputs

# 2024 Lichun: sxtwl UTC instant 2024-02-04T08:26:53Z (JPL 08:27:00Z);
# the provider's own term instant is 2024-02-04T08:27:07Z (China wall
# reading 16:27:07 minus the 8h baseline). Probes sit at +-1min/+-1h,
# far outside the ~14s inter-source divergence band.
LICHUN_PROVIDER_UTC = datetime(2024, 2, 4, 8, 27, 7, tzinfo=timezone.utc)
DAHAN_PROVIDER_UTC = datetime(2024, 1, 20, 14, 7, 22, tzinfo=timezone.utc)
XIAZHI_PROVIDER_UTC = datetime(2024, 6, 20, 20, 51, 0, tzinfo=timezone.utc)
LIXIA_1990_PROVIDER_UTC = datetime(1990, 5, 5, 18, 35, 26, tzinfo=timezone.utc)


def pillars(cal):
    return (
        cal["year_ganzhi"],
        cal["month_ganzhi"],
        cal["day_ganzhi"],
        cal["hour_ganzhi"],
    )


def started_utc(cal):
    return datetime.fromisoformat(cal["solar_term_started_at"]).astimezone(
        timezone.utc
    )


class LichunAttributionTests(unittest.TestCase):
    def test_london_one_hour_after_lichun(self):
        # Decisive case: instant is 1h past Lichun but the London wall
        # clock (09:26) had not passed the China term wall reading
        # (16:27); old code still reported the pre-term pillars.
        cal = calendar_for_zone("2024-02-04T09:26:53+00:00", "Europe/London")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊戌", "丁巳"))
        self.assertEqual(cal["solar_term"], "立春")

    def test_london_one_minute_after_lichun(self):
        cal = calendar_for_zone("2024-02-04T08:27:53+00:00", "Europe/London")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊戌", "丙辰"))

    def test_los_angeles_one_hour_after_lichun(self):
        cal = calendar_for_zone(
            "2024-02-04T01:26:53-08:00", "America/Los_Angeles")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊戌", "癸丑"))

    def test_tokyo_one_minute_before_lichun(self):
        # Tokyo wall clock (17:25) had passed the China term wall reading
        # but the instant had not reached Lichun; old code flipped early.
        cal = calendar_for_zone("2024-02-04T17:25:53+09:00", "Asia/Tokyo")
        self.assertEqual(pillars(cal), ("癸卯", "乙丑", "戊戌", "辛酉"))
        self.assertEqual(cal["solar_term"], "大寒")

    def test_tokyo_one_minute_after_lichun_control(self):
        cal = calendar_for_zone("2024-02-04T17:27:53+09:00", "Asia/Tokyo")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊戌", "辛酉"))

    def test_shanghai_controls_unchanged(self):
        cal = calendar_for_zone("2024-02-04T17:26:53+08:00", "Asia/Shanghai")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊戌", "辛酉"))
        cal = calendar_for_zone("2024-02-04T16:25:53+08:00", "Asia/Shanghai")
        self.assertEqual(pillars(cal), ("癸卯", "乙丑", "戊戌", "庚申"))


class OtherTermAttributionTests(unittest.TestCase):
    def test_jingzhe_tokyo_one_minute_before(self):
        # Month-only error in the old code (reported 丁卯 instead of 丙寅).
        cal = calendar_for_zone("2024-03-05T11:21:31+09:00", "Asia/Tokyo")
        self.assertEqual(pillars(cal), ("甲辰", "丙寅", "戊辰", "戊午"))

    def test_jingzhe_london_one_hour_after(self):
        cal = calendar_for_zone("2024-03-05T03:22:31+00:00", "Europe/London")
        self.assertEqual(pillars(cal), ("甲辰", "丁卯", "戊辰", "甲寅"))

    def test_qingming_london_bst_one_hour_after(self):
        # DST-period case (London on BST, +01:00; window 7h not 8h).
        cal = calendar_for_zone("2024-04-04T09:02:03+01:00", "Europe/London")
        self.assertEqual(pillars(cal), ("甲辰", "戊辰", "戊戌", "丁巳"))

    def test_qingming_tokyo_one_minute_before(self):
        cal = calendar_for_zone("2024-04-04T16:01:03+09:00", "Asia/Tokyo")
        self.assertEqual(pillars(cal), ("甲辰", "丁卯", "戊戌", "庚申"))

    def test_lidong_los_angeles_one_hour_after(self):
        cal = calendar_for_zone(
            "2024-11-06T15:19:49-08:00", "America/Los_Angeles")
        self.assertEqual(pillars(cal), ("甲辰", "乙亥", "甲戌", "壬申"))

    def test_lidong_tokyo_one_minute_before(self):
        cal = calendar_for_zone("2024-11-07T07:18:49+09:00", "Asia/Tokyo")
        self.assertEqual(pillars(cal), ("甲辰", "甲戌", "乙亥", "庚辰"))


class ZhongqiNegativeControlTests(unittest.TestCase):
    def test_xiazhi_london_after_keeps_wu_month(self):
        # 夏至 is a zhongqi: it never flips the month pillar, on either
        # side of the instant, in any frame. The old code's month was
        # right here but named the previous term (芒种) an hour late;
        # the term name is attribution-derived and must flip by instant.
        cal = calendar_for_zone("2024-06-20T22:50:45+01:00", "Europe/London")
        self.assertEqual(pillars(cal), ("甲辰", "庚午", "乙卯", "丁亥"))
        self.assertEqual(cal["solar_term"], "夏至")
        self.assertEqual(started_utc(cal), XIAZHI_PROVIDER_UTC)

    def test_xiazhi_los_angeles_before_keeps_wu_month(self):
        cal = calendar_for_zone(
            "2024-06-20T13:49:45-07:00", "America/Los_Angeles")
        self.assertEqual(pillars(cal), ("甲辰", "庚午", "乙卯", "癸未"))
        self.assertEqual(cal["solar_term"], "芒种")


class StartedAtInstantTests(unittest.TestCase):
    # The same birth instant expressed in four zones (Lichun + 1h):
    # every zone must name 立春 and label its start with the SAME UTC
    # instant -- the provider term instant the attribution used.
    CASES = [
        ("2024-02-04T17:26:53+08:00", "Asia/Shanghai",
         "2024-02-04 16:27:07+08:00"),
        ("2024-02-04T09:26:53+00:00", "Europe/London",
         "2024-02-04 08:27:07+00:00"),
        ("2024-02-04T18:26:53+09:00", "Asia/Tokyo",
         "2024-02-04 17:27:07+09:00"),
        ("2024-02-04T01:26:53-08:00", "America/Los_Angeles",
         "2024-02-04 00:27:07-08:00"),
    ]

    def test_started_at_same_instant_all_zones(self):
        for value, zone, expected_label in self.CASES:
            cal = calendar_for_zone(value, zone)
            self.assertEqual(cal["solar_term"], "立春", (value, zone))
            self.assertEqual(
                cal["solar_term_started_at"], expected_label, (value, zone))
            self.assertEqual(
                started_utc(cal), LICHUN_PROVIDER_UTC, (value, zone))

    def test_started_at_previous_term_tokyo(self):
        # Before Lichun the current term is 大寒; its provider wall
        # reading is 2024-01-20 22:07:22 (China baseline), i.e. the
        # instant 2024-01-20T14:07:22Z, rendered in Tokyo as 23:07:22.
        cal = calendar_for_zone("2024-02-04T17:25:53+09:00", "Asia/Tokyo")
        self.assertEqual(
            cal["solar_term_started_at"], "2024-01-20 23:07:22+09:00")
        self.assertEqual(started_utc(cal), DAHAN_PROVIDER_UTC)

    def test_started_at_london_daily_sample(self):
        # Non-boundary sample from the verification report: Lixia 1990,
        # sxtwl China wall reading 1990-05-06 02:35:26, so the instant
        # is 1990-05-05T18:35:26Z. The old label read back 7h late.
        cal = calendar_for_zone("1990-05-15T14:30:00+01:00", "Europe/London")
        self.assertEqual(pillars(cal), ("庚午", "辛巳", "庚辰", "癸未"))
        self.assertEqual(
            cal["solar_term_started_at"], "1990-05-05 19:35:26+01:00")
        self.assertEqual(started_utc(cal), LIXIA_1990_PROVIDER_UTC)


class PrepareInputsPropagationTests(unittest.TestCase):
    def test_bazi_london_lichun_via_prepare_inputs(self):
        prepared, _ = prepare_inputs(
            "bazi", {"value": "2024-02-04T09:26:53+00:00",
                     "zone": "Europe/London"})
        self.assertEqual(prepared["year_ganzhi"], "甲辰")
        self.assertEqual(prepared["month_ganzhi"], "丙寅")
        self.assertEqual(prepared["day_ganzhi"], "戊戌")

    def test_liuren_solar_term_follows_instant(self):
        prepared, _ = prepare_inputs(
            "liuren", {"value": "2024-06-20T22:50:45+01:00",
                       "zone": "Europe/London"})
        self.assertEqual(prepared["solar_term"], "夏至")


if __name__ == "__main__":
    unittest.main()
