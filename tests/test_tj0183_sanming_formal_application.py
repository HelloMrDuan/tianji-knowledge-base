"""TJ-018.3 晋级前置「PUA＋校勘正式应用批」设计审定：公开结构测试。

本批是审定批：登记模块 ``bazi_sanming_formal_application`` 为纯
数据、零函数、不被任何可执行路径 import；本测试只钉登记形制与
审定红线（冻结钉值、阶段文本钉值、管线规约要点与 fail-hard
清单、PUA 全核门与覆盖缺口、76 条 context 携带聚合与重锚登记
册的交叉核对、RD-12 逐条与候选状态口径、缺口与 manifest 的
交叉核对、用户级待裁定与验收配方、零应用口径），不验证任何
应用产物。密封侧实测复核（文件哈希、两阶段复放、阶段哈希、
RD-12 位点字、既有登记回归）在密封专项
``tests/test_tj0183_sanming_formal_application_sealed.py``
（仅离线验收，不进公开 CI）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_formal_application as fa
from tianji_kb import bazi_sanming_reanchor as ra
from tianji_kb import bazi_sanming_juan2_collation as j2a
from tianji_kb import bazi_sanming_juan2_sanxing_collation as j2b
from tianji_kb import bazi_sanming_juan2_hehua_collation as j2c
from tianji_kb import bazi_sanming_juan5_quliu_collation as j5a
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as j5b
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as j6

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0183_sanming_formal_application.json")
    .read_text(encoding="utf-8"))
MANIFEST = json.loads(
    (ROOT / "config" / "public_domain_manifest.json").read_text(
        encoding="utf-8"))
REG = fa.FORMAL_APPLICATION_DESIGN_REGISTER


def _mirror():
    return {
        "meta": {
            "register_id": REG["id"],
            "task": REG["task"],
            "kind": REG["kind"],
            "purpose": GOLDEN["meta"]["purpose"],
        },
        "headline_verdicts": REG["headline_verdicts"],
        "freeze_objects": [
            {"object": f["object"], "sha256": f["sha256"]}
            for f in fa.FREEZE_REGISTER],
        "stage_text_pins": fa.STAGE_TEXT_PINS,
        "fail_hard_ids": [
            f["id"] for f in fa.PIPELINE_SPEC["fail_hard_conditions"]],
        "context_carry": {
            "by_kind": fa.CONTEXT_CARRY_SPEC["by_kind"],
            "by_status": fa.CONTEXT_CARRY_SPEC["by_status"],
            "by_volume": fa.CONTEXT_CARRY_SPEC["by_volume"],
            "rule_ids": [r["id"] for r in fa.CONTEXT_CARRY_SPEC["rules"]],
            "partial_overlap_seq": fa.CONTEXT_CARRY_SPEC[
                "partial_overlap_seq"],
            "contained_within_seq": fa.CONTEXT_CARRY_SPEC[
                "contained_within_seq"],
        },
        "reading_disagreement": fa.READING_DISAGREEMENT_SPEC["items"],
        "permanent_gaps": [
            {"from": g["from"], "proposed_reading": g["proposed_reading"],
             "status": g["status"]}
            for g in fa.PERMANENT_GAPS["items"]],
        "user_decisions": [
            {"id": u["id"], "needed_now": u["needed_now"]}
            for u in fa.PROMOTION_INTERFACE["user_decisions"]],
        "acceptance_recipe_ids": [
            a["id"] for a in fa.APPLICATION_ACCEPTANCE_RECIPE],
        "adjudication_point_ids": [
            a["id"] for a in fa.ADJUDICATION_POINTS],
        "pua_coverage": {
            "cited": 32,
            "uncited": len(fa.PUA_FULL_VERIFICATION[
                "measured_coverage_now"]["zero_citation_codepoints"]),
            "uncited_codepoints": fa.PUA_FULL_VERIFICATION[
                "measured_coverage_now"]["zero_citation_codepoints"],
        },
        "sealed_measurements": fa.SEALED_MEASUREMENTS,
    }


class GoldenMirrorTest(unittest.TestCase):
    def test_module_matches_golden(self):
        self.assertEqual(_mirror(), GOLDEN)


class PureDataShapeTest(unittest.TestCase):
    def test_zero_functions(self):
        fns = [n for n, v in vars(fa).items() if inspect.isfunction(v)]
        self.assertEqual(fns, [])

    def test_design_only_headline(self):
        h = REG["headline_verdicts"]
        self.assertTrue(h["design_only"])
        self.assertFalse(h["applied_in_this_batch"])
        self.assertFalse(h["snapshot_modified"])
        self.assertFalse(h["sealed_assets_modified"])
        self.assertTrue(h["application_spec_ready"])
        self.assertFalse(h["canonical_ready"])
        self.assertEqual(h["review_status"], "in_progress")
        self.assertEqual(REG["task"], "TJ-018.2")
        self.assertEqual(REG["baseline"]["ledger_event"], "E0294")
        self.assertEqual(REG["baseline"]["ledger_events_before"], 293)


class FreezeAndPinsTest(unittest.TestCase):
    def test_freeze_objects(self):
        objs = {f["object"]: f for f in fa.FREEZE_REGISTER}
        self.assertEqual(
            set(objs), {"snapshot_text", "pua_collation", "text_collation",
                        "ocr_candidates", "pua_audit"})
        snap = objs["snapshot_text"]
        self.assertEqual(snap["sha256"], REG["source_snapshot"]["sanming_sha256"])
        self.assertEqual(snap["chars"], 461157)
        self.assertEqual(snap["measured_facts"]["pua_occurrences"], 524)
        self.assertEqual(snap["measured_facts"]["fang_occurrences"], 1606)
        self.assertEqual(snap["measured_facts"]["gap_square_occurrences"], 2)
        coll = objs["text_collation"]["measured_facts"]
        self.assertEqual(coll["corrections"], 603)
        self.assertEqual(coll["allow_existing_target_ids"], ["ocr-022"])
        self.assertEqual(coll["length_changing"],
                         [{"id": "ocr-017", "old_len": 16, "new_len": 15}])
        self.assertFalse(coll["summary_canonical_ready"])
        cand = objs["ocr_candidates"]["measured_facts"]
        self.assertEqual(sum(cand["status_counts"].values()), 993)
        self.assertEqual(cand["status_counts"]["confirmed_applied"], 159)

    def test_stage_pin_chain(self):
        pins = {p["stage_id"]: p for p in fa.STAGE_TEXT_PINS}
        self.assertEqual(pins["S0"]["chars"] - pins["S1"]["chars"], 0)
        self.assertEqual(pins["S1"]["chars"] - pins["S3"]["chars"], 1)
        self.assertEqual(pins["S2"]["chars"], pins["S3"]["chars"])
        self.assertEqual(pins["S1"]["pua"], 0)
        self.assertEqual(pins["S3"]["pua"], 0)
        self.assertEqual(pins["S3"]["fang"], 769)
        self.assertEqual(pins["S0"]["fang"] - pins["S3"]["fang"], 837)
        self.assertEqual(pins["S2"]["sha256"],
                         ra.REANCHOR_REGISTER["basis_text"]["sha256"])
        self.assertEqual(pins["S0"]["sha256"],
                         ra.REANCHOR_REGISTER["snapshot"]["sha256"])
        self.assertTrue(all(p["gap_square"] == 2 for p in pins.values()))

    def test_manifest_pin(self):
        s = REG["source_snapshot"]
        self.assertEqual(s["trusted_manifest_files"], 235)
        self.assertEqual(s["trusted_manifest_bytes"], 13580501)
        self.assertEqual(len(s["trusted_manifest_sha256"]), 64)


class PipelineSpecTest(unittest.TestCase):
    def test_fail_hard_set(self):
        ids = [f["id"] for f in fa.PIPELINE_SPEC["fail_hard_conditions"]]
        self.assertEqual(ids, ["F%d" % i for i in range(1, 11)])

    def test_checkpoint_and_exemption_pins(self):
        stage2 = fa.PIPELINE_SPEC["stage_2_text"]
        self.assertIn("ocr-444", stage2["semantics"][4])
        self.assertIn("ocr-022", stage2["semantics"][3])
        self.assertEqual(fa.PIPELINE_SPEC["round_trip"]["checkpoints"],
                         ["逆复放至 S2 == db8618c9…",
                          "逆复放至 S0 == 00e2a7db…"])
        self.assertIn("朴素逆字符串替换",
                      fa.PIPELINE_SPEC["round_trip"]["prohibited"])

    def test_product_form_keeps_noncanonical(self):
        pf = fa.PIPELINE_SPEC["product_form"]
        self.assertEqual(len(pf["new_sealed_files"]), 2)
        self.assertIn("canonical_ready 保持 false", pf["registration"])
        self.assertEqual(len(pf["dual_pin_sync_checklist"]), 5)

    def test_record_and_report_fields(self):
        self.assertEqual(
            len(fa.PIPELINE_SPEC["per_correction_record_fields"]), 9)
        self.assertEqual(len(fa.PIPELINE_SPEC["report_fields"]), 8)


class PuaGateTest(unittest.TestCase):
    def test_coverage_arithmetic(self):
        cov = fa.PUA_FULL_VERIFICATION["measured_coverage_now"]
        self.assertFalse(cov["audit_file_status_field"])
        self.assertEqual(cov["public_register_citations"], 32)
        self.assertEqual(len(cov["zero_citation_codepoints"]), 54)
        self.assertEqual(32 + len(cov["zero_citation_codepoints"]), 86)
        self.assertEqual(
            len(set(cov["zero_citation_codepoints"])), 54)

    def test_gate_references_f10(self):
        self.assertIn("F10", fa.PUA_FULL_VERIFICATION["gate"])
        self.assertIn("86/86", fa.PUA_FULL_VERIFICATION["requirement"])


class ContextCarryTest(unittest.TestCase):
    def test_aggregates_self_consistent(self):
        cc = fa.CONTEXT_CARRY_SPEC
        self.assertEqual(sum(cc["by_kind"].values()), 76)
        self.assertEqual(sum(cc["by_status"].values()), 76)
        self.assertEqual(
            sum(int(v) for v in cc["by_volume"].values()), 76)
        self.assertEqual(len(cc["partial_overlap_seq"]), 52)
        self.assertEqual(len(cc["contained_within_seq"]), 24)
        self.assertFalse(
            set(cc["partial_overlap_seq"]) & set(cc["contained_within_seq"]))

    def test_cross_check_against_reanchor_register(self):
        entries = ra.REANCHOR_REGISTER["entries"]
        crossed = [e for e in entries
                   if e["context_anchor_class"]
                   == "unanchorable_crosses_boundary"]
        self.assertEqual(len(crossed), 76)
        partial = sorted(
            e["seq"] for e in crossed
            if set(e["context_edits_crossed"].values())
            == {"partial_overlap"})
        contained = sorted(
            e["seq"] for e in crossed
            if set(e["context_edits_crossed"].values())
            == {"contained_within"})
        self.assertEqual(partial,
                         fa.CONTEXT_CARRY_SPEC["partial_overlap_seq"])
        self.assertEqual(contained,
                         fa.CONTEXT_CARRY_SPEC["contained_within_seq"])
        by_status = {}
        for e in crossed:
            by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        self.assertEqual(by_status, fa.CONTEXT_CARRY_SPEC["by_status"])

    def test_candidate_disposition_counts(self):
        d = fa.CANDIDATE_DISPOSITION_SPEC
        total = sum(v["count"] for v in d.values())
        self.assertEqual(total, 993)


class ReadingDisagreementTest(unittest.TestCase):
    def test_items_cross_check_reanchor(self):
        entries = {e["seq"]: e for e in ra.REANCHOR_REGISTER["entries"]
                   if e["status"] == "reading_disagreement_hold"}
        items = fa.READING_DISAGREEMENT_SPEC["items"]
        self.assertEqual(len(items), 12)
        self.assertEqual({i["seq"] for i in items}, set(entries))
        for i in items:
            e = entries[i["seq"]]
            self.assertEqual(i["basis_offset"], e["basis_offset"])
            self.assertEqual(i["old"], e["old"])
            self.assertEqual(i["historical_reading"],
                             e["historical_reading"])
            self.assertEqual(i["site_anchor_class"], "anchored_direct")
        crossed = [i for i in items
                   if i["context_anchor_class"]
                   == "unanchorable_crosses_boundary"]
        self.assertEqual([i["seq"] for i in crossed], [450])

    def test_items_summary(self):
        s = fa.READING_DISAGREEMENT_SPEC["items_summary"]
        self.assertEqual(sum(s["old_chars"].values()), 12)
        self.assertEqual(s["old_chars"]["防"], 8)
        lineages = fa.READING_DISAGREEMENT_SPEC["witness_lineages"]
        self.assertEqual(len(lineages), 2)
        self.assertEqual(len(lineages[0]["witnesses"]), 2)
        self.assertEqual(len(lineages[1]["witnesses"]), 3)


class PermanentGapsTest(unittest.TestCase):
    def test_gaps_cross_check_manifest(self):
        works = MANIFEST["sources"][0]["works"]
        work = [w for w in works if w["id"] == "sanming_tonghui"][0]
        gaps = work["unconfirmed_text_gaps"]
        self.assertEqual(len(gaps), 2)
        self.assertEqual(work["quality_blockers"]["unresolved_text_gaps"], 2)
        mine = fa.PERMANENT_GAPS["items"]
        self.assertEqual([g["from"] for g in mine],
                         [g["from"] for g in gaps])
        for g, src in zip(mine, gaps):
            self.assertEqual(g["proposed_reading"], src["proposed_reading"])
            self.assertEqual(g["status"],
                             "needs_base_text_evidence_do_not_apply")
        self.assertIn("只阻断整书 canonical 晋级",
                      fa.PERMANENT_GAPS["blocking_scope"])


class PromotionInterfaceTest(unittest.TestCase):
    def test_remaining_items(self):
        rem = fa.PROMOTION_INTERFACE["remaining_after_application"]
        self.assertEqual([r["id"] for r in rem], ["P1", "P2", "P3", "P4"])
        closed = fa.PROMOTION_INTERFACE["closed_by_application_batch"]
        self.assertEqual(len(closed), 6)

    def test_user_decisions_not_needed_now(self):
        uds = fa.PROMOTION_INTERFACE["user_decisions"]
        self.assertEqual([u["id"] for u in uds], ["UD-1", "UD-2", "UD-3"])
        self.assertTrue(all(not u["needed_now"] for u in uds))
        self.assertTrue(all(len(u["options"]) >= 2 for u in uds))
        self.assertEqual(len(uds[0]["options"]), 3)

    def test_acceptance_recipe_and_points(self):
        self.assertEqual(
            [a["id"] for a in fa.APPLICATION_ACCEPTANCE_RECIPE],
            ["A%d" % i for i in range(1, 8)])
        self.assertEqual([a["id"] for a in fa.ADJUDICATION_POINTS],
                         ["AP%d" % i for i in range(1, 7)])


class UserDecisionAdjudicationTest(unittest.TestCase):
    """E0327 UD 裁定登记：只增补 adjudication 字段，既有登记原文零改动。"""

    def test_all_three_decided_a_by_user(self):
        uds = fa.PROMOTION_INTERFACE["user_decisions"]
        self.assertEqual([u["id"] for u in uds], ["UD-1", "UD-2", "UD-3"])
        for u in uds:
            a = u["adjudication"]
            self.assertEqual(a["status"], "decided")
            self.assertEqual(a["date"], "2026-10-30")
            self.assertEqual(a["decided_by"], "用户")
            self.assertEqual(a["option_chosen"], "A")
            self.assertEqual(a["registration_event"], "E0327")
            self.assertTrue(u["options"][0].startswith("A "))
            self.assertIn("E0326", a["basis"])

    def test_original_ud_text_verbatim(self):
        uds = {u["id"]: u for u in fa.PROMOTION_INTERFACE["user_decisions"]}
        self.assertEqual([len(uds[i]["options"]) for i in
                          ("UD-1", "UD-2", "UD-3")], [3, 2, 2])
        self.assertTrue(all(not uds[i]["needed_now"] for i in uds))
        self.assertIn("不走", uds["UD-1"]["design_recommendation"])
        self.assertIn("不足以改底本", uds["UD-2"]["design_recommendation"])
        self.assertIn("P4 决策包时再正式呈请",
                      uds["UD-3"]["design_recommendation"])
        # 设计批当时状态的记录不回改：headline 仍记待裁定 3 项
        self.assertEqual(
            REG["headline_verdicts"]["user_decisions_pending"], 3)

    def test_adjudication_effects_freeze_defaults(self):
        uds = {u["id"]: u for u in fa.PROMOTION_INTERFACE["user_decisions"]}
        self.assertIn("已裁定：并列保留", uds["UD-1"]["adjudication"]["effect"])
        self.assertIn("不执行", uds["UD-1"]["adjudication"]["effect"])
        self.assertIn("永久缺口", uds["UD-2"]["adjudication"]["effect"])
        self.assertIn("42148", uds["UD-2"]["adjudication"]["effect"])
        self.assertIn("318327", uds["UD-2"]["adjudication"]["effect"])
        self.assertIn("canonical_ready 保持 false",
                      uds["UD-3"]["adjudication"]["effect"])
        # 裁定不改整书姿态与缺口登记
        self.assertFalse(REG["headline_verdicts"]["canonical_ready"])
        self.assertTrue(all(
            g["status"] == "needs_base_text_evidence_do_not_apply"
            for g in fa.PERMANENT_GAPS["items"]))
        self.assertTrue(fa.READING_DISAGREEMENT_SPEC[
            "default_disposition"].startswith("并列登记、快照字保留"))


class SealedMeasurementsTest(unittest.TestCase):
    def test_arithmetic(self):
        sm = fa.SEALED_MEASUREMENTS
        self.assertEqual(sm["snapshot"]["fang"], 1606)
        self.assertEqual(sm["final_603"]["fang"], 769)
        self.assertEqual(sm["collation_counts"]["fang_net"], -837)
        self.assertEqual(
            sm["final_603"]["fang_distinct_pm6_contexts"], 769)
        cc = sm["candidate_counts"]
        self.assertEqual(
            cc["historical_only_hold"] + cc["variant_preserve"]
            + cc["confirmed_applied"] + cc["reading_disagreement_hold"],
            cc["total"])
        self.assertTrue(cc["confirmed_id_set_equals_ocr_445_603"])

    def test_collation_register_totals_live(self):
        total = (len(j2a.COLLATION_NOTES) + len(j2b.COLLATION_NOTES)
                 + len(j2c.COLLATION_NOTES) + len(j5a.COLLATION_NOTES)
                 + len(j5b.COLLATION_NOTES) + len(j6.COLLATION_NOTES))
        reg = fa.SEALED_MEASUREMENTS["collation_registers_entries"]
        self.assertEqual(total, 383)
        self.assertEqual(reg["total"], total)
        self.assertEqual(reg["juan2_group"], 160)
        self.assertEqual(reg["juan5_group"], 151)
        self.assertEqual(reg["juan6_group"], 72)


if __name__ == "__main__":
    unittest.main()
