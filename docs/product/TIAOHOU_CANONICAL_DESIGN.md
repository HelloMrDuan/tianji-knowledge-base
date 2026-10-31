# TIAOHOU_CANONICAL_DESIGN — 穷通宝鉴经典建制设计审定（E0350）

本批性质：治理 pending 审计（docs/product/GOVERNANCE_PENDING8_AUDIT.md §2.1）指定 tiaohou-qiongtong-v1 须先立经典建制设计审定批。本批严格只设计与只读追踪：不建任何 Canonical 实体、不写任何 Phase1/Phase2 绑定、不翻转任何注册状态、不改动任何执行代码与密封资产。文中一切结论均为设计层审定（语气为「拟」「定稿为设计」），实施状态恒为未实施；实施须待关账 E0351 后由父级另行派发实施批。

## 0 授权与范围

- 授权链：用户能力补全总指令（2026-10-26）与自主批次循环授权；治理 pending 审计 §2.1 定性 tiaohou 缺口为「canonical_evidence_absent 的经典级形态」，§4.1 归类「缺 Canonical 建制（非缺原文）」，§5 明示「神峰/穷通建经典的底本与分节口径」为设计审定批的议题；神峰扩编（E0348）已立新经典镜像先例，本批为穷通立设计。
- 基线：公开 main `26bf90a3f23df6d234ac5ca5a2934f0f711f2c44`（神峰关账 #526 已合并），台账 349 事件（末号 E0349），密封钉 `380bb73e34babc30bcc80e5ad7f296175f6be206af6a77f1abb4a07b94da654b`（本批不动）。
- 范围：只答六个设计问题并给定稿判据——(a) 经典建制形态；(b) 建节计划；(c) 绑定设计（Phase1 规则组织、Phase2 步形态、validated 的 Golden 设计）；(d) 注册翻转判据（五条件可机检口径、治理行翻转形态、S5 不变量影响面）；(e) 实施批切分与硬验收清单；(f) 风险与未决项。
- 不在本批：任何实施；siling-yin-pilot（待用户裁定，本批不触）；扶抑 U1/U3（不触）；调候与其他喜用体系的合并或冲突裁决（TJ-013.2 层面，本批不触）；穷通多底本校勘（018 式校勘未做，本批不启动，只在 §8 登记为路线事项）。

## 1 现状追踪结果（只读实测）

### 1.1 tiaohou 模块消费结构实测

对象：`src/tianji_kb/bazi_tiaohou.py`（1,955 行），Variant `tiaohou-qiongtong-v1`，SOURCE_ID `bazi.source.qiongtong`，SNAPSHOT_SHA256 `a8125d7de94f93d1a3eec48f1610b0c4baf31c264e9d7c19f586a85a78a2b0b4`，SNAPSHOT_BYTES 87,430。

- ENTRIES 实测 119 条，键为（日主，月支）：甲/丙/丁/戊/己/庚/辛/壬/癸各 12 条、乙 11 条；120 格中唯一无条目格为乙×丑，已登记 ABSENT_IN_SOURCE，lookup 对该格返回 status=not_applicable、reason=entry_absent_in_source，不借用他条、不报错。
- 每条字段：section（快照字符区间＋行号）、quote＋quote_locator、sequence（先取/次取干序，可为空）、order_basis、branches（已编码条件分支）、unencoded_branches（只登记不编码）、related（只提及未入序的引文）、notes。
- sequence 长度分布：0 段 3 条（丙十月、丁五月、癸五月——原文无无条件取用顺序，序列为空，如实陈述不拟制）、1 段 28 条、2 段 63 条、3 段 23 条、4 段 2 条。
- 已编码分支恰 10 条，条件形态全一：单一干「不存在」（absent_stem）——甲五月乏癸用丁及丙四条、丁二条（七月/八月同文同位点，去重后 9 条不同引文）、庚/辛/癸各一条。分支引文逐条带 locator。
- unencoded_branches 24 条（条件超出输入契约：成局、相对旺盛、程度判断、节气分界等），related 17 条。
- 包含性实测（本批新测）：119 条主引文、10 条已编码分支引文、24 条 unencoded 引文的 locator 全部落入其条目 section 跨度内（153/153）；related 17 条中 11 条在内、6 条在自身条目跨度之外（甲九月、乙七月、丙四月与五月共用一条、丁八月、丁九月——均为「同条另一段」式旁引，落在相邻讨论文本）。此 6 条的形态在 §3.3 与 §4.2 专门处置，不在本批粉饰为「全部入节」。
- 跨度实测：119 条共 109 个不同 section 跨度。共享跨度 7 个承载 17 条：己土三夏（四/五/六月）、三秋（七/八/九月）、三冬（十/十一/十二月）各 1 跨度 3 条；戊正二月合论、戊十一/十二月合论、丁八/九月（三秋总论段）、甲五/六月各 1 跨度 2 条。不同跨度间嵌套重叠 3 对：丁七月跨度含丁八/九月共享跨度、丁十一月跨度含丁十二月跨度、戊正二月共享跨度与戊三月跨度同始点交叠。相邻跨度间未被条目覆盖的缺口文本 95 处、合计 4,884 字符（讨论段、从格/妻子等非调候取用论述）。条目区为快照字符 [1300, 33066)，末条恰至书末。
- 冲突与并列口径实测：条内先次两说不一致时（如某条条首与条末专句定序不同），Variant 从条末专句定序、条首句并列登记于 related，两说并存不强行消解；季总论与分月条目先次不一致时并列登记于 order_basis/notes，不暗中合并。本模块无「文武」裁定轴；燥/湿仅为原文气候描述词（如「湿乙伤丁」「忌丙火之燥烈」），不是裁定维度，注册不得引入此类裁定。
- 执行面实测：`operations/bazi_chart.chart` 已以显式门控 kwarg `tiaohou_variant` 接入；`tiaohou_assessment(trace)` 只消费已执行的 trace 步（pillars / ten_gods / hidden_stems），要求其 evidence 已绑定，并对天干/藏干与 pillars 步逐项交叉核对，伪造或不一致一律 fail-closed；engine.execute 以 allow_research 门控。当前 assessment 附于 result、不经 trace.add、不进 RuleMatch 与 Evidence，输出 evidence_binding=`pending_phase1_rule_registration`（模块 docstring 与 LIMITATIONS 末项均明示）。恒 research_only=True、public_enabled=False、ai_enabled=False。
- 公开 Golden 在册：`tests/golden_tj0131_tiaohou.json`（schema tj0131-tiaohou-golden-v1）含 entries 119、absent_entries 1、cases 54（真实盘四柱＋source_birth），为 lookup 层既有验收资产；ENTRIES 字面量即由该文件生成。

### 1.2 快照与来源登记实测

- Source `bazi.source.qiongtong`（config/knowledge_sources.json）：C 级、kind=classical、公有领域；底本为 daizhigev20 固定快照（commit `4a6d6f2088825f132521d848c2ea86cf9c9a7620`），content_path 与模块 SNAPSHOT_PATH 同为 `data/quarantine/public_domain_snapshots/daizhigev20/qiongtong_baojian.txt`；rights_basis 明载「当前电子本为简体转写单一谱系，不据仓库许可证推断底本权利或版本权威」；review_scope 明载 TJ-013.1 逐条审定口径（字符区间＋行号逐条定位、引文逐字保留快照字形、不作简繁转换）与 Slice C 缺证登记（全书无分日表，absent_no_day_table，不补造）。
- 机上隔离区快照实测：33,066 字符、1,367 行；全书 PUA 0、缺字框 □ 0；半角标点与简体字形（如「么」「岁」用简体、「後」等个别字形保留）为转写原貌。书首结构：书名行、五行总论（字符 [6,517)，论五行之性与寒/热/燥/温生成及「过与不及皆为乖道」的总纲）、论木等分论、三春甲木总论（[1137,1293)）等各干总论散布于条目区缺口中；条目自第 22 行（字符 1300）始。
- 文本缺字一处在册：戊土正二月总论句「先丙後，癸又次之」第二位干名在快照中缺字，TJ-013.1 已审定不补字（该两条只编码丙、癸登记不入序）。此为登记文本事实，非快照 □ 字符（实测 □ 为 0，二者不得混同）。

### 1.3 Canonical 实体结构全样本（五经典）

机上直读现行密封 phase1_knowledge.json / phase2_execution.json（钉 380bb73e…）：

- 计数：经典 5 部、章 33、节 74（最大 s074）、术语 38、Phase1 规则 41（最大 r041）、概念 18；Phase2 步 42。
- 经典五部：`bazi.classic.yuanhai`（body_stage=canonical）、`bazi.classic.ditiansui`（canonical）、`bazi.classic.sanming_tonghui`（quarantine，另带 source_ids 数组为其 S0＋应用文本双源特例）、`bazi.classic.xieji`（quarantine）、`bazi.classic.shenfeng`（quarantine，E0348 新建）。classic 实体字段恰 {id, domain, name, source_id, body_stage}（三命的 source_ids 为双源特例字段）。
- chapter 实体字段 {id, domain, name, classic_id, locator}，locator 为描述性字符串。section 实体字段 {id, domain, name, classic_id, chapter_id, source_id, locator, text, review{status, method, scope}}；review.status 均为 approved。term 实体字段 {id, domain, name, aliases, definition, source_refs, attributes, confidence, related_terms}；rule 实体字段 {id, domain, name, variant, school, conditions, inputs, operation, result, exceptions, difference, confidence, execution_status, term_refs, source_refs}；rule.variant 均为 bundle 变体 `ziping-structural-v1`，school 形如「子平·神峰通考（病药说）」。
- 两条全域不变量（实测分布）：41 条规则 term_refs 长度分布 {1: 29, 2: 5, 3: 6, 7: 1}——每条规则至少 1 个 term_ref；38 条术语 source_refs 长度最小 1——每条术语至少 1 条入节 refs。此二项是 §4.1 术语定稿的驱动事实。
- Phase2 步字段 {id, domain, name, variant, phase1_rule_refs, execution_status, validation_status, golden_case_ids, regression_test, evidence_scope}；phase1_rule_refs 长度分布 {1: 40, 2: 2}（多 refs 步有先例：annual_reference_facts、annual_li_chun_boundaries 各 2 条）。
- harness 契约实测（`src/tianji_kb/golden.py` run_cases）：provider 三重钉死（golden 文件 provider == engine PROVIDERS == phase2 contract provider）＋ `function(**case['input'])` 调用；bazi provider 即 `operations.bazi_chart.chart`，其签名已含 `tiaohou_variant=None` 门控参数——本 Variant 的 Golden 输入通道已在契约内，无需任何扩展（与 ren/dayun 神峰两批须扩 provider 签名者不同，此点在 §4.3 定稿）。

### 1.4 注册五条件逐项映射现状

翻转五条件（沿 E0333 起各批在册口径：本地四项＋第五项终局条件）：

| 条件 | 现状 | 实测依据 |
|---|---|---|
| 一、真实执行接入 | **已满足** | chart 门控 kwarg 已在、assessment 消费已执行且证据绑定的 trace 步、交叉核对 fail-closed（§1.1） |
| 二、Trace 真实步 | 未满足 | assessment 附于 result、无 trace 步、不进 RuleMatch/Evidence（模块 docstring 明示） |
| 三、EvidenceResolver 实测绑定 | 未满足 | 无穷通经典/章/节，119 条无 section 可绑，治理行 reason_class=canonical_evidence_absent |
| 四、Golden 与规定测试全过 | 部分满足 | lookup 层公开 Golden 54 例在册且 ENTRIES 由其生成；Phase2 Golden 为 0（无步可 fire） |
| 五、正式验收与部署验证 | 终局条件 | 按各批先例于实施批合并后由父级关账复核，PR 内翻转视为待终局确认 |

治理行现状（`bazi_registration_governance.py` REGISTRATION_INVENTORY）：tiaohou-qiongtong-v1 为 maintained_pending / canonical_evidence_absent；其 reason 文本仍枚举「四书」（渊海/三命/协纪/滴天髓），E0348 神峰建成后已为五书——该枚举属翻转时随 reason 整体改写消解的陈旧表述（各批翻转均整体重写 reason），本批不单独改行（只设计），在 §6.2 列为翻转清单项以免遗漏。治理维持名单现为 4 项（tiaohou、siling-yin-pilot、dayun-compose、dayun-timeline-view）。

## 2 经典建制形态定稿

### 2.1 经典实体（沿神峰镜像，偏离清单）

定稿（D-T0）：新建经典实体 `bazi.classic.qiongtong`，字段与既有经典逐项同形——{id=`bazi.classic.qiongtong`, domain=`bazi`, name=《穷通宝鉴》, source_id=`bazi.source.qiongtong`, body_stage=`quarantine`}，不带 source_ids（穷通为单一来源，与神峰同形；三命的 source_ids 系其 S0＋应用文本双源特例，不类推）。

body_stage 取 quarantine 的理由（与神峰 §2.2 同口径）：yuanhai/ditiansui 取 canonical 是因其另有清洗定本；穷通的 Canonical 在场形态只能是隔离快照原文的节级切片、无独立清洗定本，与三命/协纪/神峰三例同形态，取 quarantine，不冒充定本。

与神峰先例的偏离清单（逐项）：
- 偏离一（规模）：神峰建节 4 处、建章 4；穷通建节 110 处、建章 11（§3）。此为消费面规模的事实差异（病药消费面为两节、日级换算一节；调候消费面为全书分月条目），非机制偏离——实体字段、review 三字段、locator 口径、逐字切片口径全部同形。
- 偏离二（文本来源形态）：神峰/三命建节文本或为快照切片、或为正式应用文本 S3 切片；穷通无应用文本阶段（未做 018 式多底本校勘与正式应用），建节文本一律为隔离快照原文切片。此偏离由 §2.2 底本口径承载，不另设文本阶段。
- 偏离三（术语锚节）：神峰术语的 refs 落在其消费节内；穷通术语的定义锚须落在非条目文本（五行总论），故多建 1 节总论锚节（§3.1、§4.1）。此为 §1.3 两条不变量驱动的最小增量，边界在 §3.3 钉死。
- 其余无偏离：经典准入沿「来源已登记＋快照钉值在册＋消费引文逐条审定」三件套（穷通三件均已在册，见 §1.2），不新造任何机制。

### 2.2 底本口径审定（D-T1）

审定：穷通建节文本以钉定快照逐字切片为准——简体转写字形、半角标点、异形字（如癸水二月条首「二月葵水」之葵）一律按快照原样，不作简繁转换、不作字形规范化、不补缺字；每节 review.scope 必须逐字披露：单一电子谱系（daizhigev20）、简体转写、C 级、未做多底本校勘、引文以固定快照（SHA256 钉值）为准。

理由：(一) TJ-013.1 审定早已将「引文逐字保留快照字形，不作简繁转换或改写」定为这 119 条的在册口径，ENTRIES 全部坐标以该快照为准——建制时改口径即令既有审定坐标全盘失效；(二) 同谱系先例已两次成立：神峰经典（同为 daizhigev20 单一谱系）以快照逐字切片建节、s065 以滴天髓快照原文（含快照字形）建节，均以 quarantine 阶段＋scope 披露承载，不冒充定本；(三) body_stage=quarantine 的语义正是「隔离文本节级在场」，与「已校勘定本」严格分开，登记不产生证据升级——Source 证据等级保持 C，经典建成不改变任何引文的证据等级表述。

本审定的效力边界：此为设计层裁定（审计 §5 已将底本口径明列为设计审定批议题，§2.1(d) 确认 unlock_path 无用户级裁定事项）；其性质是证据处理口径而非流派取舍。若用户在本批关账后、实施批派发前否决此口径，实施路线改走「先行 018 式多底本校勘、后建制」的长路线（见 §8 R1），本设计其余各节（粒度、绑定、翻转判据）不依赖底本口径的具体取值、可原样保留。本批不启动任何校勘。

### 2.3 章节划分定稿

定稿：共 11 章，划分原则 = 书内组织原样（总论 1 章＋十干各 1 章），章 id 沿「经典短名＋主题拼音」口径（先例 `bazi.chapter.shenfeng_bingyao`）：

- `bazi.chapter.qiongtong_zonglun`（五行总论，承载术语锚节 1 节）；
- `bazi.chapter.qiongtong_jia` / `_yi` / `_bing` / `_ding` / `_wu` / `_ji` / `_geng` / `_xin` / `_ren` / `_gui`（十干分月条目，节数依次 11/11/12/11/10/6/12/12/12/12）。

章 locator 为描述性字符串，定稿格式为「《穷通宝鉴》<章题>；快照字符 [起,止)；行 起–止」，区间与行号于实施时按快照实测填值（格式定稿、数值为测量值）。章界 = 该干全部条目跨度的最小包络（总论章为五行总论篇 [6,517)）。

## 3 建节计划定稿

### 3.1 节粒度判据与节数（D-T2）

粒度判据（定稿）：建节单位 = TJ-013.1 已审定的条目跨度（ENTRIES.section）本身，不合并、不切分。理由：注册的证据义务是 unlock_path 明文的「逐条复核引文」——绑定单位与审定单位 1:1 时，每条引文的入节包含性可逐条机检；合并为按干大节则单节达数千字且季总论与分月条目混杂、逐条复核粒度丧失；细分为按引文窗口则节数膨胀至 129 以上且与「节为篇章单位」的既有形态（s060 整篇 2,979 字、s063 整节 2,543 字）相悖。条目跨度本身即原文的条目篇章单位（每条为一完整分月条），与既有节形态同类。

节数定稿：条目节 109（= 不同跨度数实测）＋总论锚节 1 = **110 节**。id 顺延口径：现行最大 s074，新节自 s075 起按快照字符序编排——总论锚节（字符 [6,517)）为 s075，条目节按其跨度（char_start, char_end）升序编排，首节 `bazi.section.s076`、末节 `bazi.section.s184`。实施时若实测不同跨度数 ≠ 109，停工报告，不得自行调数（计数即判据，见 §6.1）。

总论锚节定稿：`bazi.section.s075`，章 qiongtong_zonglun，文本 = 快照 [6,517) 五行总论整篇（含篇题行，511 字），其唯一消费方为术语 bazi.term.tiaohou 的 source_refs（§4.1）；不入任何规则 refs、不承载任何条目。节 review.scope 须明示此定位。

每节字段定稿（镜像既有节）：name 形如「穷通宝鉴·甲木正月条」（共享节见 §3.2 命名），locator 定稿格式「隔离快照原文切片；快照字符 [起,止)；行 号」，text = 快照 [char_start, char_end) 逐字切片，source_id=`bazi.source.qiongtong`，classic_id=`bazi.classic.qiongtong`，review.status=approved、method 记 TJ-013.1 逐条审定＋实施批逐条复核、scope 逐字含 §2.2 披露口径并按 §3.2 标注共享/嵌套形态。

### 3.2 共享/嵌套跨度处置

- 共享跨度（7 个）：一跨度一节，不复制。节名以总论/合论形态命名（如「穷通宝鉴·己土三夏总论（四月至六月）」），review.scope 明示其承载的条目清单（日主＋月份）；三条条目各自绑定同节，§4.2 的 refs 恰等判据在（节，引文）对集合层面去重（己三冬三条主引文同文同位点，只成 1 条 ref，见 §4.2 计数）。
- 嵌套跨度（3 对）：各成一节，节文本各按自身跨度切片，嵌套关系在两节的 review.scope 互注。先例：s070/s072 恰幅窗口节与整节并存，节不必构成文本划分（partition）——resolver 包含性按节独立判定，嵌套不产生校验冲突。此为实测形态的如实登记，不得为求「划分整齐」而改动任一条目跨度（跨度为 TJ-013.1 审定值，只读）。
- 条目跨度与 Entries 的对应在实施批以（char_start, char_end）全等为判据逐条核对，任一条目跨度在密封侧找不到同跨度节、或节文本与快照切片不逐字相等，即整批失败（fail-hard）。

### 3.3 不建节范围

- 缺口文本（95 处、4,884 字符）与各干总论（三春甲木总论等，散布于缺口中）：不建节。理由：lookup 不消费该文本；建节的唯一依据是消费面（各批「不多建」先例）。各干总论与分月条目的先次关系已由模块侧 order_basis/notes 并列登记承载，不依赖 Canonical 节。将来若有 Variant 消费该文本，另行立批建节。
- related 6 条跨外引文（§1.1）：不为其建节、不入任何 refs。其逐字锚保持现状——钉定快照＋TJ-013.1 审定＋公开 Golden，即与今日完全相同的证据状态；治理翻转的证据主张严格限于 §4.2 的 120 条 refs，不宣称「全部登记引文入节」（见 §6.1 判据三的口径限定）。

## 4 绑定设计定稿

### 4.1 术语（不变量驱动，D-T3）

定稿：新增术语恰 1 条 `bazi.term.tiaohou`（name「调候」），10 条规则共用为 term_refs。字段镜像既有术语：definition 为平台陈述式摘要（只陈述「据月令气候寒暖燥湿、按十日主分月原文先次取用之序」的研究口径，明示不作喜用裁决、不与其他喜用体系合并——沿 zaqi 术语 definition 的自限形态）；source_refs 恰 1 条，绑总论锚节 s075 内五行总论的气候生成句（原文「北方阴极而生寒，寒生水。南方阳极而生热，热生火。东方阳散以泄而生风，风生木。西方阴止以收而生燥，燥生金。中央阴阳交而生温」所在句段，实施时以快照逐字原文与定位点实测填值），role=classical。

驱动事实：§1.3 两条不变量（规则必有 term_refs、术语必有入节 source_refs）使「无术语」与「术语无锚」两条路均不成立；十干规则同属一个方法术语，不按干拆术语（先例：同 Variant 多规则共用术语有 r038/r039 共用 dayun 术语族之外的同形处理——dayun 两规则各配一术语系其确为方向/换算两事；调候十规则为同一查表方法的十个分片，共用一术语为定稿，实施批若发现校验器另有约束须停工报告、不得自创第二术语）。

### 4.2 Phase1 规则组织（三案比较与定稿，D-T4）

候选三案：
- 甲案（全表一规则）：1 条规则绑全部 120 条 refs。否决：conditions/operation 无法承载按干分片的查表语义；单条 ref 校验失败即全表不可证，失败定位粒度丧失；与既有规则「一规则一裁定单元」的形态（最大 refs 数 17，为 bounded_strength 的条件集，与查表分片性质不同）不合。
- 乙案（逐条一规则）：109/119 条规则。否决：把数据行升格为规则实体，规则数 41 → 150+，与「规则为裁定单元、条目为数据」在册分工相悖，无任何先例；治理 S5 恰等不变量与多处计数钉的扰动与收益不成比例。
- 丙案（按干分规则，定稿）：10 条规则，每干一条，与 10 个条目章 1:1 对应。规则 id 顺延 r041 → **r042–r051**（首 `bazi.rule.r042`、末 `bazi.rule.r051`，按甲乙丙丁戊己庚辛壬癸序），name 形如「穷通宝鉴甲木分月调候」，school 统一定稿为「子平·穷通宝鉴（调候）」，variant=`ziping-structural-v1`，execution_status=executable，term_refs=[`bazi.term.tiaohou`]。conditions/inputs/operation/result 按既有规则字段形态陈述查表语义：（日主＝该干、月支）→ 条目 sequence 陈述＋存在性标注，分支条件为单一干不存在事实；exceptions 记序列为空条目与（乙规则）丑月无条目格的 not_applicable 口径。

refs 恰等判据（可否证，定稿）：对每干 s，规则 R_s 的 source_refs 集合（以（section_id, original_text）对计）**恰等于**该干全部条目的（条目节， 主引文）对与已编码分支的（条目节， 分支引文）对之并集，不多一条、不少一条，role 全为 classical。设计时点实测计数（实施时须逐条复测、不符停工）：

| 干 | 条目主引文（去重后） | 已编码分支引文（去重后） | refs 合计 |
|---|---|---|---|
| 甲 | 12 | 1 | 13 |
| 乙 | 11 | 0 | 11 |
| 丙 | 12 | 4 | 16 |
| 丁 | 12 | 1 | 13 |
| 戊 | 10 | 0 | 10 |
| 己 | 6 | 0 | 6 |
| 庚 | 12 | 1 | 13 |
| 辛 | 12 | 1 | 13 |
| 壬 | 12 | 0 | 12 |
| 癸 | 12 | 1 | 13 |
| 合计 | 111 | 9 | **120** |

去重口径：主引文按（节跨度，引文定位点）去重——119 条中共享同文同位点者（戊合论 2 组各 2 条、己三季总论 3 组各 3 条）合并为 111 个不同（节，引文）对；分支按（引文，定位点）去重——10 条中丁七月/八月同文同位点合并为 9。实施批密封测试须按条目逐条断言（119 条主引文逐条为其条目节文本的子串、10 条分支引文逐条为其条目节文本的子串），与按规则的 refs 集合恰等断言并行，二者缺一不可。

不入 refs 的引文（地位定稿）：unencoded_branches 24 条——其文本物理位于条目节内（locator 全在跨度内），地位为「入节不入 refs 的登记引文」（沿 bingyao registered_not_encoded 先例），其不编码状态由模块侧原样披露；related 17 条——11 条在节内同上，6 条在节外（§3.3），全部不入 refs，其「只提及未入序」地位由模块侧原样披露。任何实施批不得以「补全绑定」为由把此三类升格为 refs——refs 集合以本节恰等判据为唯一口径。

### 4.3 Phase2 步与执行接入（harness 契约零扩展定稿，D-T5）

定稿：新增 Phase2 步恰 1 条 `bazi.phase2.tiaohou_assessment`，phase1_rule_refs = [r042, r043, r044, r045, r046, r047, r048, r049, r050, r051]（10 条）。多 refs 步有先例（2 条上限为既往实测分布，非契约上限——字段为列表型，resolver 按步聚合校验全部所引规则）；本步 10 条为该形态的定量延伸，不改任何 schema 与机制。实施批须以专项测试钉住：resolver 对该步的 resolve 返回恰为 10 条规则的 refs 并集（120 条），且任一规则 refs 被篡改时 resolve 失败（见 §7 负例）。

执行接入定稿（沿 ren 先例的「计算后登记」形态）：chart 在既有 `tiaohou_variant` 门控内、tiaohou_assessment(trace) 计算完成后，以 trace.add 登记新步，步输出即 assessment 块，块自此进 RuleMatch 与 Evidence；门控关闭时 chart 封套逐字不变。翻转面仅限注册披露字段：assessment 输出的 evidence_binding 由 `pending_phase1_rule_registration` 改为 `registered_phase1_phase2`，LIMITATIONS 末项与模块 docstring 的未注册表述改为已注册表述（沿 zaqi 翻转的披露面清单）；ENTRIES 数据、lookup/assessment 的全部计算逻辑、sequence/presence/branches 产出逐字不动。

harness 契约扩展定稿为**零扩展**：golden.py、phase2-golden schema、engine PROVIDERS 与三重钉死逐字不动；chart 签名不动（`tiaohou_variant` kwarg 已在）；密封 Golden 用例以 input 携带既有门控字段即达步（§5）。此点与 E0344/E0346/E0348 的「provider 签名＋用例 input」扩展形态不同，差异原因是本 Variant 的门控参数先于注册批已存在——实施批不得以「沿先例」为由新增任何 chart 参数。

### 4.4 冲突与并列登记的保持

注册只绑引文，不动裁定：条内先次两说（从条末专句定序＋条首句并列于 related）、季总论与分月条目先次分歧（并列于 order_basis/notes）、戊正二月缺字不补、序列为空三条不拟制序列——全部为模块侧在册口径，绑定设计不引入任何消解机制。保持的可否证判据：实施批等价比对（§7）中，翻转前后同一真实盘的 tiaohou_assessment 块在封闭清单（仅 evidence_binding 值与注册披露句）之外逐字段全等——冲突呈现若被注册动作改动，必然在此暴露为清单外差异。调候与扶抑/病药/格局四体系分立治理为在册硬边界：本注册不产生任何跨体系合并、比较或冲突裁决，TJ-013.2 的冲突呈现层不在本设计范围内。

## 5 Golden 设计定稿（validated 证据形态，D-T6）

步的 validation_status=validated 须由密封 Phase2 Golden 真实 fire 支撑。用例形态定稿：provider 为 chart，input = {year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, tiaohou_variant: 'tiaohou-qiongtong-v1'}（四柱为真实出生时刻的真实四柱，沿 TJ-013.1 站立规则——真实日期时间经 provider 计算，严禁手编干支），expected 以 assert_subset 断言 result.tiaohou_assessment 的关键字段（status、month_label、sequence 的干与 presence、branches 的 applied、evidence_binding=registered_phase1_phase2）。用例 id 形如 `bazi.tiaohou-<slug>`。

选取判据（定稿，六组全须满足，组间重叠取并集）：
- G1 分支极性：10 条已编码分支条目，每条 ≥1 例使分支条件为真（absent_stem 在盘面不存在、分支 sequence 出现）、≥1 例为假（该干在盘面存在、分支不 applied）。任一极性经实施批在册检索仍不可构造者，按金×酉先例登记「构造性不可满足」并附检索范围与证明，不静默缺例、不造例。
- G2 缺条格：乙×丑 ≥1 例（真实乙日主丑月盘），断言 status=not_applicable、reason=entry_absent_in_source，且步仍真实 fire（轨迹含本步）。
- G3 空序列条目：丙十月、丁五月、癸五月各 ≥1 例，断言 sequence 为空、status=matched。
- G4 共享跨度：7 个共享跨度各 ≥1 例命中其任一条目（己三季总论须各有代表，合计 ≥3 例分属三季）。
- G5 十干覆盖：每干 ≥1 例（与 G1/G3/G4 并集后仍缺者补例）。
- G6 存在性三态：全集内 sequence 干的 presence 须三态齐备（visible / hidden / absent 各至少出现一次），以密封专项断言钉住。

用例来源：优先复用公开 golden_tj0131_tiaohou.json 54 例的真实四柱（其 pillars 与 source_birth 在册）中满足判据者；不足者以真实出生时刻新算四柱补之，并在实施记录中逐例注明来源。用例总数为判据并集的测量值（预计 25–35 例），于实施批记录中钉定；判据本身在本批定稿，不留实施批裁量。

与 Golden 并行的穷举绑定测试（定稿为实施批必备密封专项，非 Golden 用例）：对 119 条逐条断言主引文为其条目节文本的逐字子串、10 条分支引文同上、§4.2 refs 集合恰等、步的 golden_case_ids 与新增用例集恰等。此测试是条件三（§6.1）的主要机检载体。

## 6 注册翻转判据定稿

### 6.1 五条件可机检判据

| 条件 | 可机检判据（实施批全须通过，任一失败即不得翻转） |
|---|---|
| 一、真实执行接入 | 既有门控路径不变：chart 以 tiaohou_variant 门控执行 assessment 并交叉核对 fail-closed（既有公开/密封测试全过）；本批实施零新增公开面、零新增 chart 参数（git diff 可检） |
| 二、Trace 真实步 | 门控开启的真实盘执行轨迹中 `bazi.phase2.tiaohou_assessment` 恰出现 1 次且其输出与 result.tiaohou_assessment 块全等、进 RuleMatch 与 Evidence；门控关闭时封套与基线逐字一致 |
| 三、EvidenceResolver 实测绑定 | resolver.resolve 对 r042–r051 逐条成功且 refs 集合与 §4.2 恰等判据全等（120 条）；对步 resolve 成功且为 10 规则 refs 并集；§5 穷举绑定测试 119＋10 逐条子串断言全过；伪造负例（§7）全被拒。口径限定：本判据主张的绑定面恰为 120 条 refs，不含 unencoded/related（§4.2 地位定稿） |
| 四、Golden 与规定测试全过 | §5 判据 G1–G6 的密封 Golden 全例经 run_cases 真实 fire 本步；公开 golden_tj0131 54 例与 tiaohou 既有测试全过且 ENTRIES 逐字未动；机上全配方复跑 SUCCESS 0 失败（基线为届时正式验收数，增量逐项对平） |
| 五、正式验收与部署验证 | 终局条件：实施批 Merge SHA 的管线正式验收 SUCCESS 且已部署（父级关账直读），PR 内翻转按各批先例视为待终局确认 |

### 6.2 治理行翻转形态

实施批翻转形态定稿（沿各批先例）：REGISTRATION_INVENTORY 中 tiaohou-qiongtong-v1 行——disposition 改 registered、删除 reason_class、phase1_rule_id=`bazi.rule.r042`、additional_phase1_rule_ids=[r043..r051]、phase2_rule_id=`bazi.phase2.tiaohou_assessment`、reason 整体重写（明载经典/章/节/术语/规则/步/Golden 实体与本设计 D-T1 至 D-T6 的执行结果；顺带消解 §1.4 的「四书」陈旧枚举——翻转后 Canonical 为六书）、unlock_path 改 None。模块侧披露翻转面见 §4.3。治理维持名单 4 → 3（余 siling-yin-pilot 与 dayun 两 inherited 行）。翻转记录沿 GOVERNANCE_*_RECORD 形态入治理册（字段含 canonical_classics_added 等全套，snapshot 前后三元组与 sealed 变更文件 sha256 表）。

### 6.3 S5 不变量与计数钉影响面清单

实施批动密封数据，下列在册钉面必然受影响，须逐项按同口径迁移（只许随实体增量等值迁移，禁止放宽断言本体；E0348 已实证此类清单的必要性）：

- 密封计数：经典 5→6、章 33→44、节 74→184、术语 38→39、Phase1 规则 41→51、Phase2 步 42→43、Golden 180→180＋N（N 为 §5 用例并集测量值）。
- 合化 SEALED_MEASUREMENTS 三总数（节/规则/步）及其 golden 镜像——新节须经实测不含合化关键词与「五合」后按总数迁移（沿 E0346/E0348 口径）；phase1 可执行规则集补 r042–r051。
- S5 治理公开测试与历批治理公开测试钉着的 FLIPPED/MAINTAINED 全局集合（tiaohou 入 FLIPPED、MAINTAINED 4→3），逐文件以「E035x 注释链」迁移（沿 E0344 对 zaqi 测试、E0348 对历批测试的迁移先例）。
- product coverage 两文件（data/coverage/phase1.json、data/product/knowledge_coverage.json）以最终代码重生；密封变更文件集预期恰 5 件（phase1_knowledge、phase2_execution、phase2_golden、coverage/phase1、product/knowledge_coverage），与 zaqi/神峰两批同形。
- 快照三元组：文件数 237 预期不变、字节数增长、manifest 轮换；换代沿父级先行口径（备份→暂存换入→diff -r 核对→cicd 钉→再合并），本设计不改变该流程。

## 7 实施批切分与硬验收清单

切分定稿：**单一实施批**（＋随行关账批）。理由：经典/章/节/术语/规则/步/Golden/翻转是一个原子注册——任一中间状态（有节无步、有步无 Golden）都违反 §6.1 判据的整体性，各批先例（zaqi/ren/dayun 三命/神峰）均以单批完成同类注册。与 dayun 分两阶段（先登记后建节）的差异理由：dayun 的《论大运》从未经过 018 形制登记、须先补登记；tiaohou 的 119 条已经 TJ-013.1 逐条审定（字符区间＋行号＋引文逐字，E0199 全关账），登记层等价物已存在——unlock_path 的「逐条复核引文」在实施批内以 §5 穷举绑定测试与逐节文本逐字比对完成，属复核而非首登，不另立登记批。实施批事件号与关账号由父级派发时中央分配（本批关账预留 E0351，与实施批无关）。

实施批硬验收清单（全须满足）：
1. 密封著录：经典 1、章 11、节 110、术语 1、规则 10、步 1，与本设计 §2–§4 的 id/计数逐项对平；每节文本与快照切片逐字相等、节内 PUA/□ 为 0（全书基线已实测为 0，任一节出现即失败）。
2. 绑定：§4.2 refs 恰等（120 条）＋§5 穷举绑定测试全过；术语 refs 恰 1 条入 s075。
3. Golden：§5 判据 G1–G6 全满足且全例真实 fire；用例四柱全部可溯源至真实出生时刻。
4. 等价比对：比对集 = 公开 golden 54 例之盘＋密封 Golden 新例之盘＋120 格逐格真实盘枚举集（以在册检索范围逐格命中真实盘；检索口径与范围在实施记录中写明，未命中格如实登记、不得手编）——翻转前后 tiaohou_assessment 块与 chart 全封套在封闭清单（evidence_binding 值、LIMITATIONS 与 docstring 注册句、治理披露字段、新步的 trace/RuleMatch/Evidence 增量）之外逐字段全等，计算值零差异；门控关闭面逐字一致。
5. 伪造负例：条目引文改字一条、引文错绑他干之节一条、分支引文冒充主引文一条、总论锚句改字一条，均被 EvidenceResolver 拒绝。
6. 回滚演练：新代码＋旧快照（380bb73e…）下门控路径以 Unknown rule `bazi.phase2.tiaohou_assessment` fail-closed；默认面与基线逐字一致。
7. 全配方复跑 SUCCESS 0 失败且增量对平；公开 CI 全绿；台账门禁 plain＋--base 双模式 PASS。
8. 暂存快照＋换代清单交付父级（实施批不动 live 与 cicd 钉，沿各批先例）。

## 8 风险、未决项与用户裁定界限

- R1 底本口径（§2.2，D-T1）：本设计已按审计授权审定逐字口径；此为全设计唯一一处若被否决则改变实施路线的判断——否决的后果是实施改走「先行多底本校勘」长路线，周期与工作量数量级上升，且在校勘完成前 tiaohou 维持 pending。本批明示此点，不以「审计无用户裁定事项」为由隐匿。
- R2 步的 refs 规模：单步phase1_rule_refs=10 为既往分布（最大 2）的定量延伸。若实施时发现 harness/resolver 存在未登记的 refs 数量假设，停工报告并回本设计修订，不得私自改拆步或拆规则。
- R3 110 节为平台单批最大建节量：风险在机械面（计数钉遗漏、coverage 重生时序），已由 §6.3 清单与 §7 第 1/7 项对冲；文本面风险低（全书 PUA/□ 为 0、无缺口字、无校勘未决项落入条目区）。
- R4 嵌套节的人读误读：3 对嵌套节可能被误读为文本划分错误——以 §3.2 的 scope 互注与本节登记对冲；校验语义不受影响。
- R5 单一见证的学术风险：穷通全部引文只锚定一个电子谱系。注册不冻结学术：将来出现独立见证且读法冲突时，按平台 append-only 惯例以新事件/新登记处置，不回改本批著录。此风险由 C 级与 quarantine 阶段如实承载，不构成本批未决项。
- 未决项清点：无须用户裁定项（审计 §2.1(d) 已确认）；无实施批可自行裁量项——§5 用例总数与各节 locator 数值属测量值（判据已定稿），非裁量。siling 扩月/约定转正与扶抑 U1/U3 不在本设计视野内，本批未代决、未夹带。

## 9 本批产出与未实施声明

- 产出：本设计文档（docs/product/TIAOHOU_CANONICAL_DESIGN.md）；治理册设计记录 TIAOHOU_DESIGN_RECORD（置于 `bazi_registration_governance.py`，沿 GOVERNANCE_*_RECORD 形态——取此形态而非 TJ-018.3 式独立登记册模块的理由：彼册为文本生产管线的机器消费登记（钉值/fail-hard 编号供执行批程序读取），本设计的消费方为治理测试与实施批任务书，全部批次记录自 E0333 起均居治理册内，一致性优先）；公开治理测试 tests/test_governance_tiaohou_design_public.py（只钉三件事：设计记录在册且状态为未实施、tiaohou 行仍 maintained_pending、设计文档在册且关键定稿标识齐备）并按名接入 validate.yml；台账事件 E0350 与 TASK_STATUS TJ-018.2 行续写。
- 未实施声明：tiaohou-qiongtong-v1 仍为 maintained_pending / canonical_evidence_absent；`bazi_tiaohou.py` 的 ENTRIES、lookup/assessment 逻辑与全部披露字段逐字未动；密封资产、快照与 cicd 钉未动；本设计的一切 id（bazi.classic.qiongtong、s075–s184、r042–r051、bazi.phase2.tiaohou_assessment 等）均为拟用标识，不构成任何实体存在的主张。

## 10 设计修订（E0351，append-only 补记）

本章为设计修订记录，置于 §9 之后：§0–§9 原文一字未改；本章与原文不一致处以本章为准，覆盖关系逐项指明于 §10.4。本章同样严格只修订设计、不实施：不建任何 Canonical 实体、不写任何绑定、不翻转任何注册状态、不改动任何执行代码与密封资产。

### 10.1 停工事实与冲突证据

- 停工事实：父级派发的 tiaohou 实施批在阶段一复核（119 条逐条对 §3、§4.2 复核）中停工，未建分支/PR、未改动任何代码与密封资产、未动 live 快照与 cicd 钉。停工时点（2026-10-31T22:49Z）管线对设计合并 `e2900875` 的正式验收尚未落地（合并后约 8 分钟，尚在管线周期内，非异常）。
- 复核通过面（本批以停工批脚本 review_stage1.py 复跑抽核，结论逐项一致）：119 条键唯一、109 个不同跨度、153 个定位点（主引文 119＋已编码分支 10＋unencoded 24）全入自身跨度且逐字切片相等、行号全对、related 17＝11 入跨度＋6 跨外、共享跨度 7 个承载 17 条、嵌套/同始关系 3 对与 §1.1 一致、逐干跨度数与 §2.3 章节表全合、sequence 长度分布与空序列 3 条（丙十月、丁五月、癸五月）全合、锚节 [6,517) 511 字与气候生成句 [33,98) 逐字在位、快照 87,430 字节且 SHA256 `a8125d7d…` 与模块钉值一致（33,066 字符、PUA 0、缺字框 □ 0）。脚本输出的三处 FAIL 行即下述冲突（1 处）与 §10.5 两项口径注记（2 处），无其他不符。
- 冲突证据：丙×卯条目跨度 [8668,9025)（快照行 194 起）。按 D-T2 以整跨度逐字建节时，节文本在快照字符 8863 处含「化格」：所在句「或丙子日辛卯时,乃从化格,但不逢时贪才坏印,难招祖业。」系以具体日时（丙子日辛卯时）立论的命例讨论句，非该条主引文（主引文 [8668,8711)，干净），亦非该条任何 refs 引文（该条 refs 为主引文与已编码分支引文 [8712,8739)，均在条目首两行）。
- 全量扫描：拟建 110 节文本 × 六关键词（化气/合化/化象/真化/化格/五合）仅此 1 处命中；现行 74 节实测零命中（「五合」仅 s010 在册，与本冲突无关）。
- 不变量出处：密封测试 `tests/test_tj0123_hehua_fact_sealed.py` 的 Phase1PinsTest::test_section_keyword_scan 对 bundle 每一节断言关键词不出现于 text＋name，并断言 SEALED_MEASUREMENTS['phase1_sections_with_hehua_keywords'] == 0；按设计建节后该测试必在丙二月条新节上失败。设计 §6.3 的计数钉迁移以「新节须经实测不含合化关键词与五合」为前提——该前提对 109/110 节成立、恰对本节不成立；§3.1 的停工判据只覆盖跨度数 ≠ 109，§7 第 1 项 fail-hard 只覆盖 PUA/□，对本情形无处置定稿。冲突的任何解法（改节跨度、改不变量断言、剔除该节）都属改设计或改他人治理线断言，实施批按任务书停工待裁。

### 10.2 裁定：解法 A（窗口节）与备选处置

- 父级裁定采解法 A：丙×卯条改以窗口节承载（定稿见 §10.3）。理由：对合化不变量零改动；对 §4.2 refs 恰等判据（丙 16 条、合计 120 条）零扰动；窗口节有 s070（见证窗口、引文恰幅）、s072（正官格张力窗口）、s074（滴天髓中和篇制衡窗口）三处在册先例；且不触碰合化线审定实质——化气成立（P-D1）仍未裁定，本修订只处理节文本承载形态，被排除的命例句本就不属该条 refs 引文，其登记地位不因本修订改变。
- 解法 B（整节保留＋将合化不变量勘订为计数钉＋唯一具名例外）：不取。须变更合化治理线自身的断言形态与 SEALED_MEASUREMENTS 及其 golden 镜像，属合化线审定事项，不能由 tiaohou 实施线顺带为之。
- 解法 C（丙二月条不建节、其引文不入 refs）：不取。直接违反 §4.2 refs 恰等（丙 16、总 120）与 §6.1 条件三，翻转判据整体失效。

### 10.3 窗口定稿（丙×卯节，拟用 bazi.section.s099）

- 对象与 id：丙×卯条目节拟用 id 为 `bazi.section.s099`——按 §3.1「条目节按跨度 (char_start, char_end) 升序」编排，该跨度居第 24 位。本修订只改其 char_end（9025→8852），char_start 8668 不变，排序与 id 不变；丙章 `bazi.chapter.qiongtong_bing` 节数仍 12，章包络 [8169,11598) 不变（窗口终点 8852 在包络之内，非章界决定位点）。
- 窗口坐标：[8668,8852)，184 字，快照行 194–197。
- 窗口全文（逐字，标点为快照原样）：
  - 行 194：「二月丙火,阳气舒升,端用壬水,壬透天干,不见丁化,加以庚辛已亦透,壬水有根,定主科甲。」
  - 行 195：「或无壬水,己土姑用,主有才学,虽不能成名,必衣食充足。」
  - 行 196：「或一派壬水,见一戊制,虽不科甲,亦有恩庇。或无戊透,则有辰戌丑未之戊,但辰宫癸水,贪合成火,不能制壬,此平常衣禄。若支下全无一戊,此系奔流之人,加以金多生水,下贱之命。」
  - 行 197：「或一派戊土,亦用壬水,运喜行木,见土不祥,行火亦不利。」
- 边界句：起界句 = 窗口首句「二月丙火,阳气舒升,端用壬水,壬透天干,不见丁化,加以庚辛已亦透,壬水有根,定主科甲。」（与主引文全等、主引文居节首）；止界句 = 窗口末句「或一派戊土,亦用壬水,运喜行木,见土不祥,行火亦不利。」。窗口后一字符（8852）为换行符，排除段自 8853 起，首句「或丙子日辛卯时,乃从化格,但不逢时贪才坏印,难招祖业。」。
- 包含判据（实测）：主引文 [8668,8711) 与已编码分支引文（id `eryue_wu_ren_gu_yong_ji`）[8712,8739) 全入窗口；该条定义性文本（端用壬水的一般性论述：主引文、分支引文、行 196 一派壬水段、行 197 一派戊土段）全入；六关键词（化气/合化/化象/真化/化格/五合）逐字扫描窗口零命中。
- 排除段登记：[8853,9025)，172 字，构成——命例行 [8853,8981)（「或丙子日辛卯时,乃从化格,…或支成木局,反因奸得才,因酒得名。」）、[8982,8992)「凡用壬者,金妻水子。」、命例盘表 [8993,9025)（「时日月年」题行与两例四柱排表及空格行）。登记为未建节文本，沿 §3.3 口径：该段不含任何 refs 引文、lookup 不以节形态消费之，其逐字锚保持现状（钉定快照＋TJ-013.1 审定＋公开 Golden），不宣称入节。其中「凡用壬者,金妻水子。」为六亲映射语、非调候取用陈述，本不入消费面。
- refs 处置：该条 2 条 refs（主引文＋分支引文）改绑 s099（窗口节），（节，引文）对集合内容不变；丙干 refs 仍 16 条、十干合计仍 120 条，§4.2 计数表逐项不变。
- 节字段补记：name 定稿为「穷通宝鉴·丙火二月条（窗口节）」（name 同受关键词扫描，实测不含六关键词）；locator 记窗口坐标并注原条目跨度；review.scope 须明示窗口形态、原条目跨度 [8668,9025)、窗口 [8668,8852)、排除段 [8853,9025) 的登记与本章出处。

### 10.4 对既有定稿的逐项覆盖关系（原文不改、以下为准）

- D-T2/§3.1（粒度判据）：「建节单位 = 条目跨度本身，不合并、不切分」修订为：原则不变，增设唯一例外——条目跨度内含密封全域不变量（合化节关键词扫描）禁止文本、且命中点不在该条任何 refs 引文内时，该条改以窗口节承载；窗口 = 完整包含该条全部 refs 引文与定义性文本、且不含命中句段的、行界对齐的区间。本例外现时只适用丙×卯一节；实施批全量扫描若另有命中，按同一判据逐节处置并登记，不得扩大解释为一般切分许可。节数仍 110、id 顺延仍 s075–s184。
- §3.2（跨度全等判据）：修订为：109 个条目节中 108 节与条目跨度全等；s099 以窗口跨度 [8668,8852) 对应条目跨度 [8668,9025)，其判据改读为「窗口坐标与 §10.3 定稿逐字相等、节文本与快照 [8668,8852) 切片逐字相等、该条全部 refs 引文入窗口」。共享/嵌套跨度处置不变。
- §5（穷举绑定测试）：对丙×卯条的判据改读为：主引文与分支引文为 s099 窗口节文本的逐字子串；其余 118 条照原文。G1–G6 选取判据不变。
- §6.3（合化计数钉迁移前提）：「新节须经实测不含合化关键词与五合」修订为：110 节逐节实测扫描（text＋name）零命中后方可按总数迁移；s099 的零命中由 §10.3 窗口定稿达成（原跨度 1 处命中已由排除段登记承载）。SEALED_MEASUREMENTS 与 phase1_sections_with_hehua_keywords == 0 的断言本体不作任何勘订。
- §7（硬验收清单）：第 1 项增补 fail-hard——s099 节文本与快照 [8668,8852) 切片逐字相等、且 110 节全量关键词扫描（text＋name × 六关键词）零命中，任一节命中即整批失败（与 PUA/□ 同级）。其余各项不变。
- 不受影响（逐字不变）：D-T1 底本口径、D-T3 术语、D-T4 规则组织与 §4.2 refs 计数表（丙 16、合计 120）、D-T5 步形态与 harness 零扩展、D-T6 与 §5 选取判据、§2 章节划分（11 章与各章节数）、§6.1 五条件判据、§6.2 翻转形态、§8 风险清点。

### 10.5 两项测量口径订正与填值注记

- (i) 未消费缺口字数：§1.1「合计 4,884 字符」与 §3.3「95 处、4,884 字符」为相邻跨度朴素求和口径。本批以并集覆盖实测：95 处、合计 4,744 字符；差 140 恰为 3 对嵌套/同始跨度的重叠量。订正为并集口径 4,744 字符并保留两口径注记；§3.3 不建节决策在两口径下相同，不受影响。
- (ii) 丁分支绑定填值注记：丁×申与丁×酉的已编码分支引文同文同位点——「七八月或无甲木,乙亦可用,为枯草引灯,郤不离丙晒也」[13510,13535)（快照行 458），按 §4.2 分支去重口径（（引文，定位点）去重）合成 1 条 ref。实施填值定注：该 ref 绑其文本所在的丁×酉/戌共享跨度 (13476,13592) 之节（该位点同在丁×申跨度 (13377,13732) 内，绑共享节使（节，引文）对唯一）；丁干 refs 仍 13 条、合计仍 120 条。阶段一脚本以「分支按条目自身跨度绑定」的朴素口径计得丁 14 条、合计 121 条，与设计口径之差恰为此 1 条，非计数错误，特此注记以免实施批误读。

### 10.6 事件号再分配与后续

- 事件号经父级中央再分配：设计批（E0350）不另立关账事件（沿设计批先例）；实施批原拟号 E0351 由停工事实与本修订同批占用（本事件 E0351）；实施批顺延 **E0352**、其关账 **E0353**。§7「本批关账预留 E0351」与 §9 中相关表述，以本节为准。
- 后续：实施批 E0352 按 §0–§9 原设计＋本章修订执行；§8 R1 的用户否决窗口（实施批派发前）不因本修订改变。本修订未翻转任何注册、未建任何实体、未动 ENTRIES 与执行代码与密封资产与快照与 cicd 钉。
