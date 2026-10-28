"""TJ-018.3 晋级前置「正式应用批」设计审定密封专项（对密封原文执行）。

核验链：五件冻结对象文件哈希 → 快照统计（PUA/防/□）→ 两阶段
忠实复放（仓库脚本全语义：逐码位计数断言、语境锚串恰 1 次、
文本锚串恰 1 次 + 目标预存校验 + 豁免集钉测）→ S1 钉值 →
444 检查点 == S2 钉值（重锚登记册）→ 全量 603 == S3 钉值
（防 769 且 ±6 语境全互异、□ 2）→ 候选分布与 confirmed 集合
→ RD-12 位点字在 S3 与基线中均未被应用改动 → PUA 审计文件
无逐码位状态字段且 identified == 缺口 2 条。本专项只读密封
资产，复放只在内存进行，不写任何文件。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_formal_application as fa

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = fa.FORMAL_APPLICATION_DESIGN_REGISTER
FREEZE = {f["object"]: f for f in fa.FREEZE_REGISTER}
PINS = {p["stage_id"]: p for p in fa.STAGE_TEXT_PINS}


def _file_sha(name):
    return hashlib.sha256((SNAPSHOT_DIR / name).read_bytes()).hexdigest()


def _load(name):
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_pua(ch):
    cp = ord(ch)
    return 0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD \
        or 0x100000 <= cp <= 0x10FFFD


def _replay(snapshot, pua_spec, corrections, upto=None):
    """两阶段忠实复放（脚本全规则）。返回 (text, applied_ids, exemptions)。"""
    text = snapshot
    for row in pua_spec.get("mappings", []):
        if row.get("status") != "confirmed":
            continue
        assert text.count(row["glyph"]) == int(row["count"]), row["codepoint"]
        text = text.replace(row["glyph"], row["replacement"])
    for row in pua_spec.get("contextual_mappings", []):
        if row.get("status") != "confirmed":
            continue
        assert text.count(row["glyph"]) == int(row["count"]), row["codepoint"]
        for rule in row["replacements"]:
            assert text.count(rule["old"]) == 1, row["codepoint"]
            text = text.replace(rule["old"], rule["new"], 1)
        assert row["glyph"] not in text, row["codepoint"]
    assert not any(_is_pua(c) for c in text), "PUA remains after stage 1"
    applied, exemptions = [], set()
    for row in corrections:
        if upto is not None and int(row["id"].split("-")[1]) > upto:
            continue
        if row.get("status") != "confirmed":
            continue
        old, new = row["old"], row["new"]
        assert not any(_is_pua(c) for c in old + new), row["id"]
        assert text.count(old) == 1, row["id"]
        if text.count(new):
            assert row.get("allow_existing_target"), row["id"]
            exemptions.add(row["id"])
        text = text.replace(old, new, 1)
        applied.append(row["id"])
    return text, applied, exemptions


class SealedFormalApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes() \
            .decode("utf-8")
        cls.pua = _load("sanming_pua_collation.json")
        cls.coll = _load("sanming_text_collation.json")
        cls.cand = _load("sanming_ocr_candidates.json")
        cls.audit = _load("sanming_pua_audit.json")
        cls.stage1, _, _ = _replay(cls.snapshot, cls.pua, [])
        cls.baseline, cls.applied444, _ = _replay(
            cls.snapshot, cls.pua, cls.coll["corrections"], upto=444)
        cls.final, cls.applied603, cls.exemptions = _replay(
            cls.snapshot, cls.pua, cls.coll["corrections"])

    def test_freeze_file_hashes(self):
        names = {
            "snapshot_text": "sanming_tonghui.txt",
            "pua_collation": "sanming_pua_collation.json",
            "text_collation": "sanming_text_collation.json",
            "ocr_candidates": "sanming_ocr_candidates.json",
            "pua_audit": "sanming_pua_audit.json",
        }
        for obj, name in names.items():
            self.assertEqual(_file_sha(name), FREEZE[obj]["sha256"], obj)

    def test_snapshot_statistics(self):
        t = self.snapshot
        self.assertEqual(len(t), 461157)
        self.assertEqual(sum(1 for c in t if _is_pua(c)), 524)
        self.assertEqual(
            len({c for c in t if _is_pua(c)}), 86)
        self.assertEqual(t.count("防"), 1606)
        self.assertEqual(t.count("□"), 2)

    def test_pua_spec_shape(self):
        self.assertEqual(len(self.pua["mappings"]), 85)
        self.assertTrue(
            all(m["status"] == "confirmed" for m in self.pua["mappings"]))
        self.assertEqual(
            sum(int(m["count"]) for m in self.pua["mappings"]), 519)
        ctx = self.pua["contextual_mappings"]
        self.assertEqual(len(ctx), 1)
        self.assertEqual(ctx[0]["codepoint"], "U+E7E8")
        self.assertEqual(int(ctx[0]["count"]), 5)
        self.assertEqual(len(ctx[0]["replacements"]), 4)
        self.assertEqual(self.pua["summary"]["confirmed_mappings"], 86)
        self.assertEqual(self.pua["summary"]["confirmed_occurrences"], 524)

    def test_stage1_pin(self):
        s1 = PINS["S1"]
        self.assertEqual(len(self.stage1), s1["chars"])
        self.assertEqual(_sha(self.stage1), s1["sha256"])
        self.assertEqual(self.stage1.count("防"), 1606)
        self.assertEqual(self.stage1.count("□"), 2)

    def test_collation_spec_shape(self):
        corr = self.coll["corrections"]
        self.assertEqual(len(corr), 603)
        self.assertEqual([c["id"] for c in corr],
                         ["ocr-%03d" % i for i in range(1, 604)])
        self.assertTrue(all(c["status"] == "confirmed" for c in corr))
        self.assertEqual(
            [c["id"] for c in corr if c.get("allow_existing_target")],
            ["ocr-022"])
        self.assertEqual(
            [(c["id"], len(c["old"]), len(c["new"]))
             for c in corr if len(c["old"]) != len(c["new"])],
            [("ocr-017", 16, 15)])
        self.assertEqual(self.coll["summary"]["review_status"], "in_progress")
        self.assertFalse(self.coll["summary"]["canonical_ready"])
        self.assertEqual(
            sum(1 for c in corr if self.snapshot.count(c["old"]) == 1), 537)
        self.assertEqual(
            sum(1 for c in corr if self.snapshot.count(c["old"]) == 0), 66)

    def test_baseline_checkpoint_pin(self):
        self.assertEqual(len(self.applied444), 444)
        s2 = PINS["S2"]
        self.assertEqual(len(self.baseline), s2["chars"])
        self.assertEqual(_sha(self.baseline), s2["sha256"])
        self.assertEqual(self.baseline.count("防"), 925)

    def test_final_pin_and_residuals(self):
        self.assertEqual(len(self.applied603), 603)
        self.assertEqual(self.exemptions, {"ocr-022"})
        s3 = PINS["S3"]
        self.assertEqual(len(self.final), s3["chars"])
        self.assertEqual(len(self.final.encode("utf-8")), s3["bytes"])
        self.assertEqual(_sha(self.final), s3["sha256"])
        self.assertEqual(self.final.count("防"), 769)
        self.assertEqual(self.final.count("□"), 2)
        pos = [i for i, c in enumerate(self.final) if c == "防"]
        wins = {self.final[max(0, p - 6):p + 7] for p in pos}
        self.assertEqual(len(wins), 769)

    def test_candidates_shape(self):
        cands = self.cand["candidates"]
        self.assertEqual(len(cands), 993)
        from collections import Counter
        self.assertEqual(
            Counter(c["status"] for c in cands),
            Counter({"historical_only_hold": 775, "variant_preserve": 47,
                     "confirmed_applied": 159,
                     "reading_disagreement_hold": 12}))
        conf = sorted(c["correction_id"] for c in cands
                      if c["status"] == "confirmed_applied")
        self.assertEqual(conf, ["ocr-%03d" % i for i in range(445, 604)])
        self.assertEqual(self.cand["offset_basis"],
                         FREEZE["ocr_candidates"]["measured_facts"]
                         ["offset_basis"])

    def test_reading_disagreement_sites_untouched(self):
        items = fa.READING_DISAGREEMENT_SPEC["items"]
        self.assertEqual(len(items), 12)
        for it in items:
            off = it["basis_offset"]
            self.assertEqual(self.baseline[off], it["old"], it["seq"])
            self.assertEqual(self.final[off], it["old"], it["seq"])

    def test_pua_audit_gap_and_no_status_field(self):
        glyphs = self.audit["glyphs"]
        self.assertEqual(len(glyphs), 86)
        self.assertTrue(all("status" not in g for g in glyphs))
        self.assertEqual(self.audit["total_private_use_chars"], 524)
        self.assertEqual(self.audit["unique_private_use_chars"], 86)
        identified = self.audit[
            "replacement_char_corrections_already_identified"]
        self.assertEqual(len(identified), 2)
        self.assertEqual(
            {g["from"] for g in identified},
            {g["from"] for g in fa.PERMANENT_GAPS["items"]})


if __name__ == "__main__":
    unittest.main()
