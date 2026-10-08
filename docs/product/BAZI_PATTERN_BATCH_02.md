# Bazi Pattern Batch 02：司令冲突与取格资格门控

基线：`fd5a4549f75fc7411541e73a939f26cfab755d96`，继承 PR #141。

## 本批真实完成

1. 修正寅月分日 Concept **摘要**“八日后”误写；原文短引、来源快照、RAW、PUA/OCR 不改。
2. 对现有已审 Concept 提供十二月月令审核状态，专门区分 **未审核 / 候选 / 来源冲突 / 日界未决**。其他十一月没有来源冲突记录，仍不能解析为司令。
3. 在现有 `bazi_pattern.candidates()` 中返回 `qualification` 子对象（没有新建第二套算法）：逐项记录月藏候选、逐字透干、具体司令、禄刃与杂气、官杀去留/财旺破印、一般旺衰与实际作用、原典选格分支。
4. `qualification_status=disqualified_for_this_branch` **只适用于“月藏候选观察路线”完全无命中**；不能排除《渊海》地支官局、不透取官或其他法。其余候选状态仍 `indeterminate`；当前没有任何 `qualified_for_determination` 的实例。
5. `determination.pattern/true_false/success_failure/useful_god` 均保持 null，研究模式、公开与 AI 封闭状态不变。

## 仍然阻塞真正取格/定格

- 司令分日：现有寅月两种电子文本尚未统一，其他十一月未有经过审核的可执行分日表。
- 正官：月藏、正官透干只作结构事实；官杀去留、财印关系、未透时地支官局等需要独立规则。
- 印绶：正/偏印、财星、官鬼位置不自动转化为财旺破印、别格或官鬼多的裁定。
- 禄刃/杂气：辰戌丑未显式标记必须进一步审核；禄刃依日主和月令组合，不能只凭地支作粗暴判定。
- 限定强弱分类：`bazi-strength-adjudication-v1` 的木日主研究规则不能当作普适格局资格。
- 目前没有最终取格规则，因此不创造新的 Phase2 executable Rule 或伪造额外 Golden 数。当前只有已有两条格局候选 Rule 的证据链和新增资格拒判回归。

## 验收原则

必须跑全量 Python、Phase1/Phase2/Golden、Source/Quarantine/RAG、前端与 API 研究边界回归。
以 PR 的 Actions 真实执行状态为准；未完成 CI 不宣称通过。

下一小批应从一个证据充分的 **明确 Variant 单一路线** 审核真正资格充分条件；证据缺失则 indeterminate，不因本批资格清单存在而宣布格局可以定格。
