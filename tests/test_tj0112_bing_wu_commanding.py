"""TJ-011.2: Bing x Wu commanding visible-support predicate
(commanding_visible_support, the 4th sufficient predicate of
bazi-strength-adjudication-v1), implementing the adjudicated fire
morphology register bazi_fire_morphology.FORM_BING_WU.

Every chart-level case is a REAL birth datetime executed through the
reviewed calendar path (engine.execute); no pillar is hand-assembled.
Expected conditions per case in tests/golden_tj0112_bing_wu_commanding
.json were derived BY HAND from the nine registered conditions, the
sealed action-effects policy facts (support relations and reviewed
root branches) and the morphology register's root sets -- never copied
from implementation output. The first four cases are the morphology
design batch's own charts; their condition tables must agree with the
design batch's hand-derived tables verbatim.

Covered:
- positive: Wu-month pure visible support -> strong via the registered
  bounded exit (sufficient_rule None, predicate named in code terms,
  pending Phase1 registration disclosed), nine conditions bound to
  executed factor evidence, each carrying its registered anchor_type
  (governance-convention conditions distinguishable from original text);
- the morphology design quartet (counter / abstain / conflict) with the
  design condition tables reproduced exactly;
- visible vetoes: officer (Ren), wealth (Xin, design case), drain
  (Wu-earth x2, Ji visible -- Ji VISIBLE is vetoed, while Ji HIDDEN in
  the positive case is recorded and does not veto: the governance
  convention's boundary, proven in both directions);
- single-condition failure: no visible resource stem;
- non-applicability: Ding day master (whole Ding line blocked by
  conflict) and a Si month (F3 not adjudicated, must not be judged by
  this form or any other);
- factor-layer unit tests for the two chart-unrealizable single
  failures (no-peer, heavy-root-absent), registered in the Golden as
  unrealizable_designs with pigeonhole proofs;
- whole-domain scan: over every chart in this suite plus the wood
  regression set, the commanding predicate fires for exactly the
  positive case and never yields weak;
- regression: the three pre-existing predicates (Mao pure / You
  isolated / Hai generating) keep their verdicts, rule bindings and
  condition values.

Like the other sealed-runtime suites (test_tj0112_wood_hai_*), this
module runs in the offline assembled acceptance, not in public CI.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import public_projection
from tianji_kb.bazi_action_conditions import action_effects
from tianji_kb.bazi_adjudication import (
    ADJUDICATION_VARIANT, COMMANDING_ANCHOR_TYPES)
from tianji_kb.bazi_fire_morphology import FORM_BING_WU
from tianji_kb.bazi_strength_display import (
    PUBLIC_STRENGTH_VARIANTS, get_display_decision)
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_bing_wu_commanding.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
DESIGN = {c['id']: c for c in json.loads(
    (ROOT / 'tests/golden_tj0112_fire_morphology.json').read_text('utf-8'))['cases']}
WOOD = {c['id']: c for c in json.loads(
    (ROOT / 'tests/golden_tj0112_wood_hai.json').read_text('utf-8'))['cases']}

COMMANDING_KEYS = [c['key'] for c in FORM_BING_WU['conditions']]
DESIGN_ID = {
    'tj0112-bingwu-positive': 'tj0112-fire-positive-bing-wu',
    'tj0112-bingwu-counter-visible-wealth': 'tj0112-fire-counter-visible-wealth',
    'tj0112-bingwu-abstain-clashed-root': 'tj0112-fire-abstain-clashed-root',
    'tj0112-bingwu-conflict-xu-root-type': 'tj0112-fire-conflict-xu-root-type',
}


def run_birth(birth):
    out = execute('bazi', {'value': birth,
                           'strength_variant': ADJUDICATION_VARIANT},
                  allow_research=True)
    result = out['result']
    pillars = [p['stem']['value'] + p['branch']['value']
               for p in result['pillars']]
    return out, result, pillars


def run_case(case_id):
    case = CASES[case_id]
    out, result, pillars = run_birth(case['source_birth'])
    return case, out, result, pillars


class CommandingScopeShapeTests(unittest.TestCase):
    def test_scope_keys_match_register_exactly(self):
        _, _, result, _ = run_case('tj0112-bingwu-positive')
        effects = result['action_effects']
        self.assertEqual(
            list(effects['commanding_visible_support_scope_conditions']),
            COMMANDING_KEYS)
        # The pre-existing condition sets keep their exact key shape.
        self.assertEqual(
            set(effects['pure_support_scope_conditions']),
            {'wood_day_master', 'reviewed_same_element_month',
             'all_positions_support_only', 'visible印_present',
             'visible比_present', 'effective_day_roots',
             'all_visible_have_reviewed_roots', 'no_unresolved_interactions'})
        self.assertEqual(
            set(effects['isolated_control_scope_conditions']),
            {'wood_day_master', 'reviewed_control_month',
             'day_has_no_structural_root', 'no_support_in_any_position',
             'visible_earth_metal_only', 'month_principal_exposed_with_root',
             'no_unresolved_interactions'})

    def test_anchor_type_map_matches_register(self):
        self.assertEqual(COMMANDING_ANCHOR_TYPES,
                         {c['key']: c['anchor_type']
                          for c in FORM_BING_WU['conditions']})
        self.assertEqual(
            COMMANDING_ANCHOR_TYPES['hidden_layer_convention_applied'],
            'governance_convention')
        self.assertEqual(
            COMMANDING_ANCHOR_TYPES['visible_positions_support_only'],
            'original_text')

    def test_sealed_policy_not_edited(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertNotIn('火', policy['reviewed_root_branches'])
        self.assertNotIn('土', policy['reviewed_root_branches'])


class BingWuPositiveTests(unittest.TestCase):
    def test_positive_strong_via_bounded_exit(self):
        case, out, result, pillars = run_case('tj0112-bingwu-positive')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(
            effects['commanding_visible_support_scope_conditions'],
            case['expected_conditions'])
        self.assertTrue(effects['commanding_visible_support_scope_met'])
        self.assertTrue(all(
            r['effect_status'] == 'effective_in_reviewed_context'
            for r in effects['visible_relations']))
        self.assertTrue(all(
            r['context'] == 'commanding_visible_support'
            for r in effects['visible_relations']))
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(assessment['decision_status'],
                         'reviewed_sufficient_rule_matched')
        why = assessment['why_not_indeterminate']
        self.assertIsNotNone(why)
        # S5 governance batch: the predicate is registered in the
        # sealed snapshot (bazi.rule.r030), so the verdict is issued
        # through its own registered trace step; no pending-registration
        # disclosure remains.
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_commanding_visible_support')
        self.assertNotIn('sufficient_predicate', why)
        self.assertNotIn('predicate_rule_registration', why)
        self.assertTrue(why['all_required_conditions_verified'])
        trace_rule_ids = [s['rule_id'] for s in out['trace']]
        self.assertIn('bazi.phase2.strength_commanding_visible_support',
                      trace_rule_ids)
        self.assertIn('bazi.phase2.strength_bounded_adjudication',
                      trace_rule_ids)
        # Nine conditions, all met, each bound to executed factor
        # evidence and annotated with its REGISTERED anchor_type.
        self.assertEqual([c['condition'] for c in why['conditions']],
                         COMMANDING_KEYS)
        for cond in why['conditions']:
            self.assertTrue(cond['met'], cond['condition'])
            self.assertEqual(cond['anchor_type'],
                             COMMANDING_ANCHOR_TYPES[cond['condition']])
            self.assertEqual(cond['anchor_registration'],
                             'bazi_fire_morphology.FORM_BING_WU')
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(
                set(cond['evidence_ids']) <= set(out['evidence']))
            self.assertIn('/commanding_visible_support_scope_conditions/',
                          cond['fact_ref'])
        gov = next(c for c in why['conditions']
                   if c['condition'] == 'hidden_layer_convention_applied')
        self.assertEqual(gov['anchor_type'], 'governance_convention')
        # The verdict reports no blockers: the wood-scope availability
        # blockers against form-effective fire roots were reconciled
        # under the register's criterion (see module note), and no
        # other blocker exists on this chart.
        self.assertEqual(assessment['blockers'], [])
        self.assertEqual(assessment['conflict_ids'], [])
        # Research gate stays shut on every axis.
        self.assertTrue(assessment['research_only'])
        self.assertFalse(assessment['public_enabled'])
        self.assertFalse(assessment['ai_enabled'])
        self.assertTrue(any('治理约定' in line
                            for line in assessment['limitations']))
        self.assertTrue(any('午月丙日主分支谓词尚待' in line
                            for line in assessment['limitations']))

    def test_hidden_ji_recorded_not_vetoed(self):
        # Positive chart: Wu branches hide Ji (drain) and Yin hides Wu
        # (drain). Under the governance convention these hidden drains
        # are root facts / records only: the visible-only support
        # condition is met and the verdict is strong. (The converse --
        # Ji VISIBLE vetoing -- is the drain-ji case below.)
        case, out, result, pillars = run_case('tj0112-bingwu-positive')
        hidden = result['action_conditions']['hidden_relations']
        hidden_stems = {r['fact']['stem'] for r in hidden}
        self.assertIn('己', hidden_stems)
        self.assertIn('戊', hidden_stems)
        self.assertEqual(result['strength_assessment']['classification'],
                         'strong')

    def test_display_gate_unchanged(self):
        _, _, result, _ = run_case('tj0112-bingwu-positive')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(PUBLIC_STRENGTH_VARIANTS, frozenset())
        decision = get_display_decision(
            assessment, variant=ADJUDICATION_VARIANT,
            day_master='丙', month_branch='午')
        self.assertFalse(decision['may_display_classification'])
        self.assertIsNone(decision['classification'])
        data = {'evidence': {}, 'rule_matches': [], 'trace': [],
                'chart': {'pillars': result['pillars'],
                          'strength_assessment': copy.deepcopy(assessment)}}
        projected = public_projection.project_execution(data)
        self.assertNotEqual(
            projected['chart']['strength_assessment'].get('classification'),
            'strong')


class BingWuDesignQuartetTests(unittest.TestCase):
    """The morphology design batch's four charts: implementation
    conditions must reproduce the design hand-derived tables verbatim."""

    def check_design_case(self, case_id):
        case, out, result, pillars = run_case(case_id)
        design = DESIGN[DESIGN_ID[case_id]]
        self.assertEqual(pillars, case['expected_pillars'])
        design_table = {row['condition']: row['met']
                        for row in design['condition_table']}
        self.assertEqual(case['expected_conditions'], design_table,
                         case_id + ': batch golden disagrees with design')
        effects = result['action_effects']
        self.assertEqual(
            effects['commanding_visible_support_scope_conditions'],
            design_table, case_id)
        self.assertEqual(
            effects['commanding_visible_support_scope_met'],
            all(design_table.values()), case_id)
        return case, out, result

    def test_counter_visible_wealth(self):
        case, out, result = self.check_design_case(
            'tj0112-bingwu-counter-visible-wealth')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIsNone(assessment['why_not_indeterminate'])

    def test_abstain_clashed_root(self):
        case, out, result = self.check_design_case(
            'tj0112-bingwu-abstain-clashed-root')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        reasons = {b['reason'] for b in assessment['blockers']}
        self.assertIn('interaction_effect_unresolved', reasons)

    def test_conflict_xu_root_type(self):
        case, out, result = self.check_design_case(
            'tj0112-bingwu-conflict-xu-root-type')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIn('bazi.concept.conflict_root_type_readings',
                      assessment['conflict_ids'])
        blocking = [c for c in assessment['conflict_checks']
                    if c['conflict_id']
                    == 'bazi.concept.conflict_root_type_readings']
        self.assertTrue(blocking and all(c['blocking'] for c in blocking))


class BingWuVetoAndFailureTests(unittest.TestCase):
    def check_failed(self, case_id):
        case, out, result, pillars = run_case(case_id)
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(
            effects['commanding_visible_support_scope_conditions'],
            case['expected_conditions'], case_id)
        failed = {k for k, v in case['expected_conditions'].items()
                  if not v}
        self.assertEqual(failed,
                         set(case['expect']['failed_conditions']), case_id)
        self.assertFalse(effects['commanding_visible_support_scope_met'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIsNone(assessment['why_not_indeterminate'])
        return result

    def test_officer_veto(self):
        self.check_failed('tj0112-bingwu-officer-veto')

    def test_drain_pent_veto(self):
        self.check_failed('tj0112-bingwu-drain-pent-veto')

    def test_drain_ji_visible_veto(self):
        # Ji as a VISIBLE stem is a drain and vetoes (governance
        # convention boundary: non-veto applies to the hidden layer
        # only). Contrast with the positive case's hidden Ji.
        self.check_failed('tj0112-bingwu-drain-ji-visible')

    def test_no_resource_single_failure(self):
        result = self.check_failed('tj0112-bingwu-no-resource')
        failed = {k for k, v in
                  result['action_effects']
                  ['commanding_visible_support_scope_conditions'].items()
                  if not v}
        self.assertEqual(failed, {'visible_resource_present'})

    def test_ding_never_commanding(self):
        result = self.check_failed('tj0112-bingwu-ding-not-applicable')
        cond = result['action_effects'][
            'commanding_visible_support_scope_conditions']
        self.assertFalse(cond['fire_day_master_bing'])

    def test_wrong_month_si(self):
        result = self.check_failed('tj0112-bingwu-wrong-month-si')
        cond = result['action_effects'][
            'commanding_visible_support_scope_conditions']
        self.assertFalse(cond['reviewed_same_element_command_month'])


class FactorLayerTests(unittest.TestCase):
    """Factor-level coverage for the two chart-unrealizable single
    failures (see Golden unrealizable_designs). Inputs are synthetic
    factor structures modelled on executed output shapes; this layer is
    labelled factor-level and never presented as a real chart."""

    def _inputs(self):
        pillars = [{'name': n, 'stem': {'value': s}} for n, s in
                   (('year', '甲'), ('month', '丙'), ('day', '丙'),
                    ('hour', '丙'))]
        observed = {
            'day_master': '丙',
            'visible_relations': [
                {'fact': {'pillar': 'year', 'stem': '甲', 'element': '木',
                          'relation': 'generates_me',
                          'root_positions': [
                              {'pillar': 'day', 'branch': '寅',
                               'hidden_stem': '甲', 'same_stem': True}]},
                 'conditions': {}},
                {'fact': {'pillar': 'month', 'stem': '丙', 'element': '火',
                          'relation': 'same_element',
                          'root_positions': [
                              {'pillar': 'month', 'branch': '午',
                               'hidden_stem': '丁', 'same_stem': False}]},
                 'conditions': {}},
                {'fact': {'pillar': 'hour', 'stem': '丙', 'element': '火',
                          'relation': 'same_element',
                          'root_positions': [
                              {'pillar': 'month', 'branch': '午',
                               'hidden_stem': '丁', 'same_stem': False}]},
                 'conditions': {}},
            ],
            'hidden_relations': [
                {'fact': {'pillar': 'month', 'stem': '己', 'element': '土',
                          'relation': 'i_generate'}},
            ],
        }
        principal = {'month_branch': '午', 'status': 'reviewed_relation',
                     'relation': 'same_element',
                     'principal_qi': '丁', 'day_master': '丙'}
        availability = {
            'day_master': '丙', 'root_presence': True,
            'roots': [{'root_index': 0,
                       'root_presence': {'pillar': 'month', 'branch': '午',
                                         'hidden_stem': '丁'},
                       'root_availability': 'unresolved',
                       'type_source_conflict': None,
                       'branch_relations': []}],
        }
        relations = {'stem_five_combinations': [],
                     'branch_six_harmonies': [], 'branch_six_harms': [],
                     'branch_six_clashes': [], 'branch_triple_harmonies': []}
        return pillars, observed, relations, principal, availability

    def _effects(self, observed, principal, availability):
        pillars, _, relations, _, _ = self._inputs()
        return action_effects(pillars, observed=observed,
                              relations=relations, principal=principal,
                              availability=availability)

    def test_factor_baseline_all_true_despite_hidden_drain(self):
        _, observed, _, principal, availability = self._inputs()
        effects = self._effects(observed, principal, availability)
        cond = effects['commanding_visible_support_scope_conditions']
        self.assertTrue(all(cond.values()), cond)
        self.assertTrue(effects['commanding_visible_support_scope_met'])

    def test_factor_no_peer_isolated(self):
        _, observed, _, principal, availability = self._inputs()
        observed = copy.deepcopy(observed)
        for row in observed['visible_relations']:
            row['fact']['relation'] = 'generates_me'
        effects = self._effects(observed, principal, availability)
        cond = effects['commanding_visible_support_scope_conditions']
        self.assertFalse(cond['visible_peer_present'])
        self.assertEqual({k for k, v in cond.items() if not v},
                         {'visible_peer_present'})

    def test_factor_heavy_root_absent_isolated(self):
        _, observed, _, principal, availability = self._inputs()
        availability = copy.deepcopy(availability)
        # Only a light root (Wei, residual qi) remains.
        availability['roots'] = [{'root_index': 0,
                                  'root_presence': {
                                      'pillar': 'day', 'branch': '未',
                                      'hidden_stem': '丁'},
                                  'root_availability': 'unresolved',
                                  'type_source_conflict': None,
                                  'branch_relations': []}]
        effects = self._effects(observed, principal, availability)
        cond = effects['commanding_visible_support_scope_conditions']
        self.assertFalse(cond['effective_heavy_day_roots'])
        self.assertEqual({k for k, v in cond.items() if not v},
                         {'effective_heavy_day_roots'})

    def test_factor_hidden_officer_does_not_veto(self):
        _, observed, _, principal, availability = self._inputs()
        observed = copy.deepcopy(observed)
        observed['hidden_relations'].append(
            {'fact': {'pillar': 'year', 'stem': '壬', 'element': '水',
                      'relation': 'controls_me'}})
        effects = self._effects(observed, principal, availability)
        cond = effects['commanding_visible_support_scope_conditions']
        self.assertTrue(cond['visible_positions_support_only'])
        self.assertTrue(all(cond.values()), cond)


class WholeDomainScanTests(unittest.TestCase):
    def test_commanding_fires_exactly_for_positive_case(self):
        births = [c['source_birth'] for c in CASES.values()]
        births += [c['source_birth'] for c in WOOD.values()]
        fired = []
        for birth in births:
            _, result, _ = run_birth(birth)
            assessment = result['strength_assessment']
            why = assessment['why_not_indeterminate']
            if why and why.get('sufficient_predicate') \
                    == 'commanding_visible_support':
                fired.append(birth)
                # This form never yields weak (register: never_yields).
                self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(fired, [CASES['tj0112-bingwu-positive']
                                 ['source_birth']])


class WoodRegressionTests(unittest.TestCase):
    """The three pre-existing predicates keep their verdicts, rule
    bindings and condition values on their own Golden charts."""

    def check_wood(self, case_id):
        case = WOOD[case_id]
        out = execute('bazi', {'value': case['source_birth'],
                               'strength_variant': ADJUDICATION_VARIANT},
                      allow_research=True)
        result = out['result']
        pillars = [p['stem']['value'] + p['branch']['value']
                   for p in result['pillars']]
        self.assertEqual(pillars, case['expected_pillars'])
        return case, result['strength_assessment']

    def test_mao_pure_regression(self):
        case, assessment = self.check_wood(
            'tj0112-regression-mao-pure-support')
        self.assertEqual(assessment['classification'], 'strong')
        why = assessment['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_pure_support')
        self.assertNotIn('anchor_type', why['conditions'][0])

    def test_you_isolated_regression(self):
        case, assessment = self.check_wood(
            'tj0112-regression-you-isolated-control')
        self.assertEqual(assessment['classification'], 'weak')
        why = assessment['why_not_indeterminate']
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_isolated_control')

    def test_hai_generating_regression(self):
        case, assessment = self.check_wood(
            'tj0112-hai-positive-zhongqi-root')
        self.assertEqual(assessment['classification'], 'strong')
        why = assessment['why_not_indeterminate']
        # S5: the Hai predicate is registered (bazi.rule.r029) and now
        # issues through its own trace step, like pure_support.
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_pure_generating_support')
        self.assertNotIn('sufficient_predicate', why)
        self.assertTrue(all(c['met'] for c in why['conditions']))
        self.assertNotIn('anchor_type', why['conditions'][0])


if __name__ == '__main__':
    unittest.main()
