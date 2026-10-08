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

    def test_duplicate_executed_rule_id_is_rejected(self):
        from copy import deepcopy
        from types import SimpleNamespace
        from tianji_kb.bazi_pattern import yuanhai_resource_competing_context

        out = chart('戊午', '壬子', '甲子', '壬子',
                    pattern_variant=PATTERN_VARIANT)
        steps = deepcopy(out['trace'])
        # A duplicate ID must not overwrite its predecessor in the trace map.
        # Even identical copies cannot be accepted as unique executed facts.
        copied = deepcopy(next(row for row in steps
                               if row['rule_id'] == 'bazi.phase2.ten_gods'))
        steps.append(copied)
        with self.assertRaisesRegex(ValueError, 'duplicate executed rule identifiers'):
            yuanhai_resource_competing_context(
                SimpleNamespace(steps=steps, evidence=out['evidence']))

    def test_unverified_interaction_evidence_is_rejected(self):
        from copy import deepcopy
        from types import SimpleNamespace
        from tianji_kb.bazi_pattern import yuanhai_resource_competing_context

        out = chart('戊午', '壬子', '甲子', '壬子',
                    pattern_variant=PATTERN_VARIANT)
        original = deepcopy(out['trace'])
        clash = next(step for step in original
                     if step['rule_id'] == 'bazi.phase2.branch_six_clashes')
        self.assertTrue(clash['output'])
        self.assertTrue(clash['evidence_ids'])

        # An actual clash is present, but its evidence pointer is corrupted.
        # This must raise rather than attach a fictional citation to a blocker.
        clash['evidence_ids'] = ['missing.interaction.evidence']
        with self.assertRaisesRegex(ValueError, 'Resource interaction lacks executed evidence'):
            yuanhai_resource_competing_context(
                SimpleNamespace(steps=original, evidence=out['evidence']))

        # A present interaction with an empty citation set is equally invalid.
        clash['evidence_ids'] = []
        with self.assertRaisesRegex(ValueError, 'Resource interaction lacks executed evidence'):
            yuanhai_resource_competing_context(
                SimpleNamespace(steps=original, evidence=out['evidence']))

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

    def test_exact_stem_sites_trace_without_effect_or_strength(self):
        # Independent expected sites from the four given pillars:
        # 辰藏戊与年干戊相同；丑藏癸与月/时干癸相同。
        out = chart('戊辰', '癸丑', '甲子', '癸酉',
                    pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        self.assertEqual(gate['exact_stem_site_summary'], {
            'visible_actor_with_same_stem_hidden_site': True,
            'month_resource_with_same_stem_visible_site': True,
            'effective_root_inferred': False,
            'numeric_root_weight_applied': False,
        })
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth'
                    and p['actor']['stem'] == '戊'
                    and p['target']['stem'] == '癸')
        self.assertEqual([s['pillar'] for s in pair['actor_exact_stem_sites']['hidden']], ['year'])
        self.assertEqual([s['pillar'] for s in pair['resource_exact_stem_sites']['visible']],
                         ['month', 'hour'])
        self.assertEqual([s['pillar'] for s in pair['resource_exact_stem_sites']['hidden']],
                         ['year', 'month', 'day'])
        for side, expected_stem in [('actor_exact_stem_sites', '戊'),
                                    ('resource_exact_stem_sites', '癸')]:
            for visibility in ('visible', 'hidden'):
                for site in pair[side][visibility]:
                    ref = site['fact_ref']
                    value = out
                    for token in ref[2:].split('/'):
                        value = value[int(token)] if isinstance(value, list) else value[token]
                    self.assertEqual(value['stem'], expected_stem)
        self.assertTrue(pair['same_stem_presence_is_not_effective_root'])
        self.assertEqual(pair['actual_root_strength_status'], 'indeterminate')
        self.assertEqual(pair['effect_status'], 'indeterminate')
        self.assertIsNone(pair['effective_interaction'])
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_no_exact_stem_hidden_root_is_not_a_strength_verdict(self):
        out = chart('戊子', '壬子', '甲子', '壬子',
                    pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth')
        self.assertEqual(pair['actor_exact_stem_sites']['hidden'], [])
        self.assertEqual(pair['resource_exact_stem_sites']['visible'], [])
        self.assertEqual(gate['exact_stem_site_summary'], {
            'visible_actor_with_same_stem_hidden_site': False,
            'month_resource_with_same_stem_visible_site': False,
            'effective_root_inferred': False,
            'numeric_root_weight_applied': False,
        })
        self.assertEqual(pair['actual_root_strength_status'], 'indeterminate')
        self.assertEqual(pair['effect_status'], 'indeterminate')

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
