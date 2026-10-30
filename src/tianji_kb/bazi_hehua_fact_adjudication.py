"""合化（天干五合化气）审源与事实层设计审定登记（TJ-012.3 审定批）。

DESIGN / ADJUDICATION BATCH。本模块是纯数据审定登记，**零计算逻辑、
零判定代码**：不含任何函数，不被任何可执行路径 import（由公开测试
钉住）。本批只做四件事：(1) 盘点全树已登记来源中的合化材料；
(2) 对四种已登记条件表述（018-C 登记为 conflict 并列）做条件要素
对照与冲突结构分析；(3) 区分干合关系事实／条件要素事实／化气成立
判定三层并逐项判定可执行性；(4) 给出 SLICE_SPEC 结论（None）与
阻塞清单。实现与裁定另批。

背景：TJ-018-C 已落地三命卷二合化组三节校勘续册（校勘记 81 条、
引文 34 条），把合化条件四种表述登记为 conflict 并列不裁定
（HEHUA_CONDITION_VARIANTS）；Slice D 就绪度复审
（tj012-slice-d-readiness §3.2）判定合化「文本已登记，裁定还缺
三件」——条件分歧的裁定、戊癸未审记号、事实层口径。执行面现状：
bazi_core 已产天干五合的关系事实（Phase2 规则
bazi.phase2.stem_five_combinations，源出 Phase1 规则
bazi.rule.r005），但「合而能化」的条件判定不存在，裁定代码
bazi_action_conditions 的 transformation_status 恒 unresolved。

盘点结论（全量见 SOURCE_INVENTORY）：已登记的合化**条件**材料
全部在三命一家之内——合化组三节给出四种并存表述（逐对月条件／
旺气通则／有二则化与妬化／逐月横看表），018-C 已登记 conflict；
卷六《化象》节（018-G 登记）是相关的从化象 doctrine（日主从化，
与化气格是两个裁定对象）。滴天髓《化象》章（原注＋任氏曰）有
成套真化条件，但**未登记**——只有 BAZI_PATTERN_AUDIT.md 审计
条目 P05 在案（机上实测章界 [98297, 99943)）。渊海／神峰／穷通
的已登记 review_scope 无任何合化窗口（公开侧逐字核对），快照
文本中虽有化气／化象字样（机上计数在案）但未登记、只记缺口。
Canonical 侧：59 个 Section 中只有 s010（协纪五合名册短引）含
「五合」，无一含化气／合化／化象／真化／化格；phase1 无合化
概念实体（18 个概念中有三刑／司令／根型等 conflict 概念，独无
合化）——合化的流派冲突只存在于公开登记（018-C），密封概念层
从未立项。

冲突结构结论（全量见 CONFLICT_ANALYSIS）：真冲突四项——
(1) 逐对月条件与逐月表的化月集合系统性不一致（018-C 已逐月
计算：甲己正文要求月在表中无一作化土）；(2) 同节之内妬合字
（逐对条件）与妬化字（妬化说）对五对中的三对给出**不同**的
第三干（甲己：戊／乙；乙庚：甲／辛；戊癸：己／壬），同一功能
槽位两种触发字，不能同时编码为「阻字」；(3) 旺气通则与逐对
月条件是两套条件架构（不列月、以日辰旺气为准 vs 固定月集），
对同一命盘可给出相反结论；(4) 逐月表有化他元素之格（丁壬化
火、乙庚化木、甲己化木、戊癸化水），与名册化元素在结果层
冲突。其余为详略差（有二则化只见於甲己句、受气临官与喜时是
逐对附加项、无对应表述），不冒充冲突。戊癸逐对条件「非丙午
戌月」之丙为 unresolved_token（018-C 在案），使该对连逐对
表述自身的月集都不完整。

三层判定结论（全量见 FACT_LAYER_AUDIT 与 PROPOSITION_AUDIT）：
(a) 干合关系事实**已存在且已执行**（r005/phase2/bazi_core，
名册与三节一致、化元素只作表字段），口径差一处：现行事实是
任意柱对在场，不标示日干合与非日干合之别，而化气 doctrine
只取日干（旺气通则明文）——此差登记在案、留待裁定实现批处理，
不另立切片。(b) 条件要素事实：月支值、妬合／妬化字在场、有二
计数、辰在场都是柱面转写级在场事实（fact_ready_as_presence_
only，其「在场」可算、其效力不可算）；旺气与根气／有气被一般
旺衰与根层未建阻断；司令在任何已登记表述中**都不是**条件
要素（登记性缺位——逐对表述用月支集、通则用旺气，均不消费
分日司令，司令试点不是合化任何表述的输入）。(c) 化气成立
判定是裁定层：四表述采用属用户级流派裁定（待裁定 P-D1），
本批不代裁。

SLICE_SPEC = None（裁定理由见 SLICE_DECISION 与审定点 AP1）：
三刑切片成立的前提是「事实不存在且有消费方在等」；合化情形
相反——关系事实已存在，条件要素事实是柱面转写、无独立消费
方，且若按某一表述的要素集（月集／阻字）预建事实层，等于把
未裁定的表述选择预先编码进基础设施。故本批不出事实层切片，
产出为登记＋矩阵＋阻塞清单，与 S4 审定（SLICE_SPEC=None）
同例。

红线：本登记不产生任何化气成立／从化／化格判定，不把干合
关系事实冒充合化判定；四表述冲突不代裁；transformation_
status 的 unresolved 口径逐字不变（密封测试钉住）。
"""

HEHUA_ADJUDICATION_REGISTER = {
'id': 'bazi-hehua-fact-adjudication-v1',
'task': 'TJ-012.3',
'kind': 'transformation_condition_adjudication_register',
'adjudication_batch': '合化审源与事实层设计审定批（审定批，无判定实现）',
'source_snapshot': {
'name': 'daizhigev20',
'sanming_sha256':
'00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86',
'sanming_chars': 461157,
'trusted_manifest_sha256':
'f053761c3873d6d5cd63b738786c9b8ef683fd18f3b95c80f7bc485110cde480',
},
'baseline': {
'repo': 'HelloMrDuan/tianji-knowledge-base',
'main_sha': '729c5e6b85216ac52128ca1b9cc93429b94a3d8d',
'ledger_events_before': 269,
'ledger_event': 'E0270',
},
'headline_verdicts': {
'registered_formulations': 4,
'registered_formulations_note':
'四种条件表述全部出自三命卷二合化组（018-C 登记，conflict、'
'adjudication=None）；无第二家已登记的化气条件表述',
'unregistered_formulations': 2,
'unregistered_note':
'滴天髓《化象》原注与任氏曰各成一套真化条件，只有审计条目 '
'P05，未登记（缺口 B4）',
'related_registered_doctrine': 1,
'pairs': 5,
'condition_elements': 11,
'true_conflicts': 4,
'true_conflicts_note':
'C1–C4 为已登记表述间的真冲突；另有 C5（滴天髓化象章内逢龙/'
'逢五张力）因表述未登记，只作结构登记、不计入四项',
'propositions': 18,
'propositions_fact_ready': 2,
'propositions_presence_only': 6,
'slice_spec': None,
'slice_spec_note':
'不出事实层切片：关系事实已存在、要素事实是柱面转写、'
'预建要素层会预编码未裁定的表述选择（见 SLICE_DECISION）',
'user_decisions_pending': 2,
'implementation_in_this_batch': False,
'formulation_adjudicated': False,
'transformation_status_changed': False,
},
}

# ------------------------------------------------------------------
# 1. 盘点：全树已登记来源中的合化材料（16 项）
# ------------------------------------------------------------------

SOURCE_INVENTORY = [
{
'id': 'inv-01',
'material': '三命卷二合化组三节登记（合化条件的唯一已登记出处）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'src/tianji_kb/bazi_sanming_juan2_hehua_collation.py'
'（TJ-018-C 校勘记续册，注册表 '
'sanming-juan2-collation-register-v1）',
'locator': '《论十干合》[64208, 65956)、《论十干化气》'
'[65956, 67592)、《逐月横看理化之象》[67592, 68359)',
'counts': {'collation_notes': 81, 'quotes': 34, 'sections': 3},
'status': 'registered_evidence',
'note': '整书 quarantine_only、canonical_ready=false 不变；三节经 '
'018-C 逐条校勘（PUA 6、防 3、巳 82 处逐处判别）后达到可登记'
'状态。合化的名目、逐对条件、通则、逐月表全部已登记材料'
'都出自这三节。',
},
{
'id': 'inv-02',
'material': '表述 F1 逐对月条件（018-C 分支 prose-month-conditions）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'bazi_sanming_juan2_hehua_collation.'
'HEHUA_CONDITION_VARIANTS.branches[prose-month-conditions]；'
'引文 smhq.jiaji_cond / yigeng_cond / bingxin_cond / '
'dingren_cond / wugui_cond',
'locator': '《论十干化气》逐对条件句（字符 66607–67100 一带）',
'counts': {'pairs': 5, 'quotes': 5},
'status': 'registered_evidence_conflict_branch',
'note': '每对明列本局月（非…月不化）、其次一月与妬合字；甲己另有'
'受气临官（柱有巳亥）与喜时（戊辰时，smhq.jiaji_xi）两条'
'附加项，戊癸另有受气临官（见丁巳）。详见 '
'FORMULATION_REGISTER F1 与 PAIR_CONDITION_TABLE。',
},
{
'id': 'inv-03',
'material': '表述 F2 旺气通则（018-C 分支 general-wangqi-condition）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'HEHUA_CONDITION_VARIANTS.branches'
'[general-wangqi-condition]；引文 smhq.dafan',
'locator': '《论十干化气》[66656, 66733)',
'counts': {'quotes': 1},
'status': 'registered_evidence_conflict_branch',
'note': '「大凡化气只取日干而言，配合之神或年月与时皆可用，但要'
'日辰得旺气于时：若不得月中旺气，只时上旺气亦可；倘得月中'
'旺气而时上不乗旺气，则不可用；若月与日时俱得旺气，方为'
'全吉。」不逐对列月，以日辰旺气为条件架构。',
},
{
'id': 'inv-04',
'material': '表述 F3 有二则化与妬化（018-C 分支 erzehua-and-duhua）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'HEHUA_CONDITION_VARIANTS.branches'
'[erzehua-and-duhua]；引文 smhq.erzehua、smhq.duhua',
'locator': '《论十干化气》[66510, 66530) 与 [66571, 66607)',
'counts': {'quotes': 2},
'status': 'registered_evidence_conflict_branch',
'note': '「甲己化土，有二则化，一不能化，仍还本位之性」（有二句'
'只见於甲己对）；妬化以第三干见合分恋立说，逐对给出触发字'
'（甲己见乙、乙庚见辛、丁壬见丙、戊癸见壬、丙辛见丁）。'
'妬化触发字与 F1 妬合字对三对不同（见 CONFLICT_ANALYSIS C2）。',
},
{
'id': 'inv-05',
'material': '表述 F4 逐月横看表（018-C 分支 monthly-table-states）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'HEHUA_CONDITION_VARIANTS.branches'
'[monthly-table-states] 与 HENGKAN_TABLE_INTEGRITY；'
'引文 smhk.header_dingren、smhk.wugui_row_b3、'
'smhk.jiaji_row_b3、smhk.chenxu_row_b4',
'locator': '《逐月横看理化之象》[67592, 68359)',
'counts': {'cells': 120, 'rows': 10, 'pair_rows': 5},
'status': 'registered_evidence_conflict_branch',
'note': '10 行（五干对行＋四支组行＋四季行）×12 月全量转写；干对行'
'的化月集合与 F1 系统性不一致（018-C 已逐月计算分歧在案），'
'且有化他元素之格；状态词不限于化/不化（成形、暗秀、发贵、'
'衰薄、进秀、就妻、化秀等 20 余种，018-C 逐字登记、未归一'
'化）。支组行（寅午戌等）是局化陈述，与干合化气是两个对象，'
'只作同表登记、不用於干合条件矩阵。',
},
{
'id': 'inv-06',
'material': '戊癸条件「非丙午戌月」之丙（unresolved_token）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'HEHUA_CONDITION_VARIANTS.unresolved_tokens'
'（018-C 登记）',
'locator': '《论十干化气》字符 67073 附近（smhq.wugui_cond）',
'counts': {'unresolved_tokens': 1},
'status': 'unresolved_not_quotable_as_condition',
'note': '丙字为传本原文（kanripo、NiuTrans、youngzs 三谱系一致），'
'非快照讹字、不校改；解析未审：作月支列举则与寅午戌火局不'
'合，作干支复合条件则与同节逐对句式不齐。F1 的戊癸本局月集'
'因此只能登记为「丙午戌」（传本形）＋已解 [午, 戌]＋未解 '
'丙——任一化气裁定先行撞上它。',
},
{
'id': 'inv-07',
'material': '三命卷六《化象》节登记（从化象 doctrine，018-G）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'src/tianji_kb/bazi_sanming_juan6_fangju_baxiang_'
'collation.py（注册表 sanming-juan6-collation-register-v1）；'
'引文 hx.definition、hx.tongxuan、hx.example、hx.jingshan',
'locator': 'sanming_tonghui.txt [214516, 214948)',
'counts': {'quotes': 4},
'status': 'registered_evidence_related_doctrine',
'note': '对象是从化象（日主从化）而非化气格：通玄论「乙旺庚从、'
'庚旺乙从……日主无气，化有气方可用」，荆山居士类/属/从/化'
'四分且「类属要身旺而从化要衰」。与化气条件共享干合在场'
'事实，但裁定对象、强弱极性（从化要衰 vs 旺气通则要旺）都'
'不同，两层不得混并（见命题 P15）。',
},
{
'id': 'inv-08',
'material': '滴天髓《化象》章：审计条目在案、未登记（缺口）',
'source_id': 'bazi.source.ditiansui-spouse',
'registered_at': 'docs/product/BAZI_PATTERN_AUDIT.md 条目 P05'
'（审计条目）；本批机上实测定界',
'locator': 'ditiansui_chanwei.txt「十三、化象」[98297, 99943)；'
'P05 锚点 98303「化得真者只论化，化神还有几般话」',
'counts': {'chapters': 1, 'registered_quotes': 0,
'audit_entries': 1},
'status': 'audit_entry_only_not_registered',
'note': '原注给出逐对真化条件（甲己生四季月、丙辛冬月、戊癸夏月、'
'乙庚秋月、丁壬春月；独自相合；甲己例另要月时上合、有一辰'
'字、得龙以运之），任氏曰另立「合则化」与逢五而化（五辰之'
'位）之说、与世传逢龙而化并存。本批只记缺口与章界实测，'
'不新登记其文（逐节登记另批，见 PENDING_ITEMS B4）；'
'FORMULATION_REGISTER 的 F5/F6 只登记其条件结构概要与'
'未登记状态，不作引文消费。',
},
{
'id': 'inv-09',
'material': '渊海已登记材料：无合化条件窗口（登记性缺位）',
'source_id': 'bazi.source.yuanhai',
'registered_at': 'config/knowledge_sources.json '
'bazi.source.yuanhai review_scope（公开侧逐字核对：化气/合化/'
'化象/五合/化格关键词命中 0）',
'locator': 'yuanhai_ziping.txt 快照实测：化气 1、化象 2、妒合 2'
'（字符计数，本批机上实测）',
'counts': {'registered_hehua_windows': 0,
'snapshot_keyword_counts': {'化气': 1, '化象': 2, '妒合': 2}},
'status': 'registered_absence',
'note': '渊海文本并非没有合化字样，而是已登记窗口（四柱/十神/藏干'
'短段与正官/印綬组）不含合化条件句。未登记者只记缺口，'
'逐节登记另批，不在本批补入。',
},
{
'id': 'inv-10',
'material': '神峰／穷通已登记材料：无合化条件窗口（登记性缺位）',
'source_id': 'cross-source',
'registered_at': 'config/knowledge_sources.json 两源 review_scope'
'（关键词命中 0）；公开模块 bazi_bingyao.py（病药 Variant）、'
'bazi_tiaohou.py（调候 Variant）全文无化气/合化/化象条件句',
'locator': '快照实测：shenfeng_tongkao.txt 化气 2、化象 3、化格 3、'
'妒合 4；qiongtong_baojian.txt 化格 1、余 0（本批机上实测）',
'counts': {'registered_hehua_windows': 0},
'status': 'registered_absence',
'note': '神峰文本有化格字样但已登记窗口（病药两对）不含之；穷通以'
'调候立书，合化非其条件面。均只记缺口。',
},
{
'id': 'inv-11',
'material': '执行面事实层 (a)：五合名册事实已执行',
'source_id': 'cross-source',
'registered_at': '密封 phase1 规则 bazi.rule.r005（天干五合固定'
'配对）＋phase2 规则 bazi.phase2.stem_five_combinations'
'（executable/validated）；公开执行 bazi_core.'
'stem_five_combination / reviewed_relations；名册表 '
'foundations_v1.json stem_combinations',
'locator': 'foundations stem_combinations 五对：甲己土/乙庚金/'
'丙辛水/丁壬木/戊癸火（机上实测）',
'counts': {'pairs': 5, 'phase2_rules_total': 31},
'status': 'executed_fact_layer',
'note': 'r005 明文：traditional_result_element 是「表中传统化气'
'五行，仅作表字段，不判断化成」；exceptions「命中五合不'
'等于化气成立」；difference「化气成败条件、争合妒合及吉凶'
'解释不在本规则」。phase2 evidence_scope「只确认五组配对，'
'不判断化气成败或吉凶」。名册的 Canonical 锚点是协纪 '
's010（inv-13）。',
},
{
'id': 'inv-12',
'material': '裁定面现状：transformation 恒 unresolved（多处明文）',
'source_id': 'cross-source',
'registered_at': 'src/tianji_kb/bazi_action_conditions.py '
'transformation_status；phase2_execution.json unresolved '
'清单；bazi_pattern.py 未决项；product_coverage 能力说明',
'locator': 'bazi_action_conditions.py: transformation_status 在'
'五合/六合/三合任一出现时为 unresolved、否则 not_present',
'counts': {'explicit_unresolved_statements': 4},
'status': 'status_quo_unresolved',
'note': 'phase2 unresolved 清单两条直接相关：「五合/六合命中不'
'代表化气成立」与「半合、拱合、成化条件与吉凶解释未'
'裁定」。bazi_pattern 的渊海单例观察把 '
'actual_harmony_transformation 列入 unresolved；'
'product_coverage 明示化格 NOT_BUILT、五合结构不能定化'
'（BAZI_PATTERN_AUDIT.md 化格行）。本批后此现状逐字不变。',
},
{
'id': 'inv-13',
'material': '协纪辨方书五合名册短引（事实层的 Canonical 锚点）',
'source_id': 'bazi.source.xieji-relations',
'registered_at': '密封 phase1 Section bazi.section.s010；来源 '
'review_scope「天干五合……仅用于结构查表」；术语 '
'bazi.term.stem_five_combinations',
'locator': 'bazi.section.s010「甲与己合乙与庚合丙与辛合丁与壬合'
'戊与癸合」',
'counts': {'sections': 1, 'terms': 1},
'status': 'registered_canonical_roster',
'note': '术语定义明文「本库仅登记结构命中，不自动判断化气是否'
'成立」。机上 phase1 全量扫描（本批）：59 个 Section 中含'
'化气/合化/化象/真化/化格者 0、含五合者仅 s010——Canonical '
'层没有任何合化条件 Section。',
},
{
'id': 'inv-14',
'material': '概念层缺位：phase1 无合化概念实体',
'source_id': 'cross-source',
'registered_at': '机上实测 phase1_knowledge.json concepts 全表'
'（本批）：共 18 个，无合化/化气概念',
'locator': 'concepts: conflict_spouse_star_lens、'
'conflict_three_punishments、conflict_siling_days、'
'conflict_root_type_readings 等在册，合化不在册',
'counts': {'concepts_total': 18, 'hehua_concepts': 0},
'status': 'measured_absence',
'note': '与三刑对照：三刑的流派冲突有密封概念实体（unresolved、'
'blocked_pending_school_resolution）；合化的冲突只存在于'
'公开登记 018-C 的 HEHUA_CONDITION_VARIANTS，概念层从未'
'立项。本批不新建概念（治理批另行），只登记缺位事实。精'
'确口径：18 个概念中唯一出现「合化」字样的是 '
'action_conditions_variant_v1 的 unresolved_conditions '
'清单（把合化列为未决条件之一）——是「被提及为未决」而'
'非合化概念实体，密封测试按此口径钉住（概念 ID 全表见 '
'SEALED_MEASUREMENTS）。',
},
{
'id': 'inv-15',
'material': 'S5 注册治理登记：合化无条目（连 pending 都未立）',
'source_id': 'cross-source',
'registered_at': 'src/tianji_kb/bazi_registration_governance.py'
'（S5 治理登记全文检索：化气/合化/化象/真化/妬合/妒合 '
'命中 0）',
'locator': 'bazi_registration_governance.py',
'counts': {'hehua_entries': 0},
'status': 'measured_absence',
'note': 'S5 的 pending 12 项（调候/lu/金水/大运/病药/禄刃/杂气等）'
'不含合化——合化裁定层尚无任何谓词/Variant 存在，自然无'
'注册候选。本批不改变治理登记。',
},
{
'id': 'inv-16',
'material': '旺衰审定线对合化的处置：明示不在范围、无谓词消费',
'source_id': 'cross-source',
'registered_at': 'src/tianji_kb/bazi_fire_si_yin_morphology.py '
'诸 disposition 的 scope_limit；bazi_adjudication 八谓词',
'locator': 'bazi_fire_si_yin_morphology.py: 「combination or '
'transformation; those remain unadjudicated outside this '
'form」「until transformation is adjudicated」',
'counts': {'predicates_consuming_transformation': 0},
'status': 'registered_scope_exclusion',
'note': 'F3 审定对账中丙辛合曾作为关系事实出现在对照例推导（审定'
'批漏计、实现批订正，见 E0248）——那是干合**关系事实**在'
'计数中的出现，不是合化判定。八条旺衰谓词无一消费合化。',
},
]

# ------------------------------------------------------------------
# 2. 表述登记：四种已登记表述 + 两种未登记表述 + 从化象 doctrine
# ------------------------------------------------------------------

FORMULATION_REGISTER = [
{
'id': 'F1',
'name': '逐对月条件（prose-month-conditions）',
'registered': True,
'register_ref': 'bazi_sanming_juan2_hehua_collation.'
'HEHUA_CONDITION_VARIANTS.branches[prose-month-conditions]',
'source_id': 'bazi.source.sanmingtonghui',
'text_layer': '正文（《论十干化气》逐对条件句）',
'school_attribution': '三命通会体系',
'condition_structure': '每对：本局月集（非…月不化）＋其次一月'
'（亦化）＋妬合字（间之/柱有则不化）；甲己、戊癸另有受气'
'临官附加项，甲己另有喜时附加项',
'evidence_quotes': ['smhq.jiaji_cond', 'smhq.yigeng_cond',
'smhq.bingxin_cond', 'smhq.dingren_cond', 'smhq.wugui_cond',
'smhq.jiaji_xi'],
'status': 'conflict_branch_unadjudicated',
},
{
'id': 'F2',
'name': '旺气通则（general-wangqi-condition）',
'registered': True,
'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
'[general-wangqi-condition]',
'source_id': 'bazi.source.sanmingtonghui',
'text_layer': '正文（《论十干化气》「大凡」通则句）',
'school_attribution': '三命通会体系',
'condition_structure': '只取日干；配合之神年月时皆可用；日辰得'
'月中旺气为上、只时上旺气亦可、月时俱得为全吉、得月中旺'
'气而时上不乗旺气则不可用。不逐对列月',
'evidence_quotes': ['smhq.dafan'],
'status': 'conflict_branch_unadjudicated',
},
{
'id': 'F3',
'name': '有二则化与妬化（erzehua-and-duhua）',
'registered': True,
'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
'[erzehua-and-duhua]',
'source_id': 'bazi.source.sanmingtonghui',
'text_layer': '正文（《论十干化气》「又曰」与妬化说）',
'school_attribution': '三命通会体系',
'condition_structure': '有二则化、一不能化仍还本位（原文只见於'
'甲己句）；妬化：第三干见合分恋，逐对给触发字',
'evidence_quotes': ['smhq.erzehua', 'smhq.duhua'],
'status': 'conflict_branch_unadjudicated',
},
{
'id': 'F4',
'name': '逐月横看表（monthly-table-states）',
'registered': True,
'register_ref': 'HEHUA_CONDITION_VARIANTS.branches'
'[monthly-table-states] + HENGKAN_TABLE_INTEGRITY',
'source_id': 'bazi.source.sanmingtonghui',
'text_layer': '正文表格（《逐月横看理化之象》）',
'school_attribution': '三命通会体系',
'condition_structure': '逐对逐月给状态词（化X/不化/其他状态词）；'
'化月集合与 F1 系统性不一致；有化他元素之格；状态词未归一化',
'evidence_quotes': ['smhk.header_dingren', 'smhk.wugui_row_b3',
'smhk.jiaji_row_b3', 'smhk.chenxu_row_b4'],
'status': 'conflict_branch_unadjudicated',
},
{
'id': 'F5',
'name': '滴天髓化象原注真化条件',
'registered': False,
'register_ref': 'docs/product/BAZI_PATTERN_AUDIT.md P05（审计'
'条目）；章界机上实测 [98297, 99943)',
'source_id': 'bazi.source.ditiansui-spouse',
'text_layer': '原注（《滴天髓阐微》十三、化象）',
'school_attribution': '滴天髓原注层',
'condition_structure': '逐对季节月（甲己四季、丙辛冬、戊癸夏、'
'乙庚秋、丁壬春）；独自相合（单遇一位）；甲己例：月时上'
'合、有一辰字、得龙以运之；真化/假化之分',
'evidence_quotes': [],
'status': 'audit_entry_only_not_registered',
'note': '条件结构概要据审计条目与本批章界实测著录，不作引文'
'消费；登记前不得据此设计任何事实或判定（缺口 B4）。',
},
{
'id': 'F6',
'name': '滴天髓化象任氏曰（合则化/逢五而化）',
'registered': False,
'register_ref': '同 F5（任氏曰层，未登记）',
'source_id': 'bazi.source.ditiansui-spouse',
'text_layer': '任氏曰（《滴天髓阐微》十三、化象）',
'school_attribution': '滴天髓任氏层',
'condition_structure': '合则化之源说（数合之义）；化必得五土'
'（辰）而后成、逢五而化，与世传逢龙而化并存讨论',
'evidence_quotes': [],
'status': 'audit_entry_only_not_registered',
'note': '与 F5 的逢龙说在同章内并存（龙=辰字在场 vs 五=五辰之'
'位），是章内教义张力；未登记，只记结构。',
},
{
'id': 'HX',
'name': '三命卷六化象（从化象 doctrine）',
'registered': True,
'register_ref': 'bazi_sanming_juan6_fangju_baxiang_collation'
'（sanming.juan6.huaxiang）',
'source_id': 'bazi.source.sanmingtonghui',
'text_layer': '正文（含引述：通玄论、玄虚道人、荆山居士）',
'school_attribution': '三命通会体系',
'condition_structure': '对象是日主从化：旺者从（乙旺庚从、庚旺'
'乙从）、日主无气、化有气方可用；类/属/从/化四分，类属要'
'身旺而从化要衰',
'evidence_quotes': ['hx.definition', 'hx.tongxuan', 'hx.example',
'hx.jingshan'],
'status': 'registered_related_doctrine_not_hehua_condition',
'note': '与 F1–F4 不是同一裁定对象：化气格问「合而化否」，化象'
'问「日主从化否」。共享干合在场事实，条件面（无气/有气、'
'身旺/要衰）属从格与旺衰层。本批只登记其相关性与划界。',
},
]

# F1 逐对条件全表（与 018-C 登记逐项对应；公开测试交叉核对）。
PAIR_CONDITION_TABLE = [
{'pair': '甲己', 'element': '土',
'primary_months': ['辰', '戌', '丑', '未'],
'secondary_months': ['午'],
'blocker_stem_f1': '戊', 'blocker_phrasing': '有戊字间之',
'blocker_stem_f3_duhua': '乙',
'extras': ['受气临官：柱有巳亥（smhq.jiaji_cond）',
'喜时：戊辰时（smhq.jiaji_xi）'],
'condition_quote': 'smhq.jiaji_cond'},
{'pair': '乙庚', 'element': '金',
'primary_months': ['巳', '酉', '丑'],
'secondary_months': ['申'],
'blocker_stem_f1': '甲', 'blocker_phrasing': '有甲字间之',
'blocker_stem_f3_duhua': '辛',
'extras': [],
'condition_quote': 'smhq.yigeng_cond'},
{'pair': '丙辛', 'element': '水',
'primary_months': ['申', '子', '辰'],
'secondary_months': ['亥'],
'blocker_stem_f1': '丁', 'blocker_phrasing': '柱有丁字',
'blocker_stem_f3_duhua': '丁',
'extras': [],
'condition_quote': 'smhq.bingxin_cond'},
{'pair': '丁壬', 'element': '木',
'primary_months': ['亥', '卯', '未'],
'secondary_months': ['寅'],
'blocker_stem_f1': '丙', 'blocker_phrasing': '柱有丙字',
'blocker_stem_f3_duhua': '丙',
'extras': [],
'condition_quote': 'smhq.dingren_cond'},
{'pair': '戊癸', 'element': '火',
'primary_as_transmitted': '丙午戌',
'primary_months': ['午', '戌'],
'primary_unresolved_token': '丙',
'secondary_months': ['巳'],
'blocker_stem_f1': '己', 'blocker_phrasing': '柱有己字',
'blocker_stem_f3_duhua': '壬',
'extras': ['受气临官：寅午戌生人见丁巳（smhq.wugui_cond）'],
'condition_quote': 'smhq.wugui_cond'},
]

# ------------------------------------------------------------------
# 3. 条件要素 × 表述矩阵（§2 对照表；absent = 该表述无此要素）
# ------------------------------------------------------------------

CONDITION_MATRIX = {
'elements': [
'subject', 'month_condition', 'hour_condition',
'third_stem_blocker', 'multiplicity', 'wangqi', 'root_qi',
'commander', 'chen_factor', 'strength_polarity',
'result_element',
],
'rows': {
'subject': {
'F1': '干对（句式为逐对泛称；对象范围由 F2 限定为日干）',
'F2': '只取日干；配合之神或年月与时皆可用',
'F3': '干对（有二句只见於甲己对）',
'F4': '干对×月份（格）',
'F5': '日主（日干与合神）',
'F6': '日干（合则化之源说）',
'HX': '日主（从化主体）',
},
'month_condition': {
'F1': '本局月集（非…月不化）＋其次一月（亦化），逐对列明',
'F2': '不列月集；以得月中旺气代之',
'F3': 'absent',
'F4': '逐月状态格（化月集合与 F1 不一致，见 C1）',
'F5': '季节月：甲己四季/丙辛冬/戊癸夏/乙庚秋/丁壬春',
'F6': 'absent（以辰位立论，非月集）',
'HX': 'absent（以支组全/旺衰立论）',
},
'hour_condition': {
'F1': '仅甲己有喜时附加项（戊辰时）',
'F2': '时上旺气（可代月中旺气；月中已得而时上不乗则不可用）',
'F3': 'absent',
'F4': 'absent（表无时维）',
'F5': '甲己例：配合在月时上合',
'F6': 'absent',
'HX': 'absent',
},
'third_stem_blocker': {
'F1': '妬合字：逐对一字（戊/甲/丁/丙/己），措辞分「间之」与'
'「柱有」两式（见 P6 注记）',
'F2': 'absent',
'F3': '妬化字：逐对一字（乙/辛/丁/丙/壬），「见」式；与 F1 对'
'三对不同（见 C2）',
'F4': 'absent（表无阻字维）',
'F5': '未登记（章内有妒合字样，不作要素消费）',
'F6': '未登记',
'HX': 'absent',
},
'multiplicity': {
'F1': 'absent（《论十干合》另有偏枯说：一己合两甲/两甲合一己'
'为阴阳偏枯——属合的形态 doctrine，非化条件）',
'F2': 'absent',
'F3': '有二则化、一不能化仍还本位（只见於甲己句，向他对的'
'推广是解释步、未登记）',
'F4': 'absent',
'F5': '独自相合/单遇一位（与 F3 有二方向相反：独合 vs 有二）',
'F6': 'absent',
'HX': 'absent',
},
'wangqi': {
'F1': '隐含：本局月集即化神三合局月/四季土月，是旺地的列举，'
'不是旺气判据本身',
'F2': '核心要素：日辰得旺气（月中为上、时上亦可、俱得全吉）',
'F3': 'absent',
'F4': '隐含於逐月状态（未明言判据）',
'F5': '以季节月列举旺地（同 F1 型）',
'F6': 'absent',
'HX': '作「化有气方可用」（化神有气）',
},
'root_qi': {
'F1': '附加项：受气临官（甲己柱有巳亥、戊癸见丁巳）',
'F2': 'absent（旺气非根气）',
'F3': 'absent',
'F4': 'absent',
'F5': 'absent（辰字另列）',
'F6': 'absent',
'HX': '核心：日主无气、化有气（气之有无）',
},
'commander': {
'F1': 'absent', 'F2': 'absent', 'F3': 'absent', 'F4': 'absent',
'F5': 'absent', 'F6': 'absent', 'HX': 'absent',
'note': '任何已登记表述都不以分日司令为条件要素：F1/F5 用月支'
'集、F2 用旺气、HX 用支组与旺衰。司令试点（寅月、任氏）'
'不是合化任何表述的输入；「司令扩月未裁」不构成合化事实'
'层的阻塞项（与就绪度复审把司令列为 D-1 前置的情形不同）。',
},
'chen_factor': {
'F1': 'absent（辰只在甲己本局月集内作为四季月之一）',
'F2': 'absent',
'F3': 'absent',
'F4': 'absent',
'F5': '甲己例：有一辰字、得龙以运之（逢龙而化）',
'F6': '化必得五土（辰）、逢五而化（五辰之位）——与 F5 逢龙说'
'同章并存（见 CONFLICT_ANALYSIS C5）',
'HX': 'absent（辰戌丑未支组行属 F4 表内局化，非干合化象）',
},
'strength_polarity': {
'F1': '无明言（月集隐含化神旺）',
'F2': '日辰得旺气（日干/化神向旺）',
'F3': 'absent',
'F4': '无明言',
'F5': '真化（与假化对举，未登记展开）',
'F6': 'absent',
'HX': '从化要衰、日主无气（与 F2 极性相反——对象不同，不构成'
'同对象冲突，见 CONFLICT_ANALYSIS D3）',
},
'result_element': {
'F1': '名册固定（甲己土/乙庚金/丙辛水/丁壬木/戊癸火）',
'F2': '名册固定（同上）',
'F3': '名册固定（同上）',
'F4': '有化他元素之格（丁壬化火、乙庚化木、甲己化木、戊癸化'
'水/为水）——与名册冲突（见 C4）',
'F5': '名册固定（同上）',
'F6': '名册固定（同上）',
'HX': '从化之神即合神（名册内）',
},
},
}

# ------------------------------------------------------------------
# 4. 冲突结构分析：真冲突 vs 详略差
# ------------------------------------------------------------------

CONFLICT_ANALYSIS = {
'true_conflicts': [
{
'id': 'C1',
'title': 'F1 月集 vs F4 化月集合（同要素、不同集合）',
'element': 'month_condition',
'detail': '018-C 已逐月计算（HEHUA_CONDITION_VARIANTS 的 '
'divergence 在案；月序为表列正月至十二月）：甲己——F1 '
'要求 {三、五、六、九、十二月}，其中三、五、六月在 F4 '
'为暗秀/不化/不化，F4 化月 {七、九、十一、十二} 中七、'
'十一月 F1 未要求；乙庚——F1 要求 {四、七、八、十二}，'
'四、八月在 F4 为金秀/进秀（未作化金），F4 化月含一、'
'二月（F1 未要求）；丙辛——F1 要求 {三、七、十、十一}，'
'七、十一月在 F4 为进秀学堂/化秀（未作化水）；丁壬——'
'F1 要求月 F4 全数作化木，但 F4 另多七、十一两化月；'
'戊癸——F1 要求 {四、五、九}，五月在 F4 为不化，F4 化'
'火月 {一、二、三、四、九、十二} 中一、二、三、十二月 '
'F1 未要求。五对全部分歧，非个别月份出入。',
'kind': 'same_element_different_threshold',
},
{
'id': 'C2',
'title': 'F1 妬合字 vs F3 妬化字（同功能槽位、不同触发字）',
'element': 'third_stem_blocker',
'detail': '五对中三对不同：甲己 F1 戊/F3 乙；乙庚 F1 甲/F3 辛；'
'戊癸 F1 己/F3 壬；两对相同：丙辛同为丁、丁壬同为丙。两'
'说同在《论十干化气》一节之内、功能槽位相同（第三干出现'
'则不化），触发字却对三对不一致——无论读作同一机制的两'
'种传述，还是妬合（间之分位）与妬化（自恋其生）两个机制，'
'编码时都不能同时充当「阻字」而不作选择。',
'kind': 'same_slot_different_trigger',
},
{
'id': 'C3',
'title': 'F1 列举月集 vs F2 旺气架构（条件架构不同）',
'element': 'month_condition / wangqi',
'detail': 'F1 以固定月集为充分面（生於本局月即满足月条件），'
'F2 不列月集、以日辰实际得旺气为准（月中/时上）。月支在'
'F1 集内而日辰不得旺气、或月支不在集内而日辰得旺气（经'
'时上）两种情形下两说结论相反。这是架构级分歧，不是同一'
'判据的详略。',
'kind': 'different_condition_architecture',
},
{
'id': 'C4',
'title': 'F4 化他元素 vs 名册化元素（结果层冲突）',
'element': 'result_element',
'detail': 'F4 表内丁壬化火（四、五、九月位）、乙庚化木（十、'
'十一月位）、甲己化木（十月位）、戊癸化水/为水（七、十、'
'十一月位）——同一干对在表中可化出名册外元素，与 F1/F2/'
'F3/F5/F6 及名册本身（丁壬木、乙庚金、甲己土、戊癸火）'
'在结果层冲突。',
'kind': 'different_result',
},
{
'id': 'C5',
'title': 'F5 逢龙而化 vs F6 逢五而化（未登记、章内张力）',
'element': 'chen_factor',
'detail': '同在滴天髓化象章：原注与世传以辰（龙）在场为化之'
'助（得龙以运之），任氏曰别立「化必得五土而后成、逢五而'
'化」并谓「近世……只知逢龙而化，不知逢五而化」。两说指'
'向不同事实（辰支在场 vs 干序第五位逢辰干支），未登记、'
'只记结构；其裁定以 B4 登记为前提。',
'kind': 'intra_chapter_doctrinal_tension_unregistered',
},
],
'detail_differences_not_conflicts': [
{
'id': 'D1',
'title': 'F3 有二则化只见於甲己句',
'detail': '他对无对应陈述，是缺席而非矛盾；把「有二」推广为'
'五对通则是一个解释步，未经登记，本批不作推广。',
},
{
'id': 'D2',
'title': 'F1 受气临官/喜时是逐对附加项',
'detail': '只见於甲己（巳亥、戊辰时）与戊癸（丁巳），他对与他'
'表述无对应项；是该对条件面的加细，不与任何表述冲突。',
},
{
'id': 'D3',
'title': 'F2 要旺 vs HX 要衰：对象不同、非冲突',
'detail': 'F2 论化气格（日干与合神化出之神宜旺），HX 论从化象'
'（日主宜无气而从化神）。裁定对象不同，极性相反不构成同'
'对象冲突；但两层共享干合在场事实，下游不得把任一极性'
'错接到另一对象。',
},
{
'id': 'D4',
'title': 'F5 独自相合 vs F3 有二则化：方向相反但书别不同',
'detail': 'F5（滴天髓原注，未登记）要独合，F3（三命，又曰）言'
'有二则化——跨书、跨登记状态，只登记为流派差候选，不与'
'C1–C4 同级列为已登记真冲突。',
},
{
'id': 'D5',
'title': 'F1 妬合措辞「间之」与「柱有」并存',
'detail': '甲己/乙庚作「有X字间之」，丙辛/丁壬/戊癸作「柱有X'
'字」——同表述内的措辞差：「间之」可读作在场、亦可读作'
'居间（位于两合干之间）。这是表述内部的解析未定（见 '
'P6），不是表述间冲突。',
},
],
'adjudication': None,
'note': '本批只做冲突结构分析：标明何者真冲突、何者详略差；'
'不裁定、不统一（018-C 的 conflict 登记与本批分析都不改变'
'HEHUA_CONDITION_VARIANTS 的 status/adjudication）。',
}

# ------------------------------------------------------------------
# 5. 三层事实审计：(a) 关系事实 (b) 条件要素事实 (c) 化气成立判定
# ------------------------------------------------------------------

FACT_LAYER_AUDIT = {
'layer_a_combination_facts': {
'status': 'exists_and_executed',
'content': '五合名册五对＋化元素表字段（foundations '
'stem_combinations）；bazi_core.stem_five_combination 逐对'
'查表、reviewed_relations 汇总四柱六个柱对的在场事实（柱位、'
'干、traditional_result_element）；Phase1 r005＋Phase2 '
'stem_five_combinations 已注册已验证。',
'coverage_check': '名册与 018-C 三节逐对一致（HEHUA_FACT_LINKAGE '
'在案、018-C 密封专项以执行函数逐对交叉核对化元素不变）；'
'柱对覆盖为全部六对（含非相邻柱对），与 doctrine 的对象'
'范围（F2：配合之神或年月与时皆可用）相容。',
'calibre_gap': '现行事实不标示「日干参与」与否：任一柱对命中即'
'报，不区分日干合（如日干甲与时干己）与非日干合（如年干'
'甲与月干己而日干为他）。化气 doctrine 只取日干（F2 明'
'文），故 (a) 层事实是化气条件的**超集**——消费方须自行'
'以柱位交集筛出日干合。此口径差登记在案（命题 P3），'
'处理方式属未来裁定实现批，不另立事实切片（见 '
'SLICE_DECISION）。',
'boundary': 'traditional_result_element 是名册表字段（r005 '
'明文「仅作表字段，不判断化成」），不得读作化气结论。',
},
'layer_b_condition_elements': [
{'element': 'pair_presence', 'fact': '合对在场（柱对级）',
'verdict': 'fact_ready', 'ref': 'P2（(a) 层已执行）'},
{'element': 'day_stem_involvement', 'fact': '合对是否涉日干',
'verdict': 'fact_ready_as_presence_only',
'ref': 'P3（可由柱位导出、现行事实不单独标示）'},
{'element': 'month_branch_value', 'fact': '月支值',
'verdict': 'fact_ready', 'ref': 'P4 前半（命盘事实恒可读）'},
{'element': 'f1_month_set_membership', 'fact': '月支属 F1 本局/'
'其次月集', 'verdict': 'adjudication_required',
'ref': 'P4（机械分类无歧义，但集合属未采用表述；戊癸集另见 P5）'},
{'element': 'blocker_presence_f1', 'fact': 'F1 妬合字在场',
'verdict': 'fact_ready_as_presence_only',
'ref': 'P6（「间之」解析未定，在场≠居间）'},
{'element': 'blocker_presence_f3', 'fact': 'F3 妬化字在场',
'verdict': 'fact_ready_as_presence_only', 'ref': 'P7'},
{'element': 'blocker_effect', 'fact': '阻字出现 ⇒ 不化',
'verdict': 'blocked_by_formulation_conflict',
'ref': 'P8（C2：两说触发字对三对不同）'},
{'element': 'multiplicity_presence', 'fact': '合神/日干重见计数'
'（有二的事实面）', 'verdict': 'fact_ready_as_presence_only',
'ref': 'P9（计数是在场事实；「有二则化」之效与推广属裁定）'},
{'element': 'reception_linguanshi_presence',
'fact': '受气临官字/喜时在场（甲己巳亥、戊癸丁巳、甲己戊辰时）',
'verdict': 'fact_ready_as_presence_only', 'ref': 'P10'},
{'element': 'chen_presence', 'fact': '辰支在场',
'verdict': 'fact_ready_as_presence_only',
'ref': 'P11（事实可算；其所属表述 F5/F6 未登记）'},
{'element': 'wangqi', 'fact': '日辰月中/时上旺气',
'verdict': 'blocked_by_missing_layers',
'ref': 'P12（旺相框架只有 018-A 登记文本，无可执行旺气定义；'
'一般旺衰不存在，TJ-011.2 现状）'},
{'element': 'root_qi', 'fact': '日主/化神根气与有气无气',
'verdict': 'blocked_by_missing_layers',
'ref': 'P13（根层只有 participation 级事实，气之有无属旺衰/'
'从格层）'},
{'element': 'commander', 'fact': '分日司令',
'verdict': 'registered_absence',
'ref': 'P14（无已登记表述以司令为要素，见 CONDITION_MATRIX '
'commander 行注记）'},
],
'layer_c_transformation_verdict': {
'status': 'adjudication_layer_not_fact',
'content': '化气成立与否不是事实，是在 (a)(b) 之上按某一表述'
'作出的裁定。四表述采用（及其组合方式）属用户级流派裁定'
'P-D1；从化象成立另属 P-D2 且先被旺衰/从格层阻断。',
'current_surface': 'transformation_status 恒 unresolved（inv-12），'
'本批不变。',
},
}

# ------------------------------------------------------------------
# 6. 可执行性逐项判定（P1–P17）
# ------------------------------------------------------------------

PROPOSITION_AUDIT = [
{
'id': 'P1', 'proposition': '五合名册与化元素对应（甲己土/乙庚金/'
'丙辛水/丁壬木/戊癸火）',
'verdict': 'fact_ready',
'basis': '三独立面一致：018-C 两节正文＋逐月表行名册、协纪 s010 '
'名册（inv-13）、foundations 执行表（inv-11）；018-C 明文'
'「在两节间一致」',
'enters': '已执行（(a) 层）；本批不新增',
},
{
'id': 'P2', 'proposition': '干合对在场事实（任意柱对）',
'verdict': 'fact_ready',
'basis': 'bazi_core.reviewed_relations 已执行并经 Phase2 验证'
'（golden bazi.relations-core）；F3 审定对账曾以之为计数'
'依据（inv-16）',
'enters': '已执行；本批零接线变更',
},
{
'id': 'P3', 'proposition': '日干合对在场（化气 doctrine 的对象面）',
'verdict': 'fact_ready_as_presence_only',
'basis': '可由 P2 事实＋柱位（day 柱）交集导出，属在场事实的'
'筛选而非新判定；但现行事实输出不单独标示，消费方须自行'
'筛选——口径差登记於 FACT_LAYER_AUDIT.layer_a',
'enters': '不另立切片；留待裁定实现批在其实现内处理（B6）',
},
{
'id': 'P4', 'proposition': 'F1 月集归属（月支 ∈ 本局月/其次月）',
'verdict': 'adjudication_required',
'basis': '月支值是命盘事实、集合已登记，归属计算本身无歧义；'
'但该集合是未被采用的表述 F1 的组成部分，在 P-D1 裁定前'
'把它算成「条件满足」即等于预选 F1',
'enters': '不入任何切片；随 P-D1 裁定后由实现批计算',
},
{
'id': 'P5', 'proposition': '戊癸 F1 本局月集的完整形态',
'verdict': 'blocked_by_unresolved_token',
'basis': '「非丙午戌月」之丙解析未审（inv-06）：已解部分只有 '
'[午, 戌]；丙若作月支则不成支名、若作干支复合条件则与句'
'式不齐——该对连 F1 自身的月集都不可完整编码',
'blocker_detail': '解锁路径：他本互校/解析审定（证据工程），'
'若解析终须取舍则升级为 P-D1 的子项；不需要先行用户裁定',
'enters': '不入任何切片；登记於 PENDING_ITEMS B2',
},
{
'id': 'P6', 'proposition': 'F1 妬合字在场',
'verdict': 'fact_ready_as_presence_only',
'basis': '触发字在四柱显干中出现与否是柱面在场事实；但 F1 措辞'
'分两式（D5）：「柱有」为在场、「有X字间之」的「间之」另'
'有居间读法（位于两合干柱位之间），原文未定——在场可算、'
'居间判读未定，两者不得混同',
'enters': '在场面可算；间之解析随 P-D1 或先行审定（B2 同型）',
},
{
'id': 'P7', 'proposition': 'F3 妬化字在场',
'verdict': 'fact_ready_as_presence_only',
'basis': 'smhq.duhua 逐对明列触发字，「见」式为在场语义，无 P6 '
'的居间歧义',
'enters': '在场面可算；效力见 P8',
},
{
'id': 'P8', 'proposition': '阻字效力（妬合/妬化出现 ⇒ 不化）',
'verdict': 'blocked_by_formulation_conflict',
'basis': 'C2：F1 与 F3 的触发字对五对中三对不同（甲己戊/乙、'
'乙庚甲/辛、戊癸己/壬）。采用任一字集作「阻字」即已选边；'
'两集并用（任一出现即阻）或分工（间之归 F1、见归 F3）也'
'都是未登记的组合裁定',
'enters': '不入任何切片；属 P-D1 裁定范围（PENDING_ITEMS B1）',
},
{
'id': 'P9', 'proposition': '有二的事实面（合神/日干重见）',
'verdict': 'fact_ready_as_presence_only',
'basis': '柱面计数是在场事实；但原文「有二则化」只见於甲己句'
'（D1），向他对推广是解释步；且「有二则化」之效本身是'
'成立条件的一部分，随 P13/P-D1',
'enters': '计数可算；效与推广不入切片',
},
{
'id': 'P10', 'proposition': 'F1 附加项在场（受气临官/喜时）',
'verdict': 'fact_ready_as_presence_only',
'basis': '甲己柱有巳亥、戊癸见丁巳、甲己戊辰时，都是支/干支在'
'场事实，逐对引文在册（D2）',
'enters': '在场面可算；其在条件中的权重随 F1 采用与否（P-D1）',
},
{
'id': 'P11', 'proposition': '辰在场（F5/F6 的辰/龙/五事实面）',
'verdict': 'fact_ready_as_presence_only',
'basis': '辰支在场是命盘事实；但 F5/F6 本身未登记（inv-08），'
'「逢龙」与「逢五」指向不同事实形态（C5），事实面可算不'
'等于表述可用',
'enters': '不入任何切片；以 B4 登记为前提',
},
{
'id': 'P12', 'proposition': '旺气（日辰得月中/时上旺气）',
'verdict': 'blocked_by_missing_layers',
'basis': 'F2 的核心要素。旺相休囚框架只有 018-A 的登记文本'
'（三命卷二框架节），全树无可执行的旺气定义；把月支集'
'当旺气是 F1 的列举、不是 F2 的判据（C3）；一般旺衰不'
'存在（TJ-011.2 现状）',
'blocker_detail': 'blocked_by: 旺气可执行定义缺位（与 S4 审定'
'「程度词未阈值化」同型）；随 TJ-011.2 线推进，非本批'
'可解',
'enters': '不入任何切片；登记於 PENDING_ITEMS B3',
},
{
'id': 'P13', 'proposition': '根气/有气（日主无气、化有气）',
'verdict': 'blocked_by_missing_layers',
'basis': 'HX 的核心要素。既有根层只有 root participation 级'
'事实（r018/r019，effect_status 明示 '
'root_participation_only）；「有气/无气」是旺衰与从格层'
'的判断，无已审定义',
'blocker_detail': 'blocked_by: 一般旺衰＋从格 doctrine 层'
'（化格在 product_coverage 为 NOT_BUILT）',
'enters': '不入任何切片；登记於 PENDING_ITEMS B3/B5',
},
{
'id': 'P14', 'proposition': '司令作为合化条件要素',
'verdict': 'registered_absence',
'basis': 'CONDITION_MATRIX commander 行：F1–F6 与 HX 无一以'
'分日司令为要素（F1/F5 用月支集、F2 用旺气、HX 用支组与'
'旺衰）。任务面常见的「司令未扩月 ⇒ 合化受阻」推论不成立'
'——司令试点不是任何合化表述的输入',
'enters': '明示排除：不列为合化阻塞项；司令扩月裁定与合化'
'线无依赖',
},
{
'id': 'P15', 'proposition': '从化象成立（日主从化、化象格）',
'verdict': 'blocked_by_missing_layers',
'basis': 'HX 已登记但其条件（无气/有气、旺者从、类属从化四分）'
'全经旺衰与从格层转手（P13）；且类/属/从/化的分类采用'
'本身是 doctrine 取舍（P-D2）',
'blocker_detail': 'blocked_by: 一般旺衰＋从格层未建；其后另有'
'分类取舍待用户裁定（PENDING_ITEMS B5）',
'enters': '不入任何切片；与 P16 的化气成立严格分开',
},
{
'id': 'P16', 'proposition': '化气成立判定（按任一已登记表述）',
'verdict': 'adjudication_required',
'basis': '四表述并存且真冲突四项（C1–C4）在案，018-C 登记 '
'conflict、adjudication=None。采用哪一表述（或何种组合：'
'如 F1 月集＋F3 妬化、F4 只作旁证）决定同一命盘的不同结'
'论，是流派取舍，只能由用户裁定（P-D1）；F4 另有状态词'
'未归一化问题（成形/发贵等非二值词的读法）随同裁定',
'enters': '永不由审定批代裁；裁定后另批实现（届时 (b) 层要素'
'事实在实现内计算，见 SLICE_DECISION）',
},
{
'id': 'P17', 'proposition': '消费面现状（transformation_status 与'
'格局未决项）',
'verdict': 'consumer_not_unlocked',
'basis': 'inv-12：transformation_status 恒 unresolved、格局 '
'actual_harmony_transformation 列未决、化格 NOT_BUILT。本'
'批是审定批，消费面逐字不变；即使未来 P-D1 裁定，消费面'
'变更也须另批成对审定',
'enters': '现状保持；密封测试钉住 transformation_status 口径',
},
{
'id': 'P18', 'proposition': '任何由合化推出的吉凶/贵贱/成败结论',
'verdict': 'prohibited',
'basis': 'r005 exceptions「不得据五合直接输出感情适配、吉凶或'
'关系评分」＋内容诚实红线；逐月表状态词中的贵贱语（发'
'贵、大贵、贫乏、身贱等）是断语登记，不是事实或结论',
'enters': '永不入任何切片',
},
]

# ------------------------------------------------------------------
# 7. 切片结论：SLICE_SPEC = None（设计裁定）
# ------------------------------------------------------------------

SLICE_SPEC = None

SLICE_DECISION = {
'decision': 'no_fact_layer_slice',
'rationale': [
'与三刑情形对照：三刑组表事实切片成立的前提'
'是「组表事实不存在、且渊海正官组等消费句在等事实层」。合化'
'情形相反：(a) 关系事实已存在且已验证（P1/P2），(b) 条件要素'
'事实是柱面转写（月支值、干支在场与计数、辰在场），任何未来'
'实现都可由命盘事实直接计算，不需要一个先行治理的事实层；'
'且 (b) 中真正不可算的两项（旺气、根气）缺的是定义层、不是'
'事实层。',
'若按某一表述的要素集预建事实层（例如按 F1 月集报「月条件'
'满足」、按某一字集报「阻字在场」），等于把 P-D1 的表述选择'
'预先编码进基础设施——事实层的字段选择本身即裁定。本批拒'
'绝以基础设施预裁定。',
'现行 (a) 层与 doctrine 的口径差（不标示日干参与，P3）是筛选'
'问题而非缺层问题：一行柱位交集即可在实现内解决，为此单独立'
'一个治理切片不成比例（与 S4 审定「零行可建、SLICE_SPEC='
'None」同例）。',
],
'fallback': '若父级评审认为 (b) 层在场事实仍应先行治理，唯一可'
'接受的形态是**表述中立**的原始转写（月支值、各干在场柱位与'
'计数、辰在场），不得含任何表述的月集/阻字集/状态归一化；'
'该形态无现行消费方，本批仍不建议立项。',
'what_this_batch_delivers_instead': '盘点、条件矩阵、冲突结构'
'分析、三层审计与逐项判定、阻塞与待裁定登记——即 P-D1 裁定'
'所需的全部审定材料。',
}

# ------------------------------------------------------------------
# 8. 阻塞与待裁定登记
# ------------------------------------------------------------------

PENDING_ITEMS = [
    {
        'id': 'B1',
        'item': '化气成立条件表述的采用（F1/F2/F3/F4 取舍与组合，'
                '含 C2 阻字字集、C1 月集与 F4 孰从、F4 状态词归'
                '一化读法）',
        'blocked_by': 'formulation_conflict（018-C 登记 conflict、'
                      '真冲突四项 C1–C4）',
        'unlock': '用户级流派裁定后，另批按裁定实现化气判定',
        'needs_user_adjudication': True,
        'pending_decision_id': 'P-D1',
        'note': '本批未呈请具体裁定文本：呈请时应附四表述对同一组'
                '真实命盘的结论对照（本登记的矩阵与冲突分析即其'
                '材料基础）。裁定前 transformation_status 保持 '
                'unresolved',
    },
    {
        'id': 'B2',
        'item': '戊癸条件「丙」字解析（及同型表述内解析未定项，如 '
                'F1「间之」的居间读法）',
        'blocked_by': 'unresolved_token / unresolved_parse（018-C '
                      '在案）',
        'unlock': '他本互校与解析审定批（证据工程）；若终须取舍，'
                  '升级为 P-D1 子项',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B3',
        'item': '旺气与根气/有气可执行定义（F2 与 HX 的核心要素）',
        'blocked_by': 'missing_layers：一般旺衰无已审定义、根层只有'
                      ' participation 级事实（TJ-011.2 线现状）',
        'unlock': '随 TJ-011.2 一般旺衰线与根层审定推进；与合化线'
                  '无先后依赖',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B4',
        'item': '滴天髓《化象》章登记（F5/F6 的证据化）',
        'blocked_by': 'registration_gap：只有审计条目 P05，章内原文'
                      '（原注＋任氏曰）未逐节登记',
        'unlock': '018 式逐节登记批（章界已实测 [98297, 99943)，无'
                  ' PUA 工程负担未测、登记时实测）；登记后 F5/F6 '
                  '才可作引文消费并重审 C5',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B5',
        'item': '从化象 doctrine（类/属/从/化分类与从化成立）',
        'blocked_by': 'missing_layers（B3）＋分类取舍未裁',
        'unlock': 'B3 推进后，分类采用另行呈请用户裁定',
        'needs_user_adjudication': True,
        'pending_decision_id': 'P-D2',
        'note': '与 B1 分开登记：B1 是化气格的条件表述取舍，B5 是'
                '从化象的分类与对象取舍；两者对象不同（D3），不'
                '得合并呈请',
    },
    {
        'id': 'B6',
        'item': '(a) 层口径差：干合事实不标示日干参与',
        'blocked_by': 'nothing_structural（实现细节）',
        'unlock': '随 P-D1 后的实现批在其实现内以柱位交集处理；'
                  '若实现批前有独立消费方需要，再另行审定',
        'needs_user_adjudication': False,
    },
]

ADJUDICATION_POINTS = [
    {
        'id': 'AP1',
        'point': 'SLICE_SPEC 取 None（不出条件要素事实层切片）',
        'ruling': '采「无切片」：关系事实已存在，要素事实是柱面转'
                  '写且无现行消费方，按表述要素集预建事实层会预'
                  '编码未裁定的表述选择。裁定理由与可接受的回退'
                  '形态（表述中立转写）见 SLICE_DECISION',
        'fallback': '若评审否决，工作量只限表述中立转写层（月支值、'
                    '干在场柱位/计数、辰在场），仍不得含月集/阻'
                    '字集/状态归一化；本批盘点与逐项判定全部保留',
        'status': 'adjudicated_by_this_batch_disclosed',
    },
    {
        'id': 'AP2',
        'point': 'C2 定性：妬合/妬化字集差异列为真冲突（而非两个'
                 '和谐并存的机制）',
        'ruling': '定性依据是可编码性而非教义：两说同节同槽位（第'
                  '三干出现则不化），触发字对三对不同，且两对相同'
                  '（丙辛、丁壬）的存在说明两份名单属同一机制家'
                  '族的竞争传述。无论最终读作一机制两传述、还是'
                  '妬合（分位）与妬化（分恋）两机制，编码时都必'
                  '须作选择，故列真冲突；两机制并存的读法已在 '
                  'C2 detail 中并列登记，不因本定性被排除',
        'status': 'adjudicated_by_this_batch_disclosed',
    },
]

STATUS_QUO_LINKAGE = {
    'transformation_status': 'unresolved（bazi_action_conditions，'
                             '有五合/六合/三合时）/ not_present',
    'phase2_unresolved_statements': [
        '五合/六合命中不代表化气成立',
        '半合、拱合、成化条件与吉凶解释未裁定',
    ],
    'hehua_condition_variants_upstream': {
        'register': 'bazi_sanming_juan2_hehua_collation.'
                    'HEHUA_CONDITION_VARIANTS',
        'status': 'conflict',
        'adjudication': None,
    },
    'concept_layer': 'phase1 无合化概念实体（inv-14）；本批不新建',
    'adjudication_semantics_changed': False,
    'relationship': '本审定只在 018-C 登记之上做结构分析与可执行性'
                    '判定：不改 HEHUA_CONDITION_VARIANTS 的任何字段、'
                    '不改 transformation_status、不新建概念、不接'
                    '线。P-D1 裁定前，所有合化消费面逐字不变。',
}

# 本登记所据引文的跨登记引用（不新造引文）：密封测试逐条解析到
# 018-C／018-G 登记并对快照逐字复核。
QUOTE_REFERENCES = [
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.jiaji_cond', 'role': 'f1_condition_jiaji'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.yigeng_cond', 'role': 'f1_condition_yigeng'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.bingxin_cond', 'role': 'f1_condition_bingxin'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.dingren_cond', 'role': 'f1_condition_dingren'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.wugui_cond', 'role': 'f1_condition_wugui'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.jiaji_xi', 'role': 'f1_extra_hour'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.dafan', 'role': 'f2_general_rule'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.erzehua', 'role': 'f3_multiplicity'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhq.duhua', 'role': 'f3_duhua'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhk.header_dingren', 'role': 'f4_table_evidence'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhk.wugui_row_b3', 'role': 'f4_table_evidence'},
    {'register': 'bazi_sanming_juan2_hehua_collation',
     'quote_id': 'smhk.jiaji_row_b3', 'role': 'f4_table_evidence'},
    {'register': 'bazi_sanming_juan6_fangju_baxiang_collation',
     'quote_id': 'hx.definition', 'role': 'hx_definition'},
    {'register': 'bazi_sanming_juan6_fangju_baxiang_collation',
     'quote_id': 'hx.tongxuan', 'role': 'hx_qi_doctrine'},
    {'register': 'bazi_sanming_juan6_fangju_baxiang_collation',
     'quote_id': 'hx.example', 'role': 'hx_worked_example'},
    {'register': 'bazi_sanming_juan6_fangju_baxiang_collation',
     'quote_id': 'hx.jingshan', 'role': 'hx_taxonomy'},
]

# Canonical 钉定（公版文本；密封测试对 phase1 逐字复核）。
SEALED_PINS = [
    {
        'section_id': 'bazi.section.s010',
        'source_id': 'bazi.source.xieji-relations',
        'original_text': '甲与己合乙与庚合丙与辛合丁与壬合戊与癸合',
        'role_in_this_adjudication': '五合名册的 Canonical 锚点'
                                     '（事实层 r005 的 classical '
                                     '出处）；只有名册、无条件',
    },
    {
        'term_id': 'bazi.term.stem_five_combinations',
        'definition': '甲己、乙庚、丙辛、丁壬、戊癸五组天干配对关系；'
                      '本库仅登记结构命中，不自动判断化气是否成立。',
        'role_in_this_adjudication': '术语层明文：名册事实不蕴含'
                                     '化气判定',
    },
    {
        'rule_id': 'bazi.rule.r005',
        'exceptions': ['命中五合不等于化气成立。',
                       '不得据五合直接输出感情适配、吉凶或关系评分。'],
        'role_in_this_adjudication': '事实层规则自带红线：命中≠化成',
    },
]

# 机上实测钉值（2026-10-28，本批；密封测试逐项复核）。
SEALED_MEASUREMENTS = {
# E0329 (TJ-018.3 P1): +1 for the new Canonical section
# bazi.section.s060 (Sanming Lun Sanxing); the section text
# contains none of the HEHUA_KEYWORDS and no 五合 (verified
# in the E0329 sealed run), so the other pins are unchanged.
'phase1_sections_total': 60,
'phase1_sections_with_hehua_keywords': 0,
'phase1_sections_with_wuhe': ['bazi.section.s010'],
'phase1_rules_total': 30,
'phase1_concepts_total': 18,
'phase1_hehua_concepts': 0,
'phase1_concept_ids': [
'bazi.concept.structural_boundary',
'bazi.concept.conflict_spouse_star_lens',
'bazi.concept.conflict_three_punishments',
'bazi.concept.conflict_siling_days',
'bazi.concept.strength_factor_variant_v1',
'bazi.concept.month_command_variant_v1',
'bazi.concept.ditiansui_principal_qi_v1',
'bazi.concept.ditiansui_day_segment_candidates_v1',
'bazi.concept.yuanhai_solar_term_candidates_v1',
'bazi.concept.root_conditions_variant_v1',
'bazi.concept.conflict_root_type_readings',
'bazi.concept.action_conditions_variant_v1',
'bazi.concept.strength_adjudication_v1',
'bazi.concept.principal_month_v1',
'bazi.concept.root_availability_v1',
'bazi.concept.action_effects_v1',
'bazi.concept.bounded_strength_adjudication_v1',
'bazi.concept.pattern_candidates_v1',
],
'phase2_rules_total': 31,
'foundations_stem_combinations': [['甲', '己', '土'],
['乙', '庚', '金'], ['丙', '辛', '水'], ['丁', '壬', '木'],
['戊', '癸', '火']],
'ditiansui_huaxiang_chapter': {'start': 98297, 'end': 99943,
'heading': '十三、化象', 'audit_anchor': 98303},
'snapshot_keyword_counts': {
'ditiansui_chanwei.txt': {'化气': 5, '合化': 19, '化象': 7,
'化格': 2, '妒合': 3},
'yuanhai_ziping.txt': {'化气': 1, '化象': 2, '妒合': 2},
'shenfeng_tongkao.txt': {'化气': 2, '化象': 3, '化格': 3,
'妒合': 4},
'qiongtong_baojian.txt': {'化气': 0, '合化': 0, '化象': 0,
'化格': 1, '妒合': 0},
},
}

ADJUDICATION_LIMITATIONS = [
    'L1 本批是审定批：零实现代码、零运行时接线；合并后任何命盘的'
    '现行事实与裁定输出逐字不变（transformation_status 恒 '
    'unresolved，密封测试钉住）。',
    'L2 本审定的条件命题只以已登记引文（018-C 34 条、018-G 化象 '
    '4 条）与 Canonical 钉定为据；F5/F6（滴天髓化象章）未登记，'
    '本批只登记其条件结构概要、章界实测与缺口，不作引文消费、'
    '不据以判定任何命题的成立面。',
    'L3 渊海/神峰/穷通的合化文本缺口只记录、不在本批新登记：其'
    '快照字样（inv-09/inv-10 计数）未经逐节审读，不得引用为'
    '条件证据；若逐节登记后出现与三命不同的条件表述，按流派'
    '分歧并列登记、不得强行统一（届时另批审定）。',
    'L4 四表述冲突未裁定：HEHUA_CONDITION_VARIANTS 的 conflict '
    '状态与本批的冲突结构分析都不构成采用任何表述的依据；任何'
    '下游不得自本登记摘取某一表述作化气判定（公开测试钉住 '
    'SLICE_SPEC=None 与零接线）。',
    'L5 逐月表（F4）的支组行（寅午戌/亥卯未/申子辰/巳酉丑/辰戌'
    '丑未）是局化陈述，不属干合化气条件面；本批矩阵与冲突分析'
    '只及干对行。局化成立另属 Slice E 面，不在本批。',
    'L6 本批不动 TJ-012.3 的阻塞状态：合化裁定（P-D1）之外，'
    'Slice D 其余前置（一般旺衰、司令扩月等）未清；化气判定'
    '即使获裁定，也只解锁化气一格，不解锁从化象（P-D2/B5）'
    '与任何格局 determination。',
    'L7 (b) 层「在场可算」的命题（P3/P6/P7/P9/P10/P11）只陈述柱'
    '面转写的可计算性，不授权任何模块现在就输出这些要素为'
    '「条件事实」——在 P-D1 裁定前输出它们会造成已选边的外'
    '观（见 SLICE_DECISION）。',
]
