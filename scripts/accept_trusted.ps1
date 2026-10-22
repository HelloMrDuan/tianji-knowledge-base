# 天机平台一键可信机器验收脚本 (Windows PowerShell 5.1+)
# 用途：在用户自有 Windows 电脑上执行完整离线验收
# 前提：Python 3.12+, git 已安装；公开仓库已克隆；有私有仓库读取权限
#
# 使用方法（复制执行，替换 <> 中的实际路径）：
#   1. 设置以下 4 个变量
#   2. 逐段复制到 PowerShell 执行，或保存为 .ps1 后执行

# ============ 配置区（必须修改） ============
$PUBLIC_REPO   = "C:\tianji\tianji-knowledge-base"   # 公开仓库绝对路径
$PRIVATE_REPO  = "C:\tianji\tianji-private-knowledge" # 私有仓库本地克隆绝对路径
$PUBLIC_SHA    = "4861cdc833d1d51852a06570f2a2e0ec17fd2cc5"  # 待验收的公开 Head
$SNAPSHOT_ROOT = "C:\secure"                          # 快照父目录（必须存在或可创建）
# ============================================

$ErrorActionPreference = "Stop"
$SNAPSHOT_DIR = Join-Path $SNAPSHOT_ROOT "tianji-knowledge"
$BACKUP_DIR   = Join-Path $SNAPSHOT_ROOT ("tianji-knowledge-backup-" + (Get-Date -Format "yyyyMMdd"))

Write-Host "=== 步骤0：环境检查 ===" -ForegroundColor Cyan
python --version
git --version
if (-not (Test-Path $PUBLIC_REPO)) { throw "公开仓库不存在: $PUBLIC_REPO" }
if (-not (Test-Path $PRIVATE_REPO)) { throw "私有仓库不存在: $PRIVATE_REPO" }
if ($PUBLIC_SHA.Length -ne 40) { throw "PUBLIC_SHA 必须为40位" }

# 确认公开仓库干净且 SHA 匹配
$observed = (git -C $PUBLIC_REPO rev-parse HEAD).Trim()
if ($observed -ne $PUBLIC_SHA) { throw "公开仓库 HEAD ($observed) 与预期 ($PUBLIC_SHA) 不一致" }
$dirty = (git -C $PUBLIC_REPO status --porcelain).Trim()
if ($dirty) { throw "公开仓库有未提交改动，停止" }
Write-Host "公开仓库验证通过: $PUBLIC_SHA" -ForegroundColor Green

Write-Host "`n=== 步骤1：导出知识快照 ===" -ForegroundColor Cyan
if (Test-Path $SNAPSHOT_DIR) { throw "快照目标已存在，请删除或换路径: $SNAPSHOT_DIR" }
if (-not (Test-Path $SNAPSHOT_ROOT)) { New-Item -ItemType Directory -Path $SNAPSHOT_ROOT -Force | Out-Null }
python -c "
from pathlib import Path
import sys
sys.path.insert(0, r'$PUBLIC_REPO')
from scripts.private_data_snapshot import export_private_data, verify_private_data
import hashlib
snap = Path(r'$SNAPSHOT_DIR')
m = export_private_data(Path(r'$PRIVATE_REPO'), snap)
print(f\"导出: {m['file_count']} 个数据文件, {m['total_bytes']} 字节\")
# 立即验证
m2 = verify_private_data(snap)
sha = hashlib.sha256((snap / 'private-data-manifest.json').read_bytes()).hexdigest()
print(f\"验证通过\")
print(f\"TRUSTED_MANIFEST_SHA256={sha}\")
" | Tee-Object -Variable export_out
$TRUSTED_SHA = ($export_out | Select-String "TRUSTED_MANIFEST_SHA256=" | ForEach-Object { $_.Line.Split("=")[1] }).Trim()
if ($TRUSTED_SHA.Length -ne 64) { throw "未能获取可信 manifest SHA256" }
Write-Host "可信 manifest SHA256 已记录（独立来源：本次可信导出）" -ForegroundColor Green

Write-Host "`n=== 步骤2：第二份独立备份 + 恢复演练 ===" -ForegroundColor Cyan
if (Test-Path $BACKUP_DIR) { throw "备份目标已存在: $BACKUP_DIR" }
Copy-Item -Recurse -Path $SNAPSHOT_DIR -Destination $BACKUP_DIR
python -c "
from pathlib import Path
import sys
sys.path.insert(0, r'$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path(r'$BACKUP_DIR'))
print(f\"第二份备份验证通过: {m['file_count']} 文件\")
"
$restoreTmp = Join-Path $env:TEMP ("tianji-restore-" + (Get-Random))
New-Item -ItemType Directory -Path $restoreTmp | Out-Null
Copy-Item -Recurse -Path (Join-Path $BACKUP_DIR "*") -Destination $restoreTmp
python -c "
from pathlib import Path
import sys
sys.path.insert(0, r'$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path(r'$restoreTmp'))
print(f\"恢复演练通过: {m['file_count']} 文件\")
"
Remove-Item -Recurse -Force $restoreTmp
Write-Host "备份与恢复演练完成" -ForegroundColor Green

Write-Host "`n=== 步骤3：运行离线全量验收 ===" -ForegroundColor Cyan
Set-Location $PUBLIC_REPO
python scripts/accept_offline.py `
  --public-code $PUBLIC_REPO `
  --expected-sha $PUBLIC_SHA `
  --knowledge-snapshot $SNAPSHOT_DIR `
  --trusted-manifest-sha256 $TRUSTED_SHA `
  --suite all | Tee-Object -Variable accept_out

if ($LASTEXITCODE -ne 0) { throw "离线验收失败，退出码 $LASTEXITCODE" }

Write-Host "`n=== 验收完成 ===" -ForegroundColor Green
Write-Host "公开 Head: $PUBLIC_SHA"
Write-Host "知识 manifest SHA256: $TRUSTED_SHA"
Write-Host "详细测试报告见上方 JSON 输出（test_reports 含各阶段模块数/测试数/失败/跳过）"
