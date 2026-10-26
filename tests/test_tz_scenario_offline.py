"""End-to-end scenario zone threading (accuracy-audit fix batch F-1;
rewritten to the real scenario contract in TJ-031.2).

OFFLINE / PRIVATE-CI ONLY. Requires the sealed production runtime and the
private canonical data: execute_scenario() raises RuntimeUnavailable in a
public checkout. DO NOT add this file to .github/workflows/validate.yml;
it runs in offline acceptance (--suite all discovers every test module).

Real output contract (copied from scenario_engine.py, TJ-031.2 audit —
the F-1 version of this file read paths that do not exist and errored):

- bazi-profile: result["pillars"] / result["day_master"] (no "natal" wrap)
- yearly / romance / career / daily: result["natal"]["pillars"]
- weekly / monthly: result["natal"] carries the day master only (no
  pillars); the shared natal is proven through the day master plus each
  day's ganzhi and stem_ten_god, which are computed against that master
- life: result["profile"]["pillars"] plus the yearly / romance / career
  sections embedded verbatim; the handler itself raises on any natal or
  target-year disagreement, so a returned report whose four pillar sets
  are equal IS the four-source consistency proof
- compatibility: result["person_a"]["pillars"] / ["person_b"]["pillars"]

Expected values: day pillars cross-checked with the independent sxtwl
2.0.7 implementation (1990-05-15 = 庚辰, 2020-05-15 = 戊午,
2026-10-04 = 辛亥, 2026-10-05 = 壬子); hour pillars follow the standard
day-stem clock arithmetic; stem ten-gods are read off the standard
ten-god table against the sxtwl-verified London day master 庚
(辛 -> 劫财, 壬 -> 食神). Under the old Shanghai frame the London day
master would be 辛 and both ten-gods would differ, so these assertions
detect a lost zone.
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
            pillars_of(output["result"]["pillars"]), LONDON_PILLARS)
        self.assertEqual(output["result"]["day_master"]["stem"], "庚")

    def test_bazi_profile_london_evening_keeps_day(self):
        output = execute_scenario("bazi-profile", {
            "value": LONDON_EVENING, "zone": "Europe/London"})
        self.assertEqual(
            pillars_of(output["result"]["pillars"]),
            LONDON_EVENING_PILLARS)

    def test_bazi_profile_tokyo_noon_first_hour(self):
        output = execute_scenario("bazi-profile", {
            "value": TOKYO_NOON_FIRST_HOUR, "zone": "Asia/Tokyo"})
        self.assertEqual(
            pillars_of(output["result"]["pillars"]), TOKYO_PILLARS)

    def test_bazi_profile_shanghai_regression(self):
        output = execute_scenario("bazi-profile", {"value": SHANGHAI})
        self.assertEqual(
            pillars_of(output["result"]["pillars"]), SHANGHAI_PILLARS)

    def test_bazi_profile_foreign_offset_without_zone_rejected(self):
        # No zone means the documented Asia/Shanghai default; the London
        # offset contradicts tzdb under that default, so the scenario
        # must fail closed end-to-end instead of recomputing in Shanghai
        # time (the F-1 defect at scenario level).
        with self.assertRaises(ValueError) as ctx:
            execute_scenario("bazi-profile", {"value": LONDON})
        self.assertIn("contradicts", str(ctx.exception))

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

    def test_daily_shares_london_natal(self):
        output = execute_scenario("daily", {
            "birth_value": LONDON, "target_date": "2026-10-04",
            "birth_zone": "Europe/London"})
        self.assertEqual(
            pillars_of(output["result"]["natal"]["pillars"]), LONDON_PILLARS)
        # 2026-10-04 is 辛亥 (sxtwl); against the London day master 庚
        # its stem is 劫财. The Shanghai frame would give day master 辛
        # and 比肩 instead.
        self.assertEqual(output["result"]["target_day"]["ganzhi"], "辛亥")
        self.assertEqual(output["result"]["target_day"]["stem_ten_god"], "劫财")

    def test_weekly_shares_london_natal(self):
        output = execute_scenario("weekly", {
            "birth_value": LONDON, "anchor_date": "2026-10-05",
            "birth_zone": "Europe/London"})
        self.assertEqual(output["result"]["natal"]["day_master"]["stem"], "庚")
        week = output["result"]["week"]
        self.assertEqual(week["start_date"], "2026-10-05")
        self.assertEqual(week["end_date"], "2026-10-11")
        self.assertEqual(len(week["days"]), 7)
        # 2026-10-05 is 壬子 (sxtwl); against 庚 its stem is 食神
        # (against the Shanghai-frame master 辛 it would be 伤官).
        first = week["days"][0]
        self.assertEqual(first["date"], "2026-10-05")
        self.assertEqual(first["ganzhi"], "壬子")
        self.assertEqual(first["stem_ten_god"], "食神")

    def test_monthly_shares_london_natal(self):
        output = execute_scenario("monthly", {
            "birth_value": LONDON, "target_month": "2026-10",
            "birth_zone": "Europe/London"})
        self.assertEqual(output["result"]["natal"]["day_master"]["stem"], "庚")
        month = output["result"]["month"]
        self.assertEqual(month["day_count"], 31)
        entry = next(d for d in month["days"] if d["date"] == "2026-10-05")
        self.assertEqual(entry["ganzhi"], "壬子")
        self.assertEqual(entry["stem_ten_god"], "食神")

    def test_life_four_sources_identical_under_zone(self):
        output = execute_scenario("life", {
            "birth_value": LONDON, "target_year": 2026,
            "birth_zone": "Europe/London"})
        result = output["result"]
        # The handler raises on any cross-source natal or target-year
        # disagreement, so reaching this point already proves the four
        # computations agreed; assert the shared values explicitly.
        self.assertEqual(pillars_of(result["profile"]["pillars"]), LONDON_PILLARS)
        for section in ("yearly", "romance", "career"):
            self.assertEqual(
                pillars_of(result[section]["natal"]["pillars"]),
                LONDON_PILLARS, section)
            self.assertEqual(
                result[section]["target_year"]["ganzhi"], "丙午", section)
        self.assertEqual(result["target_year"], 2026)

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
        # Each side's spouse palace is its own day branch: the two zones
        # were applied independently (London 庚辰 -> 辰, Shanghai 戊午 -> 午).
        self.assertEqual(
            output["result"]["person_a"]["spouse_palace"]["day_branch"], "辰")
        self.assertEqual(
            output["result"]["person_b"]["spouse_palace"]["day_branch"], "午")

    def test_question_accepts_zone_end_to_end(self):
        output = execute_scenario("question", {
            "value": LONDON, "yao_values": [9, 7, 7, 7, 7, 7],
            "zone": "Europe/London"})
        self.assertEqual(output["result"]["changing_lines"], [1])
        self.assertEqual(output["result"]["changed"]["number"], 44)


if __name__ == "__main__":
    unittest.main()
