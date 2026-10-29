"""TJ-018.3 正式应用批 phase 0「PUA 86/86 全核」密封专项（对密封原文执行）。

核验链：快照哈希钉值 → 逐码位快照实测计数与登记计数、密封校勘
表计数三方对账（85 条 uniform、合计 519）→ 登记替换与校勘表
逐字一致（含 U+E7E8 语境规则 old/new）→ 全书 PUA 合计 524 处 /
86 码位与 PUA 审计文件 totals 一致 → 审计文件 glyphs 条目无逐
码位裁定状态字段（只有 codepoint/contexts/count/glyph）→ 语境
规则 old 串在快照中各恰 1 见、U+E7E8 合计 5 处 → 登记的未见证
位点与 disputed 异读位点在快照中确为对应 PUA 字。本专项只读
密封资产，不写任何文件。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_pua_verification as pv

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = pv.PUA_FULL_VERIFICATION_REGISTER
VERDICTS = {e["codepoint"]: e for e in pv.CODEPOINT_VERDICTS}


def _load(name):
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


class TestSnapshotPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        cls.text = cls.raw.decode("utf-8")

    def test_snapshot_hash_and_size(self):
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest(),
            "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86")
        self.assertEqual(len(self.raw), 1342659)
        self.assertEqual(len(self.text), 461157)

    def test_pua_totals(self):
        def is_pua(ch):
            return 0xE000 <= ord(ch) <= 0xF8FF
        counts = Counter(c for c in self.text if is_pua(c))
        self.assertEqual(sum(counts.values()), 524)
        self.assertEqual(len(counts), 86)


class TestCountReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_text(encoding="utf-8")
        cls.collation = _load("sanming_pua_collation.json")
        cls.audit = _load("sanming_pua_audit.json")

    def test_per_codepoint_three_way_counts(self):
        mappings = {m["codepoint"]: m for m in self.collation["mappings"]}
        self.assertEqual(len(mappings), 85)
        self.assertEqual(set(mappings), set(VERDICTS))
        total = 0
        for cp, e in VERDICTS.items():
            glyph = chr(int(cp[2:], 16))
            measured = self.text.count(glyph)
            self.assertEqual(measured, e["snapshot_count"], cp)
            self.assertEqual(measured, int(mappings[cp]["count"]), cp)
            self.assertEqual(measured, e["registered_count"], cp)
            total += measured
        self.assertEqual(total, 519)

    def test_replacements_match_collation_verbatim(self):
        mappings = {m["codepoint"]: m for m in self.collation["mappings"]}
        for cp, e in VERDICTS.items():
            self.assertEqual(e["replacement"], mappings[cp]["replacement"], cp)
            self.assertEqual(mappings[cp]["status"], "confirmed", cp)

    def test_audit_totals_and_no_status_field(self):
        self.assertEqual(self.audit["total_private_use_chars"], 524)
        self.assertEqual(self.audit["unique_private_use_chars"], 86)
        self.assertEqual(len(self.audit["glyphs"]), 86)
        for g in self.audit["glyphs"]:
            self.assertEqual(set(g), {"codepoint", "contexts", "count", "glyph"})
            cp = g["codepoint"]
            if cp in VERDICTS:
                self.assertEqual(int(g["count"]), VERDICTS[cp]["snapshot_count"], cp)

    def test_contextual_rules_against_snapshot_and_collation(self):
        ctx = self.collation["contextual_mappings"]
        self.assertEqual(len(ctx), 1)
        self.assertEqual(ctx[0]["codepoint"], "U+E7E8")
        rules = ctx[0]["replacements"]
        self.assertEqual(len(rules), 4)
        self.assertEqual(len(pv.CONTEXTUAL_VERDICTS), 4)
        for reg_rule, col_rule in zip(pv.CONTEXTUAL_VERDICTS, rules):
            self.assertEqual(reg_rule["old"], col_rule["old"])
            self.assertEqual(reg_rule["new"], col_rule["new"])
            self.assertEqual(self.text.count(reg_rule["old"]), 1)
            self.assertEqual(
                reg_rule["loci_offsets"],
                [self.text.find(reg_rule["old"])])
        self.assertEqual(self.text.count("\ue7e8"), 5)
        self.assertEqual(int(ctx[0]["count"]), 5)

    def test_registered_offsets_hold_the_glyph(self):
        for cp, e in VERDICTS.items():
            glyph = chr(int(cp[2:], 16))
            for off in e["unattested_loci_offsets"]:
                self.assertEqual(self.text[off], glyph, (cp, off))
            for off in e["representative_attested_offsets"]:
                self.assertEqual(self.text[off], glyph, (cp, off))
            for r in e["rival_readings"]:
                for off in r["loci"]:
                    self.assertEqual(self.text[off], glyph, (cp, off))
            for n in e["locus_notes"]:
                off = n.get("raw_offset")
                if off is not None:
                    self.assertEqual(self.text[off], glyph, (cp, off))


if __name__ == "__main__":
    unittest.main()
