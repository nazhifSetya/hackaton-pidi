import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError, createDelay } from './utils.js';

const DETECTION_INTERVAL_MS = 1500;

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
		this.lastDetectedLabel = null;

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
			console.log('[RootFacts] TensorFlow.js model loaded. Labels:', this.detector.labels);

			this.ui.updateHeaderStatus('Memuat AI...', false);
			await this.funFactGenerator.loadModel();
			console.log('[RootFacts] Transformers.js model loaded.');

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
				.then(reg => console.log('[RootFacts] Service Worker terdaftar:', reg.scope))
				.catch(err => logError('Registrasi Service Worker gagal', err));
		});
	}

	async toggleCamera() {
		if (this.isRunning) {
			this.stopDetection();
			this.stopCamera();
		} else {
			await this.startCamera();
			if (this.camera.isReady()) {
				this.startDetection();
			}
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
		this.lastDetectedLabel = null;
	}

	async onCameraChange() {
		if (this.isRunning) {
			this.stopDetection();
			await this.startCamera();
			if (this.camera.isReady()) {
				this.startDetection();
			}
		}
	}

	startDetection() {
		this.isRunning = true;
		const loopId = Symbol('loop');
		this.currentLoopId = loopId;
		this.ui.switchToState('loading');
		this.detectLoop(loopId);
	}

	stopDetection() {
		this.isRunning = false;
		this.currentLoopId = null;
	}

	async detectLoop(loopId) {
		while (this.isRunning && this.currentLoopId === loopId) {
			try {
				if (!this.camera.isReady()) {
					await createDelay(APP_CONFIG.detectionRetryInterval);
					continue;
				}

				const result = await this.detector.predict(this.camera.video);
				console.log('[RootFacts] Detection:', result.className, `${result.confidence}%`);

				if (this.currentLoopId !== loopId) return;

				if (result.className !== this.lastDetectedLabel) {
					this.lastDetectedLabel = result.className;
					await this.generateAndShowResults(result);
				} else {
					this.ui.showResults(result, { funFact: this.currentFunFact });
				}
			} catch (error) {
				logError('Error di detection loop', error);
			}
			await createDelay(DETECTION_INTERVAL_MS);
		}
	}

	async generateAndShowResults(detectionResult) {
		try {
			this.ui.showResults(detectionResult, null);

			const result = await this.funFactGenerator.generateFunFact(detectionResult.className);
			this.currentFunFact = result.funFact;
			console.log('[RootFacts] Fun fact for', detectionResult.className, '->', this.currentFunFact);
			this.ui.showResults(detectionResult, { funFact: this.currentFunFact });
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
