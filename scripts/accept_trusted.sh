#!/usr/bin/env bash
# 天机平台一键可信机器验收脚本 (Linux)
# 用途：在可信 Linux 机器上执行完整离线验收
set -euo pipefail

# ============ 配置区（必须修改） ============
PUBLIC_REPO="/opt/tianji-knowledge-base"          # 公开仓库绝对路径
PRIVATE_REPO="/opt/tianji-private-knowledge"      # 私有仓库本地克隆绝对路径
PUBLIC_SHA="4861cdc833d1d51852a06570f2a2e0ec17fd2cc5"  # 待验收的公开 Head
SNAPSHOT_ROOT="/secure"                           # 快照父目录
# ============================================

SNAPSHOT_DIR="$SNAPSHOT_ROOT/tianji-knowledge"
BACKUP_DIR="$SNAPSHOT_ROOT/tianji-knowledge-backup-$(date +%Y%m%d)"

echo "=== 步骤0：环境检查 ==="
python3 --version
git --version
[[ -d "$PUBLIC_REPO" ]] || { echo "ERROR: 公开仓库不存在"; exit 1; }
[[ -d "$PRIVATE_REPO" ]] || { echo "ERROR: 私有仓库不存在"; exit 1; }
[[ ${#PUBLIC_SHA} -eq 40 ]] || { echo "ERROR: PUBLIC_SHA 必须为40位"; exit 1; }

OBSERVED=$(git -C "$PUBLIC_REPO" rev-parse HEAD)
[[ "$OBSERVED" == "$PUBLIC_SHA" ]] || { echo "ERROR: HEAD ($OBSERVED) 与预期 ($PUBLIC_SHA) 不一致"; exit 1; }
DIRTY=$(git -C "$PUBLIC_REPO" status --porcelain)
[[ -z "$DIRTY" ]] || { echo "ERROR: 公开仓库有未提交改动"; exit 1; }
echo "公开仓库验证通过: $PUBLIC_SHA"

echo ""
echo "=== 步骤1：导出知识快照 ==="
[[ -e "$SNAPSHOT_DIR" ]] && { echo "ERROR: 快照目标已存在: $SNAPSHOT_DIR"; exit 1; }
mkdir -p "$SNAPSHOT_ROOT"
chmod 0700 "$SNAPSHOT_ROOT"
TRUSTED_SHA=$(python3 - <<PYEOF
from pathlib import Path
import sys, hashlib
sys.path.insert(0, "$PUBLIC_REPO")
from scripts.private_data_snapshot import export_private_data, verify_private_data
snap = Path("$SNAPSHOT_DIR")
m = export_private_data(Path("$PRIVATE_REPO"), snap)
print(f"导出: {m['file_count']} 个数据文件, {m['total_bytes']} 字节", file=sys.stderr)
m2 = verify_private_data(snap)
sha = hashlib.sha256((snap / "private-data-manifest.json").read_bytes()).hexdigest()
print(sha)
PYEOF
)
[[ ${#TRUSTED_SHA} -eq 64 ]] || { echo "ERROR: 未能获取可信 manifest SHA256"; exit 1; }
echo "可信 manifest SHA256 已记录（独立来源：本次可信导出）"

echo ""
echo "=== 步骤2：第二份独立备份 + 恢复演练 ==="
[[ -e "$BACKUP_DIR" ]] && { echo "ERROR: 备份目标已存在"; exit 1; }
cp -a "$SNAPSHOT_DIR" "$BACKUP_DIR"
chmod 0700 "$BACKUP_DIR"
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path('$BACKUP_DIR'))
print(f\"第二份备份验证通过: {m['file_count']} 文件\")
"
RESTORE_TMP=$(mktemp -d)
cp -a "$BACKUP_DIR"/. "$RESTORE_TMP"/
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path('$RESTORE_TMP'))
print(f\"恢复演练通过: {m['file_count']} 文件\")
"
rm -rf "$RESTORE_TMP"
echo "备份与恢复演练完成"

echo ""
echo "=== 步骤3：运行离线全量验收 ==="
cd "$PUBLIC_REPO"
python3 scripts/accept_offline.py \
  --public-code "$PUBLIC_REPO" \
  --expected-sha "$PUBLIC_SHA" \
  --knowledge-snapshot "$SNAPSHOT_DIR" \
  --trusted-manifest-sha256 "$TRUSTED_SHA" \
  --suite all

echo ""
echo "=== 验收完成 ==="
echo "公开 Head: $PUBLIC_SHA"
echo "知识 manifest SHA256: $TRUSTED_SHA"
