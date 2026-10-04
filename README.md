# 天机传统文化知识库（Tianji Knowledge Base）

面向 AI / RAG / Agent 的中国传统文化与术数知识底座。

目标不是收集几个 prompt，而是建立一套 **可持续更新、可追溯、可审计、可按流派隔离** 的统一知识层，为后续八字、周易、八卦、六爻、梅花易数、紫微斗数、奇门遁甲、大六壬、太乙、风水、姻缘、择日、塔罗等平台能力提供依据。

## 核心原则

- **确定性计算优先**：历法、干支、起卦、排盘等能算的，不让大模型猜。
- **来源优先**：每条知识保存来源、许可证、commit、流派和可信等级。
- **三层隔离**：RAW → QUARANTINE → CANONICAL。
- **不同流派并存**：规则冲突不互相覆盖，以 school/ruleset 区分。
- **AI 只负责解释**：平台先计算、再检索知识库、最后由 LLM 组织语言。
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
