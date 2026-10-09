"""Private knowledge consumer contract tests: real bytes; no mocked API."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.export_private_knowledge import export_private_knowledge
from scripts.restore_private_knowledge import stage_private_knowledge, verify_private_export


class PrivateRestoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root / "public-source"
        self.public.mkdir()
        self.files = {
            "data/canonical/seed.json": b'{"real":true}\n',
            "data/quarantine/phase1/review.txt": "待核验·甲".encode("utf-8"),
        }
        for name, contents in self.files.items():
            target = self.public / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
        self.private = self.root / "private-assets"
        export_private_knowledge(self.public, self.private)
        self.workspace = self.root / "runtime-workspace"
        self.workspace.mkdir()

    def _manifest(self):
        return json.loads((self.private / "private-export-manifest.json").read_text(encoding="utf-8"))

    def _put_manifest(self, manifest):
        (self.private / "private-export-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
        )

    def test_verify_and_stage_real_bytes_with_no_public_fallback(self):
        manifest = verify_private_export(self.private)
        result = stage_private_knowledge(self.private, self.workspace)
        self.assertEqual(result["file_count"], 2)
        self.assertEqual(result["total_bytes"], manifest["total_bytes"])
        for name, content in self.files.items():
            target = self.workspace / name
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(hashlib.sha256(content).hexdigest(),
                             hashlib.sha256(target.read_bytes()).hexdigest())
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(ValueError):
            stage_private_knowledge(self.private, self.workspace)

    def test_reject_public_checkout_data_directory_without_changing_it(self):
        existing = self.workspace / "data/canonical/seed.json"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"public-old-version")
        with self.assertRaises(ValueError):
            stage_private_knowledge(self.private, self.workspace)
        self.assertEqual(existing.read_bytes(), b"public-old-version")
        self.assertFalse((self.workspace / "data/quarantine").exists())

    def test_reject_git_checkout(self):
        (self.workspace / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git checkout"):
            stage_private_knowledge(self.private, self.workspace)

    def test_reject_workspace_containing_private_root(self):
        with self.assertRaises(ValueError):
            stage_private_knowledge(self.private, self.root)

    def test_reject_changed_content(self):
        source = self.private / "data/canonical/seed.json"
        source.write_bytes(b'{"real":false}\n')
        with self.assertRaisesRegex(ValueError, "SHA256/size mismatch"):
            verify_private_export(self.private)
        with self.assertRaises(ValueError):
            stage_private_knowledge(self.private, self.workspace)
        self.assertFalse((self.workspace / "data/canonical").exists())

    def test_reject_deleted_file(self):
        (self.private / "data/quarantine/phase1/review.txt").unlink()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            verify_private_export(self.private)

    def test_reject_extra_unmanifested_file(self):
        (self.private / "data/canonical/extra.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "Unmanifested"):
            verify_private_export(self.private)

    def test_reject_manifest_traversal(self):
        manifest = self._manifest()
        manifest["files"][0]["path"] = "data/canonical/../../outside.txt"
        self._put_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "Unsafe manifest file path"):
            verify_private_export(self.private)

    def test_reject_manifest_duplicate(self):
        manifest = self._manifest()
        manifest["files"].append(dict(manifest["files"][0]))
        manifest["file_count"] += 1
        manifest["total_bytes"] += manifest["files"][0]["bytes"]
        self._put_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "duplicated"):
            verify_private_export(self.private)

    def test_reject_manifest_total_tampering(self):
        manifest = self._manifest()
        manifest["total_bytes"] += 1
        self._put_manifest(manifest)
        with self.assertRaisesRegex(ValueError, "totals"):
            verify_private_export(self.private)

    def test_reject_symlink_inside_export(self):
        outside = self.root / "not-knowledge.txt"
        outside.write_text("not knowledge")
        link = self.private / "data/quarantine/phase1/unsafe.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "symlink"):
            verify_private_export(self.private)

    def test_reject_missing_manifest(self):
        (self.private / "private-export-manifest.json").unlink()
        with self.assertRaisesRegex(ValueError, "manifest"):
            verify_private_export(self.private)


if __name__ == "__main__":
    unittest.main()
