import json
from pathlib import Path
from .liuyao import STEMS, BRANCHES


def base():
    return json.loads((Path(__file__).resolve().parents[3]/'data/canonical/liuren/rules_v1.json').read_text())


def month_general(solar_term):
    for row in base()['month_general_by_solar_terms']:
        if solar_term in row['terms']:
            return row.copy()
    raise ValueError('Unknown solar term')


def sky_plate(month_general,hour_branch):
    if month_general not in list(BRANCHES) or hour_branch not in list(BRANCHES):
        raise ValueError('Expected single branch symbols')
    shift=(BRANCHES.index(month_general)-BRANCHES.index(hour_branch))%12
    return {branch:BRANCHES[(i+shift)%12] for i,branch in enumerate(BRANCHES)}


def validate_sky(sky):
    if set(sky)!=set(BRANCHES) or set(sky.values())!=set(BRANCHES):
        raise ValueError('Expected complete branch permutation')
    shifts={(BRANCHES.index(sky[b])-BRANCHES.index(b))%12 for b in BRANCHES}
    if len(shifts)!=1:
        raise ValueError('Sky plate must be a cyclic rotation')


def four_lessons(day_stem,day_branch,sky):
    validate_sky(sky)
    if day_stem not in list(STEMS) or day_branch not in list(BRANCHES):
        raise ValueError('Invalid day stem/branch')
    if (STEMS.index(day_stem)-BRANCHES.index(day_branch))%2:
        raise ValueError('Day stem/branch polarity mismatch')
    lodging=base()['stem_lodging'][day_stem]
    first=sky[lodging]
    third=sky[day_branch]
    return [{'lesson':1,'upper':first,'lower':day_stem},{'lesson':2,'upper':sky[first],'lower':first},{'lesson':3,'upper':third,'lower':day_branch},{'lesson':4,'upper':sky[third],'lower':third}]


def follow_transmissions(initial,sky):
    validate_sky(sky)
    if initial not in list(BRANCHES):
        raise ValueError('Invalid initial branch')
    # Initial selection and special-case methods are deliberately outside this function.
    middle=sky[initial]
    return [initial,middle,sky[middle]]


def noble_start(day_stem,day_night,variant):
    if day_stem not in list(STEMS) or day_night not in ('昼','夜') or str(variant) not in ('0','1'):
        raise ValueError('Expected valid stem, day/night and explicit variant 0 or 1')
    table=base()['heavenly_generals']['noble_start_variants'][str(variant)]
    return next(value[day_night] for group,value in table.items() if day_stem in group)
