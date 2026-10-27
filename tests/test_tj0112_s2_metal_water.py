"""TJ-011.2 S2: pure-support extension to metal x You
(pure_support_metal) and water x Zi (pure_generating_support_water) --
the 5th and 6th sufficient predicates of bazi-strength-adjudication-v1,
isomorphic extensions of the wood pure form per the general-strength
scout (S2) and the S1 root-grading register (bazi_metal_water_roots).

Every chart-level case is a REAL birth datetime executed through the
reviewed calendar path (engine.execute); no pillar is hand-assembled.
Expected condition tables in tests/golden_tj0112_s2_metal_water.json
were derived BY HAND from the eight registered conditions, the S1
register grades and the executed factor definitions -- never copied
from implementation output. (One derivation was corrected during the
batch after re-derivation disagreed with a first pass: the Geng case --
Yin does not hide Geng, and the Xin/Bing stem combination is an
unresolved interaction; the engine agreed with the corrected hand
derivation on both points.)

Covered:
- positive: Gui x Zi -> strong via the registered bounded exit
  (sufficient_rule None, pending Phase1 registration disclosed), eight
  conditions bound to executed factor evidence, each carrying its
  registered anchor_type; the month condition carries the executed
  month_root_grade (per_stem_listed) and the root condition the
  executed root_grades, so an explicitly attested root position stays
  machine-distinguishable from a framework-derived one;
- near misses with hand-derived full condition tables: Ren x Zi with
  exactly one failing condition (no visible peer -- the registered Ren
  unsatisfiability, witnessed on one face); Chou month one branch off
  the gate; a Gui chart whose Hai root is a conflicted_pending cell
  (register-presented conflict sanming-juan2.gui-changsheng -- the
  executed fact itself carries no conflict flag); a Gui chart whose
  Chou root is a light_listed_conflicted cell (fact/register agree,
  presented exactly once); Xin x You with the month gate TRUE but both
  heavy roots clash-touched; Geng x You failing through support /
  resource / visible-roots / stem-combination;
- factor-layer unit tests (synthetic factor inputs, labelled
  factor-level, following the commanding batch precedent): the water
  scope CAN evaluate all-true and each tested single failure flips
  exactly one condition; the metal scope evaluates all-true EXCEPT
  all_visible_have_registered_roots, whose sole blocker is the
  registered earth-root gap (an earth visible stem has no settled root
  set in the sealed policy or the S1 register) -- pinned as intended
  behaviour, with pending/light/clashed root and month-gate and
  no-peer isolations on top of that baseline;
- unrealizable registrations: the metal form is constructively
  unsatisfiable on real charts (three proof channels) and Ren is
  unsatisfiable within the water form (two channels); both are
  registered in the Golden and in bazi_metal_water_roots, and the
  whole-domain scan confirms the metal predicate never fires at chart
  level and the water predicate fires only for the Gui witness;
- regression: the four pre-existing predicates keep their verdicts
  (scan over the wood and commanding Golden sets), the sealed policy
  is not edited, the display whitelist stays empty and the public
  projection still strips the classification.

Like the other sealed-runtime suites, this module runs in the offline
assembled acceptance, not in public CI.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import public_projection
from tianji_kb.bazi_action_conditions import action_effects
from tianji_kb.bazi_adjudication import (
    ADJUDICATION_VARIANT, S2_ANCHOR_REGISTRATION)
from tianji_kb.bazi_metal_water_roots import (
    METAL_WATER_ROOT_TABLES, S2_ANCHOR_TYPES, S2_FORM_REGISTERS,
    S2_LIMITATIONS)
from tianji_kb.bazi_strength_display import (
    PUBLIC_STRENGTH_VARIANTS, get_display_decision)
from tianji_kb.engine import execute
from tianji_kb.resolver import EvidenceResolver

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_s2_metal_water.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
WOOD = {c['id']: c for c in json.loads(
    (ROOT / 'tests/golden_tj0112_wood_hai.json').read_text('utf-8'))['cases']}
BING = {c['id']: c for c in json.loads(
    (ROOT / 'tests/golden_tj0112_bing_wu_commanding.json')
    .read_text('utf-8'))['cases']}
FIRE = {c['id']: c for c in json.loads(
    (ROOT / 'tests/golden_tj0112_fire_morphology.json')
    .read_text('utf-8'))['cases']}

METAL_KEYS = [c['key'] for c in
              S2_FORM_REGISTERS['pure_support_metal']['conditions']]
WATER_KEYS = [c['key'] for c in
              S2_FORM_REGISTERS['pure_generating_support_water']
              ['conditions']]
NEW_PREDICATES = ('pure_support_metal', 'pure_generating_support_water')


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


class ScopeShapeTests(unittest.TestCase):
    def test_scope_keys_match_registers_exactly(self):
        _, _, result, _ = run_case('tj0112-s2-water-positive-gui')
        effects = result['action_effects']
        self.assertEqual(
            list(effects['pure_support_metal_scope_conditions']),
            METAL_KEYS)
        self.assertEqual(
            list(effects['pure_generating_support_water_scope_conditions']),
            WATER_KEYS)
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
            {'fire_day_master_bing', 'reviewed_same_element_command_month',
             'visible_positions_support_only', 'visible_resource_present',
             'visible_peer_present', 'effective_heavy_day_roots',
             'all_visible_have_reviewed_roots',
             'no_unresolved_interactions',
             'hidden_layer_convention_applied'})

    def test_anchor_maps_match_registers(self):
        self.assertEqual(S2_ANCHOR_TYPES, {
            predicate: {c['key']: c['anchor_type']
                        for c in form['conditions']}
            for predicate, form in S2_FORM_REGISTERS.items()})
        self.assertEqual(
            S2_ANCHOR_REGISTRATION['pure_support_metal'],
            'bazi_metal_water_roots.FORM_PURE_SUPPORT_METAL')
        self.assertEqual(
            S2_ANCHOR_REGISTRATION['pure_generating_support_water'],
            'bazi_metal_water_roots.FORM_PURE_GENERATING_WATER')
        # The month and root conditions are anchored in original text;
        # the scope-construction conditions are labelled as such, never
        # dressed up as text.
        for predicate in NEW_PREDICATES:
            self.assertEqual(
                S2_ANCHOR_TYPES[predicate]
                ['effective_day_roots_registered'], 'original_text')

    def test_sealed_policy_not_edited(self):
        policy = EvidenceResolver().entities[
            'bazi.concept.action_effects_v1'][1]['attributes']
        self.assertEqual(policy['pure_months'], ['卯'])
        self.assertEqual(policy['isolated_months'], ['酉'])
        self.assertEqual(policy['reviewed_root_branches'],
                         {'木': ['亥', '寅', '卯'], '水': ['亥', '子'],
                          '金': ['酉']})
        self.assertNotIn('土', policy['reviewed_root_branches'])
        self.assertNotIn('火', policy['reviewed_root_branches'])


class WaterPositiveTests(unittest.TestCase):
    def test_positive_strong_via_bounded_exit(self):
        case, out, result, pillars = run_case(
            'tj0112-s2-water-positive-gui')
        expect = case['expect']
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(
            effects['pure_generating_support_water_scope_conditions'],
            expect['scope_conditions'])
        self.assertTrue(
            effects['pure_generating_support_water_scope_met'])
        self.assertTrue(all(
            r['effect_status'] == 'effective_in_reviewed_context'
            for r in effects['visible_relations']))
        self.assertTrue(all(
            r['context'] == 'pure_generating_support_water'
            for r in effects['visible_relations']))
        # Hidden Zi roots participate through register-effective roots.
        zi_hidden = [r for r in effects['hidden_relations']
                     if r['fact']['branch'] == '子']
        self.assertTrue(zi_hidden)
        self.assertTrue(all(
            r['effect_status'] == 'root_participation_only'
            and r['root_indexes'] for r in zi_hidden))
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(assessment['decision_status'],
                         'reviewed_sufficient_rule_matched')
        why = assessment['why_not_indeterminate']
        self.assertIsNotNone(why)
        self.assertIsNone(why['sufficient_rule'])
        self.assertEqual(why['sufficient_predicate'],
                         'pure_generating_support_water')
        self.assertEqual(why['predicate_rule_registration'],
                         'pending_phase1_rule_registration')
        self.assertTrue(why['all_required_conditions_verified'])
        trace_rule_ids = [s['rule_id'] for s in out['trace']]
        self.assertIn('bazi.phase2.strength_bounded_adjudication',
                      trace_rule_ids)
        self.assertNotIn(
            'bazi.phase2.strength_pure_generating_support_water',
            trace_rule_ids)
        self.assertEqual([c['condition'] for c in why['conditions']],
                         WATER_KEYS)
        for cond in why['conditions']:
            self.assertTrue(cond['met'], cond['condition'])
            self.assertEqual(
                cond['anchor_type'],
                S2_ANCHOR_TYPES['pure_generating_support_water']
                [cond['condition']])
            self.assertEqual(
                cond['anchor_registration'],
                'bazi_metal_water_roots.FORM_PURE_GENERATING_WATER')
            self.assertTrue(cond['evidence_ids'])
            self.assertTrue(
                set(cond['evidence_ids']) <= set(out['evidence']))
            self.assertIn(
                '/pure_generating_support_water_scope_conditions/',
                cond['fact_ref'])
        month_cond = next(
            c for c in why['conditions']
            if c['condition'] == 'reviewed_same_element_month_zi')
        # Gui at Zi is the Lu position: explicitly attested per-stem,
        # NOT framework-derived -- machine-distinguishable.
        self.assertEqual(month_cond['month_root_grade'],
                         expect['month_root_grade'])
        self.assertEqual(month_cond['month_root_grade'],
                         'per_stem_listed')
        root_cond = next(
            c for c in why['conditions']
            if c['condition'] == 'effective_day_roots_registered')
        self.assertEqual(
            [[g['pillar'], g['branch'], g['hidden_stem'], g['grade']]
             for g in root_cond['root_grades']],
            expect['root_grades'])
        # The wood-scope availability blockers against the two
        # register-effective roots were reconciled; nothing else bars.
        self.assertEqual(assessment['blockers'], [])
        self.assertEqual(assessment['conflict_ids'], [])
        self.assertTrue(assessment['research_only'])
        self.assertFalse(assessment['public_enabled'])
        self.assertFalse(assessment['ai_enabled'])
        self.assertTrue(any(
            '酉月金日主与子月水日主分支谓词尚待' in line
            for line in assessment['limitations']))
        for line in S2_LIMITATIONS:
            self.assertIn(line, assessment['limitations'])

    def test_display_gate_unchanged(self):
        _, _, result, _ = run_case('tj0112-s2-water-positive-gui')
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(PUBLIC_STRENGTH_VARIANTS, frozenset())
        decision = get_display_decision(
            assessment, variant=ADJUDICATION_VARIANT,
            day_master='癸', month_branch='子')
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


class NearMissTests(unittest.TestCase):
    """Each near miss pins the FULL hand-derived condition table of the
    relevant new scope (from the Golden), not just the verdict."""

    def check_near_miss(self, case_id, scope):
        case, out, result, pillars = run_case(case_id)
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        key = ('pure_support_metal_scope_conditions' if scope == 'metal'
               else 'pure_generating_support_water_scope_conditions')
        self.assertEqual(effects[key], case['expect']['scope_conditions'])
        self.assertFalse(effects[key.replace('conditions', 'met')])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'], 'indeterminate')
        self.assertIsNone(assessment['why_not_indeterminate'])
        return case, out, result

    def test_ren_no_visible_peer_single_failure(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-water-near-miss-ren-no-visible-peer', 'water')
        table = case['expect']['scope_conditions']
        self.assertEqual([k for k, v in table.items() if not v],
                         ['visible比_present'])
        # The seven true conditions rest on framework-derived roots:
        # Ren at Zi is Di-wang by framework derivation only. The scope
        # condition is true AND the register grade is framework_derived
        # -- the derived grade is exercised, never upgraded to text.
        self.assertTrue(table['effective_day_roots_registered'])
        grades = {e['branch']: e['grade']
                  for e in METAL_WATER_ROOT_TABLES['壬']}
        self.assertEqual(grades['子'], 'framework_derived')

    def test_chou_month_gate_and_light_root(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-water-near-miss-chou-month', 'water')
        assessment = result['strength_assessment']
        self.assertIn('bazi.concept.conflict_root_type_readings',
                      assessment['conflict_ids'])
        reasons = {b['reason'] for b in assessment['blockers']}
        self.assertIn('principal_qi_not_reviewed', reasons)
        self.assertIn('root_type_source_conflict', reasons)

    def test_gui_hai_pending_root_register_presented(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-water-near-miss-gui-hai-pending-root', 'water')
        assessment = result['strength_assessment']
        # The executed root fact for the Hai root carries NO fact-level
        # conflict flag; the conflict is presented from the S1 register
        # (elif branch), with the registered branch conflict ID.
        checks = [c for c in assessment['conflict_checks']
                  if c['conflict_id'] == 'sanming-juan2.gui-changsheng']
        self.assertEqual(len(checks), 1)
        self.assertTrue(checks[0]['blocking'])
        self.assertTrue(checks[0]['fact_ref'].endswith(
            '/roots/1/root_presence/branch'))
        self.assertIn('sanming-juan2.gui-changsheng',
                      assessment['conflict_ids'])
        # The pending cell never passes: the root condition is false
        # and a root_type_source_conflict blocker stands.
        reasons = {b['reason'] for b in assessment['blockers']}
        self.assertIn('root_type_source_conflict', reasons)

    def test_gui_chou_light_root_presented_once(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-water-near-miss-gui-chou-light-root', 'water')
        assessment = result['strength_assessment']
        checks = [c for c in assessment['conflict_checks']
                  if c['conflict_id']
                  == 'bazi.concept.conflict_root_type_readings']
        # Fact-level and register-level name the same conflict for the
        # hour root; the elif ordering presents it exactly once.
        hour_checks = [c for c in checks if '/roots/1/' in c['fact_ref']]
        self.assertEqual(len(hour_checks), 1)
        self.assertEqual(
            case['expect']['root_conflict_count_for_hour_root'], 1)

    def test_xin_you_month_gate_true_but_clashed_roots(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-metal-near-miss-xin-clashed-roots', 'metal')
        table = case['expect']['scope_conditions']
        # The S1 month fact itself is satisfied (Xin Lu at You,
        # double-attested, branch-independent); the form fails on the
        # clash-touched roots and the other conditions, not the gate.
        self.assertTrue(table['reviewed_same_element_month_you'])
        self.assertFalse(table['effective_day_roots_registered'])
        assessment = result['strength_assessment']
        reasons = {b['reason'] for b in assessment['blockers']}
        self.assertIn('interaction_effect_unresolved', reasons)

    def test_geng_you_stem_combination(self):
        case, _, result = self.check_near_miss(
            'tj0112-s2-metal-near-miss-geng-stem-combination', 'metal')
        table = case['expect']['scope_conditions']
        self.assertTrue(table['effective_day_roots_registered'])
        self.assertFalse(table['no_unresolved_interactions'])
        self.assertEqual(
            result['action_effects']['unresolved_interaction_kinds'],
            ['stem_five_combinations'])


def _relations():
    return {'stem_five_combinations': [], 'branch_six_harmonies': [],
            'branch_six_harms': [], 'branch_six_clashes': [],
            'branch_triple_harmonies': []}


def _vis(pillar, stem, element, relation, positions):
    return {'fact': {'pillar': pillar, 'stem': stem, 'element': element,
                     'relation': relation, 'root_positions': positions},
            'conditions': {}}


def _pos(pillar, branch, hidden, same=False):
    return {'pillar': pillar, 'branch': branch, 'hidden_stem': hidden,
            'same_stem': same}


def _root(index, pillar, branch, hidden):
    return {'root_index': index,
            'root_presence': {'pillar': pillar, 'branch': branch,
                              'hidden_stem': hidden},
            'root_availability': 'unresolved',
            'type_source_conflict': None, 'branch_relations': []}


class FactorLayerTests(unittest.TestCase):
    """Factor-level coverage for the chart-unrealizable forms (see
    Golden unrealizable entries). Inputs are synthetic factor
    structures modelled on executed output shapes; this layer is
    labelled factor-level and never presented as a real chart."""

    def _water_inputs(self):
        pillars = [{'name': n, 'stem': {'value': s}} for n, s in
                   (('year', '辛'), ('month', '庚'), ('day', '癸'),
                    ('hour', '壬'))]
        observed = {
            'day_master': '癸',
            'visible_relations': [
                _vis('year', '辛', '金', 'generates_me',
                     [_pos('year', '酉', '辛', True)]),
                _vis('month', '庚', '金', 'generates_me',
                     [_pos('year', '酉', '辛'), _pos('day', '酉', '辛')]),
                _vis('hour', '壬', '水', 'same_element',
                     [_pos('month', '子', '癸'),
                      _pos('hour', '子', '癸')])],
            'hidden_relations': [
                {'fact': {'pillar': 'year', 'stem': '辛',
                          'element': '金', 'relation': 'generates_me'}},
                {'fact': {'pillar': 'month', 'stem': '癸',
                          'element': '水', 'relation': 'same_element'}},
                {'fact': {'pillar': 'day', 'stem': '辛',
                          'element': '金', 'relation': 'generates_me'}},
                {'fact': {'pillar': 'hour', 'stem': '癸',
                          'element': '水', 'relation': 'same_element'}}]}
        principal = {'month_branch': '子', 'status': 'reviewed_relation',
                     'relation': 'same_element', 'principal_qi': '癸',
                     'day_master': '癸'}
        availability = {'day_master': '癸', 'root_presence': True,
                        'roots': [_root(0, 'month', '子', '癸'),
                                  _root(1, 'hour', '子', '癸')]}
        return pillars, observed, principal, availability

    def _water_effects(self, observed, principal, availability):
        pillars, _, _, _ = self._water_inputs()
        return action_effects(pillars, observed=observed,
                              relations=_relations(),
                              principal=principal,
                              availability=availability)

    def _water_failures(self, effects):
        cond = effects['pure_generating_support_water_scope_conditions']
        return {k for k, v in cond.items() if not v}

    def test_factor_water_baseline_all_true(self):
        _, observed, principal, availability = self._water_inputs()
        effects = self._water_effects(observed, principal, availability)
        self.assertEqual(self._water_failures(effects), set())
        self.assertTrue(
            effects['pure_generating_support_water_scope_met'])

    def test_factor_water_pending_root_isolated(self):
        _, observed, principal, availability = self._water_inputs()
        availability = copy.deepcopy(availability)
        # Gui at Hai: conflicted_pending cell (gui-changsheng branch).
        # The synthetic fact carries no conflict flag and no branch
        # relation, so ONLY the register grade can block it.
        availability['roots'].append(_root(2, 'hour', '亥', '壬'))
        effects = self._water_effects(observed, principal, availability)
        self.assertEqual(self._water_failures(effects),
                         {'effective_day_roots_registered'})

    def test_factor_water_light_root_isolated(self):
        _, observed, principal, availability = self._water_inputs()
        availability = copy.deepcopy(availability)
        # Gui at Chou: light_listed_conflicted cell, again with a clean
        # synthetic fact -- the grade alone blocks.
        availability['roots'].append(_root(2, 'hour', '丑', '癸'))
        effects = self._water_effects(observed, principal, availability)
        self.assertEqual(self._water_failures(effects),
                         {'effective_day_roots_registered'})

    def test_factor_water_no_peer_isolated(self):
        _, observed, principal, availability = self._water_inputs()
        observed = copy.deepcopy(observed)
        observed['visible_relations'][2] = _vis(
            'hour', '庚', '金', 'generates_me', [_pos('year', '酉', '辛')])
        effects = self._water_effects(observed, principal, availability)
        self.assertEqual(self._water_failures(effects),
                         {'visible比_present'})

    def test_factor_water_month_gate_isolated(self):
        _, observed, principal, availability = self._water_inputs()
        principal = dict(principal, month_branch='丑')
        effects = self._water_effects(observed, principal, availability)
        self.assertEqual(self._water_failures(effects),
                         {'reviewed_same_element_month_zi'})

    def _metal_inputs(self, day_master='庚'):
        pillars = [{'name': n, 'stem': {'value': s}} for n, s in
                   (('year', '戊'), ('month', '辛'), ('day', day_master),
                    ('hour', '辛' if day_master == '庚' else '庚'))]
        peer = '辛' if day_master == '庚' else '庚'
        observed = {
            'day_master': day_master,
            'visible_relations': [
                _vis('year', '戊', '土', 'generates_me',
                     [_pos('year', '戌', '戊', True)]),
                _vis('month', '辛', '金', 'same_element',
                     [_pos('month', '酉', '辛', True)]),
                _vis('hour', peer, '金', 'same_element',
                     [_pos('month', '酉', '辛')])],
            'hidden_relations': [
                {'fact': {'pillar': 'year', 'stem': '戊',
                          'element': '土', 'relation': 'generates_me'}},
                {'fact': {'pillar': 'year', 'stem': '辛',
                          'element': '金', 'relation': 'same_element'}},
                {'fact': {'pillar': 'month', 'stem': '辛',
                          'element': '金', 'relation': 'same_element'}},
                {'fact': {'pillar': 'day', 'stem': day_master,
                          'element': '金', 'relation': 'same_element'}},
                {'fact': {'pillar': 'hour', 'stem': '辛',
                          'element': '金', 'relation': 'same_element'}}]}
        principal = {'month_branch': '酉', 'status': 'reviewed_relation',
                     'relation': 'same_element', 'principal_qi': '辛',
                     'day_master': day_master}
        if day_master == '庚':
            roots = [_root(0, 'month', '酉', '辛'),
                     _root(1, 'day', '申', '庚')]
        else:
            roots = [_root(0, 'month', '酉', '辛'),
                     _root(1, 'day', '酉', '辛')]
        availability = {'day_master': day_master, 'root_presence': True,
                        'roots': roots}
        return pillars, observed, principal, availability

    def _metal_effects(self, day_master, observed, principal, availability):
        pillars, _, _, _ = self._metal_inputs(day_master)
        return action_effects(pillars, observed=observed,
                              relations=_relations(),
                              principal=principal,
                              availability=availability)

    def _metal_failures(self, effects):
        cond = effects['pure_support_metal_scope_conditions']
        return {k for k, v in cond.items() if not v}

    def test_factor_metal_baseline_only_earth_gap_fails(self):
        # Every metal condition except all_visible_have_registered_
        # roots can hold simultaneously. The sole blocker is the
        # registered earth-root gap: the earth resource stem (Wu) has
        # no settled root set in the sealed policy or the S1 register,
        # so its (physically real) Xu position never counts. This pins
        # METAL_YOU_SATISFIABILITY channel 3 as intended behaviour.
        _, observed, principal, availability = self._metal_inputs()
        effects = self._metal_effects('庚', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots'})
        self.assertFalse(effects['pure_support_metal_scope_met'])

    def test_factor_metal_earth_gap_cause_isolated(self):
        # Removing the earth stem flips all_visible to true (and the
        # resource condition to false): the gap is exactly the earth
        # stem's eligibility, nothing else in the condition.
        _, observed, principal, availability = self._metal_inputs()
        observed = copy.deepcopy(observed)
        del observed['visible_relations'][0]
        effects = self._metal_effects('庚', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'visible印_present'})

    def test_factor_metal_month_gate_isolated(self):
        _, observed, principal, availability = self._metal_inputs()
        principal = dict(principal, month_branch='申')
        effects = self._metal_effects('庚', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots',
                          'reviewed_same_element_month_you'})

    def test_factor_metal_clashed_root_isolated(self):
        _, observed, principal, availability = self._metal_inputs()
        availability = copy.deepcopy(availability)
        availability['roots'][0]['branch_relations'] = [
            {'branch': '卯', 'kind': 'branch_six_clashes'}]
        effects = self._metal_effects('庚', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots',
                          'effective_day_roots_registered'})

    def test_factor_metal_no_peer_isolated(self):
        _, observed, principal, availability = self._metal_inputs()
        observed = copy.deepcopy(observed)
        for row in observed['visible_relations'][1:]:
            row['fact']['relation'] = 'generates_me'
        effects = self._metal_effects('庚', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots',
                          'visible比_present'})

    def test_factor_metal_pending_root_isolated(self):
        _, observed, principal, availability = self._metal_inputs('辛')
        availability = copy.deepcopy(availability)
        # Xin at Shen: conflicted_pending cell (xin-changsheng branch),
        # clean synthetic fact -- the grade alone blocks.
        availability['roots'].append(_root(2, 'hour', '申', '庚'))
        effects = self._metal_effects('辛', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots',
                          'effective_day_roots_registered'})

    def test_factor_metal_light_root_isolated(self):
        _, observed, principal, availability = self._metal_inputs('辛')
        availability = copy.deepcopy(availability)
        # Xin at Xu: light_listed_conflicted cell.
        availability['roots'].append(_root(2, 'hour', '戌', '辛'))
        effects = self._metal_effects('辛', observed, principal,
                                      availability)
        self.assertEqual(self._metal_failures(effects),
                         {'all_visible_have_registered_roots',
                          'effective_day_roots_registered'})


class WholeDomainScanTests(unittest.TestCase):
    def test_new_predicates_fire_only_where_registered(self):
        births = [c['source_birth'] for c in CASES.values()]
        births += [c['source_birth'] for c in WOOD.values()]
        births += [c['source_birth'] for c in BING.values()]
        births += [c['source_birth'] for c in FIRE.values()]
        fired = {p: [] for p in NEW_PREDICATES}
        for birth in births:
            _, result, _ = run_birth(birth)
            assessment = result['strength_assessment']
            why = assessment['why_not_indeterminate']
            if why and why.get('sufficient_predicate') in NEW_PREDICATES:
                fired[why['sufficient_predicate']].append(birth)
                # The new forms only ever yield strong.
                self.assertEqual(assessment['classification'], 'strong')
        self.assertEqual(
            fired['pure_generating_support_water'],
            [CASES['tj0112-s2-water-positive-gui']['source_birth']])
        # Constructively unsatisfiable on real charts (registered
        # proof): the metal predicate fires for no chart in the domain.
        self.assertEqual(fired['pure_support_metal'], [])

    def test_regression_verdicts_unchanged(self):
        _, result, _ = run_birth(
            WOOD['tj0112-hai-positive-zhongqi-root']['source_birth'])
        why = result['strength_assessment']['why_not_indeterminate']
        self.assertEqual(why['sufficient_predicate'],
                         'pure_generating_support')
        self.assertEqual(result['strength_assessment']['classification'],
                         'strong')
        _, result, _ = run_birth(BING['tj0112-bingwu-positive']
                                 ['source_birth'])
        why = result['strength_assessment']['why_not_indeterminate']
        self.assertEqual(why['sufficient_predicate'],
                         'commanding_visible_support')
        self.assertEqual(result['strength_assessment']['classification'],
                         'strong')


if __name__ == '__main__':
    unittest.main()
