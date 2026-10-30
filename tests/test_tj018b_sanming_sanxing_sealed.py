"""TJ-018-B 密封快照专项：三命卷二《论三刑》校勘记续册与扩登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan2_sanxing_collation`` 登记的 11 条引文对机上
快照做切片逐字等值 + 全文计数 ==1 复核；35 条校勘记逐条复核定位
字、语境窗口与「原文切片经校勘记变换 == 登记 mapped_reading」
关系；本节 PUA / 防 / 戍 / 己 / 已全量扫描与注册表逐位对账；
来源普查钉值（101 条，C 95 / D 6）与 review_scope 新增段落钉值；
018-A 注册表在本环境一并回归（44 条钉位不变）。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cja
from tianji_kb import bazi_sanming_juan2_sanxing_collation as cj

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018b_sanming_sanxing.json").read_text(
        encoding="utf-8"))

S = (71874, 74856)


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
        self.assertEqual(len(cj.COLLATION_QUOTES), 11)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            window = sanming[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(sanming.count(quote["quote"]), 1,
                             quote["id"])

    def test_section_titles_and_parts(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(sanming[71875:71878], "论三刑")
        self.assertEqual(sanming[74035:74038], "论冲击")
        parts = cj.COLLATION_SECTIONS[0]["parts"]
        bounds = [parts[0]["locator"]["char_start"]] + \
            [p["locator"]["char_end"] for p in parts]
        self.assertEqual(bounds, [71874, 74035, 74856])


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 35)
        for note in cj.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])
            self.assertEqual(sanming[offset - 14:offset + 15],
                             note["context_short"], note["id"])

    def test_coverage_scans_match_register(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        sec = sanming[S[0]:S[1]]

        def positions(pred) -> set[int]:
            return {S[0] + i for i, ch in enumerate(sec) if pred(ch)}

        by_prefix: dict[str, set[int]] = {}
        for note in cj.COLLATION_NOTES:
            by_prefix.setdefault(note["id"].split("-")[1], set()).add(
                note["char_offset"])
        self.assertEqual(positions(_is_pua), by_prefix["pua"])
        self.assertEqual(positions(lambda c: c == "防"), by_prefix["fang"])
        self.assertEqual(positions(lambda c: c == "戍"), by_prefix["shu"])
        self.assertEqual(positions(lambda c: c == "己"), by_prefix["ji"])
        self.assertEqual(positions(lambda c: c == "已"), by_prefix["yi"])
        # 做/寅/敛各为定点处置：以快照原文钉位复核
        self.assertEqual(sanming.find("做曰无恩"), by_prefix["zuo"].pop())
        self.assertEqual(sanming[71984], "寅")
        self.assertIn(71984, by_prefix["anomaly"])
        self.assertEqual(sanming[73886], "敛")
        self.assertIn(73886, by_prefix["lian"])

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
        for needle in ("论三刑", "71874–74856", "TJ-018-B",
                       "conflict_three_punishments", "三车一览"):
            self.assertIn(needle, sanming, needle)

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_NOTES, ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_SECTIONS,
                                  ensure_ascii=False)),
            GOLDEN["sections"])

    def test_018a_register_still_pinned(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        for note in cja.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])


if __name__ == "__main__":
    unittest.main()
