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

    def test_same_instant_same_apparent_whatever_representation(self):
        """Regression (ChatGPT review, batch 3): one physical instant,
        one apparent solar time, whatever representation it is written
        in. The equation of time used to be evaluated at
        wall-minus-offset while the shift was applied to dt's own
        instant, so the same birth gave different apparent times
        (and, near a jieqi moment, different solar terms) depending
        on whether it was written +08:00, UTC or -05:00.
        """
        reps = (
            datetime(2024, 2, 11, 16, 27, 7, tzinfo=CST),
            datetime(2024, 2, 11, 8, 27, 7, tzinfo=UTC),
            datetime(2024, 2, 11, 3, 27, 7,
                     tzinfo=timezone(timedelta(hours=-5))),
        )
        results = [apparent_solar_time(rep, 121.47, 8) for rep in reps]
        keys = ("apparent_solar_time", "input_date", "apparent_date",
                "date_shifted", "date_shift_days",
                "longitude_correction_minutes",
                "equation_of_time_minutes", "total_correction_minutes",
                "julian_day")
        first = {key: results[0][key] for key in keys}
        for rep, result in zip(reps[1:], results[1:]):
            with self.subTest(rep=rep.isoformat()):
                self.assertEqual(
                    {key: result[key] for key in keys}, first)

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
        """tz_offset=+9 governs the meridian and the returned zone.

        Same instant 12:00+08:00 (04:00Z), lon 120E: with tz_offset 9
        the standard meridian is 135E, so the longitude correction is
        exactly -60 min. The instant itself is dt's own (04:00Z):
        the equation of time and the Julian Day are evaluated at
        that instant, not at wall-minus-offset (03:00Z). (Batch 3
        correction: the old docstring claimed UTC was 03:00, but the
        asserted apparent value already pinned the 04:00Z instant;
        the EoT/JD pins below make the instant explicit.)
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
        self.assertAlmostEqual(
            r["equation_of_time_minutes"],
            equation_of_time_minutes(
                datetime(2026, 3, 20, 4, 0, tzinfo=UTC)),
            places=9)
        self.assertAlmostEqual(
            r["julian_day"],
            datetime(2026, 3, 20, 4, 0, tzinfo=UTC).timestamp()
            / 86400.0 + 2440587.5, places=9)

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
        """tz_offset=+9 (DST in force) governs the meridian.

        The instant is dt's own; tz_offset names the civil zone
        (meridian 135E here) and the zone of the returned apparent
        time. (Batch 3 correction: the old docstring claimed it
        also governed the UTC instant.)
        """
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



# ======================================================================
# TJ-0424 batch 3, P5: unified true-solar wiring (pillar adapter) +
# expanded coverage (more longitudes / time zones / cross-day cases /
# jieqi boundaries, incl. 年柱+月柱同变 and 节-vs-气 distinction).
#
# New independent EoT values below (2026-02-04, 2026-07-07,
# 2026-09-23, 2026-12-07) were derived exactly the way the batch-2
# table was: JPL DE421 via Skyfield 1.55, almanac.meridian_transits
# at Greenwich, EoT = 12:00 minus transit time. They reproduce the
# four batch-2 table values they overlap to within 0.017 min
# (2026-01-01 -3.550 vs -3.567; 2026-03-20 -7.433 vs -7.436;
# 2026-06-21 -1.817 vs -1.819; 2026-11-03 +16.450 vs +16.446).
# Expected apparent times are wall + 4*(lon - meridian) + EoT from
# that table, with the same 60 s tolerance as batch 2. Expected
# pillars were read off the pinned provider (lunar-python 1.4.8)
# directly, not off the module under test.
# ======================================================================

from tianji_kb.bazi_true_solar_chart import (
    compare_pillars,
    pillar_comparison,
)
from tianji_kb.bazi_true_solar_chart import (
    _lichun_near,
    _next_day_boundary,
    _next_shichen_boundary,
)

# (date, DE421 transit-derived EoT in minutes), batch-3 additions.
DE421_EOT_BATCH3 = (
    (datetime(2026, 2, 4), -13.867),
    (datetime(2026, 7, 7), -4.950),
    (datetime(2026, 9, 23), +7.633),
    (datetime(2026, 12, 7), +8.567),
)

JST = timezone(timedelta(hours=9))


class Batch3EoTTests(unittest.TestCase):
    def test_eot_additional_de421_dates(self):
        """EoT at 12:00 UTC matches JPL DE421 on four new dates."""
        for day, expected in DE421_EOT_BATCH3:
            with self.subTest(date=day.date().isoformat()):
                got = equation_of_time_minutes(
                    datetime(day.year, day.month, day.day, 12, 0,
                             tzinfo=UTC))
                self.assertAlmostEqual(got, expected, delta=EOT_TOL_MIN)


class MoreLongitudeTimezoneTests(unittest.TestCase):
    def _check(self, wall, lon, tz, expect_ast, expect_lon_corr,
               expect_eot, expect_shift):
        r = apparent_solar_time(wall, lon, tz)
        self.assertAlmostEqual(r["longitude_correction_minutes"],
                               expect_lon_corr, places=3)
        self.assertAlmostEqual(r["equation_of_time_minutes"],
                               expect_eot, delta=0.5)
        delta = abs((r["apparent_solar_time"] - expect_ast)
                    .total_seconds())
        self.assertLess(delta, 60.0)
        self.assertEqual(r["date_shift_days"], expect_shift)
        self.assertEqual(r["date_shifted"], expect_shift != 0)

    def test_sydney_dst_cross_day_backwards(self):
        """Sydney 151.2093E, +11 DST, 2026-01-01 00:30 -> prev day 23:31."""
        self._check(
            datetime(2026, 1, 1, 0, 30, tzinfo=timezone(timedelta(hours=11))),
            151.2093, 11,
            datetime(2025, 12, 31, 23, 31, 17,
                     tzinfo=timezone(timedelta(hours=11))),
            -55.1628, -3.550, -1)

    def test_tokyo_february(self):
        """Tokyo 139.767E, +9, 2026-02-04 05:01 -> ~05:06 (EoT -13.9)."""
        self._check(
            datetime(2026, 2, 4, 5, 1, tzinfo=JST), 139.767, 9,
            datetime(2026, 2, 4, 5, 6, 12, tzinfo=JST),
            19.068, -13.867, 0)

    def test_kathmandu_quarter_hour_zone(self):
        """Kathmandu 85.324E, +5:45 (meridian 86.25E): -3.7 min."""
        self._check(
            datetime(2026, 3, 20, 12, 0,
                     tzinfo=timezone(timedelta(hours=5, minutes=45))),
            85.324, 5.75,
            datetime(2026, 3, 20, 11, 48, 52,
                     tzinfo=timezone(timedelta(hours=5, minutes=45))),
            -3.704, -7.433, 0)

    def test_honolulu_cross_day_backwards(self):
        """Honolulu -157.858, -10, 2026-01-01 00:20 -> prev day 23:45."""
        self._check(
            datetime(2026, 1, 1, 0, 20, tzinfo=timezone(timedelta(hours=-10))),
            -157.858, -10,
            datetime(2025, 12, 31, 23, 45, 1,
                     tzinfo=timezone(timedelta(hours=-10))),
            -31.432, -3.550, -1)

    def test_auckland_meridian_wrap_plus_13(self):
        """Auckland 174.776E, +13: meridian 195E wraps to -165E."""
        r = apparent_solar_time(
            datetime(2026, 1, 1, 1, 0, tzinfo=timezone(timedelta(hours=13))),
            174.776, 13)
        self.assertEqual(r["standard_meridian_deg"], -165.0)
        self.assertAlmostEqual(r["longitude_correction_minutes"],
                               -80.896, places=3)
        self.assertAlmostEqual(r["equation_of_time_minutes"],
                               -3.550, delta=0.5)
        expect = datetime(2025, 12, 31, 23, 35, 33,
                          tzinfo=timezone(timedelta(hours=13)))
        self.assertLess(
            abs((r["apparent_solar_time"] - expect).total_seconds()), 60.0)
        self.assertEqual(r["date_shift_days"], -1)

    def test_mumbai_half_hour_zone(self):
        """Mumbai 72.8777E, +5:30 (meridian 82.5E): -38.5 min."""
        self._check(
            datetime(2026, 3, 20, 12, 0,
                     tzinfo=timezone(timedelta(hours=5, minutes=30))),
            72.8777, 5.5,
            datetime(2026, 3, 20, 11, 14, 5,
                     tzinfo=timezone(timedelta(hours=5, minutes=30))),
            -38.4892, -7.433, 0)

    def test_los_angeles_november(self):
        """Los Angeles -118.2437, -8, 2026-11-03 12:00 -> ~12:23."""
        self._check(
            datetime(2026, 11, 3, 12, 0, tzinfo=timezone(timedelta(hours=-8))),
            -118.2437, -8,
            datetime(2026, 11, 3, 12, 23, 29,
                     tzinfo=timezone(timedelta(hours=-8))),
            7.0252, 16.450, 0)

    def test_chatham_three_quarter_hour_zone(self):
        """Chatham -176.5, +12:45: meridian 191.25E wraps to -168.75E."""
        r = apparent_solar_time(
            datetime(2026, 1, 1, 12, 0,
                     tzinfo=timezone(timedelta(hours=12, minutes=45))),
            -176.5, 12.75)
        self.assertEqual(r["standard_meridian_deg"], -168.75)
        self.assertAlmostEqual(r["longitude_correction_minutes"],
                               -31.0, places=3)
        self.assertAlmostEqual(r["equation_of_time_minutes"],
                               -3.550, delta=0.5)
        expect = datetime(2026, 1, 1, 11, 25, 27,
                          tzinfo=timezone(timedelta(hours=12, minutes=45)))
        self.assertLess(
            abs((r["apparent_solar_time"] - expect).total_seconds()), 60.0)
        self.assertEqual(r["date_shift_days"], 0)


class TrueSolarChartMoreJieqiTests(unittest.TestCase):
    def test_jieqi_crossed_backwards_xiaoshu_urumqi(self):
        """Urumqi 2026-07-07 11:00 CST: apparent ~08:46, before 小暑.

        Month pillar changes 乙未 -> 甲午 (小暑 is a 节); year and
        day pillars do not change; hour pillar changes 丙午 -> 甲辰.
        """
        birth = datetime(2026, 7, 7, 11, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "丙午")
        self.assertEqual(d["year"]["true_solar"], "丙午")
        self.assertEqual(d["month"]["standard"], "乙未")
        self.assertEqual(d["month"]["true_solar"], "甲午")
        self.assertEqual(d["day"]["standard"], "壬午")
        self.assertEqual(d["day"]["true_solar"], "壬午")
        self.assertEqual(d["hour"]["standard"], "丙午")
        self.assertEqual(d["hour"]["true_solar"], "甲辰")
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "小暑")
        self.assertEqual(j["standard_solar_term"], "小暑")
        self.assertEqual(j["true_solar_solar_term"], "夏至")
        expected = _independent_jieqi_utc(2026, 7, 7, 12, 0, 0, "小暑")
        got = datetime.fromisoformat(j["crossed_at_utc"])
        self.assertLess(abs((got - expected).total_seconds()), 60.0)
        # Input 11:00 is 63.1 min after the 09:56:57 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -63.05, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 71.4, delta=2.0)

    def test_jieqi_crossed_backwards_daxue_urumqi(self):
        """Urumqi 2026-12-07 11:30 CST: apparent ~09:29, before 大雪.

        Month pillar changes 庚子 -> 己亥 (大雪 is a 节); day pillar
        does not change; hour pillar changes 壬午 -> 辛巳.
        """
        birth = datetime(2026, 12, 7, 11, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["month"]["standard"], "庚子")
        self.assertEqual(d["month"]["true_solar"], "己亥")
        self.assertEqual(d["day"]["standard"], "乙卯")
        self.assertEqual(d["day"]["true_solar"], "乙卯")
        self.assertEqual(d["hour"]["standard"], "壬午")
        self.assertEqual(d["hour"]["true_solar"], "辛巳")
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "大雪")
        self.assertEqual(j["standard_solar_term"], "大雪")
        self.assertEqual(j["true_solar_solar_term"], "小雪")
        expected = _independent_jieqi_utc(2026, 12, 7, 12, 0, 0, "大雪")
        got = datetime.fromisoformat(j["crossed_at_utc"])
        self.assertLess(abs((got - expected).total_seconds()), 60.0)
        # Input 11:30 is 37.5 min after the 10:52:32 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -37.47, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 83.5, delta=2.0)

    def test_jieqi_crossed_forwards_lichun_tokyo(self):
        """Tokyo 2026-02-04 05:01 JST: apparent ~05:06, past 立春.

        Forward 立春 crossing: year AND month pillars change
        together (乙巳/己丑 -> 丙午/庚寅); day and hour pillars do
        not change (己酉 / 丙寅 on both sides).
        """
        birth = datetime(2026, 2, 4, 5, 1, tzinfo=JST)
        r = compare_standard_vs_true_solar(birth, 139.767, 9)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "乙巳")
        self.assertEqual(d["year"]["true_solar"], "丙午")
        self.assertEqual(d["month"]["standard"], "己丑")
        self.assertEqual(d["month"]["true_solar"], "庚寅")
        self.assertEqual(d["day"]["standard"], "己酉")
        self.assertEqual(d["day"]["true_solar"], "己酉")
        self.assertEqual(d["hour"]["standard"], "丙寅")
        self.assertEqual(d["hour"]["true_solar"], "丙寅")
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "立春")
        self.assertEqual(j["standard_solar_term"], "大寒")
        self.assertEqual(j["true_solar_solar_term"], "立春")
        # Input 05:01 JST is 1.1 min before the 05:02:08 JST boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               1.13, delta=1.0)
        # Converted instant is ~4.1 min past the boundary: settled.
        self.assertFalse(j["within_precision_budget"])
        self.assertGreater(j["nearest_boundary_minutes"], 2.0)

    def test_qi_crossed_backwards_chunfen_month_unchanged(self):
        """Urumqi 2026-03-20 23:30 CST: apparent ~21:13, before 春分.

        春分 is a 中气: the solar term changes (春分 -> 惊蛰) but
        the month pillar does NOT change (辛卯 on both sides). The
        hour pillar changes 壬子 -> 癸亥; the day pillar does not.
        """
        birth = datetime(2026, 3, 20, 23, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["month"]["standard"], "辛卯")
        self.assertEqual(d["month"]["true_solar"], "辛卯")
        self.assertEqual(d["day"]["standard"], "癸巳")
        self.assertEqual(d["day"]["true_solar"], "癸巳")
        self.assertEqual(d["hour"]["standard"], "壬子")
        self.assertEqual(d["hour"]["true_solar"], "癸亥")
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "春分")
        self.assertEqual(j["standard_solar_term"], "春分")
        self.assertEqual(j["true_solar_solar_term"], "惊蛰")
        self.assertFalse(r["differences"]["month_pillar_changed"])
        self.assertTrue(r["differences"]["hour_pillar_changed"])
        # Input 23:30 is 44.0 min after the 22:45:59 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -44.02, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 92.9, delta=2.0)

    def test_qi_crossed_backwards_xiazhi_month_unchanged(self):
        """Urumqi 2026-06-21 17:30 CST: apparent ~15:19, before 夏至.

        夏至 is a 中气: term changes (夏至 -> 芒种), month pillar
        stays 甲午, day pillar stays 丙寅, hour changes 丁酉 -> 丙申.
        """
        birth = datetime(2026, 6, 21, 17, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["month"]["standard"], "甲午")
        self.assertEqual(d["month"]["true_solar"], "甲午")
        self.assertEqual(d["day"]["standard"], "丙寅")
        self.assertEqual(d["day"]["true_solar"], "丙寅")
        self.assertEqual(d["hour"]["standard"], "丁酉")
        self.assertEqual(d["hour"]["true_solar"], "丙申")
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "夏至")
        self.assertEqual(j["standard_solar_term"], "夏至")
        self.assertEqual(j["true_solar_solar_term"], "芒种")
        self.assertFalse(r["differences"]["month_pillar_changed"])
        # Input 17:30 is 65.5 min after the 16:24:30 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -65.5, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 65.8, delta=2.0)

    def test_qi_crossed_forwards_qiufen_only_term_changes(self):
        """Tokyo 2026-09-23 08:50 JST: apparent ~09:16, past 秋分.

        秋分 is a 中气: only the solar term changes (白露 -> 秋分).
        All four pillars are identical on both sides.
        """
        birth = datetime(2026, 9, 23, 8, 50, tzinfo=JST)
        r = compare_standard_vs_true_solar(birth, 139.767, 9)
        d = r["differences"]["pillars"]
        for name in ("year", "month", "day", "hour"):
            self.assertEqual(d[name]["standard"], d[name]["true_solar"],
                             name)
        self.assertEqual(d["month"]["standard"], "丁酉")
        self.assertEqual(d["day"]["standard"], "庚子")
        self.assertEqual(d["hour"]["standard"], "庚辰")
        self.assertFalse(r["differences"]["any_pillar_changed"])
        j = r["jieqi"]
        self.assertTrue(j["crossed"])
        self.assertEqual(j["crossed_term"], "秋分")
        self.assertEqual(j["standard_solar_term"], "白露")
        self.assertEqual(j["true_solar_solar_term"], "秋分")
        # Input 08:50 JST is 15.2 min before the 09:05:14 JST boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               15.23, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 11.5, delta=2.0)

    def test_cross_day_backwards_sydney_local_date_only(self):
        """Sydney 2026-01-01 00:30 +11: local date shifts back a day.

        The local date shifts (date_shift_days == -1) but both
        instants fall on 2025-12-31 in Shanghai, so the day pillar
        does NOT change; only the hour pillar changes (乙亥 -> 甲戌).
        """
        birth = datetime(2026, 1, 1, 0, 30,
                         tzinfo=timezone(timedelta(hours=11)))
        r = compare_standard_vs_true_solar(birth, 151.2093, 11)
        self.assertEqual(r["conversion"]["date_shift_days"], -1)
        self.assertEqual(r["differences"]["chart_date"]["standard"],
                         "2025-12-31")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"],
                         "2025-12-31")
        self.assertFalse(r["differences"]["chart_date"]["changed"])
        self.assertFalse(r["differences"]["day_pillar_changed"])
        d = r["differences"]["pillars"]
        self.assertEqual(d["day"]["standard"], "甲戌")
        self.assertEqual(d["day"]["true_solar"], "甲戌")
        self.assertEqual(d["hour"]["standard"], "乙亥")
        self.assertEqual(d["hour"]["true_solar"], "甲戌")
        self.assertFalse(r["jieqi"]["crossed"])

    def test_cross_day_backwards_honolulu_no_pillar_change(self):
        """Honolulu 2026-01-01 00:20 -10: local date shifts, no pillar.

        Local date shifts back a day (date_shift_days == -1), yet
        all four pillars are identical: both instants fall on
        2026-01-01 in Shanghai, far from every boundary.
        """
        birth = datetime(2026, 1, 1, 0, 20,
                         tzinfo=timezone(timedelta(hours=-10)))
        r = compare_standard_vs_true_solar(birth, -157.858, -10)
        self.assertEqual(r["conversion"]["date_shift_days"], -1)
        self.assertFalse(r["differences"]["any_pillar_changed"])
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "乙巳")
        self.assertEqual(d["month"]["standard"], "戊子")
        self.assertEqual(d["day"]["standard"], "乙亥")
        self.assertEqual(d["hour"]["standard"], "乙酉")
        self.assertFalse(r["jieqi"]["crossed"])

    def test_zi_start_day_boundary_contrast(self):
        """NY 2026-11-03 10:50 EST under midnight vs zi-start.

        Shanghai 23:50 -> 00:10 next day. Under the midnight
        convention the day pillar changes (辛巳 -> 壬午); under
        zi-start the day starts at 23:00, so both instants are
        already on the next day and the day pillar is 壬午 on both
        sides. Same birth, same conversion, different day boundary.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r_mid = compare_standard_vs_true_solar(
            birth, -74.0060, -5, day_boundary="midnight")
        self.assertTrue(r_mid["differences"]["day_pillar_changed"])
        self.assertEqual(
            r_mid["differences"]["pillars"]["day"]["standard"], "辛巳")
        self.assertEqual(
            r_mid["differences"]["pillars"]["day"]["true_solar"], "壬午")
        r_zi = compare_standard_vs_true_solar(
            birth, -74.0060, -5, day_boundary="zi-start")
        self.assertFalse(r_zi["differences"]["day_pillar_changed"])
        self.assertEqual(
            r_zi["differences"]["pillars"]["day"]["standard"], "壬午")
        self.assertEqual(
            r_zi["differences"]["pillars"]["day"]["true_solar"], "壬午")
        # The conversion itself is identical under both conventions.
        self.assertEqual(r_mid["conversion"], r_zi["conversion"])


class PillarAdapterTests(unittest.TestCase):
    def _rows(self, result):
        return {row["name"]: row
                for row in result["pillar_comparison"]["pillars"]}

    def test_adapter_contract_flags(self):
        r = compare_pillars(datetime(2026, 3, 20, 12, 0, tzinfo=CST),
                            116.4074, 8)
        pc = r["pillar_comparison"]
        self.assertEqual(pc["adapter"], "true-solar-pillar-adapter-v1")
        self.assertEqual(pc["entry"], ENTRY_ID)
        self.assertEqual(pc["method"], "modern_engineering")
        self.assertTrue(pc["research_only"])
        self.assertFalse(pc["public"])
        self.assertFalse(pc["ai"])
        self.assertEqual(pc["status"], "ok")
        self.assertIn("recomputes nothing", pc["reuse_note"])
        self.assertIn("pillar_comparison", r)
        # The underlying comparison is untouched by the adapter.
        self.assertEqual(r["standard_time_chart"],
                         compare_standard_vs_true_solar(
                             datetime(2026, 3, 20, 12, 0, tzinfo=CST),
                             116.4074, 8)["standard_time_chart"])

    def test_adapter_copies_charts_verbatim(self):
        """Adapter rows are the real charts' pillar dicts, not recomputed."""
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        apparent = r["conversion"]["apparent_solar_time"]
        std_pillars = {item["name"]: item
                       for item in chart_from_datetime(birth)["pillars"]}
        sol_pillars = {item["name"]: item
                       for item in chart_from_datetime(apparent)["pillars"]}
        for row in r["pillar_comparison"]["pillars"]:
            self.assertEqual(row["standard"], std_pillars[row["name"]])
            self.assertEqual(row["true_solar"], sol_pillars[row["name"]])
            # Each row carries the deterministic derivations: stem
            # ten god and hidden stems with ten gods.
            for side in ("standard", "true_solar"):
                self.assertIn("ten_god", row[side]["stem"])
                self.assertIn("hidden_stems", row[side]["branch"])
                self.assertTrue(row[side]["branch"]["hidden_stems"])

    def test_adapter_beijing_no_change(self):
        """Beijing noon: no pillar changes; reasons name the boundaries."""
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = compare_pillars(birth, 116.4074, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        for name in ("year", "month", "day", "hour"):
            self.assertFalse(rows[name]["changed"], name)
            self.assertFalse(rows[name]["ten_god_reading_changed"], name)
        self.assertFalse(pc["day_master"]["changed"])
        self.assertEqual(pc["day_master"]["standard"]["stem"], "癸")
        self.assertFalse(pc["year_and_month_changed_together"])
        self.assertTrue(pc["month_attribution_settled"])
        self.assertEqual(pc["month_attribution"], "settled")
        self.assertFalse(pc["derived"]["branch_relations_changed"])
        self.assertFalse(pc["derived"]["taohua_changed"])
        self.assertIn("立春", rows["year"]["reason"])
        self.assertIn("No jieqi was crossed", rows["month"]["reason"])
        self.assertIn("Shanghai date is unchanged",
                      rows["day"]["reason"])
        self.assertIn("shichen is unchanged", rows["hour"]["reason"])
        # Boundary distances: next shichen 13:00 is 60 min after the
        # standard instant, ~82 min after the converted instant.
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_standard_instant_to_next_shichen_boundary"],
            60.0, delta=2.0)
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_converted_instant_to_next_shichen_boundary"],
            81.9, delta=2.0)
        self.assertAlmostEqual(
            rows["day"]["detail"]
            ["minutes_from_standard_instant_to_next_boundary"],
            720.0, delta=2.0)

    def test_adapter_lichun_urumqi_year_month_together(self):
        """Urumqi 立春 crossing: year+month change together, reasons say why."""
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertTrue(pc["year_and_month_changed_together"])
        self.assertTrue(rows["year"]["changed"])
        self.assertTrue(rows["month"]["changed"])
        self.assertFalse(rows["day"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertIn("立春", rows["year"]["reason"])
        self.assertIn("only at 立春", rows["year"]["reason"])
        self.assertIn("节", rows["month"]["reason"])
        self.assertEqual(rows["month"]["detail"]["crossed_term"], "立春")
        self.assertEqual(rows["month"]["detail"]["crossed_term_kind"], "节")
        self.assertIn("Shanghai date is unchanged", rows["day"]["reason"])
        self.assertIn("shichen changed", rows["hour"]["reason"])
        # Standard 05:00 is 卯时 (丁卯）; the ~143 min backward
        # conversion lands ~02:36, i.e. 丑时 (乙丑）.
        self.assertIn("卯时", rows["hour"]["reason"])
        self.assertIn("丑时", rows["hour"]["reason"])
        # Day master is 己 on both sides: ten-god readings agree
        # wherever the pillar itself is unchanged.
        self.assertFalse(pc["day_master"]["changed"])
        self.assertEqual(pc["day_master"]["standard"]["stem"], "己")
        self.assertFalse(rows["day"]["ten_god_reading_changed"])
        self.assertTrue(rows["year"]["ten_god_reading_changed"])
        self.assertTrue(pc["derived"]["branch_relations_changed"])
        self.assertTrue(pc["derived"]["taohua_changed"])
        self.assertTrue(pc["month_attribution_settled"])
        self.assertIn("changed together", pc["note"])

    def test_adapter_lichun_forward_tokyo(self):
        """Tokyo forward 立春 crossing: same together-flag, hour unchanged."""
        birth = datetime(2026, 2, 4, 5, 1, tzinfo=JST)
        r = compare_pillars(birth, 139.767, 9)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertTrue(pc["year_and_month_changed_together"])
        self.assertTrue(rows["year"]["changed"])
        self.assertTrue(rows["month"]["changed"])
        self.assertFalse(rows["day"]["changed"])
        self.assertFalse(rows["hour"]["changed"])
        self.assertIn("立春", rows["year"]["reason"])
        self.assertIn("寅时", rows["hour"]["reason"])
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_standard_instant_to_next_shichen_boundary"],
            59.0, delta=2.0)
        self.assertTrue(pc["month_attribution_settled"])

    def test_adapter_qi_crossing_chunfen(self):
        """春分 crossing: term changes, month pillar does not (中气)."""
        birth = datetime(2026, 3, 20, 23, 30, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertFalse(rows["month"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertIn("中气", rows["month"]["reason"])
        self.assertIn("month pillar changes only at 节 boundaries",
                      rows["month"]["reason"])
        self.assertEqual(rows["month"]["detail"]["crossed_term"], "春分")
        self.assertEqual(rows["month"]["detail"]["crossed_term_kind"], "气")
        self.assertFalse(pc["year_and_month_changed_together"])
        self.assertTrue(pc["month_attribution_settled"])

    def test_adapter_qi_crossing_qiufen_only_term_changes(self):
        """秋分 forward crossing: no pillar changes at all."""
        birth = datetime(2026, 9, 23, 8, 50, tzinfo=JST)
        r = compare_pillars(birth, 139.767, 9)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        for name in ("year", "month", "day", "hour"):
            self.assertFalse(rows[name]["changed"], name)
        self.assertTrue(r["jieqi"]["crossed"])
        self.assertEqual(r["jieqi"]["crossed_term"], "秋分")
        self.assertIn("中气", rows["month"]["reason"])
        self.assertTrue(pc["month_attribution_settled"])

    def test_adapter_day_master_change_cascade(self):
        """Urumqi 2026-01-01 00:30: day pillar changes, day master 乙->甲.

        The day-master change recomputes the ten-god reading of
        every pillar: the year and month pillars are unchanged as
        ganzhi, yet their ten-god readings differ between the sides.
        """
        birth = datetime(2026, 1, 1, 0, 30, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertTrue(pc["day_master"]["changed"])
        self.assertEqual(pc["day_master"]["standard"]["stem"], "乙")
        self.assertEqual(pc["day_master"]["true_solar"]["stem"], "甲")
        self.assertTrue(rows["day"]["changed"])
        self.assertEqual(rows["day"]["standard"]["ganzhi"], "乙亥")
        self.assertEqual(rows["day"]["true_solar"]["ganzhi"], "甲戌")
        self.assertTrue(rows["hour"]["changed"])
        # Unchanged pillars, changed ten-god readings: the cascade.
        self.assertFalse(rows["year"]["changed"])
        self.assertTrue(rows["year"]["ten_god_reading_changed"])
        self.assertFalse(rows["month"]["changed"])
        self.assertTrue(rows["month"]["ten_god_reading_changed"])
        self.assertIn("recomputed", pc["note"])
        self.assertIn("Shanghai date changed", rows["day"]["reason"])
        self.assertIn("2025-12-31", rows["day"]["reason"])

    def test_adapter_within_budget_month_undetermined(self):
        """Within the 2-minute window: 月令归属未定 (status quo, T1).

        Urumqi 06:24 -> apparent 04:00:37, 1.5 min BEFORE 立春
        (crossed AND inside the window); Urumqi 06:26 -> apparent
        04:02:37, 0.5 min AFTER 立春 (not crossed, inside the
        window). Both keep the month attribution undetermined.
        """
        for wall_hh, wall_mm, expect_crossed in ((6, 24, True),
                                                 (6, 26, False)):
            with self.subTest(wall="%02d:%02d" % (wall_hh, wall_mm)):
                birth = datetime(2026, 2, 4, wall_hh, wall_mm, tzinfo=CST)
                r = compare_pillars(birth, 87.62, 8)
                pc = r["pillar_comparison"]
                self.assertEqual(r["jieqi"]["crossed"], expect_crossed)
                self.assertTrue(r["jieqi"]["within_precision_budget"])
                self.assertFalse(pc["month_attribution_settled"])
                self.assertEqual(pc["month_attribution"], "undetermined")
                self.assertIn("月令归属未定", pc["note"])
                self.assertIn("NOT settled",
                              self._rows(r)["month"]["reason"])
                self.assertFalse(
                    self._rows(r)["year"]["detail"]["attribution_settled"])

    def test_adapter_zi_start_day_unchanged(self):
        """NY case under zi-start: day row unchanged, reason names 23:00."""
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r_zi = compare_pillars(birth, -74.0060, -5, day_boundary="zi-start")
        rows_zi = self._rows(r_zi)
        self.assertFalse(rows_zi["day"]["changed"])
        self.assertIn("23:00", rows_zi["day"]["reason"])
        self.assertEqual(
            rows_zi["day"]["detail"]["governing_boundary"],
            "shanghai_zi_start_23h")
        r_mid = compare_pillars(birth, -74.0060, -5, day_boundary="midnight")
        rows_mid = self._rows(r_mid)
        self.assertTrue(rows_mid["day"]["changed"])
        self.assertIn("00:00", rows_mid["day"]["reason"])
        self.assertEqual(
            rows_mid["day"]["detail"]["governing_boundary"],
            "shanghai_midnight")

    def test_adapter_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            pillar_comparison({})
        with self.assertRaises(ValueError):
            pillar_comparison({"standard_time_chart": {}})
        with self.assertRaises(ValueError):
            compare_pillars(datetime(2026, 3, 20, 12, 0), 116.4074, 8)


class PillarAdapterHelperTests(unittest.TestCase):
    def test_next_shichen_boundary(self):
        shanghai = timezone(timedelta(hours=8))
        wall = datetime(2026, 3, 20, 12, 0, tzinfo=shanghai)
        nxt, hour = _next_shichen_boundary(wall)
        self.assertEqual((nxt.hour, nxt.minute), (13, 0))
        wall = datetime(2026, 3, 20, 23, 30, tzinfo=shanghai)
        nxt, hour = _next_shichen_boundary(wall)
        self.assertEqual(nxt.day, 21)
        self.assertEqual((nxt.hour, nxt.minute), (1, 0))
        wall = datetime(2026, 3, 20, 9, 0, tzinfo=shanghai)
        nxt, hour = _next_shichen_boundary(wall)
        self.assertEqual((nxt.hour, nxt.minute), (11, 0))
        wall = datetime(2026, 3, 20, 0, 10, tzinfo=shanghai)
        nxt, hour = _next_shichen_boundary(wall)
        self.assertEqual((nxt.hour, nxt.minute), (1, 0))

    def test_next_day_boundary(self):
        shanghai = timezone(timedelta(hours=8))
        wall = datetime(2026, 11, 3, 23, 50, tzinfo=shanghai)
        nxt, label = _next_day_boundary(wall, "midnight")
        self.assertEqual((nxt.day, nxt.hour), (4, 0))
        self.assertEqual(label, "00:00")
        nxt, label = _next_day_boundary(wall, "zi-start")
        self.assertEqual((nxt.day, nxt.hour), (4, 23))
        self.assertEqual(label, "23:00")
        wall = datetime(2026, 11, 3, 22, 30, tzinfo=shanghai)
        nxt, label = _next_day_boundary(wall, "zi-start")
        self.assertEqual((nxt.day, nxt.hour), (3, 23))

    def test_lichun_near(self):
        found = _lichun_near(datetime(2026, 2, 4, 5, 0, tzinfo=UTC))
        isos = [moment.isoformat() for moment in found]
        self.assertIn("2026-02-03T20:02:08+00:00", isos)
        self.assertIn("2025-02-03T14:10:28+00:00", isos)
        self.assertIn("2027-02-04T01:46:18+00:00", isos)
        self.assertEqual(isos, sorted(isos))


# ======================================================================
# TJ-0424 batch 3, T1-T4 adjudicated (2026-11-25 14:41).
#
# T1: the 2-minute jieqi window is PROVISIONAL (NOAA +/-1 min budget
# + 1 min margin), not a proven maximum error; near-boundary cases
# are verified here, including the exact flip at the window edge.
# T2: the +/-180 longitude wrap is approved as the formal dateline
# convention; local date, time-zone and cross-day results are
# verified here with a cross-day pair at the dateline.
# T3: IANA tzdb validates supplied offsets (match / mismatch /
# LMT-era); coverage and uncertainty are stated per call.
# T4: the research API entry research_dual_time_chart (function
# level) plus the admin-backend comparison function compare_pillars;
# the key invariant is representation invariance -- the same
# physical instant always carries the same solar term, and a term
# changes between the two charts only when a jieqi moment lies
# strictly between the standard and the converted instants.
# ======================================================================

from tianji_kb.bazi_true_solar_chart import (
    JIEQI_WINDOW_ADJUDICATION,
    JIEQI_WINDOW_STATUS,
    RESEARCH_API_ID,
    research_dual_time_chart,
)
from tianji_kb.bazi_true_solar_time import (
    TZDB_COVERAGE_NOTE,
    tzdb_offset_hours,
    tzdb_version,
    validate_tz_offset,
)


class T1WindowEdgeTests(unittest.TestCase):
    def test_window_is_provisional_two_minutes(self):
        self.assertEqual(JIEQI_UNCERTAINTY_WINDOW_MINUTES, 2.0)
        self.assertEqual(JIEQI_WINDOW_STATUS, "provisional")
        self.assertIn("T1", JIEQI_WINDOW_ADJUDICATION)
        self.assertIn("provisional", JIEQI_WINDOW_ADJUDICATION)
        self.assertIn("not a proven maximum error",
                      JIEQI_WINDOW_ADJUDICATION)

    def test_window_edge_flip_at_lichun(self):
        """Sweep wall 06:23-06:28 across 立春: flag flips at 2.0 min.

        Urumqi 2026-02-04, lon 87.62: each wall minute moves the
        apparent instant ~1 min. The flag must equal
        (nearest_boundary_minutes < 2.0) at every step, must be
        True on both sides of the boundary while inside, and must
        flip to False once the converted instant is 2+ min away --
        on both the before and the after side.
        """
        lichun = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        seen_inside = seen_outside = 0
        for wall_mm in (23, 24, 25, 26, 27, 28):
            with self.subTest(wall="06:%02d" % wall_mm):
                birth = datetime(2026, 2, 4, 6, wall_mm, tzinfo=CST)
                r = compare_standard_vs_true_solar(birth, 87.62, 8)
                j = r["jieqi"]
                self.assertEqual(j["nearest_boundary_term"], "立春")
                self.assertEqual(j["uncertainty_window_status"],
                                 "provisional")
                self.assertIn("T1", j["uncertainty_window_adjudication"])
                # Distance recomputed independently from the provider
                # instant and the already-tested conversion.
                apparent = r["conversion"]["apparent_solar_time"]
                expected_distance = abs(
                    (apparent.astimezone(timezone.utc) - lichun)
                    .total_seconds()) / 60.0
                self.assertAlmostEqual(j["nearest_boundary_minutes"],
                                       expected_distance, delta=0.1)
                self.assertEqual(j["within_precision_budget"],
                                 expected_distance < 2.0)
                if j["within_precision_budget"]:
                    seen_inside += 1
                    self.assertIn("NOT settled", j["note"])
                    self.assertIn("provisional", j["note"])
                    self.assertIn("not a proven maximum error", j["note"])
                else:
                    seen_outside += 1
                    self.assertIn("provisional", j["note"])
        self.assertGreater(seen_inside, 0)
        self.assertGreater(seen_outside, 0)

    def test_just_outside_window_is_settled(self):
        """Wall 06:28 -> apparent ~04:04:37, ~2.5 min past 立春: settled."""
        birth = datetime(2026, 2, 4, 6, 28, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        self.assertFalse(r["jieqi"]["within_precision_budget"])
        self.assertGreater(r["jieqi"]["nearest_boundary_minutes"], 2.0)
        self.assertEqual(r["jieqi"]["uncertainty_window_status"],
                         "provisional")
        pc = compare_pillars(birth, 87.62, 8)["pillar_comparison"]
        self.assertTrue(pc["month_attribution_settled"])


class T2DatelineCrossDayTests(unittest.TestCase):
    def test_dateline_cross_day_pair(self):
        """Same wall time, lon +179.9 vs -179.9, tz 0: a ~24 h split.

        2026-03-20 00:05 UTC: +179.9 corrects +719.6 min (EoT
        ~-7.4) and stays on Mar 20; -179.9 corrects -719.6 min and
        falls back to Mar 19. The two apparent instants differ by
        1439.2 min (24 h minus the 0.8 min dateline-neighbour gap):
        no 1440-minute jump, no silently shared date.
        """
        birth = datetime(2026, 3, 20, 0, 5, tzinfo=UTC)
        r_east = apparent_solar_time(birth, 179.9, 0)
        r_west = apparent_solar_time(birth, -179.9, 0)
        self.assertAlmostEqual(
            r_east["longitude_correction_minutes"], 719.6, places=3)
        self.assertAlmostEqual(
            r_west["longitude_correction_minutes"], -719.6, places=3)
        self.assertEqual(r_east["date_shift_days"], 0)
        self.assertEqual(r_west["date_shift_days"], -1)
        self.assertEqual(r_east["apparent_date"], "2026-03-20")
        self.assertEqual(r_west["apparent_date"], "2026-03-19")
        gap = abs((r_east["apparent_solar_time"]
                   - r_west["apparent_solar_time"]).total_seconds()) / 60.0
        self.assertAlmostEqual(gap, 1439.2, delta=1.0)

    def test_dateline_cross_day_chart_dates(self):
        """Chart-level: the -179.9 side changes Shanghai day, +179.9 not.

        Standard instant 00:05 UTC is 08:05 Shanghai Mar 20. The
        -179.9 converted instant is Mar 19 11:58 UTC (19:58 Shanghai
        Mar 19): the day pillar changes. The +179.9 converted
        instant is Mar 20 11:57 UTC (19:57 Shanghai Mar 20): the
        Shanghai date -- and the day pillar -- do not change.
        """
        birth = datetime(2026, 3, 20, 0, 5, tzinfo=UTC)
        r_west = compare_standard_vs_true_solar(birth, -179.9, 0)
        self.assertTrue(r_west["differences"]["day_pillar_changed"])
        self.assertTrue(r_west["differences"]["chart_date"]["changed"])
        self.assertEqual(
            r_west["differences"]["chart_date"]["standard"], "2026-03-20")
        self.assertEqual(
            r_west["differences"]["chart_date"]["true_solar"], "2026-03-19")
        r_east = compare_standard_vs_true_solar(birth, 179.9, 0)
        self.assertFalse(r_east["differences"]["day_pillar_changed"])
        self.assertFalse(r_east["differences"]["chart_date"]["changed"])

    def test_same_instant_plus_minus_180_same_apparent(self):
        """T2: lon +180 and -180 are one meridian -- identical result."""
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r_plus = apparent_solar_time(birth, 180.0, 8)
        r_minus = apparent_solar_time(birth, -180.0, 8)
        self.assertEqual(r_plus["apparent_solar_time"],
                         r_minus["apparent_solar_time"])
        self.assertEqual(r_plus["date_shift_days"],
                         r_minus["date_shift_days"])


class TzdbValidationTests(unittest.TestCase):
    def test_tzdb_version_is_reported(self):
        version = tzdb_version()
        self.assertIsInstance(version, str)
        self.assertTrue(version)
        self.assertIn("local mean time", TZDB_COVERAGE_NOTE)
        self.assertIn("versioned", TZDB_COVERAGE_NOTE)

    def test_shanghai_modern_match(self):
        for year in (1926, 1949, 2026):
            with self.subTest(year=year):
                v = validate_tz_offset(
                    "Asia/Shanghai",
                    datetime(year, 6, 15, 12, 0, tzinfo=UTC), 8)
                self.assertEqual(v["status"], "match")
                self.assertTrue(v["matches"])
                self.assertEqual(v["tzdb_offset_hours"], 8.0)
                self.assertTrue(v["tzdb_offset_is_whole_minutes"])
                self.assertEqual(v["tzdb_offset"], "+08:00")
                self.assertTrue(v["tzdb_version"])
                self.assertIn("consistency check", v["uncertainty"])

    def test_kathmandu_historical_mismatch(self):
        """Kathmandu was +05:30 in 1926, +05:45 today: 5.75 mismatches."""
        v = validate_tz_offset(
            "Asia/Kathmandu",
            datetime(1926, 6, 15, 12, 0, tzinfo=UTC), 5.75)
        self.assertEqual(v["status"], "mismatch")
        self.assertFalse(v["matches"])
        self.assertEqual(v["tzdb_offset_hours"], 5.5)
        self.assertEqual(v["tzdb_offset"], "+05:30")
        v = validate_tz_offset(
            "Asia/Kathmandu",
            datetime(2026, 6, 15, 12, 0, tzinfo=UTC), 5.75)
        self.assertEqual(v["status"], "match")

    def test_new_york_dst_state(self):
        """2026-11-07 04:40 EST is -05:00 (DST ended Nov 1)."""
        v = validate_tz_offset(
            "America/New_York",
            datetime(2026, 11, 7, 9, 40, tzinfo=UTC), -5)
        self.assertEqual(v["status"], "match")
        self.assertEqual(v["tzdb_offset_hours"], -5.0)
        v = validate_tz_offset(
            "America/New_York",
            datetime(2026, 11, 7, 9, 40, tzinfo=UTC), -4)
        self.assertEqual(v["status"], "mismatch")

    def test_shanghai_lmt_era(self):
        """Asia/Shanghai before 1901 is LMT +08:05:43: not validatable."""
        v = validate_tz_offset(
            "Asia/Shanghai",
            datetime(1899, 6, 15, 12, 0, tzinfo=UTC), 8)
        self.assertEqual(v["status"], "lmt_era")
        self.assertFalse(v["matches"])
        self.assertFalse(v["tzdb_offset_is_whole_minutes"])
        self.assertEqual(v["tzdb_offset"], "+08:05:43")
        self.assertAlmostEqual(v["tzdb_offset_hours"], 8.0953, places=3)
        self.assertIn("local mean time", v["uncertainty"])
        self.assertIn("never be rounded", v["uncertainty"])

    def test_tzdb_offset_hours_values(self):
        self.assertEqual(
            tzdb_offset_hours(
                "Asia/Shanghai", datetime(2026, 3, 20, 12, 0, tzinfo=UTC)),
            8.0)
        self.assertEqual(
            tzdb_offset_hours(
                "Asia/Kathmandu", datetime(2026, 6, 15, 12, 0, tzinfo=UTC)),
            5.75)
        self.assertEqual(
            tzdb_offset_hours(
                "Pacific/Auckland",
                datetime(2026, 3, 20, 12, 0, tzinfo=UTC)),
            13.0)

    def test_validation_fail_closed_inputs(self):
        with self.assertRaises(ValueError):
            validate_tz_offset(
                "Mars/Olympus",
                datetime(2026, 3, 20, 12, 0, tzinfo=UTC), 8)
        with self.assertRaises(ValueError):
            validate_tz_offset(
                "Asia/Shanghai", datetime(2026, 3, 20, 12, 0), 8)
        with self.assertRaises(ValueError):
            validate_tz_offset(
                "Asia/Shanghai",
                datetime(2026, 3, 20, 12, 0, tzinfo=UTC), 8.001)
        with self.assertRaises(ValueError):
            tzdb_offset_hours("Asia/Shanghai",
                              datetime(2026, 3, 20, 12, 0))


class ResearchApiEntryTests(unittest.TestCase):
    def test_research_entry_tz_name_only(self):
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = research_dual_time_chart(
            birth, 116.4074, tz_name="Asia/Shanghai")
        self.assertEqual(r["research_api"], RESEARCH_API_ID)
        self.assertTrue(r["research_only"])
        self.assertFalse(r["public"])
        self.assertFalse(r["ai"])
        self.assertEqual(r["tz_validation"]["status"],
                         "resolved_from_tzdb")
        self.assertEqual(r["tz_validation"]["tzdb_offset_hours"], 8.0)
        self.assertEqual(r["tz_validation"]["tz_name"], "Asia/Shanghai")
        self.assertIn("pillar_comparison", r)
        self.assertEqual(r["provenance"]["research_api"], RESEARCH_API_ID)
        self.assertEqual(r["provenance"]["jieqi_window_status"],
                         "provisional")
        self.assertTrue(r["provenance"]["tzdb_version"])
        # Standard chart identical to chart_from_datetime(birth).
        self.assertEqual(r["standard_time_chart"],
                         chart_from_datetime(birth))
        # Same as compare_pillars with the resolved offset.
        twin = compare_pillars(birth, 116.4074, 8)
        self.assertEqual(r["standard_time_chart"],
                         twin["standard_time_chart"])
        self.assertEqual(r["true_solar_time_chart"],
                         twin["true_solar_time_chart"])
        self.assertEqual(r["pillar_comparison"],
                         twin["pillar_comparison"])

    def test_research_entry_tz_offset_only(self):
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = research_dual_time_chart(birth, 116.4074, tz_offset=8)
        self.assertEqual(r["tz_validation"]["status"], "not_requested")
        self.assertIn("pillar_comparison", r)
        self.assertEqual(r["research_api"], RESEARCH_API_ID)

    def test_research_entry_both_matching(self):
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = research_dual_time_chart(
            birth, 116.4074, tz_name="Asia/Shanghai", tz_offset=8)
        self.assertEqual(r["tz_validation"]["status"], "match")
        self.assertTrue(r["tz_validation"]["matches"])

    def test_research_entry_mismatch_refused(self):
        with self.assertRaises(ValueError) as ctx:
            research_dual_time_chart(
                datetime(1926, 6, 15, 12, 0, tzinfo=CST), 85.324,
                tz_name="Asia/Kathmandu", tz_offset=5.75)
        self.assertIn("mismatch", str(ctx.exception))
        self.assertIn("+05:30", str(ctx.exception))

    def test_research_entry_lmt_era_refused(self):
        # tz_name only: LMT resolves to no usable offset.
        with self.assertRaises(ValueError) as ctx:
            research_dual_time_chart(
                datetime(1899, 6, 15, 12, 0, tzinfo=CST), 121.4737,
                tz_name="Asia/Shanghai")
        self.assertIn("local mean time", str(ctx.exception))
        # Both given: LMT era cannot validate the supplied offset.
        with self.assertRaises(ValueError) as ctx:
            research_dual_time_chart(
                datetime(1899, 6, 15, 12, 0, tzinfo=CST), 121.4737,
                tz_name="Asia/Shanghai", tz_offset=8)
        self.assertIn("local mean time", str(ctx.exception))

    def test_research_entry_fail_closed_inputs(self):
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        with self.assertRaises(ValueError):
            research_dual_time_chart(birth, 116.4074)
        with self.assertRaises(ValueError):
            research_dual_time_chart(
                birth, 116.4074, tz_name="Mars/Olympus")
        with self.assertRaises(ValueError):
            research_dual_time_chart(
                datetime(2026, 3, 20, 12, 0), 116.4074, tz_offset=8)

    def test_research_entry_accepts_iso_string(self):
        r = research_dual_time_chart(
            "2026-03-20T12:00:00+08:00", 116.4074,
            tz_name="Asia/Shanghai")
        self.assertEqual(r["research_api"], RESEARCH_API_ID)
        self.assertEqual(r["tz_validation"]["status"],
                         "resolved_from_tzdb")


class RepresentationInvarianceTests(unittest.TestCase):
    def test_same_instant_same_term_whatever_representation(self):
        """T4 key invariant: one physical instant, one solar term.

        2026-03-20 04:00 UTC written as 12:00 +08:00, 04:00 UTC and
        23:00 -05:00 (previous day) charts identically: same solar
        term and same four pillars. The time representation must
        never change the term of the same instant.
        """
        representations = (
            datetime(2026, 3, 20, 12, 0, tzinfo=CST),
            datetime(2026, 3, 20, 4, 0, tzinfo=UTC),
            datetime(2026, 3, 19, 23, 0,
                     tzinfo=timezone(timedelta(hours=-5))),
        )
        charts = [chart_from_datetime(rep) for rep in representations]
        terms = {chart["calendar"]["solar_term"] for chart in charts}
        self.assertEqual(len(terms), 1)
        first = _pillars(charts[0])
        for chart in charts[1:]:
            self.assertEqual(_pillars(chart), first)

    def test_term_changes_iff_boundary_between_instants(self):
        """T4: a term changes only when a jieqi moment lies between.

        For each case the between-check is computed independently
        from the pinned provider (prev/next jieqi around each
        endpoint); the entry's crossed flag and the two charts'
        solar terms must agree with it exactly.
        """
        cases = (
            (datetime(2026, 2, 4, 5, 0, tzinfo=CST), 87.62, 8),
            (datetime(2026, 11, 7, 4, 40, tzinfo=EST), -74.0060, -5),
            (datetime(2026, 3, 20, 23, 30, tzinfo=CST), 87.62, 8),
            (datetime(2026, 3, 20, 12, 0, tzinfo=CST), 116.4074, 8),
        )
        for birth, lon, tz in cases:
            with self.subTest(birth=birth.isoformat()):
                r = compare_standard_vs_true_solar(birth, lon, tz)
                std_utc = birth.astimezone(timezone.utc)
                app_utc = r["conversion"]["apparent_solar_time"].astimezone(
                    timezone.utc)
                lo, hi = (std_utc, app_utc) if std_utc < app_utc \
                    else (app_utc, std_utc)
                moments = set()
                for endpoint in (std_utc, app_utc):
                    shanghai = endpoint.astimezone(CST)
                    lunar = _LunarSolar.fromYmdHms(
                        shanghai.year, shanghai.month, shanghai.day,
                        shanghai.hour, shanghai.minute,
                        shanghai.second).getLunar()
                    for term in (lunar.getPrevJieQi(False),
                                 lunar.getNextJieQi()):
                        wall = datetime.strptime(
                            term.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S")
                        moments.add(wall.replace(tzinfo=CST).astimezone(
                            timezone.utc))
                between = any(lo < moment < hi for moment in moments)
                self.assertEqual(r["jieqi"]["crossed"], between)
                self.assertEqual(
                    r["jieqi"]["standard_solar_term"]
                    != r["jieqi"]["true_solar_solar_term"], between)

    def test_same_instant_same_solar_term_across_representations(self):
        """Regression (ChatGPT review, batch 3): the true-solar chart
        of one physical instant must not depend on how the instant
        was written. The birth is aimed so the +08:00-representation
        apparent instant lands 1 s BEFORE 立春 2026 (Urumqi lon
        87.62, tz 8): before the fix the UTC representation put the
        apparent instant ~2 s later, AFTER 立春, so the two
        representations reported different solar terms (大寒 vs 立春)
        -- and different year/month pillars -- for the same birth.
        After the fix both agree.
        """
        lichun = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        probe = apparent_solar_time(
            datetime(2026, 2, 4, 6, 25, 0, tzinfo=CST), 87.62, 8)
        app_utc = probe["apparent_solar_time"].astimezone(timezone.utc)
        target = lichun - timedelta(seconds=1)
        birth = (datetime(2026, 2, 4, 6, 25, 0, tzinfo=CST)
                 .astimezone(timezone.utc) + (target - app_utc))
        reps = (birth.astimezone(CST), birth.astimezone(timezone.utc))
        seen_terms = set()
        seen_pillars = set()
        seen_apparent = set()
        for rep in reps:
            with self.subTest(rep=rep.isoformat()):
                r = compare_standard_vs_true_solar(rep, 87.62, 8)
                seen_terms.add(
                    (r["jieqi"]["standard_solar_term"],
                     r["jieqi"]["true_solar_solar_term"]))
                seen_pillars.add((
                    tuple(sorted(
                        _pillars(r["standard_time_chart"]).items())),
                    tuple(sorted(
                        _pillars(r["true_solar_time_chart"]).items()))))
                seen_apparent.add(
                    r["conversion"]["apparent_solar_time"])
        self.assertEqual(len(seen_terms), 1)
        self.assertEqual(len(seen_pillars), 1)
        self.assertEqual(len(seen_apparent), 1)
        # The aimed case really is the near-boundary one: the
        # standard instant is after 立春, the converted instant
        # just before it -- a designed crossing, identical in both
        # representations.
        (std_term, sol_term), = seen_terms
        self.assertEqual(std_term, "立春")
        self.assertEqual(sol_term, "大寒")

    def test_near_boundary_no_crossing_keeps_term(self):
        """Near-jieqi-boundary control: a birth 30 min after 立春
        2026 (Beijing lon 116.4074, tz 8) corrects ~28 min back, so
        the converted instant is still ~2 min after 立春: the solar
        term must not flip, in either representation.
        """
        birth = datetime(2026, 2, 4, 4, 32, 8, tzinfo=CST)
        for rep in (birth, birth.astimezone(timezone.utc)):
            with self.subTest(rep=rep.isoformat()):
                r = compare_standard_vs_true_solar(rep, 116.4074, 8)
                self.assertFalse(r["jieqi"]["crossed"])
                self.assertEqual(r["jieqi"]["standard_solar_term"], "立春")
                self.assertEqual(r["jieqi"]["true_solar_solar_term"], "立春")
                self.assertFalse(r["differences"]["month_pillar_changed"])
                self.assertFalse(r["differences"]["year_pillar_changed"])
