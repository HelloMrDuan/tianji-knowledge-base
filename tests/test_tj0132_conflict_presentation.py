"""TJ-013.2 phase 1 (cross-system conflict presentation) PUBLIC tests.

Public-safe by construction, following the tiaohou/bingyao public
companion precedent: the golden transcription is pinned against the
module constants, and the tiaohou/bingyao statements are produced by
the REAL pure lookups from golden-recorded facts (real birth instants
-> real pillars via the calendar path, verified in the sealed suite).
The strength statement cannot be produced in a public checkout (the
bounded adjudication needs the sealed Canonical foundations), so the
public tests feed the presenter a clearly-marked synthetic strength
statement carrying only the golden-recorded, hand-derived expectation
(classification + decision_status); the REAL strength verdict for
every golden chart is verified through chart() in
test_tj0132_conflict_presentation_sealed.py. Do not cite this file as
evidence that any golden chart's strength verdict was executed.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_bingyao import VARIANT as BINGYAO_VARIANT, bingyao_lookup
from tianji_kb.bazi_conflict_presentation import (
    ABSENT_REASONS, BUILT_SYSTEMS, LIMITATIONS, RELATION_DEFINITIONS,
    STATUS_DEFINITIONS, VARIANT, conflict_presentation)
from tianji_kb.bazi_tiaohou import VARIANT as TIAOHOU_VARIANT, tiaohou_lookup
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart as bazi_chart
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0132_conflict_presentation.json').read_text('utf-8'))
CASES = {case['id']: case for case in GOLDEN['cases']}

# No unified useful-god / recommendation / scoring / verdict key may
# appear anywhere in a presentation output (scan by KEY, mirroring the
# bingyao public suite's VERDICT_KEYS precedent; the one legitimate
# determination key is asserted to be None separately).
FORBIDDEN_KEYS = {
    'score', 'scores', 'rating', 'weight', 'weights', 'useful_god',
    'favorable', 'favourable', 'recommended', 'recommendation',
    'verdict', 'combined_verdict', 'final_verdict', 'resolution',
    'resolved_choice', 'preference',
    '喜用神', '用神', '喜神', '忌神', '吉凶', '评分', '推荐', '权重', '裁决',
}


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


def _tiaohou_statement(case):
    facts = case['facts']['tiaohou']
    hidden = [facts['hidden_stems'][pillar]
              for pillar in ('year', 'month', 'day', 'hour')]
    return tiaohou_lookup(case['day_master'], facts['month_branch'],
                          facts['visible_stems'], hidden)


def _bingyao_statement(case):
    return bingyao_lookup(case['day_master'],
                          case['facts']['bingyao']['visible_gods'])


def _strength_statement(case):
    """Synthetic strength statement input for the public presenter tests.

    Carries ONLY the golden-recorded hand-derived expectation; the real
    verdict is executed and verified in the sealed suite."""
    expected = case['expected_strength']
    return {'variant': ADJUDICATION_VARIANT,
            'classification': expected['classification'],
            'decision_status': expected['decision_status'],
            'input_kind': 'synthetic_strength_statement_for_public_presenter_tests',
            'research_only': True, 'public_enabled': False,
            'ai_enabled': False}


def _present(case):
    return conflict_presentation(_tiaohou_statement(case),
                                 _bingyao_statement(case),
                                 _strength_statement(case))


class GoldenTranscriptionTests(unittest.TestCase):
    def test_golden_matches_module_constants(self):
        self.assertEqual(GOLDEN['variant'], 'xiyong-conflict-presentation-v1')
        self.assertEqual(GOLDEN['variant'], VARIANT)
        self.assertEqual(len(GOLDEN['cases']), 5)
        self.assertEqual({case['focus'] for case in GOLDEN['cases']},
                         {'support', 'conflict', 'incomparable', 'abstain',
                          'absent'})

    def test_definitions_cover_every_relation_and_status(self):
        self.assertEqual(set(RELATION_DEFINITIONS),
                         {'support', 'conflict', 'pivot_overlap',
                          'one_sided', 'incomparable'})
        self.assertEqual(set(STATUS_DEFINITIONS),
                         {'presented_with_conflicts', 'presented_partial',
                          'presented_no_conflict'})
        self.assertEqual(set(ABSENT_REASONS),
                         {'fuyi', 'pattern_useful_god'})
        self.assertEqual(set(BUILT_SYSTEMS),
                         {'tiaohou', 'bingyao', 'strength'})
        self.assertTrue(all(LIMITATIONS))


class PresentationGoldenTests(unittest.TestCase):
    def test_every_case_matches_hand_derived_expectation(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = _present(case)
                expected = case['expected_presentation']
                self.assertEqual(out['variant'], VARIANT)
                self.assertEqual(out['layer'], 'presentation')
                self.assertIsNone(out['determination'])
                self.assertEqual(out['status'], expected['status'])
                self.assertEqual(out['status_definition'],
                                 STATUS_DEFINITIONS[expected['status']])
                self.assertEqual(out['day_master'], case['day_master'])
                systems = {r['system']: r for r in out['systems']}
                self.assertEqual([r['system'] for r in out['systems']],
                                 ['tiaohou', 'bingyao', 'strength', 'fuyi',
                                  'pattern_useful_god'])
                for system, status in expected['systems'].items():
                    self.assertEqual(systems[system]['status'], status,
                                     f'{case["id"]}:{system}')
                relations = {r['stem']: r['kind'] for r in out['relations']
                             if r['stem'] is not None}
                self.assertEqual(relations, expected['relations'])
                context = [r for r in out['relations']
                           if r['kind'] == 'incomparable']
                self.assertEqual(len(context), 1)
                self.assertEqual(context[0]['system'], 'strength')
                self.assertEqual(context[0]['classification'],
                                 case['expected_strength']['classification'])

    def test_statements_carried_verbatim_and_inputs_not_mutated(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                tiaohou = _tiaohou_statement(case)
                bingyao = _bingyao_statement(case)
                strength = _strength_statement(case)
                snapshot = copy.deepcopy((tiaohou, bingyao, strength))
                out = conflict_presentation(tiaohou, bingyao, strength)
                self.assertEqual((tiaohou, bingyao, strength), snapshot)
                systems = {r['system']: r for r in out['systems']}
                self.assertEqual(systems['tiaohou']['statement'], tiaohou)
                self.assertEqual(systems['bingyao']['statement'], bingyao)
                self.assertEqual(systems['strength']['statement'], strength)
                # The carried copies are deep copies: editing the output
                # must not reach back into the caller's statements.
                systems['tiaohou']['statement']['status'] = 'tampered'
                self.assertEqual(tiaohou['status'], snapshot[0]['status'])

    def test_absent_systems_explicit_in_every_case(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = _present(case)
                systems = {r['system']: r for r in out['systems']}
                for system in ('fuyi', 'pattern_useful_god'):
                    record = systems[system]
                    self.assertEqual(record['status'], 'absent')
                    self.assertIsNone(record['variant'])
                    self.assertIsNone(record['statement'])
                    self.assertEqual(record['absent_reason'],
                                     ABSENT_REASONS[system])

    def test_abstention_never_degrades_other_statements(self):
        case = CASES['abstain-three-states-coexist']
        out = _present(case)
        systems = {r['system']: r for r in out['systems']}
        # The bingyao abstention leaves the tiaohou statement byte-equal
        # to the raw lookup output, and the abstained bingyao names no
        # stem even though its diagnostic subject row mentions 庚/壬.
        self.assertEqual(systems['tiaohou']['statement'],
                         _tiaohou_statement(case))
        self.assertEqual(systems['bingyao']['abstain_reason'],
                         'peer_god_not_visible')
        relations = {r['stem']: r for r in out['relations']
                     if r['stem'] is not None}
        self.assertEqual(set(relations), {'壬', '庚'})
        for relation in relations.values():
            self.assertEqual(relation['kind'], 'one_sided')
            self.assertIsNone(relation['bingyao'])

    def test_conflict_is_presented_not_resolved(self):
        case = CASES['conflict-first-pick-is-disease']
        out = _present(case)
        self.assertEqual(out['status'], 'presented_with_conflicts')
        self.assertIsNone(out['determination'])
        conflict = [r for r in out['relations'] if r['kind'] == 'conflict']
        self.assertEqual(len(conflict), 1)
        self.assertEqual(conflict[0]['stem'], '癸')
        self.assertEqual(conflict[0]['tiaohou']['role'], 'primary_pick')
        self.assertEqual(conflict[0]['tiaohou']['order'], 1)
        self.assertEqual(conflict[0]['bingyao']['role'], 'disease')
        refs = {ref['system']: ref for ref in conflict[0]['evidence_refs']}
        self.assertEqual(refs['tiaohou']['variant'], TIAOHOU_VARIANT)
        self.assertEqual(refs['bingyao']['variant'], BINGYAO_VARIANT)
        self.assertEqual(refs['bingyao']['rule_id'],
                         'shenfeng.wealth_peer_officer')

    def test_support_relation_carries_both_evidence_refs(self):
        case = CASES['support-first-pick-is-medicine']
        out = _present(case)
        support = [r for r in out['relations'] if r['kind'] == 'support']
        self.assertEqual(len(support), 1)
        self.assertEqual(support[0]['stem'], '庚')
        self.assertEqual(support[0]['bingyao']['role'], 'medicine')
        self.assertEqual({ref['system'] for ref in support[0]['evidence_refs']},
                         {'tiaohou', 'bingyao'})

    def test_no_unified_useful_god_or_verdict_keys_anywhere(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = _present(case)
                self.assertEqual(set(_all_keys(out)) & FORBIDDEN_KEYS, set())
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])

    def test_presented_no_conflict_branch_classifier_logic(self):
        # CLASSIFIER-LOGIC ONLY, not a chart claim: on currently reviewed
        # scopes this top status is unreachable for a real chart (whenever
        # bingyao triggers, the strength predicates abstain — see the
        # module docstring's coverage note). Feed the support case's real
        # lookup statements with a synthetic adjudicated strength
        # statement to pin the branch so it cannot silently rot.
        case = CASES['support-first-pick-is-medicine']
        strength = _strength_statement(case)
        strength['classification'] = 'strong'
        strength['decision_status'] = 'reviewed_sufficient_rule_matched'
        out = conflict_presentation(_tiaohou_statement(case),
                                    _bingyao_statement(case), strength)
        self.assertEqual(out['status'], 'presented_no_conflict')


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self.case = CASES['support-first-pick-is-medicine']
        self.tiaohou = _tiaohou_statement(self.case)
        self.bingyao = _bingyao_statement(self.case)
        self.strength = _strength_statement(self.case)

    def test_mixed_chart_statements_rejected(self):
        other = _bingyao_statement(CASES['conflict-first-pick-is-disease'])
        with self.assertRaisesRegex(ValueError, 'one chart'):
            conflict_presentation(self.tiaohou, other, self.strength)

    def test_forged_public_statement_rejected(self):
        forged = copy.deepcopy(self.tiaohou)
        forged['public_enabled'] = True
        with self.assertRaisesRegex(ValueError, 'research-only'):
            conflict_presentation(forged, self.bingyao, self.strength)

    def test_wrong_variants_rejected(self):
        for slot in ('tiaohou', 'bingyao', 'strength'):
            forged = {'tiaohou': copy.deepcopy(self.tiaohou),
                      'bingyao': copy.deepcopy(self.bingyao),
                      'strength': copy.deepcopy(self.strength)}
            forged[slot]['variant'] = 'forged-v9'
            with self.subTest(slot=slot):
                with self.assertRaisesRegex(ValueError, 'variant'):
                    conflict_presentation(forged['tiaohou'], forged['bingyao'],
                                          forged['strength'])
        with self.assertRaisesRegex(ValueError, 'variant'):
            conflict_presentation(self.tiaohou, self.bingyao, self.strength,
                                  presentation_variant='forged-v9')

    def test_bingyao_determination_rejected(self):
        forged = copy.deepcopy(self.bingyao)
        forged['determination'] = 'disease_confirmed'
        with self.assertRaisesRegex(ValueError, 'determination'):
            conflict_presentation(self.tiaohou, forged, self.strength)

    def test_unknown_statement_status_rejected(self):
        forged = copy.deepcopy(self.tiaohou)
        forged['status'] = 'resolved'
        with self.assertRaisesRegex(ValueError, 'tiaohou statement status'):
            conflict_presentation(forged, self.bingyao, self.strength)
        forged_strength = copy.deepcopy(self.strength)
        forged_strength['classification'] = 'very_strong'
        with self.assertRaisesRegex(ValueError, 'strength statement'):
            conflict_presentation(self.tiaohou, self.bingyao, forged_strength)

    def test_missing_statements_rejected(self):
        with self.assertRaisesRegex(ValueError, 'statement object'):
            conflict_presentation(None, self.bingyao, self.strength)


class WiringGateTests(unittest.TestCase):
    def test_engine_requires_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'conflict_variant': VARIANT},
                    allow_research=False)

    def test_chart_requires_all_three_variants_together(self):
        # Pre-computation validation only: these calls are rejected
        # before any chart data is touched, so they run in a public
        # checkout (the full combination is sealed-suite territory).
        pillars = CASES['support-first-pick-is-medicine']['pillars']
        with self.assertRaisesRegex(ValueError, 'Unsupported conflict'):
            bazi_chart(*pillars, conflict_variant='forged-v9')
        with self.assertRaisesRegex(ValueError, 'requires the adjudication'):
            bazi_chart(*pillars, conflict_variant=VARIANT)
        with self.assertRaisesRegex(ValueError, 'requires the adjudication'):
            bazi_chart(*pillars, conflict_variant=VARIANT,
                       strength_variant=ADJUDICATION_VARIANT,
                       tiaohou_variant=TIAOHOU_VARIANT)

    def test_projection_strips_presentation_from_public_answers(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'conflict_presentation': {'status': 'x'}},
            'chart': {'conflict_presentation': {'status': 'x'}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        projected = project_execution(copy.deepcopy(payload))
        self.assertNotIn('conflict_presentation',
                         json.dumps(projected, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
