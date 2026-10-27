"""TJ-011.2 public contracts for the commanding_visible_support
implementation batch (Bing x Wu strong form):

- the implementation's anchor-provenance map is keyed exactly by the
  morphology register's nine conditions, in register order, and the
  governance-convention conditions are the register's own
  (hidden_layer_convention_applied), never relabelled original text;
- the batch Golden's first four cases carry condition tables identical
  to the morphology design batch's hand-derived tables (cross-file
  consistency, pure data);
- every Golden case's expected failed set agrees with its own expected
  condition table, and the chart-unrealizable single-failure designs
  are registered with their reasons.

Chart execution against the sealed policy and the production calendar
lives in test_tj0112_bing_wu_commanding.py (offline acceptance only,
NOT public CI).
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import COMMANDING_ANCHOR_TYPES
from tianji_kb.bazi_fire_morphology import FORM_BING_WU

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_bing_wu_commanding.json').read_text('utf-8'))
DESIGN = json.loads(
    (ROOT / 'tests/golden_tj0112_fire_morphology.json').read_text('utf-8'))
FORM_KEYS = [c['key'] for c in FORM_BING_WU['conditions']]
DESIGN_BY_ID = {c['id']: c for c in DESIGN['cases']}
REF = {
    'tj0112-bingwu-positive': 'tj0112-fire-positive-bing-wu',
    'tj0112-bingwu-counter-visible-wealth':
        'tj0112-fire-counter-visible-wealth',
    'tj0112-bingwu-abstain-clashed-root': 'tj0112-fire-abstain-clashed-root',
    'tj0112-bingwu-conflict-xu-root-type':
        'tj0112-fire-conflict-xu-root-type',
}


class AnchorProvenanceTests(unittest.TestCase):
    def test_anchor_map_matches_register(self):
        self.assertEqual(list(COMMANDING_ANCHOR_TYPES), FORM_KEYS)
        self.assertEqual(
            COMMANDING_ANCHOR_TYPES,
            {c['key']: c['anchor_type'] for c in FORM_BING_WU['conditions']})
        governance = {k for k, v in COMMANDING_ANCHOR_TYPES.items()
                      if v == 'governance_convention'}
        self.assertEqual(governance, {'hidden_layer_convention_applied'})

    def test_predicate_name_is_not_pure_support(self):
        self.assertEqual(FORM_BING_WU['predicate_name_candidate'],
                         'commanding_visible_support')
        self.assertEqual(FORM_BING_WU['classification_if_matched'],
                         'strong')
        self.assertEqual(FORM_BING_WU['never_yields'], ['weak'])


class GoldenConsistencyTests(unittest.TestCase):
    def test_ten_cases_cover_the_four_test_families(self):
        cats = [c['category'] for c in GOLDEN['cases']]
        self.assertEqual(len(GOLDEN['cases']), 10)
        for required in ('positive_strong', 'outside_form_counterexample',
                         'abstain_unknown', 'conflict_presentation',
                         'single_condition_veto',
                         'single_condition_failure', 'other_day_master',
                         'wrong_month'):
            self.assertIn(required, cats)

    def test_design_quartet_tables_identical(self):
        for case_id, design_id in REF.items():
            case = next(c for c in GOLDEN['cases'] if c['id'] == case_id)
            design_table = {row['condition']: row['met']
                            for row in
                            DESIGN_BY_ID[design_id]['condition_table']}
            self.assertEqual(case['expected_conditions'], design_table,
                             case_id)
            self.assertEqual(case['expected_pillars'],
                             DESIGN_BY_ID[design_id]['expected_pillars'])
            self.assertEqual(case['source_birth'],
                             DESIGN_BY_ID[design_id]['source_birth'])

    def test_failed_sets_agree_with_tables(self):
        for case in GOLDEN['cases']:
            table = case['expected_conditions']
            self.assertEqual(set(table), set(FORM_KEYS), case['id'])
            failed = {k for k, v in table.items() if not v}
            if case['category'] == 'positive_strong':
                self.assertEqual(failed, set(), case['id'])
                self.assertEqual(case['expect']['classification'],
                                 'strong', case['id'])
                # S5 governance batch: the commanding predicate is
                # registered in the sealed snapshot (bazi.rule.r030);
                # the design Golden records the registered binding.
                self.assertEqual(
                    case['expect']['sufficient_rule'],
                    'bazi.phase2.strength_commanding_visible_support')
                self.assertEqual(
                    case['expect']['predicate_rule_registration'],
                    'registered_phase1_phase2')
            else:
                self.assertEqual(
                    failed, set(case['expect']['failed_conditions']),
                    case['id'])
                self.assertEqual(case['expect']['classification'],
                                 'indeterminate', case['id'])

    def test_unrealizable_designs_registered(self):
        designs = GOLDEN['unrealizable_designs']
        self.assertEqual(len(designs), 3)
        text = json.dumps(designs, ensure_ascii=False)
        self.assertIn('visible_peer_present', text)
        self.assertIn('effective_heavy_day_roots', text)
        for entry in designs:
            self.assertTrue(entry['reason'])


if __name__ == '__main__':
    unittest.main()
