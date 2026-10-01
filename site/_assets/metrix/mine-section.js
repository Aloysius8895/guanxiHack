// Works on initial load and the site's existing animated page transitions.
export function initMineSections(){
  document.querySelectorAll('[data-mine-story]:not([data-mine-initialized])').forEach(section=>{
    section.dataset.mineInitialized='true';const iframe=section.querySelector('iframe');let last=-1,wasVisible=false,scheduled=false;
    function update(){
      scheduled=false;if(!section.isConnected){cleanup();return;}
      const rect=section.getBoundingClientRect(),height=innerHeight,visible=rect.bottom>0&&rect.top<height;
      const progress=Math.max(0,Math.min(1,-rect.top/Math.max(1,rect.height-height)));
      if(Math.abs(progress-last)>.0005||visible!==wasVisible){iframe.contentWindow?.postMessage({type:'metrix-mine-progress',progress,visible},location.origin);last=progress;wasVisible=visible;}
    }
    function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(update);}}
    function message(event){
      if(event.origin!==location.origin||event.source!==iframe.contentWindow)return;
      if(event.data?.type==='metrix-mine-ready'){last=-1;update();}
      if(event.data?.type==='metrix-mine-scroll'){
        const wrapper=window.__lenisWrapper||window,delta=Number(event.data.delta);
        if(!Number.isFinite(delta))return;
        if(window.lenis?.scrollTo)window.lenis.scrollTo(window.lenis.targetScroll+delta,{immediate:!!event.data.immediate||matchMedia('(prefers-reduced-motion: reduce)').matches,duration:.55});
        else wrapper.scrollBy({top:delta,behavior:'instant'});
      }
      if(event.data?.type==='metrix-mine-select'){
        const progress=Math.max(0,Math.min(1,Number(event.data.progress)||0));
        const wrapper=window.__lenisWrapper;
        const offset=wrapper && wrapper!==window ? wrapper.scrollTop : scrollY;
        const top=section.getBoundingClientRect().top+offset+progress*(section.offsetHeight-innerHeight);
        if(window.lenis?.scrollTo)window.lenis.scrollTo(top,{immediate:matchMedia('(prefers-reduced-motion: reduce)').matches});
        else (wrapper||window).scrollTo({top,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
      }
    }
    function cleanup(){removeEventListener('scroll',schedule,true);removeEventListener('resize',schedule);removeEventListener('message',message);observer.disconnect();}
    addEventListener('scroll',schedule,{passive:true,capture:true});addEventListener('resize',schedule);addEventListener('message',message);
    iframe.addEventListener('load',()=>{last=-1;update();});const observer=new ResizeObserver(schedule);observer.observe(section);update();
  });
}
