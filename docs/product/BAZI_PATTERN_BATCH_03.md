# Bazi Pattern Batch 03：渊海甲辛地支官局研究分支

前置：PR #142 的十二月司令矩阵及取格资格。**这批不是定格，也没有提升人工证据等级。**

## 来源与范围

沿用已批准的 `bazi.section.s056`（《渊海子平·正官论》、C级固定电子文本）和现有 `bazi.phase2.branch_triple_harmonies` 已执行结构事实。该原文在甲日以辛为官的上下文提到辛未透而地支见巳酉丑，随后又要求身旺与时辰相关条件。我们只在 **甲日 / 酉月 / 四柱显干无辛 / 四柱巳酉丑俱全** 的狭窄范围记录 `reviewed_structural_candidate`。这四项中任一不满足返回 `not_observed`。不外推非甲日、其他月令，也不把全三合成员等同于合化成功。

## 技术实现

- 复用 `pattern_variant=bazi-pattern-structure-candidates-v1` 与已审 `bazi.rule.r027`，而非新增未经审核的独立取格引擎。
- 研究入口自动执行已有五合、六合、六冲、三合等结构轨迹；新增候选只读取既有 `pillars`、`ten_gods`、`branch_triple_harmonies` 的 Trace/Evidence。普通生产不增加这些可选输出。
- `pattern_candidates.official.yuanhai_unexposed_official_branch` 记录四项逐条事实、`#/trace/` 引用、来源段 `s056`、未解决的身旺/时辰/分日/官杀/成化等条件。
- `qualification_status` 仍 `indeterminate` 或当前月藏支路的 `disqualified_for_this_branch`；`determination.pattern` / 真伪 / 成败 / 喜用不变，`ai_may_explain=false`。
- 五个独立 Golden：完整成立条件的研究候选、缺一支、辛已透、非酉月、非甲日。另有真实 Trace/Evidence/研究门禁回归。

## 未解决

原典“八月中气之后”的日期归属与其他底本尚待核；即使四项结构全部匹配，也**不能**据此推出正官格成立、现实职业预测、旺衰、婚姻、吉凶或喜用。财印、官杀、禄刃/杂气、司令冲突依旧研究中。

RAW、Source 快照、《三命通会》隔离状态、PUA/OCR不改变。不触碰前端或背景音乐。
