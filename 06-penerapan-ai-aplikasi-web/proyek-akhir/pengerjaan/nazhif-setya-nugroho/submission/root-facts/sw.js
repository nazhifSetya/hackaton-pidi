/* Service Worker untuk RootFacts App - berbasis Workbox 7.
 * Strategy caching per resource:
 *   - App shell (HTML + CSS + JS + icons + model TF.js)      => Precache (install-time)
 *   - Navigation HTML                                          => NetworkFirst (fresh saat online, cache saat offline)
 *   - Library eksternal (jsdelivr, unpkg, workbox CDN)         => CacheFirst (versi lock, jarang berubah)
 *   - Google Fonts stylesheet + files                          => StaleWhileRevalidate
 *   - Model Transformers.js dari HuggingFace + LFS CDN         => CacheFirst (file besar, immutable per revisi)
 */

importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');

if (workbox) {
	workbox.setConfig({ debug: false });

	const { precacheAndRoute } = workbox.precaching;
	const { registerRoute, setDefaultHandler } = workbox.routing;
	const { StaleWhileRevalidate, CacheFirst, NetworkFirst } = workbox.strategies;
	const { ExpirationPlugin } = workbox.expiration;
	const { CacheableResponsePlugin } = workbox.cacheableResponse;

	const REVISION = 'v2.0.0';

	// === Precache: app shell + model TF.js (auto tersedia offline setelah install SW) ===
	precacheAndRoute([
		{ url: 'index.html', revision: REVISION },
		{ url: 'manifest.json', revision: REVISION },
		{ url: 'assets/css/styles.css', revision: REVISION },
		{ url: 'assets/js/core/app.js', revision: REVISION },
		{ url: 'assets/js/core/config.js', revision: REVISION },
		{ url: 'assets/js/core/utils.js', revision: REVISION },
		{ url: 'assets/js/services/camera.service.js', revision: REVISION },
		{ url: 'assets/js/services/detection.service.js', revision: REVISION },
		{ url: 'assets/js/services/facts.service.js', revision: REVISION },
		{ url: 'assets/js/ui/ui.handler.js', revision: REVISION },
		{ url: 'assets/icons/favicon.ico', revision: REVISION },
		{ url: 'assets/icons/icon-192x192.png', revision: REVISION },
		{ url: 'assets/icons/icon-512x512.png', revision: REVISION },
		{ url: 'assets/icons/apple-touch-icon.png', revision: REVISION },
		// Model TensorFlow.js Teachable Machine (WAJIB offline)
		{ url: 'model/model.json', revision: REVISION },
		{ url: 'model/metadata.json', revision: REVISION },
		{ url: 'model/weights.bin', revision: REVISION }
	]);

	// === Navigasi HTML: NetworkFirst supaya update deploy langsung terbaca, fallback ke cache ===
	registerRoute(
		({ request }) => request.mode === 'navigate',
		new NetworkFirst({
			cacheName: 'pages',
			networkTimeoutSeconds: 3,
			plugins: [new CacheableResponsePlugin({ statuses: [0, 200] })]
		})
	);

	// === Google Fonts stylesheet (kecil, sering berubah minor) ===
	registerRoute(
		({ url }) => url.origin === 'https://fonts.googleapis.com',
		new StaleWhileRevalidate({ cacheName: 'google-fonts-stylesheets' })
	);

	// === Google Fonts font files (immutable, cache lama) ===
	registerRoute(
		({ url }) => url.origin === 'https://fonts.gstatic.com',
		new CacheFirst({
			cacheName: 'google-fonts-webfonts',
			plugins: [
				new CacheableResponsePlugin({ statuses: [0, 200] }),
				new ExpirationPlugin({ maxEntries: 20, maxAgeSeconds: 365 * 24 * 60 * 60 })
			]
		})
	);

	// === Library CDN (TF.js, Transformers.js loader, Workbox, Lucide) — version-locked, immutable ===
	registerRoute(
		({ url }) =>
			url.origin === 'https://cdn.jsdelivr.net' ||
			url.origin === 'https://unpkg.com' ||
			url.origin === 'https://storage.googleapis.com',
		new CacheFirst({
			cacheName: 'cdn-libs',
			plugins: [
				new CacheableResponsePlugin({ statuses: [0, 200] }),
				new ExpirationPlugin({ maxEntries: 60, maxAgeSeconds: 30 * 24 * 60 * 60 })
			]
		})
	);

	// === HuggingFace model files (SmolLM2-135M ONNX + tokenizer) — file besar, per-revision immutable ===
	registerRoute(
		({ url }) =>
			url.origin === 'https://huggingface.co' ||
			url.origin === 'https://cdn-lfs.huggingface.co' ||
			url.origin === 'https://cas-bridge.xethub.hf.co' ||
			url.hostname.endsWith('.hf.co'),
		new CacheFirst({
			cacheName: 'hf-models',
			plugins: [
				new CacheableResponsePlugin({ statuses: [0, 200] }),
				new ExpirationPlugin({ maxEntries: 30, maxAgeSeconds: 90 * 24 * 60 * 60 })
			]
		})
	);

	// === Fallback: file same-origin lain (kalau ada asset yang lupa didaftar precache) ===
	registerRoute(
		({ url }) => url.origin === self.location.origin,
		new StaleWhileRevalidate({ cacheName: 'same-origin-fallback' })
	);

	self.addEventListener('install', () => self.skipWaiting());
	self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));
} else {
	console.error('Workbox gagal dimuat.');
}
