#!/usr/bin/env python3
"""Offline checks for a scoped deterministic backend, never a model quality score."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

from tianji_kb.ai_providers import provider_configured, settings_from_environment
from tianji_kb.explanation import ExplanationFailure
from tianji_kb.engine import PROVIDERS
from tianji_kb.golden import run_cases
from tianji_kb.knowledge import read_json, validate_protected_files
from tianji_kb.resolver import EvidenceResolver
from tianji_kb.runtime_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]


def configuration_status():
    """Only presence flags and fixed status codes; no credential/endpoint/model values."""
    fields = ('TIANJI_AI_PROVIDER', 'TIANJI_AI_BASE_URL', 'TIANJI_AI_MODEL', 'TIANJI_AI_API_KEY')
    status = {'environment_present': {name: bool(os.environ.get(name)) for name in fields},
              'configured_for_explanation': provider_configured()}
    try:
        settings = settings_from_environment(require_model=False)
        status['calibration_configuration'] = 'ready' if settings else 'disabled'
    except (ExplanationFailure, ValueError) as error:
        status['calibration_configuration'] = error.code if isinstance(error, ExplanationFailure) else 'provider_configuration_invalid'
    # A key/model setting and even a passing connection probe do not prove quality.
    status.update(quality_checked=False, real_pass_rate=None, hallucination_rate=None,
                  human_semantic_review='not_checked', automatic_release_allowed=False)
    return status


def check_backend(root=ROOT):
    root = Path(root)
    checks = {}
    report = {'schema_version': '1.0', 'check_kind': 'offline_deterministic_readiness',
              'checks': checks, 'deterministic_backend_ready': False,
              'bazi_execution_available': False, 'ai': configuration_status(),
              'scope': 'Registered variants and fixed regression cases only; not unrestricted divination accuracy'}
    try:
        validate_protected_files(root)
        checks['protected_bytes'] = True
        payload = load_catalog(root)
        checks['runtime_integrity'] = True
        checks['registered_domains'] = set(payload['contracts']) == set(PROVIDERS)
        report['bazi_execution_available'] = 'bazi' in payload['contracts']
        rag = root / 'build/production_rag.jsonl'
        checks['reviewed_rag_integrity'] = rag.is_file() and hashlib.sha256(rag.read_bytes()).hexdigest() == payload['retrieval_index_sha256']
        manifest = read_json(root / 'config/public_domain_manifest.json')
        sanming = next(work for source in manifest['sources'] for work in source['works'] if work['id'] == 'sanming_tonghui')
        blockers = sanming['quality_blockers']
        checks['sanming_quarantine'] = (sanming['promotion'] == 'quarantine_only'
            and blockers['canonical_ready'] is False
            and not (root / sanming['planned_output']).exists())
        report['sanming'] = {'promotion': sanming['promotion'], 'canonical_ready': blockers['canonical_ready'],
            'confirmed_text_corrections': blockers['confirmed_text_corrections'],
            'pua': {name: blockers[name] for name in ('confirmed_private_use_mappings', 'confirmed_occurrences',
                'remaining_unique_private_use_chars', 'remaining_private_use_chars')},
            'basis': 'Manifest metadata; full collation assertions run separately in test_domains'}
        resolver = EvidenceResolver(root)
        cases = run_cases(root)
        checks['golden_cases'] = bool(cases) and all(case['passed'] for case in cases)
        levels = Counter(source['evidence_level'] for source in resolver.sources.values())
        report['source_grades'] = {grade: levels[grade] for grade in 'ABCD'}
        report['golden_cases_passed'] = len(cases)
        report['domains'] = {domain: {'variant': contract['variant'], 'scope': contract.get('scope', ''),
            'limitations': contract.get('unresolved', []), 'golden_cases': sum(case['domain'] == domain for case in cases)}
            for domain, contract in sorted(resolver.contracts.items())}
        report['deterministic_backend_ready'] = all(checks.values())
    except (OSError, ValueError, KeyError, TypeError, AssertionError, StopIteration):
        # Do not echo exceptions or repository/provider values into operational logs.
        report['error'] = 'backend_check_failed'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/backend-readiness.json')
    args = parser.parse_args()
    report = check_backend()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Deterministic backend:', 'ready within reported scope' if report['deterministic_backend_ready'] else 'blocked')
    print('AI calibration configuration:', report['ai']['calibration_configuration'])
    print('Model quality not checked; automatic AI release remains disabled')
    return 0 if report['deterministic_backend_ready'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
