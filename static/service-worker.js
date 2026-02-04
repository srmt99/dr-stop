// Ensure we're running in a secure context
if (location.protocol !== 'https:') {
  throw new Error('Service workers require HTTPS');
}

const CACHE_NAME = 'dr-stop-radio-v1';
const ASSETS = [
  '/images/dr_avatar.jpg',
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
  // Handle audio requests separately
  if (event.request.url.includes('/dr_stop_radio_stream')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone the response to use it and cache it
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => cache.put(event.request, responseToCache));
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
  } else {
    event.respondWith(
      caches.match(event.request)
        .then((response) => response || fetch(event.request))
    );
  }
});

// Background sync for audio playback
self.addEventListener('sync', (event) => {
  if (event.tag === 'audio-sync') {
    event.waitUntil(
      fetch('/dr_stop_radio_stream')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response;
        })
        .catch(error => {
          console.error('Background sync failed:', error);
        })
    );
  }
});

// Periodic sync for background updates
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'audio-update') {
    event.waitUntil(
      fetch('/dr_stop_radio_stream')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response;
        })
        .catch(error => {
          console.error('Periodic sync failed:', error);
        })
    );
  }
});
