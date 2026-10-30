"""TJ-018-A 密封快照专项：三命卷二两节校勘记与扩登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan2_collation`` 登记的 22 条引文对机上快照做切片
逐字等值 + 全文计数 ==1 复核；44 条校勘记逐条复核定位字、语境窗口
与「原文切片经校勘记变换 == 校定读法」关系；两节 PUA / 防 / 己 /
已全量扫描与注册表逐位对账；十干覆盖锚点节内唯一性；来源普查钉值
（101 条，C 95 / D 6）与两来源 review_scope 新增段落钉值。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_juan2_collation as cj

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj018a_sanming_juan2.json").read_text(
        encoding="utf-8"))

SOURCE_FILE = {
    "bazi.source.sanmingtonghui": "sanming_tonghui.txt",
    "bazi.source.shenfeng": "shenfeng_tongkao.txt",
    "bazi.source.yuanhai": "yuanhai_ziping.txt",
    "bazi.source.ditiansui-spouse": "ditiansui_chanwei.txt",
}
S1 = (38890, 43082)
S2 = (54894, 55673)


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshots_match_registry(self) -> None:
        for filename, meta in cj.COLLATION_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], filename)
            self.assertEqual(
                hashlib.sha256(raw).hexdigest(), meta["sha256"], filename)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             filename)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        texts = {name: _text(name) for name in SOURCE_FILE.values()}
        self.assertEqual(len(cj.COLLATION_QUOTES), 22)
        for quote in cj.COLLATION_QUOTES:
            text = texts[SOURCE_FILE[quote["source_id"]]]
            loc = quote["locator"]
            window = text[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(text.count(quote["quote"]), 1, quote["id"])

    def test_section_titles_and_parts(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(sanming[38891:38898], "论天干隂阳生死")
        self.assertEqual(sanming[54895:54909], "论五行旺相休囚死并寄生十二宫")
        parts = cj.COLLATION_SECTIONS[0]["parts"]
        bounds = [parts[0]["locator"]["char_start"]] + \
            [p["locator"]["char_end"] for p in parts]
        self.assertEqual(bounds, [38890, 41810, 42151, 43082])


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 44)
        for note in cj.COLLATION_NOTES:
            offset = note["char_offset"]
            self.assertEqual(sanming[offset], note["snapshot_glyph"],
                             note["id"])
            self.assertEqual(sanming[offset - 14:offset + 15],
                             note["context_short"], note["id"])

    def test_coverage_scans_match_register(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        s1 = sanming[S1[0]:S1[1]]
        s2 = sanming[S2[0]:S2[1]]

        def positions(text: str, base: int, pred) -> list[int]:
            return [base + i for i, ch in enumerate(text) if pred(ch)]

        by_prefix = {}
        for note in cj.COLLATION_NOTES:
            by_prefix.setdefault(note["id"].split("-")[1], set()).add(
                note["char_offset"])
        self.assertEqual(
            set(positions(s1, S1[0], _is_pua)
                + positions(s2, S2[0], _is_pua)),
            by_prefix["pua"])
        self.assertEqual(
            set(positions(s1, S1[0], lambda c: c == "防")
                + positions(s2, S2[0], lambda c: c == "防")),
            by_prefix["fang"])
        self.assertEqual(set(positions(s1, S1[0], lambda c: c == "己")),
                         by_prefix["ji"])
        self.assertEqual(set(positions(s1, S1[0], lambda c: c == "已")),
                         by_prefix["yi"])
        # 第二节无 PUA、己、已（实测），与注册表一致
        self.assertEqual(positions(s2, S2[0], _is_pua), [])
        self.assertEqual(positions(s2, S2[0], lambda c: c in "己已"), [])

    def test_transformed_quotes_match_readings(self) -> None:
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
            transformed = "".join(chars)
            self.assertNotEqual(transformed, quote["quote"], quote["id"])
            if quote["id"] == "sm2.bing_lu":
                self.assertEqual(transformed, "其禄在巳巳为炉冶之火")
            if quote["id"] == "sm2.tiyao":
                self.assertIn("沐浴之㡬", transformed)
            if quote["id"] == "sm2.summary_tu":
                self.assertIn("归禄于巳己临丁", transformed)
                self.assertIn("己土生于酉", transformed)
                self.assertIn("己生邜", transformed)
                self.assertIn("癸己归禄于子", transformed)


class CoverageAnchorTest(unittest.TestCase):
    def test_anchors_slice_equal_and_unique_in_section(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        s1 = sanming[S1[0]:S1[1]]
        for row in cj.STEM_COVERAGE:
            for kind in ("lu", "sheng", "si"):
                cell = row[kind]
                loc = cell["locator"]
                self.assertEqual(
                    sanming[loc["char_start"]:loc["char_end"]],
                    cell["anchor"], f"{row['stem']}.{kind}")
                self.assertEqual(s1.count(cell["anchor"]), 1,
                                 f"{row['stem']}.{kind}")


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
        for needle in ("论天干阴阳生死", "38890–43082",
                       "论五行旺相休囚死并寄生十二宫", "TJ-018-A",
                       "丁长生", "conflict"):
            self.assertIn(needle, sanming, needle)
        shenfeng = by_id["bazi.source.shenfeng"]["review_scope"]
        for needle in ("79659", "十干禄", "丁火长生于酉", "TJ-018-A"):
            self.assertIn(needle, shenfeng, needle)

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_NOTES, ensure_ascii=False)),
            GOLDEN["collation_notes"])
        self.assertEqual(
            json.loads(json.dumps(cj.COLLATION_SECTIONS,
                                  ensure_ascii=False)),
            GOLDEN["sections"])


if __name__ == "__main__":
    unittest.main()
