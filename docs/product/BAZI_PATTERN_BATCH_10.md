# Bazi Pattern Batch 10：任氏通根原典例的条件化复用

## 范围

基于原有 `bazi.phase2.resource_pattern_candidates`，从已执行的藏干/十神/地支互动事实中标注财、官、印各自的**根型原典候选**。同五行藏干与同字藏干仍为结构事实，**不**等于“根力有效”。

本批复用现有 `bazi.concept.root_conditions_variant_v1` 的审核政策，而非新建权重模型：已审核的长生禄旺列举（甲乙逢亥寅卯）、余气例（丙丁未、甲乙辰、庚辛戌、壬癸丑）；本气只在已审的八个分支登记，不覆盖四库未知司令。

## Evidence 与冲突

- 现有《渊海子平》印绶原典 s057/s058 继续证明取材位置。
- 追加复用《滴天髓阐微》s026 根型列举、s027 司令限定、s041 余气异文；来源已在 canonical 中审核过，绑定到既有 r028 的 Phase2 Evidence，未凭空发明文本。
- s026 和 s041 余气列举不完全一致，遇到 s026 余气根型候选必须保留 `bazi.concept.conflict_root_type_readings`，不得合并成通用无冲突的根型表。
- 新字段 `reviewed_root_type_examples`、`principal_qi_review`、`residual_type_conflict`、`reviewed_root_type_comparison` 与 `reviewed_root_type_summary` 仅供研究解释其结构来源。

## 双文本余气候选

s026 的受审示例保留：丙丁未、甲乙辰、庚辛戌、壬癸丑；s041 的另一文本单独保留：丙丁未/戌、庚辛丑、壬癸辰。后一类从 `alternative_residual_type_candidates` 输出到 `alternative_root_type_examples`，每条标注 `ren-residual-alternate-text` 和 s041，不与 s026 覆盖或投票合并。两种文本相关根型皆不证明根力与生克已经有效。

## 验收与限制

固定 Golden 覆盖庚戌甲寅丙午戊子（审定庚辛逢戌余气、甲乙逢寅长生禄旺及余气异文冲突）和戊子壬子甲子壬子（没有审核根型例不能反推无根或无力）。回归校验具体藏干指针和执行 Rule Evidence 中的 s026/s027/s041。

继续保留 `research_only=true`、`public_enabled=false`、`ai_enabled=false`，以及所有实际根力/财旺破印/官印相生/喜用/旺衰的拒判状态。此批不是一般旺衰分类器，不能据原典举例创造“定量有效根力”。
