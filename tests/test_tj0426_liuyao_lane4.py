"""TJ-0426 batch 4 Lane 4: liuyao L-01--L-08 tests.

Evidence first, mapping later. What this suite locks:

- L-01/L-02: career evidence is CONSTRUCTED (evidence pack 05) but the
  mapping is NOT approved: ``USEFUL_GOD_MAPPINGS`` stays ``{}``,
  ``relative_category`` stays None for every type, ``assess()`` still
  abstains for all 8 types, and free-text question fields are still
  rejected by ``validate_question_input``.
- L-03: r013-r018 are registered verbatim (definitions, locators,
  r017/r018 pair tables locked against the registered sentences);
  role efficacy stays ``framework_only`` / ``not_approved``.
- L-04: the 四時旺相 chapter text is located but unregistered, with no
  死 state; ``assess_wangshuai`` still abstains.
- L-05: moving/changed-line STRUCTURE (6/9 moving; branch-changed is
  not motion) + ``assess_moving_effect`` abstains; 暗動 stays
  undetermined because 旺 is unknown.
- L-06: NOT built -- ``EMPTY_HANDLING_EVIDENCE`` stays all
  ``no_registered_basis`` and no chukong/tianshi callable exists.
- L-07: month-break x motion four-class structure facts only;
  distinction verdict and un-breaking stay None.
- L-08: 应期 not started (``RESPONSE_TIMING_GAP``: 0 approved conditions).
- r020: three preconditions (clash + static + weak); missing any one
  means no day-break. The "weak" half depends on the unbuilt L-04
  wangshuai layer, so r020's trigger surface is extremely narrow.
- Real cases (evidence pack 05 §5, 《增删卜易》 originals, never
  invented): C1 未月丁卯日占功名同人變革 (positive: 用神 = 官鬼亥水,
  line 3) and C2 午月辛酉日占功名萃變遁 (negative: 代占, mapping does
  not apply). Yao values are derived from the printed ○/ㄨ/⚊/⚋ marks
  (增删卜易 line 356) and cross-checked against the stated hexagram
  names with the standard eight-trigram table; structure flags
  (empty / month-break / day-clash / day-break) are computed with the
  existing callable layer. 60-day xunkong and 12-month month-break
  full sweeps + real day-ganzhi spot checks (丁卯, 辛酉) included.

Two parts, following test_tj0424_liuyao_xunkong_yuepo.py:
- Pure-function tests: stdlib + the callable layer only; they run
  locally with ``PYTHONPATH=src``.
- ``ChartIntegrationTests``: the same case expectations through the
  real ``operations.liuyao_chart.chart()`` (which needs the canonical
  tables). These run ONLY in the assembled environment; locally they
  skip with an explicit reason.
"""
import unittest
from pathlib import Path

from tianji_kb.foundations import CYCLE
import tianji_kb.liuyao_moving_yao as moving_yao
import tianji_kb.liuyao_yongshen as yongshen
from tianji_kb.liuyao_empty_break import (
    EMPTY_HANDLING_EVIDENCE,
    broken_branch_for_month,
    day_break_assessment,
    day_clash_flags,
    empty_branches_for_day,
    empty_flags_for_day,
    empty_handling_evidence,
    month_break_flags,
)
from tianji_kb.liuyao_moving_yao import (
    CALIBRE,
    DARK_MOVING_CONDITIONS,
    MOVING_YAO_EVIDENCE,
    YUEPO_MOTION_EVIDENCE,
    assess_moving_effect,
    changed_line_facts,
    dark_moving_structure,
    line_motion,
    moving_lines,
    moving_yao_evidence,
    yuepo_motion_evidence,
    yuepo_motion_structure,
)
from tianji_kb.liuyao_yongshen import (
    ROLE_EVIDENCE,
    WEAK_PRECONDITION_NARROW_SCOPE_NOTE,
    SISH_WANGXIANG_CHAPTER,
    SISH_WANGXIANG_EVIDENCE,
    USEFUL_GOD_MAPPINGS,
    RESPONSE_TIMING_GAP,
    assess,
    assess_wangshuai,
    line_month_day_structure,
    list_role_evidence,
    mapping_slot,
    role_evidence,
    roles_for_element,
    validate_question_input,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PRESENT = (
    (ROOT / "data/canonical/liuyao/najia_v1.json").exists()
    and (ROOT / "data/canonical/seed.json").exists()
)

# Standard eight-trigram binary table (bottom to top, 1 = yang):
# 乾 111, 兑 110, 离 101, 震 100, 巽 011, 坎 010, 艮 001, 坤 000.
# Used ONLY to cross-check the case yao-value derivations against the
# hexagram names printed in the book; it is not a doctrine rule.
TRIGRAMS = {
    "111": "乾", "110": "兑", "101": "离", "100": "震",
    "011": "巽", "010": "坎", "001": "艮", "000": "坤",
}


def hexagram_names(yao_values):
    """Return (original, changed) trigram-name pairs for six yao values.

    Original bits: 1 iff the value is yang (7/9). Changed bits: 1 iff
    the value stays yang after movement (6/7).
    """
    bits = "".join("1" if v in (7, 9) else "0" for v in yao_values)
    changed = "".join("1" if v in (6, 7) else "0" for v in yao_values)
    return (
        (TRIGRAMS[bits[:3]], TRIGRAMS[bits[3:]]),
        (TRIGRAMS[changed[:3]], TRIGRAMS[changed[3:]]),
    )


# Real cases (evidence pack 05 §5, 《增删卜易》 originals).
# C1: 未月丁卯日占功名, 火天同人變革卦 (ZS lines 1076-1083).
# C2: 午月辛酉日占功名, 萃變遁 (ZS lines 1761-1768).
CASE_C1 = {
    "question_type": "career",
    "month_branch": "未",
    "day_ganzhi": "丁卯",
    "yao_values": [7, 8, 7, 7, 7, 9],
    "line_branches": ["卯", "丑", "亥", "午", "申", "戌"],
    "changed_branches": ["卯", "丑", "亥", "亥", "酉", "未"],
    "hexagram": ("离", "乾"),
    "changed_hexagram": ("离", "兑"),
    "yongshen_line": 3,
    "yongshen_relative": "官鬼",
    "yongshen_branch": "亥",
    "mapping_applies": True,
}
CASE_C2 = {
    "question_type": "career",
    "month_branch": "午",
    "day_ganzhi": "辛酉",
    "yao_values": [8, 8, 6, 7, 7, 6],
    "line_branches": ["未", "巳", "卯", "亥", "酉", "未"],
    "changed_branches": ["辰", "午", "申", "午", "申", "戌"],
    "hexagram": ("坤", "兑"),
    "changed_hexagram": ("艮", "乾"),
    "yongshen_line": 2,
    "yongshen_relative": "官鬼",
    "yongshen_branch": "巳",
    "mapping_applies": False,
    "not_applying_reason": "父叫子占（父之念）：实为父占子，官鬼取用不成立",
}


class CareerMappingStillUnapprovedTests(unittest.TestCase):
    def test_useful_god_mappings_still_empty(self):
        self.assertEqual(USEFUL_GOD_MAPPINGS, {})
        self.assertEqual(yongshen.get_useful_god_mapping("career"), None)

    def test_career_relative_category_still_none(self):
        career = yongshen.QUESTION_TYPES["career"]
        self.assertIsNone(career["relative_category"])
        self.assertIsNone(career["evidence"]["classical_citation"])
        self.assertEqual(career["evidence"]["status"], "framework_only")

    def test_all_types_still_framework_only(self):
        for type_id, record in yongshen.QUESTION_TYPES.items():
            with self.subTest(type_id=type_id):
                self.assertIsNone(record["relative_category"])
                self.assertEqual(record["evidence"]["status"], "framework_only")

    def test_assess_still_abstains_for_career(self):
        result = assess({
            "question_type": "career",
            "yao_values": [7, 8, 7, 7, 7, 9],
            "value": "2026-11-27T10:00:00+08:00",
        })
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "ambiguous_category")
        self.assertIsNone(result["verdict"])
        self.assertIsNone(result["useful_god"])

    def test_assess_still_abstains_for_all_types(self):
        for type_id in yongshen.QUESTION_TYPES:
            with self.subTest(type_id=type_id):
                result = assess({
                    "question_type": type_id,
                    "yao_values": [7, 7, 7, 7, 7, 7],
                    "value": "2026-11-27T10:00:00+08:00",
                })
                self.assertEqual(result["status"], "abstained")
                self.assertIsNone(result["useful_god"])

    def test_mapping_slot_career_still_unapproved(self):
        slot = mapping_slot("career")
        self.assertIsNone(slot["relative_role"])
        self.assertIsNone(slot["candidate_lines"])
        self.assertIsNone(slot["mapping"])
        self.assertEqual(slot["evidence_status"], "no_approved_mapping")

    def test_free_text_question_still_rejected(self):
        for field in ("question_text", "question", "text", "query"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_question_input({
                        "question_type": "career",
                        "yao_values": [7, 7, 7, 7, 7, 7],
                        "value": "2026-11-27T10:00:00+08:00",
                        field: "我能升职吗",
                    })


class RoleEvidenceRegistrationTests(unittest.TestCase):
    EXPECTED_DEFINITIONS = {
        "liuyao.rule.r013": "用神﹐卽前各類之用神也。",
        "liuyao.rule.r014": "元神﹐生用神之神卽為元神。",
        "liuyao.rule.r015": "忌神克用神之爻也。",
        "liuyao.rule.r016": "仇神者克元神而生忌神也。",
        "liuyao.rule.r017": (
            "凡卦中亥變子，醜變辰，寅變卯，辰變未，巳變午，未變戌，"
            "申變酉，戌變丑，乃進神也"
        ),
        "liuyao.rule.r018": (
            "凡卦中子變亥，戌變未，酉變申，未變辰，午變巳，辰變丑，"
            "卯變寅，醜變戌，乃退神也"
        ),
    }
    EXPECTED_LOCATORS = {
        "liuyao.rule.r013": "增删卜易 chars [15722,15734)",
        "liuyao.rule.r014": "增删卜易 chars [15734,15747)",
        "liuyao.rule.r015": "增删卜易 chars [15747,15756)",
        "liuyao.rule.r016": "增删卜易 chars [15756,15768)",
        "liuyao.rule.r017": "卜筮正宗 chars [29889,29928)",
        "liuyao.rule.r018": "卜筮正宗 chars [29942,29981)",
    }

    def test_all_six_rules_registered(self):
        self.assertEqual(
            sorted(ROLE_EVIDENCE),
            [
                "liuyao.rule.r013", "liuyao.rule.r014", "liuyao.rule.r015",
                "liuyao.rule.r016", "liuyao.rule.r017", "liuyao.rule.r018",
            ],
        )

    def test_definitions_verbatim(self):
        for rule_id, definition in self.EXPECTED_DEFINITIONS.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(ROLE_EVIDENCE[rule_id]["definition"], definition)
                self.assertEqual(role_evidence(rule_id)["definition"], definition)

    def test_locators_verbatim(self):
        for rule_id, locator in self.EXPECTED_LOCATORS.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(ROLE_EVIDENCE[rule_id]["locator"], locator)

    def test_all_partially_structured_and_efficacy_not_approved(self):
        for rule_id, record in ROLE_EVIDENCE.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(record["execution_status"], "partially_structured")
                self.assertEqual(record["status"], "registered_definition_only")
                self.assertEqual(record["efficacy"], "not_approved")

    def test_pair_tables_match_the_registered_sentences(self):
        import re

        for rule_id in ("liuyao.rule.r017", "liuyao.rule.r018"):
            with self.subTest(rule_id=rule_id):
                definition = ROLE_EVIDENCE[rule_id]["definition"]
                parsed = tuple(
                    (a, b) for a, b in re.findall("(.)變(.)", definition)
                )
                self.assertEqual(len(parsed), 8)
                self.assertEqual(ROLE_EVIDENCE[rule_id]["pairs"], parsed)

    def test_pair_tables_normalize_to_the_expected_standard_branches(self):
        expected_jin = {
            ("亥", "子"), ("丑", "辰"), ("寅", "卯"), ("辰", "未"),
            ("巳", "午"), ("未", "戌"), ("申", "酉"), ("戌", "丑"),
        }
        expected_tui = {
            ("子", "亥"), ("戌", "未"), ("酉", "申"), ("未", "辰"),
            ("午", "巳"), ("辰", "丑"), ("卯", "寅"), ("丑", "戌"),
        }
        normalize = lambda pairs: {(a.replace("醜", "丑"), b.replace("醜", "丑")) for a, b in pairs}
        self.assertEqual(normalize(ROLE_EVIDENCE["liuyao.rule.r017"]["pairs"]), expected_jin)
        self.assertEqual(normalize(ROLE_EVIDENCE["liuyao.rule.r018"]["pairs"]), expected_tui)

    def test_variant_character_preserved_verbatim(self):
        # The original writes 醜 (U+91DC) in r017 pair 2 and r018 pair 8,
        # 丑 (U+4E11) elsewhere: transcription must not normalize it away.
        self.assertEqual(ROLE_EVIDENCE["liuyao.rule.r017"]["pairs"][1][0], "醜")
        self.assertEqual(ROLE_EVIDENCE["liuyao.rule.r018"]["pairs"][7][0], "醜")
        self.assertEqual(ROLE_EVIDENCE["liuyao.rule.r017"]["pairs"][7][1], "丑")

    def test_role_evidence_accessor_returns_copies(self):
        first = role_evidence("liuyao.rule.r013")
        first["definition"] = "tampered"
        self.assertEqual(
            role_evidence("liuyao.rule.r013")["definition"],
            self.EXPECTED_DEFINITIONS["liuyao.rule.r013"],
        )
        self.assertEqual(len(list_role_evidence()), 6)

    def test_role_evidence_rejects_unknown_rule(self):
        with self.assertRaises(ValueError):
            role_evidence("liuyao.rule.r999")

    def test_roles_framework_still_framework_only(self):
        partition = roles_for_element("火")
        self.assertEqual(partition["evidence_status"], "framework_only")
        self.assertIsNone(partition["verdict"])
        self.assertIsNone(partition["effect"])


class WangshuaiStillAbstainsTests(unittest.TestCase):
    def test_sishi_chapter_located_but_unregistered(self):
        self.assertEqual(
            SISH_WANGXIANG_CHAPTER["registration_status"],
            "text_located_unregistered",
        )
        self.assertIsNone(SISH_WANGXIANG_CHAPTER["mapping_table"])
        self.assertEqual(SISH_WANGXIANG_CHAPTER["status"], "no_registered_basis")

    def test_sishi_chapter_has_no_death_state(self):
        self.assertNotIn("死", SISH_WANGXIANG_CHAPTER["states_attested"])
        self.assertEqual(SISH_WANGXIANG_CHAPTER["states_missing"], ("死",))
        self.assertEqual(SISH_WANGXIANG_CHAPTER["state_counts"]["死"], 0)
        self.assertEqual(
            SISH_WANGXIANG_CHAPTER["states_attested"], ("旺", "相", "休", "囚")
        )

    def test_sishi_chapter_locators(self):
        self.assertEqual(
            SISH_WANGXIANG_CHAPTER["text_locator"],
            "增删卜易 chars [18818,19181), 第 532 行，363 字",
        )
        self.assertIn("[18808,18817)", SISH_WANGXIANG_CHAPTER["title_locator"])

    def test_assess_wangshuai_still_abstains(self):
        structure = line_month_day_structure(
            ["子", "寅", "辰", "午", "申", "戌"], "寅", "甲子"
        )
        result = assess_wangshuai(structure)
        self.assertEqual(result["status"], "insufficient_basis")
        self.assertIsNone(result["wangshuai"])
        self.assertIsNone(result["verdict"])
        self.assertIn(
            "registered_sishi_wangxiang_table", result["unmet_conditions"]
        )

    def test_original_sishi_evidence_record_unchanged(self):
        self.assertFalse(SISH_WANGXIANG_EVIDENCE["text_registered"])
        self.assertIsNone(SISH_WANGXIANG_EVIDENCE["mapping_table"])
        self.assertEqual(
            SISH_WANGXIANG_EVIDENCE["status"], "no_registered_basis"
        )


class MovingYaoStructureTests(unittest.TestCase):
    def test_calibre_is_research_only(self):
        self.assertTrue(CALIBRE["research_only"])
        self.assertFalse(CALIBRE["public"])
        self.assertFalse(CALIBRE["ai"])
        self.assertIn("moving_line_efficacy", CALIBRE["does_not_compute"])
        self.assertIn("yuepo_unbreaking", CALIBRE["does_not_compute"])

    def test_moving_lines_split_6_9_from_7_8(self):
        self.assertEqual(moving_lines([7, 8, 7, 7, 7, 9]), [6])
        self.assertEqual(moving_lines([8, 8, 6, 7, 7, 6]), [3, 6])
        self.assertEqual(moving_lines([7, 7, 7, 7, 7, 7]), [])
        self.assertEqual(moving_lines([6, 9, 6, 9, 6, 9]), [1, 2, 3, 4, 5, 6])

    def test_line_motion_marks_each_line(self):
        motion = line_motion([6, 7, 8, 9, 7, 8])
        self.assertEqual(
            [ln["moving"] for ln in motion],
            [True, False, False, True, False, False],
        )

    def test_moving_lines_reject_malformed_input(self):
        for bad in ([7] * 5, [7] * 7, [5, 7, 7, 7, 7, 7], "777777", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    moving_lines(bad)

    def test_branch_changed_is_not_motion_c1_trap(self):
        # Case C1: lines 4 and 5 show different changed branches while
        # static (whole-trigram najia recomputation); only line 6 moves.
        facts = changed_line_facts(
            CASE_C1["yao_values"],
            CASE_C1["line_branches"],
            CASE_C1["changed_branches"],
        )
        self.assertEqual(facts["moving_lines"], [6])
        self.assertEqual(facts["branch_changed_lines"], [4, 5, 6])
        self.assertFalse(facts["lines"][3]["moving"])
        self.assertTrue(facts["lines"][3]["branch_changed"])
        self.assertFalse(facts["lines"][4]["moving"])
        self.assertTrue(facts["lines"][4]["branch_changed"])
        self.assertIsNone(facts["effect"])
        self.assertIsNone(facts["verdict"])

    def test_changed_line_facts_c2_all_branches_differ(self):
        facts = changed_line_facts(
            CASE_C2["yao_values"],
            CASE_C2["line_branches"],
            CASE_C2["changed_branches"],
        )
        self.assertEqual(facts["moving_lines"], [3, 6])
        self.assertEqual(facts["branch_changed_lines"], [1, 2, 3, 4, 5, 6])

    def test_assess_moving_effect_abstains(self):
        facts = changed_line_facts(
            CASE_C1["yao_values"],
            CASE_C1["line_branches"],
            CASE_C1["changed_branches"],
        )
        result = assess_moving_effect(facts)
        self.assertEqual(result["status"], "insufficient_basis")
        self.assertIsNone(result["effect"])
        self.assertIsNone(result["verdict"])
        self.assertEqual(result["moving_lines"], [6])
        self.assertIn(
            "registered_return_effect_rule", result["unmet_conditions"]
        )

    def test_assess_moving_effect_rejects_non_structure(self):
        for bad in (None, {}, {"moving_lines": [1]}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    assess_moving_effect(bad)

    def test_moving_yao_evidence_registered_vs_located(self):
        evidence = moving_yao_evidence()
        self.assertEqual(evidence["motion_definition"]["status"], "registered")
        self.assertEqual(
            evidence["motion_definition"]["definition"],
            "六爻不動則不變﹐動則必變",
        )
        self.assertEqual(
            evidence["changed_line_relatives"]["definition"],
            "變出之爻安六親者仍照正卦而推",
        )
        self.assertEqual(
            evidence["dark_moving_definition"]["definition"],
            "爻之旺而靜者沖之則為暗動",
        )
        self.assertEqual(
            evidence["return_effect_candidates"]["status"],
            "located_unregistered",
        )
        # Accessor returns a copy.
        evidence["motion_definition"]["definition"] = "tampered"
        self.assertEqual(
            moving_yao_evidence()["motion_definition"]["definition"],
            "六爻不動則不變﹐動則必變",
        )

    def test_dark_moving_stays_undetermined_because_strong_unknown(self):
        # A static line clashed by the day: static + clashed hold, but
        # 旺 is unknown (L-04), so 暗動 must stay undetermined.
        result = dark_moving_structure(
            ["子", "寅", "辰", "午", "申", "戌"], [7, 7, 7, 7, 7, 7],
            "午", "甲子",
        )
        self.assertEqual(result["dark_moving_lines"], [])
        self.assertEqual(result["undetermined_lines"], [1, 2, 3, 4, 5, 6])
        self.assertIsNone(result["verdict"])
        line_4 = result["lines"][3]
        self.assertTrue(line_4["is_static"])
        self.assertTrue(line_4["clashes_day"])
        self.assertIsNone(line_4["strong"])
        self.assertIsNone(line_4["dark_moving"])
        self.assertEqual(line_4["status"], "undetermined_strong_unknown")

    def test_dark_moving_conditions_name_the_unmet_strong_condition(self):
        by_id = {c["id"]: c for c in DARK_MOVING_CONDITIONS}
        self.assertEqual(by_id["line_static"]["status"], "computable")
        self.assertEqual(by_id["line_clashed"]["status"], "computable")
        self.assertEqual(by_id["line_strong"]["status"], "unmet")


class EmptyHandlingNotBuiltTests(unittest.TestCase):
    def test_every_candidate_still_no_registered_basis(self):
        evidence = empty_handling_evidence()
        self.assertEqual(
            set(evidence),
            {"chukong", "tianshi", "zhiri", "hezhu_chongkai_empty",
             "yuepo_unbreaking"},
        )
        for key, record in evidence.items():
            with self.subTest(key=key):
                self.assertEqual(record["status"], "no_registered_basis")

    def test_empty_handling_constant_unchanged(self):
        self.assertEqual(
            EMPTY_HANDLING_EVIDENCE["chukong"]["status"],
            "no_registered_basis",
        )
        self.assertEqual(
            EMPTY_HANDLING_EVIDENCE["yuepo_unbreaking"]["status"],
            "no_registered_basis",
        )

    def test_no_chukong_tianshi_callable_exists_in_lane_modules(self):
        for module in (moving_yao, yongshen):
            for name in dir(module):
                self.assertNotIn("chukong", name.lower())
                self.assertNotIn("tianshi", name.lower())

    def test_no_yingqi_callable_exists_in_lane_modules(self):
        for module in (moving_yao, yongshen):
            self.assertFalse(hasattr(module, "assess_yingqi"))
            self.assertFalse(hasattr(module, "yingqi"))


class YuepoMotionStructureTests(unittest.TestCase):
    def test_four_motion_classes_cover_all_lines(self):
        result = yuepo_motion_structure(
            ["子", "寅", "辰", "午", "申", "戌"], "午", [9, 7, 7, 7, 7, 7]
        )
        classes = [ln["motion_class"] for ln in result["lines"]]
        self.assertEqual(
            classes,
            ["broken_moving", "unbroken_static", "unbroken_static",
             "unbroken_static", "unbroken_static", "unbroken_static"],
        )
        self.assertEqual(result["broken_moving_lines"], [1])
        self.assertEqual(result["broken_static_lines"], [])

    def test_broken_static_class(self):
        result = yuepo_motion_structure(
            ["子", "寅", "辰", "午", "申", "戌"], "午", [7, 7, 7, 7, 7, 7]
        )
        self.assertEqual(result["lines"][0]["motion_class"], "broken_static")
        self.assertEqual(result["broken_static_lines"], [1])

    def test_distinction_verdict_and_unbreaking_stay_none(self):
        result = yuepo_motion_structure(
            ["子", "寅", "辰", "午", "申", "戌"], "午", [9, 7, 7, 7, 7, 7]
        )
        self.assertIsNone(result["distinction_verdict"])
        self.assertIsNone(result["unbreaking"])
        self.assertEqual(result["unbreaking_status"], "no_registered_basis")
        self.assertIsNone(result["verdict"])

    def test_yuepo_motion_evidence_records_no_basis(self):
        evidence = yuepo_motion_evidence()
        self.assertEqual(
            evidence["moving_static_distinction"]["status"],
            "no_registered_basis",
        )
        self.assertEqual(
            evidence["yuepo_unbreaking"]["status"], "no_registered_basis"
        )
        self.assertIn("張星元", evidence["yuepo_unbreaking"]["located_candidates"])
        # Accessor returns a copy.
        evidence["yuepo_unbreaking"]["status"] = "tampered"
        self.assertEqual(
            yuepo_motion_evidence()["yuepo_unbreaking"]["status"],
            "no_registered_basis",
        )

    def test_yuepo_motion_rejects_malformed_input(self):
        with self.assertRaises(ValueError):
            yuepo_motion_structure(["子"] * 5, "午", [7] * 6)
        with self.assertRaises(ValueError):
            yuepo_motion_structure(["子"] * 6, "午", [7] * 5)


class YingqiGapTests(unittest.TestCase):
    def test_yingqi_not_started(self):
        self.assertEqual(RESPONSE_TIMING_GAP["status"], "not_started")
        self.assertEqual(RESPONSE_TIMING_GAP["approved_conditions"], 0)
        self.assertIn("approved L-01 useful-god mapping", RESPONSE_TIMING_GAP["prerequisites"])
        self.assertIn("L-04 wangshuai efficacy layer", RESPONSE_TIMING_GAP["prerequisites"])
        self.assertEqual(
            RESPONSE_TIMING_GAP["prerequisite_status"]["approved L-01 useful-god mapping"],
            "unmet",
        )


class RipoThreePremisesTests(unittest.TestCase):
    """r020: clash + static + weak; missing any one means no day-break."""

    def test_all_three_premises_trigger(self):
        result = day_break_assessment(
            ["子", "寅", "辰", "午", "申", "戌"], "甲子", [7, 7, 7, 7, 7, 7],
            line_weak_flags=[None, None, None, True, None, None],
        )
        self.assertEqual(result["day_break_lines"], [4])
        self.assertEqual(result["lines"][3]["status"], "day_break")

    def test_missing_weak_is_undetermined_not_triggered(self):
        result = day_break_assessment(
            ["子", "寅", "辰", "午", "申", "戌"], "甲子", [7, 7, 7, 7, 7, 7],
        )
        self.assertEqual(result["day_break_lines"], [])
        self.assertEqual(result["undetermined_lines"], [4])
        self.assertIsNone(result["lines"][3]["day_break"])
        self.assertEqual(
            result["lines"][3]["status"], "undetermined_weak_unknown"
        )

    def test_explicitly_not_weak_does_not_trigger(self):
        result = day_break_assessment(
            ["子", "寅", "辰", "午", "申", "戌"], "甲子", [7, 7, 7, 7, 7, 7],
            line_weak_flags=[None, None, None, False, None, None],
        )
        self.assertEqual(result["day_break_lines"], [])
        self.assertEqual(result["lines"][3]["status"], "not_day_break_not_weak")

    def test_moving_line_never_triggers_even_when_weak(self):
        result = day_break_assessment(
            ["子", "寅", "辰", "午", "申", "戌"], "甲子", [9, 7, 7, 7, 7, 7],
            line_weak_flags=[True, None, None, None, None, None],
        )
        self.assertEqual(result["day_break_lines"], [])
        self.assertEqual(result["lines"][0]["status"], "not_day_break")

    def test_unclashed_line_never_triggers_even_when_weak_and_static(self):
        result = day_break_assessment(
            ["子", "寅", "辰", "午", "申", "戌"], "甲子", [7, 7, 7, 7, 7, 7],
            line_weak_flags=[True, True, True, True, True, True],
        )
        self.assertEqual(result["day_break_lines"], [4])

    def test_ripo_narrow_scope_note_is_recorded(self):
        self.assertIn("L-04", WEAK_PRECONDITION_NARROW_SCOPE_NOTE)
        self.assertIn("触发面极窄", WEAK_PRECONDITION_NARROW_SCOPE_NOTE)
        self.assertIn("冲日支", WEAK_PRECONDITION_NARROW_SCOPE_NOTE)


class RealCaseVerificationTests(unittest.TestCase):
    def test_c1_yao_values_reproduce_the_stated_hexagrams(self):
        original, changed = hexagram_names(CASE_C1["yao_values"])
        self.assertEqual(original, CASE_C1["hexagram"])
        self.assertEqual(changed, CASE_C1["changed_hexagram"])
        self.assertEqual(original, ("离", "乾"))  # 火天同人
        self.assertEqual(changed, ("离", "兑"))  # 泽火革

    def test_c2_yao_values_reproduce_the_stated_hexagrams(self):
        original, changed = hexagram_names(CASE_C2["yao_values"])
        self.assertEqual(original, CASE_C2["hexagram"])
        self.assertEqual(changed, CASE_C2["changed_hexagram"])
        self.assertEqual(original, ("坤", "兑"))  # 泽地萃
        self.assertEqual(changed, ("艮", "乾"))  # 天山遁

    def test_c1_moving_lines(self):
        self.assertEqual(moving_lines(CASE_C1["yao_values"]), [6])

    def test_c2_moving_lines(self):
        self.assertEqual(moving_lines(CASE_C2["yao_values"]), [3, 6])

    def test_c1_yongshen_line_is_the_official_line(self):
        # The book's 断曰 takes 官鬼亥水 (line 3, 世) as 用神; the case
        # record locks that stated line/relative/branch, it is not a
        # computed mapping (no mapping is approved).
        self.assertEqual(CASE_C1["yongshen_line"], 3)
        self.assertEqual(CASE_C1["yongshen_relative"], "官鬼")
        self.assertEqual(
            CASE_C1["line_branches"][CASE_C1["yongshen_line"] - 1], "亥"
        )
        self.assertTrue(CASE_C1["mapping_applies"])

    def test_c2_mapping_does_not_apply(self):
        # 父叫子占: the question belongs to the father, so the career
        # mapping does not hit even though 官鬼巳火 holds the 世 line.
        self.assertFalse(CASE_C2["mapping_applies"])
        self.assertIn("父叫子占", CASE_C2["not_applying_reason"])
        self.assertEqual(
            CASE_C2["line_branches"][CASE_C2["yongshen_line"] - 1], "巳"
        )

    def test_c1_structure_flags(self):
        self.assertEqual(
            empty_branches_for_day(CASE_C1["day_ganzhi"]), ["戌", "亥"]
        )
        self.assertEqual(
            empty_flags_for_day(
                CASE_C1["line_branches"], CASE_C1["day_ganzhi"]
            ),
            [False, False, True, False, False, True],
        )
        self.assertEqual(
            month_break_flags(
                CASE_C1["line_branches"], CASE_C1["month_branch"]
            ),
            [False, True, False, False, False, False],
        )
        self.assertEqual(
            day_clash_flags(
                CASE_C1["line_branches"], CASE_C1["day_ganzhi"]
            ),
            [False] * 6,
        )
        assessment = day_break_assessment(
            CASE_C1["line_branches"],
            CASE_C1["day_ganzhi"],
            CASE_C1["yao_values"],
        )
        self.assertEqual(assessment["day_break_lines"], [])
        self.assertEqual(assessment["undetermined_lines"], [])

    def test_c2_structure_flags(self):
        self.assertEqual(
            empty_branches_for_day(CASE_C2["day_ganzhi"]), ["子", "丑"]
        )
        self.assertEqual(
            empty_flags_for_day(
                CASE_C2["line_branches"], CASE_C2["day_ganzhi"]
            ),
            [False] * 6,
        )
        self.assertEqual(
            month_break_flags(
                CASE_C2["line_branches"], CASE_C2["month_branch"]
            ),
            [False] * 6,
        )
        self.assertEqual(
            day_clash_flags(
                CASE_C2["line_branches"], CASE_C2["day_ganzhi"]
            ),
            [False, False, True, False, False, False],
        )
        # Line 3 day-clashes but moves: not day-break (missing 静).
        assessment = day_break_assessment(
            CASE_C2["line_branches"],
            CASE_C2["day_ganzhi"],
            CASE_C2["yao_values"],
        )
        self.assertEqual(assessment["day_break_lines"], [])
        self.assertEqual(assessment["lines"][2]["status"], "not_day_break_moving")

    def test_c1_yuepo_motion_classes(self):
        result = yuepo_motion_structure(
            CASE_C1["line_branches"],
            CASE_C1["month_branch"],
            CASE_C1["yao_values"],
        )
        self.assertEqual(
            [ln["motion_class"] for ln in result["lines"]],
            ["unbroken_static", "broken_static", "unbroken_static",
             "unbroken_static", "unbroken_static", "unbroken_moving"],
        )
        self.assertIsNone(result["distinction_verdict"])
        self.assertIsNone(result["unbreaking"])

    def test_c2_jinshen_pair_present_in_case(self):
        # C2 line 6: 未土 -> 戌土 is an r017 进神 pair (data only).
        pairs = dict(
            (a, b) for a, b in ROLE_EVIDENCE["liuyao.rule.r017"]["pairs"]
        )
        self.assertEqual(pairs.get("未"), "戌")
        facts = changed_line_facts(
            CASE_C2["yao_values"],
            CASE_C2["line_branches"],
            CASE_C2["changed_branches"],
        )
        self.assertEqual(
            (facts["lines"][5]["original_branch"],
             facts["lines"][5]["changed_branch"]),
            ("未", "戌"),
        )

    def test_c1_tuishen_pair_present_in_case(self):
        # C1 line 6: 戌土 -> 未土 is an r018 退神 pair (data only).
        pairs = dict(
            (a, b) for a, b in ROLE_EVIDENCE["liuyao.rule.r018"]["pairs"]
        )
        self.assertEqual(pairs.get("戌"), "未")


class FullSweepRegressionTests(unittest.TestCase):
    def test_empty_branches_for_all_sixty_days(self):
        for day in CYCLE:
            with self.subTest(day=day):
                branches = empty_branches_for_day(day)
                self.assertEqual(len(branches), 2)
                self.assertEqual(len(set(branches)), 2)

    def test_real_day_ganzhi_spot_checks(self):
        self.assertEqual(empty_branches_for_day("丁卯"), ["戌", "亥"])
        self.assertEqual(empty_branches_for_day("辛酉"), ["子", "丑"])
        self.assertEqual(empty_branches_for_day("甲子"), ["戌", "亥"])
        self.assertEqual(empty_branches_for_day("己丑"), ["午", "未"])

    def test_broken_branch_for_all_twelve_months(self):
        from tianji_kb.operations.liuyao import branch_relation

        for month in "子丑寅卯辰巳午未申酉戌亥":
            with self.subTest(month=month):
                broken = broken_branch_for_month(month)
                self.assertTrue(branch_relation(month, broken)["clash"])
                self.assertNotEqual(broken, month)

    def test_month_break_flags_twelve_month_sweep(self):
        branches = ["子", "寅", "辰", "午", "申", "戌"]
        for month in "子丑寅卯辰巳午未申酉戌亥":
            with self.subTest(month=month):
                broken = broken_branch_for_month(month)
                flags = month_break_flags(branches, month)
                if broken in branches:
                    self.assertEqual(sum(flags), 1)
                    self.assertEqual(flags.index(True), branches.index(broken))
                else:
                    self.assertEqual(sum(flags), 0)


@unittest.skipUnless(
    DATA_PRESENT,
    "assembled environment only: needs data/canonical/liuyao/najia_v1.json "
    "and data/canonical/seed.json",
)
class ChartIntegrationTests(unittest.TestCase):
    def test_c1_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart(
            list(CASE_C1["yao_values"]),
            CASE_C1["day_ganzhi"],
            CASE_C1["month_branch"],
        )["result"]
        self.assertEqual(result["empty_branches"], ["戌", "亥"])
        self.assertEqual(
            [line["empty"] for line in result["lines"]],
            [False, False, True, False, False, True],
        )
        self.assertEqual(
            [line["month_break"] for line in result["lines"]],
            [False, True, False, False, False, False],
        )
        self.assertEqual(
            [line["najia"][1] for line in result["lines"]],
            CASE_C1["line_branches"],
        )
        self.assertEqual(
            [line["changed_najia"][1] for line in result["lines"]],
            CASE_C1["changed_branches"],
        )
        self.assertEqual(result["lines"][2]["relative"], "官鬼")
        self.assertEqual(result["lines"][2]["najia"], "亥水")

    def test_c2_via_chart(self):
        from tianji_kb.operations.liuyao_chart import chart

        result = chart(
            list(CASE_C2["yao_values"]),
            CASE_C2["day_ganzhi"],
            CASE_C2["month_branch"],
        )["result"]
        self.assertEqual(result["empty_branches"], ["子", "丑"])
        self.assertEqual(
            [line["empty"] for line in result["lines"]],
            [False] * 6,
        )
        self.assertEqual(
            [line["month_break"] for line in result["lines"]],
            [False] * 6,
        )
        self.assertEqual(
            [line["najia"][1] for line in result["lines"]],
            CASE_C2["line_branches"],
        )
        self.assertEqual(
            [line["changed_najia"][1] for line in result["lines"]],
            CASE_C2["changed_branches"],
        )
        self.assertEqual(result["lines"][1]["relative"], "官鬼")


if __name__ == "__main__":
    unittest.main()
