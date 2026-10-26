"""《神峰通考》病药结构候选研究 Variant（TJ-013 病药线首切片）：只报结构候选，不作裁定。

治理定位：Source 已登记为 bazi.source.shenfeng（C 级，单一电子谱系，
daizhigev20 固定快照，422432 字节 / 154642 字符）。全书病药体系陈述
集中于病药说类定义节（快照第 38 行，字符 7014–7680）与四病四药诸节；
本 Variant 编码定义节示例二、示例三两句给出的两组条件形态病药对：
示例二（字符 7351「如用财见比肩为病，喜见官杀为药也」）——所论之神
为财时，显干见比劫为病候选，显干见官杀为药候选；示例三（字符 7368
「如用食神伤官，以印为病，喜财为药也」）——所论之神为食伤时，显干
见印为病候选，显干见财为药候选。两对主体不同（财为日主所克之神，
食伤为日主所生之神），同一命盘逐对独立评估、逐对陈述，永不合并为
单一病药结论。其余病药文字（示例一土重、四病四药、格论太弱太旺口
径）或缺操作定义、或系行运之药、或与定义节口径未统一，只登记不编
码，逐项见本模块 QUOTES 与 LIMITATIONS。

审定点（实现批逐项留痕，与审源报告 tj013-bingyao-scout §4.3 对位）：
- S1「用财」读法：读作「所论之神为财」，不读作格局用神。依据：同句
  下句「如用食神伤官」与之平行，若作用神义则两句都预设格局已定，与
  定义节通篇不论格局的语境不合；定义节开篇以「原所害之神」立病，
  本节是总定义而非格论。若将来审定改作用神义读法，本 Variant 即被
  格局裁定缺位阻塞，须降级为仅登记，不得静默沿用。第二对「用食神
  伤官」的「用」与「用财」同构（两句相邻并列、句式全同），同一读法
  一体适用；若改作用神义，两对同被阻塞、同走降级路径。
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

输出形态：顶层字段保持首切片（财对）的语义不变（status / subject /
disease_candidate / medicine_candidate / medicine_status /
not_triggered_reason / rule 均指第一对），另以 pairs 列表逐对给出两
对的完整独立陈述（每对自带 rule、status、主体/病/药构成与未触发原
因）；既有消费方按顶层字段消费不受影响，第二对只经 pairs 并列携
带，不改变任何顶层字段的含义。

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

关于双对同盘：两对触发共需财、比劫、食伤、印四类显干，而非日主显
干只有年、月、时三位——双对同时触发在真实命盘中算术上不可出现
（与上文冲突例同型），Golden 登记于 unrealizable_designs 并附算术
证明，不以合成盘面充数；公开全域扫描断言任意显干组合下至多一对
triggered。双对一触发一不触发则真实可达，Golden 双对例钉住。

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
from .foundations import CONTROLS, GENERATES, STEMS, stem_element

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
FOODWOUND_GODS = ('食神', '伤官')
SEAL_GODS = ('正印', '偏印')
TEN_GOD_NAMES = frozenset((
    '比肩', '劫财', '食神', '伤官', '偏财', '正财',
    '七杀', '正官', '偏印', '正印',
))

DEFINITION_SECTION = {'line': 38, 'char_start': 7019, 'char_end': 7680}

RULES = (
    {
        'pair_id': 'wealth_peer_officer',
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
    },
    {
        'pair_id': 'foodwound_seal_wealth',
        'id': 'shenfeng.foodwound_seal_wealth',
        'subject_god_class': '食伤',
        'subject_gods': FOODWOUND_GODS,
        'disease_god_class': '印',
        'disease_gods': SEAL_GODS,
        'medicine_god_class': '财',
        'medicine_gods': WEALTH_GODS,
        'quote': '如用食神伤官,以印为病,喜财为药也',
        'quote_locator': {'line': 38, 'char_start': 7368, 'char_end': 7385},
        'section': DEFINITION_SECTION,
    },
)

# 首切片兼容别名：顶层输出的 rule 字段与既有消费方均指第一对。
RULE = RULES[0]

# 逐对的未触发原因与病对主体的关系陈述（原句口径，逐对写明，不合并）。
_PAIR_META = {
    'wealth_peer_officer': {
        'subject_missing_reason': 'subject_wealth_not_visible',
        'disease_missing_reason': 'peer_god_not_visible',
        'disease_relation': '比劫为所论之财的所害之神（按原句）',
    },
    'foodwound_seal_wealth': {
        'subject_missing_reason': 'subject_foodwound_not_visible',
        'disease_missing_reason': 'seal_god_not_visible',
        'disease_relation': '印为所论之食伤的所害之神（按原句）',
    },
}

# 登记引文：encoded 为 RULES 两条（wealth_pair、food_pair）；其余为审定登记（定义、
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
        'note': '本 Variant 编码的第一对（RULES 第一条，wealth_peer_officer）。',
    },
    {
        'id': 'food_pair', 'role': 'encoded_rule',
        'source_id': SOURCE_ID,
        'quote': '如用食神伤官,以印为病,喜财为药也',
        'locator': {'line': 38, 'char_start': 7368, 'char_end': 7385},
        'note': '第二对（食伤—印—财），形态与财对同构，本批编码为 RULES 第二条（foodwound_seal_wealth）。',
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
    '本 Variant 编码《神峰通考》病药说类定义节示例二、示例三两对（财—比劫—官杀；食伤—印—财）；示例一（土重）的前提无操作定义，四病四药或缺阈值判据或是行运之药，均不在本 Variant 范围。',
    '存在性口径只计显干（年、月、时三干），不计藏干（审定点 S3）；两对的主体与病、药均按此口径，藏干中出现的财、比劫、官杀、食伤、印不触发、不补位。',
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
    'S1 延伸（第二对）：「用食神伤官」的「用」与首对「用财」同构——两句在定义节中相邻并列（字符 7351–7385），句式全同（用 X、见/以 Y 为病、喜 Z 为药），同读作所论之神；若改作用神义，两对同被格局裁定缺位阻塞，降级路径与首对相同。',
    'S2 类读延伸（第二对）：食伤取食神、伤官两神（原句并列明言「食神伤官」，非类推）；印取正印、偏印（原句单言「印」，按十神类读，与首对「比肩」取比劫类同例）；财取正财、偏财（与首对主体财同一类读）。各类成员在规则表逐项写明，Golden 以伤官、偏印、偏财同盘例钉住各类的第二成员。',
    'S4 延伸（第二对）：食伤显一字即触发第二对候选（与首对财显一字同口径）；「从重者论」的未尽事项同样适用，不另设门槛。',
    '双对独立：两对主体不同（财为日主所克，食伤为日主所生），同盘逐对独立评估、逐对陈述（pairs），不合并为单一病药结论；一对的部分事实（如食伤已显而印未显）不借给另一对，顶层字段保持第一对语义不变。',
    '双对同触发不可实现：两对触发共需财、比劫、食伤、印四个互异十神类各至少一显干，非日主显干只有年、月、时三位，鸽笼原理下真实命盘不可出现；已登记 Golden unrealizable_designs 并附算术证明，不以合成盘面充数，公开全域扫描断言至多一对 triggered。',
)


# 十神类之五行相对日主五行的生克像：比劫=本行、食伤=我生之行、
# 财=我克之行、官杀=克我之行、印=生我之行（十神定义本身）。
_CLASS_ELEMENT = {
    '比劫': lambda e: e,
    '食伤': lambda e: GENERATES[e],
    '财': lambda e: CONTROLS[e],
    '官杀': lambda e: next(x for x in CONTROLS if CONTROLS[x] == e),
    '印': lambda e: next(x for x in GENERATES if GENERATES[x] == e),
}


def _assert_rule_coherence():
    # 编码时自检（审源报告 §4.2）：任意日主下，两对的「药克病、病克
    # 主体」结构关系都由十神类定义构造恒立——主体/病/药之五行只是
    # 日主五行经生克关系的像，不依赖任何未审关系表。此处以
    # foundations 的 GENERATES/CONTROLS 逐对逐行断言该构造关系，
    # 并断言三类成员互不相交且均为合法十神名，防止类常量被误改。
    for rule in RULES:
        classes = (rule['subject_gods'], rule['disease_gods'],
                   rule['medicine_gods'])
        flat = [g for gods in classes for g in gods]
        assert len(flat) == len(set(flat))
        assert set(flat) <= TEN_GOD_NAMES
        for element in ('木', '火', '土', '金', '水'):
            subject = _CLASS_ELEMENT[rule['subject_god_class']](element)
            disease = _CLASS_ELEMENT[rule['disease_god_class']](element)
            medicine = _CLASS_ELEMENT[rule['medicine_god_class']](element)
            assert CONTROLS[medicine] == disease
            assert CONTROLS[disease] == subject


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


def _evaluate_pair(rule, rows):
    """Evaluate one bingyao pair over validated visible fact rows.

    Pure per-pair statement: a pair triggers only when its subject god
    class and its disease god class are both attested in visible stems;
    the medicine candidate is reported present/absent, never inferred.
    Each pair is evaluated on its own facts — no fact is borrowed from
    the other pair — and a non-triggered pair is an abstention of that
    pair only, never a 「无病」 statement.
    """
    meta = _PAIR_META[rule['pair_id']]
    subject = [r for r in rows if r['ten_god'] in rule['subject_gods']]
    disease = [r for r in rows if r['ten_god'] in rule['disease_gods']]
    medicine = [r for r in rows if r['ten_god'] in rule['medicine_gods']]
    pair = {
        'pair_id': rule['pair_id'],
        'rule': dict(rule),
        'subject': {'god_class': rule['subject_god_class'], 'gods': subject},
        'determination': None,
        'medicine_effect_status': 'unadjudicated',
    }
    if not subject or not disease:
        return {**pair, 'status': 'not_triggered',
                'disease_candidate': None, 'medicine_candidate': None,
                'medicine_status': None,
                'not_triggered_reason': (
                    meta['subject_missing_reason'] if not subject
                    else meta['disease_missing_reason'])}
    disease_block = {'god_class': rule['disease_god_class'],
                     'gods': disease,
                     'relation_to_subject': meta['disease_relation']}
    if not medicine:
        return {**pair, 'status': 'triggered',
                'disease_candidate': disease_block,
                'medicine_candidate': None, 'medicine_status': 'absent'}
    medicine_block = {
        'god_class': rule['medicine_god_class'], 'gods': medicine,
        'structural_relation': 'medicine_element_controls_disease_element',
        'medicine_element': stem_element(medicine[0]['stem']),
        'disease_element': stem_element(disease[0]['stem']),
    }
    return {**pair, 'status': 'triggered',
            'disease_candidate': disease_block,
            'medicine_candidate': medicine_block,
            'medicine_status': 'candidate_present'}


def bingyao_lookup(day_master, visible_gods):
    """Pure structural-candidate lookup over visible ten-god facts.

    visible_gods: three fact rows {'pillar', 'stem', 'ten_god'} for the
    year, month and hour pillars (the day pillar carries no ten-god).
    Only visible stems are read; hidden stems are never consulted, so a
    god attested only in hidden stems cannot trigger or complete either
    pair. Both encoded pairs are evaluated independently and reported
    side by side under 'pairs'; the top-level fields keep the first
    pair's (wealth) semantics unchanged from the first slice. Malformed
    input fails closed (ValueError). A pair that does not trigger is
    reported as not_triggered, never as 「无病」.
    """
    rows = _validate_visible_gods(day_master, visible_gods)
    pairs = [_evaluate_pair(rule, rows) for rule in RULES]
    first = pairs[0]
    output = {
        'variant': VARIANT, 'system': 'bingyao',
        'source_id': SOURCE_ID, 'evidence_level': 'C',
        'day_master': day_master,
        'subject': first['subject'],
        'status': first['status'],
        'disease_candidate': first['disease_candidate'],
        'medicine_candidate': first['medicine_candidate'],
        'medicine_status': first['medicine_status'],
        'determination': None,
        'medicine_effect_status': 'unadjudicated',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'evidence_binding': 'pending_phase1_rule_registration',
        'rule': dict(RULE),
        'pairs': pairs,
        'adjudication_notes': list(ADJUDICATION_NOTES),
        'scope_limits': list(LIMITATIONS),
    }
    if first['status'] == 'not_triggered':
        output['not_triggered_reason'] = first['not_triggered_reason']
    return output


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
