"""TJ-018 993 条跨本候选重锚登记册密封专项（对密封原文执行）。

核验链：钉定快照哈希 → 以仓库脚本口径两阶段复放重建基线文本
（PUA 86 映射 + ocr-001..444）并与登记册钉值逐字比对 → 逐条
候选与密封候选 JSON 对齐、位点/context 在基线文本中逐字核验
→ 可锚条目往返校验（快照区间正向映射 == 登记 context；单订正
内位点的前像校验）。本专项只读密封资产，不应用任何候选。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = ra.REANCHOR_REGISTER
E7E8 = "\ue7e8"


def _load(name):
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def _snapshot():
    return (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes().decode("utf-8")


def _is_pua(ch):
    cp = ord(ch)
    return 0xE000 <= cp <= 0xF8FF or 0xF0000 <= cp <= 0xFFFFD or 0x100000 <= cp <= 0x10FFFD


def _replay_basis(snapshot, pua_spec, corrections):
    """两阶段忠实复放（脚本全规则：计数断言 + 目标预存校验）。"""
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


def _pua_forward(text, pua_spec):
    """快照区间正向 PUA 映射：语境规则先行，其后统一映射逐字翻译。"""
    for row in pua_spec.get("contextual_mappings", []):
        if row.get("status") != "confirmed":
            continue
        for rule in row["replacements"]:
            if rule["old"] in text:
                text = text.replace(rule["old"], rule["new"], 1)
    uni = {m["glyph"]: m["replacement"]
           for m in pua_spec.get("mappings", []) if m.get("status") == "confirmed"}
    return "".join(uni.get(ch, ch) for ch in text)


class TestReanchorSealed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = _snapshot()
        cls.pua = _load("sanming_pua_collation.json")
        cls.col = _load("sanming_text_collation.json")
        cls.colmap = {c["id"]: c for c in cls.col["corrections"]}
        cls.cands = _load("sanming_ocr_candidates.json")["candidates"]
        cls.basis = _replay_basis(cls.snapshot, cls.pua, cls.col["corrections"])

    def test_snapshot_and_basis_identity(self):
        raw = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         REG["snapshot"]["sha256"])
        self.assertEqual(len(self.snapshot), REG["snapshot"]["chars"])
        self.assertEqual(len(self.basis), REG["basis_text"]["chars"])
        self.assertEqual(
            hashlib.sha256(self.basis.encode("utf-8")).hexdigest(),
            REG["basis_text"]["sha256"])

    def test_register_matches_sealed_candidates(self):
        self.assertEqual(len(self.cands), 993)
        for entry, cand in zip(REG["entries"], self.cands):
            self.assertEqual(entry["volume"], int(cand["volume"]))
            self.assertEqual(entry["status"], cand["status"])
            self.assertEqual(entry["correction_id"], cand["correction_id"])
            self.assertEqual(entry["basis_offset"],
                             int(cand["baseline_character_offset"]))
            self.assertEqual(entry["old"], cand["old"])
            self.assertEqual(entry["historical_reading"],
                             cand["historical_reading"])
            self.assertEqual(entry["context"], cand["context"])

    def test_all_sites_and_contexts_verified_in_basis(self):
        for entry in REG["entries"]:
            off = entry["basis_offset"]
            self.assertEqual(
                self.basis[off:off + len(entry["old"])], entry["old"],
                entry["seq"])
            s, e = entry["context_span_basis"]
            self.assertEqual(self.basis[s:e], entry["context"], entry["seq"])

    def test_direct_contexts_roundtrip(self):
        checked = 0
        for entry in REG["entries"]:
            if entry["context_anchor_class"] != "anchored_direct":
                continue
            lo, hi = entry["context_snapshot_span"]
            fwd = _pua_forward(self.snapshot[lo:hi], self.pua)
            if fwd != entry["context"]:
                # 仅允许差异落在 U+E7E8 语境映射位点（其读法取决于
                # 更宽语境，区间外语境不入本校验）
                self.assertEqual(len(fwd), len(entry["context"]), entry["seq"])
                for a, b, raw in zip(fwd, entry["context"],
                                     self.snapshot[lo:hi]):
                    self.assertTrue(a == b or raw == E7E8,
                                    (entry["seq"], a, b))
            checked += 1
        self.assertEqual(checked, 900)

    def test_through_edits_contexts_roundtrip(self):
        checked = 0
        for entry in REG["entries"]:
            if entry["context_anchor_class"] != "anchored_through_edits":
                continue
            lo, hi = entry["context_snapshot_span"]
            text = _pua_forward(self.snapshot[lo:hi], self.pua)
            for cid in sorted(entry["context_edits_covered"],
                              key=lambda x: int(x.split("-")[1])):
                corr = self.colmap[cid]
                self.assertIn(corr["old"], text, (entry["seq"], cid))
                text = text.replace(corr["old"], corr["new"], 1)
            self.assertEqual(text, entry["context"], entry["seq"])
            checked += 1
        self.assertEqual(checked, 17)

    def test_direct_sites_roundtrip(self):
        checked = 0
        for entry in REG["entries"]:
            if entry["site_anchor_class"] != "anchored_direct":
                continue
            lo, hi = entry["site_snapshot_span"]
            self.assertEqual(hi - lo, len(entry["old"]), entry["seq"])
            fwd = _pua_forward(self.snapshot[lo:hi], self.pua)
            self.assertEqual(fwd, entry["old"], entry["seq"])
            checked += 1
        self.assertEqual(checked, 942)

    def test_within_edit_sites_preimage(self):
        checked = 0
        for entry in REG["entries"]:
            if entry["site_anchor_class"] != "anchored_within_single_edit":
                continue
            lo, hi = entry["site_snapshot_span"]
            eid = entry["site_edit"]
            enum = int(eid.split("-")[1])
            text = _pua_forward(self.snapshot[lo:hi], self.pua)
            for corr in self.col["corrections"]:
                n = int(corr["id"].split("-")[1])
                if n >= enum or n > 444:
                    continue
                if corr["old"] in text:
                    text = text.replace(corr["old"], corr["new"], 1)
            self.assertEqual(text, self.colmap[eid]["old"], entry["seq"])
            checked += 1
        self.assertEqual(checked, 51)

    def test_crossed_entries_reference_basis_edits(self):
        checked = 0
        for entry in REG["entries"]:
            if entry["context_anchor_class"] != "unanchorable_crosses_boundary":
                continue
            self.assertIsNone(entry["context_snapshot_span"])
            for cid in entry["context_edits_crossed"]:
                self.assertTrue(1 <= int(cid.split("-")[1]) <= 444, cid)
            checked += 1
        self.assertEqual(checked, 76)

    def test_snapshot_verbatim_findable_count(self):
        found = sum(1 for e in REG["entries"]
                    if self.snapshot.find(e["context"]) >= 0)
        self.assertEqual(found, 748)
        self.assertEqual(
            REG["summary"]["contexts_findable_verbatim_in_snapshot"], 748)


if __name__ == "__main__":
    unittest.main()
