import { logError, validateModelMetadata } from '../core/utils.js';

/**
 * DetectionService — "Si Mata".
 * Memuat model Teachable Machine (TensorFlow.js) lalu memetakan frame kamera
 * menjadi satu label sayuran dengan skor kepercayaannya.
 */
class DetectionService {
	constructor() {
		this.model = null;
		this.labels = [];
		this.config = null;

		// Lokasi berkas model relatif terhadap index.html.
		this.paths = {
			graph: './model/model.json',
			meta: './model/metadata.json'
		};
		this.inputSize = 224; // default; ditimpa oleh metadata bila ada.
	}

	async loadModel() {
		try {
			if (typeof tf === 'undefined') {
				throw new Error('Script TensorFlow.js belum termuat di halaman.');
			}
			await tf.ready();

			// 1) Ambil metadata untuk daftar label + ukuran input.
			const response = await fetch(this.paths.meta);
			if (!response.ok) {
				throw new Error(`Metadata tidak terbaca (HTTP ${response.status}).`);
			}
			const meta = await response.json();
			if (!validateModelMetadata(meta)) {
				throw new Error('Struktur metadata model tidak sesuai.');
			}
			this.labels = [...meta.labels];
			this.inputSize = Number(meta.imageSize) || this.inputSize;

			// 2) Muat graf model.
			this.model = await tf.loadLayersModel(this.paths.graph);
		} catch (error) {
			logError('Failed to load model', error);
			throw new Error(`Failed to load model: ${error.message}`);
		}
	}

	/**
	 * Ubah elemen gambar menjadi tensor batch ternormalisasi ke rentang [-1, 1].
	 * Dipisah agar alur predict() lebih ringkas dan mudah dibaca.
	 */
	toInputTensor(imageElement) {
		return tf.tidy(() =>
			tf.browser
				.fromPixels(imageElement)
				.resizeBilinear([this.inputSize, this.inputSize])
				.toFloat()
				.mul(1 / 127.5)
				.sub(1)
				.expandDims(0)
		);
	}

	async predict(imageElement) {
		let inputTensor = null;
		let outputTensor = null;
		try {
			if (!this.isLoaded()) throw new Error('Model belum siap dipakai.');
			if (!imageElement) throw new Error('Sumber gambar kosong.');

			inputTensor = this.toInputTensor(imageElement);
			outputTensor = this.model.predict(inputTensor);

			const scores = Array.from(await outputTensor.data());
			const topIndex = scores.indexOf(Math.max(...scores));

			return {
				className: this.labels[topIndex] ?? 'Unknown',
				confidence: Math.round(scores[topIndex] * 100),
				isValid: true
			};
		} catch (error) {
			logError('Prediction error', error);
			throw new Error(`Prediksi gagal: ${error.message}`);
		} finally {
			inputTensor?.dispose();
			outputTensor?.dispose();
		}
	}

	isLoaded() {
		return Boolean(this.model) && this.labels.length > 0;
	}
}

export default DetectionService;
