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
    def reply(code,data,kind='application/json'):
        start_response(str(code)+' '+HTTPStatus(code).phrase,headers+[('Content-Type',kind),('Content-Length',str(len(data)))])
        return [data]
    # Fail closed until exact origin and source offer are configured.
    if not valid(origin) or not valid(source):
        return reply(503,b'{"error":"Deployment configuration is incomplete."}')
    path=environ.get('PATH_INFO','/')
    method=environ.get('REQUEST_METHOD','GET')
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
    h.allowed_origins=(origin,) # browsers must send the configured same origin
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
    try:
        with LOCK: # Swiss has global configuration; serialize inside each process.
            if method=='GET':h.do_GET()
            else:h.do_POST()
    except Exception:
        # Never log exception payloads or submitted data.
        return reply(500,b'{"error":"No pudimos completar la solicitud."}')
    code,data,kind=response
    if kind=='application/pdf':
        headers.append(('Content-Disposition','attachment; filename="mi-carta-trace-astra.pdf"'))
    return reply(code,data,kind)
