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

    def test_pairwise_element_root_sites_and_fact_provenance(self):
        # 辰藏戊、乙、癸；丑藏己、癸、辛；子藏癸；酉藏辛。
        # 同字与同五行异字都是位置事实，不是“根力有效”。
        out = chart('戊辰', '癸丑', '甲子', '癸酉', pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth'
                    and p['actor']['stem'] == '戊' and p['target']['stem'] == '癸')
        actor = pair['actor_element_root_candidates']
        resource = pair['resource_element_root_candidates']
        self.assertEqual([(p['pillar'], p['branch'], p['stem'], p['same_stem'])
                          for p in actor], [
                              ('year', '辰', '戊', True),
                              ('month', '丑', '己', False),
                          ])
        self.assertEqual([(p['pillar'], p['branch'], p['stem'], p['same_stem'])
                          for p in resource], [
                              ('year', '辰', '癸', True),
                              ('month', '丑', '癸', True),
                              ('day', '子', '癸', True),
                          ])
        self.assertEqual(pair['root_candidate_comparison']['root_effect_status'],
                         'indeterminate')
        self.assertFalse(pair['root_candidate_comparison']['pairwise_effect_proved_by_root_sites'])
        self.assertFalse(pair['root_candidate_comparison']['root_loss_inferred_from_clash'])
        for site in actor + resource:
            pointer = out
            for token in site['fact_ref'][2:].split('/'):
                pointer = pointer[int(token)] if isinstance(pointer, list) else pointer[token]
            self.assertEqual(pointer['stem'], site['stem'])
            self.assertTrue(site['structural_candidate_only'])
            self.assertEqual(site['root_effect_status'], 'indeterminate')
            for interaction in site['branch_interactions']:
                self.assertIn(site['pillar'], interaction['pillars'])
                self.assertEqual(interaction['effect_status'], 'indeterminate')
                value = out
                for token in interaction['fact_ref'][2:].split('/'):
                    value = value[int(token)] if isinstance(value, list) else value[token]
                self.assertEqual(value['pillars'], interaction['pillars'])
                self.assertIn(interaction['rule_id'], [row['rule_id'] for row in out['trace']])
                self.assertTrue(interaction['evidence_ids'])
                self.assertTrue(all(eid in out['evidence'] for eid in interaction['evidence_ids']))
        self.assertEqual(pair['effect_status'], 'indeterminate')
        self.assertIsNone(pair['effective_interaction'])
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_root_candidate_absence_is_not_root_strength_verdict(self):
        out = chart('戊子', '壬子', '甲子', '壬子', pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth'
                    and p['target']['stem'] == '癸')
        self.assertEqual(pair['actor_element_root_candidates'], [])
        self.assertEqual([site['stem'] for site in pair['resource_element_root_candidates']],
                         ['癸', '癸', '癸', '癸'])
        self.assertEqual(gate['element_root_candidate_summary'], {
            'actor_candidate_observed': False,
            'resource_candidate_observed': True,
            'other_stem_same_element_observed': False,
            'root_branch_interaction_observed': False,
            'actual_root_strength_inferred': False,
            'actual_effect_inferred': False,
        })
        self.assertEqual(pair['actor_strength'], None)
        self.assertEqual(pair['effect_status'], 'indeterminate')

    def test_clashed_root_branch_remains_structurally_present(self):
        out = chart('戊午', '壬子', '甲子', '壬子', pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth'
                    and p['target']['stem'] == '癸')
        actor = pair['actor_element_root_candidates']
        self.assertEqual([(p['pillar'], p['stem'], p['same_stem']) for p in actor],
                         [('year', '己', False)])
        self.assertTrue(any(
            observation['rule_id'] == 'bazi.phase2.branch_six_clashes'
            and 'year' in observation['pillars']
            for observation in actor[0]['branch_interactions']))
        self.assertTrue(gate['element_root_candidate_summary']['root_branch_interaction_observed'])
        self.assertFalse(pair['root_candidate_comparison']['root_loss_inferred_from_clash'])
        self.assertEqual(pair['actual_root_strength_status'], 'indeterminate')
        self.assertIsNone(pair['effective_interaction'])
        self.assertIsNone(gate['effect_gate']['wealth_damages_resource'])

    def test_month_without_resource_has_no_pair_root_summary(self):
        out = chart('戊子', '丙寅', '甲子', '庚子', pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        self.assertEqual(gate['status'], 'outside_month_resource_branch')
        self.assertFalse(any(gate['element_root_candidate_summary'].values()))
        self.assertEqual(gate['relation_candidates'], [])

    def test_reviewed_root_type_examples_keep_source_variant_conflict(self):
        # 任氏 s026: 庚辛逢戌余气，甲乙逢亥寅卯长生禄旺。
        # 戌中辛并不使年干庚自动有“有效根”。
        out = chart('庚戌', '甲寅', '丙午', '戊子',
                    pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(x for x in gate['relation_candidates']
                    if x['actor_category'] == 'visible_wealth'
                    and x['actor']['stem'] == '庚'
                    and x['target']['stem'] == '甲')
        actor = next(x for x in pair['actor_element_root_candidates']
                     if x['branch'] == '戌' and x['stem'] == '辛')
        resource = next(x for x in pair['resource_element_root_candidates']
                        if x['branch'] == '寅' and x['stem'] == '甲')
        self.assertFalse(actor['same_stem'])
        self.assertEqual(actor['reviewed_root_type_examples'], [{
            'kind': 'residual_qi_candidate',
            'source_section_ids': ['bazi.section.s026'],
            'status': 'reviewed_type_example_only',
        }])
        self.assertEqual(actor['principal_qi_review']['status'], 'unreviewed')
        self.assertEqual(actor['residual_type_conflict'], {
            'status': 'unresolved_source_variant',
            'conflict_id': 'bazi.concept.conflict_root_type_readings',
            'competing_section_id': 'bazi.section.s041',
            'source_variant_examples_separated': True,
        })
        self.assertTrue(resource['same_stem'])
        self.assertEqual(resource['reviewed_root_type_examples'], [{
            'kind': 'growth_luwang_example',
            'source_section_ids': ['bazi.section.s026'],
            'status': 'reviewed_type_example_only',
        }])
        self.assertEqual(resource['principal_qi_review']['stem'], '甲')
        self.assertTrue(resource['principal_qi_review']['same_stem'])
        self.assertEqual(pair['reviewed_root_type_comparison'], {
            'actor_reviewed_examples': True,
            'resource_reviewed_examples': True,
            'residual_type_conflict_present': True,
            'unreviewed_principal_qi_sites': True,
            'actor_effective_root_strength': None,
            'resource_effective_root_strength': None,
            'actual_pairwise_effect': None,
        })
        for site in [actor, resource]:
            self.assertIsNone(site['effective_root_strength'])
            self.assertTrue(site['root_type_is_not_root_effect'])
            fact = out
            for token in site['fact_ref'][2:].split('/'):
                fact = fact[int(token)] if isinstance(fact, list) else fact[token]
            self.assertEqual(fact['stem'], site['stem'])
        step = next(s for s in out['trace']
                    if s['rule_id'] == 'bazi.phase2.resource_pattern_candidates')
        sections = {out['evidence'][eid]['section_id'] for eid in step['evidence_ids']}
        self.assertTrue({'bazi.section.s026', 'bazi.section.s027',
                         'bazi.section.s041', 'bazi.section.s057',
                         'bazi.section.s058'} <= sections)
        self.assertEqual(pair['effect_status'], 'indeterminate')
        self.assertIsNone(gate['effect_gate']['wealth_damages_resource'])
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_conflicting_residual_variants_are_both_visible(self):
        # 任氏 s026 给出壬癸逢丑，s041 则列壬癸逢辰；
        # 必须保留两处不同底本段字例，不能默默归并或取票决定。
        out = chart('戊辰', '癸丑', '甲子', '癸酉',
                    pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(p for p in gate['relation_candidates']
                    if p['actor_category'] == 'visible_wealth'
                    and p['actor']['stem'] == '戊' and p['target']['stem'] == '癸')
        roots = pair['resource_element_root_candidates']
        chen = next(x for x in roots if x['branch'] == '辰')
        chou = next(x for x in roots if x['branch'] == '丑')
        self.assertEqual(chen['reviewed_root_type_examples'], [])
        self.assertEqual(chen['alternative_root_type_examples'], [{
            'kind': 'residual_qi_candidate',
            'source_section_ids': ['bazi.section.s041'],
            'variant': 'ren-residual-alternate-text',
            'status': 'alternative_source_example_only',
        }])
        self.assertEqual(chou['reviewed_root_type_examples'][0]['source_section_ids'],
                         ['bazi.section.s026'])
        self.assertEqual(chou['alternative_root_type_examples'], [])
        for root in (chen, chou):
            self.assertEqual(root['residual_type_conflict']['status'],
                             'unresolved_source_variant')
            self.assertTrue(root['residual_type_conflict']['source_variant_examples_separated'])
            self.assertIsNone(root['effective_root_strength'])
        self.assertTrue(pair['reviewed_root_type_comparison']['residual_type_conflict_present'])
        self.assertIsNone(pair['reviewed_root_type_comparison']['actual_pairwise_effect'])
        self.assertFalse(out['interpretation_contract']['ai_may_explain'])

    def test_unreviewed_root_type_does_not_become_negative_proof(self):
        # 戊年财、壬月印、子月藏癸：财无同五行藏气候选，
        # 不是财星实际无力或印必旺的判断。
        out = chart('戊子', '壬子', '甲子', '壬子',
                    pattern_variant=PATTERN_VARIANT)
        gate = out['result']['pattern_candidates']['resource'][
            'yuanhai_resource_competing_context']['elemental_causal_gate']
        pair = next(x for x in gate['relation_candidates']
                    if x['actor_category'] == 'visible_wealth')
        self.assertEqual(pair['actor_element_root_candidates'], [])
        self.assertTrue(all(
            site['root_type_review_status'] == 'not_covered_by_reviewed_examples'
            for site in pair['resource_element_root_candidates']))
        self.assertEqual(pair['reviewed_root_type_comparison'], {
            'actor_reviewed_examples': False,
            'resource_reviewed_examples': False,
            'residual_type_conflict_present': False,
            'unreviewed_principal_qi_sites': False,
            'actor_effective_root_strength': None,
            'resource_effective_root_strength': None,
            'actual_pairwise_effect': None,
        })
        self.assertEqual(pair['actor_strength'], None)
        self.assertEqual(pair['adjudication'], 'indeterminate')

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
