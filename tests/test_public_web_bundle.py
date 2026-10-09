"""The public HTML/CSS/JS release may never contain internal knowledge files."""
from pathlib import Path
import tempfile
import unittest

from scripts.check_public_web_bundle import check_public_bundle


class PublicBundleBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "dist"
        (self.root / "assets").mkdir(parents=True)
        (self.root / "music").mkdir()
        (self.root / "index.html").write_text("<html></html>", encoding="utf-8")
        (self.root / "assets" / "app-123.js").write_text("console.log('ok')", encoding="utf-8")
        (self.root / "assets" / "style-123.css").write_text("body{}", encoding="utf-8")
        (self.root / "music" / "quiet-waters.ogg").write_bytes(b"OGG")

    def test_known_public_files_are_allowed(self):
        paths = check_public_bundle(self.root)
        self.assertEqual(len(paths), 4)

    def test_nonpublic_payloads_and_sourcemaps_are_rejected(self):
        forbidden = ["assets/production_runtime.json", "assets/production_rag.jsonl",
                     "assets/private-key.pem", "assets/bundle.js.map",
                     "data/canonical/phase1_knowledge.json", ".env",
                     "build/production_runtime.json", "assets/internal-notes.txt"]
        for name in forbidden:
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("not public", encoding="utf-8")
                with self.assertRaises(ValueError):
                    check_public_bundle(self.root)
                path.unlink()
                if path.parent not in (self.root, self.root/"assets", self.root/"music"):
                    path.parent.rmdir()
                    if path.parent.name in ("canonical",):
                        path.parent.parent.rmdir()

    def test_symlink_is_rejected_even_if_named_like_js(self):
        link = self.root / "assets" / "external.js"
        try:
            link.symlink_to(self.root / "index.html")
        except (OSError, NotImplementedError):
            self.skipTest("Filesystem does not support symbolic links")
        with self.assertRaises(ValueError):
            check_public_bundle(self.root)


if __name__ == "__main__":
    unittest.main()
