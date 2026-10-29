"""TJ-018.3 晋级 P1 终局化登记册密封专项（对密封原文执行）。

核验链：钉定快照哈希 → 两阶段复放重建 S2 基线文本并验钉 →
S3 应用文本逐字核对（822 位点实际字全量、S3 context 哈希全量）
→ 应用报告 origin 图对账（dispositions 位点与处置、46 条携带
交叠的 context 全文/哈希）→ 候选 JSON 逐条对齐（含见证原文）。
本专项只读密封资产，不改任何文本与候选记录。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_finalization as fin
from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = fin.FINALIZATION_REGISTER
ENTRIES = REG["entries"]
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


class TestFinalizationSealed(unittest.TestCase):
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
        self.assertEqual(
            hashlib.sha256(rawr).hexdigest(),
            "691ccb60b61534f60024843a5a5e692aa70d967c5a1939"
            "d70c2e8814d23e914b")

    def test_entries_match_sealed_candidates(self):
        self.assertEqual(len(self.cands), 993)
        for e in ENTRIES:
            cand = self.cands[e["seq"] - 1]
            self.assertEqual(e["status"], cand["status"], e["seq"])
            self.assertEqual(e["volume"], int(cand["volume"]), e["seq"])
            self.assertIsNone(cand["correction_id"], e["seq"])
            self.assertEqual(e["site_s2"],
                             int(cand["baseline_character_offset"]), e["seq"])
            self.assertEqual(e["s2_reading"], cand["old"], e["seq"])
            self.assertEqual(e["historical_reading"],
                             cand["historical_reading"], e["seq"])
            self.assertEqual(RE[e["seq"]]["context"], cand["context"],
                             e["seq"])
            self.assertEqual(e["historical_witnesses"],
                             cand.get("historical_evidence") or [], e["seq"])
            self.assertEqual(e["crosscheck_witnesses"],
                             cand.get("crosscheck_evidence") or [], e["seq"])

    def test_origin_map_against_report(self):
        disp = {d["seq"]: d
                for d in self.report["candidate_annex"]["dispositions"]}
        self.assertEqual(len(disp), 993)
        for seq, d in disp.items():
            self.assertEqual(d["site_s2_offset"], RE[seq]["basis_offset"],
                             seq)
        for e in ENTRIES:
            d = disp[e["seq"]]
            self.assertEqual(d["site_s3_offset"], e["site_s3"], e["seq"])
            self.assertEqual(d["disposition"],
                             "deferred_to_P1_finalization_batch", e["seq"])
            self.assertEqual(d["site_state_in_S3"], e["s3_reading"],
                             e["seq"])
            self.assertEqual(d["flags"]["in_context_carry_76"],
                             e["in_context_carry_76"], e["seq"])
            self.assertFalse(d["flags"]["confirmed_applied_reconciled"],
                             e["seq"])
            self.assertFalse(d["flags"]["in_reading_disagreement_12"],
                             e["seq"])

    def test_s2_verbatim(self):
        for e in ENTRIES:
            off = e["site_s2"]
            self.assertEqual(self.s2[off:off + len(e["s2_reading"])],
                             e["s2_reading"], e["seq"])
            cs, ce = e["context_span_s2"]
            self.assertEqual(self.s2[cs:ce], RE[e["seq"]]["context"],
                             e["seq"])
            self.assertEqual(_sha(self.s2[cs:ce]), e["context_s2_sha256"],
                             e["seq"])

    def test_s3_verbatim_full(self):
        for e in ENTRIES:
            off = e["site_s3"]
            self.assertEqual(self.s3[off:off + len(e["s3_reading"])],
                             e["s3_reading"], e["seq"])
            cs, ce = e["context_span_s3"]
            self.assertEqual(_sha(self.s3[cs:ce]), e["context_s3_sha256"],
                             e["seq"])

    def test_carry_overlap_matches_report(self):
        carry = {c["seq"]: c
                 for c in self.report["candidate_annex"]["context_carry"]}
        self.assertEqual(len(carry), 76)
        self.assertEqual(
            self.report["candidate_annex"]["context_carry_limitations"], [])
        checked = 0
        for e in ENTRIES:
            if not e["in_context_carry_76"]:
                continue
            c = carry[e["seq"]]
            self.assertEqual(c["s3_context_span"], e["context_span_s3"],
                             e["seq"])
            self.assertEqual(c["context_final_sha256"],
                             e["context_s3_sha256"], e["seq"])
            self.assertEqual(c["baseline_context_sha256"],
                             e["context_s2_sha256"], e["seq"])
            cs, ce = e["context_span_s3"]
            self.assertEqual(self.s3[cs:ce], c["s3_context"], e["seq"])
            checked += 1
        self.assertEqual(checked, 46)


if __name__ == "__main__":
    unittest.main()
