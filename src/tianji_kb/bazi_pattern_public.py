"""TJ-012.3 D-1 寅月真格有限公开呈现（Stage B）: the public
pattern-presentation builder.

Authorized by the user's 2026-11-10 decision: a LIMITED EXCEPTION to
the U1 pattern-field ban (the ban itself stands; this batch does not
lift it). The exception covers exactly one reviewed local fact -- the
Ren-branch 寅月 true-pattern determination (Variant
``ren-pattern-yin-true-v1``, Phase1 bazi.rule.r037) -- and only through
the dedicated presentation Variant
``bazi-pattern-public-presentation-v1`` under the new output key
``pattern_presentation``. The underlying D-1 determination stays
research_only / public_enabled=False / ai_enabled=False and is NEVER
flipped; the research raw block (``pattern_determination_ren_yin``)
is never exposed wholesale. Only the independently reviewed
presentation object may be public_enabled=true; ai_enabled is
always false.

What the object is and is not. It states, for one chart of the same
request, whether this pilot's true-pattern conditions are met, and
nothing else. A presented positive names one approved pattern, the
commander stem, and the reviewed visible-stem facts. A presented
negative states the D1 conservative reading verbatim in substance --
司令不透、无真格 -- and never writes 假格. The object never carries
破格/成败/清浊， never carries a pattern useful-god / 喜忌 / 吉凶，
never carries a career/wealth/marriage/lifespan prediction, never
presents another month's pattern conclusion, and never presents a
pattern name outside the reviewed public whitelist. A chart that
cannot be presented yields ``not_judgeable`` (never a renamed
pattern, never a forged positive); a determination that explicitly
refused yields ``abstained``.

Public whitelist (the eight 八格 names of the s054 procedure only):
正官格、七杀格、正财格、偏财格、正印格、偏印格、食神格、伤官格.
The D5 boundary: when the commander stem equals the day master and
the mechanical name would be 比肩格， the builder returns
``not_judgeable`` (reason ``pattern_name_not_public``) -- it does not
show "比肩格已成立" and does not auto-rename to another pattern.
劫财格 follows the same rule (it is likewise outside the 八格名目
list); the underlying research trace and Golden are unchanged. This
limit is presentation-only; the D-1 algorithm is not modified.

The builder is pure and deterministic, calls no model and no
ExplanationService, and never looks anything up statically: every
rule id, condition and evidence reference is checked mechanically
against the same request's executed records (the research gate's
envelope: trace steps, rule matches, evidence records) and the live
pilot the gate itself used. Any forged, drifted or incompletely
bound input fails closed with ``ValueError``; the scenario layer
turns that into a failed request rather than a partial presentation.
"""

from .bazi_pattern import (
    EXPOSABLE_PILLARS,
    PATTERN_VARIANT,
    REN_YIN_TRUE_VARIANT,
)
from .bazi_siling_pilot import SILING_PILOT_VARIANT
from .foundations import BRANCHES, STEMS

VARIANT = "bazi-pattern-public-presentation-v1"
TITLE = "任氏寅月局部真格研究结果"
SCOPE_STATEMENT = (
    "本呈现仅陈述任氏分支寅月局部真格研究结果：司令之神透于年/月/时干"
    "（日干不计）则真格成立，司令不透则无真格；不是全盘格局判断，"
    "不构成八格真假判断体系，不意味着喜用神或吉凶；未呈现不等于假格。")
LIMITATIONS = (
    "仅限任氏分支寅月试点；其余月份与流派暂不可判。",
    "不输出假格、破格、成败、清浊、用神或吉凶。",
    "公开呈现的格名仅限正官、七杀、正财、偏财、正印、偏印、食神、"
    "伤官八格；其余格名暂不公开呈现。",
    "司令段以已审试点为准；试点不确定时暂不可判。")

# The reviewed public whitelist: the eight 八格 names only. Any other
# mechanical name (比肩格、劫财格， or any invented name) fails closed
# to not_judgeable, never to a renamed or presented pattern.
PUBLIC_PATTERN_NAMES = frozenset((
    "正官格", "七杀格", "正财格", "偏财格",
    "正印格", "偏印格", "食神格", "伤官格"))
TEN_GODS = frozenset((
    "正官", "七杀", "正财", "偏财", "正印",
    "偏印", "食神", "伤官", "比肩", "劫财"))
DEFINITION_RULE_ID = "renshi.zhenge_definition"
DEFINITION_SECTION_ID = "bazi.section.s053"
PROCEDURE_RULE_ID = "renshi.siling_true_false_procedure"
PROCEDURE_SECTION_ID = "bazi.section.s054"
DETERMINATION_SCOPE = "ren_branch_yin_month_true_pattern_only"
SCHOOL = "任氏分支"
SCOPE_MONTH_BRANCH = "寅"
D1_STEP_ID = "bazi.phase2.ren_yin_true_pattern"
CONSUMED_STEP_IDS = (
    "bazi.phase2.pillars", "bazi.phase2.ten_gods",
    "bazi.phase2.hidden_stems", "bazi.phase2.hidden_to_visible")
# r037's source_refs are exactly the three registered quotes (s053
# 原注定义句、s054 任氏曰程序句、s024 寅月分日用事句), all from the
# one classical source below. Any other source on the bound evidence
# fails closed: the presentation must not launder an unreviewed
# citation into the public response.
PERMITTED_SOURCE_IDS = frozenset(("bazi.source.ditiansui-spouse",))
# D-1 abstention reasons the presentation may carry verbatim. Any
# other reason is a forgery and fails closed.
ABSTENTION_REASONS = frozenset((
    "month_not_yin", "luren_route_precedence",
    "pilot_result_unverifiable", "pilot_not_computed",
    "commander_not_month_hidden"))
NOT_JUDGEABLE_REASONS = frozenset((
    "month_not_yin", "birth_uncomputable", "pilot_uncertain",
    "pilot_rejected", "pilot_not_applicable",
    "pattern_name_not_public"))
_PILLAR_LABELS = {"year": "年", "month": "月", "hour": "时"}

_COMMON_KEYS = frozenset((
    "variant", "title", "status", "day_master", "month_branch",
    "scope_statement", "limitations"))
_PRESENTED_KEYS = _COMMON_KEYS | frozenset((
    "outcome", "statement", "pattern", "commander", "rule_ids",
    "source_sections", "school", "scope_month_branch",
    "evidence_ids", "source_ids"))
_NOT_JUDGEABLE_KEYS = _COMMON_KEYS | frozenset(("reason",))
_ABSTAINED_KEYS = _COMMON_KEYS | frozenset(("reason", "decision_step"))


def _fail(message):
    raise ValueError("Pattern public presentation rejected: " + message)


def _pillars_day_month(pillars):
    if not isinstance(pillars, list) or len(pillars) != 4:
        _fail("pillars must be the four chart pillars")
    day_master = None
    month_branch = None
    for index, pillar in enumerate(pillars):
        if not isinstance(pillar, dict):
            _fail("chart pillar must be a mapping")
        stem = pillar.get("stem")
        branch = pillar.get("branch")
        if isinstance(stem, dict):
            stem_value = stem.get("value")
        elif isinstance(stem, str):
            stem_value = stem
        else:
            stem_value = None
        if isinstance(branch, dict):
            branch_value = branch.get("value")
        elif isinstance(branch, str):
            branch_value = branch
        else:
            branch_value = None
        if index == 2:
            day_master = stem_value
        if index == 1:
            month_branch = branch_value
    if day_master not in STEMS:
        _fail("pillars lack a valid day master")
    if month_branch not in BRANCHES:
        _fail("pillars lack a valid month branch")
    return day_master, month_branch


def _base(day_master, month_branch, status):
    return {
        "variant": VARIANT,
        "title": TITLE,
        "status": status,
        "day_master": day_master,
        "month_branch": month_branch,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }


def _not_judgeable(day_master, month_branch, reason):
    if reason not in NOT_JUDGEABLE_REASONS:
        _fail("unknown not_judgeable reason: " + str(reason))
    result = _base(day_master, month_branch, "not_judgeable")
    result["reason"] = reason
    return result


def _steps_by_id(trace):
    if not isinstance(trace, list):
        _fail("execution trace must be a list")
    steps = {}
    for index, step in enumerate(trace):
        if not isinstance(step, dict) or not isinstance(
                step.get("rule_id"), str):
            _fail("execution trace step must carry a rule_id")
        if step["rule_id"] in steps:
            _fail("duplicate rule_id in execution trace")
        steps[step["rule_id"]] = (index, step)
    return steps


def _require_match(rule_matches, rule_id, evidence_ids):
    if not isinstance(rule_matches, list):
        _fail("execution rule_matches must be a list")
    for match in rule_matches:
        if isinstance(match, dict) and match.get("rule_id") == rule_id \
                and match.get("matched") is True \
                and match.get("evidence_ids") == evidence_ids:
            return
    _fail("no executed rule match for " + rule_id)


def _require_evidence(evidence, evidence_ids):
    """Every id must bind a record with a source. Returns source_ids.

    The permitted-source restriction is checked separately, and only
    for the D-1 step's own evidence: the consumed structural fact
    steps (pillars / ten-gods / hidden stems) bind their own
    structural sources, which are not the D-1 rule's citations.
    """
    if not isinstance(evidence, dict):
        _fail("execution evidence must be a mapping")
    source_ids = set()
    for evidence_id in evidence_ids or []:
        record = evidence.get(evidence_id)
        if not isinstance(record, dict):
            _fail("evidence id without a bound record: "
                  + str(evidence_id))
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            _fail("evidence id without a bound source record: "
                  + str(evidence_id))
        source_ids.add(source_id)
    return sorted(source_ids)


def _check_fact_refs(determination, steps):
    """The determination's fact_refs must index the executed steps.

    Mirrors the strength builder's fact_ref discipline: a ref that
    points at the wrong step (or a step that is not in the trace) is
    a forgery and fails closed.
    """
    refs = determination.get("fact_refs")
    if not isinstance(refs, dict):
        _fail("determination without fact_refs")
    expected = {}
    for step_id in CONSUMED_STEP_IDS:
        if step_id not in steps:
            _fail("missing executed step " + step_id)
        expected[step_id] = steps[step_id][0]
    pillars_index = expected["bazi.phase2.pillars"]
    hidden_index = expected["bazi.phase2.hidden_stems"]
    visible_index = expected["bazi.phase2.hidden_to_visible"]
    if refs.get("day_master") != (
            "#/trace/%d/output/day_master/stem" % pillars_index):
        _fail("determination day_master fact_ref outside the trace")
    if refs.get("month_branch") != (
            "#/trace/%d/output/ganzhi/1" % pillars_index):
        _fail("determination month_branch fact_ref outside the trace")
    hidden_output = steps["bazi.phase2.hidden_stems"][1].get("output")
    if not isinstance(hidden_output, list):
        _fail("executed hidden_stems output must be a list")
    month_rows = [i for i, row in enumerate(hidden_output)
                  if isinstance(row, dict) and row.get("pillar") == "month"]
    if len(month_rows) != 1:
        _fail("executed hidden_stems lack a single month row")
    if refs.get("month_hidden_stems") != (
            "#/trace/%d/output/%d/hidden_stems"
            % (hidden_index, month_rows[0])):
        _fail("determination month_hidden_stems fact_ref outside "
              "the trace")
    if refs.get("hidden_to_visible") != (
            "#/trace/%d/output/positions" % visible_index):
        _fail("determination hidden_to_visible fact_ref outside the trace")
    if refs.get("route") != "#/result/pattern_route":
        _fail("determination route fact_ref mismatch")


def public_pattern_presentation(record, execution, pillars):
    """Build the public pattern presentation for one gate record.

    ``record`` is a ``ren_yin_research_execution`` record (entered or
    not); ``execution`` is ``{"trace", "rule_matches", "evidence"}``
    from the record's envelope when entered, else None; ``pillars``
    is the same request's chart pillars (four pillars, stem/branch
    values). Returns the presentation dict. Raises ``ValueError`` on
    any drift, forgery or incomplete binding -- the caller must fail
    the whole request, never return a partial object.
    """
    if not isinstance(record, dict):
        _fail("gate record must be a mapping")
    if record.get("research_only") is not True \
            or record.get("public_enabled") is not False \
            or record.get("ai_enabled") is not False:
        _fail("gate record governance flags mismatch")
    day_master, month_branch = _pillars_day_month(pillars)
    if record.get("month_branch") != month_branch:
        _fail("gate record month branch drifted from the chart")

    if not record.get("entered"):
        # Non-entry: the reason is the whole content. No
        # determination exists, so no pattern fact may be shown.
        reason = record.get("reason")
        if reason == "month_not_yin":
            return _not_judgeable(day_master, month_branch,
                                  "month_not_yin")
        if reason == "birth_uncomputable":
            return _not_judgeable(day_master, month_branch,
                                  "birth_uncomputable")
        if isinstance(reason, str) and reason.startswith("pilot_"):
            pilot_reason = reason[len("pilot_"):]
            if pilot_reason in ("uncertain", "rejected",
                                "not_applicable"):
                return _not_judgeable(day_master, month_branch,
                                      "pilot_" + pilot_reason)
        _fail("unknown gate non-entry reason: " + str(reason))

    # Entered: the determination and the live pilot must be the
    # gate's own records, bound to this request's execution.
    if not isinstance(execution, dict):
        _fail("entered gate record needs its execution records")
    determination = record.get("determination")
    pilot = record.get("pilot")
    envelope = record.get("envelope")
    if not isinstance(determination, dict):
        _fail("entered gate record without a determination")
    if not isinstance(pilot, dict) or not isinstance(envelope, dict):
        _fail("entered gate record without its pilot or envelope")
    if determination.get("variant") != PATTERN_VARIANT:
        _fail("determination variant mismatch")
    if determination.get("determination_variant") != REN_YIN_TRUE_VARIANT:
        _fail("determination D-1 variant mismatch")
    if determination.get("research_only") is not True \
            or determination.get("public_enabled") is not False \
            or determination.get("ai_enabled") is not False:
        _fail("determination governance flags mismatch")
    if determination.get("evidence_binding") != "registered_phase1_phase2":
        _fail("determination evidence binding mismatch")
    if determination.get("determination_scope") != DETERMINATION_SCOPE:
        _fail("determination scope mismatch")
    if determination.get("day_stem") != day_master \
            or determination.get("month_branch") != "寅" \
            or determination.get("month_branch") != month_branch:
        _fail("determination day stem or month branch drifted")
    # The D-1 block never carries a verdict on 破格/成败/清浊/用神:
    # any such value on the block is a forgery, never presentable.
    inner = determination.get("determination")
    if not isinstance(inner, dict):
        _fail("determination without its inner verdict")
    if inner.get("success_failure") is not None \
            or inner.get("purity") is not None \
            or inner.get("useful_god") is not None:
        _fail("determination carries an unreviewed verdict field")
    # Rule identity pins: exactly the s053 definition and the s054
    # procedure, no other rule may stand behind a presented fact.
    rule = determination.get("rule")
    procedure = determination.get("procedure_rule")
    if not isinstance(rule, dict) or not isinstance(procedure, dict):
        _fail("determination without its rule pins")
    if rule.get("id") != DEFINITION_RULE_ID \
            or rule.get("source_section_id") != DEFINITION_SECTION_ID \
            or rule.get("layer") != "原注":
        _fail("determination definition rule pin mismatch")
    if procedure.get("id") != PROCEDURE_RULE_ID \
            or procedure.get("source_section_id") != PROCEDURE_SECTION_ID \
            or procedure.get("layer") != "任氏曰":
        _fail("determination procedure rule pin mismatch")
    if determination.get("consumed_rule_ids") != list(CONSUMED_STEP_IDS):
        _fail("determination consumed rule ids mismatch")
    # Live-pilot binding: the block's pilot claim must be the live
    # pilot the gate itself used (variant, status, commander), and
    # the commander must be the pilot's commander.
    block_pilot = determination.get("pilot")
    if not isinstance(block_pilot, dict):
        _fail("determination without its pilot claim")
    if block_pilot.get("variant") != SILING_PILOT_VARIANT \
            or block_pilot.get("status") != "computed" \
            or block_pilot.get("commander") != pilot.get("commander") \
            or pilot.get("variant") != SILING_PILOT_VARIANT \
            or pilot.get("status") != "computed":
        _fail("determination pilot does not match the live pilot")
    # Execution binding: the D-1 trace step must carry this exact
    # block, with bound evidence from the permitted source only, and
    # a matching RuleMatch.
    trace = execution.get("trace")
    rule_matches = execution.get("rule_matches")
    evidence = execution.get("evidence")
    steps = _steps_by_id(trace)
    if D1_STEP_ID not in steps:
        _fail("missing executed D-1 step")
    _check_fact_refs(determination, steps)
    step = steps[D1_STEP_ID][1]
    if step.get("output") != determination:
        _fail("D-1 trace step output drifted from the determination")
    step_evidence = step.get("evidence_ids")
    if not isinstance(step_evidence, list) or not step_evidence:
        _fail("D-1 step without bound evidence")
    source_ids = _require_evidence(evidence, step_evidence)
    if not set(source_ids) <= PERMITTED_SOURCE_IDS:
        _fail("D-1 evidence source outside the permitted set")
    _require_match(rule_matches, D1_STEP_ID, step_evidence)
    for step_id in CONSUMED_STEP_IDS:
        consumed = steps[step_id][1]
        if not consumed.get("evidence_ids"):
            _fail("executed step without evidence: " + step_id)
        _require_evidence(evidence, consumed["evidence_ids"])
        _require_match(rule_matches, step_id,
                       consumed["evidence_ids"])

    status = determination.get("status")
    true_false = inner.get("true_false")
    if status == "abstained":
        # An explicit refusal to present from the current input.
        # The reason is carried verbatim; nothing else is shown.
        # An abstained determination sets no commander block.
        if determination.get("commander") is not None:
            _fail("abstained determination carries a commander block")
        reason = determination.get("abstention_reason")
        decision_step = determination.get("decision_step")
        if reason not in ABSTENTION_REASONS:
            _fail("determination abstention reason outside the "
                  "reviewed set")
        if not isinstance(decision_step, int) \
                or decision_step not in (1, 2, 3, 4):
            _fail("determination abstention step mismatch")
        if true_false != "abstained" \
                or inner.get("pattern") is not None:
            _fail("abstained determination carries a pattern verdict")
        result = _base(day_master, month_branch, "abstained")
        result["reason"] = reason
        result["decision_step"] = decision_step
        return result
    if status != "determined":
        _fail("determination status outside true/commander_not_visible/"
              "abstained")

    commander = determination.get("commander")
    if not isinstance(commander, dict):
        _fail("determination without its commander block")
    if commander.get("stem") != pilot.get("commander") \
            or commander.get("stem") not in STEMS:
        _fail("determination commander stem mismatch")
    if commander.get("day_stem_counts_as_exposure") is not False:
        _fail("determination counts the day stem as exposure")
    visible = commander.get("visible_pillars")
    if not isinstance(visible, list) \
            or any(p not in EXPOSABLE_PILLARS for p in visible) \
            or len(set(visible)) != len(visible):
        _fail("determination commander visibility is not year/month/hour")

    ten_god = commander.get("ten_god")
    if ten_god not in TEN_GODS:
        _fail("determination commander ten-god is not a ten god")
    if true_false == "commander_not_visible":
        # The D1 conservative reading: the conclusion stops at
        # 司令不透、无真格. Presented, never renamed, never 假格.
        if inner.get("pattern") is not None or visible:
            _fail("commander_not_visible determination carries a "
                  "pattern or a visible pillar")
        result = _base(day_master, month_branch, "presented")
        result["outcome"] = "commander_not_visible"
        result["statement"] = "司令%s不透，无真格。" % commander["stem"]
        result["pattern"] = None
        result["commander"] = {
            "stem": commander["stem"],
            "ten_god": ten_god,
            "visible_pillars": [],
        }
        result["rule_ids"] = [DEFINITION_RULE_ID, PROCEDURE_RULE_ID]
        result["source_sections"] = [DEFINITION_SECTION_ID,
                                     PROCEDURE_SECTION_ID]
        result["school"] = SCHOOL
        result["scope_month_branch"] = SCOPE_MONTH_BRANCH
        result["evidence_ids"] = sorted(step_evidence)
        result["source_ids"] = source_ids
        return result
    if true_false != "true":
        _fail("determination true_false outside the reviewed states")
    if inner.get("pattern") != ten_god + "格":
        _fail("determination pattern is not the commander ten-god name")
    if not visible:
        _fail("true determination without a visible commander pillar")
    pattern = inner["pattern"]
    if pattern not in PUBLIC_PATTERN_NAMES:
        # D5 (and the same rule for 劫财格）: a mechanical name
        # outside the reviewed 八格 list is not publicly
        # presentable. Not judgeable, never renamed, never shown.
        return _not_judgeable(day_master, month_branch,
                              "pattern_name_not_public")
    pillars_text = "、".join(
        _PILLAR_LABELS[p] + "干" for p in visible)
    result = _base(day_master, month_branch, "presented")
    result["outcome"] = "true_pattern"
    result["statement"] = "司令%s透于%s，真格成立。" % (
        commander["stem"], pillars_text)
    result["pattern"] = pattern
    result["commander"] = {
        "stem": commander["stem"],
        "ten_god": ten_god,
        "visible_pillars": list(visible),
    }
    result["rule_ids"] = [DEFINITION_RULE_ID, PROCEDURE_RULE_ID]
    result["source_sections"] = [DEFINITION_SECTION_ID,
                                 PROCEDURE_SECTION_ID]
    result["school"] = SCHOOL
    result["scope_month_branch"] = SCOPE_MONTH_BRANCH
    result["evidence_ids"] = sorted(step_evidence)
    result["source_ids"] = source_ids
    return result


def is_valid_public_pattern_presentation(obj):
    """Closed-shape validator for the projection's scoped release.

    Mirrors the strength validator: exact top-level key set per
    status (and per outcome for presented), verbatim variant/title/
    scope/limitations, the eight-name whitelist, the reason enums,
    and the commander/rule/source consistency that can be checked
    without the execution record. Anything else is stripped by the
    projection.
    """
    if not isinstance(obj, dict):
        return False
    status = obj.get("status")
    if status == "presented":
        keys = _PRESENTED_KEYS
    elif status == "not_judgeable":
        keys = _NOT_JUDGEABLE_KEYS
    elif status == "abstained":
        keys = _ABSTAINED_KEYS
    else:
        return False
    if set(obj) != set(keys):
        return False
    if obj.get("variant") != VARIANT:
        return False
    if obj.get("title") != TITLE:
        return False
    if obj.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if obj.get("limitations") != list(LIMITATIONS):
        return False
    if obj.get("day_master") not in STEMS:
        return False
    if obj.get("month_branch") not in BRANCHES:
        return False
    if status == "presented":
        outcome = obj.get("outcome")
        commander = obj.get("commander")
        if not isinstance(commander, dict) \
                or set(commander) != {"stem", "ten_god",
                                      "visible_pillars"} \
                or commander.get("stem") not in STEMS \
                or commander.get("ten_god") not in TEN_GODS \
                or not isinstance(commander.get("visible_pillars"), list) \
                or any(p not in EXPOSABLE_PILLARS
                       for p in commander["visible_pillars"]) \
                or len(set(commander["visible_pillars"])) != len(
                    commander["visible_pillars"]):
            return False
        if outcome == "true_pattern":
            pattern = obj.get("pattern")
            if pattern not in PUBLIC_PATTERN_NAMES:
                return False
            if commander.get("ten_god") != pattern[:-1]:
                return False
            if not commander.get("visible_pillars"):
                return False
            if obj.get("statement") != (
                    "司令%s透于%s，真格成立。" % (
                        commander.get("stem"),
                        "、".join(_PILLAR_LABELS[p] + "干"
                                 for p in commander["visible_pillars"]))):
                return False
        elif outcome == "commander_not_visible":
            if obj.get("pattern") is not None:
                return False
            if commander.get("visible_pillars") != []:
                return False
            if obj.get("statement") != (
                    "司令%s不透，无真格。" % commander.get("stem")):
                return False
        else:
            return False
        if obj.get("rule_ids") != [DEFINITION_RULE_ID,
                                   PROCEDURE_RULE_ID]:
            return False
        if obj.get("source_sections") != [DEFINITION_SECTION_ID,
                                          PROCEDURE_SECTION_ID]:
            return False
        if obj.get("school") != SCHOOL:
            return False
        if obj.get("scope_month_branch") != SCOPE_MONTH_BRANCH:
            return False
        if not isinstance(obj.get("evidence_ids"), list) \
                or not obj["evidence_ids"] \
                or not all(isinstance(e, str) for e in obj["evidence_ids"]):
            return False
        if not isinstance(obj.get("source_ids"), list) \
                or not obj["source_ids"] \
                or not all(s in PERMITTED_SOURCE_IDS
                           for s in obj["source_ids"]):
            return False
    elif status == "not_judgeable":
        if obj.get("reason") not in NOT_JUDGEABLE_REASONS:
            return False
        if "pattern" in obj or "commander" in obj:
            return False
    elif status == "abstained":
        if obj.get("reason") not in ABSTENTION_REASONS:
            return False
        if obj.get("decision_step") not in (1, 2, 3, 4):
            return False
        if "pattern" in obj or "commander" in obj:
            return False
    return True
