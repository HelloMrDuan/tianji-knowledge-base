# Bazi Pattern Batch 08：印绶五行方向 Golden 与逐对效力拒判补充

## 基线与补充
在已合并的 #147 基础上仅补充审计边界，不新增第二套引擎：
- 为每条财星／官星／七杀指向月藏印的方向候选添加独立 `effect_blockers`、Fact 指针、已执行 Trace Evidence IDs 和来源短引 s057/s058。
- 阻塞项包含财官行为干有效根力、月印有效根力、具体司令、成对生克效力 Rule、流派适用范围；仅藏干时单列「藏干实际参与未证明」。
- 若已执行干合、六合、六冲或三合结构事实，链接相应 `#/trace` 与 Evidence，**但不将结构关系解释为作用已经发生**。
- 添加 3 个手写预期 Golden：财官同现、子午冲条件、财七杀共现；方向 Golden 由 7 增至 10，仓库 Golden 总数由 129 增至 132。
- 所有候选依然 `effect_status=indeterminate`，`effective_interaction=null`；财旺破印／官印相生／官鬼多均拒判。
- 仍为 C 级固定电子文本、研究专用，`research_only=true`、`public_enabled=false`、`ai_enabled=false`。

## 未解决
缺少经不同流派分别审核的通用财／印根力与旺衰条件、日司令确定规则、合冲生克相互作用实效 Rule、财旺与官鬼多的可编程且有文献支持的边界。不可通过数量、权重或 LLM 代替这些证据。

本批不触及 RAW、三命通会隔离、原有 OCR 校勘成果或公开网站。
