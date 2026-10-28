"""TJ-012.3 Slice D 前置密封快照专项：渊海子平财组三节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_cai`` 登记的引文（46 条）与含缺字段（3 条）对
机上快照做切片逐字等值 + 全文计数 ==1 复核；三节全文窗切片
等值；缺字对账——三节范围内半角 ? 位点与登记 3 条逐位相等、
全书 ? 总数 36；字形位点（偏财分题标题缺《、自家日本有力、
女貲财、劫财节末版心行）钉位；引用关系 5 条的 locator 对快照
切片与正官组/七杀组登记引文逐字一致（只验证引用关系成立，
不复制登记）；来源普查钉值（101 条，C 95 / D 6）与渊海
review_scope 新增段落钉值；正官组与七杀组登记
（bazi_yuanhai_zhengguan / bazi_yuanhai_qisha）逐字不变回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cai as yh
from tianji_kb import bazi_yuanhai_qisha as qs
from tianji_kb import bazi_yuanhai_zhengguan as zg

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20" / "yuanhai_ziping.txt")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]


def _text() -> str:
    return SNAPSHOT.read_bytes().decode("utf-8")


def _blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob %d\0" % len(raw) + raw).hexdigest()


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        raw = SNAPSHOT.read_bytes()
        meta = yh.YUANHAI_SNAPSHOT
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])
        self.assertEqual(meta["chars"], 58905)
        self.assertEqual(_blob_sha(raw), meta["blob_sha"])
        self.assertEqual(meta["blob_sha"],
                         "f945a48cbedf5883808a72bb6f544a4dca603cb3")


class SectionSliceTest(unittest.TestCase):
    def test_full_sections_slice_equal(self) -> None:
        text = _text()
        for s in yh.YUANHAI_CAI_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # preceding block before 论正财 is the last 诗诀 of the
        # shishen group ([8143] poem: 食神居先杀居后）
        self.assertTrue(
            text[8143:].startswith("《诗诀》★食神居先杀居后"))
        self.assertTrue(text[8183:].startswith("《论 正 财》"))
        # piancai part header in the snapshot lacks the opening 《
        self.assertTrue(text[9330:].startswith("论 偏 财》"))
        self.assertTrue(text[9703:].startswith("《正 官 论》"))
        self.assertTrue(text[14119:].startswith("《论 倒 食》"))
        self.assertTrue(text[14566:].startswith("《论 劫 财》"))
        self.assertTrue(text[14796:].startswith("《论 阳 刃》"))


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (yh.YUANHAI_CAI_QUOTES
                      + yh.YUANHAI_CAI_CONTEXT_QUOTES)
        self.assertEqual(len(all_quotes), 49)
        for q in all_quotes:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        zc = [i for i in range(8183, 9330) if text[i] == "?"]
        pc = [i for i in range(9330, 9703) if text[i] == "?"]
        jc = [i for i in range(14566, 14796) if text[i] == "?"]
        self.assertEqual(zc, [8197])
        self.assertEqual(pc, [9344, 9522])
        self.assertEqual(jc, [])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_CAI_GAP_REGISTER)
        self.assertEqual(registered, sorted(zc + pc + jc))

    def test_gap_contexts_slice_equal(self) -> None:
        text = _text()
        for g in yh.YUANHAI_CAI_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[9330:9336], "论 偏 财》")
        self.assertEqual(text[8300:8306], "自家日本有力")
        self.assertEqual(text[8229:8232], "女貲财")
        self.assertEqual(text[8230], "貲")
        self.assertEqual(text[14783:14793], "【渊海子平】神 煞 ")


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        text = _text()
        pools = {
            "bazi_yuanhai_zhengguan": {
                q["id"]: q for q in
                (zg.YUANHAI_ZHENGGUAN_QUOTES
                 + zg.YUANHAI_LEGACY_WINDOWS)},
            "bazi_yuanhai_qisha": {
                q["id"]: q for q in
                (qs.YUANHAI_QISHA_QUOTES
                 + qs.YUANHAI_QISHA_CONTEXT_QUOTES)},
        }
        for r in yh.YUANHAI_CAI_CROSS_REFERENCES:
            target = pools[r["target_module"]][r["target_quote_id"]]
            self.assertEqual(r["locator"], target["locator"],
                             r["id"])
            loc = r["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]],
                target["quote"], r["id"])


class PriorGroupsRegressionTest(unittest.TestCase):
    def test_prior_groups_mirror_their_goldens(self) -> None:
        zg_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_zhengguan.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(zg.YUANHAI_SECTIONS, zg_golden["sections"])
        self.assertEqual(zg.YUANHAI_ZHENGGUAN_QUOTES,
                         zg_golden["quotes"])
        qs_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_qisha.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(qs.YUANHAI_QISHA_SECTIONS,
                         qs_golden["sections"])
        self.assertEqual(qs.YUANHAI_QISHA_QUOTES, qs_golden["quotes"])


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 95)
        self.assertEqual(levels.count("D"), 6)

    def test_yuanhai_source_blob_sha_matches(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        self.assertEqual(yuanhai["blob_sha"],
                         yh.YUANHAI_SNAPSHOT["blob_sha"])
        self.assertEqual(yuanhai["sha256"],
                         yh.YUANHAI_SNAPSHOT["sha256"])

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("财组）整节登记《论正财》",
                       "节内分题论偏财",
                       "《论劫财》",
                       "只登记引用关系",
                       "财格成格/破格/真假仍不可裁定",
                       "不含任何由财格推现实财富的口径",
                       # qisha batch markers remain intact
                       "七杀组）整节登记《论七杀》",
                       # zhengguan batch markers remain intact
                       "本批（TJ-012.3 Slice D 前置）整节登记《正官论》"):
            self.assertIn(marker, scope)


if __name__ == "__main__":
    unittest.main()
