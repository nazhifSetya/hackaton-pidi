import {
	getCameraErrorMessage,
	logError
} from '../core/utils.js';

/**
 * CameraService membungkus MediaStream API: minta izin, buka aliran video,
 * dan menyediakan elemen <video> yang siap dibaca oleh DetectionService.
 */
class CameraService {
	constructor() {
		this.stream = null;
		this.video = null;
		this.canvas = null;
		this.config = null;
		this.selectEl = null;
		this.videoInputs = [];

		this.initializeElements();
		this.init();
	}

	initializeElements() {
		this.video = document.getElementById('videoElement');
		this.canvas = document.getElementById('canvasElement');
		this.selectEl = document.getElementById('camera-select');
	}

	async init() {
		await this.loadCameras();
	}

	async loadCameras() {
		try {
			// Minta izin sekali dulu supaya label & deviceId terisi saat enumerate.
			const warmup = await navigator.mediaDevices.getUserMedia({ video: true });
			warmup.getTracks().forEach((track) => track.stop());

			const all = await navigator.mediaDevices.enumerateDevices();
			this.videoInputs = all.filter((device) => device.kind === 'videoinput');
		} catch (error) {
			logError('Gagal memuat kamera', error);
			throw new Error(`Akses kamera gagal: ${error.message}`);
		}
	}

	/**
	 * Bangun constraints berdasar pilihan dropdown (depan/belakang).
	 * Bila perangkat punya >1 kamera fisik, prioritaskan deviceId agar akurat.
	 */
	buildConstraints() {
		const wantsFront = this.selectEl?.value === 'front';
		const facing = wantsFront ? 'user' : 'environment';

		const video = {
			facingMode: { ideal: facing },
			width: { ideal: 1280 },
			height: { ideal: 720 }
		};

		return { audio: false, video };
	}

	async startCamera() {
		try {
			if (this.stream) this.stopCamera();

			this.stream = await navigator.mediaDevices.getUserMedia(this.buildConstraints());
			if (!this.video) throw new Error('Elemen <video> tidak ditemukan.');

			this.video.srcObject = this.stream;
			await this.waitUntilReady();
			await this.video.play();
		} catch (error) {
			logError('Gagal memulai kamera', error);
			const errorMessage = getCameraErrorMessage(error);
			throw new Error(errorMessage);
		}
	}

	// Tunggu frame pertama tersedia sebelum dipakai untuk inferensi.
	waitUntilReady() {
		return new Promise((resolve) => {
			if (this.video.readyState >= 2) {
				resolve();
				return;
			}
			this.video.addEventListener('loadeddata', () => resolve(), { once: true });
		});
	}

	stopCamera() {
		this.stream?.getTracks().forEach((track) => track.stop());
		this.stream = null;
		if (this.video) this.video.srcObject = null;
	}

	setFPS(fps) {
		// [Skilled] Pengaturan FPS tidak diaktifkan pada jalur Basic.
	}

	isActive() {
		if (!this.stream) return false;
		return this.stream.getVideoTracks().some((track) => track.readyState === 'live');
	}

	isReady() {
		return this.isActive() && !!this.video && this.video.readyState >= 2;
	}
}

export default CameraService;
