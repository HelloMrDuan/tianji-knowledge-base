# GOVERNANCE_DAYUN_SANMING_PROMOTION — dayun-classical-variants 三命分段注册晋级（E0346）

治理 pending 8 项审计（E0341，docs/product/GOVERNANCE_PENDING8_AUDIT.md）dayun 三项逐项审计（§2.2/2.3/2.4）推荐第三批：为《三命通会》卷二《论大运》与卷十一珞琭子消息赋注大运见证窗口建 Canonical 节，把 TJ-017.1 古典大运 Variant 的三命分段（方向 + 三命换算）绑定为已注册的 Phase1 规则 + Phase2 执行步 + 密封 Golden，并按分段诚实口径翻转治理登记；神峰分段不连带翻转。本批基线 main `16459af1468ce81189909d57f6db837895fd9296`、台账 345 事件、密封钉 `2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6`。

## 0 授权与范围

- 授权来源：治理 pending-8 审计定 dayun-classical-variants 为真 pending（引文完整但《论大运》不在 Canonical 三命经典内），unlock_path 为「先补《论大运》018 形制登记与建节、引文改指应用文本来源，再行三命分段注册；神峰分段待神峰经典扩编，不得连带」；dayun-compose / dayun-timeline-view 为 inherited_pending、随三命分段翻转后按实测改记。本批按该路径分两阶段执行（阶段一登记、阶段二建节与绑定）。
- 开工三核实（2026-11-01）：API main HEAD = `16459af1468ce81189909d57f6db837895fd9296` ✓；TASK_HISTORY 345 事件、末号 E0345 ✓；机上 cicd 钉 = `2fdcfaec…` 且 live 快照 manifest 与之逐字一致 ✓；SSH known_hosts 指纹与在册一致 ✓。
- 不可动摇的语义边界（TJ-017.1 契约）：输出契约只有区间、无单点字段、无年龄键；恰逢节拒绝口径 `zero_jie_boundary_convention_unreviewed` 不变；对抗集 ADV-001..012 行为不变；研究层视图不接公开页面；用户可见能力变化为零。
- 明确不在本批范围：神峰分段（神峰方向旁证与神峰换算）不连带翻转、维持 pending；不改 dayun 输出契约；不接公开页面；不触扶抑 U1/U3；不混入 TJ-017.2（原局＋大运＋流年跨规则调用，仍阻塞于 M2）。

## 1 五问答复

1. **实际建立的 Canonical 实体**：新章 2（`bazi.chapter.sanming_lun_dayun`、`bazi.chapter.sanming_luoluozi_dayun_witness`）、新节 3（`bazi.section.s068` = 《论大运》S3 切片 741 字、`bazi.section.s069` = 卷十一见证窗口 A 261 字、`bazi.section.s070` = 见证窗口 B 24 字）、新术语 2（`bazi.term.dayun_direction`、`bazi.term.dayun_handover`）、Phase1 规则 `bazi.rule.r038`（方向）与 `bazi.rule.r039`（三命换算）、Phase2 步 `bazi.phase2.dayun_classical_direction` 与 `bazi.phase2.dayun_sanming_conversion`（均 validated）、密封 Golden +6 例（163 → 169）。密封规模迁移：章 27 → 29、节 67 → 70、术语 34 → 36、Phase1 规则 37 → 39、Phase2 步 38 → 40。
2. **真实解除的 pending**：dayun-classical-variants 的三命分段由 maintained_pending / canonical_evidence_absent 翻转为 registered（分段注册，见 §2.2）；神峰分段维持 pending 并在同一治理行内以 segments 明细逐字在册明示。dayun-compose / dayun-timeline-view 按实测改记 inherited（evidence_binding 改记 `segmented_inherited_pending`、理由与解锁路径逐字在册），两行仍为 maintained_pending。治理维持名单 6 → 5（余：tiaohou-qiongtong-v1、dayun-compose、dayun-timeline-view、bingyao-shenfeng-v1、siling-yin-pilot）。
3. **因此具备下一阶段条件的依赖**：三命方向与三命换算自此可经 chart 已注册 Phase2 步以 trace / RuleMatch / Evidence 形态产出，注册成立五条件满足前四项（原典在 Canonical、Phase1 规则已执行、Phase2 harness 真实验证、Golden 已登记），第五项（部署验收绑定）待关账批 E0347 以正式验收与部署记录终局核对。组合入口与研究视图继承的三命分段随之获得已注册上游；其神峰继承部分仍 pending，不因本批解锁。
4. **用户可见能力变化**：零。两新块恒 research 门控（engine 非 research 模式拒绝），公开投影对 `dayun_classical_direction` / `dayun_sanming_conversion` 两键整体剥离；默认（无门控输入）封套逐字不变；研究层视图仍不接公开页面。
5. **下一步确定前置**：父级按「先换位 live 快照 + cicd 钉、后合并」执行换代与合并，随后正式验收（部署管线对 Merge SHA）与部署完成即由 E0347 关账；队列下一批为神峰扩编（服务 bingyao-shenfeng-v1 与 dayun 神峰分段）与 tiaohou 设计审定批。

## 2 注册形态结论与分段审定

### 2.1 现行古典大运执行形态实测

- 本体为 `bazi_dayun_classical.py` 四个独立函数（`classical_direction`、`sanming_convert_elapsed`、`sanming_convert_measurement`、`shenfeng_convert_days`），共用 `_flags()` 披露 `evidence_binding='pending_phase1_rule_registration'` 并共用 LIMITATIONS（含注册状态句一条）；`validate_classical_direction` 断言该 binding 值且断言 `phase2_allowed=False`、`direction_rule_match=None`。批前唯一调用方是测试与 compose / view 两继承模块，chart() 不调用，产出不进 trace / RuleMatch / Evidence。
- 引文集 QUOTES 21 条：三命 15 条（卷二《论大运》11 条 + 卷十一 4 条）+ 神峰 6 条。方向输出的 evidence_quotes = direction_rule + vol11_direction_witness + 神峰 6 条；三命换算（elapsed）消费 6 条、measurement 级另消费 handover_decade / handover_approx；神峰换算消费 sf_ex1 / sf_ex3 / sf_ex4。15 条三命引文的 attributive 来源批前指 S0 登记来源（`bazi.source.sanmingtonghui`），无 Canonical 节可绑。
- 换算拒绝口径实测（均为返回 unresolved 结果、非抛异常）：三命 rounding 请求 reason 以 "rounding 'year' refused" 起并附 anti_rounding_quote；神峰零日 reason = `zero_day_count_not_exemplified_in_text`；elapsed 0 → unresolved + `zero_jie_boundary_convention_unreviewed`。

### 2.2 绑定形态定稿

沿批一/B-2/zaqi/ren 的 trace 接入先例定稿（trace 接入为唯一可注册形态）：

- chart() 签名尾追加门控 kwargs `dayun_classical_role=None`、`dayun_sanming_measurement=None`（函数头类型校验：role ∈ {male, female}、measurement 须 dict，违约先于任何计算抛 ValueError）；engine.execute 加两行 allow_research 门禁（非 research 模式传入任一门控字段即拒绝）；public_projection 对两新键整体剥离。
- role 给定 → `classical_direction(年柱, role)` 经 `validate_classical_direction` 后 `trace.add('bazi.phase2.dayun_classical_direction', …)`，块挂 `result['dayun_classical_direction']`；measurement 给定 → 先以声明内 `birth_month_ganzhi` 与已执行月柱交叉核对，再 `sanming_convert_measurement(measured)`（其内含 TJ-015 测量重放校验），两者并存时另做 direction 一致性核对，`trace.add('bazi.phase2.dayun_sanming_conversion', …)`，块挂 `result['dayun_sanming_conversion']`。交叉核对不符即拒绝，不产出半成品块。
- 披露分段翻转：`_flags(segment='sanming')` 使三命方向/换算输出 `evidence_binding='registered_phase1_phase2'`；神峰换算 `_flags('shenfeng')` 保持 `pending_phase1_rule_registration`；`validate_classical_direction` 的 binding 断言同步改 registered（两条过时断言文案更新、断言本身不变）；LIMITATIONS 两句更新（注册分段口径句 + 三命整书校勘状态句，三处 genuine 点改述为已经 E0346 阶段一校勘册逐处登记）。
- 引文改指：15 条三命引文 source 改指应用文本来源 `bazi.source.sanmingtonghui-applied` 并补 `source_section_id`（s068 × 11、s069 × 3、s070 × 1），引文文本逐字不动；两条 PUA 引文（handover_example / handover_decade）公开引文保留快照原字 + `mapped_reading_text`，Canonical 节绑定其 S3 应用形。公开 Golden 镜像 golden_tj0171 同步改指。
- 治理行分段注册（方案 c）：dayun-classical-variants 行翻 registered——主 `phase1_rule_id` / `phase2_rule_id` 记方向段（r038 / dayun_classical_direction），三命换算段以 `additional_phase1_rule_ids` / `additional_phase2_rule_ids` 补记（r039 / dayun_sanming_conversion），行内 `segments` 明细逐段标示（三命段 registered、神峰段 maintained_pending）。S5 治理不变量（全部 records 的 rules_added 并集与全部 registered 行的 rule id 集合恰等）的收集表达式同步扩展为并入 additional_* 字段——结构扩展、恰等不变量保留、注释明示。

### 2.3 神峰旁证不入 refs 审定

神峰 6 条引文**不入任何规则 source_refs**：其在方向输出中是 corroboration 披露而非三命裁定依据，沿 r035「只绑实际消费的裁定依据」与 zaqi 批例证不作规则引文两先例；且神峰段本身维持 pending、无 Canonical 节可绑。方向输出中神峰引文保持原样披露（来源 `bazi.source.shenfeng`、无 source_section_id），随神峰段 pending 在册明示。conversion-shenfeng 维持 pending，待神峰经典扩编批处理。

### 2.4 compose / view 改记口径

两模块 `_flags()` 的 evidence_binding 由 `pending_phase1_rule_registration` 改记 `segmented_inherited_pending`，各自 LIMITATIONS 与文档串同步改写为分段实情（继承的三命分段已注册、神峰分段仍 pending）。连带修复：view 的 `_sources` 原按 S0 来源过滤三命引文，引文改指后改按新常量 `SANMING_APPLIED_SOURCE_ID='bazi.source.sanmingtonghui-applied'` 过滤、两个三命引文块的 source_id 改记 applied；`_method_options` 的方法级出处登记保持 S0 来源不变。compose 无来源过滤、无需改。视图校验器不校验 binding 值、无需改校验。

## 3 第一阶段——《论大运》018 形制登记记录

- 登记册：`sanming-juan2-dayun-collation-register-v1`（新模块 `src/tianji_kb/bazi_sanming_juan2_dayun_collation.py`，纯数据、零函数），以 TJ-017.1 审定底稿（dayun-collation-register-v1）为基础逐条承接复核，既有登记逐字不动；双基线钉：S0 SHA256 `00e2a7db8bb59b259b99938033bb1bb77947e04a15dafc111e62b59378010c86`（461,157 字 / 1,342,659 字节 / blob `463c47cdde72c84ca6f1bd6d910a4f3fc1801f6a`）、S3 SHA256 `a89c0b5da16ea4e07dc85180c49135ed280875318059f923ff7154f2c217662f`（461,156 字 / 1,342,682 字节 / blob `f967400bfabeb09b627a747fa1b654de8a0c1970`），S0→S3 全程位移 −1。
- 登记两节：`sanming.juan2.lun_dayun`（S0 [58457, 59198) / S3 [58456, 59197)，741 字，首字为节题「论大运」）；`sanming.juan11.luoluozi_dayun_witness` 两 part——见证窗口 A（S0 [396898, 397159) / S3 [396897, 397158)，261 字，含方向见证 / 比率见证 / 计数分歧三引文）、见证窗口 B（S0 [408771, 408795) / S3 [408770, 408794)，24 字，恰为方向见证二引文本身）。
- 引文 16 条（前缀 `ldy.`：15 条消费/见证引文 + 闰月子句排除段）：13 条 verbatim（S0 原形逐字）；handover_example 与 handover_decade 以 applied_reading 在位（「行运算至」「从此算后十周年方换一运」——decade 引文 S0 原字为简体行文，S3 只换 PUA 一字、繁简逐字保留）。15 条引文逐条在 S3 定位点复现且包含于节文本，15/15。闰月排除段 S3 形与 S0 仅差 1 字（段内 U+ED92 → 算），整段排除不变、只登记不入任何引文消费。
- 节内校勘 10 条（前缀 `ldy-`）：PUA 4 处——59080 / 59123 / 59162（均 U+ED92，confirmed = 算，Q1；dayun 册 dy-pua-* 与密封 PUA 映射表 mappings[28] 双据）、397081（U+EA20，confirmed = 玄，Q1，位于窗口 A 正文、不在引文内）；防 3 处——58542（P2 处置册 seq 35、deferred_no_witness、上下文「薄者如蒿莱之防春风潜发亦能」，本册唯一未决项，不在任何引文内，随节元数据携带，先例同 s063 / s064）、397045 / 397047（S0 位点，S3 对应位点已应用为码位 U+3479 之字，位于窗口 A 正文、不在引文内；reading_status=contextual，只登记 S3 应用读法、不独立定字）；genuine 3 处——58834（日，worked_example 内）、58888（三，worked_example_check 内）、408791（岁，方向见证二引文内，传本异文并列），均 confirmed genuine、Q1。
- **阶段一硬门结论：通过。** 两节 S3 切片 PUA 0、□ 0；□ 命中节内关键引文 0 处；引文与 S3 不符 0 条；校勘未决项（仅 58542 一处）不落入任何消费引文。字形注记：码位 U+3479 之字在本批全部文档与台账中只写码位、不直接键入，以防形近异字混入。

## 4 密封著录明细

著录于私有检出（可信机受控环境），公开仓只保存本治理文档与公开代码披露，不含密封文本。

- 新章 2：`bazi.chapter.sanming_lun_dayun`、`bazi.chapter.sanming_luoluozi_dayun_witness`（经典条目无需改动：无 chapter_ids 清单、source_ids 已含应用文本来源）。
- 新节 3（均为 S3 切片、建节时 PUA / □ 归零核查通过）：s068 = 《论大运》741 字；s069 = 见证窗口 A 261 字；s070 = 见证窗口 B 24 字。
- 新术语 2：`bazi.term.dayun_direction`（供 r038）、`bazi.term.dayun_handover`（供 r039）。
- Phase1 规则 2：`bazi.rule.r038`「古典大运方向（三命通会）」source_refs **恰 2 条** = direction_rule（s068）+ vol11_direction_witness（s069）；`bazi.rule.r039`「三命大运换算」source_refs **恰 8 条** = ratio_statement、ratio_derivation、worked_example、anti_rounding、zero_borrow_definition、zero_borrow_example、handover_decade（以 S3 应用形绑定）、handover_approx（均 s068）。未入 refs 者各有明示地位：神峰 6 条为 corroboration 披露（§2.3）；worked_example_check、handover_example、vol11_ratio_witness、vol11_counting_divergence、方向见证二为登记证据（evidence-only），由阶段一校勘册承载；闰月子句排除段整段排除。
- Phase2 步 2（均 validated）：`bazi.phase2.dayun_classical_direction`（golden_case_ids = 下列 6 例全集）、`bazi.phase2.dayun_sanming_conversion`（golden_case_ids = 前 5 例）；回归测试 `tests/test_phase2_bazidayunsanming.py`。
- 密封 Golden +6 例（163 → 169），全部源为 golden_tj0174 既有 dayun 见证集的真实盘 / 真实时刻（measurement 由 `adjacent_jie_distance` 对真实出生时刻现生成，严禁手编干支）：`bazi.dayun-sanming-q1-1958-forward-male`（1958-08-15T19:30:00+08:00，戊戌 / 庚申 / 甲子 / 甲戌，male，forward，区间 [2840, 2850)）、`q2-1949-backward-female`（1949-01-04T09:30:00+08:00，戊子 / 甲子 / 甲午 / 己巳，female，backward，[3340, 3350)）、`q3-1959-forward-female`（己亥 / 庚午 / 戊辰 / 丁巳，female，forward，[2730, 2740)）、`q4-1959-backward-male`（同 Q3 盘，male，backward，[1030, 1040)）、`adv001-zero-jie-2000`（2000-02-04T20:40:24+08:00，庚辰 / 戊寅 / 壬辰 / 庚戌，female，backward，elapsed 0 → unresolved、duration None，恰逢节拒绝口径在已注册步内复现）、`direction-only-1959-male`（同 Q3 盘，male，无 measurement，只方向步 fire）。
- 计数迁移：Canonical 章 27 → 29、节 67 → 70、术语 34 → 36、Phase1 规则 37 → 39、Phase2 步 38 → 40、密封 Golden 163 → 169；既有密封套件计数钉同步迁移（sections / chapters / terms / rules / contract 步 / Golden 总数与治理维持名单 6 → 5，涉及 test_phase2_baziganzhi / baziluren / bazizaiqi / bazirenyin / bazisanxing 五文件，逐处带 E0346 注记）。coverage 两件在组装树内以官方生成器重生后回填私有检出；公开侧 docs/COVERAGE.md 的 bazi 行同步更新（节 67 → 70、术语 34 → 36、章节分项 25/11/1 → 27/11/1）。

## 5 等价比对（封闭清单与结果）

比对集（捕获为整封套规范 JSON；基线 = main `16459af1` + live 快照组装，工作侧 = 本批代码 + 暂存快照组装）：direction_exhaustive 240（60 干支 × 2 角色全穷举）、conversion_elapsed 43、conversion_shenfeng 17、conversion_measurement 70、compose 12、timeline_view 6、adversarial 19（ADV-001..012 及其变体）、golden_envelopes 163（基线密封 Golden 全集）。

封闭清单（清单外零差异；dayun 各段共 2,318 处叶级差异全部落入下列 7 类）：

1. 引文 ref `source_id` 改指应用文本来源 ×751（引文 ref 746 + view 三命引文块级 source_id 5）；
2. KEY_ADDED `source_section_id` ×746（仅三命引文 ref，神峰引文不加）；
3. LIMITATIONS 三命整书校勘状态句改写 ×267；
4. LIMITATIONS 注册分段口径句改写 ×267；
5. `evidence_binding` pending → registered（三命段）×260；
6. `evidence_binding` pending → segmented_inherited_pending（compose / view）×15；
7. compose LIMITATIONS 注册句改写 ×12。

结果：163 个基线 Golden 封套**零差异**；工作侧捕获恰多 6 个新例键（新 Golden 6 例）；**所有计算值（方向、区间端点、交运时刻、状态、reason）零差异**，差异全部为注册披露类。输出契约逐项复核：区间不变、无单点字段、无年龄键、恰逢节拒绝口径不变。

## 6 伪造负例与回滚演练

- 伪造引文负例（密封专项测试内直测 EvidenceResolver）：方向句改一字（阳男 → 阳安）、方向句错绑 s069（文本不在该节）、handover_decade 以 S0 PUA 原形绑定（与 Canonical 节应用形不符）、引文错配 S0 来源——四例均被 `EvidenceResolver.resolve(rule_id, variant)` 拒绝。
- 回滚演练：新代码 + 旧快照（manifest `2fdcfaec…`）组装——门控 direction 路径以 `ValueError: Unknown rule: bazi.phase2.dayun_classical_direction` fail-closed、门控 conversion 路径以 `Unknown rule: bazi.phase2.dayun_sanming_conversion` fail-closed；163 个默认封套与基线逐字一致。

## 7 实施记录与换代清单

- 机上全配方复跑（`scripts/accept_offline.py --suite all`，分支代码 + 暂存快照，trusted-manifest 钉暂存值）：public-git-checkout 15、public-only 24（skipped 1）、private-backend 2748，**合计 2787，failures 与 errors 均为 0**。对账：正式基线 2742（15 + 24 / 2703，skipped 1）+ 本批增量 45（新公开专项 test_tj0183_e0346_dayun_sanming_collation 16 测 + test_governance_dayun_sanming_promotion_public 11 测 + 新密封专项 test_phase2_bazidayunsanming 12 测 + test_tj0183_e0346_dayun_sanming_collation_sealed 6 测，全部入 backend 分区）= 2787，逐项对平。
- 密封交付三元组：文件 237 → 237；字节 16,170,283 → 16,221,036；manifest SHA256 `2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6` → `97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324`。
- 变更文件（恰 5 件）与 after SHA256：
  - data/canonical/bazi/phase1_knowledge.json — 09208b963ff527e4aa0255e2e48e90e4fb49cfcd685b6cfd28c4ced5e1fd9f3d
  - data/canonical/bazi/phase2_execution.json — cab21f4d41a4b76c2d4f061fd791e409eb81d95967cfc6f79ec29044c0b426f6
  - data/canonical/bazi/phase2_golden.json — bd750ba860a5e4651b38809258226fa2a43acb8ea295871db00e452573551c31
  - data/coverage/phase1.json — 13e75db1102f84fa212988a27fdad43d15bf29133b83c2d1829cc3512fc7b87d
  - data/product/knowledge_coverage.json — a60343d43d5f2e62bbbc37bb3f12f1b2b6f4d06fc15198a537864ef5c092492d
- 私有检出同步：scripts/import_public_snapshot.py 的 EXPECTED_FILES=237、EXPECTED_BYTES 已由 16170283 改为 16221036，检出根 manifest 按其实存结构重生并以全新盘点逐行核对，verify 通过（237 文件 / 16,221,036 字节）。
- 暂存快照位置：机上 `/data/workspace/dayun-sm/staged`（verify 通过）。**live 快照与 cicd 钉未动**。
- 既有公开测试的批转折更新（1 处，非放宽）：TJ-017.1 公开测试 `test_variants_not_wired_into_production_paths` 的全域隔离断言（三生产路径均不得引用古典模块）与本批审定的三命分段门控接入形态冲突，已按批转折改写为钉住接入的精确形状——engine 与 public_projection 仍不得出现模块名 / Variant id / handover 内部键，bazi_chart 只许 import 恰一次、不得硬编码 Variant id、不得触 handover 内部、只接两条已注册三命步且不得接入神峰换算函数；断言总数不变、判定力不减（改写后本地与机上复跑均通过）。全仓同型断言排查无其他残留。
- 计数钉迁移的完整清单（首轮全配方复跑暴露并补齐，非改判定语义）：除 §4 所列五件 Phase2 密封套件外，另有四处随本批计数迁移——test_phase1_bazi 的可执行规则例外集补 r038 / r039；合化事实层 SEALED_MEASUREMENTS 三总数（节 67 → 70、Phase1 规则 37 → 39、Phase2 规则 38 → 40，逐批注释链续写 E0346 条目，新三节经实测不含合化关键词与「五合」、关键词钉不变）及其公开 golden 镜像同步；test_tj0183_p1_sanxing_promotion_sealed 的章 / 节 / 术语 / 规则与 Phase2 步计数（27 → 29、67 → 70、34 → 36、37 → 39、38 → 40，注释链续写）；test_tj0171_dayun_classical_sealed 的逐字核验改按双文本口径（15 条三命引文在 S0 原文于原登记坐标逐字核验不变，另在 S3 应用文本于 E0346 校勘册 S3 坐标逐字核验其绑定形：verbatim 13 条与公开引文一致、applied_reading 2 条与 mapped_reading_text 一致）。首轮复跑该四处共 6 失败 + 1 错误，补齐后定向复跑全过、终局全配方复跑 0 失败（见上）。
- 换代清单（父级合并前先行）：(1) 备份 live 快照至 secure/tianji-knowledge-pre-dayun-sanming-backup；(2) 以暂存快照换入 live，`diff -r --brief` 逐字核对；(3) cicd 钉 TRUSTED_MANIFEST_SHA256 改为 `97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324`；(4) 再合并本 PR；(5) 合并后直读部署管线对 Merge SHA 的正式验收与 DEPLOYED pin，关账 E0347。

## 8 仍未判断与后续

- 神峰分段仍未注册：神峰方向旁证与神峰换算（conversion-shenfeng）维持 pending，待神峰经典扩编批建节后另行绑定；bingyao-shenfeng-v1 与之同源、同批处理。
- tiaohou-qiongtong-v1 维持 pending：需设计审定批先行（缺 Canonical 构造、非文本缺口）。
- siling-yin-pilot 维持 pending：扩月与「连续 24 小时计日」约定转正仍待用户裁定，本批未代决、未外推。
- TJ-017.2（原局＋大运＋流年跨规则调用）仍阻塞于 M2（扶抑 / 格局用神未建；U1/U3 用户暂缓），本批未触及、未混入。
- 《论大运》节内唯一未决校勘点（残余防 S0 58542，deferred_no_witness）随节元数据保留，不影响任何消费引文；三命整书 canonical_ready 仍为 false，只走逐节晋级。
- TJ-018.2 保持阻塞、TJ-018.3 保持待做；注册成立第五条件（部署验收绑定）待 E0347 关账终局核对。

## 9 关账记录（E0347，append-only 补记）

- 实施批与合并：公开 PR #523 已合并，Merge SHA `7a652969b7e5a08a528597f437b98b058a249b44`（基线 main `16459af1`）；本关账批为纯台账与文档批，不动代码与密封资产，未做机上复跑——所记验收与部署事实为父级直读的管线正式记录，关账批开工三核实（main HEAD、台账末号 E0346、本节 §8 后续表述）全符。
- 正式验收终局核对（直读管线 `acceptance-7a652969b7e5a08a528597f437b98b058a249b44` 记录）：result SUCCESS，public-git-checkout 15、public-only 24（skipped 1）、private-backend 2748，合计 2787 测，failures 与 errors 均为 0；快照 237 文件、16,221,036 字节、manifest `97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324`，与实施批复跑 2787 逐项对平。
- 部署终局核对：deploys.log 记录 `7a652969` 于 2026-10-31T19:17:53Z DEPLOYED，pin `f702c2f44a5f9bda6cc75bbfb4f36c26e6237209dc7fd3bfce81f093401ebb76`（health 与 bazi 探针 ok）。
- 换代实际执行记录：父级合并前先行执行——旧快照备份于 `secure/tianji-knowledge-pre-dayun-sanming-backup`（manifest `2fdcfaec…`），live 快照由暂存快照（/data/workspace/dayun-sm/staged）换入且 diff -r 逐字一致，cicd 钉 `TRUSTED_MANIFEST_SHA256` 由 `2fdcfaec…` 改为 `97e211c4…`；换代 before 为 237 文件、16,170,283 字节、manifest `2fdcfaec…`，after 为 237 文件、16,221,036 字节、manifest `97e211c4…`。
- 机上清理记录：关账批已删除 /data/workspace/dayun-sm 下组装树（asm2、asm-base、asm-final、asm-rollback、asm-work、pub-base、pub-final、pub-work、stage-root）、暂存快照 staged、捕获文件（capture-after.json、capture-baseline.json、capture-rollback.json）、传输 bundle 三件（e0346.bundle、e0346-delta.bundle、e0346-delta2.bundle）与 tmp 临时库文件；日志（backend-v.log、combined.log、final-accept*.log）与脚本保留；清理前后 live manifest 复核仍为 `97e211c4…`、备份目录完好，/data 已用 71% 降至 67%。
- 注册成立第五条件（部署验收绑定）终局核对完成，分段注册翻转已随合并生效——dayun-classical-variants 三命段 registered、神峰段维持 maintained_pending 在册（待神峰经典扩编批），dayun-compose 与 dayun-timeline-view 为 segmented_inherited_pending，治理维持名单 6 降至 5；输出契约守恒——只有区间、无单点字段、无年龄键、恰逢节拒绝口径与 ADV-001 至 012 行为逐字不变、研究视图不接公开页面，用户可见能力零变化；dayun 三命分段晋级全链闭合，TJ-018.2 保持阻塞、TJ-018.3 保持待做。队列下一批：神峰经典扩编（一次服务 bingyao-shenfeng-v1 与 dayun 神峰分段）与 tiaohou 设计审定批。
