"""Small source-backed placements; full Ziwei charts are not implemented."""
import json
from pathlib import Path
from .liuyao import STEMS, BRANCHES


def base():
    return json.loads((Path(__file__).resolve().parents[3] / 'data/canonical/ziwei/iztro_rules_v1.json').read_text())


def lucun(year_stem):
    if year_stem not in list(STEMS):
        raise ValueError('Unknown year stem')
    return base()['star_placement_rules']['lucun']['by_year_stem'][year_stem]


def tianma(year_branch):
    if year_branch not in list(BRANCHES):
        raise ValueError('Unknown year branch')
    return next(value for group,value in base()['star_placement_rules']['tianma']['by_year_branch_group'].items() if year_branch in group)


def four_transformations(year_stem, variant):
    """Legacy implementation lookup only; never resolves textual differences."""
    if variant!='iztro-default-v2':
        raise ValueError('Unsupported or unreviewed four-transformation variant')
    if year_stem not in list(STEMS):
        raise ValueError('Unknown year stem')
    return dict(zip(['化禄','化权','化科','化忌'],base()['four_transformations'][year_stem]))
