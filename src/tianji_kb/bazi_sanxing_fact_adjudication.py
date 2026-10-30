"""三刑组表事实层设计审定登记（TJ-012.3 审定批：盘点＋设计＋逐项判定）。

DESIGN / ADJUDICATION BATCH。本模块是纯数据审定登记，**零计算逻辑、
零判定代码**：不含任何函数，不被任何可执行路径 import（由公开测试
钉住）。本批只做四件事：(1) 盘点全树已登记来源中的三刑组表材料；
(2) 给出可计算事实的模式设计；(3) 逐项判定每条组表命题的可执行性；
(4) 登记一个窄口径事实层切片规格（SLICE_SPEC）与阻塞清单。实现另批。

背景：Slice D 就绪度复审（tj012-slice-d-readiness §3.1）判定三刑
「文本层已就位（018-B），规则层未动」——Phase2 已执行规则无三刑
（机上实测 phase2_execution.json 全文 punish 命中 0，两处 limitations
明文「三刑存在明确流派分歧，当前不进入统一 executable 规则」），
foundations_v1 支关系表无 punishments 键，bazi_core 的
reviewed_branch_pair_relations 只产 six_harmony/harm/clash 三种事实。
渊海正官组破格侧两句（yh.zg_taboo_xingchong、yh.zg_jia_mixed）在
登记时即注明经「三刑/刑冲破害事实层未建成」转手。本批即该事实层的
设计审定。

盘点结论（全量见 SOURCE_INVENTORY）：全树已登记的三刑组表材料只有
一个原典出处——三命卷二《论三刑》（018-B 校勘续册登记：整节
[71874, 74856)、校勘记 35 条、引文 11 条）。Canonical 侧另有两段
已登记 Section 含刑：渊海 s020「三刑自刑魁罡全，发跡疆场」（断语歌
诀，属消费侧）与滴天髓阐微 s021 刑义批评段（任氏斥机械套刑为俗谬；
其枚举文字与三命总结句逐字同文，构成组表的跨书见证）。神峰、穷通、
滴天髓原注的已登记窗口与 Canonical Section 中**无**三刑组表（机上
phase1 全量扫描：original_text 含「刑」的 Section 恰 s020/s021 两段）。
协纪辨方书结构短引（来源 95）只登记五合/六合/六害/六冲/三合，无刑表。

设计裁定（全量见 FACT_PATTERN_DESIGN 与 DIRECTED_PAIR_TABLE）：
组表按三命总结句的序数立组（一刑子卯、二刑寅巳申、三刑丑戌未），
外加自刑集辰午酉亥；组名（无恩/恃势/无礼）在节内即有正文与
《三车一览》互换两说（018-B 已登记 conflict、不裁定），**事实层不
输出任何组名**，只输出无名组号、成员与方向。有向对按「组内单向
环」建模：数起句的计数链只给一个方向（寅逆至巳、巳逆至申；丑顺
至戌、戌顺至未；子卯互数），反向边不在方案内、不是「缺失的见证」。
8 条环边中 6 条有三命正文枚举引文逐字见证（等级 A），卯刑子有
数起句计数链＋s021 逐字枚举＋018-B 注记所引无礼段正文三重支持
（等级 B，入切片但等级必须随事实输出）；未刑丑在三命侧只存在于
含未决字的残句（校勘记 smxing-anomaly-71984，不入引文），仅有
s021 逐字枚举与「未为刑上」的框架暗示——**不入切片**，
登记为证据缺口（blocked_by_evidence_gap），非流派裁定问题。

可执行性结论（全量见 PROPOSITION_AUDIT）：组员关系、自刑集、
等级 A/B 有向对、三支全/缺一的**在场组态**（仅在场事实、不得读作
刑之成否）可进事实层（纯支关系事实，不经旺衰/裁定转手）；
组名采用被命名冲突阻断（如未来有消费方必须用名，属用户级流派
裁定，本批登记为待裁定项 P-D1，不阻断无名事实切片）；刑上/刑下
是解释框架异文、登记不消费；「三刑要相等」与太过/不及、刑中有制
等程度/效力命题被一般旺衰与制伏效力层缺失阻断；正官破格侧等
消费句即使事实层建成仍被贵命整体判断等其他转手阻断，本切片不
解锁任何 determination；任氏分支依既有概念口径不应用三刑
（not_applied_in_explicit_ren_school），本批不改变该概念的任何
语义（status unresolved、executable_policy
blocked_pending_school_resolution 逐字不变，由密封测试钉住）。

审定点 AP1（本批裁定、随登记披露）：概念 production_policy
「当前不建立统一三刑 executable」所指为统一的**教义性** executable
与前台吉凶输出；本切片是裁决前结构事实层（与六害/六冲事实在
ziping-structural-v1 下的地位相同：bazi_core 自述「stops before
… pattern judgement, auspiciousness」），只报成员/方向/在场，
不报刑名、不报成否、不报吉凶，不建 Phase2 规则、不进
unresolved_interactions、不接任何场景与 AI。若评审对该 policy
作严格解读（结构事实亦在其内），SLICE_SPEC 应降为 None，本批
盘点与设计仍然成立——此降级条件明示在案，不另行请示。

红线：本登记不产生任何三刑判定、吉凶或灾祸结论；事实层只许
支关系事实，不得由刑推灾祸（概念 production_policy 与内容诚实
红线双重在案）。引文政策与 F3/F4 审定同例：本登记不新造引文，
所据引文一律以（登记模块，quote_id）引用既有登记（018-B 引文
11 条、渊海正官组 2 条）；s020/s021 是 Canonical Section 而非
公开登记引文，以 Section 钉定形式登记原文（公版文本，密封测试
对 phase1 逐字复核）。
"""

SANXING_ADJUDICATION_REGISTER = {
'id': 'bazi-sanxing-fact-adjudication-v1',
'task': 'TJ-012.3',
'kind': 'punishment_fact_layer_design_adjudication_register',
'adjudication_batch': '三刑组表事实层设计审定批（审定批，无实现代码）',
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
'main_sha': 'f5d0e6a1d170f123e699c4c748d59adf033b6e2c',
'ledger_events_before': 266,
'ledger_event': 'E0267',
},
'headline_verdicts': {
'group_table_sources': 1,
'group_table_source_note':
'全树已登记组表只有一个原典出处：三命卷二《论三刑》'
'（018-B 登记）；s021 为跨书见证而非独立组表来源'
'（其立场是斥机械套刑为俗谬）。',
'groups': 3,
'self_punishment_branches': 4,
'branch_coverage': '12/12（组员 8 支＋自刑 4 支）',
'cycle_edges_total': 8,
'cycle_edges_grade_a': 6,
'cycle_edges_grade_b': 1,
'cycle_edges_excluded': 1,
'slice_spec': 'sanxing-branch-fact-v1（非 None，窄口径结构事实）',
'implementation_in_this_batch': False,
'naming_adjudicated': False,
'concept_semantics_changed': False,
},
}

# ------------------------------------------------------------------
# 1. 盘点：全树已登记来源中的三刑组表材料（14 项）
# ------------------------------------------------------------------

SOURCE_INVENTORY = [
{
'id': 'inv-01',
'material': '三命卷二《论三刑》整节登记（组表的唯一原典出处）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'src/tianji_kb/bazi_sanming_juan2_sanxing_collation.py'
'（TJ-018-B 校勘记续册，注册表 '
'sanming-juan2-collation-register-v1）',
'locator': 'sanming_tonghui.txt 字符 [71874, 74856)；正文段 '
'[71874, 74035)、《论冲击》子题段 [74035, 74856)',
'counts': {'collation_notes': 35, 'quotes': 11, 'pua': 8, 'fang': 5},
'status': 'registered_evidence',
'note': '整书 quarantine_only、canonical_ready=false 不变；本节经 '
'018-A 同表形制逐条校勘后达到可登记状态。开篇以三合＋方局'
'加位的生成式枚举给出刑关系，总结句立三组序数，数起句给'
'名目依据，自刑定义给四支集合与结构理由。',
},
{
'id': 'inv-02',
'material': '018-B 登记引文 11 条（逐条角色见 QUOTE_REFERENCES）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'bazi_sanming_juan2_sanxing_collation.COLLATION_QUOTES',
'locator': '字符 [71908, 74856) 内 11 处（见各引文 locator）',
'counts': {'quotes': 11,
'group_table_bearing': 5,
'naming_or_variant': 3,
'doctrine': 1,
'subsection_framework': 2},
'status': 'registered_evidence',
'note': '组表承载引文 5 条：sm3.enum_opening（生成式枚举前三组）、'
'sm3.enum_group4_partial（第四组只到亥自刑止）、'
'sm3.summary_groups（三组序数）、sm3.counting_method'
'（计数链与名目依据）、sm3.zixing_definition（自刑定义）。',
},
{
'id': 'inv-03',
'material': '三刑名目异文登记（正文 vs《三车一览》互换＋别解）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'bazi_sanming_juan2_sanxing_collation.'
'SANXING_NAMING_VARIANTS',
'locator': '正文名目见 sm3.counting_method 等；异文 sm3.sanche_variant'
' [73084, 73128)、sm3.houyue_bracket [73982, 74033)',
'counts': {'variants': 2, 'adjudication': None},
'status': 'conflict_registered_unadjudicated',
'note': '正文：无恩=寅巳申、恃势=丑戌未、无礼=子卯、自刑=辰午酉亥；'
'《三车一览》反置无恩/恃势两名（节内自注「其説亦通」）；'
'另立刑上/刑下框架（自注「此説更好」）。无礼与自刑'
'两名在节内无争议。分歧并列登记、不裁定（018-B 在案）。',
},
{
'id': 'inv-04',
'material': '校勘记语境级见证（在节内、未入引文的刑表述）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'bazi_sanming_juan2_sanxing_collation.COLLATION_NOTES'
' 的 context_short 字段',
'locator': '字符 72482（丑恃旺水刑戌中之墓火）、72555（戌恃辛金之势'
'以刑未中之木）、73611（丑刑戌看是何丑何戌）、73633'
'（刑丙戌壬戌）、73836（三刑之位带三奇）、73868'
'（三刑要相等）等',
'counts': {'items_noted': 4},
'status': 'note_context_only_not_quote_registered',
'note': '丑刑戌、戌刑未在定义段正文另有明文（与枚举引文互证，'
'不改变等级 A 的依据构成）；「三刑要相等」是程度命题'
'且只有语境级见证（见命题 P9）；歌赋类断语不入事实层。',
},
{
'id': 'inv-05',
'material': '第四组残句「卯寅子未刑丑」的未决字（组表唯一文本缺口）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': '校勘记 smxing-anomaly-71984（reading=None、'
'reading_status=unresolved）',
'locator': '字符 71984（句在 [71970, 71996) 区间）',
'counts': {'unresolved_glyphs': 1},
'status': 'unresolved_not_quotable',
'note': '「寅」疑衍字或讹字，密封三资产无见证锚点、018-B 未查得'
'外部见证定字；该句不入任何登记引文。未刑丑在三命'
' exposition 侧的唯一文字踪迹即此残句（见命题 P4）。',
},
{
'id': 'inv-06',
'material': '渊海 Canonical Section s020「三刑自刑魁罡全，发跡疆场」',
'source_id': 'bazi.source.yuanhai',
'registered_at': '密封 phase1_knowledge.json Section '
'bazi.section.s020（概念 conflict_three_punishments '
'的 yuanhai-uses-punishment 立场锚点）',
'locator': 'bazi.section.s020',
'counts': {'sections': 1},
'status': 'registered_canonical_section_consumption_side',
'note': '断语歌诀：渊海体系「使用」三刑/自刑作为判断因子的立场'
'证据，本身是贵贱断语，不含组表，不得作事实或结论消费。',
},
{
'id': 'inv-07',
'material': '渊海正官组破格侧忌句两条（经三刑事实层转手）',
'source_id': 'bazi.source.yuanhai',
'registered_at': 'src/tianji_kb/bazi_yuanhai_zhengguan.py'
'（yh.zg_taboo_xingchong、yh.zg_jia_mixed）',
'locator': '《正官论》[9827, 9841)「正官乃贵气之物，大忌刑冲破害」；'
'甲例混合句（最怕刑冲破害、阳刃七杀）',
'counts': {'statements': 2},
'status': 'registered_evidence_consumption_blocked',
'note': '登记时已注明 routed_through_other=三刑/刑冲破害事实层'
'未建成；甲例另经贵命整体判断转手。事实层建成只解除'
'其中一重转手，determination 仍不可执行（见命题 P11）。',
},
{
'id': 'inv-08',
'material': '滴天髓阐微 Canonical Section s021 刑义批评段（跨书见证）',
'source_id': 'bazi.source.ditiansui-spouse',
'registered_at': '密封 phase1_knowledge.json Section '
'bazi.section.s021（概念 ditiansui-rejects-'
'mechanical-punishment 立场锚点；亦为规则 '
'r024/r025/r026 的引用锚点之一，S5 治理文档称'
'「刑义 s021」）',
'locator': 'bazi.section.s021',
'counts': {'sections': 1},
'status': 'registered_canonical_section_rejection_position',
'note': '任氏枚举自刑四支、子刑卯/卯刑子、戌刑未/未刑丑、寅刑巳、'
'寅申相刑并复述总结句「子卯一刑也，寅巳申二刑也，'
'丑戌未三刑也」，随即斥「此皆俗谬，姑置之」。其枚举文字'
'是组表的跨书见证（与三命总结句逐字同文），其立场是'
'任氏分支不采用的依据。见证与立场须分开登记、不得互相'
'抵消：见证可支持「方案含此边」的事实著录，立场决定'
'任氏分支不消费（见命题 P3/P4/P12）。',
},
{
'id': 'inv-09',
'material': '概念 bazi.concept.conflict_three_punishments 及公开镜像',
'source_id': 'cross-source',
'registered_at': '密封 phase1 concept（status unresolved、'
'executable_policy blocked_pending_school_resolution、'
'production_policy「当前不建立统一三刑 executable，'
'不在合盘前台输出“刑=凶”“相刑=关系冲突”等结论」）；'
'公开镜像：bazi_adjudication.py 的 conflict check'
'（unresolved、blocking=False、reason '
'not_applied_in_explicit_ren_school）、'
'bazi_root_conditions.py（punishment_policy '
'not_applied_in_selected_ren_school、'
'punishment_status unresolved）、018-B 的 '
'THREE_PUNISHMENTS_CONCEPT_LINKAGE',
'locator': 'bazi.concept.conflict_three_punishments',
'counts': {'positions': 2},
'status': 'unresolved_non_blocking_for_structure',
'note': '本批不改变该概念的任何字段与语义；事实层与概念的关系'
'见 CONCEPT_LINKAGE 与审定点 AP1。',
},
{
'id': 'inv-10',
'material': '三命卷五杂气/阳刃组消费侧刑冲表述（018-F 登记引文）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'src/tianji_kb/bazi_sanming_juan5_zaqi_yangren_'
'collation.py 登记引文',
'locator': '《论杂气》节题「喜身旺 刑冲忌压伏」、「此格喜透露冲刑'
'忌压伏」、「杂气财官，刑冲则发」；《论阳刃》「不喜'
'刑冲破害」「合刑者㓙」等',
'counts': {'statements': 4},
'status': 'registered_evidence_doctrine_valence',
'note': '同一刑冲事实在杂气语境作「发用」（喜），在正官语境作'
'「大忌」，在阳刃语境作「不喜」——效价随格局语境而反转，'
'证明效价不是事实的属性。属教义消费层，不入事实层'
'（见命题 P13）。',
},
{
'id': 'inv-11',
'material': '协纪辨方书结构短引（来源 95）：无三刑组表',
'source_id': 'bazi.source.xieji (sources[95])',
'registered_at': 'config/knowledge_sources.json sources[95] '
'review_scope',
'locator': '「逐字核对固定 commit 中天干五合、地支六合、六害、'
'六冲与三合结构短段；仅用于结构查表，不据合冲刑害或'
'三合关系输出婚恋吉凶」',
'counts': {'relation_families_registered': 5,
'punishment_tables': 0},
'status': 'registered_absence',
'note': '既有结构事实表（foundations 六合/六害/六冲/三合/方局）'
'的查表来源口径不含刑；刑组表不能从该来源补入。',
},
{
'id': 'inv-12',
'material': '执行面缺位实测（foundations / Phase2 / bazi_core）',
'source_id': 'cross-source',
'registered_at': '机上实测（2026-10-28，本批）：data/canonical/bazi/'
'foundations_v1.json、phase2_execution.json；'
'公开仓 src/tianji_kb/bazi_core.py',
'locator': 'foundations earthly_branch_relations 键恰 '
'{clashes, triple_harmonies, directional_meetings, '
'six_harmonies, harms}；phase2_execution 全文 punish '
'命中 0、三刑命中 2（均为 limitations 排除声明）',
'counts': {'phase2_rules_with_punishment': 0,
'foundation_relation_keys': 5},
'status': 'measured_absence',
'note': 'reviewed_branch_pair_relations 只产 six_harmony/harm/clash；'
'reviewed_relations 与 branch_relations 的输出键无刑事实。'
'本批审定后此现状不变（零运行时接线，由测试钉住）。',
},
{
'id': 'inv-13',
'material': '神峰/穷通/滴天髓原注已登记材料：无三刑组表',
'source_id': 'cross-source',
'registered_at': '机上 phase1 全量扫描（2026-10-28，本批）＋公开仓'
'模块检索（bazi_bingyao.py、bazi_tiaohou.py、'
'bazi_ditiansui_fuyi.py、bazi_siling_matrix.py '
'均无三刑组表）',
'locator': 'phase1 bazi 域 original_text 含「刑」的 Section 恰 '
's020、s021 两段',
'counts': {'sections_with_punishment_text': 2,
'shenfeng_qiongtong_group_tables': 0},
'status': 'measured_absence',
'note': 'bazi_siling_matrix 中的醉醒子段落是分日司令异议、与三刑'
'无关，不计入本盘点。缺口只记录、不在本批新登记大段'
'原文（逐节登记另批）。',
},
{
'id': 'inv-14',
'material': '三命卷五去留组校勘记语境「四柱刑伤害己是也」（018-D）',
'source_id': 'bazi.source.sanmingtonghui',
'registered_at': 'src/tianji_kb/bazi_sanming_juan5_quliu_collation.py'
' 校勘记 context_short',
'locator': '卷五去留组校勘记条目（字符定位见该模块）',
'counts': {'items': 1},
'status': 'note_context_only_not_quote_registered',
'note': '语境级出现、非引文登记、非组表材料；仅作盘点完整性'
'记录，不支持任何事实命题。',
},
]

# ------------------------------------------------------------------
# 2. 组表设计：无名组＋成员＋单向环（事实层只输出结构，不输出组名）
# ------------------------------------------------------------------

GROUP_TABLE = {
'naming_policy': 'fact layer emits NO group names',
'naming_note': '组以三命总结句序数立号（一刑/二刑/三刑是枚举序数，'
'不是无恩/恃势/无礼名目）。名目分配在节内即冲突'
'（inv-03），事实层一律不输出名目字段；名目只在本'
'登记中以「登记状态」形式著录（main_text / '
'sanche_variant 两列并列），供审定与未来裁定引用，'
'不进事实输出契约。',
'groups': [
{
'group_id': 'sanxing-group-1',
'ordinal_label': '一刑',
'members': ['子', '卯'],
'cycle': ['子', '卯'],
'cycle_note': '二支互为环：子→卯与卯→子两边都在方案内'
'（数起句「数自卯顺至子，子逆至卯」双向计数）。',
'naming_registered': {
'main_text': '无礼',
'sanche_variant': None,
'status': 'uncontested_within_section',
},
'evidence_refs': ['sm3.enum_opening', 'sm3.summary_groups',
'sm3.counting_method'],
},
{
'group_id': 'sanxing-group-2',
'ordinal_label': '二刑',
'members': ['寅', '巳', '申'],
'cycle': ['寅', '巳', '申'],
'cycle_note': '单向环 寅→巳→申→寅，三边全有正文枚举见证'
'（等级 A×3），是三组中唯一环闭合且全 A 的组。',
'naming_registered': {
'main_text': '无恩',
'sanche_variant': '恃势',
'status': 'conflict_unadjudicated',
},
'evidence_refs': ['sm3.enum_opening', 'sm3.summary_groups',
'sm3.counting_method', 'sm3.wuen_core'],
},
{
'group_id': 'sanxing-group-3',
'ordinal_label': '三刑',
'members': ['丑', '戌', '未'],
'members_note': '总结句作「丑未戌」、计数/枚举作丑→戌→未；'
'成员集合一致，成员顺序以环序为准。',
'cycle': ['丑', '戌', '未'],
'cycle_note': '单向环 丑→戌→未→丑：前两边等级 A，闭合边'
'未→丑只有等级 C 证据（见 DIRECTED_PAIR_TABLE），'
'不入切片——本组环在事实层呈开口状态，如实输出，'
'不得以环的「应然」补边。',
'naming_registered': {
'main_text': '恃势',
'sanche_variant': '无恩',
'status': 'conflict_unadjudicated',
},
'evidence_refs': ['sm3.enum_opening', 'sm3.summary_groups',
'sm3.counting_method'],
},
],
'self_punishment': {
'set_id': 'sanxing-self',
'members': ['辰', '午', '酉', '亥'],
'definition_basis': 'sm3.zixing_definition：辰午酉亥谓之自刑——'
'寅申巳亥一组内寅巳申互刑而亥无刑、辰戌丑未'
'一组内戌丑未互刑而辰无刑、子午卯酉一组内'
'子卯互刑而午酉无刑，「是以此四位谓之自刑」。'
'自刑集是四支按「同类组内无刑者」定义的结构'
'集合，不是与三组并列的第四组名目。',
'configuration': '同一自刑支在命盘中见于两个或以上柱位'
'（原文「辰见辰自刑」句式）',
'naming_registered': {
'main_text': '自刑',
'sanche_variant': None,
'status': 'uncontested_within_section',
},
'evidence_refs': ['sm3.enum_opening', 'sm3.enum_group4_partial',
'sm3.zixing_definition'],
},
}

# 有向对全表：8 条环边逐条著录见证等级；组内其余 6 条有序对是
# 「非边」（方案本身不含，数起句单向计数为据），与「缺见证」严格
# 区分——非边永不输出，缺见证边（未→丑）登记在案但不入切片。
DIRECTED_PAIR_TABLE = [
{
'actor': '子', 'target': '卯', 'group_id': 'sanxing-group-1',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「子刑卯」',
'evidence_refs': ['sm3.enum_opening', 'sm3.houyue_bracket'],
'in_slice': True,
},
{
'actor': '卯', 'target': '子', 'group_id': 'sanxing-group-1',
'attestation_grade': 'B',
'attestation': '三命数起句计数链「数自卯顺至子」＋阐微 s021 逐字'
'枚举「卯刑子」＋018-B 引文注记所引无礼段正文'
'「所以卯刑子」（该段在已登记节内、文字干净，'
'但未被提升为登记引文）三重支持',
'evidence_refs': ['sm3.counting_method', 'bazi.section.s021'],
'in_slice': True,
'slice_condition': '入切片，但事实输出必须携带 attestation_grade=B，'
'不得与等级 A 混同呈现',
},
{
'actor': '寅', 'target': '巳', 'group_id': 'sanxing-group-2',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「寅刑巳」；无恩核心引文'
' sm3.wuen_core 另给机制释文（寅中甲木刑巳中戊土）',
'evidence_refs': ['sm3.enum_opening', 'sm3.houyue_bracket',
'sm3.wuen_core'],
'in_slice': True,
},
{
'actor': '巳', 'target': '申', 'group_id': 'sanxing-group-2',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「巳刑申」',
'evidence_refs': ['sm3.enum_opening'],
'in_slice': True,
},
{
'actor': '申', 'target': '寅', 'group_id': 'sanxing-group-2',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「申刑寅」（开篇枚举首句）',
'evidence_refs': ['sm3.enum_opening'],
'in_slice': True,
},
{
'actor': '丑', 'target': '戌', 'group_id': 'sanxing-group-3',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「丑刑戌」；定义段正文'
'「丑恃旺水刑戌中之墓火」另有明文（语境级，'
'与引文互证、不改变等级依据构成）',
'evidence_refs': ['sm3.enum_opening', 'sm3.houyue_bracket'],
'in_slice': True,
},
{
'actor': '戌', 'target': '未', 'group_id': 'sanxing-group-3',
'attestation_grade': 'A',
'attestation': '三命正文枚举引文逐字「戌刑未」；定义段正文'
'「戌恃辛金之势以刑未中之木」另有明文（语境级，'
'互证同上）',
'evidence_refs': ['sm3.enum_opening'],
'in_slice': True,
},
{
'actor': '未', 'target': '丑', 'group_id': 'sanxing-group-3',
'attestation_grade': 'C',
'attestation': '三命侧只见于含未决字的残句「卯寅子未刑丑」'
'（smxing-anomaly-71984，不入引文、不可逐字'
'引用）；跨书见证：阐微 s021 逐字枚举「未刑丑」'
'（斥谬语境）；「未为刑上」为框架暗示。'
'三者皆非三命 exposition 的可引明文',
'evidence_refs': ['bazi.section.s021', 'sm3.houyue_bracket'],
'in_slice': False,
'blocker': 'blocked_by_evidence_gap：三命组表原典的可引明文'
'缺位；解锁需先行校勘定字（残句「寅」字）或找到'
'可引见证，属证据工程而非流派裁定（见 PENDING_ITEMS '
'B1）',
},
]

NON_EDGE_REGISTER = {
    'count': 6,
    'pairs': [['巳', '寅'], ['申', '巳'], ['寅', '申'],
              ['戌', '丑'], ['未', '戌'], ['丑', '未']],
    'explanation': '三组组内有序对共 14 条（子卯组 2＋寅巳申组 6＋'
                   '丑戌未组 6）：环边 8 条见 DIRECTED_PAIR_TABLE；'
                   '其余 6 条为非边——方案本身不含（数起句计数链'
                   '只给环向一途，反向无任何陈述），与「未刑丑」'
                   '那种「环边在方案内但见证不足」严格区分：非边'
                   '永不输出、永不登记为缺口。子卯组两条有序对皆'
                   '环边，非边为零。s021「寅申相刑」的对语表述不'
                   '创设反向边寅→申（同段自家枚举用有向形式，'
                   '且其语境是「即冲何必再刑」的斥谬论点）。',
}

COVERAGE_MATRIX = {
'branch_coverage': {
'group_members': ['子', '卯', '寅', '巳', '申', '丑', '戌', '未'],
'self_punishment': ['辰', '午', '酉', '亥'],
'union_count': 12,
'all_branches_covered': True,
'note': '三命方案在组表层面覆盖全部十二支：8 支入三组、4 支入'
'自刑集。覆盖完备性只陈述方案结构，不陈述任何命盘结论。',
},
'edge_coverage': {
'cycle_edges': 8,
'grade_a': 6,
'grade_b': 1,
'grade_c_excluded': 1,
'in_slice': 7,
},
'overlap_with_existing_relations': {
'basis': '机上实测 foundations_v1.json earthly_branch_relations'
'（2026-10-28）：clashes 子午/丑未/寅申/卯酉/辰戌/巳亥；'
'six_harmonies 子丑/寅亥/卯戌/辰酉/巳申/午未；'
'harms 子未/丑午/寅巳/卯辰/申亥/酉戌',
'pair_overlaps': [
{'pair': ['寅', '巳'], 'existing_kind': 'harm',
'note': '寅巳既是六害对，又是等级 A 有向刑边（寅→巳）'},
{'pair': ['巳', '申'], 'existing_kind': 'six_harmony',
'note': '巳申既是六合对（传统化水），又是等级 A 有向刑边'
'（巳→申）——合与刑同对并存，任何一层不得取消另一层'},
{'pair': ['申', '寅'], 'existing_kind': 'clash',
'note': '寅申既是六冲对，又是等级 A 有向刑边（申→寅）；'
's021「寅申相刑，即冲何必再刑」是任氏据此斥刑的'
'论点，属立场而非事实取消'},
],
'pairs_without_existing_relation': [['子', '卯'], ['卯', '子'],
['丑', '戌'], ['戌', '未']],
'group_level_overlaps': [
'sanxing-group-2（寅巳申）内部同时含冲对（寅申）、害对'
'（寅巳）、合对（巳申）各一：组关系与对关系是两个独立'
'维度，组在场不得推定对关系，反之亦然',
'sanxing-group-3（丑戌未）内部含冲对（丑未）：三支全在场时'
'冲事实与组组态事实并存输出、互不抵消',
'刑组与三合局（申子辰/亥卯未/寅午戌/巳酉丑）、方局'
'（寅卯辰等）成员集合 pairwise 皆不相等：刑组不是合局；'
'开篇枚举以三合＋方局加位「生成」刑陈述是教义推演，'
'不是集合等同',
'自刑四支各有既有关系（辰：冲戌/合酉/害卯；午：冲子/害丑/'
'合未；酉：冲卯/合金/害戌；亥：冲巳/合寅/害申），自刑组态'
'与之并存、互不抵消',
],
},
'boundary_with_chong': '冲的机制在同节子题段另有登记（sm3.'
'chong_definition「地支取七位为冲」）：冲是'
'对宫七位关系，刑是组内环向关系，两者在原文'
'中即分属两套框架；事实层沿此分界，kind '
'严格分开、无优先序、无抵消规则。',
}

# ------------------------------------------------------------------
# 3. 事实模式设计：组态类型与边界规则（设计裁定，非实现）
# ------------------------------------------------------------------

FACT_PATTERN_DESIGN = {
'fact_kinds': [
{
'kind': 'directed_pair',
'definition': '两个不同柱位的支恰构成一条入切片环边'
'（actor 支在 actor 柱、target 支在 target 柱）',
'fields': ['actor_branch', 'target_branch', 'actor_pillar',
'target_pillar', 'group_id', 'attestation_grade',
'evidence_refs'],
'note': '同一支对在多柱对出现时逐柱对各报一条；自刑不经'
'本 kind（同支不构成有向对）。',
},
{
'kind': 'group_configuration',
'definition': '一组组员在四柱中的在场组态（纯集合在场事实）',
'fields': ['group_id', 'members', 'present_branches',
'present_pillars', 'present_member_count',
'completeness'],
'completeness_values': {
'full': '三组员全在场（present_member_count=3；子卯组为 2）',
'partial': '三员组恰两员在场',
'single': '仅一员在场',
},
'note': 'completeness 只陈述在场计数：partial 不是「刑不全」'
'的裁定、full 不是「刑成立」的裁定。原文对组态的'
'任何成否读法（如三支全才论刑）属教义层，本层不'
'编码。子卯组无 partial 档（两员即 full）。',
},
{
'kind': 'self_punishment',
'definition': '自刑集成员支在两个或以上柱位出现（「X见X」）',
'fields': ['branch', 'pillars', 'evidence_refs'],
'note': '单柱出现不报（无「见」的关系面）；同支三见/四见'
'仍报一条并列全柱位，不作程度区分。',
},
],
'boundary_rules': [
'kind 隔离：刑事实与既有 clash/six_harmony/harm/triple_harmony/'
'directional_meeting 事实并存输出、互不抵消、互不优先（覆盖'
'矩阵的三条同对重叠为常态而非异常）。',
'组与对隔离：group_configuration 不蕴含 directed_pair（丑、未 '
'两员在场时组组态为 partial 而有向对为零条——这是本'
'设计的判别性组态，实现批 Golden 必须含此例）；反之有向'
'对必同组，但其报告不依赖组组态档。',
'环向-only：只报 DIRECTED_PAIR_TABLE 中 in_slice 的边；非边与'
'等级 C 边在任何输入下永不出现于输出。',
'无名：输出不含无恩/恃势/无礼任何名目字段；group_id 只用'
'序数立号。',
'无价：输出不含吉凶、成否、效价、程度、评分任何字段；'
'present_member_count 是集合计数、不是程度量，字段名与文档'
'必须明示其在场语义（与「不得以计数作裁决依据」的红线不冲突：'
'此计数不喂任何裁决）。',
'柱位保真：柱位以 year/month/day/hour 原样报告，不赋权重、'
'不分主次（与既有结构事实同口径）。',
],
}

# ------------------------------------------------------------------
# 4. 可执行性逐项判定（P1–P14）
# ------------------------------------------------------------------

PROPOSITION_AUDIT = [
{
'id': 'P1', 'proposition': '三组组员关系（子卯／寅巳申／丑戌未）',
'verdict': 'fact_ready',
'basis': 'sm3.enum_opening、sm3.summary_groups、sm3.counting_method '
'三引文互证，成员集合无争议（争议只在名目，见 P7）',
'enters': 'SLICE_SPEC.group_configurations 与 directed_pairs 的 '
'group_id 归属',
},
{
'id': 'P2', 'proposition': '等级 A 有向对 6 条（子→卯、寅→巳、'
'巳→申、申→寅、丑→戌、戌→未）',
'verdict': 'fact_ready',
'basis': '三命正文枚举引文逐字明文（sm3.enum_opening 为主锚，'
'sm3.houyue_bracket 对子→卯/寅→巳/丑→戌同向复述）',
'enters': 'SLICE_SPEC.directed_pairs（grade A）',
},
{
'id': 'P3', 'proposition': '有向对 卯→子',
'verdict': 'fact_ready_with_grade',
'basis': '数起句计数链＋s021 逐字枚举＋无礼段正文（018-B 注记'
'所引）三重支持，但无三命枚举引文逐字明文，等级 B',
'enters': 'SLICE_SPEC.directed_pairs（grade B，等级必须随事实'
'输出、不得与 A 混同）',
},
{
'id': 'P4', 'proposition': '有向对 未→丑（三刑组闭合边）',
'verdict': 'blocked_by_evidence_gap',
'basis': '三命侧唯一文字踪迹在含未决字的残句（inv-05），不可'
'逐字引用；s021 逐字枚举与暗示是跨书/框架级'
'支持，不足以替代组表原典的可引明文',
'blocker_detail': '解锁路径：018 线后续校勘批定字残句「寅」字，'
'或在三命他节/他本找到可引明文后另批提升'
'等级；属证据工程，不是流派裁定，不需要用户'
'裁定',
'enters': '不入切片；登记于 DIRECTED_PAIR_TABLE（grade C、'
'in_slice=False）与 PENDING_ITEMS B1',
},
{
'id': 'P5', 'proposition': '自刑集（辰午酉亥）与「见同支」组态',
'verdict': 'fact_ready',
'basis': 'sm3.zixing_definition 给出集合与结构定义，'
'sm3.enum_opening／sm3.enum_group4_partial 给出四支'
'「见X自刑」的枚举句式',
'enters': 'SLICE_SPEC.self_punishments',
},
{
'id': 'P6', 'proposition': '三支全／缺一的组态区分',
'verdict': 'fact_ready_as_presence_only',
'basis': '组员集合确定后，在场计数是纯集合事实；但原文并未给'
'「缺一不成刑」式成否规则，本层只报在场、不报成否',
'enters': 'SLICE_SPEC.group_configurations.completeness'
'（语义钉死为在场档，见 FACT_PATTERN_DESIGN）',
},
{
'id': 'P7', 'proposition': '组名分配（无恩／恃势／无礼）',
'verdict': 'blocked_by_naming_conflict',
'basis': '节内正文与《三车一览》互换无恩/恃势（inv-03，018-B '
'已登记 conflict、adjudication=None）；任一名字进'
'事实输出即等于替用户选边',
'enters': '不入切片（事实层无名）；如未来消费方必须用名，'
'升级为用户级裁定项 P-D1（见 PENDING_ITEMS）',
},
{
'id': 'P8', 'proposition': '刑上／刑下框架（别解）',
'verdict': 'registered_variant_not_consumed',
'basis': 'sm3.houyue_bracket 已登记为解释框架异文（节内自注'
'「此説更好」）；它是对有向对的上下关系重述，不是'
'新的事实维度，且其取舍与名目问题同属解释层',
'enters': '不入切片；其对子→卯等的同向复述只作 P2 的互证'
'引用',
},
{
'id': 'P9', 'proposition': '程度命题：「三刑要相等」、太过／不及、'
'刑中有制',
'verdict': 'blocked_by_missing_layers',
'basis': '「相等」是旺衰比较（一般旺衰不存在，TJ-011.2 现状）；'
'「有制」是制伏效力（未裁定）；「三刑要相等」本身'
'只有校勘记语境级见证（inv-04）、未入引文',
'blocker_detail': 'blocked_by: 一般旺衰（无阈值定义）＋制伏'
'效力层未建；与 S4 审定「程度词未阈值化」'
'同型红线',
'enters': '不入切片',
},
{
'id': 'P10', 'proposition': '机制与方位教义（无恩释文、方向句、'
'数起法）',
'verdict': 'registered_doctrine_not_fact',
'basis': 'sm3.wuen_core（父妻母的藏干关系释文）、'
'sm3.direction_statement（金位刑在西方等方位陈述）是'
'教义解释；sm3.counting_method 的计数链只作 P3 的'
'见证支持与环向依据，不作事实输出',
'enters': '不入切片（释文不向事实层转写）',
},
{
'id': 'P11', 'proposition': '消费：渊海正官破格侧「大忌刑冲破害」',
'verdict': 'consumer_not_unlocked',
'basis': '该句转手有二：三刑事实层（本切片可供）与贵命整体'
'判断（「皆未为贵命看」，未裁定）；甲例另经制伏效力',
'enters': '事实层只作前置供给；正官格 determination 维持'
'不可裁定（与渊海正官组登记结论一致）',
},
{
'id': 'P12', 'proposition': '消费：任氏分支（三刑不应用）',
'verdict': 'not_applied_by_registered_concept',
'basis': '概念 conflict_three_punishments 口径：任氏显式学派'
'不采用三刑（s021 为立场锚点）；bazi_adjudication '
'与 bazi_root_conditions 的既有处置逐字不变',
'enters': '切片是结构事实层，不改变任何分支的消费口径',
},
{
'id': 'P13', 'proposition': '消费：杂气「刑冲则发」等效价教义',
'verdict': 'doctrine_not_fact',
'basis': 'inv-10：效价随格局语境反转（杂气喜、正官忌、阳刃'
'不喜），是教义判断而非事实属性；且各句分别经身旺'
'等其他条件',
'enters': '不入切片；事实层不携带任何效价',
},
{
'id': 'P14', 'proposition': '任何由刑推出的吉凶／灾祸／贵贱结论',
'verdict': 'prohibited',
'basis': '概念 production_policy（不在前台输出「刑=凶」等结论）'
'＋内容诚实红线（不发明灾祸预测）；s020「发跡疆场」'
'类歌诀是断语而非事实',
'enters': '永不入任何切片；SLICE_SPEC 输出契约以禁用键扫描'
'钉住',
},
]

# ------------------------------------------------------------------
# 5. 切片规格（非 None）：窄口径结构事实层，实现另批
# ------------------------------------------------------------------

SLICE_SPEC = {
    'id': 'sanxing-branch-fact-v1',
    'status': 'design_adjudicated_not_implemented',
    'layer': 'structural_facts（bazi_core 事实族同层，ziping-structural-v1 '
             '的「裁决前」定位：只报结构事实，止于旺衰/格局/吉凶之前）',
    'placement_decision': '独立函数 reviewed_branch_punishment_facts'
                          '（暂名，实现批定名）与既有 '
                          'reviewed_branch_pair_relations 并列；切片一期'
                          '不改写 reviewed_relations / branch_relations '
                          '的既有输出键（避免既有消费面无声变化），是否'
                          '并入其输出另批审定',
    'inputs': {
        'branches': '四支（year/month/day/hour 柱序），每支须为十二支'
                    '成员；非法输入 ValueError（与既有事实函数同口径）',
        'explicit_only': '只接受真实命盘四柱支，不接受调用方自报的'
                         '组态结论',
    },
    'outputs': {
        'directed_pairs': 'FACT_PATTERN_DESIGN.fact_kinds[directed_pair] '
                          '字段集；只含 in_slice 边（A×6＋B×1）；每行'
                          '必带 attestation_grade 与 evidence_refs',
        'group_configurations': '三组中至少一员在场者逐组一行；'
                                'completeness 语义以 FACT_PATTERN_DESIGN '
                                '钉死（在场档，非成否）',
        'self_punishments': '自刑集成员支见于 ≥2 柱位者逐支一行',
        'names': None,
        'naming_status': 'conflict_unresolved_not_emitted',
        'verdict_fields': '无。输出键全集在实现批以白名单钉住；吉凶、'
                          '成否、效价、程度、评分、名目键的出现即'
                          '测试失败',
    },
    'fail_closed': [
        '登记完整性：实现批加载时逐条核验 DIRECTED_PAIR_TABLE 的 '
        'evidence_refs 可解析到登记引文/Section（镜像 siling pilot 的'
        '登记篡改 fail-closed 先例）；核验失败拒绝产出事实、不降级'
        '猜测',
        '等级 C 边与非边在任何输入下不出现于输出（以穷举/对抗用例'
        '钉住：含未、丑两支的盘不得报未→丑；含寅、申的盘只报申→寅'
        '、不得报寅→申）',
        'group partial 组态必须能表达「组在场而有向对为零」（丑未'
        '判别例），不得为凑对而补边',
        '事实层不读旺衰/裁定层任何输出，不因命盘其他条件抑制或'
        '放大事实（刑中有制等程度命题不属本层）',
    ],
    'golden_requirements': [
        '全部用例以真实出生时刻经生产历法链生成四柱，期望手工推导，'
        '严禁手编干支（站立规则）',
        '必含判别例一：仅丑、未两员在场的盘——group_configuration '
        '为 partial 且 directed_pairs 为空（区分组在场与对事实）',
        '必含判别例二：寅、申同盘——只报申→寅（环向-only），且同盘'
        '的 clash 事实在既有函数输出中并存（kind 隔离）',
        '必含判别例三：巳、申同盘——directed_pair 巳→申与既有 '
        'six_harmony 事实并存；寅、巳同盘——寅→巳与 harm 并存',
        '必含：三支全组态（G2 全员、G3 全员各一；G3 全员时只报'
        '丑→戌、戌→未两条，不得补未→丑）、子卯双向对（A/B 两级'
        '同盘呈现）、自刑重见（辰辰）、无任何刑事实的盘（空输出）',
        '必含：现行行为回归——本切片实现前，同一批用例经既有事实'
        '函数不得出现任何刑事实键（实现批落地时改为新函数的'
        '契约用例）',
    ],
    'registration': {
        'evidence_binding': 'pending_phase1_registration'
                            '（与既有研究级 Variant 同口径：材料不足'
                            '保持 pending，不得借用既有 rule id）',
        'sufficient_rule': None,
        'research_only': True,
        'public_enabled': False,
        'ai_enabled': False,
        'scenario_wiring': '不接公开场景；公开投影无新增键',
    },
    'consumption_boundaries': [
        '不建 Phase2 规则、不进 action_effects 的 unresolved_interactions',
        '不改变 bazi.concept.conflict_three_punishments 的任何字段'
        '（含 executable_policy=blocked_pending_school_resolution）',
        '不改变任氏不应用口径、正官破格侧的不可裁定状态、杂气效价'
        '教义的未审状态',
        'AI 不得消费本事实层作任何解释生成（ai_enabled=False）',
    ],
}

# ------------------------------------------------------------------
# 6. 阻塞与待裁定登记
# ------------------------------------------------------------------

PENDING_ITEMS = [
    {
        'id': 'B1',
        'item': '未刑丑的三命可引明文（组表唯一文本缺口）',
        'blocked_by': 'evidence_gap（校勘未决 smxing-anomaly-71984）',
        'unlock': '018 线后续校勘/登记批：残句定字或他节可引明文'
                  '出现后，另批将该边由 C 提升并修订切片',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B2',
        'item': '组名（三刑名目）的采用',
        'blocked_by': 'naming_conflict（三命正文 vs《三车一览》，'
                      '018-B 已登记 conflict）',
        'unlock': '仅当未来有消费方必须输出名目时，才需要裁定',
        'needs_user_adjudication': True,
        'pending_decision_id': 'P-D1',
        'note': '当前无消费方需要名目；事实层无名设计已绕开本项，'
                '本项不阻断切片、不阻断任何既有功能',
    },
    {
        'id': 'B3',
        'item': '程度命题（相等／太过不及／有制）',
        'blocked_by': 'missing_layers：一般旺衰无阈值定义、制伏效力'
                      '未裁定（TJ-011.2 线现状）',
        'unlock': '随一般旺衰与效力层各自的审定推进，与本事实层无'
                  '依赖关系',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B4',
        'item': '教义性消费（正官破格、杂气发用等）',
        'blocked_by': 'missing_layers：贵命整体判断、格局 determination '
                      '其余前置（渊海逐节登记、一般旺衰、合化裁定等，'
                      '见 Slice D 前置表）',
        'unlock': '各消费句逐句成对审定另批；事实层建成不自动解锁',
        'needs_user_adjudication': False,
    },
    {
        'id': 'B5',
        'item': '统一三刑教义 executable',
        'blocked_by': 'concept_policy：blocked_pending_school_resolution'
                      '（流派取舍未决）',
        'unlock': '用户级流派裁定；本批不呈请、不预判',
        'needs_user_adjudication': True,
        'pending_decision_id': 'P-D2',
        'note': '与 B2 分开登记：B2 是名目取舍，B5 是教义采用与否；'
                '两者都不阻断无名结构事实切片',
    },
]

ADJUDICATION_POINTS = [
    {
        'id': 'AP1',
        'point': '结构事实层与概念 production_policy 的相容性',
        'ruling': '采「分层读法」：policy 所禁为统一教义 executable 与'
                  '前台吉凶输出；本切片是裁决前结构事实（与六害/六冲'
                  '事实同层同地位），只报成员/方向/在场，不报刑名、'
                  '成否、吉凶，不建 Phase2 规则、不接场景与 AI，'
                  '故与 policy 相容，SLICE_SPEC 成立',
        'fallback': '若父级评审作严格读法（结构事实亦在 policy 内），'
                    'SLICE_SPEC 降为 None，本批盘点、设计与逐项判定'
                    '全部保留、阻塞清单不变；降级只改本登记的 '
                    'SLICE_SPEC 与台账措辞，不需要重做审定',
        'status': 'adjudicated_by_this_batch_disclosed',
    },
    {
        'id': 'AP2',
        'point': '卯刑子的等级 B 入切片（而非与未刑丑一并排除）',
        'ruling': '分界线取「组表原典（三命）侧文字状态」：卯刑子在'
                  '三命节内有干净文字的三重支持（数起句计数链明文、'
                  '无礼段定义正文、总结句组归属），只是未被提升为'
                  '登记引文；未刑丑的三命文字只存在于含未决字的'
                  '残句。二者证据状态有实质差别，故 B 入、C 不入；'
                  '等级随事实输出使差别对消费方可见',
        'status': 'adjudicated_by_this_batch_disclosed',
    },
]

CONCEPT_LINKAGE = {
    'concept_id': 'bazi.concept.conflict_three_punishments',
    'sealed_status': 'unresolved',
    'executable_policy': 'blocked_pending_school_resolution',
    'production_policy': '当前不建立统一三刑 executable，不在合盘前台'
                         '输出“刑=凶”“相刑=关系冲突”等结论。',
    'public_mirrors_unchanged': [
        'bazi_adjudication.py conflict check（unresolved、'
        'blocking=False、not_applied_in_explicit_ren_school）',
        'bazi_root_conditions.py punishment_policy / punishment_status',
        'bazi_sanming_juan2_sanxing_collation.'
        'THREE_PUNISHMENTS_CONCEPT_LINKAGE（adjudication_semantics_'
        'changed=False）',
    ],
    'adjudication_semantics_changed': False,
    'relationship': '本审定只在概念的「事实供给侧」工作：把三命组表'
                    '设计为可计算的无名结构事实规格。概念的流派冲突'
                    '状态、任氏不应用口径、教义 executable 的阻断'
                    '状态均不因本批改变；事实层实现后亦然（实现批须'
                    '在登记中重申本节）。',
}

# 本登记所据引文的跨登记引用（不新造引文）：密封测试逐条解析到
# 018-B／渊海正官组登记并对快照逐字复核。
QUOTE_REFERENCES = [
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.enum_opening', 'role': 'group_table_primary'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.enum_group4_partial', 'role': 'group_table_group4'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.summary_groups', 'role': 'group_ordinals'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.counting_method', 'role': 'counting_chains_naming_basis'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.wuen_core', 'role': 'mechanism_doctrine'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.zixing_definition', 'role': 'self_punishment_definition'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.sanche_variant', 'role': 'naming_variant_evidence'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.houyue_bracket', 'role': 'framing_variant_evidence'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.direction_statement', 'role': 'direction_doctrine'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.chong_definition', 'role': 'chong_boundary_framework'},
    {'register': 'bazi_sanming_juan2_sanxing_collation',
     'quote_id': 'sm3.polu_poma', 'role': 'subsection_enumeration_evidence'},
    {'register': 'bazi_yuanhai_zhengguan',
     'quote_id': 'yh.zg_taboo_xingchong', 'role': 'consumer_statement'},
    {'register': 'bazi_yuanhai_zhengguan',
     'quote_id': 'yh.zg_jia_mixed', 'role': 'consumer_statement'},
]

# Canonical Section 钉定（公版文本；密封测试对 phase1 逐字复核）。
SEALED_SECTION_PINS = [
    {
        'section_id': 'bazi.section.s020',
        'source_id': 'bazi.source.yuanhai',
        'original_text': '三刑自刑魁罡全,发跡疆场。',
        'role_in_this_adjudication': '渊海「使用」立场锚点；断语歌诀，'
                                     '不作事实消费',
    },
    {
        'section_id': 'bazi.section.s021',
        'source_id': 'bazi.source.ditiansui-spouse',
        'original_text': '刑之义无所取,如亥刑亥、辰刑辰、酉刑酉、午刑午,'
                         '谓之自刑,本支见本支,自谓同气,何以相刑?子刑卯,'
                         '卯刑子,是谓相生,何以相刑?戌刑未,未刑丑,皆为土气,'
                         '更不当刑。寅刑巳,亦是相生,寅申相刑,即冲何必再刑?'
                         '又曰子卯一刑也,寅巳申二刑也,丑戌未三刑也,故称三刑,'
                         '又有自刑,此皆俗谬,姑置之。',
        'role_in_this_adjudication': '任氏「不采用」立场锚点；其枚举文字'
                                     '同时是组表跨书见证（卯刑子等级 B、'
                                     '未刑丑等级 C 的支持之一）——见证与'
                                     '立场分开登记',
    },
]

ADJUDICATION_LIMITATIONS = [
    'L1 本批是审定批：零实现代码、零运行时接线；合并后任何命盘的'
    '现行事实输出逐字不变（密封测试钉住 reviewed_relations / '
    'branch_relations 无刑事实键、概念口径不变）。',
    'L2 本审定的事实命题只以已登记引文与 Canonical Section 为据；'
    '节内未入引文的文字只以校勘记语境级著录（inv-04/inv-14），'
    '不支撑任何入切片命题（「三刑要相等」因此同时被证据等级与'
    '程度层缺失双重阻断）。',
    'L3 未在本批新登记任何大段原文：神峰/穷通他节、三命他节可能'
    '存在的刑表述不在已登记范围内，只记缺口（inv-13），逐节登记'
    '另批；若他节登记后出现与三命组表不同的组表，按流派分歧并列'
    '登记、不得强行统一（届时另批审定）。',
    'L4 组名未裁定：正文与《三车一览》的无恩/恃势互换维持 018-B '
    '的 conflict 登记；任何下游不得自本登记摘取某一列名目作事实'
    '输出（公开测试钉住 GROUP_TABLE 的 naming_policy 与事实层'
    '无名字段）。',
    'L5 未刑丑不入切片是证据裁定而非方案裁定：三命方案的环结构'
    '本身含此边（生成式枚举的平行结构与环的闭合预期均指向它），'
    '本批只是拒绝在原典可引明文出现之前把它写进可执行事实。',
    'L6 事实层即使按 SLICE_SPEC 实现，也只是 Slice D 前置之一：'
    '正官格及其他格局 determination 仍被一般旺衰、制伏效力、'
    '贵命整体判断等独立前置阻断（命题 P11），不得宣称事实层'
    '建成即格局可判。',
    'L7 本批不动 TJ-012.3 的阻塞状态：Slice D 其余前置（司令扩月'
    '裁定、合化裁定等）未清，八格真假（寅月以外）与破格侧仍未审。',
]


# E0333（TJ-018.3 批一：三刑事实执行接入，用户 2026-10-30 授权，
# 设计 docs/product/TJ0183_EXECUTION_BINDING_DESIGN.md §2/§9）对本
# 审定（E0267）的承接记录。本常量为 append-only 追加：SLICE_SPEC
# 原文（含 consumption_boundaries 与 placement_decision）逐字不
# 动；E0267 时点「一期不并入 chart 输出、是否并入另批审定」的决
# 定，已由执行绑定设计批（E0332）完成该「另批审定」并由用户授
# 权本批实施，本记录即该审定链的在案承接，不回改原决定文本。
EXECUTION_BINDING_TAKEOVER = {
    'takeover_event': 'E0333',
    'adjudication_event': 'E0267',
    'design_event': 'E0332',
    'placement': 'tianji_kb.operations.bazi_chart.chart 内关系事实'
                 '块之后、strength_factors 步组之前，以显式门控参数'
                 ' include_punishment_facts（默认 False）接入为已'
                 '注册 Phase2 事实步 '
                 'bazi.phase2.branch_punishment_facts（Phase1 '
                 'bazi.rule.r031）；E0267 placement_decision 的'
                 '「另批审定」即执行绑定设计批，本批为其实施。',
    'gate': 'engine.execute 绑定 allow_research 门禁（非研究模式传'
            '入该参数即拒绝）；公开投影维持既有剥离口径逐字不变。',
    'registration_disposition': 'SLICE_SPEC.registration 原文不'
        '动；实现模块 bazi_sanxing_facts.SLICE_REGISTRATION 的 '
        'evidence_binding 翻转为 registered_phase1_phase2、'
        'phase2_rule 填入 bazi.phase2.branch_punishment_facts、'
        'sufficient_rule 保持 None；治理登记见 '
        'bazi_registration_governance 的 TJ0183_EXECBIND_RECORD '
        '与 sanxing-branch-fact-v1 项。翻转终局条件（正式验收与'
        '部署验证）由父级关账时复核。',
    'consumption_boundaries_takeover': [
        '边界一（不建 Phase2 规则、不进 unresolved_interactions）'
        '由设计批审定承接为：本批新建的 Phase2 步是事实步而非裁'
        '决规则——不产生 RuleMatch、不写入 sufficient_rule、不'
        '进 strength/pattern/adjudication 任何输入、'
        'unresolved_interactions 逐字不变；边界的实质（事实层不'
        '得冒充裁决绑定）由事实步与裁决面的结构分离保持。',
        '边界二（不动 concept 字段）逐字维持：'
        'bazi.concept.conflict_three_punishments 的 sealed_status '
        '与 executable_policy 不变，B2 组名采用与 B5 统一教义 '
        'executable 仍为用户级待裁定。',
        '边界三（不动任氏不应用与破格不可裁定状态）逐字维持：'
        '任氏曰「刑无所取」立场登记与 B4 破格前置状态不变。',
        '边界四（AI 不得消费）逐字维持且加强：开启路径封套强制 '
        'research_only=True、ai_may_explain=False；公开投影剥离'
        '本事实块。',
    ],
}
