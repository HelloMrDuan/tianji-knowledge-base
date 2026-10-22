#!/usr/bin/env bash
# 天机平台一键可信机器验收 (Linux)
# 用法：./accept_trusted.sh <公开仓库> <私有仓库> <公开40位SHA> <私有40位SHA> <快照父目录>
set -euo pipefail

[[ $# -eq 5 ]] || { echo "用法: $0 <公开仓库> <私有仓库> <公开SHA> <私有SHA> <快照父目录>"; exit 1; }
PUBLIC_REPO="$1"; PRIVATE_REPO="$2"; PUBLIC_SHA="$3"; PRIVATE_SHA="$4"; SNAPSHOT_ROOT="$5"

[[ ${#PUBLIC_SHA} -eq 40 ]] || { echo "ERROR: 公开SHA必须40位"; exit 1; }
[[ ${#PRIVATE_SHA} -eq 40 ]] || { echo "ERROR: 私有SHA必须40位"; exit 1; }
[[ -d "$PUBLIC_REPO" ]] || { echo "ERROR: 公开仓库不存在"; exit 1; }
[[ -d "$PRIVATE_REPO" ]] || { echo "ERROR: 私有仓库不存在"; exit 1; }

SNAPSHOT_DIR="$SNAPSHOT_ROOT/tianji-knowledge"
BACKUP_DIR="$SNAPSHOT_ROOT/tianji-knowledge-backup-$(date +%Y%m%d)"

echo "=== 步骤0：环境与版本核对 ==="
python3 --version; git --version
OBSERVED=$(git -C "$PUBLIC_REPO" rev-parse HEAD)
[[ "$OBSERVED" == "$PUBLIC_SHA" ]] || { echo "ERROR: 公开HEAD不一致"; exit 1; }
[[ -z "$(git -C "$PUBLIC_REPO" status --porcelain)" ]] || { echo "ERROR: 公开仓库有改动"; exit 1; }
PRIV_OBSERVED=$(git -C "$PRIVATE_REPO" rev-parse HEAD)
[[ "$PRIV_OBSERVED" == "$PRIVATE_SHA" ]] || { echo "ERROR: 私有HEAD不一致"; exit 1; }
echo "版本核对通过"
[[ -e "$SNAPSHOT_DIR" ]] && { echo "ERROR: 快照已存在，不自动删除"; exit 1; }
[[ -e "$BACKUP_DIR" ]] && { echo "ERROR: 备份已存在，不自动删除"; exit 1; }
mkdir -p "$SNAPSHOT_ROOT"; chmod 0700 "$SNAPSHOT_ROOT"

echo ""
echo "=== 步骤1：导出知识快照 ==="
read -r TRUSTED_SHA FILE_COUNT < <(python3 <<PYEOF
from pathlib import Path
import sys, hashlib
sys.path.insert(0, "$PUBLIC_REPO")
from scripts.private_data_snapshot import export_private_data, verify_private_data
snap = Path("$SNAPSHOT_DIR")
m = export_private_data(Path("$PRIVATE_REPO"), snap)
verify_private_data(snap)
sha = hashlib.sha256((snap / "private-data-manifest.json").read_bytes()).hexdigest()
print(sha, m["file_count"])
PYEOF
)
[[ ${#TRUSTED_SHA} -eq 64 ]] || { echo "ERROR: 未能获取可信SHA"; exit 1; }
echo "导出 $FILE_COUNT 个文件"

echo ""
echo "=== 步骤2：逐文件比对 ==="
python3 <<PYEOF
from pathlib import Path
import sys, hashlib, json
sys.path.insert(0, "$PUBLIC_REPO")
snap = Path("$SNAPSHOT_DIR")
manifest = json.loads((snap / "private-data-manifest.json").read_text(encoding="utf-8"))
bad = [r["path"] for r in manifest["files"]
       if not (snap / r["path"]).is_file()
       or hashlib.sha256((snap / r["path"]).read_bytes()).hexdigest() != r["sha256"]]
if bad:
    print("MISMATCHED:", bad[:10], file=sys.stderr); sys.exit(1)
print(f"verified {len(manifest['files'])} files")
PYEOF
echo "逐文件比对通过"

echo ""
echo "=== 步骤3：独立备份 + 恢复演练 ==="
echo "注意：备份与快照在同一父目录。如需独立灾难恢复，请手动复制到独立磁盘。"
cp -a "$SNAPSHOT_DIR" "$BACKUP_DIR"; chmod 0700 "$BACKUP_DIR"
python3 -c "
from pathlib import Path; import sys
sys.path.insert(0, '$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path('$BACKUP_DIR'))
print(f\"backup: {m['file_count']} files\")"
RESTORE_TMP=$(mktemp -d)
cp -a "$BACKUP_DIR"/. "$RESTORE_TMP"/
python3 -c "
from pathlib import Path; import sys
sys.path.insert(0, '$PUBLIC_REPO')
from scripts.private_data_snapshot import verify_private_data
m = verify_private_data(Path('$RESTORE_TMP'))
print(f\"restore: {m['file_count']} files\")"
rm -rf "$RESTORE_TMP"
echo "备份与恢复完成"

echo ""
echo "=== 步骤4：离线全量验收 ==="
cd "$PUBLIC_REPO"
python3 scripts/accept_offline.py \
  --public-code "$PUBLIC_REPO" \
  --expected-sha "$PUBLIC_SHA" \
  --knowledge-snapshot "$SNAPSHOT_DIR" \
  --trusted-manifest-sha256 "$TRUSTED_SHA" \
  --suite all

echo ""
echo "=== 验收完成 ==="
echo "公开: $PUBLIC_SHA | 私有: $PRIVATE_SHA | 文件: $FILE_COUNT"
