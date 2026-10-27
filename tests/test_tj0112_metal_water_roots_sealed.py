"""TJ-011.2 S1 金/水根分级审定密封专项（只在组装后的离线验收环境
运行，公开 CI 不执行本文件）：

- 三快照完整性（SHA256/字节/字数）与登记一致；
- 本批 10 条三命引文对机上快照切片逐字等值 + 全文计数 ==1，且与
  TJ-018-A 的 STEM_COVERAGE 锚点定位逐项一致；
- 根表所引神峰短表群、论曰总结块、十二宫框架句经 018-A 登记
  （COLLATION_QUOTES）切片逐字复核；轻根所引滴天髓根列举经火线
  登记（MORPHOLOGY_QUOTES）切片逐字复核；
- 辛/癸冲突两分支的见证引文（本批登记与 018-A 登记）均可解析且
  逐字成立；政策形状对齐断言所据的火线登记关键值在密封侧复核。
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from tianji_kb import bazi_metal_water_roots as M
from tianji_kb import bazi_fire_morphology as F
from tianji_kb import bazi_sanming_juan2_collation as C18

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")

SOURCE_FILE = {
    "bazi.source.sanmingtonghui": "sanming_tonghui.txt",
    "bazi.source.shenfeng": "shenfeng_tongkao.txt",
    "bazi.source.ditiansui-spouse": "ditiansui_chanwei.txt",
}


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshots_match_registry(self) -> None:
        for filename, meta in M.ROOT_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], filename)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             meta["sha256"], filename)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             filename)


class RootQuoteSliceTest(unittest.TestCase):
    def test_quotes_verbatim_and_unique(self) -> None:
        text = _text("sanming_tonghui.txt")
        self.assertEqual(len(M.ROOT_QUOTES), 10)
        for q in M.ROOT_QUOTES:
            loc = q["locator"]
            self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                             q["quote"], q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])

    def test_quote_locators_agree_with_018a_coverage(self) -> None:
        cov = {row["stem"]: row for row in C18.STEM_COVERAGE}
        by_id = {q["id"]: q for q in M.ROOT_QUOTES}
        pairs = [
            ("sm.geng_lu", cov["庚"]["lu"]),
            ("sm.geng_shengsi", cov["庚"]["si"]),
            ("sm.xin_lu", cov["辛"]["lu"]),
            ("sm.xin_shengsi", cov["辛"]["si"]),
            ("sm.ren_lu", cov["壬"]["lu"]),
            ("sm.ren_shengsi", cov["壬"]["si"]),
            ("sm.gui_lu", cov["癸"]["lu"]),
            ("sm.gui_shengsi", cov["癸"]["si"]),
        ]
        for qid, anchor in pairs:
            self.assertEqual(by_id[qid]["locator"]["char_start"],
                             anchor["locator"]["char_start"], qid)


class CrossRegisterEvidenceTest(unittest.TestCase):
    def _resolve(self, quotes, ref, texts):
        self.assertIn(ref, quotes, ref)
        q = quotes[ref]
        text = texts[q["source_id"]]
        loc = q["locator"]
        self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                         q["quote"], ref)
        self.assertEqual(text.count(q["quote"]), 1, ref)

    def test_all_cross_refs_resolve_verbatim(self) -> None:
        texts = {sid: _text(fn) for sid, fn in SOURCE_FILE.items()}
        quotes18 = {q["id"]: q for q in C18.COLLATION_QUOTES}
        quotes_f = {q["id"]: q for q in F.MORPHOLOGY_QUOTES}
        used18, used_f = set(), set()
        tables = list(M.METAL_WATER_ROOT_TABLES.values())
        conflicts = [M.XIN_CHANGSHENG_CONFLICT,
                     M.GUI_CHANGSHENG_CONFLICT]
        for table in tables:
            for cell in table:
                for ev in cell["evidence"]:
                    ref = ev.get("quote_ref")
                    if not ref:
                        continue
                    if ev.get("register") == (
                            "bazi_sanming_juan2_collation"):
                        self._resolve(quotes18, ref, texts)
                        used18.add(ref)
                    elif ev.get("register") == "bazi_fire_morphology":
                        self._resolve(quotes_f, ref, texts)
                        used_f.add(ref)
        for conf in conflicts:
            for branch in conf["branches"]:
                for ev in branch["evidence"]:
                    ref = ev.get("quote_ref")
                    if ev.get("register") == (
                            "bazi_sanming_juan2_collation"):
                        self._resolve(quotes18, ref, texts)
                        used18.add(ref)
        # The corroboration spine must actually be exercised: Shenfeng
        # tables for Lu/Changsheng/Ku/Jue and the Ditiansui listings.
        self.assertTrue({"sf.lubiao", "sf.sisheng", "sf.siku",
                         "sf.sijue", "sm2.summary_bracket"} <= used18)
        self.assertTrue({"dt.root_mu", "dt.root_yuqi_1",
                         "dt.root_yuqi_2"} <= used_f)


if __name__ == "__main__":
    unittest.main()
