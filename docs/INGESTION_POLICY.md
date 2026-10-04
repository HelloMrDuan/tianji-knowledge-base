# Ingestion Policy

## 三个状态

- **RAW**：原始抓取缓存，不供平台直接查询，默认不提交 Git。
- **QUARANTINE**：许可证、出处、冲突或准确性尚未确认的候选资料。
- **CANONICAL**：通过来源、许可、结构与冲突审计后，可供生产检索。

## 自动发现

GitHub 每日按八字、紫微、奇门、六爻、周易、八卦、风水、梅花、大六壬、太乙、择日、姻缘、塔罗等关键词检索新仓库。

新仓库只进入候选池，默认 `QUARANTINE`，不会自动写进正式知识。

## 已登记源同步

每 6 小时检查默认分支最新 commit SHA 与许可证元数据。SHA 有变化只标记变更，不自动覆盖 Canonical。

## Canonical 晋级流程

1. 确认领域与主题。
2. 保存 repo/path/commit/license。
3. 删除导航、广告、Prompt 包装和重复文本。
4. 区分客观计算规则与解释文字。
5. 标注流派/ruleset。
6. 与现有知识做去重和冲突检测。
7. 关键规则加黄金案例。
8. 通过校验后才晋级。

## 公版古籍

无许可证仓库中即便包含古籍，也只抽取明确属于公共领域的原典内容；现代作者白话解释、注释、评分、改写不直接复制。

## 产品知识边界（最高优先级）

所有公开测算的解释性结论必须来自现有知识库：输入 → 确定性计算 → RuleMatch → 已审核检索 → Evidence → Variant/Conflict 检查 → 有界解释 → 用户结果。

缺知识就按上述既有入库流程补知识；不得创建另一套知识模型、凭语义猜规则、跳过 Quarantine/Review，或用模型先验填空。Prompt 必须明确：**Absence of knowledge is not permission to use model prior knowledge.**

沿用现有 Classic/Chapter/Section/Term/Rule/Concept、来源登记与等级、补充 Evidence、执行契约、晋级记录、Golden 与校验器。新领域必须审核扩展同一模型，不能把旧说明表或全文关键词命中当成生产规则。GitHub 实现资料按工程参考处理，不因旧 registry 的 trust_level 自动成为 A/B 级原典证据。

Rule 上线前必须回答来源、适用条件/Variant、限制/冲突；用户 claim 必须回溯 fact_ref → rule_id → evidence_id → source → classic/chapter/locator。计算结构不得自行升级成运势、婚恋、财富、健康或概率预测。人工语义复核及真实模型质量校准仍不可省略。

产品覆盖报告见 [KNOWLEDGE_GAPS.md](product/KNOWLEDGE_GAPS.md)，机器数据为 `data/product/knowledge_coverage.json`。它们是既有知识的自动派生报告，不是知识库或发布授权。知识开发顺序 P0（八字基础/旺衰/格局/喜用/大运/流年/婚恋/事业财富/合盘/梦境）→ P1（六爻深化/流月/流日/人生聚合）→ P2（专业工具扩展）。

《三命通会》保持 `quarantine_only` 与 `canonical_ready=false`；不得改原始 snapshot 或因 PUA 完成直接晋级。AI 未完成真实质量校准，不因产品或知识报告重构开放。
