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
