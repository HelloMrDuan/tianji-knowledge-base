import tempfile
import unittest
from pathlib import Path
from tianji_kb.staging import stage_update

class StagingTests(unittest.TestCase):
    def test_changed_canonical_is_quarantined_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / 'data/canonical/yijing/book.txt'
            canonical.parent.mkdir(parents=True)
            canonical.write_text('reviewed', encoding='utf-8')
            candidate, changed = stage_update(root, canonical.relative_to(root).as_posix(), 'source', 'abc', 'unreviewed')
            self.assertTrue(changed)
            self.assertEqual(canonical.read_text(), 'reviewed')
            self.assertEqual(candidate.read_text(), 'unreviewed')
            self.assertIn('data/quarantine/', candidate.as_posix())
            self.assertFalse(stage_update(root, canonical.relative_to(root).as_posix(), 'source', 'abc', 'unreviewed')[1])
