"""Real production API with no data/canonical or data/quarantine checkout at runtime."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tianji_kb.resolver import ROOT
from tianji_kb.runtime_catalog import RuntimeUnavailable, load_catalog
from tianji_kb.sealed_bundle import export_sealed_bundle, RUNTIME_TABLES


CHECK = """
from pathlib import Path
from fastapi.testclient import TestClient
from tianji_kb.api import create_app
from tianji_kb.resolver import ROOT
from tianji_kb.runtime_catalog import load_catalog
from tianji_kb import api as api_module
# Both the trusted bundle AND the imported Python source tree must have no knowledge checkout.
assert not (ROOT/'data/quarantine').exists()
assert set(p.relative_to(ROOT).as_posix() for p in (ROOT/'data').rglob('*.json')) == set(__import__('tianji_kb.sealed_bundle',fromlist=['RUNTIME_TABLES']).RUNTIME_TABLES)
assert set(p.name for p in (ROOT/'build').iterdir()) == {'production_runtime.json','production_rag.jsonl'}
client = TestClient(create_app(admin_read_token='backend-token'))
health = client.get('/health')
assert health.status_code == 200, health.text
assert health.json()['rag_ready'] is True
dream = client.post('/api/v1/dream/culture', json={'dream_text': '我梦见被蛇咬了'})
assert dream.status_code == 200, dream.text
assert dream.json()['status'] == 'reviewed_cultural_matches'
assert dream.json()['matches'][0]['short_quote'] == '蛇咬人主得大财'
empty = client.post('/api/v1/dream/culture', json={'dream_text': '梦见考试'})
assert empty.status_code == 200 and empty.json()['matches'] == []
hidden = client.post('/api/v1/admin/research/dream', json={'dream_text': '我梦见被蛇咬了'})
assert hidden.status_code == 401
bazi = client.post('/api/v1/public/execute', json={'domain':'bazi',
        'variant':'ziping-structural-v1','input':{'value':'2000-01-07T12:00:00+08:00'},
        'mode':'production','explain':False})
assert bazi.status_code == 200, bazi.text
assert bazi.json()['chart']['day_master']['stem'] == '甲'
restricted = client.post('/api/v1/execute', json={'domain':'bazi','input':{'value':'2000-01-07T12:00:00+08:00'}})
assert restricted.status_code == 503, restricted.text
print('sealed runtime: health, reviewed dream, no-match, admin auth, actual Bazi passed')
"""


class SealedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)/'private-server-only'
        self.hashes = export_sealed_bundle(ROOT, self.path)

    def environment(self, **extra):
        env = os.environ.copy()
        env.update({'TIANJI_RUNTIME_MODE':'sealed',
                    'TIANJI_RUNTIME_ROOT':str(self.path.resolve()),
                    'TIANJI_RUNTIME_SHA256':self.hashes['production_runtime.json'],
                    'PYTHONPATH':str(ROOT/'src')})
        env.update(extra)
        return env

    def test_source_free_full_api_with_real_reviewed_rag(self):
        self.assertFalse((self.path/'data/quarantine').exists())
        self.assertEqual({p.relative_to(self.path).as_posix() for p in (self.path/'data').rglob('*.json')}, set(RUNTIME_TABLES))
        self.assertEqual(sorted(p.name for p in (self.path/'build').iterdir()),
                         ['production_rag.jsonl', 'production_runtime.json'])
        self.assertTrue((self.path/'src/tianji_kb/api.py').is_file())
        self.assertFalse((self.path/'src'/'data').exists())
        result = subprocess.run([sys.executable, '-c', CHECK], cwd=self.path,
                                env=self.environment(PYTHONPATH=str(self.path/'src')),
                                capture_output=True, text=True, timeout=100)
        self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)
        self.assertIn('actual Bazi passed', result.stdout)

    def test_wrong_pin_missing_index_and_unexpected_file_fail_closed(self):
        with self.assertRaises(RuntimeUnavailable):
            with patch.dict(os.environ, self.environment(TIANJI_RUNTIME_SHA256='0'*64)):
                load_catalog(self.path)
        (self.path/'build'/'production_rag.jsonl').unlink()
        with self.assertRaises(RuntimeUnavailable):
            with patch.dict(os.environ, self.environment()):
                load_catalog(self.path)
        (self.path/'build'/'production_rag.jsonl').write_bytes((ROOT/'build/production_rag.jsonl').read_bytes())
        (self.path/'data'/'accidental-source.txt').write_text('must not ship')
        with self.assertRaises(RuntimeUnavailable):
            with patch.dict(os.environ, self.environment()):
                load_catalog(self.path)

    def test_tampered_runtime_table_is_rejected(self):
        table = self.path / RUNTIME_TABLES[0]
        table.write_bytes(table.read_bytes() + b' ')
        with self.assertRaises(RuntimeUnavailable):
            with patch.dict(os.environ, self.environment()):
                load_catalog(self.path)

    def test_export_rejects_public_tree_or_preexisting_destination(self):
        with self.assertRaises(ValueError):
            export_sealed_bundle(ROOT, ROOT/'web/visual-prototype/dist/private-knowledge')
        with self.assertRaises(ValueError):
            export_sealed_bundle(ROOT, self.path)


if __name__ == '__main__':
    unittest.main()
