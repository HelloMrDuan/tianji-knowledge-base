<#
.SYNOPSIS
  天机平台一键可信机器验收 (Windows PowerShell 5.1+)
.DESCRIPTION
  在用户自有 Windows 电脑上执行完整离线验收：
  导出知识快照 → 独立备份 → 恢复演练 → 离线全量验收 → 报告
.PARAMETER PublicRepo
  公开仓库绝对路径
.PARAMETER PrivateRepo
  私有仓库本地克隆绝对路径
.PARAMETER PublicSha
  待验收的公开 Head（完整40位）
.PARAMETER SnapshotRoot
  快照父目录（脚本只在此下创建新目录，不删除现有内容）
.PARAMETER PrivateSha
  私有仓库预期的固定 main SHA（用于导出前核对）
.EXAMPLE
  .\accept_trusted.ps1 -PublicRepo "C:\tianji\tianji-knowledge-base" `
    -PrivateRepo "C:\tianji\tianji-private-knowledge" `
    -PublicSha "abc123..." -PrivateSha "def456..." -SnapshotRoot "C:\secure"
#>
param(
    [Parameter(Mandatory=$true)][string]$PublicRepo,
    [Parameter(Mandatory=$true)][string]$PrivateRepo,
    [Parameter(Mandatory=$true)][string]$PublicSha,
    [Parameter(Mandatory=$true)][string]$PrivateSha,
    [Parameter(Mandatory=$true)][string]$SnapshotRoot
)

$ErrorActionPreference = "Stop"

function Test-ExitCode($step) {
    if ($LASTEXITCODE -ne 0) { throw "$step 失败，退出码 $LASTEXITCODE" }
}

# 参数校验
if ($PublicSha.Length -ne 40) { throw "PublicSha 必须为40位" }
if ($PrivateSha.Length -ne 40) { throw "PrivateSha 必须为40位" }
if (-not (Test-Path $PublicRepo)) { throw "公开仓库不存在: $PublicRepo" }
if (-not (Test-Path $PrivateRepo)) { throw "私有仓库不存在: $PrivateRepo" }

$SnapshotDir = Join-Path $SnapshotRoot "tianji-knowledge"
$BackupDir = Join-Path $SnapshotRoot ("tianji-knowledge-backup-" + (Get-Date -Format "yyyyMMdd"))

Write-Host "=== 步骤0：环境与版本核对 ===" -ForegroundColor Cyan
python --version; Test-ExitCode "python"
git --version; Test-ExitCode "git"

# 公开仓库：SHA 匹配 + 干净
$observed = (git -C $PublicRepo rev-parse HEAD).Trim(); Test-ExitCode "git rev-parse"
if ($observed -ne $PublicSha) { throw "公开 HEAD ($observed) 与预期 ($PublicSha) 不一致" }
$dirty = (git -C $PublicRepo status --porcelain).Trim(); Test-ExitCode "git status"
if ($dirty) { throw "公开仓库有未提交改动" }
Write-Host "公开仓库 OK: $PublicSha" -ForegroundColor Green

# 私有仓库：SHA 匹配（导出前核对固定版本）
$privObserved = (git -C $PrivateRepo rev-parse HEAD).Trim(); Test-ExitCode "git rev-parse private"
if ($privObserved -ne $PrivateSha) { throw "私有 HEAD ($privObserved) 与预期 ($PrivateSha) 不一致" }
$privDirty = (git -C $PrivateRepo status --porcelain).Trim(); Test-ExitCode "git status private"
if ($privDirty) { throw "私有仓库有未提交改动，拒绝导出" }
Write-Host "私有仓库 OK: $PrivateSha (干净)" -ForegroundColor Green

# 不删除现有快照/备份
if (Test-Path $SnapshotDir) { throw "快照已存在，不自动删除: $SnapshotDir" }
if (Test-Path $BackupDir) { throw "备份已存在，不自动删除: $BackupDir" }
if (-not (Test-Path $SnapshotRoot)) { New-Item -ItemType Directory -Path $SnapshotRoot -Force | Out-Null }

Write-Host "`n=== 步骤1：导出知识快照 ===" -ForegroundColor Cyan
# 使用 here-string 通过 stdin 传递 Python，避免引号转义问题
$exportPy = @'
from pathlib import Path
import sys, hashlib, json
sys.path.insert(0, r"__PUBLIC__")
from scripts.private_data_snapshot import export_private_data, verify_private_data
snap = Path(r"__SNAP__")
m = export_private_data(Path(r"__PRIVATE__"), snap)
sys.stderr.write("exported %d files\n" % m["file_count"])
m2 = verify_private_data(snap)
sha = hashlib.sha256((snap / "private-data-manifest.json").read_bytes()).hexdigest()
# 输出可信 manifest 内容摘要（独立来源：本次可信导出）
print(sha)
print(m["file_count"])
'@
$exportPy = $exportPy.Replace("__PUBLIC__", $PublicRepo).Replace("__SNAP__", $SnapshotDir).Replace("__PRIVATE__", $PrivateRepo)
$exportResult = $exportPy | python
Test-ExitCode "知识导出"
$lines = $exportResult -split "`n"
$TrustedSha = $lines[0].Trim()
$FileCount = $lines[1].Trim()
if ($TrustedSha.Length -ne 64) { throw "未能获取可信 manifest SHA256" }
Write-Host "导出 $FileCount 个文件，可信 SHA256: $($TrustedSha.Substring(0,16))..." -ForegroundColor Green

Write-Host "`n=== 步骤1b：与私有固定提交的原始 manifest 交叉核对 ===" -ForegroundColor Cyan
# 不仅验证新快照自洽，还要用私有固定提交中的原始 manifest 核对源数据
$crossPy = @'
from pathlib import Path
import sys, hashlib, json, subprocess
sys.path.insert(0, r"__PUBLIC__")
priv = Path(r"__PRIVATE__")
snap = Path(r"__SNAP__")
# 从私有固定提交获取原始 manifest（不依赖工作区状态）
raw = subprocess.check_output(
    ["git", "-C", str(priv), "show", "__PRIVSHA__:private-data-manifest.json"],
    text=True)
orig = json.loads(raw)
newm = json.loads((snap / "private-data-manifest.json").read_text(encoding="utf-8"))
if orig["file_count"] != newm["file_count"]:
    sys.stderr.write("file_count mismatch: orig=%d new=%d\n" % (orig["file_count"], newm["file_count"]))
    sys.exit(1)
orig_map = {r["path"]: r["sha256"] for r in orig["files"]}
new_map = {r["path"]: r["sha256"] for r in newm["files"]}
if set(orig_map) != set(new_map):
    sys.stderr.write("file set mismatch\n")
    sys.exit(1)
bad = [p for p in orig_map if orig_map[p] != new_map[p]]
if bad:
    sys.stderr.write("SHA mismatch: %s\n" % bad[:5])
    sys.exit(1)
print("cross-check OK: %d files match private commit manifest" % len(orig_map))
'@
$crossPy = $crossPy.Replace("__PUBLIC__", $PublicRepo).Replace("__PRIVATE__", $PrivateRepo).Replace("__SNAP__", $SnapshotDir).Replace("__PRIVSHA__", $PrivateSha)
$crossPy | python
Test-ExitCode "原始manifest交叉核对"
Write-Host "与私有固定提交的原始 manifest 一致" -ForegroundColor Green

Write-Host "`n=== 步骤2：逐文件比对（可信源 vs 快照） ===" -ForegroundColor Cyan
$verifyPy = @'
from pathlib import Path
import sys, hashlib, json
sys.path.insert(0, r"__PUBLIC__")
snap = Path(r"__SNAP__")
manifest = json.loads((snap / "private-data-manifest.json").read_text(encoding="utf-8"))
mismatched = []
for row in manifest["files"]:
    target = snap / row["path"]
    if not target.is_file():
        mismatched.append(row["path"] + " (missing)")
        continue
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != row["sha256"]:
        mismatched.append(row["path"] + " (sha mismatch)")
if mismatched:
    sys.stderr.write("MISMATCHED:\n" + "\n".join(mismatched[:10]) + "\n")
    sys.exit(1)
print("verified %d files, all SHA256 match" % len(manifest["files"]))
'@
$verifyPy = $verifyPy.Replace("__PUBLIC__", $PublicRepo).Replace("__SNAP__", $SnapshotDir)
$verifyPy | python
Test-ExitCode "逐文件比对"
Write-Host "逐文件 SHA256 比对通过" -ForegroundColor Green

Write-Host "`n=== 步骤3：独立备份 + 恢复演练 ===" -ForegroundColor Cyan
# 备份位置独立性提示
$snapDrive = (Get-Item $SnapshotRoot).PSDrive.Name
$backupDrive = $snapDrive  # 同一父目录下
Write-Host "注意：备份与快照在同一磁盘 ($snapDrive)。如需独立灾难恢复，请手动复制到独立磁盘。" -ForegroundColor Yellow
Copy-Item -Recurse -Path $SnapshotDir -Destination $BackupDir
if ($LASTEXITCODE -ne 0 -and (Test-Path $BackupDir) -eq $false) { throw "备份复制失败" }

# 验证模板（保留占位符，分别替换）
$verifyTemplate = @'
from pathlib import Path
import sys
sys.path.insert(0, r"__PUBLIC__")
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path(r"__TARGET__"))
print("verified: %d files" % m["file_count"])
'@
$verifyTemplate = $verifyTemplate.Replace("__PUBLIC__", $PublicRepo)

# 验证备份
$backupPy = $verifyTemplate.Replace("__TARGET__", $BackupDir)
$backupPy | python
Test-ExitCode "备份验证"

# 恢复演练：真正验证 $restoreTmp（修复前版本错误地重复验证了 $BackupDir）
$restoreTmp = Join-Path $env:TEMP ("tianji-restore-" + (Get-Random))
New-Item -ItemType Directory -Path $restoreTmp | Out-Null
Copy-Item -Recurse -Path (Join-Path $BackupDir "*") -Destination $restoreTmp
$restorePy = $verifyTemplate.Replace("__TARGET__", $restoreTmp)
$restorePy | python
Test-ExitCode "恢复验证"
Remove-Item -Recurse -Force $restoreTmp
Write-Host "备份与恢复演练完成" -ForegroundColor Green

Write-Host "`n=== 步骤4：离线全量验收 ===" -ForegroundColor Cyan
Set-Location $PublicRepo
python scripts/accept_offline.py --public-code $PublicRepo --expected-sha $PublicSha `
  --knowledge-snapshot $SnapshotDir --trusted-manifest-sha256 $TrustedSha --suite all
Test-ExitCode "离线验收"

Write-Host "`n=== 验收完成 ===" -ForegroundColor Green
Write-Host "公开 Head: $PublicSha"
Write-Host "私有版本: $PrivateSha"
Write-Host "知识文件数: $FileCount"
Write-Host "Manifest SHA256: $TrustedSha"
