"""Offline acceptance snapshot-validation negative tests.

These verify that the knowledge-snapshot verifier FAILS CLOSED on:
- missing files, extra files, symlinks, path traversal,
- tampered SHA256/size, untrusted manifest schema.

They use SYNTHETIC snapshots (not real private data) and run in public CI.
"""
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.private_data_snapshot import verify_private_data, AREAS


def _make_snapshot(base: Path, files: dict[str, bytes]) -> Path:
    """Create a synthetic snapshot with the given {rel_path: content}."""
    snap = base / "snap"
    snap.mkdir(mode=0o700)
    rows = []
    for rel, content in sorted(files.items()):
        target = snap / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        rows.append({
            "path": rel,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    manifest = {
        "schema_version": "private-data-snapshot-v2",
        "areas": list(AREAS),
        "file_count": len(rows),
        "total_bytes": sum(r["bytes"] for r in rows),
        "files": rows,
    }
    (snap / "private-data-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return snap


def _minimal_files() -> dict[str, bytes]:
    """One tiny file per required area."""
    return {f"data/{area}/probe.json": b'{"ok": true}' for area in AREAS}


class SnapshotNegativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="snapneg-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_valid_snapshot_passes(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        manifest = verify_private_data(snap)
        self.assertEqual(manifest["file_count"], len(AREAS))

    def test_missing_file_rejected(self):
        files = _minimal_files()
        snap = _make_snapshot(self.tmp, files)
        # Delete one file but keep the manifest claiming it exists.
        victim = snap / f"data/{AREAS[0]}/probe.json"
        victim.unlink()
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_extra_file_rejected(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        (snap / f"data/{AREAS[0]}" / "extra.json").write_bytes(b"{}")
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_symlink_rejected(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        victim = snap / f"data/{AREAS[0]}" / "probe.json"
        content = victim.read_bytes()
        victim.unlink()
        (snap / f"data/{AREAS[0]}" / "real.json").write_bytes(content)
        os.symlink("real.json", victim)
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_tampered_content_rejected(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        victim = snap / f"data/{AREAS[0]}" / "probe.json"
        victim.write_bytes(b'{"ok": false, "tampered": true}')
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_path_traversal_in_manifest_rejected(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        manifest_path = snap / "private-data-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"].append({
            "path": "data/../evil.json",
            "bytes": 2,
            "sha256": hashlib.sha256(b"{}").hexdigest(),
        })
        manifest["file_count"] += 1
        manifest["total_bytes"] += 2
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_untrusted_schema_rejected(self):
        snap = _make_snapshot(self.tmp, _minimal_files())
        manifest_path = snap / "private-data-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "attacker-v1"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_private_data(snap)

    def test_snapshot_inside_git_rejected(self):
        # stage_private_data must refuse Git checkouts; verify_private_data
        # requires exactly {data, manifest} at root.
        snap = _make_snapshot(self.tmp, _minimal_files())
        (snap / ".git").mkdir()
        with self.assertRaises(ValueError):
            verify_private_data(snap)


if __name__ == "__main__":
    unittest.main()
