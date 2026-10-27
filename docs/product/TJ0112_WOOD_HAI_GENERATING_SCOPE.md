# TJ-011.2 扩围：木日主 × 亥月「印比生扶」强分支（从旺口径）

本文件是 `bazi-strength-adjudication-v1` 新增第三个充分谓词分支的条件核定记录，与 TJ-011.1 的
[BAZI_STRENGTH_ADJUDICATION_AUDIT.md](BAZI_STRENGTH_ADJUDICATION_AUDIT.md) 同级引用、互不改写。
TJ-011.1 的两条既有谓词（木 × 卯 pure → strong、木 × 酉 isolated → weak）条件一字未动；
本批只新增一个平行合取分支，结论只有 strong / indeterminate，本分支不产出 weak。

## 1. 分支定义与依据差异（必须明示）

- 既有卯月分支：月本气乙与日主同类，属于「得令 + 纯印比」，从旺、从强两定义可同时援引。
- 新增亥月分支：月本气壬生木（印月），日主**不得令**。其依据只取任氏**从旺**定义
  （《滴天髓阐微》char 96521 / line 4905：「从旺者，四柱皆比劫，无官杀之制，有印绶之生，旺之极者」）——
  该定义要求四柱皆比劫、有印绶之生、无官杀之制，**不要求当令**；**从强**定义（char 96605 / line 4906）
  含「日主又当令」要件，本分支不援引、也不宣称得令。
- 证据 Source 不变：`bazi.source.ditiansui-spouse`（C 级，单一电子谱系 daizhigev20 固定快照，
  SHA256 `6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795`）。无新 Source、无密封政策改动：
  密封概念 `bazi.concept.action_effects_v1` 的 `pure_months=[卯]`、`isolated_months=[酉]` 保持原值；
  新分支的月份范围按本仓既有模式在公开代码侧声明（`PURE_GENERATING_MONTHS = ('亥',)`，
  与裁决层对卯/酉的硬编码、显示层 `AUDITED_MONTHS` 互证模式一致），并由专项测试钉死密封政策未漂移。

## 2. scope 条件表（逐条派生自既有 pure 谓词 + 证据锚点）

新条件集 `pure_generating_support_scope_conditions`，8 条，与 pure 集逐条对位；除月份条件外，
其余 7 条复用 pure 集的同一计算事实，两集不可能在共享条件上分叉。

| # | 条件键 | 亥月口径（与 pure 的差异） | 证据锚点 |
| --- | --- | --- | --- |
| 1 | `wood_day_master` | 日主甲/乙，同 pure | s052 春木甲乙语境；TJ-011.1 审计 §C |
| 2 | `reviewed_generating_month` | **唯一改动**：月支 ∈ {亥} ∧ 本气状态 reviewed ∧ relation = `generates_me`（亥本气壬生木）。pure 版为月支 ∈ 密封政策 `pure_months`（卯）∧ relation = `same_element` | 本气关系：亥本气壬 = section s034；Golden `bazi.principal-generate`；从旺定义 char 96521（印绶之生与印月吻合） |
| 3 | `all_positions_support_only` | 全部显/藏关系仅生扶类，同 pure。按亥藏干构成复核：亥藏壬（生我）、甲（同类），均为生扶，故本条件在亥月**可满足**（与午月对火的结构性不可满足相反，见证据侦察结论） | 从旺定义 char 96521「四柱皆比劫，无官杀之制」；藏干表 s004 |
| 4 | `visible印_present` | 显干须见印（壬/癸），同 pure | 从旺定义 char 96521「有印绶之生」 |
| 5 | `visible比_present` | 显干须见比劫（甲/乙），同 pure | 从旺定义 char 96521「四柱皆比劫」 |
| 6 | `effective_day_roots` | 有根且全部根 availability = effective，同 pure。根位按已审根表：木根 {亥， 寅， 卯}（亥为表中首列） | 根列举段 char 39967–40222 / line 1613「如甲乙逢亥寅卯之类是也」；密封政策 `reviewed_root_branches.木 = [亥，寅，卯]` |
| 7 | `all_visible_have_reviewed_roots` | 每个显干均有已审根位，同 pure（木干根位 {亥，寅，卯}、水干根位 {亥，子} 均在已审表内） | 同上根列举段与密封政策根表 |
| 8 | `no_unresolved_interactions` | 无未解干支作用类型，同 pure | TJ-011.1 既有口径（合冲害三合未解即弃判） |

裁决层合取（`bazi_adjudication._bounded_assessment` 新增析取支）：
`pure_generating_support_scope_met ∧ 8 条件全真 ∧ 月支 ∈ PURE_GENERATING_MONTHS ∧ relation = generates_me ∧ 有根 ∧ 全部根 effective ∧ 全部显干 effect_status = effective_in_reviewed_context ∧ 无 blockers`
→ classification = `strong`，谓词名 `pure_generating_support`。
既有 blockers 体系（根异文冲突、根可用性未达 effective、本气未审、作用未解、因子链不一致/重放不符）对本分支一体适用。

**规则注册状态（如实）**：本谓词尚无密封 Phase1/Phase2 规则注册。密封快照由可信 manifest 钉死，
且已注册的 r024 条件明文限于「木日主、月卯本气同类」，借用其规则 ID 会构成证据冒充；
`ExecutionTrace.add` 对未注册 ID 直接拒绝，亦无公开侧注册通道。因此本分支不新增 trace 规则步、
不借用 r024/r025 的 ID：裁决经已注册的有限裁决出口（`bazi.rule.r026` /
`bazi.phase2.strength_bounded_adjudication`）发出，`why_not_indeterminate` 以
`sufficient_rule = None`、`sufficient_predicate = 'pure_generating_support'`、
`predicate_rule_registration = 'pending_phase1_rule_registration'` 明示待注册状态
（同 TJ-013.1 调候 Variant 的披露先例）；8 条条件的证据仍逐条绑定已执行的因子步证据。
密封侧规则注册须另走知识治理批次在可信环境完成，不在本 PR 范围。

## 3. 结构性事实（实现与用例设计依据）

- 亥月木日主**恒有结构根**：月支亥藏甲，木日主在亥月必然以月支中气甲为根之一。
  因此本分支不存在「根位全无」的反例形态；根条件的实际约束点在**可用性**层
  （根被冲/合/害牵连时 availability 非 effective），反例以巳冲亥实现（全部木根失效）。
- 同理，「仅本气根」的日主根构成在亥月不可实现（中气甲根恒存在）；边界例取可实现的
  最接近构成：卯本气乙根与亥中气甲根并存（本气根参与），与「仅中气甲根」构成对照两例。
- 亥月月干永不为壬（五虎遁下亥月干 ∈ {乙，丁，己，辛，癸}），故显干印只能由年/时干
  或月干癸（戊癸年组）提供；用例据此构造。

## 4. 用例（全部真实出生时刻，Asia/Shanghai；预期由条件手工推导）

用例定义与逐例推导链：`tests/golden_tj0112_wood_hai.json`；执行测试：
`tests/test_tj0112_wood_hai_generating.py`（密封组装环境运行，同 Phase2 八字套件口径）。

| 用例 | 出生时刻 | 四柱（历法路径实算） | 预期 |
| --- | --- | --- | --- |
| 正例·仅中气甲根 | 1983-12-02 00:30 | 癸亥 / 癸亥 / 甲子 / 甲子 | strong（新谓词） |
| 正例·本气根参与 | 1963-11-17 00:30 | 癸卯 / 癸亥 / 甲子 / 甲子 | strong（新谓词） |
| 反例·月支非亥 | 1983-12-13 00:30 | 癸亥 / 甲子 / 乙亥 / 丙子 | `reviewed_generating_month` = False → indeterminate |
| 反例·日主非木 | 1983-11-14 10:00 | 癸亥 / 癸亥 / 丙午 / 癸巳 | `wood_day_master` = False → indeterminate |
| 反例·泄气透干 | 1983-12-02 03:30 | 癸亥 / 癸亥 / 甲子 / 丙寅 | `all_positions_support_only` = False → indeterminate |
| 反例·根被冲失效 | 1983-11-13 10:00 | 癸亥 / 癸亥 / 乙巳 / 辛巳 | `effective_day_roots` = False + blocker → indeterminate |
| 冲突例·余气根异文 | 2024-12-06 00:30 | 甲辰 / 乙亥 / 甲辰 / 甲子 | blocker `root_type_source_conflict` → indeterminate |
| 弃判例·无显印 | 1984-11-26 00:30 | 甲子 / 乙亥 / 甲子 / 甲子 | `visible印_present` = False（余皆真）→ indeterminate |
| 回归·卯 pure | 1963-03-22 22:00 | 癸卯 / 乙卯 / 甲子 / 乙亥 | strong（原 `strength_pure_support`） |
| 回归·酉 isolated | 1978-09-20 10:00 | 戊午 / 辛酉 / 乙酉 / 辛巳 | weak（原 `strength_isolated_control`） |

## 5. 门控与未扩范围

- 显示门控不变：服务端公开白名单 `PUBLIC_STRENGTH_VARIANTS` 仍为空集；`AUDITED_MONTHS`
  本批不扩（显示范围的扩展须另走 TJ-011.3 型显示审核），新谓词的 classification 在公开投影中
  被剥离，专项测试以真实裁定结果断言之。
- 结果对象不变：research_only = true、public_enabled = false、ai_enabled = false；不接公开场景。
- 未扩：其他日主、其他月份（含木 × 寅/子等）、weak 方向、balanced/从格；分日司令等既有
  blocker 与冲突口径原样保留（亥月分支不旁路任何 blocker）。
- 计数影响：无新 Source、无新 Phase2 合同规则（新谓词待密封注册，见 §2 注册状态说明）、
  无新密封 Golden（用例在公开仓 tests 内，同 TJ-013.1 golden 先例）；
  覆盖工件因能力口径文本更新而再生成，计数钉值不变。

## 6. S5 注册完成注记（2026-10-28，E0254）

§2「规则注册状态」所述 pending 状态已由 S5 密封注册治理批解除：本谓词已在
密封 Canonical 登记为 Phase1 规则 `bazi.rule.r029`、Phase2 执行规则
`bazi.phase2.strength_pure_generating_support`（快照 manifest
`b9f9b8fd…`），裁决改经该注册 trace 步发出，`why.sufficient_rule` 为该 ID、
不再带 pending 披露。条件集、分类与 blockers 逐字不变。治理全记录见
`docs/product/TJ0112_S5_REGISTRATION_GOVERNANCE.md`。
