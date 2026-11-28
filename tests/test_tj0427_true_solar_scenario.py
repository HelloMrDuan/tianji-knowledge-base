"""TJ-031.19 / E0427: the ``true-solar`` scenario (batch-5 final-review
remediation, P0-3).

The bazi-profile page calls POST /api/v1/scenarios/public with
``scenario_id: "true-solar"`` and ``input: {value, longitude_deg,
tz_name? | tz_offset?}`` and expects the comparison in
``result.true_solar_comparison``, validated strictly by the frontend
(``api.ts`` : ``assertTrueSolarComparison`` -- entry id,
``research_only === true``, the conversion, both charts, the
differences, the jieqi block, and four pillar rows with
name/standard/true_solar/changed/reason).

What this file proves:

* (a) a case with a real day/hour-pillar change returns the
  comparison with ``changed=true`` on the right pillars and reasons
  (Urumqi: day + hour change; New York: hour-only change);
* (b) a case with no change returns all-unchanged (the frontend's
  own P0-3 input: 2024-02-11T16:27:00+08:00, lon 116.4, Asia/Shanghai);
* (c) invalid longitude / invalid tz fails closed with a clean
  error and no partial result -- locally, because every one of
  those failures raises before the sealed chart computation;
* (d) the scenario is research-only (the record carries
  ``research_only=True`` / ``public=False`` / ``ai=False``; it is
  deliberately NOT a SCENARIOS registry entry -- it has no page of
  its own and the registry is pinned to page-bearing scenarios by
  test_b016 -- and the projected envelope carries only the
  allowlisted fields: no sealed text, no internal identifiers, no
  raw research statements (boundary scan clean).

Live tests: real envelopes through the real backend. They skip in
the public checkout (no sealed data/), like the other real-engine
scenario tests in test_tj0427_scenario_presentations.py, and run in
the offline acceptance. The contract, projection and HTTP
fail-closed tests run locally: invalid inputs fail before any
sealed-data read, and the projection tests build their raw record
from the real pure functions (``apparent_solar_time``,
``validate_tz_offset``) plus hand-written chart pillars.
"""

import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import (
    PUBLIC_SCENARIO_SUBFUNCTIONS,
    _true_solar_unverified_period_years,
    create_app,
)
from tianji_kb.bazi_true_solar_chart import ENTRY_ID
from tianji_kb.bazi_true_solar_public import (
    is_valid_public_true_solar_comparison,
    to_public_true_solar_comparison,
)
from tianji_kb.bazi_true_solar_time import (
    apparent_solar_time,
    tzdb_version,
    validate_tz_offset,
)
from tianji_kb.public_boundary import find_public_boundary_violations
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    execute_scenario,
    execute_true_solar_scenario,
    registry,
)

CST = timezone(timedelta(hours=8))
EST = timezone(timedelta(hours=-5))

# (a) Urumqi 2026-01-01 00:30 CST, lon 87.62: the apparent solar
# time is 2025-12-31 ~22:17 at the birthplace, so the research day
# pillar follows the local solar date (2025-12-31, 甲戌） while the
# standard day pillar follows the Shanghai date (2026-01-01, 乙亥）.
# Pinned values come from test_tj0424_true_solar_time
# (test_cross_day_backwards_urumqi_changes_day_pillar): the hour
# pillar changes too (00:30 子时 vs 22:17 亥时), year/month do not.
URUMQI = {"value": "2026-01-01T00:30:00+08:00",
          "longitude_deg": 87.62, "tz_offset": 8}
# (a) New York 2026-11-03 10:50 EST, lon -74.006: day unchanged
# (辛巳 on both sides), hour 戊子 -> 甲午. Pinned by test_tj0424
# (test_cross_day_forwards_new_york_local_date_unchanged).
NEW_YORK = {"value": "2026-11-03T10:50:00-05:00",
            "longitude_deg": -74.006, "tz_offset": -5}
# (b) The frontend's own P0-3 input: no pillar changes. The chart
# below is the standard-time chart for the 2024-02-11T16:27:00+08:00
# input itself (year 甲辰, month 丙寅, day 乙巳, hour 甲申) — the
# sealed executor returns exactly this in repro22, and the local
# pure calendar agrees; the previous value belonged to a
# ~2024-04-14 chart, not this input.
BEIJING = {"value": "2024-02-11T16:27:00+08:00",
           "longitude_deg": 116.4, "tz_name": "Asia/Shanghai"}
BEIJING_GANZHI = ["甲辰", "丙寅", "乙巳", "甲申"]


def _pillar(name, ganzhi, ten_god, branch, hidden):
    return {
        "name": name, "ganzhi": ganzhi,
        "stem": {"value": ganzhi[0], "element": "木", "polarity": "阳",
                 "ten_god": ten_god},
        "branch": {
            "value": branch,
            "hidden_stems": [{"stem": stem, "ten_god": "比肩"}
                             for stem in hidden]},
    }


def _chart(pillars, local_datetime, day_master_stem):
    return {
        "domain": "bazi", "variant": "ziping-structural-v1",
        "deterministic": True,
        "pillars": copy.deepcopy(pillars),
        "day_master": {"stem": day_master_stem, "element": "木",
                       "polarity": "阳"},
        "branch_relations": [],
        "auxiliary": {"taohua": {"targets": []}},
        "limitations": ["不计算旺衰强弱。"],
        "calendar": {"local_datetime": local_datetime,
                     "solar_term": "冬至",
                     "solar_term_started_at": "2025-12-21 23:04:00+08:00",
                     "year_ganzhi": "乙巳", "month_ganzhi": "戊子",
                     "day_ganzhi": "乙亥", "hour_ganzhi": "丙子",
                     "day_boundary": "midnight",
                     "calendar_provider": "lunar-python==1.4.8",
                     "lunar_year": 2025, "lunar_month": 11,
                     "lunar_day": 12},
    }


def _raw_record():
    """A realistic raw research_dual_time_chart record (Urumqi case).

    The conversion record and the tz validation come from the REAL
    pure functions for this input; the charts, differences, jieqi
    and adapter rows are hand-written in the exact raw shapes
    (pillar ganzhi taken from the pinned test_tj0424 Urumqi case).
    This record exercises the validator/converter locally, where
    the sealed chart computation is unavailable.
    """
    birth = datetime(2026, 1, 1, 0, 30, tzinfo=CST)
    conversion = apparent_solar_time(birth, 87.62, 8)
    validation = validate_tz_offset("Asia/Shanghai", birth, 8.0)
    validation["status"] = "resolved_from_tzdb"
    validation["supplied_offset_hours"] = None
    validation["supplied_offset"] = None
    validation["uncertainty"] = (
        "Offset resolved from IANA tzdb at this instant; resolution "
        "is a lookup, not proof of historical correctness (tzdb "
        "version %s)." % validation["tzdb_version"])
    std = [_pillar("year", "乙巳", "比肩", "巳", ["丙", "戊", "庚"]),
           _pillar("month", "戊子", "比肩", "子", ["癸"]),
           _pillar("day", "乙亥", "日主", "亥", ["壬", "甲"]),
           _pillar("hour", "丙子", "比肩", "子", ["癸"])]
    sol = [_pillar("year", "乙巳", "比肩", "巳", ["丙", "戊", "庚"]),
           _pillar("month", "戊子", "比肩", "子", ["癸"]),
           _pillar("day", "甲戌", "比肩", "戌", ["戊", "辛", "丁"]),
           _pillar("hour", "乙亥", "比肩", "亥", ["壬", "甲"])]
    rows = [
        {"name": "year", "standard": std[0], "true_solar": sol[0],
         "changed": False, "ten_god_reading_changed": False,
         "reason": "The year pillar is fixed by the true birth instant.",
         "detail": {
             "governing_boundary": "lichun",
             "nearest_lichun_utc": "2026-02-04T08:27:00+00:00",
             "minutes_from_true_instant_to_nearest_lichun": 50000.0,
             "attribution_settled": True}},
        {"name": "month", "standard": std[1], "true_solar": sol[1],
         "changed": False, "ten_god_reading_changed": False,
         "reason": "No jieqi was crossed.",
         "detail": {
             "governing_boundary": "jieqi", "crossed_term": None,
             "crossed_term_kind": None, "crossed_at_utc": None,
             "nearest_boundary_term": "冬至",
             "nearest_boundary_term_kind": "气",
             "nearest_boundary_minutes": 10000.0,
             "attribution_settled": True}},
        {"name": "day", "standard": std[2], "true_solar": sol[2],
         "changed": True, "ten_god_reading_changed": True,
         "reason": "The day pillar changed 乙亥 -> 甲戌.",
         "detail": {
             "standard_basis": "shanghai_date",
             "true_solar_basis": "local_solar_date",
             "standard_day_date": "2026-01-01",
             "true_solar_day_date": "2025-12-31",
             "day_boundary": "midnight", "boundary_label": "00:00",
             "minutes_from_standard_instant_to_next_shanghai_boundary":
                 1410.0,
             "minutes_from_apparent_solar_time_to_next_local_boundary":
                 103.0}},
        {"name": "hour", "standard": std[3], "true_solar": sol[3],
         "changed": True, "ten_god_reading_changed": True,
         "reason": "The shichen changed 子时 -> 亥时.",
         "detail": {
             "governing_boundary": "shichen",
             "standard_shichen_branch": "子",
             "true_solar_shichen_branch": "亥",
             "minutes_from_standard_instant_to_next_shichen_boundary":
                 90.0,
             "minutes_from_apparent_solar_time_to_next_shichen_boundary":
                 43.0,
             "next_shichen_boundary_local": "2025-12-31T23:00:00+08:00"}},
    ]
    return {
        "entry": "true-solar-chart-research-v1",
        "method": "modern_engineering",
        "conversion_method": "noaa-solar-calculator-approx-v1",
        "astronomical_basis": "NOAA Global Monitoring Laboratory "
                              "Solar Calculator equations.",
        "research_only": True, "public": False, "ai": False,
        "status": "ok",
        "input": {"birth_local_time": "2026-01-01T00:30:00+08:00",
                  "longitude_deg": 87.62, "tz_offset_hours": 8,
                  "standard_meridian_deg": 120.0,
                  "day_boundary": "midnight",
                  "use_true_solar_time": True},
        "conversion": conversion,
        "standard_time_chart": _chart(std, "2026-01-01T00:30:00+08:00",
                                      "乙"),
        "true_solar_time_chart": _chart(sol, "2025-12-31T22:17:17+08:00",
                                        "甲"),
        "differences": {
            "pillars": {
                "year": {"standard": "乙巳", "true_solar": "乙巳",
                         "changed": False},
                "month": {"standard": "戊子", "true_solar": "戊子",
                          "changed": False},
                "day": {"standard": "乙亥", "true_solar": "甲戌",
                        "changed": True},
                "hour": {"standard": "丙子", "true_solar": "乙亥",
                         "changed": True}},
            "solar_term": {"standard": "冬至", "true_solar": "冬至",
                           "changed": False},
            "chart_date": {"standard": "2026-01-01",
                           "true_solar": "2025-12-31", "changed": True},
            "any_pillar_changed": True,
            "month_pillar_changed": False,
            "year_pillar_changed": False,
            "day_pillar_changed": True,
            "hour_pillar_changed": True},
        "jieqi": {"crossed": False, "crossed_term": None,
                  "crossed_at_utc": None, "crossed_at_local": None,
                  "minutes_from_input_to_boundary": -10000.0,
                  "standard_solar_term": "冬至",
                  "true_solar_solar_term": "冬至",
                  "nearest_boundary_term": "冬至",
                  "nearest_boundary_minutes": 10000.0,
                  "within_precision_budget": False,
                  "uncertainty_window_minutes": 2.0,
                  "uncertainty_window_status": "provisional",
                  "uncertainty_window_adjudication":
                      "T1 (2026-11-25): 2-minute provisional research "
                      "window (NOAA +/-1 min equation-of-time budget "
                      "+ 1 min margin); provisional, not a proven "
                      "maximum error",
                  "note": "The solar-time correction never crosses a "
                          "jieqi."},
        "pillar_comparison": {
            "adapter": "true-solar-pillar-adapter-v1",
            "entry": "true-solar-chart-research-v1",
            "method": "modern_engineering",
            "research_only": True, "public": False, "ai": False,
            "status": "ok",
            "day_master": {
                "standard": {"stem": "乙", "element": "木",
                             "polarity": "阴"},
                "true_solar": {"stem": "甲", "element": "木",
                               "polarity": "阳"},
                "changed": True},
            "pillars": rows,
            "year_and_month_changed_together": False,
            "month_attribution": "settled",
            "month_attribution_settled": True,
            "derived": {"branch_relations_changed": True,
                        "taohua_changed": False},
            "note": "The day master changed.",
            "reuse_note": "Every stem is copied verbatim."},
        "research_api": "true-solar-research-api-v1",
        "tz_validation": validation,
        "provenance": {"research_api": "true-solar-research-api-v1",
                       "entry": "true-solar-chart-research-v1",
                       "adapter": "true-solar-pillar-adapter-v1",
                       "conversion_method":
                           "noaa-solar-calculator-approx-v1",
                       "tzdb_version": tzdb_version(),
                       "jieqi_window_minutes": 2.0,
                       "jieqi_window_status": "provisional"},
        "comparison_note": "The standard-time chart and the "
                           "true-solar-time chart are two separate "
                           "results for the same birth instant.",
        "standard_time_convention_unchanged": True,
    }


def _envelope(record, scenario_id="true-solar"):
    return {
        "scenario_id": scenario_id,
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": {"release_scope": "true_solar_comparison_only",
                   "true_solar_comparison": record},
        "rule_matches": [],
        "trace": [{"step": "true_solar_comparison"}],
        "evidence": {},
        "warnings": [],
        "limitations": ["真太阳时对照是研究入口。"],
    }


def _assert_frontend_shape(test, record):
    """Mirror of the frontend's assertTrueSolarComparison (api.ts).

    The record must carry the entry id, research_only=true, the
    conversion, both charts, the differences, the jieqi block and
    four pillar rows with name/standard/true_solar/changed/reason.
    """
    test.assertIsInstance(record, dict)
    test.assertEqual(record.get("entry"), ENTRY_ID)
    test.assertIs(record.get("research_only"), True)
    for key in ("conversion", "standard_time_chart",
                "true_solar_time_chart", "differences", "jieqi",
                "pillar_comparison"):
        test.assertIsInstance(record.get(key), dict, key)
    rows = record["pillar_comparison"]["pillars"]
    test.assertIsInstance(rows, list)
    test.assertEqual(len(rows), 4)
    for row in rows:
        test.assertIsInstance(row.get("name"), str)
        test.assertIsInstance(row.get("standard"), dict)
        test.assertIsInstance(row.get("true_solar"), dict)
        test.assertIsInstance(row.get("changed"), bool)
        test.assertIsInstance(row.get("reason"), str)


def _live(test, inputs):
    """Real envelope, computed once per input shape.

    Skips the calling test when the sealed runtime is absent
    (same pattern as test_tj0427_scenario_presentations._live).
    """
    try:
        return execute_true_solar_scenario(dict(inputs))
    except Exception as error:  # sealed data absent locally
        test.skipTest("live true-solar needs sealed data: %s" % error)


class TrueSolarExecutorContractTests(unittest.TestCase):
    def test_invalid_longitude_fails_closed(self):
        for bad in (200, 200.0, -180.1, 181, "116.4", None, True):
            with self.subTest(longitude=bad):
                with self.assertRaises(ValueError):
                    execute_true_solar_scenario(
                        {"value": BEIJING["value"],
                         "longitude_deg": bad,
                         "tz_name": "Asia/Shanghai"})
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(longitude=bad):
                with self.assertRaises(ValueError):
                    execute_true_solar_scenario(
                        {"value": BEIJING["value"],
                         "longitude_deg": bad,
                         "tz_name": "Asia/Shanghai"})

    def test_longitude_boundaries_are_accepted_by_validation(self):
        # +/-180 pass the contract and reach the sealed chart
        # computation, which is absent locally: the failure must be
        # the sealed-data error, never a longitude error.
        for longitude in (-180, 180):
            with self.subTest(longitude=longitude):
                try:
                    execute_true_solar_scenario(
                        {"value": BEIJING["value"],
                         "longitude_deg": longitude,
                         "tz_name": "Asia/Shanghai"})
                except ValueError as error:
                    self.fail("boundary longitude rejected: %s" % error)
                except Exception as error:
                    self.assertIn("foundations_v1",
                                  str(error), str(error))

    def test_invalid_tz_fails_closed(self):
        cases = (
            # Unknown IANA zone.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_name": "Mars/Olympus"},
            # Empty zone name.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_name": ""},
            # Non-string zone name.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_name": 8},
            # Offset out of the civil range.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_offset": 15},
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_offset": -13},
            # Offset with sub-minute precision: never rounded.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_offset": 8.001},
            # Offset as a string.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_offset": "8"},
            # No time-zone source at all.
            {"value": BEIJING["value"], "longitude_deg": 116.4},
            # Supplied offset disagrees with tzdb for the instant.
            {"value": BEIJING["value"], "longitude_deg": 116.4,
             "tz_name": "Asia/Shanghai", "tz_offset": 9},
        )
        for inputs in cases:
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    execute_true_solar_scenario(dict(inputs))

    def test_lmt_era_zone_fails_closed(self):
        # Asia/Shanghai in 1850 resolves to local mean time: no
        # civil offset exists, so the entry must refuse rather than
        # round an LMT value into a tz_offset.
        with self.assertRaises(ValueError):
            execute_true_solar_scenario(
                {"value": "1850-06-01T12:00:00+08:00",
                 "longitude_deg": 116.4, "tz_name": "Asia/Shanghai"})

    def test_invalid_birth_fails_closed(self):
        cases = (
            # Naive datetime: no zone to read.
            {"value": "2024-02-11T16:27:00", "longitude_deg": 116.4,
             "tz_name": "Asia/Shanghai"},
            # Not a datetime at all.
            {"value": "not-a-date", "longitude_deg": 116.4,
             "tz_name": "Asia/Shanghai"},
            {"value": 20240211, "longitude_deg": 116.4,
             "tz_name": "Asia/Shanghai"},
            {"value": None, "longitude_deg": 116.4,
             "tz_name": "Asia/Shanghai"},
        )
        for inputs in cases:
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    execute_true_solar_scenario(dict(inputs))

    def test_closed_input_contract(self):
        base = {"value": BEIJING["value"], "longitude_deg": 116.4,
                "tz_name": "Asia/Shanghai"}
        for inputs in (
                {"longitude_deg": 116.4, "tz_name": "Asia/Shanghai"},
                {"value": BEIJING["value"], "tz_name": "Asia/Shanghai"},
                {**base, "day_boundary": "midnight"},
                {**base, "standard_meridian_deg": 120.0},
                {**base, "extra": 1},
                "not-a-dict",
                [("value", BEIJING["value"])]):
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    execute_true_solar_scenario(inputs)

    def test_executor_returns_research_record_untouched(self):
        record = _raw_record()
        with patch(
                "tianji_kb.bazi_true_solar_chart."
                "research_dual_time_chart",
                return_value=record) as stub:
            envelope = execute_true_solar_scenario(dict(BEIJING))
        stub.assert_called_once_with(
            BEIJING["value"], 116.4, tz_name="Asia/Shanghai",
            tz_offset=None)
        self.assertEqual(envelope["scenario_id"], "true-solar")
        self.assertEqual(envelope["status"], "production_limited")
        self.assertIs(envelope["public_release"], False)
        self.assertIs(envelope["deterministic"], True)
        self.assertEqual(envelope["result"]["release_scope"],
                         "true_solar_comparison_only")
        # The executor is a thin shell: the record is returned
        # exactly as the research entry produced it, never
        # re-computed or merged.
        self.assertIs(envelope["result"]["true_solar_comparison"],
                      record)
        self.assertEqual(envelope["rule_matches"], [])
        self.assertEqual(envelope["evidence"], {})
        _assert_frontend_shape(self, record)

    def test_unverified_period_helper(self):
        # TJ-031.7: 1900-1948 is refused on the public path, in the
        # request's own time-zone frame (zone name or fixed offset).
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "1940-06-15T12:00:00+08:00",
                 "tz_name": "Asia/Shanghai"}),
            [1940])
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "1940-06-15T12:00:00-05:00",
                 "tz_offset": -5}),
            [1940])
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "1948-12-31T23:30:00-05:00",
                 "tz_offset": -5}),
            [1948])
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "1949-01-01T00:30:00+08:00",
                 "tz_name": "Asia/Shanghai"}),
            [])
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "2024-02-11T16:27:00+08:00",
                 "tz_name": "Asia/Shanghai"}),
            [])
        self.assertEqual(
            _true_solar_unverified_period_years(
                {"value": "not-a-date", "tz_name": "Asia/Shanghai"}),
            [])


class TrueSolarLiveTests(unittest.TestCase):
    def test_day_and_hour_pillars_change_urumqi(self):
        envelope = _live(self, URUMQI)
        record = envelope["result"]["true_solar_comparison"]
        _assert_frontend_shape(self, record)
        self.assertIs(record["research_only"], True)
        self.assertIs(record["public"], False)
        self.assertIs(record["ai"], False)
        differences = record["differences"]
        self.assertTrue(differences["day_pillar_changed"])
        self.assertEqual(differences["pillars"]["day"]["standard"],
                         "乙亥")
        self.assertEqual(differences["pillars"]["day"]["true_solar"],
                         "甲戌")
        self.assertTrue(differences["hour_pillar_changed"])
        self.assertFalse(differences["year_pillar_changed"])
        self.assertFalse(differences["month_pillar_changed"])
        self.assertTrue(differences["any_pillar_changed"])
        self.assertEqual(differences["chart_date"]["standard"],
                         "2026-01-01")
        self.assertEqual(differences["chart_date"]["true_solar"],
                         "2025-12-31")
        rows = {row["name"]: row
                for row in record["pillar_comparison"]["pillars"]}
        self.assertTrue(rows["day"]["changed"])
        self.assertTrue(rows["hour"]["changed"])
        self.assertFalse(rows["year"]["changed"])
        self.assertFalse(rows["month"]["changed"])
        for name in ("year", "month", "day", "hour"):
            self.assertTrue(rows[name]["reason"],
                            "pillar %s carries no reason" % name)
        # The day master follows the day pillar, so the ten-god
        # readings are recomputed against the new day master.
        self.assertTrue(
            record["pillar_comparison"]["day_master"]["changed"])
        # The standard chart is untouched: identical to the
        # standard-time charting of the same instant.
        from tianji_kb.bazi_core import chart_from_datetime
        standard = record["standard_time_chart"]
        self.assertEqual(
            [item["ganzhi"] for item in standard["pillars"]],
            [item["ganzhi"] for item in
             chart_from_datetime(URUMQI["value"])["pillars"]])

    def test_hour_only_change_new_york(self):
        envelope = _live(self, NEW_YORK)
        record = envelope["result"]["true_solar_comparison"]
        _assert_frontend_shape(self, record)
        differences = record["differences"]
        self.assertFalse(differences["day_pillar_changed"])
        self.assertEqual(differences["pillars"]["day"]["standard"],
                         "辛巳")
        self.assertEqual(differences["pillars"]["day"]["true_solar"],
                         "辛巳")
        self.assertTrue(differences["hour_pillar_changed"])
        self.assertEqual(differences["pillars"]["hour"]["standard"],
                         "戊子")
        self.assertEqual(differences["pillars"]["hour"]["true_solar"],
                         "甲午")
        self.assertFalse(differences["year_pillar_changed"])
        self.assertFalse(differences["month_pillar_changed"])

    def test_no_change_beijing(self):
        envelope = _live(self, BEIJING)
        record = envelope["result"]["true_solar_comparison"]
        _assert_frontend_shape(self, record)
        differences = record["differences"]
        self.assertFalse(differences["any_pillar_changed"])
        for name in ("year", "month", "day", "hour"):
            self.assertFalse(differences["pillars"][name]["changed"],
                             name)
        self.assertEqual(
            [differences["pillars"][name]["standard"]
             for name in ("year", "month", "day", "hour")],
            BEIJING_GANZHI)
        self.assertEqual(
            record["pillar_comparison"]["month_attribution"], "settled")
        self.assertIs(
            record["pillar_comparison"]["month_attribution_settled"],
            True)
        tz_validation = record["tz_validation"]
        self.assertEqual(tz_validation["status"], "resolved_from_tzdb")
        self.assertEqual(tz_validation["tz_name"], "Asia/Shanghai")
        self.assertIsInstance(tz_validation["tzdb_version"], str)
        self.assertTrue(tz_validation["tzdb_version"])

    def test_live_projected_envelope_passes_frontend_shape(self):
        envelope = _live(self, BEIJING)
        projected = project_execution(envelope)
        record = projected["result"]["true_solar_comparison"]
        _assert_frontend_shape(self, record)
        self.assertEqual(find_public_boundary_violations(projected),
                         [])
        # The projected record is JSON-serialisable: no datetime
        # objects survive the projection.
        json.dumps(projected, ensure_ascii=False)


class TrueSolarProjectionTests(unittest.TestCase):
    def test_validator_accepts_real_shaped_record(self):
        self.assertTrue(
            is_valid_public_true_solar_comparison(_raw_record()))

    def test_projection_is_exact_allowlist(self):
        public = to_public_true_solar_comparison(_raw_record())
        self.assertEqual(set(public), {
            "entry", "research_only", "public", "ai", "status",
            "method", "input", "conversion", "standard_time_chart",
            "true_solar_time_chart", "differences", "jieqi",
            "pillar_comparison", "tz_validation", "comparison_note"})
        self.assertIs(public["research_only"], True)
        self.assertIs(public["public"], False)
        self.assertIs(public["ai"], False)
        # Internal identifiers / bibliographic strings are gone.
        for banned in ("provenance", "research_api",
                       "conversion_method", "astronomical_basis",
                       "standard_time_convention_unchanged"):
            self.assertNotIn(banned, public, banned)
        # Conversion: only the twelve fields the page renders.
        self.assertEqual(set(public["conversion"]), {
            "apparent_solar_time", "input_local_time", "input_date",
            "apparent_date", "date_shifted", "date_shift_days",
            "longitude_deg", "tz_offset_hours",
            "standard_meridian_deg", "longitude_correction_minutes",
            "equation_of_time_minutes", "total_correction_minutes"})
        self.assertIsInstance(
            public["conversion"]["apparent_solar_time"], str)
        self.assertEqual(
            public["conversion"]["apparent_solar_time"],
            "2025-12-31T22:17:17.747856+08:00")
        self.assertEqual(public["conversion"]["date_shift_days"], -1)
        # Charts: pillars + day master + local datetime only.
        for key in ("standard_time_chart", "true_solar_time_chart"):
            self.assertEqual(set(public[key]), {
                "pillars", "day_master", "calendar"})
            self.assertEqual(set(public[key]["calendar"]),
                             {"local_datetime"})
            self.assertEqual(
                [item["ganzhi"]
                 for item in public[key]["pillars"]],
                ["乙巳", "戊子",
                 "乙亥" if key == "standard_time_chart" else "甲戌",
                 "丙子" if key == "standard_time_chart" else "乙亥"])
        # Jieqi: the long note is dropped, the flags stay.
        self.assertNotIn("note", public["jieqi"])
        self.assertIs(public["jieqi"]["within_precision_budget"],
                      False)
        # Pillar rows: name/standard/true_solar/changed/reason only.
        rows = public["pillar_comparison"]["pillars"]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(set(row), {
                "name", "standard", "true_solar", "changed", "reason"})
        self.assertEqual(
            [row["name"] for row in rows],
            ["year", "month", "day", "hour"])
        day = rows[2]
        self.assertEqual(day["standard"]["ganzhi"], "乙亥")
        self.assertEqual(day["true_solar"]["ganzhi"], "甲戌")
        self.assertIs(day["changed"], True)
        self.assertNotIn("detail", day)
        self.assertNotIn("ten_god_reading_changed", day)
        # Adapter prose blocks are dropped.
        self.assertNotIn("derived", public["pillar_comparison"])
        self.assertNotIn("note", public["pillar_comparison"])
        self.assertNotIn("reuse_note", public["pillar_comparison"])
        # tz validation: status + version stay, prose goes.
        self.assertEqual(set(public["tz_validation"]), {
            "tz_name", "instant", "tzdb_offset_hours", "tzdb_offset",
            "tzdb_offset_is_whole_minutes", "supplied_offset_hours",
            "supplied_offset", "matches", "status", "tzdb_version"})
        self.assertEqual(public["tz_validation"]["status"],
                         "resolved_from_tzdb")
        _assert_frontend_shape(self, public)
        json.dumps(public, ensure_ascii=False)

    def test_validator_rejects_tampered_records(self):
        base = _raw_record()
        tampered = copy.deepcopy(base)
        tampered["research_only"] = False
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["public"] = True
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["extra_key"] = "forged"
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["entry"] = "something-else-v1"
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["differences"]["pillars"]["day"]["changed"] = False
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["pillar_comparison"]["pillars"] = \
            tampered["pillar_comparison"]["pillars"][:3]
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        tampered = copy.deepcopy(base)
        tampered["pillar_comparison"]["pillars"][2]["reason"] = ""
        self.assertFalse(
            is_valid_public_true_solar_comparison(tampered))
        with self.assertRaises(ValueError):
            to_public_true_solar_comparison(tampered)

    def test_projection_releases_only_on_true_solar(self):
        projected = project_execution(_envelope(_raw_record()))
        self.assertIn("true_solar_comparison",
                      projected["result"])
        _assert_frontend_shape(
            self, projected["result"]["true_solar_comparison"])
        self.assertEqual(
            find_public_boundary_violations(projected), [])
        # The release_scope survives the projection untouched.
        self.assertEqual(projected["result"]["release_scope"],
                         "true_solar_comparison_only")
        # A forged copy on any other scenario is stripped.
        forged = _envelope(_raw_record(), scenario_id="bazi-profile")
        projected_forged = project_execution(forged)
        self.assertNotIn("true_solar_comparison",
                         projected_forged["result"])
        # A tampered record on the true-solar scenario is stripped
        # too -- the projection never releases a partial record.
        tampered = copy.deepcopy(_raw_record())
        tampered["research_only"] = False
        projected_tampered = project_execution(_envelope(tampered))
        self.assertNotIn("true_solar_comparison",
                         projected_tampered["result"])

    def test_projection_does_not_mutate_raw_record(self):
        record = _raw_record()
        snapshot = copy.deepcopy(record)
        # The raw conversion carries datetime objects; deepcopy the
        # snapshot for comparison (datetimes compare by value).
        to_public_true_solar_comparison(record)
        project_execution(_envelope(record))
        self.assertEqual(record, snapshot)


class TrueSolarRegistrationTests(unittest.TestCase):
    def test_not_a_registered_product_scenario(self):
        # The registry is the inventory of page-bearing product
        # scenarios (pinned by test_b016): true-solar has no page
        # of its own, so it is deliberately absent, and the
        # registry still holds exactly the eleven product scenarios.
        rows = {item["id"]: item for item in registry()}
        self.assertEqual(len(rows), 11)
        self.assertNotIn("true-solar", rows)
        with self.assertRaises(ValueError):
            execute_scenario("true-solar", dict(BEIJING))

    def test_envelope_flags_are_research_only(self):
        record = _raw_record()
        with patch(
                "tianji_kb.bazi_true_solar_chart."
                "research_dual_time_chart",
                return_value=record):
            envelope = execute_true_solar_scenario(dict(BEIJING))
        comparison = envelope["result"]["true_solar_comparison"]
        self.assertIs(comparison["research_only"], True)
        self.assertIs(comparison["public"], False)
        self.assertIs(comparison["ai"], False)
        self.assertIs(envelope["public_release"], False)
        self.assertEqual(envelope["status"], "production_limited")


class TrueSolarHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(TestClient(create_app()))

    def test_invalid_input_returns_422_invalid_scenario_input(self):
        for inputs in (
                {"value": BEIJING["value"], "longitude_deg": 200,
                 "tz_name": "Asia/Shanghai"},
                {"value": BEIJING["value"], "longitude_deg": 116.4,
                 "tz_name": "Mars/Olympus"},
                {"value": BEIJING["value"], "longitude_deg": 116.4},
                {"value": "2024-02-11T16:27:00", "longitude_deg": 116.4,
                 "tz_name": "Asia/Shanghai"},
                {"value": BEIJING["value"], "longitude_deg": 116.4,
                 "tz_name": "Asia/Shanghai", "extra": 1}):
            with self.subTest(inputs=inputs):
                response = self.client.post(
                    "/api/v1/scenarios/public",
                    json={"scenario_id": "true-solar", "input": inputs})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(
                    response.json()["detail"]["code"],
                    "invalid_scenario_input")

    def test_unknown_scenario_still_refused(self):
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "nope", "input": {}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"],
                         "unsupported_public_scenario")

    def test_registry_endpoint_does_not_list_true_solar(self):
        response = self.client.get("/api/v1/scenarios")
        self.assertEqual(response.status_code, 200)
        ids = [item["id"]
               for item in response.json()["scenarios"]]
        self.assertEqual(len(ids), 11)
        self.assertNotIn("true-solar", ids)

    def test_valid_request_returns_projected_comparison(self):
        # Live: skips in the public checkout (no sealed data/).
        try:
            envelope = execute_true_solar_scenario(dict(BEIJING))
        except Exception as error:
            self.skipTest(
                "live true-solar needs sealed data: %s" % error)
        self.assertIsNotNone(envelope)
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "true-solar", "input": dict(BEIJING)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["scenario_id"], "true-solar")
        self.assertIs(body["public_release"], False)
        record = body["result"]["true_solar_comparison"]
        _assert_frontend_shape(self, record)
        self.assertEqual(find_public_boundary_violations(body), [])

    def test_unverified_period_is_refused(self):
        # Live: skips in the public checkout (no sealed data/).
        # In the sealed runtime the execution succeeds and the
        # TJ-031.7 boundary refuses the 1900-1948 birth.
        try:
            execute_true_solar_scenario(
                {"value": "1940-06-15T12:00:00+08:00",
                 "longitude_deg": 116.4, "tz_name": "Asia/Shanghai"})
        except Exception as error:
            self.skipTest(
                "live true-solar needs sealed data: %s" % error)
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "true-solar",
                  "input": {"value": "1940-06-15T12:00:00+08:00",
                            "longitude_deg": 116.4,
                            "tz_name": "Asia/Shanghai"}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"],
                         "unverified_birth_period")


class TrueSolarAdmissionTests(unittest.TestCase):
    """TJ-031.19 / E0427 closing fix: true-solar admission.

    True-solar is NOT a 12th scenario and has no page: it stays out
    of the SCENARIOS registry (exactly 11, pinned by test_b016) and
    reaches an executor only through the one named admission point,
    PUBLIC_SCENARIO_SUBFUNCTIONS in tianji_kb.api -- an explicit
    id -> executor table. A dedicated endpoint was rejected: it
    would duplicate the shared post-execution boundary/projection
    logic and force a frontend contract change, while the allowlist
    leaves the frontend call (POST /api/v1/scenarios/public,
    scenario_id "true-solar") untouched.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(TestClient(create_app()))

    def test_allowlist_admits_exactly_true_solar(self):
        self.assertEqual(set(PUBLIC_SCENARIO_SUBFUNCTIONS),
                         {"true-solar"})
        self.assertIs(PUBLIC_SCENARIO_SUBFUNCTIONS["true-solar"],
                      execute_true_solar_scenario)
        rows = {item["id"]: item for item in registry()}
        self.assertEqual(len(rows), 11)
        self.assertNotIn("true-solar", rows)
        with self.assertRaises(ValueError):
            execute_scenario("true-solar", dict(BEIJING))

    def test_allowed_true_solar_call_succeeds_over_http(self):
        # Stubbed at the research entry, not the executor: the
        # request must pass admission, execute, project, and return
        # the frontend-shaped comparison -- locally, where the
        # sealed chart computation is absent.
        record = _raw_record()
        with patch(
                "tianji_kb.bazi_true_solar_chart."
                "research_dual_time_chart",
                return_value=record):
            response = self.client.post(
                "/api/v1/scenarios/public",
                json={"scenario_id": "true-solar",
                      "input": dict(BEIJING)})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["scenario_id"], "true-solar")
        self.assertIs(body["public_release"], False)
        _assert_frontend_shape(
            self, body["result"]["true_solar_comparison"])
        self.assertEqual(find_public_boundary_violations(body), [])

    def test_unapproved_scenario_ids_are_rejected(self):
        # Near-misses must not ride the admission point, and a
        # registered-but-not-public scenario (dream) must not pass
        # the registry-status gate either.
        for scenario_id in (
                "true-solar2", "true-solar-chart", "TRUE-SOLAR",
                "true_solar", "bazi-profile-true-solar", "nope",
                "dream"):
            with self.subTest(scenario_id=scenario_id):
                response = self.client.post(
                    "/api/v1/scenarios/public",
                    json={"scenario_id": scenario_id,
                          "input": dict(BEIJING)})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(
                    response.json()["detail"]["code"],
                    "unsupported_public_scenario")

    def test_true_solar_invalid_input_still_422s(self):
        response = self.client.post(
            "/api/v1/scenarios/public",
            json={"scenario_id": "true-solar",
                  "input": {"value": BEIJING["value"],
                            "longitude_deg": 200,
                            "tz_name": "Asia/Shanghai"}})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"],
                         "invalid_scenario_input")

    def test_registry_endpoint_still_lists_exactly_eleven(self):
        response = self.client.get("/api/v1/scenarios")
        self.assertEqual(response.status_code, 200)
        ids = [item["id"] for item in response.json()["scenarios"]]
        self.assertEqual(len(ids), 11)
        self.assertNotIn("true-solar", ids)


if __name__ == "__main__":
    unittest.main()
