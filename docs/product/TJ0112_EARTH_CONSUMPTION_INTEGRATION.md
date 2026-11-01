# TJ-011.2 土根消费接入实现记录（E0355）

## 0. 文档定位与授权依据

本文件是 E0257《土根消费接入审定契约》（`TJ0112_EARTH_CONSUMPTION_CONTRACT.md`，
登记 `bazi-earth-root-consumption-contract-v1`）的实现批记录。契约在 E0257
审定时结论为「零接入、零新谓词」，并明示「接入实现（未来批次，另行过
全量复现门）」；本批即该实现批，基线为 main `e8d52e7c`（台账 354 事件，
密封钉 `26b63e64…`）。本批不是重新审定：契约的格级裁定、接入面审计与
前置条件逐字沿用 E0257，本文件只记录实现如何逐项符合契约。

本批边界（任务书与契约共同约束）：只做契约审定的消费接入；不新设旺衰
谓词、不产生任何新的 strong/weak 判定、不改动既有 8 条谓词语义与
TJ-011.2 阻塞状态；不改动土根分级表 24 格本身；不触及扶抑 U1/U3、丁线、
F5/F6 已关闭项；不把土根登记升级为裁决依据。

## 1. 契约条目逐项符合性表

| 契约条目 | 契约裁定 | 实现落点 | 符合性 |
|---|---|---|---|
| 戊×巳、己×午（eligible 2 格） | per_stem_listed 禄位重根，仅根位资格面 eligible；引用须随行标注等级 | `registered_eligible` 土分支只查由契约 eligible 格集派生的白名单 `EARTH_ELIGIBLE_CELLS`；查得资格时 fact 标注 `grade_basis='per_stem_listed'`、`rule_source='土根消费契约白名单'` | 符合 |
| 待定 8 格（戊×子/寅/午/申、己×子/巳/申/酉） | conflicted_pending，恒阻断，无任何分支可回退为 eligible | 白名单外一律不计资格；代码无任何回退路径；因子层与真实盘层均有专项钉 | 符合 |
| 未分级 8 格（两干各丑/辰/未/戌） | structural_present_ungraded，明确裁定 not_eligible，未分级即未审 | 不在白名单、不计资格；24 格逐格穷举测试钉住；真实盘纯未分级例（1924-04-12）钉住「唯一阻断格」形态 | 符合 |
| no_root 6 格（戊×卯/酉/亥、己×寅/卯/亥） | 已审否定事实消费，不计资格、不携冲突语义 | 不在白名单；消费面不产生任何冲突标记 | 符合 |
| framework_derived 0 格 | 框架派生通道在土根语境零适用，不构成消费路径 | 实现未引入任何框架派生路径 | 符合 |
| 计数自洽 24 = 2 + 8 + 14 | 契约自洽钉 | 公开测试钉住契约计数与白名单派生计数（2/8/14） | 符合 |
| 防误接条款（资格判定须格级白名单化，禁止把分级表机械代入排除法） | S2 现行资格规则是排除法形状；土根表多出未分级一级，机械代入会误计八格 | 实现为显式白名单（正列举），非排除法；土分支亦不回退密封政策（政策无土集） | 符合 |
| 契约 R1–R6 红线 | 不得新设谓词/新判定；不得改 8 谓词语义；不得升级为裁决依据；不得处置土长生 conflict；不得类推藏干；密封注册另按 S5 形制 | 逐项遵守，见 §2、§3、§4、§8 | 符合 |

## 2. 接入面审计与已实现/新实现清单

开工审计（先审计后建设）：逐项复核 E0257 接入面审计结论在当前 main
的现状——运行时四文件（`bazi_action_conditions`、`bazi_adjudication`、
`bazi_strength`、`bazi_pattern`）零引用土根登记，与契约
`runtime_wiring='none'` 现状一致；契约审定的唯一既有落点（金属形态
`registered_eligible` 对土干的落空否定面）尚未被任何后续批次实现。
契约与现状无实质冲突。

| 消费方 | 契约审计结论 | 本批动作 |
|---|---|---|
| 金×酉 pure（r033，S2） | 唯一既有落点：`registered_eligible` 喂 `all_registered_roots` → `all_visible_have_registered_roots` | 新实现：土显干走契约白名单分支 |
| 水×子 pure（r034，S2） | 与金属共用同一资格函数；土显干在其盘为官杀、被 support-only 先行否决（可达性为零） | 同一函数自动共享白名单；因子层专项钉住共用一致性 |
| 其余六谓词（木×卯、木×酉、木×亥、丙×午、丙×巳、丙×寅 F4） | 无土根位消费面（F4 的司令消费与土根无关） | 零改动、零接入 |
| D-1 任氏寅月真格（r037） | 无土根位消费面，透干判定只查月支藏干本气 | 零改动、零接入 |

文件级变更清单：

- `src/tianji_kb/bazi_action_conditions.py`：新增土根契约导入（只引
  `EARTH_CONSUMPTION_CONTRACT`，不引分级表）、模块级白名单派生、
  `registered_eligible` 土分支；`register_effective` 逐字未动。
- `src/tianji_kb/bazi_earth_roots.py`：文末追加实现登记
  `EARTH_CONSUMPTION_INTEGRATION_E0355`（纯数据）；24 格分级与契约
  记录本身逐字未动。
- `src/tianji_kb/bazi_metal_water_roots.py`：`METAL_YOU_SATISFIABILITY`
  追加 `integration_e0355` 注记（接入内容、通道三退役、结论由通道
  一/二独立承担）；proof_channels 与 review_e0257 历史文本未动。
- `src/tianji_kb/bazi_registration_governance.py`：pure_support_metal
  条目 reason 追加 E0355 披露句；disposition 与 Phase1 规则号不变。
- 测试：公开 `tests/test_tj0112_earth_consumption_integration.py`（8 测）、
  密封 `tests/test_tj0112_earth_consumption_integration_sealed.py`
  （10 测）、S2 Golden 新增 4 例；契约/土根两处「零接线」状态钉按新
  状态转换为「接线落点恰为契约面」钉（转换依据写入测试注释，非放宽）。
- `.github/workflows/validate.yml`：新公开测试按名接入；两处过时注释
  按 E0355 状态更新。

## 3. 实现形态

资格判定形态：显干根位由引擎按「同行根存在」给出（root_positions 为
全盘同五行藏干位点），资格按（显干，位点支）格级裁定——与 S1/S2 登记
表既有的消费形状一致。土分支只查白名单集合
`{(戊，巳), (己，午）}`，该集合在模块加载时由契约记录的 eligible 格
派生（单一来源，契约若变则派生随变，公开测试钉住派生等值）。土干不走
金/水登记表的排除法、不回退密封政策。`register_effective`（日根
effective 路径）与藏干位点构造均未触及。

产出披露口径不变：两形态仍以 scope 条件字典形态产出
`all_visible_have_registered_roots` 布尔值；无新字段、无新判定类型、
无分数/权重；研究级披露（research_only 等）沿既有形态不变。

## 4. 前置条件七项逐项满足表

| # | 契约前置条件 | 本批满足方式 |
|---|---|---|
| 1 | 格级白名单化 + 未分级八格逐格不合计格测试 | 白名单实现；密封因子层 24 格逐格穷举（戊/己 × 12 支），未分级八格逐格断言不合 |
| 2 | 待定格恒阻断；长生 conflict 处置不在接入批权力内 | 白名单外不计、无回退；conflict 本体未处置（见 §8） |
| 3 | 土日主 principal 未审，土日主形态不可建 | 未建任何土日主形态；契约未被用作 principal 授权 |
| 4 | 藏干根位资格口径未审，不得类推显干面 | 接入只及显干资格面；F34 pending 第 2 项维持；密封因子层钉住土日主根不经 effective 路径（藏干面无新消费） |
| 5 | 日根 effective 口径未审，本契约只裁 eligible 面 | `register_effective` 逐字未动；公开测试钉住金/水 grade 查询对土干恒 None（effective 路径未接入） |
| 6 | Golden 四类 + 判定面逐项对账，E0257 零变化证明不得沿用 | 四类真实命盘入 S2 Golden（§5）；738 语料等价比对（§6） |
| 7 | 进入裁决出口时密封注册另按 S5 形制，pending 披露不得省略 | 实现登记 + 金属不可满足注记 + S5 治理登记披露句同批落地；金属 Phase2 步 validation_status 保持 pending、负例见证集不变 |

## 5. Golden 四类（真实命盘，条件表逐条手工推导）

四例入 `tests/golden_tj0112_s2_metal_water.json`（7 → 11 例），出生时刻
经历法核验、四柱与条件表逐项手工推导后与引擎双树实测对平：

| 类 | 用例 | 出生时刻 | 四柱 | 关键断言 |
|---|---|---|---|---|
| 正例（戊/己白名单经位点混合集生效） | tj0112-e0355-metal-earth-wu-listed | 1928-06-10T01:30+08:00 | 戊辰/戊午/辛巳/己丑 | all_visible False→True（戊经巳、己经午；同集内的待定/未分级格不计） |
| 正例（己白名单 + 日根 effective 在册） | tj0112-e0355-metal-earth-ji-listed | 1929-05-25T05:30+08:00 | 己巳/己巳/庚午/己卯 | all_visible False→True（己经午；巳为待定不计） |
| 未知类（未分级格阻断） | tj0112-e0355-metal-earth-wu-ungraded | 1924-04-12T05:30+08:00 | 甲子/戊辰/辛酉/辛卯 | all_visible 恒 False；唯一阻断 = 戊×辰未分级格（排除法会误计的那一格）；封套接入前后逐字一致 |
| 冲突类（待定格阻断） | tj0112-e0355-metal-earth-wu-pending | 1928-06-19T05:30+08:00 | 戊辰/戊午/庚寅/己卯 | all_visible 恒 False；戊位点含寅/午待定格恒阻断、无回退 |

对照类由既有语料承担：S2 Golden 原 7 例全回归（水正例仍 fire、金属近失
表不变），且 §6 的 738 语料等价比对覆盖全部仓库 Golden 出生时刻。

## 6. 等价比对（封闭清单与实测）

封闭清单（先行设定）：允许差异仅限两形态 scope 条件字典内
`all_visible_have_registered_roots` 由 False 翻 True，且每处翻转须可由
白名单解释；scope 是否满足、classification、可见/隐含 effects 及其余
一切键的差异必须为 0；执行错误集必须逐字相同。

语料：738 个真实出生时刻（仓库全部 Golden 出生时刻 138 + 潜在翻转扫
描 400 + 土显干抽样 200，1924–2030），基线树（e8d52e7c）与接入树在同
一密封快照下组装、逐封套比对。

实测结果：690 个成功封套比对，叶子差异共 179 处，全部落在封闭清单内
（金属 91、水 88）；清单外差异 0；scope 满足状态变化 0；classification
变化 0；48 个执行错误两侧逐字相同。

## 7. 判定面结论与金属不可满足的通道变化

判定面变化 = 条件值层 179 处、裁决层 0。金属形态在真实盘仍构造性不
可满足：月门迫全酉盘时，土显干的根位支只能是酉——戊×酉为 no_root、
己×酉为 conflicted_pending，均非白名单格，故资格面在金属盘恒不可达。
E0257 通道三（土印根位缺口）的预登记复核条件已由 E0257 订正与本批接
入两步满足，自本批起退役为历史通道；不可满足结论改由通道一（藏干唯
一支）、通道二（全酉盘显干干对，五虎遁/五鼠遁 + 干支阴阳配伍）独立
承担，结论不变。水形态下土显干为官杀、被 support-only 先行否决，条
件值翻转不产生任何裁决路径。

## 8. 仍未判断范围（本批未动）

- 土日主任何形态与四季月 principal（未审、不可建）。
- 日根 effective 口径对土根的适用（未审；register_effective 未接入）。
- 藏干根位资格口径（F34 pending 第 2 项维持 pending）。
- 土长生 conflict 本体（三命干级 vs 神峰水土同宫，未裁；待定八格只
  保持阻断）。
- 土轻根分级（辰戌丑未四格，未审；本批只按契约裁定其不计资格）。
- 扶抑 U1/U3、丁线、F5/F6：均未触及。TJ-011.2 保持阻塞。

## 9. 五问答复（沿 E0257 五问，就实现批作答）

Q1 土根事实由哪些消费方读取：仅 S2 金/水两形态共用的
`registered_eligible` 资格函数，在 `all_visible_have_registered_roots`
条件内读取契约白名单两格；其余六谓词与 D-1 零读取（审计证据见 §2）。

Q2 允许产出什么：仅既有条件字典内一个既有布尔条件的值可因白名单格
由 False 变 True；无新字段、无新判定、无新谓词（实测见 §6、§7）。

Q3 禁止产出什么：任何 strong/weak 新判定、土日主形态、effective 根
地位、藏干资格结论、待定格的任何回退资格——实现与测试逐项钉住缺席。

Q4 与既有判定的关系：判定面变化限于条件值层（179 处），裁决层零变
化；金属不可满足结论不变、承担通道由三减二（通道三退役）。

Q5 未审范围如何保持未审：白名单为正列举、契约外格级一律不计；
effective/藏干/principal/conflict/轻根分级五面在代码与登记两侧均保
持未接入/未裁定状态（§8），S5 治理登记的 pending 披露未省略。

## 10. 验证与复跑记录

基线正式验收（开工直读）：管线对 e8d52e7c 的 acceptance 证据
SUCCESS，总数 2844（public-git-checkout 15 + public-only 24
（skipped 1）+ private-backend 2805），失败/错误 0。

本批机上全配方复跑（TJ-013.1 站立规则，合并前硬门）：在可信机以
`scripts/accept_offline.py --suite all` 对本批分支代码复现快照
（树内容与本地分支逐 blob 核对一致）+ live 密封快照（钉
`26b63e64…`）实跑，结果 **OFFLINE ACCEPTANCE SUCCESSFUL**，总数
**2862**，逐项对账：

| 套件 | 基线（e8d52e7c 正式） | 本批复跑 | 差 |
|---|---|---|---|
| public-git-checkout | 15 | 15 | 0 |
| public-only | 24（skipped 1） | 24（skipped 1） | 0 |
| private-backend | 2805 | 2823 | +18 |
| 合计 | 2844 | 2862 | +18（失败/错误 0） |

+18 构成：公开集成测试 8 测 + 密封集成测试 10 测（组装树内全量
执行口径）。密封专项在组装树内直跑另行核对 49/49（集成 10 + S2
全套 + 契约密封 + 土根密封 + 金水根密封）。本地基线对比旁证：裸
公开检出下本批与基线的失败/错误集差异恰为本批新增的 11 条（密封
环境缺失所致，含尚未落册时点的登记记录 1 条，落册后公开侧全绿）。

等价比对的双树组装与探针证据见 §6；四例 Golden 的条件表先由手工
推导、再与双树实测逐项对平（§5）。公开 CI 结果随 PR 记录（交付报
告引用 run 链接）。

## 11. 台账与收尾

台账事件 E0355（中央分配），归属 TJ-011.2，行状态「阻塞」不变，后三
列「—」；TASK_STATUS 仅动 TJ-011.2 行。本批无密封文件变更，无需快照
换代（live 快照与 cicd 钉不动）。止于 PR，合并由父级亲核后执行。

## 12. 关账记录（E0356，append-only 补记）

- 合并：实施 PR #532 已由父级亲核后合并，Merge SHA `d8574489574665f6e2a2cf727433a12dc57a6811`（Head `488f19d94e28b31bf5cf24b4985823e1d5d90fb6`），公开 CI 全绿。
- 正式验收（部署管线对 Merge SHA 的密封验收，关账时以机上 `acceptance-d8574489574665f6e2a2cf727433a12dc57a6811.json` 直读为准）：result SUCCESS，总计 **2862** 测——public-git-checkout 15、public-only 24（skipped 1）、private-backend 2823，failures 与 errors 均为 0；密封清单 237 文件、16,722,816 字节、manifest SHA256 `26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`。
- 部署：ACCEPTED 2026-11-01T04:14:17Z；DEPLOYED 2026-11-01T04:14:46Z，pin `db6673d2599b4a51415e4678f21728aeb44c66b9cea3a796afe437d1b90f210a`（health 与 bazi 探针 ok）。
- 基线链：2844（`e8d52e7c`，E0354 合并后正式验收）→ 2862（本批 Merge SHA），增量 18 = 公开新增 8 + 密封新增 10，与 §10 实施批机上全配方复跑（SUCCESS 2862）逐项对平。
- 无换代声明：本批无密封文件变更，无快照换代——live 快照 manifest 与 cicd 钉 `TRUSTED_MANIFEST_SHA256` 在合并前后均为 `26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`，关账时机上直读复核一致。
- 机上清理：`/data/workspace/earth-e0355/` 残余已清理——删除 `pub` 检出副本约 112M，保留日志（accept-e0355.log 等）、脚本（assemble.py 等）与 corpus.json 共约 76K；清理后 `df -h /data` 为 80% 已用（余 4.0G，清理前 81% / 余 3.9G）；projects、secure、evidence 未触碰。
- 台账：事件 E0356（中央分配），归属 TJ-011.2，行状态「阻塞」不变，后三列「—」；TASK_STATUS 仅动 TJ-011.2 行。本关账止于 PR，合并由父级亲核后执行。
