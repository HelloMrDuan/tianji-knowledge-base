"""TJ-011.2 火线形态审定密封专项（只在组装后的离线验收环境运行，
公开 CI 不执行本文件）：

- 登记的 10 条滴天髓引文对机上快照切片逐字等值 + 全文计数 ==1；
- 丙根位所引三命/神峰引文经 TJ-018-A 登记（COLLATION_QUOTES）切片
  逐字复核，分级与 018-A 覆盖表一致；
- Golden 设计四例经生产历法链（engine.execute）实算四柱，与设计
  文件逐柱一致（设计阶段以 sxtwl 复核的日柱/月支在此终验）；
- 设计批时点四例在 bazi-strength-adjudication-v1 下均为
  indeterminate（证明设计批未夹带实现）；实现批（commanding_
  visible_support 谓词）落地后本断言已按实现期望更新：正强例为
  strong（sufficient_predicate=commanding_visible_support），其余
  三例仍 indeterminate——见 test_implementation_outcomes。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_fire_morphology as M
from tianji_kb import bazi_sanming_juan2_collation as C18
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.engine import execute

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
                / "daizhigev20")
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj0112_fire_morphology.json").read_text(
        encoding="utf-8"))

SOURCE_FILE = {
    "bazi.source.sanmingtonghui": "sanming_tonghui.txt",
    "bazi.source.shenfeng": "shenfeng_tongkao.txt",
    "bazi.source.yuanhai": "yuanhai_ziping.txt",
    "bazi.source.ditiansui-spouse": "ditiansui_chanwei.txt",
}


def _text(filename: str) -> str:
    return (SNAPSHOT_DIR / filename).read_bytes().decode("utf-8")


class SnapshotIntegrityTest(unittest.TestCase):
    def test_snapshots_match_registry(self) -> None:
        for filename, meta in M.MORPHOLOGY_SNAPSHOTS.items():
            raw = (SNAPSHOT_DIR / filename).read_bytes()
            self.assertEqual(len(raw), meta["bytes"], filename)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             meta["sha256"], filename)
            self.assertEqual(len(raw.decode("utf-8")), meta["chars"],
                             filename)


class DitiansuiQuoteSliceTest(unittest.TestCase):
    def test_definition_and_root_quotes_verbatim(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        self.assertEqual(len(M.MORPHOLOGY_QUOTES), 10)
        for q in M.MORPHOLOGY_QUOTES:
            loc = q["locator"]
            self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                             q["quote"], q["id"])
            self.assertEqual(text.count(q["quote"]), 1, q["id"])


class RootEvidenceCrossCheckTest(unittest.TestCase):
    def test_sanming_refs_resolve_verbatim(self) -> None:
        quotes18 = {q["id"]: q for q in C18.COLLATION_QUOTES}
        texts = {sid: _text(fn) for sid, fn in SOURCE_FILE.items()}
        used = set()
        for pos in M.BING_ROOT_POSITIONS:
            for ev in pos["evidence"]:
                ref = ev.get("quote_ref")
                if not ref or ev.get("register") != ("bazi_sanming_"
                                                    "juan2_collation"):
                    continue
                self.assertIn(ref, quotes18, (pos["branch"], ref))
                q = quotes18[ref]
                text = texts[q["source_id"]]
                loc = q["locator"]
                self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                                 q["quote"], ref)
                self.assertEqual(text.count(q["quote"]), 1, ref)
                used.add(ref)
        # The per-stem-listed heavy roots must actually lean on the
        # registered per-stem quotes, not on air.
        self.assertTrue({"sm2.bing_sheng", "sm2.bing_lu"} <= used)


class GoldenCalendarReplayTest(unittest.TestCase):
    def _run(self, case):
        out = execute("bazi", {"value": case["source_birth"],
                               "strength_variant": ADJUDICATION_VARIANT},
                      allow_research=True)
        result = out["result"]
        pillars = [p["stem"]["value"] + p["branch"]["value"]
                   for p in result["pillars"]]
        return result, pillars

    def test_design_pillars_replay_exactly(self) -> None:
        self.assertEqual(len(GOLDEN["cases"]), 4)
        for case in GOLDEN["cases"]:
            _, pillars = self._run(case)
            self.assertEqual(pillars, case["expected_pillars"], case["id"])

    def test_implementation_outcomes(self) -> None:
        # Updated by the TJ-011.2 implementation batch: the design
        # batch's no-smuggling assertion (all four indeterminate) held
        # at design time. Now the positive case is strong via the
        # commanding_visible_support predicate (bounded exit, pending
        # registration), and the other three design cases remain
        # indeterminate for their registered reasons.
        for case in GOLDEN["cases"]:
            result, _ = self._run(case)
            assessment = result["strength_assessment"]
            if case["category"] == "positive_strong":
                self.assertEqual(assessment["classification"],
                                 "strong", case["id"])
                why = assessment["why_not_indeterminate"]
                self.assertIsNotNone(why, case["id"])
                self.assertEqual(why["sufficient_predicate"],
                                 "commanding_visible_support",
                                 case["id"])
                self.assertIsNone(why["sufficient_rule"], case["id"])
            else:
                self.assertEqual(assessment["classification"],
                                 "indeterminate", case["id"])
                self.assertEqual(assessment["decision_status"],
                                 "insufficient_reviewed_rules", case["id"])
                self.assertIsNone(assessment["why_not_indeterminate"],
                                  case["id"])


if __name__ == "__main__":
    unittest.main()
