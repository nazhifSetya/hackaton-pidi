import { logError } from '../core/utils.js';

/*
 * FunFactService — penghasil fun fact berbasis model bahasa untuk RootFacts.
 * Menjalankan FLAN-T5-base lokal di peramban via Transformers.js. Model ini
 * encoder-decoder (seq2seq), jadi dijalankan lewat pipeline
 * 'text2text-generation': satu prompt masuk, satu kalimat keluar. Keluaran
 * diambil dengan decoding greedy agar tetap fokus pada sayuran; varian q8
 * menekan ukuran unduhan agar wajar dijalankan di perangkat pengguna.
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

	/*
	 * Muat pipeline. `onProgress(percent)` dipanggil selama pengunduhan berkas
	 * model dari Hub sehingga pemanggil bisa menampilkan persentase ke pengguna.
	 * Persen dihitung dari total byte terunduh / total byte semua berkas.
	 */
	async loadModel(onProgress) {
		try {
			const lib = await import(HF_LIB);
			// Nonaktifkan pencarian berkas lokal supaya model diunduh dari Hub.
			lib.env.allowLocalModels = false;

			const files = new Map();
			const track = (event) => {
				if (event.status !== 'progress' || !event.file) return;
				files.set(event.file, { loaded: event.loaded || 0, total: event.total || 0 });
				let loaded = 0;
				let total = 0;
				for (const f of files.values()) {
					loaded += f.loaded;
					total += f.total;
				}
				// Batasi ke 99% selama mengunduh; 100% baru setelah pipeline siap.
				if (total > 0 && typeof onProgress === 'function') {
					onProgress(Math.min(99, Math.round((loaded / total) * 100)));
				}
			};

			this.generator = await lib.pipeline(LLM_TASK, LLM_ID, { dtype: 'q8', progress_callback: track });
			this.currentBackend = 'wasm';
			this.isModelLoaded = true;
			if (typeof onProgress === 'function') onProgress(100);
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
			// FLAN-T5-base menjawab paling relevan ketika sayuran dibingkai sebagai
			// "the vegetable <nama>". Decoding dipakai greedy (do_sample:false)
			// karena sampling pada model sekecil ini cenderung mengarang; greedy
			// membuat keluaran lebih fokus & masuk akal. Deterministik per sayuran,
			// namun tetap unik antar sayuran (bukan teks statis yang sama semua).
			const prompt = `Tell me an interesting fun fact about the vegetable ${name}.`;

			const output = await this.generator(prompt, {
				max_new_tokens: 60,
				do_sample: false,
				repetition_penalty: 1.4,
				no_repeat_ngram_size: 3
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
