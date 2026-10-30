"""TJ-012.3 Slice D 前置密封快照专项：渊海子平禄刃组两节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_luren`` 新登记引文（20 条）与含缺字段（1 条）对
机上快照做切片逐字等值 + 全文计数 ==1 复核；两节全文窗切片
等值；覆盖扫描——两节内未被引文/含缺字段覆盖的非空白字符只
剩节题字；缺字对账——两节范围内半角 ? 位点 [14875] 与
lr-gap-01 逐项相等、全书 ? 总数 36；字形位点（例造 XX 占位、
兼受七杀、安得不举）钉位；引用关系 8 条的 locator 对快照切片
与正官组/七杀组/财组登记引文逐字一致（只验证引用关系成立，
不复制登记）；禄散见代表句切片等值与全书节题无禄字复核；
来源普查钉值（101 条，C 95 / D 6）与渊海 review_scope 新增
段落钉值；正官组、七杀组、财组、印组与食伤组登记
（bazi_yuanhai_zhengguan / bazi_yuanhai_qisha / bazi_yuanhai_cai /
bazi_yuanhai_yin / bazi_yuanhai_shishang）逐字不变回归。
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_yuanhai_cai as cai
from tianji_kb import bazi_yuanhai_luren as lr
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
        meta = lr.YUANHAI_SNAPSHOT
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
        for s in lr.YUANHAI_LUREN_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # yangren opens the 神煞 part (after cai-registered 论劫财
        # and the part divider)
        self.assertEqual(text[14783:14796], "【渊海子平】神 煞 \n \n")
        self.assertTrue(text[14796:].startswith("《论 阳 刃》"))
        # the in-paragraph 《喜忌篇》 quotation at 15176 is NOT a
        # section boundary: prose examples continue to 15439
        self.assertEqual(text[15176:15181], "《喜忌篇》")
        self.assertTrue(text[15206:].startswith(" 如【辛酉,甲午,戊午,甲寅】"))
        # eight 诗诀 follow yangren before 论日刃
        self.assertTrue(text[15439:].startswith("《诗诀》★阳刃存时莫看凶"))
        self.assertEqual(text[15439:15752].count("《诗诀》"), 8)
        self.assertTrue(text[15752:].startswith("《论 日 刃》"))
        self.assertTrue(text[16116:].startswith("《论 日 贵》"))
        self.assertTrue(text[17642:].startswith("《六 亲 总 篇》"))


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        all_quotes = (lr.YUANHAI_LUREN_QUOTES
                      + lr.YUANHAI_LUREN_CONTEXT_QUOTES)
        self.assertEqual(len(all_quotes), 21)
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
            "yuanhai.yangren": {14796: "《", 14797: "论", 14799: "阳",
                                14801: "刃", 14802: "》"},
            "yuanhai.riren": {15752: "《", 15753: "论", 15755: "日",
                              15757: "刃", 15758: "》"},
        }
        secs = {s["section_id"]: s for s in lr.YUANHAI_LUREN_SECTIONS}
        for sid, residue_map in expect.items():
            s = secs[sid]
            a, b = s["locator"]["char_start"], s["locator"]["char_end"]
            covered = set()
            for pool in (lr.YUANHAI_LUREN_QUOTES,
                         lr.YUANHAI_LUREN_CONTEXT_QUOTES):
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
        yr = [i for i in range(14796, 15439) if text[i] == "?"]
        rr = [i for i in range(15752, 16116) if text[i] == "?"]
        self.assertEqual(yr, [14875])
        self.assertEqual(rr, [])
        self.assertEqual(text.count("?"), 36)
        registered = sorted(g["position"]
                            for g in lr.YUANHAI_LUREN_GAP_REGISTER)
        self.assertEqual(registered, yr)

    def test_gap_context_slice_equal(self) -> None:
        text = _text()
        for g in lr.YUANHAI_LUREN_GAP_REGISTER:
            loc = g["context_locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], g["context"],
                g["id"])
            self.assertEqual(text[g["position"]], "?")


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[15067:15072], "甲寅,XX")
        self.assertEqual(text[15070], "X")
        self.assertEqual(text[15799:15803], "兼受七杀")
        self.assertEqual(text[15800], "受")
        self.assertEqual(text[15916:15920], "安得不举")
        self.assertEqual(text[15919], "举")
        for g in lr.YUANHAI_LUREN_GLYPH_NOTES:
            self.assertEqual(text[g["position"]], g["char"], g["id"])


class LuScatteredTest(unittest.TestCase):
    def test_no_lu_section_anywhere(self) -> None:
        text = _text()
        titles = [m.group(0)
                  for m in re.finditer(r"《[^》]{1,14}》", text)]
        self.assertFalse(any("禄" in t for t in titles))
        self.assertEqual(text.count("建禄"), 5)
        self.assertEqual(text.count("归禄"), 20)
        self.assertEqual(text.count("月劫"), 1)

    def test_lu_representative_slice_equal(self) -> None:
        text = _text()
        item = next(i for i in lr.YUANHAI_LUREN_UNREGISTERED_RELATED
                    if i["section_id"] == "yuanhai.lu_scattered")
        loc = item["locator"]
        self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                         "日时归禄,官逢有祸。(归禄格)")


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        text = _text()
        pool = {}
        for mod_quotes in (zg.YUANHAI_ZHENGGUAN_QUOTES,
                           qs.YUANHAI_QISHA_QUOTES,
                           cai.YUANHAI_CAI_QUOTES):
            for q in mod_quotes:
                pool[q["id"]] = q
        self.assertEqual(len(lr.YUANHAI_LUREN_CROSS_REFERENCES), 8)
        for r in lr.YUANHAI_LUREN_CROSS_REFERENCES:
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
        ss_golden = json.loads(
            (ROOT / "tests" / "golden_tj012_yuanhai_shishang.json")
            .read_text(encoding="utf-8"))
        self.assertEqual(ss.YUANHAI_SHISHANG_SECTIONS,
                         ss_golden["sections"])
        self.assertEqual(ss.YUANHAI_SHISHANG_QUOTES,
                         ss_golden["quotes"])


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
                         lr.YUANHAI_SNAPSHOT["blob_sha"])
        self.assertEqual(yuanhai["sha256"],
                         lr.YUANHAI_SNAPSHOT["sha256"])

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("禄刃组）整节登记《论阳刃》",
                       "《论日刃》（字符 15752–16116",
                       "节界以机上实测内容界订正",
                       "禄于全书无专节",
                       "只登记引用关系",
                       "阳刃格/日刃格成格/破格/真假仍不可裁定",
                       "不得被用于由阳刃格、日刃格推断祸福、刑伤、生死",
                       "诗诀八首",
                       "神煞四节",
                       # shishang batch markers remain intact
                       "食伤组）整节登记《论伤官》",
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
