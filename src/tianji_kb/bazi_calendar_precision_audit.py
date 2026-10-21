"""Independent research audit for calendar precision claims (TJ-015.2).

Compares the pinned provider's Jie moments against independently published
references AT THE SOURCE'S PRECISION, and fail-closed classifies civil birth
times against the real tzdb. This module never modifies the Phase4-frozen
``calendar.py`` and never upgrades any global precision flag.

Honesty rules enforced here:
- A minute-precision source supports only minute-level comparison.
  Truncated-to-minute equality -> "minute_agreement".
  Exactly-one-minute nominal difference -> "unresolved_minute_ambiguity"
  (true difference lies somewhere in [1s, 119s]; neither agreement nor
  disagreement can be decided).
  Two or more minutes -> "exceeds_minute_tolerance" (genuine disagreement).
- A passing audit covers ONLY its listed (year, terms, source). It is never
  extrapolated to 1901..2098.
- Ambiguous or nonexistent civil times are rejected, never silently guessed.
"""
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

UTC = timezone.utc

# Independent reference records, frozen with provenance (TJ-015.2).
# Source B: Wikipedia solar-term pages, each citing
# "NASA JPL Horizons online ephemeris system" (second-hand citation;
# time scale / reference frame / root-finding method NOT verified).
# Precision: minute. Timezone: UTC, as stated on each page.
# lunar-python 1.4.8 moments were measured locally on 2026-10-21 and are
# re-computed live by the tests; they are NOT trusted from this table.
INDEPENDENT_JIE_REFERENCES_V1 = [
    {"term": "立春", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立春",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-02-04T08:27:00+00:00"},
    {"term": "惊蛰", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/惊蛰",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-03-05T02:23:00+00:00"},
    {"term": "清明", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/清明",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-04-04T07:02:00+00:00"},
    {"term": "立夏", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立夏",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-05-05T00:10:00+00:00"},
    {"term": "芒种", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/芒种",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-06-05T04:10:00+00:00"},
    {"term": "小暑", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/小暑",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-07-06T14:20:00+00:00"},
    {"term": "立秋", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立秋",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-08-07T00:09:00+00:00"},
    {"term": "白露", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/白露",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-09-07T03:11:00+00:00"},
    {"term": "寒露", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/寒露",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-10-07T19:00:00+00:00"},
    {"term": "立冬", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立冬",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-11-06T22:20:00+00:00"},
    {"term": "大雪", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/大雪",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2024-12-06T15:17:00+00:00"},
    {"term": "小寒", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/小寒",
     "source_precision": "minute", "source_timezone": "UTC",
     "published_utc": "2025-01-05T02:33:00+00:00"},
]

SUPPORTED_PRECISIONS = ("minute",)

# Version tag for the frozen reference set below (collection date + task).
REFERENCE_SET_VERSION = "tj0152-v1 collected 2026-10-21"


def _require_aware(value, name):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("%s must be a timezone-aware datetime" % name)
    if value.microsecond != 0:
        raise ValueError("%s must be at whole-second precision" % name)
    return value


def audit_jie_against_reference(*, term, gregorian_year, provider_moment_utc,
                                 reference):
    """Audit one provider Jie moment against one independent reference record.

    Comparison happens at the SOURCE's precision only. Returns a full audit
    record; raises ValueError on missing/incoherent inputs (fail-closed).
    """
    if type(term) is not str or not term:
        raise ValueError("term must be a non-empty string")
    if type(gregorian_year) is not int:
        raise ValueError("gregorian_year must be an int")
    provider_moment_utc = _require_aware(provider_moment_utc, "provider_moment_utc")
    if type(reference) is not dict:
        raise ValueError("reference must be a dict record")
    for key in ("source_org", "source_url", "source_precision",
                "source_timezone", "published_utc"):
        if not reference.get(key):
            raise ValueError("reference is missing required field: %s" % key)
    precision = reference["source_precision"]
    if precision not in SUPPORTED_PRECISIONS:
        raise ValueError(
            "reference precision %r is not supported for comparison" % (precision,))
    try:
        published = datetime.fromisoformat(reference["published_utc"])
    except ValueError as exc:
        raise ValueError("reference published_utc is not a valid ISO datetime") from exc
    published = _require_aware(published, "reference published_utc")
    if reference["term"] != term:
        raise ValueError("reference term does not match the audited term")

    provider_utc = provider_moment_utc.astimezone(UTC)
    published_utc = published.astimezone(UTC)
    # Minute-level comparison only: truncate the provider's seconds.
    provider_minute = provider_utc.replace(second=0)
    published_minute = published_utc.replace(second=0, microsecond=0)
    minute_difference = int((provider_minute - published_minute).total_seconds() // 60)
    second_difference = int((provider_utc - published_utc).total_seconds())

    if minute_difference == 0:
        verdict = "minute_agreement"
        unresolved = []
    elif abs(minute_difference) == 1:
        verdict = "unresolved_minute_ambiguity"
        unresolved = [
            "nominal one-minute difference; true difference lies in [1s, 119s]; "
            "agreement and disagreement are both undecidable at source precision",
        ]
    else:
        verdict = "exceeds_minute_tolerance"
        unresolved = []

    return {
        "term": term,
        "gregorian_year": gregorian_year,
        "source_org": reference["source_org"],
        "source_url": reference["source_url"],
        "source_precision": precision,
        "source_timezone": reference["source_timezone"],
        "published_utc": published_utc.isoformat(),
        "provider_utc": provider_utc.isoformat(),
        "minute_difference": minute_difference,
        "second_difference": second_difference,
        "tolerance_basis": ("minute-precision source: truncated-to-minute equality; "
                            "1-minute nominal difference is undecidable"),
        "verdict": verdict,
        "unresolved_items": unresolved,
        "astronomical_precision_independently_verified": False,
        "scope": "single (term, year, source) comparison only; not extrapolated",
    }


def summarize_audits(results):
    """Summarize audit records without upgrading any global precision flag."""
    if type(results) is not list or not results:
        raise ValueError("results must be a non-empty list")
    verdicts = {}
    for record in results:
        verdicts[record["verdict"]] = verdicts.get(record["verdict"], 0) + 1
    covered_terms = sorted({r["term"] for r in results})
    covered_years = sorted({r["gregorian_year"] for r in results})
    covered_sources = sorted({r["source_org"] for r in results})
    return {
        "audit_count": len(results),
        "verdicts": verdicts,
        "coverage": {"terms": covered_terms, "gregorian_years": covered_years,
                     "sources": covered_sources},
        "coverage_disclaimer": ("covers only the listed (term, year, source) records; "
                                "must NOT be extrapolated to 1901..2098 or to "
                                "second-level precision"),
        "astronomical_precision_independently_verified": False,
        "historical_timezone_independently_verified": False,
        "research_only": True,
    }


def tzdata_version():
    """Best-effort tzdb version identifier for audit provenance."""
    try:
        from importlib.metadata import version as _v
        return "tzdata-package/" + _v("tzdata")
    except Exception:
        pass
    try:
        with open("/usr/share/zoneinfo/tzdata.zi", encoding="utf-8") as handle:
            first = handle.readline().strip()
            if first:
                return "system-tzdata/" + first[:80]
    except OSError:
        pass
    return "tzdata-version-unverified"


def classify_civil_time(naive_local, tz_name):
    """Classify a wall-clock time against the real tzdb (fail-closed helper).

    Returns "unique", "ambiguous" (fall-back overlap: two UTC instants), or
    "nonexistent" (spring-forward gap). Never guesses.
    """
    if ZoneInfo is None:
        raise ValueError("zoneinfo is unavailable; civil-time source unverifiable")
    if not isinstance(naive_local, datetime) or naive_local.tzinfo is not None:
        raise ValueError("naive_local must be a naive datetime")
    if naive_local.microsecond != 0:
        raise ValueError("naive_local must be at whole-second precision")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError("unknown timezone: %r" % (tz_name,)) from exc

    def round_trips(fold):
        candidate = naive_local.replace(tzinfo=tz, fold=fold)
        back = candidate.astimezone(UTC).astimezone(tz).replace(tzinfo=None)
        return back == naive_local

    ok0, ok1 = round_trips(0), round_trips(1)
    if ok0 and ok1:
        off0 = naive_local.replace(tzinfo=tz, fold=0).utcoffset()
        off1 = naive_local.replace(tzinfo=tz, fold=1).utcoffset()
        if off0 != off1:
            return "ambiguous"
        return "unique"
    if not ok0 and not ok1:
        return "nonexistent"
    return "unique"


def _valid_offsets_for(naive_local, tz):
    """tzdb-valid UTC offsets for a civil time (empty when nonexistent)."""
    valid = set()
    for fold in (0, 1):
        candidate = naive_local.replace(tzinfo=tz, fold=fold)
        if candidate.astimezone(UTC).astimezone(tz).replace(tzinfo=None) == naive_local:
            valid.add(candidate.utcoffset())
    return valid


def audit_birth_instant(value, *, tz_name="Asia/Shanghai"):
    """Validate a birth instant for research use; fail-closed on incoherence.

    Accepts a tz-aware datetime (or ISO string with numeric offset). The civil
    time AS WRITTEN and the claimed UTC offset must both cohere with the real
    tzdb for tz_name:
    - naive input -> rejected (no offset to trust);
    - nonexistent civil time (DST gap) -> rejected, never remapped;
    - claimed offset contradicting tzdb (historical offset misuse) -> rejected;
    - ambiguous civil time with a named-zone input -> rejected (fold would be
      a silent guess); with an explicit numeric offset -> accepted as the
      offset-selected instant, fully recorded (no guessing: the offset chose).
    """
    instant = datetime.fromisoformat(value) if isinstance(value, str) else value
    instant = _require_aware(instant, "birth instant")
    if ZoneInfo is None:
        raise ValueError("zoneinfo is unavailable; civil-time source unverifiable")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError("unknown timezone: %r" % (tz_name,)) from exc
    claimed_offset = instant.utcoffset()
    if claimed_offset == timedelta(0):
        # A UTC input is an unambiguous instant, not a civil claim in tz_name.
        naive_local = instant.astimezone(tz).replace(tzinfo=None)
        classification = classify_civil_time(naive_local, tz_name)
        return {
            "utc_instant": instant.astimezone(UTC).isoformat(),
            "civil_time": naive_local.isoformat(),
            "civil_classification": classification,
            "offset_disambiguation": "utc_instant",
            "resolved_fold": None,
            "tz_name": tz_name,
            "tzdb": tzdata_version(),
            "astronomical_precision_independently_verified": False,
            "historical_timezone_independently_verified": False,
            "research_only": True,
        }
    # Civil time AS WRITTEN by the claimant (not converted: conversion would
    # hide a historically wrong offset behind the modern one).
    naive_local = instant.replace(tzinfo=None)
    classification = classify_civil_time(naive_local, tz_name)
    valid_offsets = _valid_offsets_for(naive_local, tz)
    if classification == "nonexistent":
        raise ValueError(
            "birth civil time %s does not exist in %s (DST transition gap); "
            "refusing to guess a UTC instant" % (naive_local.isoformat(), tz_name))
    if claimed_offset not in valid_offsets:
        raise ValueError(
            "claimed UTC offset %s contradicts tzdb for civil time %s in %s; "
            "historical offset misuse is rejected" % (
                claimed_offset, naive_local.isoformat(), tz_name))
    named_zone_input = isinstance(instant.tzinfo, ZoneInfo) and (
        getattr(instant.tzinfo, "key", None) == tz_name)
    disambiguation = "not_needed"
    resolved_fold = None
    if classification == "ambiguous":
        if named_zone_input:
            raise ValueError(
                "birth civil time %s is ambiguous in %s (DST fall-back overlap); "
                "fold would be a silent guess" % (naive_local.isoformat(), tz_name))
        # Explicit numeric offset selects the fold; record the choice.
        fold0 = naive_local.replace(tzinfo=tz, fold=0)
        resolved_fold = 0 if fold0.utcoffset() == claimed_offset else 1
        disambiguation = "explicit_offset"
    resolved = naive_local.replace(tzinfo=tz, fold=resolved_fold or 0)
    return {
        "utc_instant": resolved.astimezone(UTC).isoformat(),
        "civil_time": naive_local.isoformat(),
        "civil_classification": classification,
        "offset_disambiguation": disambiguation,
        "resolved_fold": resolved_fold,
        "tz_name": tz_name,
        "tzdb": tzdata_version(),
        "astronomical_precision_independently_verified": False,
        "historical_timezone_independently_verified": False,
        "research_only": True,
    }
