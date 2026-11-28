"""TJ-031.19 / E0427 central integration: the five plain-language
presentations wired into their scenario envelopes.

This file proves the central wiring (scenario_engine.py + the
public-projection allowlist), not the builders themselves -- each
builder's own shape, boundary and fail-closed tests live in its
Lane test file (test_tj0427_*_presentation.py).

* Each scenario attaches its presentation, built from that request's
  own execution records: bazi-profile -> profile_presentation,
  career -> career_presentation, romance -> romance_presentation,
  compatibility -> compatibility_presentation, life ->
  life_presentation. Every attached object passes its closed-shape
  validator.
* Q3=A (user adjudication 2026-11-28): with a role the full
  8-period dayun timeline is presented via the career / life /
  bazi-profile presentations (period 2 carries a real interval
  there); the legacy dayun_presentation field stays
  first-period-trimmed by contract (T-D1 pins in
  test_tj0173_dayun_career_life_td1.py). Compatibility stays
  first-period-only (Q3=A does not cover it).
* The public projection releases each presentation only on its own
  scenario; a forged copy on any other scenario is stripped.
* No starting age / single date is produced anywhere in the five
  results, and the five projected envelopes pass the public
  boundary scan.

Live tests: real envelopes through the real backend. They skip in
the public checkout (no sealed data/), like the other real-engine
scenario tests, and run in the offline acceptance.
"""
import copy
import json
import unittest

from tianji_kb.bazi_profile_presentation import (
    is_valid_bazi_profile_presentation,
)
from tianji_kb.career_presentation import is_valid_career_presentation
from tianji_kb.compatibility_presentation import (
    is_valid_compatibility_presentation,
)
from tianji_kb.life_presentation import is_valid_life_presentation
from tianji_kb.public_boundary import find_public_boundary_violations
from tianji_kb.public_projection import project_execution
from tianji_kb.romance_presentation import is_valid_romance_presentation
from tianji_kb.scenario_engine import execute_scenario

BIRTH = "2000-01-07T12:00:00+08:00"
PERSON_B_BIRTH = "1995-06-15T08:30:00+08:00"
TARGET_YEAR = 2026
BANNED_AGE_KEYS = ("start_age", "end_age", "start_date", "end_date")

_CACHE = {}

# (scenario_id, presentation key, validator)
PRESENTATIONS = (
    ("bazi-profile", "profile_presentation",
     is_valid_bazi_profile_presentation),
    ("career", "career_presentation", is_valid_career_presentation),
    ("romance", "romance_presentation", is_valid_romance_presentation),
    ("compatibility", "compatibility_presentation",
     is_valid_compatibility_presentation),
    ("life", "life_presentation", is_valid_life_presentation),
)


def _inputs(scenario_id, role=None):
    if scenario_id == "bazi-profile":
        inputs = {"value": BIRTH,
                  "strength_variant": "ditiansui-root-visibility-v1"}
        if role is not None:
            inputs["traditional_role"] = role
        return inputs
    if scenario_id == "compatibility":
        inputs = {"person_a_birth_value": BIRTH,
                  "person_b_birth_value": PERSON_B_BIRTH}
        if role is not None:
            # Lane D's fixture roles: A male, B female.
            inputs["person_a_traditional_role"] = "male"
            inputs["person_b_traditional_role"] = "female"
        return inputs
    inputs = {"birth_value": BIRTH, "target_year": TARGET_YEAR}
    if role is not None:
        inputs["traditional_role"] = role
    return inputs


def _live(test, scenario_id, role=None):
    """Shared real-backend envelope, computed once per input shape.

    Skips the calling test when the sealed runtime is absent.
    """
    key = (scenario_id, role)
    if key not in _CACHE:
        try:
            _CACHE[key] = execute_scenario(
                scenario_id, _inputs(scenario_id, role))
        except Exception as error:  # sealed data absent locally
            test.skipTest("live scenario needs sealed data: %s" % error)
    return _CACHE[key]


class ScenarioPresentationWiringTests(unittest.TestCase):
    def test_bazi_profile_presentation_attached(self):
        for role, dayun_status in (("male", "presented"),
                                   (None, "not_provided")):
            envelope = _live(self, "bazi-profile", role)
            presentation = envelope["result"]["profile_presentation"]
            self.assertTrue(
                is_valid_bazi_profile_presentation(presentation))
            self.assertEqual(
                [section["id"] for section in presentation["sections"]],
                ["five_elements", "strength", "pattern", "xiyong",
                 "fuyi_research", "dayun", "true_solar"])
            dayun = next(
                section for section in presentation["sections"]
                if section["id"] == "dayun")
            self.assertEqual(dayun["status"], dayun_status)
            if role is not None:
                periods = dayun["periods"]["sanming"]
                self.assertEqual(len(periods), 8)
                self.assertEqual(periods[1]["state"], "interval")
                self.assertIsNotNone(periods[1]["start_interval"])

    def test_career_presentation_carries_full_timeline(self):
        envelope = _live(self, "career", "male")
        presentation = envelope["result"]["career_presentation"]
        self.assertTrue(is_valid_career_presentation(presentation))
        self.assertEqual(
            [section["id"] for section in presentation["sections"]],
            ["natal_ten_gods", "dayun_timeline", "natal_luck_linkage",
             "grounded_boundaries"])
        section = next(
            item for item in presentation["sections"]
            if item["id"] == "dayun_timeline")
        self.assertEqual(section["status"], "presented")
        entries = section["content"]["methods"]["sanming"]["entries"]
        self.assertEqual(len(entries), 8)
        # Q3=A proof: period 2 carries a real interval here.
        self.assertEqual(entries[1]["state"], "interval")
        self.assertIsNotNone(entries[1]["start_interval"])
        self.assertEqual(entries[7]["state"], "interval")
        self.assertIsNotNone(entries[7]["start_interval"])
        # The legacy field stays first-period-trimmed by contract.
        trimmed = envelope["result"]["dayun_presentation"]
        self.assertEqual(
            trimmed["methods"]["sanming"]["entries"][1]["state"],
            "unresolved")
        self.assertIsNone(
            trimmed["methods"]["sanming"]["entries"][1]["start_interval"])

    def test_career_presentation_without_role_has_no_dayun(self):
        envelope = _live(self, "career")
        presentation = envelope["result"]["career_presentation"]
        self.assertTrue(is_valid_career_presentation(presentation))
        section = next(
            item for item in presentation["sections"]
            if item["id"] == "dayun_timeline")
        self.assertEqual(section["status"], "not_presented")
        self.assertNotIn("dayun_presentation", envelope["result"])

    def test_romance_presentation_attached(self):
        envelope = _live(self, "romance", "female")
        presentation = envelope["result"]["romance_presentation"]
        self.assertTrue(is_valid_romance_presentation(presentation))
        self.assertEqual(
            [section["id"] for section in presentation["sections"]],
            ["peach_blossom_spouse_star_palace",
             "natal_marriage_structure", "dayun_liunian_linkage"])

    def test_compatibility_presentation_attached_first_period_only(self):
        envelope = _live(self, "compatibility", "male")
        presentation = envelope["result"]["compatibility_presentation"]
        self.assertTrue(
            is_valid_compatibility_presentation(presentation))
        self.assertEqual(
            [section["id"] for section in presentation["sections"]],
            ["charts", "relations", "patterns_and_xiyong", "dayun",
             "inference_boundary"])
        self.assertIsNone(presentation["unified_verdict"])
        dayun = next(
            section for section in presentation["sections"]
            if section["id"] == "dayun")
        # Q3=A does not cover compatibility: first period only.
        self.assertEqual(dayun["facts"]["periods_opened"], "first_only")

    def test_life_presentation_carries_full_timeline(self):
        envelope = _live(self, "life", "male")
        presentation = envelope["result"]["life_presentation"]
        self.assertTrue(is_valid_life_presentation(presentation))
        self.assertEqual(presentation["dayun"]["status"], "presented")
        self.assertEqual(len(presentation["stages"]), 8)
        self.assertIsNotNone(presentation["stages"][1]["start_interval"])
        self.assertIsNotNone(presentation["stages"][7]["start_interval"])
        self.assertEqual(
            presentation["stages"][1]["age_presentation"], "not_presented")
        # The legacy field stays first-period-trimmed by contract.
        trimmed = envelope["result"]["dayun_presentation"]
        self.assertEqual(
            trimmed["methods"]["sanming"]["entries"][1]["state"],
            "unresolved")

    def test_life_presentation_without_role_has_no_dayun(self):
        envelope = _live(self, "life")
        presentation = envelope["result"]["life_presentation"]
        self.assertTrue(is_valid_life_presentation(presentation))
        self.assertEqual(presentation["dayun"]["status"], "not_presented")
        self.assertNotIn("dayun_presentation", envelope["result"])

    def test_no_starting_age_anywhere_in_five_results(self):
        for scenario_id, _, _ in PRESENTATIONS:
            envelope = _live(self, scenario_id, "male")
            blob = json.dumps(envelope["result"], ensure_ascii=False)
            for banned in BANNED_AGE_KEYS:
                self.assertNotIn(banned, blob, scenario_id)


class ProjectionScopeTests(unittest.TestCase):
    def test_projection_releases_each_presentation_on_its_scenario(self):
        for scenario_id, key, validator in PRESENTATIONS:
            envelope = _live(self, scenario_id, "male")
            projected = project_execution(copy.deepcopy(envelope))
            self.assertIn(key, projected["result"], scenario_id)
            self.assertTrue(validator(projected["result"][key]),
                            scenario_id)

    def test_projection_strips_each_presentation_from_other_scenarios(self):
        # A forged copy on any other scenario must be stripped.
        carriers = {}
        for scenario_id, key, _ in PRESENTATIONS:
            carriers[scenario_id] = _live(self, scenario_id, "male")
        for scenario_id, key, _ in PRESENTATIONS:
            for other_id, _, _ in PRESENTATIONS:
                if other_id == scenario_id:
                    continue
                forged = copy.deepcopy(carriers[other_id])
                forged["result"][key] = copy.deepcopy(
                    carriers[scenario_id]["result"][key])
                projected = project_execution(forged)
                self.assertNotIn(key, projected["result"],
                                 (scenario_id, other_id))

    def test_projected_envelopes_pass_public_boundary_scan(self):
        for scenario_id, _, _ in PRESENTATIONS:
            envelope = _live(self, scenario_id, "male")
            projected = project_execution(copy.deepcopy(envelope))
            self.assertEqual(
                find_public_boundary_violations(projected), [],
                scenario_id)


if __name__ == "__main__":
    unittest.main()
