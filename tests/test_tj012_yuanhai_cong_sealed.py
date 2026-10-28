"""TJ-012.3 Slice D 前置密封快照专项：渊海子平从格专题组一节逐节登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_yuanhai_cong`` 新登记引文（15 条）对机上快照做切片逐字
等值 + 全文计数 ==1 复核；一节全文窗切片等值；覆盖扫描——
节内未被引文覆盖的非空白字符只剩节题字；缺字对账——节内
半角 ? 位点为空集、全书 ? 总数 36；字形位点（命殞、孤神）
钉位；散见代表句切片等值（四言独步末句、挈要捷驰玄妙诀首句、
五行元理消息赋从化句、碧渊赋从革格句）与从格形态全文计数
复核（从财 3/从杀 3/从化 4/专旺 2/从旺 0/从强 0/从儿 0/从势 0）；
滴天髓交叉引用 3 条的 locator 对滴天髓快照切片与
bazi_fire_morphology 登记引文逐字一致（只验证引用关系成立，
不复制登记）；来源普查钉值（101 条，C 95 / D 6）与渊海
review_scope 新增段落钉值；正官组、七杀组、财组、印组、
食伤组与禄刃组登记（bazi_yuanhai_zhengguan / bazi_yuanhai_qisha /
bazi_yuanhai_cai / bazi_yuanhai_yin / bazi_yuanhai_shishang /
bazi_yuanhai_luren）逐字不变回归。
"""

from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from tianji_kb import bazi_fire_morphology as fm
from tianji_kb import bazi_yuanhai_cai as cai
from tianji_kb import bazi_yuanhai_cong as cg
from tianji_kb import bazi_yuanhai_luren as luren
from tianji_kb import bazi_yuanhai_qisha as qs
from tianji_kb import bazi_yuanhai_shishang as ss
from tianji_kb import bazi_yuanhai_yin as yh
from tianji_kb import bazi_yuanhai_zhengguan as zg

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20")
SNAPSHOT = SNAP_DIR / "yuanhai_ziping.txt"
DT_SNAPSHOT = SNAP_DIR / "ditiansui_chanwei.txt"
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]


def _text() -> str:
    return SNAPSHOT.read_bytes().decode("utf-8")


def _dt_text() -> str:
    return DT_SNAPSHOT.read_bytes().decode("utf-8")


def _blob_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob %d\0" % len(raw) + raw).hexdigest()


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        raw = SNAPSHOT.read_bytes()
        meta = cg.YUANHAI_SNAPSHOT
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])
        self.assertEqual(meta["chars"], 58905)
        self.assertEqual(_blob_sha(raw), meta["blob_sha"])
        self.assertEqual(meta["blob_sha"],
                         "f945a48cbedf5883808a72bb6f544a4dca603cb3")

    def test_ditiansui_snapshot_matches_reference_meta(self) -> None:
        raw = DT_SNAPSHOT.read_bytes()
        meta = cg.YUANHAI_CONG_DITIANSUI_SNAPSHOT
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])
        self.assertEqual(meta["chars"], 139538)
        self.assertEqual(_blob_sha(raw), meta["blob_sha"])


class SectionSliceTest(unittest.TestCase):
    def test_full_section_slice_equal(self) -> None:
        text = _text()
        for s in cg.YUANHAI_CONG_SECTIONS:
            loc = s["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], s["full_text"],
                s["section_id"])
            self.assertEqual(text.count(s["full_text"]), 1,
                             s["section_id"])

    def test_section_boundaries(self) -> None:
        text = _text()
        # preceded by the final 四言独步 verse and a blank line
        self.assertEqual(text[54052:54055], "\n \n")
        self.assertTrue(text[54055:].startswith("《弃 命 从 杀 论》"))
        self.assertEqual(text.find("《四 言 独 步》"), 51898)
        # followed immediately by 《五言独步》
        self.assertTrue(text[54359:].startswith("《五 言 独 步》"))
        self.assertEqual(text.find("《五 行 生 剋 赋》"), 55002)
        # the only section title in the book containing 从
        titles = [m.group(0)
                  for m in re.finditer(r"《[^》]{1,16}》", text)]
        self.assertEqual([t for t in titles if "从" in t],
                         ["《弃 命 从 杀 论》"])


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        self.assertEqual(len(cg.YUANHAI_CONG_QUOTES), 15)
        for q in cg.YUANHAI_CONG_QUOTES:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class CoverageScanTest(unittest.TestCase):
    def test_section_coverage_residue_is_title_only(self) -> None:
        text = _text()
        expect = {54055: "《", 54056: "弃", 54058: "命", 54060: "从",
                  54062: "杀", 54064: "论", 54065: "》"}
        s = cg.YUANHAI_CONG_SECTIONS[0]
        a, b = s["locator"]["char_start"], s["locator"]["char_end"]
        covered = set()
        for q in cg.YUANHAI_CONG_QUOTES:
            covered.update(range(q["locator"]["char_start"],
                                 q["locator"]["char_end"]))
        residue = {i: text[i] for i in range(a, b)
                   if i not in covered and text[i] not in " \n"}
        self.assertEqual(residue, expect)


class GapReconciliationTest(unittest.TestCase):
    def test_gap_positions_reconcile(self) -> None:
        text = _text()
        in_section = [i for i in range(54055, 54359) if text[i] == "?"]
        self.assertEqual(in_section, [])
        self.assertEqual(text.count("?"), 36)
        self.assertEqual(cg.YUANHAI_CONG_GAP_REGISTER, [])
        self.assertFalse(
            any(0xE000 <= ord(c) <= 0xF8FF
                for c in text[54055:54359]))


class GlyphPositionTest(unittest.TestCase):
    def test_glyph_positions(self) -> None:
        text = _text()
        self.assertEqual(text[54351:54355], "命殞无猜")
        self.assertEqual(text[54352], "殞")
        self.assertEqual(text[54149:54153], "孤神得失")
        self.assertEqual(text[54149], "孤")
        for g in cg.YUANHAI_CONG_GLYPH_NOTES:
            self.assertEqual(text[g["position"]], g["char"], g["id"])


class ScatteredFormsTest(unittest.TestCase):
    def test_scattered_census_counts(self) -> None:
        text = _text()
        self.assertEqual(text.count("从财"), 3)
        self.assertEqual(text.count("从杀"), 3)
        self.assertEqual(text.count("从化"), 4)
        self.assertEqual(text.count("专旺"), 2)
        self.assertEqual(text.count("弃命"), 6)
        for w in ("从旺", "从强", "从儿", "从势", "从財"):
            self.assertEqual(text.count(w), 0, w)
        self.assertEqual(text.count("曲直格"), 2)
        self.assertEqual(text.count("炎上格"), 2)
        self.assertEqual(text.count("从革格"), 2)
        self.assertEqual(text.count("润下格"), 2)
        self.assertEqual(text.count("稼穡格"), 1)
        self.assertEqual(text.count("从革"), 4)

    def test_scattered_representative_slices_equal(self) -> None:
        text = _text()
        expect = {
            "yuanhai.siyandubu_congcai_verse":
                "癸巳无根,火土重见;透财名彰,露根则贱。(弃命从财格)",
            "yuanhai.cong_scattered_qieyao":
                "贵全官杀,有弃命就财、就杀、就官者;有餘富贵,无依专旺。",
            "yuanhai.conghua_scattered": "从化得从,显达功名之士。",
            "yuanhai.zhuanwang_scattered":
                "庚辛局全巳酉丑,位重权高。(从革格)",
        }
        items = {i["section_id"]: i
                 for i in cg.YUANHAI_CONG_UNREGISTERED_RELATED}
        for sid, sentence in expect.items():
            loc = items[sid]["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], sentence, sid)
            self.assertEqual(text.count(sentence), 1, sid)

    def test_wuyandubu_span(self) -> None:
        text = _text()
        item = next(i for i in cg.YUANHAI_CONG_UNREGISTERED_RELATED
                    if i["section_id"] == "yuanhai.wuyandubu_adjacent")
        loc = item["locator"]
        self.assertTrue(
            text[loc["char_start"]:loc["char_end"]].startswith(
                "《五 言 独 步》"))


class CrossReferenceTest(unittest.TestCase):
    def test_cross_reference_targets_slice_equal(self) -> None:
        dt = _dt_text()
        pool = {x["id"]: x for x in fm.MORPHOLOGY_QUOTES}
        self.assertEqual(len(cg.YUANHAI_CONG_CROSS_REFERENCES), 3)
        for r in cg.YUANHAI_CONG_CROSS_REFERENCES:
            target = pool[r["target_quote_id"]]
            self.assertEqual(r["locator"], target["locator"], r["id"])
            self.assertEqual(r["target_layer"], target["layer"], r["id"])
            loc = r["locator"]
            self.assertEqual(
                dt[loc["char_start"]:loc["char_end"]],
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
        for mod, golden_name, sec_attr, quote_attr in (
                (qs, "golden_tj012_yuanhai_qisha.json",
                 "YUANHAI_QISHA_SECTIONS", "YUANHAI_QISHA_QUOTES"),
                (cai, "golden_tj012_yuanhai_cai.json",
                 "YUANHAI_CAI_SECTIONS", "YUANHAI_CAI_QUOTES"),
                (yh, "golden_tj012_yuanhai_yin.json",
                 "YUANHAI_YIN_SECTIONS", "YUANHAI_YIN_QUOTES"),
                (ss, "golden_tj012_yuanhai_shishang.json",
                 "YUANHAI_SHISHANG_SECTIONS",
                 "YUANHAI_SHISHANG_QUOTES"),
                (luren, "golden_tj012_yuanhai_luren.json",
                 "YUANHAI_LUREN_SECTIONS", "YUANHAI_LUREN_QUOTES")):
            golden = json.loads(
                (ROOT / "tests" / golden_name).read_text(
                    encoding="utf-8"))
            self.assertEqual(getattr(mod, sec_attr),
                             golden["sections"], golden_name)
            self.assertEqual(getattr(mod, quote_attr),
                             golden["quotes"], golden_name)


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
                         cg.YUANHAI_SNAPSHOT["blob_sha"])
        self.assertEqual(yuanhai["sha256"],
                         cg.YUANHAI_SNAPSHOT["sha256"])

    def test_yuanhai_review_scope_extended(self) -> None:
        yuanhai = next(s for s in SOURCES
                       if s["source_id"] == "bazi.source.yuanhai")
        scope = yuanhai["review_scope"]
        for marker in ("从格组）整节登记《弃命从杀论》",
                       "（字符 54055–54359",
                       "四言韵文体专论",
                       "只登记交叉引用",
                       "不跨节拼凑从格登记",
                       "从杀格/从财格成格/破格/真假仍不可裁定",
                       "不得被用于由从格推断生死、祸福、寿夭、刑伤",
                       "无新缺字登记",
                       # luren batch markers remain intact
                       "禄刃组）整节登记《论阳刃》",
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
