"""TJ-0424 batch 2 P1 liuyao: xunkong / yuepo minimum-calibre tests.

User adjudication 2026-11-25 Q15/Q16: the approved minimum calibres are
(a) xunkong empty-branch determination + per-line empty flags, covering
all six xun, with NO chukong/tianshi efficacy; (b) yuepo month-break
determination + per-line month-break flags, with proposed Golden B1-B3
verified as real tests and a twelve-month对照, with NO fortune or
yingqi conclusion. Q14 (yuejian/richen) stays definition-only: inputs
are recorded verbatim, nothing is derived.

Two parts:
- Pure-function tests (``XunkongTableTests`` etc.): stdlib + the new
  callable layer only; they run locally with ``PYTHONPATH=src``.
- ``ChartIntegrationTests``: verifies the same expectations through the
  real ``operations.liuyao_chart.chart()`` (which needs the canonical
  tables). These run ONLY in the assembled environment; locally they
  skip with an explicit reason. Run in the worktree with
  ``PYTHONPATH=src python -m unittest
  tests.test_tj0424_liuyao_xunkong_yuepo``.

Real computed examples used below (all verified against the evidence
pack, ~/workspace/tj-core-engine-batch2-liuyao-evidence/):
- qian-static (sealed Golden): day 己丑 -> empty [午, 未]; Qian palace
  najia branches [子, 寅, 辰, 午, 申, 戌] -> only line 4 empty.
- E1 (proposed Golden, 甲戌旬): day 甲戌 -> empty [申, 酉]; same
  branches -> line 5 (申) empty, line 6 (戌) not empty.
- E2 (proposed Golden): chart([9,7,7,7,7,7], 甲子, 午) -> line 6
  (壬戌) empty.
- B1 (proposed Golden): chart([7]*6, 己丑, 午) -> line 1 (甲子)
  month-broken, other five lines not.
- B2 (proposed Golden): chart([9,7,7,7,7,7], 甲子, 午) -> line 1
  (甲子) month-broken.
- B3 (proposed Golden): chart([7]*6, 甲子, 午) -> line 4 (壬午,
  branch equals the month branch) NOT month-broken.
"""
import unittest
from pathlib import Path

from tianji_kb.foundations import CYCLE
from tianji_kb.liuyao_empty_break import (
    CALIBRE,
    GAPS,
    MONTH_BRANCH_BY_LUNAR_MONTH,
    MONTH_BREAK_BY_LUNAR_MONTH,
    XUN_TABLE,
    broken_branch_for_month,
    empty_branches_for_day,
    empty_flags_for_day,
    line_empty_flags,
    month_break_flags,
    xun_head_for_day,
)
from tianji_kb.liuyao_yongshen import (
    USEFUL_GOD_MAPPINGS,
    YUEJIAN_RICHEN_DEFINITIONS,
    assess,
    record_month_day_context,
)
from tianji_kb.operations.liuyao import branch_relation, xunkong

ROOT = Path(__file__).resolve().parents[1]
DATA_PRESENT = (
    (ROOT / "data/canonical/liuyao/najia_v1.json").exists()
    and (ROOT / "data/canonical/seed.json").exists()
)

# Qian palace najia branches, bottom to top, for a static Qian cast
# ([7]*6): 甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌. Line 1 甲子 and line 4
# 壬午 are the branches named in proposed Golden B1-B3; line 4 壬午 is
# the branch named in sealed Golden qian-static.
QIAN_BRANCHES = ["子", "寅", "辰", "午", "申", "戌"]


class XunkongTableTests(unittest.TestCase):
    def test_all_six_xun_heads_have_exact_empty_branches(self):
        self.assertEqual(
            XUN_TABLE,
            {
                "甲子": ("戌", "亥"),
                "甲戌": ("申", "酉"),
                "甲申": ("午", "未"),
                "甲午": ("辰", "巳"),
                "甲辰": ("寅", "卯"),
                "甲寅": ("子", "丑"),
            },
        )
        self.assertEqual(len(XUN_TABLE), 6)

    def test_xun_head_for_day_spots_each_xun(self):
        cases = {
            "甲子": "甲子",
            "癸酉": "甲子",
            "甲戌": "甲戌",
            "癸未": "甲戌",
            "甲申": "甲申",
            "癸巳": "甲申",
            "甲午": "甲午",
            "癸卯": "甲午",
            "甲辰": "甲辰",
            "癸丑": "甲辰",
            "甲寅": "甲寅",
            "癸亥": "甲寅",
            "己丑": "甲申",
        }
        for day, head in cases.items():
            with self.subTest(day=day):
                self.assertEqual(xun_head_for_day(day), head)

    def test_empty_branches_for_day_matches_xun_table_for_all_sixty_days(self):
        # Lock test: the reusable xunkong() computation agrees with the
        # six-xun table for every day of the sixty-cycle (10 days each).
        for day in CYCLE:
            with self.subTest(day=day):
                self.assertEqual(
                    tuple(empty_branches_for_day(day)),
                    XUN_TABLE[xun_head_for_day(day)],
                )
                self.assertEqual(
                    empty_branches_for_day(day), list(xunkong(day))
                )

    def test_empty_branches_real_examples(self):
        self.assertEqual(empty_branches_for_day("甲子"), ["戌", "亥"])
        self.assertEqual(empty_branches_for_day("己丑"), ["午", "未"])
        self.assertEqual(empty_branches_for_day("甲戌"), ["申", "酉"])
        self.assertEqual(empty_branches_for_day("癸亥"), ["子", "丑"])

    def test_empty_branches_reject_invalid_day(self):
        for bad in ["甲丑", "甲子午", "", "子", None, 60, "甲子 "]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    empty_branches_for_day(bad)
                with self.assertRaises(ValueError):
                    xun_head_for_day(bad)


class LineEmptyFlagTests(unittest.TestCase):
    def test_qian_static_sealed_golden_empty_flags(self):
        # Sealed Golden qian-static: day 己丑, empty [午, 未], line 4 empty.
        flags = empty_flags_for_day(QIAN_BRANCHES, "己丑")
        self.assertEqual(flags, [False, False, False, True, False, False])
        self.assertEqual(
            [i + 1 for i, f in enumerate(flags) if f], [4]
        )

    def test_proposed_golden_e1_jiaxu_xun(self):
        # E1: day 甲戌, empty [申, 酉]; line 5 (申) empty, line 6 (戌) not.
        flags = empty_flags_for_day(QIAN_BRANCHES, "甲戌")
        self.assertEqual(flags, [False, False, False, False, True, False])

    def test_empty_mark_falls_on_line_branch_not_day_or_month_branch(self):
        # Counter-proof (evidence pack 03 §3.3): the day branch itself
        # being an empty branch does not make any line empty. Day 癸亥
        # sits in the 甲寅旬 (empty 子/丑) yet no line here is 子/丑.
        flags = empty_flags_for_day(
            ["寅", "卯", "辰", "巳", "午", "未"], "癸亥"
        )
        self.assertEqual(flags, [False] * 6)
        # And a line branch equal to the DAY branch is not empty by that.
        flags = line_empty_flags(
            ["子", "丑", "寅", "卯", "辰", "巳"], ["戌", "亥"]
        )
        self.assertEqual(flags, [False] * 6)

    def test_line_empty_flags_reject_malformed_input(self):
        with self.assertRaises(ValueError):
            line_empty_flags(["子"] * 5, ["戌", "亥"])
        with self.assertRaises(ValueError):
            line_empty_flags(["子"] * 6, ["戌"])
        with self.assertRaises(ValueError):
            line_empty_flags(["子"] * 5 + ["午子"], ["戌", "亥"])
        with self.assertRaises(ValueError):
            line_empty_flags(QIAN_BRANCHES, ["戌", "亥", "子"])


class MonthBreakTests(unittest.TestCase):
    def test_broken_branch_for_all_twelve_month_branches(self):
        expected = {
            "子": "午",
            "丑": "未",
            "寅": "申",
            "卯": "酉",
            "辰": "戌",
            "巳": "亥",
            "午": "子",
            "未": "丑",
            "申": "寅",
            "酉": "卯",
            "戌": "辰",
            "亥": "巳",
        }
        for month, broken in expected.items():
            with self.subTest(month=month):
                self.assertEqual(broken_branch_for_month(month), broken)

    def test_broken_branch_agrees_with_branch_relation_clash(self):
        # Cross-check against the existing r006 six-clash callable:
        # exactly the clash partner is broken, and no other branch is.
        branches = ["子", "丑", "寅", "卯", "辰", "巳",
                    "午", "未", "申", "酉", "戌", "亥"]
        for month in branches:
            with self.subTest(month=month):
                clashers = [b for b in branches
                            if branch_relation(b, month)["clash"]]
                self.assertEqual(clashers, [broken_branch_for_month(month)])

    def test_twelve_lunar_month_table_matches_six_clash_month_by_month(self):
        # 12-month对照 (zs05): 正月申 ... 十二月未. Each lunar month's
        # month branch (正月建寅 ... 十二月建丑) must break exactly the
        # branch the zs05 table names -- 12/12, no exception.
        self.assertEqual(len(MONTH_BREAK_BY_LUNAR_MONTH), 12)
        self.assertEqual(len(MONTH_BRANCH_BY_LUNAR_MONTH), 12)
        for lunar_month in range(1, 13):
            with self.subTest(lunar_month=lunar_month):
                self.assertEqual(
                    broken_branch_for_month(
                        MONTH_BRANCH_BY_LUNAR_MONTH[lunar_month]
                    ),
                    MONTH_BREAK_BY_LUNAR_MONTH[lunar_month],
                )

    def test_proposed_golden_b1_month_break_flags(self):
        # B1: 午月, Qian branches -> only line 1 (甲子, 子冲午) broken.
        flags = month_break_flags(QIAN_BRANCHES, "午")
        self.assertEqual(flags, [True, False, False, False, False, False])
        self.assertEqual([i + 1 for i, f in enumerate(flags) if f], [1])

    def test_proposed_golden_b3_same_branch_is_not_broken(self):
        # B3: line 4 (壬午) has the branch equal to the month branch 午:
        # same branch is not a clash, so it is NOT month-broken.
        flags = month_break_flags(QIAN_BRANCHES, "午")
        self.assertFalse(flags[3])

    def test_break_direction_follows_the_month_not_the_pair(self):
        # Counter-proof (evidence pack 04 §3.1): the same clash pair
        # (子午) breaks different lines as the month changes. 午月 breaks
        # 子 lines; 子月 breaks 午 lines, never 子 lines.
        self.assertEqual(
            month_break_flags(QIAN_BRANCHES, "子"),
            [False, False, False, True, False, False],
        )
        self.assertEqual(
            month_break_flags(QIAN_BRANCHES, "午"),
            [True, False, False, False, False, False],
        )

    def test_month_break_flags_reject_malformed_input(self):
        with self.assertRaises(ValueError):
            month_break_flags(["子"] * 5, "午")
        with self.assertRaises(ValueError):
            month_break_flags(QIAN_BRANCHES, "午子")
        with self.assertRaises(ValueError):
            broken_branch_for_month("甲子")


class NoFortuneOrYingqiTests(unittest.TestCase):
    def test_calibre_is_research_only_not_public_not_ai(self):
        self.assertTrue(CALIBRE["research_only"])
        self.assertFalse(CALIBRE["public"])
        self.assertFalse(CALIBRE["ai"])
        self.assertEqual(
            CALIBRE["does_not_compute"],
            (
                "chukong_or_tianshi_efficacy",
                "yuepo_fortune_or_severity",
                "yuepo_moving_vs_static",
                "yuepo_unbreaking",
                "yingqi",
                "ripo",
                "yongshen",
            ),
        )

    def test_gaps_record_what_is_still_missing(self):
        for key in (
            "chukong_tianshi",
            "other_five_xun_rows_unregistered",
            "yuepo_moving_static_and_unbreaking",
            "yuepo_sealed_golden_positive",
            "yuejian_richen_mappings",
            "yongshen_yuanshen_jishen_choushen_yingqi",
            "ripo_not_parallel",
        ):
            self.assertIn(key, GAPS)
            self.assertTrue(GAPS[key])

    def test_yongshen_registry_still_empty_and_assess_still_abstains(self):
        self.assertEqual(USEFUL_GOD_MAPPINGS, {})
        result = assess({
            "question_type": "career",
            "yao_values": [7, 7, 7, 7, 7, 7],
            "value": "2026-11-25T12:00:00+08:00",
        })
        self.assertEqual(result["status"], "abstained")
        self.assertIsNone(result["verdict"])
        self.assertIsNone(result["useful_god"])


class YuejianRichenRecordTests(unittest.TestCase):
    def test_definitions_are_registered_and_mapping_free(self):
        self.assertEqual(
            set(YUEJIAN_RICHEN_DEFINITIONS), {"yuejian", "richen"}
        )
        for key, record in YUEJIAN_RICHEN_DEFINITIONS.items():
            with self.subTest(key=key):
                self.assertEqual(record["status"], "definition_only")
                self.assertIsNone(record["mapping"])
                self.assertTrue(record["definition"])

    def test_record_returns_inputs_verbatim_with_no_conclusions(self):
        # Proposed Golden M1: only {month_branch: 寅} is recorded.
        record = record_month_day_context("寅", "甲子")
        self.assertEqual(record["month_branch"], "寅")
        self.assertEqual(record["day_ganzhi"], "甲子")
        self.assertIsNone(record["derived_conclusions"])
        self.assertNotIn("wangshuai", str(record))
        self.assertNotIn("yongshen", str(record))

    def test_changing_month_branch_changes_only_the_recorded_field(self):
        # Proposed Golden M2: with month 申 instead of 寅, no line fact
        # appears or changes -- the record differs only in month_branch.
        first = record_month_day_context("寅", "甲子")
        second = record_month_day_context("申", "甲子")
        self.assertEqual(first["day_ganzhi"], second["day_ganzhi"])
        self.assertEqual(first["yuejian"], second["yuejian"])
        self.assertEqual(first["richen"], second["richen"])
        self.assertEqual(first["derived_conclusions"],
                         second["derived_conclusions"])
        self.assertNotEqual(first["month_branch"], second["month_branch"])

    def test_record_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            record_month_day_context("寅午", "甲子")
        with self.assertRaises(ValueError):
            record_month_day_context("寅", "甲丑")
        with self.assertRaises(ValueError):
            record_month_day_context("寅", "甲子 ")


@unittest.skipUnless(DATA_PRESENT, "needs assembled runtime with data/canonical")
class ChartIntegrationTests(unittest.TestCase):
    """Same expectations through the real chart() (machine only)."""

    def test_b1_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "己丑", "午")["result"]
        self.assertEqual(result["empty_branches"], ["午", "未"])
        self.assertEqual(
            [line["month_break"] for line in result["lines"]],
            [True, False, False, False, False, False],
        )
        self.assertEqual(
            [line["position"] for line in result["lines"]
             if line["month_break"]],
            [1],
        )

    def test_b2_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([9, 7, 7, 7, 7, 7], "甲子", "午")["result"]
        self.assertTrue(result["lines"][0]["month_break"])
        self.assertEqual(result["lines"][0]["najia"], "甲子")

    def test_b3_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "甲子", "午")["result"]
        self.assertEqual(result["lines"][3]["najia"], "壬午")
        self.assertFalse(result["lines"][3]["month_break"])

    def test_e1_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "甲戌", "午")["result"]
        self.assertEqual(result["empty_branches"], ["申", "酉"])
        self.assertTrue(result["lines"][4]["empty"])
        self.assertFalse(result["lines"][5]["empty"])

    def test_e2_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([9, 7, 7, 7, 7, 7], "甲子", "午")["result"]
        self.assertEqual(result["empty_branches"], ["戌", "亥"])
        self.assertEqual(result["lines"][5]["najia"], "壬戌")
        self.assertTrue(result["lines"][5]["empty"])

    def test_qian_static_sealed_golden_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "己丑", "酉")["result"]
        self.assertEqual(result["empty_branches"], ["午", "未"])
        self.assertTrue(result["lines"][3]["empty"])
        self.assertEqual(
            [line["month_break"] for line in result["lines"]],
            [False] * 6,
        )

    def test_chart_flags_agree_with_callable_layer(self):
        from tianji_kb.operations.liuyao_chart import chart

        for yao_values, day, month in (
            ([7] * 6, "己丑", "午"),
            ([9, 7, 7, 7, 7, 7], "甲子", "午"),
            ([7] * 6, "甲戌", "午"),
            ([9, 7, 7, 8, 8, 8], "甲子", "子"),
        ):
            with self.subTest(yao_values=yao_values, day=day, month=month):
                result = chart(list(yao_values), day, month)["result"]
                branches = [line["najia"][1] for line in result["lines"]]
                self.assertEqual(
                    [line["empty"] for line in result["lines"]],
                    empty_flags_for_day(branches, day),
                )
                self.assertEqual(
                    [line["month_break"] for line in result["lines"]],
                    month_break_flags(branches, month),
                )
                self.assertEqual(
                    result["empty_branches"],
                    empty_branches_for_day(day),
                )


if __name__ == "__main__":
    unittest.main()
