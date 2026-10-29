"""TJ-018.3 晋级 P3 RD-12 互校登记册公开结构测试（不依赖密封资产）。

只核对登记册自身的形制、计数自洽与与既有公开登记册（设计、
重锚、终局化、残余防处置）的交叉一致；S2/S3 逐字核验与应用
报告对账在密封专项 ``test_tj0183_sanming_rd12_collation_sealed``
中对密封原文执行。
"""
from __future__ import annotations

import ast
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_fang_disposition as fd
from tianji_kb import bazi_sanming_finalization as fin
from tianji_kb import bazi_sanming_formal_application as fa
from tianji_kb import bazi_sanming_rd12_collation as rd
from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
REG = rd.RD12_COLLATION_REGISTER
ENTRIES = REG["entries"]
BY_SEQ = {e["seq"]: e for e in ENTRIES}
RE = {e["seq"]: e for e in ra.REANCHOR_REGISTER["entries"]}
DESIGN = {d["seq"]: d for d in fa.READING_DISAGREEMENT_SPEC["items"]}
FANG_SEQS = [361, 385, 450, 612, 616, 824, 873, 933]
PENDING7 = [361, 385, 612, 616, 824, 873, 933]
SIKU_REPOS = {"kanripo/KR3g0042", "mikkokotila/Sanming-Tongshui"}


class TestRd12CollationPublic(unittest.TestCase):
    def test_golden_mirror(self):
        golden = json.loads(
            (ROOT / "tests" / "golden_tj0183_sanming_rd12_collation.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(golden, REG)

    def test_register_is_pure_data(self):
        tree = ast.parse(Path(rd.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        self.assertEqual(REG["ledger_event"], "E0324")
        self.assertEqual(REG["ledger_row"], "TJ-018.2")
        self.assertEqual(
            REG["baseline_main_sha"],
            "9c42339048ec716a313541a3b68fc61a4543d6db")
        self.assertEqual(
            REG["register_id"],
            "sanming-reading-disagreement-collation-register-v1")

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
        self.assertEqual(inp["candidates_file"]["sha256"],
                         "4209b85d003d07ca696e298c3f446c43ea8a8d6871dfe73e52"
                         "fc7c17a16d211c")
        self.assertEqual(inp["application_report"]["file_sha256"],
                         "691ccb60b61534f60024843a5a5e692aa70d967c5a1939"
                         "d70c2e8814d23e914b")
        self.assertEqual(inp["snapshot_manifest"]["files"], 237)
        self.assertEqual(inp["snapshot_manifest"]["bytes"], 15883200)
        self.assertEqual(inp["snapshot_manifest"]["sha256"],
                         "5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180"
                         "dc454ea874cbc")
        # 与既有登记册的阶段钉交叉一致
        fin_inp = fin.FINALIZATION_REGISTER["inputs"]
        self.assertEqual(inp["snapshot"]["sha256"],
                         fin_inp["snapshot"]["sha256"])
        self.assertEqual(inp["basis_text"]["sha256"],
                         fin_inp["basis_text"]["sha256"])
        self.assertEqual(inp["applied_text"]["sha256"],
                         fin_inp["applied_text"]["sha256"])
        self.assertEqual(inp["candidates_file"]["sha256"],
                         ra.REANCHOR_REGISTER["candidates_file"]["sha256"])

    def test_selection_completeness(self):
        # 选集完备：本批 12 条 == 设计 spec 全集 == 重锚册 RD 状态全集
        self.assertEqual(len(ENTRIES), 12)
        self.assertEqual(sorted(BY_SEQ), sorted(DESIGN))
        rd_in_reanchor = sorted(
            seq for seq, e in RE.items()
            if e["status"] == "reading_disagreement_hold")
        self.assertEqual(sorted(BY_SEQ), rd_in_reanchor)
        # P1 状态维度对账：993 = 822 + 159 + 12
        self.assertEqual(len(fin.FINALIZATION_REGISTER["entries"]), 822)
        self.assertEqual(822 + 159 + len(ENTRIES), 993)
        self.assertEqual(
            Counter(e["volume"] for e in ENTRIES),
            Counter({5: 3, 7: 2, 10: 3, 11: 4}))
        self.assertEqual(
            Counter(e["snapshot_reading"] for e in ENTRIES),
            Counter({"防": 8, "着": 2, "胤": 1, "玄": 1}))

    def test_entries_align_design_and_reanchor(self):
        for seq, e in BY_SEQ.items():
            dsg, r = DESIGN[seq], RE[seq]
            self.assertEqual(e["volume"], dsg["volume"], seq)
            self.assertEqual(e["volume"], r["volume"], seq)
            self.assertEqual(e["site_s2"], dsg["basis_offset"], seq)
            self.assertEqual(e["site_s2"], r["basis_offset"], seq)
            self.assertEqual(e["site_s3"], e["site_s2"], seq)
            self.assertEqual(e["snapshot_reading"], dsg["old"], seq)
            self.assertEqual(e["snapshot_reading"], r["old"], seq)
            self.assertEqual(e["s3_reading"], dsg["old"], seq)
            self.assertEqual(e["siku_lineage"]["reading"],
                             dsg["historical_reading"], seq)
            self.assertEqual(e["siku_lineage"]["reading"],
                             r["historical_reading"], seq)
            self.assertEqual(e["context"], r["context"], seq)
            self.assertEqual(e["context_span_s2"], r["context_span_basis"],
                             seq)
            self.assertEqual(e["context_span_s3"], r["context_span_basis"],
                             seq)
            self.assertEqual(e["context_s2_sha256"], r["context_sha256"],
                             seq)
            self.assertEqual(e["context_s3_sha256"], r["context_sha256"],
                             seq)
            self.assertEqual(e["site_snapshot_span"],
                             r["site_snapshot_span"], seq)
            self.assertEqual(e["site_snapshot_span"][0], e["site_s2"] + 1,
                             seq)
            self.assertEqual(e["site_in_context"], r["site_in_context"], seq)
            self.assertEqual(e["context_anchor_class"],
                             r["context_anchor_class"], seq)
            self.assertEqual(e["site_anchor_class"], r["site_anchor_class"],
                             seq)
            self.assertEqual(e["context_edits_crossed"],
                             r["context_edits_crossed"], seq)
            self.assertEqual(e["status"], "reading_disagreement_hold", seq)
            # 候选记录见证原文逐字随行
            self.assertEqual(
                {w["repo"] for w in
                 e["candidate_record_evidence"]["historical_evidence"]},
                SIKU_REPOS, seq)

    def test_outcomes_all_parallel_no_adjudication(self):
        for e in ENTRIES:
            self.assertEqual(e["outcome"],
                             "parallel_registered_pending_adjudication")
            self.assertIs(e["snapshot_char_retained"], True)
            self.assertIs(e["internal_evidence_adopted"], False)
            self.assertIsNone(e["third_lineage_witness"])
            self.assertEqual(e["registration_kind"], "collation_parallel")
        self.assertEqual(
            Counter(e["collation_form"] for e in ENTRIES),
            Counter({"semantic_divergence": 8,
                     "glyph_variant_same_word_plus_semantic_divergence": 4}))
        glyph = sorted(e["seq"] for e in ENTRIES
                       if e["siku_reading_is_glyph_variant_of_snapshot_word"])
        self.assertEqual(glyph, [784, 853, 880, 931])
        sm = REG["summary"]
        self.assertEqual(sm["total"], 12)
        self.assertEqual(sm["adjudicated"], 0)
        self.assertEqual(sm["applied"], 0)
        self.assertEqual(sm["third_lineage_witness_found"], 0)
        self.assertEqual(sm["internal_evidence_adopted"], 0)
        self.assertEqual(REG["decision_standard"]["ud1_default"], "A")
        self.assertEqual(
            REG["decision_standard"]["standard_a_satisfied_entries"], 0)

    def test_witness_attestation_counts(self):
        siku = Counter()
        modern = Counter()
        for e in ENTRIES:
            self.assertEqual(e["siku_lineage"]["counts_as"], "one_lineage")
            for w in e["siku_lineage"]["witnesses"]:
                siku[(w["repo"], w["attestation"])] += 1
                self.assertEqual(w["site_reading"],
                                 e["siku_lineage"]["reading"], e["seq"])
                self.assertEqual(w["source"], "p3_fresh_probe", e["seq"])
            self.assertEqual(
                e["modern_cluster"]["counts_as"],
                "one_cluster_until_independence_verified")
            for h in e["modern_cluster"]["houses"]:
                modern[(h["repo"], h["attestation"])] += 1
            for b in e["modern_cluster"]["corroboration"]:
                self.assertEqual(b["repo"], "Banny-Gao")
                self.assertEqual(b["attestation"], "attested")
                self.assertEqual(b["role"], "corroboration_only")
        self.assertEqual(siku[("kanripo/KR3g0042", "attested")], 12)
        self.assertEqual(siku[("mikkokotila/Sanming-Tongshui", "attested")],
                         12)
        self.assertEqual(modern[("NiuTrans/Classical-Modern", "attested")],
                         12)
        self.assertEqual(modern[("youngzs/xuanxue", "attested")], 7)
        self.assertEqual(modern[("youngzs/xuanxue", "not_located")], 5)
        self.assertEqual(
            modern[("michiboo/Classical_Chinese_Wikisource",
                    "attested_in_candidate_record")], 5)
        self.assertEqual(
            modern[("michiboo/Classical_Chinese_Wikisource",
                    "not_in_candidate_record")], 7)
        yz_missing = sorted(
            e["seq"] for e in ENTRIES
            for h in e["modern_cluster"]["houses"]
            if h["repo"] == "youngzs/xuanxue"
            and h["attestation"] == "not_located")
        self.assertEqual(yz_missing, [450, 873, 880, 931, 933])
        self.assertEqual(REG["witness_lineages"]["third_lineage_witness_found"],
                         0)

    def test_reconciliation_8_vs_7(self):
        freg = fd.FANG_DISPOSITION_REGISTER
        inv_rd = {row["rd12_seq"]: row for row in freg["inventory"]
                  if row.get("rd12_seq") is not None}
        self.assertEqual(sorted(inv_rd), FANG_SEQS)
        # 盘点行坐标与本批条目逐条对平
        for seq in FANG_SEQS:
            self.assertEqual(inv_rd[seq]["s3_offset"],
                             BY_SEQ[seq]["site_s3"], seq)
            self.assertEqual(inv_rd[seq]["s0_offset"],
                             BY_SEQ[seq]["site_snapshot_span"][0], seq)
            link = BY_SEQ[seq]["p2_linkage"]
            self.assertIs(link["in_p2_inventory"], True, seq)
            self.assertEqual(link["p2_inventory_seq"], inv_rd[seq]["seq"],
                             seq)
        pending = sorted(
            seq for seq in FANG_SEQS
            if BY_SEQ[seq]["p2_linkage"]["p2_state"]
            == "pending_later_tranche")
        self.assertEqual(pending, PENDING7)
        # 第 8 条 seq 450：P2 处置记录在案，deferred 而非 pending
        disp_rd = [d for d in freg["dispositions"]
                   if d.get("rd12_seq") is not None]
        self.assertEqual(len(disp_rd), 1)
        self.assertEqual(disp_rd[0]["rd12_seq"], 450)
        self.assertEqual(disp_rd[0]["category"], "deferred_no_witness")
        self.assertEqual(disp_rd[0]["defer_reason"],
                         "reading_disagreement_rd12_p3_scope")
        link450 = BY_SEQ[450]["p2_linkage"]
        self.assertEqual(link450["p2_state"], "deferred_no_witness")
        self.assertEqual(link450["p2_defer_reason"],
                         "reading_disagreement_rd12_p3_scope")
        self.assertEqual(link450["p2_collation_note_id"],
                         disp_rd[0]["collation_note_id"])
        # P2 收官对账数字与本批对账块一致
        sm = freg["summary"]
        self.assertEqual((sm["disposed_total"], sm["deferred_no_witness"],
                          sm["pending_later_tranche"]), (161, 601, 7))
        self.assertEqual(161 + 601 + 7, 769)
        self.assertEqual(sm["rd12_sites_in_inventory"], 8)
        self.assertEqual(sm["rd12_sites_in_pending_tranches"], 7)
        rec = REG["reconciliation_rd12_vs_p2"]
        self.assertEqual(rec["arithmetic"],
                         "161 disposed + 601 deferred + 7 pending = 769")
        self.assertEqual(
            rec["pending7_state_after_this_batch"],
            "collation_registered_pending_adjudication")
        # 非防条目不在 P2 盘点范围内
        for seq in (784, 853, 880, 931):
            self.assertIs(BY_SEQ[seq]["p2_linkage"]["in_p2_inventory"],
                          False, seq)

    def test_pua_sites_and_context_positions(self):
        e784, e880 = BY_SEQ[784], BY_SEQ[880]
        self.assertEqual(e784["site_s0_codepoint"], "U+EA23")
        self.assertEqual(e784["site_s0_char"], "\uea23")
        self.assertIn("胤", e784["pua_site_note"])
        self.assertEqual(e880["site_s0_codepoint"], "U+EA20")
        self.assertEqual(e880["site_s0_char"], "\uea20")
        self.assertIn("玄", e880["pua_site_note"])
        for seq, e in BY_SEQ.items():
            if seq not in (784, 880):
                self.assertIsNone(e["pua_site_note"], seq)
                self.assertEqual(e["site_s0_char"], e["snapshot_reading"],
                                 seq)
        # seq 853 site_in_context 取登记原值 21，不得手填猜值
        self.assertEqual(BY_SEQ[853]["site_in_context"], 21)
        # seq 450 是 76 条携带中唯一的 RD 条目
        carry = [e["seq"] for e in ENTRIES if e["in_context_carry_76"]]
        self.assertEqual(carry, [450])
        self.assertEqual(BY_SEQ[450]["context_edits_crossed"],
                         {"ocr-228": "partial_overlap"})

    def test_posture(self):
        post = REG["posture"]
        self.assertIs(post["canonical_ready"], False)
        self.assertIs(post["snapshot_text_modified"], False)
        self.assertIs(post["applied_text_modified"], False)
        self.assertIs(post["existing_registers_modified"], False)
        self.assertEqual(post["tj0183_status"], "待做")
        self.assertEqual(post["tj0182_status"], "阻塞")


if __name__ == "__main__":
    unittest.main()
