"""《神峰通考》病药结构候选研究 Variant（TJ-013 病药线首切片）：只报结构候选，不作裁定。

治理定位：Source 已登记为 bazi.source.shenfeng（C 级，单一电子谱系，
daizhigev20 固定快照，422432 字节 / 154642 字符）。全书病药体系陈述
集中于病药说类定义节（快照第 38 行，字符 7014–7680）与四病四药诸节；
本 Variant 只编码定义节示例二一句（字符 7351「如用财见比肩为病，喜见
官杀为药也」）给出的一组条件形态病药对：所论之神为财时，显干见比劫
为病候选，显干见官杀为药候选。其余病药文字（示例一土重、示例三食伤
对、四病四药、格论太弱太旺口径）或缺操作定义、或系行运之药、或与定
义节口径未统一，只登记不编码，逐项见本模块 QUOTES 与 LIMITATIONS。

审定点（实现批逐项留痕，与审源报告 tj013-bingyao-scout §4.3 对位）：
- S1「用财」读法：读作「所论之神为财」，不读作格局用神。依据：同句
  下句「如用食神伤官」与之平行，若作用神义则两句都预设格局已定，与
  定义节通篇不论格局的语境不合；定义节开篇以「原所害之神」立病，
  本节是总定义而非格论。若将来审定改作用神义读法，本 Variant 即被
  格局裁定缺位阻塞，须降级为仅登记，不得静默沿用。
- S2「比肩」类界：取比劫类（比肩、劫财）。依据：本书土重例对火日主
  言「比肩太重」指同行之神的类聚，非仅同阴阳一字；十神治理中夺财
  之害素以比劫并称。此为类读，Golden 中另设劫财单见例钉住分界。
- S3 存在性口径：只计显干（年/月/时三干），不计藏干。原句用「见」
  （见比肩/喜见官杀），与透出事实同口径；藏干纳入会使候选失去区
  分度。此口径由 Golden 双边界例钉死，改口径须另立 Variant。
- S4 主体门槛：财显一字即触发候选（候选语义本身即弱断言）；定义节
  程序句「从重者论」（字符 7505）提示判断以重者为对象，但书
  中无「重」之阈值，本 Variant 不声称已按从重选定唯一病神，该未
  尽事项写入 LIMITATIONS。

定位与硬边界：输出与格局候选同级——结构候选，不是病药裁定。
determination 恒为 None；不输出「命有病/无病」结论（「无病」的成立
要求整盘不旺不弱且中和的裁定，本平台无此能力，故本模块不存在输出
「无病」的代码路径，未命中只能记 not_triggered）；药候选只陈述其存
在与「药之五行克病之五行」的结构关系，去病效力
（medicine_effect_status）恒为未裁定，不输出「药已去病」；不把候选
翻译成吉凶、喜用神或现实预测；与调候 Variant
（tiaohou-qiongtong-v1）并列，任何层不得把两者输出合并为统一喜用
结论。本 Variant 恒 research_only=True、public_enabled=False、
ai_enabled=False。

关于审源设计的冲突例（药被伤官所克）：四柱显干中非日主位只有年、
月、时三位，财、比劫、官杀三类各占其一时已无第四位容纳克药之食伤
干——该构形在真实命盘中算术上不可出现（审源报告 §4.5 冲突例的柱级
设计隐含了第四个非日主显干）。故本 Variant 不设「药受制」子状态：
药的效力由 medicine_effect_status 恒未裁定一并覆盖「不得断言已去
病」的守卫，Golden 以劫财分界例与输出字段全域断言钉住此边界，不以
不可实现的盘面充数。

执行链接入方式与调候相同：engine.execute 以 allow_research 门控，
operations.bazi_chart.chart 以 bingyao_variant 显式开启，本模块的
bingyao_assessment 只消费已执行的 trace 步骤（pillars / ten_gods，
且要求其 evidence 已绑定），伪造或缺失事实一律 fail-closed。与调候
先例相同的一点如实说明：本 Variant 尚无密封 Phase1 bundle /
Phase2 contract 的 rule 注册，故 assessment 附于 result 而不新增
trace rule，不进 RuleMatch 与 Evidence，evidence_binding 标记为
pending_phase1_rule_registration，不得冒充已绑定证据的裁决。
"""
from .bazi_core import VARIANT as BAZI_VARIANT
from .foundations import CONTROLS, STEMS, stem_element

VARIANT = 'bingyao-shenfeng-v1'
SOURCE_ID = 'bazi.source.shenfeng'
SNAPSHOT_PATH = 'data/quarantine/public_domain_snapshots/daizhigev20/shenfeng_tongkao.txt'
SNAPSHOT_SHA256 = '121a571b7fa63e073f067d5532a42e2feb7d4d5fdd7874de2ca48036a615e200'
SNAPSHOT_BYTES = 422432
SNAPSHOT_CHARS = 154642

# 制衡旁证（同谱系，不构成第二独立底本）：《滴天髓阐微》中和篇任氏注。
COUNTERWEIGHT_SOURCE_ID = 'bazi.source.ditiansui-spouse'
COUNTERWEIGHT_SNAPSHOT_PATH = 'data/quarantine/public_domain_snapshots/daizhigev20/ditiansui_chanwei.txt'

PILLAR_NAMES = ('year', 'month', 'day', 'hour')
VISIBLE_PILLARS = ('year', 'month', 'hour')

WEALTH_GODS = ('正财', '偏财')
PEER_GODS = ('比肩', '劫财')
OFFICER_GODS = ('正官', '七杀')
TEN_GOD_NAMES = frozenset((
    '比肩', '劫财', '食神', '伤官', '偏财', '正财',
    '七杀', '正官', '偏印', '正印',
))

DEFINITION_SECTION = {'line': 38, 'char_start': 7019, 'char_end': 7680}

RULE = {
    'id': 'shenfeng.wealth_peer_officer',
    'subject_god_class': '财',
    'subject_gods': WEALTH_GODS,
    'disease_god_class': '比劫',
    'disease_gods': PEER_GODS,
    'medicine_god_class': '官杀',
    'medicine_gods': OFFICER_GODS,
    'quote': '如用财见比肩为病,喜见官杀为药也',
    'quote_locator': {'line': 38, 'char_start': 7351, 'char_end': 7367},
    'section': DEFINITION_SECTION,
}

# 登记引文：encoded 只有 RULE 一条；其余为审定登记（定义、平行对、
# 程序、否定侧条款、书内张力、制衡旁证），逐字以固定快照为准，快照
# 为简体转写，不作简繁转换。每条在快照全文中恰出现一次，密封专项
# 逐条核对（tests/test_tj013_bingyao_sealed.py）。
QUOTES = (
    {
        'id': 'disease_definition', 'role': 'definition',
        'source_id': SOURCE_ID,
        'quote': '何以为之病?原八字中原所害之神也',
        'locator': {'line': 38, 'char_start': 7019, 'char_end': 7035},
        'note': '病之定义：局中「所害之神」。「害」的具体枚举由同节示例句给出。',
    },
    {
        'id': 'medicine_definition', 'role': 'definition',
        'source_id': SOURCE_ID,
        'quote': '何以为之药?如八字原有所害之字,而得一字以去之谓了',
        'locator': {'line': 38, 'char_start': 7036, 'char_end': 7061},
        'note': '药之定义：能去病之字。本节示例中「去」的机制均为五行克；实际克效未裁定。',
    },
    {
        'id': 'wealth_pair', 'role': 'encoded_rule',
        'source_id': SOURCE_ID,
        'quote': '如用财见比肩为病,喜见官杀为药也',
        'locator': {'line': 38, 'char_start': 7351, 'char_end': 7367},
        'note': '本 Variant 唯一编码的病药对（RULE）。',
    },
    {
        'id': 'food_pair', 'role': 'registered_not_encoded',
        'source_id': SOURCE_ID,
        'quote': '如用食神伤官,以印为病,喜财为药也',
        'locator': {'line': 38, 'char_start': 7368, 'char_end': 7385},
        'note': '第二对（食伤—印—财），形态与财对同构，列为扩展候选，本批不编码、不验收。',
    },
    {
        'id': 'earth_example', 'role': 'registered_not_encoded',
        'source_id': SOURCE_ID,
        'quote': '是则土为诸格之病,俱喜木为医药,以去其病也',
        'locator': {'line': 38, 'char_start': 7329, 'char_end': 7350},
        'note': '示例一（土重）结论句：其前提「四柱纯土水」无操作定义，且分日主结论为旺弱味断语，不编码。',
    },
    {
        'id': 'procedure_zhong', 'role': 'registered_not_encoded',
        'source_id': SOURCE_ID,
        'quote': '又或地支虽又藏有别物,且不必看,若再看别物,由混杂不明,故曰:从重者论',
        'locator': {'line': 38, 'char_start': 7505, 'char_end': 7540},
        'note': '看法程序：判断以重者为对象。但「重」无阈值，本 Variant 只陈述示例对的存在性命中，不声称已按从重选定唯一病神（见 S4）。',
    },
    {
        'id': 'no_disease_clause', 'role': 'registered_not_encoded',
        'source_id': SOURCE_ID,
        'quote': '如八字纯然不旺不弱,原财官印俱无损伤,日干之气,又得中和,并无起发可观,此是平常人也',
        'locator': {'line': 38, 'char_start': 7605, 'char_end': 7647},
        'note': '否定侧条款：无病（平常）的成立要求不旺不弱加中和的整盘裁定，本平台无此能力；本 Variant 永不输出「无病」，未命中只记未触发。',
    },
    {
        'id': 'zhengguan_tension', 'role': 'registered_tension',
        'source_id': SOURCE_ID,
        'quote': '惟官星太弱太旺,方为有病,因其病而药之,斯可作为用神而论祸福也',
        'locator': {'line': 51, 'char_start': 10010, 'char_end': 10041},
        'note': '正官格节另一口径：病系于官星太弱太旺，与定义节存在性口径并存未统一；该口径依赖旺弱裁定且直通用神，本 Variant 不覆盖、不得引此句升级候选为用神结论。',
    },
    {
        'id': 'ditiansui_counterweight', 'role': 'counterweight',
        'source_id': COUNTERWEIGHT_SOURCE_ID,
        'quote': '若所谓“有病有药,吉凶易验,无病地药,祸福难推”,此论仍乃失之偏。大凡有病者显而易取,无病者隐而难推。然总以中和为主',
        'locator': {'line': 1896, 'char_start': 43767, 'char_end': 43825},
        'note': '《滴天髓阐微》中和篇任氏制衡：病药之论「仍乃失之偏」，总以中和为主。与神峰同为 daizhigev20 单一谱系，只作 limitations 制衡证据，不构成第二独立底本。快照作「无病地药」，字形如实保留。',
    },
)

LIMITATIONS = (
    '本 Variant 只编码《神峰通考》病药说类定义节示例二一对（财—比劫—官杀）；示例一（土重）的前提无操作定义、示例三（食伤对）未编码，四病四药或缺阈值判据或是行运之药，均不在本 Variant 范围。',
    '存在性口径只计显干（年、月、时三干），不计藏干（审定点 S3）；主体财与病、药均按此口径，藏干中出现的财、比劫、官杀不触发、不补位。',
    '本 Variant 未按定义节「从重者论」选定唯一病神：「重」在书中无阈值，切片只陈述示例对的存在性命中（审定点 S4）。',
    '药候选只陈述存在与「药之五行克病之五行」的结构关系，去病效力恒未裁定；药存在不等于病已去，本 Variant 不输出「药已去病」。',
    '本 Variant 永不输出「无病」：无病（平常）的成立要求整盘不旺不弱且中和的裁定（定义节否定侧条款），本平台无此能力；未命中只记未触发。',
    '正官格节「惟官星太弱太旺，方为有病」口径（字符 10010）与定义节口径并存未统一，本 Variant 不覆盖太弱太旺型之病，不得引该句把候选升级为用神结论。',
    '《滴天髓阐微》中和篇任氏注明言病药之论「仍乃失之偏」「总以中和为主」（字符 43767），病药说非通则，本 Variant 的候选陈述须与此制衡同读。',
    '审定点 S1：「用财」按所论之神读法审定（依据同节平行句与总定义语境）；若改作用神义，本 Variant 应被格局裁定缺位阻塞并降级，不得静默沿用。',
    '来源为 C 级单一电子谱系（简体转写），未做全书逐字校勘，已见个别讹字与一处重文，未订正；同书末篇「病源赋」为身体疾病占验文字，属排除范围，本 Variant 不引用。',
    '与调候 Variant 并列而非合并：病药候选不得与调候、扶抑、格局用神的输出合并为统一「喜用神」结论。',
    '本 Variant 尚未在密封 Phase1 bundle/Phase2 contract 注册 rule，不进 RuleMatch 与 Evidence。',
)

ADJUDICATION_NOTES = (
    'S1 用财=所论之神（非格局用神）：同句下句「如用食神伤官」平行，定义节通篇不论格局，开篇以「原所害之神」立病。备选读法（用神义）若成立，本切片被格局裁定缺位阻塞，降级路径为仅登记 Source 与定义节审定存档。',
    'S2 比肩取比劫类（比肩、劫财）：本书土重例以「比肩太重」指同行类聚；夺财之害以比劫并称。Golden 劫财单见例钉住此类界。',
    'S3 只计显干：原句用「见」；藏干不计。Golden 双边界例（比劫仅藏干、财仅藏干）钉住此口径。',
    'S4 财显一字即触发候选；「从重者论」的未尽事项写入 LIMITATIONS，不另设门槛。',
    '冲突例处置：药被食伤所克的构形需第四个非日主显干位，真实命盘中不可出现（年、月、时三位已被财、比劫、官杀占满）；效力守卫由 medicine_effect_status 恒未裁定承担，不设不可达成的子状态，不以合成盘面充数。',
)


def _assert_rule_coherence():
    # 编码时自检（审源报告 §4.2）：任意日主下，官杀之五行 = 克日主
    # 之行，比劫之五行 = 日主本行，故「药克病」的结构关系由十神类
    # 定义构造恒立，不依赖任何未审关系表。此处以 foundations 的
    # CONTROLS 逐行断言该构造关系，防止类常量被误改。
    for element in ('木', '火', '土', '金', '水'):
        officer = next(x for x in CONTROLS if CONTROLS[x] == element)
        assert CONTROLS[officer] == element


_assert_rule_coherence()


def _validate_visible_gods(day_master, visible_gods):
    if type(day_master) is not str or len(day_master) != 1 \
            or day_master not in STEMS:
        raise ValueError('Bingyao lookup requires an explicit day master stem')
    if type(visible_gods) not in (list, tuple) or len(visible_gods) != 3:
        raise ValueError('Bingyao lookup requires visible ten-god facts '
                         'for the year, month and hour pillars')
    rows = []
    seen = set()
    for row in visible_gods:
        if not isinstance(row, dict) \
                or set(row) != {'pillar', 'stem', 'ten_god'}:
            raise ValueError('Bingyao visible fact rows must carry exactly '
                             'pillar, stem and ten_god')
        pillar, stem, ten_god = row['pillar'], row['stem'], row['ten_god']
        if pillar not in VISIBLE_PILLARS or pillar in seen:
            raise ValueError('Bingyao visible facts must cover year, month '
                             'and hour exactly once')
        if type(stem) is not str or len(stem) != 1 or stem not in STEMS:
            raise ValueError('Bingyao visible fact stem must be one heavenly stem')
        if ten_god not in TEN_GOD_NAMES:
            raise ValueError('Bingyao visible fact ten_god must be one of '
                             'the ten canonical ten-god names')
        seen.add(pillar)
        rows.append({'pillar': pillar, 'stem': stem, 'ten_god': ten_god})
    if seen != set(VISIBLE_PILLARS):
        raise ValueError('Bingyao visible facts must cover year, month and hour')
    rows.sort(key=lambda r: VISIBLE_PILLARS.index(r['pillar']))
    return rows


def bingyao_lookup(day_master, visible_gods):
    """Pure structural-candidate lookup over visible ten-god facts.

    visible_gods: three fact rows {'pillar', 'stem', 'ten_god'} for the
    year, month and hour pillars (the day pillar carries no ten-god).
    Only visible stems are read; hidden stems are never consulted, so a
    god attested only in hidden stems cannot trigger or complete the
    pair. Malformed input fails closed (ValueError). A chart that does
    not trigger is reported as not_triggered, never as 「无病」.
    """
    rows = _validate_visible_gods(day_master, visible_gods)
    wealth = [r for r in rows if r['ten_god'] in WEALTH_GODS]
    peers = [r for r in rows if r['ten_god'] in PEER_GODS]
    officers = [r for r in rows if r['ten_god'] in OFFICER_GODS]
    base = {
        'variant': VARIANT, 'system': 'bingyao',
        'source_id': SOURCE_ID, 'evidence_level': 'C',
        'day_master': day_master,
        'subject': {'god_class': '财', 'gods': wealth},
        'determination': None,
        'medicine_effect_status': 'unadjudicated',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
        'rule': dict(RULE),
        'adjudication_notes': list(ADJUDICATION_NOTES),
        'scope_limits': list(LIMITATIONS),
    }
    if not wealth or not peers:
        return {**base, 'status': 'not_triggered',
                'disease_candidate': None, 'medicine_candidate': None,
                'medicine_status': None,
                'not_triggered_reason': (
                    'subject_wealth_not_visible' if not wealth
                    else 'peer_god_not_visible')}
    disease = {'god_class': '比劫', 'gods': peers,
               'relation_to_subject': '比劫为所论之财的所害之神（按原句）'}
    if not officers:
        return {**base, 'status': 'triggered',
                'disease_candidate': disease, 'medicine_candidate': None,
                'medicine_status': 'absent'}
    medicine = {
        'god_class': '官杀', 'gods': officers,
        'structural_relation': 'medicine_element_controls_disease_element',
        'medicine_element': stem_element(officers[0]['stem']),
        'disease_element': stem_element(peers[0]['stem']),
    }
    return {**base, 'status': 'triggered',
            'disease_candidate': disease, 'medicine_candidate': medicine,
            'medicine_status': 'candidate_present'}


def bingyao_assessment(trace, *, bingyao_variant=VARIANT):
    """Consume an executed Bazi trace, mirroring the tiaohou assessment.

    Only facts from executed, evidence-bound trace steps are read; the
    ten-god facts are cross-checked against the pillar step so a forged
    or inconsistent trace fails closed instead of being quoted. A trace
    without the executed ten-god step is an abstention (ValueError),
    never a silently empty candidate.
    """
    if bingyao_variant != VARIANT:
        raise ValueError('Unsupported bingyao variant')
    if getattr(trace, 'domain', None) != 'bazi' or getattr(trace, 'variant', None) != BAZI_VARIANT:
        raise ValueError('Bingyao assessment requires the Bazi execution variant')
    rule_ids = [step['rule_id'] for step in trace.steps]
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError('Duplicate rule ID in bingyao trace')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    required = ('pillars', 'ten_gods')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Bingyao assessment requires executed pillar and ten-god facts')
    for key in required:
        step = steps['bazi.phase2.' + key][1]
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Bingyao dependencies lack executed evidence')
    pillars = steps['bazi.phase2.pillars'][1]['output']
    ganzhi = pillars['ganzhi']
    day_master = pillars['day_master']['stem']
    ten_by_pillar = {row['pillar']: row
                     for row in steps['bazi.phase2.ten_gods'][1]['output']}
    if set(ten_by_pillar) != set(PILLAR_NAMES):
        raise ValueError('Bingyao factor chain inconsistent: pillar coverage')
    visible = [ten_by_pillar[name]['stem'] for name in PILLAR_NAMES]
    if visible != [g[0] for g in ganzhi]:
        raise ValueError('Bingyao factor chain inconsistent: visible stems')
    if ten_by_pillar['day']['ten_god'] != '日主':
        raise ValueError('Bingyao factor chain inconsistent: day pillar ten-god')
    facts = [{'pillar': name, 'stem': ten_by_pillar[name]['stem'],
              'ten_god': ten_by_pillar[name]['ten_god']}
             for name in VISIBLE_PILLARS]
    output = bingyao_lookup(day_master, facts)
    output['consumed_rule_ids'] = ['bazi.phase2.' + key for key in required]
    output['fact_refs'] = {key: f"#/trace/{steps['bazi.phase2.' + key][0]}/output"
                           for key in required}
    return output
