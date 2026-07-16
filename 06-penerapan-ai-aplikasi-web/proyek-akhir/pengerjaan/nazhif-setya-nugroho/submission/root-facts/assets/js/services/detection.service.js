import { logError, validateModelMetadata } from '../core/utils.js';

const MODEL_URL = './model/model.json';
const METADATA_URL = './model/metadata.json';

class DetectionService {
	constructor() {
		this.model = null;
		this.labels = [];
		this.imageSize = 224;
		this.config = null;
	}

	async loadModel() {
		try {
			if (typeof tf === 'undefined') {
				throw new Error('TensorFlow.js belum dimuat. Pastikan script tf.min.js di-load di index.html.');
			}
			await tf.ready();

			const metadataResp = await fetch(METADATA_URL);
			if (!metadataResp.ok) throw new Error(`Gagal fetch metadata: ${metadataResp.status}`);
			const metadata = await metadataResp.json();
			if (!validateModelMetadata(metadata)) {
				throw new Error('Metadata model tidak valid (labels missing).');
			}
			this.labels = metadata.labels;
			this.imageSize = metadata.imageSize || 224;

			this.model = await tf.loadLayersModel(MODEL_URL);
		} catch (error) {
			logError('Failed to load model', error);
			throw new Error(`Failed to load model: ${error.message}`);
		}
	}

	async predict(imageElement) {
		let input = null;
		let predictions = null;
		try {
			if (!this.isLoaded()) throw new Error('Model belum dimuat');
			if (!imageElement) throw new Error('Elemen gambar tidak diberikan');

			input = tf.tidy(() => {
				return tf.browser.fromPixels(imageElement)
					.resizeNearestNeighbor([this.imageSize, this.imageSize])
					.toFloat()
					.div(127.5)
					.sub(1)
					.expandDims(0);
			});

			predictions = this.model.predict(input);
			const probs = await predictions.data();

			let bestIndex = 0;
			let bestProb = probs[0];
			for (let i = 1; i < probs.length; i += 1) {
				if (probs[i] > bestProb) {
					bestProb = probs[i];
					bestIndex = i;
				}
			}

			return {
				className: this.labels[bestIndex] || 'Unknown',
				confidence: Math.round(bestProb * 100),
				isValid: true
			};
		} catch (error) {
			logError('Prediction error', error);
			throw new Error(`Prediksi gagal: ${error.message}`);
		} finally {
			if (input) input.dispose();
			if (predictions) predictions.dispose();
		}
	}

	isLoaded() {
		return this.model !== null && this.labels.length > 0;
	}
}

export default DetectionService;
