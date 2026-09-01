/* 考研刷题 PWA 离线缓存 Service Worker
 * - 构建指纹：每次 `flutter build web` 后由 tools/post_build_sw.py 将 __BUILD_ID__
 *   替换为 main.dart.js 的 SHA-256 前缀，缓存据此版本化，发布新版本自动重建缓存。
 * - 策略：App Shell 预缓存（install）+ 静态资源缓存优先 + 页面导航网络优先。
 * - 仅处理同源 GET；跨域（如 fonts.gstatic.com 字体分片）走网络，不缓存。
 */
'use strict';

const BUILD_ID = '__BUILD_ID__';
const SHELL_CACHE = 'quiz-shell-' + BUILD_ID;
const RUNTIME_CACHE = 'quiz-runtime-' + BUILD_ID;

/* App Shell 预缓存清单：离线打开 App 的核心资源。
 * - 含 Flutter 引擎、主程序、数据库引擎（sqlite3.wasm + sqflite_sw.js）、
 *   中文字体（web woff2）、canvaskit 实际使用的 chromium 变体、图标、manifest。
 * - 题库 zip / 其他 canvaskit 变体不预缓存（体积大），首次在线访问时由运行时
 *   缓存优先策略自动缓存。
 */
const SHELL_ASSETS = [
  './index.html',
  './flutter_bootstrap.js',
  './main.dart.js',
  './flutter.js',
  './manifest.json',
  './favicon.png',
  './sqlite3.wasm',
  './sqflite_sw.js',
  './icons/Icon-192.png',
  './icons/Icon-512.png',
  './icons/Icon-maskable-192.png',
  './icons/Icon-maskable-512.png',
  './assets/AssetManifest.json',
  './assets/FontManifest.json',
  './assets/fonts/MaterialIcons-Regular.otf',
  './assets/packages/cupertino_icons/assets/CupertinoIcons.ttf',
  './assets/assets/fonts/NotoSansSC-subset.woff2',
  './canvaskit/canvaskit.js',
  './canvaskit/chromium/canvaskit.wasm',
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    try {
      const cache = await caches.open(SHELL_CACHE);
      await Promise.allSettled(SHELL_ASSETS.map((url) =>
        fetch(url, { cache: 'no-cache' })
          .then((res) => { if (res.ok) return cache.put(url, res); })
          .catch(() => {})
      ));
    } catch (_) {
      // 预缓存失败不阻塞 SW 安装
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    // 清理旧构建版本缓存，避免残留旧资源
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((k) => k.startsWith('quiz-') && k !== SHELL_CACHE && k !== RUNTIME_CACHE)
      .map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 仅处理同源请求；跨域（fonts.gstatic 等）走网络
  if (url.origin !== self.location.origin) return;

  // 页面导航：网络优先，离线回退缓存首页（App Shell 模式）
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      const cache = await caches.open(SHELL_CACHE);
      try {
        const res = await fetch(req);
        if (res.ok) await cache.put('./index.html', res.clone());
        return res;
      } catch (_) {
        const cached = await cache.match('./index.html');
        return cached || new Response(
          '离线模式：当前无网络且应用未缓存，请联网后打开。',
          { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
      }
    })());
    return;
  }

  // 静态资源（js / wasm / 字体 / 图片 / json / zip 等）：缓存优先，命中即返回
  if (/\.(js|wasm|woff2?|ttf|otf|png|svg|ico|json|zip|css|map|frag)$/.test(url.pathname)) {
    event.respondWith((async () => {
      const cache = await caches.open(RUNTIME_CACHE);
      const cached = await cache.match(req);
      if (cached) return cached;
      try {
        const res = await fetch(req);
        if (res.ok) await cache.put(req, res.clone());
        return res;
      } catch (_) {
        return new Response('', { status: 504 });
      }
    })());
  }
});
