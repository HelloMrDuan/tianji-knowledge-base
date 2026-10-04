"""Reviewed structural claim bindings over existing Scenario RuleMatch facts.

This is a presentation contract, not a second knowledge base. It neither computes
charts nor authorizes AI. Full predictions are deliberately absent. Empty lists
are valid negative structural observations, not missing data.
"""
import copy
import hashlib
import json


def _binding(match, rules, path='', kind=None):
    return {'match_rule_id': match, 'execution_rule_ids': rules,
            'fact_path': path, 'filter_kind': kind, 'scope': 'deterministic_structure_only'}


B = 'bazi.phase2.'
SCENARIO_CLAIMS = {
    'bazi-profile': {
        'bazi.pillars': _binding(B + 'pillars', [B + 'pillars'], '/ganzhi'),
        'bazi.day_master': _binding(B + 'pillars', [B + 'pillars'], '/day_master'),
        'bazi.ten_gods': _binding(B + 'ten_gods', [B + 'ten_gods']),
        'bazi.hidden_stems': _binding(B + 'hidden_stems', [B + 'hidden_stems']),
    },
    'romance': {
        'romance.xianchi_structure': _binding('bazi.scenario.xianchi_structure', [B + 'xianchi_lookup']),
    },
    'daily': {
        'fortune.day_structure': _binding('bazi.scenario.daily_structure', [B + 'ten_gods', B + 'xianchi_lookup']),
    },
    'weekly': {
        'fortune.week_structure': _binding('bazi.scenario.weekly_structure', [B + 'ten_gods', B + 'xianchi_lookup']),
    },
    'monthly': {
        'fortune.civil_month_structure': _binding('bazi.scenario.monthly_structure', [B + 'ten_gods', B + 'xianchi_lookup']),
    },
    'yearly': {
        'fortune.year_stem_structure': _binding('bazi.scenario.flow_stem_ten_god', [B + 'ten_gods']),
    },
    'career': {
        'career.ten_god_positions': _binding('bazi.scenario.career_wealth_structure', [B + 'ten_gods', B + 'hidden_stems']),
    },
    'compatibility': {
        'compatibility.a_sees_b': _binding('bazi.scenario.compatibility_structure', [B + 'ten_gods'], '/a_sees_b_ten_god'),
        'compatibility.b_sees_a': _binding('bazi.scenario.compatibility_structure', [B + 'ten_gods'], '/b_sees_a_ten_god'),
        'relationship.stem_combination': _binding('bazi.scenario.compatibility_structure', [B + 'stem_five_combinations'], '/day_master_five_combination'),
        'relationship.branch_clash': _binding('bazi.scenario.compatibility_structure', [B + 'branch_six_clashes'], '/spouse_palace_relation/relations', 'clash'),
        'relationship.branch_harmony': _binding('bazi.scenario.compatibility_structure', [B + 'branch_six_harmonies'], '/spouse_palace_relation/relations', 'six_harmony'),
        'relationship.branch_harm': _binding('bazi.scenario.compatibility_structure', [B + 'branch_six_harms'], '/spouse_palace_relation/relations', 'harm'),
        'compatibility.cross_matrix_structure': _binding('bazi.scenario.compatibility_structure', [B + 'stem_five_combinations', B + 'branch_six_harmonies', B + 'branch_six_clashes', B + 'branch_six_harms'], '/cross_relation_matrix_summary'),
    },
    'life': {
        'bazi.pillars': _binding(B + 'pillars', [B + 'pillars'], '/ganzhi'),
        'bazi.day_master': _binding(B + 'pillars', [B + 'pillars'], '/day_master'),
        'romance.xianchi_structure': _binding('bazi.scenario.xianchi_structure', [B + 'xianchi_lookup']),
        'career.ten_god_positions': _binding('bazi.scenario.career_wealth_structure', [B + 'ten_gods', B + 'hidden_stems']),
    },
}

# Every liuyao calculation RuleMatch already has reviewed evidence and a Golden.
SCENARIO_CLAIMS['question'] = {
    'liuyao.' + name: _binding('liuyao.phase2.' + name, ['liuyao.phase2.' + name])
    for name in ('najia', 'relatives', 'palace', 'spirits', 'empty', 'month_break', 'motion')
}


def ready_bindings(scenario_id, engines):
    """Fail on stale bindings; never upgrade undocumented engine output."""
    result = copy.deepcopy(SCENARIO_CLAIMS.get(scenario_id, {}))
    known = {r['id'] for e in engines.values() for r in e['rules']}
    for item in result.values():
        if not set(item['execution_rule_ids']) <= known:
            raise ValueError('Claim binding references unknown execution Rule')
    return result


def bind_structural_claim(raw, claim_id, resolver):
    """Server-computed Scenario result only. No client-supplied raw or whitelist.

    Validate the actual fired rule, current Variant, Golden bindings and exact
    citations. The returned value is copied directly from RuleMatch facts.
    """
    binding = SCENARIO_CLAIMS.get(raw.get('scenario_id'), {}).get(claim_id)
    if not binding or raw.get('deterministic') is not True or raw.get('source_conflicts'):
        raise ValueError('claim_unavailable')
    matches = [m for m in raw.get('rule_matches', []) if m['rule_id'] == binding['match_rule_id'] and m.get('matched') is True]
    if len(matches) != 1:
        raise ValueError('claim_rule_not_fired')
    match = matches[0]
    declared = match.get('derived_from_rule_ids', [])
    if match.get('derived_from_rule_id'):
        declared = [*declared, match['derived_from_rule_id']]
    if match.get('kind') == 'scenario_composition' and not set(binding['execution_rule_ids']) <= set(declared):
        raise ValueError('claim_composition_mismatch')
    expected = {}
    for rid in binding['execution_rule_ids']:
        rule = resolver.rule(rid)
        domain = rule['domain']
        contract = resolver.contracts[domain]
        if match.get('variant') != contract['variant'] or rule['validation_status'] != 'validated' or rule['execution_status'] != 'executable':
            raise ValueError('claim_variant_or_rule_unavailable')
        from .knowledge import read_json
        cases = {c['id']: c for c in read_json(resolver.root / f'data/canonical/{domain}/phase2_golden.json')['cases']}
        if not rule['golden_case_ids'] or any(g not in cases or cases[g]['variant'] != rule['variant'] for g in rule['golden_case_ids']):
            raise ValueError('claim_golden_missing')
        for ref in resolver.resolve(rid, match['variant']):
            if ref['evidence_level'] not in ('A', 'B', 'C'):
                raise ValueError('claim_evidence_unreviewed')
            key = hashlib.sha256(json.dumps(ref, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]
            expected[key] = ref
    for eid, ref in expected.items():
        if eid not in match.get('evidence_ids', []) or raw.get('evidence', {}).get(eid) != ref:
            raise ValueError('claim_evidence_mismatch')
    value = match['facts']
    try:
        for token in binding['fact_path'].split('/')[1:]:
            value = value[int(token)] if isinstance(value, list) else value[token]
    except (KeyError, IndexError, ValueError, TypeError) as error:
        raise ValueError('claim_fact_missing') from error
    if value is None:
        raise ValueError('claim_fact_missing')
    if binding['filter_kind']:
        value = [row for row in value if row['kind'] == binding['filter_kind']]
    return {'claim_id': claim_id, 'scope': binding['scope'], 'fact_value': copy.deepcopy(value),
            'match_rule_id': match['rule_id'], 'rule_ids': binding['execution_rule_ids'],
            'variant': match['variant'], 'evidence': expected, 'ai_enabled': False}
