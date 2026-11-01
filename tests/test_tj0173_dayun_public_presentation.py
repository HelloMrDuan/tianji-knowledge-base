"""TJ-017.3 分阶段开放第二阶段（实现批 E0375）：公开专项测试。

构建器以**合成组合结果**为执行记录：组合字典按注册形态手工构造，
字段值取自注册 Golden（golden_tj0174_dayun_compose.json /
golden_tj0173_dayun_timeline_view.json），方向块为真实
``classical_direction`` 纯函数输出（引文逐字真实）；两方法视图由
真实 ``dayun_timeline_view`` 自合成组合派生。合成组合是密封组合
链的测试替身：真实出生时刻的完整组合、场景信封与 API 对平由密
封专项 test_tj0173_dayun_public_sealed.py 在离线验收中钉住，本
文件不冒称真实组合执行。篡改类、投影定域与内容禁入在本文件以
合成视图与合成信封实测；前端源码断言带存在性守卫（组装树无
web/ 时跳过该段，沿 E0359/E0362 先例）。
"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    SHENFENG_CONVERSION_VARIANT,
    _quote_ref,
    classical_direction,
)
from tianji_kb.bazi_dayun_compose import COMPOSE_VARIANT
from tianji_kb.bazi_dayun_public import (
    LIMITATIONS,
    RULES,
    SCOPE,
    VARIANT,
    is_valid_public_dayun_presentation,
    public_dayun_presentation,
)
from tianji_kb.bazi_dayun_sequence import VARIANT as SEQUENCE_VARIANT
from tianji_kb.bazi_dayun_timeline_view import dayun_timeline_view
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import execute_scenario

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0173_dayun_public.json").read_text(
        encoding="utf-8"))
CASES = {case["id"]: case for case in GOLDEN["cases"]}

FLAGS = {"research_only": True, "public_enabled": False,
         "ai_enabled": False,
         "evidence_binding": "inherited_registered_phase1_phase2"}
CLASSICAL_FLAGS = {"research_only": True, "public_enabled": False,
                   "ai_enabled": False,
                   "evidence_binding": "registered_phase1_phase2"}
MEASUREMENT_VARIANT = "bazi-dayun-adjacent-jie-research-v1"
REMAINDER_HANDLING = (
    "interval_upper_bound_only_not_proportionally_converted")
DECOMPOSITION_DOCTRINE = (
    "surplus_or_deficit_against_whole_year_units_carries_linearly_"
    "at_10_days_per_shichen_never_discarded_never_rounded")
GRANULARITY_NOTE = (
    "日级计数截断亚日余数：真实历时在 [whole_days, whole_days+1) 日内，"
    "区间据此给出；本法无时级余数 doctrine。")


def _rows(ganzhi_gods, intervals=None, unresolved_status=None):
    rows = []
    alignment = []
    for index, (ganzhi, god) in enumerate(ganzhi_gods, start=1):
        base = {"period_index": index, "candidate_ganzhi": ganzhi,
                "stem": ganzhi[0], "branch": ganzhi[1],
                "ten_god_relative_to_natal_day_stem": god}
        rows.append({**base, "start_date": None, "end_date": None,
                     "start_age": None, "end_age": None,
                     "natal_interaction": None, "luck_assessment": None})
        entry = dict(base)
        if intervals is not None:
            earliest, latest = intervals[index - 1]
            basis = ("birth_plus_start_duration_interval" if index == 1
                     else f"start_duration_interval_plus_"
                          f"{index - 1}_calendar_decades")
            entry["start_interval"] = {
                "earliest": earliest, "latest": latest,
                "max_inclusive": False, "basis": basis,
                "method": "sanming_shichen_level",
                "variant": CONVERSION_VARIANT}
        else:
            entry["start_interval"] = None
            entry["start_interval_status"] = unresolved_status
        alignment.append(entry)
    return rows, alignment


def _composition(case):
    """Synthetic composition in the registered shape for one case."""
    pillars = case["pillars"]
    direction = classical_direction(pillars["year"],
                                    traditional_role=case["role"])
    counted = case["direction"]["counted_jie"]
    birth = case["birth"]
    if case["status"] == "unresolved":
        conversion = {
            "variant": CONVERSION_VARIANT, "status": "unresolved",
            "method": "sanming_shichen_level",
            "direction": case["direction"]["value"],
            "counting_target": case["direction"]["counting_target"],
            "counted_jie": counted, "birth_instant": birth,
            "jie_selection_scope": "counting target is a Jie (节)",
            "consumer_conventions": {}, "limitations": [],
            **CLASSICAL_FLAGS,
            "reason": case["sanming"]["reason"],
            "duration_interval_days": None, "handover_intervals": None,
        }
        rows, alignment = _rows(
            [tuple(pair) for pair in case["sanming"]["entries_ganzhi"]],
            unresolved_status="unresolved: " + case["sanming"]["reason"])
        shenfeng = {
            "variant": SHENFENG_CONVERSION_VARIANT,
            "status": "unresolved", "method": "shenfeng_day_level",
            "input": {"whole_days": 0,
                      "direction": case["direction"]["value"]},
            "counting_target": case["direction"]["counting_target"],
            "text_result_days": None, "duration_interval_days": None,
            "granularity_note": None, "parallel_note": "分立。",
            "reason": case["shenfeng"]["reason"],
        }
        counting = {
            "measurement_variant": MEASUREMENT_VARIANT,
            "calendar_provider": "provider",
            "selected_jie": counted, "previous_jie": counted,
            "next_jie": counted, "elapsed_seconds": 0,
            "elapsed_whole_days": 0,
            "remaining_seconds_after_whole_days": 0,
            "zero_distance": True}
        status = "unresolved"
    else:
        sanming = case["sanming"]
        intervals = [(row[2], row[3]) for row in sanming["entries"]]
        ganzhi_gods = [(row[0], row[1]) for row in sanming["entries"]]
        rows, alignment = _rows(ganzhi_gods, intervals=intervals)
        handovers = [{
            "period_index": index, "earliest": earliest,
            "latest": latest, "max_inclusive": False,
            "basis": alignment[index - 1]["start_interval"]["basis"]}
            for index, (earliest, latest) in enumerate(intervals, 1)]
        conversion = {
            "variant": CONVERSION_VARIANT, "status": "converted",
            "method": "sanming_shichen_level",
            "direction": case["direction"]["value"],
            "counting_target": case["direction"]["counting_target"],
            "counted_jie": counted, "birth_instant": birth,
            "jie_selection_scope": "counting target is a Jie (节)",
            "consumer_conventions": {}, "limitations": [],
            **CLASSICAL_FLAGS,
            "duration_interval_days": sanming["interval_days"],
            "duration_decomposition": {
                **sanming["decomposition"],
                "remainder_doctrine": DECOMPOSITION_DOCTRINE},
            "counting": {
                **sanming["counting"],
                "sub_shichen_remainder_handling": REMAINDER_HANDLING},
            "rounding_applied": False, "approximate": False,
            "handover_intervals": handovers,
            "handover_basis_quote": _quote_ref("handover_decade"),
        }
        shenfeng_case = case["shenfeng"]
        if shenfeng_case.get("status") == "unresolved":
            shenfeng = {
                "variant": SHENFENG_CONVERSION_VARIANT,
                "status": "unresolved", "method": "shenfeng_day_level",
                "input": {"whole_days": 0,
                          "direction": case["direction"]["value"]},
                "counting_target": case["direction"]["counting_target"],
                "text_result_days": None,
                "duration_interval_days": None,
                "granularity_note": None, "parallel_note": "分立。",
                "reason": shenfeng_case["reason"],
            }
        else:
            first = shenfeng_case["first_interval"]
            shenfeng = {
                "variant": SHENFENG_CONVERSION_VARIANT,
                "status": "converted", "method": "shenfeng_day_level",
                "input": {"whole_days": shenfeng_case["whole_days"],
                          "direction": case["direction"]["value"]},
                "counting_target": case["direction"]["counting_target"],
                "text_result_days": shenfeng_case["text_result_days"],
                "duration_interval_days": shenfeng_case["interval_days"],
                "granularity_note": GRANULARITY_NOTE,
                "parallel_note": "分立。",
                "first_period_start_interval": {
                    "earliest": first["earliest"],
                    "latest": first["latest"],
                    "max_inclusive": first["max_inclusive"],
                    "derivation": ("composition_level_birth_plus_"
                                   "shenfeng_duration_interval"),
                    "decade_shifts": ("not_provided_for_shenfeng_at_"
                                      "composition_level")},
            }
        counting = {
            "measurement_variant": MEASUREMENT_VARIANT,
            "calendar_provider": "provider",
            "selected_jie": counted, "previous_jie": counted,
            "next_jie": counted, "elapsed_seconds": 1,
            "elapsed_whole_days": shenfeng_case.get("whole_days", 0),
            "remaining_seconds_after_whole_days": 0,
            "zero_distance": False}
        status = "converted"
    composition = {
        "variant": COMPOSE_VARIANT, "status": status,
        "composition_chain": [
            DIRECTION_VARIANT, MEASUREMENT_VARIANT, CONVERSION_VARIANT,
            SEQUENCE_VARIANT],
        "birth": {"input_value": birth, "zone": case["zone"],
                  "local_datetime": birth},
        "pillars": {"year_ganzhi": pillars["year"],
                    "month_ganzhi": pillars["month"],
                    "day_ganzhi": pillars["day"],
                    "hour_ganzhi": pillars["hour"],
                    "day_master": pillars["day_master"]},
        "traditional_role": case["role"],
        "traditional_role_selection":
            "explicit_historical_category_not_inferred_identity",
        "direction": direction,
        "counting": counting,
        "sanming_conversion": conversion,
        "sequence": {"variant": SEQUENCE_VARIANT,
                     "source_month_ganzhi": pillars["month"],
                     "natal_day_master": pillars["day_master"],
                     "direction": case["direction"]["value"],
                     "rows": rows},
        "sequence_time_alignment": alignment,
        "alignment_method": "sanming_shichen_level",
        "parallel_variants": {"shenfeng_day_level": shenfeng},
        "limitations": [],
        **FLAGS,
    }
    if status != "converted":
        composition["reason"] = case["sanming"]["reason"]
    return composition


def _build(case):
    composition = _composition(case)
    return public_dayun_presentation(
        dayun_timeline_view(composition, method="sanming"),
        dayun_timeline_view(composition, method="shenfeng"),
        execution={"composition": composition})


def _strings(value):
    """System-composed strings only: verbatim registered quotes and
    the pinned §4.4 constants are exempt (quotes are pinned verbatim
    against the composition instead; the constants are the one
    registered negation context)."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("quotes", "rule_quote", "scope", "limitations"):
                continue
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield value


def _keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _keys(item)


class GoldenFormTests(unittest.TestCase):
    def test_g1_full_sanming_form(self):
        case = CASES["G1-Q1-forward-male-1958"]
        presentation = _build(case)
        self.assertTrue(is_valid_public_dayun_presentation(presentation))
        self.assertEqual(presentation["variant"], VARIANT)
        self.assertEqual(presentation["status"], "presented")
        self.assertEqual(presentation["role"], {
            "traditional_role": "male",
            "selection":
                "explicit_historical_category_not_inferred_identity"})
        self.assertEqual(presentation["scope"], list(SCOPE))
        self.assertEqual(presentation["limitations"], list(LIMITATIONS))
        self.assertEqual(presentation["evidence"]["rules"],
                         [dict(rule) for rule in RULES])
        self.assertEqual(
            presentation["evidence"]["sequence_disclosure"],
            {"variant": "bazi-dayun-month-sequence-research-v1",
             "ten_god_rule_id": "bazi.phase2.ten_gods"})
        sanming = presentation["methods"]["sanming"]
        self.assertEqual(sanming["direction"]["value"], "forward")
        self.assertEqual(sanming["direction"]["label"], "顺行")
        self.assertEqual(sanming["duration"]["interval_days"],
                         {"min_days": 2840, "max_days": 2850,
                          "max_inclusive": False})
        self.assertEqual(
            [entry["ganzhi"] for entry in sanming["entries"]],
            [row[0] for row in case["sanming"]["entries"]])
        for entry, expected in zip(sanming["entries"],
                                   case["sanming"]["entries"]):
            self.assertEqual(entry["state"], "interval")
            self.assertEqual(entry["start_interval"]["earliest"],
                             expected[2])
            self.assertEqual(entry["start_interval"]["latest"],
                             expected[3])
            self.assertEqual(
                entry["ten_god_relative_to_natal_day_stem"], expected[1])
        self.assertEqual([n["code"] for n in sanming["notices"]],
                         case["sanming"]["notice_codes"])
        quote_ids = [q["id"] for block in sanming["sources"]
                     for q in block["quotes"]]
        self.assertEqual(quote_ids, ["direction_rule",
                                     "vol11_direction_witness",
                                     "handover_decade"])
        # Natal projection carries pillars only — no birth echo.
        self.assertEqual(set(sanming["natal"]), {"pillars"})

    def test_g4_shenfeng_form(self):
        case = CASES["G1-Q1-forward-male-1958"]
        presentation = _build(case)
        shenfeng = presentation["methods"]["shenfeng"]
        self.assertEqual(shenfeng["status"], "converted")
        self.assertEqual(shenfeng["duration"]["interval_days"],
                         {"min_days": 2760, "max_days": 2880,
                          "max_inclusive": False})
        self.assertEqual(shenfeng["duration"]["text_result_days"], 2760)
        first = shenfeng["entries"][0]
        self.assertEqual(first["state"], "interval")
        self.assertEqual(first["start_interval"]["earliest"],
                         "1966-03-06T19:30:00+08:00")
        self.assertEqual(first["start_interval"]["latest"],
                         "1966-07-04T19:30:00+08:00")
        self.assertEqual(
            first["start_interval"]["derivation"],
            "composition_level_birth_plus_shenfeng_duration_interval")
        for entry in shenfeng["entries"][1:]:
            self.assertEqual(entry["state"], "not_provided")
            self.assertIsNone(entry["start_interval"])
        self.assertEqual([n["code"] for n in shenfeng["notices"]],
                         case["shenfeng"]["notice_codes"])
        quote_ids = [q["id"] for block in shenfeng["sources"]
                     for q in block["quotes"]]
        self.assertEqual(quote_ids, ["sf_ex1", "sf_ex3", "sf_ex4"])

    def test_g5_zero_jie_unresolved_form(self):
        case = CASES["G5-ADV001-zero-jie-2000"]
        presentation = _build(case)
        self.assertEqual(presentation["status"], "unresolved")
        sanming = presentation["methods"]["sanming"]
        self.assertEqual(sanming["status"], "unresolved")
        self.assertEqual(sanming["reason"],
                         "zero_jie_boundary_convention_unreviewed")
        # The direction block is still presented in the empty state.
        self.assertEqual(sanming["direction"]["value"], "backward")
        for entry in sanming["entries"]:
            self.assertEqual(entry["state"], "unresolved")
            self.assertIsNone(entry["start_interval"])
        shenfeng = presentation["methods"]["shenfeng"]
        self.assertEqual(shenfeng["status"], "unresolved")
        self.assertEqual(shenfeng["reason"],
                         "zero_day_count_not_exemplified_in_text")
        self.assertEqual([n["code"] for n in shenfeng["notices"]],
                         case["shenfeng"]["notice_codes"])

    def test_shenfeng_zero_day_form(self):
        # §5 second form: Sanming converts, Shenfeng alone unresolved;
        # the two method states are independent.
        case = CASES["S1-shenfeng-zero-day-1958"]
        presentation = _build(case)
        self.assertEqual(presentation["status"], "presented")
        self.assertEqual(presentation["methods"]["sanming"]["status"],
                         "converted")
        shenfeng = presentation["methods"]["shenfeng"]
        self.assertEqual(shenfeng["status"], "unresolved")
        self.assertEqual(shenfeng["reason"],
                         "zero_day_count_not_exemplified_in_text")
        self.assertIn("shenfeng_zero_day_count",
                      [n["code"] for n in shenfeng["notices"]])

    def test_g11_method_switch_consistency(self):
        for case in CASES.values():
            composition = _composition(case)
            sanming = dayun_timeline_view(composition, method="sanming")
            shenfeng = dayun_timeline_view(composition,
                                          method="shenfeng")
            for key in ("natal", "direction", "counting"):
                self.assertEqual(sanming[key], shenfeng[key], case["id"])
            presentation = _build(case)
            self.assertEqual(
                presentation["methods"]["sanming"]["direction"],
                presentation["methods"]["shenfeng"]["direction"])
            self.assertEqual(
                presentation["methods"]["sanming"]["natal"],
                presentation["methods"]["shenfeng"]["natal"])

    def test_deterministic_rebuild(self):
        for case in CASES.values():
            self.assertEqual(_build(case), _build(case), case["id"])


class BannedContentTests(unittest.TestCase):
    BANNED = ("效力", "运势", "吉凶", "旺衰", "喜用", "扶抑", "格局",
              "岁数", "年龄", "预测", "婚期", "灾祸", "评分", "百分比",
              "应期", "流年")

    def test_g7_no_banned_content_anywhere(self):
        for case in CASES.values():
            presentation = _build(case)
            for text in _strings(presentation):
                for banned in self.BANNED:
                    self.assertNotIn(banned, text, (case["id"], text))
            for key in _keys(presentation):
                self.assertNotIn("age", key, (case["id"], key))
                self.assertNotIn(key, ("start_date", "end_date",
                                       "start_age", "end_age"))

    def test_g7_no_research_object_keys(self):
        forbidden = {
            "dayun_timeline_view", "dayun_timeline_views",
            "dayun_classical_direction", "dayun_sanming_conversion",
            "dayun_shenfeng_conversion", "classical_dayun_timeline",
            "sequence_time_alignment", "sanming_conversion",
            "parallel_variants", "research_only",
        }
        for case in CASES.values():
            keys = set(_keys(_build(case)))
            self.assertFalse(keys & forbidden, (case["id"], keys))


class TamperTests(unittest.TestCase):
    """§6.2 / G8: tamper classes against the G1 synthetic records."""

    def setUp(self):
        self.case = CASES["G1-Q1-forward-male-1958"]
        self.composition = _composition(self.case)

    def _views(self, composition):
        return (dayun_timeline_view(composition, method="sanming"),
                dayun_timeline_view(composition, method="shenfeng"))

    def test_interval_endpoint_altered(self):
        composition = copy.deepcopy(self.composition)
        composition["sequence_time_alignment"][0][
            "start_interval"]["earliest"] = "1966-05-26T19:30:00+08:00"
        sanming, shenfeng = self._views(composition)
        with self.assertRaises(ValueError):
            public_dayun_presentation(
                sanming, shenfeng, execution={"composition":
                                              self.composition})

    def test_governance_flag_flipped(self):
        composition = copy.deepcopy(self.composition)
        composition["public_enabled"] = True
        with self.assertRaises(ValueError):
            public_dayun_presentation(
                *self._views(self.composition),
                execution={"composition": composition})

    def test_quote_text_altered(self):
        composition = copy.deepcopy(self.composition)
        quote = composition["direction"]["rule_quote"]
        quote["quote"] = quote["quote"][:-1] + "X"
        with self.assertRaises(ValueError):
            public_dayun_presentation(
                *self._views(self.composition),
                execution={"composition": composition})

    def test_cross_method_natal_mismatch(self):
        sanming, shenfeng = self._views(self.composition)
        shenfeng = copy.deepcopy(shenfeng)
        shenfeng["natal"]["pillars"]["day"] = "乙丑"
        with self.assertRaises(ValueError):
            public_dayun_presentation(
                sanming, shenfeng,
                execution={"composition": self.composition})

    def test_shenfeng_decade_shift_fabricated(self):
        composition = copy.deepcopy(self.composition)
        sanming, shenfeng = self._views(composition)
        shenfeng = copy.deepcopy(shenfeng)
        entry = shenfeng["entries"][1]
        entry["state"] = "interval"
        entry["start_interval"] = {
            "earliest": "1976-03-06T19:30:00+08:00",
            "latest": "1976-07-04T19:30:00+08:00",
            "max_inclusive": False,
            "derivation": ("composition_level_birth_plus_shenfeng_"
                           "duration_interval"),
            "decade_shifts": "not_provided_for_shenfeng_at_"
                             "composition_level",
            "method": "shenfeng_day_level",
            "variant": SHENFENG_CONVERSION_VARIANT}
        del entry["start_interval_status"]
        with self.assertRaises(ValueError):
            public_dayun_presentation(
                sanming, shenfeng,
                execution={"composition": composition})


class ProjectionScopeTests(unittest.TestCase):
    """§7 row 3: strip everywhere + scoped release for bazi-profile."""

    def _envelope(self, scenario_id, presentation, container="result"):
        envelope = {
            "scenario_id": scenario_id, "status": "production",
            "result": {}, "evidence": {}, "rule_matches": [],
            "trace": [],
        }
        envelope[container] = {
            "dayun_presentation": presentation,
            "dayun_timeline_view": {"variant": "dayun-timeline-view-v1"},
            "dayun_classical_direction": {"variant": "x"},
            "dayun_sanming_conversion": {"variant": "y"},
            "dayun_shenfeng_conversion": {"variant": "z"},
        }
        return envelope

    def setUp(self):
        self.presentation = _build(CASES["G1-Q1-forward-male-1958"])
        self.assertTrue(
            is_valid_public_dayun_presentation(self.presentation))

    def test_bazi_profile_release_is_verbatim(self):
        projected = project_execution(
            self._envelope("bazi-profile", self.presentation))
        self.assertEqual(projected["result"]["dayun_presentation"],
                         self.presentation)
        for key in ("dayun_timeline_view", "dayun_classical_direction",
                    "dayun_sanming_conversion",
                    "dayun_shenfeng_conversion"):
            self.assertNotIn(key, projected["result"])

    def test_other_scenario_carrier_is_stripped(self):
        projected = project_execution(
            self._envelope("life", self.presentation))
        self.assertNotIn("dayun_presentation", projected["result"])

    def test_domain_chart_carrier_is_stripped(self):
        envelope = self._envelope("bazi-profile", self.presentation,
                                  container="chart")
        del envelope["scenario_id"]
        projected = project_execution(envelope)
        self.assertNotIn("dayun_presentation", projected["chart"])
        self.assertNotIn("dayun_presentation", projected["result"])

    def test_malformed_presentation_is_stripped(self):
        forged = copy.deepcopy(self.presentation)
        forged["methods"]["shenfeng"]["entries"][1]["state"] = "interval"
        projected = project_execution(
            self._envelope("bazi-profile", forged))
        self.assertNotIn("dayun_presentation", projected["result"])


class ClientGateTests(unittest.TestCase):
    """§3.2/§7 rows 1-2: the client contract cannot reach the gate."""

    BIRTH = "1958-08-15T19:30:00+08:00"

    def test_research_keys_rejected_by_contract(self):
        for key in ("dayun_classical_role", "dayun_sanming_measurement",
                    "dayun_shenfeng_measurement",
                    "classical_dayun_timeline", "dayun_timeline_view"):
            with self.assertRaises(ValueError) as caught:
                execute_scenario("bazi-profile",
                                 {"value": self.BIRTH, key: "x"})
            self.assertIn("do not match the reviewed contract",
                          str(caught.exception))

    def test_illegal_role_rejected_before_computation(self):
        for role in ("unknown", "", 1, True):
            with self.assertRaises(ValueError) as caught:
                execute_scenario("bazi-profile",
                                 {"value": self.BIRTH,
                                  "traditional_role": role})
            self.assertIn("traditional_role must be male or female",
                          str(caught.exception))

    def test_other_scenarios_reject_the_role_key(self):
        # The key is scoped to bazi-profile: yearly (like the other
        # scenarios) keeps its exact contract and refuses it. The
        # romance/compatibility scenarios have their own adjudicated
        # role keys and are not probed here.
        with self.assertRaises(ValueError) as caught:
            execute_scenario("yearly", {
                "birth_value": self.BIRTH, "target_year": 2026,
                "traditional_role": "male"})
        self.assertIn("do not match the reviewed contract",
                      str(caught.exception))


class FrontendWiringTests(unittest.TestCase):
    """Guarded source pins for the page wiring (E0359 lesson: the
    assembled acceptance tree has no web/ — skip when absent)."""

    def test_page_consumes_dayun_presentation(self):
        page_path = (ROOT / "web" / "visual-prototype" / "src" / "public"
                     / "BaziProfilePage.tsx")
        api_path = (ROOT / "web" / "visual-prototype" / "src" / "public"
                    / "api.ts")
        if not page_path.exists() or not api_path.exists():
            self.skipTest("web tree not present in this checkout")
        page = page_path.read_text(encoding="utf-8")
        api = api_path.read_text(encoding="utf-8")
        self.assertIn("traditional_role", api)
        self.assertIn("传统大运口径（可选）", page)
        self.assertIn("dayun_presentation", page)
        # The role is sent only when explicitly selected.
        self.assertIn('if (dayunRole) scenarioInput.traditional_role '
                      '= dayunRole;', page)


if __name__ == "__main__":
    unittest.main()
