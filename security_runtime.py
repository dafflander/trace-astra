"""Bounded transient abuse protection; no birth data or IP addresses persisted."""
import hashlib
import hmac
import io
import math
import multiprocessing
import secrets
import time
from collections import OrderedDict, deque
from threading import Lock

SECURITY_HEADERS=[
 ('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),
 ('X-Frame-Options','DENY'),('Permissions-Policy','camera=(), microphone=(), geolocation=()'),
 ('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://geocoding-api.open-meteo.com; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"),
]

class RateLimiter:
    def __init__(self,per_peer=30,total=120,window=60,capacity=2048):
        self.per_peer,self.total,self.window,self.capacity=per_peer,total,window,capacity
        self.peers=OrderedDict();self.global_hits=deque();self.lock=Lock();self.salt=secrets.token_bytes(32)
    def admit(self,peer,now=None):
        now=time.monotonic() if now is None else now
        key=hmac.new(self.salt,str(peer).encode(),hashlib.sha256).digest()
        with self.lock:
            cutoff=now-self.window
            while self.global_hits and self.global_hits[0]<=cutoff:self.global_hits.popleft()
            for k in list(self.peers):
                q=self.peers[k]
                while q and q[0]<=cutoff:q.popleft()
                if not q:del self.peers[k]
            q=self.peers.get(key,deque())
            if len(q)>=self.per_peer or len(self.global_hits)>=self.total:
                first=q[0] if len(q)>=self.per_peer else self.global_hits[0]
                return max(1,math.ceil(first+self.window-now))
            if key not in self.peers and len(self.peers)>=self.capacity:
                return max(1,math.ceil(self.window))
            q.append(now);self.peers[key]=q;self.global_hits.append(now)
            return 0

LIMITER=RateLimiter()

def _calculate(connection,path,raw,origin,allowed):
    try:
        from natal_server import Handler
        handler=Handler.__new__(Handler)
        handler.path=path;handler.allowed_origins=allowed
        handler.headers={'Content-Length':str(len(raw)),'Origin':origin}
        handler.rfile=io.BytesIO(raw)
        handler.respond=lambda code,data,kind='application/json':connection.send((code,data,kind))
        handler.do_POST()
    except Exception:
        connection.send((500,b'{"error":"No pudimos completar la solicitud."}','application/json'))
    finally:connection.close()

def run_calculation(path,raw,origin,allowed,timeout=75):
    # A separate process can be terminated even inside a native ephemeris call.
    ctx=multiprocessing.get_context('spawn')
    reader,writer=ctx.Pipe(duplex=False)
    process=ctx.Process(target=_calculate,args=(writer,path,raw,origin,allowed),daemon=True)
    try:
        process.start();writer.close()
        if reader.poll(timeout):
            try:return reader.recv()
            except EOFError:return (500,b'{"error":"No pudimos completar la solicitud."}','application/json')
        return (504,b'{"error":"El calculo supero el tiempo disponible. Prueba un periodo mas corto."}','application/json')
    finally:
        if process.pid:
            if process.is_alive():process.terminate()
            process.join(timeout=2)
            if process.is_alive():process.kill();process.join(timeout=2)
        reader.close();writer.close()
