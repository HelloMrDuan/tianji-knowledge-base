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

## 怎样追加下一条

1. 先确认选中的 `TJ-xxx.y` 真正达到了它在 WBS 中的验收条件。没有就仍记进行中、阻塞或 CI 待验，不造完成。
2. 在 `TASK_STATUS.md` 中**只改对应的一行**，附最新真实 PR / 检查状态 / SHA / 下一动作。
3. 在上表最后**追加一条**事件，编号递增，不改旧行（纠错也要新事件）。
4. 对应父任务仅当所有必要子项完成时才能变为已完成；本次若只验收子任务，不得给父任务打勾。
5. GitHub PR 必须运行 `python scripts/check_task_tracking.py --base <base-commit>`，确认本次恰好一个任务、一个新事件。PR 合并成功后再以**同一任务**单独做关账更新，补齐实际 main SHA。

**验收警戒线**：WBS 全部子任务数量 ≠ 已完成功能数量；公开 PR 合并 ≠ 私有 Canonical 完成；静态截图 ≠ 人工视觉还原；推送成功 ≠ 生产部署完成。
