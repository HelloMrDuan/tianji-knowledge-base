# 第 162 批：解梦知识研究真实后台闭环

**目的**：在不对公网发布不成熟解梦测算的前提下，让已有十条审核场景、实际索引和证据可以被后台人员真正检索，而不是继续只写文档和 CLI。

## 实际接口

`POST /api/v1/admin/research/dream`，必须配置环境变量 `TIANJI_ADMIN_READ_TOKEN`，传 `Authorization: Bearer <token>`。请求体仅接受 `{"dream_text":"我梦见被蛇咬了"}`，字符串 2–500 字，额外字段全部拒绝。缺少后台令牌配置返回 503，未授权返回 401，无效字段返回 422。权限检查在正式检索前执行；不接受其他模式参数，不储存请求文本，也不调模型。

返回 `read_only=true`、`research_only=true`、`public_release=false`，内含原有 `dream_knowledge.retrieve` **直接来自实际 reviewed Canonical 和 RAG 的结果**：单项具体场景、审核短引、来源引用、输入片段、弃判理由。仅在有匹配的已审核条目时显示解释候选，没有匹配则 `no_reviewed_interpretation`；预测能力和 `ai_enabled/public_enabled` 必须一直为 false。

## 实际 UI

后台 `/admin/dream-research` 中可输入临时访问令牌、梦境叙述，提交到真实服务端。返回匹配的文化短解释、原文短引和证据级别；不会在网页存储令牌，不会自动提交/检索，也不向公共首页添加梦境入口。注意：静态后台页面本身不是权限边界，真正保护来自服务端 Bearer Token；未配置令牌时绝不能展示研究结果。

## 验收

`tests/test_private_dream_api.py` 使用真实 TestClient、实际 Canonical/RAG，对“蛇咬人”场景正例和考试、否定、影视转述负例、禁用权限、超长输入作验证；`web/visual-prototype/tests/admin-dream-research.spec.ts` 验证页面无自动请求、错误令牌无法获得内容、令牌不持久化。所有运行时测试仍必须通过生产构建的真实清单；不使用 Mock/假古籍证据。

## 尚未开放的能力

公开的个性化解梦和 AI 解读、完整自然语言理解与组合梦义仍未具备，不能把单一电子本中的传统象征当成真实未来预测。源文本的权利与独立性、后端部署秘钥配置、知识资产从 public 仓库迁往私有仓库仍有单独缺口。
