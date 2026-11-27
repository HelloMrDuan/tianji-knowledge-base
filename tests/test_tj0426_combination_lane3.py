"""TJ-0426 Lane 3：八字原局大运流年 + 司令（D-01～D-05）专项。

范围（只测本 lane 在 bazi_combination_engine.py 内新增的内容）：

- D-01 跨层效力（TJ-017.2 真定义）：效力规则逐条立项——当前无任何
  已审跨层效力规则，故注册表为空；无证据的效力一律 abstain 并具名
  缺口；overall_effect 恒 None。
- D-02 期位映射：调用方显式指定当期运的校验口径；不起运岁数、不算
  交运单点日期；区间口径（TJ-017.1/017.4）不动。
- D-03 流年边界：边界对照完备性（调用方传入
  bazi-annual-lichun-boundary-v1 行，本引擎只作消费侧对照，不推导
  立春交界、不接进组合引擎）。
- D-04 刑与三合组：刑表登记由 Lane 1 先行（S-06）；本 lane 只扩展
  scope 说明，不自造刑评估；跨三层组不产生条件结论（C5 已批）。
- D-05 事业/总览 2–8 运：本次不做呈现扩展；只核对组合引擎 8 运数据
  完整可用（sequence_completeness）。

真实算例：

- f2：2024-02-11T16:27:07+08:00，四柱 甲辰/丙寅/乙巳/甲申（独立
  以 lunar_python 回放核对：年/月/日/时干支逐字一致；立春
  2024-02-04T16:27:07+08:00，2025 立春 2025-02-03T22:10:28+08:00，
  2026 立春 2026-02-04T04:02:08+08:00，均为 provider 节气表回放值，
  本地回放用 lunar-python 1.4.9，仓库钉定 1.4.8——密封对照
  CrossCheckTests 在组装环境以钉定版本复核为准）。
  大运为 candidate_sequence forward 形制（月柱丙寅之后顺排，首运
  排除月柱本身，见 bazi_dayun_sequence.py）：丁卯/戊辰/己巳/庚午/
  辛未/壬申/癸酉/甲戌，十神由 ten_god 规则手算（丁食神、戊正财、
  己偏财、庚正官、辛七杀、壬正印、癸偏印、甲劫财）。
- 算例 A：1958-08-15T19:30:00+08:00，戊戌/庚申/甲子/甲戌（沿用
  test_tj0424_combination_engine.py 的已审 Golden）；大运辛酉/壬戌/
  癸亥；流年 1988（戊辰）。
- 算例 B：1959-06-15T10:30:00+08:00，己亥/庚午/戊辰/丁巳；大运
  辛未/壬申/癸酉；流年 1997（丁丑）用于跨三层组复核。

本文件只依赖标准库与组合引擎本身；公开检出可直接运行。密封对照
（CrossCheckTests）只在组装环境跑，公开检出跳过，不伪造通过。
"""
import unittest

from tianji_kb.bazi_combination_engine import (
    CONDITIONAL_VERDICTS,
    FLOW_BOUNDARY_VARIANT,
    PERIOD_BASIS_KINDS,
    check_flow_year_boundary,
    combine,
    cross_layer_effect_rules,
    dayun_sequence_completeness,
    evaluate_cross_layer_effect,
    punishment_status,
    ten_god_for,
    validate_current_period,
)

# --- 真实算例 ----------------------------------------------------------
F2_PILLARS = ["甲辰", "丙寅", "乙巳", "甲申"]
F2_DAYUN_8 = [
    {"candidate_ganzhi": "丁卯", "period_index": 1, "ten_god": "食神"},
    {"candidate_ganzhi": "戊辰", "period_index": 2, "ten_god": "正财"},
    {"candidate_ganzhi": "己巳", "period_index": 3, "ten_god": "偏财"},
    {"candidate_ganzhi": "庚午", "period_index": 4, "ten_god": "正官"},
    {"candidate_ganzhi": "辛未", "period_index": 5, "ten_god": "七杀"},
    {"candidate_ganzhi": "壬申", "period_index": 6, "ten_god": "正印"},
    {"candidate_ganzhi": "癸酉", "period_index": 7, "ten_god": "偏印"},
    {"candidate_ganzhi": "甲戌", "period_index": 8, "ten_god": "劫财"},
]
CASE_A_PILLARS = ["戊戌", "庚申", "甲子", "甲戌"]
CASE_A_DAYUN = [
    {"candidate_ganzhi": "辛酉", "period_index": 1, "ten_god": "正官"},
    {"candidate_ganzhi": "壬戌", "period_index": 2, "ten_god": "偏印"},
    {"candidate_ganzhi": "癸亥", "period_index": 3, "ten_god": "正印"},
]
CASE_B_PILLARS = ["己亥", "庚午", "戊辰", "丁巳"]
CASE_B_DAYUN = [
    {"candidate_ganzhi": "辛未", "period_index": 1, "ten_god": "伤官"},
    {"candidate_ganzhi": "壬申", "period_index": 2, "ten_god": "偏财"},
    {"candidate_ganzhi": "癸酉", "period_index": 3, "ten_god": "正财"},
]
# Golden Q1 交运区间依据（沿用 test_tj0424_combination_engine.py
# CallerSelectedPeriodTests 的已审引用写法）。
GOLDEN_Q1_BASIS = ("Golden Q1 handover interval period 3 "
                   "[1986-05-25, 1986-06-04)")

# 流年边界行：provider 节气表回放瞬时（2024 立春 16:27:07、2025 立春
# 22:10:28、2026 立春 04:02:08，Asia/Shanghai 秒级）；四边界干支按
# annual_lichun_boundaries 的同一核对式（at_start/before_end=当年，
# before_start=上年，at_end=下年）取值，十神由 ten_god 规则手算。
BOUNDARY_2024 = {
    "variant": "bazi-annual-lichun-boundary-v1",
    "day_master": "乙",
    "rows": [{
        "gregorian_lichun_year": 2024,
        "start_inclusive": "2024-02-04T16:27:07+08:00",
        "end_exclusive": "2025-02-03T22:10:28+08:00",
        "ganzhi_in_interval": "甲辰",
        "year_stem": "甲",
        "year_branch": "辰",
        "ten_god_relative_to_natal_day_stem": "劫财",
        "ganzhi_one_second_before_start": "癸卯",
        "ganzhi_at_start": "甲辰",
        "ganzhi_one_second_before_end": "甲辰",
        "ganzhi_at_end": "乙巳",
    }],
}
BOUNDARY_2025 = {
    "variant": "bazi-annual-lichun-boundary-v1",
    "day_master": "乙",
    "rows": [{
        "gregorian_lichun_year": 2025,
        "start_inclusive": "2025-02-03T22:10:28+08:00",
        "end_exclusive": "2026-02-04T04:02:08+08:00",
        "ganzhi_in_interval": "乙巳",
        "year_stem": "乙",
        "year_branch": "巳",
        "ten_god_relative_to_natal_day_stem": "比肩",
        "ganzhi_one_second_before_start": "甲辰",
        "ganzhi_at_start": "乙巳",
        "ganzhi_one_second_before_end": "乙巳",
        "ganzhi_at_end": "丙午",
    }],
}


def _combine_f2(target_year, **overrides):
    return combine(F2_PILLARS, "乙", F2_DAYUN_8, target_year, **overrides)


class D01CrossLayerEfficacyTests(unittest.TestCase):
    """D-01：无已审跨层效力规则时，注册表为空、效力一律 abstain。"""

    def test_registry_is_empty_by_design(self):
        registry = cross_layer_effect_rules()
        self.assertEqual(registry["rules_registered"], [])
        self.assertEqual(registry["rules_count"], 0)
        self.assertIsNone(registry["overall_effect"])
        self.assertEqual(registry["status"], "no_reviewed_rules")
        # 候选效力问题逐条具名缺口，不是不记缺口。
        self.assertTrue(registry["candidate_gaps"])
        for gap in registry["candidate_gaps"]:
            self.assertIn("gap", gap)
            self.assertIn("TJ-017.2", gap["gap"])

    def test_every_candidate_efficacy_question_abstains(self):
        registry = cross_layer_effect_rules()
        for gap in registry["candidate_gaps"]:
            with self.subTest(rule=gap["rule_id"]):
                result = evaluate_cross_layer_effect(gap["rule_id"])
                self.assertIsNone(result["verdict"])
                self.assertEqual(result["status"], "abstain")
                self.assertEqual(result["gap"], gap["gap"])
                self.assertIn("TJ-017.2", result["reason"])

    def test_unregistered_rule_abstains_not_invented(self):
        result = evaluate_cross_layer_effect("not_a_registered_rule")
        self.assertIsNone(result["verdict"])
        self.assertEqual(result["status"], "abstain")
        self.assertEqual(result["gap"], "TJ-017.2-unregistered_rule")

    def test_combine_carries_efficacy_block_and_overall_stays_none(self):
        output = _combine_f2(2024)
        efficacy = output["effects"]["cross_layer_efficacy"]
        self.assertIsNone(output["effects"]["overall_effect"])
        self.assertIsNone(efficacy["overall_effect"])
        self.assertEqual(efficacy["rules_registered"], [])
        self.assertEqual(efficacy["status"], "no_reviewed_rules")
        # 8 种条件结论逐条登记为“存在性事实，不是效力断言”。
        self.assertEqual(
            {row["verdict"] for row in efficacy["conditional_verdicts"]},
            set(CONDITIONAL_VERDICTS))
        for row in efficacy["conditional_verdicts"]:
            self.assertFalse(row["treated_as_efficacy"])
        # 本例无任何条件结论输入：全部关系 abstain。
        self.assertTrue(output["effects"]["all_abstained"])
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": output["relation_summary"]["total"]})


class D02PeriodMappingTests(unittest.TestCase):
    """D-02：当期运须调用方显式指定并校验；不起运岁数、不算单点日期。"""

    def test_basis_kinds_are_closed(self):
        self.assertEqual(set(PERIOD_BASIS_KINDS), {
            "dayun_compose_interval", "golden_reference",
            "caller_attested"})

    def test_unspecified_period_is_not_determined(self):
        result = validate_current_period(None, CASE_A_DAYUN, None)
        self.assertEqual(result["status"], "not_determined")
        self.assertIsNone(result["period_index"])
        self.assertFalse(result["start_age_computed"])
        self.assertFalse(result["handover_single_date_computed"])

    def test_specified_period_with_interval_basis(self):
        result = validate_current_period(
            3, CASE_A_DAYUN, GOLDEN_Q1_BASIS,
            basis_kind="dayun_compose_interval")
        self.assertEqual(result["status"], "caller_selected")
        self.assertEqual(result["period_index"], 3)
        self.assertEqual(result["basis_kind"], "dayun_compose_interval")
        self.assertFalse(result["start_age_computed"])
        self.assertFalse(result["handover_single_date_computed"])

    def test_interval_basis_must_carry_an_interval(self):
        # dayun_compose_interval 口径的依据必须带区间；只有文字、无
        # 区间的依据拒收（不把一句话当成交运区间）。
        with self.assertRaises(ValueError):
            validate_current_period(
                3, CASE_A_DAYUN, "third period per Golden Q1",
                basis_kind="dayun_compose_interval")

    def test_period_validation_is_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_current_period(9, CASE_A_DAYUN, "x")
        with self.assertRaises(ValueError):
            validate_current_period(3, CASE_A_DAYUN, None)
        with self.assertRaises(ValueError):
            validate_current_period(None, CASE_A_DAYUN, "x")
        with self.assertRaises(ValueError):
            validate_current_period(
                3, CASE_A_DAYUN, "x", basis_kind="single_date")
        with self.assertRaises(ValueError):
            validate_current_period(
                3, [{"candidate_ganzhi": "辛酉", "period_index": 1},
                    {"candidate_ganzhi": "壬戌", "period_index": 1}],
                "x")

    def test_combine_records_per_period_mapping_detail(self):
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                         current_period_index=3,
                         current_period_basis=GOLDEN_Q1_BASIS,
                         current_period_basis_kind="golden_reference")
        detail = output["dayun"]["period_year_mapping_detail"]
        self.assertEqual(detail["status"], "caller_selected")
        self.assertEqual(detail["basis_kind"], "golden_reference")
        self.assertFalse(detail["start_age_computed"])
        self.assertFalse(detail["handover_single_date_computed"])
        self.assertEqual(detail["per_period"], [
            {"period_index": 1, "mapping": "other"},
            {"period_index": 2, "mapping": "other"},
            {"period_index": 3, "mapping": "current"},
        ])
        # 未指定时逐运皆 undetermined，仍不指定当期。
        plain = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988)
        detail = plain["dayun"]["period_year_mapping_detail"]
        self.assertEqual(detail["status"], "not_determined")
        self.assertTrue(all(row["mapping"] == "undetermined"
                            for row in detail["per_period"]))

    def test_basis_kind_mismatch_is_rejected_by_combine(self):
        with self.assertRaises(ValueError):
            combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988,
                    current_period_index=3,
                    current_period_basis=GOLDEN_Q1_BASIS,
                    current_period_basis_kind="single_date")


class D03FlowBoundaryTests(unittest.TestCase):
    """D-03：流年边界只作消费侧对照，不推导立春交界。"""

    def test_boundary_rows_match_for_2024_and_2025(self):
        for boundary, year, ganzhi in (
                (BOUNDARY_2024, 2024, "甲辰"),
                (BOUNDARY_2025, 2025, "乙巳")):
            with self.subTest(year=year):
                result = check_flow_year_boundary(boundary, year, "乙")
                self.assertEqual(result["status"], "checked_match")
                self.assertEqual(result["ganzhi"], ganzhi)
                self.assertEqual(result["boundary_variant"],
                                 FLOW_BOUNDARY_VARIANT)
                self.assertEqual(result["target_year"], year)

    def test_boundary_mismatch_is_fail_closed(self):
        import copy
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["rows"][0]["ganzhi_in_interval"] = "乙巳"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["rows"][0]["ganzhi_at_end"] = "甲辰"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["rows"][0]["ten_god_relative_to_natal_day_stem"] = "正财"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["variant"] = "other-variant"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["day_master"] = "甲"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")
        # 没有目标年份的行：不是“对不上就按推导值补”，而是拒收。
        with self.assertRaises(ValueError):
            check_flow_year_boundary(BOUNDARY_2024, 2025, "乙")
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["rows"][0]["end_exclusive"] = "2024-02-04T16:27:07+08:00"
        with self.assertRaises(ValueError):
            check_flow_year_boundary(wrong, 2024, "乙")

    def test_combine_boundary_check_default_is_not_checked(self):
        output = _combine_f2(2024)
        check = output["flow_year"]["boundary_check"]
        self.assertEqual(check["status"], "not_checked")
        self.assertEqual(check["boundary_variant"], FLOW_BOUNDARY_VARIANT)
        self.assertEqual(output["flow_year"]["ganzhi"], "甲辰")

    def test_combine_with_matching_boundary_rows(self):
        output = _combine_f2(2024, flow_boundary=BOUNDARY_2024)
        check = output["flow_year"]["boundary_check"]
        self.assertEqual(check["status"], "checked_match")
        self.assertEqual(check["ganzhi"], "甲辰")
        self.assertEqual(output["flow_year"]["ganzhi"], "甲辰")

    def test_combine_with_mismatching_boundary_rows_is_rejected(self):
        import copy
        wrong = copy.deepcopy(BOUNDARY_2024)
        wrong["rows"][0]["ganzhi_in_interval"] = "乙巳"
        with self.assertRaises(ValueError):
            _combine_f2(2024, flow_boundary=wrong)


class D04PunishmentAndGroupsTests(unittest.TestCase):
    """D-04：刑不评估（无表）、跨三层组不产生条件结论。"""

    def test_punishment_status_names_the_gap(self):
        status = punishment_status()
        self.assertEqual(status["kind"], "branch_punishment")
        self.assertEqual(status["status"], "not_evaluated")
        self.assertFalse(status["table_available"])
        self.assertEqual(status["gap"], "S-06/D-04")
        self.assertEqual(status["branch_pairs_examined_for_punishment"], 0)
        self.assertIn("Lane 1", status["reason"])

    def test_no_punishment_relation_is_ever_emitted(self):
        for pillars, day_master, dayun, year in (
                (CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988),
                (F2_PILLARS, "乙", F2_DAYUN_8, 2024)):
            with self.subTest(year=year):
                output = combine(pillars, day_master, dayun, year)
                self.assertFalse([
                    r for r in output["structural_relations"]
                    if "punishment" in r["kind"]])
                self.assertEqual(
                    output["relation_summary"]["punishment_status"],
                    punishment_status())

    def test_spanning_groups_never_produce_conditional_conclusions(self):
        # B 盘 1997：原局巳＋大运三酉＋流年丁丑＝巳酉丑三合金（跨三层）。
        output = combine(CASE_B_PILLARS, "戊", CASE_B_DAYUN, 1997)
        spanning = [r for r in output["structural_relations"]
                    if r["scope"] == "dayun_x_flow_x_natal"]
        self.assertEqual(len(spanning), 1)
        self.assertEqual(spanning[0]["detail"]["branches"],
                         ["巳", "酉", "丑"])
        self.assertEqual(spanning[0]["effect"]["status"], "abstain")
        group_status = output["relation_summary"][
            "cross_layer_group_status"]
        self.assertFalse(
            group_status["groups_produce_conditional_conclusions"])
        self.assertEqual(group_status["spanning_group_relations"], 1)
        self.assertEqual(group_status["scope"], "dayun_x_flow_x_natal")


class D05EightPeriodCompletenessTests(unittest.TestCase):
    """D-05：8 运数据完整可用；呈现仍只首运（产品边界，不扩展）。"""

    def test_three_period_sequence_is_incomplete(self):
        result = dayun_sequence_completeness(CASE_A_DAYUN)
        self.assertEqual(result["periods_present"], [1, 2, 3])
        self.assertEqual(result["periods_expected"], 8)
        self.assertFalse(result["complete"])
        self.assertEqual(result["missing_period_indices"], [4, 5, 6, 7, 8])
        self.assertIn("首运", result["presentation_note"])

    def test_eight_period_f2_sequence_is_complete(self):
        result = dayun_sequence_completeness(F2_DAYUN_8)
        self.assertTrue(result["complete"])
        self.assertEqual(result["missing_period_indices"], [])
        self.assertEqual(result["periods_present"], [1, 2, 3, 4, 5, 6, 7, 8])

    def test_duplicate_period_index_is_rejected(self):
        with self.assertRaises(ValueError):
            dayun_sequence_completeness([
                {"candidate_ganzhi": "辛酉", "period_index": 1},
                {"candidate_ganzhi": "壬戌", "period_index": 1}])

    def test_combine_carries_sequence_completeness(self):
        output = _combine_f2(2024)
        completeness = output["dayun"]["sequence_completeness"]
        self.assertTrue(completeness["complete"])
        self.assertEqual(completeness["periods_present"],
                         [1, 2, 3, 4, 5, 6, 7, 8])
        # 呈现边界：本批不扩展 career/life 的 2–8 运呈现。
        self.assertIn("不扩展", completeness["presentation_note"])
        short = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988)
        self.assertFalse(
            short["dayun"]["sequence_completeness"]["complete"])


class F2FullChainTests(unittest.TestCase):
    """f2 真实命盘全链复核（2024-02-11T16:27:07+08:00）。"""

    def test_f2_flow_years_and_ten_gods(self):
        self.assertEqual(_combine_f2(2024)["flow_year"]["ganzhi"], "甲辰")
        self.assertEqual(
            _combine_f2(2024)["flow_year"]["stem_ten_god"], "劫财")
        self.assertEqual(_combine_f2(2025)["flow_year"]["ganzhi"], "乙巳")
        self.assertEqual(
            _combine_f2(2025)["flow_year"]["stem_ten_god"], "比肩")
        self.assertEqual(_combine_f2(2026)["flow_year"]["ganzhi"], "丙午")
        self.assertEqual(
            _combine_f2(2026)["flow_year"]["stem_ten_god"], "伤官")
        # 十神手算复核：乙日主，甲劫财、乙比肩、丙伤官。
        self.assertEqual(ten_god_for("乙", "甲"), "劫财")
        self.assertEqual(ten_god_for("乙", "乙"), "比肩")
        self.assertEqual(ten_god_for("乙", "丙"), "伤官")

    def test_f2_flow_x_natal_2024_hand_count(self):
        # 手算：流年甲辰 × 原局四柱——天干 4 行（甲对甲/丙/乙/甲，
        # 无五合），地支 0 行（辰对辰/寅/巳/申皆无已审六合/害/冲），
        # 组 0 行（三合/方位会皆缺支）。合计 4 行。
        output = _combine_f2(2024)
        flow_rows = [r for r in output["structural_relations"]
                     if r["scope"] == "flow_x_natal"]
        self.assertEqual(len(flow_rows), 4)
        self.assertTrue(all(r["kind"] == "stem_five_element"
                            for r in flow_rows))
        same_stem = [r for r in flow_rows
                     if r["detail"]["same_stem"]]
        self.assertEqual(len(same_stem), 2)
        self.assertTrue(all(r["detail"]["stems"] == ["甲", "甲"]
                            for r in same_stem))
        self.assertIsNone(output["effects"]["overall_effect"])

    def test_f2_boundary_and_period_mapping(self):
        output = _combine_f2(2024, flow_boundary=BOUNDARY_2024)
        self.assertEqual(
            output["flow_year"]["boundary_check"]["status"],
            "checked_match")
        self.assertEqual(output["dayun"]["period_year_mapping"],
                         "not_determined")
        # 显式指定当期运（caller_attested 口径，不虚构交运区间）。
        specified = _combine_f2(
            2024, flow_boundary=BOUNDARY_2024,
            current_period_index=1,
            current_period_basis=(
                "caller attested period 1 for research example; "
                "no handover interval computed"),
            current_period_basis_kind="caller_attested")
        self.assertEqual(specified["dayun"]["period_year_mapping"],
                         "caller_selected")
        self.assertEqual(
            specified["dayun"]["period_year_mapping_detail"]["status"],
            "caller_selected")

    def test_bare_case_a_relation_total_unchanged(self):
        # 回归锚：无夹具输入时关系总数仍为 30（与既有算例 A 一致），
        # 全部 abstain（无条件结论输入）。
        output = combine(CASE_A_PILLARS, "甲", CASE_A_DAYUN, 1988)
        self.assertEqual(output["relation_summary"]["total"], 30)
        self.assertEqual(output["effects"]["verdict_counts"],
                         {"abstain": 30})
        self.assertIsNone(output["effects"]["overall_effect"])


class CrossCheckTests(unittest.TestCase):
    """组装环境复核：边界行须与实时 annual_lichun_boundaries 一致。

    公开检出无历法 provider 与密封数据时跳过（不伪造通过）。
    """

    def test_boundary_rows_match_live_lichun_boundaries(self):
        try:
            from tianji_kb.bazi_annual_reference import (
                annual_lichun_boundaries as live_boundaries)
        except Exception as error:  # noqa: BLE001 - 密封依赖缺失即跳过
            self.skipTest("live boundary module unavailable: %s" % error)
        for boundary, year in ((BOUNDARY_2024, 2024),
                               (BOUNDARY_2025, 2025)):
            with self.subTest(year=year):
                try:
                    live = live_boundaries("乙", [year])["rows"][0]
                except ValueError as error:
                    # provider 身份/版本未核验（如本地装 1.4.9 而仓库钉
                    # 定 1.4.8）：环境限制，跳过，不伪造通过。
                    self.skipTest(
                        "live boundary call refused: %s" % error)
                row = boundary["rows"][0]
                self.assertEqual(live["ganzhi_in_interval"],
                                 row["ganzhi_in_interval"])
                self.assertEqual(live["start_inclusive"],
                                 row["start_inclusive"])
                self.assertEqual(live["end_exclusive"],
                                 row["end_exclusive"])
                self.assertEqual(live["ganzhi_one_second_before_start"],
                                 row["ganzhi_one_second_before_start"])
                self.assertEqual(live["ganzhi_at_start"],
                                 row["ganzhi_at_start"])
                self.assertEqual(live["ganzhi_one_second_before_end"],
                                 row["ganzhi_one_second_before_end"])
                self.assertEqual(live["ganzhi_at_end"],
                                 row["ganzhi_at_end"])


if __name__ == "__main__":
    unittest.main()
