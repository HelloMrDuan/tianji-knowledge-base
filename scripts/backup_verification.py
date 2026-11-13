#!/usr/bin/env python3
"""TJ-005.3: read-only backup / rollback / health-state verification.

Checks the real deployment base (default /data/workspace/platform-deploy)
and reports gaps. This script NEVER writes, rebuilds, deploys, or touches
the deploy agent: every probe is a read (file read, ``git status``,
``systemctl is-active``, ``docker images``). It contains no private
knowledge and prints no private content -- only counts, manifest
fingerprints, and structural paths.

What it verifies:
- the live private snapshot manifest is self-consistent (and, with
  --full, every file re-hashes to its recorded SHA256);
- the snapshot-rotation backup dirs each carry a valid manifest;
- deploys.log span, result counts, and that the last DEPLOYED SHA
  matches the recorded prerelease state;
- the current + previous image pair and the protected rollback pair
  (``tianji-api:sealed-82b119e`` / ``tianji-web:static-82b119e``) exist
  as docker images (skipped when docker is unavailable);
- rollback history: FAILED_ROLLED_BACK lines split stable vs preview
  (a stable rollback never exercised is reported as a gap);
- the private repo checkout state (read-only git status; a live tree
  that differs from its committed HEAD is reported, not hidden);
- disk headroom against the deploy agent's thresholds;
- the deploy timer state;
- the audit-DB bind-mount target;
- off-machine backup: reported as a gap until an operator records one
  in ``cicd/env/off-machine-backup.json`` (target + last_verified).
  B002 (off-machine backup/migration) is frozen pending user
  authorization, so this check is expected to report the gap today.

Exit code: 0 = every check passed (skips allowed), 1 = at least one
gap found, 2 = the base directory is unusable for verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MANIFEST_NAME = "private-data-manifest.json"
SNAPSHOT_SCHEMA = "private-data-snapshot-v2"
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
PROTECTED_API = "tianji-api:sealed-82b119e"
PROTECTED_WEB = "tianji-web:static-82b119e"
# Deploy agent thresholds (scripts/deploy-agent-tj.sh ensure_disk_tj):
# root filesystem >= 4 GiB free, /data >= 2 GiB free.
MIN_FREE_ROOT_GB = 4
MIN_FREE_DATA_GB = 2


def _hash(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _manifest_self_consistent(manifest: dict) -> str | None:
    """Return an error string, or None when the manifest is self-consistent."""
    if not isinstance(manifest, dict):
        return "manifest is not an object"
    if manifest.get("schema_version") != SNAPSHOT_SCHEMA:
        return "schema_version is not %s" % SNAPSHOT_SCHEMA
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        return "manifest has no files"
    seen = set()
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            return "malformed manifest entry"
        path, size, sha = row.get("path"), row.get("bytes"), row.get("sha256")
        if (not isinstance(path, str) or not path or "\\" in path
                or path in seen or type(size) is not int or size < 0
                or not isinstance(sha, str) or not DIGEST.fullmatch(sha)):
            return "invalid or duplicated manifest entry: %r" % (path,)
        seen.add(path)
        total += size
    if manifest.get("file_count") != len(rows):
        return "file_count does not match the file list"
    if manifest.get("total_bytes") != total:
        return "total_bytes does not match the file list"
    return None


def check_snapshot(base: Path, full: bool) -> dict:
    """Verify the live snapshot dir (not the private repo checkout)."""
    snap = base / "secure" / "tianji-knowledge"
    if not snap.is_dir():
        return {"name": "live_snapshot", "status": "fail",
                "detail": "missing snapshot dir: %s" % snap}
    manifest_path = snap / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"name": "live_snapshot", "status": "fail",
                "detail": "missing manifest: %s" % manifest_path}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"name": "live_snapshot", "status": "fail",
                "detail": "manifest unreadable: %s" % type(exc).__name__}
    error = _manifest_self_consistent(manifest)
    if error:
        return {"name": "live_snapshot", "status": "fail", "detail": error}
    detail = "%d files, %d bytes, schema %s" % (
        manifest["file_count"], manifest["total_bytes"],
        manifest["schema_version"])
    for row in manifest["files"]:
        target = snap / row["path"]
        if not target.is_file():
            return {"name": "live_snapshot", "status": "fail",
                    "detail": "manifested file missing: %s" % row["path"]}
        if target.stat().st_size != row["bytes"]:
            return {"name": "live_snapshot", "status": "fail",
                    "detail": "size mismatch: %s" % row["path"]}
    if full:
        for row in manifest["files"]:
            if _hash(snap / row["path"]) != row["sha256"]:
                return {"name": "live_snapshot", "status": "fail",
                        "detail": "SHA256 mismatch: %s" % row["path"]}
        detail += "; full re-hash OK"
    return {"name": "live_snapshot", "status": "pass", "detail": detail}


def check_rotation_backups(base: Path) -> dict:
    """Every pre-* snapshot dir must carry a self-consistent manifest."""
    secure = base / "secure"
    if not secure.is_dir():
        return {"name": "rotation_backups", "status": "fail",
                "detail": "missing secure dir: %s" % secure}
    backups = sorted(p for p in secure.iterdir()
                     if p.is_dir() and p.name.startswith("tianji-knowledge-pre-"))
    if not backups:
        return {"name": "rotation_backups", "status": "fail",
                "detail": "no tianji-knowledge-pre-* backup dirs found"}
    bad = []
    for backup in backups:
        manifest_path = backup / MANIFEST_NAME
        if not manifest_path.is_file():
            bad.append("%s: no manifest" % backup.name)
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            bad.append("%s: manifest unreadable" % backup.name)
            continue
        error = _manifest_self_consistent(manifest)
        if error:
            bad.append("%s: %s" % (backup.name, error))
    if bad:
        return {"name": "rotation_backups", "status": "fail",
                "detail": "%d backup dirs, %d invalid: %s"
                          % (len(backups), len(bad), "; ".join(bad[:5]))}
    return {"name": "rotation_backups", "status": "pass",
            "detail": "%d backup dirs, all manifests self-consistent: %s"
                      % (len(backups), ", ".join(b.name for b in backups))}


def _parse_deploys_log(path: Path) -> tuple[list[dict], list[str]]:
    rows, errors = [], []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return rows, ["unreadable: %s" % type(exc).__name__]
    for number, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            errors.append("line %d is not JSON" % number)
    return rows, errors


def check_deploys_log(base: Path) -> dict:
    """Span, result counts, and last DEPLOYED vs recorded state."""
    log = base / "deployment-evidence" / "tj-core-01" / "deploys.log"
    if not log.is_file():
        return {"name": "deploys_log", "status": "fail",
                "detail": "missing deploys.log: %s" % log}
    rows, errors = _parse_deploys_log(log)
    if errors:
        return {"name": "deploys_log", "status": "fail",
                "detail": "; ".join(errors[:5])}
    if not rows:
        return {"name": "deploys_log", "status": "fail",
                "detail": "deploys.log is empty"}
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.get("result", "?")] = counts.get(row.get("result", "?"), 0) + 1
    deployed = [r for r in rows if r.get("result") == "DEPLOYED"]
    if not deployed:
        return {"name": "deploys_log", "status": "fail",
                "detail": "%d lines, no DEPLOYED entry; counts %s"
                          % (len(rows), counts)}
    last = deployed[-1]
    state = base / "cicd" / "state" / "tianji-prerelease.sha"
    detail = ("%d lines %s..%s; counts %s; last DEPLOYED %s at %s"
              % (len(rows), rows[0].get("ts"), rows[-1].get("ts"),
                 counts, str(last.get("sha"))[:12], last.get("ts")))
    if state.is_file():
        recorded = state.read_text(encoding="utf-8").strip()
        if recorded and recorded != last.get("sha"):
            return {"name": "deploys_log", "status": "fail",
                    "detail": detail + "; recorded state %s != last DEPLOYED %s"
                              % (recorded[:12], str(last.get("sha"))[:12])}
    return {"name": "deploys_log", "status": "pass", "detail": detail}


def _docker_images() -> set[str] | None:
    """Read-only image list, or None when docker is unavailable."""
    if shutil.which("docker") is None:
        return None
    try:
        out = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def check_image_pairs(base: Path) -> dict:
    """Current + previous pair and the protected rollback pair exist."""
    images = _docker_images()
    if images is None:
        return {"name": "image_pairs", "status": "skip",
                "detail": "docker unavailable; image presence not checked"}
    state = base / "cicd" / "state"
    missing = []
    for name in ("tianji-prerelease.api-image", "tianji-prerelease.web-image"):
        path = state / name
        if not path.is_file():
            missing.append("state file missing: %s" % name)
            continue
        image = path.read_text(encoding="utf-8").strip()
        if image and image not in images:
            missing.append("recorded image not present: %s" % image)
    for image in (PROTECTED_API, PROTECTED_WEB):
        if image not in images:
            missing.append("protected rollback image not present: %s" % image)
    if missing:
        return {"name": "image_pairs", "status": "fail",
                "detail": "; ".join(missing)}
    return {"name": "image_pairs", "status": "pass",
            "detail": "recorded pair + protected rollback pair present"}


def check_rollback_history(base: Path) -> dict:
    """FAILED_ROLLED_BACK lines, split stable vs preview channel."""
    log = base / "deployment-evidence" / "tj-core-01" / "deploys.log"
    if not log.is_file():
        return {"name": "rollback_history", "status": "fail",
                "detail": "missing deploys.log: %s" % log}
    rows, errors = _parse_deploys_log(log)
    if errors:
        return {"name": "rollback_history", "status": "fail",
                "detail": "; ".join(errors[:5])}
    rolled = [r for r in rows if r.get("result") == "FAILED_ROLLED_BACK"]
    stable = [r for r in rolled if r.get("channel") == "prerelease"]
    preview = [r for r in rolled if str(r.get("channel", "")).startswith("preview-")]
    detail = "%d rollbacks total (%d stable, %d preview)" % (
        len(rolled), len(stable), len(preview))
    if not stable:
        return {"name": "rollback_history", "status": "fail",
                "detail": detail + "; GAP: stable-channel rollback never "
                          "exercised (only preview rollback on record)"}
    return {"name": "rollback_history", "status": "pass",
            "detail": detail}


def check_private_repo(base: Path) -> dict:
    """Read-only git status of the private checkout (never its content)."""
    repo = base / "projects" / "tianji-private-knowledge"
    if not (repo / ".git").exists():
        return {"name": "private_repo", "status": "fail",
                "detail": "private clone missing: %s" % repo}
    try:
        head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=30, check=False)
        status = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return {"name": "private_repo", "status": "skip",
                "detail": "git unavailable; checkout state not checked"}
    if head.returncode != 0 or status.returncode != 0:
        return {"name": "private_repo", "status": "fail",
                "detail": "git rev-parse/status failed"}
    dirty = [line for line in status.stdout.splitlines() if line.strip()]
    detail = "HEAD %s" % head.stdout.strip()[:12]
    if dirty:
        return {"name": "private_repo", "status": "fail",
                "detail": detail + "; GAP: %d uncommitted/untracked entries "
                          "(live tree differs from committed HEAD; the "
                          "pinned snapshot, not the git HEAD, is the "
                          "deploy input)" % len(dirty)}
    return {"name": "private_repo", "status": "pass",
            "detail": detail + "; working tree clean"}


def check_disk(base: Path, min_root_gb: int, min_data_gb: int) -> dict:
    """Free space vs the deploy agent's thresholds (root, data)."""
    try:
        root_free = shutil.disk_usage("/").free
        data_free = shutil.disk_usage(str(base)).free
    except OSError as exc:
        return {"name": "disk", "status": "fail",
                "detail": "disk usage unreadable: %s" % type(exc).__name__}
    root_gb = root_free / (1024 ** 3)
    data_gb = data_free / (1024 ** 3)
    detail = "/ free %.1f GiB (need >= %d), data free %.1f GiB (need >= %d)" % (
        root_gb, min_root_gb, data_gb, min_data_gb)
    if root_gb < min_root_gb or data_gb < min_data_gb:
        return {"name": "disk", "status": "fail", "detail": detail}
    return {"name": "disk", "status": "pass", "detail": detail}


def check_timer() -> dict:
    """Deploy timer state (skipped where systemctl is unavailable)."""
    if shutil.which("systemctl") is None:
        return {"name": "deploy_timer", "status": "skip",
                "detail": "systemctl unavailable; timer state not checked"}
    try:
        out = subprocess.run(
            ["systemctl", "is-active", "tianji-deploy-agent.timer"],
            capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return {"name": "deploy_timer", "status": "skip",
                "detail": "systemctl call failed; timer state not checked"}
    state = out.stdout.strip()
    if state != "active":
        return {"name": "deploy_timer", "status": "fail",
                "detail": "tianji-deploy-agent.timer is %r, not active" % state}
    return {"name": "deploy_timer", "status": "pass",
            "detail": "tianji-deploy-agent.timer active"}


def check_admin_db(base: Path) -> dict:
    """The audit-DB bind-mount target the agent generates the override for."""
    target = base / "data" / "tianji-admin" / "tianji_admin.db"
    if not target.is_file():
        return {"name": "admin_db", "status": "fail",
                "detail": "missing audit DB target: %s" % target}
    return {"name": "admin_db", "status": "pass",
            "detail": "audit DB present (%d bytes)" % target.stat().st_size}


def check_off_machine_backup(base: Path) -> dict:
    """Off-machine backup is a gap until an operator records one.

    Expected record: cicd/env/off-machine-backup.json with "target" and
    "last_verified" (ISO date). B002 is frozen pending user authorization,
    so this check reports the gap until that authorization lands.
    """
    record = base / "cicd" / "env" / "off-machine-backup.json"
    if not record.is_file():
        return {"name": "off_machine_backup", "status": "fail",
                "detail": "GAP: no off-machine backup recorded "
                          "(cicd/env/off-machine-backup.json absent; "
                          "B002 frozen pending user authorization)"}
    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"name": "off_machine_backup", "status": "fail",
                "detail": "off-machine backup record unreadable"}
    if not isinstance(data, dict) or not data.get("target") \
            or not data.get("last_verified"):
        return {"name": "off_machine_backup", "status": "fail",
                "detail": "off-machine backup record lacks target/last_verified"}
    return {"name": "off_machine_backup", "status": "pass",
            "detail": "recorded target %s, last verified %s"
                      % (data["target"], data["last_verified"])}


def verify(base: Path, full: bool = False,
           min_root_gb: int = MIN_FREE_ROOT_GB,
           min_data_gb: int = MIN_FREE_DATA_GB) -> dict:
    """Run every check. Returns {"checks": [...], "gaps": [...]}."""
    if not base.is_dir():
        return {"checks": [], "gaps": ["base dir missing: %s" % base],
                "error": "base dir missing: %s" % base}
    checks = [
        check_snapshot(base, full),
        check_rotation_backups(base),
        check_deploys_log(base),
        check_image_pairs(base),
        check_rollback_history(base),
        check_private_repo(base),
        check_disk(base, min_root_gb, min_data_gb),
        check_timer(),
        check_admin_db(base),
        check_off_machine_backup(base),
    ]
    gaps = ["%s: %s" % (c["name"], c["detail"])
            for c in checks if c["status"] == "fail"]
    return {"checks": checks, "gaps": gaps}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only TJ-005.3 backup/rollback/health-state verification")
    parser.add_argument("--base", type=Path,
                        default=Path("/data/workspace/platform-deploy"),
                        help="Deployment base dir (default: %(default)s)")
    parser.add_argument("--full", action="store_true",
                        help="Re-hash every snapshot file (slower)")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON instead of a human summary")
    parser.add_argument("--min-root-gb", type=int, default=MIN_FREE_ROOT_GB)
    parser.add_argument("--min-data-gb", type=int, default=MIN_FREE_DATA_GB)
    args = parser.parse_args()
    result = verify(args.base, full=args.full,
                    min_root_gb=args.min_root_gb,
                    min_data_gb=args.min_data_gb)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for check in result["checks"]:
            print("[%s] %s: %s" % (
                check["status"].upper(), check["name"], check["detail"]))
        if result["gaps"]:
            print("GAPS (%d):" % len(result["gaps"]))
            for gap in result["gaps"]:
                print("  - %s" % gap)
        else:
            print("No gaps found.")
    if "error" in result:
        return 2
    return 1 if result["gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
