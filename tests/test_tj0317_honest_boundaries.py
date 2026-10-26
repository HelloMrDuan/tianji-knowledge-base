"""TJ-031.7 honest boundaries: the 1900-1948 public production gate
and the solar-term precision note.

Task A: backend calendar conversion for 1900-1948 has never been
independently cross-checked (Track B evidence gap), while the
frontend already limits birth years to 1949-2099. The public handlers
in api.py refuse that period with HTTP 422 after a successful
execution, deciding via the pure helpers in public_projection; the
internal and eval paths never pass through those helpers. These tests
pin the helpers and the calendar-level facts they rely on.

Task B: solar-term instants diverge by up to ~14 seconds between
independent sources (2024 Lichun: lunar-python 08:27:07Z, sxtwl
08:26:53Z, JPL Horizons 08:27:00Z). calendar_for_zone flags births
within 60 seconds of the nearest term instant via
solar_term_precision_note instead of presenting the year/month
attribution as exact.

Public-CI safe: lunar-python + zoneinfo + public_projection + engine
prepare_inputs only, same partition as test_tz_birth_calendar.py.
HTTP-level wiring of the handlers is exercised in offline acceptance
(the public checkout has no sealed runtime), like
test_public_execution_projection_api.py.
"""

import unittest

from tianji_kb.calendar_tz import calendar_for_zone, precision_note_for
from tianji_kb.engine import prepare_inputs
from tianji_kb.public_projection import (
    UNVERIFIED_PERIOD_CODE,
    UNVERIFIED_PERIOD_MESSAGE,
    calendar_local_year,
    scenario_unverified_period_years,
    unverified_period_year,
)

AUDIT_MESSAGE = (
    "claimed UTC offset 8:00:00 contradicts tzdb for civil time "
    "1900-01-07T12:00:00 in Asia/Shanghai; historical offset misuse "
    "is rejected"
)


class UnverifiedPeriodGateTests(unittest.TestCase):
    def test_period_bounds(self):
        self.assertFalse(unverified_period_year(1899))
        self.assertTrue(unverified_period_year(1900))
        self.assertTrue(unverified_period_year(1948))
        self.assertFalse(unverified_period_year(1949))
        self.assertFalse(unverified_period_year(None))
        self.assertFalse(unverified_period_year("1948"))

    def test_gate_contract_constants(self):
        self.assertEqual(UNVERIFIED_PERIOD_CODE, "unverified_birth_period")
        self.assertIn("未经独立核对", UNVERIFIED_PERIOD_MESSAGE)
        self.assertIn("不提供", UNVERIFIED_PERIOD_MESSAGE)

    def test_1948_winter_birth_is_gated(self):
        # January 1948 Shanghai is on standard time (+08:00), so this
        # input passes the tz audit and computes today.
        cal = calendar_for_zone("1948-01-15T12:00:00+08:00", "Asia/Shanghai")
        self.assertEqual(calendar_local_year(cal), 1948)
        self.assertTrue(unverified_period_year(calendar_local_year(cal)))

    def test_1900_birth_with_exact_tzdb_offset_is_gated(self):
        # The claimed offset equals the tzdb offset for that civil
        # time (+08:05:43), so the audit accepts and it computes.
        cal = calendar_for_zone(
            "1900-06-01T12:00:00+08:05:43", "Asia/Shanghai")
        self.assertEqual(calendar_local_year(cal), 1900)
        self.assertTrue(unverified_period_year(calendar_local_year(cal)))

    def test_1949_birth_is_not_gated(self):
        # Positive control: 1949-01-01 onward is unaffected.
        cal = calendar_for_zone("1949-01-01T08:00:00+08:00", "Asia/Shanghai")
        self.assertEqual(cal["local_datetime"], "1949-01-01T08:00:00+08:00")
        self.assertEqual(calendar_local_year(cal), 1949)
        self.assertFalse(unverified_period_year(calendar_local_year(cal)))

    def test_scenario_daily_birth_in_period(self):
        years = scenario_unverified_period_years(
            {"birth_value": "1935-05-01T12:00:00+08:00",
             "target_date": "2026-01-01"},
            "daily",
        )
        self.assertEqual(years, [1935])

    def test_scenario_compatibility_second_person_in_period(self):
        years = scenario_unverified_period_years(
            {"person_a_birth_value": "1990-05-01T12:00:00+08:00",
             "person_b_birth_value": "1920-03-01T12:00:00+08:00"},
            "compatibility",
        )
        self.assertEqual(years, [1920])

    def test_scenario_question_value_is_not_a_birth(self):
        years = scenario_unverified_period_years(
            {"value": "1935-05-01T12:00:00+08:00",
             "yao_values": [7, 7, 7, 7, 7, 7]},
            "question",
        )
        self.assertEqual(years, [])

    def test_scenario_bazi_profile_value_is_a_birth(self):
        years = scenario_unverified_period_years(
            {"value": "1935-05-01T12:00:00+08:00"},
            "bazi-profile",
        )
        self.assertEqual(years, [1935])

    def test_scenario_zone_frame_decides_the_year(self):
        # The string year is 1949, but in the birth zone frame
        # (America/New_York) the local civil year is 1948: the gate
        # follows the audited frame, not the raw string.
        years = scenario_unverified_period_years(
            {"birth_value": "1949-01-01T00:30:00+08:00",
             "birth_zone": "America/New_York",
             "target_date": "2026-01-01"},
            "daily",
        )
        self.assertEqual(years, [1948])

    def test_qimen_internal_rejection_reason_unchanged(self):
        # The eval-boundary-05 surface: the internal qimen path must
        # keep rejecting 1900-01-07 +08:00 with the exact tzdb audit
        # message; the public period gate must not preempt it.
        with self.assertRaises(ValueError) as ctx:
            prepare_inputs("qimen", {"value": "1900-01-07T12:00:00+08:00"})
        self.assertIn(AUDIT_MESSAGE, str(ctx.exception))


class SolarTermPrecisionNoteTests(unittest.TestCase):
    # 2024 Lichun provider instant: 2024-02-04T08:27:07Z
    # (China wall reading 16:27:07 minus the 8h baseline).

    def test_shanghai_thirty_seconds_after_lichun(self):
        cal = calendar_for_zone(
            "2024-02-04T16:27:37+08:00", "Asia/Shanghai")
        note = cal["solar_term_precision_note"]
        self.assertIsNotNone(note)
        self.assertIn("30 秒", note)
        self.assertIn("lunar-python", note)
        self.assertIn("sxtwl", note)
        self.assertIn("JPL", note)
        self.assertIn("秒", note)

    def test_london_thirty_seconds_after_lichun(self):
        cal = calendar_for_zone(
            "2024-02-04T08:27:37+00:00", "Europe/London")
        self.assertIsNotNone(cal["solar_term_precision_note"])

    def test_london_thirty_seconds_before_lichun(self):
        # Before the term, the nearest term is the NEXT one (Lichun);
        # the previous term (Dahan) is weeks away.
        cal = calendar_for_zone(
            "2024-02-04T08:26:37+00:00", "Europe/London")
        self.assertIsNotNone(cal["solar_term_precision_note"])

    def test_window_edge_sixty_seconds_still_flagged(self):
        cal = calendar_for_zone(
            "2024-02-04T16:28:07+08:00", "Asia/Shanghai")
        self.assertIsNotNone(cal["solar_term_precision_note"])

    def test_one_hour_after_lichun_not_flagged(self):
        cal = calendar_for_zone(
            "2024-02-04T17:27:07+08:00", "Asia/Shanghai")
        self.assertIsNone(cal["solar_term_precision_note"])

    def test_sixty_one_seconds_after_lichun_not_flagged(self):
        cal = calendar_for_zone(
            "2024-02-04T16:28:08+08:00", "Asia/Shanghai")
        self.assertIsNone(cal["solar_term_precision_note"])

    def test_precision_note_for_matches_calendar_output(self):
        note = precision_note_for(
            "2024-02-04T16:27:37+08:00", "Asia/Shanghai")
        cal = calendar_for_zone(
            "2024-02-04T16:27:37+08:00", "Asia/Shanghai")
        self.assertEqual(note, cal["solar_term_precision_note"])
        self.assertIsNotNone(note)


if __name__ == "__main__":
    unittest.main()
