/* Shared browser math, also exercised in Node. Does not emulate TI BCD numbers. */
(function(root){
'use strict';
const normalize=a=>{const t=a-360*Math.floor(a/360);return t>=360?0:t;};
function polar(r,t){t=normalize(t);const a=t>=180?t-180:t,sign=t>=180?-1:1;
let x=sign*r*Math.cos(a*Math.PI/180),y=sign*r*Math.sin(a*Math.PI/180);
if(t===0||t===180)y=0;if(t===90||t===270)x=0;return {x,y,r,t:r===0?null:t,type:'polar'};}
function compass(a,d){const map={EN:90-a,WN:90+a,ES:270+a,WS:270-a,NE:a,SE:360-a,NW:180-a,SW:180+a};
if(!(d in map)||a<0||a>90)throw Error('Compass angles must be between 0° and 90°.');return normalize(map[d]);}
function components(x,y){return {x,y,r:Math.hypot(x,y),t:x===0&&y===0?null:normalize(Math.atan2(y,x)*180/Math.PI),type:'xy'};}
function sum(vectors){let x=0,y=0,total=0;const points=[{x:0,y:0}];for(const v of vectors){x+=v.x;y+=v.y;total+=v.r;points.push({x,y});}
return {...components(x,y),near:Math.hypot(x,y)>0&&Math.hypot(x,y)<=1e-12*total,points};}
function decimal(s){if(!/^-?(?:\d+(?:\.\d*)?|\.\d+)$/.test(s)||s.length>18)throw Error('Enter a decimal number, without units, EE or expressions.');const v=Number(s);
if(!Number.isFinite(v)||Math.abs(v)>1e9||(v!==0&&Math.abs(v)<1e-9))throw Error('Use 0, or an absolute value from 0.000000001 to 1000000000.');return v;}
function bearing(t){if(t===null)return 'No defined direction';if(t===0)return 'East';if(t===90)return 'North';if(t===180)return 'West';if(t===270)return 'South';
const f=n=>Number(n.toPrecision(9)).toString();if(t<90)return f(t)+'° north of east';if(t<180)return f(180-t)+'° north of west';if(t<270)return f(t-180)+'° south of west';return f(360-t)+'° south of east';}
const api={normalize,polar,compass,components,sum,decimal,bearing};root.VectorMath=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
