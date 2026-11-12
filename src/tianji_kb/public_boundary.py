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
  generalized to every presentation object.
* A 24-hex / 64-hex token is a violation ANYWHERE in the envelope
  (a hash is a hash, whether it is the whole field value or
  embedded in free text).
* A string containing ``renshi.*`` is a violation anywhere: no
  reviewed public shape carries a Ren-variant id.
* A string containing ``bazi.source.*`` / ``bazi.section.*`` is a
  violation anywhere EXCEPT the xiyong presentation's
  bound-citation fields
  (``source_id`` / ``section_id`` / ``section_ids`` inside an
  ``xiyong_presentation`` subtree): each such citation is bound to
  a displayed 120-char quote and validated by the xiyong builder
  against Phase1 refs (adjudicated TJ-013.3 shape). The exemption
  is field-scoped, not subtree-scoped -- prose lines inside the
  xiyong presentation still fail on a raw source id.
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


def find_public_boundary_violations(value):
    """All raw-internal-identifier violations in ``value``.

    Returns a list of human-readable violation strings (empty means
    clean). ``value`` is a projected public envelope, a single
    presentation object, or any nested value inside one.
    """
    violations = []
    _scan(value, "$", False, None, violations)
    return violations


def scan_public_envelope(envelope):
    """Alias: the check over a whole projected public envelope."""
    return find_public_boundary_violations(envelope)


def find_raw_hash_tokens(text):
    """Standalone 24-hex / 64-hex tokens inside free text."""
    if not isinstance(text, str):
        return []
    return RAW_HASH_TOKEN_RE.findall(text)


def _scan(value, path, in_xiyong, key, violations):
    if isinstance(value, str):
        token = RAW_HASH_TOKEN_RE.search(value)
        if token is not None:
            violations.append(
                "raw hash token %r at %s" % (token.group(0), path))
            return
        for prefix in _INTERNAL_ID_PREFIXES:
            if prefix in value:
                if prefix.startswith("bazi.") and in_xiyong \
                        and key in _XIYONG_CITATION_KEYS:
                    return
                violations.append(
                    "raw internal identifier %r at %s" % (value, path))
                return
        return
    if isinstance(value, list):
        if key in _IDENTIFIER_LIST_FIELDS:
            for index, item in enumerate(value):
                item_path = "%s[%d]" % (path, index)
                if isinstance(item, str) \
                        and not _PUBLIC_ALIAS_RE.match(item):
                    violations.append(
                        "unresolved identifier %r in %s at %s"
                        % (item, key, item_path))
                else:
                    _scan(item, item_path, in_xiyong, key, violations)
        else:
            for index, item in enumerate(value):
                _scan(item, "%s[%d]" % (path, index), in_xiyong, key,
                      violations)
        return
    if isinstance(value, dict):
        for child_key, item in value.items():
            _scan(item, "%s.%s" % (path, child_key),
                  in_xiyong or child_key == "xiyong_presentation",
                  child_key, violations)
        return
