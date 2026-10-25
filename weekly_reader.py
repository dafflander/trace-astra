"""Weekly beta: bounded sampled geometry and deterministic editorial composition.
No storage, probabilities, or predicted biographical events.
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import hashlib
import json
from engine import position, separation

from weekly_editorial import VERSION, PAIRS, TITLES, OPENINGS, ASPECT_NOTES, TARGET_LABELS, ENDINGS
# Own editorial vocabulary; every selected passage retains its geometric evidence.
BODIES={
 'Sun':('Sol','Elegir una prioridad','La expresión personal invita a distinguir qué merece tu atención.','Elige una tarea propia y reserva un momento concreto para ella.'),
 'Moon':('Luna','Encontrar tu ritmo','Las necesidades cotidianas ofrecen una ocasión para observar tu ritmo.','Antes de una tarea, decide cuándo quieres hacer una pausa.'),
 'Mercury':('Mercurio','Aclarar lo esencial','La comunicación y la organización invitan a separar lo principal de los detalles.','Revisa un mensaje pendiente y escribe primero qué necesitas preguntar.'),
 'Venus':('Venus','Compartir con intención','Los gustos y los acuerdos ofrecen un tema para explorar en tus vínculos.','Expresa una preferencia sencilla sobre un plan compartido.'),
 'Mars':('Marte','Un comienzo acotado','La iniciativa puede servir como tema para dar forma a algo elegido por ti.','Dedica veinte minutos al primer paso de una tarea, sin exigirte terminarla.'),
 'Jupiter':('Júpiter','Ampliar una pregunta','El aprendizaje invita a explorar una opción sin dar por cierta la primera explicación.','Consulta una fuente adicional sobre una pregunta que te interese.'),
 'Saturn':('Saturno','Acuerdos sostenibles','Los compromisos ofrecen un tema para revisar el tiempo y los límites disponibles.','Distingue lo que puedes ofrecer hoy de lo que necesita otra fecha.'),
 'Uranus':('Urano','Probar otra manera','La autonomía y la revisión de hábitos invitan a considerar una alternativa.','Prueba un cambio pequeño y reversible en una rutina elegida por ti.'),
 'Neptune':('Neptuno','Dar forma a una idea','La imaginación invita a distinguir una posibilidad de lo que ya has comprobado.','Anota una idea y la información que necesitarías para darle forma.'),
 'Pluto':('Plutón','Revisar lo importante','La revisión profunda ofrece un tema para observar qué quieres seguir sosteniendo.','Elige un compromiso y examina qué parte está realmente en tus manos.')}
TARGETS={
 'Sun':('Sol','tus prioridades personales','¿Qué merece un lugar propio en tu semana?'),
 'Moon':('Luna','tus necesidades cotidianas','¿Qué haría tu semana más cómoda?'),
 'Mercury':('Mercurio','tu manera de explicar y organizar ideas','¿Qué necesitas aclarar antes de continuar?'),
 'Venus':('Venus','tus preferencias y acuerdos','¿Qué te gustaría expresar con más claridad?'),
 'Mars':('Marte','tu manera de empezar y poner límites','¿Qué primer paso tiene un alcance realista?'),
 'Ascendant':('Ascendente','tu manera de presentarte y empezar','¿Cómo quieres dar ese primer paso?')}
ASPECTS={0:('conjunción','Estos temas se reúnen en la interpretación; puedes observarlos juntos.'),60:('sextil','La propuesta es explorar cómo articular ambos temas mediante una iniciativa pequeña.'),90:('cuadratura','Puedes explorar una diferencia de ritmos o prioridades sin dar por hecho que exista un problema.'),120:('trígono','La propuesta es buscar continuidad entre ambos temas, sin esperar resultados garantizados.'),180:('oposición','La propuesta es dar lugar a ambas prioridades sin obligarte a elegir una sola.')}
SLOW={'Jupiter','Saturn','Uranus','Neptune','Pluto'}

def week_bounds(zone,now=None):
    tz=ZoneInfo(zone)
    local=(now or datetime.now(timezone.utc)).astimezone(tz)
    monday=local.date()-timedelta(days=local.weekday())
    start=datetime.combine(monday,datetime.min.time(),tzinfo=tz)
    end=datetime.combine(monday+timedelta(days=7),datetime.min.time(),tzinfo=tz)
    return start,end

def calculate_weekly(chart,zone='UTC',now=None):
    start,end=week_bounds(zone,now)
    first,last=start.astimezone(timezone.utc),end.astimezone(timezone.utc)
    if datetime.fromisoformat(chart['birth']['utc'])>=first:
        raise ValueError('La semana debe ser posterior al nacimiento.')
    targets={p['id']:p['longitude_deg'] for p in chart['planets'] if p['id'] in TARGETS}
    if chart['birth'].get('time_accuracy')=='recorded':targets['Ascendant']=chart['ascendant']['longitude_deg']
    candidates=[]
    for body in BODIES:
        step=timedelta(hours=1 if body=='Moon' else 6)
        best={};t=first
        while t<last:
            longitude=position(t,body)['longitude_deg']
            for target,value in targets.items():
                distance=separation(longitude,value)
                for angle in ASPECTS:
                    orb=abs(distance-angle)
                    key=(target,angle)
                    if orb<=1 and (key not in best or orb<best[key][0]):best[key]=(orb,t)
            t+=step
        for (target,angle),(orb,t) in best.items():
            candidates.append(dict(body=body,target=target,angle=angle,orb_deg=round(orb,5),sample_utc=t.isoformat()))
    # Editorial order, never a probability or strength score. At most one slow context.
    candidates.sort(key=lambda c:(c['body']=='Moon',c['body'] in SLOW,c['orb_deg'],c['body'],c['target'],c['angle']))
    chosen=[];used_bodies=set();used_targets=set();slow=False
    for c in candidates:
        if c['body'] in used_bodies or c['target'] in used_targets or (slow and c['body'] in SLOW):continue
        chosen.append(c);used_bodies.add(c['body']);used_targets.add(c['target']);slow|=c['body'] in SLOW
        if len(chosen)==3:break
    cards=[]
    for c in chosen:
        name,title,copy,action=BODIES[c['body']];target,theme,question=TARGETS[c['target']];aspect,nuance=ASPECTS[c['angle']]
        cards.append(dict(title=TARGET_LABELS[c['target']],text=PAIRS[c['body']+'.'+c['target']]+' '+ENDINGS[c['angle']],action=action,question=question,aspect_note=ASPECT_NOTES[c['angle']],
          context='Contexto de ritmo lento: puede continuar durante otras semanas.' if c['body'] in SLOW else 'Contacto breve: no describe necesariamente los siete días.' if c['body']=='Moon' else 'Tema seleccionado para esta semana.',
          evidence=f'{name} en {aspect} a {target} natal',rule_id=f"weekly.{c['body']}.{c['target']}.{c['angle']}.v2",**c))
    summary=OPENINGS[chosen[0]['body']] if chosen else 'Esta semana no encontramos contactos destacados dentro del criterio de esta lectura. Esto no significa que no vaya a pasar nada. Puedes volver a tu carta natal para explorar sus temas generales.'
    result=dict(version=VERSION,start=start.date().isoformat(),end=(end.date()-timedelta(days=1)).isoformat(),timezone=zone,headline=TITLES[chosen[0]['body']] if chosen else 'Una semana abierta.',summary=summary,cards=cards,
      notice='Una lectura simbólica para explorar, no una certeza. No garantiza acontecimientos ni sustituye asesoramiento médico, psicológico, legal o financiero.',
      method='Beta sin IA. Contactos con orbe de hasta 1°. Muestreo cada hora para la Luna y cada seis horas para los demás cuerpos. La fecha mostrada es la muestra más cercana detectada, no la hora exacta del aspecto ni el inicio o final de su ventana. El muestreo puede omitir contactos breves. Se seleccionan hasta tres temas; el orbe no mide probabilidad ni impacto personal.')
    result['content_id']=hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return result
