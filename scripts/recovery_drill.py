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
   manifest exactly is a FAIL. The scratch dir must be a new
   dedicated empty directory outside the deployment base (never the
   base itself, never inside it, never a symlink); a pre-existing
   restored dir is never deleted or overwritten. The source tree
   must contain no symlink, and every manifest path must be a safe
   relative path (data/<area>/...) -- traversal, absolute paths,
   and links are rejected before any copy.
2. rollback -- read the recorded state (current sha/api-image/
   web-image) and the previous healthy pair (the last stable-channel
   DEPLOYED pair before the current deploy row in deploys.log; the
   protected rollback pair when there is none). Preview-channel
   records are never eligible. When the recorded state SHA has no
   matching stable DEPLOYED row the drill fails closed instead of
   guessing. Reconstruct the exact env file the deploy agent writes
   on rollback (TIANJI_PRIVATE_API_IMAGE, TIANJI_PUBLIC_WEB_IMAGE,
   TIANJI_HOST_PORT), write it to scratch/rollback.env, and verify
   it parses back to the previous pair.
3. health_gate -- three separately reported sub-results: current
   production health (/health rag_ready + a real bazi execute probe
   against the currently-running service), rollback-pair
   availability (the rollback pair images are shown available), and
   actual post-rollback health (NOT performed by this drill: it
   requires an actual rollback with separate user authorization).
   A PASS here verifies current health and rollback-pair
   availability only; it must never be reported as a production
   rollback verification.
4. evidence -- write scratch/drill-evidence.json with the source
   SHA, the restored manifest fingerprint, per-step pass/fail,
   and timestamps.

Exit code: 0 = every step passed, 1 = at least one step failed,
2 = the base or scratch dir is unusable. A step that cannot run
(e.g. no rotation backup, docker unavailable) is a FAIL with a
precise reason, never silently skipped.
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
# The stable deploy channel (see scripts/backup_verification.py).
STABLE_CHANNEL = bv.STABLE_CHANNEL


def _validate_scratch(base: Path, scratch: Path) -> str | None:
    """Fail-closed scratch isolation. Returns an error, or None when safe.

    The scratch dir must be an absolute path outside the deployment
    base, not a symlink, and either new or an existing empty
    directory. It must never be the base itself, inside the base
    (which would put the restored copy on the live snapshot or a
    rotation backup), or contain the base. resolve() follows every
    symlink component that exists, so a scratch under a symlinked
    parent is caught here before anything is created or written.
    """
    if not scratch.is_absolute():
        return "scratch must be an absolute path: %s" % scratch
    if scratch.is_symlink():
        return "scratch is a symlink: %s" % scratch
    base_resolved = base.resolve()
    # resolve() (non-strict) resolves every symlink component that
    # exists, so a scratch under a symlinked parent is caught too.
    scratch_resolved = scratch.resolve()
    if (scratch_resolved == base_resolved
            or scratch_resolved.is_relative_to(base_resolved)
            or base_resolved.is_relative_to(scratch_resolved)):
        return ("scratch must be outside the deployment base: %s "
                "(resolves to %s, base is %s)"
                % (scratch, scratch_resolved, base_resolved))
    if scratch.exists():
        if not scratch.is_dir():
            return "scratch exists and is not a directory: %s" % scratch
        if any(scratch.iterdir()):
            return ("scratch is not empty; use a new dedicated empty "
                    "directory: %s" % scratch)
    return None


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
    if src.is_symlink():
        return _step("restore", "fail",
                     "source dir is a symlink: %s" % src)
    if not src.is_dir():
        return _step("restore", "fail", "source dir missing: %s" % src)
    manifest_path = src / MANIFEST_NAME
    if manifest_path.is_symlink():
        return _step("restore", "fail",
                     "source manifest is a symlink: %s" % manifest_path)
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
    # Reject any symlink in the source tree before copying: copytree
    # follows symlinks, so a linked file or dir would read content
    # from outside the snapshot into the restored tree.
    for node in sorted(src.rglob("*")):
        if node.is_symlink():
            return _step("restore", "fail",
                         "source tree contains a symlink: %s"
                         % node.relative_to(src))
    restored = scratch / "restored"
    if restored.is_symlink() or restored.exists():
        # Never delete or overwrite a pre-existing restored dir: the
        # scratch dir must be a new dedicated empty directory, and a
        # pre-existing restored tree may hold data the operator did
        # not ask us to destroy.
        return _step("restore", "fail",
                     "restored dir already exists in scratch; refusing to "
                     "overwrite or delete a pre-existing directory: %s"
                     % restored)
    try:
        shutil.copytree(src, restored)
    except OSError as exc:
        return _step("restore", "fail",
                     "copy to scratch failed: %s" % type(exc).__name__)
    # 1. The restored manifest file must be byte-identical.
    restored_manifest = restored / MANIFEST_NAME
    if restored_manifest.is_symlink():
        return _step("restore", "fail",
                     "restored manifest is a symlink after copy")
    if not restored_manifest.is_file():
        return _step("restore", "fail",
                     "restored manifest missing after copy")
    if _manifest_bytes(restored_manifest) != _manifest_bytes(manifest_path):
        return _step("restore", "fail",
                     "restored manifest bytes differ from source")
    # 2. Re-hash every restored file against the manifest. Each row path
    #    is re-validated here (defense in depth: the manifest was already
    #    validated, but a path is trusted only after this check).
    for row in manifest["files"]:
        try:
            bv._safe_manifest_path(row["path"])
        except ValueError:
            return _step("restore", "fail",
                         "unsafe manifest path: %r" % (row["path"],))
        target = restored / row["path"]
        if target.is_symlink():
            return _step("restore", "fail",
                         "restored file is a symlink: %s" % row["path"])
        if not target.is_file():
            return _step("restore", "fail",
                         "restored file missing: %s" % row["path"])
        if target.stat().st_size != row["bytes"]:
            return _step("restore", "fail",
                         "restored size mismatch: %s" % row["path"])
        if _hash(target) != row["sha256"]:
            return _step("restore", "fail",
                         "restored SHA256 mismatch: %s" % row["path"])
    # 3. Exact membership: the restored tree must contain exactly the
    #    manifested files (plus the manifest itself). An extra file means
    #    the source backup is not the manifest's backup, and a file
    #    count / SHA comparison alone cannot prove the source path.
    expected = {row["path"] for row in manifest["files"]}
    for node in sorted(restored.rglob("*")):
        if node.is_symlink():
            return _step("restore", "fail",
                         "restored tree contains a symlink: %s"
                         % node.relative_to(restored))
        if node.is_file():
            rel = node.relative_to(restored).as_posix()
            if rel == MANIFEST_NAME:
                continue
            if rel not in expected:
                return _step("restore", "fail",
                             "restored tree has unmanifested file: %s" % rel)
    detail = ("%s %s restored to scratch: %d files, %d bytes, "
              "manifest %s byte-identical, full re-hash OK"
              % (label, src.name, manifest["file_count"],
                 manifest["total_bytes"],
                 _hash(manifest_path)[:16]))
    return _step("restore", "pass", detail)


def _previous_deployed_pair(base: Path, current_sha: str) -> tuple[dict | None, str | None]:
    """The previous stable healthy pair, or (None, error).

    Returns (pair, None) with the last stable-channel (prerelease)
    DEPLOYED record BEFORE the current deploy row in log order, or
    (None, None) when there is no earlier stable pair (the caller
    then uses the protected rollback pair). Preview-channel records
    are never eligible: a newer preview DEPLOYED must not become the
    stable rollback pair. Returns (None, error) when the log parses
    but the recorded state SHA has no matching stable DEPLOYED row
    -- the state and the log disagree, so the previous pair cannot
    be determined and the drill fails closed rather than guessing.

    The api image is the entry's "image" field; the web image is
    the web=... token inside its "detail" field.
    """
    log = base / "deployment-evidence" / "tj-core-01" / "deploys.log"
    if not log.is_file():
        return None, None
    rows, errors = bv._parse_deploys_log(log)
    if errors:
        return None, None
    stable = [r for r in rows
              if r.get("result") == "DEPLOYED"
              and r.get("channel") == STABLE_CHANNEL]
    if not stable:
        return None, None
    if not current_sha:
        # No recorded current deploy: nothing to anchor on; the
        # protected rollback pair is the safe fallback.
        return None, None
    current_idx = None
    for i, row in enumerate(stable):
        if row.get("sha") == current_sha:
            current_idx = i  # last match wins: the most recent deploy of it
    if current_idx is None:
        return None, ("recorded state SHA %s has no matching stable "
                      "DEPLOYED row in deploys.log; refusing to guess the "
                      "previous pair (state/log mismatch)"
                      % current_sha[:12])
    if current_idx == 0:
        return None, None
    last = stable[current_idx - 1]
    api = last.get("image") or ""
    match = WEB_IMAGE_RE.search(str(last.get("detail") or ""))
    web = match.group(1) if match else ""
    if not api or not web:
        return None, None
    return {"sha": str(last.get("sha")), "api": api, "web": web,
            "ts": str(last.get("ts"))}, None


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
    pair, error = _previous_deployed_pair(base, current_sha)
    if error:
        return (_step("rollback", "fail", error), None)
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
    """Three separately reported sub-results; see the module docstring.

    1. current_production_health: the currently-running service answers
       /health with rag_ready true and the bazi execute probe returns
       "pillars".
    2. rollback_pair_availability: the rollback pair is shown available
       (docker: both pair images present in `docker images`; file: the
       recorded pair equals the rollback pair). The running images are
       reported alongside, but a service running the CURRENT pair is
       normal production state, not a failure.
    3. post_rollback_health: NOT performed by this drill. Verifying
       health after an actual rollback requires a real rollback with
       separate user authorization; a PASS here must never be reported
       as a production rollback verification.
    """
    base = api_url.rstrip("/")
    sub = {
        "current_production_health": {"status": "not_checked", "detail": ""},
        "rollback_pair_availability": {"status": "not_checked", "detail": ""},
        "post_rollback_health": {
            "status": "not_performed",
            "detail": ("Actual post-rollback health was not verified by "
                       "this drill; it requires an actual rollback with "
                       "separate user authorization.")},
    }

    def _fail(detail: str) -> dict:
        step = _step("health_gate", "fail", detail)
        step.update(sub)
        return step

    # 1. Current production health: /health rag_ready (poll, like the agent).
    rag_ready = False
    health_status = 0
    for _ in range(HEALTH_ATTEMPTS):
        health_status, body = _http_json(base + "/health", timeout=3)
        if isinstance(body, dict) and body.get("rag_ready") is True:
            rag_ready = True
            break
        time.sleep(HEALTH_INTERVAL_S)
    if not rag_ready:
        sub["current_production_health"] = {
            "status": "fail",
            "detail": "/health did not return rag_ready true (last HTTP %s)"
                      % health_status}
        return _fail("/health did not return rag_ready true "
                     "(last HTTP %s)" % health_status)
    # 2. Rollback pair availability. The image provider reports the
    #    RUNNING images (docker inspect, or a recorded file pair).
    api, web, note = _image_provider(image_provider)
    if api is None or web is None:
        sub["current_production_health"] = {
            "status": "pass", "detail": "/health rag_ready true"}
        sub["rollback_pair_availability"] = {
            "status": "fail",
            "detail": "image identity not verifiable: %s" % note}
        return _fail("image identity not verifiable: %s" % note)
    running = "%s, %s" % (api, web)
    on_rollback_pair = api == pair["api"] and web == pair["web"]
    if image_provider.startswith("file:"):
        # A recorded file pair is the only availability evidence this
        # provider offers: it establishes the rollback pair only when
        # the recorded pair IS the rollback pair.
        if not on_rollback_pair:
            sub["current_production_health"] = {
                "status": "pass", "detail": "/health rag_ready true"}
            sub["rollback_pair_availability"] = {
                "status": "fail",
                "detail": ("recorded running images (%s) != rollback pair "
                           "(%s, %s); rollback pair availability not "
                           "established by the recorded pair"
                           % (running, pair["api"], pair["web"]))}
            return _fail("recorded running images (%s) != rollback pair "
                         "(%s, %s); rollback pair availability not "
                         "established by the recorded pair"
                         % (running, pair["api"], pair["web"]))
        sub["rollback_pair_availability"] = {
            "status": "pass",
            "detail": ("recorded pair equals the rollback pair (%s); the "
                       "pair was available when recorded" % running)}
    else:
        # Docker: availability is the pair's presence in `docker images`,
        # independent of which pair is currently running.
        images = bv._docker_images()
        if images is None:
            sub["current_production_health"] = {
                "status": "pass", "detail": "/health rag_ready true"}
            sub["rollback_pair_availability"] = {
                "status": "fail",
                "detail": "docker images unavailable; rollback pair "
                          "availability cannot be verified"}
            return _fail("docker images unavailable; rollback pair "
                         "availability cannot be verified")
        missing = [img for img in (pair["api"], pair["web"])
                   if img not in images]
        if missing:
            sub["current_production_health"] = {
                "status": "pass", "detail": "/health rag_ready true"}
            sub["rollback_pair_availability"] = {
                "status": "fail",
                "detail": "rollback pair image not available in docker: %s"
                          % ", ".join(missing)}
            return _fail("rollback pair image not available in docker: %s"
                         % ", ".join(missing))
        sub["rollback_pair_availability"] = {
            "status": "pass",
            "detail": "both rollback pair images present in docker"}
    # 3. The bazi execute probe (part of current production health).
    status, body = _http_json(base + "/api/v1/public/execute",
                              payload=BAZI_PROBE, timeout=10)
    text = body if isinstance(body, str) else json.dumps(body or {})
    if status != 200 or '"pillars"' not in text:
        sub["current_production_health"] = {
            "status": "fail",
            "detail": "bazi execute probe failed (HTTP %s)" % status}
        return _fail("bazi execute probe failed (HTTP %s)" % status)
    sub["current_production_health"] = {
        "status": "pass",
        "detail": "/health rag_ready true; bazi execute returned pillars"}
    detail = ("/health rag_ready true; rollback pair available (%s); bazi "
              "execute returned pillars; running images (%s)%s the rollback "
              "pair (normal production state when they differ); "
              "post-rollback health NOT verified (requires an actual "
              "rollback with separate authorization) (image source: %s)"
              % (pair["api"], running,
                 " equal" if on_rollback_pair else " differ from", note))
    step = _step("health_gate", "pass", detail)
    step.update(sub)
    return step


def run_drill(base: Path, scratch: Path, source: str, api_url: str,
              image_provider: str) -> dict:
    """Run the drill. Returns the evidence dict (also written to disk)."""
    started = _now()
    if not base.is_dir():
        return {"result": "FAIL", "started_at": started,
                "finished_at": _now(),
                "error": "base dir missing: %s" % base, "steps": []}
    scratch_error = _validate_scratch(base, scratch)
    if scratch_error is not None:
        return {"result": "FAIL", "started_at": started,
                "finished_at": _now(),
                "error": scratch_error, "steps": []}
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
        health = _step("health_gate", "fail",
                       "skipped: rollback step did not produce a pair")
        health["current_production_health"] = {
            "status": "not_performed",
            "detail": "health gate skipped: rollback step did not produce a pair"}
        health["rollback_pair_availability"] = {
            "status": "not_performed",
            "detail": "health gate skipped: rollback step did not produce a pair"}
        health["post_rollback_health"] = {
            "status": "not_performed",
            "detail": ("Actual post-rollback health was not verified by "
                       "this drill; it requires an actual rollback with "
                       "separate user authorization.")}
        steps.append(health)
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
        # The three health sub-results, reported separately (see
        # step_health_gate): a PASS verifies current production health
        # and rollback-pair availability only, never an actual
        # production rollback.
        "current_production_health": health.get(
            "current_production_health",
            {"status": "not_performed", "detail": ""}),
        "rollback_pair_availability": health.get(
            "rollback_pair_availability",
            {"status": "not_performed", "detail": ""}),
        "post_rollback_health": health.get(
            "post_rollback_health",
            {"status": "not_performed",
             "detail": ("Actual post-rollback health was not verified by "
                        "this drill; it requires an actual rollback with "
                        "separate user authorization.")}),
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
