"""Original deterministic reading aids; elemental counts are editorial, not psychometrics."""
ELEMENT_SIGNS={
 'Fuego':('Aries','Leo','Sagitario'),
 'Tierra':('Tauro','Virgo','Capricornio'),
 'Aire':('Géminis','Libra','Acuario'),
 'Agua':('Cáncer','Escorpio','Piscis'),
}
SIGN_ELEMENT={sign:element for element,signs in ELEMENT_SIGNS.items() for sign in signs}
ELEMENT_COPY={
 'Fuego':'Se asocia con entusiasmo, iniciativa y ganas de experimentar. Su imagen cotidiana es ponerse en marcha para descubrir qué es posible. El matiz a explorar es dar espacio a la preparación y escuchar antes de acelerar.',
 'Tierra':'Se asocia con constancia, sentido práctico y atención a lo tangible. Su imagen cotidiana es convertir una idea en pasos que puedan sostenerse. El matiz a explorar es permitir cambios cuando una rutina deja de ayudar.',
 'Aire':'Se asocia con curiosidad, comunicación y búsqueda de perspectivas. Su imagen cotidiana es comprender una situación conversando o comparando ideas. El matiz a explorar es pasar de las alternativas a una decisión concreta.',
 'Agua':'Se asocia con sensibilidad, memoria afectiva y atención a los vínculos. Su imagen cotidiana es reconocer cómo se siente una experiencia antes de decidir qué hacer. El matiz a explorar es expresar las necesidades y comprobar las suposiciones.',
}
BODY_GUIDE={
 'Sun':('Identidad y dirección','Al elegir un proyecto, el Sol invita a explorar qué parte responde a un deseo propio y qué parte a expectativas ajenas. No describe toda tu personalidad: ofrece un hilo para pensar qué quieres desarrollar.'),
 'Moon':('Emociones y necesidades','Después de un día exigente, la Luna invita a reconocer qué te ayuda a recuperar calma: compañía, descanso, una rutina o espacio a solas. La lectura propone una pregunta sobre tus necesidades, no un diagnóstico emocional.'),
 'Mercury':('Pensamiento y comunicación','Al aprender algo o explicar una diferencia, Mercurio invita a observar cómo ordenas la información, haces preguntas y eliges palabras. La posición no mide inteligencia ni determina tu capacidad para aprender.'),
 'Venus':('Afectos, gustos y valores','En una amistad, una relación o una elección cotidiana, Venus invita a distinguir lo que disfrutas y los gestos que valoras. Esa preferencia no decide con quién debes vincularte: los acuerdos se construyen entre personas.'),
 'Mars':('Iniciativa y límites','Cuando quieres empezar una tarea o decir que no, Marte invita a observar cómo pasas de la intención a la acción. Su lectura no predice agresividad; permite pensar cómo expresar un deseo o un límite con claridad.'),
 'Jupiter':('Aprendizaje y expansión','Ante una oportunidad, Júpiter invita a preguntar qué podrías aprender y qué recursos requiere. Ampliar perspectivas no equivale a tener suerte asegurada: también implica evaluar posibilidades y límites reales.'),
 'Saturn':('Responsabilidad y estructura','Al asumir un compromiso, Saturno invita a revisar plazos, obligaciones y lo que puedes sostener. La estructura puede ayudar a avanzar; esta posición no anuncia castigos ni dificultades inevitables.'),
 'Uranus':('Autonomía y cambio','Si una forma de hacer las cosas queda pequeña, Urano invita a imaginar alternativas y negociar el margen de autonomía. Su signo es compartido por muchas personas de una generación; la casa y los aspectos aportan contexto al mapa.'),
 'Neptune':('Imaginación y expectativas','En un proyecto creativo o una ilusión compartida, Neptuno invita a distinguir lo imaginado de lo acordado. No permite inferir engaños ni trastornos; propone contrastar expectativas con información concreta.'),
 'Pluto':('Transformación y control','Cuando revisas un hábito o un acuerdo importante, Plutón invita a preguntarte qué deseas conservar y qué estás dispuesto a cambiar. No anuncia pérdidas ni crisis: su interpretación es simbólica y generacional.'),
}

def overview(chart,lib):
 positions={p['id']:p for p in chart['planets']}
 counts={e:0 for e in ELEMENT_SIGNS};members={e:[] for e in ELEMENT_SIGNS}
 for body in BODY_GUIDE:
  p=positions.get(body)
  if not p:continue
  element=SIGN_ELEMENT[p['sign']];counts[element]+=1;members[element].append(p['name'])
 total=sum(counts.values());maximum=max(counts.values(),default=0)
 dominant=[e for e,n in counts.items() if n==maximum and maximum]
 sun=positions['Sun'];moon=positions.get('Moon');solar=SIGN_ELEMENT[sun['sign']]
 join=lambda xs:', '.join(xs[:-1])+' y '+xs[-1] if len(xs)>1 else (xs[0] if xs else '')
 summary=('En este recuento tiene más presencia '+dominant[0]+'.' if len(dominant)==1 else 'En este recuento comparten la mayor presencia '+join(dominant)+'.')
 element_paragraphs=[f"Tu signo solar, {sun['sign']}, pertenece a {solar.lower()}.",summary+' El elemento solar y el más representado en la carta pueden ser distintos. Ninguno define por sí solo quién eres.',
 'Contamos una vez cada uno de los diez cuerpos: Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno y Plutón. Cada uno vale un punto según su signo; no incluimos ascendente, medio cielo ni casas. Es una convención sencilla de TraceAstra, no un porcentaje de personalidad ni una medida científica.',
 'Una casilla con cero no significa que te falte esa cualidad. La distribución describe posiciones del mapa, no capacidades o carencias personales.']
 themes=lib['closing']['themes'];quick=[f"El Sol en {sun['sign']} pone el foco simbólico en {themes[sun['sign']]['theme']}. Para una primera lectura, esta es la dirección que la astrología asocia con tu manera de expresarte y con lo que buscas desarrollar."]
 if moon:quick.append(f"La Luna en {moon['sign']} añade el tema de {themes[moon['sign']]['theme']}: una mirada a lo que puede resultar importante al buscar bienestar emocional. Sol y Luna hablan de ámbitos distintos; expresar algo hacia afuera y necesitar algo por dentro no tiene por qué coincidir.")
 asc=chart.get('ascendant') if chart.get('birth',{}).get('time_accuracy')=='recorded' else None
 if asc:quick.append(f"El ascendente en {asc['sign']} completa este primer retrato con {themes[asc['sign']]['theme']}, aplicado al modo de empezar y presentarte. "+summary+' Lee esta combinación como un conjunto de temas para reconocer o cuestionar, no como una etiqueta fija sobre tu carácter.')
 else:quick.append(summary+' No incluimos el ascendente porque requiere una hora registrada. Este retrato simbólico puede servir para reflexionar; no determina tu carácter.')
 return {'version':'elements-1','title':'Tu carta en pocas palabras','paragraphs':quick,
         'elements':{'title':'Tus elementos','solar':solar,'counts':counts,'members':members,'total':total,'dominant':dominant,'descriptions':ELEMENT_COPY,'paragraphs':element_paragraphs}}

def deepen_sections(chart,sections,lib):
 for section in sections:
  if section['kind']!='natal':continue
  body=section['rule_ids'][0].split('.')[0]
  if body not in BODY_GUIDE:continue
  section['paragraphs'].append('En la vida cotidiana. '+BODY_GUIDE[body][1])
  aspects=sorted((a for a in chart.get('aspects',[]) if body in (a['body_a'],a['body_b'])),key=lambda a:(a['orb_deg'],a['body_a'],a['body_b']))
  if aspects:
   a=aspects[0];key=next((k for k in (f"{a['body_a']}.{a['body_b']}.{a['id']}",f"{a['body_b']}.{a['body_a']}.{a['id']}") if k in lib['natal_aspects']),None)
   if key:
    entry=lib['natal_aspects'][key]
    section['paragraphs'].append('Una relación que matiza esta posición. '+entry['title']+f" (orbe {a['orb_deg']:.2f}°). "+entry['paragraphs'][1]+' La explicación completa aparece en las relaciones entre posiciones. Elegimos aquí el aspecto de menor orbe para orientar la lectura; no significa que tenga mayor validez predictiva.')
    section['related_aspect']=key
