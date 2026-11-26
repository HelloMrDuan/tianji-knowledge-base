"""TJ-0424 喜用神实际计算引擎专项（P0-3）。

真实算例（均取自仓内已审 Golden / 已审模块输出，不另造命盘）：

- 算例 A：1958-08-15T19:30:00+08:00，男，四柱 戊戌/庚申/甲子/甲戌，
  日主甲（组合引擎算例 A；强弱/调候/病药夹具与
  tests/test_tj0424_combination_engine.py 的 _FIXTURES 同源）。
  现代旺衰 weak -21（手算分项 -15/0/10/4/-20，机上 cross-check 复核）。
- 算例 B：1959-06-15T10:30:00+08:00，女，四柱 己亥/庚午/戊辰/丁巳，
  日主戊（组合引擎算例 B）。现代旺衰 balanced 53
  （手算分项 20/15/20/10/-12，机上 cross-check 复核；土日主得地未校准）。
- 强例：1963-03-22T22:00:00+08:00，四柱 癸卯/乙卯/甲子/乙亥，日主甲
  （Golden tj0112-regression-mao-pure-support；古典 strong，
  现代 strong 105，分项 30/35/30/10/0）。
- 弱例（古典）：1978-09-20T10:00:00+08:00，四柱 戊午/辛酉/乙酉/辛巳，
  日主乙（Golden tj0112-regression-you-isolated-control；古典 weak，
  现代 weak -35，分项 -15/0/0/0/-20）。
- 已成立格例：Golden t1-wu-zhengcai，四柱 甲辰/丙寅/乙巳/戊寅，
  日主乙，任氏寅月真格正财格成立。

本文件只依赖标准库与 ``tianji_kb.bazi_xiyong_engine``（只 import
``foundations``），故公开检出可直接运行。输入夹具为上述真实输出的
逐字转录（只含本引擎消费的字段）；``LiveCrossCheckTests`` 在可导入
真实引擎时（可信机装配环境）逐项复算夹具字段，漂移即失败，公开检出
无历法 provider 时整类跳过，不伪造通过。
"""
import copy
import unittest

from tianji_kb.bazi_xiyong_engine import (
    ANNUAL_IMPLEMENTED,
    ANNUAL_PENDING,
    FUYI_DIRECTION_TABLE,
    FUYI_MODERN_RULES_V1,
    VALIDATED_CANDIDATE_RULE_IDS,
    XIYONG_ENGINE_VARIANT,
    evaluate_annual_xiyong,
    evaluate_bingyao_xiyong,
    evaluate_fuyi,
    evaluate_pattern_xiyong,
    evaluate_tiaohou_xiyong,
    evaluate_xiyong,
    ten_god_for,
)

# --- 真实算例夹具 -------------------------------------------------------
CASE_A_PILLARS = ['戊戌', '庚申', '甲子', '甲戌']
CASE_B_PILLARS = ['己亥', '庚午', '戊辰', '丁巳']
STRONG_PILLARS = ['癸卯', '乙卯', '甲子', '乙亥']
WEAK_PILLARS = ['戊午', '辛酉', '乙酉', '辛巳']
T1_PILLARS = ['甲辰', '丙寅', '乙巳', '戊寅']


def _strength_fixture(day_master, month_branch, pillars, classification,
                      matched_predicate, modern):
    return {
        'variant': 'bazi-strength-engine-v1',
        'day_master': day_master, 'month_branch': month_branch,
        'pillars': list(pillars),
        'classical': {'classification': classification,
                      'matched_predicate': matched_predicate,
                      'research_only': True, 'public_enabled': False,
                      'ai_enabled': False},
        'modern': modern,
        'agreement': {},
        'research_only': True, 'public_enabled': False, 'ai_enabled': False}


def _modern_fixture(verdict, score, components, limitations=(),
                    abstain_reason=None, abstain_detail=None):
    return {
        'model_id': 'strength_model_modern_v1',
        'model_kind': 'modern_engineering',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'verdict': verdict, 'score': score,
        'thresholds': {'strong_at_least': 60, 'weak_at_most': 15,
                       'balanced_between': [16, 59]},
        'components': components,
        'abstain_reason': abstain_reason,
        'abstain_detail': abstain_detail,
        'limitations': list(limitations)}


def _components(de_ling, de_di, de_shi, hidden, kexiehao):
    return {
        'de_ling': {'score': de_ling}, 'de_di': {'score': de_di},
        'de_shi': {'score': de_shi},
        'shengfu_hidden': {'score': hidden},
        'kexiehao': {'score': kexiehao}}


STRENGTH_A = _strength_fixture(
    '甲', '申', CASE_A_PILLARS, 'indeterminate', None,
    _modern_fixture('weak', -21, _components(-15, 0, 10, 4, -20)))
STRENGTH_B = _strength_fixture(
    '戊', '午', CASE_B_PILLARS, 'indeterminate', None,
    _modern_fixture('balanced', 53, _components(20, 15, 20, 10, -12),
                    limitations=('土日主无已审重根集：得地分只计余根，未校准。',)))
STRENGTH_STRONG = _strength_fixture(
    '甲', '卯', STRONG_PILLARS, 'strong',
    {'predicate_id': 'pure_support', 'verification': 'factor_level_only'},
    _modern_fixture('strong', 105, _components(30, 35, 30, 10, 0)))
STRENGTH_WEAK_CLASSICAL = _strength_fixture(
    '乙', '酉', WEAK_PILLARS, 'weak',
    {'predicate_id': 'isolated_control', 'verification': 'factor_level_only'},
    _modern_fixture('weak', -35, _components(-15, 0, 0, 0, -20)))
STRENGTH_ABSTAIN_EARTH = _strength_fixture(
    '戊', '巳', ['甲辰', '丙巳', '戊午', '乙卯'], 'indeterminate', None,
    _modern_fixture('abstain', None, None,
                    abstain_reason='earth_form_unbuildable_tj0112',
                    abstain_detail='日主 戊 × 月支 巳 属 TJ-011.2 UNBUILDABLE。'))


def _tiaohou_fixture(day_master, month_branch, month_label, quote, order_basis,
                     sequence, branches=(), unencoded=()):
    return {
        'variant': 'tiaohou-qiongtong-v1', 'status': 'matched',
        'system': 'tiaohou', 'source_id': 'bazi.source.qiongtong',
        'evidence_level': 'C', 'day_master': day_master,
        'month_branch': month_branch, 'month_label': month_label,
        'entry': {'quote': quote, 'quote_locator': {},
                  'section': {}, 'order_basis': order_basis},
        'sequence': sequence, 'branches': list(branches),
        'unencoded_branches': list(unencoded), 'related': [], 'notes': [],
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'registered_phase1_phase2',
        'limitations': []}


def _seq(stem, order, presence, visible=(), hidden=()):
    return {'stem': stem, 'order': order, 'presence': presence,
            'visible_positions': list(visible),
            'hidden_positions': list(hidden)}


TIAOHOU_A = _tiaohou_fixture(
    '甲', '申', '七月', '七月甲木,丁火为尊,庚金次之,庚金不可少。',
    '原文「丁火为尊,庚金次之」明示先次,并明示「庚金不可少」。',
    [_seq('丁', 1, 'hidden', hidden=('year:2', 'hour:2')),
     _seq('庚', 2, 'visible', visible=('month',), hidden=('month:0',))])
TIAOHOU_B = _tiaohou_fixture(
    '戊', '午', '五月', '五月戊土,仲夏火炎,先看壬水,次取甲木,丙火酌用,用癸力微。',
    '原文「先看壬水，次取甲木」明示先次；「丙火酌用」「用癸力微」为酌量与力微陈述，未列先次，不入序列。',
    [_seq('壬', 1, 'hidden', hidden=('year:0',)),
     _seq('甲', 2, 'hidden', hidden=('year:1',))])
# 甲午乏癸分支：组装陈述（非 live lookup 输出），用于分支取代路径单测；
# live 核对见 LiveCrossCheckTests.test_tiaohou_branch_live。
TIAOHOU_JIA_WU_BRANCH = _tiaohou_fixture(
    '甲', '午', '五月', '五六月甲木,木性虚焦,一理共推。五月先癸後丁庚金次之。',
    '原文「五月先癸後丁庚金次之」明示三级先次(节区为五六月合论段)。',
    [_seq('癸', 1, 'absent'), _seq('丁', 2, 'visible', visible=('hour',)),
     _seq('庚', 3, 'hidden', hidden=('month:0',))],
    branches=[{'id': 'wuyue_fa_gui_yong_ding', 'applied': True,
               'condition': {'absent_stem': '癸'},
               'quote': '或五月乏癸,用丁亦可,要运行北地为隹。',
               'locator': {},
               'sequence': [_seq('丁', 1, 'visible', visible=('hour',)),
                            _seq('庚', 2, 'hidden', hidden=('month:0',))],
               'note': '原文「或五月乏癸,用丁亦可」:癸在四柱透干与藏干皆无时，丁可代为首取，庚仍次之。'}])
TIAOHOU_ABSENT = {
    'variant': 'tiaohou-qiongtong-v1', 'status': 'not_applicable',
    'reason': 'entry_absent_in_source', 'day_master': '乙',
    'month_branch': '丑', 'system': 'tiaohou',
    'source_id': 'bazi.source.qiongtong', 'evidence_level': 'C',
    'research_only': True, 'public_enabled': False, 'ai_enabled': False,
    'evidence_binding': 'registered_phase1_phase2', 'limitations': []}
TIAOHOU_EMPTY = _tiaohou_fixture(
    '丙', '亥', '十月', '十月丙火,太阳失令,得见甲戊庚出干,可云科甲,主为人性好清高,斯文领袖。',
    '本月条未给出无条件取用顺序：首句甲戊庚为「得见出干」之并列陈述，条末总述明言随宜酌用，本 Variant 不拟制序列，序列为空。',
    [], unencoded=[{'quote': '总之十月丙火,木旺宜庚,水旺宜戊,火旺用壬,随宜酌用可也。',
                    'reason': '三干之用各以木/水/火「旺」为条件，属相对旺衰判断，且原文自述「随宜酌用」，未给无条件先次，只登记不编码。'}])


def _bingyao_pair(pair_id, rule_id, subject_gods, disease_gods, medicine_gods,
                  quote, status, subject, disease, medicine, medicine_status,
                  not_triggered_reason=None):
    return {
        'pair_id': pair_id,
        'rule': {'pair_id': pair_id, 'id': rule_id,
                 'subject_god_class': {
                     'wealth_peer_officer': '财',
                     'foodwound_seal_wealth': '食伤'}[pair_id],
                 'disease_god_class': {
                     'wealth_peer_officer': '比劫',
                     'foodwound_seal_wealth': '印'}[pair_id],
                 'medicine_god_class': {
                     'wealth_peer_officer': '官杀',
                     'foodwound_seal_wealth': '财'}[pair_id],
                 'subject_gods': list(subject_gods),
                 'disease_gods': list(disease_gods),
                 'medicine_gods': list(medicine_gods), 'quote': quote},
        'subject': subject, 'status': status,
        'disease_candidate': disease, 'medicine_candidate': medicine,
        'medicine_status': medicine_status,
        'medicine_effect_status': 'unadjudicated', 'determination': None,
        **({'not_triggered_reason': not_triggered_reason}
           if not_triggered_reason else {})}


def _bingyao_fixture(day_master, pairs, status):
    return {
        'variant': 'bingyao-shenfeng-v1', 'system': 'bingyao',
        'source_id': 'bazi.source.shenfeng', 'evidence_level': 'C',
        'day_master': day_master, 'status': status,
        'determination': None, 'medicine_effect_status': 'unadjudicated',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'registered_phase1_phase2', 'pairs': pairs}


BINGYAO_A = _bingyao_fixture('甲', [
    _bingyao_pair(
        'wealth_peer_officer', 'shenfeng.wealth_peer_officer',
        ('正财', '偏财'), ('比肩', '劫财'), ('正官', '七杀'),
        '如用财见比肩为病,喜见官杀为药也', 'triggered',
        {'god_class': '财', 'gods': [{'pillar': 'year', 'stem': '戊',
                                      'ten_god': '偏财'}]},
        {'god_class': '比劫', 'gods': [{'pillar': 'hour', 'stem': '甲',
                                        'ten_god': '比肩'}],
         'relation_to_subject': '比劫为所论之财的所害之神（按原句）'},
        {'god_class': '官杀', 'gods': [{'pillar': 'month', 'stem': '庚',
                                        'ten_god': '七杀'}],
         'structural_relation': 'medicine_element_controls_disease_element',
         'medicine_element': '金', 'disease_element': '木'},
        'candidate_present'),
    _bingyao_pair(
        'foodwound_seal_wealth', 'shenfeng.foodwound_seal_wealth',
        ('食神', '伤官'), ('正印', '偏印'), ('正财', '偏财'),
        '如用食神伤官,以印为病,喜财为药也', 'not_triggered',
        {'god_class': '食伤', 'gods': []}, None, None, None,
        not_triggered_reason='subject_foodwound_not_visible'),
], 'triggered')
BINGYAO_B = _bingyao_fixture('戊', [
    _bingyao_pair(
        'wealth_peer_officer', 'shenfeng.wealth_peer_officer',
        ('正财', '偏财'), ('比肩', '劫财'), ('正官', '七杀'),
        '如用财见比肩为病,喜见官杀为药也', 'not_triggered',
        {'god_class': '财', 'gods': []}, None, None, None,
        not_triggered_reason='subject_wealth_not_visible'),
    _bingyao_pair(
        'foodwound_seal_wealth', 'shenfeng.foodwound_seal_wealth',
        ('食神', '伤官'), ('正印', '偏印'), ('正财', '偏财'),
        '如用食神伤官,以印为病,喜财为药也', 'triggered',
        {'god_class': '食伤', 'gods': [{'pillar': 'month', 'stem': '庚',
                                        'ten_god': '食神'}]},
        {'god_class': '印', 'gods': [{'pillar': 'hour', 'stem': '丁',
                                      'ten_god': '正印'}],
         'relation_to_subject': '印为所论之食伤的所害之神（按原句）'},
        None, 'absent'),
], 'not_triggered')


PATTERN_NAMES = {
    'zhengguan': '正官', 'qisha': '七杀', 'zhengyin': '正印',
    'pianyin': '偏印', 'zhengcai': '正财', 'piancai': '偏财',
    'shishen': '食神', 'shangguan': '伤官', 'jianlu': '建禄',
    'yangren': '阳刃', 'zaqi': '杂气', 'special': '特殊格局'}


def _pattern_result(key, state, rule_ids=(), evidence_ids=()):
    return {
        'pattern': PATTERN_NAMES[key], 'pattern_key': key, 'state': state,
        'evidence': [{'id': eid, 'detail': ''} for eid in evidence_ids],
        'limitations': [], 'rule_ids': list(rule_ids),
        'research_only': True, 'public': False, 'ai': False,
        'variant': 'bazi-pattern-engine-v1'}


def _pattern_fixture(day_stem, month_branch, states):
    # 默认 rule_ids 按格局引擎各评估器的非命中分支逐字取值：
    # 建禄/阳刃恒带 pattern_route，杂气恒带 pattern_zaqi，其余为空。
    default_rule_ids = {
        'jianlu': ('bazi.phase2.pattern_route',),
        'yangren': ('bazi.phase2.pattern_route',),
        'zaqi': ('bazi.phase2.pattern_zaqi',),
    }
    results = {}
    for key in PATTERN_NAMES:
        state, rule_ids, evidence_ids = states.get(
            key, ('not_judgeable', default_rule_ids.get(key, ()),
                  ('no_basis',)))
        results[key] = _pattern_result(key, state, rule_ids, evidence_ids)
    return {
        'variant': 'bazi-pattern-engine-v1', 'day_stem': day_stem,
        'month_branch': month_branch, 'results': results,
        'research_only': True, 'public': False, 'ai': False}


PATTERN_A = _pattern_fixture('甲', '申', {
    'qisha': ('candidate', (), ('month_hidden_god',
                                'month_hidden_observation')),
    'pianyin': ('candidate', ('bazi.phase2.resource_pattern_candidates',),
                ('month_hidden_god', 'bazi.phase2.resource_pattern_candidates')),
    'piancai': ('candidate', (), ('month_hidden_god',
                                  'month_hidden_observation')),
})
PATTERN_B = _pattern_fixture('戊', '午', {
    'zhengyin': ('candidate', ('bazi.phase2.resource_pattern_candidates',),
                 ('month_hidden_god', 'bazi.phase2.resource_pattern_candidates')),
    'yangren': ('not_judgeable', ('bazi.phase2.pattern_route',),
                ('luren_route_exclusion', 'luren_route_rule')),
})
PATTERN_T1 = _pattern_fixture('乙', '寅', {
    'zhengcai': ('established', ('bazi.phase2.ren_yin_true_pattern',),
                 ('ren_yin_true_pattern', 'ren_yin_rule')),
    'shangguan': ('candidate', (), ('month_hidden_god',
                                    'month_hidden_observation')),
})
PATTERN_NONE = _pattern_fixture('甲', '申', {})


class ShapeTests(unittest.TestCase):
    def test_variant_and_governance_flags(self):
        self.assertEqual(XIYONG_ENGINE_VARIANT, 'bazi-xiyong-engine-v1')
        out = evaluate_xiyong(day_master='甲', month_branch='申',
                              pillars=CASE_A_PILLARS, strength=STRENGTH_A,
                              tiaohou=TIAOHOU_A, bingyao=BINGYAO_A,
                              pattern=PATTERN_A, flow_year=1988)
        self.assertTrue(out['research_only'])
        self.assertFalse(out['public_enabled'])
        self.assertFalse(out['ai_enabled'])
        self.assertIsNone(out['unified_verdict'])
        self.assertEqual(out['unified_verdict_status'],
                         'abstain_by_adjudication_TJ-013.2-A')
        self.assertEqual(set(out['systems']),
                         {'fuyi', 'tiaohou', 'bingyao', 'pattern_yongshen'})
        self.assertEqual(out['pillars'], CASE_A_PILLARS)

    def test_ten_god_spot_checks(self):
        self.assertEqual(ten_god_for('甲', '丁'), '伤官')
        self.assertEqual(ten_god_for('甲', '庚'), '七杀')
        self.assertEqual(ten_god_for('戊', '壬'), '偏财')
        self.assertEqual(ten_god_for('戊', '甲'), '七杀')
        self.assertEqual(ten_god_for('乙', '戊'), '正财')
        with self.assertRaises(ValueError):
            ten_god_for('甲', 'X')

    def test_input_consistency_fail_closed(self):
        with self.assertRaises(ValueError):
            evaluate_xiyong(day_master='乙', month_branch='申',
                            pillars=CASE_A_PILLARS, strength=STRENGTH_A)
        with self.assertRaises(ValueError):
            evaluate_xiyong(day_master='甲', month_branch='酉',
                            pillars=CASE_A_PILLARS, strength=STRENGTH_A)
        with self.assertRaises(ValueError):
            evaluate_xiyong(day_master='甲', month_branch='申',
                            pillars=['戊戌', '庚申', '乙子', '甲戌'],
                            strength=STRENGTH_A)
        bad = copy.deepcopy(STRENGTH_A)
        bad['variant'] = 'other'
        with self.assertRaises(ValueError):
            evaluate_fuyi(bad)
        bad = copy.deepcopy(TIAOHOU_A)
        bad['public_enabled'] = True
        with self.assertRaises(ValueError):
            evaluate_tiaohou_xiyong(bad)


class FuyiTests(unittest.TestCase):
    def test_strong_modern_and_classical_agree(self):
        out = evaluate_fuyi(STRENGTH_STRONG, pillars=STRONG_PILLARS)
        self.assertEqual(out['status'], 'presented')
        self.assertEqual(out['classical']['classification'], 'strong')
        self.assertEqual(out['classical']['matched_predicate'], 'pure_support')
        self.assertEqual(out['classical']['direction'], None)
        self.assertEqual(out['classical']['conditional_directions'],
                         ['财星', '食伤'])
        self.assertTrue(all(
            r['row_outcome'] == 'cannot_fire_quantifier_unthresholded'
            for r in out['classical']['rows']))
        self.assertEqual(out['classical']['rows'][0]['premise_status'],
                         'satisfied')
        self.assertEqual(out['classical']['rows'][5]['premise_status'],
                         'not_satisfied')
        modern = out['modern']
        self.assertEqual(modern['model_kind'], 'modern_engineering')
        self.assertEqual(modern['adjudication_status'],
                         'proposed_pending_adjudication')
        self.assertEqual(modern['rule_id'], 'fuyi-modern-strong')
        self.assertEqual(modern['direction'], 'drain_control')
        self.assertEqual(modern['direction_cn'], '泄耗克')
        self.assertEqual(sorted(modern['direction_elements']),
                         ['土', '火', '金'])
        self.assertEqual(modern['ten_god_classes'],
                         ['食神', '伤官', '正财', '偏财', '正官', '七杀'])
        # 显干癸/乙/乙皆不在泄耗克元素内：只给方向，不给候选干。
        self.assertEqual(modern['candidate_stems'], [])
        self.assertEqual(modern['confidence'], 'model_candidate')
        self.assertEqual(modern['uncertainty'], [])
        self.assertEqual(out['cross_layer']['relationship'], 'agree')
        self.assertEqual(out['uncertainty'], [])

    def test_weak_case_a_modern_direction_and_visible_candidate(self):
        out = evaluate_fuyi(STRENGTH_A, pillars=CASE_A_PILLARS)
        self.assertEqual(out['status'], 'presented')
        self.assertEqual(out['classical']['conditional_directions'], [])
        modern = out['modern']
        self.assertEqual(modern['rule_id'], 'fuyi-modern-weak')
        self.assertEqual(modern['direction'], 'support')
        self.assertEqual(modern['direction_cn'], '生扶')
        self.assertEqual(sorted(modern['direction_elements']), ['木', '水'])
        self.assertEqual(modern['candidate_stems'],
                         [{'stem': '甲', 'pillar': 'hour',
                           'ten_god': '比肩', 'element': '木'}])
        self.assertEqual(modern['input_score'], -21)
        self.assertEqual(out['cross_layer']['relationship'],
                         'classical_indeterminate')
        self.assertEqual(out['uncertainty'],
                         ['classical_strength_indeterminate'])

    def test_weak_classical_and_modern_agree(self):
        out = evaluate_fuyi(STRENGTH_WEAK_CLASSICAL, pillars=WEAK_PILLARS)
        self.assertEqual(out['classical']['conditional_directions'],
                         ['印绶', '比劫'])
        self.assertEqual(out['modern']['direction'], 'support')
        self.assertEqual(out['modern']['candidate_stems'], [])
        self.assertEqual(out['cross_layer']['relationship'], 'agree')
        self.assertIn('扶抑现代层候选方向：生扶', out['conclusion'])

    def test_balanced_propagates_uncertainty_no_direction(self):
        out = evaluate_fuyi(STRENGTH_B, pillars=CASE_B_PILLARS)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertIsNone(out['conclusion'])
        self.assertEqual(out['modern']['rule_id'], 'fuyi-modern-balanced')
        self.assertIsNone(out['modern']['direction'])
        self.assertEqual(out['modern']['status'], 'indeterminate_direction')
        self.assertEqual(out['modern']['confidence'], 'provisional')
        self.assertEqual(out['uncertainty'], [
            'balanced_middle_band_only',
            'classical_strength_indeterminate',
            'earth_de_di_uncalibrated'])
        self.assertEqual(out['cross_layer']['relationship'],
                         'classical_indeterminate')

    def test_modern_abstain_earth_unbuildable(self):
        out = evaluate_fuyi(STRENGTH_ABSTAIN_EARTH)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['modern']['status'], 'abstain')
        self.assertEqual(out['modern']['abstain_reason'],
                         'earth_form_unbuildable_tj0112')
        self.assertEqual(out['cross_layer']['relationship'], 'modern_abstains')

    def test_not_provided_and_modern_not_provided(self):
        out = evaluate_fuyi(None)
        self.assertEqual(out['status'], 'not_provided')
        self.assertIsNone(out['classical'])
        no_modern = copy.deepcopy(STRENGTH_A)
        no_modern['modern'] = None
        out = evaluate_fuyi(no_modern, pillars=CASE_A_PILLARS)
        self.assertEqual(out['modern']['status'], 'not_provided')
        self.assertEqual(out['cross_layer']['relationship'],
                         'modern_not_provided')

    def test_direction_table_shape_and_rules_pinned(self):
        self.assertEqual(len(FUYI_DIRECTION_TABLE['rows']), 10)
        self.assertEqual(
            [r['direction_god'] for r in FUYI_DIRECTION_TABLE['rows']],
            ['财星', '财星', '食伤', '食伤', '财星',
             '印绶', '印绶', '比劫', '食伤', '印比'])
        self.assertEqual(
            [r['rule_id'] for r in FUYI_MODERN_RULES_V1['rules']],
            ['fuyi-modern-strong', 'fuyi-modern-weak',
             'fuyi-modern-balanced'])
        self.assertEqual(FUYI_MODERN_RULES_V1['adjudication_status'],
                         'proposed_pending_adjudication')
        self.assertEqual(VALIDATED_CANDIDATE_RULE_IDS, frozenset((
            'bazi.phase2.official_pattern_candidates',
            'bazi.phase2.resource_pattern_candidates',
            'bazi.phase2.ren_yin_true_pattern')))


class TiaohouTests(unittest.TestCase):
    def test_case_a_operative_hidden_first(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_A)
        self.assertEqual(out['status'], 'presented')
        self.assertEqual(out['active_sequence'], 'main')
        self.assertEqual(
            [(c['stem'], c['presence'], c['ten_god']) for c in out['candidates']],
            [('丁', 'hidden', '伤官'), ('庚', 'visible', '七杀')])
        self.assertEqual(out['operative_candidate']['stem'], '丁')
        self.assertEqual(out['operative_status'], 'hidden')
        self.assertEqual(out['gaps'], [])
        self.assertIn('首取 丁', out['conclusion'])

    def test_case_b_operative_hidden(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_B)
        self.assertEqual(out['operative_candidate']['stem'], '壬')
        self.assertEqual(out['operative_candidate']['ten_god'], '偏财')
        self.assertEqual(out['candidates'][1]['ten_god'], '七杀')

    def test_branch_supersedes_main_sequence(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_WU_BRANCH)
        self.assertEqual(out['active_sequence'],
                         'branch:wuyue_fa_gui_yong_ding')
        self.assertEqual([c['stem'] for c in out['candidates']], ['丁', '庚'])
        self.assertEqual(out['operative_candidate']['stem'], '丁')
        self.assertEqual(out['operative_candidate']['presence'], 'visible')

    def test_entry_absent_and_empty_sequence(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_ABSENT)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['gaps'][0]['gap_id'], 'entry_absent_in_source')
        out = evaluate_tiaohou_xiyong(TIAOHOU_EMPTY)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(
            [g['gap_id'] for g in out['gaps']],
            ['empty_sequence', 'unencoded_branch'])

    def test_all_candidates_absent_is_gap(self):
        tiaohou = copy.deepcopy(TIAOHOU_A)
        for item in tiaohou['sequence']:
            item['presence'] = 'absent'
            item['visible_positions'] = []
            item['hidden_positions'] = []
        out = evaluate_tiaohou_xiyong(tiaohou)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['operative_status'], 'absent_all')
        self.assertEqual(out['gaps'][0]['gap_id'],
                         'candidates_absent_in_chart')

    def test_not_provided(self):
        out = evaluate_tiaohou_xiyong(None)
        self.assertEqual(out['status'], 'not_provided')


class BingyaoTests(unittest.TestCase):
    def test_case_a_wealth_pair_medicine_present(self):
        out = evaluate_bingyao_xiyong(BINGYAO_A)
        self.assertEqual(out['status'], 'presented')
        wealth = out['pairs'][0]
        self.assertEqual(wealth['status'], 'triggered')
        self.assertEqual(wealth['medicine_status'], 'candidate_present')
        self.assertTrue(wealth['medicine_check'])
        self.assertEqual(wealth['yongshen_candidate'],
                         [{'stem': '庚', 'pillar': 'month',
                           'ten_god': '七杀', 'element': '金'}])
        self.assertEqual(wealth['medicine_effect_status'], 'unadjudicated')
        food = out['pairs'][1]
        self.assertEqual(food['status'], 'not_triggered')
        self.assertIsNone(food['yongshen_candidate'])
        self.assertIn('药神候选 庚', out['conclusion'])

    def test_case_b_foodwound_pair_medicine_absent(self):
        out = evaluate_bingyao_xiyong(BINGYAO_B)
        self.assertEqual(out['status'], 'presented')
        food = out['pairs'][1]
        self.assertEqual(food['status'], 'triggered')
        self.assertEqual(food['medicine_status'], 'absent')
        self.assertIsNone(food['yongshen_candidate'])
        gap = next(g for g in out['gaps']
                   if g['gap_id'] == 'medicine_absent_in_chart')
        self.assertEqual(gap['pair_id'], 'foodwound_seal_wealth')
        self.assertIn('财', gap['detail'])
        self.assertIn('病已触发、药不在盘', out['conclusion'])

    def test_no_triggered_pair(self):
        bingyao = copy.deepcopy(BINGYAO_B)
        bingyao['pairs'][1]['status'] = 'not_triggered'
        bingyao['pairs'][1]['disease_candidate'] = None
        bingyao['pairs'][1]['not_triggered_reason'] = 'seal_god_not_visible'
        out = evaluate_bingyao_xiyong(bingyao)
        self.assertEqual(out['status'], 'no_triggered_pair')
        self.assertIsNone(out['conclusion'])
        # 未触发只记未触发：结论中不出现「无病」断语，缺口中明言不是「无病」。
        self.assertTrue(any('不是「无病」' in g['detail']
                            for g in out['gaps']))

    def test_not_provided_and_drift(self):
        self.assertEqual(evaluate_bingyao_xiyong(None)['status'],
                         'not_provided')
        bad = copy.deepcopy(BINGYAO_A)
        bad['determination'] = {'pattern': '正官格'}
        with self.assertRaises(ValueError):
            evaluate_bingyao_xiyong(bad)


class PatternTests(unittest.TestCase):
    def test_case_a_only_validated_resource_candidate_eligible(self):
        out = evaluate_pattern_xiyong(PATTERN_A, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        self.assertEqual(out['status'], 'presented')
        self.assertEqual([e['pattern_key'] for e in out['eligible']],
                         ['pianyin'])
        entry = out['eligible'][0]
        self.assertEqual(entry['state'], 'candidate')
        self.assertIsNone(entry['useful_god'])
        self.assertEqual(entry['useful_god_status'],
                         'no_reviewed_yongshen_rule')
        self.assertEqual(entry['visible_positions'], [])
        ineligible = {e['pattern_key']: e for e in out['ineligible']}
        self.assertIn('仅月藏结构观察', ineligible['qisha']['reason'])
        self.assertIn('仅月藏结构观察', ineligible['piancai']['reason'])
        self.assertEqual(out['counts'],
                         {'eligible': 1, 'ineligible': 11, 'total': 12})

    def test_case_b_resource_candidate_with_visible_basis(self):
        out = evaluate_pattern_xiyong(PATTERN_B, pillars=CASE_B_PILLARS,
                                      day_master='戊')
        self.assertEqual([e['pattern_key'] for e in out['eligible']],
                         ['zhengyin'])
        self.assertEqual(out['eligible'][0]['visible_positions'],
                         [{'stem': '丁', 'pillar': 'hour',
                           'ten_god': '正印', 'element': '火'}])

    def test_established_pattern_still_yields_no_yongshen(self):
        out = evaluate_pattern_xiyong(PATTERN_T1, pillars=T1_PILLARS,
                                      day_master='乙')
        self.assertEqual([e['pattern_key'] for e in out['eligible']],
                         ['zhengcai'])
        entry = out['eligible'][0]
        self.assertEqual(entry['state'], 'established')
        self.assertIsNone(entry['useful_god'])
        self.assertEqual(entry['visible_positions'],
                         [{'stem': '戊', 'pillar': 'hour',
                           'ten_god': '正财', 'element': '土'}])

    def test_no_eligible_pattern(self):
        out = evaluate_pattern_xiyong(PATTERN_NONE, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        self.assertEqual(out['status'], 'no_eligible_pattern')
        self.assertEqual(out['eligible'], [])
        self.assertEqual(out['gaps'][0]['gap_id'],
                         'no_pattern_yields_yongshen')

    def test_not_provided_and_broken_refused(self):
        self.assertEqual(evaluate_pattern_xiyong(None)['status'],
                         'not_provided')
        bad = copy.deepcopy(PATTERN_A)
        bad['results']['qisha']['state'] = 'broken'
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(bad)


class AnnualTests(unittest.TestCase):
    def _systems_a(self):
        return evaluate_xiyong(
            day_master='甲', month_branch='申', pillars=CASE_A_PILLARS,
            strength=STRENGTH_A, tiaohou=TIAOHOU_A, bingyao=BINGYAO_A,
            pattern=PATTERN_A, flow_year=1988)['systems']

    def test_case_a_flow_1988(self):
        annual = evaluate_annual_xiyong(self._systems_a(), 1988,
                                        day_master='甲')
        self.assertEqual(annual['status'], 'contract_only_pending_rules')
        self.assertEqual(annual['flow_year']['ganzhi'], '戊辰')
        self.assertEqual(annual['flow_year']['stem_ten_god'], '偏财')
        for item in ('flow_year_ganzhi_and_ten_god',
                     'flow_stem_presence_against_natal_tiaohou_sequence',
                     'flow_stem_ten_god_role_against_bingyao_pairs',
                     'rule_call_structure'):
            self.assertIn(item, annual['implemented'])
        self.assertEqual(annual['pending'], list(ANNUAL_PENDING))
        self.assertIsNone(annual['derivation'])
        self.assertIsNone(annual['unified_verdict'])
        refs = annual['flow_references']
        self.assertIs(refs['tiaohou']
                      ['flow_stem_in_natal_tiaohou_sequence'], False)
        roles = {p['pair_id']: p['flow_ten_god_role_in_pair']
                 for p in refs['bingyao']['pairs']}
        self.assertEqual(roles, {'wealth_peer_officer': 'subject',
                                 'foodwound_seal_wealth': 'medicine'})
        self.assertIs(refs['fuyi']
                      ['flow_stem_in_natal_fuyi_modern_candidates'], False)
        # A 盘有资格格（偏印）的格神壬不透干，结构依据干为空，故对照为 None。
        self.assertIsNone(refs['pattern_yongshen']['flow_stem_in_pattern_basis'])
        self.assertEqual(annual['rule_call_structure'],
                         {'fuyi': 'presented', 'tiaohou': 'presented',
                          'bingyao': 'presented',
                          'pattern_yongshen': 'presented'})

    def test_case_b_flow_1970(self):
        systems = evaluate_xiyong(
            day_master='戊', month_branch='午', pillars=CASE_B_PILLARS,
            strength=STRENGTH_B, tiaohou=TIAOHOU_B, bingyao=BINGYAO_B,
            pattern=PATTERN_B, flow_year=1970)['systems']
        annual = evaluate_annual_xiyong(systems, 1970, day_master='戊')
        self.assertEqual(annual['flow_year']['ganzhi'], '庚戌')
        self.assertEqual(annual['flow_year']['stem_ten_god'], '食神')
        refs = annual['flow_references']
        self.assertIs(refs['tiaohou']
                      ['flow_stem_in_natal_tiaohou_sequence'], False)
        roles = {p['pair_id']: p['flow_ten_god_role_in_pair']
                 for p in refs['bingyao']['pairs']}
        self.assertEqual(roles, {'wealth_peer_officer': 'none',
                                 'foodwound_seal_wealth': 'subject'})
        self.assertIsNone(refs['fuyi']
                          ['flow_stem_in_natal_fuyi_modern_candidates'])
        self.assertIs(refs['pattern_yongshen']['flow_stem_in_pattern_basis'],
                      False)

    def test_flow_year_bounds_and_missing_systems(self):
        with self.assertRaises(ValueError):
            evaluate_annual_xiyong({}, 1899, day_master='甲')
        annual = evaluate_annual_xiyong({}, 2000, day_master='甲')
        self.assertEqual(annual['flow_year']['ganzhi'], '庚辰')
        self.assertIsNone(annual['flow_references']['tiaohou']
                          ['flow_stem_in_natal_tiaohou_sequence'])
        self.assertEqual(annual['rule_call_structure'],
                         {'fuyi': 'not_provided', 'tiaohou': 'not_provided',
                          'bingyao': 'not_provided',
                          'pattern_yongshen': 'not_provided'})


class FullEvaluationTests(unittest.TestCase):
    def test_full_case_a(self):
        out = evaluate_xiyong(
            day_master='甲', month_branch='申', pillars=CASE_A_PILLARS,
            strength=STRENGTH_A, tiaohou=TIAOHOU_A, bingyao=BINGYAO_A,
            pattern=PATTERN_A, flow_year=1988)
        self.assertEqual(out['systems']['fuyi']['modern']['direction'],
                         'support')
        self.assertEqual(out['systems']['tiaohou']['operative_candidate']
                         ['stem'], '丁')
        self.assertEqual(out['systems']['bingyao']['pairs'][0]
                         ['yongshen_candidate'][0]['stem'], '庚')
        self.assertEqual([e['pattern_key'] for e in
                          out['systems']['pattern_yongshen']['eligible']],
                         ['pianyin'])
        self.assertEqual(out['annual_xiyong']['flow_year']['ganzhi'], '戊辰')
        self.assertIsNone(out['unified_verdict'])

    def test_full_without_flow_year_and_without_systems(self):
        out = evaluate_xiyong(day_master='甲', month_branch='申')
        self.assertIsNone(out['annual_xiyong'])
        self.assertIsNone(out['pillars'])
        self.assertEqual(out['systems']['fuyi']['status'], 'not_provided')
        self.assertEqual(out['systems']['tiaohou']['status'], 'not_provided')
        self.assertEqual(out['systems']['bingyao']['status'], 'not_provided')
        self.assertEqual(out['systems']['pattern_yongshen']['status'],
                         'not_provided')


def _live_modules():
    """真实引擎模块（仅可信机装配环境可导入）；公开检出返回 None。"""
    try:
        from tianji_kb.bazi_core import chart_from_datetime  # noqa: F401
        from tianji_kb.bazi_core import chart_from_pillars  # noqa: F401
        from tianji_kb.bazi_strength_engine import assess_strength  # noqa: F401
        from tianji_kb.bazi_tiaohou import tiaohou_lookup  # noqa: F401
        from tianji_kb.bazi_bingyao import bingyao_lookup  # noqa: F401
        from tianji_kb.bazi_pattern_engine import evaluate_all  # noqa: F401
        from tianji_kb import bazi_ditiansui_fuyi as fuyi_mod  # noqa: F401
    except Exception:
        return None
    import tianji_kb.bazi_core as core
    import tianji_kb.bazi_strength_engine as strength_mod
    import tianji_kb.bazi_tiaohou as tiaohou_mod
    import tianji_kb.bazi_bingyao as bingyao_mod
    import tianji_kb.bazi_pattern_engine as pattern_mod
    return {'core': core, 'strength': strength_mod, 'tiaohou': tiaohou_mod,
            'bingyao': bingyao_mod, 'pattern': pattern_mod,
            'fuyi_mod': fuyi_mod}


class LiveCrossCheckTests(unittest.TestCase):
    """机上复核：夹具字段与真实引擎输出逐项一致，漂移即失败。"""

    def setUp(self):
        self.live = _live_modules()
        if self.live is None:
            self.skipTest('live engines unavailable in this checkout')

    def test_strength_scores_match_live(self):
        cases = [
            ('1958-08-15T19:30:00+08:00', STRENGTH_A),
            ('1959-06-15T10:30:00+08:00', STRENGTH_B),
            ('1963-03-22T22:00:00+08:00', STRENGTH_STRONG),
            ('1978-09-20T10:00:00+08:00', STRENGTH_WEAK_CLASSICAL),
        ]
        for birth, fixture in cases:
            chart = self.live['core'].chart_from_datetime(birth)
            live = self.live['strength'].assess_strength(
                chart['pillars'], chart['day_master']['stem'])
            self.assertEqual(
                [p['stem']['value'] + p['branch']['value']
                 for p in chart['pillars']], fixture['pillars'], birth)
            self.assertEqual(live['classical']['classification'],
                             fixture['classical']['classification'], birth)
            if fixture['classical']['matched_predicate'] is not None:
                self.assertEqual(
                    live['classical']['matched_predicate']['predicate_id'],
                    fixture['classical']['matched_predicate']
                    ['predicate_id'], birth)
            else:
                self.assertIsNone(live['classical']['matched_predicate'],
                                  birth)
            self.assertEqual(live['modern']['verdict'],
                             fixture['modern']['verdict'], birth)
            self.assertEqual(live['modern']['score'],
                             fixture['modern']['score'], birth)
            live_components = {k: v['score'] for k, v in
                               live['modern']['components'].items()}
            fixture_components = {k: v['score'] for k, v in
                                  fixture['modern']['components'].items()}
            self.assertEqual(live_components, fixture_components, birth)

    def test_tiaohou_bingyao_match_live(self):
        cases = [
            (STRENGTH_A, TIAOHOU_A, BINGYAO_A,
             ['戊', '庚', '甲', '甲'],
             [['戊', '辛', '丁'], ['庚', '壬', '戊'], ['癸'],
              ['戊', '辛', '丁']]),
            (STRENGTH_B, TIAOHOU_B, BINGYAO_B,
             ['己', '庚', '戊', '丁'],
             [['壬', '甲'], ['丁', '己'], ['戊', '乙', '癸'],
              ['丙', '庚', '戊']]),
        ]
        for strength, tiaohou, bingyao, visible, hidden in cases:
            day = strength['day_master']
            month = strength['month_branch']
            live_t = self.live['tiaohou'].tiaohou_lookup(
                day, month, visible, hidden)
            self.assertEqual(live_t['status'], tiaohou['status'], day)
            self.assertEqual(
                [(s['stem'], s['presence']) for s in live_t['sequence']],
                [(s['stem'], s['presence']) for s in tiaohou['sequence']],
                day)
            facts = []
            for name, stem, god in (
                    ('year', visible[0], None), ('month', visible[1], None),
                    ('hour', visible[3], None)):
                facts.append({'pillar': name, 'stem': stem,
                              'ten_god': ten_god_for(day, stem)})
            live_b = self.live['bingyao'].bingyao_lookup(day, facts)
            self.assertEqual(live_b['status'], bingyao['status'], day)
            for live_pair, fixture_pair in zip(live_b['pairs'],
                                               bingyao['pairs']):
                self.assertEqual(live_pair['status'],
                                 fixture_pair['status'], day)
                self.assertEqual(live_pair['medicine_status'],
                                 fixture_pair['medicine_status'], day)

    def test_tiaohou_branch_live(self):
        live = self.live['tiaohou'].tiaohou_lookup(
            '甲', '午', ['甲', '丙', '甲', '丁'],
            [[], [], [], []])
        applied = [b for b in live['branches'] if b['applied']]
        self.assertEqual([b['id'] for b in applied],
                         ['wuyue_fa_gui_yong_ding'])
        self.assertEqual([s['stem'] for s in applied[0]['sequence']],
                         ['丁', '庚'])

    def test_pattern_states_match_live(self):
        cases = [
            (CASE_A_PILLARS, '甲', PATTERN_A),
            (CASE_B_PILLARS, '戊', PATTERN_B),
        ]
        for pillars, day, fixture in cases:
            chart = self.live['core'].chart_from_pillars(*pillars)
            live = self.live['pattern'].evaluate_all(chart)
            for key, result in fixture['results'].items():
                self.assertEqual(live['results'][key]['state'],
                                 result['state'], (day, key))
                self.assertEqual(live['results'][key]['rule_ids'],
                                 result['rule_ids'], (day, key))
        chart = self.live['core'].chart_from_pillars(*T1_PILLARS)
        ren_yin = {'status': 'determined',
                   'determination': {'true_false': 'true',
                                     'pattern': '正财格'},
                   'commander': {'stem': '戊', 'visible_pillars': ['hour'],
                                 'ten_god': '正财'}}
        live = self.live['pattern'].evaluate_all(chart, ren_yin=ren_yin)
        self.assertEqual(live['results']['zhengcai']['state'], 'established')

    def test_fuyi_table_transcription_matches_registered(self):
        live_rows = self.live['fuyi_mod'].FUYI_DIRECTION_TABLE['rows']
        mine = FUYI_DIRECTION_TABLE['rows']
        self.assertEqual(len(live_rows), len(mine))
        for live_row, my_row in zip(live_rows, mine):
            self.assertEqual(live_row['text'], my_row['text'])
            self.assertEqual(live_row['premise_day_master_state'],
                             my_row['premise_day_master_state'])
            self.assertEqual(
                [q['term'] for q in live_row['condition_quantifiers']],
                list(my_row['condition_quantifiers']))
            self.assertEqual(live_row['direction_god'],
                             my_row['direction_god'])


if __name__ == '__main__':
    unittest.main()
