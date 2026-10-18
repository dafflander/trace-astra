(() => {
 const f=$('#comparison-form');let place=null,revision=0,searchRevision=0,result=null,payload=null,controller=null,busy=false;
 for(const c of countryChoices){const o=node('option',c.name);o.value=c.code;$('#comparison-country').append(o);}
 const timelineBusy=()=>window.traceTimelineProgress?.().some(p=>p.phase==='queued'||p.phase==='loading');
 function availability(){
  $('#comparison-submit').disabled=!current||busy||timelineBusy()||!!window.tracePdfBusy;
  $('#comparison-first').textContent=!current?'Prepara tu primera carta para continuar.':timelineBusy()?'Tu primera carta está lista. Puedes completar los datos de la segunda mientras termina el pasado y el futuro.': 'Usaremos tu carta ya calculada: Sol en '+current.planets[0].sign+'.';
 }
 function invalidate(){revision++;controller?.abort();controller=null;busy=false;result=null;payload=null;$('#comparison-result').hidden=true;$('#comparison-result').replaceChildren();$('#comparison-pdf').hidden=true;$('#comparison-status').textContent='';$('#comparison-pdf-status').textContent='';availability();}
 function resetPlace(){searchRevision++;place=null;$('#comparison-places').replaceChildren();$('#comparison-place-status').textContent='';f.elements.fold.value='';$('#comparison-clock').hidden=true;}
 f.addEventListener('input',invalidate);
 $('#comparison-country').addEventListener('change',resetPlace);$('#comparison-city').addEventListener('input',resetPlace);
 form.addEventListener('input',invalidate);form.addEventListener('submit',invalidate);$('#city-results').addEventListener('click',invalidate);$('#clear-data').addEventListener('click',()=>{f.reset();resetPlace();invalidate();});
 window.addEventListener('trace:chart-ready',invalidate);window.addEventListener('trace:timeline-updated',availability);
 $('#comparison-clear').onclick=()=>{f.reset();resetPlace();invalidate();};
 $('#comparison-search').onclick=async()=>{
  resetPlace();invalidate();const token=searchRevision,country=$('#comparison-country').value,query=$('#comparison-city').value.trim().split(',')[0];
  if(!country||query.length<3){$('#comparison-place-status').textContent='Selecciona un país y escribe al menos tres letras de la ciudad.';return;}
  $('#comparison-place-status').textContent='Buscando ciudades…';const c=new AbortController(),timer=setTimeout(()=>c.abort(),12000);
  try{
   const r=await fetch('https://geocoding-api.open-meteo.com/v1/search?'+new URLSearchParams({name:query,countryCode:country,count:'100',language:'es',format:'json'}),{signal:c.signal,referrerPolicy:'no-referrer'});
   if(!r.ok)throw Error();const data=await r.json();if(token!==searchRevision)return;
   const places=(data.results||[]).filter(p=>p.country_code===country&&p.timezone&&Number.isFinite(p.latitude)&&Number.isFinite(p.longitude));
   $('#comparison-place-status').textContent=places.length?'Selecciona la ciudad y confirma el país.':'Prueba otro nombre de la ciudad o una localidad cercana que puedas identificar.';
   for(const p of places){const label=[p.name,p.admin1,p.country].filter(Boolean).join(', '),b=node('button',label,'secondary city-choice');b.type='button';b.onclick=()=>{invalidate();place={latitude:p.latitude,longitude:p.longitude,timezone:p.timezone};$('#comparison-places').replaceChildren();$('#comparison-place-status').textContent='Lugar confirmado: '+label;};$('#comparison-places').append(b);}
  }catch(e){if(token===searchRevision)$('#comparison-place-status').textContent='No pudimos buscar la ciudad. Conservamos los datos; puedes reintentar.';}finally{clearTimeout(timer);}
 };
 function show(data){
  const box=$('#comparison-result');box.replaceChildren(node('h3','Su lectura en pocas palabras'),node('p',data.notice,'note'));
  for(const section of data.sections){const card=node('article','','reading-entry');card.append(node('h3',section.title),node('p',section.summary),node('p',section.question));const details=node('details','');details.append(node('summary','Cruces que sustentan esta lectura'));for(const c of section.crossings){details.append(node('p',c.label,'reading-evidence'));if(c.text!==section.summary)details.append(node('p',c.text));}if(!section.crossings.length)details.append(node('p','Sin cruces seleccionados para este tema dentro del margen de 3°.'));card.append(details);box.append(card);}
  box.append(node('p',data.method,'note'));box.hidden=false;$('#comparison-pdf').hidden=false;box.focus();
 }
 f.onsubmit=async e=>{
  e.preventDefault();if(!current||busy||timelineBusy()||window.tracePdfBusy)return;
  if(!place){$('#comparison-status').textContent='Busca la ciudad de la segunda persona y selecciona un resultado.';return;}
  invalidate();const token=revision,firstRevision=calculationRevision,fd=new FormData(f);
  const second={...place,local_datetime:fd.get('date')+'T'+fd.get('time'),time_accuracy:'recorded',house_system:'P'};if(fd.get('fold')!=='')second.fold=Number(fd.get('fold'));
  const request={first:{...current.birth,house_system:current.conventions.houses==='Placidus'?'P':'W'},second};
  controller=new AbortController();const active=controller,timer=setTimeout(()=>active.abort(),180000);busy=true;availability();$('#comparison-status').textContent='Comparando ambas cartas…';
  try{const r=await traceFetch('/api/comparison',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal:active.signal});const data=await r.json();if(token!==revision||firstRevision!==calculationRevision)return;if(!r.ok){if(data.field==='second.fold'){$('#comparison-clock').hidden=false;$('#comparison-clock').open=true;}throw Error(data.error||'No pudimos comparar las cartas.');}result=data;payload=request;show(data);$('#comparison-status').textContent='Comparación lista. Puedes leer el resumen y abrir los cruces de cada tema.';
  }catch(e){if(token===revision)$('#comparison-status').textContent=e.name==='AbortError'?'Se interrumpió la espera. Conservamos tus datos para reintentar.':e.message;}finally{clearTimeout(timer);if(token===revision){busy=false;availability();}}
 };
 $('#comparison-pdf').onclick=async()=>{
  if(!result||busy||timelineBusy())return;const token=revision,button=$('#comparison-pdf');controller=new AbortController();const active=controller,timer=setTimeout(()=>active.abort(),180000);busy=true;button.disabled=true;availability();$('#comparison-pdf-status').textContent='Preparando el PDF de ambas cartas…';
  try{const r=await traceFetch('/api/comparison/pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,expected_result_id:result.result_id}),signal:active.signal});if(!r.ok){const error=await r.json();throw Error(error.error||'No pudimos preparar el PDF.');}const blob=await r.blob();if(token!==revision)return;const url=URL.createObjectURL(blob),a=node('a','');a.href=url;a.download='traceastra-dos-cartas.pdf';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('#comparison-pdf-status').textContent='PDF listo. Contiene datos de ambas personas; guárdalo en un lugar privado.';}catch(e){if(token===revision)$('#comparison-pdf-status').textContent=e.name==='AbortError'?'Se interrumpió la descarga. Puedes reintentar.':e.message;}finally{clearTimeout(timer);button.disabled=false;if(token===revision){busy=false;availability();}}
 };
 availability();
})();
