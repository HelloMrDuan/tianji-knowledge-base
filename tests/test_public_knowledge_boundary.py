"""Public automation must update source metadata, never refreshed knowledge bodies."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.public_knowledge_boundary import (
    refuse_public_knowledge_write,
    validate_metadata_only_paths,
)

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ENV = {
    "GITHUB_ACTIONS": "true",
    "GITHUB_REPOSITORY": "HelloMrDuan/tianji-knowledge-base",
}


class PublicKnowledgeBoundaryTests(unittest.TestCase):
    def test_public_actions_block_knowledge_mutation(self):
        with self.assertRaisesRegex(RuntimeError, "Public automated knowledge"):
            refuse_public_knowledge_write(PUBLIC_ENV)

    def test_non_action_local_knowledge_processing_still_supported(self):
        refuse_public_knowledge_write({
            "GITHUB_ACTIONS": "false",
            "GITHUB_REPOSITORY": "HelloMrDuan/tianji-knowledge-base",
        })

    def test_private_repository_not_falsely_blocked(self):
        refuse_public_knowledge_write({
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "HelloMrDuan/tianji-private-knowledge",
        })

    def test_metadata_whitelist_accepts_only_version_state(self):
        self.assertEqual(
            validate_metadata_only_paths(["data/state/source_state.json"]),
            ("data/state/source_state.json",),
        )
        self.assertEqual(validate_metadata_only_paths([]), ())

    def test_metadata_whitelist_rejects_knowledge_and_prefix_attacks(self):
        for bad in (
            "data/canonical/seed.json",
            "data/quarantine/source_snapshots/source.json",
            "data/index/bazi-rules.jsonl",
            "data/product/coverage.json",
            "data/upstream/src.txt",
            "data/reference/review.json",
            "data/state/source_state.json/extra",
            "../data/state/source_state.json",
            "data/state/source_state.json\nother",
            "data/state/source_state.json.bak",
            "",
        ):
            with self.subTest(path=bad), self.assertRaises(ValueError):
                validate_metadata_only_paths([bad])

    def test_metadata_whitelist_rejects_duplicates(self):
        with self.assertRaisesRegex(ValueError, "Duplicated"):
            validate_metadata_only_paths(["data/state/source_state.json"] * 2)

    def test_real_scripts_fail_before_network_or_filesystem_write_in_public_ci(self):
        for script in (
            "scripts/sync_content.py",
            "scripts/sync_public_domain.py",
            "scripts/refresh_manifest_sources.py",
        ):
            with self.subTest(script=script):
                process = subprocess.run(
                    [sys.executable, script],
                    cwd=ROOT,
                    env={**os.environ, **PUBLIC_ENV},
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertNotEqual(process.returncode, 0, process.stdout)
                self.assertIn("Public automated knowledge content writes are disabled",
                              process.stderr)

    def test_retire_full_text_refresh_automation(self):
        self.assertFalse((ROOT / ".github/workflows/refresh-manifest.yml").exists())

    def test_public_scheduled_source_sync_is_metadata_only(self):
        text = (ROOT / ".github/workflows/kb-sync.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/sync_sources.py", text)
        self.assertIn("git add -- data/state/source_state.json", text)
        self.assertIn("scripts/public_knowledge_boundary.py", text)
        for forbidden in (
            "scripts/sync_content.py",
            "scripts/sync_public_domain.py",
            "scripts/refresh_manifest_sources.py",
            "git add data/quarantine",
            "git add data/canonical",
        ):
            self.assertNotIn(forbidden, text)

    def test_no_public_workflow_stages_raw_knowledge(self):
        for workflow in (ROOT / ".github/workflows").glob("*.yml"):
            content = workflow.read_text(encoding="utf-8")
            if "git push" not in content:
                continue
            for area in (
                "canonical", "quarantine", "upstream", "index",
                "product", "reference", "research", "audit",
            ):
                with self.subTest(workflow=workflow.name, area=area):
                    self.assertNotIn("git add data/" + area, content)


if __name__ == "__main__":
    unittest.main()
