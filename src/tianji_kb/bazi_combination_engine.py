"""原局 / 大运 / 流年组合引擎（TJ-0424，B3/B4 已批准）。

只消费已有的可执行输出，不产生新规则、新裁定：

- 原局结构：调用方传入的四柱（与 ``bazi_core.chart_from_pillars`` 的
  结构形态一致）；
- 大运干支及十神：调用方传入的 ``candidate_sequence`` 行
  （``bazi-dayun-month-sequence-research-v1``）；
- 流年干支及十神：本模块按六十甲子表由目标年份推导（与
  ``bazi-annual-lichun-boundary-v1`` 核对年干支的同一公式
  ``CYCLE[(year - 4) % 60]``；立春交界、年内分界不在此推导范围）；
- 干支关系：下文转录的已审关系表——与
  ``bazi_core.stem_five_combination`` /
  ``bazi_core.reviewed_branch_pair_relations`` /
  ``bazi_core.branch_relations`` 所消费的同一 canonical 表一致
  （``data/canonical/bazi/foundations_v1.json`` 的
  ``stem_combinations`` 与 ``earthly_branch_relations``），
  密封环境下的专项测试逐项核对转录与 canonical 表一致，漂移即失败。
  本模块不 import ``bazi_core``（它依赖历法 provider 与密封数据），
  只依赖纯常量模块 ``foundations``，因此在公开检出也可执行；
  关系表本身是通用传统配对事实，不含密封文本引文。
- 强弱 / 喜用：调用方传入的 ``factors()``、``tiaohou_lookup()``、
  ``bingyao_lookup()``、格局候选输出，本模块只原样转述并校验其
  variant 与 release 旗标，不重算、不合并。

输出明确区分三层，缺一不可：

1. 结构关系层（``structural_relations``）：大运×原局、流年×原局、
   大运×流年的干支关系列表，只报结构事实，不推效力。
2. 条件判断层：每条关系附触发条件与前提（已满足 / 未满足 /
   无法判定），引用所消费的已审规则 ID。
3. 效力层（``effects``）：只写有依据的效力；本模块无任何已审跨层
   效力规则可用（TJ-017.2 与 TJ-023.3 均阻塞），故每条效力一律
   abstain 并写明理由，绝不把缺少依据的效力判断写成已经完成。

喜用神综合分析契约（``xiyong``）：扶抑、调候、病药、格局用神四体系
并列输出，各体系原样消费现有输出，不新造判断；
``unified_verdict`` 恒为 None（TJ-013.2 裁决 A：并列呈现、统一裁决
拒判）。流年喜用部分只完成数据契约与规则调用结构，完整推演待对应
规则获批后接入，契约中显式标注已实现段与待批段。

恒 research_only=True、public_enabled=False、ai_enabled=False；
任何输入漂移或缺失一律 fail-closed（ValueError），不静默补全。
"""

import copy

from .foundations import BRANCHES, CYCLE, GENERATES, CONTROLS, STEMS, ganzhi_index, stem_element

VARIANT = "bazi-combination-engine-v1"
XIYONG_CONTRACT_VARIANT = "bazi-xiyong-combination-contract-v1"

# 已审规则 ID（只列本模块实际消费的；流年干支推导只用六十甲子表，
# 不冒充已调用 annual_lichun_boundaries）。
RULE_PILLARS = "bazi.phase2.pillars"
RULE_TEN_GODS = "bazi.phase2.ten_gods"
RULE_STEM_COMBINATIONS = "bazi.phase2.stem_five_combinations"
RULE_SIX_HARMONIES = "bazi.phase2.branch_six_harmonies"
RULE_HARMS = "bazi.phase2.branch_six_harms"
RULE_CLASHES = "bazi.phase2.branch_six_clashes"
RULE_TRIPLE_HARMONIES = "bazi.phase2.branch_triple_harmonies"
RULE_DIRECTIONAL_MEETINGS = "bazi.phase2.branch_directional_meetings"
RULE_DAYUN_SEQUENCE = "bazi-dayun-month-sequence-research-v1"
RULE_TIAOHOU_ASSESSMENT = "bazi.phase2.tiaohou_assessment"
RULE_BINGYAO_ASSESSMENT = "bazi.phase2.bingyao_assessment"
RULE_STRENGTH_FACTORS = "ditiansui-root-visibility-v1"
RULE_PATTERN_CANDIDATES = "bazi-pattern-structure-candidates-v1"
RULE_FUYI_SLICE = "bazi-fuyi-slice-adjudication-v1"

PILLAR_NAMES = ("year", "month", "day", "hour")

# --- 转录的已审关系表 -----------------------------------------------
# 来源：data/canonical/bazi/foundations_v1.json（stem_combinations 与
# earthly_branch_relations）；与 bazi_core 的三个已审函数消费同一表。
# 刑（punishment）在已审表中不存在，故本模块不评估刑，只登记未评估。

# 五合：(甲, 己) -> 土，余类推。frozenset 作键，值取化气之行。
STEM_FIVE_COMBINATIONS = {
    frozenset(("甲", "己")): "土",
    frozenset(("乙", "庚")): "金",
    frozenset(("丙", "辛")): "水",
    frozenset(("丁", "壬")): "木",
    frozenset(("戊", "癸")): "火",
}
# 六合：值取合化之行；午未一项原文作“火/土(有争议)”，逐字保留。
BRANCH_SIX_HARMONIES = {
    frozenset(("子", "丑")): "土",
    frozenset(("寅", "亥")): "木",
    frozenset(("卯", "戌")): "火",
    frozenset(("辰", "酉")): "金",
    frozenset(("巳", "申")): "水",
    frozenset(("午", "未")): "火/土(有争议)",
}
BRANCH_HARMS = {
    frozenset(("子", "未")),
    frozenset(("丑", "午")),
    frozenset(("寅", "巳")),
    frozenset(("卯", "辰")),
    frozenset(("申", "亥")),
    frozenset(("酉", "戌")),
}
BRANCH_CLASHES = {
    frozenset(("子", "午")),
    frozenset(("丑", "未")),
    frozenset(("寅", "申")),
    frozenset(("卯", "酉")),
    frozenset(("辰", "戌")),
    frozenset(("巳", "亥")),
}
# 三合 / 方位会：(成员三支, 成局之行)。
BRANCH_TRIPLE_HARMONIES = (
    (("申", "子", "辰"), "水"),
    (("亥", "卯", "未"), "木"),
    (("寅", "午", "戌"), "火"),
    (("巳", "酉", "丑"), "金"),
)
BRANCH_DIRECTIONAL_MEETINGS = (
    (("寅", "卯", "辰"), "木"),
    (("巳", "午", "未"), "火"),
    (("申", "酉", "戌"), "金"),
    (("亥", "子", "丑"), "水"),
)

# 十神判定表（与 foundations_v1.json 的 ten_gods_rule 逐字一致；
# 阳干为同性、阴干为异性，见 foundations 的 polarity 约定）。
_TEN_GOD_BY_RELATION = {
    "same_element": {"same_polarity": "比肩", "different_polarity": "劫财"},
    "generates_me": {"same_polarity": "偏印", "different_polarity": "正印"},
    "i_generate": {"same_polarity": "食神", "different_polarity": "伤官"},
    "controls_me": {"same_polarity": "七杀", "different_polarity": "正官"},
    "i_control": {"same_polarity": "偏财", "different_polarity": "正财"},
}
_STEM_POLARITY = {stem: ("阳" if i % 2 == 0 else "阴")
                  for i, stem in enumerate(STEMS)}

LIMITATIONS = (
    "本引擎只报告跨层干支结构事实，不推断任何效力：无已审跨层效力规则 "
    "（TJ-017.2 原局＋大运＋流年跨规则调用阻塞，TJ-023.3 流年用神阻塞），"
    "效力层一律 abstain。",
    "合化是否成立未裁定：五合、六合、三合只报配对事实，化气成立需另行 "
    "审定的合化规则（《渊海》合化事实审定亦只记 unresolved）。",
    "刑未评估：已审地支关系表（canonical foundations_v1.json 的 "
    "earthly_branch_relations）不含刑表，本引擎不自行补刑表、不评估刑。",
    "大运与流年的期位映射未裁定：大运起运岁数、交运时刻未在本引擎计算； "
    "除非调用方显式指定当期运及其依据，否则流年落在哪一运记为未确定， "
    "大运×流年关系按逐运列举，不指定当期。",
    "流年干支只按公历年份的六十甲子表推导，不裁定立春交界与年内分界； "
    "精确的流年边界以 bazi-annual-lichun-boundary-v1 为准，本引擎不代行。",
    "扶抑零行可建（bazi-fuyi-slice-adjudication-v1，buildable_count=0）； "
    "B2（2026-11-25 裁决）重开扶抑三模型仍无可执行模型，本契约不预判其结论。",
    "喜用四体系并列呈现、统一裁决恒拒判（TJ-013.2 裁决 A）；流年喜用完整 "
    "推演待对应规则获批，契约只含数据与调用结构。",
    "本引擎不注册 Phase1/Phase2 rule，不进 RuleMatch 与 Evidence； "
    "恒 research_only=True、public_enabled=False、ai_enabled=False。",
)


def ten_god_for(day_master, target_stem):
    """十神：与 bazi_core.ten_god 同一判定（五行关系＋阴阳同异性）。

    只依赖 foundations 的纯常量与 canonical ten_gods_rule 的转录表。
    """
    if day_master not in STEMS or target_stem not in STEMS:
        raise ValueError("ten_god_for requires two heavenly stems")
    day_element = stem_element(day_master)
    target_element = stem_element(target_stem)
    if target_element == day_element:
        relation = "same_element"
    elif GENERATES[target_element] == day_element:
        relation = "generates_me"
    elif GENERATES[day_element] == target_element:
        relation = "i_generate"
    elif CONTROLS[target_element] == day_element:
        relation = "controls_me"
    elif CONTROLS[day_element] == target_element:
        relation = "i_control"
    else:  # 五行生克图应使此分支不可达。
        raise ValueError("Unresolvable five-element relation")
    polarity = ("same_polarity"
                if _STEM_POLARITY[day_master] == _STEM_POLARITY[target_stem]
                else "different_polarity")
    return _TEN_GOD_BY_RELATION[relation][polarity]


def _five_element_direction(from_element, to_element):
    """从 from_element 看 to_element 的五行方向事实（只报方向，不报效力）。"""
    if from_element == to_element:
        return "same"
    if GENERATES[from_element] == to_element:
        return "generates"
    if GENERATES[to_element] == from_element:
        return "generated_by"
    if CONTROLS[from_element] == to_element:
        return "controls"
    if CONTROLS[to_element] == from_element:
        return "controlled_by"
    raise ValueError("Unresolvable five-element direction")


def _fail(message):
    raise ValueError(message)


def _stem_of(pillar, label):
    stem = pillar.get("stem")
    if isinstance(stem, dict):
        stem = stem.get("value")
    if type(stem) is not str or stem not in STEMS:
        _fail("%s stem must be one heavenly stem" % label)
    return stem


def _branch_of(pillar, label):
    branch = pillar.get("branch")
    if isinstance(branch, dict):
        branch = branch.get("value")
    if type(branch) is not str or branch not in BRANCHES:
        _fail("%s branch must be one earthly branch" % label)
    return branch


def _normalize_pillars(natal_pillars, day_master):
    if type(natal_pillars) is not list or len(natal_pillars) != 4:
        _fail("natal_pillars must be four ordered year/month/day/hour pillars")
    normalized = []
    for index, pillar in enumerate(natal_pillars):
        name = PILLAR_NAMES[index]
        if isinstance(pillar, str):
            ganzhi_index(pillar)  # 校验六十甲子合法性
            stem, branch = pillar[0], pillar[1]
            row = {"name": name, "ganzhi": pillar, "stem": stem,
                   "branch": branch}
        elif isinstance(pillar, dict):
            if pillar.get("name", name) != name:
                _fail("natal pillar order must be year/month/day/hour")
            stem = _stem_of(pillar, name)
            branch = _branch_of(pillar, name)
            ganzhi = pillar.get("ganzhi")
            if ganzhi is not None and ganzhi != stem + branch:
                _fail("natal pillar ganzhi disagrees with its stem and branch")
            row = {"name": name, "ganzhi": stem + branch, "stem": stem,
                   "branch": branch}
        else:
            _fail("natal pillar must be a ganzhi string or a pillar object")
        supplied = None
        if isinstance(pillar, dict) and isinstance(pillar.get("stem"), dict):
            supplied = pillar["stem"].get("ten_god")
        computed = ("日主" if name == "day"
                    else ten_god_for(day_master, row["stem"]))
        if supplied is not None and supplied != computed:
            _fail("natal pillar ten_god disagrees with the reviewed ten-god rule")
        row["stem_ten_god"] = computed
        row["stem_element"] = stem_element(row["stem"])
        normalized.append(row)
    if normalized[2]["stem"] != day_master:
        _fail("day_master must equal the day pillar stem")
    return normalized


def _normalize_dayun(dayun_periods, day_master):
    if type(dayun_periods) is not list or not dayun_periods:
        _fail("dayun_periods must be a non-empty list of sequence rows")
    seen = set()
    normalized = []
    for row in dayun_periods:
        if not isinstance(row, dict):
            _fail("dayun period must be a sequence row object")
        period_index = row.get("period_index")
        if type(period_index) is not int or not 1 <= period_index <= 12:
            _fail("dayun period_index must be an integer from 1 to 12")
        if period_index in seen:
            _fail("dayun period_index duplicated")
        seen.add(period_index)
        ganzhi = row.get("candidate_ganzhi", row.get("ganzhi"))
        if type(ganzhi) is not str:
            _fail("dayun period must carry candidate_ganzhi or ganzhi")
        ganzhi_index(ganzhi)
        stem, branch = ganzhi[0], ganzhi[1]
        if row.get("stem") is not None and row["stem"] != stem:
            _fail("dayun period stem disagrees with its ganzhi")
        if row.get("branch") is not None and row["branch"] != branch:
            _fail("dayun period branch disagrees with its ganzhi")
        supplied = row.get("ten_god_relative_to_natal_day_stem",
                           row.get("ten_god"))
        computed = ten_god_for(day_master, stem)
        if supplied is not None and supplied != computed:
            _fail("dayun period ten_god disagrees with the reviewed ten-god rule")
        normalized.append({
            "period_index": period_index,
            "candidate_ganzhi": ganzhi,
            "stem": stem,
            "branch": branch,
            "stem_ten_god": computed,
            "stem_element": stem_element(stem),
        })
    normalized.sort(key=lambda r: r["period_index"])
    return normalized


def _flow_year(target_year, day_master):
    if type(target_year) is not int or not 1900 <= target_year <= 2098:
        _fail("target_year must be an integer calendar year 1900..2098")
    ganzhi = CYCLE[(target_year - 4) % 60]
    return {
        "target_year": target_year,
        "ganzhi": ganzhi,
        "stem": ganzhi[0],
        "branch": ganzhi[1],
        "stem_ten_god": ten_god_for(day_master, ganzhi[0]),
        "stem_element": stem_element(ganzhi[0]),
        "derivation": "sexagenary_cycle_index",
        "derivation_note": ("年干支按六十甲子表 CYCLE[(year-4)%60] 推导，与 "
                            "bazi-annual-lichun-boundary-v1 的核对公式一致；"
                            "立春交界与年内分界不在此推导范围。"),
    }


def _side(layer, *, pillar=None, period_index=None, stem, branch,
          stem_ten_god):
    side = {"layer": layer, "stem": stem, "branch": branch,
            "stem_ten_god": stem_ten_god,
            "stem_element": stem_element(stem)}
    if pillar is not None:
        side["pillar"] = pillar
    if period_index is not None:
        side["period_index"] = period_index
    return side


def _condition(condition_id, statement, status, rule_ids, basis=None):
    row = {"id": condition_id, "statement": statement, "status": status,
           "rule_ids": list(rule_ids)}
    if basis is not None:
        row["basis"] = basis
    return row


def _abstain(reason, rule_ids):
    return {"verdict": None, "status": "abstain", "reason": reason,
            "rule_ids": list(rule_ids)}


_ABSTAIN_EFFECT_REASON = (
    "无已审跨层效力规则：TJ-017.2（原局＋大运＋流年跨规则调用）与 "
    "TJ-023.3（流年用神）均阻塞；结构事实本身不推效力，故拒判。"
)


def _stem_pair_relations(counter, scope, side_a, side_b, *, period_index,
                         mapping_condition):
    """一对天干之间的结构关系：五合（若命中）＋五行方向事实（恒报）。"""
    rows = []
    key = frozenset((side_a["stem"], side_b["stem"]))
    if key in STEM_FIVE_COMBINATIONS:
        counter[0] += 1
        rows.append({
            "id": "R%03d" % counter[0],
            "scope": scope,
            "period_index": period_index,
            "side_a": copy.deepcopy(side_a),
            "side_b": copy.deepcopy(side_b),
            "kind": "stem_five_combination",
            "detail": {
                "stems": [side_a["stem"], side_b["stem"]],
                "traditional_result_element":
                    STEM_FIVE_COMBINATIONS[key],
            },
            "conditions": [
                _condition(
                    "both_sides_attested",
                    "双方天干均由已审输入给出",
                    "satisfied", [RULE_PILLARS, RULE_TEN_GODS]),
                _condition(
                    "combination_transformation",
                    "五合配对成立，但合化是否成立未裁定：化气成立需另行审定的合化规则",
                    "cannot_judge", [RULE_STEM_COMBINATIONS]),
            ] + ([mapping_condition] if mapping_condition else []),
            "effect": _abstain(
                _ABSTAIN_EFFECT_REASON + "合化未裁定亦不得据合推效力。",
                [RULE_STEM_COMBINATIONS]),
            "rule_ids": [RULE_STEM_COMBINATIONS, RULE_TEN_GODS],
        })
    counter[0] += 1
    rows.append({
        "id": "R%03d" % counter[0],
        "scope": scope,
        "period_index": period_index,
        "side_a": copy.deepcopy(side_a),
        "side_b": copy.deepcopy(side_b),
        "kind": "stem_five_element",
        "detail": {
            "stems": [side_a["stem"], side_b["stem"]],
            "elements": [side_a["stem_element"], side_b["stem_element"]],
            "direction_from_a_to_b": _five_element_direction(
                side_a["stem_element"], side_b["stem_element"]),
            "ten_gods": [side_a["stem_ten_god"], side_b["stem_ten_god"]],
        },
        "conditions": [
            _condition(
                "both_sides_attested",
                "双方天干与五行均由已审输入与 foundations 常量给出",
                "satisfied", [RULE_PILLARS, RULE_TEN_GODS]),
            _condition(
                "generating_controlling_effect",
                "生克方向事实不等于效力：生扶克泄耗的实际效力未裁定（整体强弱未判）",
                "cannot_judge", [RULE_TEN_GODS]),
        ] + ([mapping_condition] if mapping_condition else []),
        "effect": _abstain(_ABSTAIN_EFFECT_REASON, [RULE_TEN_GODS]),
        "rule_ids": [RULE_TEN_GODS],
    })
    return rows


def _branch_pair_relations(counter, scope, side_a, side_b, *, period_index,
                           mapping_condition):
    """一对地支之间的已审关系：六合 / 害 / 冲（刑不在已审表中，不评估）。"""
    rows = []
    key = frozenset((side_a["branch"], side_b["branch"]))
    specs = (
        ("branch_six_harmony", "six_harmony", BRANCH_SIX_HARMONIES,
         RULE_SIX_HARMONIES,
         "六合配对成立，但合化是否成立未裁定：化气成立需另行审定的合化规则",
         "combination_transformation"),
        ("branch_harm", "harm", BRANCH_HARMS, RULE_HARMS,
         "害的结构事实已报，但害的效力（是否损局、应期）未裁定：无已审跨层害效力规则",
         "harm_effect"),
        ("branch_clash", "clash", BRANCH_CLASHES, RULE_CLASHES,
         "冲的结构事实已报，但冲的效力（是否冲动、冲破、应期）未裁定：无已审跨层冲效力规则",
         "clash_effect"),
    )
    for kind, _, table, rule_id, effect_statement, condition_id in specs:
        if key not in table:
            continue
        counter[0] += 1
        detail = {"branches": [side_a["branch"], side_b["branch"]]}
        if kind == "branch_six_harmony":
            detail["traditional_result_element"] = table[key]
        rows.append({
            "id": "R%03d" % counter[0],
            "scope": scope,
            "period_index": period_index,
            "side_a": copy.deepcopy(side_a),
            "side_b": copy.deepcopy(side_b),
            "kind": kind,
            "detail": detail,
            "conditions": [
                _condition(
                    "both_sides_attested",
                    "双方地支均由已审输入给出",
                    "satisfied", [RULE_PILLARS]),
                _condition(condition_id, effect_statement, "cannot_judge",
                           [rule_id]),
            ] + ([mapping_condition] if mapping_condition else []),
            "effect": _abstain(_ABSTAIN_EFFECT_REASON, [rule_id]),
            "rule_ids": [rule_id],
        })
    return rows


def _group_relations(counter, scope, branches_with_sides, *, period_index,
                     mapping_condition):
    """三合 / 方位会：只在该 scope 的地支集合上评估，不跨 scope 借支。"""
    rows = []
    present = {}
    for branch, side in branches_with_sides:
        present.setdefault(branch, []).append(side)
    for table, kind, rule_id in (
            (BRANCH_TRIPLE_HARMONIES, "branch_triple_harmony",
             RULE_TRIPLE_HARMONIES),
            (BRANCH_DIRECTIONAL_MEETINGS, "branch_directional_meeting",
             RULE_DIRECTIONAL_MEETINGS)):
        for members, result_element in table:
            if not all(member in present for member in members):
                continue
            counter[0] += 1
            rows.append({
                "id": "R%03d" % counter[0],
                "scope": scope,
                "period_index": period_index,
                "side_a": None,
                "side_b": None,
                "kind": kind,
                "detail": {
                    "branches": list(members),
                    "traditional_result_element": result_element,
                    "member_sides": [
                        copy.deepcopy(present[member][0])
                        for member in members
                    ],
                },
                "conditions": [
                    _condition(
                        "all_members_attested",
                        "三支均由已审输入给出（同一 scope 内）",
                        "satisfied", [RULE_PILLARS]),
                    _condition(
                        "group_transformation" if kind == "branch_triple_harmony"
                        else "group_effect",
                        ("三合成局但合化是否成立未裁定：化气成立需另行审定的合化规则"
                         if kind == "branch_triple_harmony"
                         else "方位会合的结构事实已报，但其效力未裁定：无已审跨层会合效力规则"),
                        "cannot_judge", [rule_id]),
                ] + ([mapping_condition] if mapping_condition else []),
                "effect": _abstain(_ABSTAIN_EFFECT_REASON, [rule_id]),
                "rule_ids": [rule_id],
            })
    return rows


def _mapping_condition(current_period_index, current_period_basis,
                       period_index):
    """大运×流年关系的期位前提：未指定当期运时一律无法判定。"""
    if current_period_index is None:
        return _condition(
            "period_year_mapping",
            "未指定当期运：流年落在哪一运未确定，本关系按逐运列举，不指定当期",
            "cannot_judge", [RULE_DAYUN_SEQUENCE])
    if period_index == current_period_index:
        return _condition(
            "period_year_mapping",
            "调用方指定当期运（依据见 dayun.current_period_basis）",
            "satisfied", [RULE_DAYUN_SEQUENCE],
            basis=current_period_basis)
    return _condition(
        "period_year_mapping",
        "非调用方指定的当期运：本关系只作逐运结构列举，不指定当期",
        "not_satisfied", [RULE_DAYUN_SEQUENCE],
        basis=current_period_basis)


def _validate_system_statement(statement, *, variant, system, label):
    if not isinstance(statement, dict):
        _fail("%s statement must be an object" % label)
    if statement.get("variant") != variant:
        _fail("%s statement variant drifted" % label)
    if system is not None and statement.get("system") != system:
        _fail("%s statement system drifted" % label)
    if statement.get("research_only") is not True:
        _fail("%s statement research_only drifted" % label)
    if statement.get("public_enabled") is not False:
        _fail("%s statement public_enabled drifted" % label)
    if statement.get("ai_enabled") is not False:
        _fail("%s statement ai_enabled drifted" % label)
    return copy.deepcopy(statement)


def _xiyong_contract(*, strength, tiaohou, bingyao, pattern, natal,
                     flow, day_master):
    systems = {}

    # 扶抑：零行可建（S4 审定）。即使传入已审强弱因素，也只原样转述，
    # 不推出任何扶抑方向或喜用。
    fuyi = {
        "system": "fuyi",
        "status": "not_buildable",
        "adjudication_id": RULE_FUYI_SLICE,
        "adjudication_conclusion": "no_buildable_rows",
        "buildable_count": 0,
        "direction": None,
        "useful_god": None,
        "reason": ("扶抑最小切片审定结论为零行可建：方向表十行判别条件全是 "
                   "未阈值化程度词，F-1/F-3 总则带前提不可评估的反例/反转条款；"
                   "B2（2026-11-25）重开的三模型仍无可执行模型。"),
    }
    if strength is None:
        fuyi["consumed_strength_factors"] = None
        fuyi["strength_note"] = "未传入已审强弱因素；即使传入，扶抑仍零行可建。"
    else:
        if not isinstance(strength, dict):
            _fail("strength factors must be an object")
        if strength.get("factor_variant") != RULE_STRENGTH_FACTORS:
            _fail("strength factors variant drifted")
        if strength.get("overall_strength") is not None:
            _fail("strength factors carry an adjudicated overall strength")
        fuyi["consumed_strength_factors"] = copy.deepcopy(strength)
        fuyi["strength_note"] = ("已审强弱因素原样转述：overall_strength 恒为 None，"
                                 "只含月令/通根/透干等结构事实，不作强弱分类。")
    systems["fuyi"] = fuyi

    # 调候：原样转述 tiaohou_lookup 输出。
    if tiaohou is None:
        systems["tiaohou"] = {
            "system": "tiaohou", "status": "not_provided",
            "sequence": None,
            "reason": "未传入已审调候输出，本契约不补调候判断。",
        }
    else:
        statement = _validate_system_statement(
            tiaohou, variant="tiaohou-qiongtong-v1", system="tiaohou",
            label="tiaohou")
        if statement.get("day_master") != day_master:
            _fail("tiaohou statement disagrees on the day master")
        if statement.get("month_branch") != natal[1]["branch"]:
            _fail("tiaohou statement disagrees on the month branch")
        status = statement.get("status")
        if status == "matched":
            state = "presented"
        elif status == "not_applicable":
            state = "not_judgeable"
        else:
            _fail("tiaohou statement status drifted")
        systems["tiaohou"] = {
            "system": "tiaohou", "status": state,
            "statement": statement,
            "sequence_stems": [item["stem"] for item in statement.get("sequence", [])]
            if status == "matched" else [],
            "determination": None,
        }

    # 病药：原样转述 bingyao_lookup 输出（两对并列，不合并）。
    if bingyao is None:
        systems["bingyao"] = {
            "system": "bingyao", "status": "not_provided",
            "pairs": None,
            "reason": "未传入已审病药输出，本契约不补病药判断。",
        }
    else:
        statement = _validate_system_statement(
            bingyao, variant="bingyao-shenfeng-v1", system="bingyao",
            label="bingyao")
        if statement.get("day_master") != day_master:
            _fail("bingyao statement disagrees on the day master")
        if statement.get("determination") is not None:
            _fail("bingyao statement carries an adjudicated determination")
        pairs = statement.get("pairs")
        if type(pairs) is not list or len(pairs) != 2:
            _fail("bingyao statement pairs malformed")
        systems["bingyao"] = {
            "system": "bingyao", "status": "presented",
            "statement": statement,
            "pairs": [{"pair_id": pair.get("pair_id"),
                       "status": pair.get("status"),
                       "medicine_status": pair.get("medicine_status"),
                       "medicine_effect_status":
                           pair.get("medicine_effect_status")}
                      for pair in pairs],
            "determination": None,
        }

    # 格局用神：原样转述格局候选输出；定格字段恒为空，否则拒收。
    if pattern is None:
        systems["pattern_yongshen"] = {
            "system": "pattern_yongshen", "status": "not_provided",
            "pattern": None, "useful_god": None,
            "reason": ("未传入已审格局候选输出（格局候选需已执行的 trace，"
                       "本引擎不自行重算取格）；本契约不补格局判断。"),
        }
    else:
        if not isinstance(pattern, dict):
            _fail("pattern statement must be an object")
        if pattern.get("variant") != RULE_PATTERN_CANDIDATES:
            _fail("pattern statement variant drifted")
        determination = pattern.get("determination")
        if isinstance(determination, dict):
            if determination.get("pattern") is not None:
                _fail("pattern statement carries a determined pattern")
            if determination.get("true_false") is not None:
                _fail("pattern statement carries a true/false determination")
            if determination.get("useful_god") is not None:
                _fail("pattern statement carries a determined useful god")
        elif determination is not None:
            _fail("pattern statement determination malformed")
        if pattern.get("research_only") is not True:
            _fail("pattern statement research_only drifted")
        if pattern.get("public_enabled") is not False:
            _fail("pattern statement public_enabled drifted")
        if pattern.get("ai_enabled") is not False:
            _fail("pattern statement ai_enabled drifted")
        systems["pattern_yongshen"] = {
            "system": "pattern_yongshen",
            "status": pattern.get("status", "structural_observation_only"),
            "statement": copy.deepcopy(pattern),
            "pattern": None,
            "useful_god": None,
        }

    # 流年喜用：只完成数据契约与规则调用结构，完整推演待规则获批。
    flow_stem = flow["stem"]
    flow_ten_god = flow["stem_ten_god"]
    references = {}
    tiaohou_block = systems["tiaohou"]
    if tiaohou_block["status"] == "presented":
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence":
                flow_stem in tiaohou_block["sequence_stems"],
            "natal_tiaohou_sequence_stems":
                list(tiaohou_block["sequence_stems"]),
            "note": ("只报流年干是否在原局调候序列中这一存在性事实；"
                     "流年调候推演未获批，不据此取流年调候用神。"),
        }
    elif tiaohou_block["status"] == "not_judgeable":
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence": None,
            "note": "原局调候条目在审定文本中不存在，流年调候对照无序列可比。",
        }
    else:
        references["tiaohou"] = {
            "flow_stem": flow_stem,
            "flow_stem_in_natal_tiaohou_sequence": None,
            "note": "未传入原局调候输出，流年调候对照待原局调候传入后方可列举。",
        }
    bingyao_block = systems["bingyao"]
    if bingyao_block["status"] == "presented":
        pair_refs = []
        for pair in bingyao_block["statement"]["pairs"]:
            rule = pair.get("rule", {})
            pair_refs.append({
                "pair_id": pair.get("pair_id"),
                "flow_stem_ten_god": flow_ten_god,
                "flow_ten_god_role_in_pair":
                    ("subject" if flow_ten_god in rule.get("subject_gods", ())
                     else "disease" if flow_ten_god in rule.get("disease_gods", ())
                     else "medicine" if flow_ten_god in rule.get("medicine_gods", ())
                     else "none"),
                "pair_status": pair.get("status"),
                "note": ("只报流年干十神在该病药对中的角色这一结构对照；"
                         "流年病药推演未获批，不据此断流年病药去留。"),
            })
        references["bingyao"] = {"pairs": pair_refs}
    else:
        references["bingyao"] = {
            "pairs": None,
            "note": "未传入原局病药输出，流年病药对照待原局病药传入后方可列举。",
        }
    references["fuyi"] = {
        "note": "流年扶抑推演未获批：原局扶抑已零行可建，流年扶抑无可调用的规则。",
    }
    references["pattern_yongshen"] = {
        "note": "流年格局用神推演未获批：原局定格未完成，流年格局用神无可调用的规则。",
    }
    annual_xiyong = {
        "status": "contract_only_pending_rules",
        "implemented": [
            "flow_year_ganzhi_and_ten_god",
            "flow_stem_presence_against_natal_tiaohou_sequence",
            "flow_stem_ten_god_role_against_bingyao_pairs",
            "rule_call_structure",
        ],
        "pending": [
            "annual_tiaohou_derivation",
            "annual_bingyao_derivation",
            "annual_fuyi_derivation",
            "annual_pattern_yongshen_derivation",
            "unified_annual_verdict",
        ],
        "pending_reason": ("流年喜用完整推演待对应规则获批后接入；现阶段只列数据契约 "
                           "与调用结构，不推演任何流年喜用。"),
        "flow_references": references,
        "derivation": None,
        "unified_verdict": None,
    }

    return {
        "variant": XIYONG_CONTRACT_VARIANT,
        "systems": systems,
        "annual_xiyong": annual_xiyong,
        "unified_verdict": None,
        "unified_verdict_status": "abstain_by_adjudication_TJ-013.2-A",
        "unified_verdict_note": ("TJ-013.2 裁决 A：四体系并列呈现、统一裁决拒判；"
                                 "本契约永不输出统一喜用神。"),
    }


def combine(natal_pillars, day_master, dayun_periods, target_year, *,
            strength=None, tiaohou=None, bingyao=None, pattern=None,
            current_period_index=None, current_period_basis=None,
            variant=VARIANT):
    """组合原局、大运、流年三层，返回结构化 dict。

    ``natal_pillars``：四柱（ganzhi 字符串或 chart_from_pillars 形态的
    pillar 对象，年/月/日/时顺序）；``day_master``：日干；
    ``dayun_periods``：``candidate_sequence`` 行列表；
    ``target_year``：公历目标年份（1900..2098）。
    ``strength``/``tiaohou``/``bingyao``/``pattern``：已审体系输出
    （缺省为 None，即该体系未传入）。``current_period_index`` 与
    ``current_period_basis`` 须成对出现：调用方显式指定当期运及其依据
    （如已审交运区间），引擎只记录、不推导期位映射。
    """
    if variant != VARIANT:
        raise ValueError("Unsupported combination engine variant")
    if type(day_master) is not str or day_master not in STEMS:
        _fail("day_master must be one heavenly stem")
    if (current_period_index is None) != (current_period_basis is None):
        _fail("current_period_index and current_period_basis must be given together")
    if current_period_basis is not None and (
            type(current_period_basis) is not str or not current_period_basis):
        _fail("current_period_basis must be a non-empty string")

    natal = _normalize_pillars(natal_pillars, day_master)
    dayun = _normalize_dayun(dayun_periods, day_master)
    if current_period_index is not None and current_period_index not in {
            row["period_index"] for row in dayun}:
        _fail("current_period_index does not match any supplied dayun period")
    flow = _flow_year(target_year, day_master)

    natal_sides = [
        _side("natal", pillar=row["name"], stem=row["stem"],
              branch=row["branch"], stem_ten_god=row["stem_ten_god"])
        for row in natal
    ]
    flow_side = _side("flow_year", stem=flow["stem"], branch=flow["branch"],
                      stem_ten_god=flow["stem_ten_god"])

    counter = [0]
    relations = []

    # 1) 大运×原局（逐运）。
    for period in dayun:
        dayun_side = _side("dayun", period_index=period["period_index"],
                           stem=period["stem"], branch=period["branch"],
                           stem_ten_god=period["stem_ten_god"])
        for natal_side in natal_sides:
            relations.extend(_stem_pair_relations(
                counter, "dayun_x_natal", dayun_side, natal_side,
                period_index=period["period_index"],
                mapping_condition=None))
            relations.extend(_branch_pair_relations(
                counter, "dayun_x_natal", dayun_side, natal_side,
                period_index=period["period_index"],
                mapping_condition=None))
        branches = [(row["branch"], _side(
            "natal", pillar=row["name"], stem=row["stem"],
            branch=row["branch"], stem_ten_god=row["stem_ten_god"]))
            for row in natal]
        branches.append((period["branch"], dayun_side))
        relations.extend(_group_relations(
            counter, "dayun_x_natal", branches,
            period_index=period["period_index"], mapping_condition=None))

    # 2) 流年×原局。
    for natal_side in natal_sides:
        relations.extend(_stem_pair_relations(
            counter, "flow_x_natal", flow_side, natal_side,
            period_index=None, mapping_condition=None))
        relations.extend(_branch_pair_relations(
            counter, "flow_x_natal", flow_side, natal_side,
            period_index=None, mapping_condition=None))
    branches = [(row["branch"], _side(
        "natal", pillar=row["name"], stem=row["stem"],
        branch=row["branch"], stem_ten_god=row["stem_ten_god"]))
        for row in natal]
    branches.append((flow["branch"], flow_side))
    relations.extend(_group_relations(
        counter, "flow_x_natal", branches,
        period_index=None, mapping_condition=None))

    # 3) 大运×流年（逐运；期位映射条件逐条附注）。
    for period in dayun:
        dayun_side = _side("dayun", period_index=period["period_index"],
                           stem=period["stem"], branch=period["branch"],
                           stem_ten_god=period["stem_ten_god"])
        mapping = _mapping_condition(
            current_period_index, current_period_basis,
            period["period_index"])
        relations.extend(_stem_pair_relations(
            counter, "dayun_x_flow", dayun_side, flow_side,
            period_index=period["period_index"],
            mapping_condition=mapping))
        relations.extend(_branch_pair_relations(
            counter, "dayun_x_flow", dayun_side, flow_side,
            period_index=period["period_index"],
            mapping_condition=mapping))

    counts_by_scope = {}
    counts_by_kind = {}
    condition_statuses = {}
    for relation in relations:
        counts_by_scope[relation["scope"]] = (
            counts_by_scope.get(relation["scope"], 0) + 1)
        counts_by_kind[relation["kind"]] = (
            counts_by_kind.get(relation["kind"], 0) + 1)
        for condition in relation["conditions"]:
            condition_statuses[condition["status"]] = (
                condition_statuses.get(condition["status"], 0) + 1)

    xiyong = _xiyong_contract(
        strength=strength, tiaohou=tiaohou, bingyao=bingyao, pattern=pattern,
        natal=natal, flow=flow, day_master=day_master)

    consumed = {
        RULE_PILLARS, RULE_TEN_GODS, RULE_STEM_COMBINATIONS,
        RULE_SIX_HARMONIES, RULE_HARMS, RULE_CLASHES,
        RULE_TRIPLE_HARMONIES, RULE_DIRECTIONAL_MEETINGS,
        RULE_DAYUN_SEQUENCE,
    }
    if strength is not None:
        consumed.add(RULE_STRENGTH_FACTORS)
    if tiaohou is not None:
        consumed.add(RULE_TIAOHOU_ASSESSMENT)
    if bingyao is not None:
        consumed.add(RULE_BINGYAO_ASSESSMENT)
    if pattern is not None:
        consumed.add(RULE_PATTERN_CANDIDATES)

    return {
        "variant": VARIANT,
        "research_only": True,
        "public_enabled": False,
        "ai_enabled": False,
        "natal": {
            "pillars": copy.deepcopy(natal),
            "day_master": day_master,
            "month_branch": natal[1]["branch"],
        },
        "dayun": {
            "periods": copy.deepcopy(dayun),
            "current_period_index": current_period_index,
            "current_period_basis": current_period_basis,
            "period_year_mapping": (
                "caller_selected" if current_period_index is not None
                else "not_determined"),
        },
        "flow_year": flow,
        "structural_relations": relations,
        "relation_summary": {
            "total": len(relations),
            "counts_by_scope": counts_by_scope,
            "counts_by_kind": counts_by_kind,
            "condition_status_counts": condition_statuses,
            "not_evaluated": [
                {"kind": "branch_punishment",
                 "reason": ("刑不在已审地支关系表中（canonical "
                            "foundations_v1.json 的 earthly_branch_relations "
                            "无刑表），本引擎不评估刑。")},
            ],
        },
        "effects": {
            "overall_effect": None,
            "all_abstained": True,
            "abstain_count": len(relations),
            "verdict_counts": {"abstain": len(relations)},
            "note": _ABSTAIN_EFFECT_REASON,
        },
        "xiyong": xiyong,
        "consumed_rule_ids": sorted(consumed),
        "limitations": list(LIMITATIONS),
        "scope": ("原局×大运、流年×原局、大运×流年的干支结构关系与条件列举；"
                  "效力一律拒判；喜用四体系并列、统一裁决恒为 None。"),
    }
