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
    ANNUAL_PENDING_DETAIL,
    BINGYAO_REGISTERED_DEFINITIONS,
    BINGYAO_REGISTERED_NOT_ENCODED_PAIRS,
    FUYI_DIRECTION_TABLE,
    FUYI_MODERN_RULES_V1,
    FUYI_SUPPLEMENTAL_GUARDS,
    FUYI_SUPPLEMENTAL_STATEMENTS,
    FUYI_TERM_GLOSSES,
    MODERN_COMPONENT_RANGES,
    MODERN_SCORE_RANGE,
    MODERN_THRESHOLDS,
    PATTERN_GOD_RELATIONS,
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
# X8 对照：古典强＋现代 balanced（53），无土/丁/四库缺口——balanced 只是
# 现代模型分数区间，本身不代表输入证据不足，不降低结论确定性。
STRENGTH_STRONG_BALANCED = _strength_fixture(
    '甲', '卯', STRONG_PILLARS, 'strong',
    {'predicate_id': 'pure_support', 'verification': 'factor_level_only'},
    _modern_fixture('balanced', 53, _components(20, 15, 20, 10, -12)))
STRENGTH_WEAK_CLASSICAL = _strength_fixture(
    '乙', '酉', WEAK_PILLARS, 'weak',
    {'predicate_id': 'isolated_control', 'verification': 'factor_level_only'},
    _modern_fixture('weak', -35, _components(-15, 0, 0, 0, -20)))
STRENGTH_ABSTAIN_EARTH = _strength_fixture(
    '戊', '巳', ['甲辰', '丙巳', '戊午', '乙卯'], 'indeterminate', None,
    _modern_fixture('abstain', None, None,
                    abstain_reason='earth_form_unbuildable_tj0112',
                    abstain_detail='日主 戊 × 月支 巳 属 TJ-011.2 UNBUILDABLE。'))
# 弱例＋帮身者显干：与 STRENGTH_WEAK_CLASSICAL 同一古典/现代输入，
# 四柱改配甲木年干（劫财）以覆盖提纲衰行「别寻帮身者」的在场路径。
STRENGTH_WEAK_HELPER = _strength_fixture(
    '乙', '酉', ['甲辰', '辛酉', '乙酉', '丁巳'], 'weak',
    {'predicate_id': 'isolated_control', 'verification': 'factor_level_only'},
    _modern_fixture('weak', -35, _components(-15, 0, 0, 0, -20)))
WEAK_HELPER_PILLARS = ['甲辰', '辛酉', '乙酉', '丁巳']
# 形缺例：戊×寅（原注枚举形缺），古典暂不可判、现代 balanced。
STRENGTH_FORM_DEFICIENT = _strength_fixture(
    '戊', '寅', ['己亥', '丙寅', '戊辰', '丁巳'], 'indeterminate', None,
    _modern_fixture('balanced', 53, _components(20, 15, 20, 10, -12)))
FORM_DEFICIENT_PILLARS = ['己亥', '丙寅', '戊辰', '丁巳']


def _tiaohou_fixture(day_master, month_branch, month_label, quote, order_basis,
                     sequence, branches=(), unencoded=(), related=(),
                     notes=()):
    return {
        'variant': 'tiaohou-qiongtong-v1', 'status': 'matched',
        'system': 'tiaohou', 'source_id': 'bazi.source.qiongtong',
        'evidence_level': 'C', 'day_master': day_master,
        'month_branch': month_branch, 'month_label': month_label,
        'entry': {'quote': quote, 'quote_locator': {},
                  'section': {}, 'order_basis': order_basis},
        'sequence': sequence, 'branches': list(branches),
        'unencoded_branches': list(unencoded),
        'related': list(related), 'notes': list(notes),
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
# X4 对照：原典首选丁缺位，庚在盘——在盘首取为庚，只作在盘首取，
# 不冒充原典首选；缺口 canonical_first_absent。
TIAOHOU_A_CANONICAL_ABSENT = _tiaohou_fixture(
    '甲', '申', '七月', '七月甲木,丁火为尊,庚金次之,庚金不可少。',
    '原文「丁火为尊,庚金次之」明示先次,并明示「庚金不可少」。',
    [_seq('丁', 1, 'absent'),
     _seq('庚', 2, 'visible', visible=('month',), hidden=('month:0',))])
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
# 第三批新增覆盖（均转录自已登记 ENTRIES 的原文与先次；presence 由下述
# 显干/藏干事实手算，机上 LiveCrossCheckTests 以同一事实调 live lookup 复核）：
# 甲×午分支未应用：显干 癸/丙/甲/丁，藏干 亥[壬甲]/午[丁己]/子[癸]/卯[乙]。
# 癸透干故分支 wuyue_fa_gui_yong_ding 不应用，主序列 癸/丁/庚生效，原典首选癸。
TIAOHOU_JIA_WU_NOT_APPLIED_PILLARS = ['癸亥', '丙午', '甲子', '丁卯']
TIAOHOU_JIA_WU_NOT_APPLIED = _tiaohou_fixture(
    '甲', '午', '五月', '五六月甲木,木性虚焦,一理共推。五月先癸後丁庚金次之。',
    '原文「五月先癸後丁庚金次之」明示三级先次(节区为五六月合论段)。',
    [_seq('癸', 1, 'visible', visible=('year',)),
     _seq('丁', 2, 'visible', visible=('hour',)),
     _seq('庚', 3, 'absent')],
    branches=[{'id': 'wuyue_fa_gui_yong_ding', 'applied': False,
               'condition': {'absent_stem': '癸'},
               'quote': '或五月乏癸,用丁亦可,要运行北地为隹。',
               'locator': {'line': 42, 'char_start': 2447, 'char_end': 2466},
               'sequence': [_seq('丁', 1, 'visible', visible=('hour',)),
                            _seq('庚', 2, 'absent')],
               'note': '原文「或五月乏癸,用丁亦可」:癸在四柱透干与藏干皆无时，丁可代为首取，庚仍次之。'}],
    unencoded=[{'quote': '五六月甲木,木盛先庚,庚盛先丁。',
                'locator': {'line': 45, 'char_start': 2563, 'char_end': 2579},
                'reason': '条件「木盛/庚盛」为相对旺盛判断,非存在性事实,不在本 Variant 输入契约内,只登记不编码。'}])
# 甲×寅：显干 丙/庚/甲/乙，藏干 辰[乙癸戊]/寅[甲丙戊]/子[癸]/亥[壬甲]。
# 丙透干为原典首选，癸藏于年支；条目注记 1 条（正二月合论段相邻段落登记）。
TIAOHOU_JIA_YIN = _tiaohou_fixture(
    '甲', '寅', '正月', '正月甲木,初春尚有余寒,得丙癸逢,富贵双全。癸藏丙透,名寒木向阳',
    '原文先举「得丙癸逢」按列举顺序定先次,次句「癸藏丙透」以丙透为要、癸为辅。',
    [_seq('丙', 1, 'visible', visible=('year',)),
     _seq('癸', 2, 'hidden', hidden=('year:1',))],
    notes=('正二月合论段(快照字符 1363-1818)含从格与妻子等论述,非调候取用顺序陈述,不编码;仅登记为相邻段落。',))
# 甲×戌 related：显干 丁/戊/甲/癸，藏干 未[己丁乙]/戌[戊辛丁]/子[癸]/酉[辛]。
# 丁癸皆透干，原典首选丁；related 登记「独爱丁火，壬癸滋扶」一段，壬不入序列。
TIAOHOU_JIA_XU = _tiaohou_fixture(
    '甲', '戌', '九月', '九月甲木,端用丁癸,见戊透必贵。',
    '原文「端用丁癸」按列举顺序定先次;同月另一段「独爱丁火,壬癸滋扶」将壬列于滋扶而非端用,壬不入序列(见 related)。',
    [_seq('丁', 1, 'visible', visible=('year',)),
     _seq('癸', 2, 'visible', visible=('hour',))],
    related=[{'quote': '九月甲木,木星凋零,独爱丁火,壬癸滋扶',
              'locator': {'line': 70, 'char_start': 3683, 'char_end': 3702},
              'note': '同条另一段:独爱丁火、壬癸滋扶。壬在此仅列于滋扶,未列入端用顺序,故不入序列;戊在主引文中为「见戊透」之条件陈述,亦不入序列。'}])
# 甲×辰未编码分支：显干 庚/戊/甲/壬，藏干 午[丁己]/辰[乙癸戊]/子[癸]/申[庚壬戊]。
# 庚壬皆透干，原典首选庚；未编码分支「支成金局方可用丁」只登记不编码。
TIAOHOU_JIA_CHEN = _tiaohou_fixture(
    '甲', '辰', '三月', '三月甲木,木气相竭。先取庚金,次用壬水。',
    '原文「先取庚金,次用壬水」明示先次。',
    [_seq('庚', 1, 'visible', visible=('year',)),
     _seq('壬', 2, 'visible', visible=('hour',))],
    unencoded=[{'quote': '或支成金局,方可用丁,不然,三月无用丁之法。惟有先庚後壬取用。',
                'locator': {'line': 34, 'char_start': 2142, 'char_end': 2173},
                'reason': '条件「支成金局」需地支三合/三会成局事实,不在本 Variant 输入契约(日主、月支、天干与藏干存在性)内,只登记不编码。'}])


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


def _pattern_result(key, state, day_stem, month_branch, rule_ids=(),
                    evidence_ids=(), broken_gaps=()):
    return {
        'pattern': PATTERN_NAMES[key], 'pattern_key': key, 'state': state,
        'evidence': [{'id': eid, 'detail': ''} for eid in evidence_ids],
        'limitations': [], 'rule_ids': list(rule_ids),
        'broken_gaps': list(broken_gaps),
        'research_only': True, 'public': False, 'ai': False,
        'variant': 'bazi-pattern-engine-v2',
        'day_stem': day_stem, 'month_branch': month_branch}


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
        results[key] = _pattern_result(key, state, day_stem, month_branch,
                                       rule_ids, evidence_ids)
    return {
        'variant': 'bazi-pattern-engine-v2', 'day_stem': day_stem,
        'month_branch': month_branch, 'results': results,
        # C1：v2 子变体钉住格局结果所依据的已审块；strength_overall 在
        # v2 恒为 None（因素模块不计算整局强弱）。
        'pattern_variant': 'bazi-pattern-structure-candidates-v1',
        'ren_yin_determination_variant': 'ren-pattern-yin-true-v1',
        'luren_route_variant': 'bazi-pattern-luren-route-v1',
        'strength_overall': None,
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
        # 方向表十行给出财星/食伤；第三批 F-1 总纲「旺则宜泄宜伤」
        # 经术语 gloss（伤→官杀）再补官杀，仍只作条件方向、不点火。
        self.assertEqual(out['classical']['conditional_directions'],
                         ['财星', '食伤', '官杀'])
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
                         'approved_research_model')
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
        # 第三批：现代层完备性——分项解释、分项和、推导 trace。
        self.assertEqual(
            [(e['component'], e['score'], e['reading'])
             for e in modern['component_explanations']],
            [('de_ling', 30, 'supports_strong_side'),
             ('de_di', 35, 'supports_strong_side'),
             ('de_shi', 30, 'supports_strong_side'),
             ('shengfu_hidden', 10, 'supports_strong_side'),
             ('kexiehao', 0, 'neutral')])
        self.assertTrue(all(e['at_bound']
                            for e in modern['component_explanations']))
        self.assertEqual(modern['input_completeness'],
                         {'verdict_present': True, 'score_present': True,
                          'score_in_registered_range': True,
                          'band_matches_thresholds': True,
                          'components_present': True,
                          'components_complete': True,
                          'components_sum_matches_score': True,
                          'pillars_present': True,
                          'candidate_stems_computed': True})
        self.assertEqual(
            [step['step'] for step in modern['direction_derivation']],
            ['input', 'rule_match', 'element_resolution',
             'candidate_stems'])
        self.assertEqual(modern['direction_derivation'][0]['score_range'],
                         [-35, 105])

    def test_supplemental_rows_strong_form_full(self):
        # 甲×卯：形全（原注枚举），F-1 总纲与 F-3 总则前提成立但不点火；
        # 提纲旺行缺月支本气十神输入，适用性恒不可判。
        out = evaluate_fuyi(STRENGTH_STRONG, pillars=STRONG_PILLARS)
        classical = out['classical']
        self.assertEqual(classical['form_classification']['form'], '形全')
        self.assertEqual(
            classical['form_classification']['basis'],
            'registered_enumeration')
        by_id = {row['id']: row for row in classical['supplemental_rows']}
        self.assertEqual(len(classical['supplemental_rows']), 8)
        self.assertEqual(len(classical['supplemental_guards']), 6)
        self.assertEqual(by_id['f1-general-strong']['premise_status'],
                         'satisfied')
        self.assertEqual(by_id['f1-general-strong']['conditional_gods'],
                         ['食伤', '官杀'])
        self.assertEqual(
            by_id['f1-general-strong']['row_outcome'],
            'conditional_only_no_mechanical_selection')
        self.assertEqual(by_id['f1-general-weak']['premise_status'],
                         'not_satisfied')
        self.assertEqual(by_id['f2-form-full']['premise_status'],
                         'satisfied')
        self.assertEqual(by_id['f2-form-full']['direction_verbs'], ['损'])
        self.assertEqual(by_id['f2-form-full']['conditional_gods'], [])
        self.assertEqual(by_id['f2-form-full']['row_outcome'],
                         'cannot_fire_quantifier_unthresholded')
        self.assertEqual(by_id['f2-form-deficient']['premise_status'],
                         'not_satisfied')
        self.assertEqual(by_id['f3-general']['premise_status'], 'satisfied')
        self.assertEqual(by_id['f3-general']['conditional_gods'], [])
        self.assertEqual(by_id['f3-tigang-strong']['premise_status'],
                         'satisfied')
        self.assertEqual(
            by_id['f3-tigang-strong']['applicability_status'],
            'cannot_judge')
        self.assertEqual(by_id['f3-tigang-strong']['conditional_gods'], [])
        self.assertEqual(by_id['f3-table-preamble']['premise_status'],
                         'cannot_judge')
        self.assertEqual(by_id['f3-table-preamble']['row_outcome'],
                         'cannot_fire_quantifier_unthresholded')
        guards = {g['id']: g for g in classical['supplemental_guards']}
        self.assertEqual(
            guards['f3-reversal-strong']['evaluation'], 'not_evaluated')
        self.assertEqual(len(classical['term_glosses']), 4)
        self.assertEqual(
            [g['term'] for g in classical['term_glosses']],
            ['泄', '伤', '帮', '助'])
        self.assertIsNone(classical['direction'])
        self.assertEqual(classical['direction_status'], 'no_row_fires')

    def test_supplemental_rows_weak_tigang_helper_present(self):
        # 乙×酉弱：表行给印绶/比劫；提纲衰行在显干见甲（劫财）帮身者，
        # 只记其干，不另给方向结论。
        out = evaluate_fuyi(STRENGTH_WEAK_HELPER,
                            pillars=WEAK_HELPER_PILLARS)
        classical = out['classical']
        self.assertIsNone(classical['form_classification']['form'])
        self.assertEqual(
            classical['form_classification']['basis'],
            'analogy_forbidden')
        by_id = {row['id']: row for row in classical['supplemental_rows']}
        self.assertEqual(by_id['f1-general-weak']['conditional_gods'],
                         ['比劫', '印绶'])
        tigang = by_id['f3-tigang-weak']
        self.assertEqual(tigang['premise_status'], 'satisfied')
        self.assertEqual(tigang['applicability_status'], 'satisfied')
        self.assertEqual(tigang['helper_stems'],
                         [{'stem': '甲', 'pillar': 'year',
                           'ten_god': '劫财', 'element': '木'}])
        self.assertEqual(tigang['conditional_gods'], ['比劫'])
        self.assertEqual(out['classical']['conditional_directions'],
                         ['印绶', '比劫'])
        # 未传四柱时提纲衰行适用性不可判、helper_stems 为 None。
        out = evaluate_fuyi(STRENGTH_WEAK_CLASSICAL)
        tigang = {row['id']: row
                  for row in out['classical']['supplemental_rows']
                  }['f3-tigang-weak']
        self.assertEqual(tigang['applicability_status'], 'cannot_judge')
        self.assertIsNone(tigang['helper_stems'])

    def test_supplemental_rows_form_deficient(self):
        out = evaluate_fuyi(STRENGTH_FORM_DEFICIENT,
                            pillars=FORM_DEFICIENT_PILLARS)
        classical = out['classical']
        self.assertEqual(classical['form_classification']['form'], '形缺')
        by_id = {row['id']: row for row in classical['supplemental_rows']}
        self.assertEqual(by_id['f2-form-deficient']['premise_status'],
                         'satisfied')
        self.assertEqual(by_id['f2-form-deficient']['direction_verbs'],
                         ['补'])
        # 古典暂不可判：F-1/F-3 总纲前提恒不可判，条件方向为空。
        self.assertEqual(out['classical']['conditional_directions'], [])
        self.assertEqual(out['status'], 'not_judgeable')

    def test_modern_boundary_validation_fail_closed(self):
        def _drifted(**overrides):
            modern = copy.deepcopy(STRENGTH_A['modern'])
            modern.update(overrides)
            strength = copy.deepcopy(STRENGTH_A)
            strength['modern'] = modern
            return strength
        # 总分出域。
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(score=106))
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(score=-36))
        # verdict 与分数档位不一致（-21 应为 weak，不可标 strong）。
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(verdict='strong'))
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(verdict='balanced'))
        # 分项和不等于总分。
        components = copy.deepcopy(STRENGTH_A['modern']['components'])
        components['de_shi']['score'] = 11
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(components=components))
        # 分项出域。
        components = copy.deepcopy(STRENGTH_A['modern']['components'])
        components['de_ling']['score'] = 31
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(components=components))
        # 未知分项。
        components = copy.deepcopy(STRENGTH_A['modern']['components'])
        components['unknown_item'] = {'score': 0}
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(components=components))
        # 非整数总分。
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(score=-21.0))
        # 弃判态须 score/components 皆为 None。
        with self.assertRaises(ValueError):
            evaluate_fuyi(_drifted(verdict='abstain', score=-21))
        # 分项缺失只记不完备、不拒收：分项解释为空，分项和为 None。
        strength = _drifted(components={})
        out = evaluate_fuyi(strength, pillars=CASE_A_PILLARS)
        self.assertEqual(out['modern']['component_explanations'], [])
        self.assertFalse(
            out['modern']['input_completeness']['components_complete'])
        self.assertIsNone(
            out['modern']['input_completeness']
            ['components_sum_matches_score'])

    def test_modern_abstain_and_not_provided_completeness(self):
        out = evaluate_fuyi(STRENGTH_ABSTAIN_EARTH)
        modern = out['modern']
        self.assertEqual(modern['status'], 'abstain')
        self.assertEqual(modern['input_completeness']['verdict_present'],
                         True)
        self.assertFalse(modern['input_completeness']['score_present'])
        self.assertFalse(modern['input_completeness']['components_present'])
        self.assertEqual(modern['component_explanations'], [])
        self.assertIsNone(modern['direction_derivation'])
        no_modern = copy.deepcopy(STRENGTH_A)
        no_modern['modern'] = None
        out = evaluate_fuyi(no_modern, pillars=CASE_A_PILLARS)
        modern = out['modern']
        self.assertEqual(modern['status'], 'not_provided')
        self.assertFalse(modern['input_completeness']['verdict_present'])
        self.assertTrue(modern['input_completeness']['pillars_present'])
        self.assertFalse(
            modern['input_completeness']['candidate_stems_computed'])

    def test_weak_case_a_component_explanations(self):
        out = evaluate_fuyi(STRENGTH_A, pillars=CASE_A_PILLARS)
        explanations = out['modern']['component_explanations']
        self.assertEqual(
            [(e['component'], e['score'], e['reading'])
             for e in explanations],
            [('de_ling', -15, 'supports_weak_side'),
             ('de_di', 0, 'neutral'),
             ('de_shi', 10, 'supports_strong_side'),
             ('shengfu_hidden', 4, 'supports_strong_side'),
             ('kexiehao', -20, 'supports_weak_side')])
        self.assertEqual(
            [e['at_bound'] for e in explanations],
            [True, True, False, False, True])
        self.assertTrue(
            out['modern']['input_completeness']
            ['components_sum_matches_score'])

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
            'classical_strength_indeterminate',
            'earth_de_di_uncalibrated'])
        self.assertEqual(out['cross_layer']['relationship'],
                         'classical_indeterminate')

    def test_balanced_alone_does_not_lower_certainty(self):
        # X8：balanced 仅是现代模型分数区间，本身不代表输入证据不足；
        # 古典强＋现代 balanced 且无其他缺口时，不确定性为空、置信度为
        # model_candidate（与 STRENGTH_B 的土未校准＋古典暂不可判对照）。
        out = evaluate_fuyi(STRENGTH_STRONG_BALANCED,
                            pillars=STRONG_PILLARS)
        self.assertEqual(out['uncertainty'], [])
        self.assertEqual(out['modern']['confidence'], 'model_candidate')
        self.assertEqual(out['modern']['input_verdict'], 'balanced')
        self.assertIsNone(out['modern']['direction'])
        self.assertEqual(out['cross_layer']['relationship'],
                         'modern_balanced')

    def test_x1_approved_research_model_and_visible_stem_scope(self):
        # X1：FUYI_MODERN_RULES_V1 已批为现代研究模型；X2：候选干只取显干。
        self.assertEqual(FUYI_MODERN_RULES_V1['adjudication_status'],
                         'approved_research_model')
        self.assertEqual(FUYI_MODERN_RULES_V1['adjudication_ref'],
                         'X1 approved 2026-11-25 as modern research model')
        out = evaluate_fuyi(STRENGTH_A, pillars=CASE_A_PILLARS)
        self.assertEqual(out['modern']['candidate_scope'],
                         'visible_stems_only')
        # X2：水（癸）只藏于日支子时不入候选；候选只有显干甲（时柱）。
        self.assertEqual(
            [(c['stem'], c['pillar'], c['ten_god']) for c in
             out['modern']['candidate_stems']],
            [('甲', 'hour', '比肩')])
        self.assertNotIn('癸', [c['stem'] for c in
                                out['modern']['candidate_stems']])

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
                         'approved_research_model')
        self.assertEqual(FUYI_MODERN_RULES_V1['adjudication_ref'],
                         'X1 approved 2026-11-25 as modern research model')
        self.assertEqual(VALIDATED_CANDIDATE_RULE_IDS, frozenset((
            'bazi.phase2.official_pattern_candidates',
            'bazi.phase2.resource_pattern_candidates',
            'bazi.phase2.ren_yin_true_pattern')))
        # 第三批 pin：补充陈述 8 行＋守卫 6 条、现代层边界常量。
        self.assertEqual(len(FUYI_SUPPLEMENTAL_STATEMENTS), 8)
        self.assertEqual(
            [s['id'] for s in FUYI_SUPPLEMENTAL_STATEMENTS],
            ['f1-general-strong', 'f1-general-weak', 'f2-form-full',
             'f2-form-deficient', 'f3-general', 'f3-tigang-strong',
             'f3-tigang-weak', 'f3-table-preamble'])
        self.assertEqual(len(FUYI_SUPPLEMENTAL_GUARDS), 6)
        self.assertEqual(len(FUYI_TERM_GLOSSES), 4)
        self.assertEqual(MODERN_SCORE_RANGE, (-35, 105))
        self.assertEqual(MODERN_THRESHOLDS,
                         {'strong_at_least': 60, 'weak_at_most': 15,
                          'balanced_between': [16, 59]})
        self.assertEqual(MODERN_COMPONENT_RANGES,
                         {'de_ling': (-15, 30), 'de_di': (0, 35),
                          'de_shi': (0, 30), 'shengfu_hidden': (0, 10),
                          'kexiehao': (-20, 0)})
        self.assertEqual(
            [p['pair_id'] for p in BINGYAO_REGISTERED_NOT_ENCODED_PAIRS],
            ['earth_heavy_unencoded', 'officer_strength_tension'])
        self.assertEqual(
            [d['definition_id'] for d in BINGYAO_REGISTERED_DEFINITIONS],
            ['disease_definition', 'medicine_definition'])
        self.assertEqual(
            [d['item'] for d in ANNUAL_PENDING_DETAIL],
            list(ANNUAL_PENDING))
        self.assertEqual(
            PATTERN_GOD_RELATIONS,
            {'正官': 'controls_me', '七杀': 'controls_me',
             '正印': 'generates_me', '偏印': 'generates_me',
             '正财': 'i_control', '偏财': 'i_control',
             '食神': 'i_generate', '伤官': 'i_generate'})


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
        self.assertIn('原典首选 丁', out['conclusion'])
        self.assertEqual(out['canonical_first']['stem'], '丁')
        self.assertEqual(out['operative_kind'], 'canonical_first')
        self.assertEqual([c['stem'] for c in out['in_chart_candidates']],
                         ['丁', '庚'])

    def test_canonical_first_absent_is_not_promoted(self):
        # X4：原典首选丁不在盘，在盘首取庚只作在盘首取，绝不冒充原典首选。
        out = evaluate_tiaohou_xiyong(TIAOHOU_A_CANONICAL_ABSENT)
        self.assertEqual(out['canonical_first']['stem'], '丁')
        self.assertEqual(out['canonical_first']['presence'], 'absent')
        self.assertEqual(
            [c['stem'] for c in out['canonical_alternatives']], ['庚'])
        self.assertEqual(out['operative_candidate']['stem'], '庚')
        self.assertEqual(out['operative_kind'], 'in_chart_first')
        self.assertEqual(out['operative_status'], 'visible')
        self.assertIn('原典首选 丁 不在盘', out['conclusion'])
        self.assertIn('在盘首取 庚', out['conclusion'])
        self.assertNotIn('原典首选 庚', out['conclusion'])
        self.assertIn('canonical_first_absent',
                      [g['gap_id'] for g in out['gaps']])
        self.assertTrue(any(
            c['id'] == 'canonical_first' and c['status'] == 'not_satisfied'
            for c in out['conditions']))

    def test_case_b_operative_hidden(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_B)
        self.assertEqual(out['operative_candidate']['stem'], '壬')
        self.assertEqual(out['operative_candidate']['ten_god'], '偏财')
        self.assertEqual(out['candidates'][1]['ten_god'], '七杀')
        self.assertEqual(out['canonical_first']['stem'], '壬')
        self.assertEqual(out['operative_kind'], 'canonical_first')

    def test_branch_supersedes_main_sequence(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_WU_BRANCH)
        self.assertEqual(out['active_sequence'],
                         'branch:wuyue_fa_gui_yong_ding')
        self.assertEqual([c['stem'] for c in out['candidates']], ['丁', '庚'])
        self.assertEqual(out['operative_candidate']['stem'], '丁')
        self.assertEqual(out['operative_candidate']['presence'], 'visible')
        self.assertEqual(out['canonical_first']['stem'], '丁')
        self.assertEqual(out['operative_kind'], 'canonical_first')

    def test_entry_absent_and_empty_sequence(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_ABSENT)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(out['gaps'][0]['gap_id'], 'entry_absent_in_source')
        out = evaluate_tiaohou_xiyong(TIAOHOU_EMPTY)
        self.assertEqual(out['status'], 'not_judgeable')
        self.assertEqual(
            [g['gap_id'] for g in out['gaps']],
            ['empty_sequence', 'unencoded_branch'])

    def test_branch_not_applied_records_unapplied(self):
        # 甲×午、癸透干：分支不应用，主序列生效，原典首选癸（透干）。
        out = evaluate_tiaohou_xiyong(
            TIAOHOU_JIA_WU_NOT_APPLIED,
            pillars=TIAOHOU_JIA_WU_NOT_APPLIED_PILLARS)
        self.assertEqual(out['status'], 'presented')
        self.assertEqual(out['active_sequence'], 'main')
        self.assertEqual(out['branches']['applied'], [])
        self.assertEqual(len(out['branches']['unapplied']), 1)
        unapplied = out['branches']['unapplied'][0]
        self.assertEqual(unapplied['id'], 'wuyue_fa_gui_yong_ding')
        self.assertEqual(unapplied['condition'], {'absent_stem': '癸'})
        self.assertEqual(unapplied['absent_stem'], '癸')
        self.assertEqual(unapplied['absent_stem_presence'], 'visible')
        self.assertEqual(out['operative_candidate']['stem'], '癸')
        self.assertEqual(out['canonical_first']['stem'], '癸')
        self.assertEqual(out['operative_kind'], 'canonical_first')
        self.assertIn('原典首选 癸', out['conclusion'])
        self.assertEqual(out['operative_status'], 'visible')
        self.assertEqual(
            [c['stem'] for c in out['candidates']], ['癸', '丁', '庚'])
        self.assertEqual(
            [g['gap_id'] for g in out['gaps']], ['unencoded_branch'])
        self.assertTrue(any(
            c['id'] == 'branch_not_applied' and c['status'] == 'not_satisfied'
            for c in out['conditions']))
        # 未传四柱时条件干在场性只记在盘、不区分显干/藏干。
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_WU_NOT_APPLIED)
        self.assertEqual(out['branches']['unapplied'][0]
                         ['absent_stem_presence'],
                         'present_detail_unknown')
        self.assertEqual(out['operative_candidate']['stem'], '癸')
        self.assertEqual(out['canonical_first']['stem'], '癸')
        self.assertEqual(out['operative_kind'], 'canonical_first')

    def test_branch_applied_records_applied(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_WU_BRANCH)
        self.assertEqual(out['branches']['applied'],
                         [{'id': 'wuyue_fa_gui_yong_ding',
                           'condition': {'absent_stem': '癸'},
                           'quote': '或五月乏癸,用丁亦可,要运行北地为隹。',
                           'sequence_stems': ['丁', '庚'],
                           'note': '原文「或五月乏癸,用丁亦可」:癸在四柱透干与藏干皆无时，丁可代为首取，庚仍次之。'}])
        self.assertEqual(out['branches']['unapplied'], [])

    def test_new_month_coverage_jia_yin_xu_chen(self):
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_YIN)
        self.assertEqual(out['operative_candidate']['stem'], '丙')
        self.assertEqual(out['operative_status'], 'visible')
        self.assertEqual(
            [(c['stem'], c['presence']) for c in out['candidates']],
            [('丙', 'visible'), ('癸', 'hidden')])
        self.assertEqual(len(out['entry_notes']), 1)
        self.assertIn('正二月合论段', out['entry_notes'][0])
        self.assertEqual(out['related_entries'], [])
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_XU)
        self.assertEqual(out['operative_candidate']['stem'], '丁')
        self.assertEqual(len(out['related_entries']), 1)
        self.assertIn('壬癸滋扶', out['related_entries'][0]['quote'])
        # related 只登记、不并入序列：候选仍为丁/癸，壬不在其中。
        self.assertEqual([c['stem'] for c in out['candidates']], ['丁', '癸'])
        out = evaluate_tiaohou_xiyong(TIAOHOU_JIA_CHEN)
        self.assertEqual(out['operative_candidate']['stem'], '庚')
        self.assertEqual(
            [g['gap_id'] for g in out['gaps']], ['unencoded_branch'])

    def test_branch_shape_drift_fail_closed(self):
        bad = copy.deepcopy(TIAOHOU_JIA_WU_BRANCH)
        bad['branches'][0]['applied'] = 'yes'
        with self.assertRaises(ValueError):
            evaluate_tiaohou_xiyong(bad)
        bad = copy.deepcopy(TIAOHOU_JIA_WU_BRANCH)
        bad['branches'][0]['condition'] = {'absent_stem': 'X'}
        with self.assertRaises(ValueError):
            evaluate_tiaohou_xiyong(bad)
        bad = copy.deepcopy(TIAOHOU_JIA_XU)
        bad['related'] = [{'quote': 123}]
        with self.assertRaises(ValueError):
            evaluate_tiaohou_xiyong(bad)

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
        # 全缺位时仍有原典首选记录（丁），但无在盘首取、不冒充。
        self.assertEqual(out['canonical_first']['stem'], '丁')
        self.assertIsNone(out['operative_candidate'])
        self.assertIsNone(out['operative_kind'])
        self.assertEqual(out['in_chart_candidates'], [])

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
        # X5：药神类（官杀）所含之干为十神类→干的纯算术展开，只记类不新立规则。
        self.assertEqual(wealth['medicine_class_stems'],
                         [{'stem': '庚', 'ten_god': '七杀', 'element': '金'},
                          {'stem': '辛', 'ten_god': '正官', 'element': '金'}])
        self.assertEqual(wealth['medicine_presence_scope'],
                         'visible_stems_only')
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
        # X5：缺位缺口明记药神类（财）及其所含之干（壬偏财/癸正财）。
        self.assertEqual(gap['medicine_god_class'], '财')
        self.assertEqual(gap['medicine_class_stems'],
                         [{'stem': '壬', 'ten_god': '偏财', 'element': '水'},
                          {'stem': '癸', 'ten_god': '正财', 'element': '水'}])
        self.assertEqual(food['medicine_class_stems'],
                         gap['medicine_class_stems'])
        self.assertEqual(food['medicine_presence_scope'],
                         'visible_stems_only')
        self.assertIn('病已触发、药不在盘', out['conclusion'])

    def test_registered_not_encoded_inventory(self):
        out = evaluate_bingyao_xiyong(BINGYAO_A)
        inventory = out['registered_not_encoded_pairs']
        self.assertEqual(
            [(item['pair_id'], item['status']) for item in inventory],
            [('earth_heavy_unencoded', 'registered_not_encoded'),
             ('officer_strength_tension', 'registered_tension')])
        earth = inventory[0]
        self.assertEqual(earth['quote'], '是则土为诸格之病,俱喜木为医药,以去其病也')
        self.assertEqual(earth['locator'],
                         {'line': 38, 'char_start': 7329, 'char_end': 7350})
        self.assertIn('无操作定义', earth['reason'])
        tension = inventory[1]
        self.assertEqual(tension['medicine_god_class'], None)
        self.assertIn('并存未统一', tension['reason'])
        definitions = out['registered_definitions']
        self.assertEqual(
            [d['quote'] for d in definitions],
            ['何以为之病?原八字中原所害之神也',
             '何以为之药?如八字原有所害之字,而得一字以去之谓了'])
        # 清单只登记、不编码：编码对仍为两对，不产额外药神候选。
        self.assertEqual(len(out['pairs']), 2)
        self.assertEqual(
            [p['pair_id'] for p in out['pairs']],
            ['wealth_peer_officer', 'foodwound_seal_wealth'])
        # 未传入时清单仍在（静态登记知识），编码对为空。
        out = evaluate_bingyao_xiyong(None)
        self.assertEqual(len(out['registered_not_encoded_pairs']), 2)
        self.assertEqual(len(out['registered_definitions']), 2)
        self.assertEqual(out['pairs'], [])

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
        # X6：逐格规则开发方向已批，但具体规则仍待证据审查；即使已成立
        # 的格，useful_god 仍为 None——有资格不等于格局用神已成立。
        dev = out['yongshen_rule_development']
        self.assertEqual(dev['status'], 'approved_in_direction')
        self.assertEqual(dev['adjudication'], 'X6 (2026-11-25)')
        self.assertEqual(dev['per_pattern_rules'],
                         'pending_evidence_review')
        self.assertEqual(dev['useful_god'], 'none_reviewed')
        self.assertIn('有资格只表示可列结构依据', dev['note'])

    def test_case_a_structure_basis(self):
        out = evaluate_pattern_xiyong(PATTERN_A, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        entry = out['eligible'][0]
        self.assertEqual(entry['structure_basis'],
                         {'pattern_god': '偏印',
                          'god_relation_to_day_master': 'generates_me',
                          'god_element': '水',
                          'visible_count': 0,
                          'month_pillar_present': False,
                          'evidence': [{'id': 'month_hidden_god', 'detail': ''},
                                       {'id': 'bazi.phase2.resource_pattern_candidates',
                                        'detail': ''}],
                          'result_limitations': []})
        self.assertEqual(out['counts_by_state'],
                         {'candidate': 3, 'not_judgeable': 9})
        self.assertIsNone(out['basis']['engine_counts'])
        self.assertIsNone(out['basis']['earth_gate'])
        self.assertEqual(out['basis']['counts_by_state'],
                         {'candidate': 3, 'not_judgeable': 9})

    def test_case_b_and_t1_structure_basis(self):
        out = evaluate_pattern_xiyong(PATTERN_B, pillars=CASE_B_PILLARS,
                                      day_master='戊')
        entry = out['eligible'][0]
        self.assertEqual(entry['structure_basis']['god_element'], '火')
        self.assertEqual(entry['structure_basis']['god_relation_to_day_master'],
                         'generates_me')
        self.assertEqual(entry['structure_basis']['visible_count'], 1)
        self.assertFalse(entry['structure_basis']['month_pillar_present'])
        self.assertEqual(out['counts_by_state'],
                         {'candidate': 1, 'not_judgeable': 11})
        out = evaluate_pattern_xiyong(PATTERN_T1, pillars=T1_PILLARS,
                                      day_master='乙')
        entry = out['eligible'][0]
        self.assertEqual(entry['structure_basis']['pattern_god'], '正财')
        self.assertEqual(entry['structure_basis']['god_element'], '土')
        self.assertEqual(entry['structure_basis']['god_relation_to_day_master'],
                         'i_control')
        self.assertEqual(entry['structure_basis']['visible_count'], 1)
        self.assertFalse(entry['structure_basis']['month_pillar_present'])
        self.assertEqual(out['counts_by_state'],
                         {'candidate': 1, 'established': 1,
                          'not_judgeable': 10})

    def test_engine_counts_and_earth_gate_passthrough(self):
        pattern = copy.deepcopy(PATTERN_A)
        pattern['counts'] = {'candidate': 3, 'not_judgeable': 9}
        pattern['earth_gate'] = False
        out = evaluate_pattern_xiyong(pattern, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        self.assertEqual(out['basis']['engine_counts'],
                         {'candidate': 3, 'not_judgeable': 9})
        self.assertIs(out['basis']['earth_gate'], False)
        # 引擎 counts 与结果数不一致即漂移拒收。
        pattern['counts'] = {'candidate': 4, 'not_judgeable': 9}
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(pattern)
        pattern['counts'] = {'candidate': 3, 'not_judgeable': 9}
        pattern['earth_gate'] = 'no'
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(pattern)
        # 证据 detail 非字符串、rule_ids 非字符串即漂移拒收。
        pattern = copy.deepcopy(PATTERN_A)
        pattern['results']['pianyin']['evidence'][0]['detail'] = 123
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(pattern)
        pattern = copy.deepcopy(PATTERN_A)
        pattern['results']['pianyin']['rule_ids'] = [123]
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(pattern)

    def test_no_eligible_pattern(self):
        out = evaluate_pattern_xiyong(PATTERN_NONE, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        self.assertEqual(out['status'], 'no_eligible_pattern')
        self.assertEqual(out['eligible'], [])
        self.assertEqual(out['gaps'][0]['gap_id'],
                         'no_pattern_yields_yongshen')

    def test_not_provided_and_broken_outside_channel_refused(self):
        self.assertEqual(evaluate_pattern_xiyong(None)['status'],
                         'not_provided')
        # 第三批集成：broken 只认伤官见官一途；七杀格破格无已审通道，
        # 仍拒收（合法的伤官破格见新文件 BrokenContractTests）。
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

    def test_pending_detail_names_missing_rules(self):
        annual = evaluate_annual_xiyong(self._systems_a(), 1988,
                                        day_master='甲')
        self.assertEqual(annual['pending'], list(ANNUAL_PENDING))
        self.assertEqual(
            [(d['item'], d['blocked_by_adjudication']) for d in
             annual['pending_detail']],
            [('annual_tiaohou_derivation',
              'X4 已批准原局调候三分口径（2026-11-25）；流年调候推演规则本身仍未立'),
             ('annual_bingyao_derivation',
              'X5 已批准病药药神缺位候选类（2026-11-25）；流年病药推演规则本身仍未立'),
             ('annual_fuyi_derivation',
              'X1 已批准现代扶抑规则本身为研究模型（2026-11-25）；流年扶抑推演规则本身仍未立'),
             ('annual_pattern_yongshen_derivation',
              'X6 已批准逐格规则开发方向（2026-11-25）；具体逐格规则仍待证据审查'),
             ('unified_annual_verdict', 'TJ-013.2 裁决 A（四体系并列呈现、统一裁决恒拒判）')])
        self.assertTrue(all(d['missing_underlying_rule']
                            for d in annual['pending_detail']))
        # 清单本身不变（组合引擎 pin 住 implemented / pending 两清单）。
        self.assertEqual(annual['implemented'], list(ANNUAL_IMPLEMENTED))
        self.assertIsNone(annual['derivation'])
        self.assertIsNone(annual['unified_verdict'])

    def test_case_a_flow_1988(self):
        annual = evaluate_annual_xiyong(self._systems_a(), 1988,
                                        day_master='甲')
        self.assertEqual(annual['status'], 'contract_only_pending_rules')
        self.assertEqual(annual['flow_year']['ganzhi'], '戊辰')
        self.assertEqual(annual['flow_year']['stem_ten_god'], '偏财')
        # X7：新增两项存在性对照只报存在性事实，明标 existence_only，
        # 存在性不等于作用效力。
        for key in ('fuyi', 'pattern_yongshen'):
            ref = annual['flow_references'][key]
            self.assertTrue(ref['existence_only'])
            self.assertIn('存在性不等于作用效力', ref['note'])
            self.assertIn('X7', ref['note'])
        self.assertEqual(annual['implemented'], list(ANNUAL_IMPLEMENTED))
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
        from tianji_kb import bazi_bingyao as bingyao_mod  # noqa: F401
        from tianji_kb import bazi_strength_engine as strength_mod  # noqa: F401
        from tianji_kb import bazi_pattern_engine as pattern_engine_mod  # noqa: F401
    except Exception:
        return None
    import tianji_kb.bazi_core as core
    import tianji_kb.bazi_strength_engine as strength_mod
    import tianji_kb.bazi_tiaohou as tiaohou_mod
    import tianji_kb.bazi_bingyao as bingyao_mod
    import tianji_kb.bazi_pattern_engine as pattern_mod
    return {'core': core, 'strength': strength_mod, 'tiaohou': tiaohou_mod,
            'bingyao': bingyao_mod, 'pattern': pattern_mod,
            'fuyi_mod': fuyi_mod, 'strength_mod': strength_mod,
            'bingyao_mod': bingyao_mod,
            'pattern_engine_mod': pattern_engine_mod}


class TranscriptionTests(unittest.TestCase):
    """补充登记转录核对（本地可跑：bazi_ditiansui_fuyi 为纯数据模块）。

    逐句核对补充陈述/守卫/术语 gloss 的文本与字符定位与登记原文
    FUYI_QUOTES 的判句一致，漂移即失败。
    """

    def test_supplemental_transcription_matches_registered(self):
        try:
            from tianji_kb import bazi_ditiansui_fuyi as fuyi_mod
        except Exception as error:  # noqa: BLE001
            self.skipTest('fuyi registration module unavailable: %s' % error)
        quotes = {q['id']: q for q in fuyi_mod.FUYI_QUOTES}
        sentences = {}
        for quote in fuyi_mod.FUYI_QUOTES:
            for sentence in quote.get('judgment_sentences') or []:
                sentences[sentence['text']] = sentence
        for spec in FUYI_SUPPLEMENTAL_STATEMENTS:
            sentence = sentences.get(spec['text'])
            self.assertIsNotNone(sentence, spec['id'])
            self.assertEqual(sentence['locator']['char_start'],
                             spec['locator']['char_start'], spec['id'])
            self.assertEqual(sentence['locator']['char_end'],
                             spec['locator']['char_end'], spec['id'])
            self.assertEqual(
                [q['term'] for q in sentence.get('quantifiers') or []],
                list(spec['condition_quantifiers']), spec['id'])
            self.assertEqual(quotes[spec['quote_id']]['passage_id'],
                             spec['passage_id'], spec['id'])
        for guard in FUYI_SUPPLEMENTAL_GUARDS:
            sentence = sentences.get(guard['text'])
            self.assertIsNotNone(sentence, guard['id'])
            self.assertEqual(sentence['locator']['char_start'],
                             guard['locator']['char_start'], guard['id'])
            self.assertEqual(sentence['locator']['char_end'],
                             guard['locator']['char_end'], guard['id'])
        for gloss in FUYI_TERM_GLOSSES:
            sentence = sentences.get(gloss['gloss_sentence'])
            self.assertIsNotNone(sentence, gloss['term'])
            self.assertEqual(sentence['locator']['char_start'],
                             gloss['locator']['char_start'], gloss['term'])
            self.assertEqual(sentence['locator']['char_end'],
                             gloss['locator']['char_end'], gloss['term'])


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

    def test_modern_boundaries_match_registered(self):
        strength_mod = self.live['strength_mod']
        self.assertEqual(tuple(MODERN_SCORE_RANGE),
                         tuple(strength_mod.MODERN_SCORE_RANGE))
        self.assertEqual(MODERN_THRESHOLDS['strong_at_least'],
                         strength_mod.MODERN_THRESHOLDS['strong_at_least'])
        self.assertEqual(MODERN_THRESHOLDS['weak_at_most'],
                         strength_mod.MODERN_THRESHOLDS['weak_at_most'])
        self.assertEqual(list(MODERN_THRESHOLDS['balanced_between']),
                         list(strength_mod.MODERN_THRESHOLDS
                              ['balanced_between']))
        for key, (low, high) in MODERN_COMPONENT_RANGES.items():
            self.assertEqual(
                [low, high],
                list(strength_mod.MODERN_WEIGHTS[key]['range']), key)

    def test_tiaohou_new_coverage_matches_live(self):
        cases = [
            # (fixture, visible_stems, hidden_stems)
            (TIAOHOU_JIA_WU_NOT_APPLIED,
             ['癸', '丙', '甲', '丁'],
             [['壬', '甲'], ['丁', '己'], ['癸'], ['乙']]),
            (TIAOHOU_JIA_YIN,
             ['丙', '庚', '甲', '乙'],
             [['乙', '癸', '戊'], ['甲', '丙', '戊'], ['癸'], ['壬', '甲']]),
            (TIAOHOU_JIA_XU,
             ['丁', '戊', '甲', '癸'],
             [['己', '丁', '乙'], ['戊', '辛', '丁'], ['癸'], ['辛']]),
            (TIAOHOU_JIA_CHEN,
             ['庚', '戊', '甲', '壬'],
             [['丁', '己'], ['乙', '癸', '戊'], ['癸'], ['庚', '壬', '戊']]),
        ]
        for fixture, visible, hidden in cases:
            day = fixture['day_master']
            month = fixture['month_branch']
            live = self.live['tiaohou'].tiaohou_lookup(
                day, month, visible, hidden)
            self.assertEqual(live['status'], fixture['status'], day)
            self.assertEqual(
                [(s['stem'], s['presence']) for s in live['sequence']],
                [(s['stem'], s['presence'])
                 for s in fixture['sequence']], (day, month))
            self.assertEqual(
                [(b['id'], b['applied']) for b in live['branches']],
                [(b['id'], b['applied'])
                 for b in fixture['branches']], (day, month))
            for live_branch, fixture_branch in zip(live['branches'],
                                                    fixture['branches']):
                self.assertEqual(
                    [(s['stem'], s['presence'])
                     for s in live_branch['sequence']],
                    [(s['stem'], s['presence'])
                     for s in fixture_branch['sequence']], (day, month))
            self.assertEqual(
                [(u['quote'], u['reason'])
                 for u in live['unencoded_branches']],
                [(u['quote'], u['reason'])
                 for u in fixture['unencoded_branches']], (day, month))
            self.assertEqual(
                [(r['quote'], r['note']) for r in live['related']],
                [(r['quote'], r['note']) for r in fixture['related']],
                (day, month))
            self.assertEqual(list(live['notes']), list(fixture['notes']),
                             (day, month))

    def test_bingyao_inventory_matches_registered(self):
        quotes = {q['id']: q
                  for q in self.live['bingyao_mod'].QUOTES}
        for item in BINGYAO_REGISTERED_NOT_ENCODED_PAIRS:
            quote = quotes[item['quote_id']]
            self.assertEqual(quote['quote'], item['quote'], item['pair_id'])
            self.assertEqual(quote['locator'], item['locator'],
                             item['pair_id'])
            self.assertEqual(quote['section_id'], item['section_id'],
                             item['pair_id'])
        for item in BINGYAO_REGISTERED_DEFINITIONS:
            quote = quotes[item['quote_id']]
            self.assertEqual(quote['quote'], item['quote'],
                             item['definition_id'])
            self.assertEqual(quote['locator'], item['locator'],
                             item['definition_id'])
            self.assertEqual(quote['note'], item['note'],
                             item['definition_id'])

    def test_pattern_v2_pin_accepts_live_v2(self):
        # C1（2026-11-25）：喜用侧 pin 已统一为 v2，live v2 输出接通；
        # 变体、子变体、字段语义与治理旗标逐项校验见下方的拒收测试。
        self.assertEqual(
            self.live['pattern_engine_mod'].PATTERN_ENGINE_VARIANT,
            'bazi-pattern-engine-v2')
        chart = self.live['core'].chart_from_pillars(*CASE_A_PILLARS)
        live = self.live['pattern'].evaluate_all(chart)
        self.assertEqual(live['variant'], 'bazi-pattern-engine-v2')
        out = evaluate_pattern_xiyong(live, pillars=CASE_A_PILLARS,
                                      day_master='甲')
        self.assertEqual(out['basis']['pattern_variant'],
                         'bazi-pattern-engine-v2')
        self.assertEqual(out['basis']['pattern_structure_variant'],
                         'bazi-pattern-structure-candidates-v1')
        self.assertEqual(out['basis']['ren_yin_determination_variant'],
                         'ren-pattern-yin-true-v1')
        self.assertEqual(out['basis']['luren_route_variant'],
                         'bazi-pattern-luren-route-v1')
        self.assertIsNone(out['basis']['strength_overall'])
        self.assertEqual(out['basis']['engine_counts'], live['counts'])
        for entry in out['eligible'] + out['ineligible']:
            key = entry['pattern_key']
            self.assertEqual(entry['broken_gaps'],
                             live['results'][key]['broken_gaps'], key)

    def test_pattern_v2_pin_rejects_v1_and_drifted_inputs(self):
        # C1 拒收口径：v1 变体、缺失 broken_gaps、逐格变体漂移、缺失子变体、
        # strength_overall 非 None、broken_gaps 非字符串条目，一律拒收。
        chart = self.live['core'].chart_from_pillars(*CASE_A_PILLARS)
        live = self.live['pattern'].evaluate_all(chart)

        def _bad(mutate):
            statement = copy.deepcopy(live)
            mutate(statement)
            return statement

        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s.update(
                    variant='bazi-pattern-engine-v1')),
                pillars=CASE_A_PILLARS, day_master='甲')
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s['results']['qisha'].pop('broken_gaps')),
                pillars=CASE_A_PILLARS, day_master='甲')
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s['results']['qisha'].update(
                    variant='bazi-pattern-engine-v1')),
                pillars=CASE_A_PILLARS, day_master='甲')
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s.pop('ren_yin_determination_variant')),
                pillars=CASE_A_PILLARS, day_master='甲')
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s.update(strength_overall='strong')),
                pillars=CASE_A_PILLARS, day_master='甲')
        with self.assertRaises(ValueError):
            evaluate_pattern_xiyong(
                _bad(lambda s: s['results']['qisha'].update(
                    broken_gaps=['ok', 7])),
                pillars=CASE_A_PILLARS, day_master='甲')

    def test_pattern_structure_basis_matches_live(self):
        # live v2 输出直接传入，校验结构依据抽取与 live 证据/计数/土门
        # 一致，并校验 broken_gaps 转录与子变体 basis。
        cases = [
            (CASE_A_PILLARS, '甲', PATTERN_A),
            (CASE_B_PILLARS, '戊', PATTERN_B),
        ]
        for pillars, day, fixture in cases:
            chart = self.live['core'].chart_from_pillars(*pillars)
            live = self.live['pattern'].evaluate_all(chart)
            out = evaluate_pattern_xiyong(live, pillars=pillars,
                                          day_master=day)
            self.assertEqual(out['basis']['engine_counts'],
                             live['counts'], day)
            self.assertEqual(out['basis']['earth_gate'],
                             live['earth_gate'], day)
            self.assertEqual(out['counts_by_state'], live['counts'], day)
            for entry in out['eligible']:
                key = entry['pattern_key']
                live_result = live['results'][key]
                self.assertEqual(entry['structure_basis']['evidence'],
                                 live_result['evidence'], (day, key))
                self.assertEqual(
                    entry['structure_basis']['result_limitations'],
                    live_result['limitations'], (day, key))
                self.assertEqual(entry['rule_ids'],
                                 live_result['rule_ids'], (day, key))
        chart = self.live['core'].chart_from_pillars(*T1_PILLARS)
        ren_yin = {'status': 'determined',
                   'determination': {'true_false': 'true',
                                     'pattern': '正财格'},
                   'commander': {'stem': '戊', 'visible_pillars': ['hour'],
                                 'ten_god': '正财'}}
        live = self.live['pattern'].evaluate_all(chart, ren_yin=ren_yin)
        out = evaluate_pattern_xiyong(live, pillars=T1_PILLARS,
                                      day_master='乙')
        entry = next(e for e in out['eligible']
                     if e['pattern_key'] == 'zhengcai')
        self.assertEqual(entry['structure_basis']['evidence'],
                         live['results']['zhengcai']['evidence'])
        self.assertEqual(entry['structure_basis']['visible_count'], 1)
        self.assertEqual(entry['structure_basis']['god_element'], '土')


if __name__ == '__main__':
    unittest.main()
