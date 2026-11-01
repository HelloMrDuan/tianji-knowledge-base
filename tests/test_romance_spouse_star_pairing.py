"""TJ-022.2 配偶星候选位置 × 流年干支结构配对（E0360 实现，E0359 审定）。

Golden 用例全部由真实出生时刻经基线机器（透镜 + 已审地支关系表 +
历法）独立推导、再以标准六合/六冲/六害表与十神规则手工复核后冻结；
断言为精确值，不是包含断言。role 缺席时配对块、规则匹配与 trace 步
整体缺席（E0）；role 在场差异恰入审定封闭五项清单（机上组装树
逐封套深等价比对为批次证据，本文件钉在场形态与 fail-closed）。
"""
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb import scenario_engine

BLOCK_LIMITATIONS = (
    "只观察配偶星候选位置与目标流年干支的同一性与已审六合、六害、六冲；"
    "无命中不代表配偶星缺失或婚恋缺失，不判断婚期、正缘、吉凶、合化或旺衰喜忌。")
BASELINE_PALACE_LINE = (
    "夫妻宫仅以日支位置配对已审六合、六冲、六害；三合、刑、破、合化效力、"
    "配偶星、旺衰喜忌、大运和紫微等未组合裁定。")
PAIRED_PALACE_LINE = (
    "夫妻宫仅以日支位置配对已审六合、六冲、六害；配偶星仅以候选位置与"
    "流年干支作同一性及已审六合、六冲、六害配对；三合、刑、破、合化效力、"
    "旺衰喜忌、大运和紫微等未组合裁定。")
MATCH_ID = "bazi.scenario.spouse_star_year_pairing"
STEP = "reviewed_spouse_star_target_year_pairing"
LENS_ID = "bazi.phase2.spouse_star_lens"

# (birth, year, role) golden inputs, hand-derived in the E0360 record.
CASE_A = ("1988-01-07T12:00:00+08:00", 2026, "male")    # G1 same_branch
CASE_H = ("1988-02-15T18:00:00+08:00", 2029, "male")    # G1 multi-row order
CASE_B = ("1988-10-20T00:00:00+08:00", 2029, "female")  # G2 hidden harmony
CASE_C = ("1988-02-15T00:00:00+08:00", 2025, "female")  # G2 hidden harm
CASE_D = ("1988-02-15T00:00:00+08:00", 2028, "female")  # G2 hidden clash
CASE_E = ("1988-01-07T00:00:00+08:00", 2027, "female")  # G3 same_stem
CASE_F = ("1988-12-25T00:00:00+08:00", 2026, "female")  # G4 no candidates
CASE_G = ("1988-01-07T00:00:00+08:00", 2026, "female")  # G5 no pair hits
ALL_CASES = [CASE_A, CASE_H, CASE_B, CASE_C, CASE_D, CASE_E, CASE_F, CASE_G]


def run(birth, year, role=None):
    payload = {"birth_value": birth, "target_year": year}
    if role is not None:
        payload["traditional_role"] = role
    return scenario_engine.execute_scenario("romance", payload)


def block_of(envelope):
    return envelope["result"]["spouse_star_year_pairing"]


class SpouseStarPairingGoldenTests(unittest.TestCase):
    def test_g1_male_visible_same_branch_exact(self):
        env = run(*CASE_A)
        self.assertEqual([p["ganzhi"] for p in env["result"]["natal"]["pillars"]],
                         ["丁卯", "癸丑", "辛酉", "甲午"])
        block = block_of(env)
        self.assertEqual(block["scope"],
                         "reviewed_spouse_star_positions_and_year_pairs")
        self.assertEqual(block["role_basis"], "user_selected_traditional_lens")
        self.assertEqual(block["traditional_role"], "male")
        self.assertEqual(block["candidate_ten_gods"], ["正财", "偏财"])
        self.assertEqual(block["candidate_positions"]["visible"],
                         [{"pillar": "hour", "stem": "甲", "ten_god": "正财"}])
        self.assertEqual(block["candidate_positions"]["hidden"],
                         [{"pillar": "year", "branch": "卯", "stem": "乙",
                           "ten_god": "偏财"}])
        self.assertEqual(block["target_year"],
                         {"year": 2026, "ganzhi": "丙午", "stem": "丙", "branch": "午"})
        self.assertEqual(block["pairs_checked"], 2)
        self.assertEqual(block["pairings"], [{
            "position_kind": "visible", "pillar": "hour", "branch": "午",
            "stem": "甲", "ten_god": "正财", "relation": "same_branch",
            "rule_id": None, "evidence_ids": block["pairings"][0]["evidence_ids"]}])
        self.assertEqual(block["pairings"][0]["evidence_ids"], block["evidence_ids"])
        self.assertEqual(block["pairing_state"], "paired")
        self.assertEqual(block["reviewed_rule_ids"], [LENS_ID])
        self.assertFalse(block["interpretation_allowed"])
        self.assertEqual(block["limitations"], BLOCK_LIMITATIONS)
        self.assertTrue(set(block["evidence_ids"]) <= set(env["evidence"]))
        match = next(m for m in env["rule_matches"] if m["rule_id"] == MATCH_ID)
        self.assertTrue(match["matched"])
        self.assertEqual(match["derived_from_rule_ids"], block["reviewed_rule_ids"])
        self.assertEqual(match["variant"], "ziping-structural-v1")
        self.assertEqual(match["kind"], "scenario_composition")
        self.assertEqual(set(match["facts"]), {"traditional_role", "pairs_checked", "pairings"})
        self.assertEqual(match["facts"]["pairings"], block["pairings"])
        self.assertEqual(set(match["evidence_ids"]), set(block["evidence_ids"]))
        self.assertIn(STEP, [s["step"] for s in env["trace"]])
        self.assertIn(PAIRED_PALACE_LINE, env["limitations"])

    def test_g1_multi_position_ordering_and_reviewed_rules(self):
        env = run(*CASE_H)
        block = block_of(env)
        self.assertEqual(block["pairs_checked"], 4)
        self.assertEqual(
            [(r["position_kind"], r["pillar"], r["relation"]) for r in block["pairings"]],
            [("visible", "hour", "same_branch"), ("hidden", "year", "six_harmony")])
        self.assertEqual(block["pairings"][0]["stem"], "乙")
        self.assertEqual(block["pairings"][0]["ten_god"], "正财")
        self.assertIsNone(block["pairings"][0]["rule_id"])
        self.assertEqual(block["pairings"][1]["branch"], "辰")
        self.assertEqual(block["pairings"][1]["rule_id"],
                         "bazi.phase2.branch_six_harmonies")
        self.assertEqual(block["reviewed_rule_ids"],
                         [LENS_ID, "bazi.phase2.branch_six_harmonies"])

    def test_g2_hidden_positions_harmony_harm_clash(self):
        expectations = [
            (CASE_B, "six_harmony", "bazi.phase2.branch_six_harmonies",
             ("year", "辰", "乙", "正官"), 1),
            (CASE_C, "harm", "bazi.phase2.branch_six_harms",
             ("month", "寅", "丙", "七杀"), 2),
            (CASE_D, "clash", "bazi.phase2.branch_six_clashes",
             ("month", "寅", "丙", "七杀"), 2),
        ]
        for case, relation, rule_id, where, checked in expectations:
            with self.subTest(relation=relation):
                env = run(*case)
                block = block_of(env)
                self.assertEqual(block["pairs_checked"], checked)
                self.assertEqual(len(block["pairings"]), 1)
                row = block["pairings"][0]
                self.assertEqual(row["position_kind"], "hidden")
                self.assertEqual(
                    (row["pillar"], row["branch"], row["stem"], row["ten_god"]),
                    where)
                self.assertEqual(row["relation"], relation)
                self.assertEqual(row["rule_id"], rule_id)
                self.assertTrue(row["evidence_ids"])
                self.assertTrue(set(row["evidence_ids"]) <= set(env["evidence"]))
                self.assertEqual(block["reviewed_rule_ids"], [LENS_ID, rule_id])
                self.assertEqual(block["pairing_state"], "paired")

    def test_g3_visible_same_stem_exact(self):
        env = run(*CASE_E)
        block = block_of(env)
        self.assertEqual(block["candidate_positions"]["visible"],
                         [{"pillar": "year", "stem": "丁", "ten_god": "七杀"}])
        self.assertEqual(block["candidate_positions"]["hidden"], [])
        self.assertEqual(block["pairs_checked"], 1)
        self.assertEqual(len(block["pairings"]), 1)
        row = block["pairings"][0]
        self.assertEqual(
            (row["position_kind"], row["pillar"], row["branch"], row["stem"],
             row["ten_god"], row["relation"], row["rule_id"]),
            ("visible", "year", "卯", "丁", "七杀", "same_stem", None))
        self.assertEqual(row["evidence_ids"], block["evidence_ids"])

    def test_g4_zero_candidates_block_present_but_empty(self):
        env = run(*CASE_F)
        self.assertEqual([p["ganzhi"] for p in env["result"]["natal"]["pillars"]],
                         ["戊辰", "甲子", "甲寅", "甲子"])
        block = block_of(env)
        self.assertEqual(block["candidate_ten_gods"], ["正官", "七杀"])
        self.assertEqual(block["candidate_positions"], {"visible": [], "hidden": []})
        self.assertEqual(block["pairs_checked"], 0)
        self.assertEqual(block["pairings"], [])
        self.assertEqual(block["pairing_state"], "no_candidates")
        self.assertEqual(block["limitations"], BLOCK_LIMITATIONS)
        match = next(m for m in env["rule_matches"] if m["rule_id"] == MATCH_ID)
        self.assertEqual(match["facts"]["pairs_checked"], 0)
        self.assertIn(STEP, [s["step"] for s in env["trace"]])

    def test_g5_candidates_without_any_pair_hit(self):
        env = run(*CASE_G)
        block = block_of(env)
        self.assertEqual(block["pairs_checked"], 1)
        self.assertEqual(block["pairings"], [])
        self.assertEqual(block["pairing_state"], "no_pair_hits")
        self.assertEqual(block["reviewed_rule_ids"], [LENS_ID])

    def test_g6_role_absent_block_match_and_step_all_absent(self):
        for birth, year, _role in ALL_CASES:
            with self.subTest(birth=birth, year=year):
                env = run(birth, year)
                self.assertNotIn("spouse_star_year_pairing", env["result"])
                self.assertNotIn(MATCH_ID,
                                 [m["rule_id"] for m in env["rule_matches"]])
                self.assertNotIn(STEP, [s["step"] for s in env["trace"]])
                self.assertIn(BASELINE_PALACE_LINE, env["limitations"])
                self.assertNotIn(PAIRED_PALACE_LINE, env["limitations"])
        # The pre-existing spouse-palace block keeps its exact shape.
        env = run("2000-01-07T12:00:00+08:00", 2026)
        palace = env["result"]["spouse_palace_year_relations"]
        self.assertEqual((palace["natal_day_branch"], palace["target_year_branch"]),
                         ("子", "午"))
        self.assertEqual([r["relation_type"] for r in palace["relations"]], ["clash"])

    def test_g7_no_forbidden_keys_scores_or_verdicts(self):
        forbidden = ('"fortune_score"', '"marriage_date"',
                     '"compatibility_percent"', '"conflict_score"',
                     '"auspicious"', '"relationship_advice"', '"breakup_risk"',
                     '"score"', '"percent"')
        for case in (CASE_A, CASE_H, CASE_B):
            with self.subTest(case=case):
                env = run(*case)
                block = block_of(env)
                blob = json.dumps(block, ensure_ascii=False)
                for token in forbidden:
                    self.assertNotIn(token, blob)
                self.assertFalse(block["interpretation_allowed"])
                for row in block["pairings"]:
                    self.assertIn(row["relation"],
                                  {"same_branch", "same_stem", "six_harmony",
                                   "harm", "clash"})
                self.assertEqual(set(block), {
                    "scope", "role_basis", "traditional_role",
                    "candidate_ten_gods", "candidate_positions", "target_year",
                    "pairs_checked", "pairings", "pairing_state",
                    "reviewed_rule_ids", "evidence_ids",
                    "interpretation_allowed", "limitations"})

    def test_g8_invalid_role_unknown_key_and_tampered_evidence_fail_closed(self):
        birth, year, _ = CASE_A
        for bad in ("unknown", 1, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run(birth, year, bad)
        with self.assertRaises(ValueError):
            scenario_engine.execute_scenario("romance", {
                "birth_value": birth, "target_year": year,
                "traditional_role": "male", "spouse_note": "x"})
        real_execute = scenario_engine.execute

        def strip_lens_evidence(domain, inputs):
            envelope = real_execute(domain, inputs)
            for match in envelope["rule_matches"]:
                if match["rule_id"] == LENS_ID:
                    match["evidence_ids"] = []
            return envelope

        with patch.object(scenario_engine, "execute", strip_lens_evidence):
            with self.assertRaises(ValueError):
                run(birth, year, "male")


def _strip_evidence(value):
    if isinstance(value, dict):
        return {k: _strip_evidence(v) for k, v in value.items()
                if k != "evidence_ids"}
    if isinstance(value, list):
        return [_strip_evidence(v) for v in value]
    return value


class SpouseStarPairingApiTests(unittest.TestCase):
    def test_g9_real_api_matches_engine_with_and_without_role(self):
        # The public projection aliases evidence ids platform-wide
        # (the standing API contract, identical for the spouse-palace
        # block), so parity is asserted verbatim on every field except
        # evidence_ids, whose counts must match and whose values must
        # resolve inside the API envelope's own evidence map.
        client = TestClient(create_app())
        birth, year, role = CASE_A
        with_role = client.post("/api/v1/scenarios/public", json={
            "scenario_id": "romance",
            "input": {"birth_value": birth, "target_year": year,
                      "traditional_role": role},
        })
        self.assertEqual(with_role.status_code, 200, with_role.text)
        api_env = with_role.json()
        engine_env = run(birth, year, role)
        api_block = api_env["result"]["spouse_star_year_pairing"]
        engine_block = engine_env["result"]["spouse_star_year_pairing"]
        self.assertEqual(_strip_evidence(api_block), _strip_evidence(engine_block))
        self.assertEqual(len(api_block["evidence_ids"]),
                         len(engine_block["evidence_ids"]))
        self.assertTrue(set(api_block["evidence_ids"]) <= set(api_env["evidence"]))
        for api_row, engine_row in zip(api_block["pairings"],
                                       engine_block["pairings"]):
            self.assertEqual(len(api_row["evidence_ids"]),
                             len(engine_row["evidence_ids"]))
        self.assertEqual(api_env["status"], engine_env["status"])
        without_role = client.post("/api/v1/scenarios/public", json={
            "scenario_id": "romance",
            "input": {"birth_value": birth, "target_year": year},
        })
        self.assertEqual(without_role.status_code, 200, without_role.text)
        self.assertNotIn("spouse_star_year_pairing",
                         without_role.json()["result"])

    def test_g10_life_envelope_has_no_pairing_and_rejects_role(self):
        birth, year, _ = CASE_A
        env = scenario_engine.execute_scenario(
            "life", {"birth_value": birth, "target_year": year})
        self.assertNotIn("spouse_star_year_pairing",
                         json.dumps(env, ensure_ascii=False))
        with self.assertRaises(ValueError):
            scenario_engine.execute_scenario("life", {
                "birth_value": birth, "target_year": year,
                "traditional_role": "male"})


if __name__ == "__main__":
    unittest.main()
