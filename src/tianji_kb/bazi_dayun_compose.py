"""大运古典链组合入口（TJ-017.4）：真实盘 → 方向 → 节距测量 → 换算区间 → 序列时间对齐。

治理定位：本模块是 TJ-017.1 区间契约的**消费侧接线**，不产生任何新规
则、新裁定或新口径。它把四个已审资产按固定顺序串联：

1. `calendar_for_zone`（TJ-031 已审历法路径）由出生时刻与时区推导四柱；
2. `classical_direction`（TJ-017.1 方向 Variant）由年柱与**显式**传统
   角色裁定方向与计数目标（角色绝不由身份数据推断，缺失即拒绝）；
3. `adjacent_jie_distance`（TJ-015 节距测量，provider 钉定）按方向测量
   出生至目标节的实历秒数；
4. `sanming_convert_measurement`（TJ-017.1 三命换算 Variant，含测量重
   放校验）折算为起运时长区间与交运时刻区间；
5. `candidate_sequence`（TJ-014.2 候选序列）给出逐运干支，本模块把其
   逐运条目与交运时刻区间按 period_index 对齐标注（序列时间对齐）。

硬边界（与 TJ-017.1 契约一致，组合层以断言与专项钉死）：

- 输出只有区间：起运时长区间（日）与交运/序列起始时刻区间；组合自产
  结构不含任何单点日期字段、不含任何年龄数值字段。被逐字嵌入的既有
  结果中若含同名键，其值恒为 None（序列模块的防伪空位），组合不填充。
- 恰逢节（实历计数为零）维持 TJ-016.2/TJ-017.1 拒绝口径：组合返回
  status='unresolved' 并传播 reason，时长与交运/起始区间均不给出。
- 生刻不明（birth_time_precision='unknown'）沿用 TJ-017.1 近似口径：
  区间按原文「生刻不明许近似」加宽并标注 approximate，不伪造精度。
- 神峰日级口径只可**并列**请求（include_shenfeng）：独立给出其时长区
  间与首运起始区间（组合层由其时长区间平移出生时刻导出，逐项标
  注 derivation），不提供神峰口径的逐运对齐；两口径永不混算、不取
  平均、不互相覆盖，引用必须带 method 标签。
- 序列口径沿用 TJ-014.2 既有政策（首运排除月柱本身）；三命例首运取
  月柱本身的差异已在 TJ-017.1 登记为不在其 Variant 范围，本组合不自
  行裁定，仅在 limitations 中标注。
- 本模块只存在于研究模块层：不接入 engine 公开面、不接任何显示面
  （TJ-017.3 的范围），不改变生产 dayun 显示口径。TJ-017.2（原局＋大
  运＋流年跨规则调用）与本组合无涉。
- 运行边界与所调用的序列模块相同：candidate_sequence 的十神计算依赖
  组装环境的 canonical foundations 数据，公共检出（按验收规则不含
  data/）无法执行完整组合；公开专项只钉 Golden 转写与 fail-closed
  路径，真实盘全链由密封专项在组装环境回验（仓库既有分区规则）。
- 本组合与所串联的 Variant 相同：尚未在密封 Phase1/Phase2 注册
  rule，evidence_binding 为 pending_phase1_rule_registration。
- 恒 research_only=True、public_enabled=False、ai_enabled=False。
"""
from datetime import datetime, timedelta

from .bazi_dayun_classical import (
    CONVERSION_VARIANT,
    DIRECTION_VARIANT,
    PRECISIONS,
    ROLES,
    SHENFENG_CONVERSION_VARIANT,
    classical_direction,
    sanming_convert_measurement,
    shenfeng_convert_days,
    validate_classical_direction,
)
from .bazi_dayun_jie import adjacent_jie_distance
from .bazi_dayun_sequence import VARIANT as SEQUENCE_VARIANT
from .bazi_dayun_sequence import candidate_sequence
from .calendar_tz import calendar_for_zone, resolve_zone

COMPOSE_VARIANT = 'dayun-classical-composition-v1'
MEASUREMENT_VARIANT = 'bazi-dayun-adjacent-jie-research-v1'
MAX_PERIODS = 12

LIMITATIONS = (
    '组合层不产生新规则、新裁定：方向、测量、换算、序列全部逐字调用已审资产，组合输出与手动串联同一链的结果逐项一致（专项钉死）。',
    '首运口径沿用 TJ-014.2 候选序列政策（首运排除月柱本身）；三命例首运取月柱本身的口径差异已在 TJ-017.1 登记为不在其 Variant 范围，本组合不自行裁定。',
    '神峰日级并列只给首运起始区间（组合层导出，逐项标注 derivation），不提供神峰口径的逐运对齐；两口径结果永不合并、不取平均。',
    '出生时刻的时区与历史时区口径沿用 TJ-015/TJ-017.1 既有边界（节距测量归一 Asia/Shanghai、1901–2098、历史时区未独立验证），本组合不新裁定。',
    '闰月交运子规则未编码（TJ-017.1 已整段排除）：闰月出生者的交运区间按非闰算式给出时必须视为未审，此限定随 TJ-017.1 limitations 一并在所嵌入的换算结果中给出。',
    '虚岁/实岁无原典口径：本组合一切输出不含年龄数值；「约 X 岁」式呈现属 TJ-017.3 的产品约定，不在本模块范围。',
    '本组合尚未在密封 Phase1 bundle/Phase2 contract 注册 rule，不进 RuleMatch 与 Evidence（evidence_binding 与 TJ-017.1 同口径披露）。',
)


def _flags():
    return {'research_only': True, 'public_enabled': False,
            'ai_enabled': False,
            'evidence_binding': 'pending_phase1_rule_registration'}


def classical_dayun_timeline(birth_value, *, zone=None, traditional_role,
                             periods=8, birth_time_precision='second',
                             include_shenfeng=False):
    """Compose the classical Dayun chain for one real birth instant.

    birth_value: ISO datetime string (timezone-aware) or aware datetime,
    exactly as the reviewed calendar path accepts. zone: IANA name for
    the pillar frame (None -> Asia/Shanghai, the calendar default).
    traditional_role: 'male' | 'female', an explicit historical
    category label; it is never inferred and its absence is a refusal.

    Returns intervals only: the Sanming start-duration interval, the
    handover moment intervals, and the TJ-014.2 candidate sequence with
    each period's start interval aligned by period_index. On the
    zero-jie boundary the result is status='unresolved' with the
    TJ-017.1 refusal reason propagated and no intervals.
    """
    if type(traditional_role) is not str or traditional_role not in ROLES:
        raise ValueError('Explicit traditional_role=male|female is '
                         'required; it is never inferred')
    if type(periods) is not int or not 1 <= periods <= MAX_PERIODS:
        raise ValueError('periods must be an integer from 1 to %d'
                         % MAX_PERIODS)
    if birth_time_precision not in PRECISIONS:
        raise ValueError('birth_time_precision must be one of %r'
                         % (PRECISIONS,))
    if type(include_shenfeng) is not bool:
        raise ValueError('include_shenfeng must be a boolean')
    effective_zone = resolve_zone(zone)
    cal = calendar_for_zone(birth_value, zone)
    pillars = {
        'year_ganzhi': cal['year_ganzhi'],
        'month_ganzhi': cal['month_ganzhi'],
        'day_ganzhi': cal['day_ganzhi'],
        'hour_ganzhi': cal['hour_ganzhi'],
        'day_master': cal['day_ganzhi'][0],
    }
    direction_result = classical_direction(
        pillars['year_ganzhi'], traditional_role=traditional_role)
    validate_classical_direction(direction_result)
    direction = direction_result['direction']
    measured = adjacent_jie_distance(
        birth_value, direction,
        expected_month_ganzhi=pillars['month_ganzhi'])
    converted = sanming_convert_measurement(
        measured, birth_time_precision=birth_time_precision,
        periods=periods)
    sequence = candidate_sequence(
        pillars['month_ganzhi'], pillars['day_master'],
        direction=direction, periods=periods)

    handovers = converted.get('handover_intervals') or []
    alignment = []
    for row in sequence['rows']:
        entry = {
            'period_index': row['period_index'],
            'candidate_ganzhi': row['candidate_ganzhi'],
            'stem': row['stem'],
            'branch': row['branch'],
            'ten_god_relative_to_natal_day_stem':
                row['ten_god_relative_to_natal_day_stem'],
        }
        if converted['status'] == 'converted':
            handover = handovers[row['period_index'] - 1]
            if handover['period_index'] != row['period_index']:
                raise ValueError('Handover/sequence period alignment '
                                 'mismatch')
            entry['start_interval'] = {
                'earliest': handover['earliest'],
                'latest': handover['latest'],
                'max_inclusive': handover['max_inclusive'],
                'basis': handover['basis'],
                'method': 'sanming_shichen_level',
                'variant': CONVERSION_VARIANT,
            }
        else:
            entry['start_interval'] = None
            entry['start_interval_status'] = (
                'unresolved: ' + converted['reason'])
        alignment.append(entry)

    result = {
        'variant': COMPOSE_VARIANT,
        'status': converted['status'],
        'composition_chain': [
            DIRECTION_VARIANT, MEASUREMENT_VARIANT, CONVERSION_VARIANT,
            SEQUENCE_VARIANT],
        'birth': {
            'input_value': (birth_value.isoformat()
                            if isinstance(birth_value, datetime)
                            else birth_value),
            'zone': effective_zone,
            'local_datetime': measured['birth_local_datetime'],
        },
        'pillars': pillars,
        'traditional_role': traditional_role,
        'traditional_role_selection':
            'explicit_historical_category_not_inferred_identity',
        'direction': direction_result,
        'counting': {
            'measurement_variant': measured['variant'],
            'calendar_provider': measured['calendar_provider'],
            'selected_jie': measured['selected_jie'],
            'previous_jie': measured['previous_jie'],
            'next_jie': measured['next_jie'],
            'elapsed_seconds': measured['elapsed_seconds'],
            'elapsed_whole_days': measured['elapsed_whole_days'],
            'remaining_seconds_after_whole_days':
                measured['remaining_seconds_after_whole_days'],
            'zero_distance': measured['zero_distance'],
        },
        'sanming_conversion': converted,
        'sequence': sequence,
        'sequence_time_alignment': alignment,
        'alignment_method': 'sanming_shichen_level',
        'parallel_variants': {},
        'limitations': list(LIMITATIONS),
        **_flags(),
    }
    if converted['status'] != 'converted':
        result['reason'] = converted['reason']
    if include_shenfeng:
        result['parallel_variants']['shenfeng_day_level'] = (
            _shenfeng_parallel(measured, direction))
    return result


def _shenfeng_parallel(measured, direction):
    """Shenfeng day-level result next to the Sanming chain, unmerged.

    Only the duration interval comes from the TJ-017.1 Shenfeng
    Variant. The first-period start interval is a composition-level
    derivation (birth instant + that duration interval) and is labeled
    as such; no decade-shifted Shenfeng period starts are provided.
    """
    converted = shenfeng_convert_days(measured['elapsed_whole_days'],
                                      direction=direction)
    block = {
        'variant': SHENFENG_CONVERSION_VARIANT,
        'status': converted['status'],
        'method': 'shenfeng_day_level',
        'input': converted.get('input'),
        'counting_target': converted.get('counting_target'),
        'text_result_days': converted.get('text_result_days'),
        'duration_interval_days': converted.get('duration_interval_days'),
        'granularity_note': converted.get('granularity_note'),
        'parallel_note': ('神峰日级与三命时级分立：本块独立给出，永不与'
                          '三命链合并、不取平均；引用必须带 method 标签。'),
    }
    if converted['status'] == 'converted':
        birth = datetime.fromisoformat(measured['birth_local_datetime'])
        interval = converted['duration_interval_days']
        block['first_period_start_interval'] = {
            'earliest': (birth + timedelta(days=interval['min_days']))
            .isoformat(),
            'latest': (birth + timedelta(days=interval['max_days']))
            .isoformat(),
            'max_inclusive': interval['max_inclusive'],
            'derivation': ('composition_level_birth_plus_shenfeng_'
                           'duration_interval'),
            'decade_shifts': ('not_provided_for_shenfeng_at_'
                              'composition_level'),
        }
    else:
        block['reason'] = converted['reason']
    return block
