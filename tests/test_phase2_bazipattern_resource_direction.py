"""Elemental-direction candidates stay separate from pairwise effective action."""
import unittest

from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.foundations import CONTROLS, GENERATES, stem_element
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart


class ResourceDirectionGateTests(unittest.TestCase):
    def test_seven_fixed_goldens(self):
        observed = [r for r in run_cases(domain='bazi')
                    if r['id'].startswith('bazi.resource-direction-')]
        self.assertEqual(len(observed), 7)

    def test_pair_provenance_directions_and_ineligible_effect(self):
        rows = [
            ('戊子','壬子','甲子','壬子'),
            ('丙辰','壬子','甲子','壬子'),
            ('辛亥','壬子','甲子','壬子'),
            ('乙酉','壬子','甲子','壬子'),
            ('庚子','壬子','甲子','壬子'),
            ('甲申','壬子','甲子','壬子'),
        ]
        for pillars in rows:
            with self.subTest(pillars=pillars):
                out = chart(*pillars, pattern_variant=PATTERN_VARIANT)
                resource = out['result']['pattern_candidates']['resource']
                gate = resource['yuanhai_resource_competing_context']['elemental_causal_gate']
                self.assertEqual(gate['status'], 'direction_observed_effect_unresolved')
                self.assertTrue(gate['relation_candidates'])
                self.assertIsNone(gate['effect_gate']['wealth_damages_resource'])
                self.assertFalse(gate['effect_gate']['general_day_master_action_effects_reused'])
                for pair in gate['relation_candidates']:
                    actor = pair['actor']
                    target = pair['target']
                    self.assertEqual(pair['actor_element'], stem_element(actor['stem']))
                    self.assertEqual(pair['target_element'], stem_element(target['stem']))
                    direction = (CONTROLS if pair['actor_category'].endswith('wealth')
                                 else GENERATES)
                    self.assertEqual(direction[pair['actor_element']], pair['target_element'])
                    self.assertEqual(pair['effective_interaction_status'], 'indeterminate')
                    self.assertIsNone(pair['effective_interaction'])
                    self.assertFalse(pair['stem_or_hidden_equivalence_assumed'])
                    self.assertEqual(pair['actor_visibility'],
                                     'visible' if pair['actor_category'].startswith('visible') else 'hidden')
                    for fact_ref in (actor['fact_ref'],target['fact_ref']):
                        value = out
                        for key in fact_ref[2:].split('/'):
                            value = value[int(key)] if isinstance(value,list) else value[key]
                        self.assertIsNotNone(value)
                self.assertIsNone(resource['determination']['pattern'])
                self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_no_resource_and_no_actor_do_not_fake_a_relation(self):
        for pillars,status in [
            (('甲子','壬子','甲子','壬子'),'no_relevant_elemental_pair'),
            (('戊子','丙寅','甲子','庚子'),'outside_month_resource_branch')
        ]:
            out=chart(*pillars,pattern_variant=PATTERN_VARIANT)
            context=out['result']['pattern_candidates']['resource']['yuanhai_resource_competing_context']
            gate=context['elemental_causal_gate']
            self.assertEqual(gate['status'],status)
            self.assertEqual(gate['relation_candidates'],[])
            self.assertFalse(any(gate['relation_summary'].values()))
            self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_source_and_production_gates(self):
        out=chart('辛亥','壬子','甲子','壬子',pattern_variant=PATTERN_VARIANT)
        step=next(s for s in out['trace'] if s['rule_id']=='bazi.phase2.resource_pattern_candidates')
        source_sections={out['evidence'][e]['section_id'] for e in step['evidence_ids']}
        self.assertTrue({'bazi.section.s057','bazi.section.s058'} <= source_sections)
        self.assertTrue(out['research_only'])
        default=chart('辛亥','壬子','甲子','壬子')
        self.assertNotIn('pattern_candidates',default['result'])


if __name__ == '__main__':
    unittest.main()
