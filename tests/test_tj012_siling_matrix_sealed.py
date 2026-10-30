"""TJ-012.3 Slice C 第一步密封快照专项：分日司令冲突矩阵登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_siling_matrix`` 登记的 36 条引文对机上快照做切片逐字等值 +
全文计数 ==1 复核；五份快照本身做 SHA256 / 字节数 / 字符数校验；
三命本节唯一 PUA（U+EA20，字符 48861，落在醉醒子关键句内）逐字保留
并钉位；来源普查钉值（101 条，C 95 / D 6）与五来源 review_scope
新增段落钉值。登记引文的字符区间以机上实测为准。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_siling_matrix as sm

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_siling_matrix.json").read_text(
        encoding="utf-8"))

SOURCE_FILE = {
    "bazi.source.ditiansui-spouse": "ditiansui_chanwei.txt",
    "bazi.source.sanmingtonghui": "sanming_tonghui.txt",
    "bazi.source.yuanhai": "yuanhai_ziping.txt",
    "bazi.source.shenfeng": "shenfeng_tongkao.txt",
    "bazi.source.qiongtong": "qiongtong_baojian.txt",
}
PUA_QUOTES = {"sm.zuixingzi_block", "sm.zuixingzi_key"}


def _snapshot_text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_five_snapshots_match_registry(self) -> None:
        for filename, meta in sm.SILING_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], filename)
            self.assertEqual(
                hashlib.sha256(raw).hexdigest(), meta["sha256"], filename)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             filename)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        texts = {name: _snapshot_text(name) for name in SOURCE_FILE.values()}
        self.assertEqual(len(sm.SILING_QUOTES), 36)
        for quote in sm.SILING_QUOTES:
            text = texts[SOURCE_FILE[quote["source_id"]]]
            locator = quote["locator"]
            window = text[locator["char_start"]:locator["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(text.count(quote["quote"]), 1, quote["id"])

    def test_pua_pinned_to_zuixingzi_key_sentence(self) -> None:
        sanming = _snapshot_text("sanming_tonghui.txt")
        # 本节（《论人元司事》，字符 47833–49050）窗口内 PUA 恰一处：
        # U+EA20 在 48861，落在醉醒子关键句「进退之<PUA>机」内。
        # （全书他处另有同码位字形，不在本批登记窗口内，不作断言。）
        section = sanming[47833:49050]
        pua = [c for c in section if 0xE000 <= ord(c) <= 0xF8FF]
        self.assertEqual(pua, ["\uea20"])
        self.assertEqual(sanming[48861], "\uea20")
        for quote in sm.SILING_QUOTES:
            has_pua = any(0xE000 <= ord(c) <= 0xF8FF
                          for c in quote["quote"])
            if quote["id"] in PUA_QUOTES:
                self.assertTrue(has_pua, quote["id"])
                self.assertTrue(quote.get("contains_pua"), quote["id"])
                self.assertEqual(quote["quote"].count("\uea20"), 1,
                                 quote["id"])
            else:
                self.assertFalse(has_pua, quote["id"])


class RegistrationCensusTest(unittest.TestCase):
    def test_source_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 102)
        grades: dict[str, int] = {}
        for source in SOURCES:
            grade = source["evidence_level"]
            grades[grade] = grades.get(grade, 0) + 1
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied
        # （《三命通会》正式应用文本，C 级）后来源普查由 C:95 变 C:96
        # （登记表共 102 条），同上口径。
        self.assertEqual(grades, {"C": 96, "D": 6})

    def test_review_scope_additions_present(self) -> None:
        by_id = {s["source_id"]: s for s in SOURCES}
        fragments = {
            "bazi.source.sanmingtonghui": [
                "论人元司事", "sanming-t1", "sanming-t2",
                "酉合计 32 日", "岂可以几日为限哉",
            ],
            "bazi.source.ditiansui-spouse": [
                "s024", "余月依此而论", "pilot_authorized_ren_branch",
            ],
            "bazi.source.yuanhai": ["暗藏总诀", "念三", "不闭合"],
            "bazi.source.shenfeng": ["地支造化图", "不可复原", "节气歌断"],
            "bazi.source.qiongtong": ["缺证", "分日」与「用事」均 0 命中"],
        }
        for source_id, needles in fragments.items():
            scope = by_id[source_id]["review_scope"]
            for needle in needles:
                self.assertIn(needle, scope, f"{source_id}: {needle}")

    def test_module_matches_golden(self) -> None:
        self.assertEqual(
            json.loads(json.dumps(sm.SILING_QUOTES, ensure_ascii=False)),
            GOLDEN["quotes"])
        self.assertEqual(
            json.loads(json.dumps(sm.SILING_MATRIX, ensure_ascii=False)),
            GOLDEN["matrix"])


if __name__ == "__main__":
    unittest.main()
