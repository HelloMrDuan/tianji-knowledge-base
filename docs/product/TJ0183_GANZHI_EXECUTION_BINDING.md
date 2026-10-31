# TJ-018.3 批二执行绑定：卷二干支三规则实施记录（E0335）

## 0. 授权与范围

- 授权链：用户 2026-10-30 锁定实施顺序（执行绑定设计批 → 批一三刑 →
  批二干支三规则 → 批三阳刃重新评估），2026-10-31 明示启动批二；
  规范依据 = TJ0183_P2_GANZHI_ADJUDICATION.md（P2 审定）全文、
  TJ0183_EXECUTION_BINDING_DESIGN.md §§0–7、批一 E0333 已验证机制。
- 范围：卷二干支两节（《论天干阴阳生死》《论五行旺相休囚死并寄生
  十二宫》）建密封 Canonical 节；三谓词 lu_visible_support（丙×巳）、
  pure_support_metal（金×酉）、pure_generating_support_water（水×子）
  各建 Phase1 规则与 Phase2 规则步并翻转治理登记；裁决出口由
  r026 gate 步披露改为经各自新步发出，逐盘等价为验收对象。
- 不在范围：批三阳刃、扶抑 U1/U3、丁谓词、长生冲突（丁/辛/癸/土）
  的任何处置、三谓词以外的规则与判定逻辑。B2/B4/B5 与 concept
  口径逐字不变。用户可见能力变化仅限翻转谓词的研究层披露字段。

## 1. 晋级五问答复

1. 实际建立哪些 Canonical 实体：新章 2（bazi.chapter.
   sanming_tianganshengsi、bazi.chapter.sanming_wangxiangjisheng）、
   新节 2（bazi.section.s061《论天干阴阳生死》、bazi.section.s062
   《论五行旺相休囚死并寄生十二宫》，文本为 S3 工作本口径、零 PUA）、
   Phase1 规则 3（bazi.rule.r032/r033/r034）、Phase2 规则步 3
   （bazi.phase2.strength_lu_visible_support、bazi.phase2.
   strength_pure_support_metal、bazi.phase2.
   strength_pure_generating_support_water）、Golden 4 例（lu 正例、
   water 正例各 1，metal 负例见证 2）。
2. 哪些 pending 注册被真实解除：治理登记三行（lu/metal/water
   bounded-strength 谓词）由 pending_phase1_rule_registration
   翻转为 registered，sufficient_rule 改指各自新步；
   FORM_BING_SI 的 evidence_binding 由 pending 翻转为
   registered_phase1_phase2（规则 bazi.rule.r032、步 bazi.phase2.
   strength_lu_visible_support）；S5 清单翻转集 3 → 6、维持集
   12 → 9。
3. 哪些依赖因此具备下一阶段条件：三谓词成为已注册可执行规则，
   其裁决自本批起经注册步发出并携带注册证据链（扶抑与格局用神
   审定的上游事实之一就位）；metal 步以 validation_status=
   pending 在册（见 §5），其等价断言与不可满足证明在册，
   validated 状态构造性不可达、不作承诺。扶抑 U1/U3 仍为用户
   暂缓事项，TJ-013.1 不因本批解锁。
4. 用户可见能力是否实际变化：否。公开投影逐字不变；
   research_only=true、public=false、ai=false 姿态不变；变化
   仅为研究层裁决披露（sufficient_rule 指向、matched_rule_ids、
   limitations 注册状态句与新步证据）。
5. 下一步确定前置：扶抑最小切片仍待用户对 U1/U3 的裁定；
   批三阳刃重新评估待卷三禄节前置登记与用户授权。

## 2. 逐谓词翻转结论表

| 谓词 | Phase1 | Phase2 步 | validation | Golden 形态 | 翻转 |
|---|---|---|---|---|---|
| 丙×巳 lu_visible_support | bazi.rule.r032 | bazi.phase2.strength_lu_visible_support | validated | 正例 1（harness fire） | registered |
| 金×酉 pure_support_metal | bazi.rule.r033 | bazi.phase2.strength_pure_support_metal | pending（见 §5） | 负例见证集 2（等价断言） | registered |
| 水×子 pure_generating_support_water | bazi.rule.r034 | bazi.phase2.strength_pure_generating_support_water | validated | 正例 1（harness fire） | registered |

三谓词逐条独立满足自身条件（定义锚绑定、Golden/等价、注册
契约）后翻转，无捆绑成败。丙×巳的滴天髓侧锚经本批内另核可绑
（s048 从强句与「绝无一毫财星官杀之气」句、s047 从旺句、
s026 根框架句、s004 藏遁歌巳段，逐字在 Canonical）；
dt.bing_lu_single「丙禄居巳」不在 Canonical，仅作互证锚、
不绑定、不阻断。

## 3. 密封著录明细

- 节界（S3 坐标）：s061 = S3 [38891,43082)、4191 字；s062 =
  S3 [54894,55672)、778 字；两节零 PUA，与 S0 坐标经 603 条校勘
  应用复放换算（全书唯一净位移 ocr-017 在两节之间、节一因此
  +1）。22 条登记引文的 S3 形与登记原文逐字一致。
- 规则壳与 r029/r030 同构（operation=bounded_strength_
  adjudication、variant=ziping-structural-v1、confidence=
  medium、任氏有限充分条件口径）；source_refs 逐条在新节或
  既有节文本内逐字验证。
- 帝旺代偿等级：金×酉帝旺（酉）、水×子帝旺（子）为推步得出，
  注册定稿措辞逐字为「帝旺位（推步）：本位无逐干逐字句，系由
  该干逐干明句之长生位 + 《论五行旺相休囚死并寄生十二宫》
  十二宫次序 + 阴阳顺逆推步得出，证据等级 framework_derived
  （推论级），与 per_stem_listed（逐干明句级）分级并列、永不
  混同。」；S1 六条 forbidden_phrasings 与火线两条禁用表述
  落密封测试断言、全注册文本零命中。
- 丁隔离（绑定层）：三规则 source_refs 与 {sm2.ding_sheng,
  sm2.ding_shengsi} 交集为空（机检断言）；DING_BLOCK、
  DING_SI/YIN_DISPOSITION 的 blocked_by_conflict 登记逐字
  不变（回归断言）；丁/辛/癸三 conflict 记录随 s061 scope
  元数据逐字携带。
- □1 排除三断言：(a) 绑定引文不覆盖 S0 42148（S0/S3 坐标
  各跑一次），lunyue_summary 尾段 [42116,42151) 整段排除；
  (b) 伪绑定引文（覆盖 42148）被 EvidenceResolver 拒绝
  （负例实测，含「谬误甚矣」伪引文）；(c) 缺口 sm2-gap-42148
  disposition=unresolved 在册。

## 4. 等价比对

- 比对集：密封 phase2_golden 全部 129 例柱面输入 + F34
  Golden 7 例 + S2 Golden 7 例 = 143 盘（新 Golden 4 例为
  新增、不在比对集）。
- 方法：旧代码+旧快照 与 新代码+暂存快照 两组装各跑
  operations/bazi_chart.chart 全封套（result、trace 步序、
  步输出、evidence 图），按设计 §7.1 逐字段比对，fact_ref
  以所指步内容规范化后深比对；仅允许 §7.2 封闭清单变化
  （why.sufficient_rule 落步 ID、sufficient_predicate 与
  predicate_rule_registration 两键移除、matched_rule_ids
  新增步 ID、trace 新增步及其证据——新步证据归属逐条断言
  落在三新规则 source_refs 所属章节内、limitations 注册
  状态句、治理 disposition）。
- 结论：143 盘在封闭清单外零差异；lu 与 water 见证盘经
  新步 fire 且裁定内容与 r026 出口逐字一致；metal 在全部
  143 盘不 fire（构造性，见 §5）。

## 5. 金×酉 Golden 定稿口径与偏离记录

- 父级审定定稿：该规则照常注册，golden_case_ids 指向其
  负例见证集；密封注册测试以「新步与 r026 出口在见证集上
  等价 + 正例构造性不可满足证明在册」断言执行，不入
  harness 正例 fire 通道，不得伪造或要求真实盘正例。
- 不可满足证明（在册）：S2 批（E0263 在册）已以三条证明
  通道登记该形态在真实盘上构造性不可满足——因子层该形态
  各项条件可同时为真，唯 all_visible_have_registered_roots
  一条被在册的土根缺口阻断（土透干在密封根政策与 S1 登记
  中均无已定根集）；全域扫描复证其在盘面层从不 fire。
  本批密封测试复跑同一结论：161 例 Golden 全集内该步
  零 fire、两负例见证盘恒 indeterminate。
- 与设计 §3.4 的一处偏离：设计原拟负例见证不入
  phase2_golden.json；实施中发现 product_coverage 对每条
  已注册步的 golden_case_ids 作无条件存在性硬检，负例
  见证 2 例遂入 phase2_golden.json，其 expected 仅断言
  indeterminate 面（decision_status 与 sufficient_rule
  为 None），不进入任何正例 fire 断言通道；validate_
  phase2.py 对该步以 validation_status=pending 接受在册
  （execution_status=executable）。偏离与理由如上记录，
  不影响 §3.4 的「不伪造正例、不要求真实盘正例」实质。
- 连带披露：管理面 reviewed_algorithms 的 bazi 记录自本批起
  validated_rule_count=71、rule_count=72（差额恰为该步），
  其 production_ready 派生值随之为 False；该记录为只读
  管理面披露，不被任何用户场景消费，phase3 API 契约测试
  已按「唯一例外恰为该步」精确钉住。

## 6. 回滚演练

- 新代码 + 旧快照（b93e4b97…）组装实测：lu 正例盘与
  water 正例盘在裁定步 fail-closed 抛错（Unknown rule:
  bazi.phase2.strength_lu_visible_support /
  strength_pure_generating_support_water），不静默产出；
  非触发盘 result 除 limitations 注册披露句外与旧代码+
  旧快照逐字一致（trace 与 evidence 图逐字一致）——披露句
  为代码侧文本、与快照同属本批原子变更，父级按先换代后
  合并执行，生产不出现新代码配旧快照的服务状态。

## 7. 快照换代清单（父级合并前执行）

- before：237 文件 / 15,922,702 字节 / manifest sha256
  b93e4b97830ff15aca1a9e77847796e5ddd5cb7e1f3cd6512db20a358c159622
- after：237 文件 / 15,964,218 字节 / manifest sha256
  c815dc4ed02a9b7d0bd1487c3e1ed4e39d0bc826659d4ff0fb7f8a37ff685cdf
- 变更文件 4：data/canonical/bazi/phase1_knowledge.json
  （sha256 6501e0b6…）、data/canonical/bazi/
  phase2_execution.json（aaf8a385…）、data/canonical/bazi/
  phase2_golden.json（7f1620de…）、data/coverage/phase1.json
  （a9aa13a4…，按模型再生）；完整 sha256 以治理记录
  TJ0183_P2_RECORD 为准。data/product/knowledge_coverage.json
  存储版不回写：离线验收在组装树内以最终代码再生该报告后
  再行校验（accept_offline 步骤序），存储版不影响验收，
  沿批一先例不入换代清单。
- 顺序：live 快照换位 → cicd 钉 TRUSTED_MANIFEST_SHA256
  更新 → 合并（E0329 竞态教训）；私有检出侧 EXPECTED_BYTES
  =15964218 与检出 manifest 已同步重生、verify 通过；
  暂存快照与换代清单（swap_list.json）已交付父级。

## 8. 实施前复核结论与 P2 审定 §8 未判项处置

- 编号复核：密封实测 rules 31 条（r001–r031）、sections
  60、chapters 21，r032–r034、s061/s062 与两新章 ID 均未
  占用，按拟定编号实施。
- 验证器粒度复核：validate_phase2.py 对 validated 步要求
  Golden 真实 fire——metal 步因此定稿为 validation_status
  =pending（见 §5），其余断言（丁隔离、□1、帝旺措辞、
  禁用表述）均以机检形式落入密封注册测试
  tests/test_phase2_baziganzhi.py，无人工声明替代。
- P2 审定 §8 未判项：丁长生两说、辛/癸长生冲突、土长生
  口径、□缺口处置、合化与从格消费面——本批一律维持原
  登记逐字不变（conflict 记录随节携带、缺口保持
  unresolved），不建新谓词、不作任何裁定，留待用户级
  裁定与后续批次。

## 9. 仍未判断与后续

- TJ-013.1 扶抑仍阻塞（U1/U3 用户暂缓）；TJ-017.2 真实
  定义（原局＋大运＋流年跨规则调用）仍阻塞。
- S5 维持 pending 9 项随材料齐备逐项再议；批三阳刃重新
  评估待卷三《论十干禄》前置登记批与用户授权。
- 注册翻转第五条件（正式验收 SUCCESS 与部署验证）为
  终局条件，由父级关账批（E0336 预留）复核。
