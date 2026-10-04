# 天机场景产品：第一阶段设计交付

审计日期：2026-10-04。main 基线 `a9bc0fd3549e5be44296e1e23161d9fe6da7211c`。本分支交付产品矩阵、可校验注册表、输入输出样例与单页设计板，**未实现 Scenario runtime、场景 API、历史服务或后台写入，也未开放 AI**。

前台按用户问题组织：今日、本周、本月、年度、关系、事业、财运、合盘、一件事、梦境、人生档案。术数名称留在方法说明与“专业排盘”二级入口。11 个入口对应 10 个核心场景；事业与财运共用 `career_wealth`，按 `career/wealth` 视图阅读同一份底层结果。

| 交付 | 文件 | 用途 |
| --- | --- | --- |
| 场景产品矩阵与首批选择 | [PRODUCT_MATRIX.md](PRODUCT_MATRIX.md) | 每个场景能做什么、不能做什么、开放条件 |
| 当前能力、八字缺口 | [CAPABILITY_GAPS.md](CAPABILITY_GAPS.md) | 对照真实 provider、variant、规则、证据和 API |
| Scenario Engine 设计 | [SCENARIO_ENGINE.md](SCENARIO_ENGINE.md) | 调度、聚合、证据绑定、历史、合盘与 AI 边界 |
| 首页与后台信息架构 | [HOME_ADMIN_IA.md](HOME_ADMIN_IA.md) | 场景首页、二级专业工具、Scenario 管理 |
| 10 套输入输出原型 | [PROTOTYPES.md](PROTOTYPES.md) | 阅读顺序、具体字段、结果状态与验收案例 |
| 单页交互设计板 | [prototype.html](prototype.html) | 11 个入口切换、输入结构、报告布局和后台字段；不联网不保存 |
| 注册表 | [registry.json](../../config/scenarios/registry.json) | 每场景的依赖、现有结构规则、证据引用、缺口和开放状态 |
| 机器输入输出原型 | [prototypes.json](../../config/scenarios/prototypes.json) | 10 个固定样例；缺失指标用 null |
| 能力审计快照 | [capability_snapshot.json](../../config/scenarios/capability_snapshot.json) | 7 个底层域、37 条执行规则、28 个 Golden Cases、文件 SHA256 |

**当前直接上线结论：所要求的完整场景报告为 0 个。** 六域已有专业结构计算接口，但没有任何一个场景已完成适配器、聚合规则、用户历史、正式页面与场景验收。最早可工程化开放的是“一事占问·结构参考版”；“人生全盘·基础档案”可做第二个限定结构报告，但不能用“人生全盘”暗示已具备完整人生评断。日历知识和日记可单独做复访基础，不冒充“个人今日运势”。

**首批三个核心产品优先级：一事占问 → 桃花姻缘 → 事业财运。** 前者最快验证报告阅读链，后两者需先补八字和场景依据。此排序是基于输入负担、现有代码可复用程度、场景聚合复杂度的产品判断，尚无用户调研或营收数据支持；不是三项已能公开交付的承诺。

校验：`python scripts/validate_scenarios.py`。它检查真实 engine/variant/rule/证据引用、审计文件哈希、11→10 映射、报告空值、双人结构及禁用 AI。单元测试验证伪造依赖、伪分数、非法开放和污染样例会被拒绝；通过只证明设计资产内部一致，不证明产品已实现或预测准确。

本地验证：五项场景设计测试、知识库与 Phase1 模型校验通过；桌面和 390px 手机各检查 11 个入口，七段报告、标题、只读示例和 AI 关闭状态正确，整页无横向溢出。后台十行配置与三个禁用动作通过检查，没有控制台错误。观测记录见 [ui-verification.json](screenshots/ui-verification.json)，[桌面首页](screenshots/home-desktop.png)、[手机首页](screenshots/home-mobile.png)、[手机占问完整原型](screenshots/question-mobile-full.png)、[后台预览](screenshots/admin-desktop.png)。这些是设计 UI 检查，不是产品运行或模型质量评测。

本地浏览 `python -m http.server 4180 --bind 127.0.0.1 --directory docs/scenarios`，打开 `http://127.0.0.1:4180/prototype.html`；不加载外部资源、不中转任何密钥、不请求场景 API、不保存输入。设计板数据变更后执行 `python scripts/build_scenario_design_board.py`，重新校验并核对相应截图。

PR #87 的网站原型与 PR #88 的后端就绪/模型校准尚属独立工作：本分支没有把它们当作 main 已合并能力。Windows 原生 main 的 runtime manifest 路径会被 guard 拒绝；两份实际结构样例在 PR #88 工作区运行，逐文件核对确定性执行、历法与 operations 代码与本 main 基线完全一致，出处记录在审计快照中。没有改 main 源码以伪造 probe 成功。

《三命通会》仍为 quarantine_only、canonical_ready=false，Canonical 文件不存在。当前模型候选没有完成真实质量评测与人工语义复核；场景重构不产生新资格。
