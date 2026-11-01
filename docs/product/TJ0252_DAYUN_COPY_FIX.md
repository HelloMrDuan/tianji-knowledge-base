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
| 6 | `tests/test_tj0252_life_condition_markers.py` 第 47 行 fixture | `"dayun": "大运方向、起运岁数、交运日期及岁运效力尚无完成审核的生产规
...[truncated 1898 chars]