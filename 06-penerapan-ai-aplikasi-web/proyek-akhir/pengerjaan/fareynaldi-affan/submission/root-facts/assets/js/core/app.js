import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

// Jeda antar-pemindaian (ms). Dijadwalkan ulang secara rekursif via setTimeout.
const SCAN_INTERVAL_MS = 1600;
const LOG_TAG = '[RootFacts·FA]';

class RootFactsApp {
	constructor() {
		this.detector = null;
		this.camera = null;
		this.funFactGenerator = null;
		this.ui = new UIHandler();
		this.isRunning = false;
		this.currentLoopId = null;
		this.config = APP_CONFIG;
		this.currentFunFact = '';

		// Label yang sedang tampil; dipakai agar fun fact tak digenerate berulang.
		this.activeLabel = null;
		this.scanTimer = null;

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
			console.log(`${LOG_TAG} Model TensorFlow.js siap. Label:`, this.detector.labels);

			this.ui.updateHeaderStatus('Memuat AI...', false);
			await this.funFactGenerator.loadModel();
			console.log(`${LOG_TAG} Model Transformers.js (LaMini-Flan-T5) siap.`);

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
		window.addEventListener('load', async () => {
			try {
				const reg = await navigator.serviceWorker.register('./sw.js');
				console.log(`${LOG_TAG} Service Worker terdaftar pada scope:`, reg.scope);
			} catch (err) {
				logError('Registrasi Service Worker gagal', err);
			}
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
		this.activeLabel = null;
	}

	async onCameraChange() {
		if (!this.isRunning) return;
		this.stopDetection();
		await this.startCamera();
		if (this.camera.isReady()) this.startDetection();
	}

	startDetection() {
		this.isRunning = true;
		const loopId = Symbol('scan');
		this.currentLoopId = loopId;
		this.ui.switchToState('loading');
		this.runScan(loopId); // mulai pemindaian pertama segera.
	}

	stopDetection() {
		this.isRunning = false;
		this.currentLoopId = null;
		if (this.scanTimer) {
			clearTimeout(this.scanTimer);
			this.scanTimer = null;
		}
	}

	// Satu siklus pemindaian; menjadwalkan siklus berikutnya bila masih aktif.
	async runScan(loopId) {
		if (!this.isRunning || this.currentLoopId !== loopId) return;

		try {
			if (this.camera.isReady()) {
				const prediction = await this.detector.predict(this.camera.video);
				console.log(`${LOG_TAG} Deteksi: ${prediction.className} (${prediction.confidence}%)`);

				if (this.currentLoopId !== loopId) return;

				if (prediction.className !== this.activeLabel) {
					this.activeLabel = prediction.className;
					await this.generateAndShowResults(prediction);
				} else {
					this.ui.showResults(prediction, { funFact: this.currentFunFact });
				}
			}
		} catch (error) {
			logError('Error saat pemindaian', error);
		}

		if (this.isRunning && this.currentLoopId === loopId) {
			this.scanTimer = setTimeout(() => this.runScan(loopId), SCAN_INTERVAL_MS);
		}
	}

	async generateAndShowResults(detectionResult) {
		try {
			// Tampilkan hasil deteksi dulu dengan placeholder fun fact (state loading).
			this.ui.showResults(detectionResult, null);

			const { funFact } = await this.funFactGenerator.generateFunFact(detectionResult.className);
			this.currentFunFact = funFact;
			console.log(`${LOG_TAG} Fun fact "${detectionResult.className}":`, funFact);

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
