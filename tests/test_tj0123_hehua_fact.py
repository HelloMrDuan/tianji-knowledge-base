"""TJ-012.3 合化审源与事实层设计审定：公开结构测试。

本批是审定批：登记模块 ``bazi_hehua_fact_adjudication`` 为纯数据、
零函数、不被任何可执行路径 import；本测试只钉登记形制与审定红线
（盘点计数、表述登记与 018-C 上游登记的交叉核对、逐对条件表与
妬合/妬化字集差异、条件矩阵、真冲突计数、逐项判定、
SLICE_SPEC=None、待裁定登记、零运行时接线、transformation_status
口径不变），不验证任何化气判定。引文对快照的逐字复核、密封侧
实测钉值复核与现行行为回归在密封专项
``tests/test_tj0123_hehua_fact_sealed.py``（仅离线验收，不进公开
CI）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_hehua_fact_adjudication as adj
from tianji_kb import bazi_sanming_juan2_hehua_collation as hc
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as j6

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0123_hehua_fact.json").read_text(
        encoding="utf-8"))

VERDICTS = {"fact_ready", "fact_ready_as_presence_only",
            "blocked_by_missing_layers",
            "blocked_by_formulation_conflict",
            "blocked_by_unresolved_token", "adjudication_required",
            "registered_absence", "consumer_not_unlocked",
            "prohibited"}
FORMULATION_IDS = ["F1", "F2", "F3", "F4", "F5", "F6", "HX"]


def _mirror():
    return {
        "meta": {
            "register_id": adj.HEHUA_ADJUDICATION_REGISTER["id"],
            "task": adj.HEHUA_ADJUDICATION_REGISTER["task"],
            "kind": adj.HEHUA_ADJUDICATION_REGISTER["kind"],
            "purpose": GOLDEN["meta"]["purpose"],
        },
        "headline_verdicts":
            adj.HEHUA_ADJUDICATION_REGISTER["headline_verdicts"],
        "inventory": [{"id": e["id"], "status": e["status"]}
                      for e in adj.SOURCE_INVENTORY],
        "formulations": [{"id": f["id"], "registered": f["registered"],
                          "status": f["status"]}
                         for f in adj.FORMULATION_REGISTER],
        "pair_conditions": adj.PAIR_CONDITION_TABLE,
        "condition_matrix": adj.CONDITION_MATRIX,
        "conflicts": {
            "true_conflicts": [
                {"id": c["id"], "element": c["element"],
                 "kind": c["kind"]}
                for c in adj.CONFLICT_ANALYSIS["true_conflicts"]],
            "detail_differences": [
                d["id"] for d in
                adj.CONFLICT_ANALYSIS[
                    "detail_differences_not_conflicts"]],
            "adjudication": adj.CONFLICT_ANALYSIS["adjudication"],
        },
        "layer_b_verdicts": [
            {"element": e["element"], "verdict": e["verdict"]}
            for e in adj.FACT_LAYER_AUDIT["layer_b_condition_elements"]],
        "proposition_verdicts": [
            {"id": p["id"], "verdict": p["verdict"]}
            for p in adj.PROPOSITION_AUDIT],
        "slice_spec": adj.SLICE_SPEC,
        "pending_items": [
            {"id": p["id"],
             "needs_user_adjudication": p["needs_user_adjudication"]}
            for p in adj.PENDING_ITEMS],
        "quote_references": adj.QUOTE_REFERENCES,
        "sealed_pins": adj.SEALED_PINS,
        "sealed_measurements": adj.SEALED_MEASUREMENTS,
    }


class RegisterFormTest(unittest.TestCase):
    def test_module_is_pure_data(self) -> None:
        funcs = [n for n, o in inspect.getmembers(adj)
                 if inspect.isfunction(o) or inspect.isclass(o)]
        self.assertEqual(funcs, [])

    def test_register_identity(self) -> None:
        reg = adj.HEHUA_ADJUDICATION_REGISTER
        self.assertEqual(reg["id"], "bazi-hehua-fact-adjudication-v1")
        self.assertEqual(reg["task"], "TJ-012.3")
        self.assertEqual(reg["baseline"]["ledger_event"], "E0270")
        self.assertEqual(reg["baseline"]["ledger_events_before"], 269)
        hv = reg["headline_verdicts"]
        self.assertEqual(hv["registered_formulations"], 4)
        self.assertEqual(hv["unregistered_formulations"], 2)
        self.assertEqual(hv["pairs"], 5)
        self.assertEqual(hv["condition_elements"], 11)
        self.assertEqual(hv["true_conflicts"], 4)
        self.assertEqual(hv["propositions"], 18)
        self.assertIsNone(hv["slice_spec"])
        self.assertFalse(hv["implementation_in_this_batch"])
        self.assertFalse(hv["formulation_adjudicated"])
        self.assertFalse(hv["transformation_status_changed"])

    def test_module_matches_golden(self) -> None:
        self.assertEqual(_mirror(), GOLDEN)


class InventoryTest(unittest.TestCase):
    def test_inventory_shape(self) -> None:
        inv = adj.SOURCE_INVENTORY
        self.assertEqual(len(inv), 16)
        self.assertEqual([e["id"] for e in inv],
                         [f"inv-{i:02d}" for i in range(1, 17)])
        for e in inv:
            for key in ("material", "source_id", "registered_at",
                        "locator", "counts", "status", "note"):
                self.assertIn(key, e, e["id"])

    def test_upstream_018c_counts(self) -> None:
        inv01 = adj.SOURCE_INVENTORY[0]
        self.assertEqual(inv01["counts"]["collation_notes"],
                         len(hc.COLLATION_NOTES))
        self.assertEqual(len(hc.COLLATION_NOTES), 81)
        self.assertEqual(inv01["counts"]["quotes"],
                         len(hc.COLLATION_QUOTES))
        self.assertEqual(len(hc.COLLATION_QUOTES), 34)

    def test_upstream_conflict_still_unadjudicated(self) -> None:
        variants = hc.HEHUA_CONDITION_VARIANTS
        self.assertEqual(variants["status"], "conflict")
        self.assertIsNone(variants["adjudication"])
        self.assertEqual(len(variants["branches"]), 4)
        self.assertEqual(
            adj.STATUS_QUO_LINKAGE["hehua_condition_variants_upstream"]
            ["status"], "conflict")
        self.assertIsNone(
            adj.STATUS_QUO_LINKAGE["hehua_condition_variants_upstream"]
            ["adjudication"])
        self.assertFalse(
            adj.STATUS_QUO_LINKAGE["adjudication_semantics_changed"])
        self.assertFalse(hc.HEHUA_FACT_LINKAGE[
            "adjudication_semantics_changed"])


class FormulationTest(unittest.TestCase):
    def test_formulation_register_shape(self) -> None:
        forms = adj.FORMULATION_REGISTER
        self.assertEqual([f["id"] for f in forms], FORMULATION_IDS)
        registered = [f["id"] for f in forms if f["registered"]]
        self.assertEqual(registered, ["F1", "F2", "F3", "F4", "HX"])
        unregistered = [f["id"] for f in forms if not f["registered"]]
        self.assertEqual(unregistered, ["F5", "F6"])
        for f in forms:
            if not f["registered"]:
                self.assertEqual(f["evidence_quotes"], [])

    def test_pair_table_matches_upstream_variants(self) -> None:
        branch = next(b for b in hc.HEHUA_CONDITION_VARIANTS["branches"]
                      if b["branch_id"] == "prose-month-conditions")
        upstream = branch["pairs"]
        self.assertEqual(len(adj.PAIR_CONDITION_TABLE), 5)
        for row in adj.PAIR_CONDITION_TABLE:
            key = "甲巳" if row["pair"] == "甲己" else row["pair"]
            up = upstream[key]
            self.assertEqual(up["pair_reading"], row["pair"])
            self.assertEqual(up["element"], row["element"])
            self.assertEqual(up["secondary"], row["secondary_months"])
            self.assertEqual(up["blocker"], row["blocker_stem_f1"])
            self.assertEqual(up["condition_quote"],
                             row["condition_quote"])
            if row["pair"] == "戊癸":
                self.assertEqual(up["primary_as_transmitted"],
                                 row["primary_as_transmitted"])
                self.assertEqual(up["primary_months_resolved"],
                                 row["primary_months"])
                self.assertEqual(up["primary_unresolved_token"],
                                 row["primary_unresolved_token"])
            else:
                self.assertEqual(up["primary"], row["primary_months"])

    def test_duhua_stems_against_quote_text(self) -> None:
        quotes = {q["id"]: q for q in hc.COLLATION_QUOTES}
        duhua = (quotes["smhq.duhua"].get("mapped_reading")
                 or quotes["smhq.duhua"]["quote"])
        for row in adj.PAIR_CONDITION_TABLE:
            self.assertIn(
                f"{row['pair']}见{row['blocker_stem_f3_duhua']}",
                duhua, row["pair"])
        erzehua = (quotes["smhq.erzehua"].get("mapped_reading")
                   or quotes["smhq.erzehua"]["quote"])
        self.assertIn("有二则化", erzehua)
        self.assertIn("甲己", erzehua)

    def test_blocker_sets_differ_for_exactly_three_pairs(self) -> None:
        differ = [r["pair"] for r in adj.PAIR_CONDITION_TABLE
                  if r["blocker_stem_f1"] != r["blocker_stem_f3_duhua"]]
        self.assertEqual(differ, ["甲己", "乙庚", "戊癸"])
        same = [r["pair"] for r in adj.PAIR_CONDITION_TABLE
                if r["blocker_stem_f1"] == r["blocker_stem_f3_duhua"]]
        self.assertEqual(same, ["丙辛", "丁壬"])

    def test_divergence_numbers_pinned_upstream(self) -> None:
        branch = next(b for b in hc.HEHUA_CONDITION_VARIANTS["branches"]
                      if b["branch_id"] == "monthly-table-states")
        div = branch["divergence"]
        self.assertEqual(
            div["甲巳"]["prose_required_but_table_not_transform"],
            [3, 5, 6])
        self.assertEqual(
            div["甲巳"]["table_transform_but_prose_not_required"],
            [7, 11])
        self.assertEqual(
            div["戊癸"]["prose_required_but_table_not_transform"], [5])
        self.assertEqual(
            div["戊癸"]["table_transform_but_prose_not_required"],
            [1, 2, 3, 12])
        self.assertEqual(hc.HENGKAN_TABLE_INTEGRITY["cell_count"], 120)
        self.assertEqual(len(hc.HENGKAN_TABLE_INTEGRITY["rows"]), 10)


class ConditionMatrixTest(unittest.TestCase):
    def test_matrix_shape(self) -> None:
        matrix = adj.CONDITION_MATRIX
        self.assertEqual(len(matrix["elements"]), 11)
        self.assertEqual(set(matrix["rows"]),
                         set(matrix["elements"]))
        for element in matrix["elements"]:
            row = matrix["rows"][element]
            for fid in FORMULATION_IDS:
                self.assertIn(fid, row, (element, fid))

    def test_commander_absent_everywhere(self) -> None:
        row = adj.CONDITION_MATRIX["rows"]["commander"]
        for fid in FORMULATION_IDS:
            self.assertEqual(row[fid], "absent", fid)
        self.assertIn("note", row)

    def test_result_element_conflict_row(self) -> None:
        row = adj.CONDITION_MATRIX["rows"]["result_element"]
        self.assertIn("化他元素", row["F4"])
        for fid in ("F1", "F2", "F3", "F5", "F6"):
            self.assertIn("名册固定", row[fid], fid)


class ConflictAnalysisTest(unittest.TestCase):
    def test_true_conflicts(self) -> None:
        conflicts = adj.CONFLICT_ANALYSIS["true_conflicts"]
        self.assertEqual([c["id"] for c in conflicts],
                         ["C1", "C2", "C3", "C4", "C5"])
        registered = [c for c in conflicts
                      if "unregistered" not in c["kind"]]
        self.assertEqual(len(registered), 4)
        self.assertIsNone(adj.CONFLICT_ANALYSIS["adjudication"])
        details = [d["id"] for d in adj.CONFLICT_ANALYSIS[
            "detail_differences_not_conflicts"]]
        self.assertEqual(details, ["D1", "D2", "D3", "D4", "D5"])


class PropositionAuditTest(unittest.TestCase):
    def test_rows_and_verdicts(self) -> None:
        rows = adj.PROPOSITION_AUDIT
        self.assertEqual([p["id"] for p in rows],
                         [f"P{i}" for i in range(1, 19)])
        for p in rows:
            self.assertIn(p["verdict"], VERDICTS, p["id"])
            self.assertTrue(p["basis"])
            self.assertTrue(p["enters"])
        by_id = {p["id"]: p for p in rows}
        self.assertEqual(by_id["P1"]["verdict"], "fact_ready")
        self.assertEqual(by_id["P2"]["verdict"], "fact_ready")
        self.assertEqual(by_id["P5"]["verdict"],
                         "blocked_by_unresolved_token")
        self.assertEqual(by_id["P8"]["verdict"],
                         "blocked_by_formulation_conflict")
        self.assertEqual(by_id["P12"]["verdict"],
                         "blocked_by_missing_layers")
        self.assertEqual(by_id["P14"]["verdict"], "registered_absence")
        self.assertEqual(by_id["P16"]["verdict"],
                         "adjudication_required")
        self.assertEqual(by_id["P18"]["verdict"], "prohibited")
        presence = [p["id"] for p in rows
                    if p["verdict"] == "fact_ready_as_presence_only"]
        self.assertEqual(presence,
                         ["P3", "P6", "P7", "P9", "P10", "P11"])

    def test_layer_b_matches_propositions(self) -> None:
        layer_b = adj.FACT_LAYER_AUDIT["layer_b_condition_elements"]
        self.assertEqual(len(layer_b), 13)
        for e in layer_b:
            self.assertIn(e["verdict"], VERDICTS, e["element"])
        self.assertEqual(
            adj.FACT_LAYER_AUDIT["layer_c_transformation_verdict"]
            ["status"], "adjudication_layer_not_fact")


class SliceAndPendingTest(unittest.TestCase):
    def test_slice_spec_is_none_with_decision(self) -> None:
        self.assertIsNone(adj.SLICE_SPEC)
        decision = adj.SLICE_DECISION
        self.assertEqual(decision["decision"], "no_fact_layer_slice")
        self.assertTrue(decision["rationale"])
        self.assertTrue(decision["fallback"])

    def test_pending_items(self) -> None:
        items = adj.PENDING_ITEMS
        self.assertEqual([p["id"] for p in items],
                         ["B1", "B2", "B3", "B4", "B5", "B6"])
        by_id = {p["id"]: p for p in items}
        self.assertTrue(by_id["B1"]["needs_user_adjudication"])
        self.assertEqual(by_id["B1"]["pending_decision_id"], "P-D1")
        self.assertTrue(by_id["B5"]["needs_user_adjudication"])
        self.assertEqual(by_id["B5"]["pending_decision_id"], "P-D2")
        for bid in ("B2", "B3", "B4", "B6"):
            self.assertFalse(by_id[bid]["needs_user_adjudication"], bid)


class ReferenceResolutionTest(unittest.TestCase):
    def test_quote_references_resolve_publicly(self) -> None:
        homes = {
            "bazi_sanming_juan2_hehua_collation":
                {q["id"]: q for q in hc.COLLATION_QUOTES},
            "bazi_sanming_juan6_fangju_baxiang_collation":
                {q["id"]: q for q in j6.COLLATION_QUOTES},
        }
        self.assertEqual(len(adj.QUOTE_REFERENCES), 16)
        for ref in adj.QUOTE_REFERENCES:
            self.assertIn(ref["quote_id"], homes[ref["register"]],
                          ref["quote_id"])

    def test_formulation_evidence_refs_resolve(self) -> None:
        valid = ({q["id"] for q in hc.COLLATION_QUOTES}
                 | {q["id"] for q in j6.COLLATION_QUOTES})
        for f in adj.FORMULATION_REGISTER:
            for qid in f["evidence_quotes"]:
                self.assertIn(qid, valid, (f["id"], qid))


class WiringTest(unittest.TestCase):
    def test_zero_runtime_wiring(self) -> None:
        src = ROOT / "src" / "tianji_kb"
        offenders = []
        for path in src.rglob("*.py"):
            if path.name == "bazi_hehua_fact_adjudication.py":
                continue
            text = path.read_text(encoding="utf-8")
            if ("bazi_hehua_fact_adjudication" in text
                    or "bazi-hehua-fact-adjudication-v1" in text):
                offenders.append(path.name)
        self.assertEqual(offenders, [])

    def test_transformation_status_wording_unchanged(self) -> None:
        text = (ROOT / "src" / "tianji_kb" / "bazi_action_conditions.py"
                ).read_text(encoding="utf-8")
        self.assertIn("'transformation_status': 'unresolved' if any(",
                      text)
        self.assertIn("'stem_erasure_applied': False", text)


if __name__ == "__main__":
    unittest.main()
