import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def luoshu_grid(orientation='south_up'):
    matrix=json.loads((ROOT/'data/canonical/foundations/hetu_luoshu_v1.json').read_text())['luoshu']['matrix_south_up']
    if orientation=='south_up':
        return matrix
    if orientation=='north_up':
        return [row[::-1] for row in matrix[::-1]]
    raise ValueError('Expected south_up or north_up orientation')


def mountain_at(degrees):
    if isinstance(degrees,bool) or not isinstance(degrees,(int,float)) or not math.isfinite(degrees):
        raise ValueError('Expected finite compass degree')
    degree=degrees%360
    records=json.loads((ROOT/'data/canonical/fengshui/twenty_four_mountains_v1.json').read_text())['records']
    # Half-open sectors, using the existing reviewed table without recreating it.
    for record in records:
        start,end=record['start_degrees'],record['end_degrees']
        if (start<=degree<end) if not record['wraps_zero'] else (degree>=start or degree<end):
            return record
    raise ValueError('Existing sector table is incomplete')


def four_beasts():
    return {'left':'青龙','right':'白虎','front':'朱雀','back':'玄武'}


def research_period(year, *, research=False):
    if not research:
        raise ValueError('Unreviewed period data requires explicit research=True')
    if type(year) is not int:
        raise ValueError('Expected integer Gregorian year')
    data=json.loads((ROOT/'data/quarantine/phase1/fengshui/periods.json').read_text())
    for period in data['periods']:
        if period['start_year']<=year<=period['end_year']:
            return period
    raise ValueError('Research table supports 1864..2043 only')
