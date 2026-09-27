# TRACE ASTRA - preparación del piloto

Servicio de carta natal sin base de datos, cuentas, anuncios activos ni IA.
Estado: preparación privada. No activar públicamente hasta completar la oferta de código AGPL y revisión de dependencias, validación y configuración del hosting.

## Ejecutar
Python 3.10. Instalar requirements-hosting.txt.
Definir TRACE_PUBLIC_ORIGIN (origen HTTPS exacto) y TRACE_SOURCE_URL (fuente correspondiente accesible).
Arranque: gunicorn wsgi:application --workers 1 --threads 1 --bind 0.0.0.0:$PORT
Render: plan Free, instalación pip install -r requirements-hosting.txt, comprobación /healthz.

Sin variables correctas responde 503. No configurar la fuente a este repositorio mientras sea privado para usuarios públicos.
No se incluyen datos de nacimiento, registros, documentos privados ni módulos de investigación.

## Licencias
Swiss Ephemeris y pyswisseph: vía AGPLv3 prevista.
AGPL-3.0.txt contiene una copia del texto de licencia de pyswisseph.
La declaración de licencia del programa propio y el conjunto de fuentes de dependencias deben completarse antes de publicar.
Fuentes: https://github.com/astrorigin/pyswisseph y https://www.astro.com/swisseph/
