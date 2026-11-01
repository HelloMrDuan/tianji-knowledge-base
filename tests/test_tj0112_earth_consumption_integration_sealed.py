"""TJ-011.2 earth-root consumption integration (E0355): sealed
checks. Runs in the offline assembled acceptance only (NOT public
CI, same partition rule as the S2 suite).

Two layers:

- Factor layer (synthetic factor inputs, labelled factor-level,
  following the S2 FactorLayerTests precedent): the exhaustive
  24-cell pin -- for each earth stem (Wu/Ji) and each of the twelve
  branches, a visible earth stem whose only root position sits in
  that branch counts toward all_visible_have_registered_roots IFF
  the cell is one of the contract's two whitelist cells (Wu x Si,
  Ji x Wu). This is the anti-mechanical-integration pin: the eight
  structural_present_ungraded cells would pass an exclusion-shaped
  rule and must NOT count; the eight conflicted_pending cells stay
  blocked; the six no_root cells never count. The same whitelist is
  verified through the water scope's shared function, and an earth
  day master gains no register-effective root (the effective
  caliber is not wired).

- Real-chart layer: the four E0355 Golden cases in
  tests/golden_tj0112_s2_metal_water.json (positive Wu, positive
  Ji, ungraded-blocked, pending-blocked), each a REAL birth datetime
  executed through the reviewed calendar path (engine.execute) with
  a hand-derived eight-condition table for the metal scope. The
  metal predicate still fires for none of them (the form stays
  constructively unsatisfiable on real charts; channels one/two).
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_action_conditions import action_effects
from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.engine import execute

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0112_s2_metal_water.json').read_text('utf-8'))
CASES = {c['id']: c for c in GOLDEN['cases']}
E0355_CASES = ('tj0112-e0355-metal-earth-wu-listed',
               'tj0112-e0355-metal-earth-ji-listed',
               'tj0112-e0355-metal-earth-wu-ungraded',
               'tj0112-e0355-metal-earth-wu-pending')
WHITELIST = {('戊', '巳'), ('己', '午')}
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'


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


def _effects(day_master, visible, month_branch, roots):
    pillars = [{'name': n, 'stem': {'value': s}} for n, s in
               (('year', '辛'), ('month', '庚'), ('day', day_master),
                ('hour', '壬'))]
    observed = {'day_master': day_master,
                'visible_relations': visible,
                'hidden_relations': []}
    principal = {'month_branch': month_branch,
                 'status': 'reviewed_relation',
                 'relation': 'same_element',
                 'principal_qi': '辛' if month_branch == '酉' else '癸',
                 'day_master': day_master}
    availability = {'day_master': day_master, 'root_presence': True,
                    'roots': roots}
    return action_effects(pillars, observed=observed,
                          relations=_relations(),
                          principal=principal,
                          availability=availability)


def _metal_all_visible(stem, branch):
    visible = [
        _vis('year', stem, '土', 'generates_me',
             [_pos('year', branch, stem)]),
        _vis('month', '辛', '金', 'same_element',
             [_pos('month', '酉', '辛', True)])]
    effects = _effects('庚', visible, '酉',
                       [_root(0, 'month', '酉', '辛'),
                        _root(1, 'day', '申', '庚')])
    return effects['pure_support_metal_scope_conditions'][
        'all_visible_have_registered_roots']


class FactorExhaustiveWhitelistTests(unittest.TestCase):
    def test_all_24_cells_match_the_whitelist_exactly(self):
        for stem in ('戊', '己'):
            for branch in BRANCHES:
                self.assertEqual(
                    _metal_all_visible(stem, branch),
                    (stem, branch) in WHITELIST,
                    f'{stem}×{branch}')

    def test_multiple_positions_one_whitelisted_is_enough(self):
        visible = [
            _vis('year', '戊', '土', 'generates_me',
                 [_pos('year', '辰', '戊'), _pos('day', '巳', '戊')]),
            _vis('month', '辛', '金', 'same_element',
                 [_pos('month', '酉', '辛', True)])]
        effects = _effects('庚', visible, '酉',
                           [_root(0, 'month', '酉', '辛'),
                            _root(1, 'day', '申', '庚')])
        self.assertTrue(effects['pure_support_metal_scope_conditions']
                        ['all_visible_have_registered_roots'])

    def test_pending_positions_never_count_no_branch_fallback(self):
        for branch in ('寅', '申'):
            visible = [
                _vis('year', '戊', '土', 'generates_me',
                     [_pos('day', branch, '戊')]),
                _vis('month', '辛', '金', 'same_element',
                     [_pos('month', '酉', '辛', True)])]
            effects = _effects('庚', visible, '酉',
                               [_root(0, 'month', '酉', '辛'),
                                _root(1, 'day', '申', '庚')])
            self.assertFalse(
                effects['pure_support_metal_scope_conditions']
                ['all_visible_have_registered_roots'], branch)

    def test_no_position_never_counts(self):
        visible = [
            _vis('year', '己', '土', 'generates_me', []),
            _vis('month', '辛', '金', 'same_element',
                 [_pos('month', '酉', '辛', True)])]
        effects = _effects('庚', visible, '酉',
                           [_root(0, 'month', '酉', '辛'),
                            _root(1, 'day', '申', '庚')])
        self.assertFalse(effects['pure_support_metal_scope_conditions']
                         ['all_visible_have_registered_roots'])

    def test_water_scope_shares_the_same_whitelist(self):
        # The water form shares registered_eligible; under a water
        # day master the condition value follows the same whitelist
        # (the scope itself stays unreachable for earth stems through
        # the support-only veto, which this factor input bypasses by
        # construction -- the pin is on the shared function only).
        for stem, branch, expect in (('戊', '巳', True),
                                     ('戊', '辰', False),
                                     ('己', '午', True),
                                     ('己', '未', False)):
            visible = [
                _vis('year', stem, '土', 'controls_me',
                     [_pos('year', branch, stem)]),
                _vis('month', '辛', '金', 'generates_me',
                     [_pos('month', '酉', '辛', True)])]
            effects = _effects('癸', visible, '子',
                               [_root(0, 'month', '子', '癸')])
            self.assertEqual(
                effects['pure_generating_support_water_scope_'
                        'conditions']
                ['all_visible_have_registered_roots'], expect,
                f'{stem}×{branch}')

    def test_earth_day_master_gains_no_effective_root(self):
        # Precondition 5: the day-root effectiveness path is not
        # wired for earth. An earth day master whose root sits in
        # its own whitelist cell (Wu at Si) still yields no
        # register-effective root in either S2 scope.
        visible = [
            _vis('year', '辛', '金', 'generates_me',
                 [_pos('month', '酉', '辛', True)])]
        effects = _effects('戊', visible, '酉',
                           [_root(0, 'day', '巳', '戊')])
        self.assertFalse(effects['pure_support_metal_scope_conditions']
                         ['effective_day_roots_registered'])
        self.assertFalse(
            effects['pure_generating_support_water_scope_conditions']
            ['effective_day_roots_registered'])
        self.assertFalse(effects['pure_support_metal_scope_met'])
        self.assertFalse(
            effects['pure_generating_support_water_scope_met'])


class RealChartGoldenTests(unittest.TestCase):
    def run_case(self, case_id):
        case = CASES[case_id]
        out = execute('bazi', {'value': case['source_birth'],
                               'strength_variant': ADJUDICATION_VARIANT},
                      allow_research=True)
        result = out['result']
        pillars = [p['stem']['value'] + p['branch']['value']
                   for p in result['pillars']]
        self.assertEqual(pillars, case['expected_pillars'])
        effects = result['action_effects']
        self.assertEqual(
            effects['pure_support_metal_scope_conditions'],
            case['expect']['scope_conditions'])
        self.assertFalse(effects['pure_support_metal_scope_met'])
        assessment = result['strength_assessment']
        self.assertEqual(assessment['classification'],
                         case['expect']['classification'])
        self.assertIsNone(assessment['why_not_indeterminate'])
        return result

    def test_wu_listed_positive(self):
        result = self.run_case('tj0112-e0355-metal-earth-wu-listed')
        # Both earth stems pass ONLY through the whitelist: their
        # shared root-presence branches are {Chen, Wu, Si, Chou};
        # Wu counts via Si (listed), Ji via Wu (listed); the
        # pending and ungraded cells in the same set never count.
        self.assertTrue(result['action_effects']
                        ['pure_support_metal_scope_conditions']
                        ['all_visible_have_registered_roots'])

    def test_ji_listed_positive(self):
        self.run_case('tj0112-e0355-metal-earth-ji-listed')

    def test_wu_ungraded_blocked(self):
        result = self.run_case('tj0112-e0355-metal-earth-wu-ungraded')
        # The sole blocking stem is Wu, whose ONLY root position is
        # Chen (structural_present_ungraded) -- the cell an
        # exclusion-shaped wiring would have miscounted as eligible.
        # Jia (Mao policy position) and Xin (You, listed) both pass.
        self.assertFalse(result['action_effects']
                         ['pure_support_metal_scope_conditions']
                         ['all_visible_have_registered_roots'])

    def test_wu_pending_blocked(self):
        self.run_case('tj0112-e0355-metal-earth-wu-pending')


if __name__ == '__main__':
    unittest.main()
