"""TJ-018.3 晋级 P3 RD-12 互校登记册密封专项（对密封原文执行）。

核验链：钉定快照哈希 → 两阶段复放重建 S2 基线文本并验钉 →
12 条候选逐条对齐（坐标、快照字、见证原文逐字）→ 应用报告
dispositions/flags 对账（RD-12 标记、450 携带记录）→ S2/S3
位点与语境逐字核验（语境与重锚登记原 span/哈希全等）。
本专项只读密封资产，不改任何文本与候选记录。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_rd12_collation as rd
from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = rd.RD12_COLLATION_REGISTER
ENTRIES = REG["entries"]
BY_SEQ = {e["seq"]: e for e in ENTRIES}
RE = {e["seq"]: e for e in ra.REANCHOR_REGISTER["entries"]}


def _load(name):
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def _text(name):
    return (SNAPSHOT_DIR / name).read_bytes().decode("utf-8")


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _is_pua(ch):
    cp = ord(ch)
    return 0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD \
        or 0x100000 <= cp <= 0x10FFFD


def _replay_s2(snapshot, pua_spec, corrections):
    text = snapshot
    for row in pua_spec.get("mappings", []):
        if row.get("status") != "confirmed":
            continue
        assert text.count(row["glyph"]) == int(row["count"]), row["codepoint"]
        text = text.replace(row["glyph"], row["replacement"])
    for row in pua_spec.get("contextual_mappings", []):
        if row.get("status") != "confirmed":
            continue
        for rule in row["replacements"]:
            assert text.count(rule["old"]) == 1, row["codepoint"]
            text = text.replace(rule["old"], rule["new"], 1)
    assert not any(_is_pua(c) for c in text), "PUA remains after stage 1"
    for row in corrections:
        if int(row["id"].split("-")[1]) > 444:
            continue
        old, new = row["old"], row["new"]
        assert text.count(old) == 1, row["id"]
        if text.count(new) and not row.get("allow_existing_target", False):
            raise AssertionError("target preexists " + row["id"])
        text = text.replace(old, new, 1)
    return text


class TestRd12CollationSealed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s0 = _text("sanming_tonghui.txt")
        cls.s3 = _text("sanming_tonghui_applied_v1.txt")
        cls.pua = _load("sanming_pua_collation.json")
        cls.col = _load("sanming_text_collation.json")
        cls.s2 = _replay_s2(cls.s0, cls.pua, cls.col["corrections"])
        cls.cands = _load("sanming_ocr_candidates.json")["candidates"]
        cls.report = _load("sanming_formal_application_report_v1.json")

    def test_stage_text_identities(self):
        inp = REG["inputs"]
        raw0 = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        self.assertEqual(hashlib.sha256(raw0).hexdigest(),
                         inp["snapshot"]["sha256"])
        self.assertEqual(len(self.s0), inp["snapshot"]["chars"])
        self.assertEqual(_sha(self.s2), inp["basis_text"]["sha256"])
        self.assertEqual(len(self.s2), inp["basis_text"]["chars"])
        raw3 = (SNAPSHOT_DIR / "sanming_tonghui_applied_v1.txt").read_bytes()
        self.assertEqual(hashlib.sha256(raw3).hexdigest(),
                         inp["applied_text"]["sha256"])
        self.assertEqual(len(raw3), inp["applied_text"]["bytes"])
        self.assertEqual(len(self.s3), inp["applied_text"]["chars"])
        rawc = (SNAPSHOT_DIR / "sanming_ocr_candidates.json").read_bytes()
        self.assertEqual(hashlib.sha256(rawc).hexdigest(),
                         inp["candidates_file"]["sha256"])
        rawr = (SNAPSHOT_DIR
                / "sanming_formal_application_report_v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(rawr).hexdigest(),
                         inp["application_report"]["file_sha256"])

    def test_entries_match_sealed_candidates(self):
        self.assertEqual(len(self.cands), 993)
        for e in ENTRIES:
            cand = self.cands[e["seq"] - 1]
            self.assertEqual(e["status"], cand["status"], e["seq"])
            self.assertEqual(e["volume"], int(cand["volume"]), e["seq"])
            self.assertIsNone(cand["correction_id"], e["seq"])
            self.assertEqual(e["site_s2"],
                             int(cand["baseline_character_offset"]), e["seq"])
            self.assertEqual(e["snapshot_reading"], cand["old"], e["seq"])
            self.assertEqual(e["siku_lineage"]["reading"],
                             cand["historical_reading"], e["seq"])
            self.assertEqual(e["context"], cand["context"], e["seq"])
            self.assertEqual(
                e["candidate_record_evidence"]["historical_evidence"],
                cand.get("historical_evidence") or [], e["seq"])
            self.assertEqual(
                e["candidate_record_evidence"]["crosscheck_evidence"],
                cand.get("crosscheck_evidence") or [], e["seq"])

    def test_report_dispositions_and_flags(self):
        disp = {d["seq"]: d
                for d in self.report["candidate_annex"]["dispositions"]}
        self.assertEqual(len(disp), 993)
        rd_flagged = sorted(
            seq for seq, d in disp.items()
            if d["flags"]["in_reading_disagreement_12"])
        self.assertEqual(rd_flagged, sorted(BY_SEQ))
        for e in ENTRIES:
            d = disp[e["seq"]]
            self.assertEqual(d["site_s2_offset"], e["site_s2"], e["seq"])
            self.assertEqual(d["site_s3_offset"], e["site_s3"], e["seq"])
            self.assertEqual(d["site_s0_offset"],
                             e["site_snapshot_span"][0], e["seq"])
            self.assertEqual(d["site_state_in_S3"], e["s3_reading"],
                             e["seq"])
            self.assertEqual(d["disposition"],
                             "deferred_to_P1_finalization_batch", e["seq"])
            self.assertFalse(d["flags"]["confirmed_applied_reconciled"],
                             e["seq"])
            self.assertEqual(d["flags"]["in_context_carry_76"],
                             e["in_context_carry_76"], e["seq"])

    def test_sites_and_contexts_verbatim(self):
        for e in ENTRIES:
            seq = e["seq"]
            # S0 位点原字（含两处 PUA）逐字核对
            s0_at = self.s0[e["site_snapshot_span"][0]]
            self.assertEqual(s0_at, e["site_s0_char"], seq)
            self.assertEqual(
                "U+%04X" % ord(s0_at), e["site_s0_codepoint"], seq)
            # S2/S3 位点字即快照读法（应用批未动 RD-12 位点）
            self.assertEqual(self.s2[e["site_s2"]], e["snapshot_reading"],
                             seq)
            self.assertEqual(self.s3[e["site_s3"]], e["s3_reading"], seq)
            # 语境：S2 与 S3 同 span 同文同哈希（全取重锚登记原值）
            lo, hi = e["context_span_s2"]
            self.assertEqual(self.s2[lo:hi], e["context"], seq)
            self.assertEqual(_sha(self.s2[lo:hi]), e["context_s2_sha256"],
                             seq)
            lo3, hi3 = e["context_span_s3"]
            self.assertEqual((lo3, hi3), (lo, hi), seq)
            self.assertEqual(self.s3[lo3:hi3], e["context"], seq)
            self.assertEqual(_sha(self.s3[lo3:hi3]), e["context_s3_sha256"],
                             seq)
            self.assertEqual(e["context"][e["site_in_context"]],
                             e["snapshot_reading"], seq)

    def test_carry450_record(self):
        carry = self.report["candidate_annex"]["context_carry"]
        recs = [c for c in carry if c["seq"] == 450]
        self.assertEqual(len(recs), 1)
        rec = recs[0]
        e = BY_SEQ[450]
        self.assertEqual(rec["s3_context_span"], e["context_span_s3"])
        self.assertEqual(rec["s3_context"], e["context"])
        self.assertEqual(rec["context_final_sha256"],
                         e["context_s3_sha256"])
        self.assertEqual(rec["baseline_context_sha256"],
                         e["context_s2_sha256"])
        self.assertEqual(rec["crossed_corrections"],
                         e["context_edits_crossed"])
        # 76 条携带中 RD 条目仅此一条
        self.assertEqual(len(carry), 76)
        self.assertEqual(
            [c["seq"] for c in carry if c["seq"] in BY_SEQ], [450])


if __name__ == "__main__":
    unittest.main()
