import{af as h,ag as D,ah as M}from"./index-BdT8h_5n.js";import"./frappe-ui-5f3Xtay5.js";/*!
 * (C) Ionic http://ionicframework.com - MIT License
 */const G=(n,m,g,p,X)=>{const c=n.ownerDocument.defaultView;let s=h(n);const w=t=>{const{startX:e}=t;return s?e>=c.innerWidth-50:e<=50},i=t=>s?-t.deltaX:t.deltaX,f=t=>s?-t.velocityX:t.velocityX;return D({el:n,gestureName:"goback-swipe",gesturePriority:101,threshold:10,canStart:t=>(s=h(n),w(t)&&m()),onStart:g,onMove:t=>{const e=i(t)/c.innerWidth;p(e)},onEnd:t=>{const o=i(t),e=c.innerWidth,r=o/e,a=f(t),v=e/2,l=a>=0&&(a>.2||o>v),u=(l?1-r:r)*e;let d=0;if(u>5){const y=u/Math.abs(a);d=Math.min(y,540)}X(l,r<=0?.01:M(0,r,.9999),d)}})};export{G as createSwipeBackGesture};
//# sourceMappingURL=swipe-back-B_jwi9vK.js.map
