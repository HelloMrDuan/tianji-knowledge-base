"""TJ-018.3 晋级 P2 残余「防」处置登记册密封专项（对密封原文执行）。

核验链：六件密封文件哈希钉逐字未动 → 两阶段带 origin 追踪的
复放重建 S1/S2/S3 并验四钉 → S3 残余「防」位点全量与登记册
盘点逐处对平（坐标、origin、±6 语境及哈希）→ 候选位点与
RD-12 标记对应用报告 dispositions 对账 → 695 条处置的校勘记
交叉核对（带校勘记者 40 条；第二至第九分册 652 条无校勘记，
断言其位点不在校勘记集合内）。本专项只读密封资产，不改任何
文本与登记。
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_sanming_fang_disposition as fd
from tianji_kb import (bazi_sanming_juan2_collation,
                       bazi_sanming_juan2_hehua_collation,
                       bazi_sanming_juan2_sanxing_collation,
                       bazi_sanming_juan5_quliu_collation,
                       bazi_sanming_juan5_zaqi_yangren_collation,
                       bazi_sanming_juan6_fangju_baxiang_collation)

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
REG = fd.FANG_DISPOSITION_REGISTER
INV = REG["inventory"]
DISP = REG["dispositions"]

PUA_COL_SHA256 = ("96943525453662663918965d28711a2f1b0758aef7bc9b4a3"
                  "aaafb770dbfdd97")
TEXT_COL_SHA256 = ("e47bce8c478327b3bcb7f804c29ad4189d824b40a9d2e0e"
                   "a5032ddebf39ff4ce")


def _load(name):
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def _text(name):
    return (SNAPSHOT_DIR / name).read_bytes().decode("utf-8")


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _file_sha(name):
    return hashlib.sha256((SNAPSHOT_DIR / name).read_bytes()).hexdigest()


def _replace_tracked(chars, origins, old, new, count_all=False):
    """Replace occurrence(s) of old with new, tracking origins.

    New characters inherit the origin of the positionally
    corresponding old character (clamped to the old span), which
    is exact for the 1:1 PUA mappings and position-wise for the
    correction spans that carry a residual fang.
    """
    old_l = list(old)
    new_l = list(new)
    text = "".join(chars)
    start = 0
    replaced = 0
    while True:
        i = text.find(old, start)
        if i < 0:
            break
        span_origins = origins[i:i + len(old_l)]
        new_origins = [span_origins[min(j, len(span_origins) - 1)]
                       for j in range(len(new_l))]
        chars[i:i + len(old_l)] = new_l
        origins[i:i + len(old_l)] = new_origins
        replaced += 1
        start = i + len(new_l)
        text = "".join(chars)
        if not count_all:
            break
    return replaced


def _replay(snapshot, pua_spec, corrections):
    chars = list(snapshot)
    origins = list(range(len(chars)))
    for row in pua_spec.get("mappings", []):
        if row.get("status") != "confirmed":
            continue
        n = _replace_tracked(chars, origins, row["glyph"],
                             row["replacement"], count_all=True)
        assert n == int(row["count"]), row["codepoint"]
    for row in pua_spec.get("contextual_mappings", []):
        if row.get("status") != "confirmed":
            continue
        for rule in row["replacements"]:
            n = _replace_tracked(chars, origins, rule["old"],
                                 rule["new"])
            assert n == 1, row["codepoint"]
    s1 = "".join(chars)
    s2 = None
    for idx, row in enumerate(corrections):
        n = _replace_tracked(chars, origins, row["old"], row["new"])
        assert n == 1, row["id"]
        if idx == 443:
            s2 = "".join(chars)
    return s1, s2, "".join(chars), origins


def _collation_notes():
    notes = {}
    for mod in (bazi_sanming_juan2_collation,
                bazi_sanming_juan2_sanxing_collation,
                bazi_sanming_juan2_hehua_collation,
                bazi_sanming_juan5_quliu_collation,
                bazi_sanming_juan5_zaqi_yangren_collation,
                bazi_sanming_juan6_fangju_baxiang_collation):
        for note in mod.COLLATION_NOTES:
            if "-fang-" in note["id"]:
                notes[note["char_offset"]] = note
    return notes


class TestFangDispositionSealed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s0 = _text("sanming_tonghui.txt")
        cls.s3 = _text("sanming_tonghui_applied_v1.txt")
        cls.pua = _load("sanming_pua_collation.json")
        cls.col = _load("sanming_text_collation.json")
        cls.cands = _load("sanming_ocr_candidates.json")["candidates"]
        cls.report = _load("sanming_formal_application_report_v1.json")
        cls.s1, cls.s2, cls.s3r, cls.origins = _replay(
            cls.s0, cls.pua, cls.col["corrections"])

    def test_sealed_files_unchanged(self):
        inp = REG["inputs"]
        self.assertEqual(_file_sha("sanming_tonghui.txt"),
                         inp["snapshot"]["sha256"])
        self.assertEqual(_file_sha("sanming_tonghui_applied_v1.txt"),
                         inp["applied_text"]["sha256"])
        self.assertEqual(
            _file_sha("sanming_formal_application_report_v1.json"),
            inp["application_report"]["file_sha256"])
        self.assertEqual(_file_sha("sanming_ocr_candidates.json"),
                         inp["candidates_file"]["sha256"])
        self.assertEqual(_file_sha("sanming_pua_collation.json"),
                         PUA_COL_SHA256)
        self.assertEqual(_file_sha("sanming_text_collation.json"),
                         TEXT_COL_SHA256)

    def test_stage_replay_pins(self):
        self.assertEqual(_sha(self.s1),
                         "b4f196f2100347618d7907330b2db93bd536a5663f16249"
                         "a6e0ff19e23c05daa")
        self.assertEqual(_sha(self.s2),
                         "db8618c9cdbc545b59149f7550644a44"
                         "0fdf8bba8ddbe0e23b615029f8a896d9")
        self.assertEqual(self.s3r, self.s3)
        self.assertEqual(_sha(self.s3),
                         REG["inputs"]["applied_text"]["sha256"])
        self.assertEqual(self.report["residual_scan"]["fang"], 769)
        self.assertEqual(self.report["residual_scan"]["pua_codepoints"], 0)
        self.assertEqual(self.report["residual_scan"]["gap_square"], 2)

    def test_inventory_against_sealed(self):
        loci = [i for i, ch in enumerate(self.s3) if ch == "防"]
        self.assertEqual(loci, [x["s3_offset"] for x in INV])
        self.assertEqual(len(self.cands), 993)
        disp_by_s3 = {d["site_s3_offset"]: d
                      for d in self.report["candidate_annex"]
                      ["dispositions"]}
        self.assertEqual(len(disp_by_s3), 993)
        for x in INV:
            o3 = x["s3_offset"]
            o0 = self.origins[o3]
            self.assertEqual(o0, x["s0_offset"], x["seq"])
            self.assertEqual(self.s0[o0], "防", x["seq"])
            ctx = self.s3[o3 - 6:o3 + 7]
            self.assertEqual(ctx, x["context_s3"], x["seq"])
            self.assertEqual(_sha(ctx), x["context_s3_sha256"], x["seq"])
            if x["candidate_site"]:
                d = disp_by_s3[o3]
                self.assertEqual(d["site_s0_offset"], o0, x["seq"])
            if x["rd12_seq"]:
                d = disp_by_s3[o3]
                self.assertTrue(
                    d["flags"]["in_reading_disagreement_12"], x["seq"])
                self.assertEqual(d["seq"], x["rd12_seq"], x["seq"])

    def test_dispositions_verbatim_and_notes(self):
        notes = _collation_notes()
        self.assertEqual(len(notes), 106)
        self.assertEqual(len(DISP), 695)
        fang_notes_in_sections = {x["collation_note_id"] for x in INV
                                  if x["collation_note_id"]}
        self.assertEqual(len(fang_notes_in_sections), 40)
        for d in DISP:
            x = [r for r in INV if r["s0_offset"] == d["s0_offset"]][0]
            self.assertEqual(self.s3[d["s3_offset"]], "防")
            self.assertEqual(x["context_s3"][6], "防")
            if d["collation_note_id"]:
                note = notes[d["s0_offset"]]
                self.assertEqual(note["id"], d["collation_note_id"])
                self.assertEqual(note["reading"],
                                 d["collation_note_reading"])
                self.assertEqual(note["reading_status"],
                                 d["collation_note_status"])
                self.assertEqual(note["disposition"],
                                 d["collation_note_disposition"])
                if d["category"] in ("disposed_confirmed",
                                     "disposed_kept"):
                    self.assertEqual(d["reading_glyph"], note["reading"])
            else:
                self.assertNotIn(d["s0_offset"], notes)


if __name__ == "__main__":
    unittest.main()
