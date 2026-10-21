"""Real research-entry consumer for the calendar precision audit (TJ-015.2).

This module is the executable entry point -- not just tests -- that wires
real birth instants and jie terms through the audit pipeline:

- ``research_audit_birth()`` takes a real birth value + tz name, runs
  ``audit_birth_instant()`` (fail-closed on nonexistent / ambiguous /
  historically-misoffset times), and returns a research-scoped report.
- ``research_audit_jie()`` takes a real term + year + provider moment and
  audits it against the frozen reference set (the caller cannot substitute
  a reference).
- ``research_audit_summary()`` summarizes verified audit records.

Research boundaries (hard):
- ``research_only`` stays True; precision flags stay False.
- This module has NO API for deriving 起运岁数 / 交运日期 / 大运时间轴.
  Any such request is a misuse of this entry point.
- The Phase4-frozen ``calendar.py`` is not imported or modified here.
"""
from .bazi_calendar_precision_audit import (
    INDEPENDENT_JIE_REFERENCES_V2,
    REFERENCE_SET_VERSION,
    audit_birth_instant,
    audit_jie_against_reference,
    get_frozen_reference,
    summarize_audits,
)

# Explicitly forbidden conclusion kinds for this entry point. Used by tests
# to assert the module never grows a dayun-conclusion API by accident.
FORBIDDEN_CONCLUSION_KINDS = (
    "qiyun_age", "jiaoyun_date", "dayun_timeline",
    "起运岁数", "交运日期", "大运时间轴",
)


def research_audit_birth(*, birth_value, tz_name="Asia/Shanghai"):
    """Audit a real birth instant for research use; fail-closed on incoherence.

    ``birth_value``: tz-aware datetime or ISO string with numeric offset.
    Raises ValueError on naive input, nonexistent civil time, historical
    offset misuse, or ambiguous named-zone time (see audit_birth_instant).
    """
    birth = audit_birth_instant(birth_value, tz_name=tz_name)
    return {
        "kind": "birth_instant_research_audit",
        "birth": birth,
        "precision_certification": {
            "astronomical_precision_independently_verified": False,
            "historical_timezone_independently_verified": False,
            "note": ("tzdb classification is verified; the civil time actually "
                     "written on any particular birth record is NOT verified "
                     "from tzdb alone"),
        },
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
    }


def research_audit_jie(*, term, gregorian_year, provider_moment_utc):
    """Audit one jie term against the frozen reference set (no substitution)."""
    reference = get_frozen_reference(term, gregorian_year)
    return audit_jie_against_reference(
        term=term, gregorian_year=gregorian_year,
        provider_moment_utc=provider_moment_utc, reference=reference)


def research_audit_summary(records):
    """Summarize verified jie audit records (re-verified, never trusted)."""
    return summarize_audits(records)


def reference_catalog():
    """List the frozen reference set (for inspection, not trust)."""
    return {
        "reference_set_version": REFERENCE_SET_VERSION,
        "record_count": len(INDEPENDENT_JIE_REFERENCES_V2),
        "records": [
            {"record_id": r["record_id"], "term": r["term"],
             "gregorian_year": r["gregorian_year"],
             "source_org": r["source_org"], "source_url": r["source_url"],
             "citation_class": r["citation_class"],
             "primary_verified": r["primary_verified"]}
            for r in INDEPENDENT_JIE_REFERENCES_V2
        ],
    }
