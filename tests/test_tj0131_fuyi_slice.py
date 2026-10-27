"""TJ-013.1 S4（扶抑最小切片审定）的公开结构测试。

本模块（``bazi_fuyi_slice_adjudication``）是纯数据审定登记、零
判定代码；本测试只钉审定结构与红线：结论为零行可建且无 Variant
规格、输入面七谓词与可喂入/不可喂入事实清单、方向表十行逐行审
计与 S3 登记逐字对齐（行文/定位/量化词/方向）、判句 37 句逐句
归组恰覆盖一次、近失项驳回登记、解锁前置六项与决策层级、若解
锁的输出契约要求（喜用字段恒 None）、与 TJ-013.2 呈现层的接口
常量一致、禁止判定/阈值语义键、零运行时接入。真实命盘回放与
「已得判定仍无扶抑产出」的防夹带钉在密封专项
``tests/test_tj0131_fuyi_slice_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_conflict_presentation as cp
from tianji_kb import bazi_ditiansui_fuyi as fy
from tianji_kb import bazi_fuyi_slice_adjudication as s4

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0131_fuyi_slice.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "determination", "true_false", "verdict", "threshold",
    "quantifier_threshold", "fuyi_result", "support_suppress_result",
    "扶抑结果", "扶抑判定", "用神裁定",
}

PREDICATE_IDS = [
    "pure_support", "pure_generating_support", "isolated_control",
    "commanding_visible_support", "lu_visible_support",
    "pure_support_metal", "pure_generating_support_water",
]


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


def _module_data():
    return [s4.ADJUDICATION_VERDICT, s4.INPUT_SURFACE,
            s4.DIRECTION_TABLE_AUDIT, s4.PASSAGE_AUDITS, s4.NEAR_MISSES,
            s4.UNLOCK_PRECONDITIONS, s4.REQUIREMENTS_IF_UNLOCKED,
            s4.TJ0132_INTERFACE, s4.CURRENT_STATE_PINS,
            s4.ADJUDICATION_NOTES, s4.ADJUDICATION_LIMITATIONS]


class MirrorTest(unittest.TestCase):
    def test_module_mirrors_golden(self) -> None:
        self.assertEqual(s4.SLICE_ADJUDICATION_ID,
                         GOLDEN["adjudication_id"])
        self.assertEqual(s4.ADJUDICATION_VERDICT, GOLDEN["conclusion"])
        self.assertEqual(s4.INPUT_SURFACE, GOLDEN["input_surface"])
        self.assertEqual(s4.DIRECTION_TABLE_AUDIT,
                         GOLDEN["direction_table_audit"])
        self.assertEqual(s4.PASSAGE_AUDITS, GOLDEN["passage_audits"])
        self.assertEqual(s4.NEAR_MISSES, GOLDEN["near_misses"])
        self.assertEqual(s4.UNLOCK_PRECONDITIONS,
                         GOLDEN["unlock_preconditions"])
        self.assertEqual(s4.REQUIREMENTS_IF_UNLOCKED,
                         GOLDEN["requirements_if_unlocked"])
        self.assertEqual(s4.TJ0132_INTERFACE, GOLDEN["tj0132_interface"])
        self.assertEqual(s4.CURRENT_STATE_PINS,
                         GOLDEN["current_state_pins"])
        self.assertEqual(s4.ADJUDICATION_NOTES, GOLDEN["notes"])
        self.assertEqual(s4.ADJUDICATION_LIMITATIONS,
                         GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        funcs = [n for n, _ in inspect.getmembers(s4, inspect.isfunction)]
        classes = [n for n, _ in inspect.getmembers(s4, inspect.isclass)]
        self.assertEqual(funcs, [])
        self.assertEqual(classes, [])


class VerdictTest(unittest.TestCase):
    def test_zero_buildable_rows(self) -> None:
        v = s4.ADJUDICATION_VERDICT
        self.assertEqual(v["conclusion"], "no_buildable_rows")
        self.assertEqual(v["buildable_count"], 0)
        self.assertEqual(v["buildable_units"], [])
        self.assertIsNone(s4.SLICE_SPEC)
        self.assertEqual(v["audited"], {
            "direction_table_rows": 10, "judgment_sentences": 37,
            "passage_units": 9, "cross_references": 4})

    def test_nothing_buildable_anywhere(self) -> None:
        for entry in s4.DIRECTION_TABLE_AUDIT:
            self.assertFalse(entry["buildable"], entry["row"])
        for unit in s4.PASSAGE_AUDITS:
            self.assertFalse(unit["buildable"], unit["unit_id"])
            self.assertTrue(unit["blocking_reasons"], unit["unit_id"])
            for r in unit["blocking_reasons"]:
                self.assertTrue(r["code"] and r["detail"],
                                unit["unit_id"])


class InputSurfaceTest(unittest.TestCase):
    def test_seven_predicates_enumerated(self) -> None:
        preds = s4.INPUT_SURFACE["predicates"]
        self.assertEqual([p["id"] for p in preds], PREDICATE_IDS)
        by_id = {p["id"]: p for p in preds}
        self.assertEqual(by_id["isolated_control"]["classification"],
                         "weak")
        for pid in PREDICATE_IDS:
            if pid != "isolated_control":
                self.assertEqual(by_id[pid]["classification"], "strong",
                                 pid)
        self.assertEqual(by_id["pure_support"]["registration"],
                         "registered")
        self.assertEqual(by_id["isolated_control"]["registration"],
                         "registered")
        for pid in ("pure_generating_support",
                    "commanding_visible_support", "lu_visible_support",
                    "pure_support_metal",
                    "pure_generating_support_water"):
            self.assertEqual(by_id[pid]["registration"],
                             "pending_phase1_rule_registration", pid)
        self.assertEqual(by_id["pure_support_metal"]["witness"],
                         "none_constructively_unsatisfiable_s2")

    def test_output_contract_has_no_middle_state(self) -> None:
        self.assertEqual(
            s4.INPUT_SURFACE["supported_classifications"],
            ["strong", "weak", "indeterminate"])

    def test_feedable_and_non_feedable_facts(self) -> None:
        self.assertEqual(
            [f["id"] for f in s4.INPUT_SURFACE["feedable_facts"]],
            ["F1", "F2", "F3"])
        self.assertEqual(
            [f["id"] for f in s4.INPUT_SURFACE["non_feedable_facts"]],
            ["N1", "N2", "N3", "N4"])
        n1 = s4.INPUT_SURFACE["non_feedable_facts"][0]
        self.assertIn("十神计数", n1["reason"])
        self.assertIn("weights_available=False", n1["reason"])


class DirectionTableAuditTest(unittest.TestCase):
    def test_rows_align_verbatim_with_s3_register(self) -> None:
        rows = fy.FUYI_DIRECTION_TABLE["rows"]
        self.assertEqual(len(s4.DIRECTION_TABLE_AUDIT), 10)
        for entry, row in zip(s4.DIRECTION_TABLE_AUDIT, rows):
            self.assertEqual(entry["row"], row["row"])
            self.assertEqual(entry["text"], row["text"])
            self.assertEqual(entry["locator"], row["locator"])
            self.assertEqual(entry["premise_day_master_state"],
                             row["premise_day_master_state"])
            self.assertEqual(entry["direction_god"],
                             row["direction_god"])
            self.assertEqual(
                [c["term"] for c in entry["condition_audits"]],
                [q["term"] for q in row["condition_quantifiers"]])
            self.assertTrue(entry["blocking_summary"])

    def test_every_condition_unfeedable_with_reason(self) -> None:
        for entry in s4.DIRECTION_TABLE_AUDIT:
            self.assertTrue(entry["condition_audits"], entry["row"])
            for c in entry["condition_audits"]:
                self.assertFalse(c["feedable"], (entry["row"], c["term"]))
                self.assertEqual(c["registered_status"],
                                 "quantifier_unthresholded")
                marker = "N1" if entry["row"] < 9 else "N3"
                self.assertIn(marker, c["reason"],
                              (entry["row"], c["term"]))

    def test_middle_state_rows_blocked_at_premise(self) -> None:
        for entry in s4.DIRECTION_TABLE_AUDIT[:8]:
            self.assertTrue(entry["premise_feedable"], entry["row"])
        for entry in s4.DIRECTION_TABLE_AUDIT[8:]:
            self.assertFalse(entry["premise_feedable"], entry["row"])
            self.assertIn("不可裁决", entry["premise_blocking_reason"])

    def test_other_party_strength_rows_double_blocked(self) -> None:
        for row_no in (6, 8):
            entry = s4.DIRECTION_TABLE_AUDIT[row_no - 1]
            self.assertIn("N2", entry["condition_audits"][0]["reason"])
            self.assertIn("双重", entry["blocking_summary"])

    def test_glyph_blockers_only_on_rows_3_and_5(self) -> None:
        self.assertEqual(s4.DIRECTION_TABLE_AUDIT[2]["glyph_blockers"],
                         ["fy-glyph-06"])
        self.assertEqual(s4.DIRECTION_TABLE_AUDIT[4]["glyph_blockers"],
                         ["fy-glyph-05"])
        for i, entry in enumerate(s4.DIRECTION_TABLE_AUDIT):
            if i not in (2, 4):
                self.assertNotIn("glyph_blockers", entry)


class PassageAuditTest(unittest.TestCase):
    def test_units_cover_all_sentences_exactly_once(self) -> None:
        seen = []
        for unit in s4.PASSAGE_AUDITS:
            for ref in unit["sentence_refs"]:
                seen.append((ref["quote_id"], ref["sentence_index"]))
        expect = {(q["id"], i) for q in fy.FUYI_QUOTES
                  for i in range(len(q["judgment_sentences"]))}
        self.assertEqual(set(seen), expect)
        self.assertEqual(len(seen), 37)

    def test_sentence_refs_resolve_verbatim(self) -> None:
        quotes = {q["id"]: q for q in fy.FUYI_QUOTES}
        for unit in s4.PASSAGE_AUDITS:
            for ref in unit["sentence_refs"]:
                src = quotes[ref["quote_id"]]["judgment_sentences"][
                    ref["sentence_index"]]
                self.assertEqual(ref["text"], src["text"])
                self.assertEqual(ref["kind"], src["kind"])
                self.assertEqual(ref["quantifiers"], src["quantifiers"])

    def test_all_quotes_and_xrefs_covered(self) -> None:
        covered = set()
        for unit in s4.PASSAGE_AUDITS:
            covered |= set(unit["quote_ids"])
        self.assertEqual(covered, {q["id"] for q in fy.FUYI_QUOTES})
        xref_unit = next(u for u in s4.PASSAGE_AUDITS
                         if u["unit_id"] == "xref_fu_verses")
        self.assertEqual(xref_unit["xref_ids"],
                         [x["id"] for x in fy.FUYI_CROSS_REFERENCES])

    def test_unit_ids_and_dispositions(self) -> None:
        self.assertEqual(
            [u["unit_id"] for u in s4.PASSAGE_AUDITS],
            ["f1_general_rules", "f1_counter_clauses",
             "f3_general_rule_and_reversals", "f3_tigang_statements",
             "f2_xingxiang_form", "direction_table_framing",
             "u2_capability_statement", "xref_fu_verses",
             "chapter_head_framing"])
        by_id = {u["unit_id"]: u for u in s4.PASSAGE_AUDITS}
        for uid in ("u2_capability_statement", "xref_fu_verses",
                    "chapter_head_framing"):
            self.assertEqual(by_id[uid]["disposition"], "excluded", uid)

    def test_f1_blockers_name_counter_clauses_first(self) -> None:
        unit = next(u for u in s4.PASSAGE_AUDITS
                    if u["unit_id"] == "f1_general_rules")
        codes = [r["code"] for r in unit["blocking_reasons"]]
        self.assertEqual(codes, ["counter_clauses_unevaluable",
                                 "undifferentiated_pair_output"])
        self.assertTrue(unit["premise_feedable"])

    def test_f2_cross_cutting_analysis_registered(self) -> None:
        unit = next(u for u in s4.PASSAGE_AUDITS
                    if u["unit_id"] == "f2_xingxiang_form")
        codes = [r["code"] for r in unit["blocking_reasons"]]
        self.assertEqual(codes, [
            "direction_is_f1_restatement",
            "classification_partial_enumeration",
            "classification_not_strength_premise",
            "differentiation_examples_unthresholded",
            "no_cong_form_identification"])
        detail = unit["blocking_reasons"][2]["detail"]
        self.assertIn("辰月", detail)
        self.assertIn("亥", detail)


class NearMissTest(unittest.TestCase):
    def test_cong_form_follow_rejected_with_reasons(self) -> None:
        self.assertEqual(len(s4.NEAR_MISSES), 1)
        miss = s4.NEAR_MISSES[0]
        self.assertEqual(miss["id"], "near_miss_cong_form_follow")
        self.assertEqual(miss["status"], "rejected_registered")
        self.assertEqual(len(miss["rejected_because"]), 3)
        self.assertEqual(miss["unlock_refs"], ["U1", "U2"])


class UnlockPreconditionsTest(unittest.TestCase):
    def test_six_preconditions_with_decision_levels(self) -> None:
        pres = s4.UNLOCK_PRECONDITIONS
        self.assertEqual([p["id"] for p in pres],
                         ["U1", "U2", "U3", "U4", "U5", "U6"])
        by_id = {p["id"]: p for p in pres}
        for uid in ("U1", "U3"):
            self.assertEqual(by_id[uid]["decision_level"],
                             "user_level_school_adjudication", uid)
            self.assertTrue(by_id[uid]["gates"], uid)
        for uid in ("U4", "U5", "U6"):
            self.assertTrue(by_id[uid]["non_gating_alone"], uid)
            self.assertEqual(by_id[uid]["gates"], [], uid)


class RequirementsTest(unittest.TestCase):
    def test_output_contract_requirements_keep_useful_god_none(self) -> None:
        joined = "\n".join(s4.REQUIREMENTS_IF_UNLOCKED)
        self.assertIn("useful_god", joined)
        self.assertIn("恒为 None", joined)
        self.assertIn("research_only=True", joined)
        self.assertIn("public_enabled=False", joined)
        self.assertIn("ai_enabled=False", joined)
        self.assertIn("弃判", joined)
        self.assertIn("TJ-013.2", joined)


class TJ0132InterfaceTest(unittest.TestCase):
    def test_interface_matches_presentation_layer(self) -> None:
        iface = s4.TJ0132_INTERFACE
        self.assertEqual(iface["system_key"], cp.SYSTEM_FUYI)
        self.assertEqual(iface["built_systems"],
                         list(cp.BUILT_SYSTEMS))
        self.assertFalse(iface["fuyi_in_built_systems"])
        self.assertNotIn(cp.SYSTEM_FUYI, cp.BUILT_SYSTEMS)
        self.assertEqual(iface["absent_reason_registered"],
                         cp.ABSENT_REASONS[cp.SYSTEM_FUYI])
        self.assertEqual(iface["effect_of_this_adjudication"], "none")


class CurrentStatePinsTest(unittest.TestCase):
    def test_six_witness_charts_cover_six_predicates(self) -> None:
        pins = s4.CURRENT_STATE_PINS["witness_charts"]
        self.assertEqual([w["predicate"] for w in pins], [
            "pure_support", "pure_generating_support",
            "isolated_control", "commanding_visible_support",
            "lu_visible_support", "pure_generating_support_water"])
        self.assertEqual([w["classification"] for w in pins],
                         ["strong", "strong", "weak",
                          "strong", "strong", "strong"])
        for w in pins:
            self.assertEqual(len(w["pillars"]), 4)
            self.assertIn("#", w["golden_ref"])
        self.assertIn("pure_support_metal",
                      s4.CURRENT_STATE_PINS["metal_witness_note"])


class DisciplineTest(unittest.TestCase):
    def test_no_determination_or_threshold_semantics(self) -> None:
        for blob in _module_data():
            for key in _walk_keys(blob):
                self.assertNotIn(key, FORBIDDEN_KEYS)

    def test_zero_runtime_wiring(self) -> None:
        src = ROOT / "src" / "tianji_kb"
        for path in src.glob("*.py"):
            if path.name == "bazi_fuyi_slice_adjudication.py":
                continue
            self.assertNotIn("bazi_fuyi_slice_adjudication",
                             path.read_text(encoding="utf-8"),
                             path.name)
        for name in ("bazi_adjudication.py", "bazi_action_conditions.py"):
            text = (src / name).read_text(encoding="utf-8")
            self.assertNotIn("fuyi", text, name)
            self.assertNotIn("扶抑", text, name)

    def test_notes_keep_fuyi_unbuilt_and_census_unchanged(self) -> None:
        joined = "\n".join(s4.ADJUDICATION_NOTES)
        self.assertIn("零 Variant 规格", joined)
        self.assertIn("101 条", joined)
        lim = "\n".join(s4.ADJUDICATION_LIMITATIONS)
        self.assertIn("格局用神", lim)


if __name__ == "__main__":
    unittest.main()
