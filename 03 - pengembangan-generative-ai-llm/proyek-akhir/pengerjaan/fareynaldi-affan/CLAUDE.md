# CLAUDE.md — Fine-tuned Chatbot Tim Legal berbasis RAG (PGABL) — versi **Fareynaldi (MINIMAL/BASIC)**

> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> Update bagian [Progress Log](#-progress-log) tiap satu tahap selesai.

---

## ⛔ SCOPE & TARGET

- Proyek: submission akhir Dicoding **"Pengembangan Generative AI Berbasis LLM (PGABL)"** — Asisten AI tim legal (SLM fine-tuned + RAG) untuk 4 regulasi Cipta Kerja.
- **Pemilik submission: Fareynaldi** (rekan tim). Submission **TERPISAH** & independen.
- **TARGET NILAI: KRITERIA MINIMAL / BASIC saja (⭐⭐⭐ lulus).** BUKAN Skilled, BUKAN Advanced. Tujuan: cukup lulus, hemat waktu & compute.
- Proyek **self-contained** di folder ini. Aturan CLAUDE.md proyek lain (Everest/EBC dll) TIDAK berlaku.

## 🔴 ATURAN #1 — ANTI-PLAGIARISME (WAJIB, jangan dilanggar)

- Ada versi **rekannya (Nazhif)** yang sudah DITERIMA Advanced di folder sibling:
  `../Fine-tuned_Chatbot_Tim_Legal_berbasis_RAG/`
- **Baca versi Nazhif HANYA untuk memahami rubrik + metodologi + "gotcha" teknis (di PROGRESS LOG-nya) — DILARANG COPY-PASTE kode/notebook.** Dicoding mengecek kemiripan antar-submission; kalau notebook Fareynaldi identik → KEDUA submission bisa kena reject/flag kolusi (termasuk milik Nazhif yang sudah diterima).
- Bangun implementasi **INDEPENDEN**:
  - Akun & token Hugging Face **milik Fareynaldi sendiri** (bukan `nazhifsetya-merpati`).
  - Kode ditulis ulang dengan struktur/gaya/penamaan sendiri.
  - Pertanyaan uji, contoh, dan narasi markdown berbeda.
  - Hyperparameter boleh berbeda.
  - Sama METODE (rubrik memang sama untuk semua), beda KODE & ASET.
- 4 PDF regulasi = knowledge base yang DISEDIAKAN (sama untuk semua peserta) → boleh dipakai (bukan plagiarisme). Copy dari `../Fine-tuned_Chatbot_Tim_Legal_berbasis_RAG/artifacts/document_knowledge_RAG/*.pdf` ke `data/raw/` (rename path-safe: `PP_5_2021.pdf`, `PP_35_2021.pdf`, `PP_51_2023.pdf`, `UU_6_2023.pdf`).

## 👤 USER & GAYA KERJA

- **Nama:** Fareynaldi — dipakai di nama file submission (`_Fareynaldi`).
- **Komunikasi (WAJIB):** Bahasa Indonesia simpel, pelan-pelan, step-by-step, jelaskan **KENAPA** tiap langkah. Teliti detail.
- **ASK, DON'T ASSUME:** kalau ambigu (username HF, chunking, dsb), TANYA dulu via `AskUserQuestion` SEBELUM nulis kode.

---

## 🎯 YANG DIBANGUN — hanya tier BASIC tiap kriteria

### K1 — SLM Fine-tuning (BASIC, 2 pts)
- Load `unsloth/Llama-3.2-3B-Instruct` **4-bit** (QLoRA double quantization, `nf4`, compute `bfloat16`).
- LoRA di target **MHA+FFN** (`q,k,v,o,gate,up,down`).
- Chat template **Llama-3** ke dataset `Ichsan2895/alpaca-gpt4-indonesian` via `datasets.map()`, lalu **PRINT satu contoh baris terformat** (harus terlihat special token `<|begin_of_text|>`, `<|start_header_id|>`, `<|eot_id|>`) → **BUKTI WAJIB**.
- `SFTTrainer` **min 800 steps** tanpa OOM (kalau OOM: turunkan batch/max_seq_length, JANGAN turunkan step).
- Push model ke HF **PUBLIC** (akun Fareynaldi) dengan `merged_16bit` → simpan link di `submission/link_huggingface.txt`.
- **CUKUP 1 eksperimen.** ❌ JANGAN buat train/val split + `eval_strategy` + eksperimen ke-2 (Skilled). ❌ JANGAN buat GRPO (Advanced).

### K2 — Sistem RAG (BASIC, 2 pts)
- Loader **4 PDF** (`pypdf`).
- Chunker sederhana (per-pasal / flat): `chunk_size ≤ 5000`, **overlap EKSPLISIT** (mis. 1000 / 100) — WAJIB eksplisit (bukan default library), didokumentasikan di config + notebook.
- Embedder `BAAI/bge-m3` (open-source, no OpenAI).
- **ChromaDB persistent — CUKUP 1 collection** (❌ TIDAK perlu 18 collection per-klaster; itu bukan syarat Basic).
- Retriever **top-k dense** sederhana → rangkai prompt `{context}` + `{question}` → generate pakai **model K1** (bukan model proprietary).
- ❌ JANGAN buat: metadata filtering, ensemble BM25, parent-child, HyDE, reranker, relevance-threshold, DuckDuckGo fallback (semua Skilled/Advanced).

### K3 — Antarmuka (BASIC, 2 pts)
- `gr.Interface` **sederhana** ATAU loop `input()` interaktif — yang penting jawaban tampil.
- ❌ JANGAN `gr.Blocks` + chat history + citation panel + streaming (Skilled/Advanced).

---

## 📋 KEPUTUSAN TERKUNCI (jangan diubah tanpa konfirmasi Fareynaldi)

| Aspek | Keputusan |
|---|---|
| Target nilai | **BASIC (⭐⭐⭐ lulus)** — semua kriteria cukup Basic |
| Environment berat | **Google Colab T4 16 GB** (free tier) |
| SLM base | `unsloth/Llama-3.2-3B-Instruct` (4-bit QLoRA) |
| Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` (LOCKED rubric; **2 kolom** `input`+`output`) |
| Chat template | Llama-3 via `datasets.map()` + print output ter-format |
| SFT | SFTTrainer ≥800 steps, push `merged_16bit` HF public |
| Embedding | `BAAI/bge-m3` (open-source) |
| Vector DB | ChromaDB persistent, **1 collection** |
| Chunking | flat/per-pasal, `chunk_size ≤5000`, overlap **eksplisit** |
| RAG source | HANYA 4 PDF disediakan |
| Interface | `gr.Interface` sederhana / `input()` loop |
| Env var | HF_TOKEN via `google.colab.userdata` / Colab Secret — **NO hardcode** |
| Seed | 42 |
| Bahasa | Python 3.11 |

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

1. Dataset SFT WAJIB `Ichsan2895/alpaca-gpt4-indonesian`.
2. Chat template Llama-3 via `datasets.map()` + **print output ter-format** (bukti).
3. QLoRA **4-bit double quantization** (bukan 8-bit/fp16 penuh).
4. SFTTrainer **min 800 steps** tanpa OOM.
5. Model WAJIB `push_to_hub`/`save` **merged_16bit** ke HF **Public** (akun Fareynaldi), link di `link_huggingface.txt`.
6. Chunk size ≤5000, **overlap EKSPLISIT** (documented).
7. Embedding **open-source** (bge-m3), no OpenAI.
8. RAG source HANYA 4 PDF disediakan.
9. Token/API key via **env var / Colab Secret** — TIDAK boleh hardcoded/committed.
10. Notebook `.ipynb` WAJIB **sudah dijalankan penuh** (output ter-embed).
11. `requirements.txt` **pipreqs-style** (hanya library yang dipakai), BUKAN pip freeze.
12. **Zip flat** — no subfolder di dalam zip. Bahasa Python.
13. **DILARANG AutoML / No-Code / UI-tool instan.**
14. **TIDAK BOLEH meta-conversation di deliverable** (notebook/submission): dilarang "share ke aku", "kasih tau aku", kata "Claude", referensi ke CLAUDE.md/panduan. Notebook harus professional & self-contained untuk reviewer Dicoding.

---

## 🧭 METODOLOGI KERJA (playbook — WAJIB ikut)

1. **VERTICAL per-kriteria:** K1 (SFT Basic) → tuntas → K2 (RAG Basic) → K3 (interface). Notebook = pipeline berurutan.
2. **VERIFY-FIRST:** logika non-model (PDF loader, chunker, cleaner) → prototype `scripts/*.py` lokal, simpan hasil ke `outputs/samples/`, **verify via Read tool** (jangan percaya stdout doang). Logika model (embed/generate) → prototype di Colab.
3. **Model muat SEKALI, cache di memory** (bge-m3 + LLM). Jangan reload per query.
4. **Config-driven:** magic number (chunk_size, overlap, top_k, model id) di `configs/*.yaml`, load via `yaml.safe_load`. Jangan hardcode di notebook.
5. **Colab = Fareynaldi yang jalanin.** Kamu **produce file lalu STOP** — jangan auto-run training/heavy script.
6. **Output ter-embed** via user Run All di Colab. Semua notebook harus lolos re-run penuh.
7. **Seed=42** di semua random ops.
8. **Sensitive info via env var / Colab Secret** (HF_TOKEN).
9. Update [Progress Log](#-progress-log) tiap tahap selesai.

## 🐍 ENVIRONMENT

- **Utama: Google Colab GPU T4 16GB.** 2 notebook (Fine-tuning, RAG) dieksekusi di sini. Library via `!pip install` sel awal.
- **Mac lokal (mesin ini):** HANYA prototyping non-model (edit notebook via JSON script, baca PDF/rubric, script chunker/loader). JANGAN load Llama/bge-m3 lokal. Python homebrew di Mac ini pyexpat rusak → untuk verify lokal, pakai venv dari `/usr/bin/python3` (Apple 3.9.6, sehat) + pip install pypdf/pyyaml.

## 🔑 GOTCHA TEKNIS (dari pengalaman Nazhif — baca PROGRESS LOG-nya, hemat berjam-jam)

- **Download model HF di Colab sering STALL** (63kB/s / stuck di ~67M). Solusi: set Colab Secret `HF_TOKEN` (role **Read**, Notebook access ON) → `login()`. Kalau tetap stall: unduh via **`aria2c`** (16 koneksi + header `Authorization: Bearer <token>` untuk file LFS) dan/atau **cache model ke Drive** (download sekali, sesi berikut load dari Drive). Route VM jelek → **Disconnect and delete runtime** (bukan cuma restart) untuk VM baru.
- **Unsloth 2026.7.x butuh transformers ≥4.51.3** → install Unsloth **unpinned** (jangan pin manual transformers/trl/datasets → ImportError `CompileConfig`).
- **`push_to_hub_merged` bug** (`TypeError: safe_serialization`) di Unsloth 2026.7.2 → pakai pola 2 langkah: `save_pretrained_merged(DIR, tokenizer, save_method="merged_16bit")` lalu `HfApi().upload_folder(...)`.
- **Dataset `alpaca-gpt4-indonesian` = 2 kolom** (`input`, `output`), BUKAN 3 kolom Alpaca klasik.
- **`apply_chat_template(return_tensors="pt")`** di transformers 5.x kadang balikin `BatchEncoding` (dict) bukan tensor → ambil `input_ids` dari dict, jangan `.shape` langsung.
- **Colab pola 2× Run All** (sel install → restart runtime → Run All lagi).

## 📁 STRUKTUR FOLDER

```
Fine-tuned_Chatbot_RAG_Fareynaldi/
├── CLAUDE.md                 ← file ini
├── README.md
├── requirements.txt          ← draft; final di-generate saat packaging
├── .env.example              ← HF_TOKEN + HF_USERNAME
├── .gitignore
├── configs/                  ← config-driven (BASIC)
│   ├── model_config.yaml
│   ├── training_config.yaml
│   └── rag_config.yaml
├── src/                      ← core code (agent tulis independen)
│   ├── data/                 # loaders, formatters (SFT + PDF)
│   └── rag/                  # chunker, embedder, vector_store
├── scripts/                  ← prototyping VERIFY-FIRST lokal
├── notebooks/                ← notebook kerja (bukan submission)
├── data/{raw,processed}/     ← PDF (copy dari Nazhif) + chunks
├── outputs/samples/          ← hasil verify
├── docs/
└── submission/               ← 💻 DELIVERABLE (yang di-zip)
    ├── Fine-tuning_submission_..._Fareynaldi.ipynb
    ├── RAG_submission_..._Fareynaldi.ipynb
    ├── link_huggingface.txt
    └── requirements.txt
```

**Deliverable zip:** flat (semua file di root zip). Cek `../Fine-tuned_Chatbot_Tim_Legal_berbasis_RAG/artifacts/4.ketentuan_berkas.md` untuk nama & struktur file yang PASTI.

---

## ✅ PROGRESS LOG

> WAJIB diupdate tiap tahap selesai. Format: `**Tahap N — [Judul] ([Status], tanggal)**`.

- **Tahap 0 — Setup: ✅ SELESAI (2026-07-15).**
  - [x] Konfirmasi user via AskUserQuestion: target **Basic** ✅, nama file `fareynaldi_affan` (lowercase), akun HF belum ada → instruksi setup HF diberikan (daftar → generate token role Write → set Colab Secret `HF_TOKEN` + `HF_USERNAME`).
  - [x] Jawab jujur soal "Victus bisa training?": **TIDAK** — RTX 3050 4 GB VRAM tidak cukup untuk SFT Llama-3.2-3B (peak ~5-7 GB). Wajib Colab T4 free tier (16 GB).
  - [x] 4 PDF regulasi disalin dari `../Fine-tuned_Chatbot_Tim_Legal_berbasis_RAG/artifacts/document_knowledge_RAG/` ke `data/raw/` dengan rename path-safe: `PP_5_2021.pdf` (17M), `PP_35_2021.pdf` (2.5M), `PP_51_2023.pdf` (2.7M), `UU_6_2023.pdf` (82M).
  - [x] Config skeleton (`configs/{model,training,rag}_config.yaml`) sudah tersedia — nilai Basic (LoRA r=8/α=16 MHA+FFN, SFT 800 step LR 3e-4, chunk 1000/overlap 100, top-k=4, ChromaDB 1 collection).

- **Tahap 1 — Notebook Fine-tuning SFT Basic: ✅ SKELETON SELESAI (2026-07-15) — PENDING Colab Run All.**
  - [x] `submission/Fine-tuning_submission_PGABL_fareynaldi_affan.ipynb` di-generate via `scripts/build_sft_notebook.py` (24 cell: 13 markdown + 11 code, JSON valid, Python syntax 0-error).
  - [x] Cell layout linear (single-experiment, no split/eval — Basic tier): setup Colab & HF Secret → install Unsloth unpinned → `FastLanguageModel.from_pretrained(load_in_4bit=True)` (QLoRA nf4 + double quant) → LoRA MHA+FFN 7 target (`q,k,v,o,gate,up,down`) → load `Ichsan2895/alpaca-gpt4-indonesian` (2 kolom, subset 12k baris) → `get_chat_template("llama-3")` + `datasets.map()` + **print bukti 4 special token** → `SFTTrainer` 800 step (batch 2 × grad_accum 4 = eff 8) → **push pola 2-langkah** (`save_pretrained_merged` + `HfApi.upload_folder`, dgn `delete_patterns=["adapter_*"]` bypass bug `TypeError: safe_serialization`) → tulis `link_huggingface.txt`.
  - [x] Anti-plagiarisme: struktur linear (Nazhif 2-exp winner-picker), LoRA r=8 (Nazhif r=16/32), LR 3e-4 (Nazhif 2e-4), naming variabel & narasi markdown berbeda, repo HF `PGABL-Llama-3.2-3B-SFT-Fareynaldi` (Nazhif `PGABL-Llama-3.2-3B-SFT`).
  - [x] HR-14 scan: notebook CLEAN dari "Claude"/"CLAUDE.md"/"share ke aku"/"Nazhif"/token literal.
  - [ ] **USER TODO**: buka `submission/Fine-tuning_submission_PGABL_fareynaldi_affan.ipynb` di Colab T4 → set 2 Colab Secret (`HF_TOKEN`, `HF_USERNAME`) → **Run All** (~90-120 menit). Setelah berhasil, isi `submission/link_huggingface.txt` di-generate otomatis oleh notebook — copy URL ke deliverable folder.

- **Tahap 2 — Notebook RAG Basic + Gradio: ✅ SKELETON SELESAI (2026-07-15) — PENDING Colab Run All (setelah SFT).**
  - [x] `submission/RAG_submission_PGABL_fareynaldi_affan.ipynb` di-generate via `scripts/build_rag_notebook.py` (26 cell: 14 markdown + 12 code, JSON valid, Python syntax 0-error).
  - [x] Cell layout: setup + secrets → mount Drive & verify 4 PDF di `MyDrive/PGABL_Fareynaldi/data/raw/` → `pypdf` extract per-halaman → **sliding window chunker `size=1000, overlap=100` (EKSPLISIT, bukan default)** → embed `BAAI/bge-m3` (open-source, GPU T4) → **ChromaDB persistent, 1 koleksi `regulasi_ciptaker`** (rubric Basic cukup 1 collection) → retriever top-k dense (k=4) → generator = model K1 dari HF (4-bit `bitsandbytes` + `apply_chat_template("llama-3")`) → **3 query uji tampilkan jawaban + sumber (regulasi + halaman + similarity)** → **`gr.Interface`** sederhana (input Textbox + output Textbox + 3 examples).
  - [x] Anti-plagiarisme: 1 collection (Nazhif 18 per-BAB UU), dense-only (Nazhif ensemble BM25+dense RRF + parent-child + HyDE + reranker + DDG fallback), `gr.Interface` (Nazhif `gr.Blocks` + chat + citation Dataframe + streaming), chunk 1000/100 (Nazhif 1200/100), top-k=4 (Nazhif 5), system prompt & function naming berbeda (`retrieve`, `jawab_rag`, `antarmuka_rag` vs Nazhif `rag_basic`/`rag_advanced`).
  - [x] HR-14 scan: CLEAN.
  - [ ] **USER TODO**: upload 4 PDF ke Drive `MyDrive/PGABL_Fareynaldi/data/raw/` (drag-drop dari lokal `data/raw/*.pdf`) → buka notebook di Colab T4 → **Run All** setelah SFT selesai. Gradio akan launch di URL `share=True`.

- **Tahap 3 — Packaging & Submission: ⏸️ SIAP EKSEKUSI setelah notebook run.**
  - [x] `submission/link_huggingface.txt` placeholder dibuat (isi otomatis di-overwrite oleh cell terakhir notebook SFT saat Run All).
  - [x] `submission/requirements.txt` pipreqs-style (16 lib, no pin, no freeze) — cover Fine-tuning + RAG + gradio + huggingface_hub + numpy.
  - [x] Root `requirements.txt` juga di-update sync.
  - [ ] **USER TODO** (setelah kedua notebook Run All di Colab):
    1. Download 2 notebook `.ipynb` (dengan output ter-embed) dari Colab ke lokal `submission/`.
    2. Download `link_huggingface.txt` dari Colab, replace file lokal `submission/link_huggingface.txt`.
    3. Verify HR-12 (semua cell output ter-embed) + HR-5 (repo HF public, ada `model-*.safetensors`, bukan cuma adapter).
    4. Zip flat 4 file: `PGABL_fareynaldi_affan.zip` = `Fine-tuning_submission_PGABL_fareynaldi_affan.ipynb` + `RAG_submission_PGABL_fareynaldi_affan.ipynb` + `link_huggingface.txt` + `requirements.txt`. Verify no subfolder.
    5. Upload ke Dicoding.

---
**Status ringkas:** Skeleton 2 notebook + deliverable file siap. Blocker sekarang = user (Fareynaldi): setup akun HF + Colab Secret + Run All di T4. Instruksi step-by-step sudah diberikan pada respons awal agent.
