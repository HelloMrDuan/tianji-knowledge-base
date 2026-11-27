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
# module under test. The expected pillars were likewise read off the
# pinned provider directly (``calendar()`` for the true instant's
# year/month/day/hour, plus the research day/hour derivation from
# the apparent solar time as a LOCAL reading), not invented.
#
# CORRECTED SEMANTICS (2026-11-26, true-solar defect fix): the
# apparent solar time is a local wall-clock reading at the
# birthplace, NOT a second physical instant. The year pillar, the
# month pillar and the solar term are fixed by the TRUE birth
# instant on both sides; only the day pillar (local solar date vs
# Shanghai date) and the hour pillar (local solar shichen vs
# Shanghai shichen) may differ. The earlier tests asserted the
# opposite -- that the correction moves a birth across 立春 and
# changes its year/month pillars -- because the old code fed the
# converted reading to ``chart_from_datetime`` as if it were an
# instant. Those expectations were wrong and are corrected here,
# with the reason stated in each test's docstring. E.g. Urumqi
# 2026-02-04 05:00 CST charts 丙午/庚寅/己酉/丁卯 under the
# standard caliber and 丙午/庚寅/己酉/乙丑 under the research
# caliber: same year/month/term, only the hour pillar moves.
# ======================================================================

from lunar_python import Solar as _LunarSolar

from tianji_kb.bazi_core import chart_from_datetime, chart_from_pillars
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
        chart_from_datetime(birth). The research chart is the
        uniform recompute from the true instant's year/month
        pillars plus the research day/hour pillars -- here
        identical to the standard four, because the local solar
        date and shichen agree with the Shanghai reading.
        Nothing is merged.
        """
        birth = datetime(2026, 3, 20, 12, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 116.4074, 8)
        self.assertEqual(_pillars(r["standard_time_chart"]),
                         _pillars(chart_from_datetime(birth)))
        self.assertEqual(_pillars(r["true_solar_time_chart"]),
                         {"year": "丙午", "month": "辛卯",
                          "day": "癸巳", "hour": "戊午"})
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
        """Urumqi 2026-01-01 00:30 CST -> previous LOCAL day: day pillar changes.

        The apparent solar time is 2025-12-31 22:17 at the
        birthplace, so the research day pillar follows the local
        solar date (2025-12-31, 甲戌） while the standard day pillar
        follows the Shanghai date of the true instant (2026-01-01,
        乙亥）. Year/month/term are fixed by the true instant and
        do not change.
        """
        birth = datetime(2026, 1, 1, 0, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        self.assertEqual(r["conversion"]["date_shift_days"], -1)
        self.assertTrue(r["differences"]["day_pillar_changed"])
        self.assertTrue(r["differences"]["chart_date"]["changed"])
        self.assertEqual(r["differences"]["chart_date"]["standard"], "2026-01-01")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2025-12-31")
        self.assertEqual(r["differences"]["pillars"]["day"]["standard"], "乙亥")
        self.assertEqual(r["differences"]["pillars"]["day"]["true_solar"], "甲戌")
        self.assertFalse(r["differences"]["year_pillar_changed"])
        self.assertFalse(r["differences"]["month_pillar_changed"])
        self.assertFalse(r["jieqi"]["crossed"])

    def test_cross_day_forwards_new_york_local_date_only(self):
        """New York 2026-11-03 23:58 EST -> next LOCAL day, same pillar day.

        The conversion moves the local wall date forward a day
        (date_shift_days == +1), and the Shanghai date of the true
        instant is Nov 4 too (23:58 EST = Nov 4 12:58 Shanghai), so
        the research local solar date (Nov 4) and the Shanghai date
        (Nov 4) agree: the day pillar does NOT change. A local-date
        shift therefore does NOT by itself change the day pillar;
        the day pillar changes only when the local solar date
        differs from the Shanghai date of the true instant.
        """
        birth = datetime(2026, 11, 3, 23, 58, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        self.assertEqual(r["conversion"]["date_shift_days"], 1)
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2026-11-04")
        self.assertFalse(r["differences"]["chart_date"]["changed"])
        self.assertFalse(r["differences"]["day_pillar_changed"])

    def test_cross_day_forwards_new_york_local_date_unchanged(self):
        """New York 2026-11-03 10:50 EST: day pillar does NOT change.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the day pillar changes 辛巳 -> 壬午 here, because
        the old code read the day pillar off the Shanghai date of
        the apparent-as-instant (11:10 EST as an instant is 00:10
        Shanghai, Nov 4). That was the defect: the apparent solar
        time is a LOCAL wall-clock reading at the birthplace
        (11:10 EST, Nov 3), not a second instant to re-convert to
        Shanghai. The research day pillar follows the local solar
        date (Nov 3, 辛巳）, the same date as the Shanghai date of
        the true instant (23:50 Nov 3), so the day pillar is
        unchanged. Only the shichen moves (戊子 -> 甲午）.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        self.assertEqual(r["conversion"]["date_shift_days"], 0)
        self.assertFalse(r["differences"]["chart_date"]["changed"])
        self.assertEqual(r["differences"]["chart_date"]["standard"], "2026-11-03")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"], "2026-11-03")
        self.assertFalse(r["differences"]["day_pillar_changed"])
        self.assertEqual(
            r["differences"]["pillars"]["day"]["standard"], "辛巳")
        self.assertEqual(
            r["differences"]["pillars"]["day"]["true_solar"], "辛巳")
        self.assertTrue(r["differences"]["hour_pillar_changed"])
        self.assertEqual(
            r["differences"]["pillars"]["hour"]["standard"], "戊子")
        self.assertEqual(
            r["differences"]["pillars"]["hour"]["true_solar"], "甲午")
        self.assertFalse(r["differences"]["year_pillar_changed"])
        self.assertFalse(r["differences"]["month_pillar_changed"])


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
    def test_jieqi_fixed_lichun_urumqi(self):
        """Urumqi 2026-02-04 05:00 CST: year/month/term fixed by the true instant.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the correction moves the birth across 立春, so the
        year pillar changes 丙午 -> 乙巳 and the month pillar 庚寅 ->
        己丑. That was the defect: the apparent solar time (02:36
        local) is a wall-clock reading at the birthplace, not a
        second instant, so it cannot move the birth across 立春.
        The true instant (05:00) is after 立春 (04:02:08), so both
        readings carry 丙午/庚寅 and the term 立春. Only the hour
        pillar moves (丁卯 -> 乙丑, 卯时 -> 丑时）; the day pillar
        (己酉） does not.
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "丙午")
        self.assertEqual(d["year"]["true_solar"], "丙午")
        self.assertEqual(d["month"]["standard"], "庚寅")
        self.assertEqual(d["month"]["true_solar"], "庚寅")
        self.assertEqual(d["day"]["standard"], "己酉")
        self.assertEqual(d["day"]["true_solar"], "己酉")
        self.assertEqual(d["hour"]["standard"], "丁卯")
        self.assertEqual(d["hour"]["true_solar"], "乙丑")
        self.assertTrue(d["hour"]["changed"])
        self.assertFalse(r["differences"]["year_pillar_changed"])
        self.assertFalse(r["differences"]["month_pillar_changed"])
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertIsNone(j["crossed_at_utc"])
        self.assertEqual(j["standard_solar_term"], "立春")
        self.assertEqual(j["true_solar_solar_term"], "立春")
        self.assertEqual(j["nearest_boundary_term"], "立春")
        expected = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        # Input 05:00 is 57.9 min after the 04:02:08 boundary; the
        # signed distance is measured from the TRUE instant.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -57.87, delta=1.0)
        self.assertAlmostEqual(j["nearest_boundary_minutes"],
                               57.87, delta=1.0)
        self.assertFalse(j["within_precision_budget"])

    def test_jieqi_fixed_lidong_new_york(self):
        """New York 2026-11-07 04:40 EST: year/month/term fixed by the true instant.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the correction moves the birth across 立冬
        (04:52:05 EST), so the month pillar changes. The apparent
        solar time (05:00 EST) is a local reading, not a second
        instant: the true instant (04:40 EST) is before 立冬， so
        both readings carry the term 霜降 and the pillars 丙午/戊戌.
        Only the hour pillar moves (乙酉 -> 己卯, 酉时 -> 卯时）.
        """
        birth = datetime(2026, 11, 7, 4, 40, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "霜降")
        self.assertEqual(j["true_solar_solar_term"], "霜降")
        self.assertEqual(j["nearest_boundary_term"], "立冬")
        # Input 04:40 EST is 12.1 min before the 04:52:05 EST boundary;
        # the signed distance is measured from the TRUE instant.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               12.08, delta=1.0)
        self.assertAlmostEqual(j["nearest_boundary_minutes"],
                               12.08, delta=1.0)
        self.assertFalse(r["differences"]["month_pillar_changed"])
        self.assertFalse(r["differences"]["year_pillar_changed"])
        d = r["differences"]["pillars"]
        self.assertEqual(d["month"]["standard"], "戊戌")
        self.assertEqual(d["month"]["true_solar"], "戊戌")
        self.assertEqual(d["day"]["standard"], "乙酉")
        self.assertEqual(d["day"]["true_solar"], "乙酉")
        self.assertEqual(d["hour"]["standard"], "乙酉")
        self.assertEqual(d["hour"]["true_solar"], "己卯")
        # The true instant is ~12.1 min from the boundary: outside the
        # +/-1 min precision budget, so the attribution is settled.
        self.assertFalse(j["within_precision_budget"])
        self.assertGreater(j["nearest_boundary_minutes"], 2.0)

    def test_jieqi_near_boundary_flagged_uncertain(self):
        """True instants within 2 min of 立春 are flagged, not settled.

        CORRECTED (2026-11-26, true-solar defect fix): the window is
        anchored at the TRUE instant's distance to the true jieqi
        boundary, never at the corrected reading. The old test aimed
        the CORRECTED reading at the boundary (Urumqi 06:24/06:26,
        whose true instants are ~140 min past 立春 and so were never
        inside the window under the corrected anchor). The new cases
        put the TRUE instant itself near 立春： 04:00:30 (1.6 min
        BEFORE) and 04:03:00 (0.9 min AFTER), Beijing lon. Expected
        distances are recomputed independently here from the provider
        instant and the TRUE instant.
        """
        lichun = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        for wall_hh, wall_mm, wall_ss, expect_term in (
                (4, 0, 30, "大寒"), (4, 3, 0, "立春")):
            with self.subTest(wall="%02d:%02d:%02d"
                              % (wall_hh, wall_mm, wall_ss)):
                birth = datetime(2026, 2, 4, wall_hh, wall_mm, wall_ss,
                                 tzinfo=CST)
                r = compare_standard_vs_true_solar(birth, 116.4074, 8)
                expected_distance = abs(
                    (birth.astimezone(timezone.utc) - lichun)
                    .total_seconds()) / 60.0
                self.assertAlmostEqual(r["jieqi"]["nearest_boundary_minutes"],
                                       expected_distance, delta=0.1)
                self.assertEqual(r["jieqi"]["nearest_boundary_term"], "立春")
                self.assertFalse(r["jieqi"]["crossed"])
                self.assertEqual(r["jieqi"]["standard_solar_term"],
                                 expect_term)
                self.assertEqual(r["jieqi"]["true_solar_solar_term"],
                                 expect_term)
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
        """Urumqi 1900-01-01 00:05: research local date 1899-12-31, refused.

        (Wording corrected 2026-11-26: the refusal is the
        research-caliber local solar date falling outside the
        supported calendar range 1900..2099, not a converted instant
        as such. The standard-time chart is unaffected and no chart
        is returned.)
        """
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
    def test_jieqi_fixed_xiaoshu_urumqi(self):
        """Urumqi 2026-07-07 11:00 CST: year/month/term fixed by the true instant.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the correction moves the birth across 小暑， so the
        month pillar changes 乙未 -> 甲午. The apparent solar time
        (~08:46 local) is a wall-clock reading, not a second
        instant: the true instant (11:00) is after 小暑
        (09:56:57), so both readings carry 乙未 and the term 小暑.
        Only the hour pillar moves (丙午 -> 甲辰， 午时 -> 辰时）;
        the day pillar (壬午） does not.
        """
        birth = datetime(2026, 7, 7, 11, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "丙午")
        self.assertEqual(d["year"]["true_solar"], "丙午")
        self.assertEqual(d["month"]["standard"], "乙未")
        self.assertEqual(d["month"]["true_solar"], "乙未")
        self.assertEqual(d["day"]["standard"], "壬午")
        self.assertEqual(d["day"]["true_solar"], "壬午")
        self.assertEqual(d["hour"]["standard"], "丙午")
        self.assertEqual(d["hour"]["true_solar"], "甲辰")
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "小暑")
        self.assertEqual(j["true_solar_solar_term"], "小暑")
        self.assertEqual(j["nearest_boundary_term"], "小暑")
        # Input 11:00 is 63.1 min after the 09:56:57 boundary; the
        # signed distance is measured from the TRUE instant, and the
        # nearest-boundary distance is the same number now (it was
        # 71.4 min measured from the corrected reading).
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -63.05, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 63.05, delta=1.0)

    def test_jieqi_fixed_daxue_urumqi(self):
        """Urumqi 2026-12-07 11:30 CST: year/month/term fixed by the true instant.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the correction moves the birth across 大雪， so the
        month pillar changes 庚子 -> 己亥. The true instant (11:30)
        is after 大雪 (10:52:32), so both readings carry 庚子 and
        the term 大雪. Only the hour pillar moves (壬午 -> 辛巳）;
        the day pillar (乙卯） does not.
        """
        birth = datetime(2026, 12, 7, 11, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        self.assertEqual(d["month"]["standard"], "庚子")
        self.assertEqual(d["month"]["true_solar"], "庚子")
        self.assertEqual(d["day"]["standard"], "乙卯")
        self.assertEqual(d["day"]["true_solar"], "乙卯")
        self.assertEqual(d["hour"]["standard"], "壬午")
        self.assertEqual(d["hour"]["true_solar"], "辛巳")
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "大雪")
        self.assertEqual(j["true_solar_solar_term"], "大雪")
        self.assertEqual(j["nearest_boundary_term"], "大雪")
        # Input 11:30 is 37.5 min after the 10:52:32 boundary; the
        # signed distance is measured from the TRUE instant, and the
        # nearest-boundary distance is the same number now (it was
        # 83.5 min measured from the corrected reading).
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -37.47, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 37.47, delta=1.0)

    def test_jieqi_fixed_lichun_tokyo(self):
        """Tokyo 2026-02-04 05:01 JST: year/month/term fixed by the true instant.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the correction moves the birth across 立春
        (05:02:08 JST), so the year AND month pillars change
        together (乙巳/己丑 -> 丙午/庚寅）. The apparent solar time
        (~05:06 JST) is a local reading, not a second instant: the
        true instant (05:01 JST) is BEFORE 立春， so both readings
        carry 乙巳/己丑 and the term 大寒. Only the hour pillar
        moves (丙寅 -> 丁卯, 寅时 -> 卯时）; the day pillar (己酉）
        does not. The true instant is 1.1 min before 立春， inside
        the provisional window, so the month attribution is NOT
        settled (it was "settled" before, measured from the
        corrected reading 4.1 min past the boundary).
        """
        birth = datetime(2026, 2, 4, 5, 1, tzinfo=JST)
        r = compare_standard_vs_true_solar(birth, 139.767, 9)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "乙巳")
        self.assertEqual(d["year"]["true_solar"], "乙巳")
        self.assertEqual(d["month"]["standard"], "己丑")
        self.assertEqual(d["month"]["true_solar"], "己丑")
        self.assertEqual(d["day"]["standard"], "己酉")
        self.assertEqual(d["day"]["true_solar"], "己酉")
        self.assertEqual(d["hour"]["standard"], "丙寅")
        self.assertEqual(d["hour"]["true_solar"], "丁卯")
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "大寒")
        self.assertEqual(j["true_solar_solar_term"], "大寒")
        # Input 05:01 JST is 1.1 min before the 05:02:08 JST boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               1.13, delta=1.0)
        # True instant inside the window: NOT settled.
        self.assertTrue(j["within_precision_budget"])
        self.assertLess(j["nearest_boundary_minutes"], 2.0)
        self.assertIn("NOT settled", j["note"])

    def test_qi_fixed_chunfen_month_unchanged(self):
        """Urumqi 2026-03-20 23:30 CST: term fixed too, month unchanged.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the solar term changes 春分 -> 惊蛰 while the month
        pillar stays 辛卯 (a 中气 crossing). No crossing ever
        happens now: the true instant (23:30) is after 春分
        (22:45:59), so both readings carry the term 春分 and the
        month pillar 辛卯. Only the hour pillar moves (壬子 -> 癸亥）;
        the day pillar (癸巳） does not.
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
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "春分")
        self.assertEqual(j["true_solar_solar_term"], "春分")
        self.assertFalse(r["differences"]["month_pillar_changed"])
        self.assertTrue(r["differences"]["hour_pillar_changed"])
        # Input 23:30 is 44.0 min after the 22:45:59 boundary; the
        # signed distance is measured from the TRUE instant, and the
        # nearest-boundary distance is the same number now (it was
        # 92.9 min measured from the corrected reading).
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -44.02, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 44.02, delta=1.0)

    def test_qi_fixed_xiazhi_month_unchanged(self):
        """Urumqi 2026-06-21 17:30 CST: term fixed too, month unchanged.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the solar term changes 夏至 -> 芒种 while the month
        pillar stays 甲午 (a 中气 crossing). No crossing ever
        happens now: the true instant (17:30) is after 夏至
        (16:24:30), so both readings carry the term 夏至 and the
        month pillar 甲午. Only the hour pillar moves (丁酉 -> 丙申）;
        the day pillar (丙寅） does not.
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
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "夏至")
        self.assertEqual(j["true_solar_solar_term"], "夏至")
        self.assertFalse(r["differences"]["month_pillar_changed"])
        # Input 17:30 is 65.5 min after the 16:24:30 boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               -65.5, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 65.5, delta=1.0)

    def test_qiufen_tokyo_term_fixed_hour_changes(self):
        """Tokyo 2026-09-23 08:50 JST: term fixed, only the hour moves.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted only the solar term changes (白露 -> 秋分） and all
        four pillars are identical (a 中气 crossing). No crossing
        ever happens now: the true instant (08:50 JST) is before
        秋分 (09:05:14 JST), so both readings carry the term 白露.
        The year/month/day pillars are identical (丙午/丁酉/庚子）,
        but the hour pillar DOES move (庚辰 -> 辛巳）: the Shanghai
        shichen of the true instant is 辰时 (08:16 Shanghai) while
        the local solar shichen is 巳时 (09:16 JST).
        """
        birth = datetime(2026, 9, 23, 8, 50, tzinfo=JST)
        r = compare_standard_vs_true_solar(birth, 139.767, 9)
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "丙午")
        self.assertEqual(d["year"]["true_solar"], "丙午")
        self.assertEqual(d["month"]["standard"], "丁酉")
        self.assertEqual(d["month"]["true_solar"], "丁酉")
        self.assertEqual(d["day"]["standard"], "庚子")
        self.assertEqual(d["day"]["true_solar"], "庚子")
        self.assertEqual(d["hour"]["standard"], "庚辰")
        self.assertEqual(d["hour"]["true_solar"], "辛巳")
        self.assertTrue(r["differences"]["hour_pillar_changed"])
        self.assertTrue(r["differences"]["any_pillar_changed"])
        self.assertFalse(r["differences"]["year_pillar_changed"])
        self.assertFalse(r["differences"]["month_pillar_changed"])
        self.assertFalse(r["differences"]["day_pillar_changed"])
        j = r["jieqi"]
        self.assertFalse(j["crossed"])
        self.assertIsNone(j["crossed_term"])
        self.assertEqual(j["standard_solar_term"], "白露")
        self.assertEqual(j["true_solar_solar_term"], "白露")
        # Input 08:50 JST is 15.2 min before the 09:05:14 JST boundary.
        self.assertAlmostEqual(j["minutes_from_input_to_boundary"],
                               15.23, delta=1.0)
        self.assertFalse(j["within_precision_budget"])
        self.assertAlmostEqual(j["nearest_boundary_minutes"], 15.23, delta=1.0)

    def test_cross_day_backwards_sydney_local_date_only(self):
        """Sydney 2026-01-01 00:30 +11: local date shifts back a day.

        The local date shifts (date_shift_days == -1) but the
        Shanghai date of the true instant is 2025-12-31 too (00:30
        +11 = 21:30 Shanghai, Dec 31), so the research local solar
        date (Dec 31) and the Shanghai date (Dec 31) agree and the
        day pillar does NOT change (甲戌 on both sides). Only the
        hour pillar changes (乙亥 -> 甲子）: the Shanghai shichen is
        亥时 (21:30) while the local solar shichen is 子时 (23:31).
        (The old test asserted the hour changes 乙亥 -> 甲戌 -- the
        戌时 reading came from the Shanghai time of the
        apparent-as-instant, the defect fixed 2026-11-26.)
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
        self.assertEqual(d["hour"]["true_solar"], "甲子")
        self.assertFalse(r["jieqi"]["crossed"])

    def test_cross_day_backwards_honolulu_day_follows_local_date(self):
        """Honolulu 2026-01-01 00:20 -10: day follows the LOCAL solar date.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted no pillar changes at all here. The Shanghai date of
        the true instant is 2026-01-01 (00:20 -10 = 18:20 Shanghai),
        but the local solar date at the birthplace is 2025-12-31
        (apparent 23:45, Dec 31), so the research day pillar is 甲戌
        while the standard day pillar is 乙亥 -- the day pillar
        genuinely changes, for the right reason (local solar date vs
        Shanghai date). The hour pillar changes too (乙酉 -> 甲子）.
        Year/month/term are fixed by the true instant (乙巳/戊子/冬至
        on both sides).
        """
        birth = datetime(2026, 1, 1, 0, 20,
                         tzinfo=timezone(timedelta(hours=-10)))
        r = compare_standard_vs_true_solar(birth, -157.858, -10)
        self.assertEqual(r["conversion"]["date_shift_days"], -1)
        self.assertTrue(r["differences"]["chart_date"]["changed"])
        self.assertEqual(r["differences"]["chart_date"]["standard"],
                         "2026-01-01")
        self.assertEqual(r["differences"]["chart_date"]["true_solar"],
                         "2025-12-31")
        self.assertTrue(r["differences"]["day_pillar_changed"])
        d = r["differences"]["pillars"]
        self.assertEqual(d["year"]["standard"], "乙巳")
        self.assertEqual(d["year"]["true_solar"], "乙巳")
        self.assertEqual(d["month"]["standard"], "戊子")
        self.assertEqual(d["month"]["true_solar"], "戊子")
        self.assertEqual(d["day"]["standard"], "乙亥")
        self.assertEqual(d["day"]["true_solar"], "甲戌")
        self.assertEqual(d["hour"]["standard"], "乙酉")
        self.assertEqual(d["hour"]["true_solar"], "甲子")
        self.assertFalse(r["jieqi"]["crossed"])

    def test_zi_start_day_boundary_contrast(self):
        """NY 2026-11-03 10:50 EST under midnight vs zi-start.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the day pillar changes under midnight (辛巳 -> 壬午）
        and is unchanged under zi-start (壬午 on both sides) -- both
        readings came from the Shanghai date of the
        apparent-as-instant (00:10 Nov 4). Under the corrected
        semantics the research day pillar follows the LOCAL solar
        date (Nov 3) in both conventions, so under midnight the day
        pillar is UNCHANGED (辛巳 on both sides: Shanghai Nov 3,
        local Nov 3), while under zi-start it CHANGES (壬午 -> 辛巳）:
        the Shanghai reading (23:50 Nov 3) is already past the 23:00
        zi-start boundary, so the standard day is Nov 4, but the
        local solar reading (11:10 Nov 3) is before it, so the
        research day is Nov 3. Same birth, same conversion,
        different day boundary -- and the contrast runs the other
        way round from the old (wrong) expectation.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r_mid = compare_standard_vs_true_solar(
            birth, -74.0060, -5, day_boundary="midnight")
        self.assertFalse(r_mid["differences"]["day_pillar_changed"])
        self.assertEqual(
            r_mid["differences"]["pillars"]["day"]["standard"], "辛巳")
        self.assertEqual(
            r_mid["differences"]["pillars"]["day"]["true_solar"], "辛巳")
        self.assertEqual(
            r_mid["differences"]["pillars"]["hour"]["standard"], "戊子")
        self.assertEqual(
            r_mid["differences"]["pillars"]["hour"]["true_solar"], "甲午")
        r_zi = compare_standard_vs_true_solar(
            birth, -74.0060, -5, day_boundary="zi-start")
        self.assertTrue(r_zi["differences"]["day_pillar_changed"])
        self.assertEqual(
            r_zi["differences"]["pillars"]["day"]["standard"], "壬午")
        self.assertEqual(
            r_zi["differences"]["pillars"]["day"]["true_solar"], "辛巳")
        self.assertEqual(
            r_zi["differences"]["pillars"]["hour"]["standard"], "庚子")
        self.assertEqual(
            r_zi["differences"]["pillars"]["hour"]["true_solar"], "甲午")
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
        """Adapter rows are the real charts' pillar dicts, not recomputed.

        CORRECTED (2026-11-26, true-solar defect fix): the standard
        side is still chart_from_datetime(birth), but the research
        side is NO LONGER chart_from_datetime(apparent) -- that was
        the defect (the apparent reading fed in as an instant). It is
        the uniform recompute from the true instant's year/month
        pillars plus the research day/hour pillars, checked here
        against an independent chart_from_pillars call with the
        hand-derived four ganzhi (丙午/庚寅/己酉/乙丑）.
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        std_pillars = {item["name"]: item
                       for item in chart_from_datetime(birth)["pillars"]}
        sol_pillars = {item["name"]: item
                       for item in chart_from_pillars(
                           "丙午", "庚寅", "己酉", "乙丑")["pillars"]}
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
        self.assertIn("cannot change", rows["year"]["reason"])
        self.assertIn("No jieqi was crossed", rows["month"]["reason"])
        self.assertIn("matches the Shanghai date",
                      rows["day"]["reason"])
        self.assertIn("shichen is unchanged", rows["hour"]["reason"])
        # Boundary distances: next shichen 13:00 is 60 min after the
        # standard instant, ~82 min after the apparent solar time.
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_standard_instant_to_next_shichen_boundary"],
            60.0, delta=2.0)
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_apparent_solar_time_to_next_shichen_boundary"],
            81.9, delta=2.0)
        self.assertAlmostEqual(
            rows["day"]["detail"]
            ["minutes_from_standard_instant_to_next_shanghai_boundary"],
            720.0, delta=2.0)
        self.assertAlmostEqual(
            rows["day"]["detail"]
            ["minutes_from_apparent_solar_time_to_next_local_boundary"],
            741.9, delta=2.0)

    def test_adapter_lichun_urumqi_year_month_fixed(self):
        """Urumqi 立春 case: year+month FIXED by the true instant, reasons say why.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        (test_adapter_lichun_urumqi_year_month_together) asserted
        the year and month pillars change together because the
        correction crosses 立春. That was the defect: the apparent
        solar time (02:36 local) is a wall-clock reading, not a
        second instant, so the true instant (05:00, after 立春
        04:02:08) fixes both readings at 丙午/庚寅. Only the hour
        pillar changes (丁卯 -> 乙丑, 卯时 -> 丑时）; the day pillar
        (己酉） does not. The year/month ten-god readings are
        therefore unchanged too (same ganzhi, same day master 己）.
        The branch relations and taohua still change, because the
        hour branch moves 卯 -> 丑 (the 卯酉 clash on the standard
        side is gone on the research side, and the taohua match on
        the year-branch basis is gone with it).
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertFalse(pc["year_and_month_changed_together"])
        self.assertFalse(rows["year"]["changed"])
        self.assertFalse(rows["month"]["changed"])
        self.assertFalse(rows["day"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertEqual(rows["year"]["standard"]["ganzhi"], "丙午")
        self.assertEqual(rows["year"]["true_solar"]["ganzhi"], "丙午")
        self.assertEqual(rows["month"]["standard"]["ganzhi"], "庚寅")
        self.assertEqual(rows["month"]["true_solar"]["ganzhi"], "庚寅")
        self.assertIn("立春", rows["year"]["reason"])
        self.assertIn("cannot change", rows["year"]["reason"])
        self.assertIn("No jieqi was crossed", rows["month"]["reason"])
        self.assertIsNone(rows["month"]["detail"]["crossed_term"])
        self.assertIsNone(rows["month"]["detail"]["crossed_term_kind"])
        self.assertEqual(rows["month"]["detail"]["nearest_boundary_term"],
                         "立春")
        self.assertEqual(rows["month"]["detail"]["nearest_boundary_term_kind"],
                         "节")
        self.assertIn("matches the Shanghai date", rows["day"]["reason"])
        self.assertIn("shichen changed", rows["hour"]["reason"])
        # Standard 05:00 is 卯时 (丁卯）; the ~143 min backward
        # correction lands ~02:36 local, i.e. 丑时 (乙丑）.
        self.assertIn("卯时", rows["hour"]["reason"])
        self.assertIn("丑时", rows["hour"]["reason"])
        # Day master is 己 on both sides: ten-god readings agree
        # wherever the pillar itself is unchanged.
        self.assertFalse(pc["day_master"]["changed"])
        self.assertEqual(pc["day_master"]["standard"]["stem"], "己")
        self.assertFalse(rows["day"]["ten_god_reading_changed"])
        self.assertFalse(rows["year"]["ten_god_reading_changed"])
        self.assertFalse(rows["month"]["ten_god_reading_changed"])
        self.assertTrue(rows["hour"]["ten_god_reading_changed"])
        self.assertTrue(pc["derived"]["branch_relations_changed"])
        self.assertTrue(pc["derived"]["taohua_changed"])
        self.assertTrue(pc["month_attribution_settled"])
        self.assertNotIn("changed together", pc["note"])

    def test_adapter_lichun_forward_tokyo(self):
        """Tokyo forward 立春 case: year/month fixed, hour moves, month undetermined.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the year and month pillars change together because
        the correction crosses 立春 (05:02:08 JST). The true instant
        (05:01 JST) is BEFORE 立春， so both readings carry 乙巳/己丑
        and the term 大寒. The hour pillar DOES move (丙寅 -> 丁卯）:
        the Shanghai shichen is 寅时 (04:01 Shanghai) while the
        local solar shichen is 卯时 (05:06 JST). The true instant is
        1.1 min before 立春， inside the provisional window, so the
        month attribution is NOT settled (the old test asserted it
        settled, measured from the corrected reading 4.1 min past
        the boundary).
        """
        birth = datetime(2026, 2, 4, 5, 1, tzinfo=JST)
        r = compare_pillars(birth, 139.767, 9)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertFalse(pc["year_and_month_changed_together"])
        self.assertFalse(rows["year"]["changed"])
        self.assertFalse(rows["month"]["changed"])
        self.assertFalse(rows["day"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertEqual(rows["hour"]["standard"]["ganzhi"], "丙寅")
        self.assertEqual(rows["hour"]["true_solar"]["ganzhi"], "丁卯")
        self.assertIn("立春", rows["year"]["reason"])
        self.assertIn("cannot change", rows["year"]["reason"])
        self.assertIn("寅时", rows["hour"]["reason"])
        self.assertIn("卯时", rows["hour"]["reason"])
        self.assertAlmostEqual(
            rows["hour"]["detail"]
            ["minutes_from_standard_instant_to_next_shichen_boundary"],
            59.0, delta=2.0)
        self.assertFalse(pc["month_attribution_settled"])
        self.assertEqual(pc["month_attribution"], "undetermined")
        self.assertIn("月令归属未定", pc["note"])
        self.assertFalse(
            rows["year"]["detail"]["attribution_settled"])

    def test_adapter_chunfen_term_fixed(self):
        """春分 case: term fixed too, month pillar does not change.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the conversion crosses 春分 (a 中气 term), so the
        term changes but the month pillar does not. No crossing ever
        happens now: the true instant (23:30) is after 春分, so both
        readings carry the term 春分 and the month pillar 辛卯. The
        month reason therefore says no jieqi was crossed, and the
        crossed-* detail fields are None.
        """
        birth = datetime(2026, 3, 20, 23, 30, tzinfo=CST)
        r = compare_pillars(birth, 87.62, 8)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertFalse(rows["month"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertIn("No jieqi was crossed", rows["month"]["reason"])
        self.assertIsNone(rows["month"]["detail"]["crossed_term"])
        self.assertIsNone(rows["month"]["detail"]["crossed_term_kind"])
        self.assertEqual(rows["month"]["detail"]["nearest_boundary_term"],
                         "春分")
        self.assertEqual(rows["month"]["detail"]["nearest_boundary_term_kind"],
                         "气")
        self.assertFalse(pc["year_and_month_changed_together"])
        self.assertTrue(pc["month_attribution_settled"])

    def test_adapter_qiufen_term_fixed_hour_changes(self):
        """秋分 case: term fixed, only the hour pillar changes.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted 秋分 is crossed forward and no pillar changes at
        all. No crossing ever happens now: the true instant (08:50
        JST) is before 秋分， so both readings carry the term 白露.
        The hour pillar DOES change (庚辰 -> 辛巳）: the Shanghai
        shichen is 辰时 while the local solar shichen is 巳时.
        """
        birth = datetime(2026, 9, 23, 8, 50, tzinfo=JST)
        r = compare_pillars(birth, 139.767, 9)
        pc = r["pillar_comparison"]
        rows = self._rows(r)
        self.assertFalse(rows["year"]["changed"])
        self.assertFalse(rows["month"]["changed"])
        self.assertFalse(rows["day"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertEqual(rows["hour"]["standard"]["ganzhi"], "庚辰")
        self.assertEqual(rows["hour"]["true_solar"]["ganzhi"], "辛巳")
        self.assertFalse(r["jieqi"]["crossed"])
        self.assertEqual(r["jieqi"]["standard_solar_term"], "白露")
        self.assertEqual(r["jieqi"]["true_solar_solar_term"], "白露")
        self.assertIn("No jieqi was crossed", rows["month"]["reason"])
        self.assertTrue(pc["month_attribution_settled"])

    def test_adapter_day_master_change_cascade(self):
        """Urumqi 2026-01-01 00:30: day pillar changes, day master 乙->甲.

        The day-master change recomputes the ten-god reading of
        every pillar: the year and month pillars are unchanged as
        ganzhi, yet their ten-god readings differ between the sides.
        The day pillar changes because the local solar date
        (2025-12-31) differs from the Shanghai date of the true
        instant (2026-01-01) -- the reason says so explicitly.
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
        self.assertEqual(rows["hour"]["standard"]["ganzhi"], "丙子")
        self.assertEqual(rows["hour"]["true_solar"]["ganzhi"], "乙亥")
        # Unchanged pillars, changed ten-god readings: the cascade.
        self.assertFalse(rows["year"]["changed"])
        self.assertTrue(rows["year"]["ten_god_reading_changed"])
        self.assertFalse(rows["month"]["changed"])
        self.assertTrue(rows["month"]["ten_god_reading_changed"])
        self.assertIn("recomputed", pc["note"])
        self.assertIn("local solar date", rows["day"]["reason"])
        self.assertIn("2025-12-31", rows["day"]["reason"])
        self.assertIn("2026-01-01", rows["day"]["reason"])

    def test_adapter_within_budget_month_undetermined(self):
        """Within the 2-minute window: 月令归属未定 (status quo, T1).

        CORRECTED (2026-11-26, true-solar defect fix): the window is
        anchored at the TRUE instant, never at the corrected reading.
        The old cases (Urumqi 06:24/06:26) aimed the CORRECTED
        reading at 立春 while their true instants were ~140 min past
        it, so they were never inside the window under the corrected
        anchor. The new cases put the TRUE instant itself near 立春：
        04:00:30 (1.6 min BEFORE) and 04:03:00 (0.9 min AFTER),
        Beijing lon. Both keep the month attribution undetermined.
        """
        for wall_hh, wall_mm, wall_ss, expect_term in (
                (4, 0, 30, "大寒"), (4, 3, 0, "立春")):
            with self.subTest(wall="%02d:%02d:%02d"
                              % (wall_hh, wall_mm, wall_ss)):
                birth = datetime(2026, 2, 4, wall_hh, wall_mm, wall_ss,
                                 tzinfo=CST)
                r = compare_pillars(birth, 116.4074, 8)
                pc = r["pillar_comparison"]
                self.assertFalse(r["jieqi"]["crossed"])
                self.assertEqual(r["jieqi"]["standard_solar_term"],
                                 expect_term)
                self.assertTrue(r["jieqi"]["within_precision_budget"])
                self.assertFalse(pc["month_attribution_settled"])
                self.assertEqual(pc["month_attribution"], "undetermined")
                self.assertIn("月令归属未定", pc["note"])
                self.assertIn("NOT settled",
                              self._rows(r)["month"]["reason"])
                self.assertFalse(
                    self._rows(r)["year"]["detail"]["attribution_settled"])

    def test_adapter_zi_start_day_contrast(self):
        """NY case under midnight vs zi-start: the contrast runs the other way.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the day row is unchanged under zi-start and changed
        under midnight, both readings taken from the Shanghai date of
        the apparent-as-instant. Under the corrected semantics the
        research day pillar follows the LOCAL solar date (Nov 3) in
        both conventions: under midnight the day row is UNCHANGED
        (辛巳 on both sides), while under zi-start it CHANGES
        (壬午 -> 辛巳） because the Shanghai reading (23:50 Nov 3)
        is already past the 23:00 zi-start boundary while the local
        solar reading (11:10 Nov 3) is not.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r_zi = compare_pillars(birth, -74.0060, -5, day_boundary="zi-start")
        rows_zi = self._rows(r_zi)
        self.assertTrue(rows_zi["day"]["changed"])
        self.assertEqual(rows_zi["day"]["standard"]["ganzhi"], "壬午")
        self.assertEqual(rows_zi["day"]["true_solar"]["ganzhi"], "辛巳")
        self.assertIn("23:00", rows_zi["day"]["reason"])
        self.assertIn("local solar date", rows_zi["day"]["reason"])
        self.assertEqual(
            rows_zi["day"]["detail"]["standard_basis"], "shanghai_date")
        self.assertEqual(
            rows_zi["day"]["detail"]["true_solar_basis"], "local_solar_date")
        self.assertEqual(
            rows_zi["day"]["detail"]["standard_day_date"], "2026-11-04")
        self.assertEqual(
            rows_zi["day"]["detail"]["true_solar_day_date"], "2026-11-03")
        r_mid = compare_pillars(birth, -74.0060, -5, day_boundary="midnight")
        rows_mid = self._rows(r_mid)
        self.assertFalse(rows_mid["day"]["changed"])
        self.assertIn("00:00", rows_mid["day"]["reason"])
        self.assertIn("matches the Shanghai date", rows_mid["day"]["reason"])
        self.assertEqual(
            rows_mid["day"]["detail"]["standard_day_date"], "2026-11-03")
        self.assertEqual(
            rows_mid["day"]["detail"]["true_solar_day_date"], "2026-11-03")

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
# physical instant always carries the same solar term, year pillar
# and month pillar, because those are fixed by the true instant and
# the correction moves only the local solar reading used for the
# research day/hour pillars. (Corrected 2026-11-26: the earlier
# formulation -- a term changes only when a jieqi moment lies
# between the standard and the converted instants -- treated the
# converted reading as a second instant; no jieqi is ever crossed
# by the correction now.)
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
        """Sweep the TRUE instant 04:00-04:05 across 立春: flag flips at 2.0 min.

        CORRECTED (2026-11-26, true-solar defect fix): the window is
        anchored at the TRUE instant's distance to the true jieqi
        boundary, never at the corrected reading. The old sweep moved
        the wall time 06:23-06:28 (Urumqi) so the CORRECTED reading
        crossed 立春； those true instants are ~140 min past 立春 and
        were never inside the window under the corrected anchor. The
        new sweep moves the true instant itself across 立春
        (04:02:08) in 1-minute steps, Beijing lon (longitude is
        irrelevant to the window now -- the anchor is the instant).
        The flag must equal (nearest_boundary_minutes < 2.0) at every
        step, must be True on both sides of the boundary while
        inside, and must flip to False once the true instant is 2+
        min away -- on both the before and the after side.
        """
        lichun = _independent_jieqi_utc(2026, 2, 4, 5, 0, 0, "立春")
        seen_inside = seen_outside = 0
        for wall_mm in (0, 1, 2, 3, 4, 5):
            with self.subTest(wall="04:%02d" % wall_mm):
                birth = datetime(2026, 2, 4, 4, wall_mm, tzinfo=CST)
                r = compare_standard_vs_true_solar(birth, 116.4074, 8)
                j = r["jieqi"]
                self.assertEqual(j["nearest_boundary_term"], "立春")
                self.assertEqual(j["uncertainty_window_status"],
                                 "provisional")
                self.assertIn("T1", j["uncertainty_window_adjudication"])
                # Distance recomputed independently from the provider
                # instant and the TRUE instant.
                expected_distance = abs(
                    (birth.astimezone(timezone.utc) - lichun)
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
        """True instant 04:04:30 -> 2.4 min past 立春: settled.

        CORRECTED (2026-11-26, true-solar defect fix): the old case
        (Urumqi 06:28, corrected reading ~04:04:37) measured the
        window from the corrected reading. The window is anchored at
        the TRUE instant now: 04:04:30 is 2.37 min past 立春, outside
        the window, so the attribution is settled.
        """
        birth = datetime(2026, 2, 4, 4, 4, 30, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 116.4074, 8)
        self.assertFalse(r["jieqi"]["within_precision_budget"])
        self.assertGreater(r["jieqi"]["nearest_boundary_minutes"], 2.0)
        self.assertEqual(r["jieqi"]["uncertainty_window_status"],
                         "provisional")
        pc = compare_pillars(birth, 116.4074, 8)["pillar_comparison"]
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

        CORRECTED (2026-11-26, true-solar defect fix): the day change
        follows the LOCAL solar date, not the Shanghai date of the
        apparent-as-instant. Standard instant 00:05 UTC is 08:05
        Shanghai Mar 20 (day 癸巳）. The -179.9 apparent reading is
        Mar 19 11:58 UTC: the local solar date is Mar 19, so the
        research day pillar is 壬辰. The +179.9 apparent reading is
        Mar 20 11:57 UTC: the local solar date is Mar 20, so the
        research day pillar stays 癸巳. The hour pillars move on
        both sides (丙辰 -> 丙午 west, 丙辰 -> 戊午 east) because the
        local solar shichen (午时） differs from the Shanghai shichen
        (辰时）.
        """
        birth = datetime(2026, 3, 20, 0, 5, tzinfo=UTC)
        r_west = compare_standard_vs_true_solar(birth, -179.9, 0)
        self.assertTrue(r_west["differences"]["day_pillar_changed"])
        self.assertTrue(r_west["differences"]["chart_date"]["changed"])
        self.assertEqual(
            r_west["differences"]["chart_date"]["standard"], "2026-03-20")
        self.assertEqual(
            r_west["differences"]["chart_date"]["true_solar"], "2026-03-19")
        self.assertEqual(
            r_west["differences"]["pillars"]["day"]["standard"], "癸巳")
        self.assertEqual(
            r_west["differences"]["pillars"]["day"]["true_solar"], "壬辰")
        self.assertEqual(
            r_west["differences"]["pillars"]["hour"]["standard"], "丙辰")
        self.assertEqual(
            r_west["differences"]["pillars"]["hour"]["true_solar"], "丙午")
        r_east = compare_standard_vs_true_solar(birth, 179.9, 0)
        self.assertFalse(r_east["differences"]["day_pillar_changed"])
        self.assertFalse(r_east["differences"]["chart_date"]["changed"])
        self.assertEqual(
            r_east["differences"]["pillars"]["day"]["standard"], "癸巳")
        self.assertEqual(
            r_east["differences"]["pillars"]["day"]["true_solar"], "癸巳")
        self.assertEqual(
            r_east["differences"]["pillars"]["hour"]["standard"], "丙辰")
        self.assertEqual(
            r_east["differences"]["pillars"]["hour"]["true_solar"], "戊午")

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

    def test_term_fixed_by_true_instant(self):
        """T4: the term is fixed by the true instant in every case.

        CORRECTED (2026-11-26, true-solar defect fix): the old test
        asserted the term changes exactly when a jieqi moment lies
        strictly between the standard instant and the converted
        instant -- i.e. it treated the converted reading as a second
        instant. No jieqi is ever crossed by the correction now: the
        term, the year pillar and the month pillar are fixed by the
        true instant, so ``crossed`` is False and both charts carry
        the same term in every case. The independent check is kept:
        the shared term must equal the provider's term at the TRUE
        instant (prev/next jieqi around the true instant only).
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
                self.assertFalse(r["jieqi"]["crossed"])
                self.assertIsNone(r["jieqi"]["crossed_term"])
                self.assertEqual(
                    r["jieqi"]["standard_solar_term"],
                    r["jieqi"]["true_solar_solar_term"])
                self.assertFalse(r["differences"]["year_pillar_changed"])
                self.assertFalse(r["differences"]["month_pillar_changed"])
                # Independent provider term at the TRUE instant.
                shanghai = birth.astimezone(CST)
                lunar = _LunarSolar.fromYmdHms(
                    shanghai.year, shanghai.month, shanghai.day,
                    shanghai.hour, shanghai.minute,
                    shanghai.second).getLunar()
                self.assertEqual(
                    r["jieqi"]["standard_solar_term"],
                    lunar.getPrevJieQi(False).getName())

    def test_same_instant_same_solar_term_across_representations(self):
        """Regression (ChatGPT review, batch 3; corrected 2026-11-26):
        the research chart of one physical instant must not depend
        on how the instant was written.

        The old version of this test aimed the APPARENT reading 1 s
        before 立春 2026 and asserted the standard term is 立春 while
        the research term is 大寒 -- i.e. it asserted the defect
        (one birth, two terms). Under the corrected semantics both
        terms are fixed by the TRUE instant: the birth below is after
        立春， so both readings carry 立春， the same year/month
        pillars, the same day pillar and the same apparent solar
        time, in either representation (+08:00 or UTC).
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        reps = (birth, birth.astimezone(timezone.utc))
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
        # The birth is after 立春: both terms are 立春 on both sides.
        (std_term, sol_term), = seen_terms
        self.assertEqual(std_term, "立春")
        self.assertEqual(sol_term, "立春")

    def test_near_boundary_no_crossing_keeps_term(self):
        """Near-jieqi-boundary control: a birth 30 min after 立春
        2026 (Beijing lon 116.4074, tz 8) corrects ~28 min back, so
        the apparent reading is still ~2 min after 立春.

        (Docstring corrected 2026-11-26: the term is fixed by the
        TRUE instant, 30 min after 立春 -- the corrected reading's
        position relative to the boundary is irrelevant now. The
        assertions are unchanged: no crossing, term 立春 on both
        sides, year/month pillars unchanged.)
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


# ======================================================================
# True-solar defect fix (2026-11-26): physical-instant counterexamples.
#
# Each test below pins the corrected semantics with one birth whose
# OLD (defective) reading changed the year/month pillars or the solar
# term, and asserts the corrected reading instead: the SAME physical
# instant carries the SAME year pillar, month pillar and solar term
# under both calibers, and ONLY the research-caliber day/hour
# readings (local solar date / shichen) may differ. Every test here
# FAILS on the old code (the old code reported different year/month
# pillars or terms for the same birth) and PASSES on the fixed code.
# Expected pillars were derived independently from the pinned
# provider (``calendar()`` for the true instant plus the research
# day/hour derivation from the apparent solar time as a LOCAL
# reading), not from the module under test.
# ======================================================================


class TrueSolarPhysicalInstantCounterexampleTests(unittest.TestCase):
    def test_urumqi_large_longitude_gap(self):
        """乌鲁木齐 (large longitude gap, -143 min): year/month/term fixed.

        The old code reported 乙巳/己丑/大寒 for the research chart
        (the converted 02:36 reading fed in as an instant, before
        立春）. The corrected code reports 丙午/庚寅/立春 on both
        sides: the true instant (05:00) is after 立春. Only the hour
        pillar differs (丁卯 -> 乙丑）.
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r = compare_standard_vs_true_solar(birth, 87.62, 8)
        d = r["differences"]["pillars"]
        for name, expected in (("year", "丙午"), ("month", "庚寅"),
                               ("day", "己酉")):
            self.assertEqual(d[name]["standard"], expected, name)
            self.assertEqual(d[name]["true_solar"], expected, name)
        self.assertEqual(d["hour"]["standard"], "丁卯")
        self.assertEqual(d["hour"]["true_solar"], "乙丑")
        self.assertFalse(r["jieqi"]["crossed"])
        self.assertEqual(r["jieqi"]["standard_solar_term"], "立春")
        self.assertEqual(r["jieqi"]["true_solar_solar_term"], "立春")

    def test_tokyo_year_month_term_fixed(self):
        """东京 (forward correction, +5 min): year/month/term fixed.

        The old code reported 丙午/庚寅/立春 for the research chart
        (the converted ~05:06 JST reading fed in as an instant,
        past 立春 05:02:08 JST). The corrected code reports 乙巳/己丑/
        大寒 on both sides: the true instant (05:01 JST) is before
        立春. Only the hour pillar differs (丙寅 -> 丁卯, 寅时 -> 卯时）.
        """
        birth = datetime(2026, 2, 4, 5, 1, tzinfo=JST)
        r = compare_standard_vs_true_solar(birth, 139.767, 9)
        d = r["differences"]["pillars"]
        for name, expected in (("year", "乙巳"), ("month", "己丑"),
                               ("day", "己酉")):
            self.assertEqual(d[name]["standard"], expected, name)
            self.assertEqual(d[name]["true_solar"], expected, name)
        self.assertEqual(d["hour"]["standard"], "丙寅")
        self.assertEqual(d["hour"]["true_solar"], "丁卯")
        self.assertFalse(r["jieqi"]["crossed"])
        self.assertEqual(r["jieqi"]["standard_solar_term"], "大寒")
        self.assertEqual(r["jieqi"]["true_solar_solar_term"], "大寒")

    def test_cross_day_honolulu_local_date_only_day_moves(self):
        """跨日 (Honolulu, local date back a day): only day/hour move.

        The old code reported NO pillar change at all (both readings
        fell on 2026-01-01 in Shanghai). The corrected code reports
        the day pillar changing 乙亥 -> 甲戌 -- for the right reason:
        the Shanghai date of the true instant is 2026-01-01 while
        the local solar date is 2025-12-31. Year/month/term are
        fixed (乙巳/戊子/冬至 on both sides).
        """
        birth = datetime(2026, 1, 1, 0, 20,
                         tzinfo=timezone(timedelta(hours=-10)))
        r = compare_standard_vs_true_solar(birth, -157.858, -10)
        d = r["differences"]["pillars"]
        for name, expected in (("year", "乙巳"), ("month", "戊子")):
            self.assertEqual(d[name]["standard"], expected, name)
            self.assertEqual(d[name]["true_solar"], expected, name)
        self.assertEqual(d["day"]["standard"], "乙亥")
        self.assertEqual(d["day"]["true_solar"], "甲戌")
        self.assertEqual(d["hour"]["standard"], "乙酉")
        self.assertEqual(d["hour"]["true_solar"], "甲子")
        self.assertFalse(r["jieqi"]["crossed"])
        self.assertEqual(r["jieqi"]["standard_solar_term"], "冬至")
        self.assertEqual(r["jieqi"]["true_solar_solar_term"], "冬至")

    def test_cross_day_new_york_local_date_agrees(self):
        """跨日 (New York 10:50 EST): day does NOT move although Shanghai would.

        The old code reported the day pillar changing 辛巳 -> 壬午
        (the apparent-as-instant is 00:10 Shanghai, Nov 4). The
        corrected code reports 辛巳 on both sides: the local solar
        date (Nov 3) agrees with the Shanghai date of the true
        instant (Nov 3). Only the hour pillar differs (戊子 -> 甲午）.
        """
        birth = datetime(2026, 11, 3, 10, 50, tzinfo=EST)
        r = compare_standard_vs_true_solar(birth, -74.0060, -5)
        d = r["differences"]["pillars"]
        for name, expected in (("year", "丙午"), ("month", "戊戌"),
                               ("day", "辛巳")):
            self.assertEqual(d[name]["standard"], expected, name)
            self.assertEqual(d[name]["true_solar"], expected, name)
        self.assertEqual(d["hour"]["standard"], "戊子")
        self.assertEqual(d["hour"]["true_solar"], "甲午")
        self.assertFalse(r["jieqi"]["crossed"])

    def test_around_lichun_before_and_after(self):
        """立春前后: two TRUE instants straddling 立春 differ; each agrees with itself.

        The year/month pillars move ONLY between the two births
        (their true instants straddle 立春 04:02:08), never between
        the two calibers of one birth. Before (04:00:30): 乙巳/己丑/
        大寒 on both sides. After (04:03:00): 丙午/庚寅/立春 on both
        sides. Both births are inside the provisional window, so
        both month attributions are undetermined.
        """
        before = datetime(2026, 2, 4, 4, 0, 30, tzinfo=CST)
        after = datetime(2026, 2, 4, 4, 3, 0, tzinfo=CST)
        r_before = compare_standard_vs_true_solar(before, 116.4074, 8)
        r_after = compare_standard_vs_true_solar(after, 116.4074, 8)
        for r, year, month, term in (
                (r_before, "乙巳", "己丑", "大寒"),
                (r_after, "丙午", "庚寅", "立春")):
            with self.subTest(term=term):
                d = r["differences"]["pillars"]
                self.assertEqual(d["year"]["standard"], year)
                self.assertEqual(d["year"]["true_solar"], year)
                self.assertEqual(d["month"]["standard"], month)
                self.assertEqual(d["month"]["true_solar"], month)
                self.assertEqual(d["day"]["standard"], "己酉")
                self.assertEqual(d["day"]["true_solar"], "己酉")
                self.assertFalse(r["jieqi"]["crossed"])
                self.assertEqual(r["jieqi"]["standard_solar_term"], term)
                self.assertEqual(r["jieqi"]["true_solar_solar_term"], term)
                self.assertTrue(r["jieqi"]["within_precision_budget"])
        # The two births differ from EACH OTHER in year/month: only
        # the true instant moves the year/month pillars.
        self.assertNotEqual(
            _pillars(r_before["standard_time_chart"])["year"],
            _pillars(r_after["standard_time_chart"])["year"])
        self.assertNotEqual(
            _pillars(r_before["standard_time_chart"])["month"],
            _pillars(r_after["standard_time_chart"])["month"])

    def test_same_instant_two_longitudes_same_year_month(self):
        """Same physical instant, two longitudes: year/month/term identical.

        One birth (2026-02-04 05:00 CST) charted with the Urumqi
        longitude (correction -143 min) and with the Tokyo longitude
        (correction +65 min, tz 8): the year/month/term are identical
        in all four readings, because they are fixed by the true
        instant. Only the research hour differs (乙丑 vs 丁卯）,
        because the local solar shichen differs.
        """
        birth = datetime(2026, 2, 4, 5, 0, tzinfo=CST)
        r_urumqi = compare_standard_vs_true_solar(birth, 87.62, 8)
        r_tokyo_lon = compare_standard_vs_true_solar(birth, 139.767, 8)
        for r in (r_urumqi, r_tokyo_lon):
            d = r["differences"]["pillars"]
            for name, expected in (("year", "丙午"), ("month", "庚寅"),
                                   ("day", "己酉")):
                self.assertEqual(d[name]["standard"], expected, name)
                self.assertEqual(d[name]["true_solar"], expected, name)
            self.assertEqual(r["jieqi"]["standard_solar_term"], "立春")
            self.assertEqual(r["jieqi"]["true_solar_solar_term"], "立春")
            self.assertFalse(r["jieqi"]["crossed"])
        self.assertEqual(
            r_urumqi["differences"]["pillars"]["hour"]["true_solar"], "乙丑")
        self.assertEqual(
            r_tokyo_lon["differences"]["pillars"]["hour"]["true_solar"], "丁卯")
