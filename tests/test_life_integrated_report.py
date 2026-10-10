"""Life overview combines reviewed factors and scenario facts; rejects absent evidence."""
import copy
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tianji_kb import scenario_engine
from tianji_kb.api import create_app

BIRTH = "2000-01-07T12:00:00+08:00"


class IntegratedLifeReportTests(unittest.TestCase):
    def run_life(self, year=2026):
        return scenario_engine.execute_scenario("life", {
            "birth_value": BIRTH, "target_year": year,
        })

    def test_year_changes_real_career_and_romance_but_not_natal_strength_factors(self):
        first = self.run_life()
        second = self.run_life(2027)
        a, b = first["result"], second["result"]
        self.assertEqual(a["report_version"], "life-overview-v1")
        self.assertEqual(a["profile"]["strength_context"], b["profile"]["strength_context"])
        self.assertNotEqual(a["integrated_reading"]["career"], b["integrated_reading"]["career"])
        self.assertEqual(a["integrated_reading"]["target_year"], 2026)
        self.assertEqual(b["integrated_reading"]["target_year"], 2027)
        self.assertIn("2027年", b["integrated_reading"]["romance"])
        for result in (first, second):
            report = result["result"]["integrated_reading"]
            strength = result["result"]["profile"]["strength_context"]
            self.assertEqual(strength["classification"], "unresolved")
            self.assertFalse(report["dayun_timeline_approved"])
            self.assertFalse(report["strength_classification_approved"])
            self.assertFalse(report["personal_prediction"])
            self.assertTrue(report["evidence_ids"])
            self.assertTrue(set(report["evidence_ids"]) <= set(result["evidence"]))
            self.assertTrue(set(strength["evidence_ids"]) <= set(result["evidence"]))
            self.assertIn("大运方向", report["dayun"])
            self.assertNotIn("fortune_score", str(report))

    def test_shared_yearly_and_spouse_pair_is_one_evidence_chain(self):
        for year in (2026, 2027):
            with self.subTest(year=year):
                response = self.run_life(year)
                data = response["result"]
                audit = data["cross_rule_audit"]
                annual = data["yearly"]["annual_branch_interactions"]
                spouse = data["romance"]["spouse_palace_year_relations"]
                day_hits = [hit for hit in annual["hits"] if hit["natal_pillar"] == "day"]
                self.assertEqual(day_hits, spouse["relations"])
                self.assertEqual(audit["shared_pair_count"], len(day_hits))
                self.assertTrue(audit["yearly_and_romance_agree"])
                self.assertFalse(audit["independent_confirmations"])
                self.assertFalse(audit["interpretation_allowed"])
                self.assertIn("并非两份独立证据", audit["reading"])
                self.assertEqual(data["integrated_reading"]["cross_rule"], audit["reading"])
                self.assertTrue(set(audit["evidence_ids"]) <= set(response["evidence"]))
                self.assertFalse(response["result"]["integrated_reading"]["personal_prediction"])

    def test_cross_rule_mismatch_fails_closed(self):
        original = scenario_engine._romance

        def corrupted(inputs):
            result = copy.deepcopy(original(inputs))
            result["result"]["spouse_palace_year_relations"]["natal_day_branch"] = "INVALID"
            return result

        with patch.object(scenario_engine, "_romance", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "Cross-scenario"):
                self.run_life(2027)

    def test_shared_pair_mismatch_fails_closed(self):
        original = scenario_engine._romance

        def corrupted(inputs):
            result = copy.deepcopy(original(inputs))
            result["result"]["spouse_palace_year_relations"]["relations"].append(
                {"natal_pillar": "day", "relation_type": "clash", "evidence_ids": []})
            return result

        with patch.object(scenario_engine, "_romance", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "Cross-scenario"):
                self.run_life(2026)

    def test_integrated_career_is_identical_to_reviewed_career_scenario_facts(self):
        life = self.run_life()["result"]
        career = scenario_engine.execute_scenario("career", {
            "birth_value": BIRTH, "target_year": 2026,
        })["result"]["annual_reading"]
        self.assertEqual(life["integrated_reading"]["career"],
                         career["year_context"] + career["natal_context"])
        self.assertIn(career["year_context"], life["integrated_reading"]["career"])

    def test_missing_strength_evidence_fails_closed(self):
        original = scenario_engine.execute

        def corrupted(domain, inputs):
            output = original(domain, inputs)
            if domain == "bazi" and inputs.get("strength_variant"):
                for row in output["rule_matches"]:
                    if row["rule_id"] == "bazi.phase2.root_candidates":
                        row["evidence_ids"] = []
            return output

        with patch.object(scenario_engine, "execute", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "Reviewed strength factor"):
                self.run_life()

    def test_conflicting_year_facts_do_not_produce_composed_reading(self):
        original = scenario_engine._career

        def mismatched(inputs):
            result = copy.deepcopy(original(inputs))
            result["result"]["target_year"]["ganzhi"] = "甲子"
            return result

        with patch.object(scenario_engine, "_career", side_effect=mismatched):
            with self.assertRaisesRegex(ValueError, "Scenario year facts disagree"):
                self.run_life()

    def test_four_scenarios_and_evidence_provenance_share_verified_identity(self):
        for year in (2026, 2027):
            with self.subTest(year=year):
                life = self.run_life(year)
                audit = life["result"]["integration_provenance"]
                self.assertEqual(audit["source_scenarios"],
                                 ["profile", "yearly", "romance", "career"])
                self.assertTrue(audit["all_natal_charts_identical"])
                self.assertTrue(audit["all_target_years_identical"])
                self.assertEqual(audit["evidence_identity_conflicts"], 0)
                self.assertFalse(audit["independent_evidence_claim"])
                self.assertFalse(audit["interpretation_allowed"])
                self.assertFalse(audit["dayun_timeline_approved"])
                self.assertFalse(audit["strength_classification_approved"])
                self.assertEqual(audit["evidence_ids"],
                                 life["result"]["integrated_reading"]["evidence_ids"])
                self.assertTrue(all(eid in life["evidence"]
                                    for eid in audit["evidence_ids"]))
                self.assertTrue(all(audit["evidence_scenarios"][eid]
                                    for eid in audit["evidence_ids"]))

    def test_other_scenario_natal_chart_mismatch_fails_closed(self):
        for scenario in ("yearly", "romance", "career"):
            original = getattr(scenario_engine, "_" + scenario)

            def corrupted(inputs, *, original=original):
                output = copy.deepcopy(original(inputs))
                output["result"]["natal"]["day_master"]["stem"] = "假"
                return output

            with self.subTest(scenario=scenario):
                with patch.object(scenario_engine, "_" + scenario, side_effect=corrupted):
                    with self.assertRaisesRegex(ValueError, "natal chart identity"):
                        self.run_life()

    def test_year_number_disagreement_fails_closed_even_if_ganzhi_matches(self):
        for scenario in ("yearly", "romance", "career"):
            original = getattr(scenario_engine, "_" + scenario)

            def corrupted(inputs, *, original=original):
                output = copy.deepcopy(original(inputs))
                output["result"]["target_year"]["year"] = 1900
                return output

            with self.subTest(scenario=scenario):
                with patch.object(scenario_engine, "_" + scenario, side_effect=corrupted):
                    with self.assertRaisesRegex(ValueError, "target-year identity"):
                        self.run_life(2027)

    def test_reused_evidence_id_with_different_source_fails_closed(self):
        original = scenario_engine._career

        def corrupted(inputs):
            output = copy.deepcopy(original(inputs))
            eid = next(iter(output["evidence"]))
            output["evidence"][eid]["original_text"] = "伪造证据（只在测试中）"
            return output

        with patch.object(scenario_engine, "_career", side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "evidence identity collision"):
                self.run_life()

    def test_public_http_projection_contains_sources_not_private_rule_identifiers(self):
        with TestClient(create_app()) as client:
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "life", "input": {"birth_value": BIRTH, "target_year": 2026},
            })
            profile = client.post("/api/v1/public/execute", json={
                "domain": "bazi", "variant": "ziping-structural-v1",
                "input": {"value": BIRTH, "strength_variant": "ditiansui-root-visibility-v1"},
                "mode": "production", "explain": False,
            })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(profile.status_code, 200, profile.text)
        data = response.json()
        report = data["result"]["integrated_reading"]
        self.assertTrue(all(eid in data["evidence"] for eid in report["evidence_ids"]))
        self.assertTrue(all(eid.startswith("E") for eid in report["evidence_ids"]))
        strength = data["result"]["profile"]["strength_context"]
        self.assertTrue(all(x.startswith("R") for x in strength["source_rule_ids"]))
        self.assertNotIn("bazi.phase2", str(strength))
        self.assertIn("strength_factors", profile.json()["chart"])
        self.assertIsNone(profile.json()["chart"]["strength_factors"]["overall_strength"])


if __name__ == "__main__":
    unittest.main()
