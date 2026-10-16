"""TJ-010.2: Unified action condition matrix for bazi strength factors.

Builds on existing variants without replacing them:
- ditiansui-root-visibility-v1 (bazi_strength.factors)
- ditiansui-root-conditions-v1 (bazi_root_conditions.root_conditions)
- ditiansui-wood-root-availability-v1 (bazi_root_conditions.root_availability)
- ditiansui-action-conditions-v1 (bazi_action_conditions.action_conditions)
- ditiansui-bounded-action-effects-v1 (bazi_action_conditions.action_effects)

Output status semantics:
- observed: verified structural fact (pillar position, stem/branch values)
- candidate: has some basis but insufficient for effectiveness determination
- effective: meets reviewed sufficient action conditions (narrow, audited)
- unresolved: conflict exists or necessary basis missing
- not_applicable: confirmed not applicable to this chart

No weights. No overall strength classification. No 喜用神.
"""
from .bazi_core import PILLAR_NAMES, reviewed_relations
from .bazi_strength import factors as strength_factors, FACTOR_VARIANT
from .bazi_root_conditions import (
    root_conditions, root_availability,
    ROOT_VARIANT, AVAILABILITY_VARIANT,
)
from .bazi_action_conditions import (
    action_conditions, action_effects,
    ACTION_VARIANT, EFFECT_VARIANT,
)
from .bazi_commander import month_command, principal_month, COMMAND_VARIANT, PRINCIPAL_VARIANT

MATRIX_VARIANT = 'bazi-action-matrix-v1'


def build_matrix_from_chart(chart):
    """Build matrix from a real chart_from_datetime()/chart_from_pillars() output.

    Strict input validation (fail-closed):
    - chart must have 'pillars' (4, ordered year/month/day/hour)
    - chart must have 'day_master' with 'stem'
    - day_master must match day pillar stem
    - all stems/branches must be valid
    """
    from .bazi_core import STEMS, BRANCHES
    from .foundations import ganzhi_index
    pillars = chart.get('pillars')
    dm = chart.get('day_master', {})
    day_master = dm.get('stem')
    if not isinstance(pillars, list) or len(pillars) != 4:
        raise ValueError('Expected four pillars')
    if tuple(p.get('name') for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    if not day_master or day_master not in STEMS:
        raise ValueError('Invalid day_master stem')
    # Day master must match day pillar stem (input consistency)
    if pillars[2]['stem']['value'] != day_master:
        raise ValueError('day_master does not match day pillar stem')
    # Validate all stems and branches
    # P0-3: Use ganzhi_index to verify each pillar is a valid 60 Jiazi combination
    for p in pillars:
        s = p.get('stem', {}).get('value')
        b = p.get('branch', {}).get('value')
        if s not in STEMS:
            raise ValueError(f"Invalid stem: {s}")
        if b not in BRANCHES:
            raise ValueError(f"Invalid branch: {b}")
        # Verify the stem-branch combination is a valid Jiazi
        # ganzhi_index raises ValueError for invalid combinations
        try:
            ganzhi_index(s + b)
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"Invalid ganzhi combination: {s}{b} - not in 60 Jiazi") from e

    stems = [p['stem']['value'] for p in pillars]
    branches = [p['branch']['value'] for p in pillars]
    relations = reviewed_relations(stems, branches)

    # Month command (P0-1: must use real month_command, fail-closed on error)
    cmd = month_command(pillars, day_master, command_variant=COMMAND_VARIANT)

    # Principal month (P0-1: audited principal_qi relation for action_effects)
    principal = principal_month(cmd, day_master, command_variant=PRINCIPAL_VARIANT)

    # Strength factors -> support relations (pure structural, no resolver needed)
    strength = strength_factors(pillars, day_master, variant=FACTOR_VARIANT)

    # Root conditions (P0-2: fail-closed, no graceful degradation)
    roots = root_conditions(
        pillars, day_master,
        relations=relations, month_command=cmd,
        root_variant=ROOT_VARIANT)

    # Root availability (P0-2: fail-closed)
    availability = root_availability(roots, root_variant=AVAILABILITY_VARIANT)

    # Action conditions (structural, uses support which is resolver-free)
    actions = action_conditions(
        pillars, day_master,
        support=strength['support_relations'],
        relations=relations, month_command=cmd,
        action_variant=ACTION_VARIANT)

    # Action effects (P0-2: fail-closed, uses principal_month output)
    effects = action_effects(
        pillars,
        observed=actions,
        relations=relations,
        principal=principal,
        availability=availability,
        action_variant=EFFECT_VARIANT)

    return _assemble(
        pillars, day_master, roots, availability, actions, effects, cmd)


def _assemble(pillars, day_master, roots, availability, actions, effects, cmd):
    """Assemble the unified matrix with 5-state statuses."""
    # --- Roots matrix with real availability ---
    # availability['roots'] has per-root availability status
    avail_by_index = {r['root_index']: r for r in availability['roots']}
    root_rows = []
    for i, r in enumerate(roots['roots']):
        fact = r['fact']
        avail = avail_by_index.get(i, {})
        avail_status = avail.get('root_availability', 'unresolved')
        # A structural root remains visible, but an unresolved branch
        # interaction forbids promoting its *availability* to a candidate.
        # Keep the upstream availability and blockers for inspection.
        if r['conditions']['branch_relations']:
            status = 'unresolved'
            reason = 'branch_interaction_effect_unresolved'
        elif avail_status == 'effective':
            status = 'effective'
            reason = 'reviewed_sufficient_conditions'
        elif avail_status == 'conditional':
            status = 'candidate'
            reason = 'conditional_' + ','.join(avail.get('blockers', []))
        else:
            status = 'unresolved'
            reason = 'unresolved_' + ','.join(avail.get('blockers', ['no_basis']))
        root_rows.append({
            'pillar': fact['pillar'],
            'branch': fact['branch'],
            'hidden_stem': fact['hidden_stem'],
            'same_stem': fact['same_stem'],
            'is_month_position': fact['is_month_position'],
            'principal_qi_match': fact['principal_qi_match'],
            'exposed_visible_pillars': fact['exposed_visible_pillars'],
            'availability': avail_status,
            'status': status,
            'status_reason': reason,
            'rule_variant': AVAILABILITY_VARIANT,
        })

    # --- Exposures (透干) matrix ---
    exposure_rows = []
    for h in actions['hidden_relations']:
        fact = h['fact']
        targets = fact['visible_same_stem_pillars']
        status = 'observed' if targets else 'not_applicable'
        exposure_rows.append({
            'hidden_pillar': fact['pillar'],
            'branch': fact['branch'],
            'hidden_stem': fact['stem'],
            'element': fact['element'],
            'relation': fact['relation'],
            'ten_god': fact['ten_god'],
            'exposed_in': targets,
            'status': status,
            'status_reason': 'stem_exposed_in_visible' if targets
                             else 'no_visible_counterpart',
        })

    # --- Actions matrix with real effects ---
    # effects['visible_relations'] has effect_status per relation
    effect_by_index = {e['action_index']: e for e in effects['visible_relations']}
    action_rows = []
    for i, v in enumerate(actions['visible_relations']):
        fact = v['fact']
        eff = effect_by_index.get(i, {})
        eff_status = eff.get('effect_status', 'unresolved')
        # Map to 5-state
        if eff_status == 'effective_in_reviewed_context':
            status = 'effective'
            reason = 'reviewed_context_' + str(eff.get('context'))
        else:
            # Check for conflicts
            cond = v['conditions']
            has_conflict = bool(cond['root_branch_relations']) or bool(cond['stem_combinations'])
            status = 'unresolved' if has_conflict else 'candidate'
            reason = 'interaction_conflict' if has_conflict else 'direction_observed_effect_unresolved'
        action_rows.append({
            'pillar': fact['pillar'],
            'stem': fact['stem'],
            'element': fact['element'],
            'relation': fact['relation'],
            'ten_god': fact['ten_god'],
            'pillar_distance_to_day': fact['pillar_distance_to_day'],
            'adjacent_to_day': fact['adjacent_to_day'],
            'rooted_visible_candidate': fact['rooted_visible_candidate'],
            'status': status,
            'status_reason': reason,
            'rule_variant': EFFECT_VARIANT,
        })

    # Summary
    all_rows = root_rows + exposure_rows + action_rows
    summary = {}
    for row in all_rows:
        summary[row['status']] = summary.get(row['status'], 0) + 1

    return {
        'matrix_variant': MATRIX_VARIANT,
        'day_master': day_master,
        'factor_variant': FACTOR_VARIANT,
        'root_variant': ROOT_VARIANT,
        'availability_variant': AVAILABILITY_VARIANT,
        'action_variant': ACTION_VARIANT,
        'effect_variant': EFFECT_VARIANT,
        'command_variant': COMMAND_VARIANT,
        'roots': root_rows,
        'exposures': exposure_rows,
        'actions': action_rows,
        'summary': summary,
        'pure_support_met': effects.get('pure_support_scope_met', False),
        'isolated_control_met': effects.get('isolated_control_scope_met', False),
        'overall_strength': None,
        'weights_available': False,
        'scope': '通根可用性、透干对应、生扶克泄作用条件的统一矩阵；'
                 'effective仅限已审核充分条件，其余为candidate/unresolved；'
                 '不计算权重，不作整体旺衰判断。',
    }
