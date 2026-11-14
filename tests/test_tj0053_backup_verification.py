"""TJ-005.3: tests for scripts/backup_verification.py.

All fixtures are synthetic temp dirs: no machine, no sealed data, no
docker, no network. The script under test is read-only; one test proves
the fixture tree is byte-identical after a run.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import backup_verification as bv

HAVE_GIT = shutil.which("git") is not None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest(rows):
    return {
        "schema_version": "private-data-snapshot-v2",
        "areas": ["canonical"],
        "file_count": len(rows),
        "total_bytes": sum(r["bytes"] for r in rows),
        "files": rows,
    }


def _write_snapshot(root: Path, files: dict[str, bytes]) -> Path:
    """Create a snapshot dir with a valid manifest. Returns the dir."""
    root.mkdir(parents=True, exist_ok=True)
    rows = []
    for rel, data in sorted(files.items()):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({"path": rel, "bytes": len(data), "sha256": _sha(data)})
    (root / "private-data-manifest.json").write_text(
        json.dumps(_manifest(rows), indent=2), encoding="utf-8")
    return root


def _log_line(**fields):
    row = {"project": "tianji", "channel": "prerelease", "branch": "main",
           "sha": "a" * 40, "image": "", "port": "8080",
           "result": "DEPLOYED", "detail": "", "ts": "2026-11-12T00:00:00+00:00"}
    row.update(fields)
    return json.dumps(row, ensure_ascii=False)


class BackupVerificationFixture(unittest.TestCase):
    """Build a complete healthy fixture base dir."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tj0053-fixture-"))
        self.base = self.tmp / "platform-deploy"
        self._build_base()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build_base(self):
        # Live snapshot: 2 small files.
        snap = self.base / "secure" / "tianji-knowledge"
        _write_snapshot(snap, {
            "data/canonical/a.json": b'{"k": 1}',
            "data/canonical/b.json": b'{"k": 2}',
        })
        # Two rotation backups.
        for name in ("tianji-knowledge-pre-a", "tianji-knowledge-pre-b"):
            _write_snapshot(self.base / "secure" / name, {
                "data/canonical/a.json": b'{"k": 1}',
            })
        # Evidence + deploys.log: accepted + deployed + one stable rollback.
        evid = self.base / "deployment-evidence" / "tj-core-01"
        evid.mkdir(parents=True)
        sha_new = "b" * 40
        lines = [
            _log_line(sha="a" * 40, result="ACCEPTED",
                      ts="2026-11-12T00:00:00+00:00"),
            _log_line(sha="a" * 40, result="DEPLOYED", image="tianji-api:x",
                      detail="health+bazi ok", ts="2026-11-12T00:01:00+00:00"),
            _log_line(sha="c" * 40, result="FAILED_ROLLED_BACK",
                      channel="prerelease", image="tianji-api:y",
                      detail="gate failed; restored tianji-api:x",
                      ts="2026-11-12T00:02:00+00:00"),
            _log_line(sha=sha_new, result="ACCEPTED",
                      ts="2026-11-12T00:03:00+00:00"),
            _log_line(sha=sha_new, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-bbbb",
                      detail="health+bazi ok",
                      ts="2026-11-12T00:04:00+00:00"),
        ]
        (evid / "deploys.log").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8")
        # State files for the current pair.
        state = self.base / "cicd" / "state"
        state.mkdir(parents=True)
        (state / "tianji-prerelease.sha").write_text(sha_new, encoding="utf-8")
        (state / "tianji-prerelease.api-image").write_text(
            "tianji-api:cicd-prerelease-bbbb", encoding="utf-8")
        (state / "tianji-prerelease.web-image").write_text(
            "ghcr.io/hellomrduan/tianji-web:" + sha_new, encoding="utf-8")
        # Admin DB target.
        admin = self.base / "data" / "tianji-admin"
        admin.mkdir(parents=True)
        (admin / "tianji_admin.db").write_bytes(b"SQLite format 3\x00" + b"\x00" * 100)
        # Off-machine backup record.
        env = self.base / "cicd" / "env"
        env.mkdir(parents=True)
        (env / "off-machine-backup.json").write_text(
            json.dumps({"target": "operator-vault:tianji-2026-11-12",
                        "last_verified": "2026-11-12",
                        "method": "snapshot-copy"}), encoding="utf-8")
        # Private repo: real git repo, clean tree.
        self._init_private_repo(clean=True)

    def _init_private_repo(self, clean=True):
        repo = self.base / "projects" / "tianji-private-knowledge"
        repo.mkdir(parents=True)
        if not HAVE_GIT:
            return
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email",
                        "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name",
                        "test"], check=True)
        (repo / "README.md").write_text("private\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."],
                       check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"],
                       check=True)
        if not clean:
            (repo / "README.md").write_text("private dirty\n",
                                            encoding="utf-8")

    def _images(self):
        return {
            "tianji-api:cicd-prerelease-bbbb",
            "ghcr.io/hellomrduan/tianji-web:" + "b" * 40,
            "tianji-api:sealed-82b119e",
            "tianji-web:static-82b119e",
        }

    def _verify(self, **kwargs):
        # /tmp in this environment is a small filesystem (< 2 GiB free),
        # so pin disk_usage to a large fake; the threshold-fail path is
        # covered separately by test_disk_threshold_override_forces_gap.
        fake_disk = type("Usage", (), {"total": 200 * 1024 ** 3,
                                       "used": 100 * 1024 ** 3,
                                       "free": 100 * 1024 ** 3})()
        with patch.object(bv, "_docker_images", return_value=self._images()), \
                patch.object(bv.shutil, "disk_usage",
                             return_value=fake_disk), \
                patch.object(bv, "check_timer",
                             return_value={"name": "deploy_timer",
                                           "status": "pass",
                                           "detail": "timer active"}):
            return bv.verify(self.base, **kwargs)

    def _tree_fingerprint(self):
        out = []
        for path in sorted(self.base.rglob("*")):
            if path.is_file():
                out.append((str(path.relative_to(self.base)),
                            path.stat().st_size, _sha(path.read_bytes())))
        return out

    def test_happy_path_has_no_gaps(self):
        result = self._verify()
        self.assertEqual(result["gaps"], [], msg=json.dumps(result, indent=2))
        self.assertTrue(all(c["status"] in ("pass", "skip")
                            for c in result["checks"]))

    def test_verify_is_read_only(self):
        before = self._tree_fingerprint()
        self._verify(full=True)
        self.assertEqual(before, self._tree_fingerprint())

    def test_full_rehash_catches_corruption(self):
        target = (self.base / "secure" / "tianji-knowledge"
                  / "data" / "canonical" / "a.json")
        data = bytearray(target.read_bytes())
        data[0] ^= 0xFF
        target.write_bytes(bytes(data))
        # Size unchanged, so the fast check still passes...
        result = self._verify(full=False)
        self.assertEqual(
            [c for c in result["checks"] if c["name"] == "live_snapshot"][0]["status"],
            "pass")
        # ...but the full re-hash must fail.
        result = self._verify(full=True)
        failed = [c for c in result["checks"]
                  if c["name"] == "live_snapshot"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("SHA256 mismatch", failed["detail"])

    def test_missing_snapshot_manifest_is_a_gap(self):
        (self.base / "secure" / "tianji-knowledge"
         / "private-data-manifest.json").unlink()
        result = self._verify()
        self.assertIn("live_snapshot", " ".join(result["gaps"]))

    def test_manifest_totals_mismatch_is_a_gap(self):
        manifest_path = (self.base / "secure" / "tianji-knowledge"
                         / "private-data-manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["file_count"] = 99
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result = self._verify()
        self.assertIn("live_snapshot", " ".join(result["gaps"]))

    def test_no_rotation_backups_is_a_gap(self):
        shutil.rmtree(self.base / "secure" / "tianji-knowledge-pre-a")
        shutil.rmtree(self.base / "secure" / "tianji-knowledge-pre-b")
        result = self._verify()
        self.assertIn("rotation_backups", " ".join(result["gaps"]))

    def test_state_sha_mismatch_is_a_gap(self):
        (self.base / "cicd" / "state" / "tianji-prerelease.sha").write_text(
            "d" * 40, encoding="utf-8")
        result = self._verify()
        self.assertIn("deploys_log", " ".join(result["gaps"]))

    def test_stable_rollback_never_exercised_is_a_gap(self):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = [line for line in evid.read_text(encoding="utf-8").splitlines()
                 if "FAILED_ROLLED_BACK" not in line]
        lines.append(_log_line(sha="e" * 40, result="FAILED_ROLLED_BACK",
                               channel="preview-round1",
                               detail="preview rolled back"))
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self._verify()
        failed = [c for c in result["checks"]
                  if c["name"] == "rollback_history"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("stable-channel rollback never exercised",
                      failed["detail"])

    def test_missing_protected_pair_is_a_gap(self):
        images = self._images() - {"tianji-api:sealed-82b119e"}
        with patch.object(bv, "_docker_images", return_value=images), \
                patch.object(bv, "check_timer",
                             return_value={"name": "deploy_timer",
                                           "status": "pass", "detail": "ok"}):
            result = bv.verify(self.base)
        self.assertIn("image_pairs", " ".join(result["gaps"]))

    @unittest.skipUnless(HAVE_GIT, "git required for repo fixture")
    def test_dirty_private_repo_is_a_gap(self):
        repo = self.base / "projects" / "tianji-private-knowledge"
        (repo / "README.md").write_text("private dirty\n", encoding="utf-8")
        result = self._verify()
        failed = [c for c in result["checks"]
                  if c["name"] == "private_repo"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("live tree differs", failed["detail"])

    def test_missing_off_machine_backup_is_a_gap(self):
        (self.base / "cicd" / "env" / "off-machine-backup.json").unlink()
        result = self._verify()
        failed = [c for c in result["checks"]
                  if c["name"] == "off_machine_backup"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("B002", failed["detail"])

    def test_symlinked_manifested_file_is_a_gap(self):
        target = (self.base / "secure" / "tianji-knowledge"
                  / "data" / "canonical" / "a.json")
        outside = self.tmp / "outside.json"
        outside.write_bytes(b'{"k": 9}')
        target.unlink()
        os.symlink(outside, target)
        result = self._verify()
        failed = [c for c in result["checks"]
                  if c["name"] == "live_snapshot"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("symlink", failed["detail"])

    def test_deploys_log_ignores_preview_for_last_stable(self):
        # A newer preview DEPLOYED must not displace the last stable
        # DEPLOYED the recorded state is compared against.
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        sha_new = "b" * 40
        lines = evid.read_text(encoding="utf-8").splitlines()
        lines.append(_log_line(sha="c" * 40, result="DEPLOYED",
                               channel="preview-round1",
                               image="tianji-api:preview-c",
                               ts="2026-11-12T00:05:00+00:00"))
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self._verify()
        passed = [c for c in result["checks"]
                  if c["name"] == "deploys_log"][0]
        self.assertEqual(passed["status"], "pass")
        self.assertIn("last stable DEPLOYED %s" % sha_new[:12],
                      passed["detail"])

    def test_deploys_log_fails_when_only_preview_deployed(self):
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = [_log_line(sha="c" * 40, result="DEPLOYED",
                           channel="preview-round1",
                           image="tianji-api:preview-c",
                           ts="2026-11-12T00:05:00+00:00")]
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self._verify()
        failed = [c for c in result["checks"]
                  if c["name"] == "deploys_log"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("no stable", failed["detail"])

    def test_disk_threshold_override_forces_gap(self):
        result = self._verify(min_root_gb=10 ** 6, min_data_gb=10 ** 6)
        self.assertIn("disk", " ".join(result["gaps"]))

    def test_main_exit_codes(self):
        fake_disk = type("Usage", (), {"total": 200 * 1024 ** 3,
                                       "used": 100 * 1024 ** 3,
                                       "free": 100 * 1024 ** 3})()
        with patch.object(bv, "_docker_images",
                          return_value=self._images()), \
                patch.object(bv.shutil, "disk_usage",
                             return_value=fake_disk), \
                patch.object(bv, "check_timer",
                             return_value={"name": "deploy_timer",
                                           "status": "pass", "detail": "ok"}), \
                patch.object(sys, "argv",
                             ["backup_verification.py", "--base",
                              str(self.base), "--json"]):
            self.assertEqual(bv.main(), 0)
        # A gap (off-machine backup record removed) exits 1.
        (self.base / "cicd" / "env" / "off-machine-backup.json").unlink()
        with patch.object(bv, "_docker_images",
                          return_value=self._images()), \
                patch.object(bv.shutil, "disk_usage",
                             return_value=fake_disk), \
                patch.object(bv, "check_timer",
                             return_value={"name": "deploy_timer",
                                           "status": "pass", "detail": "ok"}), \
                patch.object(sys, "argv",
                             ["backup_verification.py", "--base",
                              str(self.base)]):
            self.assertEqual(bv.main(), 1)
        with patch.object(sys, "argv",
                          ["backup_verification.py", "--base",
                           str(self.tmp / "does-not-exist")]):
            self.assertEqual(bv.main(), 2)


class ManifestSelfConsistencyTests(unittest.TestCase):
    def test_valid_manifest_passes(self):
        rows = [{"path": "data/canonical/a.json", "bytes": 3,
                 "sha256": _sha(b"abc")}]
        self.assertIsNone(bv._manifest_self_consistent(_manifest(rows)))

    def test_wrong_schema_fails(self):
        manifest = _manifest([])
        manifest["schema_version"] = "other"
        manifest["files"] = [{"path": "data/canonical/a.json", "bytes": 3,
                              "sha256": _sha(b"abc")}]
        manifest["file_count"] = 1
        manifest["total_bytes"] = 3
        self.assertIsNotNone(bv._manifest_self_consistent(manifest))

    def test_duplicate_path_fails(self):
        row = {"path": "data/canonical/a.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row, row])
        self.assertIsNotNone(bv._manifest_self_consistent(manifest))

    def test_bad_sha_fails(self):
        row = {"path": "data/canonical/a.json", "bytes": 3, "sha256": "zz"}
        manifest = _manifest([row])
        self.assertIsNotNone(bv._manifest_self_consistent(manifest))

    def test_traversal_path_fails(self):
        row = {"path": "data/canonical/../../evil.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_absolute_path_fails(self):
        row = {"path": "/etc/passwd", "bytes": 3, "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_dot_path_fails(self):
        row = {"path": "data/canonical/./a.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_wrong_area_fails(self):
        row = {"path": "data/unknown/a.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))
        row = {"path": "other/canonical/a.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_shallow_path_fails(self):
        row = {"path": "data/a.json", "bytes": 3, "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_backslash_path_fails(self):
        row = {"path": "data\\canonical\\a.json", "bytes": 3,
               "sha256": _sha(b"abc")}
        manifest = _manifest([row])
        self.assertIn("unsafe manifest path",
                      bv._manifest_self_consistent(manifest))

    def test_safe_manifest_path_matches_private_data_snapshot(self):
        # The bv validator must stay identical to the canonical rule in
        # scripts/private_data_snapshot._safe_relative.
        from scripts.private_data_snapshot import AREAS, _safe_relative
        self.assertEqual(bv._MANIFEST_AREAS, AREAS)
        valid = ["data/canonical/a.json", "data/quarantine/x/y/z.txt",
                 "data/state/s.json"]
        invalid = ["data/canonical/../../evil.json", "/etc/passwd",
                   "data/canonical/./a.json", "data/unknown/a.json",
                   "other/canonical/a.json", "data/a.json",
                   "data\\canonical\\a.json", "", "data//canonical/a.json",
                   "data/canonical/a.json/", "data/canonical/a.json\x00"]
        for path in valid:
            self.assertEqual(bv._safe_manifest_path(path), path)
            self.assertEqual(_safe_relative(path), path)
        for path in invalid:
            with self.assertRaises(ValueError, msg=path):
                bv._safe_manifest_path(path)
            with self.assertRaises(ValueError, msg=path):
                _safe_relative(path)


class InventoryTests(unittest.TestCase):
    """The private artifact delivery chain inventory."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tj0053-inventory-"))
        self.base = self.tmp / "platform-deploy"
        self._build_base()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build_base(self):
        files = {"data/canonical/a.json": b'{"k": 1}',
                 "data/canonical/b.json": b'{"k": 2}'}
        snap = self.base / "secure" / "tianji-knowledge"
        _write_snapshot(snap, files)
        _write_snapshot(self.base / "secure" / "tianji-knowledge-pre-a",
                        {"data/canonical/a.json": b'{"k": 1}'})
        # The cicd pin is the SHA256 of the live manifest file.
        manifest_path = snap / "private-data-manifest.json"
        pin = _sha(manifest_path.read_bytes())
        env = self.base / "cicd" / "env"
        env.mkdir(parents=True)
        (env / "trusted-acceptance").write_text(
            "trusted manifest SHA256: %s\n" % pin, encoding="utf-8")
        (env / "off-machine-backup.json").write_text(
            json.dumps({"target": "operator-vault:tianji-2026-11-12",
                        "last_verified": "2026-11-12"}), encoding="utf-8")
        # The private build script the deploy agent invokes.
        build = self.base / "tianji"
        build.mkdir(parents=True)
        script = build / "build-sealed-for.sh"
        script.write_text("#!/bin/sh\n# sealed build\n", encoding="utf-8")
        script.chmod(0o755)
        # deploys.log + state (one DEPLOYED pair).
        evid = self.base / "deployment-evidence" / "tj-core-01"
        evid.mkdir(parents=True)
        sha = "b" * 40
        (evid / "deploys.log").write_text(
            _log_line(sha=sha, result="DEPLOYED",
                      image="tianji-api:cicd-prerelease-bbbbbbbb",
                      detail="health+bazi ok",
                      ts="2026-11-12T00:01:00+00:00") + "\n",
            encoding="utf-8")
        state = self.base / "cicd" / "state"
        state.mkdir(parents=True)
        (state / "tianji-prerelease.sha").write_text(sha, encoding="utf-8")
        (state / "tianji-prerelease.api-image").write_text(
            "tianji-api:cicd-prerelease-bbbbbbbb", encoding="utf-8")
        (state / "tianji-prerelease.web-image").write_text(
            "ghcr.io/hellomrduan/tianji-web:" + sha, encoding="utf-8")
        # Admin DB.
        admin = self.base / "data" / "tianji-admin"
        admin.mkdir(parents=True)
        (admin / "tianji_admin.db").write_bytes(
            b"SQLite format 3\x00" + b"\x00" * 100)
        # Private repo: real git repo, clean tree.
        self._init_private_repo()
        self._sha = sha

    def _init_private_repo(self):
        repo = self.base / "projects" / "tianji-private-knowledge"
        repo.mkdir(parents=True)
        if not HAVE_GIT:
            return
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email",
                        "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name",
                        "test"], check=True)
        (repo / "README.md").write_text("private\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"],
                       check=True)

    def _inventory(self):
        images = {
            "tianji-api:cicd-prerelease-bbbbbbbb",
            "ghcr.io/hellomrduan/tianji-web:" + self._sha,
            "tianji-api:sealed-82b119e",
            "tianji-web:static-82b119e",
        }
        with patch.object(bv, "_docker_images", return_value=images):
            return bv.inventory(self.base)

    def _names(self, result):
        return [a["name"] for a in result["artifacts"]]

    def test_healthy_chain_has_no_unresolvable_links(self):
        result = self._inventory()
        self.assertEqual(result["unresolvable"], [],
                         msg=json.dumps(result, indent=2))
        self.assertEqual(self._names(result), [
            "live_snapshot", "cicd_pin", "private_build_script",
            "private_repo", "deploys_log", "admin_db", "ghcr_web_image"])
        by_name = {a["name"]: a for a in result["artifacts"]}
        # Every artifact carries a pin and a last-verified timestamp.
        for name, artifact in by_name.items():
            self.assertTrue(artifact["pin"], name)
            self.assertTrue(artifact["last_verified"]
                            or name == "private_repo", name)
        # The live snapshot pin equals the cicd pin (the chain binds).
        self.assertEqual(by_name["live_snapshot"]["pin"],
                         by_name["cicd_pin"]["pin"])
        self.assertEqual(by_name["deploys_log"]["pin"], self._sha)
        self.assertEqual(by_name["ghcr_web_image"]["pin"],
                         "ghcr.io/hellomrduan/tianji-web:" + self._sha)

    def test_inventory_is_read_only(self):
        def fingerprint():
            out = []
            for path in sorted(self.base.rglob("*")):
                if path.is_file():
                    out.append((str(path.relative_to(self.base)),
                                path.stat().st_size,
                                _sha(path.read_bytes())))
            return out
        before = fingerprint()
        self._inventory()
        self.assertEqual(before, fingerprint())

    def test_each_missing_artifact_is_unresolvable(self):
        cases = [
            ("live_snapshot",
             self.base / "secure" / "tianji-knowledge"
             / "private-data-manifest.json"),
            ("cicd_pin",
             self.base / "cicd" / "env" / "trusted-acceptance"),
            ("private_build_script",
             self.base / "tianji" / "build-sealed-for.sh"),
            ("private_repo",
             self.base / "projects" / "tianji-private-knowledge"),
            ("deploys_log",
             self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"),
            ("admin_db",
             self.base / "data" / "tianji-admin" / "tianji_admin.db"),
            ("ghcr_web_image",
             self.base / "cicd" / "state" / "tianji-prerelease.web-image"),
        ]
        for name, path in cases:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            result = self._inventory()
            self.assertIn(name, " ".join(result["unresolvable"]), name)
            # Rebuild the whole base from scratch for the next case.
            shutil.rmtree(self.base)
            self._build_base()

    def test_snapshot_pin_mismatch_is_unresolvable(self):
        # The cicd pin records a different manifest SHA256 than the
        # live snapshot carries: the chain link is broken.
        (self.base / "cicd" / "env" / "trusted-acceptance").write_text(
            "trusted manifest SHA256: %s\n" % ("e" * 64), encoding="utf-8")
        result = self._inventory()
        self.assertIn("live_snapshot", " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "live_snapshot"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("!= cicd pin", failed["detail"])

    def test_malformed_web_image_ref_is_unresolvable(self):
        (self.base / "cicd" / "state" / "tianji-prerelease.web-image").write_text(
            "not-a-ghcr-image", encoding="utf-8")
        result = self._inventory()
        self.assertIn("ghcr_web_image", " ".join(result["unresolvable"]))

    def test_missing_docker_is_skip_not_unresolvable(self):
        # Without docker the web image presence cannot be checked,
        # but the recorded ref is still a resolvable chain link.
        with patch.object(bv, "_docker_images", return_value=None):
            result = bv.inventory(self.base)
        by_name = {a["name"]: a for a in result["artifacts"]}
        self.assertEqual(by_name["ghcr_web_image"]["status"], "skip")
        self.assertEqual(result["unresolvable"], [])

    def test_inventory_cli_exit_codes(self):
        with patch.object(bv, "_docker_images",
                          return_value={
                              "tianji-api:cicd-prerelease-bbbbbbbb",
                              "ghcr.io/hellomrduan/tianji-web:" + self._sha,
                              "tianji-api:sealed-82b119e",
                              "tianji-web:static-82b119e"}), \
                patch.object(sys, "argv",
                             ["backup_verification.py", "--base",
                              str(self.base), "--inventory"]):
            self.assertEqual(bv.main(), 0)
        (self.base / "cicd" / "env" / "trusted-acceptance").unlink()
        with patch.object(bv, "_docker_images",
                          return_value={
                              "tianji-api:cicd-prerelease-bbbbbbbb",
                              "ghcr.io/hellomrduan/tianji-web:" + self._sha,
                              "tianji-api:sealed-82b119e",
                              "tianji-web:static-82b119e"}), \
                patch.object(sys, "argv",
                             ["backup_verification.py", "--base",
                              str(self.base), "--inventory"]):
            self.assertEqual(bv.main(), 1)

    def test_malformed_snapshot_manifest_is_unresolvable(self):
        (self.base / "secure" / "tianji-knowledge"
         / "private-data-manifest.json").write_text(
            "{not json", encoding="utf-8")
        result = self._inventory()
        self.assertIn("live_snapshot", " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "live_snapshot"][0]
        self.assertEqual(failed["status"], "fail")

    def test_cicd_pin_without_hex_is_unresolvable(self):
        (self.base / "cicd" / "env" / "trusted-acceptance").write_text(
            "no manifest hash recorded here\n", encoding="utf-8")
        result = self._inventory()
        self.assertIn("cicd_pin", " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "cicd_pin"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("no 64-hex", failed["detail"])

    def test_malformed_deploys_log_is_unresolvable(self):
        (self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
         ).write_text("{not json}\n{\"also\": \"broken\"}\n",
                      encoding="utf-8")
        result = self._inventory()
        self.assertIn("deploys_log", " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "deploys_log"][0]
        self.assertEqual(failed["status"], "fail")

    def test_non_executable_build_script_is_unresolvable(self):
        script = self.base / "tianji" / "build-sealed-for.sh"
        script.chmod(0o644)
        result = self._inventory()
        self.assertIn("private_build_script",
                      " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "private_build_script"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("NOT executable", failed["detail"])

    def test_recorded_web_image_absent_from_docker_is_unresolvable(self):
        # Docker is present but the recorded web image is not in it.
        with patch.object(bv, "_docker_images",
                          return_value={"tianji-api:something-else"}):
            result = bv.inventory(self.base)
        self.assertIn("ghcr_web_image", " ".join(result["unresolvable"]))
        failed = [a for a in result["artifacts"]
                  if a["name"] == "ghcr_web_image"][0]
        self.assertEqual(failed["status"], "fail")
        self.assertIn("not present locally", failed["detail"])
        with patch.object(sys, "argv",
                          ["backup_verification.py", "--base",
                           str(self.tmp / "does-not-exist"),
                           "--inventory"]):
            self.assertEqual(bv.main(), 2)

    def test_inventory_deploys_log_pin_is_last_stable(self):
        # A newer preview DEPLOYED must not become the stable pin.
        evid = self.base / "deployment-evidence" / "tj-core-01" / "deploys.log"
        lines = evid.read_text(encoding="utf-8").splitlines()
        lines.append(_log_line(sha="c" * 40, result="DEPLOYED",
                               channel="preview-round1",
                               image="tianji-api:preview-c",
                               ts="2026-11-12T00:05:00+00:00"))
        evid.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = self._inventory()
        by_name = {a["name"]: a for a in result["artifacts"]}
        self.assertEqual(by_name["deploys_log"]["pin"], self._sha)
        self.assertEqual(by_name["deploys_log"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
