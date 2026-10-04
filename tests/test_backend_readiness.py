import importlib.util
import asyncio
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
import httpx

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


readiness = script('check_backend_readiness')
calibration = script('calibrate_qiniu')
evaluation = script('evaluate_explanations')
with patch.object(sys,'path',[str(ROOT/'scripts'),*sys.path]):
    session = script('qiniu_calibration_session')


class BackendReadinessTests(unittest.TestCase):
    def test_private_model_override_is_bound_to_exact_job_and_cannot_override_normal_eval_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);job_id='b'*32
            session_path=root/'build/provider-discovery'/('a'*32);session_path.mkdir(parents=True)
            request=session_path/'job-model.json'
            request.write_text(json.dumps({'job_id':job_id,'model':'qwen/test-flash'}))
            with patch.object(evaluation,'__file__',str(root/'scripts/evaluate_explanations.py')):
                self.assertEqual(evaluation.private_model_request(session_path/job_id),'qwen/test-flash')
                self.assertIsNone(evaluation.private_model_request(session_path/('c'*32)))
                self.assertIsNone(evaluation.private_model_request(root/'build/explanation-evals'/job_id))
                request.write_text(json.dumps({'job_id':job_id,'model':'qwen/test-flash','endpoint':'https://other.invalid'}))
                with self.assertRaises(ValueError):evaluation.private_model_request(session_path/job_id)

    def test_comparison_model_must_be_advertised_and_does_not_persist_key_or_change_original_settings(self):
        class Fake:
            settings={'driver':'openai-compatible','endpoint':'https://example.invalid/v1',
                      'key':'private-test-key','model':'original'}
            async def get(self,url):
                return {'data':[{'id':'qwen/test-flash'},{'id':'qwen/test-thinking-flash'},
                                {'id':'private-test-key'},{'id':'embedding-flash'}]}
        with tempfile.TemporaryDirectory() as directory:
            provider=Fake();original=provider.settings;output=Path(directory)
            model=asyncio.run(evaluation.select_comparison_model(provider,'lightweight',output))
            self.assertEqual(model,'qwen/test-flash');self.assertEqual(original['model'],'original')
            self.assertNotIn('private-test-key',(output/'model-selection.json').read_text())
            with self.assertRaises(ValueError):
                asyncio.run(evaluation.select_comparison_model(provider,'not-advertised',output))
            self.assertEqual(provider.settings['model'],'qwen/test-flash')

    def test_smoke_keeps_fixed_oracles_and_all_controls_without_full_suite_digest(self):
        from tianji_kb.explanation_eval import load_suite
        from tianji_kb.runtime_catalog import digest
        from collections import Counter
        suite=load_suite();smoke=evaluation.smoke_suite(suite)
        self.assertEqual(Counter(c['domain'] for c in smoke['cases'] if c['expected']=='explanation'),
            {domain:1 for domain in ('liuyao','qimen','liuren','ziwei','fengshui','yijing')})
        self.assertEqual([c for c in smoke['cases'] if c['expected']!='explanation'],
            [c for c in suite['cases'] if c['expected']!='explanation'])
        self.assertNotEqual(digest(smoke),digest(suite))
        self.assertTrue(all(c in suite['cases'] for c in smoke['cases']))

    def test_response_audit_excludes_body_headers_ids_and_nonstandard_metadata(self):
        result=evaluation.response_metadata({'id':'private-test-key','headers':{'authorization':'private-test-key'},
            'choices':[{'finish_reason':'private-test-key','message':{'content':'private-test-key',
                'reasoning_content':'private-test-key'}}],
            'usage':{'completion_tokens':27,'total_tokens':True,'api_key':'private-test-key'}})
        self.assertNotIn('private-test-key',json.dumps(result))
        self.assertEqual(result['finish_reason'],'unrecognized')
        self.assertEqual(result['usage'],{'completion_tokens':27})

    def test_private_session_rejects_arbitrary_commands_paths_and_unbounded_requests(self):
        good={'id':'a'*32,'kind':'smoke','domains':['yijing'],'timeout_seconds':90,'max_output_tokens':8192}
        args,timeout,tokens=session.job_arguments(good)
        self.assertIn('--smoke',args);self.assertEqual(timeout,'90');self.assertEqual(tokens,'8192')
        self.assertIn('qwen/test-flash',session.job_arguments({**good,'model':'qwen/test-flash'})[0])
        for change in ({'command':'private-test-key'},{'id':'../escape'},{'domains':['bazi']},
                       {'timeout_seconds':float('nan')},{'timeout_seconds':121},{'max_output_tokens':999999},
                       {'kind':'shell'},{'prompts':['unknown']},{'model':'../ path'},{'model':'embedding-flash'}):
            with self.assertRaisesRegex(ValueError,'^invalid_job$'):session.job_arguments({**good,**change})

    def test_transport_progress_cannot_echo_headers_or_error_body_and_is_not_quality_score(self):
        class Broken:
            async def explain(self,context):
                request=httpx.Request('POST','https://example.invalid',headers={'Authorization':'Bearer private-test-key'})
                response=httpx.Response(401,request=request,text='private-test-key')
                raise httpx.HTTPStatusError('private-test-key',request=request,response=response)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'progress.jsonl';output=io.StringIO()
            with contextlib.redirect_stdout(output):
                with self.assertRaises(httpx.HTTPStatusError):
                    asyncio.run(evaluation.ProgressProvider(Broken(),path,'explanation-prompt-v2').explain({'domain':'yijing'}))
            recorded=path.read_text();event=json.loads(recorded)
            self.assertNotIn('private-test-key',recorded+output.getvalue())
            self.assertEqual(event['http_status'],401)
            self.assertEqual(event['outcome'],'http_error')
            self.assertNotIn('passed',event)
            self.assertNotIn('quality',event)

    def test_offline_check_keeps_configured_model_unscored_and_never_contacts_network(self):
        env = {'TIANJI_AI_PROVIDER': 'openai-compatible', 'TIANJI_AI_BASE_URL': calibration.BASE_URL,
               'TIANJI_AI_MODEL': 'test-model', 'TIANJI_AI_API_KEY': 'private-test-key'}
        with patch.dict(os.environ, env), patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
            report = readiness.check_backend()
        self.assertTrue(report['deterministic_backend_ready'])
        self.assertEqual(set(report['domains']), {'liuyao', 'qimen', 'liuren', 'ziwei', 'fengshui', 'yijing'})
        self.assertFalse(report['bazi_execution_available'])
        self.assertTrue(report['ai']['configured_for_explanation'])
        self.assertFalse(report['ai']['quality_checked'])
        self.assertIsNone(report['ai']['real_pass_rate'])
        self.assertIsNone(report['ai']['hallucination_rate'])
        self.assertFalse(report['ai']['automatic_release_allowed'])
        self.assertNotIn('private-test-key', json.dumps(report))
        self.assertTrue(report['checks']['sanming_quarantine'])

    def test_invalid_environment_never_echoes_values(self):
        with patch.dict(os.environ, {'TIANJI_AI_PROVIDER': 'private-test-key'}, clear=True):
            result = readiness.configuration_status()
        self.assertEqual(result['calibration_configuration'], 'provider_configuration_invalid')
        self.assertNotIn('private-test-key', json.dumps(result))

    def test_missing_backend_blocks_and_damaged_rag_cannot_be_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertFalse(readiness.check_backend(Path(directory))['deterministic_backend_ready'])
        original = Path.read_bytes
        def corrupt(path):
            return b'corrupted' if path.name == 'production_rag.jsonl' else original(path)
        with patch.object(Path, 'read_bytes', corrupt):
            report = readiness.check_backend()
        self.assertFalse(report['checks']['reviewed_rag_integrity'])
        self.assertFalse(report['deterministic_backend_ready'])

    def test_calibration_key_is_child_environment_only_and_provider_is_fixed(self):
        with patch.dict(os.environ, {'TIANJI_AI_PROVIDER': 'disabled', 'TIANJI_AI_BASE_URL': 'https://other.invalid',
                                     'TIANJI_AI_MODEL': 'unverified'}, clear=True):
            environment = calibration.calibration_environment('private-test-key')
            self.assertNotIn('TIANJI_AI_API_KEY', os.environ)
            self.assertEqual(os.environ['TIANJI_AI_PROVIDER'], 'disabled')
        self.assertEqual(environment['TIANJI_AI_BASE_URL'], calibration.BASE_URL)
        self.assertEqual(environment['TIANJI_AI_PROVIDER'], 'openai-compatible')
        self.assertEqual(environment['TIANJI_AI_MODEL'], '')
        self.assertEqual(environment['TIANJI_AI_API_KEY'], 'private-test-key')
        with self.assertRaises(ValueError):
            calibration.calibration_environment('  ')

    def test_noninteractive_missing_key_stops_before_any_child_or_prompt(self):
        with patch.dict(os.environ, {}, clear=True), patch('sys.argv', ['calibrate_qiniu.py']), \
             patch('sys.stdin.isatty', return_value=False), patch.object(calibration.subprocess, 'run') as child, \
             patch.object(calibration.getpass, 'getpass') as prompt:
            self.assertEqual(calibration.main(), 2)
        child.assert_not_called()
        prompt.assert_not_called()

    def test_prompt_cannot_fall_back_to_visible_input(self):
        with patch.dict(os.environ, {}, clear=True), patch('sys.argv', ['calibrate_qiniu.py']), \
             patch('sys.stdin.isatty', return_value=True), patch.object(calibration.subprocess, 'run') as child, \
             patch.object(calibration.getpass, 'getpass', side_effect=calibration.getpass.GetPassWarning):
            self.assertEqual(calibration.main(), 2)
        child.assert_not_called()

    def test_child_arguments_have_no_key_and_failed_discovery_cannot_export_stale_review(self):
        outputs = []
        def child(command, **kwargs):
            self.assertNotIn('private-test-key', ' '.join(command))
            self.assertEqual(kwargs['env']['TIANJI_AI_API_KEY'], 'private-test-key')
            self.assertEqual(Path(command[1]).name, 'discover_explanation_model.py')
            output = command[command.index('--output') + 1]
            outputs.append(output)
            return type('Result', (), {'returncode': 2})()
        with patch.dict(os.environ, {'TIANJI_AI_API_KEY': 'private-test-key'}, clear=True), \
             patch('sys.argv', ['calibrate_qiniu.py', '--evaluate']), \
             patch.object(calibration.subprocess, 'run', side_effect=child):
            self.assertEqual(calibration.main(), 2)
            self.assertEqual(calibration.main(), 2)
        self.assertEqual(len(outputs), 2)
        self.assertNotEqual(outputs[0], outputs[1])


if __name__ == '__main__':
    unittest.main()
