"""TJ-013.1 S4 密封专项：扶抑最小切片审定登记。

只在组装后的离线验收环境运行（公开 CI 不执行本文件）：

- 快照完整性以 S3 登记钉值复核（滴天髓 sha256/bytes/chars）；
  S3 登记计数（引文 10、判句 37、量化词 27、方向表十行）不变，
  本审定所据文本未漂移；
- S4 审计的十行行文在快照内首尾相接重演，与 S3 登记行逐字一致
  ——审定所据即快照原文；
- 当前状态钉（防夹带实现）：六个已得已审旺衰判定的真实命盘经
  生产链回放（engine.execute），四柱/分类/谓词与各自 Golden
  一致，且执行结果整树不存在任何扶抑产出（键名无 fuyi/扶抑）；
  两例金×酉近失盘回放恒 indeterminate（pure_support_metal 正例
  构造性不可满足的抽查面）；
- 来源普查 101 条（C 95 / D 6）不变；滴天髓 review_scope 维持
  S3 后状态、无 S4 扩充标记（本批不扩任何 Source 范围）。
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_ditiansui_fuyi as fy
from tianji_kb import bazi_fuyi_slice_adjudication as s4
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.engine import execute

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = (ROOT / "data" / "quarantine" / "public_domain_snapshots"
            / "daizhigev20")
SOURCES = json.loads(
    (ROOT / "config" / "knowledge_sources.json").read_text(
        encoding="utf-8"))["sources"]

REGISTERED_RULE_PREDS = ("pure_support", "isolated_control")
METAL_NEAR_MISSES = (
    "1981-09-10T00:30:00+08:00",  # 辛酉/丁酉/辛卯/戊子（S2 Golden）
    "1981-09-09T00:30:00+08:00",  # 辛酉/丁酉/庚寅/丙子（S2 Golden）
)


def _text(name: str) -> str:
    return (SNAP_DIR / name).read_bytes().decode("utf-8")


def run_birth(birth):
    out = execute("bazi", {"value": birth,
                           "strength_variant": ADJUDICATION_VARIANT},
                  allow_research=True)
    result = out["result"]
    pillars = [p["stem"]["value"] + p["branch"]["value"]
               for p in result["pillars"]]
    return result, pillars


def _walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v)


class SnapshotAndRegisterTest(unittest.TestCase):
    def test_snapshot_matches_s3_registry(self) -> None:
        meta = fy.DITIANSHUI_SNAPSHOT
        raw = (SNAP_DIR / "ditiansui_chanwei.txt").read_bytes()
        self.assertEqual(len(raw), meta["bytes"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         meta["sha256"])
        self.assertEqual(len(raw.decode("utf-8")), meta["chars"])

    def test_s3_register_counts_unchanged(self) -> None:
        self.assertEqual(len(fy.FUYI_QUOTES), 10)
        sentences = [s for q in fy.FUYI_QUOTES
                     for s in q["judgment_sentences"]]
        self.assertEqual(len(sentences), 37)
        quantifiers = [e for s in sentences for e in s["quantifiers"]]
        quantifiers += [e for r in fy.FUYI_DIRECTION_TABLE["rows"]
                        for e in r["condition_quantifiers"]]
        self.assertEqual(len(quantifiers), 27)
        self.assertEqual(len(fy.FUYI_DIRECTION_TABLE["rows"]), 10)

    def test_direction_table_audit_slices_match_snapshot(self) -> None:
        text = _text("ditiansui_chanwei.txt")
        table = fy.FUYI_DIRECTION_TABLE
        body = table["body_locator"]
        joined_s3 = "".join(r["text"] for r in table["rows"])
        joined_s4 = "".join(e["text"]
                            for e in s4.DIRECTION_TABLE_AUDIT)
        self.assertEqual(joined_s4, joined_s3)
        self.assertEqual(text[body["char_start"]:body["char_end"]],
                         joined_s4)
        for entry in s4.DIRECTION_TABLE_AUDIT:
            loc = entry["locator"]
            self.assertEqual(text[loc["char_start"]:loc["char_end"]],
                             entry["text"], entry["row"])


class WitnessReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runs = {}
        for w in s4.CURRENT_STATE_PINS["witness_charts"]:
            cls.runs[w["predicate"]] = (w, *run_birth(w["birth"]))

    def test_witness_pillars_and_verdicts(self) -> None:
        for pred, (w, result, pillars) in self.runs.items():
            self.assertEqual(pillars, w["pillars"], pred)
            assessment = result["strength_assessment"]
            self.assertEqual(assessment["classification"],
                             w["classification"], pred)
            if pred in REGISTERED_RULE_PREDS:
                self.assertIn(f"bazi.phase2.strength_{pred}",
                              assessment["matched_rule_ids"], pred)
            else:
                why = assessment["why_not_indeterminate"]
                self.assertEqual(why["sufficient_predicate"], pred)
                self.assertIsNone(why["sufficient_rule"])
                self.assertEqual(
                    why["predicate_rule_registration"],
                    "pending_phase1_rule_registration", pred)

    def test_no_fuyi_output_anywhere(self) -> None:
        # 已得旺衰判定不产生任何扶抑方向产出：整树键名无 fuyi，
        # 裁决对象键名无扶抑/方向产出字段。
        for pred, (w, result, pillars) in self.runs.items():
            for key in _walk_keys(result):
                self.assertNotIn("fuyi", str(key).lower(), pred)
                self.assertNotIn("扶抑", str(key), pred)
            assessment = result["strength_assessment"]
            self.assertNotIn("fuyi_direction", assessment)
            self.assertNotIn("direction", assessment)

    def test_metal_near_misses_stay_indeterminate(self) -> None:
        for birth in METAL_NEAR_MISSES:
            result, _ = run_birth(birth)
            assessment = result["strength_assessment"]
            self.assertEqual(assessment["classification"],
                             "indeterminate", birth)
            for key in _walk_keys(result):
                self.assertNotIn("fuyi", str(key).lower(), birth)


class RegistryScopeTest(unittest.TestCase):
    def test_census_unchanged(self) -> None:
        self.assertEqual(len(SOURCES), 101)
        levels = [s["evidence_level"] for s in SOURCES]
        self.assertEqual(levels.count("C"), 95)
        self.assertEqual(levels.count("D"), 6)

    def test_ditiansui_scope_not_expanded_by_s4(self) -> None:
        src = next(s for s in SOURCES
                   if s["source_id"] == "bazi.source.ditiansui-spouse")
        scope = src["review_scope"]
        self.assertIn("本批（TJ-013.1 S3）逐字登记扶抑三段", scope)
        self.assertNotIn("TJ-013.1 S4", scope)
        self.assertNotIn("扶抑最小切片", scope)


if __name__ == "__main__":
    unittest.main()
