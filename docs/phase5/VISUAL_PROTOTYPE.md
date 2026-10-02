# Phase 5 第一轮 · 前台与后台视觉验收

基线：远端 main `9433a8b659d288bfa4b769e2d278221f2f1b3cef`。本轮只提交可交互的静态视觉原型，未改动确定性引擎、Prompt、来源等级或知识资产，未调用排盘接口或模型服务。

## 评审范围与路由

| 产品 | 路由 | 本轮内容 |
|---|---|---|
| 用户前台 | `/` | 品牌、简洁山水 Hero、七个工具入口、最近使用、示例推演、能力说明、音乐 |
| 用户前台 | `/liuyao/result` | 一套完整的六爻示例结果结构，支持爻位、规则与相关典籍详情 |
| 管理后台 | `/admin` | 仪表盘、审核队列、发布边界、管理入口与示例审核记录 |
| 管理后台 | `/admin/classics` | 古籍管理示例：搜索、领域/状态筛选、书目与关联章节、详情 |
| 管理后台 | `/admin/rules` | 规则管理示例：执行范围、流派约定、关联 Evidence 与审核状态 |
| 管理后台 | `/admin/evidence` | Evidence 管理示例：必要原文、章节、对应规则、C/D 等级、审核状态 |

其他前台路径只显示未开放页面；其他后台模块标记“规划”，点击说明本轮不实现。八字、奇门、紫微、六壬、周易与风水入口不跳转到复制出的六套页面，也不假称其输入流程已经完成。七个产品入口不代表增加第七个排盘引擎。

## Desktop / Mobile 截图

截图由 Chromium 从代码运行页面直接捕获，不是设计稿渲染或后期合成。桌面 1440 × 1000 视口，保留完整页面；手机首屏 390 × 844。手机长截图的固定底栏位置对应截取时的视口底部，实际滚动时底栏始终贴屏。

| 页面 | Desktop 完整页面 | Mobile 首屏 | Mobile 完整内容 |
|---|---|---|---|
| 用户首页 | [截图](visual-prototype/screenshots/home-desktop.png) | [截图](visual-prototype/screenshots/home-mobile.png) | [长图](visual-prototype/screenshots/home-mobile-full.png) |
| 六爻结果 | [截图](visual-prototype/screenshots/liuyao-result-desktop.png) | [截图](visual-prototype/screenshots/liuyao-result-mobile.png) | [长图](visual-prototype/screenshots/liuyao-result-mobile-full.png) |
| 后台首页 | [截图](visual-prototype/screenshots/admin-dashboard-desktop.png) | [截图](visual-prototype/screenshots/admin-dashboard-mobile.png) | [长图](visual-prototype/screenshots/admin-dashboard-mobile-full.png) |
| 古籍管理 | [截图](visual-prototype/screenshots/admin-classics-desktop.png) | [截图](visual-prototype/screenshots/admin-classics-mobile.png) | [长图](visual-prototype/screenshots/admin-classics-mobile-full.png) |
| 规则管理 | [截图](visual-prototype/screenshots/admin-rules-desktop.png) | [截图](visual-prototype/screenshots/admin-rules-mobile.png) | [长图](visual-prototype/screenshots/admin-rules-mobile-full.png) |
| Evidence 管理 | [截图](visual-prototype/screenshots/admin-evidence-desktop.png) | [截图](visual-prototype/screenshots/admin-evidence-mobile.png) | [长图](visual-prototype/screenshots/admin-evidence-mobile-full.png) |

另附 [手机核心盘面截图](visual-prototype/screenshots/liuyao-chart-mobile.png)，用于检查本变卦逐爻对照、世应与动爻信息的可读性。

## 设计与信息层级

前台使用米白纸色、深青文字与少量金色提示；原创向量山水只出现在首页 Hero，结果区域保持安静清晰。中文衬线用于标题，正文采用系统无衬线字体。没有广告式吉凶标签、运势排行榜、资源数量宣传或知识库入口。

首页直接呈现七个工具入口，六爻示例优先；其余入口明确未开放。手机采用双列工具卡片、单列最近使用与底部首页/历史/收藏导航。收藏只在浏览器本地记录“此视觉示例”的收藏状态；历史是固定示例列表，不伪装成账号历史服务。

六爻结果严格按用户指定顺序组织：

1. 基础信息：时间、干支、装卦口径、示例范围，并标注资料未经过真实排盘。
2. 核心盘面：本卦、变卦、逐爻对照、动爻与世应；移动端保留主要爻位，点选补充六神、六亲、纳甲及旬空资料。
3. 核心结论：只概括样例结构，不增加现实事情的吉凶断语。
4. 规则命中：示例规则与结构关系，详情明确说明不是引擎实际返回的命中。
5. 典籍依据：只保留本例两个相关必要片段，含古籍、章节、等级与对应规则；第三条规则的依据标为待核，不虚构额外引用。
6. AI 解读：次要位置的未开放状态，不生成或模拟 AI 文字。
7. 查看推演过程：原生折叠区，默认收起；仅给出人可读步骤，不展示内部 JSON、错误栈或工程调试资料。

后台使用独立的浅灰/白管理布局、紧凑导航、汇总卡片、筛选区及数据表，没有山水、纹理、音乐或古风大背景。手机导航改为抽屉，表格在自身区域横向滚动，并给出滑动提示，不撑宽整页。等级与审核状态是两个不同字段；示例一律只有 C/D，未创造 A/B 来源。

## 参考关系与原创范围

此前 [Benchmark 草稿 PR #86](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/86) 尚未合并；商业产品中未能公开验证的页面不作为已观察事实。本轮以用户的新边界要求为准，舍弃前台知识库浏览架构。

| 设计点 | 参考对象 / 来源 | 为什么，以及本轮采用范围 |
|---|---|---|
| 工具入口直达示例，避免先读长介绍 | Chinese-Metaphysics-Platform 的模块入口；用户首页要求 | 将选工具作为首页第一任务；只开放一个示例验证层级 |
| 盘面置于解释之前 | mingyu 的盘面/助手分区；用户结果顺序 | 普通用户先读结构，AI 不占首屏主视觉；MingPan 是计算库，不当作网站布局来源 |
| 密集盘面按位置对齐，手机逐爻补充信息 | mingyu 的盘面详情与移动分层；MingPan 的逐爻文本 renderer | 保留排盘的相对位置，手机点选详情；元亨实际页面未验证，不声称复制其布局 |
| 领域入口与公共结果结构分离 | Chinese-Metaphysics-Platform 的工具模块组织 | 后续复用一个结果信息框架，而非复制六套交互；本轮不实现领域适配层 |
| 手机主要任务短路径 | 问真、易百查为 Benchmark 参考对象；用户移动优先要求 | 本轮设计来自用户要求与常见交互模式，未声称其未经验证的手机页面具备某具体行为 |
| 典籍仅作为本次结果的依据 | 本项目 chart / rules / evidence 能力与用户限制 | 不借鉴公开资源浏览器；必要片段与对应规则紧邻 |
| 前台新中式与后台现代管理完全分离 | 用户本轮明确要求 | 色彩、版式、SVG、图标、文案与合成音乐均为本项目创作 |

没有复制参考产品的品牌、图片、代码、文案或 UI 素材；新增 npm 包仅为通用框架与构建/浏览器验证工具。典籍短句属于既有公版文本展示，不是竞争产品文案。

## 组件结构

```text
web/visual-prototype/
├── src/main.tsx                  路由选择；按需加载后台
├── src/shared/
│   ├── router.tsx                页面导航与轻量提示
│   ├── Icon.tsx                  原创 SVG 图标
│   ├── Dialog.tsx                原生弹窗、键盘关闭与焦点恢复
│   └── base.css                  基础样式与减少动画支持
├── src/public/
│   ├── PublicApp.tsx             前台壳、导航、历史/收藏、页脚
│   ├── HomePage.tsx              Hero、七工具入口、最近使用、示例
│   ├── InkLandscape.tsx          原创山水 SVG
│   ├── LiuyaoResultPage.tsx       七段结果、逐爻详情、必要依据
│   ├── MusicPlayer.tsx           显式播放、全局暂停、音量与偏好
│   ├── fixtures.ts               手工静态展示资料；无内部全量资产
│   └── public.css                前台独立视觉与移动布局
├── src/admin/
│   ├── AdminApp.tsx              后台壳、模块导航与规划说明
│   ├── Dashboard.tsx             仪表盘示例
│   ├── AssetPage.tsx             三页共用搜索/筛选/表格/详情
│   ├── fixtures.ts               虚构 DEMO 记录；不读取真实资产
│   └── admin.css                 后台独立专业管理样式
├── public/music/quiet-waters.ogg  原创合成音乐
├── scripts/                      原创音乐生成、浏览器截图
└── tests/                        页面、边界、交互、移动与音乐验证
```

后台导航已规划仪表盘、古籍、章节、术语、规则、Evidence、来源、RAW/Quarantine/Canonical、流派冲突、算法/Variant、AI Provider/Model、Prompt、Eval/Golden Cases、失败案例、用户/权限、API/系统日志。只有本轮指定的四个后台路由实现示例，其他模块不提供操作能力。

## 前后台边界与接入约束

| 内容 | 前台 | 后台 |
|---|---|---|
| 七类工具、历史、收藏、AI | 允许，当前只有明确标注的六爻样例 | 不占管理主导航 |
| 当前结果命中的规则与必要 Evidence | 允许，不能由详情跳到全量列表 | 可管理其来源与关联 |
| 完整古籍/章节/术语/规则/Evidence 库 | 无入口、搜索或浏览路由 | 仅后台规划和样例 |
| RAW、Quarantine、来源、Prompt、内部算法与图谱 | 不提供浏览 | 后台规划；本轮不接真实资产 |
| Trace | 结果底部默认折叠，人可读过程 | 算法/日志规划另行设计 |

**当前是视觉和路由分离，不是上线安全边界。** `/admin` 尚无认证或服务端权限验证，所有展示记录为虚构 DEMO 数据；不可将真实内部数据导入这个静态站再依赖隐藏导航保护。正式后台必须先建立服务端认证、角色授权及独立资产接口。前台真实接口只返回当前执行允许公开的命中内容，不能下载或直连内部资产索引。

原型没有 `fetch`、API 封装、Mock 服务或 provider；静态资料并未模拟 `/api/v1/execute` 响应。待用户确认后，另开小 PR 直接消费真实接口，按真实 chart / rule_matches / trace / evidence 等字段展示，移除展示 fixtures。前台“未开放”是当前设计阶段状态，不代表后台引擎不能执行。A/B/C/D 来源质量、真实模型校准结果没有因视觉原型而变化。

音乐默认关闭，点击播放才加载并启动本地音频；公开页面间导航保持播放与音量。页面右上角可以随时暂停；进入后台时停止。音量与“曾主动选择播放”的偏好保存在本地，但刷新不自动发声。没有外链音乐、API Key 或模型配置。

## 验证与评审节点

已执行构建/类型检查，以及 26 项 Playwright 浏览器检查：六个路由 × 1440/390/360 三种宽度、整页不溢出、无外部/API 请求、前台未开放路径、结果顺序/折叠/详情/焦点恢复、收藏与历史标识、音乐显式播放/全局暂停/偏好/后台停止、三个管理页筛选/空状态/详情与规划导航。

GitHub PR 同时运行原有知识库校验和新增视觉原型构建/浏览器 CI。截图文件是此原型的交付物，不是正在运行的正式网站。

本轮结束于设计确认：评审首页视觉、六爻盘面密度、手机布局、后台表格与前后台边界。确认后才能继续真实接口联调；本轮不部署、合并上线、接 AI 或补全其他领域页面。
