# 旺衰第五批：生扶克泄条件链

基线 main：34a236481a960a2a1226e866aa18c853e40134ca（#130）。

新增 r019 / bazi.phase2.action_conditions 与 ditiansui-action-conditions-v1，在显式 bazi-strength-conditions-v1 下调用既有四柱、十神生克方向、藏干、月令及关系算法。默认场景保持关闭附加选项；不开发页面或 AI。

## FACT / INTERPRETATION / EFFECT

| 层 | 当前真正执行 | 禁止推论 |
|---|---|---|
| FACT | 显干3个参照位置、所有藏干位置、每个显干同五行根候选、同字透藏位置、年/月/时与日柱的柱距和相邻事实 | 不以柱距为权重；日干不再自扶一次 |
| 条件 | 月令司令未决状态、天干五合、显干根支的冲合害/三合、原典喜忌与通根得气依赖 | 相邻不等于有效；有根不等于得气；五合不等于成化 |
| EFFECT | effective_action=null、effect_status=unresolved，得势与整体强弱为空 | 不输出生扶成功、克泄成功、吉凶、喜用或强弱分数 |

显干、藏干分别列出；显干另有 rooted_visible_candidate。根是同五行结构候选而非有效力量；藏干带 equivalent_to_visible=false，不把一个藏干和一个透干相加或视作相同贡献。即使藏干同字在显干出现，也只记录位置对应，没有把两者并成两份力量。

## 原典条件逐字复核

- 已审《渊海子平》生克制化列出“水多金沉”“木坚金缺”等条件，故关系方向不能等价为效力。
- 新 s042《滴天髓阐微·清气》强调喜神得地逢生且紧贴、忌神远隔，并以“日主喜印”为前提。只记相邻事实，不跳过未知的喜忌前提。
- 新 s043 众寡篇强调火日主亦要通根得气才能生土。不能由火生土的方向自动确认其效力。
- 司令、根实际可用性、合化与距离效力尚未可执行；沿既有冲突与未决信息保留这些缺口。

## StrengthFactorGraph

月令、根条件和作用条件节点逐一绑定真实 trace、Rule、Evidence 与子 Variant；所有关系边也有 fact_ref/rule_id/evidence_id/evidence_ids/variant/status。边方向按日主视角：我生/我克从日主指向目标，生我/克我从目标指向日主；effect=null。

graph 的 overall_strength=indeterminate，full_strength_classifier_ready=false，maturity=PARTIAL。该图现在可解释“有哪些条件未解”，不能解释为已判断身强身弱。

## 固定验证与边界

四个手工 Golden 覆盖显干有根、四显木干无木根、有根但遇冲、阴日主参照。专项测试核显藏不等价、冲条件不确认效力、图边引用与方向、真实 bazi-profile 接线、默认请求无附加条件图。已有根 Golden 继续保留。

本批关闭条件链记录缺口，但没有关闭实际效力裁定。下一步分类验收必须保留无法裁定，未审核的阈值或分日口径不能用评分、计数或 LLM 补齐。三命仍 quarantine_only，原始 snapshot、已确认 PUA/OCR 不改。
