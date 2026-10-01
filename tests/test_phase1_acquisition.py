import copy
import json
import tempfile
import unittest
from pathlib import Path

from tianji_kb.acquisition import git_blob_sha, stage_candidate
from tianji_kb.staging import stage_update

SOURCE = {'source_id':'yijing.source.example','kind':'classical','public_domain':True,'license':'Public-Domain',
          'repository':'example/original','path':'原典.txt','commit':'a'*40,'blob_sha':None,'rights_basis':'古籍原文，现代整理需另核'}

class AcquisitionTests(unittest.TestCase):
    def test_candidate_records_verified_bytes_and_never_overwrites_canonical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/'data/canonical/yijing/phase1_knowledge.json'
            old.parent.mkdir(parents=True);old.write_text('reviewed')
            content='原典新版本\r\n'.encode();blob=git_blob_sha(content)
            result=stage_candidate(root,SOURCE,'b'*40,content,blob,'c'*40)
            self.assertEqual((root/result['raw_path']).read_bytes(),content)
            self.assertEqual(old.read_text(),'reviewed')
            self.assertEqual(result['evidence_level'],'D')
            self.assertTrue(result['file_changed'])
            self.assertFalse(result['body_saved_to_quarantine'])
            self.assertFalse(result['promotion_allowed'])
            self.assertEqual(stage_candidate(root,SOURCE,'b'*40,content,blob,'c'*40),result)

    def test_invalid_rights_path_or_blob_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);content=b'original';blob=git_blob_sha(content)
            for source,commit,checksum in [(SOURCE,'b'*40,'0'*40),
                    ({**SOURCE,'public_domain':False},'b'*40,blob),
                    ({**SOURCE,'source_id':'../../escape'},'b'*40,blob),
                    (SOURCE,'../escape',blob),
                    ({**SOURCE,'blob_sha':'0'*40},'a'*40,blob)]:
                with self.subTest(source=source,commit=commit),self.assertRaises(ValueError):
                    stage_candidate(root,source,commit,content,checksum)
            self.assertFalse(list(root.rglob('*')))

    def test_unchanged_blob_is_explicit_and_missing_raw_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);content=b'original';blob=git_blob_sha(content)
            result=stage_candidate(root,SOURCE,'b'*40,content,blob,blob)
            self.assertFalse(result['file_changed'])
            (root/result['raw_path']).unlink()
            with self.assertRaisesRegex(ValueError,'RAW'):
                stage_candidate(root,SOURCE,'b'*40,content,blob,blob)

    def test_unchanged_refresh_does_not_duplicate_canonical_body_in_quarantine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);name='data/canonical/yijing/original.txt';path=root/name
            path.parent.mkdir(parents=True);path.write_text('reviewed')
            result,changed=stage_update(root,name,'source','a'*40,'reviewed')
            self.assertFalse(changed);self.assertEqual(result,path.resolve())
            self.assertFalse((root/'data/quarantine').exists())
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                stage_update(root,name,'../../escape','a'*40,'new')
