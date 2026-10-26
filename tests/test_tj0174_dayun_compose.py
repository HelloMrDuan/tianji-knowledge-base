"""TJ-017.4 public contracts for the classical Dayun composition entry.

What this suite pins in the public checkout:

- the Golden case records (hand-derived pillars, elapsed counts and
  interval arithmetic) are internally consistent transcriptions;
- the composition's first three stages (reviewed calendar pillars,
  TJ-017.1 classical direction, TJ-015 jie measurement, TJ-017.1
  Sanming conversion) reproduce the Golden stage values exactly --
  these are the very objects the composition entry consumes verbatim;
- the composition entry refuses closed (missing/inferred role, bad
  periods, bad precision, naive or out-of-envelope births, unknown
  zones) before any sequence-stage data access.

The full composition (including the TJ-014.2 sequence stage, whose
ten-god computation needs the assembled canonical foundations) is
verified end-to-end in test_tj0174_dayun_compose_sealed.py under the
offline acceptance partition -- the same partition rule as the other
dayun suites. This file never fabricates a composition result.
"""
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    SHENFENG_CONVERSION_VARIANT,
    classical_direction,
    sanming_convert_measurement,
    shenfeng_convert_days,
)
from tianji_kb.bazi_dayun_compose import (
    COMPOSE_VARIANT,
    LIMITATIONS,
    classical_dayun_timeline,
)
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.bazi_dayun_sequence import VARIANT as SEQUENCE_VARIANT
from tianji_kb.calendar_tz import calendar_for_zone

GOLDEN = json.loads(
    (Path(__file__).parent / 'golden_tj0174_dayun_compose.json')
    .read_text(encoding='utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}


class GoldenTranscriptionTests(unittest.TestCase):
    def test_variant_and_chain_match_module(self):
        self.assertEqual(GOLDEN['variant'], COMPOSE_VARIANT)
        self.assertEqual(GOLDEN['chain'], [
            DIRECTION_VARIANT, 'bazi-dayun-adjacent-jie-research-v1',
            CONVERSION_VARIANT, SEQUENCE_VARIANT])
        self.assertTrue(LIMITATIONS)

    def test_case_records_are_internally_consistent(self):
        arith = GOLDEN['derivation_arithmetic']
        self.assertEqual(arith['shichen_seconds'], 7200)
        self.assertEqual(arith['days_per_shichen'], 10)
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                whole = case['counting']['whole_shichen']
                rem = case['counting']['remainder_seconds']
                self.assertEqual(whole * 7200 + rem,
                                 case['elapsed_seconds'])
                self.assertEqual(case['elapsed_seconds'] // 86400,
                                 case['elapsed_whole_days'])
                if case['status'] == 'converted':
                    expected_min = whole * 10
                    if case['birth_time_precision'] == 'unknown':
                        expected_min -= 10
                    expected_max = whole * 10 + (10 if rem else 0)
                    if case['birth_time_precision'] == 'unknown':
                        expected_max += 10
                    self.assertEqual(
                        case['duration_interval_days']['min_days'],
                        expected_min)
                    self.assertEqual(
                        case['duration_interval_days']['max_days'],
                        expected_max)
                    self.assertEqual(len(case['handover_intervals']),
                                     case['periods'])
                    self.assertEqual(len(case['sequence_rows']),
                                     case['periods'])
                else:
                    self.assertIsNone(case['duration_interval_days'])
                    self.assertIsNone(case['handover_intervals'])
                    self.assertEqual(case['elapsed_seconds'], 0)


class StageValueTests(unittest.TestCase):
    """The composition's first three stages against the Golden records."""

    def _stages(self, case):
        cal = calendar_for_zone(case['birth_value'], case['zone'])
        self.assertEqual(
            [cal['year_ganzhi'], cal['month_ganzhi'], cal['day_ganzhi'],
             cal['hour_ganzhi']], case['pillars'],
            'reviewed calendar path must reproduce the hand-derived '
            'pillars for ' + case['id'])
        direction = classical_direction(
            cal['year_ganzhi'],
            traditional_role=case['traditional_role'])
        self.assertEqual(direction['direction'], case['direction'])
        self.assertEqual(direction['counting_target'],
                         case['counting_target'])
        measured = adjacent_jie_distance(
            case['birth_value'], case['direction'],
            expected_month_ganzhi=case['pillars'][1])
        self.assertEqual(measured['selected_jie']['name'],
                         case['jie_name'])
        self.assertEqual(measured['selected_jie']['at'], case['jie_at'])
        self.assertEqual(measured['elapsed_seconds'],
                         case['elapsed_seconds'])
        self.assertEqual(measured['elapsed_whole_days'],
                         case['elapsed_whole_days'])
        return measured

    def test_quadrant_and_boundary_stage_values(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                measured = self._stages(case)
                converted = sanming_convert_measurement(
                    measured,
                    birth_time_precision=case['birth_time_precision'],
                    periods=case['periods'])
                self.assertEqual(converted['status'], case['status'])
                if case['status'] == 'converted':
                    self.assertEqual(
                        converted['duration_interval_days'],
                        case['duration_interval_days'])
                    rows = converted['handover_intervals']
                    for got, want in zip(rows,
                                         case['handover_intervals']):
                        self.assertEqual(got['period_index'],
                                         want['period_index'])
                        self.assertEqual(got['earliest'],
                                         want['earliest'])
                        self.assertEqual(got['latest'], want['latest'])
                    if case['birth_time_precision'] == 'unknown':
                        self.assertTrue(converted['approximate'])
                        self.assertIn('approximation_basis', converted)
                else:
                    self.assertEqual(converted['reason'],
                                     case['reason'])
                    self.assertIsNone(
                        converted['duration_interval_days'])
                    self.assertIsNone(converted['handover_intervals'])

    def test_shenfeng_parallel_stage_values(self):
        block = GOLDEN['shenfeng_parallel_case']
        case = CASES[block['case_id']]
        result = shenfeng_convert_days(case['elapsed_whole_days'],
                                       direction=case['direction'])
        self.assertEqual(result['variant'],
                         SHENFENG_CONVERSION_VARIANT)
        self.assertEqual(result['status'], 'converted')
        self.assertEqual(result['text_result_days'],
                         block['text_result_days'])
        self.assertEqual(result['duration_interval_days'],
                         block['duration_interval_days'])


class FailClosedTests(unittest.TestCase):
    """Refusals that fire before the sequence stage's data access."""

    BIRTH = '1958-08-15T19:30:00+08:00'

    def test_role_must_be_explicit_and_valid(self):
        for bad in (None, '', 'unknown', 'M', 1):
            with self.subTest(role=bad):
                with self.assertRaises(ValueError):
                    classical_dayun_timeline(
                        self.BIRTH, zone='Asia/Shanghai',
                        traditional_role=bad)

    def test_periods_bounds(self):
        for bad in (0, 13, '3', None):
            with self.subTest(periods=bad):
                with self.assertRaises(ValueError):
                    classical_dayun_timeline(
                        self.BIRTH, zone='Asia/Shanghai',
                        traditional_role='male', periods=bad)

    def test_precision_must_be_a_registered_label(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline(
                self.BIRTH, zone='Asia/Shanghai',
                traditional_role='male', birth_time_precision='minute')

    def test_include_shenfeng_must_be_bool(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline(
                self.BIRTH, zone='Asia/Shanghai',
                traditional_role='male', include_shenfeng='yes')

    def test_naive_birth_rejected(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline(
                '1958-08-15T19:30:00', zone='Asia/Shanghai',
                traditional_role='male')

    def test_unknown_zone_rejected(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline(
                self.BIRTH, zone='Not/AZone', traditional_role='male')

    def test_out_of_envelope_birth_rejected(self):
        with self.assertRaises(ValueError):
            classical_dayun_timeline(
                '1850-08-15T19:30:00+08:00', zone='Asia/Shanghai',
                traditional_role='male')


if __name__ == '__main__':
    unittest.main()
