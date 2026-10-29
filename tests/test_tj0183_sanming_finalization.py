"""TJ-018.3 晋级 P1 终局化登记册公开结构测试（不依赖密封资产）。

只核对登记册自身的形制、计数自洽与与既有公开登记册（重锚、
应用记录）的交叉一致；S3 逐字核验与应用报告 origin 图对账在
密封专项 ``test_tj0183_sanming_finalization_sealed`` 中对密封
原文执行。
"""
from __future__ import annotations

import ast
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_application_record as ar
from tianji_kb import bazi_sanming_finalization as fin
from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
REG = fin.FINALIZATION_REGISTER
ENTRIES = REG["entries"]
RE = {e["seq"]: e for e in ra.REANCHOR_REGISTER["entries"]}
HIST_REPOS = {"kanripo/KR3g0042", "mikkokotila/Sanming-Tongshui"}


class TestFinalizationPublic(unittest.TestCase):
    def test_golden_mirror(self):
        golden = json.loads(
            (ROOT / "tests" / "golden_tj0183_sanming_finalization.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(golden, REG)

    def test_register_is_pure_data(self):
        tree = ast.parse(Path(fin.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        self.assertEqual(REG["ledger_event"], "E0300")
        self.assertEqual(REG["ledger_row"], "TJ-018.2")
        self.assertEqual(
            REG["baseline_main_sha"],
            "a2a40c2e5ed961a0997dba0207089a859f904728")
        self.assertEqual(
            REG["register_id"],
            "sanming-ocr-candidates-finalization-register-v1")

    def test_stage_pins(self):
        inp = REG["inputs"]
        self.assertEqual(inp["snapshot"]["sha256"],
                         "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111"
                         "e62b59378010c86")
        self.assertEqual(inp["snapshot"]["chars"], 461157)
        self.assertEqual(inp["basis_text"]["sha256"],
                         "db8618c9cdbc545b59149f7550644a440fdf8bba8ddbe0e23b6"
                         "15029f8a896d9")
        self.assertEqual(inp["applied_text"]["sha256"],
                         "a89c0b5da16ea4e07dc85180c49135ed280875318059f"
                         "923ff7154f2c217662f")
        self.assertEqual(inp["applied_text"]["chars"], 461156)
        self.assertEqual(inp["applied_text"]["bytes"], 1342682)
        # 与应用记录登记册的产物登记交叉一致
        self.assertEqual(ar.PRODUCTS["applied_text"]["sha256"],
                         inp["applied_text"]["sha256"])
        self.assertEqual(ar.PRODUCTS["applied_text"]["bytes"],
                         inp["applied_text"]["bytes"])
        self.assertEqual(inp["candidates_file"]["sha256"],
                         ra.REANCHOR_REGISTER["candidates_file"]["sha256"])
        self.assertEqual(inp["basis_text"]["sha256"],
                         ra.REANCHOR_REGISTER["basis_text"]["sha256"])

    def test_total_and_selection(self):
        self.assertEqual(len(ENTRIES), 822)
        expected = sorted(
            seq for seq, e in RE.items()
            if e["status"] in ("variant_preserve", "historical_only_hold"))
        self.assertEqual([e["seq"] for e in ENTRIES], expected)
        self.assertEqual(Counter(e["status"] for e in ENTRIES),
                         Counter({"historical_only_hold": 775,
                                  "variant_preserve": 47}))
        self.assertEqual(REG["summary"]["total"], 822)

    def test_reconciliation_two_dimensions(self):
        rec = REG["reconciliation"]
        sd = rec["status_dimension"]
        self.assertEqual(sd["this_batch"]["subtotal"], 822)
        self.assertEqual(
            sd["this_batch"]["historical_only_hold"]
            + sd["this_batch"]["variant_preserve"]
            + sd["closed_by_application_batch_E0298"]["confirmed_applied"]
            + sd["pending_P3"]["reading_disagreement_hold"],
            sd["total"])
        self.assertEqual(sd["total"], 993)
        self.assertEqual(
            ar.CANDIDATE_ANNEX_SUMMARY["by_status"],
            {"historical_only_hold": 775, "variant_preserve": 47,
             "confirmed_applied": 159, "reading_disagreement_hold": 12})
        cd = rec["carry_dimension"]
        self.assertEqual(sum(cd["by_status"].values()),
                         cd["context_crosses_boundary_total"])
        self.assertEqual(cd["context_crosses_boundary_total"], 76)
        self.assertEqual(cd["in_this_batch"], 46)
        self.assertTrue(cd["orthogonal_to_status_dimension"])
        # 正交维度禁止混算的错账形态必须不成立于本登记册口径
        self.assertNotEqual(159 + 76 + 822 + 12, 993)

    def test_entries_match_reanchor(self):
        for e in ENTRIES:
            r = RE[e["seq"]]
            self.assertEqual(e["volume"], r["volume"], e["seq"])
            self.assertEqual(e["status"], r["status"], e["seq"])
            self.assertEqual(e["site_s2"], r["basis_offset"], e["seq"])
            self.assertEqual(e["s2_reading"], r["old"], e["seq"])
            self.assertEqual(e["historical_reading"],
                             r["historical_reading"], e["seq"])
            self.assertEqual(e["site_in_context"], r["site_in_context"],
                             e["seq"])
            self.assertEqual(e["context_span_s2"], r["context_span_basis"],
                             e["seq"])
            self.assertEqual(e["context_s2_sha256"], r["context_sha256"],
                             e["seq"])
            self.assertEqual(e["site_anchor_class"], r["site_anchor_class"],
                             e["seq"])
            self.assertEqual(e["site_snapshot_span"], r["site_snapshot_span"],
                             e["seq"])
            self.assertEqual(e["context_anchor_class"],
                             r["context_anchor_class"], e["seq"])
            self.assertEqual(e["context_snapshot_span"],
                             r["context_snapshot_span"], e["seq"])

    def test_s3_coordinate_shape(self):
        for e in ENTRIES:
            self.assertTrue(0 <= e["site_s3"] < 461156, e["seq"])
            cs, ce = e["context_span_s3"]
            self.assertEqual(ce - cs,
                             e["context_span_s2"][1] - e["context_span_s2"][0],
                             e["seq"])
            self.assertEqual(cs, e["site_s3"] - e["site_in_context"],
                             e["seq"])
            self.assertTrue(0 <= cs < ce <= 461156, e["seq"])
            self.assertEqual(len(e["s3_reading"]), len(e["s2_reading"]),
                             e["seq"])
            self.assertRegex(e["context_s3_sha256"], r"^[0-9a-f]{64}$")

    def test_readings_strictly_separated(self):
        for e in ENTRIES:
            # S3 现读与 S2 基线读法逐条相同是实测结论，不是定义
            self.assertEqual(e["s3_reading"], e["s2_reading"], e["seq"])
            # 历史读法与现读严格分栏：逐条必异（否则无候选可言）
            self.assertNotEqual(e["historical_reading"], e["s3_reading"],
                                e["seq"])
            if e["status"] == "variant_preserve":
                self.assertEqual(e["registration_kind"], "variant_parallel",
                                 e["seq"])
            else:
                self.assertEqual(e["registration_kind"],
                                 "historical_location", e["seq"])
        self.assertEqual(REG["summary"]["s3_reading_equals_s2_reading"], 822)

    def test_witnesses(self):
        total_cross = 0
        for e in ENTRIES:
            hw = e["historical_witnesses"]
            self.assertEqual(len(hw), 2, e["seq"])
            self.assertEqual({w["repo"] for w in hw}, HIST_REPOS, e["seq"])
            for w in hw:
                self.assertRegex(w["commit"], r"^[0-9a-f]{40}$")
                self.assertTrue(w["anchor"], e["seq"])
            total_cross += len(e["crosscheck_witnesses"])
            if e["status"] == "variant_preserve":
                self.assertTrue(e["crosscheck_witnesses"], e["seq"])
                for w in e["crosscheck_witnesses"]:
                    self.assertIn("observed", w, e["seq"])
            else:
                self.assertEqual(e["crosscheck_witnesses"], [], e["seq"])
        self.assertEqual(total_cross, 52)
        self.assertEqual(REG["summary"]["crosscheck_witness_records"], 52)
        self.assertEqual(
            REG["summary"]["crosscheck_witness_repos"],
            {"michiboo/Classical_Chinese_Wikisource": 30,
             "NiuTrans/Classical-Modern": 6, "youngzs/xuanxue": 16})

    def test_carry_overlap_flags(self):
        flagged = [e for e in ENTRIES if e["in_context_carry_76"]]
        self.assertEqual(len(flagged), 46)
        self.assertEqual(Counter(e["status"] for e in flagged),
                         Counter({"historical_only_hold": 40,
                                  "variant_preserve": 6}))
        # 与重锚登记册的跨界类别逐条对应（同一维度的两种表述）
        for e in ENTRIES:
            self.assertEqual(
                e["in_context_carry_76"],
                e["context_anchor_class"] == "unanchorable_crosses_boundary",
                e["seq"])

    def test_summary_consistency(self):
        s = REG["summary"]
        self.assertEqual(s["site_anchor_counts"],
                         dict(Counter(e["site_anchor_class"]
                                      for e in ENTRIES)))
        self.assertEqual(s["context_anchor_counts"],
                         dict(Counter(e["context_anchor_class"]
                                      for e in ENTRIES)))
        self.assertEqual(s["historical_witness_records"],
                         sum(len(e["historical_witnesses"]) for e in ENTRIES))
        self.assertEqual(s["in_context_carry_76"], 46)
        self.assertFalse(REG["posture"]["canonical_ready"])
        self.assertTrue(REG["posture"]["candidates_file_untouched"])


if __name__ == "__main__":
    unittest.main()
