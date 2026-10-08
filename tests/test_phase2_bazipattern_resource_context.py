"""Yuanhai s057/s058 resource context: presence is not causal adjudication."""
import unittest

from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart


class ResourceCompetitionTests(unittest.TestCase):
    def test_eight_fixed_positive_negative_goldens(self):
        rows = [r for r in run_cases(domain='bazi')
                if r['id'].startswith('bazi.resource-context-')]
        self.assertEqual(len(rows), 8)

    def test_visible_hidden_and_month_scope_are_separate(self):
        rows = [
            (('甲子','壬子','甲子','壬子'), 'no_related_facts_observed'),
            (('戊子','壬子','甲子','壬子'), 'related_facts_observed'),
            (('丙辰','壬子','甲子','壬子'), 'related_facts_observed'),
            (('辛亥','壬子','甲子','壬子'), 'related_facts_observed'),
            (('乙酉','壬子','甲子','壬子'), 'related_facts_observed'),
            (('庚子','壬子','甲子','壬子'), 'related_facts_observed'),
            (('甲申','壬子','甲子','壬子'), 'related_facts_observed'),
            (('戊子','丙寅','甲子','庚子'), 'outside_month_resource_branch'),
        ]
        for pillars,status in rows:
            with self.subTest(pillars=pillars):
                out=chart(*pillars, pattern_variant=PATTERN_VARIANT)
                result=out['result']['pattern_candidates']['resource']
                context=result['yuanhai_resource_competing_context']
                self.assertEqual(context['status'],status)
                self.assertFalse(context['qualified_for_determination'])
                self.assertFalse(context['ai_enabled'])
                self.assertTrue(context['research_only'])
                self.assertIsNone(result['determination']['pattern'])
                self.assertEqual(set(context['adjudications'].values()),{'indeterminate'})
                for positions in context['positions'].values():
                    for position in positions:
                        value=out
                        for token in position['fact_ref'][2:].split('/'):
                            value=value[int(token)] if isinstance(value,list) else value[token]
                        self.assertIsNotNone(value)
                self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_bound_classical_evidence_and_no_default_output(self):
        out=chart('戊子','壬子','甲子','壬子',pattern_variant=PATTERN_VARIANT)
        step=next(s for s in out['trace'] if s['rule_id']=='bazi.phase2.resource_pattern_candidates')
        source_sections={out['evidence'][k]['section_id'] for k in step['evidence_ids']}
        self.assertTrue({'bazi.section.s057','bazi.section.s058'} <= source_sections)
        plain=chart('戊子','壬子','甲子','壬子')
        self.assertNotIn('pattern_candidates',plain['result'])


if __name__=='__main__':
    unittest.main()
