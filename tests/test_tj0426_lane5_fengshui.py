"""TJ-0426 Lane 5 (O-05): Fengshui inference layer — house trigram,
absolute-period assumption gate, flying-star flight arithmetic.

Local tests run WITHOUT data/: house_trigram() takes a mountain
record dict, absolute_period()/flying_star_sequence() are pure. The
data-gated tests (skipUnless the sealed mountain table exists) replay
the 24-mountain regression and check house_trigram() against real
chart() output for all 24 centers.
"""
import unittest
from pathlib import Path

from tianji_kb.operations.fengshui_chart import relative_period
from tianji_kb.operations.fengshui_reading import (
    FENGSHUI_GAPS, FORWARD_FLIGHT, REVERSE_FLIGHT, VARIANT,
    absolute_period, flying_star_sequence, house_trigram,
)

ROOT = Path(__file__).resolve().parents[1]
MOUNTAINS_FILE = ROOT / 'data/canonical/fengshui/twenty_four_mountains_v1.json'
GOLDEN_FILE = ROOT / 'data/canonical/fengshui/phase2_golden.json'
HAS_DATA = MOUNTAINS_FILE.exists() and GOLDEN_FILE.exists()

# Fixture mountain records in the shape mountain_at() returns.
FIXTURE_MOUNTAINS = [
    {'mountain': '子', 'direction': '北', 'element': '水',
     'opposite': {'mountain': '午'}},
    {'mountain': '午', 'direction': '南', 'element': '火',
     'opposite': {'mountain': '子'}},
    {'mountain': '卯', 'direction': '东', 'element': '木',
     'opposite': {'mountain': '酉'}},
    {'mountain': '酉', 'direction': '西', 'element': '金',
     'opposite': {'mountain': '卯'}},
    {'mountain': '乾', 'direction': '西北', 'element': '金',
     'opposite': {'mountain': '巽'}},
]


class FengshuiHouseTrigramTests(unittest.TestCase):
    def test_sitting_mountain_maps_to_house_trigram(self):
        expected = {'子': ('坎', '水'), '午': ('离', '火'), '卯': ('震', '木'),
                    '酉': ('兑', '金'), '乾': ('乾', '金')}
        for record in FIXTURE_MOUNTAINS:
            with self.subTest(mountain=record['mountain']):
                result = house_trigram(record)
                self.assertEqual((result['trigram'], result['trigram_element']),
                                 expected[record['mountain']])
                self.assertEqual(result['mountain'], record['mountain'])
                self.assertEqual(result['opposite_mountain'],
                                 record['opposite']['mountain'])
                self.assertEqual(result['evidence_level'], 'C')
                self.assertTrue(result['research_only'])
                self.assertIsNone(result['verdict'])
                self.assertIsNone(result['determination'])

    def test_house_trigram_refuses_bad_records(self):
        with self.assertRaises(ValueError):
            house_trigram({'mountain': '子', 'direction': '中',
                           'element': '水', 'opposite': {'mountain': '午'}})
        with self.assertRaises(ValueError):
            house_trigram({'mountain': '子', 'direction': '北'})
        with self.assertRaises(ValueError):
            house_trigram('子')


class FengshuiAbsolutePeriodTests(unittest.TestCase):
    def test_1864_anchor_never_stands_as_evidence(self):
        # No research flag, no epoch, no basis: all refused.
        for kwargs in ({}, {'research': True}, {'research': True, 'epoch_year': 1864},
                       {'research': True, 'epoch_year': 1864, 'epoch_basis': ''},
                       {'research': False, 'epoch_year': 1864, 'epoch_basis': 'x'}):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                absolute_period(2024, **kwargs)

    def test_explicit_assumption_is_echoed_unverified(self):
        result = absolute_period(2024, research=True, epoch_year=1864,
                                 epoch_basis='caller assumes 1864 as upper-yuan start')
        self.assertEqual(result['period']['period'], 9)
        self.assertEqual(result['period']['epoch_year'], 1864)
        self.assertEqual(result['period']['epoch_basis'],
                         'caller assumes 1864 as upper-yuan start')
        self.assertFalse(result['period']['epoch_verified'])
        self.assertFalse(result['period']['production_eligible'])
        self.assertTrue(result['research_only'])
        self.assertIsNone(result['determination'])

    def test_relative_period_math_regression(self):
        self.assertEqual(relative_period(2023, 1864)['period'], 8)
        self.assertEqual(relative_period(2024, 1864)['period'], 9)
        self.assertEqual(relative_period(2044, 1864)['yuan'], '上元')
        for year in range(1664, 2200):
            period = relative_period(year, 1864)
            self.assertLessEqual(period['start_year'], year)
            self.assertGreaterEqual(period['end_year'], year)
            self.assertEqual(relative_period(year + 180, 1864)['period'], period['period'])


class FengshuiFlyingStarTests(unittest.TestCase):
    def test_forward_and_reverse_flight_cycles(self):
        self.assertEqual(FORWARD_FLIGHT, (5, 6, 7, 8, 9, 1, 2, 3, 4))
        self.assertEqual(REVERSE_FLIGHT, (5, 4, 3, 2, 1, 9, 8, 7, 6))
        forward = flying_star_sequence(5, direction='forward')
        self.assertEqual(forward['sequence'], [5, 6, 7, 8, 9, 1, 2, 3, 4])
        self.assertEqual(forward['palaces'],
                         ['中', '乾', '兑', '艮', '离', '坎', '坤', '震', '巽'])
        self.assertEqual(forward['rule_status'], 'candidate_pending_source')
        self.assertEqual(forward['evidence_level'], 'D')
        self.assertTrue(forward['research_only'])
        reverse = flying_star_sequence(5, direction='reverse')
        self.assertEqual(reverse['sequence'], [5, 4, 3, 2, 1, 9, 8, 7, 6])
        self.assertEqual(flying_star_sequence(1, direction='forward')['sequence'],
                         [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(flying_star_sequence(9, direction='reverse')['sequence'],
                         [9, 8, 7, 6, 5, 4, 3, 2, 1])

    def test_flight_sequences_are_permutations(self):
        for start in range(1, 10):
            for direction in ('forward', 'reverse'):
                result = flying_star_sequence(start, direction=direction)
                self.assertEqual(sorted(result['sequence']), list(range(1, 10)))
                self.assertEqual(result['sequence'][0], start)
                self.assertEqual(len(result['palaces']), 9)
                self.assertIsNone(result['verdict'])

    def test_flight_inputs_fail_closed(self):
        for bad in (0, 10, '5', 5.0, True, None):
            with self.assertRaises(ValueError):
                flying_star_sequence(bad)
        with self.assertRaises(ValueError):
            flying_star_sequence(5, direction='sideways')

    def test_gaps_carry_evidence_levels(self):
        self.assertEqual(FENGSHUI_GAPS['absolute_epoch']['status'], 'gap')
        self.assertEqual(FENGSHUI_GAPS['house_fate']['status'], 'gap')
        self.assertEqual(FENGSHUI_GAPS['flying_stars']['status'], 'candidate_pending_source')
        for entry in FENGSHUI_GAPS.values():
            self.assertEqual(entry['evidence_level'], 'D')


@unittest.skipUnless(HAS_DATA, 'sealed fengshui tables absent (public checkout)')
class FengshuiMountainRegressionTests(unittest.TestCase):
    def test_twenty_four_mountains_and_house_trigrams(self):
        from tianji_kb.golden import run_cases
        from tianji_kb.operations.fengshui import mountain_at
        from tianji_kb.operations.fengshui_chart import chart
        self.assertEqual(len(run_cases(domain='fengshui')), 4)
        for i in range(24):
            degree = i * 15
            mountain = mountain_at(degree)
            self.assertEqual(mountain_at(degree + 180)['mountain'],
                             mountain['opposite']['mountain'])
            result = house_trigram(mountain)
            charted = chart(degree)['result']
            self.assertEqual(result['mountain'], charted['mountain'])
            self.assertEqual(result['trigram'], charted['trigram'])
            self.assertEqual(result['trigram_element'], charted['trigram_element'])
            self.assertEqual(result['opposite_mountain'], charted['opposite'])


if __name__ == '__main__':
    unittest.main()
