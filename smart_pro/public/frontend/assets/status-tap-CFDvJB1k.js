var d=(n,a,o)=>new Promise((s,t)=>{var r=e=>{try{i(o.next(e))}catch(c){t(c)}},l=e=>{try{i(o.throw(e))}catch(c){t(c)}},i=e=>e.done?s(e.value):Promise.resolve(e.value).then(r,l);i((o=o.apply(n,a)).next())});import{ao as p,ap as m,aq as w,ar as h,as as f}from"./index-C-hcTcxK.js";import"./frappe-ui-5f3Xtay5.js";/*!
 * (C) Ionic http://ionicframework.com - MIT License
 */const v=()=>{const n=window;n.addEventListener("statusTap",()=>{p(()=>{const a=n.innerWidth,o=n.innerHeight,s=document.elementFromPoint(a/2,o/2);if(!s)return;const t=m(s);t&&new Promise(r=>w(t,r)).then(()=>{h(()=>d(void 0,null,function*(){t.style.setProperty("--overflow","hidden"),yield f(t,300),t.style.removeProperty("--overflow")}))})})})};export{v as startStatusTap};
//# sourceMappingURL=status-tap-CFDvJB1k.js.map
