"""Real-filesystem regression tests for isolated private backend packaging."""
from pathlib import Path
import tempfile
import unittest

from scripts.assemble_private_backend import (
    CODE_DIRECTORIES, assemble_private_backend,
)
from scripts.private_data_snapshot import AREAS, export_private_data


class AssemblePrivateBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.checkout = root / "checkout"
        self.checkout.mkdir()
        for code_dir in CODE_DIRECTORIES:
            p = self.checkout / code_dir
            p.mkdir()
            (p / "owned_code.txt").write_bytes(("code:" + code_dir).encode())
        (self.checkout / "pyproject.toml").write_text("[build-system]\nrequires=[]\n")
        for area in AREAS:
            f = self.checkout / "data" / area / "asset.txt"
            f.parent.mkdir(parents=True)
            f.write_bytes(("content-" + area).encode())
        self.snapshot = root / "private-snapshot"
        export_private_data(self.checkout, self.snapshot)
        self.destination = root / "private-application"

    def test_assemble_no_public_data_fallback(self):
        (self.checkout / "data/canonical/asset.txt").write_bytes(b"changed-public-copy")
        result = assemble_private_backend(self.checkout, self.snapshot, self.destination)
        self.assertEqual(result["knowledge_files"], len(AREAS))
        self.assertEqual((self.destination / "data/canonical/asset.txt").read_bytes(),
                         b"content-canonical")
        self.assertFalse((self.destination / ".git").exists())
        self.assertEqual((self.destination / "src/owned_code.txt").read_bytes(),
                         b"code:src")
        self.assertEqual(self.destination.stat().st_mode & 0o777, 0o700)

    def test_reject_existing_destination(self):
        self.destination.mkdir()
        with self.assertRaisesRegex(ValueError, "must not exist"):
            assemble_private_backend(self.checkout, self.snapshot, self.destination)

    def test_reject_destination_inside_public_checkout(self):
        with self.assertRaisesRegex(ValueError, "separated"):
            assemble_private_backend(self.checkout, self.snapshot,
                                     self.checkout / "private-build")

    def test_reject_destination_inside_git_ancestor(self):
        (self.destination.parent / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git checkout"):
            assemble_private_backend(self.checkout, self.snapshot, self.destination)

    def test_reject_application_symlinks(self):
        target = self.checkout / "unexpected-secret.txt"
        target.write_bytes(b"not code")
        link = self.checkout / "src/external-link.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported")
        with self.assertRaisesRegex(ValueError, "Unsafe application code"):
            assemble_private_backend(self.checkout, self.snapshot, self.destination)
        self.assertFalse(self.destination.exists())

    def test_reject_secret_like_file(self):
        (self.checkout / "scripts/.env").write_text("TOKEN=private")
        with self.assertRaisesRegex(ValueError, "Secret or generated"):
            assemble_private_backend(self.checkout, self.snapshot, self.destination)
        self.assertFalse(self.destination.exists())

    def test_reject_incomplete_code_tree(self):
        (self.checkout / "schemas/owned_code.txt").unlink()
        (self.checkout / "schemas").rmdir()
        with self.assertRaisesRegex(ValueError, "Missing or unsafe application"):
            assemble_private_backend(self.checkout, self.snapshot, self.destination)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
