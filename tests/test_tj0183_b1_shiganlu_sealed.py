"""TJ-018.3-B1 密封快照专项：三命卷三《论十干禄》登记复核。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：把
``bazi_sanming_juan3_collation`` 登记的一节（S0 字符
[74911, 77454)）、30 条引文与 56 条校勘记对机上快照 S0 做切片
逐字等值 + 全文计数复核；PUA / 防 / 己 / 已 / 巳 / 戌 / 戍全量
扫描与登记逐位对账；S0→S3 差异恰 17 处与残余防 1 处对账；
密封校勘 11 条与候选池 3 条在本窗口的处置对账；Slice A 定义句
引文在快照上逐字复核；来源普查（102 条）与既有六册在本环境
一并回归。
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
from tianji_kb import bazi_sanming_juan3_collation as cj
from tianji_kb import bazi_sanming_juan5_quliu_collation as cjd
from tianji_kb import bazi_sanming_juan5_zaqi_yangren_collation as cje
from tianji_kb import bazi_sanming_juan6_fangju_baxiang_collation as cjf

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

SEC = (74911, 77454)
SEC_S3 = (74910, 77453)
S3_SHA256 = "a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff7154f2c217662f"


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


def _is_pua(ch: str) -> bool:
    return 0xE000 <= ord(ch) <= 0xF8FF


def _scan(text: str, glyph: str) -> list[int]:
    return [i for i in range(SEC[0], SEC[1]) if text[i] == glyph]


class SnapshotIntegrityTest(unittest.TestCase):
    def test_s0_matches_registry(self) -> None:
        meta = cj.COLLATION_SNAPSHOTS["sanming_tonghui.txt"]
        raw = (SNAPSHOT_DIR / "sanming_tonghui.txt").read_bytes()
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])

    def test_s3_identity(self) -> None:
        raw = (SNAPSHOT_DIR / "sanming_tonghui_applied_v1.txt").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), S3_SHA256)
        self.assertEqual(len(raw.decode("utf-8")), 461156)


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_QUOTES), 30)
        for quote in cj.COLLATION_QUOTES:
            loc = quote["locator"]
            window = sanming[loc["char_start"]:loc["char_end"]]
            self.assertEqual(window, quote["quote"], quote["id"])
            self.assertEqual(sanming.count(quote["quote"]), 1, quote["id"])

    def test_section_title_and_bounds(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        sec = cj.COLLATION_SECTIONS[0]
        self.assertEqual(sanming[SEC[0]:SEC[0] + 25],
                         sec["title_snapshot"])
        # 节终点即下一节《论驿马》节题起点
        self.assertEqual(sanming[SEC[1]:SEC[1] + 3], "论驿马")
        # 金轝附论题在主文终点后两字（换行 + 空格为快照体例）
        self.assertEqual(sanming[77216:77219], "论金轝")

    def test_slice_a_quote_still_verbatim(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        luren = {q["id"]: q for q in pat_mod.LUREN_QUOTES}
        target = luren["sanming.lu_sentence"]
        loc = target["locator"]
        self.assertEqual(sanming[loc["char_start"]:loc["char_end"]],
                         target["quote"])
        ours = {q["id"]: q for q in cj.COLLATION_QUOTES}
        self.assertEqual(ours["sgl.definition"]["quote"], target["quote"])
        self.assertEqual(ours["sgl.definition"]["locator"], loc)


class CollationNoteSliceTest(unittest.TestCase):
    def test_notes_pin_to_snapshot(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        self.assertEqual(len(cj.COLLATION_NOTES), 56)
        for note in cj.COLLATION_NOTES:
            off = note["char_offset"]
            self.assertEqual(sanming[off], note["snapshot_glyph"],
                             note["id"])
            self.assertEqual(sanming[off - 14:off + 15],
                             note["context_short"], note["id"])

    def test_coverage_scans_match_register(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        pua = [i for i in range(SEC[0], SEC[1]) if _is_pua(sanming[i])]
        self.assertEqual(pua, [76614, 77193])
        notes = cj.COLLATION_NOTES
        fang = sorted(n["char_offset"] for n in notes
                      if n["id"].split("-")[1] == "fang")
        self.assertEqual(_scan(sanming, "防"), fang)
        self.assertEqual(len(fang), 16)
        ji_all = sorted(n["char_offset"] for n in notes
                        if n["id"].split("-")[1] == "ji")
        self.assertEqual(_scan(sanming, "己"), ji_all)
        self.assertEqual(len(ji_all), 23)
        self.assertEqual(_scan(sanming, "已"), [76644, 76744])
        part = cj.SI_GLYPH_DISPOSITION
        si_all = sorted(part["stem_slot_offsets"]
                        + part["branch_slot_offsets"])
        self.assertEqual(_scan(sanming, "巳"), si_all)
        self.assertEqual(len(si_all), 18)
        xu = sorted(n["char_offset"] for n in notes
                    if n["id"].split("-")[1] == "xu")
        self.assertEqual(_scan(sanming, "戌"), xu)
        self.assertEqual(len(xu), 12)
        self.assertEqual(_scan(sanming, "戍"), [])

    def test_transformed_quotes_match_mapped_readings(self) -> None:
        sanming = _text("sanming_tonghui.txt")
        notes = {n["char_offset"]: n for n in cj.COLLATION_NOTES}
        checked = 0
        for quote in cj.COLLATION_QUOTES:
            if "mapped_reading" not in quote:
                continue
            checked += 1
            loc = quote["locator"]
            chars = list(sanming[loc["char_start"]:loc["char_end"]])
            for ref in quote["collation_refs"]:
                note = [n for n in cj.COLLATION_NOTES
                        if n["id"] == ref][0]
                chars[note["char_offset"] - loc["char_start"]] = \
                    note["reading"]
            self.assertEqual("".join(chars), quote["mapped_reading"],
                             quote["id"])
        self.assertEqual(checked, 18)


class AppliedTextReconciliationTest(unittest.TestCase):
    def test_s0_s3_diff_exactly_17(self) -> None:
        s0 = _text("sanming_tonghui.txt")
        s3 = _text("sanming_tonghui_applied_v1.txt")
        sec0 = s0[SEC[0]:SEC[1]]
        sec3 = s3[SEC_S3[0]:SEC_S3[1]]
        self.assertEqual(len(sec0), 2543)
        self.assertEqual(len(sec3), 2543)
        diffs = [i for i in range(2543) if sec0[i] != sec3[i]]
        notes = cj.COLLATION_NOTES
        expected = sorted(
            n["char_offset"] - SEC[0] for n in notes
            if n["disposition"] == "corrected"
            and n["id"].split("-")[1] in ("fang", "pua"))
        self.assertEqual(diffs, expected)
        self.assertEqual(len(diffs), 17)
        for i in diffs:
            self.assertEqual(sec3[i],
                             [n for n in notes
                              if n["char_offset"] == SEC[0] + i][0]
                             ["reading"], f"index {i}")

    def test_s3_residual_fang_single(self) -> None:
        s3 = _text("sanming_tonghui_applied_v1.txt")
        sec3 = s3[SEC_S3[0]:SEC_S3[1]]
        self.assertEqual([i for i, c in enumerate(sec3) if c == "防"],
                         [76988 - SEC[0]])
        self.assertEqual(sec3[76988 - SEC[0] - 2:76988 - SEC[0] + 2],
                         "有市防态")


class SealedAssetReconciliationTest(unittest.TestCase):
    def test_text_collation_entries_in_window(self) -> None:
        col = json.loads((SNAPSHOT_DIR / "sanming_text_collation.json")
                         .read_text(encoding="utf-8"))
        by_id = {e["id"]: e for e in col["corrections"]}
        s0 = _text("sanming_tonghui.txt")
        s3 = _text("sanming_tonghui_applied_v1.txt")
        expected = cj.SEALED_ASSET_RECONCILIATION[
            "text_collation_in_window"]
        self.assertEqual(len(expected), 11)
        # 本批防注记 basis 引用的密封订正 id 集合与对账清单一致
        linked = set()
        for n in cj.COLLATION_NOTES:
            for b in n["basis"]:
                if b["witness"].startswith("sanming_text_collation.json "):
                    linked.add(b["witness"].split()[-1])
        self.assertEqual(linked, set(expected))
        for cid in expected:
            entry = by_id[cid]
            self.assertEqual(s0.count(entry["old"]), 1, cid)
            self.assertEqual(s3.count(entry["new"]), 1, cid)

    def test_ocr_candidates_in_window(self) -> None:
        cand = json.loads((SNAPSHOT_DIR / "sanming_ocr_candidates.json")
                          .read_text(encoding="utf-8"))
        entries = cand["candidates"]
        window = [c for c in entries
                  if SEC[0] <= c["baseline_character_offset"] + 1 < SEC[1]]
        got = sorted((c["baseline_character_offset"] + 1, c["status"])
                     for c in window)
        self.assertEqual(got, [(75722, "confirmed_applied"),
                               (76614, "historical_only_hold"),
                               (76988, "historical_only_hold")])


class RegistrationCensusSealedTest(unittest.TestCase):
    def test_source_census_and_scope(self) -> None:
        self.assertEqual(len(SOURCES), 102)
        by_id = {s["source_id"]: s for s in SOURCES}
        sanming = by_id["bazi.source.sanmingtonghui"]["review_scope"]
        for needle in ("论十干禄", "74911", "77454", "TJ-018.3-B1",
                       "439 条"):
            self.assertIn(needle, sanming)

    def test_previous_registers_still_pinned(self) -> None:
        self.assertEqual(len(cja.COLLATION_NOTES), 44)
        self.assertEqual(len(cjb.COLLATION_NOTES), 35)
        self.assertEqual(len(cjc.COLLATION_NOTES), 81)
        self.assertEqual(len(cjd.COLLATION_NOTES), 43)
        self.assertEqual(len(cje.COLLATION_NOTES), 108)
        self.assertEqual(len(cjf.COLLATION_NOTES), 72)


if __name__ == "__main__":
    unittest.main()
