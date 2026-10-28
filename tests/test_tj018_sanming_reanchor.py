"""TJ-018 993 条跨本候选重锚登记册公开结构测试（不依赖密封资产）。

只核对登记册自身的形制与计数自洽；逐字核验与往返校验在密封专项
``test_tj018_sanming_reanchor_sealed`` 中对密封原文执行。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_reanchor as ra

ROOT = Path(__file__).resolve().parents[1]
REG = ra.REANCHOR_REGISTER
ENTRIES = REG["entries"]


class TestRegisterShape(unittest.TestCase):
    def test_register_identity(self):
        self.assertEqual(REG["register_id"],
                         "sanming-ocr-candidates-reanchor-register-v1")
        self.assertEqual(REG["snapshot"]["chars"], 461157)
        self.assertEqual(
            REG["snapshot"]["sha256"],
            "00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86")
        self.assertEqual(REG["basis_text"]["chars"], 461156)

    def test_total_and_seq_continuity(self):
        self.assertEqual(len(ENTRIES), 993)
        self.assertEqual([e["seq"] for e in ENTRIES], list(range(1, 994)))
        self.assertEqual(REG["summary"]["total"], 993)

    def test_status_counts(self):
        counts = Counter(e["status"] for e in ENTRIES)
        self.assertEqual(counts, Counter({
            "historical_only_hold": 775,
            "variant_preserve": 47,
            "confirmed_applied": 159,
            "reading_disagreement_hold": 12,
        }))
        self.assertEqual(REG["summary"]["status_counts"], dict(counts))

    def test_anchor_class_counts_sum_to_total(self):
        ctx = Counter(e["context_anchor_class"] for e in ENTRIES)
        site = Counter(e["site_anchor_class"] for e in ENTRIES)
        self.assertEqual(ctx, Counter({
            "anchored_direct": 900,
            "anchored_through_edits": 17,
            "unanchorable_crosses_boundary": 76,
        }))
        # 位点零不可锚：只允许两类
        self.assertEqual(site, Counter({
            "anchored_direct": 942,
            "anchored_within_single_edit": 51,
        }))
        self.assertEqual(sum(ctx.values()), 993)
        self.assertEqual(sum(site.values()), 993)
        self.assertEqual(REG["summary"]["context_anchor_counts"], dict(ctx))
        self.assertEqual(REG["summary"]["site_anchor_counts"], dict(site))

    def test_context_digest_and_site_position(self):
        for e in ENTRIES:
            ctx = e["context"]
            self.assertEqual(
                hashlib.sha256(ctx.encode("utf-8")).hexdigest(),
                e["context_sha256"], e["seq"])
            self.assertTrue(28 <= len(ctx) <= 59, e["seq"])
            d = e["site_in_context"]
            self.assertEqual(ctx[d:d + len(e["old"])], e["old"], e["seq"])
            s, en = e["context_span_basis"]
            self.assertEqual(en - s, len(ctx), e["seq"])
            self.assertEqual(s + d, e["basis_offset"], e["seq"])

    def test_anchor_fields_consistent(self):
        for e in ENTRIES:
            cls = e["context_anchor_class"]
            if cls == "unanchorable_crosses_boundary":
                self.assertIsNone(e["context_snapshot_span"], e["seq"])
                self.assertTrue(e["context_edits_crossed"], e["seq"])
                for rel in e["context_edits_crossed"].values():
                    self.assertIn(rel, ("partial_overlap", "contained_within"))
            else:
                lo, hi = e["context_snapshot_span"]
                self.assertTrue(0 <= lo < hi <= 461157, e["seq"])
                if cls == "anchored_through_edits":
                    self.assertTrue(e["context_edits_covered"], e["seq"])
                else:
                    self.assertEqual(e["context_edits_covered"], [], e["seq"])
            slo, shi = e["site_snapshot_span"]
            self.assertTrue(0 <= slo < shi <= 461157, e["seq"])
            if e["site_anchor_class"] == "anchored_within_single_edit":
                self.assertTrue(e["site_edit"].startswith("ocr-"), e["seq"])
            else:
                self.assertIsNone(e["site_edit"], e["seq"])

    def test_confirmed_applied_correction_linkage(self):
        ids = sorted(e["correction_id"] for e in ENTRIES
                     if e["status"] == "confirmed_applied")
        self.assertEqual(ids, ["ocr-%03d" % i for i in range(445, 604)])
        for e in ENTRIES:
            if e["status"] != "confirmed_applied":
                self.assertIsNone(e["correction_id"], e["seq"])

    def test_golden_mirror(self):
        golden = json.loads(
            (ROOT / "tests" / "golden_tj018_sanming_reanchor.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(golden, REG)


if __name__ == "__main__":
    unittest.main()
