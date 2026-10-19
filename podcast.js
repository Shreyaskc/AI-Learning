/* One media element, explicit playback intent, and local-only resumable state. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else { const api = factory(); api.mount(document, window); }
}(this, function () {
  const KEY = 'ai-fluency-audio-v1';
  function createController({audio, tracks, storage, onChange=()=>{}, clock=()=>Date.now(), mediaSession, Metadata}) {
    const byId = new Map(tracks.map(t=>[t.id,t]));
    const sources = new Map();
    const aliases=new Map(tracks.flatMap(t=>(t.aliases||[]).map(alias=>[alias,t.id])));
    const chapterOf=id=>byId.get(id)?.chapter||id;
    const lastByChapter={};
    let saved, storageOK=!!storage;
    let raw;
    try { raw=storage?.getItem(KEY); } catch (_) {storageOK=false;}
    try {saved=JSON.parse(raw||'null');}catch(_){saved=null;}
    const positions={};
    if (saved?.version===1 && saved.positions && typeof saved.positions==='object') {
      for (const [id,value] of Object.entries(saved.positions)) if (byId.has(id) && Number.isFinite(value) && value>=0 && value<1e7 && (!byId.get(id).revision || saved.revisions?.[id]===byId.get(id).revision)) positions[id]=value;
    }
    let current=saved?.version===1 && byId.has(saved?.current) ? saved.current : (tracks.find(t=>t.transcript)||tracks[0])?.id;
    if(saved?.version===1 && aliases.has(saved?.current))current=aliases.get(saved.current);
    if(saved?.version===1 && saved.lastByChapter && typeof saved.lastByChapter==='object'){for(const [chapter,id] of Object.entries(saved.lastByChapter))if(byId.has(id)&&chapterOf(id)===chapter)lastByChapter[chapter]=id;}
    lastByChapter[chapterOf(current)]=current;
    let speed=saved?.version===1 && Number.isFinite(saved.speed) && saved.speed>=0.5 && saved.speed<=3 ? saved.speed : 1;
    let continuous=saved?.version===1 && saved.continuous===true;
    let armed=false, message='', generation=0, loaded=null, pendingSeek=null, lastWrite=-Infinity;
    const source=()=>sources.get(current)||byId.get(current)?.src;
    const snapshot=()=>({current, track:byId.get(current), speed, continuous, armed, message, storageOK, position:positions[current]||0, available:!!source(),index:tracks.findIndex(t=>t.id===current),total:tracks.length});
    function notify(){onChange(snapshot());}
    function persist(force=false){
      if (!force && clock()-lastWrite<5000) return;
      lastWrite=clock();
      try { storage?.setItem(KEY,JSON.stringify({version:1,current,speed,continuous,positions,lastByChapter,revisions:Object.fromEntries(Object.keys(positions).map(id=>[id,byId.get(id)?.revision||null]))})); } catch (_) {storageOK=false;}
    }
    function capture(force=false){
      if (loaded===current && Number.isFinite(audio.currentTime) && audio.currentTime>=0) positions[current]=audio.currentTime;
      persist(force);
    }
    function metadata(){
      if (!mediaSession) return;
      try {
        if (Metadata) mediaSession.metadata=new Metadata({title:byId.get(current).title+' · '+byId.get(current).section,artist:'AI Fluency'});
        mediaSession.playbackState=audio.paused?'paused':'playing';
        if (loaded===current && Number.isFinite(audio.duration) && audio.duration>0 && mediaSession.setPositionState) mediaSession.setPositionState({duration:audio.duration,playbackRate:speed,position:Math.min(audio.currentTime||0,audio.duration)});
      } catch (_) { /* Optional browser capability, never required for playback. */ }
    }
    function seekPending(){
      if (pendingSeek===null || loaded!==current || !Number.isFinite(audio.duration) || audio.duration<=0) return;
      audio.currentTime=Math.min(Math.max(pendingSeek,0),Math.max(0,audio.duration-0.01));
      positions[current]=audio.currentTime;pendingSeek=null;metadata();
    }
    function load(){
      if (!source()) return false;
      if (loaded!==current) {
        audio.pause();loaded=current;audio.src=source();pendingSeek=positions[current]||0;audio.load();
      }
      audio.playbackRate=speed;metadata();return true;
    }
    function pause(){generation++;armed=false;audio.pause();capture(true);message='Paused. Press Resume to continue.';metadata();notify();}
    function select(id){
      id=aliases.get(id)||id;
      if (!byId.has(id)) return false;
      pause();audio.removeAttribute('src');audio.load();current=id;lastByChapter[chapterOf(id)]=id;loaded=null;pendingSeek=null;
      message=source()?'Ready. Press Play or Resume.':byId.get(id).status+'. Choose a local recording to preview.';
      persist(true);metadata();notify();return true;
    }
    function selectChapter(chapter){const id=lastByChapter[chapter]||tracks.find(t=>(t.chapter||t.id)===chapter)?.id;return id ? select(id) : false;}
    async function play(){
      if (!source()) {armed=false;message='No recording for this section yet. Choose a local recording to preview.';notify();return false;}
      // Source preparation may pause old media; establish new intent afterward.
      load();const request=++generation;armed=true;message='Starting playback…';notify();
      try {
        await audio.play();
        if (request!==generation) return false;
        message='Playing';metadata();notify();return true;
      } catch (_) {
        if (request===generation) {armed=false;message='Playback was blocked or interrupted. Tap Play or Resume to continue.';metadata();notify();}
        return false;
      }
    }
    function stop(){pause();positions[current]=0;pendingSeek=0;if(loaded===current)audio.currentTime=0;message='Stopped. Position reset; continuous run cancelled.';persist(true);notify();}
    function previous(){const i=tracks.findIndex(t=>t.id===current);return i>0 ? select(tracks[i-1].id) : false;}
    function next(){const i=tracks.findIndex(t=>t.id===current);if(i+1<tracks.length)return select(tracks[i+1].id);pause();message='You reached the final chapter.';notify();return false;}
    function setSpeed(value){if(!Number.isFinite(value)||value<0.5||value>3)return;speed=value;audio.playbackRate=speed;persist(true);metadata();notify();}
    function setContinuous(value){continuous=value===true;persist(true);notify();}
    function setLocalSource(id,url){if(!byId.has(id))return;pause();sources.set(id,url);if(current===id){audio.removeAttribute('src');audio.load();loaded=null;}message='Local recording ready. Press Play or Resume.';notify();}
    audio.addEventListener('loadedmetadata',seekPending);
    audio.addEventListener('durationchange',seekPending);
    audio.addEventListener('timeupdate',()=>{capture();metadata();notify();});
    audio.addEventListener('seeked',()=>{capture(true);metadata();notify();});
    audio.addEventListener('ratechange',()=>{if(!Number.isFinite(audio.playbackRate))return;const bounded=Math.max(0.5,Math.min(3,audio.playbackRate));if(audio.playbackRate!==bounded)audio.playbackRate=bounded;speed=bounded;persist(true);metadata();notify();});
    audio.addEventListener('play',()=>{if(audio.paused||loaded!==current)return;armed=true;message='Playing';metadata();notify();});
    audio.addEventListener('pause',()=>{if(audio.paused && !audio.ended){generation++;armed=false;capture(true);message='Paused. Press Resume to continue.';metadata();notify();}});
    audio.addEventListener('waiting',()=>{if(loaded!==current||!armed)return;message='Buffering…';notify();});
    audio.addEventListener('error',()=>{if(loaded!==current)return;generation++;armed=false;audio.pause();message='Recording unavailable or could not be decoded. Choose another recording or retry.';capture(true);notify();});
    audio.addEventListener('ended',()=>{
      if(loaded!==current||!audio.ended)return;
      const proceed=armed && continuous;
      positions[current]=0;persist(true);armed=false;
      const i=tracks.findIndex(t=>t.id===current);
      if(!proceed){message='Section complete. Press Next to choose another section.';notify();return;}
      if(i+1>=tracks.length){message='You reached the final chapter.';notify();return;}
      select(tracks[i+1].id);
      if(!source()){message='Next section has no recording yet. Continuous playback stopped here.';notify();return;}
      play();
    });
    if(mediaSession?.setActionHandler){
      for(const [action,handler] of Object.entries({play, pause, stop, nexttrack:next, previoustrack:previous, seekto:e=>{if(Number.isFinite(e.seekTime)&&Number.isFinite(audio.duration)){audio.currentTime=Math.max(0,Math.min(e.seekTime,audio.duration));capture(true);}}})){
        try{mediaSession.setActionHandler(action,handler);}catch(_){}
      }
    }
    message='Choose Play or Resume. No audio starts automatically.';notify();
    return {play,pause,stop,next,previous,select,selectChapter,setSpeed,setContinuous,setLocalSource,snapshot,flush:()=>capture(true)};
  }
  function mount(doc,win){
    const data=doc.getElementById('audio-data');if(!data)return null;
    let tracks;try{tracks=JSON.parse(data.textContent);}catch(_){return null;}
    if(!Array.isArray(tracks)||!tracks.length)return null;
    const get=id=>doc.getElementById('audio-'+id);let storage;
    try{storage=win.localStorage;}catch(_){}
    const audio=doc.getElementById('course-audio');const localURLs=new Map();
    const setText=(element,value)=>{if(element.textContent!==value)element.textContent=value;};
    let mounted=false;
    const initialQuery=new URLSearchParams(win.location?.search||'');
    const updateURL=id=>{if(!mounted||!win.location?.href||!win.history?.replaceState)return;try{const url=new URL(win.location.href);url.searchParams.delete('chapter');url.searchParams.set('track',id);if(url.href!==win.location.href)win.history.replaceState(null,'',url.pathname+url.search+url.hash);}catch(_){}};
    const controller=createController({audio,tracks,storage,mediaSession:win.navigator?.mediaSession,Metadata:win.MediaMetadata,onChange:s=>{
      get('track').value=s.current;if(get('chapter'))get('chapter').value=s.track.chapter||s.track.id;setText(get('title'),s.track.title+' · '+s.track.section);updateURL(s.current);
      setText(get('status'),s.message);
      setText(get('storage'),s.storageOK?'Resume state is saved in this browser only.':'Browser storage unavailable: resume works in this tab only.');
      get('position').textContent='Section '+(s.index+1)+' of '+s.total+' · Position: '+Math.floor(s.position/60)+':'+String(Math.floor(s.position%60)).padStart(2,'0');
      const custom=get('custom-speed');if(custom){custom.hidden=[0.5,0.75,1,1.25,1.5,1.75,2,2.5,3].includes(s.speed);custom.value=String(s.speed);setText(custom,String(s.speed)+'×');}get('speed').value=String(s.speed);get('continue').checked=s.continuous;
      get('play').disabled=!s.available;get('resume').disabled=!s.available;
      get('resume').textContent='Resume at '+Math.floor(s.position/60)+':'+String(Math.floor(s.position%60)).padStart(2,'0');
      get('lesson').href=s.track.lesson;
      const url=localURLs.get(s.current)||s.track.src;get('download').hidden=!url;if(url)get('download').href=url;
      setText(get('transcript'),s.track.transcript||'A matching narration transcript has not been authored for this section yet.');
    }});
    for(const name of ['play','resume','pause','stop','next'])get(name).addEventListener('click',()=>controller[name==='resume'?'play':name]());
    if(get('previous'))get('previous').addEventListener('click',()=>controller.previous());
    if(get('chapter'))get('chapter').addEventListener('change',()=>controller.selectChapter(get('chapter').value));
    get('track').addEventListener('change',()=>controller.select(get('track').value));
    get('speed').addEventListener('change',()=>controller.setSpeed(Number(get('speed').value)));
    get('continue').addEventListener('change',()=>controller.setContinuous(get('continue').checked));
    get('file').addEventListener('change',()=>{const file=get('file').files?.[0];if(!file)return;const id=controller.snapshot().current;const old=localURLs.get(id);const url=win.URL.createObjectURL(file);localURLs.set(id,url);controller.setLocalSource(id,url);if(old)win.URL.revokeObjectURL(old);get('file').value='';});
    win.addEventListener('pagehide',()=>{controller.flush();controller.pause();});
    win.addEventListener('pageshow',()=>controller.pause());
    doc.addEventListener('visibilitychange',()=>{if(doc.visibilityState==='hidden')controller.flush();});
    try {const requested=initialQuery.get('track'),chapter=initialQuery.get('chapter');if(requested)controller.select(requested);else if(chapter)controller.selectChapter(chapter);}catch(_){}
    mounted=true;updateURL(controller.snapshot().current);
    win.addEventListener('popstate',()=>{try{const id=new URLSearchParams(win.location?.search||'').get('track');if(id)controller.select(id);else controller.pause();}catch(_){controller.pause();}});
    doc.getElementById('listen-interactive').hidden=false;
    return controller;
  }
  return {KEY,createController,mount};
}));
