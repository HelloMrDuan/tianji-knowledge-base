"""Twelve-Jie replay: real pinned provider, T-1/T/T+1 boundaries, provider identity.

All positive cases use the real lunar-python provider (no mocked term times).
Tamper cases clearly isolate mocked provider returns from the real replay.
A passing replay proves internal consistency of the pinned provider; it is
NOT an independent astronomical certification.
"""
import unittest
from datetime import datetime, timedelta
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch
from zoneinfo import ZoneInfo

from lunar_python import Solar

from tianji_kb.bazi_dayun_jie import JIE_NAMES, adjacent_jie_distance
from tianji_kb.calendar import PROVIDER, calendar
from tianji_kb.calendar_provider_guard import provider_identity

CHINA = ZoneInfo("Asia/Shanghai")

# (jie name, reference y/m/d inside the jie's month, expected new month pillar)
# Ganzhi year 2024 is 甲辰; month stems follow 五虎遁 from 丙寅.
JIE_REPLAY = [
    ("立春", 2024, 2, 10, "丙寅"),
    ("惊蛰", 2024, 3, 10, "丁卯"),
    ("清明", 2024, 4, 10, "戊辰"),
    ("立夏", 2024, 5, 10, "己巳"),
    ("芒种", 2024, 6, 10, "庚午"),
    ("小暑", 2024, 7, 10, "辛未"),
    ("立秋", 2024, 8, 10, "壬申"),
    ("白露", 2024, 9, 10, "癸酉"),
    ("寒露", 2024, 10, 10, "甲戌"),
    ("立冬", 2024, 11, 10, "乙亥"),
    ("大雪", 2024, 12, 10, "丙子"),
    ("小寒", 2025, 1, 10, "丁丑"),
]


def jie_moment(name, year, month, day):
    """Real provider's moment for the named Jie (Asia/Shanghai, whole second)."""
    lunar = Solar.fromYmdHms(year, month, day, 12, 0, 0).getLunar()
    term = lunar.getPrevJie(False)
    if term is None or term.getName() != name:
        raise ValueError("replay setup: provider did not return %s" % name)
    return datetime.strptime(
        term.getSolar().toYmdHms(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=CHINA)


class TwelveJieReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.moments = [(name, jie_moment(name, y, m, d), expected_month)
                       for name, y, m, d, expected_month in JIE_REPLAY]

    def test_all_twelve_jie_present_in_order_no_zhongqi(self):
        names = [name for name, _, _ in self.moments]
        self.assertEqual(names, [row[0] for row in JIE_REPLAY])
        for name in names:
            self.assertIn(name, JIE_NAMES)
        moments = [moment for _, moment, _ in self.moments]
        self.assertEqual(len(set(moments)), 12)
        for earlier, later in zip(moments, moments[1:]):
            self.assertLess(earlier, later)
            self.assertLess(later - earlier, timedelta(days=40))

    def test_each_jie_boundary_seconds(self):
        for name, moment, expected_month in self.moments:
            before = moment - timedelta(seconds=1)
            after = moment + timedelta(seconds=1)
            month_before = calendar(before.isoformat())["month_ganzhi"]
            month_at = calendar(moment.isoformat())["month_ganzhi"]
            month_after = calendar(after.isoformat())["month_ganzhi"]
            self.assertNotEqual(month_before, expected_month,
                                "%s T-1 should be in the previous month" % name)
            self.assertEqual(month_at, expected_month,
                             "%s T should enter the new month" % name)
            self.assertEqual(month_after, expected_month,
                             "%s T+1 should stay in the new month" % name)
            # Mid-month stability: the new month pillar holds well past T.
            self.assertEqual(
                calendar((moment + timedelta(hours=12)).isoformat())["month_ganzhi"],
                expected_month)

    def test_lichun_year_boundary(self):
        name, moment, _ = self.moments[0]
        self.assertEqual(name, "立春")
        self.assertEqual(
            calendar((moment - timedelta(seconds=1)).isoformat())["year_ganzhi"],
            "癸卯")
        self.assertEqual(
            calendar(moment.isoformat())["year_ganzhi"], "甲辰")

    def test_xiaohan_stays_in_ganzhi_year(self):
        # 小寒 is in Gregorian January but the ganzhi year changes at 立春.
        name, moment, _ = self.moments[11]
        self.assertEqual(name, "小寒")
        self.assertEqual(
            calendar(moment.isoformat())["year_ganzhi"], "甲辰")
        self.assertEqual(
            calendar((moment - timedelta(seconds=1)).isoformat())["year_ganzhi"],
            "甲辰")

    def test_provider_identity_verified(self):
        identity = provider_identity()
        self.assertTrue(identity["installed_version_matches_pin"])
        self.assertEqual(identity["installed_version"], "1.4.8")
        self.assertEqual(identity["pinned"], PROVIDER)
        self.assertEqual(
            calendar("2024-05-15T12:00:00+08:00")["calendar_provider"], PROVIDER)

    def test_adjacent_jie_distance_each_jie_month(self):
        for name, moment, expected_month in self.moments:
            birth = (moment + timedelta(hours=12)).isoformat()
            for direction in ("forward", "backward"):
                result = adjacent_jie_distance(
                    birth, direction, expected_month_ganzhi=expected_month)
                self.assertIn(result["previous_jie"]["name"], JIE_NAMES)
                self.assertIn(result["next_jie"]["name"], JIE_NAMES)
                self.assertEqual(result["birth_month_ganzhi"], expected_month)
                self.assertGreaterEqual(result["elapsed_seconds"], 0)
                self.assertFalse(result["astronomical_precision_independently_verified"])
                self.assertFalse(result["historical_timezone_independently_verified"])
                self.assertTrue(result["research_only"])
                self.assertFalse(result["public_enabled"])
                self.assertFalse(result["ai_enabled"])
            # Direction only selects which adjacent Jie; birth facts don't move.
            forward = adjacent_jie_distance(
                birth, "forward", expected_month_ganzhi=expected_month)
            backward = adjacent_jie_distance(
                birth, "backward", expected_month_ganzhi=expected_month)
            self.assertEqual(forward["birth_month_ganzhi"],
                             backward["birth_month_ganzhi"])


class _FakeTerm:
    def __init__(self, name, ymdhms):
        self._name = name
        self._ymdhms = ymdhms

    def getName(self):
        return self._name

    def getSolar(self):
        ymdhms = self._ymdhms

        class _Solar:
            def toYmdHms(self):
                return ymdhms

        return _Solar()


class _FakeLunar:
    def __init__(self, prev, nxt):
        self._prev = prev
        self._next = nxt

    def getPrevJie(self, exact):
        return self._prev

    def getNextJie(self, exact):
        return self._next


def _fake_solar_class(prev_name, next_name,
                      prev_t="2024-05-05 10:00:00", next_t="2024-06-05 10:00:00"):
    prev = _FakeTerm(prev_name, prev_t) if prev_name is not None else None
    nxt = _FakeTerm(next_name, next_t) if next_name is not None else None
    fake_lunar = _FakeLunar(prev, nxt)

    class _FakeSolar:
        @staticmethod
        def fromYmdHms(*args):
            class _WithLunar:
                def getLunar(self):
                    return fake_lunar

            return _WithLunar()

    return _FakeSolar


class ProviderTamperTests(unittest.TestCase):
    BIRTH = "2024-05-15T12:00:00+08:00"
    MONTH = "己巳"

    def _call(self, fake_solar):
        with patch("tianji_kb.bazi_dayun_jie.Solar", fake_solar):
            return adjacent_jie_distance(
                self.BIRTH, "forward", expected_month_ganzhi=self.MONTH)

    def test_zhongqi_instead_of_jie_rejected(self):
        with self.assertRaisesRegex(
                ValueError, "did not return one of the twelve Jie"):
            self._call(_fake_solar_class("雨水", "芒种"))

    def test_missing_previous_jie_rejected(self):
        with self.assertRaisesRegex(
                ValueError, "did not return one of the twelve Jie"):
            self._call(_fake_solar_class(None, "芒种"))

    def test_reversed_jie_order_rejected(self):
        with self.assertRaisesRegex(ValueError, "chronology invalid"):
            self._call(_fake_solar_class(
                "立夏", "芒种",
                prev_t="2024-06-05 10:00:00", next_t="2024-05-05 10:00:00"))

    def test_duplicate_jie_name_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate Jie"):
            self._call(_fake_solar_class("立夏", "立夏"))

    def test_month_boundary_mismatch_rejected(self):
        # Fake prev Jie sits in 辰月 while the birth is in 巳月.
        with self.assertRaisesRegex(
                ValueError, "does not match provider's month-pillar boundary"):
            self._call(_fake_solar_class(
                "立夏", "芒种",
                prev_t="2024-04-20 10:00:00", next_t="2024-05-25 10:00:00"))

    def test_wrong_installed_version_rejected(self):
        with patch("tianji_kb.calendar_provider_guard._installed_version", return_value="1.4.7"):
            with self.assertRaisesRegex(ValueError, "version mismatch"):
                provider_identity()
        with patch("tianji_kb.calendar_provider_guard._installed_version", return_value="1.4.7"):
            with self.assertRaisesRegex(ValueError, "version mismatch"):
                adjacent_jie_distance(
                    self.BIRTH, "forward", expected_month_ganzhi=self.MONTH)

    def test_missing_provider_package_rejected(self):
        with patch("tianji_kb.calendar_provider_guard._installed_version",
                   side_effect=PackageNotFoundError("lunar-python")):
            with self.assertRaisesRegex(ValueError, "not installed"):
                provider_identity()

    def test_research_flags_not_promotable(self):
        result = adjacent_jie_distance(
            self.BIRTH, "forward", expected_month_ganzhi=self.MONTH)
        tampered = dict(result)
        tampered["astronomical_precision_independently_verified"] = True
        # The real result keeps the flags false; a tampered copy proves nothing.
        self.assertFalse(result["astronomical_precision_independently_verified"])
        self.assertFalse(result["historical_timezone_independently_verified"])
        self.assertEqual(result["dayun_conversion_rule_review_status"], "unreviewed")


if __name__ == "__main__":
    unittest.main()
