"""巳月分日司令试点 Variant（TJ-012.3 Slice C 巳月试点，研究级）。

用户裁定（2026-11-09，Option B 附条件批准）：仅授权以已登记的三命
T1 表（《三命通会》卷二《论人元司事》T1 表，sm.t1_table）巳月分段，
建立三命 T1 口径研究 Variant，按登记的 calculation_convention
（siling-si-calculation-convention v1）以真实经过时间计算巳月司令。
T2 仅为同书内证，不作独立证据票；C1（任氏曰巳月命例 dt.case_si_wu）
与 C2（神峰《节气歌断》 sf.geduan_song）与 T1 分段冲突，并列待审，
C1「立夏后十天」语义待审。不得据此推导其他十一月；巳月司令可计算
不等于任氏八格真假成立；不解锁 Slice D，不接任何公开场景。

审计结论与实现裁定（P1–P5，照寅月试点 bazi_siling_pilot.py 同形）：

- P1 消费登记，不另存常量：分段秒界在每次调用时由
  ``bazi_siling_matrix.SILING_SI_CALCULATION_CONVENTION`` 的三段区间
  字符串（``[t0, t0+7*24h)`` 等）解析推导，并与矩阵格
  ``SILING_MATRIX['sanming-t1']['巳']`` 的 days / day_span 逐项交叉
  核对；引文、层属、免责标注与冲突标记全部自登记读取。任一不一致即以
  registration_integrity_failure 拒绝（登记被篡改 = fail-closed）。
  与寅月不同：T1 登记仅三十日（戊 7＋庚 5＋丙 18），第三段以
  ``[t0+12*24h, t0+30*24h)`` 收尾而非 next_jie；[t0+30d, 芒种) 为
  登记外尾段，一律返回 uncertain，绝不以外推补足。
- P2 事实层只复用既有链：provider 身份由
  ``calendar_provider_guard.provider_identity()`` 核验（已安装
  lunar-python 必须等于钉定 1.4.8）；调用方传入的 jie_facts 只是
  待核验声明，立夏与下一交节（芒种）瞬时一律经钉定 provider 的
  年度节气表独立回放（与 ``bazi_annual_reference._li_chun_of``、
  TJ-015.2 回放同族），与声明逐秒相等才采信。不自建平行节气来源。
- P3 精度信号有什么用什么：provider 节气表只给秒级字符串，
  TJ-015.2 冻结参照只支持分钟级比对，代码内不存在数值警戒区间
  结构；故 convention 的 fail-closed 第三条（落入精度警戒区间）
  做成显式输入声明（``precision_warning`` /
  ``precision_warning_interval``），声明落入或精度声明非秒级一律
  返回 uncertain，缺失声明字段按未确立处理。出生时刻精度沿
  ``sanming_convert_measurement`` 先例以显式参数传入，非 second
  即 uncertain。
- P4 接线形态：独立模块，不附 operations.bazi_chart。Slice A/B 靠
  已执行 trace 附于 pattern_variant 结果；本试点消费出生瞬时 +
  已核验 jie 事实 + version 选择，chart 调用并不携带这些输入，
  附入将改变既有 Variant 的输出面。故照 ``bazi_dayun_jie`` /
  TJ-017.3 时间轴视图的独立研究模块先例落地，输出契约与 Slice
  A/B 同形（research_only / public_enabled=false / ai_enabled=
  false / evidence_binding=pending_phase1_rule_registration /
  determination 恒 None）；公开投影对 ``siling_si_pilot`` 键做防御性
  整体剥离（与 TJ-017.3 先例同，不改变任何现有输出）。
- P5 状态语义：computed（窗口内且全部核验通过）/ not_applicable
  （t0 之前或下一交节及之后，绝不外推）/ rejected（口径非试点、
  身份未核验、回放不一致、来源声明冲突、登记不完整等伪造与
  形状类拒绝）/ uncertain（精度不足、警戒区间与登记外尾段类）。
  后三者 commander 恒 None。结构上不可解读的出生输入（naive、无秒级
  精度、不可解析字符串）沿 ``adjacent_jie_distance`` 纪律抛
  ValueError。
- P6 冲突标记：输出顶层 ``conflicts`` 字段具名并列 C1 与 C2（含
  引文 id、来源与字符定位、待审状态），另见 adjudication_notes；
  C1「立夏后十天」语义保持 pending_review，绝不自动确认为完整
  分段表；C3–C7 继续平行登记，本试点不择任一学派为最终正确口径。
- P7 引文边界：全表引文 sm.t1_table（十二月全表，316 字）只存于
  登记；本试点输出仅载巳月分句引文（19 字，见 provenance 的 quote
  与 quote_locator），全表不随输出重复；分段 basis 三条短语即该分句
  的三段原文。
"""

import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import bazi_siling_matrix as _matrix
from .calendar_provider_guard import (PINNED_PROVIDER_NAME,
                                      PINNED_PROVIDER_VERSION,
                                      provider_identity)

SILING_SI_PILOT_VARIANT = 'bazi-siling-si-pilot-v1'
PILOT_TASK = 'TJ-012.3 Slice C 巳月试点'

SECONDS_PER_DAY = 24 * 60 * 60
REGISTERED_DAYS = 30
_CHINA = ZoneInfo('Asia/Shanghai')
_UTC = timezone.utc
# 与 bazi_dayun_jie 的钉定历法运行包络一致（中国本地年）。
_ENVELOPE_MIN_YEAR = 1901
_ENVELOPE_MAX_YEAR = 2098
# 交节窗口合理性包络（与 adjacent_jie_distance 的 40 日上限同族，下限
# 取相邻两节实际间隔的保守下界）。
_WINDOW_MIN_SECONDS = 25 * SECONDS_PER_DAY
_WINDOW_MAX_SECONDS = 40 * SECONDS_PER_DAY
# provider 年度节气表的节名期望窗口（与 _li_chun_of 的立夏窗口同式）。
_TERM_WINDOWS = {'立夏': (5, 5, 7), '芒种': (6, 5, 7)}
_INTERVAL_RE = re.compile(
    r'^\[t0(?:\+(\d+)\*24h)?, (t0(?:\+(\d+)\*24h)?|next_jie)\)$')

PILOT_LIMITATIONS = (
    '本试点只计算巳月三命 T1 口径（《三命通会》卷二《论人元司事》T1 表）分日司令；其余十一月在冲突矩阵中仍为 conflict/research_only，本试点不推导、不外推。',
    '巳月司令可计算不等于任氏八格真假成立：真格/假格、用神、清浊与吉凶一律不在本试点输出内，determination 恒 None；Slice D 未解锁。',
    '原文以日序（第几日）表述；日序与真实经过时间的换算原文未明示，本试点采用的「连续24小时计日」是用户裁定的程序计算约定（见 provenance 的 disclaimer 原文），不是已证实的传统文献唯一解释。',
    '节气瞬时来自钉定 provider 并经年度节气表回放核验；provider 身份核验只及已安装发行版元数据与钉定版本相等，天文精度未经独立验证（TJ-015.2 冻结参照只支持分钟级比对）。',
    '登记仅三十日（戊 7＋庚 5＋丙 18）；实际立夏→芒种窗口约 31.17 日，[t0+30d, 芒种) 不属登记分段，一律返回不确定，不得以外推补足。',
    'C1（任氏曰巳月命例）与 C2（神峰《节气歌断》）与 T1 巳月分段冲突，并列待审；C1「立夏后十天」语义待审，本试点不以其名义改动分段；C3–C7 继续平行登记，不择任一学派为最终正确口径。',
    '本 Variant 尚无密封 Phase1/Phase2 rule 注册（evidence_binding=pending_phase1_rule_registration），不进 RuleMatch 与 Evidence；研究级内部使用，不接任何公开场景，公开投影整体剥离。',
)

PILOT_ADJUDICATION_NOTES = (
    'P1 分段秒界由 calculation_convention 登记的区间字符串解析推导，并与矩阵格 days/day_span 交叉核对；模块内不另存分段表；第三段以 [t0+12*24h, t0+30*24h) 收尾。',
    'P2 jie_facts 是待核验声明而非事实：立夏/芒种瞬时经钉定 provider 独立回放逐秒比对，不一致即拒绝。',
    'P3 精度警戒无既有数值结构，做成显式输入声明（precision_warning / precision_warning_interval）；声明落入即 uncertain。',
    'P4 独立研究模块（不附 bazi_chart，避免改变既有 Variant 输出面）；公开投影防御性剥离 siling_si_pilot 键。',
    'P5 状态四分：computed / not_applicable / rejected / uncertain；后三者 commander 恒 None，窗口外绝不外推；登记外尾段 [t0+30d, 芒种) 为 uncertain，不以外推补足。',
    'P6 冲突并列：顶层 conflicts 字段具名 C1（任氏曰巳月命例 dt.case_si_wu）与 C2（神峰《节气歌断》 sf.geduan_song），两者皆 pending_review；C1「立夏后十天」语义待审。',
    'P7 引文边界：输出仅载巳月分句引文（19 字）；全表引文 sm.t1_table 只存于登记，不随输出重复。',
)

# 冲突标记的释义为复述（非引文）；引文 id、来源与定位一律自登记读取。
_CONFLICT_SPECS = (
    {'id': 'C1',
     'quote_id': 'dt.case_si_wu',
     'registered_in': ('ditiansui-yuanshuo', '巳'),
     'summary': '任氏曰巳月命例称立夏后十天仍戊土司令（戊段至少十日），与三命 T1 巳月戊段七日冲突；'
                '「立夏后十天」语义待审，未自动确认为完整分段表。'},
    {'id': 'C2',
     'quote_id': 'sf.geduan_song',
     'registered_in': ('shenfeng-diagram', '巳'),
     'summary': '神峰《节气歌断》巳月首段土五日，与三命 T1、T2 的七日不合；歌断与分日表不同制，图版干数对应未证实。'},
)


def _read_conflicts():
    """Build the top-level conflict markers from the registration.

    Quote ids, sources, layers and locators are read from
    ``SILING_QUOTES`` at call time; the summaries are paraphrases
    (never verbatim quotes). A missing quote degrades to a marker
    that still names the conflict and its quote id.
    """
    quotes = {}
    try:
        quotes = {row['id']: row for row in _matrix.SILING_QUOTES}
    except (KeyError, TypeError, AttributeError):
        quotes = {}
    markers = []
    for spec in _CONFLICT_SPECS:
        quote = quotes.get(spec['quote_id'])
        marker = {'id': spec['id'],
                  'quote_id': spec['quote_id'],
                  'summary': spec['summary'],
                  'status': 'pending_review'}
        if quote is None:
            marker['source_id'] = None
            marker['source_section_id'] = None
            marker['layer'] = None
            marker['locator'] = None
            marker['note'] = '登记缺失该引文记录'
        else:
            marker['source_id'] = quote['source_id']
            marker['source_section_id'] = quote['source_section_id']
            marker['layer'] = quote['layer']
            marker['locator'] = dict(quote['locator'])
        markers.append(marker)
    return markers


def _fail(status, reason, note, *, version_id=None):
    return {
        'variant': SILING_SI_PILOT_VARIANT,
        'status': status,
        'reason': reason,
        'note': note,
        'commander': None,
        'determination': None,
        'requested_version_id': version_id,
        'scope_month_branch': '巳',
        'month_branch': None,
        'conflicts': _read_conflicts(),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
        'limitations': list(PILOT_LIMITATIONS),
        'adjudication_notes': list(PILOT_ADJUDICATION_NOTES),
    }


def _derive_registration():
    """Read the pilot's rule shape from the step-1 registration.

    Returns (derived, None) or (None, failure_note). Every value the
    pilot computes with comes from ``bazi_siling_matrix`` at call time;
    any inconsistency in the registration fails closed here.
    """
    try:
        conv = _matrix.SILING_SI_CALCULATION_CONVENTION
        scope = conv['scope']
        version_id = scope['version_id']
        if conv['id'] != 'siling-si-calculation-convention':
            return None, 'calculation_convention id 与登记不符'
        if scope['months'] != ['巳']:
            return None, 'calculation_convention 适用月份不是登记的巳月单月'
        versions = {row['version_id']: row
                    for row in _matrix.SILING_VERSIONS}
        version = versions[version_id]
        cell = _matrix.SILING_MATRIX[version_id]['巳']
        if cell['adjudication_status'] != 'pilot_authorized_sanming_t1':
            return None, '巳月格裁定状态不是 pilot_authorized_sanming_t1'
        if cell['status'] != 'segments_registered' or cell['research_only'] is not True:
            return None, '巳月格登记状态与试点授权不符'
        conv_segments = conv['segments']
        cell_segments = cell['segments']
        if len(conv_segments) != 3 or len(cell_segments) != 3:
            return None, '登记分段不是三段'
        bounds = []
        for seg in conv_segments:
            match = _INTERVAL_RE.match(seg['interval'])
            if match is None:
                return None, 'convention 区间字符串不可解析：%r' % (seg['interval'],)
            start = int(match.group(1)) * SECONDS_PER_DAY if match.group(1) else 0
            if match.group(2) == 'next_jie':
                end = None
            else:
                end = int(match.group(3)) * SECONDS_PER_DAY if match.group(3) else 0
            bounds.append((seg['stem'], start, end))
        if [b[0] for b in bounds] != [s['stem'] for s in cell_segments]:
            return None, 'convention 分段干序与矩阵格登记不一致'
        if bounds[0][1] != 0 or bounds[1][1] != bounds[0][2] \
                or bounds[2][1] != bounds[1][2] or bounds[2][2] is None:
            return None, 'convention 三段区间不连续或末段未以登记三十日收尾'
        if bounds[2][2] != REGISTERED_DAYS * SECONDS_PER_DAY:
            return None, 'convention 登记总日数不是三十日'
        day_cursor = 1
        for (stem, start, end), cell_seg in zip(bounds, cell_segments):
            span = cell_seg['day_span']
            width_days = (end - start) // SECONDS_PER_DAY
            if cell_seg['days'] != width_days \
                    or span != [day_cursor, day_cursor + width_days - 1]:
                return None, '分段登记 days/day_span 与区间定义不一致'
            day_cursor += width_days
        if day_cursor != REGISTERED_DAYS + 1:
            return None, '登记分段日序未恰满三十日'
        quotes = {row['id']: row for row in _matrix.SILING_QUOTES}
        quote = quotes[cell['quotes'][0]]
        if quote['id'] != 'sm.t1_table':
            return None, '巳月格引文不是登记的 sm.t1_table'
        if quote['source_id'] != version['source_id'] \
                or quote['source_section_id'] != version['source_section_id']:
            return None, 'sm.t1_table 引文来源与版本登记不一致'
        excerpt = cell['quote_excerpt']
        offset = quote['quote'].find(excerpt)
        if offset < 0 or quote['quote'].find(excerpt, offset + 1) >= 0:
            return None, '巳月分句引文在登记全表中不是唯一出现'
        excerpt_locator = {
            'char_start': quote['locator']['char_start'] + offset,
            'char_end': quote['locator']['char_start'] + offset + len(excerpt)}
        for spec in _CONFLICT_SPECS:
            conflict_quote = quotes.get(spec['quote_id'])
            if conflict_quote is None:
                return None, '冲突标记引文 %s 不在登记内' % (spec['quote_id'],)
            version_id_c, month_c = spec['registered_in']
            ancillary = _matrix.SILING_MATRIX[version_id_c][month_c].get(
                'ancillary_quotes', [])
            if spec['quote_id'] not in ancillary:
                return None, '冲突标记引文 %s 未登记于 %s/%s 格' % (
                    spec['quote_id'], version_id_c, month_c)
    except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
        return None, '登记读取或交叉核对失败：%s' % (exc,)
    return {
        'convention': conv,
        'version_id': version_id,
        'version': version,
        'cell': cell,
        'bounds': bounds,
        'quote': quote,
        'excerpt': excerpt,
        'excerpt_locator': excerpt_locator,
    }, None


def _provider_jie_instant(year, term_name):
    """Replay one Jie instant from the pinned provider's annual table.

    Mirrors ``bazi_annual_reference._li_chun_of``: the provider's wall
    output is interpreted as Asia/Shanghai. Raises ValueError on any
    anomaly; there is no fallback source.
    """
    from lunar_python import Solar
    table = Solar.fromYmd(year, 7, 1).getLunar().getJieQiTable()
    term = table.get(term_name)
    if term is None:
        raise ValueError('Pinned calendar has no %s term' % term_name)
    if term.getYear() != year:
        raise ValueError('%s year differs from the requested year' % term_name)
    instant = datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
    instant = instant.replace(tzinfo=_CHINA)
    month, first_day, last_day = _TERM_WINDOWS[term_name]
    if instant.year != year or instant.month != month \
            or not first_day <= instant.day <= last_day:
        raise ValueError('%s outside its expected window' % term_name)
    return instant


def _parse_instant(value):
    """Parse an aware datetime / ISO string; None when unparseable."""
    if isinstance(value, datetime):
        instant = value
    elif isinstance(value, str):
        try:
            instant = datetime.fromisoformat(value)
        except ValueError:
            return None
    else:
        return None
    if instant.tzinfo is None or instant.utcoffset() is None:
        return None
    return instant


def _iso_pair(instant):
    return {'utc': instant.astimezone(_UTC).isoformat(),
            'asia_shanghai': instant.astimezone(_CHINA).isoformat()}


def si_siling_pilot(birth_instant, *, version_id, jie_facts,
                    birth_time_precision='second'):
    """Sanming-T1 巳月 dated-commander pilot over a verified Jie window.

    ``birth_instant``: timezone-aware datetime or ISO string at
    whole-second precision (naive / sub-second / unparseable input
    raises ValueError, mirroring ``adjacent_jie_distance``).
    ``version_id``: the registered matrix version the caller selects;
    anything other than the convention's pilot version is rejected.
    ``jie_facts``: the caller's *claimed* verified Jie window, a dict
    {'provider': {'name', 'version', 'identity_verified'},
     'lixia': {'term', 'at', 'precision'},
     'next_jie': {'term', 'at', 'precision'},
     optional 'precision_warning': bool,
     optional 'precision_warning_interval': {'start', 'end'},
     optional 'source_ref': {'source_id', 'source_section_id'}}.
    The claimed instants are never trusted: both are replayed from the
    pinned provider and must match to the second.
    """
    derived, failure = _derive_registration()
    if derived is None:
        return _fail('rejected', 'registration_integrity_failure', failure,
                     version_id=version_id)
    conv = derived['convention']

    # --- version gate: only the registered pilot version computes.
    if version_id != derived['version_id']:
        return _fail(
            'rejected', 'not_pilot_version',
            '所选口径 %r 不是裁定授权的巳月三命 T1 试点口径；该口径在冲突'
            '矩阵中保持 conflict/research_only，本试点不以其名义输出任何'
            '司令。' % (version_id,), version_id=version_id)

    # --- birth input shape (structural discipline, may raise).
    birth = _parse_instant(birth_instant)
    if birth is None:
        raise ValueError('Expected timezone-aware birth ISO datetime')
    if birth.microsecond != 0:
        raise ValueError('Birth must be at whole-second precision')

    # --- jie_facts shape and provider identity claims.
    if not isinstance(jie_facts, dict):
        return _fail('rejected', 'jie_facts_incomplete',
                     'jie_facts 必须是带 provider/lixia/next_jie 的声明字典',
                     version_id=version_id)
    provider_claim = jie_facts.get('provider')
    lixia_claim = jie_facts.get('lixia')
    next_claim = jie_facts.get('next_jie')
    if not isinstance(provider_claim, dict) \
            or not isinstance(lixia_claim, dict) \
            or not isinstance(next_claim, dict):
        return _fail('rejected', 'jie_facts_incomplete',
                     'jie_facts 缺失 provider/lixia/next_jie 声明块',
                     version_id=version_id)
    if provider_claim.get('name') != PINNED_PROVIDER_NAME \
            or provider_claim.get('version') != PINNED_PROVIDER_VERSION \
            or provider_claim.get('identity_verified') is not True:
        return _fail('rejected', 'provider_identity_unverified',
                     'jie_facts 的 provider 身份声明与钉定 provider 不符或'
                     '未声明已核验', version_id=version_id)
    try:
        identity = provider_identity()
    except ValueError as exc:
        return _fail('rejected', 'provider_identity_mismatch', str(exc),
                     version_id=version_id)
    if lixia_claim.get('term') != '立夏' or next_claim.get('term') != '芒种':
        return _fail('rejected', 'jie_term_mismatch',
                     '试点窗口必须以立夏为 t0、芒种为下一交节',
                     version_id=version_id)
    source_ref = jie_facts.get('source_ref')
    if source_ref is not None:
        quote = derived['quote']
        if not isinstance(source_ref, dict) \
                or source_ref.get('source_id') != quote['source_id'] \
                or source_ref.get('source_section_id') != quote['source_section_id']:
            return _fail('rejected', 'source_claim_mismatch',
                         'jie_facts 的来源声明与登记的 sm.t1_table 引用不一致',
                         version_id=version_id)

    # --- precision declarations (uncertain class, never forced).
    lixia_at = _parse_instant(lixia_claim.get('at'))
    next_at = _parse_instant(next_claim.get('at'))
    if lixia_at is None or next_at is None:
        return _fail('rejected', 'jie_instant_invalid',
                     '声明的节气瞬时不可解析或不带时区', version_id=version_id)
    if lixia_claim.get('precision') != 'second' \
            or next_claim.get('precision') != 'second' \
            or lixia_at.microsecond != 0 or next_at.microsecond != 0:
        return _fail('uncertain', 'jie_precision_insufficient',
                     '节气瞬时精度未声明为秒级或带亚秒值；按 convention '
                     'fail-closed 条款返回不确定，不强行给出唯一司令',
                     version_id=version_id)
    if birth_time_precision != 'second':
        return _fail('uncertain', 'birth_time_precision_insufficient',
                     '出生时刻精度声明为 %r 而非 second；返回不确定'
                     % (birth_time_precision,), version_id=version_id)

    # --- replay both Jie instants from the pinned provider.
    lixia_year = lixia_at.astimezone(_CHINA).year
    if not _ENVELOPE_MIN_YEAR <= lixia_year <= _ENVELOPE_MAX_YEAR:
        return _fail('rejected', 'outside_provider_envelope',
                     '立夏年份 %d 在钉定历法运行包络 1901..2098 之外'
                     % lixia_year, version_id=version_id)
    try:
        replay_lixia = _provider_jie_instant(lixia_year, '立夏')
        replay_next = _provider_jie_instant(lixia_year, '芒种')
    except ValueError as exc:
        return _fail('rejected', 'provider_replay_mismatch', str(exc),
                     version_id=version_id)
    if lixia_at.astimezone(_UTC) != replay_lixia.astimezone(_UTC) \
            or next_at.astimezone(_UTC) != replay_next.astimezone(_UTC):
        return _fail('rejected', 'provider_replay_mismatch',
                     '声明的节气瞬时与钉定 provider 回放结果逐秒不一致',
                     version_id=version_id)
    t0, next_jie = replay_lixia, replay_next
    window_seconds = (next_jie - t0).total_seconds()
    if not _WINDOW_MIN_SECONDS <= window_seconds <= _WINDOW_MAX_SECONDS:
        return _fail('rejected', 'jie_chronology_invalid',
                     '回放的立夏→芒种窗口时长不在合理包络内',
                     version_id=version_id)

    # --- precision-warning attestation (explicit input, fail-closed).
    if jie_facts.get('precision_warning') is True:
        return _fail('uncertain', 'precision_warning_interval',
                     '调用方声明落入既有精度警戒区间；返回不确定',
                     version_id=version_id)
    warning_interval = jie_facts.get('precision_warning_interval')
    if warning_interval is not None:
        w_start = _parse_instant(
            warning_interval.get('start')) if isinstance(warning_interval, dict) else None
        w_end = _parse_instant(
            warning_interval.get('end')) if isinstance(warning_interval, dict) else None
        if w_start is None or w_end is None:
            return _fail('rejected', 'jie_facts_incomplete',
                         'precision_warning_interval 声明不可解析',
                         version_id=version_id)
        for moment in (birth, t0, next_jie):
            if w_start <= moment < w_end:
                return _fail('uncertain', 'precision_warning_interval',
                             '出生或节气瞬时落入声明的精度警戒区间；'
                             '返回不确定', version_id=version_id)

    # --- window membership: outside [t0, next_jie) never extrapolates.
    if birth < t0:
        return _fail('not_applicable', 'before_lixia',
                     '出生瞬时在立夏 t0 之前，不属本巳月窗口；本试点不'
                     '向前外推', version_id=version_id)
    if birth >= next_jie:
        return _fail('not_applicable', 'at_or_after_next_jie',
                     '出生瞬时已达下一交节（芒种）及之后，巳月 Variant '
                     '不再适用；本试点不向后外推', version_id=version_id)

    # --- registered tail: [t0+30d, next_jie) is outside the registered
    # thirty days; the registration covers 30 days while the replayed
    # 立夏→芒种 window is ~31.17 days, so the tail is uncertain by
    # design and never extended by extrapolation.
    elapsed = int((birth.astimezone(_UTC) - t0.astimezone(_UTC)).total_seconds())
    if elapsed >= REGISTERED_DAYS * SECONDS_PER_DAY:
        return _fail(
            'uncertain', 'beyond_registered_segments',
            '出生瞬时在登记三十日之后（已过 t0+30d），实际立夏→芒种窗口为'
            ' %.2f 日；尾段 [t0+30d, 芒种) 不属登记分段，返回不确定，'
            '不得以外推补足。' % (window_seconds / SECONDS_PER_DAY,),
            version_id=version_id)

    # --- segment by real elapsed seconds, left-closed right-open.
    bounds = derived['bounds']
    segment_index = None
    for index, (stem, start, end) in enumerate(bounds):
        if start <= elapsed and (end is None or elapsed < end):
            segment_index = index
            break
    if segment_index is None:  # pragma: no cover - bounds cover the window
        return _fail('uncertain', 'segment_unresolved',
                     '经过秒数未落入登记三段', version_id=version_id)
    stem, start, end = bounds[segment_index]
    t0_utc = t0.astimezone(_UTC)
    seg_start = t0_utc + timedelta(seconds=start)
    seg_end = next_jie if end is None else t0_utc + timedelta(seconds=end)
    cell_seg = derived['cell']['segments'][segment_index]
    quote = derived['quote']
    return {
        'variant': SILING_SI_PILOT_VARIANT,
        'status': 'computed',
        'reason': None,
        'commander': stem,
        'determination': None,
        'requested_version_id': version_id,
        'scope_month_branch': '巳',
        'month_branch': '巳',
        'elapsed_seconds': elapsed,
        'segment': {
            'index': segment_index + 1,
            'stem': stem,
            'start': _iso_pair(seg_start),
            'end': _iso_pair(seg_end),
            'registered_interval': conv['segments'][segment_index]['interval'],
            'registered_day_span': list(cell_seg['day_span']),
            'registered_basis': cell_seg['basis'],
        },
        'window': {
            'lixia': {'term': '立夏', **_iso_pair(t0)},
            'next_jie': {'term': '芒种', **_iso_pair(next_jie)},
        },
        'provenance': {
            'source_id': quote['source_id'],
            'source_section_id': quote['source_section_id'],
            'text_layer': quote['layer'],
            'quote_id': quote['id'],
            'quote': derived['excerpt'],
            'quote_locator': dict(derived['excerpt_locator']),
            'quote_note': '全表引文 sm.t1_table（十二月全表）只存于登记；此处仅载巳月分句（19 字），全表不随输出重复。',
            'version_id': derived['version_id'],
            'version_label': derived['version']['label'],
            'school_branch': conv['scope']['school_branch'],
            'calculation_convention': {'id': conv['id'],
                                       'version': conv['version']},
            'disclaimer': conv['disclaimer'],
        },
        'provider_verification': {
            'provider': identity['provider'],
            'installed_version': identity['installed_version'],
            'identity_verified': True,
            'replay_verified': True,
            'astronomical_precision_independently_verified': False,
        },
        'conflicts': _read_conflicts(),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
        'limitations': list(PILOT_LIMITATIONS),
        'adjudication_notes': list(PILOT_ADJUDICATION_NOTES),
        'scope': ('仅巳月三命 T1 口径研究试点：按登记 calculation_convention '
                  '以真实经过时间给出 sm.t1_table 分日司令；不推导其他十一月，'
                  '不定八格真假、用神或吉凶；C1/C2 冲突并列待审。'),
    }
