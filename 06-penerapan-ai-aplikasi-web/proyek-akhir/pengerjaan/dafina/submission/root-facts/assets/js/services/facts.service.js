import { logError } from '../core/utils.js';

/*
 * FunFactService — modul bahasa ("Si Otak") untuk RootFacts.
 * Menjalankan model bahasa kecil Qwen2.5-0.5B-Instruct secara lokal di
 * peramban lewat Transformers.js. Model ini instruction-tuned dan memakai
 * template chat (ChatML), jadi prompt disusun sebagai daftar pesan
 * system + user, lalu balasan asisten diambil dari pesan terakhir.
 */

const HF_LIB = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const LLM_ID = 'onnx-community/Qwen2.5-0.5B-Instruct';
const LLM_TASK = 'text-generation';
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
			// Ambil bobot dari Hugging Face Hub, bukan dari berkas lokal.
			lib.env.allowLocalModels = false;

			this.generator = await lib.pipeline(LLM_TASK, LLM_ID, { dtype: 'q4' });
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

	// Ambil teks balasan dari keluaran pipeline (mode chat -> pesan terakhir).
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
			// Prompt bahasa Inggris (anjuran modul). Nama disebut dua kali agar
			// model kecil tetap fokus pada sayuran yang dimaksud.
			const messages = [
				{
					role: 'system',
					content: 'You are a friendly botanist. Reply with exactly one short, surprising fun fact.'
				},
				{
					role: 'user',
					content: `Share one surprising fun fact about the vegetable ${name}. Mention ${name} and keep it under 30 words.`
				}
			];

			const output = await this.generator(messages, {
				max_new_tokens: 80,
				temperature: 0.6,
				top_p: 0.92,
				do_sample: true,
				repetition_penalty: 1.15
			});

			let funFact = this.#extractText(output);
			if (!funFact) {
				funFact = `${name} is a vegetable enjoyed in many dishes around the world.`;
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
