"""《穷通宝鉴》甲木十二月调候研究 Variant (TJ-013.1)：只陈述条目原文，不作裁决。

治理定位：Source 已登记为 bazi.source.qiongtong（C 级，单一电子谱系，
daizhigev20 固定快照，87430 字节）。甲木十二个月条目逐条按快照字符
区间与行号审定（见 ENTRIES 与 tests/golden_tj0131_tiaohou.json），只编码
原文明确陈述的内容：该月先取/次取的干（按原文顺序）、逐字短引、以及
一条条件可由存在性事实判定的分支（五月乏癸用丁）。原文含糊处、条件
超出本输入契约（成局、相对旺盛、程度判断）的分支只登记不编码，逐项
列于 unencoded_branches。快照为简体转写，引文逐字保留快照字形与标点，
不作简繁转换或改写。

硬边界：不把条目陈述翻译成吉凶/强弱/格局/喜用结论，不与其他喜用
体系（扶抑/病药/格局用神）合并，不生成评分。本 Variant 恒
research_only=True、public_enabled=False、ai_enabled=False。

执行链接入方式与旺衰裁定相同：engine.execute 以 allow_research 门控，
operations.bazi_chart.chart 以 tiaohou_variant 显式开启，本模块的
tiaohou_assessment 只消费已执行的 trace 步骤（pillars / ten_gods /
hidden_stems，且要求其 evidence 已绑定），伪造或缺失事实一律
fail-closed。与 dayun_sequence_research 先例相同的一点如实说明：
本 Variant 尚无密封 Phase1 bundle / Phase2 contract 的 rule 注册，
故 assessment 附于 result 而不新增 trace rule，不进 RuleMatch 与
Evidence，evidence_binding 标记为 pending_phase1_rule_registration，
不得冒充已绑定证据的裁决。
"""
import copy

from .bazi_core import VARIANT as BAZI_VARIANT
from .foundations import BRANCHES, STEMS

VARIANT = 'tiaohou-qiongtong-v1'
SOURCE_ID = 'bazi.source.qiongtong'
SNAPSHOT_PATH = 'data/quarantine/public_domain_snapshots/daizhigev20/qiongtong_baojian.txt'
SNAPSHOT_SHA256 = 'a8125d7de94f93d1a3eec48f1610b0c4baf31c264e9d7c19f586a85a78a2b0b4'
SNAPSHOT_BYTES = 87430

PILLAR_NAMES = ('year', 'month', 'day', 'hour')

LIMITATIONS = (
    '仅审定甲木十二月条目；其余九日主未建，不外推。',
    '来源为 C 级单一电子谱系（简体转写），未做多底本校勘；引文逐字以固定快照为准。',
    '只陈述条目原文的取用顺序与盘面存在性事实，不作吉凶、强弱、格局或喜用结论，不与其他喜用体系合并。',
    '本 Variant 尚未在密封 Phase1 bundle/Phase2 contract 注册 rule，不进 RuleMatch 与 Evidence。',
)

# ENTRIES literal is generated from tests/golden_tj0131_tiaohou.json, whose
# quotes and character locators were transcribed by slicing the pinned
# snapshot text (each quote occurs exactly once in the full text).
ENTRIES = (
    {
        'month_branch': '寅', 'month_label': '正月',
        'section': {'line': 22, 'char_start': 1300, 'char_end': 1362},
        'quote': '正月甲木,初春尚有余寒,得丙癸逢,富贵双全。癸藏丙透,名寒木向阳',
        'quote_locator': {'line': 22, 'char_start': 1300, 'char_end': 1332},
        'sequence': ({'stem': '丙', 'order': 1}, {'stem': '癸', 'order': 2},),
        'order_basis': '原文先举「得丙癸逢」按列举顺序定先次,次句「癸藏丙透」以丙透为要、癸为辅。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': ('正二月合论段(快照字符 1363-1818)含从格与妻子等论述,非调候取用顺序陈述,不编码;仅登记为相邻段落。',),
    },
    {
        'month_branch': '卯', 'month_label': '二月',
        'section': {'line': 28, 'char_start': 1819, 'char_end': 1935},
        'quote': '二月甲木,庚金得所,名阳刃驾杀,可云小贵,异途显达,或主武职,但要财资之。',
        'quote_locator': {'line': 28, 'char_start': 1819, 'char_end': 1856},
        'sequence': ({'stem': '庚', 'order': 1},),
        'order_basis': '原文以「庚金得所」陈述庚为当月取用,未明示次取;「但要财资之」为资助条件,不列为次取。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': ('「但要财资之」:财(土)为资助庚的条件陈述,原文未将其列为次取,故不入序列。',),
    },
    {
        'month_branch': '辰', 'month_label': '三月',
        'section': {'line': 29, 'char_start': 1936, 'char_end': 2202},
        'quote': '三月甲木,木气相竭。先取庚金,次用壬水。',
        'quote_locator': {'line': 29, 'char_start': 1936, 'char_end': 1956},
        'sequence': ({'stem': '庚', 'order': 1}, {'stem': '壬', 'order': 2},),
        'order_basis': '原文「先取庚金,次用壬水」明示先次。',
        'branches': (),
        'unencoded_branches': (
            {
                'quote': '或支成金局,方可用丁,不然,三月无用丁之法。惟有先庚後壬取用。',
                'locator': {'line': 34, 'char_start': 2142, 'char_end': 2173},
                'reason': '条件「支成金局」需地支三合/三会成局事实,不在本 Variant 输入契约(日主、月支、天干与藏干存在性)内,只登记不编码。',
            },
        ),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '巳', 'month_label': '四月',
        'section': {'line': 38, 'char_start': 2208, 'char_end': 2398},
        'quote': '四月甲木退气,丙火司权,先癸後丁。',
        'quote_locator': {'line': 38, 'char_start': 2208, 'char_end': 2225},
        'sequence': ({'stem': '癸', 'order': 1}, {'stem': '丁', 'order': 2},),
        'order_basis': '原文「先癸後丁」明示先次(该段为四月条首句,节区含其后讨论段)。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '午', 'month_label': '五月',
        'section': {'line': 42, 'char_start': 2398, 'char_end': 3048},
        'quote': '五六月甲木,木性虚焦,一理共推。五月先癸後丁庚金次之。',
        'quote_locator': {'line': 42, 'char_start': 2398, 'char_end': 2425},
        'sequence': ({'stem': '癸', 'order': 1}, {'stem': '丁', 'order': 2}, {'stem': '庚', 'order': 3},),
        'order_basis': '原文「五月先癸後丁庚金次之」明示三级先次(节区为五六月合论段)。',
        'branches': ({
            'id': 'wuyue_fa_gui_yong_ding', 'condition': {'absent_stem': '癸'},
            'quote': '或五月乏癸,用丁亦可,要运行北地为隹。',
            'locator': {'line': 42, 'char_start': 2447, 'char_end': 2466},
            'sequence': ({'stem': '丁', 'order': 1}, {'stem': '庚', 'order': 2},),
            'note': '原文「或五月乏癸,用丁亦可」:本 Variant 将「乏癸」界定为癸在四柱透干与藏干皆无;此时丁可代为首取,庚仍次之。运行北地为运途条件,不在本执行范围。',
        },),
        'unencoded_branches': (
            {
                'quote': '五六月甲木,木盛先庚,庚盛先丁。',
                'locator': {'line': 45, 'char_start': 2563, 'char_end': 2579},
                'reason': '条件「木盛/庚盛」为相对旺盛判断,非存在性事实,不在本 Variant 输入契约内,只登记不编码。',
            },
        ),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '未', 'month_label': '六月',
        'section': {'line': 42, 'char_start': 2398, 'char_end': 3048},
        'quote': '六月三伏生寒,丁火退气。先丁後庚,无癸亦可。',
        'quote_locator': {'line': 42, 'char_start': 2425, 'char_end': 2447},
        'sequence': ({'stem': '丁', 'order': 1}, {'stem': '庚', 'order': 2},),
        'order_basis': '原文「先丁後庚,无癸亦可」明示先次,且明示癸不在取用之列,故不列癸。',
        'branches': (),
        'unencoded_branches': (
            {
                'quote': '五六月甲木,木盛先庚,庚盛先丁。',
                'locator': {'line': 45, 'char_start': 2563, 'char_end': 2579},
                'reason': '条件「木盛/庚盛」为相对旺盛判断,非存在性事实,不在本 Variant 输入契约内,只登记不编码。',
            },
        ),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '申', 'month_label': '七月',
        'section': {'line': 62, 'char_start': 3430, 'char_end': 3512},
        'quote': '七月甲木,丁火为尊,庚金次之,庚金不可少。',
        'quote_locator': {'line': 62, 'char_start': 3430, 'char_end': 3451},
        'sequence': ({'stem': '丁', 'order': 1}, {'stem': '庚', 'order': 2},),
        'order_basis': '原文「丁火为尊,庚金次之」明示先次,并明示「庚金不可少」。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '酉', 'month_label': '八月',
        'section': {'line': 63, 'char_start': 3513, 'char_end': 3683},
        'quote': '八月甲木,木囚金旺。丁火为先,次用丙火,庚金再次。',
        'quote_locator': {'line': 63, 'char_start': 3513, 'char_end': 3538},
        'sequence': ({'stem': '丁', 'order': 1}, {'stem': '丙', 'order': 2}, {'stem': '庚', 'order': 3},),
        'order_basis': '原文「丁火为先,次用丙火,庚金再次」明示三级先次。',
        'branches': (),
        'unencoded_branches': (
            {
                'quote': '或支成木局,干透比劫,反取庚金为先,次用丁火。',
                'locator': {'line': 69, 'char_start': 3659, 'char_end': 3682},
                'reason': '条件含「支成木局」,需成局事实,不在本 Variant 输入契约内,只登记不编码。',
            },
        ),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '戌', 'month_label': '九月',
        'section': {'line': 78, 'char_start': 4197, 'char_end': 4272},
        'quote': '九月甲木,端用丁癸,见戊透必贵。',
        'quote_locator': {'line': 78, 'char_start': 4197, 'char_end': 4213},
        'sequence': ({'stem': '丁', 'order': 1}, {'stem': '癸', 'order': 2},),
        'order_basis': '原文「端用丁癸」按列举顺序定先次;同月另一段「独爱丁火,壬癸滋扶」将壬列于滋扶而非端用,壬不入序列(见 related)。',
        'branches': (),
        'unencoded_branches': (),
        'related': ({
            'quote': '九月甲木,木星凋零,独爱丁火,壬癸滋扶',
            'locator': {'line': 70, 'char_start': 3683, 'char_end': 3702},
            'note': '同条另一段:独爱丁火、壬癸滋扶。壬在此仅列于滋扶,未列入端用顺序,故不入序列;戊在主引文中为「见戊透」之条件陈述,亦不入序列。',
        },),
        'notes': (),
    },
    {
        'month_branch': '亥', 'month_label': '十月',
        'section': {'line': 82, 'char_start': 4322, 'char_end': 4499},
        'quote': '十月甲木,庚丁为要,丙火次之。忌壬水泛身,须戊土制之。',
        'quote_locator': {'line': 82, 'char_start': 4322, 'char_end': 4349},
        'sequence': ({'stem': '庚', 'order': 1}, {'stem': '丁', 'order': 2}, {'stem': '丙', 'order': 3},),
        'order_basis': '原文「庚丁为要」按列举顺序定先次,「丙火次之」为第三级。',
        'branches': (),
        'unencoded_branches': (
            {
                'quote': '十月甲木,庚丁为要,丙火次之。忌壬水泛身,须戊土制之。',
                'locator': {'line': 82, 'char_start': 4322, 'char_end': 4349},
                'reason': '同句「忌壬水泛身,须戊土制之」:「壬水泛身」为程度判断而非存在性事实,戊不列为取用序列;只登记不编码。',
            },
        ),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '子', 'month_label': '十一月',
        'section': {'line': 86, 'char_start': 4500, 'char_end': 4678},
        'quote': '十一月甲木,木性生寒,丁先庚後,丙火佐之。',
        'quote_locator': {'line': 86, 'char_start': 4500, 'char_end': 4521},
        'sequence': ({'stem': '丁', 'order': 1}, {'stem': '庚', 'order': 2}, {'stem': '丙', 'order': 3},),
        'order_basis': '原文「丁先庚後,丙火佐之」明示先次,丙为佐为第三级。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': (),
    },
    {
        'month_branch': '丑', 'month_label': '十二月',
        'section': {'line': 90, 'char_start': 4679, 'char_end': 4874},
        'quote': '十二月甲木,天寒气冻,木性极寒,无生发之象,先用庚劈甲,方引丁火始得木火有通明之象,故丁次之。',
        'quote_locator': {'line': 90, 'char_start': 4679, 'char_end': 4726},
        'sequence': ({'stem': '庚', 'order': 1}, {'stem': '丁', 'order': 2},),
        'order_basis': '原文「先用庚劈甲,方引丁火」「故丁次之」明示先次。',
        'branches': (),
        'unencoded_branches': (),
        'related': (),
        'notes': (),
    },
)

_BY_BRANCH = {entry['month_branch']: entry for entry in ENTRIES}


def entry_for(month_branch):
    """Reviewed entry for one month branch, or None."""
    return _BY_BRANCH.get(month_branch)


def _presence(stem, visible_stems, hidden_stems):
    visible_at = [PILLAR_NAMES[i] for i, s in enumerate(visible_stems) if s == stem]
    hidden_at = [f'{PILLAR_NAMES[i]}:{j}' for i, hs in enumerate(hidden_stems)
                 for j, s in enumerate(hs) if s == stem]
    presence = 'visible' if visible_at else 'hidden' if hidden_at else 'absent'
    return {'presence': presence, 'visible_positions': visible_at,
            'hidden_positions': hidden_at}


def _sequence_with_presence(sequence, visible_stems, hidden_stems):
    return [{'stem': item['stem'], 'order': item['order'],
             **_presence(item['stem'], visible_stems, hidden_stems)}
            for item in sequence]


def tiaohou_lookup(day_master, month_branch, visible_stems, hidden_stems):
    """Pure entry lookup over existence facts; no chart computation here.

    visible_stems: the four pillar stems in year/month/day/hour order.
    hidden_stems: per-pillar lists of hidden stems in the same order.
    Malformed input fails closed (ValueError). A non-甲 day master is a
    stated not-applicable result, never an error and never a 甲 entry.
    """
    if type(day_master) is not str or day_master not in STEMS:
        raise ValueError('Tiaohou lookup requires an explicit day master stem')
    if (type(visible_stems) not in (list, tuple) or len(visible_stems) != 4
            or any(type(s) is not str or s not in STEMS for s in visible_stems)):
        raise ValueError('Tiaohou lookup requires four visible stems')
    if (type(hidden_stems) not in (list, tuple) or len(hidden_stems) != 4
            or any(type(hs) not in (list, tuple)
                   or any(type(s) is not str or s not in STEMS for s in hs)
                   for hs in hidden_stems)):
        raise ValueError('Tiaohou lookup requires hidden stems for four pillars')
    if day_master != '甲':
        return {'variant': VARIANT, 'status': 'not_applicable',
                'reason': 'day_master_not_jia', 'actual_day_master': day_master,
                'system': 'tiaohou', 'source_id': SOURCE_ID, 'evidence_level': 'C',
                'research_only': True, 'public_enabled': False, 'ai_enabled': False,
                'evidence_binding': 'pending_phase1_rule_registration',
                'scope': '本 Variant 仅审定甲木十二月条目；其他日主未审定，不套用甲木条目。',
                'limitations': list(LIMITATIONS)}
    if type(month_branch) is not str or month_branch not in _BY_BRANCH:
        raise ValueError('Tiaohou lookup requires one of the twelve month branches')
    entry = _BY_BRANCH[month_branch]
    branches = []
    for branch in entry['branches']:
        absent_stem = branch['condition']['absent_stem']
        applied = _presence(absent_stem, visible_stems,
                            hidden_stems)['presence'] == 'absent'
        branches.append({'id': branch['id'], 'applied': applied,
                         'condition': dict(branch['condition']),
                         'quote': branch['quote'],
                         'locator': dict(branch['locator']),
                         'sequence': _sequence_with_presence(
                             branch['sequence'], visible_stems, hidden_stems),
                         'note': branch['note']})
    return {'variant': VARIANT, 'status': 'matched', 'system': 'tiaohou',
            'source_id': SOURCE_ID, 'evidence_level': 'C',
            'day_master': day_master, 'month_branch': month_branch,
            'month_label': entry['month_label'],
            'entry': {'quote': entry['quote'],
                      'quote_locator': dict(entry['quote_locator']),
                      'section': dict(entry['section']),
                      'order_basis': entry['order_basis']},
            'sequence': _sequence_with_presence(entry['sequence'],
                                                visible_stems, hidden_stems),
            'branches': branches,
            'unencoded_branches': copy.deepcopy(entry['unencoded_branches']),
            'related': copy.deepcopy(entry['related']),
            'notes': list(entry['notes']),
            'research_only': True, 'public_enabled': False, 'ai_enabled': False,
            'evidence_binding': 'pending_phase1_rule_registration',
            'limitations': list(LIMITATIONS)}


def tiaohou_assessment(trace, *, tiaohou_variant=VARIANT):
    """Consume an executed Bazi trace, mirroring the strength adjudication.

    Only facts from executed, evidence-bound trace steps are read; the
    visible/hidden facts are cross-checked against the pillar step so a
    forged or inconsistent trace fails closed instead of being quoted.
    """
    if tiaohou_variant != VARIANT:
        raise ValueError('Unsupported tiaohou variant')
    if getattr(trace, 'domain', None) != 'bazi' or getattr(trace, 'variant', None) != BAZI_VARIANT:
        raise ValueError('Tiaohou assessment requires the Bazi execution variant')
    rule_ids = [step['rule_id'] for step in trace.steps]
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError('Duplicate rule ID in tiaohou trace')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    required = ('pillars', 'ten_gods', 'hidden_stems')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Tiaohou assessment requires executed pillar, ten-god and hidden-stem facts')
    for key in required:
        step = steps['bazi.phase2.' + key][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Tiaohou dependencies lack executed evidence')
    pillars = steps['bazi.phase2.pillars'][1]['output']
    ganzhi = pillars['ganzhi']
    day_master = pillars['day_master']['stem']
    ten_by_pillar = {row['pillar']: row
                     for row in steps['bazi.phase2.ten_gods'][1]['output']}
    hidden_by_pillar = {row['pillar']: row
                        for row in steps['bazi.phase2.hidden_stems'][1]['output']}
    if set(ten_by_pillar) != set(PILLAR_NAMES) or set(hidden_by_pillar) != set(PILLAR_NAMES):
        raise ValueError('Tiaohou factor chain inconsistent: pillar coverage')
    visible = [ten_by_pillar[name]['stem'] for name in PILLAR_NAMES]
    if visible != [g[0] for g in ganzhi]:
        raise ValueError('Tiaohou factor chain inconsistent: visible stems')
    if [hidden_by_pillar[name]['branch'] for name in PILLAR_NAMES] != [g[1] for g in ganzhi]:
        raise ValueError('Tiaohou factor chain inconsistent: hidden stems')
    hidden = [[h['stem'] for h in hidden_by_pillar[name]['hidden_stems']]
              for name in PILLAR_NAMES]
    output = tiaohou_lookup(day_master, ganzhi[1][1], visible, hidden)
    output['consumed_rule_ids'] = ['bazi.phase2.' + key for key in required]
    output['fact_refs'] = {key: f"#/trace/{steps['bazi.phase2.' + key][0]}/output"
                           for key in required}
    return output
