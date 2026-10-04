#!/usr/bin/env python3
"""Local Qiniu calibration; prompt privately for a key, never persist credentials."""
import argparse
import getpass
import os
from pathlib import Path
import subprocess
import sys
import warnings
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://api.qnaigc.com/v1'


def calibration_environment(key):
    if not isinstance(key, str) or not key.strip():
        raise ValueError('credential_missing')
    environment = dict(os.environ)
    environment.update(TIANJI_AI_PROVIDER='openai-compatible', TIANJI_AI_BASE_URL=BASE_URL,
                       TIANJI_AI_API_KEY=key, TIANJI_AI_MODEL='', PYTHONUTF8='1',
                       PYTHONPATH=str(ROOT / 'src'))
    return environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluate', action='store_true', help='Run both fixed 102-case prompt suites after discovery (204 cases)')
    args = parser.parse_args()
    key = os.environ.get('TIANJI_AI_API_KEY', '')
    if not key:
        if not sys.stdin.isatty():
            print('Credential missing: set TIANJI_AI_API_KEY in the backend environment or run this in a local terminal')
            return 2
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', getpass.GetPassWarning)
                key = getpass.getpass('Qiniu API Key (hidden, this calibration process only): ')
        except (getpass.GetPassWarning, EOFError):
            print('Hidden credential input unavailable; configure the backend environment instead')
            return 2
    try:
        environment = calibration_environment(key)
    except ValueError:
        print('Credential missing; no provider contacted')
        return 2
    output = ROOT / 'build/provider-discovery' / uuid4().hex
    command = [sys.executable, str(ROOT / 'scripts/discover_explanation_model.py'), '--output', str(output)]
    if args.evaluate:
        command.append('--evaluate')
    result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    if args.evaluate:
        report = output / 'explanation-evals/explanation-prompt-v2.json'
        # Only use a report produced by this attempt; discovery/eval exit 2 means not run.
        if result.returncode in (0, 1) and report.is_file():
            review = subprocess.run([sys.executable, str(ROOT / 'scripts/review_explanations.py'),
                '--report', str(report), '--export-template', '--output',
                str(report.parent / 'human-review-v2.json')], cwd=ROOT, env=environment, check=False)
            if review.returncode:
                return review.returncode
        print('Human semantic review is still required; no public AI release enabled')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
