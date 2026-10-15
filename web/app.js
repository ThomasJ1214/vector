'use strict';
const VM=VectorMath,$=id=>document.getElementById(id),plain=n=>n.toLocaleString('en-US',{useGrouping:false,maximumSignificantDigits:15}),fmt=n=>n===null?'Undefined':Number(n.toPrecision(10)).toString();
let vectors=[],inputType='polar',view='head',editing=-1,step=0,selected=-1;
function setType(type){inputType=type;$('polarFields').hidden=type!=='polar';$('xyFields').hidden=type!=='xy';document.querySelectorAll('[data-type]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.type===type));}
function setView(next){view=next;if(view==='step')step=0;render();}
function stopEdit(){editing=-1;$('formTitle').textContent='Add a vector';$('saveVector').textContent='+ Add vector';$('cancelEdit').hidden=true;$('error').textContent='';}
function loadDemo(kind){stopEdit();if(kind==='345'){setType('xy');$('xInput').value='3';$('yInput').value='4';}else{setType('polar');$('magnitude').value=kind==='compass'?'24':'10';$('angle').value=kind==='compass'?'30':'0';$('direction').value=kind==='compass'?'EN':'standard';}if(kind==='compass')vectors=[{...VM.polar(24,VM.compass(30,'EN')),angle:30,direction:'EN'}];else if(kind==='345')vectors=[{...VM.components(3,0)},{...VM.components(0,4)}];else vectors=[{...VM.polar(10,0),angle:0,direction:'standard'},{...VM.polar(10,180),angle:180,direction:'standard'}];view='head';selected=-1;step=0;render();}
document.querySelectorAll('[data-type]').forEach(b=>b.onclick=()=>setType(b.dataset.type));document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
function saveVector(){try{if(vectors.length>=20&&editing<0)throw Error('Your list is full. Edit or delete a vector first.');let v;
if(inputType==='polar'){const r=VM.decimal($('magnitude').value),a=VM.decimal($('angle').value),d=$('direction').value;if(r<0)throw Error('Magnitude must be nonnegative.');v={...VM.polar(r,d==='standard'?a:VM.compass(a,d)),angle:a,direction:d,entry:{magnitude:$('magnitude').value,angle:$('angle').value}};}
else v={...VM.components(VM.decimal($('xInput').value),VM.decimal($('yInput').value)),entry:{x:$('xInput').value,y:$('yInput').value}};
if(editing<0)vectors.push(v);else vectors[editing]=v;stopEdit();step=Math.min(step,vectors.length);render();}catch(err){$('error').textContent=err.message;}}
$('saveVector').onclick=saveVector;
$('vectorForm').onsubmit=e=>{e.preventDefault();saveVector();};
$('vectorForm').addEventListener('keydown',e=>{
 if(e.key==='Enter'&&!e.isComposing&&e.target.tagName==='INPUT'){
  e.preventDefault();saveVector();
 }
});
$('cancelEdit').onclick=stopEdit;$('clearAll').onclick=()=>{if(vectors.length&&!confirm('Delete all vectors in this tab?'))return;vectors=[];selected=-1;step=0;stopEdit();render();};
$('exampleCompass').onclick=()=>loadDemo('compass');$('example345').onclick=()=>loadDemo('345');$('exampleCancel').onclick=()=>loadDemo('cancel');
$('inspect').onchange=e=>{selected=Number(e.target.value);render();};$('previous').onclick=()=>{step=Math.max(0,step-1);render();};$('next').onclick=()=>{step=Math.min(vectors.length,step+1);render();};
document.addEventListener('keydown',e=>{if(view!=='step'||/INPUT|SELECT|BUTTON|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();$('next').click();}if(e.key==='ArrowLeft'){e.preventDefault();$('previous').click();}});
function node(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
function render(){
 $('count').textContent=`${vectors.length} / 20`;$('vectors').replaceChildren();
 vectors.forEach((v,i)=>{const li=node('li',undefined,'vector');li.append(node('span',i+1,'num'));const desc=node('div',`${fmt(v.r)} units · ${v.r===0?'no direction':fmt(v.t)+'°'}`,'desc');desc.append(node('span',`x ${fmt(v.x)}  ·  y ${fmt(v.y)}`));li.append(desc);
 for(const [label,fn] of [['Inspect',()=>{selected=i;view='triangle';render();}],['Edit',()=>{editing=i;setType(v.type);$('formTitle').textContent='Edit vector '+(i+1);$('saveVector').textContent='Save changes';$('cancelEdit').hidden=false;$('error').textContent='';if(v.type==='polar'){$('magnitude').value=v.entry?.magnitude??plain(v.r);$('angle').value=v.entry?.angle??plain(v.angle??v.t??0);$('direction').value=v.direction??'standard';}else{$('xInput').value=v.entry?.x??plain(v.x);$('yInput').value=v.entry?.y??plain(v.y);}$('formTitle').scrollIntoView({block:'nearest'});}],['×',()=>{vectors.splice(i,1);if(selected===i)selected=-1;else if(selected>i)selected--;stopEdit();step=Math.min(step,vectors.length);render();}]]){const b=node('button',label,'icon');b.setAttribute('aria-label',label==='×'?`Delete vector ${i+1}`:`${label} vector ${i+1}`);b.onclick=fn;li.append(b);}$('vectors').append(li);});
 if(!vectors.length)$('vectors').append(node('li','No vectors yet. Add one or try an example.','empty'));
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.view===view));
 $('plotTitle').textContent={head:'Head to tail',origin:'Common origin',triangle:'Component triangle',step:'One vector at a time'}[view];$('stepControls').hidden=view!=='step';$('triangleControls').hidden=view!=='triangle';$('stepLabel').textContent=`${step} / ${vectors.length} vectors`;$('previous').disabled=step===0;$('next').disabled=step===vectors.length;
 $('inspect').replaceChildren(new Option('Resultant',-1),...vectors.map((v,i)=>new Option('Vector '+(i+1),i)));$('inspect').value=selected;
 const active=view==='step'?vectors.slice(0,step):vectors,result=VM.sum(active),inspected=selected>=0?vectors[selected]:result;
 const shown=view==='triangle'?inspected:result;
 $('xLabel').textContent=view==='triangle'&&selected>=0?'Vector x':'Total x';$('yLabel').textContent=view==='triangle'&&selected>=0?'Vector y':'Total y';
 $('rx').textContent=fmt(shown.x);$('ry').textContent=fmt(shown.y);$('resultMagnitude').textContent=fmt(shown.r);$('resultAngle').textContent=shown.t===null?'Undefined':fmt(shown.t)+'°';
 $('warning').hidden=!result.near;$('warning').textContent='Near cancellation: the nonzero result is retained, but its angle may be sensitive to numeric precision.';
 $('extraLegend').textContent=view==='triangle'?'Green: x leg · Orange: y leg':'Numbers show input order';
 draw(active,result,inspected);work(active,result,inspected);
}
const NS='http://www.w3.org/2000/svg';
function draw(active,result,inspected){const svg=$('plot'),W=window.matchMedia('(max-width:720px)').matches?390:780,mid=W/2;svg.setAttribute('viewBox',`0 0 ${W} 390`);svg.style.aspectRatio=W+'/390';svg.replaceChildren();function el(tag,attrs,text){const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;}
 let pts=[{x:0,y:0}];if(view==='triangle')pts.push(inspected,{x:inspected.x,y:0});else{pts.push(...active,...result.points,result);}
 const limit=Math.max(...pts.flatMap(p=>[Math.abs(p.x),Math.abs(p.y)]))||1;
 const scale=145/limit,X=x=>mid+x*scale,Y=y=>195-y*scale;
 const span=limit*2,raw=limit/2,exponent=10**Math.floor(Math.log10(raw)),n=raw/exponent,tick=(n<2?1:n<5?2:5)*exponent;
 for(let i=-4;i<=4;i++){const p=i*tick;if(Math.abs(p)<=span){el('line',{x1:X(p),y1:25,x2:X(p),y2:365,stroke:'#edf0e8'});el('line',{x1:35,y1:Y(p),x2:W-35,y2:Y(p),stroke:'#edf0e8'});if(i!==0&&Y(p)>35&&Y(p)<355)el('text',{x:mid-8,y:Y(p)-5,'text-anchor':'end',fill:'#87948c','font-size':10},fmt(p));if(i!==0&&X(p)>50&&X(p)<W-50)el('text',{x:X(p)+3,y:209,fill:'#87948c','font-size':10},fmt(p));}}
 el('line',{x1:35,y1:195,x2:W-35,y2:195,stroke:'#bdc9bd'});el('line',{x1:mid,y1:25,x2:mid,y2:365,stroke:'#bdc9bd'});el('text',{x:W-38,y:184,fill:'#6a7c6c','font-size':12},'+x');el('text',{x:mid+9,y:28,fill:'#6a7c6c','font-size':12},'+y');
 function arrow(a,b,color,label){const x1=X(a.x),y1=Y(a.y),x2=X(b.x),y2=Y(b.y),dx=x2-x1,dy=y2-y1,h=Math.hypot(dx,dy);if(h<.2)el('circle',{cx:x2,cy:y2,r:3,fill:color});else{el('line',{x1,y1,x2,y2,stroke:color,'stroke-width':2.5,'stroke-linecap':'round'});const o=Math.min(11,h*.28),ux=dx/h,uy=dy/h;el('path',{d:`M${x2-o*ux+o*.4*uy},${y2-o*uy-o*.4*ux} L${x2},${y2} L${x2-o*ux-o*.4*uy},${y2-o*uy+o*.4*ux}`,fill:'none',stroke:color,'stroke-width':2.5});}if(label)el('text',{x:x2+(color==='#3264b7'?-13:9),y:y2-9,fill:color,'font-size':12,'font-weight':600,'paint-order':'stroke',stroke:'#fcfdf9','stroke-width':4},label);}
 if(view==='triangle'){const v=inspected;el('path',{d:`M${X(0)},${Y(0)} H${X(v.x)}`,stroke:'#408756','stroke-width':2,'stroke-dasharray':'5 4',fill:'none'});el('path',{d:`M${X(v.x)},${Y(0)} V${Y(v.y)}`,stroke:'#c88335','stroke-width':2,'stroke-dasharray':'5 4',fill:'none'});arrow({x:0,y:0},v,selected<0?'#c4483b':'#3264b7',selected<0?'R':'v'+(selected+1));}
 else {active.forEach((v,i)=>arrow(view==='origin'?{x:0,y:0}:result.points[i],view==='origin'?v:result.points[i+1],'#3264b7',String(i+1)));arrow({x:0,y:0},result,'#c4483b','R');}
 if(!active.length&&view!=='triangle')el('text',{x:mid,y:330,'text-anchor':'middle',fill:'#819078','font-size':13},view==='step'?'Press → to add the first vector':'Add a vector to get started');
}
function work(active,result,inspected){$('work').replaceChildren();$('workTitle').textContent=view==='triangle'?(selected<0?'Resultant triangle · calculations':`Vector ${selected+1} · calculations`):'Follow the calculation';function line(s){$('work').append(node('div',s,'workline'));}
 const list=view==='triangle'&&selected>=0?[inspected]:active;
 list.forEach((v,i)=>{const name=view==='triangle'&&selected>=0?selected+1:i+1;line(`v${name}: x = ${fmt(v.r)} cos(${fmt(v.t??0)}°) = ${fmt(v.x)};  y = ${fmt(v.r)} sin(${fmt(v.t??0)}°) = ${fmt(v.y)}${v.type==='xy'?'  (x,y entered; polar form is a check)':''}`);});
 const r=view==='triangle'?inspected:result;
 if(!(view==='triangle'&&selected>=0)){line(`Rx = ${active.length?active.map(v=>`(${fmt(v.x)})`).join(' + '):'0'} = ${fmt(result.x)}`);line(`Ry = ${active.length?active.map(v=>`(${fmt(v.y)})`).join(' + '):'0'} = ${fmt(result.y)}`);}
 line(`R = √((${fmt(r.x)})² + (${fmt(r.y)})²) = ${fmt(r.r)}`);
 if(r.t===null)line('R = 0: direction is undefined.');else{line(r.x===0?`x = 0: use the y-axis direction → ${fmt(r.t)}°`:`θ = atan(${fmt(r.y)} / ${fmt(r.x)}), with quadrant correction → ${fmt(r.t)}° CCW from +x`);line(VM.bearing(r.t));}
}
window.addEventListener('resize',()=>render());
render();
