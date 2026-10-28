"""TJ-012.3 三刑组表事实层设计审定：公开结构测试。

本批是审定批：登记模块 ``bazi_sanxing_fact_adjudication`` 为纯数据、
零函数、不被任何可执行路径 import；本测试只钉登记形制与审定红线
（盘点计数、组表覆盖矩阵、边见证等级、SLICE_SPEC 一致性、命名
不裁定、概念语义不变、零运行时接线），不验证任何三刑判定
（不存在此种代码路径）。引文对快照的逐字复核与现行行为回归在
密封专项 ``tests/test_tj0123_sanxing_fact_sealed.py``（仅离线
验收，不进公开 CI）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj
from tianji_kb import bazi_sanxing_fact_adjudication as adj
from tianji_kb import bazi_yuanhai_zhengguan as yh

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0123_sanxing_fact.json").read_text(
        encoding="utf-8"))

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
            "午", "未", "申", "酉", "戌", "亥"]
VERDICTS = {"fact_ready", "fact_ready_with_grade",
            "fact_ready_as_presence_only", "blocked_by_evidence_gap",
            "blocked_by_naming_conflict", "blocked_by_missing_layers",
            "registered_variant_not_consumed", "registered_doctrine_not_fact",
            "consumer_not_unlocked", "not_applied_by_registered_concept",
            "doctrine_not_fact", "prohibited"}


def _mirror():
    return {
        "meta": {
            "register_id": adj.SANXING_ADJUDICATION_REGISTER["id"],
            "task": adj.SANXING_ADJUDICATION_REGISTER["task"],
            "kind": adj.SANXING_ADJUDICATION_REGISTER["kind"],
            "purpose": GOLDEN["meta"]["purpose"],
        },
        "headline_verdicts":
            adj.SANXING_ADJUDICATION_REGISTER["headline_verdicts"],
        "inventory": [{"id": e["id"], "status": e["status"]}
                      for e in adj.SOURCE_INVENTORY],
        "groups": adj.GROUP_TABLE["groups"],
        "self_punishment": adj.GROUP_TABLE["self_punishment"],
        "directed_pairs": adj.DIRECTED_PAIR_TABLE,
        "non_edges": adj.NON_EDGE_REGISTER,
        "coverage": adj.COVERAGE_MATRIX,
        "proposition_verdicts": [{"id": p["id"], "verdict": p["verdict"]}
                                 for p in adj.PROPOSITION_AUDIT],
        "slice_spec": {"id": adj.SLICE_SPEC["id"],
                       "status": adj.SLICE_SPEC["status"],
                       "registration": adj.SLICE_SPEC["registration"]},
        "pending_items": [{"id": p["id"],
                           "needs_user_adjudication":
                               p["needs_user_adjudication"]}
                          for p in adj.PENDING_ITEMS],
        "quote_references": adj.QUOTE_REFERENCES,
        "sealed_section_pins": adj.SEALED_SECTION_PINS,
    }


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [n for n, o in inspect.getmembers(adj)
                 if inspect.isfunction(o) or inspect.isclass(o)]
        self.assertEqual(funcs, [])

    def test_register_identity(self) -> None:
        reg = adj.SANXING_ADJUDICATION_REGISTER
        self.assertEqual(reg["id"], "bazi-sanxing-fact-adjudication-v1")
        self.assertEqual(reg["task"], "TJ-012.3")
        self.assertEqual(reg["baseline"]["ledger_event"], "E0267")
        hv = reg["headline_verdicts"]
        self.assertEqual(hv["groups"], 3)
        self.assertEqual(hv["cycle_edges_total"], 8)
        self.assertEqual(hv["cycle_edges_grade_a"], 6)
        self.assertEqual(hv["cycle_edges_grade_b"], 1)
        self.assertEqual(hv["cycle_edges_excluded"], 1)
        self.assertFalse(hv["implementation_in_this_batch"])
        self.assertFalse(hv["naming_adjudicated"])
        self.assertFalse(hv["concept_semantics_changed"])

    def test_module_matches_golden(self) -> None:
        self.assertEqual(_mirror(), GOLDEN)


class InventoryTest(unittest.TestCase):
    def test_inventory_shape(self) -> None:
        inv = adj.SOURCE_INVENTORY
        self.assertEqual(len(inv), 14)
        self.assertEqual([e["id"] for e in inv],
                         [f"inv-{i:02d}" for i in range(1, 15)])
        for e in inv:
            for key in ("material", "source_id", "registered_at",
                        "locator", "counts", "status", "note"):
                self.assertIn(key, e, e["id"])

    def test_core_source_counts_match_018b_register(self) -> None:
        inv01 = adj.SOURCE_INVENTORY[0]
        self.assertEqual(inv01["counts"]["collation_notes"],
                         len(cj.COLLATION_NOTES))
        self.assertEqual(inv01["counts"]["quotes"], len(cj.COLLATION_QUOTES))
        self.assertEqual(len(cj.COLLATION_NOTES), 35)
        self.assertEqual(len(cj.COLLATION_QUOTES), 11)

    def test_naming_conflict_still_unadjudicated_upstream(self) -> None:
        self.assertEqual(cj.SANXING_NAMING_VARIANTS["status"], "conflict")
        self.assertIsNone(cj.SANXING_NAMING_VARIANTS["adjudication"])
        self.assertFalse(
            cj.THREE_PUNISHMENTS_CONCEPT_LINKAGE[
                "adjudication_semantics_changed"])


class GroupTableTest(unittest.TestCase):
    def test_branch_coverage_complete(self) -> None:
        members = [b for g in adj.GROUP_TABLE["groups"]
                   for b in g["members"]]
        self_set = adj.GROUP_TABLE["self_punishment"]["members"]
        self.assertEqual(len(members), 8)
        self.assertEqual(len(set(members)), 8)
        self.assertEqual(len(self_set), 4)
        self.assertEqual(sorted(members + self_set), sorted(BRANCHES))
        cov = adj.COVERAGE_MATRIX["branch_coverage"]
        self.assertEqual(cov["union_count"], 12)
        self.assertTrue(cov["all_branches_covered"])

    def test_cycles_match_pair_table(self) -> None:
        cycle_edges = set()
        for g in adj.GROUP_TABLE["groups"]:
            cyc = g["cycle"]
            self.assertEqual(set(cyc), set(g["members"]))
            for i, a in enumerate(cyc):
                cycle_edges.add((a, cyc[(i + 1) % len(cyc)]))
        pair_edges = {(p["actor"], p["target"])
                      for p in adj.DIRECTED_PAIR_TABLE}
        self.assertEqual(cycle_edges, pair_edges)
        self.assertEqual(len(pair_edges), 8)

    def test_naming_never_emitted_as_fact(self) -> None:
        self.assertIn("NO group names", adj.GROUP_TABLE["naming_policy"])
        for g in adj.GROUP_TABLE["groups"]:
            naming = g["naming_registered"]
            self.assertIn(naming["status"],
                          ("uncontested_within_section",
                           "conflict_unadjudicated"))
        g2 = adj.GROUP_TABLE["groups"][1]["naming_registered"]
        g3 = adj.GROUP_TABLE["groups"][2]["naming_registered"]
        # the swap itself is pinned: main text and sanche exchange the
        # same two names between group-2 and group-3
        self.assertEqual(g2["main_text"], g3["sanche_variant"])
        self.assertEqual(g3["main_text"], g2["sanche_variant"])


class PairTableTest(unittest.TestCase):
    def test_grades_and_slice_membership(self) -> None:
        pairs = adj.DIRECTED_PAIR_TABLE
        grades = [p["attestation_grade"] for p in pairs]
        self.assertEqual(grades.count("A"), 6)
        self.assertEqual(grades.count("B"), 1)
        self.assertEqual(grades.count("C"), 1)
        in_slice = [p for p in pairs if p["in_slice"]]
        self.assertEqual(len(in_slice), 7)
        excluded = [p for p in pairs if not p["in_slice"]]
        self.assertEqual(len(excluded), 1)
        self.assertEqual((excluded[0]["actor"], excluded[0]["target"]),
                         ("未", "丑"))
        self.assertEqual(excluded[0]["attestation_grade"], "C")
        self.assertIn("blocked_by_evidence_gap", excluded[0]["blocker"])
        b_rows = [p for p in pairs if p["attestation_grade"] == "B"]
        self.assertEqual((b_rows[0]["actor"], b_rows[0]["target"]),
                         ("卯", "子"))
        self.assertIn("slice_condition", b_rows[0])

    def test_pairs_are_intra_group(self) -> None:
        group_of = {}
        for g in adj.GROUP_TABLE["groups"]:
            for b in g["members"]:
                group_of[b] = g["group_id"]
        for p in adj.DIRECTED_PAIR_TABLE:
            self.assertEqual(group_of[p["actor"]], p["group_id"])
            self.assertEqual(group_of[p["target"]], p["group_id"])
            self.assertNotEqual(p["actor"], p["target"])
            self.assertTrue(p["evidence_refs"])

    def test_non_edges_partition(self) -> None:
        pair_edges = {(p["actor"], p["target"])
                      for p in adj.DIRECTED_PAIR_TABLE}
        non_edges = {tuple(x) for x in adj.NON_EDGE_REGISTER["pairs"]}
        self.assertEqual(len(non_edges), 6)
        self.assertFalse(pair_edges & non_edges)
        all_ordered = set()
        for g in adj.GROUP_TABLE["groups"]:
            for a in g["members"]:
                for b in g["members"]:
                    if a != b:
                        all_ordered.add((a, b))
        self.assertEqual(len(all_ordered), 14)
        self.assertEqual(pair_edges | non_edges, all_ordered)


class CoverageMatrixTest(unittest.TestCase):
    def test_edge_coverage_counts(self) -> None:
        ec = adj.COVERAGE_MATRIX["edge_coverage"]
        self.assertEqual(ec, {"cycle_edges": 8, "grade_a": 6, "grade_b": 1,
                              "grade_c_excluded": 1, "in_slice": 7})

    def test_overlap_pairs_are_real_pairs(self) -> None:
        overlaps = adj.COVERAGE_MATRIX[
            "overlap_with_existing_relations"]["pair_overlaps"]
        self.assertEqual(len(overlaps), 3)
        kinds = {o["existing_kind"] for o in overlaps}
        self.assertEqual(kinds, {"harm", "six_harmony", "clash"})
        pair_edges = {(p["actor"], p["target"])
                      for p in adj.DIRECTED_PAIR_TABLE}
        for o in overlaps:
            a, b = o["pair"]
            self.assertTrue((a, b) in pair_edges or (b, a) in pair_edges)


class PropositionAuditTest(unittest.TestCase):
    def test_rows_and_verdicts(self) -> None:
        rows = adj.PROPOSITION_AUDIT
        self.assertEqual([p["id"] for p in rows],
                         [f"P{i}" for i in range(1, 15)])
        for p in rows:
            self.assertIn(p["verdict"], VERDICTS, p["id"])
            self.assertTrue(p["basis"])
            self.assertTrue(p["enters"])
        by_id = {p["id"]: p for p in rows}
        self.assertEqual(by_id["P4"]["verdict"], "blocked_by_evidence_gap")
        self.assertEqual(by_id["P7"]["verdict"],
                         "blocked_by_naming_conflict")
        self.assertEqual(by_id["P9"]["verdict"], "blocked_by_missing_layers")
        self.assertEqual(by_id["P14"]["verdict"], "prohibited")
        ready = [p["id"] for p in rows
                 if p["verdict"].startswith("fact_ready")]
        self.assertEqual(ready, ["P1", "P2", "P3", "P5", "P6"])


class SliceSpecTest(unittest.TestCase):
    def test_spec_present_but_not_implemented(self) -> None:
        spec = adj.SLICE_SPEC
        self.assertIsNotNone(spec)
        self.assertEqual(spec["id"], "sanxing-branch-fact-v1")
        self.assertEqual(spec["status"], "design_adjudicated_not_implemented")
        reg = spec["registration"]
        self.assertIsNone(reg["sufficient_rule"])
        self.assertTrue(reg["research_only"])
        self.assertFalse(reg["public_enabled"])
        self.assertFalse(reg["ai_enabled"])
        self.assertTrue(reg["evidence_binding"].startswith(
            "pending_phase1_registration"))

    def test_output_contract_has_no_names_or_verdicts(self) -> None:
        outputs = adj.SLICE_SPEC["outputs"]
        self.assertIsNone(outputs["names"])
        self.assertEqual(outputs["naming_status"],
                         "conflict_unresolved_not_emitted")
        self.assertEqual(set(outputs),
                         {"directed_pairs", "group_configurations",
                          "self_punishments", "names", "naming_status",
                          "verdict_fields"})

    def test_concept_linkage_unchanged(self) -> None:
        link = adj.CONCEPT_LINKAGE
        self.assertEqual(link["concept_id"],
                         "bazi.concept.conflict_three_punishments")
        self.assertEqual(link["sealed_status"], "unresolved")
        self.assertEqual(link["executable_policy"],
                         "blocked_pending_school_resolution")
        self.assertFalse(link["adjudication_semantics_changed"])


class ReferenceResolutionTest(unittest.TestCase):
    def test_quote_references_resolve_publicly(self) -> None:
        sanxing_quotes = {q["id"]: q for q in cj.COLLATION_QUOTES}
        yh_quotes = {q["id"]: q for q in yh.YUANHAI_ZHENGGUAN_QUOTES}
        homes = {"bazi_sanming_juan2_sanxing_collation": sanxing_quotes,
                 "bazi_yuanhai_zhengguan": yh_quotes}
        self.assertEqual(len(adj.QUOTE_REFERENCES), 13)
        for ref in adj.QUOTE_REFERENCES:
            self.assertIn(ref["quote_id"], homes[ref["register"]],
                          ref["quote_id"])

    def test_pair_evidence_refs_resolve(self) -> None:
        valid = ({q["id"] for q in cj.COLLATION_QUOTES}
                 | {s["section_id"] for s in adj.SEALED_SECTION_PINS})
        for p in adj.DIRECTED_PAIR_TABLE:
            for r in p["evidence_refs"]:
                self.assertIn(r, valid, (p["actor"], p["target"], r))
        for g in adj.GROUP_TABLE["groups"]:
            for r in g["evidence_refs"]:
                self.assertIn(r, valid, (g["group_id"], r))


class PendingAndWiringTest(unittest.TestCase):
    def test_pending_items(self) -> None:
        items = adj.PENDING_ITEMS
        self.assertEqual([p["id"] for p in items],
                         ["B1", "B2", "B3", "B4", "B5"])
        by_id = {p["id"]: p for p in items}
        self.assertFalse(by_id["B1"]["needs_user_adjudication"])
        self.assertTrue(by_id["B2"]["needs_user_adjudication"])
        self.assertTrue(by_id["B5"]["needs_user_adjudication"])
        self.assertEqual(by_id["B2"]["pending_decision_id"], "P-D1")
        self.assertEqual(by_id["B5"]["pending_decision_id"], "P-D2")

    def test_zero_runtime_wiring(self) -> None:
        src = ROOT / "src" / "tianji_kb"
        offenders = []
        for path in src.rglob("*.py"):
            if path.name == "bazi_sanxing_fact_adjudication.py":
                continue
            text = path.read_text(encoding="utf-8")
            if ("bazi_sanxing_fact_adjudication" in text
                    or "sanxing-branch-fact-v1" in text
                    or "reviewed_branch_punishment_facts" in text):
                offenders.append(path.name)
        self.assertEqual(offenders, [])
        core = (src / "bazi_core.py").read_text(encoding="utf-8")
        self.assertNotIn("punish", core)
        self.assertNotIn("三刑", core)


if __name__ == "__main__":
    unittest.main()
