import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

// Jeda antar pemindaian (ms) — dikelola lewat setInterval berulang.
const SCAN_INTERVAL_MS = 1800;
// Ambang kepercayaan agar sebuah deteksi dianggap "berhasil" → kamera auto-stop.
// Nilai sedang: cukup tinggi untuk mengabaikan bingkai kosong/ragu, cukup rendah
// agar sayuran nyata (biasanya 60–90%) pasti membekukan hasil. Ambang ini HANYA
// menggerbang auto-stop, BUKAN tampilan (label teratas tetap tampil tiap tick →
// UI tak pernah macet menunggu).
const AUTO_STOP_CONFIDENCE = 55;
const LOG_TAG = '[RF-Dafina]';

class RootFactsApp {
	// State internal disimpan di #private fields.
	#scanHandle = null;   // id dari setInterval
	#busy = false;        // penjaga agar tick tak tumpang tindih
	#activeLabel = null;  // label yang sedang tampil (hindari regenerasi)

	constructor() {
		this.detector = null;
		this.camera = null;
		this.funFactGenerator = null;
		this.ui = new UIHandler();
		this.isRunning = false;
		this.config = APP_CONFIG;
		this.currentFunFact = '';

		this.ui.disableButton();

		this.bindEvents();
		this.init();
		this.registerServiceWorker();
	}

	bindEvents() {
		this.ui.bindEvents({
			onToggleCamera: () => this.toggleCamera(),
			onCameraChange: () => this.onCameraChange(),
			onScanAgain: () => this.#restartScan()
		});
	}

	async init() {
		try {
			this.ui.updateHeaderStatus('Memuat model...', false);

			this.camera = new CameraService();
			this.detector = new DetectionService();
			this.funFactGenerator = new FunFactService();

			// (1) Model penglihatan (ringan) dimuat lebih dulu.
			await this.detector.loadModel();
			console.log(`${LOG_TAG} TensorFlow.js siap. Label:`, this.detector.labelList);

			// (2) Model bahasa (lebih berat) diunduh SAMPAI TUNTAS sebelum aplikasi
			//     dinyatakan "Siap". Persentase unduhan ditampilkan di header agar
			//     pengguna tahu progresnya. Tombol scan sengaja tetap nonaktif di
			//     tahap ini supaya fun fact tak pernah menggantung menunggu unduhan.
			this.ui.updateHeaderStatus('Memuat Model... 0%', false);
			await this.funFactGenerator.loadModel((percent) => {
				this.ui.updateHeaderStatus(`Memuat Model... ${percent}%`, false);
				console.log(`${LOG_TAG} Unduh model bahasa: ${percent}%`);
			});
			console.log(`${LOG_TAG} Transformers.js (FLAN-T5-base) siap.`);

			// (3) Kedua model siap → barulah tombol diaktifkan & status jadi "Siap".
			this.ui.updateHeaderStatus('Siap', false);
			this.ui.enableButton();
		} catch (error) {
			logError('Gagal menginisialisasi aplikasi', error);
			this.ui.updateHeaderStatus('Error', false);
			this.ui.showError(`Gagal menginisialisasi: ${error.message}`);
			this.ui.disableButton();
		}
	}

	registerServiceWorker() {
		if (!('serviceWorker' in navigator)) return;
		window.addEventListener('load', () => {
			navigator.serviceWorker
				.register('./sw.js')
				.then((reg) => console.log(`${LOG_TAG} Service Worker aktif, scope:`, reg.scope))
				.catch((err) => logError('Registrasi Service Worker gagal', err));
		});
	}

	async toggleCamera() {
		if (this.isRunning) {
			this.stopDetection();
			this.stopCamera();
		} else {
			await this.#activateScan();
		}
	}

	// Nyalakan kamera lalu mulai siklus deteksi bila kamera benar-benar siap.
	// Dipakai bersama oleh toggleCamera() dan onCameraChange().
	async #activateScan() {
		await this.startCamera();
		if (this.camera.isReady()) {
			this.startDetection();
		}
	}

	async startCamera() {
		try {
			await this.camera.startCamera();
			this.ui.updateCameraUI(true);
		} catch (error) {
			logError('Gagal memulai kamera', error);
			this.ui.showError(error.message);
			this.ui.updateCameraUI(false);
		}
	}

	stopCamera() {
		this.camera.stopCamera();
		this.ui.updateCameraUI(false);
		this.ui.switchToState('idle');
		this.#activeLabel = null;
	}

	async onCameraChange() {
		// Ganti perangkat kamera hanya bermakna saat sedang berjalan: hentikan
		// siklus lama, lalu nyalakan ulang dengan pilihan kamera yang baru.
		if (!this.isRunning) return;
		this.stopDetection();
		await this.#activateScan();
	}

	startDetection() {
		if (this.isRunning) return;
		this.isRunning = true;
		this.#activeLabel = null;
		this.ui.switchToState('loading');

		this.detectLoop();                                              // pindai pertama segera
		this.#scanHandle = setInterval(() => this.detectLoop(), SCAN_INTERVAL_MS);
	}

	stopDetection() {
		this.isRunning = false;
		if (this.#scanHandle) {
			clearInterval(this.#scanHandle);
			this.#scanHandle = null;
		}
		this.#busy = false;
	}

	async detectLoop() {
		// Lewati tick bila proses sebelumnya masih jalan atau kamera belum siap.
		if (this.#busy || !this.isRunning) return;
		if (!this.camera.isReady()) return;

		this.#busy = true;
		try {
			const prediction = await this.detector.predict(this.camera.video);
			console.log(`${LOG_TAG} Deteksi: ${prediction.className} (${prediction.confidence}%)`);

			if (!this.isRunning) return;

			if (prediction.className !== this.#activeLabel) {
				this.#activeLabel = prediction.className;
				await this.generateAndShowResults(prediction);
			}

			// Auto-stop (saran reviewer): begitu satu deteksi berhasil — fun fact
			// sudah tampil DAN kepercayaan cukup — kamera dihentikan otomatis supaya
			// hasil + fun fact STABIL & mudah dibaca, sekaligus mencegah deteksi
			// berulang yang boros daya. Pengguna menekan "Scan Lagi" untuk memindai
			// sayuran berikutnya.
			if (this.isRunning && this.currentFunFact &&
				prediction.confidence >= AUTO_STOP_CONFIDENCE) {
				this.#finishScan();
			}
		} catch (error) {
			logError('Kesalahan saat memindai', error);
		} finally {
			this.#busy = false;
		}
	}

	// Hentikan siklus deteksi + kamera TANPA kembali ke idle: kartu hasil & fun fact
	// dibiarkan tampil stabil, dan tombol "Scan Lagi" dimunculkan. (Beda dari
	// stopCamera() yang menyembunyikan hasil saat pengguna berhenti manual.)
	#finishScan() {
		this.stopDetection();
		this.camera.stopCamera();
		this.ui.freezeScan();
		console.log(`${LOG_TAG} Deteksi selesai → kamera auto-stop, hasil dibekukan.`);
	}

	// Dari kondisi beku (kamera mati, hasil tampil) → mulai memindai lagi.
	async #restartScan() {
		if (this.isRunning) return;
		await this.#activateScan();
	}

	async generateAndShowResults(detectionResult) {
		// Sayuran berganti → buang fakta lama agar tak salah dipasang ke label baru.
		this.currentFunFact = '';
		try {
			// Tampilkan nama sayuran dulu dengan placeholder (spinner) fun fact.
			// Model sudah dimuat penuh saat init, jadi generasi ini singkat saja.
			this.ui.showResults(detectionResult, null);

			const { funFact } = await this.funFactGenerator.generateFunFact(detectionResult.className);
			this.currentFunFact = funFact;
			console.log(`${LOG_TAG} Fun fact ${detectionResult.className}: ${funFact}`);

			this.ui.showResults(detectionResult, { funFact });
		} catch (error) {
			logError('Gagal menampilkan hasil', error);
			// Kegagalan sesaat saat generate → jangan kunci label ini; biarkan
			// tick berikutnya mencoba lagi daripada menampilkan fakta kosong.
			this.#activeLabel = null;
			this.ui.updateFunFactState('error');
		}
	}
}

document.addEventListener('DOMContentLoaded', () => {
	const app = new RootFactsApp();

	if (typeof lucide !== 'undefined') {
		lucide.createIcons();
	}
});

export default RootFactsApp;
