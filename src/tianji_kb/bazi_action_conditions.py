"""Relation direction and its observed conditions, without assumed efficacy."""
from .bazi_core import PILLAR_NAMES, foundations
from .bazi_earth_roots import EARTH_CONSUMPTION_CONTRACT
from .bazi_fire_morphology import (
    BING_ALL_ROOT_BRANCHES, BING_HEAVY_ROOT_BRANCHES, BING_ROOT_POSITIONS)
from .bazi_metal_water_roots import METAL_WATER_ROOT_TABLES
from .foundations import stem_element
from .resolver import EvidenceResolver

ACTION_VARIANT = 'ditiansui-action-conditions-v1'
EFFECT_VARIANT = 'ditiansui-bounded-action-effects-v1'

# TJ-011.2: generating-month extension of the bounded pure-support scope.
# Reviewed within the SAME Source as the existing scope
# (bazi.source.ditiansui-spouse, C-grade single electronic lineage,
# daizhigev20 snapshot SHA256
# 6a875a317c7ba1012285ed12d3bfa5577b50c9fdfd568ece323a12feafe38795):
# Ren's Congwang definition (char 96521 / line 4905: "从旺者，四柱皆
# 比劫，无官杀之制，有印绶之生，旺之极者") requires peer stems with
# resource generation and no controlling force; unlike the Congqiang
# definition (char 96605) it does NOT require the month to be the day
# master's own element or season. The root table (chars 39967-40222 /
# line 1613) lists 亥 first among the heavy roots for Jia/Yi wood
# ("如甲乙逢亥寅卯之类是也"), and 亥's reviewed principal qi is 壬
# (section s034), whose relation to a wood day master is generates_me
# (Golden bazi.principal-generate). 亥's hidden stems are exactly 壬
# (generating) and 甲 (same element), so a support-only composition is
# satisfiable in this month, as it is in single-qi 卯. The sealed
# policy concept cannot be extended from public code, so this reviewed
# month set is declared here and cross-checked in the adjudication
# layer, mirroring how the 卯/酉 scope is already hardcoded beside the
# sealed pure_months / isolated_months policy values.
PURE_GENERATING_MONTHS = ('亥',)

# TJ-011.2 S2: pure-support extension to metal x You and water x Zi,
# per the general-strength scout (S2) and the S1 root-grading register
# (bazi_metal_water_roots, FORMS FORM_PURE_SUPPORT_METAL /
# FORM_PURE_GENERATING_WATER). The two forms are condition-by-condition
# isomorphic to the pure scope: the definitions (Congwang s047 /
# Congqiang s048) are element-generic. The sealed policy cannot be
# extended from public code (pure_months stays [Mao], the availability
# variant stays wood-scoped), so the reviewed month sets are declared
# here -- mirroring PURE_GENERATING_MONTHS above -- and root
# effectiveness is driven by the S1 register, mirroring the commanding
# form's register-based form_effective: a day root is form-effective
# iff its (day-master stem, branch) cell is graded heavy in the
# register (per_stem_listed or framework_derived) and the executed
# root fact carries no root-type source conflict and no unresolved
# branch interaction. Register cells graded conflicted_pending (the
# Xin/Gui Changsheng conflicts) or light_listed_conflicted (the
# root-type readings conflict) NEVER make a root effective.
PURE_SUPPORT_METAL_MONTHS = ('酉',)
PURE_GENERATING_WATER_MONTHS = ('子',)

_MW_ROOT_TABLES = {stem: {entry['branch']: entry for entry in rows}
                   for stem, rows in METAL_WATER_ROOT_TABLES.items()}
_MW_HEAVY_GRADES = ('per_stem_listed', 'framework_derived')


def _mw_root_grade(stem, branch):
    table = _MW_ROOT_TABLES.get(stem)
    if table is None:
        return None
    entry = table.get(branch)
    return entry['grade'] if entry is not None else None


# TJ-011.2 E0355: earth visible-stem root eligibility, wired per the
# adjudicated consumption contract (bazi_earth_roots.
# EARTH_CONSUMPTION_CONTRACT, contract
# bazi-earth-root-consumption-contract-v1, adjudicated at E0257).
# The contract's eligibility is a CELL-LEVEL WHITELIST: exactly the
# two per-stem-listed Lu cells (Wu x Si, Ji x Wu) may count. The
# whitelist is derived from the contract record itself, never from
# the raw grading table through the metal/water exclusion shape
# (grade not in (no_root, conflicted_pending)): the earth grade
# vocabulary carries a fourth grade, structural_present_ungraded,
# which the contract adjudicates NOT eligible -- the exclusion shape
# would miscount all eight ungraded cells as eligible. Pending cells
# stay blocked with no branch fallback, no_root cells stay
# fact-consumption only, and the sealed policy is not edited (it
# still carries no earth set). This wires ONLY the visible-stem
# eligibility surface (registered_eligible below): day-root
# effectiveness (register_effective) is deliberately untouched, so
# the earth effective caliber and earth day-master forms remain
# unreviewed and unbuilt (contract preconditions 3 and 5).
_EARTH_ELIGIBLE_ROOT_CELLS = frozenset(
    (cell.split('×')[0], cell.split('×')[1])
    for gc in EARTH_CONSUMPTION_CONTRACT['grade_contracts']
    if gc['eligibility'] == 'eligible' for cell in gc['cells'])
_EARTH_STEMS = frozenset(stem for stem, _ in _EARTH_ELIGIBLE_ROOT_CELLS)


def action_effects(pillars, *, observed, relations, principal, availability,
                   action_variant=EFFECT_VARIANT):
    """Reviewed sufficient contexts; this is not a general effect classifier."""
    if action_variant != EFFECT_VARIANT:
        raise ValueError('Unsupported action effect variant')
    if tuple(p['name'] for p in pillars) != PILLAR_NAMES or pillars[2]['stem']['value'] != observed['day_master']:
        raise ValueError('Expected matching ordered pillars and observed day master')
    policy = EvidenceResolver().entities['bazi.concept.action_effects_v1'][1]['attributes']
    supports = tuple(policy['support_relations'])
    visible, hidden = observed['visible_relations'], observed['hidden_relations']
    interaction_kinds = [key for key in policy['unresolved_interactions'] if relations[key]]
    eligible = []
    for row in visible:
        fact = row['fact']
        roots = [r for r in fact['root_positions']
                 if r['branch'] in policy['reviewed_root_branches'].get(fact['element'], [])]
        eligible.append(roots)
    wood = stem_element(observed['day_master']) == policy['day_master_element']
    no_interactions = not interaction_kinds
    pure_conditions = {
        'wood_day_master': wood,
        'reviewed_same_element_month': principal['month_branch'] in policy['pure_months']
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'all_positions_support_only': all(r['fact']['relation'] in supports for r in visible + hidden),
        'visible印_present': any(r['fact']['relation'] == 'generates_me' for r in visible),
        'visible比_present': any(r['fact']['relation'] == 'same_element' for r in visible),
        'effective_day_roots': availability['root_presence']
            and all(r['root_availability'] == 'effective' for r in availability['roots']),
        'all_visible_have_reviewed_roots': all(eligible),
        'no_unresolved_interactions': no_interactions,
    }
    isolated_conditions = {
        'wood_day_master': wood,
        'reviewed_control_month': principal['month_branch'] in policy['isolated_months']
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'controls_me',
        'day_has_no_structural_root': not availability['root_presence'],
        'no_support_in_any_position': all(r['fact']['relation'] not in supports for r in visible + hidden),
        'visible_earth_metal_only': all(r['fact']['element'] in ('土', '金') for r in visible),
        'month_principal_exposed_with_root': any(r['fact']['pillar'] == 'month'
            and r['fact']['stem'] == principal['principal_qi'] and eligible[i]
            for i, r in enumerate(visible)),
        'no_unresolved_interactions': no_interactions,
    }
    # TJ-011.2: the generating-month (亥) scope mirrors the pure scope
    # condition by condition; only the month condition differs (reviewed
    # principal relation generates_me in a PURE_GENERATING_MONTHS month
    # instead of same_element in a policy pure_months month). Every other
    # key reuses the pure scope's computed fact, so the two scopes can
    # never diverge on a shared condition.
    generating_conditions = {
        'wood_day_master': pure_conditions['wood_day_master'],
        'reviewed_generating_month': principal['month_branch'] in PURE_GENERATING_MONTHS
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'generates_me',
        'all_positions_support_only': pure_conditions['all_positions_support_only'],
        'visible印_present': pure_conditions['visible印_present'],
        'visible比_present': pure_conditions['visible比_present'],
        'effective_day_roots': pure_conditions['effective_day_roots'],
        'all_visible_have_reviewed_roots': pure_conditions['all_visible_have_reviewed_roots'],
        'no_unresolved_interactions': pure_conditions['no_unresolved_interactions'],
    }
    # TJ-011.2: commanding visible-support scope (Bing day master, Wu
    # month, same-element command), per the adjudicated fire morphology
    # register (bazi_fire_morphology.FORM_BING_WU, nine conditions). This
    # is a NEW form, not a widening of the pure scope: its quantitative
    # layer is the VISIBLE stems only. Hidden stems enter solely as root
    # facts (existence and availability) under the registered governance
    # convention fire-morph.hidden-layer-root-facts-only -- a Variant
    # governance convention, NOT original text -- so a non-support hidden
    # stem (e.g. Ji in Wu) is recorded but never vetoes, and a support
    # hidden stem never counts as support. Fire's reviewed root branches
    # come from the public morphology register (BING_ALL_ROOT_BRANCHES);
    # every other element keeps the sealed policy set. Root
    # effectiveness for this form is read off the executed root facts
    # themselves (no root-type source conflict, no unresolved branch
    # interaction touching the root), exactly as the register's
    # effective_heavy_day_roots condition defines it; the sealed
    # availability variant remains wood-scoped and is not edited.
    commanding_reviewed_roots = dict(policy['reviewed_root_branches'])
    commanding_reviewed_roots['火'] = list(BING_ALL_ROOT_BRANCHES)
    eligible_commanding = []
    for row in visible:
        fact = row['fact']
        roots = [r for r in fact['root_positions']
                 if r['branch'] in commanding_reviewed_roots.get(fact['element'], [])]
        eligible_commanding.append(roots)
    day_roots = availability['roots']
    # The register grades the Xu fire root light_listed_conflicted
    # (root-type readings conflict, bazi.concept.conflict_root_type_
    # readings): the sealed root-conditions candidate table marks the
    # fire residual-qi candidate at Wei only, so the executed facts do
    # not flag Xu roots. The register is this form's specification, so
    # a fire root in a register-conflicted branch is not form-effective
    # either; the sealed policy is not edited.
    register_conflicted_fire_branches = {
        entry['branch'] for entry in BING_ROOT_POSITIONS
        if entry['grade'] == 'light_listed_conflicted'}
    fire_day = stem_element(observed['day_master']) == '火'

    def form_effective(root):
        if root['type_source_conflict'] or root['branch_relations']:
            return False
        return not (fire_day and root['root_presence']['branch']
                    in register_conflicted_fire_branches)
    commanding_conditions = {
        'fire_day_master_bing': observed['day_master'] == '丙',
        'reviewed_same_element_command_month': principal['month_branch'] == '午'
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'visible_positions_support_only': all(r['fact']['relation'] in supports for r in visible),
        'visible_resource_present': any(r['fact']['relation'] == 'generates_me' for r in visible),
        'visible_peer_present': any(r['fact']['relation'] == 'same_element' for r in visible),
        'effective_heavy_day_roots': bool(day_roots)
            and any(r['root_presence']['branch'] in BING_HEAVY_ROOT_BRANCHES for r in day_roots)
            and all(form_effective(r) for r in day_roots),
        'all_visible_have_reviewed_roots': all(eligible_commanding),
        'no_unresolved_interactions': no_interactions,
        # Governance convention condition: true by the construction of
        # this scope (the hidden layer IS handled root-facts-only here);
        # the register lists it as a condition of the form and it is
        # annotated as governance_convention, never original_text, in
        # the adjudication conditions output.
        'hidden_layer_convention_applied': True,
    }
    # TJ-011.2 F3: lu-month visible-support scope (Bing day master, Si
    # month), per the adjudicated register
    # bazi_fire_si_yin_morphology.FORM_BING_SI (nine conditions, key
    # order = register order). This form mirrors the commanding form
    # condition by condition; the ONLY condition that differs is the
    # month condition: Si in place of Wu, where Si's principal stem
    # Bing is reviewed same_element AND Si is the day master's
    # stem-listed LU position (per-stem listed, triple-attested across
    # Sanming, Shenfeng and Ditiansui -- see the register). Like the
    # commanding form, the quantitative layer is the VISIBLE stems
    # only; hidden stems enter solely as root facts under the
    # registered governance convention instance
    # fire-morph.wu-geng-in-si-non-veto (Si's hidden Wu = output and
    # hidden Geng = wealth are recorded, never vetoes) -- a Variant
    # governance convention, NOT original text. Every shared condition
    # reuses the commanding scope's computed facts (visible relations,
    # form-effective day roots, reviewed-root eligibility, interaction
    # kinds), so the two fire scopes can never diverge on a shared
    # condition; the sealed policy is not edited.
    lu_conditions = {
        'fire_day_master_bing': commanding_conditions['fire_day_master_bing'],
        'reviewed_lu_command_month': principal['month_branch'] == '巳'
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'visible_positions_support_only': commanding_conditions['visible_positions_support_only'],
        'visible_resource_present': commanding_conditions['visible_resource_present'],
        'visible_peer_present': commanding_conditions['visible_peer_present'],
        'effective_heavy_day_roots': commanding_conditions['effective_heavy_day_roots'],
        'all_visible_have_reviewed_roots': commanding_conditions['all_visible_have_reviewed_roots'],
        'no_unresolved_interactions': commanding_conditions['no_unresolved_interactions'],
        # Governance convention condition: true by the construction of
        # this scope (the hidden layer IS handled root-facts-only here,
        # under the Si instance fire-morph.wu-geng-in-si-non-veto); the
        # register lists it as a condition of the form and it is
        # annotated as governance_convention, never original_text, in
        # the adjudication conditions output.
        'hidden_layer_convention_applied': True,
    }
    # TJ-011.2 F4: changsheng / generating-month visible-support scope
    # (Bing day master, Yin month), per the adjudicated register
    # bazi_fire_si_yin_morphology.FORM_BING_YIN (nine conditions, key
    # order = register order). It mirrors the commanding/lu scopes
    # condition by condition; the only condition that differs is the
    # month condition: Yin in place of Wu/Si, where Yin's principal
    # stem Jia is reviewed generates_me (a generating month) AND Yin
    # is the day master's stem-listed CHANGSHENG position (per-stem
    # listed, multiply corroborated -- see the register). The form
    # claims NO commanding: Yin is neither the lu nor the diwang
    # position of Bing. Like the sibling fire forms, the quantitative
    # layer is the VISIBLE stems only; hidden stems enter solely as
    # root facts under the registered governance convention instance
    # fire-morph.wu-in-yin-non-veto (Yin's hidden Wu = output is
    # recorded, never a veto; hidden Bing = peer is recorded as a
    # support hidden stem) -- a Variant governance convention, NOT
    # original text. Every shared condition reuses the commanding
    # scope's computed facts, so the fire scopes can never diverge on
    # a shared condition; the sealed policy is not edited.
    #
    # SEGMENT GATE (user adjudication, 2026-10-28, reading 乙
    # segment-tightened): the registered month condition is
    # additionally tightened at the ADJUDICATION layer -- the birth
    # instant must fall in the Jia commander segment [+14d, next jie)
    # of the authorized pilot Variant bazi-siling-yin-pilot-v1. This
    # scope therefore deliberately does NOT enter the proved/context
    # chain below: the effects layer receives no birth instant and
    # cannot know the segment, so it must not assert effectiveness
    # for a context whose defining extra condition is unresolved
    # there (a Wu- or Bing-segment chart meets these nine conditions
    # yet must not fire). The nine executed conditions are exposed
    # verbatim; sufficiency is concluded only by the combination
    # function strength_assessment_changsheng in bazi_adjudication,
    # which consumes an explicit pilot result (Slice D-1 D4 form).
    changsheng_conditions = {
        'fire_day_master_bing': commanding_conditions['fire_day_master_bing'],
        'reviewed_generating_changsheng_month': principal['month_branch'] == '寅'
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'generates_me',
        'visible_positions_support_only': commanding_conditions['visible_positions_support_only'],
        'visible_resource_present': commanding_conditions['visible_resource_present'],
        'visible_peer_present': commanding_conditions['visible_peer_present'],
        'effective_heavy_day_roots': commanding_conditions['effective_heavy_day_roots'],
        'all_visible_have_reviewed_roots': commanding_conditions['all_visible_have_reviewed_roots'],
        'no_unresolved_interactions': commanding_conditions['no_unresolved_interactions'],
        # Governance convention condition: true by the construction of
        # this scope (the hidden layer IS handled root-facts-only here,
        # under the Yin instance fire-morph.wu-in-yin-non-veto); the
        # register lists it as a condition of the form and it is
        # annotated as governance_convention, never original_text, in
        # the adjudication conditions output.
        'hidden_layer_convention_applied': True,
    }
    # TJ-011.2 S2: register-driven root facts for the metal/water pure
    # forms. Root effectiveness and visible-root eligibility are read
    # off the S1 register (see the PURE_SUPPORT_METAL_MONTHS note);
    # every shared condition reuses the pure scope's computed fact, so
    # the new scopes can never diverge from pure on a shared condition.
    day_master = observed['day_master']
    dm_element = stem_element(day_master)
    metal_day = dm_element == '金'
    water_day = dm_element == '水'

    def register_effective(root):
        if root['type_source_conflict'] or root['branch_relations']:
            return False
        return _mw_root_grade(day_master, root['root_presence']['branch']) \
            in _MW_HEAVY_GRADES

    registered_roots_effective = bool(day_roots) and availability['root_presence'] \
        and all(register_effective(r) for r in day_roots)

    def registered_eligible(row):
        # A visible stem has a registered/reviewed root position iff
        # some root position's branch is a settled root cell for that
        # stem in the S1 register (heavy or light; pending and no_root
        # cells never count), or -- for stems the register does not
        # grade -- the branch is in the sealed policy's reviewed set.
        # Earth stems are the adjudicated exception (E0355): they
        # consult ONLY the E0257 consumption contract's cell-level
        # whitelist (Wu x Si, Ji x Wu) -- neither the exclusion shape
        # nor the sealed-policy fallback applies to them (the policy
        # still carries no earth set). The metal form's former
        # register-gap channel is retired by this wiring; its
        # chart-unrealizability stands on the two calendar channels
        # (see bazi_metal_water_roots.METAL_YOU_SATISFIABILITY).
        fact = row['fact']
        if fact['stem'] in _EARTH_STEMS:
            return [r for r in fact['root_positions']
                    if (fact['stem'], r['branch'])
                    in _EARTH_ELIGIBLE_ROOT_CELLS]
        table = _MW_ROOT_TABLES.get(fact['stem'])
        out = []
        for r in fact['root_positions']:
            if table is not None:
                entry = table.get(r['branch'])
                if entry is not None and entry['grade'] not in (
                        'no_root', 'conflicted_pending'):
                    out.append(r)
            elif r['branch'] in policy['reviewed_root_branches'].get(
                    fact['element'], []):
                out.append(r)
        return out

    all_registered_roots = all(registered_eligible(row) for row in visible)
    metal_conditions = {
        'metal_day_master': metal_day,
        'reviewed_same_element_month_you': principal['month_branch'] in PURE_SUPPORT_METAL_MONTHS
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'all_positions_support_only': pure_conditions['all_positions_support_only'],
        'visible印_present': pure_conditions['visible印_present'],
        'visible比_present': pure_conditions['visible比_present'],
        'effective_day_roots_registered': registered_roots_effective if metal_day else False,
        'all_visible_have_registered_roots': all_registered_roots if metal_day else False,
        'no_unresolved_interactions': no_interactions,
    }
    water_conditions = {
        'water_day_master': water_day,
        'reviewed_same_element_month_zi': principal['month_branch'] in PURE_GENERATING_WATER_MONTHS
            and principal['status'] == 'reviewed_relation' and principal['relation'] == 'same_element',
        'all_positions_support_only': pure_conditions['all_positions_support_only'],
        'visible印_present': pure_conditions['visible印_present'],
        'visible比_present': pure_conditions['visible比_present'],
        'effective_day_roots_registered': registered_roots_effective if water_day else False,
        'all_visible_have_registered_roots': all_registered_roots if water_day else False,
        'no_unresolved_interactions': no_interactions,
    }
    pure, generating, commanding, isolated = (all(pure_conditions.values()),
        all(generating_conditions.values()), all(commanding_conditions.values()),
        all(isolated_conditions.values()))
    lu = all(lu_conditions.values())
    changsheng = all(changsheng_conditions.values())
    metal = all(metal_conditions.values())
    water = all(water_conditions.values())
    visible_effects = []
    for i, row in enumerate(visible):
        proved = pure or generating or commanding or lu or metal or water or (isolated and row['fact']['pillar'] == 'month')
        visible_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'eligible_root_positions': eligible[i], 'conditions': row['conditions'],
            'effective_action': row['fact']['relation'] if proved else None,
            'effect_status': 'effective_in_reviewed_context' if proved else 'unresolved',
            'context': 'pure_support' if pure else (
                'pure_generating_support' if generating else (
                    'commanding_visible_support' if commanding else (
                        'lu_visible_support' if lu else (
                            'pure_support_metal' if metal else (
                                'pure_generating_support_water' if water else (
                                    'isolated_control' if proved else None)))))),
            'polarity_equivalence_assumed': False, 'distance_weight': None})
    hidden_effects = []
    for i, row in enumerate(hidden):
        root_indexes = [j for j, r in enumerate(availability['roots'])
            if r['root_presence']['pillar'] == row['fact']['pillar']
            and r['root_presence']['hidden_stem'] == row['fact']['stem']
            and r['root_availability'] == 'effective']
        if not root_indexes and (metal or water):
            root_indexes = [j for j, r in enumerate(availability['roots'])
                if r['root_presence']['pillar'] == row['fact']['pillar']
                and r['root_presence']['hidden_stem'] == row['fact']['stem']
                and register_effective(r)]
        participates = (pure or generating or metal or water) and root_indexes
        hidden_effects.append({'action_index': i, 'fact': dict(row['fact']),
            'effective_action': 'root_support' if participates else None,
            'effect_status': 'root_participation_only' if participates else 'unresolved',
            'root_indexes': root_indexes, 'equivalent_to_visible': False})
    return {'action_variant': action_variant, 'day_master': observed['day_master'],
            'pure_support_scope_conditions': pure_conditions, 'pure_support_scope_met': pure,
            'pure_generating_support_scope_conditions': generating_conditions,
            'pure_generating_support_scope_met': generating,
            'commanding_visible_support_scope_conditions': commanding_conditions,
            'commanding_visible_support_scope_met': commanding,
            'lu_visible_support_scope_conditions': lu_conditions,
            'lu_visible_support_scope_met': lu,
            'changsheng_visible_support_scope_conditions': changsheng_conditions,
            'changsheng_visible_support_scope_met': changsheng,
            'pure_support_metal_scope_conditions': metal_conditions,
            'pure_support_metal_scope_met': metal,
            'pure_generating_support_water_scope_conditions': water_conditions,
            'pure_generating_support_water_scope_met': water,
            'isolated_control_scope_conditions': isolated_conditions, 'isolated_control_scope_met': isolated,
            'visible_relations': visible_effects, 'hidden_relations': hidden_effects,
            'unresolved_interaction_kinds': interaction_kinds,
            'transformation_status': 'unresolved' if any(relations[k] for k in (
                'stem_five_combinations', 'branch_six_harmonies', 'branch_triple_harmonies')) else 'not_present',
            'stem_erasure_applied': False, 'hidden_visible_equivalence_applied': False,
            'weights_available': False, 'overall_strength': None,
            'scope': '仅已审木日主纯印比月卯生扶、亥月印比生扶（从旺口径）、或无根无扶月酉透辛的条件作用；丙日主午月同类当令显纯生扶（从强主锚，藏干仅作根位事实——治理约定非原文）；丙日主巳月禄月显纯生扶（从强主锚，藏干仅作根位事实——治理约定非原文）；丙日主寅月长生印月显纯生扶九条件（从旺主锚，藏干仅作根位事实——治理约定非原文；九条件之外另须寅月司令甲段，由裁决层组合函数凭试点结果核验，本层不据九条件单独断效）；金日主酉月、水日主子月全位置纯生扶（从旺/从强通述口径，根有效性以 S1 登记表驱动、冲突格阻断）；其他效力未裁定，不推从格、喜用或吉凶。'}


def action_conditions(pillars, day_master, *, support, relations, month_command,
                      action_variant=ACTION_VARIANT):
    if action_variant != ACTION_VARIANT:
        raise ValueError('Unsupported conditional action variant')
    if len(pillars) != 4 or tuple(p['name'] for p in pillars) != PILLAR_NAMES:
        raise ValueError('Expected ordered year/month/day/hour pillars')
    table = foundations()['hidden_stems']
    visible = []
    for row in support['visible_positions']:
        pillar = row['pillar']
        index = PILLAR_NAMES.index(pillar)
        root_positions = [{'pillar': p['name'], 'branch': p['branch']['value'], 'hidden_stem': h,
                           'same_stem': h == row['stem']}
                          for p in pillars for h in table[p['branch']['value']]
                          if stem_element(h) == row['element']]
        exposures = [r for r in root_positions if r['same_stem']]
        stem_combinations = [r for r in relations['stem_five_combinations'] if pillar in r['pillars']]
        branch_relations = [{'kind': k, **r} for k in ('branch_six_clashes', 'branch_six_harmonies',
                             'branch_six_harms', 'branch_triple_harmonies') for r in relations[k]
                            if any(p['pillar'] in r['pillars'] for p in root_positions)]
        visible.append({
            'fact': {**row, 'visibility': 'visible', 'pillar_distance_to_day': abs(index - 2),
                     'adjacent_to_day': abs(index - 2) == 1,
                     'root_positions': root_positions, 'rooted_visible_candidate': bool(root_positions),
                     'hidden_same_stem_positions': exposures},
            'conditions': {'month_commander_status': month_command['commander_status'],
                           'stem_combinations': stem_combinations, 'root_branch_relations': branch_relations,
                           'season_effect': 'unresolved', 'root_availability': 'unresolved',
                           'proximity_effect': 'unresolved', 'combination_effect': 'unresolved',
                           'favorable_or_unfavorable': 'unresolved'},
            'effective_action': None, 'effect_status': 'unresolved',
        })
    hidden = []
    for row in support['hidden_positions']:
        targets = [p['name'] for p in pillars if p['name'] != 'day' and p['stem']['value'] == row['stem']]
        hidden.append({'fact': {**row, 'visibility': 'hidden', 'visible_same_stem_pillars': targets},
                       'effective_action': None, 'effect_status': 'unresolved',
                       'equivalent_to_visible': False})
    return {'action_variant': action_variant, 'day_master': day_master,
            'visible_relations': visible, 'hidden_relations': hidden,
            'hidden_visible_equivalence_applied': False, 'weights_available': False,
            'de_shi': None, 'overall_strength': None,
            'scope': '仅记录方向与显藏、有根、柱位距离、合冲条件；方向、邻近或有根均不自动证明效力或得势。'}
