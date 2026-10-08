# Bazi Pattern Batch 09：财印五行通根候选与具体冲合关系

## 实现范围

沿用 Phase2 `bazi.phase2.resource_pattern_candidates` 和经审来源《渊海子平》`bazi.section.s057` / `s058`；本批**不晋级新古籍**，也不创建平行命理引擎。

在 `yuanhai_resource_competing_context` 的已执行 `ten_gods`、`hidden_stems` 和审定干支关系 Trace 中，对每条财克印、正官生印、七杀生印结构方向候选，额外给出：

- `actor_element_root_candidates`：财或官杀元素在四柱地支内的同五行藏干位置；区分同字与同五行异字。
- `resource_element_root_candidates`：月藏印元素对应的同五行藏干位置。
- 每个候选保留柱位、支、具体藏干、`fact_ref` 和结构候选状态；可从完整执行返回值 `#/trace/…` 解引用。
- 根位涉及的实际六冲、六合、三合，仅列为 `branch_interactions`，每条保存 Rule ID、Evidence ID 和匹配的关系行 Fact 指针。
- `root_candidate_comparison` / `element_root_candidate_summary` 分开记录同字、同五行异字、冲合事实与**仍未裁定**的根力或实际生克。

## 严格边界

此处“通根候选”专指同五行藏干事实，不等同于日主通根算法、根有效参与、旺衰、根被冲去、财旺破印、官印相生、格局真假或喜用。藏干不能自动视为天干透出；具体日司令与流派冲突未解决。没有评分、权重或臆造原典阈值。

固定 Golden：`bazi.resource-element-roots-no-actor`、`same-and-other`、`clashed`、`no-month`，预期按人工预先确认的四柱藏干/冲合事实和拒判边界编写。回归测试检查指针指向藏干、互动行及 Rule/Evidence 可解引用。

保留 `research_only=true`、`public_enabled=false`、`ai_enabled=false`。本批只推进“确定性结构 Fact → 已执行 Rule → Evidence → 审核来源”；下一批仍需审核根气有效性、司令和成对作用的充分条件。
