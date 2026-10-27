# TJ-011.2 S5 密封 Phase1/Phase2 注册治理（E0254）

本批把多批积压的 `pending_phase1_rule_registration` 披露项逐项清点处置：
能在密封 Canonical 内逐字验证定义锚点、且经 ExecutionTrace 真实执行绑定的，
按密封侧既有机制（可信机受控环境：私有数据树著录 → `private_data_snapshot`
导出 → 校验 → 换位 live 快照 → 更新 `cicd/env/trusted-acceptance` 钉值）补登记
并翻转披露；前提不成立的维持 pending，逐项登记实证理由与解锁路径。
**判定面零变化**：两条翻转谓词的 classification、条件集、blockers 与全部其他
产出逐字不变（全量比对见 §4），变化仅在 `why.sufficient_rule`、
`matched_rule_ids` 与披露文本。本批不借用、不冒充任何既有规则 ID。

机器可读登记与本文件同源：`src/tianji_kb/bazi_registration_governance.py`
（公开测试 `tests/test_tj0112_s5_registration_public.py` 钉住二者与代码披露
的一致性；密封回归 `tests/test_phase2_baziregistration.py`）。

## 1. 逐项清点与处置

清点口径：以 main（`7b52527f`，台账 E0253）现行代码全文实测
`pending_phase1_rule_registration` 全部出现处为准，共 12 个文件、17 个处置项。
锚点验证方法：各登记模块的全部登记引文逐条与密封 Canonical 59 条 section
文本做逐字包含检验（可信机实测）。

| # | 项 | 处置 | 理由（实证） |
|---|---|---|---|
| 1 | 调候 tiaohou-qiongtong-v1 | 维持 pending | 《穷通宝鉴》不在 Canonical 经典内（仅渊海/三命/协纪/滴天髓四书），全部引文无 section 可绑（canonical_evidence_absent） |
| 2 | 木×亥 pure_generating_support | **已注册 r029** | 定义锚点全部在 Canonical 内（从旺 s047、长生禄旺例 s026、本气 s034/s035、藏遁歌 s004、春木 s052、刑义 s021），与 r024 引用集同构；经 trace 执行 |
| 3 | 丙×午 commanding_visible_support | **已注册 r030** | 从强 s048、从旺 s047、比肩/余气 s025/s041、长生禄旺例 s026、本气 s034/s035、藏遁歌 s004 在 Canonical 内（登记 10 引文 7 条可验证；未验证 3 条为孤立定义/根重轻句/墓句，规则不引用，其操作内容由 s026 与因子规则 r018/r022 承载，同 r024 只引 Canonical 子集先例）；经 trace 执行 |
| 4 | 丙×巳 lu_visible_support | 维持 pending | 定义锚点「丙禄在巳」（三命卷二/卷三、神峰禄表）无 canonical section；F34 引文引用中三命/神峰部分 0 条可验证（canonical_evidence_absent） |
| 5 | 金×酉 pure_support_metal | 维持 pending | S1 根引文（三命卷二庚辛逐干句）0/10 在 Canonical 内（canonical_evidence_absent） |
| 6 | 水×子 pure_generating_support_water | 维持 pending | 壬癸逐干句 0/10 在 Canonical 内（canonical_evidence_absent） |
| 7 | 大运古典三 Variant | 维持 pending | 21 条引文 0 条在 Canonical 内（三命卷十一无 section；神峰不在 Canonical）（canonical_evidence_absent） |
| 8 | 大运组合 classical_dayun_timeline | 维持 pending | 组合层继承底层 pending，无独立规则（inherited_pending） |
| 9 | 大运视图 dayun-timeline-view-v1 | 维持 pending | 视图层继承底层 pending（inherited_pending） |
| 10 | 病药 bingyao-shenfeng-v1 | 维持 pending | 神峰不在 Canonical 经典内，9 条引文 0 条可验证（canonical_evidence_absent） |
| 11 | 禄刃路线 pattern_route | 维持 pending | 定义性禄/刃表（三命卷三禄节、卷五刃节）无 canonical section；4 引文仅路线排除句（s054）在册（canonical_evidence_absent） |
| 12 | 杂气 pattern_zaqi | 维持 pending | 原注杂气段与三命例证 0/3 在 Canonical 内（canonical_evidence_absent） |
| 13 | Slice D-1 ren-pattern-yin-true-v1 | 维持 pending | 锚点全在 Canonical（s053/s054/s024），但 determination 在 ExecutionTrace 之外产出、Phase2 golden harness 输入契约仅四柱无出生瞬时/交节 provider，注册无执行步可绑（execution_binding_structure） |
| 14 | 司令试点 bazi-siling-yin-pilot-v1 | 维持 pending | 独立 Variant 不经 trace；bazi Phase2 契约单 Variant；其定义性约定（连续 24 小时计日）为用户裁定的暂定程序约定、非原典规则；原典锚点 s024 已由 r017/r020/r026 覆盖（execution_binding_structure） |
| 15 | 司令矩阵登记 | 非候选 | 纯登记数据、无执行产出 |
| 16 | F4 丙×寅形态设计 | 非候选 | 未实现（实现门 = 司令扩月用户裁定） |
| 17 | 扶抑审定登记（S4） | 非候选 | 零行可建、无可执行单元；其 registration 字段是审定记录本身 |

解锁路径（维持项）：第 1/4/5/6/7/10/11/12 项均需先行 Canonical 扩编批
（对应经典建册或逐节登记入 Canonical 并逐条复核引文）后再行注册批；
第 13 项需执行绑定设计批；第 14 项需试点转正（用户裁定）并接入 trace；
第 8/9 项随第 7 项自动解除。

## 2. 本批实际注册（密封侧著录）

私有数据树（可信机受控检出）`data/canonical/bazi/` 三文件变更，纯增量：

- `phase1_knowledge.json`：规则 28 → 30。新增 `bazi.rule.r029`
  「纯印比生扶木月亥强状态充分裁决」（source_refs 8 条：s047/s052/s026/
  s033/s034/s035/s004/s021，引文全部取自 bundle 内既有引用并逐条复断
  `quote ∈ section.text`）与 `bazi.rule.r030`「丙日主午月当令显纯生扶
  强状态充分裁决」（source_refs 8 条：s048/s047/s025/s026/s041/s035/
  s034/s004）。两规则 operation/provider/result/exceptions 形制与 r024
  同构（provider `tianji_kb.operations.bazi_chart.strength_assessment`，
  research_only、PARTIAL）。
- `phase2_execution.json`：规则 29 → 31。新增
  `bazi.phase2.strength_pure_generating_support`（phase1_refs=[r029]）与
  `bazi.phase2.strength_commanding_visible_support`（phase1_refs=[r030]），
  均 executable + validated，golden_case_ids 各 1、regression_test 为
  `tests/test_phase2_baziregistration.py`。契约 `scope` 一句同步更新为
  四条已注册充分规则口径（原文只述卯/酉两条，早已陈旧）。
- `phase2_golden.json`：用例 117 → 119。新增
  `bazi.adjudication-strong-hai-generating`（癸亥/癸亥/甲子/甲子）与
  `bazi.adjudication-strong-bingwu-commanding`（丙午/甲午/丙寅/甲午），
  expected 只钉 classification 级字段（与既有 adjudication 用例同形），
  均经组装环境实算验证。

公开侧配套：`bazi_adjudication.py` 两谓词改走各自注册 trace 步
（`relevant` 集合同步增两步）、limitations 两行改注册口径；
`bazi_xiyong_readable.py` 的 RULE_TO_PREDICATE 增两映射（commanding 的
谓词名仍不在 PREDICATE_LABELS，本层对其继续 fail-closed，与注册前一致）；
`bazi_fire_morphology.py` 的 F1 登记 evidence_binding 改注册口径；
`bazi_conflict_presentation.py` LIMITATIONS 陈旧文本（「仅 3 条木日主
充分谓词」）订正为现行 7 条谓词口径（4 注册 + 3 待注册），该层其余定性
结论未动。

## 3. manifest 钉值记录（不静默改钉）

- 快照文件数 235 → 235，总字节 13,518,179 → 13,531,890。
- manifest SHA256：`8055efb3881128837548da2536f210928db96b4f295ad25bbfb09ba9cf89c6c1`
  → `b9f9b8fd37c812ffda7e075c38e48ab406e1aeb75b4944bb42907ae98661db5a`。
- 变更后三文件 SHA256：phase1_knowledge `f2360d400f335d3c9741fbd40e31bbf0daeb50d208e06c7631b6c369c34552cc`、
  phase2_execution `947cfc1d05c248c9e4d1efd35e9fde450e0dee2f77b1a4d150b92b9492ae8720`、
  phase2_golden `eebda931f7be6a812a7929ad1052905330dcabc80637a997a128e6f1ba1ac3ca`。
- 可信机 `cicd/env/trusted-acceptance` 已更新为新值；旧快照与旧钉值在
  机器侧留档备份（`secure/tianji-knowledge` 换位前备份 + 备份目录
  `s5-backup-20261028`），可整批回退（恢复旧快照 + 旧钉值即可，公开侧
  翻转代码在旧快照下 fail-closed、不会误绑）。
- 向后兼容已验证：现行 main（`7b52527f`）对新快照全量验收 SUCCESS
  （新增实体为纯增量，旧代码不引用新规则）。

## 4. 验证

- 机上全配方复跑（PR Head + 新快照 + 新钉值）：SUCCESS，计数与基线
  1903 的对账见 PR 正文（新增：公开 S5 治理测试、密封
  test_phase2_baziregistration、Phase2 golden 用例 +2 驱动的既有套件
  计数变化逐项列明）。
- 判定面不变性：以七谓词全部 Golden 见证/反例盘 + D-1/格局/调候抽样盘，
  在（旧代码 + 旧快照）与（新代码 + 新快照）两组装下逐盘比对
  classification 与 conditions，差异仅两条翻转谓词的
  sufficient_rule / matched_rule_ids / 披露文本（脚本与结果见 PR 正文）。
- Phase4 冻结文件零触碰（本批改动文件均不在 engine-baseline 17 文件内）。

## 5. 未覆盖

- 土根消费接入（S2 通道三陈述复核订正、ungraded 格资格裁定）仍另批。
- F4 实现待司令扩月用户裁定；维持 pending 的 12 项按 §1 解锁路径另行
  排批（Canonical 扩编为多项共同前置）。
- 018-F/G/H、三刑事实层、合化裁定等既有队列不变。
