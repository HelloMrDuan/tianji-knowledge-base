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

## 3 实现说明

- 唯一代码改动：`web/visual-prototype/src/public/MusicPlayer.tsx` 新增一个 effect（+13 行、零删改既有行）——注册 `visibilitychange` 监听，`document.visibilityState === "hidden"` 时仅调用 `audioRef.current?.pause()`；visible 分支刻意无任何动作（落实「不擅自重启」字面）；组件卸载时移除监听。
- 暂停经 audio 元素原生 `pause()` 触发既有 onPause → `playing=false`，播放指示与全局暂停键随之消失，UI 状态机与手动暂停完全同路。
- 刻意不调用 `pauseByChoice`：可见性暂停不写 optedIn、不触发 localStorage 变化（对平表 #7）；音量、持久化、默认不播、挂载不自动播放等既有口径逐字未动。
- 新增真实浏览器专项 `web/visual-prototype/tests/tj0092-music-visibility.spec.ts`（3 测）与专属 CI workflow `.github/workflows/tj0092-music-visibility-playwright.yml`（沿 tj0063 先例，步骤名如实标注测试性质）。

## 4 测试与等价核查

- 新专项（真实 Chromium、真实 dev server、真实组件与 audio 元素；仅浏览器自身可见性信号经 evaluate 覆写属性并派发真实 `visibilitychange` 事件模拟——无头 CI 无法按需把标签页真实切入后台，文件头已如实标注；无任何 API stub）：
  1. 播放中切 hidden → 元素暂停、播放指示消失、持久化偏好逐字不变（{volume: 0.5, optedIn: true}）；切回 visible 500ms 后仍暂停且 currentTime 冻结；其后可手动再播。
  2. 手动暂停（optedIn=false）后 hidden→visible 全程仍暂停、currentTime 冻结、偏好不变——手动暂停不被可见性行为覆盖。
  3. 从未播放的标签页 hidden→visible 后仍 paused 且 currentTime=0——不擅自开始播放。
- 本地执行：新专项 3/3 通过。**负对照**：临时撤下组件改动（基线代码）重跑同一专项，用例 1 恰失败（音乐在后台继续播放）、用例 2/3 通过（其性质为防过度恢复的守卫用例）——核心用例能真实识别缺失行为，非 vacuously-true。
- 回归（本地同环境）：prototype.spec.ts + b0084-mobile-a11y + tj0063-privacy 共 207 通过、2 失败；2 失败（prototype:51 首页标题探针、tj0063:127 出生档案删除回归）经基线同点复跑**逐项同失败**，为本机裸环境既有伪影、与本批改动无关（改动面仅 MusicPlayer 可见性监听）；其中既有音乐用例（手势播放/音量持久化/全局暂停/进 AdminApp 元素消失）通过。TypeScript `tsc --noEmit` 0 错误。
- 等价面：可见性行为之外，播放器开关、持久化、默认态与 AdminApp 读法 a 行为均由既有测试原样通过、零改动；后端与密封面零改动（§5 对账增量 0 佐证）。

## 5 机上复跑与基线对账

- 机上完整配方（`scripts/accept_offline.py --suite all`，分支检出 `14524880…` + live 快照 + cicd 钉 `26b63e64…` 开工直读对平）：**SUCCESS，合计 2901** = public-git-checkout 15（0 f/e）+ public-only 24（skipped 1）+ private-backend 2862（skipped 4），0 failures / 0 errors。
- 对账：正式基线 2901（7c80a26c）+ **0** = 2901——本批为纯前端行为补齐，Python 离线验收面无新增无减少，分项与 skipped 构成逐项一致。新增 Playwright 专项的权威执行面为其专属 GitHub CI workflow（与在册各浏览器专项同制），不计入离线验收总数。
- 密封口径未动：237 文件 / 16,722,816 字节 / manifest `26b63e64…`，无换代。

## 6 五问简答

- 问一（新能力）：无新命理能力。本批为既有产品行为补齐：背景音乐在标签页切入后台时停止、回到前台不自动重启，落实 WBS TJ-009.2 字面规格中此前未实现的一半。
- 问二（来源）：依据为 WBS 原文行与现行播放器实测，无新规则、无新证据、无新来源。
- 问三（真实可达）：合并部署后，真实用户在任意前台页面播放背景音乐、切换标签页即触发停止；回到标签页音乐保持停止，须手动再播。未播放过音乐的用户无任何可见变化。
- 问四（先行条件）：不适用（非登记/接线批）；不翻转任何注册状态。
- 问五（做不到）：见 §7。

## 7 仍不可判断范围

- TJ-009.2 行在本批后仍不关账：本批止于 PR，合并、管线正式验收与部署记录由关账批 E0365 补记后，行状态再行处置。
- 移动端浏览器对后台音频的系统级策略（操作系统强制暂停、音频焦点抢占）不在本批范围，本批只实现页面可见性语义。
- TJ-009.1（播放器持久化与默认静音）为 D 类陈旧行，其关账订正属 D 类订正批范围，本批未动。

## 8 本批产出与边界

- 产出：本治理文档、MusicPlayer 可见性处理（+13 行）、真实浏览器专项 1 个（3 测）、专属 CI workflow 1 个、台账事件 E0364 与 TASK_STATUS 的 TJ-009.2 行续写。
- 未实施声明：本批未改播放器视觉、默认不播与持久化口径、AdminApp 任何文件、任何后端与密封资产、快照与 cicd 钉；TJ-009.2 行状态保持「待做」不变（实现止于 PR，关账由 E0365 在正式验收与部署记录齐备后补记）。

## 9 关账（E0365）

本节由关账批 E0365 追加，§0 至 §8 原文一字未动。

### 9.1 合并与公开 CI

- 实现 PR #541 已由父级合并：Merge SHA `105d5dbce44b3e110f927d3351d960bfbe4d0ce4`（父 = 基线 `ccd6f201…`），最终 Head `c8ddb61750e826ab1b220f52380487648336a237`。
- 公开 CI：最终 Head 的 Actions workflow runs 全部 success、零失败，含本批专属 `TJ-009.2 Music Visibility Playwright`（run 41301105700）与 `Validate Public Code`（run 41301105742）；无卡死 job。

### 9.2 正式验收终局核对

- 关账批机上直读 `acceptance-105d5dbce44b3e110f927d3351d960bfbe4d0ce4.json`：result = SUCCESS，合计 **2901** = public-git-checkout 15（0 f/e、skipped 0）+ public-only 24（skipped 1）+ private-backend 2862（255 模块、skipped 4），failures 与 errors 均为 0，total_skipped 5。
- 与正式基线 2901（`7c80a26c` 管线正式验收）逐项一致：本批纯前端变更、离线验收面增量 0，与实现批 §5 分支复跑对账（2901）对平。
- 密封口径未动：237 文件 / 16,722,816 字节 / manifest `26b63e64bed736b08a7dcd686f6a75de733fd44ba9eec9195248e69730485329`，无快照换代。

### 9.3 部署终局核对

- `deploys.log`（关账批机上直读）：ACCEPTED 2026-11-01T11:43:00Z；**DEPLOYED 2026-11-01T11:43:30Z，pin `88ef7f893f0aaf7d8d776c44663142099181dd538ca4db3c7dd32bc5c06e1a67`**，health 与 bazi 探针 ok，web 镜像 tag 为本 Merge SHA `105d5dbc…`。

### 9.4 行状态处置：WBS 验收口径逐条对平

WBS TJ-009.2 原文（DETAILED_DELIVERY_BACKLOG_V1.md）：标题「进入后台停止音乐、离开后台不擅自重启」，范围 `PublicApp` 与 `AdminApp`，验收条件「背景音乐不进入后台、静音权限和浏览器 autoplay 控制生效」。逐条对平：

| WBS 口径 | 证据 | 结论 |
| --- | --- | --- |
| 背景音乐不进入后台（读法 a：进入 AdminApp） | 播放器仅挂 PublicApp，进入 AdminApp 时组件卸载、audio 元素消失；既有真实浏览器测试（prototype.spec.ts 音乐用例）断言 audio count 0 | 满足（E0364 前已成立，本批零改动） |
| 进入后台停止音乐（读法 b：标签页切入后台 hidden） | E0364 新增 `visibilitychange` 处理；新专项用例 1（播放中切 hidden 停播、播放指示消失、持久化偏好逐字不变）通过，且基线负对照恰该核心用例失败 | 满足（本批补齐） |
| 离开后台不擅自重启（读法 b：标签页回到前台 visible） | visible 分支刻意无任何动作；新专项用例 1（回前台 500ms 后仍暂停、currentTime 冻结、其后可手动再播）、用例 2（手动暂停不被 hidden→visible 覆盖）、用例 3（从未播放者全程静默、currentTime=0）全过 | 满足（本批补齐） |
| 离开后台不擅自重启（读法 a：自 AdminApp 返回） | 返回后播放器重新挂载、`playing` 初值恒 false、从不自动播放；既有真实浏览器测试在册 | 满足（本批零改动） |
| 静音权限和浏览器 autoplay 控制生效 | 默认 optedIn=false、播放只能由用户手势触发、挂载永不自动播放（即使持久化 optedIn=true）；既有真实浏览器测试在册 | 满足（本批零改动） |

- 结论：WBS 全部验收口径均有真实测试在册并满足，TJ-009.2 行状态由「待做」关账为「已部署验收」（事件 E0365）。移动端操作系统级后台音频策略不在 WBS 本任务口径内（§7 已记），不构成关账缺口。
- 门禁路径：本次处置恰为 1 个任务行状态变更 + 1 个新事件，走 legacy 单任务路径（无批次标记）；DONE 终态行与事件的 PR/SHA/CI 三列均填本批真实证据。

### 9.5 两面证据区分

- 离线正式验收（§9.2 的 2901）覆盖 Python 离线面，不执行任何浏览器专项；音乐可见性行为的权威执行面为其专属 GitHub CI workflow（真实 Chromium、真实组件与 audio 元素），与在册各浏览器专项同制。关账结论由离线验收与浏览器专项两面证据共同支撑，不以离线总数冒称浏览器行为已验。

### 9.6 机上清理与环境记录

- 机上 `/data/workspace/tj0092-e0364` 经关账批复核仅余 `repro1.log`（约 20K，日志按先例保留），组装与暂存已由实现批清理；本批临时监视脚本已删除；/data 已用 25%、余 15G。
- 环境记录：关账等待期间 SSH 一度中断（VM 替换清空 `/root/.ssh`），按 AGENTS.md 在册程序自 `~/.ssh/config` 还原并核对网关指纹一致后恢复；机上验收进程（accept_offline）未受影响，其后正式验收与部署记录均以恢复后第一手直读为准。
- 本批止于 PR，未自行合并；合并由父级执行。
