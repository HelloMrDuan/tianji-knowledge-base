"""End-to-end scenario zone threading (accuracy-audit fix batch F-1).

OFFLINE / PRIVATE-CI ONLY. Requires the sealed production runtime and the
private canonical data: full execute_scenario() raises RuntimeUnavailable
in a public checkout. DO NOT add this file to .github/workflows/validate.yml;
it runs in offline acceptance (--suite all discovers every test module).

NOT YET EXECUTED in the F-1 round that authored it (no sealed runtime is
available in the authoring sandbox): run it in offline acceptance before
claiming scenario-level zone coverage. Expected pillars are the same
birthplace-frame values already verified at the prepare_inputs level in
test_tz_birth_calendar.py, so any failure here points at scenario
threading, not at the calendar itself.
"""

import unittest

from tianji_kb.scenario_engine import execute_scenario

LONDON = "1990-05-15T14:30:00+01:00"
LONDON_EVENING = "1990-05-15T17:00:00+01:00"
TOKYO_NOON_FIRST_HOUR = "2020-05-15T11:30:00+09:00"
SHANGHAI = "2020-05-15T14:30:00+08:00"

LONDON_PILLARS = [("庚", "午"), ("辛", "巳"), ("庚", "辰"), ("癸", "未")]
LONDON_EVENING_PILLARS = [("庚", "午"), ("辛", "巳"), ("庚", "辰"), ("乙", "酉")]
TOKYO_PILLARS = [("庚", "子"), ("辛", "巳"), ("戊", "午"), ("戊", "午")]
SHANGHAI_PILLARS = [("庚", "子"), ("辛", "巳"), ("戊", "午"), ("己", "未")]


def pillars_of(result_pillars):
    return [
        (p["stem"]["value"], p["branch"]["value"])
        for p in result_pillars
    ]


class ScenarioZoneThreadingTests(unittest.TestCase):
    def test_bazi_profile_london(self):
        output = execute_scenario("bazi-profile", {
            "value": LONDON, "zone": "Europe/London"})
        self.assertEqual(
            pillars_of(output["result"]["natal"]["pillars"]), LONDON_PILLARS)
        self.assertEqual(output["result"]["day_master"]["stem"], "庚")

    def test_bazi_profile_london_evening_keeps_day(self):
        output = execute_scenario("bazi-profile", {
            "value": LONDON_EVENING, "zone": "Europe/London"})
        self.assertEqual(
            pillars_of(output["result"]["natal"]["pillars"]),
            LONDON_EVENING_PILLARS)

    def test_bazi_profile_tokyo_noon_first_hour(self):
        output = execute_scenario("bazi-profile", {
            "value": TOKYO_NOON_FIRST_HOUR, "zone": "Asia/Tokyo"})
        self.assertEqual(
            pillars_of(output["result"]["natal"]["pillars"]), TOKYO_PILLARS)

    def test_bazi_profile_shanghai_regression(self):
        output = execute_scenario("bazi-profile", {"value": SHANGHAI})
        self.assertEqual(
            pillars_of(output["result"]["natal"]["pillars"]), SHANGHAI_PILLARS)

    def test_yearly_romance_career_share_london_natal(self):
        for scenario in ("yearly", "romance", "career"):
            output = execute_scenario(scenario, {
                "birth_value": LONDON, "target_year": 2026,
                "birth_zone": "Europe/London"})
            self.assertEqual(
                pillars_of(output["result"]["natal"]["pillars"]),
                LONDON_PILLARS, scenario)
            self.assertEqual(
                output["result"]["target_year"]["ganzhi"], "丙午", scenario)

    def test_daily_weekly_monthly_share_london_natal(self):
        cases = [
            ("daily", {"birth_value": LONDON, "target_date": "2026-10-04"}),
            ("weekly", {"birth_value": LONDON, "anchor_date": "2026-10-05"}),
            ("monthly", {"birth_value": LONDON, "target_month": "2026-10"}),
        ]
        for scenario, payload in cases:
            payload["birth_zone"] = "Europe/London"
            output = execute_scenario(scenario, payload)
            self.assertEqual(
                pillars_of(output["result"]["natal"]["pillars"]),
                LONDON_PILLARS, scenario)

    def test_life_four_sources_identical_under_zone(self):
        output = execute_scenario("life", {
            "birth_value": LONDON, "target_year": 2026,
            "birth_zone": "Europe/London"})
        self.assertTrue(output["result"]["all_natal_charts_identical"])
        self.assertTrue(output["result"]["all_target_years_identical"])

    def test_compatibility_mixed_zones(self):
        output = execute_scenario("compatibility", {
            "person_a_birth_value": LONDON,
            "person_b_birth_value": SHANGHAI,
            "person_a_zone": "Europe/London",
            "person_b_zone": "Asia/Shanghai"})
        self.assertEqual(
            pillars_of(output["result"]["person_a"]["pillars"]), LONDON_PILLARS)
        self.assertEqual(
            pillars_of(output["result"]["person_b"]["pillars"]),
            SHANGHAI_PILLARS)

    def test_question_accepts_zone_end_to_end(self):
        output = execute_scenario("question", {
            "value": LONDON, "yao_values": [9, 7, 7, 7, 7, 7],
            "zone": "Europe/London"})
        self.assertEqual(output["result"]["changing_lines"], [1])
        self.assertEqual(output["result"]["changed"]["number"], 44)


if __name__ == "__main__":
    unittest.main()
