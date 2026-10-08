# 格局研究 Batch 06：印绶之官财共现与拒判

## 已审来源

沿用已审核的《渊海子平》s057（“喜官星生印，忌财旺破印”）及 s058（“若官鬼多，或入别格，又不可专以印绶论”），均为已登记 C 级固定电子文本。**文本未给出“财旺”“官鬼多”可直接量化的阈值，也未完成作用效力或其他格局竞争规则。**

## 本批真正实现

在显式研究 `bazi-pattern-structure-candidates-v1` 下，复用已执行 `ten_gods` 与 `hidden_stems` 的 Fact/Evidence，记录：
- 月支所藏正印、偏印；
- 其他柱显干与各支藏干中的正财/偏财；
- 同样区分正官、七杀的显干与藏干；
- 无月令印候选时为 `outside_month_resource_branch`，只有月印无其他事实为 `no_related_facts_observed`，共现为 `related_facts_observed`；
- `wealth_strong_enough_to_damage_resource`、`official_actually_generates_resource`、`many_officials_or_competing_pattern` 始终 `indeterminate`。

新增 8 个 Golden，覆盖无共现、显财、藏财、显官、藏官、显杀、藏杀及月令不具印的拒判边界。新增事实指针、真实原典 Evidence、AI/public gate 回归。

**不采用数量比较判财旺；藏干不当作透干；出现正财不等于破印；出现正官不等于官印相生；出现七杀不等于官鬼多；没有形成真正的印格定格规则。**

下一阶段才逐条核实际作用、印星旺衰/根气、财克印能否成立与冲突流派。RAW、原典快照、PUA/OCR、《三命通会》隔离状态、前台均不改。
