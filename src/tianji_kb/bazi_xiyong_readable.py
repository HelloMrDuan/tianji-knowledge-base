"""喜用结果用户可读提示（TJ-013.3 第一阶段）：确定性渲染，不新增判断。

WBS 定义核对（先行审计结论）：TJ-013.3 的工作包是「适用范围明确的
用户可读提示」，边界注记为「前端只有真实经过 Phase2/Golden 的条件
才出现解释」。本阶段是该任务的研究级底座：把已裁定体系的结构化输
出渲染为确定性中文文本，恒 research_only、公开投影整体剥离、AI 关
闭状态不变——前端不出现任何新解释；被渲染的四个对象（调候、病药
双对、旺衰裁定、TJ-013.2 冲突呈现）均已有 Golden 覆盖，未建体系
（扶抑、格局用神）只渲染缺席事实、绝不生成解释。TJ-013.3 在台账上
保持阻塞（公开呈现与跨体系裁决前置未清），本阶段不构成公开可用。

既有渲染资产审计（为何不复用）：
- explanation.ExplanationService 是 LLM 解释通道（凭据/引用校验/
  Prompt 版本治理对象），研究结果在其入口即以 ai_may_explain=False
  被拒；本层明令不调用任何模型，与该通道是两种机制，不复用、不
  绕过，其关闭状态不变。
- bazi_strength_display（TJ-011.3）是公开边界的显示策略（服务端
  allowlist 门控加短拒绝文案），职责是压制研究结论不外泄，方向与
  研究级全文渲染相反，不适用作渲染器；其诚实文案口径（暂不可判
  断）与本层一致。
- scenario_engine 的 TJ-007.1 四层结果页运行在 production 公开数
  据上，研究陈述在投影边界已被剥离、永不到达该层，不适用。
- 本层直接消费冲突呈现对象内携带的 status_definition 与体系级状
  态（单一口径来源），不另造一套状态文案。

渲染契约（硬边界）：
- 纯函数，输入为同一命盘一次执行产出的四个对象：tiaohou_assessment、
  bingyao_assessment（含 pairs）、strength_assessment 与
  conflict_presentation。伪造、混盘（呈现层所携陈述与传入陈述不一
  致）、非研究标志、未知状态/谓词/条件键/关系类型一律 fail-closed
  （ValueError），绝不临场拼造文案。
- 每条 line 由模板从结构化事实字段确定性拼装；静态模板文字不含任
  何干名，line 中出现的干名只能来自输入事实（干名集合封闭性由专
  项测试钉住）。同输入两次输出逐字相同（确定性测试钉住）。
- 诚实口径：已裁定陈述直述结构事实；弃判渲染为未表态加原因的自然
  语言转写；absent 渲染为「尚未建成，暂不可判断」；病药触发段恒附
  效力未裁定明示；冲突段直述关系并明示不作统一裁定。全文禁用断言
  式吉凶与现实预测词汇（专项全域扫描钉住：吉/凶/宜/忌/灾/祸/发财/
  升职/喜用神/宜用/推荐/评分等子串零出现）；不引用古籍原文（引文
  留在结构化陈述内供复核，生成文本从严不带引文）。
- 013.2 已披露的限制在本层如实保留：关系分类只消费病药第一对的角
  色点名；第二对在病药段逐对陈述，但不单独做关系分类——冲突段以
  口径行明示，不渲染任何第二对的关系结论。
- 本层不新增 trace rule，不进 RuleMatch 与 Evidence，不改变所携
  陈述的 evidence_binding 状态。
"""
import copy

from .bazi_adjudication import ADJUDICATION_VARIANT
from .bazi_bingyao import VARIANT as BINGYAO_VARIANT
from .bazi_conflict_presentation import (
    ABSENT_REASONS, STATUS_DEFINITIONS,
    VARIANT as CONFLICT_VARIANT)
from .bazi_tiaohou import VARIANT as TIAOHOU_VARIANT
from .foundations import stem_element

VARIANT = 'xiyong-readable-hints-v1'

SYSTEM_TIAOHOU = 'tiaohou'
SYSTEM_BINGYAO = 'bingyao'
SYSTEM_STRENGTH = 'strength'
SYSTEM_FUYI = 'fuyi'
SYSTEM_PATTERN = 'pattern_useful_god'
SYSTEM_CONFLICT = 'conflict_presentation'

PILLAR_LABELS = {'year': '年柱', 'month': '月柱', 'day': '日柱',
                 'hour': '时柱'}
PAIR_ORDINALS = ('第一对', '第二对')
PAIR_IDS = ('wealth_peer_officer', 'foodwound_seal_wealth')
SUBJECT_MISSING_REASONS = frozenset((
    'subject_wealth_not_visible', 'subject_foodwound_not_visible'))
DISEASE_MISSING_REASONS = frozenset((
    'peer_god_not_visible', 'seal_god_not_visible'))

PREDICATE_LABELS = {
    'pure_support': '纯生扶',
    'pure_generating_support': '生扶从旺',
    'isolated_control': '孤立受克',
}

# 裁定出口有两种形态（见 bazi_adjudication）：pure_support 与
# isolated_control 经已注册的 trace rule 发出，why 只带
# sufficient_rule；pure_generating_support 尚待 Phase1 注册，经有限
# 出口发出，why 带 sufficient_predicate 且 sufficient_rule 为 None。
# 渲染器按此映射派生谓词，两形态并存且不一致时 fail-closed。
RULE_TO_PREDICATE = {
    'bazi.phase2.strength_pure_support': 'pure_support',
    'bazi.phase2.strength_isolated_control': 'isolated_control',
}

# 已审充分谓词条件键的自然语言转写（一一对应 bazi_action_conditions
# 三组 scope 条件字典的键；未知键 fail-closed，不临场造词）。
CONDITION_LABELS = {
    'wood_day_master': '日主为木',
    'reviewed_same_element_month': '月支本气与日主同行',
    'reviewed_generating_month': '月支本气生扶日主',
    'reviewed_control_month': '月支本气克制日主',
    'all_positions_support_only': '全部位置的作用均为生扶',
    'no_support_in_any_position': '全部位置均无生扶作用',
    'visible印_present': '显干见印',
    'visible比_present': '显干见比劫',
    'effective_day_roots': '日主根均为有效',
    'day_has_no_structural_root': '日主无结构性根',
    'all_visible_have_reviewed_roots': '显干各有已审根位',
    'visible_earth_metal_only': '显干五行仅为土与金',
    'month_principal_exposed_with_root': '月支本气透于月干且有已审根位',
    'no_unresolved_interactions': '无未决的作用关系',
}

CLASSIFICATION_LABELS = {'strong': '强', 'weak': '弱',
                         'indeterminate': '未裁定'}
PRESENTATION_STATUS_LABELS = {
    'presented_with_conflicts': '存在冲突',
    'presented_partial': '部分呈现',
    'presented_no_conflict': '无冲突',
}
RELATION_LABELS = {
    'support': '相互支持',
    'conflict': '相互冲突',
    'pivot_overlap': '主体重合',
    'one_sided': '单方点名',
}
BINGYAO_ROLE_TEXTS = {
    'subject': '为病药所论之主体',
    'disease': '为病药原文判为病之神',
    'medicine': '为病药原文判为药之神',
}
_ROLE_TO_KIND = {'medicine': 'support', 'disease': 'conflict',
                 'subject': 'pivot_overlap'}

BINGYAO_HEADER = '病药体系（《神峰通考》）：按原文两组病药对逐对陈述，两对不合并为单一结论。'
EFFICACY_LINE = '只陈述原文病药对的结构候选：药是否能去病，古籍病药说本身未给出可执行裁定，本系统不作判断。'
STRENGTH_ABSTAIN_LINE = '旺衰裁定体系在本盘未表态：已审充分谓词均未命中，旺衰未裁定；未裁定不表示中和，也不表示偏强或偏弱。'
STRENGTH_SCOPE_LINE = '该裁定只在上述已审充分条件的范围内成立，强弱是结构裁定，不延伸为对现实的判断。'
ABSENT_LINES = {
    SYSTEM_FUYI: '扶抑体系尚未建成，暂不可判断。',
    SYSTEM_PATTERN: '格局用神体系尚未建成，暂不可判断。',
}
RELATION_SCOPE_LINE = '关系分类的口径：本阶段只使用病药第一对（财—比劫—官杀）的角色点名；病药第二对（食伤—印—财）已在病药段逐对陈述，本阶段不单独做关系分类。'
NO_UNIFIED_VERDICT_LINE = '各体系陈述并列呈现，系统不作统一裁定。'

LIMITATIONS = (
    '本提示由确定性模板从已裁定的结构化陈述拼装，不调用任何模型、不新增任何判断；每条文本均可回溯到输入陈述的事实字段。',
    '本提示只存在于研究模式：不进入公开投影，不供 AI 解释使用；公开呈现须待各体系完成公开审核后另行接入。',
    '调候只渲染条目主序列；条目的条件分支序列、未编码分支与关联条目随结构化陈述携带，本阶段不展开渲染。',
    '病药两对均为结构候选：触发只陈述原文病药对的存在性命中，去病效力未裁定；未触发不等于无病，本提示不存在「无病」断言。',
    '关系分类只消费病药第一对的角色点名，第二对不单独分类（与 TJ-013.2 呈现层已披露的限制一致）；各体系陈述并列呈现，本层不作统一裁定。',
    '旺衰裁定只覆盖已审充分谓词命中的命盘；未命中即未表态，未裁定不表示中和。扶抑、格局用神两体系尚未建成，其段落只报告缺席事实。',
)


def _require_statement(name, statement, *, variant, system=None):
    if not isinstance(statement, dict):
        raise ValueError(f'Readable hints require the {name} statement object')
    if statement.get('variant') != variant:
        raise ValueError(f'Readable hints require the reviewed {name} variant')
    if system is not None and statement.get('system') != system:
        raise ValueError(f'Readable hints require the {name} system statement')
    if statement.get('research_only') is not True \
            or statement.get('public_enabled') is not False \
            or statement.get('ai_enabled') is not False:
        raise ValueError(f'Readable hints require research-only {name} statements')


def _gods_text(gods):
    if not isinstance(gods, list) or not gods:
        raise ValueError('Readable hints require non-empty god rows')
    parts = []
    for god in gods:
        if not isinstance(god, dict) or god.get('pillar') not in PILLAR_LABELS \
                or not isinstance(god.get('stem'), str) \
                or not isinstance(god.get('ten_god'), str):
            raise ValueError('Readable hints require pillar/stem/ten_god god rows')
        parts.append(f"{PILLAR_LABELS[god['pillar']]}干{god['stem']}（{god['ten_god']}）")
    return '、'.join(parts)


def _tiaohou_lines(statement):
    day_master = statement['day_master']
    label = f"{day_master}{stem_element(day_master)}"
    status = statement.get('status')
    if status == 'not_applicable':
        if statement.get('reason') != 'entry_absent_in_source':
            raise ValueError('Unsupported tiaohou abstention reason for readable hints')
        month_branch = statement['month_branch']
        return [f'调候体系（《穷通宝鉴》）：本盘日主{label}、月支{month_branch}，'
                '该组合的分月条目在审定《穷通宝鉴》文本中不存在，'
                '该体系在本盘不作陈述。']
    if status != 'matched':
        raise ValueError('Unsupported tiaohou statement status for readable hints')
    month_label = statement.get('month_label')
    if not isinstance(month_label, str) or not month_label:
        raise ValueError('Readable hints require the tiaohou month label')
    items = []
    for item in statement.get('sequence') or []:
        presence = item.get('presence')
        if presence == 'visible':
            positions = item.get('visible_positions') or []
            if not positions or any(p not in PILLAR_LABELS for p in positions):
                raise ValueError('Readable hints require visible pillar positions')
            where = '透于' + '、'.join(PILLAR_LABELS[p] for p in positions)
        elif presence == 'hidden':
            raw = item.get('hidden_positions') or []
            pillars = []
            for entry in raw:
                pillar = str(entry).split(':')[0]
                if pillar not in PILLAR_LABELS:
                    raise ValueError('Readable hints require hidden pillar positions')
                if pillar not in pillars:
                    pillars.append(pillar)
            if not pillars:
                raise ValueError('Readable hints require hidden pillar positions')
            where = '仅藏于' + '、'.join(PILLAR_LABELS[p] for p in pillars)
        elif presence == 'absent':
            where = '盘中未见'
        else:
            raise ValueError('Unsupported tiaohou presence for readable hints')
        items.append(f"{item['stem']}（第{item['order']}取，{where}）")
    if not items:
        raise ValueError('Readable hints require a non-empty tiaohou sequence')
    return [f'调候体系（《穷通宝鉴》{label}{month_label}条）：'
            f"原文取用顺序为：{'、'.join(items)}。"]


def _pair_lines(pair, ordinal):
    rule = pair.get('rule') or {}
    subject_class = rule.get('subject_god_class')
    disease_class = rule.get('disease_god_class')
    medicine_class = rule.get('medicine_god_class')
    if not all(isinstance(x, str) and x
               for x in (subject_class, disease_class, medicine_class)):
        raise ValueError('Readable hints require the bingyao pair rule classes')
    head = (f'{ordinal}（所论之神{subject_class}、病为{disease_class}、'
            f'药为{medicine_class}）')
    if pair.get('determination') is not None \
            or pair.get('medicine_effect_status') != 'unadjudicated':
        raise ValueError('Bingyao pairs never carry a determination or adjudicated effect')
    status = pair.get('status')
    subject_gods = (pair.get('subject') or {}).get('gods')
    if status == 'not_triggered':
        reason = pair.get('not_triggered_reason')
        if reason in SUBJECT_MISSING_REASONS:
            if subject_gods:
                raise ValueError('Bingyao pair contradicts its abstention reason')
            return [f'{head}：所论之神{subject_class}在本盘显干中未见，'
                    '该对未触发；未触发不等于无病。']
        if reason in DISEASE_MISSING_REASONS:
            return [f'{head}：所论之神{subject_class}见于{_gods_text(subject_gods)}，'
                    f'但病之{disease_class}在本盘显干中未见，'
                    '该对未触发；未触发不等于无病。']
        raise ValueError('Unsupported bingyao abstention reason for readable hints')
    if status != 'triggered':
        raise ValueError('Unsupported bingyao pair status for readable hints')
    disease = pair.get('disease_candidate') or {}
    medicine_status = pair.get('medicine_status')
    if medicine_status == 'candidate_present':
        medicine = pair.get('medicine_candidate') or {}
        medicine_part = f'{medicine_class}见于{_gods_text(medicine.get("gods"))}'
    elif medicine_status == 'absent':
        if pair.get('medicine_candidate') is not None:
            raise ValueError('Bingyao pair contradicts its medicine status')
        medicine_part = f'{medicine_class}在本盘显干中未见'
    else:
        raise ValueError('Unsupported bingyao medicine status for readable hints')
    main = (f'{head}：{subject_class}见于{_gods_text(subject_gods)}；'
            f'{disease_class}见于{_gods_text(disease.get("gods"))}；'
            f'{medicine_part}。')
    return [main, f'{ordinal}{EFFICACY_LINE}']


def _bingyao_lines(statement):
    pairs = statement.get('pairs')
    if not isinstance(pairs, list) or len(pairs) != len(PAIR_IDS) \
            or [p.get('pair_id') for p in pairs] != list(PAIR_IDS):
        raise ValueError('Readable hints require both reviewed bingyao pairs in order')
    lines = [BINGYAO_HEADER]
    for pair, ordinal in zip(pairs, PAIR_ORDINALS):
        lines.extend(_pair_lines(pair, ordinal))
    return lines


def _strength_lines(statement):
    classification = statement.get('classification')
    if classification == 'indeterminate':
        if statement.get('decision_status') != 'insufficient_reviewed_rules':
            raise ValueError('Unsupported strength abstention for readable hints')
        return [STRENGTH_ABSTAIN_LINE]
    if classification not in ('strong', 'weak'):
        raise ValueError('Unsupported strength classification for readable hints')
    if statement.get('decision_status') != 'reviewed_sufficient_rule_matched':
        raise ValueError('Strength verdict without a matched reviewed rule')
    why = statement.get('why_not_indeterminate')
    if not isinstance(why, dict):
        raise ValueError('Strength verdict requires its predicate record')
    rule_predicate = RULE_TO_PREDICATE.get(why.get('sufficient_rule')) \
        if why.get('sufficient_rule') else None
    predicate = why.get('sufficient_predicate')
    if predicate is not None and rule_predicate is not None \
            and predicate != rule_predicate:
        raise ValueError('Strength verdict predicate contradicts its sufficient rule')
    if predicate is None:
        predicate = rule_predicate
    if predicate not in PREDICATE_LABELS:
        raise ValueError('Unsupported strength sufficient predicate for readable hints')
    conditions = why.get('conditions')
    if not isinstance(conditions, list) or not conditions:
        raise ValueError('Strength verdict requires its verified conditions')
    labels = []
    for row in conditions:
        key = row.get('condition') if isinstance(row, dict) else None
        if key not in CONDITION_LABELS or row.get('met') is not True:
            raise ValueError('Strength verdict conditions must be known and met')
        labels.append(CONDITION_LABELS[key])
    return [
        f"旺衰裁定体系：本盘日主旺衰裁定为「{CLASSIFICATION_LABELS[classification]}」。",
        f"裁定命中的已审充分谓词为「{PREDICATE_LABELS[predicate]}」，"
        f"其条件全部成立：{'、'.join(labels)}。",
        STRENGTH_SCOPE_LINE,
    ]


def _relation_lines(presentation):
    status = presentation.get('status')
    if status not in PRESENTATION_STATUS_LABELS \
            or presentation.get('status_definition') != STATUS_DEFINITIONS[status]:
        raise ValueError('Unsupported presentation status for readable hints')
    lines = [f"跨体系关系呈现状态：{PRESENTATION_STATUS_LABELS[status]}。"
             f"{presentation['status_definition']}"]
    for relation in presentation.get('relations') or []:
        kind = relation.get('kind')
        if kind == 'incomparable':
            classification = relation.get('classification')
            if classification not in CLASSIFICATION_LABELS \
                    or relation.get('stem') is not None:
                raise ValueError('Unsupported incomparable record for readable hints')
            lines.append(
                f"旺衰结论为「{CLASSIFICATION_LABELS[classification]}」的分类"
                '而非干值点名，与调候、病药两体系不可比，只作上下文呈现。')
            continue
        if kind not in RELATION_LABELS:
            raise ValueError('Unsupported relation kind for readable hints')
        stem = relation.get('stem')
        if not isinstance(stem, str) or not stem:
            raise ValueError('Relation records require a stem')
        t_side = relation.get('tiaohou')
        b_side = relation.get('bingyao')
        if t_side is not None:
            if t_side.get('role') != 'primary_pick' \
                    or not isinstance(t_side.get('order'), int):
                raise ValueError('Unsupported tiaohou relation side')
            t_text = f"为取用序列第{t_side['order']}位"
        else:
            t_text = '未点名'
        if b_side is not None:
            role = b_side.get('role')
            if role not in BINGYAO_ROLE_TEXTS:
                raise ValueError('Unsupported bingyao relation side')
            b_text = BINGYAO_ROLE_TEXTS[role]
        else:
            role = None
            b_text = '未点名'
        if t_side is not None and b_side is not None:
            expected = _ROLE_TO_KIND[role]
        elif t_side is None and b_side is None:
            raise ValueError('Relation record names no system')
        else:
            expected = 'one_sided'
        if kind != expected:
            raise ValueError('Relation kind contradicts its sides')
        lines.append(f'干{stem}：{RELATION_LABELS[kind]}。'
                     f'调候一侧：{t_text}；病药一侧：{b_text}。')
    lines.append(RELATION_SCOPE_LINE)
    lines.append(NO_UNIFIED_VERDICT_LINE)
    return lines


def readable_hints(tiaohou, bingyao, strength, presentation, *,
                   readable_variant=VARIANT):
    """Render the four research statements of one chart as readable hints.

    Pure deterministic template rendering over the executed statements
    and their conflict presentation. Every line is assembled from fact
    fields of the inputs; static template text names no stem. Forged,
    mixed-chart or non-research inputs, and any fact the templates do
    not know how to transcribe, fail closed (ValueError). Inputs are
    never mutated. Nothing here adds a judgement: abstentions stay
    abstentions, absent systems stay absent, and cross-system relations
    are presented without any unified verdict.
    """
    if readable_variant != VARIANT:
        raise ValueError('Unsupported readable hints variant')
    _require_statement('tiaohou', tiaohou, variant=TIAOHOU_VARIANT,
                       system=SYSTEM_TIAOHOU)
    _require_statement('bingyao', bingyao, variant=BINGYAO_VARIANT,
                       system=SYSTEM_BINGYAO)
    _require_statement('strength', strength, variant=ADJUDICATION_VARIANT)
    _require_statement('conflict presentation', presentation,
                       variant=CONFLICT_VARIANT)
    if presentation.get('determination') is not None:
        raise ValueError('Conflict presentation never carries a determination')
    if bingyao.get('determination') is not None:
        raise ValueError('Bingyao statements never carry a determination')
    if tiaohou.get('day_master') != bingyao.get('day_master') \
            or presentation.get('day_master') != tiaohou.get('day_master'):
        raise ValueError('Readable hints require statements of one chart')
    records = {r['system']: r for r in presentation.get('systems') or []}
    if set(records) != {SYSTEM_TIAOHOU, SYSTEM_BINGYAO, SYSTEM_STRENGTH,
                        SYSTEM_FUYI, SYSTEM_PATTERN}:
        raise ValueError('Readable hints require the five presentation records')
    for system, statement in ((SYSTEM_TIAOHOU, tiaohou),
                              (SYSTEM_BINGYAO, bingyao),
                              (SYSTEM_STRENGTH, strength)):
        if records[system].get('statement') != statement:
            raise ValueError('Readable hints require the presented statements themselves')
    for system in (SYSTEM_FUYI, SYSTEM_PATTERN):
        record = records[system]
        if record.get('status') != 'absent' \
                or record.get('statement') is not None \
                or record.get('absent_reason') != ABSENT_REASONS[system]:
            raise ValueError('Unbuilt systems must be presented as absent')
    sections = [
        {'system': SYSTEM_TIAOHOU, 'status': records[SYSTEM_TIAOHOU]['status'],
         'lines': _tiaohou_lines(tiaohou)},
        {'system': SYSTEM_BINGYAO, 'status': records[SYSTEM_BINGYAO]['status'],
         'lines': _bingyao_lines(bingyao)},
        {'system': SYSTEM_STRENGTH, 'status': records[SYSTEM_STRENGTH]['status'],
         'lines': _strength_lines(strength)},
        {'system': SYSTEM_FUYI, 'status': 'absent',
         'lines': [ABSENT_LINES[SYSTEM_FUYI]]},
        {'system': SYSTEM_PATTERN, 'status': 'absent',
         'lines': [ABSENT_LINES[SYSTEM_PATTERN]]},
        {'system': SYSTEM_CONFLICT, 'status': presentation['status'],
         'lines': _relation_lines(presentation)},
    ]
    return {
        'variant': VARIANT, 'layer': 'readable_hints',
        'day_master': tiaohou.get('day_master'),
        'month_branch': presentation.get('month_branch'),
        'sections': sections,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(LIMITATIONS),
    }
