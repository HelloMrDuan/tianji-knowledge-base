"""TJ-018.3 三命通会「PUA＋校勘正式应用批」（E0298）密封专项。

在新快照口径（237 文件）下核验应用产物：应用文本与报告文件存在且
哈希/字节合公开登记；快照本体与冻结五件逐字未动；报告自哈希按其
登记规则复算；报告内部阶段链（S1/444 检查点/S3）、603 条逐条记录
完备性与豁免集、链式归因 66 条构成、附件完备性（159 核销、76 携
带、limitations 空、RD-12 12 条、993 处置行）、缺口在应用文本中
原位可定位、disputed 位点在快照原文为对应 PUA 字形；组装数据总
计数与新 manifest 三元组对账。本专项只在离线验收执行，不进公开
CI（读取密封资产）。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_application_record as ar
from tianji_kb import bazi_sanming_formal_application as fa
from tianji_kb import bazi_sanming_pua_verification as pv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DZ = DATA / "quarantine" / "public_domain_snapshots" / "daizhigev20"
PINS = {p["stage_id"]: p["sha256"] for p in fa.STAGE_TEXT_PINS}
FREEZE_FILES = {
    "snapshot_text": "sanming_tonghui.txt",
    "pua_collation": "sanming_pua_collation.json",
    "text_collation": "sanming_text_collation.json",
    "ocr_candidates": "sanming_ocr_candidates.json",
    "pua_audit": "sanming_pua_audit.json",
}


def _sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class ApplicationRecordSealedTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.applied_bytes = (
            DZ / "sanming_tonghui_applied_v1.txt").read_bytes()
        cls.report_bytes = (
            DZ / "sanming_formal_application_report_v1.json").read_bytes()
        cls.report = json.loads(cls.report_bytes.decode("utf-8"))
        cls.applied = cls.applied_bytes.decode("utf-8")
        cls.snapshot = (DZ / "sanming_tonghui.txt").read_text(
            encoding="utf-8")

    def test_products_pinned(self):
        self.assertEqual(_sha_b(self.applied_bytes), PINS["S3"])
        self.assertEqual(
            len(self.applied_bytes), ar.PRODUCTS["applied_text"]["bytes"])
        self.assertEqual(len(self.applied), 461156)
        self.assertEqual(self.applied.count("防"), 769)
        self.assertEqual(self.applied.count("□"), 2)
        self.assertEqual(
            len(self.report_bytes),
            ar.PRODUCTS["application_report"]["bytes"])
        self.assertEqual(
            _sha_b(self.report_bytes),
            ar.PRODUCTS["application_report"]["file_sha256"])

    def test_snapshot_and_freeze_objects_untouched(self):
        self.assertEqual(
            _sha_b((DZ / "sanming_tonghui.txt").read_bytes()), PINS["S0"])
        design = {f["object"]: f["sha256"] for f in fa.FREEZE_REGISTER}
        for obj, fname in FREEZE_FILES.items():
            self.assertEqual(
                _sha_b((DZ / fname).read_bytes()), design[obj], fname)
        reported = {o["object"]: o["sha256"]
                    for o in self.report["freeze_check"]["objects"]}
        for obj, fname in FREEZE_FILES.items():
            self.assertEqual(reported[fname], design[obj])

    def test_report_self_hash_rule(self):
        rep = json.loads(self.report_bytes.decode("utf-8"))
        stored = rep["product_registration"]["report"]["sha256"]
        self.assertEqual(
            stored, ar.PRODUCTS["application_report"]["self_sha256"])
        rep["product_registration"]["report"]["sha256"] = "0" * 64
        rep["product_registration"]["report"]["bytes"] = 0
        rep["product_registration"]["snapshot_manifest_after"][
            "total_bytes"] = 0
        blob = (json.dumps(rep, ensure_ascii=False, indent=2) + "\n") \
            .encode("utf-8")
        self.assertEqual(_sha_b(blob), stored)

    def test_report_stage_chain_and_records(self):
        r = self.report
        self.assertEqual(r["stage_1"]["output_sha256"], PINS["S1"])
        self.assertEqual(r["stage_1"]["applied_occurrences"], 524)
        self.assertEqual(r["stage_1"]["remaining_pua"], 0)
        self.assertEqual(r["checkpoint_444"]["sha256"], PINS["S2"])
        self.assertEqual(r["stage_2"]["output_sha256"], PINS["S3"])
        self.assertEqual(r["stage_2"]["exemptions_used"], ["ocr-022"])
        records = r["stage_2"]["per_correction_records"]
        self.assertEqual(len(records), 603)
        self.assertEqual([x["seq"] for x in records],
                         list(range(1, 604)))
        self.assertEqual(
            [x["correction_id"] for x in records[:3]],
            ["ocr-001", "ocr-002", "ocr-003"])
        attributed = [x for x in records if "attribution" in x]
        self.assertEqual(len(attributed), 66)
        self.assertEqual(
            Counter(x["attribution"]["category"] for x in attributed),
            {"missing_glyph_context": 41, "chain_dependency": 25})
        self.assertEqual(r["round_trip"]["result"], "pass")
        self.assertEqual(r["round_trip"]["s0_sha256_restored"], PINS["S0"])
        self.assertEqual(r["residual_scan"]["pua_codepoints"], 0)
        self.assertEqual(r["residual_scan"]["fang"], 769)
        self.assertEqual(r["residual_scan"]["gap_square"], 2)

    def test_report_annex_completeness(self):
        annex = self.report["candidate_annex"]
        self.assertEqual(annex["total"], 993)
        self.assertEqual(
            annex["by_status"], ar.CANDIDATE_ANNEX_SUMMARY["by_status"])
        recon = annex["confirmed_applied_reconciliation"]
        self.assertEqual(len(recon), 159)
        self.assertTrue(all(x["verified"] for x in recon))
        carry = annex["context_carry"]
        self.assertEqual(len(carry), 76)
        self.assertEqual(annex["context_carry_limitations"], [])
        self.assertEqual(
            Counter(k for c in carry for k in c["crossed_kinds"]),
            {"partial_overlap": 52, "contained_within": 24})
        applied_carry = [c for c in carry
                         if c["status"] == "confirmed_applied"]
        self.assertEqual(len(applied_carry), 29)
        rd = annex["reading_disagreement_sites"]
        self.assertEqual(len(rd), 12)
        self.assertTrue(all(x["verified"] for x in rd))
        self.assertEqual(len(annex["dispositions"]), 993)
        self.assertEqual(
            Counter(d["status"] for d in annex["dispositions"]),
            Counter(annex["by_status"]))

    def test_report_gaps_and_disputed_sites(self):
        for g in self.report["permanent_gaps"]:
            self.assertEqual(self.applied.count(g["from"]), 1)
            sq3 = g["square_offsets"]["S3"]
            self.assertEqual(self.applied[sq3], "□")
            sq0 = g["square_offsets"]["S0"]
            self.assertEqual(self.snapshot[sq0], "□")
        verdicts = {v["codepoint"]: v for v in pv.CODEPOINT_VERDICTS}
        marks = self.report["stage_1"]["disputed_codepoint_markings"]
        self.assertEqual(len(marks), 4)
        for m in marks:
            v = verdicts[m["codepoint"]]
            self.assertEqual(m["replacement_applied"], v["replacement"])
            glyph = chr(int(m["codepoint"][2:], 16))
            for locus in m["loci_s0"]:
                self.assertEqual(self.snapshot[locus], glyph)

    def test_assembled_snapshot_triple(self):
        files = [p for p in DATA.rglob("*") if p.is_file()]
        self.assertEqual(len(files), 237)
        self.assertEqual(
            sum(p.stat().st_size for p in files),
            ar.PRODUCTS["snapshot_manifest_after"]["total_bytes"])
        reg = self.report["product_registration"]
        self.assertEqual(reg["applied_text"]["sha256"], PINS["S3"])
        self.assertEqual(
            reg["snapshot_manifest_after"]["files"], 237)
        self.assertEqual(
            reg["snapshot_manifest_after"]["total_bytes"],
            ar.PRODUCTS["snapshot_manifest_after"]["total_bytes"])
        self.assertEqual(reg["canonical_ready"], False)
        self.assertEqual(reg["planned_output_generated"], False)
        self.assertFalse(
            (DATA / "canonical" / "classics" / "bazi"
             / "sanming_tonghui_v1.json").exists())


if __name__ == "__main__":
    unittest.main()
