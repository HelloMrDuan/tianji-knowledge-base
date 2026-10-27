"""TJ-013.1 S3 密封快照专项：滴天髓扶抑三段登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_ditiansui_fuyi`` 登记的引文（10 条）、判句（37 条）与方向
表十行对机上滴天髓快照做切片逐字等值 + 全文计数 ==1 复核；方
向表十行在快照内首尾相接重演；疑讹位点（8 项）钉位；同文传录
交叉注记（4 条）对三命/神峰快照切片复核且两赋诀同文对账；来
源普查钉值（101 条，C 95 / D 6）、滴天髓 review_scope 新增段
落钉值、三命/神峰 review_scope 未扩钉值。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ditiansui_fuyi as fy

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]


def _text(name: str) -> str:
    return (SNAP_DIR / name).read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshots_match_registry(self) -> None:
        metas = [("ditiansui_chanwei.txt", fy.DITIANSHUI_SNAPSHOT)]
        metas += [(name, m) for name, m in fy.CROSS_SNAPSHOTS.items()]
        self.assertEqual(len(metas), 3)
        for name, meta in metas:
            raw = (SNAP_DIR / name).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             meta["sha256"], name)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             name)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        self.assertEqual(len(fy.FUYI_QUOTES), 10)
        for q in fy.FUYI_QUOTES:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])

    def test_judgment_sentence_slices(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        total = 0
        for q in fy.FUYI_QUOTES:
            for s in q["judgment_sentences"]:
                total += 1
                loc = s["locator"]
                self.assertEqual(
                    text[loc["char_start"]:loc["char_end"]], s["text"],
                    (q["id"], s["text"]))
        self.assertEqual(total, 37)

    def test_passage_boundaries(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        self.assertTrue(text[39507:].startswith("十七、衰旺"))
        self.assertTrue(text[39534:].startswith("原注:"))
        self.assertTrue(text[39644:].startswith("任氏曰;"))
        # xingxiang passage: verse directly precedes its 原注/任氏曰
        self.assertTrue(text[27065:].startswith("原注:"))
        self.assertTrue(text[27124:].startswith("任氏曰:"))
        # tiyong fuyi passage sits inside the 任氏曰 that starts at 35323
        self.assertTrue(text[35323:].startswith("任氏曰:"))
        self.assertTrue(text[35408:].startswith("玩本文末句云"))
        self.assertTrue(text[35872:].startswith("\n如日主不能为力"))


class DirectionTableSealedTest(unittest.TestCase):
    def test_rows_tile_the_snapshot_segment(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        table = fy.FUYI_DIRECTION_TABLE
        body_loc = table["body_locator"]
        joined = "".join(r["text"] for r in table["rows"])
        self.assertEqual(
            text[body_loc["char_start"]:body_loc["char_end"]], joined)
        for r in table["rows"]:
            loc = r["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], r["text"],
                r["row"])
        self.assertEqual(text.count(joined), 1)


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        for g in fy.FUYI_GLYPH_NOTES:
            if "position" in g:
                self.assertEqual(text[g["position"]], g["char"], g["id"])
            else:
                span = g["span"]
                self.assertEqual(
                    text[span["char_start"]:span["char_end"]],
                    "衰之极者不可所当损者而损之", g["id"])


class CrossReferenceSealedTest(unittest.TestCase):
    def test_cross_reference_slices(self) -> None:
        texts = {name: _text(name) for name in
                 ("sanming_tonghui.txt", "shenfeng_tongkao.txt")}
        for x in fy.FUYI_CROSS_REFERENCES:
            text = texts[x["snapshot_file"]]
            segments = ([{"quote": x["quote"], "locator": x["locator"]}]
                        if "quote" in x else x["segments"])
            for seg in segments:
                loc = seg["locator"]
                self.assertEqual(
                    text[loc["char_start"]:loc["char_end"]],
                    seg["quote"], x["id"])
                self.assertEqual(text.count(seg["quote"]), 1, x["id"])


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 95)
        self.assertEqual(levels.count("D"), 6)

    def test_ditiansui_review_scope_extended(self) -> None:
        src = next(s for s in SOURCES
                   if s["source_id"] == "bazi.source.ditiansui-spouse")
        scope = src["review_scope"]
        for marker in ("本批（TJ-013.1 S3）逐字登记扶抑三段",
                       "quantifier_unthresholded",
                       "快照实测十行",
                       "同文传录",
                       "扶抑仍双重受阻",
                       "不执行任何扶抑判定"):
            self.assertIn(marker, scope)

    def test_sanming_shenfeng_scopes_not_expanded(self) -> None:
        for sid in ("bazi.source.sanmingtonghui", "bazi.source.shenfeng"):
            src = next(s for s in SOURCES if s["source_id"] == sid)
            self.assertNotIn("TJ-013.1 S3", src["review_scope"], sid)
            self.assertNotIn("扶抑三段", src["review_scope"], sid)


if __name__ == "__main__":
    unittest.main()
