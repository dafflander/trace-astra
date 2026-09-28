"""Deterministic editorial lookup. Does not calculate or validate ephemerides."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

LIBRARY = Path(__file__).parent / 'library.es.json'

def load_library():
    return json.loads(LIBRARY.read_text())

def natal_reading(chart):
    lib = load_library()
    sections = []
    accurate = chart.get('birth', {}).get('time_accuracy') == 'recorded'
    for p in chart['planets']:
        key = f"{p['id']}.{p['sign']}"
        sections.append({'rule_id':key,'kind':'sign',**lib['natal_signs'][key],
                         'evidence':{'body':p['id'],'longitude_deg':p['longitude_deg']}})
        if accurate and p.get('house'):
            key = f"{p['id']}.{p['house']}"
            sections.append({'rule_id':key,'kind':'house',**lib['natal_houses'][key],
                             'evidence':{'house':p['house'],'houses':chart['conventions']['houses']}})
    if accurate:
        for field,body in [('ascendant','Ascendant'),('midheaven','Midheaven')]:
            p=chart[field]; key=f"{body}.{p['sign']}"
            sections.append({'rule_id':key,'kind':'angle',**lib['natal_signs'][key], 'evidence':p})
    for a in sorted(chart['aspects'], key=lambda a:(a['orb_deg'],a['body_a'],a['body_b'])):
        keys=[f"{a['body_a']}.{a['body_b']}.{a['id']}",f"{a['body_b']}.{a['body_a']}.{a['id']}"]
        key=next((k for k in keys if k in lib['natal_aspects']),None)
        if key:
            sections.append({'rule_id':key,'kind':'aspect',**lib['natal_aspects'][key],
                             'evidence':{'separation_deg':a['separation_deg'],'orb_deg':a['orb_deg']}})
    return {'library_version':lib['version'],'notice':lib['notice'],
            'time_note':'Casas y ángulos omitidos si la hora no figura como registrada. Las demás posiciones conservan la incertidumbre del cálculo de entrada.',
            'sections':sections}

def temporal_reading(window):
    lib=load_library()
    rules=[r for r in lib['temporal_rules'] if all(r[k]==window.get(k) for k in ('transit_body','natal_body','aspect_deg'))]
    if not rules:
        raise ValueError('No editorial rule for this geometry')
    start,end,closest=(datetime.fromisoformat(window[k]) for k in ('entry_utc','exit_utc','closest_utc'))
    if not all(d.tzinfo for d in (start,end,closest)) or not start<=closest<=end:
        raise ValueError('Invalid dated window')
    orb=window['minimum_orb_deg']
    if not isinstance(orb,(int,float)) or not 0<=orb<=1:
        raise ValueError('Expected a finite orb within the current engine threshold')
    if window.get('entry_clipped',True) or window.get('exit_clipped',True):
        raise ValueError('Extend the scan before interpreting a clipped window')
    r=rules[0]
    result={'library_version':lib['version'],'rule':r,'evidence':dict(window),
            'evaluate_after_utc':(end+timedelta(days=r['evaluation_delay_days'])).isoformat(),
            'status':'experimental_unvalidated','notice':lib['notice']}
    result['content_id']=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
    return result


def anchor_readings(transit_record):
    """Explain only detected natal anchor links; no scoring or new geometry."""
    rules=load_library()['natal_anchor_rules']
    result=[]
    for link in transit_record['natal_interrelations']:
        for rule in rules:
            if ({rule['body_a'],rule['body_b']}=={link['body_a'],link['body_b']}
                    and rule['aspect_deg']==link['aspect_deg']):
                result.append({'rule_id':rule['id'],'text':rule['text'],'limit':rule['limit'],'evidence':link})
    return result
