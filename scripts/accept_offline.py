#!/usr/bin/env python3
"""Offline controlled acceptance — independent of private GitHub Actions.

Runs the FULL product acceptance using:
- A public code checkout at an exact pinned SHA
- A controlled knowledge snapshot (NOT in Git, on a trusted machine)

Reuses ONLY public scripts:
- scripts/private_data_snapshot.py (verify_private_data, stage_private_data)
- scripts/assemble_private_backend.py (assemble_private_backend)

Safe orchestration logic (public-checkout verification, test partitioning,
evidence recording) is implemented here. No private knowledge, credentials,
or private-repo scripts are used or copied.

TOOL VERSION: 3 (2026-10-22) — independent of private GitHub Actions.

Usage (on a trusted machine):
    python scripts/accept_offline.py \
        --public-code /path/to/tianji-knowledge-base \
        --expected-sha <40-char SHA> \
        --knowledge-snapshot /secure/tianji-knowledge \
        --trusted-manifest-sha256 <64-char SHA> \
        --suite all

Exit 0 on success, non-zero on any failure. Never writes PASS without running.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "3"
TOOL_DATE = "2026-10-22"

# Test modules that MUST run on the real public Git checkout.
GIT_CHECKOUT_TESTS = ("test_public_asset_changes", "test_public_knowledge_boundary")
# Deploy/static config tests that need deploy/ and web/.
# These RUN on the public checkout (not skipped), in a separate phase.
PUBLIC_ONLY_TESTS = ("test_deploy_config", "test_frontend_hygiene",
                     "test_offline_acceptance")

TRUSTED_ORIGINS = {
    "https://github.com/HelloMrDuan/tianji-knowledge-base",
    "https://github.com/HelloMrDuan/tianji-knowledge-base.git",
    "git@github.com:HelloMrDuan/tianji-knowledge-base.git",
}

# Public code integrity: these paths must be clean (no unreviewed changes).
# Includes deploy/, web/, workflows, and the acceptance scope itself.
INTEGRITY_PATHS = ("config", "src", "scripts", "tests", "schemas", "evals",
                   "docs", "deploy", "web", ".github/workflows", "pyproject.toml")


def _run(argv: list[str], *, cwd: Path, env: dict[str, str] | None = None,
         capture: bool = False) -> subprocess.CompletedProcess:
    """Fixed argv only; never a shell; caller-supplied commands never executed."""
    return subprocess.run(argv, cwd=cwd, env=env, check=True,
                          capture_output=capture, text=True)


def _check_path_safety(raw: Path, label: str) -> Path:
    """Validate a user-provided path BEFORE resolve().

    Rejects: symlinks (at the path itself), non-absolute paths.
    Returns the unresolved Path if safe.
    """
    if not raw.is_absolute():
        raise ValueError(f"{label} must be an absolute path: {raw}")
    # Check symlink BEFORE resolve() — resolve() would follow it silently.
    if raw.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {raw}")
    if not raw.exists():
        raise ValueError(f"{label} does not exist: {raw}")
    return raw


def _check_not_in_git_workspace(path: Path, label: str) -> None:
    """Reject paths inside a Git working tree (before resolve)."""
    # Walk up checking for .git (do not resolve symlinks yet).
    current = path
    for _ in range(32):  # bound the walk
        git_dir = current / ".git"
        # Use lexists-style check without following the path's own symlinks.
        try:
            if git_dir.exists() or os.path.islink(str(git_dir)):
                raise ValueError(
                    f"{label} must not be inside a Git workspace: {path}")
        except OSError:
            pass
        parent = current.parent
        if parent == current:
            break
        current = parent


def _assert_public_checkout(code: Path, expected_sha: str) -> str:
    """Verify public checkout pristine at exact SHA. Returns tool+code record."""
    _check_path_safety(code, "Public code checkout")
    _check_not_in_git_workspace(code.parent, "Public code parent")
    code = code.resolve(strict=True)
    if (code / "data").exists() or (code / "data").is_symlink():
        raise ValueError("Public code checkout must not contain private data")
    if len(expected_sha) != 40 or any(c not in "0123456789abcdef" for c in expected_sha):
        raise ValueError("Expected exact 40-character public commit SHA")
    origin = subprocess.check_output(
        ["git", "-C", str(code), "remote", "get-url", "origin"], text=True).strip()
    if origin not in TRUSTED_ORIGINS:
        raise ValueError("Only the owner's public repository is accepted")
    observed = subprocess.check_output(
        ["git", "-C", str(code), "rev-parse", "HEAD"], text=True).strip()
    if observed != expected_sha:
        raise ValueError("Public code checkout does not match expected pinned SHA")
    # Integrity: no unreviewed changes in code, deploy, web, workflows, docs.
    changes = subprocess.check_output(
        ["git", "-C", str(code), "status", "--porcelain",
         "--untracked-files=all", "--", *INTEGRITY_PATHS], text=True).strip()
    if changes:
        raise ValueError(
            f"Public checkout has unreviewed changes in {INTEGRITY_PATHS}:\n{changes[:500]}")
    # Record the acceptance tool's own version (prevent running unaudited script).
    tool_path = code / "scripts" / "accept_offline.py"
    tool_sha = hashlib.sha256(tool_path.read_bytes()).hexdigest() if tool_path.is_file() else "missing"
    print(f"public checkout verified: {observed} (pristine, {', '.join(INTEGRITY_PATHS)} clean)")
    print(f"acceptance tool: version {TOOL_VERSION} ({TOOL_DATE}), sha256={tool_sha[:16]}...")
    return tool_sha


def _partition_tests(code: Path) -> tuple[list[str], list[str], list[str]]:
    """Partition ALL discovered modules. Every test_*.py gets an execution location.

    Returns (git_modules, public_only_modules, backend_modules).
    - git_modules: run on real public Git checkout (assert repo state).
    - public_only_modules: RUN on real public checkout (need deploy//web/).
    - backend_modules: run in assembled private backend.
    """
    test_dir = code / "tests"
    discovered = {p.stem for p in test_dir.glob("test_*.py") if p.is_file()}
    git_modules = sorted(set(GIT_CHECKOUT_TESTS))
    if not set(git_modules) <= discovered:
        raise ValueError("Required public Git-checkout tests are missing")
    public_only = sorted(set(PUBLIC_ONLY_TESTS) & discovered)
    # PUBLIC_ONLY_TESTS listed but not found is a configuration error.
    missing_public = set(PUBLIC_ONLY_TESTS) - discovered
    if missing_public:
        raise ValueError(f"Declared public-only tests missing: {sorted(missing_public)}")
    backend_modules = sorted(discovered - set(git_modules) - set(public_only))
    total = len(git_modules) + len(public_only) + len(backend_modules)
    if not backend_modules or total != len(discovered):
        raise ValueError(f"Test partition incomplete: {len(discovered)} discovered, "
                         f"{total} partitioned")
    print(f"test partition: {len(discovered)} modules "
          f"(git-checkout={len(git_modules)}, public-only={len(public_only)}, "
          f"backend={len(backend_modules)})")
    print(f"  public-only (run on public checkout): {public_only}")
    return git_modules, public_only, backend_modules


def _verify_snapshot(snapshot: Path, trusted_manifest_sha256: str) -> dict:
    """Verify snapshot + bind to independent trusted manifest SHA256.

    The snapshot's own manifest is verified for internal consistency AND
    its SHA256 must match the independently-provided trusted value.
    This prevents a forged snapshot+manifest pair from passing.
    """
    _check_path_safety(snapshot, "Knowledge snapshot")
    _check_not_in_git_workspace(snapshot, "Knowledge snapshot")
    snapshot = snapshot.resolve(strict=True)
    if not snapshot.is_dir():
        raise ValueError("Knowledge snapshot is not a directory")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from scripts.private_data_snapshot import verify_private_data
        manifest = verify_private_data(snapshot)
    finally:
        sys.path.remove(str(Path(__file__).resolve().parents[1]))
    # Independent binding: manifest SHA256 must match the trusted value.
    manifest_path = snapshot / "private-data-manifest.json"
    actual_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if not trusted_manifest_sha256 or len(trusted_manifest_sha256) != 64:
        raise ValueError("trusted-manifest-sha256 must be a 64-char hex SHA256")
    if actual_sha != trusted_manifest_sha256.lower():
        raise ValueError(
            f"Snapshot manifest does not match trusted manifest SHA256 "
            f"(expected {trusted_manifest_sha256[:16]}..., got {actual_sha[:16]}...)")
    # Note: 235 is the TOTAL data-file count in the current manifest,
    # not "235 Canonical files". Report accurately.
    print(f"knowledge snapshot verified: {manifest['file_count']} total data files, "
          f"{manifest['total_bytes']} bytes, manifest bound to trusted SHA256")
    return manifest


def _run_unittest_modules(modules: list[str], cwd: Path, env: dict,
                          label: str) -> dict:
    """Run unittest modules, parse results accurately (not just exit code).

    Returns {modules, tests_run, failures, errors, skipped}.
    """
    result = _run([sys.executable, "-m", "unittest", "-v", *modules],
                  cwd=cwd, env=env, capture=True)
    output = result.stdout + result.stderr
    # Parse unittest -v output for accurate counts.
    tests_run = failures = errors = skipped = 0
    for line in output.splitlines():
        if line.startswith("Ran "):
            try:
                tests_run = int(line.split()[1])
            except (IndexError, ValueError):
                pass
        elif line.startswith("OK"):
            pass
        elif line.startswith("FAILED"):
            # e.g. "FAILED (failures=2, errors=1, skipped=1)"
            import re
            m = re.search(r"failures=(\d+)", line)
            if m: failures = int(m.group(1))
            m = re.search(r"errors=(\d+)", line)
            if m: errors = int(m.group(1))
            m = re.search(r"skipped=(\d+)", line)
            if m: skipped = int(m.group(1))
    # unittest -v prints "skipped" lines; also count them as a fallback.
    if "skipped" in output.lower() and skipped == 0:
        import re
        skipped = len(re.findall(r"\.\.\. skipped", output))
    report = {
        "label": label,
        "modules": modules,
        "module_count": len(modules),
        "tests_run": tests_run,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }
    print(f"{label}: {tests_run} tests, {failures} failures, "
          f"{errors} errors, {skipped} skipped ({len(modules)} modules)")
    return report


def run_offline_acceptance(public_code: Path, expected_sha: str,
                           snapshot: Path, trusted_manifest_sha256: str,
                           suite: str) -> dict:
    public_code = _check_path_safety(public_code, "Public code")
    snapshot = _check_path_safety(snapshot, "Knowledge snapshot")
    if snapshot.is_relative_to(public_code) or public_code.is_relative_to(snapshot):
        raise ValueError("Snapshot and public code must be separate directories")

    timestamp = datetime.now(timezone.utc).isoformat()
    hostname = platform.node()

    # 1. Public checkout integrity (incl. deploy/, web/, workflows).
    tool_sha = _assert_public_checkout(public_code, expected_sha)
    public_code = public_code.resolve(strict=True)

    # 2. Knowledge snapshot + trusted manifest binding.
    manifest = _verify_snapshot(snapshot, trusted_manifest_sha256)
    snapshot = snapshot.resolve(strict=True)

    # 3. Partition ALL tests with explicit execution locations.
    git_modules, public_only_modules, backend_modules = _partition_tests(public_code)

    public_env = dict(os.environ)
    public_env["PYTHONPATH"] = os.pathsep.join(
        (str(public_code / "src"), str(public_code / "tests")))

    reports = []

    # 4. Run Git-checkout tests on the REAL public checkout.
    reports.append(_run_unittest_modules(
        git_modules, public_code, public_env, "public-git-checkout"))

    # 5. Run PUBLIC_ONLY tests on the REAL public checkout (not skipped).
    reports.append(_run_unittest_modules(
        public_only_modules, public_code, public_env, "public-only"))

    # 6. Assemble ephemeral backend OUTSIDE any Git checkout.
    temp_base = Path(tempfile.gettempdir()).resolve(strict=True)
    _check_not_in_git_workspace(temp_base, "Temp base")
    with tempfile.TemporaryDirectory(prefix="tianji-offline-", dir=temp_base) as tmp:
        stage = Path(tmp)
        stage.chmod(0o700)
        sys.path.insert(0, str(public_code))
        try:
            from scripts.assemble_private_backend import assemble_private_backend
            assembled = stage / "backend"
            details = assemble_private_backend(public_code, snapshot, assembled)
        finally:
            sys.path.remove(str(public_code))
        if details["knowledge_files"] != manifest["file_count"]:
            raise ValueError("Assembled knowledge count differs from manifest")

        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            (str(assembled / "src"), str(assembled / "tests")))
        for script in ("scripts/validate_kb.py", "scripts/validate_knowledge.py",
                       "scripts/build_production_runtime.py",
                       "scripts/validate_phase2.py"):
            _run([sys.executable, script], cwd=assembled, env=env)
        _run([sys.executable, "scripts/build_product_coverage.py"],
             cwd=assembled, env=env)
        _run([sys.executable, "scripts/build_product_coverage.py", "--check"],
             cwd=assembled, env=env)
        print("knowledge validation, runtime build, Phase4 freeze: PASS")

        # 7. Run ALL backend tests (no silent drops).
        reports.append(_run_unittest_modules(
            backend_modules, assembled, env, "private-backend"))

    total_failures = sum(r["failures"] for r in reports)
    total_errors = sum(r["errors"] for r in reports)
    if total_failures or total_errors:
        raise ValueError(
            f"Acceptance failed: {total_failures} failures, "
            f"{total_errors} errors across {len(reports)} phases")

    evidence = {
        "mode": "offline-controlled",
        "tool_version": TOOL_VERSION,
        "tool_sha256": tool_sha,
        "tool_date": TOOL_DATE,
        "timestamp": timestamp,
        "hostname": hostname,
        "public_sha": expected_sha,
        "knowledge_manifest_sha256": trusted_manifest_sha256,
        "knowledge_file_count": manifest["file_count"],
        "knowledge_total_bytes": manifest["total_bytes"],
        "suite": suite,
        "test_reports": reports,
        "total_tests_run": sum(r["tests_run"] for r in reports),
        "total_skipped": sum(r["skipped"] for r in reports),
        "result": "SUCCESS",
    }
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline controlled acceptance (no private GitHub Actions)")
    parser.add_argument("--public-code", type=Path, required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--knowledge-snapshot", type=Path, required=True)
    parser.add_argument("--trusted-manifest-sha256", required=True,
                        help="Independently-known SHA256 of private-data-manifest.json")
    parser.add_argument("--suite", default="all", choices=["all"])
    args = parser.parse_args()

    try:
        evidence = run_offline_acceptance(
            args.public_code, args.expected_sha,
            args.knowledge_snapshot, args.trusted_manifest_sha256, args.suite)
    except Exception as exc:
        print(f"\nOFFLINE ACCEPTANCE FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 60)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("=" * 60)
    print("\nOFFLINE ACCEPTANCE SUCCESSFUL")
    print("NOTE: This is NOT a GitHub Actions run. Do not report it as such.")


if __name__ == "__main__":
    main()
