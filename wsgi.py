"""Hosting adapter. No birth persistence or request logging in this application."""
import json
import os
from http import HTTPStatus
from threading import Lock
from urllib.parse import urlparse
from natal_server import Handler

LOCK=Lock()
def application(environ,start_response):
    origin=os.environ.get('TRACE_PUBLIC_ORIGIN','')
    source=os.environ.get('TRACE_SOURCE_URL','')
    valid=lambda value: urlparse(value).scheme=='https' and bool(urlparse(value).netloc)
    headers=[('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer')]
    browser_origin=environ.get('HTTP_ORIGIN')
    allowed=(origin,'https://traceastra.com')
    if browser_origin in allowed:
        headers.extend([('Access-Control-Allow-Origin',browser_origin),('Vary','Origin')])
    def reply(code,data,kind='application/json'):
        start_response(str(code)+' '+HTTPStatus(code).phrase,headers+[('Content-Type',kind),('Content-Length',str(len(data)))])
        return [data]
    # Fail closed until exact origin and source offer are configured.
    if not valid(origin) or not valid(source):
        return reply(503,b'{"error":"Deployment configuration is incomplete."}')
    commit=os.environ.get('RENDER_GIT_COMMIT','')
    if len(commit)==40 and all(c in '0123456789abcdef' for c in commit):
        source='https://github.com/dafflander/trace-astra/tree/'+commit
    path=environ.get('PATH_INFO','/')
    method=environ.get('REQUEST_METHOD','GET')
    if method=='OPTIONS':
        if browser_origin not in allowed or path not in ('/api/natal','/api/natal/pdf','/api/timeline'):
            return reply(403,b'{}')
        headers.extend([('Access-Control-Allow-Methods','POST'),('Access-Control-Allow-Headers','Content-Type'),('Access-Control-Max-Age','600')])
        return reply(204,b'')
    if path=='/healthz' and method=='GET':
        return reply(200,b'{"status":"ok","storage":false}')
    if path=='/source' and method=='GET':
        start_response('302 Found',headers+[('Location',source),('Content-Length','0')]);return [b'']
    if method not in ('GET','POST'):
        return reply(405,b'{}')
    if method=='POST' and environ.get('CONTENT_TYPE','').split(';')[0]!='application/json':
        return reply(415,b'{"error":"Expected application/json"}')
    h=Handler.__new__(Handler)
    h.path=path
    h.allowed_origins=allowed # browsers must send the configured same origin
    h.headers={'Content-Length':environ.get('CONTENT_LENGTH','0'),'Origin':environ.get('HTTP_ORIGIN')}
    h.rfile=environ['wsgi.input']
    response=[]
    def capture(code,data,kind='application/json'):
        if path=='/' and code==200:
            # Override local-only copy for the hosted, transient-processing mode.
            page=data.decode().replace('http://127.0.0.1:8765/','https://traceastra.com/')
            page=page.replace('CARTA NATAL · LOCAL','CARTA NATAL · PILOTO')
            page=page.replace('En esta versión local, los datos se usan momentáneamente para calcular y no se guardan en una base de datos.','Los datos se envían a este servicio para calcular la carta. La aplicación no los guarda en una base de datos. El proveedor de alojamiento puede tratar información técnica de conexión.')
            page=page.replace('<footer>','<p><a href="/source">Código fuente del servicio</a></p><footer>')
            data=page.encode()
        response.extend([code,data,kind])
    h.respond=capture
    # Never occupy every HTTP thread waiting for the calculation lock.
    # Health checks and static files must remain available during a long scan.
    acquired=False
    if method=='POST':
        acquired=LOCK.acquire(blocking=False)
        if not acquired:
            headers.append(('Retry-After','5'))
            return reply(503,json.dumps({'error':'El servicio está completando otra lectura. Espera unos segundos y vuelve a intentarlo.'},ensure_ascii=False).encode())
    try:
        if method=='GET':h.do_GET()
        else:h.do_POST()
    except Exception:
        # Never log exception payloads or submitted data.
        return reply(500,b'{"error":"No pudimos completar la solicitud."}')
    finally:
        if acquired:LOCK.release()
    code,data,kind=response
    if kind=='application/pdf':
        headers.append(('Content-Disposition','attachment; filename="mi-carta-trace-astra.pdf"'))
    return reply(code,data,kind)
