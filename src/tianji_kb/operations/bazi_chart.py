"""Evidence-bound Bazi structural chart. No strength, useful-god or fortune judgement."""
from ..bazi_core import VARIANT, chart_from_pillars, reviewed_relations, traditional_spouse_star_lens
from ..resolver import ExecutionTrace
from ..bazi_commander import COMMAND_VARIANT, PRINCIPAL_VARIANT, month_command, principal_month, month_factor_graph
from ..bazi_action_conditions import EFFECT_VARIANT, action_conditions, action_effects
from ..bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from ..bazi_root_conditions import STRENGTH_VARIANT, AVAILABILITY_VARIANT, root_conditions, root_availability, conditional_factor_graph
from ..bazi_strength import FACTOR_VARIANT, factors as _strength_factors
from ..bazi_pattern import (PATTERN_VARIANT, candidates as pattern_candidates,
                            month_pattern_route, month_pattern_zaqi)
from ..bazi_tiaohou import VARIANT as TIAOHOU_VARIANT, tiaohou_assessment
from ..bazi_bingyao import VARIANT as BINGYAO_VARIANT, bingyao_assessment
from ..bazi_conflict_presentation import VARIANT as CONFLICT_VARIANT, conflict_presentation
from ..bazi_xiyong_readable import VARIANT as READABLE_VARIANT, readable_hints
from ..bazi_annual_reference import annual_reference, annual_lichun_boundaries
from ..bazi_dayun_sequence import candidate_sequence


def strength_factors(pillars, day_master, *, factor_variant=FACTOR_VARIANT, output_key=None):
    observed = _strength_factors(pillars, day_master, variant=factor_variant)
    if output_key is None:
        return observed
    if output_key not in ('month_command', 'root_candidates', 'hidden_to_visible', 'support_relations'):
        raise ValueError('Unsupported factor output')
    return observed[output_key]

def chart(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, include_xianchi=False, include_relations=False, traditional_role=None, strength_variant=None, month_command_variant=None, root_availability_variant=None, action_effect_variant=None, variant=VARIANT, *, pattern_variant=None, tiaohou_variant=None, bingyao_variant=None, conflict_variant=None, readable_variant=None, annual_reference_years=None, annual_boundary_years=None, dayun_sequence_direction=None, dayun_sequence_count=8):
    if variant != VARIANT:
        raise ValueError("Unsupported Bazi variant")
    if type(include_xianchi) is not bool:
        raise ValueError("include_xianchi must be boolean")
    if type(include_relations) is not bool:
        raise ValueError("include_relations must be boolean")
    if traditional_role is not None and traditional_role not in ("male", "female"):
        raise ValueError("traditional_role must be male or female")
    if annual_reference_years is not None:
        # Validate input before doing any chart computation or executing rules.
        if type(annual_reference_years) is not list or not 1 <= len(annual_reference_years) <= 20:
            raise ValueError('annual_reference_years must be a list of 1..20 years')
    if annual_boundary_years is not None:
        if type(annual_boundary_years) is not list or not 1 <= len(annual_boundary_years) <= 10:
            raise ValueError('annual_boundary_years must be a list of 1..10 years')
    if dayun_sequence_direction is None:
        if type(dayun_sequence_count) is not int or dayun_sequence_count != 8:
            raise ValueError("dayun_sequence_count requires explicit dayun_sequence_direction")
    else:
        if type(dayun_sequence_direction) is not str or dayun_sequence_direction not in ("forward", "backward"):
            raise ValueError("dayun_sequence_direction must be forward or backward")
        if type(dayun_sequence_count) is not int or not 1 <= dayun_sequence_count <= 12:
            raise ValueError("dayun_sequence_count must be an integer from 1 to 12")
    if pattern_variant is not None:
        if pattern_variant != PATTERN_VARIANT:
            raise ValueError('Unsupported pattern candidate variant')
    if tiaohou_variant is not None and tiaohou_variant != TIAOHOU_VARIANT:
        raise ValueError('Unsupported tiaohou variant')
    if bingyao_variant is not None and bingyao_variant != BINGYAO_VARIANT:
        raise ValueError('Unsupported bingyao variant')
    if conflict_variant is not None:
        if conflict_variant != CONFLICT_VARIANT:
            raise ValueError('Unsupported conflict presentation variant')
        if strength_variant != ADJUDICATION_VARIANT \
                or tiaohou_variant is None or bingyao_variant is None:
            raise ValueError(
                'Conflict presentation requires the adjudication, tiaohou '
                'and bingyao variants together')
    if readable_variant is not None:
        if readable_variant != READABLE_VARIANT:
            raise ValueError('Unsupported readable hints variant')
        if conflict_variant is None:
            raise ValueError(
                'Readable hints require the conflict presentation variant '
                '(and thereby the adjudication, tiaohou and bingyao '
                'variants together)')
    conditional_strength = strength_variant in (STRENGTH_VARIANT, ADJUDICATION_VARIANT)
    if strength_variant is not None and strength_variant not in (FACTOR_VARIANT, STRENGTH_VARIANT, ADJUDICATION_VARIANT):
        raise ValueError("Unsupported strength factor variant")
    if month_command_variant is not None and month_command_variant not in (COMMAND_VARIANT, PRINCIPAL_VARIANT):
        raise ValueError('Unsupported month command variant')
    if root_availability_variant is not None and (root_availability_variant != AVAILABILITY_VARIANT or not conditional_strength):
        raise ValueError('Root availability requires its explicit variant and conditional strength factors')
    if action_effect_variant is not None:
        if action_effect_variant != EFFECT_VARIANT or not conditional_strength:
            raise ValueError('Action effects require their explicit variant and conditional strength factors')
        root_availability_variant = AVAILABILITY_VARIANT
    if strength_variant == ADJUDICATION_VARIANT:
        if month_command_variant not in (None, PRINCIPAL_VARIANT):
            raise ValueError('Bounded strength requires the explicit principal-qi policy')
        month_command_variant = PRINCIPAL_VARIANT
        root_availability_variant = AVAILABILITY_VARIANT
        action_effect_variant = EFFECT_VARIANT
    if pattern_variant is not None and month_command_variant is None:
        month_command_variant = COMMAND_VARIANT
    raw = chart_from_pillars(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, variant=variant)
    trace = ExecutionTrace("bazi", variant)

    pillar_fact = trace.add(
        "bazi.phase2.pillars",
        {"year_ganzhi": year_ganzhi, "month_ganzhi": month_ganzhi, "day_ganzhi": day_ganzhi, "hour_ganzhi": hour_ganzhi},
        {"ganzhi": [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi], "day_master": raw["day_master"]},
    )
    stem_ten_gods = trace.add(
        "bazi.phase2.ten_gods",
        {"day_stem": raw["day_master"]["stem"], "target_stems": [item["stem"]["value"] for item in raw["pillars"]]},
        [{"pillar": item["name"], "stem": item["stem"]["value"], "ten_god": item["stem"]["ten_god"]} for item in raw["pillars"]],
    )
    hidden = trace.add(
        "bazi.phase2.hidden_stems",
        {"day_stem": raw["day_master"]["stem"], "branches": [item["branch"]["value"] for item in raw["pillars"]]},
        [{"pillar": item["name"], "branch": item["branch"]["value"], "hidden_stems": item["branch"]["hidden_stems"]} for item in raw["pillars"]],
    )
    xianchi = None
    if include_xianchi:
        xianchi = trace.add(
            "bazi.phase2.xianchi_lookup",
            {
                "basis_policy": "year_and_day_reported_separately",
                "year_branch": year_ganzhi[1],
                "day_branch": day_ganzhi[1],
                "branches": [year_ganzhi[1], month_ganzhi[1], day_ganzhi[1], hour_ganzhi[1]],
            },
            raw["auxiliary"]["taohua"],
        )

    spouse_star_lens = None
    if traditional_role is not None:
        spouse_star_lens = traditional_spouse_star_lens(raw["pillars"], traditional_role)
        trace.add(
            "bazi.phase2.spouse_star_lens",
            {
                "traditional_role": traditional_role,
                "candidate_ten_gods": spouse_star_lens["candidate_ten_gods"],
            },
            spouse_star_lens,
        )

    relation_facts = None
    if include_relations or conditional_strength or pattern_variant is not None:
        stems = [year_ganzhi[0], month_ganzhi[0], day_ganzhi[0], hour_ganzhi[0]]
        branches = [year_ganzhi[1], month_ganzhi[1], day_ganzhi[1], hour_ganzhi[1]]
        relation_facts = reviewed_relations(stems, branches)
        trace.add(
            "bazi.phase2.stem_five_combinations",
            {"stems": stems},
            relation_facts["stem_five_combinations"],
        )
        trace.add(
            "bazi.phase2.branch_six_harmonies",
            {"branches": branches},
            relation_facts["branch_six_harmonies"],
        )
        trace.add(
            "bazi.phase2.branch_six_harms",
            {"branches": branches},
            relation_facts["branch_six_harms"],
        )
        trace.add(
            "bazi.phase2.branch_six_clashes",
            {"branches": branches},
            relation_facts["branch_six_clashes"],
        )
        trace.add(
            "bazi.phase2.branch_triple_harmonies",
            {"branches": branches},
            relation_facts["branch_triple_harmonies"],
        )
        trace.add(
            "bazi.phase2.spouse_palace_day_branch",
            {"day_ganzhi": day_ganzhi},
            relation_facts["spouse_palace"],
        )

    result = {
        "pillars": raw["pillars"],
        "day_master": raw["day_master"],
        "stem_ten_gods": stem_ten_gods,
        "hidden_stems": hidden,
        "limitations": raw["limitations"],
        "production_scope": "四柱、日主、十神、藏干结构事实",
    }
    if xianchi is not None:
        result["xianchi_lookup"] = xianchi
        result["production_scope"] += "；可选咸池四组结构查表（年支/日支分别报告，不作婚恋吉凶解释）"
    if relation_facts is not None:
        result["reviewed_relations"] = relation_facts
        result["production_scope"] += "；可选已审核五合、六合、六害、六冲、三合与日支传统配偶宫结构位（只报结构，不作关系吉凶解释）"
    if spouse_star_lens is not None:
        result["traditional_spouse_star_lens"] = spouse_star_lens
        result["production_scope"] += "；可选传统配偶星候选位置（用户显式选择口径，仅定位星位，不作婚恋解释）"
    if strength_variant is not None or pattern_variant is not None:
        observed = strength_factors(raw['pillars'], raw['day_master']['stem'], factor_variant=FACTOR_VARIANT)
        for rule, key in (('month_command_factors', 'month_command'),
                          ('root_candidates', 'root_candidates'),
                          ('hidden_to_visible', 'hidden_to_visible'),
                          ('support_relations', 'support_relations')):
            if strength_variant is None and rule != 'hidden_to_visible':
                continue
            trace.add('bazi.phase2.' + rule, {'factor_variant': FACTOR_VARIANT,
                      'ganzhi': [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]}, observed[key])
        if strength_variant is not None:
            result['strength_factors'] = observed
            result['production_scope'] += '；可选月支、通根候选、透藏与生克位置观察（整体旺衰分类未完成）'
    if month_command_variant is not None or conditional_strength:
        command = month_command(raw['pillars'], raw['day_master']['stem'], command_variant=COMMAND_VARIANT)
        trace.add('bazi.phase2.month_command_variant',
                  {'command_variant': COMMAND_VARIANT, 'month_branch': month_ganzhi[1]}, command)
        result['month_command_variant'] = command
        result['strength_factor_graph'] = month_factor_graph(trace, command)
        result['production_scope'] += '；可选独立月令口径审计（具体日司令 unresolved）'
        if month_command_variant == PRINCIPAL_VARIANT or root_availability_variant is not None:
            principal = principal_month(command, raw['day_master']['stem'])
            trace.add('bazi.phase2.principal_month', {'command_variant': PRINCIPAL_VARIANT}, principal)
            result['principal_month'] = principal
    if conditional_strength:
        roots = root_conditions(raw['pillars'], raw['day_master']['stem'],
                                relations=relation_facts, month_command=command)
        trace.add('bazi.phase2.root_conditions', {'strength_variant': strength_variant,
                  'ganzhi': [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]}, roots)
        result['root_conditions'] = roots
        if root_availability_variant is not None:
            availability = root_availability(roots, root_variant=root_availability_variant)
            trace.add('bazi.phase2.root_availability', {'root_variant': root_availability_variant}, availability)
            result['root_availability'] = availability
        action = action_conditions(raw['pillars'], raw['day_master']['stem'],
                                   support=observed['support_relations'],
                                   relations=relation_facts, month_command=command)
        trace.add('bazi.phase2.action_conditions', {'strength_variant': strength_variant,
                  'ganzhi': [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]}, action)
        result['action_conditions'] = action
        if action_effect_variant is not None:
            effects = action_effects(raw['pillars'], observed=action, relations=relation_facts,
                                     principal=principal, availability=availability)
            trace.add('bazi.phase2.action_effects', {'action_variant': action_effect_variant}, effects)
            result['action_effects'] = effects
        result['strength_factor_graph'] = conditional_factor_graph(trace)
        assessment = strength_assessment(trace, strength_variant=strength_variant)
        gate = 'strength_bounded_adjudication' if strength_variant == ADJUDICATION_VARIANT else 'strength_adjudication'
        trace.add('bazi.phase2.' + gate,
                  {'strength_variant': strength_variant}, assessment)
        result['strength_assessment'] = assessment
        if strength_variant == ADJUDICATION_VARIANT:
            graph = result['strength_factor_graph']
            graph['variant'] = strength_variant
            graph['overall_strength'] = assessment['classification']
            graph['variant_dependencies'] = assessment['variant_dependencies']
            graph['adjudication_fact_ref'] = f'#/trace/{len(trace.steps)-1}/output'
            for i, step in enumerate(trace.steps):
                if step['rule_id'] in ('bazi.phase2.principal_month','bazi.phase2.root_availability','bazi.phase2.action_effects'):
                    graph['factors'].append({'id':step['rule_id'].removeprefix('bazi.phase2.'),
                        'fact_ref':f'#/trace/{i}/output','rule_id':step['rule_id'],
                        'evidence_ids':step['evidence_ids'],'status':'bounded_conditional',
                        'variant':step['output'].get('command_variant',step['output'].get('root_variant',step['output'].get('action_variant')))})
        result['production_scope'] += ('；定性木根可用性与有限实际作用，通用根力仍未裁定'
            if strength_variant == ADJUDICATION_VARIANT else '；条件化根候选（可用性与实际根力未裁定）')
    if annual_reference_years is not None:
        annual = annual_reference(raw['day_master']['stem'], annual_reference_years)
        trace.add('bazi.phase2.annual_reference_facts',
                  {'annual_reference_years': list(annual_reference_years),
                   'reference_policy': annual['reference_policy']},
                  annual)
        result['annual_reference'] = annual
        result['production_scope'] += '；研究用指定公历年份七月一日干支与日主十神参照（不构成流年吉凶或完整岁运）'
    if annual_boundary_years is not None:
        boundary = annual_lichun_boundaries(raw['day_master']['stem'], annual_boundary_years)
        trace.add('bazi.phase2.annual_li_chun_boundaries',
                  {'annual_boundary_years': list(annual_boundary_years),
                   'boundary_policy': boundary['boundary_policy']},
                  boundary)
        result['annual_li_chun_boundaries'] = boundary
        result['production_scope'] += '；研究用精确到历法库秒级的立春干支年区间（不推断运势）'
    if dayun_sequence_direction is not None:
        sequence = candidate_sequence(month_ganzhi, raw['day_master']['stem'],
                                      direction=dayun_sequence_direction, periods=dayun_sequence_count)
        # Not an ExecutionTrace.add: a Dayun-specific classical method has NOT
        # passed Phase1/Phase2 source review. Keep explicit month-pillar lineage.
        result['dayun_sequence_research'] = sequence
        result['production_scope'] += '；显式研究用月柱相邻干支候选（顺逆及起运法尚未审核，非正式大运排盘）'
    if pattern_variant is not None:
        result['pattern_candidates'] = {}
        for family in ('official', 'resource'):
            observation = pattern_candidates(trace, family=family, pattern_variant=pattern_variant)
            trace.add('bazi.phase2.' + family + '_pattern_candidates',
                      {'pattern_variant': pattern_variant, 'family': family}, observation)
            result['pattern_candidates'][family] = observation
        # TJ-012.3 Slice A: Ren 禄刃 route exclusion over the executed
        # pillars only. Not a trace.add: this route rule has no sealed
        # Phase1 rule / Phase2 contract registration yet, so it must not
        # enter RuleMatch or Evidence (see bazi_pattern adjudication
        # notes); it attaches to the result beside the candidates.
        result['pattern_route'] = month_pattern_route(trace)
        # TJ-012.3 Slice B: 杂气 selection statement over the executed
        # structural facts. Same registration status as Slice A: not a
        # trace.add, no RuleMatch or Evidence entry.
        result['pattern_zaqi'] = month_pattern_zaqi(trace)
        result['production_scope'] += '；研究用正官/印绶月藏透干候选位置，不定格或判断成败喜用；含任氏禄刃路线负向裁定（月逢禄刃无格可取、借用路线未定），不定格名真假用神；含杂气月选格陈述（原注分支：戊己日看人元透出、一般日主只录原文不换算土格）与三命杂气格流派冲突并列，不定格名真假用神'
    if tiaohou_variant is not None:
        # TJ-013.1: consumes only the executed pillar/ten-god/hidden-stem
        # steps above. Not a trace.add: this Variant has no sealed Phase1
        # rule / Phase2 contract registration yet, so the assessment must
        # not enter RuleMatch or Evidence (see bazi_tiaohou docstring).
        result['tiaohou_assessment'] = tiaohou_assessment(trace, tiaohou_variant=tiaohou_variant)
        result['production_scope'] += '；研究用《穷通宝鉴》甲木十二月调候条目陈述（仅原文取用顺序与存在性事实，不作吉凶、喜用结论，不公开）'
    if bingyao_variant is not None:
        # TJ-013: consumes only the executed pillar/ten-god steps above.
        # Not a trace.add: this Variant has no sealed Phase1 rule /
        # Phase2 contract registration yet, so the assessment must
        # not enter RuleMatch or Evidence (see bazi_bingyao docstring).
        result['bingyao_assessment'] = bingyao_assessment(trace, bingyao_variant=bingyao_variant)
        result['production_scope'] += '；研究用《神峰通考》病药结构候选（仅财—比劫—官杀一对的存在性事实，不作病药裁定、喜用结论，不公开）'
    if conflict_variant is not None:
        # TJ-013.2 phase 1: pure presentation over the three executed
        # assessments above (the variant validation block guarantees all
        # three were requested). Not a trace.add: the layer adds no rule
        # and no evidence (see bazi_conflict_presentation docstring).
        result['conflict_presentation'] = conflict_presentation(
            result['tiaohou_assessment'], result['bingyao_assessment'],
            result['strength_assessment'])
        result['production_scope'] += '；研究用跨体系冲突呈现（只并列呈现各体系陈述与关系分类，不作跨体系裁决、统一喜用结论，不公开）'
    if readable_variant is not None:
        # TJ-013.3 phase 1: deterministic template rendering over the
        # four executed/carried research objects above. Not a trace.add:
        # the layer adds no rule, no evidence and no judgement (see
        # bazi_xiyong_readable docstring).
        result['readable_hints'] = readable_hints(
            result['tiaohou_assessment'], result['bingyao_assessment'],
            result['strength_assessment'], result['conflict_presentation'])
        result['production_scope'] += '；研究用喜用结果可读提示（确定性模板渲染已裁定结构化陈述，不新增判断、不公开）'
    output = trace.finish(result)
    if strength_variant == ADJUDICATION_VARIANT or pattern_variant is not None or tiaohou_variant is not None or bingyao_variant is not None or conflict_variant is not None or readable_variant is not None or annual_reference_years is not None or annual_boundary_years is not None or dayun_sequence_direction is not None:
        output['interpretation_contract']['ai_may_explain'] = False
        output['research_only'] = True
    if strength_variant == ADJUDICATION_VARIANT:
        result['production_scope'] += '；显式研究 Variant 增加有限充分条件强弱裁决，不授权公开深度解释'
    return output
