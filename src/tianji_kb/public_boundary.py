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
  violation anywhere EXCEPT a bound citation at a reviewed path:
  the field must be one of the approved citation fields for its
  subtree (xiyong: ``source_id`` / ``section_id`` / ``section_ids``;
  dayun: ``source_id`` / ``source_section_id``), the value's path
  must be one of the reviewed citation paths (xiyong
  ``blocks.*.evidence`` and its ``quotes[*]`` items; dayun
  ``methods.*.direction.rule_quote``,
  ``methods.*.sources[*]`` and its ``quotes[*]`` items,
  ``method_options[*]``, ``evidence.rules[*]``), AND the parent
  object must carry the binding that path requires (a displayed
  quote or quotes list, or the method / rule the source
  identifies). A citation in an unreviewed subtree -- even one
  that carries a forged quote or a forged method-option shape --
  is a violation, because no nested object can buy an exemption
  by merely adding a quote. The xiyong citations are bound to a
  displayed 120-char quote and validated by the xiyong builder
  against Phase1 refs (adjudicated TJ-013.3 shape); the dayun
  citations are bound to a displayed rule quote or source list
  and are part of the reviewed dayun public shape (staged
  opening Phase 2, TJ-017.3). A raw source id in a prose line,
  a raw hash, or a ``renshi.*`` id anywhere still fails.
* An ``E`` alias in an identifier list must resolve inside the
  current public evidence map (the envelope's top-level
  ``evidence`` map) when one is present -- including an
  explicitly empty map, which resolves nothing: ``E999`` and any
  other alias with no entry in the map is a violation, not a
  dangling reference. Only a scan with no evidence context at
  all (a single presentation, no ``evidence`` key) skips the
  resolvability check and verifies format only.
* JSON key names are scanned like values: a dict key carrying a
  raw 24/64-hex token or a ``renshi.*`` / ``bazi.source.*`` /
  ``bazi.section.*`` reference is a violation. ``rule_matches``.
  ``rule_id`` must be a public R alias (``R\\d+``): a regression
  to a raw ``bazi.phase2.*`` / ``bazi.rule.*`` id is a violation.
  Reviewed scalar registry ids (strength / xiyong
  ``phase1_rule_id`` / ``phase2_step_id``) are different keys and
  are untouched by that check.
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

# Public R alias for rule_matches[].rule_id (public_projection._Aliases).
_R_ALIAS_RE = re.compile(r"^R\d+$")

# Reviewed citation paths, as the suffix of the value's path after the
# presentation key (``xiyong_presentation`` / ``dayun_presentation``).
# A citation is exempt ONLY at one of these reviewed paths, and only
# when its parent carries the binding for that path's kind. Any other
# path -- an unreviewed subtree that happens to carry a quote, a
# forged method option, a stray citation field -- is flagged, even
# when the parent looks like a citation container. Binding kinds:
# "quote" (parent must carry a displayed quote or quotes list),
# "method_option" (parent must be a method_options item),
# "rule" (parent must be an evidence.rules item).
_REVIEWED_CITATION_SUFFIXES = (
    # xiyong evidence object (tiaohou: quote; bingyao: quotes list).
    (re.compile(
        r"^\.blocks\.[^.]+\.evidence\.(source_id|section_id)$"),
     "quote"),
    (re.compile(
        r"^\.blocks\.[^.]+\.evidence\.section_ids\[\d+\]$"),
     "quote"),
    # xiyong quotes item inside bingyao evidence.
    (re.compile(
        r"^\.blocks\.[^.]+\.evidence\.quotes\[\d+\]\."
        r"(source_id|section_id|source_section_id)$"),
     "quote"),
    # xiyong bingyao pair rule (carries a displayed quote).
    (re.compile(
        r"^\.blocks\.[^.]+\.pairs\[\d+\]\.rule\."
        r"(source_id|section_id|source_section_id)$"),
     "quote"),
    # dayun rule_quote.
    (re.compile(
        r"^\.methods\.[^.]+\.direction\.rule_quote\."
        r"(source_id|source_section_id)$"),
     "quote"),
    # dayun sources item.
    (re.compile(
        r"^\.methods\.[^.]+\.sources\[\d+\]\.source_id$"),
     "quote"),
    # dayun quotes item.
    (re.compile(
        r"^\.methods\.[^.]+\.sources\[\d+\]\.quotes\[\d+\]\."
        r"(source_id|source_section_id)$"),
     "quote"),
    # dayun method_options item.
    (re.compile(r"^\.method_options\[\d+\]\.source_id$"),
     "method_option"),
    # dayun evidence.rules item.
    (re.compile(r"^\.evidence\.rules\[\d+\]\.source_id$"),
     "rule"),
)


def find_public_boundary_violations(value):
    """All raw-internal-identifier violations in ``value``.

    Returns a list of human-readable violation strings (empty means
    clean). ``value`` is a projected public envelope, a single
    presentation object, or any nested value inside one.
    """
    violations = []
    evidence_keys, has_evidence_map = _public_evidence_map(value)
    _scan(value, "$", False, False, None, None, evidence_keys,
          has_evidence_map, violations)
    return violations


def scan_public_envelope(envelope):
    """Alias: the check over a whole projected public envelope."""
    return find_public_boundary_violations(envelope)


def find_raw_hash_tokens(text):
    """Standalone 24-hex / 64-hex tokens inside free text."""
    if not isinstance(text, str):
        return []
    return RAW_HASH_TOKEN_RE.findall(text)


def _public_evidence_map(value):
    """The envelope's top-level public evidence map.

    Returns ``(evidence_keys, has_map)``. ``evidence_keys`` is the
    set of E-alias keys in the map. ``has_map`` is True when the
    value explicitly carries a public evidence map -- an ``evidence``
    dict that is empty or keyed by E-aliases. A non-empty
    ``evidence`` object with no E-alias keys (a dayun / xiyong
    evidence object, not the public map) is not a map at all, and
    a value with no ``evidence`` key has no evidence context.

    The distinction matters: a whole envelope that explicitly
    declares an empty evidence map (``"evidence": {}``) must reject
    every unresolvable E reference, while a single presentation
    scanned with no evidence context at all cannot resolve
    references and is checked for format only.
    """
    if not isinstance(value, dict):
        return set(), False
    evidence = value.get("evidence")
    if not isinstance(evidence, dict):
        return set(), False
    keys = {key for key in evidence
            if isinstance(key, str) and _PUBLIC_ALIAS_RE.match(key)
            and key.startswith("E")}
    if evidence and not keys:
        return set(), False
    return keys, True


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


def _citation_binding_kind(path, in_xiyong, in_dayun):
    """The binding kind of a citation at ``path``, or None.

    The path must be at one of the reviewed citation paths
    (``_REVIEWED_CITATION_SUFFIXES``), taken as the suffix after
    the presentation key. Any other path -- an unreviewed subtree
    that happens to carry a quote, a forged method option, a stray
    citation field -- has no reviewed binding, however
    citation-like its parent looks.
    """
    if in_xiyong:
        marker = ".xiyong_presentation"
    elif in_dayun:
        marker = ".dayun_presentation"
    else:
        return None
    idx = path.rfind(marker)
    if idx < 0:
        return None
    suffix = path[idx + len(marker):]
    for pattern, kind in _REVIEWED_CITATION_SUFFIXES:
        if pattern.match(suffix):
            return kind
    return None


def _is_bound_citation(parent, key, path, in_xiyong, in_dayun):
    """True only if this citation field sits at a reviewed path
    AND its parent carries the binding that path requires.

    Path-locked: the field must be an approved citation key for
    its subtree AND the value's path must be one of the reviewed
    citation paths. Binding-verified: for a quote path the parent
    must carry a displayed quote or quotes list; for a
    method_options path the parent must be a method item
    (``id`` + ``label`` + ``selectable``); for an evidence.rules
    path the parent must be a rule item (``phase1_rule_id`` +
    ``phase2_step_id``). A citation at an unreviewed path, or at
    a reviewed path without its binding, is flagged -- no nested
    object can buy an exemption by merely adding a quote.
    """
    if not isinstance(parent, dict):
        return False
    if in_xiyong and key not in _XIYONG_CITATION_KEYS:
        return False
    if in_dayun and key not in _DAYUN_CITATION_KEYS:
        return False
    if not (in_xiyong or in_dayun):
        return False
    kind = _citation_binding_kind(path, in_xiyong, in_dayun)
    if kind is None:
        return False
    if kind == "quote":
        return _has_bound_quote(parent)
    if kind == "method_option":
        return (isinstance(parent.get("id"), str)
                and isinstance(parent.get("label"), str)
                and "selectable" in parent)
    if kind == "rule":
        return (isinstance(parent.get("phase1_rule_id"), str)
                and isinstance(parent.get("phase2_step_id"), str))
    return False


def _check_identifier(item, key, path, evidence_keys, has_evidence_map,
                      violations):
    """One entry of an identifier list.

    Must be a public alias string (``E\\d+`` / ``R\\d+``), and an
    ``E`` alias must resolve inside the current public evidence
    map when one is present -- including an explicitly empty map,
    which resolves nothing. A non-string entry, a wrong-prefix
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
    if (item.startswith("E") and has_evidence_map
            and item not in evidence_keys):
        violations.append(
            "identifier %r in %s does not resolve in the public "
            "evidence map at %s" % (item, key, path))
        return


def _check_key_name(key, path, violations):
    """A JSON key name must not carry a banned stable identifier.

    Keys are scanned like values: a raw 24/64-hex token or a
    ``renshi.*`` / ``bazi.source.*`` / ``bazi.section.*`` reference
    hiding in a key name is a violation. Reviewed field names
    (``phase1_rule_id``, ``source_id``, ``evidence_ids`` ...) carry
    no banned prefix and are unaffected.
    """
    if not isinstance(key, str):
        return
    token = RAW_HASH_TOKEN_RE.search(key)
    if token is not None:
        violations.append(
            "raw hash token %r in key at %s" % (token.group(0), path))
        return
    for prefix in _INTERNAL_ID_PREFIXES:
        if prefix in key:
            violations.append(
                "raw internal identifier %r in key at %s" % (key, path))
            return


def _scan(value, path, in_xiyong, in_dayun, key, parent, evidence_keys,
          has_evidence_map, violations):
    if isinstance(value, str):
        # rule_matches[].rule_id must be a public R alias: a
        # regression to a raw bazi.phase2.* / bazi.rule.* id is a
        # leak. Reviewed scalar registry ids (strength / xiyong
        # phase1_rule_id, phase2_step_id) are different keys and
        # are untouched by this check.
        if key == "rule_id" and ".rule_matches[" in path:
            if not _R_ALIAS_RE.match(value):
                violations.append(
                    "rule_matches rule_id %r is not a public R alias "
                    "at %s" % (value, path))
                return
        token = RAW_HASH_TOKEN_RE.search(value)
        if token is not None:
            violations.append(
                "raw hash token %r at %s" % (token.group(0), path))
            return
        for prefix in _INTERNAL_ID_PREFIXES:
            if prefix in value:
                if prefix.startswith("bazi.") and _is_bound_citation(
                        parent, key, path, in_xiyong, in_dayun):
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
                    has_evidence_map, violations)
        else:
            for index, item in enumerate(value):
                _scan(item, "%s[%d]" % (path, index), in_xiyong, in_dayun,
                      key, parent, evidence_keys, has_evidence_map,
                      violations)
        return
    if isinstance(value, dict):
        for child_key, item in value.items():
            _check_key_name(child_key, "%s.%s" % (path, child_key),
                            violations)
            if (child_key in _IDENTIFIER_LIST_FIELDS
                    and not isinstance(item, list)):
                violations.append(
                    "identifier list field %r is not a list at %s.%s"
                    % (child_key, path, child_key))
            _scan(item, "%s.%s" % (path, child_key),
                  in_xiyong or child_key == "xiyong_presentation",
                  in_dayun or child_key == "dayun_presentation",
                  child_key, value, evidence_keys, has_evidence_map,
                  violations)
        return
