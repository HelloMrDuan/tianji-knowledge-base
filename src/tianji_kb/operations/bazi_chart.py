"""Evidence-bound Bazi structural chart. No strength, useful-god or fortune judgement."""
from ..bazi_core import VARIANT, chart_from_pillars, reviewed_relations, traditional_spouse_star_lens
from ..resolver import ExecutionTrace
from ..bazi_strength import FACTOR_VARIANT, factors as _strength_factors


def strength_factors(pillars, day_master, *, factor_variant=FACTOR_VARIANT, output_key=None):
    observed = _strength_factors(pillars, day_master, variant=factor_variant)
    if output_key is None:
        return observed
    if output_key not in ('month_command', 'root_candidates', 'hidden_to_visible'):
        raise ValueError('Unsupported factor output')
    return observed[output_key]

def chart(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, include_xianchi=False, include_relations=False, traditional_role=None, strength_variant=None, variant=VARIANT):
    if variant != VARIANT:
        raise ValueError("Unsupported Bazi variant")
    if type(include_xianchi) is not bool:
        raise ValueError("include_xianchi must be boolean")
    if type(include_relations) is not bool:
        raise ValueError("include_relations must be boolean")
    if traditional_role is not None and traditional_role not in ("male", "female"):
        raise ValueError("traditional_role must be male or female")
    if strength_variant is not None and strength_variant != FACTOR_VARIANT:
        raise ValueError("Unsupported strength factor variant")
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
    if include_relations:
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
    if strength_variant is not None:
        observed = strength_factors(raw['pillars'], raw['day_master']['stem'], factor_variant=strength_variant)
        for rule, key in (('month_command_factors', 'month_command'),
                          ('root_candidates', 'root_candidates'),
                          ('hidden_to_visible', 'hidden_to_visible')):
            trace.add('bazi.phase2.' + rule, {'factor_variant': strength_variant,
                      'ganzhi': [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]}, observed[key])
        result['strength_factors'] = observed
        result['production_scope'] += '；可选月支、通根候选与透藏结构观察（整体旺衰分类未完成）'
    return trace.finish(result)
