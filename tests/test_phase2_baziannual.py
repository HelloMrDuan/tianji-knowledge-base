"""Real calendar annual references; explicitly not 起运 or 吉凶 forecasts."""
import unittest

from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart

NATAL = ('庚辰', '己丑', '甲子', '庚午')


class AnnualCalendarReferenceTests(unittest.TestCase):
    def test_fixed_midyear_ganzhi_and_daymaster_tengod(self):
        result = chart(*NATAL, annual_reference_years=[2024, 2025, 2026])
        rows = result['result']['annual_reference']['rows']
        self.assertEqual([(r['calendar_year'], r['year_ganzhi_at_reference'], r['relative_ten_god'])
                          for r in rows], [
                              (2024, '甲辰', '比肩'),
                              (2025, '乙巳', '劫财'),
                              (2026, '丙午', '食神'),
                          ])
        self.assertTrue(all(r['reference_datetime'].endswith('07-01T12:00:00+08:00')
                            for r in rows))
        self.assertTrue(all(r['calendar_provider'] == 'lunar-python==1.4.8' for r in rows))
        self.assertTrue(all(not r['jieqi_boundary_of_year_resolved'] and
                            r['annual_natal_interaction_status'] == 'not_evaluated'
                            and r['annual_luck_prediction'] is None for r in rows))
        ref = result['result']['annual_reference']
        self.assertFalse(ref['annual_boundary_calculated'])
        self.assertFalse(ref['dayun_start_age_calculated'])
        self.assertFalse(ref['dayun_direction_calculated'])
        self.assertIsNone(ref['annual_luck_assessment'])
        self.assertTrue(result['research_only'])
        self.assertFalse(result['interpretation_contract']['ai_may_explain'])

    def test_actual_execution_rule_evidence_and_no_implicit_output(self):
        out = chart(*NATAL, annual_reference_years=[2026])
        step = next(s for s in out['trace'] if s['rule_id'] == 'bazi.phase2.annual_reference_facts')
        self.assertEqual(step['output'], out['result']['annual_reference'])
        self.assertEqual(step['inputs']['annual_reference_years'], [2026])
        self.assertTrue(step['evidence_ids'])
        self.assertTrue({'bazi.section.s001', 'bazi.section.s002'} <= {
            out['evidence'][eid]['section_id'] for eid in step['evidence_ids']
        })
        plain = chart(*NATAL)
        self.assertNotIn('annual_reference', plain['result'])
        self.assertNotIn('bazi.phase2.annual_reference_facts',
                         [s['rule_id'] for s in plain['trace']])

    def test_gateway_research_only_manual_and_datetime(self):
        manual = {'year_ganzhi': NATAL[0], 'month_ganzhi': NATAL[1],
                  'day_ganzhi': NATAL[2], 'hour_ganzhi': NATAL[3],
                  'annual_reference_years': [2026, 2027]}
        with self.assertRaisesRegex(ValueError, 'explicit research mode'):
            execute('bazi', manual)
        research = execute('bazi', manual, allow_research=True)
        self.assertEqual(research['mode'], 'research')
        self.assertEqual(research['result']['annual_reference']['rows'][1]['year_ganzhi_at_reference'],
                         '丁未')
        birth = execute('bazi', {
            'value': '2000-01-07T12:00:00+08:00',
            'annual_reference_years': [2024, 2025],
        }, allow_research=True)
        self.assertEqual(birth['input_calendar']['calendar_provider'], 'lunar-python==1.4.8')
        self.assertEqual(len(birth['result']['annual_reference']['rows']), 2)
        self.assertFalse(birth['interpretation_contract']['ai_may_explain'])

    def test_fail_closed_invalid_year_arrays(self):
        for years in ([], [2024] * 2, [2026, 2024], [2024, 2024],
                      [2026, '2027'], [True], [2099, 2100], [1899],
                      list(range(2000, 2021)), '2026', None):
            if years is None:
                continue  # None explicitly means feature not requested
            with self.subTest(years=years), self.assertRaises(ValueError):
                chart(*NATAL, annual_reference_years=years)
        with self.assertRaises(ValueError):
            chart(*NATAL, annual_reference_years=[2024, 2025.0])
        with self.assertRaises(ValueError):
            execute('bazi', {**dict(zip(
                ('year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi'), NATAL)),
                'annual_reference_years': [2026]}, allow_research=False)


if __name__ == '__main__':
    unittest.main()
