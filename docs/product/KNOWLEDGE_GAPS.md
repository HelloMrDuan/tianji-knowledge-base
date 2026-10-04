# 产品知识覆盖与缺口

由既有来源、Phase1/Phase2、Golden 与 Scenario 派生。报告不是知识库或发布授权；`--check` 检查漂移。

READY 表示指定结构 claim 的执行契约、证据、Golden 和测试绑定齐全；PRODUCTIZABLE 表示可做有限结构产品；PARTIAL 表示仍缺关键解释；BLOCKED_ADVANCED 表示聚合基础可用但高级解释受阻；NOT_BUILT 表示没有对应执行链。静态审计不冒充测试执行。

| 产品 | 状态 | 已接入的结构 claim 数 | 现有结构公开标志 |
|---|---|---:|---|
| 八字详批 | PRODUCTIZABLE | 7 | True |
| 今日运势 | PARTIAL | 1 | False |
| 本周运势 | PARTIAL | 1 | False |
| 本月运势 | PARTIAL | 1 | False |
| 今年运势 | PARTIAL | 1 | False |
| 桃花姻缘 | PRODUCTIZABLE | 1 | False |
| 事业财运 | PARTIAL | 1 | False |
| 缘分合盘 | PRODUCTIZABLE | 7 | False |
| 人生总览 | BLOCKED_ADVANCED | 4 | False |
| AI解梦 | NOT_BUILT | 0 | False |
| 一事占问 | PRODUCTIZABLE | 7 | True |
| 紫微专业工具 | PARTIAL | 0 | False |
| 奇门专业工具 | PARTIAL | 0 | False |
| 六壬专业工具 | PARTIAL | 0 | False |
| 风水专业工具 | PARTIAL | 0 | False |
| 周易专业工具 | PARTIAL | 0 | False |

能力逐项追踪、原典定位与下一批工作见 [KNOWLEDGE_CAPABILITY_MAP.md](KNOWLEDGE_CAPABILITY_MAP.md)。依赖图见 `data/product/knowledge_dependencies.json`。

现有 7 个确定性引擎；51 条 Phase2 Rule；40 个 Golden。
证据来源等级 {"C": 91, "D": 6}。GitHub 实现参考不能成为古籍证据；通用 RAG 可检索不代表已授权推断。

结构 claim 由实际 RuleMatch facts 绑定，并核对 Variant、当前 Golden 和逐字 Evidence。不得升级为吉凶、适配分、婚期或财富保证。AI 质量尚未批准，结构可用与 AI 放行分别检查。

## 既有治理与开发顺序

Source → RAW → Quarantine → Review → Canonical → Terms/Rules → Evidence → Variant/Conflict → Golden → Phase2 → Scenario。沿用现有 schema、来源登记、晋级记录和校验器，禁止另建旁路知识库。
暂停公开页面开发。保留十一产品入口、古风视觉、背景音乐播放/暂停/音量/路由持续播放、后台静音与山水云雾水墨动画需求，待底层阶段验收后实施。
每批一个专题：基础/月令/通根/透干 → 单一旺衰 Variant → 核心格局 → 喜用体系分别治理 → 大运/流年作用 → 婚恋/事业/双人条件解释。梦境来源审查可独立开展，传统与现代心理证据分开。

## 冲突和隔离

沿用既有 governance.school_conflicts：寅月司令分日异文=unresolved；传统配偶星观察口径差异=bounded；三刑 / 自刑口径冲突=unresolved。保留 Rule difference/exceptions、执行 unresolved 与来源审计。
《三命通会》维持 quarantine_only / canonical_ready=false；PUA 完成不代表整本可晋级。原始 snapshot 不改动。

## 来源与待审材料

- `易藏/术数/渊海子平.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`：整本 pending，Quarantine，不能因下载而晋级。
- `易藏/术数/滴天髓阐微.txt` @ `4a6d6f2088825f132521d848c2ea86cf9c9a7620`：整本 pending，Quarantine，不能因下载而晋级。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/3/text` 含 若思按、(新增)：逐段排除未审核现代注释。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/4/text` 含 若思按：逐段排除未审核现代注释。
- `data/canonical/classics/bazi/ditiansui_chanwei_v1.json#/sections/7/text` 含 若思按：逐段排除未审核现代注释。

知命前段新增描述性规则 `bazi.rule.r012` 只禁止机械套财官食印，没有编造旺衰算法或权重。后续 executable 仍须独立完成证据、反例与测试。
