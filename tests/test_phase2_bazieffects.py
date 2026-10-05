from pathlib import Path
import unittest
from tianji_kb.bazi_action_conditions import EFFECT_VARIANT
from tianji_kb.bazi_root_conditions import STRENGTH_VARIANT
from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]


class ActionEffectTests(unittest.TestCase):
    def chart(self, *pillars):
        return chart(*pillars, strength_variant=STRENGTH_VARIANT, action_effect_variant=EFFECT_VARIANT)

    def test_four_fixed_goldens_cover_both_contexts_and_unresolved_changes(self):
        self.assertEqual(len([r for r in run_cases(ROOT, 'bazi') if r['id'].startswith('bazi.effects-')]), 4)

    def test_real_pure_support_date_confirms_rooted_visible_support_without_hidden_equivalence(self):
        out = execute('bazi', {'value':'1963-03-22T22:00:00+08:00',
                              'strength_variant':STRENGTH_VARIANT,'action_effect_variant':EFFECT_VARIANT})
        effects = out['result']['action_effects']
        self.assertTrue(effects['pure_support_scope_met'])
        self.assertEqual([r['effective_action'] for r in effects['visible_relations']],
                         ['generates_me','same_element','same_element'])
        self.assertTrue(all(r['eligible_root_positions'] and r['distance_weight'] is None for r in effects['visible_relations']))
        self.assertTrue(all(not r['equivalent_to_visible'] for r in effects['hidden_relations']))
        self.assertTrue(any(r['effective_action'] is None for r in effects['hidden_relations']))
        self.assertEqual(out['result']['strength_assessment']['classification'], 'indeterminate')

    def test_real_isolated_date_requires_no_root_no_support_and_exposed_month_principal(self):
        out = execute('bazi', {'value':'2038-09-14T12:00:00+08:00',
                              'strength_variant':STRENGTH_VARIANT,'action_effect_variant':EFFECT_VARIANT})
        e = out['result']['action_effects']
        self.assertTrue(e['isolated_control_scope_met'])
        self.assertEqual([r['effective_action'] for r in e['visible_relations']], [None,'controls_me',None])
        self.assertFalse(out['result']['root_availability']['root_presence'])
        mixed = self.chart('戊午','辛酉','甲午','壬子')['result']['action_effects']
        self.assertFalse(mixed['isolated_control_scope_met'])
        self.assertFalse(mixed['isolated_control_scope_conditions']['no_support_in_any_position'])

    def test_five_combination_does_not_erase_original_stems_or_assume_transformation(self):
        out = self.chart('癸卯','乙卯','甲子','己巳')
        e=out['result']['action_effects']
        self.assertEqual(e['transformation_status'], 'unresolved')
        self.assertFalse(e['stem_erasure_applied'])
        self.assertEqual([p['stem']['value'] for p in out['result']['pillars']], ['癸','乙','甲','己'])
        self.assertTrue(all(r['effective_action'] is None for r in e['visible_relations']))

    def test_clashed_roots_unrooted_support_and_nonwood_charts_still_abstain(self):
        for ps in [('癸卯','乙卯','甲子','癸酉'), ('壬子','壬子','甲子','壬子'), ('丙午','甲午','丙午','甲午')]:
            e=self.chart(*ps)['result']['action_effects']
            self.assertFalse(e['pure_support_scope_met'])
            self.assertFalse(e['isolated_control_scope_met'])
            self.assertTrue(all(r['effective_action'] is None for r in e['visible_relations']))

    def test_new_quotes_are_exact_and_old_default_does_not_enable_effects(self):
        resolver=EvidenceResolver()
        for n in range(47,51):
            s=resolver.entities[f'bazi.section.s{n:03d}'][1]
            src=resolver.sources[s['source_id']]
            raw=(ROOT/src['content_path']).read_text(encoding='utf-8')
            self.assertEqual(raw.count(s['text']),1)
            self.assertTrue(s['locator'].endswith(str(raw.index(s['text']))))
            self.assertEqual(src['evidence_level'],'C')
        self.assertNotIn('action_effects', chart('癸卯','乙卯','甲子','乙亥')['result'])
        with self.assertRaises(ValueError): chart('癸卯','乙卯','甲子','乙亥',action_effect_variant=EFFECT_VARIANT)


if __name__ == '__main__':
    unittest.main()
