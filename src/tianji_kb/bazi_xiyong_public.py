"""TJ-013.3 staged-opening phase 1: the public 喜用 presentation builder.

Adjudicated in docs/product/TJ0133_STAGED_OPENING_PHASE1.md (E0371) under
the user's 2026-11-01 staged-opening decision. This module derives the
public presentation object (Variant ``xiyong-public-presentation-v1``)
exclusively from the two executed research statements of the same request
(调候 ``bazi-tiaohou-assessment-v1`` and 病药
``bazi-bingyao-structural-candidates-v1``) plus that request's own
execution records (trace steps, rule matches, evidence records and the
Phase1 rule references registered for the two Phase2 steps).

The builder is pure and deterministic: it calls no model and no
ExplanationService, and it never looks evidence up statically — every
``phase1_rule_id`` is derived mechanically from the request's own
evidence records (a record whose original text equals the statement
quote, whose section is registered under exactly one Phase1 rule of the
same step). Any forged, drifted or incompletely bound input fails
closed with ``ValueError``; the scenario layer turns that into a failed
request rather than a partial presentation.

Scope is exactly the two registered systems. No 扶抑， no 格局用神， no
旺衰 content is produced anywhere in the object; ``unified_verdict`` is
a constant ``None`` and cross-system relations never merge the two
systems into one verdict.
"""

import copy
import re

from .bazi_bingyao import RULES as _BINGYAO_RULES
from .bazi_bingyao import VARIANT as BINGYAO_VARIANT
from .bazi_tiaohou import VARIANT as TIAOHOU_VARIANT
from .bazi_xiyong_readable import (
    BINGYAO_HEADER,
    DISEASE_MISSING_REASONS,
    EFFICACY_LINE,
    NO_UNIFIED_VERDICT_LINE,
    PAIR_ORDINALS,
    PILLAR_LABELS,
    SUBJECT_MISSING_REASONS,
    _gods_text,
)
from .foundations import stem_element

VARIANT = "xiyong-public-presentation-v1"
PRESENTATION_SCOPE = "tiaohou_bingyao_only"
TIAOHOU_STEP_ID = "bazi.phase2.tiaohou_assessment"
BINGYAO_STEP_ID = "bazi.phase2.bingyao_assessment"
TIAOHOU_SOURCE_ID = "bazi.source.qiongtong"
BINGYAO_SOURCE_ID = "bazi.source.shenfeng"
BINGYAO_PHASE1_RULE_ID = "bazi.rule.r040"
PAIR_IDS = tuple(rule["pair_id"] for rule in _BINGYAO_RULES)

SCOPE_STATEMENT = (
    "本呈现只含调候（《穷通宝鉴》）与病药（《神峰通考》）两类已注册取用依据，"
    "逐条可回溯到注册证据与本次执行记录；两类依据并列呈现、互不合并，"
    "系统不据此给出统一的取用结论；扶抑、格局用神等其他取用判断尚未建成，"
    "不在本呈现内，暂不可判。")
LIMITATIONS = (
    "证据等级为 C 级：所据《穷通宝鉴》《神峰通考》均为单一电子谱系、简体转写，未做多底本校勘。",
    "调候条目的未编码分支与关联条目不在注册范围内，不呈现；本呈现只含条目主序列与已编码分支。",
    "病药两对均为结构候选，去病效力未裁定；某一对未触发不等于无病。",
    "本呈现为传统文化观察，不构成对现实的预测。",
)
_EFFICACY_NOT_JUDGEABLE_SUFFIX = "去病效力暂不可判。"

_FACT_REF = re.compile(r"^#/trace/(\d+)/output$")
_BLOCK_KEYS = {"tiaohou", "bingyao"}
_TOP_KEYS = {
    "variant", "presentation_scope", "day_master", "month_branch",
    "blocks", "relations", "relations_closing_line", "unified_verdict",
    "public_enabled", "ai_enabled", "scope_statement", "limitations",
}


def _fail(message):
    raise ValueError(message)


def _require(condition, message):
    if not condition:
        _fail(message)


def _statement_shell(statement, *, variant, system, label):
    _require(isinstance(statement, dict), f"{label} statement must be an object")
    _require(statement.get("variant") == variant,
             f"{label} statement variant drifted")
    _require(statement.get("system") == system,
             f"{label} statement system drifted")
    _require(statement.get("research_only") is True
             and statement.get("public_enabled") is False
             and statement.get("ai_enabled") is False,
             f"{label} statement release flags drifted")
    _require(statement.get("evidence_binding") == "registered_phase1_phase2",
             f"{label} statement lost its registered evidence binding")


def _execution_view(execution):
    _require(isinstance(execution, dict), "execution view must be an object")
    for key in ("trace", "rule_matches", "evidence", "phase1_rule_refs"):
        _require(key in execution, f"execution view is missing {key}")
    _require(isinstance(execution["trace"], list), "execution trace malformed")
    _require(isinstance(execution["rule_matches"], list),
             "execution rule matches malformed")
    _require(isinstance(execution["evidence"], dict),
             "execution evidence malformed")
    _require(isinstance(execution["phase1_rule_refs"], dict),
             "execution Phase1 rule references malformed")
    return execution


def _step(view, step_id):
    steps = [step for step in view["trace"]
             if isinstance(step, dict) and step.get("rule_id") == step_id]
    _require(len(steps) == 1, f"execution trace must carry exactly one {step_id} step")
    return steps[0]


def _step_records(view, step):
    evidence_ids = step.get("evidence_ids")
    _require(isinstance(evidence_ids, list) and evidence_ids,
             "assessment step carries no evidence binding")
    records = []
    for evidence_id in evidence_ids:
        record = view["evidence"].get(evidence_id)
        _require(isinstance(record, dict),
                 "assessment step evidence binding does not resolve")
        records.append(record)
    return records


def _check_step_execution(view, step, statement):
    _require(step.get("output") == statement,
             "assessment statement does not equal its executed step output")
    matches = [match for match in view["rule_matches"]
               if isinstance(match, dict)
               and match.get("rule_id") == step["rule_id"]]
    _require(len(matches) == 1, "assessment step rule match missing or duplicated")
    match = matches[0]
    _require(match.get("matched") is True
             and match.get("kind") == "executed_calculation",
             "assessment step did not execute")
    _require(match.get("evidence_ids") == step.get("evidence_ids"),
             "assessment step rule match evidence drifted from the trace step")
    _step_records(view, step)


def _check_fact_refs(view, statement):
    consumed = statement.get("consumed_rule_ids")
    fact_refs = statement.get("fact_refs")
    _require(isinstance(consumed, list) and consumed,
             "statement consumed_rule_ids malformed")
    _require(isinstance(fact_refs, dict) and fact_refs,
             "statement fact_refs malformed")
    shorts = {rule_id.rsplit(".", 1)[-1] for rule_id in consumed}
    _require(set(fact_refs) == shorts,
             "statement fact_refs do not cover its consumed rules")
    for key, ref in fact_refs.items():
        matched = _FACT_REF.match(ref) if isinstance(ref, str) else None
        _require(matched is not None, "statement fact_ref is malformed")
        index = int(matched.group(1))
        _require(index < len(view["trace"]), "statement fact_ref out of range")
        target = view["trace"][index]
        _require(isinstance(target, dict)
                 and target.get("rule_id") == f"bazi.phase2.{key}",
                 "statement fact_ref does not resolve to its consumed step")
        _step_records(view, target)


def _ref_pairs(view, step_id, phase1_rule_id):
    refs = view["phase1_rule_refs"].get(step_id)
    _require(isinstance(refs, dict), "Phase1 rule references for the step missing")
    pairs = refs.get(phase1_rule_id)
    _require(isinstance(pairs, list) and pairs,
             "Phase1 rule references malformed")
    normalized = []
    for pair in pairs:
        _require(isinstance(pair, (list, tuple)) and len(pair) == 2
                 and all(isinstance(part, str) for part in pair),
                 "Phase1 rule reference entry malformed")
        normalized.append((pair[0], pair[1]))
    return normalized


def _derive_phase1_owner(view, step_id, section_id, quote):
    """Name the unique Phase1 rule of ``step_id`` registering (section, quote)."""
    refs = view["phase1_rule_refs"].get(step_id)
    _require(isinstance(refs, dict), "Phase1 rule references for the step missing")
    owners = [rule_id for rule_id, pairs in refs.items()
              if isinstance(pairs, list)
              and any(isinstance(pair, (list, tuple)) and len(pair) == 2
                      and pair[0] == section_id and pair[1] == quote
                      for pair in pairs)]
    _require(len(owners) == 1,
             "quote is not registered under exactly one Phase1 rule of its step")
    return owners[0]


def _check_rule_chapter_homogeneity(view, step_id, owner, records, chapter_id):
    by_pair = {}
    for record in records:
        by_pair.setdefault(
            (record.get("section_id"), record.get("original_text")),
            record)
    for pair in _ref_pairs(view, step_id, owner):
        record = by_pair.get(pair)
        _require(record is not None,
                 "a registered reference of the derived rule is unbound in "
                 "this execution")
        _require(record.get("chapter_id") == chapter_id,
                 "derived rule spans more than one chapter in this execution")


def _find_record(records, *, source_id, section_id, quote):
    found = [record for record in records
             if record.get("source_id") == source_id
             and record.get("section_id") == section_id
             and record.get("original_text") == quote]
    _require(len(found) == 1,
             "statement quote does not resolve to exactly one evidence record")
    return found[0]


def _presence_text(item):
    presence = item["presence"]
    if presence == "visible":
        places = "、".join(PILLAR_LABELS[pillar]
                            for pillar in item["visible_positions"])
        return f"透于{places}"
    if presence == "hidden":
        pillars = []
        for position in item["hidden_positions"]:
            pillar = position.split(":", 1)[0]
            if pillar not in pillars:
                pillars.append(pillar)
        places = "、".join(PILLAR_LABELS[pillar] for pillar in pillars)
        return f"仅藏于{places}"
    _require(presence == "absent", "sequence presence drifted")
    return "盘中未见"


def _sequence_items_text(sequence):
    return "、".join(
        f"{item['stem']}（第{item['order']}取，{_presence_text(item)}）"
        for item in sequence)


def _validate_sequence(sequence, *, label):
    _require(isinstance(sequence, list) and sequence,
             f"{label} sequence malformed")
    seen = set()
    for position, item in enumerate(sequence, start=1):
        _require(isinstance(item, dict), f"{label} sequence item malformed")
        _require(item.get("order") == position,
                 f"{label} sequence order drifted")
        stem = item.get("stem")
        _require(isinstance(stem, str) and len(stem) == 1 and stem not in seen,
                 f"{label} sequence stem drifted")
        seen.add(stem)
        _require(item.get("presence") in ("visible", "hidden", "absent"),
                 f"{label} sequence presence drifted")
        visible_positions = item.get("visible_positions")
        hidden_positions = item.get("hidden_positions")
        _require(isinstance(visible_positions, list)
                 and all(pillar in PILLAR_LABELS
                         for pillar in visible_positions),
                 f"{label} sequence visible positions drifted")
        _require(isinstance(hidden_positions, list)
                 and all(isinstance(place, str)
                         and place.split(":", 1)[0] in PILLAR_LABELS
                         for place in hidden_positions),
                 f"{label} sequence hidden positions drifted")
        if item["presence"] == "visible":
            _require(visible_positions,
                     f"{label} visible sequence item has no visible position")
        elif item["presence"] == "hidden":
            _require(not visible_positions and hidden_positions,
                     f"{label} hidden sequence item positions drifted")
        else:
            _require(not visible_positions and not hidden_positions,
                     f"{label} absent sequence item carries positions")


def _tiaohou_block(statement, view, step, records):
    block = {
        "system": "tiaohou",
        "source_label": "《穷通宝鉴》",
        "day_master": statement["day_master"],
        "month_branch": statement["month_branch"],
    }
    if statement.get("status") == "not_applicable":
        _require(statement.get("reason") == "entry_absent_in_source",
                 "tiaohou not-applicable reason drifted")
        block["state"] = "not_judgeable"
        block["not_judgeable_reason"] = "entry_absent_in_source"
        block["lines"] = [
            f"调候体系（《穷通宝鉴》）：日主{statement['day_master']}、"
            f"月支{statement['month_branch']}的调候条目在审定《穷通宝鉴》文本中"
            "不存在，该组合的调候取用暂不可判；不以其他月份条目或其他典籍补齐。"]
        block["evidence"] = {
            "source_id": TIAOHOU_SOURCE_ID,
            "evidence_level": "C",
            "phase2_step_id": TIAOHOU_STEP_ID,
            "status": "not_applicable",
            "reason": "entry_absent_in_source",
        }
        return block
    _require(statement.get("status") == "matched",
             "tiaohou statement status drifted")
    _require(statement.get("source_id") == TIAOHOU_SOURCE_ID
             and statement.get("evidence_level") == "C",
             "tiaohou statement source drifted")
    entry = statement.get("entry")
    _require(isinstance(entry, dict), "tiaohou entry missing")
    quote = entry.get("quote")
    _require(isinstance(quote, str) and quote, "tiaohou entry quote missing")
    candidates = [record for record in records
                  if record.get("source_id") == TIAOHOU_SOURCE_ID
                  and record.get("original_text") == quote]
    _require(len(candidates) == 1,
             "tiaohou entry quote does not resolve to exactly one record")
    record = candidates[0]
    section_id = record.get("section_id")
    _require(isinstance(section_id, str) and section_id,
             "tiaohou entry record carries no section")
    _require(record.get("rule_id") == TIAOHOU_STEP_ID,
             "tiaohou entry record is not bound by the tiaohou step")
    locator = entry.get("quote_locator")
    span = entry.get("section")
    _require(isinstance(locator, dict) and isinstance(span, dict),
             "tiaohou entry locator malformed")
    _require(span.get("line") == locator.get("line")
             and span.get("char_start") <= locator.get("char_start")
             and locator.get("char_end") <= span.get("char_end")
             and locator.get("char_end") - locator.get("char_start") == len(quote),
             "tiaohou entry quote locator drifted from its section span")
    chapter_id = record.get("chapter_id")
    _require(isinstance(chapter_id, str)
             and record.get("chapter_title", "").startswith(
                 statement["day_master"]),
             "tiaohou entry record chapter drifted from the day master")
    owner = _derive_phase1_owner(view, TIAOHOU_STEP_ID, section_id, quote)
    _check_rule_chapter_homogeneity(
        view, TIAOHOU_STEP_ID, owner, records, chapter_id)
    block["state"] = "presented"
    block["month_label"] = statement["month_label"]
    sequence = copy.deepcopy(statement.get("sequence"))
    _validate_sequence(sequence, label="tiaohou entry")
    block["sequence"] = sequence
    label = (f"{statement['day_master']}"
             f"{stem_element(statement['day_master'])}")
    lines = [
        f"调候体系（《穷通宝鉴》{label}{statement['month_label']}条）："
        f"原文取用顺序为：{_sequence_items_text(sequence)}。"]
    presence_by_stem = {item["stem"]: item["presence"] for item in sequence}
    branches = []
    raw_branches = statement.get("branches")
    _require(isinstance(raw_branches, list), "tiaohou branches malformed")
    for branch in raw_branches:
        _require(isinstance(branch, dict), "tiaohou branch malformed")
        branch_quote = branch.get("quote")
        _require(isinstance(branch_quote, str) and branch_quote,
                 "tiaohou branch quote missing")
        owned = [candidate for candidate in records
                 if candidate.get("source_id") == TIAOHOU_SOURCE_ID
                 and candidate.get("original_text") == branch_quote
                 and _derive_phase1_owner(
                     view, TIAOHOU_STEP_ID,
                     candidate.get("section_id"), branch_quote) == owner]
        _require(len(owned) == 1,
                 "tiaohou branch quote is not bound under the entry rule")
        branch_record = owned[0]
        _require(branch_record.get("rule_id") == TIAOHOU_STEP_ID,
                 "tiaohou branch record is not bound by the tiaohou step")
        condition = branch.get("condition")
        _require(isinstance(condition, dict)
                 and set(condition) == {"absent_stem"}
                 and isinstance(condition.get("absent_stem"), str)
                 and len(condition["absent_stem"]) == 1,
                 "tiaohou branch condition drifted from the encoded form")
        absent_stem = condition["absent_stem"]
        applied = branch.get("applied")
        _require(isinstance(applied, bool), "tiaohou branch applied flag drifted")
        branch_sequence = copy.deepcopy(branch.get("sequence"))
        _validate_sequence(branch_sequence, label="tiaohou branch")
        for item in branch_sequence:
            prior = presence_by_stem.setdefault(item["stem"], item["presence"])
            _require(prior == item["presence"],
                     "tiaohou branch sequence presence contradicts the entry")
        if absent_stem in presence_by_stem:
            _require(applied == (presence_by_stem[absent_stem] == "absent"),
                     "tiaohou branch applied flag contradicts the chart facts")
        branch_sequence_text = _sequence_items_text(branch_sequence)
        if applied:
            condition_fact = f"{absent_stem}未见于本盘"
            lines.append(
                f"条目分支（条件成立）：{absent_stem}未见于本盘，原文在此情形下"
                f"改以下列取用顺序为准：{branch_sequence_text}。")
        else:
            condition_fact = f"{absent_stem}见于本盘"
            lines.append(
                f"条目分支（条件不成立）：{absent_stem}见于本盘，仍以主序列为准；"
                f"分支取用顺序为：{branch_sequence_text}。")
        branches.append({
            "id": branch["id"],
            "applied": applied,
            "condition": {"absent_stem": absent_stem},
            "condition_fact": condition_fact,
            "quote": branch_quote,
            "sequence": branch_sequence,
        })
    block["branches"] = branches
    block["entry_basis"] = entry.get("order_basis")
    _require(isinstance(block["entry_basis"], str) and block["entry_basis"],
             "tiaohou entry order basis missing")
    lines.append(f"取用顺序的原文依据：{block['entry_basis']}")
    block["lines"] = lines
    block["evidence"] = {
        "source_id": TIAOHOU_SOURCE_ID,
        "evidence_level": "C",
        "phase1_rule_id": owner,
        "phase2_step_id": TIAOHOU_STEP_ID,
        "section_id": section_id,
        "quote": quote,
        "quote_locator": copy.deepcopy(locator),
        "consumed_rule_ids": copy.deepcopy(statement["consumed_rule_ids"]),
        "fact_refs": copy.deepcopy(statement["fact_refs"]),
    }
    return block


def _bingyao_pairs(statement):
    pairs = statement.get("pairs")
    _require(isinstance(pairs, list) and len(pairs) == len(PAIR_IDS),
             "bingyao statement pairs malformed")
    by_id = {}
    for pair in pairs:
        _require(isinstance(pair, dict), "bingyao pair malformed")
        _require(pair.get("pair_id") in PAIR_IDS
                 and pair["pair_id"] not in by_id,
                 "bingyao pair identity drifted")
        by_id[pair["pair_id"]] = pair
    _require([pair["pair_id"] for pair in pairs] == list(PAIR_IDS),
             "bingyao pairs out of registered order")
    first = pairs[0]
    for field in ("subject", "status", "disease_candidate",
                  "medicine_candidate", "medicine_status"):
        _require(statement.get(field) == first.get(field),
                 "bingyao top-level fields drifted from the first pair")
    _require(statement.get("determination") is None
             and statement.get("medicine_effect_status") == "unadjudicated",
             "bingyao statement carries an adjudicated determination")
    return pairs


def _gods_of(block, *, label):
    _require(isinstance(block, dict), f"bingyao {label} block missing")
    gods = block.get("gods")
    _require(isinstance(gods, list), f"bingyao {label} gods malformed")
    for god in gods:
        _require(isinstance(god, dict)
                 and god.get("pillar") in PILLAR_LABELS
                 and isinstance(god.get("stem"), str)
                 and len(god["stem"]) == 1
                 and isinstance(god.get("ten_god"), str),
                 f"bingyao {label} god row malformed")
    return gods


def _bingyao_block(statement, view, step, records):
    _require(statement.get("source_id") == BINGYAO_SOURCE_ID
             and statement.get("evidence_level") == "C",
             "bingyao statement source drifted")
    pairs = _bingyao_pairs(statement)
    lines = [BINGYAO_HEADER]
    out_pairs = []
    quotes = []
    section_ids = set()
    owner = None
    for index, pair in enumerate(pairs):
        ordinal = PAIR_ORDINALS[index]
        rule = pair.get("rule")
        _require(isinstance(rule, dict), "bingyao pair rule missing")
        registered = _BINGYAO_RULES[index]
        for field in ("subject_god_class", "disease_god_class",
                      "medicine_god_class", "quote"):
            _require(rule.get(field) == registered[field],
                     "bingyao pair rule drifted from the registered rule")
        quote = rule["quote"]
        record = _find_record(records, source_id=BINGYAO_SOURCE_ID,
                              section_id=_section_of_quote(records, quote),
                              quote=quote)
        _require(record.get("rule_id") == BINGYAO_STEP_ID,
                 "bingyao pair record is not bound by the bingyao step")
        pair_owner = _derive_phase1_owner(
            view, BINGYAO_STEP_ID, record["section_id"], quote)
        if owner is None:
            owner = pair_owner
            _check_rule_chapter_homogeneity(
                view, BINGYAO_STEP_ID, owner, records,
                record.get("chapter_id"))
        _require(pair_owner == owner,
                 "bingyao pairs derive to different Phase1 rules")
        section_ids.add(record["section_id"])
        quotes.append({
            "pair_id": pair["pair_id"],
            "quote": quote,
            "quote_locator": copy.deepcopy(rule["quote_locator"]),
            "section_id": record["section_id"],
        })
        subject_class = rule["subject_god_class"]
        disease_class = rule["disease_god_class"]
        medicine_class = rule["medicine_god_class"]
        head = (f"{ordinal}（所论之神{subject_class}、病为{disease_class}、"
                f"药为{medicine_class}）")
        out_pair = {
            "pair_id": pair["pair_id"],
            "rule": {
                "subject_god_class": subject_class,
                "disease_god_class": disease_class,
                "medicine_god_class": medicine_class,
                "quote": quote,
                "quote_locator": copy.deepcopy(rule["quote_locator"]),
                "section_id": record["section_id"],
            },
            "status": pair.get("status"),
            "subject": copy.deepcopy(pair.get("subject")),
            "determination": None,
            "medicine_effect_status": "unadjudicated",
            "efficacy_state": "not_judgeable",
        }
        subject_gods = _gods_of(pair.get("subject"), label="subject")
        if pair.get("status") == "not_triggered":
            reason = pair.get("not_triggered_reason")
            out_pair["not_triggered_reason"] = reason
            if reason in SUBJECT_MISSING_REASONS:
                _require(not subject_gods,
                         "bingyao subject-missing pair carries subject gods")
                lines.append(
                    f"{head}：所论之神{subject_class}在本盘显干中未见，"
                    "该对未触发；未触发不等于无病。")
            elif reason in DISEASE_MISSING_REASONS:
                _require(subject_gods,
                         "bingyao disease-missing pair carries no subject gods")
                lines.append(
                    f"{head}：所论之神{subject_class}见于"
                    f"{_gods_text(subject_gods)}，但病之{disease_class}"
                    "在本盘显干中未见，该对未触发；未触发不等于无病。")
            else:
                _fail("bingyao pair not-triggered reason drifted")
        elif pair.get("status") == "triggered":
            disease = pair.get("disease_candidate")
            medicine = pair.get("medicine_candidate")
            disease_gods = _gods_of(disease, label="disease")
            _require(subject_gods and disease_gods,
                     "triggered bingyao pair is missing its god facts")
            out_pair["disease_candidate"] = copy.deepcopy(disease)
            out_pair["medicine_candidate"] = copy.deepcopy(medicine)
            out_pair["medicine_status"] = pair.get("medicine_status")
            text = (f"{head}：所论之神{subject_class}见于"
                    f"{_gods_text(subject_gods)}；病之{disease_class}见于"
                    f"{_gods_text(disease_gods)}；")
            if medicine is None:
                _require(pair.get("medicine_status") == "absent",
                         "bingyao medicine status contradicts its god facts")
                text += f"药之{medicine_class}在本盘显干中未见。"
            else:
                medicine_gods = _gods_of(medicine, label="medicine")
                _require(medicine_gods
                         and pair.get("medicine_status")
                         == "candidate_present",
                         "bingyao medicine status contradicts its god facts")
                text += (f"药之{medicine_class}见于"
                         f"{_gods_text(medicine_gods)}。")
            lines.append(text)
            lines.append(
                f"{ordinal}{EFFICACY_LINE}{_EFFICACY_NOT_JUDGEABLE_SUFFIX}")
        else:
            _fail("bingyao pair status drifted")
        out_pairs.append(out_pair)
    _require(owner == BINGYAO_PHASE1_RULE_ID,
             "bingyao evidence does not derive to the registered Phase1 rule")
    return {
        "system": "bingyao",
        "source_label": "《神峰通考》",
        "day_master": statement["day_master"],
        "pairs": out_pairs,
        "lines": lines,
        "evidence": {
            "source_id": BINGYAO_SOURCE_ID,
            "evidence_level": "C",
            "phase1_rule_id": owner,
            "phase2_step_id": BINGYAO_STEP_ID,
            "section_ids": sorted(section_ids),
            "quotes": quotes,
            "consumed_rule_ids": copy.deepcopy(statement["consumed_rule_ids"]),
            "fact_refs": copy.deepcopy(statement["fact_refs"]),
        },
    }


def _section_of_quote(records, quote):
    found = {record.get("section_id") for record in records
             if record.get("original_text") == quote}
    _require(len(found) == 1, "bingyao pair quote section is ambiguous")
    return found.pop()


def _relations(tiaohou_block, bingyao_block):
    if tiaohou_block.get("state") != "presented":
        return []
    tiaohou_side = {
        item["stem"]: {"role": "primary_pick", "order": item["order"]}
        for item in tiaohou_block["sequence"]}
    bingyao_side = {}
    for pair in bingyao_block["pairs"]:
        if pair["status"] != "triggered":
            continue
        named = (("subject", pair.get("subject")),
                 ("disease", pair.get("disease_candidate")),
                 ("medicine", pair.get("medicine_candidate")))
        for role, candidate in named:
            for god in (candidate or {}).get("gods") or []:
                stem = god["stem"]
                entry = {"role": role, "pair_id": pair["pair_id"]}
                if stem in bingyao_side and bingyao_side[stem] != entry:
                    _fail("one stem is named twice by the bingyao pairs")
                bingyao_side[stem] = entry
    relations = []
    for stem in sorted(set(tiaohou_side) | set(bingyao_side)):
        item = {"stem": stem}
        if stem in tiaohou_side:
            item["tiaohou"] = tiaohou_side[stem]
        if stem in bingyao_side:
            item["bingyao"] = bingyao_side[stem]
        if stem in tiaohou_side and stem in bingyao_side:
            role = bingyao_side[stem]["role"]
            if role == "medicine":
                item["kind"] = "support"
            elif role == "subject":
                item["kind"] = "pivot_overlap"
            else:
                item["kind"] = "conflict"
                item["judgeable"] = False
                item["not_judgeable_line"] = (
                    f"干{stem}的综合取用暂不可判：调候取用点名此干，"
                    "病药以此干所属神类为病，方向相反；两体系事实只并列"
                    "呈现，不作统一裁定。")
        else:
            item["kind"] = "one_sided"
        relations.append(item)
    return relations


def public_xiyong_presentation(tiaohou, bingyao, *, execution):
    """Build the phase-1 public presentation from one request's execution.

    ``tiaohou``/``bingyao`` are the two executed research statements;
    ``execution`` is the same request's view {trace, rule_matches,
    evidence, phase1_rule_refs}. Any drift fails closed (ValueError).
    """
    view = _execution_view(execution)
    _statement_shell(tiaohou, variant=TIAOHOU_VARIANT, system="tiaohou",
                     label="tiaohou")
    _statement_shell(bingyao, variant=BINGYAO_VARIANT, system="bingyao",
                     label="bingyao")
    _require(tiaohou.get("day_master") == bingyao.get("day_master"),
             "the two statements disagree on the day master")
    tiaohou_step = _step(view, TIAOHOU_STEP_ID)
    bingyao_step = _step(view, BINGYAO_STEP_ID)
    _check_step_execution(view, tiaohou_step, tiaohou)
    _check_step_execution(view, bingyao_step, bingyao)
    _check_fact_refs(view, tiaohou)
    _check_fact_refs(view, bingyao)
    tiaohou_records = _step_records(view, tiaohou_step)
    bingyao_records = _step_records(view, bingyao_step)
    tiaohou_block = _tiaohou_block(tiaohou, view, tiaohou_step, tiaohou_records)
    bingyao_block = _bingyao_block(bingyao, view, bingyao_step, bingyao_records)
    return {
        "variant": VARIANT,
        "presentation_scope": PRESENTATION_SCOPE,
        "day_master": tiaohou["day_master"],
        "month_branch": tiaohou["month_branch"],
        "blocks": {"tiaohou": tiaohou_block, "bingyao": bingyao_block},
        "relations": _relations(tiaohou_block, bingyao_block),
        "relations_closing_line": NO_UNIFIED_VERDICT_LINE,
        "unified_verdict": None,
        "public_enabled": True,
        "ai_enabled": False,
        "scope_statement": SCOPE_STATEMENT,
        "limitations": list(LIMITATIONS),
    }


def is_valid_public_presentation(candidate):
    """Structural check used by the public projection's scoped release.

    Only an object with exactly the adjudicated top-level shape, the two
    registered blocks and the constant verdict/flag values may pass the
    projection under the ``xiyong_presentation`` key; anything else is
    stripped like every other research object.
    """
    if not isinstance(candidate, dict) or set(candidate) != _TOP_KEYS:
        return False
    if candidate.get("variant") != VARIANT:
        return False
    if candidate.get("presentation_scope") != PRESENTATION_SCOPE:
        return False
    if candidate.get("unified_verdict") is not None:
        return False
    if candidate.get("public_enabled") is not True:
        return False
    if candidate.get("ai_enabled") is not False:
        return False
    if candidate.get("scope_statement") != SCOPE_STATEMENT:
        return False
    if candidate.get("limitations") != list(LIMITATIONS):
        return False
    if candidate.get("relations_closing_line") != NO_UNIFIED_VERDICT_LINE:
        return False
    blocks = candidate.get("blocks")
    if not isinstance(blocks, dict) or set(blocks) != _BLOCK_KEYS:
        return False
    tiaohou = blocks["tiaohou"]
    bingyao = blocks["bingyao"]
    if not isinstance(tiaohou, dict) or not isinstance(bingyao, dict):
        return False
    if tiaohou.get("system") != "tiaohou" or bingyao.get("system") != "bingyao":
        return False
    if tiaohou.get("source_label") != "《穷通宝鉴》":
        return False
    if bingyao.get("source_label") != "《神峰通考》":
        return False
    if tiaohou.get("state") not in ("presented", "not_judgeable"):
        return False
    if not isinstance(tiaohou.get("lines"), list) or not tiaohou["lines"]:
        return False
    if not isinstance(bingyao.get("lines"), list) or not bingyao["lines"]:
        return False
    if not isinstance(tiaohou.get("evidence"), dict):
        return False
    if not isinstance(bingyao.get("evidence"), dict):
        return False
    if tiaohou["evidence"].get("source_id") != TIAOHOU_SOURCE_ID:
        return False
    if bingyao["evidence"].get("source_id") != BINGYAO_SOURCE_ID:
        return False
    pairs = bingyao.get("pairs")
    if not isinstance(pairs, list) or len(pairs) != len(PAIR_IDS):
        return False
    for pair in pairs:
        if not isinstance(pair, dict):
            return False
        if pair.get("determination") is not None:
            return False
        if pair.get("medicine_effect_status") != "unadjudicated":
            return False
        if pair.get("efficacy_state") != "not_judgeable":
            return False
    relations = candidate.get("relations")
    if not isinstance(relations, list):
        return False
    for item in relations:
        if not isinstance(item, dict) or "stem" not in item:
            return False
        if item.get("kind") not in ("support", "conflict", "pivot_overlap",
                                    "one_sided"):
            return False
        if item.get("kind") == "conflict" and item.get("judgeable") is not False:
            return False
    return True
