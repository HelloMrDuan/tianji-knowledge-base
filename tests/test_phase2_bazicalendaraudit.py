"""TJ-015.2 final P0 anti-tamper: frozen-set immutability + summary bypass
closure. Real lunar-python + real tzdb; no network."""
import unittest
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from zoneinfo import ZoneInfo

from lunar_python import Solar

import tianji_kb.bazi_calendar_precision_audit as audit_mod
from tianji_kb.bazi_calendar_precision_audit import (
    HISTORICAL_TZ_TRANSITIONS_V1,
    INDEPENDENT_JIE_REFERENCES_V3,
    REFERENCE_SET_VERSION,
    _check_tz_offset_correspondence,
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
        # Baseline untouched:
        self.assertEqual(
            get_frozen_reference("立春", 2024)["source_url"],
            "https://zh.wikipedia.org/wiki/立春")
        # Tampered copy rejected:
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
        # The genuine audit is unaffected:
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
        # Internal baseline still verifies:
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
        # Mutating a returned snapshot does not affect later verifications:
        verify_reference_record(get_frozen_reference("立春", 2024))

    def test_unknown_record_id_rejected(self):
        ref = dict(get_frozen_reference("立春", 2024))
        ref["record_id"] = "tj0152-forged-1"
        with self.assertRaisesRegex(ValueError, "not in the frozen verified set"):
            verify_reference_record(ref)

    def test_full_twelve_still_8_agreement_4_unresolved(self):
        records = all_real_records()
        verdicts = [r["verdict"] for r in records]
        self.assertEqual(verdicts.count("minute_agreement"), 8)
        self.assertEqual(verdicts.count("unresolved_minute_ambiguity"), 4)
        by_term = {r["term"]: r["verdict"] for r in records}
        for term in ("惊蛰", "芒种", "寒露", "小寒"):
            self.assertEqual(by_term[term], "unresolved_minute_ambiguity")


class SummaryBypassClosureTests(unittest.TestCase):
    def test_complete_twelve_summarizes(self):
        summary = summarize_audits(all_real_records())
        self.assertEqual(summary["audit_count"], 12)
        self.assertEqual(summary["verdicts"].get("minute_agreement"), 8)
        self.assertEqual(summary["verdicts"].get("unresolved_minute_ambiguity"), 4)
        self.assertEqual(summary["scope"], "complete_12_term_acceptance")
        self.assertFalse(summary["astronomical_precision_independently_verified"])
        self.assertTrue(summary["research_only"])

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

    def test_empty_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            summarize_audits([])


class ReferenceBindingTests(unittest.TestCase):
    def test_invalid_source_timezone_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a known zone"):
            _check_tz_offset_correspondence(
                "2024-02-04T08:27:00+00:00", "Mars/Olympus")

    def test_utc_vs_offset_contradiction_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts the offset"):
            _check_tz_offset_correspondence(
                "2024-02-04T08:27:00+08:00", "UTC")

    def test_reference_year_misuse_rejected(self):
        ref = get_frozen_reference("立春", 2024)
        with self.assertRaisesRegex(ValueError, "does not match the verified"):
            audit_jie_against_reference(
                term="立春", gregorian_year=2025,
                provider_moment_utc=provider_jie_utc("立春", ref),
                reference=ref)

    def test_second_hand_citation_marked(self):
        record = real_record("立春", 2024)
        self.assertEqual(record["citation_class"], "second_hand")
        self.assertFalse(record["primary_verified"])
        self.assertEqual(record["source_binding"], "frozen_verified")
        self.assertFalse(record["astronomical_precision_independently_verified"])


class ResearchEntryTests(unittest.TestCase):
    def test_entry_birth_real(self):
        report = research_audit_birth(birth_value="1988-07-01T12:00:00+09:00")
        self.assertEqual(report["birth"]["utc_instant"], "1988-07-01T03:00:00+00:00")
        self.assertTrue(report["research_only"])

    def test_entry_birth_historical_offset_misuse_rejected(self):
        with self.assertRaisesRegex(ValueError, "contradicts tzdb"):
            research_audit_birth(birth_value="1988-07-01T12:00:00+08:00")

    def test_entry_jie_real(self):
        ref = get_frozen_reference("立春", 2024)
        record = research_audit_jie(
            term="立春", gregorian_year=2024,
            provider_moment_utc=provider_jie_utc("立春", ref))
        self.assertEqual(record["verdict"], "minute_agreement")

    def test_entry_summary_roundtrip(self):
        records = [research_audit_jie(
            term=r["term"], gregorian_year=r["gregorian_year"],
            provider_moment_utc=provider_jie_utc(r["term"], dict(r)))
            for r in INDEPENDENT_JIE_REFERENCES_V3]
        summary = research_audit_summary(records)
        self.assertEqual(summary["audit_count"], 12)

    def test_entry_forbids_dayun_conclusions(self):
        import tianji_kb.bazi_calendar_research_entry as entry_mod
        for kind in FORBIDDEN_CONCLUSION_KINDS:
            self.assertFalse(hasattr(entry_mod, kind), kind)

    def test_reference_catalog_v3(self):
        catalog = reference_catalog()
        self.assertEqual(catalog["record_count"], 12)
        self.assertIn("tj0152-v3", catalog["reference_set_version"])


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

    def test_evidence_marks_unverified_scope(self):
        self.assertIn("UNVERIFIED", HISTORICAL_TZ_TRANSITIONS_V1["note"])


class CivilTimeAuditTests(unittest.TestCase):
    def test_dst_gap_nonexistent_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1986-05-04T02:30:00+08:00")

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


if __name__ == "__main__":
    unittest.main()
