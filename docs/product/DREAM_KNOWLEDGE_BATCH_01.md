# Dream Knowledge 首批：五个具体场景的文化解释与检索

本批沿用现有 Source → Quarantine/Review → Classic/Chapter/Section/Term/Rule/Concept → Evidence → RAG 流程，在同一 Phase1 schema 中受控接纳 `dream` 域，保留全部七个既有核心域。没有建立另一个知识格式，没有添加梦排盘引擎。

## 真实审核内容

| Term | 具体场景 | 固定原句 | 解释范围 |
|---|---|---|---|
| 蛇 | 蛇咬人 | 蛇咬人主得大财 | 传统得财象征；不泛化到所有蛇梦 |
| 水 | 自在身处水中 | 自在水中大吉利 | 传统吉象；不等同落水、饮水或洪水 |
| 火 | 身在火中 | 身在火中贵人扶 | 传统扶助象征；不保证现实安全或帮助 |
| 飞翔 | 人飞上天 | 飞上天富贵大吉 | 传统上升意象；不包括鸟飞、龙飞或飞机 |
| 坠落 | 人坠井中 | 身坠井中疾病凶 | 古代负面象征；不包括一般坠落，不作疾病诊断 |

每个 Term 保存 aliases、symbol/entity、source、locator、原句、interpretation、interpretation_type、limitations、confidence、cultural_context。Rule 同时引用具体条目和开篇梦语境，证明这是梦象与传统解释的关系，而非只在古籍中找到一个词。

## 来源与证据等级

使用 #127 已固定的殆知阁 UTF-8 RAW：commit `4a6d6f2088825f132521d848c2ea86cf9c9a7620`，blob `0c7b0823265c4ff00465f833e0be28f1bf0f2175`，23527 bytes，SHA256 `d80c42b0b8f44f5b8cf2c4e1c286b200388b65dcd321347eb7ac1011d0be5e97`。原始字节不修改，五句均逐字唯一匹配。仅保存短原句、题名/梦语境及必要章节头作为审核摘录；审核 Source 的 SHA256 是此摘录文件的校验值，不能混同整本 RAW 校验值。

新 Source 为 **C 级可追溯的单一电子版本**。作者为空，不确证周公旦署名；刊本、年代与独立性仍未核。沿用现有 PUBLIC_DOMAIN_EXTRACT_ONLY 范围审核简短前现代条目，不复制现代注解，也不据此宣称整书整理版权已获许可。整本 acquisition 元数据仍为 D/pending/promotion_allowed=false，书体继续 quarantine_only、canonical_ready=false，完整书体 Canonical 不存在。

[维基文库](https://zh.wikisource.org/zh-hans/周公解夢)中水、火、飞上天、坠井条目可以对照，但不是已证明独立的刊本。蛇条目显示“蛇蛟人”，本固定版为“蛇咬人”；异字记录为未决，不能凭网址多数票纠 RAW。这里只解释本固定电子版本的“蛇咬人”读法，保留局限。P.Ch.3908 是另一个梦书见证，不能混同本 27 节电子文本。

## 可运行链路

`用户梦境 → 字面实体/场景识别 → 已审 Dream Term → 现有 Canonical RAG → EvidenceResolver → 文化 interpretation candidates`

研究入口：`PYTHONPATH=src python scripts/retrieve_dream.py "我梦见被蛇咬了"`，须先执行现有 `build_production_runtime.py`。检索只使用 release 审核过的 Canonical 索引，核对其 SHA256、Term 内容、Rule、Variant 与 SourceRefs；运行时不读取 RAW 或 Quarantine 正文，也没有网络或模型调用。

字面场景 aliases 是保守输入匹配方式，不宣称完整自然语言理解。实体出现、其他动作/主体、否定、假设、间接叙述及不明语境不能直接形成解释。无审核命中返回 `no_reviewed_interpretation`；证据索引损坏则报未可用，不能调用 LLM 补写。

## 成熟度与测试真值

Dream 知识阶段为 PARTIAL，五个场景有文化解释关系；完整解梦 Scenario/产品仍未建立，公开与 AI 均关闭。Phase1 的 phase1_complete 仅表示同一模型中的最小审核骨架，不表示全梦象覆盖或产品可上线。

这五条 Rule 为 partially_structured 文化关系，未冒充 Phase2 排盘执行规则。固定正反例测试文化场景与引文是否正确、无证据时是否弃答；不将现实发财、疾病或未来当作 Golden 真值。传统 `traditional_chinese_dream` 与现代 `modern_dream_psychology` 分离，后者仍仅来源审计。

《三命通会》原始快照、86/86 PUA、524/524 occurrences、603 条 OCR overlay 及 quarantine_only/canonical_ready=false 均保持不变。旺衰仍 PARTIAL，不开启格局、喜用、行运。
