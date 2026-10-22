# 可信机器执行命令：知识备份与离线验收

## 前提

- 一台用户控制的可信机器（Linux 或 Windows + PowerShell）
- 已安装 Python 3.12、git
- 公开仓库已克隆到 `<PUBLIC>`（如 `/opt/tianji-knowledge-base`）
- 有私有仓库读取权限（仅首次备份需要）

## 步骤1：创建受控知识目录（Linux）

```bash
sudo mkdir -p /secure/tianji-knowledge
sudo chmod 0700 /secure/tianji-knowledge
sudo chown $USER:$USER /secure/tianji-knowledge
```

## 步骤1：创建受控知识目录（Windows PowerShell）

```powershell
New-Item -ItemType Directory -Path C:\secure\tianji-knowledge -Force
icacls C:\secure\tianji-knowledge /inheritance:r /grant:r "$env:USERNAME:(OI)(CI)F"
```

## 步骤2：从私有仓库导出知识快照（仅首次）

```bash
# 在公开仓库目录执行（export_private_data 拒绝导出到仓库内）
cd <PUBLIC>
python scripts/private_data_snapshot.py --help  # 查看用法
# 实际导出（需私有仓库本地克隆到 <PRIVATE>）：
python - <<'PYEOF'
from pathlib import Path
from scripts.private_data_snapshot import export_private_data
manifest = export_private_data(
    Path("<PRIVATE>"), Path("/secure/tianji-knowledge"))
print(f"exported {manifest['file_count']} files")
PYEOF
```

## 步骤3：验证快照（每次验收前自动执行，也可手动）

```bash
python - <<'PYEOF'
from pathlib import Path
from scripts.private_data_snapshot import verify_private_data
import sys
sys.path.insert(0, "<PUBLIC>")
m = verify_private_data(Path("/secure/tianji-knowledge"))
print(f"verified {m['file_count']} files, {m['total_bytes']} bytes")
PYEOF
```

## 步骤4：建立独立备份并验证恢复

```bash
# 第二份备份
cp -a /secure/tianji-knowledge /secure/tianji-knowledge-backup-$(date +%Y%m%d)
# 验证备份可恢复：对比 manifest SHA256
sha256sum /secure/tianji-knowledge/private-data-manifest.json
sha256sum /secure/tianji-knowledge-backup-*/private-data-manifest.json
# 两者必须一致
```

## 步骤5：运行离线验收

```bash
cd <PUBLIC>
# 固定公开 SHA（示例，替换为实际 PR Head）
PUBLIC_SHA="ffb52c5812f8b44c11aef560e2c05f92bb97535d"
python scripts/accept_offline.py \
  --public-code <PUBLIC> \
  --expected-sha $PUBLIC_SHA \
  --knowledge-snapshot /secure/tianji-knowledge \
  --suite all
```

## 步骤5（Windows PowerShell）

```powershell
cd <PUBLIC>
$PUBLIC_SHA = "ffb52c5812f8b44c11aef560e2c05f92bb97535d"
python scripts/accept_offline.py `
  --public-code <PUBLIC> `
  --expected-sha $PUBLIC_SHA `
  --knowledge-snapshot C:\secure\tianji-knowledge `
  --suite all
```

## 成功标准

- 退出码 0
- 输出 JSON evidence 包含：public_sha、knowledge_manifest_sha256、测试模块数、result=SUCCESS
- 明确标注 `mode: offline-controlled`（非 GitHub Actions）

## 失败回滚

- 私有仓库未删除，仍可作为数据源
- 公开代码零改动（迁移分支可删除）
- 恢复私有 Actions：取消 workflow 的 paths 限制即可
