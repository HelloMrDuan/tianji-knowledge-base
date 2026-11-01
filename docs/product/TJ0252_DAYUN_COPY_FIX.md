# TJ-025.2 大运退出文案订正（E0362）

## 0 授权与范围

- 授权来源：全盘再审计 E0358（docs/product/PROGRAM_REMAINDER_AUDIT_E0358.md §8 附带发现、§11 顺位 A2）将本项定级 A 类微项：`integrated_reading`（人生总览组合层）的大运退出文案自 E0346（三命大运分段注册）与 E0348（神峰大运分段注册）后部分陈旧，建议一只文案订正微批——区分已注册与未建面、标记 reason 口径不变、零标记逻辑改动、零判定改动、专项测试逐字钉新文案。
- 本批范围：仅订正与当前注册事实矛盾的文案措辞；组合层代码（`src/tianji_kb/scenario_engine.py` 的 `integrated_reading["dayun"]`）与其前端呈现（`LifeOverviewPage.tsx` 逐字呈现该字段）两侧一并核查。前端无独立镜像文案（逐字渲染后端字段），故实际订正点恰一处。
- 硬边界：不改任何判定逻辑、provenance 旗标（组合层硬编码 False 常量）、7 维可用性与 reason_category 口径、任何数值；不把「已注册」表述成「已公开开放/已接线」；不顺带处理 TJ-025.2 其他余项或 7 维可用性；TJ-025.2 本体已关账（E0280，已部署验收），本批为后续面文案订正，行状态不变。
- 本批止于 PR，不自行合并；关账批 E0363 在合并与正式验收后另行派发。

## 1 开工核实与基线实测

- GitHub API main HEAD = `e27dd6a2c15585af852e68b59eef2278274b472a`（关账 PR #538 已合并），与任务书基线一致。
- 台账：TASK_HISTORY 事件连续至 E0361（361 事件）；TJ-025.2 行状态「已部署验收」（E0280 关账）。
- 正式验收基线：2894（Merge SHA `12e6415d` 的管线正式验收 SUCCESS，E0361 关账在册）。
- 密封钉：`26b63e64…`（237 文件 / 16,722,816 字节）；本批预期无密封变更、无快照换代。
- 注册事实（订正依据，逐项实测）：
  - 三命分段已注册（E0346）：方向 Phase1 `bazi.rule.r038` + Phase2 `bazi.phase2.dayun_classical_direction`；三命换算 Phase1 `bazi.rule.r039` + Phase2 `bazi.phase2.dayun_sanming_conversion`；Golden 6 例（治理册 `bazi_registration_governance.py` 与 `bazi_dayun_classical.py` 注册分段口径条目在册）。
  - 神峰换算分段已注册（E0348）：Phase1 `bazi.rule.r041` + Phase2 `bazi.phase2.dayun_shenfeng_conversion`（《起大运法》节 s073）。
  - 两分段均经 bazi_chart 研究门控进入 RuleMatch 与 Evidence；不接入公开场景（`bazi_dayun_classical.py` 在册口径：ai_enabled=False、不接入公开场景、生产 dayun 显示口径不变）。
  - 换算产出为交运时刻区间（handover_intervals），不折算单点岁数：虚岁/实岁无原典口径，本 Variant 不输出任何年龄数值；三命时级法与神峰日级法分立、永不合并。
  - dayun-compose / dayun-timeline-view 为 inherited 终局形态；TJ-017.3 公开开放未裁定、行保持阻塞；岁运效力（大运吉凶/作用效力）无任何已建规则。

## 2 陈旧条目清单（先行登记）

组合层与前端呈现两侧全量排查（关键词：尚无完成审核的生产规则 / 不推算 / 大运 + 限制表述；范围 `src/`、`web/visual-prototype/src/`、测试与产品文档）：

| # | 位置 | 原文 | 与注册事实对平 | 处置 |
| --- | --- | --- | --- | --- |
| 1 | `src/tianji_kb/scenario_engine.py` `integrated_reading["dayun"]` 第一句 | 「大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规则，」 | 方向与起运换算已有注册 Phase1 规则、validated Phase2 步与 Golden（E0346/E0348），此句对该两面已不成立；仅「岁运效力」一面仍成立 | **陈旧，订正**（见 §3） |
| 2 | 同上第二句 | 「本总览不推算或伪造大运时间线。」 | 总览组合仍未批准（`dayun_timeline_approved` 双旗标为组合层硬编码 False）、TJ-017.3 未开放，本总览确实不推算大运时间线 | 不陈旧，逐字保留 |
| 3 | `web/visual-prototype/src/public/LifeOverviewPage.tsx` 侧栏标题 | 「大运与旺衰仍未裁定」 | 述本总览内的裁定状态（总览不裁定大运与旺衰），未声称「无注册规则存在」；实质仍成立 | 不陈旧，不动；正文 `{integrated.dayun}` 逐字渲染后端字段，随条目 1 自动更新 |
| 4 | `src/tianji_kb/bazi_dayun_timeline_view.py` 模块 docstring | 引述人生总览「本总览不推算或伪造大运时间线」为既有公开口径 | 所引恰为条目 2，本批逐字保留，引述不失效 | 不动 |
| 5 | `docs/product/M4_M5_LEFTOVER_TASK_AUDIT.md` 第 59 行 | 引述大运维出口原文（E0275 时点实测） | 历史审计记录，append-only，不回改历史 | 不动（记录在册） |
| 6 | `tests/test_tj0252_life_condition_markers.py` 第 47 行 fixture | `"dayun": "大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规则。"` | 该 fixture 自述为「今日真实 _life 结构的镜像」，镜像对象即条目 1，须随订正同步（属文案逐字钉更新，依据 E0358/E0362） | 随订正更新为新文案逐字镜像并加依据注释 |
| 7 | `web/visual-prototype/tests/b028-booklet-stubs.spec.ts` stub 数据 | `dayun: "大运仍未裁定。"` | 前端 stub 契约测试的夹具文本，非生产文案 | 不动 |
| 8 | 其他页面大运限制文案（BaziProfilePage、CareerWealthStructurePage、YearlyStructurePage、ConsumerResultSummary 等） | 各页自身的能力边界表述 | 非 integrated_reading 呈现面，述各页自身的裁定/接线状态，不在本批范围（E0358 仅点名 integrated_reading 一处为 A 类微项） | 不动（排查在册） |

## 3 订正对照与文案裁定

- 原文（逐字）：「大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规则，本总览不推算或伪造大运时间线。」
- 订正后（逐字）：「大运方向与起运换算已有完成审核的注册规则（方向据三命分段；起运换算有三命、神峰两套口径分别注册，只给出交运时刻区间，不折算单点岁数或日期），但尚未批准接入本总览；岁运效力仍无完成审核的生产规则，本总览不推算或伪造大运时间线。」
- 逐项对平：
  - 「方向据三命分段」——方向注册恰为三命分段（r038）；神峰引文在方向产出中仅为 corroboration 旁证、不构成方向裁定依据，故不并列神峰。
  - 「起运换算有三命、神峰两套口径分别注册」——r039（三命时级法）与 r041（神峰日级法）分立注册、永不合并不取平均，「分别注册」如实呈现分立状态。
  - 「只给出交运时刻区间，不折算单点岁数或日期」——注册换算的产出契约即交运时刻区间；起运只给区间不给单点为 E0358 审计确认仍成立的契约本意；不输出年龄数值（虚岁/实岁无原典口径）。
  - 「但尚未批准接入本总览」——保留未批准/未接线实质：两分段仅经研究门控，总览组合批准旗标仍为 False，TJ-017.3 公开开放未裁定；文案不暗示已开放。
  - 「岁运效力仍无完成审核的生产规则」——该面确实未建，原文此分句保留语义并独立成句。
  - 第二句逐字保留（条目 2）。
- 文案纪律：不含规则 ID、评分、吉凶或预测语义；保留「大运方向」起首，既有子串断言（`test_life_integrated_report` 与浏览器专项 `life-strength-integration.spec.ts` 的 `toContainText("大运方向")`）不作改动地继续成立。

## 4 测试与等价核查

- 本地：新专项 `tests/test_tj0252_dayun_copy_e0362.py` 7 测全过；更新后的 `tests/test_tj0252_life_condition_markers.py` 7 测全过（fixture 镜像更新后，含禁入词表断言在新文案上仍成立）。
- 等价比对（机上双组装树，基线 `e27dd6a2` vs 本批分支）：真实语料 48 个出生时刻（1956–2005 年、冬月、+08:00、三时辰档）× 目标年 2026/2027 = 96 个 life 场景全封套逐叶深比对。差异叶恰 288 处 = 96 例 × 3 叶（`integrated_reading.dayun`、dayun_timeline 标记 reason 与 exit_text），逐叶恰为旧文案 → 新文案；封闭清单外差异 0——判定、旗标、7 维可用性、证据与其余全部文案逐字不变。

## 5 机上复跑与基线对账

- 机上完整配方（`scripts/accept_offline.py --suite all`，组装树内 validate/build/coverage 系列先行）在本批分支 Head 检出上复跑：**SUCCESS，合计 2901 测，0 failures、0 errors**；分项：public-git-checkout 15、public-only 24（skipped 1）、private-backend 2862（skipped 4）。
- 对账：正式基线 2894（12e6415d 管线正式验收）+ 7 = 2901，增量恰为本批新专项 7 测（该模块落 private-backend 分区执行）；skipped 总数 4 → 5，增量恰 1 = 新专项 web 巡检在组装树内的存在性守卫 skip（真实检出上全量执行、不计通过）。密封口径未动：237 文件 / 16,722,816 字节 / manifest `26b63e64…`，无换代。
- 本节数字为分支复跑对账；本批 Merge SHA 的管线正式验收与部署记录由关账批 E0363 直读补记。

## 6 五问简答

- 问一（新能力）：无新能力。本批为文案事实订正：人生总览大运维的退出说明此前误称方向与换算无审核规则，订正后与注册事实一致；用户可见行为除该段文字外零变化。
- 问二（来源）：订正依据为在册注册记录（E0346/E0348 分段注册、治理册条目与 Phase2 步/Golden），无新来源、无新规则、无新证据。
- 问三（真实可达）：合并部署后，人生总览大运维退出文案即为新文案（前端逐字渲染后端字段）；维度本身仍 not_available，呈现状态不变。
- 问四（先行条件）：不适用（非登记/接线批）；本批不翻转任何注册状态、不接线任何研究能力。
- 问五（做不到）：见 §7。

## 7 仍不可判断范围

- 大运时间线维度仍 not_available：总览组合未批准（双旗标硬编码 False 不变）、TJ-017.3 公开开放未裁定、TJ-017.2 跨规则调用未建；注册规则存在不等于总览可呈现大运。
- 岁运效力（大运吉凶与作用）无已建规则，总览与任何场景均不判断。
- 起运在已注册契约下只给交运时刻区间：单点交运日期与「起运岁数」单点值不可判断（虚岁/实岁无原典口径），本批文案如实保留此边界。
- 其余 3 个 not_available 维度（跨规则综合、旺衰喜用与格局判定、综合个人评价）的阻塞性质与文案均不在本批范围、未变更。

## 8 本批产出与边界

- 产出：本治理文档、引擎文案订正 1 处、公开专项 1 个（7 测）、fixture 镜像更新 1 处、validate.yml 接入 1 行、台账事件 E0362 与 TASK_STATUS 的 TJ-025.2 行续写。PR #539（止于 PR，不合并；合并与正式验收由关账 E0363 补记）。
- 未实施声明：本批未改 `scenario_engine.py` 的任何判定、旗标、标记派生与可用性逻辑，未改前端任何文件，未动密封资产、快照与 cicd 钉；TJ-025.2 行状态保持「已部署验收」不变（微项完成不改变本体关账）。
