"""Daily, weekly and monthly target branch pair results backed by real Phase2 evidence."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_core import reviewed_branch_pair_relations
from tianji_kb import scenario_engine

BIRTH = "2000-01-07T12:00:00+08:00"
NATAL_BRANCHES = ["辰", "丑", "子", "午"]
RELATION_IDS = {
    "six_harmony": "bazi.phase2.branch_six_harmonies",
    "harm": "bazi.phase2.branch_six_harms",
    "clash": "bazi.phase2.branch_six_clashes",
}


def daily(on_date):
    return scenario_engine.execute_scenario("daily", {
        "birth_value": BIRTH,
        "target_date": on_date,
    })


class DailyPeriodBranchRelationsTests(unittest.TestCase):
    def test_daily_recalculates_real_date_and_four_natal_pillar_pairs(self):
        for target_date in ("2026-10-04", "2026-10-05", "2027-02-03"):
            with self.subTest(target_date=target_date):
                item = daily(target_date)
                structure = item["result"]["day_branch_interactions"]
                branch = item["result"]["target_day"]["branch"]
                self.assertEqual(structure["flow_branch"], branch)
                self.assertEqual(structure["evaluated_pairs"], 4)
                self.assertEqual([p["branch"] for p in structure["natal_branches_checked"]],
                                 NATAL_BRANCHES)
                expected = [
                    (pillar, r["kind"], r["branches"])
                    for pillar, natal in zip(("year", "month", "day", "hour"), NATAL_BRANCHES)
                    for r in reviewed_branch_pair_relations(branch, natal)
                ]
                actual = [
                    (hit["natal_pillar"], hit["relation_type"], hit["branches"])
                    for hit in structure["hits"]
                ]
                self.assertEqual(actual, expected)
                self.assertEqual(sum(structure["counts"].values()), len(actual))
                self.assertEqual(set(structure["counts"]), set(RELATION_IDS))
                self.assertEqual(set(structure["rule_ids"]), set(RELATION_IDS.values()))
                self.assertFalse(structure["interpretation_allowed"])
                self.assertTrue(set(structure["evidence_ids"]) <= set(item["evidence"]))
                for hit in structure["hits"]:
                    self.assertEqual(hit["rule_id"], RELATION_IDS[hit["relation_type"]])
                    self.assertTrue(hit["evidence_ids"])
                    self.assertTrue(set(hit["evidence_ids"]) <= set(item["evidence"]))
                rule = next(x for x in item["rule_matches"]
                            if x["rule_id"] == "bazi.scenario.daily_branch_relations")
                self.assertTrue(rule["matched"])
                self.assertEqual(rule["facts"]["counts"], structure["counts"])
                self.assertEqual(rule["evidence_ids"], structure["evidence_ids"])
                self.assertFalse(item["public_release"])

    def test_weekly_is_exact_daily_aggregation_without_new_predictions(self):
        out = scenario_engine.execute_scenario("weekly", {
            "birth_value": BIRTH,
            "anchor_date": "2026-10-04",
        })
        self.assertEqual(out["result"]["week"]["start_date"], "2026-09-28")
        self.assertEqual(out["result"]["week"]["end_date"], "2026-10-04")
        days = out["result"]["week"]["days"]
        self.assertEqual(len(days), 7)
        for day in days:
            current = daily(day["date"])
            self.assertEqual(day["branch_interactions"],
                             current["result"]["day_branch_interactions"])
            self.assertTrue(set(day["branch_interactions"]["evidence_ids"])
                            <= set(out["evidence"]))
        summary = out["result"]["summary"]
        for kind in RELATION_IDS:
            self.assertEqual(summary["branch_relation_counts"][kind],
                             sum(d["branch_interactions"]["counts"][kind] for d in days))
        self.assertEqual([item["date"] for item in summary["branch_relation_dates"]],
                         [day["date"] for day in days if day["branch_interactions"]["hits"]])
        self.assertEqual(len(out["rule_matches"]), 2)
        self.assertNotIn("fortune_score", str(out["result"]))

    def test_monthly_exact_calendar_days_and_cited_date_hits(self):
        out = scenario_engine.execute_scenario("monthly", {
            "birth_value": BIRTH, "target_month": "2026-10",
        })
        self.assertEqual(out["result"]["month"]["day_count"], 31)
        days = out["result"]["month"]["days"]
        self.assertEqual(len(days), 31)
        self.assertEqual(days[0]["date"], "2026-10-01")
        self.assertEqual(days[-1]["date"], "2026-10-31")
        summary = out["result"]["summary"]
        self.assertEqual(set(summary["branch_relation_counts"]), set(RELATION_IDS))
        self.assertEqual(sum(summary["branch_relation_counts"].values()),
                         sum(len(day["branch_interactions"]["hits"]) for day in days))
        self.assertEqual([x["date"] for x in summary["branch_relation_dates"]],
                         [d["date"] for d in days if d["branch_interactions"]["hits"]])
        for row in summary["branch_relation_dates"]:
            for relation in row["relations"]:
                self.assertEqual(relation["rule_id"], RELATION_IDS[relation["relation_type"]])
                self.assertTrue(set(relation["evidence_ids"]) <= set(out["evidence"]))
        match = next(x for x in out["rule_matches"]
                     if x["rule_id"] == "bazi.scenario.monthly_branch_relations")
        self.assertEqual(match["facts"]["branch_relation_counts"],
                         summary["branch_relation_counts"])
        self.assertTrue(set(match["evidence_ids"]) <= set(out["evidence"]))
        self.assertFalse(out["public_release"])

    def test_public_http_daily_returns_reviewed_relations_without_fortune_advice(self):
        with TestClient(create_app()) as client:
            result = client.post("/api/v1/scenarios/public", json={
                "scenario_id": "daily",
                "input": {"birth_value": BIRTH, "target_date": "2026-10-04"},
            })
        self.assertEqual(result.status_code, 200, result.text)
        payload = result.json()
        rows = payload["result"]["day_branch_interactions"]
        self.assertEqual(rows["evaluated_pairs"], 4)
        self.assertTrue(rows["evidence_ids"])
        self.assertTrue(set(rows["evidence_ids"]) <= set(payload["evidence"]))
        self.assertFalse(rows["interpretation_allowed"])
        for forbidden in ("wealth_score", "fortune_score", "marriage_prediction"):
            self.assertNotIn(forbidden, str(rows))

    def test_missing_reviewed_branch_evidence_fails_closed_for_all_three_windows(self):
        real_execute = scenario_engine.execute

        def missing_clash(domain, inputs):
            output = real_execute(domain, inputs)
            if domain == "bazi":
                for rule in output["rule_matches"]:
                    if rule["rule_id"] == "bazi.phase2.branch_six_clashes":
                        rule["evidence_ids"] = []
            return output

        with patch.object(scenario_engine, "execute", side_effect=missing_clash):
            for scenario, args in (
                ("daily", {"target_date": "2026-10-04"}),
                ("weekly", {"anchor_date": "2026-10-04"}),
                ("monthly", {"target_month": "2026-10"}),
            ):
                with self.subTest(scenario=scenario):
                    with self.assertRaisesRegex(ValueError, "evidence is missing"):
                        scenario_engine.execute_scenario(scenario, {
                            "birth_value": BIRTH, **args,
                        })


if __name__ == "__main__":
    unittest.main()
