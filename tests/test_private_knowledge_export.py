"""Private asset export: real byte copy, hash integrity, and fail-closed destination."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.export_private_knowledge import export_private_knowledge


class PrivateExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "source"
        self.root.mkdir()
        for name, data in (
            ("data/canonical/bazi/table.json", b'{"validated":true}'),
            ("data/quarantine/phase1/notes.txt", "待核验内容".encode("utf-8")),
        ):
            f = self.root / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        self.dest = Path(self.tmp.name) / "private-export"

    def test_export_is_exact_with_manifest_and_restricted_files(self):
        manifest = export_private_knowledge(self.root, self.dest)
        self.assertEqual(manifest["file_count"], 2)
        self.assertEqual(manifest["total_bytes"], sum(x["bytes"] for x in manifest["files"]))
        actual = json.loads((self.dest / "private-export-manifest.json").read_text())
        self.assertEqual(actual, manifest)
        for row in manifest["files"]:
            original = self.root / row["path"]
            copy = self.dest / row["path"]
            self.assertEqual(copy.read_bytes(), original.read_bytes())
            self.assertEqual(hashlib.sha256(copy.read_bytes()).hexdigest(), row["sha256"])
            self.assertEqual(copy.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.dest.stat().st_mode & 0o777, 0o700)

    def test_reject_public_destinations_and_existing_directory(self):
        with self.assertRaises(ValueError):
            export_private_knowledge(self.root, self.root / "web" / "dist")
        export_private_knowledge(self.root, self.dest)
        with self.assertRaises(ValueError):
            export_private_knowledge(self.root, self.dest)

    def test_reject_symlink_and_missing_quarantine(self):
        other = Path(self.tmp.name) / "outside"
        other.write_text("confidential")
        link = self.root / "data/canonical/outside.json"
        try:
            link.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not supported")
        with self.assertRaises(ValueError):
            export_private_knowledge(self.root, self.dest)
        link.unlink()
        (self.root / "data/quarantine/phase1/notes.txt").unlink()
        (self.root / "data/quarantine/phase1").rmdir()
        (self.root / "data/quarantine").rmdir()
        with self.assertRaises(ValueError):
            export_private_knowledge(self.root, self.dest)


if __name__ == "__main__":
    unittest.main()
