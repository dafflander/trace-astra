// Readiness checks carry no birth data. Cancellation leaves the form in memory.
(() => {
 const base=document.querySelector('meta[name=trace-api]')?.content||'';
 let readyUntil=0;
 const overlay=document.createElement('section');overlay.className='service-wait';overlay.hidden=true;
 const title=document.createElement('h2');title.textContent='Estamos preparando la lectura de tu cielo';
 const text=document.createElement('p');text.setAttribute('role','status');text.setAttribute('aria-live','polite');
 const elapsed=document.createElement('p');elapsed.className='note';
 const cancel=document.createElement('button');cancel.type='button';cancel.textContent='Cancelar y volver a mis datos';
 const orbit=document.createElement('div');orbit.className='service-orbit';orbit.setAttribute('aria-hidden','true');
 overlay.append(orbit,title,text,elapsed,cancel);document.body.append(overlay);
 const visible=new Set();let displayed=null,previousFocus=null;
 function paint(){
  const jobs=Array.from(visible);displayed=jobs[jobs.length-1]||null;
  if(!displayed){overlay.hidden=true;if(previousFocus?.isConnected)previousFocus.focus();previousFocus=null;return;}
  const first=overlay.hidden;overlay.hidden=false;text.textContent=displayed.message;
  title.textContent=displayed.pdf?'Estamos preparando tu PDF':'Estamos preparando la lectura de tu cielo';
  elapsed.textContent=Math.floor((Date.now()-displayed.started)/1000)+' segundos de espera · Puedes cancelar sin borrar tus datos.';
  if(first){previousFocus=document.activeElement;cancel.focus();}
 }
 function show(job,message){job.message=message;visible.add(job);paint();}
 cancel.onclick=()=>{if(displayed){displayed.cancelled=true;displayed.controller.abort();}};
 const error=(name,message)=>Object.assign(new Error(message),{name});
 const aborted=()=>error('AbortError','La espera se interrumpió. Tus datos siguen en el formulario.');
 function check(signal){if(signal.aborted)throw aborted();}
 function pause(ms,signal){return new Promise((resolve,reject)=>{
  let timer;const stop=()=>{clearTimeout(timer);signal.removeEventListener('abort',stop);reject(aborted());};
  if(signal.aborted)return stop();signal.addEventListener('abort',stop);
  timer=setTimeout(()=>{signal.removeEventListener('abort',stop);resolve();},ms);
 });}
 // Avoid AbortSignal.any, AbortSignal.timeout and throwIfAborted (older mobile browsers).
 function bounded(signal,ms){
  const controller=new AbortController(),stop=()=>controller.abort();
  if(signal.aborted)stop();else signal.addEventListener('abort',stop);
  const timer=setTimeout(stop,ms);
  return {signal:controller.signal,close(){clearTimeout(timer);signal.removeEventListener('abort',stop);}};
 }
 async function wake(job){
  const deadline=Date.now()+120000;let attempts=0,receivedResponse=false;
  while(Date.now()<deadline){
   check(job.controller.signal);attempts++;
   show(job,attempts===1?'Comprobando la conexión con el servicio…':'Comprobando de nuevo la disponibilidad · intento '+attempts+'. La primera consulta puede tardar unos minutos.');
   const probe=bounded(job.controller.signal,Math.min(10000,deadline-Date.now()));
   try{
    const r=await fetch(base+'/healthz',{cache:'no-store',signal:probe.signal});receivedResponse=true;
    if(r.ok){let data;try{data=await r.json();}catch(_){}if(data?.status==='ok')return;}
    if(r.status===429)throw error('ServiceBusy','El servicio tiene demasiadas solicitudes. Espera un momento y vuelve a intentarlo. Tus datos siguen aquí.');
    show(job,'El servicio responde, pero aún no está listo. Puede estar iniciándose o temporalmente no disponible. Volveremos a comprobarlo.');
   }catch(e){
    check(job.controller.signal);if(e.name==='ServiceBusy')throw e;
    show(job,'No pudimos confirmar la conexión. Estamos reintentando; tus datos siguen aquí.');
   }finally{probe.close();}
   await pause(Math.min(2000,Math.max(0,deadline-Date.now())),job.controller.signal);
  }
  if(receivedResponse)throw error('ServiceUnavailable','El servicio responde, pero aún no está disponible para calcular. Puede estar iniciándose o tener una incidencia. Tus datos siguen aquí; vuelve a intentarlo en unos minutos.');
  throw error('ConnectionError','No pudimos conectar con el servicio. Comprueba tu conexión o prueba a abrir la página en Safari o Chrome fuera de WhatsApp. Tus datos siguen en este formulario.');
 }
 window.traceFetch=async(url,options={})=>{
  if(typeof fetch!=='function'||typeof AbortController!=='function')throw error('BrowserUnsupported','Este navegador no permite completar la conexión. Abre esta página en una versión actualizada de Safari o Chrome.');
  const job={controller:new AbortController(),cancelled:false,started:Date.now(),pdf:url.endsWith('/pdf')};
  const parent=options.signal,stop=()=>job.controller.abort();
  if(parent?.aborted)stop();else parent?.addEventListener('abort',stop);
  const ticker=setInterval(()=>{if(displayed===job)paint();},1000);
  try{
   check(job.controller.signal);
   if(Date.now()>=readyUntil){await wake(job);readyUntil=Date.now()+120000;}
   check(job.controller.signal);
   if(url==='/api/natal'||url==='/api/comparison'||job.pdf)show(job,job.pdf?'Conexión lista. Estamos creando tu documento…':'Conexión lista. Estamos calculando tu carta…');
   else {visible.delete(job);paint();}
   let response;
   try{response=await fetch(base+url,{...options,signal:job.controller.signal});}
   catch(e){check(job.controller.signal);readyUntil=0;throw error('ConnectionError','Se perdió la conexión con el servicio. Tus datos siguen aquí; vuelve a intentarlo.');}
   if(response.status===429||response.status===503){
    readyUntil=0;
    let data;try{data=await response.clone().json();}catch(_){}
    if(response.status===429)throw error('ServiceBusy','Has realizado varias solicitudes seguidas. Espera un minuto antes de reintentar. Tus datos siguen aquí.');
    if(data?.error?.includes('completando otra lectura'))throw error('ServiceBusy','El servicio está ocupado con otra lectura. Espera unos segundos y vuelve a intentarlo. Tus datos siguen aquí.');
    throw error('ServiceUnavailable','El servicio no está disponible en este momento. Tus datos siguen aquí; vuelve a intentarlo en unos minutos.');
   }
   if([502,504].includes(response.status)){readyUntil=0;throw error('ServiceUnavailable','El servicio no respondió a tiempo. Tus datos siguen aquí; vuelve a intentarlo.');}
   return response;
  }catch(e){if(job.cancelled)throw error('UserCancelled','Cancelaste la espera. Tus datos siguen aquí; puedes volver a preparar tu lectura cuando quieras.');throw e;}
  finally{clearInterval(ticker);parent?.removeEventListener('abort',stop);visible.delete(job);paint();}
 };
})();
