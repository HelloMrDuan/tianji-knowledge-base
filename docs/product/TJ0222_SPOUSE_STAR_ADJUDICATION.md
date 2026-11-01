# TJ-022.2 配偶星×桃花年运结构面审定（E0359）

## 0 授权与范围

本批为审定批：依据 docs/product/PROGRAM_REMAINDER_AUDIT_E0358.md §4 与 §10 的 A1 定级，裁定 TJ-022.2 配偶星结构面的两问——Q1 配对口径、Q2 输入面——并成文实现批（E0360）所需的完整接入契约。本批不实现任何配对逻辑，不改动任何判定，不触及旺衰喜忌面与扶抑 U1/U3，不动密封资产、快照与 cicd 钉。WBS 原文（docs/product/DETAILED_DELIVERY_BACKLOG_V1.md 第 141 行）对 TJ-022.2 的定义为「经审配偶宫/星与年运条件｜只有 M2/M3 审核通过的条件可参与；缺失直接限界」，本审定在此定义内工作：配偶宫（日支）×目标年成对结构已在主干，本批只审配偶星×桃花年运的结构配对面。

## 1 开工核实与基线实测

- 基线：API main HEAD = `74e48d83c580f60a408ef2607bf6eee1a364fa30`（再审计 PR #535 合并提交），台账末号 E0358，TASK_STATUS 中 TJ-022.2 行状态为「阻塞」。三项与任务书逐项相符。
- 配偶星透镜实测（`src/tianji_kb/bazi_core.py` 第 168 行 `traditional_spouse_star_lens(pillars, traditional_role)`）：`traditional_role` 不在 `("male", "female")` 即抛 ValueError；候选十神男为正财、偏财，女为正官、七杀；遍历四柱显干与藏干十神产出 `visible_positions` 与 `hidden_positions`（字段为 pillar、stem、ten_god，藏干另带 branch）；返回含 `role_basis="user_selected_traditional_lens"` 与 `interpretation_allowed=False`。其 docstring 自述为「Locate traditional spouse-star candidates without inferring relationship outcomes」。`operations/bazi_chart.py` 仅在 `traditional_role is not None` 时计算透镜并落 trace 步 `bazi.phase2.spouse_star_lens`（opt-in，专项测试 `test_traditional_spouse_star_lens_is_opt_in_and_role_is_strict` 在册）。
- 配偶宫面实测（`src/tianji_kb/scenario_engine.py` `_romance`）：结果键 `spouse_palace_year_relations`，scope 为 `reviewed_spouse_palace_day_branch_and_year_pairs`，`pairs_checked=1`，`interpretation_allowed=False`，块内 limitations 为「只观察日支位置与流年地支的六合、六害、六冲；无关系命中不代表婚恋缺失，不判断合化、婚期或吉凶。」；规则匹配 `bazi.scenario.spouse_palace_year_structure`（`derived_from_rule_ids` 含 `bazi.phase2.spouse_palace_day_branch` 与年度结构规则），专项 `tests/test_romance_spouse_year_structure.py` 恰 6 测。封套 limitations 现行文本含「三合、刑、破、合化效力、配偶星、旺衰喜忌、大运和紫微等未组合裁定」——配偶星现仍明示未组合。
- 桃花场景输入面实测：`_romance` 契约为必填 `{birth_value, target_year}`、可选 `{birth_zone}`，经 `_require_with_optional` 严格校验（键集必须是必填与可选之子集，未知键抛「Scenario input fields do not match the reviewed contract」）。本批实测探针：向 romance 传入 `traditional_role` 即在任何计算前被该契约错误拒绝——现行契约确无 role 输入，非仅页面缺失。
- 合盘先例实测：`_compatibility` 可选 `person_a_traditional_role`、`person_b_traditional_role`，逐人校验 ∈ {male, female}，仅在非 None 时写入各自的 execute 输入；未给 role 一方透镜为 None（`test_scenario_engine.py` 在册断言）。前端 `CompatibilityStructurePage.tsx` 仅在用户已选择时才发送对应 role 键（第 73–91 行）。透镜口径差异在 docs/product/KNOWLEDGE_GAPS.md 第 41 行定级为 bounded（`governance.school_conflicts`：传统配偶星观察口径差异=bounded），非 unresolved 阻断。
- 年度关系机器实测：`_annual_branch_structure(natal, flow_branch)` 对流年支×四柱原局支恰评四对，关系类恰为 `six_harmony`、`harm`、`clash`，规则 id 依次为 `bazi.phase2.branch_six_harmonies`、`bazi.phase2.branch_six_harms`、`bazi.phase2.branch_six_clashes`；任一已审规则未匹配或证据未解析即抛 ValueError（fail-closed）；配偶宫面即由此过滤 `natal_pillar == "day"` 的命中并逐条做分支一致性断言。
- 人生总览实测：`_life` 以 `{"birth_value", "target_year", **scenario_zone}` 调用 `_romance`（第 1884 行），从不传 role；其输入契约与 romance 现行契约同形。
- 本地裸克隆口径注记：本批在本机公开克隆直跑 `tests.test_romance_spouse_year_structure` 为 2 failures + 4 errors，逐项归因同一根因 `RuntimeUnavailable`（裸克隆无组装生产运行时，两条 FAIL 是期望错误被运行时错误抢先触发的报文不符），与在册「裸克隆需密封数据树」基线伪影同类；该专项的权威执行面是机上正式验收（模块在 accept_offline 清单内，[B033]/E0275 已记正式验收执行通过）。本批未据本地裸跑宣称通过。

## 2 Q1 裁定：配对只许位置级事实

**裁定：配偶星×桃花年运的配对只许位置级事实。** 配对的全部合法内容，是透镜候选位置（纯十神位置事实）与目标年干支之间的同一性事实与已审地支关系事实；不引入任何效力、旺衰喜忌量或婚恋推断。此裁定与审计 §4 第 (i) 问逐字对齐。

### 2.1 允许的配对事实（穷举三类）

- **P1 地支同一性**：目标年地支与某候选位置所在柱的地支相同（显干、藏干位置同等适用；位置所在柱与支均为命盘事实，逐字取自透镜与四柱）。
- **P2 已审地支关系**：目标年地支与候选位置所在柱地支之间，经 `reviewed_branch_pair_relations` 已审关系表命中的 `six_harmony`（六合）、`harm`（六害）、`clash`（六冲）三类，规则 id 恰为 `bazi.phase2.branch_six_harmonies`、`bazi.phase2.branch_six_harms`、`bazi.phase2.branch_six_clashes`。实现上即 `_annual_branch_structure` 命中中 `natal_pillar` 属于候选位置所在柱的子集，且须逐条断言命中 `natal_branch` 与该位置所在柱地支相等（沿配偶宫面的一致性断言先例）。关系类穷举止于此三类：三合、刑、破不在本配对内（未纳入本场景已审关系集，合化效力另属未裁定线）。
- **P3 天干同一性**：目标年天干与某候选位置的天干相同（显干位置与其藏干同等适用，行内以 `position_kind` 区分，逐字取自透镜字段；不赋予显/藏任何权重或等级）。
- 目标年干支的导出沿用 `_romance` 现行口径（目标年 7 月 1 日参考点、节气年、`calendar` provider），不新造历法逻辑。本批曾考虑「流年天干对日主的十神恰为候选十神」一类事实：其属十神归类而非位置同一性或已审支关系，超出审计 §4 第 (i) 问划定的帧，**不裁入本配对**（见 §7）。

### 2.2 禁止项（穷举）

- 禁止消费或产出任何旺衰、喜忌、扶抑、调候、病药量与裁决词（喜、用、忌、仇作为裁决结论，以及 strong/weak 类判定）；配对函数不得读取任何 strength/adjudication 变体产出。
- 禁止效力语义：关系命中不得表述为事件将发生或已激活（咸池 `target_year_activation` 的既有语义不延伸至本配对）；不判断合化成败、不含刑、破、三合。
- 禁止婚恋预测语义：婚期、正缘、结婚、离婚、配偶出现时间、恋爱发生与否、关系建议类字段与文案一律禁入（沿内容诚实红线与既有测试禁入先例：`fortune_score`、`marriage_date`、`conflict_score`、`auspicious`、`relationship_advice`、`breakup_risk`）。
- 禁止评分化：不得产出分数、百分比、指数、等级或吉凶标签；命中与未命中都不得渲染为婚恋前景的有无（无命中不代表婚恋缺失，沿配偶宫 limitations 口径）。
- 禁止改动候选口径：候选十神集恰为透镜既定（男正财、偏财；女正官、七杀），不得增删十神、不得按任何量重排或加权候选位置；不得由命盘事实反推 role（如以日干阴阳冒充性别口径）。
- 数据最小化：配对块只携带 §2.3 所列字段，不整份复制透镜内部结构之外的命盘数据，不新增回显出生数据。

### 2.3 配对结构数据形态（字段级契约）

结果键名 `spouse_star_year_pairing`，与 `spouse_palace_year_relations` 同级，形态如下（字段名与取值域为契约，实现不得增删字段）：

- `scope`：固定 `"reviewed_spouse_star_positions_and_year_pairs"`。
- `traditional_role`：`"male"` 或 `"female"`，逐字回显本次请求显式选择。
- `role_basis`：固定 `"user_selected_traditional_lens"`（与透镜返回值逐字一致）。
- `candidate_ten_gods`：逐字取自透镜（male 为 ["正财", "偏财"]，female 为 ["正官", "七杀"]）。
- `candidate_positions`：`{"visible": [...], "hidden": [...]}`，逐行逐字取自透镜 `visible_positions`、`hidden_positions`。
- `target_year`：`{"year": int, "ganzhi": str, "stem": str, "branch": str}`，为本场景现行目标年干支事实。
- `pairs_checked`：本次检视的候选位置总数（visible 与 hidden 行数之和）。
- `pairings`：逐条事实行 `{"position_kind": "visible"|"hidden", "pillar": str, "branch": str, "stem": str, "ten_god": str, "relation": "same_branch"|"same_stem"|"six_harmony"|"harm"|"clash", "rule_id": str|None, "evidence_ids": [...]}`；`branch` 为该位置所在柱地支；关系三类的 `rule_id` 为对应 Phase2 规则 id，同一性两类的 `rule_id` 为 None（同一性是算术事实而非规则命中，其 `evidence_ids` 为透镜证据）；行序确定性：按透镜位置序（visible 先于 hidden，柱序年、月、日、时），同一位置按 same_stem、same_branch、关系类（已审表序）逐项成行，不跨事实类去重、不排序加权。
- `pairing_state`：由计数机械派生的状态枚举，恰三值：`no_candidates`（候选位置为 0）、`no_pair_hits`（候选位置 >0 且 pairings 为空）、`paired`（pairings 非空）；只是计数摘要，不是解释。
- `evidence_ids`：本块全部引用证据的去重集（透镜证据与关系命中证据），且必须是封套 `evidence` 的子集。
- `reviewed_rule_ids`：`["bazi.phase2.spouse_star_lens",...实际命中的关系规则 id]`。
- `interpretation_allowed`：固定 `False`。
- `limitations`：固定文本「只观察配偶星候选位置与目标流年干支的同一性与已审六合、六害、六冲；无命中不代表配偶星缺失或婚恋缺失，不判断婚期、正缘、吉凶、合化或旺衰喜忌。」

### 2.4 空态与 fail-closed 条件

- **E0 role 缺席**：`spouse_star_year_pairing` 键**整体缺席**（非 None、非空块），对应规则匹配与 trace 步同时缺席，封套其余部分逐字不变（见 §4 等价口径）。
- **E1 候选为零**：role 已给但透镜候选位置为空集时，块在场，`candidate_positions` 两列表为空，`pairs_checked=0`，`pairings=[]`，`pairing_state="no_candidates"`。
- **E2 有候选无命中**：`pairings=[]`，`pairing_state="no_pair_hits"`，`pairs_checked` 为候选总数。
- **F1 role 非法**：`traditional_role` 存在但不是字符串 `"male"`/`"female"`（含其他字符串、数字、布尔）即在计算前抛 ValueError（沿 `_compatibility` 与透镜本身的严格校验）。
- **F2 透镜缺失**：role 已给但原局执行结果无 `traditional_spouse_star_lens` 时抛 ValueError，不降级产出空块。
- **F3 证据缺失**：透镜 trace 步（`bazi.phase2.spouse_star_lens`）的规则匹配缺 `evidence_ids` 或证据未在原局 evidence 中解析时抛 ValueError（沿配偶宫与咸池的证据校验先例）。
- **F4 分支不一致**：任一配对命中的 `natal_branch` 与对应候选位置所在柱地支不等时抛 ValueError（沿配偶宫一致性断言）。
- **F5 关系证据缺失**：`_annual_branch_structure` 既有 fail-closed 行为（已审关系规则未匹配或证据缺失即抛错）原样传播，不捕获、不软化。
- **F6 未知键**：含 role 拼写错误在内的任何契约外键，仍由现行 `_require_with_optional` 契约错误拒绝（不变）。

## 3 Q2 裁定：新增可选输入 traditional_role（结论 ii）【产品面影响单独标明】

**裁定取 (ii)：桃花场景新增一个可选输入 `traditional_role`，沿合盘已在产先例的逐请求显式选择形态；缺省即缺席、fail-closed。不取 (i)，不收敛 (iii)。**

### 3.1 三案证据与裁定理由

- **(i) 无需新输入即可自洽计算——否决，两条独立证据**：其一，命盘事实内不存在性别/role 数据：四柱、日主与十神均为性别无关事实，透镜函数签名强制显式 role 且对缺省抛错，`chart()` 亦以 opt-in 测试钉死「无 role 即无透镜键」；由日干阴阳等命盘量反推 role 是无任何在册来源裁定的虚构映射，且与 `role_basis="user_selected_traditional_lens"` 的登记口径直接冲突。其二，出生档案无此字段：`web/visual-prototype/src/public/birthProfile.ts` 的 `BirthInput` 字段穷举为 calendarType、year、month、day、isLeapMonth、time、timeUnknown、region、_regionNeedsConfirm，无性别字段；产品内唯一的「性别」控件是专业工具页共享 `birthFields` 的「传统排盘性别口径」选择（`domainPages.ts`），经 TJ-031.8 审计确认后端无承接参数（紫微页已将其禁用并注记），它不是出生档案字段、与场景输入面无连接。把该控件的页面态值静默当作 role 来源，等于以未登记口径冒充用户对本场景的显式选择，不取。
- **(iii) 输入不足、本项收敛——不取**：输入面并非无路可走——合盘场景已以同一透镜、同一 chart 通道、同一 role 值域在生产运行逐人可选 role 的完整先例（引擎校验、缺席即透镜 None、前端仅在已选时发送，三层齐备且有测试在册）。本项的 fail-closed 形态可完全复用该先例，不存在无法闭合的输入缺口，故不收敛；TJ-022.2 的余项处置因此不写收敛，保留至 §7 的喜忌面口径。
- **(ii) 成立**：role 的语义自始至终是「用户对本场景本次请求的显式传统口径选择」，与登记的 role_basis 逐字一致；新增面恰为一个可选键，缺省行为由 E0 空态完全定义，对既有调用方零影响。

### 3.2 输入契约裁定

- 引擎：`_romance` 的可选键集由 `{birth_zone}` 扩为 `{birth_zone, traditional_role}`；必填不变。校验：`traditional_role` 存在时必须是字符串且 ∈ {"male", "female"}，否则 ValueError（沿 `_compatibility` 第 1349–1353 行的同形校验）。
- 透传：仅当 role 存在时，才把 `traditional_role` 写入原局 execute 输入（沿 `_compatibility` 「非 None 才写入」的同形写法）；缺席时 execute 输入逐字不变。
- 缺省行为：role 缺席 → E0 空态，封套逐字等价（§4）；role 永不设默认值，任何层（引擎、API、前端）不得代填。
- `_life` 不改：人生总览不转发 role、其输入契约不变，总览内的 romance 段恒为 role 缺席形态（见 §4、§5 G10）。
- API 层不需改动：场景输入经 `/api/v1/scenarios/public` 透传至引擎契约校验；实现批须以真实 API 测试证明带 role 与不带 role 两路（沿配偶宫专项的 real-API 测试先例）。

### 3.3 产品面影响（单独标明，供父级合并审读）

- **页面新增一个控件**：`RomanceStructurePage.tsx` 新增一个可选选择控件「传统配偶星口径（可选）」，选项为未选择（缺省空）、女、男；仅当用户已选择时才在请求中发送 `traditional_role` 键（逐字效仿 `CompatibilityStructurePage.tsx` 第 73–91 行的发送形态）。这是本审定唯一的页面级新增面。
- **同批落地红线**：控件与后端契约必须在同一实现批（E0360）内同时落地——不得先上控件后接契约（TJ-031.8 教训：看似可选实则静默不生效的控件已被在册明令禁止），也不得先上契约而页面无入口（能力不可达）。
- **文案口径**：控件说明须点明其为传统定位口径而非结论，效仿在册文案「用于传统算法选项，不代表性格结论」；配对块在页面上只作结构事实呈现并附块内 limitations 原文，页面不得为命中或未命中添加任何解释性文案（吉凶、旺衰、婚恋前景类措辞禁入，沿 §2.2 与 TJ-007.1 结果页四层口径）。
- **不变项**：桃花页路由、场景 id、出生资料表单其余字段、目标年选择均不变；未选择 role 的用户看到的页面与结果与现状逐字一致（新块缺席、控件只是多一个未选控件）。

### 3.4 与既有输入契约的相容性

- **_regionNeedsConfirm**：出生地区确认流程作用于已存出生档案、发生在场景输入构造之前，本裁定不触及：role 不从出生档案读取、不参与 birth_value/birth_zone 的派生，档案未确认地区时仍按现行口径阻断计算，role 选择不能替代或绕过地区确认。
- **出生隐私**：role 是逐请求的传统口径选择（与合盘同类），不写入出生档案 schema、不新增 localStorage 字段、不进入 URL 与日志的本功能新增面；出生档案字段集保持 §3.1 所列九项不变。
- **出生时间输入契约**：小时/分钟显式选择等既有契约与本裁定正交，不受影响。
- **场景纯洁性**：role 只决定透镜候选十神集（传统口径本身），不进入咸池查表、配偶宫配对与目标年历法计算；同一 birth_value/target_year 下，role 只影响新块的在场与内容，不改变任何既有键的取值。

## 4 与既有配偶宫结构的组合方式

- 配对块与配偶宫块是同场景内的两个独立结构面：配偶宫管日支一柱与流年支的一对关系，配对块管候选位置各柱与流年干支的位置事实；二者不互相派生、不合并计数、证据集各自闭合（配对块的证据子集断言独立成立）。
- 封套组合（role 在场时相对 role 缺席基线的**封闭差异清单**，清单外逐字一致）：(1) `result` 新增键 `spouse_star_year_pairing`；(2) `rule_matches` 追加一条 `{"rule_id": "bazi.scenario.spouse_star_year_pairing", "derived_from_rule_ids": 配对块 reviewed_rule_ids, "variant": "ziping-structural-v1", "matched": True, "kind": "scenario_composition", "evidence_scope": "已审配偶星候选位置与流年干支同一性及六合、六冲、六害；无婚恋断语。", "facts": {traditional_role、pairs_checked、pairings 逐字}, "evidence_ids": 配对块 evidence_ids}`；(3) `trace` 追加一步 `{"step": "reviewed_spouse_star_target_year_pairing",...}`，形态沿配偶宫 trace 步先例；(4) `evidence` 增加配对块实际引用的证据条目；(5) 封套 `limitations` 中现行「夫妻宫仅以日支位置配对…」一条在 role 在场路径改写为「夫妻宫仅以日支位置配对已审六合、六冲、六害；配偶星仅以候选位置与流年干支作同一性及已审六合、六冲、六害配对；三合、刑、破、合化效力、旺衰喜忌、大运和紫微等未组合裁定。」——role 缺席路径该条逐字不变。`warnings`、`release_scope`、`status`、`public_release` 在两路均不变。
- 人生总览组合面不受影响：`_life` 恒以 role 缺席调用 romance，其跨场景一致性校验（日支关系与 evidence 的逐项对平）不涉及新块；TJ-025.2 的条件标记面不因本配对增减任何维度。

## 5 Golden 设计判据

- **导出纪律**：全部用例由真实出生时刻经现行历法 provider 导出四柱（场景输入只接受出生时刻与目标年，本无手编干支入口）；候选集、位置与关系逐项手工推导并断言精确值，不得以「键存在」类弱断言充数；透镜层既有手编四柱夹具（`test_phase2_bazi.py` 中 `己丑/戊辰/甲子/庚申` 例）只是 chart 层证据，不作场景 Golden 输入。
- **G1 支同一性（male）**：真实命盘 + 目标年，其年支与某候选位置所在柱地支相同；断言 pairings 中恰有对应 `same_branch` 行（rule_id 为 None、位置字段逐字、evidence_ids 为透镜证据子集）。
- **G2 已审关系命中（female，藏干位置）**：真实命盘 + 目标年，对某藏干候选位置构成六冲、六合、六害之一；断言对应行 `relation` 与 `rule_id` 恰为该类 Phase2 规则、evidence_ids ⊆ 封套 evidence。实现批至少覆盖一类，宜三类各一（可分用例）。
- **G3 干同一性**：目标年天干与某显干候选位置天干相同；断言恰有对应 `same_stem` 行。
- **G4 候选为零空态**：role 在场且所选口径下候选位置为空集的真实命盘（手工推导证明显干与全部藏干均无候选十神）；断言 E1 全部字段（含 `pairing_state="no_candidates"`、`pairs_checked=0`）。
- **G5 有候选无命中**：候选非空、目标年无任何同一性与关系命中的真实组合；断言 E2（`pairing_state="no_pair_hits"`、`pairings=[]`）。
- **G6 role 缺席等价**：与 G1–G5 同命盘同目标年、不带 role 调用，断言封套与实现前基线深等价（全部键含 limitations 逐字），且既有配偶宫专项 6 测不作修改地通过。
- **G7 禁入负例**：role 在场封套的配对块序列化文本不含禁入词表（至少含 `fortune_score`、`marriage_date`、`compatibility_percent`、`conflict_score`、`auspicious`、`relationship_advice`、`breakup_risk` 及「婚期」「正缘」作为结论键的形态）；块内 `interpretation_allowed` 为 False；块 facts 不含喜忌裁决词。
- **G8 fail-closed 负例**：role 取 `"unknown"`、`1`、`True` 各抛 ValueError；契约外未知键抛契约错误；以 patch 抽掉透镜证据（沿 `test_missing_spouse_source_denies_new_ability` 的篡改形态）时抛 ValueError 且不产出配对块。
- **G9 真实 API 对平**：经 `POST /api/v1/scenarios/public` 带 role 调用 romance，配对块与引擎直调逐字一致；不带 role 时响应无配对块（沿配偶宫专项 real-API 测试形态，非 mock 成功响应冒充）。
- **G10 人生总览不变**：同输入下 life 封套与基线深等价，全封套无 `spouse_star_year_pairing` 键。

## 6 实现批（E0360）验收清单

1. 契约差异恰为 §3.2 所裁：`_romance` 可选集新增 `traditional_role` 一键、校验与透传同形于合盘先例；`_life` 与其他场景零改动。
2. 配对块字段与 §2.3 逐字对平（键名、取值域、limitations 原文、行序）；规则匹配与 trace 步 id 恰为 §4 所定；F1–F6 fail-closed 均有测试落点。
3. 等价比对：role 缺席语料（真实命盘×目标年组合，数量与清单在实现批治理记录中先行登记）在新旧两树逐封套深等价、清单外差异为 0；role 在场差异严格限于 §4 封闭清单五项。
4. Golden G1–G10 全部落地并通过；新专项按名接入公开 CI（validate.yml）；既有配偶宫专项 6 测与合盘、人生总览相关测试不作修改地通过（若必须改动任何既有断言，停工报告父级，不得放宽）。
5. 机上全配方复跑（`scripts/accept_offline.py --suite all`）SUCCESS、0 失败：基线为实现批开工时直读的最新正式验收总数，增量逐项对平；本审定不涉密封资产，实现批原则上无换代——若实现中发现密封侧依赖，停工报告。
6. 前端同批落地 §3.3 控件与呈现，浏览器契约测试按名更新；控件文案与块呈现文案过 §2.2 禁入自查。
7. 台账：E0360 事件归属 TJ-022.2、状态保持「阻塞」不变（喜忌面未清，不得关账行状态）；关账批 E0361 在正式验收与部署记录齐备后另行派发。

## 7 仍不可判断范围

- **喜忌/效力面继续阻塞**：配偶星与年运的旺衰喜忌条件、配偶星效力与任何条件解释，仍被 TJ-013.1/TJ-013.2 阻塞（扶抑 U1/U3 为用户明示暂缓项，本批未触及、未代决）；TJ-022.2 在 E0360 完成后仍不得关账，其余项恰为该面。
- 本配对不产出任何婚恋结论：不判断桃花旺衰、恋爱或婚姻事件、配偶情况；命中与未命中均无吉凶含义。
- 三合、刑、破关系与天干五合不在配对内；「流年天干十神归属候选集」一类事实未裁入（§2.1），如未来需要，须另行审定，不得由实现批顺带加入。
- TJ-023.3（事业财运跨规则）与本批无涉，其阻塞复核不变；人生总览不消费配对块（§4），其 7 维标记面不变。

## 8 本批产出与边界

- 产出：本审定文档（docs/product/TJ0222_SPOUSE_STAR_ADJUDICATION.md）、公开治理测试（tests/test_tj0222_spouse_star_adjudication.py，已按名接入 validate.yml）、台账事件 E0359 与 TASK_STATUS 的 TJ-022.2 行续写。
- 未实施声明：本批未改动 `scenario_engine.py`、`bazi_core.py` 及任何运行代码，未新增场景输入，桃花场景现行契约逐字不变；§2–§6 的全部形态均为对实现批 E0360 的裁定契约，不构成任何已实现能力的主张。
