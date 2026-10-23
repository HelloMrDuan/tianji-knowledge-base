# 可信机器执行命令：知识备份与离线验收

> **术语澄清**：235 是当前 manifest 中的**全部数据文件总数**（含 audit、canonical、
> coverage、index、product、quarantine、reference、registry、research、state、
> upstream 各区），不是“235 份 Canonical”。验收报告必须如实表述。

## 前提

- 一台用户控制的可信机器（Linux 或 Windows + PowerShell 5.1+）
- Python 3.12、git 已安装
- 公开仓库已克隆到 `<PUBLIC>`（如 `/opt/tianji-knowledge-base`），且 `git status` 干净
- 有私有仓库读取权限（仅首次备份需要）

## 步骤1：创建受控知识目录（Linux）

```bash
# 只创建父目录；导出目标本身必须不存在（export_private_data 会自行创建）
if [ -e /secure/tianji-knowledge ]; then
  echo "ERROR: /secure/tianji-knowledge already exists, choose a new path"
  exit 1
fi
sudo mkdir -p /secure
sudo chmod 0700 /secure
sudo chown "$USER:$USER" /secure
```

## 步骤1：创建受控知识目录（Windows PowerShell）

```powershell
# 只创建父目录；导出目标本身必须不存在（export_private_data 会自行创建）
if (Test-Path C:\secure\tianji-knowledge) {
  Write-Error "C:\secure\tianji-knowledge already exists, choose a new path"
  exit 1
}
New-Item -ItemType Directory -Path C:\secure -Force | Out-Null
icacls C:\secure /inheritance:r | Out-Null
icacls C:\secure /grant:r "$env:USERNAME:(OI)(CI)F" | Out-Null
```

## 步骤2：从私有仓库导出知识快照（仅首次）

```bash
cd <PUBLIC>
# 确认公开仓库干净
git status --porcelain --untracked-files=all -- config src scripts tests schemas evals docs deploy web .github/workflows pyproject.toml
# 上条命令必须无输出，否则停止

python3 - <<'PYEOF'
from pathlib import Path
from scripts.private_data_snapshot import export_private_data
manifest = export_private_data(
    Path("/path/to/private-clone"),   # 私有仓库本地克隆（绝对路径）
    Path("/secure/tianji-knowledge"),  # 必须是不存在的目录
)
print(f"exported {manifest['file_count']} total data files, "
      f"{manifest['total_bytes']} bytes")
PYEOF
```

## 步骤3：验证快照并记录可信 manifest SHA256

```bash
python3 - <<'PYEOF'
from pathlib import Path
import hashlib, sys
sys.path.insert(0, "<PUBLIC>")
from scripts.private_data_snapshot import verify_private_data
snap = Path("/secure/tianji-knowledge")
m = verify_private_data(snap)
sha = hashlib.sha256(
    (snap / "private-data-manifest.json").read_bytes()).hexdigest()
print(f"verified {m['file_count']} files")
print(f"TRUSTED_MANIFEST_SHA256={sha}")
print("")
print("独立可信来源说明：")
print("此 SHA256 必须来自独立可信来源，而非快照自身。")
print("首次建立时：在可信机器上直接从私有数据源导出并验证后，")
print("将此 SHA256 记录在受控位置（如加密笔记或独立配置文件）。")
print("后续验收时：--trusted-manifest-sha256 使用该独立记录的值，")
print("验收工具会验证快照内 manifest 的 SHA256 与独立记录一致，")
print("防止伪造快照+清单对。")
PYEOF
```

## 步骤4：第二份独立备份 + 恢复演练

```bash
# 第二份备份放在独立受控位置（不同目录，推荐不同磁盘）
BACKUP2="/secure/tianji-knowledge-backup-$(date +%Y%m%d)"
if [ -e "$BACKUP2" ]; then echo "ERROR: $BACKUP2 exists"; exit 1; fi
cp -a /secure/tianji-knowledge "$BACKUP2"
chmod 0700 "$BACKUP2"

# 完整重新验证第二份备份
python3 - <<PYEOF
from pathlib import Path
import sys
sys.path.insert(0, "<PUBLIC>")
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path("$BACKUP2"))
print(f"backup2 verified: {m['file_count']} files")
PYEOF

# 恢复演练：从第二份备份恢复到临时目录并验证
RESTORE_TMP="$(mktemp -d)"
cp -a "$BACKUP2"/. "$RESTORE_TMP"/
python3 - <<PYEOF
from pathlib import Path
import sys
sys.path.insert(0, "<PUBLIC>")
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path("$RESTORE_TMP"))
print(f"restore drill passed: {m['file_count']} files")
PYEOF
rm -rf "$RESTORE_TMP"
echo "restore drill OK"
```

## 步骤4（Windows PowerShell）：第二份备份 + 恢复演练

```powershell
$Backup2 = "D:\secure\tianji-knowledge-backup-$(Get-Date -Format 'yyyyMMdd')"
if (Test-Path $Backup2) { Write-Error "$Backup2 exists"; exit 1 }
Copy-Item -Recurse -Path C:\secure\tianji-knowledge -Destination $Backup2
icacls $Backup2 /inheritance:r | Out-Null
icacls $Backup2 /grant:r "$env:USERNAME:(OI)(CI)F" | Out-Null

python -c "
from pathlib import Path
import sys
sys.path.insert(0, r'<PUBLIC>')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path(r'$Backup2'))
print(f\"backup2 verified: {m['file_count']} files\")
"

$RestoreTmp = Join-Path $env:TEMP ("restore-" + (Get-Random))
Copy-Item -Recurse -Path "$Backup2\*" -Destination $RestoreTmp
python -c "
from pathlib import Path
import sys
sys.path.insert(0, r'<PUBLIC>')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path(r'$RestoreTmp'))
print(f\"restore drill passed: {m['file_count']} files\")
"
Remove-Item -Recurse -Force $RestoreTmp
Write-Host "restore drill OK"
```

## 步骤5：运行离线验收（Linux）

```bash
cd <PUBLIC>
PUBLIC_SHA="<当前受验PR的最终40位HEAD_SHA>"  # 替换为实际 PR Head
TRUSTED_SHA="<步骤3记录的64位SHA256>"                    # 替换为实际值
python3 scripts/accept_offline.py \
  --public-code <PUBLIC> \
  --expected-sha "$PUBLIC_SHA" \
  --knowledge-snapshot /secure/tianji-knowledge \
  --trusted-manifest-sha256 "$TRUSTED_SHA" \
  --suite all
```

## 步骤5（Windows PowerShell）

```powershell
cd <PUBLIC>
$PUBLIC_SHA = "<当前受验PR的最终40位HEAD_SHA>"
$TRUSTED_SHA = "<步骤3记录的64位SHA256>"
python scripts/accept_offline.py `
  --public-code <PUBLIC> `
  --expected-sha $PUBLIC_SHA `
  --knowledge-snapshot C:\secure\tianji-knowledge `
  --trusted-manifest-sha256 $TRUSTED_SHA `
  --suite all
```

## 成功标准

- 退出码 0
- 输出 JSON evidence 包含：`mode: offline-controlled`、`tool_version`、
  `public_sha`、`knowledge_manifest_sha256`（与可信值一致）、
  `test_reports`（各阶段模块数/测试数/失败数/跳过数）、`result: SUCCESS`
- 明确标注非 GitHub Actions

## 失败回滚

1. 私有仓库未删除，仍可作为数据源
2. 公开代码零改动（迁移分支可删除）
3. 恢复私有 Actions：移除 workflow 的 `paths` 限制或手动触发即可
