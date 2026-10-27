"""TJ-011.2: wood x Hai generating-month extension of the bounded strength
adjudication Variant (bazi-strength-adjudication-v1).

Every chart-level case is a REAL birth datetime executed through the
reviewed calendar path (engine.execute); no pillar is hand-assembled.
Expected pillars in tests/golden_tj0112_wood_hai.json were confirmed
producible by the reviewed calendar, and every expected adjudication
outcome was derived by hand from the scope conditions (the derivation
is recorded per case in the golden file), never copied from output.

What is covered:
- positive: Hai-month pure generating support -> strong, in two root
  compositions (middle-qi Jia root only; principal-qi root in Mao
  participating alongside the Hai middle-qi root);
- counterexamples: wrong month (Zi, same generating relation), non-wood
  day master, a draining visible stem, clashed (non-effective) roots;
- conflict: residual-qi root type source conflict abstains by blocker;
- abstention: no visible resource stem -> indeterminate, no verdict;
- regression: the two v1 predicates (Mao pure / You isolated) are
  untouched and still fire through their original rule IDs;
- display gate: the public allowlist stays empty and the new branch's
  classification never reaches a public projection (TJ-011.3 pattern).

Like the other sealed-runtime suites (test_phase2_bazi*), this module
runs in the offline assembled acceptance, not in public CI.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import public_projection
from tianji_kb.bazi_action_conditions import PURE_GENERATING_MONTHS
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_strength_display import (
    PUBLIC_STRENGTH_VARIANTS, get_display_decision)
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
CASES = {c['id']: c for c in
         json.loads((ROOT / 'tests/golden_tj0112_wood_hai.json').read_text('utf-8'))['cases']}

GENERATING_KEYS = {
    'wood_day_master', 'reviewed_generating_month', 'all_positions_support_only',
    'visible印_present', 'visible比_present', 'effective_day_roots',
    'all_visible_have_reviewed_roots', 'no_unresolved_interactions',
}
PURE_KEYS = {
    'wood_day_master', 'reviewed_same_element_month', 'all_positions_support_only',
    'visible印_present', 'visible比_present', 'effective_day_roots',
    'all_visible_have_reviewed_roots', 'no_unresolved_interactions',
}
ISOLATED_KEYS = {
    'wood_day_master', 'reviewed_control_month', 'day_has_no_structural_root',
    'no_support_in_any_position', 'visible_earth_metal_only',
    'month_principal_exposed_with_root', 'no_unresolved_interactions',
}


def run_case(case_id):
    case = CASES[case_id]
    out = execute('bazi', {'value': case['source_birth'],
                           'strength_variant': ADJUDICATION_VARIANT},
                  allow_research=True)
    result = out['result']
    pillars = [p['stem']['value'] + p['branch']['value'] for p in result['pillars']]
    return case, out, result, pillars


class GeneratingScopeShapeTests(unittest.TestCase):
    def test_condition_key_sets_and_sealed_policy_provenance(self):
        _, _, result, _ = run_case('tj0112-hai-positive-zhongqi-root')
        effects = result['action_effects']
        self.assertEqual(set(effects['pure_generating_support_scope_conditions']),
                         GENERATING_KEYS)
        # The v1 condition sets are byte-identical in shape: the extension
        # adds a parallel set and does not touch either existing one.
        self.assertEqual(set(effects['pure_support_scope_conditions']), PURE_KEYS)
        self.assertEqual(set(effects['isolated_control_scope_conditions']), ISOLATED_KEYS)
        self.assertEqual(PURE_GENERATING_MONTHS, ('亥',))
        # The extension is declared in public code; the sealed policy is
        # NOT edited (its month lists keep their TJ-011.1 values).
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches']['木'], ['亥', '寅', '卯'])


class HaiPositiveTests(unittest.TestCase):
    def check_positive(self, case_id):
        case, out, result, pillars = run_case(case_id)
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(assessment['decision_status'],
                         'reviewed_sufficient_rule_matched')
        why = assessment['why_not_indeterminate']
        self.assertIsNotNone(why)
        # S5 governance batch: the predicate is registered in the
        # sealed snapshot (bazi.rule.r029), so the verdict is issued
        # through its own registered trace step, exactly like
        # pure_support; it carries no pending-registration disclosure
        # and no sufficient_predicate alias.
        self.assertEqual(why['sufficient_rule'],
                         'bazi.phase2.strength_pure_generating_support')
        self.assertNotIn('sufficient_predicate', why)
        self.assertNotIn('predicate_rule_registration', why)
        trace_rule_ids = [s['rule_id'] for s in out['trace']]
        self.assertIn('bazi.phase2.strength_pure_generating_support',
                      trace_rule_ids)
        self.assertIn('bazi.phase2.strength_bounded_adjudication',
                      trace_rule_ids)
        self.assertIn('bazi.phase2.strength_pure_generating_support',
                      assessment['matched_rule_ids'])
        self.assertTrue(why['all_required_conditions_verified'])
        self.assertEqual({c['condition'] for c in why['conditions']}, GENERATING_KEYS)
        for cond in why['conditions']:
            self.assertTrue(cond['met'])
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(set(cond['evidence_ids']) <= set(out['evidence']))
        effects = result['action_effects']
        self.assertTrue(effects['pure_generating_support_scope_met'])
        self.assertTrue(all(
            effects['pure_generating_support_scope_conditions'].values()))
        self.assertTrue(all(r['effect_status'] == 'effective_in_reviewed_context'
                            for r in effects['visible_relations']))
        self.assertTrue(all(r['context'] == 'pure_generating_support'
                            for r in effects['visible_relations']))
        # Research gate stays shut on every axis.
        self.assertTrue(assessment['research_only'])
        self.assertFalse(assessment['public_enabled'])
        self.assertFalse(assessment['ai_enabled'])
        return result

    def test_positive_roots_only_via_hai_middle_qi_jia(self):
        result = self.check_positive('tj0112-hai-positive-zhongqi-root')
        roots = result['root_conditions']['roots']
        self.assertTrue(roots)
        for root in roots:
            self.assertEqual(root['fact']['branch'], '亥')
            self.assertEqual(root['fact']['hidden_stem'], '甲')
            self.assertTrue(root['fact']['same_stem'])
            # Hai's principal qi is Ren, so the Jia root is a middle-qi
            # root, never a principal-qi match.
            self.assertFalse(root['fact']['principal_qi_match'])
        self.assertTrue(all(r['root_availability'] == 'effective'
                            for r in result['root_availability']['roots']))

    def test_positive_with_benqi_root_participating(self):
        result = self.check_positive('tj0112-hai-positive-benqi-root')
        facts = [r['fact'] for r in result['root_conditions']['roots']]
        self.assertTrue(any(f['branch'] == '卯' and f['principal_qi_match']
                            for f in facts))
        self.assertTrue(any(f['branch'] == '亥' and not f['principal_qi_match']
                            for f in facts))
        self.assertTrue(all(r['root_availability'] == 'effective'
                            for r in result['root_availability']['roots']))


class HaiCounterexampleTests(unittest.TestCase):
    def test_counterexample_month_not_hai(self):
        case, out, result, pillars = run_case('tj0112-hai-counter-month-not-hai')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        cond = effects['pure_generating_support_scope_conditions']
        # Zi's principal qi also generates wood; the month SCOPE is what
        # fails, which is exactly the reviewed-scope discipline of v1.
        self.assertFalse(cond['reviewed_generating_month'])
        self.assertFalse(effects['pure_generating_support_scope_met'])
        self.assertEqual(result['strength_assessment']['classification'],
                         'indeterminate')

    def test_counterexample_nonwood_day_master(self):
        case, out, result, pillars = run_case(
            'tj0112-hai-counter-nonwood-day-master')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertFalse(
            effects['pure_generating_support_scope_conditions']['wood_day_master'])
        self.assertFalse(
            effects['pure_support_scope_conditions']['wood_day_master'])
        self.assertEqual(result['strength_assessment']['classification'],
                         'indeterminate')

    def test_counterexample_visible_drain_breaks_support_only(self):
        case, out, result, pillars = run_case('tj0112-hai-counter-visible-drain')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertFalse(effects['pure_generating_support_scope_conditions']
                         ['all_positions_support_only'])
        self.assertFalse(effects['pure_support_scope_conditions']
                         ['all_positions_support_only'])
        self.assertFalse(effects['pure_generating_support_scope_met'])
        self.assertEqual(result['strength_assessment']['classification'],
                         'indeterminate')

    def test_counterexample_clashed_roots_are_not_effective(self):
        case, out, result, pillars = run_case('tj0112-hai-counter-root-clashed')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertFalse(effects['pure_generating_support_scope_conditions']
                         ['effective_day_roots'])
        self.assertTrue(result['root_availability']['roots'])
        self.assertTrue(all(r['root_availability'] != 'effective'
                            for r in result['root_availability']['roots']))
        assessment = result['strength_assessment']
        self.assertIn('root_availability_not_effective',
                      {b['reason'] for b in assessment['blockers']})
        self.assertEqual(assessment['classification'], 'indeterminate')

    def test_conflict_root_type_readings_abstains(self):
        case, out, result, pillars = run_case(
            'tj0112-hai-conflict-root-type-readings')
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertIn('root_type_source_conflict',
                      {b['reason'] for b in assessment['blockers']})
        self.assertIn('bazi.concept.conflict_root_type_readings',
                      assessment['conflict_ids'])
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIsNone(assessment['why_not_indeterminate'])

    def test_abstain_when_no_visible_resource(self):
        case, out, result, pillars = run_case(
            'tj0112-hai-abstain-no-visible-resource')
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        cond = effects['pure_generating_support_scope_conditions']
        self.assertFalse(cond['visible印_present'])
        # Everything else in the generating scope holds: the abstention
        # is attributable to the single missing visible resource stem.
        for key in GENERATING_KEYS - {'visible印_present'}:
            self.assertTrue(cond[key], key)
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIsNone(assessment['why_not_indeterminate'])
        self.assertEqual(assessment['decision_status'],
                         'insufficient_reviewed_rules')


class V1RegressionTests(unittest.TestCase):
    def test_mao_pure_support_still_fires_through_original_rule(self):
        case, out, result, pillars = run_case('tj0112-regression-mao-pure-support')
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(assessment['why_not_indeterminate']['sufficient_rule'],
                         'bazi.phase2.strength_pure_support')
        self.assertFalse(result['action_effects']
                         ['pure_generating_support_scope_met'])

    def test_you_isolated_control_still_fires_through_original_rule(self):
        case, out, result, pillars = run_case(
            'tj0112-regression-you-isolated-control')
        self.assertEqual(pillars, case['expected_pillars'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'weak')
        self.assertEqual(assessment['why_not_indeterminate']['sufficient_rule'],
                         'bazi.phase2.strength_isolated_control')
        self.assertFalse(result['action_effects']
                         ['pure_generating_support_scope_met'])

    def test_generating_branch_never_yields_weak(self):
        for case_id, case in CASES.items():
            if case['expected_pillars'][1].endswith('亥'):
                _, _, result, _ = run_case(case_id)
                self.assertNotEqual(
                    result['strength_assessment']['classification'], 'weak',
                    case_id)


class DisplayGateTests(unittest.TestCase):
    """TJ-011.3 pattern: the new branch's verdict is research-only."""

    def real_positive(self):
        _, _, result, _ = run_case('tj0112-hai-positive-zhongqi-root')
        return result

    def test_allowlist_remains_empty(self):
        self.assertEqual(PUBLIC_STRENGTH_VARIANTS, frozenset())

    def test_display_decision_never_displays_hai_classification(self):
        result = self.real_positive()
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        decision = get_display_decision(
            assessment, variant=ADJUDICATION_VARIANT,
            day_master='甲', month_branch='亥')
        self.assertFalse(decision['may_display_classification'])
        self.assertIsNone(decision['classification'])

    def test_projection_strips_hai_classification(self):
        result = self.real_positive()
        assessment = copy.deepcopy(result['strength_assessment'])
        data = {'evidence': {}, 'rule_matches': [], 'trace': [],
                'chart': {'pillars': result['pillars'],
                          'strength_assessment': assessment}}
        projected = public_projection.project_execution(data)
        projected_assessment = projected['chart']['strength_assessment']
        self.assertNotIn('classification', projected_assessment)
        # The display scope (AUDITED_MONTHS) is intentionally unchanged
        # in this batch; the verdict is withheld either way.
        self.assertEqual(projected_assessment['display_state'], 'out_of_scope')

    def test_projection_strips_forged_public_enabled(self):
        result = self.real_positive()
        assessment = copy.deepcopy(result['strength_assessment'])
        assessment['public_enabled'] = True  # forged flag must not matter
        data = {'evidence': {}, 'rule_matches': [], 'trace': [],
                'chart': {'pillars': result['pillars'],
                          'strength_assessment': assessment}}
        projected = public_projection.project_execution(data)
        self.assertNotIn('classification',
                         projected['chart']['strength_assessment'])


if __name__ == '__main__':
    unittest.main()
