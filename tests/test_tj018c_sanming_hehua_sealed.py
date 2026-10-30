"""TJ-018-C 密封快照专项：三命卷二合化组三节校勘记续册与扩登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan2_hehua_collation`` 登记的 34 条引文对机上
快照做切片逐字等值 + 全文计数 ==1 复核；81 条校勘记逐条复核
定位字、语境窗口与「原文切片经校勘记变换 == 登记
mapped_reading」关系；三节 PUA / 防 / 戍 / 己 / 已全量扫描与
注册表逐位对账、「巳」82 处干支槽位分判与登记表逐位对账；
逐月横看表 120 格按登记数据在快照中顺序重演；既有五合事实层
（stem_five_combinations）输出与登记名册逐对交叉核对且不变；
来源普查钉值（101 条，C 95 / D 6）与 review_scope 新增段落
钉值；018-A（44 条）与 018-B（35 条）注册表在本环境一并回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cj
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018c_sanming_hehua.json").read_text(
        encoding="utf-8"))

SECTIONS = [(64208, 65956), (65956, 67592), (67592, 68359)]


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        meta = cj.COLLATION_SNAPSHOTS["sanming_tonghui.txt"]
        raw = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_QUOTES), 34)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            window = sanming[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(sanming.count(quote["quote"]), 1,
                             quote["id"])

    def test_section_titles_and_bounds(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(sanming[64209:64213], "论十干合")
        self.assertEqual(sanming[65957:65962], "论十干化气")
        self.assertEqual(sanming[67593:67601], "逐月横看理化之象")
        self.assertEqual(sanming[68360:68365], "论支元六合")
        for sec in cj.COLLATION_SECTIONS:
            part = sec["parts"][0]
            self.assertEqual(part["locator"], sec["locator"])


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 81)
        for note in cj.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])
            self.assertEqual(sanming[offset - 14:offset + 15],
                             note["context_short"], note["id"])

    def test_coverage_scans_match_register(self) -> None:
        sanming = _text("sanming_tonghui.txt")

        def positions(pred) -> set[int]:
            out: set[int] = set()
            for start, end in SECTIONS:
                out |= {start + i for i, ch in
                        enumerate(sanming[start:end]) if pred(ch)}
            return out

        by_prefix: dict[str, set[int]] = {}
        for note in cj.COLLATION_NOTES:
            by_prefix.setdefault(note["id"].split("-")[1], set()).add(
                note["char_offset"])
        self.assertEqual(positions(_is_pua), by_prefix["pua"])
        self.assertEqual(positions(lambda c: c == "防"), by_prefix["fang"])
        self.assertEqual(positions(lambda c: c == "戍"), by_prefix["shu"])
        self.assertEqual(positions(lambda c: c == "己"), by_prefix["ji"])
        self.assertEqual(positions(lambda c: c == "已"), by_prefix["yi"])
        # 「巳」全量分判：干名槽位点集合与登记表逐位一致，
        # 支位真义点集合与 SI_GLYPH_DISPOSITION 逐位一致
        all_si = positions(lambda c: c == "巳")
        part = cj.SI_GLYPH_DISPOSITION
        self.assertEqual(all_si, set(part["stem_slot_offsets"])
                         | set(part["branch_slot_offsets"]))
        self.assertEqual(set(part["stem_slot_offsets"]), by_prefix["si"])
        # 戌入干位一处以原文钉位复核
        self.assertEqual(sanming[66591], "戌")
        self.assertIn(66591, by_prefix["xu"])
        self.assertEqual(sanming[66590:66593], "丙戌癸")
        # 叠字格以原文钉位复核
        self.assertEqual(sanming[68069:68073], "甲甲巳化")
        self.assertIn(68070, by_prefix["jia"])

    def test_transformed_quotes_match_mapped_readings(self) -> None:
        notes = {n["id"]: n for n in cj.COLLATION_NOTES}
        for quote in cj.COLLATION_QUOTES:
            refs = quote.get("collation_refs")
            if not refs:
                continue
            chars = list(quote["quote"])
            start = quote["locator"]["char_start"]
            for ref in refs:
                note = notes[ref]
                idx = note["char_offset"] - start
                self.assertTrue(0 <= idx < len(chars), ref)
                self.assertEqual(chars[idx], note["snapshot_glyph"], ref)
                self.assertIsNotNone(note["reading"], ref)
                chars[idx] = note["reading"]
            self.assertEqual("".join(chars), quote["mapped_reading"],
                             quote["id"])


class HengkanGridSliceTest(unittest.TestCase):
    def test_grid_replays_in_snapshot_order(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        table = sanming[67592:68359]
        integ = cj.HENGKAN_TABLE_INTEGRITY
        pos = 0
        cells = 0
        for block in range(4):
            for row in integ["rows"]:
                for month in range(block * 3 + 1, block * 3 + 4):
                    state = integ["grid"][row][month - 1]
                    raw_label = integ["raw_label_variants"].get(
                        f"{row}|{month}", row)
                    raw = raw_label + (state or "")
                    found = table.find(raw, pos)
                    self.assertGreaterEqual(found, 0, (row, month, raw))
                    pos = found + len(raw)
                    cells += 1
        self.assertEqual(cells, 120)

    def test_group_label_counts(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        table = sanming[67592:68359]
        for label, expected in (("甲巳", 12), ("巳酉丑", 10),
                                ("己酉丑", 2), ("戍癸", 2),
                                ("寅午戍", 6), ("寅午戌", 6),
                                ("辰戍丑未", 3), ("辰戌丑未", 9),
                                ("戊癸", 10)):
            self.assertEqual(table.count(label), expected, label)
        # 八月辰戌丑未格无状态词由上方顺序重演钉住：该格登记
        # state=None，其 raw 仅组名，M7/M9 两格在其前后按序命中。


class FactLayerInvarianceTest(unittest.TestCase):
    def test_stem_five_combination_roster_matches_sections(self) -> None:
        from tianji_kb.bazi_core import stem_five_combination
        expected = {("甲", "己"): "土", ("乙", "庚"): "金",
                    ("丙", "辛"): "水", ("丁", "壬"): "木",
                    ("戊", "癸"): "火"}
        for (left, right), element in expected.items():
            fact = stem_five_combination(left, right)
            self.assertTrue(fact["matched"], (left, right))
            self.assertEqual(fact["traditional_result_element"], element,
                             (left, right))
        non_pair = stem_five_combination("甲", "乙")
        self.assertFalse(non_pair["matched"])
        self.assertIsNone(non_pair["traditional_result_element"])
        prose = cj.HEHUA_CONDITION_VARIANTS["branches"][0]["pairs"]
        self.assertEqual(
            {v["pair_reading"]: v["element"] for v in prose.values()},
            {"甲己": "土", "乙庚": "金", "丙辛": "水", "丁壬": "木",
             "戊癸": "火"})


class RegistrationCensusTest(unittest.TestCase):
    def test_source_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)
        grades: dict[str, int] = {}
        for source in SOURCES:
            grade = source["evidence_level"]
            grades[grade] = grades.get(grade, 0) + 1
        self.assertEqual(grades, {"C": 96, "D": 6})

    def test_review_scope_additions_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论十干合", "论十干化气", "逐月横看理化之象",
                       "64208–68359", "TJ-018-C", "transformation_status"):
            self.assertIn(needle, sanming, needle)

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_NOTES,
                                  ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_SECTIONS,
                                  ensure_ascii=False)),
            GOLDEN["sections"])

    def test_previous_registers_still_pinned(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        for note in cja.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        for note in cjb.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])


if __name__ == "__main__":
    unittest.main()
