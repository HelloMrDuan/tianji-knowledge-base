"""TJ-025.2 condition markers against the real life integrated report.

Offline acceptance only (NOT public CI): executing the life scenario needs
the assembled reviewed production runtime, exactly like
test_life_integrated_report.py. These tests pin the marker surface to the
real report it summarises: same birth instant, same target year, markers
derived from the same fact set as the per-dimension prose exits.
"""
import copy
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tianji_kb import scenario_engine
from tianji_kb.api import create_app

BIRTH = "2000-01-07T12:00:00+08:00"
NOT_AVAILABLE = "本项尚未具备解释条件"
AVAILABLE = "具备解释条件"
NOT_AVAILABLE_DIMENSIONS = {
    "cross_rule_synthesis": "shared_rules_not_independent_evidence",
    "strength_classification": "strength_classification_unresolved",
    "dayun_timeline": "no_approved_production_rule",
    "personal_evaluation": "comprehensive_synthesis_not_approved",
}


class LifeConditionMarkerEndToEndTests(unittest.TestCase):
    def run_life(self, year=2026):
        return scenario_engine.execute_scenario("life", {
            "birth_value": BIRTH, "target_year": year,
        })

    def markers_by_dimension(self, response):
        return {m["dimension"]: m
                for m in response["result"]["condition_markers"]}

    def test_marker_set_matches_report_dimensions_and_exits(self):
        for year in (2026, 2027):
            with self.subTest(year=year):
                response = self.run_life(year)
                result = response["result"]
                markers = result["condition_markers"]
                self.assertEqual(
                    [m["dimension"] for m in markers],
                    ["natal_foundation", "annual_career", "annual_romance",
                     "cross_rule_synthesis", "strength_classification",
                     "dayun_timeline", "personal_evaluation"])
                by_dim = self.markers_by_dimension(response)
                reading = result["integrated_reading"]
                strength = result["profile"]["strength_context"]
                audit = result["cross_rule_audit"]
                # Marker <-> prose exit consistency, field by field.
                self.assertEqual(by_dim["natal_foundation"]["exit_text"],
                                 reading["foundation"])
                self.assertEqual(by_dim["annual_career"]["exit_text"],
                                 reading["career"])
                self.assertEqual(by_dim["annual_romance"]["exit_text"],
                                 reading["romance"])
                self.assertEqual(by_dim["cross_rule_synthesis"]["exit_text"],
                                 audit["reading"])
                self.assertEqual(by_dim["strength_classification"]["exit_text"],
                                 strength["boundary"])
                self.assertEqual(by_dim["dayun_timeline"]["exit_text"],
                                 reading["dayun"])
                self.assertEqual(by_dim["personal_evaluation"]["exit_text"],
                                 reading["boundary"])
                # Refused dimensions: WBS statement + reason category, and
                # the marker basis equals the report's own flags.
                for dimension, category in NOT_AVAILABLE_DIMENSIONS.items():
                    m = by_dim[dimension]
                    self.assertEqual(m["condition"], "not_available", dimension)
                    self.assertEqual(m["statement"], NOT_AVAILABLE, dimension)
                    self.assertEqual(m["reason_category"], category, dimension)
                self.assertEqual(
                    by_dim["strength_classification"]["basis"]["classification"],
                    strength["classification"])
                self.assertFalse(
                    by_dim["dayun_timeline"]["basis"]["dayun_timeline_approved"])
                self.assertFalse(by_dim["cross_rule_synthesis"]["basis"]
                                 ["interpretation_allowed"])
                self.assertFalse(by_dim["personal_evaluation"]["basis"]
                                 ["personal_prediction"])
                # Structural dimensions: available for reviewed structure
                # only, never as interpretation or evaluation.
                for dimension in ("natal_foundation", "annual_career",
                                  "annual_romance"):
                    m = by_dim[dimension]
                    self.assertEqual(m["condition"], "available", dimension)
                    self.assertEqual(m["statement"], AVAILABLE, dimension)
                    self.assertEqual(m["scope"], "reviewed_structure_only",
                                     dimension)
                # Marker evidence is a subset of the report's own evidence.
                for m in markers:
                    self.assertTrue(
                        set(m["evidence_ids"]) <= set(response["evidence"]),
                        m["dimension"])
                self.assertFalse(reading["personal_prediction"])
                self.assertNotIn("fortune_score", str(markers))
                self.assertEqual(response["status"], "production_limited")
                self.assertFalse(response["public_release"])

    def test_markers_track_year_and_natal_facts_like_the_report(self):
        first = self.markers_by_dimension(self.run_life(2026))
        second = self.markers_by_dimension(self.run_life(2027))
        # Natal-bound markers are identical across target years.
        for dimension in ("natal_foundation", "strength_classification",
                          "dayun_timeline", "personal_evaluation"):
            self.assertEqual(first[dimension], second[dimension], dimension)
        # Annual markers follow the target year's own exits.
        self.assertNotEqual(first["annual_career"]["exit_text"],
                            second["annual_career"]["exit_text"])
        self.assertNotEqual(first["annual_romance"]["exit_text"],
                            second["annual_romance"]["exit_text"])
        self.assertIn("2027", second["annual_romance"]["exit_text"])

    def test_zero_hit_romance_year_still_marks_structure_available(self):
        # 1985-11-02 x 2024 (verified on the assembled runtime): the
        # spouse-palace relation computation legitimately produces zero
        # hits. Zero hits is itself the presented structural fact
        # ("未命中已审核的六合、六害、六冲"), so the romance marker must
        # stay available on the reviewed rule evidence instead of
        # flipping to not_available.
        response = scenario_engine.execute_scenario("life", {
            "birth_value": "1985-11-02T22:40:00+08:00", "target_year": 2024,
        })
        result = response["result"]
        spouse = result["romance"]["spouse_palace_year_relations"]
        self.assertEqual(spouse["relations"], [])
        self.assertTrue(spouse["evidence_ids"])
        marker = {m["dimension"]: m
                  for m in result["condition_markers"]}["annual_romance"]
        self.assertEqual(marker["condition"], "available")
        self.assertEqual(marker["statement"], AVAILABLE)
        self.assertEqual(marker["scope"], "reviewed_structure_only")
        self.assertEqual(marker["evidence_ids"], spouse["evidence_ids"])
        self.assertTrue(set(marker["evidence_ids"]) <= set(response["evidence"]))
        self.assertEqual(marker["exit_text"],
                         result["integrated_reading"]["romance"])
        self.assertIn("未命中已审核的六合、六害、六冲", marker["exit_text"])

    def test_fail_closed_compositions_produce_no_markers(self):
        original = scenario_engine._romance

        def corrupted(inputs):
            result = copy.deepcopy(original(inputs))
            result["result"]["spouse_palace_year_relations"][
                "natal_day_branch"] = "INVALID"
            return result

        with patch.object(scenario_engine, "_romance", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "Cross-scenario"):
                self.run_life(2027)

        original_execute = scenario_engine.execute

        def corrupted_execute(domain, inputs):
            output = original_execute(domain, inputs)
            if domain == "bazi" and inputs.get("strength_variant"):
                for row in output["rule_matches"]:
                    if row["rule_id"] == "bazi.phase2.root_candidates":
                        row["evidence_ids"] = []
            return output

        with patch.object(scenario_engine, "execute",
                          side_effect=corrupted_execute):
            with self.assertRaisesRegex(ValueError, "Reviewed strength factor"):
                self.run_life()

    def test_public_projection_keeps_markers_without_private_identifiers(self):
        with TestClient(create_app()) as client:
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "life",
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        markers = data["result"]["condition_markers"]
        by_dim = {m["dimension"]: m for m in markers}
        self.assertEqual(by_dim["dayun_timeline"]["statement"], NOT_AVAILABLE)
        self.assertEqual(by_dim["strength_classification"]["statement"],
                         NOT_AVAILABLE)
        self.assertEqual(by_dim["natal_foundation"]["statement"], AVAILABLE)
        for m in markers:
            self.assertTrue(all(eid.startswith("E")
                                for eid in m["evidence_ids"]))
            self.assertTrue(all(eid in data["evidence"]
                                for eid in m["evidence_ids"]))
        self.assertNotIn("bazi.phase2", str(markers))
        self.assertNotIn("rule_id", str(markers))


if __name__ == "__main__":
    unittest.main()
