"""TJ-011.2 F4 implementation: public contracts for the segment-gated
changsheng_visible_support predicate (reading (乙) segment_tightened,
user adjudication 2026-10-28).

Public layer (no sealed snapshot needed): the implementation's
anchor-provenance map in bazi_adjudication (CHANGSHENG_ANCHOR_TYPES)
is keyed exactly by the adjudication register's nine conditions in
register order, with anchor types identical to the register's per
condition - the governance-convention condition (hidden layer, Yin
instance fire-morph.wu-in-yin-non-veto) is never relabelled original
text; the register's governance flags and the implementation gate
record are unchanged by the wiring (the gate record still shows both
readings as registered history; the SELECTION lives in the
implementation, CHANGSHENG_SEGMENT_READING); the satisfiability
record carries the E0262 execution-caliber correction (adjudication
scan preserved verbatim, operative figures corrected to the
production execution surface - see F4_SATISFIABILITY
correction_note); the pilot-claim
validation (_changsheng_pilot_claim) is exercised at factor level
with hand-built pilot blocks - identity pins, provenance agreement
with the live Slice C registration, segment/commander/interval
agreement, forged blocks unverifiable; and the batch Golden is
self-consistent - real birth instants, parity-valid pillars, the
adjudication batch's two design charts carried over with condition
tables identical to the design Golden, failed sets matching
expectations, and the chart-unrealizable single-failure designs
registered with their proofs.

Chart execution against the sealed policy and the production
calendar, the real pilot and the combination function over real
traces live in test_tj0112_bing_yin_changsheng.py (offline
acceptance only, NOT public CI).
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_fire_si_yin_morphology as f34
from tianji_kb.bazi_adjudication import (
    CHANGSHENG_ANCHOR_TYPES, CHANGSHENG_PILOT_VARIANT,
    CHANGSHENG_SEGMENT_READING, CHANGSHENG_SEGMENT_STEM,
    _changsheng_pilot_claim)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.foundations import ganzhi_index

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_yin_changsheng.json')
    .read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
DESIGN = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json')
    .read_text('utf-8'))['cases']}
REGISTER_KEYS = [c['key'] for c in f34.FORM_BING_YIN['conditions']]


def _jie_facts(window):
    return {'provider': dict(GOLDEN['provider']),
            'lichun': dict(window['lichun']),
            'next_jie': dict(window['next_jie'])}


def _real_pilot(case_id):
    case = CASES[case_id]
    return yin_siling_pilot(
        case['source_birth'], version_id=GOLDEN['meta']['pilot_version_id'],
        jie_facts=_jie_facts(GOLDEN['jie_windows'][case['window']]))


class AnchorProvenanceTests(unittest.TestCase):
    def test_anchor_map_matches_register_exactly(self):
        self.assertEqual(
            CHANGSHENG_ANCHOR_TYPES,
            {c['key']: c['anchor_type']
             for c in f34.FORM_BING_YIN['conditions']})

    def test_anchor_map_key_order_is_register_order(self):
        self.assertEqual(list(CHANGSHENG_ANCHOR_TYPES), REGISTER_KEYS)
        self.assertEqual(len(CHANGSHENG_ANCHOR_TYPES), 9)

    def test_governance_convention_never_original_text(self):
        self.assertEqual(CHANGSHENG_ANCHOR_TYPES[
            'hidden_layer_convention_applied'], 'governance_convention')
        original = {k for k, v in CHANGSHENG_ANCHOR_TYPES.items()
                    if v == 'original_text'}
        self.assertEqual(original, {
            'reviewed_generating_changsheng_month',
            'visible_positions_support_only',
            'visible_resource_present', 'visible_peer_present',
            'effective_heavy_day_roots'})
        scope = {k for k, v in CHANGSHENG_ANCHOR_TYPES.items()
                 if v == 'scope_construction'}
        self.assertEqual(scope, {
            'fire_day_master_bing', 'all_visible_have_reviewed_roots',
            'no_unresolved_interactions'})


class RegisterGovernanceTests(unittest.TestCase):
    def test_form_identity_and_binding_unchanged(self):
        form = f34.FORM_BING_YIN
        self.assertEqual(form['form_id'],
                         'bing-yin-changsheng-visible-support-v1')
        self.assertEqual(form['scope_candidate'],
                         'changsheng_visible_support')
        self.assertEqual(form['day_master'], '丙')
        self.assertEqual(form['month_branch'], '寅')
        self.assertEqual(form['direction'], 'strong')
        self.assertEqual(form['evidence_binding'],
                         'pending_phase1_rule_registration')
        self.assertIs(form['research_only'], True)
        self.assertIs(form['public_enabled'], False)
        self.assertIs(form['ai_enabled'], False)

    def test_selected_reading_is_segment_tightened_only(self):
        # The implementation implements exactly the user-selected
        # reading (乙); the register's gate record is history and is
        # NOT edited by this batch (both readings remain registered,
        # neither marked selected there).
        self.assertEqual(CHANGSHENG_SEGMENT_READING, 'segment_tightened')
        self.assertEqual(CHANGSHENG_SEGMENT_STEM, '甲')
        self.assertEqual(CHANGSHENG_PILOT_VARIANT,
                         'bazi-siling-yin-pilot-v1')
        readings = {r['id']: r['status']
                    for r in f34.F4_IMPLEMENTATION_GATE['readings']}
        self.assertEqual(readings, {
            'principal_only': 'registered_not_selected',
            'segment_tightened': 'registered_not_selected'})

    def test_satisfiability_record_corrected_to_execution(self):
        sat = f34.F4_SATISFIABILITY
        # The adjudication scan record is preserved verbatim.
        self.assertEqual(sat['scan']['chart_count'], 7164)
        self.assertEqual(sat['scan']['positive_count'], 39)
        self.assertEqual(sat['scan']['segment_distribution'],
                         {'戊': 12, '丙': 8, '甲': 19})
        # E0262 correction (parent ruling: the production
        # execution surface governs, F3 precedent E0248): the
        # operative satisfiability figures are the execution
        # re-verification; the nine conditions are unchanged.
        ex = sat['execution_reverification']
        self.assertEqual(ex['status'], 'operative_figures')
        self.assertEqual(ex['range'], '1900-2099')
        self.assertEqual(ex['chart_count'], 7142)
        self.assertEqual(ex['positive_count'], 31)
        self.assertEqual(ex['segment_distribution'],
                         {'戊': 10, '丙': 6, '甲': 15})
        self.assertEqual(ex['fired_count'], 15)
        self.assertEqual(ex['fired_segment_distribution'],
                         {'甲': 15})
        self.assertEqual(ex['non_jia_positives_fired'], 0)
        self.assertEqual(ex['execution_errors'], 0)
        note = sat['correction_note']
        for marker in ('39', '2100', '36', '598', '597',
                       'non-executed factor', 'execution figures',
                       'segment_tightened'):
            self.assertIn(marker, note)


class PilotClaimValidationTests(unittest.TestCase):
    """Factor-level: hand-built / real pilot blocks against the claim
    validator. Real-chart combination behaviour is sealed-tested."""

    def test_real_computed_jia_block_verifiable(self):
        pilot = _real_pilot('tj0112-bingyin-positive-jia-segment')
        self.assertEqual(pilot['status'], 'computed')
        claim = _changsheng_pilot_claim(pilot)
        self.assertTrue(claim['verifiable'])
        self.assertEqual(claim['status'], 'computed')
        self.assertEqual(claim['segment_stem'], '甲')
        self.assertEqual(claim['segment_index'], 3)
        self.assertEqual(claim['registered_interval'],
                         '[t0+14*24h, next_jie)')
        self.assertEqual(claim['calculation_convention'],
                         {'id': 'siling-calculation-convention',
                          'version': 'v1'})

    def test_real_computed_wu_block_verifiable_not_jia(self):
        pilot = _real_pilot('tj0112-bingyin-gate-excluded-wu-segment')
        self.assertEqual(pilot['status'], 'computed')
        claim = _changsheng_pilot_claim(pilot)
        self.assertTrue(claim['verifiable'])
        self.assertEqual(claim['segment_stem'], '戊')
        self.assertEqual(claim['segment_index'], 1)

    def test_missing_and_misshapen_blocks_unverifiable(self):
        for block, reason in ((None, 'pilot_result_missing'),
                              ('computed', 'pilot_result_missing'),
                              ({}, 'pilot_variant_mismatch')):
            claim = _changsheng_pilot_claim(block)
            self.assertFalse(claim['verifiable'], block)
            self.assertIsNone(claim['status'])
            self.assertEqual(claim['reason'], reason)

    def test_governance_flags_and_binding_pinned(self):
        pilot = _real_pilot('tj0112-bingyin-positive-jia-segment')
        forged = copy.deepcopy(pilot)
        forged['public_enabled'] = True
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'],
                         'pilot_governance_flags_mismatch')
        forged = copy.deepcopy(pilot)
        forged['evidence_binding'] = 'registered'
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_binding_mismatch')

    def test_forged_provenance_unverifiable(self):
        pilot = _real_pilot('tj0112-bingyin-positive-jia-segment')
        forged = copy.deepcopy(pilot)
        forged['provenance']['version_id'] = 'sanming-t1'
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_provenance_mismatch')
        forged = copy.deepcopy(pilot)
        forged['provenance']['source_section_id'] = 'bazi.section.s999'
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_provenance_mismatch')

    def test_segment_commander_interval_agreement_required(self):
        pilot = _real_pilot('tj0112-bingyin-positive-jia-segment')
        forged = copy.deepcopy(pilot)
        forged['segment']['stem'] = '戊'
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_segment_invalid')
        forged = copy.deepcopy(pilot)
        forged['segment']['index'] = 1
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_segment_mismatch')
        forged = copy.deepcopy(pilot)
        forged['segment']['registered_interval'] = '[t0, t0+7*24h)'
        claim = _changsheng_pilot_claim(forged)
        self.assertFalse(claim['verifiable'])
        self.assertEqual(claim['reason'], 'pilot_segment_mismatch')

    def test_noncomputed_statuses_pass_through_verifiable(self):
        pilot = _real_pilot('tj0112-bingyin-positive-jia-segment')
        for status in ('rejected', 'uncertain', 'not_applicable'):
            block = {k: pilot[k] for k in
                     ('variant', 'research_only', 'public_enabled',
                      'ai_enabled', 'evidence_binding')}
            block['status'] = status
            block['reason'] = 'some_reason'
            block['commander'] = None
            claim = _changsheng_pilot_claim(block)
            self.assertTrue(claim['verifiable'], status)
            self.assertEqual(claim['status'], status)
            self.assertIsNone(claim['segment_stem'])


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
            if case['expect'].get('combined_classification') == 'strong':
                self.assertTrue(all(table.values()), case['id'])
                self.assertEqual(case['expect']['segment'], '甲')

    def test_design_pair_tables_identical_to_design_golden(self):
        pairs = {
            'tj0112-bingyin-positive-jia-segment':
                'tj0112-f4-positive-both-readings',
            'tj0112-bingyin-gate-excluded-wu-segment':
                'tj0112-f4-gate-sensitivity-first-segment',
        }
        for impl_id, design_id in pairs.items():
            case, design = CASES[impl_id], DESIGN[design_id]
            self.assertEqual(case['source_birth'],
                             design['source_birth'], impl_id)
            self.assertEqual(case['expected_pillars'],
                             design['expected_pillars'], impl_id)
            self.assertEqual(case['expected_conditions'],
                             design['expected_conditions'], impl_id)

    def test_case_families_cover_the_gate_and_veto_faces(self):
        categories = {c['category'] for c in GOLDEN['cases']}
        for needed in ('positive_strong', 'gate_excluded_segment'):
            self.assertIn(needed, categories)

    def test_unrealizable_designs_registered(self):
        designs = GOLDEN['unrealizable_designs']
        for entry in designs:
            self.assertIn('构造性不可实现', entry['reason'])
            self.assertIn('因子层', entry['reason'])


if __name__ == '__main__':
    unittest.main()
