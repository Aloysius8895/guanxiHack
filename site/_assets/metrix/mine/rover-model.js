import * as THREE from '/_assets/metrix/three/build/three.module.js';
import {RoundedBoxGeometry} from '/_assets/metrix/three/examples/jsm/geometries/RoundedBoxGeometry.js';
import {mergeGeometries} from '/_assets/metrix/three/examples/jsm/utils/BufferGeometryUtils.js';
export function createRover(){
const mat=(color,metalness=.1,roughness=.55)=>new THREE.MeshStandardMaterial({color,metalness,roughness});const white=mat(0xf1f0ed,.25,.42),black=mat(0x111b25,.72,.35),dark=mat(0x080d12,.34,.7),steel=mat(0x71889a,.84,.28),blue=new THREE.MeshStandardMaterial({color:0x006fe9,emissive:0x003b84,emissiveIntensity:.7,metalness:.45,roughness:.28}),purple=mat(0x35527e,.56,.35),red=mat(0xc83524,.35,.35),glass=mat(0x05131f,.75,.11);
function mesh(parent,geo,m,x=0,y=0,z=0){let o=new THREE.Mesh(geo,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
function box(parent,w,h,d,m,x=0,y=0,z=0){return mesh(parent,new RoundedBoxGeometry(w,h,d,3,Math.min(w,h,d)*.11),m,x,y,z)}
function cyl(parent,rt,rb,h,m,x=0,y=0,z=0,segments=32){return mesh(parent,new THREE.CylinderGeometry(rt,rb,h,segments),m,x,y,z)}
function ball(parent,r,m,x=0,y=0,z=0){return mesh(parent,new THREE.SphereGeometry(r,16,12),m,x,y,z)}
function rod(parent,a,b,r,m){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),mid=A.clone().add(B).multiplyScalar(.5);const o=cyl(parent,r,r,A.distanceTo(B),m,...mid.toArray(),12);o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.sub(A).normalize());return o}
const rover=new THREE.Group();const shell=new THREE.Group();rover.add(shell);
cyl(shell,1.48,1.48,.18,black,0,1.28,0,64);
cyl(shell,1.43,1.48,.58,white,0,1.62,0,64);
cyl(shell,1.42,1.42,.12,black,0,1.97,0,64);
cyl(shell,1.39,1.39,.055,steel,0,2.04,0,64);
for(const y of [1.34,1.93]){let trim=mesh(shell,new THREE.TorusGeometry(1.455,.035,10,64),black,0,y,0);trim.rotation.x=Math.PI/2}
let accent=mesh(shell,new THREE.TorusGeometry(1.465,.016,8,64),blue,0,1.42,0);accent.rotation.x=Math.PI/2;
// Segmented armored perimeter rather than a smooth toy-like disk.
const armor=mat(0xe3e5e5,.3,.4),recess=mat(0x07111a,.55,.45),titanium=mat(0x344958,.82,.3);
for(let i=0;i<16;i++){
  const a=i*Math.PI/8,rad=1.44;
  const panel=box(shell,.47,.34,.075,i%4===0?titanium:armor,Math.sin(a)*rad,1.68,Math.cos(a)*rad);
  panel.rotation.y=a;
  const seam=box(shell,.40,.025,.08,recess,Math.sin(a)*1.49,1.83,Math.cos(a)*1.49);seam.rotation.y=a;
  for(const d of [-.17,.17]){
    const bolt=cyl(shell,.018,.018,.014,black,Math.sin(a)*rad+d*Math.cos(a),1.72,Math.cos(a)*rad-d*Math.sin(a),8);
    bolt.rotation.x=Math.PI/2;
  }
}
for(let ring of [1.05,1.22]){
  let track=mesh(shell,new THREE.TorusGeometry(ring,.012,7,80),recess,0,2.084,0);track.rotation.x=Math.PI/2;
}
// Recessed access hatches, thermal grills and low-profile status modules.
for(let i=0;i<8;i++){
  const a=i*Math.PI/4;
  const x=Math.sin(a)*1.15,z=Math.cos(a)*1.15;
  const panel=box(shell,.32,.027,.16,i%2?black:titanium,x,2.087,z);panel.rotation.y=a;
  for(let j=-1;j<=1;j++){const slot=box(shell,.055,.03,.013,recess,x+j*.075*Math.cos(a),2.108,z-j*.075*Math.sin(a));slot.rotation.y=a}
}
// Front protruding head removed; circular chassis remains continuous.
// Side armor and decals as real canvas textures.
const label=document.createElement('canvas');label.width=768;label.height=192;
const ctx=label.getContext('2d');ctx.fillStyle='#14212d';ctx.fillRect(0,0,768,192);
ctx.fillStyle='#eaf3fa';ctx.font='bold 82px Arial';ctx.fillText('MetriX AI',34,107);
ctx.fillStyle='#68b6ff';ctx.fillRect(34,126,180,5);
ctx.fillStyle='#a8bdce';ctx.font='29px Arial';ctx.fillText('SMART SAMPLING ROVER',34,169);
const tex=new THREE.CanvasTexture(label);tex.colorSpace=THREE.SRGBColorSpace;
// A recessed plaque on two short mounts stays clear of the circular side armor.
box(shell,.09,.51,1.48,black,1.53,1.64,.02);
for(const z of [-.48,.48])rod(shell,[1.34,1.64,z],[1.54,1.64,z],.055,steel);
let sign=mesh(shell,new THREE.PlaneGeometry(1.43,.47),new THREE.MeshBasicMaterial({map:tex,side:THREE.DoubleSide}),1.58,1.64,.02);sign.rotation.y=Math.PI/2;
for(const side of [-1,1]){ball(shell,.12,black,side*1.34,1.59,0);ball(shell,.055,blue,side*1.46,1.6,0)}
// Six radial assemblies: three on each side, no center-front leg.
const wheels=[],pods=[],legs=[];
const legAngles=[30,90,150,210,270,330];
for(const degrees of legAngles){
  const a=THREE.MathUtils.degToRad(degrees),dx=Math.sin(a),dz=Math.cos(a);
  const leg=new THREE.Group();shell.add(leg);legs.push(leg);
  leg.rotation.y=a;leg.userData.direction=new THREE.Vector3(dx,0,dz);
  const root=[0,1.30,1.14],knee=[0,1.47,1.54],ankle=[0,1.26,1.86];
  rod(leg,root,knee,.16,white);rod(leg,knee,ankle,.14,white);
  rod(leg,[-.11,1.16,1.19],[-.11,1.31,1.54],.04,steel);
  rod(leg,[-.11,1.31,1.54],[-.11,1.10,1.86],.04,steel);
  for(const joint of [root,knee,ankle]){
    const hinge=cyl(leg,.13,.13,.36,black,...joint,24);hinge.rotation.z=Math.PI/2;
    for(const side of [-1,1]){let cap=cyl(leg,.065,.065,.02,steel,side*.19,joint[1],joint[2],12);cap.rotation.z=Math.PI/2}
  }
  const upper=box(leg,.31,.21,.40,white,0,1.39,1.34);upper.rotation.x=-.40;
  const lower=box(leg,.29,.20,.37,white,0,1.36,1.70);lower.rotation.x=.58;
  rod(leg,[-.17,1.38,1.30],[-.17,1.56,1.44],.016,steel);
  rod(leg,[-.17,1.56,1.44],[.17,1.56,1.44],.016,steel);
  rod(leg,[.17,1.56,1.44],[.17,1.38,1.30],.016,steel);
  const pod=new THREE.Group();pod.position.set(dx*1.84,1.3,dz*1.84);pod.rotation.y=a;shell.add(pod);pods.push(pod);
  box(pod,.49,.42,.48,white,0,-.20,.12);box(pod,.43,.09,.46,black,0,.01,.12);
  rod(pod,[0,-.29,.16],[0,-.81,.30],.085,black);
  for(const side of [-1,1]){
    box(pod,.055,.29,.40,white,side*.22,-.19,.12);
    ball(pod,.029,steel,side*.255,-.10,.22);
  }
  const w=new THREE.Group();w.position.set(0,-.85,.30);pod.add(w);
  const tyre=cyl(w,.41,.41,.31,dark);tyre.rotation.z=Math.PI/2;
  const hub=cyl(w,.18,.18,.34,steel);hub.rotation.z=Math.PI/2;
  const cap=cyl(w,.12,.12,.36,black);cap.rotation.z=Math.PI/2;
  wheels.push(w);
}
// Undercarriage skid and angled rock deflectors on the round hull.
cyl(shell,1.06,1.16,.075,black,0,1.16,0,48);
for(const sx of [-1,1])for(const sz of [-1,1]){
  const plate=box(shell,.29,.06,.43,titanium,sx*1.14,1.19,sz*.88);
  plate.rotation.y=sx*sz*.36;
}
// Sample carousel and removable-looking cylindrical sample canisters.
const tray=new THREE.Group();tray.position.set(-.64,2.1,.44);shell.add(tray);cyl(tray,.66,.66,.09,purple);cyl(tray,.61,.61,.12,black,0,.1,0);for(let i=0;i<8;i++){const a=i*Math.PI/4,x=Math.cos(a)*.43,z=Math.sin(a)*.43;cyl(tray,.105,.105,.28,steel,x,.26,z,12);cyl(tray,.108,.108,.04,white,x,.42,z,12)}cyl(tray,.17,.17,.1,white,0,.22,0);
// Lower protected sensor pod keeps the overhead profile compact.
const mast=new THREE.Group();mast.position.set(-.1,2.07,-.67);shell.add(mast);
cyl(mast,.20,.24,.13,black,0,.05,0);box(mast,.17,1.28,.17,titanium,0,.73,0);
for(const y of [.18,.79,1.17])box(mast,.23,.035,.23,steel,0,y,0);
cyl(mast,.31,.31,.17,black,0,1.48,0);cyl(mast,.30,.30,.035,steel,0,1.59,0);
cyl(mast,.31,.31,.025,blue,0,1.44,0);
box(mast,.62,.15,.23,black,0,1.40,.20);
for(const x of [-.21,.21]){let eye=cyl(mast,.065,.065,.035,glass,x,1.40,.34);eye.rotation.x=Math.PI/2}
// Robot arm with local pivot groups: yaw -> shoulder -> elbow -> wrist / scoop.
const yaw=new THREE.Group();yaw.position.set(0,2.07,1.22);shell.add(yaw);cyl(yaw,.39,.39,.16,black);cyl(yaw,.31,.31,.34,white,0,.2,0);const shoulder=new THREE.Group();shoulder.position.set(0,.37,0);yaw.add(shoulder);ball(shoulder,.22,black);rod(shoulder,[0,0,0],[.18,.61,0],.16,white);rod(shoulder,[.18,.61,0],[.34,.78,0],.15,black);const elbow=new THREE.Group();elbow.position.set(.34,.78,0);shoulder.add(elbow);ball(elbow,.19,black);rod(elbow,[0,0,0],[.14,-.64,0],.13,white);const wrist=new THREE.Group();wrist.position.set(.14,-.64,0);elbow.add(wrist);ball(wrist,.15,black);rod(wrist,[0,0,0],[.08,-.36,0],.11,white);const scoop=new THREE.Group();scoop.position.set(.08,-.42,0);wrist.add(scoop);box(scoop,.28,.15,.32,steel,.08,-.04,0);let lip=box(scoop,.29,.03,.35,steel,.2,-.13,0);lip.rotation.z=-.5;shoulder.rotation.z=-.95;elbow.rotation.z=1.25;wrist.rotation.z=.1;yaw.rotation.y=-Math.PI/2;

const bolts=mat(0x52606c,.8,.3),rubber=mat(0x202630,.1,.86);
// Circular perimeter service lights and upper fasteners.
for(let k=0;k<20;k++){const a=k*Math.PI/10;cyl(shell,.027,.027,.018,bolts,Math.cos(a)*1.32,2.08,Math.sin(a)*1.32,8);if(k%2===0)ball(shell,.033,blue,Math.cos(a)*1.47,1.68,Math.sin(a)*1.47)}
for(const wheel of wheels){
  for(let k=0;k<24;k++){
    const a=k*Math.PI/12;
    for(const side of [-1,1]){let lug=box(wheel,.15,.068,.12,black,side*.1,Math.sin(a)*.42,Math.cos(a)*.42);lug.rotation.x=-a;lug.rotation.z=side*.35}
  }
  for(const side of [-1,1]){
    const ring=mesh(wheel,new THREE.TorusGeometry(.29,.018,7,32),steel,side*.175,0,0);ring.rotation.y=Math.PI/2;
    for(let i=0;i<6;i++){const a=i*Math.PI/3;ball(wheel,.025,black,side*.19,Math.cos(a)*.15,Math.sin(a)*.15)}
  }
}
for(let i=0;i<8;i++){
  const a=i*Math.PI/4,x=Math.cos(a)*.43,z=Math.sin(a)*.43;
  cyl(tray,.115,.115,.23,new THREE.MeshPhysicalMaterial({color:0xdfe9f1,transparent:true,opacity:.54,roughness:.18,depthWrite:false}),x,.29,z,12);
  cyl(tray,.12,.12,.025,black,x,.43,z,12);
}
// LiDAR optical windows belong to the mast assembly and move with it in exploded view.
for(let k=0;k<12;k++){
  const a=k*Math.PI/6;
  const window=box(mast,.057,.065,.032,glass,Math.sin(a)*.303,1.48,Math.cos(a)*.303);
  window.rotation.y=a;
}
for(const x of [-.07,.07])rod(mast,[x,.09,-.04],[x,1.37,-.04],.018,steel);
for(const side of [-1,1]){
  rod(shoulder,[side*.06,.08,side*.11],[.18+side*.06,.61,side*.11],.039,black);
  rod(elbow,[side*.04,-.03,side*.1],[.14+side*.04,-.59,side*.1],.028,black);
  for(const joint of [shoulder,elbow,wrist]){let axle=cyl(joint,.09,.09,.028,steel,0,0,side*.18);axle.rotation.x=Math.PI/2}
}
mesh(shoulder,new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(0,.08,.18),new THREE.Vector3(.1,.47,.23),new THREE.Vector3(.34,.78,.18)]),20,.026,7,false),rubber);
mesh(elbow,new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(0,0,.18),new THREE.Vector3(.03,-.34,.22),new THREE.Vector3(.14,-.64,.17)]),20,.022,7,false),rubber);
for(let k=0;k<4;k++)box(scoop,.05,.07,.06,steel,.25,-.16,-.12+k*.08).rotation.z=-.35;
cyl(shell,.23,.23,.035,black,.12,2.1,.84,32);
// Optical payload and industrial warning details.
for(const sx of [-1,1]){
  const optic=box(shell,.22,.16,.16,titanium,sx*1.0,2.15,.82);
  const lens=cyl(shell,.06,.06,.035,glass,sx*1.0,2.16,.915);lens.rotation.x=Math.PI/2;
  const iris=cyl(shell,.03,.03,.039,blue,sx*1.0,2.16,.94);iris.rotation.x=Math.PI/2;
}
rod(shell,[-1.18,2.02,-.28],[-1.18,2.72,-.28],.022,black);
for(let y of [2.12,2.25,2.38])cyl(shell,.048,.048,.025,steel,-1.18,y,-.28);
ball(shell,.04,blue,-1.18,2.74,-.28);
for(const sx of [-1,1]){
  for(let j=0;j<3;j++)box(shell,.13,.018,.28,recess,sx*.82,2.088,-.98+j*.12);
}
// Status lights and emergency stop.
cyl(shell,.16,.16,.11,black,.24,2.07,-.75);cyl(shell,.13,.13,.13,red,.24,2.16,-.75);for(const x of [-1.37,1.37])box(shell,.12,.045,.26,blue,x,1.93,.7);

// Merge within each assembly, retaining wheel and mast pivots for scene animation.
function mergeAssembly(source){
 source.updateMatrixWorld(true);
 const inverse=source.matrixWorld.clone().invert(),groups=new Map(),result=new THREE.Group();
 source.traverse(node=>{if(!node.isMesh)return;const key=node.material.uuid;if(!groups.has(key))groups.set(key,{material:node.material,geometries:[]});let g=node.geometry.clone();if(g.index)g=g.toNonIndexed();g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse,node.matrixWorld));for(const name of Object.keys(g.attributes))if(!['position','normal','uv'].includes(name))g.deleteAttribute(name);groups.get(key).geometries.push(g)});
 for(const {material,geometries} of groups.values()){const part=new THREE.Mesh(mergeGeometries(geometries),material);part.castShadow=true;part.receiveShadow=true;result.add(part);geometries.forEach(g=>g.dispose())}
 source.traverse(node=>{if(node.isMesh)node.geometry.dispose()});return result;
}
rover.updateMatrixWorld(true);
const animated=[...wheels,mast].map(source=>{
 const world=source.matrixWorld.clone(),part=mergeAssembly(source);
 world.decompose(part.position,part.quaternion,part.scale);source.removeFromParent();
 part.userData.restQuaternion=part.quaternion.clone();return part;
});
const merged=mergeAssembly(rover);
animated.forEach(part=>merged.add(part));
merged.userData.wheels=animated.slice(0,6);merged.userData.mast=animated[6];
return merged;
}
