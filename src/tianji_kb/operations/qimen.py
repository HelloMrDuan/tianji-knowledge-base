"""Structural qfdk compatibility; classical variants remain separate.

Algorithm reference: qfdk/qimen (MIT), commit
1d0d1c5b39755e67525a11e68bab9b73baae1937, lib/{dipan,jiuxing,bamen,bashen,qimen}.js.
Calendar adapter uses lunar-python 1.4.8. No auspiciousness interpretation.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .liuyao import STEMS, BRANCHES

ORDER = ['1','8','3','4','9','2','7','6']
STARS = ['天蓬','天任','天冲','天辅','天英','禽芮','天柱','天心']
DOORS = ['休门','生门','伤门','杜门','景门','死门','惊门','开门']
DEITIES = ['值符','腾蛇','太阴','六合','白虎','玄武','九地','九天']
RULESET = 'qfdk-table-exact-term-v1'


def base():
    return json.loads((Path(__file__).resolve().parents[3] / 'data/canonical/qimen/qfdk_maoshan_v1.json').read_text())


def ganzhi_index(value):
    cycle = [STEMS[i%10]+BRANCHES[i%12] for i in range(60)]
    if value not in cycle:
        raise ValueError('Invalid sexagenary pillar')
    return cycle.index(value)


def bureau(solar_term, day_ganzhi):
    day = ganzhi_index(day_ganzhi)
    fu = BRANCHES[(day-day%5)%12]
    yuan = 0 if fu in '子午卯酉' else 1 if fu in '寅申巳亥' else 2
    matches = [x for x in base()['solar_term_bureaus'] if x[0]==solar_term]
    if not matches:
        raise ValueError('Unknown solar term')
    term, direction, numbers = matches[0]
    return {'solar_term':term,'dun':direction,'bureau':int(numbers[yuan]),'yuan':['上元','中元','下元'][yuan],'futou_branch':fu}


def earth_plate(dun, number):
    if dun not in ('阴','阳') or type(number) is not int or not 1 <= number <= 9:
        raise ValueError('Expected yin/yang and bureau 1..9')
    step = 1 if dun=='阳' else -1
    return {str((number-1+step*i)%9+1): stem for i,stem in enumerate('戊己庚辛壬癸丁丙乙')}


def chart_from_calendar(solar_term, day_ganzhi, hour_ganzhi, ruleset=RULESET):
    if ruleset != RULESET:
        raise ValueError('Unsupported school/variant; no implicit fallback')
    info = bureau(solar_term,day_ganzhi)
    hour = ganzhi_index(hour_ganzhi)
    earth = earth_plate(info['dun'],info['bureau'])
    instrument = '戊己庚辛壬癸'[hour//10]
    def palace(stem):
        found = next(p for p,s in earth.items() if s==stem)
        return '2' if found=='5' else found
    origin = palace(instrument)
    target = origin if hour_ganzhi[0]=='甲' else palace(hour_ganzhi[0])
    shift = (ORDER.index(target)-ORDER.index(origin))%8
    sky = {ORDER[(i+shift)%8]:earth[p] for i,p in enumerate(ORDER)}
    sky['5']=earth['5']
    stars = {ORDER[(i+shift)%8]:star for i,star in enumerate(STARS)}
    stars['5']=''
    door_raw = (int(origin)-1+(hour%10)*(1 if info['dun']=='阳' else -1))%9+1
    door_palace = '2' if door_raw==5 else str(door_raw)
    door_shift = (ORDER.index(door_palace)-ORDER.index(origin))%8
    doors = {ORDER[(i+door_shift)%8]:door for i,door in enumerate(DOORS)}
    doors['5']=''
    gods = {p:'' for p in map(str,range(1,10))}
    sign = 1 if info['dun']=='阳' else -1
    for i,god in enumerate(DEITIES):
        gods[ORDER[(ORDER.index(target)+sign*i)%8]]=god
    return {'ruleset':ruleset,'school':'茅山派/转盘（沿用上游命名）','variant':'固定 qfdk 表；节气按准确时刻，非上游整日切换',**info,'day_ganzhi':day_ganzhi,'hour_ganzhi':hour_ganzhi,'earth_plate':earth,'sky_plate':sky,'stars':stars,'doors':doors,'deities':gods,'chief_star_origin':origin,'chief_star_palace':target,'chief_door_palace':door_palace,'chief_door_raw':str(door_raw),'scope':'基础符号盘；不含置闰、超神接气、暗干、格局占断与其他流派。'}


def calendar_from_datetime(value):
    from lunar_python import Solar
    instant = datetime.fromisoformat(value) if isinstance(value,str) else value
    if not isinstance(instant,datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError('Datetime must include an explicit timezone')
    china = instant.astimezone(ZoneInfo('Asia/Shanghai'))
    if not 1900 <= china.year <= 2099:
        raise ValueError('Calendar adapter supports 1900..2099')
    lunar = Solar.fromYmdHms(china.year,china.month,china.day,china.hour,china.minute,china.second).getLunar()
    previous = lunar.getPrevJieQi(False)  # exact instant, not a whole-day boundary
    # Upstream uses midnight day pillar plus lunar-library hour pillar (23h convention).
    return {'solar_term':previous.getName(),'day_ganzhi':lunar.getDayInGanZhi(),'hour_ganzhi':lunar.getTimeInGanZhi(),'local_datetime':china.isoformat(),'solar_term_started_at':previous.getSolar().toYmdHms()+'+08:00','calendar_provider':'lunar-python==1.4.8','day_boundary':'midnight day; hour pillar follows lunar-python 23h convention'}


def chart_from_datetime(value, ruleset=RULESET):
    calendar = calendar_from_datetime(value)
    chart = chart_from_calendar(calendar['solar_term'],calendar['day_ganzhi'],calendar['hour_ganzhi'],ruleset)
    chart['calendar']=calendar
    return chart
