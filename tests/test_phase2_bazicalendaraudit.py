"""TJ-015.2: historical-timezone, leap/century and independent-precision audits.

Real tzdb (system zoneinfo), real lunar-python provider, and frozen
independent reference records. No network in tests: the reference records
carry their provenance (source URL, version, precision, timezone).
"""
import copy
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from lunar_python import Solar

from tianji_kb.bazi_calendar_precision_audit import (
    INDEPENDENT_JIE_REFERENCES_V1,
    audit_birth_instant,
    audit_jie_against_reference,
    classify_civil_time,
    summarize_audits,
    tzdata_version,
)
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.calendar import calendar

UTC = timezone.utc
CHINA = ZoneInfo("Asia/Shanghai")


def provider_jie_utc(term, ref):
    """Provider moment for the jie matching the reference's published date."""
    published = datetime.fromisoformat(ref["published_utc"])
    lunar = Solar.fromYmdHms(published.year, published.month, 15, 12, 0, 0).getLunar()
    found = lunar.getPrevJie(False)
    if found is None or found.getName() != term:
        raise ValueError("setup: provider did not return " + term)
    return datetime.strptime(
        found.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=CHINA)


class IndependentReferenceAuditTests(unittest.TestCase):
    def test_twelve_jie_minute_level_audit(self):
        results = []
        for ref in INDEPENDENT_JIE_REFERENCES_V1:
            moment = provider_jie_utc(ref["term"], ref)
            results.append(audit_jie_against_reference(
                term=ref["term"], gregorian_year=ref["gregorian_year"],
                provider_moment_utc=moment, reference=ref))
        verdicts = [r["verdict"] for r in results]
        self.assertEqual(verdicts.count("minute_agreement"), 8)
        self.assertEqual(verdicts.count("unresolved_minute_ambiguity"), 4)
        self.assertNotIn("exceeds_minute_tolerance", verdicts)
        by_term = {r["term"]: r["verdict"] for r in results}
        for term in ("惊蛰", "芒种", "寒露", "小寒"):
            self.assertEqual(by_term[term], "unresolved_minute_ambiguity")
            record = next(r for r in results if r["term"] == term)
            self.assertTrue(record["unresolved_items"])
        for record in results:
            self.assertFalse(record["astronomical_precision_independently_verified"])
            self.assertIn("not extrapolated", record["scope"])

    def test_audit_summary_never_upgrades_global_flags(self):
        results = [audit_jie_against_reference(
            term=ref["term"], gregorian_year=ref["gregorian_year"],
            provider_moment_utc=provider_jie_utc(ref["term"], ref),
            reference=ref) for ref in INDEPENDENT_JIE_REFERENCES_V1]
        summary = summarize_audits(results)
        self.assertEqual(summary["audit_count"], 12)
        self.assertFalse(summary["astronomical_precision_independently_verified"])
        self.assertFalse(summary["historical_timezone_independently_verified"])
        self.assertTrue(summary["research_only"])
        self.assertIn("must NOT be extrapolated", summary["coverage_disclaimer"])
        self.assertEqual(summary["coverage"]["gregorian_years"], [2024])

    def test_reference_records_carry_provenance(self):
        self.assertEqual(len(INDEPENDENT_JIE_REFERENCES_V1), 12)
        for ref in INDEPENDENT_JIE_REFERENCES_V1:
            for key in ("term", "gregorian_year", "source_org", "source_url",
                        "source_precision", "source_timezone", "published_utc"):
                self.assertTrue(ref[key], key)
            self.assertEqual(ref["source_precision"], "minute")
            self.assertEqual(ref["gregorian_year"], 2024)

    def test_tampered_reference_detected_as_disagreement(self):
        ref = copy.deepcopy(INDEPENDENT_JIE_REFERENCES_V1[0])
        published = datetime.fromisoformat(ref["published_utc"])
        ref["published_utc"] = (published + timedelta(minutes=5)).isoformat()
        moment = provider_jie_utc("立春", INDEPENDENT_JIE_REFERENCES_V1[0])
        record = audit_jie_against_reference(
            term="立春", gregorian_year=2024,
            provider_moment_utc=moment, reference=ref)
        self.assertEqual(record["verdict"], "exceeds_minute_tolerance")

    def test_reference_missing_timezone_rejected(self):
        ref = copy.deepcopy(INDEPENDENT_JIE_REFERENCES_V1[0])
        del ref["source_timezone"]
        with self.assertRaisesRegex(ValueError, "missing required field"):
            audit_jie_against_reference(
                term="立春", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc("立春", INDEPENDENT_JIE_REFERENCES_V1[0]),
                reference=ref)

    def test_unsupported_precision_rejected(self):
        ref = copy.deepcopy(INDEPENDENT_JIE_REFERENCES_V1[0])
        ref["source_precision"] = "second"
        with self.assertRaisesRegex(ValueError, "not supported"):
            audit_jie_against_reference(
                term="立春", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc("立春", INDEPENDENT_JIE_REFERENCES_V1[0]),
                reference=ref)

    def test_term_mismatch_rejected(self):
        ref = copy.deepcopy(INDEPENDENT_JIE_REFERENCES_V1[0])
        with self.assertRaisesRegex(ValueError, "does not match"):
            audit_jie_against_reference(
                term="惊蛰", gregorian_year=2024,
                provider_moment_utc=provider_jie_utc("立春", INDEPENDENT_JIE_REFERENCES_V1[0]),
                reference=ref)


class CivilTimeAuditTests(unittest.TestCase):
    def test_dst_gap_nonexistent_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1986-05-04T02:30:00+08:00")

    def test_wartime_dst_gap_rejected(self):
        # 1940-05-31 16:00 UTC spring-forward: 1940-06-01 00:00-00:59 never existed.
        with self.assertRaisesRegex(ValueError, "does not exist"):
            audit_birth_instant("1940-06-01T00:30:00+08:00")

    def test_dst_overlap_named_zone_rejected_no_silent_fold(self):
        ambiguous = datetime(1986, 9, 14, 1, 30, tzinfo=CHINA)
        self.assertEqual(
            classify_civil_time(datetime(1986, 9, 14, 1, 30), "Asia/Shanghai"),
            "ambiguous")
        with self.assertRaisesRegex(ValueError, "silent guess"):
            audit_birth_instant(ambiguous)

    def test_dst_overlap_explicit_offsets_distinguished(self):
        first = audit_birth_instant("1986-09-14T01:30:00+09:00")
        second = audit_birth_instant("1986-09-14T01:30:00+08:00")
        self.assertEqual(first["utc_instant"], "1986-09-13T16:30:00+00:00")
        self.assertEqual(second["utc_instant"], "1986-09-13T17:30:00+00:00")
        for result in (first, second):
            self.assertEqual(result["civil_classification"], "ambiguous")
            self.assertEqual(result["offset_disambiguation"], "explicit_offset")

    def test_historical_offset_misuse_rejected(self):
        # 1988-07-01 was in DST (+09:00); a fixed +08:00 claim contradicts tzdb.
        with self.assertRaisesRegex(ValueError, "contradicts tzdb"):
            audit_birth_instant("1988-07-01T12:00:00+08:00")

    def test_historical_dst_correct_offset_accepted(self):
        result = audit_birth_instant("1988-07-01T12:00:00+09:00")
        self.assertEqual(result["utc_instant"], "1988-07-01T03:00:00+00:00")

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
        version = tzdata_version()
        self.assertTrue(version and version != "tzdata-version-unverified")


class LeapCenturyBoundaryTests(unittest.TestCase):
    def test_1900_not_leap_year_rejected(self):
        with self.assertRaises(ValueError):
            calendar("1900-02-29T12:00:00+08:00")

    def test_2000_is_leap_year(self):
        result = calendar("2000-02-29T12:00:00+08:00")
        self.assertEqual(result["month_ganzhi"], "戊寅")

    def test_2100_not_leap_year_rejected(self):
        with self.assertRaises(ValueError):
            calendar("2100-02-29T12:00:00+08:00")

    def test_2100_outside_provider_range(self):
        with self.assertRaisesRegex(ValueError, "1900..2099"):
            calendar("2100-06-01T12:00:00+08:00")

    def test_century_boundary_year_pillar_unchanged(self):
        # Ganzhi year changes at Lichun, not on Jan 1.
        self.assertEqual(
            calendar("1999-12-31T12:00:00+08:00")["year_ganzhi"], "己卯")
        self.assertEqual(
            calendar("2000-01-01T12:00:00+08:00")["year_ganzhi"], "己卯")

    def test_2099_boundary(self):
        result = calendar("2099-06-01T12:00:00+08:00")
        self.assertTrue(result["month_ganzhi"])
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
