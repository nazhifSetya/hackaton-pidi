# PGABL — Asisten Legal Cipta Kerja (versi Bimo, Basic)

Submission akhir Dicoding **Pengembangan Generative AI Berbasis LLM (PGABL)**: asisten AI tim legal
yang menjawab pertanyaan seputar **4 regulasi Cipta Kerja** (PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023),
dengan **SLM fine-tuned** (QLoRA) + **RAG**.

**Target:** kriteria **Basic** (lulus ⭐⭐⭐), fokus cepat & mudah.

## Isi

- `submission/` — deliverable final (2 notebook + `link_huggingface.txt` + `requirements.txt`) yang di-zip ke Dicoding.
- `scripts/` — generator notebook (`build_sft_notebook.py`, `build_rag_notebook.py`) + `verify_chunker.py`.
- `data/raw/` — 4 PDF regulasi (tidak di-commit; diunggah ke Google Drive saat menjalankan).
- `panduan/PANDUAN_COLAB.md` — langkah menjalankan di Google Colab T4.
- `CLAUDE.md` — memory internal + hard rules + matriks anti-plagiarisme + progress log.

## Stack

| Komponen | Pilihan |
|---|---|
| Base model | `unsloth/gemma-2-2b-it-bnb-4bit` (QLoRA 4-bit) |
| Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` |
| Embedder | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector DB | ChromaDB (in-memory, cosine) |
| Chunker | `RecursiveCharacterTextSplitter` (1000/150) |
| Interface | Gradio `gr.Interface` |
| Compute | Google Colab T4 16 GB |

## Cara pakai

Lihat [`panduan/PANDUAN_COLAB.md`](panduan/PANDUAN_COLAB.md).
