# GOVERNANCE_SHENFENG_EXPANSION — 神峰经典 Canonical 扩编（E0348）

治理 pending 队列「缺 Canonical 建制」类第一批：一次扩编同时服务 bingyao-shenfeng-v1 与 dayun-classical-variants 神峰分段。密封 Canonical 新建《神峰通考》经典、既有滴天髓经典内补中和篇制衡窗口节；bingyao 注册 Phase1 规则 bazi.rule.r040 / Phase2 步 bazi.phase2.bingyao_assessment，dayun 神峰分段注册 Phase1 规则 bazi.rule.r041 / Phase2 步 bazi.phase2.dayun_shenfeng_conversion；dayun-compose / dayun-timeline-view 两 inherited 行改记终局形态。基线：公开 main `6b64dc1dc1a6dd0f83475dbe6d4a14b55350eb7a`、台账 347 事件、密封钉 237 文件 / 16,221,036 字节 / manifest `97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324`、正式验收 SUCCESS 2787。

## 0 授权与范围

授权链：治理 pending 8 项审计（E0341，`docs/product/GOVERNANCE_PENDING8_AUDIT.md`）将 8 项维持 pending 分为三类，其中「缺 Canonical 建制（非缺原文）」类含 bingyao-shenfeng-v1（§2.5）与 dayun 神峰分段（§2.2 行内 segments），并明示「一次神峰扩编同时服务两项」；dayun 三命分段批（E0346，`docs/product/GOVERNANCE_DAYUN_SANMING_PROMOTION.md`）§2.3 审定神峰 6 条在方向输出中只作 corroboration 披露、不入任何规则 refs，神峰换算维持 pending 待神峰经典扩编——本批即该扩编。注册形态沿批一/B-2/zaqi/ren/dayun 的 trace 接入先例（门控 kwargs + trace.add + RuleMatch/Evidence，harness 契约最小扩展）。

本批范围：新经典建制、四节建节、两术语、两规则、两步、11 例密封 Golden、两条执行路径改经注册步、治理三行翻转/改记与两行 inherited 终局改记。**语义边界逐字不变**：bingyao determination 恒 None、无「无病」输出、双对结构与审定点 S1–S4 不变；dayun 输出契约（只有区间、无单点字段、无年龄键、恰逢节拒绝、ADV-001..012 行为）不变；用户可见能力变化为零；不触扶抑 U1/U3；不混入 TJ-017.2（仍阻塞）；不连带处理 tiaohou（其经典建制另行设计审定批）。

引用口径说明：任务书转述审计结论时所引章节号（§2.4/§2.6）与神峰病药节坐标（parts [3863,6214)、11 条引文）与现行文档/模块实测不符——审计文档实际编号为 §2.5（bingyao）与 §2.2（dayun 行），病药消费子集以 bazi_bingyao 模块实测为准（定义节 [7019,7680)、登记引文 9 条，见 §2.1）。按任务书第 2 条「消费子集实测」口径，本批以模块实测为准据实建节，并在本节留痕。

## 1 五问答复

（1）真正补齐的专业判断是什么？——无新增判断。补齐的是两个既有 Variant 的证据注册：《神峰通考》此前根本不在密封 Canonical 四经典内，病药 9 条引文与神峰大运 6 条引文 0 条可在 Canonical 验证、两个 Variant 的 evidence_binding 均为 pending；本批新建神峰经典并建节绑定，使病药结构候选（TJ-013 已审定、已在研究路径输出）与神峰日级换算（TJ-017.1 已审定）成为可由 EvidenceResolver 逐条复核、由 ExecutionTrace 留痕、由密封 Golden 真实 fire 的注册产出。bingyao determination 仍恒 None，dayun 仍只出区间。

（2）引文如何绑定到 Canonical 节？——按消费子集定建节范围（§2.1/§2.3）：神峰病药定义节整段建节 s071（快照字符 [7019,7680)、661 字，含登记引文 7 条）；正官格张力句以窗口节 s072 承载（[10010,10041) 恰幅）；《起大运法》整节建节 s073（[85001,85246)、245 字，含神峰 6 条）；滴天髓制衡句在既有滴天髓经典内补窗口节 s074（[43767,43825) 恰幅）。公开登记侧：bingyao 9 条引文补 section_id（source 不变）；dayun 神峰 6 条补 source_section_id=s073（source 不改指——神峰无 S0/S3 双轨，隔离快照即登记原文，沿 E0346 映射机制扩展）。

（3）Phase1/Phase2 注册形态？——新规则 r040（source_refs 恰为病药实际编码消费的 4 条：病/药定义句 + 两条编码对句）与 r041（source_refs 恰为神峰换算实际消费的 3 条例算 sf_ex1/sf_ex3/sf_ex4）；新术语 bazi.term.bingyao、bazi.term.dayun_shenfeng_conversion；新 Phase2 步 bazi.phase2.bingyao_assessment（validated，6 例 Golden 真实 fire）与 bazi.phase2.dayun_shenfeng_conversion（validated，5 例 Golden 真实 fire）。未入 refs 者各有明示地位（§2.4）：登记引文入节不入 refs（沿 E0342 例证先例）、制衡引文只作 limitations 证据（沿 E0346 §2.3 旁证审定）、方向 corroboration 引文不入任何规则 refs。

（4）翻转前后等价如何证明？——比对集与封闭清单见 §5：13 个捕获集（bingyao 查证明证 13 盘 + 冲突/可读组合封套、dayun 方向 60 干支×2 角色全穷举、elapsed 扫描、神峰日数 0–40×双向、五测量对象、组合 12 例 + 神峰并列组合、双方法视图、密封 Golden 全集封套）翻转前后逐叶比对，实测 1,759 处叶级差异全数落入封闭清单五类、清单外 0、计算值差异 0、无 REMOVED。

（5）仍未判断的范围？——见 §8：病药裁定（determination、去病效力、「无病」）仍不可判断；神峰其余诸节（四病四药、格论诸节）未建节、未注册；dayun 神峰分段以外的神峰消费（如病药以外的神峰口径）不在本批；tiaohou 经典建制未动（另行设计审定批）；TJ-017.2 跨规则调用仍阻塞。

## 2 设计定稿

### 2.1 消费子集实测（建节范围的唯一依据）

bingyao（`src/tianji_kb/bazi_bingyao.py`，Variant `bingyao-shenfeng-v1`）登记引文 9 条：神峰 8 条——disease_definition（definition，[7019,7035)）、medicine_definition（definition，[7036,7061)）、wealth_pair（encoded_rule，[7351,7367)，与 RULES[0] 同）、food_pair（encoded_rule，[7368,7385)，与 RULES[1] 同）、earth_example（registered_not_encoded，[7329,7350)）、procedure_zhong（registered_not_encoded，[7505,7540)，S4 审定明示不消费、只登记）、no_disease_clause（registered_not_encoded，[7605,7647)）、zhengguan_tension（registered_tension，[10010,10041)，在正官格节内）；滴天髓 1 条——ditiansui_counterweight（counterweight，Source `bazi.source.ditiansui-spouse`，[43767,43825)，只作 limitations 制衡证据）。定义节登记区间 DEFINITION_SECTION=[7019,7680)。现行 9 条均无 section_id。现行接入：chart 以 bingyao_variant 门控、bingyao_assessment(trace) 消费已执行步，assessment 不经 trace.add、不进 RuleMatch/Evidence。

dayun 神峰（`src/tianji_kb/bazi_dayun_classical.py`，Variant `conversion-shenfeng`）登记引文 6 条，全在《起大运法》节 [85001,85246)：sf_heading_yang（corroboration，[85001,85009)）、sf_ex1（corroboration_and_golden_basis，[85010,85068)）、sf_ex2（corroboration_direction_only，[85069,85123)；日数「四三十二日」讹乱已登记 EXCLUDED_SPANS、换算不消费）、sf_heading_yin（corroboration，[85129,85137)）、sf_ex3（corroboration_and_golden_basis，[85138,85188)）、sf_ex4（corroboration_and_golden_basis，[85189,85241)）。消费实测分两面：classical_direction 的 evidence_quotes 含神峰 6 条（corroboration 披露面）；shenfeng_convert_days 的 converted 输出 evidence_quotes 恰为 sf_ex1/sf_ex3/sf_ex4 三条——后者才是神峰换算 Variant 自身的实际消费子集。既有不一致如实登记：shenfeng_convert_days 的 rounding 拒绝分支与 zero-day 分支取 `_flags()` 默认（三命）段值、只有 converted 分支取 `_flags('shenfeng')`——pending 时代前两分支已写 registered 值，本批翻转后全段统一（等价比对 K2 类据实包含此统一，见 §5）。

### 2.2 新经典镜像结构定稿

新经典实体逐项镜像既有四经典实测结构，不得新造机制：classic 实体恰五字段 {id, domain, name, source_id, body_stage}（三命实体另带 source_ids 数组系其 S0+应用文本双源特例，神峰无双轨不带）；body_stage 取 `quarantine`——与三命、协纪同例（两者的 Canonical 在场形态均为隔离快照原文的节级切片、无独立清洗定本；滴天髓/渊海作 canonical 系因其另有清洗定本，神峰无此定本，不冒充）。chapter 实体 {id, domain, name, classic_id, locator}、section 实体 {id, domain, name, classic_id, chapter_id, source_id, locator, text, review{status=approved, method, scope}}、term 与 rule 实体字段集均与既有实体逐项同形（实施时以 s068–s070、r038/r039、dayun 两术语为逐字模板）。新经典 id `bazi.classic.shenfeng`（沿 yuanhai/sanming_tonghui/xieji/ditiansui 的短名拼音口径）。镜像不能成立处：无——四经典结构可完整镜像，未触发停工报告。

### 2.3 建节定稿（不多建）

- s071 病药定义节：章节 `bazi.chapter.shenfeng_bingyao`；文本 = 快照 [7019,7680) 整段 661 字（节首「何以为之病？」至节末「详见见验类。」为完整段落边界）；PUA 0、□ 0；含登记引文 7 条。
- s072 正官格张力窗口：章节 `bazi.chapter.shenfeng_zhengguan`；文本 = [10010,10041) 恰为张力引文本身 31 字（沿 s070 恰幅先例；该句自成完整句、前后文属其他论题，不扩窗）；PUA 0、□ 0。
- s073《起大运法》：章节 `bazi.chapter.shenfeng_qi_dayun_fa`；文本 = [85001,85246) 整节 245 字；PUA 0、□ 0；含神峰 6 条。节内异文（例 2 逆数目标与日数讹乱、例 3 表述差异）逐字保留、只登记不径改，sf_ex2 日数段禁用状态由公开模块 EXCLUDED_SPANS 承载。
- s074 滴天髓中和篇制衡窗口：章节 `bazi.chapter.ditiansui_zhonghe`（既有滴天髓经典内新章）；文本 = [43767,43825) 恰为制衡引文本身 58 字；PUA 0、□ 0。

节号顺延实测：现行最大 s070 → s071–s074；规则现行最大 r039 → r040/r041；Phase2 步名 bazi.phase2.bingyao_assessment、bazi.phase2.dayun_shenfeng_conversion 未占用（现行 40 步全量核查）。

### 2.4 规则 refs 子集审定

- r040 source_refs 恰 4 条（disease_definition、medicine_definition、wealth_pair、food_pair，全 s071）：定义句 + 两条编码对句，即 Variant 实际编码消费的全集（镜像 r037「定义+程序句」、r036「只绑裁定依据」）。earth_example / procedure_zhong / no_disease_clause 为登记引文（入节、公开登记补 section_id、不入 refs；procedure_zhong 经 S4 明示不消费）；zhengguan_tension 为登记张力引文（s072 承载、Variant 明示不覆盖）；ditiansui_counterweight 为 limitations 制衡证据（s074 承载、不入 refs，沿 E0346 §2.3 旁证不入 refs 审定——其证据功能是限制而非支持病药陈述）。
- r041 source_refs 恰 3 条（sf_ex1、sf_ex3、sf_ex4，全 s073）：即 shenfeng_convert_days converted 输出 evidence_quotes 全集。sf_heading_yang / sf_heading_yin / sf_ex2 为方向 corroboration 披露，不入任何规则 refs（sf_ex2 日数禁用在册）。

### 2.5 compose / view 终局形态审定

dayun-compose / dayun-timeline-view 两行自身无规则，其 pending 完全继承底层（E0346 改记 segmented_inherited_pending，unlock_path 明文「随神峰分段注册自动解除」）。神峰分段注册后，终局形态只有三种候选，逐一审定：

- 改记 registered：**不可行**。治理不变量要求 registered 行携带自有 phase1_rule_id/phase2_rule_id，且各批 records 的 rules_added 并集与全部 registered 行规则 id（含 additional_*）**恰等**（S5 公开测试钉死）；两行复用底层 id（r038/r039/r041 等）将使恰等多重集重复计数而断裂，新造 id 即无执行步的空注册——任务书明文禁止。
- 移出治理册（删行）：**不可行**。登记册为 append-only 历史，行项从未删除；且两模块的披露仍需在册可核。
- 维持 maintained_pending / inherited_pending 并改记终局披露（**采用**）：两行留在维持名单，reason 改记继承链已终局解除，unlock_path 改记为仅余「本层将来产生独立规则时另行注册」的条件路径；两模块 evidence_binding 改记终局形态 `inherited_registered_phase1_phase2`（沿 pending → segmented_inherited_pending 的披露词表谱系补全终局值：底层全段已注册、本层只继承披露、不冒充自有注册）。

据此治理维持名单实测 **5 → 4**（bingyao 翻转 −1；两 inherited 行以终局形态留在名单内）。任务书「预期 5→3」预设两 inherited 行退出名单，与上述不变量冲突；任务书同时明示「以代码实测为准并在报告说明」——本审定即该说明，父级复核以本节为准。

### 2.6 执行接入定稿

- bingyao：沿既有 bingyao_variant 门控，chart 在 bingyao_assessment 计算后以 trace.add 登记新步（形同 ren 先例：步输出由已执行步计算得出后登记）；assessment 块除注册披露（evidence_binding）外逐字不变；engine allow_research 门禁与公开投影剥离（bingyao_assessment 既有剥离）保持。
- dayun 神峰：bazi_dayun_classical 新增测量级入口 shenfeng_convert_measurement（镜像 sanming_convert_measurement：经 _validate_measurement 对钉定 provider 重放校验后只消费实历整日数）；chart 新增门控 kwarg dayun_shenfeng_measurement（默认 None；月柱交叉核对、与方向结果一致性核对，与三命测量同位处理），trace.add 新步产出 result['dayun_shenfeng_conversion']；engine 新增研究门禁一行；public_projection 新增剥离一行。harness 契约扩展与 E0344/E0346 同形：golden.py / validate_phase2.py / golden schema 零改动，provider 三重钉死逐字不变，扩展只落 provider 签名与用例 input。

## 3 密封著录明细

密封变更恰 5 文件（私有检出著录 → 暂存快照导出）：

- `data/canonical/bazi/phase1_knowledge.json`（SHA256 `de79653afb384d8c0275a8cf2caff3ab4170c4a200acfd7b03afde02a63ba198`）：新经典 bazi.classic.shenfeng（body_stage=quarantine）；新章 4（shenfeng_bingyao、shenfeng_zhengguan、shenfeng_qi_dayun_fa、ditiansui_zhonghe）；新节 s071（661 字）/s072（31 字）/s073（245 字）/s074（58 字），文本逐字切片、PUA/□ 均 0；新术语 bazi.term.bingyao、bazi.term.dayun_shenfeng_conversion；新规则 r040（refs 恰 4）/r041（refs 恰 3）。计数：经典 4→5、章 29→33、节 70→74、术语 36→38、规则 39→41。著录为 append-only（既有实体逐字未动，经前缀一致性核验）。
- `data/canonical/bazi/phase2_execution.json`（SHA256 `2163c6cf9495ad8dd6e171f6083d66bc02bd2ee881e46c18b721c6cb0f56c98e`）：新步 bazi.phase2.bingyao_assessment / bazi.phase2.dayun_shenfeng_conversion（均 validated）；步数 40→42。回归测试文件名受 execution schema 模式 `^tests/test_phase2_[a-z]+\.py$` 约束，密封专项定名 tests/test_phase2_bazishenfeng.py。
- `data/canonical/bazi/phase2_golden.json`（SHA256 `bbffab397f976bd5430c257c327fa12e3248e2c5484a1ec64e2b4a6e011c6171`）：新增 11 例（169→180）。bingyao 6 例复用 tests/golden_tj013_bingyao.json 既有见证盘（真实出生时刻在册：1958-08-15T19:30 等，柱经真实历法路径得）——wealth-disease-medicine、wealth-disease-no-medicine、medicine-without-disease、peer-class-boundary-jiecai、foodwound-disease-medicine、dual-pair-wealth-only（源 id dual-pair-wealth-only-foodwound-incomplete），期望值以 TJ-013 黄金文件的审定 expected / expected_pair2 / pair2_regression 为独立依据；神峰换算 5 例复用密封 Golden 既有三命测量对象（q1–q4 + ADV-001，真实盘/真实时刻，elapsed_whole_days 依次 23/27/22/8/0 → 文本运数 2760/3240/2640/960 与零日 unresolved），input 以同一测量对象改挂 dayun_shenfeng_measurement。
- `data/coverage/phase1.json`（SHA256 `dd546d0d426242daace7816327d6d7da9d46ec80b4a639fa370655de4b1f021b`）与 `data/product/knowledge_coverage.json`（SHA256 `d45b876c3cceae73eb37ec3ed26cde76353c856ba8c3d538bd2da43052cf43fc`）：组装树上以官方生成器（build_phase1_coverage / build_product_coverage）重生回填；公开侧 docs/COVERAGE.md bazi 行同步为 `| bazi | 2/3 | 74 | 38 | 29/11/1 | 0/0/7/0 | phase1_complete |`。

## 4 公开侧改动明细

- `src/tianji_kb/bazi_bingyao.py`：QUOTES 9 条补 section_id（神峰 7 条 s071、张力 s072、制衡 s074）；bingyao_lookup 的 evidence_binding 翻转 registered_phase1_phase2；LIMITATIONS 末条改记注册状态句（引 r040/新步）；模块 docstring 补 E0348 注册段。
- `src/tianji_kb/bazi_dayun_classical.py`：神峰 6 条经 _SHENFENG_SECTION_OF_QUOTE 映射补 source_section_id=s073（沿 E0346 映射机制，source 不改指）；_flags 全段统一 registered_phase1_phase2（pending 时代默认段分支的历史不一致据实登记于函数注释）；新增 shenfeng_convert_measurement；LIMITATIONS 注册分段口径句改记 E0346/E0348 双分段已注册；模块 docstring 补 E0348 段。
- `src/tianji_kb/operations/bazi_chart.py`：bingyao 块改 trace.add 接入；dayun 组合块条件增 dayun_shenfeng_measurement 并同位处理（月柱/方向交叉核对 + trace.add 新步）；签名新增 kwarg（默认 None）与函数头类型校验一行；production_scope 注册口径句更新（两分段均已注册）；AI 门条件增该 kwarg。
- `src/tianji_kb/engine.py` / `public_projection.py`：各增一行（研究门禁 / 剥离 dayun_shenfeng_conversion）。
- `src/tianji_kb/bazi_dayun_compose.py` / `bazi_dayun_timeline_view.py`：_flags 改记 inherited_registered_phase1_phase2；compose LIMITATIONS 注册句与两模块 docstring 补 E0348 终局改记段。
- `src/tianji_kb/bazi_registration_governance.py`：新增 GOVERNANCE_SHENFENG_RECORD；bingyao 行翻转 registered（r040/新步）；dayun 行 additional ids 增 r041/神峰步、segments.shenfeng 改记 registered、reason 补 E0348 段；compose/view 两行 reason/unlock_path 改记终局形态（§2.5）。
- `config/knowledge_sources.json`：bazi.source.shenfeng 与 bazi.source.ditiansui-spouse 各追加 E0348 review_scope 补记一句（来源总数 102 不变、内容哈希不动）。
- 测试：新增公开专项 tests/test_governance_shenfeng_expansion_public.py（11 测）与密封专项 tests/test_phase2_bazishenfeng.py（13 测），新公开专项已按名接入公开 CI（validate.yml）。既有钉迁移均以 E0348 注释链改写、无放宽、无删测：治理集合钉（S5 治理公开专项、zaqi/ren/dayun 三命晋级公开专项、四份 TJ-018.3 历史晋级公开专项、三刑/干支/禄刃/ren/zaqi 五份密封注册专项的治理一致性断言、TJ-013 bingyao 公开专项的 binding 钉）；全局计数钉（干支/禄刃/ren/zaqi 密封注册专项与 P1 三刑密封专项的经典/章/节/术语/规则/步计数、密封 Golden 总数 169→180（含三刑密封专项两处）、合化裁定模块 SEALED_MEASUREMENTS 三总数及其公开 golden 镜像（新节已经实测不含合化关键词与「五合」、关键词钉不变）、Phase1 bazi 可执行规则 id 集增 r040/r041 与规则引文来源集增 bazi.source.shenfeng）。另注：product coverage 的审计输入含全部 src 与 test_phase 文件哈希，覆盖文件已以最终代码重生并重导出暂存快照（钉值见 §7 注）。

## 5 等价比对（封闭清单与结果）

比对集（同一捕获脚本在基线组装 = main 6b64dc1d + 旧快照 97e211c4… 与工作组装 = 本批代码 + 暂存新快照各跑一次，逐叶 JSON 比对）：bingyao_lookup 13 见证盘、bingyao chart 封套 13、冲突/可读组合封套 9（TJ-013.2 黄金全集）、dayun 方向 120（60 干支×2 角色）、sanming elapsed 扫描 44、神峰日数扫描 83（0–40×双向 + 约整拒绝）、测量级换算 5 对象、compose 6 例、compose 神峰并列 1 例、view 双方法 12 个方法产出 + 并列视图 2 个、密封 Golden 全集封套（基线 169 例）。

封闭清单（先行定义，实施前定稿于本节）：
- K1 引文节绑定新增：引文 refs 新增 source_section_id（神峰 6 条 → s073），仅新增键、无既有键改值。
- K2 注册披露值翻转：evidence_binding 由 pending_phase1_rule_registration / segmented_inherited_pending 改记 registered_phase1_phase2 / inherited_registered_phase1_phase2（含神峰换算 pending 时代默认段分支的历史不一致统一）。
- K3 注册口径句更新：LIMITATIONS / scope_limits / production_scope 中注册状态句的改记文本。
- K4 bingyao 新步接入的封套增量：trace 与 rule_matches 各 +1 条（新步及其 match）、evidence 新增新步 4 条引文的证据条目；既有步/match/证据逐字不变。
- K5 新增对象：密封 Golden 新增 11 例的封套与 rule_ids、shenfeng_convert_measurement 新入口的产出（基线无此函数，非既有产出变更）。

实测结果：叶级差异共 **1,759** 处——K1 1,113、K2/K3 披露值与口径句 487（披露值 145 + 句子 342）、K4 132、K5 27；**清单外差异 0、计算值差异 0、REMOVED 0**。神峰并列组合块与双方法视图除 K1/K2/K3 外逐字一致；163 例非门控 Golden 封套在回滚组装下逐字 identical（见 §6）。

## 6 伪造负例与回滚演练

伪造引文负例（密封专项 test_forged_bindings_are_rejected，以 resolver 实时实体追加伪造 ref 后复原）：(1) r040 病定义句改字（病→疾）——拒；(2) r040 wealth_pair 错绑 s072 窗口节——拒；(3) r041 sf_ex1 错绑 s071——拒；(4) r041 sf_ex4 改字（三岁→四岁）——拒。四负例均被 EvidenceResolver 以引文/节不匹配拒绝。另两类冒充不属 resolver 职责、据实区分：制衡引文（滴天髓 s074）绑回本节在形式上是合法引文，其「永不作 r040 规则引文」的纪律是语义审定，由密封专项的 refs 恰等断言钉住（该引文被断言不出现在任何规则的 refs 中）；在节内但未消费引文（sf_ex2、标题句）冒充 refs 同理由 refs 恰等断言钉住。

回滚演练（本批代码 + 旧快照 97e211c4… 组装）：默认面 163 例非门控 Golden 封套与基线逐字 identical（169 例中余 6 例为三命门控例，单独验证见下）；bingyao 门控路径 fail-closed（ValueError: Unknown rule: bazi.phase2.bingyao_assessment）；神峰测量门控路径 fail-closed（ValueError: Unknown rule: bazi.phase2.dayun_shenfeng_conversion）；既有三命门控路径在旧快照下照常 converted（不受影响）。

## 7 实施记录与换代清单

- 机上全配方复跑（accept_offline --suite all，本批代码 + 暂存快照 + 新钉）：见 PR 报告与本节关账前补记（基线正式验收 2787，增量逐项对平）。
- 换代清单（交付父级，合并前先行换代）：暂存快照 237 文件 / 16,272,294 字节 / manifest SHA256 `380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b`（旧值 237 / 16,221,036 / `97e211c4582f7cf4d890c2bf8071573fbaced193d740c185d2c891a3f2e51324`）；私有检出根 manifest 与 import_public_snapshot EXPECTED_BYTES 已同步重生（237 / 16,272,294，verify 绿）；live 快照备份名建议 `secure/tianji-knowledge-pre-shenfeng-backup`；cicd 钉改 `TRUSTED_MANIFEST_SHA256=380bb73e…`（父级合并前先行，本批不动 live 与 cicd 钉）。注：暂存快照曾以 manifest f758297a 首版导出，其后因 product coverage 的审计输入含 src 与 test_phase 文件哈希、钉迁移后须以最终代码重生 coverage 并重导出，最终钉值以本节 380bb73e 为准（字节数不变、仅 coverage 文件哈希不同）。
- 台账：E0348（归属 TJ-018.2、状态「阻塞」不变）。

## 8 仍未判断与后续

- 病药裁定面全未开放：determination 恒 None、去病效力恒未裁定、「无病」永不输出；正官格太弱太旺口径与定义节口径的冲突只并列登记（s071/s072），不裁决。
- 神峰经典目前只建四节：四病四药诸节、格论诸节、赋论等均未建节；《起大运法》以外的大运相关神峰文字未审定。神峰全书逐字校勘未做（C 级单一谱系、简体转写，讹字只登记）。
- dayun 输出契约不变：神峰换算与三命换算永不合并；首运序列口径差异仍不在 Variant 范围；TJ-017.2 跨规则调用仍阻塞（依赖 M2 存量，与本批无涉）。
- 治理维持名单余 4 项：tiaohou-qiongtong-v1（经典建制须先立设计审定批，为下一批）、siling-yin-pilot（待用户裁定）、dayun-compose / dayun-timeline-view（inherited 终局形态，本层产生独立规则时另行注册；视图公开开放仍须分阶段开放另行裁定）。
- 阳刃「凶/㓙」勘误登记仍待后续校勘勘误批（与本批无涉）。

## 9 关账记录（E0349，append-only 补记）

- 实施批终局：PR #525 已合并，Merge SHA `579185498d5c4669584a49f7f2d5ffab924c5596`（main 现行 HEAD）。
- 正式验收终局核对（直读管线 acceptance-579185498d5c4669584a49f7f2d5ffab924c5596 记录）：result SUCCESS，分项 public-git-checkout 15 / public-only 24（skipped 1）/ private-backend 2772，合计 2811 测，failures 与 errors 均为 0；密封快照 237 文件 / 16,272,294 字节 / manifest `380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b`，与本批暂存快照 staged-v2 三元组一致。
- 部署终局核对（deploys.log）：2026-10-31T22:09:51Z DEPLOYED，pin `13598de617066e41146e9f836592e737a059f66cc6b76d6dc3ef8401f99925a8`，health 与 bazi 探针 ok。
- 换代实际执行记录：父级于合并前先行执行——旧快照备份于 `secure/tianji-knowledge-pre-shenfeng-backup`（manifest `97e211c4…`）；live 快照由最终暂存快照 staged-v2 换入，`diff -r` 逐字一致；cicd 钉（cicd/env/trusted-acceptance 的 TRUSTED_MANIFEST_SHA256）由 `97e211c4…` 改为 `380bb73e…`。换代 before/after：237 文件 / 16,221,036 字节 / `97e211c4…` → 237 文件 / 16,272,294 字节 / `380bb73e…`。
- 注册翻转终局核对：bingyao-shenfeng-v1 已翻转 registered、dayun-classical-variants 神峰分段随行翻转 registered（两段均 registered）、dayun-compose 与 dayun-timeline-view 为 inherited 终局形态（见 §2.5 审定）；治理维持名单 5 降至 4。注册成立第五条件（部署验收绑定）终局核对完成，翻转已随合并生效。
- 语义守恒终局核对：bingyao determination 恒 None、无「无病」输出、双对结构不变；dayun 输出契约逐字不变（只有区间、无单点字段、无年龄键、恰逢节拒绝与 ADV 行为不变）；用户可见能力零变化。
- 机上清理记录（关账批执行）：已删除 `/data/workspace/shenfeng` 下组装树（base-asm、rollback-asm、work-asm、work-asm2、repro-pub、repro2-pub、work-pub、orig）、三代暂存快照（staged-pre、staged-final、staged-v2）、捕获文件（baseline.json、work.json）与 tmp 临时库文件一批；日志（backend.log、backend2.log、fixrun.log、fixrun2.log、fixrun3.log、repro.log、repro2.log）与脚本 capture.py 及 backend_mods.txt 保留。清理前后 live manifest 复核仍为 `380bb73e…`、备份目录完好；/data 已用 74% 降至 70%（20G 总量、已用 14G、可用 6.0G）。
- TJ-018.2 保持阻塞、TJ-018.3 保持待做；队列下一批：tiaohou 经典建制设计审定批，其后为阳刃「凶/㓙」校勘勘误登记批。
