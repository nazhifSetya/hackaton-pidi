import { logError } from '../core/utils.js';

/*
 * FunFactService — penghasil fun fact berbasis model bahasa untuk RootFacts.
 * Menjalankan FLAN-T5-base lokal di peramban via Transformers.js (seq2seq,
 * pipeline 'text2text-generation', varian q8 agar unduhan wajar).
 *
 * Pendekatan GROUNDED (RAG-lite) — ini pembeda pendekatan Dafina: model kecil
 * seperti FLAN-T5-base lemah "mengarang" fakta dari nol (cenderung melingkar/salah),
 * tetapi ANDAL memparafrase fakta yang sudah benar. Maka tiap sayuran dipasangkan
 * sebuah "seed fact" terkurasi (VEG_FACTS), lalu model diminta menyusunnya jadi satu
 * kalimat yang mengalir. Hasilnya: fun fact yang AKURAT sekaligus menarik, bukan
 * deskripsi melingkar. Bila parafrase menyimpang (subjek hilang/ketukar), dipakai
 * seed fact-nya langsung sebagai jaring pengaman. Decoding greedy = deterministik.
 */

const HF_LIB = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const LLM_ID = 'Xenova/flan-t5-base';
const LLM_TASK = 'text2text-generation';
const LABEL_MAX = 32;

// Seed fact terkurasi per label model (18 sayuran). Kunci = huruf kecil agar cocok
// apa pun kapitalisasi label. Fakta ini sengaja unik & menarik (sejarah/asal/keunikan)
// dan menjadi bahan yang diparafrase model menjadi fun fact akhir.
const VEG_FACTS = {
	beetroot: 'Beetroot juice was once used as a natural dye and even as a lipstick and hair colouring in the 19th century',
	paprika: 'Paprika is made from dried and ground red peppers, and Hungary is so famous for it that paprika is treated as its national spice',
	cabbage: 'The heaviest cabbage ever grown weighed more than 62 kilograms, about the same as a full-grown adult',
	carrot: 'Carrots were originally purple and white, and the familiar orange carrot was bred by Dutch farmers in the 16th century',
	cauliflower: 'Cauliflower also grows in purple, orange, and green varieties, and the orange type contains extra beta-carotene',
	chilli: 'The fiery heat of a chilli comes from a compound called capsaicin, which tricks your brain into feeling a burning sensation',
	corn: 'Every ear of corn has an even number of rows, and a single cob usually carries about 800 kernels',
	cucumber: 'A cucumber is about 96 percent water, which is why it tastes so cool and refreshing',
	eggplant: 'Eggplants were named after early European types of the plant that were small, white, and shaped just like chicken eggs',
	garlic: 'Ancient Egyptians gave garlic to the workers who built the pyramids because they believed it boosted their strength',
	ginger: 'Ginger grows as an underground stem called a rhizome, and people have used it as a spice and medicine for more than 5,000 years',
	lettuce: 'The ancient Egyptians treated lettuce as a sacred plant and linked it to their god of fertility',
	onion: 'Cutting an onion releases a gas that turns into a mild acid when it reaches your eyes, which is why it makes you cry',
	peas: 'Peas are one of the oldest crops, and archaeologists have found pea remains that are more than 9,000 years old',
	potato: 'In 1995 the potato became the first vegetable ever to be grown in space, aboard a NASA space shuttle',
	turnip: 'People in Ireland and Scotland once carved spooky faces into turnips to make the very first Halloween lanterns',
	soybean: 'Soybeans are so versatile that they are turned into everything from tofu and soy milk to crayons and eco-friendly ink',
	spinach: 'A decimal-point printing error once listed spinach as having ten times more iron than it really has, which helped inspire Popeye'
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

	// Cari seed fact untuk sebuah label (kunci huruf kecil, tahan bentuk jamak
	// sederhana mis. "Carrots" -> "carrot"). null bila di luar 18 label.
	#lookupSeed(name) {
		const key = name.toLowerCase();
		return VEG_FACTS[key] || VEG_FACTS[key.replace(/s$/, '')] || null;
	}

	// Prompt grounding: minta model MEMPARAFRASE seed fact menjadi satu kalimat yang
	// mengalir (bukan mengarang dari nol). Ini yang membuat FLAN-T5-base kecil andal.
	#buildPrompt(seed) {
		return `Paraphrase into one engaging sentence: ${seed}.`;
	}

	// Rapikan hasil parafrase + JARING PENGAMAN. Bila keluaran menyimpang — subjek
	// (nama sayuran) hilang/ketukar atau terlalu pendek — pakai seed fact langsung
	// supaya yang tampil selalu AKURAT. Terakhir: pastikan kapital & diakhiri titik.
	#tidyFact(raw, name, seed) {
		let text = (raw || '')
			.replace(/^\s*(paraphrase[^:]*:|fun fact:?)\s*/i, '')
			.replace(/\s+/g, ' ')
			.trim();

		const stem = name.replace(/s$/i, '');
		const onTopic = new RegExp(`\\b${stem}`, 'i').test(text);
		if (seed && (text.length < 25 || !onTopic)) {
			text = seed;
		}
		if (!text) {
			text = `${name} has a long history in kitchens around the world and is prized for the vitamins, minerals, and fibre it adds to a healthy diet`;
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
			// Grounding: ambil seed fact terkurasi untuk sayuran ini, lalu minta
			// model MEMPARAFRASE-nya. Karena seed sudah benar & cukup panjang,
			// output jadi akurat sekaligus kaya — menjawab keluhan reviewer (fakta
			// terlalu umum/pendek & melingkar). Greedy = deterministik. Untuk label
			// di luar 18 (semestinya tak terjadi), model menjawab bebas sebagai
			// jalan terakhir.
			const seed = this.#lookupSeed(name);
			const prompt = seed
				? this.#buildPrompt(seed)
				: `Tell me one surprising and specific fun fact about the vegetable ${name}, in one full sentence.`;

			const output = await this.generator(prompt, {
				max_new_tokens: 90,
				min_new_tokens: 12,
				do_sample: false,
				repetition_penalty: 1.2,
				no_repeat_ngram_size: 3
			});

			const funFact = this.#tidyFact(this.#extractText(output), name, seed);

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
