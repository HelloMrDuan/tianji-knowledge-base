"""Bounded evidence rules and legacy abstention; no source-case lookup predictions."""

from .bazi_core import VARIANT as BAZI_VARIANT
from .bazi_root_conditions import STRENGTH_VARIANT, AVAILABILITY_VARIANT, root_availability
from .bazi_commander import PRINCIPAL_VARIANT, principal_month
from .bazi_action_conditions import (
    EFFECT_VARIANT, PURE_GENERATING_MONTHS, PURE_GENERATING_WATER_MONTHS,
    PURE_SUPPORT_METAL_MONTHS)
from .bazi_fire_morphology import BING_ROOT_POSITIONS, FORM_BING_WU
from .bazi_fire_si_yin_morphology import FORM_BING_SI
from .bazi_metal_water_roots import (
    METAL_WATER_ROOT_TABLES, S2_ANCHOR_TYPES, S2_LIMITATIONS)
from .foundations import stem_element

ADJUDICATION_VARIANT = 'bazi-strength-adjudication-v1'

# TJ-011.2: registered anchor provenance of the nine commanding-form
# conditions (bazi_fire_morphology.FORM_BING_WU). The adjudication
# conditions output for the commanding predicate carries each
# condition's registered anchor_type verbatim, so governance-convention
# conditions (hidden_layer_convention_applied) are machine-distinguish-
# able from original-text conditions and never presented as such.
COMMANDING_ANCHOR_TYPES = {c['key']: c['anchor_type']
                           for c in FORM_BING_WU['conditions']}

# TJ-011.2 F3: registered anchor provenance of the nine lu-month form
# conditions (bazi_fire_si_yin_morphology.FORM_BING_SI). The
# adjudication conditions output for the lu predicate carries each
# condition's registered anchor_type verbatim, exactly like the
# commanding form, so the governance-convention condition
# (hidden_layer_convention_applied, instance
# fire-morph.wu-geng-in-si-non-veto) stays machine-distinguishable
# from original-text conditions.
LU_ANCHOR_TYPES = {c['key']: c['anchor_type']
                   for c in FORM_BING_SI['conditions']}

# TJ-011.2: fire root branches whose root-type readings the morphology
# register grades light_listed_conflicted (Xu: tomb listing vs
# residual-qi listing), with their registered conflict ID. The sealed
# root-conditions candidate table flags the fire residual candidate at
# Wei only, so executed facts leave Xu roots unflagged; the register
# states such roots carry the conflict and bar adjudication under the
# existing mechanism, so the bounded assessment presents the conflict
# for fire day masters from the register (sealed policy not edited).
REGISTER_FIRE_ROOT_CONFLICTS = {
    entry['branch']: entry['conflict_id']
    for entry in BING_ROOT_POSITIONS
    if entry['grade'] == 'light_listed_conflicted'}

# TJ-011.2 S2: registered anchor provenance of the two new pure-form
# predicates (bazi_metal_water_roots FORM_PURE_SUPPORT_METAL /
# FORM_PURE_GENERATING_WATER). Each emitted condition carries its
# registered anchor_type verbatim, exactly like the commanding form.
S2_ANCHOR_REGISTRATION = {
    'pure_support_metal': 'bazi_metal_water_roots.FORM_PURE_SUPPORT_METAL',
    'pure_generating_support_water':
        'bazi_metal_water_roots.FORM_PURE_GENERATING_WATER'}

_MW_TABLES = {stem: {entry['branch']: entry for entry in rows}
              for stem, rows in METAL_WATER_ROOT_TABLES.items()}
_MW_HEAVY_GRADES = ('per_stem_listed', 'framework_derived')


def _mw_grade(stem, branch):
    entry = _MW_TABLES.get(stem, {}).get(branch)
    return entry['grade'] if entry is not None else None


# TJ-011.2 S2: metal/water day roots whose S1 register cells carry an
# unresolved conflict -- conflicted_pending cells (the Xin/Gui
# Changsheng branch conflicts, each with its registered conflict ID)
# and light_listed_conflicted cells (the root-type readings conflict).
# The sealed root-conditions candidate table does not flag all of
# these (e.g. a Gui root in Hai carries no fact-level flag), so the
# bounded assessment presents the conflict from the register and
# blocks under the existing mechanism, mirroring the fire register
# conflicts above; the sealed policy is not edited.
REGISTER_METAL_WATER_ROOT_CONFLICTS = {
    stem: {entry['branch']: entry['conflict_id'] for entry in rows
           if entry['grade'] in ('conflicted_pending',
                                 'light_listed_conflicted')}
    for stem, rows in METAL_WATER_ROOT_TABLES.items()}


def _bounded_assessment(trace):
    # Check trace identity and uniqueness before indexing executed evidence.
    # A repeated rule ID would otherwise silently overwrite an earlier
    # observation, even if both rows carried individually valid citations.
    if getattr(trace, 'domain', None) != 'bazi' or getattr(trace, 'variant', None) != BAZI_VARIANT:
        raise ValueError('Bounded strength requires the Bazi execution variant')
    rule_ids = [step['rule_id'] for step in trace.steps]
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError('Duplicate rule ID in bounded strength trace')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    keys = ('principal_month', 'root_availability', 'action_effects')
    # A research verdict also requires its upstream observed facts. Evidence IDs
    # alone cannot prove that outputs belong to the same executed chart.
    required = keys + ('pillars', 'month_command_variant', 'root_conditions',
                       'action_conditions')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Bounded strength requires executed principal, availability and effect rules')
    for _, step in steps.values():
        if not step['evidence_ids'] or any(e not in trace.evidence for e in step['evidence_ids']):
            raise ValueError('Strength factors lack executed evidence')
    blockers, checks = [], []

    def pointer(key, suffix=''):
        return f"#/trace/{steps['bazi.phase2.' + key][0]}/output" + suffix

    def block(key, suffix, reason, conflicts=()):
        step = steps['bazi.phase2.' + key][1]
        blockers.append({'reason': reason, 'fact_ref': pointer(key, suffix),
            'rule_id': step['rule_id'], 'variant': ADJUDICATION_VARIANT,
            'status': 'unresolved', 'evidence_ids': list(step['evidence_ids']),
            'evidence_id': step['evidence_ids'][0], 'conflict_ids': list(conflicts)})

    command = steps['bazi.phase2.principal_month'][1]['output']
    roots = steps['bazi.phase2.root_availability'][1]['output']
    effects = steps['bazi.phase2.action_effects'][1]['output']
    # Fail closed when a downstream factor contradicts its actual upstream
    # source. This checks computation identity, NOT a new classical school,
    # strength threshold, effective root weight, or useful-god selection.
    pillar_facts = steps['bazi.phase2.pillars'][1]['output']
    command_facts = steps['bazi.phase2.month_command_variant'][1]['output']
    root_facts = steps['bazi.phase2.root_conditions'][1]['output']
    action_facts = steps['bazi.phase2.action_conditions'][1]['output']
    day_master = pillar_facts['day_master']['stem']
    month_branch = pillar_facts['ganzhi'][1][1]
    for key, facts in (
        ('month_command_variant', command_facts),
        ('principal_month', command),
        ('root_conditions', root_facts),
        ('root_availability', roots),
        ('action_conditions', action_facts),
        ('action_effects', effects),
    ):
        if facts.get('day_master') != day_master:
            block(key, '/day_master', 'factor_chain_inconsistent')
    if command_facts.get('month_branch') != month_branch:
        block('month_command_variant', '/month_branch', 'factor_chain_inconsistent')
    if (command.get('month_branch') != month_branch or
            command.get('principal_qi') != command_facts.get('principal_qi')):
        block('principal_month', '/month_branch', 'factor_chain_inconsistent')
    if roots.get('root_presence') != root_facts.get('present_structurally'):
        block('root_availability', '/root_presence', 'factor_chain_inconsistent')
    if len(roots['roots']) != len(root_facts['roots']):
        block('root_availability', '/roots', 'factor_chain_inconsistent')
    else:
        for i, (raw, reviewed) in enumerate(zip(root_facts['roots'], roots['roots'])):
            if reviewed.get('root_index') != i or reviewed.get('root_presence') != raw.get('fact'):
                block('root_availability', f'/roots/{i}', 'factor_chain_inconsistent')
    for kind in ('visible', 'hidden'):
        observed = action_facts[kind + '_relations']
        adjudicated = effects[kind + '_relations']
        if len(observed) != len(adjudicated):
            block('action_effects', '/' + kind + '_relations', 'factor_chain_inconsistent')
        else:
            for i, (raw, reviewed) in enumerate(zip(observed, adjudicated)):
                if (reviewed.get('action_index') != i or
                        reviewed.get('fact') != raw.get('fact')):
                    block('action_effects',
                          f'/{kind}_relations/{i}', 'factor_chain_inconsistent')
    # Reconstruct both reviewed derived factors directly from their actual
    # upstream facts, not merely by comparing a subset of output fields.
    # Forged "effective" roots or a forged month relation otherwise preserve
    # the evidence IDs and might incorrectly satisfy a sufficient predicate.
    if command != principal_month(command_facts, day_master):
        block('principal_month', '/status', 'derived_principal_replay_mismatch')
    if roots != root_availability(root_facts):
        block('root_availability', '/root_presence',
              'derived_root_availability_replay_mismatch')
    for key, field, expected in [('principal_month','command_variant',PRINCIPAL_VARIANT),
                                 ('root_availability','root_variant',AVAILABILITY_VARIANT),
                                 ('action_effects','action_variant',EFFECT_VARIANT)]:
        if steps['bazi.phase2.' + key][1]['output'][field] != expected:
            block(key, '/' + field, 'factor_variant_mismatch')
    for cid in command['dated_source_conflicts']:
        checks.append({'conflict_id':cid,'status':'unresolved','blocking':False,
                       'reason':'dated_commander_not_a_dependency',
                       'fact_ref':pointer('principal_month','/dated_source_conflicts'),
                       'evidence_ids':list(steps['bazi.phase2.month_command_variant'][1]['evidence_ids'])})
    checks.append({'conflict_id':'bazi.concept.conflict_three_punishments',
                   'status':'unresolved','blocking':False,
                   'reason':'not_applied_in_explicit_ren_school',
                   'fact_ref':pointer('root_availability'),
                   'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
    for i, root in enumerate(roots['roots']):
        if root['type_source_conflict']:
            cid=root['type_source_conflict']
            checks.append({'conflict_id':cid,'status':'unresolved','blocking':True,
                           'reason':'root_type_source_conflict',
                           'fact_ref':pointer('root_availability',f'/roots/{i}/type_source_conflict'),
                           'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
            block('root_availability',f'/roots/{i}/type_source_conflict','root_type_source_conflict',[cid])
        elif (stem_element(day_master) == '火'
              and root['root_presence']['branch'] in REGISTER_FIRE_ROOT_CONFLICTS):
            # Register-sourced root-type conflict (see
            # REGISTER_FIRE_ROOT_CONFLICTS): presented and blocking
            # under the same mechanism as a fact-sourced conflict.
            cid = REGISTER_FIRE_ROOT_CONFLICTS[root['root_presence']['branch']]
            checks.append({'conflict_id':cid,'status':'unresolved','blocking':True,
                           'reason':'root_type_source_conflict',
                           'fact_ref':pointer('root_availability',f'/roots/{i}/root_presence/branch'),
                           'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
            block('root_availability',f'/roots/{i}/root_presence/branch','root_type_source_conflict',[cid])
        elif (day_master in REGISTER_METAL_WATER_ROOT_CONFLICTS
              and root['root_presence']['branch']
                  in REGISTER_METAL_WATER_ROOT_CONFLICTS[day_master]):
            # Register-sourced root conflict (see
            # REGISTER_METAL_WATER_ROOT_CONFLICTS): presented and
            # blocking under the same mechanism as a fact-sourced
            # conflict, for metal/water day masters only.
            cid = REGISTER_METAL_WATER_ROOT_CONFLICTS[day_master][
                root['root_presence']['branch']]
            checks.append({'conflict_id':cid,'status':'unresolved','blocking':True,
                           'reason':'root_type_source_conflict',
                           'fact_ref':pointer('root_availability',f'/roots/{i}/root_presence/branch'),
                           'evidence_ids':list(steps['bazi.phase2.root_availability'][1]['evidence_ids'])})
            block('root_availability',f'/roots/{i}/root_presence/branch','root_type_source_conflict',[cid])
        if root['root_availability'] != 'effective':
            block('root_availability',f'/roots/{i}/root_availability','root_availability_not_effective')
    if command['status'] != 'reviewed_relation':
        block('principal_month','/status','principal_qi_not_reviewed')
    if effects['unresolved_interaction_kinds']:
        block('action_effects','/unresolved_interaction_kinds','interaction_effect_unresolved')

    # Sufficient predicates are conjunctions, not votes or count thresholds.
    pure = (effects['pure_support_scope_met']
        and all(effects['pure_support_scope_conditions'].values())
        and command['month_branch'] == '卯' and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['root_availability'] == 'effective' for r in roots['roots'])
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    # TJ-011.2: generating-month (亥) disjunct, structurally identical to
    # the pure disjunct except the month condition: a reviewed generating
    # month (principal qi generates the wood day master) instead of the
    # same-element month. It rests on Ren's Congwang definition, not on
    # seasonal command (得令), and yields strong only, never weak.
    pure_generating = (effects['pure_generating_support_scope_met']
        and all(effects['pure_generating_support_scope_conditions'].values())
        and command['month_branch'] in PURE_GENERATING_MONTHS and command['relation'] == 'generates_me'
        and roots['root_presence']
        and all(r['root_availability'] == 'effective' for r in roots['roots'])
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    isolated = (effects['isolated_control_scope_met']
        and all(effects['isolated_control_scope_conditions'].values())
        and command['month_branch'] == '酉' and command['relation'] == 'controls_me'
        and not roots['root_presence']
        and any(r['fact']['pillar'] == 'month' and r['effective_action'] == 'controls_me'
                and r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    # TJ-011.2: commanding visible-support disjunct (Bing day master, Wu
    # month, same-element command), per the adjudicated fire morphology
    # register FORM_BING_WU. Structurally parallel to the pure disjuncts
    # except the root gate: the sealed availability variant is
    # wood-scoped, so for a fire day master it reports every root as
    # out-of-scope ('root_type_not_in_reviewed_scope') rather than
    # effective. This form's registered root-effectiveness criterion is
    # defined on the executed root facts themselves (no root-type
    # source conflict, no unresolved branch interaction touching the
    # root) and is already computed as the scope condition
    # effective_heavy_day_roots. Accordingly, a
    # 'root_availability_not_effective' blocker raised against a root
    # that IS effective under the form's registered criterion does not
    # bar this predicate (it still bars every other predicate, and the
    # blocker list of any non-commanding verdict is unchanged); every
    # other blocker bars this predicate exactly as it bars the others.
    commanding = (effects['commanding_visible_support_scope_met']
        and all(effects['commanding_visible_support_scope_conditions'].values())
        and command['month_branch'] == '午' and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    # TJ-011.2 F3: lu-month visible-support disjunct (Bing day master,
    # Si month), per the adjudicated register FORM_BING_SI. It is
    # structurally identical to the commanding disjunct except the
    # month condition (Si, the stem-listed lu position, in place of
    # Wu, the diwang position): the root gate is the same
    # register-defined criterion on the executed root facts (no
    # root-type source conflict, no unresolved branch interaction
    # touching the root), already computed as the scope condition
    # effective_heavy_day_roots, and the same blocker reconciliation
    # applies below.
    lu_support = (effects['lu_visible_support_scope_met']
        and all(effects['lu_visible_support_scope_conditions'].values())
        and command['month_branch'] == '巳' and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    # TJ-011.2 S2: pure-form extension disjuncts (metal x You /
    # water x Zi), structurally parallel to the pure disjuncts except
    # the root gate: the sealed availability variant is wood-scoped, so
    # for a metal/water day master it reports every root as
    # out-of-scope rather than effective. These forms' registered
    # root-effectiveness criterion is defined on the S1 register (heavy
    # cell for the day-master stem, no root-type source conflict, no
    # unresolved branch interaction on the root) and is already
    # computed as the scope condition effective_day_roots_registered.
    # Accordingly, a 'root_availability_not_effective' blocker raised
    # against a root that IS effective under the register criterion
    # does not bar these predicates (it still bars every other
    # predicate, and non-S2 verdicts' blocker lists are unchanged);
    # every other blocker bars them exactly as it bars the others.
    pure_support_metal = (effects['pure_support_metal_scope_met']
        and all(effects['pure_support_metal_scope_conditions'].values())
        and command['month_branch'] in PURE_SUPPORT_METAL_MONTHS and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))
    pure_generating_water = (effects['pure_generating_support_water_scope_met']
        and all(effects['pure_generating_support_water_scope_conditions'].values())
        and command['month_branch'] in PURE_GENERATING_WATER_MONTHS and command['relation'] == 'same_element'
        and roots['root_presence']
        and all(r['effect_status'] == 'effective_in_reviewed_context' for r in effects['visible_relations']))

    def register_effective_root(index):
        root = roots['roots'][index]
        if root['type_source_conflict'] or root['branch_relations']:
            return False
        return _mw_grade(day_master, root['root_presence']['branch']) \
            in _MW_HEAVY_GRADES

    def form_effective_root(index):
        root = roots['roots'][index]
        if root['type_source_conflict'] or root['branch_relations']:
            return False
        return root['root_presence']['branch'] not in REGISTER_FIRE_ROOT_CONFLICTS

    commanding_blockers = blockers
    if commanding and day_master == '丙':
        reconcilable_refs = {
            pointer('root_availability', f'/roots/{i}/root_availability')
            for i in range(len(roots['roots'])) if form_effective_root(i)}
        commanding_blockers = [
            b for b in blockers
            if not (b['reason'] == 'root_availability_not_effective'
                    and b['fact_ref'] in reconcilable_refs)]
    lu_blockers = blockers
    if lu_support and day_master == '丙':
        reconcilable_refs = {
            pointer('root_availability', f'/roots/{i}/root_availability')
            for i in range(len(roots['roots'])) if form_effective_root(i)}
        lu_blockers = [
            b for b in blockers
            if not (b['reason'] == 'root_availability_not_effective'
                    and b['fact_ref'] in reconcilable_refs)]
    metal_blockers = blockers
    if pure_support_metal and day_master in ('庚', '辛'):
        reconcilable_refs = {
            pointer('root_availability', f'/roots/{i}/root_availability')
            for i in range(len(roots['roots'])) if register_effective_root(i)}
        metal_blockers = [
            b for b in blockers
            if not (b['reason'] == 'root_availability_not_effective'
                    and b['fact_ref'] in reconcilable_refs)]
    water_blockers = blockers
    if pure_generating_water and day_master in ('壬', '癸'):
        reconcilable_refs = {
            pointer('root_availability', f'/roots/{i}/root_availability')
            for i in range(len(roots['roots'])) if register_effective_root(i)}
        water_blockers = [
            b for b in blockers
            if not (b['reason'] == 'root_availability_not_effective'
                    and b['fact_ref'] in reconcilable_refs)]
    classification, why, conditions = 'indeterminate', None, []
    if not blockers and (pure or pure_generating or isolated):
        if pure:
            classification, predicate = 'strong', 'pure_support'
        elif pure_generating:
            classification, predicate = 'strong', 'pure_generating_support'
        else:
            classification, predicate = 'weak', 'isolated_control'
        for key, met in effects[predicate + '_scope_conditions'].items():
            conditions.append({'condition':key,'met':met,
                'fact_ref':pointer('action_effects','/' + predicate + '_scope_conditions/' + key),
                'rule_id':'bazi.phase2.action_effects',
                'evidence_ids':list(steps['bazi.phase2.action_effects'][1]['evidence_ids'])})
        # TJ-011.2 S5: pure_generating_support is registered in the
        # sealed snapshot (bazi.rule.r029 /
        # bazi.phase2.strength_pure_generating_support), so it takes the
        # same registered trace-step exit as pure_support and
        # isolated_control; no predicate here borrows another rule's ID.
        rule_id = 'bazi.phase2.strength_' + predicate
        trace.add(rule_id, {'strength_variant':ADJUDICATION_VARIANT,
                  'factor_refs':[pointer(k) for k in keys]},
                  {'classification':classification,'variant':ADJUDICATION_VARIANT,'conditions':conditions})
        why = {'sufficient_rule':rule_id,'conditions':conditions,
               'all_required_conditions_verified':True,
               'excluded_dependencies':['dated_commander','independent_hidden_effect_scores']}
    elif commanding and not commanding_blockers:
        # TJ-011.2 S5: this predicate is registered in the sealed
        # snapshot (bazi.rule.r030 /
        # bazi.phase2.strength_commanding_visible_support), so the
        # verdict is issued through its own registered trace step with
        # every condition bound to executed factor evidence; no rule ID
        # is borrowed from another predicate. Each condition
        # additionally carries its registered anchor_type from
        # FORM_BING_WU, so the governance-convention condition stays
        # machine-distinguishable from original-text conditions.
        classification, predicate = 'strong', 'commanding_visible_support'
        for key, met in effects['commanding_visible_support_scope_conditions'].items():
            conditions.append({'condition':key,'met':met,
                'fact_ref':pointer('action_effects','/commanding_visible_support_scope_conditions/' + key),
                'rule_id':'bazi.phase2.action_effects',
                'evidence_ids':list(steps['bazi.phase2.action_effects'][1]['evidence_ids']),
                'anchor_type':COMMANDING_ANCHOR_TYPES[key],
                'anchor_registration':'bazi_fire_morphology.FORM_BING_WU'})
        rule_id = 'bazi.phase2.strength_' + predicate
        trace.add(rule_id, {'strength_variant':ADJUDICATION_VARIANT,
                  'factor_refs':[pointer(k) for k in keys]},
                  {'classification':classification,'variant':ADJUDICATION_VARIANT,'conditions':conditions})
        why = {'sufficient_rule':rule_id,'conditions':conditions,
               'all_required_conditions_verified':True,
               'excluded_dependencies':['dated_commander','independent_hidden_effect_scores']}
        # The verdict's blocker list is the reconciled one: the
        # wood-scope availability blockers against form-effective fire
        # roots were considered and set aside under the register's
        # criterion above, so they are not reported as barring this
        # verdict. (conflict_checks still reports every root conflict.)
        blockers = commanding_blockers
    elif lu_support and not lu_blockers:
        # TJ-011.2 F3: like the S2 predicates below, this predicate
        # has no sealed Phase1/Phase2 rule registration yet, so the
        # verdict is issued through the registered bounded-adjudication
        # exit (bazi.rule.r026) with every condition bound to executed
        # factor evidence and the pending registration disclosed on
        # the verdict itself; no rule ID is borrowed from another
        # predicate. Each condition additionally carries its
        # registered anchor_type from FORM_BING_SI, so the
        # governance-convention condition (hidden layer, instance
        # fire-morph.wu-geng-in-si-non-veto) stays
        # machine-distinguishable from original-text conditions.
        classification, predicate = 'strong', 'lu_visible_support'
        for key, met in effects['lu_visible_support_scope_conditions'].items():
            conditions.append({'condition':key,'met':met,
                'fact_ref':pointer('action_effects','/lu_visible_support_scope_conditions/' + key),
                'rule_id':'bazi.phase2.action_effects',
                'evidence_ids':list(steps['bazi.phase2.action_effects'][1]['evidence_ids']),
                'anchor_type':LU_ANCHOR_TYPES[key],
                'anchor_registration':'bazi_fire_si_yin_morphology.FORM_BING_SI'})
        why = {'sufficient_rule':None,'sufficient_predicate':predicate,
               'predicate_rule_registration':'pending_phase1_rule_registration',
               'conditions':conditions,
               'all_required_conditions_verified':True,
               'excluded_dependencies':['dated_commander','independent_hidden_effect_scores']}
        # The verdict's blocker list is the reconciled one (see the
        # commanding branch note); conflict_checks still reports
        # every root conflict.
        blockers = lu_blockers
    elif (pure_support_metal and not metal_blockers) or \
            (pure_generating_water and not water_blockers):
        # TJ-011.2 S2: like lu_visible_support above, these predicates
        # have no sealed Phase1/Phase2 rule registration yet (their
        # defining root evidence has no canonical section; see the S5
        # registration governance register), so the verdict is issued
        # through the registered bounded-adjudication exit
        # (bazi.rule.r026) with every condition bound to executed
        # factor evidence and the pending registration disclosed on
        # the verdict itself; no rule ID is borrowed. Each condition
        # carries its registered anchor_type from the S1 form
        # registers; the month condition additionally carries the
        # executed chart's S1 grade for the day master's month-branch
        # cell (month_root_grade: per_stem_listed for Xin You / Gui Zi,
        # framework_derived for Geng You / Ren Zi), and the root
        # condition carries every day root's executed grade
        # (root_grades), so a derived-grade (framework_derived) root
        # position stays machine-distinguishable from an explicitly
        # attested (per_stem_listed) one.
        if pure_support_metal and not metal_blockers:
            predicate, reconciled = 'pure_support_metal', metal_blockers
        else:
            predicate, reconciled = 'pure_generating_support_water', water_blockers
        classification = 'strong'
        scope_key = predicate + '_scope_conditions'
        for key, met in effects[scope_key].items():
            cond = {'condition':key,'met':met,
                'fact_ref':pointer('action_effects','/' + scope_key + '/' + key),
                'rule_id':'bazi.phase2.action_effects',
                'evidence_ids':list(steps['bazi.phase2.action_effects'][1]['evidence_ids']),
                'anchor_type':S2_ANCHOR_TYPES[predicate][key],
                'anchor_registration':S2_ANCHOR_REGISTRATION[predicate]}
            if key in ('reviewed_same_element_month_you',
                       'reviewed_same_element_month_zi'):
                cond['month_root_grade'] = _mw_grade(
                    day_master, command['month_branch'])
            if key == 'effective_day_roots_registered':
                cond['root_grades'] = [
                    {'pillar':r['root_presence']['pillar'],
                     'branch':r['root_presence']['branch'],
                     'hidden_stem':r['root_presence']['hidden_stem'],
                     'grade':_mw_grade(
                         day_master, r['root_presence']['branch'])}
                    for r in roots['roots']]
            conditions.append(cond)
        why = {'sufficient_rule':None,'sufficient_predicate':predicate,
               'predicate_rule_registration':'pending_phase1_rule_registration',
               'conditions':conditions,
               'all_required_conditions_verified':True,
               'excluded_dependencies':['dated_commander','independent_hidden_effect_scores']}
        # The verdict's blocker list is the reconciled one (see the
        # disjunct note above); conflict_checks still reports every
        # root conflict.
        blockers = reconciled
    else:
        block('action_effects','/pure_support_scope_conditions','outside_reviewed_sufficient_conditions')
    relevant = {'bazi.phase2.' + k for k in ('pillars','hidden_stems','support_relations',
        'stem_five_combinations','branch_six_harmonies','branch_six_harms','branch_six_clashes',
        'branch_triple_harmonies','month_command_variant','principal_month','root_conditions','root_availability',
        'action_conditions','action_effects','strength_pure_support','strength_isolated_control',
        'strength_pure_generating_support','strength_commanding_visible_support')}
    matched = [s['rule_id'] for s in trace.steps if s['rule_id'] in relevant]
    evidence_ids = sorted({e for s in trace.steps if s['rule_id'] in relevant for e in s['evidence_ids']}
                          | {e for c in checks for e in c['evidence_ids']})
    return {'classification':classification,'variant':ADJUDICATION_VARIANT,
        'decision_status':'reviewed_sufficient_rule_matched' if why else 'insufficient_reviewed_rules',
        'matched_rule_ids':matched,'fact_refs':[f'#/trace/{i}/output' for i,s in enumerate(trace.steps) if s['rule_id'] in relevant],
        'evidence_ids':evidence_ids,'source_ids':sorted({trace.evidence[e]['source_id'] for e in evidence_ids}),
        'conflict_checks':checks,'conflict_ids':sorted({c['conflict_id'] for c in checks if c['blocking']}),
        'blockers':blockers,'unresolved_evidence':sorted({e for b in blockers for e in b['evidence_ids']}),
        'why_not_indeterminate':why,'supported_classifications':['strong','weak','indeterminate'],
        'variant_dependencies':{'dated_commander':False,'principal_qi':True,
            'root_availability':True,'bounded_visible_effects':True,'independent_hidden_effect_scores':False},
        'maturity':'PARTIAL','research_only':True,'public_enabled':False,'ai_enabled':False,
        'weights_available':False,'source_case_lookup_used':False,'full_strength_classifier_ready':False,
        'limitations':['仅显式任氏木日主：纯印比月卯、印比生扶月亥（从旺口径，不取当令），或无根无扶透辛月酉；丙日主午月同类当令显纯生扶（从强主锚）；丙日主巳月禄月显纯生扶（从强主锚）；金日主酉月、水日主子月全位置纯生扶（从旺/从强通述口径）；其余未裁定。',
            '亥月分支谓词已完成密封 Phase1/Phase2 规则注册（bazi.rule.r029 / bazi.phase2.strength_pure_generating_support），裁决经该注册规则步发出并逐条件绑定因子证据。',
            '午月丙日主分支谓词已完成密封 Phase1/Phase2 规则注册（bazi.rule.r030 / bazi.phase2.strength_commanding_visible_support），裁决经该注册规则步发出并逐条件绑定因子证据；其藏干仅作根位事实（不否决、不计效）是 Variant 治理约定而非原文，藏干克破不在本形态裁定范围，逐盘记录在案。',
            '巳月丙日主分支谓词尚待密封 Phase1/Phase2 规则注册（pending），裁决经已注册的有限裁决出口发出并逐条件绑定因子证据，不冒充已注册规则的裁决；其藏干仅作根位事实（不否决、不计效）是 Variant 治理约定而非原文，藏干克破不在本形态裁定范围，逐盘记录在案。',
            '酉月金日主与子月水日主分支谓词尚待密封 Phase1/Phase2 规则注册（pending），裁决经已注册的有限裁决出口发出并逐条件绑定因子证据，不冒充已注册规则的裁决；其根有效性以 S1 金/水根审定登记表驱动（密封可用性 Variant 仍为木专属），辛/癸长生冲突与轻根列举冲突未裁定，受影响根一律阻断、绝不放行。',
            *S2_LIMITATIONS,
            '来源仍为 C 级单一电子版本，未宣称独立底本一致；强不等于吉，弱不等于凶。',
            '不处理 balanced、数字力度、从格、喜用、行运，暗合、半合拱夹与其他学派刑法不在范围。',
            '分日冲突与其他学派刑法仍 unresolved，但不是此明确 Variant 的依赖；不自动开放产品或 AI。']}


def strength_assessment(trace, *, strength_variant=STRENGTH_VARIANT):
    if strength_variant == ADJUDICATION_VARIANT:
        return _bounded_assessment(trace)
    if strength_variant != STRENGTH_VARIANT:
        raise ValueError('Unsupported strength adjudication variant')
    steps = {s['rule_id']: (i, s) for i, s in enumerate(trace.steps)}
    required = ('month_command_variant', 'root_conditions', 'action_conditions')
    if any('bazi.phase2.' + key not in steps for key in required):
        raise ValueError('Strength adjudication requires executed conditional factors')
    blockers = []

    def add(key, suffix, reason, conflicts=()):
        i, step = steps['bazi.phase2.' + key]
        output = step['output']
        blockers.append({'reason': reason, 'fact_ref': f'#/trace/{i}/output' + suffix,
                         'rule_id': step['rule_id'], 'evidence_id': step['evidence_ids'][0],
                         'evidence_ids': list(step['evidence_ids']),
                         'variant': output.get('command_variant', output.get('root_variant',
                                                output.get('action_variant'))),
                         'status': 'unresolved', 'conflict_ids': list(conflicts)})

    command = steps['bazi.phase2.month_command_variant'][1]['output']
    add('month_command_variant', '/commander_status', 'dated_commander_unresolved',
        command['source_conflict'])
    if command['principal_qi_status'] == 'not_reviewed':
        add('month_command_variant', '/principal_qi_status', 'principal_qi_not_reviewed')
    roots = steps['bazi.phase2.root_conditions'][1]['output']['roots']
    for j, root in enumerate(roots):
        add('root_conditions', f'/roots/{j}/availability_status', 'root_availability_unresolved')
        if root['type_source_conflict']:
            add('root_conditions', f'/roots/{j}/type_source_conflict',
                'root_type_source_conflict', [root['type_source_conflict']])
        if root['conditions']['branch_relations']:
            add('root_conditions', f'/roots/{j}/conditions/branch_relations',
                'root_interaction_effect_unresolved')
    actions = steps['bazi.phase2.action_conditions'][1]['output']
    for visibility in ('visible', 'hidden'):
        for j, _ in enumerate(actions[visibility + '_relations']):
            add('action_conditions', f'/{visibility}_relations/{j}/effect_status',
                visibility + '_action_effect_unresolved')
    return {'variant': strength_variant, 'classification': 'indeterminate',
            'decision_status': 'insufficient_reviewed_rules',
            'blockers': blockers, 'supported_classifications': [],
            'weights_available': False, 'maturity': 'PARTIAL',
            'full_strength_classifier_ready': False,
            'source_case_lookup_used': False, 'ai_enabled': False,
            'scope': '真实执行条件的判定出口；尚无可复算的通用强弱或平衡 Rule。'
                     '古例裁语仅供独立复核，不能查表当作算法预测。'}
