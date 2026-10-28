"""TJ-018-F 密封快照专项：三命卷五杂气/阳刃组校勘续册。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan5_zaqi_yangren_collation`` 登记的 39 条引文
对机上快照做切片逐字等值 + 全文计数 ==1 复核；108 条校勘记
逐条复核定位字、语境窗口与「原文切片经校勘记变换 == 登记
mapped_reading」关系；两节 PUA / 防 / 巳 / 己 / 已 / 戌 / 戍
全量扫描与注册表逐位对账（巳 23 处分判与登记表逐位一致）；
Slice A 两条已登记引文（纲句/刃位句）在快照上逐字复核；
来源普查钉值（101 条，C 95 / D 6）与 review_scope 新增段落
钉值；018-A（44 条）、018-B（35 条）、018-C（81 条）、018-D
（43 条）注册表在本环境一并回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_pattern as pat_mod
from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cj

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018f_sanming_juan5.json").read_text(
        encoding="utf-8"))

SECTIONS = [(170743, 172958), (180874, 184328)]


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
        self.assertEqual(len(cj.COLLATION_QUOTES), 39)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            window = sanming[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(sanming.count(quote["quote"]), 1,
                             quote["id"])

    def test_section_titles_and_bounds(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        # 节题起于 char_start（题前一空格为快照体例，在 char_start-1）
        self.assertEqual(sanming[170743:170757], "论杂气【喜身旺 刑冲忌压伏】")
        self.assertEqual(sanming[180874:180888],
                         "论阳刃【前论羊刄煞与此\ueb07防】")
        # 两节终点为下一节题行前空格位
        self.assertEqual(sanming[172958], " ")
        self.assertEqual(sanming[172959:172962], "论伤官")
        self.assertEqual(sanming[184328], " ")
        self.assertEqual(sanming[184329:184332], "论建禄")
        # 附论墓运子题钉位（zaqi 第二 part 起点）
        self.assertEqual(sanming[172859:172863], "附论墓运")

    def test_slice_a_quotes_still_verbatim(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        for quote in pat_mod.LUREN_QUOTES:
            if quote["source_id"] != "bazi.source.sanmingtonghui":
                continue
            loc = quote["locator"]
            self.assertEqual(sanming[loc["char_start"]:loc["char_end"]],
                             quote["quote"], quote["id"])


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 108)
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
        self.assertEqual(positions(lambda c: c == "己"), by_prefix["ji"])
        self.assertEqual(positions(lambda c: c == "已"), by_prefix["yi"])
        self.assertEqual(positions(lambda c: c == "戌"), by_prefix["xu"])
        # 两节窗口内「戍」0 见
        self.assertEqual(positions(lambda c: c == "戍"), set())
        # 「巳」全量分判：干名槽（入册）/ 支位真义两类集合与
        # 登记表逐位一致且互不交叠
        all_si = positions(lambda c: c == "巳")
        part = cj.SI_GLYPH_DISPOSITION
        self.assertEqual(all_si, set(part["stem_slot_offsets"])
                         | set(part["branch_slot_offsets"]))
        self.assertEqual(set(part["stem_slot_offsets"]), by_prefix["si"])
        self.assertEqual(len(all_si), 23)

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


class RegistrationCensusTest(unittest.TestCase):
    def test_source_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        grades: dict[str, int] = {}
        for source in SOURCES:
            grade = source["evidence_level"]
            grades[grade] = grades.get(grade, 0) + 1
        self.assertEqual(grades, {"C": 95, "D": 6})

    def test_review_scope_additions_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论杂气", "论阳刃", "170743–172958", "180874–184328",
                       "TJ-018-F", "sanming-juan5-collation-register-v1",
                       "311 条"):
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
        for mod, expected in ((cja, 44), (cjb, 35), (cjc, 81), (cjd, 43)):
            self.assertEqual(len(mod.COLLATION_NOTES), expected)
            for note in mod.COLLATION_NOTES:
                offset = note["char_offset"]
                self.assertEqual(sanming[offset], note["snapshot_glyph"],
                                 note["id"])


if __name__ == "__main__":
    unittest.main()
