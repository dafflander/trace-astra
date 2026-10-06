(() => {
 const notifyClosing=()=>window.dispatchEvent(new Event('trace:timeline-updated'));
 const kinds=['past','future'];let automatic={past:true,future:true};let revision=0,queue=Promise.resolve();
 const states=Object.fromEntries(kinds.map(k=>[k,{controller:null,token:0,result:null,period:null}]));
 const bodyNames={Sun:'Sol',Moon:'Luna',Mercury:'Mercurio',Venus:'Venus',Mars:'Marte',Jupiter:'Júpiter',Saturn:'Saturno',Uranus:'Urano',Neptune:'Neptuno',Pluto:'Plutón',Ascendant:'Ascendente'};
 const date=s=>new Date(s).toLocaleString('es',{timeZone:'UTC',dateStyle:'medium',timeStyle:'short'})+' UTC';
 const iso=d=>d.toISOString().slice(0,10);
 const today=()=>{const d=new Date();return new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate()));};
 function reset(){revision++;$('#review-cards').replaceChildren();for(const k of kinds){$('#review-cards').replaceChildren();const s=states[k];s.controller?.abort();s.token++;s.result=null;s.period=null;$('#'+k+'-cards').replaceChildren();$('#'+k+'-context').replaceChildren();$('#'+k+'-status').textContent='';$('#'+k+'-period').textContent='';$('#'+k+'-load').disabled=false;}}
 form.addEventListener('input',reset);form.addEventListener('submit',reset);$('#clear-data').addEventListener('click',reset);$('#city-results').addEventListener('click',reset);
 window.traceTimelineRevision=()=>revision+':'+kinds.map(k=>states[k].token).join(':');
 window.traceReadingData=()=>kinds.map(k=>({kind:k,...states[k].period,status:states[k].result?'ready':'unavailable',timeline:states[k].result}));
 window.tracePeriods=()=>kinds.map(k=>({kind:k,...states[k].period,status:states[k].result?'ready':'unavailable'}));
 function display(c,cards,k){
  const article=node('article','','timeline-card');article.append(node('h4',c.title),node('p',date(c.start_utc)+' — '+date(c.end_utc)));
  const pending=Date.now()<Date.parse(c.evaluate_after_utc);
  article.append(node('p',k==='past'?c.past:c.future));const review=node('article','','timeline-card');review.append(node('h4',c.title),node('p',date(c.start_utc)+' — '+date(c.end_utc)));const criteria=node('details','');criteria.append(node('summary','Cómo reconocer este tema'));article.append(criteria);
  for(const [label,items] of [['Cuenta como coincidencia',c.counts],['No cuenta',c.does_not_count]]){criteria.append(node('strong',label));const ul=node('ul','');items.forEach(t=>ul.append(node('li',t)));criteria.append(ul);}
  const detail=node('details','');detail.append(node('summary','Ver origen del cálculo'));const ev=c.detail.evidence;detail.append(node('p',`${bodyNames[ev.transit_body]||ev.transit_body} respecto de ${bodyNames[ev.natal_body]||ev.natal_body} · ${ev.aspect_deg}° · orbe mínimo ${ev.minimum_orb_deg.toFixed(3)}°. Regla ${c.detail.rule.id}.`));article.append(detail);
  if(pending){article.append(node('p','Pendiente · evaluable desde '+date(c.evaluate_after_utc)));}
  else {
   const label=node('label','Tu respuesta'),select=node('select','');['Selecciona una respuesta','Sí','No','No recuerdo','No aplica'].forEach(t=>{const o=node('option',t);o.value=t;select.append(o);});label.append(select);
   const whenLabel=node('label','Fecha y hora del evento (UTC)'),when=node('input','');when.type='datetime-local';whenLabel.append(when);
   const confirmLabel=node('label',''),confirm=node('input','');confirm.type='checkbox';confirmLabel.append(confirm,document.createTextNode(' Confirmo que se cumplen todos los criterios anteriores.'));
   const feedback=node('p','');feedback.setAttribute('role','status');
   function update(){const yes=select.value==='Sí';whenLabel.hidden=!yes;confirmLabel.hidden=!yes;feedback.textContent='';if(yes){const t=Date.parse(when.value+'Z');feedback.textContent=!Number.isFinite(t)||!confirm.checked?'Indica cuándo ocurrió y confirma los criterios.':t<Date.parse(c.start_utc)||t>=Date.parse(c.end_utc)?'La fecha queda fuera de esta ventana.':'Coincidencia declarada por ti; no verificada de forma independiente.';}else if(select.value==='No')feedback.textContent='Desacierto declarado.';else if(['No recuerdo','No aplica'].includes(select.value))feedback.textContent='Respuesta sin puntuación.';}
   select.onchange=update;when.oninput=update;confirm.onchange=update;update();review.append(label,whenLabel,confirmLabel,feedback);$('#review-cards').append(review);
  }
  cards.append(article);
 }

 async function load(k,expectedRevision,token){
  const state=states[k];if(!current||revision!==expectedRevision||state.token!==token)return;
  const status=$('#'+k+'-status'),button=$('#'+k+'-load');
  const auto=automatic[k];const start=$('#'+k+'-start').value,end=$('#'+k+'-end').value,days=(Date.parse(end)-Date.parse(start))/86400000;
  const boundary=today().getTime(),birth={...current.birth};
  const fail=message=>{notifyClosing();status.textContent=message;button.disabled=false;button.textContent='Reintentar este período';};
  if(!Number.isFinite(days)||days<=0||days>730)return fail('Elige un intervalo de 1 a 730 días.');
  if(Date.parse(start+'T00:00:00Z')<Date.parse(birth.utc))return fail('El período debe comenzar después del nacimiento.');
  if((k==='past'&&Date.parse(end)>boundary)||(k==='future'&&Date.parse(start)<boundary))return fail(k==='past'?'El pasado debe terminar como máximo al comenzar hoy.':'El futuro debe comenzar hoy o después.');
  state.period={start,end,...(auto?{mode:'milestones',anchor:iso(today())}:{})};$('#'+k+'-period').textContent=auto?(k==='past'?'Cuatro intervalos retrospectivos, más separados hacia atrás':'Cuatro intervalos del próximo año'):start+' a '+end+' · UTC (fecha final excluida)';
  const controller=new AbortController();state.controller=controller;const timer=setTimeout(()=>controller.abort(),120000);
  status.textContent='Estamos explorando este período de tu cielo…';button.disabled=true;
  try{
   const response=await traceFetch('/api/timeline',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({...birth,start,end,...(auto?{mode:'milestones',kind:k,anchor:iso(today())}:{})})});const data=await response.json();
   if(revision!==expectedRevision||state.token!==token)return;
   if(!response.ok)throw Error(data.error||'No pudimos completar este período.');
   state.result=data;$('#review-cards').replaceChildren();for(const other of kinds.filter(x=>x!==k)){if(states[other].result){$('#'+other+'-cards').replaceChildren();states[other].result.cards.forEach(c=>display(c,$('#'+other+'-cards'),other));}}notifyClosing();data.cards.forEach(c=>display(c,$('#'+k+'-cards'),k));
   for(const c of data.long_term_context||[]){
    const d=node('article','','timeline-context-entry');d.append(node('h4',c.system==='bazi'?'BaZi · contexto anual':'Jyotisha · contexto de largo plazo'),node('p',date(c.start_utc)+' — '+date(c.end_utc)));
    for(const paragraph of c.rule.reading||[c.rule.text])d.append(node('p',paragraph));
    d.append(node('p',c.clipped?'Solo una parte de este período coincide con la consulta. Se muestran sus fechas originales; no se puntúa.':'Contexto interpretativo; no se suma como confirmación de las ventanas occidentales.','note'));
    $('#'+k+'-context').append(d);
   }
   status.textContent=data.cards.length?`${data.cards.length} ventanas para explorar. La selección no indica mayor probabilidad de acierto.`:'No se encontraron ventanas completas dentro de los criterios. Esto no significa que no hayan ocurrido o vayan a ocurrir acontecimientos.';
   button.textContent='Actualizar este período';
  }catch(e){if(revision===expectedRevision&&state.token===token)fail(e.name==='AbortError'?'Este período tardó demasiado. Tu carta sigue disponible; puedes reintentarlo.':e.message);}
  finally{clearTimeout(timer);if(revision===expectedRevision&&state.token===token)button.disabled=false;notifyClosing();}
 }
 function enqueue(k){
  $('#review-cards').replaceChildren();const s=states[k];s.controller?.abort();s.token++;s.result=null;s.period=null;
  $('#'+k+'-cards').replaceChildren();$('#'+k+'-context').replaceChildren();
  $('#'+k+'-status').textContent='En espera para completar tu lectura…';$('#'+k+'-load').disabled=true;
  notifyClosing();const rev=revision,token=s.token;queue=queue.catch(()=>{}).then(()=>load(k,rev,token));
 }
 for(const k of kinds){
  $('#'+k+'-load').onclick=()=>{automatic[k]=false;enqueue(k);};
  for(const suffix of ['start','end'])$('#'+k+'-'+suffix).addEventListener('input',()=>{
   $('#review-cards').replaceChildren();const s=states[k];s.controller?.abort();s.token++;s.result=null;s.period=null;
   $('#'+k+'-cards').replaceChildren();$('#'+k+'-context').replaceChildren();$('#'+k+'-period').textContent='';
   $('#'+k+'-status').textContent='Pulsa actualizar para calcular el nuevo período.';$('#'+k+'-load').disabled=false;notifyClosing();
  });
 }
 window.addEventListener('trace:chart-ready',()=>{
  reset();automatic={past:true,future:true};const t=today(),past=new Date(t),future=new Date(t);past.setUTCDate(past.getUTCDate()-365);future.setUTCDate(future.getUTCDate()+365);
  const firstBirthDay=new Date(current.birth.utc);firstBirthDay.setUTCHours(0,0,0,0);firstBirthDay.setUTCDate(firstBirthDay.getUTCDate()+1);
  $('#past-start').value=iso(new Date(Math.max(past.getTime(),firstBirthDay.getTime())));$('#past-end').value=iso(t);
  $('#future-start').value=iso(new Date(Math.max(t.getTime(),firstBirthDay.getTime())));$('#future-end').value=iso(future);
  enqueue('past');enqueue('future');
 });
})();
