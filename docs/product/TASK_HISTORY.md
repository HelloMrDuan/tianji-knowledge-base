# 天机平台｜原子任务状态变更日志

> 对应[任务状态表](TASK_STATUS.md)、[详细 WBS](DETAILED_DELIVERY_BACKLOG_V1.md)和[执行制度](TASK_EXECUTION_RULES.md)。  
> **2026-10-11 初次建账时**，E0001～E0008 是对之前实际 PR/CI 的事实回填，并非宣称此前每批已采用新制度。E0009 是本轮 `TJ-001.4` 认领事件。之后**严格追加**，旧事件不得删除、排序、覆盖；发现错误只能增加纠错事件。  
> 每次状态变化需有一个任务 ID、实证链接、变更结果与下一步；没有实际合并不能填完成。日后新增一次 PR/CI 更新只添加**一条新的事件**，同一 PR 不得为两个任务同时关账。

| 事件 | 日期（北京时间） | 唯一任务 ID | 事件后状态 | 本次实际变化/未完成界限 | 真实 PR / 分支 | 证据 SHA | CI/运行凭证 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0001 | 2026-10-11 | TJ-001.1 | 已合并 | 原始视觉/场景基线写入正式规划 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0002 | 2026-10-11 | TJ-001.2 | 已合并 | 逐页交互/输入/异常规格归档；属历史一次性批量计划 PR | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0003 | 2026-10-11 | TJ-001.3 | 已合并 | README 与细化规划入口已合并，历史规则不追溯适用一 PR 一任务 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221 | 07165cc5be8986b7ddd7f60863619c754cc2e355 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/221/checks |
| E0004 | 2026-10-11 | TJ-002.1 | 已合并 | 私有 #50 双回归核对：combined-main、merged-main-209 | https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50 | e0f95051a65dcdb5337853405a4e18a798eeb19d | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38069517719 |
| E0005 | 2026-10-11 | TJ-002.2 | 已合并 | 私有 #50 已按准确 head 完成合并 | https://github.com/HelloMrDuan/tianji-private-knowledge/pull/50 | e0f95051a65dcdb5337853405a4e18a798eeb19d | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38069517886 |
| E0006 | 2026-10-11 | TJ-004.1 | 已合并 | 11 场景 API 对应表与原首页差异审计合并；全场景异常矩阵另见 TJ-004.3 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224 | b42a1d89f2b7bcc7b3c2a75a168299ce7128285c | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38072602895 |
| E0007 | 2026-10-11 | TJ-004.2 | 已合并 | 11/11 真实入口成功、12/12 浏览器、524 Python、235 私有文件合并验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/225 | a9f0b276d2b506c0cb0768fcb74f57da01de72af | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38073174926 |
| E0008 | 2026-10-11 | TJ-008.2 | 进行中 | 首页主 CTA/四时间入口已合并，但 #87/#89 原图完整人工对照未验收 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/224 | b42a1d89f2b7bcc7b3c2a75a168299ce7128285c | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38072602895 |
| E0009 | 2026-10-11 | TJ-001.4 | 进行中 | 本次仅认领逐任务状态/追加日志/PR 校验制度；真实合并 SHA 后续关账 | 本 PR 尚待创建 | — | — |

| E0010 | 2026-10-11 | TJ-001.4 | 已合并 | 92 项独立状态表、追加式日志、逐 PR 单任务门禁和单测已通过并合并；无生产部署声明 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/228 | 6a22f29f2ec2e0b3a2bd9689c0dd9df5fd3d883d | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38101246241 |

| E0011 | 2026-10-11 | TJ-008.2 | 进行中 | 用户明确否决旧首页“一事占问”首位；本批改运势、桃花、事业财运首屏与三张重点卡，保留 #87 水墨/11 入口；新真实截图/视觉对照仍待 CI | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230 | — | — |

| E0012 | 2026-10-11 | TJ-008.2 | 已合并 | 按用户纠偏：首页运势主入口、桃花/事业辅助、前三张重点卡、手机适配；完整 11 页面原图审核仍属后续其他任务 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/230 | e00137addfd1ddd19d9d7080b13d8095d6b895f3 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38106598250 |

| E0013 | 2026-10-11 | TJ-008.3 | 进行中 | 开发单一工作包：今日、流年、桃花、事业财运由真实 Scenario 响应生成首屏可读摘要、来源数量与无依据边界；完整 11 场景报告未宣称完成 | 当前任务 PR 正在提交 | — | — |

| E0014 | 2026-10-11 | TJ-008.3 | 已合并 | 四个真实结果页先展示可读计算事实、可核对短引数量和明确不能判断的范围；公开四项 CI 与私有 7/7 Chromium、四张 390px 截图已验证；其余功能仍待完成 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/232 | 4f00515048d08ee92e998d08cc03a543756cfddc | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38109609969 |

| E0015 | 2026-10-11 | TJ-004.3 | 进行中 | 本批补真实前台 11 入口非法资料、断网恢复、来源缺失与请求乱序负例；真实超时/重复提交仍需补充，不因测试新增即宣布关闭 | 新 PR 尚待创建 | — | — |

| E0016 | 2026-10-11 | TJ-004.3 | 已合并 | 11 入口无效值、4 个年份非法区间、3 场景断网恢复、真实后端超时、防重复点击、缺源限界、乱序请求覆盖等回归 24/24 通过；未声称全部吉凶解释能力完成 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/234 | 283557b3e595ee8dc80be31b809a0a4315db8fa0 | https://github.com/HelloMrDuan/tianji-private-knowledge/actions/runs/38110293680 |

| E0017 | 2026-10-11 | TJ-004.4 | 进行中 | 依据用户确认的夜景古风图存档冻结视觉与播放器位置；提交桌面/手机页面骨架、11 场景及音乐真交互；完整 11 场景与 #87/#89 逐页差异仍待执行 | 设计分支 design/tj0044-night-ink-music-20261011，PR 待创建 | — | 本地 Chromium 1440/390/360 音乐与场景交互通过；仓库 CI 待验 |

| E0018 | 2026-10-14 | TJ-004.4 | 进行中 | 对 main@c615a33 构建产物真实 Chromium 取证：12 页 × 1440/390/360 共 36 张全页截图；音乐播放/暂停/音量/持久化/路由持续/默认静音/全局暂停 7/7 通过；差异台账已提交，主题级差异 D-01 待用户裁定，结果态比对待后端 | 本 PR（分支 tj-004.4-visual-diff-ledger） | — | 本地 original-design-home 5/5 通过；仓库 CI 待验 |

| E0019 | 2026-10-14 | TJ-004.4 | 已合并 | 审计交付完成：差异台账 v2（#87/#89 对照、严重程度、后续任务、D-01 双主题深青默认已裁定）+ 42 张截图归档 + tj0044-capture/music 可复现脚本（36/36、18/18 含后台停止）全部入库；结果态比对缺口如实保留待受控后端，未伪造；私有库无变更 | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/237 | ff9e9d11908cd27155b00cfb6595b224c5d06b98 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38534526334 |

| E0020 | 2026-10-14 | TJ-008.6 | 进行中 | 双主题技术基础开发启动：data-theme 主题机制（深青夜景默认/米白宣纸可选）、localStorage 偏好持久化、桌面+手机切换入口、index.html 内联初始化防首屏闪烁、异常值回退；WBS 已登记 TJ-008.6 | 本 PR（分支 tj-008.6-theme-foundation） | — | 真实 Chromium 三视口验证待执行；仓库 CI 待验 |

| E0021 | 2026-10-14 | TJ-008.6 | 已合并 | 双主题基础交付完成：主题机制/持久化/切换入口/防闪烁；WCAG AA 对比度门禁（夜景/宣纸双通过，零匹配选择器会 FAIL）；回归单测去硬编码；Chromium 25/25、页面回归 35/35；19 张双主题截图入库；未宣称首页精确还原（归 TJ-008.7） | https://github.com/HelloMrDuan/tianji-knowledge-base/pull/239 | 023543a9c4787333e614e1612321a83de65b21c0 | https://github.com/HelloMrDuan/tianji-knowledge-base/actions/runs/38542003719 |

| E0022 | 2026-10-14 | TJ-008.7 | 进行中 | 首页深青夜景真实视觉还原认领并登记：WBS 已新增 TJ-008.7，TASK_STATUS 标进行中；以 approved-reference.webp 为最高基准开始 React 还原 | 分支 tj-008.7-night-home-restoration（待建） | — | — |

## 怎样追加下一条

1. 先确认选中的 `TJ-xxx.y` 真正达到了它在 WBS 中的验收条件。没有就仍记进行中、阻塞或 CI 待验，不造完成。
2. 在 `TASK_STATUS.md` 中**只改对应的一行**，附最新真实 PR / 检查状态 / SHA / 下一动作。
3. 在上表最后**追加一条**事件，编号递增，不改旧行（纠错也要新事件）。
4. 对应父任务仅当所有必要子项完成时才能变为已完成；本次若只验收子任务，不得给父任务打勾。
5. GitHub PR 必须运行 `python scripts/check_task_tracking.py --base <base-commit>`，确认本次恰好一个任务、一个新事件。PR 合并成功后再以**同一任务**单独做关账更新，补齐实际 main SHA。

**验收警戒线**：WBS 全部子任务数量 ≠ 已完成功能数量；公开 PR 合并 ≠ 私有 Canonical 完成；静态截图 ≠ 人工视觉还原；推送成功 ≠ 生产部署完成。
