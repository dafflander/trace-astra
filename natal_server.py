"""Loopback-only development server; no logging of birth inputs or persistence."""
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from zoneinfo import ZoneInfoNotFoundError
import swisseph as swe
from natal_request import calculate_request, InputError

ROOT = Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    allowed_origins=(None,'http://127.0.0.1:8766','http://localhost:8766')
    def log_message(self, *args):
        pass
    def respond(self, status, data, kind='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', kind if kind=='application/pdf' else kind+'; charset=utf-8')
        if kind=='application/pdf':
            self.send_header('Content-Disposition','attachment; filename="mi-carta-trace-astra.pdf"')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=()')
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path == '/healthz':
            return self.respond(200,b'{"status":"ok"}')
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/timeline.js':'timeline.js','/service.js':'service.js'}
        name=files.get(self.path)
        if not name:
            return self.respond(404,b'{}')
        kinds={'html':'text/html','js':'text/javascript','css':'text/css'}
        self.respond(200,(ROOT/name).read_bytes(),kinds[name.split('.')[-1]])
    def do_POST(self):
        if self.path not in ('/api/natal','/api/natal/pdf','/api/timeline'):
            return self.respond(404,b'{}')
        if self.headers.get('Origin') not in self.allowed_origins:
            return self.respond(403,b'{}')
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0 < size <= 4096:
                raise ValueError('Entrada demasiado extensa o vacía.')
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):
                raise ValueError('Formato de datos inválido.')
            result=calculate_request(body)
            if self.path == '/api/timeline':
                from research_reading import calculate_research_reading
                reading=calculate_research_reading(result['birth'],body['start'],body['end'])
                return self.respond(200,json.dumps(reading['timeline'],ensure_ascii=False,allow_nan=False).encode())
            if self.path == '/api/natal/pdf':
                if body.get('expected_result_id') != result['result_id']:
                    return self.respond(409,json.dumps({'error':'El cálculo cambió o esta carta es anterior. Vuelve a calcularla antes de descargar el PDF.'},ensure_ascii=False).encode())
                try:
                    from natal_pdf import create_pdf
                except ImportError:
                    return self.respond(503,json.dumps({'error':'La descarga PDF no está disponible en este servidor.'}).encode())
                return self.respond(200,create_pdf(result),'application/pdf')
            self.respond(200,json.dumps(result,ensure_ascii=False,allow_nan=False).encode())
        except InputError as exc:
            self.respond(400,json.dumps({'error':str(exc),'field':exc.field},ensure_ascii=False).encode())
        except (ValueError,KeyError,TypeError,ZoneInfoNotFoundError,swe.Error):
            self.respond(400,json.dumps({'error':'No pudimos calcular esta carta. Revisa los datos del formulario.'},ensure_ascii=False).encode())

if __name__ == '__main__':
    print('Carta local: http://127.0.0.1:8766/',flush=True)
    HTTPServer(('127.0.0.1',8766),Handler).serve_forever()
