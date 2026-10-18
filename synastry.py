"""Two validated birth profiles, actual cross-chart geometry, transient processing."""
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from natal_request import calculate_request, InputError

LIBRARY = Path(__file__).parent / 'synastry.es.json'
NAMES={'Sun':'Sol','Moon':'Luna','Mercury':'Mercurio','Venus':'Venus','Mars':'Marte','Jupiter':'Júpiter','Saturn':'Saturno','Uranus':'Urano','Neptune':'Neptuno','Pluto':'Plutón','Ascendant':'Ascendente'}
ANGLES={0:'Conjunción',60:'Sextil',90:'Cuadratura',120:'Trígono',180:'Oposición'}


def compare_charts(first, second):
    lib=json.loads(LIBRARY.read_text())
    def points(c):
        result={p['id']:p for p in c['planets']}
        if c['birth'].get('time_accuracy')=='recorded':result['Ascendant']=c['ascendant']
        return result
    a,b=points(first),points(second)
    crossings=[]
    for x,p in a.items():
        for y,q in b.items():
            separation=abs((p['longitude_deg']-q['longitude_deg']+180)%360-180)
            for angle,label in ANGLES.items():
                orb=abs(separation-angle)
                if orb<=3:
                    crossings.append({'id':f'A.{x}.B.{y}.{angle}','a':x,'b':y,'angle':angle,'aspect':label,'orb':round(orb,4),'separation':round(separation,4),
                     'label':f'{NAMES[x]} de la primera carta / {NAMES[y]} de la segunda · {label} · orbe {orb:.2f}°'})
    crossings.sort(key=lambda c:(c['orb'],c['id']))
    sections=[]
    for category in lib['categories']:
        selected=[]
        for c in crossings:
            key='|'.join(sorted([c['a'],c['b']]))
            if key not in category['pairs']:continue
            tone='meeting' if c['angle'] in (0,60,120) else 'adjustment'
            rule=category['pairs'][key]
            selected.append({**c,'text':rule[tone],'rule_id':category['id']+'.'+key+'.'+tone})
        chosen=selected[:3]
        sections.append({'id':category['id'],'title':category['title'],
          'summary':chosen[0]['text'] if chosen else category['fallback'],
          'question':category['question'],'crossings':chosen})
    payload={'version':lib['version'],'notice':lib['notice'],'method':lib['method'],'sections':sections,
             'all_crossings':crossings,'profiles':[{'birth':c['birth'],'sun':c['planets'][0]['sign'],'moon':c['planets'][1]['sign'],'ascendant':c['ascendant']['sign']} for c in (first,second)]}
    payload['result_id']=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return payload


def calculate_comparison(body):
    if not isinstance(body,dict):raise InputError('Revisa los datos de ambas cartas.','form')
    charts=[]
    for key in ('first','second'):
        try:
            chart=calculate_request(body.get(key))
            born=datetime.fromisoformat(chart['birth']['local_datetime']).date()
            today=date.today();age=today.year-born.year-((today.month,today.day)<(born.month,born.day))
            if age<18:raise InputError('Esta comparación de vínculos está disponible para personas adultas.','date')
            charts.append(chart)
        except InputError as exc:raise InputError(exc.args[0],key+'.'+exc.field) from exc
    return compare_charts(*charts)
