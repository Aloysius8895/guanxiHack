// A weighted graph: cost = segment length * illustrative terrain resistance.
// Dijkstra supplies both the search order and the lowest-cost connected path.
function network() {
  const nodes = Array.from({length:35}, (_,i) => ({x:(i%7)/6,y:Math.floor(i/7)/4}));
  const edges=[];
  nodes.forEach((n,i)=>{
    const col=i%7,row=Math.floor(i/7);
    for(const j of [col<6?i+1:-1,row<4?i+7:-1,col<6&&row<4?i+8:-1]) {
      if(j<0)continue;
      const rough=(i===10||i===17||i===18||j===18)?4:1+((i*13+j*7)%9)/12;
      edges.push({a:i,b:j,cost:Math.hypot(n.x-nodes[j].x,n.y-nodes[j].y)*rough,rough:rough>3});
    }
  });
  const start=28,end=6,dist=nodes.map(()=>Infinity),prev=[],visited=[],done=new Set();dist[start]=0;
  while(done.size<nodes.length){
    let u=-1;nodes.forEach((_,i)=>{if(!done.has(i)&&(u<0||dist[i]<dist[u]))u=i;});
    if(u<0||!Number.isFinite(dist[u]))break;
    done.add(u);visited.push(u);if(u===end)break;
    edges.forEach(e=>{const v=e.a===u?e.b:e.b===u?e.a:-1;if(v<0||done.has(v))return;const cost=dist[u]+e.cost;if(cost<dist[v]){dist[v]=cost;prev[v]=u;}});
  }
  const path=[];for(let n=end;n!==undefined;n=prev[n])path.unshift(n);
  return {nodes,edges,visited,path,start,end,cost:dist[end]};
}
export function initRouteSearch(){
 document.querySelectorAll('[data-route-search]:not([data-route-ready])').forEach(section=>{
  section.dataset.routeReady='true';
  const canvas=section.querySelector('canvas'),ctx=canvas.getContext('2d');if(!ctx)return;
  const graph=network(),status=section.querySelector('[data-route-status]'),metric=section.querySelector('[data-route-metric]'),button=section.querySelector('[data-route-pause]');
  const stage=section.querySelector('.metrix-route-sticky')||section;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let width=0,height=0,visible=false,paused=false,elapsed=0,clock=0,last=0,raf=0;
  // The real site photo is shown first; a greyscale copy stays as a faint ghost under the wireframe.
  let photo=null,ghost=null;
  if(section.dataset.routePhoto){
    const img=new Image();img.decoding='async';
    img.onload=()=>{
      photo=img;ghost=document.createElement('canvas');ghost.width=img.naturalWidth;ghost.height=img.naturalHeight;
      const g=ghost.getContext('2d');g.drawImage(img,0,0);
      try{const data=g.getImageData(0,0,ghost.width,ghost.height),px=data.data;for(let i=0;i<px.length;i+=4){const v=px[i]*.3+px[i+1]*.59+px[i+2]*.11;px[i]=px[i+1]=px[i+2]=v;}g.putImageData(data,0,0);}catch{}
      draw();
    };
    img.src=section.dataset.routePhoto;
  }
  function cover(image,zoom){const s=Math.max(width/image.width,height/image.height)*zoom,w=image.width*s,h=image.height*s;ctx.drawImage(image,(width-w)/2,(height-h)*.55,w,h);}
  // 0 = photo only, 1 = fully digitised; driven by how far the pinned stage has been scrolled.
  function progress(){const r=section.getBoundingClientRect(),track=r.height-stage.clientHeight;return track>0?Math.min(1,Math.max(0,-r.top/track)):1;}
  const ease=x=>x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2;
  function resize(){width=stage.clientWidth;height=stage.clientHeight;const dpr=Math.min(devicePixelRatio||1,2);canvas.width=width*dpr;canvas.height=height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);draw();}
  function project(x,y,t=0){
    const mobile=width<700,depth=.58+y*.42;
    return {x:width/2+(x-.5)*width*(mobile?.95:.87)*depth,y:height*(mobile?.14:.1)+y*height*(mobile?.41:.66)+Math.sin(x*9+y*5+t*.18)*height*.022};
  }
  function line(a,b,color,lineWidth=1,dash=[]){ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.setLineDash(dash);ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();ctx.setLineDash([]);}
  function rover(p,angle=0){
    ctx.save();ctx.translate(p.x,p.y);ctx.rotate(angle);ctx.shadowBlur=18;ctx.shadowColor='#ff9a46';ctx.fillStyle='#e2e9df';ctx.strokeStyle='#101318';ctx.lineWidth=1;
    for(let side of [-1,1])for(let x of [-7,0,7]){ctx.fillStyle='#6f7884';ctx.fillRect(x-2,side*7-3,4,6);}
    ctx.fillStyle='#e8ebef';ctx.beginPath();ctx.roundRect(-10,-6,20,12,4);ctx.fill();ctx.stroke();ctx.fillStyle='#ff8a28';ctx.fillRect(0,-3,6,6);ctx.restore();
  }
  // Transparent wireframe of the mine site, drawn in the same warped plane as the network.
  // The open pit sits over the high-cost edges, so the search visibly routes around it.
  const PIT={x:.57,y:.4,rx:.15,ry:.24};
  function ring(c,s,k,t){const out=[];for(let a=0;a<=Math.PI*2+.01;a+=Math.PI/40){const w=1+.07*Math.sin(3*a+k)+.04*Math.sin(5*a-k);out.push(project(c.x+Math.cos(a)*c.rx*s*w,c.y+Math.sin(a)*c.ry*s*w,t));}return out;}
  function poly(points,stroke,lineWidth=1,dash=[],fill){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));if(fill){ctx.fillStyle=fill;ctx.fill();}ctx.strokeStyle=stroke;ctx.lineWidth=lineWidth;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
  function tag(p,text,color='rgba(176,186,198,.62)',size=9){ctx.font=size+'px monospace';ctx.fillStyle=color;ctx.fillText(text,p.x,p.y);}
  function mineSite(t){
    [1,.83,.67,.52,.38,.25].forEach((s,i)=>{
      const pts=ring(PIT,s,1.3,t);
      poly(pts,i===5?'rgba(244,121,32,.5)':`rgba(200,210,222,${.42-i*.04})`,1,i===0?[7,5]:[3,4],i===5?'rgba(244,121,32,.035)':'rgba(150,166,186,.018)');
      if(i<5&&i%2===0)tag({x:pts[66].x+4,y:pts[66].y-3},`-${(i+1)*15} M`,'rgba(170,180,192,.55)',8);
    });
    // Haul ramp spiralling down the benches.
    for(const off of [-.035,.035]){const pts=[];for(let k=0;k<=60;k++){const f=k/60,a=Math.PI*.3+f*Math.PI*1.8,s=1.04-f*.74+off;pts.push(project(PIT.x+Math.cos(a)*PIT.rx*s,PIT.y+Math.sin(a)*PIT.ry*s,t));}poly(pts,'rgba(232,206,156,.5)',1.2,[2,4]);}
    const rim=ring(PIT,1,1.3,t);tag({x:rim[40].x-150,y:rim[40].y},'OPEN PIT · PHASE 2');tag({x:rim[40].x-150,y:rim[40].y+13},'STEEP BENCHES / HIGH COST','rgba(244,121,32,.7)',8);
    const ramp=project(PIT.x+Math.cos(Math.PI*.3)*PIT.rx*1.1,PIT.y+Math.sin(Math.PI*.3)*PIT.ry*1.1,t);tag({x:ramp.x+10,y:ramp.y-6},'HAUL RAMP 10%','rgba(226,200,150,.62)',8);
    // Waste dump: stacked lifts of a stockpile mound.
    const dump={x:.2,y:.13,rx:.08,ry:.1};[1,.68,.38].forEach((s,i)=>poly(ring(dump,s,4,t),`rgba(196,206,218,${.26-i*.05})`,1,[3,4],'rgba(150,164,182,.03)'));
    const d=project(dump.x-.06,dump.y-.14,t);tag(d,'WASTE DUMP');
    // ROM pad and crusher near the haul destination.
    const pad=[[.8,.74],[.95,.74],[.95,.9],[.8,.9],[.8,.74]].map(([x,y])=>project(x,y,t));poly(pad,'rgba(196,206,218,.3)',1,[5,4],'rgba(150,164,182,.035)');
    for(let k=1;k<4;k++)poly([project(.8+k*.0375,.74,t),project(.8+k*.0375-.03,.9,t)],'rgba(196,206,218,.12)',1,[2,5]);
    tag({x:pad[3].x,y:pad[3].y+16},'ROM PAD / CRUSHER');
    // Underground decline running out from a portal on the pit wall.
    for(const off of [-.012,.012])poly([project(.74,.62+off,t),project(.88,.56+off,t),project(1.02,.6+off,t)],'rgba(120,170,220,.3)',1,[8,6]);
    const portal=project(.74,.62,t);tag({x:portal.x+6,y:portal.y+22},'UNDERGROUND DECLINE','rgba(140,180,220,.6)',8);
  }
  function draw(){
    const scroll=progress(),reveal=ease(Math.min(1,Math.max(0,(scroll-.1)/.42))),scanned=reveal>=1;
    const scanY=height*(-.04+reveal*1.08),wave=reduced.matches?0:clock/1000;
    const t=reduced.matches?10:elapsed/1000,phase=scanned?t%16:0,found=scanned&&(phase>=6||reduced.matches);
    const explored=new Set(graph.visited.slice(0,Math.floor(Math.min(1,phase/6)*graph.visited.length)));
    ctx.clearRect(0,0,width,height);ctx.fillStyle='#0d0f12';ctx.fillRect(0,0,width,height);
    const zoom=1.04+scroll*.1;
    // Below the scan line: the real mine.
    if(photo&&scanY<height){ctx.save();ctx.beginPath();ctx.rect(0,Math.max(0,scanY),width,height);ctx.clip();cover(photo,zoom);ctx.fillStyle='rgba(8,10,13,.28)';ctx.fillRect(0,0,width,height);ctx.restore();}
    // Above it: the dark survey view with a faint trace of the photo.
    ctx.save();ctx.beginPath();ctx.rect(0,0,width,Math.max(0,scanY));ctx.clip();
    const glow=ctx.createRadialGradient(width*.55,height*.4,0,width*.55,height*.4,width*.65);glow.addColorStop(0,'#1e242c');glow.addColorStop(1,'#0b0d10');ctx.fillStyle=glow;ctx.fillRect(0,0,width,height);
    if(ghost){ctx.globalAlpha=.09;cover(ghost,zoom);ctx.globalAlpha=1;}
    {const t=wave;
    // Warped perspective grid under the network, matching the reference's terrain plane.
    for(let x=-.12;x<1.13;x+=.05){let p=null;for(let y=-.1;y<=1.12;y+=.035){const q=project(x,y,t);if(p)line(p,q,'rgba(160,174,192,.055)');p=q;}}
    for(let y=-.1;y<=1.12;y+=.05){let p=null;for(let x=-.12;x<1.13;x+=.035){const q=project(x,y,t);if(p)line(p,q,'rgba(160,174,192,.055)');p=q;}}
    mineSite(t);
    const pts=graph.nodes.map((n,i)=>project(n.x+(i%7===0||i%7===6?0:Math.sin(i*13)*.033),n.y+Math.sin(i*17)*.027,t));
    const scanY=height*(.12+(phase/16)*.63);const scan=ctx.createLinearGradient(0,scanY-40,0,scanY+3);scan.addColorStop(0,'transparent');scan.addColorStop(1,'rgba(196,212,232,.05)');ctx.fillStyle=scan;ctx.fillRect(0,scanY-40,width,43);
    graph.edges.forEach(e=>{
      const active=explored.has(e.a)&&explored.has(e.b);
      line(pts[e.a],pts[e.b],e.rough?'rgba(244,121,32,.32)':active&&!found?'rgba(232,236,242,.7)':'rgba(176,186,200,.24)',active?1.3:1,[3,5]);
    });
    if(found){
      const amount=reduced.matches?1:Math.min(1,(phase-6)/2);
      const count=(graph.path.length-1)*amount;
      for(let i=0;i<count;i++){
        const a=pts[graph.path[i]],b=pts[graph.path[i+1]],fraction=Math.min(1,count-i);if(!b)break;
        const end={x:a.x+(b.x-a.x)*fraction,y:a.y+(b.y-a.y)*fraction};
        ctx.shadowColor='#f47920';ctx.shadowBlur=16;line(a,end,'#ff8a2b',2.5);ctx.shadowBlur=0;
      }
      const travel=reduced.matches?.56:Math.max(0,Math.min(.999,(phase-8)/7));
      const segment=travel*(graph.path.length-1),index=Math.floor(segment),f=segment-index;
      const a=pts[graph.path[index]],b=pts[graph.path[index+1]]||a;
      rover({x:a.x+(b.x-a.x)*f,y:a.y+(b.y-a.y)*f},Math.atan2(b.y-a.y,b.x-a.x));
    }
    pts.forEach((p,i)=>{
      const onPath=found&&graph.path.includes(i),endpoint=i===graph.start||i===graph.end;
      ctx.fillStyle=onPath?'#ff9a46':explored.has(i)?'#e4e8ee':'#6f7884';
      ctx.beginPath();ctx.arc(p.x,p.y,endpoint?5:2.7,0,Math.PI*2);ctx.fill();
      if(endpoint){ctx.strokeStyle=onPath?'#ff9a4680':'#aab4c266';ctx.beginPath();ctx.arc(p.x,p.y,12+Math.sin(t*2)*2,0,Math.PI*2);ctx.stroke();ctx.font='10px monospace';ctx.fillStyle='#dde2e8';ctx.fillText(i===graph.start?'START / R01':'TARGET / S06',Math.min(width-90,Math.max(12,p.x-26)),p.y-23);}
      else if(i%4===0){ctx.font='8px monospace';ctx.fillStyle='#7c8591';ctx.fillText('N'+String(i+1).padStart(2,'0'),p.x+9,p.y-7);}
    });
    }
    ctx.restore();
    if(reveal>0&&!scanned){
      const band=ctx.createLinearGradient(0,scanY-70,0,scanY);band.addColorStop(0,'rgba(244,121,32,0)');band.addColorStop(1,'rgba(244,121,32,.2)');ctx.fillStyle=band;ctx.fillRect(0,scanY-70,width,70);
      ctx.shadowColor='#f47920';ctx.shadowBlur=14;line({x:0,y:scanY},{x:width,y:scanY},'rgba(255,176,104,.95)',1.5);ctx.shadowBlur=0;
      tag({x:width-150,y:scanY-10},`SURVEY SCAN ${Math.round(reveal*100)}%`,'rgba(255,190,130,.9)',10);
    }
    const shade=ctx.createLinearGradient(0,height*.55,0,height);shade.addColorStop(0,'transparent');shade.addColorStop(1,'#0a0c0f');ctx.fillStyle=shade;ctx.fillRect(0,height*.55,width,height*.45);
    const label=!scanned?(reveal>0?'DIGITISING SITE SURVEY':'LIVE SITE / PIT 02'):found?(phase>=8?'OPTIMAL ROUTE / READY':'LOWEST-COST PATH FOUND'):'SEARCHING CANDIDATE ROUTES';
    if(status.textContent!==label)status.textContent=label;
    const value=!scanned?`TERRAIN MODEL ${Math.round(reveal*100)}%`:found?`${graph.path.length} WAYPOINTS / COST ${graph.cost.toFixed(2)} AU`:`${explored.size} / ${graph.nodes.length} NODES EVALUATED`;
    if(metric.textContent!==value)metric.textContent=value;
    section.dataset.routePhase=!scanned?'survey':found?'optimal':'searching';
    // Restart the search each time the survey is scrolled back over.
    if(!scanned)elapsed=0;
  }
  function tick(now){raf=0;if(!section.isConnected){observer.disconnect();resizer.disconnect();document.removeEventListener('visibilitychange',sync);reduced.removeEventListener('change',sync);return;}if(last&&!paused){const dt=Math.min(now-last,80);elapsed+=dt;clock+=dt;}last=now;draw();if(visible&&!document.hidden)raf=requestAnimationFrame(tick);}
  function sync(){cancelAnimationFrame(raf);raf=0;last=0;draw();if(visible&&!document.hidden)raf=requestAnimationFrame(tick);}
  button.addEventListener('click',()=>{paused=!paused;button.setAttribute('aria-pressed',String(paused));button.textContent=paused?'Resume animation ▷':'Pause animation Ⅱ';sync();});
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();});observer.observe(section);
  const resizer=new ResizeObserver(resize);resizer.observe(stage);
  document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);resize();
 });
}
