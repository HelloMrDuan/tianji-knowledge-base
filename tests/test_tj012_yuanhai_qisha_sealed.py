"""TJ-012.3 Slice D 前置密封快照专项：渊海子平七杀组两节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_qisha`` 登记的引文（21 条）与含缺字段（2 条）对
机上快照做切片逐字等值 + 全文计数 ==1 复核；两节全文窗切片
等值；缺字对账——两节范围内半角 ? 位点与登记 2 条逐位相等、
全书 ? 总数 36；字形位点（生忌无制、元有为好、辛丑并称）钉位；
引用关系 4 条的 locator 对快照切片与正官组登记引文逐字一致
（只验证引用关系成立，不复制登记）；来源普查钉值（101 条，
C 95 / D 6）与渊海 review_scope 新增段落钉值；正官组登记
（bazi_yuanhai_zhengguan）逐字不变回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_qisha as yh
from tianji_kb import bazi_yuanhai_zhengguan as zg

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20" / "yuanhai_ziping.txt")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]


def _text() -> str:
    return SNAPSHOT.read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        raw = SNAPSHOT.read_bytes()
        meta = yh.YUANHAI_SNAPSHOT
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])
        self.assertEqual(meta["chars"], 58905)


class SectionSliceTest(unittest.TestCase):
    def test_full_sections_slice_equal(self) -> None:
        text = _text()
        for s in yh.YUANHAI_QISHA_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # preceding block is the last 诗诀 before 论七杀
        self.assertTrue(
            text[11587:].startswith("《诗诀》★春木无金不是奇"))
        self.assertTrue(text[11627:].startswith("《论 七 杀》"))
        self.assertTrue(text[12285:].startswith("《论 官 星 太 过》"))
        self.assertTrue(
            text[12400:].startswith("《论 官 杀 混 杂 要 制 伏》"))


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (yh.YUANHAI_QISHA_QUOTES
                      + yh.YUANHAI_QISHA_CONTEXT_QUOTES)
        self.assertEqual(len(all_quotes), 23)
        for q in all_quotes:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        qs = [i for i in range(11627, 12285) if text[i] == "?"]
        gt = [i for i in range(12285, 12400) if text[i] == "?"]
        self.assertEqual(qs, [11702, 11955])
        self.assertEqual(gt, [])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_QISHA_GAP_REGISTER)
        self.assertEqual(registered, sorted(qs + gt))

    def test_gap_contexts_slice_equal(self) -> None:
        text = _text()
        for g in yh.YUANHAI_QISHA_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[11668:11672], "生忌无制")
        self.assertEqual(text[12333:12340], "若四柱元有为好")
        self.assertEqual(text[12336], "元")
        self.assertEqual(text[12119:12128], "岁干透出辛丑为七杀")


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        text = _text()
        zg_quotes = {q["id"]: q for q in
                     (zg.YUANHAI_ZHENGGUAN_QUOTES
                      + zg.YUANHAI_LEGACY_WINDOWS)}
        for r in yh.YUANHAI_QISHA_CROSS_REFERENCES:
            target = zg_quotes[r["target_quote_id"]]
            self.assertEqual(r["locator"], target["locator"],
                             r["id"])
            loc = r["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]],
                target["quote"], r["id"])


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 95)
        self.assertEqual(levels.count("D"), 6)

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("七杀组）整节登记《论七杀》",
                       "《论官星太过》",
                       "只登记引用关系",
                       "七杀格成格/破格/真假仍不可裁定",
                       # zhengguan batch markers remain intact
                       "本批（TJ-012.3 Slice D 前置）整节登记《正官论》"):
            self.assertIn(marker, scope)


if __name__ == "__main__":
    unittest.main()
