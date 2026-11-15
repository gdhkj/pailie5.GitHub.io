const CACHE='p5-v5-shell-2';
const LLM_URL='https://esm.run/@mlc-ai/web-llm@0.2.84';
const SHELL=['./','./index.html','./manifest.webmanifest','./data/draws.json'];
self.addEventListener('install',event=>event.waitUntil((async()=>{const c=await caches.open(CACHE);await c.addAll(SHELL);try{await c.add(LLM_URL)}catch(e){}await self.skipWaiting()})()));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{const u=new URL(event.request.url);if(event.request.method!=='GET')return;if(event.request.url===LLM_URL){event.respondWith(caches.match(LLM_URL).then(cached=>cached||fetch(event.request).then(response=>{if(response.ok)caches.open(CACHE).then(c=>c.put(LLM_URL,response.clone()));return response})));return}if(u.origin!==location.origin)return;event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(c=>c.put(event.request,copy))}return response}).catch(()=>caches.match('./index.html'))))});
