"""T-D1 (E0409): first-period dayun wired into career and life scenarios.

The career and life scenarios accept the optional traditional_role
(bazi-profile precedent, TJ-017.3 phase 2) and return the public
dayun_presentation -- FIRST PERIOD ONLY on the legacy field -- when a
role is given. Without a role there is no dayun anywhere in either
result. The scene-scoped trim (E0410) clears the sanming periods 2-8
intervals (state ``unresolved`` with a status naming the scene
scope) while shenfeng periods 2-8 stay ``not_provided``; no starting
age is ever computed or shown (precision adjudication A, 2026-11-17).
TJ-031.19 (E0427, Q3=A, user adjudication 2026-11-28): the full
8-period timeline IS now approved for career and life -- presented
via the career_presentation / life_presentation, never by widening
the legacy field -- and the three dayun_timeline_approved flags are
True exactly when a role was given. The public projection releases
the dayun presentation for career and life (same validated shape as
bazi-profile); every other scenario still has it stripped.

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
# TJ-031.19 (E0427, Q3=A): no-role life dayun exit. The E0362
# "尚未批准接入本总览" wording is superseded: the timeline IS now
# approved for this overview, role-gated, so the no-role text states
# the selection state instead of a blanket non-approval.
NO_ROLE_DAYUN = (
    "大运方向与起运换算已有完成审核的注册规则（方向据三命分段；"
    "起运换算有三命、神峰两套口径分别注册，只给出交运时刻区间，"
    "不折算单点岁数或日期）；未选择传统口径，本总览不呈现大运，"
    "选定口径后呈现完整 8 运时间线；岁运效力仍无完成审核的"
    "生产规则，本总览不推算或伪造大运时间线。")


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


def _flag_paths(value, key, path=""):
    if isinstance(value, dict):
        for name, item in value.items():
            if name == key:
                yield path + "/" + name
            yield from _flag_paths(item, key, path + "/" + name)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _flag_paths(item, key, path + f"[{index}]")


# Scene-scoped trim (E0410): sanming periods 2-8 are unresolved
# (intervals cleared, status names the scene scope); shenfeng
# periods 2-8 stay not_provided. The shared validator forbids
# sanming + not_provided (E0375), so not_provided is not an
# available state for sanming entries at all.
TRIMMED_STATE = {"sanming": "unresolved", "shenfeng": "not_provided"}


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
                self.assertEqual(entry["state"], TRIMMED_STATE[method])
                self.assertIsNone(entry["start_interval"])

    def test_no_role_means_no_dayun(self):
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026})
        self.assertNotIn("dayun_presentation", envelope["result"])
        self.assertIn("尚未纳入格局、喜用神、身强身弱、大运、",
                      envelope["limitations"][2])

    def test_role_limitation_drops_periods_2_to_8(self):
        # TJ-031.19 (E0427, Q3=A): with a role the full 8-period
        # timeline is presented via the career presentation, so
        # periods 2-8 no longer belong in the unincluded list.
        envelope = execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "female"})
        self.assertNotIn("大运第 2–8 运", envelope["limitations"][2])
        section = next(
            item for item in
            envelope["result"]["career_presentation"]["sections"]
            if item["id"] == "dayun_timeline")
        self.assertEqual(section["status"], "presented")
        entries = section["content"]["methods"]["sanming"]["entries"]
        self.assertEqual(len(entries), 8)
        self.assertEqual(entries[1]["state"], "interval")
        self.assertIsNotNone(entries[1]["start_interval"])

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
            e["state"] == "unresolved" for e in entries[1:]))
        self.assertTrue(all(
            e["start_interval"] is None for e in entries[1:]))

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
                e["state"] == TRIMMED_STATE[method] for e in entries[1:]))
            self.assertTrue(all(
                e["start_interval"] is None for e in entries[1:]))
        # The career section inside the report carries the same
        # presentation (same request, same role).
        self.assertEqual(
            envelope["result"]["career"]["dayun_presentation"],
            presentation)

    def test_role_dayun_exit_names_full_timeline(self):
        # TJ-031.19 (E0427, Q3=A): with a role the life dayun exit
        # names the full 8-period timeline (presented via the life
        # presentation); the first-period-only phrasing is gone.
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        dayun_text = envelope["result"]["integrated_reading"]["dayun"]
        self.assertIn("完整 8 运大运时间线", dayun_text)
        self.assertNotIn("大运首运", dayun_text)
        self.assertNotIn("第 2–8 运尚未在本场景开放", dayun_text)
        self.assertIn("不折算起运岁数或日期", dayun_text)
        self.assertEqual(
            envelope["result"]["life_presentation"]["dayun"]["status"],
            "presented")
        self.assertEqual(
            len(envelope["result"]["life_presentation"]["stages"]), 8)

    def test_no_role_keeps_q3a_no_role_wording(self):
        # TJ-031.19 (E0427, Q3=A): the E0362 wording is superseded
        # (see the NO_ROLE_DAYUN note above); the no-role exit now
        # states the selection state, verbatim.
        envelope = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026})
        self.assertNotIn("dayun_presentation", envelope["result"])
        self.assertEqual(
            envelope["result"]["integrated_reading"]["dayun"],
            NO_ROLE_DAYUN)
        self.assertEqual(
            envelope["result"]["life_presentation"]["dayun"]["status"],
            "not_presented")

    def test_full_timeline_flags_are_role_conditional(self):
        # TJ-031.19 (E0427, Q3=A): the three flags are True exactly
        # when a role was given, False without one.
        for role, expected in ((None, False), ("male", True)):
            inputs = {"birth_value": BIRTH, "target_year": 2026}
            if role is not None:
                inputs["traditional_role"] = role
            envelope = execute_scenario("life", inputs)
            flags = list(_flag_values(
                envelope, "dayun_timeline_approved"))
            # Three flags, not two: integrated_reading, the dayun
            # condition marker basis, and integration_provenance.
            # The provenance flag predates T-D1 and must stay.
            self.assertEqual(len(flags), 3)
            self.assertTrue(all(flag is expected for flag in flags))

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
            # TJ-031.19 (E0427, Q3=A): the first-period block says
            # so itself and points at the full 8-period timeline;
            # the "第 2–8 运尚未在本场景开放" claim is gone.
            self.assertIn("本块只呈现首运方向与交运区间", page, page_name)
            self.assertIn("完整 8 运时间线见", page, page_name)
            self.assertNotIn("第 2–8 运尚未在本场景开放", page, page_name)


class SceneScopedTrimSafetyTests(unittest.TestCase):
    """E0410 safety regressions for the scene-scoped trim.

    The trim lives only at the career/life output boundary: the
    shared builder still computes the full sanming intervals, the
    bazi-profile presentation is unchanged, and only the two scenes
    withhold periods 2-8 -- as ``unresolved`` with the real
    intervals cleared, never as a claim that the underlying data
    was not computed.
    """

    def _full_builder_intervals(self):
        # bazi-profile returns the shared gate output untrimmed:
        # the real sanming intervals for periods 2-8.
        envelope = execute_scenario("bazi-profile", {
            "value": BIRTH, "traditional_role": "male"})
        presentation = envelope["result"]["dayun_presentation"]
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))
        intervals = []
        for entry in presentation["methods"]["sanming"]["entries"][1:]:
            self.assertEqual(entry["state"], "interval")
            self.assertIsNotNone(entry["start_interval"])
            intervals.append(entry["start_interval"]["earliest"])
            intervals.append(entry["start_interval"]["latest"])
        return presentation, intervals

    def test_sanming_periods_2_to_8_leak_no_real_intervals(self):
        # (a) No real interval -- neither the interval objects nor
        # any of their datetimes -- may appear anywhere in the
        # trimmed career/life presentations.
        _, real_intervals = self._full_builder_intervals()
        self.assertTrue(real_intervals)
        for scenario_id in ("career", "life"):
            envelope = execute_scenario(scenario_id, {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "male"})
            trimmed = envelope["result"]["dayun_presentation"]
            self.assertTrue(
                is_valid_public_dayun_presentation(trimmed))
            for entry in trimmed["methods"]["sanming"]["entries"][1:]:
                self.assertEqual(entry["state"], "unresolved")
                self.assertIsNone(entry["start_interval"])
                self.assertIn(
                    "not opened in the career and life scenes",
                    entry["start_interval_status"])
                self.assertIn(
                    "shared builder computed",
                    entry["start_interval_status"])
            blob = json.dumps(trimmed, ensure_ascii=False)
            for value in real_intervals:
                self.assertNotIn(value, blob, scenario_id)
            # The nested career section inside life carries the same
            # trimmed object, not a second copy with full intervals.
            if scenario_id == "life":
                nested = envelope["result"]["career"]["dayun_presentation"]
                self.assertEqual(nested, trimmed)

    def test_shared_builder_result_unchanged(self):
        # (b) The original shared builder result is unchanged: the
        # same request still yields sanming intervals for all 8
        # periods through bazi-profile.
        presentation, _ = self._full_builder_intervals()
        entries = presentation["methods"]["sanming"]["entries"]
        self.assertEqual(len(entries), 8)
        self.assertTrue(all(
            e["state"] == "interval" for e in entries))

    def test_bazi_profile_full_presentation_unchanged(self):
        # (c) bazi-profile keeps its original full presentation:
        # sanming intervals for periods 2-8, shenfeng first period
        # only, and the presentation still validates.
        presentation, _ = self._full_builder_intervals()
        shenfeng = presentation["methods"]["shenfeng"]["entries"]
        self.assertEqual(shenfeng[0]["state"], "interval")
        self.assertTrue(all(
            e["state"] == "not_provided" for e in shenfeng[1:]))
        self.assertEqual(
            presentation["role"]["traditional_role"], "male")

    def test_projected_trimmed_dayun_validates(self):
        # (d) The career/life public projection passes real
        # public-structure validation on the TRIMMED object.
        for scenario_id in ("career", "life"):
            envelope = execute_scenario(scenario_id, {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "female"})
            projected = project_execution(envelope)
            presentation = projected["result"]["dayun_presentation"]
            self.assertTrue(
                is_valid_public_dayun_presentation(presentation))
            sanming = presentation["methods"]["sanming"]["entries"]
            self.assertTrue(all(
                e["state"] == "unresolved" for e in sanming[1:]))

    def test_no_role_means_no_dayun_at_api_level(self):
        # (e) Without a role the whole dayun block is absent from
        # both scenes, including at the public API level.
        client = TestClient(create_app())
        for scenario_id in ("career", "life"):
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": scenario_id,
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(
                "dayun_presentation", response.json()["result"])

    def test_all_three_dayun_timeline_flags_are_role_conditional(self):
        # (f) Exactly three dayun_timeline_approved flags, all
        # False without a role and all True with one (TJ-031.19,
        # E0427, Q3=A) -- integrated_reading, the dayun condition
        # marker basis, and integration_provenance (which must stay).
        expected = {
            "/result/integrated_reading/dayun_timeline_approved",
            "/result/condition_markers[5]/basis/dayun_timeline_approved",
            "/result/integration_provenance/dayun_timeline_approved",
        }
        for role, expected_value in ((None, False), ("male", True)):
            inputs = {"birth_value": BIRTH, "target_year": 2026}
            if role is not None:
                inputs["traditional_role"] = role
            envelope = execute_scenario("life", inputs)
            paths = set(_flag_paths(envelope, "dayun_timeline_approved"))
            self.assertEqual(paths, expected)
            self.assertTrue(all(
                flag is expected_value
                for flag in _flag_values(
                    envelope, "dayun_timeline_approved")))

    def test_no_starting_age_or_fortune_judgment(self):
        # (g) No starting age is produced anywhere, and the trimmed
        # presentation still carries its no-age and
        # no-fortune-judgment limitations.
        for scenario_id in ("career", "life"):
            envelope = execute_scenario(scenario_id, {
                "birth_value": BIRTH, "target_year": 2026,
                "traditional_role": "male"})
            keys = set(_all_keys(envelope["result"]))
            for banned in ("start_age", "end_age", "start_date",
                           "end_date"):
                self.assertNotIn(banned, keys, scenario_id)
            presentation = envelope["result"]["dayun_presentation"]
            self.assertIn(
                "不呈现任何年龄数值：古典起运为实历时长，年龄折算无原典口径。",
                presentation["limitations"])
            self.assertIn(
                "本呈现不是吉凶判断，不预测任何现实事件。",
                presentation["limitations"])
        life = execute_scenario("life", {
            "birth_value": BIRTH, "target_year": 2026,
            "traditional_role": "male"})
        self.assertIn(
            "不折算起运岁数",
            life["result"]["integrated_reading"]["dayun"])


if __name__ == "__main__":
    unittest.main()
