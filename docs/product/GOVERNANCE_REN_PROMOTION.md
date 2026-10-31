# GOVERNANCE_REN_PROMOTION — ren-pattern-yin-true-v1 执行绑定与注册晋级（E0344）

治理 pending 8 项审计（E0341，docs/product/GOVERNANCE_PENDING8_AUDIT.md）§2.7 推荐第二批：把 Slice D-1 任氏寅月真格 determination 从「独立组合函数在 ExecutionTrace 之外产出」绑定为已注册的 Phase1 规则 + Phase2 执行步 + 密封 Golden 三件套，并翻转治理登记。本批基线 main `3400b6a02c4cc280e3da6854304d723de3d1e16c`、台账 343 事件、密封钉 `6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0`。

## 0 授权与范围

- 授权来源：治理 pending-8 审计 §2.7 定 ren-pattern-yin-true-v1 为零材料缺口、纯 `execution_binding_structure` 缺口，列为现在可执行的第二顺位；其 unlock_path 写明「determination 接入 trace 步（显式试点结果作为已执行输入）并扩 golden 输入契约后，再行注册」——本批按该路径执行。
- 不可动摇的语义边界：`true_false ∈ {true, commander_not_visible, abstained}` 三态、永不输出「假格」、破格/成败/清浊/用神恒 None + unreviewed；父级裁定 D1（commander_not_visible 保守读法）与 D2（日干不计入透干）逐字不变；Slice A 禄刃路线优先序不变；legacy determination 字段逐字不变。
- 明确不在本批范围：不扩月（司令仍仅寅月；siling-yin-pilot 登记维持 pending、待用户裁定）；不触扶抑 U1/U3；不改 D-1 语义与 D1/D2 裁定；不削弱 golden harness 的 provider 钉死；公开侧不接场景、不开放（块恒 research_only，公开投影整体剥离）。

## 1 五问答复

1. **实际建立的 Canonical 实体**：无新节、无新章——D-1 的三条原典锚点（真格定义 bazi.section.s053、任氏程序 bazi.section.s054、寅月分段 bazi.section.s024）均已在 Canonical 在位，本批只建注册实体：新术语 `bazi.term.ren_true_pattern`、Phase1 规则 `bazi.rule.r037`、Phase2 步 `bazi.phase2.ren_yin_true_pattern`。Phase1 实体总数 1097 → 1099。
2. **真实解除的 pending**：ren-pattern-yin-true-v1 由 maintained_pending / execution_binding_structure 翻转为 registered；治理维持名单 7 → 6（余：tiaohou-qiongtong-v1、dayun-classical-variants、dayun-compose、dayun-timeline-view、bingyao-shenfeng-v1、siling-yin-pilot）。
3. **因此具备下一阶段条件的依赖**：D-1 determination 自此经已注册 Phase2 步与 EvidenceResolver 证据链产生（trace / RuleMatch / Evidence 三面齐备），注册成立五条件满足前四项（原典在 Canonical、Phase1 规则已执行、Phase2 harness 真实验证、Golden 已登记），第五项（部署验收绑定）待关账批 E0345 以正式验收与部署记录终局核对。注意：本批不改变 siling-yin-pilot 的 pending 状态，司令扩月与约定转正仍待用户裁定，不因本批解锁。
4. **用户可见能力变化**：零。块恒 research_only、public_enabled=false、ai_enabled=false，公开投影对 pattern_determination_ren_yin 键整体剥离；默认（无门控输入）封套逐字不变。
5. **下一步确定前置**：父级按「先换位 live 快照 + cicd 钉、后合并」执行换代与合并，随后正式验收（部署管线对 Merge SHA）与部署完成即由 E0345 关账；队列下一批为 dayun 三命分段（先《论大运》018 形制登记、后建节分段翻转）。

## 2 注册形态结论与 harness 输入契约扩展

### 2.1 现行 D-1 执行形态实测

- determination 本体为 `bazi_pattern.ren_yin_true_pattern(trace, pilot_result)`：消费已执行事实（pillars / ten_gods / hidden_stems / hidden_to_visible / pattern_route 步输出）与显式传入的司令试点结果；判定序 D3 = 月支域门（寅）→ 禄刃路线优先序 → 试点 computed → 司令透干核对。
- 试点信任界 D6 在组合函数内：`_ren_yin_pilot_claim` 做身份钉验证（Variant 名 `bazi-siling-yin-pilot-v1`、计算约定 id/version、version_id、s024 来源节、research 旗标）与已执行事实交叉核对（司令须为月支藏干；hidden_to_visible 与 ten_gods 两面事实一致），不可验证的声明只能弃判。
- 批前状态：组合函数的唯一调用方是测试；chart() 不调用它，块不经任何已注册 Phase2 步产生，`evidence_binding` 为 `pending_phase1_rule_registration`，不进 RuleMatch 与 Evidence。
- 结构事实（审定 D4）：chart() 不携带出生瞬时与 jie 声明，试点不能在 chart 内调用——故「试点结果显式传入」不是临时形态而是契约本身；缺口只在该显式输入未被 harness 契约与 trace 接入承接。

### 2.2 绑定形态定稿

沿批一/B-2/zaqi 的 trace 接入先例定稿（批一结论：trace 接入为唯一可注册形态）：

- chart() 新增 keyword-only 门控参数 `ren_yin_pilot_result=None`（置于 include_punishment_facts 之后）；非 None 且非 dict → ValueError（先于任何计算）。
- engine.execute 新增一行门禁：bazi 域传入 `ren_yin_pilot_result` 且非 allow_research → ValueError（措辞 'Ren yin true-pattern determination requires explicit research mode'，与既有门禁行同形）。
- pattern 块内、zaqi 步之后：参数非 None 时调用既有组合函数并 `trace.add('bazi.phase2.ren_yin_true_pattern', {'pattern_variant': ..., 'pilot_variant': ...}, block)`，块以 `pattern_determination_ren_yin` 键挂 result；production_scope 的研究口径追加句仅在门控开启时出现。参数为 None 时封套逐字不变（§4 Set A/C 与 §5 回滚实测）。
- 组合函数本体、D6 信任界、三态语义零改动；chart 不调用试点、不生成试点结果，D4 的「试点结果恒为显式输入」保持为真，仅原「不附 chart、不新增 trace rule」一句随注册落地改写（代码注记 D4 与治理文档本节即其登记）。

### 2.3 harness 输入契约扩展（最小扩展）

- 缺口精确定位：`golden.py run_cases` 对每例以 `function(**case['input'])` 执行 provider，并做 provider 三重钉死（domain == 目录名、provider == PROVIDERS[domain]、provider == contract.provider，且须 `tianji_kb.operations.` 前缀）；批前 provider `operations.bazi_chart.chart` 的输入不含试点结果，D-1 所需的显式输入通道不存在。
- 扩展方案：`golden.py`、`validate_phase2.py`、golden schema（`schemas/knowledge/phase2-golden.schema.json`，其对 input 只有 `{"type": "object"}`、无键限制）**零改动**，provider 三重钉死逐字不变；扩展只落两处——provider 签名新增门控 kwarg（默认 None 时行为逐字不变）与用例 input 增带 `ren_yin_pilot_result` 字段。
- 旧契约行为不变的钉法（专项测试）：公开测试断言无参数时封套无 ren 键、trace 无新步、engine 门禁拒绝、kwarg 类型拒绝、golden.py 钉死断言串（provider 三重比较与 operations 前缀）在位；密封测试 `test_old_contract_unchanged_without_gated_input` 以新 Golden 用例的同盘输入去门控后直测无 ren 键、无新步。

## 3 密封著录明细

著录于私有检出（可信机受控环境），公开仓只保存本治理文档与公开代码披露，不含密封文本。

- 术语 `bazi.term.ren_true_pattern`「任氏真格」：definition_kind=classical_excerpt；source_refs = [s053 定义句]；related_terms = [bazi.term.month_commander, bazi.term.official_pattern_candidates, bazi.term.resource_pattern_candidates]；confidence=medium。
- Phase1 规则 `bazi.rule.r037`「任氏寅月真格裁定（滴天髓原注＋任氏曰）」：execution_status=executable；school=子平·滴天髓阐微任氏分支（原注定义＋任氏曰程序）；variant=ziping-structural-v1；operation.kind=evidence_bound_true_pattern_determination，provider=tianji_kb.operations.bazi_chart.chart，parameters 含 pattern_variant 与 ren_yin_pilot_result 显式输入声明；term_refs=[bazi.term.ren_true_pattern]。
  - **source_refs 恰 3 条**（子集定稿沿 r031/r035/r036 先例：只含 determination 实际消费的裁定依据）：s053 原注定义句（节全文 37 字 = 引文 renshi.zhenge_definition 本身）、s054 任氏曰程序句（节全文 92 字 = 引文 renshi.siling_true_false_procedure 本身）、s024 寅月分段句（节全文 45 字，三命分段原文）；source_id 均 bazi.source.ditiansui-spouse、role 均 classical。两例证类材料不入 refs（本批无例证引用；15 例 Golden 即执行见证）。
- Phase2 步 `bazi.phase2.ren_yin_true_pattern`「任氏寅月真格裁定步」：phase1_rule_refs=[bazi.rule.r037]；validation_status=validated；golden_case_ids = 下列 15 例；regression_test=tests/test_phase2_bazirenyin.py；evidence_scope 为 C 级研究口径（只登记寅月真格裁定、不外推、公开投影剥离）。
- 密封 Golden +15 例（148 → 163），id 为 `bazi.ren-yin-true-<公开用例 id>`：t1-wu-zhengcai、n1-touchstone、t2-bing-qisha、f1-boundary-minus-1s、f2-boundary-exact、t3-jia-pianyin、t4-jia-shishen、s3-route-precedence、a1-wu-daymaster-neg、a2-wu-daymaster-pos、a3-bing-daymaster-neg、a4-bing-daymaster-pos、n2-jia-not-visible-2025、s1-non-yin、s2-pilot-uncertain。全部源为 Slice D-1 既有见证真实盘（含试金石 2024-02-06 庚日主戊段 → commander_not_visible、段界 ±1 秒翻转对 f1/f2、甲×寅路线让位 abstained 的 s3、D2 四件 a1–a4、2025 年窗 n2、非寅月 s1、试点 uncertain 的 s2）；input = 四干支 + pattern_variant + ren_yin_pilot_result（试点块由真实 pilot 以真实出生瞬时与钉定交节窗口生成，逐例与公开 Golden 的 pilot_expectation 核对一致：status / commander / segment index / reason）；expected = 对 pattern_determination_ren_yin 块的子集断言（status / decision_step / abstention_reason / determination{status, pattern, true_false, success_failure=None, purity=None, useful_god=None} / evidence_binding=registered_phase1_phase2 / commander{stem, ten_god, visible_pillars}），由基线组合函数产块导出并与公开 Golden 期望逐字段交叉核对一致后钉定。
- 计数迁移：Canonical 节 67 → 67（不变）、章 27 → 27（不变）、术语 33 → 34、Phase1 规则 36 → 37、Phase2 步 37 → 38、密封 Golden 148 → 163；Phase1 实体 1097 → 1099；Phase2 全域口径：执行步 74 → 75、validated 73 → 74、Golden 总数 176 → 191。合化事实层密封计数钉同步迁移（phase1_rules_total 36 → 37、phase2_rules_total 37 → 38、sections 67 不变，r037 与新步均不含合化内容，由合化密封测试全节扫描复核）。

## 4 等价比对（封闭清单与结果）

比对集（捕获为整封套规范 JSON）：

- **Set A**：密封 Golden 全部用例原输入（基线 148 例；工作侧 163 例）。
- **Set B**：D-1 见证 15 盘——基线侧 = 旧代码封套（pattern_variant，无试点输入）+ 独立组合函数产块；工作侧 = 新代码门控 chart 封套（块在封套内）。
- **Set C**：密封 Golden 全部用例强制 pattern_variant（基线 148 例；工作侧 163 例）。

封闭清单（清单外零差异；归一化只许下列七项）：

1. 新增 trace 步 `bazi.phase2.ren_yin_true_pattern` 及其 step 条目；
2. 新增 rule_matches 中该步的条目；
3. 新增 evidence 中 rule_id 为该步的条目；
4. result 新增键 `pattern_determination_ren_yin`（仅 Set B 工作侧与新 Golden 用例）；
5. 块内 `evidence_binding` 值 pending_phase1_rule_registration → registered_phase1_phase2；
6. 块内注册披露句成对归一：adjudication_notes 的 D4 落地形态句、scope_limits 的注册状态句（双侧均为注册/落地形态句时归一为同一标记）；
7. 门控开启时 production_scope 尾部追加的研究口径句（仅 Set B 工作侧）。

结果：基线捕获 311 键（A 148 + B 15 + C 148）、工作捕获 341 键（A 163 + B 15 + C 163）；工作侧多出恰 30 键 = 15 例新 Golden 于 A/C 两集各一份；基线独有键 0；**共有键经封闭清单归一化后逐字段全等，清单外差异 0**。Set B 另证：门控封套去掉清单 1–4、7 项后与基线封套逐字全等，门控产块与独立组合函数产块在清单 5、6 项外逐字全等（密封专项测试另以试金石/正例/路线让位三盘直测两路产块逐字相等）。determination 语义零变化。

## 5 伪造负例与回滚演练

- 伪造引文负例（密封专项测试内直测 EvidenceResolver）：定义句改一字、程序句错绑 s053（文本不在该节）、分段句改一字、定义句错配来源（bazi.source.sanmingtonghui）——四例均被 resolver 拒绝（ValueError）。
- 回滚演练：新代码（分支 e8d5bb83）+ 旧快照（manifest 6edcebc6）组装——门控路径以 `ValueError: Unknown rule: bazi.phase2.ren_yin_true_pattern` fail-closed；默认面（无 pattern_variant）与 pattern-only 面（试金石盘）与基线组装（旧代码 + 旧快照）逐字一致。旧代码对门控 kwarg 为 TypeError（契约新增的预期形态）。

## 6 实施记录与换代清单

- 机上全配方复跑（`scripts/accept_offline.py --suite all`，分支代码 + 暂存快照，trusted-manifest 钉暂存值）：public-git-checkout 15、public-only 24（skipped 1）、private-backend 2703，**合计 2742，failures 与 errors 均为 0**。对账：正式基线 2724（15 + 24 / 2685，skipped 1）+ 本批增量 18（新公开专项 test_governance_ren_promotion_public 10 测 + 新密封专项 test_phase2_bazirenyin 8 测）= 2742，逐项对平；分区模块 242 → 244（+2 新测试文件，均入 backend 分区）。
- 密封交付三元组：文件 237 → 237；字节 16,072,121 → 16,170,283；manifest SHA256 `6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0` → `2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6`。
- 变更文件（恰 5 件）与 after SHA256：
  - data/canonical/bazi/phase1_knowledge.json — 7fb6b8ad23a871e5b8e4e0a52d972ad2254f3ef8a59773562ffe81c2b478f18e
  - data/canonical/bazi/phase2_execution.json — 449d5c8e6a8cf2d04f443bea00d68770103d84655119bda86bd3a8c18cce7bd7
  - data/canonical/bazi/phase2_golden.json — 393f53dc566ab37455964e5f3b761f4293295d20e3d4598b7cd085db29480050
  - data/coverage/phase1.json — 2a35ef718aab2505d867565c0ddd2a7d68abb3c62a63fed9243039dfa19982dd
  - data/product/knowledge_coverage.json — 241820ed62d7ff3ed92e9e7fc05d0189edce3e36a8a14b70d93bb8bc6f1803e3
  （coverage 两件为组装树内以官方生成器 build_phase1_coverage.py / build_product_coverage.py 重生后回填私有检出；公开侧 docs/COVERAGE.md 的 bazi 行同步更新：术语 33 → 34、规则口径 24/11/1 → 25/11/1。）
- 私有检出同步：scripts/import_public_snapshot.py 的 EXPECTED_FILES=237、EXPECTED_BYTES=16170283 已同步，检出根 manifest 以脚本自身 inventory()/manifest_for() 重生，verify 通过（237 文件 / 16,170,283 字节）。
- 暂存快照位置：机上 `/data/workspace/ren/staged`（verify 通过）。**live 快照与 cicd 钉未动**。
- 换代清单（父级合并前先行）：(1) 备份 live 快照至 secure/tianji-knowledge-pre-ren-backup；(2) 以暂存快照换入 live，`diff -r --brief` 逐字核对；(3) cicd 钉 TRUSTED_MANIFEST_SHA256 改为 `2fdcfaec3ffd5f3ac5e991cb0da591df5dda57c3583bba4e431e7c098b4036b6`；(4) 再合并本 PR；(5) 合并后直读部署管线对 Merge SHA 的正式验收与 DEPLOYED pin，关账 E0345。

## 7 实施前复核

- 开工三核实（2026-10-31）：API main HEAD = `3400b6a02c4cc280e3da6854304d723de3d1e16c` ✓；TASK_HISTORY 343 事件、末号 E0343 ✓；机上 cicd 钉 = `6edcebc6…` 且 live 快照 manifest 与之逐字一致 ✓；SSH known_hosts 指纹与在册一致 ✓。
- ID 空闲核查：Phase1 规则现行最大 r036 → 新规 r037 空闲；Phase2 步现行 37 条全量核查，`bazi.phase2.ren_yin_true_pattern` 未占用；术语 `bazi.term.ren_true_pattern` 未占用；新 Golden 15 个 id 与现行 148 例无冲突。
- 审计 §2.7 复核：组合函数签名、D6 信任界位置、harness 三重钉死与 `**case['input']` 契约、golden schema 对 input 无键限制，均以源码实测复核，与审计结论一致；审计所称「可能超出契约」的输入（出生瞬时/交节数据）经定稿不入 harness——入 harness 的只有已生成的试点结果块本身，出生瞬时与交节声明仍留在试点调用侧（§2.3）。
- 试点块生成复核：15 例试点块由公开代码真实 pilot 生成（真实出生瞬时 + 公开 Golden 钉定的 provider 与 2023/2024/2025 交节窗口），逐例与公开 Golden 的 pilot_expectation 一致；四柱经历法路径重算与公开 Golden 钉定四柱逐例一致。

## 8 仍未判断与后续

- D-1 判定面不变：真格三态之外，破格/成败/清浊/用神仍未审；正格成格、官杀去留、从化象等 determination 仍为 None（审源结论不变）。
- siling-yin-pilot 维持 pending：扩月（寅月以外月份）与「连续 24 小时计日」约定转正仍待用户裁定，本批未代决、未外推。
- TJ-012.3 仍阻塞（格局真假体系未全建）；TJ-018.2 保持阻塞、TJ-018.3 保持待做。
- 注册成立第五条件（部署验收绑定）待 E0345 关账终局核对；队列下一批：dayun 三命分段。
