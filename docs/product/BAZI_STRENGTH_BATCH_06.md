# 旺衰第六批：判定出口、古例参照及无法判断的 Golden

本批继续既有 Source → 审核 Section → Term/Concept/Rule → Evidence → Phase2 → Golden 流程。没有创建新的知识模型，没有修改 RAW，没有升级来源等级。

## 实际结果

显式 `strength_variant=bazi-strength-conditions-v1` 增加 `strength_assessment`。它汇总当前服务端真实执行的司令、根及生克条件，每一缺口绑定 `fact_ref / rule_id / evidence_id / variant / status`。输出 `indeterminate` 与 `insufficient_reviewed_rules`，不使用五行计数、显藏等效、数值权重或古例标签查表。

这是可执行的未裁定出口，**仍不是完成的强弱分类器**。`supported_classifications=[]`、`maturity=PARTIAL`、`full_strength_classifier_ready=false`，不开放 AI 或后续格局、喜用、行运。

## 原典参照与算法的区别

- 《滴天髓阐微》方局：戊寅 / 甲寅 / 甲辰 / 丁卯，成方透元神；相邻原论明确“旺可知矣”，同时强调须看气势、不可一例而推。原版时柱丁卯紧接大运乙卯，保留原排版，手工区分。
- 《渊海子平》论财：庚申 / 乙酉 / 丙申 / 丙申，明确财旺与日弱，并称“身弱太甚”。显干乙及申藏壬确实存在；当前算法不能凭简单删除或等效计数重现作用条件。

以上短段已逐字审核，引用固定快照与字符定位，证据为 C 级单一电子版本。它们用于对照真实算法缺口，不按四柱记住答案冒充通用分类。因此两个古例在本引擎均返回 `indeterminate`。这两条 Golden **不能计作完成标准中的可复算强/弱正例**。

## Golden 覆盖

固定预期包括：强例参照、弱例参照、临界混合结构、司令体系冲突、四库本气未审、余气类型异文、方向明确而实际作用未定。没有把临界等同 balanced，也没有把缺根等同 weak。

## 尚未完成的标准

司令、根结构与显藏分层已有明确 Variant/Rule，所有执行规则有 Evidence 和 Golden；但根的可用性、实际生克效力，以及可通用复算的强/弱正例仍未闭环。一般平衡分类也没有充分规则。旺衰仍为 PARTIAL，后续阶段继续关闭。七域产品成熟度和公共页面不因缺口报告而晋级。

《三命通会》维持 quarantine_only、canonical_ready=false；PUA 与 OCR overlay 均不改变。
