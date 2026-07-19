import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

// Jeda antar pemindaian (ms) — dikelola lewat setInterval berulang.
const SCAN_INTERVAL_MS = 1800;
const LOG_TAG = '[RootFacts·DMR]';

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
			onCameraChange: () => this.onCameraChange()
		});
	}

	async init() {
		try {
			this.ui.updateHeaderStatus('Memuat model...', false);

			this.camera = new CameraService();
			this.detector = new DetectionService();
			this.funFactGenerator = new FunFactService();

			await this.detector.loadModel();
			console.log(`${LOG_TAG} TensorFlow.js siap. Label:`, this.detector.labelList);

			this.ui.updateHeaderStatus('Memuat AI...', false);
			await this.funFactGenerator.loadModel();
			console.log(`${LOG_TAG} Transformers.js (Qwen2.5-0.5B) siap.`);

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
			return;
		}
		await this.startCamera();
		if (this.camera.isReady()) this.startDetection();
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
		if (!this.isRunning) return;
		this.stopDetection();
		await this.startCamera();
		if (this.camera.isReady()) this.startDetection();
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
			} else {
				this.ui.showResults(prediction, { funFact: this.currentFunFact });
			}
		} catch (error) {
			logError('Kesalahan saat memindai', error);
		} finally {
			this.#busy = false;
		}
	}

	async generateAndShowResults(detectionResult) {
		try {
			// Tampilkan nama sayuran dulu dengan placeholder (spinner) fun fact.
			this.ui.showResults(detectionResult, null);

			const { funFact } = await this.funFactGenerator.generateFunFact(detectionResult.className);
			this.currentFunFact = funFact;
			console.log(`${LOG_TAG} Fun fact ${detectionResult.className}: ${funFact}`);

			this.ui.showResults(detectionResult, { funFact });
		} catch (error) {
			logError('Gagal menampilkan hasil', error);
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
