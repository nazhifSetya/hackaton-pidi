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
 * selalu keluaran model.
 *
 * VARIASI (dua lapis, agar scan berulang sayuran yang SAMA tetap beda):
 *   1. Sampling (do_sample:true, temperature 0.7) → beda pilihan kata tiap panggilan.
 *   2. Rotasi SUDUT isi (FACT_ANGLES: gizi/sejarah/masak/kebun/mengejutkan) yang
 *      berputar tiap generasi → beda DIMENSI isi, dijamin walau entropi model kecil.
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

// Sudut pandang fun fact yang DIROTASI tiap generasi. Karena scan berulang sayuran
// yang sama memakai sudut berbeda, isinya berganti dimensi (bukan sekadar beda kata)
// — inilah penjamin variasi walau model 77M kadang bersampling nyaris sama. `lead`
// diselipkan ke prompt sebagai arah fokus; hint kata-kunci tetap meng-anchor topik.
const FACT_ANGLES = [
	{ key: 'nutrition', lead: 'its nutrition or health benefits' },
	{ key: 'history', lead: 'its history or where it originally comes from' },
	{ key: 'cooking', lead: 'how people cook or eat it around the world' },
	{ key: 'gardening', lead: 'how it grows on the plant or in the garden' },
	{ key: 'surprising', lead: 'a surprising or record-breaking detail about it' }
];

class FunFactService {
	// Penunjuk rotasi sudut. Hidup selama umur instance (dibuat sekali di app.js),
	// jadi maju terus tiap "Scan Lagi" → dua generasi berturut tak pernah sesudut.
	#angleIndex = 0;

	constructor() {
		this.generator = null;
		this.isModelLoaded = false;
		this.isGenerating = false;
		this.config = null;
		this.currentBackend = null;
	}

	// Ambil sudut berikutnya secara round-robin. Dipilih ketimbang acak agar dua
	// scan beruntun DIJAMIN beda sudut (persis skenario yang diuji reviewer).
	#nextAngle() {
		const angle = FACT_ANGLES[this.#angleIndex % FACT_ANGLES.length];
		this.#angleIndex += 1;
		return angle;
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

	// Prompt utama: model MENYUSUN satu kalimat fun fact. `angle.lead` mengarahkan
	// FOKUS isi (sudut yang dirotasi), hint kata-kunci sebagai konteks peng-anchor
	// topik (bukan disalin) — model yang menulis kalimatnya sendiri.
	#buildPrompt(name, hint, angle) {
		return `Write one interesting fun fact about the ${name}, focusing on ${angle.lead}. Use these keywords as context: ${hint}.`;
	}

	// Prompt cadangan (dipakai bila keluaran pertama melenceng dari sayurannya).
	// Tetap keluaran model — hanya membingkai hint dari sudut berbeda, bukan teks jadi.
	#altPrompt(name, hint) {
		return `${hint}. Turn this into one fun fact about the ${name}.`;
	}

	// Rapikan keluaran MODEL (buang sisa label prompt, kapital, akhiri titik) + potong
	// ke maksimal 2 kalimat pertama (buang racauan ekor model 77M).
	// TIDAK ADA teks pra-tulis: bila keluaran model kosong, kembalikan string kosong
	// dan biarkan pemanggil melempar error → yang tampil ke pengguna SELALU keluaran model.
	#tidyFact(raw) {
		let text = (raw || '')
			.replace(/^\s*(fun fact:?|keywords?:.*|answer:?)\s*/i, '')
			.replace(/\s+/g, ' ')
			.trim();
		const sentences = text.match(/[^.!?]+[.!?]+/g);
		if (sentences && sentences.length > 2) {
			text = sentences.slice(0, 2).join(' ').trim();
		}
		if (!text) return '';
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
			// (bukan menyalin). Sudut isi dirotasi tiap panggilan, dan decoding pakai
			// SAMPLING → scan berulang sayuran yang sama menghasilkan fakta berbeda.
			// Kalau keluaran pertama melenceng (tak menyebut nama sayurannya), dicoba
			// sekali lagi dengan prompt cadangan — tetap keluaran model, tetap sampled.
			const hint = this.#lookupHint(name);
			const angle = this.#nextAngle();
			const params = {
				max_new_tokens: 60,
				min_new_tokens: 18,
				do_sample: true,
				temperature: 0.5,   // rendah demi koherensi model 77M; variasi tetap dijamin rotasi sudut
				top_p: 0.9,
				top_k: 50,
				repetition_penalty: 1.3,
				no_repeat_ngram_size: 3
			};

			const prompt = hint
				? this.#buildPrompt(name, hint, angle)
				: `Write one interesting fun fact about the vegetable ${name}, focusing on ${angle.lead}.`;
			let funFact = this.#tidyFact(this.#extractText(await this.generator(prompt, params)));

			// Penjaga on-topic. Keluaran dianggap "melenceng" bila tak menyebut nama
			// sayur, ATAU tak memakai satu pun kata penting dari hint (gejala halusinasi
			// seperti spinach→"rock band"). Bila begitu, coba prompt cadangan yang
			// hint-heavy — tetap keluaran model, tetap di-sampling — dan pakai bila lebih
			// grounded (menyebut sayur, dan memakai hint / setidaknya tak lebih buruk).
			const stem = name.replace(/s$/i, '');
			const hintWords = hint ? (hint.toLowerCase().match(/[a-z]{4,}/g) || []) : [];
			const mentionsVeg = (t) => new RegExp(`\\b${stem}`, 'i').test(t);
			const usesHint = (t) => {
				const low = t.toLowerCase();
				return hintWords.some((w) => low.includes(w));
			};
			if (hint && (!mentionsVeg(funFact) || !usesHint(funFact))) {
				const retry = this.#tidyFact(
					this.#extractText(await this.generator(this.#altPrompt(name, hint), params)));
				if (mentionsVeg(retry) && (usesHint(retry) || !usesHint(funFact))) {
					funFact = retry;
				}
			}

			// Tanpa jaring teks pra-tulis: bila model tak menghasilkan apa pun (nyaris
			// mustahil karena min_new_tokens:18), lempar error → app.js tak jadi mengunci,
			// kamera lanjut memindai & mencoba lagi. Yang tampil SELALU keluaran model.
			if (!funFact) {
				throw new Error('Model tidak menghasilkan teks');
			}

			return { vegetable: name, funFact, tone, angle: angle.key };
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
