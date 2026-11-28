"""Yijing reading layer — classical-text excerpts only, no divination.

O-04 (TJ-0426 Lane 5). The structure layer
(operations/yijing.py + operations/yijing_chart.py: 64 hexagrams,
derived transforms, 4096 change masks) is untouched. This module is
the reading layer's立项 (establishment):

- `candidate_texts()`: pure selection of verbatim classical texts for
  a chart — the hexagram judgment, the moving lines' statements, the
  changed hexagram's judgment — labelled 原文摘录. Selection is
  mechanical (which texts, not what they mean); no interpretation is
  attached and no verdict is produced.
- `reading()`: the fail-closed gate. No reviewed reading rule exists
  (which line's text governs a reading, how multiple moving lines are
  weighed, when 用九/用六 is read), so it ALWAYS abstains:
  verdict None, determination None, with the named O-04 gaps. The
  excerpts ride along, but they are never presented as a conclusion.
- `corpus_inventory()`: structural counts of the supplied corpus
  (64 judgments / 384 line statements / 用九·用六 special uses).

The corpus is injected, never read here by default: tests use a
clearly-labelled synthetic fixture, and `load_classic_corpus()` (the
sealed-core loader, data-gated in tests) is the only path that touches
the classical-text file. No AI computation is involved anywhere.
"""

from pathlib import Path
import json

from .yijing import transform

VARIANT = 'yijing-reading-registry-v1'
ROOT = Path(__file__).resolve().parents[3]

# Reading-rule slots. Every slot is unregistered: the selection rule
# for a reading (which text governs, how several moving lines combine)
# has no reviewed source, so no slot may fire.
READING_RULE_SLOTS = {
    'no_moving_line': {'status': 'unregistered', 'evidence_level': None,
                       'gap': 'O-04: 无动爻时读何文（卦辞/彖辞）未立规则。'},
    'single_moving_line': {'status': 'unregistered', 'evidence_level': None,
                           'gap': 'O-04: 单动爻取爻辞的占断规则未登记。'},
    'multiple_moving_lines': {'status': 'unregistered', 'evidence_level': None,
                              'gap': 'O-04: 多动爻取爻规则未登记。'},
    'all_lines_moving': {'status': 'unregistered', 'evidence_level': None,
                         'gap': 'O-04: 六爻皆动时取爻规则未登记。'},
    'qian_kun_special_use': {'status': 'unregistered', 'evidence_level': None,
                             'gap': 'O-04: 乾坤用九/用六的取用规则未登记；'
                                    '语料中存在用九/用六条目只是结构事实。'},
}

YIJING_GAPS = {
    'reading_rules': {'status': 'gap', 'evidence_level': 'D',
                      'note': '占断规则 0 条；结构层完整不等于占断层立项。'},
}


def load_classic_corpus():
    """Load the sealed classical core (64 records) as a lookup corpus.

    The classic-core file carries the texts (judgment / line
    statements / special use) but no binary key; the bit string
    (``binary_bottom_to_top``) lives in the sealed relations file
    (``hexagram_relations_v1.json``), joined here on the King Wen
    ``number`` (1..64, verified identical in both files). No bit
    string is hard-coded: both sides are read from sealed data at
    runtime, and a missing or duplicate join key fails loudly.

    Raises FileNotFoundError when the public checkout has no data/;
    that is an environment limitation, not a reading rule.
    """
    core = json.loads((ROOT / 'data/canonical/yijing/zhouyi_classic_core.json').read_text())
    relations = json.loads((ROOT / 'data/canonical/yijing/hexagram_relations_v1.json').read_text())
    bits_by_number = {}
    for record in relations['records']:
        number = record['number']
        if number in bits_by_number:
            raise ValueError(
                'Duplicate hexagram number %r in the relations file'
                % (number,))
        bits_by_number[number] = record['binary_bottom_to_top']
    corpus = {}
    for record in core['records']:
        number = record['number']
        if number not in bits_by_number:
            raise ValueError(
                'Classic core record %r has no binary key in the relations file'
                % (number,))
        bits = bits_by_number[number]
        if bits in corpus:
            raise ValueError('Duplicate hexagram bits %r' % (bits,))
        corpus[bits] = {'judgment': record['judgment'],
                        'lines': {i + 1: line for i, line in enumerate(record['lines'])},
                        'special_use': record.get('special_use')}
    return corpus


def corpus_inventory(corpus):
    """Structural counts of an injected corpus (no interpretation)."""
    if not isinstance(corpus, dict) or not corpus:
        raise ValueError('Expected a non-empty corpus mapping bits -> texts')
    line_count = sum(len(entry['lines']) for entry in corpus.values())
    special = sorted({bits for bits, entry in corpus.items() if entry.get('special_use')})
    return {'hexagrams': len(corpus), 'line_statements': line_count,
            'special_use_hexagrams': special}


def _validate(bits, changing_lines, corpus):
    if not isinstance(corpus, dict) or bits not in corpus:
        raise ValueError('Hexagram %r is not in the supplied corpus' % (bits,))
    # transform() validates bits and changing lines (unique ints 1..6).
    changed = transform(bits, 'change', tuple(changing_lines))
    if changed not in corpus:
        raise ValueError('Changed hexagram %r is not in the supplied corpus' % (changed,))
    return changed


def candidate_texts(bits, changing_lines=(), corpus=None):
    """Verbatim classical texts for a chart — excerpts, not a reading.

    Returns the original hexagram's judgment, the moving lines'
    statements (in line order), and the changed hexagram's judgment.
    The special-use text (用九/用六) is listed as present when the
    corpus carries it, but no rule selects it: its use is unregistered.
    """
    if corpus is None:
        raise ValueError('A corpus must be supplied explicitly; no default corpus is assumed')
    changed = _validate(bits, tuple(changing_lines), corpus)
    original = corpus[bits]
    lines = tuple(changing_lines)
    return {'variant': VARIANT, 'research_only': True, 'public': False, 'ai': False,
            'evidence_level': 'C', 'determination': None, 'verdict': None,
            'kind': '原文摘录，非占断结论',
            'original_bits': bits, 'changed_bits': changed,
            'original_judgment': original['judgment'],
            'moving_line_statements': {line: original['lines'][line] for line in lines},
            'changed_judgment': corpus[changed]['judgment'],
            'special_use_present': bool(original.get('special_use')),
            'special_use_text': original.get('special_use'),
            'special_use_note': '用九/用六条目存在与否是结构事实；取用规则未登记，不选用。'}


def reading(bits, changing_lines=(), corpus=None):
    """Fail-closed reading gate: always abstains.

    The excerpts are returned for reference, but no 占断 conclusion
    is ever produced: every reading-rule slot is unregistered (O-04).
    Callers must not present `candidate_texts` as a reading.
    """
    excerpts = candidate_texts(bits, changing_lines, corpus)
    return {'variant': VARIANT, 'research_only': True, 'public': False, 'ai': False,
            'evidence_level': 'D', 'determination': None, 'verdict': None,
            'status': 'abstain_unregistered_reading_rule',
            'gaps': [slot['gap'] for slot in READING_RULE_SLOTS.values()],
            'excerpts': excerpts}
