"""喜用神实际计算引擎 TJ-0424（P0-3）：四体系并列计算，统一裁决恒拒判。

只消费已有的可执行输出，不产生新的古典裁定、不编造古籍依据：

* 扶抑（``fuyi``）：三层并列。古典定性层逐行求值《滴天髓阐微》任氏
  扶抑方向表十行（``FUYI_DIRECTION_TABLE``，逐字转录自已登记的
  ``bazi_ditiansui_fuyi.FUYI_DIRECTION_TABLE``；转录漂移由专项测试
  在可导入时逐行核对）：每行的「日主旺/弱」前提可由古典层分类核对，
  但十行全部含量化词（多/轻/重/旺/两停/均敌）且全部未阈值化
  （U3 Q1=B：不设计数口径），故古典层没有任何一行能点火，
  只输出「前提成立行的条件方向」作为条件方向，不给方向结论。
  条件谓词层即此逐行核对本身（前提 satisfied / cannot_judge、
  量化词恒 cannot_judge）。现代工程层执行新拟的
  ``FUYI_MODERN_RULES_V1``（研究模型，恒标
  ``model_kind="modern_engineering"``）：以已批准的现代旺衰模型
  ``strength_model_modern_v1`` 的 verdict/score/components 为输入，
  strong→泄耗克、weak→生扶、balanced→不给方向；候选干只取显干中
  方向元素所含之干，且只标 ``candidate``。现代规则是新拟约定，
  ``adjudication_status`` 恒为 ``proposed_pending_adjudication``，
  未经用户裁定不得升格为古典规则。
* 调候（``tiaohou``）：消费 ``tiaohou_lookup`` 输出（穷通宝鉴
  ``tiaohou-qiongtong-v1``）。主序列按原文先次排序，取首个在盘干
  （显干优先于藏干、藏干优先于不在盘）；已应用的分支序列取代主序列；
  每候选干附十神；条目缺失（乙×丑）、序列为空（丙×亥/丁×午）、
  候选全不在盘、未编码分支，全部明记为缺口。
* 病药（``bingyao``）：消费 ``bingyao_lookup`` 输出（神峰通考
  ``bingyao-shenfeng-v1``）。逐对独立：触发且药在盘→药神候选干；
  触发而药不在盘→药神类（官杀/财）明记为缺口；未触发→该对无输出；
  药去病效力恒未裁定；「从重者论」无阈值故不选唯一病神。
* 格局用神（``pattern_yongshen``）：消费格局引擎 ``evaluate_all``
  输出。只对已成立（任氏寅月真格）或有 validated 候选规则
  （正官 Golden 20 / 印绶 Golden 42 / 任氏 D-1）的格列资格；
  但密封树中全部格的 ``useful_god`` 恒未审，故任何格都不输出用神——
  输出为「无已审用神规则」的确定结论，附该格的结构依据（格神、
  显干位置）与未覆盖原因；无资格的格不输出用神，只记原因。
  ``broken`` 永不输出。

四体系结果独立输出；每体系输出必含结论、输入依据、适用条件、
局限/不确定性标记。流年喜用（``evaluate_annual_xiyong``）接入组合
引擎 ``contract_only_pending_rules`` 已实现的 4 项（流年干支与十神、
流年干在原局调候序列中的存在性、流年干十神在病药对中的角色、
规则调用结构），另加两项同类存在性对照（扶抑现代候选干、格局结构
依据）；其余 5 项保持 pending 并明记。``unified_verdict`` 恒为 None
（TJ-013.2 裁决 A）。

本模块只依赖纯常量模块 ``foundations``，公开检出可直接执行；
不 import ``bazi_core`` / 强度 / 格局 / 调候 / 病药模块（它们依赖
历法 provider 与密封数据），输入一律为调用方传入的已审输出字典，
变体与治理旗标漂移一律 fail-closed（ValueError）。
恒 research_only=True、public_enabled=False、ai_enabled=False；
不新增公开字段，不接公开 API。
"""

from .foundations import (
    BRANCHES, CYCLE, GENERATES, CONTROLS, STEMS, ganzhi_index, stem_element)

XIYONG_ENGINE_VARIANT = 'bazi-xiyong-engine-v1'
ANNUAL_CONTRACT_VARIANT = 'bazi-xiyong-annual-contract-v1'

STRENGTH_ENGINE_VARIANT = 'bazi-strength-engine-v1'
MODERN_MODEL_ID = 'strength_model_modern_v1'
TIAOHOU_VARIANT = 'tiaohou-qiongtong-v1'
BINGYAO_VARIANT = 'bingyao-shenfeng-v1'
PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v1'

# 格局引擎中带 validated 候选规则的 rule_id（正官 Golden 20、
# 印绶 Golden 42、任氏 D-1 Golden 15）。仅观察（rule_ids 为空）的
# 候选不在此列，无资格输出格局用神。
VALIDATED_CANDIDATE_RULE_IDS = frozenset((
    'bazi.phase2.official_pattern_candidates',
    'bazi.phase2.resource_pattern_candidates',
    'bazi.phase2.ren_yin_true_pattern',
))

# 格键 -> 格神（十神）。建禄/阳刃/杂气/特殊无十神格神。
PATTERN_TEN_GODS = {
    'zhengguan': '正官', 'qisha': '七杀', 'zhengyin': '正印',
    'pianyin': '偏印', 'zhengcai': '正财', 'piancai': '偏财',
    'shishen': '食神', 'shangguan': '伤官',
}

# --- 扶抑方向表 -------------------------------------------------------
# 逐字转录自 bazi_ditiansui_fuyi.FUYI_DIRECTION_TABLE（《滴天髓阐微》
# 任氏曰「日主为体者」段，快照字符 35697–35862，source
# bazi.source.ditiansui-spouse）。行序、断句与量化词不归一化；
# 转录正确性由专项测试在可导入时逐行核对原文模块，漂移即失败。
FUYI_DIRECTION_TABLE = {
    'source_id': 'bazi.source.ditiansui-spouse',
    'passage_id': 'ditiansui.fuyi_tiyong',
    'layer': '任氏曰',
    'lead_in': '日主为体者',
    'closing': '此皆用神之的当者也。',
    'body_locator': {'char_start': 35697, 'char_end': 35862},
    'rows': (
        {'row': 1, 'text': '日主旺,印绶多,必要财星为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多',), 'direction_god': '财星'},
        {'row': 2, 'text': '日主旺,官杀轻,亦以财星为用。',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('轻',), 'direction_god': '财星'},
        {'row': 3, 'text': '日主旺,比劫多 ,耐我财星,以食伤为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多',), 'direction_god': '食伤'},
        {'row': 4, 'text': '日主旺,比劫多,而财星轻,亦以食伤为用。',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多', '轻'), 'direction_god': '食伤'},
        {'row': 5, 'text': '日主旺,官星轻,銕绶重,以财星为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('轻', '重'), 'direction_god': '财星'},
        {'row': 6, 'text': '日主弱,官杀旺,则以印绶为用,',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('旺',), 'direction_god': '印绶'},
        {'row': 7, 'text': '日主弱,食伤多,亦以印绶为用;',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('多',), 'direction_god': '印绶'},
        {'row': 8, 'text': '日主弱,财星旺,则以比劫为用。',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('旺',), 'direction_god': '比劫'},
        {'row': 9, 'text': '日主与官杀两停者,则以食伤为用;',
         'premise_day_master_state': '两停',
         'condition_quantifiers': ('两停',), 'direction_god': '食伤'},
        {'row': 10, 'text': '日主与财星均敌者,则以印比为用。',
         'premise_day_master_state': '均敌',
         'condition_quantifiers': ('均敌',), 'direction_god': '印比'},
    ),
}

# 方向神类 -> 相对日主的五行关系。印比 = 生我 + 同类。
_DIRECTION_GOD_RELATIONS = {
    '财星': ('i_control',),
    '食伤': ('i_generate',),
    '印绶': ('generates_me',),
    '比劫': ('same_element',),
    '印比': ('generates_me', 'same_element'),
}

# --- 扶抑现代工程规则（新拟，需用户裁定）------------------------------
# 以 strength_model_modern_v1 的 verdict 为输入的方向映射。阈值沿用
# 已批准的现代模型阈值（strong >= 60、weak <= 15、其余 balanced），
# 但「verdict→方向」的映射本身是本批新拟的工程约定，未经裁定前
# 只作研究级候选，恒标 proposed_pending_adjudication，绝不冒充古典规则。
FUYI_MODERN_RULES_V1 = {
    'model_id': 'fuyi-modern-rules-v1',
    'model_kind': 'modern_engineering',
    'adjudication_status': 'proposed_pending_adjudication',
    'input_model_id': MODERN_MODEL_ID,
    'input_thresholds': {'strong_at_least': 60, 'weak_at_most': 15,
                         'balanced_between': [16, 59]},
    'rules': (
        {'rule_id': 'fuyi-modern-strong', 'modern_verdict': 'strong',
         'direction': 'drain_control', 'direction_cn': '泄耗克',
         'element_relations': ('i_generate', 'i_control', 'controls_me'),
         'ten_god_classes': ('食神', '伤官', '正财', '偏财', '正官', '七杀')},
        {'rule_id': 'fuyi-modern-weak', 'modern_verdict': 'weak',
         'direction': 'support', 'direction_cn': '生扶',
         'element_relations': ('same_element', 'generates_me'),
         'ten_god_classes': ('比肩', '劫财', '正印', '偏印')},
        {'rule_id': 'fuyi-modern-balanced', 'modern_verdict': 'balanced',
         'direction': None, 'direction_cn': None,
         'element_relations': (), 'ten_god_classes': ()},
    ),
}

# 流年喜用：组合引擎契约已实现的 4 项 + 本引擎新增的 2 项同类存在性对照。
ANNUAL_IMPLEMENTED = (
    'flow_year_ganzhi_and_ten_god',
    'flow_stem_presence_against_natal_tiaohou_sequence',
    'flow_stem_ten_god_role_against_bingyao_pairs',
    'rule_call_structure',
    'flow_stem_presence_against_fuyi_modern_candidates',
    'flow_stem_presence_against_pattern_basis',
)
ANNUAL_PENDING = (
    'annual_tiaohou_derivation',
    'annual_bingyao_derivation',
    'annual_fuyi_derivation',
    'annual_pattern_yongshen_derivation',
    'unified_annual_verdict',
)

GLOBAL_LIMITATIONS = (
    '本引擎 research_only / public_enabled=false / ai_enabled=false，'
    '不接任何公开场景；不新增公开字段。',
    '四体系并列呈现、统一裁决恒拒判（TJ-013.2 裁决 A）；'
    'unified_verdict 恒为 None，任何体系的候选都不合并为统一喜用神。',
    '古典与现代工程模型严格区分：现代层恒标 modern_engineering、'
    'research_only，不冒充古典规则；新拟的现代扶抑规则未经用户裁定，'
    '只作研究级候选。',
    '本引擎不输出吉凶、婚恋、事业、财富断语；不调用真实模型，不开启公开 AI。',
)

_TEN_GOD_BY_RELATION = {
    'same_element': {'same_polarity': '比肩', 'different_polarity': '劫财'},
    'generates_me': {'same_polarity': '偏印', 'different_polarity': '正印'},
    'i_generate': {'same_polarity': '食神', 'different_polarity': '伤官'},
    'controls_me': {'same_polarity': '七杀', 'different_polarity': '正官'},
    'i_control': {'same_polarity': '偏财', 'different_polarity': '正财'},
}
_STEM_POLARITY = {stem: ('阳' if i % 2 == 0 else '阴')
                  for i, stem in enumerate(STEMS)}


def _fail(message):
    raise ValueError(message)


def _relation_of(day_element, target_element):
    if target_element == day_element:
        return 'same_element'
    if GENERATES[target_element] == day_element:
        return 'generates_me'
    if GENERATES[day_element] == target_element:
        return 'i_generate'
    if CONTROLS[target_element] == day_element:
        return 'controls_me'
    return 'i_control'


def ten_god_for(day_master, target_stem):
    """十神：与 bazi_core.ten_god 同一判定（五行关系＋阴阳同异性）。

    本地实现，只依赖 foundations，不 import 组合引擎或 bazi_core。
    """
    if day_master not in STEMS or target_stem not in STEMS:
        _fail('ten_god_for requires two heavenly stems')
    relation = _relation_of(stem_element(day_master),
                            stem_element(target_stem))
    polarity = ('same_polarity'
                if _STEM_POLARITY[day_master] == _STEM_POLARITY[target_stem]
                else 'different_polarity')
    return _TEN_GOD_BY_RELATION[relation][polarity]


def _condition(condition_id, statement, status, basis=None):
    row = {'id': condition_id, 'statement': statement, 'status': status}
    if basis is not None:
        row['basis'] = basis
    return row


def _check_statement(statement, variant, label):
    if not isinstance(statement, dict):
        _fail('%s statement must be an object' % label)
    if statement.get('variant') != variant:
        _fail('%s statement variant drifted' % label)
    if statement.get('research_only') is not True:
        _fail('%s statement research_only drifted' % label)
    if statement.get('public_enabled') is not False:
        _fail('%s statement public_enabled drifted' % label)
    if statement.get('ai_enabled') is not False:
        _fail('%s statement ai_enabled drifted' % label)
    return statement


def _normalize_pillars(pillars, day_master):
    """四柱归一化：ganzhi 字符串或 pillar 对象列表，年/月/日/时顺序。"""
    if type(pillars) is not list or len(pillars) != 4:
        _fail('pillars must be four ordered year/month/day/hour pillars')
    names = ('year', 'month', 'day', 'hour')
    normalized = []
    for index, pillar in enumerate(pillars):
        name = names[index]
        if isinstance(pillar, str):
            ganzhi_index(pillar)
            stem, branch = pillar[0], pillar[1]
        elif isinstance(pillar, dict):
            stem = pillar.get('stem')
            if isinstance(stem, dict):
                stem = stem.get('value')
            branch = pillar.get('branch')
            if isinstance(branch, dict):
                branch = branch.get('value')
            if type(stem) is not str or stem not in STEMS:
                _fail('%s stem must be one heavenly stem' % name)
            if type(branch) is not str or branch not in BRANCHES:
                _fail('%s branch must be one earthly branch' % name)
        else:
            _fail('pillar must be a ganzhi string or a pillar object')
        normalized.append({'name': name, 'ganzhi': stem + branch,
                           'stem': stem, 'branch': branch,
                           'stem_ten_god': ('日主' if name == 'day'
                                            else ten_god_for(day_master, stem)),
                           'stem_element': stem_element(stem)})
    if normalized[2]['stem'] != day_master:
        _fail('day_master must equal the day pillar stem')
    return normalized


def _validate_day_month(day_master, month_branch):
    if type(day_master) is not str or day_master not in STEMS:
        _fail('day_master must be one heavenly stem')
    if type(month_branch) is not str or month_branch not in BRANCHES:
        _fail('month_branch must be one earthly branch')


def _modern_uncertainty(modern):
    """把现代模型的 Q5/Q6/Q9 不确定性传导为喜用层的标记。"""
    flags = []
    if not isinstance(modern, dict):
        return flags
    limitations = modern.get('limitations') or []
    text = '\n'.join(str(item) for item in limitations)
    if '土日主无已审重根集' in text:
        flags.append('earth_de_di_uncalibrated')
    if '丁日主火重根集未审' in text:
        flags.append('ding_de_di_uncalibrated')
    if '四库' in text and '得令分恒为 0' in text:
        flags.append('tomb_de_ling_zero_provisional')
    if '四库' in text and '得令分记 0' in text:
        flags.append('tomb_de_ling_zero_provisional')
    if modern.get('verdict') == 'balanced':
        flags.append('balanced_middle_band_only')
    return sorted(set(flags))


def _classical_direction_rows(classification):
    """古典方向表逐行核对：前提可判、量化词恒不可判、故无行点火。"""
    rows = []
    conditional = []
    premise_map = {'strong': '旺', 'weak': '弱'}
    for spec in FUYI_DIRECTION_TABLE['rows']:
        premise = spec['premise_day_master_state']
        if premise in ('旺', '弱'):
            if classification in premise_map \
                    and premise_map[classification] == premise:
                premise_status = 'satisfied'
            elif classification in ('strong', 'weak'):
                premise_status = 'not_satisfied'
            else:
                premise_status = 'cannot_judge'
        else:  # 两停 / 均敌：古典层无此分类，恒不可判。
            premise_status = 'cannot_judge'
        row = {
            'row': spec['row'],
            'text': spec['text'],
            'premise_day_master_state': premise,
            'premise_status': premise_status,
            'condition_quantifiers': [
                {'term': term, 'status': 'cannot_judge',
                 'reason': 'quantifier_unthresholded_no_counting_convention'}
                for term in spec['condition_quantifiers']],
            'direction_god': spec['direction_god'],
            'row_outcome': 'cannot_fire_quantifier_unthresholded',
        }
        rows.append(row)
        if premise_status == 'satisfied' \
                and spec['direction_god'] not in conditional:
            conditional.append(spec['direction_god'])
    return rows, conditional


def evaluate_fuyi(strength, *, pillars=None):
    """扶抑取用：古典定性层＋条件谓词层＋现代工程层，三层并列。

    ``strength`` 为 ``assess_strength`` 的输出字典（可为 None，
    表示未传入）。``pillars`` 为四柱（可选；用于现代候选干的显干核对）。
    """
    base = {'system': 'fuyi', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if strength is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'classical': None, 'modern': None, 'cross_layer': None,
                'basis': None,
                'conditions': [_condition(
                    'strength_input', '未传入已审强弱输出', 'not_satisfied')],
                'limitations': [
                    '未传入强弱输出：古典层与现代层均无输入依据，扶抑不作任何判断。'],
                'uncertainty': ['strength_input_missing']}
    _check_statement(strength, STRENGTH_ENGINE_VARIANT, 'strength')
    day_master = strength.get('day_master')
    month_branch = strength.get('month_branch')
    _validate_day_month(day_master, month_branch)
    classical_in = strength.get('classical') or {}
    classification = classical_in.get('classification')
    if classification not in ('strong', 'weak', 'indeterminate'):
        _fail('strength classical classification drifted')
    matched = classical_in.get('matched_predicate')
    matched_id = matched.get('predicate_id') if isinstance(matched, dict) \
        else None
    modern_in = strength.get('modern')
    if modern_in is not None:
        if not isinstance(modern_in, dict):
            _fail('strength modern layer must be an object or None')
        if modern_in.get('model_id') != MODERN_MODEL_ID:
            _fail('strength modern model_id drifted')
        if modern_in.get('model_kind') != 'modern_engineering':
            _fail('strength modern model_kind drifted')
        if modern_in.get('verdict') not in (
                'strong', 'weak', 'balanced', 'abstain'):
            _fail('strength modern verdict drifted')

    # 古典层：逐行核对方向表；无行点火，只给前提成立行的条件方向。
    rows, conditional = _classical_direction_rows(classification)
    classical = {
        'layer': 'classical_qualitative',
        'classification': classification,
        'matched_predicate': matched_id,
        'matched_predicate_verification': (
            matched.get('verification') if isinstance(matched, dict) else None),
        'rows': rows,
        'conditional_directions': conditional,
        'direction': None,
        'direction_status': 'no_row_fires',
        'reason': ('方向表十行全部含量化词（多/轻/重/旺/两停/均敌）且'
                   '未阈值化（U3 Q1=B：不设计数口径），故古典层不给方向结论；'
                   '前提成立行的方向神只作条件方向并列。'),
    }

    # 现代层：新拟规则（待裁定）以现代 verdict 定方向与候选干。
    uncertainty = _modern_uncertainty(modern_in) if modern_in else []
    if classification == 'indeterminate':
        uncertainty.append('classical_strength_indeterminate')
    uncertainty = sorted(set(uncertainty))
    modern = None
    if modern_in is None:
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': 'not_provided',
            'input_verdict': None, 'input_score': None,
            'rule_id': None, 'direction': None, 'direction_cn': None,
            'direction_elements': [], 'ten_god_classes': [],
            'candidate_stems': None,
            'confidence': None,
            'uncertainty': uncertainty,
            'reason': '未启用现代模型（include_modern=False），现代层无输入。'}
    elif modern_in.get('verdict') == 'abstain':
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': 'abstain',
            'input_verdict': 'abstain',
            'input_score': None,
            'abstain_reason': modern_in.get('abstain_reason'),
            'abstain_detail': modern_in.get('abstain_detail'),
            'rule_id': None, 'direction': None, 'direction_cn': None,
            'direction_elements': [], 'ten_god_classes': [],
            'candidate_stems': None,
            'confidence': None,
            'uncertainty': uncertainty,
            'reason': '现代模型弃判（%s），现代层不给扶抑方向。'
                      % modern_in.get('abstain_reason')}
    else:
        verdict = modern_in.get('verdict')
        rule = next((r for r in FUYI_MODERN_RULES_V1['rules']
                     if r['modern_verdict'] == verdict), None)
        direction_elements = []
        day_element = stem_element(day_master)
        for relation in rule['element_relations']:
            for element in ('木', '火', '土', '金', '水'):
                if _relation_of(day_element, element) == relation:
                    direction_elements.append(element)
        candidate_stems = None
        if pillars is not None:
            normalized = _normalize_pillars(pillars, day_master)
            candidate_stems = []
            for row in normalized:
                if row['name'] == 'day':
                    continue
                if row['stem_element'] in direction_elements:
                    candidate_stems.append({
                        'stem': row['stem'], 'pillar': row['name'],
                        'ten_god': row['stem_ten_god'],
                        'element': row['stem_element']})
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': ('direction_candidate'
                       if rule['direction'] is not None
                       else 'indeterminate_direction'),
            'input_verdict': verdict,
            'input_score': modern_in.get('score'),
            'input_components': modern_in.get('components'),
            'rule_id': rule['rule_id'],
            'direction': rule['direction'],
            'direction_cn': rule['direction_cn'],
            'direction_elements': direction_elements,
            'ten_god_classes': list(rule['ten_god_classes']),
            'candidate_stems': candidate_stems,
            'confidence': ('provisional' if uncertainty
                           else 'model_candidate'),
            'uncertainty': uncertainty,
            'reason': (
                '现代模型 %s（%s 分）：方向 %s。'
                % (verdict, modern_in.get('score'), rule['direction_cn'])
                if rule['direction'] is not None else
                '现代模型 balanced（%s 分）只是中间分数带（Q9），'
                '不是古典中和裁决：现代层不给扶抑方向。'
                % modern_in.get('score')),
        }

    # 两层关系：并列，不以任一侧覆盖另一侧。
    modern_verdict = modern_in.get('verdict') if modern_in else None
    if modern_in is None:
        relationship, note = 'modern_not_provided', '现代模型未启用。'
    elif modern_verdict == 'abstain':
        relationship = 'modern_abstains'
        note = '现代层弃判（%s）；古典层结论 %s 保持独立。' % (
            modern_in.get('abstain_reason'), classification)
    elif classification == 'indeterminate':
        relationship = 'classical_indeterminate'
        note = '古典层暂不可判；现代层 %s 只是工程近似，不替古典层裁决。' \
            % modern_verdict
    elif ((classification == 'strong' and modern_verdict == 'strong')
            or (classification == 'weak' and modern_verdict == 'weak')):
        relationship = 'agree'
        note = '两层结论一致（%s），但依据不同：古典谓词 vs 工程评分，仍并列报告。' \
            % classification
    elif modern_verdict == 'balanced':
        relationship = 'modern_balanced'
        note = '古典层 %s；现代层 balanced（中间带），不是古典中和裁决。' \
            % classification
    else:
        relationship = 'conflict'
        note = '两层冲突：古典层 %s，现代层 %s；不强制统一，待用户裁定。' \
            % (classification, modern_verdict)
    cross_layer = {'classical': classification, 'modern': modern_verdict,
                   'relationship': relationship, 'note': note}

    modern_direction = modern.get('direction_cn')
    if modern_direction is not None:
        status = 'presented'
        conclusion = '扶抑现代层候选方向：%s（研究模型，未裁定）；古典层无方向结论。' \
            % modern_direction
    elif conditional:
        status = 'presented'
        conclusion = '扶抑只给条件方向：古典前提成立行的方向神为 %s（量化词未阈值化，须另行裁定）；现代层未给方向。' \
            % '、'.join(conditional)
    else:
        status = 'not_judgeable'
        conclusion = None
    conditions = [
        _condition('classical_premise_evaluated',
                   '古典层分类 %s 已用于方向表十行的前提核对' % classification,
                   'satisfied'),
        _condition('direction_table_quantifiers',
                   '方向表十行的量化词（多/轻/重/旺/两停/均敌）全部未阈值化',
                   'cannot_judge',
                   basis='U3 Q1=B：不设计数口径；B2 扶抑重开后集中裁定'),
        _condition('modern_input',
                   '现代模型 verdict=%s score=%s'
                   % (modern_verdict, modern_in.get('score')
                      if modern_in else None),
                   'satisfied' if modern_in is not None else 'not_satisfied'),
    ]
    limitations = [
        '古典扶抑方向表十行全部含量化词且未阈值化：本层不输出古典方向结论，'
        '只列前提成立行的条件方向；涉及改变阈值化的规则须集中提交用户裁定。',
        '现代扶抑规则（FUYI_MODERN_RULES_V1）是新拟工程约定，未经用户裁定，'
        '只作研究级候选；候选干只取显干，不据藏干补位，不作确定用神。',
        'balanced 只是现代模型中间分数带（Q9），不是古典中和：balanced 时'
        '现代层不给方向。',
        '土日主得地未校准（Q5）、四库月得令记零（Q6）的不确定性已由 '
        'uncertainty 标记传导进本层，confidence 相应降为 provisional，'
        '不得在喜用层洗成确定结论。',
        '从格候选屏、合化未裁定等现代模型弃判原因原样传导：现代层弃判时'
        '不另给方向。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'classical': classical, 'modern': modern,
            'cross_layer': cross_layer,
            'basis': {
                'strength_variant': STRENGTH_ENGINE_VARIANT,
                'day_master': day_master, 'month_branch': month_branch,
                'classical_classification': classification,
                'classical_matched_predicate': matched_id,
                'modern_verdict': modern_verdict,
                'modern_score': modern_in.get('score')
                                if modern_in else None},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': uncertainty}


def evaluate_tiaohou_xiyong(tiaohou, *, pillars=None):
    """调候取用：消费 tiaohou_lookup 输出，月令条件→候选调候用神。"""
    base = {'system': 'tiaohou', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if tiaohou is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'condition': None, 'active_sequence': None,
                'candidates': [], 'operative_candidate': None,
                'operative_status': None, 'gaps': [],
                'basis': None,
                'conditions': [_condition(
                    'tiaohou_input', '未传入已审调候输出', 'not_satisfied')],
                'limitations': ['未传入调候输出，本体系不补调候判断。'],
                'uncertainty': ['tiaohou_input_missing']}
    _check_statement(tiaohou, TIAOHOU_VARIANT, 'tiaohou')
    day_master = tiaohou.get('day_master')
    month_branch = tiaohou.get('month_branch')
    _validate_day_month(day_master, month_branch)
    status_in = tiaohou.get('status')
    if status_in not in ('matched', 'not_applicable'):
        _fail('tiaohou statement status drifted')
    gaps = []
    conditions = []
    if status_in == 'not_applicable':
        return {**base, 'status': 'not_judgeable', 'conclusion': None,
                'condition': {'day_master': day_master,
                              'month_branch': month_branch},
                'active_sequence': None, 'candidates': [],
                'operative_candidate': None, 'operative_status': None,
                'gaps': [{'gap_id': 'entry_absent_in_source',
                          'detail': '乙木十二月条目在审定快照中不存在，'
                                    '不以其他月份条目或其他典籍补齐。'}],
                'basis': {'tiaohou_variant': TIAOHOU_VARIANT,
                          'day_master': day_master,
                          'month_branch': month_branch,
                          'status': status_in},
                'conditions': [_condition(
                    'tiaohou_entry', '该日主×月支无审定条目', 'not_satisfied')],
                'limitations': ['条目缺失是来源缺口，不是该盘无调候之论；'
                                '本体系不外推、不借他月条目。'],
                'uncertainty': ['tiaohou_entry_absent']}
    entry = tiaohou.get('entry') or {}
    sequence_in = tiaohou.get('sequence') or []
    branches_in = tiaohou.get('branches') or []
    active_kind = 'main'
    active_sequence = sequence_in
    applied_branch = None
    for branch in branches_in:
        if branch.get('applied'):
            applied_branch = branch
            active_kind = 'branch:%s' % branch.get('id')
            active_sequence = branch.get('sequence') or []
            break
    candidates = []
    for item in active_sequence:
        stem = item['stem']
        candidates.append({
            'stem': stem, 'order': item['order'],
            'presence': item['presence'],
            'visible_positions': list(item.get('visible_positions') or []),
            'hidden_positions': list(item.get('hidden_positions') or []),
            'ten_god': ten_god_for(day_master, stem),
            'element': stem_element(stem)})
    operative = next((c for c in candidates if c['presence'] != 'absent'),
                     None)
    operative_status = (operative['presence'] if operative is not None
                        else 'absent_all')
    if not active_sequence:
        gaps.append({'gap_id': 'empty_sequence',
                     'detail': '该条目无无条件取用顺序（取用皆系于成局、'
                               '相对旺盛、节气分界等条件），本体系不拟制序列。'})
    if operative is None and active_sequence:
        gaps.append({'gap_id': 'candidates_absent_in_chart',
                     'detail': '调候候选干 %s 均不在盘中（既不透干亦不藏干）；'
                               '本局无在场调候候选，须由大运/流年补位与否另行判断，'
                               '本体系不据缺位推断。'
                     % '、'.join(c['stem'] for c in candidates)})
    for unencoded in tiaohou.get('unencoded_branches') or []:
        gaps.append({'gap_id': 'unencoded_branch',
                     'detail': '未编码分支（条件超出输入契约）：%s；原因：%s'
                               % (unencoded.get('quote'),
                                  unencoded.get('reason'))})
    if applied_branch is not None:
        conditions.append(_condition(
            'branch_applied', '分支 %s 已应用（%s 不在盘），分支序列取代主序列'
            % (applied_branch.get('id'),
               (applied_branch.get('condition') or {}).get('absent_stem')),
            'satisfied', basis=applied_branch.get('note')))
    else:
        conditions.append(_condition(
            'branch_applied', '无已应用的分支条件，主序列生效',
            'not_satisfied'))
    conditions.append(_condition(
        'operative_candidate_present',
        '首个在盘候选干：%s' % (operative['stem'] if operative else '无'),
        'satisfied' if operative is not None else 'not_satisfied'))
    if operative is not None:
        status = 'presented'
        conclusion = '调候候选：首取 %s（%s，%s在盘），次取 %s。' % (
            operative['stem'], operative['ten_god'],
            '透干' if operative['presence'] == 'visible' else '藏干',
            '、'.join('%s（%s）' % (c['stem'], c['ten_god'])
                      for c in candidates[1:])
            or '无')
    else:
        status = 'not_judgeable'
        conclusion = None
    limitations = [
        '只陈述条目原文的取用顺序与盘面存在性事实，不作吉凶、强弱、格局或'
        '喜用结论；调候候选不等于确定用神。',
        '来源为 C 级单一电子谱系（简体转写），未做多底本校勘；季总论与分月'
        '条目先次不一致时并列登记，不暗中合并。',
        '未编码分支的条件（成局、相对旺盛、节气分界等）不在本体系输入契约内，'
        '只登记为缺口，不编码、不推断。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'condition': {
                'day_master': day_master, 'month_branch': month_branch,
                'month_label': tiaohou.get('month_label'),
                'quote': entry.get('quote'),
                'quote_locator': entry.get('quote_locator'),
                'order_basis': entry.get('order_basis')},
            'active_sequence': active_kind,
            'candidates': candidates,
            'operative_candidate': operative,
            'operative_status': operative_status,
            'gaps': gaps,
            'basis': {'tiaohou_variant': TIAOHOU_VARIANT,
                      'day_master': day_master,
                      'month_branch': month_branch,
                      'status': status_in},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['tiaohou_quote_single_lineage_c']}


def evaluate_bingyao_xiyong(bingyao, *, pillars=None):
    """病药取用：消费 bingyao_lookup 输出，逐对独立给药神候选。"""
    base = {'system': 'bingyao', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if bingyao is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'pairs': [], 'gaps': [], 'basis': None,
                'conditions': [_condition(
                    'bingyao_input', '未传入已审病药输出', 'not_satisfied')],
                'limitations': ['未传入病药输出，本体系不补病药判断。'],
                'uncertainty': ['bingyao_input_missing']}
    _check_statement(bingyao, BINGYAO_VARIANT, 'bingyao')
    day_master = bingyao.get('day_master')
    if type(day_master) is not str or day_master not in STEMS:
        _fail('bingyao statement day_master drifted')
    if bingyao.get('determination') is not None:
        _fail('bingyao statement carries an adjudicated determination')
    pairs_in = bingyao.get('pairs')
    if type(pairs_in) is not list or len(pairs_in) != 2:
        _fail('bingyao statement pairs malformed')
    pairs = []
    gaps = []
    for pair_in in pairs_in:
        rule = pair_in.get('rule') or {}
        pair_id = pair_in.get('pair_id')
        status = pair_in.get('status')
        if status not in ('triggered', 'not_triggered'):
            _fail('bingyao pair status drifted')
        disease = pair_in.get('disease_candidate')
        medicine = pair_in.get('medicine_candidate')
        medicine_status = pair_in.get('medicine_status')
        yongshen_candidate = None
        medicine_check = None
        if status == 'triggered' and medicine is not None:
            # 结构核对：药之五行克病之五行（十神类定义构造恒立，此处逐盘复核）。
            disease_element = medicine.get('disease_element')
            medicine_element = medicine.get('medicine_element')
            if disease_element is None or medicine_element is None:
                _fail('bingyao medicine candidate lacks elements')
            medicine_check = (CONTROLS[medicine_element] == disease_element)
            if not medicine_check:
                _fail('bingyao medicine does not control disease element')
            yongshen_candidate = [{
                'stem': god['stem'], 'pillar': god['pillar'],
                'ten_god': god['ten_god'],
                'element': stem_element(god['stem'])}
                for god in medicine.get('gods') or []]
        if status == 'triggered' and medicine is None:
            gaps.append({
                'gap_id': 'medicine_absent_in_chart',
                'pair_id': pair_id,
                'detail': '病已触发（%s），但药神类 %s 在显干中无在场之干；'
                          '药神候选只记类，不据缺位拟制具体干。'
                          % ((disease or {}).get('god_class'),
                             rule.get('medicine_god_class'))})
        if status == 'not_triggered':
            gaps.append({
                'gap_id': 'pair_not_triggered',
                'pair_id': pair_id,
                'detail': '该对未触发（%s）：本对不输出病药候选；'
                          '未触发不是「无病」，无病的成立要求整盘不旺不弱'
                          '且中和的裁定，本平台无此能力。'
                          % pair_in.get('not_triggered_reason')})
        pairs.append({
            'pair_id': pair_id,
            'rule_id': rule.get('id'),
            'quote': rule.get('quote'),
            'status': status,
            'subject_gods': list(rule.get('subject_gods') or []),
            'disease_gods': list(rule.get('disease_gods') or []),
            'medicine_gods': list(rule.get('medicine_gods') or []),
            'subject': pair_in.get('subject'),
            'disease_candidate': disease,
            'medicine_candidate': medicine,
            'medicine_status': medicine_status,
            'medicine_effect_status': pair_in.get('medicine_effect_status'),
            'medicine_check': medicine_check,
            'yongshen_candidate': yongshen_candidate,
            'determination': None})
    gaps.append({'gap_id': 'severity_threshold_undefined',
                 'detail': '定义节「从重者论」的「重」无阈值：本体系不选定'
                           '唯一病神，只陈述示例对的存在性命中。'})
    gaps.append({'gap_id': 'officer_strength_pattern_not_covered',
                 'detail': '正官格节「惟官星太弱太旺，方为有病」口径与定义节'
                           '口径并存未统一，本体系不覆盖太弱太旺型之病。'})
    triggered = [p for p in pairs if p['status'] == 'triggered']
    if triggered:
        status = 'presented'
        parts = []
        for pair in triggered:
            if pair['yongshen_candidate']:
                parts.append('%s对药神候选 %s' % (
                    pair['pair_id'],
                    '、'.join('%s（%s）' % (g['stem'], g['ten_god'])
                              for g in pair['yongshen_candidate'])))
            else:
                parts.append('%s对病已触发、药不在盘' % pair['pair_id'])
        conclusion = '病药候选：%s；药去病效力恒未裁定。' % '；'.join(parts)
    else:
        status = 'no_triggered_pair'
        conclusion = None
    conditions = [
        _condition('pair_triggered',
                   '触发的病药对：%s' % (
                       '、'.join(p['pair_id'] for p in triggered) or '无'),
                   'satisfied' if triggered else 'not_satisfied'),
        _condition('medicine_effect',
                   '药去病效力恒未裁定（药存在不等于病已去）',
                   'cannot_judge'),
    ]
    limitations = [
        '只编码定义节示例二、示例三两对；示例一（土重）前提无操作定义、'
        '四病四药或缺阈值判据或是行运之药，均不在本体系范围。',
        '存在性口径只计显干，不计藏干；药候选只陈述存在与药克病的结构关系，'
        '去病效力恒未裁定，不输出「药已去病」。',
        '本体系永不输出「无病」；未触发只记未触发。',
        '《滴天髓阐微》中和篇制衡：病药之论「仍乃失之偏」「总以中和为主」，'
        '病药说非通则，候选陈述须与此制衡同读。',
        '与调候、扶抑、格局用神并列，不合并为统一喜用结论。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'pairs': pairs, 'gaps': gaps,
            'basis': {'bingyao_variant': BINGYAO_VARIANT,
                      'day_master': day_master,
                      'triggered_pairs': [p['pair_id'] for p in triggered]},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['medicine_effect_unadjudicated',
                            'severity_threshold_undefined']}


def evaluate_pattern_xiyong(pattern, *, pillars=None, day_master=None):
    """格局用神：消费格局引擎 evaluate_all 输出，只对有资格的格列依据。

    有资格 = state 为 established，或 state 为 candidate 且 rule_ids
    含 validated 候选规则。任何格的 useful_god 恒为 None（密封树中
    全部格的用神未审），本函数只输出该确定结论与结构依据，不捏造用神。
    """
    base = {'system': 'pattern_yongshen', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if pattern is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'eligible': [], 'ineligible': [], 'counts': {},
                'gaps': [], 'basis': None,
                'conditions': [_condition(
                    'pattern_input', '未传入已审格局输出', 'not_satisfied')],
                'limitations': ['未传入格局输出，本体系不补格局判断。'],
                'uncertainty': ['pattern_input_missing']}
    # 格局引擎的治理旗标键为 public / ai（非 public_enabled / ai_enabled），
    # 故此处不用 _check_statement，逐项核对 variant 与四项旗标。
    if not isinstance(pattern, dict):
        _fail('pattern statement must be an object')
    if pattern.get('variant') != PATTERN_ENGINE_VARIANT:
        _fail('pattern statement variant drifted')
    if pattern.get('research_only') is not True:
        _fail('pattern statement research_only drifted')
    if pattern.get('public') is not False:
        _fail('pattern statement public drifted')
    if pattern.get('ai') is not False:
        _fail('pattern statement ai drifted')
    pattern_day = pattern.get('day_stem')
    month_branch = pattern.get('month_branch')
    if day_master is not None and day_master != pattern_day:
        _fail('pattern statement disagrees on the day master')
    _validate_day_month(pattern_day, month_branch)
    results = pattern.get('results')
    if not isinstance(results, dict) or not results:
        _fail('pattern statement results malformed')
    normalized = None
    if pillars is not None:
        normalized = _normalize_pillars(pillars, pattern_day)
    eligible = []
    ineligible = []
    gaps = []
    for key, result in sorted(results.items()):
        if not isinstance(result, dict):
            _fail('pattern result must be an object')
        state = result.get('state')
        if state not in ('candidate', 'established', 'broken', 'conflict',
                         'not_judgeable'):
            _fail('pattern result state drifted')
        if state == 'broken':
            _fail('pattern engine never emits broken; refusing input')
        rule_ids = result.get('rule_ids') or []
        god = PATTERN_TEN_GODS.get(key)
        visible_positions = []
        if god is not None and normalized is not None:
            for row in normalized:
                if row['name'] == 'day':
                    continue
                if row['stem_ten_god'] == god:
                    visible_positions.append({
                        'stem': row['stem'], 'pillar': row['name'],
                        'ten_god': god, 'element': row['stem_element']})
        is_eligible = (state == 'established'
                       or (state == 'candidate'
                           and bool(set(rule_ids)
                                    & VALIDATED_CANDIDATE_RULE_IDS)))
        record = {
            'pattern_key': key,
            'pattern': result.get('pattern'),
            'state': state,
            'rule_ids': list(rule_ids),
            'evidence_ids': [e.get('id') for e in
                             (result.get('evidence') or [])
                             if isinstance(e, dict)],
        }
        if is_eligible:
            record.update({
                'pattern_god': god,
                'visible_positions': visible_positions,
                'useful_god': None,
                'useful_god_status': 'no_reviewed_yongshen_rule',
                'reason': ('该格已成立或有 validated 候选规则，但密封树中'
                           '全部格的 useful_god 恒未审（破格/成败/清浊/'
                           '用神未审）：本体系不输出格局用神，只列结构依据。'),
            })
            eligible.append(record)
        else:
            if state == 'established':
                reason = '已成立但无格神可列（非十神格），不输出用神。'
            elif state == 'candidate':
                reason = ('仅月藏结构观察，无 validated 候选规则：'
                          '无资格输出格局用神。')
            elif state == 'conflict':
                reason = '流派冲突未裁定（官杀去留/杂气换算未审）：不输出用神。'
            else:
                reason = '无已审依据：不输出用神。'
            record.update({'reason': reason})
            ineligible.append(record)
    if not eligible:
        gaps.append({'gap_id': 'no_pattern_yields_yongshen',
                     'detail': '本盘无任何格可输出已审格局用神：有资格的格'
                               '亦因 useful_god 未审而无用神；无资格的格按'
                               '状态分别记原因。'})
    else:
        gaps.append({'gap_id': 'eligible_pattern_no_yongshen_rule',
                     'detail': '有资格的格（%s）均无已审用神规则：'
                               '格局用神的逐格规则待证据裁定与用户裁定后另行接入。'
                     % '、'.join(e['pattern'] for e in eligible)})
    if eligible:
        status = 'presented'
        conclusion = '格局用神：有资格的格 %s 均无已审用神规则，不输出用神；' \
            '结构依据见 eligible。' % '、'.join(
                e['pattern'] for e in eligible)
    else:
        status = 'no_eligible_pattern'
        conclusion = None
    conditions = [
        _condition('eligible_pattern_present',
                   '有资格的格：%s' % (
                       '、'.join(e['pattern'] for e in eligible) or '无'),
                   'satisfied' if eligible else 'not_satisfied'),
        _condition('yongshen_rule_reviewed',
                   '格局用神逐格规则已审', 'not_satisfied',
                   basis='密封树 useful_god 恒未审'),
    ]
    limitations = [
        '成立的唯一通道是任氏寅月真格；候选只认 validated 候选规则；'
        '观察级候选、冲突、未可判一律无资格。',
        '破格恒不输出：无逐格破格条件句。',
        '戊×巳 / 己×午土日主成格不可建（TJ-011.2），一律不作格局裁定。',
        '格神显干位置只是结构依据，不是用神结论；不得据格神反推用神。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'eligible': eligible, 'ineligible': ineligible,
            'counts': {'eligible': len(eligible),
                       'ineligible': len(ineligible),
                       'total': len(results)},
            'gaps': gaps,
            'basis': {'pattern_variant': PATTERN_ENGINE_VARIANT,
                      'day_stem': pattern_day,
                      'month_branch': month_branch},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['pattern_yongshen_rule_unreviewed']}


def _flow_year_ganzhi(target_year):
    if type(target_year) is not int or not 1900 <= target_year <= 2098:
        _fail('target_year must be an integer calendar year 1900..2098')
    ganzhi = CYCLE[(target_year - 4) % 60]
    return ganzhi


def evaluate_annual_xiyong(systems, target_year, *, day_master):
    """流年喜用：接入组合引擎契约已实现的 4 项，余 5 项保持 pending。

    ``systems`` 为四体系输出字典（键 fuyi / tiaohou / bingyao /
    pattern_yongshen，缺失的体系可为 None）。只报存在性对照与调用结构，
    不推演任何流年喜用。
    """
    if type(day_master) is not str or day_master not in STEMS:
        _fail('day_master must be one heavenly stem')
    if not isinstance(systems, dict):
        _fail('systems must be an object')
    flow_ganzhi = _flow_year_ganzhi(target_year)
    flow_stem = flow_ganzhi[0]
    flow_branch = flow_ganzhi[1]
    flow_ten_god = ten_god_for(day_master, flow_stem)

    tiaohou = systems.get('tiaohou')
    tiaohou_sequence = []
    if isinstance(tiaohou, dict):
        tiaohou_sequence = [c['stem'] for c in
                            (tiaohou.get('candidates') or [])]
    tiaohou_presence = (flow_stem in tiaohou_sequence
                        if tiaohou_sequence else None)
    if not isinstance(tiaohou, dict):
        tiaohou_note = '未传入原局调候输出，流年调候对照待原局调候传入后方可列举。'
    elif tiaohou.get('status') == 'not_judgeable':
        tiaohou_note = '原局调候无在场候选或条目未审定，流年调候对照无序列可比。'
    else:
        tiaohou_note = ('只报流年干是否在原局调候序列中这一存在性事实；'
                        '流年调候推演未获批，不据此取流年调候用神。')

    bingyao = systems.get('bingyao')
    pair_roles = []
    if isinstance(bingyao, dict):
        for pair in bingyao.get('pairs') or []:
            if flow_ten_god in (pair.get('subject_gods') or []):
                role = 'subject'
            elif flow_ten_god in (pair.get('disease_gods') or []):
                role = 'disease'
            elif flow_ten_god in (pair.get('medicine_gods') or []):
                role = 'medicine'
            else:
                role = 'none'
            pair_roles.append({
                'pair_id': pair.get('pair_id'), 'flow_stem_ten_god': flow_ten_god,
                'flow_ten_god_role_in_pair': role,
                'pair_status': pair.get('status'),
                'note': ('只报流年干十神在该病药对中的角色这一结构对照；'
                         '流年病药推演未获批，不据此断流年病药去留。')})

    fuyi = systems.get('fuyi')
    fuyi_candidates = []
    if isinstance(fuyi, dict) and isinstance(fuyi.get('modern'), dict):
        fuyi_candidates = [g['stem'] for g in
                           (fuyi['modern'].get('candidate_stems') or [])]
    fuyi_presence = (flow_stem in fuyi_candidates
                     if fuyi_candidates else None)

    pattern_sys = systems.get('pattern_yongshen')
    pattern_basis_stems = []
    if isinstance(pattern_sys, dict):
        for entry in pattern_sys.get('eligible') or []:
            pattern_basis_stems.extend(
                pos['stem'] for pos in entry.get('visible_positions') or [])
    pattern_presence = (flow_stem in pattern_basis_stems
                        if pattern_basis_stems else None)

    references = {
        'tiaohou': {
            'flow_stem': flow_stem,
            'flow_stem_in_natal_tiaohou_sequence': tiaohou_presence,
            'natal_tiaohou_sequence_stems': tiaohou_sequence,
            'note': tiaohou_note},
        'bingyao': {
            'pairs': pair_roles,
            'note': ('未传入原局病药输出，流年病药对照待原局病药传入后方可列举。'
                     if not isinstance(bingyao, dict) else
                     '只报角色对照，不推演流年病药。')},
        'fuyi': {
            'flow_stem': flow_stem,
            'flow_stem_in_natal_fuyi_modern_candidates': fuyi_presence,
            'natal_fuyi_modern_candidate_stems': fuyi_candidates,
            'note': ('只报流年干是否与原局扶抑现代候选干同字这一存在性事实；'
                     '流年扶抑推演未获批，不据此取流年扶抑用神。')},
        'pattern_yongshen': {
            'flow_stem': flow_stem,
            'flow_stem_in_pattern_basis': pattern_presence,
            'pattern_basis_stems': sorted(set(pattern_basis_stems)),
            'note': ('只报流年干是否与有资格格局的结构依据干同字这一存在性事实；'
                     '流年格局用神推演未获批，不据此取流年格局用神。')},
    }
    call_structure = {
        system: (systems.get(system) or {}).get('status')
                if isinstance(systems.get(system), dict) else 'not_provided'
        for system in ('fuyi', 'tiaohou', 'bingyao', 'pattern_yongshen')
    }
    return {
        'variant': ANNUAL_CONTRACT_VARIANT,
        'status': 'contract_only_pending_rules',
        'implemented': list(ANNUAL_IMPLEMENTED),
        'pending': list(ANNUAL_PENDING),
        'pending_reason': ('流年喜用完整推演待对应规则获批后接入；现阶段只列'
                           '数据契约与调用结构，不推演任何流年喜用。'),
        'flow_year': {
            'target_year': target_year, 'ganzhi': flow_ganzhi,
            'stem': flow_stem, 'branch': flow_branch,
            'stem_ten_god': flow_ten_god,
            'derivation': 'sexagenary_cycle_index',
            'derivation_note': ('年干支按六十甲子表 CYCLE[(year-4)%60] 推导；'
                                '立春交界与年内分界不在此推导范围。')},
        'flow_references': references,
        'rule_call_structure': call_structure,
        'derivation': None,
        'unified_verdict': None,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
    }


def evaluate_xiyong(*, day_master, month_branch, pillars=None, strength=None,
                    tiaohou=None, bingyao=None, pattern=None, flow_year=None):
    """四体系喜用神并列计算（组合任务消费的入口）。

    ``strength`` / ``tiaohou`` / ``bingyao`` / ``pattern`` 分别为
    ``assess_strength`` / ``tiaohou_lookup`` / ``bingyao_lookup`` /
    ``evaluate_all`` 的输出字典（缺省为 None，即该体系未传入）。
    ``pillars`` 为四柱（可选；用于现代扶抑候选干与格局结构依据的显干核对）。
    ``flow_year`` 为公历目标年份（可选；传入时计算流年喜用契约）。
    返回 dict：``systems``（四体系）、``annual_xiyong``、
    ``unified_verdict``（恒 None，TJ-013.2 裁决 A）。
    """
    _validate_day_month(day_master, month_branch)
    normalized = None
    if pillars is not None:
        normalized = _normalize_pillars(pillars, day_master)
        if normalized[1]['branch'] != month_branch:
            _fail('month_branch disagrees with the month pillar branch')
    systems = {
        'fuyi': evaluate_fuyi(strength, pillars=pillars),
        'tiaohou': evaluate_tiaohou_xiyong(tiaohou, pillars=pillars),
        'bingyao': evaluate_bingyao_xiyong(bingyao, pillars=pillars),
        'pattern_yongshen': evaluate_pattern_xiyong(
            pattern, pillars=pillars, day_master=day_master),
    }
    # 输入一致性：各体系的日主/月支须与顶层一致，否则 fail-closed。
    for key, statement in (('strength', strength), ('tiaohou', tiaohou),
                           ('bingyao', bingyao)):
        if statement is None:
            continue
        stmt_day = statement.get('day_master')
        if stmt_day != day_master:
            _fail('%s statement disagrees on the day master' % key)
        if key in ('strength', 'tiaohou') \
                and statement.get('month_branch') != month_branch:
            _fail('%s statement disagrees on the month branch' % key)
    annual = (evaluate_annual_xiyong(systems, flow_year, day_master=day_master)
              if flow_year is not None else None)
    return {
        'variant': XIYONG_ENGINE_VARIANT,
        'day_master': day_master,
        'month_branch': month_branch,
        'pillars': [row['ganzhi'] for row in normalized]
                   if normalized is not None else None,
        'systems': systems,
        'annual_xiyong': annual,
        'unified_verdict': None,
        'unified_verdict_status': 'abstain_by_adjudication_TJ-013.2-A',
        'unified_verdict_note': ('TJ-013.2 裁决 A：四体系并列呈现、统一裁决拒判；'
                                 '本引擎永不输出统一喜用神。'),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(GLOBAL_LIMITATIONS),
    }
