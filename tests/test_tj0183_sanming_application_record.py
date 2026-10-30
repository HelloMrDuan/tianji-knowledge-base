"""TJ-018.3 三命通会「PUA＋校勘正式应用批」（E0298）：公开结构测试。

登记模块 ``bazi_sanming_application_record`` 为纯数据、零函数、不被
任何可执行路径 import；本测试只钉执行记录摘要的形制与跨登记册一致
性（冻结/阶段钉值对照设计登记册、状态分布对照重锚登记册、disputed
位点对照全核登记册、产物登记对照 public_domain_manifest 应用记录、
三元组算术、公开侧不含全文与逐条 old/new 的红线）。密封侧实证
（产物文件哈希、报告内部完备性、附件计数、既有登记回归）在密封
专项 ``tests/test_tj0183_sanming_application_record_sealed.py``
（仅离线验收，不进公开 CI）。
"""

from __future__ import annotations

import ast
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_application_record as ar
from tianji_kb import bazi_sanming_formal_application as fa
from tianji_kb import bazi_sanming_pua_verification as pv
from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0183_sanming_application_record.json")
    .read_text(encoding="utf-8"))
MANIFEST = json.loads(
    (ROOT / "config" / "public_domain_manifest.json").read_text(
        encoding="utf-8"))
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))
REG = ar.APPLICATION_RECORD_REGISTER


def _mirror():
    return {
        "meta": {
            "register_id": REG["id"],
            "task": REG["task"],
            "kind": REG["kind"],
            "purpose": GOLDEN["meta"]["purpose"],
        },
        "freeze_check": ar.FREEZE_CHECK,
        "stage_1": ar.STAGE_1_RECORD,
        "checkpoint_444": ar.CHECKPOINT_444,
        "stage_2": ar.STAGE_2_RECORD,
        "residual_scan": ar.RESIDUAL_SCAN,
        "round_trip": ar.ROUND_TRIP,
        "candidate_annex": ar.CANDIDATE_ANNEX_SUMMARY,
        "permanent_gaps": ar.PERMANENT_GAPS_RECORD,
        "products": ar.PRODUCTS,
        "canonical_posture": ar.CANONICAL_POSTURE,
        "next_routes": ar.NEXT_ROUTES,
    }


def _work():
    return next(w for s in MANIFEST["sources"] for w in s["works"]
                if w["id"] == "sanming_tonghui")


class ApplicationRecordPublicTest(unittest.TestCase):

    def test_golden_mirror(self):
        self.assertEqual(_mirror(), GOLDEN)

    def test_register_is_pure_data(self):
        tree = ast.parse(Path(ar.__file__).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        self.assertEqual(REG["ledger_event"], "E0298")
        self.assertEqual(
            REG["baseline_main_sha"],
            "ee928c4439fc4b86600e639bfe5739db616732d5")

    def test_freeze_objects_match_design_register(self):
        design = {f["object"]: f["sha256"] for f in fa.FREEZE_REGISTER}
        mine = {o["object"]: o["sha256"]
                for o in ar.FREEZE_CHECK["objects"]}
        self.assertEqual(mine, design)
        self.assertEqual(ar.FREEZE_CHECK["result"], "pass")
        before = ar.FREEZE_CHECK["snapshot_manifest_before"]
        self.assertEqual((before["files"], before["bytes"]), (235, 13580501))

    def test_stage_pins_match_design_register(self):
        pins = {p["stage_id"]: p["sha256"] for p in fa.STAGE_TEXT_PINS}
        self.assertEqual(ar.STAGE_1_RECORD["input_sha256"], pins["S0"])
        self.assertEqual(ar.STAGE_1_RECORD["output_sha256"], pins["S1"])
        self.assertEqual(ar.CHECKPOINT_444["sha256"], pins["S2"])
        self.assertEqual(ar.STAGE_2_RECORD["output_sha256"], pins["S3"])
        self.assertEqual(ar.ROUND_TRIP["s0_restored_sha256"], pins["S0"])
        self.assertEqual(
            ar.ROUND_TRIP["checkpoint_444_restored_sha256"], pins["S2"])
        self.assertEqual(ar.ROUND_TRIP["result"], "pass")
        self.assertEqual(
            ar.CHECKPOINT_444["sha256"],
            ra.REANCHOR_REGISTER["basis_text"]["sha256"])

    def test_stage_counts_and_exemption(self):
        self.assertEqual(ar.STAGE_1_RECORD["applied_mappings"], 86)
        self.assertEqual(ar.STAGE_1_RECORD["applied_occurrences"], 524)
        self.assertEqual(ar.STAGE_1_RECORD["remaining_pua"], 0)
        self.assertEqual(ar.STAGE_2_RECORD["applied"], 603)
        self.assertEqual(ar.STAGE_2_RECORD["exemptions_used"], ["ocr-022"])
        self.assertEqual(ar.STAGE_2_RECORD["per_correction_records"], 603)
        self.assertEqual(
            ar.STAGE_2_RECORD["chain_attribution_records"],
            {"total": 66, "missing_glyph_context": 41,
             "chain_dependency": 25})
        self.assertEqual(
            ar.RESIDUAL_SCAN, {"pua_codepoints": 0, "fang": 769,
                               "gap_square": 2})

    def test_annex_aggregates_match_reanchor(self):
        counts = Counter(e["status"]
                         for e in ra.REANCHOR_REGISTER["entries"])
        self.assertEqual(dict(counts),
                         ar.CANDIDATE_ANNEX_SUMMARY["by_status"])
        self.assertEqual(
            ra.REANCHOR_REGISTER["summary"]["status_counts"],
            ar.CANDIDATE_ANNEX_SUMMARY["by_status"])
        annex = ar.CANDIDATE_ANNEX_SUMMARY
        self.assertEqual(annex["total"], 993)
        self.assertEqual(sum(annex["by_status"].values()), 993)
        self.assertEqual(annex["confirmed_applied_reconciled"], 159)
        self.assertEqual(annex["context_carry"]["total"], 76)
        self.assertEqual(
            sum(annex["context_carry"]["by_kind"].values()), 76)
        self.assertEqual(
            sum(annex["context_carry"]["contained_within_relations"]
                .values()),
            annex["context_carry"]["by_kind"]["contained_within"])
        self.assertEqual(annex["context_carry_limitations"], 0)
        self.assertEqual(annex["reading_disagreement_sites_verified"], 12)
        self.assertEqual(annex["dispositions_recorded"], 993)

    def test_disputed_against_full_verification(self):
        verdicts = {v["codepoint"]: v for v in pv.CODEPOINT_VERDICTS}
        mine = {d["codepoint"]: d
                for d in ar.STAGE_1_RECORD["disputed_codepoints"]}
        self.assertEqual(
            set(mine),
            {cp for cp, v in verdicts.items() if v["verdict"] == "disputed"})
        for cp, d in mine.items():
            v = verdicts[cp]
            self.assertEqual(d["replacement_applied"], v["replacement"])
            self.assertEqual(len(d["loci_s0"]), v["snapshot_count"])
            for off in v["unattested_loci_offsets"]:
                self.assertIn(off, d["loci_s0"])
            self.assertEqual(
                d["rival_readings"],
                [r["reading"] for r in v["rival_readings"]])

    def test_products_and_triple_arithmetic(self):
        after = ar.PRODUCTS["snapshot_manifest_after"]
        self.assertEqual(after["files"], 235 + 2)
        self.assertEqual(
            after["total_bytes"],
            13580501 + ar.PRODUCTS["applied_text"]["bytes"]
            + ar.PRODUCTS["application_report"]["bytes"])
        self.assertEqual(
            ar.PRODUCTS["applied_text"]["sha256"],
            ar.STAGE_2_RECORD["output_sha256"])
        self.assertEqual(ar.CANONICAL_POSTURE["canonical_ready"], False)
        self.assertEqual(
            ar.CANONICAL_POSTURE["planned_output_generated"], False)
        self.assertEqual(
            ar.CANONICAL_POSTURE["snapshot_original_untouched"], True)

    def test_manifest_application_record(self):
        work = _work()
        rec = work["formal_application"]
        self.assertEqual(rec["record_register"], REG["id"])
        self.assertEqual(
            rec["derived_from_snapshot_sha256"],
            ar.STAGE_1_RECORD["input_sha256"])
        self.assertEqual(
            rec["stage_text_sha256"],
            {"S1": ar.STAGE_1_RECORD["output_sha256"],
             "S2": ar.CHECKPOINT_444["sha256"],
             "S3": ar.STAGE_2_RECORD["output_sha256"]})
        self.assertEqual(rec["applied_text"], ar.PRODUCTS["applied_text"])
        self.assertEqual(
            rec["application_report"]["bytes"],
            ar.PRODUCTS["application_report"]["bytes"])
        self.assertEqual(
            rec["application_report"]["file_sha256"],
            ar.PRODUCTS["application_report"]["file_sha256"])
        self.assertEqual(
            rec["snapshot_manifest_after"],
            ar.PRODUCTS["snapshot_manifest_after"])
        self.assertEqual(rec["canonical_ready"], False)
        self.assertEqual(rec["text_review_status"], "in_progress")
        self.assertEqual(work["promotion"], "quarantine_only")
        self.assertEqual(work["quality_blockers"]["canonical_ready"], False)
        self.assertEqual(
            work["quality_blockers"]["text_review_status"], "in_progress")
        gaps = work["unconfirmed_text_gaps"]
        self.assertEqual(len(gaps), 2)
        self.assertEqual(
            [g["proposed_reading"] for g in gaps],
            [g["proposed_reading"] for g in ar.PERMANENT_GAPS_RECORD])
        for g in ar.PERMANENT_GAPS_RECORD:
            self.assertEqual(g["status"], "permanent_gap")
            self.assertEqual(g["verbatim_preserved_in_S3"], True)
            self.assertEqual(g["square_offsets"]["S0"],
                             g["square_offsets"]["S1"])

    def test_public_summary_carries_only_registered_hashes(self):
        # 逐条记录只在密封报告：公开登记只给计数（int），不给逐条清单；
        # 且模块中出现的全部 64 位哈希恰为设计钉值/冻结哈希与本批产物
        # 登记哈希，无其他来源不明的哈希或全文。
        self.assertIsInstance(
            ar.STAGE_2_RECORD["per_correction_records"], int)

        def strings(obj):
            if isinstance(obj, str):
                yield obj
            elif isinstance(obj, dict):
                for v in obj.values():
                    yield from strings(v)
            elif isinstance(obj, (list, tuple)):
                for v in obj:
                    yield from strings(v)

        found = set()
        for name in ("FREEZE_CHECK", "STAGE_1_RECORD", "CHECKPOINT_444",
                     "STAGE_2_RECORD", "ROUND_TRIP",
                     "CANDIDATE_ANNEX_SUMMARY", "PERMANENT_GAPS_RECORD",
                     "PRODUCTS"):
            for s in strings(getattr(ar, name)):
                if len(s) == 64 and all(
                        c in "0123456789abcdef" for c in s):
                    found.add(s)
        expected = {p["sha256"] for p in fa.STAGE_TEXT_PINS}
        expected |= {f["sha256"] for f in fa.FREEZE_REGISTER}
        expected |= {
            ar.FREEZE_CHECK["snapshot_manifest_before"]["sha256"],
            ar.PRODUCTS["application_report"]["file_sha256"],
            ar.PRODUCTS["application_report"]["self_sha256"],
            ar.PRODUCTS["snapshot_manifest_after"]["sha256"]}
        self.assertEqual(found, expected)
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES["sources"]), 102)


if __name__ == "__main__":
    unittest.main()
