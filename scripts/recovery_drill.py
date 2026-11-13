#!/usr/bin/env python3
"""TJ-005.1/TJ-005.3: executable backup-restore + stable-rollback drill.

Runs a recovery drill against a deployment base (default
/data/workspace/platform-deploy) into a scratch dir, and writes
machine-readable drill evidence (JSON). The drill NEVER deploys,
never touches the live service, and never writes outside the
scratch dir: it copies a backup, re-hashes it, reconstructs the
rollback env file the deploy agent would write, and evaluates the
deploy agent's health gate against a service endpoint.

Steps:
1. restore -- copy the newest rotation backup (or the live snapshot
   with --source live) into scratch/restored, re-hash every file,
   and verify the restored manifest is byte-identical to the source
   manifest (manifest file bytes, file_count, total_bytes, and
   every file's SHA256). A restore that does not reproduce the
   manifest exactly is a FAIL.
2. rollback -- read the recorded state (current sha/api-image/
   web-image) and the previous healthy pair (the last DEPLOYED pair
   in deploys.log before the current SHA; the protected rollback
   pair when there is none), reconstruct the exact env file the
   deploy agent writes on rollback (TIANJI_PRIVATE_API_IMAGE,
   TIANJI_PUBLIC_WEB_IMAGE, TIANJI_HOST_PORT), write it to
   scratch/rollback.env, and verify it parses back to the
   previous pair.
3. health_gate -- evaluate the deploy agent's gate against a
   service endpoint: /health must return rag_ready true; the
   running images (from the image provider) must equal the
   rollback pair; a real bazi execute probe must return
   "pillars". The image provider defaults to docker inspect on
   the stable container names; --image-provider file:<path>
   reads a recorded {"api": ..., "web": ...} pair instead
   (for a drill against a stub service). --api-url overrides
   the service endpoint (default http://127.0.0.1:8080).
4. evidence -- write scratch/drill-evidence.json with the source
   SHA, the restored manifest fingerprint, per-step pass/fail,
   and timestamps.

Exit code: 0 = every step passed, 1 = at least one step failed,
2 = the base or scratch dir is unusable. A step that cannot run
(e.g. no rotation backup, docker unavailable) is a FAIL with a
precise reason, never silently skipped -- except the health gate's
image-identity sub-check, which is reported as "skip" only when
an explicit --image-provider file is used AND the file is absent
(the drill then verifies the env file + /health + execute probe,
and records the image check as not-verified).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import backup_verification as bv

MANIFEST_NAME = "private-data-manifest.json"
PROTECTED_API = bv.PROTECTED_API
PROTECTED_WEB = bv.PROTECTED_WEB
DEFAULT_API_URL = "http://127.0.0.1:8080"
# The deploy agent's health gate polls /health up to 40 x 2s.
HEALTH_ATTEMPTS = 40
HEALTH_INTERVAL_S = 2.0
# The deploy agent's bazi business probe (a real execute call whose
# response must contain "pillars").
BAZI_PROBE = {
    "domain": "bazi",
    "input": {"year_ganzhi": "庚午", "month_ganzhi": "壬午",
              "day_ganzhi": "甲子", "hour_ganzhi": "甲子"},
}
WEB_IMAGE_RE = re.compile(r"web=([^\s;]+)")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _hash(path: Path) -> str:
    return bv._hash(path)


def _step(name: str, status: str, detail: str) -> dict:
    return {"name": name, "status": status, "detail": detail,
            "at": _now()}


def _newest_rotation_backup(base: Path) -> Path | None:
    secure = base / "secure"
    if not secure.is_dir():
        return None
    backups = sorted(p for p in secure.iterdir()
                     if p.is_dir() and p.name.startswith("tianji-knowledge-pre-"))
    return backups[-1] if backups else None


def _manifest_bytes(manifest_path: Path) -> bytes:
    return manifest_path.read_bytes()


def step_restore(base: Path, scratch: Path, source: str) -> dict:
    """Copy a backup to scratch and prove it restores byte-identical."""
    if source == "live":
        src = base / "secure" / "tianji-knowledge"
        label = "live snapshot"
    else:
        src = _newest_rotation_backup(base)
        label = "newest rotation backup"
        if src is None:
            return _step("restore", "fail",
                         "no tianji-knowledge-pre-* backup dir found")
    if not src.is_dir():
        return _step("restore", "fail", "source dir missing: %s" % src)
    manifest_path = src / MANIFEST_NAME
    if not manifest_path.is_file():
        return _step("restore", "fail",
                     "source manifest missing: %s" % manifest_path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _step("restore", "fail", "source manifest unreadable")
    error = bv._manifest_self_consistent(manifest)
    if error:
        return _step("restore", "fail",
                     "source manifest not self-consistent: %s" % error)
    restored = scratch / "restored"
    if restored.exists():
        shutil.rmtree(restored)
    try:
        shutil.copytree(src, restored)
    except OSError as exc:
        return _step("restore", "fail",
                     "copy to scratch failed: %s" % type(exc).__name__)
    # 1. The restored manifest file must be byte-identical.
    restored_manifest = restored / MANIFEST_NAME
    if not restored_manifest.is_file():
        return _step("restore", "fail",
                     "restored manifest missing after copy")
    if _manifest_bytes(restored_manifest) != _manifest_bytes(manifest_path):
        return _step("restore", "fail",
                     "restored manifest bytes differ from source")
    # 2. Re-hash every restored file against the manifest.
    for row in manifest["files"]:
        target = restored / row["path"]
        if not target.is_file():
            return _step("restore", "fail",
                         "restored file missing: %s" % row["path"])
        if target.stat().st_size != row["bytes"]:
            return _step("restore", "fail",
                         "restored size mismatch: %s" % row["path"])
        if _hash(target) != row["sha256"]:
            return _step("restore", "fail",
                         "restored SHA256 mismatch: %s" % row["path"])
    detail = ("%s %s restored to scratch: %d files, %d bytes, "
              "manifest %s byte-identical, full re-hash OK"
              % (label, src.name, manifest["file_count"],
                 manifest["total_bytes"],
                 _hash(manifest_path)[:16]))
    return _step("restore", "pass", detail)


def _previous_deployed_pair(base: Path, current_sha: str) -> dict | None:
    """The last DEPLOYED pair before the current SHA, or None.

    The api image is the entry's "image" field; the web image is
    the web=... token inside its "detail" field.
    """
    log = base / "deployment-evidence" / "tj-core-01" / "deploys.log"
    if not log.is_file():
        return None
    rows, errors = bv._parse_deploys_log(log)
    if errors:
        return None
    deployed = [r for r in rows if r.get("result") == "DEPLOYED"]
    earlier = [r for r in deployed if r.get("sha") != current_sha]
    if not earlier:
        return None
    last = earlier[-1]
    api = last.get("image") or ""
    match = WEB_IMAGE_RE.search(str(last.get("detail") or ""))
    web = match.group(1) if match else ""
    if not api or not web:
        return None
    return {"sha": str(last.get("sha")), "api": api, "web": web,
            "ts": str(last.get("ts"))}


def step_rollback(base: Path, scratch: Path) -> tuple[dict, dict | None]:
    """Reconstruct the rollback env file the deploy agent writes.

    Returns (step, pair). The pair is the previous healthy pair the
    rollback would restore (or the protected rollback pair).
    """
    state = base / "cicd" / "state"
    current_sha = ""
    sha_path = state / "tianji-prerelease.sha"
    if sha_path.is_file():
        current_sha = sha_path.read_text(encoding="utf-8").strip()
    pair = _previous_deployed_pair(base, current_sha)
    if pair is None:
        pair = {"sha": "", "api": PROTECTED_API, "web": PROTECTED_WEB,
                "ts": "", "fallback": "protected rollback pair"}
    # The deploy agent's rollback writes exactly these three lines.
    env_text = ("TIANJI_PRIVATE_API_IMAGE=%s\n"
                "TIANJI_PUBLIC_WEB_IMAGE=%s\n"
                "TIANJI_HOST_PORT=8080\n" % (pair["api"], pair["web"]))
    env_path = scratch / "rollback.env"
    try:
        env_path.write_text(env_text, encoding="utf-8")
    except OSError as exc:
        return (_step("rollback", "fail",
                      "cannot write rollback env: %s" % type(exc).__name__),
                None)
    # Verify the written file parses back to the same pair.
    parsed = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            parsed[key.strip()] = value.strip()
    if (parsed.get("TIANJI_PRIVATE_API_IMAGE") != pair["api"]
            or parsed.get("TIANJI_PUBLIC_WEB_IMAGE") != pair["web"]
            or parsed.get("TIANJI_HOST_PORT") != "8080"):
        return (_step("rollback", "fail",
                      "rollback env does not parse back to the pair"),
                None)
    detail = ("rollback to %s (previous healthy pair): api %s, web %s; "
              "env file %s written and parses back"
              % (pair["sha"][:12] if pair.get("sha") else "protected pair",
                 pair["api"], pair["web"], env_path.name))
    return _step("rollback", "pass", detail), pair


def _docker_images_for_containers() -> tuple[str | None, str | None]:
    """Actual running images via docker inspect, or (None, None)."""
    if shutil.which("docker") is None:
        return None, None
    api = web = None
    for name, slot in (("tianji-tianji-api-1", "api"),
                       ("tianji-tianji-web-1", "web")):
        try:
            out = subprocess.run(
                ["docker", "inspect", name, "--format", "{{.Config.Image}}"],
                capture_output=True, text=True, timeout=30, check=False)
        except (OSError, subprocess.SubprocessError):
            return None, None
        if out.returncode != 0:
            return None, None
        image = out.stdout.strip()
        if slot == "api":
            api = image
        else:
            web = image
    return api, web


def _image_provider(spec: str) -> tuple[str | None, str | None, str]:
    """Resolve an image provider spec to (api, web, note).

    "docker" (default): docker inspect on the stable containers.
    "file:<path>": a recorded {"api": ..., "web": ...} JSON pair.
    """
    if spec == "docker":
        api, web = _docker_images_for_containers()
        if api is None or web is None:
            return None, None, "docker inspect unavailable or containers absent"
        return api, web, "docker inspect"
    if spec.startswith("file:"):
        path = Path(spec[5:])
        if not path.is_file():
            return None, None, "image-provider file missing: %s" % path
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None, None, "image-provider file unreadable"
        if not isinstance(data, dict) or not data.get("api") \
                or not data.get("web"):
            return None, None, "image-provider file lacks api/web"
        return data["api"], data["web"], "recorded pair from %s" % path.name
    return None, None, "unknown image-provider spec: %r" % spec


def _http_json(url: str, payload: dict | None = None,
               timeout: int = 10) -> tuple[int, dict | str | None]:
    """GET (payload None) or POST a JSON call. Returns (status, body)."""
    if payload is None:
        request = urllib.request.Request(url, method="GET")
    else:
        request = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(2 * 1024 * 1024 + 1)
            try:
                return response.status, json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return response.status, raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (OSError, ValueError):
        return 0, None


def step_health_gate(api_url: str, pair: dict,
                     image_provider: str) -> dict:
    """The deploy agent's gate: rag_ready + image identity + bazi probe."""
    base = api_url.rstrip("/")
    # 1. /health must return rag_ready true (poll, like the agent).
    rag_ready = False
    health_status = 0
    for _ in range(HEALTH_ATTEMPTS):
        health_status, body = _http_json(base + "/health", timeout=3)
        if isinstance(body, dict) and body.get("rag_ready") is True:
            rag_ready = True
            break
        time.sleep(HEALTH_INTERVAL_S)
    if not rag_ready:
        return _step("health_gate", "fail",
                     "/health did not return rag_ready true "
                     "(last HTTP %s)" % health_status)
    # 2. The running images must equal the rollback pair.
    api, web, note = _image_provider(image_provider)
    if api is None or web is None:
        return _step("health_gate", "fail",
                     "image identity not verifiable: %s" % note)
    if api != pair["api"] or web != pair["web"]:
        return _step("health_gate", "fail",
                     "running images (%s, %s) != rollback pair (%s, %s)"
                     % (api, web, pair["api"], pair["web"]))
    # 3. A real bazi execute probe must return "pillars".
    status, body = _http_json(base + "/api/v1/public/execute",
                              payload=BAZI_PROBE, timeout=10)
    text = body if isinstance(body, str) else json.dumps(body or {})
    if status != 200 or '"pillars"' not in text:
        return _step("health_gate", "fail",
                     "bazi execute probe failed (HTTP %s)" % status)
    return _step("health_gate", "pass",
                 "/health rag_ready true; running images match the "
                 "rollback pair (%s); bazi execute returned pillars "
                 "(image source: %s)" % (pair["api"], note))


def run_drill(base: Path, scratch: Path, source: str, api_url: str,
              image_provider: str) -> dict:
    """Run the drill. Returns the evidence dict (also written to disk)."""
    started = _now()
    if not base.is_dir():
        return {"result": "FAIL", "started_at": started,
                "finished_at": _now(),
                "error": "base dir missing: %s" % base, "steps": []}
    scratch.mkdir(parents=True, exist_ok=True)
    steps: list[dict] = []
    restore = step_restore(base, scratch, source)
    steps.append(restore)
    rollback, pair = step_rollback(base, scratch)
    steps.append(rollback)
    health = None
    if pair is not None and rollback["status"] == "pass":
        health = step_health_gate(api_url, pair, image_provider)
        steps.append(health)
    else:
        steps.append(_step("health_gate", "fail",
                           "skipped: rollback step did not produce a pair"))
    result = "PASS" if all(s["status"] == "pass" for s in steps) else "FAIL"
    evidence = {
        "drill": "recovery",
        "result": result,
        "started_at": started,
        "finished_at": _now(),
        "base": str(base),
        "scratch": str(scratch),
        "source": source,
        "api_url": api_url,
        "image_provider": image_provider,
        "steps": steps,
    }
    # Attach the restored manifest fingerprint and the rollback pair.
    restored_manifest = scratch / "restored" / MANIFEST_NAME
    if restored_manifest.is_file():
        evidence["restored_manifest_sha256"] = _hash(restored_manifest)
        try:
            manifest = json.loads(
                restored_manifest.read_text(encoding="utf-8"))
            evidence["restored_manifest"] = {
                "file_count": manifest.get("file_count"),
                "total_bytes": manifest.get("total_bytes"),
            }
        except (OSError, ValueError):
            pass
    if pair is not None:
        evidence["rollback_pair"] = {
            "sha": pair.get("sha"), "api": pair["api"], "web": pair["web"]}
    evidence_path = scratch / "drill-evidence.json"
    evidence_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TJ-005.1/TJ-005.3 recovery drill: restore a backup, "
                    "simulate a stable rollback, evaluate the health gate")
    parser.add_argument("--base", type=Path,
                        default=Path("/data/workspace/platform-deploy"),
                        help="Deployment base dir (default: %(default)s)")
    parser.add_argument("--scratch", type=Path, required=True,
                        help="Scratch dir for the restored copy + evidence "
                             "(created if missing; the live service is "
                             "never touched)")
    parser.add_argument("--source", choices=("backup", "live"),
                        default="backup",
                        help="Restore the newest rotation backup "
                             "(default) or the live snapshot")
    parser.add_argument("--api-url", default=DEFAULT_API_URL,
                        help="Service endpoint for the health gate "
                             "(default: %(default)s)")
    parser.add_argument("--image-provider", default="docker",
                        help="docker (default) or file:<path> with a "
                             "recorded {\"api\": ..., \"web\": ...} pair")
    parser.add_argument("--json", action="store_true",
                        help="Emit the evidence JSON instead of a summary")
    args = parser.parse_args()
    evidence = run_drill(args.base, args.scratch, args.source,
                         args.api_url, args.image_provider)
    if args.json:
        print(json.dumps(evidence, ensure_ascii=False, indent=2))
    else:
        for step in evidence.get("steps", []):
            print("[%s] %s: %s" % (step["status"].upper(), step["name"],
                                   step["detail"]))
        print("RESULT: %s (evidence: %s)"
              % (evidence["result"],
                 Path(args.scratch) / "drill-evidence.json"))
    if "error" in evidence:
        return 2
    return 0 if evidence["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
