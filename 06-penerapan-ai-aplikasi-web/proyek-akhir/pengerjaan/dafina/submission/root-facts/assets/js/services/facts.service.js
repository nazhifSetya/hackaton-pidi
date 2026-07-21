import { logError } from '../core/utils.js';

/*
 * FunFactService — penghasil fun fact berbasis model bahasa untuk RootFacts.
 * Menjalankan model lokal ringan di peramban via Transformers.js (seq2seq,
 * pipeline 'text2text-generation', varian q8).
 *
 * Model = LaMini-Flan-T5-77M (~90 MB). Dipilih agar unduhan ke peramban jauh lebih
 * kecil dibanding flan-t5-base (yang membengkak ~600 MB di Cache Storage) namun tetap
 * instruction-tuned sehingga bisa menghasilkan kalimat.
 *
 * Fun fact BENAR-BENAR DIHASILKAN model: tiap sayuran hanya diberi HINT kata-kunci
 * singkat (VEG_HINTS) sebagai konteks di dalam prompt — bukan kalimat jadi yang tinggal
 * disalin — lalu model MENYUSUN sendiri kalimat fun fact-nya. Tidak ada mekanisme yang
 * mengganti keluaran model dengan teks yang sudah ditulis; yang tampil ke pengguna
 * selalu keluaran model. Decoding greedy = deterministik per sayuran.
 */

const HF_LIB = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const LLM_ID = 'Xenova/LaMini-Flan-T5-77M';
const LLM_TASK = 'text2text-generation';
const LABEL_MAX = 32;

// HINT kata-kunci per label (18 sayuran) — SENGAJA berupa frasa/kata kunci singkat,
// BUKAN kalimat fun fact utuh. Ini dipakai sebagai konteks di prompt supaya model
// menyusun sendiri kalimatnya (keluaran genuine, bukan salinan). Tiap hint diawali
// jenis sayuran (root/leafy/bulb/…) untuk meng-anchor model agar tetap relevan.
const VEG_HINTS = {
	beetroot: 'deep red root, once used as a natural dye and even lipstick in the 1800s',
	paprika: 'red spice ground from dried peppers, the national spice of Hungary',
	cabbage: 'leafy vegetable, the biggest one ever weighed over 62 kilograms',
	carrot: 'root vegetable, purple long ago before orange ones came from the Netherlands',
	cauliflower: 'vegetable that also grows in purple, orange and green, not only white',
	chilli: 'spicy pepper, its burning heat comes from a compound called capsaicin',
	corn: 'grain vegetable, always an even number of rows, about 800 kernels a cob',
	cucumber: 'green vegetable made almost entirely of water',
	eggplant: 'purple vegetable, named after early white types shaped like eggs',
	garlic: 'strong-smelling bulb, fed to ancient Egyptian pyramid workers for strength',
	ginger: 'spicy underground stem, used as medicine for over 5000 years',
	lettuce: 'leafy green, treated as a sacred plant by the ancient Egyptians',
	onion: 'bulb that makes you cry because it releases an eye-stinging gas',
	peas: 'small green seeds, one of the oldest crops, over 9000 years old',
	potato: 'starchy vegetable, the first ever grown in space back in 1995',
	turnip: 'root vegetable, once carved into lanterns for Halloween in Ireland',
	soybean: 'legume bean, made into tofu, soy milk and even crayons and ink',
	spinach: 'leafy green, wrongly believed to be very high in iron, which inspired Popeye'
};

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

	// Cari hint kata-kunci untuk sebuah label (kunci huruf kecil, tahan bentuk jamak
	// sederhana mis. "Carrots" -> "carrot"). null bila di luar 18 label.
	#lookupHint(name) {
		const key = name.toLowerCase();
		return VEG_HINTS[key] || VEG_HINTS[key.replace(/s$/, '')] || null;
	}

	// Prompt utama: model MENYUSUN satu kalimat fun fact dengan hint kata-kunci
	// sebagai konteks (bukan disalin) — model yang menulis kalimatnya sendiri.
	#buildPrompt(name, hint) {
		return `Write one interesting fun fact sentence about the ${name}, using these keywords: ${hint}.`;
	}

	// Prompt cadangan (dipakai bila keluaran pertama melenceng dari sayurannya).
	// Tetap keluaran model — hanya membingkai hint dari sudut berbeda, bukan teks jadi.
	#altPrompt(name, hint) {
		return `${hint}. Turn this into one fun fact about the ${name}.`;
	}

	// Rapikan keluaran MODEL (buang sisa label prompt, kapital, akhiri titik).
	// TIDAK ada penggantian ke kalimat siap pakai — yang tampil selalu keluaran model.
	// Hanya bila keluaran benar-benar kosong dipakai pembuka generik netral.
	#tidyFact(raw, name) {
		let text = (raw || '')
			.replace(/^\s*(fun fact:?|keywords?:.*|answer:?)\s*/i, '')
			.replace(/\s+/g, ' ')
			.trim();
		if (!text) {
			text = `Here is a fun fact: the ${name} is more interesting than it looks`;
		}
		text = text.charAt(0).toUpperCase() + text.slice(1);
		if (!/[.!?]$/.test(text)) text += '.';
		return text;
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
			// Hint kata-kunci dijadikan konteks; MODEL yang menyusun kalimat fun fact
			// (bukan menyalin). Kalau keluaran pertama melenceng (tak menyebut nama
			// sayurannya), dicoba sekali lagi dengan prompt cadangan — tetap keluaran
			// model, bukan teks siap pakai. Greedy = deterministik per sayuran.
			const hint = this.#lookupHint(name);
			const params = {
				max_new_tokens: 70,
				min_new_tokens: 16,
				do_sample: false,
				repetition_penalty: 1.3,
				no_repeat_ngram_size: 3
			};

			const prompt = hint
				? this.#buildPrompt(name, hint)
				: `Write one interesting and surprising fun fact about the vegetable ${name}.`;
			let funFact = this.#tidyFact(this.#extractText(await this.generator(prompt, params)), name);

			const stem = name.replace(/s$/i, '');
			const mentionsVeg = (t) => new RegExp(`\\b${stem}`, 'i').test(t);
			if (hint && !mentionsVeg(funFact)) {
				const retry = this.#tidyFact(
					this.#extractText(await this.generator(this.#altPrompt(name, hint), params)), name);
				if (mentionsVeg(retry)) funFact = retry;
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
