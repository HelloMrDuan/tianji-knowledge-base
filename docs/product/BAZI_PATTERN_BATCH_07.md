# Bazi Pattern Batch 07：财克印/官生印方向与实际效力门控

## 来源与原则

沿用 Canonical 已审《渊海子平》`bazi.section.s057` / `s058` 和本仓库 `foundations.CONTROLS/GENERATES` 五行结构表。s057 含“喜官星生印，忌财旺破印”，但没有可执行的财旺界限、根力以及实际生克效力门槛。**可证明五行方向，不等于已发生有效作用。**

## 本批落实

在原研究入口 `bazi-pattern-structure-candidates-v1`、已有 `bazi.phase2.resource_pattern_candidates` 下，复用 Batch 06 的原始 `#/trace` 位置：

- 对每一个已执行的显财/藏财与月藏印建立 `wealth_controls_resource_element` 的**五行克关系候选**。
- 对每一个正官显藏干与月藏印建立 `official_generates_resource_element` 的**五行生关系候选**。
- 七杀只记 `killing_generates_resource_element_only`：五行方向成立，不等于原典“官星”适用范围已经审核。
- 每一条携带两端干、五行、显藏类别、各自 Trace 指针、方向成立情况，`effective_interaction=null`。
- 显式效力门控拒判：有效根力、被作用印星状态、显藏参与方式、实际干支互动、流派范围、竞争格局仍未形成可复算的**成效充分条件**。不复用仅判日主受生克的有限 `bazi-action-effects-v1` 去声称“财克印已发生”。
- 有月藏印但无对手返回 `no_relevant_elemental_pair`；无月藏印返回 `outside_month_resource_branch`，不编造效应。
- 新增 7 组 Golden 和多组 Trace、原典、拒判回归，保留全部旧案例。

## 未达能力

本轮不能确定“财旺”“破印”“官印相生”“官鬼多”，没有数值权重、相邻加分、隐干当显干；更没有正官格/印绶格定格及喜用神。所有新的结论研究模式可查，public_enabled=false，ai_enabled=false。

下一批应审核财、印双方根与有效作用的**成对条件**，而不是用现有日主单点作用结果替代；在没有充分原典前不得做因果裁决。
