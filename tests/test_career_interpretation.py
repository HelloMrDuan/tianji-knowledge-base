"""Career five Ten-God groups: readable semantics derived only from reviewed RuleMatch facts."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb import scenario_engine

BIRTH = "2000-01-07T12:00:00+08:00"

DIRECTIONS = {
    "wealth": "我克",
    "authority": "克我",
    "output": "我生",
    "resource": "生我",
    "peers": "同我",
}


class CareerInterpretationTests(unittest.TestCase):
    def test_five_dynamic_cards_match_exact_executed_ten_god_facts(self):
        output = scenario_engine.execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
        })
        result = output["result"]
        cards = result["interpretation_cards"]
        self.assertEqual(len(cards), 5)
        self.assertEqual({item["group_id"]: item["five_element_relation"] for item in cards},
                         DIRECTIONS)
        for item in cards:
            group = result["structure_groups"][item["group_id"]]
            self.assertEqual(item["visible_count"], group["visible_count"])
            self.assertEqual(item["hidden_count"], group["hidden_count"])
            self.assertEqual(item["ten_gods"], group["ten_gods"])
            self.assertTrue(item["observation"])
            self.assertTrue(item["traditional_structure_definition"])
            self.assertFalse(item["personal_prediction"])
            self.assertEqual(item["interpretation_level"], "reviewed_structural_relation_only")
            self.assertEqual(set(item["source_rule_ids"]), {
                "bazi.phase2.ten_gods", "bazi.phase2.hidden_stems"})
            self.assertTrue(item["evidence_ids"])
            self.assertTrue(set(item["evidence_ids"]) <= set(output["evidence"]))
            expected_presence = (
                "both_layers" if group["visible_count"] and group["hidden_count"] else
                "visible_only" if group["visible_count"] else
                "hidden_only" if group["hidden_count"] else "not_observed")
            self.assertEqual(item["natal_presence"], expected_presence)
        self.assertEqual(sum(i["target_year_stem_matches_group"] for i in cards), 1)
        flow = result["target_year"]
        self.assertEqual(flow["stem_ten_god"], "食神")
        self.assertTrue(next(i for i in cards if i["group_id"] == "output")[
            "target_year_stem_matches_group"])
        self.assertTrue(output["evidence"])

    def test_another_year_changes_year_stem_explanation_without_faking_strength(self):
        first = scenario_engine.execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
        })
        second = scenario_engine.execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2027,
        })
        self.assertNotEqual(first["result"]["target_year"]["stem_ten_god"],
                            second["result"]["target_year"]["stem_ten_god"])
        a, b = first["result"]["interpretation_cards"], second["result"]["interpretation_cards"]
        self.assertEqual([(i["group_id"], i["visible_count"], i["hidden_count"]) for i in a],
                         [(i["group_id"], i["visible_count"], i["hidden_count"]) for i in b])
        self.assertEqual(sum(x["target_year_stem_matches_group"] for x in b), 1)

    def test_public_http_response_is_bound_to_backend_evidence(self):
        with TestClient(create_app()) as client:
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "career",
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        cards = data["result"]["interpretation_cards"]
        self.assertEqual(len(cards), 5)
        self.assertTrue(all(set(c["evidence_ids"]) <= set(data["evidence"]) for c in cards))
        self.assertTrue(all(c["personal_prediction"] is False for c in cards))
        serialized = str(cards)
        for invented in ("wealth_score", "career_score", "wealth_amount",
                         "expected_salary", "good_luck", "raise_prediction"):
            self.assertNotIn(invented, serialized)

    def test_annual_reading_joins_only_executed_natal_locations(self):
        for year in (2026, 2027):
            output = scenario_engine.execute_scenario("career", {
                "birth_value": BIRTH, "target_year": year,
            })
            result = output["result"]
            reading = result["annual_reading"]
            group = result["structure_groups"][result["target_year"]["structure_group"]]
            self.assertEqual(reading["year"], year)
            self.assertEqual(reading["flow_ten_god"], result["target_year"]["stem_ten_god"])
            self.assertEqual(reading["natal_locations"], group["occurrences"])
            self.assertIn(f"{year}年", reading["year_context"])
            self.assertIn(str(group["visible_count"]), reading["natal_context"])
            self.assertIn(str(group["hidden_count"]), reading["natal_context"])
            for occurrence in group["occurrences"]:
                self.assertIn(occurrence["stem"], reading["natal_context"])
                self.assertIn(occurrence["ten_god"], reading["natal_context"])
            self.assertEqual(set(reading["source_rule_ids"]), {
                "bazi.phase2.ten_gods", "bazi.phase2.hidden_stems"})
            self.assertTrue(reading["evidence_ids"])
            self.assertTrue(set(reading["evidence_ids"]) <= set(output["evidence"]))
            self.assertFalse(reading["personal_prediction"])
            self.assertIn("不得用它预测升迁", reading["boundary"])
        self.assertNotEqual(
            scenario_engine.execute_scenario("career", {
                "birth_value": BIRTH, "target_year": 2026,
            })["result"]["annual_reading"]["headline"],
            scenario_engine.execute_scenario("career", {
                "birth_value": BIRTH, "target_year": 2027,
            })["result"]["annual_reading"]["headline"],
        )

    def test_public_annual_reading_has_aliases_and_no_private_evidence_keys(self):
        with TestClient(create_app()) as client:
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "career",
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        reading = data["result"]["annual_reading"]
        self.assertTrue(reading["evidence_ids"])
        self.assertTrue(all(item in data["evidence"] for item in reading["evidence_ids"]))
        self.assertTrue(all(item.startswith("E") for item in reading["evidence_ids"]))
        self.assertTrue(all(item.startswith("R") for item in reading["source_rule_ids"]))
        self.assertNotIn("bazi.phase2", str(reading))
        self.assertNotIn("canonical_path", str(reading))
        self.assertFalse(reading["personal_prediction"])

    def test_missing_executed_canonical_evidence_abstains(self):
        actual = scenario_engine.execute

        def corrupted(domain, inputs):
            output = actual(domain, inputs)
            if domain == "bazi":
                for match in output["rule_matches"]:
                    if match["rule_id"] == "bazi.phase2.hidden_stems":
                        match["evidence_ids"] = []
            return output

        with patch.object(scenario_engine, "execute", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "evidence is missing"):
                scenario_engine.execute_scenario("career", {
                    "birth_value": BIRTH, "target_year": 2026,
                })


if __name__ == "__main__":
    unittest.main()
