# TJ-017.3 分阶段开放第二阶段：独立性复核与开放契约审定（E0374）

## 0 授权与范围

- 授权来源：用户 2026-11-01 分阶段开放裁定的第二阶段——第一阶段（TJ-013.3 喜用可读呈现）已独立验收通过（正式验收 2937、部署与生产实测三项全过，关账 E0373 在册）后，TJ-017.3 大运公开启动；开工必须先复核其是否真正独立于 TJ-017.2 跨规则调用与扶抑 U1/U3：独立部分按已注册证据开放，依赖未完成规则的预测与解释继续保持关闭，不允许为了公开大运而绕过跨规则调用门禁。
- 本批范围：仅复核与审定——产出独立性复核全文与实现批 E0375 的字段级开放契约；不实现任何呈现逻辑、不翻转任何公开开关、不改动任何运行代码。关账预留 E0376。
- 任务定义以 WBS 为准：TJ-017.3 原文行「用户可读时间轴视图 | 允许方法选择与来源；未知/争议交运年份用空态，而不是拟制时间」；TJ-017.2 原文行「原局＋大运＋流年跨规则调用 | 依赖 M2，真实测试需覆盖合冲作用、未判定和相反意见」。两行与本批任务书一致，无冲突。
- 明确不启动（用户同次裁定）：扶抑 U1/U3（暂缓维持）、长生冲突群、siling-yin-pilot、B002、TJ-018.2、TJ-019.2、TJ-028.1、合化 P-D1/P-D2、三刑 B2/B5——本批一概不碰。

## 1 开工核实与基线实测

- GitHub API main HEAD = `562c21f7b2f1cbea2ca9b4cfddb8a363e509950f`（第一阶段关账 PR #546 合并），与任务书基线一致；台账末号 E0373（373 事件）；密封钉 `26b63e64…`（237 文件 / 16,722,816 字节）；正式验收基线 2937（9a672e76）。
- TASK_STATUS 现行行：TJ-017.3「阻塞」，备注记第一阶段研究级视图模型完成（`bazi_dayun_timeline_view` 消费 TJ-017.4 组合结果构造双口径时间轴视图、落点后端研究层不接公开页面、公开投影已加防御剥离），公开开放待「密封 Phase1 注册与分阶段开放裁定」两前置——本批开工时两前置均已解除：密封 Phase1 注册已由 E0346（三命分段）与 E0348（神峰分段）完成，分阶段开放裁定已由用户 2026-11-01 给出并完成第一阶段。TJ-017.2 行「阻塞」，定义与状态未动。
- 视图模块实测（`src/tianji_kb/bazi_dayun_timeline_view.py`，503 行）：纯确定性呈现层，消费 `classical_dayun_timeline`（TJ-017.4）组合结果逐字构造视图——方向块、计数块、时长块、逐运条目（含起始区间逐字复制）、notices、sources（只呈现组合结果实际携带的引文）；恒 `research_only=True、public_enabled=False、ai_enabled=False`，`evidence_binding='inherited_registered_phase1_phase2'`；输入 fail-closed（治理标志被篡改、方向未过自校验、字段缺失或形态不符一律 ValueError）；年龄不呈现（AGE_PRESENTATION='not_presented'）。
- 组合入口实测（`src/tianji_kb/bazi_dayun_compose.py`）：调用链为 四柱（provider 历法）→ `classical_direction`（TJ-017.1，结果随即 `validate_classical_direction` 复算防伪）→ `adjacent_jie_distance`（相邻节实历测量）→ `sanming_convert_measurement` → `candidate_sequence`（月柱邻接序列）→ 按 period_index 与换算交运区间对齐；神峰并列块经 `include_shenfeng=True` 独立给出、永不合并。`traditional_role` 必须显式传入（缺席即拒绝、永不推断）；全链无任何对格局、喜用、旺衰或跨规则模块的调用（见 §2.3）。
- 公开面实测：`public_projection.py` 对 `dayun_timeline_view`、`dayun_timeline_views` 与三注册块 `dayun_classical_direction`、`dayun_sanming_conversion`、`dayun_shenfeng_conversion` 均有防御性剥离；`classical_dayun_timeline` 与视图函数在 src 内无任何生产调用方（仅治理登记引用），组合与视图现为研究层直调入口，未接线任何场景。

## 2 独立性复核

### 2.1 复核方法

逐项盘点 TJ-017.3 的候选公开面，对每一项实测三件事：（a）证据是否已注册（治理登记 `bazi_registration_governance.py` 的 dayun-classical-variants 行与 Canonical/Phase1/Phase2/Golden 实体）；（b）执行依赖是否只落在已注册证据与 provider 历法事实上（读实际代码调用链与门控，不凭文档印象）；（c）结论是否需要 TJ-017.2 跨规则组合（原局×大运×流年作用判断）或旺衰/喜用/效力判断（U1/U3 与未建面）。三项全过判「独立」；任一不过判「依赖未完成规则」或「契约上不存在」，逐项列明依赖点。

### 2.2 证据链实测（注册面）

- 治理登记 dayun-classical-variants 行 disposition = `registered`，两分段齐备：三命分段（E0346）= 方向 Phase1 `bazi.rule.r038`（引文恰 2 条）+ Phase2 `bazi.phase2.dayun_classical_direction`（validated）、三命换算 Phase1 `bazi.rule.r039`（引文恰 8 条，`handover_decade` 以 S3 应用形绑定——逐运交运区间在注册换算范围内）+ Phase2 `bazi.phase2.dayun_sanming_conversion`（validated）、密封 Golden 6 例；神峰分段（E0348）= 换算 Phase1 `bazi.rule.r041`（source_refs 恰为实际消费的 3 条例算引文 sf_ex1/sf_ex3/sf_ex4）+ Phase2 `bazi.phase2.dayun_shenfeng_conversion`（validated）、密封 Golden 5 例。Canonical 实体：三命节 s068/s069/s070 与术语 dayun_direction/dayun_handover、神峰新经典节 s073 与术语 dayun_shenfeng_conversion。
- dayun-compose 与 dayun-timeline-view 两治理行复测：disposition = `maintained_pending`、reason_class = `inherited_pending`，终局形态理由在册（治理恰等不变量：组合/视图层不产生独立规则，复用底层规则 id 即重复计数、新造 id 即空注册；底层全段已注册、本层只继承披露，`evidence_binding` 终局记 `inherited_registered_phase1_phase2`）。**对公开面的含义**：开放是呈现层的定域放行（沿第一阶段先例：新呈现 Variant 承载公开对象、源 Variant 与治理行标志一律不翻转），不以翻转该两行或其 `public_enabled` 标志达成；该两行在本阶段后保持 inherited 终局形态不变。
- 注册 Golden 真实命例（公开治理文档在册、期望手工推导）：Q1 = 1958-08-15T19:30:00+08:00 男命（戊戌/庚申/甲子/甲戌）顺行、三命时长区间 [2840, 2850) 日；Q2 = 1949-01-04T09:30:00+08:00 女命（戊子/甲子/甲午/己巳）逆行、[3340, 3350) 日；Q3/Q4 = 1959-06-15T10:30:00+08:00 同盘（己亥/庚午/戊辰/丁巳）女命顺行 [2730, 2740) 日、男命逆行 [1030, 1040) 日（首运交运区间 [1966-12-05, 1966-12-15) 手算在册）；ADV001 = 2000-02-04T20:40:24+08:00 女命恰逢节 elapsed 0 → unresolved。

### 2.3 执行链实测（为何开放路径是组合+视图、而非 chart 路径）

- 组合链的每一步依赖：四柱与相邻节测量为 provider 历法事实（测量 Variant `bazi-dayun-adjacent-jie-research-v1` 只测实历、非规则裁断）；方向与两换算为已注册函数且方向结果在组合内即经复算自校验；序列为月柱六十甲子邻接的确定性展开（见 §2.4 第 4 项的附带披露）。链上不存在对 TJ-017.2 本体（合冲作用、跨规则裁决）、扶抑、格局、调候、病药或旺衰模块的任何调用——以模块 import 与调用点全域实测为准。
- chart 路径（`operations/bazi_chart.py` 的 `dayun_classical_role` / `dayun_sanming_measurement` / `dayun_shenfeng_measurement` 显式输入声明）不是本阶段的开放路径，两条实测理由：（a）其换算消费的是调用方供入的 measurement 声明而非由出生时刻现算的测量，单凭出生时刻与 role 不能在该路径内产出已注册换算；（b）engine 的 `dayun_jie_distance` 路径在源码内明示「This is NOT a reviewed Dayun Phase2 Rule or classical Evidence... explicitly excluded from RuleMatch」——经该路径拼出的时间线不具注册证据资格。由出生时刻产出注册证据时间线的唯一在册路径是 TJ-017.4 组合入口（其内部执行的正是已注册的方向/换算函数与自校验门）。故 §3 的服务端门裁定走组合+视图，engine 客户端研究门禁逐字不动。
- 人生总览实测（`scenario_engine.py`）：`dayun_timeline_approved` 在组合层两处硬编码 False（integration_provenance 与 integrated_reading），大运维可用性由该旗标派生、reason/exit_text 为 E0362 订正在册文案（明示「尚未批准接入本总览」）；`_life` 以自有输入调用 `_bazi_profile`，从不传 role（与 E0360 的 `_life` 不转发先例同形）。

### 2.4 候选公开面逐项判定

| # | 候选面 | 判定 | 依据与依赖点 |
| --- | --- | --- | --- |
| 1 | 大运方向（顺/逆、计数目标节、方向规则引文） | **独立** | r038 + Phase2 validated + Golden 6 例；只依赖年柱干支与显式 role；结果经复算自校验防伪 |
| 2 | 三命换算（起运时长区间、逐运交运时刻区间） | **独立** | r039（含 handover_decade 绑定）+ Phase2 validated；输入为 provider 历法测量事实；产出恒区间、防舍入为原文禁令 |
| 3 | 神峰换算（时长区间、首运起始区间） | **独立（限首运）** | r041 + Phase2 validated + Golden 5 例；首运区间为组合层导出并在数据内以 derivation 标明；第二运起组合层不提供（not_provided 空态），无可开放之物 |
| 4 | 逐运干支序列与十神事实标签 | **独立（附披露）** | 给定已注册方向后自月柱的六十甲子邻接展开为确定性历法事实；序列模块自身为研究 Variant（`bazi-dayun-month-sequence-research-v1`，其独立「用作大运」口径未审），但在 TJ-017.4 已审组合内行恒为候选行、方向来自已注册 Variant、时间对齐来自已注册换算，且行内 natal_interaction / luck_assessment 恒 None（构造性不存在作用与评价内容）；呈现只限干支/干/支/十神事实标签，序列 Variant id 在证据对象中如实披露 |
| 5 | 方法选择（三命/神峰）与来源呈现 | **独立** | WBS 明文「允许方法选择与来源」；两口径分立呈现、永不合并，为注册分立口径本身 |
| 6 | 人生总览大运维 | **不在本阶段范围（保持关闭）** | 其可用性是人生总览组合层硬编码批准常量，位于 integrated_reading 组合面内（该面另含跨规则审计维）；翻转它是对总览组合的批准决定、非 TJ-017.3 时间轴视图的开放，且 E0362 在册文案明示未批准接入。依赖点：总览组合层批准（与 TJ-017.2 相邻）——本阶段不裁、不翻 |
| 7 | 大运×流年、大运×原局作用判断、岁运效力/吉凶 | **依赖未完成规则（保持关闭）** | 作用判断即 TJ-017.2 跨规则调用本体（未建、依赖 M2）；岁运效力无任何已建规则。组合与视图内此两类内容构造性不存在（恒 None / 零文案），开放面不得新增 |
| 8 | 单点交运日期、起运岁数/年龄数值 | **契约上不存在（禁入）** | 已注册换算只产区间（纲领硬规则：起运精度不足返回区间、不得伪造精确日期）；年龄折算无原典口径（TJ-017.1 审源：虚岁/实岁五书零命中），视图 AGE_PRESENTATION 恒 not_presented |

### 2.5 复核结论

TJ-017.3 的时间轴视图面（第 1–5 项）在证据与执行上真正独立于 TJ-017.2 与 U1/U3：其全部用户可见事实均可追溯到已注册的 r038/r039/r041 与对应 Phase2 步、密封 Golden 及 provider 历法事实，执行链不经任何跨规则或旺衰喜用模块。第 6–8 项不开放：人生总览大运维保持关闭（组合层批准未给）、作用与效力面保持关闭（TJ-017.2 与未建规则）、单点与年龄不存在。§3 起的开放契约只覆盖第 1–5 项。

## 3 呈现面裁定

### 3.1 落点

开放落点为既有场景 `bazi-profile`（八字命理）的场景结果内新对象 `dayun_presentation`（呈现 Variant `dayun-public-presentation-v1`），沿第一阶段定域放行先例：只在 bazi-profile 信封放行、其他场景与端点零放行。不新造场景、不改首页架构、不改 bazi-profile 既有结果的任何既有键。

### 3.2 输入面裁定：新增可选输入 traditional_role（结论 ii）

方向由「年干阴阳 × 传统角色」决定，role 是显式历史分类标签、组合入口强制显式传入（缺席即拒绝）。三案裁定：

- (i) 无需新输入、自洽导出——**否决**，两条独立证据同 E0359 Q2：命盘事实无 role 数据（组合入口明示 never inferred；由日干阴阳反推属虚构映射且与登记的 role_basis 冲突）；出生档案 BirthInput 字段穷举无性别字段，产品内唯一的性别控件经 TJ-031.8 审计确认后端无承接、非档案字段。
- (ii) 新增可选输入——**采纳**：`_bazi_profile` 契约可选集恰新增 `traditional_role` 一键，值域与校验、非 None 才透传的形态同形于合盘 `_compatibility`（已在产）与桃花 `_romance`（E0360）两先例；缺省永不代填；缺席时整块 `dayun_presentation` 缺席（非置空）；role 逐请求使用、不落盘、不进档案 schema、不进 URL。
- (iii) 输入不足、本项收敛——**不取**：在产先例两处齐备、fail-closed 形态可完全复用，输入缺口经 (ii) 即不存在。
- 产品面影响（单独标明，供父级合并审读）：八字命理页新增一个可选控件「传统大运口径（可选）」（缺省未选择、仅已选时发送）与时间轴只读呈现（方法切换三命/神峰），**必须与后端契约在 E0375 同批落地**（TJ-031.8「无承接控件」红线）；文案只作传统定位口径与事实呈现、零解释性文案。相容性：role 不读出生档案、不参与出生值派生、不能绕过 _regionNeedsConfirm 地区确认流程；出生时间输入契约正交不变；`_life` 不转发 role（其调用 `_bazi_profile` 的输入不变），人生总览路径由构造保证无 dayun 呈现（另有 §7 零泄漏钉）。

### 3.3 执行路径裁定（生产开启门）

服务端专属门，沿第一阶段 §3.2 形态落于 `_bazi_profile`：

- 客户端契约：必填 {value}、可选 {strength_variant, zone, traditional_role}（恰增一键）；客户端仍不得命名任何研究键（dayun_classical_role、dayun_sanming_measurement、dayun_shenfeng_measurement、组合/视图键名），engine 客户端研究门禁逐字不变，组合与视图不经 domain 端点到达。
- role 缺席时：门不执行，结果信封与基线逐字等价（组合为独立确定性函数、不经 execute()，无需第一阶段的 scope 双执行守卫；以 G6 深等价钉死）。
- role 在场时：先按先例校验值域（非法即契约错误、计算前拒绝）；服务端以固定常量调用 `classical_dayun_timeline_views(value, zone=zone, traditional_role=role)`——periods=8、birth_time_precision='second'、include_shenfeng=True 均为服务端常量、不可由客户端选择；同一组合结果派生双方法视图后交 §3.4 构建器校验并生成呈现对象。
- fail-closed（沿第一阶段 §3.3 处置）：构建器校验任一不过即整请求失败，不返回缺呈现的部分成功信封；组合自身抛错（恰逢节以外的校验失败）同样整请求失败——恰逢节不是错误、按 §5 空态契约呈现。

### 3.4 构建器裁定

新模块 `src/tianji_kb/bazi_dayun_public.py`，函数 `public_dayun_presentation(sanming_view, shenfeng_view, *, execution)`，Variant `dayun-public-presentation-v1`。execution 恒携带同请求的组合结果（`execution['composition']`），构建器以组合结果为执行记录独立校验两视图（见 §6.2），不信任视图自报。构建器只做投影与校验：不重算方向/换算、不改区间端点、不生成任何视图外文本（范围声明与限制为 §4.4 定稿常量）。

## 4 内容契约（字段级）

### 4.1 顶层对象 dayun_presentation

| 字段 | 形态 |
| --- | --- |
| variant | 恒 `dayun-public-presentation-v1` |
| status | `presented` 或 `unresolved`（镜像组合 status：converted → presented；unresolved → §5 空态） |
| role | {traditional_role, selection}，selection 恒 `explicit_historical_category_not_inferred_identity` |
| methods | {sanming: 方法视图， shenfeng: 方法视图}，两视图派生自同一次组合（同请求） |
| method_options | 视图 method_options 逐字投影：[{id, label, variant, source_id, selectable}] |
| evidence | §4.3 证据对象 |
| scope | §4.4 范围声明（定稿常量） |
| limitations | §4.4 限制（定稿常量） |

### 4.2 方法视图（methods.<method>，自 dayun_timeline_view 输出投影）

- method（sanming/shenfeng）、status（converted/unresolved）、reason（仅 unresolved 时在场，逐字取自组合）。
- natal：{pillars: {year, month, day, hour, day_master}}——视图 natal 的出生回显三字段（input_value、zone、local_datetime）**不投影**（最小化：用户自有输入、呈现无需、隐私卫生）；traditional_role 与 selection 已由顶层 role 承载、不重复。
- direction：{value（forward/backward）, label（顺行/逆行）, counting_target, counted_jie, rule_quote}，逐字投影。
- duration：三命 = {method, variant, status, interval_days, decomposition, counting, approximate, rounding_applied（恒 False）, rounding_policy}；神峰 = {method, variant, status, interval_days, text_result_days, counting: {whole_days, counting_target}, granularity_note, approximate（恒 False）}；unresolved 时附 reason。
- entries[]：{period_index, ganzhi, stem, branch, ten_god_relative_to_natal_day_stem, state, start_interval}；state ∈ interval / unresolved / not_provided；start_interval 在 interval 态为对象、其余态恒 null 并附 start_interval_status 逐字。三命 interval 对象 = {earliest, latest, max_inclusive, basis, method, variant}；神峰首运 interval 对象 = {earliest, latest, max_inclusive, derivation, decade_shifts, method, variant}（derivation 标明组合层导出）。全部端点逐字复制、开闭不变。
- notices[]：{code, text}，封闭集合恰为视图五 notice（methods_presented_separately、zero_jie_boundary、approximate_birth_time、shenfeng_decade_shifts_not_provided、shenfeng_zero_day_count）按视图规则出现者。
- sources[]：{method, role, variant, source_id, quotes}，quotes 为组合结果实际携带的引文对象逐字（三命 direction_rule 块引文 id 恰为 direction_rule 与 vol11_direction_witness、converted 时另有 handover_basis 块；神峰 conversion_examples 块引文 id 恰为 sf_ex1/sf_ex3/sf_ex4）。

### 4.3 证据对象（顶层 evidence，恒带）

- composition_chain：组合 composition_chain 逐字（四 Variant id）。
- rules：恰三条 {phase1_rule_id, phase2_step_id, variant, source_id}——（r038, bazi.phase2.dayun_classical_direction, dayun-direction-classical-v1, bazi.source.sanmingtonghui-applied）、（r039, bazi.phase2.dayun_sanming_conversion, dayun-conversion-sanming-v1, bazi.source.sanmingtonghui-applied）、（r041, bazi.phase2.dayun_shenfeng_conversion, dayun-conversion-shenfeng-v1, bazi.source.shenfeng）。
- sequence_disclosure：{variant: bazi-dayun-month-sequence-research-v1, ten_god_rule_id: bazi.phase2.ten_gods}——序列事实层的出处如实披露（见 §2.4 第 4 项）。
- validation：{direction_self_validated: True, interval_fidelity: 'verbatim_from_composition', quote_sets: 'exact_registered_citation_sets'}——均为构建器在本请求的实际校验结论；任一不成立时构建器抛错而非置 False（§6.2）。

### 4.4 范围声明与限制（定稿语义，E0375 逐字落文并以测试钉住）

- scope 语义：本呈现只包含已注册古典规则算出的大运方向、起运换算与逐运干支序列事实；三命时级与神峰日级为两套分立注册口径、并列呈现、永不合并；交运时间只给出区间。
- 与喜用呈现的关系：`dayun_presentation` 与 `xiyong_presentation` 为相互独立的两个对象，任一不构成对另一的结论；本呈现不含旺衰、喜用、格局或调候/病药结论。
- limitations 语义：不呈现任何年龄数值（古典起运为实历时长、年龄折算无原典口径）；神峰口径逐运起始区间只提供首运、第二运起为空态而非平移拟制；恰逢节时交运时间呈空态；本呈现不是吉凶判断、不预测任何现实事件。

### 4.5 禁入项穷举（公开对象与页面呈现面全域适用）

岁运效力与吉凶/运势评价词；单点交运日期字段与「起运岁数」及任何年龄数值；两口径区间的合并、平均、中点或择一改写；神峰第二运起的十年平移区间；大运与原局/流年的合冲刑害作用判断及一切解释性文案；十神的解释性文案（事实标签本身除外）；扶抑/调候/病药/格局结论（dayun 对象内）；流年叠加呈现；预测语义（官运、财运、婚期、灾祸等）；评分、百分比、指数；由任何身份数据推断 role 的路径；role 的落盘、入 URL、入档案字段。

## 5 暂不可判契约

- 恰逢节（组合 status=unresolved）：顶层 status='unresolved'；方向块照常呈现（方向已注册且已算出）；两方法 duration 呈 unresolved 与 reason 逐字；全部 entries state='unresolved'、start_interval=null；notices 含 zero_jie_boundary。页面语义为「交运时间暂不可判」，不得以任何近似值填充。
- 神峰整日计数为零：三命方法照常 presented；神峰方法 status='unresolved'、附 reason 与 shenfeng_zero_day_count notice；两方法状态独立、互不拖累。
- 神峰第二运起：state='not_provided' 为常态空态（非不可判、非错误），附 shenfeng_decade_shifts_not_provided notice。
- 两口径结果不同：不是冲突态——两套是分立注册约定，按 §4 并列呈现并附 methods_presented_separately notice；页面默认显示三命视图（主注册口径、沿视图默认 method），神峰一键可达；系统不替用户合并或裁定何者为准。
- 出生时刻精度：本阶段 precision 为服务端常量 'second'，approximate 恒 False；若未来开放精度输入须另行审定，本契约不预授权。
- 非法 role、缺 value 等输入错误走既有契约错误路径，不是暂不可判；role 缺席走整块缺席（§3.2），不是置空对象。

## 6 可追溯验收契约

### 6.1 追溯链（每条用户可见事实 → 注册证据 + 同请求执行记录）

- 方向事实 → r038 / `bazi.phase2.dayun_classical_direction` + 方向块 rule_quote（组合结果携带的应用文本引文）；执行记录 = 同请求组合结果的 direction 块，且其自校验（validate_classical_direction 复算）在本请求内已通过（组合入口内建、视图校验复行）。
- 三命换算事实（时长与逐运区间） → r039 / `bazi.phase2.dayun_sanming_conversion` + sources 的 handover_basis 引文（converted 时）；区间端点逐字等于同请求组合结果 sequence_time_alignment 的 start_interval。
- 神峰换算事实 → r041 / `bazi.phase2.dayun_shenfeng_conversion` + sources 的 sf_ex1/sf_ex3/sf_ex4 例算引文；首运区间逐字等于组合并列块 first_period_start_interval 并带 derivation 标明。
- 序列事实 → 月柱邻接展开（sequence_disclosure 披露 Variant）+ 十神标签规则 `bazi.phase2.ten_gods`；条目逐字等于组合 sequence rows 与对齐表（period_index 一一对应）。
- 引文集合恰等：三命方向引文 id 集 {direction_rule, vol11_direction_witness}、神峰引文 id 集 {sf_ex1, sf_ex3, sf_ex4} 为注册引用集，构建器逐一断言，多一少一皆 fail-closed。

### 6.2 构建器校验方法与测试落点（E0375 必须落地）

构建器对两视图与 execution['composition'] 逐项核对，任一不过抛错（整请求 fail-closed）：（a）两视图与组合的 variant 链、治理标志集（research_only=True、public_enabled=False、ai_enabled=False、evidence_binding 终局形态）恰等；（b）两方法的 natal、direction、counting 逐字相等（同一次组合的构造性不变量，跨方法篡改在此检出）；（c）entries 与组合 sequence/alignment 逐行对应、区间端点逐字相等；（d）引文 id 集恰等注册集且引文文本逐字等于组合携带文本；（e）direction 块经 validate_classical_direction 复算通过；（f）投影后对象全域禁入扫描（§4.5 字段名与词表）无命中、且无 age/start_date/end_date 一类单点或年龄字段。
测试落点：公开构建器测试（合成组合/视图输入、纯函数，入公开 CI 按名接入）覆盖投影形态与篡改类；密封伴随测试（真实 bundle、真实出生时刻，只入离线验收、绝不在公开 CI 冒称执行）覆盖 G1–G5 的真实盘期望；场景与 API 测试覆盖 G6/G9/G10。

## 7 门控翻转清单（现状 → 目标态，E0375 逐项落地）

1. `_bazi_profile` 客户端可选集 {strength_variant, zone} → 恰增 traditional_role 一键；其余契约逐字不变。
2. `_bazi_profile` 服务端门：无 dayun 门 → 新增 role 门控的服务端组合+构建器门（§3.3）；role 缺席零执行。
3. public_projection 剥离表：新增 `dayun_presentation` 全域剥离 + 形态校验后的定域放行（仅 bazi-profile 信封、仅第 §4 形态的对象）；既有 dayun 剥离（dayun_timeline_view、dayun_timeline_views、三注册块）逐字不变、继续全域剥离。
4. 新模块 `bazi_dayun_public.py` 与新 Variant `dayun-public-presentation-v1`：无 → 建（呈现层新对象，不注册 Phase1/Phase2 规则）。
5. 源 Variant 与组合/视图治理标志（direction、conversion 三命、conversion 神峰、compose、timeline-view）：research_only=True、public_enabled=False、ai_enabled=False 与 evidence_binding 终局形态——**不翻转、逐字不变**。
6. 治理登记三行（dayun-classical-variants=registered、dayun-compose 与 dayun-timeline-view=inherited 终局形态）：**不变**。
7. engine.execute 客户端研究门禁（dayun_classical_role、dayun_sanming_measurement、dayun_shenfeng_measurement 需 research 模式，及 dayun_jie_distance 等其余大运研究键）：**逐字不变**。
8. `_life` 与人生总览大运维：代码不变、`dayun_timeline_approved` 两处恒 False、E0362 文案不变、`_life` 不转发 role（构造 + 测试钉）。
9. 前端 BaziProfilePage：新增可选控件与时间轴只读呈现（与后端同批）；未选 role 时页面行为逐字不变。
10. validate.yml：新增公开测试按名接入；密封伴随测试不入公开 CI（沿在册分区规则）。

## 8 Golden 判据设计（E0375 落地，真实出生时刻、期望手工推导）

- G1 顺行·三命全形态：1958-08-15T19:30:00+08:00、male → direction=forward/顺行；duration interval_days [2840, 2850)；entries 8 运起始区间逐字等于组合对齐表；sources 引文集恰等；evidence 三规则齐备。
- G2 逆行·女命：1949-01-04T09:30:00+08:00、female → backward/逆行；时长 [3340, 3350)。
- G3 同盘 role 对照：1959-06-15T10:30:00+08:00 同盘，female → forward、[2730, 2740)、首运交运 [1966-12-05, 1966-12-15)；male → backward、[1030, 1040)——证明 role 为输入而非命盘导出。
- G4 神峰方法形态：G1 命例神峰视图——时长与首运区间与已注册神峰期望一致、首运 interval 带 derivation；第 2–8 运 state=not_provided、无区间。
- G5 恰逢节空态：2000-02-04T20:40:24+08:00、female → 顶层 unresolved；方向 backward 在场；全部 entries 无区间；reason 与 notice 逐字。
- G6 role 缺席深等价：真实命例语料（在实现批治理记录中先行登记清单）逐封套与基线深等价、无 dayun_presentation 键。
- G7 禁入扫描：呈现对象与页面文案对 §4.5 词表/字段名全域扫描零命中；无年龄字段、无单点日期字段。
- G8 篡改 fail-closed：区间端点改字、治理标志翻转、引文文本改字、跨方法 natal 不一致四类篡改，构建器逐类抛错且场景无部分信封返回。
- G9 真实 API 对平：POST /api/v1/scenarios/public（bazi-profile + role）返回的 dayun_presentation 与构建器直出逐字一致；其余场景携 traditional_role 键仍按各自契约拒绝（未知键）。
- G10 零泄漏：life/yearly/romance/career 四场景在携 role 尝试下信封与基线逐字不变；全部公开响应（含 bazi-profile）无 dayun_timeline_view、dayun_classical_direction、dayun_sanming_conversion、dayun_shenfeng_conversion 键；人生总览大运维仍 not_available 且文案逐字不变。
- G11 方法切换一致性：同一命例两方法视图的 natal、direction、counting 逐字相等（同一次组合）。

## 9 实现批（E0375）验收清单

1. 契约差异恰为 §3.2/§7 所裁：`_bazi_profile` 可选集恰增 traditional_role 一键、校验同形于合盘/桃花先例；`_life` 与其他场景零改动；engine 门禁零改动。
2. 构建器字段与 §4 逐字对平（键名、取值域、定稿文案、条目行序）；§6.2 六类校验均有测试落点；§5 空态三形态（恰逢节、神峰零日、神峰 not_provided）均有测试落点。
3. 等价比对：role 缺席语料（真实命例清单先行登记于实现批治理记录）新旧两树逐封套深等价、清单外差异 0；role 在场差异严格限于新键 dayun_presentation 与其投影放行。
4. Golden G1–G11 全部落地并通过；公开新专项按名接入 validate.yml，密封伴随专项只入离线验收且如实标注；既有 bazi-profile、人生总览、桃花/合盘 role 相关测试不作修改地通过（若必须改动任何既有断言，停工报告父级，不得放宽）。
5. 机上全配方复跑（scripts/accept_offline.py --suite all）SUCCESS、0 失败：基线为实现批开工时直读的最新正式验收总数（本审定基线 2937），增量逐项对平；本审定不涉密封资产，实现批原则上无换代——若实现中发现密封侧依赖，停工报告。
6. 前端同批落地 §3.2 控件与时间轴呈现，浏览器契约测试按名更新并如实标注 stub/真实性质；控件与呈现文案过 §4.5 禁入自查。
7. 台账：E0375 事件归属 TJ-017.3、状态保持「阻塞」不变（人生总览大运维与跨规则面未开放，本任务不因本阶段关账）；关账批 E0376 在正式验收与部署记录齐备后另行派发，TJ-017.3 行的最终处置由关账批按 WBS 原文逐项对平后决定，本审定不预判。

## 10 仍不可判断范围

- 大运与原局、流年的全部作用判断（合冲刑害、应期、效力）属 TJ-017.2 跨规则调用，未建；本阶段开放不包含、不暗示其任何部分。
- 人生总览大运维保持 not_available：总览组合层批准未给（`dayun_timeline_approved` 恒 False），其开放须另行裁定，不在本阶段。
- 事业财运场景的大运消费（TJ-023.3）不在本阶段，未接线。
- 神峰口径第二运起的起始区间在注册证据内不存在（组合层不导出），本阶段与任何后续阶段均不得以十年平移拟制，除非另有来源经准入链注册。
- 单点交运日期与起运岁数在已注册契约内不存在：换算只产区间、年龄无原典口径；呈现层永不折算。
- TJ-017.3 呈现面以外的扶抑、长生冲突与其余不启动清单九项，状态一律不变。

## 11 本批产出与边界

- 产出：本审定文档（docs/product/TJ0173_STAGED_OPENING_PHASE2.md）、公开治理测试（tests/test_tj0173_staged_opening_phase2.py，已按名接入 validate.yml）、台账事件 E0374 与 TASK_STATUS 的 TJ-017.3 行续写。
- 未实施声明：本批未改动 scenario_engine.py、public_projection.py、engine.py 及任何运行代码，未新增场景输入，未翻转任何 Variant 或治理标志；§3–§8 的全部形态均为对实现批 E0375 的裁定契约，不构成任何已实现能力的主张。

## 12 实现记录（E0375，实现批 append-only 追加）

本节由实现批 E0375 在审定契约（§1–§11）之后追加，只记录实测结果，不改动审定原文任何一句。实现分支 tj0173-phase2-impl-e0375，基线 main ed71b32605682c080dab38e5a5bb4b559a419c8f（审定 PR #547 已合并、台账 374 事件、密封钉 26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329 不变、无密封资产变更、无换代）。

### 12.1 §6.1 五项追溯链答复（逐项：实现位置 + 测试落点）

1. 方向事实 → r038：构建器（src/tianji_kb/bazi_dayun_public.py）自同请求组合结果的 direction 块逐字投影 label/counting_target/counted_jie/rule_quote，并以 validate_classical_direction 在构建时复算（不过即抛错）；evidence.rules 第一条恒为 (bazi.rule.r038, bazi.phase2.dayun_classical_direction, dayun-direction-classical-v1, bazi.source.sanmingtonghui-applied)。测试落点：公开专项 GoldenFormTests（合成组合+真实 classical_direction）与密封专项 RealChainGoldenTests（真实链五例 direction 逐字对平注册 Golden）。
2. 三命换算事实 → r039：duration 与 entries 的 start_interval 逐字取自同请求组合的 sanming_conversion 与 sequence_time_alignment，构建器逐行对平（ganzhi/十神/端点/basis/method/variant），handover_basis 引文（handover_decade）converted 时随 sources 呈现且文本逐字等于组合携带文本。测试落点：密封专项逐例断言 8 运端点、decomposition 与 counting 对平本批 Golden（tests/golden_tj0173_dayun_public.json，期望锚定注册 Golden 并由 3 运扩展至 8 运、手工复核）；篡改类 test_interval_endpoint_altered 钉端点改字必抛错。
3. 神峰换算事实 → r041：duration 逐字取自组合并列块，首运 start_interval 逐字等于 first_period_start_interval 并带 derivation=composition_level_birth_plus_shenfeng_duration_interval 与 decade_shifts=not_provided_for_shenfeng_at_composition_level；二运起条目恒 not_provided（视图派生形态，构建器断言与组合行对平，伪造十年平移在 test_shenfeng_decade_shift_fabricated 钉为抛错）。引文 sf_ex1/sf_ex3/sf_ex4 逐字对平组合携带文本。
4. 序列事实 → 月柱邻接展开 + bazi.phase2.ten_gods：evidence.sequence_disclosure 恒为 {variant: bazi-dayun-month-sequence-research-v1, ten_god_rule_id: bazi.phase2.ten_gods}；条目 ganzhi/stem/branch/十神逐行对平组合 sequence rows 与对齐表（period_index 一一对应，构建器断言）。
5. 引文集合恰等：构建器对每方法 sources 的引文 id 集与注册集逐一断言（三命方向块 {direction_rule, vol11_direction_witness}、converted 另 handover 块 {handover_decade}、神峰块 {sf_ex1, sf_ex3, sf_ex4}），多一少一或文本改字皆抛错；evidence.validation 恒为 {direction_self_validated: True, interval_fidelity: 'verbatim_from_composition', quote_sets: 'exact_registered_citation_sets'}（任一不成立抛错而非置 False）。测试落点：公开专项 test_quote_text_altered、密封专项逐例引文 id 序断言。

### 12.2 §9 验收清单七项逐项结果

1. 契约差异：_bazi_profile 可选集恰增 traditional_role 一键（{strength_variant, zone, traditional_role}）；role 值域在任何计算前校验（非法值 ValueError 先于执行）；role 自 domain execute 输入剥离（engine 的 traditional_role 转发会触发配偶星透镜、改变命盘本体，不属封闭差异清单——剥离后 role 在场与缺席的命盘、xiyong 呈现与信封其余部分逐字一致，由密封 G6 钉住）；_life 与其他场景函数零改动（git diff 仅 _bazi_profile 一处场景函数变更，另加模块级 _dayun_public_gate）；engine 门禁零改动（git diff 不含 engine.py）。
2. 构建器与 §4 逐字对平：顶层键恰八键、方法视图字段集、duration 两形态、entries 三态、notices 封闭五码、scope 两条与 limitations 四条定稿文本均与 §4 一致（父级逐节亲核用）；§6.2 六类校验 (a)–(f) 均有测试落点（公开专项 TamperTests 五测 + 构建器内校验 + BannedContentTests）；§5 空态三形态均有落点：恰逢节（G5 密封+公开合成）、神峰零日（S1 密封+公开合成）、神峰 not_provided（G4 断言）。
3. 等价比对：G6 语料 8 例（清单见 §12.4）role 缺席与 role 在场（剥离新键后）逐封套深等价（密封专项）；新旧两树比对结果见 §12.4。
4. Golden G1–G11 全部落地：G1–G5+神峰零日密封真实链、G6 密封等价、G7 公开禁入扫描、G8 公开篡改类、G9 密封 API 对平、G10 密封四场景、G11 公开+密封两方法一致性；公开新专项 test_tj0173_dayun_public_presentation.py 已按名接入 validate.yml；密封伴随 test_tj0173_dayun_public_sealed.py 只入离线验收、文件头如实标注；既有断言唯一改动 = 审定批自身两处现状钉按 §7 有意更新（test_scenario_contract_and_public_surface_unchanged、test_projection_strip_list_baseline，注释注明依据），其余既有测试不作修改地通过（全配方复跑 0 失败为证）。
5. 机上全配方复跑：见 §12.6（基线、总数、增量逐项对平）；无密封变更、无换代（git diff 不含 data/ 与密封资产路径；机上 cicd 钉复核仍为 26b63e64…）。
6. 前端同批落地：八字页新增可选控件与时间轴只读呈现（默认三命、两口径分立切换、unresolved 呈「交运时间暂不可判」）；Playwright stub 专项 tj0173-dayun-presentation.spec.ts + 专属 workflow 已按名落地，fixture 为组装后真实后端录制的 Q1 真实响应（文件头如实标注 stub 契约性质）；页面文案三处按现状收窄（hero、能力边界卡、说明与限制节），呈现对象与页面文案过 §4.5 禁入自查（公开专项 BannedContentTests 扫描呈现对象；页面呈现节只转写呈现对象字段）。
7. 台账：本批事件 E0375 归属 TJ-017.3、状态「阻塞」不变；TASK_STATUS 仅 TJ-017.3 一行续写；门禁 check_task_tracking.py plain 与 --base ed71b326… 双模式 PASS（实测见 §12.6）。

### 12.3 §7 翻转清单十项实际落地对照

1. _bazi_profile 可选集增 traditional_role：已落地（scenario_engine.py）。
2. 新增服务端门 _dayun_public_gate：已落地——固定常量 periods=8、precision='second'、include_shenfeng=True 调 classical_dayun_timeline 一次 + dayun_timeline_view 两次 + 构建器；role 缺席零执行（门只在 role 在场时调用）。
3. public_projection 新增 dayun_presentation 全域剥离 + 定域放行：已落地——沿第一阶段 xiyong 先例（懒 import is_valid_public_dayun_presentation、容器循环剥离、仅 bazi-profile 的 result 容器校验后回挂逐字对象）；既有五研究键剥离逐字不变。
4. 新模块 bazi_dayun_public.py + Variant dayun-public-presentation-v1：已建。
5. 源 Variant/治理标志不翻转：未动（bazi_dayun_compose.py、bazi_dayun_timeline_view.py、bazi_dayun_classical.py、bazi_dayun_sequence.py 均不在 git diff 内）。
6. 治理登记三行不变：未动（bazi_registration_governance.py 不在 diff 内）。
7. engine 客户端研究门禁逐字不变：未动（engine.py 不在 diff 内）；公开专项 ClientGateTests 钉研究键仍被契约拒绝。
8. _life 与 dayun_timeline_approved 两处恒 False、E0362 文案不变、_life 不转发 role：未动（_life 不在 diff 内）；密封 G10 钉四场景携 role 行为（契约绑定场景拒绝未知键、role 自有场景信封零 dayun 键）与人生总览 limitations 文案逐字在场、旗标全 False。
9. 前端同批落地：已落地（api.ts 输入类型、BaziProfilePage 控件/呈现节/文案收窄、bazi-profile.css 样式）；未选 role 时请求不携带该键（Playwright 专项断言请求体），页面既有行为不变（既有 Playwright 与前端卫生测试不作修改地通过）。
10. validate.yml 按名新增公开测试一行（附注释块）；密封专项不入公开 CI：已落地。

### 12.4 G6 语料清单与等价比对结果

语料（全部真实出生时刻、Asia/Shanghai）：1958-08-15T19:30:00+08:00、1949-01-04T09:30:00+08:00、1959-06-15T10:30:00+08:00、2000-02-04T20:40:24+08:00、1958-09-07T19:30:00+08:00、1975-05-20T08:15:00+08:00、1988-11-02T23:45:00+08:00、2001-02-28T06:00:00+08:00（同登记于 tests/golden_tj0173_dayun_public.json 的 equivalence_corpus）。

等价比对实测（机上双组装树，同一密封快照、同一 runtime 构建）：基线树（ed71b326 组装）与实现树（本批分支组装）各导出 17 个信封——语料 8 例 role 缺席 bazi-profile（strength_variant 在场）+ yearly、romance（缺席与携自有 role 各一）、career、life、compatibility（双 role）、daily、weekly、monthly——逐封套深等价、差异 0；role 在场差异严格限于 bazi-profile 信封 result 内新键 dayun_presentation（密封 G6 钉：同树 role 在场信封剥离新键后与 role 缺席信封逐字相等，语料 8 例 × 双 role 全过）。


### 12.5 前端新增可选控件的用户呈报事项

八字命理页出生资料表单内新增可选控件「传统大运口径（可选）」（下拉：不启用/传统男命口径/传统女命口径），同合盘/桃花既有 role 控件先例：缺省未选择、仅用户显式选择时随本次计算请求发送 traditional_role、不写入出生资料档案、不进 URL、逐请求不落盘；未选择时不呈现大运时间轴、页面行为与此前逐字一致。说明小字：「只用于按传统口径呈现大运方向与交运区间；不选择时不呈现大运时间轴。该选择只随本次计算发送，不保存。」本事项随实现批 PR 呈报用户，沿 E0360 先例留否决口：用户若反对，撤下该控件即可（后端门控以 role 缺席为缺省安全态，撤控件不影响其余部分）。

### 12.6 验收数字

基线（开工三核实直读）：main HEAD ed71b32605682c080dab38e5a5bb4b559a419c8f、台账末号 E0374、机上 cicd 钉 26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329；管线对 ed71b326 的正式验收 SUCCESS 总数 2945（public-git-checkout 15 + public-only 24 + private-backend 2906，证据 acceptance-ed71b32605682c080dab38e5a5bb4b559a419c8f.json），即审定基线 2937 + 审定批 8 公开测。
机上全配方复跑（scripts/accept_offline.py --suite all，密封快照同钉）：复跑树 d5c648b65e0b5b3311d2c8b05070897b68be3bc8 与 PR 头的全部代码、测试与前端内容逐字一致（PR 头仅在此基础上追加本治理记录与台账三文件，该三文件的专项测试与台账门禁已在本批实跑 PASS，见本节末）——SUCCESS、0 失败 0 错误，总数 2978（15 + 24 + private-backend 2939）。增量 +33 逐项对平：新增公开专项 test_tj0173_dayun_public_presentation 21 测 + 密封专项 test_tj0173_dayun_public_sealed 12 测，均落 private-backend 分区；审定批公开测按 §7 更新后仍 8 测、净增 0；private-backend skipped 5 → 6（+1 为公开专项的前端源码守卫测在组装树无 web/ 时按 E0359 先例跳过，本机与公开 CI 均实跑通过）。Playwright 专项本地实跑 2/2 通过（fixture 为本批组装树真实后端录制），第一阶段 Playwright 专项同页回归 2/2 通过。台账门禁：scripts/check_task_tracking.py plain 与 --base ed71b32605682c080dab38e5a5bb4b559a419c8f 双模式 PASS（375 事件、PR change 恰 TJ-017.3 一行）。本批止于 PR，不自行合并；正式验收与部署由管线在合并后产生，关账 E0376 另行对平。

## 13 关账（E0376，2026-11-02，append-only 追加）

本节由关账批 E0376 追加，§0–§12 原文一字未动。关账基线：实现 PR #548 已合并，Merge SHA `e893bc2005cfbc1cd4235f114804e393bf76442d`，台账 375 事件；本节逐项消费 §9 第 7 项预留的关账对平（正式验收、部署记录、生产实测、行状态处置）。

### 13.1 合并与公开 CI

- PR #548 于 2026-11-01T17:45:40Z 合并，Merge SHA `e893bc2005cfbc1cd4235f114804e393bf76442d`（本批开工经 API 复核 main HEAD 与 PR merged 状态一致，PR 头 `71923b8e972d590278733564f6bc67ab49331282`）。
- 公开 CI：合并提交的 check runs 共 20 项，19 success + 1 skipped、0 failure（run 41333111242）。

### 13.2 正式验收终局核对

- 部署管线正式验收记录 `acceptance-e893bc2005cfbc1cd4235f114804e393bf76442d.json`（机上 deployment-evidence/tj-core-01 直读）：**SUCCESS**，`total_tests_run = 2978`、`total_skipped = 7`、failures/errors 均为 0；分项 = public-git-checkout 15（skipped 0）+ public-only 24（skipped 1）+ private-backend 2939（skipped 6、261 模块）。
- 对平：正式基线 2945（`ed71b326`，15 + 24 + 2906、skip 5）+ 33 = 2978，与 §12.6 实现批复跑逐项一致（新增公开专项 21 测 + 密封专项 12 测均落 private-backend 分区，2906 → 2939；private-backend skipped 5 → 6，增量恰为公开专项前端源码守卫测在组装树无 web/ 时按 E0359 先例跳过）。
- 密封口径未动：验收记录内 `knowledge_file_count = 237`、`knowledge_total_bytes = 16722816`、`knowledge_manifest_sha256 = 26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`，机上 cicd 钉复核同值，无换代。

### 13.3 部署终局核对

- `deploys.log`：ACCEPTED 2026-11-01T18:06:17Z；**DEPLOYED 2026-11-01T18:06:47Z**，image `tianji-api:cicd-prerelease-e893bc20`、web `ghcr.io/hellomrduan/tianji-web:e893bc2005cfbc1cd4235f114804e393bf76442d`、health+bazi ok、port 8080、pin `3e5d801089a90a25d73e4aa63db345d46964d37bffa63c938d43beeea55af615`。
- pin 口径说明（防误读，沿 E0373 先例）：deploys.log 的 pin 为部署 bundle 钉，本批因 src 变更（新构建器、服务端门、投影放行）由前值 `d9cbbf03…` 变为 `3e5d8010…`；密封知识清单钉仍为 `26b63e64…`（§13.2），两钉不混同。

### 13.4 生产实测（第二阶段独立验收）

- 方法：部署完成后，经机上生产服务（127.0.0.1:8080，即部署管线同源核验的生产实例）真实调用 `POST /api/v1/scenarios/public`，探针脚本 `prod_probe_e0376.py` 与输出 `prod_probe_e0376_out.json` 留机上 `/data/workspace/`；共 59 项断言，**全部通过**（含 /health rag_ready）。出生时刻均为在册 Golden 公开例。断言口径按公开投影后形态设定（沿 E0373 教训）：`dayun_presentation` 为定域放行后逐字保留的呈现对象、其内 id 为 §4 契约内容，trace/rule_matches 通道的匿名化不属本阶段改动面，未按场景层口径断言。
- (a) G1 盘（1958-08-15T19:30:00+08:00、traditional_role=male）：HTTP 200，`result.dayun_presentation` 在位；顶层恰八键、variant = `dayun-public-presentation-v1`、status = presented、role 块逐字（selection 恒 explicit_historical_category_not_inferred_identity）；方向 forward/顺行、counting_target = future_jie、counted_jie = 白露、natal 四柱（戊戌/庚申/甲子/甲戌、甲）与 Golden 逐字一致；三命 duration interval_days = [2840, 2850)（max_inclusive False）、8 运条目（干支、十神、起止区间端点）与 Golden 逐字全等、state 恒 interval；两方法 natal 与 direction 逐字相等（G11 形态）。
- (a) 续·两口径分立与证据对象：神峰 duration interval_days = [2760, 2880)、text_result_days = 2760；首运 start_interval = [1966-03-06T19:30:00+08:00, 1966-07-04T19:30:00+08:00) 且 derivation = composition_level_birth_plus_shenfeng_duration_interval、decade_shifts = not_provided_for_shenfeng_at_composition_level 逐字在位；notices 恰为三命 {methods_presented_separately}、神峰 {methods_presented_separately, shenfeng_decade_shifts_not_provided}；evidence.rules 恰三条 (r038, bazi.phase2.dayun_classical_direction)、(r039, bazi.phase2.dayun_sanming_conversion)、(r041, bazi.phase2.dayun_shenfeng_conversion)，sequence_disclosure = {variant: bazi-dayun-month-sequence-research-v1, ten_god_rule_id: bazi.phase2.ten_gods}、validation 三项逐字、composition_chain 恰四 Variant（dayun-direction-classical-v1、bazi-dayun-adjacent-jie-research-v1、dayun-conversion-sanming-v1、bazi-dayun-month-sequence-research-v1）；引文 id 集恰等（三命 {direction_rule, vol11_direction_witness, handover_decade}、神峰 {sf_ex1, sf_ex3, sf_ex4}）；scope 两条与 limitations 四条与构建器定稿常量逐字一致；method_options 两口径 selectable 恒 True。每条用户可见事实均可回溯至上述注册证据与同请求组合执行记录（composition_chain 与 validation 为同请求校验结论）。
- (b) 同盘不带 role：HTTP 200，`dayun_presentation` 整块缺席；将 (a) 响应全域剥除该键后与本响应逐叶深等价（差异 0）——role 缺席路径与基线逐字一致的生产面复核。
- (c) 空态两形态：神峰第二运起（(a) 内）entries 2–8 恒 state = not_provided、start_interval = null；G5 恰逢节盘（2000-02-04T20:40:24+08:00、female）顶层 status = unresolved、方向 backward 照常呈现、两方法 duration 均 unresolved 且 reason 逐字（三命 zero_jie_boundary_convention_unreviewed、神峰 zero_day_count_not_exemplified_in_text）、8 运条目恒 unresolved 且无区间、干支序列与 Golden 逐字一致、两方法 notices 均含 zero_jie_boundary。
- (d) 零泄漏全量扫描：四份响应（(a)/(b)/(c) 与 life）全域键扫描——研究键 dayun_timeline_view、dayun_timeline_views、dayun_classical_direction、dayun_sanming_conversion、dayun_shenfeng_conversion 零出现（evidence.rules 内的 phase2_step_id 为 §4.3 契约值、非键泄漏）；作用键 natal_interaction、luck_assessment 零出现；(a)/(b)/(c) 含 fuyi、useful_god、strength 子串的键零出现；两份呈现对象内无 age 类与 start_date/end_date 单点字段。`life` 响应（同 G1 盘、target_year 2026）：无 dayun_presentation 键；dayun_timeline_approved 共 3 处、全 False；condition_markers 的 dayun_timeline 维 condition = not_available、reason 与 exit_text 与 E0362 订正文案逐字一致，integrated_reading.dayun 同文逐字在位——人生总览大运维文案与旗标逐字不变。

### 13.5 WBS 验收口径对平与行状态处置

- WBS 原文实测：TJ-017.3 =「用户可读时间轴视图」，验收口径 =「允许方法选择与来源；未知/争议交运年份用空态，而不是拟制时间」；任务分界同表实测——跨规则调用属 TJ-017.2（「原局＋大运＋流年跨规则调用」）、组合与序列对齐属 TJ-017.4（明示「与 TJ-017.3 显示面无涉」的反向分界），人生总览大运维属总览组合层批准面（E0362 文案在册、本阶段 §2.4 第 6 项判不在本阶段范围）。
- 逐条对平：(1) 用户可读时间轴视图——bazi-profile 定域 `dayun_presentation` 只读时间轴已部署，§13.4 (a) 生产实测真实可达（用户显式选择传统口径后呈现实测全形态，缺席整块缺席）；(2) 允许方法选择与来源——method_options 两口径并列可选（默认三命、神峰一键可达），sources 引文逐字随呈现、evidence 三规则齐备，§13.4 (a) 已逐项核实；(3) 未知/争议交运年份用空态而不是拟制时间——恰逢节 unresolved（§13.4 (c) 生产实测）、神峰零日 unresolved、神峰二运起 not_provided，全程无单点交运日期、无年龄数值、无十年平移区间（§13.4 (d) 扫描佐证）。三条口径在本阶段审定范围（§2.4 第 1–5 项）内全部成立。
- 余项判定：§2.4 第 6–8 项不属本行本体——第 6 项人生总览大运维是总览组合层的批准决定（§13.4 (d) 已核实其保持关闭、文案与旗标不变，其开放须另行裁定）；第 7 项作用与岁运效力是 TJ-017.2 本体与未建规则；第 8 项单点与年龄在已注册契约内不存在。三者均不构成 TJ-017.3 的未清余项。与第一阶段 E0373 处置的区别：TJ-013.3 的本体建成面含四对象、本阶段只开放其二，未开放段各有本行内未清前置，故行保持阻塞；TJ-017.3 的本体口径与本阶段开放面恰等，无本行内余面。行备注历史亦印证：研究级视图本体已于 E0220 关账，此后保持阻塞的唯一原因是「公开开放待分阶段开放裁定」——该裁定已经用户作出、本阶段已执行并经正式验收与生产实测独立核实。
- **行状态处置：TJ-017.3 关账为「已部署验收」**（E0376 事件状态与 TASK_STATUS 行状态均据此填写）。本结论与 §13.6 的第二阶段子项关闭结论分别表述、依据不同：子项关闭是分阶段开放第二阶段工作项的阶段结论，行关账是 WBS 本行口径逐条对平的结论，二者分别成立。
- 状态钉转换（如实记录）：审定批公开治理测试 `test_tj0173_staged_opening_phase2.py` 的台账断言含 TJ-017.3 行状态钉「阻塞」（审定时点形态）；本批行关账使该钉按状态转换先例（同 E0360 契约钉转换形态）在本 PR 内同步转换为「已部署验收」，测试内注释注明依据（审定 §9 第 7 项将行最终处置留待关账批决定、§13.5 本节对平结论），其余断言逐字未动；该测试其余 7 测与本批全部公开测试在 PR CI 的处理见合并记录。

### 13.6 第二阶段关闭结论与分阶段开放两阶段总收束

- **分阶段开放第二阶段（TJ-017.3 大运公开，范围严格限于独立性复核判独立的五面）关闭**：审定 E0374 → 实现 E0375 → 合并 #548 → 正式验收 SUCCESS 2978 → 部署（bundle pin `3e5d8010…`、密封清单钉 `26b63e64…` 不变）→ 生产实测 59 项全过。普通用户现已能在八字页（显式选择传统大运口径后）看到有证据（方向、换算、序列逐条可回溯 r038/r039/r041 注册证据与同请求组合执行记录）、有边界（范围声明与限制随呈现同出、不含年龄、单点日期与作用判断）、能解释（两套注册口径分立并列、来源引文逐字、未知与争议以空态如实呈现）的大运时间轴；恰逢节等暂不可判形态按契约呈空态，无任何拟制填充；未修改底层裁决规则、未翻转任何源 Variant 与治理标志、未解锁扶抑 U1/U3、未绕过 TJ-017.2 跨规则门禁（作用面在呈现内构造性不存在）。
- **两阶段总收束**：用户 2026-11-01 裁定的分阶段开放两阶段均已执行并各自独立验收完毕——第一阶段 TJ-013.3 喜用可读呈现（调候 + 病药，E0373 关账）与第二阶段 TJ-017.3 大运公开（本关账），普通用户已实际获得两面有证据、有边界、能解释的结果呈现，均为呈现层定域放行、证据绑定、fail-closed，不动底层裁决。两阶段之外保持关闭且状态不变的面：扶抑 U1/U3（用户暂缓维持）、TJ-017.2 跨规则调用（未建）、人生总览大运维（组合层批准未给）、TJ-013.3 旺衰段与冲突段（其行保持阻塞）、长生冲突群（未裁）、siling-yin-pilot 扩月、B002、TJ-018.2、TJ-019.2、TJ-028.1、合化 P-D1/P-D2、三刑 B2/B5 等不启动清单各项；后续任何开放须另行裁定，本关账不预判。
- 用户否决面：§12.5 前端新增可选控件「传统大运口径（可选）」已随实现批与本关账向用户呈报，沿 E0360 先例留否决口（后端门控以 role 缺席为缺省安全态，撤下控件不影响其余部分）；本关账不另设否决项。

### 13.7 机上清理与环境记录

- 清理：机上未见实现批专属组装/暂存目录（实现批复跑位于部署管线托管的检出与组装面内，`platform-deploy` 为部署代理自有目录、不在本批清理范围）；本批探针脚本与输出（`prod_probe_e0376.py`、`prod_probe_e0376_out.json`）及管线等待日志（`wait_accept_e0376.log`）按先例保留于机上 `/data/workspace/`；核实时 /data 已用 38%、余 13G。
- 环境记录：本批等待管线期间发生一次 VM 替换，本机 `/root/.ssh` 被清空、SSH 一度被出口代理 reset，且本机 /tmp 内首版探针脚本随替换丢失；已按 AGENTS.md 在册程序自 `~/.ssh/config` 还原 `/root/.ssh/config` 并核对网关指纹 `SHA256:DQYkbhc9iBYcfVvhXZBsT9qhzAyLvLIyjmm57Vimfxk` 逐字一致后恢复，探针已于 `~/workspace` 持久路径重写（断言与期望未变）并复跑全过；机上部署管线、验收进程与等待脚本未受影响（验收文件由机上等待脚本记录落盘），本节全部数字均以恢复后前台直读为准。
- 本批止于 PR，未自行合并；合并由父级执行。
