import { logError } from '../core/utils.js';

class FunFactService {
	constructor() {
		this.generator = null;
		this.isModelLoaded = false;
		this.isGenerating = false;
		this.config = null;
		this.currentBackend = null;
	}

	// TODO [Basic] Implementasikan metode untuk memuat model Transformers.js
	// TODO [Advance] Gunakan strategi Backend Adaptive seperti yang telah dipelajari sebelumnya
	async loadModel() {
		try { } catch (error) {
			logError('Error loading Transformers.js model', error);
			throw new Error(`Failed to load FunFact model: ${error.message}`);
		}
	}

	// TODO [Basic] Implementasikan metode untuk menghasilkan fun fact tentang sayuran
	// TODO [Basic] Tambahkan validasi untuk maksimum panjang input dan pembersihan input terhadap karakter khusus untuk mengatasi prompt injection
	// TODO [Advanced] Gunakan parameter `tone` untuk variasi personalitas
	async generateFunFact(vegetable, tone = 'normal') {
		if (!this.isModelLoaded || this.isGenerating) {
			throw new Error('Model belum siap atau sedang menghasilkan fakta');
		}

		if (!vegetable || typeof vegetable !== 'string') {
			throw new Error('Nama sayuran yang valid diperlukan');
		}

		try { } catch (error) {
			logError('Error generating fun fact', error);
			throw new Error(`Failed to generate fun fact: ${error.message}`);
		} finally {
			this.isGenerating = false;
		}
	}

	// TODO [Basic] Periksa apakah model siap dan tidak sedang menghasilkan fakta
	isReady() {}
}

export default FunFactService;
