"""Product scenario runtime built strictly on reviewed deterministic engines.

The scenario layer may compose already-validated facts. It must not invent chart
facts, promote research material, or turn structural signals into fortune claims.
"""
import copy
from datetime import date

from .bazi_core import ten_god
from .calendar import calendar
from .engine import execute

SCENARIOS = [
    {
        "id": "bazi-profile",
        "name": "八字基础档案",
        "status": "production",
        "public_release": True,
        "execution": "scenario_api",
        "depends_on": ["bazi/ziping-structural-v1"],
        "scope": "四柱、日主、十神、藏干结构事实。",
    },
    {
        "id": "question",
        "name": "一事占问",
        "status": "production",
        "public_release": True,
        "execution": "scenario_api",
        "depends_on": ["liuyao/jingfang-eight-palaces-v1"],
        "scope": "六爻确定性盘面、规则、典籍依据与 Trace。",
    },
    {
        "id": "yearly",
        "name": "年度结构",
        "status": "production_limited",
        "public_release": False,
        "execution": "scenario_api",
        "depends_on": ["bazi/ziping-structural-v1", "calendar/lunar-python==1.4.8"],
        "scope": "原局四柱 + 目标干支年 + 流年天干相对日主的十神结构；不输出年度吉凶。",
    },
    {"id": "daily", "name": "今日结构", "status": "production_limited", "public_release": False, "execution": "scenario_api", "depends_on": ["bazi.phase2.ten_gods", "bazi.phase2.xianchi_lookup", "calendar/lunar-python==1.4.8"], "scope": "返回目标日干支、日干相对日主的十神结构，以及两套咸池目标支是否被当日地支命中；不输出今日吉凶。"},
    {"id": "weekly", "name": "本周运势", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待周运规则与证据。"},
    {"id": "monthly", "name": "本月运势", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待流月规则与证据。"},
    {"id": "romance", "name": "桃花结构", "status": "production_limited", "public_release": False, "execution": "scenario_api", "depends_on": ["bazi/ziping-structural-v1", "bazi.phase2.xianchi_lookup"], "scope": "分别按年支、日支返回咸池目标支、原局命中与目标年份地支激活；不输出婚恋吉凶。"},
    {"id": "career", "name": "事业财运结构", "status": "production_limited", "public_release": False, "execution": "scenario_api", "depends_on": ["bazi.phase2.ten_gods", "bazi.phase2.hidden_stems", "calendar/lunar-python==1.4.8"], "scope": "聚合原局财星、官杀、食伤、印星、比劫的位置事实，并显示目标年天干十神；不输出事业财运吉凶或评分。"},
    {"id": "compatibility", "name": "缘分合盘", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待双人比较规则与证据。"},
    {"id": "dream", "name": "AI 解梦", "status": "research", "public_release": False, "execution": None, "depends_on": ["dream-rag", "ai"], "scope": "待梦境语料与真实模型校准。"},
    {"id": "life", "name": "人生总览", "status": "production_limited", "public_release": False, "execution": "scenario_api", "depends_on": ["bazi-profile", "yearly", "romance", "career"], "scope": "聚合八字基础、年度结构、桃花结构、事业财运结构为一份可读总览；不新增任何吉凶判断。"},
]

_BY_ID = {item["id"]: item for item in SCENARIOS}


def registry():
    return copy.deepcopy(SCENARIOS)


def _normalize_raw(scenario_id, raw):
    return {
        "scenario_id": scenario_id,
        "status": _BY_ID[scenario_id]["status"],
        "public_release": _BY_ID[scenario_id]["public_release"],
        "deterministic": True,
        "result": copy.deepcopy(raw["result"]),
        "rule_matches": copy.deepcopy(raw["rule_matches"]),
        "trace": copy.deepcopy(raw["trace"]),
        "evidence": copy.deepcopy(raw["evidence"]),
        "warnings": [],
        "limitations": [raw.get("scope", ""), *raw.get("unresolved", [])],
    }


def _require_exact(inputs, required):
    if not isinstance(inputs, dict):
        raise ValueError("Scenario input must be a JSON object")
    if set(inputs) != set(required):
        raise ValueError("Scenario input fields do not match the reviewed contract")


def _bazi_profile(inputs):
    _require_exact(inputs, {"value"})
    if not isinstance(inputs["value"], str):
        raise ValueError("value must be an ISO datetime string")
    return _normalize_raw("bazi-profile", execute("bazi", {"value": inputs["value"]}))


def _question(inputs):
    _require_exact(inputs, {"value", "yao_values"})
    return _normalize_raw("question", execute("liuyao", inputs))



def _daily(inputs):
    _require_exact(inputs, {"birth_value", "target_date"})
    birth_value = inputs["birth_value"]
    target_date = inputs["target_date"]
    if not isinstance(birth_value, str):
        raise ValueError("birth_value must be an ISO datetime string")
    if not isinstance(target_date, str):
        raise ValueError("target_date must be YYYY-MM-DD")
    try:
        parsed_date = date.fromisoformat(target_date)
    except ValueError as error:
        raise ValueError("target_date must be YYYY-MM-DD") from error
    if not 1900 <= parsed_date.year <= 2100:
        raise ValueError("target_date year must be from 1900 through 2100")

    natal = execute("bazi", {"value": birth_value, "include_xianchi": True})
    result_chart = natal["result"]
    day_master = result_chart["day_master"]["stem"]
    xianchi = copy.deepcopy(result_chart["xianchi_lookup"])

    target_value = f"{target_date}T12:00:00+08:00"
    target_calendar = calendar(target_value)
    day_ganzhi = target_calendar["day_ganzhi"]
    day_stem, day_branch = day_ganzhi
    day_ten_god = ten_god(day_master, day_stem)
    day_group = _ten_god_group(day_ten_god)

    activation = {
        "year_branch_basis": {
            "target_branch": xianchi["targets"]["year_branch"],
            "target_day_branch": day_branch,
            "matched": day_branch == xianchi["targets"]["year_branch"],
        },
        "day_branch_basis": {
            "target_branch": xianchi["targets"]["day_branch"],
            "target_day_branch": day_branch,
            "matched": day_branch == xianchi["targets"]["day_branch"],
        },
    }

    source_rules = [
        next(rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.ten_gods"),
        next(rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.xianchi_lookup"),
    ]
    evidence_ids = []
    for rule in source_rules:
        for eid in rule["evidence_ids"]:
            if eid not in evidence_ids:
                evidence_ids.append(eid)
    evidence = {eid: copy.deepcopy(natal["evidence"][eid]) for eid in evidence_ids}

    result = {
        "natal": {
            "pillars": copy.deepcopy(result_chart["pillars"]),
            "day_master": copy.deepcopy(result_chart["day_master"]),
        },
        "target_day": {
            "date": target_date,
            "ganzhi": day_ganzhi,
            "stem": day_stem,
            "branch": day_branch,
            "stem_ten_god": day_ten_god,
            "structure_group": day_group,
            "structure_group_label": _TEN_GOD_GROUPS[day_group]["label"] if day_group else None,
            "calendar_provider": target_calendar["calendar_provider"],
            "day_boundary": target_calendar["day_boundary"],
        },
        "xianchi": {
            "basis_policy": "year_and_day_reported_separately",
            "targets": copy.deepcopy(xianchi["targets"]),
            "target_day_activation": activation,
        },
        "summary": {
            "headline": f"{target_date} · {day_ganzhi} · {day_ten_god}",
            "text": (
                f"目标日为{day_ganzhi}；日干{day_stem}相对日主{day_master}为{day_ten_god}。"
                "咸池仅按年支、日支两套固定目标分别检查当日地支是否命中。"
            ),
        },
        "release_scope": "daily_structure_only",
    }
    rule_match = {
        "rule_id": "bazi.scenario.daily_structure",
        "derived_from_rule_ids": ["bazi.phase2.ten_gods", "bazi.phase2.xianchi_lookup"],
        "variant": "ziping-structural-v1",
        "matched": True,
        "kind": "scenario_composition",
        "evidence_scope": "复用已验证十神与咸池 Evidence；只描述当日结构，不输出吉凶。",
        "facts": {
            "target_date": target_date,
            "day_ganzhi": day_ganzhi,
            "day_ten_god": day_ten_god,
            "day_group": day_group,
            "xianchi_activation": copy.deepcopy(activation),
        },
        "evidence_ids": evidence_ids,
    }
    trace = [
        {
            "step": "target_day_calendar",
            "provider": target_calendar["calendar_provider"],
            "inputs": {"target_date": target_date, "value": target_value},
            "facts": {"day_ganzhi": day_ganzhi},
        },
        {
            "step": "target_day_ten_god",
            "derived_from_rule_id": "bazi.phase2.ten_gods",
            "facts": {
                "day_master": day_master,
                "target_day_stem": day_stem,
                "ten_god": day_ten_god,
                "structure_group": day_group,
            },
            "evidence_ids": evidence_ids,
        },
        {
            "step": "target_day_xianchi_activation",
            "derived_from_rule_id": "bazi.phase2.xianchi_lookup",
            "basis_policy": "year_and_day_reported_separately",
            "facts": copy.deepcopy(activation),
            "evidence_ids": evidence_ids,
        },
    ]
    return {
        "scenario_id": "daily",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": result,
        "rule_matches": [rule_match],
        "trace": trace,
        "evidence": evidence,
        "warnings": [
            "今日结构可重复计算，但当前不把十神或咸池命中转换成好运/坏运、宜忌或事件预测。",
        ],
        "limitations": [
            "目标日天干十神只表示与日主的结构关系，不等同于当天事业、财富、感情或健康结果。",
            "咸池当日命中只表示固定查表结构相同，不等同于今天一定有桃花或感情事件。",
            "尚未纳入旺衰、喜用神、大运、流月、流日支互动、时辰变化与完整择日体系。",
            "不提供投资、健康、法律、安全等现实决策建议。",
            "AI 不参与本场景计算。",
        ],
    }


def _yearly(inputs):
    _require_exact(inputs, {"birth_value", "target_year"})
    birth_value = inputs["birth_value"]
    target_year = inputs["target_year"]
    if not isinstance(birth_value, str):
        raise ValueError("birth_value must be an ISO datetime string")
    if type(target_year) is not int or not 1900 <= target_year <= 2100:
        raise ValueError("target_year must be an integer from 1900 through 2100")

    natal = execute("bazi", {"value": birth_value})
    # July 1 is deliberately inside the target solar-term year. The response
    # reports this convention instead of pretending a Gregorian Jan-1 boundary.
    reference = f"{target_year:04d}-07-01T12:00:00+08:00"
    target_calendar = calendar(reference)
    flow_ganzhi = target_calendar["year_ganzhi"]
    flow_stem, flow_branch = flow_ganzhi
    day_master = natal["result"]["day_master"]["stem"]
    flow_ten_god = ten_god(day_master, flow_stem)

    base_rule = next(rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.ten_gods")
    evidence_ids = list(base_rule["evidence_ids"])
    evidence = {eid: copy.deepcopy(natal["evidence"][eid]) for eid in evidence_ids}

    result = {
        "natal": {
            "pillars": copy.deepcopy(natal["result"]["pillars"]),
            "day_master": copy.deepcopy(natal["result"]["day_master"]),
        },
        "target_year": {
            "year": target_year,
            "ganzhi": flow_ganzhi,
            "stem": flow_stem,
            "branch": flow_branch,
            "stem_ten_god": flow_ten_god,
            "calendar_provider": target_calendar["calendar_provider"],
            "year_boundary": "solar-term year; reference date fixed to July 1 for stable annual stem/branch selection",
        },
        "release_scope": "annual_structure_only",
    }
    rule_match = {
        "rule_id": "bazi.scenario.flow_stem_ten_god",
        "derived_from_rule_id": "bazi.phase2.ten_gods",
        "variant": "ziping-structural-v1",
        "matched": True,
        "kind": "scenario_composition",
        "evidence_scope": base_rule["evidence_scope"],
        "facts": {
            "day_master": day_master,
            "flow_year_stem": flow_stem,
            "flow_year_stem_ten_god": flow_ten_god,
        },
        "evidence_ids": evidence_ids,
    }
    trace = [
        {
            "step": "natal_bazi",
            "provider": "bazi/ziping-structural-v1",
            "facts": {"day_master": copy.deepcopy(natal["result"]["day_master"])},
        },
        {
            "step": "target_year_calendar",
            "provider": target_calendar["calendar_provider"],
            "inputs": {"target_year": target_year, "reference": reference},
            "facts": {"year_ganzhi": flow_ganzhi},
        },
        {
            "step": "flow_stem_ten_god",
            "derived_from_rule_id": "bazi.phase2.ten_gods",
            "facts": copy.deepcopy(rule_match["facts"]),
            "evidence_ids": evidence_ids,
        },
    ]
    return {
        "scenario_id": "yearly",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": result,
        "rule_matches": [rule_match],
        "trace": trace,
        "evidence": evidence,
        "warnings": ["年度结构运行层已可用，但当前不对普通用户自动发布年度吉凶解释。"],
        "limitations": [
            "只描述目标干支年与日主的十神结构，不等同于年度运势。",
            "尚未把旺衰、格局、喜用神、流年支与原局冲合等争议规则纳入本生产场景。",
            "不输出桃花、婚恋、事业、财富、健康或事件应期判断。",
            "AI 不参与本场景计算。",
        ],
    }


def _romance(inputs):
    _require_exact(inputs, {"birth_value", "target_year"})
    birth_value = inputs["birth_value"]
    target_year = inputs["target_year"]
    if not isinstance(birth_value, str):
        raise ValueError("birth_value must be an ISO datetime string")
    if type(target_year) is not int or not 1900 <= target_year <= 2100:
        raise ValueError("target_year must be an integer from 1900 through 2100")

    natal = execute("bazi", {"value": birth_value, "include_xianchi": True})
    xianchi = copy.deepcopy(natal["result"]["xianchi_lookup"])
    xianchi_rule = next(
        rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.xianchi_lookup"
    )
    evidence_ids = list(xianchi_rule["evidence_ids"])
    evidence = {eid: copy.deepcopy(natal["evidence"][eid]) for eid in evidence_ids}

    reference = f"{target_year:04d}-07-01T12:00:00+08:00"
    target_calendar = calendar(reference)
    flow_ganzhi = target_calendar["year_ganzhi"]
    flow_branch = flow_ganzhi[1]
    activation = {
        "year_branch_basis": {
            "target_branch": xianchi["targets"]["year_branch"],
            "target_year_branch": flow_branch,
            "matched": flow_branch == xianchi["targets"]["year_branch"],
        },
        "day_branch_basis": {
            "target_branch": xianchi["targets"]["day_branch"],
            "target_year_branch": flow_branch,
            "matched": flow_branch == xianchi["targets"]["day_branch"],
        },
    }
    result = {
        "natal": {
            "pillars": copy.deepcopy(natal["result"]["pillars"]),
            "day_master": copy.deepcopy(natal["result"]["day_master"]),
        },
        "xianchi": {
            "basis_policy": "year_and_day_reported_separately",
            "targets": copy.deepcopy(xianchi["targets"]),
            "natal_matches": copy.deepcopy(xianchi["matches"]),
            "source_warning": xianchi["warning"],
        },
        "target_year": {
            "year": target_year,
            "ganzhi": flow_ganzhi,
            "branch": flow_branch,
            "calendar_provider": target_calendar["calendar_provider"],
            "year_boundary": "solar-term year; reference date fixed to July 1 for stable annual branch selection",
        },
        "target_year_activation": activation,
        "release_scope": "xianchi_structure_only",
    }
    rule_match = {
        "rule_id": "bazi.scenario.xianchi_structure",
        "derived_from_rule_id": "bazi.phase2.xianchi_lookup",
        "variant": "ziping-structural-v1",
        "matched": True,
        "kind": "scenario_composition",
        "evidence_scope": xianchi_rule["evidence_scope"],
        "facts": {
            "targets": copy.deepcopy(xianchi["targets"]),
            "natal_matches": copy.deepcopy(xianchi["matches"]),
            "target_year_branch": flow_branch,
            "target_year_activation": copy.deepcopy(activation),
        },
        "evidence_ids": evidence_ids,
    }
    trace = [
        {
            "step": "natal_xianchi_lookup",
            "derived_from_rule_id": "bazi.phase2.xianchi_lookup",
            "facts": {
                "targets": copy.deepcopy(xianchi["targets"]),
                "natal_matches": copy.deepcopy(xianchi["matches"]),
            },
            "evidence_ids": evidence_ids,
        },
        {
            "step": "target_year_calendar",
            "provider": target_calendar["calendar_provider"],
            "inputs": {"target_year": target_year, "reference": reference},
            "facts": {"year_ganzhi": flow_ganzhi, "year_branch": flow_branch},
        },
        {
            "step": "xianchi_target_year_activation",
            "basis_policy": "year_and_day_reported_separately",
            "facts": copy.deepcopy(activation),
            "evidence_ids": evidence_ids,
        },
    ]
    return {
        "scenario_id": "romance",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": result,
        "rule_matches": [rule_match],
        "trace": trace,
        "evidence": evidence,
        "warnings": [
            "桃花结构运行层已可用，但当前只报告咸池查表事实，不对普通用户自动发布婚恋吉凶解释。",
        ],
        "limitations": [
            "年支与日支两个起查基准分别展示，不裁定其中任何一个为唯一标准。",
            "目标年份是否落在咸池目标支，只表示固定查表结构命中，不等同于桃花旺、恋爱发生或婚姻结果。",
            "《三命通会》相关纳音附加条件尚未纳入自动规则。",
            "尚未组合配偶星、夫妻宫、合冲刑害、旺衰喜忌、紫微等其他婚恋判断体系。",
            "AI 不参与本场景计算。",
        ],
    }


_TEN_GOD_GROUPS = {
    "wealth": {"label": "财星", "ten_gods": ("正财", "偏财")},
    "authority": {"label": "官杀", "ten_gods": ("正官", "七杀")},
    "output": {"label": "食伤", "ten_gods": ("食神", "伤官")},
    "resource": {"label": "印星", "ten_gods": ("正印", "偏印")},
    "peers": {"label": "比劫", "ten_gods": ("比肩", "劫财")},
}


def _ten_god_group(ten_god_name):
    for group_id, meta in _TEN_GOD_GROUPS.items():
        if ten_god_name in meta["ten_gods"]:
            return group_id
    return None


def _career(inputs):
    _require_exact(inputs, {"birth_value", "target_year"})
    birth_value = inputs["birth_value"]
    target_year = inputs["target_year"]
    if not isinstance(birth_value, str):
        raise ValueError("birth_value must be an ISO datetime string")
    if type(target_year) is not int or not 1900 <= target_year <= 2100:
        raise ValueError("target_year must be an integer from 1900 through 2100")

    natal = execute("bazi", {"value": birth_value})
    result_chart = natal["result"]
    groups = {
        group_id: {
            "label": meta["label"],
            "ten_gods": list(meta["ten_gods"]),
            "occurrences": [],
            "visible_count": 0,
            "hidden_count": 0,
        }
        for group_id, meta in _TEN_GOD_GROUPS.items()
    }

    for pillar in result_chart["pillars"]:
        stem = pillar["stem"]
        group_id = _ten_god_group(stem["ten_god"])
        if group_id:
            groups[group_id]["occurrences"].append({
                "pillar": pillar["name"],
                "layer": "visible_stem",
                "stem": stem["value"],
                "ten_god": stem["ten_god"],
            })
            groups[group_id]["visible_count"] += 1
        for hidden in pillar["branch"]["hidden_stems"]:
            group_id = _ten_god_group(hidden["ten_god"])
            if group_id:
                groups[group_id]["occurrences"].append({
                    "pillar": pillar["name"],
                    "layer": "hidden_stem",
                    "branch": pillar["branch"]["value"],
                    "stem": hidden["stem"],
                    "ten_god": hidden["ten_god"],
                })
                groups[group_id]["hidden_count"] += 1

    reference = f"{target_year:04d}-07-01T12:00:00+08:00"
    target_calendar = calendar(reference)
    flow_ganzhi = target_calendar["year_ganzhi"]
    flow_stem, flow_branch = flow_ganzhi
    day_master = result_chart["day_master"]["stem"]
    flow_ten_god = ten_god(day_master, flow_stem)
    flow_group = _ten_god_group(flow_ten_god)

    source_rules = [
        next(rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.ten_gods"),
        next(rule for rule in natal["rule_matches"] if rule["rule_id"] == "bazi.phase2.hidden_stems"),
    ]
    evidence_ids = []
    for rule in source_rules:
        for eid in rule["evidence_ids"]:
            if eid not in evidence_ids:
                evidence_ids.append(eid)
    evidence = {eid: copy.deepcopy(natal["evidence"][eid]) for eid in evidence_ids}

    result = {
        "natal": {
            "pillars": copy.deepcopy(result_chart["pillars"]),
            "day_master": copy.deepcopy(result_chart["day_master"]),
        },
        "structure_groups": groups,
        "target_year": {
            "year": target_year,
            "ganzhi": flow_ganzhi,
            "stem": flow_stem,
            "branch": flow_branch,
            "stem_ten_god": flow_ten_god,
            "structure_group": flow_group,
            "structure_group_label": groups[flow_group]["label"] if flow_group else None,
            "calendar_provider": target_calendar["calendar_provider"],
            "year_boundary": "solar-term year; reference date fixed to July 1 for stable annual stem/branch selection",
        },
        "release_scope": "career_wealth_structure_only",
    }
    rule_match = {
        "rule_id": "bazi.scenario.career_wealth_structure",
        "derived_from_rule_ids": ["bazi.phase2.ten_gods", "bazi.phase2.hidden_stems"],
        "variant": "ziping-structural-v1",
        "matched": True,
        "kind": "scenario_composition",
        "evidence_scope": "复用已验证十神与藏干 Evidence；仅聚合位置事实，不作旺衰或事业财运断语。",
        "facts": {
            "group_counts": {
                key: {
                    "visible_count": value["visible_count"],
                    "hidden_count": value["hidden_count"],
                }
                for key, value in groups.items()
            },
            "target_year_stem": flow_stem,
            "target_year_ten_god": flow_ten_god,
            "target_year_group": flow_group,
        },
        "evidence_ids": evidence_ids,
    }
    trace = [
        {
            "step": "natal_ten_god_locations",
            "derived_from_rule_ids": ["bazi.phase2.ten_gods", "bazi.phase2.hidden_stems"],
            "facts": copy.deepcopy(rule_match["facts"]["group_counts"]),
            "evidence_ids": evidence_ids,
        },
        {
            "step": "target_year_calendar",
            "provider": target_calendar["calendar_provider"],
            "inputs": {"target_year": target_year, "reference": reference},
            "facts": {"year_ganzhi": flow_ganzhi},
        },
        {
            "step": "target_year_ten_god",
            "derived_from_rule_id": "bazi.phase2.ten_gods",
            "facts": {
                "day_master": day_master,
                "target_year_stem": flow_stem,
                "ten_god": flow_ten_god,
                "structure_group": flow_group,
            },
            "evidence_ids": evidence_ids,
        },
    ]
    return {
        "scenario_id": "career",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": result,
        "rule_matches": [rule_match],
        "trace": trace,
        "evidence": evidence,
        "warnings": [
            "事业财运结构运行层已可用，但当前位置数量不代表强弱、吉凶或财富/职业水平。",
        ],
        "limitations": [
            "财星、官杀、食伤、印星、比劫仅按已验证十神映射聚合其出现位置，不比较旺衰、月令权重或组合成败。",
            "目标年天干十神只表示结构关系，不等同于升职、赚钱、失业、投资收益或风险。",
            "尚未纳入格局、喜用神、身强身弱、大运、流年支互动、行业映射与紫微交叉判断。",
            "不输出事业指数、财运指数、收入金额或投资建议。",
            "AI 不参与本场景计算。",
        ],
    }



def _dedupe_strings(items):
    seen = set()
    output = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output


def _life(inputs):
    _require_exact(inputs, {"birth_value", "target_year"})
    birth_value = inputs["birth_value"]
    target_year = inputs["target_year"]
    if not isinstance(birth_value, str):
        raise ValueError("birth_value must be an ISO datetime string")
    if type(target_year) is not int or not 1900 <= target_year <= 2100:
        raise ValueError("target_year must be an integer from 1900 through 2100")

    profile = _bazi_profile({"value": birth_value})
    yearly = _yearly({"birth_value": birth_value, "target_year": target_year})
    romance = _romance({"birth_value": birth_value, "target_year": target_year})
    career = _career({"birth_value": birth_value, "target_year": target_year})

    evidence = {}
    for section in (profile, yearly, romance, career):
        for eid, record in section["evidence"].items():
            evidence.setdefault(eid, copy.deepcopy(record))

    pillars = profile["result"]["pillars"]
    day_master = profile["result"]["day_master"]
    target = yearly["result"]["target_year"]
    romance_result = romance["result"]
    career_result = career["result"]

    year_basis = romance_result["target_year_activation"]["year_branch_basis"]
    day_basis = romance_result["target_year_activation"]["day_branch_basis"]
    romance_activation_count = int(bool(year_basis["matched"])) + int(bool(day_basis["matched"]))

    highlights = [
        {
            "id": "foundation",
            "title": "命盘基础",
            "text": f"四柱为{' · '.join(item['ganzhi'] for item in pillars)}；日主为{day_master['stem']}（{day_master['element']}，{day_master['polarity']}）。",
            "fact_paths": ["/profile/pillars", "/profile/day_master"],
        },
        {
            "id": "yearly",
            "title": f"{target_year} 年结构",
            "text": f"{target_year} 干支为{target['ganzhi']}；流年天干{target['stem']}相对日主{day_master['stem']}为{target['stem_ten_god']}。",
            "fact_paths": ["/yearly/target_year/ganzhi", "/yearly/target_year/stem_ten_god"],
        },
        {
            "id": "romance",
            "title": "桃花结构",
            "text": (
                f"年支基准咸池目标为{romance_result['xianchi']['targets']['year_branch']}，"
                f"日支基准目标为{romance_result['xianchi']['targets']['day_branch']}；"
                f"{target_year} 年地支{romance_result['target_year']['branch']}命中 {romance_activation_count} 个基准。"
            ),
            "fact_paths": ["/romance/xianchi/targets", "/romance/target_year_activation"],
        },
        {
            "id": "career",
            "title": "事业财运结构",
            "text": (
                f"{target_year} 流年天干{career_result['target_year']['stem']}对应"
                f"{career_result['target_year']['stem_ten_god']}，归入"
                f"{career_result['target_year']['structure_group_label'] or '未分组'}结构。"
            ),
            "fact_paths": ["/career/target_year/stem_ten_god", "/career/target_year/structure_group"],
        },
    ]

    rule_matches = []
    trace = []
    for section_id, section in (
        ("profile", profile),
        ("yearly", yearly),
        ("romance", romance),
        ("career", career),
    ):
        for rule in section["rule_matches"]:
            item = copy.deepcopy(rule)
            item["scenario_section"] = section_id
            rule_matches.append(item)
        for step in section["trace"]:
            item = copy.deepcopy(step)
            item["scenario_section"] = section_id
            trace.append(item)

    return {
        "scenario_id": "life",
        "status": "production_limited",
        "public_release": False,
        "deterministic": True,
        "result": {
            "report_version": "life-overview-v1",
            "target_year": target_year,
            "highlights": highlights,
            "profile": {
                "pillars": copy.deepcopy(pillars),
                "day_master": copy.deepcopy(day_master),
            },
            "yearly": copy.deepcopy(yearly["result"]),
            "romance": copy.deepcopy(romance["result"]),
            "career": copy.deepcopy(career["result"]),
            "release_scope": "deterministic_aggregate_only",
        },
        "rule_matches": rule_matches,
        "trace": trace,
        "evidence": evidence,
        "warnings": _dedupe_strings(
            profile["warnings"] + yearly["warnings"] + romance["warnings"] + career["warnings"]
        ),
        "limitations": _dedupe_strings([
            "人生总览只聚合已经通过校验的结构事实，不新增任何吉凶、性格或人生事件推断。",
            *profile["limitations"],
            *yearly["limitations"],
            *romance["limitations"],
            *career["limitations"],
            "AI 不参与本总览计算。",
        ]),
    }


_EXECUTORS = {
    "bazi-profile": _bazi_profile,
    "question": _question,
    "daily": _daily,
    "yearly": _yearly,
    "romance": _romance,
    "career": _career,
    "life": _life,
}


def execute_scenario(scenario_id, inputs):
    if scenario_id not in _BY_ID:
        raise ValueError("Unknown scenario")
    if scenario_id not in _EXECUTORS:
        raise ValueError("Scenario is not executable yet")
    return _EXECUTORS[scenario_id](inputs)
