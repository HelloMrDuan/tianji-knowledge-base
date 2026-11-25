"""TJ-0424 pattern engine: one evaluator per pattern, research_only.

Anchors (public worktree Golden files, no sealed text copied):
- tests/golden_tj012_ren_yin_true.json (15 D-1 cases, real birth instants)
- tests/golden_tj012_zaqi_selection.json (6 zaqi cases, real birth instants)
- tests/golden_tj012_luren_route.json (9 route cases, real birth instants)
- pillar sets already used by tests/test_phase2_bazipattern.py for the
  official / resource candidate blocks (Golden 20 / 42 in the sealed
  phase2_execution.json; replayed here through the live candidate code).

``broken`` is never a legitimate engine output: no per-pattern 破格
condition is reviewed anywhere in the sealed tree.
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_core import chart_from_datetime, chart_from_pillars
from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.bazi_pattern_engine import (
    PATTERNS,
    evaluate_all,
    evaluate_pattern,
    evaluate_patterns_from_trace,
)
from tianji_kb.bazi_siling_pilot import yin_siling_pilot
from tianji_kb.operations.bazi_chart import chart as chart_op

ROOT = Path(__file__).resolve().parents[1]
REN_YIN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_ren_yin_true.json').read_text('utf-8'))
ZAQI_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_zaqi_selection.json').read_text('utf-8'))
LUREN_GOLDEN = json.loads(
    (ROOT / 'tests/golden_tj012_luren_route.json').read_text('utf-8'))

TWELVE_KEYS = [key for key, _, _ in PATTERNS]


def _chart(*pillars):
    return chart_from_pillars(*pillars)


def _state(out, key):
    return out['results'][key]['state']


def _evidence_ids(out, key):
    return {e['id'] for e in out['results'][key]['evidence']}


def _pilot_for(birth_value):
    year = birth_value[:4]
    window = REN_YIN_GOLDEN['jie_windows'][year]
    return yin_siling_pilot(
        birth_value, version_id='ditiansui-yuanshuo',
        jie_facts={'provider': dict(REN_YIN_GOLDEN['provider']),
                   'lichun': dict(window['lichun']),
                   'next_jie': dict(window['next_jie'])})


def _trace_engine(pillars, birth_value=None):
    """Run the trace path: chart() with the pattern variant, then the
    engine over the executed trace (real pilot when a birth is given).
    The pilot block itself -- not the D-1 determination -- is the
    explicit Slice C input (adjudication D4)."""
    pilot = _pilot_for(birth_value) if birth_value else None
    out = chart_op(*pillars, pattern_variant=PATTERN_VARIANT,
                   ren_yin_pilot_result=pilot)
    trace = {'trace': out['trace'], 'evidence': out['evidence']}
    return evaluate_patterns_from_trace(trace, pilot_result=pilot), out


class ShapeTests(unittest.TestCase):
    def test_twelve_patterns_governance_and_shape(self):
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(set(out['results']), set(TWELVE_KEYS))
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public'])
        self.assertFalse(out['ai'])
        self.assertIsNone(out['strength_overall'])
        for key, result in out['results'].items():
            self.assertTrue(set(result) >= {
                'pattern', 'state', 'evidence', 'limitations'},
                key)
            self.assertIn(result['state'], (
                'candidate', 'established', 'broken', 'conflict',
                'not_judgeable'), key)
            self.assertTrue(result['research_only'], key)
            self.assertFalse(result['public'], key)
            self.assertFalse(result['ai'], key)
            self.assertTrue(result['evidence'], key)
            self.assertTrue(result['limitations'], key)

    def test_unknown_pattern_key_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_pattern(_chart('戊午', '辛酉', '甲午', '丙午'), 'nope')

    def test_broken_is_never_emitted(self):
        battery = [
            ('戊午', '辛酉', '甲午', '庚午'),
            ('戊午', '辛酉', '甲午', '丙午'),
            ('癸亥', '壬子', '甲寅', '癸酉'),
            ('丙寅', '壬申', '甲子', '乙丑'),
            ('壬辰', '癸丑', '己未', '庚午'),
            ('己丑', '丙寅', '甲戌', '己巳'),
            ('戊午', '丁巳', '戊辰', '庚申'),
            ('己丑', '甲戌', '戊寅', '己未'),
        ]
        for pillars in battery:
            out = evaluate_all(_chart(*pillars))
            self.assertNotIn('broken', out['counts'], pillars)


class OfficialTests(unittest.TestCase):
    def test_month_hidden_official_is_candidate(self):
        # 甲日酉月藏辛正官，透于月干；时柱无七杀。
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertIn('month_hidden_god', _evidence_ids(out, 'zhengguan'))
        self.assertIn('bazi.phase2.official_pattern_candidates',
                      out['results']['zhengguan']['rule_ids'])

    def test_hour_killing_is_conflict_not_broken(self):
        # 同盘而时干庚为七杀：s055 只追加审核，不定混杂、不定破格。
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '庚午'))
        self.assertEqual(_state(out, 'zhengguan'), 'conflict')
        self.assertIn('hour_killing_restriction_s055',
                      _evidence_ids(out, 'zhengguan'))
        self.assertNotEqual(_state(out, 'zhengguan'), 'broken')

    def test_scattered_visible_official_is_not_a_pattern(self):
        # 反证：辛透于年干、月支寅无藏官——散见官星不导入月令取格。
        out = evaluate_all(_chart('辛酉', '丙寅', '甲子', '庚午'))
        self.assertEqual(_state(out, 'zhengguan'), 'not_judgeable')

    def test_yuanhai_unexposed_branch_observed(self):
        # 甲日酉月、辛不透、巳酉丑齐备：s056 单例分支观察。
        out = evaluate_all(_chart('乙巳', '癸酉', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertIn('yuanhai_unexposed_official_s056',
                      _evidence_ids(out, 'zhengguan'))

    def test_yuanhai_branch_counterexample_xin_exposed(self):
        # 反证：辛透干与“不透”例直接矛盾，分支不适用（仍为月藏候选）。
        out = evaluate_all(_chart('辛巳', '癸酉', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertNotIn('yuanhai_unexposed_official_s056',
                         _evidence_ids(out, 'zhengguan'))


class ResourceTests(unittest.TestCase):
    def test_month_hidden_resource_is_candidate(self):
        # 甲日亥月藏壬偏印；甲日亥子月为渊海 s059 生我例。
        out = evaluate_all(_chart('癸亥', '壬子', '甲寅', '癸酉'))
        self.assertEqual(_state(out, 'zhengyin'), 'candidate')
        self.assertIn('yuanhai_resource_month_example_s059',
                      _evidence_ids(out, 'zhengyin'))
        self.assertIn('bazi.phase2.resource_pattern_candidates',
                      out['results']['zhengyin']['rule_ids'])

    def test_resource_with_visible_wealth_stays_candidate(self):
        # 戊偏财与月藏印共现：方向已见、效力 indeterminate，不判破印。
        out = evaluate_all(_chart('戊午', '癸亥', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'pianyin'), 'candidate')
        self.assertIn('resource_context_visible_wealth',
                      _evidence_ids(out, 'pianyin'))
        self.assertNotEqual(_state(out, 'pianyin'), 'broken')

    def test_no_month_resource_is_not_judgeable(self):
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'zhengyin'), 'not_judgeable')
        self.assertEqual(_state(out, 'pianyin'), 'not_judgeable')


class ObservationOnlyTests(unittest.TestCase):
    def test_qisha_wealth_food_are_observation_only(self):
        # 丙日申月：庚偏财、壬七杀、戊食神皆为月藏观察，无独立候选规则。
        out = evaluate_all(_chart('甲子', '丙申', '丙午', '丁酉'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        self.assertEqual(_state(out, 'piancai'), 'candidate')
        self.assertEqual(_state(out, 'shishen'), 'candidate')
        self.assertEqual(out['results']['qisha']['rule_ids'], [])
        self.assertEqual(out['results']['piancai']['rule_ids'], [])
        self.assertEqual(_state(out, 'zhengguan'), 'not_judgeable')
        self.assertEqual(_state(out, 'shangguan'), 'not_judgeable')

    def test_shangguan_month_hidden_is_candidate(self):
        # 乙日巳月藏丙伤官（午藏丁为食神，不可混用）。
        out = evaluate_all(_chart('甲子', '辛巳', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')


class LurenTests(unittest.TestCase):
    def test_jianlu_month_is_not_judgeable(self):
        # 甲日寅月：禄支当月，路线关闭；建禄本身无成格依据。
        out = evaluate_all(_chart('己丑', '丙寅', '甲戌', '己巳'))
        self.assertEqual(_state(out, 'jianlu'), 'not_judgeable')
        self.assertIn('luren_route_exclusion',
                      _evidence_ids(out, 'jianlu'))

    def test_yangren_month_is_not_judgeable(self):
        # 庚日酉月：刃支当月，路线关闭。
        out = evaluate_all(_chart('己丑', '癸酉', '庚戌', '丙戌'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('luren_route_exclusion',
                      _evidence_ids(out, 'yangren'))

    def test_yin_stem_has_no_ren_branch(self):
        # 乙日卯月：阴干无刃（三命纲句）。
        out = evaluate_all(_chart('己丑', '丁卯', '乙亥', '癸未'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('yin_stem_no_ren', _evidence_ids(out, 'yangren'))

    def test_ordinary_month_has_no_luren_fact(self):
        out = evaluate_all(_chart('己丑', '庚午', '甲戌', '戊辰'))
        self.assertEqual(_state(out, 'jianlu'), 'not_judgeable')
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('no_luren_observation',
                      _evidence_ids(out, 'jianlu'))


class ZaqiTests(unittest.TestCase):
    def test_miscellaneous_month_is_conflict(self):
        # 己日丑月：原注 vs 三命杂气格名目冲突并列，不定格。
        out = evaluate_all(_chart('壬辰', '癸丑', '己未', '庚午'))
        self.assertEqual(_state(out, 'zaqi'), 'conflict')
        self.assertIn('zaqi_conflict', _evidence_ids(out, 'zaqi'))
        self.assertIn('zaqi_selected_candidates',
                      _evidence_ids(out, 'zaqi'))

    def test_non_miscellaneous_month_not_applicable(self):
        out = evaluate_all(_chart('己丑', '丙寅', '甲戌', '己巳'))
        self.assertEqual(_state(out, 'zaqi'), 'not_judgeable')

    def test_zaqi_golden_cases_are_conflict(self):
        for case in ZAQI_GOLDEN['cases']:
            out = evaluate_all(_chart(*case['pillars']))
            if case['month_branch'] in ('辰', '戌', '丑', '未'):
                self.assertEqual(_state(out, 'zaqi'), 'conflict',
                                 case['id'])
            else:
                self.assertEqual(_state(out, 'zaqi'), 'not_judgeable',
                                 case['id'])


class SpecialAndEarthTests(unittest.TestCase):
    def test_special_is_always_not_judgeable(self):
        for pillars in [('戊午', '辛酉', '甲午', '丙午'),
                        ('壬辰', '癸丑', '己未', '庚午'),
                        ('甲辰', '丙寅', '乙巳', '戊寅')]:
            out = evaluate_all(_chart(*pillars))
            self.assertEqual(_state(out, 'special'), 'not_judgeable',
                             pillars)
            self.assertIn('no_special_pattern_rule',
                          _evidence_ids(out, 'special'))

    def test_earth_gate_wu_si(self):
        # 戊日巳月：月藏丙偏印本可候选，TJ-011.2 土门一律不判。
        out = evaluate_all(_chart('戊午', '丁巳', '戊辰', '庚申'))
        self.assertTrue(out['earth_gate'])
        for key in TWELVE_KEYS:
            self.assertEqual(_state(out, key), 'not_judgeable', key)

    def test_earth_gate_ji_wu(self):
        out = evaluate_all(_chart('己丑', '庚午', '己未', '丙寅'))
        self.assertTrue(out['earth_gate'])
        for key in TWELVE_KEYS:
            self.assertEqual(_state(out, key), 'not_judgeable', key)


class RenYinGoldenTests(unittest.TestCase):
    def test_established_patterns_match_golden(self):
        want = {'t1-wu-zhengcai': ('zhengcai', '正财'),
                't2-bing-qisha': ('qisha', '七杀'),
                't3-jia-pianyin': ('pianyin', '偏印'),
                't4-jia-shishen': ('shishen', '食神'),
                'f2-boundary-exact': ('shangguan', '伤官')}
        cases = {c['id']: c for c in REN_YIN_GOLDEN['cases']}
        for case_id, (key, pattern) in want.items():
            case = cases[case_id]
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            result = engine['results'][key]
            self.assertEqual(result['state'], 'established', case_id)
            self.assertEqual(result['pattern'], pattern, case_id)
            self.assertIn('ren_yin_true_pattern',
                          {e['id'] for e in result['evidence']}, case_id)

    def test_bijian_established_via_d1(self):
        for case_id in ('a2-wu-daymaster-pos', 'a4-bing-daymaster-pos'):
            case = next(c for c in REN_YIN_GOLDEN['cases']
                        if c['id'] == case_id)
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertIn('bijian', engine['results'], case_id)
            self.assertEqual(engine['results']['bijian']['state'],
                             'established', case_id)
            self.assertIn('pattern_name_not_public',
                          ' '.join(engine['results']['bijian']
                                   ['limitations']), case_id)

    def test_commander_not_visible_stays_candidate(self):
        # n1：庚日寅月，司令戊（偏印）不透——无真格，不标假格。
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 'n1-touchstone')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['pianyin']
        self.assertEqual(result['state'], 'candidate')
        self.assertIn('ren_yin_commander_not_visible',
                      {e['id'] for e in result['evidence']})
        self.assertNotIn('broken', engine['counts'])

    def test_route_precedence_abstains_d1(self):
        # s3：甲日寅月，禄刃路线优先关闭，D-1 不达司令步。
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 's3-route-precedence')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        self.assertNotIn('established', engine['counts'])
        self.assertEqual(_state(engine, 'jianlu'), 'not_judgeable')

    def test_non_yin_month_has_no_d1_establishment(self):
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 's1-non-yin')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        self.assertNotIn('established', engine['counts'])


class TracePathTests(unittest.TestCase):
    def test_trace_path_without_pilot_establishes_nothing(self):
        engine, out = _trace_engine(('甲辰', '丙寅', '乙巳', '戊寅'))
        self.assertNotIn('established', engine['counts'])
        # Trace blocks were consumed: 乙日寅月藏戊为正财，仍为候选观察。
        self.assertEqual(_state(engine, 'zhengcai'), 'candidate')
        self.assertEqual(out['result']['pattern_route']['route'],
                         'not_luren')

    def test_trace_path_missing_steps_fail_closed(self):
        with self.assertRaises(ValueError):
            evaluate_patterns_from_trace({'trace': [], 'evidence': {}})


class RealBirthExamplesTests(unittest.TestCase):
    def test_real_birth_t1_zhengcai_established(self):
        value = '2024-02-11T04:00:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['甲辰', '丙寅', '乙巳', '戊寅'])
        engine, _ = _trace_engine(
            tuple(p['ganzhi'] for p in chart['pillars']), value)
        self.assertEqual(_state(engine, 'zhengcai'), 'established')

    def test_real_birth_1949_luren(self):
        value = '1949-02-13T09:30:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['己丑', '丙寅', '甲戌', '己巳'])
        out = evaluate_all(chart)
        self.assertEqual(_state(out, 'jianlu'), 'not_judgeable')
        self.assertEqual(_state(out, 'zaqi'), 'not_judgeable')

    def test_real_birth_1953_zaqi_conflict(self):
        value = '1953-01-08T11:30:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['壬辰', '癸丑', '己未', '庚午'])
        out = evaluate_all(chart)
        self.assertEqual(_state(out, 'zaqi'), 'conflict')


if __name__ == '__main__':
    unittest.main()
