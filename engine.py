"""Local astronomical prototype. No biographical inference or network access."""
import argparse
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import swisseph as swe
from temporal import find_windows

VERSION = 'trace-calculation-0.2.0'
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
BODIES = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
          'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
          'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
          'Pluto': swe.PLUTO}
RULE = {'id': 'geometry.saturn-natal-sun.major-aspects', 'version': 2,
        'angles_deg': [0, 60, 90, 120, 180], 'orb_deg': 1.0,
        'sample_step_hours': 24, 'interpretation': None,
        'status': 'geometric_detector_only',
        'source': 'https://www.astro.com/swisseph/swephprg.htm',
        'policy': 'Angles and one-degree threshold are explicit prototype configuration, not validated predictors.'}

def normalize(profile):
    local = datetime.fromisoformat(profile['local_datetime'])
    if local.tzinfo is not None:
        raise ValueError('local_datetime must have no UTC offset; supply an IANA timezone.')
    if not 1900 <= local.year <= 2100:
        raise ValueError('Prototype supports birth years 1900–2100.')
    zone = ZoneInfo(profile['timezone'])
    candidates = {}
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        utc = aware.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == local:
            candidates[fold] = utc
    if not candidates:
        raise ValueError('Nonexistent local time due to clock change.')
    if len(set(candidates.values())) > 1 and 'fold' not in profile:
        raise ValueError('Ambiguous local time; specify fold 0 or 1 after checking the birth record.')
    fold = profile.get('fold', 0)
    if fold not in (0, 1) or fold not in candidates:
        raise ValueError('Invalid fold.')
    for key, limit in [('latitude', 90), ('longitude', 180)]:
        value = profile[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > limit:
            raise ValueError(f'Invalid {key}.')
    if profile.get('time_accuracy') != 'recorded':
        raise ValueError('This prototype requires a recorded time; approximate/unknown time needs a separate uncertainty protocol.')
    return {'utc': candidates[fold].isoformat(), 'timezone': profile['timezone'],
            'local_datetime': local.isoformat(), 'fold': fold,
            'latitude': profile['latitude'], 'longitude': profile['longitude'],
            'time_accuracy': 'recorded'}

def julian(utc):
    utc = utc.astimezone(timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                     utc.hour + utc.minute/60 + utc.second/3600 + utc.microsecond/3.6e9)

def position(utc, body):
    values, flags = swe.calc_ut(julian(utc), BODIES[body], FLAGS)
    if flags & swe.FLG_MOSEPH == 0:
        raise RuntimeError('Unexpected ephemeris backend.')
    return {'longitude_deg': values[0], 'latitude_deg': values[1],
            'distance_au': values[2], 'longitude_speed_deg_day': values[3],
            'returned_flags': flags}

def separation(a, b):
    return abs((a-b+180) % 360-180)

def calculate(profile, start, end):
    normalized = normalize(profile)
    start = datetime.combine(date.fromisoformat(start), datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(date.fromisoformat(end), datetime.min.time(), tzinfo=timezone.utc)
    if start.time() != datetime.min.time() or end.time() != datetime.min.time():
        raise ValueError('Scan boundaries must be ISO dates at midnight UTC.')
    if not (1900 <= start.year <= 2100 and 1900 <= end.year <= 2100) or not 0 <= (end-start).days <= 730:
        raise ValueError('Scan must be ordered, 1900–2100, and at most 730 days.')
    birth = datetime.fromisoformat(normalized['utc'])
    swe.set_ephe_path('')
    natal = {name: position(birth, name) for name in BODIES}
    target = natal['Sun']['longitude_deg']
    samples = []
    for day in range((end-start).days+1):
        time = start+timedelta(days=day)
        saturn = position(time, 'Saturn')['longitude_deg']
        distance = separation(saturn, target)
        for angle in RULE['angles_deg']:
            orb = abs(distance-angle)
            if orb <= RULE['orb_deg']:
                samples.append({'utc': time.isoformat(), 'transit_body': 'Saturn',
                                'natal_body': 'Sun', 'transit_longitude_deg': saturn,
                                'natal_longitude_deg': target, 'separation_deg': distance,
                                'aspect_deg': angle, 'orb_deg': orb,
                                'rule_id': RULE['id'], 'rule_version': RULE['version']})
    # Cache positions shared by the five aspect scans; refinements remain deterministic.
    cache = {}
    def longitude(time):
        if time not in cache:
            cache[time] = position(time, 'Saturn')['longitude_deg']
        return cache[time]
    windows = []
    for angle in RULE['angles_deg']:
        def orb(time):
            return abs(separation(longitude(time), target)-angle)
        for window in find_windows(orb, start, end, threshold=RULE['orb_deg']):
            closest = datetime.fromisoformat(window['closest_utc'])
            window.update({'transit_body':'Saturn','natal_body':'Sun',
                           'aspect_deg':angle,'rule_id':RULE['id'],'rule_version':RULE['version'],
                           'natal_longitude_deg':target,
                           'transit_longitude_at_closest_deg':longitude(closest),
                           'statement':f"Saturno y el Sol natal presentan una separación cercana a {angle}°, dentro del umbral de 1°. No implica un acontecimiento personal."})
            windows.append(window)
    windows.sort(key=lambda w:(w['entry_utc'],w['aspect_deg']))
    record = {'schema_version': 2, 'engine_version': VERSION,
              'provider': {'name':'Swiss Ephemeris', 'version':swe.version,
                           'backend':'Moshier (explicit)', 'requested_flags':FLAGS,
                           'frame':'geocentric, apparent, tropical ecliptic of date',
                           'time_policy':'UTC supplied to calc_ut as UT approximation; no DUT1 correction',
                           'location_use':'retained as input only; no topocentric positions or houses'},
              'birth_profile':normalized, 'natal_positions':natal,
              'scan':{'start_utc':start.isoformat(), 'end_utc':end.isoformat(),
                      'inclusive':True, 'step_hours':24,
                      'window_discovery_step_hours':6,
                      'limitation':'Six-hour grid discovers windows; bracketed boundaries and local minima refined to one second numerically. Sub-grid contacts may be missed; this is not one-second astronomical accuracy. End is midnight UTC at the start of the supplied end date.'},
              'rules':[RULE], 'astronomical_samples':samples, 'astronomical_windows':windows,
              'biographical_predictions':[],
              'interpretation_status':'blocked_missing_sourced_and_versioned_rules'}
    canonical=json.dumps(record,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    return {'record':record,'sha256':hashlib.sha256(canonical.encode()).hexdigest(),
            'integrity_notice':'Reproducibility checksum only; not a server seal or proof of immutability.'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('profile');parser.add_argument('--start',required=True)
    parser.add_argument('--end',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args()
    with open(args.profile) as f: profile=json.load(f)
    result=calculate(profile,args.start,args.end)
    with open(args.out,'w') as f: json.dump(result,f,indent=2,ensure_ascii=False,allow_nan=False)
    print(f"Calculated 10 natal positions and {len(result['record']['astronomical_samples'])} geometric samples, {len(result['record']['astronomical_windows'])} windows. No life-event predictions generated.")
