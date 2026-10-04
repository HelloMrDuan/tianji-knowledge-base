# 本地后端就绪检查与七牛模型校准

知识库构建和确定性计算不需要模型密钥。真实模型校准需要后端密钥；API 读取进程环境，不自动加载 `.env` 文件。`.env.api.example` 只是变量说明，复制文件不会完成配置。密钥不得写入前端、Git、命令参数或聊天。

## 已实现范围与准确性边界

当前计算 API 注册六域：六爻、奇门、六壬、紫微、风水、易经。八字已有知识资料，但尚未注册可执行排盘服务；网站的八字设计页不能视为已完成后端。

| 域 | 已实现计算范围 | 必须保留的限制 |
| --- | --- | --- |
| 六爻 | 八宫、世应、纳甲、六亲、六神、旬空、月破与动变 | 不含完整旺衰、用神选择和吉凶判断 |
| 奇门 | `qfdk-exact-term-midnight-v2` 精确节气、符头三元表及转盘遁局、地星门神盘 | 不泛化为整个茅山派或其他流派；置闰/超接未实现，历法实现证据仍保留 D 级范围 |
| 六壬 | 天地盘、四课、九宗门三传 | 不含完整贵人与天将判读 |
| 紫微 | 身命宫、五行局、十二宫、十四主星与已实现辅星/四化 | 闰月和流派冲突不自动裁决；四化实现证据保留 D 级范围 |
| 风水 | 方位、二十四山、后天八卦、五行与对宫 | 绝对年份推元运仍仅供研究，不作为生产已验证能力 |
| 易经 | 六爻位编码、六十四卦、错综互变 | 卦象计算通过不代表任意解卦结论成立 |

精确变体、范围和未决问题以 `/api/v1/capabilities` 与 `build/backend-readiness.json` 为准。固定案例验证计算是否符合登记规则，不证明预测现实事件准确。引用可追溯也不自动证明语义推论成立。来源 A/B 级独立证据仍不足，不能宣称全知识库已经完成权威交叉校验。

《三命通会》保留 `quarantine_only`、`canonical_ready=false`；未创建 Canonical 文件。当前 main 的校勘记录为 603 条，PUA 86/86 codepoint、524/524 occurrence、remaining=0。原始快照和已确认映射不在本次修改范围。

## Windows 本地检查

在仓库根目录的 PowerShell 中执行，首次创建虚拟环境后安装依赖：

```powershell
python -m venv .venv
$env:PYTHONUTF8 = '1'
& .\.venv\Scripts\python.exe -m pip install -e '.[validation,calendar,api]'
& .\.venv\Scripts\python.exe scripts/validate_kb.py
& .\.venv\Scripts\python.exe scripts/validate_knowledge.py
& .\.venv\Scripts\python.exe scripts/build_production_runtime.py
& .\.venv\Scripts\python.exe scripts/validate_phase2.py
& .\.venv\Scripts\python.exe scripts/check_backend_readiness.py
& .\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
& .\.venv\Scripts\python.exe scripts/evaluate_explanations.py --dry-run
```

每一步失败都先修复再继续。受保护文件的 SHA256 不能为通过测试而改写。

Windows 依赖安装包括 `tzdata`，让既有 `Asia/Shanghai` 历法转换可用；参见 [Python 官方时区数据说明](https://docs.python.org/3/library/zoneinfo.html#data-sources)。运行快照统一使用 `/` 路径。Git 属性保留 LF 代码/数据与 quarantine 原始字节，避免自动换行造成受保护哈希失配。旧 Windows checkout 如已有 CRLF，需要在保留本地工作后重新 checkout；仅拉取 `.gitattributes` 不一定重写现存文件。

离线报告输出至忽略提交的 `build/backend-readiness.json`，包含运行包与 RAG 完整性、已运行 Golden Cases、源证据等级、变体范围和三命隔离状态。`deterministic_backend_ready=true` 仅对应这些检查。模型质量、语义复核和自动发布资格不会由离线报告授予；真实评分保持未检查/空值。

## 七牛校准入口

用户已选择继续使用 `https://api.qnaigc.com/v1`。本地未带密钥的 `/models` 请求返回 HTTP 200，只说明可访问模型列表，不能证明密钥有效、账号有该模型权限或回答质量。

在本机交互终端运行：

```powershell
# 首先验证一个实际公布且能通过 JSON 对话探针的模型
& .\.venv\Scripts\python.exe scripts/calibrate_qiniu.py

# 再运行固定评测与导出未评分人工复核模板
& .\.venv\Scripts\python.exe scripts/calibrate_qiniu.py --evaluate
```

若后端环境没有 `TIANJI_AI_API_KEY`，命令会隐藏输入；密钥只传给校准子进程，不写入文件或持久环境，不启用服务端公开 AI 功能。非交互环境没有密钥会直接停止，避免退回明文输入。发现阶段最多尝试三个实际公布的模型，不凭空填模型名；JSON 探针通过仍不算解释质量通过。

`--evaluate` 按 v1/v2 各 102 案例执行，共 204 个评测案例，正常案例会调用真实服务。结果按运行独立存放在 `build/provider-discovery/<run-id>/`，防止误用旧报告；输出中不含密钥。模型发现/评测只使用校准子进程环境，选中模型不会自动变成 API 服务的默认模型。上线配置须后续选定实测和复核合格的准确模型 ID。

控制台会输出每次模型请求开始和结束，`<prompt>-progress.jsonl` 记录请求序号、耗时和有限状态码，不记录请求头、密钥或错误正文。`reply_received` 仅表示拿到回复，不是案例通过或准确性认证。每版完整 JSON/Markdown 报告在该版全部案例结束后写出；不能把模型探针完成当成整轮评测完成。旧版本运行没有逐请求进度时，应保持窗口打开并等待完整报告。

v2 未评分模板位于该运行的 `explanation-evals/human-review-v2.json`。按 [固定评测和人工复核流程](EVALUATION.md) 审阅实际回复与上下文，记录复核人、时间、完整性和逐条语义判断，再用 `review_explanations.py --reviews` 绑定原报告。空模板、机械 fixture、缺失回复和连通性探针都不具备发布资格。未实测及未完成复核前，真实模型指标是 N/A；生产保持 AI disabled/`explain=false`。

## 网站后续接入

默认启动确定性服务：

```powershell
$env:TIANJI_AI_PROVIDER = 'disabled'
& .\.venv\Scripts\python.exe -m uvicorn tianji_kb.api:app --host 127.0.0.1 --port 8000
```

在另一终端执行 `python scripts/check_api.py` 核验真实 HTTP 六域响应。网站需显示真实的范围、出处、限制和失败状态；八字未实现的功能继续标为待接入。真实模型通过固定评测和人工复核后，也只能按被评审的模型、提示词、流派和案例范围进入受监督试用，不能据此承诺所有问题都正确。
