"""Product release checks reusing existing Evidence/Rule/AI policy; no new inference."""
import copy
import hashlib
import json
from pathlib import Path

from .explanation import context_for, validate_reply, ExplanationFailure
from .explanation_policy import preflight
from .knowledge import read_json
from .prompts import get_prompt
from .resolver import EvidenceResolver
from .runtime_catalog import digest


PRODUCT_PROMPT = 'explanation-prompt-v3'


def _reject(code):
    raise ExplanationFailure(code)


def validate_calculation_basis(root, raw, *, resolver=None):
    """Only server-computed results enter here; this does not replace chart execution."""
    root = Path(root).resolve()
    preflight(raw)
    if raw.get('deterministic') is not True:
        _reject('deterministic_fact_missing')
    resolver = resolver or EvidenceResolver(root, review_sources=True)
    contract = resolver.contracts.get(raw['domain'])
    if not contract or contract['variant'] != raw['variant']:
        _reject('variant_policy_mismatch')
    actual_rules = {r['id']: r for r in contract['rules']}
    golden = read_json(root / f"data/canonical/{raw['domain']}/phase2_golden.json")
    golden_cases = {c['id']: c for c in golden['cases']}
    for match in raw['rule_matches']:
        r = actual_rules.get(match['rule_id'])
        if not r or r['execution_status'] != 'executable' or r['validation_status'] != 'validated':
            _reject('rule_not_executable')
        if not r['golden_case_ids'] or any(cid not in golden_cases or golden_cases[cid]['variant'] != raw['variant'] for cid in r['golden_case_ids']):
            _reject('golden_case_missing')
        expected = {hashlib.sha256(json.dumps(ref, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]: ref
                    for ref in resolver.resolve(r['id'], raw['variant'])}
        for eid in match['evidence_ids']:
            if eid not in expected or digest(raw['evidence'][eid]) != digest(expected[eid]):
                _reject('citation_rejected')
            if raw['evidence'][eid]['evidence_level'] not in ('A', 'B', 'C'):
                _reject('insufficient_evidence')
        if set(match['evidence_ids']) != set(expected):
            _reject('evidence_grounding_missing')
    # Contract unresolved may describe unsupported features. No conclusion may
    # resolve them; product-specific whitelists must exclude those features.
    verified_raw = copy.deepcopy(raw)
    verified_raw['scope'] = contract.get('scope', '')
    verified_raw['unresolved'] = contract.get('unresolved', [])
    return context_for(verified_raw, [], PRODUCT_PROMPT)


def product_preflight(root, product_id, raw):
    """Run BEFORE model invocation. Current derived report authorizes no products."""
    root = Path(root).resolve()
    report = read_json(root / 'data/product/knowledge_coverage.json')
    if report.get('_audit', {}).get('publication_authority') is not False:
        _reject('product_coverage_invalid')
    for ref in report['_audit']['input_files']:
        path = (root / ref['path']).resolve()
        if not path.is_relative_to(root) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
            _reject('product_coverage_stale')
    product = report.get(product_id)
    if not product or product_id.startswith('_'):
        _reject('unknown_product')
    # The report is derived, not an authorization contract. Opening a product
    # requires a reviewed Scenario and existing AI semantic-review artifacts;
    # no such product release contract exists in this repository yet.
    if not product['production_ready'] or not product['public_enabled'] or not product['production_claims']:
        _reject('product_claim_unavailable')
    scenarios = read_json(root / 'config/scenarios/registry.json')
    scenario = next((s for s in scenarios['scenarios'] if s['scenario_id'] == product['scenario_id']), None)
    if not scenario or not all(scenario[k] is True for k in ('runtime_implemented', 'public_enabled', 'ai_enabled')):
        _reject('scenario_claim_unavailable')
    if product['ai_enabled'] is not True:
        _reject('ai_quality_not_approved')
    # Do not trust edited booleans in a derived JSON report as human/model review.
    # Intentionally closed until an existing-model product release is reviewed.
    _reject('product_release_contract_missing')


def validate_product_reply(root, product_id, raw, reply, *, rag_rows):
    """Server-controlled inputs only; no browser-supplied raw chart/whitelist."""
    product_preflight(root, product_id, raw)
    context = validate_calculation_basis(root, raw)
    if not rag_rows:
        _reject('insufficient_evidence')
    context['rag'] = copy.deepcopy(rag_rows)
    if reply.get('prompt_version') != PRODUCT_PROMPT or reply.get('prompt_sha256') != get_prompt(PRODUCT_PROMPT)['sha256']:
        _reject('prompt_version_mismatch')
    # Existing fact, RuleMatch, citation, scope and uncertainty checks; this
    # function remains unreachable for public products until release governance.
    return validate_reply(reply, context)


class ProductExplanationService:
    """Future Scenario integration boundary; unavailable products never call AI."""
    def __init__(self, root, provider, *, retriever=None, timeout=20):
        from .explanation import ExplanationService
        self.root = Path(root).resolve()
        self.service = ExplanationService(provider, retriever=retriever, timeout=timeout,
                                          prompt_version=PRODUCT_PROMPT)

    async def explain(self, product_id, raw):
        product_preflight(self.root, product_id, raw)
        validate_calculation_basis(self.root, raw)
        return await self.service.explain(raw)
