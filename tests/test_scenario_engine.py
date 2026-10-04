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
        self.assertEqual(rows["daily"]["status"], "production_limited")
        self.assertFalse(rows["daily"]["public_release"])
        self.assertEqual(rows["weekly"]["status"], "production_limited")
        self.assertEqual(rows["monthly"]["status"], "production_limited")
        self.assertFalse(rows["weekly"]["public_release"])
        self.assertFalse(rows["monthly"]["public_release"])
        self.assertFalse(rows["yearly"]["public_release"])
        self.assertEqual(rows["yearly"]["status"], "production_limited")
        self.assertEqual(rows["romance"]["status"], "production_limited")
        self.assertFalse(rows["romance"]["public_release"])
        self.assertEqual(rows["career"]["status"], "production_limited")
        self.assertFalse(rows["career"]["public_release"])
        self.assertEqual(rows["compatibility"]["status"], "production_limited")
        self.assertFalse(rows["compatibility"]["public_release"])
        self.assertEqual(rows["life"]["status"], "production_limited")
        self.assertFalse(rows["life"]["public_release"])
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

    def test_daily_structure_is_repeatable_and_evidence_bound(self):
        payload = {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_date": "2026-10-04",
        }
        first = execute_scenario("daily", payload)
        second = execute_scenario("daily", payload)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "production_limited")
        self.assertFalse(first["public_release"])
        self.assertEqual(first["result"]["release_scope"], "daily_structure_only")
        self.assertEqual(first["result"]["target_day"]["date"], "2026-10-04")
        self.assertEqual(len(first["result"]["target_day"]["ganzhi"]), 2)
        self.assertTrue(first["result"]["target_day"]["stem_ten_god"])
        self.assertEqual(
            set(first["result"]["xianchi"]["target_day_activation"]),
            {"year_branch_basis", "day_branch_basis"},
        )
        self.assertTrue(first["evidence"])
        self.assertEqual(
            first["rule_matches"][0]["derived_from_rule_ids"],
            ["bazi.phase2.ten_gods", "bazi.phase2.xianchi_lookup"],
        )
        serialized = str(first["result"])
        for forbidden in [
            "fortune_score", "daily_score", "auspicious", "investment_advice",
            "health_advice", "relationship_advice",
        ]:
            self.assertNotIn(forbidden, serialized)

    def test_weekly_structure_has_exact_monday_to_sunday_window(self):
        output = execute_scenario("weekly", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "anchor_date": "2026-10-04",
        })
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["release_scope"], "weekly_structure_only")
        self.assertEqual(output["result"]["week"]["start_date"], "2026-09-28")
        self.assertEqual(output["result"]["week"]["end_date"], "2026-10-04")
        self.assertEqual(len(output["result"]["week"]["days"]), 7)
        self.assertTrue(output["evidence"])
        self.assertEqual(
            output["rule_matches"][0]["derived_from_rule_ids"],
            ["bazi.phase2.ten_gods", "bazi.phase2.xianchi_lookup"],
        )
        serialized = str(output["result"])
        for forbidden in ["fortune_score", "weekly_score", "auspicious", "investment_advice"]:
            self.assertNotIn(forbidden, serialized)

    def test_monthly_structure_has_every_calendar_day_and_summary(self):
        output = execute_scenario("monthly", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_month": "2026-10",
        })
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["release_scope"], "monthly_structure_only")
        self.assertEqual(output["result"]["month"]["target_month"], "2026-10")
        self.assertEqual(output["result"]["month"]["day_count"], 31)
        self.assertEqual(len(output["result"]["month"]["days"]), 31)
        self.assertEqual(
            sum(output["result"]["summary"]["structure_group_counts"].values()),
            31,
        )
        self.assertTrue(output["evidence"])
        serialized = str(output["result"])
        for forbidden in ["fortune_score", "monthly_score", "auspicious", "investment_advice"]:
            self.assertNotIn(forbidden, serialized)

    def test_2026_yearly_structure_is_limited_and_evidence_bound(self):
        output = execute_scenario("yearly", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_year": 2026,
        })
        self.assertEqual(output["result"]["target_year"]["ganzhi"], "丙午")
        self.assertEqual(output["result"]["target_year"]["stem_ten_god"], "食神")
        self.assertEqual(output["result"]["release_scope"], "annual_structure_v2")
        self.assertFalse(output["public_release"])
        self.assertTrue(output["evidence"])
        relations = output["result"]["target_year"]["branch_relations"]
        self.assertIn(
            {"kind": "clash", "natal_pillar": "day", "natal_branch": "子", "flow_branch": "午"},
            relations,
        )
        rule = output["rule_matches"][0]
        self.assertEqual(rule["derived_from_rule_id"], "bazi.phase2.ten_gods")
        self.assertEqual(
            rule["derived_from_rule_ids"],
            [
                "bazi.phase2.ten_gods",
                "bazi.phase2.branch_six_harmonies",
                "bazi.phase2.branch_six_harms",
                "bazi.phase2.branch_six_clashes",
            ],
        )
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
        self.assertEqual(output["result"]["release_scope"], "romance_structure_v2")
        self.assertEqual(output["result"]["xianchi"]["basis_policy"], "year_and_day_reported_separately")
        self.assertEqual(set(output["result"]["target_year_activation"]), {"year_branch_basis", "day_branch_basis"})
        self.assertEqual(output["result"]["spouse_palace_interaction"]["day_branch"], "子")
        self.assertEqual(output["result"]["spouse_palace_interaction"]["target_year_branch"], "午")
        self.assertEqual(
            output["result"]["spouse_palace_interaction"]["relations"],
            [{"kind": "clash", "natal_pillar": "day", "natal_branch": "子", "flow_branch": "午"}],
        )
        self.assertTrue(output["evidence"])
        self.assertEqual(output["rule_matches"][0]["derived_from_rule_id"], "bazi.phase2.xianchi_lookup")
        self.assertEqual(
            output["rule_matches"][0]["derived_from_rule_ids"],
            [
                "bazi.phase2.xianchi_lookup",
                "bazi.phase2.spouse_palace_day_branch",
                "bazi.phase2.branch_six_harmonies",
                "bazi.phase2.branch_six_harms",
                "bazi.phase2.branch_six_clashes",
            ],
        )
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

    def test_compatibility_structure_is_bidirectional_and_non_scoring(self):
        output = execute_scenario("compatibility", {
            "person_a_birth_value": "2000-01-07T12:00:00+08:00",
            "person_b_birth_value": "2000-02-01T12:00:00+08:00",
        })
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["release_scope"], "two_person_structure_only")
        self.assertEqual(output["result"]["report_version"], "compatibility-structure-v3")
        relations = output["result"]["day_master_relations"]
        self.assertEqual(relations["a_sees_b"]["ten_god"], "正财")
        self.assertEqual(relations["b_sees_a"]["ten_god"], "正官")
        self.assertEqual(
            set(output["result"]["xianchi_cross_matches"]),
            {"a_targets_vs_b", "b_targets_vs_a"},
        )
        reviewed = output["result"]["reviewed_cross_relations"]
        self.assertTrue(reviewed["day_master_five_combination"]["matched"])
        self.assertEqual(reviewed["day_master_five_combination"]["stems"], ["甲", "己"])
        self.assertEqual(reviewed["day_master_five_combination"]["traditional_result_element"], "土")
        self.assertEqual(
            reviewed["spouse_palace_relation"]["relations"],
            [{"kind": "six_harmony", "branches": ["子", "丑"], "traditional_result_element": "土"}],
        )
        self.assertEqual(output["result"]["person_a"]["spouse_palace"]["day_branch"], "子")
        self.assertEqual(output["result"]["person_b"]["spouse_palace"]["day_branch"], "丑")
        self.assertIn("natal_triple_harmonies", output["result"]["person_a"])
        self.assertIn("natal_triple_harmonies", output["result"]["person_b"])
        self.assertIsNone(output["result"]["person_a"]["traditional_spouse_star_lens"])
        self.assertIsNone(output["result"]["person_b"]["traditional_spouse_star_lens"])
        self.assertTrue(output["evidence"])
        self.assertEqual(
            output["rule_matches"][0]["derived_from_rule_ids"],
            [
                "bazi.phase2.ten_gods",
                "bazi.phase2.xianchi_lookup",
                "bazi.phase2.stem_five_combinations",
                "bazi.phase2.branch_six_harmonies",
                "bazi.phase2.branch_six_harms",
                "bazi.phase2.branch_six_clashes",
                "bazi.phase2.branch_triple_harmonies",
                "bazi.phase2.spouse_palace_day_branch",
            ],
        )
        serialized = str(output["result"])
        for forbidden in [
            "compatibility_score", "match_score", "love_score", "marriage_score",
            "auspicious", "relationship_advice", "breakup_risk",
        ]:
            self.assertNotIn(forbidden, serialized)

    def test_compatibility_optional_spouse_star_lenses_are_user_selected(self):
        output = execute_scenario("compatibility", {
            "person_a_birth_value": "2000-01-07T12:00:00+08:00",
            "person_b_birth_value": "2000-02-01T12:00:00+08:00",
            "person_a_traditional_role": "male",
            "person_b_traditional_role": "female",
        })
        self.assertEqual(output["result"]["report_version"], "compatibility-structure-v3")
        a_lens = output["result"]["person_a"]["traditional_spouse_star_lens"]
        b_lens = output["result"]["person_b"]["traditional_spouse_star_lens"]
        self.assertEqual(a_lens["traditional_role"], "male")
        self.assertEqual(a_lens["candidate_ten_gods"], ["正财", "偏财"])
        self.assertEqual(b_lens["traditional_role"], "female")
        self.assertEqual(b_lens["candidate_ten_gods"], ["正官", "七杀"])
        self.assertFalse(a_lens["interpretation_allowed"])
        self.assertFalse(b_lens["interpretation_allowed"])
        self.assertIn("bazi.phase2.spouse_star_lens", output["rule_matches"][0]["derived_from_rule_ids"])
        self.assertTrue(any(step["step"] == "traditional_spouse_star_lenses" for step in output["trace"]))
        serialized = str(output["result"])
        for forbidden in ["spouse_score", "marriage_score", "match_score", "relationship_advice"]:
            self.assertNotIn(forbidden, serialized)

    def test_compatibility_rejects_inferred_or_unknown_traditional_role(self):
        with self.assertRaises(ValueError):
            execute_scenario("compatibility", {
                "person_a_birth_value": "2000-01-07T12:00:00+08:00",
                "person_b_birth_value": "2000-02-01T12:00:00+08:00",
                "person_a_traditional_role": "unknown",
            })

    def test_life_overview_aggregates_only_validated_sections(self):
        output = execute_scenario("life", {
            "birth_value": "2000-01-07T12:00:00+08:00",
            "target_year": 2026,
        })
        self.assertEqual(output["scenario_id"], "life")
        self.assertEqual(output["status"], "production_limited")
        self.assertFalse(output["public_release"])
        self.assertEqual(output["result"]["report_version"], "life-overview-v1")
        self.assertEqual(output["result"]["release_scope"], "deterministic_aggregate_only")
        self.assertEqual(output["result"]["yearly"]["target_year"]["ganzhi"], "丙午")
        self.assertIn("romance", output["result"])
        self.assertIn("career", output["result"])
        self.assertEqual(
            {item["id"] for item in output["result"]["highlights"]},
            {"foundation", "yearly", "romance", "career"},
        )
        self.assertTrue(output["evidence"])
        self.assertTrue(output["rule_matches"])
        self.assertTrue(output["trace"])
        serialized = str(output["result"])
        for forbidden in [
            "fortune_score", "romance_score", "marriage_score", "career_score",
            "wealth_score", "income", "investment_advice", "auspicious",
        ]:
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
        self.assertIn(
            {"kind": "clash", "natal_pillar": "day", "natal_branch": "子", "flow_branch": "午"},
            data["result"]["target_year"]["branch_relations"],
        )
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

    def test_http_weekly_and_monthly_structure_never_call_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            weekly = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "weekly",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "anchor_date": "2026-10-04",
                },
            })
            monthly = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "monthly",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "target_month": "2026-10",
                },
            })
        self.assertEqual(weekly.status_code, 200, weekly.text)
        self.assertEqual(monthly.status_code, 200, monthly.text)
        self.assertEqual(len(weekly.json()["result"]["week"]["days"]), 7)
        self.assertEqual(monthly.json()["result"]["month"]["day_count"], 31)
        self.assertFalse(weekly.json()["public_release"])
        self.assertFalse(monthly.json()["public_release"])

    def test_http_daily_structure_never_calls_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            response = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "daily",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "target_date": "2026-10-04",
                },
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["scenario_id"], "daily")
        self.assertEqual(data["result"]["target_day"]["date"], "2026-10-04")
        self.assertEqual(data["result"]["release_scope"], "daily_structure_only")
        self.assertFalse(data["public_release"])
        self.assertTrue(data["evidence"])

    def test_http_compatibility_structure_never_calls_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            response = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "compatibility",
                "input": {
                    "person_a_birth_value": "2000-01-07T12:00:00+08:00",
                    "person_b_birth_value": "2000-02-01T12:00:00+08:00",
                },
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["scenario_id"], "compatibility")
        self.assertEqual(data["result"]["release_scope"], "two_person_structure_only")
        self.assertEqual(data["result"]["report_version"], "compatibility-structure-v3")
        self.assertEqual(data["result"]["day_master_relations"]["a_sees_b"]["ten_god"], "正财")
        self.assertTrue(data["result"]["reviewed_cross_relations"]["day_master_five_combination"]["matched"])
        self.assertEqual(
            data["result"]["reviewed_cross_relations"]["spouse_palace_relation"]["relations"][0]["kind"],
            "six_harmony",
        )
        self.assertFalse(data["public_release"])
        self.assertTrue(data["evidence"])

    def test_http_life_overview_never_calls_model(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network model call forbidden")):
            response = self.client.post("/api/v1/scenarios/execute", json={
                "scenario_id": "life",
                "input": {
                    "birth_value": "2000-01-07T12:00:00+08:00",
                    "target_year": 2026,
                },
            })
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["scenario_id"], "life")
        self.assertEqual(data["result"]["report_version"], "life-overview-v1")
        self.assertEqual(data["result"]["yearly"]["target_year"]["ganzhi"], "丙午")
        self.assertFalse(data["public_release"])
        self.assertTrue(data["evidence"])

    def test_http_rejects_unimplemented_and_unknown_inputs(self):
        response = self.client.post("/api/v1/scenarios/execute", json={"scenario_id": "dream", "input": {}})
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "compatibility",
            "input": {"person_a_birth_value": "2000-01-07T12:00:00+08:00"},
        })
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "yearly",
            "input": {"birth_value": "2000-01-07T12:00:00+08:00", "target_year": "2026"},
        })
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "daily",
            "input": {"birth_value": "2000-01-07T12:00:00+08:00", "target_date": "2026/10/04"},
        })
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "weekly",
            "input": {"birth_value": "2000-01-07T12:00:00+08:00", "anchor_date": "bad-date"},
        })
        self.assertEqual(response.status_code, 422)
        response = self.client.post("/api/v1/scenarios/execute", json={
            "scenario_id": "monthly",
            "input": {"birth_value": "2000-01-07T12:00:00+08:00", "target_month": "2026/10"},
        })
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
