"""Reproducible enrichment of original TRACE editorial entries; no generated biography."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
# Every sign has an explicit everyday example and a counterpoint, shared transparently.
STYLES={
'Aries':('iniciativa y rapidez','dar un primer paso sin esperar a tener resueltos todos los detalles','acordar qué necesita preparación antes de actuar'),
'Tauro':('continuidad y estabilidad','sostener una rutina o un acuerdo que resulta valioso','dejar espacio para cambiar una costumbre cuando ya no ayuda'),
'Géminis':('curiosidad e intercambio','comparar alternativas y conversar para entenderlas','elegir una opción y darle continuidad'),
'Cáncer':('cuidado y pertenencia','preguntar qué necesita alguien para sentirse acompañado','expresar las necesidades propias sin suponer que son evidentes'),
'Leo':('expresión y reconocimiento','compartir una creación y reconocer el aporte de otros','dejar espacio para que las demás personas también se expresen'),
'Virgo':('análisis y mejora','revisar un detalle y proponer una mejora concreta','distinguir una mejora útil de una corrección que puede esperar'),
'Libra':('cooperación y equilibrio','escuchar dos propuestas antes de buscar un acuerdo','decidir sin exigir una opción perfecta para todos'),
'Escorpio':('profundidad y reserva','dedicar tiempo a una conversación importante y respetar lo privado','preguntar antes de interpretar lo que otra persona calla'),
'Sagitario':('exploración y sentido','aprender algo nuevo y relacionarlo con una perspectiva más amplia','contrastar una explicación general con los detalles del caso'),
'Capricornio':('organización y persistencia','dividir un proyecto en compromisos que se puedan cumplir','revisar un plan cuando cambian las circunstancias'),
'Acuario':('independencia y perspectiva colectiva','proponer una alternativa y conservar espacio para el criterio propio','explicar cómo esa alternativa afecta a quienes participan'),
'Piscis':('sensibilidad e imaginación','usar música, escritura o imágenes para dar forma a una experiencia','poner en palabras lo que se necesita y comprobar los hechos')}
BODIES={
'Sun':('Tu identidad y tus objetivos','El Sol se utiliza para hablar de lo que buscas desarrollar y expresar.','elegir un proyecto que quieras sostener por decisión propia'),
'Moon':('Lo que te ayuda a recuperar calma','La Luna se utiliza para explorar necesidades emocionales y formas de recuperar calma.','distinguir si necesitas compañía, descanso o tiempo a solas'),
'Mercury':('Cómo elaboras y compartes ideas','Mercurio representa pensamiento, aprendizaje y comunicación.','preparar lo que quieres decir antes de una conversación'),
'Venus':('Lo que valoras en tus vínculos','Venus representa preferencias, afecto y aquello que se valora al compartir tiempo.','hablar de qué gestos y acuerdos hacen agradable un vínculo'),
'Mars':('De la intención a la acción','Marte representa iniciativa y la manera de plantear límites.','definir una primera tarea y aclarar hasta dónde puedes comprometerte'),
'Jupiter':('Aprender y ampliar perspectivas','Júpiter representa aprendizaje y expansión dentro de esta tradición.','explorar una oportunidad y revisar qué permite aprender'),
'Saturn':('Compromisos que puedes sostener','Saturno representa estructura, responsabilidades y compromisos.','acordar responsabilidades y plazos realistas'),
'Uranus':('Tu espacio para cambiar','Urano representa autonomía y cambios.','revisar un acuerdo que necesita más margen de decisión'),
'Neptune':('Dar forma a lo que imaginas','Neptuno representa imaginación e ideales.','distinguir una expectativa de un compromiso hablado'),
'Pluto':('Qué conservar y qué transformar','Plutón se asocia con control y transformación.','revisar qué quieres conservar en un proyecto y qué aceptarías cambiar'),
'Ascendant':('Cómo das el primer paso','El ascendente es el punto del zodíaco que aparece por el horizonte oriental. En astrología se asocia con cómo empiezas y te presentas.','observar cómo abordas una situación desconocida'),
'Midheaven':('Tu actividad ante los demás','El medio cielo es un punto del mapa asociado con la proyección pública. No determina una profesión ni garantiza éxito.','definir qué parte de un trabajo quieres hacer visible')}
HOUSES={
1:('presencia e iniciativa','empezar algo propio o presentarte ante un grupo'),2:('recursos propios','organizar el tiempo y los recursos de los que dispones'),3:('comunicación cotidiana','explicar una idea o coordinar una tarea cercana'),4:('hogar y raíces','conversar sobre la organización del espacio que habitas'),5:('expresión y disfrute','reservar tiempo para una actividad creativa'),6:('rutinas y tareas','repartir tareas y revisar cómo organizas el día'),7:('acuerdos entre dos personas','aclarar qué espera cada parte de una colaboración'),8:('recursos compartidos','acordar cómo repartir un gasto o una responsabilidad común'),9:('aprendizaje y perspectivas','estudiar un tema que amplíe tu manera de entenderlo'),10:('actividad pública','presentar un trabajo o asumir una tarea visible'),11:('grupos y proyectos','coordinar una iniciativa con amistades o colegas'),12:('retiro y privacidad','ordenar ideas a solas antes de compartirlas')}
ASPECTS={
'conjunction':('cercanía','La conjunción reúne posiciones cercanas. La tradición propone leer sus temas juntos, sin asumir que esa unión sea siempre fácil.','distinguir qué aporta cada tema cuando aparecen juntos'),
'sextile':('colaboración posible','El sextil es un ángulo cercano a 60°. Se interpreta como una posibilidad de colaboración entre temas, no como una ventaja garantizada.','buscar una acción concreta que permita relacionar ambos temas'),
'square':('necesidades que requieren ajuste','La cuadratura es un ángulo cercano a 90°. Se interpreta como tensión entre temas que requieren ajustes, no como un anuncio de problemas.','aclarar qué necesita cada tema antes de elegir cómo actuar'),
'trine':('facilidad para conectar temas','El trígono es un ángulo cercano a 120°. Se interpreta como facilidad para conectar temas, sin demostrar una habilidad personal.','observar si esa facilidad propuesta se traduce en alguna práctica concreta'),
'opposition':('perspectivas que necesitan espacio','La oposición es un ángulo cercano a 180°. Se interpreta como una polaridad: dos temas que conviene considerar sin eliminar uno de ellos.','dar espacio a ambas prioridades al formular un acuerdo')}
def upgrade():
 l=json.loads((ROOT/'library.es.json').read_text())
 l['version']=l.get('version','0.3.0')
 l['reading_notice']='Las posiciones se calculan; las interpretaciones son asociaciones astrológicas, no conclusiones comprobadas sobre tu personalidad ni predicciones demostradas. Los ejemplos ilustran conceptos: no son hechos deducidos de tu vida.'
 for key,e in l['natal_signs'].items():
  body,sign=key.split('.');title,meaning,example=BODIES[body];theme,action,balance=STYLES[sign]
  e['heading']=title
  e['paragraphs']=[meaning,f'En {sign}, TraceAstra interpreta este tema desde {theme}. Una manera cotidiana de entenderlo es {action}.',f'Aplicado a este elemento, el ejemplo sería {example}. El contrapunto para explorar es {balance}.']
 for key,e in l['natal_houses'].items():
  body,house=key.split('.');area,example=HOUSES[int(house)]
  e['paragraphs']=[f'La casa {house} sitúa esta interpretación en el ámbito de {area}. Las casas son doce divisiones del mapa calculadas a partir de la hora, el lugar y el sistema elegido.',f'En ese ámbito, un ejemplo sería {example}. Esto indica dónde enfoca el tema la lectura astrológica; no confirma experiencias pasadas ni anuncia acontecimientos.']
 for key,e in l['natal_aspects'].items():
  a,b,kind=key.split('.');label,definition,action=ASPECTS[kind]
  e['paragraphs']=[definition,e['text'],f'Para entender la relación en la vida cotidiana, puedes {action}. No basta con el ángulo para saber cómo actúa una persona.']
 # A reusable, versioned compatibility guide: 4 anchors x 12 natal signs x 12 comparison signs.
 l['compatibility']={'notice':'Guía editorial por signos solares, no comparación de dos cartas. No calcula aspectos entre personas ni asigna porcentajes. La calidad de una relación depende de cómo se tratan sus integrantes.','anchors':['Sun','Moon','Mercury','Venus'],'rules':{}}
 for body in l['compatibility']['anchors']:
  for natal,(theme,action,balance) in STYLES.items():
   for other,(otheme,oaction,obalance) in STYLES.items():
    same=natal==other
    paragraphs=[f'En esta dimensión, {natal} aporta el tema de {theme}. '+(f'La guía solar de {other} repite ese tema; compartir un signo no demuestra una conexión entre dos cartas.' if same else f'La guía solar de {other} propone {otheme}. Son temas para comparar, no descripciones de la otra persona.'),f'Un ejemplo para conversar: {action}'+('.' if same else f', dejando también espacio para {oaction}.'),f'La diferencia o el punto a cuidar: {balance}. '+('Evita suponer que una coincidencia de signo implica necesidades idénticas.' if same else f'Para la otra perspectiva, la guía propone {obalance}.')]
    l['compatibility']['rules'][f'{body}.{natal}.{other}']={'title':BODIES[body][0],'paragraphs':paragraphs,'reading':f'{theme.capitalize()} y {otheme}: '+('el tema coincide, pero eso no implica necesidades idénticas. ' if same else 'dos perspectivas para explorar. ')+f'Un ejemplo compartido sería {BODIES[body][2]}. El punto a cuidar desde tu posición: {balance}.'}
 l['reading_glossary']={'Signo':'Sector de 30° del zodíaco tropical. No resume por sí solo a una persona.','Grados':'Posición dentro del signo, expresada en grados decimales: 24,07° no equivale a 24 grados y 7 minutos.','Casa':'División del mapa asociada con un ámbito de experiencia. Depende de la hora, el lugar y el método.','Aspecto':'Relación angular entre posiciones; no representa una conexión física.','Orbe':'Distancia al ángulo exacto. Menor orbe significa mayor cercanía angular, no mayor certeza predictiva.'}
 (ROOT/'library.es.json').write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':upgrade(); from brand_voice import build as apply_voice; apply_voice()
