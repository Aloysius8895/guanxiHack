// Shared UX modules survive the site's animated navigation.
// Page transitions and text animations mutate the DOM heavily, so re-scan at most once per frame.
function onDomChange(callback){
  let queued=false;
  new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;callback();});})
    .observe(document.documentElement,{childList:true,subtree:true});
}
// Heavy 3D embeds start when they are within ~1.5 screens or once the page is idle, so their
// setup never lands inside the page-entrance animation.
function deferFrames(){
  document.querySelectorAll('iframe[data-defer-src]:not([src])').forEach(frame=>{
    if(frame.dataset.deferWatch)return;frame.dataset.deferWatch='1';
    let io=null,idle=0;
    const start=()=>{if(frame.src)return;io?.disconnect();clearTimeout(idle);if(frame.isConnected)frame.src=frame.dataset.deferSrc;};
    const root=frame.closest('[data-barba="container"]');
    try{io=new IntersectionObserver(e=>{if(e.some(x=>x.isIntersecting))start();},{root:root&&root.scrollHeight>root.clientHeight?root:null,rootMargin:'25% 0px'});io.observe(frame);}catch{start();}
    // After a full load wait for the intro loader; after a page switch, for the entrance transition.
    const later=delay=>{idle=setTimeout(()=>('requestIdleCallback' in window?requestIdleCallback(start,{timeout:2000}):start()),delay);};
    if(window.__loaderDone)later(2500);
    else{const done=()=>{clearTimeout(idle);later(1200);};document.addEventListener('loader:done',done,{once:true});idle=setTimeout(()=>{document.removeEventListener('loader:done',done);later(0);},6000);}
  });
}
deferFrames();onDomChange(deferFrames);
import('/_assets/metrix/scroll-history.js');
import('/_assets/metrix/route-search.js').then(({initRouteSearch}) => {
  initRouteSearch();
  onDomChange(initRouteSearch);
});
// Mount the mine story after initial load and the existing animated page transitions.
if (!window.metrixMineBoot) {
  window.metrixMineBoot = true;
  import('/_assets/metrix/mine-section.js').then(({initMineSections}) => {
    initMineSections();
    onDomChange(initMineSections);
  });
}
// One delegated handler also covers forms reached through the existing page transitions.
if (!window.metrixProductReady) {
  window.metrixProductReady = true;
  document.addEventListener('submit', function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.matches('[data-metrix-brief]')) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (!form.reportValidity()) return;
    const data = new FormData(form);
    const zh = document.documentElement.lang.startsWith('zh');
    const content = (zh
      ? ['MetriX AI · 试点咨询简报', '',
        '姓名：' + (data.get('name') || ''), '邮箱：' + (data.get('email') || ''),
        '', '场景：', data.get('Message') || '', '',
        '本文件在本地生成，尚未发送给 MetriX AI。',
        '建议下一步：约定数据、基准与验收标准。']
      : ['MetriX AI · Pilot enquiry brief', '',
        'Name: ' + (data.get('name') || ''), 'Email: ' + (data.get('email') || ''),
        '', 'Scenario:', data.get('Message') || '', '',
        'Prepared locally. This file has not been sent to MetriX AI.',
        'Suggested next step: agree the data, baseline and acceptance criteria.']).join('\r\n');
    const url = URL.createObjectURL(new Blob(['\ufeff' + content], {type: 'text/plain;charset=utf-8'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'MetriX-AI-pilot-brief.txt';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    const status = form.parentElement.querySelector('.w-form-done');
    if (status) { status.style.display = 'block'; status.textContent = zh ? '简报已下载，尚未发送；请将文件分享给您的 MetriX AI 联系人。' : 'Brief downloaded. It has not been sent; share the file with your MetriX AI contact.'; }
  }, true);
}
