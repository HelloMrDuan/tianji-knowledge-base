"""TJ-031.19 (E0427) Lane C: romance presentation builder tests.

Two classes, honestly separated (batch-4 pattern):

* ``RomancePresentationLocalTests``: pure-local, no sealed data. The
  builder is exercised against a synthetic ``_romance``-shaped envelope
  fixture -- explicitly a plumbing fixture modelled on the repo's own
  frontend stub values (2000-01-07 chart, 2026 target year), NOT a
  real chart; it makes no Golden claim. It covers section shape,
  fact fidelity to the envelope, the no-role / no-candidates /
  no-pair-hits branches, and the fail-closed checks (banned
  prediction/scoring wording, internal fields, drift rejection,
  input immutability, determinism, closed-shape validation).
* ``RomancePresentationLiveTests``: real-chart checks against f2
  (2024-02-11T16:27:07+08:00, 甲辰 / 丙寅 / 乙巳 / 甲申). They run
  only where the sealed runtime exists; in a public checkout without
  ``data/`` (``execute("bazi")`` raises ``RuntimeUnavailable``) the
  whole class skips -- it never fabricates a pass. Live assertions
  compare the presentation against the SAME request's ``_romance``
  envelope field by field (the builder must mirror the existing
  builder's outputs), plus the f2 pillars pinned by the batch-4
  unified-compute docstring, plus the banned-word sweep.
"""

import copy
import json
import unittest

from tianji_kb.romance_presentation import (
    LIMITATIONS,
    NO_INFERENCE_STATEMENT,
    SCOPE_STATEMENT,
    VARIANT,
    build_romance_presentation,
    build_romance_presentation_for,
    is_valid_romance_presentation,
)

F2_BIRTH = "2024-02-11T16:27:07+08:00"
F2_GANZHI = ["甲辰", "丙寅", "乙巳", "甲申"]

BANNED_SUBSTRINGS = (
    "婚期", "正缘", "脱单", "桃花运", "桃花指数", "评分", "得分",
    "吉凶", "注定", "红鸾", "天喜", "一定会", "必然",
    "会结婚", "将结婚", "适合结婚", "最佳婚期",
)


def _fixture_envelope(traditional_role=None, pairing_state="paired"):
    """Synthetic _romance-shaped envelope (plumbing fixture, not a real chart).

    Values mirror the repo's own frontend stub (b028) chart
    己卯 / 丁丑 / 甲子 / 庚午, day branch 子, 2026 丙午, 子午六冲 --
    except the stub's natal_matches, which do not follow the real
    lookup: the year-branch target 子 sits on the DAY pillar (甲子),
    and the day-branch target 酉 has no pillar at all, so the real
    lookup yields exactly one match (year basis, day pillar).
    Hidden stems follow the standard branch tables against day stem 甲
    (卯藏乙比肩；丑藏己正财、癸正印、辛正官；子藏癸正印；
    午藏丁伤官、己正财), so the female-role hidden candidate (月柱藏干
    辛正官) and its 丑午六害 pairing are internally consistent.
    """
    envelope = {
        "scenario_id": "romance",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "limitations": ["structure facts only"],
        "result": {
            "release_scope": "xianchi_structure_only",
            "natal": {
                "pillars": [
                    {"name": "year", "ganzhi": "己卯",
                     "stem": {"value": "己", "ten_god": "七杀"},
                     "branch": {"value": "卯",
                                "hidden_stems": [
                                    {"stem": "乙", "ten_god": "比肩"}]}},
                    {"name": "month", "ganzhi": "丁丑",
                     "stem": {"value": "丁", "ten_god": "食神"},
                     "branch": {"value": "丑",
                                "hidden_stems": [
                                    {"stem": "己", "ten_god": "正财"},
                                    {"stem": "癸", "ten_god": "正印"},
                                    {"stem": "辛", "ten_god": "正官"}]}},
                    {"name": "day", "ganzhi": "甲子",
                     "stem": {"value": "甲", "ten_god": "日主"},
                     "branch": {"value": "子",
                                "hidden_stems": [
                                    {"stem": "癸", "ten_god": "正印"}]}},
                    {"name": "hour", "ganzhi": "庚午",
                     "stem": {"value": "庚", "ten_god": "正官"},
                     "branch": {"value": "午",
                                "hidden_stems": [
                                    {"stem": "丁", "ten_god": "伤官"},
                                    {"stem": "己", "ten_god": "正财"}]}},
                ],
                "day_master": {"stem": "甲", "element": "木"},
            },
            "xianchi": {
                "targets": {"year_branch": "子", "day_branch": "酉"},
                "natal_matches": [
                    {"basis": "year_branch", "pillar": "day",
                     "target_branch": "子"},
                ],
                "source_warning": "年支与日支两个起查基准分别展示。",
            },
            "target_year": {"year": 2026, "ganzhi": "丙午", "branch": "午"},
            "target_year_activation": {
                "year_branch_basis": {"target_branch": "子",
                                      "target_year_branch": "午",
                                      "matched": False},
                "day_branch_basis": {"target_branch": "酉",
                                     "target_year_branch": "午",
                                     "matched": False},
            },
            "spouse_palace_year_relations": {
                "natal_day_branch": "子",
                "target_year_branch": "午",
                "pairs_checked": 1,
                "relations": [{"relation_type": "clash",
                               "natal_branch": "子", "flow_branch": "午",
                               "natal_pillar": "day"}],
                "interpretation_allowed": False,
            },
        },
    }
    if traditional_role is not None:
        positions = {"visible": [{"pillar": "hour", "stem": "庚",
                                  "ten_god": "正官"}],
                     "hidden": [{"pillar": "month", "branch": "丑",
                                 "stem": "辛", "ten_god": "正官"}]}
        if pairing_state == "no_candidates":
            positions = {"visible": [], "hidden": []}
        pairings = []
        if pairing_state == "paired":
            pairings = [{"position_kind": "visible", "pillar": "hour",
                         "branch": "午", "stem": "庚", "ten_god": "正官",
                         "relation": "same_branch", "rule_id": None,
                         "evidence_ids": []},
                        {"position_kind": "hidden", "pillar": "month",
                         "branch": "丑", "stem": "辛", "ten_god": "正官",
                         "relation": "harm",
                         "rule_id": "bazi.phase2.branch_six_harms",
                         "evidence_ids": []}]
        envelope["result"]["spouse_star_year_pairing"] = {
            "traditional_role": traditional_role,
            "candidate_ten_gods": ["正官", "七杀"],
            "candidate_positions": positions,
            "target_year": {"year": 2026, "ganzhi": "丙午",
                            "stem": "丙", "branch": "午"},
            "pairs_checked": len(positions["visible"]) + len(positions["hidden"]),
            "pairings": pairings,
            "pairing_state": pairing_state,
            "interpretation_allowed": False,
        }
    return envelope


def _section(presentation, section_id):
    return next(s for s in presentation["sections"] if s["id"] == section_id)


def _fact(section, label):
    return next(f for f in section["facts"] if f["label"] == label)


class RomancePresentationLocalTests(unittest.TestCase):
    def test_three_sections_in_order_with_structure_caliber(self):
        presentation = build_romance_presentation(_fixture_envelope())
        self.assertEqual(presentation["variant"], VARIANT)
        self.assertEqual(presentation["scenario_id"], "romance")
        self.assertEqual(presentation["status"], "structure_only")
        self.assertEqual(presentation["caliber"], "structure_only")
        self.assertEqual(
            [s["id"] for s in presentation["sections"]],
            ["peach_blossom_spouse_star_palace",
             "natal_marriage_structure", "dayun_liunian_linkage"])
        for section in presentation["sections"]:
            self.assertEqual(section["caliber"], "structure_only")
            self.assertTrue(section["basis"])
            self.assertTrue(section["facts"])
            self.assertTrue(section["undecided"])
            for item in section["undecided"]:
                self.assertTrue(item["item"])
                self.assertTrue(item["reason"])
        self.assertTrue(is_valid_romance_presentation(presentation))

    def test_section_one_facts_match_envelope(self):
        presentation = build_romance_presentation(_fixture_envelope())
        section = _section(presentation, "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "年支基准咸池目标")["value"], "子")
        self.assertEqual(_fact(section, "日支基准咸池目标")["value"], "酉")
        self.assertEqual(_fact(section, "年支基准原局命中")["value"],
                         "日柱（地支 子）")
        self.assertEqual(_fact(section, "日支基准原局命中")["value"],
                         "未见结构命中")
        self.assertEqual(
            _fact(section, "2026 年流年地支（年支基准）")["value"],
            "未命中目标支 子")
        self.assertEqual(_fact(section, "夫妻宫位置")["value"], "日支 子")
        self.assertEqual(
            _fact(section, "日支 × 2026 年流年地支")["value"], "六冲（子 ↔ 午）")
        self.assertIn("bazi.phase2.xianchi_lookup", section["basis_rules"])
        self.assertIn("bazi.phase2.spouse_palace_day_branch",
                      section["basis_rules"])

    def test_section_two_natal_structure_matches_envelope(self):
        presentation = build_romance_presentation(_fixture_envelope())
        section = _section(presentation, "natal_marriage_structure")
        self.assertEqual(_fact(section, "年柱")["value"], "己卯（己 · 七杀）")
        self.assertEqual(_fact(section, "日柱")["value"], "甲子（甲 · 日主）")
        self.assertEqual(_fact(section, "日主")["value"], "甲（木）")
        self.assertEqual(_fact(section, "夫妻宫位置")["value"], "日支 子")
        self.assertEqual(_fact(section, "年柱藏干（卯）")["value"], "乙（比肩）")
        self.assertEqual(_fact(section, "月柱藏干（丑）")["value"],
                         "己（正财）、癸（正印）、辛（正官）")
        self.assertEqual(_fact(section, "日柱藏干（子）")["value"], "癸（正印）")
        self.assertEqual(_fact(section, "时柱藏干（午）")["value"],
                         "丁（伤官）、己（正财）")
        self.assertIn("己卯、丁丑、甲子、庚午", section["summary"])
        self.assertEqual(len(section["undecided"]), 1)
        self.assertIn("暂不可判", section["undecided"][0]["reason"])

    def test_section_three_liunian_facts_and_dayun_undecided(self):
        presentation = build_romance_presentation(_fixture_envelope())
        section = _section(presentation, "dayun_liunian_linkage")
        self.assertEqual(_fact(section, "目标年")["value"],
                         "2026 年 丙午（流年地支 午）")
        self.assertEqual(_fact(section, "咸池目标年激活")["value"],
                         "两个基准均未命中")
        self.assertEqual(_fact(section, "夫妻宫 × 流年")["value"],
                         "六冲（子 ↔ 午）")
        dayun = next(u for u in section["undecided"]
                     if u["item"] == "大运与婚姻结构的联动")
        self.assertIn("暂不可判", dayun["reason"])
        self.assertIn("不计算大运", dayun["reason"])
        marriage_year = next(u for u in section["undecided"]
                             if u["item"] == "结婚年份或具体时间")
        self.assertIn("不作此类推断", marriage_year["reason"])

    def test_no_role_pairing_is_explicitly_undecided_not_silent(self):
        presentation = build_romance_presentation(_fixture_envelope())
        section = _section(presentation, "peach_blossom_spouse_star_palace")
        self.assertFalse(any("配偶星" in f["label"]
                             for f in section["facts"]))
        undecided = next(u for u in section["undecided"]
                         if u["item"] == "配偶星候选位置与流年配对")
        self.assertIn("未启用传统配偶星口径", undecided["reason"])
        self.assertNotIn("bazi.phase2.spouse_star_lens",
                         section["basis_rules"])

    def test_female_role_pairing_facts_match_envelope(self):
        presentation = build_romance_presentation(
            _fixture_envelope(traditional_role="female"))
        section = _section(presentation, "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "传统配偶星口径")["value"],
                         "传统女命口径 · 看官杀")
        self.assertEqual(_fact(section, "传统口径候选十神")["value"],
                         "正官、七杀")
        self.assertEqual(_fact(section, "配偶星候选位置")["value"],
                         "显干 1 处、藏干 1 处，共核对 2 个候选位置")
        # Every candidate position is listed, paired or not.
        self.assertEqual(_fact(section, "配偶星候选位置 · 时柱显干")["value"],
                         "庚（正官）")
        self.assertEqual(_fact(section, "配偶星候选位置 · 月柱藏干")["value"],
                         "辛（正官）")
        self.assertEqual(_fact(section, "配偶星 × 2026 年流年干支")["value"],
                         "时柱显干 庚（正官）：地支相同、"
                         "月柱藏干 辛（正官）：六害")
        self.assertIn("bazi.phase2.spouse_star_lens",
                      section["basis_rules"])
        linkage = _section(presentation, "dayun_liunian_linkage")
        self.assertEqual(_fact(linkage, "配偶星 × 流年")["value"],
                         "命中 2 处配对")

    def test_six_harmony_carries_result_element_and_unassessed_effect(self):
        envelope = _fixture_envelope()
        envelope["result"]["target_year"] = {"year": 2021, "ganzhi": "辛丑",
                                             "branch": "丑"}
        envelope["result"]["target_year_activation"] = {
            "year_branch_basis": {"target_branch": "子",
                                  "target_year_branch": "丑",
                                  "matched": False},
            "day_branch_basis": {"target_branch": "酉",
                                 "target_year_branch": "丑",
                                 "matched": False},
        }
        envelope["result"]["spouse_palace_year_relations"] = {
            "natal_day_branch": "子", "target_year_branch": "丑",
            "pairs_checked": 1,
            "relations": [{"relation_type": "six_harmony",
                           "natal_branch": "子", "flow_branch": "丑",
                           "natal_pillar": "day",
                           "traditional_result_element": "土",
                           "transformation_effectiveness_assessed": False}],
            "interpretation_allowed": False,
        }
        presentation = build_romance_presentation(envelope)
        section = _section(presentation, "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "日支 × 2021 年流年地支")["value"],
                         "六合（子 ↔ 丑；传统合化结果五行：土，合化效力未评估）")
        self.assertTrue(is_valid_romance_presentation(presentation))

    def test_no_candidates_and_no_pair_hits_are_named(self):
        no_candidates = build_romance_presentation(
            _fixture_envelope(traditional_role="male",
                              pairing_state="no_candidates"))
        section = _section(no_candidates, "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "传统配偶星口径")["value"],
                         "传统男命口径 · 看财星")
        self.assertEqual(_fact(section, "配偶星候选位置")["value"],
                         "显干 0 处、藏干 0 处，共核对 0 个候选位置")
        self.assertIn("未见候选十神位置",
                      json.dumps(section["undecided"], ensure_ascii=False))
        no_hits = build_romance_presentation(
            _fixture_envelope(traditional_role="female",
                              pairing_state="no_pair_hits"))
        section = _section(no_hits, "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "配偶星 × 2026 年流年干支")["value"],
                         "未见配对命中")
        self.assertIn("未见天干、地支同一性",
                      json.dumps(section["undecided"], ensure_ascii=False))

    def test_no_prediction_or_scoring_text_anywhere(self):
        for role in (None, "female", "male"):
            presentation = build_romance_presentation(
                _fixture_envelope(traditional_role=role))
            serialized = json.dumps(presentation, ensure_ascii=False)
            for banned in BANNED_SUBSTRINGS:
                self.assertNotIn(banned, serialized,
                                 "banned wording %r in output" % banned)
            self.assertNotIn("evidence_ids", serialized)
            self.assertNotIn("trace", serialized)
            self.assertNotIn("production_limited", serialized)
            self.assertNotIn("rule_matches", serialized)
            self.assertNotIn("fortune_score", serialized)
            self.assertTrue(is_valid_romance_presentation(presentation))

    def test_global_undecided_states_no_approved_inference_output(self):
        presentation = build_romance_presentation(_fixture_envelope())
        self.assertEqual(len(presentation["undecided"]), 1)
        item = presentation["undecided"][0]
        self.assertEqual(item["reason"], NO_INFERENCE_STATEMENT)
        self.assertIn("目前没有已获批的桃花姻缘推理输出", item["reason"])
        self.assertEqual(presentation["scope_statement"], SCOPE_STATEMENT)
        self.assertEqual(presentation["limitations"], list(LIMITATIONS))
        self.assertEqual(presentation["natal"]["day_master_element"], "木")

    def test_builder_is_deterministic_and_does_not_mutate_input(self):
        envelope = _fixture_envelope(traditional_role="female")
        before = copy.deepcopy(envelope)
        first = build_romance_presentation(envelope)
        second = build_romance_presentation(envelope)
        self.assertEqual(first, second)
        self.assertEqual(envelope, before)

    def test_activation_flag_drift_fails_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["target_year_activation"]["year_branch_basis"]["matched"] = True
        with self.assertRaisesRegex(ValueError, "activation drifted"):
            build_romance_presentation(envelope)

    def test_day_branch_drift_fails_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["spouse_palace_year_relations"]["natal_day_branch"] = "丑"
        with self.assertRaisesRegex(ValueError, "day branch drifted"):
            build_romance_presentation(envelope)

    def test_interpretation_allowed_fails_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["spouse_palace_year_relations"]["interpretation_allowed"] = True
        with self.assertRaisesRegex(ValueError, "must not allow interpretation"):
            build_romance_presentation(envelope)

    def test_wrong_release_scope_and_scenario_fail_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["release_scope"] = "something_else"
        with self.assertRaisesRegex(ValueError, "release_scope"):
            build_romance_presentation(envelope)
        envelope = _fixture_envelope()
        envelope["scenario_id"] = "career"
        with self.assertRaisesRegex(ValueError, "not a romance scenario"):
            build_romance_presentation(envelope)

    def test_pairing_pairs_checked_drift_fails_closed(self):
        envelope = _fixture_envelope(traditional_role="female")
        envelope["result"]["spouse_star_year_pairing"]["pairs_checked"] = 9
        with self.assertRaisesRegex(ValueError, "pairs_checked drifted"):
            build_romance_presentation(envelope)

    def test_candidate_position_must_match_its_pillar(self):
        envelope = _fixture_envelope(traditional_role="female")
        visible = envelope["result"]["spouse_star_year_pairing"][
            "candidate_positions"]["visible"]
        visible[0]["stem"] = "辛"
        with self.assertRaisesRegex(
                ValueError, "visible spouse star position drifted"):
            build_romance_presentation(envelope)
        envelope = _fixture_envelope(traditional_role="female")
        hidden = envelope["result"]["spouse_star_year_pairing"][
            "candidate_positions"]["hidden"]
        hidden[0]["stem"] = "癸"
        with self.assertRaisesRegex(
                ValueError, "not a hidden stem of its pillar"):
            build_romance_presentation(envelope)

    def test_xianchi_match_branch_drift_fails_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["xianchi"]["natal_matches"][0]["target_branch"] = "酉"
        with self.assertRaisesRegex(ValueError, "target drifted"):
            build_romance_presentation(envelope)

    def test_six_harmony_without_result_element_fails_closed(self):
        envelope = _fixture_envelope()
        envelope["result"]["spouse_palace_year_relations"]["relations"] = [
            {"relation_type": "six_harmony", "natal_branch": "子",
             "flow_branch": "午", "natal_pillar": "day"}]
        with self.assertRaisesRegex(ValueError, "lacks its result element"):
            build_romance_presentation(envelope)

    def test_validator_rejects_tampered_presentations(self):
        presentation = build_romance_presentation(_fixture_envelope())
        self.assertTrue(is_valid_romance_presentation(presentation))
        tampered = copy.deepcopy(presentation)
        tampered["sections"][0]["facts"].append(
            {"label": "婚期", "value": "2027 年"})
        self.assertFalse(is_valid_romance_presentation(tampered))
        tampered = copy.deepcopy(presentation)
        tampered["extra_key"] = True
        self.assertFalse(is_valid_romance_presentation(tampered))
        tampered = copy.deepcopy(presentation)
        tampered["sections"] = tampered["sections"][:2]
        self.assertFalse(is_valid_romance_presentation(tampered))
        self.assertFalse(is_valid_romance_presentation(None))
        self.assertFalse(is_valid_romance_presentation("romance"))


def _skip_sealed(reason):
    raise unittest.SkipTest("sealed runtime unavailable: " + reason)


class RomancePresentationLiveTests(unittest.TestCase):
    """Real-chart checks on f2; skip entirely without the sealed runtime."""

    def _live_envelope(self, **inputs):
        try:
            from tianji_kb import scenario_engine
            from tianji_kb.runtime_catalog import RuntimeUnavailable
        except ImportError as exc:
            _skip_sealed("engine import failed: %s" % exc)
        try:
            return scenario_engine.execute_scenario("romance", inputs)
        except RuntimeUnavailable as exc:
            _skip_sealed(str(exc))
        except ImportError as exc:
            _skip_sealed("engine import failed: %s" % exc)

    def test_live_f2_presentation_mirrors_romance_builder(self):
        envelope = self._live_envelope(birth_value=F2_BIRTH,
                                       target_year=2026)
        presentation = build_romance_presentation(envelope)
        self.assertTrue(is_valid_romance_presentation(presentation))
        result = envelope["result"]
        self.assertEqual(
            [p["ganzhi"] for p in presentation["natal"]["pillars"]],
            F2_GANZHI)
        self.assertEqual(presentation["natal"]["day_master"], "乙")
        self.assertEqual(presentation["natal"]["day_master_element"], "木")
        self.assertEqual(presentation["natal"]["day_branch"], "巳")
        natal_section = _section(presentation, "natal_marriage_structure")
        day_hidden = _fact(natal_section, "日柱藏干（巳）")["value"]
        for expected in ("丙（伤官）", "庚（正官）", "戊（正财）"):
            self.assertIn(expected, day_hidden)
        self.assertEqual(presentation["target_year"], 2026)
        self.assertEqual(presentation["target_year_ganzhi"],
                         result["target_year"]["ganzhi"])
        section = _section(presentation,
                           "peach_blossom_spouse_star_palace")
        self.assertEqual(
            _fact(section, "年支基准咸池目标")["value"],
            result["xianchi"]["targets"]["year_branch"])
        self.assertEqual(
            _fact(section, "日支基准咸池目标")["value"],
            result["xianchi"]["targets"]["day_branch"])
        self.assertEqual(
            _fact(section, "夫妻宫位置")["value"],
            "日支 %s" % result["spouse_palace_year_relations"]["natal_day_branch"])
        palace_relations = result["spouse_palace_year_relations"]["relations"]
        palace_value = _fact(section, "日支 × 2026 年流年地支")["value"]
        if palace_relations:
            for relation in palace_relations:
                self.assertIn(relation["natal_branch"], palace_value)
                self.assertIn(relation["flow_branch"], palace_value)
        else:
            self.assertEqual(palace_value, "未命中已审六合、六冲、六害")
        serialized = json.dumps(presentation, ensure_ascii=False)
        for banned in BANNED_SUBSTRINGS:
            self.assertNotIn(banned, serialized)
        self.assertIn("目前没有已获批的桃花姻缘推理输出",
                      presentation["undecided"][0]["reason"])

    def test_live_f2_female_role_pairing_mirrors_envelope(self):
        envelope = self._live_envelope(birth_value=F2_BIRTH,
                                       target_year=2026,
                                       traditional_role="female")
        presentation = build_romance_presentation(envelope)
        self.assertTrue(is_valid_romance_presentation(presentation))
        pairing = envelope["result"]["spouse_star_year_pairing"]
        section = _section(presentation,
                           "peach_blossom_spouse_star_palace")
        self.assertEqual(_fact(section, "传统配偶星口径")["value"],
                         "传统女命口径 · 看官杀")
        self.assertEqual(_fact(section, "传统口径候选十神")["value"],
                         "、".join(pairing["candidate_ten_gods"]))
        self.assertEqual(
            _fact(section, "配偶星候选位置")["value"],
            "显干 %d 处、藏干 %d 处，共核对 %d 个候选位置" % (
                len(pairing["candidate_positions"]["visible"]),
                len(pairing["candidate_positions"]["hidden"]),
                pairing["pairs_checked"]))
        # Every candidate position is listed, paired or not.
        position_facts = [f for f in section["facts"]
                          if f["label"].startswith("配偶星候选位置 · ")]
        self.assertEqual(len(position_facts), pairing["pairs_checked"])
        linkage = _section(presentation, "dayun_liunian_linkage")
        self.assertEqual(
            _fact(linkage, "配偶星 × 流年")["value"],
            "命中 %d 处配对" % len(pairing["pairings"])
            if pairing["pairings"] else "未见配对命中")

    def test_live_f2_wrapper_builds_the_same_presentation(self):
        try:
            presentation = build_romance_presentation_for(
                F2_BIRTH, 2026)
        except ImportError as exc:
            _skip_sealed("engine import failed: %s" % exc)
        except Exception as exc:
            from tianji_kb.runtime_catalog import RuntimeUnavailable
            if isinstance(exc, RuntimeUnavailable):
                _skip_sealed(str(exc))
            raise
        envelope = self._live_envelope(birth_value=F2_BIRTH,
                                       target_year=2026)
        self.assertEqual(
            presentation,
            build_romance_presentation(envelope))


if __name__ == "__main__":
    unittest.main()
