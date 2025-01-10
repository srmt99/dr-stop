const CACHE_NAME = 'dr-stop-radio-v1';
const ASSETS = [
  '/dr_avatar',
  '/dr_stop_radio_stream',
  '/images/dr_avatar_closed.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
