"""Exact provider-second Li Chun boundaries, not annual fortune predictions."""
import unittest
from datetime import datetime, timedelta

from tianji_kb.bazi_annual_reference import annual_lichun_boundaries
from tianji_kb.calendar import calendar
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

NATAL = ('庚辰', '己丑', '甲子', '庚午')


class LiChunBoundaryTests(unittest.TestCase):
    def test_fixed_ganzhi_years_and_exact_boundary_second(self):
        out = chart(*NATAL, annual_boundary_years=[2024, 2025, 2026])
        data = out['result']['annual_li_chun_boundaries']
        rows = data['rows']
        self.assertEqual([
            (x['gregorian_lichun_year'], x['ganzhi_in_interval'],
             x['ten_god_relative_to_natal_day_stem'])
            for x in rows], [
                (2024, '甲辰', '比肩'),
                (2025, '乙巳', '劫财'),
                (2026, '丙午', '食神'),
            ])
        for row in rows:
            start = datetime.fromisoformat(row['start_inclusive'])
            end = datetime.fromisoformat(row['end_exclusive'])
            self.assertEqual(start.utcoffset(), timedelta(hours=8))
            self.assertEqual(start.year, row['gregorian_lichun_year'])
            self.assertEqual(start.month, 2)
            self.assertGreater(end, start)
            self.assertEqual(end.year, row['gregorian_lichun_year'] + 1)
            self.assertEqual(row['ganzhi_at_start'], row['ganzhi_in_interval'])
            self.assertEqual(row['ganzhi_one_second_before_end'], row['ganzhi_in_interval'])
            self.assertEqual(calendar(start - timedelta(seconds=1))['year_ganzhi'],
                             row['ganzhi_one_second_before_start'])
            self.assertEqual(calendar(start)['year_ganzhi'], row['ganzhi_in_interval'])
            self.assertEqual(calendar(end - timedelta(seconds=1))['year_ganzhi'],
                             row['ganzhi_in_interval'])
            self.assertEqual(calendar(end)['year_ganzhi'], row['ganzhi_at_end'])
            self.assertIsNone(row['annual_luck_prediction'])
            self.assertIsNone(row['effective_natal_interaction'])
        for a, b in zip(rows, rows[1:]):
            self.assertEqual(a['end_exclusive'], b['start_inclusive'])
        self.assertTrue(data['annual_boundary_calculated'])
        self.assertFalse(data['astronomical_precision_independently_verified'])
        self.assertFalse(data['dayun_start_age_calculated'])
        self.assertFalse(data['dayun_direction_calculated'])
        self.assertIsNone(data['annual_luck_assessment'])
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_early_february_is_not_calendar_new_year(self):
        out = chart(*NATAL, annual_boundary_years=[2025])
        row = out['result']['annual_li_chun_boundaries']['rows'][0]
        self.assertEqual(row['ganzhi_one_second_before_start'], '甲辰')
        self.assertEqual(row['ganzhi_at_start'], '乙巳')
        # A January civil-calendar timestamp still belongs to the prior
        # 立春-to-立春 interval. This is not a fortune conclusion.
        self.assertEqual(calendar('2025-01-20T12:00:00+08:00')['year_ganzhi'], '甲辰')
        self.assertNotEqual('甲辰', row['ganzhi_in_interval'])

    def test_existing_sample_contract_and_default_chart_unchanged(self):
        plain = chart(*NATAL)
        sampled = chart(*NATAL, annual_reference_years=[2024])
        bounded = chart(*NATAL, annual_boundary_years=[2024])
        self.assertNotIn('annual_li_chun_boundaries', plain['result'])
        self.assertNotIn('annual_li_chun_boundaries', sampled['result'])
        self.assertNotIn('annual_reference', bounded['result'])
        self.assertFalse(sampled['result']['annual_reference']['annual_boundary_calculated'])
        self.assertTrue(bounded['result']['annual_li_chun_boundaries']['annual_boundary_calculated'])
        self.assertEqual(plain['result']['production_scope'],
                         '四柱、日主、十神、藏干结构事实')

    def test_evidence_trace_research_gate_and_datetime_entry(self):
        input_manual = dict(zip(
            ('year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi'), NATAL))
        input_manual['annual_boundary_years'] = [2024, 2025]
        with self.assertRaisesRegex(ValueError, 'explicit research mode'):
            execute('bazi', input_manual)
        result = execute('bazi', input_manual, allow_research=True)
        self.assertEqual(result['mode'], 'research')
        step = next(s for s in result['trace']
                    if s['rule_id'] == 'bazi.phase2.annual_li_chun_boundaries')
        self.assertEqual(step['output'], result['result']['annual_li_chun_boundaries'])
        self.assertEqual(step['inputs']['annual_boundary_years'], [2024, 2025])
        self.assertTrue(step['evidence_ids'])
        self.assertTrue({'bazi.section.s001', 'bazi.section.s024'} <= {
            result['evidence'][eid]['section_id'] for eid in step['evidence_ids']})
        self.assertFalse(result['interpretation_contract']['ai_may_explain'])
        birth = execute('bazi', {
            'value': '2000-01-07T12:00:00+08:00',
            'annual_boundary_years': [2025],
        }, allow_research=True)
        self.assertEqual(len(birth['result']['annual_li_chun_boundaries']['rows']), 1)
        self.assertFalse(birth['interpretation_contract']['ai_may_explain'])

    def test_fail_closed_invalid_years(self):
        for bad in ([], [2025, 2025], [2025, 2024],
                    [2026, '2027'], [True], [1899], [2099], [2026, 2027.0],
                    list(range(2020, 2031)), {'year': 2026}, '2026'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                annual_lichun_boundaries('甲', bad)
        with self.assertRaisesRegex(ValueError, 'explicit research mode'):
            execute('bazi', {'value': '2000-01-07T12:00:00+08:00',
                             'annual_boundary_years': [2026]})
        with self.assertRaisesRegex(ValueError, 'annual_boundary_years'):
            chart(*NATAL, annual_boundary_years=[])


if __name__ == '__main__':
    unittest.main()
