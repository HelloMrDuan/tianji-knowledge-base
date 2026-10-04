"""Product scenario runtime built strictly on reviewed deterministic engines.

The scenario layer may compose already-validated facts. It must not invent chart
facts, promote research material, or turn structural signals into fortune claims.
"""
import copy

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
    {"id": "daily", "name": "今日运势", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待日运规则与证据。"},
    {"id": "weekly", "name": "本周运势", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待周运规则与证据。"},
    {"id": "monthly", "name": "本月运势", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待流月规则与证据。"},
    {"id": "romance", "name": "桃花姻缘", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi", "ziwei"], "scope": "待姻缘场景规则与证据。"},
    {"id": "career", "name": "事业财运", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi", "ziwei"], "scope": "待事业财运聚合规则与证据。"},
    {"id": "compatibility", "name": "缘分合盘", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "待双人比较规则与证据。"},
    {"id": "dream", "name": "AI 解梦", "status": "research", "public_release": False, "execution": None, "depends_on": ["dream-rag", "ai"], "scope": "待梦境语料与真实模型校准。"},
    {"id": "life", "name": "人生全盘", "status": "building", "public_release": False, "execution": None, "depends_on": ["bazi"], "scope": "基础档案可用，完整人生报告待补。"},
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


_EXECUTORS = {
    "bazi-profile": _bazi_profile,
    "question": _question,
    "yearly": _yearly,
}


def execute_scenario(scenario_id, inputs):
    if scenario_id not in _BY_ID:
        raise ValueError("Unknown scenario")
    if scenario_id not in _EXECUTORS:
        raise ValueError("Scenario is not executable yet")
    return _EXECUTORS[scenario_id](inputs)
