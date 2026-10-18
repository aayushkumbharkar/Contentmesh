import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {Graph,Node,colors} from './types';

export function GraphView({graph,selected,onSelect}:{graph:Graph;selected:string;onSelect:(n:Node)=>void}) {
 const host=useRef<HTMLDivElement>(null); const callback=useRef(onSelect);callback.current=onSelect;
 const [failure,setFailure]=useState('');
 useEffect(()=>{
  if(!host.current)return;
  let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});}catch{setFailure('3D rendering is unavailable. Use the accessible list view.');return;}
  const container=host.current;renderer.setPixelRatio(Math.min(devicePixelRatio,2));container.appendChild(renderer.domElement);
  renderer.domElement.setAttribute('aria-label','Interactive graph. Drag to orbit, scroll to zoom. Use list view for keyboard navigation.');
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(48,1,.1,1000);camera.position.set(0,12,42);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=8;controls.maxDistance=110;
  const positions=new Map<string,THREE.Vector3>();const meshes:THREE.Mesh[]=[];
  const kinds=[...new Set(graph.nodes.map(n=>n.kind))];
  graph.nodes.forEach((node,i)=>{
   const group=kinds.indexOf(node.kind),angle=i*2.39996,radius=4+Math.sqrt(i)*1.7;
   const pos=new THREE.Vector3(Math.cos(angle)*radius,(group%4-1.5)*3+Math.sin(i)*2,Math.sin(angle)*radius*.7);positions.set(node.id,pos);
   const mesh=new THREE.Mesh(new THREE.SphereGeometry(node.id===selected?.42:.25,16,12),new THREE.MeshBasicMaterial({color:colors[node.kind]||'#ffffff'}));mesh.position.copy(pos);mesh.userData.node=node;scene.add(mesh);meshes.push(mesh);
   const canvas=document.createElement('canvas');canvas.width=512;canvas.height=64;const ctx=canvas.getContext('2d');
   if(ctx){ctx.font='23px system-ui';ctx.fillStyle=node.id===selected?'#ffffff':'#afbfce';ctx.fillText(node.label.slice(0,35),8,36);const texture=new THREE.CanvasTexture(canvas);const label=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false}));label.position.copy(pos).add(new THREE.Vector3(2.3,.7,0));label.scale.set(6.5,.8125,1);scene.add(label);}
  });
  graph.edges.forEach(edge=>{const a=positions.get(edge.source),b=positions.get(edge.target);if(!a||!b)return;const active=edge.source===selected||edge.target===selected;scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([a,b]),new THREE.LineBasicMaterial({color:active?'#77e8df':'#354959',transparent:true,opacity:active?.85:.42})));});
  const grid=new THREE.GridHelper(100,40,0x213140,0x15212d);grid.position.y=-9;scene.add(grid);
  const resize=()=>{const {width,height}=container.getBoundingClientRect();renderer.setSize(width,height);camera.aspect=width/Math.max(height,1);camera.updateProjectionMatrix();};const observer=new ResizeObserver(resize);observer.observe(container);resize();
  const ray=new THREE.Raycaster();let down=[0,0];const pointerdown=(e:PointerEvent)=>{down=[e.clientX,e.clientY];};const click=(e:MouseEvent)=>{if(Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect();ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hit=ray.intersectObjects(meshes)[0];if(hit)callback.current(hit.object.userData.node as Node);};renderer.domElement.addEventListener('pointerdown',pointerdown);renderer.domElement.addEventListener('click',click);
  let frame=0;const animate=()=>{frame=requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);};animate();
  return()=>{cancelAnimationFrame(frame);observer.disconnect();controls.dispose();scene.traverse(obj=>{if(obj instanceof THREE.Mesh||obj instanceof THREE.Line||obj instanceof THREE.Sprite){obj.geometry?.dispose();const materials=Array.isArray(obj.material)?obj.material:[obj.material];materials.forEach(m=>{if('map' in m)(m.map as THREE.Texture)?.dispose();m.dispose();});}});renderer.dispose();renderer.domElement.remove();};
 },[graph,selected]);
 return <div className="graph-canvas" ref={host}>{failure&&<p className="canvas-message">{failure}</p>}</div>;
}
