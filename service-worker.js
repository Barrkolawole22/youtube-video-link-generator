// This is the service worker file referenced in your index.html

const CACHE_NAME = 'igfbsaver-v1';
// Add all the files you want to cache for offline use
const URLS_TO_CACHE = [
  '/',
  '/index.html',
  '/facebook-video-downloader.html',
  '/instagram-video-downloader.html',
  '/twitter-video-downloader.html',
  '/threads-video-downloader.html',
  '/terms-of-service.html',
  '/privacy.html',
  '/static/logo.png/',
  '/static/og-image.jpg',
  '/static/tutorial-image.jpg',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
  // NOTE: Your /static/script.js and menu.js are not in your index.html
  // If you have them on other pages, add them here.
];

// Install event: This is when the browser "installs" the PWA
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching app shell');
        return cache.addAll(URLS_TO_CACHE);
      })
      .then(() => {
        self.skipWaiting();
      })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch event: Serve files from cache if available
self.addEventListener('fetch', event => {
  // We only want to cache GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // If we find a match in the cache, return it
        if (response) {
          console.log('Service Worker: Serving from cache', event.request.url);
          return response;
        }

        // Otherwise, fetch from the network
        console.log('Service Worker: Fetching from network', event.request.url);
        return fetch(event.request);
      })
  );
});