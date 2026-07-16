# Fine-tuned Chatbot Tim Legal berbasis RAG — PGABL (Fareynaldi)

Submission Dicoding **"Pengembangan Generative AI Berbasis LLM (PGABL)"**: asisten AI internal
tim legal untuk 4 regulasi Cipta Kerja (PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023), memakai
**SLM fine-tuned (Llama-3.2-3B) + RAG**.

> **Target: kriteria BASIC (⭐⭐⭐ lulus).** Detail rules & rencana ada di `CLAUDE.md`.

## Pilar
1. **K1 — Fine-tuning:** Llama-3.2-3B-Instruct + QLoRA 4-bit, SFT pada `alpaca-gpt4-indonesian`
   (mengajarkan format instruksi Bahasa Indonesia). Model di-push ke Hugging Face (public).
2. **K2 — RAG:** 4 PDF → chunk (overlap eksplisit) → embedding BGE-M3 → ChromaDB → retrieval
   top-k → generate dengan model K1.
3. **K3 — Antarmuka:** Gradio sederhana untuk tanya-jawab.

## Struktur
- `configs/` — parameter (config-driven)
- `src/` — kode modular (loader, chunker, embedder, vector store)
- `notebooks/` — notebook kerja
- `submission/` — deliverable final (2 ipynb + link_huggingface.txt + requirements.txt)

## Menjalankan
Notebook fine-tuning & RAG dijalankan di **Google Colab GPU T4**. Set Colab Secret `HF_TOKEN`
(akun Fareynaldi) lebih dulu. 4 PDF sumber diletakkan di Google Drive.

---
_Submission independen. Bukan turunan/salinan submission peserta lain._
