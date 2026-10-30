# TJ-018.3 P1《论三刑》Canonical 逐节晋级（E0329）

用户 2026-10-30 授权 P1 直接实施：完成《论三刑》真正的密封
Canonical 章节晋级与证据绑定。机器可读登记与本文件同源：
`src/tianji_kb/bazi_registration_governance.py` 的
`TJ0183_P1_RECORD` 与 REGISTRATION_INVENTORY 的
`sanxing-branch-fact-v1` 项（公开专项
`tests/test_tj0183_p1_sanxing_promotion_public.py` 钉住二者与
事实层披露的一致性；密封专项
`tests/test_tj0183_p1_sanxing_promotion_sealed.py` 只在离线
验收运行）。

**先行结论（与晋级前置审计的总声明一致）**：本批建成了
Canonical 章节与证据绑定，但**注册未翻转**——执行链核查
（§3）证明三刑事实层不存在可绑定的执行步，强行登记即空
注册。`evidence_binding` 保持 `pending_phase1_registration`、
`phase2_rule` 与 `sufficient_rule` 保持 None，事实层披露字段
逐字未动。本批不宣称正官破格、完整三刑效力或八格真假解锁；
组名采用（B2）、统一教义 executable（B5）、破格消费（B4）
状态逐字不变。

## 1. Canonical 建节（密封侧著录）

私有数据树（可信机受控检出的暂存副本）`data/canonical/bazi/
phase1_knowledge.json` 纯增量变更，实体计数：chapters 20→21、
sections 59→60、terms 30→31，classics 4、rules 30、concepts 18
不变：

- classic `bazi.classic.sanming_tonghui` 新增 `source_ids` 绑定
  两来源：`bazi.source.sanmingtonghui`（快照 S0，原文依据）与
  `bazi.source.sanmingtonghui-applied`（正式应用文本 S3，本节
  文本依据，见下）。主 `source_id`
  `bazi.source.sanming-xianchi-niutrans` 与 `body_stage`
  `quarantine` 逐字不变；整书 `canonical_ready` 保持 false，
  本批是单节建节、不是整书标记。
- 新增 chapter `bazi.chapter.sanming_sanxing`（卷二·论三刑）。
- 新增 section `bazi.section.s060`（三命通会·论三刑）：文本为
  正式应用文本 `sanming_tonghui_applied_v1.txt`（S3，sha256
  `a89c0b5d…`）字符 71874–74853 整节逐字（2,979 字），review
  口径只确认组表结构事实的原典依据，名目冲突并列不裁、吉凶
  断语不晋级，概念 `bazi.concept.conflict_three_punishments`
  字段逐字不变。
- 新增 term `bazi.term.branch_punishments`（三刑）：定义采
  本节总结句原文，2 条 classical 引文绑定 s060。

文本依据的形制核查（晋级审计 §8 预留项，本批两轮实测后定案）：
密封校验器 `validate_knowledge` 要求 section 文本必须是其
`source_id` 已登记来源文本的子串、来源须在 classic 的
`source_id`/`source_ids` 内，且 Canonical 全域另有跨域测试钉住
的不变量——任一 section 文本不得含 PUA 码位。本节快照 S0 切片
（71874–74856，2,982 字）含 PUA 8 处（惨 1、带 6、玄 1）：首版
按 S0 建节在机上全配方复跑中被跨域不变量实测否决（backend 段
4 处既有钉值失败之一），故改以 TJ-018.3 正式应用文本 S3 为
依据——S3 经 PUA 全核映射与 603 条订正正式应用（E0298），
本节切片（71874–74853，2,979 字）PUA 归零。为此公开侧配套
登记：`config/knowledge_sources.json` 新增来源
`bazi.source.sanmingtonghui-applied`（content_path 指向快照内
应用文本、sha256 与 S3 钉值一致、kind classical、证据级 C），
`config/phase2_source_audit.json` 同步增谱系行（与 S0 同一
lineage_group，不投独立票，edition/authority 均 unverified、
grade_ceiling C）。S0 快照仍为原文依据存于 quarantine 层，
引文原字与校定读法对照见 018-B 校勘记；本登记只及本节，
整书 canonical_ready=false 不变。

## 2. 引文绑定验证（11 条）

018-B 登记引文 11 条（`sm3.enum_opening`、`sm3.enum_group4_partial`、
`sm3.direction_statement`、`sm3.summary_groups`、`sm3.counting_method`、
`sm3.wuen_core`、`sm3.zixing_definition`、`sm3.sanche_variant`、
`sm3.houyue_bracket`、`sm3.chong_definition`、`sm3.polu_poma`）
逐条复核：于登记定位点在快照原文逐字复现，且全数包含于
s060 节文本（机上实测 11/11）。组名不入任何产物、输出零效价
字段的事实层口径不变。

## 3. 执行链核查（决定不翻转的核心实证）

逐项实测（live main `006097d5` 公开代码 + 密封 bundle）：

1. 事实函数 `reviewed_branch_punishment_facts` 在生产代码中
   **零调用点**：不被 `tianji_kb.operations.bazi_chart.chart`
   或任何场景/API 路径调用；公开投影中的
   `branch_punishment_facts` 剥离只是防御性处理，生产产出
   从不携带该键。
2. 函数不经 ExecutionTrace、无 RuleMatch 产出；其定位在
   审定登记（E0267）中明示为独立函数、与
   `reviewed_branch_pair_relations` 并列，「是否并入其输出
   另批审定」。
3. Phase2 golden harness（`tianji_kb.golden.run_cases`）只
   执行 `tianji_kb.operations.*` provider；注册契约测试要求
   golden 用例**真实 fire** 注册规则（见
   `tests/test_phase2_baziregistration.py`）。本切片无从
   fire，Phase2 注册前提不成立。
4. S5 翻转先例（r029/r030）的标准是 Phase1 规则 + Phase2
   规则 + 见证盘经注册规则步发出三者齐备，翻转后的
   `evidence_binding` 取值本身即 `registered_phase1_phase2`；
   只建 Phase1 声明规则而无执行步，按治理登记册自身定义即
   `execution_binding_structure` 的「无执行步的空注册」
   （ren-pattern-yin-true-v1 同类处置）。
5. 审定消费边界明示「不建 Phase2 规则、不进
   unresolved_interactions」。

结论：注册前提不成立，`evidence_binding` 维持
`pending_phase1_registration`。缺口登记为治理项
`sanxing-branch-fact-v1`（disposition maintained_pending、
reason_class `execution_binding_structure`）；Canonical 建节
已消除本切片原有的 canonical_evidence_absent 面（晋级审计
候选 1 所指的阻塞），剩余缺口只有执行绑定结构一项。解锁
路径 = 执行绑定设计批：先审定事实函数并入 operations
provider 输出并接入 ExecutionTrace 的 placement（改变生产
产出表面，须独立审定），再扩 Phase2 harness 覆盖后另行
注册。本批未触碰该步，未伪造任何执行绑定。

## 4. manifest 钉值记录（不静默改钉）

- 暂存快照：237 文件（不变），总字节 15,883,200 → 15,902,169。
- manifest SHA256：`5ea551f5ffe3e3abbe42f4edf03dfe9d973fd7bc49ab7207180dc454ea874cbc`
  → `305e20be96a38b614495236f8c3252cf7e21c6d1635a5a29bce1c299b746526c`。
- 变更文件恰 4 个（逐文件对旧 manifest 比对）：phase1_knowledge
  （304,883 → 317,050 字节，新 sha256 `04354cbc…`）与实体计数
  变化使三份 coverage 工件按既有生成脚本再生成：
  `data/coverage/phase1.json`、`data/product/
  knowledge_coverage.json`、`data/product/
  knowledge_dependencies.json`；公开侧 `docs/COVERAGE.md` 与
  `docs/product/KNOWLEDGE_CAPABILITY_MAP.md` 同步再生成入仓。
- 钉值状态：新钉值即 `305e20be…`；live 快照换位、
  `cicd/env/trusted-acceptance` 改钉与私有构建脚本
  （`scripts/import_public_snapshot.py`）EXPECTED 钉值更新
  **须与本 PR 合并同步执行**（父级），本批未先行替换任何
  一端，暂存快照只用于机上复跑。回退路径不变（恢复旧快照
  目录 + 旧钉值）。

## 5. 验证

- `validate_knowledge` 对暂存 bundle 全量通过（schema、来源
  校验和、section 文本子串、term 引文绑定由既有校验器逐项
  执行）；密封专项另以断言钉住 s060 文本与快照切片逐字
  等值、11 引文包含、概念语义不变与无三刑 Phase1/Phase2
  规则存在。
- 独立复核：真实盘 Golden 10 例经生产历法链回放，柱与事实
  期望逐字全过（差异探针内含断言，新组装实测通过）。
- 同盘差异测试：129 个真实盘（119 个密封 Phase2 Golden
  柱面输入 + 10 个三刑真实出生时刻盘）在（旧快照）与
  （暂存新快照）两组装、同一公开代码下，chart 全量产出、
  三刑事实与公开投影逐字一致（21MB JSON 字节级相同）——
  判定面零非预期变化。
- 机上全配方复跑按站立规则在与本 PR Head 逐字一致的机上
  检出 + 暂存快照 + 新钉值执行，结果（SUCCESS 总数与三段
  分布）入账于本批 PR 记录与台账关账事件（执行批 E0329
  备注「结果见 PR」口径同 E0327）。
- Phase4 冻结文件零触碰（本批改动文件均不在
  engine-baseline 17 文件内）。
- 首轮全配方复跑 backend 段实测 4 处既有钉值失败，均为真实
  建节移动的钉值，逐项处置并在修订后复跑归零：（1）跨域 PUA
  不变量 → 节文本改 S3 依据并新登记来源（§1）；（2）合化审定
  登记 `SEALED_MEASUREMENTS.phase1_sections_total` 59 → 60
  （s060 经实测不含合化关键词与「五合」，其余合化钉值不动）；
  （3）三刑密封钉「提及刑的 Canonical 节集合」由 {s020, s021}
  增 s060；（4）三刑隔离扫描将治理登记册列为本切片披露台账
  豁免（登记册只以数据形式提名切片，公开专项另钉其不 import、
  不调用实现，零消费接线的不变量实质不变）；（5）新来源登记
  使来源普查 C:95 → C:96（登记表 101 → 102 条），全部普查
  钉值逐处同步并带普查同步叙述，共 32 个测试文件（含
  test_product_coverage、test_dream_source_review、
  test_tj012_luren_route_sealed、test_tj012_siling_matrix_sealed、
  test_tj012_zaqi_selection_sealed、test_tj0171_dayun_collation
  与各密封专项的 Registry 普查钉，仿 TJ-017.1 登记三命快照时
  的同口径处置）。全部测试更新均只随真实登记增项移动钉值，
  不放宽任何判定断言。

## 6. 未覆盖

- 执行绑定设计批未立项：事实函数并入生产产出的 placement
  审定（含公开投影与场景消费面变化）属独立审定，不在本批
  授权内。
- P2 卷二干支两节补充审定（用户已授权、与本批并行不阻塞）
  与 P3《论阳刃》暂缓，均不在本批范围。
- 事实层其余 pending 面不变：未刑丑等级 C 边（B1 证据
  工程）、组名（B2）、程度命题（B3）、破格消费（B4）、
  统一教义（B5）逐字保持原状。
