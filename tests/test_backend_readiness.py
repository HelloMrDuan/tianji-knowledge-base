import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


readiness = script('check_backend_readiness')
calibration = script('calibrate_qiniu')


class BackendReadinessTests(unittest.TestCase):
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
