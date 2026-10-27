"""TJ-011.2 火线形态审定登记（设计裁定批：只登记，不实现）。

本批对象：火日主旺衰形态的「形态审定」——在 018-A 已登记的根表材料
（《三命通会》卷二两节校勘登记，ROOT_TABLE_ASSESSMENT = partial、丁长生
conflict 在案）之上，裁定五项设计问题并登记为结构化数据：

1. 丙×午强形态（F1）：新形态定义全文——同类当令的严格表述、通根要件
   （已登记根位逐项标注证据等级）、午中气己土的处置（不否决记录项，
   经「藏干层次」治理约定，**标注为 Variant 治理约定、非原文**）、
   克破排除条件、反例与弃判/冲突条件。
2. 帝旺缺位处置：午根位以十二宫推步登记为 framework_derived（推论级），
   不得表述为逐干明句；其功能由本气同类当令关系（commander 层已审事实）
   并行承担。
3. 火×子弱形态（F5）：孤立定义要件逐条对子月复核——定义四要件皆可
   满足，唯既有 isolated scope 的「月干即月本气」条件在子月构造性不可
   满足（五虎遁子月干恒为阳干，本气癸永不透月干）；两个替代条件均无
   原文锚点，裁定**不可建**，不硬凑。
4. 丁线：全部丁形态登记为 blocked_by_conflict（丁长生 conflict
   sanming-juan2.ding-changsheng 未裁定），本批不设计丁谓词。
5. Golden 命盘设计四例（正强命中 / 形态外对照 / 未知弃判 / 冲突呈现）：
   真实出生时刻、四柱由历法实算、逐条件核对表与期望由人工按形态定义
   逐条推导（设计文件 tests/golden_tj0112_fire_morphology.json）。

本模块是纯数据登记，**零计算逻辑、零函数**：不编写
bazi-strength-adjudication-v1 的任何新谓词，不改变既有三谓词的任何
条件与输出。形态定义的状态是 adjudicated_design_not_implemented，
实现属下一批。凡本批新立口径，一律在条目内标注 anchor_type：
original_text（原文锚点）/ governance_convention（Variant 治理约定，
非古籍明示）/ scope_construction（沿既有已审 scope 的构造方式）。
"""

MORPHOLOGY_REGISTER_ID = 'bazi-fire-morphology-adjudication-v1'

MORPHOLOGY_TASK = 'TJ-011.2'

MORPHOLOGY_SNAPSHOTS = {
'ditiansui_chanwei.txt': {
'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/ditiansui_chanwei.txt',
'sha256': '6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795',
'bytes': 368684,
'chars': 139538},
'sanming_tonghui.txt': {
'snapshot_path': 'data/quarantine/public_domain_snapshots/daizhigev20/sanming_tonghui.txt',
'sha256': '00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
'bytes': 1342659,
'chars': 461157}}

# 《滴天髓阐微》定义与根列举引文（Source bazi.source.ditiansui-spouse，
# 与既有三谓词同一 Source、同一快照）。引文逐字保留快照原字：该快照
# 此数段用半角逗号/分号，逐字保留、不改作全角；「奶之轻者也」之「奶」
# 为快照原字（义为根之轻者），保留原字并注记，不静默订正。
MORPHOLOGY_QUOTES = [
{'id': 'dt.guli_def',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '原注',
'role': 'weak_form_definition',
'quote': '日主孤立无气,无地人元,绝无一毫生扶之意,财官强甚,乃为真从也',
'locator': {'char_start': 96219, 'char_end': 96250},
'note': '从象章原注：孤立（弱侧）通述定义，不点名五行。'},
{'id': 'dt.congwang_def',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'strong_form_definition_co_anchor',
'quote': '从旺者,四柱皆比劫,无官杀之制,有印绶之生,旺之极者',
'locator': {'char_start': 96521, 'char_end': 96547},
'note': '从象章任氏曰：从旺定义。不含当令要件（木×亥分支只锚此条）；'
        '「无官杀之制」为克破排除的直接锚点。'},
{'id': 'dt.congqiang_def',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'strong_form_definition_primary_anchor',
'quote': '从强者,四柱印绶重重,比劫叠叠,日主又当令',
'locator': {'char_start': 96605, 'char_end': 96626},
'note': '从象章任氏曰：从强定义，含「日主又当令」要件——丙×午形态'
        '（当令在位）的主锚。'},
{'id': 'dt.congqiang_no_caiguan',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'strong_form_definition_primary_anchor',
'quote': '绝无一毫财星官杀之气',
'locator': {'char_start': 96627, 'char_end': 96637},
'note': '从强定义紧随句：财星与官杀显于四柱皆为否决项的直接锚点。'},
{'id': 'dt.root_heavy_light',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_grade_framework',
'quote': '长生禄旺,根之重者也;墓库余气,奶之轻者也',
'locator': {'char_start': 39967, 'char_end': 39988},
'note': '衰旺章根列举总述：根分重/轻两等——本批通根要件只取重根'
        '（长生/禄/帝旺位），轻根（墓/余气）只作根事实登记。'
        '「奶」为快照原字，义同「根」，保留不改。'},
{'id': 'dt.root_bijian_yuqi',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_grade_framework',
'quote': '天干得一比肩,不如地支得一余气墓库',
'locator': {'char_start': 39989, 'char_end': 40006},
'note': '根列举同段：轻根亦为根事实（存在性），但等级在重根之下。'},
{'id': 'dt.root_mu',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_position_listing_light',
'quote': '墓者,如甲乙逢未,丙丁逢戌,庚辛逢丑,壬癸辰之类是也',
'locator': {'char_start': 40007, 'char_end': 40033},
'note': '墓列：丙丁逢戌。快照「壬癸辰」脱「逢」字，原样保留。'},
{'id': 'dt.root_yuqi_1',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_position_listing_light',
'quote': '余气者,如丙丁逢未,丙丁逢戌,庚辛逢丑,壬癸逢辰之类是也',
'locator': {'char_start': 40034, 'char_end': 40062},
'note': '余气列复本一：丙丁逢未、丙丁逢戌——戌在此列入余气，'
        '与墓列冲突（见 registered conflict）。'},
{'id': 'dt.root_yuqi_2',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_position_listing_light',
'quote': '余气者,如丙丁逢未,甲乙逢辰,庚辛逢戌,壬癸逢丑之类是也',
'locator': {'char_start': 40063, 'char_end': 40091},
'note': '余气列复本二：丙丁逢未（与复本一一致）；未在两复本均为'
        '丙丁余气，无冲突。'},
{'id': 'dt.root_heavy_example',
'source_id': 'bazi.source.ditiansui-spouse',
'layer': '任氏曰',
'role': 'root_position_listing_heavy',
'quote': '得二比肩,不如支中得一长生禄旺,如甲乙逢亥寅卯之类是也',
'locator': {'char_start': 40092, 'char_end': 40119},
'note': '重根列举只举甲乙（木）一例——火的重根位不在本段列举内，'
        '丙位取自三命卷二逐干句（018-A 登记），分级见根位登记表。'}]

# 丙根位登记（本批裁定一/二）：根 = 支中藏有丙/丁（火）之支，逐位标注
# 证据等级。等级枚举（不得混用）：
# - per_stem_listed：逐干明句（三命卷二逐干铺陈，018-A 已校勘登记）；
# - framework_derived：十二宫推步（长生位明句 + 十二宫序框架节登记 +
#   阳干顺行推得），属推论级，**不是逐干明句**；
# - light_listed：滴天髓根列举的轻根列（墓/余气）明列；
# - light_listed_conflicted：轻根明列但列间异文冲突未裁定。
BING_ROOT_POSITIONS = [
{'branch': '寅', 'position_kind': '长生', 'grade': 'per_stem_listed',
 'is_heavy': True,
 'evidence': [
  {'quote_ref': 'sm2.bing_sheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '三命卷二逐干明句「丙火生于寅其理甚明」（char 39659–39668）'},
  {'quote_ref': 'sm2.bing_shengsi', 'register': 'bazi_sanming_juan2_collation',
   'note': '三命卷二「故丙火生于寅而死于酉」（char 39709–39719）'},
  {'quote_ref': 'sf.sisheng', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰五行级四生「火生在寅」互证（018-A CORROBORATION_FACTS '
           'bing-sheng-agreement 三方一致）'},
  {'quote_ref': 'sm2.renyuan_bing', 'register': 'bazi_sanming_juan2_collation',
   'note': '三命同书《论人元司事》「丙火长生五日」藏干司事旁证'}]},
{'branch': '巳', 'position_kind': '禄/临官', 'grade': 'per_stem_listed',
 'is_heavy': True,
 'evidence': [
  {'quote_ref': 'sm2.bing_lu', 'register': 'bazi_sanming_juan2_collation',
   'note': '三命卷二禄句「其禄在己巳为炉冶之火」（char 39568–39578，'
           '「己」经校勘记 sm2-ji-39571 读巳）'},
  {'quote_ref': 'sm2.summary_bracket', 'register': 'bazi_sanming_juan2_collation',
   'note': '同节论曰总结块「至巳临官归禄丙火得垣」（char 41895–42017）'},
  {'quote_ref': 'sf.lubiao', 'register': 'bazi_sanming_juan2_collation',
   'note': '神峰十干禄表「丙戊禄在巳」互证（018-A '
           'bing-lu-guan-agreement）'}]},
{'branch': '午', 'position_kind': '帝旺（推步）', 'grade': 'framework_derived',
 'is_heavy': True,
 'evidence': [
  {'derivation': '丙长生寅（逐干明句，sm2.bing_sheng）＋十二宫次序'
   '（三命卷二《论五行旺相休囚死并寄生十二宫》框架节登记：长生、沐浴、'
   '冠带、临官、帝旺、衰、病、死、墓、绝、胎、养）＋阳干顺行：寅→卯'
   '（沐浴）→辰（冠带）→巳（临官）→午（帝旺）',
   'note': '推步链每一环都有登记依据，但「丙帝旺在午」本身无任何逐干'
           '逐字句（018-A CORROBORATION_FACTS no-diwang-sentence：'
           '全书以帝旺句式检索 0 见）。本位等级恒为 framework_derived，'
           '任何引用不得表述为明句。'},
  {'carrier': 'principal_relation',
   'note': '功能承担：午本气丁与丙同属火，commander 层 principal 关系'
           '为 same_element（已审事实，独立于根表推步）——本形态的当令'
           '要件由该关系承担，帝旺推步只作根位登记，不单独作当令证据。'}]},
{'branch': '未', 'position_kind': '余气（轻根）', 'grade': 'light_listed',
 'is_heavy': False,
 'evidence': [
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'self',
   'note': '余气列复本一「丙丁逢未」（char 40034–40062）'},
  {'quote_ref': 'dt.root_yuqi_2', 'register': 'self',
   'note': '余气列复本二「丙丁逢未」（char 40063–40091）——两复本一致，'
           '无异文冲突'}]},
{'branch': '戌', 'position_kind': '墓/余气（轻根，异文冲突）',
 'grade': 'light_listed_conflicted',
 'is_heavy': False,
 'conflict_id': 'bazi.concept.conflict_root_type_readings',
 'evidence': [
  {'quote_ref': 'dt.root_mu', 'register': 'self',
   'note': '墓列「丙丁逢戌」（char 40007–40033）'},
  {'quote_ref': 'dt.root_yuqi_1', 'register': 'self',
   'note': '余气列复本一亦「丙丁逢戌」（char 40034–40062）——同支两列'
           '异文，冲突已登记为 conflict_root_type_readings（s026/s041），'
           '未裁定。根位在戌者携 type_source_conflict，按既有机制阻断'
           '裁决（见 Golden 冲突呈现例）。'}]}]

BING_HEAVY_ROOT_BRANCHES = ['寅', '巳', '午']

BING_ALL_ROOT_BRANCHES = ['寅', '巳', '午', '未', '戌']

# 帝旺缺位处置裁定（本批裁定二）：结论汇总（细节在根位登记表午条）。
DIWANG_DISPOSITION = {
 'question': '丙/丁帝旺位（午）无逐干逐字句，形态定义若需帝旺位如何处置',
 'verdict': 'substituted_by_framework_derivation_with_grade_disclosure',
 'statement': '午登记为丙的帝旺根位，等级 framework_derived（十二宫推步，'
              '推论级），与寅/巳的 per_stem_listed（逐干明句级）分级并列、'
              '永不混同；本形态的「当令」功能要件由 commander 层已审的'
              '本气同类关系（午本气丁与丙同火）承担，不由推步单独承担。'
              '任何后续引用若把午帝旺表述为原文逐干句，即属证据等级'
              '冒充，禁止。',
 'forbidden_phrasings': ['丙帝旺在午（原文）', '三命明言丙旺于午'],
 'assessment_ref': 'bazi_sanming_juan2_collation.ROOT_TABLE_ASSESSMENT'
                   '（verdict=partial，derived_positions 含帝旺，'
                   'blocking_items 含「帝旺位代偿口径未审定」——本批'
                   '即该审定）'}

# 治理约定登记：本批新立口径，**全部标注为 Variant 治理约定、非古籍
# 明示**。原文锚点只作支持语境，不构成对约定文本的逐字授权。
GOVERNANCE_CONVENTIONS = [
{'id': 'fire-morph.hidden-layer-root-facts-only',
 'label': '治理约定（非原文）',
 'statement': '本形态内，藏干只作根位事实进入裁定（根的存在与可用性），'
              '不独立产生生扶或克破效力：非生扶藏干不否决形态，生扶藏干'
              '亦不单独计作生扶条件成立。显干层（年/月/时干）承载定义的'
              '全部量化要求。',
 'supporting_context_not_mandate': [
  '从旺/从强定义以「四柱」量化（四柱皆比劫 / 四柱印绶重重、比劫叠叠），'
  '其量化对象是四柱之干（显干层）；定义文本未对藏干作量化要求。',
  '已审架构立场（与本约定同 Source 的已审段落与既有实现一致）：藏干'
  '效力从不与显干等同——既有因子层中藏干关系 effect_status 只及'
  'root_participation_only / unresolved，equivalent_to_visible 恒 False；'
  '「局部藏干只证明根存在/可用，不独立宣称所有藏干产生可量化作用」'
  '为 TJ-011.1 审计 C 节已审口径。'],
 'divergence_from_v1': '既有 pure 谓词的条件 all_positions_support_only'
  '覆盖显干与藏干全部关系；本形态的条件 '
  'visible_positions_support_only 只覆盖显干，藏干按本约定处理。两形态'
  '范围语义不同，本形态**不使用 pure_support 名称**（见形态定义 '
  'predicate_name_candidate），不得静默沿用 v1 名义。',
 'scope_limit': '本约定只适用于本形态（丙×午）；不回溯改写既有三谓词的'
                '任何条件，既有谓词的藏干口径不变。'},
{'id': 'fire-morph.ji-in-wu-non-veto',
 'label': '治理约定（非原文）',
 'statement': '午中气己（对丙为食神、泄气）在本形态内为**不否决记录项**：'
              '逐盘记录在案，不否决形态成立，亦不计作任何条件成立的依据。'
              '此为上条约定的直接实例（己是午的固定藏干构成，任何午月造'
              '必然含之；若作否决项，本形态构造性不可满足——与 pure 形态'
              '在午月的已证结论相同）。己一旦透出为显干，则按显干层规则'
              '处理（visible_positions_support_only 否决），不适用本条。',
 'anchor_status': '无定义层逐字锚点——本条是治理约定，登记于此并标注'
                  '非原文；支持语境同上条。'}]

# 丙×午强形态定义（本批裁定一）：设计登记，未实现。
FORM_BING_WU = {
 'form_id': 'bing-wu-commanding-visible-support-v1',
 'name_cn': '丙日主午月同类当令显纯生扶形态',
 'status': 'adjudicated_design_not_implemented',
 'task': 'TJ-011.2',
 'school': '任氏（滴天髓阐微）分支，与既有三谓词同一 Source',
 'day_master': '丙',
 'month_branch': '午',
 'classification_if_matched': 'strong',
 'never_yields': ['weak'],
 'predicate_name_candidate': 'commanding_visible_support',
 'predicate_name_note': '实现批拟用名；不得用 pure_support（其藏干范围'
                        '语义不同，见治理约定 divergence_from_v1）。',
 'definition_anchors': {
  'primary': ['dt.congqiang_def', 'dt.congqiang_no_caiguan'],
  'co_anchor': ['dt.congwang_def'],
  'anchoring_rationale': '本形态当令在位（午本气与丙同类），主锚取含'
   '「日主又当令」要件的从强定义；从旺定义为共锚（其「无官杀之制」为'
   '克破排除的直接文本）。两定义均为五行通述、不点名火，火分支在定义层'
   '与木分支同标准，不需要火专属定义段（审源已核：不存在点名火日主的'
   '同形态裁定段）。'},
 'same_element_commanding_statement': '同类当令的严格表述：月支本气之'
  '五行与日主之五行相同（commander 层 principal 关系 == same_element)，'
  '即为同类当令。本气干与日主是否同干不论——午本气为丁，与丙异干而'
  '同属火，仍为同类当令；「同气」在本登记中恒指同五行，不得读作同干。',
 'conditions': [
  {'key': 'fire_day_master_bing',
   'statement': '日主为丙。本形态不适用于丁（丁线整体阻断，见 '
                'DING_BLOCK），亦不适用于其余日主。',
   'anchor_type': 'scope_construction',
   'anchors': ['FORM scope', 'DING_BLOCK']},
  {'key': 'reviewed_same_element_command_month',
   'statement': '月支为午，本气（丁）已经审，principal 关系为 '
                'same_element（同类当令，表述见 '
                'same_element_commanding_statement）。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congqiang_def（日主又当令）',
               'commander 层 principal 关系已审事实（午本气丁）']},
  {'key': 'visible_positions_support_only',
   'statement': '年、月、时三显干对日主的关系全部属于生扶类'
                '（generates_me 印 / same_element 比劫）；任一显干为'
                '克泄耗类（controls_me 官杀 / i_control 财 / i_generate '
                '食伤）即否决。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congqiang_def（四柱印绶重重，比劫叠叠）',
               'dt.congqiang_no_caiguan（绝无一毫财星官杀之气）',
               'dt.congwang_def（四柱皆比劫，无官杀之制）']},
  {'key': 'visible_resource_present',
   'statement': '显干中至少一干为印（generates_me）。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（有印绶之生）',
               'dt.congqiang_def（印绶重重）']},
  {'key': 'visible_peer_present',
   'statement': '显干中至少一干为比劫（same_element）。日干本身不计'
                '（既有架构：日干是参照，不作独立显干）。',
   'anchor_type': 'original_text',
   'anchors': ['dt.congwang_def（四柱皆比劫）',
               'dt.congqiang_def（比劫叠叠）']},
  {'key': 'effective_heavy_day_roots',
   'statement': '日主结构根中至少一根落在重根位 {寅， 巳， 午}，且全部'
                '结构根（含轻根位未/戌之根）的可用性均为 effective'
                '（无未解支作用触及其柱、无根类型异文冲突）。重/轻之'
                '分见根列举总述；根位与等级见 BING_ROOT_POSITIONS。',
   'anchor_type': 'original_text',
   'anchors': ['dt.root_heavy_light（长生禄旺，根之重者也）',
               'BING_ROOT_POSITIONS（018-A 登记根位与等级）']},
  {'key': 'all_visible_have_reviewed_roots',
   'statement': '每个显干在其五行已审根位集合内至少有一个根位（根位='
                '盘中藏有该五行之干的支）：木用密封政策已审集合 '
                '{亥， 寅， 卯}；火用本登记 BING_ALL_ROOT_BRANCHES。',
   'anchor_type': 'scope_construction',
   'anchors': ['既有 pure scope 同名条件先例',
               'BING_ROOT_POSITIONS']},
  {'key': 'no_unresolved_interactions',
   'statement': '无未解干支作用类型（合/冲/害/三合与干合按既有口径）：'
                '任一未解作用在盘即弃判，与既有三谓词同口径。',
   'anchor_type': 'scope_construction',
   'anchors': ['TJ-011.1 既有口径（作用未解即弃判）']},
  {'key': 'hidden_layer_convention_applied',
   'statement': '藏干层按治理约定 fire-morph.hidden-layer-root-facts-only'
                '处理：藏干只作根位事实；非生扶藏干（含午中气己）记录'
                '在案、不否决，生扶藏干不单独计作生扶。此条为治理约定，'
                '非原文。',
   'anchor_type': 'governance_convention',
   'anchors': ['GOVERNANCE_CONVENTIONS: '
               'fire-morph.hidden-layer-root-facts-only',
               'GOVERNANCE_CONVENTIONS: fire-morph.ji-in-wu-non-veto']}],
 'control_break_exclusions': [
  {'target': '显干官杀（壬/癸，controls_me)',
   'disposition': '否决',
   'anchor': 'dt.congwang_def「无官杀之制」＋ dt.congqiang_no_caiguan'
             '「绝无一毫财星官杀之气」，直接原文锚点'},
  {'target': '显干财（庚/辛，i_control)',
   'disposition': '否决',
   'anchor': 'dt.congqiang_no_caiguan「绝无一毫财星官杀之气」，'
             '直接原文锚点'},
  {'target': '显干食伤（戊/己，i_generate)',
   'disposition': '否决',
   'anchor': '从强/从旺「四柱」量化（印绶重重、比劫叠叠 / 皆比劫）＋'
             '显干生扶 scope 构造——定义未逐字点名食伤显干，登记为'
             'scope_construction，不冒充逐字锚点'},
  {'target': '藏干克破（藏壬癸/庚辛/戊己于各支）',
   'disposition': '本形态不裁定（治理约定：藏干只作根位事实）；逐盘'
                  '记录，不否决亦不计效',
   'anchor': 'GOVERNANCE_CONVENTIONS '
             'fire-morph.hidden-layer-root-facts-only（非原文）'},
  {'target': '官杀通根月支等藏干层克破形态',
   'disposition': '不在本形态裁定范围（同上约定）',
   'anchor': '同上'}],
 'counterexamples': [
  '显干见财（辛）：形态外——见 Golden '
  'tj0112-fire-counter-visible-wealth 例（财星显干，从强定义直接否决）。',
  '显干见官杀（壬/癸）：从旺「无官杀之制」直接否决（定义层反例，'
  '无需命盘）。',
  '月支非午（丙日主他月）：不在本形态适用范围，形态不启动。',
  '丁日主午月：不适用本形态——丁线整体 blocked_by_conflict，'
  '不作任何裁定。'],
 'abstain_and_conflict_conditions': [
  '未解干支作用（合/冲/害/三合/干合）在盘 → 弃判（indeterminate），'
  '见 Golden tj0112-fire-abstain-clashed-root 例。',
  '根类型异文冲突（戌根墓/余气）在盘 → 冲突呈现并阻断裁决'
  '（indeterminate + conflict_checks），见 Golden '
  'tj0112-fire-conflict-xu-root-type 例。',
  '结构根可用性未达 effective（支作用未解触及其柱）→ 弃判。',
  '因子链不一致 / 派生重放不符（既有 blockers 体系）→ 弃判，'
  '与既有三谓词一体适用。'],
 'sufficiency_statement': '九条件全真且无 blockers 时，设计期望裁定为 '
  'strong（充分性依据：从强主锚＋从旺共锚的定义合取＋已登记根位＋已审'
  '本气关系，与既有三谓词的合取形态同构）。本批只登记设计期望，'
  '不产生任何运行时裁定；实现批须以真实命盘四类测试复证后方可发出。',
 'evidence_binding': 'registered_phase1_phase2（S5 治理批完成密封注册：'
                     'bazi.rule.r030 / '
                     'bazi.phase2.strength_commanding_visible_support；'
                     '裁决经该注册规则步发出）',
 'research_only': True,
 'public_enabled': False,
 'ai_enabled': False}

# F5 火×子弱形态逐条复核（本批裁定三）：结论不可建。
F5_ZI_WEAK_REVIEW = {
 'form_id': 'fire-zi-isolated-control-candidate',
 'name_cn': '火日主子月弱形态（isolated 型候选）',
 'verdict': 'not_buildable',
 'definition_ref': 'dt.guli_def（原注 char 96219）',
 'definition_requirements_review': [
  {'requirement': '日主孤立无气',
   'satisfiable_in_zi_month': True,
   'note': '结构事实：子月造可令日主无根、月不生扶（见下 scope 条件'
           '3/4 的可构造性）。'},
  {'requirement': '无地人元（支中无人元生扶）',
   'satisfiable_in_zi_month': True,
   'note': '子（癸）、丑（己癸辛）、申（庚壬戊）、酉（辛）四支藏干均'
           '无木火，可构造全支无人元生扶之造；辰（乙）、亥（甲）则'
           '不可用。'},
  {'requirement': '绝无一毫生扶之意（显藏皆无生扶）',
   'satisfiable_in_zi_month': True,
   'note': '显干避甲乙丙丁、支取上述集合即可满足——弱侧藏干条件在子月'
           '可构造（子为单气纯支，是其余条件可满足的关键）。'},
  {'requirement': '财官强甚',
   'satisfiable_in_zi_month': True,
   'note': '子本气癸为官（controls_me），本气关系已审——月令克身在'
           'principal 层可满足。惟「强甚」的操作化在既有 scope 中靠'
           '月干透出条件（见下条件 6），该条件正是不可满足处。'}],
 'scope_conditions_review': [
  {'key': 'fire_day_master', 'satisfiable': True,
   'note': '丙可建模（丁另受 DING_BLOCK 约束）。'},
  {'key': 'reviewed_control_month', 'satisfiable': True,
   'note': '子本气癸克火，relation=controls_me 已审；月份集合本身属'
           '已审 scope 登记事项（如 PURE_GENERATING_MONTHS 先例），'
           '非构造性障碍。'},
  {'key': 'day_has_no_structural_root', 'satisfiable': True,
   'note': '支避 {寅，巳，午，未，戌} 可构造。'},
  {'key': 'no_support_in_any_position', 'satisfiable': True,
   'note': '同定义要件 2/3。'},
  {'key': 'visible_earth_metal_only', 'satisfiable': True,
   'note': '子月干可为戊（乙/庚年组）或庚（丙/辛年组），显干土金-only'
           '在相应年组可构造。'},
  {'key': 'month_principal_exposed_with_root', 'satisfiable': False,
   'note': '**构造性不可满足**：条件要求月干 == 月本气（癸）。五虎遁'
           '下子月干恒为阳干 {甲，丙，戊，庚，壬}，永不为阴干癸'
           '（证明见 wuhudun_proof）。此为全形态唯一不可满足条件。'},
  {'key': 'no_unresolved_interactions', 'satisfiable': True,
   'note': '支组合可避合冲害三合。'}],
 'wuhudun_proof': {
  'statement': '五虎遁年上起月：甲/己年寅月丙、乙/庚年寅月戊、丙/辛年'
               '寅月庚、丁/壬年寅月壬、戊/癸年寅月甲；子月为寅后第十月，'
               '干序进十还原——子月干与寅月干同干：{丙，戊，庚，壬，甲}，'
               '全为阳干。子本气癸为阴干，故月干永不为癸，无一例外。',
  'zi_month_stems': ['甲', '丙', '戊', '庚', '壬'],
  'zi_principal_qi': '癸'},
 'candidate_alternatives_reviewed': [
  {'candidate': '改以「月干为克我之干且结构通根于月支」替代条件 6'
                '（壬子月可满足：壬克火、壬根在子，子在密封已审水根位'
                '表内）',
   'verdict': 'rejected_no_anchor',
   'reason': '孤立定义（dt.guli_def）只言「财官强甚」，无任何月干透出'
             '要求；同 Source 已审材料内亦无弱形态的月干替代 doctrine。'
             '采纳即凭治理约定新造一个弱裁定的充分条件——是实质新裁定，'
             '不是口径澄清，无原文锚点不得为之。'},
  {'candidate': '径删条件 6，其余六条合取即判弱',
   'verdict': 'rejected_widening',
   'reason': '删除已审 scope 的构成条件即扩大裁定范围，无锚点；且删后'
             '「财官强甚」无任何操作化承载，与定义的合取形态不符。'}],
 'anchor_search_record': '检索范围：孤立定义（96219)、衰旺章与从象章'
  '已审段落、s051 弱参照段（char 98058「日主休囚无根，惟官星当令…」'
  '为古例评注套语，TJ-011.1 审计明示仅参照、不作孤立判定主据）、根'
  '列举段。结论：无月干替代条件的 doctrine 锚点。子月本气克火是已审'
  '关系事实，但关系不单独证明弱（commander 层 scope 明示）。',
 'verdict_statement': 'F5 不可建：定义四要件与 scope 七条件中六条在子月'
  '皆可满足，唯「月干即月本气」构造性不可满足，且替代条件无原文锚点。'
  '按治理红线（找不到锚点宁可不可建、不得放宽），本形态登记为 '
  'not_buildable；将来若有新来源/新段落提供月干替代 doctrine 的锚点，'
  '可另行重审，本登记不预判。',
 'research_only': True}

# 丁线阻断登记（本批裁定四）。
DING_BLOCK = {
 'subject': '丁日主全部旺衰形态（F2 丁×午强及其余丁形态）',
 'status': 'blocked_by_conflict',
 'conflict_id': 'sanming-juan2.ding-changsheng',
 'conflict_register': 'bazi_sanming_juan2_collation.'
                      'DING_CHANGSHENG_CONFLICT',
 'statement': '丁长生位两说并列未裁定：酉（阴阳分判体例：三命逐干铺陈'
              '两见＋神峰楠曰个例）与寅（五行统摄体例：神峰五行级四生，'
              '丙丁共用）。丁的根位集合因长生位未定而不可视为齐备'
              '（丁禄午两说一致，不受影响，但禄一位不足以构成根表）。'
              '本批不设计任何丁谓词、不登记丁形态定义；丁形态在本 '
              'conflict 处置（用户裁定级流派取舍或长期并列分支登记）'
              '之前一律 blocked_by_conflict，不得以任一分支单独建模。',
 'ding_facts_not_in_dispute': ['丁禄午（两说一致，sm2.ding_lu / '
                               'sf.lubiao 互证）'],
 'research_only': True}

# F1–F7 处置总表（与火线审源 F 编号对齐）。
F_DISPOSITIONS = [
 {'id': 'F1', 'form': '丙 × 午月 强（同类当令型）',
  'status': 'adjudicated_design_not_implemented',
  'ref': 'FORM_BING_WU'},
 {'id': 'F2', 'form': '丁 × 午月 强',
  'status': 'blocked_by_conflict', 'ref': 'DING_BLOCK'},
 {'id': 'F3', 'form': '火 × 巳月 强（禄月型）',
  'status': 'not_adjudicated',
  'note': '巳为丙禄位（明句级），但「禄月」形态与既有 generating 形态'
          '名实不符（巳非印月），须另立形态审定；本批未审，维持未裁定，'
          '不得套用 generating 或本批 F1 形态（F1 月份要件为午）。'},
 {'id': 'F4', 'form': '火 × 寅月 强（印月/长生月型）',
  'status': 'deferred_not_adjudicated',
  'note': '形态与分日司令两重前置（寅藏戊破纯、司令属格局线事实层），'
          '排在 F1 之后；本批未审。'},
 {'id': 'F5', 'form': '火 × 子月 弱（isolated 型）',
  'status': 'not_buildable', 'ref': 'F5_ZI_WEAK_REVIEW'},
 {'id': 'F6', 'form': '衰极从弱型（任意月）',
  'status': 'not_buildable_no_definition',
  'note': '《滴天髓阐微》无从弱（衰极）定义段：全书「从弱」仅名目'
          '（31859）与古例套语（117621/118041)，不满足定义要件'
          '（火线审源 §2.1 已核），不可建。'},
 {'id': 'F7', 'form': '轻根参与型（未/戌根影响强弱边界）',
  'status': 'not_standalone',
  'note': '不独立成形态：未/戌轻根只作 F1 的根事实与阻断事实'
          '（戌根异文冲突）进入根位登记，不另立谓词。'}]

MORPHOLOGY_ADJUDICATION_NOTES = [
 'R1 形态与 v1 的关系：本批 F1 是新形态，不是 v1 pure 谓词的扩围——'
 '藏干范围语义不同（治理约定），谓词名不得共用 pure_support；与木×亥'
 '分支（pure_generating_support，只改月份条件、其余条件逐条复用 pure '
 '的同一计算事实）不同，F1 的条件集是独立合取，实现批不得声称与 '
 'pure 集「不可能分叉」。',
 'R2 帝旺分级：午根位等级 framework_derived 在登记、文档、后续实现的'
 '每一处引用中都必须随行标注；把推步表述为逐干明句即证据冒充。',
 'R3 己土处置的边界：己为不否决项仅限藏干层；己透干即按显干否决。'
 '本处置是治理约定（非原文），其依据是定义的「四柱」量化对象与已审'
 '藏干层次口径，不是任何一句原文说「己不否决」。',
 'R4 F5 的不可建是裁定结论，不是暂缓：六条可满足、一条构造性不可'
 '满足、替代无锚点，三项事实齐备后按红线关闭；重开须有新锚点证据。',
 'R5 丁线只登记阻断关系：DING_BLOCK 不含任何丁形态定义或条件，'
 '实现批不得从本登记推出丁谓词。',
 'R6 Golden 四例的期望是按本登记形态定义的人工推导（设计期望），'
 '不是实现输出；实现批须以同一批命盘复证，推导与输出不符时以定义'
 '为准并回改实现，不得改定义迁就输出。',
 'R7 本批零谓词代码：bazi_adjudication.py 与 bazi_action_conditions.py'
 '一字未动；密封测试另断言四例命盘在现行裁决下仍为 indeterminate，'
 '证明设计未夹带实现。',
 'R8 引文半角标点与「奶」字为快照原形，逐字保留；任何转写（含本文档）'
 '引用时须保留原形或显式标注为排版转写。']

MORPHOLOGY_LIMITATIONS = [
 '丙根表完整性仍为 partial（018-A 结论）：沐浴/冠带/衰/病/墓/绝/胎/养'
 '逐干位属推步，本形态只用长生/禄/帝旺三重根位，其中帝旺为推步级。',
 '藏干克破不裁定是本形态的明示范围限制：藏官杀/藏财在盘时本形态仍'
 '可判强（若其余条件全真），该限制随形态定义一并交付，实现与展示'
 '不得隐去。',
 'F3/F4 未审定；F5 不可建；F6 无定义不可建；丁线阻断——火日主可裁定'
 '范围在本批后仍只有「丙×午强」一个设计（且未实现）。',
 '密封 Phase1/Phase2 规则注册仍 pending（形态实现的 evidence_binding'
 '同既有口径披露），本批不处理注册。',
 '本批不改变 Slice D 未解锁条件：一般旺衰/有效作用仍未建成，格局线'
 '消费旺衰的范围不因本设计登记而扩大。']
