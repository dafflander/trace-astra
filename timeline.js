(() => {
 const panel=$('#timeline-panel'),status=$('#timeline-status'),cards=$('#timeline-cards'),context=$('#timeline-context'),button=$('#timeline-load');
 let revision=0,controller;
 const today=new Date(),end=new Date(today);end.setUTCFullYear(end.getUTCFullYear()+1);
 $('#timeline-start').value=today.toISOString().slice(0,10);$('#timeline-end').value=end.toISOString().slice(0,10);
 function reset(){revision++;controller?.abort();cards.replaceChildren();context.replaceChildren();status.textContent='';button.disabled=false;}
 form.addEventListener('input',reset);form.addEventListener('submit',reset);$('#sample').addEventListener('click',reset);$('#clear-data').addEventListener('click',reset);
 $('#city-results').addEventListener('click',reset);
 for(const id of ['timeline-start','timeline-end'])$('#'+id).addEventListener('input',reset);
 const date=s=>new Date(s).toLocaleString('es',{timeZone:'UTC',dateStyle:'medium',timeStyle:'short'})+' UTC';
 function display(c){
  const article=node('article','','timeline-card');article.append(node('h4',c.title),node('p',date(c.start_utc)+' — '+date(c.end_utc)));
  const pending=Date.now()<Date.parse(c.evaluate_after_utc);
  article.append(node('p',pending?c.future:c.past));
  for(const [label,items] of [['Cuenta como coincidencia',c.counts],['No cuenta',c.does_not_count]]){article.append(node('strong',label));const ul=node('ul','');items.forEach(t=>ul.append(node('li',t)));article.append(ul);}
  const detail=node('details','');detail.append(node('summary','Ver origen del cálculo'));const ev=c.detail.evidence;detail.append(node('p',`${ev.transit_body} respecto de ${ev.natal_body} · ${ev.aspect_deg}° · orbe mínimo ${ev.minimum_orb_deg.toFixed(3)}°. Regla ${c.detail.rule.id}.`));article.append(detail);
  if(pending){article.append(node('p','Pendiente · evaluable desde '+date(c.evaluate_after_utc)));}
  else {
   const label=node('label','Tu respuesta'),select=node('select','');['Selecciona una respuesta','Sí','No','No recuerdo','No aplica'].forEach(t=>{const o=node('option',t);o.value=t;select.append(o);});label.append(select);
   const whenLabel=node('label','Fecha y hora del evento (UTC)'),when=node('input','');when.type='datetime-local';whenLabel.append(when);
   const confirmLabel=node('label',''),confirm=node('input','');confirm.type='checkbox';confirmLabel.append(confirm,document.createTextNode(' Confirmo que se cumplen todos los criterios anteriores.'));
   const feedback=node('p','');feedback.setAttribute('role','status');
   function update(){const yes=select.value==='Sí';whenLabel.hidden=!yes;confirmLabel.hidden=!yes;feedback.textContent='';if(yes){const t=Date.parse(when.value+'Z');feedback.textContent=!Number.isFinite(t)||!confirm.checked?'Indica cuándo ocurrió y confirma los criterios.':t<Date.parse(c.start_utc)||t>=Date.parse(c.end_utc)?'La fecha queda fuera de esta ventana.':'Coincidencia declarada por ti; no verificada de forma independiente.';}else if(select.value==='No')feedback.textContent='Desacierto declarado.';else if(['No recuerdo','No aplica'].includes(select.value))feedback.textContent='Respuesta sin puntuación.';}
   select.onchange=update;when.oninput=update;confirm.onchange=update;update();article.append(label,whenLabel,confirmLabel,feedback);
  }
  cards.append(article);
 }
 button.onclick=async()=>{
  if(!current)return;reset();const localRevision=revision,chartRevision=calculationRevision,birth={...current.birth};
  const start=$('#timeline-start').value,end=$('#timeline-end').value,days=(Date.parse(end)-Date.parse(start))/86400000;
  if(!Number.isFinite(days)||days<=0||days>730){status.textContent='Elige un intervalo de 1 a 730 días.';return;}
  if(Date.parse(start+'T00:00:00Z')<Date.parse(birth.utc)){status.textContent='El intervalo debe comenzar después del nacimiento.';return;}
  controller=new AbortController();const requestController=controller;const timer=setTimeout(()=>requestController.abort(),120000);button.disabled=true;status.textContent='Calculando ventanas y seleccionando etapas…';
  try{const response=await traceFetch('/api/timeline',{method:'POST',headers:{'Content-Type':'application/json'},signal:controller.signal,body:JSON.stringify({...birth,start,end})});const data=await response.json();if(localRevision!==revision||chartRevision!==calculationRevision)return;if(!response.ok)throw Error(data.error||'No pudimos calcular el período.');data.cards.forEach(display);for(const c of data.long_term_context){context.append(node('p',c.rule.text),node('p',date(c.start_utc)+' — '+date(c.end_utc)));}status.textContent=data.cards.length?`${data.cards.length} ventanas seleccionadas de ${data.candidate_count} candidatos. La selección no indica mayor probabilidad de acierto.`:'No hay ventanas completas que cumplan los criterios en este intervalo. Prueba un período más amplio.';
  }catch(e){if(localRevision===revision)status.textContent=e.name==='AbortError'?'El cálculo tardó demasiado. Prueba un intervalo menor.':e.message;}finally{clearTimeout(timer);if(localRevision===revision)button.disabled=false;}
 };
})();
