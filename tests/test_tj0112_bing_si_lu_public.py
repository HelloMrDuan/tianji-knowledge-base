"""TJ-011.2 F3 implementation: public contracts for lu_visible_support.

Public layer (no sealed snapshot needed): the implementation's
anchor-provenance map in bazi_adjudication (LU_ANCHOR_TYPES) is keyed
exactly by the adjudication register's nine conditions in register
order, with anchor types identical to the register's per condition -
the governance-convention condition (hidden layer, Si instance
fire-morph.wu-geng-in-si-non-veto) is never relabelled original text;
the register's governance flags (form id, pending evidence binding,
research-only, no public/AI enablement, strong-only direction) are
unchanged by the wiring; and the batch Golden is self-consistent -
real birth instants, parity-valid pillars, the adjudication batch's
five design charts carried over with condition tables identical to
the design Golden (the counterexample table as corrected by this
batch's sealed replay, correction registered in both files), failed
sets matching expectations, and the chart-unrealizable
single-failure designs registered with their proofs.

Chart execution against the sealed policy and the production
calendar lives in test_tj0112_bing_si_lu.py (offline acceptance only,
NOT public CI).
"""
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_fire_si_yin_morphology as f34
from tianji_kb.bazi_adjudication import LU_ANCHOR_TYPES
from tianji_kb.foundations import ganzhi_index

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_si_lu.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
DESIGN = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json')
    .read_text('utf-8'))['cases']}
REGISTER_KEYS = [c['key'] for c in f34.FORM_BING_SI['conditions']]


class AnchorProvenanceTests(unittest.TestCase):
    def test_anchor_map_matches_register_exactly(self):
        self.assertEqual(
            LU_ANCHOR_TYPES,
            {c['key']: c['anchor_type']
             for c in f34.FORM_BING_SI['conditions']})

    def test_anchor_map_key_order_is_register_order(self):
        self.assertEqual(list(LU_ANCHOR_TYPES), REGISTER_KEYS)
        self.assertEqual(len(LU_ANCHOR_TYPES), 9)

    def test_governance_convention_never_original_text(self):
        self.assertEqual(LU_ANCHOR_TYPES[
            'hidden_layer_convention_applied'], 'governance_convention')
        original = {k for k, v in LU_ANCHOR_TYPES.items()
                    if v == 'original_text'}
        self.assertEqual(original, {
            'reviewed_lu_command_month',
            'visible_positions_support_only',
            'visible_resource_present', 'visible_peer_present',
            'effective_heavy_day_roots'})
        scope = {k for k, v in LU_ANCHOR_TYPES.items()
                 if v == 'scope_construction'}
        self.assertEqual(scope, {
            'fire_day_master_bing', 'all_visible_have_reviewed_roots',
            'no_unresolved_interactions'})


class RegisterGovernanceTests(unittest.TestCase):
    def test_form_identity_and_binding_unchanged(self):
        form = f34.FORM_BING_SI
        self.assertEqual(form['form_id'],
                         'bing-si-lu-commanding-visible-support-v1')
        self.assertEqual(form['scope_candidate'], 'lu_visible_support')
        self.assertEqual(form['day_master'], '丙')
        self.assertEqual(form['month_branch'], '巳')
        self.assertEqual(form['direction'], 'strong')
        # E0335 (TJ-018.3 batch 2): the form's evidence binding
        # flipped with the sealed registration (identity unchanged).
        self.assertTrue(form['evidence_binding'].startswith(
            'registered_phase1_phase2'))
        self.assertIn('bazi.rule.r032', form['evidence_binding'])
        self.assertIs(form['research_only'], True)
        self.assertIs(form['public_enabled'], False)
        self.assertIs(form['ai_enabled'], False)

    def test_satisfiability_record_points_at_golden_witness(self):
        sat = f34.F3_SATISFIABILITY
        self.assertEqual(sat['scan']['chart_count'], 7512)
        self.assertEqual(sat['scan']['positive_count'], 1)
        case = CASES['tj0112-bingsi-positive']
        self.assertTrue(sat['scan']['witness'].startswith('1927-05-12'))
        self.assertEqual(case['source_birth'],
                         '1927-05-12T12:00:00+08:00')
        self.assertEqual(case['expected_pillars'],
                         ['丁卯', '乙巳', '丙午', '甲午'])


class GoldenConsistencyTests(unittest.TestCase):
    def test_pillars_parity_valid(self):
        for case in GOLDEN['cases']:
            pillars = case['expected_pillars']
            self.assertEqual(len(pillars), 4, case['id'])
            for pillar in pillars:
                self.assertGreaterEqual(ganzhi_index(pillar), 0,
                                        (case['id'], pillar))

    def test_failed_sets_match_condition_tables(self):
        for case in GOLDEN['cases']:
            table = case['expected_conditions']
            self.assertEqual(set(table), set(REGISTER_KEYS),
                             case['id'])
            failed = {k for k, v in table.items() if not v}
            self.assertEqual(
                failed,
                set(case['expect'].get('failed_conditions', [])),
                case['id'])
            if case['expect']['classification'] == 'strong' and \
                    case['expect'].get('sufficient_predicate') == \
                    'lu_visible_support':
                self.assertTrue(all(table.values()), case['id'])

    def test_design_quintet_tables_identical_to_design_golden(self):
        pairs = {
            'tj0112-bingsi-positive':
                'tj0112-f3-positive-scan-witness',
            'tj0112-bingsi-near-miss-unrooted-resource':
                'tj0112-f3-near-miss-unrooted-resource',
            'tj0112-bingsi-abstain-yin-si-harm':
                'tj0112-f3-abstain-yin-si-harm',
            'tj0112-bingsi-conflict-xu-root':
                'tj0112-f3-conflict-xu-root',
            'tj0112-bingsi-counterexample-visible-denial':
                'tj0112-f3-counterexample-visible-denial',
        }
        for impl_id, design_id in pairs.items():
            case, design = CASES[impl_id], DESIGN[design_id]
            self.assertEqual(case['source_birth'],
                             design['source_birth'], impl_id)
            self.assertEqual(case['expected_pillars'],
                             design['expected_pillars'], impl_id)
            self.assertEqual(case['expected_conditions'],
                             design['expected_conditions'], impl_id)

    def test_exactly_one_lu_positive(self):
        positives = [c for c in GOLDEN['cases']
                     if c['expect'].get('sufficient_predicate')
                     == 'lu_visible_support']
        self.assertEqual([c['id'] for c in positives],
                         ['tj0112-bingsi-positive'])

    def test_case_families_cover_the_veto_faces(self):
        categories = {c['category'] for c in GOLDEN['cases']}
        for needed in ('positive_strong', 'near_miss_single_condition',
                       'abstain_unknown', 'conflict_registered',
                       'counterexample', 'wrong_month',
                       'officer_veto', 'output_veto',
                       'not_applicable_ding'):
            self.assertIn(needed, categories)

    def test_unrealizable_designs_registered(self):
        designs = GOLDEN['unrealizable_designs']
        self.assertGreaterEqual(len(designs), 3)
        joined = ' '.join(d['design'] + d['reason'] for d in designs)
        for key in ('visible_peer_present', 'visible_resource_present',
                    'effective_heavy_day_roots'):
            self.assertIn(key, joined)
        for entry in designs:
            self.assertIn('构造性不可实现', entry['reason'])
            self.assertIn('因子层', entry['reason'])


if __name__ == '__main__':
    unittest.main()
