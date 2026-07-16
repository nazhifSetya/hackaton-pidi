import { logError } from '../core/utils.js';

/**
 * FunFactService — "Si Otak".
 * Memakai Transformers.js untuk menjalankan model bahasa kecil secara lokal
 * di peramban. Model yang dipilih adalah LaMini-Flan-T5 (seq2seq / text2text)
 * sehingga jawabannya langsung berupa kalimat, tanpa perlu template chat.
 */

const LIBRARY_URL = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const MODEL_NAME = 'Xenova/LaMini-Flan-T5-248M';
const TASK = 'text2text-generation';
const MAX_LABEL_CHARS = 40;

class FunFactService {
	constructor() {
		this.generator = null;
		this.isModelLoaded = false;
		this.isGenerating = false;
		this.config = null;
		this.currentBackend = null;
	}

	async loadModel() {
		try {
			const transformers = await import(LIBRARY_URL);
			// Ambil model dari Hub, bukan dari berkas lokal.
			transformers.env.allowLocalModels = false;

			this.generator = await transformers.pipeline(TASK, MODEL_NAME, { dtype: 'q8' });
			this.currentBackend = 'wasm';
			this.isModelLoaded = true;
		} catch (error) {
			logError('Error loading Transformers.js model', error);
			throw new Error(`Failed to load FunFact model: ${error.message}`);
		}
	}

	/**
	 * Bersihkan nama sayuran agar aman dijadikan bagian prompt.
	 * Hanya izinkan huruf/spasi, rapikan spasi ganda, batasi panjang.
	 */
	sanitizeLabel(raw) {
		return raw
			.normalize('NFKD')
			.replace(/[^a-zA-Z\s]/g, ' ')
			.replace(/\s+/g, ' ')
			.trim()
			.slice(0, MAX_LABEL_CHARS)
			.toLowerCase();
	}

	async generateFunFact(vegetable, tone = 'normal') {
		if (!this.isModelLoaded || this.isGenerating) {
			throw new Error('Model belum siap atau sedang menghasilkan fakta');
		}

		if (!vegetable || typeof vegetable !== 'string') {
			throw new Error('Nama sayuran yang valid diperlukan');
		}

		const label = this.sanitizeLabel(vegetable);
		if (!label) {
			throw new Error('Nama sayuran tidak valid setelah dibersihkan');
		}

		this.isGenerating = true;
		try {
			// Prompt bahasa Inggris (sesuai anjuran modul) sebagai satu instruksi.
			// Menyebut ulang label mendorong model kecil tetap fokus pada sayuran itu.
			const prompt =
				`Write one short and interesting fun fact about the vegetable ${label}. ` +
				`Mention ${label} in the answer.`;

			const output = await this.generator(prompt, {
				max_new_tokens: 90,
				temperature: 0.5,
				top_p: 0.9,
				do_sample: true,
				repetition_penalty: 1.2
			});

			let funFact = (output?.[0]?.generated_text ?? '').trim();
			if (!funFact) {
				funFact = `Did you know? The ${label} is a vegetable enjoyed in kitchens all over the world.`;
			}

			return { vegetable: label, funFact, tone };
		} catch (error) {
			logError('Error generating fun fact', error);
			throw new Error(`Failed to generate fun fact: ${error.message}`);
		} finally {
			this.isGenerating = false;
		}
	}

	isReady() {
		return this.isModelLoaded && !this.isGenerating;
	}
}

export default FunFactService;
