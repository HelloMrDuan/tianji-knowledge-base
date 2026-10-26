"""TJ-017.4 sealed end-to-end verification of the composition entry.

Runs only in the assembled offline-acceptance environment (the
sequence stage needs the canonical foundations data, the same
boundary as TJ-014.2 itself). Verifies, for every Golden case, that
the composition entry returns exactly the hand-derived expectations
AND exactly the objects produced by manually chaining the four
reviewed assets -- the composition must add wiring, never drift.
"""
import json
import unittest
from pathlib import Path

from tianji_kb.bazi_dayun_classical import (
    classical_direction,
    sanming_convert_elapsed,
    sanming_convert_measurement,
)
from tianji_kb.bazi_dayun_compose import classical_dayun_timeline
from tianji_kb.bazi_dayun_jie import adjacent_jie_distance
from tianji_kb.bazi_dayun_sequence import candidate_sequence
from tianji_kb.calendar_tz import calendar_for_zone
from tianji_kb.operations.bazi_chart import chart

GOLDEN = json.loads(
    (Path(__file__).parent / 'golden_tj0174_dayun_compose.json')
    .read_text(encoding='utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}

POINT_KEYS = ('start_date', 'end_date', 'handover_datetime')
AGE_KEYS = ('start_age', 'end_age')


def _walk(node, path='$'):
    if isinstance(node, dict):
        for key, value in node.items():
            yield path + '.' + str(key), key, value
            yield from _walk(value, path + '.' + str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _walk(value, '%s[%d]' % (path, i))


class CompositionEndToEndTests(unittest.TestCase):
    def _compose(self, case, **overrides):
        kwargs = dict(
            zone=case['zone'],
            traditional_role=case['traditional_role'],
            periods=case['periods'],
            birth_time_precision=case['birth_time_precision'],
            include_shenfeng=case['include_shenfeng'])
        kwargs.update(overrides)
        return classical_dayun_timeline(case['birth_value'], **kwargs)

    def test_every_golden_case(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = self._compose(case)
                self.assertEqual(out['status'], case['status'])
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])
                self.assertEqual(out['pillars']['year_ganzhi'],
                                 case['pillars'][0])
                self.assertEqual(out['pillars']['month_ganzhi'],
                                 case['pillars'][1])
                self.assertEqual(out['pillars']['day_ganzhi'],
                                 case['pillars'][2])
                self.assertEqual(out['pillars']['hour_ganzhi'],
                                 case['pillars'][3])
                self.assertEqual(out['direction']['direction'],
                                 case['direction'])
                self.assertEqual(out['direction']['counting_target'],
                                 case['counting_target'])
                self.assertEqual(out['counting']['selected_jie']
                                 ['name'], case['jie_name'])
                self.assertEqual(out['counting']['selected_jie']['at'],
                                 case['jie_at'])
                self.assertEqual(out['counting']['elapsed_seconds'],
                                 case['elapsed_seconds'])
                converted = out['sanming_conversion']
                self.assertEqual(converted['duration_interval_days'],
                                 case['duration_interval_days'])
                if case['status'] == 'converted':
                    rows = converted['handover_intervals']
                    for got, want in zip(rows,
                                         case['handover_intervals']):
                        self.assertEqual(got['earliest'],
                                         want['earliest'])
                        self.assertEqual(got['latest'], want['latest'])
                else:
                    self.assertEqual(out['reason'], case['reason'])
                    self.assertIsNone(converted['handover_intervals'])
                # Sequence is the TJ-014.2 result, verbatim.
                direct = candidate_sequence(
                    case['pillars'][1], case['pillars'][2][0],
                    direction=case['direction'],
                    periods=case['periods'])
                self.assertEqual(out['sequence'], direct)
                # Alignment: golden rows + golden start intervals.
                self.assertEqual(len(out['sequence_time_alignment']),
                                 case['periods'])
                for i, (entry, want_row) in enumerate(zip(
                        out['sequence_time_alignment'],
                        case['sequence_rows'])):
                    self.assertEqual(entry['period_index'],
                                     want_row['period_index'])
                    self.assertEqual(entry['candidate_ganzhi'],
                                     want_row['candidate_ganzhi'])
                    self.assertEqual(
                        entry['ten_god_relative_to_natal_day_stem'],
                        want_row['ten_god'])
                    if case['status'] == 'converted':
                        want_h = case['handover_intervals'][i]
                        start = entry['start_interval']
                        self.assertEqual(start['earliest'],
                                         want_h['earliest'])
                        self.assertEqual(start['latest'],
                                         want_h['latest'])
                        self.assertEqual(start['method'],
                                         'sanming_shichen_level')
                        self.assertEqual(start['variant'],
                                         'dayun-conversion-sanming-v1')
                    else:
                        self.assertIsNone(entry['start_interval'])
                        self.assertIn('unresolved',
                                      entry['start_interval_status'])

    def test_composition_equals_manual_chain(self):
        # The composition is wiring only: every embedded block must be
        # the verbatim object of the corresponding reviewed asset.
        for case_id in ('Q1-forward-male-1958',
                        'Q2-backward-female-1949'):
            case = CASES[case_id]
            with self.subTest(case=case_id):
                out = self._compose(case)
                cal = calendar_for_zone(case['birth_value'],
                                        case['zone'])
                direction = classical_direction(
                    cal['year_ganzhi'],
                    traditional_role=case['traditional_role'])
                self.assertEqual(out['direction'], direction)
                measured = adjacent_jie_distance(
                    case['birth_value'], direction['direction'],
                    expected_month_ganzhi=cal['month_ganzhi'])
                converted = sanming_convert_measurement(
                    measured,
                    birth_time_precision=case['birth_time_precision'],
                    periods=case['periods'])
                self.assertEqual(out['sanming_conversion'], converted)

    def test_text_example_doctrine_anchor(self):
        # TJ-017.1 Golden C1 (the Sanming worked example): 63 shichen
        # convert to exactly [630, 630] inclusive -- the conversion
        # stage the composition consumes, unchanged.
        result = sanming_convert_elapsed(63 * 7200)
        self.assertEqual(result['status'], 'converted')
        self.assertEqual(result['duration_interval_days'],
                         {'min_days': 630, 'max_days': 630,
                          'max_inclusive': True})


class ShenfengParallelTests(unittest.TestCase):
    def test_parallel_block_matches_golden(self):
        block = GOLDEN['shenfeng_parallel_case']
        case = CASES[block['case_id']]
        out = classical_dayun_timeline(
            case['birth_value'], zone=case['zone'],
            traditional_role=case['traditional_role'],
            periods=case['periods'],
            birth_time_precision=case['birth_time_precision'],
            include_shenfeng=True)
        sf = out['parallel_variants']['shenfeng_day_level']
        self.assertEqual(sf['status'], 'converted')
        self.assertEqual(sf['method'], 'shenfeng_day_level')
        self.assertEqual(sf['text_result_days'],
                         block['text_result_days'])
        self.assertEqual(sf['duration_interval_days'],
                         block['duration_interval_days'])
        first = sf['first_period_start_interval']
        want = block['first_period_start_interval']
        self.assertEqual(first['earliest'], want['earliest'])
        self.assertEqual(first['latest'], want['latest'])
        self.assertEqual(first['max_inclusive'], want['max_inclusive'])
        self.assertIn('composition_level', first['derivation'])
        # Parallel means parallel: the Sanming chain is untouched by
        # the Shenfeng request and the two intervals stay distinct.
        self.assertEqual(out['sanming_conversion']
                         ['duration_interval_days'],
                         case['duration_interval_days'])
        self.assertNotEqual(sf['duration_interval_days'],
                            case['duration_interval_days'])

    def test_parallel_absent_by_default(self):
        case = CASES['Q1-forward-male-1958']
        out = classical_dayun_timeline(
            case['birth_value'], zone=case['zone'],
            traditional_role=case['traditional_role'], periods=1)
        self.assertEqual(out['parallel_variants'], {})


class OutputContractTests(unittest.TestCase):
    def test_no_point_dates_and_no_age_values_anywhere(self):
        case = CASES['Q1-forward-male-1958']
        out = classical_dayun_timeline(
            case['birth_value'], zone=case['zone'],
            traditional_role=case['traditional_role'], periods=3,
            include_shenfeng=True)
        for path, key, value in _walk(out):
            if key in POINT_KEYS or key in AGE_KEYS:
                self.assertIsNone(
                    value, '%s must stay None, got %r' % (path, value))
            self.assertNotEqual(key, 'age', path)
        # Composition-generated structures carry no such keys at all.
        generated = [out, out['birth'], out['pillars'], out['counting'],
                     out['parallel_variants']['shenfeng_day_level']]
        generated += out['sequence_time_alignment']
        generated += [e['start_interval']
                      for e in out['sequence_time_alignment']]
        for block in generated:
            for forbidden in POINT_KEYS + AGE_KEYS:
                self.assertNotIn(forbidden, block)

    def test_default_chart_carries_no_composition_output(self):
        payload = json.dumps(chart('戊戌', '庚申', '甲子', '甲戌'),
                             ensure_ascii=False)
        self.assertNotIn('dayun-classical-composition-v1', payload)
        self.assertNotIn('sequence_time_alignment', payload)


if __name__ == '__main__':
    unittest.main()
