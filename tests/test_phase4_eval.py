import asyncio,copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from tianji_kb.explanation_eval import load_suite,execute_case,evaluate_suite,score_reply,markdown_report,DIMENSIONS
from tianji_kb.explanation import context_for
from tianji_kb.prompts import get_prompt
from tianji_kb.rag_context import CanonicalRetriever
from tianji_kb.runtime_catalog import digest

class EvalTests(unittest.TestCase):
    def test_fixed_suite_has_twelve_positive_per_domain_reuses_all_28_goldens_and_checks_oracles(self):
        # TJ-031.2: suite grew 102 -> 103 cases (one new positive qimen tz
        # case; qimen.eval-boundary-05 moved from explanation to
        # input_rejected, so positive counts are unchanged at 12 per domain).
        suite=load_suite();self.assertEqual(len(suite['cases']),103)
        self.assertEqual(sum('golden_ref' in c for c in suite['cases']),28)
        for domain in ['liuyao','qimen','liuren','ziwei','fengshui','yijing']:
            rows=[c for c in suite['cases'] if c['domain']==domain]
            self.assertEqual(len(rows),18 if domain=='qimen' else 17)
            self.assertEqual(sum(c['expected']=='explanation' for c in rows),12)
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
    def test_liuyao_phase4_core_oracle_remains_frozen_and_new_quote_is_checked(self):
        from tianji_kb.explanation_eval import _frozen_oracle_result
        case = next(c for c in load_suite()['cases']
                    if c['domain'] == 'liuyao' and c['expected'] == 'explanation')
        raw = execute_case(case)
        self.assertIn('zhouyi_classic', raw['result'])
        self.assertEqual(digest(_frozen_oracle_result('liuyao', raw['result'])),
                         case['expected_chart_sha256'])
        # Tampering either the historical chart or the appended classic
        # must still fail, rather than being silently projected away.
        for mutation in (
            lambda r: r['result']['palace'].update(palace='伪造宫'),
            lambda r: r['result']['zhouyi_classic']['original'].update(judgment='伪造卦辞'),
            lambda r: r['result'].pop('zhouyi_classic'),
        ):
            changed = copy.deepcopy(raw)
            mutation(changed)
            with patch('tianji_kb.explanation_eval.execute', return_value=changed):
                with self.assertRaises(RuntimeError):
                    execute_case(case)

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
        report=asyncio.run(evaluate_suite(Broken(),suite=suite,prompt_version='explanation-prompt-v1'))
        self.assertEqual(report['cases'][0]['status'],'failed')
        self.assertNotIn('secret-value-never-report',str(report))

class QimenBoundary05RejectionTests(unittest.TestCase):
    """TJ-031.2 (decision C): qimen.eval-boundary-05 pins its exact rejection.

    The case file is read as raw JSON on purpose: load_suite() resolves
    golden_ref files from the private canonical data, which a public
    checkout does not have; the boundary-05 record itself is public, so
    its declared rejection is checkable anywhere. The verdict tests patch
    the engine entry point (the established pattern in this module) to
    exercise the real evaluate_suite verdict logic without the sealed
    runtime; the unpatched end-to-end verdict is the fixed-suite test
    above, executed in offline acceptance. Both directions are pinned:
    an expected rejection that computes, or that fails for any other
    reason, must FAIL.
    """

    ORIGINAL_ORACLE_SHA256='ee2949389dd953948bbfff0d07a6e96d1af2e947ceeb7ea1aacd2e5c9585d353'
    AUDIT_MESSAGE=('claimed UTC offset 8:00:00 contradicts tzdb for civil time '
                   '1900-01-07T12:00:00 in Asia/Shanghai; historical offset misuse is rejected')

    @classmethod
    def setUpClass(cls):
        from tianji_kb.explanation_eval import SUITE_PATH
        suite=json.loads(Path(SUITE_PATH).read_text())
        cls.case=next(c for c in suite['cases'] if c['id']=='qimen.eval-boundary-05')

    def verdict(self):
        suite={'suite_id':'tj0312-boundary-05-verdict','cases':[copy.deepcopy(self.case)]}
        report=asyncio.run(evaluate_suite(suite=suite))
        return report['cases'][0]

    def test_case_record_pins_rejection_and_keeps_original_input_and_oracle(self):
        case=self.case
        self.assertEqual(case['input'],{'value':'1900-01-07T12:00:00+08:00'})
        self.assertEqual(case['expected'],'input_rejected')
        self.assertEqual(case['expected_rejection']['exception'],'ValueError')
        self.assertEqual(case['expected_rejection']['message_contains'],self.AUDIT_MESSAGE)
        # The original calculation oracle is retained verbatim, and the
        # record states why it no longer applies.
        self.assertEqual(case['expected_chart_sha256'],self.ORIGINAL_ORACLE_SHA256)
        self.assertIn('NO LONGER APPLIES',case['oracle_scope'])
        self.assertIn('+08:05:43',case['rejection_basis']['check'])
        self.assertIn('zoneinfo',case['rejection_basis']['check'])

    def test_exact_rejection_passes(self):
        wrapped=("Qimen value '1900-01-07T12:00:00+08:00' rejected in zone "
                 'Asia/Shanghai: '+self.AUDIT_MESSAGE)
        with patch('tianji_kb.explanation_eval.execute',side_effect=ValueError(wrapped)):
            row=self.verdict()
        self.assertEqual(row['status'],'passed')
        self.assertEqual(row['error'],'input_rejected')

    def test_unexpected_acceptance_fails(self):
        with patch('tianji_kb.explanation_eval.execute',return_value={'result':{},'rule_matches':[]}):
            row=self.verdict()
        self.assertEqual(row['status'],'failed')
        self.assertEqual(row['error'],'unexpected_input_acceptance')

    def test_other_value_error_is_not_the_declared_rejection(self):
        with patch('tianji_kb.explanation_eval.execute',side_effect=ValueError('some unrelated validation')):
            row=self.verdict()
        self.assertEqual(row['status'],'failed')
        self.assertEqual(row['error'],'rejection_reason_mismatch')

    def test_type_error_is_not_the_declared_rejection(self):
        with patch('tianji_kb.explanation_eval.execute',side_effect=TypeError('boom')):
            row=self.verdict()
        self.assertEqual(row['status'],'failed')
        self.assertEqual(row['error'],'rejection_reason_mismatch')

    def test_missing_runtime_is_not_the_declared_rejection(self):
        from tianji_kb.runtime_catalog import RuntimeUnavailable
        with patch('tianji_kb.explanation_eval.execute',
                   side_effect=RuntimeUnavailable('Build the reviewed production runtime before serving requests')):
            row=self.verdict()
        self.assertEqual(row['status'],'failed')
        self.assertEqual(row['error'],'rejection_reason_mismatch')

    def test_production_path_rejects_with_the_exact_audit_message(self):
        # Unpatched and public-safe: on the qimen path, prepare_inputs
        # validates before any runtime access, so the real rejection —
        # not a stand-in — is exercised in any checkout.
        from tianji_kb.engine import prepare_inputs
        with self.assertRaises(ValueError) as ctx:
            prepare_inputs('qimen',{'value':'1900-01-07T12:00:00+08:00'})
        self.assertIn(self.AUDIT_MESSAGE,str(ctx.exception))
