"""大运古典证据 Variant（TJ-017.1）：方向（三命主句+神峰旁证）与换算（三命时级 / 神峰日级分立）。

治理定位：证据来自两个已登记 Source——
- bazi.source.sanmingtonghui（《三命通会》daizhigev20 固定快照，C 级，
  1,342,659 字节 / 461,157 字符，SHA256 00e2a7db…）。整书仍
  quarantine_only、canonical_ready=false（全书 PUA 524 处）；本批只审定
  卷二《论大运》节（字符 58457–59198，规则核心 58594–59060 零 PUA）
  与卷十一《珞琭子消息赋》注两处见证窗口，不构成整书晋级。
- bazi.source.shenfeng（《神峰通考》，C 级，已由 TJ-013 登记）：本批扩
  展审定其《起大运法》节（字符 85001–85246）。

审源裁定（tj0171-evidence-scout）要点与本模块的对应：
- 方向：三命规则句把方向与计数目标绑定为一条规则，神峰四例逐一实例
  化四象限，卷十一赋注另有两处书内见证；与现代还原候选
  （bazi-dayun-modern-restoration-candidate-v1）四象限零分歧——候选保
  留为历史记录，古典据自本批起为首要登记。两书的年干阴阳均为「例
  定」（甲子=阳、乙丑=阴），外延与通行干阴阳表一致；本模块如实标注
  例定来源，不冒充书中有抽象定义句。
- 换算（三命时级）：比率推导（3 日=36 时→360 日为一嵗；1 时=10 日）
  、余数零/借 doctrine（时粒度线性结转）、明文反约整，全部有原文。
  交运闰月子句（「内小六个月即进六日」）语义未明，整段排除，只登记。
  节选择只有例证一致（立春/惊蛰皆节、「六节」用词）与书内自承的
  「就生就节互异」披露，无排斥中气的明文，scope 如实写此限定。
- 换算（神峰日级）：日级粒度（整日计数、1 日=120 日），四例中例 2
  日数转写讹乱禁用。与三命时级法分立为两个 Variant，永不合并、不
  互相覆盖、结果必带口径标签。
- 年龄口径：在场五书全文检索「虚岁/实岁/足岁」零命中，无原典口径。
  古典起运龄是自出生起算的实历时长，不经过年龄计数。故本模块输出
  只有起运时长区间与交运时刻区间，不含任何年龄数值字段；现行
  refuse_age_counting_conversion（拒绝两制互换）保留不变。

输出契约（硬边界）：
- 精确单点交运日期在类型层不存在：输出只有 handover_intervals（每项
  earliest/latest/max_inclusive），不存在 handover_datetime/start_date
  等单点字段；起运时长只有 duration_interval_days 区间。
- 恰逢节瞬间（实历计数为零）维持 TJ-016.2 既有拒绝口径
  （zero_jie_boundary_convention_unreviewed），原文例算未覆盖此情形，
  不得默认时长为零；神峰日级零计数同理拒绝。
- 反约整：换算不提供任何取整路径；调用方显式传入 rounding 一律拒
  绝（三命反约法句为据）。
- 亚时余数：原文计数以时为粒度，亚时（<1 时）余数无原文处理，只许
  以区间上端表达（+10 日、上端不含），不按比例折算为单点冒充原文。
- 与调候/病药先例相同的一点如实说明：本批 Variant 尚无密封 Phase1
  bundle / Phase2 contract 的 rule 注册，evidence_binding 标记为
  pending_phase1_rule_registration，不进 RuleMatch 与 Evidence。
- 本模块恒 research_only=True、public_enabled=False、
  ai_enabled=False；不接入公开场景，生产 dayun 显示口径不变。
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .bazi_dayun_direction import traditional_direction
from .bazi_dayun_jie import adjacent_jie_distance
from .calendar import PROVIDER
from .foundations import STEMS, ganzhi_index

DIRECTION_VARIANT = 'dayun-direction-classical-v1'
CONVERSION_VARIANT = 'dayun-conversion-sanming-v1'
SHENFENG_CONVERSION_VARIANT = 'dayun-conversion-shenfeng-v1'
MODERN_CANDIDATE_VARIANT = 'bazi-dayun-modern-restoration-candidate-v1'

SANMING_SOURCE_ID = 'bazi.source.sanmingtonghui'
SANMING_SNAPSHOT_PATH = ('data/quarantine/public_domain_snapshots/'
                         'daizhigev20/sanming_tonghui.txt')
SANMING_SNAPSHOT_SHA256 = ('00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc'
                           '111e62b59378010c86')
SANMING_SNAPSHOT_BYTES = 1342659
SANMING_SNAPSHOT_CHARS = 461157

SHENFENG_SOURCE_ID = 'bazi.source.shenfeng'
SHENFENG_SNAPSHOT_PATH = ('data/quarantine/public_domain_snapshots/'
                          'daizhigev20/shenfeng_tongkao.txt')
SHENFENG_SNAPSHOT_SHA256 = ('121a571b7fa63e073f067d5532a42e2feb7d4d5fdd'
                            '7874de2ca48036a615e200')
SHENFENG_SNAPSHOT_BYTES = 422432
SHENFENG_SNAPSHOT_CHARS = 154642

CHINA = ZoneInfo('Asia/Shanghai')

SECONDS_PER_DAY = 86400
SHICHEN_SECONDS = 7200            # 一时（时辰）= 2 小时；原文以时计数
DAYS_PER_SHICHEN = 10             # 一时 = 一旬 = 10 日（63 时→630 日）
SHICHEN_PER_YEAR_UNIT = 36        # 三日有三十六时，乃见三百六十日为一嵗
DAYS_PER_YEAR_UNIT = 360
DAYS_PER_COUNTED_DAY = 120        # 神峰日级 / 三命同率：1 日 = 120 日（四月）
MAX_PERIODS = 12

YANG_STEMS = frozenset('甲丙戊庚壬')
YIN_STEMS = frozenset('乙丁己辛癸')
# 两书均未在规则句内抽象定义年干阴阳，而以年柱例固定（甲子=阳、乙丑
# =阴；三命元辰诸节与神峰四例同）。下表外延与现代候选的显式定义一致，
# 呈现方式不同，此差异如实标注，不冒充书中有定义句。
POLARITY_EXEMPLARS = {'甲': 'yang', '乙': 'yin'}
ROLES = ('male', 'female')
PRECISIONS = ('second', 'shichen', 'unknown')

SANMING_SECTION = {'id': 'sanming_lun_dayun', 'title': '论大运',
                   'juan': '卷二', 'line': 341,
                   'char_start': 58457, 'char_end': 59198}
SHENFENG_SECTION = {'id': 'shenfeng_qi_dayun_fa', 'title': '起大运法',
                    'line': 1307, 'char_start': 85001, 'char_end': 85246}

_PUA_BASIS = ('sanming_pua_collation.json mappings[28]（U+ED92，'
              'status=confirmed，confidence=high）；互证锚点：lhw828/GuWen '
              '《星学大成》「行运算至乙丑年」、kanripo KR3g0041「只要算足十二月」')


def _pua(char_offset, quote_id):
    return {'char_offset': char_offset, 'codepoint': 'U+ED92',
            'mapped_reading': '算', 'mapping_status': 'confirmed',
            'mapping_basis': _PUA_BASIS, 'quote_id': quote_id}


QUOTES = (
    {'id': 'ratio_statement', 'role': 'encoded_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '古人以大运则一辰十嵗折除以三日为年者何',
     'locator': {'line': 342, 'char_start': 58584, 'char_end': 58603},
     'note': '比率命题句：一辰十嵗、折除三日为年。'},
    {'id': 'ratio_derivation', 'role': 'encoded_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '葢一月之终晦朔周而有三十日一日之终昼夜周而有十二时总十年之运气凡三日有三十六时乃见三百六十日为一嵗之数在一月之中有三百六十时折除节气算计三千六百日为一辰之十嵗也',
     'locator': {'line': 342, 'char_start': 58603, 'char_end': 58683},
     'note': '全书唯一给出推导的条目：3 日=36 时→360 日为一嵗；1 时=10 日、1 日=120 日由此导出。'},
    {'id': 'direction_rule', 'role': 'encoded_rule',
     'source_id': SANMING_SOURCE_ID,
     'quote': '论折除之法必用生者日歴过日时数其节气之数阳男隂女大运以生日后未来节气日时为数顺而行之隂男阳女大运以生日前过去节气日时为数逆而行之',
     'locator': {'line': 342, 'char_start': 58693, 'char_end': 58757},
     'note': '方向与计数目标绑定为一条规则。本方向 Variant 的唯一编码规则句。'},
    {'id': 'worked_example', 'role': 'golden_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '假如甲子阳男十二月二十四日巳时生是月也二十九日申时立春阳男数以未来之日自二十四日巳时至二十五日巳时方是一日之实数至二十九申时正得五日三时之节气实歴过六十三日折除过六十三时折除计六百三十日乃一嵗竒九月之大运起于丁丑',
     'locator': {'line': 342, 'char_start': 58757, 'char_end': 58863},
     'note': '原文例算：五日三时=63 时→630 日。句中「实歴过六十三日」疑似转写讹衍，逐字保留只存疑登记。首运「起于丁丑」（月柱本身）与神峰例首运取次位的序列口径差异由 TJ-014.2 既有链显式声明处理，本批方向 Variant 不输出序列。'},
    {'id': 'worked_example_check', 'role': 'registered_not_encoded',
     'source_id': SANMING_SOURCE_ID,
     'quote': '必自十二月生日后实经厯过二十有一之日月运方移宫是越三嵗九月之内方是甲子十二月生行一嵗竒九月之大运也',
     'locator': {'line': 342, 'char_start': 58863, 'char_end': 58912},
     'note': '例算自洽校验句。「越三嵗九月」之「三」与算式矛盾，疑似讹字，逐字保留存疑登记。'},
    {'id': 'anti_rounding', 'role': 'encoded_prohibition',
     'source_id': SANMING_SOURCE_ID,
     'quote': '今人行运多用约法论以一嵗竒八月起运便以二嵗殊不明折除实厯之数也',
     'locator': {'line': 342, 'char_start': 58912, 'char_end': 58943},
     'note': '明文反对约整。本换算 Variant 据此禁止任何整岁取整路径。'},
    {'id': 'zero_borrow_definition', 'role': 'encoded_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '然三日而成一歳见有余人谓之零见不足人谓之借但知其零借不知其所以零借',
     'locator': {'line': 342, 'char_start': 58969, 'char_end': 59002},
     'note': '零/借定义：余为零、欠为借。'},
    {'id': 'zero_borrow_example', 'role': 'encoded_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '假如阳命正月初一日丑时正一刻生至初四日丑时正一刻立春节乃作一嵗全若春在寅时则多一时乃零一旬若欠一时乃借一旬',
     'locator': {'line': 342, 'char_start': 59002, 'char_end': 59055},
     'note': '零/借算式：36 时=一嵗全；37 时零一旬→370 日；35 时借一旬→350 日。余数在时粒度线性结转。'},
    {'id': 'handover_example', 'role': 'registered_not_encoded',
     'source_id': SANMING_SOURCE_ID,
     'quote': '假如甲子年正月初一子时正一刻生行运至乙丑年正月初一日子时正一刻乃作一嵗',
     'locator': {'line': 342, 'char_start': 59063, 'char_end': 59099},
     'pua_annotations': [_pua(59080, 'handover_example')],
     'mapped_reading_text': '假如甲子年正月初一子时正一刻生行运算至乙丑年正月初一日子时正一刻乃作一嵗',
     'note': '交运例起句（刻精度）。完整算式依赖闰月条款与未明句，只登记不编码其整年折算。引文逐字保留快照 PUA 原字；mapped_reading_text 为校勘映射读法，另行标注、非引文。'},
    {'id': 'handover_decade', 'role': 'encoded_basis',
     'source_id': SANMING_SOURCE_ID,
     'quote': '从此后十周年方换一运',
     'locator': {'line': 342, 'char_start': 59160, 'char_end': 59171},
     'pua_annotations': [_pua(59162, 'handover_decade')],
     'mapped_reading_text': '从此算后十周年方换一运',
     'note': '交运后每运十周年递换。后续运区间=首交运区间+ k×10 历年平移（宽度平移）；闰日平移处理为实现约定并标注，非原文算式。'},
    {'id': 'handover_approx', 'role': 'encoded_labeling_rule',
     'source_id': SANMING_SOURCE_ID,
     'quote': '若学者不知其生刻独知其生时即以生时扣筭六节之时亦差不逺',
     'locator': {'line': 342, 'char_start': 59171, 'char_end': 59198},
     'note': '生刻不明近似口径，原文自标「差不远」为近似而非等值。本 Variant 据此加宽区间并标注 approximate。'},
    {'id': 'vol11_direction_witness', 'role': 'corroboration',
     'source_id': SANMING_SOURCE_ID,
     'quote': '以支为命而详之则有逆顺如阳男阴女从生月顺行阴男阳女从生月逆行',
     'locator': {'line': 5588, 'char_start': 396898, 'char_end': 396928},
     'note': '卷十一赋注书内第二见证，方向分组与卷二主句一致。'},
    {'id': 'vol11_ratio_witness', 'role': 'corroboration',
     'source_id': SANMING_SOURCE_ID,
     'quote': '运行则一辰十载折除乃三日为年此古人立运之法也',
     'locator': {'line': 5590, 'char_start': 397112, 'char_end': 397134},
     'note': '卷十一赋注比率见证。'},
    {'id': 'vol11_counting_divergence', 'role': 'registered_limit',
     'source_id': SANMING_SOURCE_ID,
     'quote': '命有节气浅深不同运有就生就节互异',
     'locator': {'line': 5590, 'char_start': 397142, 'char_end': 397158},
     'note': '书内自承「就生/就节」异口径并存未裁定。计数目标按例证取节登记，scope 注明无排斥中气明文。'},
    {'id': 'vol11_direction_witness2', 'role': 'registered_not_encoded',
     'source_id': SANMING_SOURCE_ID,
     'quote': '阴男阳女阳男阴女依逆顺行运折除即前折除三岁为年也',
     'locator': {'line': 5668, 'char_start': 408771, 'char_end': 408795},
     'note': '卷十一赋注第三见证。「折除三岁为年」之「岁」为单点讹字（与三处「三日为年」矛盾），逐字保留登记异文，不得径改。'},
    {'id': 'sf_heading_yang', 'role': 'corroboration',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '起大运法阳男阴女',
     'locator': {'line': 1307, 'char_start': 85001, 'char_end': 85009},
     'note': '神峰分题标题即方向表一半。'},
    {'id': 'sf_ex1', 'role': 'corroboration_and_golden_basis',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '如甲子年,甲己之年丙作首,正月逢丙寅,初一立春后一日生男,折除三日,为一岁,顺数至二月惊蛰,得三十日起十岁,丁卯是也',
     'locator': {'line': 1308, 'char_start': 85010, 'char_end': 85068},
     'note': '例 1：甲子年男顺数未来节 30 日→十岁。首运丁卯为月柱次位，序列口径差异同 worked_example 注。'},
    {'id': 'sf_ex2', 'role': 'corroboration_direction_only',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '如乙丑年,乙庚之岁戊为头,正月起戊庚,初一立春,十八日生女,顺数至二月惊蛰,四三十二日,四岁运,己卯顺行是也',
     'locator': {'line': 1308, 'char_start': 85069, 'char_end': 85123},
     'note': '例 2：乙丑年女顺行。日数「四三十二日」转写讹乱（四岁须 12 日），月柱句「正月起戊庚」疑似讹字；只用方向与「四岁运」结果陈述，日数/月柱字面禁用，换算 Golden 不收。'},
    {'id': 'sf_heading_yin', 'role': 'corroboration',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '起大运法阴男阳女',
     'locator': {'line': 1309, 'char_start': 85129, 'char_end': 85137},
     'note': '神峰分题标题：阴男阳女一组。'},
    {'id': 'sf_ex3', 'role': 'corroboration_and_golden_basis',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '如乙丑年,乙庚之岁戊为头,正月起戊寅,初二立春,后十五日生男,逆数至初一日立春,五三十五,五岁运逆行',
     'locator': {'line': 1310, 'char_start': 85138, 'char_end': 85188},
     'note': '例 3：乙丑年男逆数过去节 15 日→五岁。「五三十五」字序讹（三五十五），算式自明，登记异文。'},
    {'id': 'sf_ex4', 'role': 'corroboration_and_golden_basis',
     'source_id': SHENFENG_SOURCE_ID,
     'quote': '如甲子年,甲己之年丙作首,正是丙寅,初一立春,后十日生女,逆数至初一日立春止,得九日三三得九,三岁运逆行',
     'locator': {'line': 1310, 'char_start': 85189, 'char_end': 85241},
     'note': '例 4：甲子年女逆数 9 日→三岁。「后十日生」而「得九日」为端点含/不含之差，按原文结果登记，不另裁端点口径。'},
)

EXCLUDED_SPANS = (
    {'id': 'leap_clause_excluded_span', 'source_id': SANMING_SOURCE_ID,
     'locator': {'line': 342, 'char_start': 59099, 'char_end': 59142},
     'quote': '内小六个月即进六日在初七日子时正一刻方作一嵗只要足十二个月却为本年有闰四月乃多一月矣',
     'pua_annotations': [_pua(59123, 'leap_clause_excluded_span')],
     'mapped_reading_text': '内小六个月即进六日在初七日子时正一刻方作一嵗只要算足十二个月却为本年有闰四月乃多一月矣',
     'reason': '「内小六个月即进六日」语义未明，闰月交运「退还」条款的完整算式依赖该句：闰月交运子规则整段排除，只登记存档；合规路径为 TJ-018.2 对该段专项互校后再议。'},
    {'id': 'sf_ex2_day_count', 'source_id': SHENFENG_SOURCE_ID,
     'locator': {'line': 1308, 'char_start': 85107, 'char_end': 85112},
     'quote': '四三十二日',
     'reason': '神峰例 2 日数转写讹乱（四岁须 12 日）；第二刊本互校前只用其岁数结果与方法，不用日数字面。'},
)

LIMITATIONS = (
    '方向年干阴阳为「例定」呈现（三命、神峰均以甲子/乙丑等年柱例固定），与显式五阳五阴表外延一致但呈现方式不同；书中无抽象定义句，本 Variant 不冒充有定义句。',
    '节的选择：例证一致指向「节」（三命例用立春，神峰例用立春/惊蛰）且交运段有「六节」用词，但无排斥中气的明文；三命赋注自承「就生/就节互异」。本 Variant 计数目标按例证取节（与 TJ-015 已审节距测量同口径），不声称原文排斥中气。',
    '闰月交运子规则未编码：「内小六个月即进六日」语义未明，交运段闰月「退还」算式依赖该句，整段排除（见 EXCLUDED_SPANS）；闰月出生者的交运区间按非闰算式给出时必须视为未审，本 Variant 的测量级入口不区分闰月与非闰月，此限定随输出 limitations 一并给出。',
    '换算分立：三命时级法与神峰日级法是两个 Variant，粒度不同（时/日），结果永不合并、不取平均；同一命盘两法结果可差至近四个月起运时长，引用时必须带口径标签。',
    '后续运的十年平移用历年加法实现（三命「十周年」），闰日（2 月 29 日）目标年无此日时钳至 2 月 28 日并逐项标注，此为实现约定，非原文算式。',
    '出生时刻的时区与历史时区口径沿用 TJ-015 节距测量的既有边界（Asia/Shanghai 归一、1901–2098、历史时区未独立验证），本 Variant 不新裁定。',
    '虚岁/实岁无原典口径（在场五书零命中）：本 Variant 不输出任何年龄数值；「约 X 岁」式呈现属产品约定（TJ-017.3），须界面标注。',
    '三命整书仍 quarantine_only：《论大运》节外未审定；疑似讹字（越三嵗九月、实歴过六十三日、卷十一折除三岁为年）只存疑登记，未径改，待 TJ-018.2 校勘。',
    '本 Variant 尚未在密封 Phase1 bundle/Phase2 contract 注册 rule，不进 RuleMatch 与 Evidence。',
    '首运取月柱本身（三命例）或次位（神峰例）的序列口径差异不在本 Variant 范围：本 Variant 只输出方向与计数目标，不输出干支序列。',
)

CONSUMER_CONVENTIONS = {
    'tj0172': '跨规则调用必须直接消费交运时刻区间（handover_intervals），禁止先把区间折算成某个「岁数」再调用——折算必然引入无原典的年龄口径选择。',
    'tj0173': '时间轴视图若出现「约 X 岁」字样，属产品约定，必须标注为约定（如「按实历时长换算的约数」）；未知/争议交运年份用空态。',
    'age_counting': '虚岁/实岁无原典口径；refuse_age_counting_conversion 拒绝两制互换，保留不变。本模块一切输出不含年龄数值字段。',
}


def _flags():
    return {'research_only': True, 'public_enabled': False,
            'ai_enabled': False,
            'evidence_binding': 'pending_phase1_rule_registration'}


def _quote_ref(quote_id):
    for q in QUOTES:
        if q['id'] == quote_id:
            return {'id': q['id'], 'role': q['role'],
                    'source_id': q['source_id'], 'quote': q['quote'],
                    'locator': dict(q['locator'])}
    raise KeyError(quote_id)


# ---------------------------------------------------------------- direction

def classical_direction(year_ganzhi, *, traditional_role):
    """Classical-evidence Dayun direction (TJ-017.1).

    The role category is a historical classification label selected
    explicitly by the caller; it is never inferred from identity data
    (same gate as the TJ-014.1 modern candidate). Direction and the
    counting target are bound by one classical rule sentence, so the
    result always carries both.
    """
    if type(year_ganzhi) is not str:
        raise ValueError('Expected a valid natal year Ganzhi')
    ganzhi_index(year_ganzhi)  # Reject forged or invalid combinations.
    if type(traditional_role) is not str or traditional_role not in ROLES:
        raise ValueError('Explicit traditional_role=male|female is required')
    stem = year_ganzhi[0]
    if stem not in STEMS:
        raise ValueError('Invalid natal year stem')
    polarity = 'yang' if stem in YANG_STEMS else 'yin'
    forward = (polarity == 'yang' and traditional_role == 'male') or (
        polarity == 'yin' and traditional_role == 'female')
    return {
        'variant': DIRECTION_VARIANT,
        'year_ganzhi': year_ganzhi,
        'year_stem': stem,
        'year_stem_polarity': polarity,
        'year_stem_polarity_basis': 'exemplar_fixed',
        'polarity_exemplars': dict(POLARITY_EXEMPLARS),
        'polarity_table_note': ('两书以年柱例固定阴阳（甲子=阳、乙丑=阴），'
                                '无抽象定义句；全表外延与通行干阴阳一致，'
                                '呈现方式差异如实标注。'),
        'traditional_role': traditional_role,
        'traditional_role_selection':
            'explicit_historical_category_not_inferred_identity',
        'direction': 'forward' if forward else 'backward',
        'counting_target': 'future_jie' if forward else 'past_jie',
        'rule_quote': _quote_ref('direction_rule'),
        'evidence_quotes': [_quote_ref(qid) for qid in (
            'direction_rule', 'vol11_direction_witness',
            'sf_heading_yang', 'sf_ex1', 'sf_ex2',
            'sf_heading_yin', 'sf_ex3', 'sf_ex4')],
        'modern_candidate_comparison': {
            'variant': MODERN_CANDIDATE_VARIANT,
            'quadrant_agreement': 'full_four_quadrants',
            'divergences': [],
            'candidate_status': ('retained_as_historical_record; classical '
                                 'evidence is now the primary registration'),
        },
        'phase2_allowed': False,
        'direction_rule_match': None,
        'scope': ('古典方向规则研究口径：阳男阴女顺行数生日后未来节，'
                  '阴男阳女逆行数生日前过去节；只给方向与计数目标，'
                  '不给起运时长、交运时刻或序列。'),
        'limitations': list(LIMITATIONS),
        **_flags(),
    }


def validate_classical_direction(result):
    """Fail-closed gate for a classical direction result.

    Recomputes the result from its declared inputs and rejects any
    promotion or forgery: public/AI enablement, a Phase2 rule match,
    an added handover/age field, altered evidence quotes, or a
    direction/counting-target that disagrees with the classical rule.
    """
    def fail(message):
        raise ValueError('Classical Dayun direction rejected: ' + message)

    if not isinstance(result, dict):
        fail('result is not an object')
    if result.get('variant') != DIRECTION_VARIANT:
        fail('unknown or missing variant')
    expected = classical_direction(
        result.get('year_ganzhi'),
        traditional_role=result.get('traditional_role'))
    for field in ('year_stem', 'year_stem_polarity', 'direction',
                  'counting_target', 'traditional_role_selection',
                  'year_stem_polarity_basis'):
        if result.get(field) != expected[field]:
            fail('field %s disagrees with the classical rule' % field)
    if result.get('polarity_exemplars') != expected['polarity_exemplars']:
        fail('polarity exemplar record altered')
    if result.get('rule_quote') != expected['rule_quote']:
        fail('rule quote altered')
    if result.get('evidence_quotes') != expected['evidence_quotes']:
        fail('evidence quote set altered')
    if result.get('research_only') is not True:
        fail('research_only must remain true')
    if result.get('public_enabled') is not False:
        fail('public_enabled must remain false')
    if result.get('ai_enabled') is not False:
        fail('ai_enabled must remain false')
    if result.get('phase2_allowed') is not False:
        fail('phase2 promotion is not authorized')
    if result.get('direction_rule_match') is not None:
        fail('forged Phase2 rule match: no Phase2 dayun direction rule '
             'is registered')
    if result.get('evidence_binding') != 'pending_phase1_rule_registration':
        fail('evidence binding status forged')
    for forbidden in ('handover_intervals', 'handover_datetime',
                      'start_duration_interval_days', 'start_age'):
        if forbidden in result:
            fail('direction result must not carry %s' % forbidden)
    return True


# ---------------------------------------------------------------- conversion

def _duration_block(*, min_days, max_days, max_inclusive, approximate,
                    approximation_basis, extra):
    block = {
        'duration_interval_days': {
            'min_days': min_days, 'max_days': max_days,
            'max_inclusive': max_inclusive,
        },
        'rounding_applied': False,
        'rounding_policy': 'refused_classical_text_prohibits_rounding',
        'approximate': approximate,
    }
    if approximation_basis is not None:
        block['approximation_basis'] = approximation_basis
    block.update(extra)
    return block


def sanming_convert_elapsed(elapsed_seconds, *,
                            birth_time_precision='second', rounding=None):
    """三命时级换算（纯算术层）：实历秒数 → 起运时长区间（日）。

    时粒度计数（1 时=10 日）+ 零/借线性结转 + 明文反约整。亚时余数无
    原文处理，只许区间上端表达。恰逢节（0 秒）按既有拒绝口径返回
    unresolved。rounding 参数为拒绝哨兵：任何非 None 值一律拒绝执行。
    """
    if rounding is not None:
        return {
            'variant': CONVERSION_VARIANT, 'status': 'unresolved',
            'reason': ('rounding %r refused: the classical text explicitly '
                       'rejects approximate rounding of the exact elapsed '
                       'count' % (rounding,)),
            'anti_rounding_quote': _quote_ref('anti_rounding'),
            **_flags(),
        }
    if type(elapsed_seconds) is not int or elapsed_seconds < 0:
        raise ValueError('elapsed_seconds must be a non-negative integer')
    if birth_time_precision not in PRECISIONS:
        raise ValueError('birth_time_precision must be one of %r'
                         % (PRECISIONS,))
    if elapsed_seconds == 0:
        return {
            'variant': CONVERSION_VARIANT, 'status': 'unresolved',
            'reason': 'zero_jie_boundary_convention_unreviewed',
            'note': ('恰逢节瞬间：原文例算未覆盖，不得默认起运时长为零'
                     '（与 TJ-016.2 对抗口径一致）。'),
            **_flags(),
        }
    whole_shichen, remainder_seconds = divmod(elapsed_seconds,
                                              SHICHEN_SECONDS)
    base_min = whole_shichen * DAYS_PER_SHICHEN
    base_max = base_min + (DAYS_PER_SHICHEN if remainder_seconds else 0)
    approximate = birth_time_precision != 'second'
    widen = 0 if not approximate else DAYS_PER_SHICHEN
    min_days = base_min - widen
    max_days = base_max + widen
    max_inclusive = remainder_seconds == 0 and not approximate
    whole_year_units, remainder_shichen = divmod(whole_shichen,
                                                 SHICHEN_PER_YEAR_UNIT)
    remainder_days = remainder_shichen * DAYS_PER_SHICHEN
    basis = None
    if birth_time_precision == 'unknown':
        basis = {'kind': 'text_approximation_for_unknown_ke',
                 'quote': _quote_ref('handover_approx'),
                 'widened_days_each_side': DAYS_PER_SHICHEN}
    elif birth_time_precision == 'shichen':
        basis = {'kind': 'counting_granularity_within_one_shichen',
                 'widened_days_each_side': DAYS_PER_SHICHEN}
    result = {
        'variant': CONVERSION_VARIANT, 'status': 'converted',
        'method': 'sanming_shichen_level',
        'input': {'elapsed_seconds': elapsed_seconds,
                  'birth_time_precision': birth_time_precision},
        'counting': {
            'whole_shichen_counted': whole_shichen,
            'sub_shichen_remainder_seconds': remainder_seconds,
            'sub_shichen_remainder_handling':
                'interval_upper_bound_only_not_proportionally_converted',
        },
        'duration_decomposition': {
            'whole_year_units': whole_year_units,
            'remainder_shichen': remainder_shichen,
            'remainder_days': remainder_days,
            'remainder_months_of_30_days': (
                remainder_days // 30 if remainder_days % 30 == 0 else None),
            'remainder_doctrine': ('surplus_or_deficit_against_whole_year_'
                                   'units_carries_linearly_at_10_days_per_'
                                   'shichen_never_discarded_never_rounded'),
        },
        'evidence_quotes': [_quote_ref(qid) for qid in (
            'ratio_statement', 'ratio_derivation', 'worked_example',
            'anti_rounding', 'zero_borrow_definition',
            'zero_borrow_example')],
        'limitations': list(LIMITATIONS),
        **_flags(),
    }
    result.update(_duration_block(
        min_days=min_days, max_days=max_days, max_inclusive=max_inclusive,
        approximate=approximate, approximation_basis=basis, extra={}))
    return result


def shenfeng_convert_days(whole_days, *, direction, rounding=None):
    """神峰日级换算：整日计数 → 起运时长区间（日）。

    与三命时级法分立：本法只有整日粒度（1 日=120 日），无余数
    doctrine、无时辰参与。原文结果（整日×120 日）记为
    text_result_days；日级粒度下真实历时在 [d, d+1) 日，区间上端
    为 (d+1)×120、不含。例 2 日数讹乱不在 Golden 内（见模块
    EXCLUDED_SPANS）。rounding 同三命口径拒绝。
    """
    if rounding is not None:
        return {
            'variant': SHENFENG_CONVERSION_VARIANT, 'status': 'unresolved',
            'reason': ('rounding %r refused: no rounding rule exists in '
                       'the shenfeng day-level text' % (rounding,)),
            **_flags(),
        }
    if type(whole_days) is not int or whole_days < 0:
        raise ValueError('whole_days must be a non-negative integer')
    if type(direction) is not str or direction not in ('forward', 'backward'):
        raise ValueError('Explicit forward/backward direction required')
    if whole_days == 0:
        return {
            'variant': SHENFENG_CONVERSION_VARIANT, 'status': 'unresolved',
            'reason': 'zero_day_count_not_exemplified_in_text',
            'note': ('日级零计数未见原文例：生于节气当日而时刻未明与恰逢'
                     '节瞬间不可区分，不得默认时长为零。'),
            **_flags(),
        }
    text_result = whole_days * DAYS_PER_COUNTED_DAY
    result = {
        'variant': SHENFENG_CONVERSION_VARIANT, 'status': 'converted',
        'method': 'shenfeng_day_level',
        'input': {'whole_days': whole_days, 'direction': direction},
        'counting_target': ('future_jie' if direction == 'forward'
                            else 'past_jie'),
        'text_result_days': text_result,
        'granularity_note': ('日级计数截断亚日余数：真实历时在 '
                             '[whole_days, whole_days+1) 日内，区间据此'
                             '给出；本法无时级余数 doctrine。'),
        'evidence_quotes': [_quote_ref(qid) for qid in (
            'sf_ex1', 'sf_ex3', 'sf_ex4')],
        'limitations': list(LIMITATIONS),
        **_flags(),
    }
    result.update(_duration_block(
        min_days=text_result, max_days=text_result + DAYS_PER_COUNTED_DAY,
        max_inclusive=False, approximate=False, approximation_basis=None,
        extra={}))
    return result


# ------------------------------------------------------- measurement binding

def _validate_measurement(measured):
    """Replay-validate a TJ-015 jie measurement, as the ratio module does.

    This authenticates the measurement against the pinned provider by
    recomputation; it is not an independent astronomical review.
    """
    if (type(measured) is not dict
            or measured.get('variant') != 'bazi-dayun-adjacent-jie-research-v1'
            or measured.get('calendar_provider') != PROVIDER
            or measured.get('research_only') is not True
            or measured.get('dayun_conversion_rule_review_status')
            != 'unreviewed'):
        raise ValueError('Conversion requires a pinned unreviewed Jie '
                         'measurement')
    direction = measured.get('direction')
    if type(direction) is not str or direction not in ('forward', 'backward'):
        raise ValueError('Measurement requires an explicit direction')
    birth_value = measured.get('birth_local_datetime')
    month = measured.get('birth_month_ganzhi')
    if type(month) is not str:
        raise ValueError('Missing source month Ganzhi')
    ganzhi_index(month)
    replay = adjacent_jie_distance(birth_value, direction,
                                   expected_month_ganzhi=month)
    for key in ('birth_local_datetime', 'birth_month_ganzhi',
                'previous_jie', 'next_jie', 'selected_jie',
                'elapsed_seconds', 'elapsed_whole_days',
                'remaining_seconds_after_whole_days', 'zero_distance'):
        if measured.get(key) != replay[key]:
            raise ValueError('Jie measurement differs from pinned provider')
    if (measured.get('public_enabled') is not False
            or measured.get('ai_enabled') is not False
            or any(measured.get(k) is not None for k in
                   ('conversion_to_start_age', 'start_age',
                    'handover_datetime'))):
        raise ValueError('Unreviewed measurement cannot authorize dated age')
    return replay


def _add_calendar_years(moment, years):
    """Calendar-year shift for the 十周年 decade rule (implementation
    convention, labeled): Feb 29 clamps to Feb 28 in non-leap targets."""
    try:
        return moment.replace(year=moment.year + years), False
    except ValueError:
        # Only reachable for Feb 29 -> non-leap target year.
        return moment.replace(year=moment.year + years, day=28), True


def _handover_intervals(birth, duration, periods):
    interval = duration['duration_interval_days']
    earliest0 = birth + timedelta(days=interval['min_days'])
    latest0 = birth + timedelta(days=interval['max_days'])
    rows = []
    for k in range(periods):
        earliest, clamp_e = _add_calendar_years(earliest0, 10 * k)
        latest, clamp_l = _add_calendar_years(latest0, 10 * k)
        row = {
            'period_index': k + 1,
            'earliest': earliest.isoformat(),
            'latest': latest.isoformat(),
            'max_inclusive': interval['max_inclusive'],
            'basis': ('start_duration_interval_plus_%d_calendar_decades'
                      % k if k else 'birth_plus_start_duration_interval'),
        }
        if clamp_e or clamp_l:
            row['calendar_year_shift_clamped_feb29'] = True
        rows.append(row)
    return rows


def sanming_convert_measurement(measured, *, birth_time_precision='second',
                                periods=1):
    """Measurement-level 三命换算：节距测量 → 时长区间 + 交运时刻区间。

    输出只有区间：起运时长区间（日）与交运时刻区间（首运及后续运，
    后续运=首交运区间+ k×10 历年平移，宽度平移不放大）。类型层不提
    供任何单点日期字段，也不含任何年龄数值字段。恰逢节的测量按既有
    拒绝口径返回 unresolved（时长区间与交运区间均不给出）。
    """
    if type(periods) is not int or not 1 <= periods <= MAX_PERIODS:
        raise ValueError('periods must be an integer from 1 to %d'
                         % MAX_PERIODS)
    replay = _validate_measurement(measured)
    converted = sanming_convert_elapsed(
        replay['elapsed_seconds'], birth_time_precision=birth_time_precision)
    direction = replay['direction']
    selected = replay['selected_jie']
    result = {
        'variant': CONVERSION_VARIANT,
        'status': converted['status'],
        'method': 'sanming_shichen_level',
        'direction': direction,
        'counting_target': ('future_jie' if direction == 'forward'
                            else 'past_jie'),
        'counted_jie': {'name': selected['name'], 'at': selected['at']},
        'birth_instant': replay['birth_local_datetime'],
        'jie_selection_scope': ('counting target is a Jie (节) per the '
                                'text examples and the 六节 wording; no '
                                'explicit exclusion of zhongqi exists in '
                                'the text (registered limit)'),
        'consumer_conventions': dict(CONSUMER_CONVENTIONS),
        'limitations': list(LIMITATIONS),
        **_flags(),
    }
    if converted['status'] != 'converted':
        result['reason'] = converted['reason']
        result['duration_interval_days'] = None
        result['handover_intervals'] = None
        return result
    birth = datetime.fromisoformat(replay['birth_local_datetime'])
    if birth.tzinfo is None:
        raise ValueError('Measurement birth instant must be timezone-aware')
    result['duration_interval_days'] = converted['duration_interval_days']
    result['duration_decomposition'] = converted['duration_decomposition']
    result['counting'] = converted['counting']
    result['rounding_applied'] = False
    result['approximate'] = converted['approximate']
    if 'approximation_basis' in converted:
        result['approximation_basis'] = converted['approximation_basis']
    result['handover_intervals'] = _handover_intervals(birth, converted,
                                                       periods)
    result['handover_basis_quote'] = _quote_ref('handover_decade')
    return result


def compare_with_modern_candidate(year_ganzhi, *, traditional_role):
    """Classical result next to the retained modern candidate, unmerged.

    The two are returned side by side with their agreement stated; the
    candidate is never silently replaced or merged into the classical
    result (conflict-surfacing convention).
    """
    classical = classical_direction(year_ganzhi,
                                    traditional_role=traditional_role)
    candidate = traditional_direction(year_ganzhi,
                                        traditional_role=traditional_role)
    return {
        'classical': classical,
        'modern_candidate': candidate,
        'agreement': classical['direction'] == candidate['direction'],
        'primary_registration': 'classical',
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
    }
