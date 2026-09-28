"""Local candidate timeline. No persistence, AI, confidence score or causal claim."""
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from jyotisha import calculate

LIBRARY=Path(__file__).parent/'multisystem.es.json'

def load_library():return json.loads(LIBRARY.read_text())

def utc(value):
    d=datetime.fromisoformat(value)
    if d.tzinfo is None or d.utcoffset()!=timedelta(0):
        raise ValueError('UTC offset required')
    return d

def jyotisha_candidates(record,start_utc,end_utc):
    lib=load_library();first,last=utc(start_utc),utc(end_utc)
    if first>=last:raise ValueError('Nonempty ordered interval required')
    expected=lib['jyotisha']['conventions']
    if record.get('provider')!='jyotisha' or any(record.get('conventions',{}).get(k)!=v for k,v in expected.items()):
        raise ValueError('Unsupported provider or conventions')
    birth=utc(record['birth_profile']['utc'])
    periods=record['mahadashas']
    if first<birth or first<utc(periods[0]['start_utc']) or last>utc(periods[-1]['end_utc']):
        raise ValueError('Query outside available post-birth calendar')
    rules={(r['major'],r['minor']):r for r in lib['jyotisha']['rules']}
    candidates=[]
    for parent in periods:
        for sub in parent['antardashas']:
            a,b=utc(sub['start_utc']),utc(sub['end_utc'])
            if not utc(parent['start_utc'])<=a<b<=utc(parent['end_utc']):
                raise ValueError('Invalid subperiod containment')
            if a>=last or b<=first:continue
            rule=rules[parent['lord'],sub['lord']]
            clipped=a<first or b>last
            item={'system':'jyotisha','library_version':lib['version'],'engine_version':record['engine_version'],
                  'conventions':record['conventions'],'rule':rule,'start_utc':a.isoformat(),'end_utc':b.isoformat(),
                  'visible_start_utc':max(a,first).isoformat(),'visible_end_utc':min(b,last).isoformat(),
                  'clipped':clipped,'prebirth':a<birth,'eligible_for_review':not clipped and a>=birth,
                  'evaluate_after_utc':(b+timedelta(days=rule['evaluation_delay_days'])).isoformat(),
                  'status':'experimental_candidate','probability':None}
            # No generated-at timestamp: reproducibility hash, not a trusted seal.
            item['content_id']=hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            candidates.append(item)
    return candidates

def calculate_other_systems(profile,start_utc,end_utc):
    record=calculate(profile,year_days=365.25)
    return {'jyotisha':jyotisha_candidates(record,start_utc,end_utc),
            'unavailable':{'bazi':'Calendar conventions and full calculation pending; excluded from predictions.'},
            'notice':'Experimental editorial candidates. No automatic agreement score or independent confirmation.'}

def review_candidate(candidate,answer,as_of_utc,event_utc=None,criteria_confirmed=False):
    """Structured self-report. Does not independently verify a biography."""
    if answer not in ('Sí','No','No recuerdo','No aplica'):raise ValueError('Invalid answer')
    if not candidate['eligible_for_review']:raise ValueError('Full post-birth window required')
    now=utc(as_of_utc)
    if now<utc(candidate['evaluate_after_utc']):return {'status':'pending','scored':False}
    if answer in ('No recuerdo','No aplica'):return {'status':'unscored','scored':False}
    if answer=='No':return {'status':'self_reported_miss','scored':True}
    if not event_utc or criteria_confirmed is not True:raise ValueError('Dated event and all criteria required')
    when=utc(event_utc)
    if not utc(candidate['start_utc'])<=when<utc(candidate['end_utc']):
        return {'status':'outside_window','scored':True,'match':False}
    return {'status':'self_reported_match','scored':True,'match':True,'notice':'Self-report, not independent verification'}
