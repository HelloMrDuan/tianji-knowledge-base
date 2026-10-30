"""TJ-012.3 证据登记批密封快照专项：滴天髓阐微《化象》章整章登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：逐条把
``bazi_ditiansui_huaxiang`` 登记对机上快照做切片逐字等值 + 全文计数
==1 复核（整章 1646 字、引文 19 条、例造干支行 45 行、层属标记位
点）；章界钉值（起于「十三、化象」、终于「十四、假从」之前）；
字形疑点 10 项逐位钉定；章内缺字/PUA 对账（半角 ? 0、PUA 0；全书
? 共 132 处均在章外）；来源普查钉值（101 条，C 95 / D 6）与滴天髓
review_scope 新增段落钉值；E0270 合化登记册逐字未改钉值（F5/F6 在
该册内仍为 audit_entry_only、裁定语义未变）。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ditiansui_huaxiang as hx
from tianji_kb import bazi_hehua_fact_adjudication as hh

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20" / "ditiansui_chanwei.txt")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]


def _raw() -> bytes:
    return SNAPSHOT.read_bytes()


def _text() -> str:
    return _raw().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshot_matches_registry(self) -> None:
        raw = _raw()
        meta = hx.DITIANSHUI_SNAPSHOT
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])
        self.assertEqual(meta["chars"], 139538)
        # git blob sha (sha1 of "blob <len>\\0" + content), as registered
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode()
                            + b"\x00" + raw).hexdigest()
        self.assertEqual(blob, meta["blob_sha"])
        src = next(s for s in SOURCES
                   if s["source_id"] == "bazi.source.ditiansui-spouse")
        self.assertEqual(src["blob_sha"], meta["blob_sha"])
        self.assertEqual(src["sha256"], meta["sha256"])


class ChapterSliceTest(unittest.TestCase):
    def test_full_chapter_slice_equal_and_unique(self) -> None:
        text = _text()
        ch = hx.HUAXIANG_CHAPTER
        loc = ch["locator"]
        self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                         ch["full_text"])
        self.assertEqual(text.count(ch["full_text"]), 1)

    def test_chapter_boundaries(self) -> None:
        text = _text()
        self.assertEqual(text[98297:98302], "十三、化象")
        self.assertTrue(text[98297:].startswith("十三、化象\n"))
        self.assertTrue(text[99943:].startswith("十四、假从\n"))
        self.assertEqual(text[98303:98319], "化得真者只论化,化神还有几般话。")


class QuoteSliceTest(unittest.TestCase):
    def test_quotes_slice_equal_and_unique(self) -> None:
        text = _text()
        self.assertEqual(len(hx.HUAXIANG_QUOTES), 19)
        for q in hx.HUAXIANG_QUOTES:
            loc = q["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], q["quote"],
                q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])

    def test_layer_markers(self) -> None:
        text = _text()
        self.assertEqual(text[98320:98323], "原注:")
        self.assertEqual(text[98508:98512], "任氏曰:")

    def test_example_chart_lines_slice_equal(self) -> None:
        text = _text()
        lines = [line for s in hx.HUAXIANG_SEGMENTS
                 if s["layer"] == "任氏曰（例造）"
                 for line in s["chart_lines"]]
        self.assertEqual(len(lines), 45)
        for line in lines:
            loc = line["locator"]
            self.assertEqual(
                text[loc["char_start"]:loc["char_end"]], line["text"],
                (loc["char_start"], line["text"]))


class GlyphPositionTest(unittest.TestCase):
    def test_single_char_positions(self) -> None:
        text = _text()
        self.assertEqual(text[98336], "已")
        self.assertEqual(text[98531], "爱")
        self.assertEqual(text[98459], " ")
        self.assertEqual(text[99113], "秘")
        self.assertEqual(text[99451], "黄")
        self.assertEqual(text[99463], "黄")
        self.assertEqual(text[99915], "挑")

    def test_span_positions(self) -> None:
        text = _text()
        self.assertEqual(text[98344:98354], "遇壬、癸、甲、乙、戊")
        self.assertEqual(text[98877:98886], "辰龙之说,供引之意")
        self.assertEqual(text[99145:99155], "火虽有虚,水木无而实")

    def test_glyph_register_matches_text(self) -> None:
        text = _text()
        for g in hx.HUAXIANG_GLYPH_NOTES:
            if "position" in g:
                self.assertEqual(text[g["position"]], g["char"], g["id"])
            else:
                span = g["span"]
                piece = text[span["char_start"]:span["char_end"]]
                self.assertEqual(len(piece),
                                 span["char_end"] - span["char_start"],
                                 g["id"])
                self.assertTrue(piece, g["id"])


class ChapterHygieneTest(unittest.TestCase):
    def test_no_placeholders_or_pua_in_chapter(self) -> None:
        text = _text()
        chapter = text[98297:99943]
        self.assertEqual(chapter.count("?"), 0)
        self.assertEqual(chapter.count("？"), 0)
        self.assertEqual(
            sum(1 for c in chapter if 0xE000 <= ord(c) <= 0xF8FF), 0)
        # whole-book reconciliation: all 132 half-width ? sit outside
        self.assertEqual(text.count("?"), 132)
        self.assertEqual(
            sum(1 for c in text if 0xE000 <= ord(c) <= 0xF8FF), 0)


class RegistryTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        # TJ-018.3 P1 普查同步：登记 bazi.source.sanmingtonghui-applied（C 级）后登记表 101→102 条、C:95→C:96，非放宽断言。
        self.assertEqual(len(SOURCES), 102)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 96)
        self.assertEqual(levels.count("D"), 6)

    def test_ditiansui_review_scope_extended(self) -> None:
        src = next(s for s in SOURCES
                   if s["source_id"] == "bazi.source.ditiansui-spouse")
        scope = src["review_scope"]
        for marker in ("《化象》章整章登记", "98297", "99943",
                       "引文 19 条", "同题异述",
                       "transformation_status 恒 unresolved"):
            self.assertIn(marker, scope)
        # earlier paragraphs are appended to, never replaced
        self.assertIn("扶抑三段", scope)
        self.assertIn("影响遥系", scope)


class HehuaRegisterUnchangedTest(unittest.TestCase):
    def test_f5_f6_still_audit_only_in_e0270_register(self) -> None:
        forms = {f["id"]: f for f in hh.FORMULATION_REGISTER}
        for fid in ("F5", "F6"):
            self.assertFalse(forms[fid]["registered"], fid)
            self.assertEqual(forms[fid]["status"],
                             "audit_entry_only_not_registered", fid)
            self.assertEqual(forms[fid]["evidence_quotes"], [], fid)

    def test_e0270_verdicts_unchanged(self) -> None:
        hv = hh.HEHUA_ADJUDICATION_REGISTER["headline_verdicts"]
        self.assertEqual(hv["true_conflicts"], 4)
        self.assertFalse(hv["formulation_adjudicated"])
        self.assertFalse(hv["transformation_status_changed"])
        self.assertFalse(
            hh.STATUS_QUO_LINKAGE["adjudication_semantics_changed"])
        pending = {p["id"]: p for p in hh.PENDING_ITEMS}
        self.assertIn("滴天髓《化象》章登记", pending["B4"]["item"])


if __name__ == "__main__":
    unittest.main()
