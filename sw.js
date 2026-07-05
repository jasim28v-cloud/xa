// 🃏 جوكر - Service Worker محسن للتطبيق
const CACHE_NAME = 'joker-cache-v1.0.0';

// قائمة الملفات للتخزين
const urlsToCache = [
  '/',
  '/index.html',
  '/js/sw-register.js'
];

// تثبيت Service Worker
self.addEventListener('install', function(event) {
  console.log('🃏 [جوكر] جاري تثبيت Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('📦 [جوكر] جاري تخزين الملفات الأساسية...');
        return cache.addAll(urlsToCache);
      })
      .then(function() {
        console.log('✅ [جوكر] تم تخزين جميع الملفات');
        return self.skipWaiting();
      })
      .catch(function(error) {
        console.log('❌ [جوكر] خطأ في التخزين:', error);
      })
  );
});

// تفعيل Service Worker
self.addEventListener('activate', function(event) {
  console.log('🔄 [جوكر] جاري تفعيل Service Worker...');
  
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ [جوكر] حذف الكاش القديم:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
    .then(function() {
      console.log('✅ [جوكر] Service Worker مفعل!');
      return self.clients.claim();
    })
  );
});

// استراتيجية: Network First ثم Cache
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    fetch(event.request)
      .then(function(networkResponse) {
        // تخزين النسخة في الكاش
        if (networkResponse && networkResponse.status === 200) {
          var responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            console.log('💾 [جوكر] تخزين:', event.request.url);
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(function() {
        // إذا فشل الاتصال - استخدم الكاش
        return caches.match(event.request)
          .then(function(cachedResponse) {
            if (cachedResponse) {
              console.log('📦 [جوكر] من الكاش:', event.request.url);
              return cachedResponse;
            }
            
            // إذا كان الملف غير موجود - عرض الصفحة الرئيسية
            if (event.request.mode === 'navigate') {
              return caches.match('/index.html');
            }
          });
      })
  );
});

// استقبال الرسائل
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'CACHE_ALL') {
    console.log('📦 [جوكر] جاري تخزين جميع الملفات...');
    
    caches.open(CACHE_NAME).then(function(cache) {
      event.data.files.forEach(function(file) {
        fetch(file)
          .then(function(response) {
            if (response.ok) {
              cache.put(file, response);
              console.log('💾 [جوكر] تم تخزين:', file);
            }
          })
          .catch(function(error) {
            console.log('⚠️ [جوكر] فشل تخزين:', file, error);
          });
      });
    });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME).then(function() {
      console.log('🗑️ [جوكر] تم مسح الكاش');
    });
  }
});

console.log('🃏 [جوكر] Service Worker جاهز! 🎭');

