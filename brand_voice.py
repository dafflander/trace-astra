"""Original TraceAstra voice and deterministic closing, not author imitation."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
THEMES={
'Aries':('iniciativa para comenzar','elegir un primer paso que puedas dar hoy'),
'Tauro':('continuidad para sostener lo valioso','cuidar un acuerdo con una acción concreta'),
'Géminis':('curiosidad para abrir caminos','elegir una idea y darle forma'),
'Cáncer':('cuidado y sentido de pertenencia','poner en palabras una necesidad de cuidado'),
'Leo':('expresión y reconocimiento','compartir algo propio y escuchar la respuesta'),
'Virgo':('atención para mejorar los detalles','hacer una mejora pequeña y útil'),
'Libra':('cooperación para construir acuerdos','hablar de lo que ambas partes necesitan'),
'Escorpio':('profundidad para explorar lo importante','dedicar tiempo a una conversación pendiente'),
'Sagitario':('apertura para ampliar perspectivas','convertir una pregunta en una oportunidad de aprender'),
'Capricornio':('organización para dar continuidad','elegir un compromiso que puedas sostener'),
'Acuario':('autonomía y perspectiva compartida','proponer una alternativa y escuchar cómo afecta a otros'),
'Piscis':('sensibilidad e imaginación','dar forma a una emoción mediante palabras o una actividad creativa')}
def build():
 for name in ['library.es.json','multisystem.es.json']:
  path=ROOT/name;data=json.loads(path.read_text())
  def replace(v):
   if isinstance(v,str):return v.replace('TRACE ASTRA','TraceAstra').replace('la biblioteca interpreta','TraceAstra interpreta').replace('Biblioteca editorial original de TRACE.','TraceAstra presenta esta lectura original.').replace('En esta ficha de elementos,','En esta lectura,')
   if isinstance(v,list):return [replace(x) for x in v]
   if isinstance(v,dict):return {k:replace(x) for k,x in v.items()}
   return v
  data=replace(data)
  if name=='library.es.json':
   data['version']='0.4.2'
   data['closing']={'title':'Una mirada para seguir','themes':{k:{'theme':v[0],'action':v[1]} for k,v in THEMES.items()},
    'temporal':{'past':{'ready':'Al mirar hacia atrás, las ventanas propuestas exploran {topics}. Revisa lo que ocurrió y deja espacio también para lo que no coincide: reconocer una diferencia es tan importante como encontrar una semejanza.',
                        'empty':'En el período pasado consultado no se seleccionaron ventanas completas. Tu historia conserva su valor aunque este método no encuentre una hipótesis para ella.',
                        'unavailable':'La revisión del pasado no está incluida todavía. No hace falta llenar ese espacio con una interpretación: podrás retomarlo cuando el cálculo esté disponible.'},
                'future':{'ready':'Hacia adelante, las hipótesis incluidas se refieren a {topics}. Consérvalas como preguntas fechadas para contrastar, sin convertirlas en obligaciones ni certezas sobre lo que vendrá.',
                          'empty':'En el período futuro consultado no se seleccionaron ventanas completas. Eso no limita lo que puedas emprender ni significa que no vaya a ocurrir nada.',
                          'unavailable':'La parte futura no está incluida todavía. Mientras se completa, la lectura natal puede servir como una invitación a observar y decidir, sin anticipar acontecimientos.'}},
    'last_line':'Tu carta es un punto de partida. Lo que sigue también se construye con tus decisiones.'}
  path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':build()
