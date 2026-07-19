import { logError } from '../core/utils.js';

/*
 * FunFactService — penghasil fun fact berbasis model bahasa untuk RootFacts.
 * Menjalankan FLAN-T5-base lokal di peramban via Transformers.js. Model ini
 * encoder-decoder (seq2seq), jadi dijalankan lewat pipeline
 * 'text2text-generation': satu prompt masuk, satu kalimat keluar. FLAN-T5
 * merespons baik pada instruksi format tanya-jawab; varian q8 menekan ukuran
 * unduhan agar wajar dijalankan di perangkat pengguna.
 */

const HF_LIB = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const LLM_ID = 'Xenova/flan-t5-base';
const LLM_TASK = 'text2text-generation';
const LABEL_MAX = 32;

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
			const lib = await import(HF_LIB);
			// Nonaktifkan pencarian berkas lokal supaya model diunduh dari Hub.
			lib.env.allowLocalModels = false;

			this.generator = await lib.pipeline(LLM_TASK, LLM_ID, { dtype: 'q8' });
			this.currentBackend = 'wasm';
			this.isModelLoaded = true;
		} catch (error) {
			logError('Error loading Transformers.js model', error);
			throw new Error(`Failed to load FunFact model: ${error.message}`);
		}
	}

	/*
	 * Rapikan nama sayuran sebelum dimasukkan ke prompt (mitigasi prompt
	 * injection): normalisasi NFKC, izinkan hanya huruf/angka/spasi (Unicode),
	 * padatkan spasi, potong panjang, lalu jadikan Title Case.
	 */
	#cleanLabel(raw) {
		const base = raw
			.normalize('NFKC')
			.replace(/[^\p{L}\p{N}\s]/gu, ' ')
			.replace(/\s+/g, ' ')
			.trim()
			.slice(0, LABEL_MAX);
		return base.replace(/\b\p{L}/gu, (ch) => ch.toUpperCase());
	}

	// Ambil teks jawaban dari keluaran pipeline.
	// text2text -> { generated_text: 'kalimat' }; tetap tahan bila berupa array pesan.
	#extractText(output) {
		const first = Array.isArray(output) ? output[0] : output;
		const generated = first?.generated_text;
		if (Array.isArray(generated)) {
			return (generated.at(-1)?.content ?? '').trim();
		}
		return (typeof generated === 'string' ? generated : '').trim();
	}

	async generateFunFact(vegetable, tone = 'normal') {
		if (!this.isModelLoaded || this.isGenerating) {
			throw new Error('Model belum siap atau sedang menghasilkan fakta');
		}

		if (!vegetable || typeof vegetable !== 'string') {
			throw new Error('Nama sayuran yang valid diperlukan');
		}

		const name = this.#cleanLabel(vegetable);
		if (!name) {
			throw new Error('Nama sayuran kosong setelah dibersihkan');
		}

		this.isGenerating = true;
		try {
			// Disusun sebagai pasangan Question/Answer karena FLAN-T5 paling patuh
			// pada pola itu. Nama muncul di pertanyaan sekaligus di instruksi
			// jawaban supaya keluaran tidak melenceng ke sayuran lain.
			const prompt =
				`Question: What is one surprising and true fun fact about ${name}, a vegetable? ` +
				`Answer with one full sentence that mentions ${name}.`;

			const output = await this.generator(prompt, {
				max_new_tokens: 70,
				temperature: 0.7,
				top_p: 0.95,
				do_sample: true,
				repetition_penalty: 1.3
			});

			let funFact = this.#extractText(output);
			if (!funFact) {
				funFact = `${name} is a nutritious vegetable worth adding to your plate.`;
			}

			return { vegetable: name, funFact, tone };
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
