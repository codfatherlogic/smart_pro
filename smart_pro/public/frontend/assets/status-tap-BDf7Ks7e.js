var d=(o,a,n)=>new Promise((s,t)=>{var r=e=>{try{i(n.next(e))}catch(c){t(c)}},l=e=>{try{i(n.throw(e))}catch(c){t(c)}},i=e=>e.done?s(e.value):Promise.resolve(e.value).then(r,l);i((n=n.apply(o,a)).next())});import{an as p,ao as m,ap as w,aq as h,ar as f}from"./index-BdT8h_5n.js";import"./frappe-ui-5f3Xtay5.js";/*!
 * (C) Ionic http://ionicframework.com - MIT License
 */const v=()=>{const o=window;o.addEventListener("statusTap",()=>{p(()=>{const a=o.innerWidth,n=o.innerHeight,s=document.elementFromPoint(a/2,n/2);if(!s)return;const t=m(s);t&&new Promise(r=>w(t,r)).then(()=>{h(()=>d(void 0,null,function*(){t.style.setProperty("--overflow","hidden"),yield f(t,300),t.style.removeProperty("--overflow")}))})})})};export{v as startStatusTap};
//# sourceMappingURL=status-tap-BDf7Ks7e.js.map
