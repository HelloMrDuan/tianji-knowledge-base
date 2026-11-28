"""TJ-031.19 (E0427) Lane C: plain-language romance/marriage presentation.

Builds a JSON-able presentation dict from ONE already-executed romance
scenario envelope (``scenario_engine.execute_scenario("romance", ...)``,
``_romance``). The builder is pure and deterministic: it reuses the
existing computation, never rebuilds it, calls no model and no
ExplanationService, and never looks anything up statically -- every
fact is checked mechanically against the same envelope's own outputs.
Any drift, forgery or incomplete binding fails closed with
``ValueError``; the caller must fail the request, never return a
partial presentation.

What the object is and is not (opening plan §2.2/§3). Romance wires
internal assembly only: there is currently NO approved romance
inference output to wire, so this presentation states structure facts
only and says so explicitly wherever a conclusion would otherwise be
expected:

* §1 桃花（咸池）· 配偶星 · 夫妻宫 -- xianchi targets / natal hits /
  target-year activation, day-branch spouse-palace pairing, and
  spouse-star candidate positions (only when the user explicitly
  selected a traditional role).
* §2 原局婚姻关系结构 -- what the natal chart structurally shows
  (pillars, day master, day branch as the spouse-palace position).
  No new inference engine.
* §3 流年联动与大运 -- structural activation facts for the target
  year only. Dayun linkage is explicitly undecided: the romance
  scenario does not compute dayun and no approved dayun-marriage
  combination rule exists.

Hard rules, enforced by construction and by a final banned-text sweep
over the serialized output:

* never fabricate a marriage year or any destined-partner / marriage
  timing prediction; never invent a match/score; never present a
  research candidate as a definite romance verdict, and never convert
  strength scores or fuyi candidates into romance fortune judgments
  (this builder does not consume strength / fuyi output at all);
* show the existing structural computation FULLY: every xianchi match
  (with its target branch), every spouse-star candidate position
  (visible and hidden, paired or not), every spouse-palace and
  spouse-star pairing (including a six-harmony hit's traditional
  result element, with its effectiveness explicitly unassessed), every
  pillar's hidden stems, and the day master's element -- each fact
  mechanically cross-checked against the same envelope (a candidate
  position must match the pillar it claims to sit in; a six-harmony
  hit must carry its result element);
* uncomputable parts say so plainly in Chinese, but only where a
  reader would otherwise expect an answer: one global statement that
  no approved romance inference output exists, one core boundary per
  section, and the dayun pointer (the romance scenario does not
  compute dayun). Undecided items are never padded into extra
  columns -- the presentation is the computed facts first, and the
  envelope's own boundary list (``limitations``) carries the rest;
* no internal reference fields (``evidence_ids`` / ``trace``) and no
  internal status codes (``production_limited``) reach the object;
  the reviewed rule ids are kept only as a server-side audit trail in
  each section's ``basis_rules``.

The builder does NOT execute the scenario itself; see
``build_romance_presentation_for`` for the thin live wrapper (lazy
engine import, so this module stays importable without the sealed
runtime or the lunar provider).
"""

import copy
import json

VARIANT = "romance-presentation-v1"
STATUS = "structure_only"
CALIBER_STRUCTURE = "structure_only"
CALIBER_UNDECIDED = "not_judgeable"

SCOPE_STATEMENT = (
    "本呈现只陈述已审核的桃花姻缘结构事实（咸池查表、夫妻宫日支配对、"
    "配偶星候选位置、目标年结构激活），不作任何婚恋推断；"
    "未命中不等于缺失，未列出的关系不等于不存在。")
NO_INFERENCE_STATEMENT = (
    "目前没有已获批的桃花姻缘推理输出：旺衰、格局、喜用、组合推理均未"
    "接入本页公开呈现，配偶星与桃花推理的公开口径须另行提请晋升。"
    "本呈现只陈述结构事实，不作婚恋推断。")
LIMITATIONS = (
    "年支与日支两个起查基准分别展示，不裁定其中任何一个为唯一标准。",
    "目标年份落在咸池目标支，只表示固定查表结构命中，不等同于桃花旺、"
    "恋爱发生或婚姻结果。",
    "《三命通会》相关纳音附加条件尚未纳入自动规则。",
    "夫妻宫仅以日支位置配对已审六合、六冲、六害；配偶星仅以候选位置与"
    "流年干支作同一性及已审六合、六冲、六害配对；三合、刑、破、合化效力、"
    "旺衰喜忌、大运和紫微等未组合裁定。",
    "本呈现不推断结婚年份或具体时间，不设任何婚恋方面的量化评价。",
)

# Words that must never appear in the presentation, even inside a
# negation: the envelope's own limitations carry some of them
# ("不判断婚期、正缘、吉凶"), so the builder paraphrases those limits
# in its own words instead of copying the envelope text verbatim.
_BANNED_SUBSTRINGS = (
    "婚期", "正缘", "脱单", "桃花运", "桃花指数", "评分", "得分",
    "吉凶", "注定", "红鸾", "天喜", "一定会", "必然",
    "会结婚", "将结婚", "适合结婚", "最佳婚期",
)

_RELATION_LABELS = {
    "six_harmony": "六合",
    "harm": "六害",
    "clash": "六冲",
    "same_branch": "地支相同",
    "same_stem": "天干相同",
}
_PILLAR_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
}
_BASIS_LABELS = {
    "year_branch": "年支基准",
    "day_branch": "日支基准",
}
_ROLE_LABELS = {
    "male": "传统男命口径 · 看财星",
    "female": "传统女命口径 · 看官杀",
}
_SECTION_IDS = (
    "peach_blossom_spouse_star_palace",
    "natal_marriage_structure",
    "dayun_liunian_linkage",
)


def _fail(message):
    raise ValueError("Romance presentation rejected: " + message)


def _require(condition, message):
    if not condition:
        _fail(message)


def _is_branch(value):
    return isinstance(value, str) and len(value) == 1


def _pillar_label(name):
    return _PILLAR_LABELS.get(name, name)


def _relation_label(relation):
    return _RELATION_LABELS.get(relation, relation)


def _validate_envelope(envelope):
    """Mechanical binding checks against the executed envelope."""
    if not isinstance(envelope, dict):
        _fail("envelope must be a mapping")
    if envelope.get("scenario_id") != "romance":
        _fail("envelope is not a romance scenario")
    if envelope.get("status") != "production_limited":
        _fail("envelope status is not production_limited")
    if envelope.get("public_release") is not False:
        _fail("envelope public_release must be False")
    if envelope.get("deterministic") is not True:
        _fail("envelope must be deterministic")
    result = envelope.get("result")
    if not isinstance(result, dict):
        _fail("envelope result must be a mapping")
    if result.get("release_scope") != "xianchi_structure_only":
        _fail("envelope release_scope is not xianchi_structure_only")
    if not isinstance(envelope.get("limitations"), list):
        _fail("envelope limitations must be a list")

    natal = result.get("natal")
    if not isinstance(natal, dict):
        _fail("result natal must be a mapping")
    pillars = natal.get("pillars")
    if not isinstance(pillars, list) or len(pillars) != 4:
        _fail("natal pillars must be a list of four")
    seen_names = set()
    day_branch = None
    pillar_by_name = {}
    for pillar in pillars:
        if not isinstance(pillar, dict):
            _fail("natal pillar must be a mapping")
        name = pillar.get("name")
        if name not in _PILLAR_LABELS or name in seen_names:
            _fail("natal pillar name is not a known pillar")
        seen_names.add(name)
        pillar_by_name[name] = pillar
        ganzhi = pillar.get("ganzhi")
        if not isinstance(ganzhi, str) or len(ganzhi) != 2:
            _fail("natal pillar ganzhi must be two characters")
        branch = pillar.get("branch")
        if not isinstance(branch, dict) or not _is_branch(branch.get("value")):
            _fail("natal pillar branch must be a single branch")
        if branch["value"] != ganzhi[1]:
            _fail("natal pillar branch drifted from its ganzhi")
        stem = pillar.get("stem")
        if not isinstance(stem, dict) or not isinstance(
                stem.get("value"), str) or not stem["value"]:
            _fail("natal pillar stem must carry a value")
        hidden = branch.get("hidden_stems")
        if hidden is not None:
            if not isinstance(hidden, list) or not all(
                    isinstance(item, dict)
                    and isinstance(item.get("stem"), str)
                    and item["stem"]
                    and isinstance(item.get("ten_god"), str)
                    and item["ten_god"] for item in hidden):
                _fail("natal pillar hidden stems must carry stem/ten_god")
        if name == "day":
            day_branch = branch["value"]
    if seen_names != set(_PILLAR_LABELS):
        _fail("natal pillars do not cover all four pillars")
    day_master = natal.get("day_master")
    if isinstance(day_master, dict):
        day_master_stem = day_master.get("stem")
        day_master_element = day_master.get("element")
    elif isinstance(day_master, str):
        day_master_stem = day_master
        day_master_element = None
    else:
        day_master_stem = None
        day_master_element = None
    if not isinstance(day_master_stem, str) or not day_master_stem:
        _fail("natal day_master must carry a stem")
    if day_master_element is not None \
            and not isinstance(day_master_element, str):
        _fail("natal day_master element must be a string")
    day_pillar = next(p for p in pillars if p["name"] == "day")
    if day_pillar["stem"]["value"] != day_master_stem:
        _fail("day master drifted from the day pillar stem")

    xianchi = result.get("xianchi")
    if not isinstance(xianchi, dict):
        _fail("result xianchi must be a mapping")
    targets = xianchi.get("targets")
    if not isinstance(targets, dict) \
            or not _is_branch(targets.get("year_branch")) \
            or not _is_branch(targets.get("day_branch")):
        _fail("xianchi targets must carry two target branches")
    natal_matches = xianchi.get("natal_matches")
    if not isinstance(natal_matches, list):
        _fail("xianchi natal_matches must be a list")
    for match in natal_matches:
        if not isinstance(match, dict) \
                or match.get("basis") not in _BASIS_LABELS \
                or match.get("pillar") not in _PILLAR_LABELS:
            _fail("xianchi natal match has an unknown basis or pillar")
        # A match means that pillar's branch IS the basis target.
        if pillar_by_name[match["pillar"]]["branch"]["value"] \
                != targets[match["basis"]]:
            _fail("xianchi natal match branch drifted from its target")
        if match.get("target_branch") is not None \
                and match["target_branch"] != targets[match["basis"]]:
            _fail("xianchi natal match target drifted")

    target_year = result.get("target_year")
    if not isinstance(target_year, dict):
        _fail("result target_year must be a mapping")
    year = target_year.get("year")
    ganzhi = target_year.get("ganzhi")
    branch = target_year.get("branch")
    if type(year) is not int or not isinstance(ganzhi, str) \
            or len(ganzhi) != 2 or branch != ganzhi[1]:
        _fail("target year ganzhi/branch inconsistent")
    activation = result.get("target_year_activation")
    if not isinstance(activation, dict):
        _fail("result target_year_activation must be a mapping")
    for basis, target in (("year_branch_basis", targets["year_branch"]),
                          ("day_branch_basis", targets["day_branch"])):
        entry = activation.get(basis)
        if not isinstance(entry, dict):
            _fail("target year activation entry must be a mapping")
        if entry.get("target_branch") != target \
                or entry.get("target_year_branch") != branch \
                or entry.get("matched") is not (branch == target):
            _fail("target year activation drifted from the xianchi targets")

    palace = result.get("spouse_palace_year_relations")
    if not isinstance(palace, dict):
        _fail("result spouse_palace_year_relations must be a mapping")
    if palace.get("interpretation_allowed") is not False:
        _fail("spouse palace must not allow interpretation")
    if palace.get("natal_day_branch") != day_branch:
        _fail("spouse palace day branch drifted from the natal day branch")
    if palace.get("target_year_branch") != branch:
        _fail("spouse palace target year branch drifted")
    if palace.get("pairs_checked") != 1:
        _fail("spouse palace must check exactly one pair")
    relations = palace.get("relations")
    if not isinstance(relations, list):
        _fail("spouse palace relations must be a list")
    for relation in relations:
        _validate_relation(relation, "relation_type", day_branch, branch,
                           natal_pillar="day")

    pairing = result.get("spouse_star_year_pairing")
    if pairing is not None:
        if not isinstance(pairing, dict):
            _fail("spouse star pairing must be a mapping")
        if pairing.get("interpretation_allowed") is not False:
            _fail("spouse star pairing must not allow interpretation")
        if pairing.get("traditional_role") not in _ROLE_LABELS:
            _fail("spouse star pairing role is not a known traditional role")
        candidate_ten_gods = pairing.get("candidate_ten_gods")
        if not isinstance(candidate_ten_gods, list) or not candidate_ten_gods \
                or not all(isinstance(god, str) and god
                           for god in candidate_ten_gods):
            _fail("spouse star candidate ten gods must be a non-empty list")
        positions = pairing.get("candidate_positions")
        if not isinstance(positions, dict) \
                or not isinstance(positions.get("visible"), list) \
                or not isinstance(positions.get("hidden"), list):
            _fail("spouse star candidate positions must carry visible/hidden lists")
        if pairing.get("pairs_checked") != (
                len(positions["visible"]) + len(positions["hidden"])):
            _fail("spouse star pairs_checked drifted from candidate positions")
        if pairing.get("pairing_state") not in (
                "no_candidates", "no_pair_hits", "paired"):
            _fail("spouse star pairing_state is not a known state")
        # Every candidate position must sit where it claims to sit:
        # a visible position is the pillar's own stem; a hidden
        # position is one of that pillar's hidden stems.
        for row in positions["visible"]:
            _validate_position(row, "visible", pillar_by_name)
        for row in positions["hidden"]:
            _validate_position(row, "hidden", pillar_by_name)
        pairings = pairing.get("pairings")
        if not isinstance(pairings, list):
            _fail("spouse star pairings must be a list")
        for item in pairings:
            if not isinstance(item, dict) \
                    or item.get("relation") not in _RELATION_LABELS \
                    or item.get("pillar") not in _PILLAR_LABELS \
                    or item.get("position_kind") not in ("visible", "hidden"):
                _fail("spouse star pairing entry drifted")
            # Pairing rows carry the pillar branch under "branch" and
            # no flow branch / result element (the pairing builder does
            # not copy them); only the pillar branch is checkable here.
            _validate_relation(
                item, "relation",
                pillar_by_name[item["pillar"]]["branch"]["value"],
                branch, branch_key="branch", flow_key=None,
                require_element=False)
        target = pairing.get("target_year")
        if not isinstance(target, dict) or target.get("ganzhi") != ganzhi \
                or target.get("branch") != branch:
            _fail("spouse star pairing target year drifted")
    return result, pillars, day_master_stem, day_master_element, day_branch


def _validate_relation(row, key, natal_branch, flow_branch,
                       natal_pillar=None, branch_key="natal_branch",
                       flow_key="flow_branch", require_element=True):
    """One branch-pair relation row against the branches it claims."""
    if not isinstance(row, dict) or row.get(key) not in (
            "six_harmony", "harm", "clash", "same_branch", "same_stem"):
        _fail("branch relation has an unknown relation type")
    if row.get(branch_key) != natal_branch:
        _fail("branch relation drifted from its branches")
    if flow_key is not None and row.get(flow_key) != flow_branch:
        _fail("branch relation drifted from its branches")
    if natal_pillar is not None and row.get("natal_pillar") != natal_pillar:
        _fail("spouse palace relation is not a day-pillar relation")
    if require_element and row.get(key) == "six_harmony":
        # A six-harmony hit carries its traditional result element;
        # its transformation effectiveness is never assessed here.
        if not isinstance(row.get("traditional_result_element"), str) \
                or not row["traditional_result_element"]:
            _fail("six-harmony relation lacks its result element")
        if row.get("transformation_effectiveness_assessed") is not None \
                and row["transformation_effectiveness_assessed"] is not False:
            _fail("six-harmony effectiveness must stay unassessed")


def _relation_text(row, key):
    """Plain-language rendering of one relation row.

    A six-harmony hit names its traditional result element and states
    plainly that the transformation effectiveness is not assessed.
    """
    label = _relation_label(row[key])
    natal_branch = row.get("natal_branch") or row.get("branch")
    flow_branch = row.get("flow_branch")
    if flow_branch is None:
        return label
    text = "%s（%s ↔ %s" % (label, natal_branch, flow_branch)
    if row.get(key) == "six_harmony":
        text += "；传统合化结果五行：%s，合化效力未评估" % (
            row["traditional_result_element"])
    return text + "）"


def _validate_position(row, kind, pillar_by_name):
    if not isinstance(row, dict) or row.get("pillar") not in _PILLAR_LABELS:
        _fail("spouse star position has an unknown pillar")
    pillar = pillar_by_name[row["pillar"]]
    if kind == "visible":
        if row.get("stem") != pillar["stem"]["value"] \
                or row.get("ten_god") != pillar["stem"].get("ten_god"):
            _fail("visible spouse star position drifted from its pillar stem")
    else:
        if row.get("branch") != pillar["branch"]["value"]:
            _fail("hidden spouse star position drifted from its pillar branch")
        hidden = pillar["branch"].get("hidden_stems")
        if isinstance(hidden, list) and not any(
                item.get("stem") == row.get("stem")
                and item.get("ten_god") == row.get("ten_god")
                for item in hidden):
            _fail("hidden spouse star position is not a hidden stem of its pillar")


def _activation_sentence(year, branch, targets):
    hits = [basis for basis in ("year_branch", "day_branch")
            if branch == targets[basis]]
    if not hits:
        return "两个基准均未命中"
    if len(hits) == 2:
        return "两个基准均命中"
    return "命中 1 项（%s命中）" % _BASIS_LABELS[hits[0]]


def _section_peach(result, pillars, day_branch, target_year):
    xianchi = result["xianchi"]
    targets = xianchi["targets"]
    year = target_year["year"]
    branch = target_year["branch"]
    facts = []
    for basis in ("year_branch", "day_branch"):
        matches = [m for m in xianchi["natal_matches"]
                   if m["basis"] == basis]
        facts.append({
            "label": "%s咸池目标" % _BASIS_LABELS[basis],
            "value": targets[basis],
        })
        facts.append({
            "label": "%s原局命中" % _BASIS_LABELS[basis],
            "value": ("、".join(
                "%s（地支 %s）" % (_pillar_label(m["pillar"]),
                                 targets[basis])
                for m in matches)
                if matches else "未见结构命中"),
        })
        facts.append({
            "label": "%d 年流年地支（%s）" % (year, _BASIS_LABELS[basis]),
            "value": ("命中目标支 %s" % targets[basis]
                      if branch == targets[basis]
                      else "未命中目标支 %s" % targets[basis]),
        })
    source_warning = xianchi.get("source_warning") or xianchi.get("warning")
    if isinstance(source_warning, str) and source_warning.strip():
        facts.append({"label": "查表口径说明", "value": source_warning.strip()})

    palace = result["spouse_palace_year_relations"]
    relations = palace["relations"]
    facts.append({"label": "夫妻宫位置", "value": "日支 %s" % day_branch})
    facts.append({
        "label": "日支 × %d 年流年地支" % year,
        "value": ("、".join(_relation_text(r, "relation_type")
                            for r in relations)
                  if relations else "未命中已审六合、六冲、六害"),
    })

    pairing = result.get("spouse_star_year_pairing")
    basis_rules = ["bazi.phase2.xianchi_lookup",
                   "bazi.phase2.spouse_palace_day_branch"]
    undecided = [
        {"item": "咸池命中是否意味着桃花旺、恋爱发生或婚姻结果",
         "reason": "目标年份落在咸池目标支，只表示固定查表结构命中；"
                   "本场景不输出婚恋方面的好坏判断。"},
    ]
    if pairing is None:
        undecided.append({
            "item": "配偶星候选位置与流年配对",
            "reason": "未启用传统配偶星口径；不启用时不做配偶星配对。"})
    else:
        basis_rules.append("bazi.phase2.spouse_star_lens")
        positions = pairing["candidate_positions"]
        facts.append({
            "label": "传统配偶星口径",
            "value": _ROLE_LABELS[pairing["traditional_role"]],
        })
        facts.append({
            "label": "传统口径候选十神",
            "value": "、".join(pairing["candidate_ten_gods"]),
        })
        facts.append({
            "label": "配偶星候选位置",
            "value": "显干 %d 处、藏干 %d 处，共核对 %d 个候选位置" % (
                len(positions["visible"]), len(positions["hidden"]),
                pairing["pairs_checked"]),
        })
        # Every candidate position, paired or not -- the full list,
        # not just the positions that happened to pair.
        for row in positions["visible"]:
            facts.append({
                "label": "配偶星候选位置 · %s显干" % _pillar_label(row["pillar"]),
                "value": "%s（%s）" % (row["stem"], row["ten_god"]),
            })
        for row in positions["hidden"]:
            facts.append({
                "label": "配偶星候选位置 · %s藏干" % _pillar_label(row["pillar"]),
                "value": "%s（%s）" % (row["stem"], row["ten_god"]),
            })
        facts.append({
            "label": "配偶星 × %d 年流年干支" % year,
            "value": ("、".join(
                "%s%s %s（%s）：%s" % (
                    _pillar_label(item["pillar"]),
                    "藏干" if item["position_kind"] == "hidden" else "显干",
                    item["stem"], item["ten_god"],
                    _relation_text(item, "relation"))
                for item in pairing["pairings"])
                if pairing["pairings"] else "未见配对命中"),
        })
        if pairing["pairing_state"] == "no_candidates":
            undecided.append({
                "item": "配偶星候选位置",
                "reason": "所选传统口径下，原局显干与藏干中未见候选十神位置。"})
        elif pairing["pairing_state"] == "no_pair_hits":
            undecided.append({
                "item": "配偶星与流年的配对命中",
                "reason": "候选位置与流年干支未见天干、地支同一性，"
                          "也未命中已审六合、六害、六冲。"})
    return {
        "id": "peach_blossom_spouse_star_palace",
        "title": "桃花（咸池）· 配偶星 · 夫妻宫",
        "caliber": CALIBER_STRUCTURE,
        "basis": ("已审咸池查表（年支、日支两套基准分别展示）与夫妻宫日支配对；"
                  "配偶星仅在用户显式选择传统口径时配对。"),
        "basis_rules": basis_rules,
        "summary": ("%d 年流年地支 %s，咸池目标年激活%s；"
                    "日支 %s 与流年地支%s。"
                    % (year, branch,
                       _activation_sentence(year, branch, targets),
                       day_branch,
                       ("命中" + "、".join(
                           _relation_text(r, "relation_type")
                           for r in relations))
                       if relations else "未命中已审六合、六冲、六害")),
        "facts": facts,
        "undecided": undecided,
    }


def _section_natal(result, pillars, day_master_stem, day_master_element,
                   day_branch):
    facts = []
    for pillar in pillars:
        stem = pillar["stem"]
        ten_god = stem.get("ten_god")
        value = pillar["ganzhi"]
        if isinstance(ten_god, str) and ten_god:
            value = "%s（%s · %s）" % (value, stem["value"], ten_god)
        facts.append({"label": _pillar_label(pillar["name"]), "value": value})
        hidden = pillar["branch"].get("hidden_stems")
        if isinstance(hidden, list) and hidden:
            facts.append({
                "label": "%s藏干（%s）" % (_pillar_label(pillar["name"]),
                                        pillar["branch"]["value"]),
                "value": "、".join("%s（%s）" % (item["stem"], item["ten_god"])
                                  for item in hidden),
            })
    day_master_value = day_master_stem
    if isinstance(day_master_element, str) and day_master_element:
        day_master_value = "%s（%s）" % (day_master_stem, day_master_element)
    facts.append({"label": "日主", "value": day_master_value})
    facts.append({"label": "夫妻宫位置", "value": "日支 %s" % day_branch})
    return {
        "id": "natal_marriage_structure",
        "title": "原局婚姻关系结构",
        "caliber": CALIBER_STRUCTURE,
        "basis": "原局四柱与日主结构；日支为传统夫妻宫位置。只陈述原局结构，不新增推理。",
        "basis_rules": ["bazi.phase2.spouse_palace_day_branch"],
        "summary": "原局四柱为%s，日主 %s，日支 %s 为传统夫妻宫位置。" % (
            "、".join(p["ganzhi"] for p in pillars),
            day_master_value, day_branch),
        "facts": facts,
        "undecided": [
            {"item": "夫妻宫喜忌、配偶星强弱与婚姻关系质量",
             "reason": "没有已获批的推理输出；旺衰、格局、喜用推理均未接入本页，"
                       "暂不可判；日支位置与候选位置不等于完整婚姻判断。"},
        ],
    }


def _section_linkage(result, target_year):
    targets = result["xianchi"]["targets"]
    year = target_year["year"]
    branch = target_year["branch"]
    palace = result["spouse_palace_year_relations"]
    relations = palace["relations"]
    facts = [
        {"label": "目标年",
         "value": "%d 年 %s（流年地支 %s）" % (
             year, target_year["ganzhi"], branch)},
        {"label": "咸池目标年激活",
         "value": _activation_sentence(year, branch, targets)},
        {"label": "夫妻宫 × 流年",
         "value": ("、".join(_relation_text(r, "relation_type")
                             for r in relations)
                   if relations else "未命中已审成对规则")},
        {"label": "流年边界口径",
         "value": "太阳年；参考日固定为 7 月 1 日，以稳定选取年度地支。"},
    ]
    pairing = result.get("spouse_star_year_pairing")
    if pairing is not None:
        facts.append({
            "label": "配偶星 × 流年",
            "value": ("命中 %d 处配对" % len(pairing["pairings"])
                      if pairing["pairings"] else "未见配对命中"),
        })
    return {
        "id": "dayun_liunian_linkage",
        "title": "流年联动与大运",
        "caliber": CALIBER_STRUCTURE,
        "basis": "目标年流年干支与原局结构的配对事实；大运不在本场景计算范围内。",
        "basis_rules": ["bazi.phase2.spouse_palace_day_branch"],
        "summary": ("%d 年与原局的联动只有流年结构事实：咸池激活%s，"
                    "夫妻宫配对%s；大运联动暂不可判。"
                    % (year,
                       _activation_sentence(year, branch, targets),
                       ("命中" + "、".join(
                           _relation_text(r, "relation_type")
                           for r in relations))
                       if relations else "未命中已审成对规则")),
        "facts": facts,
        "undecided": [
            {"item": "大运与婚姻结构的联动",
             "reason": "暂不可判：本场景不计算大运，大运与婚姻的组合规则尚未获批；"
                       "大运时间轴请见八字命理页，"
                       "本页不由流年结构推断大运影响。"},
            {"item": "结婚年份或具体时间",
             "reason": "没有任何已审规则可以从本页结构事实推断结婚时间；"
                       "本呈现不作此类推断。"},
        ],
    }


def build_romance_presentation(envelope):
    """Build the plain-language romance presentation for one envelope.

    ``envelope`` is the executed ``_romance`` envelope of the same
    request. Returns a fresh JSON-able dict. Raises ``ValueError`` on
    any drift, forgery or incomplete binding.
    """
    if not isinstance(envelope, dict):
        _fail("envelope must be a mapping")
    result, pillars, day_master_stem, day_master_element, day_branch = \
        _validate_envelope(envelope)
    target_year = result["target_year"]
    sections = [
        _section_peach(result, pillars, day_branch, target_year),
        _section_natal(result, pillars, day_master_stem,
                       day_master_element, day_branch),
        _section_linkage(result, target_year),
    ]
    presentation = {
        "variant": VARIANT,
        "scenario_id": "romance",
        "status": STATUS,
        "caliber": CALIBER_STRUCTURE,
        "target_year": target_year["year"],
        "target_year_ganzhi": target_year["ganzhi"],
        "target_year_branch": target_year["branch"],
        "natal": {
            "pillars": [
                {"pillar": p["name"], "ganzhi": p["ganzhi"],
                 "stem": p["stem"]["value"],
                 "ten_god": (p["stem"].get("ten_god")
                             if isinstance(p["stem"].get("ten_god"), str)
                             else None),
                 "branch": p["branch"]["value"]}
                for p in pillars
            ],
            "day_master": day_master_stem,
            "day_master_element": day_master_element,
            "day_branch": day_branch,
        },
        "sections": sections,
        "undecided": [
            {"item": "桃花姻缘推理结论（配偶星与桃花推理）",
             "reason": NO_INFERENCE_STATEMENT},
        ],
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }
    # Final sweep: no prediction / scoring wording anywhere, even
    # inside a negation, and no internal reference fields.
    serialized = json.dumps(presentation, ensure_ascii=False)
    for banned in _BANNED_SUBSTRINGS:
        if banned in serialized:
            _fail("presentation carries banned wording: " + banned)
    for forbidden in ("evidence_ids", "trace", "production_limited",
                      "rule_matches", "fortune_score"):
        if forbidden in serialized:
            _fail("presentation carries an internal field: " + forbidden)
    return presentation


def build_romance_presentation_for(birth_value, target_year,
                                   traditional_role=None, birth_zone=None):
    """Live wrapper: execute the romance scenario, then present it.

    Lazy engine import keeps this module importable without the sealed
    runtime. A sealed-runtime failure propagates (the caller decides
    whether it is a skip or a failure); a presentation rejection raises
    ``ValueError``.
    """
    from .scenario_engine import execute_scenario

    inputs = {"birth_value": birth_value, "target_year": target_year}
    if birth_zone is not None:
        inputs["birth_zone"] = birth_zone
    if traditional_role is not None:
        inputs["traditional_role"] = traditional_role
    envelope = execute_scenario("romance", inputs)
    return build_romance_presentation(envelope)


def is_valid_romance_presentation(obj):
    """Closed-shape validator for the presentation object.

    Exact top-level key set, the three sections in order, structure
    caliber throughout, no banned wording and no internal reference
    fields. Anything else is not a valid romance presentation.
    """
    if not isinstance(obj, dict):
        return False
    if set(obj) != {"variant", "scenario_id", "status", "caliber",
                    "target_year", "target_year_ganzhi",
                    "target_year_branch", "natal", "sections",
                    "undecided", "scope_statement", "limitations"}:
        return False
    if obj.get("variant") != VARIANT or obj.get("scenario_id") != "romance" \
            or obj.get("status") != STATUS \
            or obj.get("caliber") != CALIBER_STRUCTURE:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    if type(obj.get("target_year")) is not int:
        return False
    if not isinstance(obj.get("target_year_ganzhi"), str) \
            or len(obj["target_year_ganzhi"]) != 2 \
            or obj.get("target_year_branch") != obj["target_year_ganzhi"][1]:
        return False
    natal = obj.get("natal")
    if not isinstance(natal, dict) or set(natal) != {
            "pillars", "day_master", "day_master_element", "day_branch"}:
        return False
    if len(natal.get("pillars") or []) != 4:
        return False
    for pillar in natal["pillars"]:
        if not isinstance(pillar, dict) or set(pillar) != {
                "pillar", "ganzhi", "stem", "ten_god", "branch"}:
            return False
    sections = obj.get("sections")
    if not isinstance(sections, list) \
            or [s.get("id") for s in sections] != list(_SECTION_IDS):
        return False
    for section in sections:
        if not isinstance(section, dict) or set(section) != {
                "id", "title", "caliber", "basis", "basis_rules",
                "summary", "facts", "undecided"}:
            return False
        if section.get("caliber") != CALIBER_STRUCTURE:
            return False
        if not isinstance(section.get("facts"), list) \
                or not section["facts"]:
            return False
        if not isinstance(section.get("undecided"), list) \
                or not section["undecided"]:
            return False
        for fact in section["facts"]:
            if not isinstance(fact, dict) or set(fact) != {"label", "value"} \
                    or not isinstance(fact.get("label"), str) \
                    or not isinstance(fact.get("value"), str):
                return False
        for item in section["undecided"]:
            if not isinstance(item, dict) or set(item) != {"item", "reason"} \
                    or not isinstance(item.get("item"), str) \
                    or not isinstance(item.get("reason"), str):
                return False
    undecided = obj.get("undecided")
    if not isinstance(undecided, list) or not undecided:
        return False
    serialized = json.dumps(obj, ensure_ascii=False)
    for banned in _BANNED_SUBSTRINGS:
        if banned in serialized:
            return False
    for forbidden in ("evidence_ids", "trace", "production_limited",
                      "rule_matches"):
        if forbidden in serialized:
            return False
    return True


def to_public_romance_presentation(candidate):
    """Allowlist projection of a validated romance presentation.

    The object is public-safe by construction (the validator enforces
    the exact top-level key set, structure caliber throughout, no
    banned wording and no internal reference fields). The projection
    is the final gate: validator pass, then a deep copy. An invalid
    candidate raises ``ValueError``; the projection layer treats that
    as "strip the field", never as a partial release.
    """
    if not is_valid_romance_presentation(candidate):
        _fail("candidate is not a valid romance presentation")
    return copy.deepcopy(candidate)
