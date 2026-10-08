"""Explicit opt-in historical year-stem / traditional-role Dayun direction candidate.

The caller deliberately selects a historical role category; it must never be
inferred from a person's identity, pronouns, DOB, or real-world sex. The rule is
legacy research and not an adjudicated Phase2 Dayun rule.
"""
from .foundations import STEMS, ganzhi_index

VARIANT = "bazi-dayun-year-stem-traditional-role-research-v1"
YANG_STEMS = frozenset("甲丙戊庚壬")
YIN_STEMS = frozenset("乙丁己辛癸")
ROLES = ("male", "female")


def traditional_direction(year_ganzhi, *, traditional_role):
    """Calculate only the legacy four-case direction after explicit selection."""
    if type(year_ganzhi) is not str:
        raise ValueError("Expected a valid natal year Ganzhi")
    ganzhi_index(year_ganzhi)  # Reject forged or invalid combinations.
    if type(traditional_role) is not str or traditional_role not in ROLES:
        raise ValueError("Explicit traditional_role=male|female is required")
    stem = year_ganzhi[0]
    if stem not in YANG_STEMS | YIN_STEMS:
        raise ValueError("Invalid natal year stem")
    polarity = "yang" if stem in YANG_STEMS else "yin"
    forward = (polarity == "yang" and traditional_role == "male") or (
        polarity == "yin" and traditional_role == "female")
    return {
        "variant": VARIANT,
        "year_ganzhi": year_ganzhi,
        "year_stem": stem,
        "year_stem_polarity": polarity,
        "traditional_role": traditional_role,
        "traditional_role_selection": "explicit_historical_category_not_inferred_identity",
        "direction": "forward" if forward else "backward",
        "direction_origin": "opt_in_traditional_year_stem_role_candidate",
        "rule_review_status": "legacy_candidate_unreviewed",
        "source_reference": {
            "path": "data/canonical/bazi/dayun_v1.json",
            "provenance": "jinchenma94/bazi-skill/references/dayun-rules.md",
            "level": "modern_implementation_not_classical_evidence"
        },
        "natal_year_stem_rule_id": None,
        "direction_rule_match": None,
        "classical_direction_evidence_approved": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "历史年干阴阳与传统角色分类的四种方向候选；角色只能由用户主动选择，非现实身份认定或经审定的唯一规则。"
    }
