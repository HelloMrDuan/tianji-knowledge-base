"""TJ-012.3 D-1 寅月真格有限公开呈现 public contract tests (Stage B).

Public-safe by design: the presentation builder over fact-shape stub
traces (the real D-1 composition over hand-derived ten-god /
visibility facts), the live research gate's non-entry conditions
(non-寅月 and 巳月 births), the pilot replay rejection, uncertain /
forged / version-mismatched pilots, the whitelist, the evidence
binding, and the public-projection scoped release need no sealed
data. Real-chart end-to-end coverage -- the full pattern gate through
_bazi_profile over all fifteen Golden cases, byte equality of the
presentation against the gate's own determination, the production
API no-leak check, and the U1/tiaohou/bingyao/dayun no-regression
check -- lives only in the sealed companion
test_tj0123_pattern_public_sealed.py (offline acceptance, NOT public
CI: the bazi-profile execution needs the sealed Canonical
foundations).

Golden expectations are hand-derived from
golden_tj012_ren_yin_true.json and
golden_tj012_d1_yin_research_link.json (see those files' meta
blocks): t1-wu-zhengcai (正财格， hour), n1-touchstone
(commander_not_visible), a2-wu-daymaster-pos / a4-bing-daymaster-pos
(比肩格 -- D5, never public), s3-route-precedence (abstained),
link-non-yin (午月）, link-si (巳月）. No expected value here was
produced by running the implementation. Ten-god facts in the stub
traces are hand-computed from stem five-element generation/control
and yin/yang sameness (e.g. 戊对乙 = 正财： 乙克戊，阴克阳）.
"""
import copy
import json
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from lunar_python import Solar as _Solar

from tianji_kb import bazi_siling_matrix as matrix
from tianji_kb.bazi_pattern import ren_yin_true_pattern
from tianji_kb.bazi_pattern_public import (
    VARIANT,
    is_valid_public_pattern_presentation,
    public_pattern_presentation,
)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.public_projection import project_execution
from tianji_kb.scenario_engine import (
    _pattern_public_gate,
    execute_scenario,
    registry,
    ren_yin_research_execution,
)

ROOT = Path(__file__).resolve().parents[1]
REN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
LINK_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_d1_yin_research_link.json').read_text('utf-8'))
ZONE = 'Asia/Shanghai'
PERMITTED_SOURCE = 'bazi.source.ditiansui-spouse'
FORBIDDEN_KEYS = {
    'score', 'scores', 'rating', 'weight', 'weights', 'useful_god',
    'favorable', 'favourable', 'recommended', 'recommendation',
    'verdict', 'combined_verdict', 'final_verdict', 'resolution',
    'resolved_choice', 'preference', 'true_false', 'success_failure',
    'pattern_name', '喜用神', '用神', '喜神', '忌神', '吉凶', '评分',
    '推荐', '权重', '裁决', '真格', '假格', '成格', '破格',
}


def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_keys(item)


def _all_strings(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _all_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _all_strings(item)
    elif isinstance(node, str):
        yield node


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


def _provider_pillars(value, zone=ZONE):
    """Real chart pillars from the pinned provider (lunar-python).

    The same calendar path the platform uses; the returned ganzhi
    are checked against the Golden pillars for the known cases
    (t1, a2) rather than trusted blindly.
    """
    birth = datetime.fromisoformat(value).astimezone(ZoneInfo(zone))
    lunar = _Solar.fromYmdHms(
        birth.year, birth.month, birth.day,
        birth.hour, birth.minute, birth.second).getLunar()
    eight = lunar.getEightChar()
    ganzhi = [eight.getYear(), eight.getMonth(),
              eight.getDay(), eight.getTime()]
    return [{'stem': {'value': pair[0]}, 'branch': {'value': pair[1]}}
            for pair in ganzhi]


class _StubTrace:
    def __init__(self, steps, evidence):
        self.steps = steps
        self.evidence = evidence


def _stub_steps(ganzhi, day_master, ten_gods, month_hidden, positions):
    """Fact-shape stub trace for one hand-derived chart.

    ``ten_gods``: [{pillar, stem, ten_god}] rows relative to the day
    master; ``month_hidden``: [{stem, ten_god}] for the 寅 month;
    ``positions``: [{hidden_pillar, hidden_stem, visible_pillars}].
    """
    pillars = {'ganzhi': [list(pair) for pair in ganzhi],
               'day_master': {'stem': day_master}}
    hidden_rows = []
    for pillar, pair in zip(('year', 'month', 'day', 'hour'), ganzhi):
        hidden_rows.append({
            'pillar': pillar, 'branch': pair[1],
            'hidden_stems': list(month_hidden)
            if pillar == 'month' else []})
    return [
        {'rule_id': 'bazi.phase2.pillars', 'evidence_ids': ['e1'],
         'output': pillars},
        {'rule_id': 'bazi.phase2.ten_gods', 'evidence_ids': ['e2'],
         'output': ten_gods},
        {'rule_id': 'bazi.phase2.hidden_stems', 'evidence_ids': ['e3'],
         'output': hidden_rows},
        {'rule_id': 'bazi.phase2.hidden_to_visible',
         'evidence_ids': ['e4'],
         'output': {'positions': positions,
                    'day_stem_excluded': True}},
    ]


def _evidence():
    records = {}
    for evidence_id in ('e1', 'e2', 'e3', 'e4',
                        'd1e1', 'd1e2', 'd1e3'):
        records[evidence_id] = {'source_id': PERMITTED_SOURCE}
    return records


def _build_case(ganzhi, day_master, ten_gods, month_hidden, positions,
                commander):
    """Run the real D-1 composition over a stub trace and wrap it.

    Returns (determination, execution, record, pillars) where the
    execution carries the D-1 trace step (output == determination)
    with its bound evidence, and the record is an entered gate
    record over the live-shaped pilot block.
    """
    steps = _stub_steps(ganzhi, day_master, ten_gods, month_hidden,
                        positions)
    evidence = _evidence()
    pilot = _pilot_block(commander=commander)
    determination = ren_yin_true_pattern(
        _StubTrace(steps, evidence), pilot)
    d1_step = {'rule_id': 'bazi.phase2.ren_yin_true_pattern',
               'evidence_ids': ['d1e1', 'd1e2', 'd1e3'],
               'output': copy.deepcopy(determination)}
    trace = steps + [d1_step]
    matches = [{'rule_id': step['rule_id'], 'matched': True,
                'evidence_ids': list(step['evidence_ids'])}
               for step in trace]
    execution = {'trace': trace, 'rule_matches': matches,
                 'evidence': evidence}
    record = {'entered': True, 'reason': None,
              'month_branch': ganzhi[1][1], 'pilot': pilot,
              'envelope': copy.deepcopy(execution),
              'determination': determination,
              'research_only': True, 'public_enabled': False,
              'ai_enabled': False}
    pillars = [{'stem': {'value': pair[0]}, 'branch': {'value': pair[1]}}
               for pair in ganzhi]
    return determination, execution, record, pillars


# Hand-derived stub facts (ten-gods relative to the day master).
T1 = {
    'ganzhi': [('甲', '辰'), ('丙', '寅'), ('乙', '巳'), ('戊', '寅')],
    'day_master': '乙',
    'ten_gods': [
        {'pillar': 'year', 'stem': '甲', 'ten_god': '劫财'},
        {'pillar': 'month', 'stem': '丙', 'ten_god': '伤官'},
        {'pillar': 'day', 'stem': '乙', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '戊', 'ten_god': '正财'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '劫财'},
        {'stem': '丙', 'ten_god': '伤官'},
        {'stem': '戊', 'ten_god': '正财'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '甲',
         'visible_pillars': ['year']},
        {'hidden_pillar': 'month', 'hidden_stem': '丙',
         'visible_pillars': ['month']},
        {'hidden_pillar': 'month', 'hidden_stem': '戊',
         'visible_pillars': ['hour']}],
    'commander': '戊',
}
N1 = {
    'ganzhi': [('甲', '辰'), ('丙', '寅'), ('庚', '子'), ('丙', '子')],
    'day_master': '庚',
    'ten_gods': [
        {'pillar': 'year', 'stem': '甲', 'ten_god': '偏财'},
        {'pillar': 'month', 'stem': '丙', 'ten_god': '七杀'},
        {'pillar': 'day', 'stem': '庚', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '丙', 'ten_god': '七杀'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '偏财'},
        {'stem': '丙', 'ten_god': '七杀'},
        {'stem': '戊', 'ten_god': '偏印'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '甲',
         'visible_pillars': ['year']},
        {'hidden_pillar': 'month', 'hidden_stem': '丙',
         'visible_pillars': ['month', 'hour']}],
    'commander': '戊',
}
A2 = {
    'ganzhi': [('癸', '卯'), ('甲', '寅'), ('戊', '戌'), ('戊', '午')],
    'day_master': '戊',
    'ten_gods': [
        {'pillar': 'year', 'stem': '癸', 'ten_god': '正财'},
        {'pillar': 'month', 'stem': '甲', 'ten_god': '七杀'},
        {'pillar': 'day', 'stem': '戊', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '戊', 'ten_god': '比肩'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '七杀'},
        {'stem': '丙', 'ten_god': '偏印'},
        {'stem': '戊', 'ten_god': '比肩'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '甲',
         'visible_pillars': ['month']},
        {'hidden_pillar': 'month', 'hidden_stem': '戊',
         'visible_pillars': ['hour']}],
    'commander': '戊',
}
A4 = {
    'ganzhi': [('乙', '巳'), ('戊', '寅'), ('丙', '辰'), ('丙', '申')],
    'day_master': '丙',
    'ten_gods': [
        {'pillar': 'year', 'stem': '乙', 'ten_god': '正印'},
        {'pillar': 'month', 'stem': '戊', 'ten_god': '食神'},
        {'pillar': 'day', 'stem': '丙', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '丙', 'ten_god': '比肩'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '偏印'},
        {'stem': '丙', 'ten_god': '比肩'},
        {'stem': '戊', 'ten_god': '食神'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '丙',
         'visible_pillars': ['hour']},
        {'hidden_pillar': 'month', 'hidden_stem': '戊',
         'visible_pillars': ['month']}],
    'commander': '丙',
}
S3 = {
    'ganzhi': [('甲', '辰'), ('丙', '寅'), ('甲', '寅'), ('己', '巳')],
    'day_master': '甲',
    'ten_gods': [
        {'pillar': 'year', 'stem': '甲', 'ten_god': '比肩'},
        {'pillar': 'month', 'stem': '丙', 'ten_god': '食神'},
        {'pillar': 'day', 'stem': '甲', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '己', 'ten_god': '正财'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '比肩'},
        {'stem': '丙', 'ten_god': '食神'},
        {'stem': '戊', 'ten_god': '偏财'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '甲',
         'visible_pillars': ['year']},
        {'hidden_pillar': 'month', 'hidden_stem': '丙',
         'visible_pillars': ['month']}],
    'commander': '戊',
}
JIECAI = {
    'ganzhi': [('甲', '辰'), ('丙', '寅'), ('乙', '巳'), ('戊', '寅')],
    'day_master': '乙',
    'ten_gods': [
        {'pillar': 'year', 'stem': '甲', 'ten_god': '劫财'},
        {'pillar': 'month', 'stem': '丙', 'ten_god': '伤官'},
        {'pillar': 'day', 'stem': '乙', 'ten_god': '日主'},
        {'pillar': 'hour', 'stem': '戊', 'ten_god': '正财'}],
    'month_hidden': [
        {'stem': '甲', 'ten_god': '劫财'},
        {'stem': '丙', 'ten_god': '伤官'},
        {'stem': '戊', 'ten_god': '正财'}],
    'positions': [
        {'hidden_pillar': 'month', 'hidden_stem': '甲',
         'visible_pillars': ['year']},
        {'hidden_pillar': 'month', 'hidden_stem': '丙',
         'visible_pillars': ['month']},
        {'hidden_pillar': 'month', 'hidden_stem': '戊',
         'visible_pillars': ['hour']}],
    'commander': '甲',
}


def _present(case):
    determination, execution, record, pillars = _build_case(
        case['ganzhi'], case['day_master'], case['ten_gods'],
        case['month_hidden'], case['positions'], case['commander'])
    return public_pattern_presentation(record, execution, pillars)


class BuilderPositiveTests(unittest.TestCase):
    def test_t1_true_pattern_presented(self):
        # (1) 寅月 legal true-pattern positive: Golden t1.
        out = _present(T1)
        self.assertEqual(out, {
            'variant': VARIANT,
            'title': '任氏寅月局部真格研究结果',
            'status': 'presented',
            'outcome': 'true_pattern',
            'statement': '司令戊透于时干，真格成立。',
            'pattern': '正财格',
            'day_master': '乙',
            'month_branch': '寅',
            'commander': {'stem': '戊', 'ten_god': '正财',
                          'visible_pillars': ['hour']},
            'rule_ids': ['renshi.zhenge_definition',
                         'renshi.siling_true_false_procedure'],
            'source_sections': ['bazi.section.s053',
                                'bazi.section.s054'],
            'school': '任氏分支',
            'scope_month_branch': '寅',
            'evidence_ids': ['d1e1', 'd1e2', 'd1e3'],
            'source_ids': [PERMITTED_SOURCE],
            'scope_statement': out['scope_statement'],
            'limitations': out['limitations'],
        })
        self.assertTrue(is_valid_public_pattern_presentation(out))
        self.assertEqual(
            set(_all_keys(out)) & FORBIDDEN_KEYS, set(),
            'a presented object carries no verdict-shaped key')
        # The scope/limitations text names 假格 only as a forbidden
        # output; the conclusion itself never states it.
        self.assertNotIn('假格', out['statement'])
        self.assertNotEqual(out['pattern'], '假格')

    def test_presented_object_is_distinct_from_determination(self):
        # The presentation is a new object, not the research block
        # relabelled: it carries no research block keys.
        out = _present(T1)
        for key in ('determination_variant', 'pilot', 'unreviewed',
                    'adjudication_notes', 'scope_limits',
                    'determination', 'fact_refs', 'consumed_rule_ids',
                    'evidence_binding', 'research_only',
                    'public_enabled', 'ai_enabled'):
            self.assertNotIn(key, out)


class BuilderCommanderNotVisibleTests(unittest.TestCase):
    def test_n1_commander_not_visible_presented(self):
        # (2) Commander-not-visible conservative presentation:
        # Golden n1 touchstone. The conclusion stops at 司令不透、
        # 无真格 -- presented, never 假格.
        out = _present(N1)
        self.assertEqual(out['status'], 'presented')
        self.assertEqual(out['outcome'], 'commander_not_visible')
        self.assertEqual(out['statement'], '司令戊不透，无真格。')
        self.assertIsNone(out['pattern'])
        self.assertEqual(out['commander'], {
            'stem': '戊', 'ten_god': '偏印', 'visible_pillars': []})
        self.assertEqual(out['day_master'], '庚')
        self.assertEqual(out['month_branch'], '寅')
        self.assertTrue(is_valid_public_pattern_presentation(out))
        self.assertNotIn('假格', out['statement'])
        self.assertEqual(
            set(_all_keys(out)) & FORBIDDEN_KEYS, set())


class BuilderD5Tests(unittest.TestCase):
    def test_a2_bijie_not_public(self):
        # (3) D5 比肩格 boundary: Golden a2 (戊 day master, 戊段，
        # 戊透于时干）. The underlying determination is true 比肩格；
        # the public builder returns not_judgeable and shows no name.
        determination, execution, record, pillars = _build_case(
            A2['ganzhi'], A2['day_master'], A2['ten_gods'],
            A2['month_hidden'], A2['positions'], A2['commander'])
        self.assertEqual(
            determination['determination']['pattern'], '比肩格')
        self.assertEqual(
            determination['determination']['true_false'], 'true')
        out = public_pattern_presentation(record, execution, pillars)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'pattern_name_not_public')
        self.assertEqual(out['day_master'], '戊')
        self.assertNotIn('pattern', out)
        self.assertNotIn('比肩格', json.dumps(out, ensure_ascii=False))
        self.assertTrue(is_valid_public_pattern_presentation(out))

    def test_a4_bijie_not_public(self):
        # D5 second witness: Golden a4 (丙 day master, 丙段，丙透于时干）.
        determination, _, record, pillars = _build_case(
            A4['ganzhi'], A4['day_master'], A4['ten_gods'],
            A4['month_hidden'], A4['positions'], A4['commander'])
        self.assertEqual(
            determination['determination']['pattern'], '比肩格')
        out = public_pattern_presentation(
            record, record['envelope'], pillars)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'pattern_name_not_public')
        self.assertNotIn('比肩格', json.dumps(out, ensure_ascii=False))

    def test_jiecai_not_public(self):
        # Same whitelist rule for 劫财格 (likewise outside the 八格
        # 名目 list): a true 劫财格 determination is not presentable.
        determination, execution, record, pillars = _build_case(
            JIECAI['ganzhi'], JIECAI['day_master'],
            JIECAI['ten_gods'], JIECAI['month_hidden'],
            JIECAI['positions'], JIECAI['commander'])
        self.assertEqual(
            determination['determination']['pattern'], '劫财格')
        out = public_pattern_presentation(record, execution, pillars)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'pattern_name_not_public')
        self.assertNotIn('劫财格', json.dumps(out, ensure_ascii=False))


class BuilderAbstainedTests(unittest.TestCase):
    def test_s3_route_precedence_abstained(self):
        # Golden s3: 甲×寅月, Slice A 禄刃 route precedence.
        out = _present(S3)
        self.assertEqual(out['status'], 'abstained')
        self.assertEqual(out['reason'], 'luren_route_precedence')
        self.assertEqual(out['decision_step'], 2)
        self.assertNotIn('pattern', out)
        self.assertTrue(is_valid_public_pattern_presentation(out))


class GateNonEntryTests(unittest.TestCase):
    def test_non_yin_birth_is_not_judgeable(self):
        # (4) Non-寅月: the real gate never enters; the presentation
        # is not_judgeable with the month reason, pillars from the
        # pinned provider (甲辰/庚午/庚戌/辛巳 -- Golden link-non-yin).
        value = '2024-06-15T10:00:00+08:00'
        pillars = _provider_pillars(value)
        self.assertEqual(
            [p['stem']['value'] + p['branch']['value'] for p in pillars],
            ['甲辰', '庚午', '庚戌', '辛巳'])
        out = _pattern_public_gate(value, ZONE, pillars)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'month_not_yin')
        self.assertEqual(out['day_master'], '庚')
        self.assertEqual(out['month_branch'], '午')
        self.assertTrue(is_valid_public_pattern_presentation(out))

    def test_si_month_never_enters_ren_presentation(self):
        # (5) 巳月 Sanming T1 must not enter the Ren pattern
        # presentation: the real gate never enters (month_not_yin);
        # the 巳月 pilot is never consulted as a D-1 input.
        case = next(c for c in LINK_GOLDEN['cases']
                    if c['id'] == 'link-si')
        value = case['source_birth']['value']
        pillars = _provider_pillars(
            value, case['source_birth']['zone'])
        self.assertEqual(pillars[1]['branch']['value'], '巳')
        record = ren_yin_research_execution(
            value, case['source_birth']['zone'])
        self.assertFalse(record['entered'])
        self.assertEqual(record['reason'], 'month_not_yin')
        out = _pattern_public_gate(
            value, case['source_birth']['zone'], pillars)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'month_not_yin')
        self.assertEqual(out['month_branch'], '巳')
        self.assertNotIn('pattern', out)


class PilotFailureTests(unittest.TestCase):
    def test_provider_replay_mismatch_rejected(self):
        # (6) Provider replay mismatch: lichun +1s vs the provider
        # replay rejects at the pilot layer, never computes; the
        # gate record for a rejected pilot presents nothing.
        case = next(c for c in LINK_GOLDEN['cases']
                    if c['id'] == 'link-t1')
        window = LINK_GOLDEN['jie_windows'][case['window']]
        facts = {'provider': dict(LINK_GOLDEN['provider']),
                 'lichun': dict(window['lichun']),
                 'next_jie': dict(window['next_jie'])}
        facts['lichun']['at'] = '2024-02-04T16:27:08+08:00'
        pilot = yin_siling_pilot(
            case['source_birth']['value'],
            version_id='ditiansui-yuanshuo', jie_facts=facts)
        self.assertEqual(pilot['status'], 'rejected')
        self.assertEqual(pilot['reason'], 'provider_replay_mismatch')
        record = {'entered': False, 'reason': 'pilot_rejected',
                  'month_branch': '寅', 'pilot': pilot,
                  'envelope': None, 'determination': None,
                  'research_only': True, 'public_enabled': False,
                  'ai_enabled': False}
        out = public_pattern_presentation(
            record, None, _provider_pillars(
                case['source_birth']['value']))
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'pilot_rejected')

    def test_uncertain_pilot_presents_nothing(self):
        # (7a) Uncertain pilot: no conclusion presented.
        record = {'entered': False, 'reason': 'pilot_uncertain',
                  'month_branch': '寅', 'pilot': None,
                  'envelope': None, 'determination': None,
                  'research_only': True, 'public_enabled': False,
                  'ai_enabled': False}
        out = public_pattern_presentation(
            record, None, _provider_pillars('2024-02-16T10:00:00+08:00'))
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['reason'], 'pilot_uncertain')
        self.assertNotIn('pattern', out)

    def test_forged_pilot_variant_fails_closed(self):
        # (7b) Forged pilot inside an entered determination: the
        # pilot claim variant does not match the live pilot.
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        record = copy.deepcopy(record)
        record['determination']['pilot']['variant'] = 'forged'
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_version_mismatched_pilot_fails_closed(self):
        # (7c) Version-mismatched pilot: the live pilot block itself
        # carries a non-pilot variant, so the determination cannot
        # be bound to it.
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        record = copy.deepcopy(record)
        record['pilot'] = _pilot_block(
            variant='bazi-siling-si-pilot-v1')
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_forged_determination_governance_fails_closed(self):
        # A determination flipped to public_enabled is a forgery.
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        record = copy.deepcopy(record)
        record['determination']['public_enabled'] = True
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)


class WhitelistTests(unittest.TestCase):
    def test_renamed_pattern_fails_closed(self):
        # (8) An illegal pattern name cannot bypass the whitelist:
        # a determination whose pattern disagrees with its commander
        # ten-god is a forgery, not a presentable name.
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        record = copy.deepcopy(record)
        record['determination']['determination']['pattern'] = '正官格'
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_invented_pattern_name_is_not_valid(self):
        # The closed-shape validator rejects any name outside the
        # eight, even in an otherwise well-formed object.
        out = _present(T1)
        forged = copy.deepcopy(out)
        forged['pattern'] = '财神格'
        self.assertFalse(is_valid_public_pattern_presentation(forged))
        forged = copy.deepcopy(out)
        forged['pattern'] = '比肩格'
        self.assertFalse(is_valid_public_pattern_presentation(forged))

    def test_all_eight_names_validate(self):
        # Every whitelisted name passes the validator in shape.
        for name in ('正官格', '七杀格', '正财格', '偏财格',
                     '正印格', '偏印格', '食神格', '伤官格'):
            out = _present(T1)
            out['pattern'] = name
            out['commander']['ten_god'] = name[:-1]
            self.assertTrue(
                is_valid_public_pattern_presentation(out), name)


class EvidenceTests(unittest.TestCase):
    def test_evidence_ids_exist_and_are_permitted(self):
        # (10) Evidence IDs must actually exist in the execution
        # evidence and comply with the public boundary (the single
        # registered classical source of the r037 refs).
        out = _present(T1)
        self.assertEqual(out['evidence_ids'], ['d1e1', 'd1e2', 'd1e3'])
        self.assertEqual(out['source_ids'], [PERMITTED_SOURCE])

    def test_missing_evidence_fails_closed(self):
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        execution = copy.deepcopy(execution)
        del execution['evidence']['d1e2']
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_unpermitted_evidence_source_fails_closed(self):
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        execution = copy.deepcopy(execution)
        execution['evidence']['d1e1']['source_id'] = 'bazi.source.other'
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_d1_step_without_evidence_fails_closed(self):
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        execution = copy.deepcopy(execution)
        execution['trace'][-1]['evidence_ids'] = []
        execution['rule_matches'][-1]['evidence_ids'] = []
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)

    def test_trace_step_output_drift_fails_closed(self):
        _, execution, record, pillars = _build_case(
            T1['ganzhi'], T1['day_master'], T1['ten_gods'],
            T1['month_hidden'], T1['positions'], T1['commander'])
        execution = copy.deepcopy(execution)
        execution['trace'][-1]['output'] = copy.deepcopy(
            execution['trace'][-1]['output'])
        execution['trace'][-1]['output']['determination']['pattern'] = \
            '正官格'
        with self.assertRaises(ValueError):
            public_pattern_presentation(record, execution, pillars)


class ProjectionTests(unittest.TestCase):
    def _envelope(self, scenario_id, presentation, container='result'):
        result = {'pillars': []}
        chart = {}
        if container == 'result':
            result['pattern_presentation'] = presentation
            result['pattern_determination_ren_yin'] = {'x': 1}
        else:
            chart['pattern_presentation'] = presentation
            chart['pattern_determination_ren_yin'] = {'x': 2}
        return {
            'scenario_id': scenario_id,
            'result': result,
            'chart': chart,
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }

    def test_valid_presentation_lifted_only_for_bazi_profile(self):
        # (9) The research raw block is never passed through; only
        # the validated presentation is lifted, only for bazi-profile.
        out = _present(T1)
        projected = project_execution(self._envelope('bazi-profile', out))
        self.assertEqual(projected['result']['pattern_presentation'], out)
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['chart'])

    def test_presentation_stripped_for_other_scenarios(self):
        out = _present(T1)
        projected = project_execution(self._envelope('daily', out))
        self.assertNotIn('pattern_presentation', projected['result'])
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])

    def test_forged_presentation_is_stripped(self):
        out = _present(T1)
        forged = copy.deepcopy(out)
        forged['pattern'] = '比肩格'
        projected = project_execution(
            self._envelope('bazi-profile', forged))
        self.assertNotIn('pattern_presentation', projected['result'])
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])

    def test_raw_block_stripped_without_presentation(self):
        payload = {
            'scenario_id': 'bazi-profile',
            'result': {'pillars': [],
                       'pattern_determination_ren_yin': {'x': 1}},
            'chart': {'pattern_determination_ren_yin': {'x': 2}},
            'evidence': {}, 'rule_matches': [], 'trace': [],
        }
        projected = project_execution(copy.deepcopy(payload))
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['result'])
        self.assertNotIn('pattern_determination_ren_yin',
                         projected['chart'])

    def test_no_raw_d1_trace_in_projected_json(self):
        # (11, public part) An ordinary projected response carries
        # no raw D-1 trace, block, or pilot anywhere in its JSON.
        out = _present(T1)
        projected = project_execution(self._envelope('bazi-profile', out))
        dumped = json.dumps(projected, ensure_ascii=False)
        self.assertNotIn('pattern_determination_ren_yin', dumped)
        self.assertNotIn('ren_yin_true_pattern', dumped)
        self.assertNotIn('ren-pattern-yin-true-v1', dumped)
        self.assertNotIn('siling-yin-pilot', dumped)


class OptInTests(unittest.TestCase):
    def test_presentation_is_not_a_registered_scenario(self):
        # The presentation is not a scenario entry and cannot be
        # reached through execute_scenario; the research entry
        # itself stays unregistered.
        ids = {item['id'] for item in registry()}
        self.assertNotIn('pattern-presentation', ids)
        self.assertNotIn('pattern_presentation', ids)
        with self.assertRaises(ValueError):
            execute_scenario('pattern-presentation',
                             {'value': '2024-02-11T04:00:00+08:00'})

    def test_bazi_profile_calls_only_the_presentation_gate(self):
        # Source-shape pin (Stage B update of the E0385 pin): the
        # production scenario function must not invoke the research
        # gate directly -- no raw record reaches the profile
        # function. The only authorized path is the presentation
        # gate, which consumes the research gate server-side and
        # attaches only the validated presentation object.
        source = (ROOT / 'src' / 'tianji_kb' / 'scenario_engine.py'
                  ).read_text(encoding='utf-8')
        profile = source.split('def _bazi_profile')[1].split(
            'def _question')[0]
        self.assertNotIn('ren_yin_research_execution', profile)
        self.assertNotIn('_ren_yin_research_pilot', profile)
        self.assertNotIn('pattern_determination_ren_yin', profile)
        self.assertEqual(profile.count('_pattern_public_gate('), 1)
        gate = source.split('def _pattern_public_gate')[1].split(
            '\ndef ')[0]
        self.assertIn('ren_yin_research_execution', gate)


class FrontendWiringTests(unittest.TestCase):
    """Guarded source pins for the page wiring (E0359 lesson: the
    assembled acceptance tree has no web/ -- skip when absent)."""

    def test_page_consumes_pattern_presentation(self):
        page_path = (ROOT / "web" / "visual-prototype" / "src" / "public"
                     / "BaziProfilePage.tsx")
        if not page_path.exists():
            self.skipTest("web tree not present in this checkout")
        page = page_path.read_text(encoding="utf-8")
        self.assertIn("pattern_presentation", page)
        self.assertIn("patternPresentation", page)
        self.assertIn("pattern_name_not_public", page)
        # The page never renders the research raw block; the backend
        # scope text may name 假格 only as a forbidden output, so
        # the pin is on the conclusion wording, not the word itself.
        self.assertNotIn("pattern_determination_ren_yin", page)
        self.assertNotIn("假格成立", page)


if __name__ == '__main__':
    unittest.main()
