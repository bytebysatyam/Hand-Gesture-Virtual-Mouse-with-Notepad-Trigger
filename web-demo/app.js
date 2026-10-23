const video = document.getElementById("inputVideo");
const canvas = document.getElementById("outputCanvas");
const ctx = canvas.getContext("2d");
const sandbox = document.getElementById("sandbox");
const cursor = document.getElementById("virtualCursor");
const statusText = document.getElementById("statusText");
const actionText = document.getElementById("actionText");
const fpsText = document.getElementById("fpsText");
const clickResult = document.getElementById("clickResult");
const scrollPanel = document.getElementById("scrollPanel");
const contextMenu = document.getElementById("contextMenu");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

let camera = null;
let running = false;
let cursorX = 0.5;
let cursorY = 0.5;
let lastClick = 0;
let lastScroll = 0;
let lastFrame = performance.now();
let fps = 0;
const CLICK_DELAY = 700;
const SCROLL_DELAY = 180;

const dist = (a,b) => Math.hypot(a.x-b.x,a.y-b.y);
const isExtended = (tip,pip,margin=0.015) => tip.y < pip.y - margin;
const isPinching = (a,b,palm,ratio=0.28) => palm > 0 && dist(a,b) <= palm*ratio;

function classify(lm){
  const thumb=lm[4], indexTip=lm[8], indexPip=lm[6], middleTip=lm[12], middlePip=lm[10], wrist=lm[0], middleMcp=lm[9];
  const palm=Math.max(dist(wrist,middleMcp),1e-6);
  const indexExtended=isExtended(indexTip,indexPip);
  const middleExtended=isExtended(middleTip,middlePip);

  if(isPinching(thumb,indexTip,palm)) return "left_click";
  if(isPinching(thumb,middleTip,palm)) return "right_click";
  if(indexExtended && !middleExtended) return "move";

  if(indexExtended && middleExtended){
    const gap=(middleTip.y-indexTip.y)/palm;
    if(gap>0.45) return "scroll_up";
    if(gap<-0.45) return "scroll_down";
  }
  return "none";
}

function updateCursor(lm){
  const targetX = Math.min(1,Math.max(0,1-lm[8].x));
  const targetY = Math.min(1,Math.max(0,lm[8].y));
  cursorX += (targetX-cursorX)/4.5;
  cursorY += (targetY-cursorY)/4.5;
  const rect=sandbox.getBoundingClientRect();
  cursor.style.left=`${cursorX*rect.width}px`;
  cursor.style.top=`${cursorY*rect.height}px`;
}

function cursorClientPoint(){
  const r=sandbox.getBoundingClientRect();
  return {x:r.left+cursorX*r.width,y:r.top+cursorY*r.height};
}

function simulateLeftClick(){
  const now=performance.now();
  if(now-lastClick<CLICK_DELAY) return;
  lastClick=now;
  cursor.classList.add("clicking");
  setTimeout(()=>cursor.classList.remove("clicking"),120);
  const p=cursorClientPoint();
  const el=document.elementFromPoint(p.x,p.y);
  if(el && sandbox.contains(el)){
    const target=el.closest("[data-demo-action]");
    if(target){
      clickResult.textContent=target.dataset.demoAction;
      target.animate([{transform:"scale(1)"},{transform:"scale(.96)"},{transform:"scale(1)"}],{duration:180});
    } else {
      clickResult.textContent="Left-click detected inside the playground.";
    }
  }
}

function simulateRightClick(){
  const now=performance.now();
  if(now-lastClick<CLICK_DELAY) return;
  lastClick=now;
  const p=cursorClientPoint();
  const s=sandbox.getBoundingClientRect();
  contextMenu.hidden=false;
  contextMenu.style.left=`${Math.min(p.x-s.left,s.width-280)}px`;
  contextMenu.style.top=`${Math.min(p.y-s.top,s.height-100)}px`;
  setTimeout(()=>contextMenu.hidden=true,1800);
}

function simulateScroll(direction){
  const now=performance.now();
  if(now-lastScroll<SCROLL_DELAY) return;
  lastScroll=now;
  scrollPanel.scrollBy({top:direction*55,behavior:"smooth"});
}

function onResults(results){
  canvas.width=video.videoWidth || 640;
  canvas.height=video.videoHeight || 480;
  ctx.save();
  ctx.clearRect(0,0,canvas.width,canvas.height);
  ctx.drawImage(results.image,0,0,canvas.width,canvas.height);

  let action="none";
  if(results.multiHandLandmarks?.length){
    const lm=results.multiHandLandmarks[0];
    drawConnectors(ctx,lm,HAND_CONNECTIONS,{color:"#74c0ff",lineWidth:4});
    drawLandmarks(ctx,lm,{color:"#b9ffda",lineWidth:2,radius:3});
    action=classify(lm);
    updateCursor(lm);

    if(action==="left_click") simulateLeftClick();
    else if(action==="right_click") simulateRightClick();
    else if(action==="scroll_up") simulateScroll(-1);
    else if(action==="scroll_down") simulateScroll(1);
  }

  actionText.textContent=action;
  const now=performance.now();
  const instant=1000/Math.max(1,now-lastFrame);
  fps=fps?fps*0.85+instant*0.15:instant;
  fpsText.textContent=Math.round(fps);
  lastFrame=now;
  ctx.restore();
}

const hands = new Hands({
  locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1675469240/${file}`
});
hands.setOptions({
  maxNumHands:1,
  modelComplexity:1,
  minDetectionConfidence:0.7,
  minTrackingConfidence:0.7
});
hands.onResults(onResults);

async function start(){
  if(running) return;
  statusText.textContent="Requesting camera…";
  try{
    camera=new Camera(video,{
      onFrame:async()=>{if(running) await hands.send({image:video});},
      width:640,
      height:480
    });
    running=true;
    await camera.start();
    statusText.textContent="Live";
    startBtn.disabled=true;
    stopBtn.disabled=false;
  }catch(err){
    running=false;
    statusText.textContent="Camera error";
    clickResult.textContent="Could not access webcam. Allow camera permission and reload.";
    console.error(err);
  }
}

async function stop(){
  running=false;
  if(camera){
    try{camera.stop();}catch(_){}
    camera=null;
  }
  const stream=video.srcObject;
  if(stream) stream.getTracks().forEach(t=>t.stop());
  video.srcObject=null;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  statusText.textContent="Stopped";
  actionText.textContent="none";
  fpsText.textContent="0";
  startBtn.disabled=false;
  stopBtn.disabled=true;
}

startBtn.addEventListener("click",start);
stopBtn.addEventListener("click",stop);
document.querySelectorAll("[data-demo-action]").forEach(el=>{
  el.addEventListener("click",()=>clickResult.textContent=el.dataset.demoAction);
});
