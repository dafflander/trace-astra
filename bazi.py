"""Four pillars and annual elemental context under explicit TRACE conventions.

Solar year/month boundaries are astronomical; day/hour use local civil time.
No luck score, event forecasts, gender inference or implicit Da Yun convention.
"""
from datetime import datetime, date, timedelta, timezone
from functools import lru_cache
import swisseph as swe
from engine import normalize, julian, FLAGS

VERSION='trace-bazi-0.1.0'
STEMS=('Jia','Yi','Bing','Ding','Wu','Ji','Geng','Xin','Ren','Gui')
BRANCHES=('Zi','Chou','Yin','Mao','Chen','Si','Wu','Wei','Shen','You','Xu','Hai')
ELEMENTS=('Madera','Fuego','Tierra','Metal','Agua')
BRANCH_ELEMENTS=('Agua','Tierra','Madera','Madera','Tierra','Fuego','Fuego','Tierra','Metal','Metal','Tierra','Agua')
JIE=('Li Chun','Jing Zhe','Qing Ming','Li Xia','Mang Zhong','Xiao Shu','Li Qiu','Bai Lu','Han Lu','Li Dong','Da Xue','Xiao Han')
UTC=timezone.utc
CONVENTIONS={'clock':'local civil IANA time, including DST; no apparent solar-time correction',
 'day_boundary':'00:00 local Gregorian date; late Zi hour uses following day stem',
 'year_boundary':'Li Chun, apparent tropical solar longitude 315 degrees',
 'month_boundary':'12 jie: 315 + 30*n degrees, half-open intervals',
 'day_anchor':'2000-01-07 Jia-Zi, proleptic Gregorian',
 'southern_hemisphere':'same traditional solar-month sequence; no seasonal inversion',
 'scope':'four pillars and annual elemental context; not a complete BaZi life-event model',
 'dayun':'not inferred: direction and age convention require an explicit separate profile'}

def pillar(stem,branch):
    stem%=10;branch%=12
    if stem%2!=branch%2:raise ValueError('Invalid stem/branch parity')
    return {'stem':STEMS[stem],'branch':BRANCHES[branch],'stem_index':stem,'branch_index':branch,
            'label':STEMS[stem]+'-'+BRANCHES[branch],'element':ELEMENTS[stem//2],
            'polarity':'Yang' if stem%2==0 else 'Yin','branch_element':BRANCH_ELEMENTS[branch]}

def from_jd(jd):
    # Unix anchor avoids seconds=60 floating point edge cases in calendar unpacking.
    return datetime(1970,1,1,tzinfo=UTC)+timedelta(days=jd-2440587.5)

@lru_cache(maxsize=210*12)
def solar_term(year,index):
    if type(year) is not int or not 1898<=year<=2102 or type(index) is not int or not 0<=index<12:
        raise ValueError('Unsupported solar term')
    # Last jie is January in the following Gregorian year.
    month=index+2;cy=year
    if month>12:month-=12;cy+=1
    start=datetime(cy,month,1,tzinfo=UTC)
    swe.set_ephe_path('')
    jd=swe.solcross_ut((315+30*index)%360,julian(start),FLAGS)
    t=from_jd(jd)
    if not start<=t<start+timedelta(days=15):raise RuntimeError('Solar term outside expected bracket')
    values,flags=swe.calc_ut(jd,swe.SUN,FLAGS)
    if not flags&swe.FLG_MOSEPH:raise RuntimeError('Unexpected solar term backend')
    return t

def solar_year(at):
    return at.year if at>=solar_term(at.year,0) else at.year-1

def calculate(profile):
    birth=normalize(profile);at=datetime.fromisoformat(birth['utc']);local=datetime.fromisoformat(birth['local_datetime'])
    year=solar_year(at);yi=(year-1984)%60
    boundaries=[solar_term(year,i) for i in range(12)]+[solar_term(year+1,0)]
    month=next(i for i in range(12) if boundaries[i]<=at<boundaries[i+1])
    di=(local.date()-date(2000,1,7)).days%60
    hb=((local.hour+1)//2)%12
    hour_day=di+(1 if local.hour==23 else 0)
    pillars={'year':pillar(yi%10,yi%12),'month':pillar((yi%5)*2+2+month,month+2),
             'day':pillar(di%10,di%12),'hour':pillar((hour_day%5)*2+hb,hb)}
    return {'system':'bazi','version':VERSION,'birth':birth,'conventions':dict(CONVENTIONS),
            'pillars':pillars,'day_master':pillars['day'],
            'solar_year':year,'solar_month':{'index':month,'name':JIE[month],
             'start_utc':boundaries[month].isoformat(),'end_utc':boundaries[month+1].isoformat()},
            'status':'calendar_with_editorial_context_not_predictive_validation'}

def annual_context(profile,start,end,rules):
    record=calculate(profile);a=datetime.fromisoformat(start);b=datetime.fromisoformat(end)
    if a.tzinfo is None or b.tzinfo is None or a>=b:raise ValueError('Ordered aware interval required')
    if a<datetime.fromisoformat(record['birth']['utc']):raise ValueError('Pre-birth interval')
    if not (1900<=a.year<=2100 and 1900<=b.year<=2100) or b-a>timedelta(days=730):raise ValueError('Unsupported range')
    output=[]
    for year in range(a.year-1,b.year+1):
        first,last=solar_term(year,0),solar_term(year+1,0)
        if first>=b or last<=a:continue
        yi=(year-1984)%60;annual=pillar(yi%10,yi%12)
        rule=next(r for r in rules if r['day_master_element']==record['day_master']['element'] and r['annual_stem_element']==annual['element'])
        output.append({'system':'bazi','rule':rule,'start_utc':first.isoformat(),'end_utc':last.isoformat(),
          'visible_start_utc':max(a,first).isoformat(),'visible_end_utc':min(b,last).isoformat(),
          'clipped':first<a or last>b,'eligible_for_review':False,'probability':None,
          'annual_pillar':annual,'day_master':record['day_master'],'conventions':dict(CONVENTIONS),
          'status':'editorial_context_not_event_forecast'})
    return record,output
