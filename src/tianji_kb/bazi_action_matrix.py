"""TJ-010.2: Unified action condition matrix for bazi strength factors.

Builds on existing variants without replacing them:
- ditiansui-root-visibility-v1 (bazi_strength.factors)
- ditiansui-root-conditions-v1 (bazi_root_conditions.root_conditions)
- ditiansui-action-conditions-v1 (bazi_action_conditions.action_conditions)

Output status semantics (per TJ-010.2 Work B):
- observed: verified structural fact (pillar position, stem/branch values)
- candidate: has some basis but insufficient for effectiveness determination
- effective: meets reviewed sufficient action conditions
- unresolved: conflict exists or necessary basis missing
- not_applicable: confirmed not applicable to this chart

No weights. No overall strength classification. No 喜用神.
"""
from .bazi_core import PILLAR_NAMES
from .bazi_strength import factors as strength_factors, FACTOR_VARIANT
from .bazi_root_conditions import root_conditions, ROOT_VARIANT
from .bazi_action_conditions import action_conditions, ACTION_VARIANT

MATRIX_VARIANT = 'bazi-action-matrix-v1'


def build_matrix(pillars, day_master, *, relations, month_command,
                 factor_variant=FACTOR_VARIANT,
                 root_variant=ROOT_VARIANT,
                 action_variant=ACTION_VARIANT):
    """Build the unified action condition matrix from real pillars.

    Returns a dict with:
    - roots: per-pillar root candidates with status
    - exposures: 透干 correspondences (hidden -> visible)
    - actions: per-relation action conditions with status
    - summary: counts by status
    """
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')

    # Reuse existing computations (do not reimplement)
    strength = strength_factors(pillars, day_master, variant=factor_variant)
    roots = root_conditions(
        pillars, day_master,
        relations=relations, month_command=month_command,
        root_variant=root_variant)
    actions = action_conditions(
        pillars, day_master,
        support=strength['support_relations'],
        relations=relations, month_command=month_command,
        action_variant=action_variant)

    # --- Roots matrix ---
    root_rows = []
    for r in roots['roots']:
        fact = r['fact']
        # Status: structural fact observed; effectiveness unresolved unless
        # explicitly adjudicated (which this matrix does not do)
        has_conflict = bool(r['conditions']['branch_relations'])
        status = 'unresolved' if has_conflict else 'candidate'
        root_rows.append({
            'pillar': fact['pillar'],
            'branch': fact['branch'],
            'hidden_stem': fact['hidden_stem'],
            'same_stem': fact['same_stem'],
            'is_month_position': fact['is_month_position'],
            'principal_qi_match': fact['principal_qi_match'],
            'exposed_visible_pillars': fact['exposed_visible_pillars'],
            'status': status,
            'status_reason': 'branch_interaction_unresolved' if has_conflict
                             else 'structural_candidate_only',
            'rule_variant': root_variant,
        })

    # --- Exposures (透干) matrix ---
    # For each hidden stem, which visible pillars expose it
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

    # --- Actions matrix ---
    action_rows = []
    for v in actions['visible_relations']:
        fact = v['fact']
        cond = v['conditions']
        has_conflict = bool(cond['root_branch_relations']) or bool(cond['stem_combinations'])
        status = 'unresolved' if has_conflict else 'candidate'
        action_rows.append({
            'pillar': fact['pillar'],
            'stem': fact['stem'],
            'element': fact['element'],
            'relation': fact['relation'],
            'ten_god': fact['ten_god'],
            'polarity': fact['polarity'],
            'pillar_distance_to_day': fact['pillar_distance_to_day'],
            'adjacent_to_day': fact['adjacent_to_day'],
            'rooted_visible_candidate': fact['rooted_visible_candidate'],
            'root_position_count': len(fact['root_positions']),
            'status': status,
            'status_reason': 'interaction_conflict' if has_conflict
                             else 'direction_observed_effect_unresolved',
            'rule_variant': action_variant,
        })
    for h in actions['hidden_relations']:
        fact = h['fact']
        action_rows.append({
            'pillar': fact['pillar'],
            'stem': fact['stem'],
            'element': fact['element'],
            'relation': fact['relation'],
            'ten_god': fact['ten_god'],
            'visibility': 'hidden',
            'status': 'candidate',
            'status_reason': 'hidden_direction_only',
            'rule_variant': action_variant,
        })

    # --- Summary ---
    all_rows = root_rows + exposure_rows + action_rows
    summary = {}
    for row in all_rows:
        summary[row['status']] = summary.get(row['status'], 0) + 1

    return {
        'matrix_variant': MATRIX_VARIANT,
        'day_master': day_master,
        'factor_variant': factor_variant,
        'root_variant': root_variant,
        'action_variant': action_variant,
        'roots': root_rows,
        'exposures': exposure_rows,
        'actions': action_rows,
        'summary': summary,
        'overall_strength': None,
        'weights_available': False,
        'scope': '通根候选、透干对应、生扶克泄方向的条件矩阵；'
                 'observed=结构事实，candidate=候选，effective=已审充分条件，'
                 'unresolved=冲突或依据不足，not_applicable=不适用；'
                 '不计算权重，不作整体旺衰判断。',
    }
