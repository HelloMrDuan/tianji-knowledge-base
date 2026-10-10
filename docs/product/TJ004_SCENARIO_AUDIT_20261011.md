# TJ-004.1 / TJ-004.4｜11 场景真实链路与原始首页差异审计

> 2026-10-11 首轮 · **基于代码与已有测试的静态盘点**，不是新增 11 条完整浏览器测试已通过的声明。  
> 验收入口：[产品总纲](PRODUCT_MASTER_PLAN_V1.md)｜[原设计基准](ORIGINAL_DESIGN_BASELINE_V1.md)｜[逐页规格](PAGE_SPECIFICATIONS_V1.md)｜[执行台账](EXECUTION_LEDGER.md)  
> 核验版本：公开 `main@af1909dd350b9ad4a91ae7a817e77274a4644740`、私有 `main@e0f95051a65dcdb5337853405a4e18a798eeb19d`。

## 一、入口→真实计算合同初审

| UI ID | 生活入口 | 当前实际前台路由 | 后端调用分类 | 源码/既有浏览器用例 | 本次静态审计判断 |
| --- | --- | --- | --- | --- | --- |
| UI-02 | 八字基础 | `/bazi-profile` | `POST /api/v1/public/execute`, `bazi` | `BaziProfilePage.tsx` / `birth-profile-reuse.spec.ts` | 有真实基础盘；通用旺衰/喜用未完成 |
| UI-03 | 今日 | `/daily-structure` | `POST /api/v1/scenarios/public`, `daily` | `DailyStructurePage.tsx` / `period-branch-evidence.spec.ts` | 有真实日结构与证据边界 |
| UI-04 | 本周 | `/weekly-structure` | 同接口 `weekly` | `PeriodStructurePage.tsx` / 同上 | 有实际 7 日结构；不是吉凶 |
| UI-05 | 本月 | `/monthly-structure` | 同接口 `monthly` | `PeriodStructurePage.tsx` / 同上 | 公历自然月，非节气流月 |
| UI-06 | 流年 | `/yearly-structure` | 同接口 `yearly` | `YearlyStructurePage.tsx` / `flow-year-label-consistency.spec.ts` | 年份可选且真实重算 |
| UI-07 | 桃花姻缘 | `/romance-structure` | 同接口 `romance` | `RomanceStructurePage.tsx` / `selectable-flow-year.spec.ts` | 有咸池等结构，不是婚期 |
| UI-08 | 事业财运 | `/career-wealth-structure` | 同接口 `career` | `CareerWealthStructurePage.tsx` / `career-annual-reading.spec.ts` | 一个事业财运结构接口，尚未拆出两个显示视图 |
| UI-09 | 缘分合盘 | `/compatibility-structure` | 同接口 `compatibility` | `CompatibilityStructurePage.tsx` / `compatibility-result-consistency.spec.ts` | 双人结构及反例，无适配分 |
| UI-10 | 一事占问 | `/ask` | `POST /api/v1/public/execute`, `liuyao` | `QuestionPage.tsx` / `guided-coin-casting.spec.ts` | 有真实起卦/动变；未审事件断语不输出 |
| UI-11 | 梦象文化 | `/dream-culture` | `POST /api/v1/dream/culture` | `DreamCulturePage.tsx` / `dream-reviewed-explorer.spec.ts` | 10 个已审具体场景；不是通用 AI 解梦 |
| UI-12 | 人生总览 | `/life-overview` | `POST /api/v1/scenarios/public`, `life` | `LifeOverviewPage.tsx` / `life-strength-integration.spec.ts` | 聚合四个受限计算场景，非综合人生结论 |

**审核规则**：表中“有真实调用”来自代码审计和既有用例路径；本轮必须在**固定新 public head、真实 assembled private API** 重跑才升级为本批已验证。证据不足保留 research/limited，不把“场景卡可点击”当完整产品上线。

## 二、发现的最初设计偏差及本批修复目标

| 对照项 | 原版要求 | 当前 `main@af1909d` | 处理策略 |
| --- | --- | --- | --- |
| 首页第一 CTA | [PR #89](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/f2a5b2b1077419711982597cfb0e0bb945e7e12f/docs/scenarios/HOME_ADMIN_IA.md) 的“一事占问”优先，桃花/事业辅助 | 主按钮为“生成我的人生总览” | **本批**调回“一事占问”主 CTA，桃花/事业辅助，人生总览保留在聚合推荐区 |
| 时间快速入口 | 今日 / 本周 / 本月 / 年份 | 首页只有卡片，没有独立时间带 | **本批**按原米白/深青/细分割线风格恢复 4 个链接；全年目标年在后续页面自选，绝不锁死 2026 |
| 原古风 | [PR #87 原图](https://github.com/HelloMrDuan/tianji-knowledge-base/blob/8412304daefe74e1984953a6b85ebd912cfba614/docs/phase5/visual-prototype/screenshots/home-desktop.png) 纸色、深青、山水、书卷与音乐 | 这些资产/结构仍在当前 React 源码 | **保留所有原艺术与 tokens**，只在原布局内添加快捷条，不换视觉主题 |
| 场景目录 | 11 个生活入口 | 当前 11 张卡均有真实有限功能页面 | 保留全部 11，不删/不造评分 |
| 专业目录 | 7 个二级专业领域 | 当前 `domainPages.ts` 7 个，排在生活场景后 | 本批不改七域专业页、不伪造专业算法 |
| 手机底部导航 | #89：首页／场景／记录／我的 | 当前：首页／占问／历史／收藏 | 归 `TJ-008.4` 单独做路由迁移设计与前后图比对；**本批不随意删除功能** |
| 事业/财运入口 | #89：两张卡、一个核心计算 | 当前一张“事业财运”综合卡 | 归 `TJ-023.2` 单独按真实一个 Scenario 双视图实现，不拆双引擎 |

## 三、本批 UI-00 最低自动化门禁

- **静态路由和交互**：点击首页第一 CTA 必须到 `/ask`；桃花/事业两个辅助入口真实可导航；四个时间链接分别到日/周/月/流年；11 生活 + 7 专业保留；人生总览仍在推荐区。
- **视觉**：1440×1000、390×844、360×844 三种视口由真实 Chromium 捕获 `test-results/tj008-home-*.png`，断言无根级横向溢出；原始 #87/#89 设计截图固定链接已写[视觉基线](ORIGINAL_DESIGN_BASELINE_V1.md)。
- **交互/隐私**：首页导航不直接进行生日 API 请求、不会自动保存出生资料；未改真实 Scenario Engine，不改变任何审核来源。
- **公开**：code/frontend-build/gate-public-data 三项全部成功；**私有**：固定本批公开 PR head 全量 Canonical 加 `original-design-home.spec.ts` 真实浏览器；图片 artifact 要附带对应 SHA。
- **不能声称的部分**：没有对原版全部 73 张图片逐像素比对；未覆盖的 11 场景 E2E 与所有异常拒判继续列 `TJ-004.2/.3`，不得把本批 homepage CI 绿当 11 产品全面通过。

## 四、后续真实测试任务（明确排队）

1. `TJ-004.2`：在受控 API 按上表对 11 场景逐一执行样本提交，核对响应目标日期、盘面事实、可见证据、页面 empty 状态，覆盖率必须是 11/11 的实测结果；有失败修复且保留失败日志。
2. `TJ-004.3`：分别加入非法日期、跨节气、无 Evidence、断网、服务超时、先后两请求乱序、合盘双方数据互换、梦境否定/转述/他人主体等用例；只有真正 pass 才更新状态。
3. `TJ-004.4`：从当前实际运行 Vite 页面生成所有主要路由的 1440/390/360 截图，对照原 #87/#89 的位置与版式；原图与现图并排审查，差异逐项创建 `TJ-008.x` 修复 PR。**没有实测截图时一律留“视觉待验”**。

本次 PR 若未合并，以上状态仍按“待验”记录。无真实生产部署验证，不能写“用户已可在线访问”。
