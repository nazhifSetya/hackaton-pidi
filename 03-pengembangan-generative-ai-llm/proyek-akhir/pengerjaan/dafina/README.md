# Asisten Legal Cipta Kerja — PGABL (Dafina)

Submission Dicoding **"Pengembangan Generative AI Berbasis LLM (PGABL)"**: asisten AI
tim legal untuk 4 regulasi Cipta Kerja (PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023),
memakai **SLM fine-tuned (Qwen2.5-1.5B-Instruct) + RAG**.

> **Target: kriteria BASIC (⭐⭐⭐ lulus).** Detail rules & rencana ada di `CLAUDE.md`.

## Pilar
1. **K1 — Fine-tuning:** `Qwen2.5-1.5B-Instruct` + QLoRA 4-bit, SFT pada
   `alpaca-gpt4-indonesian` (mengajarkan gaya instruksi Bahasa Indonesia). Chat
   template **ChatML**. Model di-push ke Hugging Face (public).
2. **K2 — RAG:** 4 PDF → chunk berbasis-kalimat (overlap eksplisit) → embedding
   `multilingual-e5-base` → indeks **FAISS** → retrieval top-k → generate dengan model K1.
3. **K3 — Antarmuka:** loop `input()` interaktif + `IPython.display.Markdown`.

## Struktur
- `configs/` — parameter (config-driven)
- `src/` — placeholder kode modular
- `scripts/` — builder notebook (`build_sft_notebook.py`, `build_rag_notebook.py`)
- `submission/` — deliverable final (2 ipynb + link_huggingface.txt + requirements.txt)

## Menjalankan
Notebook fine-tuning & RAG dijalankan di **Google Colab GPU T4**. Set Colab Secret
`HF_TOKEN` + `HF_USERNAME` (akun Dafina) lebih dulu. 4 PDF sumber diletakkan di
Google Drive `MyDrive/PGABL_Dafina/`.

---
_Submission independen. Bukan turunan/salinan submission peserta lain._
