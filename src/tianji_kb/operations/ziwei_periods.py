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
