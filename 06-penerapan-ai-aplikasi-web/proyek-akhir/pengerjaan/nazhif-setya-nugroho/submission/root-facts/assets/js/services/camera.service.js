import {
	getCameraErrorMessage,
	logError
} from '../core/utils.js';

class CameraService {
	constructor() {
		this.stream = null;
		this.video = null;
		this.canvas = null;
		this.config = null;
		this.facingMode = 'environment';
		this.availableDevices = [];
		this.cameraSelect = null;

		this.initializeElements();
		this.init();
	}

	initializeElements() {
		this.video = document.getElementById('videoElement');
		this.canvas = document.getElementById('canvasElement');
		this.cameraSelect = document.getElementById('camera-select');
	}

	async init() {
		await this.loadCameras();
	}

	async loadCameras() {
		try {
			const probe = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
			probe.getTracks().forEach(t => t.stop());
			const devices = await navigator.mediaDevices.enumerateDevices();
			this.availableDevices = devices.filter(d => d.kind === 'videoinput');
		} catch (error) {
			logError('Gagal memuat kamera', error);
			throw new Error(`Akses kamera gagal: ${error.message}`);
		}
	}

	async startCamera() {
		try {
			if (this.stream) {
				this.stopCamera();
			}

			const selected = this.cameraSelect?.value || 'default';
			this.facingMode = selected === 'front' ? 'user' : 'environment';

			const constraints = {
				video: {
					facingMode: { ideal: this.facingMode },
					width: { ideal: 640 },
					height: { ideal: 480 }
				},
				audio: false
			};

			this.stream = await navigator.mediaDevices.getUserMedia(constraints);
			if (!this.video) throw new Error('Elemen video tidak ditemukan');
			this.video.srcObject = this.stream;

			await new Promise((resolve) => {
				if (this.video.readyState >= 2) return resolve();
				this.video.onloadedmetadata = () => resolve();
			});
			await this.video.play();
		} catch (error) {
			logError('Gagal memulai kamera', error);
			const errorMessage = getCameraErrorMessage(error);
			throw new Error(errorMessage);
		}
	}

	stopCamera() {
		if (this.stream) {
			this.stream.getTracks().forEach(track => track.stop());
			this.stream = null;
		}
		if (this.video) {
			this.video.srcObject = null;
		}
	}

	setFPS(fps) {
		// [Skilled] tidak dikerjakan pada tier Basic.
	}

	isActive() {
		return this.stream !== null && this.stream.getTracks().some(t => t.readyState === 'live');
	}

	isReady() {
		return !!this.video && this.video.readyState >= 2 && this.isActive();
	}
}

export default CameraService;
