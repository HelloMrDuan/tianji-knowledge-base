"""喜用神实际计算引擎 TJ-0424（P0-3）：四体系并列计算，统一裁决恒拒判。

只消费已有的可执行输出，不产生新的古典裁定、不编造古籍依据：

* 扶抑（``fuyi``）：三层并列。古典定性层逐行求值《滴天髓阐微》任氏
  扶抑方向表十行（``FUYI_DIRECTION_TABLE``，逐字转录自已登记的
  ``bazi_ditiansui_fuyi.FUYI_DIRECTION_TABLE``；转录漂移由专项测试
  在可导入时逐行核对）：每行的「日主旺/弱」前提可由古典层分类核对，
  但十行全部含量化词（多/轻/重/旺/两停/均敌）且全部未阈值化
  （U3 Q1=B：不设计数口径），故古典层没有任何一行能点火，
  只输出「前提成立行的条件方向」作为条件方向，不给方向结论。
  条件谓词层即此逐行核对本身（前提 satisfied / cannot_judge、
  量化词恒 cannot_judge）。第三批另逐行核对补充登记方向陈述
  （``FUYI_SUPPLEMENTAL_STATEMENTS``，转录自同一登记模块的
  ``FUYI_QUOTES``：F-1 总纲两句、F-2 形全/形缺两句、F-3 总则一句、
  提纲为用两句、表前引一句；反转/反例条款六句只作
  ``supplemental_guards`` 登记、不评估）：无量化词的总纲/总则行
  同样不点火——任氏曰明言四字须分用、通变在一「宜」字且带反转
  条款，故只作条件方向；提纲为用行需月支本气十神（本引擎输入契
  约无藏干事实）故适用性恒不可判，日主衰行只在显干见帮身者时记
  其干；形全/形缺只认原注枚举的四干组合，不以「余仿此」类推。
  现代工程层执行已批准的
  ``FUYI_MODERN_RULES_V1``（现代研究模型，恒标
  ``model_kind="modern_engineering"``）：以已批准的现代旺衰模型
  ``strength_model_modern_v1`` 的 verdict/score/components 为输入，
  strong→泄耗克、weak→生扶、balanced→不给方向；候选干只取显干中
  方向元素所含之干，且只标 ``candidate``（X2：显干候选口径已批准，
  不自动以藏干补位，不宣称确定用神）。现代规则是已批研究模型
  （X1，用户裁定 2026-11-25），``adjudication_status`` 为
  ``approved_research_model``，恒标 modern_engineering/research_only，
  不得升格为古典规则。第三批只做现代层计算能力的
  完备性：输入边界校验（总分域 [-35, 105]、分项域、verdict 与分数
  档位一致、分项和等于总分，均转录自已批准的现代模型常量，漂移
  即 fail-closed）、分项解释（``component_explanations``，只读分
  项分数符号的方向性，不构成独立方向结论）、输入完备性
  （``input_completeness``）与方向推导 trace
  （``direction_derivation``）；规则本身不改、不升格。
* 调候（``tiaohou``）：消费 ``tiaohou_lookup`` 输出（穷通宝鉴
  ``tiaohou-qiongtong-v1``）。主序列按原文先次排序，取首个在盘干
  （显干优先于藏干、藏干优先于不在盘）；已应用的分支序列取代主序列；
  每候选干附十神；条目缺失（乙×丑）、序列为空（丙×亥/丁×午）、
  候选全不在盘、未编码分支，全部明记为缺口。第三批扩充已登记条目
  的覆盖面；原典首选 / 原典备选 / 在盘候选三分口径已批准（X4，
  用户裁定 2026-11-25）：原典首选恒为取用序列首位干（不论在盘与否），
  原典备选为其后序列干，在盘候选为在盘（透干/藏干）之干；在盘首取
  （首个在盘干）与原典首选是两个位置——原典首选缺位时，后续在盘干
  只作在盘首取，绝不冒充原典首选。未应用的分支逐条登记
  （条件干在盘的事实、显干/藏干口径），``related`` 与条目注记只作
  登记、不并入取用序列；``pillars`` 入参首次用于未应用分支条件干
  的显干/藏干区分。
* 病药（``bingyao``）：消费 ``bingyao_lookup`` 输出（神峰通考
  ``bingyao-shenfeng-v1``）。逐对独立：触发且药在盘→药神候选干；
  触发而药不在盘→药神类（官杀/财）明记为缺口；未触发→该对无输出；
  药去病效力恒未裁定；「从重者论」无阈值故不选唯一病神。第三批
  另列已登记未编码的病药对子（``BINGYAO_REGISTERED_NOT_ENCODED_PAIRS``，
  转录自同一登记模块的 ``QUOTES``：示例一土重对、正官格太弱太旺
  张力句）与定义句（``BINGYAO_REGISTERED_DEFINITIONS``），只登记
  不编码、不产药神候选；病药药神缺位候选类已批准（X5，用户裁定
  2026-11-25）：触发而药不在盘时，药神类（官杀/财）明记为缺口候选类，
  并给出该类所含之干（十神类→干的纯算术展开，不新立药神规则）。
* 格局用神（``pattern_yongshen``）：消费格局引擎 ``evaluate_all``
  输出。只对已成立（任氏寅月真格）或有 validated 候选规则
  （正官 Golden 20 / 印绶 Golden 42 / 任氏 D-1）的格列资格；
  但密封树中全部格的 ``useful_god`` 恒未审，故任何格都不输出用神——
  输出为「无已审用神规则」的确定结论，附该格的结构依据（格神、
  显干位置）与未覆盖原因；无资格的格不输出用神，只记原因。
  ``broken`` 只经伤官见官一途输出（任氏寅月真格成立的伤官格＋
  正官在场）：按契约验收后记 ineligible，破格依据与原成立身份随
  记录携带，永不计入成立、永不输出格局用神。第三批扩充有资格格的
  结构依据输出
  （``structure_basis``：格神五行与相对日主的关系、显干计数与月柱
  在场、证据全文、逐格 limitations、按状态计数、引擎 ``counts`` 与
  ``earth_gate`` 原样转述并校验），不新立任何格局用神规则。
  格局用神逐格规则开发方向已批准（X6，用户裁定 2026-11-25），
  但具体逐格规则仍需证据审查——有资格（established 或 validated
  候选）只表示可列结构依据，不等于格局用神已经成立，``useful_god``
  恒为 None。格局变体 pin 为 v2（C1，用户裁定 2026-11-25：喜用侧
  接通格局引擎 v2，逐项校验变体、输入结构、字段语义与兼容性）。

四体系结果独立输出；每体系输出必含结论、输入依据、适用条件、
局限/不确定性标记。流年喜用（``evaluate_annual_xiyong``）接入组合
引擎 ``contract_only_pending_rules`` 已实现的 4 项（流年干支与十神、
流年干在原局调候序列中的存在性、流年干十神在病药对中的角色、
规则调用结构），另加两项同类存在性对照（扶抑现代候选干、格局结构
依据干；X7 已批准，用户裁定 2026-11-25——存在性不等于作用效力，
只报同字存在性，不推演流年喜用）；其余 5 项保持 pending，逐项明记
所缺的底层规则（``ANNUAL_PENDING_DETAIL``）。``unified_verdict`` 恒为 None
（TJ-013.2 裁决 A）。

本模块只依赖纯常量模块 ``foundations``，公开检出可直接执行；
不 import ``bazi_core`` / 强度 / 格局 / 调候 / 病药模块（它们依赖
历法 provider 与密封数据），输入一律为调用方传入的已审输出字典，
变体与治理旗标漂移一律 fail-closed（ValueError）。
恒 research_only=True、public_enabled=False、ai_enabled=False；
不新增公开字段，不接公开 API。
"""

from .foundations import (
    BRANCHES, CYCLE, GENERATES, CONTROLS, STEMS, ganzhi_index, stem_element)

XIYONG_ENGINE_VARIANT = 'bazi-xiyong-engine-v1'
ANNUAL_CONTRACT_VARIANT = 'bazi-xiyong-annual-contract-v1'

STRENGTH_ENGINE_VARIANT = 'bazi-strength-engine-v1'
MODERN_MODEL_ID = 'strength_model_modern_v1'
TIAOHOU_VARIANT = 'tiaohou-qiongtong-v1'
BINGYAO_VARIANT = 'bingyao-shenfeng-v1'
PATTERN_ENGINE_VARIANT = 'bazi-pattern-engine-v2'

# 格局引擎中带 validated 候选规则的 rule_id（正官 Golden 20、
# 印绶 Golden 42、任氏 D-1 Golden 15）。仅观察（rule_ids 为空）的
# 候选不在此列，无资格输出格局用神。
VALIDATED_CANDIDATE_RULE_IDS = frozenset((
    'bazi.phase2.official_pattern_candidates',
    'bazi.phase2.resource_pattern_candidates',
    'bazi.phase2.ren_yin_true_pattern',
))

# 格键 -> 格神（十神）。建禄/阳刃/杂气/特殊无十神格神。
PATTERN_TEN_GODS = {
    'zhengguan': '正官', 'qisha': '七杀', 'zhengyin': '正印',
    'pianyin': '偏印', 'zhengcai': '正财', 'piancai': '偏财',
    'shishen': '食神', 'shangguan': '伤官',
}

# --- 扶抑方向表 -------------------------------------------------------
# 逐字转录自 bazi_ditiansui_fuyi.FUYI_DIRECTION_TABLE（《滴天髓阐微》
# 任氏曰「日主为体者」段，快照字符 35697–35862，source
# bazi.source.ditiansui-spouse）。行序、断句与量化词不归一化；
# 转录正确性由专项测试在可导入时逐行核对原文模块，漂移即失败。
FUYI_DIRECTION_TABLE = {
    'source_id': 'bazi.source.ditiansui-spouse',
    'passage_id': 'ditiansui.fuyi_tiyong',
    'layer': '任氏曰',
    'lead_in': '日主为体者',
    'closing': '此皆用神之的当者也。',
    'body_locator': {'char_start': 35697, 'char_end': 35862},
    'rows': (
        {'row': 1, 'text': '日主旺,印绶多,必要财星为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多',), 'direction_god': '财星'},
        {'row': 2, 'text': '日主旺,官杀轻,亦以财星为用。',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('轻',), 'direction_god': '财星'},
        {'row': 3, 'text': '日主旺,比劫多 ,耐我财星,以食伤为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多',), 'direction_god': '食伤'},
        {'row': 4, 'text': '日主旺,比劫多,而财星轻,亦以食伤为用。',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('多', '轻'), 'direction_god': '食伤'},
        {'row': 5, 'text': '日主旺,官星轻,銕绶重,以财星为用;',
         'premise_day_master_state': '旺',
         'condition_quantifiers': ('轻', '重'), 'direction_god': '财星'},
        {'row': 6, 'text': '日主弱,官杀旺,则以印绶为用,',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('旺',), 'direction_god': '印绶'},
        {'row': 7, 'text': '日主弱,食伤多,亦以印绶为用;',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('多',), 'direction_god': '印绶'},
        {'row': 8, 'text': '日主弱,财星旺,则以比劫为用。',
         'premise_day_master_state': '弱',
         'condition_quantifiers': ('旺',), 'direction_god': '比劫'},
        {'row': 9, 'text': '日主与官杀两停者,则以食伤为用;',
         'premise_day_master_state': '两停',
         'condition_quantifiers': ('两停',), 'direction_god': '食伤'},
        {'row': 10, 'text': '日主与财星均敌者,则以印比为用。',
         'premise_day_master_state': '均敌',
         'condition_quantifiers': ('均敌',), 'direction_god': '印比'},
    ),
}

# 方向神类 -> 相对日主的五行关系。印比 = 生我 + 同类。
_DIRECTION_GOD_RELATIONS = {
    '财星': ('i_control',),
    '食伤': ('i_generate',),
    '印绶': ('generates_me',),
    '比劫': ('same_element',),
    '印比': ('generates_me', 'same_element'),
}

# --- 扶抑现代工程规则（已批研究模型，X1）------------------------------
# 以 strength_model_modern_v1 的 verdict 为输入的方向映射。阈值沿用
# 已批准的现代模型阈值（strong >= 60、weak <= 15、其余 balanced），
# 「verdict→方向」的映射本身是本批新拟的工程约定，用户裁定
# 2026-11-25（X1）已批准其为现代研究模型（modern_engineering /
# research_only），绝不冒充古典规则、绝不升格。
FUYI_MODERN_RULES_V1 = {
    'model_id': 'fuyi-modern-rules-v1',
    'model_kind': 'modern_engineering',
    'adjudication_status': 'approved_research_model',
    'adjudication_ref': 'X1 approved 2026-11-25 as modern research model',
    'input_model_id': MODERN_MODEL_ID,
    'input_thresholds': {'strong_at_least': 60, 'weak_at_most': 15,
                         'balanced_between': [16, 59]},
    'rules': (
        {'rule_id': 'fuyi-modern-strong', 'modern_verdict': 'strong',
         'direction': 'drain_control', 'direction_cn': '泄耗克',
         'element_relations': ('i_generate', 'i_control', 'controls_me'),
         'ten_god_classes': ('食神', '伤官', '正财', '偏财', '正官', '七杀')},
        {'rule_id': 'fuyi-modern-weak', 'modern_verdict': 'weak',
         'direction': 'support', 'direction_cn': '生扶',
         'element_relations': ('same_element', 'generates_me'),
         'ten_god_classes': ('比肩', '劫财', '正印', '偏印')},
        {'rule_id': 'fuyi-modern-balanced', 'modern_verdict': 'balanced',
         'direction': None, 'direction_cn': None,
         'element_relations': (), 'ten_god_classes': ()},
    ),
}

# --- 扶抑补充登记方向陈述（第三批）------------------------------------
# 转录自 bazi_ditiansui_fuyi.FUYI_QUOTES（F-1 原注、F-2 诗句＋任氏曰、
# F-3 体用章任氏曰）。只收录有明确方向陈述的登记规则；行序、断句与
# 量化词不归一化；转录正确性由专项测试在可导入时逐句核对原文模块，
# 漂移即失败。方向神类映射（泄→食伤、伤→官杀、帮→比劫、助→印绶）
# 取自同一登记的术语 gloss（FUYI_TERM_GLOSSES），非本批新立。
# 任何补充行都不点火、不给方向结论（X3 已批准条件方向并列呈现，
# 2026-11-25；不点火本身不变）：无量化词的总纲/
# 总则行受 F-2 反机械告诫（四字须分用、通变在一「宜」字）与 F-3
# 反转条款约束，只作条件方向；提纲行需月支本气十神，不在输入契约内。
FUYI_TERM_GLOSSES = (
    {'term': '泄', 'god_class': '食伤',
     'gloss_sentence': '泄者食伤也,伤者官杀也',
     'quote_id': 'fy.xingxiang_renshi_differentiation',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '任氏曰',
     'locator': {'char_start': 27277, 'char_end': 27288}},
    {'term': '伤', 'god_class': '官杀',
     'gloss_sentence': '泄者食伤也,伤者官杀也',
     'quote_id': 'fy.xingxiang_renshi_differentiation',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '任氏曰',
     'locator': {'char_start': 27277, 'char_end': 27288}},
    {'term': '帮', 'god_class': '比劫',
     'gloss_sentence': '帮者比劫也,助者印绶也',
     'quote_id': 'fy.xingxiang_renshi_differentiation',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '任氏曰',
     'locator': {'char_start': 27349, 'char_end': 27360}},
    {'term': '助', 'god_class': '印绶',
     'gloss_sentence': '帮者比劫也,助者印绶也',
     'quote_id': 'fy.xingxiang_renshi_differentiation',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '任氏曰',
     'locator': {'char_start': 27349, 'char_end': 27360}},
)

# 形全/形缺的月令集合定义（fy.xingxiang_yuanzhu 原注逐干举例）：
# 甲木生于寅卯辰、丙火生于巳午未为形全；戊土生于寅卯辰、庚金生于
# 巳午未为形缺；其余以「余仿此」类推——治理禁止以类推补表，本引擎
# 不展开未举例诸干的集合成员资格，未列组合恒不可判。丙火「生于已」
# 之已为转写疑讹（fy-glyph-03，疑为巳之讹，逐字保留、不径改），
# 本表按巳登记并在此明示。
FUYI_FORM_ENUMERATION = {
    'form_full': frozenset((
        ('甲', '寅'), ('甲', '卯'), ('甲', '辰'),
        ('丙', '巳'), ('丙', '午'), ('丙', '未'))),
    'form_deficient': frozenset((
        ('戊', '寅'), ('戊', '卯'), ('戊', '辰'),
        ('庚', '巳'), ('庚', '午'), ('庚', '未'))),
    'glyph_note': 'fy-glyph-03：丙火「生于已」之已疑为巳之讹，'
                  '逐字保留、不径改；本表按巳登记。',
}

FUYI_SUPPLEMENTAL_STATEMENTS = (
    {'id': 'f1-general-strong', 'kind': 'general_rule',
     'quote_id': 'fy.shaiwang_yuanzhu',
     'passage_id': 'ditiansui.fuyi_shaiwang', 'layer': '原注',
     'text': '旺则宜泄宜伤',
     'locator': {'char_start': 39537, 'char_end': 39543},
     'premise_kind': 'day_master_state', 'premise_day_master_state': '旺',
     'premise_form': None, 'condition_quantifiers': (),
     'direction_verbs': ('泄', '伤'), 'direction_gods': ('食伤', '官杀'),
     'direction_basis': 'term_gloss 泄者食伤也，伤者官杀也',
     'applicability': 'premise_only'},
    {'id': 'f1-general-weak', 'kind': 'general_rule',
     'quote_id': 'fy.shaiwang_yuanzhu',
     'passage_id': 'ditiansui.fuyi_shaiwang', 'layer': '原注',
     'text': '衰则喜帮喜助',
     'locator': {'char_start': 39544, 'char_end': 39550},
     'premise_kind': 'day_master_state', 'premise_day_master_state': '弱',
     'premise_form': None, 'condition_quantifiers': (),
     'direction_verbs': ('帮', '助'), 'direction_gods': ('比劫', '印绶'),
     'direction_basis': 'term_gloss 帮者比劫也，助者印绶也',
     'applicability': 'premise_only'},
    {'id': 'f2-form-full', 'kind': 'verse_principle',
     'quote_id': 'fy.xingxiang_verse',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '诗句',
     'text': '形全者宜损其有余',
     'locator': {'char_start': 27046, 'char_end': 27054},
     'premise_kind': 'form', 'premise_day_master_state': None,
     'premise_form': '形全', 'condition_quantifiers': ('有余',),
     'direction_verbs': ('损',), 'direction_gods': (),
     'direction_basis': '损/补为取用动词，非十神类，不入条件方向神类',
     'applicability': 'premise_only'},
    {'id': 'f2-form-deficient', 'kind': 'verse_principle',
     'quote_id': 'fy.xingxiang_verse',
     'passage_id': 'ditiansui.fuyi_xingxiang', 'layer': '诗句',
     'text': '形缺者宜补其不足',
     'locator': {'char_start': 27055, 'char_end': 27063},
     'premise_kind': 'form', 'premise_day_master_state': None,
     'premise_form': '形缺', 'condition_quantifiers': ('不足',),
     'direction_verbs': ('补',), 'direction_gods': (),
     'direction_basis': '损/补为取用动词，非十神类，不入条件方向神类',
     'applicability': 'premise_only'},
    {'id': 'f3-general', 'kind': 'general_rule',
     'quote_id': 'fy.tiyong_general_rule',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '旺则抑之,弱则扶之',
     'locator': {'char_start': 35441, 'char_end': 35450},
     'premise_kind': 'day_master_state', 'premise_day_master_state': '旺/弱',
     'premise_form': None, 'condition_quantifiers': (),
     'direction_verbs': ('抑', '扶'), 'direction_gods': (),
     'direction_basis': '抑/扶为总则动词，无已登记的十神类 gloss，不映射为神类',
     'applicability': 'premise_only'},
    {'id': 'f3-tigang-strong', 'kind': 'direction_statement',
     'quote_id': 'fy.tiyong_tigang',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '如日主旺,提纲或官或财或食伤,皆可为用',
     'locator': {'char_start': 35585, 'char_end': 35604},
     'premise_kind': 'day_master_state', 'premise_day_master_state': '旺',
     'premise_form': None, 'condition_quantifiers': (),
     'direction_verbs': (), 'direction_gods': ('官', '财', '食伤'),
     'direction_basis': '原文逐字列举官/财/食伤；适用性须先定提纲十神',
     'applicability': 'needs_tigang'},
    {'id': 'f3-tigang-weak', 'kind': 'direction_statement',
     'quote_id': 'fy.tiyong_tigang',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '日主衰,别寻四柱干支有帮身者为用',
     'locator': {'char_start': 35605, 'char_end': 35621},
     'premise_kind': 'day_master_state', 'premise_day_master_state': '弱',
     'premise_form': None, 'condition_quantifiers': (),
     'direction_verbs': ('帮身',), 'direction_gods': ('比劫', '印绶'),
     'direction_basis': 'term_gloss 帮者比劫也，助者印绶也；'
                        '只计显干（输入契约无藏干事实）',
     'applicability': 'needs_pillars'},
    {'id': 'f3-table-preamble', 'kind': 'table_preamble',
     'quote_id': 'fy.tiyong_table_para',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '如四柱干支财杀过旺,日主旺中变弱,须寻其帮身制化财杀者而用之',
     'locator': {'char_start': 35660, 'char_end': 35690},
     'premise_kind': 'preamble', 'premise_day_master_state': None,
     'premise_form': None, 'condition_quantifiers': ('过旺',),
     'direction_verbs': ('帮身', '制化'), 'direction_gods': (),
     'direction_basis': '表前引：前提「旺中变弱」非古典分类值，程序句非神类',
     'applicability': 'not_evaluable'},
)

# 补充反转/反例条款：只登记、不评估（前提「中有衰/旺者存」「不可抑/
# 不可扶」「极」均无操作定义或未阈值化，无可机械执行的判据）。
FUYI_SUPPLEMENTAL_GUARDS = (
    {'id': 'f1-counter-strong', 'kind': 'counter_clause',
     'quote_id': 'fy.shaiwang_yuanzhu',
     'passage_id': 'ditiansui.fuyi_shaiwang', 'layer': '原注',
     'text': '旺中有衰者存,不可损也',
     'locator': {'char_start': 39558, 'char_end': 39569},
     'condition_quantifiers': (),
     'reason_not_evaluated': '前提「旺中有衰者存」无操作定义：'
                             '何者为当存之衰者未界定，不评估。'},
    {'id': 'f1-counter-weak', 'kind': 'counter_clause',
     'quote_id': 'fy.shaiwang_yuanzhu',
     'passage_id': 'ditiansui.fuyi_shaiwang', 'layer': '原注',
     'text': '衰右有旺者存,不可益也',
     'locator': {'char_start': 39570, 'char_end': 39581},
     'condition_quantifiers': (),
     'reason_not_evaluated': '前提「衰中有旺者存」无操作定义：'
                             '何者为当存之旺者未界定，不评估。'},
    {'id': 'f3-reversal-strong', 'kind': 'reversal_clause',
     'quote_id': 'fy.tiyong_general_rule',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '旺则抑之,如不可抑,反宜扶之',
     'locator': {'char_start': 35482, 'char_end': 35496},
     'condition_quantifiers': (),
     'reason_not_evaluated': '反转条件「不可抑」无操作定义，'
                             '不评估；其存在使总则不可机械执行。'},
    {'id': 'f3-reversal-weak', 'kind': 'reversal_clause',
     'quote_id': 'fy.tiyong_general_rule',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '弱则扶之,如不可扶,反宜抑之',
     'locator': {'char_start': 35497, 'char_end': 35511},
     'condition_quantifiers': (),
     'reason_not_evaluated': '反转条件「不可扶」无操作定义，'
                             '不评估；其存在使总则不可机械执行。'},
    {'id': 'f3-extreme-strong', 'kind': 'extreme_reversal_clause',
     'quote_id': 'fy.tiyong_general_rule',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '旺极者抑之,抑之反激而有害,则宜从其强而扶之',
     'locator': {'char_start': 35529, 'char_end': 35551},
     'condition_quantifiers': ('极',),
     'reason_not_evaluated': '触发状态「极」未阈值化，不评估。'},
    {'id': 'f3-extreme-weak', 'kind': 'extreme_reversal_clause',
     'quote_id': 'fy.tiyong_general_rule',
     'passage_id': 'ditiansui.fuyi_tiyong', 'layer': '任氏曰',
     'text': '弱极者扶之,扶之徒劳而无功,则宜从其弱而抑之',
     'locator': {'char_start': 35552, 'char_end': 35574},
     'condition_quantifiers': ('极',),
     'reason_not_evaluated': '触发状态「极」未阈值化，不评估。'},
)

# --- 扶抑现代工程层输入边界（第三批）------------------------------------
# 转录自已批准的现代模型常量（bazi_strength_engine.MODERN_WEIGHTS
# 各分项 range、MODERN_SCORE_RANGE、MODERN_THRESHOLDS）；漂移即
# fail-closed，专项测试在可导入时逐项核对，漂移即失败。
MODERN_SCORE_RANGE = (-35, 105)
MODERN_THRESHOLDS = {'strong_at_least': 60, 'weak_at_most': 15,
                     'balanced_between': [16, 59]}
MODERN_COMPONENT_RANGES = {
    'de_ling': (-15, 30), 'de_di': (0, 35), 'de_shi': (0, 30),
    'shengfu_hidden': (0, 10), 'kexiehao': (-20, 0),
}
MODERN_COMPONENT_NAMES = {
    'de_ling': '得令', 'de_di': '得地', 'de_shi': '得势',
    'shengfu_hidden': '藏干生扶', 'kexiehao': '克泄耗',
}

# --- 病药已登记未编码清单（第三批）---------------------------------------
# 转录自 bazi_bingyao.QUOTES（role 为 registered_not_encoded 的对子句
# 与 registered_tension 的张力句、definition 的定义句）；只登记、不
# 编码、不产药神候选；转录漂移由专项测试在可导入时逐条核对。
BINGYAO_REGISTERED_NOT_ENCODED_PAIRS = (
    {'pair_id': 'earth_heavy_unencoded', 'quote_id': 'earth_example',
     'section_id': 'bazi.section.s071',
     'subject_god_class': '土', 'disease_god_class': '土',
     'medicine_god_class': '木',
     'quote': '是则土为诸格之病,俱喜木为医药,以去其病也',
     'locator': {'line': 38, 'char_start': 7329, 'char_end': 7350},
     'status': 'registered_not_encoded',
     'reason': '示例一（土重）结论句：其前提「四柱纯土水」无操作定义，'
               '且分日主结论为旺弱味断语，不编码。'},
    {'pair_id': 'officer_strength_tension', 'quote_id': 'zhengguan_tension',
     'section_id': 'bazi.section.s072',
     'subject_god_class': '官星', 'disease_god_class': '官星太弱太旺',
     'medicine_god_class': None,
     'quote': '惟官星太弱太旺,方为有病,因其病而药之,斯可作为用神而论祸福也',
     'locator': {'line': 51, 'char_start': 10010, 'char_end': 10041},
     'status': 'registered_tension',
     'reason': '正官格节另一口径：病系于官星太弱太旺，与定义节存在性口径'
               '并存未统一；该口径依赖旺弱裁定且直通用神，本体系不覆盖、'
               '不得引此句升级候选为用神结论。'},
)
BINGYAO_REGISTERED_DEFINITIONS = (
    {'definition_id': 'disease_definition', 'quote_id': 'disease_definition',
     'section_id': 'bazi.section.s071',
     'quote': '何以为之病?原八字中原所害之神也',
     'locator': {'line': 38, 'char_start': 7019, 'char_end': 7035},
     'note': '病之定义：局中「所害之神」。「害」的具体枚举由同节示例句给出。'},
    {'definition_id': 'medicine_definition', 'quote_id': 'medicine_definition',
     'section_id': 'bazi.section.s071',
     'quote': '何以为之药?如八字原有所害之字,而得一字以去之谓了',
     'locator': {'line': 38, 'char_start': 7036, 'char_end': 7061},
     'note': '药之定义：能去病之字。本节示例中「去」的机制均为五行克；'
             '实际克效未裁定。'},
)

# --- 格局用神结构依据：格神十神 -> 相对日主的五行关系（第三批）---------
# 与 ten_god_for 同一十神定义（五行关系＋阴阳同异性）之关系侧；
# 格神元素由关系反推，不另立关系表。
PATTERN_GOD_RELATIONS = {
    '正官': 'controls_me', '七杀': 'controls_me',
    '正印': 'generates_me', '偏印': 'generates_me',
    '正财': 'i_control', '偏财': 'i_control',
    '食神': 'i_generate', '伤官': 'i_generate',
}

# --- 流年 pending 逐项所缺底层规则（第三批）-------------------------------
# 5 项无一可实现：逐项明记所缺的底层规则与所涉裁定，不推演、不改
# implemented / pending 清单（组合引擎 pin 住两清单，改动即漂移）。
ANNUAL_PENDING_DETAIL = (
    {'item': 'annual_tiaohou_derivation',
     'missing_underlying_rule': '流年调候推演规则（流年干支如何取调候用神）',
     'blocked_by_adjudication': 'X4 已批准原局调候三分口径（2026-11-25）；流年调候推演规则本身仍未立',
     'note': '原局调候首取/备选/在盘三分口径已获批，但流年推演规则仍未立，流年调候推演无已获批的底层计算。'},
    {'item': 'annual_bingyao_derivation',
     'missing_underlying_rule': '流年病药推演规则（流年干支如何触发病药对、药去病效力）',
     'blocked_by_adjudication': 'X5 已批准病药药神缺位候选类（2026-11-25）；流年病药推演规则本身仍未立',
     'note': '药去病效力恒未裁定，流年病药推演无已获批的底层计算。'},
    {'item': 'annual_fuyi_derivation',
     'missing_underlying_rule': '流年扶抑推演规则（流年干支如何取扶抑用神）',
     'blocked_by_adjudication': 'X1 已批准现代扶抑规则本身为研究模型（2026-11-25）；流年扶抑推演规则本身仍未立',
     'note': '现代扶抑规则已获批为研究模型，但流年干支如何取扶抑用神的推演规则仍未立，流年扶抑推演无已获批的底层计算。'},
    {'item': 'annual_pattern_yongshen_derivation',
     'missing_underlying_rule': '格局用神逐格规则（逐格用神取法）',
     'blocked_by_adjudication': 'X6 已批准逐格规则开发方向（2026-11-25）；具体逐格规则仍待证据审查',
     'note': '密封树全部格 useful_god 恒未审，具体逐格用神规则仍待证据审查，流年格局用神推演无已获批的底层计算。'},
    {'item': 'unified_annual_verdict',
     'missing_underlying_rule': '统一裁决规则（四体系如何合并为统一流年喜用）',
     'blocked_by_adjudication': 'TJ-013.2 裁决 A（四体系并列呈现、统一裁决恒拒判）',
     'note': '统一裁决恒拒判，流年统一结论永不输出。'},
)

# 流年喜用：组合引擎契约已实现的 4 项 + 本引擎新增的 2 项同类存在性对照。
ANNUAL_IMPLEMENTED = (
    'flow_year_ganzhi_and_ten_god',
    'flow_stem_presence_against_natal_tiaohou_sequence',
    'flow_stem_ten_god_role_against_bingyao_pairs',
    'rule_call_structure',
    'flow_stem_presence_against_fuyi_modern_candidates',
    'flow_stem_presence_against_pattern_basis',
)
ANNUAL_PENDING = (
    'annual_tiaohou_derivation',
    'annual_bingyao_derivation',
    'annual_fuyi_derivation',
    'annual_pattern_yongshen_derivation',
    'unified_annual_verdict',
)

GLOBAL_LIMITATIONS = (
    '本引擎 research_only / public_enabled=false / ai_enabled=false，'
    '不接任何公开场景；不新增公开字段。',
    '四体系并列呈现、统一裁决恒拒判（TJ-013.2 裁决 A）；'
    'unified_verdict 恒为 None，任何体系的候选都不合并为统一喜用神。',
    '古典与现代工程模型严格区分：现代层恒标 modern_engineering、'
    'research_only，不冒充古典规则；现代扶抑规则已获批为现代研究模型'
    '（X1，2026-11-25），仍只作研究级候选，不升格为古典规则。',
    '本引擎不输出吉凶、婚恋、事业、财富断语；不调用真实模型，不开启公开 AI。',
)

_TEN_GOD_BY_RELATION = {
    'same_element': {'same_polarity': '比肩', 'different_polarity': '劫财'},
    'generates_me': {'same_polarity': '偏印', 'different_polarity': '正印'},
    'i_generate': {'same_polarity': '食神', 'different_polarity': '伤官'},
    'controls_me': {'same_polarity': '七杀', 'different_polarity': '正官'},
    'i_control': {'same_polarity': '偏财', 'different_polarity': '正财'},
}
_STEM_POLARITY = {stem: ('阳' if i % 2 == 0 else '阴')
                  for i, stem in enumerate(STEMS)}


# 药神类 -> 所含十神（X5 完善药神条件计算所用；与十神定义同一口径）。
_MEDICINE_CLASS_TEN_GODS = {
    '官杀': ('正官', '七杀'), '财': ('正财', '偏财'),
    '印绶': ('正印', '偏印'), '比劫': ('比肩', '劫财'),
    '食伤': ('食神', '伤官'),
}


def _medicine_class_stems(day_master, god_class):
    """药神类所含之干：十神类→干的纯算术展开。

    只说明哪些干属于该类（相对日主的十神判定），不新立药神规则，
    不据缺位拟制具体干；类未知（如张力句无药类）时返回 None。
    """
    ten_gods = _MEDICINE_CLASS_TEN_GODS.get(god_class)
    if ten_gods is None:
        return None
    return [{'stem': stem, 'ten_god': ten_god_for(day_master, stem),
             'element': stem_element(stem)}
            for stem in STEMS
            if ten_god_for(day_master, stem) in ten_gods]


def _fail(message):
    raise ValueError(message)


def _relation_of(day_element, target_element):
    if target_element == day_element:
        return 'same_element'
    if GENERATES[target_element] == day_element:
        return 'generates_me'
    if GENERATES[day_element] == target_element:
        return 'i_generate'
    if CONTROLS[target_element] == day_element:
        return 'controls_me'
    return 'i_control'


def ten_god_for(day_master, target_stem):
    """十神：与 bazi_core.ten_god 同一判定（五行关系＋阴阳同异性）。

    本地实现，只依赖 foundations，不 import 组合引擎或 bazi_core。
    """
    if day_master not in STEMS or target_stem not in STEMS:
        _fail('ten_god_for requires two heavenly stems')
    relation = _relation_of(stem_element(day_master),
                            stem_element(target_stem))
    polarity = ('same_polarity'
                if _STEM_POLARITY[day_master] == _STEM_POLARITY[target_stem]
                else 'different_polarity')
    return _TEN_GOD_BY_RELATION[relation][polarity]


def _condition(condition_id, statement, status, basis=None):
    row = {'id': condition_id, 'statement': statement, 'status': status}
    if basis is not None:
        row['basis'] = basis
    return row


def _check_statement(statement, variant, label):
    if not isinstance(statement, dict):
        _fail('%s statement must be an object' % label)
    if statement.get('variant') != variant:
        _fail('%s statement variant drifted' % label)
    if statement.get('research_only') is not True:
        _fail('%s statement research_only drifted' % label)
    if statement.get('public_enabled') is not False:
        _fail('%s statement public_enabled drifted' % label)
    if statement.get('ai_enabled') is not False:
        _fail('%s statement ai_enabled drifted' % label)
    return statement


def _normalize_pillars(pillars, day_master):
    """四柱归一化：ganzhi 字符串或 pillar 对象列表，年/月/日/时顺序。"""
    if type(pillars) is not list or len(pillars) != 4:
        _fail('pillars must be four ordered year/month/day/hour pillars')
    names = ('year', 'month', 'day', 'hour')
    normalized = []
    for index, pillar in enumerate(pillars):
        name = names[index]
        if isinstance(pillar, str):
            ganzhi_index(pillar)
            stem, branch = pillar[0], pillar[1]
        elif isinstance(pillar, dict):
            stem = pillar.get('stem')
            if isinstance(stem, dict):
                stem = stem.get('value')
            branch = pillar.get('branch')
            if isinstance(branch, dict):
                branch = branch.get('value')
            if type(stem) is not str or stem not in STEMS:
                _fail('%s stem must be one heavenly stem' % name)
            if type(branch) is not str or branch not in BRANCHES:
                _fail('%s branch must be one earthly branch' % name)
        else:
            _fail('pillar must be a ganzhi string or a pillar object')
        normalized.append({'name': name, 'ganzhi': stem + branch,
                           'stem': stem, 'branch': branch,
                           'stem_ten_god': ('日主' if name == 'day'
                                            else ten_god_for(day_master, stem)),
                           'stem_element': stem_element(stem)})
    if normalized[2]['stem'] != day_master:
        _fail('day_master must equal the day pillar stem')
    return normalized


def _validate_day_month(day_master, month_branch):
    if type(day_master) is not str or day_master not in STEMS:
        _fail('day_master must be one heavenly stem')
    if type(month_branch) is not str or month_branch not in BRANCHES:
        _fail('month_branch must be one earthly branch')


def _modern_uncertainty(modern):
    """把现代模型的 Q5/Q6 不确定性传导为喜用层的标记（X8 口径）。

    土日主得地未校准（Q5）、丁日主火重根集未审（Q5）、四库月得令
    记零（Q6）为条件缺失，入 uncertainty 并降 confidence 为
    provisional。balanced 只是现代模型分数区间（Q9：16–59 分），
    本身不代表输入证据不足——不入 uncertainty（X8，用户裁定
    2026-11-25）。
    """
    flags = []
    if not isinstance(modern, dict):
        return flags
    limitations = modern.get('limitations') or []
    text = '\n'.join(str(item) for item in limitations)
    if '土日主无已审重根集' in text:
        flags.append('earth_de_di_uncalibrated')
    if '丁日主火重根集未审' in text:
        flags.append('ding_de_di_uncalibrated')
    if '四库' in text and '得令分恒为 0' in text:
        flags.append('tomb_de_ling_zero_provisional')
    if '四库' in text and '得令分记 0' in text:
        flags.append('tomb_de_ling_zero_provisional')
    return sorted(set(flags))


def _element_for_relation(day_element, relation):
    """由十神关系反推格神五行（与 ten_god_for 同一十神定义）。"""
    if relation == 'same_element':
        return day_element
    if relation == 'generates_me':
        return next(e for e in ('木', '火', '土', '金', '水')
                    if GENERATES[e] == day_element)
    if relation == 'i_generate':
        return GENERATES[day_element]
    if relation == 'controls_me':
        return next(e for e in ('木', '火', '土', '金', '水')
                    if CONTROLS[e] == day_element)
    return CONTROLS[day_element]


def _form_of(day_master, month_branch):
    """形全/形缺：只认原注枚举的四干组合，其余恒不可判（不类推）。"""
    pair = (day_master, month_branch)
    if pair in FUYI_FORM_ENUMERATION['form_full']:
        return '形全'
    if pair in FUYI_FORM_ENUMERATION['form_deficient']:
        return '形缺'
    return None


def _premise_status_for_state(premise, classification):
    if premise == '旺/弱':
        return ('satisfied' if classification in ('strong', 'weak')
                else 'cannot_judge')
    want = {'旺': 'strong', '弱': 'weak'}[premise]
    if classification == want:
        return 'satisfied'
    if classification in ('strong', 'weak'):
        return 'not_satisfied'
    return 'cannot_judge'


def _supplemental_direction_rows(classification, day_master, month_branch,
                                 normalized_pillars):
    """补充登记方向陈述逐行核对：前提可判、量化词恒不可判、无行点火。

    返回 (rows, guards, conditional_gods, form)。``rows`` 为 8 条方向
    陈述；``guards`` 为 6 条反转/反例条款（只登记、不评估）；
    ``conditional_gods`` 为前提成立且适用性满足的行的方向神类（去重，
    保序）；``form`` 为形全/形缺/None。
    """
    form = _form_of(day_master, month_branch)
    rows = []
    conditional_gods = []
    for spec in FUYI_SUPPLEMENTAL_STATEMENTS:
        if spec['premise_kind'] == 'form':
            if form is None:
                premise_status = 'cannot_judge'
            elif form == spec['premise_form']:
                premise_status = 'satisfied'
            else:
                premise_status = 'not_satisfied'
        elif spec['premise_kind'] == 'preamble':
            premise_status = 'cannot_judge'
        else:
            premise_status = _premise_status_for_state(
                spec['premise_day_master_state'], classification)
        quantifiers = [
            {'term': term, 'status': 'cannot_judge',
             'reason': 'quantifier_unthresholded_no_counting_convention'}
            for term in spec['condition_quantifiers']]
        applicability = spec['applicability']
        helper_stems = None
        contributed = []
        if applicability == 'needs_tigang':
            applicability_status = 'cannot_judge'
            applicability_note = ('适用性须先定提纲十神（月支本气十神）；'
                                  '本引擎输入契约无藏干事实，不评估适用性。')
        elif applicability == 'needs_pillars':
            if normalized_pillars is None:
                applicability_status = 'cannot_judge'
                applicability_note = '未传入四柱，帮身者在场性不可判。'
            else:
                helper_stems = [
                    {'stem': row['stem'], 'pillar': row['name'],
                     'ten_god': row['stem_ten_god'],
                     'element': row['stem_element']}
                    for row in normalized_pillars
                    if row['name'] != 'day'
                    and row['stem_ten_god'] in ('比肩', '劫财', '正印', '偏印')]
                if helper_stems:
                    applicability_status = 'satisfied'
                    applicability_note = ('显干见帮身者 %s。'
                                          % '、'.join('%s（%s）' % (
                                              h['stem'], h['ten_god'])
                                              for h in helper_stems))
                else:
                    applicability_status = 'not_satisfied'
                    applicability_note = '显干无帮身者（比劫/印绶）之干。'
        elif applicability == 'not_evaluable':
            applicability_status = 'cannot_judge'
            applicability_note = ('前提「旺中变弱」非古典分类值，'
                                  '且含量化词「过旺」：不评估。')
        else:
            applicability_status = 'satisfied'
            applicability_note = '只以前提为适用条件。'
        if spec['condition_quantifiers']:
            row_outcome = 'cannot_fire_quantifier_unthresholded'
            outcome_reason = ('含量化词（%s）且未阈值化（U3 Q1=B：'
                              '不设计数口径），故本行不点火、不给方向结论。'
                              % '、'.join(spec['condition_quantifiers']))
        else:
            row_outcome = 'conditional_only_no_mechanical_selection'
            outcome_reason = ('无量化词，但任氏曰明言四字须分用、通变在'
                              '一「宜」字且带反转条款，故本行只作条件方向，'
                              '不点火、不给方向结论。')
        if premise_status == 'satisfied' \
                and applicability_status == 'satisfied':
            if spec['id'] == 'f3-tigang-weak':
                contributed = [g for g in ('比劫', '印绶')
                               if any(h['ten_god'] in (
                                   ('比肩', '劫财') if g == '比劫'
                                   else ('正印', '偏印'))
                                   for h in (helper_stems or []))]
            else:
                contributed = list(spec['direction_gods'])
            for god in contributed:
                if god not in conditional_gods:
                    conditional_gods.append(god)
        rows.append({
            'id': spec['id'], 'kind': spec['kind'],
            'quote_id': spec['quote_id'],
            'passage_id': spec['passage_id'], 'layer': spec['layer'],
            'text': spec['text'], 'locator': dict(spec['locator']),
            'premise_kind': spec['premise_kind'],
            'premise_day_master_state': spec['premise_day_master_state'],
            'premise_form': spec['premise_form'],
            'premise_status': premise_status,
            'condition_quantifiers': quantifiers,
            'direction_verbs': list(spec['direction_verbs']),
            'direction_gods': list(spec['direction_gods']),
            'direction_basis': spec['direction_basis'],
            'applicability': applicability,
            'applicability_status': applicability_status,
            'applicability_note': applicability_note,
            'helper_stems': helper_stems,
            'conditional_gods': contributed,
            'row_outcome': row_outcome,
            'outcome_reason': outcome_reason,
        })
    guards = [{
        'id': guard['id'], 'kind': guard['kind'],
        'quote_id': guard['quote_id'],
        'passage_id': guard['passage_id'], 'layer': guard['layer'],
        'text': guard['text'], 'locator': dict(guard['locator']),
        'condition_quantifiers': [
            {'term': term, 'status': 'cannot_judge',
             'reason': 'quantifier_unthresholded_no_counting_convention'}
            for term in guard['condition_quantifiers']],
        'evaluation': 'not_evaluated',
        'reason_not_evaluated': guard['reason_not_evaluated'],
    } for guard in FUYI_SUPPLEMENTAL_GUARDS]
    return rows, guards, conditional_gods, form


def _check_modern_input(modern_in):
    """现代层输入边界校验（转录自已批准的现代模型常量，漂移即拒收）。

    弃判态：score 与 components 恒为 None；非弃判态：score 为整数、
    在总分域 [-35, 105] 内、verdict 与分数档位一致；components 若在
    场：键须为已知的 5 个分项、每分项分数为整数且在其分项域内、5 项
    齐全时分项和等于总分。返回 (score, components)。
    """
    verdict = modern_in.get('verdict')
    score = modern_in.get('score')
    components = modern_in.get('components')
    if verdict == 'abstain':
        if score is not None:
            _fail('strength modern abstain must carry score None')
        if components is not None:
            _fail('strength modern abstain must carry components None')
        return None, None
    if type(score) is not int:
        _fail('strength modern score must be an integer for a non-abstain verdict')
    low, high = MODERN_SCORE_RANGE
    if not low <= score <= high:
        _fail('strength modern score out of registered range')
    band = ('strong' if score >= MODERN_THRESHOLDS['strong_at_least']
            else 'weak' if score <= MODERN_THRESHOLDS['weak_at_most']
            else 'balanced')
    if band != verdict:
        _fail('strength modern verdict/score band mismatch')
    if components is not None:
        if not isinstance(components, dict):
            _fail('strength modern components must be an object or None')
        for key, entry in components.items():
            if key not in MODERN_COMPONENT_RANGES:
                _fail('strength modern component drifted')
            if not isinstance(entry, dict) \
                    or type(entry.get('score')) is not int:
                _fail('strength modern component score must be an integer')
            comp_low, comp_high = MODERN_COMPONENT_RANGES[key]
            if not comp_low <= entry['score'] <= comp_high:
                _fail('strength modern component score out of registered range')
        if set(components) == set(MODERN_COMPONENT_RANGES):
            if sum(entry['score'] for entry in components.values()) != score:
                _fail('strength modern component scores do not sum to total')
    return score, components


def _component_explanations(components):
    """分项解释：只读分项分数符号的方向性，不构成独立的方向结论。"""
    explanations = []
    if not isinstance(components, dict):
        return explanations
    for key in ('de_ling', 'de_di', 'de_shi', 'shengfu_hidden', 'kexiehao'):
        entry = components.get(key)
        if not isinstance(entry, dict):
            continue
        score = entry['score']
        low, high = MODERN_COMPONENT_RANGES[key]
        if score > 0:
            reading, reading_cn = 'supports_strong_side', '该分项指向强侧'
        elif score < 0:
            reading, reading_cn = 'supports_weak_side', '该分项指向弱侧'
        else:
            reading, reading_cn = 'neutral', '该分项中性（零分）'
        explanations.append({
            'component': key, 'name_cn': MODERN_COMPONENT_NAMES[key],
            'score': score, 'range': [low, high],
            'reading': reading,
            'at_bound': score in (low, high),
            'note': '%s分 %+d：%s；分项符号读数，不构成独立的方向结论。'
                    % (MODERN_COMPONENT_NAMES[key], score, reading_cn)})
    return explanations


def _input_completeness(*, verdict_present, score_present,
                        score_in_range, band_matches, components_present,
                        components_complete, components_sum_matches,
                        pillars_present, candidate_stems_computed):
    return {
        'verdict_present': verdict_present,
        'score_present': score_present,
        'score_in_registered_range': score_in_range,
        'band_matches_thresholds': band_matches,
        'components_present': components_present,
        'components_complete': components_complete,
        'components_sum_matches_score': components_sum_matches,
        'pillars_present': pillars_present,
        'candidate_stems_computed': candidate_stems_computed,
    }


def _classical_direction_rows(classification):
    """古典方向表逐行核对：前提可判、量化词恒不可判、故无行点火。"""
    rows = []
    conditional = []
    premise_map = {'strong': '旺', 'weak': '弱'}
    for spec in FUYI_DIRECTION_TABLE['rows']:
        premise = spec['premise_day_master_state']
        if premise in ('旺', '弱'):
            if classification in premise_map \
                    and premise_map[classification] == premise:
                premise_status = 'satisfied'
            elif classification in ('strong', 'weak'):
                premise_status = 'not_satisfied'
            else:
                premise_status = 'cannot_judge'
        else:  # 两停 / 均敌：古典层无此分类，恒不可判。
            premise_status = 'cannot_judge'
        row = {
            'row': spec['row'],
            'text': spec['text'],
            'premise_day_master_state': premise,
            'premise_status': premise_status,
            'condition_quantifiers': [
                {'term': term, 'status': 'cannot_judge',
                 'reason': 'quantifier_unthresholded_no_counting_convention'}
                for term in spec['condition_quantifiers']],
            'direction_god': spec['direction_god'],
            'row_outcome': 'cannot_fire_quantifier_unthresholded',
        }
        rows.append(row)
        if premise_status == 'satisfied' \
                and spec['direction_god'] not in conditional:
            conditional.append(spec['direction_god'])
    return rows, conditional


def evaluate_fuyi(strength, *, pillars=None):
    """扶抑取用：古典定性层＋条件谓词层＋现代工程层，三层并列。

    ``strength`` 为 ``assess_strength`` 的输出字典（可为 None，
    表示未传入）。``pillars`` 为四柱（可选；用于现代候选干的显干核对）。
    """
    base = {'system': 'fuyi', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if strength is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'classical': None, 'modern': None, 'cross_layer': None,
                'basis': None,
                'conditions': [_condition(
                    'strength_input', '未传入已审强弱输出', 'not_satisfied')],
                'limitations': [
                    '未传入强弱输出：古典层与现代层均无输入依据，扶抑不作任何判断。'],
                'uncertainty': ['strength_input_missing']}
    _check_statement(strength, STRENGTH_ENGINE_VARIANT, 'strength')
    day_master = strength.get('day_master')
    month_branch = strength.get('month_branch')
    _validate_day_month(day_master, month_branch)
    classical_in = strength.get('classical') or {}
    classification = classical_in.get('classification')
    if classification not in ('strong', 'weak', 'indeterminate'):
        _fail('strength classical classification drifted')
    matched = classical_in.get('matched_predicate')
    matched_id = matched.get('predicate_id') if isinstance(matched, dict) \
        else None
    modern_in = strength.get('modern')
    if modern_in is not None:
        if not isinstance(modern_in, dict):
            _fail('strength modern layer must be an object or None')
        if modern_in.get('model_id') != MODERN_MODEL_ID:
            _fail('strength modern model_id drifted')
        if modern_in.get('model_kind') != 'modern_engineering':
            _fail('strength modern model_kind drifted')
        if modern_in.get('verdict') not in (
                'strong', 'weak', 'balanced', 'abstain'):
            _fail('strength modern verdict drifted')

    # 四柱归一化一次，供补充行（提纲衰行需显干帮身者）与现代候选干共用。
    normalized_pillars = (_normalize_pillars(pillars, day_master)
                          if pillars is not None else None)

    # 古典层：逐行核对方向表；无行点火，只给前提成立行的条件方向。
    rows, conditional = _classical_direction_rows(classification)
    # 补充登记方向陈述：同上逐行核对，同样无行点火。
    supp_rows, supp_guards, supp_conditional, form = \
        _supplemental_direction_rows(classification, day_master,
                                     month_branch, normalized_pillars)
    for god in supp_conditional:
        if god not in conditional:
            conditional.append(god)
    classical = {
        'layer': 'classical_qualitative',
        'classification': classification,
        'matched_predicate': matched_id,
        'matched_predicate_verification': (
            matched.get('verification') if isinstance(matched, dict) else None),
        'rows': rows,
        'conditional_directions': conditional,
        'supplemental_rows': supp_rows,
        'supplemental_guards': supp_guards,
        'term_glosses': [dict(gloss) for gloss in FUYI_TERM_GLOSSES],
        'form_classification': {
            'form': form,
            'basis': ('registered_enumeration' if form is not None
                      else 'analogy_forbidden'),
            'day_master': day_master, 'month_branch': month_branch,
            'note': ('形全/形缺只认原注枚举的四干组合；'
                     '未列组合不以「余仿此」类推，恒不可判。')},
        'direction': None,
        'direction_status': 'no_row_fires',
        'reason': ('方向表十行全部含量化词（多/轻/重/旺/两停/均敌）且'
                   '未阈值化（U3 Q1=B：不设计数口径），补充登记方向陈述'
                   '（F-1 总纲、F-2 形全/形缺、F-3 总则/提纲/表前引）'
                   '同样无行点火——无量化词的行受四字分用反机械告诫与'
                   '反转条款约束，提纲行缺月支本气十神输入；故古典层不给'
                   '方向结论；前提成立行的方向神只作条件方向并列。'),
    }

    # 现代层：已批研究模型规则（X1）以现代 verdict 定方向与候选干。
    # 先作输入边界校验（总分域、分项域、档位一致、分项和），漂移即拒收。
    if modern_in is not None:
        _check_modern_input(modern_in)
    modern_components = (modern_in.get('components')
                         if modern_in is not None else None)
    explanations = _component_explanations(modern_components)
    pillars_present = pillars is not None
    uncertainty = _modern_uncertainty(modern_in) if modern_in else []
    if classification == 'indeterminate':
        uncertainty.append('classical_strength_indeterminate')
    uncertainty = sorted(set(uncertainty))
    modern = None
    if modern_in is None:
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': 'not_provided',
            'input_verdict': None, 'input_score': None,
            'rule_id': None, 'direction': None, 'direction_cn': None,
            'direction_elements': [], 'ten_god_classes': [],
            'candidate_stems': None,
            'candidate_scope': 'visible_stems_only',
            'confidence': None,
            'uncertainty': uncertainty,
            'input_completeness': _input_completeness(
                verdict_present=False, score_present=False,
                score_in_range=None, band_matches=None,
                components_present=False, components_complete=False,
                components_sum_matches=None,
                pillars_present=pillars_present,
                candidate_stems_computed=False),
            'component_explanations': [],
            'direction_derivation': None,
            'reason': '未启用现代模型（include_modern=False），现代层无输入。'}
    elif modern_in.get('verdict') == 'abstain':
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': 'abstain',
            'input_verdict': 'abstain',
            'input_score': None,
            'abstain_reason': modern_in.get('abstain_reason'),
            'abstain_detail': modern_in.get('abstain_detail'),
            'rule_id': None, 'direction': None, 'direction_cn': None,
            'direction_elements': [], 'ten_god_classes': [],
            'candidate_stems': None,
            'candidate_scope': 'visible_stems_only',
            'confidence': None,
            'uncertainty': uncertainty,
            'input_completeness': _input_completeness(
                verdict_present=True, score_present=False,
                score_in_range=None, band_matches=None,
                components_present=False, components_complete=False,
                components_sum_matches=None,
                pillars_present=pillars_present,
                candidate_stems_computed=False),
            'component_explanations': [],
            'direction_derivation': None,
            'reason': '现代模型弃判（%s），现代层不给扶抑方向。'
                      % modern_in.get('abstain_reason')}
    else:
        verdict = modern_in.get('verdict')
        rule = next((r for r in FUYI_MODERN_RULES_V1['rules']
                     if r['modern_verdict'] == verdict), None)
        direction_elements = []
        day_element = stem_element(day_master)
        for relation in rule['element_relations']:
            for element in ('木', '火', '土', '金', '水'):
                if _relation_of(day_element, element) == relation:
                    direction_elements.append(element)
        candidate_stems = None
        if pillars is not None:
            candidate_stems = []
            for row in normalized_pillars:
                if row['name'] == 'day':
                    continue
                if row['stem_element'] in direction_elements:
                    candidate_stems.append({
                        'stem': row['stem'], 'pillar': row['name'],
                        'ten_god': row['stem_ten_god'],
                        'element': row['stem_element']})
        components_complete = (
            isinstance(modern_components, dict)
            and set(modern_components) == set(MODERN_COMPONENT_RANGES))
        components_sum_matches = (
            sum(entry['score'] for entry in modern_components.values())
            == modern_in.get('score')
            if components_complete else None)
        modern = {
            'model_id': FUYI_MODERN_RULES_V1['model_id'],
            'model_kind': 'modern_engineering',
            'adjudication_status':
                FUYI_MODERN_RULES_V1['adjudication_status'],
            'status': ('direction_candidate'
                       if rule['direction'] is not None
                       else 'indeterminate_direction'),
            'input_verdict': verdict,
            'input_score': modern_in.get('score'),
            'input_components': modern_in.get('components'),
            'rule_id': rule['rule_id'],
            'direction': rule['direction'],
            'direction_cn': rule['direction_cn'],
            'direction_elements': direction_elements,
            'ten_god_classes': list(rule['ten_god_classes']),
            'candidate_stems': candidate_stems,
            'candidate_scope': 'visible_stems_only',
            'confidence': ('provisional' if uncertainty
                           else 'model_candidate'),
            'uncertainty': uncertainty,
            'input_completeness': _input_completeness(
                verdict_present=True, score_present=True,
                score_in_range=True, band_matches=True,
                components_present=modern_components is not None,
                components_complete=components_complete,
                components_sum_matches=components_sum_matches,
                pillars_present=pillars_present,
                candidate_stems_computed=candidate_stems is not None),
            'component_explanations': explanations,
            'direction_derivation': [
                {'step': 'input', 'verdict': verdict,
                 'score': modern_in.get('score'),
                 'thresholds': dict(MODERN_THRESHOLDS),
                 'score_range': list(MODERN_SCORE_RANGE)},
                {'step': 'rule_match', 'rule_id': rule['rule_id'],
                 'direction': rule['direction'],
                 'direction_cn': rule['direction_cn'],
                 'element_relations': list(rule['element_relations']),
                 'ten_god_classes': list(rule['ten_god_classes'])},
                {'step': 'element_resolution',
                 'direction_elements': direction_elements},
                {'step': 'candidate_stems',
                 'pillars_present': pillars_present,
                 'candidate_stems': candidate_stems}],
            'reason': (
                '现代模型 %s（%s 分）：方向 %s。'
                % (verdict, modern_in.get('score'), rule['direction_cn'])
                if rule['direction'] is not None else
                '现代模型 balanced（%s 分）只是中间分数带（Q9），'
                '不是古典中和裁决：现代层不给扶抑方向。'
                % modern_in.get('score')),
        }

    # 两层关系：并列，不以任一侧覆盖另一侧。
    modern_verdict = modern_in.get('verdict') if modern_in else None
    if modern_in is None:
        relationship, note = 'modern_not_provided', '现代模型未启用。'
    elif modern_verdict == 'abstain':
        relationship = 'modern_abstains'
        note = '现代层弃判（%s）；古典层结论 %s 保持独立。' % (
            modern_in.get('abstain_reason'), classification)
    elif classification == 'indeterminate':
        relationship = 'classical_indeterminate'
        note = '古典层暂不可判；现代层 %s 只是工程近似，不替古典层裁决。' \
            % modern_verdict
    elif ((classification == 'strong' and modern_verdict == 'strong')
            or (classification == 'weak' and modern_verdict == 'weak')):
        relationship = 'agree'
        note = '两层结论一致（%s），但依据不同：古典谓词 vs 工程评分，仍并列报告。' \
            % classification
    elif modern_verdict == 'balanced':
        relationship = 'modern_balanced'
        note = '古典层 %s；现代层 balanced（中间带），不是古典中和裁决。' \
            % classification
    else:
        relationship = 'conflict'
        note = '两层冲突：古典层 %s，现代层 %s；不强制统一，待用户裁定。' \
            % (classification, modern_verdict)
    cross_layer = {'classical': classification, 'modern': modern_verdict,
                   'relationship': relationship, 'note': note}

    modern_direction = modern.get('direction_cn')
    if modern_direction is not None:
        status = 'presented'
        conclusion = '扶抑现代层候选方向：%s（研究模型，未裁定）；古典层无方向结论。' \
            % modern_direction
    elif conditional:
        status = 'presented'
        conclusion = '扶抑只给条件方向：古典前提成立行的方向神为 %s（量化词未阈值化，须另行裁定）；现代层未给方向。' \
            % '、'.join(conditional)
    else:
        status = 'not_judgeable'
        conclusion = None
    conditions = [
        _condition('classical_premise_evaluated',
                   '古典层分类 %s 已用于方向表十行的前提核对' % classification,
                   'satisfied'),
        _condition('direction_table_quantifiers',
                   '方向表十行的量化词（多/轻/重/旺/两停/均敌）全部未阈值化',
                   'cannot_judge',
                   basis='U3 Q1=B：不设计数口径；前提成立行的条件方向并列'
                         '呈现已获批（X3，2026-11-25）'),
        _condition('supplemental_directions_evaluated',
                   '补充登记方向陈述 8 条已逐行核对（F-1 总纲 2、F-2 形全/形缺 2、'
                   'F-3 总则 1、提纲 2、表前引 1）；反转/反例条款 6 条只登记不评估',
                   'satisfied'),
        _condition('form_classification',
                   '形全/形缺：%s' % (form if form is not None else '未列组合，不可判'),
                   'satisfied' if form is not None else 'cannot_judge',
                   basis='原注只枚举甲/丙形全、戊/庚形缺，余仿此不展开'),
        _condition('modern_input',
                   '现代模型 verdict=%s score=%s'
                   % (modern_verdict, modern_in.get('score')
                      if modern_in else None),
                   'satisfied' if modern_in is not None else 'not_satisfied'),
        _condition('modern_input_boundaries',
                   '现代层输入边界：总分域 [-35, 105]、分项域、verdict 与分数档位'
                   '一致、分项和等于总分',
                   'satisfied' if modern_in is not None
                   and modern_verdict != 'abstain' else 'not_satisfied',
                   basis='边界常量转录自已批准的现代模型，漂移即拒收'),
    ]
    limitations = [
        '古典扶抑方向表十行全部含量化词且未阈值化：本层不输出古典方向结论，'
        '只列前提成立行的条件方向；涉及改变阈值化的规则须集中提交用户裁定。',
        '补充方向陈述同样不点火：F-1 总纲与 F-3 总则无量化词，但任氏曰明言'
        '四字须分用、通变在一「宜」字且带反转条款，故只作条件方向；提纲为用'
        '需月支本气十神，本引擎输入契约无藏干事实，不评估适用性；形全/形缺'
        '只认原注枚举的四干组合，其余不以「余仿此」类推。',
        '现代扶抑规则（FUYI_MODERN_RULES_V1）已获批为现代研究模型'
        '（X1，2026-11-25），仍只作研究级候选，不冒充古典规则；'
        '候选干只取显干（X2 已批准显干候选口径），不据藏干补位，'
        '不作确定用神。',
        '现代层分项解释只读分项分数符号的方向性，不构成独立的方向结论；'
        '输入边界校验（总分域、分项域、档位一致、分项和）只校验输入一致性，'
        '不改变规则本身的已批研究模型状态。',
        'balanced 只是现代模型中间分数带（Q9），不是古典中和：balanced 时'
        '现代层不给方向；balanced 本身不代表输入证据不足，不入 uncertainty'
        '（X8，2026-11-25）。',
        '土日主得地未校准（Q5）、丁日主火重根集未审（Q5）、四库月得令记零'
        '（Q6）的不确定性已由 uncertainty 标记传导进本层，confidence 相应'
        '降为 provisional，不得在喜用层洗成确定结论（X8，2026-11-25）。',
        '从格候选屏、合化未裁定等现代模型弃判原因原样传导：现代层弃判时'
        '不另给方向。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'classical': classical, 'modern': modern,
            'cross_layer': cross_layer,
            'basis': {
                'strength_variant': STRENGTH_ENGINE_VARIANT,
                'day_master': day_master, 'month_branch': month_branch,
                'classical_classification': classification,
                'classical_matched_predicate': matched_id,
                'modern_verdict': modern_verdict,
                'modern_score': modern_in.get('score')
                                if modern_in else None},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': uncertainty}


def evaluate_tiaohou_xiyong(tiaohou, *, pillars=None):
    """调候取用：消费 tiaohou_lookup 输出，月令条件→候选调候用神。"""
    base = {'system': 'tiaohou', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if tiaohou is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'condition': None, 'active_sequence': None,
                'branches': {'applied': [], 'unapplied': []},
                'related_entries': [], 'entry_notes': [],
                'candidates': [], 'canonical_first': None,
                'canonical_alternatives': [], 'in_chart_candidates': [],
                'operative_candidate': None, 'operative_kind': None,
                'operative_status': None, 'gaps': [],
                'basis': None,
                'conditions': [_condition(
                    'tiaohou_input', '未传入已审调候输出', 'not_satisfied')],
                'limitations': ['未传入调候输出，本体系不补调候判断。'],
                'uncertainty': ['tiaohou_input_missing']}
    _check_statement(tiaohou, TIAOHOU_VARIANT, 'tiaohou')
    day_master = tiaohou.get('day_master')
    month_branch = tiaohou.get('month_branch')
    _validate_day_month(day_master, month_branch)
    status_in = tiaohou.get('status')
    if status_in not in ('matched', 'not_applicable'):
        _fail('tiaohou statement status drifted')
    gaps = []
    conditions = []
    if status_in == 'not_applicable':
        return {**base, 'status': 'not_judgeable', 'conclusion': None,
                'condition': {'day_master': day_master,
                              'month_branch': month_branch},
                'active_sequence': None,
                'branches': {'applied': [], 'unapplied': []},
                'related_entries': [], 'entry_notes': [],
                'candidates': [],
                'canonical_first': None, 'canonical_alternatives': [],
                'in_chart_candidates': [],
                'operative_candidate': None, 'operative_kind': None,
                'operative_status': None,
                'gaps': [{'gap_id': 'entry_absent_in_source',
                          'detail': '乙木十二月条目在审定快照中不存在，'
                                    '不以其他月份条目或其他典籍补齐。'}],
                'basis': {'tiaohou_variant': TIAOHOU_VARIANT,
                          'day_master': day_master,
                          'month_branch': month_branch,
                          'status': status_in},
                'conditions': [_condition(
                    'tiaohou_entry', '该日主×月支无审定条目', 'not_satisfied')],
                'limitations': ['条目缺失是来源缺口，不是该盘无调候之论；'
                                '本体系不外推、不借他月条目。'],
                'uncertainty': ['tiaohou_entry_absent']}
    entry = tiaohou.get('entry') or {}
    sequence_in = tiaohou.get('sequence') or []
    branches_in = tiaohou.get('branches') or []
    if not isinstance(branches_in, list):
        _fail('tiaohou statement branches malformed')
    normalized_pillars = (_normalize_pillars(pillars, day_master)
                          if pillars is not None else None)
    visible_stems = ({row['stem'] for row in normalized_pillars}
                     if normalized_pillars is not None else None)
    # 分支逐条校验形态：applied 恒为布尔值，条件恒为缺干存在性事实。
    validated_branches = []
    for branch in branches_in:
        if not isinstance(branch, dict):
            _fail('tiaohou branch must be an object')
        if type(branch.get('applied')) is not bool:
            _fail('tiaohou branch applied flag drifted')
        condition = branch.get('condition')
        if not isinstance(condition, dict) \
                or condition.get('absent_stem') not in STEMS:
            _fail('tiaohou branch condition drifted')
        sequence = branch.get('sequence')
        if not isinstance(sequence, list):
            _fail('tiaohou branch sequence malformed')
        for item in sequence:
            if not isinstance(item, dict) or item.get('stem') not in STEMS:
                _fail('tiaohou branch sequence item drifted')
        validated_branches.append(branch)
    active_kind = 'main'
    active_sequence = sequence_in
    applied_branch = None
    unapplied_branches = []
    for branch in validated_branches:
        if branch.get('applied'):
            if applied_branch is None:
                applied_branch = branch
                active_kind = 'branch:%s' % branch.get('id')
                active_sequence = branch.get('sequence') or []
        else:
            absent_stem = branch['condition']['absent_stem']
            if visible_stems is None:
                presence = 'present_detail_unknown'
            elif absent_stem in visible_stems:
                presence = 'visible'
            else:
                presence = 'hidden'
            unapplied_branches.append({
                'id': branch.get('id'),
                'condition': dict(branch.get('condition') or {}),
                'quote': branch.get('quote'),
                'absent_stem': absent_stem,
                'absent_stem_presence': presence,
                'note': branch.get('note')})
    applied_branches = [{
        'id': applied_branch.get('id'),
        'condition': dict(applied_branch.get('condition') or {}),
        'quote': applied_branch.get('quote'),
        'sequence_stems': [item['stem'] for item in
                           (applied_branch.get('sequence') or [])],
        'note': applied_branch.get('note'),
    }] if applied_branch is not None else []
    # related 与条目注记：只作登记，不并入取用序列（X4 已批准三分口径；
    # related 与注记本身仍只登记、不并入序列）。
    related_in = tiaohou.get('related') or []
    if not isinstance(related_in, list) \
            or any(not isinstance(item, dict)
                   or type(item.get('quote')) is not str
                   or type(item.get('note')) is not str
                   for item in related_in):
        _fail('tiaohou statement related malformed')
    related_entries = [{
        'quote': item.get('quote'), 'locator': item.get('locator'),
        'note': item.get('note')} for item in related_in]
    notes_in = tiaohou.get('notes') or []
    if not isinstance(notes_in, list) \
            or any(type(item) is not str for item in notes_in):
        _fail('tiaohou statement notes malformed')
    entry_notes = list(notes_in)
    candidates = []
    for item in active_sequence:
        stem = item['stem']
        candidates.append({
            'stem': stem, 'order': item['order'],
            'presence': item['presence'],
            'visible_positions': list(item.get('visible_positions') or []),
            'hidden_positions': list(item.get('hidden_positions') or []),
            'ten_god': ten_god_for(day_master, stem),
            'element': stem_element(stem)})
    operative = next((c for c in candidates if c['presence'] != 'absent'),
                     None)
    operative_status = (operative['presence'] if operative is not None
                        else 'absent_all')
    # X4 三分口径（用户裁定 2026-11-25）：原典首选恒为取用序列首位干
    # （不论在盘与否），原典备选为其后序列干，在盘候选为在盘之干；
    # 在盘首取（首个在盘干）与原典首选是两个位置，原典首选缺位时
    # 后续在盘干只作在盘首取，绝不冒充原典首选。
    canonical_first = candidates[0] if candidates else None
    canonical_alternatives = candidates[1:]
    in_chart_candidates = [c for c in candidates
                           if c['presence'] != 'absent']
    operative_kind = (None if operative is None
                      else 'canonical_first' if operative is canonical_first
                      else 'in_chart_first')
    if not active_sequence:
        gaps.append({'gap_id': 'empty_sequence',
                     'detail': '该条目无无条件取用顺序（取用皆系于成局、'
                               '相对旺盛、节气分界等条件），本体系不拟制序列。'})
    if operative is None and active_sequence:
        gaps.append({'gap_id': 'candidates_absent_in_chart',
                     'detail': '调候候选干 %s 均不在盘中（既不透干亦不藏干）；'
                               '本局无在场调候候选，须由大运/流年补位与否另行判断，'
                               '本体系不据缺位推断。'
                     % '、'.join(c['stem'] for c in candidates)})
    if canonical_first is not None \
            and canonical_first['presence'] == 'absent' \
            and operative is not None:
        gaps.append({'gap_id': 'canonical_first_absent',
                     'detail': '原典首选 %s 不在盘（既不透干亦不藏干）；'
                               '在盘首取为 %s（%s在盘），只作在盘首取，'
                               '不冒充原典首选；原典备选 %s。'
                     % (canonical_first['stem'], operative['stem'],
                        '透干' if operative['presence'] == 'visible'
                        else '藏干',
                        '、'.join(c['stem']
                                  for c in canonical_alternatives)
                        or '无')})
    for unencoded in tiaohou.get('unencoded_branches') or []:
        gaps.append({'gap_id': 'unencoded_branch',
                     'detail': '未编码分支（条件超出输入契约）：%s；原因：%s'
                               % (unencoded.get('quote'),
                                  unencoded.get('reason'))})
    if applied_branch is not None:
        conditions.append(_condition(
            'branch_applied', '分支 %s 已应用（%s 不在盘），分支序列取代主序列'
            % (applied_branch.get('id'),
               (applied_branch.get('condition') or {}).get('absent_stem')),
            'satisfied', basis=applied_branch.get('note')))
    else:
        conditions.append(_condition(
            'branch_applied', '无已应用的分支条件，主序列生效',
            'not_satisfied'))
    for unapplied in unapplied_branches:
        conditions.append(_condition(
            'branch_not_applied',
            '分支 %s 未应用：条件干 %s 在盘（%s），主序列生效'
            % (unapplied['id'], unapplied['absent_stem'],
               {'visible': '透干', 'hidden': '藏干',
                'present_detail_unknown': '在盘，显干/藏干未区分（未传入四柱）'}
               [unapplied['absent_stem_presence']]),
            'not_satisfied', basis=unapplied['note']))
    conditions.append(_condition(
        'canonical_first',
        '原典首选：%s（%s）' % (
            canonical_first['stem'] if canonical_first is not None else '无',
            {'visible': '透干在盘', 'hidden': '藏干在盘',
             'absent': '不在盘'}.get(
                canonical_first['presence']) if canonical_first is not None
            else '无序列'),
        'satisfied' if canonical_first is not None
        and canonical_first['presence'] != 'absent'
        else 'not_satisfied'))
    conditions.append(_condition(
        'operative_candidate_present',
        '在盘首取：%s（%s）' % (
            operative['stem'] if operative else '无',
            '即原典首选' if operative_kind == 'canonical_first'
            else '非原典首选，仅为在盘首取'
            if operative is not None else '无在盘候选'),
        'satisfied' if operative is not None else 'not_satisfied'))
    if operative is not None:
        status = 'presented'
        alternatives_text = '、'.join(
            '%s（%s）' % (c['stem'], c['ten_god'])
            for c in canonical_alternatives) or '无'
        if operative_kind == 'canonical_first':
            conclusion = '调候候选：原典首选 %s（%s，%s在盘），原典备选 %s。' % (
                operative['stem'], operative['ten_god'],
                '透干' if operative['presence'] == 'visible' else '藏干',
                alternatives_text)
        else:
            conclusion = ('调候候选：原典首选 %s 不在盘；'
                          '在盘首取 %s（%s，%s在盘），原典备选 %s。' % (
                              canonical_first['stem'], operative['stem'],
                              operative['ten_god'],
                              '透干' if operative['presence'] == 'visible'
                              else '藏干', alternatives_text))
    else:
        status = 'not_judgeable'
        conclusion = None
    limitations = [
        '只陈述条目原文的取用顺序与盘面存在性事实，不作吉凶、强弱、格局或'
        '喜用结论；调候候选不等于确定用神。',
        '来源为 C 级单一电子谱系（简体转写），未做多底本校勘；季总论与分月'
        '条目先次不一致时并列登记，不暗中合并。',
        '未编码分支的条件（成局、相对旺盛、节气分界等）不在本体系输入契约内，'
        '只登记为缺口，不编码、不推断。',
        '未应用的分支只登记条件干在盘的事实，不改主序列首取语义；related 与'
        '条目注记只作登记，不并入取用序列。',
        '原典首选 / 原典备选 / 在盘候选三分（X4，2026-11-25）：原典首选'
        '恒为取用序列首位干；原典首选缺位时，后续在盘干只作在盘首取，'
        '不冒充原典首选。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'condition': {
                'day_master': day_master, 'month_branch': month_branch,
                'month_label': tiaohou.get('month_label'),
                'quote': entry.get('quote'),
                'quote_locator': entry.get('quote_locator'),
                'order_basis': entry.get('order_basis')},
            'active_sequence': active_kind,
            'branches': {'applied': applied_branches,
                         'unapplied': unapplied_branches},
            'related_entries': related_entries,
            'entry_notes': entry_notes,
            'candidates': candidates,
            'canonical_first': canonical_first,
            'canonical_alternatives': canonical_alternatives,
            'in_chart_candidates': in_chart_candidates,
            'operative_candidate': operative,
            'operative_kind': operative_kind,
            'operative_status': operative_status,
            'gaps': gaps,
            'basis': {'tiaohou_variant': TIAOHOU_VARIANT,
                      'day_master': day_master,
                      'month_branch': month_branch,
                      'status': status_in},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['tiaohou_quote_single_lineage_c']}


def evaluate_bingyao_xiyong(bingyao, *, pillars=None):
    """病药取用：消费 bingyao_lookup 输出，逐对独立给药神候选。"""
    base = {'system': 'bingyao', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if bingyao is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'pairs': [], 'gaps': [], 'basis': None,
                'registered_not_encoded_pairs': [
                    dict(item)
                    for item in BINGYAO_REGISTERED_NOT_ENCODED_PAIRS],
                'registered_definitions': [
                    dict(item) for item in BINGYAO_REGISTERED_DEFINITIONS],
                'conditions': [_condition(
                    'bingyao_input', '未传入已审病药输出', 'not_satisfied')],
                'limitations': ['未传入病药输出，本体系不补病药判断。'],
                'uncertainty': ['bingyao_input_missing']}
    _check_statement(bingyao, BINGYAO_VARIANT, 'bingyao')
    day_master = bingyao.get('day_master')
    if type(day_master) is not str or day_master not in STEMS:
        _fail('bingyao statement day_master drifted')
    if bingyao.get('determination') is not None:
        _fail('bingyao statement carries an adjudicated determination')
    pairs_in = bingyao.get('pairs')
    if type(pairs_in) is not list or len(pairs_in) != 2:
        _fail('bingyao statement pairs malformed')
    pairs = []
    gaps = []
    for pair_in in pairs_in:
        rule = pair_in.get('rule') or {}
        pair_id = pair_in.get('pair_id')
        status = pair_in.get('status')
        if status not in ('triggered', 'not_triggered'):
            _fail('bingyao pair status drifted')
        disease = pair_in.get('disease_candidate')
        medicine = pair_in.get('medicine_candidate')
        medicine_status = pair_in.get('medicine_status')
        # X5：药神类所含之干（十神类→干的纯算术展开），缺位与否皆列。
        medicine_class_stems = _medicine_class_stems(
            day_master, rule.get('medicine_god_class'))
        yongshen_candidate = None
        medicine_check = None
        if status == 'triggered' and medicine is not None:
            # 结构核对：药之五行克病之五行（十神类定义构造恒立，此处逐盘复核）。
            disease_element = medicine.get('disease_element')
            medicine_element = medicine.get('medicine_element')
            if disease_element is None or medicine_element is None:
                _fail('bingyao medicine candidate lacks elements')
            medicine_check = (CONTROLS[medicine_element] == disease_element)
            if not medicine_check:
                _fail('bingyao medicine does not control disease element')
            yongshen_candidate = [{
                'stem': god['stem'], 'pillar': god['pillar'],
                'ten_god': god['ten_god'],
                'element': stem_element(god['stem'])}
                for god in medicine.get('gods') or []]
        if status == 'triggered' and medicine is None:
            class_stems_text = (
                '、'.join('%s（%s）' % (g['stem'], g['ten_god'])
                          for g in (medicine_class_stems or []))
                or '未知')
            gaps.append({
                'gap_id': 'medicine_absent_in_chart',
                'pair_id': pair_id,
                'medicine_god_class': rule.get('medicine_god_class'),
                'medicine_class_stems': medicine_class_stems,
                'medicine_presence_scope': 'visible_stems_only',
                'detail': '病已触发（%s），但药神类 %s 在显干中无在场之干；'
                          '该类所含之干为 %s，皆不在盘；'
                          '药神候选只记类，不据缺位拟制具体干。'
                          % ((disease or {}).get('god_class'),
                             rule.get('medicine_god_class'),
                             class_stems_text)})
        if status == 'not_triggered':
            gaps.append({
                'gap_id': 'pair_not_triggered',
                'pair_id': pair_id,
                'detail': '该对未触发（%s）：本对不输出病药候选；'
                          '未触发不是「无病」，无病的成立要求整盘不旺不弱'
                          '且中和的裁定，本平台无此能力。'
                          % pair_in.get('not_triggered_reason')})
        pairs.append({
            'pair_id': pair_id,
            'rule_id': rule.get('id'),
            'quote': rule.get('quote'),
            'status': status,
            'subject_gods': list(rule.get('subject_gods') or []),
            'disease_gods': list(rule.get('disease_gods') or []),
            'medicine_gods': list(rule.get('medicine_gods') or []),
            'subject': pair_in.get('subject'),
            'disease_candidate': disease,
            'medicine_candidate': medicine,
            'medicine_status': medicine_status,
            'medicine_effect_status': pair_in.get('medicine_effect_status'),
            'medicine_check': medicine_check,
            'medicine_class_stems': medicine_class_stems,
            'medicine_presence_scope': 'visible_stems_only',
            'yongshen_candidate': yongshen_candidate,
            'determination': None})
    gaps.append({'gap_id': 'severity_threshold_undefined',
                 'detail': '定义节「从重者论」的「重」无阈值：本体系不选定'
                           '唯一病神，只陈述示例对的存在性命中。'})
    gaps.append({'gap_id': 'officer_strength_pattern_not_covered',
                 'detail': '正官格节「惟官星太弱太旺，方为有病」口径与定义节'
                           '口径并存未统一，本体系不覆盖太弱太旺型之病。'})
    triggered = [p for p in pairs if p['status'] == 'triggered']
    if triggered:
        status = 'presented'
        parts = []
        for pair in triggered:
            if pair['yongshen_candidate']:
                parts.append('%s对药神候选 %s' % (
                    pair['pair_id'],
                    '、'.join('%s（%s）' % (g['stem'], g['ten_god'])
                              for g in pair['yongshen_candidate'])))
            else:
                parts.append('%s对病已触发、药不在盘' % pair['pair_id'])
        conclusion = '病药候选：%s；药去病效力恒未裁定。' % '；'.join(parts)
    else:
        status = 'no_triggered_pair'
        conclusion = None
    conditions = [
        _condition('pair_triggered',
                   '触发的病药对：%s' % (
                       '、'.join(p['pair_id'] for p in triggered) or '无'),
                   'satisfied' if triggered else 'not_satisfied'),
        _condition('medicine_effect',
                   '药去病效力恒未裁定（药存在不等于病已去）',
                   'cannot_judge'),
    ]
    limitations = [
        '只编码定义节示例二、示例三两对；示例一（土重）前提无操作定义、'
        '四病四药或缺阈值判据或是行运之药，均不在本体系范围。',
        '已登记未编码的病药对子（示例一土重对、正官格太弱太旺张力句）与'
        '病/药定义句只列于 registered_not_encoded_pairs / '
        'registered_definitions，不编码、不产药神候选；病药药神缺位候选类'
        '已批准（X5，2026-11-25）：触发而药不在盘时，药神类明记为缺口'
        '候选类，并给出该类所含之干（十神类→干的纯算术展开），不新立药神规则。',
        '存在性口径只计显干，不计藏干；药候选只陈述存在与药克病的结构关系，'
        '去病效力恒未裁定，不输出「药已去病」。',
        '本体系永不输出「无病」；未触发只记未触发。',
        '《滴天髓阐微》中和篇制衡：病药之论「仍乃失之偏」「总以中和为主」，'
        '病药说非通则，候选陈述须与此制衡同读。',
        '与调候、扶抑、格局用神并列，不合并为统一喜用结论。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'pairs': pairs, 'gaps': gaps,
            'registered_not_encoded_pairs': [
                dict(item) for item in BINGYAO_REGISTERED_NOT_ENCODED_PAIRS],
            'registered_definitions': [
                dict(item) for item in BINGYAO_REGISTERED_DEFINITIONS],
            'basis': {'bingyao_variant': BINGYAO_VARIANT,
                      'day_master': day_master,
                      'triggered_pairs': [p['pair_id'] for p in triggered]},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['medicine_effect_unadjudicated',
                            'severity_threshold_undefined']}


def _validate_broken_pattern_result(key, result, evidence):
    """破格输入契约（第三批集成）：只认唯一已审古典破格通道。

    伤官见官（任氏寅月真格成立的伤官格＋正官在场）。逐项核对：
    格键须为 ``shangguan``；rule_ids 须含 Ren D-1 规则；证据须含
    原成立身份 ``ren_yin_true_pattern`` 与破格证据
    ``shangguan_sees_officer_broken``；additive 结构化字段须在场且
    与证据一致（``broken_condition`` 为 ``shangguan_sees_officer``、
    ``broken_evidence_ids`` 含破格证据 id、
    ``original_state`` 为 ``established``、
    ``original_pattern`` 与本格 pattern 名一致）。任一项漂移即
    fail-closed：通道外、缺证据、缺字段的 broken 一律拒收。
    """
    if key != 'shangguan':
        _fail('pattern result broken outside the reviewed '
              'shangguan channel')
    rule_ids = result.get('rule_ids') or []
    if 'bazi.phase2.ren_yin_true_pattern' not in rule_ids:
        _fail('pattern result broken lacks the reviewed ren_yin rule')
    evidence_ids = {item['id'] for item in evidence}
    if not {'ren_yin_true_pattern',
            'shangguan_sees_officer_broken'} <= evidence_ids:
        _fail('pattern result broken lacks establishment or breaking '
              'evidence')
    if result.get('broken_condition') != 'shangguan_sees_officer':
        _fail('pattern result broken_condition drifted')
    broken_evidence_ids = result.get('broken_evidence_ids')
    if type(broken_evidence_ids) is not list \
            or any(type(item) is not str for item in broken_evidence_ids) \
            or 'shangguan_sees_officer_broken' not in broken_evidence_ids:
        _fail('pattern result broken_evidence_ids drifted')
    if result.get('original_state') != 'established':
        _fail('pattern result broken original_state drifted')
    if result.get('original_pattern') != result.get('pattern'):
        _fail('pattern result broken original_pattern drifted')


def evaluate_pattern_xiyong(pattern, *, pillars=None, day_master=None):
    """格局用神：消费格局引擎 evaluate_all 输出，只对有资格的格列依据。

    有资格 = state 为 established，或 state 为 candidate 且 rule_ids
    含 validated 候选规则。state 为 broken 的格按破格契约验收后记
    ineligible（原格局已破格，成立前提不再满足），永不进入 eligible、
    永不输出格局用神。任何格的 useful_god 恒为 None（密封树中
    全部格的用神未审），本函数只输出该确定结论与结构依据，不捏造用神。
    """
    base = {'system': 'pattern_yongshen', 'research_only': True,
            'public_enabled': False, 'ai_enabled': False}
    if pattern is None:
        return {**base, 'status': 'not_provided', 'conclusion': None,
                'eligible': [], 'ineligible': [], 'counts': {},
                'counts_by_state': {},
                'gaps': [], 'basis': None,
                'conditions': [_condition(
                    'pattern_input', '未传入已审格局输出', 'not_satisfied')],
                'limitations': ['未传入格局输出，本体系不补格局判断。'],
                'uncertainty': ['pattern_input_missing']}
    # 格局引擎的治理旗标键为 public / ai（非 public_enabled / ai_enabled），
    # 故此处不用 _check_statement，逐项核对 variant 与四项旗标。
    if not isinstance(pattern, dict):
        _fail('pattern statement must be an object')
    if pattern.get('variant') != PATTERN_ENGINE_VARIANT:
        _fail('pattern statement variant drifted')
    if pattern.get('research_only') is not True:
        _fail('pattern statement research_only drifted')
    if pattern.get('public') is not False:
        _fail('pattern statement public drifted')
    if pattern.get('ai') is not False:
        _fail('pattern statement ai drifted')
    pattern_day = pattern.get('day_stem')
    month_branch = pattern.get('month_branch')
    if day_master is not None and day_master != pattern_day:
        _fail('pattern statement disagrees on the day master')
    _validate_day_month(pattern_day, month_branch)
    # C1：v2 兼容性校验——子变体身份与 strength_overall 语义。
    # 三个子变体钉住格局结果所依据的已审块（结构候选 / 寅月真格 /
    # 禄刃路线）；strength_overall 在 v2 恒为 None（因素模块不计算
    # 整局强弱），任何非 None 值都是语义漂移，拒收。
    for sub_key in ('pattern_variant', 'ren_yin_determination_variant',
                    'luren_route_variant'):
        sub_value = pattern.get(sub_key)
        if type(sub_value) is not str or not sub_value:
            _fail('pattern statement %s drifted' % sub_key)
    if 'strength_overall' not in pattern \
            or pattern.get('strength_overall') is not None:
        _fail('pattern statement strength_overall drifted')
    results = pattern.get('results')
    if not isinstance(results, dict) or not results:
        _fail('pattern statement results malformed')
    normalized = None
    if pillars is not None:
        normalized = _normalize_pillars(pillars, pattern_day)
    # 引擎顶层结构事实（可选转述）：counts 与 earth_gate 只在输入携带时
    # 校验后转述，缺失记 None，不据缺失推断。
    engine_counts = pattern.get('counts')
    if engine_counts is not None:
        if not isinstance(engine_counts, dict) \
                or any(type(key) is not str or type(value) is not int
                       for key, value in engine_counts.items()) \
                or any(key not in ('candidate', 'established', 'broken',
                                   'conflict', 'not_judgeable')
                       for key in engine_counts) \
                or sum(engine_counts.values()) != len(results):
            _fail('pattern statement engine counts drifted')
    earth_gate = pattern.get('earth_gate')
    if earth_gate is not None and type(earth_gate) is not bool:
        _fail('pattern statement earth_gate drifted')
    counts_by_state = {}
    for result in results.values():
        if isinstance(result, dict):
            state_value = result.get('state')
            counts_by_state[state_value] = \
                counts_by_state.get(state_value, 0) + 1
    counts_by_state = {key: counts_by_state[key]
                       for key in sorted(counts_by_state)}
    eligible = []
    ineligible = []
    gaps = []
    for key, result in sorted(results.items()):
        if not isinstance(result, dict):
            _fail('pattern result must be an object')
        state = result.get('state')
        if state not in ('candidate', 'established', 'broken', 'conflict',
                         'not_judgeable'):
            _fail('pattern result state drifted')
        rule_ids = result.get('rule_ids') or []
        if not isinstance(rule_ids, list) \
                or any(type(item) is not str for item in rule_ids):
            _fail('pattern result rule_ids drifted')
        evidence_in = result.get('evidence') or []
        if not isinstance(evidence_in, list) \
                or any(not isinstance(item, dict)
                       or type(item.get('id')) is not str
                       for item in evidence_in):
            _fail('pattern result evidence drifted')
        evidence = [{'id': item['id'],
                     'detail': item.get('detail', '')}
                    for item in evidence_in]
        for item in evidence:
            if type(item['detail']) is not str:
                _fail('pattern result evidence detail drifted')
        result_limitations = result.get('limitations') or []
        if not isinstance(result_limitations, list) \
                or any(type(item) is not str for item in result_limitations):
            _fail('pattern result limitations drifted')
        # C1：逐格 v2 字段语义校验——每格自带变体、日主/月支与治理
        # 旗标须与顶层一致；broken_gaps 为 v2 新增字段（具名破格缺口
        # 表，只登记、永不输出 broken），须在场且为字符串列表。
        if result.get('variant') != PATTERN_ENGINE_VARIANT:
            _fail('pattern result variant drifted')
        if result.get('day_stem') != pattern_day \
                or result.get('month_branch') != month_branch:
            _fail('pattern result disagrees on day stem or month branch')
        if result.get('research_only') is not True \
                or result.get('public') is not False \
                or result.get('ai') is not False:
            _fail('pattern result governance flags drifted')
        broken_gaps = result.get('broken_gaps')
        if type(broken_gaps) is not list \
                or any(type(gap) is not str or not gap
                       for gap in broken_gaps):
            _fail('pattern result broken_gaps drifted')
        # 破格契约验收（第三批集成）：只认伤官见官一途，逐项核对破格
        # 条件、破格证据与原成立身份；通道外或字段漂移的 broken 拒收。
        if state == 'broken':
            _validate_broken_pattern_result(key, result, evidence)
        god = PATTERN_TEN_GODS.get(key)
        visible_positions = []
        if god is not None and normalized is not None:
            for row in normalized:
                if row['name'] == 'day':
                    continue
                if row['stem_ten_god'] == god:
                    visible_positions.append({
                        'stem': row['stem'], 'pillar': row['name'],
                        'ten_god': god, 'element': row['stem_element']})
        is_eligible = (state == 'established'
                       or (state == 'candidate'
                           and bool(set(rule_ids)
                                    & VALIDATED_CANDIDATE_RULE_IDS)))
        record = {
            'pattern_key': key,
            'pattern': result.get('pattern'),
            'state': state,
            'rule_ids': list(rule_ids),
            'evidence_ids': [item['id'] for item in evidence],
            'broken_gaps': list(broken_gaps),
        }
        if state == 'broken':
            # 破格依据与原成立身份随记录下游携带，任何环节不得丢弃。
            record.update({
                'broken_condition': result.get('broken_condition'),
                'broken_evidence_ids':
                    list(result.get('broken_evidence_ids')),
                'original_state': result.get('original_state'),
                'original_pattern': result.get('original_pattern'),
            })
        if is_eligible:
            god_relation = PATTERN_GOD_RELATIONS.get(god)
            day_element = stem_element(pattern_day)
            record.update({
                'pattern_god': god,
                'visible_positions': visible_positions,
                'useful_god': None,
                'useful_god_status': 'no_reviewed_yongshen_rule',
                'reason': ('该格已成立或有 validated 候选规则，但密封树中'
                           '全部格的 useful_god 恒未审（破格/成败/清浊/'
                           '用神未审）：本体系不输出格局用神，只列结构依据。'),
                'structure_basis': {
                    'pattern_god': god,
                    'god_relation_to_day_master': god_relation,
                    'god_element': (
                        _element_for_relation(day_element, god_relation)
                        if god_relation is not None else None),
                    'visible_count': len(visible_positions),
                    'month_pillar_present': any(
                        pos['pillar'] == 'month'
                        for pos in visible_positions),
                    'evidence': evidence,
                    'result_limitations': list(result_limitations),
                },
            })
            eligible.append(record)
        else:
            if state == 'established':
                reason = '已成立但无格神可列（非十神格），不输出用神。'
            elif state == 'candidate':
                reason = ('仅月藏结构观察，无 validated 候选规则：'
                          '无资格输出格局用神。')
            elif state == 'conflict':
                reason = '流派冲突未裁定（官杀去留/杂气换算未审）：不输出用神。'
            elif state == 'broken':
                reason = ('原格局已破格（伤官见官）：原为伤官格（任氏寅月'
                          '真格成立），正官在场破格，成立前提不再满足，'
                          '不输出格局用神。')
            else:
                reason = '无已审依据：不输出用神。'
            record.update({'reason': reason})
            ineligible.append(record)
    if not eligible:
        gaps.append({'gap_id': 'no_pattern_yields_yongshen',
                     'detail': '本盘无任何格可输出已审格局用神：有资格的格'
                               '亦因 useful_god 未审而无用神；无资格的格按'
                               '状态分别记原因。'})
    else:
        gaps.append({'gap_id': 'eligible_pattern_no_yongshen_rule',
                     'detail': '有资格的格（%s）均无已审用神规则：'
                               '格局用神的逐格规则开发方向已获批（X6），'
                               '具体规则待逐格证据审查后另行接入。'
                     % '、'.join(e['pattern'] for e in eligible)})
    if eligible:
        status = 'presented'
        conclusion = '格局用神：有资格的格 %s 均无已审用神规则，不输出用神；' \
            '结构依据见 eligible。' % '、'.join(
                e['pattern'] for e in eligible)
    else:
        status = 'no_eligible_pattern'
        conclusion = None
    conditions = [
        _condition('eligible_pattern_present',
                   '有资格的格：%s' % (
                       '、'.join(e['pattern'] for e in eligible) or '无'),
                   'satisfied' if eligible else 'not_satisfied'),
        _condition('yongshen_rule_reviewed',
                   '格局用神逐格规则已审', 'not_satisfied',
                   basis='X6：开发方向已批，具体逐格规则待证据审查；'
                         '密封树 useful_god 恒未审'),
    ]
    limitations = [
        '成立的唯一通道是任氏寅月真格；候选只认 validated 候选规则；'
        '观察级候选、冲突、未可判一律无资格。',
        '破格只经伤官见官一途输出（任氏寅月真格成立＋正官在场）；破格'
        '结果只作破格登记，永不计入成立、不输出格局用神；其余破格缺口'
        '只见各结果的 broken_gaps 具名表（登记，不立规则）。',
        '戊×巳 / 己×午土日主成格不可建（TJ-011.2），一律不作格局裁定。',
        '格神显干位置只是结构依据，不是用神结论；不得据格神反推用神。',
        '结构依据（structure_basis：格神五行与相对日主的关系、显干计数与'
        '月柱在场、证据全文、逐格 limitations）只陈述已审结构事实，不新立'
        '任何格局用神规则；逐格规则开发方向已批准（X6，2026-11-25），'
        '具体规则待逐格证据审查。',
        '格局变体 pin 为 v2（C1，2026-11-25）：live v2 输出已接通，逐项'
        '校验变体、输入结构、字段语义与兼容性；有资格只表示可列结构依据，'
        '不等于格局用神已经成立。',
    ]
    return {**base, 'status': status, 'conclusion': conclusion,
            'eligible': eligible, 'ineligible': ineligible,
            'counts': {'eligible': len(eligible),
                       'ineligible': len(ineligible),
                       'total': len(results)},
            'counts_by_state': counts_by_state,
            'yongshen_rule_development': {
                'status': 'approved_in_direction',
                'adjudication': 'X6 (2026-11-25)',
                'per_pattern_rules': 'pending_evidence_review',
                'useful_god': 'none_reviewed',
                'note': '格局用神逐格规则开发方向已批准；具体逐格规则仍需'
                        '证据审查，未审前 useful_god 恒为 None；有资格只表示'
                        '可列结构依据，不等于格局用神已经成立。'},
            'gaps': gaps,
            'basis': {'pattern_variant': PATTERN_ENGINE_VARIANT,
                      'day_stem': pattern_day,
                      'month_branch': month_branch,
                      'engine_counts': engine_counts,
                      'earth_gate': earth_gate,
                      'counts_by_state': counts_by_state,
                      'pattern_structure_variant':
                          pattern.get('pattern_variant'),
                      'ren_yin_determination_variant':
                          pattern.get('ren_yin_determination_variant'),
                      'luren_route_variant':
                          pattern.get('luren_route_variant'),
                      'strength_overall': pattern.get('strength_overall')},
            'conditions': conditions, 'limitations': limitations,
            'uncertainty': ['pattern_yongshen_rule_unreviewed']}


def _flow_year_ganzhi(target_year):
    if type(target_year) is not int or not 1900 <= target_year <= 2098:
        _fail('target_year must be an integer calendar year 1900..2098')
    ganzhi = CYCLE[(target_year - 4) % 60]
    return ganzhi


def evaluate_annual_xiyong(systems, target_year, *, day_master):
    """流年喜用：接入组合引擎契约已实现的 4 项，余 5 项保持 pending。

    ``systems`` 为四体系输出字典（键 fuyi / tiaohou / bingyao /
    pattern_yongshen，缺失的体系可为 None）。只报存在性对照与调用结构，
    不推演任何流年喜用。
    """
    if type(day_master) is not str or day_master not in STEMS:
        _fail('day_master must be one heavenly stem')
    if not isinstance(systems, dict):
        _fail('systems must be an object')
    flow_ganzhi = _flow_year_ganzhi(target_year)
    flow_stem = flow_ganzhi[0]
    flow_branch = flow_ganzhi[1]
    flow_ten_god = ten_god_for(day_master, flow_stem)

    tiaohou = systems.get('tiaohou')
    tiaohou_sequence = []
    if isinstance(tiaohou, dict):
        tiaohou_sequence = [c['stem'] for c in
                            (tiaohou.get('candidates') or [])]
    tiaohou_presence = (flow_stem in tiaohou_sequence
                        if tiaohou_sequence else None)
    if not isinstance(tiaohou, dict):
        tiaohou_note = '未传入原局调候输出，流年调候对照待原局调候传入后方可列举。'
    elif tiaohou.get('status') == 'not_judgeable':
        tiaohou_note = '原局调候无在场候选或条目未审定，流年调候对照无序列可比。'
    else:
        tiaohou_note = ('只报流年干是否在原局调候序列中这一存在性事实；'
                        '流年调候推演未获批，不据此取流年调候用神。')

    bingyao = systems.get('bingyao')
    pair_roles = []
    if isinstance(bingyao, dict):
        for pair in bingyao.get('pairs') or []:
            if flow_ten_god in (pair.get('subject_gods') or []):
                role = 'subject'
            elif flow_ten_god in (pair.get('disease_gods') or []):
                role = 'disease'
            elif flow_ten_god in (pair.get('medicine_gods') or []):
                role = 'medicine'
            else:
                role = 'none'
            pair_roles.append({
                'pair_id': pair.get('pair_id'), 'flow_stem_ten_god': flow_ten_god,
                'flow_ten_god_role_in_pair': role,
                'pair_status': pair.get('status'),
                'note': ('只报流年干十神在该病药对中的角色这一结构对照；'
                         '流年病药推演未获批，不据此断流年病药去留。')})

    fuyi = systems.get('fuyi')
    fuyi_candidates = []
    if isinstance(fuyi, dict) and isinstance(fuyi.get('modern'), dict):
        fuyi_candidates = [g['stem'] for g in
                           (fuyi['modern'].get('candidate_stems') or [])]
    fuyi_presence = (flow_stem in fuyi_candidates
                     if fuyi_candidates else None)

    pattern_sys = systems.get('pattern_yongshen')
    pattern_basis_stems = []
    if isinstance(pattern_sys, dict):
        for entry in pattern_sys.get('eligible') or []:
            pattern_basis_stems.extend(
                pos['stem'] for pos in entry.get('visible_positions') or [])
    pattern_presence = (flow_stem in pattern_basis_stems
                        if pattern_basis_stems else None)

    references = {
        'tiaohou': {
            'flow_stem': flow_stem,
            'flow_stem_in_natal_tiaohou_sequence': tiaohou_presence,
            'natal_tiaohou_sequence_stems': tiaohou_sequence,
            'note': tiaohou_note},
        'bingyao': {
            'pairs': pair_roles,
            'note': ('未传入原局病药输出，流年病药对照待原局病药传入后方可列举。'
                     if not isinstance(bingyao, dict) else
                     '只报角色对照，不推演流年病药。')},
        'fuyi': {
            'flow_stem': flow_stem,
            'flow_stem_in_natal_fuyi_modern_candidates': fuyi_presence,
            'natal_fuyi_modern_candidate_stems': fuyi_candidates,
            'existence_only': True,
            'note': ('只报流年干是否与原局扶抑现代候选干同字这一存在性事实；'
                     '流年扶抑推演未获批，不据此取流年扶抑用神。存在性不等于'
                     '作用效力（X7 已批准，2026-11-25）。')},
        'pattern_yongshen': {
            'flow_stem': flow_stem,
            'flow_stem_in_pattern_basis': pattern_presence,
            'pattern_basis_stems': sorted(set(pattern_basis_stems)),
            'existence_only': True,
            'note': ('只报流年干是否与有资格格局的结构依据干同字这一存在性事实；'
                     '流年格局用神推演未获批，不据此取流年格局用神。存在性不等于'
                     '作用效力（X7 已批准，2026-11-25）。')},
    }
    call_structure = {
        system: (systems.get(system) or {}).get('status')
                if isinstance(systems.get(system), dict) else 'not_provided'
        for system in ('fuyi', 'tiaohou', 'bingyao', 'pattern_yongshen')
    }
    return {
        'variant': ANNUAL_CONTRACT_VARIANT,
        'status': 'contract_only_pending_rules',
        'implemented': list(ANNUAL_IMPLEMENTED),
        'pending': list(ANNUAL_PENDING),
        'pending_detail': [dict(item) for item in ANNUAL_PENDING_DETAIL],
        'pending_reason': ('流年喜用完整推演待对应规则获批后接入；现阶段只列'
                           '数据契约与调用结构，不推演任何流年喜用。'),
        'flow_year': {
            'target_year': target_year, 'ganzhi': flow_ganzhi,
            'stem': flow_stem, 'branch': flow_branch,
            'stem_ten_god': flow_ten_god,
            'derivation': 'sexagenary_cycle_index',
            'derivation_note': ('年干支按六十甲子表 CYCLE[(year-4)%60] 推导；'
                                '立春交界与年内分界不在此推导范围。')},
        'flow_references': references,
        'rule_call_structure': call_structure,
        'derivation': None,
        'unified_verdict': None,
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
    }


def evaluate_xiyong(*, day_master, month_branch, pillars=None, strength=None,
                    tiaohou=None, bingyao=None, pattern=None, flow_year=None):
    """四体系喜用神并列计算（组合任务消费的入口）。

    ``strength`` / ``tiaohou`` / ``bingyao`` / ``pattern`` 分别为
    ``assess_strength`` / ``tiaohou_lookup`` / ``bingyao_lookup`` /
    ``evaluate_all`` 的输出字典（缺省为 None，即该体系未传入）。
    ``pillars`` 为四柱（可选；用于现代扶抑候选干与格局结构依据的显干核对）。
    ``flow_year`` 为公历目标年份（可选；传入时计算流年喜用契约）。
    返回 dict：``systems``（四体系）、``annual_xiyong``、
    ``unified_verdict``（恒 None，TJ-013.2 裁决 A）。
    """
    _validate_day_month(day_master, month_branch)
    normalized = None
    if pillars is not None:
        normalized = _normalize_pillars(pillars, day_master)
        if normalized[1]['branch'] != month_branch:
            _fail('month_branch disagrees with the month pillar branch')
    systems = {
        'fuyi': evaluate_fuyi(strength, pillars=pillars),
        'tiaohou': evaluate_tiaohou_xiyong(tiaohou, pillars=pillars),
        'bingyao': evaluate_bingyao_xiyong(bingyao, pillars=pillars),
        'pattern_yongshen': evaluate_pattern_xiyong(
            pattern, pillars=pillars, day_master=day_master),
    }
    # 输入一致性：各体系的日主/月支须与顶层一致，否则 fail-closed。
    for key, statement in (('strength', strength), ('tiaohou', tiaohou),
                           ('bingyao', bingyao)):
        if statement is None:
            continue
        stmt_day = statement.get('day_master')
        if stmt_day != day_master:
            _fail('%s statement disagrees on the day master' % key)
        if key in ('strength', 'tiaohou') \
                and statement.get('month_branch') != month_branch:
            _fail('%s statement disagrees on the month branch' % key)
    annual = (evaluate_annual_xiyong(systems, flow_year, day_master=day_master)
              if flow_year is not None else None)
    return {
        'variant': XIYONG_ENGINE_VARIANT,
        'day_master': day_master,
        'month_branch': month_branch,
        'pillars': [row['ganzhi'] for row in normalized]
                   if normalized is not None else None,
        'systems': systems,
        'annual_xiyong': annual,
        'unified_verdict': None,
        'unified_verdict_status': 'abstain_by_adjudication_TJ-013.2-A',
        'unified_verdict_note': ('TJ-013.2 裁决 A：四体系并列呈现、统一裁决拒判；'
                                 '本引擎永不输出统一喜用神。'),
        'research_only': True, 'public_enabled': False, 'ai_enabled': False,
        'limitations': list(GLOBAL_LIMITATIONS),
    }
