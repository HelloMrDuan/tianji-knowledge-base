"""TJ-017.1 七项清单收尾批密封快照专项（审源编号 018-B）。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_dayun_collation`` 登记的 8 条引文对机上快照做切片逐字等值 +
全文计数 ==1 复核；13 条校勘记逐条复核定位字、语境窗口与「原文
切片经校勘记变换 == 登记 mapped_reading」关系；七项点位覆盖钉值
（《论大运》节内 U+ED92 恰 3 处、赋文两点位码位、神峰三短语切片）；
来源普查钉值（101 条，C 95 / D 6）与两 Source review_scope 追加
段落钉值。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_dayun_collation as dc

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0171_dayun_collation.json").read_text(
        encoding="utf-8"))

SOURCE_FILE = {
    "bazi.source.sanmingtonghui": "sanming_tonghui.txt",
    "bazi.source.shenfeng": "shenfeng_tongkao.txt",
}


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshots_match_registry(self) -> None:
        for filename, meta in dc.COLLATION_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], filename)
            self.assertEqual(
                hashlib.sha256(raw).hexdigest(), meta["sha256"], filename)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             filename)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        texts = {name: _text(name) for name in SOURCE_FILE.values()}
        self.assertEqual(len(dc.COLLATION_QUOTES), 8)
        for quote in dc.COLLATION_QUOTES:
            text = texts[SOURCE_FILE[quote["source_id"]]]
            loc = quote["locator"]
            window = text[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(text.count(quote["quote"]), 1, quote["id"])


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        texts = {name: _text(name) for name in SOURCE_FILE.values()}
        sections = {s["section_id"]: s for s in dc.COLLATION_SECTIONS}
        self.assertEqual(len(dc.COLLATION_NOTES), 13)
        for note in dc.COLLATION_NOTES:
            source_id = sections[note["section_id"]]["source_id"]
            text = texts[SOURCE_FILE[source_id]]
            offset = note["char_offset"]
            self.assertEqual(text[offset], note["snapshot_glyph"],
                             note["id"])
            self.assertEqual(text[offset - 14:offset + 15],
                             note["context_short"], note["id"])
            if "snapshot_codepoint" in note:
                self.assertEqual(
                    f"U+{ord(note['snapshot_glyph']):04X}",
                    note["snapshot_codepoint"], note["id"])

    def test_transformed_quotes_match_readings(self) -> None:
        notes = {n["id"]: n for n in dc.COLLATION_NOTES}
        for quote in dc.COLLATION_QUOTES:
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
            transformed = "".join(chars)
            self.assertNotEqual(transformed, quote["quote"], quote["id"])
            self.assertEqual(transformed, quote["mapped_reading"],
                             quote["id"])


class CoveragePinTest(unittest.TestCase):
    def test_dayun_section_pua_coverage(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        section = sanming[58457:59198]
        ed92 = [58457 + i for i, ch in enumerate(section)
                if ord(ch) == 0xED92]
        self.assertEqual(ed92, [59080, 59123, 59162])
        registered = {n["char_offset"] for n in dc.COLLATION_NOTES
                      if n.get("snapshot_codepoint") == "U+ED92"}
        self.assertEqual(registered, {59080, 59123, 59162})

    def test_vol11_pua_points(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        for offset in (397081, 397192):
            self.assertEqual(ord(sanming[offset]), 0xEA20, offset)

    def test_genuine_phrases_slice(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(sanming[58887:58892], "越三嵗九月")
        self.assertEqual(sanming[58828:58834], "实歴过六十三")
        self.assertEqual(sanming[58834], "日")
        self.assertEqual(sanming[408788:408794], "折除三岁为年")

    def test_shenfeng_phrases_slice(self) -> None:
        shenfeng = _text("shenfeng_tongkao.txt")
        self.assertEqual(shenfeng[85107:85112], "四三十二日")
        self.assertEqual(shenfeng[85178:85182], "五三十五")
        self.assertEqual(shenfeng[85082:85087], "正月起戊庚")
        self.assertEqual(shenfeng[85086], "庚")


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
        for needle in ("dayun-collation-register-v1", "KR3g0042",
                       "传本本文", "正式流程复核"):
            self.assertIn(needle, sanming, needle)
        shenfeng = by_id["bazi.source.shenfeng"]["review_scope"]
        for needle in ("dayun-collation-register-v1", "同一数字谱系",
                       "字面禁用维持", "三五十五"):
            self.assertIn(needle, shenfeng, needle)

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(dc.COLLATION_NOTES, ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(dc.COLLATION_SECTIONS,
                                  ensure_ascii=False)),
            GOLDEN["sections"])
        self.assertEqual(
            json.loads(json.dumps(dc.ITEM_DISPOSITIONS,
                                  ensure_ascii=False)),
            GOLDEN["item_dispositions"])


if __name__ == "__main__":
    unittest.main()
