"""Experimental Lahiri/Vimshottari arithmetic; no life-event interpretations."""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import swisseph as swe
from engine import normalize, julian, FLAGS

VERSION='trace-jyotisha-0.1.0'
LORDS=('Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury')
YEARS=(7,20,6,10,7,18,16,19,17)
STARS=('Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati')


def lunar_sector(longitude):
    if not math.isfinite(longitude) or not 0 <= longitude < 360:
        raise ValueError('Sidereal longitude must be finite and in [0,360).')
    # Multiplication first preserves exact sector boundaries such as 40 degrees.
    coordinate=longitude*3/40
    index=min(26,math.floor(coordinate))
    fraction=coordinate-index
    return {'index_zero_based':index,'name':STARS[index],
            'pada':min(4,math.floor(fraction*4)+1),
            'elapsed_fraction':fraction,'lord':LORDS[index%9]}


def periods(birth, moon_longitude, *, year_days=365.25, count=10):
    if birth.tzinfo is None or birth.utcoffset()!=timedelta(0):
        raise ValueError('Birth must be UTC-aware.')
    if year_days not in (360.0,365.25,365.25636):
        raise ValueError('Supported explicit conventions: 360, 365.25, 365.25636 days.')
    if isinstance(count,bool) or not isinstance(count,int) or not 1<=count<=18:
        raise ValueError('Count must be 1–18.')
    sector=lunar_sector(moon_longitude)
    initial=sector['index_zero_based']%9
    elapsed_days=sector['elapsed_fraction']*YEARS[initial]*year_days
    origin=birth-timedelta(days=elapsed_days)
    output=[]
    accumulated=0
    for k in range(count):
        lord=(initial+k)%9
        start=origin+timedelta(days=accumulated*year_days)
        end=origin+timedelta(days=(accumulated+YEARS[lord])*year_days)
        children=[]
        weights=0
        for j in range(9):
            child=(lord+j)%9
            a=start+timedelta(days=YEARS[lord]*weights/120*year_days)
            weights+=YEARS[child]
            b=end if j==8 else start+timedelta(days=YEARS[lord]*weights/120*year_days)
            children.append({'lord':LORDS[child],'start_utc':a.isoformat(),'end_utc':b.isoformat(),
                             'active_at_birth':a<=birth<b})
        output.append({'lord':LORDS[lord],'duration_years':YEARS[lord],
                       'start_utc':start.isoformat(),'end_utc':end.isoformat(),
                       'active_at_birth':start<=birth<end,'antardashas':children})
        accumulated+=YEARS[lord]
    return {'nakshatra':sector,'balance_years_at_birth':(1-sector['elapsed_fraction'])*YEARS[initial],
            'mahadashas':output}


def calculate(profile,year_days=365.25):
    normalized=normalize(profile)
    birth=datetime.fromisoformat(normalized['utc'])
    swe.set_ephe_path('')
    # Swiss sidereal mode is process-global: always set it explicitly.
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    values,flags=swe.calc_ut(julian(birth),swe.MOON,FLAGS|swe.FLG_SIDEREAL)
    if not flags&swe.FLG_SIDEREAL or not flags&swe.FLG_MOSEPH:
        raise RuntimeError('Unexpected ephemeris flags.')
    data=periods(birth,values[0],year_days=year_days)
    return {'schema_version':1,'provider':'jyotisha','engine_version':VERSION,
            'birth_profile':normalized,
            'conventions':{'ayanamsha':'Swiss SIDM_LAHIRI (1), not Lahiri variants',
                           'sidereal_mode':int(swe.SIDM_LAHIRI),'year_days':year_days,
                           'year_policy':'fixed elapsed days, not calendar anniversaries',
                           'intervals':'[start,end), UTC; pre-birth portions retained',
                           'balance':'remaining angular fraction of lunar nakshatra',
                           'subperiods':'parent years × child years / 120; anchored to full parent start',
                           'uncertainty':'recorded birth time required; no interval propagation implemented',
                           'shared_state':'single-threaded local CLI; isolate Swiss calls before server use'},
            'astronomy':{'swiss_version':swe.version,'backend':'Moshier','returned_flags':flags,
                         'moon_sidereal_longitude_deg':values[0]},
            **data,'biographical_predictions':[],
            'validation_status':'internal_arithmetic_tests_only; independent reference pending',
            'sources':['https://www.astro.com/swisseph/swephprg.htm',
                       'https://astrowatch.live/docs/vimshottari-dasha',
                       'https://occultapi.com/docs/astro/dasha/vimshottari']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('profile');parser.add_argument('--out',required=True)
    parser.add_argument('--year-days',type=float,default=365.25,choices=[360.0,365.25,365.25636])
    args=parser.parse_args();result=calculate(json.loads(Path(args.profile).read_text()),args.year_days)
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    print(f"Lahiri Moon: {result['astronomy']['moon_sidereal_longitude_deg']:.6f}°; {result['nakshatra']['name']}; {len(result['mahadashas'])} major periods. No personal predictions.")
