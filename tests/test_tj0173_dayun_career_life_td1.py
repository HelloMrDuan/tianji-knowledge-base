"""T-D1 (E0409): first-period dayun wired into career and life scenarios.

The career and life scenarios accept the optional traditional_role
(bazi-profile precedent, TJ-017.3 phase 2) and return the public
dayun_presentation -- FIRST PERIOD ONLY -- when a role is given.
Without a role there is no dayun anywhere in either result. Periods
2-8 stay not_provided and no starting age is ever computed or shown
(precision adjudication A, 2026-11-17). The full dayun timeline
stays unapproved: both dayun_timeline_approved flags remain False.
The public projection releases the dayun presentation for career and
life (same validated shape as bazi-profile); every other scenario
still has it stripped.

Runs in the offline acceptance (assembled tree with the sealed
runtime), not in public CI -- like the other real-engine scenario
tests. The presentation-scope pins in
test_tj0173_dayun_public_presentation.py run in public CI.
"""
import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_dayun_public import (
    is_valid_public_dayun_presentation,
)
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]
BIRTH = "2000-01-07T12:00:00+08:00"
# E0362 verbatim copy for the no-role life dayun exit.
NO_ROLE_DAYUN = (
    "大运方向与起运换算已有完成审核的注册规则（方向据三命分段；"
    "起运换算有三命、神峰两套口径分别注册，只给出交运时刻区间，"
    "不折算单点岁数或日期），但尚未批准接入本总览；"
    "岁运效力仍无完成审核的生产规则，本总览不推算或伪造大运时间线。")


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


def _flag_values(value, key):
    if isinstance(value, dict):
        for name, item in value.items():
            if name == key:
                yield item
            yield from _flag_values(item, key)
    elif isinstance(value, list):
        for item in value:
            yield from _flag_values(item, key)


class CareerDayunTests(unittest.TestCase):
    def test_role_returns_first_period_only(self):
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        presentation = envelope["result"]["dayun_presentation"]
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))
        self.assertEqual(
            set(presentation),
            {"variant", "status", "role", "methods",
             "method_options", "evidence", "scope", "limitations"})
        self.assertEqual(
            presentation["role"]["traditional_role"], "male")
        for method in ("sanming", "shenfeng"):
            entries = presentation["methods"][method]["entries"]
            self.assertEqual(len(entries), 8)
            self.assertEqual(entries[0]["period_index"], 1)
            self.assertEqual(entries[0]["state"], "interval")
            self.assertIsNotNone(entries[0]["start_interval"])
            for entry in entries[1:]:
                self.assertEqual(entry["state"], "not_provided")
                self.assertIsNone(entry["start_interval"])

    def test_no_role_means_no_dayun(self):
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026})
        self.assertNotIn("dayun_presentation", envelope["result"])
        self.assertIn("尚未纳入格局、喜用神、身强身弱、大运、",
                      envelope["limitations"][2])

    def test_role_limitation_names_periods_2_to_8(self):
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "female"})
        self.assertIn("大运第 2–8 运", envelope["limitations"][2])

    def test_no_starting_age_anywhere(self):
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        blob = json.dumps(envelope["result"], ensure_ascii=False)
        for banned in ("start_age", "end_age", "start_date", "end_date"):
            self.assertNotIn(banned, blob)

    def test_invalid_role_rejected(self):
        with self.assertRaises(ValueError):
            execute_scenario("career", {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "other"})

    def test_api_returns_dayun_through_projection(self):
        client = TestClient(create_app())
        response = client.post("/api/v1/scenarios/public", json={
            "scenario_id": "career",
            "input": {"birth_value": BIRTH, "target_year": 2026,
                      "traditional_role": "male"},
        })
        self.assertEqual(response.status_code, 200)
        presentation = response.json()["result"]["dayun_presentation"]
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))
        entries = presentation["methods"]["sanming"]["entries"]
        self.assertEqual(entries[0]["state"], "interval")
        self.assertTrue(all(
            e["state"] == "not_provided" for e in entries[1:]))

    def test_api_without_role_has_no_dayun(self):
        client = TestClient(create_app())
        response = client.post("/api/v1/scenarios/public", json={
            "scenario_id": "career",
            "input": {"birth_value": BIRTH, "target_year": 2026},
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "dayun_presentation", response.json()["result"])


class LifeDayunTests(unittest.TestCase):
    def test_role_returns_first_period_only_at_top_level(self):
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "female"})
        presentation = envelope["result"]["dayun_presentation"]
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))
        self.assertEqual(
            presentation["role"]["traditional_role"], "female")
        for method in ("sanming", "shenfeng"):
            entries = presentation["methods"][method]["entries"]
            self.assertEqual(len(entries), 8)
            self.assertEqual(entries[0]["state"], "interval")
            self.assertTrue(all(
                e["state"] == "not_provided" for e in entries[1:]))
        # The career section inside the report carries the same
        # presentation (same request, same role).
        self.assertEqual(
            envelope["result"]["career"]["dayun_presentation"],
            presentation)

    def test_role_dayun_exit_names_first_period(self):
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        dayun_text = envelope["result"]["integrated_reading"]["dayun"]
        self.assertIn("大运首运", dayun_text)
        self.assertIn("第 2–8 运未提供", dayun_text)
        self.assertIn("不折算起运岁数或日期", dayun_text)

    def test_no_role_keeps_e0362_wording_verbatim(self):
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026})
        self.assertNotIn("dayun_presentation", envelope["result"])
        self.assertEqual(
            envelope["result"]["integrated_reading"]["dayun"],
            NO_ROLE_DAYUN)

    def test_full_timeline_flags_stay_false(self):
        for role in (None, "male"):
            inputs = {"birth_value": BIRTH, "target_year": 2026}
            if role is not None:
                inputs["traditional_role"] = role
            envelope = execute_scenario("life", inputs)
            flags = list(_flag_values(
                envelope, "dayun_timeline_approved"))
            self.assertEqual(len(flags), 2)
            self.assertTrue(all(flag is False for flag in flags))

    def test_no_starting_age_anywhere(self):
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        blob = json.dumps(envelope["result"], ensure_ascii=False)
        for banned in ("start_age", "end_age", "start_date", "end_date"):
            self.assertNotIn(banned, blob)

    def test_invalid_role_rejected(self):
        with self.assertRaises(ValueError):
            execute_scenario("life", {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "other"})

    def test_api_returns_dayun_through_projection(self):
        client = TestClient(create_app())
        response = client.post("/api/v1/scenarios/public", json={
            "scenario_id": "life",
            "input": {"birth_value": BIRTH, "target_year": 2026,
                      "traditional_role": "female"},
        })
        self.assertEqual(response.status_code, 200)
        presentation = response.json()["result"]["dayun_presentation"]
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))


class YearlyStillRejectsRoleTests(unittest.TestCase):
    def test_yearly_rejects_traditional_role(self):
        with self.assertRaises(ValueError):
            execute_scenario("yearly", {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "male"})


class ProjectionScopeTests(unittest.TestCase):
    def test_projection_keeps_dayun_for_career_and_life(self):
        career = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        life = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        for envelope in (career, life):
            projected = project_execution(envelope)
            self.assertIn("dayun_presentation", projected["result"])
            self.assertTrue(is_valid_public_dayun_presentation(
                projected["result"]["dayun_presentation"]))

    def test_projection_strips_dayun_for_yearly(self):
        # Yearly rejects the role at the scenario layer, so a forged
        # yearly envelope carrying a presentation must still be
        # stripped by the projection.
        career = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        forged = json.loads(json.dumps(career, ensure_ascii=False))
        forged["scenario_id"] = "yearly"
        projected = project_execution(forged)
        self.assertNotIn("dayun_presentation", projected["result"])


class FrontendWiringTests(unittest.TestCase):
    """Guarded source pins for the page wiring (E0359 lesson: the
    assembled acceptance tree has no web/ -- skip when absent)."""

    def test_pages_consume_dayun_presentation(self):
        for page_name in ("CareerWealthStructurePage.tsx",
                          "LifeOverviewPage.tsx"):
            page_path = (ROOT / "web" / "visual-prototype" / "src"
                         / "public" / page_name)
            if not page_path.exists():
                self.skipTest("web tree not present in this checkout")
            page = page_path.read_text(encoding="utf-8")
            self.assertIn("dayun_presentation", page, page_name)
            self.assertIn("传统大运口径（可选）", page, page_name)
            # The role is sent only when explicitly selected.
            self.assertIn("traditional_role", page, page_name)
            # First period only; periods 2-8 and starting age are
            # never shown.
            self.assertIn("第 2–8 运未提供", page, page_name)


if __name__ == "__main__":
    unittest.main()
