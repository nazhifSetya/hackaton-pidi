/* =====================================================================
 * RootFacts — Service Worker (Workbox 7)
 * ---------------------------------------------------------------------
 * Tujuan: aplikasi tetap terbuka & mampu mendeteksi sayuran walau offline.
 *
 *   Precache (saat install) : app shell (HTML/CSS/JS/ikon) + model TF.js.
 *   Runtime cache           : font, pustaka CDN, dan berkas model T5 (HF Hub).
 * ===================================================================== */

importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');

if (!self.workbox) {
	console.error('[SW] Workbox tidak berhasil dimuat.');
} else {
	const wb = self.workbox;
	wb.setConfig({ debug: false });

	const { precacheAndRoute } = wb.precaching;
	const { registerRoute } = wb.routing;
	const { CacheFirst, NetworkFirst, StaleWhileRevalidate } = wb.strategies;
	const { ExpirationPlugin } = wb.expiration;
	const { CacheableResponsePlugin } = wb.cacheableResponse;

	const BUILD = 'ff-2026-07-16';
	const stamp = (files) => files.map((url) => ({ url, revision: BUILD }));

	// ---- 1. Precache: berkas inti yang wajib ada saat luring -------------
	precacheAndRoute(
		stamp([
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
			'assets/icons/favicon.ico',
			// Model Teachable Machine → agar deteksi tetap jalan tanpa internet.
			'model/model.json',
			'model/metadata.json',
			'model/weights.bin'
		])
	);

	const okStatus = () => new CacheableResponsePlugin({ statuses: [0, 200] });

	// ---- 2. Navigasi halaman: utamakan jaringan, jatuh ke cache ----------
	registerRoute(
		({ request }) => request.mode === 'navigate',
		new NetworkFirst({
			cacheName: 'rf-pages',
			networkTimeoutSeconds: 3,
			plugins: [okStatus()]
		})
	);

	// ---- 3. Google Fonts (stylesheet berubah pelan) ---------------------
	registerRoute(
		({ url }) => url.origin === 'https://fonts.googleapis.com',
		new StaleWhileRevalidate({ cacheName: 'rf-font-css' })
	);

	// ---- 4. Google Fonts (berkas font, praktis immutable) ---------------
	registerRoute(
		({ url }) => url.origin === 'https://fonts.gstatic.com',
		new CacheFirst({
			cacheName: 'rf-font-files',
			plugins: [okStatus(), new ExpirationPlugin({ maxEntries: 24, maxAgeSeconds: 31536000 })]
		})
	);

	// ---- 5. Pustaka CDN: TF.js, Transformers.js, Workbox, Lucide --------
	registerRoute(
		({ url }) =>
			['https://cdn.jsdelivr.net', 'https://unpkg.com', 'https://storage.googleapis.com'].includes(url.origin),
		new CacheFirst({
			cacheName: 'rf-vendor',
			plugins: [okStatus(), new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 2592000 })]
		})
	);

	// ---- 6. Berkas model dari Hugging Face Hub (LaMini-Flan-T5) ---------
	registerRoute(
		({ url }) =>
			url.hostname === 'huggingface.co' ||
			url.hostname.endsWith('.huggingface.co') ||
			url.hostname.endsWith('.hf.co'),
		new CacheFirst({
			cacheName: 'rf-llm-model',
			plugins: [okStatus(), new ExpirationPlugin({ maxEntries: 40, maxAgeSeconds: 7776000 })]
		})
	);

	// ---- 7. Fallback aset same-origin yang belum tercakup --------------
	registerRoute(
		({ url }) => url.origin === self.location.origin,
		new StaleWhileRevalidate({ cacheName: 'rf-runtime' })
	);

	// Aktifkan SW baru sesegera mungkin.
	self.addEventListener('install', () => self.skipWaiting());
	self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));
}
