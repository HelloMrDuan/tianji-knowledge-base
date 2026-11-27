"""TJ-0424 pattern engine: one evaluator per pattern, research_only.

Anchors (public worktree Golden files, no sealed text copied):
- tests/golden_tj012_ren_yin_true.json (15 D-1 cases, real birth instants)
- tests/golden_tj012_zaqi_selection.json (6 zaqi cases, real birth instants)
- tests/golden_tj012_luren_route.json (9 route cases, real birth instants)
- pillar sets already used by tests/test_phase2_bazipattern.py for the
  official / resource candidate blocks (Golden 20 / 42 in the sealed
  phase2_execution.json; replayed here through the live candidate code).

v2 (TJ-0425 pattern batch): each ten-god candidate now carries the
condition facts registered in the public Yuanhai section registrations
(``bazi_yuanhai_{qisha,cai,shishang,zhengguan,yin,luren,cong}``) --
presence is computed from the pillars, efficacy is never judged;
官杀混杂 carries two parallel Variants (s055 / 《论官杀混杂要制伏》);
杂气 carries three parallel Variants (原注 / 三命 / 子平真诠 Ch16);
特殊格局 carries four separated candidate screens (从杀 / 从财 /
现代从格屏 / 化气). Established is still only Ren D-1, now proven for
正官 / 正印 / 偏财 as well (real 2023 births found by scanning the
寅月 pilot, not Golden cases).

v3 (TJ-0424 pattern batch 3, this file's route only): condition-fact
coverage widened strictly inside registered material (暗藏官杀 yh.gt_hidden,
官星透/藏区分 yh.sw_not_exhausted_officer, 印/财/官在场与否诸事实,
偏印制杀 yh.ds_killing_control, 刃印/时财 yh.yr_preferences /
yh.rr_hour_wealth_taboo, 杂气月藏全清单 + 透干位置, 从杀论十条例句
结构比对, 支六合入化气屏 / 三合支齐备只作事实）; every per-pattern
破格缺口 registered as a named table (``BROKEN_GAPS``, surfaced per
result as ``broken_gaps``); P6 two blocking gates recorded in
``BLOCKING_GATES``, never decided, never thresholded. Variant stays
v2 on purpose (combination engine pins v2 by exact match). All 15
Ren D-1 Golden cases are now exercised: 5 established, 5
commander_not_visible, 2 bijian, route-precedence, non-yin month,
pilot-uncertain.

P1--P6 batch (this file's route only, user adjudication 2026-11-25):
one classical ``broken`` channel -- 伤官见官 on a Ren D-1 established
伤官格 with 正官在场 (Golden f2-boundary-exact is the first broken
case; ``broken`` otherwise never fires) -- plus the additive modern
layer (``modern_assessment``, ``pattern-modern-p6-v1``: P6 身旺门 /
伤尽标尺, P1 modern establishment, P4 modern root / extreme-weak /
assembly screens, P5 modern broken flags, P2 retention observation,
P3 conditional 土格换算 mapping). A1: ``evaluate_all`` always returns
the two extra ten-god results (比肩/劫财, not_judgeable unless D-1
establishes them), so the suite counts 14 results, not 12; the
commander_not_visible fact lands on the extra result whose god the
commander is (Golden a1/a3). A2: every result -- including the
non-miscellaneous 杂气 branch and the TJ-011.2 earth gate -- carries
a 破格缺口 limitation. B1: the five 从格例句 test charts are truly
rootless (verified by probe: ``structural_roots()`` empty). B2: the
three impossible pillars are corrected to valid sexagenary pillars;
the 时刃时财 hour check counts 财星 (正财 + 偏财) per the cited
“财乡”句 -- with 偏财 only it was unreachable for 甲/庚日 valid
charts (their blade branches 卯/酉 are 阴支); 丙/戊/壬日 were
already reachable (庚午/壬午/丙子).

``broken`` is emitted only through the one reviewed 伤官见官 channel:
a Ren D-1 established 伤官格 with 正官在场. Every other pattern's
``broken`` remains unreviewed.
"""
import json
from pathlib import Path
import unittest

from tianji_kb.bazi_core import chart_from_datetime, chart_from_pillars
from tianji_kb.bazi_pattern import PATTERN_VARIANT
from tianji_kb.bazi_pattern_engine import (
    BLOCKING_GATES,
    BROKEN_GAPS,
    MODERN_MODEL_ID,
    PATTERN_ENGINE_VARIANT,
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
# A1: evaluate_all always returns the two extra ten-god results as
# well (not_judgeable unless Ren D-1 establishes them).
ALL_KEYS = TWELVE_KEYS + ['bijian', 'jiecai']


def _modern(out, key):
    return out['results'][key]['modern_assessment']


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
        # A1: twelve patterns plus the two always-present extras.
        self.assertEqual(set(out['results']), set(ALL_KEYS))
        self.assertEqual(out['modern_model'], MODERN_MODEL_ID)
        self.assertEqual(out['modern_model'], 'pattern-modern-p6-v1')
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public'])
        self.assertFalse(out['ai'])
        self.assertIsNone(out['strength_overall'])
        self.assertEqual(sum(out['counts'].values()), 14)
        for key, result in out['results'].items():
            self.assertTrue(set(result) >= {
                'pattern', 'state', 'evidence', 'limitations',
                'modern_assessment'},
                key)
            self.assertIn(result['state'], (
                'candidate', 'established', 'broken', 'conflict',
                'not_judgeable'), key)
            self.assertTrue(result['research_only'], key)
            self.assertFalse(result['public'], key)
            self.assertFalse(result['ai'], key)
            self.assertTrue(result['evidence'], key)
            self.assertTrue(result['limitations'], key)
            modern = result['modern_assessment']
            self.assertEqual(modern['model_id'], MODERN_MODEL_ID, key)
            self.assertEqual(modern['model_kind'], 'modern_engineering',
                             key)
            self.assertTrue(modern['research_only'], key)
            self.assertFalse(modern['public'], key)
            self.assertFalse(modern['ai'], key)

    def test_unknown_pattern_key_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_pattern(_chart('戊午', '辛酉', '甲午', '丙午'), 'nope')

    def test_broken_only_via_reviewed_shangguan_channel(self):
        # No D-1 pilot runs through evaluate_all, so no chart in this
        # battery can be broken: 财破印在场、伤官见官在场（候选前提）、
        # 杀多在场、官杀混杂在场——皆只作候选 / 冲突，永不破格。
        # The single classical broken channel needs a Ren D-1
        # established 伤官格 (see ClassicalBrokenTests, Golden f2).
        battery = [
            ('戊午', '辛酉', '甲午', '庚午'),
            ('戊午', '辛酉', '甲午', '丙午'),
            ('癸亥', '壬子', '甲寅', '癸酉'),
            ('丙寅', '壬申', '甲子', '乙丑'),
            ('壬辰', '癸丑', '己未', '庚午'),
            ('己丑', '丙寅', '甲戌', '己巳'),
            ('戊午', '丁巳', '戊辰', '庚申'),
            ('己丑', '甲戌', '戊寅', '己未'),
            ('戊午', '癸亥', '甲子', '乙丑'),
            ('庚申', '辛巳', '乙丑', '丙子'),
            ('甲子', '丙申', '丙午', '壬辰'),
            ('丙寅', '辛酉', '甲午', '庚申'),
            ('癸酉', '庚子', '丁酉', '庚子'),
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
    def test_special_is_not_judgeable_without_screen_hit(self):
        # Batch 3: 午未六合入化气屏后，旧例（壬辰/癸丑/己未/庚午）已
        # 改判为候选（见 test_six_harmony_reclassifies_former_miss），
        # 故改用无五合、无六合、无三合的盘：乙巳/丁酉/己亥/癸酉。
        # 从杀论例句比对命中（戊己亥月）只记事实，不改状态。
        for pillars in [('乙巳', '丁酉', '己亥', '癸酉'),
                        ('甲辰', '丙寅', '乙巳', '戊寅')]:
            out = evaluate_all(_chart(*pillars))
            self.assertEqual(_state(out, 'special'), 'not_judgeable',
                             pillars)
            self.assertIn('no_special_pattern_rule',
                          _evidence_ids(out, 'special'))

    def test_six_harmony_reclassifies_former_miss(self):
        # 旧无命中例：壬辰/癸丑/己未/庚午——午未六合在场，第三批起
        # 化气结构屏命中，只作候选，永不判化气格成立。
        out = evaluate_all(_chart('壬辰', '癸丑', '己未', '庚午'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        self.assertIn('huaqi_six_harmony_screen',
                      _evidence_ids(out, 'special'))
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_special_congcai_screen_hit_is_candidate_not_established(self):
        # 戊午/辛酉/甲午/丙午：财在场、无结构根、无七杀、无比劫分夺——
        # 从财结构屏命中，只作候选，永不判从财格成立。
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        self.assertIn('congcai_screen_hit', _evidence_ids(out, 'special'))
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_earth_gate_wu_si(self):
        # 戊日巳月：月藏丙偏印本可候选，TJ-011.2 土门一律不判。
        out = evaluate_all(_chart('戊午', '丁巳', '戊辰', '庚申'))
        self.assertTrue(out['earth_gate'])
        for key in ALL_KEYS:
            self.assertEqual(_state(out, key), 'not_judgeable', key)
            self.assertIsNone(out['results'][key]['modern_assessment'],
                              key)

    def test_earth_gate_ji_wu(self):
        out = evaluate_all(_chart('己丑', '庚午', '己未', '丙寅'))
        self.assertTrue(out['earth_gate'])
        for key in ALL_KEYS:
            self.assertEqual(_state(out, key), 'not_judgeable', key)


class RenYinGoldenTests(unittest.TestCase):
    def test_established_patterns_match_golden(self):
        want = {'t1-wu-zhengcai': ('zhengcai', '正财'),
                't2-bing-qisha': ('qisha', '七杀'),
                't3-jia-pianyin': ('pianyin', '偏印'),
                't4-jia-shishen': ('shishen', '食神')}
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

    def test_f2_shangguan_is_broken_not_established(self):
        # P5: f2 成立伤官格（乙日寅月司令丙透）且正官在场（申藏庚），
        # 伤官见官古典通道开启：broken 取代 established。
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 'f2-boundary-exact')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['shangguan']
        self.assertEqual(result['state'], 'broken')
        self.assertEqual(result['pattern'], '伤官')
        ids = {e['id'] for e in result['evidence']}
        self.assertIn('ren_yin_true_pattern', ids)
        self.assertIn('shangguan_sees_officer_broken', ids)
        self.assertIn('bazi.phase2.ren_yin_true_pattern',
                      result['rule_ids'])

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


class QishaConditionTests(unittest.TestCase):
    def test_control_present_vs_absent_differ(self):
        # 制伏在场：丙日申月藏壬七杀，戊食神透时干。
        out = evaluate_all(_chart('甲子', '丙申', '丙午', '戊戌'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        self.assertIn('qisha_control_present', _evidence_ids(out, 'qisha'))
        self.assertIn('qisha_positions', _evidence_ids(out, 'qisha'))
        self.assertIn('qisha_wealth_feeds', _evidence_ids(out, 'qisha'))
        self.assertIn('qisha_blade_present', _evidence_ids(out, 'qisha'))
        # 制伏不在场：丙日子月藏壬七杀，四柱无戊己食伤。
        out = evaluate_all(_chart('甲子', '癸亥', '丙子', '丁酉'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        self.assertIn('qisha_control_absent', _evidence_ids(out, 'qisha'))
        self.assertNotIn('qisha_control_present',
                         _evidence_ids(out, 'qisha'))

    def test_combined_killing_and_many_positions(self):
        # 甲日申月藏庚七杀，乙年干合庚（贪合忘杀事实）；杀 2 处。
        out = evaluate_all(_chart('乙丑', '庚申', '甲子', '丙寅'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        ids = _evidence_ids(out, 'qisha')
        self.assertIn('qisha_combined_killing', ids)
        self.assertIn('qisha_many_positions', ids)

    def test_hour_killing_and_seven_days(self):
        # 时干壬七杀（时七杀句）与甲申日（七日列举）。
        out = evaluate_all(_chart('甲子', '丙申', '丙午', '壬辰'))
        self.assertIn('qisha_hour_position', _evidence_ids(out, 'qisha'))
        self.assertIn('qisha_many_positions', _evidence_ids(out, 'qisha'))
        out = evaluate_all(_chart('乙丑', '庚申', '甲申', '丙寅'))
        self.assertIn('qisha_day_position', _evidence_ids(out, 'qisha'))
        self.assertIn('qisha_seven_days', _evidence_ids(out, 'qisha'))

    def test_established_qisha_carries_conditions(self):
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 't2-bing-qisha')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['qisha']
        self.assertEqual(result['state'], 'established')
        self.assertIn('qisha_positions',
                      {e['id'] for e in result['evidence']})
        # t2 辰支藏癸伤官：制伏在场事实（效力未裁定）。
        self.assertIn('qisha_control_present',
                      {e['id'] for e in result['evidence']})
        self.assertTrue(any('破格缺口' in lim for lim in result['limitations']))


class WealthConditionTests(unittest.TestCase):
    def test_robbery_and_officer_and_food_present(self):
        # 甲日未月藏己正财：乙劫财透时干、辛官藏丑支、丁伤官藏月支。
        out = evaluate_all(_chart('丙子', '己未', '甲午', '乙丑'))
        self.assertEqual(_state(out, 'zhengcai'), 'candidate')
        ids = _evidence_ids(out, 'zhengcai')
        self.assertIn('wealth_positions', ids)
        self.assertIn('wealth_many_positions', ids)
        self.assertIn('wealth_robbery_present', ids)
        self.assertIn('wealth_officer_present', ids)
        self.assertIn('wealth_food_generates', ids)
        self.assertIn('wealth_shangguan_sees_wealth', ids)

    def test_piancai_exposure_and_many(self):
        # 甲日戌月藏戊偏财透年干；财 2 处以上。
        out = evaluate_all(_chart('戊辰', '庚戌', '甲午', '丙寅'))
        self.assertEqual(_state(out, 'piancai'), 'candidate')
        ids = _evidence_ids(out, 'piancai')
        self.assertIn('piancai_exposure', ids)
        self.assertIn('wealth_many_positions', ids)

    def test_established_zhengcai_carries_conditions(self):
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 't1-wu-zhengcai')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['zhengcai']
        self.assertEqual(result['state'], 'established')
        self.assertIn('wealth_positions',
                      {e['id'] for e in result['evidence']})
        self.assertTrue(any('破格缺口' in lim for lim in result['limitations']))


class FoodConditionTests(unittest.TestCase):
    def test_shangguan_sees_officer_stays_candidate(self):
        # 乙日巳月藏丙伤官，庚正官透年干：伤官见官事实，不判破格。
        out = evaluate_all(_chart('庚申', '辛巳', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')
        self.assertIn('shangguan_sees_officer',
                      _evidence_ids(out, 'shangguan'))
        self.assertNotEqual(_state(out, 'shangguan'), 'broken')

    def test_shangguan_exhausted_is_observation_not_established(self):
        # 甲日午月藏丁伤官，四柱无官杀：伤尽结构观察，仍只作候选。
        out = evaluate_all(_chart('丙子', '丙午', '甲寅', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')
        self.assertIn('shangguan_exhausted_observation',
                      _evidence_ids(out, 'shangguan'))
        self.assertNotEqual(_state(out, 'shangguan'), 'established')

    def test_shishen_seized_by_seal_stays_candidate(self):
        # 甲日寅月藏丙食神透月干，壬偏印透年干：倒食事实，不判破格。
        out = evaluate_all(_chart('壬子', '丙寅', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'shishen'), 'candidate')
        self.assertIn('shishen_seized_by_seal',
                      _evidence_ids(out, 'shishen'))
        self.assertIn('shishen_generates_wealth',
                      _evidence_ids(out, 'shishen'))

    def test_established_food_carries_conditions(self):
        cases = {c['id']: c for c in REN_YIN_GOLDEN['cases']}
        case = cases['t4-jia-shishen']
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['shishen']
        self.assertEqual(result['state'], 'established')
        self.assertTrue(any('破格缺口' in lim
                            for lim in result['limitations']))
        # P5: f2 成立伤官格 + 正官在场 → broken，仍附条件事实与缺口。
        case = cases['f2-boundary-exact']
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['shangguan']
        self.assertEqual(result['state'], 'broken')
        self.assertIn('shangguan_sees_officer_broken',
                      {e['id'] for e in result['evidence']})
        self.assertTrue(any('破格缺口' in lim
                            for lim in result['limitations']))


class OfficialExpansionTests(unittest.TestCase):
    def test_other_pillar_killing_is_fact_not_conflict(self):
        # 甲日酉月藏辛正官，庚七杀只藏年支巳：s055 只论时干支逢杀，
        # 他柱杀只记事实，仍为候选。
        out = evaluate_all(_chart('辛巳', '癸酉', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertIn('official_other_pillar_killing',
                      _evidence_ids(out, 'zhengguan'))
        self.assertNotIn('hour_killing_restriction_s055',
                         _evidence_ids(out, 'zhengguan'))

    def test_official_many_is_fact_not_broken(self):
        # 辛正官 3 处（年干、月干、月支藏）：官多事实，不判破格。
        out = evaluate_all(_chart('辛丑', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertIn('official_many_positions',
                      _evidence_ids(out, 'zhengguan'))

    def test_conflict_carries_two_variants_and_retention_fact(self):
        # 时干庚七杀 + 丙食神透年干：两 Variant 并列，去留条件事实在场。
        out = evaluate_all(_chart('丙寅', '辛酉', '甲午', '庚申'))
        self.assertEqual(_state(out, 'zhengguan'), 'conflict')
        ids = _evidence_ids(out, 'zhengguan')
        self.assertIn('guansha_variant_s055', ids)
        self.assertIn('guansha_variant_yuanhai_zhifu', ids)
        self.assertIn('guansha_retention_condition', ids)

    def test_established_zhengguan_real_birth_2023(self):
        # 辛日寅月，司令丙（正官）透时干：扫描所得真实出生 instant。
        value = '2023-02-12T16:00:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['癸卯', '甲寅', '辛丑', '丙申'])
        engine, _ = _trace_engine(
            tuple(p['ganzhi'] for p in chart['pillars']), value)
        self.assertEqual(_state(engine, 'zhengguan'), 'established')

    def test_established_piancai_real_birth_2023(self):
        # 庚日寅月，司令甲（偏财）透月干：扫描所得真实出生 instant。
        value = '2023-02-21T04:00:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['癸卯', '甲寅', '庚戌', '戊寅'])
        engine, _ = _trace_engine(
            tuple(p['ganzhi'] for p in chart['pillars']), value)
        self.assertEqual(_state(engine, 'piancai'), 'established')


class ResourceExpansionTests(unittest.TestCase):
    def test_wealth_breaks_seal_stays_candidate(self):
        # 甲日亥月藏壬偏印，戊偏财透年干：财破印事实，不判破格。
        out = evaluate_all(_chart('戊午', '癸亥', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'pianyin'), 'candidate')
        self.assertIn('resource_wealth_breaks_seal',
                      _evidence_ids(out, 'pianyin'))
        self.assertNotEqual(_state(out, 'pianyin'), 'broken')

    def test_officer_generates_seal_and_seal_seizes_food(self):
        # 辛官透年干（官印相生方向）与丙食神透年干（倒食事实）。
        out = evaluate_all(_chart('辛巳', '癸亥', '甲子', '乙丑'))
        self.assertIn('resource_officer_generates_seal',
                      _evidence_ids(out, 'pianyin'))
        out = evaluate_all(_chart('丙子', '癸亥', '甲子', '乙丑'))
        self.assertIn('resource_seal_seizes_food',
                      _evidence_ids(out, 'pianyin'))

    def test_established_zhengyin_real_birth_2023(self):
        # 丁日寅月，司令甲（正印）透月干：扫描所得真实出生 instant。
        value = '2023-02-18T16:00:00+08:00'
        chart = chart_from_datetime(value)
        self.assertEqual(
            [p['ganzhi'] for p in chart['pillars']],
            ['癸卯', '甲寅', '丁未', '戊申'])
        engine, _ = _trace_engine(
            tuple(p['ganzhi'] for p in chart['pillars']), value)
        self.assertEqual(_state(engine, 'zhengyin'), 'established')


class LurenExpansionTests(unittest.TestCase):
    def test_day_lu_position_is_fact_not_candidate(self):
        # 甲日卯月，日支寅为禄：日禄位置事实，仍不可判。
        out = evaluate_all(_chart('己丑', '癸卯', '甲寅', '丙戌'))
        self.assertEqual(_state(out, 'jianlu'), 'not_judgeable')
        self.assertIn('day_lu_position', _evidence_ids(out, 'jianlu'))

    def test_day_ren_enumerated_pillar(self):
        # 壬子日：日支子为刃，且在《论日刃》所列三柱内。
        out = evaluate_all(_chart('己丑', '癸卯', '壬子', '丙戌'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        ids = _evidence_ids(out, 'yangren')
        self.assertIn('day_ren_position', ids)
        self.assertIn('day_ren_enumerated', ids)
        self.assertIn('blade_killing_present', ids)

    def test_blade_killing_month(self):
        # 庚日酉月刃支当月，丙七杀透年干：刃杀俱全事实，仍不可判。
        out = evaluate_all(_chart('丙子', '癸酉', '庚戌', '丁丑'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('luren_route_exclusion',
                      _evidence_ids(out, 'yangren'))
        self.assertIn('blade_killing_present',
                      _evidence_ids(out, 'yangren'))


class ZaqiVariantTests(unittest.TestCase):
    def test_general_arm_has_three_variants(self):
        # 甲日辰月（一般臂）：三 Variant 并列，土格换算未裁定。
        out = evaluate_all(_chart('甲子', '戊辰', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'zaqi'), 'conflict')
        ids = _evidence_ids(out, 'zaqi')
        self.assertIn('zaqi_variant_yuanzhu', ids)
        self.assertIn('zaqi_variant_sanming', ids)
        self.assertIn('zaqi_variant_ziping', ids)
        self.assertIn('zaqi_earth_conversion_unadjudicated', ids)

    def test_wuji_arm_has_three_variants(self):
        # 己日丑月（戊己臂）：三 Variant 并列，选格对象仍只并列。
        out = evaluate_all(_chart('壬辰', '癸丑', '己未', '庚午'))
        self.assertEqual(_state(out, 'zaqi'), 'conflict')
        ids = _evidence_ids(out, 'zaqi')
        self.assertIn('zaqi_variant_yuanzhu', ids)
        self.assertIn('zaqi_variant_sanming', ids)
        self.assertIn('zaqi_variant_ziping', ids)
        self.assertIn('zaqi_selected_candidates', ids)


class SpecialScreenTests(unittest.TestCase):
    def test_congsha_screen_hit_is_candidate(self):
        # 丁日：癸七杀 3 处、无结构根、无制伏、无印比救援。
        out = evaluate_all(_chart('癸酉', '庚子', '丁酉', '庚子'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        ids = _evidence_ids(out, 'special')
        self.assertIn('congsha_screen_hit', ids)
        self.assertIn('cong_screen_miss_modern', ids)
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_congcai_screen_hit_is_candidate(self):
        # 丁日：庚辛财在场、无结构根、无七杀、无比劫分夺。
        out = evaluate_all(_chart('庚申', '辛酉', '丁酉', '庚申'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        ids = _evidence_ids(out, 'special')
        self.assertIn('congcai_screen_hit', ids)
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_huaqi_screen_hit_is_candidate(self):
        # 甲己五合在场：化气结构屏命中，仍只作候选。
        out = evaluate_all(_chart('己巳', '甲子', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        self.assertIn('huaqi_combination_screen',
                      _evidence_ids(out, 'special'))
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_congsha_screen_miss_names_root_veto(self):
        # 甲日申月：七杀在场但结构根（甲藏寅）与印（壬藏申）在场——
        # 根气一票否决与印救援并记。
        out = evaluate_all(_chart('乙丑', '庚申', '甲子', '丙寅'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        ids = _evidence_ids(out, 'special')
        self.assertIn('congsha_screen_miss', ids)
        self.assertIn('huaqi_combination_screen', ids)
        detail = ' '.join(e['detail']
                          for e in out['results']['special']['evidence'])
        self.assertIn('根气一票否决', detail)


class PerPatternCoverageTests(unittest.TestCase):
    """每格状态机实际运转证明：候选例 + 成立例（有成立通道者），
    或明确说明无成立例的原因（建禄 / 阳刃：禄刃路线优先关闭；
    杂气：四季月不在寅月 D-1 内；特殊：成立恒无依据）。"""

    def test_ten_god_patterns_have_candidate_and_established(self):
        cases = {
            'zhengguan': (('戊午', '辛酉', '甲午', '丙午'),
                          '2023-02-12T16:00:00+08:00'),
            'qisha': (('甲子', '丙申', '丙午', '戊戌'), None),
            'zhengyin': (('癸亥', '壬子', '甲寅', '癸酉'),
                         '2023-02-18T16:00:00+08:00'),
            'pianyin': (('戊午', '癸亥', '甲子', '乙丑'), None),
            'zhengcai': (('丙子', '己未', '甲午', '乙丑'), None),
            'piancai': (('戊辰', '庚戌', '甲午', '丙寅'),
                        '2023-02-21T04:00:00+08:00'),
            'shishen': (('壬子', '丙寅', '甲子', '乙丑'), None),
            'shangguan': (('庚申', '辛巳', '乙丑', '丙子'), None),
        }
        golden_established = {
            'qisha': 't2-bing-qisha', 'pianyin': 't3-jia-pianyin',
            'zhengcai': 't1-wu-zhengcai', 'shishen': 't4-jia-shishen',
        }
        for key, (pillars, birth) in cases.items():
            out = evaluate_all(_chart(*pillars))
            self.assertEqual(_state(out, key), 'candidate', key)
            if key == 'shangguan':
                # P5: f2 成立伤官格 + 正官在场 → broken（非 established）。
                case = next(c for c in REN_YIN_GOLDEN['cases']
                            if c['id'] == 'f2-boundary-exact')
                engine, _ = _trace_engine(
                    case['pillars'], case['source_birth']['value'])
                self.assertEqual(_state(engine, key), 'broken', key)
                continue
            if birth is not None:
                chart = chart_from_datetime(birth)
                engine, _ = _trace_engine(
                    tuple(p['ganzhi'] for p in chart['pillars']), birth)
                self.assertEqual(_state(engine, key), 'established', key)
            else:
                case = next(c for c in REN_YIN_GOLDEN['cases']
                            if c['id'] == golden_established[key])
                engine, _ = _trace_engine(
                    case['pillars'], case['source_birth']['value'])
                self.assertEqual(_state(engine, key), 'established', key)

    def test_no_established_channel_patterns(self):
        # 建禄 / 阳刃：日禄 / 日刃位置事实可算，但成格恒不可判。
        out = evaluate_all(_chart('己丑', '癸卯', '甲寅', '丙戌'))
        self.assertEqual(_state(out, 'jianlu'), 'not_judgeable')
        self.assertIn('day_lu_position', _evidence_ids(out, 'jianlu'))
        out = evaluate_all(_chart('己丑', '癸卯', '壬子', '丙戌'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('day_ren_enumerated', _evidence_ids(out, 'yangren'))
        # 杂气：四季月恒为冲突，三 Variant 并列，永无成立。
        out = evaluate_all(_chart('甲子', '戊辰', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'zaqi'), 'conflict')
        self.assertIn('zaqi_variant_ziping', _evidence_ids(out, 'zaqi'))
        # 特殊：屏命中只作候选，永无成立。
        out = evaluate_all(_chart('癸酉', '庚子', '丁酉', '庚子'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        self.assertIn('congsha_screen_hit', _evidence_ids(out, 'special'))


class Batch3QishaExpansionTests(unittest.TestCase):
    def test_hidden_officer_killing_gt_hidden(self):
        # 壬日、四柱支皆在辰戌丑未巳午、天干不露官杀：官杀暗藏事实。
        # 月支巳藏戊七杀为候选；午支藏己正官，故官星在场事实亦见。
        out = evaluate_all(_chart('庚辰', '辛巳', '壬午', '甲辰'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        ids = _evidence_ids(out, 'qisha')
        self.assertIn('qisha_hidden_officer_killing', ids)
        self.assertIn('qisha_official_present', ids)

    def test_official_absent_is_fact_not_gap(self):
        # 丙日申月藏壬七杀，四柱无癸：正官在场事实缺席，只记缺席。
        out = evaluate_all(_chart('甲寅', '丙申', '丙午', '戊戌'))
        self.assertEqual(_state(out, 'qisha'), 'candidate')
        self.assertNotIn('qisha_official_present',
                         _evidence_ids(out, 'qisha'))
        self.assertNotIn('qisha_hidden_officer_killing',
                         _evidence_ids(out, 'qisha'))


class Batch3OfficialExpansionTests(unittest.TestCase):
    def test_official_positions_and_seal_present(self):
        # 辛正官 2 处（月干透 + 月支藏），壬癸印在场，无七杀共现。
        out = evaluate_all(_chart('壬子', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        ids = _evidence_ids(out, 'zhengguan')
        self.assertIn('official_positions', ids)
        self.assertIn('official_seal_present', ids)
        self.assertNotIn('guansha_coexistence_count', ids)

    def test_guansha_coexistence_count(self):
        # 正官 2 处、七杀 2 处并见：只记数量，不定混杂、不定去留。
        out = evaluate_all(_chart('庚申', '辛酉', '甲午', '丙午'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        ids = _evidence_ids(out, 'zhengguan')
        self.assertIn('guansha_coexistence_count', ids)
        self.assertIn('official_many_positions', ids)
        self.assertNotEqual(_state(out, 'zhengguan'), 'conflict')


class Batch3WealthExpansionTests(unittest.TestCase):
    def test_wealth_seal_present_and_absence_check(self):
        # 甲日未月藏己正财：壬偏印透年干，乙劫财透时干，正官不在场。
        out = evaluate_all(_chart('壬子', '己未', '甲午', '乙丑'))
        self.assertEqual(_state(out, 'zhengcai'), 'candidate')
        ids = _evidence_ids(out, 'zhengcai')
        self.assertIn('wealth_seal_present', ids)
        self.assertIn('wealth_robbery_officer_absence', ids)

    def test_piancai_officer_brothers_contrast(self):
        # 甲日戌月藏戊偏财：辛官透年干、藏月支，乙劫财透时干。
        out = evaluate_all(_chart('辛巳', '庚戌', '甲午', '乙丑'))
        self.assertEqual(_state(out, 'piancai'), 'candidate')
        ids = _evidence_ids(out, 'piancai')
        self.assertIn('piancai_officer_brothers_contrast', ids)
        self.assertIn('wealth_officer_present', ids)
        self.assertIn('wealth_robbery_present', ids)


class Batch3FoodExpansionTests(unittest.TestCase):
    def test_shishen_single_position_and_seal_present(self):
        # 甲日巳月藏丙食神仅一处（月支藏），癸正印藏丑/子。
        # B2：原月柱庚巳非六十甲子（庚阳 / 巳阴）；改月柱为辛巳
        # （辛阴 / 巳阴合法；巳藏丙庚戊，食神仍仅月支藏一处）。
        out = evaluate_all(_chart('乙丑', '辛巳', '甲子', '丁卯'))
        self.assertEqual(_state(out, 'shishen'), 'candidate')
        ids = _evidence_ids(out, 'shishen')
        self.assertIn('shishen_single_position', ids)
        self.assertIn('shishen_seal_present', ids)
        self.assertNotIn('shishen_seized_by_seal', ids)

    def test_shangguan_officer_exposed(self):
        # 乙日巳月藏丙伤官，庚正官透年干：官星露事实。
        out = evaluate_all(_chart('庚申', '辛巳', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')
        ids = _evidence_ids(out, 'shangguan')
        self.assertIn('shangguan_officer_exposed', ids)
        self.assertNotIn('shangguan_officer_hidden_only', ids)

    def test_shangguan_officer_hidden_only(self):
        # 乙日巳月藏丙伤官，正官庚只藏年支申：藏而未露事实。
        out = evaluate_all(_chart('甲申', '辛巳', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')
        ids = _evidence_ids(out, 'shangguan')
        self.assertIn('shangguan_officer_hidden_only', ids)
        self.assertNotIn('shangguan_officer_exposed', ids)


class Batch3ResourceExpansionTests(unittest.TestCase):
    def test_pianyin_killing_control_fact(self):
        # 甲日亥月藏壬偏印：庚七杀透时干、藏申支，丙食神透年干。
        out = evaluate_all(_chart('丙子', '癸亥', '甲午', '庚申'))
        self.assertEqual(_state(out, 'pianyin'), 'candidate')
        self.assertIn('resource_seal_controls_killing',
                      _evidence_ids(out, 'pianyin'))

    def test_pianyin_killing_control_absent_without_killing(self):
        # 甲日亥月藏壬偏印，四柱无庚：制杀结构事实缺席。
        out = evaluate_all(_chart('戊午', '癸亥', '甲子', '乙丑'))
        self.assertEqual(_state(out, 'pianyin'), 'candidate')
        self.assertNotIn('resource_seal_controls_killing',
                         _evidence_ids(out, 'pianyin'))


class Batch3LurenExpansionTests(unittest.TestCase):
    def test_blade_seal_present(self):
        # 庚日酉月刃支当月，己正印藏丑支：喜印綬方向已见。
        out = evaluate_all(_chart('丙子', '癸酉', '庚戌', '丁丑'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        self.assertIn('blade_seal_present',
                      _evidence_ids(out, 'yangren'))

    def test_blade_wealth_hour_position(self):
        # 庚日酉月刃、时支酉为刃、时柱见财：时刃时财共现事实。
        # B2：原时柱甲酉非六十甲子（甲阳 / 酉阴）。甲申（申非刃支）与
        # 乙酉（乙为正财）皆不合原“偏财透时干”意图；且对庚日（刃酉为
        # 阴支）偏财-only 条件一切合法盘不可达：偏财甲为阳干、坐不上
        # 阴支酉，酉藏辛为劫财非偏财，故本测试盘非修引擎不可。引擎已
        # 按引文“财乡”（财星通称）修正时刃时财条件：时柱见正财亦记
        # 事实。年干改甲（偏财在场，blade_wealth_present 仍成立），
        # 时柱改乙酉。
        out = evaluate_all(_chart('甲子', '癸酉', '庚戌', '乙酉'))
        self.assertEqual(_state(out, 'yangren'), 'not_judgeable')
        ids = _evidence_ids(out, 'yangren')
        self.assertIn('blade_wealth_hour_position', ids)
        self.assertIn('blade_wealth_present', ids)


class Batch3ZaqiExpansionTests(unittest.TestCase):
    def test_zaqi_month_hidden_inventory_and_exposed_positions(self):
        # 己日丑月：月藏己辛癸全清单；癸偏财透于月干。
        out = evaluate_all(_chart('壬辰', '癸丑', '己未', '庚午'))
        self.assertEqual(_state(out, 'zaqi'), 'conflict')
        ids = _evidence_ids(out, 'zaqi')
        self.assertIn('zaqi_month_hidden_inventory', ids)
        detail = ' '.join(e['detail']
                          for e in out['results']['zaqi']['evidence'])
        self.assertIn('己（比肩）', detail)
        self.assertIn('辛（食神）', detail)
        self.assertIn('癸（偏财', detail)
        self.assertIn('透于', detail)


class Batch3CongExampleTests(unittest.TestCase):
    def test_bing_shen_month_match_is_fact_not_state(self):
        # 丙火申提、无根从杀例句结构相符：只记比对，不改状态。
        # B1：原盘（丙午/戊戌）日支午藏丁、时支戌藏丁，皆为丙火实根；
        # 换为丙子/戊辰（子、申、辰皆无丙丁藏干），探针核实无结构根。
        out = evaluate_all(_chart('甲子', '庚申', '丙子', '戊辰'))
        self.assertEqual(_state(out, 'special'), 'not_judgeable')
        self.assertIn('cong_example_match_bing_shen_month',
                      _evidence_ids(out, 'special'))

    def test_jia_yi_rootless_match(self):
        # 甲日申支、无结构根：甲乙无根、怕逢申酉例句结构相符。
        # B1：原盘时支卯藏乙为甲木实根；换为丁巳（巳藏丙庚戊，无甲乙）。
        out = evaluate_all(_chart('乙丑', '庚申', '甲午', '丁巳'))
        self.assertIn('cong_example_match_jia_yi_rootless',
                      _evidence_ids(out, 'special'))

    def test_yin_fire_follow_wealth_match(self):
        # 丁日酉月、无根、财在场：阴火酉月、弃命就财例句结构相符。
        out = evaluate_all(_chart('庚申', '辛酉', '丁酉', '庚申'))
        self.assertIn('cong_example_match_yin_fire_follow_wealth',
                      _evidence_ids(out, 'special'))

    def test_geng_rootless_match(self):
        # 庚日寅支、无结构根：庚金无根、寅宫火局例句结构相符。
        # B1：原盘日支戌藏辛、时支丑藏辛，皆为庚金实根；换为庚子/丁卯
        # （子藏癸、卯藏乙，无庚辛藏干）。
        out = evaluate_all(_chart('甲寅', '丙午', '庚子', '丁卯'))
        self.assertIn('cong_example_match_geng_rootless',
                      _evidence_ids(out, 'special'))

    def test_yang_yin_fire_pair_matches(self):
        # 丙日 / 丁日无根、水乡官杀在场：阳火必忌 / 阴火有救并列比对。
        # B1：丙盘原日支午藏丁、时支戌藏丁，皆为丙火实根；换为丙子/戊辰
        # （子、亥、辰皆无丙丁藏干）。丁盘本就无根，不动。
        out = evaluate_all(_chart('壬子', '癸亥', '丙子', '戊辰'))
        self.assertIn('cong_example_match_yang_fire_rootless',
                      _evidence_ids(out, 'special'))
        out = evaluate_all(_chart('壬子', '癸亥', '丁卯', '戊申'))
        self.assertIn('cong_example_match_yin_fire_rootless',
                      _evidence_ids(out, 'special'))

    def test_yi_you_month_lists_subfacts(self):
        # 乙木酉月：印在场、丑支在场、结构根在场并列，根级未裁。
        out = evaluate_all(_chart('甲辰', '辛酉', '乙丑', '丙子'))
        self.assertIn('cong_example_match_yi_you_month',
                      _evidence_ids(out, 'special'))
        detail = ' '.join(e['detail']
                          for e in out['results']['special']['evidence'])
        self.assertIn('丑支在场', detail)
        self.assertIn('结构根在场', detail)

    def test_yi_sitting_you_match(self):
        # 乙木坐酉、庚丁透露：日支酉、庚丁皆透干。
        out = evaluate_all(_chart('庚申', '辛酉', '乙酉', '丁丑'))
        self.assertIn('cong_example_match_yi_sitting_you',
                      _evidence_ids(out, 'special'))

    def test_wu_ji_hai_month_match(self):
        # 戊日亥月、无结构根：戊己亥月、身弱为弃例句结构相符。
        # B2：原日柱戊酉非六十甲子（戊阳 / 酉阴）；戊申虽合法但申藏戊
        # 为实根，违“无根”前提。改日柱为戊子（子藏癸，无戊己藏干）。
        out = evaluate_all(_chart('甲子', '癸亥', '戊子', '乙卯'))
        self.assertIn('cong_example_match_wu_ji_hai_month',
                      _evidence_ids(out, 'special'))

    def test_jia_ugly_month_match(self):
        # 甲日丑月、无结构根：甲木无根、生于丑月例句结构相符。
        # B1：原盘时支卯藏乙为甲木实根；换为丁巳（巳藏丙庚戊，无甲乙）。
        out = evaluate_all(_chart('乙丑', '癸丑', '甲申', '丁巳'))
        self.assertIn('cong_example_match_jia_ugly_month',
                      _evidence_ids(out, 'special'))

    def test_no_example_match_is_recorded(self):
        # 甲日寅月、无申酉支：十条例句均不相符，记无命中事实。
        out = evaluate_all(_chart('己丑', '丙寅', '甲戌', '己巳'))
        self.assertIn('cong_example_no_match',
                      _evidence_ids(out, 'special'))


class Batch3HuaqiExpansionTests(unittest.TestCase):
    def test_six_harmony_screen_hit_is_candidate(self):
        # 子丑六合在场、无天干五合：化气结构屏命中，只作候选。
        out = evaluate_all(_chart('丙子', '丁丑', '乙卯', '戊辰'))
        self.assertEqual(_state(out, 'special'), 'candidate')
        self.assertIn('huaqi_six_harmony_screen',
                      _evidence_ids(out, 'special'))
        self.assertNotIn('huaqi_combination_screen',
                         _evidence_ids(out, 'special'))
        self.assertNotEqual(_state(out, 'special'), 'established')

    def test_triple_harmony_is_fact_not_screen_hit(self):
        # 寅午戌三合支齐备、无五合、无六合：只记事实，不作屏命中。
        out = evaluate_all(_chart('甲寅', '丙午', '乙巳', '戊戌'))
        self.assertEqual(_state(out, 'special'), 'not_judgeable')
        self.assertIn('huaqi_triple_harmony_present',
                      _evidence_ids(out, 'special'))
        self.assertIn('huaqi_six_harmony_screen_miss',
                      _evidence_ids(out, 'special'))


class Batch3GoldenCompletenessTests(unittest.TestCase):
    def test_all_fifteen_golden_cases_exercised(self):
        cases = {c['id']: c for c in REN_YIN_GOLDEN['cases']}
        self.assertEqual(len(cases), 15)
        established = {'t1-wu-zhengcai': 'zhengcai',
                       't2-bing-qisha': 'qisha',
                       't3-jia-pianyin': 'pianyin',
                       't4-jia-shishen': 'shishen'}
        for case_id, key in established.items():
            case = cases[case_id]
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertEqual(_state(engine, key), 'established', case_id)
        # P5: f2 成立伤官格 + 正官在场 → broken（见
        # RenYinGoldenTests.test_f2_shangguan_is_broken_not_established）。
        case = cases['f2-boundary-exact']
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        self.assertEqual(_state(engine, 'shangguan'), 'broken',
                         'f2-boundary-exact')
        not_visible = ('n1-touchstone', 'f1-boundary-minus-1s',
                       'a1-wu-daymaster-neg', 'a3-bing-daymaster-neg',
                       'n2-jia-not-visible-2025')
        for case_id in not_visible:
            case = cases[case_id]
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertNotIn('established', engine['counts'], case_id)
            # A1: a1/a3 的司令十神为比肩，证据落在常驻的 bijian 格上；
            # 其余不透案落在八十神格上。故须遍历全部 14 格。
            self.assertTrue(
                any('ren_yin_commander_not_visible' in _evidence_ids(engine, k)
                    for k in ALL_KEYS), case_id)
        for case_id in ('a2-wu-daymaster-pos', 'a4-bing-daymaster-pos'):
            case = cases[case_id]
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertEqual(engine['results']['bijian']['state'],
                             'established', case_id)
        for case_id in ('s3-route-precedence', 's1-non-yin'):
            case = cases[case_id]
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertNotIn('established', engine['counts'], case_id)
        # s2-pilot-uncertain: no pilot computed -> D-1 abstains.
        case = cases['s2-pilot-uncertain']
        engine, _ = _trace_engine(case['pillars'], None)
        self.assertNotIn('established', engine['counts'], 's2-pilot-uncertain')

    def test_f1_boundary_minus_1s_is_commander_not_visible(self):
        # f1 与 f2 同柱、早 1 秒：司令戊（正财）不透，无真格、不标假格。
        case = next(c for c in REN_YIN_GOLDEN['cases']
                    if c['id'] == 'f1-boundary-minus-1s')
        engine, _ = _trace_engine(
            case['pillars'], case['source_birth']['value'])
        result = engine['results']['zhengcai']
        self.assertEqual(result['state'], 'candidate')
        self.assertIn('ren_yin_commander_not_visible',
                      {e['id'] for e in result['evidence']})
        self.assertNotIn('broken', engine['counts'])


class BrokenGapTableTests(unittest.TestCase):
    def test_every_pattern_has_named_broken_gaps(self):
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        for key, result in out['results'].items():
            self.assertEqual(
                result['broken_gaps'],
                [g['id'] for g in BROKEN_GAPS[key]], key)
            self.assertTrue(result['broken_gaps'], key)
            self.assertTrue(
                any('破格缺口' in lim for lim in result['limitations']),
                key)

    def test_earth_gate_results_carry_broken_gap_limitations(self):
        # A2 latent：戊×巳土门下全部 14 格亦须有破格缺口 limitation。
        for pillars in [('戊午', '丁巳', '戊辰', '庚申'),
                        ('己丑', '庚午', '己未', '丙寅')]:
            out = evaluate_all(_chart(*pillars))
            self.assertTrue(out['earth_gate'], pillars)
            for key, result in out['results'].items():
                self.assertTrue(
                    any('破格缺口' in lim for lim in result['limitations']),
                    (pillars, key))
                self.assertTrue(result['broken_gaps'], (pillars, key))

    def test_gap_table_entries_are_complete(self):
        for key, gaps in BROKEN_GAPS.items():
            for gap in gaps:
                self.assertTrue(gap['missing_basis'], (key, gap['id']))
                self.assertTrue(gap['missing_golden'], (key, gap['id']))
                self.assertTrue(gap['quotes'] or key in (
                    'jianlu', 'zaqi', 'special', 'bijian', 'jiecai'),
                    (key, gap['id']))
                if 'gate' in gap:
                    self.assertIn(gap['gate'], BLOCKING_GATES,
                                  (key, gap['id']))
                if 'status' in gap:
                    self.assertIn(gap['status'], (
                        'partially_resolved', 'modern_flag_only'),
                        (key, gap['id']))
        # P5: 伤官见官为唯一部分解决的缺口；其余已标注者仅现代旗标。
        shangguan = {g['id']: g for g in BROKEN_GAPS['shangguan']}
        self.assertEqual(
            shangguan['bg-food-shangguan-sees-officer']['status'],
            'partially_resolved')
        self.assertIn(
            'resolved_channel',
            shangguan['bg-food-shangguan-sees-officer'])
        self.assertEqual(
            {g['id']: g for g in BROKEN_GAPS['qisha']}
            ['bg-qisha-control-moderation']['status'],
            'modern_flag_only')

    def test_variant_stays_v2_for_combination_pin(self):
        # 组合引擎按 variant 精确匹配 v2；第三批为加法证据，不升版。
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(out['variant'], 'bazi-pattern-engine-v2')
        self.assertEqual(PATTERN_ENGINE_VARIANT,
                         'bazi-pattern-engine-v2')

    def test_p6_gates_recorded_not_decided(self):
        self.assertEqual(set(BLOCKING_GATES),
                         {'p6-shenwang-gate', 'p6-shangjin-scale'})
        for gate_id, gate in BLOCKING_GATES.items():
            self.assertEqual(gate['question'], 'P6', gate_id)
            self.assertEqual(gate['status'], 'recorded_not_decided',
                             gate_id)
            self.assertTrue(gate['blocks'], gate_id)
            # P1--P6: 现代标尺另立，不裁定古典门。
            self.assertEqual(gate['modern_scale'], MODERN_MODEL_ID,
                             gate_id)
        self.assertIn('shangguan',
                      BLOCKING_GATES['p6-shangjin-scale']['blocks'])
        self.assertIn('qisha',
                      BLOCKING_GATES['p6-shenwang-gate']['blocks'])
        self.assertIn('yangren',
                      BLOCKING_GATES['p6-shenwang-gate']['blocks'])


class A1ExtraResultsTests(unittest.TestCase):
    def test_all_fourteen_results_always_present(self):
        # A1: 比肩/劫财常驻（not_judgeable），不只在 D-1 成立时出现。
        for pillars in [('戊午', '辛酉', '甲午', '丙午'),
                        ('癸亥', '壬子', '甲寅', '癸酉'),
                        ('己丑', '丙寅', '甲戌', '己巳')]:
            out = evaluate_all(_chart(*pillars))
            self.assertIn('bijian', out['results'], pillars)
            self.assertIn('jiecai', out['results'], pillars)
            self.assertEqual(_state(out, 'bijian'), 'not_judgeable',
                             pillars)
            self.assertEqual(_state(out, 'jiecai'), 'not_judgeable',
                             pillars)
            self.assertIn('no_bijian_basis',
                          _evidence_ids(out, 'bijian'), pillars)
            self.assertIn('no_jiecai_basis',
                          _evidence_ids(out, 'jiecai'), pillars)

    def test_a1_a3_commander_not_visible_lands_on_bijian(self):
        # A1: a1（戊日司令戊=比肩）、a3（丙日司令丙=比肩）不透，
        # 证据落在常驻的 bijian 格上。
        for case_id in ('a1-wu-daymaster-neg', 'a3-bing-daymaster-neg'):
            case = next(c for c in REN_YIN_GOLDEN['cases']
                        if c['id'] == case_id)
            engine, _ = _trace_engine(
                case['pillars'], case['source_birth']['value'])
            self.assertEqual(engine['results']['bijian']['state'],
                             'not_judgeable', case_id)
            self.assertIn('ren_yin_commander_not_visible',
                          _evidence_ids(engine, 'bijian'), case_id)
            self.assertNotIn('established', engine['counts'], case_id)

    def test_jiecai_commander_not_visible_via_injection(self):
        # 乙日寅月司令甲（劫财）不透：证据落在 jiecai 格上。
        # 注入 D-1 commander_not_visible（引擎的显式输入契约）。
        ren_yin = {'status': 'determined',
                   'determination': {'true_false': 'commander_not_visible'},
                   'commander': {'stem': '甲', 'ten_god': '劫财',
                                 'visible_pillars': []}}
        out = evaluate_all(_chart('丙子', '丙寅', '乙卯', '戊辰'),
                           ren_yin=ren_yin)
        self.assertEqual(_state(out, 'jiecai'), 'not_judgeable')
        self.assertIn('ren_yin_commander_not_visible',
                      _evidence_ids(out, 'jiecai'))
        self.assertNotIn('ren_yin_commander_not_visible',
                         _evidence_ids(out, 'bijian'))


class ClassicalBrokenTests(unittest.TestCase):
    def _injected_shangguan(self, pillars):
        ren_yin = {'status': 'determined',
                   'determination': {'true_false': 'true',
                                     'pattern': '伤官格'},
                   'commander': {'stem': '丙', 'visible_pillars': ['month'],
                                 'ten_god': '伤官'}}
        return evaluate_all(_chart(*pillars), ren_yin=ren_yin)

    def test_established_shangguan_without_officer_stays_established(self):
        # 乙日寅月司令丙透、四柱无庚辛：成立，无破格。
        out = self._injected_shangguan(('甲辰', '丙寅', '乙卯', '甲午'))
        self.assertEqual(_state(out, 'shangguan'), 'established')
        self.assertNotIn('shangguan_sees_officer_broken',
                         _evidence_ids(out, 'shangguan'))
        self.assertEqual(
            _modern(out, 'shangguan')['broken_assessment']['flags'][0]
            ['verdict'], 'not_flagged')

    def test_established_shangguan_with_killing_only_stays_established(self):
        # 只有七杀（辛透时干）在场：官星从窄读为正官，七杀不破格。
        out = self._injected_shangguan(('甲辰', '丙寅', '乙卯', '辛丑'))
        self.assertEqual(_state(out, 'shangguan'), 'established')
        self.assertNotIn('shangguan_sees_officer_broken',
                         _evidence_ids(out, 'shangguan'))

    def test_established_shangguan_with_officer_is_broken(self):
        # 注入成立 + 正官在场（庚藏巳支）：与 Golden f2 同构。
        out = self._injected_shangguan(('甲辰', '丙寅', '乙巳', '甲申'))
        self.assertEqual(_state(out, 'shangguan'), 'broken')
        self.assertIn('shangguan_sees_officer_broken',
                      _evidence_ids(out, 'shangguan'))

    def test_candidate_shangguan_with_officer_stays_candidate(self):
        # 候选前提未成立：见官只作现代旗标，不作古典 broken。
        out = evaluate_all(_chart('庚申', '辛巳', '乙丑', '丙子'))
        self.assertEqual(_state(out, 'shangguan'), 'candidate')
        self.assertNotIn('shangguan_sees_officer_broken',
                         _evidence_ids(out, 'shangguan'))
        flag = _modern(out, 'shangguan')['broken_assessment']['flags'][0]
        self.assertEqual(flag['flag_id'], 'shangguan_sees_officer_modern')
        self.assertEqual(flag['verdict'], 'flagged_modern')


class ModernAssessmentTests(unittest.TestCase):
    def test_shenwang_gate_present_with_source_model(self):
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        gate = _modern(out, 'qisha')['shenwang_gate']
        self.assertEqual(gate['source_model'], 'strength_model_modern_v1')
        self.assertIn(gate['verdict'],
                      ('strong', 'weak', 'balanced', 'abstain'))

    def test_root_grades_are_structural(self):
        # 甲日午/酉皆无木藏干：无根。
        out = evaluate_all(_chart('戊午', '辛酉', '甲午', '丙午'))
        self.assertEqual(_modern(out, 'qisha')['root_grade']['grade'],
                         'none')
        self.assertEqual(
            _modern(out, 'qisha')['root_grade']['root_count'], 0)
        # 甲日寅月：寅藏甲为同干根。
        out = evaluate_all(_chart('己丑', '丙寅', '甲戌', '己巳'))
        self.assertEqual(_modern(out, 'qisha')['root_grade']['grade'],
                         'same_stem')
        self.assertTrue(
            _modern(out, 'qisha')['root_grade']['same_stem_root'])

    def test_extreme_weak_band_hit_and_miss(self):
        # 丁日癸/庚在场、无根、无显干生扶、克泄耗 3 干：极弱。
        out = evaluate_all(_chart('癸酉', '庚子', '丁酉', '庚子'))
        self.assertEqual(
            _modern(out, 'special')['extreme_weak_band']['band'],
            'extreme_weak_modern')
        self.assertIn('cong_root_grade_modern',
                      _evidence_ids(out, 'special'))
        self.assertIn('cong_extreme_weak_band_modern',
                      _evidence_ids(out, 'special'))
        # 甲日寅月有根：非极弱。
        out = evaluate_all(_chart('己丑', '丙寅', '甲戌', '己巳'))
        self.assertEqual(
            _modern(out, 'special')['extreme_weak_band']['band'],
            'not_extreme_weak')

    def test_shangjin_scale_grades(self):
        # 伤官在场、官杀全无：伤尽（现代）。
        out = evaluate_all(_chart('丙子', '丙午', '甲寅', '丙子'))
        scale = _modern(out, 'shangguan')['shangjin_scale']
        self.assertEqual(scale['grade'], 'exhausted_modern')
        self.assertEqual(scale['officer_count'], 0)
        # 伤官在场、正官透干：不尽。
        out = evaluate_all(_chart('庚申', '辛巳', '乙丑', '丙子'))
        scale = _modern(out, 'shangguan')['shangjin_scale']
        self.assertEqual(scale['grade'], 'not_exhausted_modern')
        self.assertTrue(scale['officer_exposed'])
        # 伤官不在场：不分级（甲日四柱无丁，显干与藏干皆无）。
        out = evaluate_all(_chart('甲子', '壬申', '甲寅', '庚辰'))
        self.assertEqual(_modern(out, 'shangguan')['shangjin_scale']
                         ['grade'], 'ungraded')

    def test_shangguan_modern_establishment_via_exhaustion(self):
        # P1: 月藏伤官 + 现代伤尽 → established_modern（无需身旺门）。
        out = evaluate_all(_chart('丙子', '丙午', '甲寅', '丙子'))
        est = _modern(out, 'shangguan')['establishment_assessment']
        self.assertEqual(est['verdict'], 'established_modern')
        self.assertIn('shangjin_exhausted', est['conditions'])
        self.assertIn('shangguan_modern_established',
                      _evidence_ids(out, 'shangguan'))

    def test_qisha_modern_establishment_missing_control(self):
        # P1: 月藏七杀、无制伏在场 → not_established_modern。
        # 丙日亥月藏壬七杀；四柱无戊己（显干与藏干皆无），制伏缺席；
        # 丁火显干生扶在场，身旺门不触从格弃判、可算（弱）。
        out = evaluate_all(_chart('丁卯', '癸亥', '丙子', '丁酉'))
        est = _modern(out, 'qisha')['establishment_assessment']
        self.assertEqual(est['verdict'], 'not_established_modern')
        self.assertIn('control_absent', est['missing'])

    def test_over_control_modern_flag(self):
        # P5: 制伏 2 处、七杀 1 处 → 现代制伏太过旗标。
        out = evaluate_all(_chart('戊子', '壬申', '丙午', '己丑'))
        flag = _modern(out, 'qisha')['broken_assessment']['flags'][0]
        self.assertEqual(flag['flag_id'], 'control_moderation_modern')
        self.assertEqual(flag['verdict'], 'flagged_modern')
        self.assertIn('control_moderation_modern',
                      _evidence_ids(out, 'qisha'))

    def test_wealth_breaks_seal_flag_is_consistent_with_shenwang(self):
        # P5: 现代财旺破印旗标当且仅当财 >= 3 且身旺门 strong；
        # 身旺门弃判时旗标亦弃判。断言旗标逻辑与所报身旺门一致，
        # 而非硬编码身旺结论（身旺模型另有专属套件）。
        out = evaluate_all(_chart('戊午', '癸亥', '甲子', '乙丑'))
        modern = _modern(out, 'pianyin')
        flag = modern['broken_assessment']['flags'][0]
        self.assertEqual(flag['flag_id'], 'wealth_breaks_seal_modern')
        shenwang = modern['shenwang_gate']['verdict']
        if shenwang == 'abstain':
            self.assertEqual(flag['verdict'], 'abstain')
        elif shenwang == 'strong':
            self.assertEqual(flag['verdict'], 'flagged_modern')
        else:
            self.assertEqual(flag['verdict'], 'not_flagged')

    def test_cong_modern_establishment(self):
        # P4: 从杀屏命中 + 极弱档 → congsha established_modern。
        out = evaluate_all(_chart('癸酉', '庚子', '丁酉', '庚子'))
        cong = _modern(out, 'special')['cong_assembly']
        self.assertEqual(cong['congsha']['verdict'], 'established_modern')
        self.assertIn('congsha_modern_established',
                      _evidence_ids(out, 'special'))

    def test_triple_harmony_assembly_screen(self):
        # P4: 寅午戌三合 + 化神火透干（丙）→ 现代会局屏 hit。
        out = evaluate_all(_chart('甲寅', '丙午', '乙巳', '戊戌'))
        cong = _modern(out, 'special')['cong_assembly']
        self.assertEqual(len(cong['assemblies']), 1)
        self.assertEqual(cong['assemblies'][0]['assembly_modern'], 'hit')
        self.assertIn('丙', cong['assemblies'][0]['transforming_stems'])
        self.assertIn('cong_assembly_screen_modern',
                      _evidence_ids(out, 'special'))
        # 三合支齐备、化神不透 → miss（月干庚非火，显干无丙丁）。
        out = evaluate_all(_chart('甲寅', '庚午', '乙巳', '戊戌'))
        cong = _modern(out, 'special')['cong_assembly']
        self.assertEqual(len(cong['assemblies']), 1)
        self.assertEqual(cong['assemblies'][0]['assembly_modern'], 'miss')
        self.assertEqual(cong['assemblies'][0]['transforming_stems'], [])


class P2RetentionTests(unittest.TestCase):
    def test_zhifu_trigger_recorded_in_conflict(self):
        # 时干庚七杀 + 丙食神透年干：两 Variant 并列，制伏触发条件在场。
        out = evaluate_all(_chart('丙寅', '辛酉', '甲午', '庚申'))
        self.assertEqual(_state(out, 'zhengguan'), 'conflict')
        self.assertIn('guansha_zhifu_trigger',
                      _evidence_ids(out, 'zhengguan'))
        retention = _modern(out, 'zhengguan')['guansha_retention']
        self.assertEqual(retention['verdict'], 'observation_only')
        self.assertTrue(retention['zhifu_trigger']['geng_shen_present'])
        self.assertTrue(retention['control_present'])

    def test_zhifu_trigger_absent_without_geng_shen(self):
        # 正官在场、七杀不在场、四柱无庚无申：庚申触发条件不在场
        # （辛金在场，故 gold_present 为真；触发条件以庚申为准）。
        out = evaluate_all(_chart('壬子', '辛酉', '甲午', '丁卯'))
        self.assertEqual(_state(out, 'zhengguan'), 'candidate')
        self.assertNotIn('guansha_zhifu_trigger',
                         _evidence_ids(out, 'zhengguan'))
        retention = _modern(out, 'zhengguan')['guansha_retention']
        self.assertTrue(retention['zhifu_trigger']['gold_present'])
        self.assertFalse(retention['zhifu_trigger']['geng_shen_present'])


class P3EarthMappingTests(unittest.TestCase):
    def test_zaqi_earth_conversion_mapping(self):
        # 本气土→十神条件换算：辰/戌→戊，丑/未→己。
        cases = {
            ('甲子', '戊辰', '乙丑', '丙子'): ('戊', '正财'),
            ('甲子', '戊戌', '乙丑', '丙子'): ('戊', '正财'),
            ('壬辰', '癸丑', '己未', '庚午'): ('己', '比肩'),
            ('甲子', '丁未', '乙丑', '丙子'): ('己', '偏财'),
        }
        for pillars, (stem, god) in cases.items():
            out = evaluate_all(_chart(*pillars))
            self.assertEqual(_state(out, 'zaqi'), 'conflict', pillars)
            self.assertIn('zaqi_earth_conversion_mapping',
                          _evidence_ids(out, 'zaqi'), pillars)
            detail = ' '.join(e['detail']
                              for e in out['results']['zaqi']['evidence'])
            self.assertIn('本气之土为 %s' % stem, detail, pillars)
            self.assertIn('为 %s' % god, detail, pillars)


if __name__ == '__main__':
    unittest.main()
