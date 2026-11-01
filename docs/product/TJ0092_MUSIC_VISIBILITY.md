# TJ-009.2 背景音乐可见性行为补齐（E0364）

## 0 授权与范围

- 授权来源：全盘再审计 E0358（docs/product/PROGRAM_REMAINDER_AUDIT_E0358.md §3 TJ-009.2 行、§11 顺位 A3）将本项定级 A 类：web 源码全域无 `visibilitychange` 处理，WBS 字面要求的一半未实现，建议一只自包含小批（可见性处理 + 离开后台不自动重启语义 + Playwright 回归）。
- 任务定义以 WBS（docs/product/DETAILED_DELIVERY_BACKLOG_V1.md）TJ-009.2 原文为准：标题「进入后台停止音乐、离开后台不擅自重启」，范围 `PublicApp` 与 `AdminApp`，验收条件「背景音乐不进入后台、静音权限和浏览器 autoplay 控制生效」。
- 口径裁定（先行登记）：WBS 标题的「离开后台**不擅自重启**」为明确字面语义——页面回到前台时**不自动恢复播放**（无论此前是手动暂停还是被可见性暂停）。本批按此字面实现，不做「回前台按既有状态恢复」。
- 硬边界：不重做首页或播放器视觉；不改默认不播（optedIn 默认 false、挂载不自动播放）与持久化口径（localStorage `tianji.prototype.music` 的 volume/optedIn 语义）；TJ-009.1 的播放器持久化与默认静音已在主干（E0358 定级 D「已实测在主干」），本批不重复建设；无后端、无密封资产变更。
- 本批止于 PR，不自行合并；关账批 E0365 在合并与正式验收后另行派发。

## 1 开工核实与基线实测

- GitHub API main HEAD = `ccd6f2018053defbadef19a7e89faea515963334`（关账 PR #540 已合并），与任务书基线一致。
- 台账：TASK_HISTORY 事件连续至 E0363（363 事件）；TJ-009.2 行状态「待做」，备注「按 WBS 验收条件执行」。
- 正式验收基线：2901（Merge SHA `7c80a26c` 的管线正式验收 SUCCESS，E0363 关账在册）。
- 密封钉：`26b63e64…`（237 文件 / 16,722,816 字节）；本批预期无密封变更、无快照换代。
- 播放器实测（`web/visual-prototype/src/public/MusicPlayer.tsx`）：`playing` 由 audio 元素 onPlay/onPause 事件镜像；用户播放置 optedIn=true、用户暂停（toggle 或全局暂停键）经 `pauseByChoice` 置 optedIn=false；挂载时 `playing` 初值恒 false（即使持久化 optedIn=true 也不自动播放，弹窗文案「已记住你的音量，点击后继续播放」）；音量与 optedIn 经 effect 持久化；卸载时 pause。
- 挂载面实测：`MusicPlayer` 仅挂于 `src/public/PublicApp.tsx`（第 121 行）；`src/admin/AdminApp.tsx` 无播放器、无 audio 元素。
- 可见性实测：`grep -rn "visibilitychange|visibilityState|document.hidden" web/`（.ts/.tsx）**0 命中**——标签页可见性一半确未实现。
- 既有真实浏览器回归（`web/visual-prototype/tests/prototype.spec.ts` 用例 "original music requires a gesture, persists volume, pauses globally and on admin transition"）：真实 Chromium 执行，覆盖手势播放、音量持久化、全局暂停（optedIn→false）、reload 后不自动播放、切 AdminApp 后 audio 元素消失（count 0）。

## 2 WBS 要求 vs 现行实现对平表（先行登记）

| # | WBS 字面要求 | 现行实现实测 | 对平结论 |
| --- | --- | --- | --- |
| 1 | 进入后台停止音乐（读法 a：进入 AdminApp 后台） | 播放器仅挂 PublicApp；进入 AdminApp 时组件卸载、audio 元素消失，既有真实浏览器测试断言 `audio` count 0 | 已成立，本批不动 |
| 2 | 进入后台停止音乐（读法 b：标签页切入后台 hidden） | 全域无 visibilitychange 处理；播放中切后台音乐继续播放 | **未实现，本批补齐**：hidden 时暂停 audio 元素 |
| 3 | 离开后台不擅自重启（读法 a：自 AdminApp 返回） | 返回后播放器重新挂载，`playing` 初值 false，从不自动播放 | 已成立，本批不动 |
| 4 | 离开后台不擅自重启（读法 b：标签页回到前台 visible） | 无处理（且因 #2 缺失，音乐本就在后台继续） | **随本批落地**：visible 时不做任何恢复动作；被可见性暂停后保持暂停，须用户手动再播 |
| 5 | 静音权限和浏览器 autoplay 控制生效 | 默认 optedIn=false；播放只能由用户手势触发；挂载永不自动播放 | 已成立，本批不动 |
| 6 | （相容性）用户手动暂停不得被可见性行为覆盖 | 手动暂停 = audio 已 paused 且 optedIn=false | 本批设计保证：hidden 只 pause 元素（已暂停时无-op）；visible 无动作，永不覆盖手动暂停 |
| 7 | （相容性）持久化口径不变 | volume/optedIn 由既有 effect 持久化 | 本批设计保证：可见性暂停**不**写 optedIn（切标签页不是用户的暂停选择），不触发任何 localStorage 写入变化 |

- 「后台」双读法说明：WBS 标题与验收语在其成文语境中同时涵盖管理后台与标签页后台两读法；E0358 实测结论为读法 a 已结构性成立、读法 b 未实现，本表与之一致。本批只补读法 b，不改读法 a 的任何既有行为。
