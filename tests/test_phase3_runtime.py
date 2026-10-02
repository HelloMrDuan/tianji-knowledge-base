import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tianji_kb.engine import execute,PROVIDERS
from tianji_kb.resolver import ROOT
from tianji_kb.runtime_catalog import load_catalog,RuntimeUnavailable,digest

class ProductionRuntimeTests(unittest.TestCase):
    def test_all_six_execute_without_opening_quarantine(self):
        original=Path.open
        def guarded(path,*args,**kwargs):
            if '/data/quarantine/' in str(path):raise AssertionError('Production attempted to open quarantine')
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):
            for domain in PROVIDERS:
                fixture=json.loads((ROOT/f'data/canonical/{domain}/phase2_golden.json').read_text())['cases'][0]
                output=execute(domain,fixture['input'])
                self.assertTrue(output['deterministic'])
                self.assertTrue(output['evidence'])
    def test_missing_artifact_fails_without_audit_fallback(self):
        with tempfile.TemporaryDirectory() as path:
            with patch('tianji_kb.knowledge.validate_knowledge',side_effect=AssertionError('Audit fallback forbidden')):
                with self.assertRaises(RuntimeUnavailable):load_catalog(Path(path))
    def test_stale_manifest_or_payload_is_rejected(self):
        artifact=json.loads((ROOT/'build/production_runtime.json').read_text())
        for field in ['payload','manifest']:
            bad=copy.deepcopy(artifact)
            if field=='payload':bad[field]['contracts']['yijing']['variant']='forged'
            else:bad[field]['data/quarantine/not-allowed.txt']='fake'
            with patch('tianji_kb.runtime_catalog.read_json',return_value=bad):
                with self.assertRaises(RuntimeUnavailable):load_catalog(ROOT)
        bad=copy.deepcopy(artifact);bad['manifest']['data/quarantine/not-allowed.txt']='fake';bad['manifest_sha256']=digest(bad['manifest'])
        with patch('tianji_kb.runtime_catalog.read_json',return_value=bad):
            with self.assertRaises(RuntimeUnavailable):load_catalog(ROOT)
    def test_release_change_requires_rebuild(self):
        original=Path.read_bytes
        def drift(path):
            data=original(path)
            return data+b' ' if path==ROOT/'config/domain_registry.json' else data
        with patch.object(Path,'read_bytes',drift):
            with self.assertRaises(RuntimeUnavailable):load_catalog(ROOT)
