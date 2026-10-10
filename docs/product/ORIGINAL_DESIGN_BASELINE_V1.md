# 天机平台｜最初设计还原与视觉契约 V1.0

> **不可擅自重做风格** · 2026-10-11  
> 配套：[产品总纲](PRODUCT_MASTER_PLAN_V1.md)｜[逐页详细规格](PAGE_SPECIFICATIONS_V1.md)｜[分批实施与验收](DETAILED_DELIVERY_BACKLOG_V1.md)｜[执行台账](EXECUTION_LEDGER.md)  
> 此文件把**最初已经存在的设计证据**固定为后续对照基准，不是新画的一套“看着差不多”的方案。

## 一、视觉原始依据：优先级必须固定

| 层级 | 原始资料 / 已有证据 | 约束作用 |
| --- | --- | --- |
| **A. 最初页面视觉** | [原始 PR #87：Phase 5 整站前后台原型](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/87)、[原版页面/截图总索引（固定提交）](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/VISUAL_PROTOTYPE.md) | **视觉最高优先**：纸色、深青、铜金、书卷排版、水墨结构图、桌面/手机布局、前后台分离、音乐。该 PR 当时为草稿，不能写成“已部署生产”。 |
| **B. 最初产品场景重定位** | [PR #89：Scenario 信息架构](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/89)、[首页和后台 IA 固定版本](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/HOME_ADMIN_IA.md)、[当时 HTML 设计板](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/prototype.html) | **交互/阅读顺序最高优先**：普通用户的生活问题优先，11 个入口完整保留，专业工具不抢首页；报告先读结论范围再看细节。#89 是设计参考，不能冒充其当时已有完整引擎。 |
| **C. 首批真实网页实现** | [PR #90：scenario-first 网站 MVP](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/90)、当前 `web/visual-prototype/src/public` 与 `src/admin` | 技术兼容基准：React/Vite、全局水墨、音乐、Scenario/API；保留现有有效代码，不因还原 UI 删除真实功能。 |
| **D. 已审核业务边界** | [Scenario Runtime](../scenarios/RUNTIME.md)、[知识缺口](KNOWLEDGE_GAPS.md)、[质量状态](../phase4/QUALITY_STATUS.md) | 任何 UI 设计都不能把 `production_limited` 修饰成完整吉凶、真实 AI、专业结论或私有知识公开权限。 |

**冲突裁定**：
1. 样式/风格/组件形态冲突：**以 #87 的可见视觉效果为准**，局部可为真实数据密度适配，必须附前后对照与差异解释。
2. 首页是“七域术数入口”还是“11 项生活场景”的冲突：**以 #89 的产品重定位为准**，但**使用 #87 的古风设计语言**呈现 #89 的用户内容；七域仍保留到第二层。
3. 静态示例与新真实结果冲突：真实 API/隐私/知识禁区优先，保留视觉骨架而替换假数据。无数据是空状态，不编报告或占位分数。
4. 视觉参考与后续已合并真实修复冲突：不得为“像原图”回退计算、证据、隐私、音乐交互或已通过的真实测试。
5. 任何设计上需要偏离 A/B 的改动，必须在 PR 附**设计差异表 + 原始截图 + 新截图 + 原因 + 功能证据**；未经接受不得称“忠实还原”。

## 二、固定原始截图清单（可点开对照）

原版 PR #87 的固定代码版本为 `8412304daefe74e1984953a6b85ebd912cfba614`。原文档声称约 73 张真实浏览器截图，**这里的链接仅表明原设计参考位置；不是今天重新截图或已逐张视觉验收**。

| 参考用途 | 原始桌面截图 | 原始手机截图 |
| --- | --- | --- |
| 全站首页 / header / 山水 / 音乐 | [home-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/home-desktop.png) | [home-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/home-mobile.png) · [长图](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/home-mobile-full.png) |
| 八字资料页 | [bazi-home-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/bazi-home-desktop.png) | [bazi-home-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/bazi-home-mobile.png) |
| 六爻报告/盘面 | [liuyao-result-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/liuyao-result-desktop.png) | [liuyao-result-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/liuyao-result-mobile.png) · [完整盘面](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/liuyao-chart-mobile.png) |
| 管理后台仪表盘 | [admin-dashboard-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-dashboard-desktop.png) | [admin-dashboard-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-dashboard-mobile.png) |
| 古籍与规则治理 | [admin-classics-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-classics-desktop.png) · [admin-rules-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-rules-desktop.png) | [admin-classics-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-classics-mobile.png) |
| 冲突与来源审计 | [admin-conflicts-desktop](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-conflicts-desktop.png) | [admin-conflicts-mobile](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/admin-conflicts-mobile.png) |
| 场景优先重定位图 | [PR89 首页桌面](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/screenshots/home-desktop.png) | [PR89 首页手机](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/screenshots/home-mobile.png) |
| 场景后台结构 | [PR89 后台桌面](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/screenshots/admin-desktop.png) | [PR89 后台手机](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/screenshots/admin-mobile.png) |

其他七域 / 16 后台全套原始截图以 [PR87 文档目录](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/VISUAL_PROTOTYPE.md) 为准。**固定 commit 不受未来文件名改动影响；如引用不可访问，先恢复/归档原有参考，再认定视觉验收，不可自行臆画替代。** 本轮不声称原图已复制入当前 `main`。

## 三、冻结的视觉设计语言（不是让开发者自行选新主题）

以下 token 是 **#87 原 `public.css`、#89 原 `prototype.html` 已使用的值**；同色系容许微调，新的视觉实现必须说明差异，不能随意变成赛博、纯白 Dashboard、通用 SaaS 或炫彩测算页。

| 部位 | 已有设计基线 | 具体约束 |
| --- | --- | --- |
| 画布 | #87 `--paper: #f7f4ec`；#89 `--color-surface: #f6f3eb` / `--color-paper: #fffef9` | 宣纸/米白背景、低对比纸纹；真实报告在浅色纸卡上清晰阅读 |
| 主文字 | #87 `--ink: #173f36`；#89 `--color-text: #233c37` | 深青墨色，正文不得淡到看不清 |
| 次文字 | #87 `--ink-soft: #435d50`；#89 `--color-muted: #5d6f66` | 层级清晰，辅助提示移动端可读 |
| 金铜点缀 | #87 `--gold: #8c6831`；#89 `--color-accent: #a36340` | 铜色印记、小标签、细线、局部强调，不是大面积亮金 |
| 分割线 | #87 `--hair: #dddcd1`；#89 `--color-border: #d8dbcf` | 细边框、留白，不能堆十几种彩色重阴影卡 |
| 标题 | `Noto Serif CJK SC / Songti SC / SimSun` | 中文宋体/衬线书卷感；多级标题节制，不全站同一个无衬线粗体 |
| 正文 | `Noto Sans CJK SC / PingFang SC / Microsoft YaHei` | 简洁易读，正文行高约 1.7～2.0；小字必须符合可读性 |
| 按钮 | 深青主要按钮 + 描边辅助按钮；#87 原型最小高 44px | 真实可点击、触屏可用，禁用态/加载态不抢色 |
| 插画 | 已有 `InkLandscape.tsx` 原创山水 SVG；七域四柱/六爻/九宫/十二宫/四课三传/八卦/罗盘 | **保留原件与样式**；固定示意必须标示“非当前计算盘面”；不采购未授权古籍图片 |
| 视觉节奏 | 编辑式杂志排版：题签、标题、留白、分割线、报告/证据卡 | 统一但不单调，优先内容阅读与古风氛围 |
| 动效 | 山水/云雾/水墨缓动需自然、低资源；现有静态 SVG 可作基础 | `prefers-reduced-motion` 停止动画、不得盖住输入与正文；不是加载假视频或无限重绘 |
| 背景音乐 | `/music/quiet-waters.ogg`、`MusicPlayer.tsx` | **保持全局、可主动播放/暂停/音量、路由切换持续；后台不播；尊重浏览器自动播放限制**，无声时也能使用网站 |

### 现代产品化不能改变的边界

- **前台**是“米白纸色 + 山水 + 深青 + 铜色印记 + 中文衬线标题”的古风；**后台**是独立浅灰/白工作台和侧边导航，**不复制山水背景和背景音乐**。
- 旧截图中的 DEMO、固定盘面和模拟记录只能作为 **布局参考**，实际页面不得将其展示成“已计算/真实审核数据”。
- **完整古籍/RAW/Quarantine/全部 Evidence/原始 Trace 只能在受保护后台或服务端**；前台仅显示当前结果获审的短引和来源说明。
- 保持原有设计中首页、七域、历史/收藏、33 主页面路线的视觉传承。现行 11 生活产品是产品层补充，不得以替换首页把七域专业页删掉。

## 四、首页的确定阅读顺序（#89 的信息架构 + #87 的古风视觉）

1. **全站 Header**：天机印记/品牌；桌面导航“首页／生活场景／我的记录／专业排盘”，右侧古风音乐。手机底部“首页／场景／记录／我的”，专业能力放第二层；原 `/history`、`/favorites` 地址继续可达。
2. **古风水墨 Hero**：“今天，你最想看哪一件事？”或当前经确认的等义主标题；景物不盖文案。主要 CTA 优先 **一事占问**（#89 的首屏用户意图），次级 **桃花姻缘**、**事业财运**；**人生总览**可保留可见入口，但不应无设计评审就从 #89 最初 CTA 随意改成唯一主入口。首次用户明确看到“能算什么/暂不能算什么”。
3. **时间快捷入口**：今日／本周／本月／年份自选；同一有效出生资料，确无资料则引导输入；不生成随机分数、伪趋势或虚假的历史报告。
4. **11 个生活场景**：所有入口保留；事业/财运**两张入口可有不同文案，必须对应一个底层核心 Scenario 和两个可读视图**；状态显示“真实结构 / 部分参考 / 研究中”，不能把 `available` 直接翻译成“完整算命”。
5. **继续查看/我的记录**：仅在确有用户存储记录时展示真实历史；未实现账号时清楚写“本机资料/示例”。不使用伪造的复访历史。
6. **可信度说明**：确定性计算 → 审核 Rule → 原典短引 → 适用与限制，别把单一 C 级电子文本说成独立交叉验证。
7. **专业排盘**：八字、六爻、奇门、紫微、六壬、周易、风水七域作为次要入口；保留原有结构图与阅读顺序。
8. **页脚及隐私声明**：文化研究、AI 未发布、无依据则弃判、个人资料本地储存及删除入口。

## 五、核心页面结构合同（所有生活场景同源）

```text
全站 Header + 古风音乐
 └─ 面包屑 + 题签 + 主标题 + “现在能回答什么 / 还不能回答什么”
    ├─ A. 输入区域：只索取本场景必要资料 + 合法性/隐私说明
    ├─ B. 明确用户操作：生成 / 返回修改 / 清空；Loading / Error / Retry
    ├─ C. 顶部简明摘要：本次真实事实、目标日期/年份、解释范围
    ├─ D. 核心结论卡：只引用已审事实和证据，有缺口则显示不可判断
    ├─ E. 关键盘面 / 关系 / 时间窗口：实时计算、不填演示盘
    ├─ F. 依据和出处：可展开的短引 / 来源 / Variant / 限制
    ├─ G. 不确定性：流派、原文异文、缺时辰、研究/AI 禁用
    └─ H. 下一个自然场景：返回、收藏或去年度/桃花/总览
Footer + 手机底部导航（后台没有音乐）
```

**不可随意改变**：先读懂结果、再按需展开 Trace；不要把完整 JSON、Rule ID、专业盘面或古籍全文塞到主视觉。正常空态、无匹配、服务失败、无权访问、加载未完成都必须有独立状态设计，不能从“计算中”直接跳静态结果。

## 六、后台原始视觉与信息架构

#87 原型的**左侧导航（约 240px）、顶栏（约 75px）、浅灰底 + 白色内容卡、表格/筛选/详情/审核轨迹、移动抽屉**为视觉参考；真实实现必须增补 **Scenario 管理**、权限与审计，而不是重新做成古籍公开阅读站。

后台范围：
- 工作台 / 审核队列、Source / Classics / Chapters / Terms；
- RAW / Quarantine / Canonical 的证据审批；Rules / Evidence / Variants / 冲突并列；
- Scenario / 模板 / 公共发布范围；
- AI Provider / Prompt / Eval / 失败案例；
- 用户权限 / 安全审计 / API 日志 / 来源更新；
- 传统解梦校勘后台与前台梦象查阅严格分隔。

没有经过后端实际鉴权、最小权限和日志审计的后台**只可用虚构样例/禁写状态**；旧视觉上的按钮不可直接写入私有 Canonical。#87 原本 16 页，不等于现在已实装 16 个真实管理 API。

## 七、逐页截图、交互与审美验收门禁

### 测试视口
- **1440 × 1000** 原桌面参照；**390 × 844** 原手机参照；**360px** 为拥挤兼容验收；另做 **768px** 平板和更长文本/缩放 200% 检查。
- 每个 `UI-xx` 页面至少提交：**原设计截图链接（#87 或 #89） + 当前修改前截图 + 新截图（桌面/手机） + 差异说明**，并将新 screenshot 或 CI artifact 与 PR head SHA 关联。
- 参考图含模拟数据时，仅对**布局、颜色、间距、组件排布和古风氛围**做同口径比较；动态数据按真实接口断言，不因内容不同强行做严格像素相等。

### 可验收条件
1. 头部品牌、纸色、深青、铜金、宋体标题、山水插画、音乐入口、主 CTA 层级和专业区第二层均符合上面的固定依据。
2. 桌面 1440、手机 390/360 **无横向溢出、表单截断、关键操作被悬浮导航遮住、证据文字不换行、首屏挤爆**；键盘与触屏均可完成。
3. 真正从首页进入场景、输入、真实 API、结果、展开出处、切换场景，截图中不得出现伪造数字、随机好运进度条或未加载的示例盘。
4. 正常/加载/空结果/无证据/拒判/网络错误/历史无记录/权限失败均有清晰中文反馈，且“重试”不会重复提交副作用。
5. 音频默认不自动响：手动播放、音量滑动、全局暂停、跨前台路由保持、进后台即停，浏览器禁音/降低动态效果可使用。
6. 后台敏感原文只能在受保护 API 和有权限会话展示，公共构建不包含秘密、私有清单及受保护原文。
7. Playwright 实际浏览器 + 前端类型检查/构建 + `gate-public-data` + 必要的私有真实 API/Canonical 全量验收；**只看截图而没有行为测试，不得标为完成。**

### 需要先做的设计差异审查
- 目前 `HomePage.tsx` 首屏 CTA 为“生成我的人生总览”，而 #89 设计首屏主行动是“一事占问”；**需在 UI-HOME 阶段按这里的优先级做差异验收**，不是暗自套用当前页面。
- 目前前台 11 张卡可点，#89 设计允许事业/财运两张卡共享一个核心报告；对比 `scenarioProducts.ts` 是否只用一个入口、是否需要单独视图和路由。
- 目前手机底部主要是“首页／占问／历史／收藏”，而 #89 原场景导航是“首页／场景／记录／我的”；**不得把原有收藏功能删掉，须给出路由映射再调整**。
- 原型 #87 的“专业资料首页”和“结果示例”有多处仍只展示 DEMO、固定结构图；真实计算接入时**沿用设计壳而删除误导性运行态**。
- 后台部分菜单沿用 #87 演示配置，需做**原版菜单 → 真实 API/角色权限**的逐页对照，不得用视觉测试代替后端鉴权。

**这些是明确的待办偏差，并不说明本轮已修改或已复原页面。** 逐项落实请看 [逐页详细规格](PAGE_SPECIFICATIONS_V1.md) 与 [细化交付计划](DETAILED_DELIVERY_BACKLOG_V1.md)。
