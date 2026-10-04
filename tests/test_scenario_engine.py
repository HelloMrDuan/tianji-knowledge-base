import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.scenario_engine import execute_scenario, registry


class ScenarioEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app())

    def test_registry_keeps_product_status_explicit(self):
        rows = {item["id"]: item for item in registry()}
        self.assertEqual(len(rows), 11)
        self.assertTrue(rows["bazi-profile"]["public_release"])
        self.assertTrue(rows["question"]["public_release"])
        self.assertFalse(rows["yearly"]["public_release"])
        self.assertEqual(rows["yearly"]["status"], "production_limited")
        self.assertEqual(rows["romance"]["status"], "production_limited")
        self.assertFalse(rows["romance"]["public_release"])
        self.assertEqual(rows["career"]["status"], "production_limited")
        self.assertFalse(rows["career"]["public_release"])
        self.assertEqual(rows["dream"]["status"], "research")

    def test_bazi_profile_scenario_delegates_to_reviewed_engine(self):
        output = execute_scenario("bazi-profile", {"value": "2000-01-07T12:00:00+08:00"})
        self.assertTrue(output["deterministic"])
        self.assertEqual(output["result"]["day_master"]["stem"], "甲")
        self.assertTrue(output["evidence"])

    def test_question_scenario_delegates_to_real_liuyao(self):
        output = execute_scenario("question", {
            "value": "2000-01-07T12:00:00+08:00",
            "yao_values": [9, 7, 7, 7, 7, 7],
        })
        self.assertEqual(output["result"]["changing_lines"], [1])
        self.assertEqual(output["result"]["changed"]["number"], 44)
        self.assertTrue(output["evidence"])

    def test_2026_yearly_structure_is_limited_and_evidence_bound(self):
        output = execute_scenario("yearly", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_year": 2026,
        })
        self.assertEqual(output["result"]["target_year"]["ganzhi"], "丙午")
        self.assertEqual(output["result"]["target_year"]["stem_ten_god"], "食神")
        self.assertEqual(output["result"]["release_scope"], "annual_structure_only")
        self.assertFalse(output["public_release"])
        self.assertTrue(output["evidence"])
        rule = output["rule_matches"][0]
        self.assertEqual(rule["derived_from_rule_id"], "bazi.phase2.ten_gods")
        self.assertTrue(set(rule["evidence_ids"]) <= set(output["evidence"]))
        serialized = str(output["result"])
        for forbidden in ["fortune_score", "auspicious", "taohua_activation", "career_score", "wealth_score"]:
            self.assertNotIn(forbidden, serialized)

    def test_romance_structure_reports_year_and_day_basis_separately(self):
        output = execute_scenario("romance", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_year": 2026,
        })
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["release_scope"], "xianchi_structure_only")
        self.assertEqual(output["result"]["xianchi"]["basis_policy"], "year_and_day_reported_separately")
        self.assertEqual(set(output["result"]["target_year_activation"]), {"year_branch_basis", "day_branch_basis"})
        self.assertTrue(output["evidence"])
        self.assertEqual(output["rule_matches"][0]["derived_from_rule_id"], "bazi.phase2.xianchi_lookup")
        serialized = str(output["result"])
        for forbidden in ["romance_score", "marriage_score", "auspicious", "fortune_score", "relationship_advice"]:
            self.assertNotIn(forbidden, serialized)

    def test_career_wealth_structure_is_position_only_and_evidence_bound(self):
        output = execute_scenario("career", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_year": 2026,
        })
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["release_scope"], "career_wealth_structure_only")
        groups = output["result"]["structure_groups"]
        self.assertEqual(set(groups), {"wealth", "authority", "output", "resource", "peers"})
        self.assertEqual(output["result"]["target_year"]["ganzhi"], "丙午")
        self.assertEqual(output["result"]["target_year"]["stem_ten_god"], "食神")
        self.assertEqual(output["result"]["target_year"]["structure_group"], "output")
        self.assertTrue(output["evidence"])
        self.assertEqual(
            output["rule_matches"][0]["derived_from_rule_ids"],
            ["bazi.phase2.ten_gods", "bazi.phase2.hidden_stems"],
        )
        serialized = str(output["result"])
        for forbidden in ["career_score", "wealth_score", "income", "investment_advice", "auspicious"]:
            self.assertNotIn(forbidden, serialized)

    def test_scenario_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            execute_scenario("yearly", {"birth_value": "x", "target_year": 2026, "extra": True})
        with self.assertRaises(ValueError):
            execute_scenario("romance", {})
        with self.assertRaises(ValueError):
            execute_scenario("missing", {})

    def test_http_scenario_registry_and_execution_never_call_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            rows = self.client.get("/api/v1/scenarios")
            self.assertEqual(rows.status_code, 200)
            self.assertEqual(len(rows.json()["scenarios"]), 11)
            response = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "yearly",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "target_year": 2026,
                },
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["result"]["target_year"]["ganzhi"], "丙午")
        self.assertFalse(data["public_release"])
        self.assertTrue(data["limitations"])

    def test_http_career_structure_never_calls_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            response = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "career",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "target_year": 2026,
                },
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["scenario_id"], "career")
        self.assertEqual(data["result"]["target_year"]["stem_ten_god"], "食神")
        self.assertEqual(data["result"]["release_scope"], "career_wealth_structure_only")
        self.assertFalse(data["public_release"])
        self.assertTrue(data["evidence"])

    def test_http_rejects_unimplemented_and_unknown_inputs(self):
        response = self.client.post("/api/v1/scenarios/execute", json={"scenario_id": "compatibility", "input": {}})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "yearly",
            "input": {"birth_value": "2000-01-07T12:00:00+08:00", "target_year": "2026"},
        })
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
