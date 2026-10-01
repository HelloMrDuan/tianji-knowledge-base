import copy
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from tianji_kb.knowledge import local_path, read_json, validate_knowledge, validate_protected_files

ROOT = Path(__file__).resolve().parents[1]

class KnowledgeGovernanceTests(unittest.TestCase):
    def test_entire_model_and_protected_baseline(self):
        validate_protected_files(ROOT)
        validate_knowledge(ROOT)

    def test_evidence_paths_reject_escape_and_nondata(self):
        for path in ('../secret', 'data/canonical/../../../secret', 'config/source_registry.json', '/tmp/foo'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                local_path(ROOT, path)

    def test_real_json_schemas_reject_missing_data_and_invalid_grades(self):
        schema = read_json(ROOT / 'schemas/knowledge/bundle.schema.json')
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate({'model': 'phase1-knowledge'})
        source_schema = read_json(ROOT / 'schemas/knowledge/sources.schema.json')
        with self.assertRaises(ValidationError):
            Draft202012Validator(source_schema).validate({'schema_version':'1.0', 'sources':[{'evidence_level':'A+'}]})

    def test_bundles_reject_dangling_refs_and_duplicate_ids(self):
        model = validate_knowledge(ROOT)
        if not model['bundles']:
            return  # Framework PR precedes domain data.
        bundles = copy.deepcopy(model['bundles'])
        bundles[0]['terms'][0]['related_terms'] = ['yijing.term.nonexistent']
        with self.assertRaisesRegex(ValueError, 'Dangling'):
            validate_knowledge(ROOT, bundles)
        bundles = copy.deepcopy(model['bundles'])
        bundles[0]['terms'].append(copy.deepcopy(bundles[0]['terms'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            validate_knowledge(ROOT, bundles)
