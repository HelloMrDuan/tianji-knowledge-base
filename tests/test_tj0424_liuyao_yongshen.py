"""TJ-0424 batch 3 (4th lane): liuyao yongshen framework + wangshuai facts.

User direction: build ONLY what no adjudication blocks. Round-2 L1-L5
were DECIDED by the user 2026-11-25, lifting the blocks as follows:
L2 approves the sixty-cycle xunkong derivation; L4 approves yuejian /
richen structure rules (efficacy stays separate and abstains); L5
approves the conditional ripo rule; L3 approves evidence construction
for chukong / tianshi / un-breaking (no basis found, nothing
implemented); L1 approves sealed-Golden admission (sealed-governance
step, not executed in the public repo).

- Useful-god framework STRUCTURE (question type -> six-relative role
  -> candidate lines) with every slot's evidence status explicit.
  USEFUL_GOD_MAPPINGS stays EMPTY and assess() still abstains for all
  8 types -- the framework must never be reported as implemented
  useful-god selection.
- Wangshuai STRUCTURAL FACTS: per-line element vs month-branch and
  day-branch element relations (生克比和), enumerated as facts only.
  No 旺衰 verdict, no 吉凶: ``conclusion`` / ``wangshuai`` /
  ``verdict`` are always None. Yuejian/richen stay definition-only
  (L4: 四時旺相 chapter unregistered, xing/hai/earth disputes
  unadjudicated; no per-item evidence gathering is started).
- The other five xun rows: an explicit cycle-derivation provenance
  table (L2 pending) -- exactly one row registered, five rows labelled
  "循环派生、未逐条登记", never presented as registered.
- Explicitly NOT implemented (L3/L5/L1): chukong / tianshi,
  yuepo un-breaking, ripo r020 (never derived from yuepo), sealed
  Golden admission of proposed B1-B3/E1/E2.

Two parts, following test_tj0424_liuyao_xunkong_yuepo.py:
- Pure-function tests: stdlib + the new callable layer only; they run
  locally with ``PYTHONPATH=src``.
- ``ChartIntegrationTests``: the same expectations through the real
  ``operations.liuyao_chart.chart()`` plus locks against the canonical
  tables. These run ONLY in the assembled environment; locally they
  skip with an explicit reason.
"""
import unittest
from pathlib import Path

import tianji_kb.liuyao_yongshen as yongshen
from tianji_kb.foundations import CYCLE
from tianji_kb.liuyao_empty_break import (
    XUN_TABLE,
    XUN_TABLE_PROVENANCE,
    xun_table_with_provenance,
)
from tianji_kb.liuyao_yongshen import (
    BRANCH_ELEMENTS,
    MAPPING_SLOT_SCHEMA,
    OUT_OF_SCOPE,
    RELATIVE_ROLE_DEFINITIONS,
    SISH_WANGXIANG_EVIDENCE,
    SIX_RELATIVE_ROLES,
    USEFUL_GOD_MAPPINGS,
    WANGSHUAI_EFFICACY_CONDITIONS,
    assess,
    assess_wangshuai,
    element_of_branch,
    element_relation_between,
    framework_status,
    line_month_day_structure,
    line_relations_to_month_day,
    line_roles_relative_to_element,
    list_mapping_slots,
    mapping_slot,
    month_day_structure,
    roles_for_element,
)
from tianji_kb.operations.liuyao import xunkong

ROOT = Path(__file__).resolve().parents[1]
DATA_PRESENT = (
    (ROOT / "data/canonical/liuyao/najia_v1.json").exists()
    and (ROOT / "data/canonical/seed.json").exists()
)

# Qian palace najia branches, bottom to top, for a static Qian cast
# ([7]*6): 甲子, 甲寅, 甲辰, 壬午, 壬申, 壬戌.
QIAN_BRANCHES = ["子", "寅", "辰", "午", "申", "戌"]

# Independent re-derivation of the five-element relations, written
# from the element cycles directly (not by calling the module under
# test): 同我 / 我生 / 生我 / 我克 / 克我.
_TEST_GENERATES = dict(zip("木火土金水", "火土金水木"))
_TEST_CONTROLS = dict(zip("木火土金水", "土金水木火"))
_TEST_BRANCH_ELEMENTS = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}


def _expected_relation(line_element, reference_element):
    if line_element == reference_element:
        return "同我"
    if _TEST_GENERATES[line_element] == reference_element:
        return "我生"
    if _TEST_GENERATES[reference_element] == line_element:
        return "生我"
    if _TEST_CONTROLS[line_element] == reference_element:
        return "我克"
    return "克我"


class MappingFrameworkTests(unittest.TestCase):
    def test_slot_schema_declares_the_full_future_shape(self):
        self.assertEqual(
            set(MAPPING_SLOT_SCHEMA),
            {"question_type", "relative_role", "candidate_lines",
             "evidence", "approval"},
        )
        self.assertEqual(
            set(MAPPING_SLOT_SCHEMA["evidence"]),
            {"source", "version", "locator", "classical_citation", "status"},
        )
        self.assertEqual(
            set(MAPPING_SLOT_SCHEMA["approval"]),
            {"approved_by", "adjudication_ref"},
        )

    def test_six_relative_roles_are_the_chart_roles_only(self):
        self.assertEqual(
            SIX_RELATIVE_ROLES, ("父母", "兄弟", "子孙", "妻财", "官鬼")
        )

    def test_all_eight_slots_are_empty_with_explicit_evidence_status(self):
        slots = list_mapping_slots()
        self.assertEqual(len(slots), 8)
        for slot in slots:
            with self.subTest(question_type=slot["question_type"]):
                self.assertIsNone(slot["relative_role"])
                self.assertIsNone(slot["candidate_lines"])
                self.assertIsNone(slot["mapping"])
                self.assertEqual(
                    slot["evidence_status"], "no_approved_mapping"
                )
                self.assertEqual(
                    slot["evidence"]["status"], "framework_only"
                )
                self.assertIsNone(
                    slot["evidence"]["classical_citation"]
                )
                self.assertIn("L1-L5", slot["adjudication"])

    def test_mapping_slot_rejects_unknown_type(self):
        with self.assertRaises(ValueError):
            mapping_slot("not_a_type")
        with self.assertRaises(ValueError):
            mapping_slot(None)

    def test_slots_are_copies_not_live_references(self):
        slot = mapping_slot("career")
        slot["evidence"]["status"] = "tampered"
        self.assertEqual(
            mapping_slot("career")["evidence"]["status"], "framework_only"
        )

    def test_framework_status_counts_only_what_exists(self):
        status = framework_status()
        self.assertEqual(status["question_types"], 8)
        self.assertEqual(status["types_with_approved_grouping"], 0)
        self.assertEqual(status["approved_mappings"], 0)
        self.assertTrue(status["mapping_registry_empty"])
        self.assertEqual(status["assess_behavior"], "always_abstains")
        self.assertTrue(status["research_only"])
        self.assertFalse(status["public"])
        self.assertFalse(status["ai"])
        self.assertEqual(
            status["pending_adjudications"],
            ("per-item mapping approval",),
        )
        self.assertEqual(
            status["decided_adjudications"],
            ("L1", "L2", "L3", "L4", "L5"),
        )

    def test_registry_still_empty_and_assess_still_abstains_for_all_types(self):
        self.assertEqual(USEFUL_GOD_MAPPINGS, {})
        for slot in list_mapping_slots():
            with self.subTest(question_type=slot["question_type"]):
                result = assess({
                    "question_type": slot["question_type"],
                    "yao_values": [7, 7, 7, 7, 7, 7],
                    "value": "2026-11-25T12:00:00+08:00",
                })
                self.assertEqual(result["status"], "abstained")
                self.assertIsNone(result["verdict"])
                self.assertIsNone(result["useful_god"])


class OutOfScopeTests(unittest.TestCase):
    def test_out_of_scope_records_every_gated_item_as_unimplemented(self):
        self.assertEqual(
            set(OUT_OF_SCOPE),
            {
                "chukong_tianshi",
                "yuepo_unbreaking",
                "ripo",
                "yuejian_richen_executable_mapping",
                "yongshen_yuanshen_jishen_choushen_yingqi",
                "sealed_golden_admission_b1_b2_b3_e1_e2",
            },
        )
        expected_adjudications = {
            "chukong_tianshi": "L3 \u2014 decided 2026-11-25",
            "yuepo_unbreaking": "L3 \u2014 decided 2026-11-25",
            "ripo": "L5 \u2014 decided 2026-11-25",
            "yuejian_richen_executable_mapping": "L4 (Q14) \u2014 decided 2026-11-25",
            "yongshen_yuanshen_jishen_choushen_yingqi": "per-item approval; L4/L5 decided 2026-11-25",
            "sealed_golden_admission_b1_b2_b3_e1_e2": "L1 \u2014 decided 2026-11-25",
        }
        for key, record in OUT_OF_SCOPE.items():
            with self.subTest(key=key):
                self.assertFalse(record["implemented"])
                self.assertEqual(
                    record["adjudication"], expected_adjudications[key]
                )
                self.assertTrue(record["reason"])

    def test_ripo_is_not_parallel_to_yuepo(self):
        reason = OUT_OF_SCOPE["ripo"]["reason"]
        self.assertIn("衰而靜", reason)
        self.assertIn("NOT parallel", reason)
        self.assertEqual(OUT_OF_SCOPE["ripo"]["rule"], "liuyao.rule.r020")
        # Stage 2 (L5): the conditional rule lives in liuyao_empty_break.
        self.assertEqual(
            OUT_OF_SCOPE["ripo"]["conditional_rule"],
            "tianji_kb.liuyao_empty_break.day_break_assessment",
        )

    def test_no_callable_for_any_out_of_scope_item_exists(self):
        # No function/attribute in the module implements chukong,
        # tianshi, ripo/day-break, yingqi, or un-breaking.
        names = {name.lower() for name in dir(yongshen)}
        for forbidden in ("chukong", "tianshi", "ripo", "yingqi",
                          "unbreak", "day_break"):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(
                    any(forbidden in name for name in names),
                    "module must not define %r" % forbidden,
                )


class LineElementRelationTests(unittest.TestCase):
    def test_branch_element_table_is_the_twelve_branches(self):
        self.assertEqual(BRANCH_ELEMENTS, _TEST_BRANCH_ELEMENTS)
        self.assertEqual(len(BRANCH_ELEMENTS), 12)

    def test_element_of_branch_rejects_non_branch(self):
        for bad in ["甲子", "子丑", "", None, 12]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    element_of_branch(bad)

    def test_element_relation_between_covers_all_five_kinds(self):
        # One example per relation kind, read from the line's side.
        cases = [
            ("午", "巳", "同我"),   # 火 vs 火
            ("寅", "午", "我生"),   # 木生火
            ("午", "寅", "生我"),   # 木生火，火被生
            ("子", "巳", "我克"),   # 水克火
            ("巳", "子", "克我"),   # 水克火，火被克
        ]
        for line_branch, ref_branch, expected in cases:
            with self.subTest(
                line_branch=line_branch, ref_branch=ref_branch
            ):
                fact = element_relation_between(line_branch, ref_branch)
                self.assertEqual(fact["relation"], expected)
                self.assertEqual(
                    fact["line_element"],
                    _TEST_BRANCH_ELEMENTS[line_branch],
                )
                self.assertEqual(
                    fact["reference_element"],
                    _TEST_BRANCH_ELEMENTS[ref_branch],
                )

    def test_relation_is_directional_not_symmetric(self):
        # 生/克 flip when the two branches swap; 同我 does not.
        self.assertEqual(
            element_relation_between("寅", "午")["relation"], "我生"
        )
        self.assertEqual(
            element_relation_between("午", "寅")["relation"], "生我"
        )
        self.assertEqual(
            element_relation_between("子", "巳")["relation"], "我克"
        )
        self.assertEqual(
            element_relation_between("巳", "子")["relation"], "克我"
        )

    def test_full_twelve_by_twelve_relation_matrix(self):
        # Lock: every line-branch x reference-branch pair (144) gives
        # the relation derived independently from the element cycles.
        branches = list(_TEST_BRANCH_ELEMENTS)
        for line_branch in branches:
            for ref_branch in branches:
                with self.subTest(
                    line_branch=line_branch, ref_branch=ref_branch
                ):
                    expected = _expected_relation(
                        _TEST_BRANCH_ELEMENTS[line_branch],
                        _TEST_BRANCH_ELEMENTS[ref_branch],
                    )
                    self.assertEqual(
                        element_relation_between(
                            line_branch, ref_branch
                        )["relation"],
                        expected,
                    )

    def test_qian_lines_to_month_and_day_are_facts_not_verdicts(self):
        # Real example: Qian branches, month 午 (fire), day 己丑
        # (day branch 丑, earth). Relations computed by hand:
        # month 火: 子水我克, 寅木我生, 辰土生我, 午火同我,
        #           申金克我, 戌土生我.
        # day 丑土: 子水克我, 寅木我克, 辰土同我, 午火我生,
        #           申金生我, 戌土同我.
        result = line_relations_to_month_day(QIAN_BRANCHES, "午", "己丑")
        self.assertEqual(result["line_branches"], QIAN_BRANCHES)
        self.assertEqual(result["month_branch"], "午")
        self.assertEqual(result["day_branch"], "丑")
        self.assertEqual(result["day_ganzhi"], "己丑")
        self.assertEqual(
            [line["relation_to_month"] for line in result["lines"]],
            ["我克", "我生", "生我", "同我", "克我", "生我"],
        )
        self.assertEqual(
            [line["relation_to_day"] for line in result["lines"]],
            ["克我", "我克", "同我", "我生", "生我", "同我"],
        )
        self.assertEqual(
            [line["position"] for line in result["lines"]],
            [1, 2, 3, 4, 5, 6],
        )
        self.assertEqual(
            [line["line_element"] for line in result["lines"]],
            ["水", "木", "土", "火", "金", "土"],
        )
        # No verdict of any kind.
        self.assertIsNone(result["conclusion"])
        self.assertIsNone(result["wangshuai"])
        self.assertIsNone(result["verdict"])
        for line in result["lines"]:
            self.assertNotIn("verdict", line)
            self.assertNotIn("wangshuai", line)

    def test_month_and_day_relations_are_independent(self):
        # Counter-proof (cf. M2): changing the month branch changes
        # only relation_to_month; changing the day changes only
        # relation_to_day.
        base = line_relations_to_month_day(QIAN_BRANCHES, "午", "己丑")
        other_month = line_relations_to_month_day(
            QIAN_BRANCHES, "子", "己丑"
        )
        self.assertEqual(
            [line["relation_to_day"] for line in base["lines"]],
            [line["relation_to_day"] for line in other_month["lines"]],
        )
        self.assertNotEqual(
            [line["relation_to_month"] for line in base["lines"]],
            [line["relation_to_month"] for line in other_month["lines"]],
        )
        other_day = line_relations_to_month_day(
            QIAN_BRANCHES, "午", "甲子"
        )
        self.assertEqual(
            [line["relation_to_month"] for line in base["lines"]],
            [line["relation_to_month"] for line in other_day["lines"]],
        )
        self.assertNotEqual(
            [line["relation_to_day"] for line in base["lines"]],
            [line["relation_to_day"] for line in other_day["lines"]],
        )

    def test_line_relations_reject_malformed_input(self):
        with self.assertRaises(ValueError):
            line_relations_to_month_day(["子"] * 5, "午", "己丑")
        with self.assertRaises(ValueError):
            line_relations_to_month_day(QIAN_BRANCHES, "午子", "己丑")
        with self.assertRaises(ValueError):
            line_relations_to_month_day(QIAN_BRANCHES, "午", "甲丑")
        with self.assertRaises(ValueError):
            line_relations_to_month_day(
                QIAN_BRANCHES + ["子"], "午", "己丑"
            )


class XunProvenanceTests(unittest.TestCase):
    def test_provenance_table_matches_xun_table_exactly(self):
        self.assertEqual(set(XUN_TABLE_PROVENANCE), set(XUN_TABLE))
        for head, row in XUN_TABLE_PROVENANCE.items():
            with self.subTest(xun_head=head):
                self.assertEqual(row["xun_head"], head)
                self.assertEqual(row["empty_branches"], XUN_TABLE[head])

    def test_exactly_one_row_is_registered_five_are_derivations(self):
        registered = [
            head
            for head, row in XUN_TABLE_PROVENANCE.items()
            if row["registration"] == "registered_per_row"
        ]
        derived = [
            head
            for head, row in XUN_TABLE_PROVENANCE.items()
            if row["registration"] == "unregistered_per_row"
        ]
        self.assertEqual(registered, ["甲子"])
        self.assertEqual(
            derived, ["甲戌", "甲申", "甲午", "甲辰", "甲寅"]
        )
        for head in derived:
            with self.subTest(xun_head=head):
                row = XUN_TABLE_PROVENANCE[head]
                self.assertEqual(
                    row["derivation"], "sixty_cycle_derivation"
                )
                self.assertIn("循环派生、未逐条登记", row["note"])
                self.assertIn("L2", row["note"])

    def test_registered_row_carries_both_sources(self):
        row = XUN_TABLE_PROVENANCE["甲子"]
        self.assertIn("liuyao.section.s019", row["evidence"])
        self.assertIn("liuyao.evidence.phase2.zs04", row["evidence"])
        self.assertIn("13706,13731", row["evidence"])
        self.assertIn("29389,29434", row["evidence"])

    def test_derived_rows_never_quote_the_unregistered_lines(self):
        # The 卜筮正宗 lines 373-374 table is located by line number
        # only; its text is not quoted anywhere in the provenance.
        for head in ("甲戌", "甲申", "甲午", "甲辰", "甲寅"):
            with self.subTest(xun_head=head):
                row = XUN_TABLE_PROVENANCE[head]
                self.assertIn("373-374", row["evidence"])
                self.assertIn("未逐条登记", row["evidence"])

    def test_provenance_values_agree_with_cycle_for_all_sixty_days(self):
        for day in CYCLE:
            with self.subTest(day=day):
                # xun head is the jia day starting the day's ten-day xun.
                index = CYCLE.index(day)
                head = CYCLE[index // 10 * 10]
                self.assertEqual(
                    tuple(xunkong(day)),
                    XUN_TABLE_PROVENANCE[head]["empty_branches"],
                )

    def test_provenance_table_is_a_copy(self):
        table = xun_table_with_provenance()
        table["甲子"]["empty_branches"] = ("子", "丑")
        self.assertEqual(
            XUN_TABLE_PROVENANCE["甲子"]["empty_branches"], ("戌", "亥")
        )


@unittest.skipUnless(DATA_PRESENT, "needs assembled runtime with data/canonical")
class ChartIntegrationTests(unittest.TestCase):
    """Same expectations through the real chart() + canonical locks."""

    def test_branch_elements_match_canonical_seed(self):
        from tianji_kb.foundations import branch_element

        for branch, element in BRANCH_ELEMENTS.items():
            with self.subTest(branch=branch):
                self.assertEqual(branch_element(branch), element)

    def test_relations_agree_with_operations_element_relation(self):
        from tianji_kb.operations.liuyao import element_relation

        branch_for_element = {
            "水": "子", "土": "丑", "木": "寅", "火": "午", "金": "申",
        }
        for line_element in "木火土金水":
            for ref_element in "木火土金水":
                with self.subTest(
                    line_element=line_element, ref_element=ref_element
                ):
                    self.assertEqual(
                        element_relation_between(
                            branch_for_element[line_element],
                            branch_for_element[ref_element],
                        )["relation"],
                        element_relation(line_element, ref_element),
                    )

    def test_chart_branches_feed_line_relations_b1_case(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "己丑", "午")["result"]
        branches = [line["najia"][1] for line in result["lines"]]
        self.assertEqual(branches, QIAN_BRANCHES)
        facts = line_relations_to_month_day(branches, "午", "己丑")
        self.assertEqual(
            [line["relation_to_month"] for line in facts["lines"]],
            ["我克", "我生", "生我", "同我", "克我", "生我"],
        )
        self.assertEqual(
            [line["relation_to_day"] for line in facts["lines"]],
            ["克我", "我克", "同我", "我生", "生我", "同我"],
        )
        self.assertIsNone(facts["wangshuai"])
        self.assertIsNone(facts["verdict"])

    def test_chart_branches_feed_line_relations_e1_case(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart([7] * 6, "甲戌", "午")["result"]
        branches = [line["najia"][1] for line in result["lines"]]
        facts = line_relations_to_month_day(branches, "午", "甲戌")
        # Day branch 戌 (earth): 子水克我, 寅木我克, 辰土同我,
        # 午火我生, 申金生我, 戌土同我.
        self.assertEqual(
            [line["relation_to_day"] for line in facts["lines"]],
            ["克我", "我克", "同我", "我生", "生我", "同我"],
        )
        self.assertEqual(
            [line["relation_to_month"] for line in facts["lines"]],
            ["我克", "我生", "生我", "同我", "克我", "生我"],
        )


if __name__ == "__main__":
    unittest.main()


class MonthDayStructureTests(unittest.TestCase):
    """L4 DECIDED: yuejian/richen STRUCTURE rules (not efficacy)."""

    def test_month_element_covers_all_twelve_branches(self):
        expected = {
            "寅": "木", "卯": "木", "巳": "火", "午": "火",
            "申": "金", "酉": "金", "亥": "水", "子": "水",
            "辰": "土", "戌": "土", "丑": "土", "未": "土",
        }
        for branch, element in expected.items():
            with self.subTest(month_branch=branch):
                ctx = month_day_structure(branch, "甲子")
                self.assertEqual(ctx["month_element"], element)
                self.assertIsNone(ctx["wangshuai"])
                self.assertIsNone(ctx["verdict"])

    def test_day_stem_and_branch_elements(self):
        cases = [
            ("甲子", "甲", "木", "子", "水"),
            ("己丑", "己", "土", "丑", "土"),
            ("丙午", "丙", "火", "午", "火"),
            ("辛酉", "辛", "金", "酉", "金"),
            ("癸亥", "癸", "水", "亥", "水"),
        ]
        for day, stem, stem_el, branch, branch_el in cases:
            with self.subTest(day=day):
                ctx = month_day_structure("午", day)
                self.assertEqual(ctx["day_stem"], stem)
                self.assertEqual(ctx["day_stem_element"], stem_el)
                self.assertEqual(ctx["day_branch"], branch)
                self.assertEqual(ctx["day_branch_element"], branch_el)
                self.assertEqual(ctx["yuejian_rule"], "liuyao.rule.r008")
                self.assertEqual(ctx["richen_rule"], "liuyao.rule.r009")

    def test_month_day_structure_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            month_day_structure("午子", "甲子")
        with self.assertRaises(ValueError):
            month_day_structure("午", "甲丑")
        with self.assertRaises(ValueError):
            month_day_structure("午", "甲子 ")


class LineMonthDayStructureTests(unittest.TestCase):
    def test_same_as_and_clash_flags_on_qian_lines(self):
        # Qian branches, month 午 (fire), day 己丑 (branch 丑).
        result = line_month_day_structure(QIAN_BRANCHES, "午", "己丑")
        self.assertEqual(
            [ln["same_as_month"] for ln in result["lines"]],
            [False, False, False, True, False, False],
        )
        self.assertEqual(
            [ln["same_as_day"] for ln in result["lines"]],
            [False] * 6,  # no 丑 line among Qian branches
        )
        self.assertEqual(
            [ln["clashes_month"] for ln in result["lines"]],
            [True, False, False, False, False, False],  # 子冲午
        )
        self.assertEqual(
            [ln["clashes_day"] for ln in result["lines"]],
            [False] * 6,  # 丑冲未，无未爻
        )
        self.assertIsNone(result["wangshuai"])
        self.assertIsNone(result["verdict"])
        self.assertEqual(result["month_day"]["month_element"], "火")
        self.assertEqual(result["month_day"]["day_branch_element"], "土")

    def test_same_as_day_and_clashes_day_with_day_jiazi(self):
        # Day 甲子 (branch 子): line 1 (子) same-as-day, line 4 (午) clashes-day.
        result = line_month_day_structure(QIAN_BRANCHES, "午", "甲子")
        self.assertEqual(
            [ln["same_as_day"] for ln in result["lines"]],
            [True, False, False, False, False, False],
        )
        self.assertEqual(
            [ln["clashes_day"] for ln in result["lines"]],
            [False, False, False, True, False, False],
        )
        # Month facts unchanged by the day change.
        self.assertEqual(
            [ln["clashes_month"] for ln in result["lines"]],
            [True, False, False, False, False, False],
        )
        self.assertEqual(
            [ln["same_as_month"] for ln in result["lines"]],
            [False, False, False, True, False, False],
        )

    def test_clashes_month_equals_month_break_structure(self):
        from tianji_kb.liuyao_empty_break import month_break_flags

        for month in ("子", "午", "寅", "申"):
            with self.subTest(month=month):
                result = line_month_day_structure(QIAN_BRANCHES, month, "甲子")
                self.assertEqual(
                    [ln["clashes_month"] for ln in result["lines"]],
                    month_break_flags(QIAN_BRANCHES, month),
                )

    def test_same_as_facts_carry_no_doctrine_label(self):
        # No registered 临月建/临日辰 term: the structure must not name
        # the same-as facts with those labels anywhere.
        result = line_month_day_structure(QIAN_BRANCHES, "午", "甲子")
        self.assertNotIn("临月建", str(result))
        self.assertNotIn("临日辰", str(result))

    def test_line_month_day_structure_rejects_malformed_input(self):
        with self.assertRaises(ValueError):
            line_month_day_structure(["子"] * 5, "午", "己丑")
        with self.assertRaises(ValueError):
            line_month_day_structure(QIAN_BRANCHES, "午子", "己丑")
        with self.assertRaises(ValueError):
            line_month_day_structure(QIAN_BRANCHES, "午", "甲丑")


class WangshuaiEfficacyTests(unittest.TestCase):
    """L4: efficacy layer is separate and abstains -- never read off structure."""

    def test_assess_wangshuai_always_abstains(self):
        cases = [
            (QIAN_BRANCHES, "午", "己丑"),
            (QIAN_BRANCHES, "子", "甲子"),
            (["寅", "卯", "辰", "巳", "午", "未"], "午", "甲午"),
        ]
        for branches, month, day in cases:
            with self.subTest(month=month, day=day):
                structure = line_month_day_structure(branches, month, day)
                result = assess_wangshuai(structure)
                self.assertEqual(result["status"], "insufficient_basis")
                self.assertIsNone(result["wangshuai"])
                self.assertIsNone(result["verdict"])
                self.assertEqual(result["month_branch"], month)
                self.assertEqual(result["day_ganzhi"], day)

    def test_favourable_structure_still_abstains(self):
        # Even when every line is 生我 against the month (the strongest
        # looking structure: all-wood lines vs month 午 fire... here
        # all lines 生我 means line element generates month element),
        # no wangshuai verdict follows.
        structure = line_month_day_structure(
            ["寅", "卯", "寅", "卯", "寅", "卯"], "午", "甲子"
        )
        self.assertTrue(all(
            ln["relation_to_month"] == "我生" for ln in structure["lines"]
        ))
        result = assess_wangshuai(structure)
        self.assertEqual(result["status"], "insufficient_basis")
        self.assertIsNone(result["wangshuai"])
        self.assertIsNone(result["verdict"])

    def test_unmet_conditions_name_the_missing_basis(self):
        structure = line_month_day_structure(QIAN_BRANCHES, "午", "己丑")
        result = assess_wangshuai(structure)
        self.assertEqual(
            result["unmet_conditions"],
            [
                "registered_sishi_wangxiang_table",
                "xing_hai_earth_disputes_adjudicated",
                "month_day_weighting",
                "line_weak_strong_criterion",
            ],
        )
        for condition in result["conditions"]:
            with self.subTest(condition=condition["id"]):
                self.assertEqual(condition["status"], "unmet")
                self.assertTrue(condition["evidence"])

    def test_sishi_wangxiang_evidence_records_no_registered_text(self):
        self.assertEqual(
            SISH_WANGXIANG_EVIDENCE["chapter"], "四時旺相章第十五"
        )
        self.assertFalse(SISH_WANGXIANG_EVIDENCE["text_registered"])
        self.assertIsNone(SISH_WANGXIANG_EVIDENCE["mapping_table"])
        self.assertEqual(
            SISH_WANGXIANG_EVIDENCE["status"], "no_registered_basis"
        )

    def test_assess_wangshuai_rejects_non_structure_input(self):
        with self.assertRaises(ValueError):
            assess_wangshuai({"month_branch": "午"})
        with self.assertRaises(ValueError):
            assess_wangshuai(None)
        with self.assertRaises(ValueError):
            assess_wangshuai("午")


class RelativeRolesTests(unittest.TestCase):
    """Yuan-shen / ji-shen / chou-shen STRUCTURE framework (no efficacy)."""

    def test_role_definitions_are_framework_only(self):
        self.assertEqual(
            set(RELATIVE_ROLE_DEFINITIONS),
            {"yuanshen", "jishen", "choushen", "yongshen_element",
             "generated_by_yongshen"},
        )
        for key, record in RELATIVE_ROLE_DEFINITIONS.items():
            with self.subTest(role=key):
                self.assertEqual(record["evidence_status"], "framework_only")
                self.assertIsNone(record["classical_citation"])

    def test_roles_partition_all_five_elements_for_every_element(self):
        # Independent derivation from the element cycles.
        generates = dict(zip("木火土金水", "火土金水木"))
        controls = dict(zip("木火土金水", "土金水木火"))
        generated_by = {v: k for k, v in generates.items()}
        controlled_by = {v: k for k, v in controls.items()}
        for element in "木火土金水":
            with self.subTest(yongshen_element=element):
                result = roles_for_element(element)
                self.assertEqual(
                    sorted(result["roles"]), sorted("木火土金水")
                )
                self.assertEqual(
                    sorted(result["roles"].values()),
                    sorted(["yongshen_element", "yuanshen", "jishen",
                            "choushen", "generated_by_yongshen"]),
                )
                self.assertEqual(
                    result["yuanshen_element"], generated_by[element]
                )
                self.assertEqual(
                    result["jishen_element"], controlled_by[element]
                )
                # Choushen (controls the yuanshen) is the element the
                # yongshen element controls.
                self.assertEqual(
                    result["choushen_element"], controls[element]
                )
                self.assertEqual(
                    controls[result["choushen_element"]],
                    result["yuanshen_element"],
                )
                self.assertEqual(
                    result["generated_by_yongshen_element"],
                    generates[element],
                )
                self.assertIsNone(result["verdict"])
                self.assertIsNone(result["effect"])

    def test_fire_yongshen_spot_check(self):
        result = roles_for_element("火")
        self.assertEqual(result["yuanshen_element"], "木")
        self.assertEqual(result["jishen_element"], "水")
        self.assertEqual(result["choushen_element"], "金")
        self.assertEqual(result["generated_by_yongshen_element"], "土")

    def test_qian_lines_roles_relative_to_fire(self):
        result = line_roles_relative_to_element(QIAN_BRANCHES, "火")
        self.assertEqual(
            [ln["role"] for ln in result["lines"]],
            ["jishen", "yuanshen", "generated_by_yongshen",
             "yongshen_element", "choushen", "generated_by_yongshen"],
        )
        self.assertEqual(
            [ln["line_element"] for ln in result["lines"]],
            ["水", "木", "土", "火", "金", "土"],
        )
        self.assertIsNone(result["verdict"])
        self.assertIsNone(result["effect"])
        self.assertEqual(result["evidence_status"], "framework_only")

    def test_same_element_line_is_not_the_useful_god(self):
        # Line 4 shares the yongshen element (fire) but the framework
        # names no useful-god line: the role label is structural only.
        result = line_roles_relative_to_element(QIAN_BRANCHES, "火")
        self.assertEqual(result["lines"][3]["role"], "yongshen_element")
        self.assertNotIn("useful_god", str(result))
        self.assertIn("不是用神爻", result["note"])

    def test_roles_reject_invalid_element_and_branches(self):
        for bad in ("金木", "", None, "earth"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    roles_for_element(bad)
        with self.assertRaises(ValueError):
            line_roles_relative_to_element(["子"] * 5, "火")
        with self.assertRaises(ValueError):
            line_roles_relative_to_element(QIAN_BRANCHES, "火水")
