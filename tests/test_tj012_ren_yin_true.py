"""TJ-012.3 Slice D-1 （任氏分支寅月真格，非对称） public contract tests.

Public-safe by design: the registered quotes/notes transcription, the
pure determination lookup over the full judgement-order matrix, the
trace-composition mechanics over fact-shape stub traces, forged pilot
blocks, the real pilot at the Golden segment-boundary instants, and
the public-projection strip need no sealed data. Verbatim equality of
the registered quotes against the pinned snapshot text itself, and
real-chart end-to-end coverage of every Golden case (real birth
instants recomputed through the reviewed calendar path, real pilot
calls, Slice A/B blocks byte-compared on the same charts), live only
in the sealed companion test_tj012_ren_yin_true_sealed.py (offline
acceptance, NOT public CI), following the Slice A/B/C precedent.

The block is ASYMMETRIC: it determines only whether the Ren-branch
寅月 true pattern is established (commander exposed on year/month/hour
stems, day stem excluded). commander_not_visible is the negative face
of the s053 definition and is never labelled 假格； success_failure /
purity / useful_god stay None + unreviewed everywhere.
"""
import copy
import json
from pathlib import Path
import unittest

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb.bazi_pattern import (
    PATTERN_VARIANT, REN_YIN_ADJUDICATION_NOTES, REN_YIN_LIMITATIONS,
    REN_YIN_TRUE_VARIANT, REN_YIN_UNREVIEWED, ZHENGE_QUOTES,
    month_pattern_route, month_pattern_zaqi, ren_yin_true_false_lookup,
    ren_yin_true_pattern,
)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.public_projection import project_execution

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
PILOT_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_siling_pilot.json').read_text('utf-8'))
STEMS = '甲乙丙丁戊己庚辛壬癸'
# Keys that may appear only as the pinned determination fields of this
# block; every other verdict-shaped key is forbidden anywhere.
VERDICT_KEYS = {'score', 'rating', 'fortune', 'fortune_verdict',
                'auspicious', 'inauspicious', 'luck', '吉凶', '评分',
                '喜用神', '用神', 'pattern_name', 'fake_pattern'}


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


def _values(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _values(item)
    else:
        yield node


class RegistrationTests(unittest.TestCase):
    def test_registration_matches_golden_transcription(self):
        self.assertEqual(REN_YIN_TRUE_VARIANT, GOLDEN['variant'])
        golden_quotes = {q['id']: q for q in GOLDEN['quotes']}
        self.assertEqual({q['id'] for q in ZHENGE_QUOTES}, set(golden_quotes))
        for quote in ZHENGE_QUOTES:
            want = golden_quotes[quote['id']]
            self.assertEqual(quote['quote'], want['quote'])
            self.assertEqual(quote['locator'], want['locator'])
            self.assertEqual(quote['source_id'], want['source_id'])
            self.assertEqual(quote['source_section_id'],
                             want['source_section_id'])
            self.assertEqual(quote['layer'], want['layer'])
            loc = quote['locator']
            self.assertEqual(loc['char_end'] - loc['char_start'],
                             len(quote['quote']),
                             'locator span must equal the verbatim quote')
        self.assertEqual(list(REN_YIN_ADJUDICATION_NOTES),
                         GOLDEN['adjudication_notes'])
        self.assertEqual(list(REN_YIN_LIMITATIONS), GOLDEN['limitations'])

    def test_s054_quote_shared_with_slice_a(self):
        # The procedure quote is the same s054 sentence Slice A
        # registered; the two registrations must not drift apart.
        from tianji_kb.bazi_pattern import LUREN_QUOTES
        luren = {q['id']: q for q in LUREN_QUOTES}
        zhenge = {q['id']: q for q in ZHENGE_QUOTES}
        self.assertEqual(
            zhenge['renshi.siling_true_false_procedure']['quote'],
            luren['renshi.luren_route_exclusion']['quote'])
        self.assertEqual(
            zhenge['renshi.siling_true_false_procedure']['locator'],
            luren['renshi.luren_route_exclusion']['locator'])


def _lookup(**over):
    facts = {
        'route': 'not_luren', 'pilot_status': 'computed',
        'pilot_reason': None, 'pilot_commander': '戊',
        'month_hidden_stems': ['甲', '丙', '戊'],
        'commander_ten_god': '偏印', 'commander_visible_pillars': [],
    }
    facts.update(over)
    return ren_yin_true_false_lookup('庚', '寅', **facts)


class LookupOrderTests(unittest.TestCase):
    def assert_invariants(self, out):
        det = out['determination']
        self.assertIn(det['true_false'],
                      ('true', 'commander_not_visible', 'abstained'))
        self.assertIsNone(det['success_failure'])
        self.assertIsNone(det['purity'])
        self.assertIsNone(det['useful_god'])
        self.assertEqual(set(out['unreviewed']),
                         {'success_failure', 'purity', 'useful_god'})
        for note in out['unreviewed'].values():
            self.assertIn('unreviewed', note)
        self.assertEqual(out['unreviewed'], REN_YIN_UNREVIEWED)
        self.assertFalse(out['qualified_for_determination'])
        self.assertEqual(out['determination_scope'],
                         'ren_branch_yin_month_true_pattern_only')
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])
        self.assertEqual(out['evidence_binding'],
                         'pending_phase1_rule_registration')
        self.assertEqual(out['adjudication_notes'],
                         list(REN_YIN_ADJUDICATION_NOTES))
        self.assertEqual(out['scope_limits'], list(REN_YIN_LIMITATIONS))
        # Never a false/fake label, never any other verdict content.
        self.assertNotIn('假格', json.dumps(
            {'det': out['determination'], 'commander': out['commander']},
            ensure_ascii=False))
        self.assertFalse(VERDICT_KEYS & set(_keys(out)))
        self.assertNotIn('false', [v for v in _values(out['determination'])
                                    if isinstance(v, str)])

    def test_month_gate_abstains_first(self):
        out = ren_yin_true_false_lookup(
            '庚', '午', route='luren_no_month_pattern', pilot_status=None,
            pilot_reason='x', pilot_commander=None, month_hidden_stems=[],
            commander_ten_god=None, commander_visible_pillars=[])
        self.assertEqual(out['status'], 'abstained')
        self.assertEqual(out['decision_step'], 1)
        self.assertEqual(out['abstention_reason'], 'month_not_yin')
        self.assert_invariants(out)

    def test_route_precedence_before_pilot(self):
        # Even with a computed pilot, a 禄刃 route closure abstains at
        # step 2 (Slice A adjudication A1 precedence).
        out = ren_yin_true_false_lookup(
            '甲', '寅', route='luren_no_month_pattern',
            pilot_status='computed', pilot_reason=None, pilot_commander='甲',
            month_hidden_stems=['甲', '丙', '戊'], commander_ten_god='比肩',
            commander_visible_pillars=['year'])
        self.assertEqual(out['decision_step'], 2)
        self.assertEqual(out['abstention_reason'], 'luren_route_precedence')
        self.assert_invariants(out)

    def test_pilot_states_abstain_at_step_3(self):
        out = _lookup(pilot_status=None, pilot_reason='pilot_variant_mismatch',
                      pilot_commander=None)
        self.assertEqual(out['abstention_reason'], 'pilot_result_unverifiable')
        self.assertEqual(out['decision_step'], 3)
        self.assert_invariants(out)
        for status in ('rejected', 'uncertain', 'not_applicable'):
            out = _lookup(pilot_status=status, pilot_reason='some_reason',
                          pilot_commander=None)
            self.assertEqual(out['abstention_reason'], 'pilot_not_computed')
            self.assertEqual(out['pilot']['status'], status)
            self.assertEqual(out['pilot']['reason'], 'some_reason')
            self.assert_invariants(out)

    def test_commander_not_month_hidden_abstains(self):
        out = _lookup(pilot_commander='丁', commander_ten_god=None)
        self.assertEqual(out['decision_step'], 4)
        self.assertEqual(out['abstention_reason'],
                         'commander_not_month_hidden')
        self.assertIsNone(out['commander'])
        self.assert_invariants(out)

    def test_commander_not_visible_is_not_a_fake_pattern(self):
        out = _lookup()
        self.assertEqual(out['status'], 'determined')
        self.assertEqual(out['determination']['true_false'],
                         'commander_not_visible')
        self.assertIsNone(out['determination']['pattern'])
        self.assertEqual(out['commander']['stem'], '戊')
        self.assertEqual(out['commander']['visible_pillars'], [])
        self.assertFalse(out['commander']['day_stem_counts_as_exposure'])
        self.assert_invariants(out)

    def test_true_with_mechanical_pattern_name(self):
        out = _lookup(commander_visible_pillars=['month'])
        self.assertEqual(out['determination']['true_false'], 'true')
        self.assertEqual(out['determination']['pattern'], '偏印格')
        self.assertEqual(out['determination']['status'], 'determined')
        self.assert_invariants(out)

    def test_day_stem_excluded_pure_pins(self):
        # Adjudication D2 at the pure level: the commander equals the
        # day stem; only off-day exposure can make it true.
        out = ren_yin_true_false_lookup(
            '戊', '寅', route='not_luren', pilot_status='computed',
            pilot_reason=None, pilot_commander='戊',
            month_hidden_stems=['甲', '丙', '戊'], commander_ten_god='比肩',
            commander_visible_pillars=[])
        self.assertEqual(out['determination']['true_false'],
                         'commander_not_visible')
        out = ren_yin_true_false_lookup(
            '戊', '寅', route='not_luren', pilot_status='computed',
            pilot_reason=None, pilot_commander='戊',
            month_hidden_stems=['甲', '丙', '戊'], commander_ten_god='比肩',
            commander_visible_pillars=['hour'])
        self.assertEqual(out['determination']['true_false'], 'true')
        self.assertEqual(out['determination']['pattern'], '比肩格')
        # The day pillar itself is never an acceptable exposure pillar.
        with self.assertRaises(ValueError):
            ren_yin_true_false_lookup(
                '戊', '寅', route='not_luren', pilot_status='computed',
                pilot_reason=None, pilot_commander='戊',
                month_hidden_stems=['甲', '丙', '戊'],
                commander_ten_god='比肩', commander_visible_pillars=['day'])

    def test_lookup_fails_closed(self):
        with self.assertRaises(ValueError):
            _lookup(route='bogus')
        with self.assertRaises(ValueError):
            ren_yin_true_false_lookup(
                '猫', '寅', route='not_luren', pilot_status='computed',
                pilot_reason=None, pilot_commander='戊',
                month_hidden_stems=['甲', '丙', '戊'],
                commander_ten_god='偏印', commander_visible_pillars=[])
        with self.assertRaises(ValueError):
            _lookup(month_hidden_stems=['甲', '甲', '戊'])


def _pilot_block(status='computed', commander='戊', **over):
    conv = matrix.SILING_CALCULATION_CONVENTION
    version_id = conv['scope']['version_id']
    cell = matrix.SILING_MATRIX[version_id]['寅']
    quote = {row['id']: row for row in matrix.SILING_QUOTES}[
        cell['quotes'][0]]
    block = {
        'variant': 'bazi-siling-yin-pilot-v1',
        'status': status,
        'reason': None,
        'commander': commander if status == 'computed' else None,
        'scope_month_branch': '寅',
        'month_branch': '寅' if status == 'computed' else None,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'provenance': {
            'source_id': quote['source_id'],
            'source_section_id': quote['source_section_id'],
            'version_id': version_id,
            'calculation_convention': {'id': conv['id'],
                                       'version': conv['version']},
        },
    }
    block.update(over)
    return block


class _StubTrace:
    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _yin_steps(day_stem='庚', evidence_ids=('e1', 'e2', 'e3', 'e4')):
    """Fact-shape fixture for the touchstone chart 甲辰/丙寅/庚子/丙子.

    Shape only: real-chart verification of the same pillars lives in
    the sealed companion. Ten-gods are relative to the 庚 day master;
    寅 hidden stems are 甲（偏财）/丙（七杀）/戊（偏印）.
    """
    return [
        {'rule_id': 'bazi.phase2.pillars', 'evidence_ids': [evidence_ids[0]],
         'output': {'ganzhi': [['甲', '辰'], ['丙', '寅'], [day_stem, '子'],
                               ['丙', '子']],
                    'day_master': {'stem': day_stem}}},
        {'rule_id': 'bazi.phase2.ten_gods', 'evidence_ids': [evidence_ids[1]],
         'output': [{'pillar': 'year', 'stem': '甲', 'ten_god': '偏财'},
                    {'pillar': 'month', 'stem': '丙', 'ten_god': '七杀'},
                    {'pillar': 'day', 'stem': day_stem, 'ten_god': '日主'},
                    {'pillar': 'hour', 'stem': '丙', 'ten_god': '七杀'}]},
        {'rule_id': 'bazi.phase2.hidden_stems',
         'evidence_ids': [evidence_ids[2]],
         'output': [
             {'pillar': 'year', 'branch': '辰', 'hidden_stems': []},
             {'pillar': 'month', 'branch': '寅',
              'hidden_stems': [{'stem': '甲', 'ten_god': '偏财'},
                               {'stem': '丙', 'ten_god': '七杀'},
                               {'stem': '戊', 'ten_god': '偏印'}]},
             {'pillar': 'day', 'branch': '子', 'hidden_stems': []},
             {'pillar': 'hour', 'branch': '子', 'hidden_stems': []}]},
        {'rule_id': 'bazi.phase2.hidden_to_visible',
         'evidence_ids': [evidence_ids[3]],
         'output': {'positions': [
             {'hidden_pillar': 'month', 'hidden_stem': '甲',
              'visible_pillars': ['year']},
             {'hidden_pillar': 'month', 'hidden_stem': '丙',
              'visible_pillars': ['month', 'hour']}],
                    'day_stem_excluded': True}},
    ]


def _evidence(ids=('e1', 'e2', 'e3', 'e4')):
    return {i: object() for i in ids}


class CompositionTests(unittest.TestCase):
    def test_touchstone_shape_through_composition(self):
        # 本气甲 exposed on the year stem, commander 戊 nowhere:
        # the commander, not the principal hidden stem, drives it.
        out = ren_yin_true_pattern(
            _StubTrace(_yin_steps(), _evidence()), _pilot_block())
        self.assertEqual(out['determination']['true_false'],
                         'commander_not_visible')
        self.assertEqual(out['commander']['stem'], '戊')
        self.assertEqual(out['consumed_rule_ids'], [
            'bazi.phase2.pillars', 'bazi.phase2.ten_gods',
            'bazi.phase2.hidden_stems', 'bazi.phase2.hidden_to_visible'])
        self.assertEqual(out['variant'], PATTERN_VARIANT)

    def test_envelope_mapping_accepted(self):
        envelope = {'trace': _yin_steps(), 'evidence': _evidence()}
        out = ren_yin_true_pattern(envelope, _pilot_block(commander='丙'))
        self.assertEqual(out['determination']['true_false'], 'true')
        self.assertEqual(out['determination']['pattern'], '七杀格')
        self.assertEqual(out['commander']['visible_pillars'],
                         ['month', 'hour'])

    def test_forged_pilot_blocks_abstain(self):
        trace = _StubTrace(_yin_steps(), _evidence())
        out = ren_yin_true_pattern(trace, _pilot_block(variant='forged'))
        self.assertEqual(out['abstention_reason'], 'pilot_result_unverifiable')
        self.assertEqual(out['determination']['true_false'], 'abstained')
        tampered = _pilot_block()
        tampered['provenance']['calculation_convention'] = {
            'id': 'siling-calculation-convention', 'version': 'v99'}
        out = ren_yin_true_pattern(trace, tampered)
        self.assertEqual(out['abstention_reason'], 'pilot_result_unverifiable')
        out = ren_yin_true_pattern(trace, None)
        self.assertEqual(out['abstention_reason'], 'pilot_result_unverifiable')
        out = ren_yin_true_pattern(
            trace, _pilot_block(status='rejected', reason='not_pilot_version'))
        self.assertEqual(out['abstention_reason'], 'pilot_not_computed')
        self.assertEqual(out['pilot']['status'], 'rejected')
        # Caller-claimed commander that is not a month hidden stem:
        # the claimed commander and the executed facts disagree.
        out = ren_yin_true_pattern(trace, _pilot_block(commander='丁'))
        self.assertEqual(out['abstention_reason'], 'commander_not_month_hidden')
        self.assertEqual(out['decision_step'], 4)

    def test_forged_traces_fail_closed(self):
        with self.assertRaises(ValueError):
            ren_yin_true_pattern(_StubTrace([], {}), _pilot_block())
        with self.assertRaises(ValueError):
            ren_yin_true_pattern(
                _StubTrace(_yin_steps(), {}), _pilot_block())
        steps = _yin_steps()
        steps[3]['output']['positions'][1]['visible_pillars'] = ['month']
        with self.assertRaises(ValueError):
            # hidden_to_visible now disagrees with the ten-god stems
            # (丙 is on the hour stem too): executed facts in conflict.
            ren_yin_true_pattern(
                _StubTrace(steps, _evidence()), _pilot_block(commander='丙'))
        steps = _yin_steps()
        steps[2]['output'][1]['branch'] = '卯'
        with self.assertRaises(ValueError):
            ren_yin_true_pattern(
                _StubTrace(steps, _evidence()), _pilot_block())

    def test_coexisting_blocks_untouched(self):
        # Composition must not disturb the Slice A/B blocks computed
        # over the same trace.
        trace = _StubTrace(_yin_steps(), _evidence())
        route_before = month_pattern_route(trace)
        zaqi_before = month_pattern_zaqi(trace)
        ren_yin_true_pattern(trace, _pilot_block())
        self.assertEqual(month_pattern_route(trace), route_before)
        self.assertEqual(month_pattern_zaqi(trace), zaqi_before)
        self.assertEqual(route_before['route'], 'not_luren')
        self.assertEqual(zaqi_before['status'], 'not_applicable')


class RealPilotBoundaryPairTests(unittest.TestCase):
    """The Golden segment-boundary flip pair with the REAL pilot.

    Birth instants are the pilot Golden's g03/g04 (t0+7d −1s and the
    exact switch). The trace is a fact-shape fixture carrying the
    hand-derived pillars 甲辰/丙寅/乙巳/甲申 for those instants; the
    sealed companion re-derives the pillars through the production
    calendar and replays the whole Golden set end to end.
    """

    def _steps(self):
        return [
            {'rule_id': 'bazi.phase2.pillars', 'evidence_ids': ['e1'],
             'output': {'ganzhi': [['甲', '辰'], ['丙', '寅'], ['乙', '巳'],
                                   ['甲', '申']],
                        'day_master': {'stem': '乙'}}},
            {'rule_id': 'bazi.phase2.ten_gods', 'evidence_ids': ['e2'],
             'output': [{'pillar': 'year', 'stem': '甲', 'ten_god': '劫财'},
                        {'pillar': 'month', 'stem': '丙', 'ten_god': '伤官'},
                        {'pillar': 'day', 'stem': '乙', 'ten_god': '日主'},
                        {'pillar': 'hour', 'stem': '甲', 'ten_god': '劫财'}]},
            {'rule_id': 'bazi.phase2.hidden_stems', 'evidence_ids': ['e3'],
             'output': [
                 {'pillar': 'year', 'branch': '辰', 'hidden_stems': []},
                 {'pillar': 'month', 'branch': '寅',
                  'hidden_stems': [{'stem': '甲', 'ten_god': '劫财'},
                                   {'stem': '丙', 'ten_god': '伤官'},
                                   {'stem': '戊', 'ten_god': '正财'}]},
                 {'pillar': 'day', 'branch': '巳', 'hidden_stems': []},
                 {'pillar': 'hour', 'branch': '申', 'hidden_stems': []}]},
            {'rule_id': 'bazi.phase2.hidden_to_visible',
             'evidence_ids': ['e4'],
             'output': {'positions': [
                 {'hidden_pillar': 'month', 'hidden_stem': '甲',
                  'visible_pillars': ['year', 'hour']},
                 {'hidden_pillar': 'month', 'hidden_stem': '丙',
                  'visible_pillars': ['month']}],
                        'day_stem_excluded': True}},
        ]

    def _jie_facts(self):
        window = PILOT_GOLDEN['jie_windows']['2024']
        return {'provider': dict(PILOT_GOLDEN['provider']),
                'lichun': dict(window['lichun']),
                'next_jie': dict(window['next_jie'])}

    def test_one_second_flips_the_commander_and_the_verdict(self):
        trace = _StubTrace(self._steps(), _evidence())
        before = yin_siling_pilot(
            '2024-02-11T08:27:06+00:00', version_id='ditiansui-yuanshuo',
            jie_facts=self._jie_facts())
        self.assertEqual(before['status'], 'computed')
        self.assertEqual(before['commander'], '戊')
        out = ren_yin_true_pattern(trace, before)
        self.assertEqual(out['determination']['true_false'],
                         'commander_not_visible')
        at = yin_siling_pilot(
            '2024-02-11T08:27:07+00:00', version_id='ditiansui-yuanshuo',
            jie_facts=self._jie_facts())
        self.assertEqual(at['commander'], '丙')
        out = ren_yin_true_pattern(trace, at)
        self.assertEqual(out['determination']['true_false'], 'true')
        self.assertEqual(out['determination']['pattern'], '伤官格')
        self.assertEqual(out['pilot']['segment']['index'], 2)


class ProjectionTests(unittest.TestCase):
    def test_public_projection_strips_block(self):
        payload = {
            'domain': 'bazi', 'variant': 'ziping-structural-v1',
            'deterministic': True,
            'result': {'pillars': [],
                       'pattern_determination_ren_yin': {'x': 1}},
            'chart': {'pattern_determination_ren_yin': {'x': 2}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        out = project_execution(copy.deepcopy(payload))
        self.assertNotIn('pattern_determination_ren_yin', out['chart'])
        self.assertNotIn('pattern_determination_ren_yin', out['result'])


if __name__ == '__main__':
    unittest.main()
