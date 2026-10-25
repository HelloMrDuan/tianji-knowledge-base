# TJ-027.1 机上部署代理运行手册（公开仓，不含密钥与私有内容）

> 适用对象：持有部署机器的操作员。代理只部署公开 Web 镜像，绝不部署、
> 绝不构建、绝不触碰密封 API 镜像。后端版本在所有通道均为同一密封 /
> 已验收版本；预发布 Web 容器与密封 API 同网段、代理到同一 API，机制
> 上就不可能绕过密封验收。
>
> **CI 绿、镜像已推送、wake/resume 成功都不等于部署完成。** 只有本代理
> 经过健康门禁的部署（记录在部署日志与 SHA 证据文件里）才算部署。
> 本文末尾的三轮真实机器验收尚未执行——执行前不得宣称验收通过。

## 1. 代理是什么

`scripts/deploy_agent.py`（仅 Python 标准库 + docker CLI 子进程调用），
运行在操作员的机器上（不在 CI 里），轮询 GHCR 通道标签并对齐各通道：

| 通道 | 来源分支 | GHCR 通道标签 | 容器名 | 宿主端口 |
| --- | --- | --- | --- | --- |
| stable（稳定） | `main` | `channel-main` | `tianji-web-stable` | `TIANJI_DEPLOY_STABLE_PORT`（默认 8080） |
| preview（预发布） | 任意开发分支 | `channel-<分支 slug>` | `tianji-web-preview-<slug>` | 预览端口范围首个空闲端口（默认 18200–18299） |

分支 slug 规则与 `.github/workflows/deploy-pipeline.yml` 的通道标签计算
完全一致（小写、非 `[a-z0-9_.-]` 转 `-`、去首尾无效字符）。

### 隔离规则（机制 + 测试双重保证）

- stable 只接受 `channel-main` 标签指向的镜像。任何以 per-SHA 标签、
  其他通道标签或其他引用部署到 stable 的请求一律拒绝并记审计日志。
- 预览只接受自己通道标签指向的镜像；预览之间不共用容器名与端口，
  绝不覆盖其他分支的预览，绝不触碰 stable。
- 预览容器绑定在回环地址（`127.0.0.1:<port>:8080`），与密封 API 同属
  `TIANJI_DEPLOY_NETWORK`（默认 `tianji-private-net`），`/api/` 代理到
  同一 `tianji-api:8000`。
- 恢复（resume）≠ 部署（deploy）。CI 的 `resume-preview` job 只访问机器
  已发布 URL 以恢复闲置暂停的机器，不部署任何东西；部署决策只由机上
  代理按通道规则执行。#313 的分工不变：仅 main 可唤醒正式机器；本批
  把“恢复”扩展到开发分支，但没有把“部署”扩展到开发分支碰稳定服务。

### 回滚

- 每通道保留上一个健康 SHA/digest。代理**绝不删除、不清理**上一个
  健康镜像（代码里根本没有 image-remove / image-prune 路径），所以回
  滚不依赖 GHCR 可达。
- 新镜像健康门禁失败后，代理自动用本地上一个健康镜像重建并复验健康。
  回滚成功记 `rolled_back`；无上一个健康镜像、或上一个健康镜像本地
  已缺失、或回滚复验失败时，通道标记为 degraded（绝不冒充健康）。
- 部署流程：先拉取新镜像（拉取失败则旧容器继续运行）→ 停旧容器 →
  起新容器 → 健康门禁（容器运行中 + HTTP 健康检查）→ 通过则标记健康，
  失败则回滚。目标端口被其他容器占用时提前拒绝，绝不为抢端口拆掉
  健康部署。

### 健康门禁

复用 `scripts/health_check.py` 前端契约的子集：HTTP 200 + 无泄漏标记
（`traceback`、`tianji-private`、`private-knowledge`、`/root/`、`/home/`）
+ 前端 root 元素存在。完整冒烟（含模块资源、网关 `/api/` 能力）仍由
`health_check.py` 负责，不属于代理门禁。

### 容量护栏

- 预览实例上限 `TIANJI_PREVIEW_LIMIT`（默认 3）。超限时拒绝新建并记
  日志上报，不驱逐已有预览，不触碰 stable，绝不冒称实现全部分支自动
  部署。实际容量须机上实测——上限是护栏，不是容量承诺。
- 容量计数包含状态文件里记录的全部预览（含标签已消失的 stale 预览），
  直到操作员手动清理状态。标签消失的预览默认保留运行、只记 `stale`，
  代理绝不自动删除（删除由操作员决定）。
- 若稳定服务仍由 compose 管理、操作员不希望代理碰 stable，可设
  `TIANJI_DEPLOY_MANAGE_STABLE=0`：代理跳过 stable，只对齐预览。

## 2. 安装与运行

前置条件（操作员机器）：Python 3.12+（仅标准库）、docker CLI、与密封
API 容器相同的 Docker 网络、GHCR 读取权限（公开镜像无需 token；受限
网络可用只读 token，见下）。

```bash
# 从公开仓库检出（代理在仓库内运行，状态目录默认 ./tianji-deploy-state）
cd <repo-checkout>

# 一次对账：机器恢复后、或手动触发时用；只部署有变化的通道，幂等可重跑
python scripts/deploy_agent.py reconcile

# 常驻轮询：按 TIANJI_DEPLOY_POLL_INTERVAL（默认 60s）循环对账
python scripts/deploy_agent.py poll

# 查看各通道状态（SHA/digest/健康/端口/容器）与观测到的后端容器镜像
python scripts/deploy_agent.py status
```

`reconcile` 退出码：全部通道健康或无变化为 0；任一通道失败、降级、
被拒绝或发生回滚为 1（需操作员关注）。`poll` 单轮异常只记日志不退出。

### 环境变量（全部可配置，默认值须与操作员现有栈匹配）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `TIANJI_DEPLOY_STATE_DIR` | `./tianji-deploy-state` | 状态/日志/证据目录（须持久化，丢了则端口与回滚基线重建） |
| `TIANJI_DEPLOY_NETWORK` | `tianji-private-net` | Web 容器接入的网络（须与密封 API 同网段） |
| `TIANJI_DEPLOY_STABLE_PORT` | `8080` | stable 宿主端口（回环绑定） |
| `TIANJI_DEPLOY_API_PORT` | `8000` | 仅用于端口排除（预览绝不占用） |
| `TIANJI_PREVIEW_PORT_START` / `TIANJI_PREVIEW_PORT_END` | `18200` / `18299` | 预览端口范围 |
| `TIANJI_PREVIEW_LIMIT` | `3` | 预览实例上限 |
| `TIANJI_DEPLOY_POLL_INTERVAL` | `60` | 轮询间隔（秒） |
| `TIANJI_DEPLOY_HEALTH_TIMEOUT` / `TIANJI_DEPLOY_HEALTH_INTERVAL` | `60` / `2` | 健康门禁超时与轮询间隔（秒） |
| `TIANJI_DEPLOY_IMAGE_REPO` | `ghcr.io/hellomrduan/tianji-web` | 镜像仓库 |
| `GHCR_TOKEN` | （无） | 可选 GHCR 只读 token，只来自机上环境，绝不进仓库与 CI |
| `TIANJI_DEPLOY_MANAGE_STABLE` | `1` | 设为 `0` 时跳过 stable，只对齐预览 |

### 状态、日志与证据文件（均在 `TIANJI_DEPLOY_STATE_DIR` 下）

- `channels.json`：每通道一条——`sha`、`digest`、健康、更新时间、
  上一个健康 SHA/digest、端口、容器名。
- `deploy.log.jsonl`：每次部署/回滚/拒绝/对账事件一行 JSON（含时间、
  通道、动作、SHA、digest、结果、说明）。
- `evidence.jsonl`：每次成功部署与回滚的版本证据一行（含 digest 钉死
  的镜像引用 `ghcr.io/hellomrduan/tianji-web@sha256:...`）。

“实际部署版本”的可信来源是这里记录的 digest（`docker inspect` 可复核），
不是 CI 绿或镜像已推送。后端版本不在代理部署范围内：`status` 仅在密封
API 容器存在于本机时报告其观测到的镜像（只读查看，绝不管理）；后端
版本仍以可信机密封验收与 `TIANJI_RUNTIME_SHA256` pin 为准。

## 3. 三轮真实机器验收（尚未执行，执行后回传证据）

以下三轮必须在真实机器上实际执行，模拟测试通过绝不替代。每一轮回传：
各通道实际版本 SHA/digest、部署记录（`deploy.log.jsonl` 相关行）、健康
检查结果、回滚验证结果（如有）。

### 第一轮：开发分支 push → 预发布自动更新，稳定环境版本不变

1. 向开发分支（如 `feature/x`）push 一次。
2. CI：test 通过 → build 推送 `tianji-web:<SHA>` + `channel-<slug>` →
   `resume-preview` 访问已发布 URL 恢复机器（仅恢复，不是部署）。
3. 机上代理下一轮对账：`channel-<slug>` 预览更新到该 SHA；`channel-main`
   的 stable 容器 SHA/digest 不变。
4. 核对：`status` 输出中预览通道 SHA/digest 为新值、stable 为旧值；
   预览 URL（回环端口）健康检查通过；stable URL 健康检查通过。

### 第二轮：main push → 稳定环境按已有安全门禁自动更新，预发布不受影响

1. 向 `main` push 一次（须先通过可信机离线密封验收等已有门禁——代理
   本身不执行密封验收，密封验收仍是发布前置条件）。
2. CI：test → build 推送 `channel-main` → `wake` 恢复机器。
3. 机上代理对账：stable 更新到 main 的新 SHA；各预览通道 SHA/digest
   不变、容器不重启。
4. 核对：`status` 输出中 stable 为新值、预览为旧值；stable 与预览健康
   检查均通过。

### 第三轮：模拟部署失败 → 健康检查失败后自动回滚，日志可追溯

1. 选一个预览通道，推送一个健康检查必失败的镜像（例如首页无 root
   元素、或返回非 200 的构建），触发代理部署。
2. 代理健康门禁失败后自动用上一个健康镜像重建并复验健康。
3. 核对：该通道最终版本回到上一个健康 SHA/digest 且健康检查通过；
   `deploy.log.jsonl` 中有部署失败 + `rolled_back` 两行；
   `evidence.jsonl` 中有回滚证据行；stable 与其他预览不受影响。

## 4. 机上阻塞项（仓库侧工作完成后仍需操作员确认）

- 部署机器的 docker 与网络现状（`tianji-private-net` 是否存在、密封 API
  容器是否在同一网络且名为 `tianji-api`）。
- 机器恢复后代理的常驻方式（`poll` 服务或定时 `reconcile`）由操作员选定。
- 预览端口范围与上限是否与机器资源匹配（默认 18200–18299、上限 3；
  资源不足时以护栏拒绝为准，不得冒称全部分支自动部署）。
- 三轮真实机器验收的执行与证据回传（见第 3 节）。
