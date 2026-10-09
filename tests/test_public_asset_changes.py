"""Exercises the real git diff protocol used by the public exposure gate."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from scripts.audit_public_asset_changes import (
    check_change_rows,
    diff_rows,
    inventory,
)


class PublicAssetChangesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "test-repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "ci@example.invalid")
        self.git("config", "user.name", "CI")
        self.write("data/canonical/rule.json", b'{"text":"original"}')
        self.write("data/state/source_state.json", b'{"version":1}')
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True)

    def write(self, path, content):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def test_real_tracked_inventory_excludes_untracked_assets(self):
        self.write("data/quarantine/untracked.txt", b"untracked")
        result = inventory(self.repo)
        self.assertEqual(result["tracked_files"], 2)
        self.assertEqual(result["areas"]["canonical"]["files"], 1)
        self.assertEqual(result["areas"]["canonical"]["bytes"], 19)
        self.assertEqual(result["areas"]["canonical"]["classification"], "review-content-before-publication")
        self.assertNotIn("quarantine", result["areas"])

    def test_real_git_diff_denies_new_public_content_and_allows_metadata(self):
        self.write("data/canonical/rule.json", b'{"text":"changed"}')
        self.write("data/state/source_state.json", b'{"version":2}')
        self.write("data/index/new.jsonl", b'{"text":"derived"}')
        self.git("add", ".")
        self.git("commit", "-qm", "changed data")
        rows = diff_rows(self.base, self.repo)
        self.assertIn(("M", "data/canonical/rule.json"), rows)
        self.assertIn(("A", "data/index/new.jsonl"), rows)
        self.assertEqual(
            check_change_rows(rows),
            ["M data/canonical/rule.json", "A data/index/new.jsonl"],
        )

    def test_during_migration_deletions_are_permitted(self):
        self.git("rm", "data/canonical/rule.json")
        self.git("commit", "-qm", "remove published HEAD asset")
        self.assertEqual(check_change_rows(diff_rows(self.base, self.repo)), [])

    def test_only_explicit_metadata_paths_are_allowed(self):
        self.assertEqual(check_change_rows([
            ("M", "data/state/source_state.json"),
            ("M", "data/registry/discovered_candidates.json"),
            ("A", "src/app.py"),
        ]), [])
        self.assertEqual(check_change_rows([
            ("M", "data/state/file_refresh_state.json"),
            ("A", "data/unknown/payload.txt"),
            ("T", "data/upstream/a.txt"),
        ]), [
            "M data/state/file_refresh_state.json",
            "A data/unknown/payload.txt",
            "T data/upstream/a.txt",
        ])

    def test_public_head_inventory_remains_valid_after_future_migration(self):
        root = Path(os.environ.get("TIANJI_PUBLIC_CHECKOUT") or Path(__file__).resolve().parents[1])
        self.assertTrue((root / ".git").exists(), "Inventory must run on an actual Git checkout")
        result = inventory(root)
        self.assertEqual(result["tracked_files"], sum(
            area["files"] for area in result["areas"].values()
        ))
        self.assertEqual(result["tracked_bytes"], sum(
            area["bytes"] for area in result["areas"].values()
        ))
        self.assertTrue(all(area["classification"] in {
            "review-content-before-publication",
            "metadata-needs-review",
            "unclassified-fail-closed",
        } for area in result["areas"].values()))


if __name__ == "__main__":
    unittest.main()
