"""TJ-012.3 Slice D 前置密封快照专项：渊海子平正官组三节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_zhengguan`` 登记的引文（24 条）、含缺字段（2 条）与
既有 s055–s059 窗口（5 条）对机上快照做切片逐字等值 + 全文计数
==1 复核；两节全文窗切片等值；缺字对账——三节范围内半角 ? 位点
与登记 5 条逐位相等、全书 ? 总数 36；字形位点（茍、节题、死官）
钉位；来源普查钉值（101 条，C 95 / D 6）与渊海 review_scope
新增段落钉值。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_zhengguan as yh

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
        for s in yh.YUANHAI_SECTIONS:
            if s["full_text"] is None:
                continue
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        self.assertTrue(text[9703:].startswith("《正 官 论》"))
        self.assertTrue(
            text[10321:].startswith("《诗诀》★正官须在月中求"))
        self.assertTrue(text[12400:].startswith("《论 官 杀 混 杂 要 制 伏》"))
        self.assertTrue(text[12506:].startswith("论 印 綬》"))
        self.assertTrue(
            text[13494:].startswith("《诗诀》★月逢印綬喜官星"))


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (yh.YUANHAI_ZHENGGUAN_QUOTES
                      + yh.YUANHAI_CONTEXT_QUOTES
                      + yh.YUANHAI_LEGACY_WINDOWS)
        self.assertEqual(len(all_quotes), 31)
        for q in all_quotes:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        zg = [i for i in range(9703, 10321) if text[i] == "?"]
        gs = [i for i in range(12400, 12506) if text[i] == "?"]
        ys = [i for i in range(12506, 13494) if text[i] == "?"]
        self.assertEqual(zg, [9873, 9879, 9947])
        self.assertEqual(gs, [])
        self.assertEqual(ys, [12518, 12557])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_GAP_REGISTER)
        self.assertEqual(registered, sorted(zg + ys))

    def test_gap_contexts_slice_equal(self) -> None:
        text = _text()
        for g in yh.YUANHAI_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[9889], "茍")
        self.assertEqual(text[12506:12512], "论 印 綬》")
        self.assertEqual(text[12453:12455], "死官")
        # 言之 / 论 duplicate pair, separately located, never merged
        self.assertEqual(text[12721:12744],
                         "虽喜官鬼,而官鬼多或入格,又不可专以印綬言之。")
        self.assertEqual(text[13012:13031],
                         "若官鬼多,或入别格,又不可专以印綬论。")


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 96)
        self.assertEqual(levels.count("D"), 6)

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("本批（TJ-012.3 Slice D 前置）整节登记《正官论》",
                       "《论官杀混杂要制伏》",
                       "placeholder_unresolved",
                       "仍不可裁定"):
            self.assertIn(marker, scope)


if __name__ == "__main__":
    unittest.main()
