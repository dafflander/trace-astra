let calculationRevision=0;
const $=s=>document.querySelector(s), form=$('#form');let current=null;
const signs=['Aries','Tauro','Géminis','Cáncer','Leo','Virgo','Libra','Escorpio','Sagitario','Capricornio','Acuario','Piscis'];
const fmt=p=>p.sign+' '+p.degree_in_sign.toFixed(2)+'°';
function node(tag,text,cls){const e=document.createElement(tag);e.textContent=text;if(cls)e.className=cls;return e;}
function rows(target,items){$(target).replaceChildren(...items.map(([a,b])=>{const r=node('div','','row');r.append(node('span',a),node('span',b));return r;}));}
function wheel(r){
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 600 600');svg.setAttribute('role','img');svg.setAttribute('aria-label','Carta natal: signos, cúspides y posiciones numeradas. Datos completos en la tabla.');
 const asc=r.ascendant.longitude_deg;
 function el(tag,attrs,text){const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text)e.textContent=text;svg.append(e);}
 function xy(deg,rad){const a=(180-deg+asc)*Math.PI/180;return [300+rad*Math.cos(a),300+rad*Math.sin(a)];}
 function line(deg,a,b,color){const [x1,y1]=xy(deg,a),[x2,y2]=xy(deg,b);el('line',{x1,y1,x2,y2,stroke:color,'stroke-width':1});}
 for(const radius of [260,218,155])el('circle',{cx:300,cy:300,r:radius,fill:'none',stroke:'#a4b4bf'});
 for(let i=0;i<12;i++){line(i*30,218,260,'#a4b4bf');const [x,y]=xy(i*30+15,240);let rotation=(180-(i*30+15)+asc+90)%360;if(rotation>90&&rotation<270)rotation=(rotation+180)%360;el('text',{x,y,transform:'rotate('+rotation+' '+x+' '+y+')','text-anchor':'middle','dominant-baseline':'middle',fill:'#244e70','font-size':14},signs[i]);}
 r.cusps.forEach((c,i)=>{line(c.longitude_deg,45,218,'#c2c9cc');const next=r.cusps[(i+1)%12].longitude_deg;const [x,y]=xy(c.longitude_deg+(next-c.longitude_deg+360)%360/2,120);el('text',{x,y,fill:'#6a7780','font-size':13},String(i+1));});
 // Alternating label radii keep tight conjunctions legible; dots stay at true longitude.
 for(const a of r.aspects||[]){
 const pa=r.planets.find(p=>p.id===a.body_a),pb=r.planets.find(p=>p.id===a.body_b);
 const [x1,y1]=xy(pa.longitude_deg,155),[x2,y2]=xy(pb.longitude_deg,155);
 el('line',{x1,y1,x2,y2,stroke:a.color,'stroke-width':1.5,'stroke-dasharray':a.dash});
 }
 const placed=[];
 r.planets.forEach((p,i)=>{let rad=193;while(placed.some(q=>Math.abs((p.longitude_deg-q.deg+540)%360-180)<9&&Math.abs(rad-q.rad)<17))rad-=20;placed.push({deg:p.longitude_deg,rad});const [dx,dy]=xy(p.longitude_deg,218),[x,y]=xy(p.longitude_deg,rad);el('line',{x1:dx,y1:dy,x2:x,y2:y,stroke:'#65869e'});el('circle',{cx:dx,cy:dy,r:3,fill:'#244e70'});el('circle',{cx:x,cy:y,r:10,fill:'#f6f3ec'});el('text',{x,y,'text-anchor':'middle','dominant-baseline':'middle',fill:'#244e70','font-size':14},String(i+1));});
 for(const [label,deg] of [['ASC',asc],['MC',r.midheaven.longitude_deg]]){const [x,y]=xy(deg,282);el('text',{x,y,'text-anchor':'middle','dominant-baseline':'middle',fill:'#244e70','font-size':14},label);}
 $('#wheel').replaceChildren(svg);
}
const symbolicGuide=[
 ['Sol','Se asocia con la identidad, la expresión personal y aquello que buscas desarrollar.','¿Qué actividades te permiten expresarte de una manera propia?'],
 ['Luna','Se relaciona con las necesidades emocionales, los hábitos y lo que te hace sentir protegido.','¿Qué te ayuda a recuperar la calma?'],
 ['Ascendente','En astrología se asocia con la manera de empezar algo y presentarte ante los demás.','¿Cómo sueles dar el primer paso ante algo desconocido?'],
 ['Mercurio','Se asocia con la comunicación, el aprendizaje y la manera de organizar ideas.','¿Cómo te resulta más fácil aprender y explicar algo?'],
 ['Venus','Se relaciona con los afectos, los gustos y aquello que valoras en tus vínculos.','¿Qué valoras al compartir tiempo con alguien?'],
 ['Marte','Se asocia con la iniciativa, el deseo, la acción y la forma de afrontar conflictos.','¿Cómo actúas cuando quieres conseguir algo o poner un límite?']
];
const glossary=[
 ['Sol','En esta carta indica la posición aparente del Sol en el zodiaco tropical en el momento del nacimiento. El signo es el sector de 30° que contiene esa posición.'],
 ['Luna','Muestra la posición geocéntrica de la Luna. La fecha y la hora se convierten a UTC antes del cálculo; cerca de un cambio de signo, una hora incierta puede modificar el resultado.'],
 ['Ascendente','Es la intersección oriental del horizonte con la eclíptica. Depende de la hora y del lugar de nacimiento; no es otro planeta.'],
 ['Medio cielo','Es uno de los puntos de intersección del meridiano local con la eclíptica. En Placidus coincide con el inicio de la casa 10; en signos enteros puede quedar dentro de otra casa.'],
 ['Casas','Son doce divisiones según el sistema elegido. Cambiar entre Placidus y signos enteros cambia las cúspides, pero no las posiciones de los planetas.'],
 ['Retrógrado · R','Indica que la longitud de un cuerpo disminuye en ese instante desde nuestra perspectiva terrestre. No significa que haya invertido físicamente su órbita.']
];
function render(r){
 $('#symbolic-reading').replaceChildren(...symbolicGuide.map(([label,copy,question])=>{
 const position=label==='Ascendente'?r.ascendant:r.planets.find(p=>p.name===label);
 const d=node('details');d.append(node('summary',label+' · '+position.sign),node('p',copy),node('p','Para explorar: '+question,'note'));
 d.append(node('small','La explicación describe el elemento en general; todavía no interpreta su combinación con '+position.sign+'.'));return d;
 }));

 $('#pdf-status').textContent='';
 $('#reading').replaceChildren(...glossary.map(([title,copy])=>{const d=node('details');d.append(node('summary',title),node('p',copy));return d;}));
$('#context').textContent=r.birth.local_datetime.replace('T',' · ')+' · '+r.birth.timezone+' · Casas: '+r.conventions.houses;
 $('#highlights').replaceChildren(...[['Sol',r.planets[0]],['Luna',r.planets[1]],['Ascendente',r.ascendant]].map(([label,p])=>{const d=node('div','','highlight');d.append(node('small',label),node('strong',p.sign),node('span',p.degree_in_sign.toFixed(2)+'°'));return d;}));
 rows('#positions',r.planets.map((p,i)=>[(i+1)+'. '+p.name+(p.retrograde?' · R':''),fmt(p)+' · Casa '+p.house]));
 rows('#aspects',(r.aspects||[]).map(a=>[a.name_a+' / '+a.name_b,a.name+' · orbe '+a.orb_deg.toFixed(2)+'°']));
 $('#aspect-legend').replaceChildren(...(r.aspect_rules||[]).map(a=>{const p=node('p',a.name+' '+a.angle+'° · margen '+a.orb+'°');p.style.borderLeft='3px '+(a.dash?'dashed':'solid')+' '+a.color;p.style.paddingLeft='12px';return p;}));
 rows('#houses',r.cusps.map(p=>['Casa '+p.house,fmt(p)]));
 $('#method').textContent=r.conventions.provider+' · '+r.conventions.backend+' · Zodiaco tropical. '+r.conventions.time+'. '+r.conventions.validation+'.';wheel(r);$('#result').hidden=false;$('#result').focus();}
$('#sample').onclick=()=>{searchRevision++;calculationRevision++; $('#city').value='Montevideo, Uruguay';$('#chosen-city').textContent='Ejemplo ficticio · Montevideo, Uruguay';$('#city-results').replaceChildren();$('#city-status').textContent='';for(const [k,v] of Object.entries({date:'1990-06-15',time:'07:30',timezone:'America/Montevideo',latitude:'-34.9',longitude:'-56.2',fold:'',house_system:'P'}))form.elements[k].value=v;$('#status').textContent='Ejemplo ficticio cargado. Pulsa «Calcular mi carta».';current=null;$('#result').hidden=true;};
form.addEventListener('input',()=>{calculationRevision++;current=null;$('#result').hidden=true;$('#status').textContent='';});
form.onsubmit=async e=>{e.preventDefault();const revision=++calculationRevision; const f=new FormData(form),button=form.querySelector('[type=submit]');current=null;$('#result').hidden=true;button.disabled=true;$('#status').textContent='Calculando…';
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),75000);
 const body={local_datetime:f.get('date')+'T'+f.get('time'),timezone:f.get('timezone').trim(),latitude:Number(f.get('latitude')),longitude:Number(f.get('longitude')),time_accuracy:'recorded',house_system:f.get('house_system')};if(f.get('fold')!=='')body.fold=Number(f.get('fold'));
 try{if(location.protocol==='file:')throw Error('Para calcular una carta nueva, abre el servicio local en http://127.0.0.1:8766/. Esta vista de archivo no ejecuta el motor.');const response=await traceFetch('/api/natal',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const r=await response.json();if(revision!==calculationRevision)return;if(!response.ok){const field=form.elements[r.field];if(field){const details=field.closest('details');if(details)details.open=true;field.focus();}throw Error(r.error||'No pudimos calcular esta carta.');}if(revision!==calculationRevision)return;current=r;render(r);$('#status').textContent='Cálculo completo.';}catch(error){if(revision===calculationRevision)$('#status').textContent=error.name==='AbortError'?'El cálculo tardó demasiado. Vuelve a intentarlo.':error.message;}finally{clearTimeout(timer);button.disabled=false;}};
$('#download').onclick=()=>{if(!current)return;const url=URL.createObjectURL(new Blob([JSON.stringify(current,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='trace-carta-natal.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};

let searchRevision=0;
$('#city').addEventListener('input',()=>{searchRevision++;$('#city-results').replaceChildren();$('#chosen-city').textContent='';$('#city-status').textContent='';for(const key of ['latitude','longitude','timezone'])form.elements[key].value='';});
$('#search-city').onclick=async()=>{
 const query=$('#city').value.trim(), revision=++searchRevision;
 $('#city-results').replaceChildren();
 if(query.length<3){$('#city-status').textContent='Escribe al menos tres letras.';return;}
 $('#city-status').textContent='Buscando localidades…';
 const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),12000);
 try{
  const response=await fetch('https://geocoding-api.open-meteo.com/v1/search?'+new URLSearchParams({name:query,count:'8',language:'es',format:'json'}),{signal:controller.signal,referrerPolicy:'no-referrer'});
  if(!response.ok)throw Error('Búsqueda no disponible.');
  const data=await response.json();if(revision!==searchRevision)return;
  const places=(data.results||[]).filter(p=>p.timezone&&Number.isFinite(p.latitude)&&Number.isFinite(p.longitude));
  $('#city-status').textContent=places.length?'Elige tu ciudad y comprueba la región.':'Sin resultados. Prueba otro nombre o introduce la ubicación manualmente.';
  if(!places.length)$('#location-details').open=true;
  for(const p of places){const label=[p.name,p.admin1,p.country].filter(Boolean).join(', '),b=node('button',label,'secondary city-choice');b.type='button';b.onclick=()=>{calculationRevision++;current=null;$('#result').hidden=true;for(const key of ['latitude','longitude','timezone'])form.elements[key].value=p[key];$('#chosen-city').textContent='Lugar seleccionado: '+label+' · '+p.timezone;$('#city-results').replaceChildren();$('#city-status').textContent='Ubicación completada. Puedes revisarla debajo.';$('#location-details').open=true;};$('#city-results').append(b);}
 }catch(error){if(revision===searchRevision){$('#city-status').textContent='No pudimos conectar con el buscador. Puedes introducir la ubicación manualmente.';$('#location-details').open=true;}}
 finally{clearTimeout(timer);}
};
form.addEventListener('invalid',e=>{if($('#location-details').contains(e.target))$('#location-details').open=true;},true);
for(const key of ['latitude','longitude','timezone'])form.elements[key].addEventListener('input',()=>{$('#chosen-city').textContent='Ubicación editada manualmente.';});

$('#city').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('#search-city').click();}});

$('#clear-data').onclick=()=>{
 calculationRevision++;searchRevision++;current=null;form.reset();
 for(const id of ['wheel','positions','houses','reading','symbolic-reading','aspects','aspect-legend','highlights','city-results'])$('#'+id).replaceChildren();
 for(const id of ['context','method','chosen-city','city-status','status','pdf-status'])$('#'+id).textContent='';
 $('#result').hidden=true;
 $('#status').textContent='Carta y formulario borrados de esta pantalla. Los archivos que hayas descargado permanecen en tu dispositivo.';
 form.elements.date.focus();
};


// Export only the already rendered result. No forms, scripts or remote resources.
$('#download-reading').onclick=()=>{
 if(!current)return;
 const section=$('#result').cloneNode(true);
 section.querySelector('#timeline-panel')?.remove();
 section.removeAttribute('id');section.removeAttribute('tabindex');section.hidden=false;
 section.querySelectorAll('button').forEach(e=>e.remove());
 section.querySelectorAll('details').forEach(e=>e.open=true);
 section.querySelectorAll('a').forEach(e=>e.replaceWith(document.createTextNode(e.textContent)));
 const style=Array.from(document.styleSheets).map(sheet=>Array.from(sheet.cssRules).map(rule=>rule.cssText).join('\n')).join('\n');
 const doc=document.implementation.createHTMLDocument('Mi carta natal · TRACE ASTRA');
 doc.documentElement.lang='es';
 const charset=doc.createElement('meta');charset.setAttribute('charset','utf-8');doc.head.prepend(charset);
 const viewport=doc.createElement('meta');viewport.name='viewport';viewport.content='width=device-width, initial-scale=1';doc.head.append(viewport);
 const policy=doc.createElement('meta');policy.httpEquiv='Content-Security-Policy';policy.content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'none'; base-uri 'none'";doc.head.append(policy);
 const css=doc.createElement('style');css.textContent=style;doc.head.append(css);
 const main=doc.createElement('main'),brand=doc.createElement('p');brand.textContent='TRACE ASTRA · Copia personal · Guía editorial 0.1';
 main.append(brand,doc.importNode(section,true));doc.body.append(main);
 const blob=new Blob(['<!doctype html>\n'+doc.documentElement.outerHTML],{type:'text/html;charset=utf-8'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='mi-carta-trace-astra.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};

$('#download-pdf').onclick=async()=>{
 if(!current)return;
 const result=current,revision=calculationRevision,b=$('#download-pdf'),controller=new AbortController();
 b.disabled=true;$('#pdf-status').textContent='Preparando PDF…';
 const timer=setTimeout(()=>controller.abort(),80000);
 try{
  if(location.protocol==='file:')throw Error('La descarga PDF necesita el servicio local activo.');
  const profile={...result.birth,expected_result_id:result.result_id,house_system:result.conventions.houses==='Placidus'?'P':'W'};
  const response=await traceFetch('/api/natal/pdf',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify(profile)});
  if(!response.ok){const error=await response.json();throw Error(error.error||'No pudimos crear el PDF. Inténtalo de nuevo.');}
  const blob=await response.blob();if(revision!==calculationRevision)return;
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='mi-carta-trace-astra.pdf';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('#pdf-status').textContent='PDF preparado. Incluye tus datos de nacimiento; guárdalo en un lugar privado.';
 }catch(error){if(revision===calculationRevision)$('#pdf-status').textContent=error.name==='AbortError'?'La generación tardó demasiado. Vuelve a intentarlo.':error.message;}
 finally{clearTimeout(timer);b.disabled=false;}
};
