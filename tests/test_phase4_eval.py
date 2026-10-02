import asyncio,copy,unittest
from unittest.mock import patch
from tianji_kb.explanation_eval import load_suite,execute_case,evaluate_suite,score_reply,markdown_report,DIMENSIONS
from tianji_kb.explanation import context_for
from tianji_kb.prompts import get_prompt
from tianji_kb.rag_context import CanonicalRetriever
from tianji_kb.runtime_catalog import digest

class EvalTests(unittest.TestCase):
    def test_fixed_suite_has_twelve_positive_per_domain_reuses_all_28_goldens_and_checks_oracles(self):
        suite=load_suite();self.assertEqual(len(suite['cases']),102)
        self.assertEqual(sum('golden_ref' in c for c in suite['cases']),28)
        for domain in ['liuyao','qimen','liuren','ziwei','fengshui','yijing']:
            rows=[c for c in suite['cases'] if c['domain']==domain]
            self.assertEqual(len(rows),17);self.assertEqual(sum(c['expected']=='explanation' for c in rows),12)
            self.assertTrue({'boundary','variant_limitations','low_evidence'}<=set(t for c in rows for t in c['tags']))
            for case in rows:
                if case['expected']=='input_rejected':
                    with self.assertRaises((ValueError,TypeError)):execute_case(case)
                else:self.assertTrue(execute_case(case)['deterministic'])
    def test_dry_run_is_not_a_model_pass_or_zero_hallucinations(self):
        report=asyncio.run(evaluate_suite(domains=['yijing']))
        row=report['reports']['yijing']
        self.assertIsNone(row['pass_rate']);self.assertIsNone(row['hallucination_count'])
        self.assertIsNone(row['citation_accuracy']);self.assertFalse(row['online_ready'])
        self.assertFalse(report['real_model_evaluation']);self.assertIn('N/A',markdown_report(report))
    def test_oracle_drift_is_reported_without_mutating_engine(self):
        suite=copy.deepcopy(load_suite());case=next(c for c in suite['cases'] if c['expected']=='explanation')
        case['expected_chart_sha256']='changed';suite['cases']=[case]
        report=asyncio.run(evaluate_suite(suite=suite));self.assertEqual(report['cases'][0]['error'],'engine_oracle_drift')
    def test_prompt_v1_is_frozen_and_unknown_versions_rejected(self):
        prompt=get_prompt('explanation-prompt-v1')
        self.assertEqual(prompt['sha256'],'b831f0e70ad357f627fa5ad546edc3ba72c96c2585cd4f6196dcde7cc76b06af')
        with self.assertRaises(ValueError):get_prompt('latest-magic')
    def test_scoring_detects_structural_hallucination_and_does_not_certify_prose(self):
        case=next(c for c in load_suite()['cases'] if c['domain']=='yijing' and c['expected']=='explanation')
        raw=execute_case(case);context=context_for(raw,CanonicalRetriever().retrieve(raw));fact=next(iter(context['facts']))
        reply={k:context[k] for k in ['domain','variant','mode','chart_digest']}
        reply['claims']=[{'fact_ref':fact,'fact_value':'wrong','text':'不真实结论','evidence_ids':['invented'],'quotes':[],'rule_ids':['invented-rule']}]
        result=score_reply(reply,context)
        self.assertGreaterEqual(result['hallucination_count'],3);self.assertEqual(result['metrics']['chart_fidelity'],0)
        self.assertEqual(result['metrics']['unsupported_claim_rate'],1);self.assertEqual(set(result['metrics']),set(DIMENSIONS))
        self.assertEqual(result['semantic_review'],'required');self.assertFalse(result['passed'])
    def test_expected_refusal_not_confused_with_provider_failure(self):
        class Broken:
            async def explain(self,context):raise RuntimeError('secret-value-never-report')
        suite=copy.deepcopy(load_suite());suite['cases']=[next(c for c in suite['cases'] if c.get('context_fault')=='source_conflict')]
        report=asyncio.run(evaluate_suite(Broken(),suite=suite))
        self.assertEqual(report['cases'][0]['status'],'failed')
        self.assertNotIn('secret-value-never-report',str(report))
