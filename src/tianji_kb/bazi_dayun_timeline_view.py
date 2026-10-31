"""大运时间轴用户可读视图（TJ-017.3）：TJ-017.4 组合结果的确定性呈现层。

WBS 定义核对（先行审计结论）：TJ-017.3 原文行为「用户可读时间轴
视图 | 允许方法选择与来源；未知/争议交运年份用空态，而不是拟制
时间」，与本批任务书一致，无冲突。本模块就是该视图：消费
`classical_dayun_timeline`（TJ-017.4）的组合结果，确定性构造可读
时间轴视图数据——逐运干支与起始时刻区间、区间依据分解、方法选择
（三命时级 / 神峰日级并列）、逐方法的 Variant 与原文出处呈现。

落点裁定（审计后）：后端研究层视图模型，不接公开 API、不接前端
页面。理由：古典大运链全链 research_only / public_enabled=False
（TJ-016.3 硬边界、TJ-017.1/017.4 自身治理标志、evidence_binding
仍为 pending_phase1_rule_registration）；TJ-014–016 的既有公开口
径只有诚实未裁定说明（人生总览「本总览不推算或伪造大运时间线」、
八字命理页「不计算大运起运岁数」），把研究级区间推上公开页面将
超出该口径，并与「不改 TJ-017.1/017.4 任何计算与输出」的红线冲
突（翻转 public_enabled 即改输出）。公开开放属能力纲领的「分阶
段开放」阶段，须待密封 Phase1 注册后另行裁定。呈现层先例：
TJ-013.3 研究级可读渲染 + 公开投影防御剥离，本模块同例（投影层
对 dayun_timeline_view 键另有防御性剥离）。

年龄口径裁定：不呈现任何年龄数值。古典起运是实历时长（TJ-017.1
审源：虚岁/实岁五书零命中、无年龄原典），把时长折算为「约 X
岁」需要无审定来源的年长约定；既有公开页面口径亦为「不计算大运
起运岁数」。本视图只呈现交运日期区间与时长区间（日数区间 + 换
算自身的年单位/余时分解）。

硬边界（与 TJ-017.1/017.4 契约一致，专项钉死）：

- 区间保真：视图中的每个起始区间逐字复制组合结果（端点与开闭不
  变），不折算单点、不取中点、不改精度；首运区间与出生时刻 + 时
  长区间的端点一致性由专项断言钉住。
- 方法分立：三命时级与神峰日级一次呈现一种，method 字段标明；
  两口径永不合并、不取平均。神峰视图只有首运起始区间（组合层导
  出，derivation 透传），第二运起为 not_provided 空态，不以十年
  平移拟制。
- 空态而非拟制：恰逢节（组合 status='unresolved'）整图呈
  unresolved 空态；神峰整日计数为零呈该口径空态；请求神峰视图
  而组合结果未含神峰并列块时 fail-closed 拒绝（ValueError），
  绝不临时补算。
- 来源呈现只限组合结果实际携带的引文（方向规则句与卷十一见证、
  换算的交运依据句、神峰例句）；换算比率诸句登记在 TJ-017.1 算
  术层结果中、组合层未嵌入，视图不越权补引，只以 Variant 与
  Source 登记标明出处链。
- 输入 fail-closed：非 TJ-017.4 组合结果、治理标志被篡改
  （public/ai 被开启）、方向结果未过 TJ-017.1 自校验、所消费字
  段缺失或形态不符，一律 ValueError。
- 本视图不产生新规则、新裁定、新文案断语：不含任何大运吉凶、
  运势评价或预测性表述；十神仅为序列事实字段透传。
- 恒 research_only=True、public_enabled=False、ai_enabled=False，
  evidence_binding 与组合层同口径披露。

E0346 分段改记：组合所串联的三命分段已经注册（bazi.rule.r038/
r039 与对应 Phase2 步），本视图与组合层的 evidence_binding 同
步改记 segmented_inherited_pending（继承的神峰分段仍 pending）；
视图呈现的三命引文块改以其绑定来源（应用文本来源
bazi.source.sanmingtonghui-applied）标名与选取。本视图仍不接
公开页面，公开开放仍须分阶段开放另行裁定；视图内容（区间、
空态、年龄不呈现）逐字不变。
"""
import copy

from .bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    SHENFENG_CONVERSION_VARIANT,
    SHENFENG_SOURCE_ID,
    SANMING_SOURCE_ID,
    validate_classical_direction,
)
from .bazi_dayun_compose import COMPOSE_VARIANT, classical_dayun_timeline

VIEW_VARIANT = 'dayun-timeline-view-v1'
METHODS = ('sanming', 'shenfeng')
AGE_PRESENTATION = 'not_presented'

# The Shenfeng conversion Variant cites exactly these three example
# quotes (see shenfeng_convert_days.evidence_quotes). The view's
# Shenfeng source block must match that citation set exactly; the
# quotes themselves are carried verbatim by the direction result's
# evidence_quotes (the composition's Shenfeng parallel block does not
# re-embed them).
SHENFENG_CONVERSION_QUOTE_IDS = ('sf_ex1', 'sf_ex3', 'sf_ex4')

LIMITATIONS = (
    '本视图是 TJ-017.4 组合结果的确定性呈现层：不产生新规则、新裁定，不改动组合输出的任何区间端点（含端点开闭）。',
    '落点为后端研究层视图模型：全链 research_only、public_enabled=False，本视图不接入公开 API 与前端页面；公开开放须待密封 Phase1 注册与分阶段开放裁定，另行立项。',
    '年龄口径：古典起运为实历时长，虚岁/实岁无原典；本视图只呈现交运日期区间与时长区间，不折算、不呈现任何年龄数值。',
    '神峰日级视图只有首运起始区间（组合层导出并标注 derivation）；逐运起始区间仅三命时级口径提供。',
    '方向与计数目标由 TJ-017.1 古典方向 Variant 给出；传统角色为显式历史分类标签，绝不由身份数据推断（组合入口已强制显式传入）。',
)

_NOTICE_METHODS_SEPARATE = {
    'code': 'methods_presented_separately',
    'text': ('三命时级与神峰日级是两种独立口径，本视图一次呈现一种，'
             '所选口径见 method 字段；两口径永不合并、不取平均。'),
}
_NOTICE_ZERO_JIE = {
    'code': 'zero_jie_boundary',
    'text': ('出生时刻恰逢节气交界（实历计数为零）：原文例算未覆盖'
             '此情形，处理约定未经审定，本视图不拟制交运时间。'),
}
_NOTICE_APPROXIMATE = {
    'code': 'approximate_birth_time',
    'text': ('出生时刻精度不足：时长与交运区间已按原文近似口径加宽'
             '呈现，加宽后的区间不代表更精确的交运时刻。'),
}
_NOTICE_SHENFENG_NO_DECADES = {
    'code': 'shenfeng_decade_shifts_not_provided',
    'text': ('神峰日级口径在组合层只导出首运起始区间，第二运起不'
             '提供起始区间，不以十年平移拟制。'),
}
_NOTICE_SHENFENG_ZERO_DAY = {
    'code': 'shenfeng_zero_day_count',
    'text': ('神峰日级：整日计数为零未见原文例，该口径下交运时间'
             '不予拟制。'),
}


def _flags():
    # E0346: the viewed composition's Sanming segment is registered
    # upstream (bazi.rule.r038/r039); this view registers nothing
    # itself and its inherited Shenfeng segment remains pending.
    # Public opening still requires its own staged-opening ruling.
    return {'research_only': True, 'public_enabled': False,
            'ai_enabled': False,
            'evidence_binding': 'segmented_inherited_pending'}


def _require(mapping, key, where):
    if not isinstance(mapping, dict) or key not in mapping:
        raise ValueError('Timeline view requires %s.%s' % (where, key))
    return mapping[key]


def _validate_timeline(timeline):
    if not isinstance(timeline, dict):
        raise ValueError('Timeline view requires a composition result '
                         'dict')
    if timeline.get('variant') != COMPOSE_VARIANT:
        raise ValueError('Timeline view only consumes %r results'
                         % COMPOSE_VARIANT)
    if (timeline.get('research_only') is not True
            or timeline.get('public_enabled') is not False
            or timeline.get('ai_enabled') is not False):
        raise ValueError('Composition result governance flags are not '
                         'the reviewed research-only set')
    if timeline.get('status') not in ('converted', 'unresolved'):
        raise ValueError('Composition result status is not '
                         'converted/unresolved')
    for key in ('composition_chain', 'birth', 'pillars',
                'traditional_role', 'traditional_role_selection',
                'direction', 'counting', 'sanming_conversion',
                'sequence', 'sequence_time_alignment'):
        _require(timeline, key, 'timeline')
    # The direction block must pass the TJ-017.1 self-validation gate
    # (recomputation against the classical rule; forgery rejection).
    validate_classical_direction(timeline['direction'])
    conversion = timeline['sanming_conversion']
    if conversion.get('variant') != CONVERSION_VARIANT:
        raise ValueError('Composition result carries no TJ-017.1 '
                         'Sanming conversion')
    sequence = timeline['sequence']
    rows = _require(sequence, 'rows', 'timeline.sequence')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Composition result sequence has no rows')
    alignment = timeline['sequence_time_alignment']
    if (not isinstance(alignment, list)
            or len(alignment) != len(rows)):
        raise ValueError('Sequence/time alignment does not match the '
                         'sequence rows')
    for row, entry in zip(rows, alignment):
        if entry.get('period_index') != row.get('period_index'):
            raise ValueError('Sequence/time alignment period mismatch')
        if timeline['status'] == 'converted':
            interval = entry.get('start_interval')
            if not isinstance(interval, dict):
                raise ValueError('Converted composition rows must '
                                 'carry start intervals')
            for key in ('earliest', 'latest', 'max_inclusive',
                        'basis', 'method', 'variant'):
                _require(interval, key, 'start_interval')
        else:
            if entry.get('start_interval') is not None:
                raise ValueError('Unresolved composition rows must '
                                 'not carry start intervals')
    return timeline


def _natal_block(timeline):
    birth = timeline['birth']
    pillars = timeline['pillars']
    return {
        'birth': {
            'input_value': birth['input_value'],
            'zone': birth['zone'],
            'local_datetime': birth['local_datetime'],
        },
        'pillars': {
            'year': pillars['year_ganzhi'],
            'month': pillars['month_ganzhi'],
            'day': pillars['day_ganzhi'],
            'hour': pillars['hour_ganzhi'],
            'day_master': pillars['day_master'],
        },
        'traditional_role': timeline['traditional_role'],
        'traditional_role_selection':
            timeline['traditional_role_selection'],
    }


def _direction_block(timeline):
    direction = timeline['direction']
    conversion = timeline['sanming_conversion']
    return {
        'value': direction['direction'],
        'label': '顺行' if direction['direction'] == 'forward' else '逆行',
        'counting_target': direction['counting_target'],
        'counted_jie': copy.deepcopy(conversion.get('counted_jie')),
        'rule_quote': copy.deepcopy(direction['rule_quote']),
    }


def _counting_block(timeline):
    return copy.deepcopy(timeline['counting'])


def _method_options(timeline):
    parallel = timeline.get('parallel_variants') or {}
    return [
        {'id': 'sanming', 'label': '三命时级',
         'variant': CONVERSION_VARIANT, 'source_id': SANMING_SOURCE_ID,
         'selectable': True},
        {'id': 'shenfeng', 'label': '神峰日级',
         'variant': SHENFENG_CONVERSION_VARIANT,
         'source_id': SHENFENG_SOURCE_ID,
         'selectable': 'shenfeng_day_level' in parallel},
    ]


# E0346: since the Sanming segment's Canonical registration, the
# Sanming quotes carried by the direction result are bound to the
# applied-text source; the view's Sanming quote blocks name that
# binding source and select quotes by it. The classic itself (the
# method-level registration provenance) is unchanged.
SANMING_APPLIED_SOURCE_ID = 'bazi.source.sanmingtonghui-applied'


def _sources(timeline, method):
    """Source blocks from what the composition actually carries.

    The measurement-level Sanming conversion embeds no evidence
    quote list (its ratio/anti-rounding quotes live in the TJ-017.1
    arithmetic layer's results, which the composition does not
    embed); the view surfaces exactly the quotes the composed
    result carries -- the direction rule quote and its Sanming
    witness, the handover basis quote on converted results, and the
    Shenfeng example quotes -- and never invents citations the
    input does not contain. Every block still names its Variant and
    source registration, so the provenance chain is complete at the
    registration level.
    """
    direction = timeline['direction']
    conversion = timeline['sanming_conversion']
    if method == 'sanming':
        direction_quotes = [
            copy.deepcopy(q) for q in direction['evidence_quotes']
            if q.get('source_id') == SANMING_APPLIED_SOURCE_ID]
        if [q['id'] for q in direction_quotes] != [
                'direction_rule', 'vol11_direction_witness']:
            raise ValueError('Direction evidence quotes do not carry '
                             'the Sanming direction citation set')
        blocks = [
            {'method': 'sanming', 'role': 'direction_rule',
             'variant': DIRECTION_VARIANT,
             'source_id': SANMING_APPLIED_SOURCE_ID,
             'quotes': direction_quotes},
        ]
        if 'handover_basis_quote' in conversion:
            blocks.append(
                {'method': 'sanming', 'role': 'handover_basis',
                 'variant': CONVERSION_VARIANT,
                 'source_id': SANMING_APPLIED_SOURCE_ID,
                 'quotes': [copy.deepcopy(
                     conversion['handover_basis_quote'])]})
        return blocks
    wanted = set(SHENFENG_CONVERSION_QUOTE_IDS)
    quotes = [copy.deepcopy(q) for q in direction['evidence_quotes']
              if q.get('source_id') == SHENFENG_SOURCE_ID
              and q.get('id') in wanted]
    if [q['id'] for q in quotes] != list(SHENFENG_CONVERSION_QUOTE_IDS):
        raise ValueError('Direction evidence quotes do not carry the '
                         'Shenfeng conversion citation set')
    return [
        {'method': 'shenfeng', 'role': 'conversion_examples',
         'variant': SHENFENG_CONVERSION_VARIANT,
         'source_id': SHENFENG_SOURCE_ID, 'quotes': quotes},
    ]


def _sanming_duration(timeline):
    conversion = timeline['sanming_conversion']
    block = {
        'method': conversion['method'],
        'variant': CONVERSION_VARIANT,
        'status': conversion['status'],
        'interval_days': copy.deepcopy(
            conversion.get('duration_interval_days')),
        'decomposition': copy.deepcopy(
            conversion.get('duration_decomposition')),
        'counting': copy.deepcopy(conversion.get('counting')),
        'approximate': conversion.get('approximate', False),
        'rounding_applied': False,
        'rounding_policy':
            'refused_classical_text_prohibits_rounding',
    }
    if 'approximation_basis' in conversion:
        block['approximation_basis'] = copy.deepcopy(
            conversion['approximation_basis'])
    if conversion['status'] != 'converted':
        block['reason'] = conversion.get('reason')
    return block


def _shenfeng_block(timeline):
    parallel = timeline.get('parallel_variants') or {}
    block = parallel.get('shenfeng_day_level')
    if block is None:
        raise ValueError('Shenfeng view requires a composition result '
                         'built with include_shenfeng=True; the view '
                         'never derives a parallel method on its own')
    if block.get('variant') != SHENFENG_CONVERSION_VARIANT:
        raise ValueError('Composition parallel block is not the '
                         'TJ-017.1 Shenfeng conversion')
    return block


def _shenfeng_duration(block):
    duration = {
        'method': 'shenfeng_day_level',
        'variant': SHENFENG_CONVERSION_VARIANT,
        'status': block['status'],
        'interval_days': copy.deepcopy(
            block.get('duration_interval_days')),
        'text_result_days': block.get('text_result_days'),
        'counting': {
            'whole_days': (block.get('input') or {}).get('whole_days'),
            'counting_target': block.get('counting_target'),
        },
        'granularity_note': block.get('granularity_note'),
        'approximate': False,
    }
    if block['status'] != 'converted':
        duration['reason'] = block.get('reason')
    return duration


def _base_entry(row):
    return {
        'period_index': row['period_index'],
        'ganzhi': row['candidate_ganzhi'],
        'stem': row['stem'],
        'branch': row['branch'],
        'ten_god_relative_to_natal_day_stem':
            row['ten_god_relative_to_natal_day_stem'],
    }


def _sanming_entries(timeline):
    entries = []
    for row in timeline['sequence_time_alignment']:
        entry = _base_entry(row)
        if timeline['status'] == 'converted':
            entry['state'] = 'interval'
            entry['start_interval'] = copy.deepcopy(
                row['start_interval'])
        else:
            entry['state'] = 'unresolved'
            entry['start_interval'] = None
            entry['start_interval_status'] = row.get(
                'start_interval_status')
        entries.append(entry)
    return entries


def _shenfeng_entries(timeline, block):
    entries = []
    for row in timeline['sequence']['rows']:
        entry = _base_entry(row)
        if block['status'] != 'converted':
            entry['state'] = 'unresolved'
            entry['start_interval'] = None
            entry['start_interval_status'] = (
                'unresolved: ' + str(block.get('reason')))
        elif row['period_index'] == 1:
            interval = block['first_period_start_interval']
            entry['state'] = 'interval'
            entry['start_interval'] = {
                'earliest': interval['earliest'],
                'latest': interval['latest'],
                'max_inclusive': interval['max_inclusive'],
                'derivation': interval['derivation'],
                'decade_shifts': interval['decade_shifts'],
                'method': 'shenfeng_day_level',
                'variant': SHENFENG_CONVERSION_VARIANT,
            }
        else:
            entry['state'] = 'not_provided'
            entry['start_interval'] = None
            entry['start_interval_status'] = (
                'not_provided: shenfeng day-level decade shifts are '
                'not derived at composition level')
        entries.append(entry)
    return entries


def dayun_timeline_view(timeline, *, method='sanming'):
    """Build the user-readable Dayun timeline view for one method.

    timeline: a `classical_dayun_timeline` result, consumed verbatim
    (never recomputed, never re-derived). method: 'sanming' (the
    primary registration, per-period start intervals) or 'shenfeng'
    (the parallel day-level registration; only the first period's
    start interval exists, later periods are an explicit
    not_provided empty state). The two methods are alternative views
    of the same composed timeline: switching methods never changes
    the natal, direction or counting facts.
    """
    if method not in METHODS:
        raise ValueError('method must be one of %r' % (METHODS,))
    _validate_timeline(timeline)
    notices = [dict(_NOTICE_METHODS_SEPARATE)]
    if timeline['status'] != 'converted':
        notices.append(dict(_NOTICE_ZERO_JIE))
    if method == 'sanming':
        duration = _sanming_duration(timeline)
        entries = _sanming_entries(timeline)
        status = timeline['status']
        if duration.get('approximate'):
            notices.append(dict(_NOTICE_APPROXIMATE))
    else:
        block = _shenfeng_block(timeline)
        duration = _shenfeng_duration(block)
        entries = _shenfeng_entries(timeline, block)
        status = block['status']
        notices.append(dict(_NOTICE_SHENFENG_NO_DECADES))
        if block['status'] != 'converted':
            notices.append(dict(_NOTICE_SHENFENG_ZERO_DAY))
    view = {
        'variant': VIEW_VARIANT,
        'view_of_variant': COMPOSE_VARIANT,
        'composition_chain': list(timeline['composition_chain']),
        'status': status,
        'method': method,
        'method_options': _method_options(timeline),
        'natal': _natal_block(timeline),
        'direction': _direction_block(timeline),
        'counting': _counting_block(timeline),
        'duration': duration,
        'entries': entries,
        'notices': notices,
        'sources': _sources(timeline, method),
        'age_presentation': AGE_PRESENTATION,
        'limitations': list(LIMITATIONS),
        **_flags(),
    }
    if status != 'converted':
        view['reason'] = duration.get('reason')
    return view


def classical_dayun_timeline_views(birth_value, *, zone=None,
                                   traditional_role, periods=8,
                                   birth_time_precision='second'):
    """Both method views from one composed timeline (method switch).

    The composition runs once with include_shenfeng=True, so the
    Sanming and Shenfeng views share identical natal, direction and
    counting facts; only the conversion presentation differs. Same
    runtime boundary as the composition entry itself: the sequence
    stage needs the assembled canonical foundations, so in the
    public checkout this convenience entry can only run its
    fail-closed gates; end-to-end coverage lives in the sealed
    suite (仓库既有分区规则）.
    """
    timeline = classical_dayun_timeline(
        birth_value, zone=zone, traditional_role=traditional_role,
        periods=periods, birth_time_precision=birth_time_precision,
        include_shenfeng=True)
    return {
        'sanming': dayun_timeline_view(timeline, method='sanming'),
        'shenfeng': dayun_timeline_view(timeline, method='shenfeng'),
    }
