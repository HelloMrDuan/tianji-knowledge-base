"""TJ-025.2 unified life-report condition markers: pure derivation contract.

These tests exercise only the marker builder with structures shaped exactly
like the real _life outputs. End-to-end consistency against the real report
(same birth instant, real runtime) lives in
test_tj0252_life_condition_markers_sealed.py (offline acceptance only).
"""
import unittest

from tianji_kb.scenario_engine import _life_condition_markers

NOT_AVAILABLE = "本项尚未具备解释条件"
AVAILABLE = "具备解释条件"
DIMENSION_ORDER = [
    "natal_foundation", "annual_career", "annual_romance",
    "cross_rule_synthesis", "strength_classification", "dayun_timeline",
    "personal_evaluation",
]


def current_facts():
    """Mirror of today's real _life structures (all approvals withheld)."""
    strength_context = {
        "classification": "unresolved",
        "boundary": "现有证据不能通用判定身强身弱、喜用神、格局或实际作用效力。",
        "reading": "月支为寅，藏干为甲、丙、戊；通根位置观察：年支寅藏甲。",
        "evidence_ids": ["ev-strength"],
    }
    cross_rule_audit = {
        "reading": "流年与夫妻宫结构事实一致；并非两份独立证据。",
        "interpretation_allowed": False,
        "independent_confirmations": False,
        "yearly_and_romance_agree": True,
        "evidence_ids": ["ev-pair"],
    }
    provenance = {
        "all_natal_charts_identical": True,
        "all_target_years_identical": True,
        "strength_classification_approved": False,
        "dayun_timeline_approved": False,
        "interpretation_allowed": False,
    }
    reading = {
        "foundation": strength_context["reading"],
        "career": "流年结构上下文。",
        "romance": "夫妻宫结构上下文。这些不是正缘、婚期或感情走向判断。",
        # TJ-031.19 (E0427, Q3=A): mirror updated to the current real
        # _life no-role wording verbatim -- the E0362 "尚未批准接入
        # 本总览" blanket non-approval is superseded (the timeline
        # is approved, role-gated); see test_tj0252_dayun_copy_e0362.
        "dayun": ("大运方向与起运换算已有完成审核的注册规则（方向据三命分段；"
                  "起运换算有三命、神峰两套口径分别注册，只给出交运时刻区间，"
                  "不折算单点岁数或日期）；未选择传统口径，本总览不呈现大运，"
                  "选定口径后呈现完整 8 运时间线；岁运效力仍无完成审核的"
                  "生产规则，本总览不推算或伪造大运时间线。"),
        "boundary": "尚无证据将它们合成为事业、收入、婚恋吉凶或人生定论。",
        "dayun_timeline_approved": False,
        "personal_prediction": False,
        "interpretation_level": "reviewed_cross_scenario_structure_only",
    }
    return strength_context, cross_rule_audit, provenance, reading


# TJ-031.19 (E0427, Q3=A): mirror of the real _life WITH-ROLE dayun
# exit verbatim -- the full 8-period timeline is presented via the
# life presentation; the marker below must carry this text, not the
# no-role text above.
ROLE_DAYUN = ("已按所选传统口径呈现完整 8 运大运时间线（方向与交运区间，"
              "两口径分立，见人生总览呈现）；每运只给交运区间，不折算"
              "起运岁数或日期；岁运效力仍无完成审核的生产规则，本总览"
              "不推算或伪造大运时间线。")


def build(facts=None):
    sc, cra, prov, reading = facts or current_facts()
    return _life_condition_markers(
        strength_context=sc, cross_rule_audit=cra,
        integration_provenance=prov, integrated_reading=reading,
        annual_career_evidence_ids=["ev-career"],
        spouse_evidence_ids=["ev-spouse"])


class LifeConditionMarkerBuilderTests(unittest.TestCase):
    def test_dimensions_fixed_order_and_wbs_statements(self):
        markers = build()
        self.assertEqual([m["dimension"] for m in markers], DIMENSION_ORDER)
        for m in markers:
            self.assertIn(m["statement"], (AVAILABLE, NOT_AVAILABLE))
            self.assertEqual(
                m["statement"],
                AVAILABLE if m["condition"] == "available" else NOT_AVAILABLE)

    def test_current_facts_mark_refusals_not_available_with_reasons(self):
        markers = {m["dimension"]: m for m in build()}
        expected = {
            "cross_rule_synthesis": "shared_rules_not_independent_evidence",
            "strength_classification": "strength_classification_unresolved",
            "dayun_timeline": "no_approved_production_rule",
            "personal_evaluation": "comprehensive_synthesis_not_approved",
        }
        for dimension, category in expected.items():
            m = markers[dimension]
            self.assertEqual(m["condition"], "not_available", dimension)
            self.assertEqual(m["statement"], NOT_AVAILABLE, dimension)
            self.assertEqual(m["reason_category"], category, dimension)
            self.assertTrue(m["reason"], dimension)
        for dimension in ("natal_foundation", "annual_career", "annual_romance"):
            m = markers[dimension]
            self.assertEqual(m["condition"], "available", dimension)
            self.assertEqual(m["statement"], AVAILABLE, dimension)
            self.assertIsNone(m["reason_category"], dimension)
            self.assertEqual(m["scope"], "reviewed_structure_only", dimension)

    def test_exit_text_is_the_dimensions_own_prose_verbatim(self):
        sc, cra, prov, reading = current_facts()
        markers = {m["dimension"]: m for m in build((sc, cra, prov, reading))}
        self.assertEqual(markers["natal_foundation"]["exit_text"],
                         reading["foundation"])
        self.assertEqual(markers["annual_career"]["exit_text"], reading["career"])
        self.assertEqual(markers["annual_romance"]["exit_text"], reading["romance"])
        self.assertEqual(markers["cross_rule_synthesis"]["exit_text"],
                         cra["reading"])
        self.assertEqual(markers["cross_rule_synthesis"]["reason"], cra["reading"])
        self.assertEqual(markers["strength_classification"]["exit_text"],
                         sc["boundary"])
        self.assertEqual(markers["strength_classification"]["reason"],
                         sc["boundary"])
        self.assertEqual(markers["dayun_timeline"]["exit_text"], reading["dayun"])
        self.assertEqual(markers["personal_evaluation"]["exit_text"],
                         reading["boundary"])

    def test_basis_values_are_copied_from_source_facts(self):
        markers = {m["dimension"]: m for m in build()}
        self.assertEqual(
            markers["strength_classification"]["basis"],
            {"classification": "unresolved",
             "strength_classification_approved": False})
        self.assertEqual(markers["dayun_timeline"]["basis"],
                         {"dayun_timeline_approved": False})
        self.assertEqual(
            markers["cross_rule_synthesis"]["basis"],
            {"yearly_and_romance_agree": True,
             "independent_confirmations": False,
             "interpretation_allowed": False})
        self.assertEqual(
            markers["personal_evaluation"]["basis"],
            {"personal_prediction": False, "interpretation_allowed": False,
             "interpretation_level": "reviewed_cross_scenario_structure_only"})
        self.assertEqual(markers["natal_foundation"]["evidence_ids"],
                         ["ev-strength"])
        self.assertEqual(markers["cross_rule_synthesis"]["evidence_ids"],
                         ["ev-pair"])

    def test_role_dayun_text_flows_into_marker(self):
        # TJ-031.19 (E0427, Q3=A): with a role both flags are True,
        # so the dayun marker is available and carries the role
        # exit text verbatim as both reason and exit_text.
        sc, cra, prov, reading = current_facts()
        prov = dict(prov, dayun_timeline_approved=True)
        reading = dict(reading, dayun=ROLE_DAYUN,
                       dayun_timeline_approved=True)
        markers = {m["dimension"]: m
                   for m in build((sc, cra, prov, reading))}
        marker = markers["dayun_timeline"]
        self.assertEqual(marker["condition"], "available")
        self.assertEqual(marker["statement"], AVAILABLE)
        self.assertIsNone(marker["reason_category"])
        self.assertEqual(marker["reason"], ROLE_DAYUN)
        self.assertEqual(marker["exit_text"], ROLE_DAYUN)
        self.assertEqual(marker["basis"],
                         {"dayun_timeline_approved": True})

    def test_markers_flip_only_when_source_facts_flip(self):
        sc, cra, prov, reading = current_facts()
        prov = dict(prov, strength_classification_approved=True,
                    dayun_timeline_approved=True, interpretation_allowed=True)
        sc = dict(sc, classification="strong")
        cra = dict(cra, interpretation_allowed=True,
                   independent_confirmations=True)
        reading = dict(reading, dayun_timeline_approved=True,
                       personal_prediction=True)
        markers = {m["dimension"]: m for m in build((sc, cra, prov, reading))}
        for dimension in ("cross_rule_synthesis", "strength_classification",
                          "dayun_timeline", "personal_evaluation"):
            self.assertEqual(markers[dimension]["condition"], "available",
                             dimension)
            self.assertEqual(markers[dimension]["statement"], AVAILABLE,
                             dimension)
            self.assertIsNone(markers[dimension]["reason_category"], dimension)

    def test_missing_structural_evidence_marks_structure_not_available(self):
        sc, cra, prov, reading = current_facts()
        markers = _life_condition_markers(
            strength_context=sc, cross_rule_audit=cra,
            integration_provenance=prov, integrated_reading=reading,
            annual_career_evidence_ids=[], spouse_evidence_ids=[])
        by_dim = {m["dimension"]: m for m in markers}
        for dimension in ("annual_career", "annual_romance"):
            self.assertEqual(by_dim[dimension]["condition"], "not_available")
            self.assertEqual(by_dim[dimension]["statement"], NOT_AVAILABLE)
            self.assertEqual(by_dim[dimension]["reason_category"],
                             "source_identity_unverified")

    def test_markers_carry_no_scores_predictions_or_rule_identifiers(self):
        markers = build()
        blob = str(markers)
        for forbidden in ("score", "评分", "fortune", "bazi.phase2", "rule_id"):
            self.assertNotIn(forbidden, blob)
        for m in markers:
            self.assertNotIn("prediction", m)
            self.assertEqual(
                set(m), {"dimension", "label", "condition", "statement",
                         "reason_category", "reason", "scope", "exit_text",
                         "basis", "evidence_ids"})


if __name__ == "__main__":
    unittest.main()
