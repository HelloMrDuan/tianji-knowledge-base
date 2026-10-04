"""Evidence-bound Bazi structural chart. No strength, useful-god or fortune judgement."""
from ..bazi_core import VARIANT, chart_from_pillars
from ..resolver import ExecutionTrace

def chart(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, variant=VARIANT):
    if variant != VARIANT:
        raise ValueError("Unsupported Bazi variant")
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
    result = {
        "pillars": raw["pillars"],
        "day_master": raw["day_master"],
        "stem_ten_gods": stem_ten_gods,
        "hidden_stems": hidden,
        "limitations": raw["limitations"],
        "production_scope": "四柱、日主、十神、藏干结构事实",
    }
    return trace.finish(result)
