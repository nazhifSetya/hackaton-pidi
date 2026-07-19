import { logError, validateModelMetadata } from '../core/utils.js';

/*
 * DetectionService — modul penglihatan ("Si Mata") untuk RootFacts.
 * Membungkus model Teachable Machine (TensorFlow.js Layers) dan mengubah
 * satu frame kamera menjadi { className, confidence } sayuran teratas.
 *
 * Catatan gaya: state disimpan pada #private class fields agar tidak bocor
 * keluar objek, dan preprocessing dilakukan lewat kanvas luar-layar
 * (drawImage sekaligus me-resize) sebelum dibaca menjadi tensor.
 */

const GRAPH_URL = './model/model.json';
const META_URL = './model/metadata.json';
const DEFAULT_INPUT = 224;

class DetectionService {
	#model = null;
	#labels = [];
	#inputSize = DEFAULT_INPUT;
	#frameCanvas = null;
	#frameCtx = null;

	constructor() {
		// Dibiarkan minimal: seluruh state nyata ada di #private fields.
		this.config = null;
	}

	// Label dibaca lapisan aplikasi hanya lewat getter ini (salinan, read-only).
	get labelList() {
		return [...this.#labels];
	}

	async loadModel() {
		try {
			if (typeof tf === 'undefined') {
				throw new Error('Pustaka TensorFlow.js belum tersedia pada halaman.');
			}
			await tf.ready();

			// (1) Baca metadata: daftar label + ukuran input jaringan.
			const meta = await this.#fetchMetadata();
			this.#labels = Array.from(meta.labels);
			this.#inputSize = Number.isFinite(meta.imageSize) ? meta.imageSize : DEFAULT_INPUT;

			// (2) Muat bobot model Layers.
			this.#model = await tf.loadLayersModel(GRAPH_URL);
		} catch (error) {
			logError('Failed to load model', error);
			throw new Error(`Failed to load model: ${error.message}`);
		}
	}

	async #fetchMetadata() {
		const res = await fetch(META_URL);
		if (!res.ok) {
			throw new Error(`Metadata model gagal diunduh (status ${res.status}).`);
		}
		const meta = await res.json();
		if (!validateModelMetadata(meta)) {
			throw new Error('Format metadata model tidak dikenali.');
		}
		return meta;
	}

	/*
	 * Salin frame ke kanvas berukuran tetap (resize implisit via drawImage),
	 * lalu ubah menjadi tensor batch ternormalisasi ke rentang [-1, 1]:
	 *   x/255 -> [0,1], *2 -> [0,2], -1 -> [-1,1].
	 */
	#toTensor(source) {
		const size = this.#inputSize;
		if (!this.#frameCanvas) {
			this.#frameCanvas = document.createElement('canvas');
			this.#frameCanvas.width = size;
			this.#frameCanvas.height = size;
			this.#frameCtx = this.#frameCanvas.getContext('2d', { willReadFrequently: true });
		}
		this.#frameCtx.drawImage(source, 0, 0, size, size);

		return tf.tidy(() =>
			tf.browser
				.fromPixels(this.#frameCanvas)
				.toFloat()
				.div(255)
				.mul(2)
				.sub(1)
				.expandDims(0)
		);
	}

	async predict(imageElement) {
		let input = null;
		try {
			if (!this.isLoaded()) throw new Error('Model deteksi belum dimuat.');
			if (!imageElement) throw new Error('Frame kamera tidak tersedia.');

			input = this.#toTensor(imageElement);

			// Argmax dihitung sebagai operasi tensor (backend WebGL/CPU),
			// bukan perulangan JavaScript, lalu dibaca sekali ke angka biasa.
			const { index, score } = tf.tidy(() => {
				const probs = this.#model.predict(input);
				return {
					index: probs.argMax(-1).dataSync()[0],
					score: probs.max(-1).dataSync()[0]
				};
			});

			return {
				className: this.#labels[index] ?? 'Unknown',
				confidence: Math.round(score * 100),
				isValid: true
			};
		} catch (error) {
			logError('Prediction error', error);
			throw new Error(`Prediksi gagal: ${error.message}`);
		} finally {
			// Dispose tensor input agar tidak menumpuk di memori peramban.
			input?.dispose();
		}
	}

	isLoaded() {
		return this.#model !== null && this.#labels.length > 0;
	}
}

export default DetectionService;
