# 天机平台｜开发总目录（先看这里）

> **目标：按最初确认的古风设计，把 11 个生活场景真正做出来。** 2026-10-11。  
> 本目录是项目实施导航；文档规划完成不代表功能已开发或上线。

## 阅读顺序

| 顺序 | 文件 | 解决什么问题 |
| --- | --- | --- |
| 1 | [产品总纲](PRODUCT_MASTER_PLAN_V1.md) | 明确用户、11 个生活入口/7 专业入口、真实能力与业务红线 |
| **2** | **[最初设计基线与截图](ORIGINAL_DESIGN_BASELINE_V1.md)** | **固定 PR #87 古风原型 + PR #89 场景架构，禁止另起炉灶换风格** |
| **3** | **[逐页功能/视觉规格](PAGE_SPECIFICATIONS_V1.md)** | **首页、11 个生活入口、历史/收藏、7 专业和 18 个后台模块分别怎么做/怎么验收** |
| 4 | [阶段总计划 M0–M7](IMPLEMENTATION_PLAN_V1.md) | 30 项父任务、依赖和顺序 |
| **5** | **[详细 WBS 交付计划](DETAILED_DELIVERY_BACKLOG_V1.md)** | **30 项父任务拆为独立 PR 工作包，逐项列出功能/来源/反例/截图/CI** |
| 6 | [真实执行台账](EXECUTION_LEDGER.md) | 本批处在哪、哪条 GitHub PR/CI 通过、是否合并、下一项做什么 |

## 两条不可违反的原则

**一、页面必须忠实于最初视觉**：原 PR #87 的宣纸纸色/深青/铜金/宋体/山水/七域图/音乐/后台工作台不删、不重做；原 PR #89 确定的生活场景优先和报告信息层级不漂移。每次 UI PR 至少附原版截图链接、新版桌面/手机截图及差异解释，用户体验改变需要明确批准和真实浏览器验收。

**二、功能必须真实且有据**：用户输入必须调用真实 API，经过 Source/Rule/Evidence/Variant/Golden 边界；无审定古籍不得生成解释，AI 需真实校准才开放。进度只以真实 PR、Actions、可复验结果/部署记录记账。

## 接下来从哪里开工

- `TJ-002`：核对并收尾私有 PR #50 的最终组合回归、合并记录。
- `TJ-004.1~004.4`：逐一验证 11 个入口的 API、异常、证据以及对最初设计的**当前视觉差异**。
- `TJ-008.1~008.5`：由原版截图驱动还原首页/结果页/移动端；只在 TJ-004 发现真实缺口之后小批修复。
- 其他核心知识与上线任务依照 [WBS](DETAILED_DELIVERY_BACKLOG_V1.md) 的依赖开展，不凭一时兴趣插队。

## 设计与业务定位速查

- **原设计视觉与截图**：[PR #87](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/87)
- **原场景首页和后台 IA**：[PR #89](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/89)
- **第一版真实生活场景实现**：[PR #90](https://github.com/HelloMrDuan/tianji-knowledge-base/pull/90)
- **当前公开源代码**：[tianji-knowledge-base](https://github.com/HelloMrDuan/tianji-knowledge-base)
- **私有原典与审核**：仅在受控私有仓库，**不要把原始文件或 manifest 添加到公开计划文档**。

本目录和详情文档都应在 PR 中与代码同步维护。新增需求先进入执行台账并通过设计差异审查，不能靠口头说“以后再补”。
