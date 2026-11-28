"""TJ-0427 Lane B (career): plain-language career presentation tests.

Two tiers, same pattern as the other batch-5/4 lane tests:

* Synthetic fixtures (public checkout, no sealed data): the career
  result shape is hand-built from the f2 pillars (甲辰/丙寅/乙巳/甲申)
  with hand-derived Ten-God positions -- a plumbing fixture, NOT a
  Golden -- and the three lifted presentations plus the dayun
  presentation are minimal valid shapes built from the gate modules'
  own constants (strength/pattern not_judgeable, xiyong phase-1
  blocks, dayun via the real ``classical_direction`` + the real
  first-period trim). The combination block is the REAL
  ``combine()`` output for f2 (pure engine, no sealed data).
* Sealed real-chart tests: the same builder over the real
  ``execute_scenario("career", f2, 2026, male)`` envelope plus the
  real unified-compute combination block. They raise SkipTest when
  the sealed runtime is unavailable (public checkout) and never
  fabricate a pass.

Fail-closed coverage: full 8-period timeline (interval-only
precision, no fabricated start ages), trimmed-field leak rejection,
combination-sequence drift, overall_effect leak, invalid/forged
lifts, banned age/date/score keys, no fortune judgment derived from
strength scores or fuyi candidates, uncomputable parts stated as
undecided in Chinese, and the closed-shape validator + allowlist
projection.
"""

import copy
import json
import unittest

from tianji_kb.bazi_combination_engine import combine
from tianji_kb.bazi_dayun_classical import (
    CONVERSION_VARIANT,
    SHENFENG_CONVERSION_VARIANT,
    classical_direction,
)
from tianji_kb.bazi_dayun_public import (
    EXPECTED_CHAIN,
    LIMITATIONS as DAYUN_LIMITATIONS,
    ROLE_SELECTION,
    RULES as DAYUN_RULES,
    SCOPE as DAYUN_SCOPE,
    SEQUENCE_DISCLOSURE,
    VALIDATION_RECORD,
    VARIANT as DAYUN_VARIANT,
    _METHOD_OPTIONS as DAYUN_METHOD_OPTIONS,
    _NOTICE_TEXTS as DAYUN_NOTICE_TEXTS,
)
from tianji_kb.bazi_dayun_timeline_view import (
    SANMING_APPLIED_SOURCE_ID,
    SHENFENG_SOURCE_ID,
)
from tianji_kb.bazi_pattern_public import (
    LIMITATIONS as PATTERN_LIMITATIONS,
    SCOPE_STATEMENT as PATTERN_SCOPE,
    TITLE as PATTERN_TITLE,
    VARIANT as PATTERN_VARIANT,
)
from tianji_kb.bazi_strength_public import (
    LIMITATIONS as STRENGTH_LIMITATIONS,
    SCOPE_STATEMENT as STRENGTH_SCOPE,
    VARIANT as STRENGTH_VARIANT,
)
from tianji_kb.bazi_xiyong_public import (
    BINGYAO_SOURCE_ID,
    LIMITATIONS as XIYONG_LIMITATIONS,
    NO_UNIFIED_VERDICT_LINE,
    PAIR_IDS,
    PRESENTATION_SCOPE as XIYONG_SCOPE,
    SCOPE_STATEMENT as XIYONG_SCOPE_STATEMENT,
    TIAOHOU_SOURCE_ID,
    VARIANT as XIYONG_VARIANT,
)
from tianji_kb.career_presentation import (
    VARIANT,
    build_career_presentation,
    is_valid_career_presentation,
    to_public_career_presentation,
)
from tianji_kb.public_boundary import find_public_boundary_violations
from tianji_kb.scenario_engine import _first_period_dayun_for_career_life

F2_BIRTH = "2024-02-11T16:27:07+08:00"
F2_PILLARS = ["甲辰", "丙寅", "乙巳", "甲申"]
F2_DAYUN_8 = [
    {"candidate_ganzhi": "丁卯", "period_index": 1, "ten_god": "食神"},
    {"candidate_ganzhi": "戊辰", "period_index": 2, "ten_god": "正财"},
    {"candidate_ganzhi": "己巳", "period_index": 3, "ten_god": "偏财"},
    {"candidate_ganzhi": "庚午", "period_index": 4, "ten_god": "正官"},
    {"candidate_ganzhi": "辛未", "period_index": 5, "ten_god": "七杀"},
    {"candidate_ganzhi": "壬申", "period_index": 6, "ten_god": "正印"},
    {"candidate_ganzhi": "癸酉", "period_index": 7, "ten_god": "偏印"},
    {"candidate_ganzhi": "甲戌", "period_index": 8, "ten_god": "劫财"},
]
TARGET_YEAR = 2026

# Hand-derived Ten-God positions for f2 (day master 乙), standard
# hidden-stem tables (辰戊乙癸 / 寅甲丙戊 / 巳丙戊庚 / 申庚壬戊).
# Synthetic plumbing fixture only -- NOT a Golden; the sealed test
# below re-derives the same groups from the real envelope.
_F2_GROUPS = {
    # group_id: (label, ten_gods, five_element_relation, visible, hidden)
    "wealth": ("财星", ["正财", "偏财"], "我克", 0, [
        ("year", "hidden_stem", "戊", "正财"),
        ("month", "hidden_stem", "戊", "正财"),
        ("day", "hidden_stem", "戊", "正财"),
        ("hour", "hidden_stem", "戊", "正财"),
    ]),
    "authority": ("官杀", ["正官", "七杀"], "克我", 0, [
        ("day", "hidden_stem", "庚", "正官"),
        ("hour", "hidden_stem", "庚", "正官"),
    ]),
    "output": ("食伤", ["食神", "伤官"], "我生", 1, [
        ("month", "hidden_stem", "丙", "伤官"),
        ("day", "hidden_stem", "丙", "伤官"),
    ]),
    "resource": ("印星", ["正印", "偏印"], "生我", 0, [
        ("year", "hidden_stem", "癸", "偏印"),
        ("hour", "hidden_stem", "壬", "正印"),
    ]),
    "peers": ("比劫", ["比肩", "劫财"], "同我", 3, [
        ("year", "hidden_stem", "乙", "比肩"),
        ("month", "hidden_stem", "甲", "劫财"),
    ]),
}
_F2_VISIBLE = {
    "wealth": [], "authority": [],
    "output": [("month", "visible_stem", "丙", "伤官")],
    "resource": [],
    "peers": [("year", "visible_stem", "甲", "劫财"),
              ("day", "visible_stem", "乙", "比肩"),
              ("hour", "visible_stem", "甲", "劫财")],
}


def _synthetic_career_result(dayun=None):
    pillars = []
    for name, ganzhi in zip(("year", "month", "day", "hour"), F2_PILLARS):
        pillars.append({
            "name": name, "ganzhi": ganzhi,
            "stem": {"value": ganzhi[0], "ten_god": "比肩"},
            "branch": {"value": ganzhi[1], "hidden_stems": []},
        })
    groups = {}
    cards = []
    for group_id, (label, ten_gods, relation, _v, hidden) in \
            _F2_GROUPS.items():
        occurrences = [
            {"pillar": pillar, "layer": layer, "stem": stem,
             "ten_god": ten_god}
            for pillar, layer, stem, ten_god
            in _F2_VISIBLE[group_id] + hidden]
        visible = len(_F2_VISIBLE[group_id])
        groups[group_id] = {
            "label": label, "ten_gods": list(ten_gods),
            "occurrences": occurrences,
            "visible_count": visible, "hidden_count": len(hidden),
        }
        cards.append({
            "group_id": group_id, "label": label,
            "ten_gods": list(ten_gods),
            "five_element_relation": relation,
            "traditional_structure_definition": "合成夹具释义。",
            "natal_presence": "both_layers" if visible and hidden
                              else "visible_only" if visible
                              else "hidden_only",
            "visible_count": visible, "hidden_count": len(hidden),
            "observation": "合成夹具观察。",
            "target_year_stem_matches_group": group_id == "output",
            "target_year_note": None,
            "source_rule_ids": ["bazi.phase2.ten_gods",
                                "bazi.phase2.hidden_stems"],
            "evidence_ids": [],
            "interpretation_level":
                "reviewed_structural_relation_only",
            "personal_prediction": False,
        })
    result = {
        "natal": {
            "pillars": pillars,
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
        },
        "structure_groups": groups,
        "interpretation_cards": cards,
        "target_year": {
            "year": TARGET_YEAR, "ganzhi": "丙午", "stem": "丙",
            "branch": "午", "stem_ten_god": "伤官",
            "structure_group": "output",
            "structure_group_label": "食伤",
        },
        "strength_presentation": {
            "variant": STRENGTH_VARIANT, "status": "not_judgeable",
            "day_master": "乙", "month_branch": "寅",
            "scope_statement": STRENGTH_SCOPE,
            "limitations": list(STRENGTH_LIMITATIONS),
            "reason": "out_of_scope",
        },
        "pattern_presentation": {
            "variant": PATTERN_VARIANT, "title": PATTERN_TITLE,
            "status": "not_judgeable",
            "day_master": "乙", "month_branch": "寅",
            "scope_statement": PATTERN_SCOPE,
            "limitations": list(PATTERN_LIMITATIONS),
            "reason": "pilot_uncertain",
        },
        "xiyong_presentation": {
            "variant": XIYONG_VARIANT,
            "presentation_scope": XIYONG_SCOPE,
            "day_master": "乙", "month_branch": "寅",
            "blocks": {
                "tiaohou": {
                    "system": "tiaohou", "source_label": "《穷通宝鉴》",
                    "state": "not_judgeable",
                    "lines": ["合成夹具：调候未命中。"],
                    "evidence": {"source_id": TIAOHOU_SOURCE_ID},
                },
                "bingyao": {
                    "system": "bingyao", "source_label": "《神峰通考》",
                    "state": "not_judgeable",
                    "lines": ["合成夹具：病药未触发。"],
                    "evidence": {"source_id": BINGYAO_SOURCE_ID},
                    "pairs": [
                        {"pair_id": pair_id, "determination": None,
                         "medicine_effect_status": "unadjudicated",
                         "efficacy_state": "not_judgeable"}
                        for pair_id in PAIR_IDS],
                },
            },
            "relations": [],
            "relations_closing_line": NO_UNIFIED_VERDICT_LINE,
            "unified_verdict": None,
            "public_enabled": True,
            "ai_enabled": False,
            "scope_statement": XIYONG_SCOPE_STATEMENT,
            "limitations": list(XIYONG_LIMITATIONS),
        },
    }
    if dayun is not None:
        result["dayun_presentation"] = dayun
    return result


def _synthetic_full_dayun():
    """Minimal valid full dayun presentation, from the gate's own
    constants + the real pure ``classical_direction`` for f2
    (甲辰, male -> forward). Synthetic intervals, not Golden."""
    direction = classical_direction("甲辰", traditional_role="male")
    counted_jie = {"name": "立春", "at": "2024-02-04T16:27:07+08:00"}
    pillars = {"year": "甲辰", "month": "丙寅", "day": "乙巳",
               "hour": "甲申", "day_master": "乙"}
    gods = ["食神", "正财", "偏财", "正官", "七杀", "正印", "偏印", "劫财"]
    ganzhi = ["丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌"]

    def method_view(method):
        is_sanming = method == "sanming"
        entries = []
        for index, (gz, god) in enumerate(zip(ganzhi, gods), start=1):
            entry = {
                "period_index": index, "ganzhi": gz,
                "stem": gz[0], "branch": gz[1],
                "ten_god_relative_to_natal_day_stem": god,
            }
            if index == 1:
                interval = {
                    "earliest": "2031-01-01T00:00:00+08:00",
                    "latest": "2031-12-31T00:00:00+08:00",
                    "max_inclusive": False,
                    "method": ("sanming_shichen_level" if is_sanming
                               else "shenfeng_day_level"),
                    "variant": (CONVERSION_VARIANT if is_sanming
                                else SHENFENG_CONVERSION_VARIANT),
                }
                if is_sanming:
                    interval["basis"] = \
                        "birth_plus_start_duration_interval"
                else:
                    interval.update({
                        "derivation": "synthetic",
                        "decade_shifts": 0,
                    })
                    # shenfeng interval keys: earliest/latest/
                    # max_inclusive/derivation/decade_shifts/method/
                    # variant -- derivation value is free-form here.
                entry["state"] = "interval"
                entry["start_interval"] = interval
            elif is_sanming:
                # Full timeline: every sanming period carries its
                # own interval (distinct synthetic years).
                entry["state"] = "interval"
                entry["start_interval"] = {
                    "earliest": "%d-01-01T00:00:00+08:00"
                                % (2031 + (index - 1) * 10),
                    "latest": "%d-12-31T00:00:00+08:00"
                              % (2031 + (index - 1) * 10),
                    "max_inclusive": False,
                    "basis": "start_duration_interval_plus_%d_"
                             "calendar_decades" % (index - 1),
                    "method": "sanming_shichen_level",
                    "variant": CONVERSION_VARIANT,
                }
            else:
                entry["state"] = "not_provided"
                entry["start_interval"] = None
                entry["start_interval_status"] = (
                    "not_provided: shenfeng only first period")
            entries.append(entry)
        notice_codes = list(DAYUN_NOTICE_TEXTS)
        notices = [{"code": code, "text": DAYUN_NOTICE_TEXTS[code]}
                   for code in notice_codes[:1]]
        return {
            "method": method, "status": "converted",
            "natal": {"pillars": dict(pillars)},
            "direction": {
                "value": direction["direction"],
                "label": "顺行" if direction["direction"] == "forward"
                         else "逆行",
                "counting_target": direction["counting_target"],
                "counted_jie": dict(counted_jie),
                "rule_quote": direction["rule_quote"],
            },
            "duration": {
                "status": "converted",
                "variant": (CONVERSION_VARIANT if is_sanming
                            else SHENFENG_CONVERSION_VARIANT),
            },
            "entries": entries,
            "notices": notices,
            "sources": [{
                "method": method, "role": "male",
                "variant": (CONVERSION_VARIANT if is_sanming
                            else SHENFENG_CONVERSION_VARIANT),
                "source_id": (SANMING_APPLIED_SOURCE_ID if is_sanming
                              else SHENFENG_SOURCE_ID),
                "quotes": ["合成夹具引文。"],
            }],
        }

    return {
        "variant": DAYUN_VARIANT, "status": "presented",
        "role": {"traditional_role": "male",
                 "selection": ROLE_SELECTION},
        "methods": {"sanming": method_view("sanming"),
                    "shenfeng": method_view("shenfeng")},
        "method_options": copy.deepcopy(DAYUN_METHOD_OPTIONS),
        "evidence": {
            "composition_chain": list(EXPECTED_CHAIN),
            "rules": [dict(rule) for rule in DAYUN_RULES],
            "sequence_disclosure": dict(SEQUENCE_DISCLOSURE),
            "validation": dict(VALIDATION_RECORD),
        },
        "scope": list(DAYUN_SCOPE),
        "limitations": list(DAYUN_LIMITATIONS),
    }


def _all_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _all_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_keys(item)


class SyntheticPresentationTests(unittest.TestCase):
    def test_builds_four_sections_with_basis_caliber_undecided(self):
        presentation = build_career_presentation(
            _synthetic_career_result())
        self.assertEqual(presentation["variant"], VARIANT)
        self.assertTrue(presentation["public_enabled"])
        self.assertFalse(presentation["ai_enabled"])
        self.assertEqual(presentation["day_master"], "乙")
        self.assertEqual(presentation["month_branch"], "寅")
        self.assertEqual(presentation["target_year"], TARGET_YEAR)
        self.assertEqual(
            [s["id"] for s in presentation["sections"]],
            ["natal_ten_gods", "dayun_timeline",
             "natal_luck_linkage", "grounded_boundaries"])
        for section in presentation["sections"]:
            self.assertTrue(section["basis"])
            self.assertTrue(section["caliber"])
            self.assertTrue(section["undecided_conditions"])
        # JSON-able.
        json.dumps(presentation, ensure_ascii=False)

    def test_natal_section_groups_match_hand_derived_f2_counts(self):
        section = build_career_presentation(
            _synthetic_career_result())["sections"][0]
        self.assertEqual(section["status"], "presented")
        groups = {g["group_id"]: g for g in section["content"]["groups"]}
        self.assertEqual(
            (groups["wealth"]["visible_count"],
             groups["wealth"]["hidden_count"]), (0, 4))
        self.assertEqual(
            (groups["authority"]["visible_count"],
             groups["authority"]["hidden_count"]), (0, 2))
        self.assertEqual(
            (groups["output"]["visible_count"],
             groups["output"]["hidden_count"]), (1, 2))
        self.assertEqual(
            (groups["resource"]["visible_count"],
             groups["resource"]["hidden_count"]), (0, 2))
        self.assertEqual(
            (groups["peers"]["visible_count"],
             groups["peers"]["hidden_count"]), (3, 2))
        self.assertEqual(
            section["content"]["flow_year"]["stem_ten_god"], "伤官")
        self.assertEqual(
            section["content"]["flow_year"]["structure_group"], "output")
        lifted = section["content"]["lifted_presentations"]
        self.assertEqual(lifted["strength"]["status"], "not_judgeable")
        self.assertEqual(lifted["pattern"]["status"], "not_judgeable")
        self.assertIsNone(lifted["xiyong"]["unified_verdict"])
        self.assertIn("暂不可判", "；".join(
            section["undecided_conditions"]))

    def test_no_dayun_without_role_is_plainly_undecided(self):
        section = build_career_presentation(
            _synthetic_career_result())["sections"][1]
        self.assertEqual(section["status"], "not_presented")
        self.assertFalse(section["content"]["traditional_role_selected"])
        self.assertIn("未选择传统大运口径",
                      section["content"]["note"])

    def test_full_timeline_eight_periods_interval_only(self):
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        presentation = build_career_presentation(
            _synthetic_career_result(),
            combination=combination,
            full_dayun_presentation=_synthetic_full_dayun())
        section = presentation["sections"][1]
        self.assertEqual(section["id"], "dayun_timeline")
        self.assertEqual(section["status"], "presented")
        sanming = section["content"]["methods"]["sanming"]["entries"]
        shenfeng = section["content"]["methods"]["shenfeng"]["entries"]
        self.assertEqual(len(sanming), 8)
        self.assertEqual(len(shenfeng), 8)
        self.assertEqual([e["ganzhi"] for e in sanming],
                         ["丁卯", "戊辰", "己巳", "庚午",
                          "辛未", "壬申", "癸酉", "甲戌"])
        self.assertEqual([e["stem_ten_god"] for e in sanming],
                         ["食神", "正财", "偏财", "正官",
                          "七杀", "正印", "偏印", "劫财"])
        # Sanming: every period carries its interval (interval-only
        # precision -- datetimes, never a single age or date).
        for entry in sanming:
            self.assertEqual(entry["state"], "interval")
            self.assertIsNotNone(entry["start_interval"])
            self.assertEqual(entry["age_presentation"], "not_presented")
        # Shenfeng: only the first period has an interval, by
        # registered design -- periods 2-8 are explicitly
        # not_provided, not withheld by this scene.
        self.assertEqual(shenfeng[0]["state"], "interval")
        self.assertIsNotNone(shenfeng[0]["start_interval"])
        for entry in shenfeng[1:]:
            self.assertEqual(entry["state"], "not_provided")
            self.assertIsNone(entry["start_interval"])
            self.assertEqual(entry["age_presentation"], "not_presented")
        # No numeric age anywhere in the section.
        age_keys = {k for k in _all_keys(section)
                    if "age" in k.lower()}
        self.assertEqual(age_keys, {"age_presentation"})

    def test_full_timeline_hidden_stems_and_natal_relations(self):
        from tianji_kb.bazi_core import hidden_stems
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        presentation = build_career_presentation(
            _synthetic_career_result(),
            combination=combination,
            full_dayun_presentation=_synthetic_full_dayun())
        sanming = presentation["sections"][1]["content"]["methods"][
            "sanming"]["entries"]
        # Branch hidden stems reuse the existing lookup (same table
        # as the natal hidden stems). The table lives in the sealed
        # canonical store: in the public checkout the periods
        # degrade explicitly (not_available, stems None); the sealed
        # run carries them -- spot-check 卯 (乙 only) and 辰
        # (戊/乙/癸) for day master 乙 when available.
        if sanming[0]["hidden_stems_status"] == "available":
            self.assertEqual(sanming[0]["hidden_stems"],
                             hidden_stems("卯", "乙"))
            self.assertEqual([h["stem"] for h in
                              sanming[0]["hidden_stems"]], ["乙"])
            self.assertEqual([h["stem"] for h in
                              sanming[1]["hidden_stems"]],
                             ["戊", "乙", "癸"])
            self.assertEqual(
                [h["ten_god"] for h in sanming[1]["hidden_stems"]],
                ["正财", "比肩", "偏印"])
        else:
            self.assertEqual(sanming[0]["hidden_stems_status"],
                             "not_available")
            for entry in sanming:
                self.assertIsNone(entry["hidden_stems"])
        # Reviewed natal relations per period match the combination
        # engine's own structural_relations filter, exactly.
        structural = combination["structural_relations"]
        for entry in sanming:
            expected = [r for r in structural
                        if r["scope"] == "dayun_x_natal"
                        and r.get("period_index")
                        == entry["period_index"]]
            relations = entry["natal_relations"]
            self.assertEqual(relations["total"], len(expected))
            self.assertEqual(sum(relations["counts_by_kind"].values()),
                             len(expected))
            kinds = {r["kind"] for r in expected}
            self.assertEqual(set(relations["counts_by_kind"]), kinds)
        # Period 1 relations: 4 stem five-element rows + 1 branch
        # harm (卯辰害) + 1 directional-meeting group row.
        self.assertEqual(sanming[0]["natal_relations"]["total"], 6)

    def test_full_timeline_liunian_query_entries(self):
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        presentation = build_career_presentation(
            _synthetic_career_result(),
            combination=combination,
            full_dayun_presentation=_synthetic_full_dayun())
        methods = presentation["sections"][1]["content"]["methods"]
        for position, entry in enumerate(
                methods["sanming"]["entries"], start=1):
            query = entry["liunian_query"]
            self.assertTrue(query["available"])
            self.assertEqual(query["query_year"],
                             2031 + (position - 1) * 10)
        self.assertTrue(methods["shenfeng"]["entries"][0][
            "liunian_query"]["available"])
        for entry in methods["shenfeng"]["entries"][1:]:
            query = entry["liunian_query"]
            self.assertFalse(query["available"])
            self.assertIsNone(query["query_year"])

    def test_trimmed_only_degrades_to_first_period_only(self):
        trimmed = _first_period_dayun_for_career_life(
            _synthetic_full_dayun())
        presentation = build_career_presentation(
            _synthetic_career_result(dayun=trimmed))
        section = presentation["sections"][1]
        self.assertEqual(section["status"], "first_period_only")
        for method in ("sanming", "shenfeng"):
            view = section["content"]["methods"][method]
            self.assertEqual(view["first_period"]["period_index"], 1)
            self.assertEqual(view["full_timeline"], "not_attached")
        self.assertIn("完整 8 运时间线未附带",
                      section["content"]["note"])

    def test_linkage_with_real_combine_stays_none_effect(self):
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        self.assertIsNone(combination["overall_effect"])
        presentation = build_career_presentation(
            _synthetic_career_result(), combination=combination)
        section = presentation["sections"][2]
        self.assertEqual(section["status"], "assembled")
        self.assertIsNone(section["content"]["overall_effect"])
        self.assertEqual(section["content"]["rules_registered"], [])
        self.assertEqual(section["content"]["efficacy_status"],
                         "no_reviewed_rules")
        self.assertEqual(
            section["content"]["conditional_count"],
            combination["effects"]["conditional_count"])
        self.assertIn("TJ-017.2", "；".join(
            section["undecided_conditions"]))

    def test_linkage_without_combination_is_not_assembled(self):
        section = build_career_presentation(
            _synthetic_career_result())["sections"][2]
        self.assertEqual(section["status"], "not_assembled")
        self.assertIsNone(section["content"]["overall_effect"])
        self.assertEqual(section["content"]["conditional_conclusions"], [])

    def test_boundaries_section_claims_nothing(self):
        section = build_career_presentation(
            _synthetic_career_result())["sections"][3]
        not_claimed = section["content"]["not_claimed"]
        self.assertTrue(any("不预测收入" in line for line in not_claimed))
        self.assertTrue(any("不输出事业指数" in line
                            for line in not_claimed))
        self.assertTrue(any("六爻" in line for line in not_claimed))

    def test_validator_and_projection_round_trip(self):
        presentation = build_career_presentation(
            _synthetic_career_result(
                dayun=_first_period_dayun_for_career_life(
                    _synthetic_full_dayun())),
            combination=combine(F2_PILLARS, "乙", F2_DAYUN_8,
                                TARGET_YEAR),
            full_dayun_presentation=_synthetic_full_dayun())
        self.assertTrue(is_valid_career_presentation(presentation))
        projected = to_public_career_presentation(presentation)
        self.assertEqual(projected, presentation)
        self.assertIsNot(projected["sections"],
                         presentation["sections"])
        self.assertEqual(find_public_boundary_violations(projected), [])

    def test_no_banned_keys_anywhere_in_output(self):
        banned = {"start_age", "end_age", "start_date", "end_date",
                  "handover_datetime", "conversion_to_start_age",
                  "score", "income", "prediction", "useful_god",
                  "overall_strength", "strength_score", "modern_score",
                  "fuyi_candidate_stems", "candidate_stems"}
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        cases = [
            (None, None),
            (_first_period_dayun_for_career_life(
                _synthetic_full_dayun()), None),
            (None, _synthetic_full_dayun()),
        ]
        for trimmed, full in cases:
            presentation = build_career_presentation(
                _synthetic_career_result(dayun=trimmed),
                combination=combination,
                full_dayun_presentation=full)
            self.assertTrue(
                banned.isdisjoint(set(_all_keys(presentation))))
            # No key carries an age except the registered
            # age_presentation flag, always not_presented.
            for key in _all_keys(presentation):
                if "age" in key.lower():
                    self.assertEqual(key, "age_presentation")
            text = json.dumps(presentation, ensure_ascii=False)
            self.assertNotIn('"age_presentation": "presented"', text)

    def test_no_fortune_judgment_from_strength_or_fuyi(self):
        """Q2: strength scores / fuyi candidates never become
        career/wealth fortune judgments. The builder carries no
        score and no candidate-stem list at all; the only verdict
        words in the output are the combination engine's own
        conditional-conclusion verdicts (existence facts)."""
        from tianji_kb.bazi_combination_engine import (
            CONDITIONAL_VERDICTS,
        )
        presentation = build_career_presentation(
            _synthetic_career_result(),
            combination=combine(F2_PILLARS, "乙", F2_DAYUN_8,
                                TARGET_YEAR),
            full_dayun_presentation=_synthetic_full_dayun())
        verdicts = []

        def collect(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "verdict":
                        verdicts.append(item)
                    collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(presentation)
        for verdict in verdicts:
            self.assertIn(verdict, CONDITIONAL_VERDICTS)
        lifted = presentation["sections"][0]["content"][
            "lifted_presentations"]
        # No numeric score anywhere in the lifted gates: U1 carries
        # only its adjudicated status/predicate, never a score.
        for gate in lifted.values():
            for key, value in gate.items():
                self.assertNotIn("score", key)
                self.assertNotIsInstance(value, (int, float))
        self.assertEqual(
            presentation["sections"][2]["content"]["overall_effect"],
            None)


class FailClosedTests(unittest.TestCase):
    def test_untrimmed_dayun_in_trimmed_field_is_rejected(self):
        full = _synthetic_full_dayun()
        # The envelope's dayun_presentation field is first-period
        # trimmed by contract; an untrimmed full object there is a
        # wiring leak and fails closed (the full timeline must arrive
        # via full_dayun_presentation instead).
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(dayun=full))

    def test_full_timeline_interval_state_mismatch_is_rejected(self):
        full = _synthetic_full_dayun()
        forged = copy.deepcopy(full)
        forged["methods"]["sanming"]["entries"][1]["start_interval"] = \
            None
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(),
                full_dayun_presentation=forged)
        forged2 = copy.deepcopy(full)
        forged2["methods"]["shenfeng"]["entries"][1]["state"] = "interval"
        forged2["methods"]["shenfeng"]["entries"][1][
            "start_interval"] = full["methods"]["shenfeng"][
                "entries"][0]["start_interval"]
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(),
                full_dayun_presentation=forged2)

    def test_combination_sequence_drift_is_rejected(self):
        drifted_dayun = [
            {"candidate_ganzhi": "辛酉", "period_index": 1,
             "ten_god": "正官"},
            {"candidate_ganzhi": "壬戌", "period_index": 2,
             "ten_god": "偏印"},
            {"candidate_ganzhi": "癸亥", "period_index": 3,
             "ten_god": "正印"},
            {"candidate_ganzhi": "甲子", "period_index": 4,
             "ten_god": "比肩"},
            {"candidate_ganzhi": "乙丑", "period_index": 5,
             "ten_god": "劫财"},
            {"candidate_ganzhi": "丙寅", "period_index": 6,
             "ten_god": "食神"},
            {"candidate_ganzhi": "丁卯", "period_index": 7,
             "ten_god": "伤官"},
            {"candidate_ganzhi": "戊辰", "period_index": 8,
             "ten_god": "偏财"},
        ]
        combination = combine(
            ["戊戌", "庚申", "甲子", "甲戌"], "甲", drifted_dayun, 1988)
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(),
                combination=combination,
                full_dayun_presentation=_synthetic_full_dayun())

    def test_forged_overall_effect_is_rejected(self):
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        forged = copy.deepcopy(combination)
        forged["overall_effect"] = "favourable"
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(), combination=forged)
        forged2 = copy.deepcopy(combination)
        forged2["effects"]["overall_effect"] = "favourable"
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(), combination=forged2)

    def test_forged_efficacy_registry_is_rejected(self):
        combination = combine(F2_PILLARS, "乙", F2_DAYUN_8, TARGET_YEAR)
        forged = copy.deepcopy(combination)
        forged["effects"]["cross_layer_efficacy"]["rules_registered"] = \
            ["bazi.rule.r999"]
        with self.assertRaises(ValueError):
            build_career_presentation(
                _synthetic_career_result(), combination=forged)

    def test_invalid_lift_is_rejected(self):
        result = _synthetic_career_result()
        result["strength_presentation"]["status"] = "presented"
        with self.assertRaises(ValueError):
            build_career_presentation(result)
        result2 = _synthetic_career_result()
        result2["xiyong_presentation"]["unified_verdict"] = "甲"
        with self.assertRaises(ValueError):
            build_career_presentation(result2)
        result3 = _synthetic_career_result()
        del result3["pattern_presentation"]
        with self.assertRaises(ValueError):
            build_career_presentation(result3)

    def test_group_count_drift_is_rejected(self):
        result = _synthetic_career_result()
        result["structure_groups"]["wealth"]["visible_count"] = 9
        with self.assertRaises(ValueError):
            build_career_presentation(result)

    def test_validator_rejects_extra_keys_and_banned_keys(self):
        presentation = build_career_presentation(
            _synthetic_career_result())
        self.assertFalse(is_valid_career_presentation(
            {**presentation, "extra": 1}))
        tampered = copy.deepcopy(presentation)
        tampered["sections"][0]["content"]["score"] = 88
        self.assertFalse(is_valid_career_presentation(tampered))
        with self.assertRaises(ValueError):
            to_public_career_presentation(tampered)


class RealChartTests(unittest.TestCase):
    """Sealed real-chart checks (f2). Skip without the sealed runtime."""

    def _real_inputs(self):
        try:
            from tianji_kb import scenario_engine
            from tianji_kb.unified_compute import (
                assemble_birth,
                trim_for_career,
            )
        except Exception as exc:  # pragma: no cover - env dependent
            raise unittest.SkipTest("imports unavailable: %s" % exc)
        try:
            envelope = scenario_engine.execute_scenario(
                "career", {"birth_value": F2_BIRTH,
                           "target_year": TARGET_YEAR,
                           "traditional_role": "male"})
            # The full 8-period timeline is the bazi-profile gate's
            # object for the same birth instant and role (the career
            # envelope itself carries only the first-period trim).
            profile = scenario_engine.execute_scenario(
                "bazi-profile",
                {"value": F2_BIRTH,
                 "strength_variant": "ditiansui-root-visibility-v1",
                 "traditional_role": "male"})
            assembly = assemble_birth(
                F2_BIRTH, traditional_role="male",
                target_year=TARGET_YEAR)
        except Exception as exc:
            raise unittest.SkipTest(
                "sealed runtime unavailable: %s" % exc)
        trim = trim_for_career(assembly)
        return (envelope["result"],
                trim["research"]["combination"],
                trim["research"].get("combination_note"),
                profile["result"]["dayun_presentation"])

    def test_f2_real_envelope_builds_and_validates(self):
        result, combination, note, full_dayun = self._real_inputs()
        presentation = build_career_presentation(
            result, combination=combination, combination_note=note,
            full_dayun_presentation=full_dayun)
        self.assertTrue(is_valid_career_presentation(presentation))
        self.assertEqual(find_public_boundary_violations(
            to_public_career_presentation(presentation)), [])
        natal = presentation["sections"][0]
        self.assertEqual(natal["content"]["day_master"], "乙")
        self.assertEqual(natal["content"]["month_branch"], "寅")
        self.assertEqual(
            natal["content"]["flow_year"]["ganzhi"], "丙午")
        self.assertEqual(
            natal["content"]["flow_year"]["stem_ten_god"], "伤官")
        dayun = presentation["sections"][1]
        self.assertEqual(dayun["id"], "dayun_timeline")
        self.assertEqual(dayun["status"], "presented")
        sanming = dayun["content"]["methods"]["sanming"]["entries"]
        shenfeng = dayun["content"]["methods"]["shenfeng"]["entries"]
        self.assertEqual(len(sanming), 8)
        self.assertEqual(len(shenfeng), 8)
        self.assertEqual([e["ganzhi"] for e in sanming],
                         ["丁卯", "戊辰", "己巳", "庚午",
                          "辛未", "壬申", "癸酉", "甲戌"])
        for entry in sanming:
            self.assertEqual(entry["state"], "interval")
            self.assertIsNotNone(entry["start_interval"])
            self.assertEqual(entry["age_presentation"], "not_presented")
            self.assertTrue(entry["liunian_query"]["available"])
            self.assertIsInstance(
                entry["liunian_query"]["query_year"], int)
            # Sealed run: the hidden-stem table is available.
            self.assertEqual(entry["hidden_stems_status"], "available")
        self.assertEqual(sanming[0]["hidden_stems"],
                         [{"stem": "乙", "ten_god": "比肩"}])
        self.assertEqual([h["stem"] for h in
                          sanming[1]["hidden_stems"]],
                         ["戊", "乙", "癸"])
        self.assertEqual(shenfeng[0]["state"], "interval")
        for entry in shenfeng[1:]:
            self.assertEqual(entry["state"], "not_provided")
            self.assertIsNone(entry["start_interval"])
            self.assertFalse(entry["liunian_query"]["available"])
        linkage = presentation["sections"][2]
        self.assertIsNone(linkage["content"]["overall_effect"])
        self.assertEqual(linkage["content"]["rules_registered"], [])
        # No numeric age anywhere in the real presentation either.
        for key in _all_keys(presentation):
            if "age" in key.lower():
                self.assertEqual(key, "age_presentation")

    def test_f2_real_groups_match_engine_counts(self):
        result, combination, note, full_dayun = self._real_inputs()
        presentation = build_career_presentation(
            result, combination=combination, combination_note=note,
            full_dayun_presentation=full_dayun)
        groups = {g["group_id"]: g for g in
                  presentation["sections"][0]["content"]["groups"]}
        source = result["structure_groups"]
        for group_id, group in groups.items():
            self.assertEqual(group["visible_count"],
                             source[group_id]["visible_count"])
            self.assertEqual(group["hidden_count"],
                             source[group_id]["hidden_count"])
            self.assertEqual(len(group["occurrences"]),
                             len(source[group_id]["occurrences"]))


if __name__ == "__main__":
    unittest.main()
