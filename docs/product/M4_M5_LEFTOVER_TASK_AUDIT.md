# M4/M5 遗留任务真实状态核实（TJ-019.2 / TJ-022.2 / TJ-023.3 / TJ-025.2）

审计批 [B033]，事件 E0274–E0277。核实基线：公开 main `a6327830bd9d40a76cd34382674f25d22b53c4cf`，台账 273 事件（末号 E0273）。本批只核实与落账：不变更任何任务状态、不实现任何功能；状态变更建议只写在本文件，待父级处置。

核实方法（逐项同序）：先读 WBS 原文行（`docs/product/DETAILED_DELIVERY_BACKLOG_V1.md`，任务定义以 WBS 为准）→ 对照 TASK_STATUS 现行行与 TASK_HISTORY 全部相关事件 → 仓内代码/测试实测 → 机上密封面与正式验收实测。正式验收口径取机上最新已部署验收文件 `acceptance-ac74e74ed12f31e62f2c85f2aa275fbabed1461c.json`（SUCCESS，private-backend 2167 测 / 193 模块 / 0 失败，密封 manifest `f053761c…`，235 文件）；当前 main `a6327830` 的管线验收在本批执行时尚未落账，本批结论不依赖其计数，只依赖该验收的模块执行集与仓内实测。

## 结论总表

| 任务 | WBS 一句话 | 结论 | 缺口分类 |
| --- | --- | --- | --- |
| TJ-019.2 小批新场景真实入库 | 每批 1～3 条逐字审核，至少两条语义正例、两条错误主题反例、两条否定/第三人弃判 | **未开始** | 可直接续建 |
| TJ-022.2 经审配偶宫/星与年运条件 | 只有 M2/M3 审核通过的条件可参与；缺失直接限界 | **部分完成** | 配偶星面与条件解释面被 M2 阻塞（TJ-013.1 / TJ-013.2） |
| TJ-023.3 已审大运与流年合用（以后置为准） | 未经 TJ-017 完成，不输出事件应期或收益/职位承诺 | **未开始（正向能力）** | 被具体前置阻塞（TJ-017.2） |
| TJ-025.2 人生总览的条件说明/无法裁决出口 | 缺来源就显示“本项尚未具备解释条件”，不加综合个人评价 | **部分完成** | 统一条件标记面与任务级验收可直接续建 |

四项共同台账事实：TASK_STATUS 四行均为「阻塞／等待证据/前置依赖」，PR 列与日期列均为空；TASK_HISTORY 中以四项为任务列的事件均为 **0 条**（全文仅 E0097 的备注提及「TJ-025.2 保留阻塞」）。

## TJ-019.2 小批新场景真实入库 —— 未开始

已审梦境场景集合自存量定版以来恒为 **10**，三路独立实测一致：

- 公开代码 `src/tianji_kb/operations/dream_knowledge.py` 的 `_SCENE_PARAPHRASES` 恰 10 个 `dream.term.*` 键（snake / water / fire / flying / falling / dragon / fish / house / family / money），注释自述「the ten already-reviewed scenes」。
- 机上密封快照全文检索 `dream.term.*` 恰 10 个不同 ID，与公开集逐一相同。
- `tests/test_phase1_dream.py::test_ten_reviewed_scenes_extend_existing_model_without_a_chart_engine` 与 `tests/test_dream_source_review.py`（断言 `reviewed_scene_count == 10`）均在正式验收 private-backend 模块执行集内。

TJ-019.1 需求矩阵的队列主题（考试、怀孕、结婚、工作、被追、故人、死亡）在同一文件中仅为 `_UNREVIEWED_INPUT_PATTERNS`：`status=input_observation_only`、`reviewed_interpretation_available=False`、`evidence_ids=[]` —— 只记输入观察，从未有任何一批按 WBS 验收形态（1～3 条逐字审核 + 每批 ≥2 语义正例 / ≥2 错误主题反例 / ≥2 否定或第三人弃判）入库。机上 quarantine 的周公解梦候选材料实测存在（18 个顶层条目），`docs/product/KNOWLEDGE_CAPABILITY_MAP.md` 亦载「下一批复核现有 `dream.source.zhougong-scenes`，沿原模型补规则条件及 Golden」——该「下一批」至今未执行。

缺口分类：**可直接续建**。TJ-020.1–020.3 语义层已合并（否定/第三人弃判机制现成），存量十场景即逐字审核 + Golden 入库的流程先例；TJ-018.3 行仍为「待做」属流程登记任务，不构成首批的硬阻塞。无须用户新裁定（取材以有精确动作原典者为限，无原典不取，是 WBS 与 TJ-019.1 既定口径）。

下一步建议批次：首批入库批 —— 从 TJ-019.1 队列中取有精确动作原典的 1～3 条逐字审核入库，每条配齐 ≥2 语义正例、≥2 错误主题反例、≥2 否定/第三人弃判并入正式验收执行集。

## TJ-022.2 经审配偶宫/星与年运条件 —— 部分完成

**已完成面（配偶宫 × 年运的结构参与）**：桃花场景 `src/tianji_kb/scenario_engine.py` 已产出 `spouse_palace_year_relations`：配偶宫（日支）与目标年地支按已审六合、六冲、六害成对规则核对，组合规则 `bazi.scenario.spouse_palace_year_structure` 派生自已审 Phase2 规则 `bazi.phase2.spouse_palace_day_branch` 等，Evidence 链闭合（配偶宫来源证据缺失即 `raise`，fail-closed），`interpretation_allowed=False` —— 经审条件参与、只报结构不作断语，符合 WBS「只有审核通过的条件可参与；缺失直接限界」的结构面要求。专项测试 `tests/test_romance_spouse_year_structure.py` 6 测（2026 子午冲、2027 子未害、2028 无已审配对不编造、缺引文弃判等）在正式验收模块执行集内。

**缺口面**：

- 配偶星未参与桃花年运：场景 limitations 逐字声明「夫妻宫仅以日支位置配对已审六合、六冲、六害；三合、刑、破、合化效力、**配偶星、旺衰喜忌、大运**和紫微等未组合裁定」。`traditional_spouse_star_lens`（`src/tianji_kb/bazi_core.py`）仅供合盘场景在用户显式选择传统口径时附加候选位置，且另有未裁冲突登记 `bazi.concept.conflict_spouse_star_lens`（`src/tianji_kb/bazi_hehua_fact_adjudication.py`）。
- 旺衰喜忌类条件未参与：扶抑本体未建、TJ-013.1 与 TJ-013.2 均阻塞、程度词与中和定义（U1/U3）经用户裁定暂缓 —— 属被 M2 存量阻塞，非本任务可自解。

**归属说明**：上述结构面为 WBS 立项前（2026-10-09）的引擎资产，其后从未以 TJ-022.2 名义立批或记账（B026 批 E0140/E0143 只核 TJ-022.1 咸池面）。WBS 标题含「配偶宫/星」两者，星面未成，本审计**不建议关账**。

下一步建议批次：维持阻塞；待 M2 存量（TJ-013.1 扶抑 / TJ-013.2 裁决）落地后派「配偶星经审条件接入桃花年运」批；其前可由父级决定是否先派纯核账批将既有结构面正式归属本任务。

## TJ-023.3 已审大运与流年合用（以后置为准） —— 未开始（正向能力）

事业财运场景的 `depends_on` 仅 `bazi.phase2.ten_gods`、`bazi.phase2.hidden_stems` 与历法库；结果面只有原局五组十神位置事实与目标年天干十神。`classical_dayun_timeline`（TJ-017.4 组合入口）在 `scenario_engine.py` 与 `api.py` 中**零消费**（全文检索 0 命中），场景 limitations 逐字声明「尚未纳入格局、喜用神、身强身弱、大运、流年支互动……」与「尚未纳入旺衰喜忌、大运流年与紫微交叉判断」。

前置未成：WBS 明文以 TJ-017 完成为界。TJ-017.1、TJ-017.4 已部署验收，但 TJ-017.2（原局＋大运＋流年跨规则调用，本任务「以后置为准」的后置本体）仍阻塞、TJ-017.3 行亦仍阻塞（公开开放未做）—— TJ-017 整体未完成。

否定面说明：WBS 后半句「不输出事件应期或收益/职位承诺」目前由 TJ-023.1 / TJ-023.2 两批的 limitations 与 `tests/test_career_interpretation.py`（`personal_prediction=False`、不编造吉凶词等断言，正式验收执行）守住，但那是姊妹任务的交付，不构成本任务的正向完成面。

下一步建议批次：维持阻塞，阻塞项点名 **TJ-017.2**（其前置为 TJ-013.2 冲突裁决与扶抑、格局用神）；TJ-017.2 落地后派「事业财运岁运合用」批，契约以后置（TJ-017.2 输出契约）为准。

## TJ-025.2 人生总览的条件说明/无法裁决出口 —— 部分完成

**已完成面**：人生总览后端集成报告（`src/tianji_kb/scenario_engine.py` 的 life 组合）已具逐维条件说明与无法裁决出口，且全部 fail-closed：

- 大运维：`dayun_timeline_approved=False`，出口原文「大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规则，本总览不推算或伪造大运时间线。」
- 旺衰维：`strength_context.classification="unresolved"`，boundary 原文「现有证据不能通用判定身强身弱、喜用神、格局或实际作用效力。」
- 跨规则维：`cross_rule_audit.reading` 明示流年与桃花夫妻宫两入口「复用同一套已审核规则，并非两份独立证据。不能由此推断婚期、事业、财运或实际应事。」`interpretation_allowed=False`、`personal_prediction=False`。
- 证据缺失或冲突即整单拒绝：`tests/test_life_integrated_report.py` 11 测含 `test_missing_strength_evidence_fails_closed`、`test_conflicting_year_facts_do_not_produce_composed_reading`、`test_cross_rule_mismatch_fails_closed` 等，在正式验收模块执行集内。

**缺口面**：

- WBS 验收文案「本项尚未具备解释条件」逐字检索全仓（src 与 web）**0 命中** —— 现有出口是逐维散文限界，没有统一的逐项条件标记面（哪项具备、哪项尚未具备及原因）。
- 本任务从未独立立批验收：E0097（TJ-025.3 批）明文「TJ-025.2 保留阻塞」；其后 TJ-025.1 批（E0150/E0154）只核四源聚合面，并明言后端集成测试「已覆盖，不重建」—— 覆盖的是聚合与一致性，不是 025.2 的条件说明验收口径。
- life 场景在 registry 中仍为 `production_limited`、`public_release=False`。

缺口分类：**可直接续建**（统一条件标记是既有事实之上的呈现与验收工作，不需要新流派裁定）。本审计建议：补齐统一标记面并做任务级真实后端验收后，可提议关账；状态变更由父级处置，本批不变更。

下一步建议批次：一小批「人生总览条件说明统一标记与 TJ-025.2 任务级验收」—— 逐维输出统一 condition 状态（具备 / 尚未具备 + 原因，文案以 WBS 为准绳），以真实后端执行验收逐项核对。

## 与既有记录的差异项

1. 四行 TASK_STATUS 备注同为「等待证据/前置依赖」，与实测不符（偏保守方向）：TJ-022.2 与 TJ-025.2 已有实质面在主干且经正式验收执行；TJ-019.2 与 TJ-023.3 的备注则与实测一致。本批已按实测同步四行备注（状态不变）。
2. `KNOWLEDGE_CAPABILITY_MAP.md` 载 dream-traditional「新增乘龙入水、群鱼游水、屋宅更新、兄弟相打、拾得钱物」—— 系 WBS 立项前 Phase1 阶段存量由 5 扩至 10 的扩容，不是 TJ-019.2 的批次成果，不得误记为本任务进展。
3. TJ-022.2 已完成面（配偶宫 × 年运）从未被任何台账事件归属到本任务，系本次核实首次落账。
4. 与 MEMORY 纲领优先清理队列（M4 TJ-018–021、M5 TJ-022.2 / TJ-023.3 / TJ-025.2 点名待核实）一致，无其他冲突。

## 本批落账方式（门禁实测）

`scripts/check_task_tracking.py` 的 `check_delta` 实测规则：无批号标记的 PR 走 legacy 路径（恰 1 个改动行 + 1 个新事件）；多行同改必须走批量路径 —— 全部新事件带同一未用批号标记、2–6 个任务、改动行集与事件任务集相等、事件状态与行状态一致。本批改动恰为四行备注同步（状态均不变），单事件无法通过门禁，故按批量路径落账：批号 **[B033]**（实测未用，已用至 [B032]），事件 E0274（TJ-019.2）、E0275（TJ-022.2）、E0276（TJ-023.3）、E0277（TJ-025.2）。父级中央分配号为 E0274，其余三号系批量路径门禁所迫的同批顺延，特此明示待父级亲核。
