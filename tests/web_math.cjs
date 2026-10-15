const assert=require('node:assert/strict');
const M=require('../web/math.js');
let checks=0;
function close(a,b,tol=1e-10){assert.ok(Math.abs(a-b)<=tol*Math.max(1,Math.abs(b)),`${a} != ${b}`);checks++;}
for(const [d,t]of Object.entries({EN:60,WN:120,ES:300,WS:240,NE:30,SE:330,NW:150,SW:210})){assert.equal(M.compass(30,d),t);checks++;for(const a of [0,90])assert.ok(M.compass(a,d)>=0&&M.compass(a,d)<360);}
const v=M.polar(24,M.compass(30,'EN'));close(v.x,12);close(v.y,12*Math.sqrt(3));
assert.equal(M.polar(0,90).t,null);assert.equal(M.sum([]).t,null);assert.equal(M.sum([M.polar(24,30),M.polar(24,210)]).r,0);
assert.equal(M.sum([M.components(3,0),M.components(0,4)]).r,5);
assert.equal(M.sum([M.components(1e9,0),M.components(-1e9+.001,0)]).near,true);
for(const s of ['', ' ', '1e3','2+3','1/2','1.2.3','-','.','1000000001','0.0000000001','0'.repeat(19)])assert.throws(()=>M.decimal(s));
for(const s of ['0','-3.5','1000000000','.000000001','-0.000000001'])close(M.decimal(s),Number(s));
assert.throws(()=>M.compass(91,'EN'));assert.throws(()=>M.compass(-1,'EN'));
let seed=84;function rng(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2**32;}
for(let i=0;i<2000;i++){const r=rng()*1e9,a=rng()*2e9-1e9,v=M.polar(r,a),t=M.normalize(a);close(v.x,r*Math.cos(t*Math.PI/180));close(v.y,r*Math.sin(t*Math.PI/180));const c=M.components(v.x,v.y);close(c.r,r);assert.ok(c.t>=0&&c.t<360);}
for(const [x,y,t]of [[3,4,53.13010235415598],[-3,4,126.869897645844],[-3,-4,233.130102354156],[3,-4,306.869897645844],[0,1,90],[0,-1,270],[1,0,0],[-1,0,180]])close(M.components(x,y).t,t);
console.log(`Browser math: ${checks} numerical assertions plus invalid-input, zero, cancellation and quadrant checks passed`);
