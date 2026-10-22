#!/usr/bin/env python3
"""Offline controlled acceptance — independent of private GitHub Actions.

Runs the FULL product acceptance using:
- A public code checkout at an exact pinned SHA
- A controlled knowledge snapshot (NOT in Git, on a trusted machine)

Reuses ONLY public scripts:
- scripts/private_data_snapshot.py (verify_private_data, stage_private_data)
- scripts/assemble_private_backend.py (assemble_private_backend)
- scripts/build_production_runtime.py, validate_kb.py, validate_knowledge.py,
  validate_phase2.py, build_product_coverage.py

Safe orchestration logic (public-checkout verification, test partitioning,
evidence recording) is implemented here. No private knowledge, credentials,
or private-repo scripts are used or copied.

Usage (on a trusted machine):
    python scripts/accept_offline.py \
        --public-code /path/to/tianji-knowledge-base \
        --expected-sha <40-char SHA> \
        --knowledge-snapshot /secure/tianji-knowledge \
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

# Test modules that MUST run on the real public Git checkout (they assert
# repository state). All other discovered modules run in the assembled backend.
GIT_CHECKOUT_TESTS = ("test_public_asset_changes", "test_public_knowledge_boundary")
# Deploy/static config tests that need deploy/ and web/ (public checkout only).
# They are verified in public CI, not in the assembled backend.
PUBLIC_ONLY_TESTS = ("test_deploy_config", "test_frontend_hygiene")

# Trusted origin for the public repository.
TRUSTED_ORIGINS = {
    "https://github.com/HelloMrDuan/tianji-knowledge-base",
    "https://github.com/HelloMrDuan/tianji-knowledge-base.git",
    "git@github.com:HelloMrDuan/tianji-knowledge-base.git",
}


def _run(argv: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    """Fixed argv only; never a shell; caller-supplied commands never executed."""
    subprocess.run(argv, cwd=cwd, env=env, check=True)


def _assert_public_checkout(code: Path, expected_sha: str) -> None:
    """Verify the public checkout is pristine and at the exact pinned SHA."""
    if code.is_symlink() or not code.is_dir():
        raise ValueError("Public code checkout is missing or unsafe")
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
    changes = subprocess.check_output(
        ["git", "-C", str(code), "status", "--porcelain", "--untracked-files=all",
         "--", "config", "src", "scripts", "tests", "schemas", "evals", "docs",
         "pyproject.toml"], text=True).strip()
    if changes:
        raise ValueError("Public code checkout has unreviewed local files or edits")
    print(f"public checkout verified: {observed} (pristine)")


def _partition_tests(code: Path) -> tuple[list[str], list[str], list[str]]:
    """Partition discovered test modules. Reject any dropped suite.

    Returns (git_modules, public_only_modules, backend_modules).
    - git_modules: must run on the real public Git checkout.
    - public_only_modules: need deploy//web/, run in public CI (not here).
    - backend_modules: run in the assembled private backend.
    Every discovered test_*.py must land in exactly one partition.
    """
    test_dir = code / "tests"
    discovered = {p.stem for p in test_dir.glob("test_*.py") if p.is_file()}
    git_modules = sorted(set(GIT_CHECKOUT_TESTS))
    if not set(git_modules) <= discovered:
        raise ValueError("Required public Git-checkout tests are missing")
    public_only = sorted(set(PUBLIC_ONLY_TESTS) & discovered)
    backend_modules = sorted(discovered - set(git_modules) - set(public_only))
    total = len(git_modules) + len(public_only) + len(backend_modules)
    if not backend_modules or total != len(discovered):
        raise ValueError(
            f"Test partition incomplete: {len(discovered)} discovered, "
            f"{total} partitioned (git={len(git_modules)}, "
            f"public-only={len(public_only)}, backend={len(backend_modules)})")
    print(f"test partition: {len(discovered)} modules "
          f"(git={len(git_modules)}, public-only={len(public_only)} [public CI], "
          f"backend={len(backend_modules)})")
    return git_modules, public_only, backend_modules


def _verify_snapshot(snapshot: Path) -> dict:
    """Verify the knowledge snapshot using the public snapshot verifier.

    Rejects: missing/extra files, symlinks, path traversal, bad manifest,
    SHA256/size mismatches. Fail-closed on anything unexpected.
    """
    if not snapshot.is_absolute() or snapshot.is_symlink():
        raise ValueError("Knowledge snapshot must be an absolute real directory")
    snapshot = snapshot.resolve(strict=True)
    if (snapshot / ".git").exists():
        raise ValueError("Knowledge snapshot must not be inside a Git repository")
    # Import the public verifier (no private code involved).
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from scripts.private_data_snapshot import verify_private_data
        manifest = verify_private_data(snapshot)
    finally:
        sys.path.remove(str(Path(__file__).resolve().parents[1]))
    # 235 is the TOTAL data-file count in the current manifest, not "235 Canonical".
    print(f"knowledge snapshot verified: {manifest['file_count']} data files, "
          f"{manifest['total_bytes']} bytes")
    return manifest


def run_offline_acceptance(public_code: Path, expected_sha: str,
                           snapshot: Path, suite: str) -> dict:
    """Run the full offline acceptance. Returns the evidence record."""
    public_code = public_code.resolve(strict=True)
    snapshot = snapshot.resolve(strict=True)
    if snapshot.is_relative_to(public_code) or public_code.is_relative_to(snapshot):
        raise ValueError("Snapshot and public code must be separate directories")

    timestamp = datetime.now(timezone.utc).isoformat()
    hostname = platform.node()

    # 1. Verify public checkout (pristine, exact SHA, trusted origin).
    _assert_public_checkout(public_code, expected_sha)

    # 2. Verify knowledge snapshot (fail-closed on any tampering).
    manifest = _verify_snapshot(snapshot)
    manifest_sha = hashlib.sha256(
        (snapshot / "private-data-manifest.json").read_bytes()).hexdigest()

    # 3. Partition tests (reject dropped suites).
    git_modules, public_only, backend_modules = _partition_tests(public_code)

    # 4. Run Git-checkout tests on the real public checkout.
    public_env = dict(os.environ)
    public_env["PYTHONPATH"] = os.pathsep.join(
        (str(public_code / "src"), str(public_code / "tests")))
    _run([sys.executable, "-m", "unittest", "-v", *git_modules],
         cwd=public_code, env=public_env)
    print(f"public Git-checkout tests passed: {git_modules}")

    # 5. Assemble the ephemeral backend OUTSIDE any Git checkout.
    temp_base = Path(tempfile.gettempdir()).resolve(strict=True)
    if (temp_base / ".git").exists():
        raise ValueError("Temp base must not be inside a Git checkout")
    evidence_tests = []
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
        print(f"backend assembled: {details['knowledge_files']} files, "
              f"{details['code_files']} code files")

        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(
            (str(assembled / "src"), str(assembled / "tests")))
        # Rebuild derived data from the pinned code, check for drift.
        for script in ("scripts/validate_kb.py", "scripts/validate_knowledge.py",
                       "scripts/build_production_runtime.py",
                       "scripts/validate_phase2.py"):
            _run([sys.executable, script], cwd=assembled, env=env)
        _run([sys.executable, "scripts/build_product_coverage.py"],
             cwd=assembled, env=env)
        _run([sys.executable, "scripts/build_product_coverage.py", "--check"],
             cwd=assembled, env=env)
        print("knowledge validation, runtime build, Phase4 freeze: PASS")

        # 6. Run ALL backend tests. No silent drops, no fake skips.
        _run([sys.executable, "-m", "unittest", "-v", *backend_modules],
             cwd=assembled, env=env)
        evidence_tests = backend_modules
        print(f"backend tests passed: {len(backend_modules)} modules")

    evidence = {
        "mode": "offline-controlled",
        "timestamp": timestamp,
        "hostname": hostname,
        "public_sha": expected_sha,
        "knowledge_manifest_sha256": manifest_sha,
        "knowledge_file_count": manifest["file_count"],
        "knowledge_total_bytes": manifest["total_bytes"],
        "suite": suite,
        "git_checkout_modules": git_modules,
        "public_only_modules_skipped_here": public_only,
        "backend_modules": evidence_tests,
        "result": "SUCCESS",
    }
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline controlled acceptance (no private GitHub Actions)")
    parser.add_argument("--public-code", type=Path, required=True,
                        help="Absolute path to public repo checkout")
    parser.add_argument("--expected-sha", required=True,
                        help="Exact 40-char public commit SHA")
    parser.add_argument("--knowledge-snapshot", type=Path, required=True,
                        help="Absolute path to controlled knowledge snapshot")
    parser.add_argument("--suite", default="all", choices=["all"])
    args = parser.parse_args()

    try:
        evidence = run_offline_acceptance(
            args.public_code, args.expected_sha,
            args.knowledge_snapshot, args.suite)
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
