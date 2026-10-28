"""TJ-018-G 密封快照专项：三命卷六方局/八象组校勘续册。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan6_fangju_baxiang_collation`` 登记的 31 条
引文对机上快照做切片逐字等值 + 全文计数 ==1 复核；72 条校勘记
逐条复核定位字、语境窗口与「原文切片经校勘记变换 == 登记
mapped_reading」关系；十三节 PUA / 防 / 巳 / 己 / 已 / 戌 / 戍
全量扫描与注册表逐位对账（巳 38 处分判与登记表逐位一致）；
来源普查钉值（101 条，C 95 / D 6）与 review_scope 新增段落
钉值；018-A（44 条）、018-B（35 条）、018-C（81 条）、018-D
（43 条）、018-F（108 条）注册表在本环境一并回归。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_hehua_collation as cjc
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cjb
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cjf
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as cj

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018g_sanming_juan6.json").read_text(
        encoding="utf-8"))

SECTIONS = [(204089, 204236), (204236, 204349), (204349, 204476),
            (204476, 204631), (204631, 204836), (212467, 212729),
            (212729, 212991), (212991, 213270), (213270, 213485),
            (213485, 213815), (213815, 214129), (214129, 214516),
            (214516, 214948)]
TITLES = ["曲直", "炎上", "从革", "润下", "稼穑", "返象", "照象",
          "鬼象", "伏象", "属象", "类象", "从象", "化象"]


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
        self.assertEqual(len(cj.COLLATION_QUOTES), 31)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            window = sanming[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(sanming.count(quote["quote"]), 1,
                             quote["id"])

    def test_section_titles_and_bounds(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        # 节题行首一空格为快照体例，计入节界（组界与审源钉值一致）
        for (start, _end), title in zip(SECTIONS, TITLES):
            self.assertEqual(sanming[start], " ")
            self.assertEqual(sanming[start + 1:start + 3], title)
        # 方局组终点为下节题行首空格位；八象组终点前一字为换行、终点位即下节题行首空格
        self.assertEqual(sanming[204836], " ")
        self.assertEqual(sanming[204837:204841], "土局润下")
        self.assertEqual(sanming[214947], "\n")
        self.assertEqual(sanming[214949:214953], "天地德合")


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 72)
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
        self.assertEqual(positions(lambda c: c == "戌"), by_prefix["xu"])
        # 两组窗口内「已」「戍」0 见
        self.assertEqual(positions(lambda c: c == "已"), set())
        self.assertEqual(positions(lambda c: c == "戍"), set())
        # 「巳」全量分判：干名槽（入册）/ 支位真义两类集合与
        # 登记表逐位一致且互不交叠
        all_si = positions(lambda c: c == "巳")
        part = cj.SI_GLYPH_DISPOSITION
        self.assertEqual(all_si, set(part["stem_slot_offsets"])
                         | set(part["branch_slot_offsets"]))
        self.assertEqual(set(part["stem_slot_offsets"]), by_prefix["si"])
        self.assertEqual(len(all_si), 38)

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
        for needle in ("曲直", "稼穑", "返象", "化象", "204089–204836",
                       "212467–214948", "TJ-018-G",
                       "sanming-juan6-collation-register-v1", "383 条"):
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
        for mod, expected in ((cja, 44), (cjb, 35), (cjc, 81), (cjd, 43),
                              (cjf, 108)):
            self.assertEqual(len(mod.COLLATION_NOTES), expected)
            for note in mod.COLLATION_NOTES:
                offset = note["char_offset"]
                self.assertEqual(sanming[offset], note["snapshot_glyph"],
                                 note["id"])


if __name__ == "__main__":
    unittest.main()
