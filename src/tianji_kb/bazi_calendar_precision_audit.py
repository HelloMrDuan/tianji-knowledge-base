"""Independent research audit for calendar precision claims (TJ-015.2, rev 2).

Compares the pinned provider's Jie moments against independently published
references AT THE SOURCE'S PRECISION, and fail-closed classifies civil birth
times against the real tzdb. This module never modifies the Phase4-frozen
``calendar.py`` and never upgrades any global precision flag.

Reference trust model (P0):
- The ONLY trusted references are the frozen records below
  (``INDEPENDENT_JIE_REFERENCES_V2``). ``verify_reference_record()`` binds any
  incoming record to the frozen set field-by-field; substitution, version
  mismatch or forgery fails closed.
- Trust is NOT self-declared by ``source_org``/``source_url`` text. Every
  record carries ``citation_class`` / ``primary_verified``: the JPL values are
  second-hand citations via Wikipedia (primary JPL computation NOT re-run),
  so results stay ``research_only`` and minute-level at most.
- HKO availability check (2026-10-21): the HKO annual 24-term timetable page
  (https://www.hko.gov.hk/en/gts/astronomy/Solar_Term.htm) requires a
  JS-driven year selector; its data table is not obtainable by text fetch.
  HKO's definitional table (sun's longitudes per term) WAS obtained and is
  consistent with the JPL-based definitions used here. Annual HKO times
  remain UNVERIFIED/unavailable; the Wikipedia-cited JPL set stays the
  second-hand reference. See ``HKO_DEFINITION_CROSSCHECK``.

Honesty rules enforced here:
- A minute-precision source supports only minute-level comparison.
- A passing audit covers ONLY its listed (term, year, source); never
  extrapolated to 1901..2098.
- Ambiguous or nonexistent civil times are rejected, never silently guessed.
- ``summarize_audits()`` re-verifies every record against the frozen set and
  recomputes every verdict; it never trusts an externally passed verdict.
"""
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

UTC = timezone.utc
REFERENCE_SET_VERSION = "tj0152-v2 collected 2026-10-21"
SUPPORTED_PRECISIONS = ("minute",)

# HKO definitional cross-check (obtained 2026-10-21 from
# https://www.hko.gov.hk/en/gts/time/24solarterms.htm, Table 1):
# the 12 minor solar terms (Jie) and the sun's ecliptic longitudes HKO assigns.
# Used ONLY to confirm the JPL-based reference definitions agree with HKO's
# official definitions. HKO annual TIMES were not obtainable (JS selector).
HKO_DEFINITION_CROSSCHECK = {
    "source": "https://www.hko.gov.hk/en/gts/time/24solarterms.htm",
    "obtained": "2026-10-21",
    "note": "definitions only; annual times unavailable via text fetch",
    "jie_longitudes": {
        "立春": 315, "惊蛰": 345, "清明": 15, "立夏": 45,
        "芒种": 75, "小暑": 105, "立秋": 135, "白露": 165,
        "寒露": 195, "立冬": 225, "大雪": 255, "小寒": 285,
    },
}

# Frozen independent reference records. JPL values are second-hand citations
# via Wikipedia (each page states "數據來源：噴氣推進實驗室線上曆書系統",
# minute precision, UTC); the primary JPL computation was NOT re-run.
INDEPENDENT_JIE_REFERENCES_V2 = [
    {"record_id": "tj0152-jpl-jie-lichun-2024", "term": "立春", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立春",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-02-04T08:27:00+00:00"},
    {"record_id": "tj0152-jpl-jie-jingzhe-2024", "term": "惊蛰", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/惊蛰",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-03-05T02:23:00+00:00"},
    {"record_id": "tj0152-jpl-jie-qingming-2024", "term": "清明", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/清明",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-04-04T07:02:00+00:00"},
    {"record_id": "tj0152-jpl-jie-lixia-2024", "term": "立夏", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立夏",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-05-05T00:10:00+00:00"},
    {"record_id": "tj0152-jpl-jie-mangzhong-2024", "term": "芒种", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/芒种",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-06-05T04:10:00+00:00"},
    {"record_id": "tj0152-jpl-jie-xiaoshu-2024", "term": "小暑", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/小暑",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-07-06T14:20:00+00:00"},
    {"record_id": "tj0152-jpl-jie-liqiu-2024", "term": "立秋", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立秋",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-08-07T00:09:00+00:00"},
    {"record_id": "tj0152-jpl-jie-bailu-2024", "term": "白露", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/白露",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-09-07T03:11:00+00:00"},
    {"record_id": "tj0152-jpl-jie-hanlu-2024", "term": "寒露", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/寒露",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-10-07T19:00:00+00:00"},
    {"record_id": "tj0152-jpl-jie-lidong-2024", "term": "立冬", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/立冬",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-11-06T22:20:00+00:00"},
    {"record_id": "tj0152-jpl-jie-daxue-2024", "term": "大雪", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/大雪",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2024-12-06T15:17:00+00:00"},
    {"record_id": "tj0152-jpl-jie-xiaohan-2024", "term": "小寒", "gregorian_year": 2024,
     "source_org": "Wikipedia (citing NASA JPL Horizons)",
     "source_url": "https://zh.wikipedia.org/wiki/小寒",
     "source_precision": "minute", "source_timezone": "UTC",
     "citation_class": "second_hand", "primary_verified": False,
     "published_utc": "2025-01-05T02:33:00+00:00",
     "year_note": "小寒属甲辰干支年（gregorian_year=2024），公历日期为 2025-01-05（跨年，已明确）"},
]

_FROZEN_BY_ID = {r["record_id"]: r for r in INDEPENDENT_JIE_REFERENCES_V2}
_FROZEN_BY_TERM_YEAR = {(r["term"], r["gregorian_year"]): r
                        for r in INDEPENDENT_JIE_REFERENCES_V2}
_FROZEN_FIELDS = ("record_id", "term", "gregorian_year", "source_org",
                  "source_url", "source_precision", "source_timezone",
                  "citation_class", "primary_verified", "published_utc")


def get_frozen_reference(term, gregorian_year):
    """Return the frozen reference for (term, year); fail-closed when absent."""
    try:
        return _FROZEN_BY_TERM_YEAR[(term, gregorian_year)]
    except KeyError:
        raise ValueError(
            "no frozen reference for term %r year %r" % (term, gregorian_year))


def _check_tz_offset_correspondence(published_utc_iso, source_timezone):
    """Verify a claimed timezone genuinely matches an offset-bearing time.

    Raises ValueError when the zone is unknown or when the offset carried by
    the ISO time contradicts the zone's real offset at that instant.
    """
    try:
        published = datetime.fromisoformat(published_utc_iso)
    except ValueError as exc:
        raise ValueError("published_utc is not a valid ISO datetime") from exc
    if (published.tzinfo is None or published.utcoffset() is None
            or published.microsecond != 0):
        raise ValueError("published_utc must be offset-aware whole seconds")
    if ZoneInfo is None:
        raise ValueError("zoneinfo is unavailable; timezone source unverifiable")
    try:
        tz = ZoneInfo(source_timezone)
    except Exception as exc:
        raise ValueError("source_timezone is not a known zone: %r"
                         % (source_timezone,)) from exc
    real_offset = published.astimezone(tz).utcoffset()
    if published.utcoffset() != real_offset:
        raise ValueError(
            "source_timezone %r contradicts the offset %s carried by "
            "published_utc" % (source_timezone, published.utcoffset()))


def verify_reference_record(reference):
    """Bind an incoming reference record to the frozen set; fail-closed.

    Checks: the record claims a known record_id; every frozen field matches
    byte-for-byte (source substitution / version mismatch / forgery rejected);
    the declared source_timezone genuinely corresponds to the offset carried
    by published_utc (not a non-empty-string check); the published year is the
    record's gregorian_year or the documented cross-year case (小寒).
    Returns the frozen record.
    """
    if type(reference) is not dict:
        raise ValueError("reference must be a dict record")
    record_id = reference.get("record_id")
    frozen = _FROZEN_BY_ID.get(record_id) if type(record_id) is str else None
    if frozen is None:
        raise ValueError(
            "reference %r is not in the frozen verified set %s; "
            "new sources require a new versioned release" % (
                record_id, REFERENCE_SET_VERSION))
    for field in _FROZEN_FIELDS:
        if reference.get(field) != frozen[field]:
            raise ValueError(
                "reference record %s field %r does not match the frozen "
                "record; source substitution or forgery is rejected" % (
                    record_id, field))
    # Timezone/offset correspondence: the offset carried by published_utc
    # must equal the source_timezone's real offset at that instant
    # (a genuine check, not a non-empty-string check).
    _check_tz_offset_correspondence(frozen["published_utc"],
                                    frozen["source_timezone"])
    published = datetime.fromisoformat(frozen["published_utc"])
    if frozen["source_precision"] not in SUPPORTED_PRECISIONS:
        raise ValueError("reference precision %r is not supported for comparison"
                         % (frozen["source_precision"],))
    # Year correspondence: published year must be the record's gregorian_year,
    # except the documented cross-year case (小寒: published in January of
    # gregorian_year + 1).
    pub_year = published.year
    gy = frozen["gregorian_year"]
    if pub_year not in (gy, gy + 1):
        raise ValueError(
            "reference published year %d does not correspond to "
            "gregorian_year %d" % (pub_year, gy))
    return frozen


def _require_aware(value, name):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("%s must be a timezone-aware datetime" % name)
    if value.microsecond != 0:
        raise ValueError("%s must be at whole-second precision" % name)
    return value


def _minute_verdict(provider_utc, published_utc):
    provider_minute = provider_utc.replace(second=0)
    published_minute = published_utc.replace(second=0, microsecond=0)
    minute_difference = int((provider_minute - published_minute).total_seconds() // 60)
    if minute_difference == 0:
        return "minute_agreement", []
    if abs(minute_difference) == 1:
        return "unresolved_minute_ambiguity", [
            "nominal one-minute difference; true difference lies in [1s, 119s]; "
            "agreement and disagreement are both undecidable at source precision",
        ]
    return "exceeds_minute_tolerance", []


def audit_jie_against_reference(*, term, gregorian_year, provider_moment_utc,
                                 reference):
    """Audit one provider Jie moment against a frozen verified reference.

    The reference is bound to the frozen set first (fail-closed); the
    caller's term/year must then match the verified record exactly.
    """
    frozen = verify_reference_record(reference)
    if frozen["term"] != term or frozen["gregorian_year"] != gregorian_year:
        raise ValueError(
            "audited (term, year) %r does not match the verified reference "
            "record %r" % ((term, gregorian_year),
                           (frozen["term"], frozen["gregorian_year"])))
    provider_moment_utc = _require_aware(provider_moment_utc, "provider_moment_utc")
    published = datetime.fromisoformat(frozen["published_utc"])
    provider_utc = provider_moment_utc.astimezone(UTC)
    published_utc = published.astimezone(UTC)
    verdict, unresolved = _minute_verdict(provider_utc, published_utc)
    second_difference = int((provider_utc - published_utc).total_seconds())
    return {
        "record_id": frozen["record_id"],
        "term": term,
        "gregorian_year": gregorian_year,
        "source_org": frozen["source_org"],
        "source_url": frozen["source_url"],
        "source_precision": frozen["source_precision"],
        "source_timezone": frozen["source_timezone"],
        "citation_class": frozen["citation_class"],
        "primary_verified": frozen["primary_verified"],
        "source_binding": "frozen_verified",
        "published_utc": published_utc.isoformat(),
        "provider_utc": provider_utc.isoformat(),
        "minute_difference": int((provider_utc.replace(second=0)
                                  - published_utc.replace(second=0)).total_seconds() // 60),
        "second_difference": second_difference,
        "tolerance_basis": ("minute-precision source: truncated-to-minute equality; "
                            "1-minute nominal difference is undecidable"),
        "verdict": verdict,
        "unresolved_items": unresolved,
        "astronomical_precision_independently_verified": False,
        "scope": "single (term, year, source) comparison only; not extrapolated",
    }


def summarize_audits(records, *, reference_set=None):
    """Summarize audit records; re-verify every record, never trust verdicts.

    Each record is bound to the reference set (frozen by default), its verdict
    recomputed from its own provider_utc against the frozen published time,
    duplicates rejected, and completeness enforced: every reference in the set
    must have exactly one record. Tampered input is rejected, never averaged.
    """
    if type(records) is not list or not records:
        raise ValueError("records must be a non-empty list")
    refs = (reference_set if reference_set is not None
            else INDEPENDENT_JIE_REFERENCES_V2)
    frozen_by_key = {(r["term"], r["gregorian_year"]): r for r in refs}
    seen = set()
    verdicts = {}
    for record in records:
        if type(record) is not dict:
            raise ValueError("audit record must be a dict")
        key = (record.get("term"), record.get("gregorian_year"))
        frozen = frozen_by_key.get(key)
        if frozen is None:
            raise ValueError(
                "audit record for %r has no reference in the verified set" % (key,))
        if key in seen:
            raise ValueError(
                "duplicate audit record for term %r year %r" % (key[0], key[1]))
        seen.add(key)
        # The record's embedded reference fields must match the frozen set.
        for field in ("source_url", "published_utc", "source_precision",
                      "source_timezone"):
            if record.get(field) != frozen[field]:
                raise ValueError(
                    "audit record for %r carries a substituted reference field "
                    "%r" % (key[0], field))
        provider_utc = _require_aware(
            datetime.fromisoformat(record["provider_utc"]), "record provider_utc")
        published_utc = datetime.fromisoformat(frozen["published_utc"]).astimezone(UTC)
        expected_verdict, _ = _minute_verdict(provider_utc.astimezone(UTC),
                                              published_utc)
        if record.get("verdict") != expected_verdict:
            raise ValueError(
                "audit record for %r claims verdict %r but recomputation gives "
                "%r; forged verdicts are rejected" % (
                    key[0], record.get("verdict"), expected_verdict))
        verdicts[expected_verdict] = verdicts.get(expected_verdict, 0) + 1
    missing = [k for k in frozen_by_key if k not in seen]
    if missing:
        raise ValueError(
            "audit records missing for %d reference(s): %s; deleting records "
            "to fake a pass is rejected" % (len(missing), missing[:3]))
    covered_terms = sorted({t for t, _ in seen})
    covered_years = sorted({y for _, y in seen})
    return {
        "audit_count": len(records),
        "verdicts": verdicts,
        "reference_set_version": REFERENCE_SET_VERSION,
        "coverage": {"terms": covered_terms, "gregorian_years": covered_years,
                     "sources": sorted({r["source_org"] for r in refs})},
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


# Versioned historical-transition evidence (P1): Asia/Shanghai UTC-offset
# transitions in 1901..2098, extracted from the real tzdata 2026c TZif binary
# (extraction method documented in the TJ-015.2 research notes). An executable
# test re-verifies every transition against the live tzdb. Quantities that
# tzdb cannot confirm (e.g. what a birth certificate actually recorded) are
# NOT in this list and stay marked unverified.
HISTORICAL_TZ_TRANSITIONS_V1 = {
    "tz_name": "Asia/Shanghai",
    "tzdata_version": "2026c",
    "evidence_version": "tj0152-tz-v1",
    "note": ("28 transitions total in 1901..2098: 16 wartime + 12 DST 1986-1991; "
             "constant +08:00 from 1949-05-28 to 1986 and from 1991-09-15 onward. "
             "UNVERIFIED from tzdb alone: the civil time actually written on any "
             "particular birth record; true solar time corrections."),
    "transitions": [
        {"utc": "1919-04-12T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1919-09-30T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1940-05-31T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1940-10-12T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1941-03-14T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1941-11-01T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1942-01-30T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1945-09-01T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1946-05-14T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1946-09-30T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1947-04-14T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1947-10-31T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1948-04-30T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1948-09-30T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1949-04-30T16:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1949-05-27T15:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1986-05-03T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1986-09-13T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1987-04-11T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1987-09-12T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1988-04-16T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1988-09-10T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1989-04-15T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1989-09-16T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1990-04-14T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1990-09-15T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
        {"utc": "1991-04-13T18:00:00+00:00", "before": "+08:00", "after": "+09:00"},
        {"utc": "1991-09-14T17:00:00+00:00", "before": "+09:00", "after": "+08:00"},
    ],
}


def _valid_offsets_for(naive_local, tz):
    """tzdb-valid UTC offsets for a civil time (empty when nonexistent)."""
    valid = set()
    for fold in (0, 1):
        candidate = naive_local.replace(tzinfo=tz, fold=fold)
        if candidate.astimezone(UTC).astimezone(tz).replace(tzinfo=None) == naive_local:
            valid.add(candidate.utcoffset())
    return valid


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


def audit_birth_instant(value, *, tz_name="Asia/Shanghai"):
    """Validate a birth instant for research use; fail-closed on incoherence.

    Accepts a tz-aware datetime (or ISO string with numeric offset). A UTC
    input is an unambiguous instant. Otherwise the civil time AS WRITTEN and
    the claimed UTC offset must both cohere with the real tzdb for tz_name:
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
