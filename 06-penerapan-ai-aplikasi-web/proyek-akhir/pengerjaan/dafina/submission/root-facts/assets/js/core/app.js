import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

// Jeda antar pemindaian (ms) — dikelola lewat setInterval berulang.
const SCAN_INTERVAL_MS = 1800;
const LOG_TAG = '[RF-Dafina]';

class RootFactsApp {
	// State internal disimpan di #private fields.
	#scanHandle = null;   // id dari setInterval
	#busy = false;        // penjaga agar tick tak tumpang tindih
	#activeLabel = null;  // label yang sedang tampil (hindari regenerasi)
	#factReady = null;    // promise kesiapan model bahasa (dimuat di latar belakang)

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
			onCameraChange: () => this.onCameraChange()
		});
	}

	async init() {
		try {
			this.ui.updateHeaderStatus('Memuat model...', false);

			this.camera = new CameraService();
			this.detector = new DetectionService();
			this.funFactGenerator = new FunFactService();

			// Model penglihatan (ringan) dimuat lebih dulu, lalu tombol scan
			// langsung diaktifkan supaya kamera bisa dipakai tanpa menunggu.
			await this.detector.loadModel();
			console.log(`${LOG_TAG} TensorFlow.js siap. Label:`, this.detector.labelList);

			this.ui.updateHeaderStatus('Siap', false);
			this.ui.enableButton();

			// Model bahasa (lebih berat) dimuat di latar belakang; fun fact akan
			// muncul begitu model siap — kamera & label tetap jalan lebih dulu.
			this.#factReady = this.funFactGenerator
				.loadModel()
				.then(() => { console.log(`${LOG_TAG} Transformers.js (FLAN-T5-base) siap.`); return true; })
				.catch((err) => { logError('Model fun fact gagal dimuat', err); return false; });
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
			} else if (this.currentFunFact) {
				// Label sama & fakta sudah ada → cukup segarkan kartu (tanpa regenerasi).
				this.ui.showResults(prediction, { funFact: this.currentFunFact });
			}
		} catch (error) {
			logError('Kesalahan saat memindai', error);
		} finally {
			this.#busy = false;
		}
	}

	async generateAndShowResults(detectionResult) {
		// Sayuran berganti → buang fakta lama agar tak salah dipasang ke label baru.
		this.currentFunFact = '';
		try {
			// Tampilkan nama sayuran dulu dengan placeholder (spinner) fun fact.
			this.ui.showResults(detectionResult, null);

			// Bila model bahasa belum selesai dimuat, tunggu dulu (spinner tetap
			// tampil). Bila gagal dimuat permanen, tampilkan error tanpa spam retry.
			const ready = this.#factReady ? await this.#factReady : this.funFactGenerator.isReady();
			if (!ready) {
				this.ui.updateFunFactState('error');
				return;
			}

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
