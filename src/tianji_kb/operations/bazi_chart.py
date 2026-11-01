"""Evidence-bound Bazi structural chart. No strength, useful-god or fortune judgement."""
from ..bazi_core import VARIANT, chart_from_pillars, reviewed_relations, traditional_spouse_star_lens
from ..resolver import ExecutionTrace
from ..bazi_commander import COMMAND_VARIANT, PRINCIPAL_VARIANT, month_command, principal_month, month_factor_graph
from ..bazi_action_conditions import EFFECT_VARIANT, action_conditions, action_effects
from ..bazi_adjudication import ADJUDICATION_VARIANT, strength_assessment
from ..bazi_root_conditions import STRENGTH_VARIANT, AVAILABILITY_VARIANT, root_conditions, root_availability, conditional_factor_graph
from ..bazi_strength import FACTOR_VARIANT, factors as _strength_factors
from ..bazi_pattern import (PATTERN_VARIANT, candidates as pattern_candidates,
                            month_pattern_route, month_pattern_zaqi,
                            ren_yin_true_pattern)
from ..bazi_tiaohou import VARIANT as TIAOHOU_VARIANT, tiaohou_assessment
from ..bazi_bingyao import VARIANT as BINGYAO_VARIANT, bingyao_assessment
from ..bazi_conflict_presentation import VARIANT as CONFLICT_VARIANT, conflict_presentation
from ..bazi_xiyong_readable import VARIANT as READABLE_VARIANT, readable_hints
from ..bazi_annual_reference import annual_reference, annual_lichun_boundaries
from ..bazi_dayun_sequence import candidate_sequence
from ..bazi_dayun_classical import (classical_direction,
                                    sanming_convert_measurement,
                                    shenfeng_convert_measurement,
                                    validate_classical_direction)
from ..bazi_sanxing_facts import reviewed_branch_punishment_facts


def strength_factors(pillars, day_master, *, factor_variant=FACTOR_VARIANT, output_key=None):
    observed = _strength_factors(pillars, day_master, variant=factor_variant)
    if output_key is None:
        return observed
    if output_key not in ('month_command', 'root_candidates', 'hidden_to_visible', 'support_relations'):
        raise ValueError('Unsupported factor output')
    return observed[output_key]

def chart(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, include_xianchi=False, include_relations=False, traditional_role=None, strength_variant=None, month_command_variant=None, root_availability_variant=None, action_effect_variant=None, variant=VARIANT, *, pattern_variant=None, tiaohou_variant=None, bingyao_variant=None, conflict_variant=None, readable_variant=None, annual_reference_years=None, annual_boundary_years=None, dayun_sequence_direction=None, dayun_sequence_count=8, include_punishment_facts=False, ren_yin_pilot_result=None, dayun_classical_role=None, dayun_sanming_measurement=None, dayun_shenfeng_measurement=None):
    if variant != VARIANT:
        raise ValueError("Unsupported Bazi variant")
    if type(include_xianchi) is not bool:
        raise ValueError("include_xianchi must be boolean")
    if type(include_relations) is not bool:
        raise ValueError("include_relations must be boolean")
    if type(include_punishment_facts) is not bool:
        raise ValueError("include_punishment_facts must be boolean")
    if ren_yin_pilot_result is not None and not isinstance(ren_yin_pilot_result, dict):
        raise ValueError("ren_yin_pilot_result must be an explicit pilot result object")
    if dayun_classical_role is not None and dayun_classical_role not in ("male", "female"):
        raise ValueError("dayun_classical_role must be male or female")
    if dayun_sanming_measurement is not None and not isinstance(dayun_sanming_measurement, dict):
        raise ValueError("dayun_sanming_measurement must be an explicit measurement object")
    if dayun_shenfeng_measurement is not None and not isinstance(dayun_shenfeng_measurement, dict):
        raise ValueError("dayun_shenfeng_measurement must be an explicit measurement object")
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

    # TJ-018.3 execution-binding batch 1 (E0333, design
    # TJ0183_EXECUTION_BINDING_DESIGN §2): the sanxing structural
    # fact layer enters production execution at exactly this one
    # gated step. The step is a registered Phase2 fact step
    # (bazi.phase2.branch_punishment_facts -> bazi.rule.r031): it
    # only reports group configurations, directed pairs and
    # self-punishments present; it produces no RuleMatch, is never
    # a sufficient_rule, and feeds no adjudication input. Default
    # off: the default envelope stays byte-identical.
    punishment_facts = None
    if include_punishment_facts:
        branches = [year_ganzhi[1], month_ganzhi[1], day_ganzhi[1],
                    hour_ganzhi[1]]
        punishment_facts = reviewed_branch_punishment_facts(branches)
        trace.add(
            "bazi.phase2.branch_punishment_facts",
            {"branches": branches},
            punishment_facts,
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
    if punishment_facts is not None:
        result["branch_punishment_facts"] = punishment_facts
        result["production_scope"] += "；研究用三刑结构事实（只报组态、有向对与自刑在场，不作吉凶解释）"
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
    if dayun_classical_role is not None or dayun_sanming_measurement is not None or dayun_shenfeng_measurement is not None:
        # TJ-017.1 classical Dayun, Sanming segment. Governance
        # dayun Sanming-segment registration (E0346): the direction
        # and the Sanming measurement conversion are registered
        # (Phase1 bazi.rule.r038 / bazi.rule.r039, Phase2
        # bazi.phase2.dayun_classical_direction /
        # bazi.phase2.dayun_sanming_conversion; Canonical sections
        # s068/s069 bind the direction rule quote, the vol-11
        # direction witness and the eight conversion quotes), so
        # they execute through trace.add like the other registered
        # steps and enter RuleMatch and Evidence. Governance
        # Shenfeng expansion (E0348): the Shenfeng conversion
        # segment is registered the same way (Phase1 bazi.rule.r041
        # / Phase2 bazi.phase2.dayun_shenfeng_conversion; Canonical
        # section s073 in the new classic bazi.classic.shenfeng
        # binds its three consumed conversion examples) and executes
        # here through the same gated pattern.
        # chart() carries no birth instant: the traditional role
        # and the TJ-015 measurements stay explicit caller-supplied
        # input claims, cross-checked against the executed pillars
        # (month ganzhi; direction consistency when both are
        # supplied), and each measurement is additionally
        # replay-validated inside its convert_measurement entry.
        # Defaults None: the default envelope stays byte-identical.
        direction_result = None
        if dayun_classical_role is not None:
            direction_result = classical_direction(
                year_ganzhi, traditional_role=dayun_classical_role)
            validate_classical_direction(direction_result)
        conversion_result = None
        if dayun_sanming_measurement is not None:
            if dayun_sanming_measurement.get(
                    'birth_month_ganzhi') != month_ganzhi:
                raise ValueError(
                    'dayun_sanming_measurement month ganzhi does '
                    'not match the executed month pillar')
            conversion_result = sanming_convert_measurement(
                dayun_sanming_measurement)
            if direction_result is not None and \
                    conversion_result['direction'] != \
                    direction_result['direction']:
                raise ValueError(
                    'dayun_sanming_measurement direction does not '
                    'match the classical direction for the supplied '
                    'role')
        if direction_result is not None:
            trace.add('bazi.phase2.dayun_classical_direction',
                      {'dayun_classical_role': dayun_classical_role,
                       'year_ganzhi': year_ganzhi},
                      direction_result)
            result['dayun_classical_direction'] = direction_result
        if conversion_result is not None:
            trace.add('bazi.phase2.dayun_sanming_conversion',
                      {'measurement_variant':
                       dayun_sanming_measurement['variant'],
                       'direction': conversion_result['direction'],
                       'birth_month_ganzhi': month_ganzhi},
                      conversion_result)
            result['dayun_sanming_conversion'] = conversion_result
        shenfeng_result = None
        if dayun_shenfeng_measurement is not None:
            if dayun_shenfeng_measurement.get(
                    'birth_month_ganzhi') != month_ganzhi:
                raise ValueError(
                    'dayun_shenfeng_measurement month ganzhi does '
                    'not match the executed month pillar')
            shenfeng_result = shenfeng_convert_measurement(
                dayun_shenfeng_measurement)
            if direction_result is not None and \
                    shenfeng_result['direction'] != \
                    direction_result['direction']:
                raise ValueError(
                    'dayun_shenfeng_measurement direction does not '
                    'match the classical direction for the supplied '
                    'role')
        if shenfeng_result is not None:
            trace.add('bazi.phase2.dayun_shenfeng_conversion',
                      {'measurement_variant':
                       dayun_shenfeng_measurement['variant'],
                       'direction': shenfeng_result['direction'],
                       'birth_month_ganzhi': month_ganzhi},
                      shenfeng_result)
            result['dayun_shenfeng_conversion'] = shenfeng_result
        result['production_scope'] += '；研究用古典大运方向与换算（三命、神峰两分段均已注册：显式性别角色与节距测量为输入声明，只输出方向与交运时长区间，不输出年龄、不接公开页面）'
    if pattern_variant is not None:
        result['pattern_candidates'] = {}
        for family in ('official', 'resource'):
            observation = pattern_candidates(trace, family=family, pattern_variant=pattern_variant)
            trace.add('bazi.phase2.' + family + '_pattern_candidates',
                      {'pattern_variant': pattern_variant, 'family': family}, observation)
            result['pattern_candidates'][family] = observation
        # TJ-012.3 Slice A: Ren 禄刃 route exclusion over the executed
        # pillars only. TJ-018.3 B-2 (E0339): the route is registered
        # (Phase1 bazi.rule.r035 / Phase2 bazi.phase2.pattern_route,
        # Canonical sections s063/s064 bind the Sanming lu/ren table
        # quotes), so it now executes through trace.add like the
        # candidate steps above and enters RuleMatch and Evidence;
        # the route block itself attaches to the result beside the
        # candidates, byte-identical apart from its registration
        # disclosure fields.
        route = month_pattern_route(trace)
        trace.add('bazi.phase2.pattern_route',
                  {'pattern_variant': pattern_variant}, route)
        result['pattern_route'] = route
        # TJ-012.3 Slice B: 杂气 selection statement over the executed
        # structural facts. Governance zaqi promotion (E0342): the
        # statement is registered (Phase1 bazi.rule.r036 / Phase2
        # bazi.phase2.pattern_zaqi, Canonical sections s065/s066/s067
        # bind the Ren passage and the two Sanming conflict witnesses),
        # so it now executes through trace.add like the route step
        # above and enters RuleMatch and Evidence; the statement block
        # itself attaches to the result beside the route,
        # byte-identical apart from its registration disclosure fields.
        zaqi = month_pattern_zaqi(trace)
        trace.add('bazi.phase2.pattern_zaqi',
                  {'pattern_variant': pattern_variant}, zaqi)
        result['pattern_zaqi'] = zaqi
        result['production_scope'] += '；研究用正官/印绶月藏透干候选位置，不定格或判断成败喜用；含任氏禄刃路线负向裁定（月逢禄刃无格可取、借用路线未定），不定格名真假用神；含杂气月选格陈述（原注分支：戊己日看人元透出、一般日主只录原文不换算土格）与三命杂气格流派冲突并列，不定格名真假用神'
        if ren_yin_pilot_result is not None:
            # TJ-012.3 Slice D-1: Ren-branch 寅月 true-pattern
            # determination over the executed structural facts and an
            # EXPLICIT Slice C pilot result. Governance execution
            # binding (E0344): the determination is registered
            # (Phase1 bazi.rule.r037 / Phase2
            # bazi.phase2.ren_yin_true_pattern, Canonical sections
            # s053/s054/s024 bind the definition, procedure and
            # segment quotes), so it now executes through trace.add
            # like the route/zaqi steps above and enters RuleMatch
            # and Evidence; the block itself attaches to the result
            # beside the zaqi statement, byte-identical apart from
            # its registration disclosure fields. chart() carries no
            # birth instant or Jie declarations and never calls the
            # pilot itself (adjudication D4): the pilot block stays
            # an explicit caller-supplied input claim, identity-pinned
            # and cross-checked against executed facts by the
            # composition function (adjudication D6). Default None:
            # the default envelope stays byte-identical.
            ren_yin = ren_yin_true_pattern(trace, ren_yin_pilot_result)
            trace.add('bazi.phase2.ren_yin_true_pattern',
                      {'pattern_variant': pattern_variant,
                       'pilot_variant': ren_yin['pilot']['variant']},
                      ren_yin)
            result['pattern_determination_ren_yin'] = ren_yin
            result['production_scope'] += '；含任氏寅月真格裁定（显式司令试点结果为输入声明：司令透于年/月/时干则真格成立，不透则无真格；不输出假格、成败、清浊、用神，不外推其他月份）'
    if tiaohou_variant is not None:
        # TJ-013.1 lookup, governance-registered by the TJ-018.3
        # tiaohou promotion (E0352): the Variant is registered
        # (Phase1 bazi.rule.r042-r051 / Phase2
        # bazi.phase2.tiaohou_assessment; Canonical classic
        # bazi.classic.qiongtong, sections s075-s184, binds the entry
        # quotes), so it now executes through trace.add like the
        # bingyao step below and enters RuleMatch and Evidence; the
        # block itself stays byte-identical apart from its
        # evidence_binding registration field.
        tiaohou = tiaohou_assessment(trace, tiaohou_variant=tiaohou_variant)
        trace.add('bazi.phase2.tiaohou_assessment',
                  {'tiaohou_variant': tiaohou_variant}, tiaohou)
        result['tiaohou_assessment'] = tiaohou
        result['production_scope'] += '；研究用《穷通宝鉴》甲木十二月调候条目陈述（仅原文取用顺序与存在性事实，不作吉凶、喜用结论，不公开）'
    if bingyao_variant is not None:
        # TJ-013: consumes only the executed pillar/ten-god steps above.
        # Governance Shenfeng expansion (E0348): the Variant is
        # registered (Phase1 bazi.rule.r040 / Phase2
        # bazi.phase2.bingyao_assessment; Canonical sections s071/s072
        # in the new classic bazi.classic.shenfeng and s074 in
        # 滴天髓 bind its consumed quotes), so the assessment —
        # computed from the executed steps exactly as before — now
        # executes through trace.add and enters RuleMatch and
        # Evidence. The assessment block is unchanged apart from its
        # registration disclosure (evidence_binding).
        assessment = bingyao_assessment(trace, bingyao_variant=bingyao_variant)
        trace.add('bazi.phase2.bingyao_assessment',
                  {'bingyao_variant': bingyao_variant}, assessment)
        result['bingyao_assessment'] = assessment
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
    if strength_variant == ADJUDICATION_VARIANT or pattern_variant is not None or tiaohou_variant is not None or bingyao_variant is not None or conflict_variant is not None or readable_variant is not None or annual_reference_years is not None or annual_boundary_years is not None or dayun_sequence_direction is not None or include_punishment_facts or dayun_classical_role is not None or dayun_sanming_measurement is not None or dayun_shenfeng_measurement is not None:
        output['interpretation_contract']['ai_may_explain'] = False
        output['research_only'] = True
    if strength_variant == ADJUDICATION_VARIANT:
        result['production_scope'] += '；显式研究 Variant 增加有限充分条件强弱裁决，不授权公开深度解释'
    return output
