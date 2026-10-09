"""Complete private data bundle contract tests with real on-disk file bytes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.private_data_snapshot import (
    AREAS, MANIFEST, export_private_data, stage_private_data, verify_private_data,
)


class PrivateDataSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.repo = root / "public-checkout"
        self.repo.mkdir()
        self.assets = {}
        for area in AREAS:
            rel = f"data/{area}/sample.txt"
            payload = (area + ": tested真实知识文件\n").encode("utf-8")
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            self.assets[rel] = payload
        self.private = root / "private"
        self.workspace = root / "runtime"
        self.workspace.mkdir()

    def export(self):
        return export_private_data(self.repo, self.private)

    def update_manifest(self, fn):
        path = self.private / MANIFEST
        manifest = json.loads(path.read_text(encoding="utf-8"))
        fn(manifest)
        path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    def test_complete_roundtrip_and_permission_bits(self):
        manifest = self.export()
        self.assertEqual(manifest["file_count"], len(AREAS))
        self.assertEqual(manifest["areas"], list(AREAS))
        self.assertEqual(verify_private_data(self.private), manifest)
        result = stage_private_data(self.private, self.workspace)
        self.assertEqual(result["file_count"], len(AREAS))
        for rel, expected in self.assets.items():
            copied = self.workspace / rel
            self.assertEqual(copied.read_bytes(), expected)
            self.assertEqual(hashlib.sha256(expected).hexdigest(),
                             hashlib.sha256(copied.read_bytes()).hexdigest())
            self.assertEqual(copied.stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.workspace / "data").stat().st_mode & 0o777, 0o700)

    def test_reject_existing_export_and_workspace_data(self):
        self.export()
        with self.assertRaisesRegex(ValueError, "new export"):
            self.export()
        (self.workspace / "data").mkdir()
        with self.assertRaisesRegex(ValueError, "already contains data"):
            stage_private_data(self.private, self.workspace)

    def test_reject_export_into_public_checkout(self):
        with self.assertRaisesRegex(ValueError, "outside the public checkout"):
            export_private_data(self.repo, self.repo / "private-dump")
        self.assertFalse((self.repo / "private-dump").exists())

    def test_reject_missing_area_before_export(self):
        (self.repo / "data/product/sample.txt").unlink()
        with self.assertRaisesRegex(ValueError, "omitted"):
            self.export()
        self.assertFalse(self.private.exists())

    def test_reject_content_corruption_without_import(self):
        self.export()
        path = self.private / "data/product/sample.txt"
        path.write_bytes(b"altered")
        with self.assertRaisesRegex(ValueError, "SHA256 or size mismatch"):
            verify_private_data(self.private)
        with self.assertRaises(ValueError):
            stage_private_data(self.private, self.workspace)
        self.assertFalse((self.workspace / "data").exists())

    def test_reject_missing_and_undeclared_files(self):
        self.export()
        (self.private / "data/product/sample.txt").unlink()
        with self.assertRaisesRegex(ValueError, "omitted"):
            verify_private_data(self.private)
        (self.private / "data/product/sample.txt").write_bytes(self.assets["data/product/sample.txt"])
        (self.private / "data/index/extra.txt").write_bytes(b"extra")
        with self.assertRaisesRegex(ValueError, "undeclared"):
            verify_private_data(self.private)

    def test_reject_manifest_traversal(self):
        self.export()
        self.update_manifest(lambda obj: obj["files"][0].update(
            {"path": "data/canonical/../../../outside.txt"}
        ))
        with self.assertRaisesRegex(ValueError, "Unsafe data snapshot path"):
            verify_private_data(self.private)

    def test_reject_manifest_total_and_duplicate(self):
        self.export()
        self.update_manifest(lambda obj: obj.update(total_bytes=obj["total_bytes"] + 1))
        with self.assertRaisesRegex(ValueError, "totals"):
            verify_private_data(self.private)
        (self.private / MANIFEST).unlink()
        self.private.rename(self.private.with_name("old-export"))
        self.export()
        def duplicate(obj):
            obj["files"].append(dict(obj["files"][0]))
            obj["file_count"] += 1
            obj["total_bytes"] += obj["files"][0]["bytes"]
        self.update_manifest(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            verify_private_data(self.private)

    def test_reject_symlink(self):
        self.export()
        target = self.private / "data/index/unsafe.txt"
        try:
            target.symlink_to(self.private / "data/product/sample.txt")
        except (NotImplementedError, OSError):
            self.skipTest("Symlink unavailable")
        with self.assertRaisesRegex(ValueError, "Unsafe data file node"):
            verify_private_data(self.private)

    def test_reject_git_workspace_and_partial_import(self):
        self.export()
        (self.workspace / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git checkout"):
            stage_private_data(self.private, self.workspace)
        self.assertFalse((self.workspace / "data").exists())

    def test_real_repository_has_all_explicit_areas(self):
        root = Path(__file__).resolve().parents[1]
        for area in AREAS:
            with self.subTest(area=area):
                self.assertTrue((root / "data" / area).is_dir())


if __name__ == "__main__":
    unittest.main()
