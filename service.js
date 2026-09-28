// Cloudflare serves this page while the calculation service wakes up.
(() => {
 const base=document.querySelector('meta[name=trace-api]')?.content||'';
 let readiness=null;
 const overlay=document.createElement('section');overlay.className='service-wait';overlay.hidden=true;overlay.setAttribute('role','status');overlay.setAttribute('aria-live','polite');
 const title=document.createElement('h2');title.textContent='Estamos preparando el motor';
 const text=document.createElement('p');text.textContent='La primera consulta puede tardar alrededor de un minuto. Tus datos siguen en esta pestaña.';
 const orbit=document.createElement('div');orbit.className='service-orbit';orbit.setAttribute('aria-hidden','true');overlay.append(orbit,title,text);document.body.append(overlay);
 const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
 async function wake(signal){
  const deadline=Date.now()+55000;
  overlay.hidden=false;
  try {
   while(Date.now()<deadline){
    signal?.throwIfAborted();
    try{const r=await fetch(base+'/healthz',{cache:'no-store',signal:AbortSignal.any([signal||new AbortController().signal,AbortSignal.timeout(8000)])});if(r.ok&&(await r.json()).status==='ok')return;}catch(e){if(signal?.aborted)throw e;}
    await pause(2000);
   }
   throw Error('El motor sigue iniciándose. Vuelve a pulsar el botón de cálculo para reintentar; no necesitas completar los datos otra vez.');
  }finally{overlay.hidden=true;}
 }
 window.traceFetch=async (url,options={})=>{
  // Local server exposes the same readiness endpoint; no birth data in probes.
  if(!readiness)readiness=wake(options.signal).finally(()=>{readiness=null;});
  await readiness;options.signal?.throwIfAborted();
  return fetch(base+url,options);
 };
})();
