"""TJ-018.3 晋级 P2 残余「防」处置登记册公开结构测试（不依赖密封资产）。

只核对登记册自身的形制、盘点完备性、分类计数对账、处置规则
与与既有公开登记册（应用记录）的交叉一致；769 位点对密封
原文的全量复核与密封文件逐字未动验证在密封专项
``test_tj0183_sanming_fang_disposition_sealed`` 中执行。
"""
from __future__ import annotations

import ast
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_application_record as ar
from tianji_kb import bazi_sanming_fang_disposition as fd

ROOT = Path(__file__).resolve().parents[1]
REG = fd.FANG_DISPOSITION_REGISTER
INV = REG["inventory"]
DISP = REG["dispositions"]
SIKU = {"kanripo/KR3g0042", "mikkokotila/Sanming-Tongshui"}
MODERN = {"NiuTrans/Classical-Modern", "youngzs/xuanxue"}
ALL_WIT = SIKU | MODERN | {"Banny-Gao"}


class TestFangDispositionPublic(unittest.TestCase):
    def test_golden_mirror(self):
        golden = json.loads(
            (ROOT / "tests" / "golden_tj0183_sanming_fang_disposition.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(golden, REG)

    def test_register_is_pure_data(self):
        tree = ast.parse(Path(fd.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        self.assertEqual(REG["ledger_event"], "E0302")
        self.assertEqual(REG["ledger_row"], "TJ-018.2")
        self.assertEqual(
            REG["baseline_main_sha"],
            "6c11a168430ebf7a16f7ce5d591d07dc47b9f18c")
        self.assertEqual(
            REG["register_id"],
            "sanming-residual-fang-disposition-register-v1")

    def test_input_pins_cross_checked(self):
        inp = REG["inputs"]
        self.assertEqual(inp["snapshot"]["sha256"],
                         "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111"
                         "e62b59378010c86")
        self.assertEqual(inp["snapshot"]["chars"], 461157)
        self.assertEqual(inp["applied_text"]["sha256"],
                         ar.PRODUCTS["applied_text"]["sha256"])
        self.assertEqual(inp["applied_text"]["bytes"],
                         ar.PRODUCTS["applied_text"]["bytes"])
        self.assertEqual(inp["application_report"]["file_sha256"],
                         ar.PRODUCTS["application_report"]["file_sha256"])
        self.assertEqual(inp["snapshot_manifest"]["file_count"], 237)
        self.assertEqual(inp["snapshot_manifest"]["total_bytes"], 15883200)
        self.assertEqual(
            inp["snapshot_manifest"]["manifest_sha256"],
            "5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180dc454ea874cbc")
        # 残余扫描与应用记录登记册同值
        self.assertEqual(ar.RESIDUAL_SCAN["fang"], 769)
        self.assertEqual(REG["summary"]["total_residual_fang_s3"],
                         ar.RESIDUAL_SCAN["fang"])

    def test_categories_defined(self):
        self.assertEqual(set(REG["categories"]),
                         {"disposed_confirmed", "disposed_kept",
                          "disposed_parallel", "deferred_no_witness",
                          "pending_later_tranche"})
        for text in REG["categories"].values():
            self.assertTrue(text)

    def test_inventory_completeness(self):
        self.assertEqual(len(INV), 769)
        self.assertEqual([x["seq"] for x in INV], list(range(1, 770)))
        s3s = [x["s3_offset"] for x in INV]
        self.assertEqual(s3s, sorted(s3s))
        self.assertEqual(len(set(s3s)), 769)
        self.assertTrue(all(0 <= o < 461156 for o in s3s))
        for x in INV:
            # ±6 语境；全文末尾的位点（s3 461151）语境被文本
            # 末端截断为 11 字，位点仍在索引 6
            self.assertTrue(11 <= len(x["context_s3"]) <= 13)
            self.assertEqual(x["context_s3"][6], "防")
            self.assertRegex(x["context_s3_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(x["origin_kind"] == "identity"
                            or x["origin_kind"].startswith("correction:"))
        self.assertEqual(
            Counter(x["origin_kind"].split(":")[0] for x in INV),
            Counter({"identity": 739, "correction": 30}))
        self.assertEqual(sum(1 for x in INV if x["candidate_site"]), 518)
        rd = sorted(x["rd12_seq"] for x in INV if x["rd12_seq"])
        self.assertEqual(rd, [361, 385, 450, 612, 616, 824, 873, 933])

    def test_summary_reconciliation(self):
        s = REG["summary"]
        counts = Counter(x["disposition"] for x in INV)
        self.assertEqual(counts["disposed_confirmed"],
                         s["disposed_confirmed"])
        self.assertEqual(counts["disposed_kept"], s["disposed_kept"])
        self.assertEqual(counts["disposed_parallel"],
                         s["disposed_parallel"])
        self.assertEqual(counts["deferred_no_witness"],
                         s["deferred_no_witness"])
        self.assertEqual(counts["pending_later_tranche"],
                         s["pending_later_tranche"])
        self.assertEqual(s["disposed_total"],
                         s["disposed_confirmed"] + s["disposed_kept"]
                         + s["disposed_parallel"])
        self.assertEqual(s["disposed_total"], 14)
        self.assertEqual(s["disposed_total"] + s["deferred_no_witness"]
                         + s["pending_later_tranche"], 769)
        self.assertEqual(s["cumulative_disposed_fraction"], "14/769")
        self.assertEqual(s["in_registered_sections"], 43)
        self.assertEqual(s["inventory_rows_with_collation_note"], 40)
        self.assertEqual(s["rd12_sites_in_inventory"], 8)
        self.assertEqual(s["rd12_sites_in_pending_tranches"], 7)

    def test_dispositions_cover_registered_sections(self):
        in_section = {x["s0_offset"] for x in INV
                      if x["section_id"] is not None}
        self.assertEqual(len(in_section), 43)
        self.assertEqual({d["s0_offset"] for d in DISP}, in_section)
        by_s0 = {x["s0_offset"]: x for x in INV}
        for d in DISP:
            row = by_s0[d["s0_offset"]]
            self.assertEqual(row["disposition"], d["category"])
            self.assertEqual(row["s3_offset"], d["s3_offset"])
            self.assertEqual(row["section_id"], d["section_id"])
            self.assertEqual(row["collation_note_id"],
                             d["collation_note_id"])
        noted = [d for d in DISP if d["collation_note_id"]]
        self.assertEqual(len(noted), 40)
        self.assertEqual(
            sorted(d["s0_offset"] for d in DISP
                   if not d["collation_note_id"]),
            [49021, 58542, 76988])

    def test_witness_evidence_shape(self):
        for d in DISP:
            ev = d["witness_evidence"]
            self.assertEqual({e["witness"] for e in ev}, ALL_WIT,
                             d["s0_offset"])
            for e in ev:
                if e["witness"] in SIKU:
                    # 四库两家 43/43 必须在位点定位（定案的证据基座）
                    self.assertEqual(e["attestation"], "attested",
                                     d["s0_offset"])
                    self.assertTrue(e["quote_short"], d["s0_offset"])
                    self.assertTrue(e["locator"], d["s0_offset"])

    def test_confirmed_rule(self):
        conf = [d for d in DISP if d["category"] == "disposed_confirmed"]
        self.assertEqual(len(conf), 9)
        for d in conf:
            # 定案读法与校勘候选一致，且登记为未来应用候选
            self.assertTrue(d["reading_glyph"])
            self.assertTrue(d["reading_word"])
            self.assertEqual(d["candidate_reading_glyph"],
                             d["reading_glyph"])
            self.assertEqual(d["candidate_reading_word"],
                             d["reading_word"])
            self.assertNotEqual(d["reading_word"], "防")
            siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                             if e["witness"] in SIKU}
            self.assertEqual(siku_readings, {d["reading_glyph"]})
            modern_ok = [e for e in d["witness_evidence"]
                         if e["witness"] in MODERN
                         and e["attestation"] in ("attested",
                                                  "attested_title")
                         and e["site_reading"] in (d["reading_word"],
                                                   d["reading_word_simplified"])]
            self.assertTrue(modern_ok, d["s0_offset"])
            rivals = [e for e in d["witness_evidence"]
                      if e["witness"] in MODERN
                      and e["attestation"] == "rival"]
            self.assertEqual(rivals, [], d["s0_offset"])

    def test_kept_rule(self):
        kept = [d for d in DISP if d["category"] == "disposed_kept"]
        self.assertEqual(len(kept), 4)
        for d in kept:
            self.assertEqual(d["reading_glyph"], "防")
            self.assertEqual(d["reading_word"], "防")
            siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                             if e["witness"] in SIKU}
            self.assertEqual(siku_readings, {"防"})

    def test_parallel_rule(self):
        par = [d for d in DISP if d["category"] == "disposed_parallel"]
        self.assertEqual(len(par), 1)
        d = par[0]
        self.assertEqual(d["s0_offset"], 73703)
        siku_readings = {e["site_reading"] for e in d["witness_evidence"]
                         if e["witness"] in SIKU}
        self.assertEqual(siku_readings, {"㸔"})
        omitted = [e for e in d["witness_evidence"]
                   if e["witness"] in MODERN
                   and e["attestation"] == "word_omitted_at_locus"]
        self.assertEqual(len(omitted), 2)

    def test_deferred_rule(self):
        deferred = [d for d in DISP
                    if d["category"] == "deferred_no_witness"]
        self.assertEqual(len(deferred), 29)
        for d in deferred:
            # deferred 不得登记定案读法（校勘候选只在 candidate 栏）
            self.assertIsNone(d["reading_glyph"])
            self.assertIsNone(d["reading_word"])
        rd = [d for d in deferred if d.get("rd12_seq")]
        self.assertEqual(len(rd), 1)
        self.assertEqual(rd[0]["s0_offset"], 184318)
        self.assertEqual(rd[0]["rd12_seq"], 450)
        self.assertEqual(rd[0]["defer_reason"],
                         "reading_disagreement_rd12_p3_scope")
        # RD-12 双方证据在案：四库䕶 vs 现代获
        ev = {e["witness"]: e for e in rd[0]["witness_evidence"]}
        self.assertEqual(ev["kanripo/KR3g0042"]["site_reading"], "䕶")
        self.assertEqual(
            ev["NiuTrans/Classical-Modern"]["attestation"], "rival")
        self.assertEqual(
            ev["NiuTrans/Classical-Modern"]["site_reading"], "获")

    def test_tranche_plan(self):
        plan = REG["tranche_plan"]
        self.assertEqual(plan["disposed_cumulative"], "14/769")
        self.assertEqual(plan["deferred_in_registered_sections"], 29)
        self.assertEqual(sum(t["pending"]
                             for t in plan["pending_by_volume"]), 726)
        computed = Counter(x["volume"] for x in INV
                           if x["disposition"] == "pending_later_tranche")
        self.assertEqual({t["volume"]: t["pending"]
                          for t in plan["pending_by_volume"]},
                         dict(computed))

    def test_immutability_statement(self):
        self.assertIn("零文本改动", REG["immutability"])
        self.assertIn("canonical_ready 保持 false", REG["immutability"])


if __name__ == "__main__":
    unittest.main()
