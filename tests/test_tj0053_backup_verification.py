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


if __name__ == "__main__":
    unittest.main()
