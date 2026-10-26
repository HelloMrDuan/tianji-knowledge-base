"""TJ-013.3 phase 1 (xiyong readable hints) PUBLIC tests.

Public-safe by construction, following the TJ-013.2 public companion
precedent: the golden transcription is pinned against hand-written
expectations, and the tiaohou/bingyao statements are produced by the
REAL pure lookups from golden-recorded facts (real birth instants ->
real pillars via the calendar path, verified in the sealed suite).
The strength statement cannot be produced in a public checkout (the
bounded adjudication needs the sealed Canonical foundations), so the
public tests feed the renderer a clearly-marked synthetic strength
statement carrying only the golden-recorded, hand-derived expectation
(classification, predicate, condition keys); the REAL strength verdict
and the full chart() wiring for every golden chart are verified in
test_tj0133_readable_hints_sealed.py. Do not cite this file as evidence
that any golden chart's strength verdict was executed.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_adjudication import ADJUDICATION_VARIANT
from tianji_kb.bazi_bingyao import VARIANT as BINGYAO_VARIANT, bingyao_lookup
from tianji_kb.bazi_conflict_presentation import (
    VARIANT as CONFLICT_VARIANT, conflict_presentation)
from tianji_kb.bazi_tiaohou import VARIANT as TIAOHOU_VARIANT, tiaohou_lookup
from tianji_kb.bazi_xiyong_readable import (
    ABSENT_LINES, BINGYAO_HEADER, CONDITION_LABELS, LIMITATIONS,
    PREDICATE_LABELS, VARIANT, readable_hints)
from tianji_kb.engine import execute
from tianji_kb.operations.bazi_chart import chart as bazi_chart
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj0133_readable_hints.json').read_text('utf-8'))
CASES = {case['id']: case for case in GOLDEN['cases']}

STEMS = set('甲乙丙丁戊己庚辛壬癸')
# Assertive fortune/reality-prediction vocabulary and recommendation
# vocabulary: zero occurrences allowed in any rendered line. (Negated
# honesty statements in the templates are worded to avoid these
# characters entirely, so the scan needs no exceptions.)
BANNED_SUBSTRINGS = (
    '吉', '凶', '宜', '忌', '灾', '祸', '发财', '升职', '旺财', '旺夫',
    '喜用神', '宜用', '忌用', '推荐', '建议', '评分', '得分',
)
SECTION_ORDER = ['tiaohou', 'bingyao', 'strength', 'fuyi',
                 'pattern_useful_god', 'conflict_presentation']


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
    """Synthetic strength statement input for the public renderer tests.

    Carries ONLY the golden-recorded hand-derived expectation; the real
    verdict is executed and verified in the sealed suite."""
    expected = case['expected_strength']
    why = None
    if expected['sufficient_predicate'] is not None:
        # Mirror the REAL verdict shapes (see bazi_adjudication):
        # registered-rule verdicts carry only sufficient_rule; the
        # pending-registration verdict carries sufficient_predicate
        # with sufficient_rule None.
        why = {'sufficient_rule': expected['sufficient_rule'],
               'conditions': [{'condition': key, 'met': True}
                              for key in expected['conditions']],
               'all_required_conditions_verified': True}
        if expected['sufficient_rule'] is None:
            why['sufficient_predicate'] = expected['sufficient_predicate']
    return {'variant': ADJUDICATION_VARIANT,
            'classification': expected['classification'],
            'decision_status': expected['decision_status'],
            'why_not_indeterminate': why,
            'input_kind': 'synthetic_strength_statement_for_public_renderer_tests',
            'research_only': True, 'public_enabled': False,
            'ai_enabled': False}


def _render(case):
    tiaohou = _tiaohou_statement(case)
    bingyao = _bingyao_statement(case)
    strength = _strength_statement(case)
    presentation = conflict_presentation(tiaohou, bingyao, strength)
    return readable_hints(tiaohou, bingyao, strength, presentation)


def _fact_stems(case):
    """Stems named by the input fact objects themselves.

    The universe is the four input objects' fact fields: the chart's
    stems (visible and hidden), the bingyao visible gods, and the
    tiaohou entry's own sequence stems — an entry pick is a fact of
    the reviewed entry statement even when the chart does not contain
    the stem at all (presence 'absent'), and the presenter names it
    too. Anything beyond this universe in a line is a renderer
    invention and fails the closure test."""
    stems = {case['day_master']}
    facts = case['facts']
    stems.update(facts['tiaohou']['visible_stems'])
    for hidden in facts['tiaohou']['hidden_stems'].values():
        stems.update(hidden)
    for god in facts['bingyao']['visible_gods']:
        stems.add(god['stem'])
    tiaohou = _tiaohou_statement(case)
    for item in tiaohou.get('sequence') or []:
        stems.add(item['stem'])
    for branch in tiaohou.get('branches') or []:
        for item in branch.get('sequence') or []:
            stems.add(item['stem'])
    return stems


class GoldenTranscriptionTests(unittest.TestCase):
    def test_golden_matches_module_constants(self):
        self.assertEqual(GOLDEN['variant'], 'xiyong-readable-hints-v1')
        self.assertEqual(GOLDEN['variant'], VARIANT)
        self.assertEqual(len(GOLDEN['cases']), 9)
        self.assertEqual({case['focus'] for case in GOLDEN['cases']},
                         {'support', 'conflict', 'incomparable', 'abstain',
                          'absent', 'weak', 'pivot', 'pair2pos',
                          'pair2nomed'})

    def test_every_expected_line_carries_fact_sources(self):
        for case in GOLDEN['cases']:
            for section in case['expected_sections'].values():
                self.assertTrue(section['lines'])
                for line in section['lines']:
                    self.assertTrue(line['text'])
                    self.assertIsInstance(line['fact_sources'], list)
                    self.assertTrue(line['fact_sources'],
                                    f"{case['id']}: {line['text']}")

    def test_template_tables_cover_golden_vocabulary(self):
        self.assertEqual(set(PREDICATE_LABELS),
                         {'pure_support', 'pure_generating_support',
                          'isolated_control'})
        for case in GOLDEN['cases']:
            for key in case['expected_strength']['conditions']:
                self.assertIn(key, CONDITION_LABELS)
        for label in list(CONDITION_LABELS.values()) \
                + list(PREDICATE_LABELS.values()):
            self.assertEqual(set(label) & STEMS, set())
            for banned in BANNED_SUBSTRINGS:
                self.assertNotIn(banned, label)


class RenderingGoldenTests(unittest.TestCase):
    def test_every_case_matches_hand_written_expectation(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                out = _render(case)
                self.assertEqual(out['variant'], VARIANT)
                self.assertEqual(out['layer'], 'readable_hints')
                self.assertEqual(out['day_master'], case['day_master'])
                self.assertEqual([s['system'] for s in out['sections']],
                                 SECTION_ORDER)
                self.assertTrue(out['research_only'])
                self.assertFalse(out['public_enabled'])
                self.assertFalse(out['ai_enabled'])
                self.assertEqual(out['limitations'], list(LIMITATIONS))
                sections = {s['system']: s for s in out['sections']}
                for system, expected in case['expected_sections'].items():
                    self.assertEqual(sections[system]['status'],
                                     expected['status'],
                                     f"{case['id']}:{system}")
                    self.assertEqual(
                        [line for line in sections[system]['lines']],
                        [line['text'] for line in expected['lines']],
                        f"{case['id']}:{system}")

    def test_rendering_is_deterministic_and_inputs_not_mutated(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                tiaohou = _tiaohou_statement(case)
                bingyao = _bingyao_statement(case)
                strength = _strength_statement(case)
                presentation = conflict_presentation(tiaohou, bingyao,
                                                     strength)
                snapshot = copy.deepcopy(
                    (tiaohou, bingyao, strength, presentation))
                first = readable_hints(tiaohou, bingyao, strength,
                                       presentation)
                second = readable_hints(tiaohou, bingyao, strength,
                                        presentation)
                self.assertEqual(first, second)
                self.assertEqual((tiaohou, bingyao, strength, presentation),
                                 snapshot)


class FactClosureAndHonestyTests(unittest.TestCase):
    def test_line_stems_come_only_from_input_facts(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                allowed = _fact_stems(case)
                out = _render(case)
                for section in out['sections']:
                    for line in section['lines']:
                        self.assertLessEqual(set(line) & STEMS, allowed,
                                             f"{case['id']}: {line}")

    def test_no_banned_vocabulary_anywhere(self):
        texts = list(LIMITATIONS) + [BINGYAO_HEADER]
        for case in GOLDEN['cases']:
            out = _render(case)
            for section in out['sections']:
                texts.extend(section['lines'])
        for text in texts:
            for banned in BANNED_SUBSTRINGS:
                self.assertNotIn(banned, text)

    def test_abstain_and_absent_lines_are_pinned(self):
        case = CASES['abstain-three-states-coexist']
        out = _render(case)
        sections = {s['system']: s for s in out['sections']}
        self.assertEqual(sections['strength']['lines'], [
            '旺衰裁定体系在本盘未表态：已审充分谓词均未命中，旺衰未裁定；'
            '未裁定不表示中和，也不表示偏强或偏弱。'])
        for case in GOLDEN['cases']:
            out = _render(case)
            sections = {s['system']: s for s in out['sections']}
            self.assertEqual(sections['fuyi']['lines'],
                             [ABSENT_LINES['fuyi']])
            self.assertEqual(sections['pattern_useful_god']['lines'],
                             [ABSENT_LINES['pattern_useful_god']])
            # Pair-2 relations are never rendered: every stem relation
            # line in the conflict section is backed by a pair-1 named
            # stem or by a tiaohou pick (golden expectations pin this
            # per case; here the scope line must always disclose it).
            conflict_lines = sections['conflict_presentation']['lines']
            self.assertTrue(any('不单独做关系分类' in line
                                for line in conflict_lines))
            self.assertEqual(conflict_lines[-1],
                             '各体系陈述并列呈现，系统不作统一裁定。')

    def test_efficacy_caveat_present_for_every_triggered_pair(self):
        for case in GOLDEN['cases']:
            with self.subTest(case=case['id']):
                bingyao = _bingyao_statement(case)
                triggered = sum(1 for p in bingyao['pairs']
                                if p['status'] == 'triggered')
                out = _render(case)
                sections = {s['system']: s for s in out['sections']}
                caveats = [line for line in sections['bingyao']['lines']
                           if '未给出可执行裁定' in line]
                self.assertEqual(len(caveats), triggered)


class PresentedNoConflictBranchTests(unittest.TestCase):
    def test_no_conflict_status_line_branch(self):
        # RENDERER-BRANCH LOGIC ONLY, not a chart claim: on currently
        # reviewed scopes presented_no_conflict is unreachable for a
        # real chart (TJ-013.2 coverage fact: whenever bingyao triggers,
        # the strength predicates abstain). Feed the support case's real
        # lookup statements with a synthetic adjudicated strength
        # statement so the branch cannot silently rot.
        case = CASES['support-first-pick-is-medicine']
        strength = _strength_statement(
            CASES['incomparable-strength-adjudicated'])
        tiaohou = _tiaohou_statement(case)
        bingyao = _bingyao_statement(case)
        presentation = conflict_presentation(tiaohou, bingyao, strength)
        self.assertEqual(presentation['status'], 'presented_no_conflict')
        out = readable_hints(tiaohou, bingyao, strength, presentation)
        sections = {s['system']: s for s in out['sections']}
        self.assertEqual(
            sections['conflict_presentation']['lines'][0],
            '跨体系关系呈现状态：无冲突。无 conflict；已建三体系均已陈述。')
        self.assertEqual(sections['conflict_presentation']['status'],
                         'presented_no_conflict')


class FailClosedTests(unittest.TestCase):
    def setUp(self):
        self.case = CASES['support-first-pick-is-medicine']
        self.tiaohou = _tiaohou_statement(self.case)
        self.bingyao = _bingyao_statement(self.case)
        self.strength = _strength_statement(self.case)
        self.presentation = conflict_presentation(
            self.tiaohou, self.bingyao, self.strength)

    def test_mixed_chart_statements_rejected(self):
        other = _bingyao_statement(CASES['conflict-first-pick-is-disease'])
        with self.assertRaisesRegex(ValueError, 'one chart'):
            readable_hints(self.tiaohou, other, self.strength,
                           self.presentation)

    def test_statement_not_the_presented_one_rejected(self):
        # Same day master （丙）, different chart: the presentation
        # carries the abstain case's statements, so the pivot case's
        # tiaohou statement must be refused as not-the-presented-one.
        other_tiaohou = _tiaohou_statement(CASES['pivot-subject-overlap'])
        abstain = CASES['abstain-three-states-coexist']
        presentation = conflict_presentation(
            _tiaohou_statement(abstain), _bingyao_statement(abstain),
            _strength_statement(abstain))
        with self.assertRaisesRegex(ValueError, 'presented statements'):
            readable_hints(other_tiaohou, _bingyao_statement(abstain),
                           _strength_statement(abstain), presentation)

    def test_forged_flags_and_variants_rejected(self):
        forged = copy.deepcopy(self.tiaohou)
        forged['public_enabled'] = True
        with self.assertRaisesRegex(ValueError, 'research-only'):
            readable_hints(forged, self.bingyao, self.strength,
                           self.presentation)
        forged_p = copy.deepcopy(self.presentation)
        forged_p['variant'] = 'forged-v9'
        with self.assertRaisesRegex(ValueError, 'variant'):
            readable_hints(self.tiaohou, self.bingyao, self.strength,
                           forged_p)
        with self.assertRaisesRegex(ValueError, 'variant'):
            readable_hints(self.tiaohou, self.bingyao, self.strength,
                           self.presentation, readable_variant='forged-v9')
        with self.assertRaisesRegex(ValueError, 'statement object'):
            readable_hints(None, self.bingyao, self.strength,
                           self.presentation)

    def test_tampered_presentation_rejected(self):
        forged = copy.deepcopy(self.presentation)
        forged['status_definition'] = 'tampered definition'
        with self.assertRaisesRegex(ValueError, 'status'):
            readable_hints(self.tiaohou, self.bingyao, self.strength,
                           forged)
        forged = copy.deepcopy(self.presentation)
        for relation in forged['relations']:
            if relation['kind'] == 'one_sided' \
                    and relation['stem'] == '己':
                relation['kind'] = 'support'
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            readable_hints(self.tiaohou, self.bingyao, self.strength,
                           forged)

    def test_unknown_strength_facts_rejected(self):
        # The tampered statement must be the presented one (built into
        # the presentation first), otherwise the statement-identity
        # gate fires before the renderer's own fact checks.
        case = CASES['incomparable-strength-adjudicated']
        tiaohou = _tiaohou_statement(case)
        bingyao = _bingyao_statement(case)
        tampers = (
            ('predicate', lambda s: s['why_not_indeterminate']
             .update(sufficient_predicate='guessed_strength')),
            ('conditions', lambda s: s['why_not_indeterminate']
             ['conditions'][0].update(met=False)),
            ('conditions', lambda s: s['why_not_indeterminate']
             ['conditions'][0].update(condition='unreviewed_condition')),
        )
        for pattern, tamper in tampers:
            strength = _strength_statement(case)
            tamper(strength)
            presentation = conflict_presentation(tiaohou, bingyao,
                                                 strength)
            with self.subTest(pattern=pattern):
                with self.assertRaisesRegex(ValueError, pattern):
                    readable_hints(tiaohou, bingyao, strength,
                                   presentation)

    def test_bingyao_pair_determination_rejected(self):
        # Pair-level forgery passes the presenter (it inspects only
        # the top-level determination), so the renderer's own pair
        # check is the gate under test; build the presentation from
        # the forged statement so identity checks pass first.
        forged = copy.deepcopy(self.bingyao)
        forged['pairs'][0]['determination'] = 'disease_confirmed'
        presentation = conflict_presentation(self.tiaohou, forged,
                                             self.strength)
        with self.assertRaisesRegex(ValueError, 'determination'):
            readable_hints(self.tiaohou, forged, self.strength,
                           presentation)


class WiringGateTests(unittest.TestCase):
    def test_engine_requires_research_mode(self):
        with self.assertRaisesRegex(ValueError, 'research mode'):
            execute('bazi', {'readable_variant': VARIANT},
                    allow_research=False)

    def test_chart_requires_conflict_variant_together(self):
        # Pre-computation validation only: these calls are rejected
        # before any chart data is touched, so they run in a public
        # checkout (the full combination is sealed-suite territory).
        pillars = CASES['support-first-pick-is-medicine']['pillars']
        with self.assertRaisesRegex(ValueError, 'Unsupported readable'):
            bazi_chart(*pillars, readable_variant='forged-v9')
        with self.assertRaisesRegex(ValueError,
                                    'require the conflict presentation'):
            bazi_chart(*pillars, readable_variant=VARIANT)
        with self.assertRaisesRegex(ValueError,
                                    'require the conflict presentation'):
            bazi_chart(*pillars, readable_variant=VARIANT,
                       strength_variant=ADJUDICATION_VARIANT,
                       tiaohou_variant=TIAOHOU_VARIANT,
                       bingyao_variant=BINGYAO_VARIANT)

    def test_projection_strips_hints_from_public_answers(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'readable_hints': {'sections': []}},
            'chart': {'readable_hints': {'sections': []}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        projected = project_execution(copy.deepcopy(payload))
        self.assertNotIn('readable_hints',
                         json.dumps(projected, ensure_ascii=False))


if __name__ == '__main__':
    unittest.main()
