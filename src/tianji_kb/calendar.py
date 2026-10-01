"""One pinned calendar adapter with explicit timezone and day-boundary policies."""
from datetime import datetime
from zoneinfo import ZoneInfo
from lunar_python import Solar
from .foundations import STEMS, BRANCHES, ganzhi_index

PROVIDER='lunar-python==1.4.8'

def hour_pillar(day_stem,hour_branch):
    if day_stem not in list(STEMS) or hour_branch not in list(BRANCHES):
        raise ValueError('Invalid hour pillar inputs')
    return STEMS[(STEMS.index(day_stem)%5*2+BRANCHES.index(hour_branch))%10]+hour_branch

def calendar(value,day_boundary='midnight'):
    if day_boundary not in ('midnight','zi-start'):
        raise ValueError('Unsupported day boundary')
    instant=datetime.fromisoformat(value) if isinstance(value,str) else value
    if not isinstance(instant,datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('Expected timezone-aware ISO datetime')
    china=instant.astimezone(ZoneInfo('Asia/Shanghai'))
    if not 1900<=china.year<=2099:
        raise ValueError('Supported calendar range is 1900..2099')
    lunar=Solar.fromYmdHms(china.year,china.month,china.day,china.hour,china.minute,china.second).getLunar()
    day=lunar.getDayInGanZhiExact2() if day_boundary=='midnight' else lunar.getDayInGanZhiExact()
    hour=hour_pillar(day[0],BRANCHES[((china.hour+1)//2)%12])
    previous=lunar.getPrevJieQi(False)
    return {'local_datetime':china.isoformat(),'solar_term':previous.getName(),
        'solar_term_started_at':previous.getSolar().toYmdHms()+'+08:00',
        'year_ganzhi':lunar.getYearInGanZhiExact(),'month_ganzhi':lunar.getMonthInGanZhiExact(),
        'day_ganzhi':day,'hour_ganzhi':hour,'day_boundary':day_boundary,'calendar_provider':PROVIDER,
        'lunar_year':lunar.getYear(),'lunar_month':lunar.getMonth(),'lunar_day':lunar.getDay()}
