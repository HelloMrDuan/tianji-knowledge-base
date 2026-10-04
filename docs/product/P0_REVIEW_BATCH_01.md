# P0 来源复核第 1 批

本批沿用现有 `acquisition.stage_candidate`，重新取得已登记来源的固定 commit，校验上游 Git blob，保存 RAW 缓存与 Quarantine 元数据。知命前段单独审核后补入既有八字 Phase1 模型；没有新增书目、领域 schema 或可执行推断。

| 来源 | 固定版本/采纳方式 | 隔离候选 |
|---|---|---|
| [滴天髓阐微](https://github.com/garychowcmu/daizhigev20/blob/4a6d6f2088825f132521d848c2ea86cf9c9a7620/易藏/术数/滴天髓阐微.txt) | daizhigev20；PUBLIC_DOMAIN_EXTRACT_ONLY；电子底本/作者归属待核 | `data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/e269843d0544fd18ac7d7c97d4e0bd268a5240ef.json` |
| [渊海子平](https://github.com/garychowcmu/daizhigev20/blob/4a6d6f2088825f132521d848c2ea86cf9c9a7620/易藏/术数/渊海子平.txt) | 同一已登记仓库及固定 commit；不视为两部独立校勘版本 | `data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/c7de6ab493e19460f5efba49085d20437c17e1d4.json` |

RAW 不提交 Git；整本候选维持 `stage=quarantine`、`review_status=pending`、`evidence_level=D`、`promotion_allowed=false`。短引按已有流程单独审核；重新下载固定来源不等于补齐产品知识。

已审核新增：`bazi.chapter.zhiming_boundary` → `bazi.section.s022` → `bazi.term.strength_review_boundary` / `bazi.rule.r012`。短引与上游 RAW 经既有 `normalize_text` 后逐字匹配，限定任氏曰前段，不含“若思按”“新增”。复用已登记 `bazi.source.ditiansui-spouse` 的固定 commit / SHA / C 等级，追加本次 review_scope。原典未提供月令权重或旺衰算法，所以规则为 `descriptive_only`；相关解释性 Golden / Phase2 晋级尚未完成，禁止冒充已执行的 RuleMatch。

回归检查原文/定位、无现代按语、无 provider、无 Phase2 晋级；已有34个结构 Golden 保留。本批不会生成身强身弱、喜用神或个人吉凶，也不宣称独立A/B校勘。

下一批审核目标仅取少量关系及限制：

1. 《滴天髓阐微》`/sections/3`（知命）：保留对不考察日主衰旺、机械用财官/神煞的限制。该旧 JSON 同段含“若思按”与“(新增)”标记，先核 attribution/edition/rights；不能把整段都按古籍公版复制为 Evidence。
2. 同书 `/sections/34`（夫妻）、`/sections/39`（女命）：复用 main 已审核的 `bazi.section.s018/s019` 及既有配偶星冲突边界，避免重复造定义；新增解释关系仍须逐段保存条件、反例，不能从一句官星/桃花断现代关系。
3. 《渊海子平》`/sections/5`（月令）、`/sections/9`（大运）：先核上下文与顺逆/起运变体，再建立规则与反例。

已有古籍 Canonical 正文只作待审定位，字面不变；仅增补既有 Phase1 知识 bundle 和来源审核范围。原始 snapshot 和《三命通会》完全不动。此批不声称独立 A/B 印证，不升证据等级。

最新 main 已将八字结构接入同一 Phase1/Phase2 模型，并实现双人关系、显式配偶星 lens 与结构型 Scenario。本批复用这些资产，后续继续按同一 Classic/Chapter/Section/Term/Rule/Concept、`validate_knowledge`、来源审计、Golden、Phase2 与产品覆盖检查补强旺衰/喜用/岁运。尚未完成解释审核前，不添加“能解释喜用/婚恋/财运”的生产 Rule。

原典、校勘、权利、Variant、反例及执行审核不能由一次下载或自动测试代替；这些项仍 pending，后续不得把本批报作“八字知识库完成”。
