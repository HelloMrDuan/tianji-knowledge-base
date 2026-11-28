"""Lane D (TJ-0427, TJ-031.19) compatibility presentation tests.

Two classes, honestly separated:

* ``CompatibilityPresentationPlumbingTests``: pure-local, no sealed
  data. They run the pure builder against a SYNTHETIC compatibility
  result fixture (explicitly labelled synthetic below -- it is NOT a
  real chart and no Golden assertion is made from it): closed shape,
  per-section basis / caliber / undecided-conditions, the no-score /
  no-percentage scan, 刑 reported not_evaluated, validator accept /
  reject, and fail-closed behaviour.
* ``LiveCompatibilityPresentationTests``: real charts -- person A is
  f2 (2024-02-11T16:27:07+08:00, the pair used in the batch-4
  equivalence checks) and person B is 1995-06-15T08:30:00+08:00.
  They run the end-to-end builder and check the presentation's
  structure facts against a fresh ``_compatibility`` scenario run.
  The public checkout has no sealed ``data/``, so ``execute`` raises
  ``RuntimeUnavailable`` there and the whole class skips (never a
  faked pass); it runs for real in the sealed assembly environment.
"""

import copy
import json
import unittest

from tianji_kb import compatibility_presentation as cp
from tianji_kb.bazi_branch_punishment import PUNISHMENT_TABLE
from tianji_kb.compatibility_presentation import (
    build_compatibility_presentation,
    build_compatibility_presentation_for_births,
    is_valid_compatibility_presentation,
)

F2_BIRTH = "2024-02-11T16:27:07+08:00"
F2_GANZHI = ["甲辰", "丙寅", "乙巳", "甲申"]
B_BIRTH = "1995-06-15T08:30:00+08:00"

# Tokens that must never appear anywhere in a presentation object.
BANNED_TOKENS = (
    "%", "％", "percent", "score",
    "评分", "分数", "打分", "适配度", "匹配度", "契合度",
    "缘分指数", "缘分值", "compatibility score",
)


def _synthetic_pillars(ganzhi_list):
    """SYNTHETIC plumbing fixture: four pillars in scenario shape.

    NOT a real chart -- only the fields the builder reads. No Golden
    assertion is ever made from this fixture.
    """
    pillars = []
    for name, ganzhi in zip(("year", "month", "day", "hour"),
                            ganzhi_list):
        pillars.append({
            "name": name,
            "ganzhi": ganzhi,
            "stem": {"value": ganzhi[0], "ten_god": "比肩"},
            "branch": {"value": ganzhi[1], "hidden_stems": []},
        })
    return pillars


def _synthetic_compatibility_result():
    """SYNTHETIC compatibility result in ``_compatibility`` shape."""
    return {
        "report_version": "compatibility-structure-v5",
        "person_a": {
            "pillars": _synthetic_pillars(F2_GANZHI),
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
            "xianchi_targets": {"year_branch": "酉",
                                "day_branch": "午"},
            "spouse_palace": {"day_branch": "巳"},
            "natal_triple_harmonies": [],
            "traditional_spouse_star_lens": None,
        },
        "person_b": {
            "pillars": _synthetic_pillars(
                ["乙亥", "壬午", "丁酉", "丁未"]),
            "day_master": {"stem": "丁", "element": "火",
                           "polarity": "阴"},
            "xianchi_targets": {"year_branch": "酉",
                                "day_branch": "午"},
            "spouse_palace": {"day_branch": "酉"},
            "natal_triple_harmonies": [],
            "traditional_spouse_star_lens": None,
        },
        "day_master_relations": {
            "a_sees_b": {"subject_day_master": "乙",
                         "other_day_master": "丁",
                         "ten_god": "食神"},
            "b_sees_a": {"subject_day_master": "丁",
                         "other_day_master": "乙",
                         "ten_god": "偏印"},
        },
        "xianchi_cross_matches": {
            "a_targets_vs_b": {"targets": {"year_branch": "酉",
                                           "day_branch": "午"},
                               "other_branches": {
                                   "year_branch": "亥",
                                   "day_branch": "酉"},
                               "matches": []},
            "b_targets_vs_a": {"targets": {"year_branch": "酉",
                                           "day_branch": "午"},
                               "other_branches": {
                                   "year_branch": "辰",
                                   "day_branch": "巳"},
                               "matches": []},
        },
        "reviewed_cross_relations": {
            "day_master_five_combination": {
                "matched": False, "stems": ["乙", "丁"],
                "traditional_result_element": None},
            "spouse_palace_relation": {
                "person_a_day_branch": "巳",
                "person_b_day_branch": "酉",
                "relations": [{"kind": "six_harmony",
                               "branches": ["巳", "酉"],
                               "traditional_result_element": "金"}]},
        },
        # The fixture matrix carries the cross-pillar row the builder
        # reads (derived_from_rule_ids only -- the builder translates
        # each matrix hit's rule id through this first-encounter
        # mapping); the row's facts are not read here.
        "relation_evidence_matrix": [
            {
                "id": "cross-pillar-relation-matrix",
                "label": "双方四柱跨柱关系矩阵",
                "scope": "cross",
                "status": "matched",
                "facts": {},
                "derived_from_rule_ids": [
                    "bazi.phase2.stem_five_combinations",
                    "bazi.phase2.branch_six_harmonies",
                    "bazi.phase2.branch_six_harms",
                    "bazi.phase2.branch_six_clashes",
                ],
                "evidence_ids": [],
                "interpretation_allowed": False,
            },
        ],
        "cross_relation_matrix": {
            "hits": [{"tier": "core",
                      "relation_type": "six_harmony",
                      "rule_id": "bazi.phase2.branch_six_harmonies",
                      "person_a_pillar": "day",
                      "person_b_pillar": "day",
                      "branches": ["巳", "酉"],
                      "traditional_result_element": "金"}],
            "summary": {"core": 1, "day_context": 0, "supplemental": 0,
                        "stem_five_combination": 0, "six_harmony": 1,
                        "harm": 0, "clash": 0},
            "tier_policy": {"core": "双方日柱直接关系",
                            "day_context": "一方日柱与另一方其他柱关系",
                            "supplemental": "双方其他柱之间的辅助结构"},
            "interpretation_allowed": False,
        },
        "release_scope": "two_person_structure_only",
    }


def _synthetic_natal_relations():
    """SYNTHETIC within-chart relations in ``reviewed_relations`` shape.

    NOT real chart facts -- plumbing fixture only.
    """
    return {
        "stem_five_combinations": [{
            "pillars": ["year", "day"],
            "stems": ["甲", "乙"],
            "traditional_result_element": None}],
        "branch_six_harmonies": [{
            "pillars": ["month", "hour"],
            "branches": ["寅", "申"],
            "traditional_result_element": "水"}],
        "branch_six_harms": [],
        "branch_six_clashes": [{
            "pillars": ["day", "hour"],
            "branches": ["巳", "申"]}],
        "branch_triple_harmonies": [],
        "spouse_palace": {"pillar": "day", "day_branch": "巳",
                          "label": "日支（传统配偶宫结构位）"},
    }


def _synthetic_bundle():
    """SYNTHETIC person bundle: not_judgeable reviewed presentations."""
    return {
        "birth_value": F2_BIRTH,
        "zone": None,
        "traditional_role": None,
        "profile_result": {
            "strength_presentation": {
                "variant": "strength-public-presentation-v1",
                "status": "not_judgeable",
                "day_master": "乙",
                "month_branch": "寅",
                "scope_statement": "仅限已审局部形态。",
                "limitations": ["只呈现已审局部形态。"],
                "reason": "no_predicate_matched",
            },
            "pattern_presentation": {
                "variant": "pattern-public-presentation-v1",
                "title": "任氏寅月真格",
                "status": "not_judgeable",
                "day_master": "乙",
                "month_branch": "寅",
                "scope_statement": "仅限寅月。",
                "limitations": ["只呈现白名单格名。"],
                "reason": "pattern_name_not_public",
            },
            "xiyong_presentation": {
                "variant": "xiyong-public-presentation-v1",
                "presentation_scope": "phase-1",
                "day_master": "乙",
                "month_branch": "寅",
                "blocks": {"tiaohou": {"system": "tiaohou",
                                        "source_label": "调候",
                                        "state": "presented",
                                        "lines": ["调候取用顺序。"]},
                           "bingyao": {"system": "bingyao",
                                       "source_label": "病药",
                                       "state": "presented",
                                       "lines": ["病药对子。"]}},
                "relations": [],
                "relations_closing_line": "不作统一裁决。",
                "unified_verdict": None,
                "public_enabled": True,
                "ai_enabled": False,
                "scope_statement": "仅限 phase-1。",
                "limitations": ["统一裁决恒为无结论。"],
            },
        },
        "dayun_first_period": None,
    }


def _assert_no_banned_tokens(testcase, presentation):
    text = json.dumps(presentation, ensure_ascii=False)
    for token in BANNED_TOKENS:
        testcase.assertNotIn(
            token, text,
            "banned scoring token in presentation: " + token)


class CompatibilityPresentationPlumbingTests(unittest.TestCase):
    """Pure-local builder tests on the synthetic fixture."""

    def test_builder_returns_valid_presentation(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            person_a=_synthetic_bundle(),
            person_b=_synthetic_bundle())
        self.assertTrue(is_valid_compatibility_presentation(presentation))
        self.assertEqual(presentation["presentation_version"],
                         "compatibility-presentation-v1")
        self.assertEqual(presentation["scenario_id"], "compatibility")
        self.assertIs(presentation["interpretation_allowed"], False)
        self.assertIsNone(presentation["unified_verdict"])
        self.assertEqual(
            presentation["compatibility_inference"]["status"],
            "not_available")

    def test_sections_carry_basis_caliber_and_undecided(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            person_a=_synthetic_bundle(),
            person_b=_synthetic_bundle())
        self.assertEqual(
            [s["id"] for s in presentation["sections"]],
            ["charts", "relations", "patterns_and_xiyong", "dayun",
             "inference_boundary"])
        for section in presentation["sections"]:
            self.assertIsInstance(section["basis"], str)
            self.assertTrue(section["basis"])
            self.assertIn(section["caliber"], (
                "structure_fact", "reviewed_public_presentation",
                "boundary_statement"))
            self.assertIsInstance(section["undecided_conditions"], list)
            self.assertTrue(section["undecided_conditions"])
            for item in section["undecided_conditions"]:
                self.assertIsInstance(item, str)
                self.assertTrue(item)

    def test_charts_match_the_input_result(self):
        result = _synthetic_compatibility_result()
        presentation = build_compatibility_presentation(result)
        charts = presentation["sections"][0]["facts"]
        self.assertEqual(
            [p["ganzhi"] for p in charts["person_a"]["pillars"]],
            F2_GANZHI)
        self.assertEqual(charts["person_a"]["day_master"]["stem"], "乙")
        self.assertEqual(charts["person_b"]["day_master"]["stem"], "丁")

    def test_relations_copy_the_scenario_facts(self):
        result = _synthetic_compatibility_result()
        presentation = build_compatibility_presentation(
            result,
            natal_relations={
                "person_a": _synthetic_natal_relations(),
                "person_b": _synthetic_natal_relations()})
        facts = presentation["sections"][1]["facts"]
        self.assertEqual(
            facts["mutual_ten_gods"]["a_sees_b"]["ten_god"], "食神")
        self.assertEqual(
            facts["mutual_ten_gods"]["b_sees_a"]["ten_god"], "偏印")
        self.assertIs(
            facts["day_master_five_combination"]["matched"], False)
        self.assertEqual(
            facts["spouse_palace_day_branch_relation"]
            ["relations"][0]["kind"], "six_harmony")
        self.assertEqual(
            facts["cross_pillar_relation_matrix"]["summary"]["core"], 1)
        self.assertEqual(
            facts["cross_pillar_relation_matrix"]["summary"]
            ["six_harmony"], 1)

    def test_natal_relations_pass_through(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            natal_relations={
                "person_a": _synthetic_natal_relations(),
                "person_b": _synthetic_natal_relations()})
        natal = presentation["sections"][1]["facts"]["natal_relations"]
        self.assertEqual(
            natal["person_a"]["branch_six_clashes"][0]["branches"],
            ["巳", "申"])
        self.assertEqual(
            natal["person_b"]["stem_five_combinations"][0]["stems"],
            ["甲", "乙"])
        self.assertEqual(natal["person_a"]["branch_six_harms"], [])

    def test_natal_relations_absent_reports_not_provided(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result())
        natal = presentation["sections"][1]["facts"]["natal_relations"]
        self.assertEqual(natal["person_a"]["status"], "not_provided")
        self.assertEqual(natal["person_b"]["status"], "not_provided")
        self.assertTrue(is_valid_compatibility_presentation(presentation))

    def test_natal_relations_malformed_fails_closed(self):
        broken = _synthetic_natal_relations()
        del broken["branch_six_harms"]
        with self.assertRaises(ValueError):
            build_compatibility_presentation(
                _synthetic_compatibility_result(),
                natal_relations={"person_a": broken})

    def test_no_score_or_percentage_anywhere(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            person_a=_synthetic_bundle(),
            person_b=_synthetic_bundle())
        _assert_no_banned_tokens(self, presentation)

    def test_punishment_is_not_evaluated(self):
        self.assertIsNone(PUNISHMENT_TABLE)
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result())
        punishment = presentation["sections"][1]["facts"]["punishment"]
        self.assertEqual(punishment["status"], "not_evaluated")
        self.assertIn("刑表不存在", punishment["reason"])

    def test_punishment_table_registration_fails_closed(self):
        original = cp.PUNISHMENT_TABLE
        cp.PUNISHMENT_TABLE = {"子": ["卯"]}
        try:
            with self.assertRaises(ValueError):
                build_compatibility_presentation(
                    _synthetic_compatibility_result())
        finally:
            cp.PUNISHMENT_TABLE = original

    def test_missing_person_bundle_reports_not_provided(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result())
        pattern_b = presentation["sections"][2]["facts"]["person_b"]
        self.assertEqual(pattern_b["pattern"]["status"], "not_provided")
        self.assertEqual(pattern_b["xiyong"]["status"], "not_provided")
        self.assertEqual(pattern_b["strength"]["status"], "not_provided")
        dayun = presentation["sections"][3]["facts"]
        self.assertEqual(dayun["person_a"]["status"], "not_provided")
        self.assertEqual(dayun["periods_opened"], "first_only")

    def test_xiyong_unified_verdict_must_stay_none(self):
        bundle = _synthetic_bundle()
        bundle["profile_result"]["xiyong_presentation"][
            "unified_verdict"] = "甲木"
        with self.assertRaises(ValueError):
            build_compatibility_presentation(
                _synthetic_compatibility_result(), person_a=bundle)

    def test_validator_rejects_tampered_presentations(self):
        good = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            person_a=_synthetic_bundle(),
            person_b=_synthetic_bundle())
        self.assertTrue(is_valid_compatibility_presentation(good))
        tampered = copy.deepcopy(good)
        tampered["unified_verdict"] = "some verdict"
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        tampered = copy.deepcopy(good)
        tampered["sections"][1]["facts"]["punishment"]["status"] = \
            "evaluated"
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        tampered = copy.deepcopy(good)
        tampered["sections"][3]["facts"]["periods_opened"] = "all"
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        tampered = copy.deepcopy(good)
        tampered["sections"][1]["facts"]["natal_relations"][
            "person_a"] = {"stem_five_combinations": "not-a-list"}
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        tampered = copy.deepcopy(good)
        tampered["limitations"].append("缘分 98%")
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        tampered = copy.deepcopy(good)
        tampered["sections"] = tampered["sections"][:4]
        self.assertFalse(is_valid_compatibility_presentation(tampered))
        self.assertFalse(is_valid_compatibility_presentation(None))
        self.assertFalse(is_valid_compatibility_presentation({}))

    def test_builder_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            build_compatibility_presentation({})
        with self.assertRaises(ValueError):
            build_compatibility_presentation(None)
        broken = _synthetic_compatibility_result()
        del broken["cross_relation_matrix"]
        with self.assertRaises(ValueError):
            build_compatibility_presentation(broken)

    def test_presentation_is_jsonable(self):
        presentation = build_compatibility_presentation(
            _synthetic_compatibility_result(),
            person_a=_synthetic_bundle(),
            person_b=_synthetic_bundle())
        round_tripped = json.loads(
            json.dumps(presentation, ensure_ascii=False))
        self.assertTrue(is_valid_compatibility_presentation(
            round_tripped))


class LiveCompatibilityPresentationTests(unittest.TestCase):
    """Real-chart checks (f2 + 1995-06-15). Skipped without sealed data."""

    def _live_presentation(self, with_roles):
        try:
            from tianji_kb.runtime_catalog import RuntimeUnavailable
        except Exception as exc:  # noqa: BLE001 - no runtime, skip
            raise unittest.SkipTest(
                "runtime catalog unavailable: %s" % exc)
        kwargs = {}
        if with_roles:
            kwargs["person_a_traditional_role"] = "male"
            kwargs["person_b_traditional_role"] = "female"
        try:
            return build_compatibility_presentation_for_births(
                F2_BIRTH, B_BIRTH, **kwargs)
        except RuntimeUnavailable as exc:
            raise unittest.SkipTest(
                "sealed runtime unavailable locally: %s" % exc)

    def _live_compatibility_result(self):
        try:
            from tianji_kb.runtime_catalog import RuntimeUnavailable
            from tianji_kb.scenario_engine import execute_scenario
        except Exception as exc:  # noqa: BLE001 - no runtime, skip
            raise unittest.SkipTest(
                "runtime catalog unavailable: %s" % exc)
        try:
            return execute_scenario("compatibility", {
                "person_a_birth_value": F2_BIRTH,
                "person_b_birth_value": B_BIRTH,
            })["result"]
        except RuntimeUnavailable as exc:
            raise unittest.SkipTest(
                "sealed runtime unavailable locally: %s" % exc)

    def test_live_charts_are_the_real_pair(self):
        presentation = self._live_presentation(with_roles=False)
        self.assertTrue(is_valid_compatibility_presentation(presentation))
        charts = presentation["sections"][0]["facts"]
        self.assertEqual(
            [p["ganzhi"] for p in charts["person_a"]["pillars"]],
            F2_GANZHI)
        self.assertEqual(charts["person_a"]["day_master"]["stem"], "乙")
        self.assertEqual(charts["person_b"]["day_master"]["stem"], "丁")

    def test_live_relations_match_the_scenario_output(self):
        presentation = self._live_presentation(with_roles=False)
        result = self._live_compatibility_result()
        facts = presentation["sections"][1]["facts"]
        self.assertEqual(
            facts["mutual_ten_gods"],
            result["day_master_relations"])
        self.assertEqual(
            facts["day_master_five_combination"],
            result["reviewed_cross_relations"]
            ["day_master_five_combination"])
        self.assertEqual(
            facts["xianchi_cross_matches"],
            result["xianchi_cross_matches"])
        self.assertEqual(
            facts["cross_pillar_relation_matrix"]["summary"],
            result["cross_relation_matrix"]["summary"])
        # The presentation hits carry the public R aliases, not the
        # scenario's raw rule ids (same mapping the projection
        # assigns to the top-level matrix); everything else in each
        # hit is copied verbatim.
        from tianji_kb.compatibility_presentation import (
            _opaque_rule_aliases,
            _translated_matrix_hits,
        )
        aliases = _opaque_rule_aliases(result)
        self.assertEqual(
            facts["cross_pillar_relation_matrix"]["hits"],
            _translated_matrix_hits(result["cross_relation_matrix"],
                                    aliases))
        self.assertEqual(facts["punishment"]["status"], "not_evaluated")

    def test_live_natal_relations_match_the_chart_output(self):
        # Within-chart relations in the presentation must equal the
        # same persons' own bazi chart reviewed_relations, exactly.
        from tianji_kb.engine import execute
        from tianji_kb.runtime_catalog import RuntimeUnavailable
        presentation = self._live_presentation(with_roles=False)
        natal = presentation["sections"][1]["facts"]["natal_relations"]
        for key, birth in (("person_a", F2_BIRTH),
                           ("person_b", B_BIRTH)):
            try:
                chart = execute("bazi", {
                    "value": birth,
                    "include_xianchi": True,
                    "include_relations": True,
                })["result"]
            except RuntimeUnavailable as exc:
                raise unittest.SkipTest(
                    "sealed runtime unavailable locally: %s" % exc)
            reviewed = chart["reviewed_relations"]
            block = natal[key]
            for name in ("stem_five_combinations",
                         "branch_six_harmonies", "branch_six_harms",
                         "branch_six_clashes"):
                self.assertEqual(block[name], reviewed[name],
                                 "%s %s drifted" % (key, name))

    def test_live_no_score_or_percentage_anywhere(self):
        presentation = self._live_presentation(with_roles=True)
        _assert_no_banned_tokens(self, presentation)

    def test_live_person_b_pattern_is_not_judgeable(self):
        # Person B is born in 午月: outside the D-1 寅月 whitelist.
        presentation = self._live_presentation(with_roles=False)
        pattern_b = presentation["sections"][2]["facts"]["person_b"]
        pattern = pattern_b["pattern"]
        self.assertEqual(pattern["status"], "not_judgeable")
        self.assertEqual(pattern["reason"], "month_not_yin")
        self.assertIsNone(pattern.get("pattern"))

    def test_live_presentations_are_the_approved_gates(self):
        from tianji_kb.bazi_pattern_public import (
            is_valid_public_pattern_presentation,
        )
        from tianji_kb.bazi_profile_presentation import (
            strip_public_citation_ids,
        )
        from tianji_kb.bazi_strength_public import (
            is_valid_public_strength_presentation,
        )
        from tianji_kb.bazi_xiyong_public import (
            is_valid_public_presentation as is_valid_xiyong,
        )
        from tianji_kb.public_boundary import (
            find_public_boundary_violations,
        )
        from tianji_kb.scenario_engine import execute_scenario
        presentation = self._live_presentation(with_roles=False)
        self.assertEqual(find_public_boundary_violations(presentation), [])
        for key, birth in (("person_a", F2_BIRTH),
                           ("person_b", B_BIRTH)):
            person = presentation["sections"][2]["facts"][key]
            self.assertTrue(is_valid_public_strength_presentation(
                person["strength"]))
            self.assertTrue(is_valid_public_pattern_presentation(
                person["pattern"]))
            # The embedded xiyong is the citation-stripped form of
            # the standalone presentation: same reviewed content,
            # with the raw source / section references removed (they
            # are exempt only under a xiyong_presentation key, see
            # public_boundary.py). The standalone object itself
            # still validates as the approved gate.
            standalone = execute_scenario(
                "bazi-profile", {"value": birth})["result"][
                    "xiyong_presentation"]
            self.assertTrue(is_valid_xiyong(standalone))
            self.assertEqual(
                person["xiyong"],
                strip_public_citation_ids(standalone))
            self.assertIsNone(person["xiyong"]["unified_verdict"])

    def test_live_dayun_is_first_period_only(self):
        from tianji_kb.public_boundary import (
            find_public_boundary_violations,
        )
        presentation = self._live_presentation(with_roles=True)
        self.assertEqual(find_public_boundary_violations(presentation), [])
        dayun = presentation["sections"][3]["facts"]
        self.assertEqual(dayun["periods_opened"], "first_only")
        for key in ("person_a", "person_b"):
            first = dayun[key]
            # The embedded copy is the citation-stripped form of the
            # trimmed dayun presentation (same treatment as the
            # bazi-profile builder's embedded copy): the full
            # validated object is verified upstream by the trim
            # helper, and the embedded copy must carry no raw source
            # / section reference (pinned by the boundary scan
            # above, not by the dayun validator, which requires the
            # reviewed citation fields).
            sanming = first["methods"]["sanming"]
            self.assertEqual(len(sanming["entries"]), 8)
            for entry in sanming["entries"][1:]:
                self.assertEqual(entry["state"], "unresolved")
                self.assertIsNone(entry["start_interval"])

    def test_live_dayun_without_roles_is_not_available(self):
        presentation = self._live_presentation(with_roles=False)
        dayun = presentation["sections"][3]["facts"]
        self.assertEqual(dayun["person_a"]["status"], "not_available")
        self.assertEqual(dayun["person_b"]["status"], "not_available")


if __name__ == "__main__":
    unittest.main()
