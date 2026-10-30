# TJ-018.3 批一 三刑事实执行接入（E0333）

用户 2026-10-30 授权，按设计 docs/product/TJ0183_EXECUTION_BINDING_DESIGN.md
实施批一：三刑事实函数以唯一接入点接入生产执行并完成 Phase1/Phase2
注册（bazi.rule.r031 / bazi.phase2.branch_punishment_facts），三刑切片
自 E0267 审定以来以 execution_binding_structure 维持 pending 的缺口
就此解除、evidence_binding 翻转为 registered_phase1_phase2。默认关、
用户可见能力零变化。本批不实施 r032–r034、不建干支 Canonical、不处理
阳刃、不解锁 U1/U3；组名 B2、统一教义 B5、破格 B4 状态逐字不变。

## 0. 设计文档完整性说明（如实记录）

合并入 main 的设计文档 TJ0183_EXECUTION_BINDING_DESIGN.md 实测只有
568 行（38,871 字节），止于 §7.3 中途，§§8–11 不在合并文件中（设计
批源文件同为 568 行，截断发生在设计批写作/推送环节）。本批的规范性
设计内容（接入点、契约、分离设计、执行语义、等价口径）位于 §§1–7，
完整自洽；实施范围与验收由用户授权文本与父级任务书独立完整给出。
未决点中与批一相关的引文子集定稿一项，按在册摘要（设计推荐六条、
备选全引 11 条）与 §2 的可审计口径定稿。§§8–11 的缺失如实记录于
此，是否另行订正补入由父级决定。

## 1. 接入实现（公开侧）

- `operations/bazi_chart.chart`：签名新增 keyword-only 参数
  `include_punishment_facts=False`（bool 严格校验，既有位置参数调用
  逐字兼容）；关系事实块之后、strength_factors 步组之前新增门控
  事实步——开启时以四柱地支调用 `reviewed_branch_punishment_facts`，
  经 `trace.add` 写入 `bazi.phase2.branch_punishment_facts`（input
  `{'branches': [...]}`、output 为事实函数返回逐字）；结果键
  `branch_punishment_facts`，`production_scope` 追加一句；开启时封套
  `research_only=True`、`ai_may_explain=False`。
- `engine.execute`：新增门禁一行——bazi 域传入
  `include_punishment_facts`（非 None）且非 allow_research 时拒绝，
  与既有研究参数门禁同口径；默认调用方不传参即旧行为。
- 事实步与裁决面分离：事实步不产生 RuleMatch（trace 派生的
  rule_matches 条目仅为其执行记录，status=executed）、不写入任何
  sufficient_rule、不进 strength/pattern/adjudication 任何输入
  （密封专项逐盘断言钉住）。
- 公开投影：`public_projection` 既有 `branch_punishment_facts` 剥离
  逐字不变（本批对该文件零修改），单独复跑断言在密封专项内。
- E0267 承接：`bazi_sanxing_fact_adjudication` 新增 append-only 常量
  `EXECUTION_BINDING_TAKEOVER`，显式承接 E0267 的
  consumption_boundaries 四条与 placement_decision（其「另批审定」
  即执行绑定设计批 E0332 与本批）；SLICE_SPEC 原文字逐字未动。

## 2. 密封注册（著录）

- Phase1 `bazi.rule.r031`：字段照 r029/r030 同构（definition、
  conditions、operation、exceptions、term_refs=
  [bazi.term.branch_punishments]）；编号经机上实测未占用（既有
  Phase1 规则 30 条、最大 r030），无需顺延。
- source_refs = 6 条定义性引文子集（只引 bazi.section.s060）：
  sm3.enum_opening、sm3.enum_group4_partial、sm3.summary_groups、
  sm3.counting_method、sm3.wuen_core、sm3.zixing_definition。
  定稿口径：审定登记 GROUP_TABLE 三组与 self_punishment 行
  evidence_refs 的并集恰 6 条；逐条以快照字形本逐字验证于 s060
  节文本（6/6 在场）；覆盖组表（summary_groups）、七条入切片
  环边（A 级六条见 enum_opening、B 级卯刑子见 counting_method）
  与自刑全集（辰午酉见 enum_opening、亥见 enum_group4_partial、
  zixing_definition 为全集定义句）。未扩到 11 条。
- Phase2 `bazi.phase2.branch_punishment_facts`：executable /
  validated，phase1_rule_refs=[bazi.rule.r031]，
  regression_test=tests/test_phase2_bazisanxing.py（契约 schema 对
  regression_test 有 `^tests/test_phase2_[a-z]+\.py$` 模式约束，
  密封专项据此命名），golden_case_ids 为下条 10 例。
- Golden 新增 10 例 `bazi.sanxing-fact-*`：由公开
  golden_tj0123_sanxing_impl.json 的 10 个真实出生时刻盘（经生产
  历法回放的四柱）转入密封 Golden 口径，input 带
  `include_punishment_facts=True`，expected 只断言
  branch_punishment_facts 与事实函数输出逐字一致。
- 密封文件变更恰 4 个：`data/canonical/bazi/phase1_knowledge.json`、
  `data/canonical/bazi/phase2_execution.json`、
  `data/canonical/bazi/phase2_golden.json` 三个著录文件，加
  `data/coverage/phase1.json`——该文件由
  scripts/build_phase1_coverage.py 按模型再生，差异恰两处计数
  （rules execution_status executable 18→19、production_chunks
  139→140），均系新增 r031 的直接结果；
  knowledge_coverage / knowledge_dependencies 经实测无需变更
  （build_product_coverage --check 与完整性测试通过）。

## 3. 注册翻转

- `bazi_registration_governance`：sanxing-branch-fact-v1 处置
  maintained_pending → registered（phase1_rule_id /
  phase2_rule_id 在案）；FLIPPED 2 → 3 项、MAINTAINED 13 → 12 项；
  新增 TJ0183_EXECBIND_RECORD（含引文子集清单、密封文件变更与
  manifest 前后值）。
- `bazi_sanxing_facts.SLICE_REGISTRATION`：evidence_binding
  pending_phase1_registration → registered_phase1_phase2，
  phase2_rule 填入新步 ID；sufficient_rule 保持 None，
  research_only / public_enabled / ai_enabled 旗标不变；
  SLICE_SPEC（审定登记）注册字段逐字不动。
- 翻转五条件核对（用户 §五）：真实生产执行接入完成 ✓ / Trace
  记录真实执行步 ✓ / Evidence binding 经 EvidenceResolver 实测
  通过 ✓ / Golden 与全部规定测试通过 ✓ / 正式验收与部署验证
  ——第五项为终局条件：PR 内翻转视为待终局确认，由父级在关账
  时以管线对 Merge SHA 的正式验收与部署记录复核。

## 4. 等价与证据（机上实测）

- 129 盘双路径比对（119 密封 Golden 柱面输入 + 10 真实出生盘，
  密封专项 EquivalenceTests 逐盘执行）：门控关全产出与既有行为
  逐字一致（Golden 全量 129 例经 harness 复跑全过）；门控开差异
  恰在设计 §7.2 封闭清单内——result 新增 branch_punishment_facts
  键与 production_scope 追加一句、trace 新增事实步一条、evidence
  新增该步 6 条引文、rule_matches 新增该步 executed 条目、封套
  research_only/ai_may_explain 标记、其后步 fact_ref 索引位移而
  所指内容逐字一致（比对以 fact_ref 规范化后深比对）。
- 12⁴ 穷举守卫复跑通过（事实函数级，密封专项内：等级 C 边
  未→丑 在任何输入下不出现、names 恒 None）。
- Golden harness 真实 fire 新步 10/10，步 output 与事实函数逐字
  一致；EvidenceResolver 对 r031 六条引文逐条子串验证通过；
  伪造引文负例（内存副本篡改 original_text）被拒（ValueError）；
  未注册步名 trace.add fail-closed 抛错。
- 旺衰见证盘（癸×子 1981-12-21）在门控开/关下
  strength_assessment 逐字一致（fact_ref 规范化后），
  sufficient_rule 保持 None、sufficient_predicate 保持
  pure_generating_support_water（r032–r034 未实施的披露不变）。
- 回滚演练：新代码 + P1 终局快照（manifest 305e20be）组装下，
  默认路径 129 盘产出与 P1 基线一致，开启路径因事实步未注册而
  fail-closed 抛错、不静默产出未注册事实（演练记录见本批复跑
  证据）。

## 5. manifest 钉值记录（不静默改钉）

- before：237 文件 / 15,902,169 字节 / manifest sha256
  305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c
- after：237 文件 / 15,922,702 字节 / manifest sha256
  b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622
- 暂存快照：机上 /data/workspace/tj0183-execbind-stage/snapshot；
  live 换位与 cicd 改钉由父级在合并前执行（先换代、后合并）；
  私有检出侧 EXPECTED_BYTES=15922702 与检出 manifest 已同步
  重生并 verify 通过。

## 6. 验证

- 机上全配方复跑（暂存快照 + 本批代码，合并前硬门）：
  accept_offline.py --suite all SUCCESS（计数与对平见 §7 关账
  补记前的复跑记录：正式基线 2613 测 = 管线对 c466a87e 的正式
  验收直读；本批新增 = 密封专项 test_phase2_bazisanxing 与公开
  专项 test_tj0183_sanxing_execbind_public 两套，另有计数钉点
  随注册状态迁移更新，逐项对平见 PR 描述）。
- 公开 CI 与台账门禁（plain + --base 双模式）在 PR 上复核。

## 7. 未覆盖与边界

- 用户可见能力零变化：事实块只在研究门控开启时出现于执行封套，
  公开投影剥离；无任何场景接线变更；默认生产表面逐字不变。
- B2 组名采用、B5 统一教义 executable、B4 正官破格前置状态
  逐字不变；bazi.concept.conflict_three_punishments 口径不变
  （status unresolved、executable_policy
  blocked_pending_school_resolution）。
- 批二（干支三规则，拟定 r032–r034）与批三（阳刃重新评估）不在
  本批范围。r026 密封侧契约复核结论（批二前置）：密封
  phase2_execution.json 中 gate 步
  bazi.phase2.strength_bounded_adjudication 的 phase1_rule_refs
  实测为 [bazi.rule.r026]，与设计 §1 描述一致。
- 设计批 §9 对表：批一实施要求逐条按 §§2/4/5/6/7 与用户授权
  文本执行；设计文档 §§8–11 缺失的影响仅及 §10.2 子集点名
  一项，已按 §2 口径定稿并在册。

## 8. 正式验收与部署记录（关账批补记）
