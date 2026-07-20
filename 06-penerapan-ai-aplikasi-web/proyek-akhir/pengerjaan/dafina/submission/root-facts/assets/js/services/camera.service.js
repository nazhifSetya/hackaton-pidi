import {
	getCameraErrorMessage,
	logError
} from '../core/utils.js';

/*
 * CameraService — pengelola aliran kamera (MediaStream API).
 * Bertugas meminta izin, memilih perangkat kamera, dan menyediakan elemen
 * <video> yang siap dibaca DetectionService. Pemilihan kamera memakai
 * deviceId eksak bila perangkat memiliki lebih dari satu kamera.
 */
class CameraService {
	#stream = null;
	#videoDevices = [];
	#select = null;

	constructor() {
		this.video = null;
		this.canvas = null;
		this.config = null;

		this.initializeElements();
		this.init();
	}

	initializeElements() {
		this.video = document.getElementById('videoElement');
		this.canvas = document.getElementById('canvasElement');
		this.#select = document.getElementById('camera-select');
	}

	async init() {
		await this.loadCameras();
	}

	async loadCameras() {
		try {
			// Minta izin sekali supaya enumerateDevices mengembalikan deviceId+label.
			const primer = await navigator.mediaDevices.getUserMedia({ video: true });
			primer.getTracks().forEach((track) => track.stop());

			const devices = await navigator.mediaDevices.enumerateDevices();
			this.#videoDevices = devices.filter((device) => device.kind === 'videoinput');
		} catch (error) {
			logError('Gagal memuat kamera', error);
			throw new Error(`Akses kamera gagal: ${error.message}`);
		}
	}

	/*
	 * Buka aliran kamera sesuai pilihan depan/belakang. Pemilihan diutamakan
	 * lewat LABEL perangkat karena urutan enumerateDevices() TIDAK dijamin
	 * (indeks tak bisa dipercaya — di sebagian ponsel indeks 0 justru kamera
	 * depan). Bila label tak membantu, jatuh ke facingMode: dicoba "exact"
	 * dulu (memaksa sisi kamera yang benar di ponsel), lalu "ideal" sebagai
	 * jaring pengaman untuk perangkat berkamera tunggal (mis. laptop).
	 */
	async #openStream() {
		const wantFront = this.#select?.value === 'front';
		const size = { width: { ideal: 1280 }, height: { ideal: 720 } };
		const facing = wantFront ? 'user' : 'environment';

		// (1) Cocokkan label perangkat, mis. "camera2 0, facing back".
		const rx = wantFront ? /front|depan|user|selfie/i : /back|belakang|rear|environment/i;
		const match = this.#videoDevices.find((device) => rx.test(device.label));
		if (match?.deviceId) {
			try {
				return await navigator.mediaDevices.getUserMedia({
					audio: false,
					video: { deviceId: { exact: match.deviceId }, ...size }
				});
			} catch (_) { /* jatuh ke facingMode */ }
		}

		// (2) facingMode "exact" — paling tegas memilih sisi kamera di ponsel.
		try {
			return await navigator.mediaDevices.getUserMedia({
				audio: false,
				video: { facingMode: { exact: facing }, ...size }
			});
		} catch (_) { /* jatuh ke fallback longgar */ }

		// (3) Fallback longgar untuk perangkat berkamera tunggal.
		return await navigator.mediaDevices.getUserMedia({
			audio: false,
			video: { facingMode: { ideal: facing }, ...size }
		});
	}

	// Selesai ketika metadata frame pertama sudah tersedia.
	#awaitFirstFrame() {
		return new Promise((resolve) => {
			if (this.video.readyState >= 2) {
				resolve();
				return;
			}
			this.video.addEventListener('loadedmetadata', () => resolve(), { once: true });
		});
	}

	async startCamera() {
		try {
			if (this.#stream) this.stopCamera();

			this.#stream = await this.#openStream();
			if (!this.video) throw new Error('Elemen <video> tidak ditemukan.');

			this.video.srcObject = this.#stream;
			await this.#awaitFirstFrame();
			await this.video.play();
		} catch (error) {
			logError('Gagal memulai kamera', error);
			const errorMessage = getCameraErrorMessage(error);
			throw new Error(errorMessage);
		}
	}

	stopCamera() {
		this.#stream?.getTracks().forEach((track) => track.stop());
		this.#stream = null;
		if (this.video) this.video.srcObject = null;
	}

	setFPS(fps) {
		// [Skilled] Pembatasan FPS tidak diaktifkan pada jalur Basic.
	}

	isActive() {
		if (!this.#stream) return false;
		return this.#stream.getVideoTracks().some((track) => track.readyState === 'live');
	}

	isReady() {
		return this.isActive() && !!this.video && this.video.readyState >= 2;
	}
}

export default CameraService;
