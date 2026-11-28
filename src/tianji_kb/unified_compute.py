"""统一内部计算入口（TJ-0426 Lane 6，U-01/U-02/U-03）。

一次排盘 + 强度 / 格局 / 喜用 / 组合 / 流年装配 + 各页裁剪。

研究级（``research_only=True、public_enabled=False、ai_enabled=False``）：
本入口只在内部装配各 lane 已批的研究引擎输出，**不**产生任何公开
presentation。公开面仍只走既有四门控（U1 / D-1 白名单 / dayun /
xiyong-public），各门控的语义与白名单一律不动；研究字段永不进入公开
presentation 对象（见 :func:`trim_for_bazi_profile` 等裁剪函数的
allowlist 与 :mod:`tests.test_tj0426_unified_compute` 的隔离测试）。

装配内容
----------
``assemble_birth`` 对一个出生瞬时只做一次标准排盘
（``execute("bazi", {value, include_relations, include_xianchi})``——与
``_romance`` / ``_compatibility`` 已在用的输入组合完全相同，不引入
新的执行输入组合），并在其上实算：

* 强度：``assess_strength``（古典因素层 + 现代工程模型，并列不统一）。
  司令试点只透传调用方为**同一出生瞬时实算**的试点（寅月任氏试点 /
  巳月三命 T1 试点，provider 核验的 Jie 窗口实算）；永不合成试点，
  无试点时对应谓词恒不点火（fail-closed）。
* 格局：``evaluate_all``（格局引擎 v2）。**不**在此重推 D-1 任氏寅月
  真格：D-1 的唯一授权路径仍是
  ``scenario_engine.ren_yin_research_execution``（寅月 + provider
  核验 + live 试点）；入口的格局块只含候选 / 现代层 / 伤官见官以外
  的破格缺口登记，``d1_determination`` 恒为 ``not_attempted_here``。
* 喜用：``evaluate_xiyong``（四体系并列；``unified_verdict`` 恒 None，
  TJ-013.2 裁决 A），调候 / 病药取自 ``tiaohou_lookup`` /
  ``bingyao_lookup`` 的直接输出（与既有组合测试同一形态）。
* 组合：仅当调用方显式给出传统口径（``traditional_role``）与目标年
  时才装配——大运方向与 8 运候选序列取自
  ``classical_dayun_timeline``（与 ``_dayun_public_gate`` 同一套
  server-fixed 常量），流年边界取自 ``annual_lichun_boundaries``；
  当期运未显式指定时记为未确定（D-02），组合引擎只记录、不推导。
  无口径或无目标年时组合块为 None 并具名原因。
* 大运（Q3=A，2026-11-28）：显式口径给出时即服务完整 8 运序列
  （``assembly['dayun']['timeline']``，``candidate_sequence``
  periods=8 + 逐运起运区间对齐，与目标年无关——八字页无目标年
  也能拿到）；无口径时为 None 并具名原因。流年查询数据：目标年
  干支（``flow_year``）+ 该年立春边界区间（``flow_boundary``，
  ``annual_lichun_boundaries`` 原样输出）。本入口只提供序列与
  边界供调用方查询，永不自行判定当期运（D-02）。
* 流年：目标年干支取自与各页同一的 July-1 参考日历口径
  （``calendar(f"{year}-07-01T12:00:00+08:00")``），不另立边界。

变体 pin 校验：格局 v2 / 旺衰 v1 / 喜用 v1 / 组合契约 v1。任一输出
变体漂移即 raise :class:`UnifiedComputePinError`（调用方不得吞掉
此类错误）；其余研究引擎故障只记入装配的 ``research.errors``，
对应块为 None，永不拖垮公开页。

多页复用：同一出生瞬时的出生层装配在模块内按
``(birth_value, zone)`` 缓存一次（上限 8 条，FIFO；返回深拷贝），
目标年层（大运 8 运序列 / 流年 / 流年边界 / 年度喜用 / 组合）按
``(birth_value, zone, traditional_role, target_year)`` 缓存；五页
通过裁剪函数消费同一份装配，出生时刻与目标年在五页间无漂移。
缓存只认确定性输入全量作 key；装配失败不污染缓存。

缓存生命周期（TJ-0427 Lane G，工程硬化；行为与上限不动）：
三层缓存（出生层 / 目标年层 / ``execute`` 去重层）各自上限 8 条
FIFO，内存总量恒 ≤ 24 条，永不无界增长；每层满时逐出最先插入
的条目（``_cache_put``，重放同一 key 不改变其插入顺序）。
``clear_unified_compute_cache()`` 清空全部三层；
``invalidate_unified_compute_cache(birth_value, ...)`` 按 key 逐条
失效（出生层 + 对应目标年层 + 同一出生瞬时的 ``execute`` 去重
条目）；``unified_compute_cache_info()`` 报告各层条数与上限。
全部返回路径（装配 / 目标年层 / 裁剪 / ``cached_execute`` /
``project_formal``）一律返回深拷贝：调用方对返回值的原地修改
永不污染缓存，一次请求也永不通过共享对象污染另一次请求。

请求作用域（TJ-0427 P1 硬化）：生产请求须在请求边界进入
``unified_compute_request_scope()``——进入时三层缓存均为本次请求
新建的空缓存，退出时（正常返回或异常）全部清空，出生瞬时与完整
计算结果不跨请求保留；不同线程 / asyncio 任务的并发请求各自持有
自己的 contextvars 上下文，永不互相串数据。同一请求内的重复
装配仍命中本请求缓存；未进入作用域的直接调用沿用模块级缓存
（兼容 fallback，仅供测试与离线脚本使用，不得用于多用户服务）。
上限与 FIFO 逐出规则在作用域内同样适用（每层 8 条，总量 ≤ 24 条）。
``unified_compute_request_scope_active()`` 报告当前上下文是否处
于一次请求作用域内。

正式投影（TJ-0427 Lane G）：:func:`project_formal` 是从装配到
正式（公开安全）视图的唯一显式投影函数，只输出 allowlist 字段
（出生瞬时 / 时区 / 目标年 + 排盘四柱 + 流年干支结构事实），
研究字段（``RESEARCH_FIELD_NAMES``，源自各裁剪的研究块 +
``natal_envelope`` + 公开 presentation 键）一律不得进入。
既有 ``trim_*`` 函数仍是研究块的强制执行点，本函数不削弱它们，
也不产生任何公开 presentation 对象（公开面仍只走既有四门控）。

本模块顶层只 import 标准库：全部引擎 import 均在函数内懒加载，
公开检出（无密封 ``data/``）下仍可 import，纯函数部分（pin、
裁剪、标注表）可直接测试；需要密封数据的装配路径按既有形制
SkipTest，不谎称通过。
"""

import contextvars
import copy
import json

UNIFIED_COMPUTE_VARIANT = 'unified-compute-entry-v1'

RESEARCH_ONLY = True
PUBLIC_ENABLED = False
AI_ENABLED = False

# 变体 pin（与各 lane 的已批输出钉死；升级须与入口校验同步）。
PIN_PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v2'
PIN_STRENGTH_ENGINE_VARIANT = 'bazi-strength-engine-v1'
PIN_XIYONG_ENGINE_VARIANT = 'bazi-xiyong-engine-v1'
PIN_COMBINATION_ENGINE_VARIANT = 'bazi-combination-engine-v1'
PIN_XIYONG_CONTRACT_VARIANT = 'bazi-xiyong-combination-contract-v1'
PIN_FLOW_BOUNDARY_VARIANT = 'bazi-annual-lichun-boundary-v1'
PIN_SILING_YIN_VARIANT = 'bazi-siling-yin-pilot-v1'
PIN_SILING_SI_VARIANT = 'bazi-siling-si-pilot-v1'
PIN_SILING_YIN_VERSION_ID = 'ditiansui-yuanshuo'
PIN_SILING_SI_VERSION_ID = 'sanming-t1'

_CACHE_MAX_ENTRIES = 8

# 出生层装配缓存：key 为 (birth_value, zone) 的 canonical JSON。
_CORE_CACHE = {}
# 目标年层装配缓存：key 为 (birth_value, zone, traditional_role,
# target_year) 的 canonical JSON；只存组合块与年度喜用。
_YEAR_CACHE = {}
# execute() 去重缓存：key 为 (domain, inputs, allow_research) 的
# canonical JSON；只存 pristine 深拷贝，返回的永远是深拷贝。
_EXECUTE_CACHE = {}


# 请求作用域（TJ-0427 P1 硬化）：三层缓存的条目只属于一次请求。
# 进入 ``unified_compute_request_scope()`` 后，当前上下文内的全部
# 装配与 ``cached_execute`` 调用读写该作用域自有的三份空缓存；
# 退出时（正常返回或异常）三份缓存全部清空，出生瞬时与完整计算
# 结果不再保留，作用域外的调用者永远看不到作用域内的条目。
# 未进入作用域时沿用上面的模块级缓存（直接调用 / 旧测试的兼容
# fallback；生产请求路径必须进入作用域，见
# ``unified_compute_request_scope``）。
class _RequestScope:
    __slots__ = ('core', 'year', 'execute')

    def __init__(self):
        self.core = {}
        self.year = {}
        self.execute = {}


_REQUEST_SCOPE = contextvars.ContextVar(
    'unified_compute_request_scope', default=None)


def _current_caches():
    """当前生效的三层缓存：作用域内为作用域自有缓存，否则为模块级缓存。"""
    scope = _REQUEST_SCOPE.get()
    if scope is None:
        return _CORE_CACHE, _YEAR_CACHE, _EXECUTE_CACHE
    return scope.core, scope.year, scope.execute


class unified_compute_request_scope:
    """一次请求的缓存作用域（context manager）。

    进入时为本次请求新建三份空缓存（出生层 / 目标年层 / execute
    去重层），作用域内的装配与 ``cached_execute`` 只读写这三份；
    退出时（正常返回或异常）三份缓存全部清空，出生瞬时与完整
    计算结果不保留，作用域外的调用者看不到作用域内的任何条目。
    嵌套进入时内层是全新的空缓存，退出只清空内层并恢复外层。
    不同线程 / asyncio 任务各自持有自己的 contextvars 上下文，
    因此并发请求天然隔离：一个请求的出生数据永不进入另一个
    请求的缓存。

    生产请求路径必须在请求边界进入本作用域；未进入作用域的直接
    调用沿用模块级缓存（兼容 fallback，仅供测试与离线脚本使用，
    不得用于多用户服务）。进入作用域返回该作用域对象（测试可用
    它断言退出后三份缓存均已清空）。
    """

    def __enter__(self):
        self._scope = _RequestScope()
        self._token = _REQUEST_SCOPE.set(self._scope)
        return self._scope

    def __exit__(self, exc_type, exc, tb):
        try:
            self._scope.core.clear()
            self._scope.year.clear()
            self._scope.execute.clear()
        finally:
            _REQUEST_SCOPE.reset(self._token)
        return False


def unified_compute_request_scope_active():
    """当前上下文是否处于一次请求作用域内（生命周期可观测性）。"""
    return _REQUEST_SCOPE.get() is not None


class UnifiedComputePinError(ValueError):
    """引擎输出变体漂移：调用方不得吞掉，必须 loud 失败。"""


class UnifiedComputeInputError(ValueError):
    """入口输入校验失败（出生瞬时 / 目标年 / 传统口径形态非法）。"""


def clear_unified_compute_cache():
    """清空当前生效的全部三层缓存（测试隔离用；不碰任何引擎状态）。

    作用域内只清空该作用域的缓存，作用域外的缓存不受影响；
    作用域外清空模块级缓存。
    """
    core, year, execute = _current_caches()
    core.clear()
    year.clear()
    execute.clear()


# 失效维度哨兵：invalidate 调用中 traditional_role / target_year
# 取此值表示“不限定该维度”，与显式传入 None（只匹配 None）区分。
_ANY_DIMENSION = object()


def unified_compute_cache_info():
    """报告当前生效的三层缓存的条数与上限（生命周期可观测性；只读）。

    作用域内报告该作用域的条数，作用域外报告模块级缓存的条数。
    """
    core, year, execute = _current_caches()
    return {
        'core_entries': len(core),
        'year_entries': len(year),
        'execute_entries': len(execute),
        'max_entries_per_cache': _CACHE_MAX_ENTRIES,
        'max_entries_total': 3 * _CACHE_MAX_ENTRIES,
    }


def invalidate_unified_compute_cache(birth_value, *, zone=None,
                                     traditional_role=_ANY_DIMENSION,
                                     target_year=_ANY_DIMENSION):
    """按 key 失效当前生效缓存中一个出生瞬时的条目；返回实际删除的条数。

    作用域内只失效该作用域的条目，作用域外失效模块级缓存的条目。
    删除：出生层 ``(birth_value, zone)`` 条目；该出生 / 时区下的
    目标年层条目（``traditional_role`` / ``target_year`` 未给定时
    不限定该维度，即删除该出生 / 时区下的全部目标年层条目；显式
    传入 None 时只匹配该维度为 None 的条目）；以及 ``execute``
    去重层中 natal 输入 ``value`` 为该出生瞬时的条目（``zone``
    给定时还须 ``zone`` 匹配）。不存在的 key 计 0，不报错。
    输入非法（出生瞬时形状）时 raise
    :class:`UnifiedComputeInputError`，不静默跳过。
    """
    _validate_birth_value(birth_value)
    removed = 0
    core_cache, year_cache, execute_cache = _current_caches()
    core_key = _canonical_key([birth_value, zone])
    if core_key is not None and core_key in core_cache:
        del core_cache[core_key]
        removed += 1
    for key in list(year_cache):
        try:
            parts = json.loads(key)
        except ValueError:
            continue
        if not isinstance(parts, list) or len(parts) != 4:
            continue
        if parts[0] != birth_value or parts[1] != zone:
            continue
        if traditional_role is not _ANY_DIMENSION \
                and parts[2] != traditional_role:
            continue
        if target_year is not _ANY_DIMENSION \
                and parts[3] != target_year:
            continue
        del year_cache[key]
        removed += 1
    for key in list(execute_cache):
        try:
            parts = json.loads(key)
        except ValueError:
            continue
        if not isinstance(parts, list) or len(parts) != 3:
            continue
        inputs = parts[1]
        if not isinstance(inputs, dict):
            continue
        if inputs.get('value') != birth_value:
            continue
        if zone is not None and inputs.get('zone') != zone:
            continue
        del execute_cache[key]
        removed += 1
    return removed


def _canonical_key(payload):
    """payload 的 canonical JSON key；不可序列化时返回 None（不缓存）。"""
    try:
        return json.dumps(payload, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        return None


def _cache_put(cache, key, value):
    if key is None:
        return
    if key in cache:
        cache[key] = copy.deepcopy(value)
        return
    while len(cache) >= _CACHE_MAX_ENTRIES:
        cache.pop(next(iter(cache)))
    cache[key] = copy.deepcopy(value)


def cached_execute(domain, inputs, allow_research=False):
    """``engine.execute`` 的去重包装：同一输入只执行一次，返回深拷贝。

    与直接 ``execute`` 逐值相等：缓存存 pristine 深拷贝，每次返回的
    都是新的深拷贝，调用方对返回值的原地修改（如
    ``_bazi_profile`` 对 ``result["production_scope"]`` 的恢复）永不
    污染缓存。输入不可序列化或缓存本身异常时直接执行，不拖垮请求。
    """
    from .engine import execute

    key = _canonical_key([domain, inputs, allow_research])
    _, _, execute_cache = _current_caches()
    if key is not None and key in execute_cache:
        return copy.deepcopy(execute_cache[key])
    result = execute(domain, inputs, allow_research=allow_research)
    _cache_put(execute_cache, key, result)
    return copy.deepcopy(result)


# ---------------------------------------------------------------------------
# 输入校验
# ---------------------------------------------------------------------------

def _validate_birth_value(birth_value):
    if not isinstance(birth_value, str) or not birth_value:
        raise UnifiedComputeInputError(
            'birth_value must be a non-empty ISO datetime string')
    # 形状校验：时区感知、整秒（与司令试点 / 排盘路径同一口径）；
    # 历法有效性由排盘执行本身 fail-closed。
    from datetime import datetime as _datetime

    try:
        parsed = _datetime.fromisoformat(birth_value)
    except ValueError:
        raise UnifiedComputeInputError(
            'birth_value is not a parseable ISO datetime string')
    if parsed.tzinfo is None:
        raise UnifiedComputeInputError(
            'birth_value must carry a timezone offset')
    if parsed.microsecond != 0:
        raise UnifiedComputeInputError(
            'birth_value must be at whole-second precision')
    return birth_value


def _validate_target_year(target_year):
    if target_year is None:
        return None
    if type(target_year) is not int or not 1900 <= target_year <= 2100:
        raise UnifiedComputeInputError(
            'target_year must be an integer from 1900 through 2100')
    return target_year


def _validate_traditional_role(traditional_role):
    if traditional_role is not None \
            and traditional_role not in ('male', 'female'):
        raise UnifiedComputeInputError(
            'traditional_role must be male or female')
    return traditional_role


# ---------------------------------------------------------------------------
# 变体 pin 校验
# ---------------------------------------------------------------------------

def _check_pin(block, expected, label):
    if not isinstance(block, dict):
        raise UnifiedComputePinError(
            '%s output is not an object (expected variant %s)'
            % (label, expected))
    if block.get('variant') != expected:
        raise UnifiedComputePinError(
            '%s variant drifted: %r != %r'
            % (label, block.get('variant'), expected))


def _check_research_flags(block, label):
    if block.get('research_only') is not True \
            or block.get('public_enabled') is not False \
            or block.get('ai_enabled') is not False:
        raise UnifiedComputePinError(
            '%s research flags drifted (research_only must be True, '
            'public_enabled/ai_enabled must be False)' % label)


def validate_engine_pins(*, strength=None, pattern=None, xiyong=None,
                         combination=None):
    """校验一批引擎输出的变体 pin 与研究旗标；漂移即 raise（loud）。

    只做校验，不改任何输出。未传入的体系跳过（该体系未装配）。
    """
    if strength is not None:
        _check_pin(strength, PIN_STRENGTH_ENGINE_VARIANT, 'strength')
        _check_research_flags(strength, 'strength')
    if pattern is not None:
        _check_pin(pattern, PIN_PATTERN_ENGINE_VARIANT, 'pattern')
        _check_research_flags(pattern, 'pattern')
    if xiyong is not None:
        _check_pin(xiyong, PIN_XIYONG_ENGINE_VARIANT, 'xiyong')
        _check_research_flags(xiyong, 'xiyong')
    if combination is not None:
        _check_pin(combination, PIN_COMBINATION_ENGINE_VARIANT,
                   'combination')
        _check_research_flags(combination, 'combination')
    return True


# ---------------------------------------------------------------------------
# 司令试点：只透传同一出生瞬时实算的试点，永不合成
# ---------------------------------------------------------------------------

def _jie_facts(birth_value, *, first_term, next_term, first_key,
               next_key, first_window, next_window):
    """Provider 核验的 Jie 窗口声明（与 ``_strength_jie_facts`` 同形）。

    两个节气瞬时均取自钉定 provider 的年度 Jie 表；调用方试点会逐秒
    回放核对，声明本身不是事实。provider 身份 / 解析 / 窗口异常即
    raise ValueError（fail-closed），永不吞成 pilot=None。
    """
    from datetime import datetime as _datetime
    from zoneinfo import ZoneInfo as _ZoneInfo

    from lunar_python import Solar as _Solar

    from .calendar_provider_guard import (
        PINNED_PROVIDER_NAME as _PROVIDER_NAME,
        PINNED_PROVIDER_VERSION as _PROVIDER_VERSION,
        provider_identity as _provider_identity,
    )

    _provider_identity()
    birth = _datetime.fromisoformat(birth_value)
    table = _Solar.fromYmd(birth.year, 7, 1).getLunar().getJieQiTable()

    def _instant(term_name):
        term = table[term_name]
        instant = _datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
        return instant.replace(tzinfo=_ZoneInfo('Asia/Shanghai'))

    first = _instant(first_term)
    following = _instant(next_term)
    if first.year != birth.year or first.month != first_window[0] \
            or not first_window[1] <= first.day <= first_window[2]:
        raise ValueError('%s outside the expected window' % first_term)
    if following.year != birth.year or following.month != next_window[0] \
            or not next_window[1] <= following.day <= next_window[2]:
        raise ValueError('%s outside the expected window' % next_term)
    return {
        'provider': {'name': _PROVIDER_NAME, 'version': _PROVIDER_VERSION,
                     'identity_verified': True},
        first_key: {'term': first_term, 'at': first.isoformat(),
                    'precision': 'second'},
        next_key: {'term': next_term, 'at': following.isoformat(),
                   'precision': 'second'},
    }


def _live_pilot(birth_value, month_branch):
    """为同一出生瞬时实算司令试点；返回 (pilot, note)。

    只在 寅月 / 巳月 运行对应的已批试点；其余月份返回
    ``(None, 'month_not_piloted')``。试点返回非 computed 状态或
    出生形状被拒（ValueError）时返回 ``(None, reason)``：对应谓词恒
    不点火（fail-closed），调用方不得以此为由合成试点。
    """
    if month_branch == '寅':
        from .bazi_siling_pilot import yin_siling_pilot

        try:
            jie_facts = _jie_facts(
                birth_value, first_term='立春', next_term='惊蛰',
                first_key='lichun', next_key='next_jie',
                first_window=(2, 2, 6), next_window=(3, 5, 7))
            pilot = yin_siling_pilot(
                birth_value, version_id=PIN_SILING_YIN_VERSION_ID,
                jie_facts=jie_facts)
        except ValueError as exc:
            return None, 'yin_pilot_uncomputable: %s' % exc
        if not isinstance(pilot, dict):
            return None, 'yin_pilot_malformed'
        if pilot.get('variant') != PIN_SILING_YIN_VARIANT:
            return None, 'yin_pilot_variant_mismatch'
        if pilot.get('status') != 'computed':
            return None, 'yin_pilot_%s' % pilot.get('status')
        if pilot.get('month_branch') != '寅' \
                or pilot.get('scope_month_branch') != '寅':
            return None, 'yin_pilot_month_mismatch'
        return pilot, 'yin_pilot_computed'
    if month_branch == '巳':
        from .bazi_siling_si_pilot import si_siling_pilot

        try:
            jie_facts = _jie_facts(
                birth_value, first_term='立夏', next_term='小满',
                first_key='lixia', next_key='next_jie',
                first_window=(5, 5, 7), next_window=(5, 20, 22))
            pilot = si_siling_pilot(
                birth_value, version_id=PIN_SILING_SI_VERSION_ID,
                jie_facts=jie_facts)
        except ValueError as exc:
            return None, 'si_pilot_uncomputable: %s' % exc
        if not isinstance(pilot, dict):
            return None, 'si_pilot_malformed'
        if pilot.get('variant') != PIN_SILING_SI_VARIANT:
            return None, 'si_pilot_variant_mismatch'
        if pilot.get('status') != 'computed':
            return None, 'si_pilot_%s' % pilot.get('status')
        if pilot.get('month_branch') != '巳' \
                and pilot.get('scope_month_branch') != '巳':
            return None, 'si_pilot_month_mismatch'
        return pilot, 'si_pilot_computed'
    return None, 'month_not_piloted'


# ---------------------------------------------------------------------------
# 装配
# ---------------------------------------------------------------------------

def _canonical_natal_inputs(birth_value, zone):
    """标准排盘输入：与 _romance / _compatibility 已在用的组合相同。"""
    natal_input = {'value': birth_value, 'include_relations': True,
                   'include_xianchi': True}
    if zone is not None:
        natal_input['zone'] = zone
    return natal_input


def _assemble_birth_core(birth_value, zone):
    """出生层装配（缓存单位）：一次排盘 + 强度 / 格局 / 喜用（无流年）。

    返回的 core 含 ``chart``（pillars / day_master / month_branch /
    natal_envelope）与 ``research``（strength / pattern / xiyong /
    tiaohou / bingyao / pilots / errors）。研究引擎故障只记入
    ``research['errors']``，对应块为 None；pin 漂移 raise
    :class:`UnifiedComputePinError`；标准排盘本身失败则 raise，
    由调用方决定是否降级为无装配页（公开输出永不因此改变）。
    """
    _validate_birth_value(birth_value)
    core_cache, _, _ = _current_caches()
    key = _canonical_key([birth_value, zone])
    if key is not None and key in core_cache:
        return copy.deepcopy(core_cache[key])

    from .bazi_bingyao import bingyao_lookup
    from .bazi_pattern_engine import evaluate_all
    from .bazi_strength_engine import assess_strength
    from .bazi_tiaohou import tiaohou_lookup
    from .bazi_xiyong_engine import evaluate_xiyong

    natal = cached_execute(
        'bazi', _canonical_natal_inputs(birth_value, zone))
    result = natal['result']
    pillars = result['pillars']
    day_master = result['day_master']['stem'] \
        if isinstance(result['day_master'], dict) \
        else result['day_master']
    month_branch = pillars[1]['branch']['value']
    errors = []

    yin_pilot = si_pilot = None
    pilot, pilot_note = _live_pilot(birth_value, month_branch)
    if month_branch == '寅':
        yin_pilot = pilot
    elif month_branch == '巳':
        si_pilot = pilot
    pilots = {'yin_pilot': yin_pilot, 'si_pilot': si_pilot,
              'note': pilot_note}

    strength = pattern = xiyong = tiaohou = bingyao = None
    try:
        strength = assess_strength(
            pillars, day_master,
            siling_yin_pilot=yin_pilot, siling_si_pilot=si_pilot)
    except Exception as exc:  # noqa: BLE001 - 研究故障只记，不拖垮装配
        errors.append({'block': 'strength', 'reason': str(exc)[:300]})
    try:
        # D-1 不在此重推（见模块 docstring）：evaluate_all 只出候选 /
        # 现代层 / 缺口登记；D-1 仍走 ren_yin_research_execution。
        pattern = evaluate_all({'pillars': pillars,
                                'day_master': result['day_master']})
    except Exception as exc:  # noqa: BLE001 - 研究故障只记，不拖垮装配
        errors.append({'block': 'pattern', 'reason': str(exc)[:300]})
    try:
        visible_stems = [p['stem']['value'] for p in pillars]
        hidden_stems = [[h['stem'] for h in p['branch']['hidden_stems']]
                        for p in pillars]
        tiaohou = tiaohou_lookup(day_master, month_branch,
                                 visible_stems, hidden_stems)
        visible_gods = [
            {'pillar': name, 'stem': pillars[i]['stem']['value'],
             'ten_god': pillars[i]['stem']['ten_god']}
            for i, name in ((0, 'year'), (1, 'month'), (3, 'hour'))]
        bingyao = bingyao_lookup(day_master, visible_gods)
    except Exception as exc:  # noqa: BLE001 - 研究故障只记，不拖垮装配
        errors.append({'block': 'tiaohou_bingyao',
                       'reason': str(exc)[:300]})
    try:
        xiyong = evaluate_xiyong(
            day_master=day_master, month_branch=month_branch,
            pillars=[p['ganzhi'] for p in pillars],
            strength=strength, tiaohou=tiaohou, bingyao=bingyao,
            pattern=pattern, flow_year=None)
    except Exception as exc:  # noqa: BLE001 - 研究故障只记，不拖垮装配
        errors.append({'block': 'xiyong', 'reason': str(exc)[:300]})

    # Pin 校验：漂移即 loud 失败（调用方不得吞掉）。
    validate_engine_pins(strength=strength, pattern=pattern,
                         xiyong=xiyong)

    core = {
        'variant': UNIFIED_COMPUTE_VARIANT,
        'birth_value': birth_value,
        'zone': zone,
        'research_only': RESEARCH_ONLY,
        'public_enabled': PUBLIC_ENABLED,
        'ai_enabled': AI_ENABLED,
        'chart': {
            'pillars': copy.deepcopy(pillars),
            'day_master': copy.deepcopy(result['day_master']),
            'month_branch': month_branch,
            'ganzhi': [p['ganzhi'] for p in pillars],
        },
        'natal_envelope': copy.deepcopy(natal),
        'research': {
            'strength': strength,
            'pattern': pattern,
            'pattern_d1': {
                'attempted': False,
                'status': 'not_attempted_here',
                'reason': ('D-1 任氏寅月真格只走 '
                           'scenario_engine.ren_yin_research_execution；'
                           '本入口不重推 D-1，格局块只含候选 / 现代层 / '
                           '破格缺口登记。'),
            },
            'xiyong': xiyong,
            'tiaohou': tiaohou,
            'bingyao': bingyao,
            'pilots': pilots,
            'errors': errors,
        },
    }
    _cache_put(core_cache, key, core)
    return copy.deepcopy(core)


def _assemble_year_layer(core, *, traditional_role, target_year):
    """目标年层装配（缓存单位）：大运 + 流年 + 年度喜用 + 组合。

    大运（Q3=A，2026-11-28）：显式传统口径给出时即装配完整的
    8 运序列（``classical_dayun_timeline(periods=8)`` 的同一组合，
    与 ``_dayun_public_gate`` 同一套 server-fixed 常量），不依赖
    目标年——八字页无目标年也要能拿到 8 运数据；无口径时记为
    未装配并具名原因，口径永不推断。流年查询数据：目标年干支
    （``flow_year``）+ 该年的立春边界区间（``flow_boundary``，
    ``annual_lichun_boundaries`` 原样输出，只作查询与对照，不产
    生任何推断）。组合只在传统口径与目标年同时给出时装配；当期
    运未显式指定时记未确定（D-02），不推导期位——本入口只提供
    8 运序列与流年边界供调用方查询，永不自行判定当期运。
    任一步骤失败只记入 ``errors``，对应块为 None，不拖垮其余层；
    组合 pin 漂移仍 raise（调用方不得吞掉）。
    """
    birth_value = core['birth_value']
    zone = core['zone']
    _, year_cache, _ = _current_caches()
    key = _canonical_key([birth_value, zone, traditional_role,
                          target_year])
    if key is not None and key in year_cache:
        return copy.deepcopy(year_cache[key])

    from .bazi_core import ten_god
    from .calendar import calendar

    day_master = core['chart']['day_master']['stem'] \
        if isinstance(core['chart']['day_master'], dict) \
        else core['chart']['day_master']
    # 深拷贝：年层 errors 条目不得与出生层装配共享同一 dict 对象，
    # 否则一次请求的 errors 原地修改会透过共享对象污染另一层缓存。
    errors = copy.deepcopy(core['research']['errors'])

    # 大运 8 运序列：只认显式传统口径，与目标年无关。
    dayun = None
    dayun_note = None
    if traditional_role is not None:
        try:
            from .bazi_dayun_compose import classical_dayun_timeline

            timeline = classical_dayun_timeline(
                birth_value, zone=zone,
                traditional_role=traditional_role, periods=8,
                birth_time_precision='second', include_shenfeng=True)
            if timeline.get('status') != 'converted':
                dayun_note = ('dayun_timeline_unresolved: %s'
                              % timeline.get('reason'))
                errors.append({'block': 'dayun', 'reason': dayun_note})
            else:
                dayun = {
                    'status': 'assembled',
                    'periods': 8,
                    'traditional_role': traditional_role,
                    'timeline': copy.deepcopy(timeline),
                }
        except Exception as exc:  # noqa: BLE001 - 只记，不拖垮装配
            dayun_note = 'dayun_uncomputable: %s' % str(exc)[:300]
            errors.append({'block': 'dayun', 'reason': dayun_note})
    else:
        dayun_note = (
            'traditional_role_not_given: no dayun direction, '
            '8-period sequence not assembled')

    # 流年边界区间：只认目标年，与口径无关；失败只记，不拖垮流年。
    flow_boundary = None
    flow_boundary_error = None
    if target_year is not None:
        try:
            from .bazi_annual_reference import \
                annual_lichun_boundaries

            flow_boundary = annual_lichun_boundaries(
                day_master, [target_year])
        except Exception as exc:  # noqa: BLE001 - 只记，不拖垮装配
            flow_boundary_error = str(exc)[:300]
            errors.append({'block': 'flow_boundary',
                           'reason': flow_boundary_error})

    flow_year = None
    annual_xiyong = None
    combination = None
    combination_note = None
    if target_year is not None:
        reference = '%04d-07-01T12:00:00+08:00' % target_year
        target_calendar = calendar(reference)
        flow_ganzhi = target_calendar['year_ganzhi']
        flow_year = {
            'year': target_year,
            'ganzhi': flow_ganzhi,
            'stem': flow_ganzhi[0],
            'branch': flow_ganzhi[1],
            'stem_ten_god': ten_god(day_master, flow_ganzhi[0]),
            'calendar_provider': target_calendar['calendar_provider'],
            'year_boundary': ('solar-term year; reference date fixed to '
                              'July 1 for stable annual stem/branch '
                              'selection'),
        }
        try:
            from .bazi_xiyong_engine import evaluate_annual_xiyong

            annual_xiyong = evaluate_annual_xiyong(
                core['research']['xiyong']['systems'], target_year,
                day_master=day_master) \
                if core['research']['xiyong'] is not None else None
        except Exception as exc:  # noqa: BLE001 - 只记，不拖垮装配
            errors.append({'block': 'annual_xiyong',
                           'reason': str(exc)[:300]})
        if traditional_role is not None:
            try:
                from .bazi_combination_engine import combine

                if dayun is None:
                    errors.append({
                        'block': 'combination',
                        'reason': 'dayun_unavailable: %s' % dayun_note})
                elif flow_boundary is None:
                    errors.append({
                        'block': 'combination',
                        'reason': 'flow_boundary_unavailable: %s'
                                  % flow_boundary_error})
                else:
                    dayun_rows = dayun['timeline']['sequence']['rows']
                    combination = combine(
                        core['chart']['pillars'], day_master, dayun_rows,
                        target_year,
                        strength=core['research']['strength'],
                        tiaohou=core['research']['tiaohou'],
                        bingyao=core['research']['bingyao'],
                        pattern=core['research']['pattern'],
                        xiyong=core['research']['xiyong'],
                        flow_boundary=flow_boundary)
                    validate_engine_pins(combination=combination)
            except UnifiedComputePinError:
                raise
            except Exception as exc:  # noqa: BLE001 - 只记，不拖垮装配
                errors.append({'block': 'combination',
                               'reason': str(exc)[:300]})
        else:
            combination_note = (
                'traditional_role_not_given: no dayun direction, '
                'combination not assembled')
    else:
        combination_note = (
            'target_year_not_given: combination needs a flow year')

    layer = {
        'target_year': target_year,
        'traditional_role': traditional_role,
        'dayun': dayun,
        'dayun_status': (
            'assembled' if dayun is not None else 'not_assembled'),
        'dayun_note': dayun_note,
        'flow_year': flow_year,
        'flow_boundary': flow_boundary,
        'annual_xiyong': annual_xiyong,
        'combination': combination,
        'combination_status': (
            'assembled' if combination is not None else 'not_assembled'),
        'combination_note': combination_note,
        'errors': errors,
    }
    _cache_put(year_cache, key, layer)
    return copy.deepcopy(layer)


def assemble_birth(birth_value, *, zone=None, traditional_role=None,
                   target_year=None):
    """装配一个出生瞬时的统一内部计算入口。

    一次标准排盘（出生层缓存）+ 研究引擎实算 + 目标年层。返回的
    assembly 全程 research_only；公开 presentation 仍由各页门控
    另行构建，本函数永不输出公开对象。
    """
    _validate_birth_value(birth_value)
    _validate_traditional_role(traditional_role)
    _validate_target_year(target_year)
    core = _assemble_birth_core(birth_value, zone)
    layer = _assemble_year_layer(core, traditional_role=traditional_role,
                                 target_year=target_year)
    assembly = copy.deepcopy(core)
    assembly['traditional_role'] = traditional_role
    assembly['target_year'] = target_year
    assembly['dayun'] = layer['dayun']
    assembly['dayun_status'] = layer['dayun_status']
    assembly['flow_year'] = layer['flow_year']
    assembly['flow_boundary'] = layer['flow_boundary']
    assembly['annual_xiyong'] = layer['annual_xiyong']
    assembly['combination'] = layer['combination']
    assembly['combination_status'] = layer['combination_status']
    assembly['combination_note'] = layer['combination_note']
    assembly['research'] = copy.deepcopy(core['research'])
    assembly['research']['errors'] = layer['errors']
    return assembly


def assemble_pair(birth_value_a, birth_value_b, *, zone_a=None,
                  zone_b=None):
    """合盘用的双人装配：两人各一份出生层装配，无单瞬时主张。"""
    return {
        'variant': UNIFIED_COMPUTE_VARIANT,
        'research_only': RESEARCH_ONLY,
        'public_enabled': PUBLIC_ENABLED,
        'ai_enabled': AI_ENABLED,
        'person_a': assemble_birth(birth_value_a, zone=zone_a),
        'person_b': assemble_birth(birth_value_b, zone=zone_b),
    }


# ---------------------------------------------------------------------------
# 各页裁剪（allowlist：只输出各页所需字段，不多输出）
# ---------------------------------------------------------------------------

def _chart_trim(assembly):
    return {
        'birth_value': assembly['birth_value'],
        'zone': assembly['zone'],
        'pillars': copy.deepcopy(assembly['chart']['pillars']),
        'day_master': copy.deepcopy(assembly['chart']['day_master']),
        'month_branch': assembly['chart']['month_branch'],
        'ganzhi': list(assembly['chart']['ganzhi']),
    }


def _research_trim(assembly):
    """研究块裁剪：原样研究输出 + 隔离声明，永不混入公开字段。"""
    return {
        'strength': copy.deepcopy(assembly['research']['strength']),
        'pattern': copy.deepcopy(assembly['research']['pattern']),
        'pattern_d1': copy.deepcopy(assembly['research']['pattern_d1']),
        'xiyong': copy.deepcopy(assembly['research']['xiyong']),
        'annual_xiyong': copy.deepcopy(assembly.get('annual_xiyong')),
        'combination': copy.deepcopy(assembly.get('combination')),
        'combination_status': assembly.get('combination_status'),
        'combination_note': assembly.get('combination_note'),
        'pilots': copy.deepcopy(assembly['research']['pilots']),
        'errors': copy.deepcopy(assembly['research']['errors']),
        'research_only': True,
        'public_enabled': False,
        'ai_enabled': False,
    }


def _base_trim(assembly, page):
    return {
        'variant': UNIFIED_COMPUTE_VARIANT,
        'page': page,
        'research_only': RESEARCH_ONLY,
        'public_enabled': PUBLIC_ENABLED,
        'ai_enabled': AI_ENABLED,
        'chart': _chart_trim(assembly),
        'research': _research_trim(assembly),
    }


def trim_for_bazi_profile(assembly):
    """bazi-profile 所需字段：排盘 + 强度 / 格局 / 喜用研究块 + 大运。

    大运（Q3=A）：口径给出时含完整 8 运序列（``dayun``），无口径
    时为 None；不含 target_year / flow_year / combination（本页
    无流年）。公开 presentation（strength / pattern / dayun /
    xiyong 四门控）不在本裁剪内，由各门控另行构建。
    """
    trim = _base_trim(assembly, 'bazi-profile')
    trim['dayun'] = copy.deepcopy(assembly.get('dayun'))
    trim['dayun_status'] = assembly.get('dayun_status')
    return trim


def trim_for_career(assembly):
    """career 所需字段：排盘 + 研究块 + 大运 + 流年 + 组合。"""
    trim = _base_trim(assembly, 'career')
    trim['target_year'] = assembly['target_year']
    trim['dayun'] = copy.deepcopy(assembly.get('dayun'))
    trim['dayun_status'] = assembly.get('dayun_status')
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
    trim['flow_boundary'] = copy.deepcopy(assembly.get('flow_boundary'))
    return trim


def trim_for_romance(assembly):
    """romance 所需字段：排盘 + 研究块 + 流年（含流年边界查询数据）。"""
    trim = _base_trim(assembly, 'romance')
    trim['target_year'] = assembly['target_year']
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
    trim['flow_boundary'] = copy.deepcopy(assembly.get('flow_boundary'))
    return trim


def trim_for_life(assembly):
    """life 所需字段：排盘 + 研究块 + 大运 + 流年 + 组合 + 四源一致性锚点。"""
    trim = _base_trim(assembly, 'life')
    trim['target_year'] = assembly['target_year']
    trim['dayun'] = copy.deepcopy(assembly.get('dayun'))
    trim['dayun_status'] = assembly.get('dayun_status')
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
    trim['flow_boundary'] = copy.deepcopy(assembly.get('flow_boundary'))
    trim['identity_anchor'] = {
        'pillars': copy.deepcopy(assembly['chart']['pillars']),
        'day_master': copy.deepcopy(assembly['chart']['day_master']),
        'target_year': assembly['target_year'],
        'target_ganzhi': (assembly['flow_year']['ganzhi']
                          if assembly.get('flow_year') else None),
        'target_branch': (assembly['flow_year']['branch']
                          if assembly.get('flow_year') else None),
    }
    return trim


def trim_for_compatibility(pair_assembly):
    """compatibility 所需字段：两人排盘 + 各自研究块（无单瞬时流年）。"""
    return {
        'variant': UNIFIED_COMPUTE_VARIANT,
        'page': 'compatibility',
        'research_only': RESEARCH_ONLY,
        'public_enabled': PUBLIC_ENABLED,
        'ai_enabled': AI_ENABLED,
        'person_a': _base_trim(pair_assembly['person_a'],
                               'compatibility-person-a'),
        'person_b': _base_trim(pair_assembly['person_b'],
                               'compatibility-person-b'),
    }


# ---------------------------------------------------------------------------
# 正式投影（TJ-0427 Lane G）：装配 → 公开安全视图的唯一显式投影
# ---------------------------------------------------------------------------
# allowlist：正式视图只含这三组字段。排盘四柱与流年干支是结构事实；
# ``stem_ten_god`` 是流年干与日主的十神结构事实（与四柱十神同类），
# 不是任何引擎的 verdict。以下字段一律排除（即使装配里有）：
# 全部研究输出、``traditional_role``（输入口径，不属计算事实）、
# ``variant``（研究入口变体）、``identity_anchor``（裁剪 artifact）、
# ``calendar_provider`` / ``year_boundary``（流年层内部口径说明）。
FORMAL_PROJECTION_TOP_KEYS = frozenset(
    ('birth_value', 'zone', 'target_year', 'chart', 'flow_year'))
FORMAL_PROJECTION_CHART_KEYS = frozenset(
    ('pillars', 'day_master', 'month_branch', 'ganzhi'))
FORMAL_PROJECTION_FLOW_YEAR_KEYS = frozenset(
    ('year', 'ganzhi', 'stem', 'branch', 'stem_ten_god'))

# 研究字段名全集：正式投影中任何位置都不得出现。来源：研究块裁剪
# （``_research_trim`` 的全部输出键）+ 装配 ``research`` 字典的其余
# 键（``tiaohou`` / ``bingyao`` 不在裁剪内，但仍是研究输出）+
# 装配容器（``research`` / ``natal_envelope``）+ 内部装配专属字段
# （``dayun`` / ``dayun_status`` / ``flow_boundary``：其源模块自带
# ``research_only=True``，只在内部装配与裁剪内流通，永不投影）+
# 公开 presentation 键（本入口永不产生，列入是纵深防御：投影一旦
# 误含即被测试捕获）。
RESEARCH_FIELD_NAMES = frozenset((
    'strength', 'pattern', 'pattern_d1', 'xiyong', 'annual_xiyong',
    'combination', 'combination_status', 'combination_note', 'pilots',
    'errors', 'tiaohou', 'bingyao', 'research_only', 'public_enabled',
    'ai_enabled', 'research', 'natal_envelope',
    'dayun', 'dayun_status', 'flow_boundary',
    'strength_presentation', 'pattern_presentation',
    'dayun_presentation', 'xiyong_presentation',
))


def project_formal(assembly):
    """从研究装配投影出正式（公开安全）视图。

    只输出 allowlist 字段（见 ``FORMAL_PROJECTION_*_KEYS``），返回
    全深拷贝；研究字段永不进入。本函数不产生公开 presentation
    对象——公开面仍只走既有四门控；它只回答“装配里哪些事实是
    公开安全的”。装配形状非法（缺 ``chart`` / 四柱字段 / 流年
    干支）时 raise :class:`UnifiedComputeInputError`（fail-closed，
    不返回残缺视图）。
    """
    if not isinstance(assembly, dict):
        raise UnifiedComputeInputError(
            'project_formal needs an assembly object')
    chart = assembly.get('chart')
    if not isinstance(chart, dict):
        raise UnifiedComputeInputError(
            'project_formal needs an assembly with a chart')
    for key in ('pillars', 'day_master', 'month_branch', 'ganzhi'):
        if key not in chart:
            raise UnifiedComputeInputError(
                'project_formal: chart is missing %r' % key)
    birth_value = assembly.get('birth_value')
    if birth_value is None:
        raise UnifiedComputeInputError(
            'project_formal: assembly is missing birth_value')
    _validate_birth_value(birth_value)
    flow = assembly.get('flow_year')
    flow_view = None
    if flow is not None:
        if not isinstance(flow, dict) or 'ganzhi' not in flow \
                or 'year' not in flow:
            raise UnifiedComputeInputError(
                'project_formal: flow_year is missing year/ganzhi')
        flow_view = {
            key: copy.deepcopy(flow[key])
            for key in FORMAL_PROJECTION_FLOW_YEAR_KEYS if key in flow}
    return {
        'birth_value': birth_value,
        'zone': assembly.get('zone'),
        'target_year': assembly.get('target_year'),
        'chart': {
            key: copy.deepcopy(chart[key])
            for key in FORMAL_PROJECTION_CHART_KEYS},
        'flow_year': flow_view,
    }


def project_formal_pair(pair_assembly):
    """合盘装配的正式投影：两人各一份 :func:`project_formal`。"""
    if not isinstance(pair_assembly, dict):
        raise UnifiedComputeInputError(
            'project_formal_pair needs a pair assembly object')
    for key in ('person_a', 'person_b'):
        if key not in pair_assembly:
            raise UnifiedComputeInputError(
                'project_formal_pair: pair assembly is missing %r' % key)
    return {
        'person_a': project_formal(pair_assembly['person_a']),
        'person_b': project_formal(pair_assembly['person_b']),
    }


# ---------------------------------------------------------------------------
# U-02：逐页标注（可接推理输出 / 仍只结构事实）
# ---------------------------------------------------------------------------

PAGE_ANNOTATIONS = {
    'bazi-profile': {
        'page': 'bazi-profile',
        'attached_research': [
            'U1 最小公开旺衰（strength-public-presentation-v1）',
            'D-1 白名单格局（8 格名；比肩 / 劫财 → not_judgeable）',
            '大运 8 运时间轴（两口径并列，区间口径）',
            '喜用 phase-1（调候 + 病药；unified_verdict 恒 None）',
        ],
        'structure_only': [
            '强度现代模型（strength_model_modern_v1）',
            '格局现代层（pattern-modern-p6-v1）',
            '扶抑现代层（fuyi-modern-rules-v1）',
            '组合条件结论与跨层效力（overall_effect 恒 None）',
            '格局用神逐格规则（useful_god 恒 None）',
        ],
        'note': ('四门控已接；其余研究输出仍只研究，不接公开。'
                 '呈现扩展须另行提请晋升，本 lane 不提请。'),
    },
    'career': {
        'page': 'career',
        'attached_research': [
            '大运首运（first-period trim；2–8 运未展开）',
            '三份有限公开呈现（自 bazi-profile 同瞬时 lift：'
            'strength / xiyong / pattern）',
            '流年支结构（六合 / 六害 / 六冲；interpretation_allowed False）',
        ],
        'structure_only': [
            '旺衰分类、格局用神、组合效力、行业映射',
            '大运 2–8 运（#594 既定产品边界）',
        ],
        'note': '首运 + 三份 lift 呈现已接；其余推理仍只结构事实。',
    },
    'romance': {
        'page': 'romance',
        'attached_research': [],
        'structure_only': [
            '咸池目标支 / 原局命中 / 目标年激活（结构事实）',
            '夫妻宫日支配对（六合 / 六害 / 六冲）',
            '配偶星候选位置（传统口径显式选择时）',
            '未接入任何推理引擎输出（旺衰 / 格局 / 喜用 / 组合）',
        ],
        'note': '仍只结构事实；推理接入须另行提请晋升，本 lane 不提请。',
    },
    'compatibility': {
        'page': 'compatibility',
        'attached_research': [],
        'structure_only': [
            '双方日主互看十神 / 咸池交叉 / 五合 / 日支关系 / 三合 / 跨柱矩阵',
            '传统配偶星观察（传统口径显式选择时）',
            '未接入任何推理引擎输出；无适配度 / 缘分评分',
        ],
        'note': '仍只结构事实；推理接入须另行提请晋升，本 lane 不提请。',
    },
    'life': {
        'page': 'life',
        'attached_research': [
            '四份有限公开呈现（strength / xiyong / pattern / 首运 dayun）',
            'TJ-025.2 统一条件标记（按维度给条件标记，不产统一结论）',
            '四源一致性校验（同一 birth instant + 同一 target year）',
        ],
        'structure_only': [
            '跨层效力 / 统一结论（interpretation_allowed 恒 False）',
            '旺衰分类、格局用神、大运 2–8 运',
        ],
        'note': '有限呈现 + 条件标记已接；综合判断仍只结构事实。',
    },
}


def page_annotations():
    """逐页标注表的深拷贝（U-02；只作标注，不改变任何页的行为）。"""
    return copy.deepcopy(PAGE_ANNOTATIONS)


# ---------------------------------------------------------------------------
# U-03：晋升条件标注表（现状 + 晋升所需条件；不提议、不执行晋升）
# ---------------------------------------------------------------------------

PROMOTION_CONDITIONS = [
    {
        'capability': '强度现代模型（strength_model_modern_v1）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('权重 / 阈值正式化 + 用户裁定（正式权重 / '
                                '阈值变更属五类须裁定事项）；未裁定前现代结论'
                                '不得升格为古典结论。'),
        'promotion_proposed': False,
    },
    {
        'capability': '强度古典充分谓词（7 条因素层谓词 + F4）',
        'current_status': 'research_only',
        'public_surface': 'none（U1 最小公开旺衰除外，已开放）',
        'promotion_condition': ('逐条谓词获密封 Golden 准入 + 用户裁定'
                                '公开口径；F4 只认 寅月司令甲段。'),
        'promotion_proposed': False,
    },
    {
        'capability': '格局现代层（pattern-modern-p6-v1）',
        'current_status': 'research_only',
        'public_surface': 'none（D-1 白名单除外，已开放）',
        'promotion_condition': ('逐格现代评估获批公开口径 + 用户裁定；'
                                '现代旗标永不是古典 broken。'),
        'promotion_proposed': False,
    },
    {
        'capability': '格局成立 / 破格（D-1 之外各格）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('逐格成立 / 破格规则获独立 Golden + 用户'
                                '逐项裁定；比肩 / 劫财格公开须另行提请'
                                '白名单扩展。'),
        'promotion_proposed': False,
    },
    {
        'capability': '扶抑现代层（fuyi-modern-rules-v1）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('现代层获批公开口径 + 用户裁定；古典十行'
                                '零行可建（U3 Q1=B）永不重提。'),
        'promotion_proposed': False,
    },
    {
        'capability': '调候 / 病药 phase-2（乙木条目、未编码病药对）',
        'current_status': 'research_only',
        'public_surface': 'limited: phase-1（调候 + 病药）',
        'promotion_condition': ('新条目 / 新对子获来源取证 + Golden + '
                                '用户裁定 phase-2 口径。'),
        'promotion_proposed': False,
    },
    {
        'capability': '格局用神逐格规则（pattern_yongshen）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('逐格用神规则获证据审查 + 用户逐项批准；'
                                'unified_verdict 恒 None（TJ-013.2 A）不动。'),
        'promotion_proposed': False,
    },
    {
        'capability': '组合条件结论（8 种存在性 / 模型口径结论）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('逐条结论获批公开口径 + 用户裁定；存在性'
                                '不得写成效力断言。'),
        'promotion_proposed': False,
    },
    {
        'capability': '组合跨层效力（overall_effect；TJ-017.2 真定义）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('已审跨层效力规则逐条立项（须独立 Golden + '
                                '证据绑定）+ 用户裁定；M2 实质（TJ-013.2 '
                                '冲突裁决、扶抑 / 格局用神）为前置条件。'),
        'promotion_proposed': False,
    },
    {
        'capability': '六爻用神映射（8 类型；USEFUL_GOD_MAPPINGS 仍为 {}）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('逐类型映射证据包登记 + 用户逐项批准；'
                                '批准前 assess() 恒 abstain。'),
        'promotion_proposed': False,
    },
    {
        'capability': '六爻动爻 / 变爻效力、月破动静、应期',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('效力规则来源取证 + Golden + 用户裁定；'
                                '出空 / 填实 / 解破无依据，不建。'),
        'promotion_proposed': False,
    },
    {
        'capability': '分日司令单月试点（寅 / 巳之外 10 月）',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('用户逐月批复试点口径 + 计算约定 + Golden；'
                                '矩阵冲突并列不动。'),
        'promotion_proposed': False,
    },
    {
        'capability': '紫微大限 / 流年、奇门推断、六壬初传选择、周易占断、风水推断',
        'current_status': 'research_only',
        'public_surface': 'none',
        'promotion_condition': ('各引擎推断层来源取证 + Golden + 用户裁定；'
                                '证据等级（C/D）随输出携带，不得洗白。'),
        'promotion_proposed': False,
    },
    {
        'capability': '事业 / 总览页大运 2–8 运展开',
        'current_status': 'research_only',
        'public_surface': 'limited: first-period only',
        'promotion_condition': ('产品范围变更，用户决定是否展开；'
                                '不是引擎缺口，不属本次晋升表。'),
        'promotion_proposed': False,
    },
]


def promotion_conditions():
    """晋升条件标注表的深拷贝（U-03；只作标注，不提议、不执行晋升）。"""
    return copy.deepcopy(PROMOTION_CONDITIONS)
