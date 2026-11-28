"""Fengshui inference layer — structural facts and explicit assumptions.

O-05 (TJ-0426 Lane 5). The compass layer
(operations/fengshui.py + operations/fengshui_chart.py: 24 mountains,
Luoshu grid, four beasts, relative_period mathematics) is untouched.
This module adds the inference layer's scaffolding:

- `house_trigram()`: a STRUCTURAL derivation only — sitting mountain
  -> direction -> trigram, reusing the chart's DIRECTIONS mapping.
  It states the house trigram (宅卦）; the 八宅游年吉凶 that would
  consume it is unregistered (gap), so no verdict ever follows.
- `absolute_period()`: the 1864 anchor is NOT evidence. An absolute
  三元 period is refused unless the caller supplies research=True, an
  explicit epoch_year AND an explicit epoch_basis statement; the
  output then echoes that basis with epoch_verified=False and
  production_eligible=False. Only explicit assumptions are honoured;
  no historical epoch is ever recognised.
- `flying_star_sequence()`: pure Luoshu flight arithmetic for a
  caller-supplied period star — the 顺飞/逆飞 cycle 5->6->7->8->9->
  1->2->3->4->5 (forward) and its reverse. Candidate arithmetic,
  evidence D, research_only; it never derives the period from a year.

No 吉凶断语 is produced anywhere in this module.
"""

from .fengshui_chart import DIRECTIONS, relative_period

VARIANT = 'fengshui-reading-structural-v1'
EVIDENCE_LEVEL = 'D'

# Luoshu star flight (forward 顺飞 / reverse 逆飞), as cycles of star
# numbers. Forward: 5,6,7,8,9,1,2,3,4 then back to 5.
FORWARD_FLIGHT = (5, 6, 7, 8, 9, 1, 2, 3, 4)
REVERSE_FLIGHT = (5, 4, 3, 2, 1, 9, 8, 7, 6)
STAR_PALACES = {1: '坎', 2: '坤', 3: '震', 4: '巽', 5: '中', 6: '乾', 7: '兑', 8: '艮', 9: '离'}

FENGSHUI_GAPS = {
    'absolute_epoch': {'status': 'gap', 'evidence_level': 'D',
        'note': '1864 锚点、每运 20 年未证；绝对年表不立。'},
    'house_fate': {'status': 'gap', 'evidence_level': 'D',
        'note': '宅命（八宅游年）推断规则未登记；宅卦只是结构事实。'},
    'flying_stars': {'status': 'candidate_pending_source', 'evidence_level': 'D',
        'note': '飞星顺逆飞算术为候选计算，须来源取证；运数须调用方显式给定。'},
}


def _envelope(payload, evidence_level=EVIDENCE_LEVEL):
    return {'variant': VARIANT, 'research_only': True, 'public': False, 'ai': False,
            'evidence_level': evidence_level, 'determination': None, 'verdict': None,
            **payload}


def house_trigram(mountain_record):
    """Sitting mountain -> house trigram (宅卦）, structural only.

    `mountain_record` is a record as returned by mountain_at()
    (keys: mountain, direction, element, opposite). The trigram and
    its element come from the chart's DIRECTIONS mapping; nothing
    about 吉凶 is inferred, and the 八宅游年 rules that would use
    this trigram are an open gap (FENGSHUI_GAPS['house_fate']).
    """
    if not isinstance(mountain_record, dict):
        raise ValueError('Expected a mountain record dict')
    for key in ('mountain', 'direction', 'element', 'opposite'):
        if key not in mountain_record:
            raise ValueError('Mountain record lacks key: %s' % key)
    direction = mountain_record['direction']
    if direction not in DIRECTIONS:
        raise ValueError('Unknown mountain direction: %r' % (direction,))
    trigram, trigram_element = DIRECTIONS[direction]
    return _envelope({'mountain': mountain_record['mountain'],
                      'direction': direction,
                      'mountain_element': mountain_record['element'],
                      'trigram': trigram, 'trigram_element': trigram_element,
                      'opposite_mountain': mountain_record['opposite']['mountain'],
                      'kind': '结构事实（坐山->宅卦）；八宅游年吉凶未登记。'},
                     evidence_level='C')


def absolute_period(year, *, research=False, epoch_year=None, epoch_basis=None):
    """Absolute 三元 period — only on an explicit caller assumption.

    Refuses unless research=True, epoch_year is an explicit integer
    and epoch_basis is a non-empty statement of the caller's
    assumption. The 1864 anchor is never treated as verified: passing
    epoch_year=1864 still requires epoch_basis, and the output always
    records epoch_verified=False. The underlying 20-year slot math is
    relative_period(); this wrapper only adds the assumption gate.
    """
    if type(year) is not int or isinstance(year, bool):
        raise ValueError('Expected integer Gregorian year')
    if not research:
        raise ValueError('Unverified absolute period requires explicit research=True (O-05)')
    if type(epoch_year) is not int or isinstance(epoch_year, bool):
        raise ValueError('Absolute period requires an explicit integer epoch_year; '
                         'no historical epoch is recognised (O-05)')
    if not isinstance(epoch_basis, str) or not epoch_basis.strip():
        raise ValueError('Absolute period requires an explicit epoch_basis statement; '
                         'the 1864 anchor is unverified and cannot stand in for one')
    period = relative_period(year, epoch_year)
    period = dict(period)
    period.update({'epoch_basis': epoch_basis.strip(), 'epoch_verified': False})
    return _envelope({'year': year, 'period': period,
                      'note': '周期数学只认显式假设；历史纪元未证，production_eligible 恒 False。'})


def flying_star_sequence(start_star, *, direction='forward'):
    """Luoshu flight cycle starting at `start_star` (candidate).

    Forward (顺飞） follows 5->6->7->8->9->1->2->3->4->5; reverse
    （逆飞） follows 5->4->3->2->1->9->8->7->6->5. The sequence is
    pure cycle arithmetic on a caller-supplied starting star; it does
    NOT derive any period, year star or house star — the period the
    star belongs to must be supplied by the caller elsewhere, and the
    flight rule itself is candidate_pending_source (O-05).
    """
    if type(start_star) is not int or isinstance(start_star, bool) or not 1 <= start_star <= 9:
        raise ValueError('Expected starting star 1..9')
    if direction not in ('forward', 'reverse'):
        raise ValueError("Expected direction 'forward' or 'reverse'")
    cycle = FORWARD_FLIGHT if direction == 'forward' else REVERSE_FLIGHT
    start = cycle.index(start_star)
    sequence = [cycle[(start + i) % 9] for i in range(9)]
    return _envelope({'start_star': start_star, 'direction': direction,
                      'sequence': sequence,
                      'palaces': [STAR_PALACES[star] for star in sequence],
                      'rule_status': 'candidate_pending_source',
                      'note': '顺逆飞算术为候选计算；运数与飞星落宫的取用规则未登记。'})
