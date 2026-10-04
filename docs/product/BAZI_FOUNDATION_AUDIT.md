# 八字基础逐项审计

Terms/Rules/Evidence/Variant/Golden 必须一起核查。现有表可作实现输入，不因表存在而宣称对应个人判断完整。以下只反映本批确证的范围，完整强弱、格局、喜用仍未支持。

| 项目 | Terms / Rule | Evidence | Variant / Golden / 测试 | 成熟度与缺口 |
|---|---|---|---|---|
| 天干 | day_master、ten_gods；r001/r002 | 渊海四柱/甲乙十神短引 | ziping-structural-v1；structural-basic；test_phase2_bazi | 天干结构已执行；专属术语和全部阴阳五行原典依据仍需专题补足 |
| 地支 | hidden_stems；r003 | s004 十二支藏遁歌 | 同上，结构 Golden | 十二支藏干结构已执行；不能据地支数量断强弱 |
| 阴阳 | ten_gods 相关定义；r002 | 甲乙参照映射及阳见阴/阴见阳等短引 | 十神结构测试 | 已有结构映射；独立术语与全表依据仍需补足 |
| 五行 | 日主 element、ten_gods；r001/r002 | 五行生克十神关系相关选段 | 固定结构与十神测试 | 已有计算，不把实现表权重当古籍定量模型 |
| 生克 | ten_gods；r002 | 伤官、财、官、印定义 | 十神结构测试 | 同样只判关系，不判生扶克泄实际效力 |
| 四柱 | day_master；r001 | s001 四柱排定 | pillars；structural-basic；日期适配测试 | READY：四柱结构，不含真太阳时 |
| 日主 | day_master；r001 | 日上天元短引 | pillars；structural-basic | READY：取日干，不能据此直接定性格 |
| 月令 | month_command；r013 | s023/s024/s028 + 藏遁歌 | month_command_factors；六因素 Golden | PARTIAL：月支与藏干已执行，司令分日异文未裁定，得令不能冒充已完成 |
| 藏干 | hidden_stems；r003 | s004 藏遁歌 | hidden_stems；structural-basic | READY：固定表与相对十神；不使用 60/30/10 作为普适根力 |
| 十二长生 | 旧表参考，不算已审核 Rule | 尚无对应完整执行引用 | 暂无对应 Phase2 / Golden | NOT_BUILT（执行链）：阴阳顺逆、生死口径与土寄生须分 Variant 审核 |
| 通根 | root_candidates；r014 | s025/s026/s028 + 藏遁歌 | root_candidates；正常/墓库/无根/异字同五行/冲根反例 | PARTIAL：候选位置可执行，根力和受损效力尚未裁定 |
| 透干 | hidden_to_visible；r015 | s027 + 藏遁歌 | hidden_to_visible；六因素 Golden | READY（限同字透藏事实）：不把日主当额外透干，不推司令/得势/格局 |
| 节气边界 | 四柱适配；现有 calendar | 已固定 calendar 工程来源；原典提纲短引不证明现代历表精度 | lunar-python==1.4.8、北京时间 midnight；既有 calendar/网关测试 | 固定约定已执行；独立历算交叉校准、真太阳时和其他日界仍不宣称支持 |

本批新增因素子范围 `ditiansui-root-visibility-v1` 的上层执行仍为 `ziping-structural-v1`，每个新 Rule 都有来源、解释边界、当前 Golden 与 Scenario 接线。它不是完整旺衰分类器，基础全部专题也尚未达到全量验收。

补库顺序仍沿现有 Source → RAW → Quarantine → Review → Canonical → Terms/Rules → Evidence → Variant/Conflict → Golden → Phase2 → Scenario；不另建表权重体系，不修改原始 snapshot，不开放未校准 AI。
