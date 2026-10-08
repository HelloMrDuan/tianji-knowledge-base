"""Bounded Yuanhai s059 月令生我 observations and research-gate regression."""
import unittest
from tianji_kb.bazi_pattern import PATTERN_VARIANT, YUANHAI_RESOURCE_MONTHS
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.golden import run_cases

class YuanhaiResourceMonthTests(unittest.TestCase):
    def test_five_positive_five_negative_fixed_golden(self):
        ids=[row['id'] for row in run_cases(domain='bazi')
             if row['id'].startswith('bazi.pattern-resource-month-')]
        self.assertEqual(len(ids), 10)

    def test_all_ten_day_stems_in_source_examples(self):
        # Tests both polarities of every listed source group.
        for stem, months in YUANHAI_RESOURCE_MONTHS.items():
            with self.subTest(stem=stem):
                m=months[0]
                month_ganzhi = ('乙' if m in ('亥','卯','巳','酉','未','丑') else '甲') + m
                valid_day = dict(甲='甲子', 乙='乙丑', 丙='丙寅', 丁='丁卯', 戊='戊辰',
                                 己='己巳', 庚='庚午', 辛='辛未', 壬='壬申', 癸='癸酉')[stem]
                out=chart('甲子', month_ganzhi, valid_day, '丙寅', pattern_variant=PATTERN_VARIANT)
                observation=out['result']['pattern_candidates']['resource']['yuanhai_resource_month_example']
                self.assertEqual(observation['status'], 'reviewed_month_example')
                self.assertFalse(observation['qualified_for_determination'])
                self.assertIsNone(out['result']['pattern_candidates']['resource']['determination']['pattern'])
                self.assertFalse(out['interpretation_contract']['ai_may_explain'])
                for condition in observation['conditions']:
                    self.assertTrue(condition['observed'])
                    pointer=condition['fact_ref']; value=out
                    for token in pointer[2:].split('/'):
                        value=value[int(token)] if isinstance(value,list) else value[token]
                    self.assertIsNotNone(value)

    def test_real_classical_evidence_is_executed(self):
        out=chart('甲子','乙亥','甲子','丙寅',pattern_variant=PATTERN_VARIANT)
        trace=next(s for s in out['trace'] if s['rule_id']=='bazi.phase2.resource_pattern_candidates')
        self.assertTrue(any(out['evidence'][eid]['section_id']=='bazi.section.s059'
                            for eid in trace['evidence_ids']))
        self.assertTrue(out['research_only'])

    def test_default_chart_is_unchanged(self):
        out=chart('甲子','乙亥','甲子','丙寅')
        self.assertNotIn('pattern_candidates',out['result'])

if __name__=='__main__':
    unittest.main()
