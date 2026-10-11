# 天机命理平台｜执行台账与验收看板

> [详细目录](README.md)｜[总纲](PRODUCT_MASTER_PLAN_V1.md)｜[原版设计截图](ORIGINAL_DESIGN_BASELINE_V1.md)｜[逐页 UI 规格](PAGE_SPECIFICATIONS_V1.md)｜[细化 WBS](DETAILED_DELIVERY_BACKLOG_V1.md)｜[分阶段计划](IMPLEMENTATION_PLAN_V1.md)  
> 基线建立：2026-10-11。**这是唯一持续更新的进度台账。** 此文件的 `待做` 不是“尚无任何相关代码”，而是“相应里程碑的完整验收尚未完成”。  
> 可核查记录优先级：实际 Actions / PR / commit / 受保护运行结果 ＞ 机器静态覆盖 ＞ 研究文档 ＞ 口头总结。

## 新增强制进度管理入口

**逐任务事实以 [TASK_STATUS.md](TASK_STATUS.md) 为准**（现有 92 项）；每次状态变化都必须在 [TASK_HISTORY.md](TASK_HISTORY.md) 追加事件，并遵守 [一任务一闭环制度](TASK_EXECUTION_RULES.md)。此文件保留父级里程碑与汇总，**子任务状态表与逐项日志是精确依据**，不把已经完成的子任务误读为父任务全部完成。

当前这批仅认领 `TJ-001.4`，在真实合并+回填前仍记为进行中，不能直接标完整制度已交付。历史 PR 已合并事实保留；最初视觉 #87/#89 仍强制遵守。

## 已完成的原子任务追踪机制 TJ-001.4

- 实际实现：[公开 PR #228](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228) 已合并 `6a22f29f2ec2e0b3a2bd9689c0dd9df5fd3d883d`；原子任务/WBS 校验、追加式事件、9 项针对漏账/假关账/修改旧日志的回归测试和前端/公开数据门禁通过。
- **唯一任务回填**：[任务状态表 TJ-001.4](TASK_STATUS.md) 更新为“已合并”，[任务日志 E0010](TASK_HISTORY.md) 保留完整 main SHA 和 CI 凭证。本次没有将其他子任务一并标记完成。
- 以后每次开发**只认领一个子任务、及时更新一行状态、追加一条日志、双仓必要时各自验收，最终同 ID 结账**。任务仍未完成就保留真实待验/阻塞，不许修改旧日志造成功。
- 历史 #53 组合回归另按原项目计划收尾，**本次 TJ-001.4 不借此宣称其他任务完成**。

## 当前项目总览

| 维度 | 快照事实（不是完整发布承诺） |
| --- | --- |
| 公开主分支 | `17e565b8c5acf2d257de33ad12a2019a049e824e`，三项公开主分支 CI success |
| 私有主分支 | `5f810546700e9e60a2661bcf024d96719686cf85` |
| 最近双仓已完成批次 | 公开 [#218](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/218) + 私有 [#49](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/49)，524 项 Python 测试/235 文件/真实浏览器合格 |
| 遗留待验 PR | 私有 [#50](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50)，两条组合 CI 均 **success**，已于本轮按准确 head SHA 合并，私有 main=`e0f95051a65dcdb5337853405a4e18a798eeb19d` |
| 11 个生活入口 | 11 个有限体验页有入口；**并非 11 个完整测算产品** |
| 16 产品知识分级 | 4 PRODUCTIZABLE / 10 PARTIAL / 1 BLOCKED_ADVANCED / 1 NOT_BUILT |
| 梦境知识 | 十种具体审核文化场景；完整 AI 解梦不具备发布资格 |
| 古风页面与音乐 | 已有，但移动端/性能/完整用户任务仍需验收 |
| 管理后台 | 有管理页面与部分受保护 API，完整权限治理/可写 CMS 未验证 |
| 上线 | 本次未核验实际用户可访问的生产域名、HTTPS 网关和线上运行验收，**不能写“已经上线”** |

## 状态字典

- `待做`：计划已批准，但完整工作未开始；可能存在旧研究/部分代码。
- `进行中`：有实际仓库更改/验收任务正在执行。
- `已提交PR`：分支和 PR 已存在，但未达到双仓成功门禁。
- `CI待验`：指定 head SHA 的 Actions 未全部完成或尚需修复。
- `已合并`：通过要求的 PR 检查并进入相关 `main`，**不表示已上线**。
- `已部署验收`：真实受控服务成功、权限及用户端到端验收通过。
- `阻塞`：依赖证据/流派/真实模型/权限/部署尚未解决，保持弃判。

## 唯一排序的待办队列

> 任务 ID 与详细验收见[实施计划](IMPLEMENTATION_PLAN_V1.md)。一次只提取第一个“前置条件已满足、可产生真实变更”的 P0/P1 项，禁止直接跳到 M7。

| 顺位 | ID | 任务 | 当前状态 | 前置/备注 |
| --- | --- | --- | --- | --- |
| 1 | TJ-001 | 合并产品总纲、分阶段计划、台账及 README 导航 | 已合并 | [公开 #219](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/219)，merge `897aab38ee17c95b3015e449b9bf5557f833bd55`；PR 三项 CI 全绿 |
| 2 | TJ-002 | 私有 #50 最终组合回归收口 | 已合并 | 两条组合 CI 均 success；私有 [#50](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50) 已按准确 head SHA `b9a7097` squash merge `e0f95051a65dcdb5337853405a4e18a798eeb19d` |
| 3 | TJ-004 | 11 场景真实 API＋浏览器成功/异常清单 | 进行中 | **TJ-004.1/.2/.3 已合并**：11/11 真实场景、[公开 #234](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/234) 与 [私有 #56](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/56) 异常回归 **24/24**、公开四门禁成功。**TJ-004.4 原始设计逐页视觉比对仍未完成，父任务不能标完成** |
| 4 | TJ-003 | 公共/私有敏感数据表面、迁移和证据权利核验 | 待做 | 可与 TJ-004 的只读审查并行 |
| 5 | TJ-006 | 多场景日期/出生资料/年份/时区一致性 | 待做 | 已有 #215/#216 等部分实现，验收尚需全流程 |
| 6 | TJ-007 | 11 入口从输入到结果/证据/弃判闭环 | 待做 | 使用 TJ-004 实际缺陷作为改代码顺序 |
| 7 | TJ-008 | **运势/桃花/事业用户优先与可读结果，保留古风设计** | 进行中 | **TJ-008.2、TJ-008.3 两个子项均已合并**；首页 #230/#54；四个结果页可读摘要公开 [#232](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/232) `4f00515`、私有 [#55](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/55) `5e35a87`，7/7 真实浏览器和手机图通过。**TJ-008.1/.4/.5 与 TJ-004.4 其他 UI 验收未完成，父任务不能标完成** |
| 8 | TJ-009 | 背景音乐/路由/无障碍一致性 | 待做 | 保留现有音乐功能，不做强制自动播放 |
| 9 | TJ-005 | 受控真实后端/公开 API 环境与可部署性 | 待做 | 须满足 TJ-003 安全门禁；不能因没有云资源伪造上线 |
| 10 | TJ-010 | 月令、根、透干、分日冲突审核 | 待做 | 八字知识核心依赖 |
| 11 | TJ-011 | 有界旺衰正反例及弃判扩围 | 待做 | 依赖 TJ-010 |
| 12 | TJ-012 | 格局候选条件与古籍分歧处理 | 待做 | 依赖 TJ-011 与原典核对 |
| 13 | TJ-013 | 喜用神各流派分开裁决 | 阻塞 | 依赖 TJ-011/012，未经审核不计算通用喜用神 |
| 14 | TJ-014 | 大运顺逆法源与显式用户口径 | 待做 | 历史分类不得推断现实身份 |
| 15 | TJ-015 | 节界/天文提供方/历史时区/零秒校核 | 待做 | 已有研究级校验，不代表独立天文认证 |
| 16 | TJ-016 | 起运比例、取整、虚实岁、实际交运法研究 | 阻塞 | 先 TJ-014/015 原典与独立校核；现有模拟不能发布 |
| 17 | TJ-017 | 真实交运时间轴及原局/岁运关联 | 阻塞 | 依赖 TJ-011/012/014/015/016 |
| 18 | TJ-018 | 梦境版本/版权/逐条出处审核 | 待做 | 整书与未审主题仍须隔离 |
| 19 | TJ-019 | 严格新增具体梦境条目 | 阻塞 | 依赖 TJ-018，不以词表代替审核 |
| 20 | TJ-020 | 有界梦境语义识别与反例 | 待做 | 已有部分真实匹配，需扩充边界回归 |
| 21 | TJ-021 | 梦境可读结果页及 AI 禁止过度解释 | 待做 | 可先做有限文化查阅，不提前开 AI |
| 22 | TJ-022 | 桃花姻缘条件性、可追溯解释 | 阻塞 | 依赖八字/流年已审作用 |
| 23 | TJ-023 | 事业财运多规则解释 | 阻塞 | 依赖旺衰/格局/大运的适用条件 |
| 24 | TJ-024 | 双人合盘关系解释与冲突弃判 | 阻塞 | 已有结构矩阵，但现实关系判断未授权 |
| 25 | TJ-025 | 人生总览跨场景证据聚合/解释 | 阻塞 | 依赖 TJ-022/023/024 和独立核验 |
| 26 | TJ-026 | 管理后台真实只读/写权限与审计 | 待做 | 必须先证实鉴权与私有数据隔离 |
| 27 | TJ-027 | 线上可观测性、回滚、性能 | 待做 | 依赖 TJ-005 部署 |
| 28 | TJ-028 | 实际模型接入、领域级引用质量与人审 | 阻塞 | 没有可验真实模型时 AI 保持关闭 |
| 29 | TJ-029 | MVP 灰度与用户行为反馈 | 待做 | 真实部署后验收 |
| 30 | TJ-030 | 5 个专业工具按域扩展 | 待做 | P3，不能影响八字/解梦/生活场景主线 |

## 细化规划已合并的记录（与页面实际修复分开）

- **TJ-001.1～TJ-001.3 规划补充**：公开 [PR #221](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221)，合并 `07165cc5be8986b7ddd7f60863619c754cc2e355`；落地原始设计基准、逐页规格、30 项工作包拆分、README 导航与标准 PR 模板。PR code/frontend-build/gate-public-data 三项成功。**这只是规划与设计基线已合并，不表示 TJ-008 页面视觉整改或 TJ-004 真实全站验收已完成。**
- **原设计真实参考**：[PR #87](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/87)（73 个截图路径）与 [PR #89](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/89)（生活场景 IA）。已核对计划所引用的 23 个固定路径存在，**尚未完成页面的新旧图逐屏人工对比**。
- **执行顺序不变**：TJ-002 已按真实 PR/CI 合并，下一步 TJ-004.1～004.4（11 场景真实测试＋原图差异）；然后才 TJ-008.1～008.5 一批批还原页面。

## 视觉还原待检查问题（首页快捷入口已修；其余仍待验）

| UI / 参考 | 当前现状 | 接下来必须做 |
| --- | --- | --- |
| UI-00 首页 Hero | 旧 #224 把一事占问设主 CTA，**用户已明确指出错误**；[新 #230](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230) 修为今日运势主 CTA、桃花/事业辅 CTA、首排突出三项 | **这是 TJ-008.2 在进行中的纠偏**；CI、1440/390/360 新图与 #87 水墨视觉复核均待完成。不能将旧 #224 UI 排序当最终设计 |
| UI-00 时间带 | **已新增今日/本周/本月/年度四入口**，跳转到既有真实场景 | #224/#51 浏览器链接和布局通过；年度仍由具体页面自选，不在首页写死 2026 |
| UI-00 场景入口 | 11 张卡已存在；#89 曾规划事业/财运分卡但共用核心 | 对照场景卡结构与底层同一次计算，避免拆成两份结果 |
| UI-01 手机导航 | 当前为首页/占问/历史/收藏；#89 设计语义为首页/场景/记录/我的 | 设计映射、收藏兼容与安全可达，不能直接删用户入口 |
| UI-P1～P7 | 旧专业部分页面属于固定示意/设计结果模板 | 保留最初七域图形样式，但不伪装已经实时排盘 |
| UI-A01～A18 | #87 16 管理页是 DEMO 视觉；现在有部分真实受控 API | 核对原侧栏/表格/抽屉风格与实际权限，权限未实现的写操作禁用 |
| 全站音乐 | 已有可控播放器，旧设计要求后台静音 | 加真实浏览器跨路由/后台状态测试，不以单张截图验证播放 |

每个 UI 子任务必须关联[视觉基线](ORIGINAL_DESIGN_BASELINE_V1.md)与[页面规格](PAGE_SPECIFICATIONS_V1.md)中的固定截图；提交时登记原图、新图、CI 与差异结果。

## 2026-10-11 用户首页优先级纠偏（TJ-008.2，尚未验收）

- 用户明确要求以**运势（今日/周/月/流年）→ 桃花 → 事业财运**作为产品首页主线。原 #87 是古风视觉参考；原 #89 是生活场景优先参考，**其中“一事占问主 CTA”已被用户推翻，不能再按旧计划恢复**。
- [公开 PR #230](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230) 实际改首页 CTA、排序、三张重点卡和新版回归用例。本次仍是 `TJ-008.2` 一项，原 WBS 与用户新要求并存；**现已通过公开四项 CI、私有真实浏览器 8/8、1440/390/360 首页新图审查，并合并 #230/#54；本次只关闭 TJ-008.2，其他页面仍待验**。
- [逐任务状态表](TASK_STATUS.md) 与[追加日志 E0011](TASK_HISTORY.md)记录本次变动；历史 #224 截图/合并事实保留，不能删除改写旧记录。

## 最近已合并的真实工作（历史事实，不重复当新任务）

| PR | 交付 | 已有验证 |
| --- | --- | --- |
| 公开 [#215](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/215) / 私有 [#43](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/43) | 人生总览跨场景本地出生资料复用 | 公开 CI + 私有真实 API/浏览器 |
| 公开 [#216](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/216) / 私有 [#45](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/45) | 日/周/月/合盘共用合法日期资料 | 公开 CI + 私有全量 520 项及浏览器 |
| 公开 [#217](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/217) / 私有 [#47](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/47) | 审核蛇梦“梦到”的有界识别 | 522 项 Python、235 私有文件及真实浏览器 |
| 公开 [#218](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/218) / 私有 [#49](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/49) | 大运模拟固定历法节界与日主重验 | 524 项 Python、235 私有文件及真实浏览器 |

## 每批结束必须填的交付记录

在本台账末尾按下面模板**追加一行**（不可仅在聊天中口头说完成），并同步更新上表对应任务状态：

| 日期（北京时间） | ID | 目标与用户可见变化 | 公开 PR/main SHA | 私有 PR/main SHA | 真实测试/CI | 部署状态 | 新缺口 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-11 | TJ-001 | 三份文档、导航与计划基线（本批） | [公开 #219](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/219)，merge `897aab38ee17c95b3015e449b9bf5557f833bd55` | 无私有知识改动 | PR code/frontend-build/gate-public-data 三项 success；合并后 Actions 单独核对 | 未部署 | 下批 TJ-002、TJ-004 |
| 2026-10-11 | TJ-001.1～001.3 | 按原设计补详细规划：视觉基线、逐页规格、WBS 和 PR 模板 | [公开 #221](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221)，merge `07165cc5be8986b7ddd7f60863619c754cc2e355` | 无私有数据改动 | PR 三项公开 CI 全绿，合并后 CI 另行核对 | 未部署 | TJ-004.4/TJ-008 视觉对照仍待实际实施；先完成 TJ-002 |

| 2026-10-11 | TJ-002 | 私有合并回归 PR #50 收口；没有改动古籍知识 | 无公开功能修改 | [私有 #50](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50) merge `e0f95051a65dcdb5337853405a4e18a798eeb19d` | `merged-main-209` / `combined-main` 两条原 PR head CI success，mergeable=clean | 未部署 | 下项 TJ-004.1～004.4，逐页真实验收和原设计对照 |
| 2026-10-11 | TJ-004.1 / TJ-008.2 | 11 场景接口静态初审及原首页首屏修复：一事占问主 CTA、四时间导航 | [公开 #224](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224) merge `b42a1d89f2b7bcc7b3c2a75a168299ce7128285c` | [私有 #51](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/51) merge `467fbd8dbe33c425251bebe1bf52fa839cf50aea` | 公开三门禁、私有 Canonical＋真实 Chromium 全绿；[截图工件](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38072602895) 已生成 1440/390/360 | 未部署 | 原图完整视觉人工比对未完成；TJ-004.2 后续 #225/#52 已合并，参见下一行 |

| 2026-10-11 | TJ-004.2 | 11 个生活入口真实用户页面分别提交后端并呈现限定结果，附 1 条出生时间必填反例 | [公开 #225](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/225) merge `a9f0b276d2b506c0cb0768fcb74f57da01de72af` | [私有 #52](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/52) merge `416b5ef98544f4ec125f2eb807593c3d4a61009e` | [私有真实 CI](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38073174926)：11/11 实际页面 POST、12/12 浏览器、524 Python、235 私有文件均 success；公开 main 三项 success | 未部署 | [私有 #53](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/53) 固定最终合并版双回归待结束；TJ-004.3/004.4 仍需扩展 |

示例“已合并”的判定必须有**真实 merged PR**和 `main` SHA；如 CI 还在跑，保持 `CI待验`。无可证实的模型、上线或内部知识授权不得补写“成功”。

## TJ-008.2 正式完成记录（2026-10-11）

- 用户纠偏已真实交付：运势主 CTA、桃花/事业次级 CTA、三张优先大卡、其余 8 场景仍可达；#87 水墨、宣纸、古风音乐与七域专业入口保留。
- 公开 [PR #230](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230) merge `e00137addfd1ddd19d9d7080b13d8095d6b895f3`；私有 [PR #54](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/54) merge `b529ce61320fd53f6fa088207d88e9dcc9ec72b4`。
- 真实验证：公开 code/frontend-build/gate-public-data/atomic-task-tracking **4/4 success**；私有轻量真实 API + Playwright **8/8**，1440/390/360 截图已实际查看，未重复跑无需改动的 524 Python/Canonical。
- [任务状态 TJ-008.2](TASK_STATUS.md) “已合并”，[追加记录 E0012](TASK_HISTORY.md)；**父任务 TJ-008 仍进行中**。未部署、未声称全部高级命理结论或 11 页原图视觉完成。

## TJ-008.3 已合并：运势/桃花/事业财运可读结果（2026-10-11）

- 公共 [PR #232](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/232) 已合并 `4f00515048d08ee92e998d08cc03a543756cfddc`，私有 [PR #55](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/55) 已合并 `5e35a87030c4c6f2b094c24d0bb02d40b74b35ff`。
- 真实后端上的 **7/7 Playwright** 通过，四张 390px 真实结果截图已查看；包含今日、流年、桃花、事业财运、年份请求一致性、无提交不生成结果与日周月来源回归。公开四项 CI 成功。
- 只归纳真实 Scenario 字段，缺失字段不填，公开来源短引缺失不补写；保留原典/Trace 展开和未裁定声明。**无新增旺衰喜用、大运/婚期/发财预测规则，不声称 11/11 结果报告完整或已部署。**
- [子任务状态](TASK_STATUS.md)已记 TJ-008.3“已合并”，[追加日志](TASK_HISTORY.md)为 E0014；后续 TJ-004.3 异常矩阵、TJ-008.4 移动全站和知识缺口按各自任务推进。

## TJ-004.3 已合并：11 场景异常与边界验证（2026-10-11）

- 公开 [#234](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/234) merge `283557b3e595ee8dc80be31b809a0a4315db8fa0`，私有 [#56](https://github.com/HelloMrDuan/tianji-private-knowledge/pull/56) merge `99218de320468f3cddf3858c0a9b4cb6ea590b08`。
- [真实工作流](https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38110293680) **24/24**，覆盖 11 类用户输入必填、目标年份越界、断网与超时重试、无 Evidence 返回、重复提交、旧响应晚回仍不能覆盖新结果；既有八字结果变化回归。全套公开 4/4 CI 通过。
- 第一次发现测试框架无 `toBeInvalid`，已改用浏览器 `checkValidity()`；任务追踪单测中不合理的“必须始终待做”硬编码也已修正。真实计算算法/古籍正文未更改。
- [TASK_STATUS.md](TASK_STATUS.md) 对应 TJ-004.3 “已合并”，[TASK_HISTORY.md](TASK_HISTORY.md) 追加此次完成事件。**TJ-004.4 全站古风原图验收和完整知识规则仍未完成**。

## 计划变更机制

如需新增或重排功能：先在[总纲](PRODUCT_MASTER_PLAN_V1.md)里说明用户价值和目标差异，再在[分阶段计划](IMPLEMENTATION_PLAN_V1.md)中列出 ID、依赖、验收，最后改本表顺序并提交 PR。只有安全紧急事件允许先修后补台账。未合并的研究内容不提升发布状态；**优先修复真实产品闭环，不继续无止境增加零散技术报告**。

