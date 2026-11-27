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
* 流年：目标年干支取自与各页同一的 July-1 参考日历口径
  （``calendar(f"{year}-07-01T12:00:00+08:00")``），不另立边界。

变体 pin 校验：格局 v2 / 旺衰 v1 / 喜用 v1 / 组合契约 v1。任一输出
变体漂移即 raise :class:`UnifiedComputePinError`（调用方不得吞掉
此类错误）；其余研究引擎故障只记入装配的 ``research.errors``，
对应块为 None，永不拖垮公开页。

多页复用：同一出生瞬时的出生层装配在模块内按
``(birth_value, zone)`` 缓存一次（上限 8 条，FIFO；返回深拷贝），
目标年层（流年 / 年度喜用 / 组合）按
``(birth_value, zone, traditional_role, target_year)`` 缓存；五页
通过裁剪函数消费同一份装配，出生时刻与目标年在五页间无漂移。
缓存只认确定性输入全量作 key；装配失败不污染缓存。

本模块顶层只 import 标准库：全部引擎 import 均在函数内懒加载，
公开检出（无密封 ``data/``）下仍可 import，纯函数部分（pin、
裁剪、标注表）可直接测试；需要密封数据的装配路径按既有形制
SkipTest，不谎称通过。
"""

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


class UnifiedComputePinError(ValueError):
    """引擎输出变体漂移：调用方不得吞掉，必须 loud 失败。"""


class UnifiedComputeInputError(ValueError):
    """入口输入校验失败（出生瞬时 / 目标年 / 传统口径形态非法）。"""


def clear_unified_compute_cache():
    """清空入口的全部模块内缓存（测试隔离用；不碰任何引擎状态）。"""
    _CORE_CACHE.clear()
    _YEAR_CACHE.clear()
    _EXECUTE_CACHE.clear()


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
    if key is not None and key in _EXECUTE_CACHE:
        return copy.deepcopy(_EXECUTE_CACHE[key])
    result = execute(domain, inputs, allow_research=allow_research)
    _cache_put(_EXECUTE_CACHE, key, result)
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
    key = _canonical_key([birth_value, zone])
    if key is not None and key in _CORE_CACHE:
        return copy.deepcopy(_CORE_CACHE[key])

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
    _cache_put(_CORE_CACHE, key, core)
    return copy.deepcopy(core)


def _assemble_year_layer(core, *, traditional_role, target_year):
    """目标年层装配（缓存单位）：流年 + 年度喜用 + 组合。

    组合只在传统口径与目标年同时给出时装配；当期运未显式指定时
    记未确定（D-02），不推导期位。流年边界只作消费侧对照（D-03）。
    任一步骤失败只记入 ``errors``，组合块为 None，不拖垮其余层。
    """
    birth_value = core['birth_value']
    zone = core['zone']
    key = _canonical_key([birth_value, zone, traditional_role,
                          target_year])
    if key is not None and key in _YEAR_CACHE:
        return copy.deepcopy(_YEAR_CACHE[key])

    from .bazi_core import ten_god
    from .calendar import calendar

    day_master = core['chart']['day_master']['stem'] \
        if isinstance(core['chart']['day_master'], dict) \
        else core['chart']['day_master']
    errors = list(core['research']['errors'])

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
                from .bazi_annual_reference import \
                    annual_lichun_boundaries
                from .bazi_combination_engine import combine
                from .bazi_dayun_compose import classical_dayun_timeline

                timeline = classical_dayun_timeline(
                    birth_value, zone=zone,
                    traditional_role=traditional_role, periods=8,
                    birth_time_precision='second', include_shenfeng=True)
                if timeline.get('status') != 'converted':
                    errors.append({
                        'block': 'combination',
                        'reason': 'dayun_timeline_unresolved: %s'
                                  % timeline.get('reason')})
                else:
                    dayun_rows = timeline['sequence']['rows']
                    boundary = annual_lichun_boundaries(
                        day_master, [target_year])
                    combination = combine(
                        core['chart']['pillars'], day_master, dayun_rows,
                        target_year,
                        strength=core['research']['strength'],
                        tiaohou=core['research']['tiaohou'],
                        bingyao=core['research']['bingyao'],
                        pattern=core['research']['pattern'],
                        xiyong=core['research']['xiyong'],
                        flow_boundary=boundary)
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
        'flow_year': flow_year,
        'annual_xiyong': annual_xiyong,
        'combination': combination,
        'combination_status': (
            'assembled' if combination is not None else 'not_assembled'),
        'combination_note': combination_note,
        'errors': errors,
    }
    _cache_put(_YEAR_CACHE, key, layer)
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
    assembly['flow_year'] = layer['flow_year']
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
    """bazi-profile 所需字段：排盘 + 强度 / 格局 / 喜用研究块。

    不含 target_year / flow_year / combination（本页无流年）。
    公开 presentation（strength / pattern / dayun / xiyong 四门控）
    不在本裁剪内，由各门控另行构建。
    """
    trim = _base_trim(assembly, 'bazi-profile')
    return trim


def trim_for_career(assembly):
    """career 所需字段：排盘 + 研究块 + 流年 + 组合。"""
    trim = _base_trim(assembly, 'career')
    trim['target_year'] = assembly['target_year']
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
    return trim


def trim_for_romance(assembly):
    """romance 所需字段：排盘 + 研究块 + 流年（无组合消费）。"""
    trim = _base_trim(assembly, 'romance')
    trim['target_year'] = assembly['target_year']
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
    return trim


def trim_for_life(assembly):
    """life 所需字段：排盘 + 研究块 + 流年 + 组合 + 四源一致性锚点。"""
    trim = _base_trim(assembly, 'life')
    trim['target_year'] = assembly['target_year']
    trim['flow_year'] = copy.deepcopy(assembly.get('flow_year'))
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
