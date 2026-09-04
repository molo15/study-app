/* 考研刷题 PWA 离线缓存 Service Worker
 * - 构建指纹：每次 `flutter build web` 后由 tools/post_build_sw.py 将 __BUILD_ID__
 *   替换为 main.dart.js 的 SHA-256 前缀，缓存据此版本化，发布新版本自动重建缓存。
 * - 策略：App Shell 预缓存（install）+ 静态资源缓存优先 + 页面导航网络优先。
 * - 仅处理同源 GET；跨域（如 fonts.gstatic.com 字体分片）走网络，不缓存。
 */
'use strict';

const BUILD_ID = '__BUILD_ID__';
const SHELL_CACHE = 'quiz-shell-' + BUILD_ID;
// 运行时缓存不带 BUILD_ID：题库 zip 等资源 URL 自带版本号（如 v0.14.0），
// 跨构建版本保留运行时缓存可避免每次发版后全量重新下载题库；
// 资源 URL 变化时自然由缓存优先策略重新抓取新版本。
const RUNTIME_CACHE = 'quiz-runtime';

/* CanvasKit 变体选择，必须与 flutter_bootstrap.js / index.html 的判定一致：
 * Chromium 内核（Chrome/Edge）用 chromium/ 子目录变体；
 * WebKit（Safari 及 iOS 全系浏览器）/Firefox 用根目录 full 变体。
 * 写死 chromium 变体时，iPad 会预缓存一个永远用不到的 5.4MB wasm。 */
const isChromium = (function () {
  try {
    // 注意：Service Worker 是独立的 Worker 作用域，与 window / 普通 Worker 不同：
    // 1) WorkerNavigator 不暴露 navigator.vendor（恒 undefined），不能照搬 index.html；
    // 2) WebCodecs 的 ImageDecoder 按规范只暴露给 Window 和 DedicatedWorker，
    //    ServiceWorkerGlobalScope 中不存在，检测它会让 Chromium 也恒为 false。
    // 因此 SW 侧只用 UA + 标准 Intl.Segmenter 判定：Chromium 系（Chrome/Edge/Opera/
    // 国产套壳）UA 均含 "Chrome/" 且支持 Segmenter；Safari 与 iOS 全系 UA 不含
    // "Chrome/"；旧版 Firefox 无 Segmenter——后两者都应使用根目录 full 变体，结果一致。
    var ua = self.navigator.userAgent || '';
    var isChromiumUA = ua.indexOf('Chrome/') !== -1 || ua.indexOf('Chromium/') !== -1;
    return isChromiumUA && typeof Intl.Segmenter !== 'undefined';
  } catch (_) {
    return false;
  }
})();
const CK_DIR = isChromium ? './canvaskit/chromium/' : './canvaskit/';

/* App Shell 预缓存清单：离线打开 App 的核心资源。
 * - 含 Flutter 引擎、主程序、数据库引擎（sqlite3.wasm + sqflite_sw.js）、
 *   中文字体（web woff2）、当前浏览器实际使用的 canvaskit 变体、图标、manifest。
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
  './assets/AssetManifest.bin',
  './assets/AssetManifest.bin.json',
  './assets/FontManifest.json',
  './assets/fonts/MaterialIcons-Regular.otf',
  './assets/fonts/fallback/Roboto-Regular.ttf',
  './assets/packages/cupertino_icons/assets/CupertinoIcons.ttf',
  './assets/assets/fonts/NotoSansSC-subset.woff2',
  CK_DIR + 'canvaskit.js',
  CK_DIR + 'canvaskit.wasm',
];

/* 仅 HTML 文档每次向服务器校验新鲜度；其余静态资源使用默认缓存策略：
 * 首访时页面已下载过这些资源，SW install 再 fetch 可直接命中浏览器 HTTP 缓存
 * （GitHub Pages 静态资源带 Cache-Control: max-age=600），弱网下不重复消耗流量；
 * 旧实现统一用 {cache:'no-cache'} 会让 10+MB 大文件在 install 阶段再走一遍网络。 */
const REVALIDATE_URLS = new Set(['./index.html']);

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    try {
      const cache = await caches.open(SHELL_CACHE);
      await Promise.allSettled(SHELL_ASSETS.map((url) => {
        var opts = REVALIDATE_URLS.has(url) ? { cache: 'no-cache' } : { cache: 'default' };
        return fetch(url, opts)
          .then((res) => { if (res.ok) return cache.put(url, res); })
          .catch(() => {});
      }));
      // BUILD_ID 不变而变体选择修正时，同名 shell 缓存会残留上一版误选的
      // canvaskit 变体（chromium/full 互错，单个 5-7MB），按本次清单清掉多余条目。
      const allowedUrls = new Set(SHELL_ASSETS.map((u) => new URL(u, self.location.href).href));
      const oldEntries = await cache.keys();
      await Promise.all(oldEntries.map((req) =>
        allowedUrls.has(req.url) ? null : cache.delete(req)));
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
    // runtime 中不带内容版本号的固定名资源（AssetManifest、fallback 字体等）跨版本
    // 会变旧，而静态资源策略是缓存优先、不重新校验；发版激活时清掉它们，强制下次取新版。
    // 题库 zip 的文件名自带版本号（bank-*-vX.Y.Z.zip），跨版本可复用，予以保留。
    // SHELL_ASSETS 覆盖的核心文件在 install 时已写入新 shell，刷新时回退命中，零额外流量。
    const runtime = await caches.open(RUNTIME_CACHE);
    for (const req of await runtime.keys()) {
      const path = new URL(req.url).pathname;
      if (path.indexOf('/assets/assets/banks/') !== -1) continue;
      await runtime.delete(req);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // CanvasKit 的 CJK 字形回退：flutter_bootstrap.js 已用 fontFallbackBaseUrl 把
  // fonts.gstatic.com 同源化为本站 /font-fallback/s/（该路径刻意不存在）。无论同源
  // 回退路径还是漏网的 gstatic/googleapis 直连，在国内都会被阻断或无谓请求服务器，
  // 这里统一立即返回 404，让引擎快速改用本地 NotoSansSC 子集，不打网络、不挂起。
  var blockedFontFallback = url.hostname === 'fonts.gstatic.com'
    || url.hostname === 'fonts.googleapis.com'
    || url.pathname.indexOf('/font-fallback/') !== -1;
  if (blockedFontFallback) {
    event.respondWith(new Response('', { status: 404, statusText: 'font fallback blocked' }));
    return;
  }
  // 其余跨域请求不干预，直接走网络
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

  // 静态资源（js / wasm / 字体 / 图片 / json / zip 等）：缓存优先，命中即返回。
  // 查找顺序：运行时缓存 → App Shell 预缓存 → 网络（取回后写入运行时缓存）。
  // 必须回退查 SHELL_CACHE，否则 install 预缓存的引擎/主程序在离线时无法使用。
  if (/\.(js|wasm|woff2?|ttf|otf|png|svg|ico|json|zip|css|map|frag)$/.test(url.pathname)) {
    event.respondWith((async () => {
      const runtime = await caches.open(RUNTIME_CACHE);
      const cached = await runtime.match(req)
        || await caches.open(SHELL_CACHE).then((c) => c.match(req));
      if (cached) return cached;
      try {
        const res = await fetch(req);
        if (res.ok) await runtime.put(req, res.clone());
        return res;
      } catch (_) {
        return new Response('', { status: 504 });
      }
    })());
  }
});
