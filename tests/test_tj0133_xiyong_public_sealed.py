"""TJ-013.3 分阶段开放第一阶段（实现批 E0372）：密封伴随专项。

在组装后的真实后端（真实知识包 + 生产 runtime）上验证：九个
Golden 盘的真实场景执行与公开 Golden 期望逐项对平；呈现证据与同
请求 trace/rule_matches/evidence 的绑定对平（审定 §6.2）；Phase1
引用索引对注册包的恰等（10 规则 120 对 / r040 4 对）；bazi-profile
与未开门基线的封闭清单等价比对；其他场景零改动；客户端研究键在
真实域路径仍被拒；真实 API 响应与场景层逐字对平（G11）；构建失
败即场景请求失败的处置钉（§3.3，治理记录 §12 明示）。本文件只在
离线验收的组装树内运行，不进公开 CI。
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from tianji_kb import scenario_engine
from tianji_kb.api import create_app
from tianji_kb.bazi_conflict_presentation import (
    VARIANT as CONFLICT_VARIANT,
)
from tianji_kb.bazi_xiyong_public import (
    BINGYAO_STEP_ID,
    TIAOHOU_STEP_ID,
    is_valid_public_presentation,
    public_xiyong_presentation,
)
from tianji_kb.bazi_xiyong_readable import VARIANT as READABLE_VARIANT
from tianji_kb.engine import execute as domain_execute
from tianji_kb.public_projection import project_execution
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.scenario_engine import _xiyong_phase1_refs, execute_scenario

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0133_xiyong_public.json").read_text(
        encoding="utf-8"))
RAW_KEYS = ("tiaohou_assessment", "bingyao_assessment", "readable_hints",
            "conflict_presentation")


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


def _real_view(raw):
    return {
        "trace": raw["trace"],
        "rule_matches": raw["rule_matches"],
        "evidence": raw["evidence"],
        "phase1_rule_refs": _xiyong_phase1_refs(),
    }


class RealGoldenExecutionTests(unittest.TestCase):
    def test_real_scenario_executions_match_golden(self):
        for case in GOLDEN["cases"]:
            with self.subTest(case=case["id"]):
                envelope = execute_scenario("bazi-profile", {
                    "value": case["birth"], "zone": case["zone"]})
                result = envelope["result"]
                presentation = result["xiyong_presentation"]
                expected = case["expected"]
                self.assertTrue(
                    is_valid_public_presentation(presentation))
                self.assertEqual(
                    presentation["blocks"]["tiaohou"]["lines"],
                    expected["tiaohou_lines"])
                self.assertEqual(
                    presentation["blocks"]["bingyao"]["lines"],
                    expected["bingyao_lines"])
                self.assertEqual(presentation["relations"],
                                 expected["relations"])
                if expected["tiaohou_state"] == "presented":
                    self.assertEqual(
                        presentation["blocks"]["tiaohou"]
                        ["evidence"]["phase1_rule_id"],
                        expected["tiaohou_phase1_rule_id"])
                    self.assertEqual(
                        presentation["blocks"]["tiaohou"]
                        ["evidence"]["section_id"],
                        expected["entry_section_id"])
                # The presentation is exactly what the builder derives
                # from this same envelope's statements and records.
                rebuilt = public_xiyong_presentation(
                    result["tiaohou_assessment"],
                    result["bingyao_assessment"],
                    execution=_real_view(envelope))
                self.assertEqual(presentation, rebuilt)
                # §6.2: every presented quote resolves to a record of
                # this envelope bound by the corresponding step.
                steps = {step["rule_id"]: step
                         for step in envelope["trace"]}
                tiaohou_ids = set(
                    steps[TIAOHOU_STEP_ID]["evidence_ids"])
                bingyao_ids = set(
                    steps[BINGYAO_STEP_ID]["evidence_ids"])
                if expected["tiaohou_state"] == "presented":
                    evidence = presentation["blocks"]["tiaohou"]["evidence"]
                    hits = [eid for eid in tiaohou_ids
                            if envelope["evidence"][eid]
                            ["original_text"] == evidence["quote"]
                            and envelope["evidence"][eid]
                            ["section_id"] == evidence["section_id"]]
                    self.assertEqual(len(hits), 1)
                for quote_info in (presentation["blocks"]["bingyao"]
                                   ["evidence"]["quotes"]):
                    hits = [eid for eid in bingyao_ids
                            if envelope["evidence"][eid]
                            ["original_text"] == quote_info["quote"]
                            and envelope["evidence"][eid]
                            ["section_id"] == quote_info["section_id"]]
                    self.assertEqual(len(hits), 1)
                # Public projection of the real envelope: verbatim
                # presentation, no raw research objects.
                projected = project_execution(copy.deepcopy(envelope))
                self.assertEqual(
                    projected["result"]["xiyong_presentation"],
                    presentation)
                for key in RAW_KEYS:
                    self.assertNotIn(key, projected["result"])


class BundleReferenceIndexTests(unittest.TestCase):
    def test_refs_index_matches_registered_bundle(self):
        refs = _xiyong_phase1_refs()
        self.assertEqual(set(refs), {TIAOHOU_STEP_ID, BINGYAO_STEP_ID})
        tiaohou_refs = refs[TIAOHOU_STEP_ID]
        self.assertEqual(set(tiaohou_refs),
                         {f"bazi.rule.r{index:03d}"
                          for index in range(42, 52)})
        self.assertEqual(
            sum(len(pairs) for pairs in tiaohou_refs.values()), 120)
        bingyao_refs = refs[BINGYAO_STEP_ID]
        self.assertEqual(set(bingyao_refs), {"bazi.rule.r040"})
        self.assertEqual(len(bingyao_refs["bazi.rule.r040"]), 4)
        self.assertTrue(all(
            section == "bazi.section.s071"
            for section, _ in bingyao_refs["bazi.rule.r040"]))
        # Cross-check the index against an independent resolver read.
        resolver = EvidenceResolver()
        for step_id in (TIAOHOU_STEP_ID, BINGYAO_STEP_ID):
            contract = resolver.rule(step_id)
            self.assertEqual(set(refs[step_id]),
                             set(contract["phase1_rule_refs"]))
            for rule_id, pairs in refs[step_id].items():
                self.assertEqual(
                    pairs,
                    [(ref["section_id"], ref["original_text"])
                     for ref in resolver.rule(rule_id)["source_refs"]])


class EquivalenceTests(unittest.TestCase):
    """§9 #4: the gate adds exactly the closed difference list."""

    INPUTS = (
        {"value": "1960-03-07T01:30:00+08:00", "zone": "Asia/Shanghai"},
        {"value": "2000-01-07T12:00:00+08:00"},
        {"value": "1950-06-08T05:00:00+08:00", "zone": "Asia/Shanghai",
         "strength_variant": "ditiansui-root-visibility-v1"},
        {"value": "1949-01-01T01:00:00+08:00", "zone": "Asia/Shanghai"},
    )

    def test_envelope_differences_are_exactly_the_closed_list(self):
        for inputs in self.INPUTS:
            with self.subTest(inputs=inputs):
                gated = execute_scenario("bazi-profile", inputs)
                base = domain_execute("bazi", inputs)
                result = dict(gated["result"])
                presentation = result.pop("xiyong_presentation")
                self.assertTrue(
                    is_valid_public_presentation(presentation))
                tiaohou = result.pop("tiaohou_assessment")
                bingyao = result.pop("bingyao_assessment")
                self.assertEqual(result, base["result"])
                extra_steps = [step for step in gated["trace"]
                               if step["rule_id"] in
                               (TIAOHOU_STEP_ID, BINGYAO_STEP_ID)]
                self.assertEqual(
                    [step for step in gated["trace"]
                     if step["rule_id"] not in
                     (TIAOHOU_STEP_ID, BINGYAO_STEP_ID)],
                    base["trace"])
                self.assertEqual(
                    {step["rule_id"]: step["output"]
                     for step in extra_steps},
                    {TIAOHOU_STEP_ID: tiaohou, BINGYAO_STEP_ID: bingyao})
                self.assertEqual(
                    [match for match in gated["rule_matches"]
                     if match["rule_id"] not in
                     (TIAOHOU_STEP_ID, BINGYAO_STEP_ID)],
                    base["rule_matches"])
                extra_matches = [match for match in gated["rule_matches"]
                                 if match["rule_id"] in
                                 (TIAOHOU_STEP_ID, BINGYAO_STEP_ID)]
                self.assertEqual(len(extra_matches), 2)
                self.assertTrue(all(match["matched"] is True
                                    for match in extra_matches))
                for evidence_id, record in base["evidence"].items():
                    self.assertEqual(
                        gated["evidence"][evidence_id], record)
                extra_ids = (set(gated["evidence"])
                             - set(base["evidence"]))
                bound = set()
                for step in extra_steps:
                    bound |= set(step["evidence_ids"])
                self.assertTrue(extra_ids <= bound)
                self.assertTrue(bound <= set(gated["evidence"]))


class OtherScenariosUnchangedTests(unittest.TestCase):
    SAMPLES = {
        "daily": {"birth_value": "2000-01-07T12:00:00+08:00",
                  "target_date": "2026-10-04"},
        "weekly": {"birth_value": "2000-01-07T12:00:00+08:00",
                   "anchor_date": "2026-10-04"},
        "monthly": {"birth_value": "2000-01-07T12:00:00+08:00",
                    "target_month": "2026-10"},
        "yearly": {"birth_value": "2000-01-07T12:00:00+08:00",
                   "target_year": 2026},
        "romance": {"birth_value": "2000-01-07T12:00:00+08:00",
                    "target_year": 2026},
        "career": {"birth_value": "2000-01-07T12:00:00+08:00",
                   "target_year": 2026},
        "life": {"birth_value": "2000-01-07T12:00:00+08:00",
                 "target_year": 2026},
        "question": {"value": "2000-01-07T12:00:00+08:00",
                     "yao_values": [9, 7, 7, 7, 7, 7]},
        "compatibility": {
            "person_a_birth_value": "2000-01-07T12:00:00+08:00",
            "person_b_birth_value": "2000-02-01T12:00:00+08:00"},
    }

    def test_no_presentation_or_raw_statements_anywhere(self):
        for scenario_id, inputs in self.SAMPLES.items():
            with self.subTest(scenario=scenario_id):
                envelope = execute_scenario(scenario_id, inputs)
                keys = set(_all_keys(envelope))
                self.assertNotIn("xiyong_presentation", keys)
                self.assertNotIn("tiaohou_assessment", keys)
                self.assertNotIn("bingyao_assessment", keys)
                projected = project_execution(copy.deepcopy(envelope))
                projected_keys = set(_all_keys(projected))
                self.assertNotIn("xiyong_presentation", projected_keys)
                for key in RAW_KEYS:
                    self.assertNotIn(key, projected_keys)


class ClientGateRealPathTests(unittest.TestCase):
    def test_domain_research_keys_still_refused_without_research_mode(self):
        value = "1960-03-07T01:30:00+08:00"
        for key, variant, message in (
            ("tiaohou_variant", "tiaohou-qiongtong-v1",
             "Tiaohou entry statements require explicit research mode"),
            ("bingyao_variant", "bingyao-shenfeng-v1",
             "Bingyao structural candidates require explicit research mode"),
            ("conflict_variant", CONFLICT_VARIANT,
             "Cross-system conflict presentation requires explicit "
             "research mode"),
            ("readable_variant", READABLE_VARIANT,
             "Xiyong readable hints require explicit research mode"),
        ):
            with self.assertRaises(ValueError) as caught:
                domain_execute("bazi", {"value": value, key: variant})
            self.assertEqual(str(caught.exception), message)


class ApiAlignmentTests(unittest.TestCase):
    """G11 / §6.2 third check: the public API response is the
    scenario layer's presentation, verbatim."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(admin_read_token='<redacted>'))

    def test_public_scenario_api_matches_scenario_layer(self):
        birth = "1960-03-07T01:30:00+08:00"
        response = self.client.post("/api/v1/scenarios/public", json={
            "scenario_id": "bazi-profile",
            "input": {"value": birth, "zone": "Asia/Shanghai"}})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        expected = execute_scenario("bazi-profile", {
            "value": birth, "zone": "Asia/Shanghai"})
        self.assertEqual(body["result"]["xiyong_presentation"],
                         expected["result"]["xiyong_presentation"])
        for key in RAW_KEYS:
            self.assertNotIn(key, body["result"])
        # Rule matches and trace stay aligned with the scenario layer.
        self.assertEqual(len(body["rule_matches"]),
                         len(expected["rule_matches"]))
        self.assertEqual(len(body["trace"]), len(expected["trace"]))

    def test_public_domain_api_still_refuses_research_keys(self):
        response = self.client.post("/api/v1/public/execute", json={
            "domain": "bazi",
            "input": {"value": "1960-03-07T01:30:00+08:00",
                      "tiaohou_variant": "tiaohou-qiongtong-v1"}})
        self.assertEqual(response.status_code, 422)
        self.assertIn("require explicit research mode", response.text)

    def test_public_scenario_api_refuses_client_research_keys(self):
        response = self.client.post("/api/v1/scenarios/public", json={
            "scenario_id": "bazi-profile",
            "input": {"value": "1960-03-07T01:30:00+08:00",
                      "tiaohou_variant": "tiaohou-qiongtong-v1"}})
        self.assertEqual(response.status_code, 422)


class FailureDispositionTests(unittest.TestCase):
    """§3.3 disposition (recorded in the governance record): a
    presentation that cannot be built fails the scenario request."""

    def test_builder_failure_fails_the_scenario_request(self):
        with mock.patch.object(
                scenario_engine, "public_xiyong_presentation",
                side_effect=ValueError("forged execution view")):
            with self.assertRaises(ValueError):
                execute_scenario("bazi-profile", {
                    "value": "1960-03-07T01:30:00+08:00",
                    "zone": "Asia/Shanghai"})


if __name__ == "__main__":
    unittest.main()
