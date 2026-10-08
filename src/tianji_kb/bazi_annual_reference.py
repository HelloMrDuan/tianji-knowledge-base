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


# Separate opt-in contract: complete Li Chun-to-Li Chun *calendar* intervals.
# Keep annual_reference() unchanged so its fixed research Goldens stay stable.
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from lunar_python import Solar
from .foundations import CYCLE

MAX_LICHUN_YEARS = 10


def _li_chun_of(year):
    """Pinned provider's computed 立春, to seconds, in Asia/Shanghai."""
    table = Solar.fromYmd(year, 7, 1).getLunar().getJieQiTable()
    if '立春' not in table:
        raise ValueError('Pinned calendar has no Li Chun term')
    term = table['立春']
    if term.getYear() != year:
        raise ValueError('Li Chun year differs from the requested Gregorian year')
    instant = datetime.strptime(term.toYmdHms(), '%Y-%m-%d %H:%M:%S')
    instant = instant.replace(tzinfo=ZoneInfo('Asia/Shanghai'))
    if instant.year != year or instant.month != 2 or not 2 <= instant.day <= 6:
        raise ValueError('Li Chun outside the expected February window')
    return instant


def annual_lichun_boundaries(day_master, years):
    """Bounded, provider-confirmed intervals; not natal interaction or 吉凶."""
    if type(years) is not list or not 1 <= len(years) <= MAX_LICHUN_YEARS:
        raise ValueError('annual_boundary_years must contain 1..10 years')
    # The next Li Chun is required, so never extrapolate 2100 using a
    # calendar provider whose validated input range ends at 2099.
    if any(type(year) is not int or not 1900 <= year <= 2098 for year in years):
        raise ValueError('annual_boundary_years require integer years 1900..2098')
    if years != sorted(set(years)):
        raise ValueError('annual_boundary_years must be ascending and unique')
    rows = []
    for year in years:
        start, end = _li_chun_of(year), _li_chun_of(year + 1)
        if not start < end:
            raise ValueError('Li Chun boundaries not strictly increasing')
        at_start = calendar(start)['year_ganzhi']
        before_start = calendar(start - timedelta(seconds=1))['year_ganzhi']
        before_end = calendar(end - timedelta(seconds=1))['year_ganzhi']
        at_end = calendar(end)['year_ganzhi']
        expected = CYCLE[(year - 4) % 60]
        prev_expected = CYCLE[(year - 5) % 60]
        next_expected = CYCLE[(year - 3) % 60]
        if (at_start, before_start, before_end, at_end) != (
            expected, prev_expected, expected, next_expected
        ):
            raise ValueError('Calendar Li Chun boundary disagrees with year GanZhi policy')
        rows.append({
            'gregorian_lichun_year': year,
            'start_inclusive': start.isoformat(),
            'end_exclusive': end.isoformat(),
            'ganzhi_in_interval': expected,
            'year_stem': expected[0],
            'year_branch': expected[1],
            'ten_god_relative_to_natal_day_stem': ten_god(day_master, expected[0]),
            'ganzhi_one_second_before_start': before_start,
            'ganzhi_at_start': at_start,
            'ganzhi_one_second_before_end': before_end,
            'ganzhi_at_end': at_end,
            'boundary_precision': 'provider_seconds',
            'timezone': 'Asia/Shanghai',
            'calendar_provider': PROVIDER,
            'effective_natal_interaction': None,
            'annual_luck_prediction': None,
        })
    return {
        'variant': 'bazi-annual-lichun-boundary-v1',
        'day_master': day_master,
        'boundary_policy': 'Li Chun [start inclusive, next start exclusive], provider seconds, Asia/Shanghai',
        'rows': rows,
        'calendar_provider': PROVIDER,
        'annual_boundary_calculated': True,
        'astronomical_precision_independently_verified': False,
        'dayun_start_age_calculated': False,
        'dayun_direction_calculated': False,
        'annual_luck_assessment': None,
        'research_only': True,
        'public_enabled': False,
        'ai_enabled': False,
        'scope': '仅固定历法库立春秒级边界、年干支和日主十神；不提供天文测量独立认证、真太阳时、起运交运、旺衰喜忌或流年吉凶。',
    }
