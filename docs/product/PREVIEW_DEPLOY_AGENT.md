# TJ-027.1 预览部署代理：机上安装与运行手册

> 本手册对应公开仓 `scripts/deploy-agent-tj.sh`（机上 bash 代理的演进版）
> 与 `scripts/deploy-preview-compose.yml`（预览 web-only compose 模板）。
> 本手册不含任何密钥与私有内容；所有路径均为操作员环境配置。

## 1. 这是什么

机上原有代理只服务稳定通道（prerelease，端口 8080）：盯 main 头 →
本机离线密封验收 → 本机构建密封镜像（绝不推送）→ GHCR 拉 web 镜像 →
私有仓 compose 切换 → 健康 + 真实 bazi 门禁 → 失败回滚。

演进版**只做加法**，稳定通道的验收、构建、健康、回滚逻辑原样保留：

- **预览通道**：每开发分支一个 web-only 容器，独立回环端口、独立
  compose 项目（`tianji-preview-<slug>`）、独立 env/state 文件。
  预览挂到稳定网络，`/api/` 代理到**已验收的稳定密封后端**——预览
  绝不构建密封镜像，机制上无法绕过密封验收。
- **稳定保护**：稳定通道（prerelease）只接受 main；任何把稳定通道
  指向其他分支的企图一律记 `REFUSED` 日志并拒绝，服务不动。
- **容量护栏**：`MAX_PREVIEWS`（默认 5，3–5 均合理；每预览仅约
  97MB nginx 静态容器）。超限时拒绝新建，绝不驱逐已有预览。
- **恢复对账**：systemd timer 每 2 分钟重跑代理；各通道只在头 SHA
  变化时才动，幂等。机器从闲置暂停恢复后，timer 触发即自动对账。
- **首次发布**：预览首次成功部署时调用 `instabox-port publish <端口>`；
  失败只记日志，不破坏部署（可手动发布）。

## 2. 安装（替换旧脚本）

```bash
CICD=/data/workspace/platform-deploy/cicd
cp "$CICD/deploy-agent-tj.sh" "$CICD/deploy-agent-tj.sh.bak"
cp <公开仓>/scripts/deploy-agent-tj.sh "$CICD/deploy-agent-tj.sh"
cp <公开仓>/scripts/deploy-preview-compose.yml "$CICD/deploy-preview-compose.yml"
chmod +x "$CICD/deploy-agent-tj.sh"
bash -n "$CICD/deploy-agent-tj.sh"
```

systemd service 与 timer **不用改**（timer 已每 2 分钟跑一次代理；
`oneshot` 服务显示 failed 多为节流重跑 exit 1 的表象，先看部署日志，
不以服务状态单独断定部署失败）。

## 3. 操作员配置（环境变量，默认值即机上布局）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `BASE` | `/data/workspace/platform-deploy` | 部署根目录 |
| `CICD` | `$BASE/cicd` | 代理工作目录（channels/env/state/build） |
| `STATE` | `$CICD/state` | 每通道 state 文件 |
| `EVID` / `LOG` | `$BASE/deployment-evidence/tj-core-01` / `deploys.log` | JSON 部署日志 |
| `PREVIEW_COMPOSE` | 脚本同目录 `deploy-preview-compose.yml` | 预览 compose 模板 |
| `PREVIEW_PORT_START` | `8101` | 预览端口起点（稳定 8080 不在此范围） |
| `MAX_PREVIEWS` | `5` | 预览上限 |
| `TIANJI_PREVIEW_NETWORK` | `tianji_tianji-private-net` | 稳定网络名 |

## 4. 预览通道操作

```bash
CICD=/data/workspace/platform-deploy/cicd
# 启用：文件名为 slug（小写、安全字符），内容为分支名
echo "feature-xyz" > "$CICD/channels/tianji-preview-feature-xyz.branch"
# 暂停（服务不动，timer 跳过）：touch "$CICD/channels/tianji-preview-feature-xyz.paused"
# 停用：删除 .branch 文件即停止对账；容器需手动移除：
docker compose -p tianji-preview-feature-xyz -f "$CICD/deploy-preview-compose.yml" \
  --env-file "$CICD/env/tianji-preview-feature-xyz.env" down
# 手动清理残留 state（端口、SHA、发布标记）时一并删除：
#   $CICD/state/tianji-preview-feature-xyz.{port,sha,web-image,published}
```

每通道文件：

- state：`tianji-preview-<slug>.{sha,web-image,port,published}`
- env：`$CICD/env/tianji-preview-<slug>.env`（仅 web 镜像与端口）
- 日志：`deploys.log` 中 `channel="preview-<slug>"`，含 `port` 字段

## 5. 诚实边界（必须明文）

- **CI 绿 / 镜像已推送 / wake 成功不等于部署完成。** 部署完成只认
  机上证据：`deploys.log` 的 `DEPLOYED` 行 + `docker inspect` 核对的
  实际镜像 + 健康检查结果。
- **稳定验收门禁不变。** 预览通道不改变稳定通道的离线密封验收、
  SHA/PIN、健康与回滚要求；稳定通道 49904972 之后的验收失败仍在
  诊断中，fail-closed 停在原版本是门禁的正确行为，不是本批要修的。
- **预览不绕过密封验收。** 预览后端就是已验收的稳定密封后端；
  预览从不构建、从不推送密封镜像。
- **容量是护栏不是承诺。** 默认上限 5 个预览；机器实际能撑几个以
  机上实测为准，超限拒绝即为正确行为。

## 6. 三轮真实机器验收（操作与应回传证据）

> 以下三轮必须在 tj-core-01 上真实执行，仓库侧模拟测试通过不代替。

**第 1 轮：开发分支 push → 预发布更新，稳定不变**

1. 推送一开发分支（CI 构建 GHCR 镜像；分支恢复 job 仅访问已发布
   URL 恢复机器——恢复 ≠ 部署）。
2. 机上启用预览：`echo <分支> > $CICD/channels/tianji-preview-<slug>.branch`，
   等 timer 一轮（约 2 分钟）。
3. 回传：预览 `DEPLOYED` 日志行（含 channel/port/sha）、预览端口
   `curl 127.0.0.1:<port>/health`（须含 `rag_ready:true`）、
   `docker inspect tianji-preview-<slug>-tianji-web-1` 的实际镜像、
   稳定 `docker inspect tianji-tianji-web-1` 仍为原镜像的证据。

**第 2 轮：main push → 稳定更新，预发布不受影响**

1. 推送 main（main wake 恢复机器；稳定通道走完整离线密封验收门禁）。
2. 回传：稳定 `DEPLOYED` 日志行（或验收失败时的 `ACCEPTANCE_FAILED`
   行——失败时稳定不动即为正确行为）、稳定新镜像 inspect 证据、
   预览容器与端口未变的证据。

**第 3 轮：模拟部署失败 → 自动回滚，日志可追溯**

1. 推送一分支，其 GHCR 镜像故意使预览健康门禁失败（例如 web 镜像
   的 `/health` 不再返回 `rag_ready:true`），或在预览部署后手动停掉
   稳定后端再触发预览更新（门禁失败路径相同）。
2. 回传：预览 `FAILED_ROLLED_BACK` 日志行、回滚后 env 文件与
   inspect 均回到上一健康镜像的证据、稳定服务全程未动的证据。

三轮任一轮未在真实机器上跑出证据，TJ-027.1 就仍是“已提交 PR”，
不得关账为已合并或已部署验收。
