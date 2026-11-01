"""TJ-017.3 分阶段开放第二阶段（实现批 E0375）：密封伴随专项。

在组装后的真实后端（真实知识包 + 生产 runtime）上验证：注册
Golden 命例（G1–G5 + 神峰零日形）的真实组合链 → 视图 → 构建器
呈现与本批 Golden 逐项对平；role 缺席深等价语料（G6）；真实
API 响应与场景层逐字对平（G9）；其余场景零泄漏与人生总览大运
维文案/旗标逐字不变（G10）；两方法 natal/direction 逐字相等
（G11）。本文件只在离线验收的组装树内运行，不进公开 CI。
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from tianji_kb.api import create_app
from tianji_kb.bazi_dayun_public import (
    is_valid_public_dayun_presentation,
)
from tianji_kb.scenario_engine import _dayun_public_gate, execute_scenario

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0173_dayun_public.json").read_text(
        encoding="utf-8"))
CASES = {case["id"]: case for case in GOLDEN["cases"]}

RESEARCH_KEYS = {
    "dayun_timeline_view", "dayun_timeline_views",
    "dayun_classical_direction", "dayun_sanming_conversion",
    "dayun_shenfeng_conversion", "classical_dayun_timeline",
    "dayun_presentation", "sequence_time_alignment",
    "sanming_conversion", "parallel_variants",
}
LIFE_LIMITATION = (
    "八字旺衰、喜用、格局与大运真实起运仍未获得生产审核，"
    "报告不得给出这些结论。")


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


def _flag_values(value, key):
    if isinstance(value, dict):
        for name, item in value.items():
            if name == key:
                yield item
            yield from _flag_values(item, key)
    elif isinstance(value, list):
        for item in value:
            yield from _flag_values(item, key)


class RealChainGoldenTests(unittest.TestCase):
    """G1–G5 + 神峰零日形：真实链呈现对平本批 Golden。"""

    def _check_case(self, case):
        presentation = _dayun_public_gate(
            case["birth"], case["zone"], case["role"])
        self.assertTrue(
            is_valid_public_dayun_presentation(presentation))
        self.assertEqual(presentation["status"], case["status"])
        self.assertEqual(presentation["role"]["traditional_role"],
                         case["role"])
        for method in ("sanming", "shenfeng"):
            view = presentation["methods"][method]
            self.assertEqual(view["natal"]["pillars"], case["pillars"])
            self.assertEqual(view["direction"]["value"],
                             case["direction"]["value"])
            self.assertEqual(view["direction"]["label"],
                             case["direction"]["label"])
            self.assertEqual(view["direction"]["counting_target"],
                             case["direction"]["counting_target"])
            self.assertEqual(view["direction"]["counted_jie"],
                             case["direction"]["counted_jie"])
            self.assertEqual([n["code"] for n in view["notices"]],
                             case[method]["notice_codes"])
        sanming = presentation["methods"]["sanming"]
        shenfeng = presentation["methods"]["shenfeng"]
        # G11: the two method blocks carry identical natal/direction.
        self.assertEqual(sanming["natal"], shenfeng["natal"])
        self.assertEqual(sanming["direction"], shenfeng["direction"])
        expected_sanming = case["sanming"]
        if expected_sanming.get("status") == "unresolved":
            self.assertEqual(sanming["status"], "unresolved")
            self.assertEqual(sanming["reason"],
                             expected_sanming["reason"])
            # §5: the duration block is present in unresolved form.
            self.assertEqual(sanming["duration"], {
                "method": "sanming_shichen_level",
                "variant": "dayun-conversion-sanming-v1",
                "status": "unresolved", "interval_days": None,
                "decomposition": None, "counting": None,
                "approximate": False, "rounding_applied": False,
                "rounding_policy":
                    "refused_classical_text_prohibits_rounding",
                "reason": expected_sanming["reason"]})
            for entry, pair in zip(
                    sanming["entries"],
                    expected_sanming["entries_ganzhi"]):
                self.assertEqual(entry["ganzhi"], pair[0])
                self.assertEqual(
                    entry["ten_god_relative_to_natal_day_stem"],
                    pair[1])
                self.assertEqual(entry["state"], "unresolved")
                self.assertIsNone(entry["start_interval"])
        else:
            self.assertEqual(sanming["status"], "converted")
            duration = sanming["duration"]
            self.assertEqual(duration["interval_days"],
                             expected_sanming["interval_days"])
            self.assertEqual(duration["decomposition"],
                             expected_sanming["decomposition"])
            self.assertEqual(duration["counting"],
                             expected_sanming["counting"])
            self.assertEqual(duration["rounding_applied"], False)
            self.assertEqual(duration["approximate"], False)
            self.assertEqual(len(sanming["entries"]), 8)
            for entry, expected in zip(sanming["entries"],
                                       expected_sanming["entries"]):
                self.assertEqual(entry["ganzhi"], expected[0])
                self.assertEqual(
                    entry["ten_god_relative_to_natal_day_stem"],
                    expected[1])
                self.assertEqual(entry["state"], "interval")
                self.assertEqual(entry["start_interval"]["earliest"],
                                 expected[2])
                self.assertEqual(entry["start_interval"]["latest"],
                                 expected[3])
                self.assertEqual(
                    entry["start_interval"]["max_inclusive"], False)
        expected_shenfeng = case["shenfeng"]
        if expected_shenfeng.get("status") == "unresolved":
            self.assertEqual(shenfeng["status"], "unresolved")
            self.assertEqual(shenfeng["reason"],
                             expected_shenfeng["reason"])
            self.assertEqual(shenfeng["duration"], {
                "method": "shenfeng_day_level",
                "variant": "dayun-conversion-shenfeng-v1",
                "status": "unresolved", "interval_days": None,
                "text_result_days": None,
                "counting": {"whole_days": None,
                             "counting_target": None},
                "granularity_note": None, "approximate": False,
                "reason": expected_shenfeng["reason"]})
            for entry in shenfeng["entries"]:
                self.assertEqual(entry["state"], "unresolved")
                self.assertIsNone(entry["start_interval"])
        else:
            self.assertEqual(shenfeng["status"], "converted")
            duration = shenfeng["duration"]
            self.assertEqual(duration["interval_days"],
                             expected_shenfeng["interval_days"])
            self.assertEqual(duration["text_result_days"],
                             expected_shenfeng["text_result_days"])
            self.assertEqual(duration["counting"]["whole_days"],
                             expected_shenfeng["whole_days"])
            self.assertEqual(duration["approximate"], False)
            first = shenfeng["entries"][0]
            self.assertEqual(first["state"], "interval")
            self.assertEqual(first["start_interval"]["earliest"],
                             expected_shenfeng["first_interval"]
                             ["earliest"])
            self.assertEqual(first["start_interval"]["latest"],
                             expected_shenfeng["first_interval"]
                             ["latest"])
            self.assertEqual(
                first["start_interval"]["derivation"],
                "composition_level_birth_plus_shenfeng_duration_"
                "interval")
            for entry in shenfeng["entries"][1:]:
                self.assertEqual(entry["state"], "not_provided")
                self.assertIsNone(entry["start_interval"])
        quote_ids = {
            method: [q["id"] for block in
                     presentation["methods"][method]["sources"]
                     for q in block["quotes"]]
            for method in ("sanming", "shenfeng")}
        if case["status"] == "unresolved":
            self.assertEqual(quote_ids["sanming"],
                             ["direction_rule",
                              "vol11_direction_witness"])
        else:
            self.assertEqual(quote_ids["sanming"],
                             ["direction_rule",
                              "vol11_direction_witness",
                              "handover_decade"])
        self.assertEqual(quote_ids["shenfeng"],
                         ["sf_ex1", "sf_ex3", "sf_ex4"])
        self.assertEqual(
            presentation["evidence"]["composition_chain"],
            ["dayun-direction-classical-v1",
             "bazi-dayun-adjacent-jie-research-v1",
             "dayun-conversion-sanming-v1",
             "bazi-dayun-month-sequence-research-v1"])
        self.assertEqual(
            [rule["phase1_rule_id"] for rule in
             presentation["evidence"]["rules"]],
            ["bazi.rule.r038", "bazi.rule.r039", "bazi.rule.r041"])

    def test_g1_q1(self):
        self._check_case(CASES["G1-Q1-forward-male-1958"])

    def test_g2_q2(self):
        self._check_case(CASES["G2-Q2-backward-female-1949"])

    def test_g3_q3(self):
        self._check_case(CASES["G3-Q3-forward-female-1959"])

    def test_g3_q4_same_chart_opposite_role(self):
        # Same chart, opposite role: direction reverses and the
        # duration changes — the role genuinely drives the chain.
        q3 = _dayun_public_gate("1959-06-15T10:30:00+08:00",
                                "Asia/Shanghai", "female")
        q4 = _dayun_public_gate("1959-06-15T10:30:00+08:00",
                                "Asia/Shanghai", "male")
        self.assertEqual(
            q3["methods"]["sanming"]["direction"]["value"], "forward")
        self.assertEqual(
            q4["methods"]["sanming"]["direction"]["value"], "backward")
        self._check_case(CASES["G3-Q4-backward-male-1959"])

    def test_g5_zero_jie(self):
        self._check_case(CASES["G5-ADV001-zero-jie-2000"])

    def test_shenfeng_zero_day(self):
        self._check_case(CASES["S1-shenfeng-zero-day-1958"])


class RoleAbsentEquivalenceTests(unittest.TestCase):
    """G6: role 缺席时信封与无呈现路径逐字深等价（语料 8 例）。"""

    def test_corpus(self):
        for item in GOLDEN["equivalence_corpus"]:
            with self.subTest(birth=item["birth"]):
                baseline = execute_scenario("bazi-profile", {
                    "value": item["birth"], "zone": item["zone"],
                    "strength_variant":
                        "ditiansui-root-visibility-v1"})
                self.assertNotIn("dayun_presentation",
                                 baseline["result"])
                for role in ("male", "female"):
                    with_role = execute_scenario("bazi-profile", {
                        "value": item["birth"], "zone": item["zone"],
                        "strength_variant":
                            "ditiansui-root-visibility-v1",
                        "traditional_role": role})
                    presentation = with_role["result"].pop(
                        "dayun_presentation")
                    self.assertTrue(
                        is_valid_public_dayun_presentation(
                            presentation))
                    self.assertEqual(with_role, baseline)


class ApiAlignmentTests(unittest.TestCase):
    """G9: 真实 API 响应中的呈现与场景层逐字对平。"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(admin_read_token="x" * 32))

    def _post(self, payload):
        response = self.client.post("/api/v1/scenarios/public",
                                    json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_api_matches_scenario_layer(self):
        for case_id in ("G1-Q1-forward-male-1958",
                        "G5-ADV001-zero-jie-2000"):
            case = CASES[case_id]
            scenario = execute_scenario("bazi-profile", {
                "value": case["birth"], "zone": case["zone"],
                "traditional_role": case["role"]})
            api = self._post({
                "scenario_id": "bazi-profile",
                "input": {"value": case["birth"], "zone": case["zone"],
                          "traditional_role": case["role"]}})
            # G9: the released presentation is verbatim the scenario
            # layer's object; the rest of the API envelope follows
            # the phase-1 alignment level (rule_matches/trace aligned
            # with the scenario layer, raw research objects absent).
            self.assertEqual(api["result"]["dayun_presentation"],
                             scenario["result"]["dayun_presentation"])
            self.assertEqual(len(api["rule_matches"]),
                             len(scenario["rule_matches"]))
            self.assertEqual(len(api["trace"]),
                             len(scenario["trace"]))
            self.assertFalse(
                set(_all_keys(api)) & (RESEARCH_KEYS
                                       - {"dayun_presentation"}))

    def test_api_role_absent_has_no_presentation(self):
        api = self._post({
            "scenario_id": "bazi-profile",
            "input": {"value": "1958-08-15T19:30:00+08:00",
                      "zone": "Asia/Shanghai"}})
        self.assertNotIn("dayun_presentation", api["result"])
        self.assertFalse(set(_all_keys(api)) & RESEARCH_KEYS)


class OtherScenariosTests(unittest.TestCase):
    """G10: 四场景零泄漏 + 人生总览大运维文案与旗标逐字不变。"""

    BIRTH = "1958-08-15T19:30:00+08:00"

    def _assert_clean(self, envelope):
        keys = set(_all_keys(envelope))
        self.assertFalse(keys & RESEARCH_KEYS, keys & RESEARCH_KEYS)
        flags = list(_flag_values(envelope, "dayun_timeline_approved"))
        self.assertTrue(all(flag is False for flag in flags), flags)

    def test_contract_bound_scenarios_reject_role(self):
        for scenario_id, inputs in (
            ("yearly", {"birth_value": self.BIRTH, "target_year": 2026,
                        "traditional_role": "male"}),
            ("career", {"birth_value": self.BIRTH, "target_year": 2026,
                        "traditional_role": "male"}),
            ("life", {"birth_value": self.BIRTH, "target_year": 2026,
                      "traditional_role": "male"}),
        ):
            with self.assertRaises(ValueError, msg=scenario_id):
                execute_scenario(scenario_id, inputs)

    def test_role_owning_scenarios_stay_clean(self):
        # romance/compatibility own an adjudicated traditional_role
        # for other faces; the dayun presentation must not leak in.
        for scenario_id, inputs in (
            ("romance", {"birth_value": self.BIRTH, "target_year": 2026,
                         "traditional_role": "male"}),
            ("compatibility", {
                "person_a_birth_value": self.BIRTH,
                "person_b_birth_value": "1959-06-15T10:30:00+08:00",
                "person_a_traditional_role": "male",
                "person_b_traditional_role": "female"}),
        ):
            envelope = execute_scenario(scenario_id, inputs)
            self._assert_clean(envelope)

    def test_four_scenarios_without_role_stay_clean(self):
        envelopes = {
            "yearly": execute_scenario("yearly", {
                "birth_value": self.BIRTH, "target_year": 2026}),
            "romance": execute_scenario("romance", {
                "birth_value": self.BIRTH, "target_year": 2026}),
            "career": execute_scenario("career", {
                "birth_value": self.BIRTH, "target_year": 2026}),
            "life": execute_scenario("life", {
                "birth_value": self.BIRTH, "target_year": 2026}),
        }
        for scenario_id, envelope in envelopes.items():
            with self.subTest(scenario=scenario_id):
                self._assert_clean(envelope)
        life = envelopes["life"]
        self.assertIn(LIFE_LIMITATION, life["limitations"])
        flags = list(_flag_values(life, "dayun_timeline_approved"))
        self.assertTrue(flags)
        self.assertTrue(all(flag is False for flag in flags))


if __name__ == "__main__":
    unittest.main()
