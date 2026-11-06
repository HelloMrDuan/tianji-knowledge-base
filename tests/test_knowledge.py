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

    def test_sources_schema_provenance_kind(self):
        # Schema revision E0381 (TJ-012.3): provenance_kind distinguishes
        # github from library_scan sources. A library scan has no git
        # commit, so commit must be null there (never a fabricated
        # 40-hex value); catalog_id + pdf_sha256 are required instead.
        # The fixture is a deep copy of a real record from
        # config/knowledge_sources.json, mutated per case -- no
        # hand-invented field values. The library_scan catalog_id /
        # pdf_sha256 below are the verified NLC416 values from the
        # 《子平真詮》 Phase 1 report (decision-pack.md), used here
        # only as a shape example; no source record is registered.
        source_schema = read_json(ROOT / 'schemas/knowledge/sources.schema.json')
        validator = Draft202012Validator(source_schema)
        sources_obj = read_json(ROOT / 'config/knowledge_sources.json')
        self.assertEqual(len(sources_obj['sources']), 102)
        validator.validate(sources_obj)
        base = copy.deepcopy(sources_obj['sources'][0])

        def check(record, expect_valid, label):
            with self.subTest(case=label):
                obj = {'schema_version': '1.0', 'sources': [record]}
                if expect_valid:
                    validator.validate(obj)
                else:
                    with self.assertRaises(ValidationError):
                        validator.validate(obj)

        github = copy.deepcopy(base)
        github['provenance_kind'] = 'github'
        check(github, True, 'github record validates unchanged')

        library = copy.deepcopy(base)
        library['provenance_kind'] = 'library_scan'
        library['commit'] = None
        library['catalog_id'] = 'NLC416-11jh010455-35296'
        library['pdf_sha256'] = '71402a780b0351b54edf121a51bc4a4a4ce5896496c35b954563ee06f1a6f620'
        check(library, True, 'library_scan with null commit validates')

        no_pdf = copy.deepcopy(library)
        del no_pdf['pdf_sha256']
        check(no_pdf, False, 'library_scan without pdf_sha256 fails')

        no_catalog = copy.deepcopy(library)
        del no_catalog['catalog_id']
        check(no_catalog, False, 'library_scan without catalog_id fails')

        bad_commit = copy.deepcopy(base)
        bad_commit['provenance_kind'] = 'github'
        bad_commit['commit'] = 'deadbeef'
        check(bad_commit, False, 'github with non-40-hex commit fails')

        fake_commit = copy.deepcopy(library)
        fake_commit['commit'] = base['commit']
        check(fake_commit, False, 'library_scan with 40-hex commit fails')

        absent = copy.deepcopy(base)
        self.assertNotIn('provenance_kind', absent)
        check(absent, True, 'provenance_kind absent validates unchanged')

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
