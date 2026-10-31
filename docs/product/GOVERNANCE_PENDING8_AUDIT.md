# 治理登记维持 pending 8 项解锁条件审计

- 审计对象：`src/tianji_kb/bazi_registration_governance.py` 的 `REGISTRATION_INVENTORY` 中 `disposition = maintained_pending` 的全部条目（S5 治理登记，批号 TJ-011.2 S5，事件 E0254）。
- 基线：公开仓 main `32ae7664f5e344448082c0a01417e9b4b6213aab`（B-2 关账 PR #517 合并后），台账 340 事件（末号 E0340）；密封快照 manifest `15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5`（237 文件 / 16,001,603 字节）。
- 本批性质：**只审计、不实施**。不改代码、不改密封、不翻转任何注册；本文档为下一阶段选批的依据。

## 0. 审计范围与方法

1. 名单与计数一律从治理登记代码实测读出（`REGISTRATION_INVENTORY` 逐行 `disposition` 字段、`FLIPPED_ITEMS` / `MAINTAINED_ITEMS` 的代码定义），不引用任何既有文档的转述数字；与任务书预期对平后才进入逐项审计。
2. 逐项审计的每条结论须有文件级、节级或规则级证据：公开仓侧读披露站点模块的登记结构（引文条数、locator、`source_section_id` 有无、执行形态）；密封侧在可信机上直读快照 `data/canonical/bazi/phase1_knowledge.json` 的结构字段（经典清单、节数、规则数）与节文本子串在位检查；三命正式应用文本 S3（`sanming_tonghui_applied_v1.txt`，461,156 字）逐字定位相关引文；隔离区四快照以文件字节实算 SHA256 与登记值对平。
3. 缺口性质只用登记册既有 `reason_class` 词表（`canonical_evidence_absent` / `execution_binding_structure` / `inherited_pending`）加复合标注，不新造类别。
4. 「可补形态」只许引用已实证先例：批二/B-2 的 S3 建节+引文绑定、批一的 chart 门控 trace 接入、B-2 的路线 trace 接入翻转、B-1 的 018 形制纯登记。无先例的形态（如新建 Canonical 经典）如实标注「无直接先例」。
5. 凡解锁路径牵涉用户级裁定的，逐项标明裁定事项与在册状态，不代决、不以工程手段绕行。

## 1. 名单核实（代码实测）

`REGISTRATION_INVENTORY` 共 **18 行**：`registered` 7 行、`maintained_pending` **8 行**、`not_a_candidate` 3 行。已翻转 7 项为 pure_generating_support、commanding_visible_support、lu_visible_support、pure_support_metal、pure_generating_support_water、pattern-route-luren、sanxing-branch-fact-v1（与批一、批二、B-2 的翻转记录逐项对平）。维持 pending 8 项与任务书预期**恰合**，名单如下（`reason_class` 为登记册原文分类）：

| # | item | 对象 | reason_class |
|---|---|---|---|
| 1 | tiaohou-qiongtong-v1 | 调候 Variant（穷通宝鉴 119 条） | canonical_evidence_absent |
| 2 | dayun-classical-variants | 大运古典三 Variant（direction-classical / conversion-sanming / conversion-shenfeng） | canonical_evidence_absent |
| 3 | dayun-compose | 大运组合入口 classical_dayun_timeline | inherited_pending |
| 4 | dayun-timeline-view | 大运研究层视图 dayun-timeline-view-v1 | inherited_pending |
| 5 | bingyao-shenfeng-v1 | 病药 Variant（神峰通考双对） | canonical_evidence_absent |
| 6 | pattern-zaqi | 格局杂气选格陈述 pattern_zaqi | canonical_evidence_absent |
| 7 | ren-pattern-yin-true-v1 | Slice D-1 任氏寅月真格 determination | execution_binding_structure |
| 8 | siling-yin-pilot | 司令寅月试点 Variant bazi-siling-yin-pilot-v1 | execution_binding_structure |

密封侧结构实测（可信机直读现行快照 phase1_knowledge.json）：Canonical 经典恰 4 部（`bazi.classic.yuanhai`、`bazi.classic.sanming_tonghui`、`bazi.classic.xieji`、`bazi.classic.ditiansui`），**无穷通宝鉴、无神峰通考**；节 64 条（最大 s064）、章 25、Phase1 规则 35 条（最大 r035）——登记册各条原因中关于 Canonical 构成的陈述与实测一致。

另注：`not_a_candidate` 3 项（siling-matrix-register、f4-changsheng-design、fuyi-slice-adjudication-register）不在本审计 8 项内；其中后两项的解锁前置为扶抑 U1/U3 与司令扩月的用户级裁定（在册口径，用户已暂缓 U1/U3），与本 8 项无涉，仅在此标注以免混淆——**本 8 项逐项核查后，无一项的 unlock_path 依赖 U1/U3**（见 §2 各项 (d) 与 §4）。

## 2. 逐项解锁条件审计

### 2.1 tiaohou-qiongtong-v1（调候 Variant，穷通宝鉴 119 条）

- **登记原因原文**：《穷通宝鉴》不在密封 Canonical 经典内（Canonical 仅渊海子平、三命通会、协纪辨方书、滴天髓阐微四书），调候全部引文无 canonical section 可绑。unlock_path 原文：Canonical 经典扩编治理批：穷通宝鉴建经典/章节/sections 并逐条复核引文后，另行注册。
- **(a) 缺口性质**：`canonical_evidence_absent` 的经典级形态——缺的不是某一节，而是整部经典在 Canonical 中的实体（经典/章/节三层皆无）。
- **(b) 材料存在性（实测）**：原文材料**在**。Source `bazi.source.qiongtong` 已登记（C 级、daizhigev20 固定快照），机上隔离区文件 `qiongtong_baojian.txt` 实算 SHA256 `a8125d7d…` 与登记值及 `bazi_tiaohou.py` 的 `SNAPSHOT_SHA256` 逐字相符（87,430 字节）；119 条条目已逐条按快照字符区间与行号审定（模块 `ENTRIES` 实测 119 条，Golden `tests/golden_tj0131_tiaohou.json` 在册）。但该书在 Canonical 侧无任何结构：无 classic/chapter/section，无 018 式校勘登记，全书未做多底本校勘（Source review_scope 明载：单一电子谱系、简体转写、仅调候条目经逐字审定）。执行面不缺：Variant 已消费已执行 trace 步（pillars/ten_gods/hidden_stems）并 fail-closed，缺的只是 Phase1 引文向 Canonical 节的逐字绑定面。
- **(c) 可补形态**：**无直接先例**。已实证的建节先例（批二/B-2）都是在既有经典（三命）内、以已正式应用的 S3 文本建节；新建一部经典（含经典准入、底本口径——简体转写本逐字入 Canonical 的口径未定、章节切分、119 条引文绑定）在本平台无批次先例，须先立设计审定批定口径，再行实施。
- **(d) 用户裁定牵涉**：无。unlock_path 不含任何用户级裁定事项，亦不依赖 U1/U3（调候与扶抑分立治理是在册硬边界）。
- **(e) 工作量与风险**：八项中最大；风险不在文本而在建制——底本口径与分节口径一旦定错，119 条绑定全盘返工。

### 2.2 dayun-classical-variants（大运古典三 Variant）

- **登记原因原文**：21 条登记引文 0 条在 Canonical 内：三命卷十一折除诸段无 canonical section，神峰通考不在 Canonical 经典内。unlock_path 原文：先行 Canonical 扩编（三命卷十一大运节登记；神峰建经典），再行注册批。
- **(a) 缺口性质**：复合型 `canonical_evidence_absent`——三命侧为**节级缺位**（经典在、节不在），神峰侧为**经典级缺位**（同 §2.5）。两部分须分开处置，不可一概而论。
- **(b) 材料存在性（实测）**：引文构成经模块 `bazi_dayun_classical.py` 实测为 21 条 = 三命 15 条（卷二《论大运》11 条，locator 字符 58584–59198；卷十一《珞琭子消息赋》注见证 4 条，字符 396898–408795）+ 神峰《起大运法》6 条（字符 85001–85246）。三命部分材料全在 S3 中逐字在位（机上实测：方向规则句 S3 58692、交运十年句 S3 59159（PUA「算」已在 S3 应用为正字）、卷十一方向见证 S3 396897，均呈 S0→S3 位移 −1 的既有口径）；三命 Canonical 现有节仅 6 条（咸池 + s060–s064），《论大运》与卷十一窗口均不在其中；且《论大运》亦不在 018 校勘登记 25 节内（8 个 sanming 校勘模块 `COLLATION_SECTIONS` 实测 25 节、无大运节）——但 TJ-017.1 已对该节做过逐字审定（模块内 PUA 标注附 confirmed 映射依据、闰月子句整段排除登记在案），018 形制登记有现成审定底稿而非从零开始。神峰部分材料状态同 §2.5。
- **(c) 可补形态**：三命部分 = B-1 式 018 形制登记（《论大运》一节 + 卷十一见证窗口）→ 批二/B-2 式 S3 建节+绑定，两步均有先例；神峰部分 = 建经典，无直接先例（同 §2.5）。**可分段解锁**：conversion-sanming 的引文全为三命侧；direction-classical 的编码规则句为三命方向句、神峰 6 条为 corroboration 角色——旁证引文是否必须 Canonical 绑定、抑或可按 r035 先例只绑实际消费引文，属实施批审定事项，本审计不预判；conversion-shenfeng 必须等神峰经典。
- **(d) 用户裁定牵涉**：无。闰月交运子句语义未明已整段排除登记，不属本项解锁所需裁定；不依赖 U1/U3。
- **(e) 工作量与风险**：三命部分中等（登记+建节两步、文本全在 S3）；全项解锁被神峰经典拖住，分段翻转的口径设计是主要风险点。

### 2.3 dayun-compose（大运组合入口 classical_dayun_timeline）

- **登记原因原文**：组合层不产生独立规则，其 evidence_binding 继承所组合古典 Variant 的 pending 状态。unlock_path 原文：随 dayun-classical-variants 注册自动解除。
- **(a) 缺口性质**：`inherited_pending`——无独立缺口。
- **(b) 材料存在性（实测）**：模块 `bazi_dayun_compose.py` 的 `evidence_binding` 现为 `pending_phase1_rule_registration`（逐字实测），其状态完全由 §2.2 决定，无自有引文、无自有规则。
- **(c) 可补形态**：无需任何补法；§2.2 相应 Variant 翻转时随之改记披露字段即可（实施批内的登记字段迁移，非独立批次）。
- **(d) 用户裁定牵涉**：无（随 §2.2）。
- **(e) 工作量与风险**：零独立工作量；风险仅在 §2.2 分段翻转时组合层披露与底层状态不一致，实施批须逐 Variant 对平。

### 2.4 dayun-timeline-view（大运研究层视图 dayun-timeline-view-v1）

- **登记原因原文**：视图层 Variant，只呈现底层区间产出，本身不产生裁决，其 binding 继承底层 pending 状态。unlock_path 原文：随 dayun-classical-variants 注册自动解除。
- **(a) 缺口性质**：`inherited_pending`——无独立缺口。
- **(b) 材料存在性（实测）**：模块 `bazi_dayun_timeline_view.py` 的 `evidence_binding` 现为 `pending_phase1_rule_registration`（逐字实测）；视图只呈现 §2.2 的区间产出（区间保真、年龄不呈现等硬边界与注册无关，不因翻转改变）。
- **(c) 可补形态**：同 §2.3，随底层翻转改记。
- **(d) 用户裁定牵涉**：无（随 §2.2）。注：该视图的**公开开放**是另一回事（TJ-017.3 行保持阻塞的原因），不在本治理项范围，本审计不议。
- **(e) 工作量与风险**：零独立工作量；同 §2.3 的对平风险。

### 2.5 bingyao-shenfeng-v1（病药 Variant，神峰通考双对）

- **登记原因原文**：神峰通考不在 Canonical 经典内，病药 9 条引文 0 条可在 Canonical 验证。unlock_path 原文：先行 Canonical 扩编（神峰建经典并登记病药诸节），再行注册批。
- **(a) 缺口性质**：`canonical_evidence_absent` 的经典级形态（同 §2.1），外加一处既有经典内的节级缺位（制衡引文，见下）。
- **(b) 材料存在性（实测）**：引文构成经模块 `bazi_bingyao.py` 实测为 9 条 = 神峰 8 条（病药说类定义节 7 条，字符 7019–7680；正官格节口径张力 1 条，字符 10010–10041）+ 滴天髓制衡 1 条（中和篇，字符 43767–43825，role=counterweight）。神峰原文材料**在**：Source `bazi.source.shenfeng` 已登记（C 级），机上隔离区 `shenfeng_tongkao.txt` 实算 SHA256 `121a571b…` 与登记值逐字相符（422,432 字节）；定义节已经 TJ-013 逐字审定（review_scope 在册：定义节与四病四药标题节定位、讹字与整句重复如实登记未订正）。机上子串核查：制衡引文「有病有药」在 Canonical 全部 64 节文本中 **0 命中**——滴天髓虽是既有经典，该段亦无 Canonical 节，登记册「0 条可验证」逐字成立。另须标注：神峰快照为简体转写单一谱系，且 Slice C 既有裁定「神峰图版不得由损坏 OCR 重建」——本项所需为散文定义节与起大运法节（与 §2.2 神峰部分同批可建），不涉图版。
- **(c) 可补形态**：神峰建经典——**无直接先例**（同 §2.1）；制衡引文一段可在既有滴天髓经典内按批二/B-2 形制建节补齐。与 §2.2 的神峰部分（《起大运法》一节）同源：**一次神峰经典扩编可同时服务本项与 §2.2 的神峰部分**，两项的 unlock_path 都以此为先行条件。
- **(d) 用户裁定牵涉**：无。正官格节口径张力（zhengguan_tension）已登记为并存未统一、不作裁定，注册不要求先行裁定；不依赖 U1/U3（病药与扶抑分立）。
- **(e) 工作量与风险**：本体小（实际消费仅定义节两对 + 定义句），但被经典级建制拖住；与 §2.2 神峰部分合并立项可摊薄建制成本。

### 2.6 pattern-zaqi（格局杂气选格陈述）

- **登记原因原文**：原注杂气段与三命两例证 0/3 在 Canonical 内（s053/s054 不含杂气段原文）。unlock_path 原文：先行 Canonical sections 扩编（滴天髓杂气相关段与三命例证节登记），再行注册批。
- **(a) 缺口性质**：`canonical_evidence_absent` 的**纯节级形态**——两书均为既有 Canonical 经典，缺的只是三段文本对应的节。本项是 8 项中缺口最小、形态最正的一项。
- **(b) 材料存在性（实测）**：3 条引文经 `bazi_pattern.py` 的 `ZAQI_QUOTES` 实测，`source_section_id` 全为 None：(i) `renshi.zaqi_passage`——滴天髓阐微快照字符 [33161, 33313]（八格章「影响遥系」子题原注段，本陈述的编码依据）；机上隔离区 `ditiansui_chanwei.txt` 实算 SHA256 `6a875a31…` 与登记值逐字相符；机上子串核查：「只当取土为格」「杂气财官」在 Canonical 全部 64 节文本中 **0 命中**，登记原因逐字成立。(ii) `sanming.zaqi_case_rilu`——三命 S0 [192131, 192174]（卷六《日禄归时》实案），S3 逐字在位（锚句「作杂气格论尤是」S3 192153，位移 −1 既有口径）；(iii) `sanming.zaqi_poem_nvming`——三命 S0 [245030, 245081]（女命章诗句及自注），S3 逐字在位（锚句 S3 245029）。执行面不缺：`month_pattern_zaqi` 已消费已执行 trace 步（pillars/ten_gods/hidden_stems/hidden_to_visible）并 fail-closed，与 B-2 翻转前的 pattern_route 同形。
- **(c) 可补形态**：全部有先例——滴天髓杂气段按批二形制在既有经典内建节（文本以密封滴天髓文本口径为准，实施批核对）；三命两例证按批二/B-2 形制以 S3 建节或窗口节并绑定；注册翻转按 B-2 形制将陈述接入 trace 步（可真实 fire，可取 validated 姿态，同 pattern_route 先例）。引文绑定子集定稿（编码依据句必绑、两例证作 conflict_branch_evidence 绑定）沿 r031/r035 子集先例，属实施批审定。
- **(d) 用户裁定牵涉**：无。三命与原注的杂气格流派冲突已由 Slice B 审定 B5 定格为并列呈现、不裁定（在册），注册只绑已执行部分与冲突证据本身，不要求先行裁定；「取土为格」换算（B3）保持 unadjudicated 且不在执行面内；不依赖 U1/U3。
- **(e) 工作量与风险**：八项中最小（一批可完）；主要风险在滴天髓建节的文本口径核对与两例证 S3 窗口的节界定稿，均为实施批内可闭合的实测事项。

### 2.7 ren-pattern-yin-true-v1（Slice D-1 任氏寅月真格 determination）

- **登记原因原文**：原典锚点全部在 Canonical 内（真格定义 s053、任氏程序 s054、司令 s024，2/2+司令可验证），且已由 r027/r028 在候选层引用；但 determination 由独立组合函数在 ExecutionTrace 之外产出（chart 不带出生瞬时、司令试点结果显式传入），Phase2 golden harness 的输入契约仅四柱干支、无出生瞬时与交节 provider，无法执行该 determination——注册将无执行步可绑。unlock_path 原文：执行绑定设计批：determination 接入 trace 步（显式试点结果作为已执行输入）并扩 golden 输入契约后，再行注册。
- **(a) 缺口性质**：`execution_binding_structure`——纯执行结构缺口，**零材料缺口**：锚点、引文、审定（D1 保守读法、D2 日干不计透，均为已在册的父级裁定）全部齐备。
- **(b) 材料存在性（实测）**：`ZHENGE_QUOTES` 2 条均带 `source_section_id`（s053/s054），机上子串核查「格之真者」命中 `bazi.section.s053`、司令锚点节 s024 在 Canonical 内（实测在位）；组合函数 `ren_yin_true_pattern(trace, pilot_result)` 签名实测——trace 消费 + 试点结果显式传入，与登记原因逐字相符；公开 Golden `tests/golden_tj012_ren_yin_true.json` 15 例在册（真实盘）。`golden.py` 的 `run_cases` 实测：provider 三重钉死（domain/provider/contract 一致且须为 `tianji_kb.operations.*`），用例以 `function(**case['input'])` 执行——输入契约即 provider 函数签名本身，故缺口可精确表述为：现行 bazi provider `operations.bazi_chart.chart` 的输入不含试点结果，determination 无从经 harness 执行。
- **(c) 可补形态**：全部有先例，属设计+实施一批——chart 门控显式输入（批一 `include_punishment_facts` 门控参数先例：显式试点结果作为已执行输入传入）、determination 经 trace 步发出（批二三谓词 determination 步先例：裁决经自有注册步发出、sufficient_rule 改指）、Golden 用例由既有 15 例真实盘转入并扩输入字段。设计点（属实施批审定，本审计只登记）：试点结果的身份钉值核验（D6 信任界）须在 trace 步内保持；harness 侧不得为本项放宽 provider 钉死口径。
- **(d) 用户裁定牵涉**：无。注册范围仅限既有寅月真格 determination 本身；不涉司令扩月（那是 §2.8 的事）、不涉破格/成败/清浊/用神（恒 None+unreviewed，翻转不改变）；不依赖 U1/U3。
- **(e) 工作量与风险**：中等（一批可完）；风险在 golden 输入契约扩展的波及面（harness 为全域共用，须以增量字段而非改契约形态落地）与 D6 信任界在 trace 化后的保持。

### 2.8 siling-yin-pilot（司令寅月试点 Variant bazi-siling-yin-pilot-v1）

- **登记原因原文**：独立 Variant、不经 ExecutionTrace；bazi Phase2 契约为单一 Variant（ziping-structural-v1），试点无法以自身 Variant 登记执行规则。且其定义性计算约定（连续 24 小时计日）是用户裁定的暂定程序约定、非原典规则，登记为 Phase1 原典规则即属误标；其原典锚点 s024（寅月分日）已由 r017/r020/r026 注册覆盖。unlock_path 原文：试点若转正（用户裁定扩月/约定转正）并接入 ExecutionTrace 后，再行注册；当前维持研究级。
- **(a) 缺口性质**：`execution_binding_structure` 与**约定性质问题**的叠加——后者是范畴问题而非工程问题：把用户裁定的暂定程序约定登记为 Phase1 原典规则属误标，任何工程批次都不能自行消除。
- **(b) 材料存在性（实测）**：原典锚点不缺（s024 在 Canonical 内，机上实测在位，且已由 r017/r020/r026 覆盖）；试点模块 `bazi_siling_pilot.py` 头部逐字载明其授权来源为用户 2026-10-27 裁定 C+E 之 E（仅寅月、暂定约定、不得外推）。所缺者不是材料，而是「转正」这一状态本身。
- **(c) 可补形态**：无工程形态可补。转正后接入 trace 的技术形态有先例（批一），但转正与否不在工程权力内。
- **(d) 用户裁定牵涉**：**有，且是本项的唯一解锁钥匙**——须用户裁定司令扩月或将「连续 24 小时计日」约定转正（或等价的转正裁定）。用户至今未作此裁定：2026-10-28 的扩展授权仅许 F4 在寅月内消费试点判甲段，未及扩月与转正。本项标为「待用户裁定，不得代决」。注：本项不依赖扶抑 U1/U3，其裁定事项为司令线自身的用户级事项。
- **(e) 工作量与风险**：工程量在转正后不大；当前风险为零动作风险——维持研究级即为在册定格状态。

## 3. 附带项：阳刃节防位点登记—应用分歧的处置路径定性

- **分歧事实（B-2 披露，本审计逐项复核）**：三命《论阳刃》节内两处「防」位点——引文 `yr.ersha` 第 6 字（S0 182078）与 `yr.he_xing` 第 16 字（S0 182375）——密封订正集在正式应用中作「凶」（S3 对应位 182077、182374，机上逐字实测为凶），而 018-F 校勘记登记读法作「㓙」。治理文档 `TJ0183_LUREN_PROMOTION.md` §3.2 已如实记录、不裁定；s064 节文本从 S3，两处现从应用文本作凶。
- **登记侧证据（实测）**：两条校勘记 `sm5y-fang-182078`、`sm5y-fang-182375` 均为 `reading_status = confirmed`、`usable_grade = Q1`、`disposition = corrected`，读法「㓙」各有**两家见证同作**（kanripo KR3g0042 与 mikkokotila 转录子集，逐字引文在册）。即登记侧读法有双见证支撑且已定级 confirmed。
- **应用侧证据（实测）**：阳刃节内校勘记读法为㓙的「防」位点共 25 处，S3 应用结果分布为——作㓙 17 处、作残余防保留（快照原字）6 处、作凶恰 2 处（即本分歧两处）。作凶的两处既非登记读法、亦非快照原字，是 25 处中仅有的与登记、快照两口径都不合的应用结果；B-1 禄节侧同型核查（防 16 处中 15 处经订正按登记读法应用）亦表明按登记读法应用是订正集的常态。故定性：**订正集在这两处的应用结果构成对已 confirmed 登记的偏离，属应用层勘误，不是登记错误，也不是见证分歧**。
- **三选一结论：属校勘订正批（勘误路径），不属 P2 式残余处置，不需用户裁定。** 理由：
  1. 不需用户裁定：本分歧不涉流派取舍——两家见证同作㓙、无对立见证、无 UD 类未决事项；「凶」是「㓙」的现代通行字形，两读同词，歧义只在字形层。用户裁定的适用域（流派取舍、证据冲突、范围变更）均不成立。
  2. 不属 P2 式残余处置：P2 的对象是 S0/S3 中**未被应用**的残余「防」位点（处置=只登记、不动文本）；本两处恰恰相反——它们**已被应用且应用结果与 confirmed 登记相左**，问题在已产出的应用文本与订正集本身，登记处置无法纠正一个已写入 S3 的字。
  3. 属校勘订正批：订正集是可订正的登记工件（订正只能追加、不得删史，与台账同规）；正路是先以勘误登记把两处偏离定格（订正集勘误条目：原应用字、应从登记读法、见证依据），其后是否重行应用生成新版 S3 并连动 s064 节文本 2 字与快照换代，属独立的重应用批次决策（成本远高于 2 字本身），不与勘误登记捆绑。
- **影响面（实测）**：两处均不在任何绑定引文内（B-2 §3.2 在册：r035 的 4 条绑定引文逐字无「防」；本审计复核两引文 `yr.ersha`/`yr.he_xing` 为登记引文而非 r035 source_refs），不涉及任何 determination；现行遏制已在位——密封专项以精确枚举钉住恰这两处、第三处出现即测试失败。在勘误登记落地前，分歧维持「已披露、已钉住、未订正」状态，不得在任何报告中记为已解决。

## 4. 结论与选批建议

### 4.1 三类清单

**(i) 现在可执行**（材料齐备、形态有先例、无用户裁定事项）：

1. **pattern-zaqi**（§2.6）——缺口最小：3 条引文、两书皆既有经典、文本逐字在位、执行面同 B-2 翻转前形态。**推荐为第一批。**
2. **ren-pattern-yin-true-v1**（§2.7）——零材料缺口：锚点已绑、Golden 15 例现成，缺口纯在执行绑定设计与 golden 输入契约扩展。
3. **dayun-classical-variants 的三命分段**（§2.2 三命部分）——《论大运》018 形制登记（有 TJ-017.1 审定底稿）→ S3 建节+绑定 → 三命侧 Variant 分段翻转；神峰部分与全项终局翻转不在此列。dayun-compose、dayun-timeline-view 随其翻转自动改记，无独立批次。

**(ii) 缺材料**（缺的不是原文，而是 Canonical 建制或先行经典）：

4. **tiaohou-qiongtong-v1**（§2.1）——原文快照在、119 条已审定；缺穷通宝鉴的 Canonical 经典实体（经典准入与简体转写底本口径未定）。须先立经典扩编设计审定批，再谈实施。
5. **bingyao-shenfeng-v1**（§2.5）与 **dayun-classical-variants 的神峰分段**（§2.2 神峰部分）——原文快照在、相关节已逐字审定；缺神峰通考的 Canonical 经典实体。两项共用同一先行件：一次神峰经典扩编同时解锁两项的神峰部分（外加 bingyao 的滴天髓制衡段建节，属既有经典内节级补齐，可随批带走）。

**(iii) 待用户裁定/暂缓**：

6. **siling-yin-pilot**（§2.8）——解锁钥匙是用户裁定（司令扩月或计算约定转正），用户未裁；维持研究级为在册定格。**不得代决。**
7. 附带项 §3 的两处防位点分歧——不入三类清单：其路径已定性为校勘订正（勘误登记先行），建议并入下一批三命校勘/勘误类批次顺带处理，不单独为 2 字立项；重应用 S3 与否则是勘误批内的独立决策点。

**关于 U1/U3 的总核查**：8 项逐项核毕，无一项依赖扶抑 U1/U3；U1/U3 所卡者为 `not_a_candidate` 中的 fuyi-slice-adjudication-register 与 TJ-013.1 本体，不在本名单内。本审计不提出任何触及 U1/U3 的批次。

### 4.2 第一批建议切法与验收口径草案（pattern-zaqi 注册批，仅草案，不实施）

- **切法**：一批完成——(1) 密封 Canonical 扩编：滴天髓经典内为「影响遥系」杂气段建节（节界以快照 [33161, 33313] 与既有滴天髓节口径核定）、三命以 S3 为《日禄归时》案一窗口与女命章案二窗口建节（或窗口节，节界由实施批按 S3 实测定稿）；(2) 引文绑定：3 条引文补 `source_section_id`，绑定子集定稿（编码依据句为规则引文、两例证为 conflict_branch_evidence，沿 r031/r035 子集先例与 Slice B B5 口径）；(3) 新 Phase1 规则 + Phase2 步（ID 顺延核查，现行最大 r035）：陈述经 trace 步发出（批一/B-2 形制），sufficient/evidence 口径与 B-2 同规；(4) 治理翻转 pattern-zaqi 为 registered，维持名单 8 → 7。
- **验收口径草案**：翻转前后陈述输出逐盘逐字等价（比对集至少含 Slice B 全部 Golden 与四季月见证盘，差异只许在封闭清单内：新增 trace 步及其 rule_match/evidence 条目、evidence_binding 与 limitations 注册状态句、治理计数钉迁移）；伪造引文负例被 EvidenceResolver 拒绝；回滚演练（新代码+旧快照）fail-closed；机上全配方复跑 SUCCESS 0 失败且增量与正式基线逐项对平；快照换代由父级合并前先行（沿批一/批二/B-2 原子流程）；确定性边界不变——determination 恒 None、土格换算恒 unadjudicated、流派冲突恒并列。
- **第二批顺位**：ren-pattern-yin-true-v1 执行绑定设计+实施批（先设计节定 golden 契约扩展形态，再实施）；第三顺位：dayun 三命分段（登记批 → 建节绑定批 → 分段翻转）。神峰/穷通两部经典扩编各先立设计审定批，顺位在上述三批之后，视设计结论再定实施切法。

## 5. 边界与仍无法判断的范围

- 本审计只判定「解锁条件是否具备与以何种形态补」，不判定任何规则内容、格局结论或吉凶；「可执行」指治理注册层面可立项，不指 determination 解锁——§4.1 (i) 三批翻转后，用户可见能力仍为零变化（研究级披露字段迁移），与批一/批二/B-2 同性。
- 以下事项本审计**不能**判断，留实施批实测定之：杂气段在密封滴天髓文本中的确切节界与文本口径（公开快照坐标与密封文本的对应关系）；三命两例证窗口的节界定稿形态（独立节或窗口节）；ren-pattern 的 golden 输入契约扩展的具体形态（门控参数扩 chart 输入 vs 新 provider 注册，两条路的 harness 波及面）；dayun 分段翻转时 direction-classical 旁证引文的绑定口径；神峰/穷通建经典的底本与分节口径（设计审定批的议题）。
- 本审计未核：密封 phase2_golden 中与本 8 项相关的用例构成（注册形态由实施批按 validate 口径实测）；S3 全文与订正集的逐条一致性（仅 §3 两处位点及分布抽核）；机上私有检出的登记副本与公开仓治理代码的一致性（治理登记以公开仓代码为本次审计的唯一权威读本）。

## 附：实测复核路径清单

- 公开仓（基线 `32ae7664…`）：`src/tianji_kb/bazi_registration_governance.py`（REGISTRATION_INVENTORY 18 行逐行 disposition 与 reason/unlock_path 原文、REASON_CLASSES）；`src/tianji_kb/bazi_tiaohou.py`（ENTRIES 119 条实测、SNAPSHOT_SHA256）；`src/tianji_kb/bazi_dayun_classical.py`（QUOTES 21 条构成与 locator、EXCLUDED_SPANS）；`src/tianji_kb/bazi_bingyao.py`（QUOTES 9 条构成与 locator）；`src/tianji_kb/bazi_dayun_compose.py`、`src/tianji_kb/bazi_dayun_timeline_view.py`（evidence_binding 逐字）；`src/tianji_kb/bazi_pattern.py`（ZAQI_QUOTES 3 条 source_section_id 全 None、ZHENGE_QUOTES 2 条带 s053/s054、`ren_yin_true_pattern(trace, pilot_result)` 签名、Slice B 审定 B1–B6 与 D-1 审定 D1–D6）；`src/tianji_kb/bazi_siling_pilot.py`（头部授权与约定口径）；`src/tianji_kb/golden.py`（run_cases 的 provider 三重钉死与 `function(**case['input'])` 契约）；`config/knowledge_sources.json`（bazi.source.qiongtong / bazi.source.shenfeng 登记与 review_scope）；八个三命校勘模块 `COLLATION_SECTIONS` 合计 25 节、无《论大运》节；`src/tianji_kb/bazi_sanming_juan5_zaqi_yangren_collation.py`（sm5y-fang-182078 / sm5y-fang-182375 两条 confirmed/Q1 与双见证、同节防→㓙条目 25 处清单）；`docs/product/TJ0183_LUREN_PROMOTION.md` §3.1/§3.2（分歧披露与 s064 携带口径）。
- 机上只读（InstaBox 可信机）：现行快照 `data/canonical/bazi/phase1_knowledge.json`（经典 4 部、节 64、规则 35；子串核查——「只当取土为格」「杂气财官」「有病有药」0 命中、「格之真者」命中 s053、s024 在位）；隔离区四快照 SHA256 实算与登记值逐字对平（穷通 a8125d7d…、神峰 121a571b…、三命 00e2a7db…、滴天髓 6a875a31…）；S3 应用文本逐字定位（大运方向句 58692、交运十年句 59159、卷十一见证 396897、杂气案一锚句 192153、案二锚句 245029）与防位点应用分布抽核（25 处：㓙 17、凶 2、防 6；分歧两处 S3 182077/182374 逐字为凶）。
