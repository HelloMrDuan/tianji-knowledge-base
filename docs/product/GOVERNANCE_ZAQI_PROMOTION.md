# pattern-zaqi 晋级实施批（治理 pending 8 项审计推荐第一批，E0342）

状态：实施完成，PR 待合并；快照换代由父级在合并前先行（本批只交付暂存快照与换代清单，live 快照与 cicd 钉未动）。基线 main `1a43c4fec57e10ec8fdb8a52d8f8eca7ce43e889`（治理审计 E0341 已合并）、台账 341 事件、密封钉 `15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5`。

## 0. 授权与范围

授权链：治理登记维持 pending 8 项解锁条件审计（E0341，`docs/product/GOVERNANCE_PENDING8_AUDIT.md`）§2.6 将 pattern-zaqi 定为缺口最小项、§4.2 推荐其为晋级实施第一批；Slice B 杂气选格审定（E0218）定陈述语义；注册形态沿 TJ-018.3 批一 trace 接入先例与批三 B-2 禄刃晋级形制（`docs/product/TJ0183_LUREN_PROMOTION.md`）。本批范围：为既有杂气选格陈述补齐 Canonical 建节、Phase1 规则、Phase2 trace 步与密封 Golden，完成治理翻转；**陈述裁定语义逐字不变**（戊/己日主多人元透出并列、无透 abstain、一般日主「取土为格」原文 + conversion_status=unadjudicated、三命两例证仅 conflict-branch evidence）；不触及 Slice D-1 任氏寅月真格、不触及扶抑 U1/U3、不解锁任何 determination。

## 1. 晋级五问答复

（1）真正补齐的专业判断是什么？——无新增判断。补齐的是既有陈述的证据注册：杂气选格陈述（Slice B 已审定并已在生产 pattern 路径输出）此前三条引文的 source_section_id 全为 None、无 Phase1 规则、无 Phase2 步、evidence_binding 为 pending；本批使其成为可由 EvidenceResolver 逐条复核、由 ExecutionTrace 留痕、由密封 Golden 真实 fire 的注册陈述。determination 仍恒为 unresolved，吉凶/成败/清浊/用神一概不判。

（2）引文如何绑定到 Canonical 节？——三条引文各绑定一节：原注杂气选格陈述段建节 s065（滴天髓既有八格章内、段全文 152 字，段首「原注：飞天合禄之类」，半角标点为快照原形）；三命两例证各建窗口节 s066（卷六《日禄归时》七法第一法整条 84 字，引文为其后段）与 s067（卷七《女命总断》诗句条全文 51 字）。绑定口径：例证不在任何已建 Canonical 节内（审计与本批子串核查双证），故按「随本批建节」处理；窗口取完整条目而非孤句，理由与取舍见 §7。公开登记侧三条引文的 source_id 与 quote 逐字不变，仅补 source_section_id。

（3）Phase1/Phase2 注册形态？——新规则 r036（source_refs 恰为裁定依据 1 条：原注杂气段，role=classical；两例证不入规则 refs——按 Slice B B5 它们只作冲突分支证据、非裁定依据，且 Phase1 引文角色枚举（classical / implementation / derivation）无冲突分支位；其证据地位由窗口节 s066/s067（review scope 明示冲突分支角色）与陈述输出 conflict.case_refs 承载）；新术语 bazi.term.zaqi_selection；新 Phase2 步 bazi.phase2.pattern_zaqi（validated，6 例 Golden 真实 fire）；chart 内陈述由「pattern 块内直调附 result」改为 trace 步接入（批一/B-2 形制），步位于 trace 末尾，不引起既有步索引位移。

（4）翻转前后等价如何证明？——比对集与封闭清单见 §4：密封 Golden 全集 142 例原输入（Set A）、Slice B 见证 6 盘（Set B）、142 例强制 pattern_variant（Set C）；归一化仅限清单四项，清单外逐字段一致，实测结果见 §4。

（5）仍未判断的范围？——见 §8：杂气格局的真假/成败/清浊/用神仍不可判断；一般臂土格换算仍未裁定；两例证所代表的三命取格口径与原注口径的冲突仍只并列登记、不裁决；四季月以外的选格口径不在本陈述范围。

## 2. 注册形态结论（实施前复核）

- ID 占用：Canonical 节现行最大 s064 → 新节 s065/s066/s067；Phase1 规则现行最大 r035 → r036；Phase2 步名 `bazi.phase2.pattern_zaqi` 未占用（现行 36 步全量核查）；新章 ID `bazi.chapter.sanming_rilu_case`、`bazi.chapter.sanming_nvming_case` 未占用。
- zaqi 现行执行形态（实测）：chart 在 pattern_variant 块内直接调用 `month_pattern_zaqi(trace)` 并把返回 dict 附于 result，不经 trace.add 登记——与 B-2 翻转前 pattern_route 的形态相同。`month_pattern_zaqi` 消费已执行步（pillars/ten_gods/hidden_stems/hidden_to_visible）的 trace 事实，缺事实时 fail-closed 抛错；chart 中 pattern 块之后再无 trace.add，新步居 trace 末尾。
- 术语为注册契约必需：现行 35 条 Phase1 规则全部带 term_refs，故本批新建术语 bazi.term.zaqi_selection（定义为 classical_excerpt 体例，source_refs 为杂气段核心句）。
- 计数迁移：Canonical 节 64→67、章 25→27、术语 32→33、Phase1 规则 35→36、Phase2 契约步 36→37、密封 Golden 142→148、Phase1 实体 1090→1097；coverage bazi 域 chapters 25→27、sections 64→67、terms.canonical 32→33、rules.executable 23→24。

## 3. 密封著录明细

- 章：`bazi.chapter.sanming_rilu_case`（卷六·日禄归时（杂气例证窗口））、`bazi.chapter.sanming_nvming_case`（卷七·女命总断（杂气例证窗口））。
- 节：`bazi.section.s065` 滴天髓杂气选格陈述段（快照 `ditiansui_chanwei.txt` 字符区间 [33161, 33313)，152 字，与公开登记引文逐字一致，零 PUA、零 □，全书唯一出现，挂既有章 bazi.chapter.pattern_bage）；`bazi.section.s066` 案一窗口（S3 [192089, 192173)，84 字，七法第一法整条）；`bazi.section.s067` 案二窗口（S3 [245029, 245080)，51 字，诗句条全文）。两例证文本 S0 与 S3 逐字一致（位移 −1）。
- 术语：`bazi.term.zaqi_selection`「杂气选格」。
- 规则：`bazi.rule.r036`「杂气选格陈述（滴天髓原注层）」，operation.kind = evidence_bound_selection_statement，source_refs 恰 1 条（裁定依据子集，定稿见 §1（3）），窗口节内其余文本不入 refs。
- 步：`bazi.phase2.pattern_zaqi`「杂气选格陈述步」，phase1_rule_refs = [r036]，validation_status = validated，golden_case_ids 为 §3 末 6 例，regression_test = tests/test_phase2_bazizaiqi.py，evidence_scope 为 C 级研究口径（不定格名/真假/成败/清浊/用神/吉凶、土格换算未审、公开投影剥离）。
- Golden 6 例（Slice B 见证盘转入，真实出生时刻、四柱经密封日历路径重算一致，干支直给 + pattern_variant 输入，expected 为 pattern_zaqi 子集断言）：bazi.zaqi-selection-wuji-chou-single-exposed（1953-01-08T11:30+08:00，戊己臂单透）、bazi.zaqi-selection-wuji-xu-no-exposed-abstained（1949-10-15T13:30+08:00，戊己臂弃判）、bazi.zaqi-selection-general-xu-sanming-type（1949-10-09T13:30+08:00，一般臂三命同型盘）、bazi.zaqi-selection-non-misc-yin-not-applicable（1949-02-13T09:30+08:00，非四季月）、bazi.zaqi-selection-general-chen-no-exposed（1950-04-09T09:30+08:00，一般臂无透）、bazi.zaqi-selection-wuji-wei-two-exposed（1951-07-18T06:30+08:00，戊己臂双透并列）。四季月四支（辰戌丑未）与三臂全覆盖，既有见证盘已足 fire 新步，无需补盘。
- 公开侧同步：ZAQI_QUOTES 三条补 source_section_id；zaqi 块输出 rule.source_section_id、conflict.case_refs 两条补 source_section_id、evidence_binding 翻转 registered_phase1_phase2；ZAQI_ADJUDICATION_NOTES 的 B6 条与 ZAQI_LIMITATIONS 第 4 条改写为已注册表述（原审定字句的语义部分未动）；治理行 pattern-zaqi 翻转 registered，维持名单 8→7；合化事实层密封计数钉（sections 64→67、phase1 rules 35→36、phase2 steps 36→37）同步迁移，三段新节文本不含合化关键词（全词表由密封合化测试全节扫描复核）。

## 4. 等价比对（封闭清单与结果）

比对集：Set A = 密封 Golden 142 例原输入；Set B = Slice B 见证 6 盘（pattern_variant 开启）；Set C = 密封 Golden 142 例强制 pattern_variant。捕获对象为 chart 完整执行封套（result + trace + evidence），规范化 JSON 逐字段 diff。

封闭清单（归一化仅限以下四项，清单外逐字段一致）：
（1）trace 步索引指针按 rule_id 改写吸收——chart 的 trace.add 把步登记序号写入 evidence 的引用位置，新增末尾步使引用序号表示变化时按 rule_id 对齐（本批新步居 trace 末尾，实测既有步序号不变，此项为防御性归一化）；
（2）工作封套删除 pattern_zaqi 步本身、其 rule_match 记录与仅由其引出的 evidence 条目（新增注册的预期增量）；
（3）pattern_zaqi 块内的注册披露字段：evidence_binding 的值、rule.source_section_id、conflict.case_refs 的 source_section_id 键、adjudication_notes 与 scope_limits 中的注册状态句，替换为统一标记后比对；
（4）治理与计数钉的迁移属测试层断言，不在封套比对内。
production_scope 文本逐字不变（chart 注释更新、scope 句未动）。工作集 Golden 多出的 6 例新用例在 Set A/C 中各出现一次（id 前缀 bazi.zaqi-selection-），属预期增量。注册状态句的识别口径：含 evidence_binding 标记（pending_phase1_rule_registration / registered_phase1_phase2）或中文注册表述（「尚无密封 Phase1/Phase2 rule 注册」/「已完成密封 Phase1/Phase2 rule 注册」/「无 Phase1/Phase2 rule 注册」）的行，且新旧两侧须同为注册状态句才按清单（3）归一化，单侧命中即报差异。

结果（机上实测）：基线捕获 290 封套（Set A 142 + Set B 6 + Set C 142）、工作捕获 302 封套；工作集多出的键恰为 12 个（6 例新 Golden × Set A/C），基线键无一缺失；290 个共有键经封闭清单归一化后逐字段全等，清单外差异 0。首轮比对曾报 214 键差异，逐项定位为 ZAQI_LIMITATIONS 第 4 条的旧句为中文表述（「本陈述尚无密封 Phase1/Phase2 rule 注册，不进 RuleMatch 与 Evidence；…」）未被初版关键词覆盖——该行与新句同为注册状态句（句尾「透出事实以既有 hidden_to_visible 为准（日干除外）」逐字保留），按上列双侧口径归一化后差异归零；此为比对工具口径修正，非代码或断言变更。

## 5. 伪造引文负例与回滚演练

伪造负例（密封专项 tests/test_phase2_bazizaiqi.py）：将伪造引文追加进 r036 的 source_refs 后 EvidenceResolver 拒绝——（a）杂气段改字（「只当取土为格」改作「只当取金为格」）配 s065；（b）案一引文错绑案二窗口 s067（文本不在该节内）；（c）案一引文以 S0 登记来源 bazi.source.sanmingtonghui 配 s066（与节 source_id 不一致）。三例均以 ValueError 拒绝，实测通过。

回滚演练（机上实测）：新代码 + 旧快照（15bd5a26…）组装下——Slice B 见证盘的 pattern_variant 路径以 ValueError: Unknown rule: bazi.phase2.pattern_zaqi 显式 fail-closed；旧快照 142 例中不带 pattern_variant 的默认路径 76 例封套与基线捕获逐字一致（0 差异），带 pattern_variant 的 66 例全部 fail-closed（pattern 路径整体依赖新注册，与批一/B-2 回滚口径一致）。

## 6. 快照换代清单（交付父级，合并前先行换代）

before：237 文件 / 16,001,603 字节 / manifest `15bd5a268d792c86072cf9ac51effb22ca5aefa004ea7ab44e7bbf44135682d5`。
after：237 文件 / 16,072,121 字节 / manifest `6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0`。
五变更文件 sha256（after）：data/canonical/bazi/phase1_knowledge.json `df55c6505b4cad47b315b839313508ad61e844613882d901460576f9c1088818`；data/canonical/bazi/phase2_execution.json `97d7c3fa9c06f933ec6f78c4ccba34637b8904cb1a5d91a781947c47d2001d49`；data/canonical/bazi/phase2_golden.json `878c5369bb0bdb5e8a6757c949ac90ddb62db2ec0e16e4374144110bdab68d3d`；data/coverage/phase1.json `13c117993aeb141a60328468a8ea3f3b4c942770f5d124acab1db083ebb77fa2`；data/product/knowledge_coverage.json `a43cc223cf8f5bb26cebcbeed35912ff8fc3c71fc4f14e37d1571b183a0508e0`。

变更文件仅此 5 个（路径为快照内相对路径）。其中 coverage 两件为生成器重生件：在组装树（新代码 + 新数据）上运行 scripts/build_phase1_coverage.py 与 scripts/build_product_coverage.py 重生后回填私有检出（data/coverage/phase1.json 与手工口径仅 production_chunks 一处派生值差异，154；data/product/knowledge_coverage.json 的 _audit 输入指纹随三件 canonical 文件与公开测试文件同步刷新）；公开侧 docs/COVERAGE.md 的 bazi 行随 build_phase1_coverage 同步更新（64/32/23 → 67/33/24）。私有检出侧：五文件同步著录、私有检出 import 脚本 EXPECTED_BYTES 同步为 16072121、检出根 manifest 以脚本自身 inventory()/manifest_for() 重生并 verify 通过（检出根 manifest 与快照 manifest 为双格式口径，不互抄）。暂存快照位于机上 `/data/workspace/zaqi/staged-snapshot`（由私有检出经 export_private_data 导出并 verify_private_data 校验），live 快照与 cicd 钉本批未动。

## 7. 实施前复核结论（引文定位与窗口定稿）

- 引文 1（renshi.zaqi_passage）：滴天髓快照全文 find 唯一命中 [33161, 33313)，段界即引文本身，152 字、零 PUA、零 □；段以「原注：飞天合禄之类」起（论飞天合禄等遥合非格、及四季月选格口径），标点半角为快照原形，逐字保留；属既有章 bazi.chapter.pattern_bage，直接建节，无需新章。节名取「杂气选格陈述段（原注）」为描述性命名，不冒充原书节题。
- 引文 2（sanming.zaqi_case_rilu）：登记坐标 S0 [192131, 192174)、S3 [192130, 192173)，两本逐字一致。向左扩展至条首「一曰青云得路」得窗口 [192089, 192173) 共 84 字——取舍：引文是「七法」第一法的后半（含法名与断语），孤句建节会使法名脱节；整条窗口与批二 s061 整节、卷六登记整节先例一致，且窗口内非引文部分不入 r036 的 source_refs（子集定稿保证绑定精确性不因窗口放宽）。新章 bazi.chapter.sanming_rilu_case。
- 引文 3（sanming.zaqi_poem_nvming）：S0 [245030, 245081)、S3 [245029, 245080)，51 字；诗句条目前后换行分隔、自成单元，窗口即引文本身。新章 bazi.chapter.sanming_nvming_case。
- 「只当取土为格」「杂气财官」在现行 Canonical 全部 64 节中 0 命中（审计结论复核属实）；「杂气」仅出现在 s005/s040/s053 的他段语境，非本段文本。
- 两例证的 S3 区间 PUA 与 □ 均为 0；两窗口不含「五合/化气/合化/化象」字样（合化事实层全节关键词扫描由其密封测试在组装时自动复核）。

## 8. 仍未判断与后续

- 杂气格局真假、成败、清浊、用神：仍不可判断（determination 恒 unresolved）；本批只完成陈述层注册，未解锁任何格局裁定。
- 一般臂「取土为格」的土格换算：仍未裁定（conversion_status=unadjudicated），需流派级审定批另行处理。
- 三命两例证与原注口径的冲突：仍只并列登记（conflict_present 如实标注），不裁决、不升级为例证为规则。
- 后续顺位（审计 §4.1）：ren-pattern-yin-true-v1 执行绑定批（第二顺位）、dayun 三命分段批（第三顺位）；tiaohou 与 bingyao/dayun 神峰分段须先立经典扩编设计审定批；siling-yin-pilot 待用户裁定。

## 9. 关账记录（E0343，append-only 补记）

- 正式验收（直读管线记录 acceptance-ef588ee1d0deca41542f7c209eb1dcd342124de9.json）：result SUCCESS；public-git-checkout 15 测、public-only 24 测（skipped 1）、private-backend 2685 测，合计 2724 测，failures 与 errors 均为 0；快照 237 文件、16,072,121 字节、manifest 6edcebc669e9b3de09856f353f6b1eafc22bff47a8dbfef3f35afdffacc1bfc0。
- 部署（deploys.log）：ef588ee1 于 2026-10-31T14:17:22Z DEPLOYED，pin 02953fcbeb94ffc27f6dc1cb328325feb78c58d79b59ec5b4c61a0d7fc9626a1（health 与 bazi 探针 ok）。
- 换代实际执行记录（父级合并前先行执行）：旧快照备份于机上 secure/tianji-knowledge-pre-zaqi-backup（manifest 15bd5a26…）；live 快照由暂存快照换入且 diff -r 逐字一致；cicd 钉 TRUSTED_MANIFEST_SHA256 已改为 6edcebc6…；换代三元组 before 237 文件 / 16,001,603 字节 / 15bd5a26… → after 237 文件 / 16,072,121 字节 / 6edcebc6…。
- 注册翻转终局核对：pattern-zaqi 翻转 registered 已随正式验收与部署终局成立，治理维持名单 8 降至 7；§8 所列未判断范围（杂气格局真假、成败、清浊、用神，一般臂土格换算，三命两例证冲突并列）逐字不变。
- 机上清理记录：关账批已删除 /data/workspace/zaqi 下组装树（asm-base、asm-final、asm-rollback、asm-work、base-pub、work-pub）、暂存快照（staged-snapshot）、tmp 目录、work.tar.gz 与 patch 文件（zaqi.patch、zaqi-full.patch、backfill.patch），日志与脚本保留；清理前后 live manifest 复核仍为 6edcebc6…、备份目录完好，/data 已用 64% 降至 61%。
