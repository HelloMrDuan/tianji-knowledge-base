"""TJ-012.3 Slice C step 1 的公开结构测试：分日司令冲突矩阵登记。

本模块（``bazi_siling_matrix``）是纯数据登记、零计算逻辑；本测试只钉
登记结构与裁定红线（五口径齐备且互不相同一、T1/T2 分离、T2 两格算术
原样、异议在案、神峰不可复原、穷通缺证、裁定状态全域、统一表禁止键、
层属、计算约定），不验证任何司令计算（不存在此种代码路径）。
引文逐字等值与快照复核在密封专项
``tests/test_tj012_siling_matrix_sealed.py``（仅离线验收）。
"""

from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from tianji_kb import bazi_siling_matrix as sm

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / "tests" / "golden_tj012_siling_matrix.json").read_text(
        encoding="utf-8"))

FORBIDDEN_KEYS = {
    "unified_table", "merged_table", "combined_table",
    "default_version", "recommended_version", "preferred_version",
    "selected_version",
    "统一计算表", "合并表", "统一表", "默认口径", "推荐口径", "优选",
}
VERSION_IDS = ["ditiansui-yuanshuo", "sanming-t1", "sanming-t2",
               "yuanhai-zongjue", "shenfeng-diagram"]


def _norm(value):
    if isinstance(value, tuple):
        return [_norm(item) for item in value]
    if isinstance(value, list):
        return [_norm(item) for item in value]
    if isinstance(value, dict):
        return {key: _norm(item) for key, item in value.items()}
    return value


def _walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def _cell_signature(cell):
    if "segments" in cell:
        return frozenset((s["stem"], s["days"]) for s in cell["segments"])
    if "segments_as_printed" in cell:
        return frozenset((s["stem"], s["days"])
                         for s in cell["segments_as_printed"])
    if "parsed_claims" in cell:
        return frozenset((c["stem"], c["days"])
                           for c in cell["parsed_claims"])
    return cell["status"]


class MirrorTest(unittest.TestCase):
    def test_module_mirrors_golden(self) -> None:
        self.assertEqual(sm.SILING_MATRIX_ID, GOLDEN["registration_id"])
        self.assertEqual(sm.SILING_TASK, GOLDEN["task"])
        self.assertEqual(_norm(sm.SILING_DECISION_REF),
                         GOLDEN["decision_ref"])
        self.assertEqual(_norm(sm.SILING_MATRIX_STATEMENT),
                         GOLDEN["statement"])
        self.assertEqual(sm.SILING_MONTHS, GOLDEN["months"])
        self.assertEqual(_norm(sm.SILING_SNAPSHOTS), GOLDEN["snapshots"])
        self.assertEqual(_norm(sm.SILING_VERSIONS), GOLDEN["versions"])
        self.assertEqual(_norm(sm.SILING_ABSENT_SOURCES),
                         GOLDEN["absent_sources"])
        self.assertEqual(_norm(sm.SILING_QUOTES), GOLDEN["quotes"])
        self.assertEqual(_norm(sm.SILING_MATRIX), GOLDEN["matrix"])
        self.assertEqual(_norm(sm.SILING_DISSENTS), GOLDEN["dissents"])
        self.assertEqual(_norm(sm.SILING_CALCULATION_CONVENTION),
                         GOLDEN["calculation_convention"])
        self.assertEqual(list(sm.SILING_ADJUDICATION_NOTES),
                         GOLDEN["adjudication_notes"])
        self.assertEqual(list(sm.SILING_LIMITATIONS), GOLDEN["limitations"])

    def test_module_is_pure_data_no_functions(self) -> None:
        """零计算逻辑的结构证明：登记模块内不得有任何函数定义。"""
        functions = [name for name, obj in vars(sm).items()
                     if inspect.isfunction(obj)]
        self.assertEqual(functions, [])


class StructureTest(unittest.TestCase):
    def test_five_versions_and_twelve_months(self) -> None:
        self.assertEqual([v["version_id"] for v in sm.SILING_VERSIONS],
                         VERSION_IDS)
        self.assertEqual(sm.SILING_MONTHS,
                         ["寅", "卯", "辰", "巳", "午", "未",
                          "申", "酉", "戌", "亥", "子", "丑"])
        for version_id in VERSION_IDS:
            self.assertEqual(sorted(sm.SILING_MATRIX[version_id]),
                             sorted(sm.SILING_MONTHS))

    def test_no_two_versions_identical_and_no_unanimous_month(self):
        tables = {vid: {m: _cell_signature(sm.SILING_MATRIX[vid][m])
                        for m in sm.SILING_MONTHS} for vid in VERSION_IDS}
        ids = list(tables)
        for i, left in enumerate(ids):
            for right in ids[i + 1:]:
                self.assertNotEqual(tables[left], tables[right],
                                    f"{left} 与 {right} 全表相同")
        for month in sm.SILING_MONTHS:
            signatures = {tables[vid][month] for vid in VERSION_IDS}
            self.assertGreater(len(signatures), 1,
                               f"{month}月出现了全口径一致")

    def test_quote_records_well_formed(self) -> None:
        ids = [q["id"] for q in sm.SILING_QUOTES]
        self.assertEqual(len(ids), len(set(ids)))
        known_sources = set()
        config = json.loads(
            (ROOT / "config" / "knowledge_sources.json").read_text(
                encoding="utf-8"))
        known_sources = {s["source_id"] for s in config["sources"]}
        for quote in sm.SILING_QUOTES:
            self.assertIn(quote["source_id"], known_sources)
            self.assertGreater(quote["locator"]["char_end"],
                               quote["locator"]["char_start"])
            self.assertGreaterEqual(quote["locator"]["char_start"], 0)
            self.assertTrue(quote["quote"])

    def test_layer_attribution_s024_is_original_note(self) -> None:
        by_id = {q["id"]: q for q in sm.SILING_QUOTES}
        self.assertEqual(by_id["dt.s024_yinyue"]["layer"], "原注")
        self.assertEqual(by_id["dt.s024_yinyue"]["source_section_id"],
                         "bazi.section.s024")
        for quote in sm.SILING_QUOTES:
            if quote["source_id"] == "bazi.source.ditiansui-spouse":
                self.assertIn(quote["layer"], ("原注", "任氏曰"))
            if quote["id"] == "dt.s024_yinyue":
                self.assertNotEqual(quote["layer"], "任氏曰")


class T1T2Test(unittest.TestCase):
    def test_t1_t2_registered_separately(self) -> None:
        t1 = sm.SILING_MATRIX["sanming-t1"]
        t2 = sm.SILING_MATRIX["sanming-t2"]
        differing = [m for m in sm.SILING_MONTHS
                     if _cell_signature(t1[m]) != _cell_signature(t2[m])]
        self.assertEqual(len(differing), 11)
        self.assertEqual(set(sm.SILING_MONTHS) - set(differing), {"巳"})

    def test_t1_sums_all_consistent(self) -> None:
        for month, cell_ in sm.SILING_MATRIX["sanming-t1"].items():
            total = sum(s["days"] for s in cell_["segments"])
            self.assertEqual(total, 30, month)
            self.assertEqual(cell_["recorded_sum"], 30)
            self.assertTrue(cell_["sum_consistent"])

    def test_t2_arithmetic_errors_preserved_verbatim(self) -> None:
        t2 = sm.SILING_MATRIX["sanming-t2"]
        for month, cell_ in t2.items():
            total = sum(s["days"] for s in cell_["segments_as_printed"])
            self.assertEqual(total, cell_["recorded_sum"], month)
        self.assertEqual(t2["酉"]["recorded_sum"], 32)
        self.assertFalse(t2["酉"]["sum_consistent"])
        self.assertTrue(t2["酉"]["inconsistencies"])
        self.assertEqual(t2["子"]["recorded_sum"], 26)
        self.assertFalse(t2["子"]["sum_consistent"])
        self.assertTrue(t2["子"]["inconsistencies"])
        for month, cell_ in t2.items():
            if month not in ("酉", "子"):
                self.assertEqual(cell_["recorded_sum"], 30, month)
                self.assertTrue(cell_["sum_consistent"], month)

    def test_t2_glyph_suspects_kept(self) -> None:
        t2 = sm.SILING_MATRIX["sanming-t2"]
        first = t2["寅"]["segments_as_printed"][0]
        self.assertEqual(first["verbatim_stem"], "已")
        self.assertEqual(first["stem"], "戊")
        self.assertTrue(first["glyph_note"])
        for month in ("未", "申", "丑"):
            suspects = [s for s in t2[month]["segments_as_printed"]
                        if s["verbatim_stem"] == "已"]
            self.assertTrue(suspects, month)
            for segment in suspects:
                self.assertEqual(segment["stem"], "己")


class EvidenceStateTest(unittest.TestCase):
    def test_dissent_recorded(self) -> None:
        dissents = {d["id"]: d for d in sm.SILING_DISSENTS}
        record = dissents["sanming.zuixingzi_anti_daycount"]
        self.assertEqual(record["kind"], "method_dissent")
        self.assertIn("醉醒子", record["holder"])
        self.assertIn("sm.zuixingzi_key", record["quotes"])
        by_id = {q["id"]: q for q in sm.SILING_QUOTES}
        self.assertIn("岂可以几日为限哉", by_id["sm.zuixingzi_key"]["quote"])
        self.assertIn("sanming.yujing_arithmetic", dissents)
        self.assertEqual(
            dissents["sanming.yujing_arithmetic"]["kind"],
            "internal_inconsistency")

    def test_shenfeng_unrecoverable_no_segments(self) -> None:
        for month, cell_ in sm.SILING_MATRIX["shenfeng-diagram"].items():
            self.assertEqual(cell_["status"], "diagram_unrecoverable",
                             month)
            self.assertNotIn("segments", cell_)
            self.assertNotIn("segments_as_printed", cell_)
            self.assertNotIn("parsed_claims", cell_)
        fragments = sm.SILING_MATRIX["shenfeng-diagram"]["戌"]["fragments"]
        self.assertEqual(len(fragments), 1)
        self.assertFalse(fragments[0]["correspondence_verified"])

    def test_qiongtong_absent(self) -> None:
        absent = {a["version_id"]: a for a in sm.SILING_ABSENT_SOURCES}
        record = absent["qiongtong-baojian"]
        self.assertEqual(record["status"], "absent_no_day_table")
        counts = record["evidence"]["search_counts"]
        self.assertEqual(counts["分日"], 0)
        self.assertEqual(counts["用事"], 0)
        self.assertEqual(counts["司令"], 15)
        self.assertEqual(counts["司权"], 14)
        self.assertNotIn("qiongtong-baojian", sm.SILING_MATRIX)


class AdjudicationSweepTest(unittest.TestCase):
    def test_all_cells_conflict_except_authorized_pilot(self) -> None:
        for version_id, months in sm.SILING_MATRIX.items():
            for month, cell_ in months.items():
                self.assertTrue(cell_["research_only"],
                                f"{version_id}/{month}")
                if (version_id, month) == ("ditiansui-yuanshuo", "寅"):
                    self.assertEqual(cell_["adjudication_status"],
                                     "pilot_authorized_ren_branch")
                else:
                    self.assertEqual(cell_["adjudication_status"],
                                     "conflict",
                                     f"{version_id}/{month}")

    def test_statement_not_a_unified_table(self) -> None:
        self.assertFalse(sm.SILING_MATRIX_STATEMENT["is_unified_table"])
        self.assertFalse(
            sm.SILING_MATRIX_STATEMENT["is_authorized_computation_table"])

    def test_no_forbidden_unified_or_default_keys_anywhere(self) -> None:
        for key in _walk_keys(GOLDEN):
            self.assertNotIn(key, FORBIDDEN_KEYS)
            self.assertNotIn("commander", key)


class ConventionTest(unittest.TestCase):
    def test_calculation_convention_registered(self) -> None:
        conv = sm.SILING_CALCULATION_CONVENTION
        self.assertEqual(conv["id"], "siling-calculation-convention")
        self.assertEqual(conv["version"], "v1")
        self.assertEqual(conv["status"], "registered_not_implemented")
        self.assertEqual(conv["scope"]["months"], ["寅"])
        self.assertEqual(conv["scope"]["version_id"], "ditiansui-yuanshuo")
        self.assertEqual(
            [s["interval"] for s in conv["segments"]],
            ["[t0, t0+7*24h)", "[t0+7*24h, t0+14*24h)",
             "[t0+14*24h, next_jie)"])
        self.assertEqual([s["stem"] for s in conv["segments"]],
                         ["戊", "丙", "甲"])
        self.assertIn("连续24小时计日", conv["disclaimer"])
        self.assertIn("不是已证实的传统文献唯一解释", conv["disclaimer"])
        self.assertEqual(len(conv["fail_closed"]), 3)
        self.assertEqual(conv["decision"]["decision"], "C+E")


if __name__ == "__main__":
    unittest.main()
