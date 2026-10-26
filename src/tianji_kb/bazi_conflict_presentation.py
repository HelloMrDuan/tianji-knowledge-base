"""跨体系冲突呈现层（TJ-013.2 第一阶段）：只呈现，不裁决。

WBS 定义核对（先行审计结论）：TJ-013.2 的工作包是「喜用与旺衰/格局
冲突决策」，边界注记为「证据缺口必须阻断公开结果及 AI，不根据弱/强
自动猜」。本层是该任务的第一阶段——把各体系对同一命盘的陈述并列呈
现并显式标出一致/冲突/不可比/弃判，为后续裁决规则提供基底；本层不
给出任何裁决，TJ-013.2 在台账上保持阻塞（裁决规则未建）。这与边界
注记一致：证据缺口（含裁决规则缺位）下，公开与 AI 一律阻断，本层恒
research_only。

消费的三体系（只调用、不改写，各自陈述对象逐字携带）：
- 调候 tiaohou_assessment（tiaohou-qiongtong-v1）：条目取用序列
  （干、次序、存在性）与条目定位。status=matched 为已陈述；
  status=not_applicable（仅乙×丑，条目在审定快照中不存在）为不适用。
- 病药 bingyao_assessment（bingyao-shenfeng-v1）：status=triggered
  时给出主体（财）/病（比劫）/药（官杀）的显干神干行；
  status=not_triggered 为弃判（带 not_triggered_reason）。未触发时
  输出中的 subject 行只是弃判的诊断上下文（财显而比劫不显之类），
  该体系并未点名任何干——弃判体系不产生关系记录（见下）。该
  assessment 自病药第二对切片起另以 pairs 逐对携带两对（财对、食
  伤对）的独立陈述；本层只消费其顶层（第一对）字段，第二对陈述随
  陈述对象逐字携带、本阶段不单独分类。
- 旺衰 strength_assessment（bazi-strength-adjudication-v1）：输出是
  强弱分类而非干值点名，与干值型体系没有共同可比面，恒以一条
  incomparable 记录作上下文携带，不参与一致/冲突判定。分类为
  strong/weak 为已裁定；indeterminate 为弃判（已审充分谓词均不
  满足或被 blocker 阻断，decision_status 恒
  insufficient_reviewed_rules）。

未建体系（位置如实标 absent，statement 为 None，绝不留空冒充已
评估）：扶抑（TJ-013.1 未完成，尚无已审 Source/Variant）、格局用神
（格局候选 TJ-012 只给候选位置、determination 恒未裁定，不是已审
的用神体系）。

关系分类（本层唯一新增语义，纯结构比较，零新教义）。可比面 = 各
体系在其陈述中点名的干及其角色：
- 调候角色 primary_pick：条目原文取用序列中的干（主序列；条件分支
  序列是同一条目的条件性重述，只随陈述对象逐字携带，本阶段不单独
  分类）。
- 病药角色（仅 triggered 时成立）：subject（所论之神，本对为财）、
  disease（原句判为病之神类）、medicine（原句判为药之神类，「喜见
  官杀为药」的药）。
逐干分类：
- support：同一干被调候取用、且是病药之药。两体系在各自角色语义内
  都把该干的出现作正向陈述（调候「取/用」之干、病药「喜见」之
  药），方向一致。
- conflict：同一干被调候取用、且是病药之病。调候以该干为取用，病
  药以该干所属神类为「所害之神」（病），角色方向相反。此为角色语
  义的结构对立，不是吉凶判断，本层不消解、不投票、不加权。
- pivot_overlap：同一干是病药所论之主体、且被调候取用。病药对主
  体本身不作正负陈述（病在害主体之神、药在去病之神），故既非一致
  亦非冲突，仅登记重合。
- one_sided：该干只被一个已陈述体系点名。
- incomparable：旺衰专用（见上），stem 为 None。
每条关系记录携带双方证据引用（Variant ID + 条目/规则定位）。

弃判传播规则：任一体系弃判或不适用，只影响该体系自身的状态与顶
层呈现状态，不降级、不删除其他体系的陈述；弃判体系不产生任何关
系记录，其部分事实只保留在逐字携带的陈述对象内。

顶层呈现状态（单值，逐一定义）：
- presented_with_conflicts：至少一条 conflict 关系存在。
- presented_partial：无 conflict，且已建三体系中至少一个为弃判或
  不适用。
- presented_no_conflict：无 conflict，且已建三体系均已陈述。
absent 体系不参与顶层状态计算（任何命盘上它们都缺席，计入会使状
态恒为 partial 而失去区分度），但在 systems 列表中恒显式在列。

硬禁止：输出不含任何统一喜用/推荐/评分/权重字段；determination
恒 None；不存在跨体系裁决字段。本层不新增 trace rule，不进
RuleMatch 与 Evidence（所携三体系自身的 evidence_binding 状态各自
保留在其陈述对象内，本层不改变其绑定状态）。

覆盖事实（如实记录，非教义断言）：截至本批，已审旺衰三谓词均要求
显干全生扶（强）或月干官杀孤立无根无扶（弱）；病药触发要求财干与
比劫干同显——财干属耗、比劫属扶助之外的点名一旦出现即破坏强谓词
的「全生扶」，比劫显干亦破坏弱谓词的孤立条件。故在当前覆盖下，
病药 triggered 之盘旺衰恒弃判，presented_no_conflict 且三体系均已
陈述的组合在真实盘上当前不可达（该顶层状态的分类逻辑由公开专项
以合成陈述输入单测钉住，并在测试中明示其为分类器逻辑测试、非命
盘结论）。
"""
import copy

from .bazi_adjudication import ADJUDICATION_VARIANT
from .bazi_bingyao import VARIANT as BINGYAO_VARIANT
from .bazi_tiaohou import VARIANT as TIAOHOU_VARIANT

VARIANT = 'xiyong-conflict-presentation-v1'

SYSTEM_TIAOHOU = 'tiaohou'
SYSTEM_BINGYAO = 'bingyao'
SYSTEM_STRENGTH = 'strength'
SYSTEM_FUYI = 'fuyi'
SYSTEM_PATTERN = 'pattern_useful_god'
BUILT_SYSTEMS = (SYSTEM_TIAOHOU, SYSTEM_BINGYAO, SYSTEM_STRENGTH)

RELATION_DEFINITIONS = {
    'support': '同一干被调候取用、且为病药之药：两体系在各自角色语义内同向点名（调候之取用、病药「喜见」之药）。',
    'conflict': '同一干被调候取用、且为病药之病：调候以之为取用，病药以其神类为所害之神（病），角色方向相反；本层不消解。',
    'pivot_overlap': '同一干为病药所论之主体、且被调候取用：病药对主体本身不作正负陈述，仅登记重合，不判一致或冲突。',
    'one_sided': '该干只被一个已陈述体系点名，另一干值体系未点名。',
    'incomparable': '旺衰输出为强弱分类而非干值点名，与干值型体系无共同可比面；仅作上下文携带，不参与一致/冲突判定。',
}

STATUS_DEFINITIONS = {
    'presented_with_conflicts': '至少一条 conflict 关系存在，冲突原样呈现、无裁决。',
    'presented_partial': '无 conflict；已建三体系中至少一个弃判或不适用，其余陈述照常呈现。',
    'presented_no_conflict': '无 conflict；已建三体系均已陈述。',
}

ABSENT_REASONS = {
    SYSTEM_FUYI: '扶抑体系尚无已审 Source/Variant（TJ-013.1 未完成），本层不评估、不以空白冒充已评估。',
    SYSTEM_PATTERN: '格局用神尚无已审 Variant：格局候选（TJ-012）只给候选位置、determination 恒未裁定，不得冒充用神体系已经评估。',
}

LIMITATIONS = (
    '本层只呈现不裁决：不存在已审的跨体系裁决规则，冲突按总指令口径原样返回，不消解、不投票、不加权；determination 恒为 None。',
    '可比面仅限干值点名：调候条目取用主序列与病药触发后的主体/病/药神干；调候条件分支序列只随陈述对象携带，本阶段不单独分类。',
    '弃判或不适用的体系不产生关系记录：其部分事实（如病药未触发时已显的主体财）只保留在陈述对象内，不构成该体系的点名。',
    '病药切片两对（财—比劫—官杀、食伤—印—财）均为结构候选、去病效力恒未裁定；本层关系分类只消费病药顶层（第一对）的角色点名，第二对陈述随 pairs 逐字携带、本阶段不单独分类；未触发不等于无病（该 Variant 永不输出「无病」）。',
    '旺衰裁定仅 3 条木日主充分谓词（卯 pure、亥 generating、酉 isolated），其余命盘恒弃判；覆盖事实：当前覆盖下病药触发之盘旺衰恒弃判，三体系均已陈述且无冲突的组合在真实盘上当前不可达。',
    '调候陈述的是原典取用顺序与存在性事实，不是吉凶；本层的一致/冲突是角色语义的结构比较，不是吉凶或喜用判断。',
    '扶抑、格局用神两体系未建（absent），本层不评估；后续体系建成后须另行扩围接入，不得默认本层已覆盖。',
    '本层不新增 trace rule，不进 RuleMatch 与 Evidence；所携三体系的 evidence_binding 状态各自保留，本层不改变其绑定状态。',
)


def _require_statement(name, statement, *, variant, system=None):
    if not isinstance(statement, dict):
        raise ValueError(f'Conflict presentation requires the {name} statement object')
    if statement.get('variant') != variant:
        raise ValueError(f'Conflict presentation requires the reviewed {name} variant')
    if system is not None and statement.get('system') != system:
        raise ValueError(f'Conflict presentation requires the {name} system statement')
    if statement.get('research_only') is not True \
            or statement.get('public_enabled') is not False \
            or statement.get('ai_enabled') is not False:
        raise ValueError(f'Conflict presentation requires research-only {name} statements')


def _tiaohou_record(statement):
    status = statement.get('status')
    if status == 'matched':
        return {'system': SYSTEM_TIAOHOU, 'variant': TIAOHOU_VARIANT,
                'status': 'adjudicated', 'statement': copy.deepcopy(statement)}
    if status == 'not_applicable':
        return {'system': SYSTEM_TIAOHOU, 'variant': TIAOHOU_VARIANT,
                'status': 'not_applicable',
                'abstain_reason': statement.get('reason'),
                'statement': copy.deepcopy(statement)}
    raise ValueError('Unsupported tiaohou statement status for presentation')


def _bingyao_record(statement):
    status = statement.get('status')
    if status == 'triggered':
        return {'system': SYSTEM_BINGYAO, 'variant': BINGYAO_VARIANT,
                'status': 'adjudicated', 'statement': copy.deepcopy(statement)}
    if status == 'not_triggered':
        return {'system': SYSTEM_BINGYAO, 'variant': BINGYAO_VARIANT,
                'status': 'abstained',
                'abstain_reason': statement.get('not_triggered_reason'),
                'statement': copy.deepcopy(statement)}
    raise ValueError('Unsupported bingyao statement status for presentation')


def _strength_record(statement):
    classification = statement.get('classification')
    if classification in ('strong', 'weak'):
        return {'system': SYSTEM_STRENGTH, 'variant': ADJUDICATION_VARIANT,
                'status': 'adjudicated', 'statement': copy.deepcopy(statement)}
    if classification == 'indeterminate':
        return {'system': SYSTEM_STRENGTH, 'variant': ADJUDICATION_VARIANT,
                'status': 'abstained',
                'abstain_reason': statement.get('decision_status'),
                'statement': copy.deepcopy(statement)}
    raise ValueError('Unsupported strength statement classification for presentation')


def _absent_record(system):
    return {'system': system, 'variant': None, 'status': 'absent',
            'absent_reason': ABSENT_REASONS[system], 'statement': None}


def _tiaohou_named(statement):
    """Stems named by the tiaohou entry's main sequence, with order."""
    return {item['stem']: {'role': 'primary_pick', 'order': item['order'],
                           'presence': item['presence']}
            for item in statement.get('sequence') or []}


def _bingyao_named(statement):
    """Stems named by a triggered bingyao pair, with role/pillar/god."""
    named = {}
    for role, key in (('subject', 'subject'),
                      ('disease', 'disease_candidate'),
                      ('medicine', 'medicine_candidate')):
        block = statement.get(key)
        if not block:
            continue
        for god in block['gods']:
            named[god['stem']] = {'role': role, 'pillar': god['pillar'],
                                  'ten_god': god['ten_god']}
    return named


def _relations(records):
    by_system = {r['system']: r for r in records}
    tiaohou = by_system[SYSTEM_TIAOHOU]
    bingyao = by_system[SYSTEM_BINGYAO]
    strength = by_system[SYSTEM_STRENGTH]
    t_named = _tiaohou_named(tiaohou['statement']) \
        if tiaohou['status'] == 'adjudicated' else {}
    b_named = _bingyao_named(bingyao['statement']) \
        if bingyao['status'] == 'adjudicated' else {}
    t_ref = None
    if tiaohou['status'] == 'adjudicated':
        entry = tiaohou['statement']['entry']
        t_ref = {'system': SYSTEM_TIAOHOU, 'variant': TIAOHOU_VARIANT,
                 'quote_locator': copy.deepcopy(entry['quote_locator']),
                 'section': copy.deepcopy(entry['section'])}
    b_ref = None
    if bingyao['status'] == 'adjudicated':
        rule = bingyao['statement']['rule']
        b_ref = {'system': SYSTEM_BINGYAO, 'variant': BINGYAO_VARIANT,
                 'rule_id': rule['id'],
                 'quote_locator': copy.deepcopy(rule['quote_locator'])}
    relations = []
    for stem in sorted(set(t_named) | set(b_named)):
        t_role = t_named.get(stem)
        b_role = b_named.get(stem)
        if t_role is not None and b_role is not None:
            kind = {'medicine': 'support', 'disease': 'conflict',
                    'subject': 'pivot_overlap'}[b_role['role']]
        else:
            kind = 'one_sided'
        evidence_refs = []
        if t_role is not None:
            evidence_refs.append(t_ref)
        if b_role is not None:
            evidence_refs.append(b_ref)
        relations.append({
            'stem': stem, 'kind': kind,
            'definition': RELATION_DEFINITIONS[kind],
            'tiaohou': t_role, 'bingyao': b_role,
            'evidence_refs': evidence_refs,
        })
    s_statement = strength['statement']
    relations.append({
        'stem': None, 'kind': 'incomparable',
        'definition': RELATION_DEFINITIONS['incomparable'],
        'system': SYSTEM_STRENGTH, 'variant': ADJUDICATION_VARIANT,
        'classification': s_statement.get('classification'),
        'decision_status': s_statement.get('decision_status'),
        'evidence_refs': [{'system': SYSTEM_STRENGTH,
                           'variant': ADJUDICATION_VARIANT}],
    })
    return relations


def conflict_presentation(tiaohou, bingyao, strength, *,
                            presentation_variant=VARIANT):
    """Present the three built systems' statements for one chart side by side.

    Pure function over the three assessment outputs of a single executed
    chart (as produced by one operations.bazi_chart.chart call with the
    adjudication, tiaohou and bingyao variants enabled). Statements are
    carried verbatim; the only added semantics are the per-system
    presentation status and the structural relations documented in the
    module docstring. Forged, mixed-chart or non-research statements
    fail closed (ValueError); nothing here adjudicates across systems.
    """
    if presentation_variant != VARIANT:
        raise ValueError('Unsupported conflict presentation variant')
    _require_statement('tiaohou', tiaohou, variant=TIAOHOU_VARIANT,
                       system=SYSTEM_TIAOHOU)
    _require_statement('bingyao', bingyao, variant=BINGYAO_VARIANT,
                       system=SYSTEM_BINGYAO)
    _require_statement('strength', strength, variant=ADJUDICATION_VARIANT)
    if tiaohou.get('day_master') != bingyao.get('day_master'):
        raise ValueError('Conflict presentation requires statements of one chart')
    if bingyao.get('determination') is not None:
        raise ValueError('Bingyao statements never carry a determination')
    records = [_tiaohou_record(tiaohou), _bingyao_record(bingyao),
               _strength_record(strength),
               _absent_record(SYSTEM_FUYI), _absent_record(SYSTEM_PATTERN)]
    relations = _relations(records)
    if any(r['kind'] == 'conflict' for r in relations):
        status = 'presented_with_conflicts'
    elif any(r['status'] in ('abstained', 'not_applicable')
             for r in records if r['system'] in BUILT_SYSTEMS):
        status = 'presented_partial'
    else:
        status = 'presented_no_conflict'
    return {
        'variant': VARIANT, 'layer': 'presentation',
        'determination': None,
        'status': status,
        'status_definition': STATUS_DEFINITIONS[status],
        'day_master': tiaohou.get('day_master'),
        'month_branch': tiaohou.get('month_branch'),
        'systems': records,
        'relations': relations,
        'relation_definitions': dict(RELATION_DEFINITIONS),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(LIMITATIONS),
    }
