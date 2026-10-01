// Preserve each browser-history entry, including repeated visits to one URL.
(() => {
 if(window.metrixScrollHistory)return;window.metrixScrollHistory=true;
 const storage='metrix-scroll-positions-v1';let positions={};
 try{positions=JSON.parse(sessionStorage.getItem(storage)||'{}');}catch{}
 const fresh=()=>globalThis.crypto?.randomUUID?.()||`${Date.now()}-${Math.random()}`;
 const nativePush=history.pushState.bind(history),nativeReplace=history.replaceState.bind(history);
 let key=history.state?.metrixEntry||fresh(),pending=null,leaving=false,revision=0;
 const offset=()=>window.__lenisWrapper?.scrollTop??window.lenis?.scroll??scrollY;
 function save(){if(!leaving&&!pending){positions[key]=offset();try{sessionStorage.setItem(storage,JSON.stringify(positions));}catch{}}}
 nativeReplace({...history.state,metrixEntry:key},'');
 history.scrollRestoration='manual';
 history.replaceState=function(state,title,url){return nativeReplace({...state,metrixEntry:key},title,url);};
 history.pushState=function(state,title,url){save();key=fresh();pending=null;leaving=true;revision++;return nativePush({...state,metrixEntry:key},title,url);};
 addEventListener('popstate',event=>{save();key=event.state?.metrixEntry||fresh();pending=positions[key]??0;leaving=true;revision++;hold();},true);
 document.addEventListener('click',event=>{
   const a=event.target.closest?.('a[href]');
   if(!a||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||a.target==='_blank'||a.hasAttribute('download'))return;
   const url=new URL(a.href,location.href);if(url.origin!==location.origin)return;
   if(url.pathname===location.pathname&&url.search===location.search)return;
   // Freeze the clicked position: leave transitions scroll the old page before pushState runs.
   save();leaving=true;const from=location.href;
   setTimeout(()=>{if(location.href===from&&pending===null)leaving=false;},4000);
 },true);
 let saveTimer;addEventListener('scroll',()=>{clearTimeout(saveTimer);saveTimer=setTimeout(save,100);},{passive:true,capture:true});
 addEventListener('pagehide',save);
 // The site's transition code pins scrolling to window.__hardScrollLockY (0 for a new page) while
 // its clip animation runs; point that lock at the saved offset so it holds the right place.
 const locked=()=>!!(window.__lenisHeldForClip||window.__hardScrollLockActive);
 function pin(target){if(locked())window.__hardScrollLockY=target;}
 function restore(){
   if(pending===null){leaving=false;return;}
   const target=pending,version=revision;let frames=0,stable=0;
   const step=()=>{
     if(version!==revision)return;
     pin(target);
     const wrapper=window.__lenisWrapper;
     if(window.lenis?.scrollTo){window.lenis.resize();window.lenis.scrollTo(target,{immediate:true,force:true});}
     else (wrapper||window).scrollTo({top:target,behavior:'instant'});
     stable=!locked()&&Math.abs(offset()-target)<2?stable+1:0;
     // Keep going until the lock is released and layout has settled (capped at ~8s).
     if(++frames<480&&(stable<20||frames<30)){requestAnimationFrame(step);return;}
     pending=null;leaving=false;save();
   };
   requestAnimationFrame(()=>requestAnimationFrame(step));
 }
 // Each Barba container is its own scroller. On Back/Forward, every new container is placed at the
 // saved offset from the frame it appears, so the transition reveals that section rather than the top.
 function hold(){
   const target=pending,version=revision,existing=new Set(document.querySelectorAll('[data-barba="container"]'));
   const apply=()=>{
     if(version!==revision||pending===null)return;
     pin(target);
     for(const c of document.querySelectorAll('[data-barba="container"]'))
       if(!existing.has(c)&&Math.abs(c.scrollTop-target)>1)c.scrollTop=target;
     requestAnimationFrame(apply);
   };
   apply();
 }
 addEventListener('page:transition:after',restore);
 // Full-document returns and reloads use the same saved entry after the loader.
 const navigation=performance.getEntriesByType('navigation')[0];
 if(navigation&&['back_forward','reload'].includes(navigation.type)&&positions[key]!=null){
   pending=positions[key];leaving=true;
   document.addEventListener('loader:done',restore,{once:true});
   addEventListener('load',()=>{if(window.__loaderDone)restore();},{once:true});
 }
 addEventListener('pageshow',event=>{if(event.persisted){pending=positions[key]??0;restore();}});
})();
