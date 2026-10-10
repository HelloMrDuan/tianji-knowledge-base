"""Offline, fail-closed fixed-source audit for Bazi Dayun research excerpts.

NOT a Phase2 rule provider, not a public API, and not an evidence promotion.
The short excerpts must match BOTH the pinned raw source and reviewed classic.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = Path("data/research/bazi/dayun_source_collation_v1.json")
RAW_PATH = "data/quarantine/public_domain_snapshots/daizhigev20/yuanhai_ziping.txt"
CANONICAL_PATH = "data/canonical/classics/bazi/yuanhai_ziping_v1.json"
REVIEW_STATUS = "snapshot_collated_not_classical_method_adjudicated"
EXPECTED_CLAIMS = {
    "bazi.dayun.source.month-pillar-origin": (10, "论大运"),
    "bazi.dayun.source.nominal-ten-year": (188, "珞琭子消息赋"),
    "bazi.dayun.source.three-day-year": (188, "珞琭子消息赋"),
    "bazi.dayun.source.no-universal-fortune": (10, "论大运"),
}


def _check(condition, message):
    if not condition:
        raise ValueError("Dayun collation integrity error: " + message)


def validate_source_collation(audit, raw_bytes, canonical_bytes):
    """Validate exact UTF-8 bytes, unique short excerpts and section locators.

    Inputs are immutable bytes from caller, so negative mutation tests can prove
    fail-closed behavior without changing the repository files.
    """
    _check(isinstance(audit, dict), "invalid audit object")
    _check(audit.get("id") == "bazi.dayun.fixed-source-collation-v1",
           "unsupported source collation id")
    _check(audit.get("review_status") == REVIEW_STATUS,
           "unauthorized method promotion")
    meta = audit.get("baseline")
    _check(isinstance(meta, dict), "missing baseline")
    _check(meta.get("raw_path") == RAW_PATH and
           meta.get("canonical_path") == CANONICAL_PATH,
           "source path was redirected")
    _check(meta.get("repository") == "garychowcmu/daizhigev20" and
           meta.get("commit") == "4a6d6f2088825f132521d848c2ea86cf9c9a7620",
           "source provenance has changed")
    _check(meta.get("license_policy") == "PUBLIC_DOMAIN_EXTRACT_ONLY",
           "source rights policy has changed")
    _check(isinstance(raw_bytes, bytes) and isinstance(canonical_bytes, bytes),
           "source bytes required")
    _check(hashlib.sha256(raw_bytes).hexdigest() == meta.get("raw_sha256"),
           "raw snapshot digest drift")
    _check(hashlib.sha256(canonical_bytes).hexdigest() == meta.get("canonical_sha256"),
           "canonical snapshot digest drift")
    try:
        raw = raw_bytes.decode("utf-8")
        classic = json.loads(canonical_bytes)
    except (ValueError, UnicodeError) as error:
        raise ValueError("Dayun collation integrity error: invalid source encoding") from error
    _check(classic.get("provenance", {}).get("repo") == meta["repository"] and
           classic.get("provenance", {}).get("commit") == meta["commit"],
           "canonical provenance mismatch")
    _check(classic.get("provenance", {}).get("license_policy") ==
           meta["license_policy"], "canonical source rights mismatch")
    sections = {item["id"]: item for item in classic["sections"]}
    _check(isinstance(audit.get("claims"), list) and
           len(audit["claims"]) == len(EXPECTED_CLAIMS), "claim set drift")
    seen = set()
    for claim in audit["claims"]:
        _check(isinstance(claim, dict), "invalid claim")
        cid = claim.get("claim_id")
        _check(cid in EXPECTED_CLAIMS and cid not in seen,
               "unknown or duplicated claim")
        seen.add(cid)
        sec_id, title = EXPECTED_CLAIMS[cid]
        _check(claim.get("canonical_section_id") == sec_id and
               claim.get("canonical_section_title") == title,
               "section locator drift")
        section = sections.get(sec_id)
        _check(section is not None and section["title"] == title,
               "missing canonical section")
        quote = claim.get("exact_excerpt")
        offset = claim.get("raw_char_offset")
        _check(isinstance(quote, str) and 5 <= len(quote) <= 64 and
               type(offset) is int and offset >= 0, "invalid excerpt location")
        _check(raw[offset:offset + len(quote)] == quote,
               "source excerpt moved or altered")
        _check(raw.count(quote) == 1, "ambiguous raw excerpt match")
        _check(section["text"].count(quote) == 1,
               "excerpt not uniquely contained in canonical section")
        _check(isinstance(claim.get("scope"), str) and len(claim["scope"]) >= 12,
               "missing non-generalization guard")
    _check(seen == set(EXPECTED_CLAIMS), "missing source claims")
    rel = audit.get("changes_to_release", {})
    _check(rel.get("phase1_rule_promotions") == 0 and
           rel.get("phase2_rule_promotions") == 0 and
           rel.get("new_golden_promotions") == 0 and
           rel.get("public_enabled") is False and
           rel.get("ai_enabled") is False and
           rel.get("source_quotations_exposed_by_api") is False,
           "source audit cannot authorize release")
    return {
        "collation_id": audit["id"],
        "review_status": REVIEW_STATUS,
        "verified_claim_count": len(seen),
        "source_sha256": meta["raw_sha256"],
        "canonical_sha256": meta["canonical_sha256"],
        "canonical_method_adjudicated": False,
        "public_enabled": False,
        "ai_enabled": False,
    }


def verify_fixed_source_collation(root=ROOT):
    """For explicit offline build/CI validation; never called by public API."""
    base = Path(root)
    audit = json.loads((base / AUDIT_PATH).read_text(encoding="utf-8"))
    return validate_source_collation(
        audit, (base / RAW_PATH).read_bytes(),
        (base / CANONICAL_PATH).read_bytes(),
    )


# The private review appendix is an independent, opt-in file outside the
# immutable 235-file data snapshot. This validator only authenticates the
# spelling of a historical role category in the pre-pinned original source.
# Neither this appendix nor its digest is a reviewed Dayun direction rule.
ROLE_APPENDIX_ID = "bazi.dayun.traditional-role-terminology-appendix-v1"
ROLE_EXCERPT_SHA256 = "9ee55898732edf77f3921652823ba24ada85125ed0817e4ea6f4fe3f910fe8fd"


def validate_role_terminology_appendix(appendix, raw_bytes, canonical_bytes, source_audit):
    """Offline-only second collation; preserves the frozen four-claim snapshot."""
    validate_source_collation(source_audit, raw_bytes, canonical_bytes)
    _check(isinstance(appendix, dict)
           and appendix.get("id") == ROLE_APPENDIX_ID
           and appendix.get("source_collation_id") == source_audit["id"]
           and appendix.get("review_status") == "historical_terminology_only",
           "invalid research appendix identity")
    claim = appendix.get("claim")
    _check(isinstance(claim, dict)
           and claim.get("claim_id") == "bazi.dayun.source.traditional-role-categories"
           and claim.get("canonical_section_id") == 188
           and claim.get("canonical_section_title") == "珞琭子消息赋",
           "research appendix locator changed")
    quote = claim.get("exact_excerpt")
    offset = claim.get("raw_char_offset")
    _check(isinstance(quote, str) and 5 <= len(quote) <= 64
           and hashlib.sha256(quote.encode("utf-8")).hexdigest() == ROLE_EXCERPT_SHA256
           and type(offset) is int and offset >= 0,
           "research appendix quote digest or offset invalid")
    raw = raw_bytes.decode("utf-8")
    canonical = json.loads(canonical_bytes)
    section = next((s for s in canonical["sections"] if s["id"] == 188), None)
    _check(section is not None and section.get("title") == "珞琭子消息赋"
           and raw[offset:offset + len(quote)] == quote
           and raw.count(quote) == 1
           and section["text"].count(quote) == 1,
           "research appendix source fragment differs from pinned original")
    _check(isinstance(claim.get("scope"), str)
           and "不独立证明大运顺逆" in claim["scope"],
           "terminology does not authorize direction inference")
    release = appendix.get("changes_to_release")
    _check(isinstance(release, dict)
           and release.get("phase1_rule_promotions") == 0
           and release.get("phase2_rule_promotions") == 0
           and release.get("new_golden_promotions") == 0
           and release.get("public_enabled") is False
           and release.get("ai_enabled") is False
           and release.get("source_quotations_exposed_by_api") is False,
           "research appendix cannot authorize release")
    return {
        "appendix_id": ROLE_APPENDIX_ID,
        "fixed_original_fragment_verified": True,
        "canonical_method_adjudicated": False,
        "independent_edition_verified": False,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }
