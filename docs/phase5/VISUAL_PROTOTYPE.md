# Phase 5 · 整站页面设计与验收

整站共 **33 个主页面：17 个前台页面、16 个后台页面**。12 个新增后台模块另有可直达的记录详情（每模块 3 条 DEMO 记录），支持字段、关联关系、审核轨迹切换。三个既有资产模块保留可访问的详情弹窗。

本轮为可交互设计原型：表单、校验、筛选、详情、状态切换和本地收藏可操作。没有接入排盘、AI、认证、真实资产读写或生产部署。全部后台记录为虚构 DEMO 数据；原型不改变引擎、知识资产、来源等级、生产 Prompt 或任何晋级状态。

## 页面与截图

截图从实际运行页面捕获，桌面视口 1440 × 1000、手机视口 390 × 844；桌面图为长图，手机图为首屏。浏览器截取内容区时可能排除滚动条宽度。下表覆盖全部主页面。

| 前台页面 | 路由 | 内容 | 桌面 | 手机 |
|---|---|---|---|---|
| 总首页 | `/` | 七个工具入口、山水、示例、音乐 | [查看](visual-prototype/screenshots/home-desktop.png) | [查看](visual-prototype/screenshots/home-mobile.png) |
| 历史记录 | `/history` | 搜索、工具筛选、固定示例 | [查看](visual-prototype/screenshots/history-desktop.png) | [查看](visual-prototype/screenshots/history-mobile.png) |
| 收藏 | `/favorites` | 本地收藏、取消收藏、空状态 | [查看](visual-prototype/screenshots/favorites-desktop.png) | [查看](visual-prototype/screenshots/favorites-mobile.png) |
| 八字首页 | `/bazi` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/bazi-home-desktop.png) | [查看](visual-prototype/screenshots/bazi-home-mobile.png) |
| 八字结果 | `/bazi/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/bazi-result-desktop.png) | [查看](visual-prototype/screenshots/bazi-result-mobile.png) |
| 六爻首页 | `/liuyao` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/liuyao-home-desktop.png) | [查看](visual-prototype/screenshots/liuyao-home-mobile.png) |
| 六爻结果 | `/liuyao/result` | 固定六爻示例与详情 | [查看](visual-prototype/screenshots/liuyao-result-desktop.png) | [查看](visual-prototype/screenshots/liuyao-result-mobile.png) |
| 奇门遁甲首页 | `/qimen` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/qimen-home-desktop.png) | [查看](visual-prototype/screenshots/qimen-home-mobile.png) |
| 奇门遁甲结果 | `/qimen/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/qimen-result-desktop.png) | [查看](visual-prototype/screenshots/qimen-result-mobile.png) |
| 紫微斗数首页 | `/ziwei` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/ziwei-home-desktop.png) | [查看](visual-prototype/screenshots/ziwei-home-mobile.png) |
| 紫微斗数结果 | `/ziwei/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/ziwei-result-desktop.png) | [查看](visual-prototype/screenshots/ziwei-result-mobile.png) |
| 大六壬首页 | `/liuren` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/liuren-home-desktop.png) | [查看](visual-prototype/screenshots/liuren-home-mobile.png) |
| 大六壬结果 | `/liuren/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/liuren-result-desktop.png) | [查看](visual-prototype/screenshots/liuren-result-mobile.png) |
| 周易首页 | `/yijing` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/yijing-home-desktop.png) | [查看](visual-prototype/screenshots/yijing-home-mobile.png) |
| 周易结果 | `/yijing/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/yijing-result-desktop.png) | [查看](visual-prototype/screenshots/yijing-result-mobile.png) |
| 风水首页 | `/fengshui` | 专属输入表单、示意图、输入校验与资料摘要 | [查看](visual-prototype/screenshots/fengshui-home-desktop.png) | [查看](visual-prototype/screenshots/fengshui-home-mobile.png) |
| 风水结果 | `/fengshui/result` | 领域结果布局、等待 / 计算中 / 失败状态 | [查看](visual-prototype/screenshots/fengshui-result-desktop.png) | [查看](visual-prototype/screenshots/fengshui-result-mobile.png) |

| 后台页面 | 路由 | 内容 | 桌面 | 手机 |
|---|---|---|---|---|
| 仪表盘 | `/admin` | 审核队列与治理概览 | [查看](visual-prototype/screenshots/admin-dashboard-desktop.png) | [查看](visual-prototype/screenshots/admin-dashboard-mobile.png) |
| 古籍管理 | `/admin/classics` | 筛选、章节范围与只读详情 | [查看](visual-prototype/screenshots/admin-classics-desktop.png) | [查看](visual-prototype/screenshots/admin-classics-mobile.png) |
| 章节管理 | `/admin/chapters` | 章节锚点、文本范围与审核 | [查看](visual-prototype/screenshots/admin-chapters-desktop.png) | [查看](visual-prototype/screenshots/admin-chapters-mobile.png) |
| 术语管理 | `/admin/terms` | 写法、释义与关联 | [查看](visual-prototype/screenshots/admin-terms-desktop.png) | [查看](visual-prototype/screenshots/admin-terms-mobile.png) |
| 规则管理 | `/admin/rules` | 算法口径、关联依据与详情 | [查看](visual-prototype/screenshots/admin-rules-desktop.png) | [查看](visual-prototype/screenshots/admin-rules-mobile.png) |
| Evidence 管理 | `/admin/evidence` | 必要片段、等级与审核 | [查看](visual-prototype/screenshots/admin-evidence-desktop.png) | [查看](visual-prototype/screenshots/admin-evidence-mobile.png) |
| 来源管理 | `/admin/sources` | 类型、版本与独立性 | [查看](visual-prototype/screenshots/admin-sources-desktop.png) | [查看](visual-prototype/screenshots/admin-sources-mobile.png) |
| RAW / Quarantine / Canonical | `/admin/layers` | 审核流程、分层与晋级门槛 | [查看](visual-prototype/screenshots/admin-layers-desktop.png) | [查看](visual-prototype/screenshots/admin-layers-mobile.png) |
| 流派与冲突 | `/admin/conflicts` | 并列口径比较与处理策略 | [查看](visual-prototype/screenshots/admin-conflicts-desktop.png) | [查看](visual-prototype/screenshots/admin-conflicts-mobile.png) |
| 算法与 Variant | `/admin/algorithms` | 领域、约定与验证关系 | [查看](visual-prototype/screenshots/admin-algorithms-desktop.png) | [查看](visual-prototype/screenshots/admin-algorithms-mobile.png) |
| AI Provider / Model | `/admin/providers` | 连接配置预览、用途与超时 | [查看](visual-prototype/screenshots/admin-providers-desktop.png) | [查看](visual-prototype/screenshots/admin-providers-mobile.png) |
| Prompt 版本 | `/admin/prompts` | 指令草稿编辑与版本阅读 | [查看](visual-prototype/screenshots/admin-prompts-desktop.png) | [查看](visual-prototype/screenshots/admin-prompts-mobile.png) |
| Eval / Golden Cases | `/admin/evaluations` | 状态阅读板与评测案例 | [查看](visual-prototype/screenshots/admin-evaluations-desktop.png) | [查看](visual-prototype/screenshots/admin-evaluations-mobile.png) |
| 失败案例 | `/admin/failures` | 错误阶段、复现说明与跟进 | [查看](visual-prototype/screenshots/admin-failures-desktop.png) | [查看](visual-prototype/screenshots/admin-failures-mobile.png) |
| 用户与权限 | `/admin/users` | 角色矩阵与敏感操作边界 | [查看](visual-prototype/screenshots/admin-users-desktop.png) | [查看](visual-prototype/screenshots/admin-users-mobile.png) |
| API / 系统日志 | `/admin/logs` | 请求阶段时间线与追踪记录 | [查看](visual-prototype/screenshots/admin-logs-desktop.png) | [查看](visual-prototype/screenshots/admin-logs-mobile.png) |

后台详情地址采用 `/admin/{模块}/{DEMO 编号}`。例如 `/admin/prompts/DEMO-PR001`、`/admin/layers/DEMO-L002`、`/admin/logs/DEMO-LG001`。刷新可直达，未知编号显示缺失记录页。章节、术语、来源、分层、冲突、算法、模型、Prompt、评测、失败、权限和日志均具备详情视图。

[手机完整六爻盘面](visual-prototype/screenshots/liuyao-chart-mobile.png)。总首页、六爻结果、仪表盘和三个资产管理页还保留 `-mobile-full.png` 长图。固定移动导航在长截图里的位置对应截图时的视口，实际滚动时保持贴屏。

## 设计方向

前台采用编辑式排版：米白纸色、深青文字、铜色小印、中文衬线标题与系统无衬线正文。山水改为曲线轮廓，移动首页压缩开场区域，重要提示与辅助正文提高字号。七个领域共用间距、表单和导航体系，各自配四柱、六爻、九宫、十二宫、四课三传、八卦或罗盘结构图。所有结构图明确为固定示意。

后台采用独立的浅灰与白色工作台，不含前台纹理、山水或音乐。管理列表、可横向滚动表格与移动抽屉统一；审核流程、口径比较、模型设置、指令编辑、评测阅读板、权限矩阵与日志时间线分别适配用途。DEMO 状态不能被误认为生产审核或测试结果。

## 输入、结果与状态

- 出生类表单：历法、日期、时间、传统性别口径；时区固定为北京时间（中国标准时间 UTC+8），不提供其他时区选项；农历选择显示闰月字段。紫微增加安星和晚子时口径。日期控件录入数字日期，本轮不做农历合法性或公农历转换验证。
- 占时类表单：日期、时刻、固定北京时间（UTC+8）、明确口径和选填问题。六爻按初爻至上爻录入 6/7/8/9，缺少任一值不提交。
- 周易：六十四卦、爻位和研究方向；风水：角度采用 [0, 360) 范围，区分坐向与朝向。
- 确认资料只展示输入摘要；修改、清空或跨工具切换清除摘要。出生和占时资料不写入 localStorage、历史或服务器。
- 六爻结果保留基础信息、盘面、结构结论、规则、必要典籍片段、AI 待接入与默认折叠的推演过程。手机可切换简洁 / 完整盘面，后者直接显示六神、六亲与纳甲。
- 其余六个结果页已具备领域结构、字段位置和等待 / 计算中 / 失败设计，没有虚构命盘、规则命中、来源或 AI 内容。状态按钮只展示布局，没有计算请求。
- 历史列表为固定样例；收藏仅保存“是否收藏六爻样例”的本地偏好。空列表与无匹配记录有明确返回路径。
- 管理列表提供查询、状态筛选和缺失结果反馈；模型配置和 Prompt 草稿可在页面内预览，刷新后清除，不采集密钥，不执行保存、发布或调用。

## 组件与边界

`src/public/domainPages.ts` 定义七域输入和阅读内容；`DomainHomePage.tsx` 实现工具资料页；`ResultTemplatePage.tsx` 实现六域结果与状态设计；`LibraryPage.tsx` 实现历史和收藏。

`src/admin/modules.ts` 定义 12 个模块的虚构记录；`ModulePage.tsx` 实现专属工作区、列表与独立详情。原有 `AssetPage.tsx` 保留古籍、规则和 Evidence 三种管理示例。所有后台导航入口已关联实现页面；真正未知的路由仍显示未找到页。

前台仅提供工具与当前结果相关必要片段，没有完整古籍、RAW、Quarantine、全量证据或 Prompt 浏览入口。后台当前尚无认证或服务端授权，只有虚构 DEMO 数据；真实内部数据接入前需要真实权限服务。静态路由分离不是生产安全边界。

《三命通会》的 raw snapshot、PUA / OCR collation、`quarantine_only`、`canonical_ready=false` 与 Canonical 缺失状态均未修改。C/D 来源不因视觉设计变为 A/B。

音乐默认关闭、需要主动播放，支持全局暂停与音量偏好，进入后台时停止；SVG 图形和音乐沿用本项目原创素材，不加载外部资源。此前 Benchmark PR #86 仅为架构参考，本轮新增页面由本项目实现，没有声称观察或复制未验证的竞品页面。

## 验证与交付

- `npm ci` 与 `npm run build` 通过。
- **137 项 Playwright 检查通过**：33 个主路由 × 1440/390/360 三种宽度，无整页横向溢出、运行错误、外部或 API 请求；验证输入边界、隐私资料清除、完整盘面、结果状态、历史收藏、详情直达、筛选、草稿预览和音乐。
- 66 张主页面桌面 / 手机截图、6 张手机长图及 1 张完整盘面截图已从运行页面更新。
- 原型 PR 保持草稿；当前完成页面设计，不部署、不合并上线。真实引擎与服务接入需后续独立开发与验证。

运行方式见 [原型 README](../../web/visual-prototype/README.md)。本地预览服务：`npm run dev -- --host 127.0.0.1 --port 4174 --strictPort`。
