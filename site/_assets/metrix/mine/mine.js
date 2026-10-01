import * as THREE from '/_assets/metrix/three/build/three.module.js';
import {createRover} from './rover-model.js';

const root=document.querySelector('.mine-scene'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
const bg=document.querySelector('.mine-background'),buttons=[...document.querySelectorAll('[data-scene]')],pauseButton=document.querySelector('.pause');
let progress=0,thermalMix=0,visible=window.parent===window,paused=false,mode=0,time=0,previous=0,frame=0;
function setProgress(value){
  progress=Math.max(0,Math.min(1,value));mode=progress>=.5?1:0;
  root.dataset.mode=mode?'thermal':'detection';root.style.setProperty('--progress',`${progress*100}%`);
  buttons.forEach((button,index)=>button.setAttribute('aria-pressed',String(index===mode)));
  document.querySelector('.telemetry-mode').textContent=mode?'ALERT: THERMAL ANOMALY':'SCAN MODE: VISION + LIDAR';
  document.querySelector('.telemetry-status').textContent=mode?'TARGET ZONE LOCATED · REVIEW REQUESTED':'6 FEATURES TRACKED · ROUTE MAPPED';
  if(reduced.matches)thermalMix=mode;
}
buttons.forEach(button=>button.addEventListener('click',()=>{
  const value=Number(button.dataset.scene)?.8:.15;setProgress(value);
  if(window.parent!==window)window.parent.postMessage({type:'metrix-mine-select',progress:value},location.origin);
}));
pauseButton.addEventListener('click',()=>{paused=!paused;root.classList.toggle('paused',paused);pauseButton.setAttribute('aria-pressed',String(paused));pauseButton.setAttribute('aria-label',paused?'Resume scene animation':'Pause scene animation');pauseButton.textContent=paused?'▶':'Ⅱ';});
window.addEventListener('message',event=>{if(event.origin!==location.origin||event.source!==window.parent||event.data?.type!=='metrix-mine-progress')return;setProgress(event.data.progress);visible=!!event.data.visible;});
window.parent.postMessage({type:'metrix-mine-ready'},location.origin);
// Iframes do not deliver wheel/touch events to the host's Lenis container.
function forwardScroll(delta,immediate=false){if(window.parent!==window)window.parent.postMessage({type:'metrix-mine-scroll',delta,immediate},location.origin);}
addEventListener('wheel',event=>{if(window.parent===window||event.ctrlKey)return;event.preventDefault();forwardScroll(event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?innerHeight:1));},{passive:false});
let touchY=null;
addEventListener('touchstart',event=>{touchY=event.touches.length===1?event.touches[0].clientY:null;},{passive:true});
addEventListener('touchmove',event=>{if(touchY===null||event.touches.length!==1||window.parent===window)return;const y=event.touches[0].clientY;event.preventDefault();forwardScroll(touchY-y,true);touchY=y;},{passive:false});
addEventListener('touchend',()=>{touchY=null;},{passive:true});
addEventListener('keydown',event=>{if(event.target.closest('button')&&(event.key===' '||event.key==='Enter'))return;const delta={ArrowDown:80,ArrowUp:-80,PageDown:innerHeight*.8,PageUp:-innerHeight*.8,' ':innerHeight*.8}[event.key];if(delta!==undefined&&window.parent!==window){event.preventDefault();forwardScroll(event.shiftKey?-delta:delta);}});

// Thermal colors are illustrative; underlying rock features come from the scene plate.
const thermal=document.querySelector('#thermal'),thermalContext=thermal.getContext('2d'),thermalSource=document.createElement('canvas');
thermalSource.width=200;thermalSource.height=120;
const sourceContext=thermalSource.getContext('2d',{willReadFrequently:true}),plate=new Image();let thermalPixels;
plate.onload=()=>{sourceContext.drawImage(plate,plate.width*.66,plate.height*.26,plate.width*.31,plate.height*.35,0,0,200,120);thermalPixels=sourceContext.getImageData(0,0,200,120);drawThermal(0);};plate.src='tunnel.webp';
const palette=[[3,5,29],[24,7,91],[81,8,161],[165,13,173],[235,38,92],[255,114,24],[255,212,53],[255,255,207]];
function drawThermal(t){
  if(!thermalPixels)return;const output=sourceContext.createImageData(200,120);
  for(let y=0;y<120;y++)for(let x=0;x<200;x++){
    const i=(y*200+x)*4,luminance=(thermalPixels.data[i]+thermalPixels.data[i+1]+thermalPixels.data[i+2])/765;
    const hotspot=Math.exp(-((x-126)**2/520+(y-51)**2/205));
    const value=Math.min(.999,.05+luminance*.30+hotspot*(.67+.025*Math.sin(t))),p=value*7,low=Math.floor(p),fraction=p-low;
    for(let channel=0;channel<3;channel++)output.data[i+channel]=palette[low][channel]*(1-fraction)+palette[Math.min(7,low+1)][channel]*fraction;
    output.data[i+3]=255;
  }
  sourceContext.putImageData(output,0,0);thermalContext.drawImage(thermalSource,0,0,400,240);
  thermalContext.fillStyle='#ffffff15';thermalContext.fillRect(0,(t*23)%240,400,2);
}
let renderer,scene,camera,rover,shadow;
try{
  renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;renderer.setClearColor(0x000000,0);
  document.querySelector('#rover-stage').append(renderer.domElement);scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(39,innerWidth/innerHeight,.1,100);
  camera.position.set(8,6.2,11);camera.lookAt(0,1.45,0);scene.add(new THREE.HemisphereLight(0xc9def1,0x323024,2.5));
  const key=new THREE.DirectionalLight(0xe2f0ff,4.2);key.position.set(-4,8,6);scene.add(key);
  const fill=new THREE.DirectionalLight(0xffc780,1.2);fill.position.set(5,3,-5);scene.add(fill);
  const front=new THREE.DirectionalLight(0xe5f3ff,1);front.position.set(8,2,9);scene.add(front);
  rover=createRover();scene.add(rover);
  // Soft contact shadow grounds the original model on the photographed mine floor.
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=256;shadowCanvas.height=256;
  const ctx=shadowCanvas.getContext('2d'),gradient=ctx.createRadialGradient(128,128,25,128,128,124);
  gradient.addColorStop(0,'rgba(0,0,0,.85)');gradient.addColorStop(.5,'rgba(0,0,0,.48)');gradient.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,256,256);
  shadow=new THREE.Mesh(new THREE.PlaneGeometry(7,6),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false,opacity:.83}));
  shadow.rotation.x=-Math.PI/2;shadow.position.y=-.06;scene.add(shadow);root.dataset.webgl='ready';
}catch(error){
  renderer=null;root.dataset.webgl='fallback';const image=new Image();image.src='../components/six-wheel-chassis.webp';image.alt='MetriX six-wheel rover';image.className='fallback-rover';document.querySelector('#rover-stage').append(image);console.warn('Mine scene uses static rover fallback:',error.message);
}
addEventListener('resize',()=>{if(!renderer)return;renderer.setSize(innerWidth,innerHeight);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();});
function animate(now){
  requestAnimationFrame(animate);const dt=Math.min((now-previous)/1000,.05);previous=now;if(!visible||document.hidden)return;
  if(!paused&&!reduced.matches)time+=dt;thermalMix+=(mode-thermalMix)*(reduced.matches?1:Math.min(1,dt*2.6));
  const mobile=innerWidth<701,drift=Math.sin(time*.24)*.008;
  bg.style.transform=`scale(${1.035+progress*.025}) translate(${(-thermalMix*.7+drift*10).toFixed(3)}%,${(-progress*.35).toFixed(3)}%)`;
  if(renderer){
    camera.clearViewOffset();const x=mobile?.43-.15*thermalMix:.47-.15*thermalMix,y=mobile?.505:.565;
    camera.setViewOffset(innerWidth,innerHeight,(.5-x)*innerWidth,(.5-y)*innerHeight,innerWidth,innerHeight);camera.fov=mobile?57:39;camera.updateProjectionMatrix();
    const travel=Math.sin(time*.48),travelZ=Math.sin(time*.48+.5);
    rover.rotation.y=.3+thermalMix*.72+Math.sin(time*.48)*.10;
    rover.position.set(travel*.42,Math.sin(time*3.2)*.018,travelZ*.19);
    rover.rotation.z=Math.sin(time*2.1)*.008;
    rover.scale.setScalar(mobile?.65:.74);
    const wheelRotation=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),-travel*1.3);
    rover.userData.wheels.forEach(wheel=>wheel.quaternion.copy(wheel.userData.restQuaternion).multiply(wheelRotation));
    const mast=rover.userData.mast;
    mast.quaternion.copy(mast.userData.restQuaternion).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),Math.sin(time*.62)*.42));
    shadow.scale.setScalar(mobile?.65:.74);shadow.position.x=rover.position.x;shadow.position.z=rover.position.z;shadow.rotation.z=-rover.rotation.y;renderer.render(scene,camera);
    root.dataset.motionTime=time.toFixed(3);
    const sensor=rover.localToWorld(new THREE.Vector3(-.1,3.48,-.67)).project(camera);
    const sx=(sensor.x*.5+.5)*1440,sy=(-sensor.y*.5+.5)*900;
    const target=document.querySelector('.thermal-window').getBoundingClientRect();
    const tx=target.left/innerWidth*1440,center=(target.top+target.bottom)/2/innerHeight*900;
    const spread=(target.height/2/innerHeight*900)*thermalMix;
    const ty=center-spread,by=center+spread;
    const paths=document.querySelectorAll('.scan-beam path');
    paths[0].setAttribute('d',`M ${sx} ${sy} L ${tx} ${ty} L ${tx} ${by} Z`);
    paths[1].setAttribute('d',`M ${sx} ${sy} L ${tx} ${ty} M ${sx} ${sy} L ${tx} ${by}`);
  }
  if(frame++%5===0&&!paused)drawThermal(time);
}
setProgress(0);requestAnimationFrame(animate);
