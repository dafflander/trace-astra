"""Expanded, opt-in geometric detector; no inferred life events."""
import hashlib
import json
from datetime import date, datetime, timezone
from itertools import combinations
import swisseph as swe
from engine import BODIES, normalize, position, julian, separation
from temporal import find_windows
from ephemeris_cache import transit_longitude

ANGLES=(0,60,90,120,180)
TARGETS=(*BODIES,'Ascendant')
VERSION='trace-transits-0.2.0'

def calculate_transits(profile,start,end):
    birth=normalize(profile)
    if abs(birth['latitude'])>=66:
        raise ValueError('Ascendant pilot requires latitude below 66 degrees')
    first=datetime.combine(date.fromisoformat(start),datetime.min.time(),tzinfo=timezone.utc)
    last=datetime.combine(date.fromisoformat(end),datetime.min.time(),tzinfo=timezone.utc)
    if not (1900<=first.year<=2100 and 1900<=last.year<=2100) or not 0<(last-first).days<=730:
        raise ValueError('Ordered interval of 1 to 730 days required within 1900–2100')
    swe.set_ephe_path('')
    at=datetime.fromisoformat(birth['utc'])
    if first<at:raise ValueError('Temporal interval must follow birth')
    targets={b:position(at,b)['longitude_deg'] for b in BODIES}
    _,angles=swe.houses_ex(julian(at),birth['latitude'],birth['longitude'],b'P',0)
    targets['Ascendant']=angles[0]
    windows=[]
    for body in BODIES:
        cache={}
        def longitude(t):
            if t not in cache:cache[t]=transit_longitude(t,body,step)
            return cache[t]
        # The Moon can cross the full two-degree band in a few hours.
        step=1 if body=='Moon' else 6
        for target,value in targets.items():
            for angle in ANGLES:
                def orb(t):return abs(separation(longitude(t),value)-angle)
                for w in find_windows(orb,first,last,threshold=1,step_hours=step):
                    w.update(transit_body=body,natal_body=target,aspect_deg=angle,
                             natal_longitude_deg=value,
                             transit_longitude_at_closest_deg=longitude(datetime.fromisoformat(w['closest_utc'])),
                             rule_id=f'geometry.{body}.{target}.{angle}',rule_version=1)
                    w['window_id']=hashlib.sha256(json.dumps(w,sort_keys=True).encode()).hexdigest()
                    windows.append(w)
    windows.sort(key=lambda w:(w['entry_utc'],w['transit_body'],w['natal_body'],w['aspect_deg']))
    natal_links=[]
    for a,b in combinations(TARGETS,2):
        distance=separation(targets[a],targets[b])
        for angle in ANGLES:
            if abs(distance-angle)<=1:
                natal_links.append(dict(body_a=a,body_b=b,aspect_deg=angle,orb_deg=abs(distance-angle)))
    record=dict(engine_version=VERSION,provider={'name':'Swiss Ephemeris','version':swe.version,'backend':'Moshier','frame':'geocentric tropical','time':'UTC approximated as UT'},
                natal_targets=targets,natal_interrelations=natal_links,
                scan={'start_utc':first.isoformat(),'end_utc':last.isoformat(),'end_policy':'Midnight at start of end date','orb_deg':1,'moon_step_hours':1,'other_step_hours':6,'limitation':'Finite grid can miss grazing contacts. Numerical refinement is not physical accuracy.'},
                astronomical_windows=windows,overlap_groups=group_overlaps(windows),biographical_predictions=[])
    return {'record':record,'sha256':hashlib.sha256(json.dumps(record,sort_keys=True,allow_nan=False).encode()).hexdigest()}

def group_overlaps(windows):
    """Connected overlaps per transit body; grouping is not independent evidence."""
    groups=[]
    for body in BODIES:
        ordered=sorted((w for w in windows if w['transit_body']==body),key=lambda w:datetime.fromisoformat(w['entry_utc']))
        current=[];finish=None
        for w in ordered:
            start=datetime.fromisoformat(w['entry_utc']);end=datetime.fromisoformat(w['exit_utc'])
            if current and start>finish:
                groups.append({'transit_body':body,'window_ids':current});current=[];finish=None
            current.append(w['window_id']);finish=max(finish,end) if finish else end
        if current:groups.append({'transit_body':body,'window_ids':current})
    return groups
