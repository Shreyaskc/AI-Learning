// Service worker: caches the app shell + images so it works offline once installed.
// Bump CACHE_VERSION whenever shipping a change, so clients pick up fresh files.
const CACHE_VERSION = "v2";
const CACHE_NAME = "ai-fluency-" + CACHE_VERSION;

const ASSETS = [
  "./",
  "index.html",
  "style.css",
  "content.js",
  "demos.js",
  "app.js",
  "manifest.webmanifest",
  "icons/apple-touch-icon.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/favicon-32.png",
  "images/attention-calculation-steps.png",
  "images/attention-heads-it.png",
  "images/chinchilla-scaling-heatmap.png",
  "images/mcp-usbc-diagram.png",
  "images/mxn-problem-keys.png",
  "images/positional-encoding-heatmap.png",
  "images/qkv-vectors.png",
  "images/quantization-fp32-int8.png",
  "images/rag-pipeline.jpg",
  "images/react-loop.png",
  "images/rlhf-pipeline.png",
  "images/transformer-architecture.png",
  "images/word2vec-gensim-result.png",
  "images/word2vec-vector-heatmap.png",
  "icons/splash-1125x2436.png",
  "icons/splash-1170x2532.png",
  "icons/splash-1179x2556.png",
  "icons/splash-1206x2622.png",
  "icons/splash-1290x2796.png",
  "icons/splash-1320x2868.png",
  "icons/splash-750x1334.png",
  "icons/splash-1242x2208.png",
  "icons/splash-828x1792.png",
  "icons/splash-1242x2688.png",
  "icons/splash-1284x2778.png",
  "icons/splash-1668x2388.png",
  "icons/splash-2048x2732.png",
  "icons/splash-1620x2160.png",
  "icons/splash-1640x2360.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for same-origin requests (so you always get fresh content when
// online), falling back to the cache when offline. Cache gets updated with
// whatever the network returns, keeping the offline copy current.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== location.origin) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request).then((cached) => cached || caches.match("index.html")))
  );
});
