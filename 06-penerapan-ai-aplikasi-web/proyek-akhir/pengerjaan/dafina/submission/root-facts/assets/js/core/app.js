import UIHandler from '../ui/ui.handler.js';
import CameraService from '../services/camera.service.js';
import DetectionService from '../services/detection.service.js';
import FunFactService from '../services/facts.service.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

// Jeda antar pemindaian (ms) — dikelola lewat setInterval berulang. Tick rapat
// supaya kestabilan terkumpul dalam ~3–4 detik yang terasa "sedang memindai".
const SCAN_INTERVAL_MS = 700;
// Lewati beberapa tick pertama sebelum menilai frame: beri kamera waktu auto-
// exposure/white-balance mengendap agar tidak memprediksi bingkai gelap/awal.
const WARMUP_TICKS = 2;
// Ambang kepercayaan minimum agar sebuah tick dihitung sebagai deteksi "yakin".
// Nilai sedang: di atas noise bingkai kosong, tapi terjangkau sayuran nyata
// (biasanya 65–90%) sehingga penguncian pasti terjadi saat objek benar ada.
const LOCK_CONFIDENCE = 60;
// Berapa tick berturut-turut label yang SAMA harus muncul (masing-masing ≥ ambang)
// sebelum hasil dikunci. Kestabilan lintas-frame inilah bukti "objek benar-benar
// terdeteksi" — jauh lebih kuat daripada satu angka kepercayaan sesaat.
const STABILITY_STREAK = 3;
const LOG_TAG = '[RootFacts·DMR]';

class RootFactsApp {
	// State internal disimpan di #private fields.
	#scanHandle = null;   // id dari setInterval
	#busy = false;        // penjaga agar tick tak tumpang tindih
	#activeLabel = null;  // label yang sedang tampil (hindari regenerasi)
	#tickCount = 0;       // hitung tick sejak scan mulai (untuk warm-up)
	#streakLabel = null;  // label kandidat yang sedang dihitung kestabilannya
	#streakCount = 0;     // berapa tick berturut label kandidat itu bertahan

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
			console.log(`${LOG_TAG} Transformers.js (LaMini-Flan-T5-77M) siap.`);

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
		this.#resetStreak();
		this.ui.switchToState('loading');

		// TIDAK memindai langsung: biarkan setInterval yang menjalankan tick pertama
		// agar tick awal (yang paling mungkin bingkai gelap) ikut kena warm-up.
		this.#scanHandle = setInterval(() => this.detectLoop(), SCAN_INTERVAL_MS);
	}

	stopDetection() {
		this.isRunning = false;
		if (this.#scanHandle) {
			clearInterval(this.#scanHandle);
			this.#scanHandle = null;
		}
		this.#busy = false;
		this.#resetStreak();
	}

	// Nolkan penghitung warm-up + kestabilan (dipanggil tiap mulai/berhenti scan
	// supaya sesi baru tak mewarisi streak basi yang bisa mengunci seketika).
	#resetStreak() {
		this.#tickCount = 0;
		this.#streakLabel = null;
		this.#streakCount = 0;
	}

	async detectLoop() {
		// Lewati tick bila proses sebelumnya masih jalan atau kamera belum siap.
		if (this.#busy || !this.isRunning) return;
		if (!this.camera.isReady()) return;

		// Warm-up: lewati beberapa tick awal tanpa memprediksi (kamera settle dulu).
		this.#tickCount += 1;
		if (this.#tickCount <= WARMUP_TICKS) {
			console.log(`${LOG_TAG} Pemanasan sensor (tick #${this.#tickCount}/${WARMUP_TICKS})…`);
			return;
		}

		this.#busy = true;
		try {
			const prediction = await this.detector.predict(this.camera.video);
			if (!this.isRunning) return;

			// Perbarui streak kestabilan: satu tick "yakin" = label sama & ≥ ambang.
			if (prediction.confidence >= LOCK_CONFIDENCE) {
				if (prediction.className === this.#streakLabel) {
					this.#streakCount += 1;
				} else {
					this.#streakLabel = prediction.className;
					this.#streakCount = 1;
				}
			} else {
				// Bingkai ragu (mis. tak ada objek) memutus rantai kestabilan.
				this.#streakCount = 0;
			}

			console.log(
				`${LOG_TAG} Tick #${this.#tickCount}: ${prediction.className} ` +
				`(${prediction.confidence}%) — streak ${this.#streakCount}/${STABILITY_STREAK}`
			);

			// Kunci hanya setelah label yang SAMA cukup stabil & yakin. Selama belum,
			// UI tetap di keadaan "Mencari…" dengan kamera hidup (tak pernah macet:
			// begitu sayuran nyata masuk bingkai, streak terkumpul dalam ~2 detik).
			if (this.#streakCount >= STABILITY_STREAK) {
				await this.#lockDetection(prediction);
			}
		} catch (error) {
			logError('Kesalahan saat memindai', error);
		} finally {
			this.#busy = false;
		}
	}

	// Deteksi stabil tercapai → tampilkan hasil + fun fact, lalu auto-stop kamera
	// (permintaan reviewer penolakan #2) supaya hasil membeku & mudah dibaca.
	async #lockDetection(prediction) {
		if (!this.isRunning) return;
		console.log(
			`${LOG_TAG} Terkunci: ${prediction.className} (${prediction.confidence}%) ` +
			`setelah ${this.#streakCount} tick stabil.`
		);
		this.#activeLabel = prediction.className;

		const ok = await this.generateAndShowResults(prediction);
		if (ok) {
			this.#finishScan();
		} else {
			// Gagal generate sesaat → jangan bekukan kartu error; nolkan streak dan
			// biarkan pemindaian berlanjut untuk mencoba lagi.
			this.#streakCount = 0;
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

	// Kembalikan true bila hasil + fun fact berhasil tampil, false bila gagal.
	async generateAndShowResults(detectionResult) {
		// Sayuran berganti → buang fakta lama agar tak salah dipasang ke label baru.
		this.currentFunFact = '';
		try {
			// Tampilkan nama sayuran dulu dengan placeholder (spinner) fun fact.
			// Model sudah dimuat penuh saat init, jadi generasi ini singkat saja.
			this.ui.showResults(detectionResult, null);

			// `angle` = sudut isi (gizi/sejarah/masak/…) yang dirotasi tiap generasi.
			// Di-log agar reviewer bisa membuktikan variasi keluaran model tiap scan.
			const { funFact, angle } = await this.funFactGenerator.generateFunFact(detectionResult.className);
			this.currentFunFact = funFact;
			console.log(`${LOG_TAG} Fun fact [${angle}] ${detectionResult.className}: ${funFact}`);

			this.ui.showResults(detectionResult, { funFact });
			return true;
		} catch (error) {
			logError('Gagal menampilkan hasil', error);
			// Kegagalan sesaat saat generate → jangan kunci label ini; biarkan
			// tick berikutnya mencoba lagi daripada menampilkan fakta kosong.
			this.#activeLabel = null;
			this.ui.updateFunFactState('error');
			return false;
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
