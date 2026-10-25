"""Original weekly beta copy. Pair-specific scenes, not asserted life events."""
VERSION='weekly-editorial-2'
# Columns: Sun, Moon, Mercury, Venus, Mars, Ascendant.
TARGET_ORDER=('Sun','Moon','Mercury','Venus','Mars','Ascendant')
PAIR_TEXT={
'Sun':(
 'Una agenda llena puede dejar poco espacio para lo que tú querías hacer. Elige algo que seguiría importándote aunque nadie lo viera.',
 'Puedes querer estar presente para otros y necesitar un rato a solas. Antes de llenar un hueco de la agenda, pregúntate qué te vendría bien.',
 'Si tienes una idea que explicar, empieza por la frase que quieres que recuerden. Los detalles pueden llegar después.',
 'Antes de aceptar un plan, comprueba si te apetece o si solo te resulta fácil decir que sí. Una preferencia clara también ayuda a compartir.',
 'Entre pensar un proyecto y comprometerte con todo hay un primer paso. Haz una prueba pequeña antes de convertirla en una obligación.',
 'Al presentarte ante alguien, puedes elegir qué parte de ti quieres compartir. No necesitas resumir toda tu historia en el primer encuentro.'),
'Moon':(
 'Si tu plan del día y tus ganas van por caminos distintos, revisa el tamaño del plan. Ajustarlo puede ser una forma de seguir adelante.',
 'Antes de buscar otra actividad para llenar un rato libre, prueba a dejarlo libre. Observa si prefieres compañía, silencio o cambiar de ambiente.',
 'Un mensaje escrito con prisa puede decir más o menos de lo que querías. Léelo una vez pensando en lo que necesitas que se entienda.',
 'Un «como quieras» puede dejar una preferencia importante sin decir. Si compartes un plan, expresa qué te haría disfrutarlo más.',
 'Las ganas de acabar algo no obligan a hacerlo todo de una vez. Decide cuánto quieres avanzar antes de empezar y dónde vas a parar.',
 'No tienes que llegar a cada encuentro con la misma disposición. Puedes empezar escuchando y encontrar tu lugar a medida que avanza la conversación.'),
'Mercury':(
 'Si estás contando un proyecto, distingue lo que quieres hacer de lo que ya has decidido. Así puedes pedir opiniones sin sentir que has hecho una promesa.',
 'A veces «estoy bien» no alcanza para explicar lo que necesitas. Si quieres hablarlo, prueba con una petición concreta en vez de esperar que la adivinen.',
 'Una explicación puede volverse más clara al quitarle una frase. Antes de añadir argumentos, comprueba si la pregunta principal está bien planteada.',
 'Si tienes ganas de ver a alguien, propone un plan. Si necesitas otro ritmo, dilo. La conversación tiene más posibilidades cuando nadie tiene que adivinar.',
 'Antes de responder a una propuesta, separa lo que quieres hacer de lo que puedes hacer ahora. Un límite concreto evita una promesa difícil de sostener.',
 'En una conversación nueva, una buena pregunta puede abrir más espacio que una presentación perfecta. Elige algo que de verdad te interese saber.'),
'Venus':(
 'Algo puede gustarte sin encajar en lo que quieres construir. Antes de decir que sí, mira si esa elección también tiene lugar en tus prioridades.',
 'Compartir un rato no exige querer exactamente lo mismo. Prueba a poner sobre la mesa una preferencia tuya y dejar espacio para escuchar la otra.',
 'Una conversación agradable también puede ser clara. Si hay un acuerdo por cerrar, nombra los detalles que importan en lugar de dejarlos sobreentendidos.',
 'Piensa en un plan que disfrutarías aunque fuera sencillo. Puedes proponerlo sin convertir la respuesta de otra persona en una medida de tu valor.',
 'Las ganas y el ritmo no siempre coinciden entre dos personas. Si quieres acercarte, pregunta, escucha y deja espacio para una respuesta libre.',
 'Para sentirte a gusto en un encuentro, elige un detalle que te represente. No hace falta preparar una versión impecable de ti para participar.'),
'Mars':(
 'Una idea puede entusiasmarte y parecer imposible de acomodar en tu semana. Entre empezar a lo grande y dejarla para después, prueba una versión pequeña.',
 'Antes de lanzarte a una tarea, comprueba qué necesitas para hacerla a un ritmo cómodo. Preparar el espacio también forma parte del comienzo.',
 'Si quieres mover una conversación hacia una decisión, formula una pregunta que pueda responderse. Decirlo con claridad no exige decirlo con dureza.',
 'Proponer un encuentro es dar un paso; decidir por los dos es otra cosa. Deja que la otra persona pueda expresar sus ganas, sus límites y su ritmo.',
 'Empezar tres cosas puede resultar más tentador que elegir una. Pon un límite al alcance de la primera prueba y decide después si quieres ampliarla.',
 'Si estás esperando sentirte completamente preparado para empezar, prueba un paso que puedas corregir. La primera versión no tiene que ser la definitiva.'),
'Jupiter':(
 'Una posibilidad nueva merece curiosidad, pero también espacio real. Antes de sumarla a tus planes, mira qué tiempo necesitaría y qué dejarías para después.',
 'Cambiar de ambiente puede darte otra perspectiva sin exigir un gran plan. Piensa en una experiencia sencilla que te interese probar por gusto propio.',
 'Una explicación convincente puede ser solo una parte de la historia. Busca una segunda fuente o una pregunta que todavía no hayas considerado.',
 'Un plan compartido puede crecer rápido cuando entusiasma. Antes de añadir gastos o compromisos, acuerden qué quieren disfrutar de verdad.',
 'Si una meta parece enorme, diseña una prueba con un final reconocible. Lo que aprendas de ella puede ayudarte a decidir cuánto más quieres dedicarle.',
 'En un espacio nuevo, puedes participar sin tener una opinión sobre todo. Lleva una pregunta y permite que la experiencia amplíe tu primera impresión.'),
'Saturn':(
 'Antes de añadir otra obligación a un proyecto, revisa cuál lo hace avanzar de verdad. Un compromiso más pequeño puede tener un lugar más claro en tu semana.',
 'Puedes reservar tiempo para descansar o estar a solas sin convertirlo en otra tarea que cumplir perfectamente. Decide qué quieres proteger en tu agenda.',
 'Si un acuerdo depende de varios detalles, conviene escribirlos. Una fecha y un alcance claros pueden ahorrar una conversación repetida.',
 'Lo que valoras necesita espacio, no solo buenas intenciones. Revisa qué puedes ofrecer en un acuerdo y qué necesita una fecha o un límite distinto.',
 'La constancia no exige mantener siempre la misma velocidad. Define un avance que puedas repetir y deja margen para corregir el plan.',
 'Al empezar algo nuevo, distingue lo que ya te corresponde de lo que todavía puedes preguntar. No necesitas asumir todas las responsabilidades de entrada.'),
'Uranus':(
 'Una costumbre puede seguir en tu agenda mucho después de perder sentido. Elige una que puedas cambiar sin poner en juego algo importante y prueba otra manera.',
 'Si quieres salir de la rutina, empieza por un cambio pequeño de ambiente o de horario. Observa si te resulta cómodo antes de repetirlo.',
 'Si llevas varias vueltas sobre una misma idea, cambia la pregunta o la forma de anotarla. Un esquema, un paseo o una conversación pueden abrir otra entrada.',
 'Un acuerdo puede revisarse sin descartar el vínculo. Si quieres hacer algo de otra manera, plantea una propuesta concreta y escucha qué necesita la otra persona.',
 'Puedes probar un método distinto sin abandonar todo lo anterior. Elige una tarea pequeña para comparar y conserva lo que siga siendo útil.',
 'No tienes que presentarte siempre de la misma manera. En un espacio de confianza, puedes compartir un interés que normalmente dejas fuera de la conversación.'),
'Neptune':(
 'Una idea atractiva puede necesitar un contorno antes de convertirse en un plan. Escribe qué quieres crear y qué parte sigue siendo una posibilidad.',
 'Si te cuesta poner una necesidad en palabras, empieza por una escena concreta: cuándo aparece y qué te gustaría hacer distinto. No hace falta interpretarlo todo.',
 'Entre lo que alguien dijo y lo que imaginaste puede haber una pregunta pendiente. Si importa para un acuerdo, compruébalo antes de completar la historia.',
 'Un plan imaginado y una experiencia compartida pueden ser distintos. Deja espacio para conocer las preferencias reales de la otra persona.',
 'Si tienes ganas de hacer algo pero el objetivo es difuso, define una versión que puedas terminar. Puedes conservar la imaginación y acotar la primera prueba.',
 'Antes de intentar encajar en una imagen, piensa qué quieres compartir de verdad. Una presentación sencilla puede dejar más espacio a una conversación real.'),
'Pluto':(
 'Un proyecto puede seguir importándote aunque ya no quieras hacerlo como antes. Revisa qué parte deseas conservar y cuál puedes replantear.',
 'Si una costumbre ocupa más espacio del que quieres darle, empieza por observar cuándo la eliges. Puedes revisar una decisión sin explicarte toda tu historia.',
 'En una conversación importante, distingue comprender de convencer. Una pregunta honesta puede revelar qué sigue abierto sin obligar a cerrar el tema hoy.',
 'En un acuerdo, mira qué decide cada persona y qué necesita conversarse entre ambas. La cercanía también puede dejar espacio para elegir por separado.',
 'Antes de insistir con una tarea, pregúntate qué resultado sigue estando en tus manos. Puedes cambiar el método sin convertirlo en un juicio sobre ti.',
 'Una etiqueta que antes te describía puede quedarte corta. Puedes presentarte desde lo que estás haciendo ahora, sin tener que resolver quién serás después.')}
PAIRS={f'{body}.{target}':text for body,texts in PAIR_TEXT.items() for target,text in zip(TARGET_ORDER,texts)}
TITLES={
'Sun':'Hazle espacio a lo tuyo.','Moon':'También puedes cambiar de ritmo.',
'Mercury':'Lo importante merece una frase clara.','Venus':'Di qué te gustaría compartir.',
'Mars':'Empieza antes de tenerlo todo resuelto.','Jupiter':'Dale espacio a una pregunta nueva.',
'Saturn':'Promete lo que puedas sostener.','Uranus':'Prueba otra manera, en pequeño.',
'Neptune':'Dale un contorno a esa idea.','Pluto':'Puedes revisar lo que venías sosteniendo.'}
OPENINGS={
'Sun':'¿Qué quieres que tenga un lugar en tu semana? Antes de responder a todo lo que aparece, reserva espacio para una elección propia.',
'Moon':'Una semana tiene más de un ritmo. Puedes avanzar, hacer una pausa y volver a elegir sin convertir cada cambio en una tarea pendiente.',
'Mercury':'Una conversación puede empezar con algo sencillo: decir qué quieres, preguntar lo que falta o aclarar qué entendiste. Elige por dónde te gustaría abrirla.',
'Venus':'Piensa en lo que disfrutas compartir y en lo que te gustaría expresar mejor. Un plan sencillo puede ser suficiente para empezar esa conversación.',
'Mars':'Una idea puede entusiasmarte y parecer difícil de acomodar. Entre empezar a lo grande y dejarla para después, hay una tercera opción: hacer una versión pequeña.',
'Jupiter':'Antes de abrir diez caminos, elige uno que te dé curiosidad. Puedes explorar una posibilidad sin comprometerte todavía con todo lo que promete.',
'Saturn':'Revisa el espacio real que tienen tus compromisos. A veces definir una fecha, un límite o un alcance pequeño ayuda a cuidar algo que sí te importa.',
'Uranus':'No hace falta cambiarlo todo para descubrir otra manera. Una prueba reversible puede darte información sobre lo que quieres mantener y lo que prefieres ajustar.',
'Neptune':'Entre imaginar algo y darle forma hay preguntas que merecen tiempo. Elige una y distingue lo que sabes de lo que todavía te gustaría comprobar.',
'Pluto':'Hay decisiones que se pueden volver a mirar. Elige una que esté en tus manos y revisa qué quieres conservar, ajustar o dejar abierto.'}
# Aspect belongs in the evidence panel rather than a repeated technical sentence.
ASPECT_NOTES={0:'Conjunción: reúne los dos temas en una misma pregunta.',60:'Sextil: propone una articulación que requiere iniciativa.',90:'Cuadratura: plantea una diferencia de prioridades o ritmos.',120:'Trígono: propone continuidad entre los temas.',180:'Oposición: plantea dar espacio a dos prioridades.'}
TARGET_LABELS={'Sun':'Tu rumbo','Moon':'Tu ritmo','Mercury':'Conversaciones e ideas','Venus':'Vínculos y acuerdos','Mars':'Proyectos e iniciativa','Ascendant':'Nuevos comienzos'}
# Concrete aspect-specific endings preserve distinct interpretations without predicting events.
ENDINGS={0:'Elige un gesto que reúna ambas necesidades.',60:'Haz una propuesta pequeña y observa qué espacio encuentra.',90:'Antes de forzar una solución, nombra qué prioridades están compitiendo.',120:'Apóyate en algo que ya te funciona para dar el siguiente paso.',180:'Busca un acuerdo que deje espacio a ambos lados.'}
