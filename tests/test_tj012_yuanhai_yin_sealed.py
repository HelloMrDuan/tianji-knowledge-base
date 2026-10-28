"""TJ-012.3 Slice D 前置密封快照专项：渊海子平印组两节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_yin`` 新登记引文（24 条）与含缺字段（2 条）对
机上快照做切片逐字等值 + 全文计数 ==1 复核；两节全文窗切片
等值；覆盖扫描——两节内未被引文/含缺字段/引用关系覆盖的非
空白字符只剩节题字与两处分号分隔符，且正官组《论印綬》跳过
清单 12 段全部被本批引文覆盖（分号除外）；缺字对账——两节
范围内半角 ? 位点 [12518, 12557] 与本批按节归属在案的
yh-gap-04/05 逐项相等、且与正官组原登记逐字段一致、全书 ?
总数 36；字形位点（例造属木、三丁食己、吞啗煞、容貌攲斜、
纔交）钉位；引用关系 10 条的 locator 对快照切片与正官组登
记引文逐字一致（只验证引用关系成立，不复制登记）；来源普
查钉值（101 条，C 95 / D 6）与渊海 review_scope 新增段落钉
值；正官组、七杀组与财组登记（bazi_yuanhai_zhengguan /
bazi_yuanhai_qisha / bazi_yuanhai_cai）逐字不变回归——特别
是正官组《论印綬》7 窗、YINSHOU_SKIPPED_WINDOWS 与缺字登记
逐字不变（本批转引用关系不改写其原登记）。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cai as cai
from tianji_kb import bazi_yuanhai_qisha as qs
from tianji_kb import bazi_yuanhai_yin as yh
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
        for s in yh.YUANHAI_YIN_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # preceding section is the zhengguan-registered 官杀混杂
        self.assertTrue(
            text[12400:].startswith("《论 官 杀 混 杂 要 制 伏》"))
        # yinshou header in the snapshot lacks the opening 《
        self.assertTrue(text[12506:].startswith("论 印 綬》"))
        # sixteen 诗诀 follow yinshou before 论倒食
        self.assertTrue(text[13494:].startswith("《诗诀》★月逢印綬喜官星"))
        self.assertEqual(text[13494:14119].count("《诗诀》"), 16)
        self.assertTrue(text[14119:].startswith("《论 倒 食》"))
        self.assertTrue(text[14566:].startswith("《论 劫 财》"))
        # no standalone 论正印 / 论偏印 sections exist in the book
        self.assertEqual(text.count("论正印"), 0)
        self.assertEqual(text.count("论偏印"), 0)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (yh.YUANHAI_YIN_QUOTES
                      + yh.YUANHAI_YIN_CONTEXT_QUOTES)
        self.assertEqual(len(all_quotes), 26)
        for q in all_quotes:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class CoverageScanTest(unittest.TestCase):
    def _covered(self, section_id):
        covered = set()
        for pool in (yh.YUANHAI_YIN_QUOTES,
                     yh.YUANHAI_YIN_CONTEXT_QUOTES):
            for q in pool:
                if q["source_section_id"] == section_id:
                    covered.update(range(q["locator"]["char_start"],
                                         q["locator"]["char_end"]))
        for r in yh.YUANHAI_YIN_CROSS_REFERENCES:
            covered.update(range(r["locator"]["char_start"],
                                 r["locator"]["char_end"]))
        return covered

    def test_section_coverage_residue_is_titles_and_separators(
            self) -> None:
        text = _text()
        expect = {
            "yuanhai.yinshou": ({12506, 12508, 12510, 12511},
                                {12506: "论", 12508: "印", 12510: "綬",
                                 12511: "》", 12673: ";", 12979: ";"}),
            "yuanhai.daoshi": ({14119, 14120, 14122, 14124, 14125},
                               {14119: "《", 14120: "论", 14122: "倒",
                                14124: "食", 14125: "》"}),
        }
        secs = {s["section_id"]: s for s in yh.YUANHAI_YIN_SECTIONS}
        for sid, (title_pos, residue_map) in expect.items():
            s = secs[sid]
            a, b = s["locator"]["char_start"], s["locator"]["char_end"]
            covered = self._covered(sid)
            residue = {i: text[i] for i in range(a, b)
                       if i not in covered and text[i] not in " \n"}
            self.assertEqual(residue, residue_map, sid)
            self.assertTrue(title_pos <= set(residue_map), sid)

    def test_zhengguan_skipped_windows_now_covered(self) -> None:
        text = _text()
        covered = set()
        for q in yh.YUANHAI_YIN_QUOTES:
            if q["source_section_id"] == "yuanhai.yinshou":
                covered.update(range(q["locator"]["char_start"],
                                     q["locator"]["char_end"]))
        self.assertEqual(len(zg.YINSHOU_SKIPPED_WINDOWS), 12)
        for w in zg.YINSHOU_SKIPPED_WINDOWS:
            loc = w["locator"]
            missing = [i for i in range(loc["char_start"],
                                         loc["char_end"])
                       if i not in covered]
            # only the two ';' separators between split quote pairs
            # may remain outside quote windows
            self.assertTrue(
                all(text[i] == ";" for i in missing),
                (w, [text[i] for i in missing]))


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        ys = [i for i in range(12506, 13494) if text[i] == "?"]
        ds = [i for i in range(14119, 14566) if text[i] == "?"]
        self.assertEqual(ys, [12518, 12557])
        self.assertEqual(ds, [])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in yh.YUANHAI_YIN_GAP_REGISTER)
        self.assertEqual(registered, ys)

    def test_gap_entries_identical_to_zhengguan_registration(
            self) -> None:
        zg_gaps = {g["id"]: g for g in zg.YUANHAI_GAP_REGISTER}
        for g in yh.YUANHAI_YIN_GAP_REGISTER:
            orig = zg_gaps[g["id"]]
            for field in ("position", "char", "source_section_id",
                          "context", "context_locator", "status",
                          "reading", "note"):
                self.assertEqual(g[field], orig[field],
                                 (g["id"], field))

    def test_gap_contexts_slice_equal(self) -> None:
        text = _text()
        for g in yh.YUANHAI_YIN_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[13394:13403], "生气是丙丁火属木故也")
        self.assertEqual(text[13400], "属")
        self.assertEqual(text[14144:14147], "吞啗煞")
        self.assertEqual(text[14145], "啗")
        self.assertEqual(text[14370:14374], "三丁食己")
        self.assertEqual(text[14372], "食")
        self.assertEqual(text[14301:14305], "容貌攲斜")
        self.assertEqual(text[14303], "攲")
        self.assertEqual(text[14391:14396], "纔交乙巳运")
        for g in yh.YUANHAI_YIN_GLYPH_NOTES:
            self.assertEqual(text[g["position"]], g["char"], g["id"])


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        text = _text()
        pool = {q["id"]: q for q in
                (zg.YUANHAI_ZHENGGUAN_QUOTES
                 + zg.YUANHAI_LEGACY_WINDOWS)}
        self.assertEqual(len(yh.YUANHAI_YIN_CROSS_REFERENCES), 10)
        for r in yh.YUANHAI_YIN_CROSS_REFERENCES:
            target = pool[r["target_quote_id"]]
            self.assertEqual(r["locator"], target["locator"], r["id"])
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
        # the zhengguan yinshou registration is untouched verbatim:
        # 7 windows, 12 skipped segments and the gap register intact
        self.assertEqual(zg.YINSHOU_SKIPPED_WINDOWS,
                         zg_golden["yinshou_skipped_windows"])
        self.assertEqual(zg.YUANHAI_GAP_REGISTER,
                         zg_golden["gap_register"])
        self.assertEqual(zg.YUANHAI_LEGACY_WINDOWS,
                         zg_golden["legacy_windows"])
        qs_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_qisha.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(qs.YUANHAI_QISHA_SECTIONS,
                         qs_golden["sections"])
        self.assertEqual(qs.YUANHAI_QISHA_QUOTES, qs_golden["quotes"])
        cai_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_cai.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(cai.YUANHAI_CAI_SECTIONS,
                         cai_golden["sections"])
        self.assertEqual(cai.YUANHAI_CAI_QUOTES, cai_golden["quotes"])


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
        for marker in ("印组）整节登记《论印綬》",
                       "《论倒食》（字符 14119–14566",
                       "只登记引用关系",
                       "印格成格/破格/真假仍不可裁定",
                       "不得被用于由印格推断健康、寿命",
                       "诗诀十六首",
                       # cai batch markers remain intact
                       "财组）整节登记《论正财》",
                       # qisha batch markers remain intact
                       "七杀组）整节登记《论七杀》",
                       # zhengguan batch markers remain intact
                       "本批（TJ-012.3 Slice D 前置）整节登记《正官论》"):
            self.assertIn(marker, scope)


if __name__ == "__main__":
    unittest.main()
