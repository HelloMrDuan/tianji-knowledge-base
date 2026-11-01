"""TJ-018.3 阳刃节「凶/㓙」勘误登记（E0354）：公开治理测试。

登记模块 ``bazi_sanming_yangren_errata`` 为纯数据、零函数、不被任何
可执行路径 import；本测试只钉登记的在册形制：勘误恰 2 条且枚举恰等
（位点、校勘记、读法、状态），与卷五校勘册逐项对平，25 处复核集与
校勘册同节「防→㓙」全集恰等且结论计数对平，影响面（两引文非 r035
绑定）断言，以及登记文档在册。S3 应用字的机上直读实证与 B-2 密封
枚举钉在密封专项 ``tests/test_phase2_baziluren.py``（离线验收，不进
公开 CI），本批未动该钉。
"""

from __future__ import annotations

import ast
import unittest
from collections import Counter
from pathlib import Path

from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as juan5
from tianji_kb import bazi_sanming_yangren_errata as errata
from tianji_kb.bazi_pattern import LUREN_QUOTES

ROOT = Path(__file__).resolve().parents[1]
REG = errata.YANGREN_ERRATA_REGISTER


class YangrenErrataRegistrationTests(unittest.TestCase):
    def test_register_present_and_pinned(self):
        self.assertEqual(REG["id"], "sanming-yangren-errata-register-v1")
        self.assertEqual(REG["ledger_event"], "E0354")
        self.assertEqual(REG["ledger_row"], "TJ-018.2")
        self.assertEqual(REG["kind"], "collation_errata_registration")
        self.assertEqual(REG["canonical_section_id"], "bazi.section.s064")
        self.assertEqual(REG["register_section_id"],
                         "sanming.juan5.yangren")

    def test_module_is_pure_data(self):
        tree = ast.parse(
            (ROOT / "src" / "tianji_kb" / "bazi_sanming_yangren_errata.py")
            .read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, (ast.FunctionDef,
                                            ast.AsyncFunctionDef,
                                            ast.ClassDef))

    def test_errata_exactly_two_and_enumerated(self):
        self.assertEqual(len(errata.ERRATA), 2)
        self.assertEqual({e["id"] for e in errata.ERRATA},
                         {"sm5y-errata-182078", "sm5y-errata-182375"})
        self.assertEqual(
            {(e["position"]["quote_id"],
              e["position"]["char_index_in_quote"])
             for e in errata.ERRATA},
            {("yr.ersha", 6), ("yr.he_xing", 16)})
        for e in errata.ERRATA:
            self.assertEqual(e["status"], "registered_unapplied")
            self.assertEqual(e["deviation_characterization"],
                             "application_deviation")
            self.assertEqual(e["snapshot_glyph"], "防")
            self.assertEqual(e["registered_reading"]["reading"], "㓙")
            self.assertEqual(e["application_current"]["applied_glyph"],
                             "凶")
            self.assertEqual(e["position"]["s3_offset"],
                             e["position"]["s0_offset"] - 1)

    def test_errata_cross_checked_against_collation_register(self):
        notes = {n["id"]: n for n in juan5.COLLATION_NOTES}
        for e in errata.ERRATA:
            src = notes[e["collation_ref"]]
            self.assertEqual(src["section_id"], "sanming.juan5.yangren")
            self.assertEqual(src["char_offset"],
                             e["position"]["s0_offset"])
            self.assertEqual(src["snapshot_glyph"], "防")
            self.assertEqual(src["reading"], "㓙")
            self.assertEqual(src["reading_status"], "confirmed")
            self.assertEqual(src["usable_grade"], "Q1")
            self.assertEqual(src["disposition"], "corrected")
            self.assertEqual(e["position"]["context_short"],
                             src["context_short"])
            self.assertEqual(e["witness_basis"], src["basis"])
            self.assertEqual(len(e["witness_basis"]), 2)

    def test_section_review_matches_collation_full_set(self):
        expected = sorted(
            n["char_offset"] for n in juan5.COLLATION_NOTES
            if n["section_id"] == "sanming.juan5.yangren"
            and n.get("snapshot_glyph") == "防"
            and n.get("reading") == "㓙")
        self.assertEqual(len(expected), 25)
        self.assertEqual([r["s0_offset"] for r in errata.SECTION_REVIEW],
                         expected)
        counts = Counter(r["conclusion"] for r in errata.SECTION_REVIEW)
        self.assertEqual(counts["applied_as_registered"], 17)
        self.assertEqual(counts["residual_snapshot_glyph_retained"], 6)
        self.assertEqual(counts["divergent_applied_xiong"], 2)
        divergent_offsets = {
            r["s0_offset"] for r in errata.SECTION_REVIEW
            if r["conclusion"] == "divergent_applied_xiong"}
        self.assertEqual(divergent_offsets, {182078, 182375})
        self.assertEqual(
            divergent_offsets,
            {e["position"]["s0_offset"] for e in errata.ERRATA})
        summary = errata.SECTION_REVIEW_SUMMARY
        self.assertEqual(summary["positions_reviewed"], 25)
        self.assertEqual(summary["applied_as_registered"], 17)
        self.assertEqual(summary["residual_snapshot_glyph_retained"], 6)
        self.assertEqual(summary["divergent_applied_xiong"], 2)
        self.assertEqual(summary["other"], 0)

    def test_divergent_quotes_are_not_r035_bound(self):
        bound_ids = {q["id"] for q in LUREN_QUOTES}
        self.assertEqual(len(bound_ids), 4)
        self.assertNotIn("yr.ersha", bound_ids)
        self.assertNotIn("yr.he_xing", bound_ids)

    def test_document_on_file(self):
        doc = (ROOT / "docs" / "product" / "TJ0183_YANGREN_ERRATA.md") \
            .read_text(encoding="utf-8")
        self.assertIn("sanming-yangren-errata-register-v1", doc)
        self.assertIn("sm5y-errata-182078", doc)
        self.assertIn("sm5y-errata-182375", doc)
        self.assertIn("registered_unapplied", doc)


if __name__ == "__main__":
    unittest.main()
