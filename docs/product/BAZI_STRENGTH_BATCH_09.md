# 第九批：有限充分条件强弱裁决闭环

沿用原知识模型，演进 `bazi_adjudication.py`。显式 `bazi-strength-adjudication-v1` 使用本气关系、木根可用性、有限实际作用的同一明确任氏口径，返回 strong / weak / indeterminate。没有新增平行分类器、百分制、五行计票、根数阈值或古例 lookup。

## 两条充分规则

| 结果 | 同时满足的条件 | 原典依据 |
| --- | --- | --- |
| strong | 木日主；月卯本气同类；全局显藏纯印比，确有有根显印与显比；木根可用，有限实际生扶成立；不存在本口径未解冲合害、根型异文或因子 Variant 冲突 | s047–048 纯印比强状态、s052 春木甲乙语境、s026 木根、s033–035 本气与同五行、s004 藏干 |
| weak | 木日主；月酉本气克我；全局无木根或任何印比；天干土金；月辛主气透出且有根、有限克制作用成立；不存在本口径未解改变 | s049 孤立无生扶；s051 仅核弱状态的原文参照；已审月主气、藏干与克制方向 |

所有其他情况保持 indeterminate，包含无根却有印、非木日主、五合未解、余气异文等。月令关系、根或生克方向单项均不能判强弱。strong 不等于吉，weak 不等于凶；从格、喜用和行运没有实现。

## 可复算正例与边界

同一 Strength Variant 的九个固定 Golden：strong-positive 2、weak-positive 2、abstention 3、conflict 2。预期手工固定，不由测试时的输出生成。

| 历法输入（国内时区） | 四柱 | 有限裁决 |
| --- | --- | --- |
| 1963-03-22 22:00 +08:00 | 癸卯 / 乙卯 / 甲子 / 乙亥 | strong |
| 2043-03-22 22:00 +08:00 | 癸亥 / 乙卯 / 甲子 / 乙亥 | strong |
| 2038-09-14 12:00 +08:00 | 戊午 / 辛酉 / 甲午 / 庚午 | weak |
| 1978-09-20 10:00 +08:00 | 戊午 / 辛酉 / 乙酉 / 辛巳 | weak |

正例并非古书四柱查表。原已审核古例在此有限 Variant 中也可能 indeterminate；例如非木古例不会获得标签特许。

## 依赖与证据

正向结果含实际 matched_rule_ids / fact_refs / evidence_ids / source_ids / conflict_checks / limitations / why_not_indeterminate。对应强或弱充分 Rule 只在完整条件满足时才加入 trace 和 RuleMatch。未裁定保留 blockers、unresolved_evidence 和实际阻塞 conflict_ids。

分日司令不是本 Variant 的依赖。原 commander 仍 unresolved，候选冲突仍报告但不阻塞本气裁决；独立藏干数值效力也不要求完成，因为没有把藏干作为显干计票。根型异文及已检测未解冲合害会阻塞。任氏刑口径显式限定，跨流派状态仍 unresolved。

## 成熟度与开放状态

`knowledge_coverage.json` 按 Variant 派生：整体 PARTIAL；有限强弱为 RESEARCH_VALIDATED，分日体系 BLOCKED，本气单项只是 BOUNDED_FACTOR_ONLY。静态能力图核执行契约和固定 Golden 定义，不冒充 CI 实际运行结果。

引擎研究入口必须显式 `allow_research=True`；已有 API 必须 `mode=research`。默认生产及公共 bazi-profile Scenario 拒绝自动使用此 Variant，AI 解释契约关闭，研究规则不混进公开 supported_capabilities。前台、格局、喜用、运势均暂停。半合拱夹、暗合与其他学派刑法不在此口径；结构藏干保留，没有推断成化或消根。

来源仍为 C 级电子版本；不宣布完整八字旺衰算法、跨底本一致或公开预测产品完成。四类回归验收的是这两个有限充分语境的第一版闭环。《三命通会》及所有 RAW、PUA/OCR 校勘均不改。
