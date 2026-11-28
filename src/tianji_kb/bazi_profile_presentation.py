"""TJ-031.19 / E0427 Lane A: 八字详批 presentation builder.

Formal product-feature construction (batch 5). This module assembles
one plain-language detailed bazi analysis presentation from either

* a unified-compute trim / assembly (``trim_for_bazi_profile`` output
  or a full ``assemble_birth`` assembly: ``chart`` + ``research``), or
* a public bazi-profile scenario result (``pillars`` + the four gated
  public presentations).

It REUSES existing computation and never rebuilds it: the four public
parts are lifted only through their own approved validators
(``strength-public-presentation-v1``,
``bazi-pattern-public-presentation-v1``,
``xiyong-public-presentation-v1``,
``dayun-public-presentation-v1``); the five-element distribution is
deterministic counting over the chart's own pillars; everything else
is presented as research-marked reference or as an explicit undecided
statement.

What this module never does (fail-closed, see the opening plan
``~/workspace/tj-product-opening-plan.md`` §3):

* never invents content, citations, scores, predictions, or a
  "scientific prediction" wording for a research model;
* never promotes a research model to a public verdict: the modern
  strength engine (``strength_model_modern_v1``) and the modern fuyi
  layer (``fuyi-modern-rules-v1``) appear ONLY inside a
  ``research_reference`` block explicitly labelled in plain Chinese
  as a research model, not a classical conclusion;
* never claims a pattern is established without its rule + Golden:
  public establishment comes only from the D-1 whitelist (8 pattern
  names; 比肩/劫财格 -> not_judgeable, enforced here again);
* broken is surfaced only through the single approved classical
  channel (伤官见官); any other research ``broken`` marking is
  counted but never presented as a broken verdict; the P5 modern
  broken flags are never rendered as formal broken conclusions;
* classical fuyi direction rows are NOT buildable
  (``buildable_count=0``, already adjudicated closed); the section
  states that plainly, and ``unified_verdict`` stays None;
* true-solar-time charting is research entry only
  (``bazi_true_solar_chart.py``): the default public charting caliber
  is UNCHANGED, and a comparison is included only when the caller
  supplies an already-computed research comparison -- this module
  never computes one itself (it needs a birthplace longitude, which
  is not part of the bazi-profile input);
* every section carries its own computation basis, applicable
  caliber, and undecided conditions; uncomputable parts say so
  plainly in Chinese, never with a fabricated value.

USER ADJUDICATION 2026-11-28 09:56 (decided scope, supersedes the
cautious limits in the original brief where it says otherwise):

* Q1=C: the modern strength model is opened as a SEPARATE
  research-grade analysis column: model results, 得令 / 得地 / 得势 /
  得助（藏干生扶） / 克泄耗 analysis, each factor's contribution,
  model basis and applicable conditions, uncertainties and
  uncalibrated conditions (土/丁得地未校准, 四库月得令记零 -- stated
  explicitly from the engine's own notes/limitations). The score is
  NOT a percentile, NOT a probability, NOT a classical definite
  conclusion -- labelled plainly, never packaged as a scientific
  prediction. Classical U1 and the modern model are shown SEPARATELY
  and never overwrite each other. ``MODERN_WEIGHTS`` /
  ``MODERN_THRESHOLDS`` are never modified (and never copied here).
* Q2=C: fuyi modern candidate direction and candidate stems are
  opened as a SEPARATE research analysis section (``fuyi_research``):
  current model strength direction, fuyi candidate direction,
  candidate stems present in the chart, candidate formation reasons,
  already-reviewed tiaohou/bingyao results, per-system differences.
  Candidate is NOT a definite useful god. Pattern yongshen STAYS
  undecided: the 14-grid readiness table is never shown, no pattern
  yongshen is fabricated, no unified xiyong verdict is built.
* Q3=A: the full 8-period dayun timeline on the bazi page too, from
  the already-composed public dayun presentation (``periods=8``) --
  no separate recomputation. Each period shows only already-grounded
  content: stems, start interval, end described from the next
  period's start interval, stem ten-god, branch hidden stems reused
  from the natal chart only when the dayun branch matches a natal
  branch, and a liunian query entry. NO age field is produced
  anywhere: the adjudicated dayun boundary (§4.5/§6.2(f) in
  ``bazi_dayun_public.py``) bans age fields from the public object,
  so no start age is computed here; that gap is reported, not filled.

Element mapping note: ``stem_element`` is imported from
``foundations`` (pure, no sealed data). ``branch_element`` in
``foundations`` reads the sealed canonical seed table, which the
public checkout does not carry, so the fixed classical branch ->
element mapping (寅卯木、巳午火、申酉金、亥子水、辰戌丑未土) is
carried here as a literal -- it is the same fixed mapping, not a
new rule, and the tests pin it branch by branch.
"""

import copy

from .bazi_dayun_public import is_valid_public_dayun_presentation
from .bazi_pattern_public import (
    PUBLIC_PATTERN_NAMES,
    is_valid_public_pattern_presentation,
    to_public_pattern_presentation,
)
from .bazi_strength_engine import MODERN_SCORE_RANGE
from .bazi_strength_public import (
    is_valid_public_strength_presentation,
    to_public_strength_presentation,
)
from .bazi_xiyong_engine import MODERN_COMPONENT_NAMES
from .bazi_xiyong_public import is_valid_public_presentation as \
    is_valid_public_xiyong_presentation
from .foundations import BRANCHES, ELEMENTS, STEMS, stem_element

VARIANT = "bazi-profile-presentation-v1"

# Fixed classical branch -> element mapping (see module docstring).
BRANCH_ELEMENTS = {
    "寅": "木", "卯": "木",
    "巳": "火", "午": "火",
    "申": "金", "酉": "金",
    "亥": "水", "子": "水",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
}

# The single approved classical broken channel.
APPROVED_BROKEN_CONDITION = "shangguan_sees_officer_broken"
APPROVED_BROKEN_LABEL = "伤官见官"

RESEARCH_LABEL = "研究参考：以下内容来自已批研究模型，不是古典结论，不作公开判断。"
SEPARATION_LINE = "已审结论与现代模型分开呈现，互不覆盖；现代模型结论永不改写已审结论。"
SCORE_NOTE = (
    "现代模型分数是工程模型内部总分（总分域 [-35, 105]），不是百分位，"
    "不是概率，不是古典旺衰定论，不作科学预测。")
CANDIDATE_NOT_YONGSHEN_LINE = (
    "候选不是确定用神：扶抑现代层只给候选方向与候选干，不作确定用神结论。")
# Q1 component display labels. The engine's own names are 得令 / 得地 /
# 得势 / 藏干生扶 / 克泄耗; the two support components are clarified
# in plain Chinese (显干生扶 = 得势, 藏干生扶 = 得助) so the four
# analyses the adjudication names (得令 / 得地 / 得助 / 克泄耗) are
# all visibly present and no component is hidden.
COMPONENT_DISPLAY_LABELS = {
    "de_ling": "得令",
    "de_di": "得地",
    "de_shi": "得势（显干生扶）",
    "shengfu_hidden": "得助（藏干生扶）",
    "kexiehao": "克泄耗",
}
_COMPONENT_ORDER = ("de_ling", "de_di", "de_shi", "shengfu_hidden",
                    "kexiehao")
# Keys that must never appear anywhere in a built presentation:
# engine weights/thresholds (never modified, never copied), 从格
# candidate screens (never an establishment), and the pattern-yongshen
# readiness table (never shown). The validator scans for them.
_BANNED_KEYS = frozenset((
    "weights", "thresholds", "cong_candidates",
    "yongshen_rule_readiness", "interaction_effects",
    "direction_derivation"))

# Citation-id fields removed from embedded xiyong / dayun copies by
# strip_public_citation_ids (see its docstring).
_STRIPPED_CITATION_KEYS = frozenset((
    "source_id", "section_id", "section_ids", "source_section_id"))
TRUE_SOLAR_LABEL = (
    "研究对照：真太阳时排盘是研究入口，不是公开排盘口径；"
    "公开排盘口径不变（北京时间，午夜 0 点为日界）。")
FUYI_CLASSICAL_LINE = (
    "扶抑古典方向：十行方向表逐行核对后可建行数为 0 行（已裁定关闭），"
    "本节不给出任何扶抑古典方向结论；古典方向表不再重提。")
UNIFIED_VERDICT_LINE = (
    "统一喜用结论：暂不可判（unified_verdict 恒为 None，已裁定恒拒判）。")

_TOP_KEYS = frozenset((
    "variant", "page", "public_enabled", "ai_enabled",
    "chart", "sections", "undecided", "scope_statement", "limitations"))
_SECTION_KEYS = frozenset((
    "id", "title", "caliber", "status", "basis", "lines", "undecided",
    "public", "research_reference"))
_SECTION_IDS = (
    "five_elements", "strength", "pattern", "xiyong", "fuyi_research",
    "dayun", "true_solar")
_SECTION_STATUSES = frozenset(("presented", "not_judgeable", "not_provided"))

SCOPE_STATEMENT = (
    "本详批只呈现已审公开内容与确定性计数；研究模型内容只作明确标注的"
    "研究参考，不作公开判断；暂不可判的部分如实写明，不补结论，不作"
    "吉凶、婚恋、事业、财富或寿命预测。")
LIMITATIONS = (
    "强度公开结论仅限已审的八个充分谓词家族；其余命盘形态暂不可判。",
    "格局公开结论仅限任氏寅月局部真格（8 格名白名单）；其余格局暂不可判。",
    "调候与病药只含 phase-1 已注册依据；扶抑古典方向不可建，统一喜用结论恒拒判。",
    "大运只呈现已注册的方向与交运区间，不折算起运岁数、不判断大运吉凶。",
    "真太阳时对照只是研究入口，不改变公开排盘口径。",
)


def _fail(message):
    raise ValueError(
        "Bazi profile presentation rejected: " + message)


def _pillar_text(pillar):
    """One pillar as (stem, branch, [hidden stems]) from any shape."""
    if not isinstance(pillar, dict):
        _fail("chart pillar must be a mapping")
    stem = pillar.get("stem")
    branch = pillar.get("branch")
    stem_value = stem.get("value") if isinstance(stem, dict) else stem
    branch_value = branch.get("value") if isinstance(branch, dict) \
        else branch
    if stem_value not in list(STEMS) or branch_value not in list(BRANCHES):
        _fail("chart pillar lacks a valid stem or branch")
    hidden = []
    raw_hidden = []
    if isinstance(branch, dict):
        raw_hidden = branch.get("hidden_stems") or []
    if not isinstance(raw_hidden, list):
        _fail("chart pillar hidden_stems must be a list")
    for entry in raw_hidden:
        value = entry.get("stem") if isinstance(entry, dict) else entry
        if value not in list(STEMS):
            _fail("chart pillar hidden stem is not a stem")
        hidden.append(value)
    return stem_value, branch_value, hidden


def _extract_chart(source):
    """Return (pillars, day_master, month_branch, research, public)."""
    if not isinstance(source, dict):
        _fail("source must be a mapping")
    research = {}
    public = {}
    for key in ("strength_presentation", "pattern_presentation",
                "xiyong_presentation", "dayun_presentation"):
        if key in source:
            public[key] = source[key]
    if "chart" in source and "research" in source:
        # Unified trim / assembly path.
        chart = source["chart"]
        if not isinstance(chart, dict):
            _fail("chart must be a mapping")
        raw_pillars = chart.get("pillars")
        day_master = chart.get("day_master")
        if isinstance(day_master, dict):
            day_master = day_master.get("stem")
        month_branch = chart.get("month_branch")
        research = source["research"]
        if not isinstance(research, dict):
            _fail("research must be a mapping")
        # A combined source may also carry the public presentations
        # nested under "public_presentations".
        nested = source.get("public_presentations")
        if isinstance(nested, dict):
            for key in ("strength_presentation", "pattern_presentation",
                        "xiyong_presentation", "dayun_presentation"):
                if key in nested:
                    public[key] = nested[key]
    elif "pillars" in source:
        # Public scenario-result path.
        raw_pillars = source["pillars"]
        day_master = source.get("day_master")
        if isinstance(day_master, dict):
            day_master = day_master.get("stem")
        month_branch = None
    else:
        _fail("source carries neither a unified chart nor a public "
              "scenario result")
    if not isinstance(raw_pillars, list) or len(raw_pillars) != 4:
        _fail("pillars must be the four chart pillars")
    pillars = [_pillar_text(pillar) for pillar in raw_pillars]
    if month_branch is None:
        month_branch = pillars[1][1]
    if day_master != pillars[2][0]:
        _fail("day master drifted from the day pillar stem")
    if month_branch != pillars[1][1]:
        _fail("month branch drifted from the month pillar branch")
    return pillars, day_master, month_branch, research, public


def _counts_text(counts):
    return "、".join("%s %d" % (element, counts[element])
                     for element in ELEMENTS)


def _section_five_elements(pillars, day_master):
    stem_counts = {element: 0 for element in ELEMENTS}
    branch_counts = {element: 0 for element in ELEMENTS}
    hidden_counts = {element: 0 for element in ELEMENTS}
    total_counts = {element: 0 for element in ELEMENTS}
    for stem, branch, hidden in pillars:
        stem_counts[stem_element(stem)] += 1
        branch_counts[BRANCH_ELEMENTS[branch]] += 1
        for hidden_stem in hidden:
            hidden_counts[stem_element(hidden_stem)] += 1
    for element in ELEMENTS:
        total_counts[element] = (stem_counts[element]
                                 + branch_counts[element]
                                 + hidden_counts[element])
    day_element = stem_element(day_master)
    same_stems = [stem for stem, _, _ in pillars
                  if stem_element(stem) == day_element]
    hidden_total = sum(hidden_counts.values())
    lines = [
        "四柱：%s。" % "、".join(stem + branch for stem, branch, _ in pillars),
        "日主%s属%s；天干中与日主同五行的干有 %d 个（%s）。"
        % (day_master, day_element, len(same_stems),
           "、".join(same_stems) if same_stems else "无"),
        "天干五行计数：%s。" % _counts_text(stem_counts),
        "地支五行计数：%s。" % _counts_text(branch_counts),
        "藏干五行计数：%s（藏干共 %d 个）。"
        % (_counts_text(hidden_counts), hidden_total),
        "合计五行计数（天干＋地支＋藏干）：%s。"
        % _counts_text(total_counts),
        "以上只是确定性计数，不作旺衰、喜用、格局或吉凶判断。",
    ]
    undecided = []
    if hidden_total == 0:
        undecided.append(
            "本输入未附带月支藏干以外的藏干明细，藏干计数只计已附带的藏干；"
            "缺失的藏干不补算。")
    return {
        "id": "five_elements",
        "title": "五行分布与日主",
        "caliber": "确定性计数：四柱干支与附带的藏干",
        "status": "presented",
        "basis": "本盘四柱干支与藏干的五行归属计数；天干按固定配属，"
                 "地支按固定配属（寅卯木、巳午火、申酉金、亥子水、"
                 "辰戌丑未土）。",
        "lines": lines,
        "undecided": undecided,
        "public": {
            "ganzhi": [stem + branch for stem, branch, _ in pillars],
            "day_master": day_master,
            "day_master_element": day_element,
            "stem_counts": stem_counts,
            "branch_counts": branch_counts,
            "hidden_counts": hidden_counts,
            "total_counts": total_counts,
        },
        "research_reference": None,
    }


def strip_public_citation_ids(value):
    """Deep copy of ``value`` with every citation-id field removed.

    The xiyong / dayun presentations carry bound citations
    (``source_id`` / ``section_id`` / ``section_ids`` /
    ``source_section_id``) that the public-boundary check
    (``public_boundary.py``) exempts ONLY under a
    ``xiyong_presentation`` / ``dayun_presentation`` key. A profile
    (or compatibility) section embeds those presentations under a
    different key (``public`` / ``person_a`` / ``person_b``), where
    the exemption does not apply, so the embedded copies carry the
    same reviewed content with the raw source / section references
    removed. Block-level source labels (《穷通宝鉴》/《神峰通考》),
    method labels and the plain-language lines already state the
    source. The scalar registry ids (``phase1_rule_id`` /
    ``phase2_step_id``) and ``consumed_rule_ids`` are reviewed
    shapes (``public_boundary.py``) and are kept.
    """
    if isinstance(value, dict):
        return {key: strip_public_citation_ids(item)
                for key, item in value.items()
                if key not in _STRIPPED_CITATION_KEYS}
    if isinstance(value, list):
        return [strip_public_citation_ids(item) for item in value]
    return copy.deepcopy(value)


def _lift_public(public, key, validator, projector, label,
                 day_master=None, month_branch=None):
    """Lift one gated public presentation, or None when absent.

    A present-but-invalid object fails closed (ValueError): a forged
    public object must never be silently dropped into "not provided".
    When the candidate carries a day master / month branch, they must
    agree with this chart; a presentation from another chart is a
    drift and fails closed.
    """
    candidate = public.get(key)
    if candidate is None:
        return None
    if not validator(candidate):
        _fail("invalid public presentation for " + label)
    if day_master is not None and "day_master" in candidate \
            and candidate["day_master"] != day_master:
        _fail("public presentation day master drifted from the chart")
    if month_branch is not None and "month_branch" in candidate \
            and candidate["month_branch"] != month_branch:
        _fail("public presentation month branch drifted from the chart")
    return projector(candidate)


def _modern_strength_reference(strength_research):
    """Q1=C: the modern strength model as a SEPARATE research column.

    Returns the research-column block, or None when the research
    strength output is absent or has no modern block. Only an
    allowlisted subset is copied: model id, verdict, score, score
    band/range, classification status, the five factor components
    (得令 / 得地 / 得势 / 得助 / 克泄耗 with each factor's score and
    detail), the engine's own uncertainty notes and limitations
    (which state the uncalibrated conditions explicitly: 土/丁得地
    未校准, 四库月得令记零), and the abstain reason when it abstains.
    NEVER copied: weights, thresholds, cong_candidates (a screen,
    never an establishment), interaction_effects.
    """
    if not isinstance(strength_research, dict):
        return None
    modern = strength_research.get("modern")
    if not isinstance(modern, dict) \
            or modern.get("model_kind") != "modern_engineering":
        return None
    components = []
    raw_components = modern.get("components")
    if isinstance(raw_components, dict):
        for key in _COMPONENT_ORDER:
            entry = raw_components.get(key)
            if not isinstance(entry, dict):
                continue
            score = entry.get("score")
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                continue
            components.append({
                "key": key,
                "label": COMPONENT_DISPLAY_LABELS[key],
                "name_cn": MODERN_COMPONENT_NAMES.get(key),
                "score": score,
                "detail": entry.get("detail")
                          if isinstance(entry.get("detail"), str) else None,
            })
    flags = modern.get("uncertainty_flags")
    if not isinstance(flags, list):
        flags = []
    uncertainty_lines = []
    notes = modern.get("notes")
    if isinstance(notes, list):
        uncertainty_lines = [note for note in notes
                             if isinstance(note, str)]
    limitations = modern.get("limitations")
    if not isinstance(limitations, list):
        limitations = []
    score_range = list(MODERN_SCORE_RANGE)
    return {
        "research_only": True,
        "column": "research",
        "label": RESEARCH_LABEL,
        "model_id": modern.get("model_id"),
        "verdict": modern.get("verdict"),
        "score": modern.get("score"),
        "score_band": modern.get("score_band"),
        "score_range": score_range,
        "score_note": SCORE_NOTE,
        "classification_status": modern.get("classification_status"),
        "definite_classification": modern.get("definite_classification"),
        "components": components,
        "uncertainty_flags": [flag for flag in flags
                              if isinstance(flag, str)],
        "uncertainty_lines": uncertainty_lines,
        "limitations": [line for line in limitations
                        if isinstance(line, str)],
        "abstain_reason": modern.get("abstain_reason"),
        "abstain_detail": modern.get("abstain_detail"),
    }


def _section_strength(pillars, day_master, month_branch, research, public):
    presentation = _lift_public(
        public, "strength_presentation",
        is_valid_public_strength_presentation,
        to_public_strength_presentation, "strength",
        day_master, month_branch)
    undecided = []
    research_reference = _modern_strength_reference(
        research.get("strength"))
    if presentation is None:
        lines = ["强度公开呈现未附带，本节暂不可判；未呈现不等于弱。"]
        undecided.append("未传入已审强度公开呈现，强度结论暂不可判。")
        status = "not_provided"
    elif presentation["status"] == "presented":
        classification = presentation["classification"]
        lines = [
            "日主%s生于%s月，命中了一个已审的局部形态：%s。"
            % (day_master, month_branch,
               "强形态" if classification == "strong" else "弱形态"),
            "该结论只覆盖这一个已审形态，不覆盖全盘旺衰；"
            "未命中不等于弱。",
        ]
        status = "presented"
    elif presentation["status"] == "not_judgeable":
        lines = ["本盘未命中任何已审局部形态条件，强度暂不可判；"
                 "未命中不等于弱。"]
        undecided.append("本盘的日主与月份组合不在已审谓词命中范围内，"
                         "或谓词条件证据不足。")
        status = "not_judgeable"
    else:  # conflict
        lines = ["本盘存在未裁定的冲突，强度暂不可判；不作任何强弱结论。"]
        undecided.append("强度评估存在未裁定的冲突。")
        status = "not_judgeable"
    # Q1=C: the modern model is a SEPARATE research column, never
    # merged into the public lines above and never overwriting them.
    if research_reference is not None:
        lines.append(SEPARATION_LINE)
        lines.append("研究列（现代强度模型）：")
        verdict = research_reference["verdict"]
        score = research_reference["score"]
        if verdict == "abstain":
            lines.append(
                "现代模型弃判（%s）；不输出模型分数与分项。"
                % (research_reference["abstain_reason"] or "未注明原因"))
        else:
            lines.append(
                "现代模型结论：%s，总分 %s 分（总分域 [%s, %s]）。"
                % (verdict, score, research_reference["score_range"][0],
                   research_reference["score_range"][1]))
            lines.append(SCORE_NOTE)
            for component in research_reference["components"]:
                detail = component["detail"]
                lines.append(
                    "%s：%+d 分%s。"
                    % (component["label"], component["score"],
                       "（" + detail + "）" if detail else ""))
            if research_reference["classification_status"] != "definite":
                lines.append(
                    "分类状态：%s；分数为研究性暂定分，不输出确定旺衰分类。"
                    % research_reference["classification_status"])
        for line in research_reference["uncertainty_lines"]:
            lines.append(line)
        lines.append(RESEARCH_LABEL)
    else:
        undecided.append("现代强度模型研究输出未附带，研究列暂不呈现。")
    return {
        "id": "strength",
        "title": "强弱计算与依据",
        "caliber": "公开部分只认 strength-public-presentation-v1；"
                   "研究列只认 strength_model_modern_v1",
        "status": status,
        "basis": "公开结论来自同一请求的已审强度公开呈现；"
                 "研究列来自同一盘的现代强度模型输出，只作对照，"
                 "与公开结论分开呈现，互不覆盖。",
        "lines": lines,
        "undecided": undecided,
        "public": presentation,
        "research_reference": research_reference,
    }


def _section_pattern(pillars, day_master, month_branch, research, public):
    presentation = _lift_public(
        public, "pattern_presentation",
        is_valid_public_pattern_presentation,
        to_public_pattern_presentation, "pattern",
        day_master, month_branch)
    if presentation is not None and presentation["status"] == "presented" \
            and presentation.get("pattern") is not None \
            and presentation["pattern"] not in PUBLIC_PATTERN_NAMES:
        # Defence in depth: the validator already enforces the
        # whitelist, but a presented name outside it must never pass.
        _fail("presented pattern outside the D-1 whitelist")
    undecided = []
    lines = []
    broken_lines = []
    pattern_research = research.get("pattern")
    counts_by_state = {}
    approved_broken = []
    other_broken = 0
    if isinstance(pattern_research, dict):
        results = pattern_research.get("results")
        if isinstance(results, dict):
            for key, result in results.items():
                if not isinstance(result, dict):
                    continue
                state = result.get("state")
                counts_by_state[state] = counts_by_state.get(state, 0) + 1
                if state == "broken":
                    condition = result.get("broken_condition")
                    if condition == APPROVED_BROKEN_CONDITION:
                        approved_broken.append(key)
                    else:
                        other_broken += 1
    if approved_broken:
        broken_lines.append(
            "破格：%s（%s）。这是唯一已审的古典破格通道。"
            % ("、".join(approved_broken), APPROVED_BROKEN_LABEL))
    elif other_broken:
        undecided.append(
            "研究引擎对 %d 格标有破格，但不在唯一已审通道（%s）内，"
            "本节不作破格结论。" % (other_broken, APPROVED_BROKEN_LABEL))
    if counts_by_state:
        broken_lines.append(
            "格局研究引擎逐格状态计数：%s；其中成立只认公开呈现，"
            "其余只作候选、冲突或不可判。"
            % "、".join("%s %d 格" % (state, count)
                        for state, count in sorted(counts_by_state.items())))
    if presentation is None:
        lines = ["格局公开呈现未附带，本节暂不可判；未呈现不等于假格。"]
        undecided.append("未传入 D-1 格局公开呈现，格局结论暂不可判。")
        status = "not_provided"
    elif presentation["status"] == "presented" \
            and presentation.get("outcome") == "true_pattern":
        lines = [
            "日主%s生于寅月，%s" % (day_master, presentation["statement"]),
            "格名：%s；该结论只覆盖这一个已审局部事实，"
            "不覆盖全盘格局。" % presentation["pattern"],
        ]
        status = "presented"
    elif presentation["status"] == "presented":
        lines = [
            "日主%s生于寅月，%s" % (day_master, presentation["statement"]),
            "该结论只覆盖这一个已审局部事实，不覆盖全盘格局。",
        ]
        status = "presented"
    elif presentation["status"] == "not_judgeable":
        reason = presentation.get("reason")
        if reason == "pattern_name_not_public":
            # The D5 name must never reach a public response: the
            # grid name itself is not in the 8-name whitelist, so
            # the line states the exclusion without naming it.
            lines = ["本盘的格名暂不在公开呈现范围内（不在 8 格名白名单内），"
                     "暂不可判；不改写格名，不作任何格局结论。"]
        else:
            lines = ["本盘暂不可判，不作任何格局结论；"
                     "暂不可判不等于假格。"]
        undecided.append("D-1 格局公开呈现为暂不可判。")
        status = "not_judgeable"
    else:  # abstained
        lines = ["本次不作格局呈现，不作任何格局结论。"]
        undecided.append("D-1 格局公开呈现为不作呈现。")
        status = "not_judgeable"
    lines.extend(broken_lines)
    d1_note = None
    if isinstance(research, dict):
        d1 = research.get("pattern_d1")
        if isinstance(d1, dict) \
                and d1.get("status") == "not_attempted_here":
            d1_note = ("D-1 不在统一入口内重推；公开格局结论只走"
                       "场景门控的 pattern_presentation。")
    if d1_note is not None:
        undecided.append(d1_note)
    return {
        "id": "pattern",
        "title": "格局辨别、成立与破格",
        "caliber": "公开成立只认 D-1 白名单（8 格名）；"
                   "破格只认伤官见官一途",
        "status": status,
        "basis": "公开结论来自同一请求的 D-1 格局公开呈现；"
                 "破格与逐格状态来自格局研究引擎输出，"
                 "只作候选、冲突或不可判的计数，不立新格。",
        "lines": lines,
        "undecided": undecided,
        "public": presentation,
        "research_reference": None,
    }


def _section_xiyong(pillars, day_master, month_branch, research, public):
    presentation = _lift_public(
        public, "xiyong_presentation",
        is_valid_public_xiyong_presentation,
        strip_public_citation_ids, "xiyong",
        day_master, month_branch)
    undecided = []
    lines = []
    # Q2=C: the fuyi modern reference lives in the separate
    # fuyi_research section, not here; this section stays public-only.
    research_reference = None
    # S4：此处不得运行时读取扶抑切片审定记录（零接线，禁止导入
    # 扶抑切片审定登记）；已裁定关闭态（可建行数 0 行）
    # 由下文 FUYI_CLASSICAL_LINE 字面陈述，记录漂移由
    # test_tj0131_fuyi_slice 钉死，不在此设运行时守卫。
    if presentation is None:
        lines = ["调候与病药公开呈现未附带，本节暂不可判。"]
        undecided.append("未传入喜用 phase-1 公开呈现，调候与病药暂不可判。")
        status = "not_provided"
    else:
        if presentation.get("unified_verdict") is not None:
            _fail("xiyong unified_verdict must stay None")
        tiaohou = presentation["blocks"]["tiaohou"]
        bingyao = presentation["blocks"]["bingyao"]
        lines.extend(tiaohou.get("lines") or [])
        lines.extend(bingyao.get("lines") or [])
        if tiaohou.get("state") == "not_judgeable":
            undecided.append("调候条目在审定文本中不存在，该组合调候暂不可判。")
        for pair in bingyao.get("pairs") or []:
            if pair.get("status") == "not_triggered":
                undecided.append(
                    "病药%s未触发；未触发不等于无病，去病效力暂不可判。"
                    % pair.get("pair_id"))
        status = "presented"
    lines.append(FUYI_CLASSICAL_LINE)
    lines.append(UNIFIED_VERDICT_LINE)
    return {
        "id": "xiyong",
        "title": "扶抑、调候、病药与格局用神",
        "caliber": "公开只认 xiyong-public-presentation-v1（调候 119 条、"
                   "病药 2 对）；扶抑现代层见 fuyi_research 节",
        "status": status,
        "basis": "公开结论来自同一请求的喜用 phase-1 公开呈现；"
                 "扶抑古典方向状态来自已裁定的扶抑切片审定记录；"
                 "格局用神恒未审（useful_god 恒 None）。",
        "lines": lines,
        "undecided": undecided,
        "public": presentation,
        "research_reference": research_reference,
    }


def _fuyi_systems(research):
    """Return (fuyi, pattern_yongshen) research systems, or (None, None)."""
    xiyong_research = research.get("xiyong")
    if not isinstance(xiyong_research, dict):
        return None, None
    systems = xiyong_research.get("systems")
    if not isinstance(systems, dict):
        return None, None
    return systems.get("fuyi"), systems.get("pattern_yongshen")


def _section_fuyi_research(pillars, day_master, month_branch, research,
                           public):
    """Q2=C: fuyi modern candidates as a SEPARATE research section.

    Shows the current model strength direction (the modern strength
    verdict/score that feeds fuyi), the fuyi candidate direction,
    candidate stems present in the chart, candidate formation reasons
    (component explanations), the already-reviewed tiaohou/bingyao
    results, and the per-system differences. Candidate is NOT a
    definite useful god. Pattern yongshen STAYS undecided: the
    14-grid readiness table is never copied or shown, no pattern
    yongshen is fabricated, and no unified verdict is built. A
    candidate stem is listed only when it is actually a visible stem
    of this chart; any other claimed candidate is reported as
    inconsistent, never presented.
    """
    undecided = []
    lines = []
    fuyi, pattern_yongshen = _fuyi_systems(research)
    if isinstance(pattern_yongshen, dict):
        if pattern_yongshen.get("useful_god") is not None:
            _fail("pattern useful_god is not None in research")
    visible_stems = {}
    for name, (stem, _, _) in zip(("year", "month", "day", "hour"),
                                  pillars):
        if name != "day":
            visible_stems.setdefault(stem, name)
    # Per-system comparison (public parts first, then the research layer).
    xiyong_public = public.get("xiyong_presentation")
    if isinstance(xiyong_public, dict):
        tiaohou = xiyong_public["blocks"]["tiaohou"]
        bingyao = xiyong_public["blocks"]["bingyao"]
        if tiaohou.get("state") == "presented":
            lines.append("调候体系（已审）：取用顺序见本页调候节。")
        else:
            lines.append("调候体系（已审）：条目在审定文本中不存在，"
                         "该组合调候暂不可判。")
        triggered = [pair.get("pair_id") for pair in
                     bingyao.get("pairs") or []
                     if pair.get("status") == "triggered"]
        lines.append(
            "病药体系（已审）：两对结构候选，去病效力未裁定；"
            "%s。"
            % ("已触发：" + "、".join(triggered) if triggered else "两对均未触发"))
    else:
        lines.append("调候与病药体系：公开呈现未附带，暂不可判。")
        undecided.append("未传入喜用 phase-1 公开呈现，调候与病药暂不可判。")
    lines.append(FUYI_CLASSICAL_LINE)
    modern = fuyi.get("modern") if isinstance(fuyi, dict) else None
    research_reference = None
    if not isinstance(modern, dict) \
            or modern.get("model_kind") != "modern_engineering":
        lines.append("扶抑现代层：研究输出未附带，候选方向与候选干暂不呈现。")
        undecided.append("扶抑现代层研究输出未附带，候选方向与候选干暂不可判。")
        status = "not_provided"
    else:
        input_verdict = modern.get("input_verdict")
        input_score = modern.get("input_score")
        lines.append(
            "当前模型强度方向：现代强度模型结论为 %s（%s 分）；"
            "该结论只是工程模型输出，不是古典旺衰定论。"
            % (input_verdict, input_score))
        direction_cn = modern.get("direction_cn")
        raw_candidates = modern.get("candidate_stems")
        verified = []
        if isinstance(raw_candidates, list):
            for candidate in raw_candidates:
                if not isinstance(candidate, dict):
                    continue
                stem = candidate.get("stem")
                pillar = candidate.get("pillar")
                if stem in visible_stems and visible_stems[stem] == pillar:
                    verified.append({
                        "stem": stem,
                        "pillar": pillar,
                        "ten_god": candidate.get("ten_god"),
                        "element": candidate.get("element"),
                    })
                else:
                    undecided.append(
                        "候选干 %s（%s）与本盘显干不符，不列为候选。"
                        % (stem, pillar))
        elif raw_candidates is not None:
            undecided.append("候选干形状异常，不列为候选。")
        if direction_cn is None:
            lines.append("扶抑候选方向：现代层未给方向（balanced 只是中间"
                         "分数带，不是古典中和裁决）；候选干暂不呈现。")
            undecided.append("扶抑现代层未给候选方向。")
            status = "not_judgeable"
        else:
            lines.append(
                "扶抑候选方向：%s（研究模型候选，不是确定用神）。"
                % direction_cn)
            if verified:
                lines.append(
                    "候选干（均在本盘显干中）：%s。"
                    % "、".join("%s（%s，%s）" % (
                        item["stem"],
                        {"year": "年干", "month": "月干",
                         "hour": "时干"}.get(item["pillar"], item["pillar"]),
                        item["ten_god"])
                        for item in verified))
            else:
                lines.append("候选干：本盘显干中无方向元素之干，候选为空。")
                undecided.append("扶抑现代层候选干为空。")
            status = "presented"
        explanations = modern.get("component_explanations")
        formation_reasons = []
        if isinstance(explanations, list):
            for explanation in explanations:
                if not isinstance(explanation, dict):
                    continue
                note = explanation.get("note")
                if isinstance(note, str):
                    formation_reasons.append({
                        "component": explanation.get("component"),
                        "name_cn": explanation.get("name_cn"),
                        "score": explanation.get("score"),
                        "reading": explanation.get("reading"),
                        "note": note,
                    })
        if formation_reasons:
            lines.append("候选形成理由（分项符号读数，不构成独立的方向结论）：")
            for reason in formation_reasons:
                lines.append(reason["note"])
        lines.append(CANDIDATE_NOT_YONGSHEN_LINE)
        research_reference = {
            "research_only": True,
            "label": RESEARCH_LABEL,
            "model_id": modern.get("model_id"),
            "status": modern.get("status"),
            "input_verdict": input_verdict,
            "input_score": input_score,
            "direction": modern.get("direction"),
            "direction_cn": direction_cn,
            "direction_elements": copy.deepcopy(
                modern.get("direction_elements") or []),
            "ten_god_classes": copy.deepcopy(
                modern.get("ten_god_classes") or []),
            "candidate_stems": verified,
            "candidate_scope": modern.get("candidate_scope"),
            "confidence": modern.get("confidence"),
            "uncertainty": copy.deepcopy(modern.get("uncertainty") or []),
            "formation_reasons": formation_reasons,
            "reason": modern.get("reason"),
        }
    lines.append(
        "三体系口径不同，并列呈现，不合并为统一结论；"
        "统一喜用结论暂不可判。")
    lines.append(
        "格局用神：暂不可判；14 格就绪表不公开呈现，用神恒未审，"
        "不捏造用神。")
    lines.append(RESEARCH_LABEL)
    return {
        "id": "fuyi_research",
        "title": "扶抑现代层研究（研究）",
        "caliber": "研究只认 fuyi-modern-rules-v1；古典扶抑方向不可建；"
                   "格局用神恒未审",
        "status": status,
        "basis": "扶抑现代层来自同一盘的喜用研究引擎输出；"
                 "调候与病药来自同一请求的喜用 phase-1 公开呈现；"
                 "候选干只认本盘显干，候选不是确定用神。",
        "lines": lines,
        "undecided": undecided,
        "public": None,
        "research_reference": research_reference,
    }


def _summarize_dayun_periods(presentation, pillars):
    """Q3=A: grounded per-period summary from a validated presentation.

    Only fields the public presentation itself carries (period index,
    ganzhi, stem, branch, stem ten-god relative to the natal day
    stem, state, start interval + status). A period's end is
    described ONLY from the NEXT period's start interval (the same
    rule the timeline component uses); the last period's end is not
    provided. Branch hidden stems are reused from the natal chart
    only when the dayun branch matches a natal branch (the hidden
    stems then come from the chart's own already-grounded pillars);
    otherwise they are not listed. NO age field is produced anywhere:
    the adjudicated dayun boundary (§4.5/§6.2(f)) bans age fields
    from the public object, so no start age is computed here.
    ``liunian_entry`` marks whether the period offers a liunian query
    entry (navigation only, never a liunian verdict).
    """
    hidden_by_branch = {}
    for _, branch, hidden in pillars:
        hidden_by_branch.setdefault(branch, list(hidden))
    methods = presentation.get("methods")
    if not isinstance(methods, dict):
        return {}
    summary = {}
    for method in ("sanming", "shenfeng"):
        view = methods.get(method)
        if not isinstance(view, dict):
            continue
        entries = view.get("entries")
        if not isinstance(entries, list):
            continue
        periods = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            branch = entry.get("branch")
            hidden = hidden_by_branch.get(branch)
            nxt = entries[index + 1] if index + 1 < len(entries) else None
            if nxt is None:
                end_description = "末段无终点：未提供。"
            elif isinstance(nxt, dict) and nxt.get("state") == "interval" \
                    and isinstance(nxt.get("start_interval"), dict):
                end_description = (
                    "本运约在下一运交运区间之前结束：结束于第 %s 运"
                    "交运区间内。" % nxt.get("period_index"))
            else:
                end_description = "下一运交运区间未提供，本运终点未提供。"
            periods.append({
                "period_index": entry.get("period_index"),
                "ganzhi": entry.get("ganzhi"),
                "stem": entry.get("stem"),
                "branch": branch,
                "ten_god": entry.get(
                    "ten_god_relative_to_natal_day_stem"),
                "state": entry.get("state"),
                "start_interval": copy.deepcopy(
                    entry.get("start_interval")),
                "start_interval_status": entry.get("start_interval_status"),
                "end_description": end_description,
                "branch_hidden_stems": hidden,
                "branch_hidden_stems_source": (
                    "natal_chart_same_branch" if hidden is not None
                    else None),
                "liunian_entry": entry.get("state") == "interval",
                "liunian_entry_note": (
                    "进入流年页查看其中某年（导航，不作流年判断）。"
                    if entry.get("state") == "interval"
                    else "交运区间未提供，无流年入口。"),
            })
        summary[method] = periods
    return summary


def _section_dayun(pillars, day_master, month_branch, research, public):
    presentation = _lift_public(
        public, "dayun_presentation",
        is_valid_public_dayun_presentation,
        strip_public_citation_ids, "dayun",
        day_master, month_branch)
    undecided = []
    periods = None
    if presentation is None:
        lines = ["未选择传统大运口径，本节不呈现大运时间轴；"
                 "大运只在显式选择传统口径时呈现。"]
        undecided.append("未传入大运公开呈现，大运暂不呈现。")
        status = "not_provided"
    else:
        periods = _summarize_dayun_periods(presentation, pillars)
        sanming_count = len(periods.get("sanming") or [])
        lines = ["大运方向与交运区间按两口径分立呈现（区间口径，"
                 "不折算起运岁数、不判断大运吉凶）。"]
        if sanming_count == 8:
            lines.append("三命口径呈现全部 8 运；每运只含已核实的干支、"
                         "交运区间、十神与藏干（与原局同支复用），"
                         "不作跨层效力与吉凶判断。")
        else:
            lines.append("三命口径呈现 %d 运（不是 8 运），本节只呈现"
                         "已附带的运数。" % sanming_count)
            undecided.append("三命口径运数不是 8 运。")
        lines.append("年龄区间不呈现：公开大运对象不含年龄字段，"
                     "不折算起运年龄。")
        if presentation.get("status") == "unresolved":
            lines.append("交运时间暂不可判。")
            undecided.append("大运公开呈现为未 resolved，交运时间暂不可判。")
        status = "presented"
    return {
        "id": "dayun",
        "title": "大运时间轴",
        "caliber": "公开只认 dayun-public-presentation-v1（8 运，区间口径）",
        "status": status,
        "basis": "公开结论来自同一请求的大运公开呈现；"
                 "每运摘要只转写该呈现已含的字段，运末只由下一运"
                 "交运区间描述；未选择传统口径时不呈现。",
        "lines": lines,
        "undecided": undecided,
        "public": presentation,
        "research_reference": None,
        "periods": periods,
    }


def _section_true_solar(source):
    comparison = source.get("true_solar_comparison")
    undecided = []
    if comparison is None:
        lines = ["未提供出生地经纬度，未作真太阳时对照；"
                 "公开排盘口径不变（北京时间，午夜 0 点为日界）。"]
        undecided.append("未传入真太阳时研究对照，真太阳时排盘暂不可判。")
        return {
            "id": "true_solar",
            "title": "真太阳时对照（研究）",
            "caliber": "研究入口 bazi_true_solar_chart.py；"
                       "公开排盘口径不变",
            "status": "not_provided",
            "basis": "真太阳时对照是研究入口，需出生地经纬度；"
                     "未提供时不作对照，不改变公开排盘。",
            "lines": lines,
            "undecided": undecided,
            "public": None,
            "research_reference": None,
        }
    if not isinstance(comparison, dict) \
            or comparison.get("research_only") is not True:
        _fail("true solar comparison must be a research_only record")
    changed = comparison.get("changed_pillars")
    if not isinstance(changed, list):
        changed = []
    lines = [TRUE_SOLAR_LABEL]
    if changed:
        lines.append("与公开排盘相比，真太阳时排盘有变化的柱：%s；"
                     "其余柱相同。本对照只作研究比较，不替换公开排盘。"
                     % "、".join(str(item) for item in changed))
    else:
        lines.append("与公开排盘相比，真太阳时排盘四柱相同；"
                     "本对照只作研究比较，不替换公开排盘。")
    return {
        "id": "true_solar",
        "title": "真太阳时对照（研究）",
        "caliber": "研究入口 bazi_true_solar_chart.py；公开排盘口径不变",
        "status": "presented",
        "basis": "调用方提供的真太阳时研究对照记录；"
                 "本模块不自行计算真太阳时排盘。",
        "lines": lines,
        "undecided": undecided,
        "public": None,
        "research_reference": {
            "research_only": True,
            "label": TRUE_SOLAR_LABEL,
            "changed_pillars": copy.deepcopy(changed),
            "comparison": copy.deepcopy(comparison),
        },
    }


def build_bazi_profile_presentation(source):
    """Build the plain-language detailed bazi presentation for one chart.

    ``source`` is a unified trim / assembly or a public scenario
    result (see the module docstring). Returns a JSON-able dict with
    ``sections`` in V1.0 reading order. Raises ``ValueError`` on any
    drift, forgery, or incompletely bound public object -- the caller
    must fail the request, never return a partial presentation.
    """
    pillars, day_master, month_branch, research, public = \
        _extract_chart(source)
    sections = [
        _section_five_elements(pillars, day_master),
        _section_strength(pillars, day_master, month_branch, research,
                          public),
        _section_pattern(pillars, day_master, month_branch, research,
                         public),
        _section_xiyong(pillars, day_master, month_branch, research,
                        public),
        _section_fuyi_research(pillars, day_master, month_branch,
                               research, public),
        _section_dayun(pillars, day_master, month_branch, research,
                       public),
        _section_true_solar(source),
    ]
    undecided = []
    for section in sections:
        undecided.extend(section["undecided"])
    return {
        "variant": VARIANT,
        "page": "bazi-profile",
        "public_enabled": True,
        "ai_enabled": False,
        "chart": {
            "ganzhi": [stem + branch for stem, branch, _ in pillars],
            "day_master": day_master,
            "month_branch": month_branch,
        },
        "sections": sections,
        "undecided": undecided,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }


def _contains_banned_key(value, *, inside_public=False):
    """True when a banned key appears outside a ``public`` subtree.

    The ``public`` sub-objects are validated by their own gate
    validators and may carry their own registered fields; everything
    this builder adds (research references, the dayun period summary)
    must never carry weights, thresholds, cong screens, the
    readiness table, interaction effects, or a direction derivation.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "public":
                if _contains_banned_key(item, inside_public=True):
                    return True
                continue
            if not inside_public and key in _BANNED_KEYS:
                return True
            if _contains_banned_key(item, inside_public=inside_public):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_banned_key(item, inside_public=inside_public)
                   for item in value)
    return False


def is_valid_bazi_profile_presentation(obj):
    """Closed-shape validator for the presentation object.

    Exact top-level key set, the seven sections in V1.0 order (the
    Q2=C fuyi research section sits between xiyong and dayun), the
    status enum, and the research-reference rule: any
    ``research_reference`` must carry ``research_only=True`` and its
    plain-Chinese research label. The dayun section alone may carry
    the additional ``periods`` summary. A candidate carrying any
    other key (in particular a raw research block, an evidence id, a
    score outside a labelled research reference, engine weights /
    thresholds, or the pattern-yongshen readiness table) is invalid.
    """
    if not isinstance(obj, dict) or set(obj) != _TOP_KEYS:
        return False
    if obj.get("variant") != VARIANT or obj.get("page") != "bazi-profile":
        return False
    if obj.get("public_enabled") is not True \
            or obj.get("ai_enabled") is not False:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    chart = obj.get("chart")
    if not isinstance(chart, dict) or set(chart) != {
            "ganzhi", "day_master", "month_branch"}:
        return False
    if not isinstance(chart.get("ganzhi"), list) \
            or len(chart["ganzhi"]) != 4:
        return False
    sections = obj.get("sections")
    if not isinstance(sections, list) or len(sections) != 7:
        return False
    if [section.get("id") for section in sections] != list(_SECTION_IDS):
        return False
    for section in sections:
        if not isinstance(section, dict):
            return False
        allowed = set(_SECTION_KEYS)
        if section.get("id") == "dayun":
            allowed.add("periods")
            periods = section.get("periods")
            if periods is not None and not isinstance(periods, dict):
                return False
        if set(section) != allowed:
            return False
        if section.get("status") not in _SECTION_STATUSES:
            return False
        if not isinstance(section.get("lines"), list) \
                or not section["lines"] \
                or not all(isinstance(line, str) for line in section["lines"]):
            return False
        if not isinstance(section.get("undecided"), list):
            return False
        if not isinstance(section.get("title"), str) \
                or not isinstance(section.get("caliber"), str) \
                or not isinstance(section.get("basis"), str):
            return False
        reference = section.get("research_reference")
        if reference is not None:
            if not isinstance(reference, dict) \
                    or reference.get("research_only") is not True \
                    or not isinstance(reference.get("label"), str):
                return False
            components = reference.get("components")
            if components is not None:
                if not isinstance(components, list):
                    return False
                for component in components:
                    if not isinstance(component, dict) \
                            or set(component) != {
                                "key", "label", "name_cn", "score",
                                "detail"}:
                        return False
            candidate_stems = reference.get("candidate_stems")
            if candidate_stems is not None \
                    and not isinstance(candidate_stems, list):
                return False
    if not isinstance(obj.get("undecided"), list):
        return False
    if _contains_banned_key(obj):
        return False
    return True


def to_public_bazi_profile_presentation(candidate):
    """Allowlist projection of a validated presentation candidate.

    Returns a fresh dict built key by key -- never a verbatim copy.
    A candidate that fails the closed-shape validator raises
    ``ValueError``; the caller treats that as "strip the object",
    never as a partial release.
    """
    if not is_valid_bazi_profile_presentation(candidate):
        _fail("candidate is not a valid bazi profile presentation")
    result = {key: copy.deepcopy(candidate[key])
              for key in sorted(_TOP_KEYS)}
    return result
