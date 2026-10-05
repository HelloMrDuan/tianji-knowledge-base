from pathlib import Path
import unittest
from tianji_kb.bazi_commander import PRINCIPAL_VARIANT
from tianji_kb.bazi_root_conditions import AVAILABILITY_VARIANT, STRENGTH_VARIANT
from tianji_kb.engine import execute
from tianji_kb.golden import run_cases
from tianji_kb.operations.bazi_chart import chart

ROOT = Path(__file__).resolve().parents[1]


class AvailabilityTests(unittest.TestCase):
    def chart(self, *pillars):
        return chart(*pillars, strength_variant=STRENGTH_VARIANT,
                     root_availability_variant=AVAILABILITY_VARIANT)

    def test_seven_fixed_goldens_cover_independent_month_and_root_conditions(self):
        rows = [r for r in run_cases(ROOT, 'bazi') if r['id'].startswith(('bazi.principal-', 'bazi.availability-'))]
        self.assertEqual(len(rows), 7)

    def test_dated_source_conflict_does_not_overwrite_principal_relation(self):
        out = chart('甲子', '丙寅', '甲午', '庚午', month_command_variant=PRINCIPAL_VARIANT)
        self.assertEqual(out['result']['principal_month']['relation'], 'same_element')
        self.assertFalse(out['result']['principal_month']['dated_commander_required'])
        self.assertEqual(out['result']['principal_month']['dated_source_conflicts'], ['bazi.concept.conflict_siling_days'])
        self.assertIsNone(out['result']['month_command_variant']['commander'])
        self.assertIsNone(out['result']['principal_month']['de_ling'])
        self.assertNotIn('strength_assessment', out['result'])

    def test_same_stem_and_different_polarity_roots_have_no_equal_strength_assumption(self):
        out = execute('bazi', {'value': '2043-03-22T22:00:00+08:00',
                              'strength_variant': STRENGTH_VARIANT,
                              'root_availability_variant': AVAILABILITY_VARIANT})
        roots = out['result']['root_availability']['roots']
        self.assertEqual([r['same_stem'] for r in roots], [True, False, True])
        self.assertTrue(all(r['root_availability'] == 'effective' for r in roots))
        self.assertTrue(all(r['effective_strength'] is None and not r['polarity_equivalence_assumed'] for r in roots))
        self.assertEqual(out['result']['strength_assessment']['classification'], 'indeterminate')
        self.assertTrue(out['evidence'])

    def test_clash_and_harmony_keep_structural_roots_and_unresolved_transformation(self):
        for ps in [('甲寅','庚申','甲子','辛酉'), ('癸亥','乙卯','甲戌','乙亥')]:
            rows = self.chart(*ps)['result']['root_availability']['roots']
            affected = [r for r in rows if r['branch_relations']]
            self.assertTrue(affected)
            self.assertTrue(all(r['root_presence']['present_structurally'] for r in affected))
            self.assertTrue(all(r['root_availability'] == 'conditional' and r['root_effect'] is None for r in affected))

    def test_unreviewed_types_and_conflicting_residual_roots_cannot_be_effective(self):
        out = self.chart('甲子','丙寅','甲辰','戊辰')['result']['root_availability']
        self.assertTrue(any(r['type_source_conflict'] for r in out['roots']))
        self.assertTrue(all(r['root_availability'] != 'effective' for r in out['roots'] if r['type_source_conflict']))
        other = self.chart('庚申','辛酉','丙午','庚子')['result']['root_availability']
        self.assertTrue(other['roots'])
        self.assertTrue(all(r['root_availability'] == 'unresolved' for r in other['roots']))

    def test_explicit_school_retains_global_conflict_and_defaults_remain_unchanged(self):
        out = self.chart('癸亥','乙卯','甲子','乙亥')
        self.assertTrue(all('bazi.concept.conflict_three_punishments' in r['reported_school_conflicts']
                            for r in out['result']['root_availability']['roots']))
        self.assertFalse(out['result']['root_availability']['root_erasure_applied'])
        self.assertNotIn('root_availability', chart('癸亥','乙卯','甲子','乙亥')['result'])
        with self.assertRaises(ValueError):
            chart('癸亥','乙卯','甲子','乙亥', root_availability_variant=AVAILABILITY_VARIANT)
        with self.assertRaises(ValueError):
            chart('癸亥','乙卯','甲子','乙亥', month_command_variant='invented-principal')


if __name__ == '__main__':
    unittest.main()
