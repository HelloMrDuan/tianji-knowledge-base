"""Annual branch interactions: reviewed phase2 pair facts, never forecast outcomes."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_core import reviewed_branch_pair_relations
from tianji_kb.scenario_engine import execute_scenario

BIRTH = "2000-01-07T12:00:00+08:00"


class AnnualBranchInteractionsTests(unittest.TestCase):
    def test_2026_hits_have_exact_pillars_and_real_source_evidence(self):
        output = execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2026})
        self.assertTrue(output["deterministic"])
        self.assertFalse(output["public_release"])
        relation = output["result"]["annual_branch_interactions"]
        self.assertEqual(relation["flow_branch"], "午")
        self.assertEqual(relation["evaluated_pairs"], 4)
        self.assertEqual(len(relation["natal_branches_checked"]), 4)
        self.assertFalse(relation["interpretation_allowed"])
        self.assertEqual(set(relation["counts"]), {"six_harmony", "harm", "clash"})
        self.assertEqual(sum(relation["counts"].values()), len(relation["hits"]))
        self.assertGreater(len(relation["hits"]), 0)
        self.assertIn("day", {row["natal_pillar"] for row in relation["hits"]
                              if row["relation_type"] == "clash"})
        original = {p["name"]: p["branch"]["value"] for p in output["result"]["natal"]["pillars"]}
        match = next(m for m in output["rule_matches"]
                     if m["rule_id"] == "bazi.scenario.annual_branch_relations")
        self.assertTrue(match["matched"])
        self.assertEqual(set(match["derived_from_rule_ids"]), {
            "bazi.phase2.branch_six_harmonies",
            "bazi.phase2.branch_six_harms",
            "bazi.phase2.branch_six_clashes",
        })
        self.assertEqual(set(match["evidence_ids"]), set(relation["evidence_ids"]))
        for item in relation["hits"]:
            self.assertEqual(item["natal_branch"], original[item["natal_pillar"]])
            self.assertEqual(item["branches"], ["午", item["natal_branch"]])
            self.assertIn(item["relation_type"],
                          {r["kind"] for r in reviewed_branch_pair_relations(
                              "午", item["natal_branch"])})
            self.assertTrue(item["evidence_ids"])
            self.assertTrue(set(item["evidence_ids"]) <= set(output["evidence"]))
            self.assertEqual(item["rule_id"], {
                "six_harmony": "bazi.phase2.branch_six_harmonies",
                "harm": "bazi.phase2.branch_six_harms",
                "clash": "bazi.phase2.branch_six_clashes",
            }[item["relation_type"]])
            self.assertNotIn("annual_luck_prediction", item)
        self.assertTrue(all(row["evidence_ids"]
                            for row in output["trace"][-1:]))

    def test_2027_different_year_is_recomputed_without_stale_2026_hits(self):
        year26 = execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2026})
        year27 = execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2027})
        a = year26["result"]["annual_branch_interactions"]
        b = year27["result"]["annual_branch_interactions"]
        self.assertEqual(b["flow_branch"], "未")
        self.assertNotEqual(a["hits"], b["hits"])
        self.assertIn("month", {x["natal_pillar"] for x in b["hits"]
                                if x["relation_type"] == "clash"})
        self.assertTrue(all(x["flow_branch"] == "未" for x in b["hits"]))
        self.assertEqual(set(b["counts"]), set(a["counts"]))

    def test_unchanged_natal_and_restricted_output(self):
        year = execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2026})
        self.assertEqual(year["result"]["target_year"]["stem_ten_god"], "食神")
        self.assertEqual(year["result"]["release_scope"], "annual_structure_only")
        self.assertEqual(year["rule_matches"][0]["rule_id"], "bazi.scenario.flow_stem_ten_god")
        self.assertTrue(year["evidence"])
        self.assertEqual(year, execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2026}))
        text = str(year["result"]["annual_branch_interactions"])
        for forbidden in ("fortune_score", "career_score", "wealth_score", "auspicious",
                          "marriage_prediction", "health_prediction", "good_luck"):
            self.assertNotIn(forbidden, text)

    def test_real_public_api_relations_have_same_rule_bound_sources(self):
        with TestClient(create_app()) as client:
            response = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "yearly",
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
        self.assertEqual(response.status_code, 200, response.text)
        out = response.json()
        self.assertEqual(out["result"]["annual_branch_interactions"]["evaluated_pairs"], 4)
        self.assertEqual(len(out["result"]["annual_branch_interactions"]["hits"]),
                         sum(out["result"]["annual_branch_interactions"]["counts"].values()))
        self.assertTrue(out["evidence"])
        self.assertNotIn("prediction", str(out["result"]["annual_branch_interactions"]))

    def test_fails_closed_if_reviewed_relation_citation_is_missing(self):
        from tianji_kb import scenario_engine
        real = scenario_engine.execute

        def broken(domain, inputs):
            result = real(domain, inputs)
            if domain == "bazi" and inputs.get("include_relations"):
                for rule in result["rule_matches"]:
                    if rule["rule_id"] == "bazi.phase2.branch_six_clashes":
                        rule["evidence_ids"] = []
            return result

        with patch.object(scenario_engine, "execute", side_effect=broken):
            with self.assertRaisesRegex(ValueError, "evidence is missing"):
                execute_scenario("yearly", {"birth_value": BIRTH, "target_year": 2026})


if __name__ == "__main__":
    unittest.main()
