<!-- 天机项目统一 PR 模板；按原产品总纲与最初设计，不能为了合并而虚构状态。 -->
## 任务与范围
- [ ] 关联 TJ-xxx.y / UI-xx：<!-- 真实编号；紧急安全修复注明原因 -->
- 用户可以观察到的具体变化：
- 这次明确不解决的内容：
- 依据：[总纲](../docs/product/PRODUCT_MASTER_PLAN_V1.md) / [细化 WBS](../docs/product/DETAILED_DELIVERY_BACKLOG_V1.md) / [台账](../docs/product/EXECUTION_LEDGER.md)

## 保留最初设计（仅前端变动时必填）
- [ ] 已读取[原设计视觉契约](../docs/product/ORIGINAL_DESIGN_BASELINE_V1.md)与[逐页规格](../docs/product/PAGE_SPECIFICATIONS_V1.md)
- 原始 #87 桌面截图与手机截图固定链接：
- #89 场景 IA 与首页对照：
- 当前修改前截图（对应 commit/视口）：
- 本 PR 修改后截图（1440×1000、390×844、360px；附真实 Actions/附件）：
- 本次必要设计差异、原因和验证结论：
- [ ] 保留纸色/深青/铜金/宋体/水墨、生活场景优先、七专业次级、音乐与后台独立外观
- [ ] 不以 DEMO 盘面、假历史或随机分数伪装真实用户结果

## 真功能、知识与安全
- 真实 API / Scenario / 版本及输入输出：
- 原典 Source/Review/Rule/Evidence/Variant/Golden（不涉及请写“不涉及”）：
- 不确定/冲突/弃判/研究限定/AI 发布范围：
- 隐私数据/私有知识/静态包/API 响应/日志泄漏检查：
- [ ] 不会把私有 RAW、Quarantine、长篇原文、token/密钥或私有清单提交到公开仓库

## 验收（所有结果必须以真实运行凭证填写）
- 正例 / 实际结果：
- 负例 / 弃判：
- 边界：节气/闰年/年份/长文本/手机/权限：
- 前端真实 Playwright/截图差异结论（仅后端修改可注明不适用）：
- 公开 head SHA、code/frontend-build/gate-public-data：
- 私有固定公开 head SHA、完整 Canonical/真实后端/浏览器（若涉及）：
- 合并后两个 main SHA 和组合回归：
- 真实部署地址/回滚测试；**没有就写“未部署”**：

## 台账回填
- 任务状态：待验 / CI 通过 / 已合并 / 已部署验收 / 阻塞
- 本 PR 引入的新缺口/后续第一个应做的任务：
- [ ] 将 PR URL、SHA、CI 结果和原设计差异回填 [执行台账](../docs/product/EXECUTION_LEDGER.md)，不能仅在聊天里宣称完成
