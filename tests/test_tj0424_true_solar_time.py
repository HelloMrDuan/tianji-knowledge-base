"""TJ-0424 (B7): optional apparent (true) solar time conversion.

Independent reference values in this file were NOT produced by the code
under test. They come from two independent sources:

1. JPL DE421 ephemeris via Skyfield 1.55 (``almanac.meridian_transits``):
   for each date below, the Sun's Greenwich meridian-transit instant
   was read off the ephemeris and EoT derived as
   ``12:00 minus transit time`` (EoT = apparent minus mean solar time,
   so a transit after 12:00 UT means a negative EoT). The module was
   evaluated at 12:00 UTC on the same date; the largest measured
   deviation over the 16 dates was 0.058 min (2025-11-03), so the
   0.5 min tolerance below is ~8x looser than the measured agreement
   and still falsifies any sign error, any dropped factor, or any
   wrong constant of material size (a sign flip fails by 6-33 min;
   dropping the x4 in the EoT series fails by ~10 min at the extrema).
2. Published equation-of-time tables, which agree with the DE421
   values above: 11 Feb 2026 -14m12s and 3 Nov 2026 +16m27s
   (appsail.eu astronavigation tables, 2026); -14.2 min / +16.5 min
   (solarposition.org, "Equation of Time", 2026 table); -14m15s /
   +16m25s (omc.center). Zero crossings ~15 Apr, ~13 Jun, ~1 Sep,
   ~25 Dec (all sources agree to within a day).

Research only: research_only=True, public=False, ai=False. This module
adds no public API field and changes no existing charting behaviour.
"""

import unittest
from datetime import datetime, timedelta, timezone

from tianji_kb.bazi_true_solar_time import (
    apparent_solar_time,
    equation_of_time_minutes,
    longitude_correction_minutes,
)

UTC = timezone.utc
CST = timezone(timedelta(hours=8))


def _utc(y, m, d, hh=12, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=UTC)


# (date, DE421 transit-derived EoT in minutes). See module docstring.
DE421_EOT_2024_2030 = (
    (datetime(2026, 1, 1), -3.567),
    (datetime(2026, 2, 11), -14.176),
    (datetime(2026, 3, 20), -7.436),
    (datetime(2026, 4, 15), -0.007),
    (datetime(2026, 5, 14), +3.672),
    (datetime(2026, 6, 21), -1.819),
    (datetime(2026, 7, 26), -6.566),
    (datetime(2026, 8, 1), -6.359),
    (datetime(2026, 9, 22), +7.273),
    (datetime(2026, 10, 10), +13.000),
    (datetime(2026, 11, 3), +16.446),
    (datetime(2026, 12, 21), +1.935),
    (datetime(2025, 2, 11), -14.189),
    (datetime(2025, 11, 3), +16.433),
    (datetime(2024, 6, 21), -1.924),
    (datetime(2030, 3, 20), -7.438),
)

# Tolerance vs the independent ephemeris values (measured worst
# deviation 0.058 min; tolerance is ~8x that, still falsifying).
EOT_TOL_MIN = 0.5


class EquationOfTimeTests(unittest.TestCase):
    def test_eot_matches_de421_transits(self):
        """EoT at 12:00 UTC matches JPL DE421 transit-derived EoT."""
        for day, expected in DE421_EOT_2024_2030:
            with self.subTest(date=day.date().isoformat()):
                got = equation_of_time_minutes(
                    datetime(day.year, day.month, day.day, 12, 0,
                             tzinfo=UTC))
                self.assertAlmostEqual(got, expected, delta=EOT_TOL_MIN)

    def test_eot_published_extrema(self):
        """Published extrema: ~-14.2 min on 11 Feb, ~+16.5 min on 3 Nov."""
        self.assertAlmostEqual(
            equation_of_time_minutes(_utc(2026, 2, 11)), -14.2,
            delta=0.5)
        self.assertAlmostEqual(
            equation_of_time_minutes(_utc(2026, 11, 3)), 16.5, delta=0.5)

    def test_eot_published_minor_extrema(self):
        """Minor peak ~+3.7 min on 14 May; minor trough ~-6.6 min 26 Jul."""
        self.assertAlmostEqual(
            equation_of_time_minutes(_utc(2026, 5, 14)), 3.7, delta=0.5)
        self.assertAlmostEqual(
            equation_of_time_minutes(_utc(2026, 7, 26)), -6.6, delta=0.5)

    def test_eot_zero_crossings(self):
        """EoT crosses zero near 15 Apr, 13 Jun, 1 Sep, 25 Dec."""
        for day in ((2026, 4, 15), (2026, 6, 13),
                    (2026, 9, 1), (2026, 12, 25)):
            with self.subTest(date="%d-%02d-%02d" % day):
                got = equation_of_time_minutes(_utc(*day))
                self.assertLess(abs(got), 0.6)

    def test_eot_solstice_equinox_sign_and_magnitude(self):
        """Sign/magnitude at the four season points (2026)."""
        # Spring equinox: EoT clearly negative, magnitude 5-10 min.
        eot = equation_of_time_minutes(_utc(2026, 3, 20))
        self.assertLess(eot, -5.0)
        self.assertGreater(eot, -10.0)
        # Summer solstice: small negative (within 3 min of zero).
        eot = equation_of_time_minutes(_utc(2026, 6, 21))
        self.assertLess(eot, 0.0)
        self.assertGreater(eot, -3.0)
        # Autumn equinox: clearly positive, magnitude 5-10 min.
        eot = equation_of_time_minutes(_utc(2026, 9, 22))
        self.assertGreater(eot, 5.0)
        self.assertLess(eot, 10.0)
        # Winter solstice: small positive (within 3 min of zero).
        eot = equation_of_time_minutes(_utc(2026, 12, 21))
        self.assertGreater(eot, 0.0)
        self.assertLess(eot, 3.0)

    def test_eot_requires_aware_datetime(self):
        with self.assertRaises(ValueError):
            equation_of_time_minutes(datetime(2026, 3, 20, 12, 0))


class LongitudeCorrectionTests(unittest.TestCase):
    def test_longitude_correction_exact(self):
        # 4 minutes per degree east of the standard meridian.
        self.assertAlmostEqual(
            longitude_correction_minutes(116.4074, 120.0), -14.3704,
            places=3)
        self.assertAlmostEqual(
            longitude_correction_minutes(121.4737, 120.0), 5.8948,
            places=3)
        self.assertAlmostEqual(
            longitude_correction_minutes(-74.006, -75.0), 3.976, places=3)
        self.assertAlmostEqual(
            longitude_correction_minutes(0.0, 0.0), 0.0, places=6)

    def test_longitude_correction_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            longitude_correction_minutes(181.0, 120.0)
        with self.assertRaises(ValueError):
            longitude_correction_minutes(-180.5, 0.0)
        with self.assertRaises(ValueError):
            longitude_correction_minutes(120.0, 200.0)

    def test_longitude_correction_wraps_at_dateline(self):
        # +180 and -180 are the same meridian: zero correction either way.
        self.assertAlmostEqual(
            longitude_correction_minutes(180.0, -180.0), 0.0, places=9)
        self.assertAlmostEqual(
            longitude_correction_minutes(-180.0, 180.0), 0.0, places=9)
        # Neighbours across the dateline differ by 4 min per degree.
        self.assertAlmostEqual(
            longitude_correction_minutes(179.9, 120.0)
            - longitude_correction_minutes(-179.9, 120.0),
            -0.8, places=6)


class ApparentSolarTimeTests(unittest.TestCase):
    def test_beijing_spring_equinox(self):
        """Beijing 116.4074E, 2026-03-20 12:00 CST -> ~11:38 AST."""
        r = apparent_solar_time(
            datetime(2026, 3, 20, 12, 0, tzinfo=CST), 116.4074, 8)
        expect = datetime(2026, 3, 20, 11, 38, 6, tzinfo=CST)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)
        self.assertAlmostEqual(r["longitude_correction_minutes"], -14.3704,
                               places=3)
        self.assertAlmostEqual(r["equation_of_time_minutes"], -7.53,
                               delta=0.5)
        self.assertAlmostEqual(r["total_correction_minutes"], -21.90,
                               delta=0.5)
        self.assertFalse(r["date_shifted"])
        self.assertEqual(r["date_shift_days"], 0)

    def test_shanghai_summer_solstice(self):
        """Shanghai 121.4737E, 2026-06-21 12:00 CST -> ~12:04 AST."""
        r = apparent_solar_time(
            datetime(2026, 6, 21, 12, 0, tzinfo=CST), 121.4737, 8)
        expect = datetime(2026, 6, 21, 12, 4, 9, tzinfo=CST)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)
        self.assertAlmostEqual(r["longitude_correction_minutes"], 5.8948,
                               places=3)

    def test_new_york_winter_solstice_negative_longitude(self):
        """New York -74.0060, 2026-12-21 12:00 EST(-5) -> ~12:05:48 AST."""
        est = timezone(timedelta(hours=-5))
        r = apparent_solar_time(
            datetime(2026, 12, 21, 12, 0, tzinfo=est), -74.0060, -5)
        expect = datetime(2026, 12, 21, 12, 5, 48, tzinfo=est)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)
        self.assertAlmostEqual(r["longitude_correction_minutes"], 3.976,
                               places=3)
        self.assertAlmostEqual(r["equation_of_time_minutes"], 1.82,
                               delta=0.5)
        self.assertFalse(r["date_shifted"])

    def test_london_january(self):
        """London -0.1278, 2026-01-15 12:00 UTC -> ~11:50:05 AST."""
        r = apparent_solar_time(
            datetime(2026, 1, 15, 12, 0, tzinfo=UTC), -0.1278, 0)
        expect = datetime(2026, 1, 15, 11, 50, 5, tzinfo=UTC)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)

    def test_longitude_120_vs_0_same_instant(self):
        """Same instant, lon 120E vs 0: AST differs by exactly 480 min."""
        dt = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r120 = apparent_solar_time(dt, 120.0, 8)
        r0 = apparent_solar_time(dt, 0.0, 8)
        diff = (r120["apparent_solar_time"]
                - r0["apparent_solar_time"]).total_seconds() / 60.0
        self.assertAlmostEqual(diff, 480.0, places=6)
        # EoT is a function of the instant only, not of longitude.
        self.assertAlmostEqual(r120["equation_of_time_minutes"],
                               r0["equation_of_time_minutes"], places=9)
        self.assertAlmostEqual(r120["longitude_correction_minutes"], 0.0,
                               places=9)
        self.assertAlmostEqual(r0["longitude_correction_minutes"], -480.0,
                               places=9)

    def test_date_shift_backwards(self):
        """Urumqi 87.62E, 2026-01-01 00:30 CST -> previous day ~22:17."""
        r = apparent_solar_time(
            datetime(2026, 1, 1, 0, 30, tzinfo=CST), 87.62, 8)
        expect = datetime(2025, 12, 31, 22, 17, 18, tzinfo=CST)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)
        self.assertTrue(r["date_shifted"])
        self.assertEqual(r["date_shift_days"], -1)
        self.assertEqual(r["input_date"], "2026-01-01")
        self.assertEqual(r["apparent_date"], "2025-12-31")
        self.assertAlmostEqual(r["longitude_correction_minutes"], -129.52,
                               places=2)

    def test_date_shift_forwards(self):
        """New York, 2026-11-03 23:58 EST -> next day ~00:18 (+20.5 min)."""
        est = timezone(timedelta(hours=-5))
        r = apparent_solar_time(
            datetime(2026, 11, 3, 23, 58, tzinfo=est), -74.0060, -5)
        expect = datetime(2026, 11, 4, 0, 18, 28, tzinfo=est)
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)
        self.assertTrue(r["date_shifted"])
        self.assertEqual(r["date_shift_days"], 1)
        self.assertEqual(r["apparent_date"], "2026-11-04")

    def test_explicit_tz_offset_is_authoritative(self):
        """dt.tzinfo (+8) is NOT trusted: tz_offset=+9 governs.

        Same wall reading 12:00, lon 120E: with tz_offset 9 the
        standard meridian is 135E, so the longitude correction is
        exactly -60 min and UTC is 03:00, not 04:00.
        """
        r = apparent_solar_time(
            datetime(2026, 3, 20, 12, 0, tzinfo=CST), 120.0, 9)
        self.assertEqual(r["tz_offset_hours"], 9.0)
        self.assertEqual(r["standard_meridian_deg"], 135.0)
        self.assertAlmostEqual(r["longitude_correction_minutes"], -60.0,
                               places=9)
        expect = datetime(2026, 3, 20, 11, 52, 27,
                          tzinfo=timezone(timedelta(hours=9)))
        delta = abs((r["apparent_solar_time"] - expect).total_seconds())
        self.assertLess(delta, 60.0)

    def test_standard_meridian_override(self):
        """Explicit meridian 121.4737E zeroes the longitude correction."""
        r = apparent_solar_time(
            datetime(2026, 6, 21, 12, 0, tzinfo=CST), 121.4737, 8,
            standard_meridian_deg=121.4737)
        self.assertAlmostEqual(r["longitude_correction_minutes"], 0.0,
                               places=9)
        self.assertAlmostEqual(r["total_correction_minutes"],
                               r["equation_of_time_minutes"], places=9)

    def test_half_hour_zone(self):
        """IST (+5:30, meridian 82.5E): lon 77.2E -> -21.2 min."""
        ist = timezone(timedelta(hours=5, minutes=30))
        r = apparent_solar_time(
            datetime(2026, 3, 20, 12, 0, tzinfo=ist), 77.2, 5.5)
        self.assertEqual(r["standard_meridian_deg"], 82.5)
        self.assertAlmostEqual(r["longitude_correction_minutes"], -21.2,
                               places=6)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            apparent_solar_time(datetime(2026, 3, 20, 12, 0), 120.0, 8)
        with self.assertRaises(ValueError):
            apparent_solar_time(_utc(2026, 3, 20), 181.0, 8)
        with self.assertRaises(ValueError):
            apparent_solar_time(_utc(2026, 3, 20), 120.0, 15)
        with self.assertRaises(ValueError):
            apparent_solar_time(_utc(2026, 3, 20), 120.0, -13)
        with self.assertRaises(ValueError):
            # Sub-minute offsets are refused, never silently rounded.
            apparent_solar_time(_utc(2026, 3, 20), 120.0, 8.001)
        with self.assertRaises(ValueError):
            apparent_solar_time(_utc(2026, 3, 20), 120.0, 8,
                                standard_meridian_deg=200.0)

    def test_output_contract_and_status_flags(self):
        """Structured output: AST, corrections, basis, limits, flags."""
        r = apparent_solar_time(
            datetime(2026, 3, 20, 12, 0, tzinfo=CST), 116.4074, 8)
        for key in ("apparent_solar_time", "input_local_time",
                    "input_date", "apparent_date", "date_shifted",
                    "date_shift_days", "longitude_deg", "tz_offset_hours",
                    "standard_meridian_deg", "longitude_correction_minutes",
                    "equation_of_time_minutes", "total_correction_minutes",
                    "julian_day", "method", "astronomical_basis",
                    "calendar_basis", "precision_limits", "method_note",
                    "optional_conversion",
                    "current_standard_time_convention_unchanged",
                    "research_only", "public", "ai", "status"):
            self.assertIn(key, r)
        self.assertEqual(r["status"], "ok")
        self.assertTrue(r["research_only"])
        self.assertFalse(r["public"])
        self.assertFalse(r["ai"])
        self.assertTrue(r["optional_conversion"])
        self.assertTrue(r["current_standard_time_convention_unchanged"])
        self.assertIn("NOAA", r["astronomical_basis"])
        self.assertIn("Meeus", r["astronomical_basis"])
        # Standard-time charting is unchanged: the note says so.
        self.assertIn("unchanged", r["method_note"])
        # Total correction is the exact sum of its two parts.
        self.assertAlmostEqual(
            r["total_correction_minutes"],
            r["longitude_correction_minutes"]
            + r["equation_of_time_minutes"], places=9)
        # Returned AST carries the stated fixed offset.
        self.assertEqual(r["apparent_solar_time"].utcoffset(),
                         timedelta(hours=8))

    def test_deterministic_and_pure(self):
        dt = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r1 = apparent_solar_time(dt, 116.4074, 8)
        r2 = apparent_solar_time(dt, 116.4074, 8)
        self.assertEqual(r1, r2)
        self.assertEqual(dt, datetime(2026, 3, 20, 12, 0, tzinfo=CST))


if __name__ == "__main__":
    unittest.main()


# ======================================================================
# TJ-0424 batch 2, P1: research-grade charting entry
# (src/tianji_kb/bazi_true_solar_chart.py).
#
# The jieqi instants asserted below are recomputed INDEPENDENTLY in
# each test from the pinned provider (lunar-python 1.4.8), the same
# provider the calendar adapter uses -- they are not read from the
# module under test. The expected pillar changes were likewise read
# off real chart_from_datetime runs, not invented: e.g. Urumqi
# 2026-02-04 05:00 CST charts 丙午/庚寅/己酉 while the converted
# 02:36 instant charts 乙巳/己丑/己酉.
# ======================================================================

from lunar_python import Solar as _LunarSolar

from tianji_kb.bazi_core import chart_from_datetime
from tianji_kb.bazi_true_solar_chart import (
    ENTRY_ID,
    JIEQI_UNCERTAINTY_WINDOW_MINUTES,
    compare_standard_vs_true_solar,
    true_solar_chart,
)

EST = timezone(timedelta(hours=-5))


def _independent_jieqi_utc(y, m, d, hh, mm, ss, name):
    """Jieqi instant (UTC) from the pinned provider, independent of the entry.

    ``(y, m, d, hh, mm, ss)`` is a Shanghai wall-clock reading near the
    term; the provider's jieqi solar times are +08:00, mirroring
    ``tianji_kb.calendar``.
    """
    lunar = _LunarSolar.fromYmdHms(y, m, d, hh, mm, ss).getLunar()
    for term in (lunar.getPrevJieQi(False), lunar.getNextJieQi()):
        if term.getName() == name:
            wall = datetime.strptime(term.getSolar().toYmdHms(),
                                     "%Y-%m-%d %H:%M:%S")
            return wall.replace(tzinfo=CST).astimezone(timezone.utc)
    raise AssertionError("term %s not adjacent to %d-%02d-%02d" % (name, y, m, d))


def _pillars(chart):
    return {item["name"]: item["ganzhi"] for item in chart["pillars"]}


class TrueSolarChartDefaultOffTests(unittest.TestCase):
    def test_entry_is_off_by_default(self):
        """No flag -> ValueError, no chart; explicit opt-in works."""
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        with self.assertRaises(ValueError) as ctx:
            true_solar_chart(birth, 116.4074, 8)
        self.assertIn("use_true_solar_time=True", str(ctx.exception))
        ok = true_solar_chart(birth, 116.4074, 8, use_true_solar_time=True)
        self.assertEqual(ok["status"], "ok")
        self.assertTrue(ok["input"]["use_true_solar_time"])

    def test_entry_contract_flags(self):
        r = true_solar_chart(datetime(2026, 3, 20, 12, 0, tzinfo=CST),
                             116.4074, 8, use_true_solar_time=True)
        self.assertEqual(r["entry"], ENTRY_ID)
        self.assertEqual(r["method"], "modern_engineering")
        self.assertTrue(r["research_only"])
        self.assertFalse(r["public"])
        self.assertFalse(r["ai"])
        self.assertTrue(r["standard_time_convention_unchanged"])
        self.assertIn("NOAA", r["astronomical_basis"])
        self.assertIn("Neither", r["comparison_note"])
        self.assertIn("unchanged", r["comparison_note"])


class TrueSolarChartComparisonTests(unittest.TestCase):
    def test_beijing_no_pillar_change_and_standard_chart_untouched(self):
        """Beijing noon: correction -21.9 min moves no pillar.

        The standard chart in the result is exactly
        chart_from_datetime(birth); the solar chart is exactly
        chart_from_datetime(apparent). Nothing is merged.
        """
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 116.4074, 8)
        self.assertEqual(_pillars(r["standard_time_chart"]),
                         _pillars(chart_from_datetime(birth)))
        apparent = r["conversion"]["apparent_solar_time"]
        self.assertEqual(_pillars(r["true_solar_time_chart"]),
                         _pillars(chart_from_datetime(apparent)))
        self.assertFalse(r["differences"]["any_pillar_changed"])
        for name in ("year", "month", "day", "hour"):
            self.assertFalse(r["differences"]["pillars"][name]["changed"])
        self.assertFalse(r["jieqi"]["crossed"])
        self.assertFalse(r["jieqi"]["within_precision_budget"])
        self.assertEqual(r["differences"]["solar_term"]["standard"], "惊蛰")
        self.assertEqual(r["differences"]["solar_term"]["true_solar"], "惊蛰")

    def test_compare_accepts_iso_string_input(self):
        r = compare_standard_vs_true_solar("2026-03-20T12:00:00+08:00",
                                           116.4074, 8)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["input"]["birth_local_time"],
                         "2026-03-20T12:00:00+08:00")

    def test_cross_day_backwards_urumqi_changes_day_pillar(self):
        """Urumqi 2026-01-01 00:30 CST -> previous day: day pillar changes."""
        birth = datetime(2026, 1, 1, 0, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        self.assertEqual(r["conversion"]["date_shift_days"], -1)
        self.assertTrue(r["differences"]["day_pillar_changed"])
        self.assertTrue(r["differences"]["chart_date"]["changed"])
        self.assertEqual(r["differences"]["chart_date"]["standard"], "2026-01-01")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2025-12-31")
        self.assertNotEqual(r["differences"]["pillars"]["day"]["standard"],
                            r["differences"]["pillars"]["day"]["true_solar"])

    def test_cross_day_forwards_new_york_local_date_only(self):
        """New York 2026-11-03 23:58 EST -> next LOCAL day, same pillar day.

        The conversion moves the local wall date forward a day
        (date_shift_days == +1), but pillars are computed from the
        Shanghai-converted instant, and both instants fall on Nov 4
        in Shanghai (12:58 -> 13:18 CST). A local-date shift therefore
        does NOT by itself change the day pillar; the day pillar
        changes only when the Shanghai date changes (next test).
        """
        birth = datetime(2026, 11, 3, 23, 58, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        self.assertEqual(r["conversion"]["date_shift_days"], 1)
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2026-11-04")
        self.assertFalse(r["differences"]["chart_date"]["changed"])
        self.assertFalse(r["differences"]["day_pillar_changed"])

    def test_cross_day_forwards_new_york_shanghai_midnight(self):
        """New York 2026-11-03 10:50 EST: Shanghai 23:50 -> 00:10 next day.

        The local date does NOT shift (10:50 -> 11:10 EST), but the
        Shanghai-converted instant crosses midnight, so the day pillar
        genuinely changes. Local date shift and pillar-day change are
        two different boundaries and are reported separately.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        self.assertEqual(r["conversion"]["date_shift_days"], 0)
        self.assertTrue(r["differences"]["chart_date"]["changed"])
        self.assertEqual(r["differences"]["chart_date"]["standard"], "2026-11-03")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2026-11-04")
        self.assertTrue(r["differences"]["day_pillar_changed"])


class TrueSolarChartBoundaryTests(unittest.TestCase):
    def test_longitude_plus_180_and_minus_180(self):
        """Dateline extremes: lon +/-180 on its own meridian -> EoT only.

        The same absolute instant is used on both sides (2026-03-20
        12:00 +12:00 == 2026-03-19 12:00 -12:00 == 00:00 UTC), so the
        equation of time must agree exactly. tz +12 wraps its meridian
        from +180 to -180 (the same meridian); the wrapped longitude
        difference then gives a zero correction on both sides.
        """
        instant_east = datetime(2026, 3, 20, 12, 0,
                                tzinfo=timezone(timedelta(hours=12)))
        instant_west = datetime(2026, 3, 19, 12, 0,
                                tzinfo=timezone(timedelta(hours=-12)))
        self.assertEqual(instant_east.astimezone(timezone.utc),
                         instant_west.astimezone(timezone.utc))
        r_east = compare_standard_vs_true_solar(instant_east, 180.0, 12)
        self.assertEqual(r_east["conversion"]["standard_meridian_deg"], -180.0)
        self.assertAlmostEqual(
            r_east["conversion"]["longitude_correction_minutes"], 0.0, places=9)
        self.assertAlmostEqual(
            r_east["conversion"]["total_correction_minutes"],
            r_east["conversion"]["equation_of_time_minutes"], places=9)
        r_west = compare_standard_vs_true_solar(instant_west, -180.0, -12)
        self.assertEqual(r_west["conversion"]["standard_meridian_deg"], -180.0)
        self.assertAlmostEqual(
            r_west["conversion"]["longitude_correction_minutes"], 0.0, places=9)
        # Same instant, same EoT on both sides of the dateline.
        self.assertAlmostEqual(
            r_east["conversion"]["equation_of_time_minutes"],
            r_west["conversion"]["equation_of_time_minutes"], places=9)

    def test_longitude_dateline_continuity(self):
        """No 24-hour jump at the dateline: 179.9 vs -179.9 differ by 0.8 min.

        Before the wrapped-difference fix, lon -180 against meridian
        120 gave -1200 min while lon +180 gave +240 min -- a 1440-min
        discontinuity for the same meridian. Both extremes now give
        +240 min, and neighbours 0.2 degrees apart differ by 0.8 min.
        """
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r_plus = compare_standard_vs_true_solar(birth, 180.0, 8)
        r_minus = compare_standard_vs_true_solar(birth, -180.0, 8)
        self.assertAlmostEqual(
            r_plus["conversion"]["longitude_correction_minutes"], 240.0,
            places=9)
        self.assertAlmostEqual(
            r_minus["conversion"]["longitude_correction_minutes"], 240.0,
            places=9)
        self.assertEqual(r_plus["conversion"]["apparent_solar_time"],
                         r_minus["conversion"]["apparent_solar_time"])
        r_east = compare_standard_vs_true_solar(birth, 179.9, 8)
        r_west = compare_standard_vs_true_solar(birth, -179.9, 8)
        gap = abs(r_east["conversion"]["longitude_correction_minutes"]
                  - r_west["conversion"]["longitude_correction_minutes"])
        self.assertAlmostEqual(gap, 0.8, places=6)

    def test_timezone_plus_14_and_minus_12(self):
        """tz +14 wraps its meridian to -150; tz -12 keeps -180."""
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=timezone.utc)
        r = compare_standard_vs_true_solar(
            birth, -150.0, 14,
            standard_meridian_deg=None)
        self.assertEqual(r["conversion"]["standard_meridian_deg"], -150.0)
        self.assertAlmostEqual(
            r["conversion"]["longitude_correction_minutes"], 0.0, places=9)
        r = compare_standard_vs_true_solar(birth, -180.0, -12)
        self.assertEqual(r["conversion"]["standard_meridian_deg"], -180.0)
        self.assertAlmostEqual(
            r["conversion"]["longitude_correction_minutes"], 0.0, places=9)

    def test_explicit_historical_meridian_is_not_guessed(self):
        """Caller-supplied historical meridian changes the correction.

        1926 Shanghai, lon 121.4737: meridian 121.4737 (caller-supplied
        historical value) zeroes the longitude correction, while the
        default 15 * tz_offset meridian (120) gives +5.89 min. The
        module asserts nothing about actual history; it only applies
        the parameters it is given, and never invents them.
        """
        birth = datetime(1926, 6, 15, 12, 0, tzinfo=CST)
        r_hist = compare_standard_vs_true_solar(
            birth, 121.4737, 8, standard_meridian_deg=121.4737)
        self.assertAlmostEqual(
            r_hist["conversion"]["longitude_correction_minutes"], 0.0, places=9)
        r_default = compare_standard_vs_true_solar(birth, 121.4737, 8)
        self.assertAlmostEqual(
            r_default["conversion"]["longitude_correction_minutes"],
            5.8948, places=3)
        self.assertNotEqual(
            r_hist["conversion"]["total_correction_minutes"],
            r_default["conversion"]["total_correction_minutes"])

    def test_explicit_dst_offset_governs(self):
        """tz_offset=+9 (DST in force) governs meridian and UTC instant."""
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 120.0, 9)
        self.assertEqual(r["conversion"]["tz_offset_hours"], 9.0)
        self.assertEqual(r["conversion"]["standard_meridian_deg"], 135.0)
        self.assertAlmostEqual(
            r["conversion"]["longitude_correction_minutes"], -60.0, places=9)

    def test_eot_extreme_days_at_entry_level(self):
        """11 Feb (EoT minimum) and 3 Nov (EoT maximum) via the entry."""
        r_feb = compare_standard_vs_true_solar(
            datetime(2026, 2, 11, 12, 0, tzinfo=UTC), 0.0, 0)
        self.assertAlmostEqual(
            r_feb["conversion"]["total_correction_minutes"], -14.2, delta=0.5)
        r_nov = compare_standard_vs_true_solar(
            datetime(2026, 11, 3, 12, 0, tzinfo=UTC), 0.0, 0)
        self.assertAlmostEqual(
            r_nov["conversion"]["total_correction_minutes"], 16.5, delta=0.5)


class TrueSolarChartJieqiTests(unittest.TestCase):
    def test_jieqi_crossed_backwards_lichun_urumqi(self):
        """Urumqi 2026-02-04 05:00 CST: apparent 02:36, before 立春.

        Standard chart is after 立春 (丙午/庚寅); the solar chart is
        before it (乙巳/己丑). Year AND month pillars change; the day
        pillar (己酉) does not.
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "丙午")
        self.assertEqual(d["year"]["true_solar"], "乙巳")
        self.assertEqual(d["month"]["standard"], "庚寅")
        self.assertEqual(d["month"]["true_solar"], "己丑")
        self.assertEqual(d["day"]["standard"], "己酉")
        self.assertEqual(d["day"]["true_solar"], "己酉")
        self.assertTrue(d["hour"]["changed"])
        self.assertTrue(r["differences"]["year_pillar_changed"])
        self.assertTrue(r["differences"]["month_pillar_changed"])
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "立春")
        self.assertEqual(j["standard_solar_term"], "立春")
        self.assertEqual(j["true_solar_solar_term"], "大寒")
        expected = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        got = datetime.fromisoformat(j["crossed_at_utc"])
        self.assertLess(abs((got - expected).total_seconds()), 60.0)
        # Input 05:00 is 57.9 min after the 04:02:08 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -57.87, delta=1.0)
        self.assertFalse(j["within_precision_budget"])

    def test_jieqi_crossed_forwards_lidong_new_york(self):
        """New York 2026-11-07 04:40 EST: apparent 05:00, past 立冬.

        立冬 is 2026-11-07 17:52:05 +08:00 = 04:52:05 EST; the
        standard instant (04:40 EST) is before it, the converted
        instant (05:00 EST) after it. Month pillar changes.
        """
        birth = datetime(2026, 11, 7, 4, 40, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "立冬")
        self.assertEqual(j["standard_solar_term"], "霜降")
        self.assertEqual(j["true_solar_solar_term"], "立冬")
        expected = _independent_jieqi_utc(2026, 11, 7, 12, 0, 0, "立冬")
        got = datetime.fromisoformat(j["crossed_at_utc"])
        self.assertLess(abs((got - expected).total_seconds()), 60.0)
        self.assertTrue(r["differences"]["month_pillar_changed"])
        # Converted instant is ~8.3 min past the boundary: outside the
        # +/-1 min precision budget, so the attribution is settled.
        self.assertFalse(j["within_precision_budget"])
        self.assertGreater(j["nearest_boundary_minutes"], 2.0)

    def test_jieqi_near_boundary_flagged_uncertain(self):
        """Converted instants within 2 min of 立春 are flagged, not settled.

        Urumqi 06:26 -> apparent 04:02:37, 0.5 min AFTER 立春 (not
        crossed, but inside the window); Urumqi 06:24 -> apparent
        04:00:37, 1.5 min BEFORE 立春 (crossed AND inside the window).
        Expected distances are recomputed independently here from the
        provider instant and the already-tested conversion.
        """
        lichun = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        for wall_hh, wall_mm, expect_crossed in ((6, 26, False), (6, 24, True)):
            with self.subTest(wall="%02d:%02d" % (wall_hh, wall_mm)):
                birth = datetime(2026, 2, 4, wall_hh, wall_mm, tzinfo=CST)
                r = compare_standard_vs_true_solar(birth, 87.62, 8)
                apparent = r["conversion"]["apparent_solar_time"]
                expected_distance = abs(
                    (apparent.astimezone(timezone.utc) - lichun)
                    .total_seconds()) / 60.0
                self.assertAlmostEqual(r["jieqi"]["nearest_boundary_minutes"],
                                       expected_distance, delta=0.1)
                self.assertEqual(r["jieqi"]["nearest_boundary_term"], "立春")
                self.assertEqual(r["jieqi"]["crossed"], expect_crossed)
                self.assertTrue(r["jieqi"]["within_precision_budget"])
                self.assertLess(
                    r["jieqi"]["nearest_boundary_minutes"],
                    JIEQI_UNCERTAINTY_WINDOW_MINUTES)
                self.assertIn("NOT settled", r["jieqi"]["note"])

    def test_jieqi_far_from_boundary_not_flagged(self):
        """A mid-month birth is far from any jieqi: no uncertainty flag."""
        r = compare_standard_vs_true_solar(
            datetime(2026, 3, 20, 12, 0, tzinfo=CST), 116.4074, 8)
        self.assertFalse(r["jieqi"]["within_precision_budget"])
        self.assertGreater(r["jieqi"]["nearest_boundary_minutes"], 60.0)


class TrueSolarChartFailClosedTests(unittest.TestCase):
    def test_fail_closed_inputs(self):
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(
                datetime(2026, 3, 20, 12, 0), 116.4074, 8)
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(birth, 181.0, 8)
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(birth, 116.4074, 15)
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(birth, 116.4074, 8.001)
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(
                birth, 116.4074, 8, standard_meridian_deg=200.0)

    def test_converted_instant_out_of_supported_range(self):
        """Urumqi 1900-01-01 00:05 converts back into 1899: refused."""
        with self.assertRaises(ValueError) as ctx:
            compare_standard_vs_true_solar(
                datetime(1900, 1, 1, 0, 5, tzinfo=CST), 87.62, 8)
        self.assertIn("outside the supported calendar range",
                      str(ctx.exception))

    def test_invalid_day_boundary_rejected(self):
        with self.assertRaises(ValueError):
            compare_standard_vs_true_solar(
                datetime(2026, 3, 20, 12, 0, tzinfo=CST), 116.4074, 8,
                day_boundary="noon")

