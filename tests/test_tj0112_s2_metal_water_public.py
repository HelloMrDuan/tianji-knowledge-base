"""TJ-011.2 S2 public checks: the two pure-form registers
(FORM_PURE_SUPPORT_METAL / FORM_PURE_GENERATING_WATER in
bazi_metal_water_roots), the satisfiability registrations, and the
Golden file's self-consistency. Data/import level only -- no sealed
knowledge is needed, so this module also runs in public CI (wired in
validate.yml). The engine-level assertions live in
tests/test_tj0112_s2_metal_water.py (sealed acceptance only).

The Golden pillar sets are checked for stem/branch parity validity
(a fabricated pillar pair would typically violate parity), every case
carries a hand derivation, and the two unrealizable entries must stay
registered with their proof summaries: a positive metal chart and a
positive Ren chart must never be fabricated to fill the gap.
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_metal_water_roots import (
    METAL_YOU_SATISFIABILITY, S2_ANCHOR_TYPES, S2_FORM_REGISTERS,
    S2_LIMITATIONS, WATER_ZI_SATISFIABILITY)

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_s2_metal_water.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'

METAL_KEYS = ['metal_day_master', 'reviewed_same_element_month_you',
              'all_positions_support_only', 'visible印_present',
              'visible比_present', 'effective_day_roots_registered',
              'all_visible_have_registered_roots',
              'no_unresolved_interactions']
WATER_KEYS = ['water_day_master', 'reviewed_same_element_month_zi',
              'all_positions_support_only', 'visible印_present',
              'visible比_present', 'effective_day_roots_registered',
              'all_visible_have_registered_roots',
              'no_unresolved_interactions']


class FormRegisterTests(unittest.TestCase):
    def test_two_forms_registered(self):
        self.assertEqual(set(S2_FORM_REGISTERS),
                         {'pure_support_metal',
                          'pure_generating_support_water'})
        metal = S2_FORM_REGISTERS['pure_support_metal']
        water = S2_FORM_REGISTERS['pure_generating_support_water']
        self.assertEqual(metal['day_masters'], ['庚', '辛'])
        self.assertEqual(metal['month_branch'], '酉')
        self.assertEqual(water['day_masters'], ['壬', '癸'])
        self.assertEqual(water['month_branch'], '子')
        for form in (metal, water):
            self.assertEqual(form['classification_if_matched'], 'strong')
            self.assertEqual(form['never_yields'], ['weak'])
            self.assertEqual(form['status'],
                             'adjudicated_isomorphic_extension')
            self.assertEqual(
                form['definition_anchors']['primary'], ['dt.congwang_def'])

    def test_condition_keys_and_anchor_types(self):
        self.assertEqual(
            [c['key'] for c in
             S2_FORM_REGISTERS['pure_support_metal']['conditions']],
            METAL_KEYS)
        self.assertEqual(
            [c['key'] for c in
             S2_FORM_REGISTERS['pure_generating_support_water']
             ['conditions']],
            WATER_KEYS)
        self.assertEqual(S2_ANCHOR_TYPES, {
            p: {c['key']: c['anchor_type'] for c in f['conditions']}
            for p, f in S2_FORM_REGISTERS.items()})
        # Same key layout as the wood pure scope (isomorphic): the
        # eight keys differ only in the day-master and month keys.
        self.assertEqual(METAL_KEYS[2:], WATER_KEYS[2:])
        self.assertEqual(
            S2_ANCHOR_TYPES['pure_support_metal']
            ['effective_day_roots_registered'], 'original_text')
        self.assertEqual(
            S2_ANCHOR_TYPES['pure_generating_support_water']
            ['reviewed_same_element_month_zi'], 'original_text')

    def test_predicate_name_note_discloses_same_element_month(self):
        # The water form's name follows the tasking (pure_generating
        # type); the register must disclose that the Zi month relation
        # is same_element, never generates_me.
        note = S2_FORM_REGISTERS['pure_generating_support_water'][
            'predicate_name_note']
        self.assertIn('same_element', note)
        self.assertIn('不得以名称暗示月令生', note)

    def test_limitations_registered(self):
        self.assertEqual(len(S2_LIMITATIONS), 3)
        joined = ''.join(S2_LIMITATIONS)
        self.assertIn('不可满足', joined)
        self.assertIn('壬', joined)
        self.assertIn('阻断', joined)


class SatisfiabilityRegisterTests(unittest.TestCase):
    def test_metal_unrealizable_three_channels(self):
        self.assertEqual(METAL_YOU_SATISFIABILITY['status'],
                         'chart_unrealizable')
        channels = METAL_YOU_SATISFIABILITY['proof_channels']
        self.assertEqual(len(channels), 3)
        self.assertIn('藏干层唯一支', channels[0]['channel'])
        self.assertIn('显干干对', channels[1]['channel'])
        self.assertIn('土印显干根位登记缺口', channels[2]['channel'])
        # The scout correction is on record.
        self.assertIn('订正', METAL_YOU_SATISFIABILITY['scout_correction'])

    def test_water_satisfiable_for_gui_only(self):
        self.assertEqual(WATER_ZI_SATISFIABILITY['status'],
                         'satisfiable_for_gui_only')
        witness = WATER_ZI_SATISFIABILITY['witness_gui']
        positive = CASES['tj0112-s2-water-positive-gui']
        self.assertEqual(witness['birth'], positive['source_birth'])
        self.assertEqual(witness['pillars'],
                         positive['expected_pillars'])
        ren = WATER_ZI_SATISFIABILITY['ren_unrealizable']
        self.assertEqual(ren['status'], 'chart_unrealizable')
        self.assertEqual(len(ren['proof_channels']), 2)


class GoldenConsistencyTests(unittest.TestCase):
    def test_cases_are_real_and_derived(self):
        # 7 S2 cases + 4 E0355 earth-consumption cases (executed in
        # test_tj0112_earth_consumption_integration_sealed.py).
        self.assertEqual(len(CASES), 11)
        for case in CASES.values():
            self.assertTrue(case['derivation'])
            self.assertEqual(len(case['expected_pillars']), 4)
            for pillar in case['expected_pillars']:
                stem, branch = pillar[0], pillar[1]
                self.assertIn(stem, GAN)
                self.assertIn(branch, ZHI)
                # Stem/branch parity: an impossible (fabricated)
                # pillar pair fails here.
                self.assertEqual(GAN.index(stem) % 2,
                                 ZHI.index(branch) % 2, pillar)
            table = case['expect']['scope_conditions']
            self.assertTrue(
                set(table) == set(METAL_KEYS) or
                set(table) == set(WATER_KEYS), case['id'])
            self.assertTrue(
                all(isinstance(v, bool) for v in table.values()))

    def test_single_positive_is_the_gui_witness(self):
        positives = [c for c in CASES.values()
                     if c['expect']['classification'] == 'strong']
        self.assertEqual(len(positives), 1)
        positive = positives[0]
        self.assertEqual(positive['id'], 'tj0112-s2-water-positive-gui')
        self.assertEqual(positive['expect']['sufficient_predicate'],
                         'pure_generating_support_water')
        self.assertIsNone(positive['expect']['sufficient_rule'])
        self.assertEqual(positive['expect']
                         ['predicate_rule_registration'],
                         'pending_phase1_rule_registration')
        self.assertTrue(all(
            positive['expect']['scope_conditions'].values()))
        for case in CASES.values():
            if case is not positive:
                self.assertEqual(case['expect']['classification'],
                                 'indeterminate')
                self.assertIsNone(
                    case['expect']['sufficient_predicate'])
                self.assertFalse(all(
                    case['expect']['scope_conditions'].values()))

    def test_unrealizable_entries_registered(self):
        entries = {u['predicate']: u for u in GOLDEN['unrealizable']}
        self.assertEqual(set(entries),
                         {'pure_support_metal',
                          'pure_generating_support_water'})
        self.assertEqual(entries['pure_support_metal']['day_masters'],
                         ['庚', '辛'])
        self.assertEqual(
            entries['pure_generating_support_water']['day_masters'],
            ['壬'])
        for entry in entries.values():
            self.assertEqual(entry['status'], 'chart_unrealizable')
            self.assertTrue(entry['proof_summary'])
            self.assertTrue(entry['register'])


if __name__ == '__main__':
    unittest.main()
