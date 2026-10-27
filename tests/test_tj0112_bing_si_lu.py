"""TJ-011.2 F3 implementation: Bing x Si lu-month predicate tests.

Offline assembled acceptance only (NOT public CI): these tests execute
real charts against the sealed policy and the production calendar.
Synthetic factor-input tests are labelled factor-level and never
presented as real charts.

Coverage:
- the lu scope's condition keys equal the register's nine conditions
  verbatim (and in register order); the sealed policy is untouched
  (no fire/earth root set appears);
- the exhaustion-unique positive (the adjudication batch's scan
  witness) classifies strong through the lu_visible_support
  predicate: bounded exit bazi.rule.r026, sufficient_rule None,
  pending_phase1_rule_registration disclosed, every adjudication
  condition annotated with its registered anchor_type from
  FORM_BING_SI (governance convention never relabelled), no blockers,
  research gates shut, limitations disclose the pending registration
  and the hidden-layer governance convention;
- the Si hidden Wu (output) / Geng (wealth) are recorded, never
  vetoes (convention instance fire-morph.wu-geng-in-si-non-veto);
- the adjudication batch's five design charts reproduce their
  hand-derived condition tables verbatim (the counterexample table as
  corrected by this batch: the design derivation had missed the
  Bing-Xin stem combination, an executed tracked interaction - see
  the correction notes in both Golden files and the adjudication
  document);
- veto / failure families: visible officer veto, visible output
  veto, rootedness near-miss, Yin-Si harm abstention (interaction
  blocker), Xu-root conflict presented and blocking, wrong month
  (Wu: the lu month condition alone fails and the chart is judged by
  the commanding predicate, never both), Ding day master not
  applicable;
- factor-level coverage for the chart-unrealizable single failures
  registered in the Golden (peer-absent, resource-absent, heavy-root
  position absent);
- the display gate is unchanged (no public strength variant; the
  public projection strips the strong classification);
- regression: across this Golden plus the wood, Bing-Wu, S2 and
  F3/F4 design Golden birth sets, lu_visible_support fires for
  exactly the one witness chart, and the six pre-existing predicates
  keep their verdicts (strong never degrades, weak stays weak).
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import public_projection
from tianji_kb.bazi_action_conditions import action_effects
from tianji_kb.bazi_adjudication import (
    ADJUDICATION_VARIANT, LU_ANCHOR_TYPES)
from tianji_kb.bazi_fire_morphology import FORM_BING_WU
from tianji_kb.bazi_fire_si_yin_morphology import FORM_BING_SI
from tianji_kb.bazi_strength_display import (
    PUBLIC_STRENGTH_VARIANTS, get_display_decision)
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_si_lu.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
DESIGN = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_f34_si_yin.json')
    .read_text('utf-8'))['cases']}
WOOD = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_wood_hai.json').read_text('utf-8'))['cases']}
BINGWU = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_bing_wu_commanding.json')
    .read_text('utf-8'))['cases']}
S2G = {c['id']: c for c in json.loads(
    (ROOT / 'tests' / 'golden_tj0112_s2_metal_water.json')
    .read_text('utf-8'))['cases']}

LU_KEYS = [c['key'] for c in FORM_BING_SI['conditions']]
DESIGN_ID = {
    'tj0112-bingsi-positive': 'tj0112-f3-positive-scan-witness',
    'tj0112-bingsi-near-miss-unrooted-resource':
        'tj0112-f3-near-miss-unrooted-resource',
    'tj0112-bingsi-abstain-yin-si-harm': 'tj0112-f3-abstain-yin-si-harm',
    'tj0112-bingsi-conflict-xu-root': 'tj0112-f3-conflict-xu-root',
    'tj0112-bingsi-counterexample-visible-denial':
        'tj0112-f3-counterexample-visible-denial',
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


class LuScopeShapeTests(unittest.TestCase):
    def test_scope_keys_match_register_exactly(self):
        _, _, result, _ = run_case('tj0112-bingsi-positive')
        effects = result['action_effects']
        self.assertEqual(
            list(effects['lu_visible_support_scope_conditions']),
            LU_KEYS)
        # The pre-existing condition sets keep their exact key shape.
        self.assertEqual(
            set(effects['pure_support_scope_conditions']),
            {'wood_day_master', 'reviewed_same_element_month',
             'all_positions_support_only', 'visible印_present',
             'visible比_present', 'effective_day_roots',
             'all_visible_have_reviewed_roots',
             'no_unresolved_interactions'})
        self.assertEqual(
            set(effects['commanding_visible_support_scope_conditions']),
            {c['key'] for c in FORM_BING_WU['conditions']})

    def test_anchor_type_map_matches_register(self):
        self.assertEqual(LU_ANCHOR_TYPES,
                         {c['key']: c['anchor_type']
                          for c in FORM_BING_SI['conditions']})
        self.assertEqual(LU_ANCHOR_TYPES[
            'hidden_layer_convention_applied'], 'governance_convention')
        self.assertEqual(LU_ANCHOR_TYPES[
            'visible_positions_support_only'], 'original_text')

    def test_sealed_policy_not_edited(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches'],
                         {'木': ['亥', '寅', '卯'], '水': ['亥', '子'],
                          '金': ['酉']})
        self.assertNotIn('火', policy['reviewed_root_branches'])
        self.assertNotIn('土', policy['reviewed_root_branches'])


class BingSiPositiveTests(unittest.TestCase):
    def test_positive_strong_via_bounded_exit(self):
        case, out, result, pillars = run_case('tj0112-bingsi-positive')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(effects['lu_visible_support_scope_conditions'],
                         case['expected_conditions'])
        self.assertTrue(effects['lu_visible_support_scope_met'])
        self.assertTrue(all(
            r['effect_status'] == 'effective_in_reviewed_context'
            for r in effects['visible_relations']))
        self.assertTrue(all(
            r['context'] == 'lu_visible_support'
            for r in effects['visible_relations']))
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(assessment['decision_status'],
                         'reviewed_sufficient_rule_matched')
        why = assessment['why_not_indeterminate']
        self.assertIsNotNone(why)
        # Registered bounded exit, exactly like the commanding and
        # Hai predicates: no rule ID is claimed or borrowed, the
        # pending registration is disclosed on the verdict itself.
        self.assertIsNone(why['sufficient_rule'])
        self.assertEqual(why['sufficient_predicate'],
                         'lu_visible_support')
        self.assertEqual(why['predicate_rule_registration'],
                         'pending_phase1_rule_registration')
        self.assertTrue(why['all_required_conditions_verified'])
        trace_rule_ids = [s['rule_id'] for s in out['trace']]
        self.assertNotIn('bazi.phase2.strength_lu_visible_support',
                         trace_rule_ids)
        self.assertIn('bazi.phase2.strength_bounded_adjudication',
                      trace_rule_ids)
        # Nine conditions, all met, each bound to executed factor
        # evidence and annotated with its REGISTERED anchor_type.
        self.assertEqual([c['condition'] for c in why['conditions']],
                         LU_KEYS)
        for cond in why['conditions']:
            self.assertTrue(cond['met'], cond['condition'])
            self.assertEqual(cond['anchor_type'],
                             LU_ANCHOR_TYPES[cond['condition']])
            self.assertEqual(cond['anchor_registration'],
                             'bazi_fire_si_yin_morphology.FORM_BING_SI')
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(
                set(cond['evidence_ids']) <= set(out['evidence']))
            self.assertIn('/lu_visible_support_scope_conditions/',
                          cond['fact_ref'])
        gov = next(c for c in why['conditions']
                   if c['condition']
                   == 'hidden_layer_convention_applied')
        self.assertEqual(gov['anchor_type'], 'governance_convention')
        # No blockers: the wood-scope availability blockers against
        # form-effective fire roots were reconciled under the
        # register's criterion (see adjudication module note).
        self.assertEqual(assessment['blockers'], [])
        self.assertEqual(assessment['conflict_ids'], [])
        # Research gate stays shut on every axis.
        self.assertTrue(assessment['research_only'])
        self.assertFalse(assessment['public_enabled'])
        self.assertFalse(assessment['ai_enabled'])
        self.assertTrue(any('治理约定' in line
                            for line in assessment['limitations']))
        self.assertTrue(any('巳月丙日主分支谓词尚待' in line
                            for line in assessment['limitations']))

    def test_hidden_wu_geng_recorded_not_vetoed(self):
        # The Si month branch hides Wu (output) and Geng (wealth).
        # Under the registered convention instance
        # fire-morph.wu-geng-in-si-non-veto these hidden stems are
        # root facts / records only: the visible-only support
        # condition is met and the verdict is strong. (Visible Wu/Geng
        # would veto - see the veto families below.)
        case, out, result, pillars = run_case('tj0112-bingsi-positive')
        hidden = result['action_conditions']['hidden_relations']
        hidden_stems = {r['fact']['stem'] for r in hidden}
        self.assertIn('戊', hidden_stems)
        self.assertIn('庚', hidden_stems)
        self.assertEqual(result['strength_assessment']['classification'],
                         'strong')
        for row in result['action_effects']['hidden_relations']:
            self.assertNotEqual(row['effect_status'],
                                'effective_in_reviewed_context')
            self.assertIsNone(row['effective_action'])

    def test_display_gate_unchanged(self):
        _, _, result, _ = run_case('tj0112-bingsi-positive')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(PUBLIC_STRENGTH_VARIANTS, frozenset())
        decision = get_display_decision(
            assessment, variant=ADJUDICATION_VARIANT,
            day_master='丙', month_branch='巳')
        self.assertFalse(decision['may_display_classification'])
        self.assertIsNone(decision['classification'])
        data = {'evidence': {}, 'rule_matches': [], 'trace': [],
                'chart': {'pillars': result['pillars'],
                          'strength_assessment':
                              copy.deepcopy(assessment)}}
        projected = public_projection.project_execution(data)
        self.assertNotEqual(
            projected['chart']['strength_assessment']
            .get('classification'), 'strong')


class BingSiDesignQuintetTests(unittest.TestCase):
    """The adjudication batch's five design charts: executed lu
    condition tables must reproduce the design Golden tables verbatim
    (counterexample as corrected by this batch, in both files)."""

    def check_design_case(self, case_id):
        case, out, result, pillars = run_case(case_id)
        design = DESIGN[DESIGN_ID[case_id]]
        self.assertEqual(pillars, case['expected_pillars'])
        self.assertEqual(case['expected_conditions'],
                         design['expected_conditions'],
                         case_id + ': batch golden disagrees with design')
        effects = result['action_effects']
        self.assertEqual(effects['lu_visible_support_scope_conditions'],
                         design['expected_conditions'], case_id)
        self.assertEqual(effects['lu_visible_support_scope_met'],
                         all(design['expected_conditions'].values()),
                         case_id)
        return case, out, result

    def test_positive_is_the_witness(self):
        self.check_design_case('tj0112-bingsi-positive')

    def test_near_miss_rootedness(self):
        case, out, result = self.check_design_case(
            'tj0112-bingsi-near-miss-unrooted-resource')
        self.assertEqual(result['strength_assessment']
                         ['classification'], 'indeterminate')

    def test_abstain_yin_si_harm(self):
        case, out, result = self.check_design_case(
            'tj0112-bingsi-abstain-yin-si-harm')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        reasons = {b['reason'] for b in assessment['blockers']}
        self.assertIn('interaction_effect_unresolved', reasons)

    def test_conflict_xu_root(self):
        case, out, result = self.check_design_case(
            'tj0112-bingsi-conflict-xu-root')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIn('bazi.concept.conflict_root_type_readings',
                      assessment['conflict_ids'])
        blocking = [c for c in assessment['conflict_checks']
                    if c['conflict_id']
                    == 'bazi.concept.conflict_root_type_readings']
        self.assertTrue(blocking
                        and all(c['blocking'] for c in blocking))

    def test_counterexample_visible_denial(self):
        case, out, result = self.check_design_case(
            'tj0112-bingsi-counterexample-visible-denial')
        self.assertEqual(result['strength_assessment']
                         ['classification'], 'indeterminate')


class BingSiVetoAndFailureTests(unittest.TestCase):
    def check_failed(self, case_id):
        case, out, result, pillars = run_case(case_id)
        self.assertEqual(pillars, case['expected_pillars'], case_id)
        effects = result['action_effects']
        self.assertEqual(effects['lu_visible_support_scope_conditions'],
                         case['expected_conditions'], case_id)
        failed = {k for k, v in case['expected_conditions'].items()
                  if not v}
        self.assertEqual(failed,
                         set(case['expect']['failed_conditions']), case_id)
        self.assertFalse(effects['lu_visible_support_scope_met'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'],
                         case['expect']['classification'], case_id)
        return result

    def test_officer_veto(self):
        result = self.check_failed('tj0112-bingsi-officer-veto')
        cond = result['action_effects'][
            'lu_visible_support_scope_conditions']
        self.assertFalse(cond['visible_positions_support_only'])
        self.assertTrue(cond['visible_resource_present'])
        self.assertTrue(cond['visible_peer_present'])

    def test_output_veto(self):
        result = self.check_failed('tj0112-bingsi-output-veto')
        cond = result['action_effects'][
            'lu_visible_support_scope_conditions']
        self.assertFalse(cond['visible_positions_support_only'])
        self.assertTrue(cond['visible_resource_present'])
        self.assertTrue(cond['visible_peer_present'])

    def test_wrong_month_wu(self):
        # The lu table fails the month condition ALONE, and the
        # chart's strong verdict comes from the commanding predicate:
        # the two fire forms are month-exclusive, never double-fired.
        case, out, result, pillars = run_case(
            'tj0112-bingsi-wrong-month-wu')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(effects['lu_visible_support_scope_conditions'],
                         case['expected_conditions'])
        self.assertFalse(effects['lu_visible_support_scope_met'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(
            assessment['why_not_indeterminate']['sufficient_predicate'],
            'commanding_visible_support')

    def test_ding_not_applicable(self):
        # Ding x Si is blocked_by_conflict line-wide (Ding changsheng
        # conflict unadjudicated); independently, the lu form's first
        # condition is Bing-only, so a support-shaped Ding chart can
        # never fire lu_visible_support.
        result = self.check_failed('tj0112-bingsi-ding-not-applicable')
        cond = result['action_effects'][
            'lu_visible_support_scope_conditions']
        self.assertFalse(cond['fire_day_master_bing'])


class FactorLayerTests(unittest.TestCase):
    """Factor-level coverage for the chart-unrealizable single
    failures (see Golden unrealizable_designs). Inputs are synthetic
    factor structures modelled on executed output shapes; this layer
    is labelled factor-level and never presented as a real chart."""

    def _inputs(self):
        pillars = [{'name': n, 'stem': {'value': s}} for n, s in
                   (('year', '丁'), ('month', '乙'), ('day', '丙'),
                    ('hour', '甲'))]
        observed = {
            'day_master': '丙',
            'visible_relations': [
                {'fact': {'pillar': 'year', 'stem': '丁', 'element': '火',
                          'relation': 'same_element',
                          'root_positions': [
                              {'pillar': 'hour', 'branch': '午',
                               'hidden_stem': '丁', 'same_stem': True}]},
                 'conditions': {}},
                {'fact': {'pillar': 'month', 'stem': '乙', 'element': '木',
                          'relation': 'generates_me',
                          'root_positions': [
                              {'pillar': 'year', 'branch': '卯',
                               'hidden_stem': '乙', 'same_stem': True}]},
                 'conditions': {}},
                {'fact': {'pillar': 'hour', 'stem': '甲', 'element': '木',
                          'relation': 'generates_me',
                          'root_positions': [
                              {'pillar': 'year', 'branch': '卯',
                               'hidden_stem': '乙', 'same_stem': False}]},
                 'conditions': {}},
            ],
            'hidden_relations': [
                {'fact': {'pillar': 'month', 'stem': '戊', 'element': '土',
                          'relation': 'i_generate'}},
                {'fact': {'pillar': 'month', 'stem': '庚', 'element': '金',
                          'relation': 'i_control'}},
            ],
        }
        principal = {'month_branch': '巳', 'status': 'reviewed_relation',
                     'relation': 'same_element',
                     'principal_qi': '丙', 'day_master': '丙'}
        availability = {
            'day_master': '丙', 'root_presence': True,
            'roots': [{'root_index': 0,
                       'root_presence': {'pillar': 'month', 'branch': '巳',
                                         'hidden_stem': '丙'},
                       'root_availability': 'unresolved',
                       'type_source_conflict': None,
                       'branch_relations': []}],
        }
        relations = {'stem_five_combinations': [],
                     'branch_six_harmonies': [], 'branch_six_harms': [],
                     'branch_six_clashes': [],
                     'branch_triple_harmonies': []}
        return pillars, observed, relations, principal, availability

    def _effects(self, observed, principal, availability):
        pillars, _, relations, _, _ = self._inputs()
        return action_effects(pillars, observed=observed,
                              relations=relations, principal=principal,
                              availability=availability)

    def test_factor_baseline_all_true_despite_hidden_output_wealth(self):
        _, observed, _, principal, availability = self._inputs()
        effects = self._effects(observed, principal, availability)
        cond = effects['lu_visible_support_scope_conditions']
        self.assertTrue(all(cond.values()), cond)
        self.assertTrue(effects['lu_visible_support_scope_met'])

    def test_factor_no_peer_isolated(self):
        _, observed, _, principal, availability = self._inputs()
        observed = copy.deepcopy(observed)
        for row in observed['visible_relations']:
            if row['fact']['relation'] == 'same_element':
                row['fact']['relation'] = 'generates_me'
        effects = self._effects(observed, principal, availability)
        cond = effects['lu_visible_support_scope_conditions']
        self.assertEqual({k for k, v in cond.items() if not v},
                         {'visible_peer_present'})

    def test_factor_no_resource_isolated(self):
        _, observed, _, principal, availability = self._inputs()
        observed = copy.deepcopy(observed)
        for row in observed['visible_relations']:
            if row['fact']['relation'] == 'generates_me':
                row['fact']['relation'] = 'same_element'
        effects = self._effects(observed, principal, availability)
        cond = effects['lu_visible_support_scope_conditions']
        self.assertEqual({k for k, v in cond.items() if not v},
                         {'visible_resource_present'})

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
        cond = effects['lu_visible_support_scope_conditions']
        self.assertEqual({k for k, v in cond.items() if not v},
                         {'effective_heavy_day_roots'})

    def test_factor_hidden_officer_does_not_veto(self):
        _, observed, _, principal, availability = self._inputs()
        observed = copy.deepcopy(observed)
        observed['hidden_relations'].append(
            {'fact': {'pillar': 'year', 'stem': '壬', 'element': '水',
                      'relation': 'controls_me'}})
        effects = self._effects(observed, principal, availability)
        cond = effects['lu_visible_support_scope_conditions']
        self.assertTrue(cond['visible_positions_support_only'])
        self.assertTrue(all(cond.values()), cond)


class WholeDomainScanTests(unittest.TestCase):
    def test_lu_fires_exactly_for_the_witness(self):
        births = [c['source_birth'] for c in CASES.values()]
        births += [c['source_birth'] for c in WOOD.values()]
        births += [c['source_birth'] for c in BINGWU.values()]
        births += [c['source_birth'] for c in S2G.values()]
        births += [c['source_birth'] for c in DESIGN.values()]
        # The design witness and the implementation positive are the
        # same chart; dedupe so the firing list is per-chart.
        births = list(dict.fromkeys(births))
        fired = []
        for birth in births:
            _, result, _ = run_birth(birth)
            assessment = result['strength_assessment']
            why = assessment['why_not_indeterminate']
            if why and why.get('sufficient_predicate') \
                    == 'lu_visible_support':
                fired.append(birth)
                # This form never yields weak (register direction).
                self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(fired, [CASES['tj0112-bingsi-positive']
                                 ['source_birth']])

    def test_six_predicates_regression_spot_checks(self):
        # Wood pure / generating / isolated, Bing-Wu commanding, S2
        # water witness: verdicts and exits unchanged by this batch.
        checks = [
            ('tj0112-bingwu-positive', BINGWU, 'strong',
             'commanding_visible_support'),
            ('tj0112-s2-water-positive-gui', S2G, 'strong',
             'pure_generating_support_water'),
            ('tj0112-f4-positive-both-readings', DESIGN, 'indeterminate',
             None),
        ]
        for case_id, source, classification, predicate in checks:
            case = source[case_id]
            _, result, pillars = run_birth(case['source_birth'])
            self.assertEqual(pillars, case['expected_pillars'], case_id)
            assessment = result['strength_assessment']
            self.assertEqual(assessment['classification'],
                             classification, case_id)
            why = assessment['why_not_indeterminate']
            if predicate is None:
                self.assertIsNone(why, case_id)
            else:
                self.assertEqual(why['sufficient_predicate'], predicate,
                                 case_id)


if __name__ == '__main__':
    unittest.main()
