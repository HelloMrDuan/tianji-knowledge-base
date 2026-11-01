# TJ-013.3 分阶段开放第一阶段：喜用可读呈现开放契约审定（E0371）

## 0 授权与范围

- 授权来源：用户 2026-11-01 裁定选择分阶段开放并定序执行——第一阶段 = TJ-013.3 喜用可读呈现，授权启动；第二阶段 = TJ-017.3 大运公开，须待第一阶段独立验收通过后再启动，本批不碰、不预研。
- 第一阶段开放范围（用户逐字口径）：严格限定在已经注册的调候、病药证据范围：(1) 将已有取用依据转化为用户能理解的解释；(2) 明确区分调候取用、病药取用及其证据来源；(3) 不得包装成完整的扶抑喜用神结论；(4) 没有证据、存在冲突或超出注册范围的命例，明确标记暂不可判，不允许 AI 补造结论；(5) 不修改底层裁决规则，不借此解锁扶抑 U1/U3。验收重点：用户看到的每条喜用解释，都能追溯到已注册证据和实际执行记录。
- 本次明确不启动（用户同批裁定，本批一概不碰）：扶抑 U1/U3（暂缓维持）、长生冲突群、siling-yin-pilot、B002、TJ-018.2、TJ-019.2、TJ-028.1、合化 P-D1/P-D2、三刑 B2/B5。
- WBS 定义（TJ-013.3 原文）：「适用范围明确的用户可读提示」，验收口径为「前端只有真实经过 Phase2/Golden 的条件才出现解释」。本审定与该口径逐项对平：可呈现的只有已注册 Phase1 规则、validated Phase2 步与 Golden 覆盖的调候（E0352）与病药（E0348）两体系；其余体系的条件未过此门，一律不呈现为解释。
- 本批性质：只审定、不实现、不翻转任何公开开关。产出 = 本开放契约（实现批 E0372 的字段级依据）、公开治理测试、台账事件 E0371。实现预留 E0372、关账预留 E0373。TJ-013.3 行状态保持「阻塞」不变（见 §9 第 7 项与 §10）。

## 1 开工核实与基线实测

- GitHub API main HEAD = `68d18a9f08f231630e69e5285418bab1cd18e3db`（D 类订正 PR #543 已合并），与任务书基线一致。
- 台账：TASK_HISTORY 事件连续至 E0370（370 事件）；TJ-013.3 行状态「阻塞」，行备注记第一阶段研究级可读提示已关账（E0210/E0211）、阻塞原因为「公开呈现与跨体系裁决前置未清」。
- 正式验收基线：2901（Merge SHA `7c80a26c` 的管线正式验收 SUCCESS，E0363 关账在册）；本批预期无密封变更、无快照换代，密封钉 `26b63e64…`（237 文件 / 16,722,816 字节）不动。
- 再审计 E0358 §5 对本任务的在册结论与本批实测一致：证据腿（Phase2/Golden）已对调候、病药两体系解除；旺衰裁定与冲突呈现的证据状态未因注册改变；「第二阶段的呈现范围至多先行覆盖调候/病药两体系」。

## 2 现行实现全审计（实测，开发前审计）

### 2.1 第一阶段可读模块 bazi_xiyong_readable（已具备，不得重复建设）

- 模块 `src/tianji_kb/bazi_xiyong_readable.py`，Variant `xiyong-readable-hints-v1`：确定性模板渲染，输入为同一命盘一次执行的四对象——调候陈述、病药陈述（双对）、旺衰裁定陈述、TJ-013.2 冲突呈现；伪造、混盘、非研究标志、未知状态一律 fail-closed；输出恒 `research_only=True、public_enabled=False、ai_enabled=False`，全文经禁入词表扫描（吉/凶/宜/忌/灾/祸/发财/升职/喜用神/宜用/推荐/评分等子串零出现），不带古籍引文（引文留在结构化陈述内）。
- 消费面：仅 `operations/bazi_chart.py` 在 `readable_variant` 显式开启时调用，且 readable 要求 conflict 在场、conflict 又要求裁定（旺衰）+调候+病药三 Variant 齐备（chart 函数内硬校验）。公开面引用为零（§2.5）。
- 与开放范围的口径差（本审定关键事实）：该渲染器渲染旺衰裁定段（强/弱分类行）与跨体系关系段（含旺衰 incomparable 上下文行），超出用户裁定的「严格限定调候、病药」范围；且其形态为研究级全文渲染（逐体系段 + absent 伪段），不是公开呈现形态。故第一阶段成果是渲染语义与文案纪律的来源，**不是**可直接翻转公开的成品；公开呈现须按 §3–§5 另建 scoped 对象，旺衰段与 absent 伪段不得进入公开面。

### 2.2 调候 Variant 注册证据形态（tiaohou-qiongtong-v1）

- 陈述产出（`tiaohou_assessment` 消费已执行 trace 的 pillars/ten_gods/hidden_stems 三步、要求 evidence 已绑定、伪造即 fail-closed）：matched 形态含 `source_id=bazi.source.qiongtong`、`evidence_level='C'`、`day_master/month_branch/month_label`、`entry{quote, quote_locator{line,char_start,char_end}, section{…}, order_basis}`、`sequence[{stem, order, presence, visible_positions, hidden_positions}]`、`branches[{id, applied, condition, quote, locator, sequence, note}]`、`unencoded_branches`、`related`、`notes`，及包装层补入的 `consumed_rule_ids` 与 `fact_refs`（`#/trace/N/output` 指针）。`evidence_binding='registered_phase1_phase2'`。
- 注册链：Phase1 按干 10 条规则 `bazi.rule.r042–r051`，refs 恰 120 条 = 条目主引文 111 对 + 已编码分支引文 9 对（治理文档 GOVERNANCE_TIAOHOU_PROMOTION §3 实测）；Phase2 步 `bazi.phase2.tiaohou_assessment` validated；ENTRIES 119 条各带 `source_section_id`（`bazi.section.s076–s184`，丙×卯绑窗口节 s099）。**已编码条件分支（10 条，条件为单一干存在性事实）在注册 refs 内**；`unencoded_branches`（24 条）与 `related`（17 条）不在 refs 内、未注册。
- 缺席形态：仅乙×丑（乙木十二月条目在审定快照中不存在）返回 `status='not_applicable'`、`reason='entry_absent_in_source'`，不借他月条目或他典籍补齐。

### 2.3 病药 Variant 注册证据形态（bingyao-shenfeng-v1）

- 陈述产出（`bingyao_assessment` 消费 pillars/ten_gods 两步、同 fail-closed 口径）：顶层第一对语义 + `pairs` 双对并列；每对含 `rule{pair_id, subject/disease/medicine god 类与神集, quote, quote_locator, section}`（两对引文均锚定义节 `bazi.section.s071`）、`subject{god_class, gods[{pillar, stem, ten_god}]}`、`status ∈ {triggered, not_triggered}`、`not_triggered_reason`、`disease_candidate`、`medicine_candidate`、`medicine_status ∈ {candidate_present, absent}`、`determination=None`（恒）、`medicine_effect_status='unadjudicated'`（恒）。`evidence_binding='registered_phase1_phase2'`，包装层同带 `consumed_rule_ids` 与 `fact_refs`。
- 注册链：Phase1 `bazi.rule.r040`（refs 恰病药编码消费 4 条）、Phase2 步 `bazi.phase2.bingyao_assessment` validated（E0348 神峰扩编）。硬语义：不存在输出「无病」的代码路径；未触发只能记 not_triggered；双对同盘至多一对 triggered（显干算术约束，Golden 在册）。

### 2.4 冲突呈现模块（bazi_conflict_presentation，TJ-013.2）与本阶段的关系

- 该层只呈现不裁决：可比面 = 调候主序列点名干（角色 primary_pick）× 已触发病药对的角色点名（subject/disease/medicine，逐对以 pair_id 标明）；逐干关系类恰 {support, conflict, pivot_overlap, one_sided}；旺衰只以一条 incomparable 上下文记录携带、不参与分类；扶抑、格局用神标 absent。determination 恒 None。
- 本阶段公开面只取其中**调候×病药**两体系间的关系事实（用户口径 (4)：存在冲突须标记暂不可判——冲突事实呈现 + 标记，不裁决）；旺衰 incomparable 记录与 absent 记录均属范围外，不进公开面（§4.4、§5 N3）。

### 2.5 消费面与门控实测（E0358 记为 0，本批复测）

- `grep` 实测：`src/tianji_kb/scenario_engine.py` 与 `src/tianji_kb/api.py` 对 tiaohou/bingyao/xiyong/conflict_presentation/readable 的引用均为 **0**，与 E0358 在册结论一致。
- `engine.execute` 对客户端输入的 `tiaohou_variant`、`bingyao_variant`、`conflict_variant`、`readable_variant` 四键一律要求 `allow_research=True`，否则 ValueError；公开场景路径以 production 模式执行，四键均不可达。
- `operations/bazi_chart.chart` 中两 assessment 与 conflict/readable 均为显式 opt-in 参数，缺省不执行；两 assessment 各自独立可执行（conflict/readable 的级联要求不约束两 assessment 本身）。
- `public_projection.project_execution` 为最后防线：任一容器内的 `tiaohou_assessment`、`bingyao_assessment`、`readable_hints` 键在公开响应中整体剥离。
- `claim_capabilities.SCENARIO_CLAIMS['bazi-profile']` 只绑定结构事实声明（pillars/day_master/ten_gods/hidden_stems/month_command/root_candidates/hidden_to_visible/support_relations），无任何喜用面声明；本阶段呈现对象走场景结果信封（见 §3），不经 claim 绑定，该文件无需变更（§7 第 7 项）。

### 2.6 八字命理场景现行结果结构（呈现落点）

- 场景路径：`POST /api/v1/scenarios/public` → `execute_scenario('bazi-profile')` → `_bazi_profile`（输入契约恰 {value} + 可选 {strength_variant, zone}，未知键拒绝）→ `execute('bazi', …)` production 执行 → `_normalize_raw` 信封携带 `result / rule_matches / trace / evidence / limitations` 四通道 → API 层 `project_execution` 投影。信封本身已有一级执行记录通道（rule_matches/trace/evidence），§6 的可追溯链即锚于此。
- 前端 `BaziProfilePage.tsx` 结果面为 TJ-007.1 四层结构：一 · 盘面摘要（四柱/日主）；二 · 详细分析（现含「旺衰因素与通根候选」节及其边界文案）；三 · 规则命中；四 · 典籍依据；五 · 说明与限制（TJ-031.4 注记确认其为四层结构第 4 层）。现行边界文案三处与调候相关：第 117 行「通用旺衰、喜用神、大运起运仍未完成证据裁定」、第 175–176 行「不选择喜用神 / 不自动定格局、调候」、第 313 行「旺衰、喜用神、大运等需充分裁定，当前暂不提供结论」——其中「不自动定调候」与第一阶段开放后事实不符，须按 §4.7 收窄；其余两处就统一喜用神/格局/大运而言仍成立。
- 人生总览（life）聚合 bazi-profile 等四源的结果，但其组合层标记为独立硬编码口径（E0362 在册）；本阶段呈现对象只进 bazi-profile 结果，life 不得嵌入或转述（§4.6 第 8 项、§8 G10 钉死）。

### 2.7 审计结论

已具备（不得重复建设）：两体系的注册证据与执行链、确定性渲染语义与禁入词纪律、冲突关系分类语义、信封执行记录通道、公开投影剥离防线。缺失（E0372 建设面）：一条受控的生产执行开启路径（仅两 assessment）、一个 scoped 公开呈现对象及其确定性构建器、投影对新键的定域放行、前端呈现与文案收窄。旺衰段、absent 伪段、readable 全文渲染均不在建设面内。

## 3 呈现面裁定

### 3.1 落点

- 唯一呈现面 = 八字命理场景（scenario_id `bazi-profile`）的结果。呈现对象位于场景信封 `result` 内、键名裁定为 `xiyong_presentation`，Variant 标识裁定为 `xiyong-public-presentation-v1`。不新造场景、不改首页四层架构、不接线任何其他场景（含人生总览，见 §2.6）。
- 前端落层（与 TJ-007.1 四层结构相容）：第 2 层详细分析新增一节呈现两体系解释块与跨体系关系段（位置在既有「旺衰因素与通根候选」节之后，两节互不改写）；第 3 层典籍依据呈现两体系的逐字短引（与 §6 证据对象同一引文）；第 4 层说明与限制并入 §4.5 的范围声明与限制条目。页面文案不得出现 Rule ID、Trace ID 等技术字段（TJ-007.1 既有纪律）；结构化对象内的证据 id 属 API 信封层，与既有 rule_matches/trace/evidence 通道同级，不属页面文案。

### 3.2 执行路径裁定（生产开启门）

- E0372 须在场景层新增**服务端专属开启门**：由 `_bazi_profile` 在服务端构造执行输入，仅开启 `tiaohou_variant` 与 `bingyao_variant` 两个 assessment，执行形态与研究路径同一 chart 执行（同一 trace、同一 RuleMatch/Evidence 绑定），使呈现的每条解释与同请求信封内的 trace/evidence 逐字对应。
- 硬不变式（§7、§8 钉死）：(a) 客户端输入契约不变——{value} + 可选 {strength_variant, zone}，客户端夹带任何研究 variant 键（tiaohou/bingyao/conflict/readable/pattern/dayun 研究键等）的行为与基线逐字一致（未知键拒绝）；(b) 开启门只由服务端常量触发，不接受任何请求参数；(c) 开启集合恰为两 assessment——不得顺带开启 strength 裁定、conflict 呈现、readable 渲染或任何其他研究 Variant；(d) `engine.execute` 对客户端输入的四研究键 allow_research 门禁逐字不变；(e) 两 Variant 本体的 `research_only=True、public_enabled=False、ai_enabled=False` 标志**不翻转**——开放经由新呈现对象达成，不经由翻转 Variant 标志（翻转将泄漏至研究 chart 的全部消费面与投影剥离语义）。

### 3.3 构建器裁定

- 新建模块裁定为 `src/tianji_kb/bazi_xiyong_public.py`，构建器裁定名为 `public_xiyong_presentation(tiaohou, bingyao, *, execution)`：纯确定性模板拼装，不调用任何模型、不经 ExplanationService；输入 = 同一次执行的两陈述 + 该次执行的记录视图（trace 步序、RuleMatch、Evidence 键集）。
- fail-closed 纪律（沿两 assessment 与 readable 渲染器的既有口径）：陈述 variant/system/标志不符、两陈述日主不一致、陈述与执行记录对不上（Phase2 步缺失、evidence 未绑定、fact_refs 指向不存在的步）、证据字段缺失或被篡改（引文与注册 refs 不符、section id 不符、Phase1 规则 id 与同请求 RuleMatch 不符）——一律 raise，整个呈现对象不产出（场景其余结果不受影响与否由 E0372 按 fail-closed 原则定为：呈现构建失败即该键缺席且场景请求报错，二者择一须在实现批治理记录中明示并以测试钉住；不得静默产出残缺块）。
- 渲染语义来源：调候、病药两段的事实转写沿 §2.1 渲染器的既有行文语义（同一事实同一说法，不另造第二套措辞）；关系段为 §4.4 的两体系受限分类，不复用 readable 全文渲染、不经 conflict 呈现对象中转（其输入含旺衰陈述，范围外）。

## 4 内容契约（字段级）

### 4.1 顶层对象

| 字段 | 类型/取值 | 说明 |
| --- | --- | --- |
| `variant` | `'xiyong-public-presentation-v1'` | 固定 |
| `presentation_scope` | `'tiaohou_bingyao_only'` | 固定，范围自述 |
| `day_master` | 单干字 | 与两陈述一致，否则 fail-closed |
| `month_branch` | 单支字 | 同上 |
| `blocks` | `{tiaohou: §4.2, bingyao: §4.3}` | 恰两键，键集封闭 |
| `relations` | §4.4 列表（可空） | 只含两体系关系 |
| `unified_verdict` | `None` | 恒在且恒 None（与 determination 纪律同型） |
| `public_enabled` | `True` | 仅本对象、仅本场景 |
| `ai_enabled` | `False` | 固定 |
| `scope_statement` | §4.5 定稿文本 | 固定 |
| `limitations` | 字符串列表 | 至少含 §4.5 所列条目 |

### 4.2 调候块（blocks.tiaohou）

- 固定字段：`system='tiaohou'`、`source_label='《穷通宝鉴》'`、`state ∈ {presented, not_judgeable}`、`day_master`、`month_branch`、`lines`（用户可读行列表）、`evidence`（§6.1）。
- `state='presented'`（陈述 status=matched 时）：附 `month_label`、`sequence`（逐字携带陈述序列：stem/order/presence/visible_positions/hidden_positions）、`branches`（条目已编码分支逐条：id、applied、condition 的事实转写、quote、该分支 sequence；**只含已编码分支**——`unencoded_branches` 与 `related` 不得进入本块任何字段）、`entry_basis`（陈述 entry.order_basis 逐字，季总论/合论共享条目的依据形态据此如实呈现，不得把共享条目表述为该月专属条目）。
  - lines 组成：第 1 行 = 体系归属 + 条目身份（日主 + 月名）+ 主序列取用行（沿 §2.1 行文：干名、第几取、透/藏/未见位置事实）；其后每条已编码分支一行（条件事实 + 分支序列），applied 与否均如实标明；分支 applied 时，呈现必须使读者能分辨「原文在此条件下改以下列序列为准」，不得只呈现主序列而隐匿已生效分支。
- `state='not_judgeable'`（陈述 status=not_applicable 时）：`month_label/sequence/branches` 缺席，`not_judgeable_reason='entry_absent_in_source'`，lines 恰为 §5 N1 定稿行一条。

### 4.3 病药块（blocks.bingyao）

- 固定字段：`system='bingyao'`、`source_label='《神峰通考》'`、`state='presented'`（双对事实恒可陈述，块级不设 not_judgeable；不可判落在对级效力与 §5 N2/N3）、`day_master`、`pairs`（恰两对，序与陈述一致）、`lines`、`evidence`（§6.1）。
- 每对字段逐字携带陈述：`pair_id`、`rule{subject_god_class, disease_god_class, medicine_god_class, quote, quote_locator, section_id}`、`status`、`subject{god_class, gods}`、触发时 `disease_candidate`/`medicine_candidate`/`medicine_status`、未触发时 `not_triggered_reason`、`determination=None`（恒在）、`medicine_effect_status='unadjudicated'`（恒）、`efficacy_state='not_judgeable'`（恒在，见 §5 N3）。
- lines 组成：首行 = 体系归属 + 「按原文两组病药对逐对陈述，两对不合并为单一结论」（沿 BINGYAO_HEADER 语义）；逐对一行事实行（主体/病/药的显干位置事实，未触发行含未触发原因事实）；每对触发即附效力行（§5 N3 定稿语义行）。任何对的行文不得出现「有病」「无病」断言；未触发行必须含「未触发不等于无病」语义。

### 4.4 跨体系关系段（relations）

- 派生规则（TJ-013.2 已注册语义的两体系受限形态，零新教义）：可比面 = 调候主序列点名干（tiaohou 侧 {role: 'primary_pick', order}）× 已触发病药对的角色点名干（bingyao 侧 {role ∈ subject/disease/medicine, pair_id}，神行 stem 取该角色 gods 行的 stem）；逐干合并分类：同干被调候取用且为药 → `support`；为病 → `conflict`；为主体 → `pivot_overlap`；只被一方点名 → `one_sided`。未触发之对不产生点名；调候 not_judgeable 时关系段为空列表。
- 每项字段：`stem`、`kind ∈ {support, conflict, pivot_overlap, one_sided}`、`tiaohou`（侧对象或 None）、`bingyao`（侧对象或 None）、`judgeable`（布尔）。
- `kind='conflict'` 的项 `judgeable=False` 且附 §5 N2 标记行；其余 kind `judgeable=True`（仅表示该关系事实本身可呈现，不表示任何综合结论可判）。段末固定附「各体系陈述并列呈现，系统不作统一裁定」语义行（沿 NO_UNIFIED_VERDICT_LINE）。旺衰 incomparable 记录与扶抑/格局 absent 记录**不得**出现在本段或本对象任何字段。

### 4.5 范围声明与限制（定稿语义，E0372 逐字落文并以测试钉住）

- `scope_statement` 必须同时包含三个语义原子：(a) 本呈现只含调候（《穷通宝鉴》）与病药（《神峰通考》）两类已注册取用依据，逐条可回溯证据；(b) 两类依据并列呈现、互不合并，系统不据此给出统一的喜用神结论；(c) 扶抑、格局用神等其他取用判断尚未建成，不在本呈现内，暂不可判。
- `limitations` 至少包含：证据等级 C（单一电子谱系、简体转写、未做多底本校勘）；调候未编码分支与关联条目未呈现；病药为结构候选、去病效力未裁定、未触发不等于无病；本呈现为传统文化观察、不构成对现实的预测。

### 4.6 禁入项穷举（公开对象与页面呈现面全域适用）

1. 统一喜用结论：任何把某一干/某组干断言为本命「喜用神/忌神/喜神/忌神」的字段、行文或标题；`unified_verdict` 之外不得新增任何结论性字段。
2. 扶抑内容：扶抑体系的任何点名、结论、段落（含 absent 伪段）；扶抑二字只许出现在 §4.5 范围声明的「尚未建成」语境内。
3. 格局用神：任何格局用神点名或结论；格局候选亦不得借本对象呈现。
4. 旺衰裁定：强/弱分类行、裁定谓词行、incomparable 上下文行——旺衰裁定段整体禁入（既有独立的「旺衰因素与通根候选」观察节不在本对象内、不受本条影响，亦不得被本对象改写）。
5. 吉凶与评分：吉/凶断言词、评分、百分比、指数、等级（如「上等命」类）一律禁入（沿 §2.1 禁入词表全域扫描，E0372 以同一词表对公开对象与新增页面文案执行扫描）。
6. 病药效力与病断言：「药已去病」「有病」「无病」及任何效力成立/不成立的断言。
7. 调候越界内容：`unencoded_branches`、`related` 的任何转写；把取用序列翻译成吉凶、强弱、格局含义的任何行文；条目不存在时借用其他条目。
8. AI 生成文本：构建器与页面均不得调用模型或 ExplanationService 生成/改写本对象任何文本；`ai_enabled=False` 恒定。
9. 跨场景泄漏：`xiyong_presentation` 键只许出现在 bazi-profile 场景结果内；life、romance 等任何其他场景的响应含此键即违约。
10. 研究对象泄漏：`tiaohou_assessment`、`bingyao_assessment`、`readable_hints`、`conflict_presentation` 四个研究对象键不得因本阶段开放而出现在任何公开响应中（投影剥离不变，§7 第 5 项）。

### 4.7 既有页面文案的收窄裁定（E0372 执行）

- 第 176 行「不自动定格局、调候」：须改写为与事实相符的口径——格局仍不自动定；调候改为「只呈现已注册条目依据、不作统一喜用结论」语义。改写后文本由 E0372 定稿并钉入测试，但不得削弱「不自动定格局」与「不选择喜用神」（第 175 行）两项仍然成立的声明。
- 第 117 行与第 313 行：就「喜用神（统一结论）、大运」而言仍成立，保留；若改写，只许收窄到与 §4.5 同口径（区分「调候/病药依据已可呈现」与「统一喜用神结论仍不提供」），不得删去大运与统一喜用神的未裁定声明。
- 第 244 行旺衰节边界文案：不在本阶段范围，逐字不动。

## 5 暂不可判契约

三类暂不可判各自独立标记、互不替代；标记粒度到块/对/干，不许以一句总括文案覆盖全部维度。定稿行由 E0372 逐字落文并以测试钉住，语义原子不得缺失。

- **N1 无证据（调候条目缺席）**：触发条件 = 调候陈述 `status='not_applicable'`（全域仅乙×丑一格）。形态 = 调候块 `state='not_judgeable'` + `not_judgeable_reason='entry_absent_in_source'` + 定稿行一条，语义原子：含「暂不可判」、日主与月支、条目在审定《穷通宝鉴》文本中不存在、不以其他月份条目或其他典籍补齐。病药块与关系段不受 N1 影响（关系段因调候无点名而为空）。
- **N2 证据冲突（跨体系方向相反）**：触发条件 = 关系段存在 `kind='conflict'` 项。形态 = 该项 `judgeable=False` + 标记行，语义原子：含该干、「暂不可判」、调候以该干为取用与病药以该干所属之神为病两事实并列、只并列呈现不作统一裁定、该干的综合取用暂不可判。两体系各自块内的事实呈现不因 N2 而删改；N2 只标记「综合取用」一层。冲突事实来自 TJ-013.2 已注册分类语义，本阶段只呈现不消解、不投票、不加权（裁决规则属 TJ-013.2 本体，未建，不在本阶段）。
- **N3 超出注册范围**：三副形态——(a) 体系级：扶抑、格局用神与统一喜用结论由 §4.5 范围声明统一标记暂不可判，不设逐体系伪段；(b) 对级：病药每对恒带 `efficacy_state='not_judgeable'`，触发对附效力行，语义原子：只陈述原文病药对的结构候选、药是否能去病未给出可执行裁定、去病效力暂不可判（沿 §2.1 EFFICACY_LINE 并补暂不可判标记）；(c) 条目级：调候条目的未编码分支与关联条目不呈现，其存在只由 §4.5 限制条目声明，不构成可判内容。
- 与 TJ-013.2 的衔接边界：本阶段呈现的冲突是**事实层**呈现（关系分类 + 暂不可判标记）；TJ-013.2 的裁决规则本体（冲突如何消解）未建且不在本阶段范围，公开面不得出现任何消解性措辞（「以调候为准」「以病药为准」「综合判断」类一律禁入，归 §4.6 第 1 项）。

## 6 可追溯验收契约

### 6.1 证据对象（每块恒带，字段级）

- 调候块 `evidence`：`{source_id: 'bazi.source.qiongtong', evidence_level: 'C', phase1_rule_id, phase2_step_id: 'bazi.phase2.tiaohou_assessment', section_id, quote, quote_locator{line, char_start, char_end}, consumed_rule_ids, fact_refs}`。其中 `phase1_rule_id` 必须等于**同一次执行** RuleMatch 中该 Phase2 步实际命中的按干规则（r042–r051 之一），由执行记录读出，不得在呈现层按日主查静态表拼造；`section_id` 为该条目 ENTRIES 的 `source_section_id`；`quote/quote_locator` 与条目主引文逐字一致。not_judgeable（N1）时 evidence 只含 source_id/evidence_level/phase2_step_id 与缺席事实（无 section/quote 可引，缺席本身即事实）。
- 病药块 `evidence`：`{source_id: 'bazi.source.shenfeng', evidence_level: 'C', phase1_rule_id: 'bazi.rule.r040', phase2_step_id: 'bazi.phase2.bingyao_assessment', section_ids, quotes: [{pair_id, quote, quote_locator, section_id}], consumed_rule_ids, fact_refs}`，两对引文逐对携带（均锚 `bazi.section.s071` 定义节）。
- 通则：`consumed_rule_ids` 与 `fact_refs` 逐字取自对应 assessment 的同名字段；evidence 对象内任何 id 必须能在同请求信封的 `trace`/`rule_matches`/`evidence` 通道中定位到对应记录（执行记录对平，§6.2 第 3 项）。

### 6.2 校验方法与测试落点（E0372 必须落地）

1. 构建期对平：构建器逐项核对陈述 ↔ 执行记录（Phase2 步在 trace 中存在且 evidence 已绑定、fact_refs 指向真实步序、Phase1 规则 id 与 RuleMatch 一致、引文与注册 refs 逐字一致）；任一不符 raise（§3.3）。
2. 篡改 fail-closed 专项（公开测试 + 密封测试分工沿在册先例：结构面公开、需密封 bundle 的 refs 恰等核对入密封专项）：至少四类篡改各一例——改 quote 一字、改 section_id、改 phase1_rule_id 为同体系另一规则、删 evidence 绑定——期望构建失败或呈现缺席，绝不产出被篡改的解释。
3. 真实 API 对平：以 §8 真实盘经 `POST /api/v1/scenarios/public`（bazi-profile）实测，响应中 `xiyong_presentation.evidence` 的全部 id 与**同一响应**的 trace/rule_matches/evidence 通道逐项对平；页面第 3 层呈现的短引与 evidence.quote 逐字一致。
4. 每条用户可见解释行的事实回溯：lines 中每个干名、次序、位置、角色必须能在对应陈述的事实字段中定位（沿 §2.1 渲染器「静态模板不含干名、干名只能来自输入事实」的封闭性纪律，专项以全域扫描 + 逐行事实标注核对）。

## 7 门控翻转清单

| # | 门控/标志 | 现状（实测） | E0372 目标态 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | `engine.execute` 客户端四研究键（tiaohou/bingyao/conflict/readable variant）allow_research 门禁 | 无 research 模式即 ValueError | **不变** | 客户端不可达性由 §8 G10 钉死 |
| 2 | `_bazi_profile` 输入契约 | {value} + 可选 {strength_variant, zone}，未知键拒绝 | **不变** | 夹带研究键行为与基线逐字一致 |
| 3 | `_bazi_profile` 服务端执行开启 | 只跑 production 图 | **新增开启门**：服务端构造、恰开启两 assessment（§3.2） | 本清单唯一执行面翻转 |
| 4 | 两 Variant 与 readable Variant 的 research_only/public_enabled/ai_enabled 标志 | True/False/False | **不变** | 开放经新对象达成，不翻 Variant（§3.2 (e)） |
| 5 | `public_projection` 剥离表 | tiaohou_assessment/bingyao_assessment/readable_hints 全域剥离 | 原料键**不变**剥离；**新增定域放行**：`xiyong_presentation` 仅当出现在 bazi-profile 场景结果且通过 §4 形态校验时保留，其余场景出现或形态不符即剥离 | 防线不降级 |
| 6 | `bazi_xiyong_readable.readable_hints` 及其 chart 级联门 | 研究级、需四对象齐备 | **不变**，公开路径不得调用 | 旺衰段零泄漏的结构保证之一 |
| 7 | `claim_capabilities` | bazi-profile 只绑结构事实 | **不变**（已核无需变更） | 呈现对象不经 claim 通道 |
| 8 | ExplanationService / AI 通道 | 研究结果入口即拒（ai_may_explain=False） | **不变**；新对象 `ai_enabled=False` | TJ-028.1 未启动，AI 保持关闭 |
| 9 | 前端 BaziProfilePage 边界文案 | 第 117/175/176/313 行现行口径 | 按 §4.7 **收窄**（仅 176 行必改，117/313 只许收窄） | 文案面翻转，与后端同批落地 |
| 10 | 扶抑、格局用神两体系的公开状态 | 未建、absent、无公开面 | **保持关闭** | 由 §8 G10 零泄漏测试钉死：公开对象键集封闭、全文无两体系点名结论 |

## 8 Golden 判据设计（E0372 落地，真实出生时刻、期望手工推导）

沿在册 Golden 纪律：每例为真实出生时刻经真实历法路径得四柱，期望文本/结构按结构化事实手工撰写并逐项标注事实来源；既有 TJ-013.2/TJ-013.3 Golden 同盘复用为在册先例（盘面推导已在册复核）。

- G1 调候命中 + 病药首对触发 + support 关系：1960-03-07T01:30 +08:00（庚子/己卯/甲午/乙丑，甲日卯月；在册 support 例同盘）——调候块 presented（序列首取干与病药药位同干）、病药首对 triggered、关系段含 support 项、evidence 全链对平。
- G2 病药首对触发 + conflict 冲突暂不可判：1963-06-08T11:30 +08:00（癸卯/戊午/壬午/丙午，壬日午月；在册 conflict 例同盘）——关系段含 conflict 项且 `judgeable=False`、N2 标记行在位、两块事实不删改。
- G3 无证据暂不可判（N1）：1950-01-20T11:30 +08:00（己丑/丁丑/乙卯/壬午，乙日丑月；在册条目缺席例同盘）——调候块 not_judgeable、关系段为空、病药块按实测渲染。
- G4 两体系同盘并存 + pivot_overlap：1950-02-10T17:30 +08:00（庚寅/戊寅/丙子/丁酉，丙日寅月；在册 pivot 例同盘）——两块同呈、关系段含 pivot_overlap 项、无统一裁定行。
- G5 病药第二对触发：1952-08-16（在册 pair2-foodwound-triggered 例同盘，时刻以 golden_tj0133_readable_hints.json 该例 source_birth 为准）——第二对 triggered 且行内明示所属对、首对按实测（未触发）渲染、效力行在位。
- G6 病药第二对触发且药缺席：1950-10（在册 pair2-medicine-absent 例同盘，时刻同上口径）——`medicine_status='absent'` 如实呈现、无效力断言。
- G7 双对均未触发：真实盘一例（E0372 构造并手工推导，两对 not_triggered_reason 逐对核对）——两对未触发行齐备、全对象无「无病」字样、无任何 triggered 形态残留。
- G8 调候已编码分支命中：真实盘一例（E0372 按 10 条已编码分支之一构造，如甲日主午月且癸全盘未见 →「乏癸用丁」分支 applied，时刻与四柱手工推导并标注分支 id）——分支行在位且 applied 如实、主序列与分支序列关系可分辨；另配一例同条目分支未命中（applied=False）对照。
- G9 禁入词表：对 G1–G8 全部公开对象与新增页面文案执行 §4.6/§2.1 词表全域扫描，零命中（范围声明内的「扶抑……尚未建成」语境豁免按 §4.6 第 2 项的限定口径登记）。
- G10 未开放体系零泄漏 + 客户端门禁不变：公开对象键集递归扫描无 fuyi/pattern/strength/useful_god 类键与旺衰分类值；公开请求夹带 tiaohou_variant/readable_variant 等研究键的行为与基线逐字一致；life 场景响应无 `xiyong_presentation` 键；公开响应无四研究对象键。
- G11 证据篡改 fail-closed + 真实 API 对平：§6.2 第 2、3 项各至少一例落地（篡改四类 + G1 盘真实 API 全链对平）。

## 9 实现批（E0372）验收清单

1. 契约差异恰为 §7 清单所裁：第 3 项服务端开启门（恰两 assessment）、第 5 项投影定域放行、第 9 项文案收窄；其余七项逐字不变。两 Variant 与 readable Variant 的标志、engine 客户端门禁、输入契约任一被改动即停工报告。
2. 公开对象字段与 §4 逐字对平（键名、取值域、恒在字段、定稿语义行）；§4.6 禁入项有全域扫描测试落点；§5 三类暂不可判各有形态测试。
3. Golden G1–G11 全部落地并通过；新专项按名接入公开 CI（validate.yml）；需密封 bundle 的 refs 恰等核对入密封专项并在离线验收执行，不冒称公开 CI 覆盖。
4. 等价比对：除 bazi-profile 结果新增 `xiyong_presentation` 键及其 trace/RuleMatch/Evidence 通道的两步增量外，其余场景与 bazi-profile 既有字段在真实语料上逐封套深等价、清单外差异 0；前端既有页面行为（除 §4.7 收窄文案与新节呈现外）零改动。
5. 机上全配方复跑（`scripts/accept_offline.py --suite all`）SUCCESS、0 失败：基线为实现批开工时直读的最新正式验收总数（本审定基线 2901），增量逐项对平；本阶段不涉密封资产变更，实现批原则上无换代——若实现中发现密封侧依赖，停工报告。
6. 前端同批落地：两块与关系段的真实渲染（非 stub 冒称；浏览器专项如实标注性质）、第 3 层短引与 evidence.quote 逐字一致、§4.7 文案收窄落地；页面全域无 Rule ID/Trace ID 文案。
7. 台账：E0372 事件归属 TJ-013.3、状态保持「阻塞」不变（关账与行状态处置由关账批 E0373 在正式验收与部署记录齐备后，按 WBS 验收口径「前端只有真实经过 Phase2/Golden 的条件才出现解释」逐项对平再行决定，本审定不预判关账结论）；E0372 须在治理记录中给出该对平清单供 E0373 消费。
8. 呈现构建失败的处置形态（§3.3 二择一）在实现批治理文档中明示并以测试钉住。

## 10 仍不可判断范围

- 扶抑喜用、格局用神、旺衰喜忌的统一判断：未建或未开放，U1/U3 用户暂缓维持，本阶段不呈现、不解锁；公开面只有 §4.5 范围声明一处提及扶抑（「尚未建成」语境）。
- 跨体系冲突的消解（TJ-013.2 裁决规则本体）：未建；冲突只呈现事实并标记暂不可判（N2），不产生任何综合取用结论。
- 病药去病效力：恒未裁定（N3 对级标记）；病药触发与否不构成「有病/无病」判断。
- 调候条目的未编码分支（24 条）、关联条目（17 条）与未建节文本：不在注册 refs 内，不呈现为取用依据；条目主序列之外的条件性原文细节暂不可判。
- 旺衰裁定段（TJ-011.2/013.1 链）与 readable 全文渲染：保持研究级，不在第一阶段公开范围；其证据状态未因本阶段改变。
- 第二阶段（TJ-017.3 大运公开）：未启动、不预研；其开工前置（独立复核与 TJ-017.2、U1/U3 的关系）按用户裁定在第二阶段开工时另行执行。
- AI 解释：保持关闭（TJ-028.1 未启动）；本阶段全部文本为确定性模板。

## 11 本批产出与边界

- 产出：本审定文档（docs/product/TJ0133_STAGED_OPENING_PHASE1.md）、公开治理测试（tests/test_tj0133_staged_opening_phase1.py，已按名接入 validate.yml，钉：审定在册、两 Variant 与 readable Variant 现行门控标志逐字未变、scenario_engine/api 对四研究对象的引用仍为 0、engine 客户端四键门禁在册、投影剥离表三原料键在册、台账行/事件）、台账事件 E0371 与 TASK_STATUS 的 TJ-013.3 行续写。
- 未实施声明：本批未改动任何运行代码，未新建呈现对象，未翻转任何门控或标志，未改动裁决规则与冲突呈现语义；§3–§8 的全部形态均为对实现批 E0372 的裁定契约，不构成任何已开放能力的主张。TJ-013.3 行状态保持「阻塞」：公开呈现前置（用户分阶段开放裁定）已由本审定承接，但实现、正式验收与部署均未发生，跨体系裁决前置（TJ-013.2）仍未清。

## 12 实施记录（E0372，2026-11-01，append-only 追加）

本节由实现批 E0372 追加，§0–§11 审定原文未改动一字。实现基线：main `6db7b5789de05b820760a9c777bff56d56e86a80`（E0371 已合并，台账 371 事件），密封钉 `26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`，正式验收基线为开工直读的部署管线对 `6db7b578` 的 acceptance 记录：SUCCESS、总测 2908（public-git-checkout 15 + public-only 24 + private-backend 2869，skip 5）。本批无密封资产变更、无换代（验收复跑知识清单仍为同一钉）。

### 12.1 实施五问答复

1. **呈现由谁构建**：服务端场景层专属开启门（`scenario_engine._bazi_profile`）在同一 chart 执行上恰开启调候、病药两 assessment，纯确定性构建器 `bazi_xiyong_public.public_xiyong_presentation`（新模块）从该次执行的两份陈述与执行记录派生呈现对象；不调用模型、不经 ExplanationService、前端不拼装。
2. **证据从哪来**：`phase1_rule_id` 由构建器机械派生——在该 Phase2 步的 evidence_ids 内定位 `original_text` 与条目/对引文逐字相等的唯一记录，取其 `section_id`，再于场景层自同一知识包构造的引用索引（`_xiyong_phase1_refs`，自 EvidenceResolver 读两步合同的 `phase1_rule_refs` 与各 Phase1 规则 `source_refs`）中求唯一归属规则；并以「归属规则全部 refs 的记录同属条目所在章」与「记录章题以日主起首」交叉核对。呈现层无任何按日主静态查表拼造证据字段的代码路径。
3. **构建失败怎么办**（§3.3 二择一处置，本批选定并明示）：**场景请求报错**。构建器任一核对不符即 raise，`_bazi_profile` 不吞异常，不返回缺键的半成品信封；处置由密封专项 `FailureDispositionTests` 钉住（mock 构建器抛错时期望 `execute_scenario` 抛错、无信封产出）。
4. **与基线的差异面**：恰为 §7 第 3/5/9 三项翻转（见 §12.3 对照）；bazi-profile 信封差异恰为封闭清单（见 §12.4 第 4 项）；其余场景逐封套零改动（密封专项实测九场景）。
5. **如何验证**：Golden G1–G11 全量落地（§12.5）；等价比对封闭清单深等价；机上全配方复跑 SUCCESS 0 失败、增量逐项对平 2908 基线（§12.6）；真实 API 对平在密封专项内以 TestClient 对组装后端实测（G11）。

### 12.2 落地清单（文件级）

- 新增 `src/tianji_kb/bazi_xiyong_public.py`：构建器 `public_xiyong_presentation` + 投影用形态校验器 `is_valid_public_presentation`；定稿文案（范围声明、限制四条、N1/N2/效力行）以模块常量与模板落文，公开专项逐字钉住。
- `src/tianji_kb/scenario_engine.py`：`_bazi_profile` 开启门（见 §12.3 第 2/3 项与 §12.7 决定一、二）与 `_xiyong_phase1_refs` 引用索引构造；文件其余部分未动。
- `src/tianji_kb/public_projection.py`：定域放行（见 §12.3 第 5 项）；剥离表新增 `xiyong_presentation` 全域 pop 一行与校验回填。
- 前端 `web/visual-prototype/src/public/`：`api.ts` 新增 `executeBaziProfileScenario` 及其专用响应断言（见 §12.7 决定五）；`BaziProfilePage.tsx` 新增呈现节（第 2 层）、第 3 层两体系短引子块、第 4 层范围声明与限制并入、第 176 行文案收窄；`bazi-profile.css` 新增呈现节样式（沿旺衰节视觉规格）。
- 测试：`tests/test_tj0133_xiyong_public_presentation.py`（公开专项 20 测）+ `tests/golden_tj0133_xiyong_public.json`（9 例）；`tests/test_tj0133_xiyong_public_sealed.py`（密封专项 9 测，仅离线验收）；`tests/test_tj0133_staged_opening_phase1.py` 两处状态转换钉按 §7 更新（见 §12.3）；浏览器专项 `web/visual-prototype/tests/tj0133-xiyong-presentation.spec.ts`（2 测）+ 工作流 `.github/workflows/tj0133-xiyong-presentation-playwright.yml`；`validate.yml` 按名接入公开专项。
- 台账：TASK_HISTORY 追加 E0372；TASK_STATUS 仅 TJ-013.3 行续写（状态保持「阻塞」）。

### 12.3 §7 门控翻转清单十项实际落地对照

| # | 审定目标态 | 实际落地 | 证据 |
| --- | --- | --- | --- |
| 1 | engine 客户端四研究键门禁不变 | `engine.py` 未改动一字；密封专项以真实域执行复测四键逐字报错（含 conflict/readable 两键值无关门禁） | `ClientGateRealPathTests` |
| 2 | `_bazi_profile` 输入契约不变 | 契约校验代码未动；另在开启门前对 `strength_variant == 'bazi-strength-adjudication-v1'` 显式以基线原文报错（见 §12.7 决定一），夹带研究键与裁定变体的拒绝行为与基线逐字一致，公开专项钉住 | `ClientGateTests`（公开） |
| 3 | 服务端开启门新增（恰两 assessment） | `_bazi_profile` 服务端构造执行输入、恰置 `tiaohou_variant`/`bingyao_variant` 两键并以 `allow_research=True` 执行同一 chart；信封 trace 恰 +2 步、rule_matches 恰 +2 条（等价比对实测） | 密封 `EquivalenceTests` |
| 4 | 两 Variant 与 readable Variant 标志不翻转 | 三模块未改动；治理测试逐字钉（含功能层断言）保持通过 | 治理测试 `test_variants_keep_research_flags_unflipped`、`test_variant_statements_functionally_research_only` |
| 5 | 投影定域放行（原料键剥离不变） | 三原料键 + conflict 键 pop 保留，新增 `xiyong_presentation` 全域 pop；唯一放行 = 信封 `scenario_id == 'bazi-profile'` 且 `is_valid_public_presentation` 通过的逐字副本回填 `result`；其余场景/形态不符/域路径 chart 容器均剥离，公开专项四例钉住 | `ProjectionScopeTests`（公开）+ 密封真实信封投影对平 |
| 6 | readable 及其 chart 级联门不变 | `bazi_xiyong_readable.py`、`bazi_chart.py` 未改动；公开路径不调用 readable（呈现节文本由新构建器自两份陈述独立生成） | 文件零 diff（PR 文件清单） |
| 7 | `claim_capabilities` 不变 | 未改动 | 文件零 diff |
| 8 | ExplanationService / AI 通道不变 | 未改动；新对象 `ai_enabled=False` 恒在，形态校验器钉住 | 构建器常量 + `is_valid_public_presentation` |
| 9 | 页面文案收窄（176 行必改） | 第 176 行改为「不自动定格局；调候与病药只呈现已注册依据，不作统一喜用结论」；117/313 行经复核逐字保留（其口径为「通用喜用神结论未建成」，与本阶段呈现证据依据不冲突，属只许收窄而非必改）；244 行旺衰边界文案未动 | 公开专项 `FrontendWiringTests`（带存在性守卫）+ 浏览器专项 |
| 10 | 扶抑、格局用神保持关闭 | 呈现对象无两体系段与键；仅范围声明一处以「尚未建成」语境提及（§4.6 第 2 项豁免口径）；G9 全域扫描与 G10 键集递归扫描钉住 | `test_no_banned_content_anywhere`、`test_no_research_or_unopened_system_keys` |

审定批治理测试的两处状态转换钉（§7 预告）已更新并注明依据 E0371：(1) 零引用钉改为——场景层引用 tiaohou/bingyao/xiyong_presentation 与构建器为审定内行为，readable_hints/conflict_presentation 在场景层仍零引用，api.py 六 token 仍全零；(2) 剥离表钉新增 xiyong_presentation 全域 pop 与定域放行三断言（三原料键 pop 保留）。

### 12.4 §9 验收清单八项逐项结果

1. **契约差异恰为 §7 所裁**：成立，见 §12.3 十项对照；七项不变项中 engine/契约/标志/claim/AI 五项有测试或零 diff 证据，readable 级联与 claim 为文件零 diff。
2. **字段与 §4 逐字对平**：成立。顶层键集封闭（形态校验器按 §4.1 键集恒等校验）；调候块 sequence/branches 逐字、branches 只含已编码分支（Golden 断言 unencoded/related 引文不入对象）；病药块两对恒带 determination=None、medicine_effect_status='unadjudicated'、efficacy_state='not_judgeable'；关系段只取调候×病药（旺衰 incomparable 与扶抑/格局 absent 事实不入，由查表构造法保证：关系段只读两块已呈现字段）；§4.6 禁入十项由 G9/G10 扫描 + 形态校验 + 投影剥离共同钉住；§5 三类暂不可判各有形态测试（N1=G3、N2=G2/G6 conflict 项、N3=范围声明常量 + 对级 efficacy_state + 条目级限制条目）。
3. **Golden G1–G11 落地**：成立，见 §12.5；公开专项已按名接入 validate.yml；refs 恰等入密封专项（`BundleReferenceIndexTests`：调候 10 规则恰 r042–r051、refs 对恰 120；病药 r040 恰 4 对全锚 s071；并与独立 EvidenceResolver 读数逐项对平）。
4. **等价比对**：成立。封闭差异清单 = result 新增 `xiyong_presentation` + `tiaohou_assessment` + `bingyao_assessment` 三键、trace +2 步、rule_matches +2 条、evidence 新增条目（必为两步绑定集的子集）；清单外差异 0——密封 `EquivalenceTests` 以 4 组输入（含页面实际发送的 strength_variant）逐封套深等价实测，`production_scope` 经还原后逐字相等（见 §12.7 决定二）；其余九场景信封与投影递归扫描无呈现键与原料键（`OtherScenariosUnchangedTests`）。前端既有行为除 §4.7 文案与新节外零改动（页面 diff 仅限新增状态、提交后场景拉取与三处呈现插入）。
5. **机上全配方复跑**：见 §12.6。本批未触密封资产（PR 文件清单无 data/ 与密封路径），无换代。
6. **前端同批落地**：成立。呈现节真实渲染两块 lines + 关系段 + 关闭行；第 3 层短引取自呈现对象 evidence（与 evidence.quote 逐字一致由对象同一性保证）；浏览器专项为 **stub 契约**性质并已如实标注——回放响应录制自组装后真实后端（2026-11-01，G1 盘，生产 runtime），专项头注与工作流步骤名均明示；本地真实 Chromium + 真实 dev server 实跑 2/2 通过。页面全域无 Rule ID/Trace ID 文案（呈现节只渲染 lines 与结构化转写，技术 id 不入页面）。
7. **台账**：E0372 已追加（归属 TJ-013.3、状态「阻塞」、后三列「—」），TASK_STATUS 仅动 TJ-013.3 行；关账对平清单见 §12.8，供 E0373 消费。
8. **§3.3 处置明示**：选定「场景请求报错」，见 §12.1 第 3 问与密封 `FailureDispositionTests`。

### 12.5 Golden G1–G11 落地与推导记录

- G1–G6 沿在册同盘（事实取自组装后真实执行的 trace 步输出：四柱、十神、藏干逐项录入 Golden 的 facts 段）；期望 lines 按 §4 定稿模板逐行手工核对后钉入（每行干名/次序/位置/角色与 facts 段逐项对位，§6.2 第 4 项）。
- **G7 构造推导**（本批新构造）：1949-01-01T01:00+08:00，真实历法得 戊子/甲子/辛卯/己丑，辛日主子月。病药第一对：主体财 = 月干甲（正财）显，病之比劫（庚/辛）四柱显干未见 → `peer_god_not_visible`；第二对：主体食伤（癸）仅藏于子支（藏干事实），显干未见 → `subject_foodwound_not_visible`（藏干不触发，沿病药显干限定）。两对未触发行齐备；对象中「无病」仅出现于否定式「未触发不等于无病」——§8 G7「无『无病』字样」的本批解释：禁的是断言式无病/有病判断，审定 §4.3/§5 强制的否定式护栏行保留，此解释在此登记。
- **G8 构造推导**（本批新构造，分支 `wuyue_fa_gui_yong_ding`，条件 = 癸缺席）：正例 1950-06-08T05:00+08:00 得 庚寅/壬午/甲戌/丁卯，甲日主午月，癸于四柱天干与全部藏干（寅甲丙戊/午丁己/戌戊辛丁/卯乙）均未见 → applied=True，分支序列 [丁1 透时柱， 庚2 透年柱]；对照例 1949-06-13T01:00+08:00 得 己丑/庚午/甲戌/乙丑，癸藏于年、时两丑支 → applied=False，主序列为准。两例条目节均为 s080、同属 r042；甲×午另有 unencoded 分支 1 条，Golden 断言其引文不入对象。G4（丙×寅）unencoded 1 条、G6（甲×戌）related 1 条同样以引文缺席断言钉住。
- G9：Golden 全 9 例对象的系统自撰文本（lines、关系行、条件事实、范围外文本）全域扫描零命中（逐字原文 quote 与条目 order_basis 为注册文本、由逐字钉管理而豁免措辞扫描——辛×子条目原文含「切忌」即其例；范围声明为唯一登记豁免语境且以恒等常量钉住）；新增页面自撰文案（关系转写标签、节标题、边界行）经浏览器专项与源码钉核对不含禁入词。
- G10：键集递归扫描（公开专项）+ 客户端契约拒绝（公开专项，拒绝发生在执行前）+ 真实域路径四键拒绝（密封专项）+ life 等九场景零泄漏（密封专项）。
- G11：篡改四类在公开专项以合成视图实测（改 quote 一字、改记录 section_id、改 Phase1 归属至同体系另一规则——由同章性核对捕获、删 evidence 绑定），另加 rule_match 证据漂移与陈述标志翻转两例；真实 API 对平在密封专项（TestClient 对组装后端：响应呈现对象与场景层执行逐字相等、evidence 引文在同一信封内按步绑定唯一定位）。

### 12.6 复跑与计数对平

- 基线（开工直读正式验收，`6db7b578`）：SUCCESS 2908（15 + 24 + 2869），skip 5。
- 本批复跑（机上组装全配方 `accept_offline.py --suite all`，对象 = 本批分支 HEAD 的真实 git checkout + 现行密封快照）：SUCCESS、0 失败，总测 **2937**（private-backend 2898），skip 6。增量 +29 逐项对平：公开专项新模块 +20（其中前端源码守卫 1 测在组装树无 web/ 而 skip，故 skip +1）、密封专项新模块 +9；治理钉更新为断言形态转换、测数不变（7）；其余模块逐项与基线一致。知识清单钉不变（`26b63e64…`），无换代。
- 分支复跑仅作对账；可引用计数以部署管线对合并 SHA 的正式 acceptance 记录为准（关账批 E0373 对平）。

### 12.7 实施决定与审定外发现（均已在上文各节登记，此处汇总备查）

- **决定一（开启门防泄漏）**：若 `_bazi_profile` 整体改走 `allow_research=True`，客户端 `strength_variant='bazi-strength-adjudication-v1'` 将由基线的 engine 报错变为直达 chart 裁定，违反 §7 第 2 项「夹带行为与基线逐字一致」。处置：开启门前显式以基线原文（`Bounded strength adjudication requires explicit research mode`）拒绝该值；其余 strength 值仍经 chart 既有校验，行为不变。此为保住审定不变项的必要接线，非契约扩张。
- **决定二（production_scope 还原）**：开门后 chart 向 `production_scope` 尾部追加两 assessment 的研究条款，且条款文本随执行 runtime 而异（公开源码为英文条款、生产 runtime 为中文条款），不得硬编码。处置：同请求以原输入再行一次未开门执行取基线 scope，断言开门 scope 以其为真前缀且严格更长，随后还原基线值；任一关系不符即 fail-closed。等价清单因此字面成立。
- **决定三（关系段关闭行的承载）**：「各体系陈述并列呈现，系统不作统一裁定。」以顶层字段 `relations_closing_line` 承载（§4.1 仅对 blocks 声明键集封闭，顶层字段表未列此行），前端在关系段末渲染。
- **决定四（前端数据路径与审定 §2.6 的事实出入）**：实测 `BaziProfilePage` 走域端点 `/api/v1/public/execute` 而非场景端点，审定 §2.6 对页面数据路径的设想与现行实现不符。处置（加法式）：后端严格按审定落场景层；页面既有域执行渲染逐字不动，另经新增 `executeBaziProfileScenario` 拉取场景信封渲染新节；场景调用失败时新节缺席、既有行为不变。页面不直接消费研究对象，呈现对象仍是唯一新增消费面。
- **决定五（前端响应断言）**：`api.ts` 既有 `assertScenarioResponse` 只服务八个 production_limited 场景（LIMITED_SCOPES 无 bazi-profile），故为本场景新增专用断言 `assertBaziProfileScenarioResponse`（校验 production/public_release=true 的发布契约形态），既有断言函数未改动。

### 12.8 E0373 关账对平清单（供关账批逐项消费）

1. 部署管线对合并 SHA 的正式 acceptance：SUCCESS 且总测 = 2937（或与 §12.6 增量逐项对平后的解释值）；deploys.log 出现该 SHA 的 DEPLOYED 且 pin 仍为 `26b63e64…` 系（本批无密封变更，pin 不应变化）。
2. 生产实测：`POST /api/v1/scenarios/public`（bazi-profile，G1 盘）响应含 `xiyong_presentation` 且与 §12.5 G1 期望 lines 逐字一致；公开响应无四原料键。
3. WBS 验收口径对平（TJ-013.3 行文「适用范围明确的用户可读提示」）：本阶段呈现的每条解释均源自同请求 Phase2 执行记录并经 Golden G1–G11 钉住——「前端只有真实经过 Phase2/Golden 的条件才出现解释」在本阶段范围内成立；行状态处置建议材料：第一阶段（调候+病药可读呈现）子项已达「已部署验收」口径，但 TJ-013.3 本体仍含跨体系裁决（TJ-013.2 未建）与扶抑/格局（U1/U3 暂缓）未清前置，行总体是否维持「阻塞」由 E0373 按此事实决定，本批不预判。
4. 用户否决面：本批前端新增为既有八字页内的新节呈现（非新增控件），随本 PR 交付报告向用户呈报；第二阶段 TJ-017.3 未启动，不在本批范围。
