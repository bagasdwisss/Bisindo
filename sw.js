// BISINDO Translator Service Worker
const CACHE_NAME = 'bisindo-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/js/app.js',
  '/manifest.json',
  '/models/web/labels_abjad.json',
  '/models/web/labels_kosakata.json',
  '/models/web/abjad/model.json',
  '/models/web/kosakata/model.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching core assets');
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('[SW] Core assets pre-cache partial notice:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[SW] Removing old cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Stale-while-revalidate / Network-first strategy for dynamic model files
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (
          !networkResponse ||
          networkResponse.status !== 200 ||
          networkResponse.type !== 'basic'
        ) {
          return networkResponse;
        }
        // Cache weight files, assets, and scripts
        if (
          event.request.url.includes('/models/') ||
          event.request.url.includes('/js/') ||
          event.request.url.includes('/assets/')
        ) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        return caches.match('/index.html');
      });
    })
  );
});
