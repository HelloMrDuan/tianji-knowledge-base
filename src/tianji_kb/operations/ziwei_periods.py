"""Ziwei decade (大限) and annual (流年) palace arithmetic — CANDIDATE.

O-01 (TJ-0426 Lane 5). Status: candidate_pending_collation, evidence
level D, research_only=true, public=false, ai=false. The arithmetic
below (start age = bureau number; one palace per decade; annual palace
advancing one palace per year-branch step from the life palace) is
implemented so it can be checked against a collated edition; it is NOT
a settled rule. Every output carries rule_status, evidence_level and
determination=None, and no temple-prosperity (庙旺) or auspiciousness
verdict is ever produced.

Gates (fail-closed):
- Sex and year-stem polarity must be given explicitly; the direction
  (forward for yang-male / yin-female, backward otherwise) is never
  silently defaulted, because 长生男顺女逆 vs the modern yin-yang
  male/female configuration is still an open divergence (see
  operations/ziwei.py ZIWEI_GAPS).
- Bureau numbers are only 2..6 (水二/木三/金四/土五/火六局）.
- Leap lunar months are already rejected by the chart layer; this
  module takes an already-computed chart result, never a raw date.
- The annual step direction (``annual_palace`` / ``annual_palaces_for_decade``)
  must be caller-specified ('branch_plus' / 'branch_minus'); it is
  never defaulted.
- 四化壬年分歧 and 魁钺歌分歧 stay unresolved and isolated (see
  ``period_disputes``): this module computes NO 四化 mapping and NO
  天魁/天钺 palace, and produces no 庙旺 claim and no 吉凶断语.

Batch 5 (TJ-0427 Lane F) additions, same candidate calibre:
- ``decade_for_age``: which decade period contains a given age.
- ``annual_palaces_for_decade``: the ten annual palaces inside one
  decade, under the caller-specified annual step convention.
- ``period_disputes``: surfaces the two unresolved disputes from
  operations/ziwei.py at call time; registration only, never a ruling.
"""

from .ziwei_chart import PALACES, bureau_for, ziwei_position
from ..foundations import STEMS, BRANCHES

VARIANT = 'ziwei-decade-annual-candidate-v1'
EVIDENCE_LEVEL = 'D'
RULE_STATUS = 'candidate_pending_collation'
BUREAU_NUMBERS = (2, 3, 4, 5, 6)


def _envelope(payload):
    return {'variant': VARIANT, 'research_only': True, 'public': False, 'ai': False,
            'evidence_level': EVIDENCE_LEVEL, 'rule_status': RULE_STATUS,
            'determination': None, 'verdict': None, **payload}


def decade_start_age(bureau_number):
    """Candidate rule: the first decade starts at the bureau number.

    水二局起 2 岁、木三局 3 岁、金四局 4 岁、土五局 5 岁、火六局 6 岁。
    Pending collation; returns the number only as candidate arithmetic.
    """
    if type(bureau_number) is not int or bureau_number not in BUREAU_NUMBERS:
        raise ValueError('Expected bureau number 2..6 (water/wood/metal/earth/fire)')
    return bureau_number


def decade_direction(year_stem, sex):
    """Candidate direction rule; sex and stem polarity must be explicit.

    Forward when (yang stem + male) or (yin stem + female); otherwise
    backward. Never defaulted: unknown sex/stem raises.
    """
    if year_stem not in list(STEMS):
        raise ValueError('Unknown year stem')
    if sex not in ('男', '女'):
        raise ValueError('Expected explicit sex 男/女; direction is never defaulted')
    yang = STEMS.index(year_stem) % 2 == 0
    return 'forward' if (yang and sex == '男') or (not yang and sex == '女') else 'backward'


def decade_periods(*, bureau_number, life_palace_branch, year_stem, sex, count=12):
    """Twelve (by default) decade periods from the life palace.

    Each decade spans 10 ages starting at the bureau number and steps
    one palace per decade in the chosen direction. Palace names follow
    the life-palace ring (命宫 first). Returns the flagged envelope.
    """
    if life_palace_branch not in list(BRANCHES):
        raise ValueError('Unknown life palace branch')
    if type(count) is not int or count < 1:
        raise ValueError('Expected positive decade count')
    start = decade_start_age(bureau_number)
    direction = decade_direction(year_stem, sex)
    # 顺行 follows the palace ring (命宫->兄弟->夫妻...), which is
    # branch index -1 per decade (the chart lays palaces out as
    # branch(life - i)); 逆行 is +1. Candidate convention, pending
    # collation — stated here, never silently flipped.
    step = -1 if direction == 'forward' else 1
    life_index = BRANCHES.index(life_palace_branch)
    periods = []
    for i in range(count):
        age_start = start + 10 * i
        palace_index = (life_index + step * i) % 12
        branch = BRANCHES[palace_index]
        # Palace name: the ring is anchored at the life palace; the
        # palace occupying branch X is PALACES[(life_index - X) % 12]
        # counting backwards from 命宫 around the ring.
        name = PALACES[(life_index - palace_index) % 12]
        periods.append({'decade': i + 1, 'palace': name, 'branch': branch,
                        'age_start': age_start, 'age_end': age_start + 9})
    return _envelope({'direction': direction, 'decade_start_age': start,
                      'life_palace_branch': life_palace_branch, 'periods': periods})


def annual_palace(*, life_palace_branch, birth_year_branch, target_year_branch, convention):
    """Candidate annual-palace arithmetic.

    The 流年命宫 advances one palace per year-branch step from the
    life palace: offset = (target - birth) mod 12. The step direction
    is itself uncollated, so `convention` is a REQUIRED explicit
    caller choice — 'branch_plus' (palace branch = life + offset) or
    'branch_minus' (life - offset) — never silently defaulted. No year
    is ever derived from a bare Gregorian year here; both branches are
    explicit caller inputs, so no year-boundary convention is smuggled
    in.
    """
    for label, branch in (('life_palace_branch', life_palace_branch),
                          ('birth_year_branch', birth_year_branch),
                          ('target_year_branch', target_year_branch)):
        if branch not in list(BRANCHES):
            raise ValueError('Unknown branch for %s' % label)
    if convention not in ('branch_plus', 'branch_minus'):
        raise ValueError("Expected explicit convention 'branch_plus' or 'branch_minus'; "
                         'the annual step direction is uncollated and never defaulted')
    life_index = BRANCHES.index(life_palace_branch)
    offset = (BRANCHES.index(target_year_branch) - BRANCHES.index(birth_year_branch)) % 12
    signed = offset if convention == 'branch_plus' else -offset
    palace_index = (life_index + signed) % 12
    return _envelope({'life_palace_branch': life_palace_branch,
                      'birth_year_branch': birth_year_branch,
                      'target_year_branch': target_year_branch,
                      'convention': convention,
                      'annual_palace': PALACES[(life_index - palace_index) % 12],
                      'annual_palace_branch': BRANCHES[palace_index],
                      'year_offset': offset})


def decade_for_age(*, bureau_number, life_palace_branch, year_stem, sex,
                   age, count=12):
    """Candidate: which decade period contains a given age.

    Reuses ``decade_periods`` (same direction and start-age rules).
    Returns the flagged envelope with ``decade`` set to the containing
    period, or ``status`` 'not_applicable' with ``decade`` None when
    the age falls before the first decade or beyond the ``count``
    covered decades — never silently clamped to the nearest decade.
    ``age`` must be a non-negative integer; a non-integer or negative
    age raises ValueError.
    """
    if type(age) is not int or age < 0:
        raise ValueError('Expected non-negative integer age')
    result = decade_periods(bureau_number=bureau_number,
                            life_palace_branch=life_palace_branch,
                            year_stem=year_stem, sex=sex, count=count)
    for period in result['periods']:
        if period['age_start'] <= age <= period['age_end']:
            return _envelope({'status': 'computed',
                              'age': age,
                              'decade': dict(period),
                              'direction': result['direction'],
                              'decade_start_age': result['decade_start_age'],
                              'life_palace_branch': life_palace_branch})
    covered = result['periods']
    return _envelope({'status': 'not_applicable',
                      'reason': 'age_outside_covered_decades',
                      'age': age,
                      'decade': None,
                      'direction': result['direction'],
                      'decade_start_age': result['decade_start_age'],
                      'covered_age_range': [covered[0]['age_start'],
                                            covered[-1]['age_end']],
                      'life_palace_branch': life_palace_branch})


def annual_palaces_for_decade(*, life_palace_branch, birth_year_branch,
                              decade_start_year_branch, convention, count=10):
    """Candidate: the annual palaces inside one decade.

    The decade's first year has branch ``decade_start_year_branch``;
    each following year steps one year-branch forward (the year-branch
    cycle itself is fixed; only the PALACE step direction is the
    uncollated choice, so ``convention`` stays a REQUIRED explicit
    caller choice — 'branch_plus' or 'branch_minus' — exactly as in
    ``annual_palace``). No Gregorian year is ever derived here; all
    year identities are explicit branches. Returns the flagged
    envelope with one entry per year (``year_offset_in_decade`` 0..9).
    """
    for label, branch in (('life_palace_branch', life_palace_branch),
                          ('birth_year_branch', birth_year_branch),
                          ('decade_start_year_branch', decade_start_year_branch)):
        if branch not in list(BRANCHES):
            raise ValueError('Unknown branch for %s' % label)
    if convention not in ('branch_plus', 'branch_minus'):
        raise ValueError("Expected explicit convention 'branch_plus' or 'branch_minus'; "
                         'the annual step direction is uncollated and never defaulted')
    if type(count) is not int or count < 1:
        raise ValueError('Expected positive year count')
    start_index = BRANCHES.index(decade_start_year_branch)
    years = []
    for i in range(count):
        target = BRANCHES[(start_index + i) % 12]
        one = annual_palace(life_palace_branch=life_palace_branch,
                            birth_year_branch=birth_year_branch,
                            target_year_branch=target,
                            convention=convention)
        years.append({'year_offset_in_decade': i,
                      'target_year_branch': target,
                      'annual_palace': one['annual_palace'],
                      'annual_palace_branch': one['annual_palace_branch'],
                      'year_offset': one['year_offset']})
    return _envelope({'life_palace_branch': life_palace_branch,
                      'birth_year_branch': birth_year_branch,
                      'decade_start_year_branch': decade_start_year_branch,
                      'convention': convention,
                      'years': years})


def period_disputes():
    """Return the two unresolved period-layer disputes (registration only).

    Reads ``operations/ziwei.py`` at call time: the 壬年四化分歧
    (iztro software table vs the isolated candidate containing
    「壬梁紫府武」) and the 魁钺歌分歧 （古籍「丙丁猪狗」 vs 现代
    「丙丁猪鸡」). Both stay ``unresolved`` with ``determination``
    None. This module computes NO 四化 mapping and NO 天魁/天钺
    palace; the disputes are surfaced so a caller can gate on them,
    never resolved here.
    """
    from .ziwei import (FOUR_TRANSFORMATIONS_REN_DISPUTE, KUIYUE_DISPUTE)
    ren = dict(FOUR_TRANSFORMATIONS_REN_DISPUTE,
               isolated_candidate=dict(
                   FOUR_TRANSFORMATIONS_REN_DISPUTE['isolated_candidate']))
    kuiyue = dict(KUIYUE_DISPUTE)
    return _envelope({
        'four_transformations_ren_year': ren,
        'kuiyue_song': kuiyue,
        'computed_sihua': None,
        'computed_kuiyue_palaces': None,
        'note': ('四化壬年分歧与魁钺歌分歧均未裁决、保持隔离；本模块不计算'
                 '四化映射，不计算天魁/天钺落宫，不作庙旺与吉凶断语。'),
    })


def anchor_check():
    """Fixed classical anchor (regression, pure functions only).

    《紫微斗数全书》甲子年正月初一子时：丙寅火六局、酉宫紫微。
    Verified here without the sealed tables: bureau_for(丙,寅)=火6
    and ziwei_position(1,6) lands on branch index 9 (酉）.
    """
    bureau = bureau_for('丙', '寅')
    position = ziwei_position(1, 6)
    return {'bureau': bureau, 'ziwei_branch': BRANCHES[position],
            'expected': {'bureau': {'element': '火', 'number': 6}, 'ziwei_branch': '酉'},
            'matches': bureau == {'element': '火', 'number': 6} and BRANCHES[position] == '酉'}
