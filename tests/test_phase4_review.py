import asyncio,copy,hashlib,json,unittest
from pathlib import Path
from phase4_helpers import MechanicalProvider
from tianji_kb.explanation_eval import evaluate_suite,markdown_report
from tianji_kb.explanation_review import review_template,apply_reviews,POSITIVE,NEGATIVE
from tianji_kb.runtime_catalog import digest
from tianji_kb.resolver import ROOT

class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=asyncio.run(evaluate_suite(MechanicalProvider(),prompt_version='explanation-prompt-v2',domains=['yijing'],model='synthetic-unit-fixture'))
    def document(self,report=None):
        document=review_template(report or self.report)
        for row in document['reviews']:
            row.update(reviewer='synthetic-unit-test-reviewer',reviewed_at='2026-10-02T00:00:00Z',notes='Synthetic passing review fixture; not a real human/model result',explanation_completeness=True)
            for claim in row['claims']:
                claim.update({field:True for field in POSITIVE});claim.update({field:False for field in NEGATIVE})
        return document
    def test_template_unscored_not_approval_and_all_claims_need_human_values(self):
        template=review_template(self.report)
        self.assertEqual(len(template['reviews']),12)
        self.assertTrue(all(c['chart_fidelity'] is None for row in template['reviews'] for c in row['claims']))
        with self.assertRaises(ValueError):apply_reviews(self.report,template)
        partial=self.document();partial['reviews'][0]['claims'].pop()
        with self.assertRaises(ValueError):apply_reviews(self.report,partial)
    def test_review_provenance_and_duplicates_rejected(self):
        for field,value in [('model','other-model'),('suite_sha256','changed'),('prompt_sha256','changed'),('evaluation_sha256','changed')]:
            doc=self.document();doc[field]=value
            with self.assertRaises(ValueError):apply_reviews(self.report,doc)
        for field in ['reply_sha256','context_sha256']:
            doc=self.document();doc['reviews'][0][field]='changed'
            with self.assertRaises(ValueError):apply_reviews(self.report,doc)
        doc=self.document();doc['reviews'].append(copy.deepcopy(doc['reviews'][0]))
        with self.assertRaises(ValueError):apply_reviews(self.report,doc)
    def test_tampered_observed_response_context_integrity_rejected(self):
        for key in ['model_reply','review_context']:
            report=copy.deepcopy(self.report);row=next(r for r in report['cases'] if 'reply_sha256' in r)
            row[key]['variant']='forged';doc=self.document(report)
            with self.assertRaises(ValueError):apply_reviews(report,doc)
    def test_perfect_test_provider_reviews_never_qualify_a_real_model(self):
        output=apply_reviews(self.report,self.document())
        self.assertEqual(output['reports']['yijing']['semantic_review'],'complete')
        self.assertEqual(output['reports']['yijing']['semantic_hallucination_count'],0)
        self.assertFalse(output['online_ready']);self.assertFalse(output['reports']['yijing']['online_ready'])
        self.assertIn('Human semantic metrics',markdown_report(output))
    def test_human_detected_prose_hallucination_blocks_qualification(self):
        # Synthetic metadata exercises release gates, never a live-model claim.
        report=copy.deepcopy(self.report);report.update(run_kind='configured_external_http',real_model_evaluation=True)
        doc=self.document(report);first=doc['reviews'][0]['claims'][0]
        first.update(evidence_grounding=False,hallucination=True,unsupported_claim=True,contradiction=True,notes='Synthetic semantic failure despite valid structural fields')
        output=apply_reviews(report,doc);row=output['reports']['yijing']
        self.assertFalse(row['online_ready']);self.assertEqual(row['semantic_hallucination_count'],1)
        self.assertEqual(row['semantic_contradiction_count'],1);self.assertEqual(row['semantic_unsupported_claims'],1)
    def test_partial_reviews_guard_failure_and_cherry_picked_cases_cannot_qualify(self):
        report=copy.deepcopy(self.report);report.update(run_kind='configured_external_http',real_model_evaluation=True)
        doc=self.document(report);doc['reviews'].pop()
        self.assertFalse(apply_reviews(report,doc)['online_ready'])
        report['cases'][-1]['status']='failed'
        self.assertFalse(apply_reviews(report,self.document(report))['online_ready'])
        report=copy.deepcopy(self.report);report.update(run_kind='configured_external_http',real_model_evaluation=True);report['cases'].pop()
        self.assertFalse(apply_reviews(report,self.document(report))['online_ready'])
    def test_full_synthetic_external_review_gate_is_exact_model_prompt_fixture_scope(self):
        report=copy.deepcopy(self.report);report.update(run_kind='configured_external_http',real_model_evaluation=True)
        output=apply_reviews(report,self.document(report))
        self.assertTrue(output['reports']['yijing']['online_ready'])
        self.assertEqual(output['reports']['yijing']['readiness'],'eligible_for_supervised_beta')
        self.assertIn('not all arbitrary user inputs',output['release_scope'])
    def test_phase4_baseline_still_freezes_original_domain_algorithms(self):
        manifest=json.loads((ROOT/'evals/explanations/engine-baseline-v1.json').read_text())
        self.assertEqual(manifest['baseline_main_sha'],'73cccbd9ee09f52d5075a1d32223d6dab5cb7ceb')
        # The v1 baseline records the historical Phase 3 dispatcher too. Later reviewed
        # domain registration may extend engine.py, but must not rewrite the six algorithms
        # whose outputs the Phase 4 evaluation suite was frozen against.
        frozen={name:expected for name,expected in manifest['algorithm_files'].items() if name!='src/tianji_kb/engine.py'}
        self.assertTrue(any('/operations/' in name for name in frozen))
        for name,expected in frozen.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected,name)
