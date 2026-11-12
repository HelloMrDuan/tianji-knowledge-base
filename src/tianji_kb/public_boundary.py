"""Shared public-boundary check (TJ-003.3): no raw internal identifiers
in any public presentation object or public envelope.

A public response may carry response-local display ordinals (``E01`` /
``R01`` -- see ``public_projection._Aliases``) and the reviewed,
bound citations of the xiyong presentation, but never a raw internal
identifier: a 24-hex / 64-hex hash (the sealed evidence records are
keyed by ``sha256(reference)[:24]``), a ``renshi.*`` variant id, or a
``bazi.source.*`` / ``bazi.section.*`` reference that is not bound to
a displayed quote.

Scope, deliberately narrow (each exception is a reviewed shape, not
an oversight):

* The four identifier list fields -- ``evidence_ids``, ``rule_ids``,
  ``source_ids``, ``source_sections`` -- may contain ONLY public
  aliases (``E\\d+`` / ``R\\d+``). Anything else there (a raw hash,
  a ``bazi.rule.*`` / ``bazi.phase2.*`` id, a ``bazi.source.*`` id)
  is a violation. This is the #560 pattern-presentation rule,
  generalized to every presentation object. An identifier list
  field that is not a list at all (a bare string, a dict, a
  number) is a violation, as is a non-string entry inside one.
  An ``E`` alias in an identifier list must resolve inside the
  current public evidence map (the envelope's top-level
  ``evidence`` map) when one is present: ``E999`` and any other
  alias with no entry in the map is a violation, not a dangling
  reference.
* A 24-hex / 64-hex token is a violation ANYWHERE in the envelope
  (a hash is a hash, whether it is the whole field value or
  embedded in free text).
* A string containing ``renshi.*`` is a violation anywhere: no
  reviewed public shape carries a Ren-variant id.
* A string containing ``bazi.source.*`` / ``bazi.section.*`` is a
  violation anywhere EXCEPT a bound citation: the field must be
  one of the approved citation fields for its subtree
  (xiyong: ``source_id`` / ``section_id`` / ``section_ids``;
  dayun: ``source_id`` / ``source_section_id``) AND the parent
  object must be a legitimate citation container that binds the
  citation to a displayed quote (or, for the two pinned dayun
  structures that carry no quote, to the method / rule it
  identifies). A citation field in a nested object that carries
  no such binding -- an unreviewed nested citation, a forged
  citation whose quote is missing or under a non-contract key,
  a citation with an empty quote -- is a violation, even inside
  an xiyong / dayun subtree. Position alone never exempts.
  The xiyong citations are bound to a displayed 120-char quote
  and validated by the xiyong builder against Phase1 refs
  (adjudicated TJ-013.3 shape); the dayun citations are bound to
  a displayed rule quote or source list and are part of the
  reviewed dayun public shape (staged opening Phase 2, TJ-017.3).
  A raw source id in a prose line, a raw hash, or a ``renshi.*``
  id anywhere still fails.
* NOT flagged (reviewed shapes, kept by design): the scalar
  ``phase1_rule_id`` / ``phase2_step_id`` registry ids on the
  strength and xiyong presentations, the xiyong
  ``consumed_rule_ids`` Phase2 step ids, the strength conflict
  ``conflict_ids`` (reviewed named-conflict ids, not knowledge-graph
  pointers), and the strength ``conditions[].fact_ref`` values
  (same-request trace pointers, ``#/trace/NN/...``, not evidence
  references). If any of those shapes is ever re-adjudicated, this
  module's allowlist must be re-adjudicated with it.

Pure stdlib, no sealed data: the check runs in public CI over
synthetic envelopes, over the shipped frontend fixtures, and (in the
sealed companion test) over a real projected envelope.
"""

import re

# A standalone 24-hex / 64-hex token (whole value or embedded in
# free text). Bounded on both sides so a longer hex string (e.g. a
# 64-hex token inside a 128-char digest) is not double-counted as
# a 24-hex hit.
RAW_HASH_TOKEN_RE = re.compile(
    r"(?<![0-9a-f])[0-9a-f]{24}(?![0-9a-f])"
    r"|(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")

_INTERNAL_ID_PREFIXES = ("renshi.", "bazi.source.", "bazi.section.")

# Identifier-carrying list fields (the #560 four, generalized).
_IDENTIFIER_LIST_FIELDS = frozenset(
    {"evidence_ids", "rule_ids", "source_ids", "source_sections"})

# Response-local display ordinals only (public_projection._Aliases).
_PUBLIC_ALIAS_RE = re.compile(r"^[ER]\d+$")

# Approved bound-citation fields, xiyong_presentation subtree only.
_XIYONG_CITATION_KEYS = frozenset(
    {"source_id", "section_id", "section_ids"})

# Approved bound-citation fields, dayun_presentation subtree only.
_DAYUN_CITATION_KEYS = frozenset(
    {"source_id", "source_section_id"})


def find_public_boundary_violations(value):
    """All raw-internal-identifier violations in ``value``.

    Returns a list of human-readable violation strings (empty means
    clean). ``value`` is a projected public envelope, a single
    presentation object, or any nested value inside one.
    """
    violations = []
    evidence_keys = _public_evidence_keys(value)
    _scan(value, "$", False, False, None, None, evidence_keys, violations)
    return violations


def scan_public_envelope(envelope):
    """Alias: the check over a whole projected public envelope."""
    return find_public_boundary_violations(envelope)


def find_raw_hash_tokens(text):
    """Standalone 24-hex / 64-hex tokens inside free text."""
    if not isinstance(text, str):
        return []
    return RAW_HASH_TOKEN_RE.findall(text)


def _public_evidence_keys(value):
    """The E-alias keys of the envelope's top-level public evidence
    map (``project_execution`` writes it as ``evidence``), or an
    empty set when no such map is present (a sub-object, or a map
    with no E-alias keys). Only E-alias keys are collected, so a
    nested ``evidence`` object of another shape (dayun, xiyong)
    contributes nothing."""
    if not isinstance(value, dict):
        return set()
    evidence = value.get("evidence")
    if not isinstance(evidence, dict):
        return set()
    return {key for key in evidence
            if isinstance(key, str) and _PUBLIC_ALIAS_RE.match(key)
            and key.startswith("E")}


def _has_bound_quote(parent):
    """True if ``parent`` binds a citation to a displayed quote.

    Either a single displayed short quote in the same object
    (xiyong evidence, dayun ``rule_quote``, dayun quotes item) or
    a non-empty list of quote objects, each carrying its own
    displayed quote (xiyong bingyao evidence, dayun sources item).
    A missing, empty, or non-string quote is no binding.
    """
    quote = parent.get("quote")
    if isinstance(quote, str) and quote.strip():
        return True
    quotes = parent.get("quotes")
    if isinstance(quotes, list) and quotes and all(
            isinstance(item, dict)
            and isinstance(item.get("quote"), str)
            and item["quote"].strip()
            for item in quotes):
        return True
    return False


def _is_bound_citation(parent, key, in_xiyong, in_dayun):
    """True only if this citation field sits in a legitimate
    citation container.

    Position alone never exempts: the field must be an approved
    citation key for its subtree AND the parent object must carry
    the binding the public contract requires -- a displayed quote
    (xiyong evidence, dayun ``rule_quote`` / quotes item, dayun
    sources item), or, for the two pinned dayun structures that
    carry no quote, the method / rule the source identifies
    (``method_options`` item: ``id`` + ``label`` + ``selectable``;
    ``evidence.rules`` item: ``phase1_rule_id`` +
    ``phase2_step_id``). A citation in a nested object with none
    of these bindings is an unreviewed / forged / missing-quote
    citation and is flagged.
    """
    if not isinstance(parent, dict):
        return False
    if in_xiyong and key not in _XIYONG_CITATION_KEYS:
        return False
    if in_dayun and key not in _DAYUN_CITATION_KEYS:
        return False
    if not (in_xiyong or in_dayun):
        return False
    if _has_bound_quote(parent):
        return True
    if (in_dayun and isinstance(parent.get("id"), str)
            and isinstance(parent.get("label"), str)
            and "selectable" in parent):
        return True
    if (in_dayun and isinstance(parent.get("phase1_rule_id"), str)
            and isinstance(parent.get("phase2_step_id"), str)):
        return True
    return False


def _check_identifier(item, key, path, evidence_keys, violations):
    """One entry of an identifier list.

    Must be a public alias string (``E\\d+`` / ``R\\d+``), and an
    ``E`` alias must resolve inside the current public evidence
    map when one is present. A non-string entry, a wrong-prefix
    alias, and an unresolvable ``E`` alias are all violations.
    """
    if not isinstance(item, str):
        violations.append(
            "identifier %r in %s is not a string at %s"
            % (item, key, path))
        return
    if not _PUBLIC_ALIAS_RE.match(item):
        violations.append(
            "unresolved identifier %r in %s at %s" % (item, key, path))
        return
    if (item.startswith("E") and evidence_keys
            and item not in evidence_keys):
        violations.append(
            "identifier %r in %s does not resolve in the public "
            "evidence map at %s" % (item, key, path))
        return


def _scan(value, path, in_xiyong, in_dayun, key, parent, evidence_keys,
          violations):
    if isinstance(value, str):
        token = RAW_HASH_TOKEN_RE.search(value)
        if token is not None:
            violations.append(
                "raw hash token %r at %s" % (token.group(0), path))
            return
        for prefix in _INTERNAL_ID_PREFIXES:
            if prefix in value:
                if prefix.startswith("bazi.") and _is_bound_citation(
                        parent, key, in_xiyong, in_dayun):
                    return
                violations.append(
                    "raw internal identifier %r at %s" % (value, path))
                return
        return
    if isinstance(value, list):
        if key in _IDENTIFIER_LIST_FIELDS:
            for index, item in enumerate(value):
                _check_identifier(
                    item, key, "%s[%d]" % (path, index), evidence_keys,
                    violations)
        else:
            for index, item in enumerate(value):
                _scan(item, "%s[%d]" % (path, index), in_xiyong, in_dayun,
                      key, parent, evidence_keys, violations)
        return
    if isinstance(value, dict):
        for child_key, item in value.items():
            if (child_key in _IDENTIFIER_LIST_FIELDS
                    and not isinstance(item, list)):
                violations.append(
                    "identifier list field %r is not a list at %s.%s"
                    % (child_key, path, child_key))
            _scan(item, "%s.%s" % (path, child_key),
                  in_xiyong or child_key == "xiyong_presentation",
                  in_dayun or child_key == "dayun_presentation",
                  child_key, value, evidence_keys, violations)
        return
