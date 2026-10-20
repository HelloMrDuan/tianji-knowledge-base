"""Explicit opt-in historical year-stem / traditional-role Dayun direction candidate.

The caller deliberately selects a historical role category; it must never be
inferred from a person's identity, pronouns, DOB, or real-world sex. The rule is
legacy research and not an adjudicated Phase2 Dayun rule.

TJ-014.1 audit summary (see docs/product/TJ0141_DAYUN_DIRECTION_MATRIX.md):
the four-quadrant direction table is a *modern restoration candidate*
(support class B). Its only provenance is a modern open-source implementation;
no classical Source -> Section -> Rule -> Evidence chain approves it. The
fixed classical collation (bazi.dayun.fixed-source-collation-v1) verifies
adjacent fragments (month-pillar origin, nominal ten-year period, three-day
year ratio text, no-universal-fortune limit, and the historical role-category
terminology pairing) but explicitly does NOT adjudicate the direction rule.
"""
from .foundations import STEMS, ganzhi_index

VARIANT = "bazi-dayun-year-stem-traditional-role-research-v1"
YANG_STEMS = frozenset("甲丙戊庚壬")
YIN_STEMS = frozenset("乙丁己辛癸")
ROLES = ("male", "female")

COLLATION_ID = "bazi.dayun.fixed-source-collation-v1"
COLLATION_VARIANT = "bazi-dayun-source-collation-v1"
MODERN_CANDIDATE_VARIANT = "bazi-dayun-modern-restoration-candidate-v1"
SUPPORT_CLASS_MODERN = "B_modern_restoration_candidate"
DIRECTION_COLLATION_STATUS = "not_collated"

# Disputes / gaps that remain unadjudicated after the TJ-014.1 audit. These
# are recorded facts about the evidence state, not rule content.
UNRESOLVED_DISPUTES = (
    "sanming_tonghui_full_text_quarantine_no_canonical_dayun_section",
    "lun_qi_dayun_fa_only_grade_d_external_transcription_not_collated",
    "direction_wording_conflict_unresolved",
    "start_age_ratio_precision_unresolved",
    "role_terminology_fragment_does_not_independently_prove_direction",
)


def _evidence_assessment():
    """Truthful evidence state for the direction candidate.

    Every identifier below names a real, existing audit artefact. The four
    collated claims and the terminology appendix are imported from the
    source-audit module so this block cannot drift from the frozen
    collation; none of them proves the direction rule itself.
    """
    from .bazi_dayun_source_audit import EXPECTED_CLAIMS, REVIEW_STATUS
    from .bazi_dayun_source_audit import ROLE_APPENDIX_ID
    return {
        "support_class": SUPPORT_CLASS_MODERN,
        "direction_rule_classical_collation": DIRECTION_COLLATION_STATUS,
        "collation_id": COLLATION_ID,
        "collation_review_status": REVIEW_STATUS,
        "related_collated_claim_ids": sorted(EXPECTED_CLAIMS),
        "related_claims_prove_direction": False,
        "role_terminology_appendix_id": ROLE_APPENDIX_ID,
        "role_terminology_status": "historical_terminology_only_not_direction_proof",
        "unresolved_disputes": list(UNRESOLVED_DISPUTES),
        "promotion_blocked_reasons": [
            "no_classical_direction_claim_collated",
            "no_phase1_or_phase2_dayun_direction_rule_exists",
            "no_independent_second_source_adjudicated",
        ],
    }


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
        "evidence_assessment": _evidence_assessment(),
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "scope": "历史年干阴阳与传统角色分类的四种方向候选；角色只能由用户主动选择，非现实身份认定或经审定的唯一规则。"
    }


def school_matrix():
    """Per-source audit matrix for Dayun direction (TJ-014.1).

    One record per real source artefact. Class A records are fragments
    actually collated against the fixed classical base text; none of them
    proves the direction rule. The four-quadrant table is a single class B
    modern restoration candidate. Grade D / quarantine materials are kept
    as separate records and can never adjudicate. No record is
    Phase2-allowed.
    """
    from .bazi_dayun_source_audit import EXPECTED_CLAIMS, REVIEW_STATUS
    from .bazi_dayun_source_audit import ROLE_APPENDIX_ID

    claim_supports = {
        "bazi.dayun.source.month-pillar-origin": "month_pillar_is_sequence_origin",
        "bazi.dayun.source.nominal-ten-year": "nominal_ten_year_period_text_exists",
        "bazi.dayun.source.three-day-year": "three_day_year_ratio_text_exists",
        "bazi.dayun.source.no-universal-fortune": "mechanical_fortune_reading_limited",
    }
    records = []
    for claim_id in sorted(EXPECTED_CLAIMS):
        section_id, section_title = EXPECTED_CLAIMS[claim_id]
        records.append({
            "record_id": "collated-" + claim_id.rsplit(".", 1)[-1],
            "source_id": "bazi.source.yuanhai",
            "section_id": section_id,
            "section_title": section_title,
            "variant": COLLATION_VARIANT,
            "support_class": "A_classical_collated_fragment",
            "claim_id": claim_id,
            "collation_id": COLLATION_ID,
            "collation_review_status": REVIEW_STATUS,
            "supports": claim_supports[claim_id],
            "direction_support": "none",
            "year_stem_condition": None,
            "traditional_role_condition": None,
            "direction_candidate": None,
            "unreviewed_prerequisites": ["direction_rule_wording_not_in_this_fragment"],
            "conflicts": [],
            "review_conclusion": "collated_fragment_only_not_a_direction_rule",
            "phase2_allowed": False,
        })
    records.append({
        "record_id": "collated-role-terminology-appendix",
        "source_id": "bazi.source.yuanhai",
        "section_id": 188,
        "section_title": "珞琭子消息赋",
        "variant": COLLATION_VARIANT,
        "support_class": "A_classical_collated_fragment",
        "claim_id": "bazi.dayun.source.traditional-role-categories",
        "collation_id": COLLATION_ID,
        "collation_review_status": "historical_terminology_only",
        "supports": "historical_role_category_terminology_pairing_exists",
        "direction_support": "terminology_only_not_direction_proof",
        "year_stem_condition": None,
        "traditional_role_condition": "paired_historical_category_terms_present_in_fragment",
        "direction_candidate": None,
        "unreviewed_prerequisites": ["direction_inference_from_terminology_not_collated"],
        "conflicts": [],
        "review_conclusion": "terminology_fragment_verified_direction_not_proven",
        "phase2_allowed": False,
        "appendix_id": ROLE_APPENDIX_ID,
    })
    records.append({
        "record_id": "modern-four-quadrant-candidate",
        "source_id": None,
        "section_id": None,
        "section_title": None,
        "variant": MODERN_CANDIDATE_VARIANT,
        "support_class": SUPPORT_CLASS_MODERN,
        "claim_id": None,
        "collation_id": None,
        "collation_review_status": None,
        "supports": "modern_implementation_four_quadrant_table",
        "direction_support": "candidate_only_not_classically_collated",
        "year_stem_condition": "yang_stems=甲丙戊庚壬; yin_stems=乙丁己辛癸",
        "traditional_role_condition": "explicit_user_selected_male_or_female_only",
        "direction_candidate": {
            "yang_male": "forward", "yang_female": "backward",
            "yin_male": "backward", "yin_female": "forward",
        },
        "unreviewed_prerequisites": [
            "classical_direction_wording_not_collated",
            "no_independent_second_source",
            "start_age_and_handover_rules_not_adjudicated",
        ],
        "conflicts": list(UNRESOLVED_DISPUTES),
        "review_conclusion": "modern_restoration_candidate_unreviewed",
        "phase2_allowed": False,
        "provenance": "jinchenma94/bazi-skill/references/dayun-rules.md",
    })
    records.append({
        "record_id": "external-witness-lun-qi-dayun-fa",
        "source_id": None,
        "section_id": None,
        "section_title": "论起大运法（外部网页转录登记）",
        "variant": "bazi-dayun-external-witness-v1",
        "support_class": "D_external_transcription_located_only",
        "claim_id": None,
        "collation_id": None,
        "collation_review_status": "transcription_located_not_collated",
        "supports": "external_witness_registration_only",
        "direction_support": "none",
        "year_stem_condition": None,
        "traditional_role_condition": None,
        "direction_candidate": None,
        "unreviewed_prerequisites": [
            "original_image_not_compared",
            "independent_print_witness_not_verified",
            "not_part_of_fixed_base_text",
        ],
        "conflicts": ["direction_wording_conflict_unresolved"],
        "review_conclusion": "grade_d_witness_cannot_adjudicate",
        "phase2_allowed": False,
    })
    records.append({
        "record_id": "sanming-tonghui-quarantine",
        "source_id": "bazi.source.sanming-xianchi-niutrans",
        "section_id": None,
        "section_title": None,
        "variant": "bazi-dayun-sanming-quarantine-v1",
        "support_class": "C_unreviewed_quarantine",
        "claim_id": None,
        "collation_id": None,
        "collation_review_status": "quarantine_partial_collation",
        "supports": "none_for_dayun_direction",
        "direction_support": "none",
        "year_stem_condition": None,
        "traditional_role_condition": None,
        "direction_candidate": None,
        "unreviewed_prerequisites": [
            "full_text_quarantine",
            "no_canonical_dayun_section",
            "pua_collation_incomplete",
        ],
        "conflicts": [],
        "review_conclusion": "quarantine_material_cannot_adjudicate_direction",
        "phase2_allowed": False,
    })
    return records


def validate_direction_candidate(result):
    """Fail-closed consistency gate for a direction candidate result.

    Recomputes the candidate from its own declared inputs and rejects any
    result that claims a promotion the evidence does not support: an
    approved classical evidence flag, a matched direction rule, a Phase1
    rule id, an upgraded support class, public/AI enablement, or a
    direction/polarity that disagrees with the four-quadrant candidate.
    Returns True only for an internally consistent, unpromoted research
    candidate.
    """
    def fail(message):
        raise ValueError("Dayun direction candidate rejected: " + message)

    if not isinstance(result, dict):
        fail("result is not an object")
    if result.get("variant") != VARIANT:
        fail("unknown or missing variant")
    expected = traditional_direction(
        result.get("year_ganzhi"), traditional_role=result.get("traditional_role"))
    for field in ("year_stem", "year_stem_polarity", "direction",
                  "traditional_role_selection", "direction_origin",
                  "rule_review_status"):
        if result.get(field) != expected[field]:
            fail("field %s disagrees with recomputed candidate" % field)
    if result.get("research_only") is not True:
        fail("research_only must remain true")
    if result.get("public_enabled") is not False:
        fail("public_enabled must remain false")
    if result.get("ai_enabled") is not False:
        fail("ai_enabled must remain false")
    if result.get("classical_direction_evidence_approved") is not False:
        fail("forged classical evidence approval: no direction rule is approved")
    if result.get("direction_rule_match") is not None:
        fail("forged direction rule match: no Phase2 dayun direction rule exists")
    if result.get("natal_year_stem_rule_id") is not None:
        fail("forged rule id: no Phase1 dayun direction rule exists")
    reference = result.get("source_reference") or {}
    if reference.get("level") != "modern_implementation_not_classical_evidence":
        fail("source reference upgraded beyond modern implementation")
    assessment = result.get("evidence_assessment")
    if not isinstance(assessment, dict):
        fail("missing evidence assessment")
    if assessment.get("support_class") != SUPPORT_CLASS_MODERN:
        fail("support class upgraded beyond modern restoration candidate")
    if assessment.get("direction_rule_classical_collation") != DIRECTION_COLLATION_STATUS:
        fail("direction collation status forged")
    if assessment.get("related_claims_prove_direction") is not False:
        fail("collated fragments must not be presented as direction proof")
    expected_claims = _evidence_assessment()["related_collated_claim_ids"]
    if assessment.get("related_collated_claim_ids") != expected_claims:
        fail("related collated claim set drifted from the frozen collation")
    return True
