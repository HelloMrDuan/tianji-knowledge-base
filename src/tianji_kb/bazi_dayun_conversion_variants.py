"""Dayun conversion variants: evidence-bound, independently registered methods.

WBS TJ-016.1: each conversion method is an independent Variant with a
classical short quote, applicable scope, and rounding rules.

EVIDENCE STATUS (honest, verified 2026-10-22 against the sealed canon):
- The sealed 渊海子平 (daizhigev20, pinned bytes; data/canonical/classics/
  bazi/yuanhai_ziping_v1.json) contains exactly ONE conversion-rule text:
  「折除乃三日为年」 (§188 珞琭子消息赋）. Its audited scope explicitly does
  NOT specify remainder rounding, jie selection, or modern handover
  algorithms. No 余日 / 余时 / 起运 conversion algorithm exists anywhere in
  the sealed canon (the 余时 in 滴天髓阐微 §16 is 时支藏干余气, unrelated).
- Remainder handling is therefore UNRESOLVED. It is never defaulted, rounded,
  or invented. A modern mathematical derivation is never disguised as
  classical text.
- External transcriptions (e.g. 「俱折除三日爲一歲」, evidence_level D,
  transcription_located) are witnesses only, not verified originals; they do
  not create additional classical variants.

VARIANTS:
1. classical-three-day-symbolic-ratio-v1 -- exact Fraction(elapsed, 3 days),
   symbolic only, no start age. Evidence-backed (research_candidate).
2. modern-mean-year-simulation-v1 -- explicitly MODERN (365.2425 d) method,
   referencing the existing simulation; classical_basis=False. It exists so
   the modern method is never confused with a classical rule.

Boundaries: research_only=True, public_enabled=False, ai_enabled=False.
No formal 起运 age, no handover dates, no Phase2 promotion, no frozen
algorithm changes. This module never modifies the Phase4-frozen calendar.py.
"""
from fractions import Fraction

from .bazi_dayun_age_fraction import THREE_DAYS as THREE_DAYS_SECONDS
from .bazi_dayun_age_fraction import exact_three_day_ratio

# Pinned evidence descriptor for the single classical conversion rule.
# Byte-level truth is established by validate_source_collation on the real
# bundle; this descriptor pins WHAT the variant claims (claim, excerpt,
# section, SHAs, offset) so mismatches fail closed.
_PINNED_EVIDENCE = {
    "bazi.dayun.source.three-day-year": {
        "claim_id": "bazi.dayun.source.three-day-year",
        "source_id": "yuanhai_ziping_v1",
        "canonical_path": "data/canonical/classics/bazi/yuanhai_ziping_v1.json",
        "raw_path": "data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt",
        "canonical_section_id": 188,
        "canonical_section_title": "珞琭子消息赋",
        "exact_excerpt": "折除乃三日为年",
        "raw_char_offset": 55863,
        "raw_sha256": "c8f45d3228fb1958012139139a83edd019e7c2db881998d2d0bba65107417cf9",
        "canonical_sha256": "b64d8cde6a0a166332381d31b9885ad7421177b3ef071ecc65900d922524a13a",
        "scope": "证明折除与三日一年的文本存在；不规定余时舍入、前后节的选取或现代交运时间算法。",
        "supports": "以节令实测秒数除三日的符号比值",
        "does_not_support": [
            "余日/余时的舍入、截断或进位规则",
            "前后节的选取规则",
            "现代交运时间的计算方法",
            "正式起运岁数或交运日期",
        ],
        "applicable_scope": "节令差值符号比值的精确数学表达；不作年龄裁定",
        "conflicts": "外部转录本「俱折除三日爲一歲」(evidence_level D, 未见原版影印) 措辞不同，未确证；不另立变体",
    },
}

_VARIANT_REGISTRY = (
    {
        "variant_id": "classical-three-day-symbolic-ratio-v1",
        "method_name": "三日为年符号比值（折除）",
        "source_refs": ["yuanhai_ziping_v1"],
        "evidence_refs": ["bazi.dayun.source.three-day-year"],
        "review_status": "research_candidate",
        "input_unit": "elapsed_seconds: pinned-provider jie distance (whole seconds)",
        "remainder_policy": "unresolved",
        "rounding_policy": "unresolved",
        "calendar_basis": "jie-measured seconds only; no year length adjudicated",
        "applicable_scope": "精确符号比值；不裁定起运年龄、不生成交运日期",
        "unresolved_dependencies": [
            "余日取整规则：无原典",
            "余时取整规则：无原典",
            "前后节选取规则：无原典",
            "现代交运时间算法：无原典",
        ],
        "public_enabled": False,
        "ai_enabled": False,
    },
    {
        "variant_id": "modern-mean-year-simulation-v1",
        "method_name": "现代平均公历年折算（非古法，显式标记）",
        "source_refs": [],
        "evidence_refs": [],
        "review_status": "modern_research_only_not_classical",
        "input_unit": "elapsed_seconds: pinned-provider jie distance (whole seconds)",
        "remainder_policy": "modern_interpolation_not_classical",
        "rounding_policy": "modern_interpolation_not_classical",
        "calendar_basis": "gregorian mean year 365.2425 days (modern model)",
        "applicable_scope": "数学模拟对照；不得作为古法依据",
        "unresolved_dependencies": ["古法依据：无；本方法不声称古籍来源"],
        "public_enabled": False,
        "ai_enabled": False,
    },
)

_VARIANTS_BY_ID = {v["variant_id"]: v for v in _VARIANT_REGISTRY}


def list_variants():
    """Return the registered conversion variants (metadata only)."""
    return [dict(v, source_refs=list(v["source_refs"]),
                 evidence_refs=list(v["evidence_refs"]),
                 unresolved_dependencies=list(v["unresolved_dependencies"]))
            for v in _VARIANT_REGISTRY]


def get_variant(variant_id):
    """Fetch one variant; fail closed on unknown IDs (no fuzzy matching)."""
    try:
        variant = _VARIANTS_BY_ID[variant_id]
    except KeyError:
        raise ValueError(
            "unknown conversion variant %r; explicit variant selection "
            "is required, no default is applied" % (variant_id,))
    return dict(variant, source_refs=list(variant["source_refs"]),
                evidence_refs=list(variant["evidence_refs"]),
                unresolved_dependencies=list(variant["unresolved_dependencies"]))


def check_variant_evidence_match(variant_id, claim):
    """Verify a single evidence claim is the variant's pinned evidence.

    Checks claim_id membership plus exact excerpt/section binding. Byte-level
    integrity of the containing bundle is established separately by
    validate_source_collation; this proves the RIGHT evidence is attached to
    the RIGHT variant (mismatches fail closed).
    """
    variant = get_variant(variant_id)
    if not isinstance(claim, dict):
        raise ValueError("evidence claim must be a mapping")
    claim_id = claim.get("claim_id")
    if claim_id not in variant["evidence_refs"]:
        raise ValueError(
            "claim %r is not evidence for variant %r; variant-evidence "
            "mismatch is rejected" % (claim_id, variant_id))
    pinned = _PINNED_EVIDENCE[claim_id]
    for field in ("exact_excerpt", "canonical_section_id",
                  "canonical_section_title"):
        if claim.get(field) != pinned[field]:
            raise ValueError(
                "evidence %r field %r does not match the pinned descriptor "
                "for variant %r" % (claim_id, field, variant_id))
    return True


def bind_variant_evidence(variant_id, *, collation, raw_bytes, canonical_bytes,
                          require_pinned_shas=True):
    """Bind a variant to real, byte-validated evidence.

    Runs the full fixed-source collation validation (real SHA256 digests,
    exact excerpt offsets, section locators), then proves each of the
    variant's evidence_refs resolves to its pinned claim. Forged source_id,
    section_id, excerpts, or file bytes fail closed. Nothing here promotes a
    research candidate: review_status is carried through unchanged.
    """
    from .bazi_dayun_source_audit import validate_source_collation
    variant = get_variant(variant_id)
    validated = validate_source_collation(collation, raw_bytes, canonical_bytes)
    if require_pinned_shas:
        for claim_id in variant["evidence_refs"]:
            pinned = _PINNED_EVIDENCE[claim_id]
            if (validated["source_sha256"] != pinned["raw_sha256"]
                    or validated["canonical_sha256"] != pinned["canonical_sha256"]):
                raise ValueError(
                    "evidence bundle SHAs do not match the pinned descriptors "
                    "for variant %r" % (variant_id,))
    bound = []
    claims_by_id = {c.get("claim_id"): c for c in collation["claims"]}
    for claim_id in variant["evidence_refs"]:
        claim = claims_by_id.get(claim_id)
        if claim is None:
            raise ValueError(
                "variant %r requires evidence %r, absent from the validated "
                "bundle" % (variant_id, claim_id))
        check_variant_evidence_match(variant_id, claim)
        pinned = _PINNED_EVIDENCE[claim_id]
        bound.append({
            "claim_id": claim_id,
            "source_id": pinned["source_id"],
            "canonical_section_id": claim["canonical_section_id"],
            "canonical_section_title": claim["canonical_section_title"],
            "exact_excerpt": claim["exact_excerpt"],
            "raw_char_offset": claim["raw_char_offset"],
            "scope": pinned["scope"],
            "supports": pinned["supports"],
            "does_not_support": list(pinned["does_not_support"]),
        })
    return {
        "variant_id": variant_id,
        "review_status": variant["review_status"],
        "evidence_bound": bound,
        "collation_verified_claims": validated["verified_claim_count"],
        "canonical_method_adjudicated": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }


def _base_result(variant_id, measured):
    return {
        "variant_id": variant_id,
        "measured_variant": measured.get("variant"),
        "direction": measured.get("direction"),
        "elapsed_seconds": measured.get("elapsed_seconds"),
        "three_days_seconds": THREE_DAYS_SECONDS,
        "start_age": None,
        "handover_datetime": None,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }


def convert_with_variant(variant_id, measured_jie, *, rounding=None):
    """Convert a validated jie measurement with an explicit variant.

    No default variant is ever applied. A requested rounding policy with no
    classical basis returns unresolved (never a silently rounded age).
    Outputs never contain a formal start age or handover date.
    """
    variant = get_variant(variant_id)
    if rounding is not None:
        return {
            "variant_id": variant_id,
            "status": "unresolved",
            "reason": "no classical rounding rule in the sealed evidence; "
                      "rounding %r is refused" % (rounding,),
            "variant_rounding_policy": variant["rounding_policy"],
            "start_age": None,
            "handover_datetime": None,
            "research_only": True,
            "public_enabled": False,
            "ai_enabled": False,
        }
    # Reuses the exact, replay-gated arithmetic; never rebuilt here.
    ratio = exact_three_day_ratio(measured_jie)
    elapsed = ratio["elapsed_seconds"]
    if variant_id == "classical-three-day-symbolic-ratio-v1":
        result = _base_result(variant_id, ratio)
        if elapsed == 0:
            result.update({
                "candidate_kind": "symbolic_ratio",
                "symbolic_years": None,
                "whole_three_day_units": 0,
                "remainder_seconds": 0,
                "remainder_resolution": {
                    "status": "unresolved",
                    "reason": "zero jie distance convention is unreviewed",
                },
                "classical_text": "折除乃三日为年",
                "classical_basis": True,
            })
        else:
            fraction = Fraction(elapsed, THREE_DAYS_SECONDS)
            remainder = elapsed % THREE_DAYS_SECONDS
            result.update({
                "candidate_kind": "symbolic_ratio",
                "symbolic_years": {"numerator": fraction.numerator,
                                   "denominator": fraction.denominator},
                "whole_three_day_units": elapsed // THREE_DAYS_SECONDS,
                "remainder_seconds": remainder,
                "remainder_resolution": (
                    {"status": "no_remainder"}
                    if remainder == 0 else
                    {"status": "unresolved",
                     "reason": "the sealed text gives no remainder rule; "
                               "余日/余时 conversion is not adjudicated",
                     "missing_evidence": list(
                         variant["unresolved_dependencies"]),
                     "cannot_proceed_because": (
                         "no verified source specifies rounding, truncation, "
                         "or carry for sub-three-day remainders")}),
                "classical_text": "折除乃三日为年",
                "classical_basis": True,
                "evidence_claim_ids": list(variant["evidence_refs"]),
            })
        return result
    if variant_id == "modern-mean-year-simulation-v1":
        result = _base_result(variant_id, ratio)
        if elapsed == 0:
            modern_years = None
        else:
            modern_years = Fraction(elapsed, THREE_DAYS_SECONDS)
        result.update({
            "candidate_kind": "modern_mean_year_interpretation",
            "classical_basis": False,
            "modern_model": "gregorian_mean_year_365.2425_days",
            "modern_years": ({"numerator": modern_years.numerator,
                              "denominator": modern_years.denominator}
                             if modern_years is not None else None),
            "note": "modern interpolation for comparison only; not a "
                    "classical rule and not a formal start age",
        })
        return result
    raise ValueError("variant %r has no executable conversion" % (variant_id,))


def research_convert(*, variant_id, measured_jie, evidence_bundle=None,
                     rounding=None):
    """Research entry: convert with an explicitly selected variant.

    - variant_id is mandatory; no default school is ever applied.
    - evidence_bundle (optional) is truly validated via bind_variant_evidence.
    - Conflicting variants are never merged: each call returns one variant's
      result, clearly labeled.
    - Research candidates are never published to ordinary user interfaces.
    """
    if not isinstance(variant_id, str) or not variant_id:
        raise ValueError(
            "explicit variant_id is required; no default conversion method "
            "is applied")
    bound_evidence = None
    if evidence_bundle is not None:
        if not isinstance(evidence_bundle, dict):
            raise ValueError("evidence_bundle must be a mapping")
        bound_evidence = bind_variant_evidence(
            variant_id,
            collation=evidence_bundle["collation"],
            raw_bytes=evidence_bundle["raw_bytes"],
            canonical_bytes=evidence_bundle["canonical_bytes"])
    result = convert_with_variant(variant_id, measured_jie, rounding=rounding)
    result["evidence_binding"] = bound_evidence
    result["entry"] = "research_convert"
    return result


def release_variant(variant_id):
    """Boundary guard: research variants can never be promoted/released."""
    get_variant(variant_id)  # validates the ID, then refuses regardless
    raise ValueError(
        "variant %r is research_only and cannot be promoted to an "
        "adjudicated rule, Phase2, or public release" % (variant_id,))
