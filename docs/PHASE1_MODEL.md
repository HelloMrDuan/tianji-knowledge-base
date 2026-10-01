# 六域 Phase 1 模型与审核边界

新增模型延续 `data/canonical/<domain>/`，不迁移历史知识。域注册在
`config/domain_registry.json`，书目级来源在 `config/knowledge_sources.json`，
JSON Schema 在 `schemas/knowledge/`。原有仓库信任等级不等于本模型的证据等级。

来源 A：独立权威原典相互印证；B：原典与独立可靠整理本一致；C：单一可追溯原典；
D：现代实现或尚待复核。不能因两个网站复制同一电子本而提升等级。
D 不作为新增 Canonical 核心知识的证据。

书目 → 编/章 → 选段 → 术语/规则。每条引用保存原文、来源 ID、选段 ID，
并检查原文确实存在于所固定的本地证据文件。选段定位可采用原有 JSON 路径，
或纯文本的字符区间；编辑划分须明确标记，不能冒充原书章名。

公版原典整本可留在 QUARANTINE。逐段复核通过的短选段进入 CANONICAL，
不表示整本已校勘。经典的 `body_stage` 表达整本状态。
保存的正文不包含现代讲解、编辑前言或版权不明的新作。

RAW 缓存在忽略目录 `data/raw/`，固定校验和后进入 QUARANTINE，
有明确审核记录的选段才可进入 CANONICAL。上游更新不得修改 Canonical；
现有自动同步清单不加入这些新选段，后续更新仍须另开审核 PR。

规则必须声明输入、条件、操作、结果、例外、流派、版本及执行状态。
`executable` 仅指已提供并测试的确定性操作；不等于占断或完整排盘已实现。
`partially_structured` 明确缺少的步骤；`descriptive_only` 保存文本规则及证据。
原典支撑传统关系，现代形式化需在操作和例外中注明，不能冒充古籍原句。

原有 Canonical 及《三命通会》隔离校勘文件的基线散列保存在
`config/phase1_protected_files.json`；CI 检查全部字节不变。
运行：`pip install -e '.[validation]'` 后设置 `PYTHONPATH=src`，执行
`python scripts/validate_knowledge.py` 和 `python -m unittest discover -s tests`。
默认生产检索仍只读取 Canonical，完整隔离文本不参与推理。

自动刷新补充保护：源文件清单中的 Canonical 更新转存
`data/quarantine/refresh_candidates/`；定时工作流不再执行 Canonical 重建
或公版文本自动晋级。人工审核晋级仍可另开 PR。框架 PR 合并前，外部刷新
`0f43661` 仅替换旧周易文件的 64 个来源 commit 值；已逐字段比较确认正文和
属性完全一致，因此保护基线接受该外部元数据更新。

## 可重复构建与后续采集

安装 `pip install -e '.[validation,calendar]'`，运行：

```bash
python scripts/validate_knowledge.py
python scripts/build_phase1_coverage.py --check
python -m unittest discover -s tests
python scripts/build_index.py
python scripts/build_rag_chunks.py
python scripts/build_sqlite_fts.py
```

新索引逐条展开正式选段、术语、规则和概念，携带解析后的
source → classic → chapter → section → original_text、commit 与散列。
Citation/context 保留所有来源、证据等级、流派、版本及执行状态。
引用中隔离证据的文件路径用于审计，不是导入隔离正文的指令。

新现代实现证据已连同其 MIT LICENSE 按 commit 固定在隔离区；
不直接引用会被定时同步覆盖的工作快照。`retrieved_at` 使用本轮本地审查日期，
不虚构精确网络下载时间，也不改写旧 Canonical 的历史采集记录。

显式运行 `python scripts/stage_phase1_sources.py --source yijing.source.meihua --discover-head`
可比较已登记源最新 commit/blob；Git blob 必须校验吻合后才写 RAW 忽略缓存。
QUARANTINE 只新增版本化来源/差异元数据，默认不保存整本正文；不覆盖原审核证据，
不修改来源注册的固定 commit，更不写 Canonical。新 commit 的版权范围仍须复核。
每次下载、差异审查、选段审核与晋级均可形成独立 PR；该命令未挂到自动晋级流程。

覆盖生成器的九项标准仅衡量六域最小骨架。风水年份 D 表、紫微疑字、六壬初传
等待核事项始终列出；`phase1_complete` 不能被解释为全部内容可靠或全算法可执行。
