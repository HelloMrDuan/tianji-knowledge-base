"""TJ-031.19 / E0427 Lane E tests: life-overview presentation.

Two honest classes, following the batch-5 lane test discipline:

* Synthetic fixtures (run locally): the f2 chart
  (2024-02-11T16:27:07+08:00, 甲辰/丙寅/乙巳/甲申, day master 乙,
  target year 2026 丙午) with hand-built life envelopes, trims and
  sibling presentations. The career result and the full dayun
  presentation are copied from Lane B's test fixtures
  (``tests/test_tj0427_career_presentation.py``) with one documented
  change: the synthetic dayun intervals start in 2021 instead of
  2031, so the fixture target year 2026 falls inside period 1 and
  the stage-containment logic is exercised. The intervals stay
  synthetic plumbing, NOT a Golden. The life trim shape is copied
  from Lane A's test fixture
  (``tests/test_tj0427_bazi_profile_presentation.py``).
* Live test: the real f2 chart through the real builders. Skips in
  the public checkout, where sealed ``data/`` is absent.
"""

import copy
import unittest

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
from tianji_kb.bazi_profile_presentation import VARIANT as BAZI_VARIANT
from tianji_kb.bazi_strength_public import LIMITATIONS as STRENGTH_LIMITATIONS
from tianji_kb.bazi_strength_public import SCOPE_STATEMENT as STRENGTH_SCOPE
from tianji_kb.bazi_strength_public import VARIANT as STRENGTH_VARIANT
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
from tianji_kb.career_presentation import VARIANT as CAREER_VARIANT
from tianji_kb.compatibility_presentation import (
    PRESENTATION_VERSION as COMPAT_VERSION,
)
from tianji_kb.compatibility_presentation import (
    _SECTION_IDS as COMPAT_SECTION_IDS,
)
from tianji_kb.life_presentation import (
    VARIANT,
    build_life_presentation,
    build_life_presentation_for,
    is_valid_life_presentation,
    to_public_life_presentation,
)
from tianji_kb.romance_presentation import VARIANT as ROMANCE_VARIANT
from tianji_kb.romance_presentation import (
    _SECTION_IDS as ROMANCE_SECTION_IDS,
)

F2_BIRTH = "2024-02-11T16:27:07+08:00"
F2_PILLARS = ["甲辰", "丙寅", "乙巳", "甲申"]
# Classical hidden stems for the f2 branches, stated explicitly in
# the fixture (Lane A): 辰戊乙癸 / 寅甲丙戊 / 巳丙戊庚 / 申庚壬戊.
F2_HIDDEN = [["戊", "乙", "癸"], ["甲", "丙", "戊"],
             ["丙", "庚", "戊"], ["庚", "壬", "戊"]]
# Real f2 combination dayun sequence (Lane B): candidate ganzhi +
# stem ten-god relative to day master 乙.
F2_DAYUN_8 = [
    {"ganzhi": "丁卯", "ten_god": "食神"},
    {"ganzhi": "戊辰", "ten_god": "正财"},
    {"ganzhi": "己巳", "ten_god": "偏财"},
    {"ganzhi": "庚午", "ten_god": "正官"},
    {"ganzhi": "辛未", "ten_god": "七杀"},
    {"ganzhi": "壬申", "ten_god": "正印"},
    {"ganzhi": "癸酉", "ten_god": "偏印"},
    {"ganzhi": "甲戌", "ten_god": "劫财"},
]
TARGET_YEAR = 2026
TARGET_GANZHI = "丙午"
TARGET_BRANCH = "午"
TARGET_STEM = "丙"
TARGET_STEM_TEN_GOD = "伤官"


def _f2_pillars():
    """Lane A pillar shape: stem/branch dicts with hidden stems."""
    pillars = []
    for name, ganzhi, hidden in zip(
            ("year", "month", "day", "hour"), F2_PILLARS, F2_HIDDEN):
        pillars.append({
            "name": name, "ganzhi": ganzhi,
            "stem": {"value": ganzhi[0], "ten_god": "比肩"},
            "branch": {"value": ganzhi[1],
                       "hidden_stems": [{"stem": stem}
                                        for stem in hidden]},
        })
    return pillars


def _target_year_dict(year=TARGET_YEAR, ganzhi=TARGET_GANZHI,
                     branch=TARGET_BRANCH):
    return {"year": year, "ganzhi": ganzhi, "branch": branch}


def _natal_dict():
    return {"pillars": _f2_pillars(),
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"}}


# --- Lane B fixtures (copied with attribution) -----------------------
# Hand-derived Ten-God positions for f2 (day master 乙), standard
# hidden-stem tables. Synthetic plumbing fixture only -- NOT a Golden.

_F2_GROUPS = {
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


def _synthetic_career_result():
    """Lane B's synthetic career result, verbatim (target 2026)."""
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
    return {
        "natal": {
            "pillars": pillars,
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
        },
        "structure_groups": groups,
        "interpretation_cards": cards,
        "target_year": {
            "year": TARGET_YEAR, "ganzhi": TARGET_GANZHI,
            "stem": TARGET_STEM, "branch": TARGET_BRANCH,
            "stem_ten_god": TARGET_STEM_TEN_GOD,
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


def _synthetic_full_dayun():
    """Lane B's minimal valid full dayun presentation, with one
    documented change: synthetic intervals start in 2021 (not 2031),
    so the fixture target year 2026 falls inside period 1 and the
    stage-containment logic is exercised. Intervals stay synthetic
    plumbing, NOT a Golden."""
    direction = classical_direction("甲辰", traditional_role="male")
    counted_jie = {"name": "立春", "at": "2024-02-04T16:27:07+08:00"}
    pillars = {"year": "甲辰", "month": "丙寅", "day": "乙巳",
               "hour": "甲申", "day_master": "乙"}
    gods = [period["ten_god"] for period in F2_DAYUN_8]
    ganzhi = [period["ganzhi"] for period in F2_DAYUN_8]

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
                    "earliest": "2021-01-01T00:00:00+08:00",
                    "latest": "2021-12-31T00:00:00+08:00",
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
                entry["state"] = "interval"
                entry["start_interval"] = interval
            elif is_sanming:
                entry["state"] = "interval"
                entry["start_interval"] = {
                    "earliest": "%d-01-01T00:00:00+08:00"
                                % (2021 + (index - 1) * 10),
                    "latest": "%d-12-31T00:00:00+08:00"
                              % (2021 + (index - 1) * 10),
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


# --- Life fixtures ----------------------------------------------------

def _synthetic_life_envelope(year=TARGET_YEAR, ganzhi=TARGET_GANZHI,
                             branch=TARGET_BRANCH):
    """Life envelope over the f2 chart; the career result is Lane B's
    synthetic result (target year patched when a non-default year is
    requested)."""
    natal = _natal_dict()
    target = _target_year_dict(year, ganzhi, branch)
    career = _synthetic_career_result()
    if year != TARGET_YEAR:
        career["target_year"] = {
            "year": year, "ganzhi": ganzhi, "stem": ganzhi[0],
            "branch": branch, "stem_ten_god": "正印",
            "structure_group": "resource",
            "structure_group_label": "印星",
        }
    return {
        "scenario_id": "life",
        "status": "executed",
        "result": {
            "profile": {"pillars": _f2_pillars(),
                        "day_master": {"stem": "乙", "element": "木",
                                       "polarity": "阴"}},
            "target_year": year,
            "yearly": {"natal": copy.deepcopy(natal),
                       "target_year": copy.deepcopy(target)},
            "romance": {"natal": copy.deepcopy(natal),
                        "target_year": copy.deepcopy(target)},
            "career": career,
        },
        "rule_matches": [], "trace": [], "evidence": [],
        "warnings": [], "limitations": [],
    }


def _synthetic_life_trim(year=TARGET_YEAR, ganzhi=TARGET_GANZHI,
                         branch=TARGET_BRANCH, dayun_presentation=None):
    """Life trim in the real ``trim_for_life`` shape (Lane A
    chart/research blocks + life extras). ``dayun`` carries the gate
    presentation; ``dayun_presentation`` is attached only when the
    caller passes it (the bazi-fallback test)."""
    full_dayun = _synthetic_full_dayun()
    trim = {
        "variant": "unified-compute-entry-v1",
        "page": "life",
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "chart": {
            "birth_value": F2_BIRTH,
            "zone": None,
            "pillars": _f2_pillars(),
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
            "month_branch": "寅",
            "ganzhi": list(F2_PILLARS),
        },
        "research": {
            "strength": None,
            "pattern": None,
            "pattern_d1": {"attempted": False,
                           "status": "not_attempted_here"},
            "xiyong": None,
            "tiaohou": None,
            "bingyao": None,
            "pilots": {},
            "errors": [],
            "research_only": True,
            "public_enabled": False,
            "ai_enabled": False,
        },
        "target_year": year,
        "dayun": copy.deepcopy(full_dayun),
        "dayun_status": {"status": "presented"},
        "flow_year": {"year": year, "ganzhi": ganzhi, "branch": branch},
        "flow_boundary": {"state": "fixture"},
        "identity_anchor": {
            "pillars": _f2_pillars(),
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
            "target_year": year,
            "target_ganzhi": ganzhi,
            "target_branch": branch,
        },
    }
    if dayun_presentation is not None:
        trim["dayun_presentation"] = dayun_presentation
    return trim


def _synthetic_romance(year=TARGET_YEAR):
    return {
        "variant": ROMANCE_VARIANT,
        "scenario_id": "romance",
        "public_enabled": True,
        "ai_enabled": False,
        "interpretation_allowed": False,
        "birth_value": F2_BIRTH,
        "target_year": year,
        "natal": {"pillars": _f2_pillars(),
                  "day_master": "乙",
                  "day_master_element": "木",
                  "day_branch": "巳"},
        "sections": [
            {"id": "peach_blossom_spouse_star_palace",
             "title": "桃花与配偶星宫",
             "facts": [{"label": "桃花星", "value": "子",
                        "source": "fixture"}],
             "boundary": "fixture boundary",
             "undecided": ["fixture undecided"]},
            {"id": "natal_marriage_structure",
             "title": "原局婚姻结构",
             "facts": [{"label": "配偶星", "value": "甲",
                        "source": "fixture"}],
             "boundary": "fixture boundary",
             "undecided": []},
            {"id": "dayun_liunian_linkage",
             "title": "大运流年联动",
             "facts": [{"label": "流年联动", "value": "fixture",
                        "source": "fixture"}],
             "boundary": "fixture boundary",
             "undecided": []},
        ],
        "boundary": "fixture boundary",
        "scope_statement": "fixture scope",
        "limitations": ["fixture limitation"],
        "undecided": ["fixture undecided"],
    }


def _synthetic_compatibility():
    pillars_b = ["乙亥", "壬午", "丁丑", "甲辰"]
    return {
        "presentation_version": COMPAT_VERSION,
        "scenario_id": "compatibility",
        "public_enabled": True,
        "ai_enabled": False,
        "interpretation_allowed": False,
        "unified_verdict": None,
        "person_a": {"pillars": list(F2_PILLARS),
                     "day_master": "乙"},
        "person_b": {"pillars": pillars_b, "day_master": "丁"},
        "sections": [
            {"id": "charts", "title": "双方命盘",
             "content": {"person_a": {"pillars": _f2_pillars(),
                                      "day_master": "乙"},
                         "person_b": {"pillars": _f2_pillars(),
                                      "day_master": "丁"}}},
            {"id": "relations", "title": "合冲刑害关系",
             "content": {"relations": [], "summary": "fixture"}},
            {"id": "patterns_and_xiyong", "title": "格局与喜用",
             "content": {"person_a": {"status": "not_presented",
                                      "reason": "fixture"},
                         "person_b": {"status": "not_presented",
                                      "reason": "fixture"}}},
            {"id": "dayun", "title": "大运",
             "content": {"person_a": {"status": "not_presented",
                                      "reason": "fixture"},
                         "person_b": {"status": "not_presented",
                                      "reason": "fixture"}}},
            {"id": "inference_boundary", "title": "推断边界",
             "content": {"boundary": "fixture boundary",
                         "undecided": []}},
        ],
        "boundary": "fixture boundary",
        "scope_statement": "fixture scope",
        "limitations": ["fixture limitation"],
        "undecided": ["fixture undecided"],
    }


class LifePresentationTests(unittest.TestCase):
    def _presentation(self):
        return build_life_presentation(
            _synthetic_life_envelope(),
            life_trim=_synthetic_life_trim(),
            full_dayun_presentation=_synthetic_full_dayun(),
            romance=_synthetic_romance(),
            compatibility=_synthetic_compatibility())

    def test_top_shape_and_unified_identity(self):
        presentation = self._presentation()
        self.assertTrue(is_valid_life_presentation(presentation))
        self.assertEqual(presentation["variant"], VARIANT)
        self.assertEqual(presentation["page"], "life-overview")
        self.assertTrue(presentation["public_enabled"])
        self.assertFalse(presentation["ai_enabled"])
        self.assertFalse(presentation["interpretation_allowed"])
        unified = presentation["unified"]
        self.assertEqual(unified["pillars"], F2_PILLARS)
        self.assertEqual(unified["day_master"]["stem"], "乙")
        self.assertEqual(unified["target_year"], TARGET_YEAR)
        self.assertEqual(unified["target_year_ganzhi"], TARGET_GANZHI)
        self.assertEqual(unified["target_year_branch"], TARGET_BRANCH)
        self.assertEqual(unified["traditional_role"], "male")
        self.assertEqual(unified["caliber"], "传统男命口径")
        self.assertTrue(unified["four_source_consistent"])

    def test_themes_reuse_sibling_presentations(self):
        presentation = self._presentation()
        themes = presentation["themes"]
        self.assertEqual(set(themes), {"bazi", "career", "romance",
                                       "compatibility"})
        self.assertEqual(themes["bazi"]["variant"], BAZI_VARIANT)
        self.assertEqual(themes["bazi"]["chart"]["ganzhi"], F2_PILLARS)
        self.assertEqual(themes["career"]["variant"], CAREER_VARIANT)
        self.assertEqual(themes["career"]["day_master"], "乙")
        self.assertEqual(themes["romance"]["variant"], ROMANCE_VARIANT)
        self.assertEqual(themes["compatibility"]["presentation_version"],
                         COMPAT_VERSION)
        self.assertIsNone(
            themes["compatibility"]["unified_verdict"])
        self.assertFalse(
            themes["compatibility"]["interpretation_allowed"])

    def test_dayun_full_timeline_and_stages(self):
        presentation = self._presentation()
        self.assertEqual(presentation["dayun"]["status"], "presented")
        self.assertEqual(presentation["dayun"]["source"], "career")
        methods = presentation["dayun"]["methods"]
        self.assertEqual(len(methods["sanming"]["entries"]), 8)
        stages = presentation["stages"]
        self.assertEqual(len(stages), 8)
        self.assertEqual([stage["ganzhi"] for stage in stages],
                         [period["ganzhi"] for period in F2_DAYUN_8])
        for stage in stages:
            self.assertEqual(stage["age_presentation"], "not_presented")
            self.assertEqual(stage["stem_ten_god"],
                             F2_DAYUN_8[stage["period_index"] - 1]
                             ["ten_god"])
        target_stage = next(stage for stage in stages
                            if stage["target_year_here"])
        self.assertEqual(target_stage["period_index"], 1)
        self.assertEqual(target_stage["target_year_facts"]["yearly"],
                         _target_year_dict())
        self.assertIsNotNone(
            target_stage["target_year_facts"]["romance_linkage_facts"])

    def test_no_numeric_age_anywhere(self):
        presentation = self._presentation()
        payload = str(presentation)
        self.assertNotIn("start_age", payload)
        self.assertNotIn("end_age", payload)
        self.assertTrue(all(
            stage["age_presentation"] == "not_presented"
            for stage in presentation["stages"]))

    def test_cross_source_drift_fails_closed(self):
        envelope = _synthetic_life_envelope()
        envelope["result"]["career"]["natal"]["pillars"][0] = dict(
            envelope["result"]["career"]["natal"]["pillars"][0],
            ganzhi="甲子")
        with self.assertRaises(ValueError):
            build_life_presentation(
                envelope, life_trim=_synthetic_life_trim(),
                full_dayun_presentation=_synthetic_full_dayun(),
                romance=_synthetic_romance())

    def test_trim_anchor_drift_fails_closed(self):
        trim = _synthetic_life_trim()
        trim["identity_anchor"]["target_ganzhi"] = "丁未"
        with self.assertRaises(ValueError):
            build_life_presentation(
                _synthetic_life_envelope(), life_trim=trim,
                full_dayun_presentation=_synthetic_full_dayun(),
                romance=_synthetic_romance())

    def test_romance_theme_drift_fails_closed(self):
        romance = _synthetic_romance()
        romance["target_year"] = 2027
        with self.assertRaises(ValueError):
            build_life_presentation(
                _synthetic_life_envelope(),
                life_trim=_synthetic_life_trim(),
                full_dayun_presentation=_synthetic_full_dayun(),
                romance=romance)

    def test_compatibility_theme_drift_fails_closed(self):
        compatibility = _synthetic_compatibility()
        compatibility["unified_verdict"] = "some verdict"
        with self.assertRaises(ValueError):
            build_life_presentation(
                _synthetic_life_envelope(),
                life_trim=_synthetic_life_trim(),
                full_dayun_presentation=_synthetic_full_dayun(),
                compatibility=compatibility)

    def test_compatibility_optional_single_person(self):
        presentation = build_life_presentation(
            _synthetic_life_envelope(),
            life_trim=_synthetic_life_trim(),
            full_dayun_presentation=_synthetic_full_dayun(),
            romance=_synthetic_romance())
        theme = presentation["themes"]["compatibility"]
        self.assertEqual(theme["status"], "not_applicable")
        self.assertTrue(is_valid_life_presentation(presentation))

    def test_no_full_dayun_dayun_not_presented(self):
        """No full presentation anywhere: both themes degrade, the
        life dayun is honestly not presented (never a partial
        timeline)."""
        presentation = build_life_presentation(
            _synthetic_life_envelope(),
            life_trim=_synthetic_life_trim(),
            romance=_synthetic_romance())
        self.assertEqual(presentation["dayun"]["status"], "not_presented")
        self.assertEqual(presentation["stages"]["status"],
                         "not_presented")
        self.assertTrue(is_valid_life_presentation(presentation))

    def test_bazi_fallback_when_career_has_no_full_timeline(self):
        """Trim carries the gate lift but no full presentation is
        passed: the career theme degrades to first-period-only and
        the life dayun falls back to the bazi theme's periods."""
        presentation = build_life_presentation(
            _synthetic_life_envelope(),
            life_trim=_synthetic_life_trim(
                dayun_presentation=_synthetic_full_dayun()),
            romance=_synthetic_romance())
        self.assertEqual(presentation["dayun"]["status"], "presented")
        self.assertEqual(presentation["dayun"]["source"], "bazi")
        self.assertEqual(len(presentation["stages"]), 8)
        self.assertEqual([stage["ganzhi"] for stage in presentation["stages"]],
                         [period["ganzhi"] for period in F2_DAYUN_8])

    def test_no_trim_bazi_not_presented(self):
        presentation = build_life_presentation(
            _synthetic_life_envelope(),
            full_dayun_presentation=_synthetic_full_dayun(),
            romance=_synthetic_romance())
        self.assertEqual(presentation["themes"]["bazi"]["status"],
                         "not_presented")
        self.assertTrue(is_valid_life_presentation(presentation))

    def test_target_year_before_first_period_stated(self):
        presentation = build_life_presentation(
            _synthetic_life_envelope(2020, "庚子", "子"),
            life_trim=_synthetic_life_trim(2020, "庚子", "子"),
            full_dayun_presentation=_synthetic_full_dayun(),
            romance=_synthetic_romance(2020))
        self.assertEqual(
            [stage["target_year_here"] for stage in presentation["stages"]],
            [False] * 8)
        self.assertEqual(
            [stage["target_year_containment"]
             for stage in presentation["stages"]],
            ["not_within"] * 8)

    def test_banned_tokens_absent_from_own_strings(self):
        presentation = self._presentation()
        own = {
            "unified": presentation["unified"],
            "dayun": presentation["dayun"],
            "stages": presentation["stages"],
            "boundary": presentation["boundary"],
            "scope_statement": presentation["scope_statement"],
            "limitations": presentation["limitations"],
            "undecided": presentation["undecided"],
        }
        payload = str(own)
        for token in ("评分", "分数", "预测", "吉凶", "婚期", "正缘",
                      "脱单", "注定", "桃花指数", "缘分指数", "寿命",
                      "统一喜用", "unified_verdict"):
            self.assertNotIn(token, payload)

    def test_validator_rejects_tampered_shape(self):
        presentation = self._presentation()
        tampered = copy.deepcopy(presentation)
        tampered["interpretation_allowed"] = True
        self.assertFalse(is_valid_life_presentation(tampered))
        tampered = copy.deepcopy(presentation)
        tampered["stages"][0]["age_presentation"] = "presented"
        self.assertFalse(is_valid_life_presentation(tampered))
        tampered = copy.deepcopy(presentation)
        tampered["extra_key"] = True
        self.assertFalse(is_valid_life_presentation(tampered))
        tampered = copy.deepcopy(presentation)
        tampered["stages"] = tampered["stages"][:7]
        self.assertFalse(is_valid_life_presentation(tampered))

    def test_public_projection_round_trips(self):
        presentation = self._presentation()
        public = to_public_life_presentation(presentation)
        self.assertTrue(is_valid_life_presentation(public))
        self.assertEqual(public["variant"], VARIANT)
        self.assertEqual(public["unified"]["pillars"], F2_PILLARS)

    def test_section_ids_match_sibling_ids(self):
        self.assertEqual(
            [s["id"] for s in _synthetic_romance()["sections"]],
            list(ROMANCE_SECTION_IDS))
        self.assertEqual(
            [s["id"] for s in _synthetic_compatibility()["sections"]],
            list(COMPAT_SECTION_IDS))

    def test_live_real_chart(self):
        """Live test: real f2 chart through the real builders.

        Skips in the public checkout (no sealed data/), runs in sealed
        acceptance.
        """
        try:
            presentation = build_life_presentation_for(
                F2_BIRTH, 2025, traditional_role="male")
        except Exception as error:  # sealed data absent locally
            self.skipTest("live real-chart life presentation needs "
                          "sealed data: %s" % error)
            return
        self.assertTrue(is_valid_life_presentation(presentation))
        self.assertEqual(presentation["unified"]["pillars"], F2_PILLARS)
        self.assertEqual(presentation["dayun"]["status"], "presented")
        self.assertEqual(len(presentation["stages"]), 8)
        self.assertEqual(presentation["themes"]["bazi"]["variant"],
                         BAZI_VARIANT)


if __name__ == "__main__":
    unittest.main()
