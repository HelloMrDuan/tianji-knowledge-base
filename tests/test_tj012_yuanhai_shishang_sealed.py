"""TJ-012.3 Slice D 前置密封快照专项：渊海子平食伤组两节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_shishang`` 新登记引文（37 条）与含缺字段（1 条）对
机上快照做切片逐字等值 + 全文计数 ==1 复核；两节全文窗切片
等值；覆盖扫描——两节内未被引文/含缺字段覆盖的非空白字符只
剩节题字；缺字对账——两节范围内半角 ? 位点 [7667] 与 ss-gap-01
逐项相等、全书 ? 总数 36；字形位点（伤官之杀、中食丙之戊财）
钉位；引用关系 7 条的 locator 对快照切片与正官组/财组/印组
登记引文逐字一致（只验证引用关系成立，不复制登记）；来源普
查钉值（101 条，C 95 / D 6）与渊海 review_scope 新增段落钉
值；正官组、七杀组、财组与印组登记（bazi_yuanhai_zhengguan /
bazi_yuanhai_qisha / bazi_yuanhai_cai / bazi_yuanhai_yin）逐字
不变回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cai as cai
from tianji_kb import bazi_yuanhai_qisha as qs
from tianji_kb import bazi_yuanhai_shishang as ss
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
        meta = ss.YUANHAI_SNAPSHOT
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
        for s in ss.YUANHAI_SHISHANG_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # shangguan opens the 十神 part of the snapshot
        self.assertEqual(text[6076:6086], "子平】十 神 \n \n")
        self.assertTrue(text[6086:].startswith("《论 伤 官》"))
        # seven 诗诀 follow shangguan before 《伤官说》
        self.assertTrue(text[6932:].startswith("《诗诀》★伤官伤尽最为奇"))
        self.assertEqual(text[6932:7222].count("《诗诀》"), 7)
        self.assertTrue(text[7222:].startswith("《伤 官 说》"))
        self.assertTrue(text[7622:].startswith("《论 食 神》"))
        # six 诗诀 follow shishen before the cai-registered 论正财
        self.assertTrue(text[7948:].startswith("《诗诀》★食神有气胜财官"))
        self.assertEqual(text[7948:8183].count("《诗诀》"), 6)
        self.assertTrue(text[8183:].startswith("《论 正 财》"))


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (ss.YUANHAI_SHISHANG_QUOTES
                      + ss.YUANHAI_SHISHANG_CONTEXT_QUOTES)
        self.assertEqual(len(all_quotes), 38)
        for q in all_quotes:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class CoverageScanTest(unittest.TestCase):
    def test_section_coverage_residue_is_titles_only(self) -> None:
        text = _text()
        expect = {
            "yuanhai.shangguan": {6086: "《", 6087: "论", 6089: "伤",
                                  6091: "官", 6092: "》"},
            "yuanhai.shishen": {7622: "《", 7623: "论", 7625: "食",
                                7627: "神", 7628: "》"},
        }
        secs = {s["section_id"]: s for s in ss.YUANHAI_SHISHANG_SECTIONS}
        for sid, residue_map in expect.items():
            s = secs[sid]
            a, b = s["locator"]["char_start"], s["locator"]["char_end"]
            covered = set()
            for pool in (ss.YUANHAI_SHISHANG_QUOTES,
                         ss.YUANHAI_SHISHANG_CONTEXT_QUOTES):
                for q in pool:
                    if q["source_section_id"] == sid:
                        covered.update(range(q["locator"]["char_start"],
                                             q["locator"]["char_end"]))
            residue = {i: text[i] for i in range(a, b)
                       if i not in covered and text[i] not in " \n"}
            self.assertEqual(residue, residue_map, sid)


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        sw = [i for i in range(6086, 6932) if text[i] == "?"]
        sg = [i for i in range(7622, 7948) if text[i] == "?"]
        self.assertEqual(sw, [])
        self.assertEqual(sg, [7667])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in ss.YUANHAI_SHISHANG_GAP_REGISTER)
        self.assertEqual(registered, sg)

    def test_gap_context_slice_equal(self) -> None:
        text = _text()
        for g in ss.YUANHAI_SHISHANG_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[6529:6533], "伤官之杀")
        self.assertEqual(text[6532], "杀")
        self.assertEqual(text[7677:7683], "中食丙之戊财")
        self.assertEqual(text[7678], "食")
        for g in ss.YUANHAI_SHISHANG_GLYPH_NOTES:
            self.assertEqual(text[g["position"]], g["char"], g["id"])


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        text = _text()
        pool = {}
        for mod_quotes in (zg.YUANHAI_ZHENGGUAN_QUOTES,
                           cai.YUANHAI_CAI_QUOTES,
                           yh.YUANHAI_YIN_QUOTES):
            for q in mod_quotes:
                pool[q["id"]] = q
        self.assertEqual(len(ss.YUANHAI_SHISHANG_CROSS_REFERENCES), 7)
        for r in ss.YUANHAI_SHISHANG_CROSS_REFERENCES:
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
        yh_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_yin.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(yh.YUANHAI_YIN_SECTIONS, yh_golden["sections"])
        self.assertEqual(yh.YUANHAI_YIN_QUOTES, yh_golden["quotes"])


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 96)
        self.assertEqual(levels.count("D"), 6)

    def test_yuanhai_source_blob_sha_matches(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        self.assertEqual(yuanhai["blob_sha"],
                         ss.YUANHAI_SNAPSHOT["blob_sha"])
        self.assertEqual(yuanhai["sha256"],
                         ss.YUANHAI_SNAPSHOT["sha256"])

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("食伤组）整节登记《论伤官》",
                       "《论食神》（字符 7622–7948",
                       "只登记引用关系",
                       "食神格/伤官格成格/破格/真假仍不可裁定",
                       "不得被用于由伤官格、食神格推断健康、寿命、六亲",
                       "诗诀七首",
                       "《伤官说》",
                       # yin batch markers remain intact
                       "印组）整节登记《论印綬》",
                       # cai batch markers remain intact
                       "财组）整节登记《论正财》",
                       # qisha batch markers remain intact
                       "七杀组）整节登记《论七杀》",
                       # zhengguan batch markers remain intact
                       "本批（TJ-012.3 Slice D 前置）整节登记《正官论》"):
            self.assertIn(marker, scope)


if __name__ == "__main__":
    unittest.main()
