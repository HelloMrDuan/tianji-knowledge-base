"""Deterministic Bazi structural facts.

This module intentionally stops before strength (旺衰), useful-god selection,
pattern judgement, auspiciousness, Dayun start age, or life-event prediction.
It only derives reproducible structure from the existing canonical tables.
"""
import json
from functools import lru_cache
from pathlib import Path

from .calendar import calendar
from .foundations import BRANCHES, CONTROLS, GENERATES, STEMS, ganzhi_index, stem_element

ROOT = Path(__file__).resolve().parents[2]
VARIANT = "ziping-structural-v1"
PILLAR_NAMES = ("year", "month", "day", "hour")


@lru_cache(maxsize=1)
def foundations():
    return json.loads((ROOT / "data/canonical/bazi/foundations_v1.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def shensha():
    return json.loads((ROOT / "data/canonical/bazi/shensha_v1.json").read_text(encoding="utf-8"))


def _stem_row(stem):
    if stem not in STEMS:
        raise ValueError("Expected one heavenly stem")
    return next(row for row in foundations()["heavenly_stems"] if row["stem"] == stem)


def ten_god(day_stem, target_stem):
    """Return the Ten-God relation of target_stem relative to day_stem."""
    day = _stem_row(day_stem)
    target = _stem_row(target_stem)
    day_element = day["element"]
    target_element = target["element"]
    same_polarity = day["polarity"] == target["polarity"]
    rules = foundations()["ten_gods_rule"]

    if day_element == target_element:
        relation = "same_element"
    elif GENERATES[target_element] == day_element:
        relation = "generates_me"
    elif GENERATES[day_element] == target_element:
        relation = "i_generate"
    elif CONTROLS[target_element] == day_element:
        relation = "controls_me"
    elif CONTROLS[day_element] == target_element:
        relation = "i_control"
    else:  # The five-element graph should make this unreachable.
        raise ValueError("Unresolvable five-element relation")
    return rules[relation]["same_polarity" if same_polarity else "different_polarity"]


def hidden_stems(branch, day_stem):
    table = foundations()["hidden_stems"]
    if branch not in table:
        raise ValueError("Expected one earthly branch")
    return [{"stem": stem, "ten_god": ten_god(day_stem, stem)} for stem in table[branch]]


def _pair_members(rows):
    return {frozenset(row[:2]): row[2:] for row in rows}


def stem_five_combination(left_stem, right_stem):
    """Return the reviewed fixed 五合 pair fact for two stems, if present."""
    if left_stem not in STEMS or right_stem not in STEMS:
        raise ValueError("Expected two heavenly stems")
    table = _pair_members(foundations()["stem_combinations"])
    extra = table.get(frozenset((left_stem, right_stem)))
    return {
        "matched": extra is not None,
        "stems": [left_stem, right_stem],
        "traditional_result_element": extra[0] if extra else None,
    }


def reviewed_branch_pair_relations(left_branch, right_branch):
    """Return only branch pair relations that have reviewed production evidence."""
    if left_branch not in BRANCHES or right_branch not in BRANCHES:
        raise ValueError("Expected two earthly branches")
    relation = foundations()["earthly_branch_relations"]
    harmonies = _pair_members(relation["six_harmonies"])
    harms = _pair_members(relation["harms"])
    clashes = _pair_members(relation["clashes"])
    key = frozenset((left_branch, right_branch))
    output = []
    if key in harmonies:
        extra = harmonies[key]
        output.append({
            "kind": "six_harmony",
            "branches": [left_branch, right_branch],
            "traditional_result_element": extra[0] if extra else None,
        })
    if key in harms:
        output.append({"kind": "harm", "branches": [left_branch, right_branch]})
    if key in clashes:
        output.append({"kind": "clash", "branches": [left_branch, right_branch]})
    return output


def reviewed_relations(stems, branches):
    """Return evidence-backed relation facts among four pillars only."""
    if not isinstance(stems, (list, tuple)) or len(stems) != 4:
        raise ValueError("Expected four heavenly stems")
    if not isinstance(branches, (list, tuple)) or len(branches) != 4:
        raise ValueError("Expected four earthly branches")
    if any(stem not in STEMS for stem in stems):
        raise ValueError("Invalid heavenly stem")
    if any(branch not in BRANCHES for branch in branches):
        raise ValueError("Invalid earthly branch")

    stem_pairs = []
    harmonies = []
    harms = []
    clashes = []
    for i in range(4):
        for j in range(i + 1, 4):
            stem_relation = stem_five_combination(stems[i], stems[j])
            if stem_relation["matched"]:
                stem_pairs.append({
                    "pillars": [PILLAR_NAMES[i], PILLAR_NAMES[j]],
                    "stems": [stems[i], stems[j]],
                    "traditional_result_element": stem_relation["traditional_result_element"],
                })
            for item in reviewed_branch_pair_relations(branches[i], branches[j]):
                row = {
                    "pillars": [PILLAR_NAMES[i], PILLAR_NAMES[j]],
                    "branches": [branches[i], branches[j]],
                }
                if item["kind"] == "six_harmony":
                    row["traditional_result_element"] = item["traditional_result_element"]
                    harmonies.append(row)
                elif item["kind"] == "harm":
                    harms.append(row)
                elif item["kind"] == "clash":
                    clashes.append(row)

    triple_harmonies = []
    for item in foundations()["earthly_branch_relations"]["triple_harmonies"]:
        members = item[:3]
        if all(branch in branches for branch in members):
            triple_harmonies.append({
                "pillars": [PILLAR_NAMES[branches.index(branch)] for branch in members],
                "branches": members,
                "traditional_result_element": item[3],
            })

    return {
        "stem_five_combinations": stem_pairs,
        "branch_six_harmonies": harmonies,
        "branch_six_harms": harms,
        "branch_six_clashes": clashes,
        "branch_triple_harmonies": triple_harmonies,
        "spouse_palace": {
            "pillar": "day",
            "day_branch": branches[2],
            "label": "日支（传统配偶宫结构位）",
        },
    }


def traditional_spouse_star_lens(pillars, traditional_role):
    """Locate traditional spouse-star candidates without inferring relationship outcomes."""
    if traditional_role not in ("male", "female"):
        raise ValueError("traditional_role must be male or female")
    if not isinstance(pillars, (list, tuple)) or len(pillars) != 4:
        raise ValueError("Expected four structured pillars")

    candidates = ("正财", "偏财") if traditional_role == "male" else ("正官", "七杀")
    visible = []
    hidden = []
    for pillar in pillars:
        stem = pillar["stem"]
        if stem["ten_god"] in candidates:
            visible.append({
                "pillar": pillar["name"],
                "stem": stem["value"],
                "ten_god": stem["ten_god"],
            })
        for item in pillar["branch"]["hidden_stems"]:
            if item["ten_god"] in candidates:
                hidden.append({
                    "pillar": pillar["name"],
                    "branch": pillar["branch"]["value"],
                    "stem": item["stem"],
                    "ten_god": item["ten_god"],
                })

    return {
        "traditional_role": traditional_role,
        "role_basis": "user_selected_traditional_lens",
        "candidate_ten_gods": list(candidates),
        "visible_positions": visible,
        "hidden_positions": hidden,
        "interpretation_allowed": False,
    }


def branch_relations(branches):
    """Return only structural branch relations present in the four pillars."""
    if not isinstance(branches, (list, tuple)) or len(branches) != 4:
        raise ValueError("Expected four earthly branches")
    if any(branch not in BRANCHES for branch in branches):
        raise ValueError("Invalid earthly branch")

    relation = foundations()["earthly_branch_relations"]
    clashes = _pair_members(relation["clashes"])
    harmonies = _pair_members(relation["six_harmonies"])
    harms = _pair_members(relation["harms"])
    pairs = []
    for i in range(4):
        for j in range(i + 1, 4):
            key = frozenset((branches[i], branches[j]))
            if key in clashes:
                pairs.append({"kind": "clash", "pillars": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "branches": [branches[i], branches[j]]})
            if key in harmonies:
                extra = harmonies[key]
                pairs.append({"kind": "six_harmony", "pillars": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "branches": [branches[i], branches[j]], "result_element": extra[0] if extra else None})
            if key in harms:
                pairs.append({"kind": "harm", "pillars": [PILLAR_NAMES[i], PILLAR_NAMES[j]], "branches": [branches[i], branches[j]]})

    branch_set = set(branches)
    groups = []
    for kind, key in (("triple_harmony", "triple_harmonies"), ("directional_meeting", "directional_meetings")):
        for row in relation[key]:
            needed = set(row[:3])
            if needed.issubset(branch_set):
                groups.append({"kind": kind, "branches": row[:3], "result_element": row[3]})
    return {"pairs": pairs, "groups": groups}


def taohua_matches(year_branch, day_branch, branches):
    """Compute only the fixed 桃花/咸池 lookup from the reviewed table."""
    if any(branch not in BRANCHES for branch in (year_branch, day_branch, *branches)):
        raise ValueError("Invalid earthly branch")
    item = next(x for x in shensha()["items"] if x["name"] == "桃花/咸池")
    table = item["table"]

    def target_for(basis):
        for group, target in table.items():
            if basis in group:
                return target
        raise ValueError("Incomplete 桃花 table")

    targets = {"year_branch": target_for(year_branch), "day_branch": target_for(day_branch)}
    matches = []
    for basis, target in targets.items():
        for index, branch in enumerate(branches):
            if branch == target:
                matches.append({"basis": basis, "target_branch": target, "pillar": PILLAR_NAMES[index]})
    return {"targets": targets, "matches": matches, "warning": shensha()["warning"]}


def chart_from_pillars(year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi, *, variant=VARIANT):
    if variant != VARIANT:
        raise ValueError("Unsupported Bazi variant")
    pillars = [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]
    for pillar in pillars:
        ganzhi_index(pillar)

    day_stem = day_ganzhi[0]
    structured = []
    for name, pillar in zip(PILLAR_NAMES, pillars):
        stem, branch = pillar
        structured.append({
            "name": name,
            "ganzhi": pillar,
            "stem": {
                "value": stem,
                "element": stem_element(stem),
                "polarity": _stem_row(stem)["polarity"],
                "ten_god": "日主" if name == "day" else ten_god(day_stem, stem),
            },
            "branch": {
                "value": branch,
                "hidden_stems": hidden_stems(branch, day_stem),
            },
        })

    branches = [pillar[1] for pillar in pillars]
    return {
        "domain": "bazi",
        "variant": variant,
        "deterministic": True,
        "pillars": structured,
        "day_master": {
            "stem": day_stem,
            "element": stem_element(day_stem),
            "polarity": _stem_row(day_stem)["polarity"],
        },
        "branch_relations": branch_relations(branches),
        "auxiliary": {
            "taohua": taohua_matches(year_ganzhi[1], day_ganzhi[1], branches),
        },
        "limitations": [
            "不计算旺衰强弱。",
            "不选择喜用神、格局或调候结论。",
            "不输出吉凶、婚恋、事业、财富或健康断语。",
            "不计算大运起运岁数。",
            "神煞仅保留固定查表事实，不作为独立结论。",
        ],
    }


def chart_from_datetime(value, *, day_boundary="midnight", variant=VARIANT):
    cal = calendar(value, day_boundary=day_boundary)
    result = chart_from_pillars(
        cal["year_ganzhi"],
        cal["month_ganzhi"],
        cal["day_ganzhi"],
        cal["hour_ganzhi"],
        variant=variant,
    )
    return {**result, "calendar": cal}


def annual_context_from_datetime(birth_value, target_value, *, day_boundary="midnight", variant=VARIANT):
    """Return structural natal-vs-flow-year facts only.

    target_value should be a real date in the year being inspected; the pinned
    calendar adapter therefore preserves the actual solar-term year boundary.
    """
    natal = chart_from_datetime(birth_value, day_boundary=day_boundary, variant=variant)
    target_calendar = calendar(target_value, day_boundary=day_boundary)
    flow = target_calendar["year_ganzhi"]
    flow_stem, flow_branch = flow
    day_stem = natal["day_master"]["stem"]
    natal_branches = [item["branch"]["value"] for item in natal["pillars"]]

    pair_relations = []
    relation = foundations()["earthly_branch_relations"]
    clashes = _pair_members(relation["clashes"])
    harmonies = _pair_members(relation["six_harmonies"])
    harms = _pair_members(relation["harms"])
    for index, branch in enumerate(natal_branches):
        key = frozenset((branch, flow_branch))
        if key in clashes:
            pair_relations.append({"kind": "clash", "natal_pillar": PILLAR_NAMES[index], "natal_branch": branch, "flow_branch": flow_branch})
        if key in harmonies:
            extra = harmonies[key]
            pair_relations.append({"kind": "six_harmony", "natal_pillar": PILLAR_NAMES[index], "natal_branch": branch, "flow_branch": flow_branch, "result_element": extra[0] if extra else None})
        if key in harms:
            pair_relations.append({"kind": "harm", "natal_pillar": PILLAR_NAMES[index], "natal_branch": branch, "flow_branch": flow_branch})

    taohua = natal["auxiliary"]["taohua"]["targets"]
    return {
        "domain": "bazi",
        "variant": variant,
        "deterministic": True,
        "natal": natal,
        "flow_year": {
            "ganzhi": flow,
            "stem": flow_stem,
            "branch": flow_branch,
            "stem_ten_god": ten_god(day_stem, flow_stem),
            "calendar": target_calendar,
        },
        "structural_interactions": pair_relations,
        "taohua_activation": {
            "year_branch_basis": flow_branch == taohua["year_branch"],
            "day_branch_basis": flow_branch == taohua["day_branch"],
            "target_branches": taohua,
        },
        "limitations": [
            "这里只描述流年干支与原局的结构关系，不等同于年度吉凶。",
            "不根据单一冲合、十神或桃花标记生成财运、婚恋、事业结论。",
            "完整年度报告仍需旺衰/格局等争议规则完成证据裁定后再开放。",
        ],
    }
