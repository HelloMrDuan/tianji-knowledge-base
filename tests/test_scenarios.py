import copy
import importlib.util
from pathlib import Path
import unittest
from jsonschema import ValidationError

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scenario_design_validator',ROOT/'scripts/validate_scenarios.py')
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)

class ScenarioDesignTests(unittest.TestCase):
    def test_real_refs_fixed_reports_and_all_entries_validate_without_execution(self):
        result=validator.validate_design()
        self.assertEqual(result['frontend_entries'],11)
        self.assertFalse(result['scenario_runtime_implemented']);self.assertFalse(result['ai_enabled'])

    def test_cannot_fake_bazi_provider_or_mismatch_variant(self):
        r=validator.read(ROOT/'config/scenarios/registry.json')
        dep=r['scenarios'][0]['dependencies'][0];dep['registered']=True;dep['variant']='invented-bazi'
        with self.assertRaises(ValueError):validator.validate_design(registry=r,check_board=False)

    def test_cannot_enable_scenario_ai_or_publish_from_design_config(self):
        r=validator.read(ROOT/'config/scenarios/registry.json')
        for key in ('ai_enabled','public_enabled','runtime_implemented'):
            bad=copy.deepcopy(r);bad['scenarios'][0][key]=True
            with self.assertRaises(ValidationError):validator.validate_design(registry=bad,check_board=False)

    def test_cannot_insert_default_score_or_mutate_computed_sample(self):
        p=validator.read(ROOT/'config/scenarios/prototypes.json')
        bad=copy.deepcopy(p);bad['prototypes'][6]['output_example']['comprehensive_index']['value']=60
        with self.assertRaises(ValueError):validator.validate_design(prototypes=bad,check_board=False)
        bad=copy.deepcopy(p);row=next(x for x in bad['prototypes'] if x['scenario_id']=='one_question')
        row['output_example']['facts'][0]['value']='伪造卦象'
        with self.assertRaises(ValueError):validator.validate_design(prototypes=bad,check_board=False)

    def test_cannot_use_unrelated_evidence_or_fake_dream_chart(self):
        r=validator.read(ROOT/'config/scenarios/registry.json')
        r['scenarios'][0]['evidence']['existing_structural_refs'][0]['rule_id']='dream.future.success'
        with self.assertRaises(ValueError):validator.validate_design(registry=r,check_board=False)
        p=validator.read(ROOT/'config/scenarios/prototypes.json')
        question=next(x for x in p['prototypes'] if x['scenario_id']=='one_question')
        dream=next(x for x in p['prototypes'] if x['scenario_id']=='dream')
        dream['output_example']['computed_engine_runs']=copy.deepcopy(question['output_example']['computed_engine_runs'])
        with self.assertRaises(ValueError):validator.validate_design(prototypes=p,check_board=False)
