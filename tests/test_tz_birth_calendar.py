"""Timezone-aware production calendar (accuracy-audit fix batch F-1).

Public-CI safe: lunar-python + zoneinfo + production calendar modules only.
No private canonical data, no sealed runtime, no EvidenceResolver. Scenario
coverage here is contract-level only (zone keys accepted by scenario
contracts); end-to-end scenario computation with zones lives in
test_tz_scenario_offline.py, which needs the sealed runtime and is NOT in
the public workflow.

Expected pillars are independent of the code under test: day pillars were
cross-checked with sxtwl 2.0.7 (1990-05-15 = 庚辰, 2020-05-15 = 戊午) and
hour pillars follow the standard day-stem clock arithmetic.
"""

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from tianji_kb.bazi_calendar_precision_audit import audit_birth_instant
from tianji_kb.calendar import calendar
from tianji_kb.calendar_tz import DEFAULT_ZONE, calendar_for_zone
from tianji_kb.engine import prepare_inputs
from tianji_kb.runtime_catalog import RuntimeUnavailable
from tianji_kb.scenario_engine import execute_scenario

LONDON = "1990-05-15T14:30:00+01:00"
LONDON_EVENING = "1990-05-15T17:00:00+01:00"
TOKYO_NOON_FIRST_HOUR = "2020-05-15T11:30:00+09:00"
SHANGHAI = "2020-05-15T14:30:00+08:00"
SHANGHAI_DST = "1990-05-15T14:30:00+09:00"


class ShanghaiRegressionTests(unittest.TestCase):
    def test_default_zone_is_shanghai(self):
        self.assertEqual(DEFAULT_ZONE, "Asia/Shanghai")

    def test_non_dst_shanghai_matches_legacy_calendar_exactly(self):
        # Outside DST the new path must be byte-identical to the frozen
        # calendar(), including the solar-term label.
        for value in (SHANGHAI, "2024-02-05T12:00:00+08:00",
                      "2024-02-04T16:25:00+08:00"):
            new = calendar_for_zone(value)
            old = calendar(value)
            self.assertEqual(new["tz_name"], "Asia/Shanghai")
            for key in old:
                self.assertEqual(new[key], old[key], "%s key %s" % (value, key))

    def test_dst_shanghai_matches_legacy_except_jieqi_label(self):
        # 1990-05-15 is inside Shanghai DST (+09:00). The legacy calendar()
        # hardcodes a +08:00 suffix on the jieqi timestamp label even then;
        # the zone-aware path labels it with the true +09:00 offset. Every
        # other key must still match.
        new = calendar_for_zone(SHANGHAI_DST, "Asia/Shanghai")
        old = calendar(SHANGHAI_DST)
        for key in old:
            if key == "solar_term_started_at":
                self.assertTrue(new[key].endswith("+09:00"), new[key])
                self.assertTrue(old[key].endswith("+08:00"), old[key])
            else:
                self.assertEqual(new[key], old[key], key)

    def test_shanghai_pillars(self):
        cal = calendar_for_zone(SHANGHAI)
        self.assertEqual(
            (cal["year_ganzhi"], cal["month_ganzhi"],
             cal["day_ganzhi"], cal["hour_ganzhi"]),
            ("庚子", "辛巳", "戊午", "己未"),
        )


class BirthplaceFrameTests(unittest.TestCase):
    def test_london_afternoon_stays_london_afternoon(self):
        # Track A F1: the old Shanghai-frame code turned London 14:30
        # (未时) into 22:30 (亥时). The zone-aware path keeps 未时.
        cal = calendar_for_zone(LONDON, "Europe/London")
        self.assertEqual(cal["tz_name"], "Europe/London")
        self.assertEqual(cal["local_datetime"], "1990-05-15T14:30:00+01:00")
        self.assertEqual(
            (cal["year_ganzhi"], cal["month_ganzhi"],
             cal["day_ganzhi"], cal["hour_ganzhi"]),
            ("庚午", "辛巳", "庚辰", "癸未"),
        )

    def test_london_evening_keeps_london_day(self):
        # London 17:00 is still 1990-05-15 in London, but past midnight in
        # Shanghai: the old code shifted the day pillar to 辛巳 and the
        # hour to 己丑. Both must stay London-frame.
        cal = calendar_for_zone(LONDON_EVENING, "Europe/London")
        self.assertEqual(cal["day_ganzhi"], "庚辰")
        self.assertEqual(cal["hour_ganzhi"], "乙酉")

    def test_tokyo_first_hour_of_noon(self):
        # Tokyo 11:30 is the first hour of 午时; the old Shanghai-frame
        # code read it as 10:30 (巳时).
        cal = calendar_for_zone(TOKYO_NOON_FIRST_HOUR, "Asia/Tokyo")
        self.assertEqual(cal["day_ganzhi"], "戊午")
        self.assertEqual(cal["hour_ganzhi"], "戊午")

    def test_utc_input_uses_named_zone_frame(self):
        # A UTC instant has no civil ambiguity; the named zone supplies
        # the wall time (London 14:30, not 13:30).
        cal = calendar_for_zone("1990-05-15T13:30:00Z", "Europe/London")
        self.assertEqual(cal["local_datetime"], "1990-05-15T14:30:00+01:00")
        self.assertEqual(cal["hour_ganzhi"], "癸未")

    def test_zi_start_day_boundary_threads_through(self):
        cal = calendar_for_zone(LONDON_EVENING.replace("17:00", "23:30"),
                                "Europe/London", day_boundary="zi-start")
        self.assertEqual(cal["day_ganzhi"], "辛巳")
        self.assertEqual(cal["hour_ganzhi"], "戊子")


class CivilTimeValidationTests(unittest.TestCase):
    def test_gap_rejected_with_input_and_zone(self):
        for value in ("1986-05-04T02:30:00+08:00",
                      "1940-06-01T00:30:00+08:00"):
            with self.assertRaises(ValueError) as ctx:
                calendar_for_zone(value, "Asia/Shanghai")
            self.assertIn(value, str(ctx.exception))
            self.assertIn("Asia/Shanghai", str(ctx.exception))

    def test_wrong_offset_rejected_correct_offset_accepted(self):
        with self.assertRaises(ValueError) as ctx:
            calendar_for_zone("1988-07-01T12:00:00+08:00", "Asia/Shanghai")
        self.assertIn("contradicts", str(ctx.exception))
        cal = calendar_for_zone("1988-07-01T12:00:00+09:00", "Asia/Shanghai")
        self.assertEqual(cal["hour_ganzhi"], "丙午")

    def test_fixed_offset_ambiguity_accepted_via_offset(self):
        # A fixed-offset input carries its own fold disambiguation, so the
        # 1986-09-14 01:30 ambiguity is resolved explicitly, not guessed.
        cal = calendar_for_zone("1986-09-14T01:30:00+08:00", "Asia/Shanghai")
        self.assertEqual(cal["civil_classification"], "ambiguous")
        self.assertEqual(cal["offset_disambiguation"], "explicit_offset")
        self.assertTrue(cal["hour_ganzhi"].endswith("丑"), cal["hour_ganzhi"])

    def test_named_zone_ambiguous_datetime_rejected(self):
        # A bare ZoneInfo datetime in the ambiguous hour has no offset to
        # disambiguate it: refuse rather than guess a fold.
        with self.assertRaises(ValueError):
            calendar_for_zone(
                datetime(1986, 9, 14, 1, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
                "Asia/Shanghai",
            )

    def test_unknown_zone_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            calendar_for_zone(SHANGHAI, "Mars/Olympus")
        self.assertIn("Unknown birth timezone", str(ctx.exception))

    def test_validation_matches_audit_function_on_trap_set(self):
        # The production path must never drift from the audited research
        # validator: same accept/reject verdict on every trap case.
        cases = [
            ("1986-05-04T02:30:00+08:00", "Asia/Shanghai", False),
            ("1940-06-01T00:30:00+08:00", "Asia/Shanghai", False),
            ("1988-07-01T12:00:00+08:00", "Asia/Shanghai", False),
            ("1986-09-14T01:30:00+08:00", "Asia/Shanghai", True),
            (LONDON, "Europe/London", True),
            (SHANGHAI, "Asia/Shanghai", True),
        ]
        for value, zone, accepted in cases:
            try:
                audit_birth_instant(value, tz_name=zone)
                audit_ok = True
            except ValueError:
                audit_ok = False
            try:
                calendar_for_zone(value, zone)
                prod_ok = True
            except ValueError:
                prod_ok = False
            self.assertEqual(audit_ok, accepted, (value, zone))
            self.assertEqual(prod_ok, accepted, (value, zone))


class PrepareInputsTests(unittest.TestCase):
    def test_bazi_london_via_prepare_inputs(self):
        prepared, cal = prepare_inputs(
            "bazi", {"value": LONDON, "zone": "Europe/London"})
        self.assertNotIn("zone", prepared)
        self.assertEqual(cal["day_ganzhi"], "庚辰")
        self.assertEqual(cal["hour_ganzhi"], "癸未")
        self.assertEqual(prepared["year_ganzhi"], "庚午")
        self.assertEqual(prepared["hour_ganzhi"], "癸未")

    def test_missing_zone_rejects_foreign_offset(self):
        # No zone means the documented Asia/Shanghai default; a London
        # offset under that default contradicts tzdb and must fail,
        # not silently recompute in Shanghai time.
        with self.assertRaises(ValueError):
            prepare_inputs("bazi", {"value": LONDON})

    def test_zone_timezone_conflict_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            prepare_inputs("bazi", {
                "value": LONDON, "zone": "Europe/London",
                "timezone": "Asia/Shanghai"})
        self.assertIn("Conflicting birth zones", str(ctx.exception))

    def test_timezone_alias_accepted(self):
        _, cal = prepare_inputs(
            "bazi", {"value": LONDON, "timezone": "Europe/London"})
        self.assertEqual(cal["hour_ganzhi"], "癸未")

    def test_liuyao_liuren_ziwei_share_london_frame(self):
        prepared, _ = prepare_inputs(
            "liuyao", {"value": LONDON, "zone": "Europe/London"})
        self.assertEqual(prepared["day_ganzhi"], "庚辰")
        self.assertEqual(prepared["month_branch"], "巳")
        prepared, _ = prepare_inputs(
            "liuren", {"value": LONDON, "zone": "Europe/London"})
        self.assertEqual(prepared["solar_term"], "立夏")
        self.assertEqual(prepared["day_ganzhi"], "庚辰")
        self.assertEqual(prepared["hour_branch"], "未")
        prepared, _ = prepare_inputs(
            "ziwei", {"value": LONDON, "zone": "Europe/London",
                      "year_boundary": "lunar-new-year"})
        self.assertEqual(prepared["year_ganzhi"], "庚午")
        self.assertEqual(prepared["lunar_month"], 4)
        self.assertEqual(prepared["lunar_day"], 21)
        self.assertEqual(prepared["hour_branch"], "未")

    def test_ziwei_leap_month_still_rejected(self):
        # 2023-04-01 is 闰二月十一: the existing fail-closed rule survives
        # the zone refactor.
        with self.assertRaises(ValueError) as ctx:
            prepare_inputs("ziwei", {
                "value": "2023-04-01T12:00:00+08:00",
                "zone": "Asia/Shanghai",
                "year_boundary": "lunar-new-year"})
        self.assertIn("Leap-lunar-month", str(ctx.exception))

    def test_derived_mixing_still_rejected(self):
        with self.assertRaises(ValueError):
            prepare_inputs("bazi", {
                "value": SHANGHAI, "year_ganzhi": "庚子",
                "zone": "Asia/Shanghai"})

    def test_qimen_gap_rejected_london_refused_shanghai_passes(self):
        with self.assertRaises(ValueError):
            prepare_inputs("qimen", {"value": "1986-05-04T02:30:00+08:00"})
        with self.assertRaises(ValueError) as ctx:
            prepare_inputs("qimen", {"value": LONDON, "zone": "Europe/London"})
        self.assertIn("not yet supported", str(ctx.exception))
        # Shanghai qimen passes validation with value intact and zone popped
        # (chart() itself still runs the frozen Shanghai-frame calendar).
        prepared, cal = prepare_inputs(
            "qimen", {"value": SHANGHAI, "zone": "Asia/Shanghai"})
        self.assertEqual(prepared, {"value": SHANGHAI})
        self.assertIsNone(cal)


class ScenarioContractTests(unittest.TestCase):
    # Contract-key acceptance ONLY (rewritten in TJ-031.2). A scenario
    # handler validates its input keys against the reviewed contract
    # BEFORE anything executes, so in every environment: a bogus key
    # raises the contract ValueError, and a contract-valid call never
    # raises it. What happens after the contract check differs by
    # partition and both outcomes are honest here: in a public checkout
    # the call stops at RuntimeUnavailable (no sealed runtime — that
    # proves key acceptance ONLY, never a computation); under the real
    # runtime the call returns a result, whose scenario_id and
    # determinism are asserted. End-to-end zone computation (correct
    # pillars per zone) is asserted in test_tz_scenario_offline.py,
    # which runs in offline acceptance against the sealed runtime.
    # The F-1 version of these tests asserted RuntimeUnavailable
    # unconditionally, which inverted and failed wherever the runtime
    # actually exists.

    CONTRACT_ERROR = "Scenario input fields do not match the reviewed contract"

    def assert_contract_accepts(self, scenario_id, payload):
        try:
            output = execute_scenario(scenario_id, payload)
        except RuntimeUnavailable:
            return  # public checkout: keys accepted, runtime absent
        self.assertEqual(output["scenario_id"], scenario_id)
        self.assertTrue(output["deterministic"])

    def assert_contract_rejects_bogus_key(self, scenario_id, payload):
        with self.assertRaises(ValueError) as ctx:
            execute_scenario(scenario_id, dict(payload, bogus_key=1))
        self.assertIn(self.CONTRACT_ERROR, str(ctx.exception))

    def test_yearly_contract_accepts_birth_zone(self):
        payload = {
            "birth_value": LONDON, "target_year": 2026,
            "birth_zone": "Europe/London"}
        self.assert_contract_accepts("yearly", payload)
        self.assert_contract_rejects_bogus_key("yearly", payload)

    def test_question_contract_accepts_zone(self):
        payload = {
            "value": LONDON, "yao_values": [9, 7, 7, 7, 7, 7],
            "zone": "Europe/London"}
        self.assert_contract_accepts("question", payload)
        self.assert_contract_rejects_bogus_key("question", payload)

    def test_life_contract_accepts_birth_zone(self):
        payload = {
            "birth_value": LONDON, "target_year": 2026,
            "birth_zone": "Europe/London"}
        self.assert_contract_accepts("life", payload)
        self.assert_contract_rejects_bogus_key("life", payload)

    def test_compatibility_contract_accepts_person_zones(self):
        payload = {
            "person_a_birth_value": LONDON,
            "person_b_birth_value": SHANGHAI,
            "person_a_zone": "Europe/London",
            "person_b_zone": "Asia/Shanghai"}
        self.assert_contract_accepts("compatibility", payload)
        self.assert_contract_rejects_bogus_key("compatibility", payload)


if __name__ == "__main__":
    unittest.main()
