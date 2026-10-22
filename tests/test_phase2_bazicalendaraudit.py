"""TJ-015.2 rev 4: provider-replay gate closes provider_utc forgery; restores
all valid historical regressions from the 49-test suite. Real lunar-python
(pinned 1.4.8) + real tzdb; no network.

Coverage vs the 49-test suite (PR #294): 13 tests restored verbatim-adapted,
5 equivalently covered by stronger rev-3 tests (documented below), 0 silently
dropped:
- test_source_url_substitution_rejected -> test_mutating_returned_url_leaves_baseline_intact
- test_published_time_tampering_rejected -> test_mutating_returned_published_utc_does_not_affect_audit
- test_summary_recomputes_verdicts -> test_complete_twelve_summarizes (now replay-backed)
- test_deleted_failure_records_rejected -> test_eight_only_rejected_as_incomplete
- test_substituted_reference_in_record_rejected -> test_arbitrary_source_url_set_rejected
"""
import copy
import unittest
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from unittest import mock
from zoneinfo import ZoneInfo

from lunar_python import Solar

import tianji_kb.bazi_calendar_precision_audit as audit_mod
import tianji_kb.bazi_calendar_research_entry as entry_mod
from tianji_kb.bazi_calendar_precision_audit import (
    HISTORICAL_TZ_TRANSITIONS_V1,
    INDEPENDENT_JIE_REFERENCES_V3,
    REFERENCE_SET_VERSION,
    _check_tz_offset_correspondence,
    _replay_provider_jie_utc,
    audit_birth_instant,
    audit_jie_against_reference,
    classify_civil_time,
    get_frozen_reference,
    summarize_audits,
    tzdata_version,
    verify_reference_record,
)
from tianji_kb.bazi_calendar_research_entry import (
    FORBIDDEN_CONCLUSION_KINDS,
    reference_catalog,
    research_audit_birth,
    research_audit_jie,
    research_audit_summary,
)
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.calendar import calendar

UTC = timezone.utc
CHINA = ZoneInfo("Asia/Shanghai")


def provider_jie_utc(term, ref):
    published = datetime.fromisoformat(ref["published_utc"])
    lunar = Solar.fromYmdHms(published.year, published.month, 15, 12, 0, 0).getLunar()
    found = lunar.getPrevJie(False)
    if found is None or found.getName() != term:
        raise ValueError("setup: provider did not return " + term)
    return datetime.strptime(
        found.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=CHINA)


def real_record(term, year):
    ref = get_frozen_reference(term, year)
    return audit_jie_against_reference(
        term=term, gregorian_year=year,
        provider_moment_utc=provider_jie_utc(term, ref), reference=ref)


def all_real_records():
    return [real_record(r["term"], r["gregorian_year"])
            for r in INDEPENDENT_JIE_REFERENCES_V3]


class ReferenceBindingTests(unittest.TestCase):
    def test_all_frozen_records_verify(self):
        for ref in INDEPENDENT_JIE_REFERENCES_V3:
            frozen = verify_reference_record(ref)
            self.assertEqual(frozen["record_id"], ref["record_id"])

    def test_unknown_record_id_rejected(self):
        ref = dict(get_frozen_reference("立春", 2024))
        ref["record_id"] = "tj0152-forged-1"
        with self.assertRaisesRegex(ValueError, "not in the frozen verified set"):
            verify_reference_record(ref)

    def test_missing_record_id_rejected(self):
        ref = dict(get_frozen_reference("立春", 2024))
        del ref["record_id"]
        with self.assertRaisesRegex(ValueError, "not in the frozen verified set"):
            verify_reference_record(ref)

    def test_invalid_source_timezone_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a known zone"):
            _check_tz_offset_correspondence(
                "2024-02-04T08:27:00+00:00", "Mars/Olympus")

    def test_utc_vs_offset_contradiction_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts the offset"):
            _check_tz_offset_correspondence(
                "2024-02-04T08:27:00+08:00", "UTC")

    def test_timezone_offset_correspondence_accepts_valid(self):
        _check_tz_offset_correspondence("2024-02-04T08:27:00+00:00", "UTC")

    def test_reference_year_misuse_rejected(self):
        ref = get_frozen_reference("立春", 2024)
        with self.assertRaisesRegex(ValueError, "does not match the verified"):
            audit_jie_against_reference(
                term="立春", gregorian_year=2025,
                provider_moment_utc=provider_jie_utc("立春", ref),
                reference=ref)

    def test_term_mismatch_rejected(self):
        ref = get_frozen_reference("立春", 2024)
        with self.assertRaisesRegex(ValueError, "does not match the verified"):
            audit_jie_against_reference(
                term="惊蛰", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc("立春", ref),
                reference=ref)

    def test_xiaohan_cross_year_explicit(self):
        ref = get_frozen_reference("小寒", 2024)
        self.assertIn("year_note", ref)
        self.assertIn("2025-01-05", ref["year_note"])
        verify_reference_record(ref)  # must not raise on the cross-year case
        record = real_record("小寒", 2024)
        self.assertEqual(record["published_utc"], "2025-01-05T02:33:00+00:00")

    def test_second_hand_citation_marked(self):
        for ref in INDEPENDENT_JIE_REFERENCES_V3:
            self.assertEqual(ref["citation_class"], "second_hand")
            self.assertFalse(ref["primary_verified"])
        record = real_record("立春", 2024)
        self.assertEqual(record["citation_class"], "second_hand")
        self.assertFalse(record["primary_verified"])
        self.assertEqual(record["source_binding"], "frozen_verified")
        self.assertFalse(record["astronomical_precision_independently_verified"])

    def test_hko_definition_crosscheck_present(self):
        defs = audit_mod.HKO_DEFINITION_CROSSCHECK
        self.assertIn("hko.gov.hk", defs["source"])
        self.assertEqual(defs["jie_longitudes"]["立春"], 315)
        self.assertEqual(defs["jie_longitudes"]["惊蛰"], 345)
        self.assertIn("unavailable", defs["note"])


class FrozenSetImmutabilityTests(unittest.TestCase):
    def test_public_collection_is_immutable(self):
        self.assertEqual(len(INDEPENDENT_JIE_REFERENCES_V3), 12)
        for record in INDEPENDENT_JIE_REFERENCES_V3:
            self.assertIsInstance(record, MappingProxyType)
        with self.assertRaises(TypeError):
            INDEPENDENT_JIE_REFERENCES_V3[0]["source_url"] = "https://evil.example/"
        with self.assertRaises(TypeError):
            INDEPENDENT_JIE_REFERENCES_V3[0]["published_utc"] = "2030-01-01T00:00:00+00:00"

    def test_mutating_returned_url_leaves_baseline_intact(self):
        ref = get_frozen_reference("立春", 2024)
        ref["source_url"] = "https://evil.example.org/fake"
        self.assertEqual(
            get_frozen_reference("立春", 2024)["source_url"],
            "https://zh.wikipedia.org/wiki/立春")
        with self.assertRaisesRegex(ValueError, "does not exactly match"):
            verify_reference_record(ref)
        with self.assertRaisesRegex(ValueError, "does not exactly match"):
            audit_jie_against_reference(
                term="立春", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc(
                    "立春", get_frozen_reference("立春", 2024)),
                reference=ref)

    def test_mutating_returned_published_utc_does_not_affect_audit(self):
        ref = get_frozen_reference("惊蛰", 2024)
        ref["published_utc"] = "2024-03-05T02:22:00+00:00"  # forge agreement
        with self.assertRaisesRegex(ValueError, "does not exactly match"):
            audit_jie_against_reference(
                term="惊蛰", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc(
                    "惊蛰", get_frozen_reference("惊蛰", 2024)),
                reference=ref)
        record = real_record("惊蛰", 2024)
        self.assertEqual(record["verdict"], "unresolved_minute_ambiguity")

    def test_public_collection_mutation_cannot_pollute_internal(self):
        snapshot_before = [dict(r) for r in INDEPENDENT_JIE_REFERENCES_V3]
        try:
            INDEPENDENT_JIE_REFERENCES_V3[3]["source_url"] = "https://evil.example/"
        except TypeError:
            pass
        snapshot_after = [dict(r) for r in INDEPENDENT_JIE_REFERENCES_V3]
        self.assertEqual(snapshot_before, snapshot_after)
        verify_reference_record(get_frozen_reference("立夏", 2024))

    def test_xiaohan_year_note_tampering_rejected(self):
        ref = get_frozen_reference("小寒", 2024)
        self.assertIn("year_note", ref)
        ref["year_note"] = "tampered note"
        with self.assertRaisesRegex(ValueError, "does not exactly match"):
            verify_reference_record(ref)

    def test_verify_returns_independent_snapshot(self):
        ref = get_frozen_reference("立春", 2024)
        snap1 = verify_reference_record(ref)
        snap2 = verify_reference_record(ref)
        self.assertEqual(snap1, snap2)
        self.assertIsNot(snap1, snap2)
        snap1["source_url"] = "https://evil.example/"
        verify_reference_record(get_frozen_reference("立春", 2024))

    def test_full_twelve_still_8_agreement_4_unresolved(self):
        records = all_real_records()
        verdicts = [r["verdict"] for r in records]
        self.assertEqual(verdicts.count("minute_agreement"), 8)
        self.assertEqual(verdicts.count("unresolved_minute_ambiguity"), 4)
        by_term = {r["term"]: r["verdict"] for r in records}
        for term in ("惊蛰", "芒种", "寒露", "小寒"):
            self.assertEqual(by_term[term], "unresolved_minute_ambiguity")


class ProviderReplayTests(unittest.TestCase):
    def test_provider_replay_matches_all_twelve_honest_moments(self):
        for r in INDEPENDENT_JIE_REFERENCES_V3:
            term, gy = r["term"], r["gregorian_year"]
            replayed = _replay_provider_jie_utc(
                term=term, gregorian_year=gy,
                anchor_published_utc=r["published_utc"])
            honest_moment = provider_jie_utc(term, dict(r)).astimezone(UTC)
            self.assertEqual(replayed, honest_moment, term)

    def test_provider_identity_ok(self):
        from tianji_kb.calendar_provider_guard import provider_identity
        identity = provider_identity()
        self.assertEqual(identity["installed_version"], "1.4.8")
        self.assertTrue(identity["installed_version_matches_pin"])

    def test_provider_identity_error_rejected(self):
        with mock.patch(
                "tianji_kb.calendar_provider_guard.provider_identity",
                side_effect=ValueError("simulated provider identity failure")):
            with self.assertRaisesRegex(
                    ValueError, "simulated provider identity failure"):
                summarize_audits(all_real_records())

    def test_forged_provider_utc_attack_rejected(self):
        # Exact P0 attack: forge every provider_utc as the reference moment.
        forged = [
            {
                **get_frozen_reference(r["term"], r["gregorian_year"]),
                "provider_utc": r["published_utc"],
                "verdict": "minute_agreement",
            }
            for r in INDEPENDENT_JIE_REFERENCES_V3
        ]
        with self.assertRaisesRegex(
                ValueError, "forged provider moments are rejected"):
            summarize_audits(forged)

    def test_forged_four_unresolved_provider_moments_rejected(self):
        records = all_real_records()
        forged_count = 0
        for i, r in enumerate(records):
            if r["verdict"] == "unresolved_minute_ambiguity":
                records[i] = dict(r)
                records[i]["provider_utc"] = r["published_utc"]
                records[i]["verdict"] = "minute_agreement"
                forged_count += 1
        self.assertEqual(forged_count, 4)
        with self.assertRaisesRegex(
                ValueError, "forged provider moments are rejected"):
            summarize_audits(records)

    def test_tampered_provider_moment_with_consistent_verdict_rejected(self):
        records = all_real_records()
        tampered = dict(records[0])
        shifted = datetime.fromisoformat(tampered["provider_utc"]) + timedelta(minutes=2)
        tampered["provider_utc"] = shifted.isoformat()
        tampered["verdict"] = "exceeds_minute_tolerance"  # consistent with shift
        records[0] = tampered
        with self.assertRaisesRegex(
                ValueError, "forged provider moments are rejected"):
            summarize_audits(records)

    def test_entry_jie_forged_moment_rejected(self):
        ref = get_frozen_reference("立春", 2024)
        forged_moment = datetime.fromisoformat(ref["published_utc"])
        with self.assertRaisesRegex(ValueError, "forged moments are rejected"):
            research_audit_jie(
                term="立春", gregorian_year=2024,
                provider_moment_utc=forged_moment)


class SummaryBypassClosureTests(unittest.TestCase):
    def test_complete_twelve_summarizes(self):
        summary = summarize_audits(all_real_records())
        self.assertEqual(summary["audit_count"], 12)
        self.assertEqual(summary["verdicts"].get("minute_agreement"), 8)
        self.assertEqual(summary["verdicts"].get("unresolved_minute_ambiguity"), 4)
        self.assertEqual(summary["scope"], "complete_12_term_acceptance")
        self.assertEqual(summary["reference_set_version"], REFERENCE_SET_VERSION)
        self.assertIn("independent replay", summary["provider_replay"])
        self.assertFalse(summary["astronomical_precision_independently_verified"])
        self.assertFalse(summary["historical_timezone_independently_verified"])
        self.assertTrue(summary["research_only"])
        self.assertIn("must NOT be extrapolated", summary["coverage_disclaimer"])

    def test_single_forged_reference_rejected(self):
        forged = dict(get_frozen_reference("立春", 2024))
        forged["source_url"] = "https://attacker.example/jpl"
        forged["published_utc"] = "2024-02-04T08:27:00+00:00"
        record = {
            "record_id": forged["record_id"], "term": "立春", "gregorian_year": 2024,
            "source_org": forged["source_org"], "source_url": forged["source_url"],
            "source_precision": "minute", "source_timezone": "UTC",
            "citation_class": "second_hand", "primary_verified": False,
            "published_utc": forged["published_utc"],
            "provider_utc": "2024-02-04T08:27:23+00:00",
            "verdict": "minute_agreement",
        }
        with self.assertRaisesRegex(ValueError, "do not match the frozen baseline"):
            summarize_audits([record])

    def test_arbitrary_source_url_set_rejected(self):
        records = all_real_records()
        for r in records:
            r["source_url"] = "https://attacker.example/all"
        with self.assertRaisesRegex(ValueError, "do not match the frozen baseline"):
            summarize_audits(records)

    def test_forged_all_agreement_rejected(self):
        records = all_real_records()
        for r in records:
            if r["verdict"] == "unresolved_minute_ambiguity":
                r["published_utc"] = r["provider_utc"]  # forge agreement
                r["verdict"] = "minute_agreement"
        with self.assertRaisesRegex(ValueError, "do not match the frozen baseline"):
            summarize_audits(records)

    def test_forged_verdict_recompute_rejected(self):
        records = all_real_records()
        records[0] = dict(records[0])
        shifted = datetime.fromisoformat(records[0]["provider_utc"]) + timedelta(minutes=5)
        records[0]["provider_utc"] = shifted.isoformat()
        records[0]["verdict"] = "minute_agreement"
        with self.assertRaisesRegex(ValueError, "forged verdicts are rejected"):
            summarize_audits(records)

    def test_eight_only_rejected_as_incomplete(self):
        records = [r for r in all_real_records()
                   if r["verdict"] == "minute_agreement"]
        with self.assertRaisesRegex(ValueError, "incomplete acceptance"):
            summarize_audits(records)

    def test_duplicate_records_rejected(self):
        records = all_real_records()
        records.append(dict(records[0]))
        with self.assertRaisesRegex(ValueError, "duplicate audit record"):
            summarize_audits(records)

    def test_record_without_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown record_id"):
            summarize_audits([{"term": "立春", "gregorian_year": 2030,
                               "verdict": "minute_agreement",
                               "provider_utc": "2030-02-04T08:27:00+00:00"}])

    def test_empty_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            summarize_audits([])


class ResearchEntryTests(unittest.TestCase):
    def test_entry_birth_real(self):
        report = research_audit_birth(birth_value="1988-07-01T12:00:00+09:00")
        self.assertEqual(report["birth"]["utc_instant"], "1988-07-01T03:00:00+00:00")
        self.assertTrue(report["research_only"])
        self.assertFalse(report["public_enabled"])
        self.assertFalse(report["ai_enabled"])
        self.assertFalse(report["precision_certification"]
                         ["astronomical_precision_independently_verified"])

    def test_entry_birth_historical_offset_misuse_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts tzdb"):
            research_audit_birth(birth_value="1988-07-01T12:00:00+08:00")

    def test_entry_birth_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            research_audit_birth(birth_value="1986-05-04T02:30:00+08:00")

    def test_entry_birth_ambiguous_named_zone_rejected(self):
        with self.assertRaisesRegex(ValueError, "silent guess"):
            research_audit_birth(
                birth_value=datetime(1986, 9, 14, 1, 30, tzinfo=CHINA))

    def test_entry_jie_real(self):
        ref = get_frozen_reference("立春", 2024)
        record = research_audit_jie(
            term="立春", gregorian_year=2024,
            provider_moment_utc=provider_jie_utc("立春", ref))
        self.assertEqual(record["verdict"], "minute_agreement")
        self.assertEqual(record["source_binding"], "frozen_verified")

    def test_entry_jie_unknown_term_rejected(self):
        with self.assertRaisesRegex(ValueError, "no frozen reference"):
            research_audit_jie(
                term="立秋", gregorian_year=2030,
                provider_moment_utc=datetime(2030, 8, 7, 8, 9, tzinfo=CHINA))

    def test_entry_summary_roundtrip(self):
        records = [research_audit_jie(
            term=r["term"], gregorian_year=r["gregorian_year"],
            provider_moment_utc=provider_jie_utc(r["term"], dict(r)))
            for r in INDEPENDENT_JIE_REFERENCES_V3]
        summary = research_audit_summary(records)
        self.assertEqual(summary["audit_count"], 12)
        self.assertEqual(summary["verdicts"].get("minute_agreement"), 8)
        self.assertEqual(summary["verdicts"].get("unresolved_minute_ambiguity"), 4)

    def test_entry_forbids_dayun_conclusions(self):
        for kind in FORBIDDEN_CONCLUSION_KINDS:
            self.assertFalse(hasattr(entry_mod, kind), kind)
        report = research_audit_birth(birth_value="2024-05-15T12:00:00+08:00")
        blob = str(report)
        for kind in FORBIDDEN_CONCLUSION_KINDS:
            self.assertNotIn(kind, blob)

    def test_entry_does_not_import_frozen_calendar(self):
        import inspect
        source = inspect.getsource(entry_mod)
        self.assertNotIn("from .calendar import", source)
        self.assertNotIn("from tianji_kb.calendar import", source)

    def test_reference_catalog_lists_frozen_set(self):
        catalog = reference_catalog()
        self.assertEqual(catalog["record_count"], 12)
        self.assertEqual(catalog["reference_set_version"], REFERENCE_SET_VERSION)


class HistoricalTzEvidenceTests(unittest.TestCase):
    def _fmt(self, td):
        total = int(td.total_seconds())
        sign = "+" if total >= 0 else "-"
        total = abs(total)
        return "%s%02d:%02d" % (sign, total // 3600, (total % 3600) // 60)

    def test_versioned_transitions_match_live_tzdb(self):
        ev = HISTORICAL_TZ_TRANSITIONS_V1
        self.assertEqual(len(ev["transitions"]), 28)
        tz = ZoneInfo(ev["tz_name"])
        for tr in ev["transitions"]:
            t = datetime.fromisoformat(tr["utc"])
            before = (t - timedelta(seconds=1)).astimezone(tz).utcoffset()
            after = t.astimezone(tz).utcoffset()
            self.assertEqual(self._fmt(before), tr["before"], tr["utc"])
            self.assertEqual(self._fmt(after), tr["after"], tr["utc"])

    def test_transitions_sorted_and_unique(self):
        instants = [t["utc"] for t in HISTORICAL_TZ_TRANSITIONS_V1["transitions"]]
        self.assertEqual(instants, sorted(instants))
        self.assertEqual(len(set(instants)), 28)

    def test_evidence_marks_unverified_scope(self):
        self.assertIn("UNVERIFIED", HISTORICAL_TZ_TRANSITIONS_V1["note"])


class CivilTimeAuditTests(unittest.TestCase):
    def test_dst_gap_nonexistent_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1986-05-04T02:30:00+08:00")

    def test_wartime_dst_gap_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1940-06-01T00:30:00+08:00")

    def test_dst_overlap_named_zone_rejected_no_silent_fold(self):
        self.assertEqual(
            classify_civil_time(datetime(1986, 9, 14, 1, 30), "Asia/Shanghai"),
            "ambiguous")
        with self.assertRaisesRegex(ValueError, "silent guess"):
            audit_birth_instant(datetime(1986, 9, 14, 1, 30, tzinfo=CHINA))

    def test_dst_overlap_explicit_offsets_distinguished(self):
        first = audit_birth_instant("1986-09-14T01:30:00+09:00")
        second = audit_birth_instant("1986-09-14T01:30:00+08:00")
        self.assertEqual(first["utc_instant"], "1986-09-13T16:30:00+00:00")
        self.assertEqual(second["utc_instant"], "1986-09-13T17:30:00+00:00")

    def test_historical_offset_misuse_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts tzdb"):
            audit_birth_instant("1988-07-01T12:00:00+08:00")

    def test_naive_birth_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            audit_birth_instant("1988-07-01T12:00:00")

    def test_unknown_timezone_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown timezone"):
            audit_birth_instant("2024-05-15T12:00:00+08:00", tz_name="Mars/Olympus")

    def test_same_utc_instant_different_representations(self):
        via_offset = audit_birth_instant("1988-07-01T12:00:00+09:00")
        via_utc = audit_birth_instant(datetime(1988, 7, 1, 3, 0, tzinfo=UTC))
        self.assertEqual(via_offset["utc_instant"], via_utc["utc_instant"])

    def test_tzdb_version_recorded(self):
        self.assertNotEqual(tzdata_version(), "tzdata-version-unverified")


class LeapCenturyBoundaryTests(unittest.TestCase):
    def test_1900_not_leap_year_rejected(self):
        with self.assertRaises(ValueError):
            calendar("1900-02-29T12:00:00+08:00")

    def test_2000_is_leap_year(self):
        self.assertEqual(
            calendar("2000-02-29T12:00:00+08:00")["month_ganzhi"], "戊寅")

    def test_2100_not_leap_year_rejected(self):
        with self.assertRaises(ValueError):
            calendar("2100-02-29T12:00:00+08:00")

    def test_2100_outside_provider_range(self):
        with self.assertRaisesRegex(ValueError, "1900..2099"):
            calendar("2100-06-01T12:00:00+08:00")

    def test_century_boundary_year_pillar_unchanged(self):
        self.assertEqual(
            calendar("1999-12-31T12:00:00+08:00")["year_ganzhi"], "己卯")
        self.assertEqual(
            calendar("2000-01-01T12:00:00+08:00")["year_ganzhi"], "己卯")

    def test_2099_boundary(self):
        result = calendar("2099-06-01T12:00:00+08:00")
        with self.assertRaisesRegex(ValueError, "1901..2098"):
            adjacent_jie_distance(
                "2099-06-01T12:00:00+08:00", "forward",
                expected_month_ganzhi=result["month_ganzhi"])

    def test_feb28_leap_day_mar1_continuity(self):
        days = ["2024-02-28T12:00:00+08:00", "2024-02-29T12:00:00+08:00",
                "2024-03-01T12:00:00+08:00"]
        ganzhis = [calendar(day)["day_ganzhi"] for day in days]
        self.assertEqual(len(set(ganzhis)), 3)


if __name__ == "__main__":
    unittest.main()
