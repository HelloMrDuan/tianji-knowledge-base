"""Elemental-direction candidates stay separate from pairwise effective action."""
import unittest

from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.foundations import CONTROLS, GENERATES, stem_element
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart


class ResourceDirectionGateTests(unittest.TestCase):
    def test_ten_fixed_goldens(self):
        observed = [r for r in run_cases(domain='bazi')
                    if r['id'].startswith('bazi.resource-direction-')]
        self.assertEqual(len(observed), 10)

    def test_pair_provenance_directions_and_ineligible_effect(self):
        rows = [
            ('戊子','壬子','甲子','壬子'),
            ('丙辰','壬子','甲子','壬子'),
            ('辛亥','壬子','甲子','壬子'),
            ('乙酉','壬子','甲子','壬子'),
            ('庚子','壬子','甲子','壬子'),
            ('甲申','壬子','甲子','壬子'),
            ('戊子','壬子','甲子','辛酉'),
            ('戊午','壬子','甲子','壬子'),
            ('戊子','壬子','甲子','庚申'),
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
                    self.assertTrue(pair['structural_presence'])
                    self.assertEqual(pair['effect_status'], 'indeterminate')
                    self.assertEqual(pair['adjudication'], 'indeterminate')
                    self.assertEqual(pair['variant'], PATTERN_VARIANT)
                    self.assertEqual(pair['fact_refs'], [actor['fact_ref'], target['fact_ref']])
                    self.assertTrue(pair['evidence_ids'])
                    self.assertTrue(all(eid in out['evidence'] for eid in pair['evidence_ids']))
                    self.assertEqual(pair['source_refs'], ['bazi.section.s057','bazi.section.s058'])
                    blockers = {b['id']: b for b in pair['effect_blockers']}
                    self.assertTrue({
                        'actor_effective_strength_unresolved',
                        'resource_effective_strength_unresolved',
                        'dated_commander_unresolved',
                        'pairwise_effect_rule_not_reviewed',
                        'school_scope_unresolved',
                    } <= set(blockers))
                    if pair['actor_visibility'] == 'hidden':
                        self.assertIn('hidden_stem_activation_not_proven', blockers)
                    for blocker in blockers.values():
                        for ref in blocker['fact_refs']:
                            pointer = out
                            for token in ref[2:].split('/'):
                                pointer = pointer[int(token)] if isinstance(pointer,list) else pointer[token]
                            self.assertIsNotNone(pointer)
                        for eid in blocker.get('evidence_ids', []):
                            self.assertIn(eid, out['evidence'])
                    self.assertEqual(pair['actor_visibility'],
                                     'visible' if pair['actor_category'].startswith('visible') else 'hidden')
                    for fact_ref in (actor['fact_ref'],target['fact_ref']):
                        value = out
                        for key in fact_ref[2:].split('/'):
                            value = value[int(key)] if isinstance(value,list) else value[key]
                        self.assertIsNotNone(value)
                self.assertIsNone(resource['determination']['pattern'])
                self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_co_presence_does_not_promote_effect_or_pattern(self):
        out=chart('戊子','壬子','甲子','辛酉',pattern_variant=PATTERN_VARIANT)
        resource=out['result']['pattern_candidates']['resource']
        gate=resource['yuanhai_resource_competing_context']['elemental_causal_gate']
        self.assertTrue(gate['relation_summary']['wealth_element_controls_resource'])
        self.assertTrue(gate['relation_summary']['official_element_generates_resource'])
        self.assertTrue(gate['relation_summary']['hidden_official_direction'])
        self.assertEqual(gate['effect_gate']['status'],'indeterminate')
        self.assertEqual(resource['yuanhai_resource_competing_context']['adjudications'],
                         {'wealth_strong_enough_to_damage_resource':'indeterminate',
                          'official_actually_generates_resource':'indeterminate',
                          'many_officials_or_competing_pattern':'indeterminate'})
        self.assertIsNone(resource['determination']['pattern'])

    def test_observed_branch_clash_blocks_actual_effect(self):
        out=chart('戊午','壬子','甲子','壬子',pattern_variant=PATTERN_VARIANT)
        self.assertTrue(out['result']['reviewed_relations']['branch_six_clashes'])
        gate=out['result']['pattern_candidates']['resource']['yuanhai_resource_competing_context']['elemental_causal_gate']
        for pair in gate['relation_candidates']:
            blocks={b['id']:b for b in pair['effect_blockers']}
            self.assertIn('observed_interaction_effect_unresolved',blocks)
            self.assertIn('bazi.phase2.branch_six_clashes',
                          blocks['observed_interaction_effect_unresolved']['rule_ids'])
            self.assertIsNone(pair['effective_interaction'])
            self.assertEqual(pair['effect_status'],'indeterminate')

    def test_wealth_with_killing_does_not_create_official_effect(self):
        out=chart('戊子','壬子','甲子','庚申',pattern_variant=PATTERN_VARIANT)
        gate=out['result']['pattern_candidates']['resource']['yuanhai_resource_competing_context']['elemental_causal_gate']
        self.assertTrue(gate['relation_summary']['killing_element_generates_resource_only'])
        self.assertFalse(gate['relation_summary']['official_element_generates_resource'])
        self.assertIsNone(gate['effect_gate']['killing_equivalent_to_official_in_source'])
        self.assertFalse(any(pair['effect_status'] != 'indeterminate'
                             for pair in gate['relation_candidates']))

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
