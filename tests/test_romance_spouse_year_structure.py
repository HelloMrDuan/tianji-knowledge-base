"""Evidence-bound traditional spouse-palace (day branch) vs flow year, not marriage claims."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb import scenario_engine
from tianji_kb.bazi_core import reviewed_branch_pair_relations

BIRTH = "2000-01-07T12:00:00+08:00"


class RomanceYearSpousePalaceTests(unittest.TestCase):
    def test_2026_day_branch_zi_meets_year_wu_as_clash_with_citations(self):
        result = scenario_engine.execute_scenario("romance", {
            "birth_value": BIRTH, "target_year": 2026,
        })
        self.assertEqual(result["status"], "production_limited")
        self.assertFalse(result["public_release"])
        self.assertEqual(result["result"]["release_scope"], "xianchi_structure_only")
        palace = result["result"]["spouse_palace_year_relations"]
        self.assertEqual((palace["natal_day_branch"], palace["target_year_branch"]), ("子", "午"))
        self.assertEqual(palace["pairs_checked"], 1)
        self.assertFalse(palace["interpretation_allowed"])
        self.assertEqual([r["relation_type"] for r in palace["relations"]], ["clash"])
        self.assertEqual(palace["relations"][0]["rule_id"], "bazi.phase2.branch_six_clashes")
        self.assertEqual(palace["relations"][0]["natal_pillar"], "day")
        self.assertEqual(palace["relations"][0]["branches"], ["午", "子"])
        self.assertEqual(reviewed_branch_pair_relations("午", "子")[0]["kind"], "clash")
        self.assertTrue(palace["evidence_ids"])
        self.assertTrue(set(palace["evidence_ids"]) <= set(result["evidence"]))
        for relation in palace["relations"]:
            self.assertTrue(set(relation["evidence_ids"]) <= set(result["evidence"]))
        match = next(m for m in result["rule_matches"] if
                     m["rule_id"] == "bazi.scenario.spouse_palace_year_structure")
        self.assertTrue(match["matched"])
        self.assertIn("bazi.phase2.spouse_palace_day_branch",
                      match["derived_from_rule_ids"])
        self.assertEqual(set(match["evidence_ids"]), set(palace["evidence_ids"]))
        self.assertEqual(match["facts"]["pairs_checked"], 1)
        self.assertNotIn("fortune_score", str(palace))
        self.assertNotIn("marriage_date", str(palace))

    def test_2027_day_branch_zi_meets_year_wei_as_harm_not_same_answer(self):
        result = scenario_engine.execute_scenario("romance", {
            "birth_value": BIRTH, "target_year": 2027,
        })
        palace = result["result"]["spouse_palace_year_relations"]
        self.assertEqual((palace["natal_day_branch"], palace["target_year_branch"]), ("子", "未"))
        self.assertEqual([r["relation_type"] for r in palace["relations"]], ["harm"])
        self.assertEqual([r["rule_id"] for r in palace["relations"]],
                         ["bazi.phase2.branch_six_harms"])
        self.assertEqual(result["result"]["target_year"]["ganzhi"], "丁未")
        self.assertFalse(palace["interpretation_allowed"])

    def test_no_approved_day_branch_pair_does_not_invent_romance_impact(self):
        result = scenario_engine.execute_scenario("romance", {
            "birth_value": BIRTH, "target_year": 2028,
        })
        palace = result["result"]["spouse_palace_year_relations"]
        self.assertEqual(palace["target_year_branch"], "申")
        self.assertEqual(palace["natal_day_branch"], "子")
        self.assertEqual(palace["pairs_checked"], 1)
        self.assertEqual(palace["relations"], [])
        self.assertFalse(palace["interpretation_allowed"])
        self.assertTrue(set(palace["evidence_ids"]) <= set(result["evidence"]))
        self.assertEqual(result["result"]["target_year"]["ganzhi"], "戊申")
        self.assertFalse(result["public_release"])

    def test_original_two_xianchi_bases_remain_separate_and_evidence_is_real(self):
        result = scenario_engine.execute_scenario("romance", {
            "birth_value": BIRTH, "target_year": 2026,
        })
        self.assertEqual(set(result["result"]["target_year_activation"]),
                         {"year_branch_basis", "day_branch_basis"})
        self.assertEqual(result["result"]["xianchi"]["basis_policy"],
                         "year_and_day_reported_separately")
        self.assertEqual(result["rule_matches"][0]["rule_id"],
                         "bazi.scenario.xianchi_structure")
        self.assertTrue(result["evidence"])
        self.assertEqual(result, scenario_engine.execute_scenario("romance", {
            "birth_value": BIRTH, "target_year": 2026,
        }))

    def test_real_api_provides_same_cited_day_branch_and_no_prediction(self):
        with TestClient(create_app()) as client:
            r = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "romance",
                "input": {"birth_value": BIRTH, "target_year": 2026},
            })
        self.assertEqual(r.status_code, 200, r.text)
        output = r.json()
        palace = output["result"]["spouse_palace_year_relations"]
        self.assertEqual(palace["relations"][0]["relation_type"], "clash")
        self.assertTrue(set(palace["relations"][0]["evidence_ids"]) <= set(output["evidence"]))
        self.assertFalse(palace["interpretation_allowed"])

    def test_missing_spouse_source_denies_new_ability(self):
        actual = scenario_engine.execute

        def remove_source(domain, inputs):
            result = actual(domain, inputs)
            if domain == "bazi":
                for match in result["rule_matches"]:
                    if match["rule_id"] == "bazi.phase2.spouse_palace_day_branch":
                        match["evidence_ids"] = []
            return result

        with patch.object(scenario_engine, "execute", side_effect=remove_source):
            with self.assertRaisesRegex(ValueError, "Spouse palace source evidence is missing"):
                scenario_engine.execute_scenario("romance", {
                    "birth_value": BIRTH, "target_year": 2026,
                })


if __name__ == "__main__":
    unittest.main()
