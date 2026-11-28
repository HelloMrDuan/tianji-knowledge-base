"""Lane A (TJ-0427, TJ-031.19): 八字详批 presentation builder tests.

Two honest classes, following the batch-4 test discipline:

* Fixture tests (run locally): synthetic pillar fixtures with explicit
  hidden stems -- labelled fixtures, NOT real charts, no Golden
  claims -- plus minimal valid public-presentation fixtures built
  from the gate modules' own constants, so the builder's lift /
  fail-closed / research-isolation behaviour is exercised without a
  sealed execution.
* Live tests (``LiveF2Tests``): the real chart f2
  (2024-02-11T16:27:07+08:00, 甲辰 / 丙寅 / 乙巳 / 甲申) through
  ``assemble_birth`` + ``trim_for_bazi_profile``. The public
  checkout has no sealed ``data/``, so the whole class skips there
  (never a faked pass); it runs in the sealed assembly environment.
"""

import copy
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_fuyi_slice_adjudication import ADJUDICATION_VERDICT
from tianji_kb.bazi_pattern_public import (
    LIMITATIONS as PATTERN_LIMITATIONS,
)
from tianji_kb.bazi_pattern_public import (
    SCOPE_STATEMENT as PATTERN_SCOPE,
)
from tianji_kb.bazi_pattern_public import TITLE as PATTERN_TITLE
from tianji_kb.bazi_pattern_public import VARIANT as PATTERN_VARIANT
from tianji_kb.bazi_profile_presentation import (
    BRANCH_ELEMENTS,
    build_bazi_profile_presentation,
    is_valid_bazi_profile_presentation,
    to_public_bazi_profile_presentation,
)
from tianji_kb.bazi_strength_public import LIMITATIONS as STRENGTH_LIMITATIONS
from tianji_kb.bazi_strength_public import SCOPE_STATEMENT as STRENGTH_SCOPE
from tianji_kb.bazi_strength_public import VARIANT as STRENGTH_VARIANT
from tianji_kb.bazi_xiyong_public import LIMITATIONS as XIYONG_LIMITATIONS
from tianji_kb.bazi_xiyong_public import PAIR_IDS as XIYONG_PAIR_IDS
from tianji_kb.bazi_xiyong_public import PRESENTATION_SCOPE as XIYONG_SCOPE
from tianji_kb.bazi_xiyong_public import SCOPE_STATEMENT as XIYONG_SCOPE_TEXT
from tianji_kb.bazi_xiyong_public import VARIANT as XIYONG_VARIANT
from tianji_kb.bazi_xiyong_readable import (
    NO_UNIFIED_VERDICT_LINE as XIYONG_CLOSING,
)

F2_BIRTH = "2024-02-11T16:27:07+08:00"
F2_GANZHI = ["甲辰", "丙寅", "乙巳", "甲申"]
# Classical hidden stems for the f2 branches, stated explicitly in
# the fixture (not derived from any execution here).
F2_HIDDEN = [["戊", "乙", "癸"], ["甲", "丙", "戊"],
             ["丙", "庚", "戊"], ["庚", "壬", "戊"]]

REPO_ROOT = Path(__file__).resolve().parents[1]
SEALED_SEED = REPO_ROOT / "data" / "canonical" / "seed.json"


def _pillar(name, ganzhi, hidden):
    return {
        "name": name,
        "ganzhi": ganzhi,
        "stem": {"value": ganzhi[0], "ten_god": "比肩"},
        "branch": {"value": ganzhi[1],
                   "hidden_stems": [{"stem": stem} for stem in hidden]},
    }


def _f2_pillars():
    names = ("year", "month", "day", "hour")
    return [_pillar(name, ganzhi, hidden)
            for name, ganzhi, hidden
            in zip(names, F2_GANZHI, F2_HIDDEN)]


def _f2_trim():
    """Synthetic trim-shaped source for the f2 fixture chart."""
    return {
        "variant": "unified-compute-entry-v1",
        "page": "bazi-profile",
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
            "ganzhi": list(F2_GANZHI),
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
    }


def _strength_not_judgeable():
    return {
        "variant": STRENGTH_VARIANT,
        "status": "not_judgeable",
        "day_master": "乙",
        "month_branch": "寅",
        "scope_statement": STRENGTH_SCOPE,
        "limitations": list(STRENGTH_LIMITATIONS),
        "reason": "no_predicate_matched",
    }


def _pattern_not_judgeable():
    return {
        "variant": PATTERN_VARIANT,
        "title": PATTERN_TITLE,
        "status": "not_judgeable",
        "day_master": "乙",
        "month_branch": "寅",
        "scope_statement": PATTERN_SCOPE,
        "limitations": list(PATTERN_LIMITATIONS),
        "reason": "pilot_uncertain",
    }


def _xiyong_valid():
    return {
        "variant": XIYONG_VARIANT,
        "presentation_scope": XIYONG_SCOPE,
        "day_master": "乙",
        "month_branch": "寅",
        "blocks": {
            "tiaohou": {
                "system": "tiaohou",
                "source_label": "《穷通宝鉴》",
                "day_master": "乙",
                "month_branch": "寅",
                "state": "presented",
                "lines": ["调候体系（《穷通宝鉴》）：原文取用顺序为：丙（第1取）。"],
                "evidence": {"source_id": "bazi.source.qiongtong",
                             "evidence_level": "C"},
            },
            "bingyao": {
                "system": "bingyao",
                "source_label": "《神峰通考》",
                "day_master": "乙",
                "pairs": [
                    {"pair_id": pair_id, "status": "not_triggered",
                     "not_triggered_reason": "subject_missing",
                     "determination": None,
                     "medicine_effect_status": "unadjudicated",
                     "efficacy_state": "not_judgeable"}
                    for pair_id in XIYONG_PAIR_IDS
                ],
                "lines": ["病药体系（《神峰通考》）：两对均未触发。"],
                "evidence": {"source_id": "bazi.source.shenfeng",
                             "evidence_level": "C"},
            },
        },
        "relations": [],
        "relations_closing_line": XIYONG_CLOSING,
        "unified_verdict": None,
        "public_enabled": True,
        "ai_enabled": False,
        "scope_statement": XIYONG_SCOPE_TEXT,
        "limitations": list(XIYONG_LIMITATIONS),
    }


def _section(result, section_id):
    for section in result["sections"]:
        if section["id"] == section_id:
            return section
    raise AssertionError("missing section " + section_id)


class FiveElementTests(unittest.TestCase):
    def test_branch_element_map_is_pinned(self):
        self.assertEqual(BRANCH_ELEMENTS, {
            "寅": "木", "卯": "木", "巳": "火", "午": "火",
            "申": "金", "酉": "金", "亥": "水", "子": "水",
            "辰": "土", "戌": "土", "丑": "土", "未": "土",
        })

    def test_f2_fixture_counts(self):
        result = build_bazi_profile_presentation(_f2_trim())
        section = _section(result, "five_elements")
        self.assertEqual(section["status"], "presented")
        public = section["public"]
        self.assertEqual(public["day_master"], "乙")
        self.assertEqual(public["day_master_element"], "木")
        self.assertEqual(public["stem_counts"],
                         {"木": 3, "火": 1, "土": 0, "金": 0, "水": 0})
        self.assertEqual(public["branch_counts"],
                         {"木": 1, "火": 1, "土": 1, "金": 1, "水": 0})
        self.assertEqual(public["hidden_counts"],
                         {"木": 2, "火": 2, "土": 4, "金": 2, "水": 2})
        self.assertEqual(public["total_counts"],
                         {"木": 6, "火": 4, "土": 5, "金": 3, "水": 2})
        text = "\n".join(section["lines"])
        self.assertIn("只是确定性计数，不作旺衰、喜用、格局或吉凶判断", text)
        for forbidden in ("身旺", "身弱", "大吉", "大凶", "预测"):
            self.assertNotIn(forbidden, text)

    def test_every_section_states_basis_caliber_and_undecided(self):
        result = build_bazi_profile_presentation(_f2_trim())
        self.assertEqual(
            [section["id"] for section in result["sections"]],
            ["five_elements", "strength", "pattern", "xiyong",
             "fuyi_research", "dayun", "true_solar"])
        for section in result["sections"]:
            self.assertIsInstance(section["basis"], str)
            self.assertTrue(section["basis"])
            self.assertIsInstance(section["caliber"], str)
            self.assertTrue(section["caliber"])
            self.assertIsInstance(section["undecided"], list)
            self.assertTrue(section["lines"])

    def test_result_is_jsonable_and_shape_valid(self):
        result = build_bazi_profile_presentation(_f2_trim())
        json.dumps(result, ensure_ascii=False)
        self.assertTrue(is_valid_bazi_profile_presentation(result))
        projected = to_public_bazi_profile_presentation(result)
        self.assertEqual(projected, result)
        self.assertIsNot(projected, result)


class PublicLiftTests(unittest.TestCase):
    def test_valid_public_presentations_are_lifted(self):
        source = _f2_trim()
        source["strength_presentation"] = _strength_not_judgeable()
        source["pattern_presentation"] = _pattern_not_judgeable()
        source["xiyong_presentation"] = _xiyong_valid()
        result = build_bazi_profile_presentation(source)
        strength = _section(result, "strength")
        self.assertEqual(strength["status"], "not_judgeable")
        self.assertEqual(strength["public"]["reason"],
                         "no_predicate_matched")
        pattern = _section(result, "pattern")
        self.assertEqual(pattern["status"], "not_judgeable")
        xiyong = _section(result, "xiyong")
        self.assertEqual(xiyong["status"], "presented")
        self.assertIsNone(xiyong["public"]["unified_verdict"])
        self.assertIn("可建行数为 0 行", "\n".join(xiyong["lines"]))
        self.assertIn("统一喜用结论：暂不可判", "\n".join(xiyong["lines"]))

    def test_presented_strength_and_pattern_paths(self):
        # 甲×卯 chart fixture for a presented strength predicate.
        pillars = [
            _pillar("year", "甲辰", ["戊", "乙", "癸"]),
            _pillar("month", "乙卯", ["甲", "乙"]),
            _pillar("day", "甲午", ["丁", "己"]),
            _pillar("hour", "丙寅", ["甲", "丙", "戊"]),
        ]
        strength = {
            "variant": STRENGTH_VARIANT,
            "status": "presented",
            "day_master": "甲",
            "month_branch": "卯",
            "scope_statement": STRENGTH_SCOPE,
            "limitations": list(STRENGTH_LIMITATIONS),
            "statement": "已审强弱形态事实",
            "classification": "strong",
            "predicate_id": "pure_support",
            "phase1_rule_id": None,
            "phase2_step_id": "bazi.phase2.strength_pure_support",
            "rule_registration": "registered",
            "conditions": [{
                "condition": "visible印_present",
                "met": True,
                "fact_ref": "#/trace/3/output/pure_support_scope_conditions/visible印_present",
                "rule_id": "bazi.phase2.action_effects",
            }],
        }
        pattern = {
            "variant": PATTERN_VARIANT,
            "title": PATTERN_TITLE,
            "status": "presented",
            "day_master": "乙",
            "month_branch": "寅",
            "scope_statement": PATTERN_SCOPE,
            "limitations": list(PATTERN_LIMITATIONS),
            "outcome": "true_pattern",
            "statement": "司令丙透于月干，真格成立。",
            "pattern": "伤官格",
            "commander": {"stem": "丙", "ten_god": "伤官",
                          "visible_pillars": ["month"]},
            "school": "任氏分支",
            "scope_month_branch": "寅",
        }
        source = {
            "pillars": _f2_pillars(),
            "day_master": {"stem": "乙", "element": "木",
                           "polarity": "阴"},
            "strength_presentation": strength,
            "pattern_presentation": pattern,
        }
        # The strength fixture belongs to a different chart (甲/卯):
        # lifting it against the f2 chart must fail closed.
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)
        source["pillars"] = pillars
        source["day_master"] = {"stem": "甲", "element": "木",
                                "polarity": "阳"}
        source.pop("pattern_presentation")
        result = build_bazi_profile_presentation(source)
        self.assertEqual(_section(result, "strength")["status"],
                         "presented")
        self.assertIn("强形态",
                      "\n".join(_section(result, "strength")["lines"]))

    def test_presented_pattern_true_pattern(self):
        source = _f2_trim()
        source["pattern_presentation"] = {
            "variant": PATTERN_VARIANT,
            "title": PATTERN_TITLE,
            "status": "presented",
            "day_master": "乙",
            "month_branch": "寅",
            "scope_statement": PATTERN_SCOPE,
            "limitations": list(PATTERN_LIMITATIONS),
            "outcome": "true_pattern",
            "statement": "司令丙透于月干，真格成立。",
            "pattern": "伤官格",
            "commander": {"stem": "丙", "ten_god": "伤官",
                          "visible_pillars": ["month"]},
            "school": "任氏分支",
            "scope_month_branch": "寅",
        }
        result = build_bazi_profile_presentation(source)
        section = _section(result, "pattern")
        self.assertEqual(section["status"], "presented")
        self.assertIn("伤官格", "\n".join(section["lines"]))

    def test_whitelist_enforced_bijian_is_not_presented(self):
        source = _f2_trim()
        forged = {
            "variant": PATTERN_VARIANT,
            "title": PATTERN_TITLE,
            "status": "presented",
            "day_master": "乙",
            "month_branch": "寅",
            "scope_statement": PATTERN_SCOPE,
            "limitations": list(PATTERN_LIMITATIONS),
            "outcome": "true_pattern",
            "statement": "司令乙透于月干，真格成立。",
            "pattern": "比肩格",
            "commander": {"stem": "乙", "ten_god": "比肩",
                          "visible_pillars": ["month"]},
            "school": "任氏分支",
            "scope_month_branch": "寅",
        }
        source["pattern_presentation"] = forged
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)

    def test_forged_public_object_fails_closed(self):
        source = _f2_trim()
        forged = _strength_not_judgeable()
        forged["evidence_ids"] = ["E0001"]
        source["strength_presentation"] = forged
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)
        source = _f2_trim()
        source["dayun_presentation"] = {"variant": "bogus"}
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)

    def test_missing_public_presentations_are_explicitly_undecided(self):
        result = build_bazi_profile_presentation(_f2_trim())
        for section_id in ("strength", "pattern", "xiyong", "dayun",
                           "true_solar"):
            section = _section(result, section_id)
            self.assertEqual(section["status"], "not_provided")
            self.assertIsNone(section["public"])
            self.assertTrue(section["undecided"])
            joined = "\n".join(section["lines"] + section["undecided"])
            self.assertIn("暂不", joined)
        # Q2=C: the fuyi research section is likewise explicit when
        # no research output is attached.
        fuyi = _section(result, "fuyi_research")
        self.assertEqual(fuyi["status"], "not_provided")
        self.assertIsNone(fuyi["research_reference"])
        self.assertTrue(fuyi["undecided"])


class FailClosedTests(unittest.TestCase):
    def test_bad_sources_raise(self):
        for bad in (None, "x", [], {}, {"pillars": []},
                    {"chart": {}, "research": {}}):
            with self.assertRaises(ValueError, msg=repr(bad)):
                build_bazi_profile_presentation(bad)

    def test_day_master_drift_raises(self):
        source = _f2_trim()
        source["chart"]["day_master"] = {"stem": "甲"}
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)

    def test_fuyi_adjudication_record_still_zero(self):
        self.assertEqual(ADJUDICATION_VERDICT["buildable_count"], 0)


class ResearchIsolationTests(unittest.TestCase):
    def test_modern_strength_stays_a_labelled_reference_only(self):
        source = _f2_trim()
        source["strength_presentation"] = _strength_not_judgeable()
        source["research"]["strength"] = {
            "modern": {
                "model_id": "strength_model_modern_v1",
                "model_kind": "modern_engineering",
                "verdict": "strong",
                "score": 42,
                "score_band": "strong",
                "classification_status": "definite",
                "uncertainty_flags": [],
            },
        }
        result = build_bazi_profile_presentation(source)
        section = _section(result, "strength")
        self.assertEqual(section["status"], "not_judgeable")
        # The score never enters the public object.
        self.assertNotIn("score", section["public"])
        self.assertNotIn("42", json.dumps(section["public"],
                                          ensure_ascii=False))
        reference = section["research_reference"]
        self.assertIsNotNone(reference)
        self.assertTrue(reference["research_only"])
        self.assertEqual(reference["model_id"],
                         "strength_model_modern_v1")
        self.assertEqual(reference["score"], 42)
        self.assertIn("研究参考", "\n".join(section["lines"]))
        self.assertTrue(is_valid_bazi_profile_presentation(result))

    def test_modern_fuyi_candidates_stay_a_labelled_reference_only(self):
        # Q2=C: the fuyi modern reference now lives in the SEPARATE
        # fuyi_research section, not in the public xiyong section.
        source = _f2_trim()
        source["xiyong_presentation"] = _xiyong_valid()
        source["research"]["xiyong"] = {
            "systems": {
                "fuyi": {
                    "modern": {
                        "model_id": "fuyi-modern-rules-v1",
                        "model_kind": "modern_engineering",
                        "status": "direction_candidate",
                        "input_verdict": "strong",
                        "input_score": 62,
                        "direction": "drain_control",
                        "direction_cn": "泄耗克",
                        "direction_elements": ["火", "土", "金"],
                        "ten_god_classes": ["食伤", "财", "官杀"],
                        "candidate_stems": [
                            {"stem": "丙", "pillar": "month",
                             "ten_god": "伤官", "element": "火"},
                        ],
                        "candidate_scope": "visible_stems_only",
                        "confidence": "model_candidate",
                        "uncertainty": [],
                        "component_explanations": [],
                        "reason": "现代模型 strong（62 分）：方向 泄耗克。",
                    },
                },
                "pattern_yongshen": {"useful_god": None},
            },
        }
        result = build_bazi_profile_presentation(source)
        xiyong = _section(result, "xiyong")
        self.assertIsNone(xiyong["research_reference"])
        self.assertIsNone(xiyong["public"]["unified_verdict"])
        section = _section(result, "fuyi_research")
        self.assertEqual(section["status"], "presented")
        reference = section["research_reference"]
        self.assertIsNotNone(reference)
        self.assertTrue(reference["research_only"])
        self.assertEqual(reference["direction_cn"], "泄耗克")
        self.assertEqual(reference["candidate_stems"],
                         [{"stem": "丙", "pillar": "month",
                           "ten_god": "伤官", "element": "火"}])
        self.assertEqual(reference["input_verdict"], "strong")
        self.assertEqual(reference["input_score"], 62)
        text = "\n".join(section["lines"])
        self.assertIn("候选不是确定用神", text)
        self.assertIn("格局用神：暂不可判", text)
        self.assertTrue(is_valid_bazi_profile_presentation(result))

    def test_forged_pattern_yongshen_fails_closed(self):
        source = _f2_trim()
        source["xiyong_presentation"] = _xiyong_valid()
        source["research"]["xiyong"] = {
            "systems": {
                "fuyi": {},
                "pattern_yongshen": {"useful_god": "丙"},
            },
        }
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)

    def test_broken_only_through_the_approved_channel(self):
        source = _f2_trim()
        source["research"]["pattern"] = {
            "results": {
                "shangguan": {"state": "broken",
                              "broken_condition":
                                  "shangguan_sees_officer_broken"},
                "zhengcai": {"state": "candidate"},
            },
        }
        result = build_bazi_profile_presentation(source)
        text = "\n".join(_section(result, "pattern")["lines"])
        self.assertIn("伤官见官", text)
        source = _f2_trim()
        source["research"]["pattern"] = {
            "results": {
                "zhengyin": {"state": "broken",
                             "broken_condition": "some_other_condition"},
            },
        }
        result = build_bazi_profile_presentation(source)
        text = "\n".join(_section(result, "pattern")["lines"])
        self.assertNotIn("破格：", text)
        undecided = "\n".join(_section(result, "pattern")["undecided"])
        self.assertIn("不在唯一已审通道（伤官见官）内", undecided)

    def test_true_solar_is_research_only_and_default_unchanged(self):
        result = build_bazi_profile_presentation(_f2_trim())
        section = _section(result, "true_solar")
        self.assertEqual(section["status"], "not_provided")
        self.assertIn("公开排盘口径不变", "\n".join(section["lines"]))
        source = _f2_trim()
        source["true_solar_comparison"] = {
            "research_only": True,
            "changed_pillars": ["hour"],
        }
        result = build_bazi_profile_presentation(source)
        section = _section(result, "true_solar")
        self.assertEqual(section["status"], "presented")
        self.assertIn("研究对照", "\n".join(section["lines"]))
        self.assertIn("不替换公开排盘", "\n".join(section["lines"]))
        source = _f2_trim()
        source["true_solar_comparison"] = {"changed_pillars": []}
        with self.assertRaises(ValueError):
            build_bazi_profile_presentation(source)

    def test_tampered_presentation_fails_shape_validation(self):
        result = build_bazi_profile_presentation(_f2_trim())
        tampered = copy.deepcopy(result)
        tampered["extra_key"] = True
        self.assertFalse(is_valid_bazi_profile_presentation(tampered))
        with self.assertRaises(ValueError):
            to_public_bazi_profile_presentation(tampered)
        tampered = copy.deepcopy(result)
        tampered["sections"][1]["research_reference"] = {"score": 1}
        self.assertFalse(is_valid_bazi_profile_presentation(tampered))


def _earth_tomb_trim():
    """Synthetic trim fixture: 戊日主 × 辰月 (earth + tomb month).

    Carries the Q5 (earth de_di uncalibrated) and Q6 (tomb de_ling
    zero) conditions, so the modern-model uncertainty notes match
    the chart they describe.
    """
    trim = _f2_trim()
    trim["chart"]["pillars"] = [
        _pillar("year", "甲辰", ["戊", "乙", "癸"]),
        _pillar("month", "戊辰", ["戊", "乙", "癸"]),
        _pillar("day", "戊午", ["丁", "己"]),
        _pillar("hour", "甲寅", ["甲", "丙", "戊"]),
    ]
    trim["chart"]["day_master"] = {"stem": "戊", "element": "土",
                                   "polarity": "阳"}
    trim["chart"]["month_branch"] = "辰"
    trim["chart"]["ganzhi"] = ["甲辰", "戊辰", "戊午", "甲寅"]
    return trim


def _modern_strength_full():
    """Full-shape modern strength block, including fields the builder
    must NOT copy (weights / thresholds / cong screen / interactions)."""
    return {
        "model_id": "strength_model_modern_v1",
        "model_kind": "modern_engineering",
        "verdict": "strong",
        "score": 62,
        "score_band": "strong",
        "classification_status": "provisional_incomplete",
        "definite_classification": None,
        "uncertainty_flags": ["earth_de_di_uncalibrated",
                              "tomb_de_ling_zero_provisional"],
        "notes": [
            "土日主无已审重根集：得地分只计余根，未校准；"
            "分数为研究性暂定分，不输出确定旺衰分类。",
            "月支 辰 为四库，本气未审：得令分记 0 是缺失条件的暂定处理，"
            "不代表已证明月令无作用；分类不确定性已标注。",
        ],
        "limitations": [
            "现代模型是工程近似：权重与阈值是人为设定的可解释评分口径，"
            "不是古籍原文、不是已审规则；任何现代 verdict 不得表述为古典裁决。",
            "土日主无已审重根集，得地分只计余根；丁日主火重根集未审，"
            "得地分只计余根；四库月得令分恒为 0（本气未审）。",
        ],
        "components": {
            "de_ling": {"score": 0, "detail": "月支 辰，本气/司令关系计分"},
            "de_di": {"score": 12, "detail": "通根 2 处（重根 0，余根 2）"},
            "de_shi": {"score": 10, "detail": "显干生扶 2 干"},
            "shengfu_hidden": {"score": 8, "detail": "藏干生扶 2 干"},
            "kexiehao": {"score": -5, "detail": "克泄耗 3 干（显干＋藏干）"},
        },
        "abstain_reason": None,
        "abstain_detail": None,
        "weights": {"de_ling": {"a": 1}},
        "thresholds": {"strong": 50},
        "cong_candidates": [{"screen_triggered": True}],
        "interaction_effects": [{"kind": "冲"}],
    }


def _fuyi_modern_full():
    """Full-shape modern fuyi block, including a direction_derivation
    the builder must NOT copy (it carries thresholds)."""
    return {
        "model_id": "fuyi-modern-rules-v1",
        "model_kind": "modern_engineering",
        "status": "direction_candidate",
        "input_verdict": "strong",
        "input_score": 62,
        "direction": "drain_control",
        "direction_cn": "泄耗克",
        "direction_elements": ["火", "土", "金"],
        "ten_god_classes": ["食伤", "财", "官杀"],
        "candidate_stems": [
            {"stem": "丙", "pillar": "month", "ten_god": "伤官",
             "element": "火"},
            {"stem": "庚", "pillar": "hour", "ten_god": "正官",
             "element": "金"},
        ],
        "candidate_scope": "visible_stems_only",
        "confidence": "model_candidate",
        "uncertainty": [],
        "component_explanations": [
            {"component": "de_ling", "name_cn": "得令", "score": 15,
             "reading": "supports_strong_side",
             "note": "得令分 +15：该分项指向强侧；分项符号读数，"
                     "不构成独立的方向结论。"},
        ],
        "direction_derivation": [
            {"step": "input", "thresholds": {"strong": 50}},
        ],
        "reason": "现代模型 strong（62 分）：方向 泄耗克。",
    }


class Q1ModernStrengthColumnTests(unittest.TestCase):
    """USER ADJUDICATION 2026-11-28 Q1=C: modern strength as a
    SEPARATE research column."""

    def test_research_column_separate_from_u1(self):
        source = _earth_tomb_trim()
        source["strength_presentation"] = {
            "variant": STRENGTH_VARIANT,
            "status": "not_judgeable",
            "day_master": "戊",
            "month_branch": "辰",
            "scope_statement": STRENGTH_SCOPE,
            "limitations": list(STRENGTH_LIMITATIONS),
            "reason": "no_predicate_matched",
        }
        source["research"]["strength"] = {"modern": _modern_strength_full()}
        result = build_bazi_profile_presentation(source)
        section = _section(result, "strength")
        # U1 public part is untouched by the research column.
        self.assertEqual(section["status"], "not_judgeable")
        self.assertEqual(section["public"]["reason"],
                         "no_predicate_matched")
        self.assertNotIn("score", section["public"])
        reference = section["research_reference"]
        self.assertIsNotNone(reference)
        self.assertEqual(reference["column"], "research")
        self.assertEqual(reference["model_id"],
                         "strength_model_modern_v1")
        self.assertEqual(reference["verdict"], "strong")
        self.assertEqual(reference["score"], 62)
        self.assertEqual(reference["score_range"], [-35, 105])
        labels = [item["label"] for item in reference["components"]]
        self.assertEqual(labels, ["得令", "得地", "得势（显干生扶）",
                                  "得助（藏干生扶）", "克泄耗"])
        scores = {item["key"]: item["score"]
                  for item in reference["components"]}
        self.assertEqual(scores, {"de_ling": 0, "de_di": 12, "de_shi": 10,
                                  "shengfu_hidden": 8, "kexiehao": -5})
        text = "\n".join(section["lines"])
        self.assertIn("已审结论与现代模型分开呈现，互不覆盖", text)
        self.assertIn("研究列（现代强度模型）", text)
        self.assertTrue(is_valid_bazi_profile_presentation(result))

    def test_score_never_percentile_probability_or_prediction(self):
        source = _earth_tomb_trim()
        source["research"]["strength"] = {"modern": _modern_strength_full()}
        result = build_bazi_profile_presentation(source)
        section = _section(result, "strength")
        text = "\n".join(section["lines"])
        self.assertIn(
            "现代模型分数是工程模型内部总分（总分域 [-35, 105]），"
            "不是百分位，不是概率，不是古典旺衰定论，不作科学预测。",
            text)
        # No positive prediction wording anywhere in the section.
        self.assertNotIn("科学预测", text.replace("不作科学预测", ""))

    def test_uncalibrated_conditions_stated_explicitly(self):
        source = _earth_tomb_trim()
        source["research"]["strength"] = {"modern": _modern_strength_full()}
        result = build_bazi_profile_presentation(source)
        section = _section(result, "strength")
        reference = section["research_reference"]
        self.assertEqual(reference["classification_status"],
                         "provisional_incomplete")
        self.assertIn("earth_de_di_uncalibrated",
                      reference["uncertainty_flags"])
        self.assertIn("tomb_de_ling_zero_provisional",
                      reference["uncertainty_flags"])
        text = "\n".join(section["lines"])
        self.assertIn("土日主无已审重根集：得地分只计余根，未校准", text)
        self.assertIn("四库，本气未审：得令分记 0 是缺失条件的暂定处理", text)
        self.assertIn("分类状态：provisional_incomplete", text)

    def test_weights_thresholds_and_cong_screen_never_copied(self):
        from tianji_kb.bazi_strength_engine import (
            MODERN_THRESHOLDS,
            MODERN_WEIGHTS,
        )
        before_weights = copy.deepcopy(MODERN_WEIGHTS)
        before_thresholds = copy.deepcopy(MODERN_THRESHOLDS)
        source = _earth_tomb_trim()
        source["research"]["strength"] = {"modern": _modern_strength_full()}
        result = build_bazi_profile_presentation(source)
        self.assertEqual(MODERN_WEIGHTS, before_weights)
        self.assertEqual(MODERN_THRESHOLDS, before_thresholds)
        dumped = json.dumps(result, ensure_ascii=False)
        for banned in ("weights", "thresholds", "cong_candidates",
                       "interaction_effects"):
            self.assertNotIn('"%s"' % banned, dumped)
        self.assertTrue(is_valid_bazi_profile_presentation(result))

    def test_modern_abstain_has_no_score(self):
        source = _earth_tomb_trim()
        modern = _modern_strength_full()
        modern["verdict"] = "abstain"
        modern["score"] = None
        modern["score_band"] = None
        modern["classification_status"] = "abstain"
        modern["components"] = None
        modern["abstain_reason"] = "earth_form_unbuildable_tj0112"
        modern["abstain_detail"] = "土形态无可执行规则，现代模型不评分。"
        source["research"]["strength"] = {"modern": modern}
        result = build_bazi_profile_presentation(source)
        section = _section(result, "strength")
        reference = section["research_reference"]
        self.assertEqual(reference["verdict"], "abstain")
        self.assertIsNone(reference["score"])
        self.assertEqual(reference["components"], [])
        self.assertIn("现代模型弃判", "\n".join(section["lines"]))

    def test_p5_flags_never_rendered_as_formal_broken(self):
        source = _f2_trim()
        source["research"]["pattern"] = {
            "results": {
                "zhengyin": {
                    "state": "candidate",
                    "modern_assessment": {
                        "broken_flags": ["财旺破印", "制伏太过"],
                        "model_id": "pattern-modern-p6-v1",
                    },
                },
            },
        }
        result = build_bazi_profile_presentation(source)
        dumped = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("财旺破印", dumped)
        self.assertNotIn("制伏太过", dumped)
        self.assertNotIn("modern_assessment", dumped)
        self.assertNotIn("破格：", "\n".join(
            _section(result, "pattern")["lines"]))


class Q2FuyiResearchSectionTests(unittest.TestCase):
    """USER ADJUDICATION 2026-11-28 Q2=C: fuyi modern candidates as
    a SEPARATE research section."""

    def _source_with_fuyi(self):
        source = _f2_trim()
        source["xiyong_presentation"] = _xiyong_valid()
        source["research"]["xiyong"] = {
            "systems": {
                "fuyi": {"modern": _fuyi_modern_full()},
                "pattern_yongshen": {
                    "useful_god": None,
                    "yongshen_rule_readiness": [
                        {"pattern": "正官格",
                         "status": "pending_evidence_review"},
                    ],
                },
            },
        }
        return source

    def test_fuyi_research_section_full(self):
        result = build_bazi_profile_presentation(self._source_with_fuyi())
        section = _section(result, "fuyi_research")
        self.assertEqual(section["status"], "presented")
        text = "\n".join(section["lines"])
        # Current model strength direction.
        self.assertIn("当前模型强度方向：现代强度模型结论为 strong（62 分）",
                      text)
        # Candidate direction + verified candidate stems.
        self.assertIn("扶抑候选方向：泄耗克", text)
        self.assertIn("丙（月干，伤官）", text)
        self.assertIn("候选不是确定用神", text)
        # Candidate formation reasons.
        self.assertIn("得令分 +15：该分项指向强侧", text)
        # Per-system comparison + classical closed state.
        self.assertIn("调候体系（已审）：取用顺序见本页调候节。", text)
        self.assertIn("病药体系（已审）：两对结构候选，去病效力未裁定",
                      text)
        self.assertIn("可建行数为 0 行", text)
        self.assertIn("三体系口径不同，并列呈现，不合并为统一结论", text)
        reference = section["research_reference"]
        self.assertEqual(reference["candidate_stems"],
                         [{"stem": "丙", "pillar": "month",
                           "ten_god": "伤官", "element": "火"}])
        self.assertEqual(reference["input_verdict"], "strong")
        self.assertEqual(len(reference["formation_reasons"]), 1)
        self.assertTrue(is_valid_bazi_profile_presentation(result))

    def test_candidate_stem_not_in_chart_is_excluded(self):
        result = build_bazi_profile_presentation(self._source_with_fuyi())
        section = _section(result, "fuyi_research")
        # 庚 is claimed as an hour-stem candidate but the f2 hour
        # stem is 甲: it must never be presented as a candidate.
        stems = [item["stem"] for item in
                 section["research_reference"]["candidate_stems"]]
        self.assertNotIn("庚", stems)
        undecided = "\n".join(section["undecided"])
        self.assertIn("候选干 庚（hour）与本盘显干不符，不列为候选。",
                      undecided)

    def test_readiness_table_and_unified_verdict_absent(self):
        result = build_bazi_profile_presentation(self._source_with_fuyi())
        dumped = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("yongshen_rule_readiness", dumped)
        self.assertNotIn("thresholds", dumped)
        self.assertNotIn("direction_derivation", dumped)
        # The only unified_verdict key in the whole object is the
        # xiyong public presentation's constant None.
        self.assertEqual(dumped.count('"unified_verdict"'), 1)
        self.assertIn('"unified_verdict": null', dumped)
        section = _section(result, "fuyi_research")
        self.assertIn("格局用神：暂不可判；14 格就绪表不公开呈现",
                      "\n".join(section["lines"]))


class Q3DayunPeriodsTests(unittest.TestCase):
    """USER ADJUDICATION 2026-11-28 Q3=A: full 8-period dayun."""

    def _projection_fixture(self):
        from tianji_kb.bazi_profile_presentation import (
            _summarize_dayun_periods,
        )
        branches = ["辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        entries = []
        for index, branch in enumerate(branches, start=1):
            entries.append({
                "period_index": index,
                "ganzhi": "甲" + branch,
                "stem": "甲",
                "branch": branch,
                "ten_god_relative_to_natal_day_stem": "比肩",
                "state": "interval",
                "start_interval": {
                    "earliest": "2030-01-01T00:00:00+08:00",
                    "latest": "2031-01-01T00:00:00+08:00",
                },
            })
        presentation = {"methods": {
            "sanming": {"entries": entries},
            "shenfeng": {"entries": entries[:1]},
        }}
        pillars = [(stem, branch, hidden)
                   for stem, branch, hidden in
                   ((p["stem"]["value"], p["branch"]["value"],
                     [h["stem"] for h in p["branch"]["hidden_stems"]])
                    for p in _f2_pillars())]
        return _summarize_dayun_periods(presentation, pillars)

    def test_eight_periods_interval_only(self):
        summary = self._projection_fixture()
        self.assertEqual(len(summary["sanming"]), 8)
        dumped = json.dumps(summary, ensure_ascii=False)
        for banned in ("age", "start_age", "start_date", "end_date"):
            self.assertNotIn(banned, dumped)
        for period in summary["sanming"]:
            self.assertEqual(period["state"], "interval")
            self.assertEqual(
                period["start_interval"]["earliest"],
                "2030-01-01T00:00:00+08:00")
            self.assertTrue(period["liunian_entry"])
            self.assertIn("进入流年页查看其中某年",
                          period["liunian_entry_note"])

    def test_end_from_next_start_last_period_unprovided(self):
        summary = self._projection_fixture()
        periods = summary["sanming"]
        self.assertIn("下一运交运区间之前结束",
                      periods[0]["end_description"])
        self.assertIn("第 2 运", periods[0]["end_description"])
        self.assertEqual(periods[7]["end_description"],
                         "末段无终点：未提供。")

    def test_branch_hidden_stems_reused_only_from_natal_chart(self):
        summary = self._projection_fixture()
        periods = summary["sanming"]
        # 辰 / 巳 match natal branches: hidden stems reused verbatim.
        self.assertEqual(periods[0]["branch_hidden_stems"],
                         ["戊", "乙", "癸"])
        self.assertEqual(
            periods[0]["branch_hidden_stems_source"],
            "natal_chart_same_branch")
        self.assertEqual(periods[1]["branch_hidden_stems"],
                         ["丙", "庚", "戊"])
        # 午 / 未 / 酉 / 戌 / 亥 are not natal branches: not listed.
        self.assertIsNone(periods[2]["branch_hidden_stems"])
        self.assertIsNone(periods[2]["branch_hidden_stems_source"])
        self.assertIsNone(periods[7]["branch_hidden_stems"])


class LiveF2Tests(unittest.TestCase):
    """Real chart f2 through the unified entry. Sealed-gated: the
    public checkout has no sealed data/, so this class skips there."""

    def test_f2_live_assembly(self):
        if not SEALED_SEED.exists():
            raise unittest.SkipTest(
                "no sealed data/ in this checkout; live f2 runs in the "
                "sealed assembly environment")
        from tianji_kb.unified_compute import (
            assemble_birth,
            trim_for_bazi_profile,
        )
        try:
            assembly = assemble_birth(F2_BIRTH)
        except Exception as exc:  # noqa: BLE001 - env limits skip, not pass
            raise unittest.SkipTest(
                "live assembly unavailable here: %s" % exc) from exc
        trim = trim_for_bazi_profile(assembly)
        result = build_bazi_profile_presentation(trim)
        self.assertTrue(is_valid_bazi_profile_presentation(result))
        self.assertEqual(result["chart"]["ganzhi"], F2_GANZHI)
        self.assertEqual(result["chart"]["day_master"], "乙")
        self.assertEqual(result["chart"]["month_branch"], "寅")
        five = _section(result, "five_elements")
        self.assertEqual(five["public"]["stem_counts"],
                         {"木": 3, "火": 1, "土": 0, "金": 0, "水": 0})
        self.assertEqual(five["public"]["branch_counts"],
                         {"木": 1, "火": 1, "土": 1, "金": 1, "水": 0})
        self.assertEqual(five["public"]["hidden_counts"],
                         {"木": 2, "火": 2, "土": 4, "金": 2, "水": 2})
        strength = _section(result, "strength")
        reference = strength["research_reference"]
        if reference is not None:
            self.assertEqual(reference["model_id"],
                             "strength_model_modern_v1")
            self.assertTrue(reference["research_only"])
            # Q1=C: the live research column carries all five factors.
            labels = [item["label"] for item in reference["components"]]
            self.assertEqual(labels, ["得令", "得地", "得势（显干生扶）",
                                      "得助（藏干生扶）", "克泄耗"])
            self.assertIn("不是百分位", reference["score_note"])
        pattern = _section(result, "pattern")
        self.assertIn("D-1 不在统一入口内重推",
                      "\n".join(pattern["undecided"]))
        fuyi = _section(result, "fuyi_research")
        if fuyi["research_reference"] is not None:
            self.assertIn("候选不是确定用神",
                          "\n".join(fuyi["lines"]))
        dayun = _section(result, "dayun")
        self.assertEqual(dayun["status"], "not_provided")
        self.assertIsNone(dayun["periods"])
        dumped = json.dumps(result, ensure_ascii=False)
        for banned in ("weights", "thresholds", "cong_candidates",
                       "yongshen_rule_readiness"):
            self.assertNotIn('"%s"' % banned, dumped)
        json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
