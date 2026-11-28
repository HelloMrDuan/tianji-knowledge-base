"""TJ-0422 phase 2 backend: lift strength/xiyong/pattern into career+life;
career annual branch structure from the reviewed _yearly computation.

Runs only in the assembled backend (real knowledge bundle + production
runtime), like the other scenario tests -- every envelope below comes
from the real backend, never from a stub. The three lifted fields are
the exact validated objects the bazi-profile gate builds for the same
birth instant; this file proves the lift (equality with the profile
objects), the projection allowlist (career/life keep them, every other
scenario is stripped), the exact-shape validators, and the public
boundary scan over the whole projected envelopes -- the three gates
the new public fields must pass. It also proves the hard boundaries:
no 2-8 dayun periods, no starting age / single交运 date / end
interval, no year-to-dayun lookup, no dayun x natal/year efficacy
judgment, no U3 definite direction, and the role is never defaulted
or persisted outside the dayun presentation itself.
"""

import copy
import json
import unittest

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_dayun_public import is_valid_public_dayun_presentation
from tianji_kb.bazi_pattern_public import (
    is_valid_public_pattern_presentation,
)
from tianji_kb.bazi_strength_public import (
    is_valid_public_strength_presentation,
)
from tianji_kb.bazi_xiyong_public import is_valid_public_presentation
from tianji_kb.public_boundary import find_public_boundary_violations
from tianji_kb.public_projection import project_execution
from tianji_kb import scenario_engine

BIRTH = "2000-01-07T12:00:00+08:00"
TARGET_YEAR = 2026
PRESENTATION_KEYS = (
    "strength_presentation",
    "xiyong_presentation",
    "pattern_presentation",
)
BRANCH_RULE_IDS = [
    "bazi.phase2.branch_six_harmonies",
    "bazi.phase2.branch_six_harms",
    "bazi.phase2.branch_six_clashes",
]
BANNED_AGE_KEYS = ("start_age", "end_age", "start_date", "end_date")
BANNED_JUDGMENT_KEYS = (
    "natal_interaction",
    "luck_assessment",
    "annual_luck_prediction",
)

_CACHE = {}


def _envelope(scenario_id, inputs):
    """Shared real-backend envelopes, computed once per input shape."""
    key = (scenario_id, tuple(sorted(inputs.items())))
    if key not in _CACHE:
        _CACHE[key] = scenario_engine.execute_scenario(
            scenario_id, dict(inputs))
    return _CACHE[key]


def _profile():
    return _envelope("bazi-profile", {
        "value": BIRTH,
        "strength_variant": "ditiansui-root-visibility-v1",
    })


def _career(role=None):
    inputs = {"birth_value": BIRTH, "target_year": TARGET_YEAR}
    if role is not None:
        inputs["traditional_role"] = role
    return _envelope("career", inputs)


def _life(role=None):
    inputs = {"birth_value": BIRTH, "target_year": TARGET_YEAR}
    if role is not None:
        inputs["traditional_role"] = role
    return _envelope("life", inputs)


def _yearly():
    return _envelope("yearly", {
        "birth_value": BIRTH, "target_year": TARGET_YEAR,
    })


def _assert_valid_presentations(test, result):
    for key in PRESENTATION_KEYS:
        test.assertIn(key, result)
    test.assertTrue(is_valid_public_strength_presentation(
        result["strength_presentation"]))
    test.assertTrue(is_valid_public_presentation(
        result["xiyong_presentation"]))
    test.assertTrue(is_valid_public_pattern_presentation(
        result["pattern_presentation"]))


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


class LiftedPresentationsTests(unittest.TestCase):
    def test_life_carries_the_three_presentations_and_they_validate(self):
        _assert_valid_presentations(self, _life()["result"])
        _assert_valid_presentations(self, _life("male")["result"])

    def test_career_carries_the_three_presentations_and_they_validate(self):
        _assert_valid_presentations(self, _career()["result"])
        _assert_valid_presentations(self, _career("male")["result"])

    def test_lifted_presentations_equal_the_profile_objects(self):
        profile = _profile()["result"]
        for envelope in (_life(), _life("male"),
                         _career(), _career("male")):
            for key in PRESENTATION_KEYS:
                self.assertEqual(
                    envelope["result"][key], profile[key], key)

    def test_presentations_are_role_independent(self):
        for scenario in (_career, _life):
            plain = scenario()["result"]
            roled = scenario("male")["result"]
            for key in PRESENTATION_KEYS:
                self.assertEqual(plain[key], roled[key], key)

    def test_life_nested_career_presentations_equal_top_level(self):
        life = _life("male")["result"]
        for key in PRESENTATION_KEYS:
            self.assertEqual(life["career"][key], life[key], key)
        self.assertEqual(
            life["career"]["dayun_presentation"],
            life["dayun_presentation"])

    def test_life_old_strength_context_unchanged(self):
        life = _life()["result"]
        context = life["profile"]["strength_context"]
        self.assertEqual(context["classification"], "unresolved")
        self.assertEqual(
            context["month_branch"],
            life["profile"]["pillars"][1]["branch"]["value"])
        self.assertTrue(context["evidence_ids"])
        self.assertTrue(set(context["evidence_ids"]) <= set(_life()["evidence"]))
        # The lift adds keys; it never rewrites the factor display.
        self.assertNotIn("strength_presentation", life["profile"])
        self.assertNotIn("xiyong_presentation", life["profile"])
        self.assertNotIn("pattern_presentation", life["profile"])

    def test_presentations_present_without_role_but_dayun_absent(self):
        for envelope in (_career(), _life()):
            for key in PRESENTATION_KEYS:
                self.assertIn(key, envelope["result"])
            self.assertNotIn("dayun_presentation", envelope["result"])

    def test_xiyong_unified_verdict_is_none_and_ai_off(self):
        for envelope in (_career(), _life(), _profile()):
            xiyong = envelope["result"]["xiyong_presentation"]
            self.assertIsNone(xiyong["unified_verdict"])
            self.assertIs(xiyong["public_enabled"], True)
            self.assertIs(xiyong["ai_enabled"], False)
            self.assertEqual(
                set(xiyong["blocks"]), {"tiaohou", "bingyao"})

    def test_role_never_persisted_outside_the_dayun_presentation(self):
        life = _life("male")["result"]
        # The role lives only inside dayun_presentation.role, which
        # the dayun presentation itself carries by design (once at
        # the top level, once in the nested career copy); no other
        # part of the report (profile section included) stores it.
        # TJ-031.19 (E0427, Q3=A): the life presentation carries it
        # in exactly two more documented places -- its unified birth
        # block (which states the caliber the timeline was computed
        # under) and the embedded bazi theme's dayun section, whose
        # "public" field is the validated gate object itself. The
        # exact multiset is the pin: the role appears exactly four
        # times, all inside a dayun presentation or the life
        # presentation's unified block, nowhere else.
        paths = []

        def _collect(value, path):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "traditional_role":
                        paths.append(path + "/" + key)
                    _collect(item, path + "/" + key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    _collect(item, f"{path}[{index}]")

        _collect(life, "/result")
        # The order is dict-traversal order and carries no
        # meaning (the nested career copy precedes the top level
        # in the sealed run); the exact multiset is the pin: the
        # role appears exactly four times, all inside a
        # dayun_presentation or the life presentation's unified
        # block, nowhere else.
        self.assertEqual(sorted(paths), sorted([
            "/result/dayun_presentation/role/traditional_role",
            "/result/career/dayun_presentation/role/traditional_role",
            "/result/life_presentation/unified/traditional_role",
            "/result/life_presentation/themes/bazi/sections[5]/public/role/traditional_role",
        ]))


class CareerAnnualBranchTests(unittest.TestCase):
    def test_annual_reading_carries_branch_structure(self):
        reading = _career()["result"]["annual_reading"]
        branch = reading["annual_branch_interactions"]
        self.assertEqual(branch["flow_branch"], "午")
        self.assertEqual(branch["evaluated_pairs"], 4)
        self.assertEqual(branch["rule_ids"], BRANCH_RULE_IDS)
        self.assertIs(branch["interpretation_allowed"], False)

    def test_branch_structure_matches_yearly_exactly(self):
        career_branch = _career()["result"]["annual_reading"][
            "annual_branch_interactions"]
        yearly_branch = _yearly()["result"]["annual_branch_interactions"]
        self.assertEqual(career_branch, yearly_branch)

    def test_branch_equality_assertion_can_fail(self):
        # Negative control for the equality above: corrupting one
        # hit must break it, so the passing equality is evidence.
        corrupted = copy.deepcopy(
            _career()["result"]["annual_reading"][
                "annual_branch_interactions"])
        yearly_branch = _yearly()["result"]["annual_branch_interactions"]
        corrupted["hits"] = []
        corrupted["counts"] = {"six_harmony": 0, "harm": 0, "clash": 0}
        with self.assertRaises(AssertionError):
            self.assertEqual(corrupted, yearly_branch)

    def test_branch_evidence_resolves_in_the_career_envelope(self):
        envelope = _career()
        reading = envelope["result"]["annual_reading"]
        branch = reading["annual_branch_interactions"]
        self.assertTrue(branch["evidence_ids"])
        self.assertTrue(
            set(branch["evidence_ids"]) <= set(envelope["evidence"]))
        self.assertTrue(
            set(reading["evidence_ids"]) <= set(envelope["evidence"]))

    def test_branch_rule_match_and_trace_step_present(self):
        envelope = _career()
        rule_ids = [row["rule_id"] for row in envelope["rule_matches"]]
        self.assertIn("bazi.scenario.career_wealth_structure", rule_ids)
        self.assertIn("bazi.scenario.annual_branch_relations", rule_ids)
        branch_rule = next(
            row for row in envelope["rule_matches"]
            if row["rule_id"] == "bazi.scenario.annual_branch_relations")
        self.assertEqual(branch_rule["facts"]["flow_branch"], "午")
        self.assertEqual(branch_rule["facts"]["evaluated_pairs"], 4)
        self.assertEqual(
            branch_rule["evidence_ids"],
            envelope["result"]["annual_reading"][
                "annual_branch_interactions"]["evidence_ids"])
        steps = [step["step"] for step in envelope["trace"]]
        self.assertIn("reviewed_flow_year_natal_branch_pairs", steps)

    def test_no_joint_efficacy_judgment_in_annual_reading(self):
        reading = _career()["result"]["annual_reading"]
        for key in BANNED_JUDGMENT_KEYS:
            self.assertNotIn(key, reading)
        # The stem reading and the branch facts stay side by side;
        # neither the reading nor the branch block claims an effect.
        self.assertIn("尚未判定月令旺衰、喜用、格局、大运或流年实际效力",
                      reading["boundary"])


class ProjectionScopeTests(unittest.TestCase):
    def test_projection_keeps_presentations_for_profile_career_life(self):
        for envelope in (_profile(), _career(), _career("male"),
                         _life(), _life("male")):
            projected = project_execution(copy.deepcopy(envelope))
            _assert_valid_presentations(self, projected["result"])

    def test_projection_strips_presentations_for_other_scenarios(self):
        base = copy.deepcopy(_career("male"))
        for scenario_id in ("yearly", "romance", "daily", "weekly",
                            "monthly", "question", "compatibility"):
            forged = copy.deepcopy(base)
            forged["scenario_id"] = scenario_id
            projected = project_execution(forged)
            for key in PRESENTATION_KEYS:
                self.assertNotIn(key, projected["result"], scenario_id)

    def test_projection_strips_forged_presentations(self):
        # Each gate is exact-shape: one mutated field strips the key.
        mutations = (
            ("xiyong_presentation", "unified_verdict", "x"),
            ("strength_presentation", "status", "bogus"),
            ("pattern_presentation", "status", "bogus"),
        )
        for key, field, bad_value in mutations:
            forged = copy.deepcopy(_career("male"))
            forged["result"][key][field] = bad_value
            projected = project_execution(forged)
            self.assertNotIn(key, projected["result"], (key, field))

    def test_projection_boundary_scan_clean(self):
        for envelope in (_profile(), _career("male"), _life("male")):
            projected = project_execution(copy.deepcopy(envelope))
            self.assertEqual(
                find_public_boundary_violations(projected), [])

    def test_api_returns_presentations(self):
        client = TestClient(create_app())
        for scenario_id in ("career", "life"):
            for inputs in (
                    {"birth_value": BIRTH, "target_year": TARGET_YEAR},
                    {"birth_value": BIRTH, "target_year": TARGET_YEAR,
                     "traditional_role": "female"}):
                response = client.post("/api/v1/scenarios/public", json={
                    "scenario_id": scenario_id, "input": inputs})
                self.assertEqual(response.status_code, 200, scenario_id)
                _assert_valid_presentations(
                    self, response.json()["result"])
                if "traditional_role" in inputs:
                    self.assertTrue(
                        is_valid_public_dayun_presentation(
                            response.json()["result"][
                                "dayun_presentation"]))
                else:
                    self.assertNotIn(
                        "dayun_presentation", response.json()["result"])


class HardBoundaryTests(unittest.TestCase):
    def test_no_starting_age_or_interval_fields(self):
        for envelope in (_career("male"), _life("male")):
            keys = set(_all_keys(envelope["result"]))
            for banned in (*BANNED_AGE_KEYS, "end_interval"):
                self.assertNotIn(banned, keys)
            blob = json.dumps(envelope["result"], ensure_ascii=False)
            for banned in BANNED_AGE_KEYS:
                self.assertNotIn(banned, blob)

    def test_dayun_periods_2_to_8_still_withheld(self):
        for envelope in (_career("male"), _life("male")):
            presentation = envelope["result"]["dayun_presentation"]
            self.assertTrue(
                is_valid_public_dayun_presentation(presentation))
            entries = presentation["methods"]["sanming"]["entries"]
            self.assertEqual(len(entries), 8)
            self.assertEqual(entries[0]["state"], "interval")
            self.assertTrue(all(
                entry["state"] == "unresolved" for entry in entries[1:]))
            self.assertTrue(all(
                entry["start_interval"] is None for entry in entries[1:]))

    def test_no_luck_or_interaction_judgments_anywhere(self):
        for envelope in (_career("male"), _life("male")):
            keys = set(_all_keys(envelope["result"]))
            for banned in BANNED_JUDGMENT_KEYS:
                self.assertNotIn(banned, keys)

    def test_life_dayun_timeline_flags_are_three_and_role_conditional(self):
        # TJ-031.19 (E0427, Q3=A): the full 8-period timeline is
        # approved for the life overview exactly when a traditional
        # role is given, so all three flags are False without a role
        # and True with one. The count stays exactly three.
        flags = []

        def _collect(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "dayun_timeline_approved":
                        flags.append(item)
                    _collect(item)
            elif isinstance(value, list):
                for item in value:
                    _collect(item)

        for role, expected_value in ((None, False), ("male", True)):
            flags.clear()
            _collect(_life(role)["result"])
            self.assertEqual(len(flags), 3)
            self.assertTrue(all(flag is expected_value for flag in flags))

    def test_invalid_role_rejected_for_career_and_life(self):
        for scenario_id in ("career", "life"):
            with self.assertRaises(ValueError):
                scenario_engine.execute_scenario(scenario_id, {
                    "birth_value": BIRTH, "target_year": TARGET_YEAR,
                    "traditional_role": "other"})


if __name__ == "__main__":
    unittest.main()
