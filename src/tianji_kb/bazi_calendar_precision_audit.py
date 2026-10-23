"""Independent research audit for calendar precision claims (TJ-015.2, rev 4).

P0 anti-tamper guarantees (final review round):
- The internal frozen baseline (``_FROZEN_INTERNAL``) is NEVER exposed. The
  public collection (``INDEPENDENT_JIE_REFERENCES_V3``) holds immutable
  proxies; ``get_frozen_reference()`` returns defensive dict copies.
  Mutating anything handed out cannot pollute the verification baseline.
- ``verify_reference_record()`` checks an incoming record against the
  independent internal snapshot with FULL-dict equality (including optional
  metadata such as ``year_note``), then validates timezone/offset
  correspondence, precision support, and year correspondence. It returns a
  defensive copy of the trusted snapshot -- never an object shared with the
  input. Forgery (URL / time / year_note substitution) fails closed, so an
  ``unresolved`` result can never be re-forged into ``minute_agreement`` by
  editing a reference.
- ``summarize_audits()`` accepts ONLY complete, re-verified summaries over
  the frozen set. There is no custom-reference-set bypass: every record's
  embedded reference is re-bound to the internal baseline, every verdict is
  recomputed, duplicates are rejected, and all 12 frozen references must be
  covered exactly once.
- Provider-moment forgery is closed by INDEPENDENT REPLAY (rev 4): neither
  ``summarize_audits()`` nor the research entry trusts a caller-supplied
  ``provider_utc``. Each (term, year) moment is re-derived from the pinned
  provider (lunar-python==1.4.8, enforced via
  ``calendar_provider_guard.provider_identity()``) using the provider's own
  annual jieqi table -- the same API family as
  ``bazi_annual_reference._li_chun_of``. The trusted frozen published time
  only selects WHICH instance of a repeated term name the provider reports
  (nearest to anchor); the returned moment comes from the provider alone.
  A record whose claimed provider moment differs from the replay is
  rejected. Missing provider, version mismatch, or any replay anomaly fails
  closed -- there is no fallback path that could impersonate real evidence.

The frozen reference DATA is byte-identical to rev 3 (hence the V3 names);
rev 4 hardens only the verification binding.

Reference trust model:
- Trust is NOT self-declared by ``source_org``/``source_url`` text. Records
  carry ``citation_class`` / ``primary_verified``: JPL values are second-hand
  citations via the individual Wikipedia term pages (verified 2026-10-21 on
  the 立春/小寒 pages: each carries "數據來源：噴氣推進實驗室線上曆書系統"
  with the frozen minute values; the English "Solar term" overview and the
  Chinese "二十四节气" overview do NOT carry these tables -- only the
  per-term pages do). Primary JPL computation was NOT re-run.
- HKO availability check (2026-10-21): the HKO annual 24-term timetable
  requires a JS-driven year selector (not obtainable by text fetch); HKO's
  definitional longitude table WAS obtained and is consistent.

Honesty rules: minute-precision sources support only minute-level comparison;
a passing audit covers ONLY its listed (term, year, source); ambiguous or
nonexistent civil times are rejected, never silently guessed. This module
never modifies the Phase4-frozen ``calendar.py`` and never upgrades any
global precision flag.
"""
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

try:
    from types import MappingProxyType
except ImportError:  # pragma: no cover
    MappingProxyType = None

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

UTC = timezone.utc
REFERENCE_SET_VERSION = "tj0152-v3 collected 2026-10-21"
SUPPORTED_PRECISIONS = ("minute",)

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

# Uppercase alias keys observed in lunar-python 1.4.8's getJieQiTable().
# Pinned-provider behavior (enforced by provider_identity()); the nearest-
# to-anchor selection below does the real disambiguation.
_JIEQI_TABLE_ALIASES = {
    "DA_XUE": "大雪", "DONG_ZHI": "冬至", "XIAO_HAN": "小寒", "DA_HAN": "大寒",
    "LI_CHUN": "立春", "YU_SHUI": "雨水", "JING_ZHE": "惊蛰",
}

# Maximum allowed distance between the trusted frozen anchor and the
# provider's replayed moment. Genuine replays land within ~1 minute; anything
# farther signals a provider anomaly and fails closed.
_REPLAY_ANCHOR_WINDOW_SECONDS = 7 * 86400


def _rec(record_id, term, gregorian_year, source_url, published_utc,
         year_note=None):
    record = {
        "record_id": record_id, "term": term, "gregorian_year": gregorian_year,
        "source_org": "Wikipedia (citing NASA JPL Horizons)",
        "source_url": source_url,
        "source_precision": "minute", "source_timezone": "UTC",
        "citation_class": "second_hand", "primary_verified": False,
        "published_utc": published_utc,
    }
    if year_note is not None:
        record["year_note"] = year_note
    return record


# Internal frozen baseline: plain dicts, NEVER exposed outside this module.
_FROZEN_INTERNAL = tuple([
    _rec("tj0152-jpl-jie-lichun-2024", "立春", 2024,
         "https://zh.wikipedia.org/wiki/立春", "2024-02-04T08:27:00+00:00"),
    _rec("tj0152-jpl-jie-jingzhe-2024", "惊蛰", 2024,
         "https://zh.wikipedia.org/wiki/惊蛰", "2024-03-05T02:23:00+00:00"),
    _rec("tj0152-jpl-jie-qingming-2024", "清明", 2024,
         "https://zh.wikipedia.org/wiki/清明", "2024-04-04T07:02:00+00:00"),
    _rec("tj0152-jpl-jie-lixia-2024", "立夏", 2024,
         "https://zh.wikipedia.org/wiki/立夏", "2024-05-05T00:10:00+00:00"),
    _rec("tj0152-jpl-jie-mangzhong-2024", "芒种", 2024,
         "https://zh.wikipedia.org/wiki/芒种", "2024-06-05T04:10:00+00:00"),
    _rec("tj0152-jpl-jie-xiaoshu-2024", "小暑", 2024,
         "https://zh.wikipedia.org/wiki/小暑", "2024-07-06T14:20:00+00:00"),
    _rec("tj0152-jpl-jie-liqiu-2024", "立秋", 2024,
         "https://zh.wikipedia.org/wiki/立秋", "2024-08-07T00:09:00+00:00"),
    _rec("tj0152-jpl-jie-bailu-2024", "白露", 2024,
         "https://zh.wikipedia.org/wiki/白露", "2024-09-07T03:11:00+00:00"),
    _rec("tj0152-jpl-jie-hanlu-2024", "寒露", 2024,
         "https://zh.wikipedia.org/wiki/寒露", "2024-10-07T19:00:00+00:00"),
    _rec("tj0152-jpl-jie-lidong-2024", "立冬", 2024,
         "https://zh.wikipedia.org/wiki/立冬", "2024-11-06T22:20:00+00:00"),
    _rec("tj0152-jpl-jie-daxue-2024", "大雪", 2024,
         "https://zh.wikipedia.org/wiki/大雪", "2024-12-06T15:17:00+00:00"),
    _rec("tj0152-jpl-jie-xiaohan-2024", "小寒", 2024,
         "https://zh.wikipedia.org/wiki/小寒", "2025-01-05T02:33:00+00:00",
         year_note="小寒属甲辰干支年（gregorian_year=2024），公历日期为 "
                   "2025-01-05（跨年，已明确）"),
])

# Public collection: immutable proxies. Read-only; mutation raises TypeError.
if MappingProxyType is None:  # pragma: no cover
    raise ImportError("types.MappingProxyType is required for frozen-set safety")
INDEPENDENT_JIE_REFERENCES_V3 = tuple(
    MappingProxyType(dict(r)) for r in _FROZEN_INTERNAL)

_FROZEN_BY_ID = {r["record_id"]: r for r in _FROZEN_INTERNAL}
_FROZEN_BY_TERM_YEAR = {(r["term"], r["gregorian_year"]): r
                        for r in _FROZEN_INTERNAL}


def get_frozen_reference(term, gregorian_year):
    """Return a DEFENSIVE COPY of the frozen reference; fail-closed when absent.

    The copy is fully detached from the internal baseline: mutating it cannot
    pollute verification, and passing a mutated copy to any audit entry point
    is rejected by ``verify_reference_record()``.
    """
    try:
        return dict(_FROZEN_BY_TERM_YEAR[(term, gregorian_year)])
    except KeyError:
        raise ValueError(
            "no frozen reference for term %r year %r" % (term, gregorian_year))


def _check_tz_offset_correspondence(published_utc_iso, source_timezone):
    """Verify a claimed timezone genuinely matches an offset-bearing time."""
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
    """Bind an incoming record to the independent internal snapshot.

    Full-dict equality against the internal baseline (every field, including
    optional metadata such as ``year_note``): substitution, version mismatch
    or forgery fails closed. The internal snapshot is never shared with the
    input; the returned value is a defensive copy of the trusted baseline.
    """
    if not isinstance(reference, Mapping):
        raise ValueError("reference must be a mapping record")
    record_id = reference.get("record_id")
    internal = _FROZEN_BY_ID.get(record_id) if type(record_id) is str else None
    if internal is None:
        raise ValueError(
            "reference %r is not in the frozen verified set %s; "
            "new sources require a new versioned release" % (
                record_id, REFERENCE_SET_VERSION))
    if dict(reference) != internal:
        raise ValueError(
            "reference record %s does not exactly match the frozen baseline "
            "(field substitution, however small, is rejected)" % (record_id,))
    _check_tz_offset_correspondence(internal["published_utc"],
                                    internal["source_timezone"])
    if internal["source_precision"] not in SUPPORTED_PRECISIONS:
        raise ValueError("reference precision %r is not supported for comparison"
                         % (internal["source_precision"],))
    published = datetime.fromisoformat(internal["published_utc"])
    pub_year = published.year
    gy = internal["gregorian_year"]
    if pub_year not in (gy, gy + 1):
        raise ValueError(
            "reference published year %d does not correspond to "
            "gregorian_year %d" % (pub_year, gy))
    return dict(internal)


def _require_aware(value, name):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("%s must be a timezone-aware datetime" % name)
    if value.microsecond != 0:
        raise ValueError("%s must be at whole-second precision" % name)
    return value


def _replay_provider_jie_utc(*, term, gregorian_year, anchor_published_utc):
    """Independently re-derive the provider's jie moment for (term, year).

    The pinned provider (lunar-python==1.4.8, enforced by
    ``calendar_provider_guard.provider_identity()`` -- missing package or
    version mismatch raises) supplies its annual jieqi table, the same API
    family as ``bazi_annual_reference._li_chun_of``. The anchor is a TRUSTED
    frozen published time (already verified against the internal baseline);
    it only selects which instance of a repeated term name the provider
    reports (nearest to anchor, e.g. the cross-year 小寒). The returned moment
    is derived from the provider alone, never from caller input. Provider
    wall output is interpreted as Asia/Shanghai, matching ``_li_chun_of``.
    Any anomaly -- no candidate, candidate implausibly far from the anchor --
    fails closed with ValueError. There is no fallback.
    """
    # Deferred import: the guard (and through it the frozen calendar adapter)
    # is loaded only when a replay actually runs, never at module import.
    from tianji_kb.calendar_provider_guard import provider_identity
    provider_identity()
    if ZoneInfo is None:
        raise ValueError("zoneinfo is unavailable; provider wall time "
                         "cannot be interpreted")
    try:
        anchor = datetime.fromisoformat(anchor_published_utc)
    except ValueError as exc:
        raise ValueError("replay anchor is not a valid ISO datetime") from exc
    if anchor.tzinfo is None or anchor.utcoffset() is None:
        raise ValueError("replay anchor must be timezone-aware")
    anchor_utc = anchor.astimezone(UTC)
    try:
        from lunar_python import Solar
        table = Solar.fromYmd(gregorian_year, 7, 1).getLunar().getJieQiTable()
    except Exception as exc:
        raise ValueError(
            "provider jieqi table unavailable; refusing to impersonate "
            "evidence: %s" % (exc,)) from exc
    shanghai = ZoneInfo("Asia/Shanghai")
    best = None
    best_distance = None
    for key, solar in table.items():
        if _JIEQI_TABLE_ALIASES.get(key, key) != term:
            continue
        try:
            wall = datetime.strptime(solar.toYmdHms(), "%Y-%m-%d %H:%M:%S")
        except Exception as exc:
            raise ValueError(
                "provider returned an unparsable jie moment") from exc
        moment_utc = wall.replace(tzinfo=shanghai).astimezone(UTC)
        distance = abs((moment_utc - anchor_utc).total_seconds())
        if best is None or distance < best_distance:
            best, best_distance = moment_utc, distance
    if best is None:
        raise ValueError(
            "provider reports no %r near trusted anchor %s; refusing"
            % (term, anchor_published_utc))
    if best_distance > _REPLAY_ANCHOR_WINDOW_SECONDS:
        raise ValueError(
            "provider %r is %d seconds from the trusted anchor; refusing to "
            "accept an implausible replay" % (term, int(best_distance)))
    return best


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
    """Audit one provider Jie moment against a frozen verified reference."""
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
    result = {
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
    if "year_note" in frozen:
        result["year_note"] = frozen["year_note"]
    return result


def summarize_audits(records):
    """Summarize a COMPLETE 12-term acceptance; re-verify everything.

    No custom reference sets: every record's embedded reference is re-bound to
    the internal frozen baseline, every verdict is recomputed, duplicates
    are rejected, and all 12 frozen references must be covered exactly once.
    Additionally, every record's claimed provider moment is checked against
    an INDEPENDENT replay of the pinned provider (lunar-python==1.4.8):
    caller-supplied provider_utc is never trusted on its own, so forging
    provider moments cannot turn unresolved terms into agreements.
    Anything else fails closed. Subset analyses are not supported here; they
    must use per-term audits, each clearly labeled, and can never masquerade
    as the complete acceptance.
    """
    if type(records) is not list or not records:
        raise ValueError("records must be a non-empty list")
    seen = set()
    verdicts = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("audit record must be a mapping")
        record_id = record.get("record_id")
        internal = _FROZEN_BY_ID.get(record_id) if type(record_id) is str else None
        if internal is None:
            raise ValueError(
                "audit record references unknown record_id %r" % (record_id,))
        # Re-bind the record's embedded reference fields to the baseline.
        candidate = {}
        for key in internal.keys():
            if key not in record:
                raise ValueError(
                    "audit record for %s is missing reference field %r"
                    % (record_id, key))
            candidate[key] = record[key]
        if candidate != internal:
            raise ValueError(
                "audit record for %s carries reference fields that do not "
                "match the frozen baseline" % (record_id,))
        if "provider_utc" not in record:
            raise ValueError(
                "audit record for %s is missing provider_utc" % (record_id,))
        try:
            claimed_provider = datetime.fromisoformat(record["provider_utc"])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "audit record for %s has an invalid provider_utc" % (record_id,)) from exc
        if claimed_provider.tzinfo is None or claimed_provider.utcoffset() is None:
            raise ValueError(
                "audit record for %s has a naive provider_utc" % (record_id,))
        claimed_provider_utc = claimed_provider.astimezone(UTC)
        # Verdict recomputation from the record's own (still untrusted) claim.
        published_utc = datetime.fromisoformat(
            internal["published_utc"]).astimezone(UTC)
        expected_verdict, _ = _minute_verdict(claimed_provider_utc, published_utc)
        if record.get("verdict") != expected_verdict:
            raise ValueError(
                "audit record for %s claims verdict %r but recomputation gives "
                "%r; forged verdicts are rejected" % (
                    record_id, record.get("verdict"), expected_verdict))
        # Independent provider replay: the claimed moment must be what the
        # pinned provider actually reports for (term, year).
        replayed = _replay_provider_jie_utc(
            term=internal["term"], gregorian_year=internal["gregorian_year"],
            anchor_published_utc=internal["published_utc"])
        if claimed_provider_utc != replayed:
            raise ValueError(
                "audit record for %s claims provider_utc %s but the independent "
                "provider replay gives %s; forged provider moments are rejected"
                % (record_id, claimed_provider_utc.isoformat(),
                   replayed.isoformat()))
        key = (internal["term"], internal["gregorian_year"])
        if key in seen:
            raise ValueError(
                "duplicate audit record for term %r year %r" % (key[0], key[1]))
        seen.add(key)
        verdicts[expected_verdict] = verdicts.get(expected_verdict, 0) + 1
    expected_keys = set(_FROZEN_BY_TERM_YEAR.keys())
    if seen != expected_keys:
        missing = sorted(expected_keys - seen)
        raise ValueError(
            "incomplete acceptance: %d of 12 references covered; missing %s; "
            "deleting records to fake a pass is rejected"
            % (len(seen), [m[0] for m in missing][:4]))
    covered_terms = sorted({t for t, _ in seen})
    covered_years = sorted({y for _, y in seen})
    return {
        "audit_count": len(records),
        "verdicts": verdicts,
        "reference_set_version": REFERENCE_SET_VERSION,
        "scope": "complete_12_term_acceptance",
        "provider_replay": "lunar-python==1.4.8 independent replay per (term, year)",
        "coverage": {"terms": covered_terms, "gregorian_years": covered_years,
                     "sources": sorted({r["source_org"] for r in _FROZEN_INTERNAL})},
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
    """Classify a wall-clock time against the real tzdb (fail-closed helper)."""
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
    """Validate a birth instant for research use; fail-closed on incoherence."""
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
