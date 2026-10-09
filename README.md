# 天机传统文化知识库（Tianji Knowledge Base）

面向 AI / RAG / Agent 的中国传统文化与术数知识底座。

目标不是收集几个 prompt，而是建立一套 **可持续更新、可追溯、可审计、可按流派隔离** 的统一知识层，为后续八字、周易、八卦、六爻、梅花易数、紫微斗数、奇门遁甲、大六壬、太乙、风水、姻缘、择日、塔罗等平台能力提供依据。

## 核心原则

- **确定性计算优先**：历法、干支、起卦、排盘等能算的，不让大模型猜。
- **来源优先**：每条知识保存来源、许可证、commit、流派和可信等级。
- **三层隔离**：RAW → QUARANTINE → CANONICAL。
- **不同流派并存**：规则冲突不互相覆盖，以 school/ruleset 区分。
- **AI 只负责解释**：平台先计算、再检索知识库、最后由 LLM 组织语言。
- **知识空缺必须补库**：沿用现有来源/隔离/审核/规则/证据/Golden 流程，不用模型先验填补。产品覆盖见 [KNOWLEDGE_GAPS.md](docs/product/KNOWLEDGE_GAPS.md)，运行 `python scripts/build_product_coverage.py --check` 检查机器报告。
- **持续增长**：已登记仓库定时检查最新 commit；GitHub 全网持续发现候选源。
- **版权隔离**：无 LICENSE、NC、AGPL 混合项目不会自动进入商业正式知识库。

## 首版已包含

- 五行、十天干、十二地支、八卦、六十四卦结构。
- 六爻八纯卦纳甲基础表。
- 首批高价值 GitHub 来源注册表。
- GitHub 全网关键词发现脚本。
- 已登记来源 SHA / License 增量同步脚本。
- Canonical 数据校验与索引构建。
- GitHub Actions 定时发现与同步。

## 平台推荐调用链

```text
用户问题
  ↓
确定性历法/排盘/起卦引擎
  ↓
结构化盘面结果
  ↓
按 domain + school + topic 检索知识库
  ↓
经典原文 / 规则 / 表格 / 案例 + 出处
  ↓
LLM 只负责解释与组织
```

知识库没有足够依据时，应明确返回“依据不足”，而不是自由补全。

## 使用

```bash
export PYTHONPATH=src
python scripts/validate_kb.py
python scripts/build_index.py
python scripts/discover_sources.py --limit 30
python scripts/sync_sources.py
```

设置 `GITHUB_TOKEN` 可提高 GitHub API 限额。

## 许可证

本仓库自身代码采用 Apache-2.0。第三方资料不自动继承本仓库许可证，详见 `docs/LICENSING.md` 与 `THIRD_PARTY_NOTICES.md`。

## Phase 3 统一后端

```bash
python -m pip install -e '.[validation,calendar,api]'
PYTHONPATH=src python scripts/build_production_runtime.py
PYTHONPATH=src python -m uvicorn tianji_kb.api:app --host 127.0.0.1 --port 8000
```

统一入口 `POST /api/v1/execute`；能力清单 `GET /api/v1/capabilities`；健康检查 `GET /health`；OpenAPI `/openapi.json`、`/docs`。七域复用同一 engine，返回盘面、RuleMatch、trace、Evidence、限制和可选AI解释。

生产请求只读取已审运行快照与Canonical检索制品；`explain=false`完全不调用模型。模型失败或未知引用会拒绝解释，确定性结果仍正常返回。调用示例见 [Phase 3 API](docs/phase3/API.md)，模型环境配置见 [providers](docs/phase3/PROVIDERS.md)。

Phase 4 adds versioned explanation contracts and a fixed 102-case, six-domain evaluation suite (the historical Phase 4 suite remains frozen; Bazi requires its own later model-evaluation cases). See [evaluation and human review](docs/phase4/EVALUATION.md), [prompt policy](docs/phase4/PROMPTS.md), and [current quality status](docs/phase4/QUALITY_STATUS.md). Live-model scores are N/A until an environment-configured provider is actually evaluated; test providers never establish AI release readiness.

## 服务端独立运行制品（安全隔离）

> 当前 GitHub 仓库 **仍为公开仓库**。已提交的 Canonical / Quarantine 及历史版本仍可公开访问，不能因为启用此功能就宣称知识库已私有化。正式保密需要迁移到私有存储/私有仓库并审查历史公开范围。

以下操作在**受控构建环境**完成，服务端专用制品中包含经审核知识内容，因此**严禁**上传到静态网站、公开 Release 或公共构件存储：

```bash
export PYTHONPATH=src
python scripts/build_production_runtime.py
python scripts/export_sealed_runtime.py --destination /secure/tianji-runtime-v1
```

导出内容包括校验过的后端 Python 代码、`build/production_runtime.json`、`build/production_rag.jsonl` 以及九个冻结算法必需的 Canonical 查表 JSON；**不会包含** Quarantine、原始采集库或整套 Canonical 知识语料。这九个查表文件仍属于服务端受保护知识材料，不能部署为公开静态资源。默认文件权限 0600。前端只部署 `web/visual-prototype/dist`，服务端持有完整的私有后端目录：

```bash
export TIANJI_RUNTIME_MODE=sealed
export TIANJI_RUNTIME_ROOT=/secure/tianji-runtime-v1
export TIANJI_RUNTIME_SHA256=<导出打印的sha256_pin>
PYTHONPATH=/secure/tianji-runtime-v1/src python -m uvicorn tianji_kb.api:app --host 127.0.0.1 --port 8000
```

运行时必须核对独立部署的 SHA256 pin、审核载荷摘要、RAG 摘要、九份查表摘要和目录文件白名单。缺文件、篡改制品、缺 pin 或混入源码时拒绝服务。构建阶段仍用全部 Canonical 校验，**不能**用独立制品模式绕过知识审核。API 的公开输出仍需按产品能力分级；服务端隔离不等于公开接口可以返回内部资料。API 网关还必须确保私有目录不可通过静态 HTTP 路由访问。

## 公开产品 API 与内部审计 API 分离

浏览器产品页调用 `POST /api/v1/public/execute`（仅正式八字、六爻）或 `POST /api/v1/scenarios/public`（已启用的正式/受限场景）。这两个入口保留真实确定性结果、最多 120 字的审核原典短引、审核级别，以及步骤名称；不发送内部来源仓库、路径、SHA、完整 Evidence 与输入 Trace。响应设置 `Cache-Control: no-store`。研究模式、LLM 解释和未发布梦境场景不能通过此入口开启。

原始 `/api/v1/execute` 和 `/api/v1/scenarios/execute` 仍为**详细诊断接口**。在 `TIANJI_RUNTIME_MODE=sealed` 模式下，它们默认不可用；确需内部分析时，在服务端配置独立的 `TIANJI_INTERNAL_EXECUTE_TOKEN`，并由可信后端在 Authorization Bearer 中调用。**不得将此令牌放入网页、VITE_* 配置、浏览器代码或公开前端**。非 sealed 模式保留历史 API 兼容性，生产部署必须选用 sealed 模式才能启用这项详细接口门禁。

这是 HTTP 响应最小化控制，不会让已经公开发布的 GitHub 历史资料变私有，也不能替代 API 网关、权限审计与知识资产私有迁移。
