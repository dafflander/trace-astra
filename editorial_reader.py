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


def integrated_reading(chart):
    """One versioned reading for the browser, offline export and PDF.

    Natal aspects are included once, in a dedicated group. Compatibility is
    thematic, not synastry. Missing/uncertain angles and houses are not inferred.
    """
    lib=load_library(); sections=[]
    accurate=chart.get('birth',{}).get('time_accuracy')=='recorded'
    positions={p['id']:p for p in chart['planets']}
    def position_label(name,p,house=False):
        label=f"{name} en {p['sign']} · {p['degree_in_sign']:.2f}°"
        if house and accurate and p.get('house'):label+=f" · Casa {p['house']}"
        return label
    for p in chart['planets']:
        key=f"{p['id']}.{p['sign']}";entry=lib['natal_signs'][key]
        paragraphs=list(entry['paragraphs']);refs=[key];evidence=[position_label(p['name'],p,True)]
        if accurate and p.get('house'):
            hk=f"{p['id']}.{p['house']}";refs.append(hk)
            # Define houses once in the shared glossary; keep each section focused.
            paragraphs.append(lib['natal_houses'][hk]['paragraphs'][0].split(' Las casas son')[0])
            paragraphs.append(lib['natal_houses'][hk]['paragraphs'][1].split(' Esto indica')[0])
        if p['id']=='Sun' and accurate and chart.get('ascendant',{}).get('sign')==p['sign']:
            asc=chart['ascendant'];refs.append('Ascendant.'+asc['sign']);evidence.append(position_label('Ascendente',asc))
            paragraphs.append('El ascendente representa cómo empiezas y te presentas. Aparece en el mismo signo que el Sol, por lo que reunimos su tema aquí sin repetir una segunda descripción. No son dos pruebas independientes sobre tu personalidad.')
        if p['id'] in ('Uranus','Neptune','Pluto'):
            paragraphs.append('Este cuerpo se mueve lentamente: muchas personas nacidas en años próximos comparten el signo. Esta asociación por signo no es exclusiva de tu carta.')
        sections.append({'kind':'natal','title':entry['heading'],'evidence':evidence,'paragraphs':paragraphs,'rule_ids':refs})
    if accurate:
        for field,body,name in [('ascendant','Ascendant','Ascendente'),('midheaven','Midheaven','Medio cielo')]:
            p=chart.get(field)
            if not p:continue
            if body=='Ascendant' and positions.get('Sun',{}).get('sign')==p['sign']:continue
            key=f"{body}.{p['sign']}";entry=lib['natal_signs'][key]
            sections.append({'kind':'natal','title':entry['heading'],'evidence':[position_label(name,p)],'paragraphs':list(entry['paragraphs']),'rule_ids':[key]})
    for a in sorted(chart.get('aspects',[]),key=lambda x:(x['orb_deg'],x['body_a'],x['body_b'])):
        key=next((k for k in (f"{a['body_a']}.{a['body_b']}.{a['id']}",f"{a['body_b']}.{a['body_a']}.{a['id']}") if k in lib['natal_aspects']),None)
        if not key:continue
        entry=lib['natal_aspects'][key]
        sections.append({'kind':'aspect','title':entry['title'],'evidence':[f"Separación {a['separation_deg']:.2f}° · Orbe {a['orb_deg']:.2f}°"],'paragraphs':entry['paragraphs'],'rule_ids':[key]})
    signs=list(dict.fromkeys(k.split('.')[1] for k in lib['natal_signs']))
    for sign in signs:
        paragraphs=[];evidence=[];refs=[]
        for body in lib['compatibility']['anchors']:
            p=positions.get(body)
            if not p:continue
            key=f"{body}.{p['sign']}.{sign}";rule=lib['compatibility']['rules'][key]
            evidence.append(position_label(p['name'],p)+' ↔ guía solar de '+sign)
            paragraphs.append(rule['title']+'. '+rule['reading'])
            refs.append(key)
        sections.append({'kind':'compatibility','title':'Afinidades con '+sign,'evidence':evidence,'paragraphs':paragraphs,'rule_ids':refs})
    if chart.get('bazi') and accurate:
        bazi=chart['bazi'];labels={'year':'Año','month':'Mes','day':'Día','hour':'Hora'}
        evidence=[labels[k]+': '+v['label']+' · '+v['element']+' '+v['polarity'] for k,v in bazi['pillars'].items()]
        sections.append({'kind':'bazi','title':'Tu nacimiento en el calendario BaZi','evidence':evidence,
          'paragraphs':['BaZi organiza año, mes, día y hora en cuatro pares llamados pilares. Cada par combina un tronco y una rama; no son posiciones planetarias ni otra prueba de las hipótesis occidentales.',
          'El tronco del día, llamado Day Master, es '+bazi['day_master']['stem']+' ('+bazi['day_master']['element']+', '+bazi['day_master']['polarity']+'). Es la referencia de la comparación elemental anual que aparece en tus períodos.',
          'Usamos hora civil local, cambio de día a medianoche y cambio anual en Li Chun (Sol a 315°). A las 23 h el tronco horario usa el día siguiente. No aplicamos corrección de hora solar ni invertimos las estaciones en el hemisferio sur.',
          'Este módulo calcula cuatro pilares y contexto elemental anual. No incluye fuerza estacional, troncos ocultos ni ciclos Da Yun; no equivale a una lectura exhaustiva de BaZi ni pronostica hechos personales.'],
          'rule_ids':['bazi.calendar.civil-midnight.v1']})
    return {'version':lib['version'],'notice':lib['reading_notice'],
            'compatibility_notice':lib['compatibility']['notice'],
            'time_note':'Casas y ángulos requieren una hora registrada; se omiten si la hora es incierta.',
            'sections':sections,'glossary':lib['reading_glossary'],'closing':closing_for_chart(chart,lib)}


def closing_for_chart(chart,lib):
    config=lib['closing'];positions={p['id']:p for p in chart['planets']}
    chosen=[positions[k] for k in ('Sun','Moon','Venus') if k in positions]
    signs=list(dict.fromkeys(p['sign'] for p in chosen))
    themes=[config['themes'][s]['theme'] for s in signs]
    actions=[config['themes'][s]['action'] for s in signs]
    join=lambda xs: ', '.join(xs[:-1])+' y '+xs[-1] if len(xs)>1 else (xs[0] if xs else '')
    evidence=[p['name']+' en '+p['sign'] for p in chosen]
    paragraphs=[]
    if themes:paragraphs.append('En esta lectura, TraceAstra reúne '+join(themes)+'. Estos temas parten de '+join(evidence)+'. La pregunta que deja este recorrido es qué lugar quieres darles en tus decisiones cotidianas.')
    paragraphs.append('No necesitas resolverlo todo hoy. Puedes '+join(actions)+'. Son posibilidades para explorar, no obligaciones que tu carta imponga.' if actions else 'No necesitas resolverlo todo hoy. La lectura puede abrir preguntas; las decisiones siguen siendo tuyas.')
    paragraphs.append('Las afinidades ofrecen temas para conversar, no etiquetas para elegir o descartar personas. El vínculo se construye en lo que cada uno hace, escucha y acuerda.')
    return {'title':config['title'],'paragraphs':paragraphs,'temporal':config['temporal'],'last_line':config['last_line']}


def closing_paragraphs(reading,periods=None):
    closing=reading['closing'];paragraphs=list(closing['paragraphs'])
    for period in periods or []:
        cards=(period.get('timeline') or {}).get('cards',[])
        state='unavailable' if period.get('status')!='ready' else ('ready' if cards else 'empty')
        topics=list(dict.fromkeys(c['title'] for c in cards))
        summary=', '.join(topics[:-1])+' y '+topics[-1] if len(topics)>1 else (topics[0] if topics else '')
        paragraphs.append(closing['temporal'][period['kind']][state].replace('{topics}',summary))
    return [*paragraphs,closing['last_line']]
