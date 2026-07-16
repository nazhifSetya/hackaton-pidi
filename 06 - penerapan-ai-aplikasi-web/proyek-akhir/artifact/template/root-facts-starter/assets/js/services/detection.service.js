import { logError } from '../core/utils.js';

class DetectionService {
	constructor() {
		this.model = null;
		this.labels = [];
		this.config = null;
	}

	// TODO [Basic] Implementasikan metode untuk memuat model TensorFlow.js
	// TODO [Basic] Gunakan validateModelMetadata() untuk memeriksa metadata model
	// TODO [Advance] Gunakan strategi Backend Adaptive seperti yang telah dipelajari sebelumnya
	async loadModel() {
		try { } catch (error) {
			logError('Failed to load model', error);
			throw new Error(`Failed to load model: ${error.message}`);
		}
	}

	// TODO [Basic] Implementasikan metode untuk melakukan prediksi pada elemen gambar
	async predict(imageElement) {
		try { } catch (error) {
			logError('Prediction error', error);
			throw new Error(`Prediksi gagal: ${error.message}`);
		} finally {
			// TODO [Basic] Dispose tensor dan predictions untuk menghindari memory leak
		}
	}

	// TODO [Basic] Periksa apakah model sudah dimuat
	isLoaded() {}
}

export default DetectionService;
