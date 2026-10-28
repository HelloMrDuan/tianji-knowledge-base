# TJ-012.3 三刑组表事实层设计审定

状态：设计审定文档（Design Adjudication）。与数据登记模块
`src/tianji_kb/bazi_sanxing_fact_adjudication.py`（register id
`bazi-sanxing-fact-adjudication-v1`）成对交付；Golden 镜像见
`tests/golden_tj0123_sanxing_fact.json`。本批为纯审定＋登记，
**零实现代码、零运行时接线**：合并后任何命盘的现行事实输出逐字
不变（三刑事实在现行代码中不存在，见 §1 盘点 inv-12）。TJ-012.3
保持阻塞。

审定缘起：Slice D 就绪度复审（`~/workspace/capability-audit/
tj012-slice-d-readiness.md` §3.1）判定三刑「文本层已就位（018-B），
规则层未动」，并把「事实规则若只输出刑组成员关系而不输出刑名，
可绕开命名冲突」列为需要审定的设计决定。本批即该审定。

## 1. 盘点结论：组表只有一个原典出处

全树已登记来源逐项盘点（登记 §SOURCE_INVENTORY，14 项）：

| 类别 | 内容 |
|---|---|
| 组表原典 | 三命卷二《论三刑》整节（018-B 登记：[71874, 74856)、校勘记 35 条、引文 11 条）——**唯一**组表出处 |
| 跨书见证 | 滴天髓阐微 Canonical s021：枚举文字与三命总结句逐字同文，但立场是斥机械套刑为俗谬（见证与立场分开登记） |
| 消费侧登记 | 渊海 s020 歌诀（断语）；渊海正官组忌句 2 条（经事实层转手）；三命卷五杂气/阳刃刑冲效价句 4 条（效价随语境反转） |
| 概念现状 | `bazi.concept.conflict_three_punishments`：unresolved、executable_policy=blocked_pending_school_resolution、production_policy 禁统一 executable 与前台吉凶输出；任氏分支不应用（公开镜像三处，本批逐字不变） |
| 登记性缺位 | 协纪辨方书结构短引无刑表；神峰/穷通/滴天髓原注已登记材料无组表（phase1 全量扫描：含「刑」的 bazi Section 恰 s020/s021） |
| 执行面缺位 | foundations 支关系表恰五族（冲/三合/方局/六合/六害）、无刑；Phase2 规则 punish 命中 0（两处 limitations 明文排除）；bazi_core 关系函数只产合/害/冲 |

未登记者只记缺口（如三命他节、神峰他节可能存在的刑表述），本批
不新登记大段原文。

## 2. 事实模式设计：无名组＋单向环＋自刑集

- **组**：按三命总结句序数立号——`sanxing-group-1` 子卯（一刑）、
  `sanxing-group-2` 寅巳申（二刑）、`sanxing-group-3` 丑戌未
  （三刑）。组名（无恩/恃势/无礼）在节内即有正文与《三车一览》
  互换两说（018-B 已登记 conflict 不裁定），**事实层永不输出
  组名**，名目只在登记中以并列状态著录。
- **有向对**：按「组内单向环」建模（数起句计数链只给环向一途）。
  8 条环边见证分级：等级 A 6 条（三命枚举引文逐字：子→卯、寅→巳、
  巳→申、申→寅、丑→戌、戌→未）；等级 B 1 条（卯→子：数起句计数
  链＋s021 逐字枚举＋无礼段正文三重支持，入切片但等级必须随事实
  输出）；等级 C 1 条（未→丑：三命侧只在含未决字的残句中，
  **不入切片**，见 §4 B1）。组内其余 6 条有序对是**非边**
  （方案本身不含，与「缺见证」严格区分，永不输出、永不记缺口）。
- **自刑**：辰午酉亥，按自刑定义的结构理由著录（四支是三类四位
  组中「无刑者」，不是第四组名目）；组态为同支见于 ≥2 柱位。
- **组态**：三支全/缺一只报在场档（full/partial/single），语义钉死
  为集合在场——partial 不是「刑不全」的裁定、full 不是「刑成立」
  的裁定。判别性组态：丑、未两员在场时组为 partial 而有向对为
  **零条**（组在场 ≠ 对事实）。
- **边界**：与冲/合/害/三合/方局 kind 隔离、并存、互不抵消。
  实测重叠：寅巳=害、巳申=六合、申寅=冲，三条等级 A 边各与一种
  既有对关系同对并存（group-2 内部同时含冲/害/合对各一）；
  刑组与三合局、方局集合 pairwise 皆不相等，刑组不是合局。

## 3. 可执行性逐项判定（登记 §PROPOSITION_AUDIT，14 项）

| 项 | 命题 | 判定 |
|---|---|---|
| P1 | 三组组员关系 | fact_ready |
| P2 | 等级 A 有向对 6 条 | fact_ready |
| P3 | 卯→子 | fact_ready_with_grade（等级 B 随事实输出） |
| P4 | 未→丑 | **blocked_by_evidence_gap**（三命可引明文缺位） |
| P5 | 自刑集与重见组态 | fact_ready |
| P6 | 全/缺一组态 | fact_ready_as_presence_only（只报在场） |
| P7 | 组名分配 | blocked_by_naming_conflict（事实层无名绕开；用名须用户裁定 P-D1） |
| P8 | 刑上/刑下框架 | registered_variant_not_consumed |
| P9 | 程度命题（要相等/太过不及/有制） | blocked_by_missing_layers（一般旺衰＋制伏效力） |
| P10 | 机制/方位/数起教义 | registered_doctrine_not_fact |
| P11 | 正官破格侧消费 | consumer_not_unlocked（另经贵命整体判断转手） |
| P12 | 任氏分支消费 | not_applied_by_registered_concept（口径不变） |
| P13 | 杂气效价教义 | doctrine_not_fact（效价非事实属性） |
| P14 | 由刑推吉凶/灾祸 | prohibited（概念 policy＋内容诚实红线） |

## 4. 切片规格（SLICE_SPEC，非 None）

`sanxing-branch-fact-v1`（设计裁定、未实现）：结构事实层独立函数
（与 `reviewed_branch_pair_relations` 并列，一期不改写既有关系
输出键）；输入四支、非法 ValueError；输出三类事实
（directed_pairs 带等级与证据引用、group_configurations 在场组态、
self_punishments 重见），names=None、无任何裁决字段；fail-closed
含登记完整性核验与判别例钉死（未丑不补边、寅申只报申→寅）；
Golden 要求全真实盘＋三判别例（见登记）。注册口径：
evidence_binding pending Phase1 注册、sufficient_rule=None、
research_only、public/ai 关闭、不接场景、不建 Phase2 规则、
不动概念任何字段。

**审定点 AP1（随登记披露）**：概念 production_policy「不建立统一
三刑 executable」的对象是统一教义 executable 与前台吉凶输出；
本切片是裁决前结构事实（与六害/六冲事实同层同地位），故相容。
若评审作严格解读，SLICE_SPEC 降为 None，盘点与逐项判定全部
保留——降级条件明示在案。审定点 AP2：卯刑子（等级 B）与未刑丑
（等级 C）的分界取三命侧文字状态（干净正文三重支持 vs 含未决字
残句），见登记。

## 5. 阻塞与待裁定（登记 §PENDING_ITEMS）

- B1 未刑丑可引明文：证据缺口（校勘未决 smxing-anomaly-71984），
  018 线后续批解锁，**不需要用户裁定**。
- B2 组名采用：用户级待裁定 P-D1——当前无消费方需要名目，不阻断
  无名切片。
- B3 程度命题：被一般旺衰/制伏效力层阻断（TJ-011.2 线）。
- B4 教义性消费：被各自的整体判断/效力前置阻断；事实层建成不
  自动解锁任何 determination。
- B5 统一三刑教义 executable：用户级待裁定 P-D2
  （blocked_pending_school_resolution），与 B2 分开登记。

## 6. 限制（登记 §ADJUDICATION_LIMITATIONS 摘要）

本批零实现、零接线；未入引文的节内文字不支撑入切片命题；他节
刑表述若后续登记出现异表，按流派分歧并列、不得强行统一；
未刑丑不入切片是证据裁定而非方案裁定（三命方案环结构本身含
此边）；事实层只是 Slice D 前置之一，正官格等 determination
仍被独立前置阻断；TJ-012.3 保持阻塞。
