"""Extend the original rule set without inventing angle-specific life events."""
import json,copy
from pathlib import Path
from itertools import combinations
ROOT=Path(__file__).parent
CONTEXT={
 'Mercury':('un intercambio de información','El evento debe referirse a una conversación, documento o aprendizaje identificable.'),
 'Venus':('un acuerdo sobre preferencias compartidas','Debe tratarse de una actividad o acuerdo compartido, identificado antes de evaluar.'),
 'Mars':('una tarea con una acción concreta','Debe existir una tarea y una acción fechada, no solo intención.'),
 'Jupiter':('una actividad de aprendizaje organizada','Debe existir una actividad con un plan o programa, no consumo aislado de contenido.'),
 'Saturn':('una responsabilidad acordada','Debe existir un compromiso explícito con responsabilidades identificables.'),
 'Uranus':('un cambio en una organización habitual','Debe identificarse la organización anterior y el cambio concreto.'),
 'Neptune':('un proyecto creativo definido','Debe tratarse de un proyecto con una acción verificable, no una impresión o presentimiento.'),
 'Pluto':('la reorganización de un proyecto existente','Debe identificarse qué parte de un proyecto se reorganizó; no se infieren pérdidas, crisis ni daños.')}
def build():
 p=ROOT/'library.es.json';l=json.loads(p.read_text());base=[r for r in l['temporal_rules'] if r['natal_body'] in ('Sun','Moon','Ascendant')]
 expanded=list(base)
 for r in base:
  if r['natal_body']!='Sun':continue
  for target,(context,criterion) in CONTEXT.items():
   n=copy.deepcopy(r);n['id']=r['id'].replace('.Sun.',f'.{target}.',1) if r['transit_body']!='Sun' else r['id'].replace('temporal.Sun.Sun.','temporal.Sun.'+target+'.')
   n['id']=f"temporal.{r['transit_body']}.{target}.{r['aspect_deg']}.v3"
   n['natal_body']=target;n['event_family']=r['transit_body']+'.'+target
   for k in ('hypothesis','past','future'):n[k]=n[k].replace('un proyecto personal',context)
   n['counts']=[r['counts'][0],criterion]
   theme=l['natal_signs'][target+'.Aries']['text'].split(' representa ')[1].split('. En ')[0]
   n['interpretation']=f"El tránsito se compara con el tema natal de {theme}. La relación angular es {r['aspect_deg']}°. El escenario es una propuesta editorial, no una consecuencia demostrada de ese ángulo."
   expanded.append(n)
 for rule in expanded:rule['event_family']=rule['transit_body']
 l['temporal_rules']=expanded;l['version']='0.4.1'
 targets=['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto','Ascendant']
 anchors=[]
 for a,b in combinations(targets,2):
  for angle in (0,60,90,120,180):
   anchors.append({'id':f'anchors.{a}.{b}.{angle}.v2','body_a':a,'body_b':b,'aspect_deg':angle,'orb_deg':1,
    'text':f'Relación natal entre {a} y {b}, próxima a {angle}°. Conecta dos posiciones del mapa; no es una confirmación independiente de una hipótesis.',
    'limit':'Configuración natal; no aumenta una probabilidad predictiva.'})
 l['natal_anchor_rules']=anchors;p.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n')
 p=ROOT/'multisystem.es.json';m=json.loads(p.read_text());m['version']='trace-multisystem-es-0.2.0'
 names={'Sun':'Sol','Moon':'Luna','Mercury':'Mercurio','Venus':'Venus','Mars':'Marte','Jupiter':'Júpiter','Saturn':'Saturno','Rahu':'Rahu','Ketu':'Ketu'}
 for r in m['jyotisha']['rules']:
  major=m['jyotisha']['lords'][r['major']]['theme'];minor=m['jyotisha']['lords'][r['minor']]['theme']
  r['text']=f"Jyotisha organiza el tiempo en períodos y subperíodos. Aquí el período de {names[r['major']]} aporta el tema de {major}, y el subperíodo de {names[r['minor']]} enfoca {minor}. Las fechas describen ese calendario, no prueban acontecimientos."
  r['reading']=[r['text'],'Un período largo puede contener muchas experiencias distintas. No reducimos sus fechas para hacer coincidir un suceso ni lo sumamos como voto a favor de los tránsitos occidentales.',r['reflection']]
 m['bazi']['status']='four_pillars_and_solar_year_context'
 for r in m['bazi']['rules']:
  r['status']='editorial_context_not_event_forecast'
  r['limitation']='Compara elementos del tronco diario y anual. No evalúa fuerza estacional, troncos ocultos, combinaciones ni Da Yun; no es una predicción biográfica ni una lectura integral de todas las escuelas BaZi.'
  r['reading']=['BaZi organiza año, mes, día y hora en cuatro pares llamados pilares. El tronco del día sirve como referencia para esta comparación.',r['text'],r['reflection'],r['limitation']]
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':build(); from brand_voice import build as apply_voice; apply_voice()
