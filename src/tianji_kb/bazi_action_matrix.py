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
from .resolver import ExecutionTrace

MATRIX_VARIANT = 'bazi-action-matrix-v1'


def build_matrix_from_chart(chart):
    """Build matrix from a real chart_from_datetime()/chart_from_pillars() output.

    Strict input validation (fail-closed):
    - chart must have 'pillars' (4, ordered year/month/day/hour)
    - chart must have 'day_master' with 'stem'
    - day_master must match day pillar stem
    - all stems/branches must be valid
    """
    _validate_chart(chart)
    pillars = chart['pillars']
    day_master = chart['day_master']['stem']

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


def build_matrix_with_evidence(chart, *, trace_domain='bazi'):
    """Build matrix with per-row Evidence binding via ExecutionTrace.

    Runs the same 6 pure functions as build_matrix_from_chart(), but wraps
    each in trace.add() so every matrix row can be traced to:
    Rule ID -> Section ID -> Source ID -> Evidence ID -> status

    Fail-closed: if any step fails to produce evidence, raises instead of
    returning a partial matrix.
    """
    from .bazi_core import VARIANT as CORE_VARIANT
    # Reuse the strict validation from build_matrix_from_chart
    # (validates pillars, day_master, 60 Jiazi)
    _validate_chart(chart)

    pillars = chart['pillars']
    day_master = chart['day_master']['stem']
    stems = [p['stem']['value'] for p in pillars]
    branches = [p['branch']['value'] for p in pillars]
    relations = reviewed_relations(stems, branches)

    # Create trace - resolver will be EvidenceResolver() (needs private Catalog)
    trace = ExecutionTrace(trace_domain, CORE_VARIANT)

    # Step 1: month_command
    cmd = month_command(pillars, day_master, command_variant=COMMAND_VARIANT)
    trace.add('bazi.phase2.month_command_variant',
              {'command_variant': COMMAND_VARIANT,
               'pillars': [(p['stem']['value'], p['branch']['value']) for p in pillars],
               'day_master': day_master},
              cmd)

    # Step 2: principal_month
    principal = principal_month(cmd, day_master, command_variant=PRINCIPAL_VARIANT)
    trace.add('bazi.phase2.principal_month',
              {'command_variant': PRINCIPAL_VARIANT, 'day_master': day_master},
              principal)

    # Step 3: strength_factors (intermediate, not traced as separate rule)
    strength = strength_factors(pillars, day_master, variant=FACTOR_VARIANT)

    # Step 4: root_conditions
    roots = root_conditions(pillars, day_master, relations=relations,
                            month_command=cmd, root_variant=ROOT_VARIANT)
    trace.add('bazi.phase2.root_conditions',
              {'root_variant': ROOT_VARIANT, 'day_master': day_master},
              roots)

    # Step 5: root_availability
    availability = root_availability(roots, root_variant=AVAILABILITY_VARIANT)
    trace.add('bazi.phase2.root_availability',
              {'root_variant': AVAILABILITY_VARIANT},
              availability)

    # Step 6: action_conditions
    actions = action_conditions(pillars, day_master,
                                support=strength['support_relations'],
                                relations=relations, month_command=cmd,
                                action_variant=ACTION_VARIANT)
    trace.add('bazi.phase2.action_conditions',
              {'action_variant': ACTION_VARIANT, 'day_master': day_master},
              actions)

    # Step 7: action_effects
    effects = action_effects(pillars, observed=actions, relations=relations,
                             principal=principal, availability=availability,
                             action_variant=EFFECT_VARIANT)
    trace.add('bazi.phase2.action_effects',
              {'action_variant': EFFECT_VARIANT},
              effects)

    # Assemble with evidence binding
    result = _assemble_with_evidence(
        pillars, day_master, roots, availability, actions, effects, cmd,
        trace)

    # Verify same-execution consistency
    _verify_evidence_consistency(result, trace, chart)

    return result


def _validate_chart(chart):
    """Extracted strict validation (shared by both build functions)."""
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
    if pillars[2]['stem']['value'] != day_master:
        raise ValueError('day_master does not match day pillar stem')
    for p in pillars:
        s = p.get('stem', {}).get('value')
        b = p.get('branch', {}).get('value')
        if s not in STEMS:
            raise ValueError(f"Invalid stem: {s}")
        if b not in BRANCHES:
            raise ValueError(f"Invalid branch: {b}")
        try:
            ganzhi_index(s + b)
        except (ValueError, KeyError, TypeError) as e:
            raise ValueError(f"Invalid ganzhi combination: {s}{b}") from e


def _assemble_with_evidence(pillars, day_master, roots, availability, actions,
                            effects, cmd, trace):
    """Assemble matrix with per-row evidence from trace steps.

    P0-1 fix: Each row's fact is verified against the actual trace step
    output. The fact_ref must resolve to a fact whose pillar/stem/branch
    match the row. Evidence is not assigned by rule ID alone.
    """
    # Build base matrix first
    base = _assemble(pillars, day_master, roots, availability, actions,
                     effects, cmd)

    # Index trace steps by rule_id
    steps_by_rule = {}
    for i, step in enumerate(trace.steps):
        steps_by_rule[step['rule_id']] = (i, step)

    # Verify required rules exist (fail-closed on unknown/missing)
    required = ['bazi.phase2.root_conditions', 'bazi.phase2.root_availability',
                'bazi.phase2.action_conditions', 'bazi.phase2.action_effects']
    for rid in required:
        if rid not in steps_by_rule:
            raise ValueError(f"Missing required trace step: {rid}")

    # Attach evidence to root rows with fact verification
    rc_idx, rc_step = steps_by_rule['bazi.phase2.root_conditions']
    ra_idx, ra_step = steps_by_rule['bazi.phase2.root_availability']
    rc_roots = rc_step['output'].get('roots', [])
    ra_roots = ra_step['output'].get('roots', [])
    if len(rc_roots) != len(base['roots']):
        raise ValueError(f"Root count mismatch: trace={len(rc_roots)}, matrix={len(base['roots'])}")
    for i, row in enumerate(base['roots']):
        # Verify the fact matches
        trace_fact = rc_roots[i].get('fact', {})
        _verify_root_fact(trace_fact, row, i)
        row['structure_evidence'] = _evidence_block(
            rc_step, rc_idx, f'#/trace/{rc_idx}/output/roots/{i}/fact', trace)
        # Verify availability fact matches
        if i < len(ra_roots):
            ra_fact = ra_roots[i]
            if ra_fact.get('root_index') != i:
                raise ValueError(f"Root {i}: availability index mismatch")
        row['effect_evidence'] = _evidence_block(
            ra_step, ra_idx, f'#/trace/{ra_idx}/output/roots/{i}', trace)
        if row['status'] == 'effective' and not row['effect_evidence']:
            raise ValueError(f"Root {i}: effective without effect evidence")

    # Attach evidence to exposure rows with fact verification
    ac_idx, ac_step = steps_by_rule['bazi.phase2.action_conditions']
    ac_hidden = ac_step['output'].get('hidden_relations', [])
    if len(ac_hidden) != len(base['exposures']):
        raise ValueError(f"Exposure count mismatch")
    for j, row in enumerate(base['exposures']):
        trace_fact = ac_hidden[j].get('fact', {})
        _verify_exposure_fact(trace_fact, row, j)
        row['structure_evidence'] = _evidence_block(
            ac_step, ac_idx, f'#/trace/{ac_idx}/output/hidden_relations/{j}/fact', trace)
        row['effect_evidence'] = None

    # Attach evidence to action rows with fact verification
    ae_idx, ae_step = steps_by_rule['bazi.phase2.action_effects']
    ac_visible = ac_step['output'].get('visible_relations', [])
    ae_visible = ae_step['output'].get('visible_relations', [])
    if len(ac_visible) != len(base['actions']):
        raise ValueError(f"Action count mismatch")
    for k, row in enumerate(base['actions']):
        trace_fact = ac_visible[k].get('fact', {})
        _verify_action_fact(trace_fact, row, k)
        row['structure_evidence'] = _evidence_block(
            ac_step, ac_idx, f'#/trace/{ac_idx}/output/visible_relations/{k}/fact', trace)
        # Verify effect corresponds
        if k < len(ae_visible):
            ae_entry = ae_visible[k]
            if ae_entry.get('action_index') != k:
                raise ValueError(f"Action {k}: effect index mismatch")
        row['effect_evidence'] = _evidence_block(
            ae_step, ae_idx, f'#/trace/{ae_idx}/output/visible_relations/{k}', trace)
        if row['status'] == 'effective' and not row['effect_evidence']:
            raise ValueError(f"Action {k}: effective without effect evidence")

    base['evidence_trace'] = {
        'domain': trace.domain,
        'variant': trace.variant,
        'step_count': len(trace.steps),
        'rule_ids': [s['rule_id'] for s in trace.steps],
    }
    return base


def _verify_root_fact(trace_fact, row, index):
    """Verify trace fact matches matrix row (P0-1)."""
    for field in ('pillar', 'branch', 'hidden_stem'):
        if trace_fact.get(field) != row.get(field):
            raise ValueError(
                f"Root {index}: fact mismatch on {field}: "
                f"trace={trace_fact.get(field)}, row={row.get(field)}")


def _verify_exposure_fact(trace_fact, row, index):
    """Verify exposure fact matches."""
    # trace fact uses 'stem' for hidden stem, row uses 'hidden_stem'
    if trace_fact.get('stem') != row.get('hidden_stem'):
        raise ValueError(f"Exposure {index}: hidden stem mismatch")
    if trace_fact.get('pillar') != row.get('hidden_pillar'):
        raise ValueError(f"Exposure {index}: pillar mismatch")
    if trace_fact.get('branch') != row.get('branch'):
        raise ValueError(f"Exposure {index}: branch mismatch")


def _verify_action_fact(trace_fact, row, index):
    """Verify action fact matches."""
    for field in ('pillar', 'stem', 'element', 'relation'):
        if trace_fact.get(field) != row.get(field):
            raise ValueError(
                f"Action {index}: fact mismatch on {field}")


def _evidence_block(step, step_idx, fact_ref, trace):
    """Build evidence block from a trace step."""
    if not step:
        return None
    evidence_ids = step.get('evidence_ids', [])
    if not evidence_ids:
        return None
    # Get first evidence detail
    first_id = evidence_ids[0]
    ref = trace.evidence.get(first_id, {})
    return {
        'rule_id': step['rule_id'],
        'variant': trace.variant,
        'fact_ref': fact_ref,
        'evidence_id': first_id,
        'evidence_ids': list(evidence_ids),
        'section_id': ref.get('section_id'),
        'source_id': ref.get('source_id'),
        'classic_id': ref.get('classic_id'),
        'evidence_level': ref.get('evidence_level'),
    }


def _verify_evidence_consistency(result, trace, chart):
    """Verify the evidence belongs to this exact execution.

    Strict checks (fail-closed):
    1. Chart pillars/day_master match every trace step's inputs
    2. Every evidence_id exists in trace.evidence AND its ref matches
       the claimed rule_id, variant, source_id, section_id
    3. fact_ref resolves to the actual fact in trace output (not just format)
    4. Root availability and action effects rows correspond 1:1 by index
    """
    import hashlib
    import json
    # 1. Chart pillars match trace inputs
    chart_ganzhi = [(p['stem']['value'], p['branch']['value'])
                    for p in chart['pillars']]
    for step in trace.steps:
        inputs = step.get('inputs', {})
        if 'pillars' in inputs:
            if inputs['pillars'] != chart_ganzhi:
                raise ValueError(
                    f"Trace step {step['rule_id']}: pillars mismatch")
        if 'day_master' in inputs:
            if inputs['day_master'] != chart['day_master']['stem']:
                raise ValueError(
                    f"Trace step {step['rule_id']}: day_master mismatch")
    # Build step index for fact_ref resolution
    steps_by_idx = {i: s for i, s in enumerate(trace.steps)}
    # 2+3. Verify each row's evidence (strict: no skipping)
    for section, rows in (('roots', result['roots']),
                          ('exposures', result['exposures']),
                          ('actions', result['actions'])):
        for idx, row in enumerate(rows):
            # structure_evidence is REQUIRED for all rows (strict)
            sev = row.get('structure_evidence')
            if not sev:
                raise ValueError(
                    f"{section}[{idx}]: missing required structure_evidence")
            # effect_evidence required for effective rows
            eev = row.get('effect_evidence')
            if row.get('status') == 'effective' and not eev:
                raise ValueError(
                    f"{section}[{idx}]: effective without effect_evidence")
            for key, ev in (('structure_evidence', sev),
                            ('effect_evidence', eev)):
                if not ev:
                    continue
                # Verify rule_id matches a real trace step
                rule_id = ev.get('rule_id')
                step_idx = None
                step = None
                for i, s in steps_by_idx.items():
                    if s['rule_id'] == rule_id:
                        step_idx, step = i, s
                        break
                if step is None:
                    raise ValueError(
                        f"{section}[{idx}].{key}: unknown rule_id {rule_id}")
                # Verify variant matches trace
                if ev.get('variant') != trace.variant:
                    raise ValueError(
                        f"{section}[{idx}].{key}: variant mismatch")
                # Verify evidence_id non-empty and evidence_ids non-empty
                eid0 = ev.get('evidence_id')
                eids = ev.get('evidence_ids', [])
                if not eid0:
                    raise ValueError(
                        f"{section}[{idx}].{key}: empty evidence_id")
                if not eids:
                    raise ValueError(
                        f"{section}[{idx}].{key}: empty evidence_ids")
                if eid0 not in eids:
                    raise ValueError(
                        f"{section}[{idx}].{key}: evidence_id not in evidence_ids")
                # Verify evidence_ids belong to this step
                step_eids = set(step.get('evidence_ids', []))
                if not step_eids:
                    raise ValueError(
                        f"{section}[{idx}].{key}: step {rule_id} has no evidence")
                for eid in eids:
                    if eid not in step_eids:
                        raise ValueError(
                            f"{section}[{idx}].{key}: evidence {eid} not from step {rule_id}")
                    ref = trace.evidence.get(eid)
                    if ref is None:
                        raise ValueError(
                            f"{section}[{idx}].{key}: evidence {eid} not in trace")
                    # Verify the hash matches the ref content
                    expected = hashlib.sha256(
                        json.dumps(ref, ensure_ascii=False,
                                   sort_keys=True).encode()).hexdigest()[:24]
                    if expected != eid:
                        raise ValueError(
                            f"{section}[{idx}].{key}: evidence hash mismatch")
                    # Verify ref's rule_id and variant match
                    if ref.get('rule_id') != rule_id:
                        raise ValueError(
                            f"{section}[{idx}].{key}: evidence rule_id mismatch")
                    if ref.get('variant') != trace.variant:
                        raise ValueError(
                            f"{section}[{idx}].{key}: evidence variant mismatch")
                    # Verify metadata fields match the primary evidence_id's ref
                    if eid == eid0:
                        for field in ('source_id', 'section_id', 'classic_id',
                                      'evidence_level'):
                            if ev.get(field) != ref.get(field):
                                raise ValueError(
                                    f"{section}[{idx}].{key}: {field} mismatch")
                # Verify fact_ref resolves to real location AND matches row
                fact_ref = ev.get('fact_ref', '')
                _resolve_fact_ref(fact_ref, steps_by_idx, section, idx, key,
                                  row, rule_id, step_idx)
    # 4. Verify 1:1 correspondence for availability/effects
    _verify_index_correspondence(result, trace)


def _resolve_fact_ref(fact_ref, steps_by_idx, section, idx, key,
                      row, expected_rule_id, expected_step_idx):
    """Resolve fact_ref and verify it matches the row.

    Different fact types have different structures:
    - root structure (root_conditions): pillar, branch, hidden_stem in fact
    - root effect (root_availability): root_index, root_availability (no pillar)
    - action structure (action_conditions): pillar, stem, relation in fact
    - action effect (action_effects): action_index, effect_status (no pillar)
    - exposure: stem, pillar, branch in fact
    """
    if not fact_ref.startswith('#/trace/'):
        raise ValueError(f"{section}[{idx}].{key}: invalid fact_ref {fact_ref}")
    parts = fact_ref[8:].split('/')
    try:
        step_idx = int(parts[0])
    except (ValueError, IndexError):
        raise ValueError(f"{section}[{idx}].{key}: bad step index in {fact_ref}")
    if step_idx != expected_step_idx:
        raise ValueError(
            f"{section}[{idx}].{key}: fact_ref step {step_idx} != "
            f"evidence step {expected_step_idx}")
    step = steps_by_idx.get(step_idx)
    if step is None:
        raise ValueError(f"{section}[{idx}].{key}: step {step_idx} not in trace")
    if step['rule_id'] != expected_rule_id:
        raise ValueError(f"{section}[{idx}].{key}: step rule mismatch")
    node = step.get('output', {})
    for part in parts[2:]:
        if part == 'fact':
            node = node.get('fact', node) if isinstance(node, dict) else node
        elif part.isdigit():
            idx2 = int(part)
            if isinstance(node, list):
                if idx2 >= len(node):
                    raise ValueError(
                        f"{section}[{idx}].{key}: index out of range in {fact_ref}")
                node = node[idx2]
            else:
                raise ValueError(f"{section}[{idx}].{key}: bad path {fact_ref}")
        else:
            if isinstance(node, dict):
                if part not in node:
                    raise ValueError(
                        f"{section}[{idx}].{key}: path not found in {fact_ref}")
                node = node[part]
            else:
                raise ValueError(f"{section}[{idx}].{key}: bad path {fact_ref}")
    if not isinstance(node, dict):
        raise ValueError(f"{section}[{idx}].{key}: fact_ref did not resolve to dict")
    # Verify by fact type (distinguish structure vs effect)
    is_effect = (key == 'effect_evidence')
    if section == 'roots' and not is_effect:
        # Root structure: has pillar, branch, hidden_stem in fact
        for f in ('pillar', 'branch', 'hidden_stem'):
            if node.get(f) != row.get(f):
                raise ValueError(
                    f"{section}[{idx}].{key}: resolved fact {f} mismatch: "
                    f"trace={node.get(f)}, row={row.get(f)}")
    elif section == 'roots' and is_effect:
        # Root effect: has root_index, root_availability (NO pillar)
        if node.get('root_index') != idx:
            raise ValueError(
                f"{section}[{idx}].{key}: root_index mismatch")
        # Verify availability status corresponds
        # (matrix status 'effective' requires availability 'effective')
        if row.get('status') == 'effective':
            if node.get('root_availability') != 'effective':
                raise ValueError(
                    f"{section}[{idx}].{key}: matrix effective but "
                    f"availability is {node.get('root_availability')}")
    elif section == 'exposures':
        # Exposure: fact has stem (hidden), pillar, branch
        if node.get('stem') != row.get('hidden_stem'):
            raise ValueError(f"{section}[{idx}].{key}: stem mismatch")
        if node.get('pillar') != row.get('hidden_pillar'):
            raise ValueError(f"{section}[{idx}].{key}: pillar mismatch")
    elif section == 'actions' and not is_effect:
        # Action structure: pillar, stem, relation in fact
        for f in ('pillar', 'stem', 'relation'):
            if node.get(f) != row.get(f):
                raise ValueError(
                    f"{section}[{idx}].{key}: resolved fact {f} mismatch")
    elif section == 'actions' and is_effect:
        # Action effect: has action_index, effect_status (NO pillar)
        if node.get('action_index') != idx:
            raise ValueError(
                f"{section}[{idx}].{key}: action_index mismatch")


def _verify_index_correspondence(result, trace):
    """Verify strict 1:1 correspondence: lengths, indices, statuses.

    Replicates the status determination in _assemble() against the real
    Rule outputs, so a forged 'effective' can never pass:
    - Roots: branch_relations conflict forbids effective even when
      root_availability == 'effective'; effective requires availability
      'effective' AND no conflict.
    - Actions: effective requires effect_status ==
      'effective_in_reviewed_context'; otherwise conflict -> unresolved,
      else candidate.
    """
    steps = {s['rule_id']: s for s in trace.steps}
    # --- Roots: need root_conditions (conflicts) + root_availability ---
    rc_step = steps.get('bazi.phase2.root_conditions')
    ra_step = steps.get('bazi.phase2.root_availability')
    if rc_step and ra_step:
        rc_roots = rc_step['output'].get('roots', [])
        ra_roots = ra_step['output'].get('roots', [])
        if not (len(rc_roots) == len(ra_roots) == len(result['roots'])):
            raise ValueError(
                f"Root count mismatch: conditions={len(rc_roots)}, "
                f"availability={len(ra_roots)}, matrix={len(result['roots'])}")
        seen = set()
        for r in ra_roots:
            idx = r.get('root_index')
            if idx in seen:
                raise ValueError(f"Duplicate root_index {idx} in availability")
            seen.add(idx)
        for i, row in enumerate(result['roots']):
            rc_entry = rc_roots[i]
            ra_entry = next(
                (r for r in ra_roots if r.get('root_index') == i), None)
            if ra_entry is None:
                raise ValueError(f"Root {i}: missing availability entry")
            # Replicate _assemble status logic
            has_conflict = bool(
                rc_entry.get('conditions', {}).get('branch_relations'))
            avail_status = ra_entry.get('root_availability', 'unresolved')
            if has_conflict:
                expected = 'unresolved'
            elif avail_status == 'effective':
                expected = 'effective'
            elif avail_status == 'conditional':
                expected = 'candidate'
            else:
                expected = 'unresolved'
            if row['status'] != expected:
                raise ValueError(
                    f"Root {i}: matrix status {row['status']!r} != "
                    f"expected {expected!r} (conflict={has_conflict}, "
                    f"availability={avail_status!r})")
    # --- Actions: need action_conditions (conflicts) + action_effects ---
    ac_step = steps.get('bazi.phase2.action_conditions')
    ae_step = steps.get('bazi.phase2.action_effects')
    if ac_step and ae_step:
        ac_visible = ac_step['output'].get('visible_relations', [])
        ae_visible = ae_step['output'].get('visible_relations', [])
        if not (len(ac_visible) == len(ae_visible) == len(result['actions'])):
            raise ValueError(
                f"Action count mismatch: conditions={len(ac_visible)}, "
                f"effects={len(ae_visible)}, matrix={len(result['actions'])}")
        seen = set()
        for e in ae_visible:
            idx = e.get('action_index')
            if idx in seen:
                raise ValueError(f"Duplicate action_index {idx} in effects")
            seen.add(idx)
        eff_by_idx = {e.get('action_index'): e for e in ae_visible}
        for k, row in enumerate(result['actions']):
            ac_entry = ac_visible[k]
            ae_entry = eff_by_idx.get(k)
            if ae_entry is None:
                raise ValueError(f"Action {k}: missing effect entry")
            # Replicate _assemble status logic
            eff_status = ae_entry.get('effect_status', 'unresolved')
            if eff_status == 'effective_in_reviewed_context':
                expected = 'effective'
            else:
                cond = ac_entry.get('conditions', {})
                has_conflict = bool(cond.get('root_branch_relations')) or bool(
                    cond.get('stem_combinations'))
                expected = 'unresolved' if has_conflict else 'candidate'
            if row['status'] != expected:
                raise ValueError(
                    f"Action {k}: matrix status {row['status']!r} != "
                    f"expected {expected!r} (effect_status={eff_status!r})")



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
