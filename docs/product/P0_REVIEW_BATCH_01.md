# P0 来源复核第 1 批

本批沿用现有 `acquisition.stage_candidate`，重新取得已登记来源的固定 commit，校验上游 Git blob，保存 RAW 缓存与 Quarantine 元数据。仅重建审核候选，没有新增书目、领域 schema、古文定义、推断规则或 Canonical。

| 来源 | 固定版本/采纳方式 | 隔离候选 |
|---|---|---|
| [滴天髓阐微](https://github.com/garychowcmu/daizhigev20/blob/4a6d6f2088825f132521d848c2ea86cf9c9a7620/易藏/术数/滴天髓阐微.txt) | daizhigev20；PUBLIC_DOMAIN_EXTRACT_ONLY；电子底本/作者归属待核 | `data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/e269843d0544fd18ac7d7c97d4e0bd268a5240ef.json` |
| [渊海子平](https://github.com/garychowcmu/daizhigev20/blob/4a6d6f2088825f132521d848c2ea86cf9c9a7620/易藏/术数/渊海子平.txt) | 同一已登记仓库及固定 commit；不视为两部独立校勘版本 | `data/quarantine/phase1_candidates/daizhigev20/4a6d6f2088825f132521d848c2ea86cf9c9a7620/c7de6ab493e19460f5efba49085d20437c17e1d4.json` |

RAW 不提交 Git；候选维持 `stage=quarantine`、`review_status=pending`、`evidence_level=D`、`promotion_allowed=false`。重新下载固定来源不等于补齐产品知识。

下一批审核目标仅取少量关系及限制：

1. 《滴天髓阐微》`/sections/3`（知命）：保留对不考察日主衰旺、机械用财官/神煞的限制。该旧 JSON 同段含“若思按”与“(新增)”标记，先核 attribution/edition/rights；不能把整段都按古籍公版复制为 Evidence。
2. 同书 `/sections/34`（夫妻）、`/sections/39`（女命）：逐段保存传统 lens、条件与反机械解读材料，不从一句官星/桃花断现代关系。
3. 《渊海子平》`/sections/5`（月令）、`/sections/9`（大运）：先核上下文与顺逆/起运变体，再建立规则与反例。

已有 Canonical 文件只作待审定位，保持字面不变；既有原始 snapshot 和《三命通会》完全不动。此批不声称独立 A/B 印证，不升证据等级。

八字目前不在既有 Phase1 schema/domain registry 的六域枚举中。正式入模须在同一 Classic/Chapter/Section/Term/Rule/Concept 流程审核领域扩展，继续跑 `validate_knowledge`、来源审计、Golden、Phase2 与产品覆盖检查。尚未完成上述审核前，不添加“能解释喜用/婚恋/财运”的生产 Rule。

原典、校勘、权利、Variant、反例及执行审核不能由一次下载或自动测试代替；这些项仍 pending，后续不得把本批报作“八字知识库完成”。
