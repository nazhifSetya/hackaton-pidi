import UIHandler from '../ui/ui.handler.js';
import { APP_CONFIG } from './config.js';
import { logError } from './utils.js';

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

		// TODO [Advanced] Tambahkan properti untuk tone yang dipilih

		this.ui.disableButton();

		this.bindEvents();
		this.init();
		// TODO [Basic] Panggil registerServiceWorker()
	}

	// TODO [Basic] Bind toggle camera event dengan nama onToggleCamera
	// TODO [Basic] Bind camera change event dengan nama onCameraChange
	// TODO [Skilled] Bind FPS change event dengan nama onFPSChange
	// TODO [Skilled] Bind copy fun fact event dengan nama onCopy
	// TODO [Advanced] Bind tone change event dengan nama onToneChange
	bindEvents() {
		this.ui.bindEvents({});
	}
	
	// TODO [Skilled] Perbarui status header UI menjadi 'Memuat model...' saat memulai inisialisasi
	// TODO [Basic] Lengkapi inisialisasi kemampuan aplikasi
	// TODO [Skilled] Perbarui status header UI menjadi 'Siap'
	async init() {
		try { } catch (error) {
			logError('Gagal menginisialisasi aplikasi', error);
			// TODO [Skilled] Perbarui status header UI menjadi 'Error' jika inisialisasi gagal
			this.ui.updateHeaderStatus('Error', false);
			this.ui.showError(`Gagal menginisialisasi: ${error.message}`);
			this.ui.disableButton();
		}
	}


	// TODO [Basic] Buatlah berkas sw.js di root project dan konfigurasikan precaching di dalamnya menggunakan Workbox
	// TODO [Basic] Registrasikan Service Worker
	// TODO [Skilled] Buatlah metode untuk menyalin fun fact ke clipboard

	// TODO [Basic] Implementasikan metode untuk mengaktifkan atau menonaktifkan kamera
	toggleCamera() {}

	// TODO [Basic] Implementasikan metode untuk memulai kamera
	async startCamera() {}

	// TODO [Basic] Implementasikan metode untuk menghentikan kamera
	stopCamera() {}

	// TODO [Basic] Implementasikan metode untuk memulai deteksi
	startDetection() {}

	// TODO [Basic] Implementasikan metode untuk menghentikan deteksi
	stopDetection() {}

	// TODO [Basic] Implementasikan metode deteksi utama
	async detectLoop(loopId) {}

	// TODO [Basic] Implementasikan metode untuk menghasilkan dan menampilkan fun fact
	async generateAndShowResults(detectionResult) {
		try { } catch (error) {
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
