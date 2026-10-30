# TJ-018.3 执行绑定设计批（E0332）：三刑事实层与干支三谓词的统一执行绑定机制设计

- 授权来源：用户 2026-10-30 裁定——后续顺序定为「执行绑定设计 →
  三刑执行接入 → 卷二干支三规则实施 → 阳刃重新评估」，并授权启动
  本设计批。本批严格限定为**设计与只读追踪**：不修改任何生产判定
  逻辑、不翻转任何 evidence_binding、不动 Canonical 原文与快照、
  不解锁扶抑 U1/U3、不解锁八格真假或完整三刑效力、不改动公开用户
  结果与 AI 解读边界。**本文件是设计稿，不是实现记录**；文中一切
  「拟定」ID 与接口均为待实施批确认的设计提案，未注册、未生效。
- 入册形制：本文件与 P1 治理文档、P2 补审文档同列
  `docs/product/`；机器可读登记不在本批变更（治理登记册的翻转属
  实施批）。

## 0 基线与方法

- 基线：live main `a60df8a2477ba546993021a84663681eb275233b`
  （Merge PR #508），台账 331 事件（末事件 E0331）。开工经
  GitHub API 实时核实一致；所引公开仓文件以该 SHA 的 blob 为准，
  基线四文件（TASK_STATUS、TASK_HISTORY、WBS、
  check_task_tracking.py）经 git blob 哈希与 live tree 逐一验合。
- 方法：只读程序化追踪——对公开仓 `src/tianji_kb/` 全域做符号级
  检索（引用点、定义点、调用点逐一落到文件与行号），并逐项与三份
  在册结论对账：P1 治理文档 `TJ0183_P1_SANXING_CANONICAL_PROMOTION.md`
  §3、治理登记册 `bazi_registration_governance.py` 的
  `sanxing-branch-fact-v1` 项、P2 补审
  `TJ0183_P2_GANZHI_ADJUDICATION.md` §6。密封侧实体
  （phase1_knowledge / phase2_execution / phase2_golden 的具体
  条目）不在公开仓，本设计只依据公开仓内的契约测试与登记册所钉
  的形制推断其结构，并在相应位置明示「实施批须在密封侧实测复核」。
- 快照钉值：现行 `305e20be…`（237 文件、15,902,169 字节），本批
  未触碰、设计正文不引用旧钉值。

## 1 现状追踪结果

### 1.1 执行链全景（在册代码实证）

| 环节 | 在册实体 | 形制 |
|---|---|---|
| Provider 注册 | `engine.PROVIDERS`（`src/tianji_kb/engine.py:15`）：七域一律 `tianji_kb.operations.<domain>_chart.chart` | Golden harness 只认此注册（见下） |
| 执行入口 | `engine.execute(domain, inputs, variant=None, *, allow_research=False)`（`engine.py:82`） | 研究型输入（strength_variant=裁定 Variant、pattern/tiaohou/bingyao/conflict/readable Variant、annual 参考等）逐项在入口处以 `allow_research` 门禁（`engine.py:86-98` 一带）；API 生产路径 `api.py:775` 以 `allow_research = (mode == 'research')` 调用、`:749` 内部路径恒 False |
| 证据解析 | `EvidenceResolver`（`src/tianji_kb/resolver.py:12`）：生产经 `runtime_catalog.load_catalog` 载入 model/contracts；复核模式经 `validate_knowledge` 全量校验后逐域载入 `data/canonical/*/phase2_execution.json` 并做契约校验（rule id 唯一、域/变体一致、id 须以 `<domain>.phase2.` 起、phase1_rule_refs 必须指向已知 Phase1 rules 实体） | `resolve(rule_id, variant)`：取规则的 source_refs（或经 phase1_rule_refs 汇聚），逐条校验来源为 classical 且证据级非 D、引文 `original_text` 为 section 文本子串且 section 的 source 与来源一致，通过后产出带 classic/chapter/locator/commit/sha256/evidence_level 的证据记录 |
| 执行追踪 | `ExecutionTrace`（`resolver.py:98`） | `add(rule_id, inputs, output)`：先 `resolver.resolve` 解析证据（解析失败即抛错、整次执行 fail-closed），证据按内容哈希（sha256 前 24 位）入 `evidence` 字典，再追加 step `{rule_id, evidence_scope, inputs, output, evidence_ids}` 并返回 output；`match_steps(matches)`：RuleMatch 的 rule_id 必须已在 steps 中（原文断言 `RuleMatch must refer to an executed rule`），产出 `kind='executed_calculation'` 的已执行步与 `kind='algorithm_selection'` 的选择步；`finish(result, matches)` 产出封套 `{domain, variant, deterministic: True, result, trace, rule_matches, evidence, interpretation_contract}` |
| Bazi provider | `operations/bazi_chart.py:chart()`（333 行） | 顺序：历法链 `chart_from_pillars` → 基础事实步（pillars/ten_gods/hidden_stems）→ 可选咸池 → 可选配偶星 lens → 可选关系事实块（`include_relations` 门控，五合/六合/六害/六冲/三合/配偶宫六步，均为已注册 Phase2 步）→ strength_factors 步组 → 月令口径步组 → 条件旺衰链（root_conditions → root_availability → action_conditions → action_effects → 裁定 gate 步 `strength_bounded_adjudication`/`strength_adjudication`）→ 流年参照步组 → 大运候选（**非 trace 步**）→ 格局候选步 + 禄刃路线/杂气陈述（**非 trace 步**，注释明示无注册不得入 RuleMatch/Evidence）→ 调候/病药/冲突呈现/可读提示（**非 trace 步**，同上）→ `trace.finish(result)`；任一研究面开启时封套追加 `research_only=True` 且 `interpretation_contract.ai_may_explain=False` |
| Golden harness | `golden.run_cases`（`src/tianji_kb/golden.py:25`） | 遍历密封 `data/canonical/*/phase2_golden.json`，校验 provider 与 `PROVIDERS[domain]` 及同目录 `phase2_execution.json` 的 provider 三者一致、provider 必须以 `tianji_kb.operations.` 起；逐 case 以 `function(**case['input'])` 真实执行 provider，`assert_subset(execution['result'], case['expected'])`，且要求 trace 与 evidence 均非空；返回每 case 的 trace rule_id 列表 |
| 注册契约 | `tests/test_phase2_baziregistration.py`（密封侧验收运行） | 钉住：注册步在 bazi Phase2 契约内、`execution_status='executable'`、`validation_status='validated'`、`phase1_rule_refs` 恰为其 Phase1 规则、`regression_test` 指向本文件、`golden_case_ids` 非空；Phase1 规则经 resolver 解析到非 D 级证据；Golden 用例的 trace 中**真实出现**其注册步（fire 断言）；见证盘裁定 `why.sufficient_rule` 等于注册步 ID 且无 pending 披露残留 |

### 1.2 r026 旧出口的实证形态（三谓词当前路径）

- 裁定在 `bazi_adjudication._bounded_assessment(trace)`（由
  `strength_assessment` 在 ADJUDICATION_VARIANT
  `bazi-strength-adjudication-v1` 下分派）内发出；其消费的事实全部
  来自已执行步：每条 condition 以
  `{condition, met, fact_ref: '#/action_effects/...', rule_id:
  'bazi.phase2.action_effects', evidence_ids: <action_effects 步的
  evidence_ids>}` 绑定（`bazi_adjudication.py:443-450` 等各分支
  同形），即三谓词的**条件证据已在 Trace 内**，此点与 P2 §6
  「ExecutionTrace 覆盖：满足」逐字相符。
- 已注册谓词分支（pure_generating / commanding，及更早的
  pure_support / isolated_control）：分支内执行
  `trace.add('bazi.phase2.strength_' + predicate, {strength_variant,
  factor_refs}, {classification, variant, conditions})`，随后
  `why = {'sufficient_rule': <该步 ID>, 'conditions': conditions,
  'all_required_conditions_verified': True, 'excluded_dependencies':
  [...]}`（`bazi_adjudication.py:446-455`、`458-479`）。其 Phase1
  规则（r029/r030）不在裁定对象上出现，而是经 Phase2 契约的
  `phase1_rule_refs` 与治理登记册记载（`bazi_registration_governance.py:179-180` 等）。
- 未注册谓词分支（lu `bazi_adjudication.py:484-514`、changsheng
  `:517-563`、S2 metal/water `:566-614`）：**不执行 trace.add**，
  `why = {'sufficient_rule': None, 'sufficient_predicate': <谓词名>,
  'predicate_rule_registration': 'pending_phase1_rule_registration',
  'conditions': conditions, ...}`，注释原文自述「经已注册的有限裁决
  出口（bazi.rule.r026）发出」。该「出口」在 chart 层的实体是裁定
  之后的 gate 步 `bazi.phase2.strength_bounded_adjudication`
  （`operations/bazi_chart.py` 条件旺衰链尾端 `trace.add('bazi.phase2.'
  + gate, ...)`）；r026 是该出口的 Phase1 规则编号，公开代码注释
  （`bazi_adjudication.py:490/520/567`）与治理登记册
  （`bazi_registration_governance.py:335` 将 r017/r020/r026 并列为
  已注册覆盖规则）同此指称；其契约绑定（phase1_rule_refs）在密封
  侧，实施批须实测复核（见 §10）。
- 裁定尾部（`bazi_adjudication.py:616-640`）：`matched_rule_ids`
  只从固定的 `relevant` 步集合中收集——现含
  `strength_pure_support / strength_isolated_control /
  strength_pure_generating_support /
  strength_commanding_visible_support` 四个已注册裁定步，**不含**
  任何未注册谓词（它们本就无步）；`decision_status` 为
  `reviewed_sufficient_rule_matched`（有 why 时）/
  `insufficient_reviewed_rules`； limitations 文本逐谓词写明注册
  状态（已注册两条与 pending 诸条分列，`:636-640` 一带）。

### 1.3 三刑事实层的实证形态

- 定义点唯一：`bazi_sanxing_facts.py:reviewed_branch_punishment_facts(branches)`
  （签名：四柱支列表 → `{directed_pairs, group_configurations,
  self_punishments, names: None}`）；每次调用先
  `_ensure_registration()` 逐条核验审定登记完整性，不一致即
  `RuntimeError('registration_integrity_failure: ...')` 拒绝产出
  （fail-closed 在函数内自备）。
- 引用点程序化检索（`src/tianji_kb/` 全域，检索式
  `reviewed_branch_punishment_facts` 与 `branch_punishment`）：
  命中文件恰 4 个——`bazi_sanxing_facts.py`（定义）、
  `bazi_sanxing_fact_adjudication.py`（审定登记文本提名，
  `:783` placement_decision）、`bazi_registration_governance.py`
  （治理登记）、`public_projection.py`（防御剥离）。**生产调用点
  为零**，证实 P1 §3.1。
- 公开投影：`public_projection.py:301-306` 对结果容器
  `pop('branch_punishment_facts', None)`，注释明示该键为研究级
  事实层、public_enabled=false——即投影层早已按「未来 chart 结果
  可能携带 `branch_punishment_facts` 键」预置了剥离，键名与本设计
  §2 的拟定结果键一致；当前生产产出从不携带该键，剥离为纯防御。
- 审定登记的 placement 原文（`bazi_sanxing_fact_adjudication.py:783`
  一带）：「独立函数……与既有 reviewed_branch_pair_relations
  并列；切片一期不改写 reviewed_relations / branch_relations 的
  既有输出键（避免既有消费面无声变化），**是否并入其输出另批
  审定**」；SLICE_SPEC.registration 与 consumption_boundaries
  明示一期「不建 Phase2 规则、不进 unresolved_interactions」。
  本设计 §2 的推荐正是该「另批审定」的标的；实施批须以追加事件
  显式承接此 placement 点（见 §10 第 3 项）。

### 1.4 已注册规则全链路抽样（设计模板）

以 r029（木×亥 pure_generating_support）为正例的全链路：

1. Phase1 定义：密封 `phase1_knowledge.json` 内 `bazi.rule.r029`，
   source_refs 只引 Canonical 内可验引文子集（治理登记册 reason
   原文：定义锚点全部在 Canonical 内、与 r024 引用集同构；
   r030 先例进一步钉明：登记引文中不在 Canonical 的三条**不被
   规则引用**，规则只引 Canonical 子集）。
2. Phase2 契约：密封 `phase2_execution.json` 内
   `bazi.phase2.strength_pure_generating_support`：
   executable/validated、`phase1_rule_refs=['bazi.rule.r029']`、
   `regression_test='tests/test_phase2_baziregistration.py'`、
   `golden_case_ids` 非空（契约测试断言形制如上）。
3. 执行：`_bounded_assessment` 分支内 `trace.add` 该步，
   EvidenceResolver 在 add 时即解析 r029 的 source_refs 并逐条验
   子串（解析失败整次执行抛错）；step 落 trace，
   `why.sufficient_rule` 等于该步 ID，`matched_rule_ids` 经
   `relevant` 集合收录。
4. Golden：密封 `phase2_golden.json` 用例
   `bazi.adjudication-strong-hai-generating` 经 harness 真实执行
   chart 并断言 trace 含该步（fire 断言）；见证盘
   （1983-12-02）在注册契约测试中复核 classification 与
   sufficient_rule。
5. 治理：登记册行 disposition=registered + phase1/phase2 ID 对
   （`bazi_registration_governance.py:171-183`），翻转的判定面变化
   面在 S5_REGISTRATION_RECORD.verdict_surface_change 中被钉为
   「仅 why.sufficient_rule、matched_rule_ids 与披露文本」
   （`:65-68`）——此即 §7 等价口径的先例来源。

对照抽样（普通事实步）：关系事实块的
`bazi.phase2.branch_six_harmonies` 等步——在 chart 内以
`trace.add` 发出、输入为 stems/branches 原始事实、输出为事实
子集，其 Phase1 依据（干合事实 r005 一系）早已注册；它们证明
「纯事实、无裁定」的步同样走 trace.add + 契约 + Golden 的同一
机制，三刑步不需要新机制，只需要同形注册。

### 1.5 与 P1/P2 在册结论的对账

| 在册结论 | 本批追踪结果 |
|---|---|
| P1 §3.1 事实函数零生产调用点 | **相符**（§1.3 全域检索复证） |
| P1 §3.2 不经 ExecutionTrace、无 RuleMatch | **相符**（函数自备登记核验但不产 trace；且 `match_steps` 的「RuleMatch 必须指向已执行步」断言使未执行步在结构上不可能被匹配） |
| P1 §3.3 harness 只执行 operations provider | **相符**（`golden.py:33-39` 三重钉死） |
| P1 §3.4 翻转标准 = Phase1 规则 + Phase2 步 + 见证盘经注册步发出三者齐备 | **相符**（注册契约测试逐项即此三者；S5 两谓词全链路如 §1.4） |
| P1 §3.5 审定消费边界「不建 Phase2 规则」 | **相符且为实施前置**：该边界是 E0267 一期审定口径，placement 本身预留「另批审定」；本设计不改动它，实施批须显式承接（§10.3） |
| P2 §6 三谓词 Trace 覆盖满足、经 r026 出口、sufficient_rule=None、无自有规则步 | **相符**（§1.2 逐项落到行号；P2 所引 `tests/test_phase2_baziadjudication.py` 只断言 `strength_adjudication` 在场一节亦复核相符，该文件 `:18`） |
| P2 §6 金×酉无真实盘正例、Golden 须按构造性不可满足口径 | **相符**，且构成 §3.4 的负例 Golden 设计问题（注册契约的 fire 断言对本谓词无适用对象） |
| 晋级审计 §4.3「晋级还缺 ①Canonical section ③Term」 | **已被 P1 关闭的历史项**：s060 与 term 已建（E0329）；剩余缺口只有执行绑定一项，与 P1 终局结论一致，不构成出入 |

**对账结论：与 P1/P2 在册结论无出入。** 唯一需要点名的口径细节：
P2 所称「r026 出口」在代码中的实体是 chart 层 gate 步
`bazi.phase2.strength_bounded_adjudication`，r026 为其 Phase1
规则编号的指称（公开注释与登记册同此用法），其契约绑定在密封
侧——本设计沿用此指称并把密封侧复核列入实施批前置（§10.5）。

## 2 三刑接入点设计

### 2.1 候选接入点逐个分析

**候选 A：operations provider 内接入（`operations/bazi_chart.chart`）**

- 形态：在 chart 的关系事实块之后、旺衰因子步之前（事实族位置、
  「裁决前」定位与 SLICE_SPEC.layer 原文一致），以新门控参数显式
  开启时执行 `reviewed_branch_punishment_facts(branches)` 并
  `trace.add(<新 Phase2 步>, {'branches': branches}, facts)`，
  结果挂 `result['branch_punishment_facts'] = facts`。
- 对生产产出表面：默认（未开启）路径**逐字不变**——不新增步、
  不新增键、不改封套；开启路径只**新增**一个 trace 步、一个
  result 键、该步的 evidence 条目与 rule_matches 中该步的
  executed_calculation 条目（§7 钉死）。先例同形：关系事实块
  以 `include_relations` 门控、咸池以 `include_xianchi` 门控。
- 对公开投影：投影已有同名键剥离（§1.3），且本步开启条件拟与
  研究门禁绑定（§2.3），公开面双重无感。
- 对既有 Golden：harness 以 case input 调用 provider；既有 case
  不带新门控参数，结果子集断言与 trace/evidence 非空断言均不
  受影响；新 case 可直接以开启参数断言 result 子集与 fire。
- 前提成本：须先有 Phase1 规则与 Phase2 契约步（trace.add 在
  解析证据失败时抛错，无注册即无法 add）——这正是本设计要补
  的注册实体本身，非额外负担。

**候选 B：裁定/组合层接入（bazi_pattern 式旁路）**

- 形态：照 pattern_route / pattern_zaqi / tiaohou 先例，在 chart
  或组合函数内旁路计算并挂 result，不进 trace。
- 否决理由：该形态在结构上**不可能**满足注册契约——
  `match_steps` 断言 RuleMatch 必须指向已执行步、注册契约测试
  要求 Golden trace 中真实出现注册步；旁路产出永远无法 fire
  注册步，接入后 evidence_binding 仍只能维持 pending，等于把
  现状换个位置重演。这正是 P1 §3 否决「只建 Phase1 声明规则」
  的同构情形。

**候选 C：scenario 层接入**

- 形态：scenario_engine 在场景组装时调用事实函数挂入场景结果。
- 否决理由：场景层无 ExecutionTrace（场景是对 execute 封套的
  二次组装），同样无法产生可注册的执行步；且先行扩大的是公开
  消费面（与「事实层不接公开场景」的现行边界正面冲突），影响
  面最大、注册收益为零。

### 2.2 推荐（唯一）

**推荐候选 A**：在 `operations/bazi_chart.chart` 内、关系事实块
之后以显式门控参数接入为已注册 Phase2 事实步。理由一句话：
只有 provider 内的 trace 步能同时满足注册契约的 fire 断言、
ExecutionTrace 证据绑定与 Golden harness 的 provider 限定三项
硬约束，而门控默认关闭使默认生产表面逐字不变、等价证明面
最小。

### 2.3 接入细则（设计提案，实施批确认）

- 门控参数：拟定 `include_punishment_facts: bool = False`
  （命名与 `include_relations` / `include_xianchi` 同族）；
  `engine.execute` 对该参数加 `allow_research` 门禁（照
  `:86-98` 既有逐项门禁先例），生产模式（allow_research=False）
  传 True 即拒绝。开启时封套追加 `research_only=True`、
  `ai_may_explain=False`（照 chart 尾端既有研究面处理块）。
- 执行位置：关系事实块之后（同为地支事实族）、strength_factors
  步组之前；输入 branches 取四柱支（与关系块同源变量）。
- 结果键：`branch_punishment_facts`（与投影剥离键、事实层
  披露键同名，非新造）。
- Trace 生成方式：`trace.add('bazi.phase2.branch_punishment_facts'
  （拟定）, {'branches': [...]}, facts)`；step.output 即事实函
  数返回 dict **逐字**（directed_pairs / group_configurations /
  self_punishments / names=None），不加任何裁定包装字段。
- fact 与 determination 的分字段：本步是**事实步**——其 output
  只含结构事实字段（白名单由事实层既有测试钉住：吉凶/成否/效
  价/程度/评分/名目键出现即失败）；它**不产** why、**不产**
  classification、**不得**被任何 RuleMatch 以
  algorithm_selection 形式引用为裁定依据、**不得**进入任何
  `sufficient_rule`。未来教义层消费（如 B4 破格审定）只能以
  `fact_ref` 引用本步 output 作为事实输入另行审定，与旺衰条件
  绑定 action_effects 的既有形态同构（§5）。
- fail-closed 链：事实函数自备的登记完整性核验
  （RuntimeError）在 add 之前执行——核验失败则整个 execute
  抛错、不产出部分封套，与 trace.add 的证据解析抛错同为
  fail-closed 语义，无需新机制。
- 拟定注册身份：Phase1 规则拟定 `bazi.rule.r031`、Phase2 步
  拟定 `bazi.phase2.branch_punishment_facts`（均为**拟定、
  未注册**；r031 的编号以实施批在密封侧实测 Phase1 规则最大
  编号为准——P1 关账时 rules 计数为 30，若其间无新增则 r031
  为下一编号，被占用时顺延并回改本设计引用）。

## 3 三谓词规则步设计

### 3.1 共同形态：照已注册分支的原样同构

三谓词的实施形态在 `_bounded_assessment` 内已有完整模板
（§1.2 已注册分支）：实施批对 lu 分支与 S2（metal/water）分支
做且仅做以下同构改造——

1. 分支内在组装 conditions 后执行
   `trace.add('bazi.phase2.strength_' + predicate, {'strength_variant':
   ADJUDICATION_VARIANT, 'factor_refs': [...]}, {'classification':
   classification, 'variant': ADJUDICATION_VARIANT, 'conditions':
   conditions})`（inputs 的 factor_refs 组装照已注册分支的
   `pointer(k) for k in keys` 形态，实施批逐分支对齐）；
2. `why['sufficient_rule'] = <该步 ID>`，删除
   `sufficient_predicate` 与 `predicate_rule_registration` 两键
   （注册后披露形态与 r029/r030 见证断言一致：`assertNotIn
   ('predicate_rule_registration', why)`）；
3. 裁定尾部 `relevant` 集合增列三步 ID（`matched_rule_ids` 与
   `fact_refs`、`evidence_ids` 由此自然收录，机制不变）；
4. limitations 文本中三谓词的 pending 句改为已注册句（照
   `:636-637` 已注册两句的句式逐谓词改写，其余 limitations
   逐字不动）。

conditions 本身**逐字不变**：其 fact_ref、rule_id
（action_effects）、evidence_ids、anchor_type、
anchor_registration、month_root_grade、root_grades 在 §1.2
现状下已完备，注册不触碰条件逻辑与因子计算（P2 §6 总结论：
「验收对象是新规则步与 r026 出口裁定逐盘等价，而不是重新
验证谓词逻辑」）。

### 3.2 逐谓词注册身份与证据绑定（拟定）

| 谓词 | Phase2 步（拟定） | Phase1 规则（拟定） | Phase1 source_refs 绑定范围 |
|---|---|---|---|
| lu_visible_support（丙×巳） | `bazi.phase2.strength_lu_visible_support` | `bazi.rule.r032` | P2 补审 §7 实施批范围：卷二禄句主锚（列举级）+ 框架引文；滴天髓侧定义锚须实施批内另核（核不通则本谓词单独保留 pending，P2 在案条件）；卷三禄节非本谓词定义锚、不作前置 |
| pure_support_metal（金×酉） | `bazi.phase2.strength_pure_support_metal` | `bazi.rule.r033` | 五干消费锚点中的庚/辛逐干生死句（庚酉推步级、辛酉明句分级随行，P2 §1/§3）；辛 conflict 三格（子/巳/申）阻断原样保留、不入绑定 |
| pure_generating_support_water（水×子） | `bazi.phase2.strength_pure_generating_support_water` | `bazi.rule.r034` | 壬/癸逐干生死句；癸 conflict 三格（卯/申/亥）阻断保留；壬侧不可满足随注册记录明记（§3.4 同理） |

绑定通则（照 r029/r030 先例钉死）：

- Phase1 规则的 source_refs **只引 Canonical 内可验引文**——
  前置是批二先行建成卷二干支两节的 Canonical section 并完成
  P2 审定的绑定范围（丙/庚/辛/壬/癸五干锚点 + 节二框架引文）；
  丁锚点永不入任何 source_refs（绑定排除断言
  `source_refs ∩ {sm2.ding_sheng, sm2.ding_shengsi} = ∅`，
  P2 §4 在案）；□1 所在句与 lunyue_summary 尾段
  [42116,42151) 永不入绑定（P2 §5 三条机检断言随批落实）。
- 帝旺代偿的框架推步等级（framework_derived）随注册记录与
  条件中的 grade 字段随行披露，永不与 per_stem_listed 混同
  （P2 §2 定稿措辞与禁用表述在实施批逐字沿用）。
- 编号 r032–r034 为**拟定**：以批二实施时密封侧实测最大编号
  顺延（批一先行占用 r031 的前提下），被占用时顺延并回改
  引用；步 ID 的命名与 S5 公开测试、注册契约测试中已出现的
  期望 ID 逐字一致（`tests/test_phase2_baziregistration.py`
  的 pending 断言正是以
  `bazi.phase2.strength_pure_generating_support_water` 之名断言
  其**尚未**注册——实施后该断言须由实施批改为注册形态，
  属预期内的测试迁移，不是断言放宽）。

### 3.3 Trace 字段清单（三谓词步）

步的 inputs/outputs 与已注册两步逐项同形（§1.4 模板）：
inputs = `{strength_variant, factor_refs}`；output =
`{classification, variant, conditions}`，conditions 每条 =
`{condition, met, fact_ref, rule_id: 'bazi.phase2.action_effects',
evidence_ids, anchor_type, anchor_registration}`，metal/water
的月份/root 条件另带既有 `month_root_grade` / `root_grades`
（逐字保留）。证据侧：trace.add 时 resolver 经契约步的
phase1_rule_refs 解析对应 Phase1 规则的 source_refs，产出的
evidence 条目即 §4.2 表的证据字段集。

### 3.4 金×酉的负例 Golden 设计（与 fire 模板的偏离点）

注册契约对 r029/r030 的口径是「golden_case_ids 非空 + 用例
真实 fire 注册步」。metal 谓词八条件构造性不可满足（P2 §6
在册证明），不存在可 fire 的真实盘，故其 Phase2 Golden 必须
取**负例形态**，本设计给出如下拟定契约（实施批审定确认，
见 §10.1）：

- Phase2 步与 Phase1 规则照常注册（契约条目存在、
  executable/validated、phase1_rule_refs 恰为 r033）；
- `golden_case_ids` 指向一组**负例见证**：S2 因子层穷举扫描
  输入集与近失盘集——对其中每一盘断言：裁定步**不出现**于
  trace、classification 与 blockers 与旧出口逐盘一致（等价
  断言而非 fire 断言）；该组负例由密封侧注册测试执行（形制
  参照 `METAL_YOU_SATISFIABILITY` 在册证明的扫描口径），
  不入 `golden.run_cases` 的 result 子集断言通道（其 case
  语义是「不得 fire」，与 harness 的正例语义不同，强行入册
  即伪造正例）；
- 注册记录（治理登记册行）明记本谓词 Golden 形态为负例形态
  及理由，与 P2 §6「不得要求真实盘正例」一致。
lu 与 water 有真实见证盘（lu 唯一正例 1927-05-12、water 癸
正例 1981-12-21 与壬近失例 1921-12-15），照 r029/r030 模板
以正例 Golden 注册（近失例作等价集，不作 fire 用例）。

## 4 统一规则执行契约（设计稿 v1）

本节把 §1 实证到的既有机制收拢为一份可引用契约；它**不创设
新机制**，只把 provider / resolver / trace / 契约测试四处已
钉死的口径写成统一文本，供批一、批二实施时逐项对表。新注册
的四条规则（1 事实步 + 3 裁定步）全部适用本契约。

### 4.1 触发与执行

- 规则步只能经 `ExecutionTrace.add(rule_id, inputs, output)`
  在 provider 执行流内触发；触发前 resolver 必须能解析该步
  的证据（Phase2 步经 phase1_rule_refs 汇聚 Phase1
  source_refs；Phase1 规则直接取 source_refs），解析或校验
  失败（未知规则、变体不符、无 reviewed 证据、引文不可验、
  来源级别不合格）即抛错、整次执行 fail-closed，不产出部分
  封套。
- 事实步的触发另受其事实函数的自备核验约束（登记完整性）；
  裁定步的触发受其分支条件全真约束（条件有一不真即不触发，
  走弃判路径）。

### 4.2 Trace 记录字段全表（以 resolver.py 在册实现为准）

执行封套（`ExecutionTrace.finish` 产出）：

| 字段 | 类型 | 来源 | 用户可见 |
|---|---|---|---|
| domain | str | Trace 构造（'bazi'） | 经投影后部分可见 |
| variant | str | chart 的 variant（bazi_core.VARIANT，ziping-structural-v1） | 同上 |
| deterministic | bool（恒 True） | finish 钉值 | 否 |
| result | dict | provider 组装 | 经 public_projection 剥离研究键后可见 |
| trace | list[step] | add 追加 | 否（研究/内部） |
| rule_matches | list[match] | match_steps | 否 |
| evidence | dict[hash24 → ref] | add 解析 | 否 |
| interpretation_contract | dict | finish 钉值 + chart 研究面改写（ai_may_explain 等） | 否 |
| research_only | bool（可选） | chart 研究面开启时追加 | 否 |

step：`{rule_id: str, evidence_scope: str（规则自带）, inputs:
深拷贝 dict, output: 深拷贝 dict, evidence_ids: list[hash24]}`。
match：`{rule_id, variant, matched: True, kind:
'executed_calculation' | 'algorithm_selection', evidence_scope,
facts（executed 步的 output）, evidence_ids}`。
evidence ref：`{source_id, section_id, original_text, role,
rule_id, variant, classic_id, classic_title, chapter_id,
chapter_title, locator, source_url, commit, sha256,
evidence_level}`（补充证据另带 independence_status）。

### 4.3 证据来源与适用条件

- 证据来源唯一通道：Phase1 规则 source_refs → Canonical
  section 文本子串校验（§1.1）；规则不得引用登记册引文中
  不在 Canonical 的部分（r030 先例）。
- 适用条件：裁定步的条件集即其审定形态登记的条件全集，
  逐条以 fact_ref 绑定已执行事实步（§5.2 门禁）；事实步的
  适用范围即其审定切片的输入域（三刑：四柱支；越界输入
  ValueError）。

### 4.4 弃判与失败口径（与现有词汇对齐，不新造）

| 情形 | 在册形态 | 本契约沿用 |
|---|---|---|
| 裁定条件不全真 | classification='indeterminate'、decision_status='insufficient_reviewed_rules'、blockers[] 逐条带 reason 码（如 outside_reviewed_sufficient_conditions、root_type_source_conflict 等在册码）与 fact_ref/evidence_ids | 三谓词注册前后逐字沿用；注册不改变弃判面 |
| 事实步开启但盘上无在场事实 | 函数返回空列表字段（computed 而内容为空），names 恒 None | 不设单独弃判态；空事实是合法产出 |
| 事实步未开启 | 步与 result 键缺席（not_applicable 的缺席形态，照 include_relations 先例） | 同左 |
| 登记/证据完整性失败 | RuntimeError('registration_integrity_failure…')（事实层自备）/ resolver ValueError（证据解析） | 整次执行 fail-closed、无部分产出 |
| 研究门禁未授权 | engine.execute 在入口拒绝研究型输入 | 新门控参数同列 |

### 4.5 版本追溯

- 规则版本：以规则 ID + 所在快照 manifest 钉值联合定位
  （Phase1/Phase2 条目只存在于密封快照内，快照 SHA 即其版
  本坐标；治理登记册逐批记录 sealed_file_sha256_after 与
  manifest 前后值，S5/P1 两记录同形）。
- 证据版本：evidence ref 自带 source 的 commit 与 sha256、
  section locator，逐条可回溯到底本与节位。
- 契约版本：本设计稿为「执行绑定契约 v1（设计）」；实施批
  若调整契约条款，须在实施 PR 中以版本递增（v2）明示差异，
  不得静默改口径。chart 的 variant
  （ziping-structural-v1）与各研究 Variant ID
  （bazi-strength-adjudication-v1、sanxing-branch-fact-v1）
  保持不变——注册不构成 Variant 变更。

## 5 事实层与判定层分离设计

### 5.1 三刑：机制性保证（不靠自觉）

1. **字段隔离**：事实步 output 的键集由事实层既有白名单测试
   钉死（directed_pairs / group_configurations /
   self_punishments / names 四键，效价类键出现即失败）；接入
   后该白名单测试对象从函数输出扩展到 trace step output 与
   result 键，断言不变。
2. **命名隔离**：步 ID 与 result 键均为 `*_facts /
   branch_punishment_facts` 事实命名；禁止以 determination、
   verdict、pattern 等判定词命名（实施批测试以键名/步名断言
   钉住）。
3. **引用隔离**：契约 §4.1 钉死事实步不得成为任何
   RuleMatch（algorithm_selection）的对象、不得进入任何
   sufficient_rule；实施批以负例测试钉住（构造要求以事实步
   发 RuleMatch 的调用必须被 match_steps 拒绝或在组装层被
   断言拦截——match_steps 现有断言只校验「指向已执行步」，
   故实施批须在消费侧加 kind 断言：match 的 rule_id 不得为
   事实步 ID，列入 §9 测试清单）。
4. **投影隔离**：result 键继续被 public_projection 剥离
   （既有），且开启门控与研究门禁绑定，生产公开面永不携带。
5. **消费门禁**：教义层（正官破格 B4 等）对事实的消费不在
   本设计范围；未来消费必须另行审定并以 fact_ref 引用，不
   得在本步 output 上追加判定字段。

### 5.2 三谓词：适用条件不扩展的保证

1. 条件集冻结：三谓词的条件键全集以其审定形态登记
   （FORM_BING_SI / S1/S2 登记表）为准，注册步的 conditions
   与旧出口逐字相同（§7 等价表钉死）；实施批 diff 中
   conditions 生成逻辑的任何改动即越界。
2. anchor 分级随行：anchor_type / anchor_registration /
   month_root_grade / root_grades 等既有分级字段逐字保留，
   框架推步级（framework_derived）与治理约定条件
   （anchor_type 标记者）在注册后仍机器可辨（r030
   commanding 分支同形先例）。
3. 新增/变更条件须另行审定的门禁（写入实施批任务书与治理
   登记册行）：本设计授权的实施只做「同一条件集换出口」，
   任何条件增删、阈值或分级变化都使该谓词自动退出本批、
   回到 pending 并另行审定。

## 6 执行语义

- **执行顺序**：trace 步序由 chart 组装顺序唯一确定（追加
  序）；三刑步位于关系事实块之后、旺衰链之前（事实先于裁
  定）；三谓词步在 `_bounded_assessment` 内于 action_effects
  步之后、gate 步之前触发（与已注册两步现状同序）。步序变
  化会影响 fact_ref 的 `#/trace/<i>/output` 索引——批一开启
  路径新增一步会使其后步的索引位移一位；该位移只发生在开
  启路径（默认路径步序逐字不变），§7 已将其列入开启路径的
  允许变化并要求 fact_ref 指向的内容逐字一致（索引变、所指
  不变）。实施批须对开启路径的 strength_factor_graph /
  adjudication_fact_ref 索引做专项复核。
- **重复触发防护**：每条新规则步在单次执行内至多 add 一次
  （单一调用点结构保证 + 实施批测试断言
  `count(step.rule_id) == 1`）；harness 层另有 Golden case
  id 全局去重（`run_cases` seen 集）。
- **规则冲突**：事实层与既有事实并存不抵消（SLICE_SPEC
  boundary_rules：刑与冲/合/害同对并存为常态，kind 隔离）；
  裁定层冲突继续走既有 conflict_checks/blockers 通道，注册
  不改变任何冲突的 blocking 判定；两条裁定步同盘触发的既
  有优先级（分支 if/elif 顺序）逐字不变。
- **缺少证据时 fail-closed**：§4.4 表已钉：证据解析失败抛
  错整次执行终止；事实层登记漂移 RuntimeError；谓词条件
  证据缺失走 blockers 弃判而非猜测放行。
- **r026 旧出口兼容**：gate 步与 r026 不动；F4 changsheng
  谓词不在本设计范围，继续经 r026 出口并保留其 pending 披
  露（实施批 diff 不得触碰 changsheng 分支与 S2 分支以外的
  pending 分支）；弃判 else 分支（outside_reviewed_
  sufficient_conditions）不变。批二完成后 r026 出口的消费
  者只剩 changsheng 与弃判路径——此为预期收敛，不在本设计
  内退役 r026。
- **回滚策略**：逐批独立可回滚——代码侧 revert 实施 PR；
  密封侧恢复该批前快照目录 + cicd 钉值回退（P1 §4 在案路
  径）；治理登记册的 disposition 翻转以新事件回退登记
  （append-only，不删行）。回滚后状态：批一回滚 → 三刑回
  到「建节完成、evidence_binding pending」即 P1 终局状态；
  批二回滚 → 三谓词回到 r026 出口 + pending 披露即 P2 补审
  基线状态。两批回滚互不依赖（批二不依赖批一的注册实体，
  只共享本契约文本）。

## 7 逐盘等价测试设计

### 7.1 必须逐字一致的字段（新旧同盘对比）

批一（三刑接入），默认（门控关）路径：**整个执行封套逐字
一致**（result / trace / rule_matches / evidence /
interpretation_contract 全等）。开启路径：除 §7.2 列明的新
增外，既有 result 键、既有 trace 步（rule_id / inputs /
output / evidence_ids）、既有 evidence 条目、既有
rule_matches 条目逐字一致；新步所引用事实与函数直调输出逐
字一致（函数本体零改动，以 12⁴ 全组合穷举对比钉死）。

批二（三谓词注册），逐盘（ADJUDICATION_VARIANT 路径）：
classification、decision_status、conditions 全集（每条的
condition / met / fact_ref / rule_id / evidence_ids /
anchor_type / anchor_registration 及 metal/water 的
month_root_grade / root_grades）、blockers、conflict_checks、
conflict_ids、fact_refs 所指内容、evidence_ids、source_ids、
unresolved_evidence、variant_dependencies、supported_
classifications 逐字一致。

### 7.2 允许变化的新增/改写（封闭清单，清单外即失败）

批一：result 新增 `branch_punishment_facts` 键；trace 新
增该步一条；evidence 新增该步解析条目；rule_matches 新增
该步的 executed_calculation 条目；封套新增 research_only
标记（开启时）；开启路径上其后步的 fact_ref 索引位移
（§6，所指内容须逐字一致）。

批二（逐谓词，照 S5 verdict_surface_change 先例）：该谓词
why.sufficient_rule 由 None 改为其 Phase2 步 ID；
why.sufficient_predicate 与 why.predicate_rule_registration
两键移除；matched_rule_ids 新增其步 ID；trace 新增其裁定
步一条及其 evidence 条目；assessment 的 limitations 中该
谓词的注册状态句改写；治理登记册行 disposition 改
registered 并补 phase1/phase2 ID。**清单外任何字段变化
（含 production_scope 文本、其余谓词的任何字段、changsheng
分支产出）即等价失败。**

### 7.3 比对盘源与规模下限

- 批一：P1 同盘差异测试的 129 盘集（119 个密封 Phase2
  Golden 柱面输入 + 10 个三刑真实出生时刻盘）为下限，默
  认与开启两路径各跑一遍；另加事实函数 12⁴=20,736 全支组
  合的函数级直调对比（新旧代码同函数——本为零改动声明的
  穷举钉子）。
- 批二：S5 先例的 21 盘判定面比对为下限，另加逐谓词见证
  集：lu 的 F34 Golden 7 例（
...[truncated 20007 chars]

## 勘误与缺失说明（E0334 追加）

本节由 TJ-018.3 批一关账批 E0334 于 2026-10-30 追加，只陈述可验证事实，不补写、不改动上文任何一行：

- 本文件合并版本（随 PR #509 合并入 main，台账 E0332）共 569 行，止于 §7.3 中途，末行断于「lu 的 F34 Golden 7 例（」，§§8–11 不在合并文件中；设计批源文件同为截断状态，非合并过程丢失。
- 批一（三刑事实执行接入，PR #510）实施的规范依据为本文件 §§0–7 与用户 2026-10-30 14:29 授权文本，两者独立完整，批一实施未依赖 §§8–11。
- 原 §10.2 对 source_refs 子集的点名一项不在合并文件内（属缺失范围）；批一按可审计口径定稿：审定登记 GROUP_TABLE 三组与 self_punishment 行的 evidence_refs 并集恰为 6 条，即密封 Phase1 规则 bazi.rule.r031 的 source_refs，定稿记录见 docs/product/TJ0183_SANXING_EXECUTION_BINDING.md §0 与 §2。
- §§8–11 的内容（分批实施顺序、未决事项等）仅存于 E0332 完成报告的摘要转述，不作为仓库内规范文本引用；后续批次如需引用该部分，须以摘要转述为线索另行审定入册。
