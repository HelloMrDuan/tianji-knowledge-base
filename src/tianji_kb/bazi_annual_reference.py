"""Reference-year Ganzhi/ten-god facts; NOT annual luck or annual boundaries.

The exact year Ganzhi is sampled at July 1, noon China time, which is
deliberately away from Li Chun. Year boundaries and Dayun efficacy are not
computed by this interface. It is a research-only calendar reference table.
"""
from .calendar import PROVIDER, calendar
from .bazi_core import ten_god

MAX_REFERENCE_YEARS = 20
REFERENCE_MONTH_DAY_TIME = '07-01T12:00:00+08:00'


def annual_reference(day_master, years):
    if type(years) is not list or not 1 <= len(years) <= MAX_REFERENCE_YEARS:
        raise ValueError('annual_reference_years must be a list of 1..20 years')
    if any(type(year) is not int or not 1900 <= year <= 2099 for year in years):
        raise ValueError('annual_reference_years must contain integer calendar years 1900..2099')
    if years != sorted(set(years)):
        raise ValueError('annual_reference_years must be strictly ascending without duplicates')
    rows = []
    for year in years:
        instant = f'{year}-{REFERENCE_MONTH_DAY_TIME}'
        cal = calendar(instant)
        ganzhi = cal['year_ganzhi']
        rows.append({
            'calendar_year': year,
            'reference_datetime': cal['local_datetime'],
            'year_ganzhi_at_reference': ganzhi,
            'year_stem': ganzhi[0],
            'year_branch': ganzhi[1],
            'relative_ten_god': ten_god(day_master, ganzhi[0]),
            'calendar_provider': PROVIDER,
            'jieqi_boundary_of_year_resolved': False,
            'intra_year_ganzhi_not_asserted': True,
            'annual_natal_interaction_status': 'not_evaluated',
            'annual_luck_prediction': None,
        })
    return {
        'variant': 'bazi-annual-midyear-reference-v1',
        'day_master': day_master,
        'reference_policy': 'July 1, 12:00 Asia/Shanghai; sample at a stable midyear instant',
        'calendar_provider': PROVIDER,
        'rows': rows,
        'annual_boundary_calculated': False,
        'dayun_start_age_calculated': False,
        'dayun_direction_calculated': False,
        'annual_luck_assessment': None,
        'research_only': True,
        'public_enabled': False,
        'ai_enabled': False,
        'scope': '仅公历指定年份七月一日正午的真实历法干支与日主十神结构对照；不代表公历全年从元旦起同干支，未裁定立春交界、起运、岁运吉凶或喜用。',
    }
