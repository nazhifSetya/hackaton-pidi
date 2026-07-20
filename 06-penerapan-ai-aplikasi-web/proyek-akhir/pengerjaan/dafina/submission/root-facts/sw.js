/* ---------------------------------------------------------------------------
 * RootFacts · Service Worker (Workbox 7)
 * ---------------------------------------------------------------------------
 * Sasaran offline-first: aplikasi tetap terbuka DAN tetap bisa mendeteksi
 * sayuran walau tanpa internet. Karena itu app shell (HTML/CSS/JS/ikon) dan
 * berkas model TensorFlow.js sama-sama di-precache saat install; sedangkan
 * pustaka CDN dan bobot model bahasa (Hugging Face) di-cache saat runtime.
 * ------------------------------------------------------------------------- */

importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');

// Cocokkan host milik ekosistem Hugging Face (termasuk CDN xet & subdomain).
const HF_HOST_PATTERN = /(^|\.)(huggingface\.co|hf\.co)$/;
const VENDOR_ORIGINS = new Set([
	'https://cdn.jsdelivr.net',
	'https://unpkg.com',
	'https://storage.googleapis.com'
]);

function bootServiceWorker(wb) {
	const { core, precaching, routing, strategies, expiration, cacheableResponse } = wb;

	// Nama cache diberi awalan khas agar mudah dibedakan di DevTools.
	core.setCacheNameDetails({ prefix: 'rootfacts-dmr', suffix: 'v1' });
	core.setConfig?.({ debug: false });

	const REV = 'dmr-2026-07-20-r2';
	const withRev = (list) => list.map((url) => ({ url, revision: REV }));

	const APP_SHELL = [
		'index.html',
		'manifest.json',
		'assets/css/styles.css',
		'assets/js/core/app.js',
		'assets/js/core/config.js',
		'assets/js/core/utils.js',
		'assets/js/services/camera.service.js',
		'assets/js/services/detection.service.js',
		'assets/js/services/facts.service.js',
		'assets/js/ui/ui.handler.js',
		'assets/icons/icon-192x192.png',
		'assets/icons/icon-512x512.png',
		'assets/icons/apple-touch-icon.png',
		'assets/icons/favicon.ico'
	];

	const VISION_MODEL = [
		'model/model.json',
		'model/metadata.json',
		'model/weights.bin'
	];

	precaching.precacheAndRoute(withRev([...APP_SHELL, ...VISION_MODEL]));

	const acceptOpaque = () => new cacheableResponse.CacheableResponsePlugin({ statuses: [0, 200] });
	const keepFor = (days, max) =>
		new expiration.ExpirationPlugin({ maxEntries: max, maxAgeSeconds: days * 24 * 60 * 60 });

	// (a) Navigasi halaman → utamakan jaringan, jatuh ke cache saat luring.
	routing.registerRoute(
		({ request }) => request.mode === 'navigate',
		new strategies.NetworkFirst({
			cacheName: 'df-navigation',
			networkTimeoutSeconds: 3,
			plugins: [acceptOpaque()]
		})
	);

	// (b) Google Fonts — lembar gaya (jarang berubah).
	routing.registerRoute(
		({ url }) => url.origin === 'https://fonts.googleapis.com',
		new strategies.StaleWhileRevalidate({ cacheName: 'df-google-fonts' })
	);

	// (c) Google Fonts — berkas font (praktis immutable).
	routing.registerRoute(
		({ url }) => url.origin === 'https://fonts.gstatic.com',
		new strategies.CacheFirst({
			cacheName: 'df-font-files',
			plugins: [acceptOpaque(), keepFor(365, 20)]
		})
	);

	// (d) Pustaka CDN: TensorFlow.js, Transformers.js loader, Workbox, Lucide.
	routing.registerRoute(
		({ url }) => VENDOR_ORIGINS.has(url.origin),
		new strategies.CacheFirst({
			cacheName: 'df-cdn',
			plugins: [acceptOpaque(), keepFor(30, 60)]
		})
	);

	// (e) Bobot & tokenizer model bahasa dari Hugging Face Hub (FLAN-T5).
	routing.registerRoute(
		({ url }) => HF_HOST_PATTERN.test(url.hostname),
		new strategies.CacheFirst({
			cacheName: 'df-hf-hub',
			plugins: [acceptOpaque(), keepFor(90, 60)]
		})
	);

	// (f) Aset same-origin lain yang belum tertangani di atas.
	routing.registerRoute(
		({ url }) => url.origin === self.location.origin,
		new strategies.StaleWhileRevalidate({ cacheName: 'df-misc' })
	);

	// Segera aktifkan SW versi baru tanpa menunggu tab lama tertutup.
	self.addEventListener('install', () => self.skipWaiting());
	self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));
}

if (self.workbox) {
	bootServiceWorker(self.workbox);
} else {
	console.error('[SW] Pustaka Workbox tidak tersedia; caching dilewati.');
}
