# TRACE ASTRA: piloto experimental

Lectura integrada: carta natal, biblioteca 0.4.1, afinidades, ventanas occidentales, Jyotisha y PDF conjunto. Sin IA, base de datos, perfiles persistentes ni anuncios activos. Hipótesis editoriales sin validación predictiva; BaZi: cuatro pilares y contexto elemental anual, sin Da Yun ni predicción biográfica.

Python 3.10; instalar requirements-hosting.txt. Variables TRACE_PUBLIC_ORIGIN y TRACE_SOURCE_URL obligatorias. Render: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 90. /healthz comprueba disponibilidad; /source enlaza el commit ejecutado cuando RENDER_GIT_COMMIT está disponible. No registrar cuerpos de solicitudes.

Código propio AGPL-3.0-only: véanse LICENSE-NOTICE.md y AGPL-3.0.txt. Dependencias conservan sus licencias. No se incluyen datos reales de usuarios.
