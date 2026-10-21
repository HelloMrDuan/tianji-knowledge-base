"""One pinned calendar adapter with explicit timezone and day-boundary policies."""
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version as _installed_version
from zoneinfo import ZoneInfo
from lunar_python import Solar
from .foundations import STEMS, BRANCHES, ganzhi_index

PROVIDER='lunar-python==1.4.8'
PINNED_PROVIDER_NAME='lunar-python'
PINNED_PROVIDER_VERSION='1.4.8'


def provider_identity():
    """Verify the actually-installed calendar provider matches the pin.

    Returns the verified identity dict; raises ValueError when the provider
    package is missing or a different version is installed. This reads the
    installed distribution metadata (not a hand-written string), so a
    wrongly installed package cannot masquerade as the pinned provider.
    When the source cannot be reliably confirmed, this raises instead of
    returning a "verified" claim.
    """
    try:
        installed = _installed_version(PINNED_PROVIDER_NAME)
    except PackageNotFoundError as exc:
        raise ValueError(
            "Calendar provider lunar-python is not installed; source unverifiable") from exc
    if installed != PINNED_PROVIDER_VERSION:
        raise ValueError(
            "Calendar provider version mismatch: installed %s != pinned %s; source unverifiable"
            % (installed, PINNED_PROVIDER_VERSION))
    return {"provider": PINNED_PROVIDER_NAME, "installed_version": installed,
            "pinned": PROVIDER, "verified": True}


def hour_pillar(day_stem,hour_branch):
    if day_stem not in list(STEMS) or hour_branch not in list(BRANCHES):
        raise ValueError('Invalid hour pillar inputs')
    return STEMS[(STEMS.index(day_stem)%5*2+BRANCHES.index(hour_branch))%10]+hour_branch

def calendar(value,day_boundary='midnight'):
    # Fail closed on provider drift before any date is computed.
    provider_identity()
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
