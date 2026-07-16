import { logError } from '../core/utils.js';

const TRANSFORMERS_CDN = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.5';
const MODEL_ID = 'HuggingFaceTB/SmolLM2-135M-Instruct';
const MAX_VEGETABLE_INPUT_LENGTH = 50;

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
			const { pipeline, env } = await import(TRANSFORMERS_CDN);
			env.allowLocalModels = false;

			this.generator = await pipeline('text-generation', MODEL_ID, { dtype: 'q4' });
			this.currentBackend = 'wasm';
			this.isModelLoaded = true;
		} catch (error) {
			logError('Error loading Transformers.js model', error);
			throw new Error(`Failed to load FunFact model: ${error.message}`);
		}
	}

	async generateFunFact(vegetable, tone = 'normal') {
		if (!this.isModelLoaded || this.isGenerating) {
			throw new Error('Model belum siap atau sedang menghasilkan fakta');
		}

		if (!vegetable || typeof vegetable !== 'string') {
			throw new Error('Nama sayuran yang valid diperlukan');
		}

		const cleaned = vegetable
			.replace(/[^a-zA-Z0-9\s\-]/g, '')
			.trim()
			.slice(0, MAX_VEGETABLE_INPUT_LENGTH);

		if (!cleaned) {
			throw new Error('Nama sayuran tidak valid setelah pembersihan');
		}

		this.isGenerating = true;
		try {
			const messages = [
				{
					role: 'system',
					content: 'You are a friendly assistant that shares interesting fun facts about vegetables. Reply with ONE concise, unique, and true fun fact in one to two sentences. Do not repeat the question.'
				},
				{
					role: 'user',
					content: `Tell me a fun fact about the vegetable ${cleaned}.`
				}
			];

			const output = await this.generator(messages, {
				max_new_tokens: 120,
				temperature: 0.7,
				top_p: 0.9,
				do_sample: true
			});

			const raw = output?.[0]?.generated_text;
			let funFact = '';
			if (Array.isArray(raw)) {
				const lastTurn = raw[raw.length - 1];
				funFact = (lastTurn?.content || '').trim();
			} else if (typeof raw === 'string') {
				funFact = raw.trim();
			}

			if (!funFact) {
				funFact = `Fun fact: ${cleaned} is a fascinating vegetable enjoyed around the world.`;
			}

			return {
				vegetable: cleaned,
				funFact,
				tone
			};
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
