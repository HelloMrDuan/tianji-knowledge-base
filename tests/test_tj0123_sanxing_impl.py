"""TJ-012.3 三刑事实层实现（SLICE_SPEC sanxing-branch-fact-v1）：公开专项。

实现批（E0268）落地审定批（E0267，PR #447）审定的切片规格：独立
结构事实函数 ``reviewed_branch_punishment_facts``
（``bazi_sanxing_facts``）只消费审定登记
``bazi_sanxing_fact_adjudication``，输出三类事实——无名组在场
组态（full/partial/single，只报在场）、带见证等级的有向环边
（A×6＋B×1，未刑丑等级 C 不入、方案非边永不输出）、自刑重见。

公开层钉住：Golden 全真实出生时刻经生产历法链
（``tianji_kb.calendar.calendar``，即 chart_from_datetime 的柱
计算步）回放与期望逐字一致；输出键白名单与禁用键扫描（无组名、
无任何效价/成否/吉凶字段）；12^4 全穷举守卫（等级 C 边与非边
在任何输入下不出现、B 级边恒带等级）；非法输入与登记篡改
fail-closed；注册口径（pending、sufficient_rule=None、
research_only、public/ai 关闭）；公开投影防御剥离；零消费接线
（无任何其他生产模块 import 本模块）。

密封专项（快照引文逐字复核、组装环境 chart_from_datetime 全链
回放、既有关系面的并存与无刑回归）在
``tests/test_tj0123_sanxing_impl_sealed.py``（仅离线验收，
不进公开 CI）。
"""

from __future__ import annotations

import itertools
import json
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_sanxing_facts as impl
from tianji_kb.calendar import calendar
from tianji_kb.foundations import ganzhi_index
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0123_sanxing_impl.json").read_text(
        encoding="utf-8"))
CASES = GOLDEN["cases"]

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
            "午", "未", "申", "酉", "戌", "亥"]
GROUP_NAMES = ("无恩", "恃势", "无礼")
FORBIDDEN_KEYS = {
    "verdict", "judgment", "judgement", "auspicious", "inauspicious",
    "fortune", "misfortune", "score", "rating", "severity", "degree",
    "valence", "effect", "efficacy", "formed", "is_formed",
    "success", "failure", "group_name", "name_zh", "label",
    "吉凶", "成否", "效价", "程度", "评分", "组名", "刑名",
    "灾祸", "贵贱",
}
TOP_KEYS = {"directed_pairs", "group_configurations",
            "self_punishments", "names"}
PAIR_KEYS = {"actor_branch", "target_branch", "actor_pillar",
             "target_pillar", "group_id", "attestation_grade",
             "evidence_refs"}
GROUP_KEYS = {"group_id", "members", "present_branches",
              "present_pillars", "present_member_count", "completeness"}
SELF_KEYS = {"branch", "pillars", "evidence_refs"}
IN_SLICE_EDGES = {(p["actor"], p["target"])
                  for p in adj.DIRECTED_PAIR_TABLE if p["in_slice"]}
NON_EDGES = {tuple(x) for x in adj.NON_EDGE_REGISTER["pairs"]}


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for value in node:
            yield from _all_keys(value)


class GoldenReplayTest(unittest.TestCase):
    def test_cases_cover_adjudicated_discriminators(self) -> None:
        ids = [c["id"] for c in CASES]
        for required in (
                "g1_chou_wei_partial_no_edges",      # 丑未 partial 零对
                "g2_yin_shen_only",                  # 寅申只报申→寅
                "g3_group2_full",                    # 寅巳申全组
                "g4_group3_full",                    # 丑戌未全组不补未→丑
                "g5_zi_mao_bidirectional",           # 子卯 A/B 双向
                "g6_self_chen_double",               # 自刑重见
                "g7_empty_self_singles",             # 空输出
                "g8_zi_mao_multi_pillar",            # 同边多柱对
                "g9_group2_partial_with_edge"):      # partial 而有对
            self.assertIn(required, ids)

    def test_real_charts_replay_through_production_calendar(self) -> None:
        for case in CASES:
            with self.subTest(case=case["id"]):
                for pillar in case["expected_pillars"]:
                    self.assertGreaterEqual(ganzhi_index(pillar), 0,
                                            (case["id"], pillar))
                cal = calendar(case["birth"])
                pillars = [cal["year_ganzhi"], cal["month_ganzhi"],
                           cal["day_ganzhi"], cal["hour_ganzhi"]]
                self.assertEqual(pillars, case["expected_pillars"])
                self.assertEqual([p[1] for p in pillars],
                                 case["expected_branches"])

    def test_function_output_matches_hand_derived_expectations(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = impl.reviewed_branch_punishment_facts(
                    case["expected_branches"])
                self.assertEqual(out, case["expected"])

    def test_grade_b_edge_carries_its_grade_and_section_ref(self):
        case = next(c for c in CASES
                    if c["id"] == "g5_zi_mao_bidirectional")
        out = impl.reviewed_branch_punishment_facts(
            case["expected_branches"])
        b_rows = [r for r in out["directed_pairs"]
                  if r["attestation_grade"] == "B"]
        self.assertEqual(len(b_rows), 1)
        self.assertEqual((b_rows[0]["actor_branch"],
                          b_rows[0]["target_branch"]), ("卯", "子"))
        self.assertIn("bazi.section.s021", b_rows[0]["evidence_refs"])


class OutputContractTest(unittest.TestCase):
    def test_key_whitelists_and_no_names_or_verdicts(self) -> None:
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = impl.reviewed_branch_punishment_facts(
                    case["expected_branches"])
                self.assertEqual(set(out), TOP_KEYS)
                self.assertIsNone(out["names"])
                for row in out["directed_pairs"]:
                    self.assertEqual(set(row), PAIR_KEYS)
                for row in out["group_configurations"]:
                    self.assertEqual(set(row), GROUP_KEYS)
                for row in out["self_punishments"]:
                    self.assertEqual(set(row), SELF_KEYS)
                self.assertEqual(set(_all_keys(out)) & FORBIDDEN_KEYS,
                                 set())
                dump = json.dumps(out, ensure_ascii=False)
                for name in GROUP_NAMES:
                    self.assertNotIn(name, dump)

    def test_completeness_is_presence_only(self) -> None:
        for case in CASES:
            out = impl.reviewed_branch_punishment_facts(
                case["expected_branches"])
            for row in out["group_configurations"]:
                self.assertEqual(row["present_member_count"],
                                 len(row["present_branches"]))
                if row["present_member_count"] == len(row["members"]):
                    self.assertEqual(row["completeness"], "full")
                elif row["present_member_count"] == 2:
                    self.assertEqual(row["completeness"], "partial")
                else:
                    self.assertEqual(row["completeness"], "single")


class ExhaustiveGuardTest(unittest.TestCase):
    def test_all_branch_tuples_never_emit_excluded_or_non_edges(self):
        seen_edges = set()
        for branches in itertools.product(BRANCHES, repeat=4):
            out = impl.reviewed_branch_punishment_facts(list(branches))
            for row in out["directed_pairs"]:
                edge = (row["actor_branch"], row["target_branch"])
                seen_edges.add(edge)
                self.assertIn(edge, IN_SLICE_EDGES, (branches, edge))
                self.assertNotIn(edge, NON_EDGES, (branches, edge))
                if row["attestation_grade"] == "B":
                    self.assertEqual(edge, ("卯", "子"))
                    self.assertIn("bazi.section.s021",
                                  row["evidence_refs"])
                self.assertEqual(
                    branches[["year", "month", "day", "hour"].index(
                        row["actor_pillar"])], row["actor_branch"])
            for row in out["self_punishments"]:
                self.assertIn(row["branch"], ("辰", "午", "酉", "亥"))
                self.assertGreaterEqual(len(row["pillars"]), 2)
            dump = json.dumps(out, ensure_ascii=False)
            for name in GROUP_NAMES:
                self.assertNotIn(name, dump)
        # every in-slice edge is reachable, and nothing else ever was
        self.assertEqual(seen_edges, IN_SLICE_EDGES)
        self.assertNotIn(("未", "丑"), seen_edges)


class FailClosedTest(unittest.TestCase):
    def test_illegal_inputs_raise_value_error(self) -> None:
        bad_inputs = [
            [], ["子", "丑", "寅"], ["子", "丑", "寅", "卯", "辰"],
            "子丑寅卯", None, 42,
            ["子", "丑", "寅", "猫"], ["子丑", "寅", "卯", "辰"],
            ["子", "丑", "寅", None], ["子", "丑", "寅", 3],
        ]
        for bad in bad_inputs:
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    impl.reviewed_branch_punishment_facts(bad)

    def test_registration_integrity_passes_unmodified(self) -> None:
        self.assertEqual(impl._registration_integrity_errors(), [])

    def test_tampered_evidence_ref_fails_closed(self) -> None:
        row = adj.DIRECTED_PAIR_TABLE[0]
        original = row["evidence_refs"]
        row["evidence_refs"] = ["bogus.ref"]
        try:
            with self.assertRaises(RuntimeError) as ctx:
                impl.reviewed_branch_punishment_facts(
                    ["子", "卯", "辰", "午"])
            self.assertIn("registration_integrity_failure",
                          str(ctx.exception))
        finally:
            row["evidence_refs"] = original

    def test_flipping_grade_c_edge_into_slice_fails_closed(self) -> None:
        row = next(p for p in adj.DIRECTED_PAIR_TABLE
                   if not p["in_slice"])
        row["in_slice"] = True
        try:
            with self.assertRaises(RuntimeError):
                impl.reviewed_branch_punishment_facts(
                    ["未", "丑", "辰", "午"])
        finally:
            row["in_slice"] = False

    def test_removed_pair_row_fails_closed(self) -> None:
        row = adj.DIRECTED_PAIR_TABLE.pop()
        try:
            with self.assertRaises(RuntimeError):
                impl.reviewed_branch_punishment_facts(
                    ["子", "卯", "辰", "午"])
        finally:
            adj.DIRECTED_PAIR_TABLE.append(row)

    def test_reversed_group_cycle_fails_closed(self) -> None:
        group = adj.GROUP_TABLE["groups"][1]
        original = group["cycle"]
        group["cycle"] = list(reversed(original))
        try:
            with self.assertRaises(RuntimeError):
                impl.reviewed_branch_punishment_facts(
                    ["寅", "巳", "申", "午"])
        finally:
            group["cycle"] = original


class RegistrationTest(unittest.TestCase):
    def test_slice_registration_matches_adjudicated_spec(self) -> None:
        reg = impl.SLICE_REGISTRATION
        spec_reg = adj.SLICE_SPEC["registration"]
        self.assertEqual(reg["slice_id"], "sanxing-branch-fact-v1")
        self.assertEqual(reg["slice_id"], adj.SLICE_SPEC["id"])
        self.assertEqual(reg["evidence_binding"],
                         "pending_phase1_registration")
        self.assertTrue(spec_reg["evidence_binding"].startswith(
            "pending_phase1_registration"))
        self.assertIsNone(reg["sufficient_rule"])
        self.assertIsNone(spec_reg["sufficient_rule"])
        self.assertIs(reg["research_only"], True)
        self.assertIs(reg["public_enabled"], False)
        self.assertIs(reg["ai_enabled"], False)
        self.assertIsNone(reg["phase2_rule"])
        self.assertIsNone(reg["scenario_wiring"])

    def test_concept_semantics_restated_unchanged(self) -> None:
        reg = impl.SLICE_REGISTRATION
        self.assertEqual(reg["concept_id"],
                         "bazi.concept.conflict_three_punishments")
        self.assertFalse(reg["concept_semantics_changed"])
        self.assertFalse(adj.CONCEPT_LINKAGE[
            "adjudication_semantics_changed"])
        self.assertEqual(adj.CONCEPT_LINKAGE["executable_policy"],
                         "blocked_pending_school_resolution")


class ProjectionStripTest(unittest.TestCase):
    def test_punishment_facts_block_stripped_from_public(self) -> None:
        case = CASES[0]
        block = impl.reviewed_branch_punishment_facts(
            case["expected_branches"])
        payload = {
            "evidence": {},
            "rule_matches": [],
            "trace": [],
            "chart": {"branch_punishment_facts": block},
            "result": {"branch_punishment_facts": block},
        }
        projected = project_execution(payload)
        self.assertNotIn("branch_punishment_facts", projected["chart"])
        self.assertNotIn("branch_punishment_facts", projected["result"])


class WiringIsolationTest(unittest.TestCase):
    def test_no_other_production_module_imports_the_slice(self) -> None:
        src = ROOT / "src" / "tianji_kb"
        pattern = re.compile(
            r"(from\s+\.\s*bazi_sanxing_facts\s+import"
            r"|import\s+bazi_sanxing_facts"
            r"|from\s+tianji_kb\.bazi_sanxing_facts\s+import"
            r"|from\s+\.bazi_sanxing_facts\s+import)")
        offenders = []
        for path in src.rglob("*.py"):
            if path.name == "bazi_sanxing_facts.py":
                continue
            if pattern.search(path.read_text(encoding="utf-8")):
                offenders.append(path.name)
        self.assertEqual(offenders, [])

    def test_existing_relation_surface_untouched(self) -> None:
        core = (ROOT / "src" / "tianji_kb" / "bazi_core.py").read_text(
            encoding="utf-8")
        self.assertNotIn("punish", core)
        self.assertNotIn("三刑", core)


if __name__ == "__main__":
    unittest.main()
