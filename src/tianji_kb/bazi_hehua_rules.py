"""合化（天干五合化气）成立规则登记（TJ-0426 Lane 2，P-05）。

纯登记模块：只转录已审定的合化材料，不产生任何化气成立／从化／
化格判定，不接线、不被任何可执行路径 import（与审定批
``bazi_hehua_fact_adjudication`` 同例：登记不等于实现）。

来源链（逐项可核）：
- 三命卷二合化组三节校勘续册（018-C）：四种条件表述登记为
  conflict 并列（``HEHUA_CONDITION_VARIANTS``，status=conflict，
  adjudication=None）；逐对月条件全表见 ``HEHUA_PAIRS``。
- TJ-012.3 合化审源与事实层设计审定登记
  （``bazi_hehua_fact_adjudication``，E0270）：四表述、条件要素
  矩阵、真冲突 C1–C4（C5 为未登记章内张力）、逐项可执行性判定
  P1–P18、切片结论 SLICE_SPEC=None、阻塞与待裁定登记 B1–B6。
  本模块逐项转录上述登记，转录漂移由专项测试核对。
- 五合名册：协纪 s010 短引「甲与己合乙与庚合丙与辛合丁与壬合
  戊与癸合」（Canonical 锚点）；名册化元素与 018-C 两节正文＋
  逐月表行名册＋执行表三面一致（审定批 P1）。

硬边界（审定批原文口径）：
- ``HEHUA_ESTABLISHMENT_STATUS`` 恒为 ``'unresolved'``；
  ``ESTABLISHMENT_RULES`` 为空——化气成立判定是裁定层：四表述
  采用属用户级流派裁定（P-D1，待裁定项 B1），本批不代裁；
  ``transformation_status`` 恒 unresolved（审定批 P16/P17）。
- 本模块唯一可执行的计算是表述中立的原始转写
  （``raw_transcription``：月支值、各干在场柱位与计数、辰在场、
  干合对在场）：这是 SLICE_DECISION 回退形态允许的唯一先行治理
  形态，不得含任何表述的月集／阻字集／状态归一化。
- 审定批 L7：(b) 层「在场可算」的命题（P3/P6/P7/P9/P10/P11）只
  陈述柱面转写的可计算性，不授权任何模块现在就输出这些要素为
  「条件事实」——在 P-D1 裁定前输出它们会造成已选边的外观。故
  本模块不输出 F1 月集归属、妬合／妬化字在场、有二计数、受气临
  官／喜时在场、旺气、根气等要素事实；只输出原始转写与恒 unresolved
  的成立结论。``hehua_establishment`` 对任何输入恒返回 unresolved。
- 滴天髓《化象》章（F5/F6）未登记：只有审计条目 P05，章内原文未
  逐节登记（缺口 B4）；本模块只登记其条件结构概要，不作引文消费。
- 司令不是任何已登记表述的条件要素（P14）：分日司令扩月与合化线
  无依赖；不得以司令未扩月为由阻塞合化登记。
- r005 红线：命中五合不等于化气成立；不得据五合直接输出感情适配、
  吉凶或关系评分（P18）。

治理：research_only=True、public=False、ai=False。本模块只依赖
纯常量模块 ``foundations``，不 import 历法 provider 与密封数据。
"""

from .foundations import BRANCHES, STEMS

HEHUA_RULES_VARIANT = 'bazi-hehua-rules-v1'
HEHUA_ADJUDICATION_REGISTER = 'bazi-hehua-fact-adjudication-v1'
HEHUA_CONDITION_REGISTER = (
    'bazi_sanming_juan2_hehua_collation.HEHUA_CONDITION_VARIANTS')

# 化气成立状态：恒未裁定（审定批 P16，待裁定 P-D1／B1）。
HEHUA_ESTABLISHMENT_STATUS = 'unresolved'
# 化气成立规则：无（四表述并存且真冲突四项，018-C 登记 conflict）。
ESTABLISHMENT_RULES = ()


# --- F1 逐对月条件全表 --------------------------------------------------
# 转录自 bazi_hehua_fact_adjudication.PAIR_CONDITION_TABLE（与 018-C
# 登记逐项对应）。``element`` 为名册化元素（表字段，不判断化成）；
# ``primary_months``／``secondary_months`` 为 F1 本局月集／其次一月
# （月支）；``blocker_stem_f1``／``blocker_stem_f3_duhua`` 为同一功能
# 槽位的两说触发字（C2 真冲突：三对不同，不得同时充当「阻字」）；
# 戊癸本局月集另有未审记号（``primary_unresolved_token``）。
HEHUA_PAIRS = (
    {'pair': '甲己', 'stems': ('甲', '己'), 'element': '土',
     'primary_months': ('辰', '戌', '丑', '未'),
     'secondary_months': ('午',),
     'blocker_stem_f1': '戊', 'blocker_phrasing': '有戊字间之',
     'blocker_stem_f3_duhua': '乙',
     'extras': ('受气临官：柱有巳亥（smhq.jiaji_cond）',
                '喜时：戊辰时（smhq.jiaji_xi）'),
     'condition_quote': 'smhq.jiaji_cond'},
    {'pair': '乙庚', 'stems': ('乙', '庚'), 'element': '金',
     'primary_months': ('巳', '酉', '丑'),
     'secondary_months': ('申',),
     'blocker_stem_f1': '甲', 'blocker_phrasing': '有甲字间之',
     'blocker_stem_f3_duhua': '辛',
     'extras': (),
     'condition_quote': 'smhq.yigeng_cond'},
    {'pair': '丙辛', 'stems': ('丙', '辛'), 'element': '水',
     'primary_months': ('申', '子', '辰'),
     'secondary_months': ('亥',),
     'blocker_stem_f1': '丁', 'blocker_phrasing': '柱有丁字',
     'blocker_stem_f3_duhua': '丁',
     'extras': (),
     'condition_quote': 'smhq.bingxin_cond'},
    {'pair': '丁壬', 'stems': ('丁', '壬'), 'element': '木',
     'primary_months': ('亥', '卯', '未'),
     'secondary_months': ('寅',),
     'blocker_stem_f1': '丙', 'blocker_phrasing': '柱有丙字',
     'blocker_stem_f3_duhua': '丙',
     'extras': (),
     'condition_quote': 'smhq.dingren_cond'},
    {'pair': '戊癸', 'stems': ('戊', '癸'), 'element': '火',
     'primary_as_transmitted': '丙午戌',
     'primary_months': ('午', '戌'),
     'primary_unresolved_token': '丙',
     'secondary_months': ('巳',),
     'blocker_stem_f1': '己', 'blocker_phrasing': '柱有己字',
     'blocker_stem_f3_duhua': '壬',
     'extras': ('受气临官：寅午戌生人见丁巳（smhq.wugui_cond）',),
     'condition_quote': 'smhq.wugui_cond'},
)
_HEHUA_PAIR_BY_STEMS = {
    frozenset(pair['stems']): pair for pair in HEHUA_PAIRS}


# --- 条件表述登记 -------------------------------------------------------
# 转录自 bazi_hehua_fact_adjudication.FORMULATION_REGISTER。F1–F4 已
# 登记（018-C，conflict 并列，adjudication=None）；F5/F6 未登记
# （只有审计条目 P05，缺口 B4）；HX 为相关 doctrine（对象是日主从化，
# 与化气格不是同一裁定对象）。
HEHUA_FORMULATIONS = (
    {'id': 'F1', 'name': '逐对月条件（prose-month-conditions）',
     'registered': True,
     'register_ref': 'bazi_sanming_juan2_hehua_collation.'
                     'HEHUA_CONDITION_VARIANTS.branches'
                     '[prose-month-conditions]',
     'source_id': 'bazi.source.sanmingtonghui',
     'text_layer': '正文（《论十干化气》逐对条件句）',
     'school_attribution': '三命通会体系',
     'condition_structure': '每对：本局月集（非…月不化）＋其次一月'
                            '（亦化）＋妬合字（间之/柱有则不化）；甲己、戊癸另有受气'
                            '临官附加项，甲己另有喜时附加项',
     'evidence_quotes': ('smhq.jiaji_cond', 'smhq.yigeng_cond',
                         'smhq.bingxin_cond', 'smhq.dingren_cond',
                         'smhq.wugui_cond', 'smhq.jiaji_xi'),
     'status': 'conflict_branch_unadjudicated'},
    {'id': 'F2', 'name': '旺气通则（general-wangqi-condition）',
     'registered': True,
     'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
                     '[general-wangqi-condition]',
     'source_id': 'bazi.source.sanmingtonghui',
     'text_layer': '正文（《论十干化气》「大凡」通则句）',
     'school_attribution': '三命通会体系',
     'condition_structure': '只取日干；配合之神年月时皆可用；日辰得'
                            '月中旺气为上、只时上旺气亦可、月时俱得为全吉、得月中旺'
                            '气而时上不乗旺气则不可用。不逐对列月',
     'evidence_quotes': ('smhq.dafan',),
     'status': 'conflict_branch_unadjudicated'},
    {'id': 'F3', 'name': '有二则化与妬化（erzehua-and-duhua）',
     'registered': True,
     'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
                     '[erzehua-and-duhua]',
     'source_id': 'bazi.source.sanmingtonghui',
     'text_layer': '正文（《论十干化气》「又曰」与妬化说）',
     'school_attribution': '三命通会体系',
     'condition_structure': '有二则化、一不能化仍还本位（原文只见於'
                            '甲己句）；妬化：第三干见合分恋，逐对给触发字',
     'evidence_quotes': ('smhq.erzehua', 'smhq.duhua'),
     'status': 'conflict_branch_unadjudicated'},
    {'id': 'F4', 'name': '逐月横看表（monthly-table-states）',
     'registered': True,
     'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
                     '[monthly-table-states] + HENGKAN_TABLE_INTEGRITY',
     'source_id': 'bazi.source.sanmingtonghui',
     'text_layer': '正文表格（《逐月横看理化之象》）',
     'school_attribution': '三命通会体系',
     'condition_structure': '逐对逐月给状态词（化X/不化/其他状态词）；'
                            '化月集合与 F1 系统性不一致；有化他元素之格；状态词未归一化',
     'evidence_quotes': ('smhk.header_dingren', 'smhk.wugui_row_b3',
                         'smhk.jiaji_row_b3', 'smhk.chenxu_row_b4'),
     'status': 'conflict_branch_unadjudicated'},
    {'id': 'F5', 'name': '滴天髓化象原注真化条件',
     'registered': False,
     'register_ref': 'docs/product/BAZI_PATTERN_AUDIT.md P05（审计'
                     '条目）；章界机上实测 [98297, 99943)',
     'source_id': 'bazi.source.ditiansui-spouse',
     'text_layer': '原注（《滴天髓阐微》十三、化象）',
     'school_attribution': '滴天髓原注层',
     'condition_structure': '逐对季节月（甲己四季、丙辛冬、戊癸夏、'
                            '乙庚秋、丁壬春）；独自相合（单遇一位）；甲己例：月时上'
                            '合、有一辰字、得龙以运之；真化/假化之分',
     'evidence_quotes': (),
     'status': 'audit_entry_only_not_registered',
     'note': '条件结构概要据审计条目与本批章界实测著录，不作引文'
             '消费；登记前不得据此设计任何事实或判定（缺口 B4）。'},
    {'id': 'F6', 'name': '滴天髓化象任氏曰（合则化/逢五而化）',
     'registered': False,
     'register_ref': '同 F5（任氏曰层，未登记）',
     'source_id': 'bazi.source.ditiansui-spouse',
     'text_layer': '任氏曰（《滴天髓阐微》十三、化象）',
     'school_attribution': '滴天髓任氏层',
     'condition_structure': '合则化之源说（数合之义）；化必得五土'
                            '（辰）而后成、逢五而化，与世传逢龙而化并存讨论',
     'evidence_quotes': (),
     'status': 'audit_entry_only_not_registered',
     'note': '与 F5 的逢龙说在同章内并存（龙=辰字在场 vs 五=五辰之'
             '位），是章内教义张力；未登记，只记结构。'},
    {'id': 'HX', 'name': '三命卷六化象（从化象 doctrine）',
     'registered': True,
     'register_ref': 'bazi_sanming_juan6_fangju_baxiang_collation'
                     '（sanming.juan6.huaxiang）',
     'source_id': 'bazi.source.sanmingtonghui',
     'text_layer': '正文（含引述：通玄论、玄虚道人、荆山居士）',
     'school_attribution': '三命通会体系',
     'condition_structure': '对象是日主从化：旺者从（乙旺庚从、庚旺'
                            '乙从）、日主无气、化有气方可用；类/属/从/化四分，类属要'
                            '身旺而从化要衰',
     'evidence_quotes': ('hx.definition', 'hx.tongxuan', 'hx.example',
                         'hx.jingshan'),
     'status': 'registered_related_doctrine_not_hehua_condition',
     'note': '与 F1–F4 不是同一裁定对象：化气格问「合而化否」，化象'
             '问「日主从化否」。共享干合在场事实，条件面（无气/有气、'
             '身旺/要衰）属从格与旺衰层。本批只登记其相关性与划界。'},
)


# --- 冲突结构 -----------------------------------------------------------
# 转录自 bazi_hehua_fact_adjudication.CONFLICT_ANALYSIS。C1–C4 为已登记
# 表述间的真冲突；C5 为未登记的章内张力（不计入四项，只作结构登记）。
HEHUA_CONFLICTS = (
    {'id': 'C1', 'title': 'F1 月集 vs F4 化月集合（同要素、不同集合）',
     'element': 'month_condition',
     'kind': 'same_element_different_threshold',
     'registered': True,
     'detail': '018-C 已逐月计算（HEHUA_CONDITION_VARIANTS 的 divergence 在案；'
               '月序为表列正月至十二月）：甲己——F1 要求 {三、五、六、九、十二月}，'
               '其中三、五、六月在 F4 为暗秀/不化/不化，F4 化月 {七、九、十一、十二} '
               '中七、十一月 F1 未要求；乙庚——F1 要求 {四、七、八、十二}，四、八月在 '
               'F4 为金秀/进秀（未作化金），F4 化月含一、二月（F1 未要求）；丙辛——F1 '
               '要求 {三、七、十、十一}，七、十一月在 F4 为进秀学堂/化秀（未作化水）；'
               '丁壬——F1 要求月 F4 全数作化木，但 F4 另多七、十一两化月；戊癸——F1 '
               '要求 {四、五、九}，五月在 F4 为不化，F4 化火月 {一、二、三、四、九、十二} '
               '中一、二、三、十二月 F1 未要求。五对全部分歧，非个别月份出入。'},
    {'id': 'C2', 'title': 'F1 妬合字 vs F3 妬化字（同功能槽位、不同触发字）',
     'element': 'third_stem_blocker',
     'kind': 'same_slot_different_trigger',
     'registered': True,
     'detail': '五对中三对不同：甲己 F1 戊/F3 乙；乙庚 F1 甲/F3 辛；戊癸 F1 己/F3 壬；'
               '两对相同：丙辛同为丁、丁壬同为丙。两说同在《论十干化气》一节之内、功能槽位'
               '相同（第三干出现则不化），触发字却对三对不一致——无论读作同一机制的两种传述，'
               '还是妬合（间之分位）与妬化（自恋其生）两个机制，编码时都不能同时充当「阻字」'
               '而不作选择。'},
    {'id': 'C3', 'title': 'F1 列举月集 vs F2 旺气架构（条件架构不同）',
     'element': 'month_condition / wangqi',
     'kind': 'different_condition_architecture',
     'registered': True,
     'detail': 'F1 以固定月集为充分面（生於本局月即满足月条件），F2 不列月集、以日辰实际得旺气'
               '为准（月中/时上）。月支在F1 集内而日辰不得旺气、或月支不在集内而日辰得旺气（经'
               '时上）两种情形下两说结论相反。这是架构级分歧，不是同一判据的详略。'},
    {'id': 'C4', 'title': 'F4 化他元素 vs 名册化元素（结果层冲突）',
     'element': 'result_element',
     'kind': 'different_result',
     'registered': True,
     'detail': 'F4 表内丁壬化火（四、五、九月位）、乙庚化木（十、十一月位）、甲己化木（十月位）、'
               '戊癸化水/为水（七、十、十一月位）——同一干对在表中可化出名册外元素，与 F1/F2/'
               'F3/F5/F6 及名册本身（丁壬木、乙庚金、甲己土、戊癸火）在结果层冲突。'},
    {'id': 'C5', 'title': 'F5 逢龙而化 vs F6 逢五而化（未登记、章内张力）',
     'element': 'chen_factor',
     'kind': 'intra_chapter_doctrinal_tension_unregistered',
     'registered': False,
     'detail': '同在滴天髓化象章：原注与世传以辰（龙）在场为化之助（得龙以运之），任氏曰别立'
               '「化必得五土而后成、逢五而化」并谓「近世……只知逢龙而化，不知逢五而化」。两说指向'
               '不同事实（辰支在场 vs 干序第五位逢辰干支），未登记、只记结构；其裁定以 B4 登记为前提。'},
)

# 详略差（非冲突）：D1–D5，转录自同一冲突结构分析。
HEHUA_DETAIL_DIFFERENCES = (
    {'id': 'D1', 'title': 'F3 有二则化只见於甲己句',
     'detail': '他对无对应陈述，是缺席而非矛盾；把「有二」推广为五对通则是一个解释步，'
               '未经登记，本批不作推广。'},
    {'id': 'D2', 'title': 'F1 受气临官/喜时是逐对附加项',
     'detail': '只见於甲己（巳亥、戊辰时）与戊癸（丁巳），他对与他表述无对应项；是该对条件面'
               '的加细，不与任何表述冲突。'},
    {'id': 'D3', 'title': 'F2 要旺 vs HX 要衰：对象不同、非冲突',
     'detail': 'F2 论化气格（日干与合神化出之神宜旺），HX 论从化象（日主宜无气而从化神）。'
               '裁定对象不同，极性相反不构成同对象冲突；但两层共享干合在场事实，下游不得把任一'
               '极性错接到另一对象。'},
    {'id': 'D4', 'title': 'F5 独自相合 vs F3 有二则化：方向相反但书别不同',
     'detail': 'F5（滴天髓原注，未登记）要独合，F3（三命，又曰）言有二则化——跨书、跨登记状态，'
               '只登记为流派差候选，不与 C1–C4 同级列为已登记真冲突。'},
    {'id': 'D5', 'title': 'F1 妬合措辞「间之」与「柱有」并存',
     'detail': '甲己/乙庚作「有X字间之」，丙辛/丁壬/戊癸作「柱有X字」——同表述内的措辞差：'
               '「间之」可读作在场、亦可读作居间（位于两合干之间）。这是表述内部的解析未定（见 P6），'
               '不是表述间冲突。'},
)


# --- 逐项可执行性判定 -----------------------------------------------------
# 转录自 bazi_hehua_fact_adjudication.PROPOSITION_AUDIT（P1–P18）。
# ``verdict`` 取值：fact_ready（已执行）／fact_ready_as_presence_only
# （在场可算、效力不可算）／adjudication_required（须裁定）／
# blocked_by_unresolved_token（未审记号阻断）／
# blocked_by_formulation_conflict（表述冲突阻断）／
# blocked_by_missing_layers（缺定义层）／registered_absence（登记性缺位）／
# consumer_not_unlocked（消费面未解锁）／prohibited（永禁）。
HEHUA_PROPOSITIONS = (
    {'id': 'P1', 'proposition': '五合名册与化元素对应（甲己土/乙庚金/丙辛水/丁壬木/戊癸火）',
     'verdict': 'fact_ready'},
    {'id': 'P2', 'proposition': '干合对在场事实（任意柱对）',
     'verdict': 'fact_ready'},
    {'id': 'P3', 'proposition': '日干合对在场（化气 doctrine 的对象面）',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P4', 'proposition': 'F1 月集归属（月支 ∈ 本局月/其次月）',
     'verdict': 'adjudication_required'},
    {'id': 'P5', 'proposition': '戊癸 F1 本局月集的完整形态',
     'verdict': 'blocked_by_unresolved_token'},
    {'id': 'P6', 'proposition': 'F1 妬合字在场',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P7', 'proposition': 'F3 妬化字在场',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P8', 'proposition': '阻字效力（妬合/妬化出现 ⇒ 不化）',
     'verdict': 'blocked_by_formulation_conflict'},
    {'id': 'P9', 'proposition': '有二的事实面（合神/日干重见）',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P10', 'proposition': 'F1 附加项在场（受气临官/喜时）',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P11', 'proposition': '辰在场（F5/F6 的辰/龙/五事实面）',
     'verdict': 'fact_ready_as_presence_only'},
    {'id': 'P12', 'proposition': '旺气（日辰得月中/时上旺气）',
     'verdict': 'blocked_by_missing_layers'},
    {'id': 'P13', 'proposition': '根气/有气（日主无气、化有气）',
     'verdict': 'blocked_by_missing_layers'},
    {'id': 'P14', 'proposition': '司令作为合化条件要素',
     'verdict': 'registered_absence'},
    {'id': 'P15', 'proposition': '从化象成立（日主从化、化象格）',
     'verdict': 'blocked_by_missing_layers'},
    {'id': 'P16', 'proposition': '化气成立判定（按任一已登记表述）',
     'verdict': 'adjudication_required'},
    {'id': 'P17', 'proposition': '消费面现状（transformation_status 与格局未决项）',
     'verdict': 'consumer_not_unlocked'},
    {'id': 'P18', 'proposition': '任何由合化推出的吉凶/贵贱/成败结论',
     'verdict': 'prohibited'},
)


# --- 阻塞与待裁定登记 -----------------------------------------------------
# 转录自 bazi_hehua_fact_adjudication.PENDING_ITEMS（B1–B6）。
HEHUA_PENDING_ITEMS = (
    {'id': 'B1',
     'item': '化气成立条件表述的采用（F1/F2/F3/F4 取舍与组合，含 C2 阻字字集、'
             'C1 月集与 F4 孰从、F4 状态词归一化读法）',
     'blocked_by': 'formulation_conflict（018-C 登记 conflict、真冲突四项 C1–C4）',
     'unlock': '用户级流派裁定后，另批按裁定实现化气判定',
     'needs_user_adjudication': True,
     'pending_decision_id': 'P-D1',
     'note': '本批未呈请具体裁定文本：呈请时应附四表述对同一组真实命盘的结论对照'
             '（本登记的矩阵与冲突分析即其材料基础）。裁定前 transformation_status 保持 unresolved'},
    {'id': 'B2',
     'item': '戊癸条件「丙」字解析（及同型表述内解析未定项，如 F1「间之」的居间读法）',
     'blocked_by': 'unresolved_token / unresolved_parse（018-C 在案）',
     'unlock': '他本互校与解析审定批（证据工程）；若终须取舍，升级为 P-D1 子项',
     'needs_user_adjudication': False},
    {'id': 'B3',
     'item': '旺气与根气/有气可执行定义（F2 与 HX 的核心要素）',
     'blocked_by': 'missing_layers：一般旺衰无已审定义、根层只有 participation 级事实'
                   '（TJ-011.2 线现状）',
     'unlock': '随 TJ-011.2 一般旺衰线与根层审定推进；与合化线无先后依赖',
     'needs_user_adjudication': False},
    {'id': 'B4',
     'item': '滴天髓《化象》章登记（F5/F6 的证据化）',
     'blocked_by': 'registration_gap：只有审计条目 P05，章内原文（原注＋任氏曰）未逐节登记',
     'unlock': '018 式逐节登记批（章界已实测 [98297, 99943)，PUA 工程负担未测、登记时实测）；'
               '登记后 F5/F6 才可作引文消费并重审 C5',
     'needs_user_adjudication': False},
    {'id': 'B5',
     'item': '从化象 doctrine（类/属/从/化分类与从化成立）',
     'blocked_by': 'missing_layers（B3）＋分类取舍未裁',
     'unlock': 'B3 推进后，分类采用另行呈请用户裁定',
     'needs_user_adjudication': True,
     'pending_decision_id': 'P-D2',
     'note': '与 B1 分开登记：B1 是化气格的条件表述取舍，B5 是从化象的分类与对象取舍；'
             '两者对象不同（D3），不得合并呈请'},
    {'id': 'B6',
     'item': '(a) 层口径差：干合事实不标示日干参与',
     'blocked_by': 'nothing_structural（实现细节）',
     'unlock': '随 P-D1 后的实现批在其实现内以柱位交集处理；若实现批前有独立消费方需要，'
               '再另行审定',
     'needs_user_adjudication': False},
)

HEHUA_LIMITATIONS = (
    '本模块只登记、不判定：化气成立恒 unresolved（P-D1／B1 待裁定）；'
    'transformation_status 恒 unresolved。',
    '四表述冲突未裁定（C1–C4）：任何下游不得自本登记摘取某一表述作化气判定。',
    '滴天髓《化象》章（F5/F6）未登记：只登记条件结构概要与缺口 B4，不作引文消费。',
    '本模块的原始转写（月支值、各干在场柱位与计数、辰在场、干合对在场）是表述中立的；'
    '月集归属、阻字在场、有二、旺气、根气等要素事实在 P-D1 裁定前不输出。',
    '司令不是任何已登记表述的条件要素（P14）；分日司令扩月与合化线无依赖。',
    'r005 红线：命中五合不等于化气成立；不得据五合直接输出感情适配、吉凶或关系评分。',
)

_PILLAR_NAMES = ('year', 'month', 'day', 'hour')


def _fail(message):
    raise ValueError(message)


def _validate_stems(stems):
    if type(stems) not in (list, tuple) or len(stems) != 4 \
            or any(type(s) is not str or s not in STEMS for s in stems):
        _fail('hehua transcription requires four heavenly stems')


def _validate_stems_branches(stems, branches):
    _validate_stems(stems)
    if type(branches) not in (list, tuple) or len(branches) != 4 \
            or any(type(b) is not str or b not in BRANCHES
                   for b in branches):
        _fail('hehua transcription requires four earthly branches')


def pair_presence(stems):
    """干合对在场（名册事实的复核，与已执行 r005 同一表）。

    ``stems`` 为年／月／日／时四干。返回在场干合对的记录（对名、
    名册化元素、在场柱位）；干合对不在场时不列入。只报在场事实，
    不作化气成立判断——命中≠化成（r005 红线）。
    """
    _validate_stems(stems)
    out = []
    for pair in HEHUA_PAIRS:
        first, second = pair['stems']
        pillars = [name for name, stem in zip(_PILLAR_NAMES, stems)
                   if stem in (first, second)]
        present_stems = {stem for stem in stems
                         if stem in (first, second)}
        if present_stems == {first, second}:
            out.append({'pair': pair['pair'], 'stems': pair['stems'],
                        'element': pair['element'],
                        'pillars': pillars,
                        'note': '名册在场事实（r005）；命中不等于化气成立。'})
    return out


def raw_transcription(stems, branches, day_stem):
    """表述中立的原始转写（SLICE_DECISION 回退形态）。

    只含月支值、各干在场柱位与计数、辰在场、干合对在场——不含任何
    表述的月集／阻字集／状态归一化，不含旺气／根气，不作任何条件
    满足判断。本转写是 P-D1 裁定所需的原始材料，不是条件事实层。
    """
    _validate_stems_branches(stems, branches)
    if type(day_stem) is not str or day_stem not in STEMS:
        _fail('hehua transcription requires an explicit day master stem')
    if stems[2] != day_stem:
        _fail('day_stem must equal the day pillar stem')
    stem_positions = {}
    stem_counts = {}
    for name, stem in zip(_PILLAR_NAMES, stems):
        stem_positions.setdefault(stem, []).append(name)
        stem_counts[stem] = stem_counts.get(stem, 0) + 1
    chen_pillars = [name for name, branch in zip(_PILLAR_NAMES, branches)
                    if branch == '辰']
    return {
        'variant': HEHUA_RULES_VARIANT,
        'transcription_kind': 'formulation_neutral_raw',
        'day_stem': day_stem,
        'month_branch': branches[1],
        'stem_positions': stem_positions,
        'stem_counts': stem_counts,
        'chen_present': bool(chen_pillars),
        'chen_pillars': chen_pillars,
        'pair_presence': pair_presence(stems),
        'note': ('表述中立的原始转写：月支值、各干在场柱位与计数、辰在场、'
                 '干合对在场；不含月集归属、阻字在场、有二、旺气、根气等'
                 '要素事实，不作条件满足判断（审定批 L7、SLICE_DECISION 回退形态）。'),
    }


def hehua_establishment(transcription=None):
    """化气成立结论：对任何输入恒返回 unresolved。

    ``transcription`` 可为 ``raw_transcription`` 的输出（只作事实上下文
    回显：干合对在场数与月支值）；未传入时上下文为空。成立判定是裁定层
    （P16，待裁定 P-D1／B1）：四表述并存且真冲突四项在案，018-C 登记
    conflict、adjudication=None，故本函数永不输出化成／不化成的结论，
    亦不输出任一表述下的条件满足判断。
    """
    pairs_present = 0
    month_branch = None
    if transcription is not None:
        if not isinstance(transcription, dict) \
                or transcription.get('variant') != HEHUA_RULES_VARIANT:
            _fail('hehua establishment requires a raw_transcription output')
        pairs_present = len(transcription.get('pair_presence') or [])
        month_branch = transcription.get('month_branch')
    return {
        'variant': HEHUA_RULES_VARIANT,
        'establishment': HEHUA_ESTABLISHMENT_STATUS,
        'transformation_status': 'unresolved',
        'pending_decision': 'P-D1',
        'pending_items': ['B1', 'B2', 'B3', 'B4'],
        'formulations_in_conflict': ['F1', 'F2', 'F3', 'F4'],
        'pairs_present': pairs_present,
        'month_branch': month_branch,
        'reason': ('化气成立未裁定：四条件表述并存且真冲突四项（C1–C4）在案，'
                   '018-C 登记 conflict、adjudication=None；采用哪一表述（或何种组合）'
                   '属用户级流派裁定 P-D1。干合对在场≠化气成立（r005）。'),
        'research_only': True, 'public': False, 'ai': False,
    }
