# 八字十二月司令审核矩阵（研究范围）

以现有 `bazi.concept.month_command_variant_v1` 的审核来源生成，见 `commander_review_matrix()`。
**本气结构不等于某日司令**；“未登记冲突”不等于“双方已核对”，也不等于“可定格”。

| 月支 | 本气结构已审 | 分日候选资料已审 | 司令来源对照 | 日界状态 | 具体日司令 |
|---|---|---|---|---|---|
| 寅 | 甲 | 两个候选口径 | source_conflict | insufficient_text | unresolved |
| 卯 | 乙 | 无 | not_reviewed | not_reviewed | unresolved |
| 辰 | 未审 | 无 | not_reviewed | not_reviewed | unresolved |
| 巳 | 丙 | 无 | not_reviewed | not_reviewed | unresolved |
| 午 | 丁 | 无 | not_reviewed | not_reviewed | unresolved |
| 未 | 未审 | 无 | not_reviewed | not_reviewed | unresolved |
| 申 | 庚 | 无 | not_reviewed | not_reviewed | unresolved |
| 酉 | 辛 | 无 | not_reviewed | not_reviewed | unresolved |
| 戌 | 未审 | 无 | not_reviewed | not_reviewed | unresolved |
| 亥 | 壬 | 无 | not_reviewed | not_reviewed | unresolved |
| 子 | 癸 | 无 | not_reviewed | not_reviewed | unresolved |
| 丑 | 未审 | 无 | not_reviewed | not_reviewed | unresolved |

**具体纠错**：现有审过的 `bazi.section.s024` 字面为“八日后十四日前者”，不是“八日至十四日前”。
本批只修 Concept 摘要，没有改原典 Source/RAW 或 Quarantine，也没有按公历日期、节气天数或本气去推出具体日司令。
`bazi.section.s029` 中“立春念三丙火用”仍保留疑字；两个电子文本尚不能作为独立底本互证。

## 可重现的机器约束

`commander_review_matrix()` 读已审核 Concept，输出十二支的 principal_qi、candidate_profiles、source_comparison_status、
dated_boundary_status、conflict_ids，且对全部十二支 `exact_day_commander = null`。
`month_command(...)` 的 `dated_review` 引用相同的审查行。矩阵内容与代码不同步时，应修审计，不得凭无冲突自动升为 resolved。

这一矩阵不是分日司令算法，不代表十二个月已完成资料校核；继续定格必须按流派与候选取法另立审核证据。
