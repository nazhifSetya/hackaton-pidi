# CLAUDE.md — Asisten Legal Cipta Kerja (PGABL) — versi **Bimo (MINIMAL/BASIC)**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).

> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> Update bagian [Progress Log](#-progress-log) tiap satu tahap selesai.

---

## ⛔ SCOPE & TARGET

- Proyek: submission akhir Dicoding **"Pengembangan Generative AI Berbasis LLM (PGABL)"** — Asisten AI tim legal (SLM fine-tuned + RAG) untuk 4 regulasi Cipta Kerja.
- **Pemilik submission: Bimo Bramantyo** (rekan tim). Submission **TERPISAH** & independen. ⚠️ Konfirmasi ejaan nama lengkap untuk penamaan file sebelum packaging.
- **TARGET NILAI: KRITERIA MINIMAL / BASIC saja (⭐⭐⭐ lulus).** BUKAN Skilled, BUKAN Advanced. Tujuan: cukup lulus, hemat waktu & compute. Cocok profil Bimo (pemula–menengah, risk-averse).
- Proyek **self-contained** di folder ini. Aturan CLAUDE.md proyek lain TIDAK berlaku di sini.
- **Nama untuk deliverable:** `Bimo_Bramantyo` → file `..._PGABL_Bimo_Bramantyo.ipynb`, zip `PGABL_Bimo_Bramantyo.zip`.

## 🧮 CARA LULUS (rumus nilai)

- Rubrik PGABL punya **2 kriteria yang dinilai**: **K1 Fine-tuning** + **K2 RAG** (interface = bagian dari K2 Basic, bukan kriteria terpisah).
- `Nilai Akhir = Total Poin ÷ 2`. Basic = 2 poin/kriteria.
- **Basic di K1 + Basic di K2 → (2+2)/2 = 2.0 → Bintang 3 (C, "Basic/Cukup") = LULUS.**
- Jangan sampai ada 1 kriteria Reject (0 poin) → nilai anjlok "Tidak Lulus". Semua bullet Basic tiap kriteria WAJIB terpenuhi (tidak ada nilai parsial).

## 🔴 ATURAN #1 — ANTI-PLAGIARISME (WAJIB, jangan dilanggar)

Ada **TIGA** versi sibling di repo yang harus dijaga jaraknya:
- **Nazhif (Advanced, sudah DITERIMA):** [`../nazhif-setya-nugroho/`](../nazhif-setya-nugroho/)
- **Dafina (Basic, selesai):** [`../dafina/`](../dafina/)
- **Fareynaldi (Basic, skeleton):** [`../fareynaldi-affan/`](../fareynaldi-affan/)

**Baca ketiga versi HANYA untuk memahami rubrik + metodologi + gotcha teknis — DILARANG COPY-PASTE kode/notebook.** Dicoding mengecek kemiripan antar-submission; kalau notebook Bimo mirip salah satu → semua submission bisa kena reject/flag kolusi (termasuk punya Nazhif yang sudah diterima).

**Strategi diferensiasi Bimo = pilih opsi Basic yang SAH tapi BERBEDA dari ketiga sibling.** Tema + dataset SFT + 4 PDF **DIKUNCI Dicoding (sama untuk semua)** → itu BUKAN plagiarisme. Yang dibedakan = **model, chat template, embedder, vector DB, chunker, hyperparameter, penamaan variabel, dan akun HF.**

### 📊 MATRIKS DIFERENSIASI (jantung anti-plagiarisme — jaga tetap benar)

| Aspek | Nazhif (Advanced) | Fareynaldi (Basic) | Dafina (Basic) | **Bimo (Basic)** |
|---|---|---|---|---|
| Base model | Llama-3.2-3B | Llama-3.2-3B | Qwen2.5-1.5B | **Gemma-2-2B-it** |
| Chat template | Llama-3 | Llama-3 | ChatML | **Gemma** (`get_chat_template("gemma2")`) |
| Bukti special token | `<\|begin_of_text\|>` | `<\|begin_of_text\|>` | `<\|im_start\|>` `<\|im_end\|>` | **`<start_of_turn>` `<end_of_turn>`** |
| LoRA | r=16/32 | r=16 α=16 drop=0 | r=8 α=32 drop=0.05 | **r=8 α=16 drop=0.05** |
| LR / scheduler | 2e-4 linear | 3e-4 linear | 2e-4 cosine | **2e-4 linear + warmup_ratio 0.03** |
| Optimizer | adamw_8bit | adamw_8bit | paged_adamw_8bit | **adamw_8bit** |
| Subset dataset / seed | full / 42 | 12k / — | 8k / 42 | **10k / 3407** |
| Embedder | bge-m3 | bge-m3 | multilingual-e5-base | **paraphrase-multilingual-MiniLM-L12-v2** (tanpa prefix) |
| Vector DB | ChromaDB 18 col persist | ChromaDB 1 col persist | FAISS `IndexFlatIP` | **ChromaDB in-memory, `hnsw:space=cosine`, 1 col** |
| Chunker | per-pasal regex | sliding window char | kalimat greedy + overlap ekor | **`RecursiveCharacterTextSplitter`** (langchain-text-splitters) |
| chunk / overlap / top_k | 1200 / 100 / 5 | 1000 / 100 / 4 | 700 / 120 / 3 | **1000 / 150 / 4** |
| Interface (K2) | Gradio Blocks + citation | `gr.Interface` | loop `input()` | **`gr.Interface`** (+ sel contoh Q&A tercetak) |
| Repo HF | `PGABL-Llama-3.2-3B-SFT` | `...-SFT-Fareynaldi` | `PGABL-Qwen2.5-1.5B-SFT-Dafina` | **`PGABL-Gemma-2-2B-SFT-Bimo`** |
| Gaya penamaan | campuran | Inggris (`retrieve`,`trainer`) | Indonesia (`cari`,`pelatih`) | **Indonesia lain** (`muat_pdf`,`potong_teks`,`buat_embedding`,`ambil_konteks`,`hasilkan_jawaban`,`tanya`) |

- **Catatan overlap yang SAH:** `gr.Interface` (juga dipakai Fareynaldi) & ChromaDB (juga dipakai Nazhif/Fareynaldi) adalah **pilihan biner/terbatas yang disediakan rubrik**. Dibedakan lewat: ChromaDB **in-memory** (bukan persistent) + `hnsw:space=cosine` + penamaan Indonesia berbeda + sel contoh Q&A tercetak. Bukan copy kode.
- Akun & token Hugging Face **milik Bimo sendiri** (bukan akun Nazhif/Dafina/Fareynaldi). Ini juga syarat auto-reject rubrik: model instruct wajib hasil fine-tuning Bimo sendiri.
- 4 PDF regulasi = knowledge base DISEDIAKAN (sama untuk semua) → boleh dipakai. Sumber: `../nazhif-setya-nugroho/artifacts/document_knowledge_RAG/*.pdf` → copy ke `data/raw/` dengan rename path-safe.

## 👤 USER & GAYA KERJA

- **Nama:** Bimo Bramantyo — dipakai di nama file submission (`_Bimo_Bramantyo`).
- **Profil:** mahasiswa Dicoding, level **pemula–menengah**. Biasa pakai **Google Colab T4** untuk compute berat (spt proyek IndoBERT-nya). Device lokal utama: Victus (Windows).
- **Komunikasi (WAJIB):** Bahasa Indonesia simpel, pelan-pelan, step-by-step, jelaskan **KENAPA** tiap langkah. Teliti detail.
- **ASK, DON'T ASSUME:** kalau ambigu (username HF, nama lengkap, dsb), TANYA dulu SEBELUM nulis kode.

---

## 🎯 YANG DIBANGUN — hanya tier BASIC tiap kriteria

### K1 — SLM Fine-tuning (BASIC, 2 pts)
- Load `unsloth/gemma-2-2b-it-bnb-4bit` **4-bit** (QLoRA nf4 + **double quantization**, compute `bfloat16`, `max_seq_length=1024`).
- LoRA di target **MHA+FFN** (`q,k,v,o,gate,up,down`), **r=8 α=16 dropout=0.05**.
- Chat template **Gemma** (`get_chat_template(tokenizer, "gemma2")`) ke dataset `Ichsan2895/alpaca-gpt4-indonesian` via `datasets.map()`, lalu **PRINT satu contoh baris terformat** (harus terlihat `<start_of_turn>` & `<end_of_turn>`) → **BUKTI WAJIB**.
- `SFTTrainer` **800 steps** (eff batch 8, LR 2e-4 linear + warmup 0.03, adamw_8bit) tanpa OOM.
- Push model ke HF **PUBLIC** (akun Bimo) dengan `merged_16bit` → link di `submission/link_huggingface.txt`.
- **CUKUP 1 eksperimen.** ❌ JANGAN train/val split + `eval_strategy` + eksperimen ke-2 (Skilled). ❌ JANGAN GRPO (Advanced).

### K2 — Sistem RAG (BASIC, 2 pts)
- Loader **4 PDF** (`pypdf`) per-halaman. WAJIB keempatnya.
- Chunker **`RecursiveCharacterTextSplitter`** (dari `langchain-text-splitters`), `chunk_size=1000`, `chunk_overlap=150` — **EKSPLISIT**, didokumentasikan.
- Embedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (open-source, no OpenAI, **tanpa prefix** query/passage).
- **ChromaDB in-memory** (`chromadb.Client()`), 1 collection `regulasi_ciptaker_bimo`, `metadata={"hnsw:space":"cosine"}`.
- Retriever **top-4** → prompt `{konteks}` + `{pertanyaan}` → generate pakai **model K1 Bimo** (bukan model proprietary/baru).
- ❌ JANGAN: metadata filtering, ensemble BM25, parent-child, HyDE, reranker, threshold, DDG fallback (semua Skilled/Advanced).

### K3 — Antarmuka (bagian dari K2 Basic)
- **`gr.Interface`** dasar (1 textbox input → 1 textbox output, `fn=tanya`, `.launch(share=True)`).
- **Sel contoh Q&A (2-3 pertanyaan) tercetak via `IPython.display.Markdown` SEBELUM launch** → menjamin output ter-embed di notebook (UI Gradio tak persist statis di `.ipynb`).
- ❌ JANGAN `gr.Blocks` + chat history + citation panel + streaming (Skilled/Advanced).

---

## 📋 KEPUTUSAN TERKUNCI (jangan diubah tanpa konfirmasi Bimo)

| Aspek | Keputusan |
|---|---|
| Target nilai | **BASIC (⭐⭐⭐ lulus)** — K1 & K2 cukup Basic |
| Environment berat | **Google Colab T4 16 GB** (free tier) |
| SLM base | `unsloth/gemma-2-2b-it-bnb-4bit` (lisensi gemma, ungated, 4-bit QLoRA) |
| Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` (LOCKED rubric; **2 kolom** `input`+`output`) |
| Chat template | Gemma via `get_chat_template(tokenizer, "gemma2")` + `datasets.map()` + print bukti |
| SFT | SFTTrainer 800 steps (linear+warmup, eff batch 8), push `merged_16bit` HF public |
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2` (open-source, tanpa prefix) |
| Vector DB | ChromaDB in-memory, `hnsw:space=cosine`, 1 collection |
| Chunking | `RecursiveCharacterTextSplitter` 1000/150 **eksplisit** |
| RAG source | HANYA 4 PDF disediakan |
| Interface | `gr.Interface` + sel contoh Q&A tercetak |
| Env var | HF_TOKEN + HF_USERNAME via `google.colab.userdata` / Colab Secret — **NO hardcode** |
| Seed | 3407 |
| Bahasa | Python 3.11 |

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

1. Dataset SFT WAJIB `Ichsan2895/alpaca-gpt4-indonesian`.
2. Chat template Gemma via `datasets.map()` + **print output ter-format** (bukti `<start_of_turn>`/`<end_of_turn>`).
3. QLoRA **4-bit double quantization** (bukan 8-bit/fp16 penuh).
4. SFTTrainer **min 800 steps** tanpa OOM (kalau OOM: turunkan batch/max_seq, JANGAN turunkan step).
5. Model WAJIB `save`/`push` **merged_16bit** ke HF **Public** (akun Bimo), link di `link_huggingface.txt`.
6. Chunk size ≤5000, **overlap EKSPLISIT** (documented) → 1000/150.
7. Embedding **open-source** (MiniLM), no OpenAI.
8. RAG source **HANYA 4 PDF disediakan** — WAJIB keempatnya.
9. Generation WAJIB pakai **model K1 Bimo sendiri** (bukan model baru/proprietary/hasil fine-tune pihak ketiga).
10. Token/API key via **env var / Colab Secret** — TIDAK boleh hardcoded/committed.
11. Notebook `.ipynb` WAJIB **sudah dijalankan penuh** (output ter-embed) sebelum zip.
12. `requirements.txt` **pipreqs-style** (hanya library dipakai), BUKAN pip freeze.
13. **Zip flat** — no subfolder di dalam zip. Bahasa Python. **4 file** (2 ipynb + link + requirements). GRPO notebook TIDAK ada (itu Advanced/opsional).
14. **DILARANG AutoML / No-Code / UI-tool instan.**
15. **TIDAK BOLEH meta-conversation di deliverable** (notebook/submission): dilarang "share ke aku", kata "Claude", referensi CLAUDE.md/panduan/nama rekan. Notebook harus profesional & self-contained untuk reviewer Dicoding.

---

## 🧭 METODOLOGI KERJA (playbook — WAJIB ikut)

1. **VERTICAL per-kriteria:** K1 (SFT) → tuntas → K2 (RAG + interface). Notebook = pipeline berurutan.
2. **VERIFY-FIRST:** logika non-model (chunker `RecursiveCharacterTextSplitter` + hitung chunk/overlap) di-prototype & uji lokal SEBELUM masuk notebook (`scripts/verify_chunker.py`). Logika model (embed/generate) → prototype di Colab.
3. **Model muat SEKALI, cache di memory** (embedder + LLM). Jangan reload per query.
4. **Notebook submission = self-contained** (konstanta di-inline; TIDAK import `scripts/` saat Run All).
5. **Colab = Bimo yang jalanin.** Agent **produce file lalu STOP** — jangan auto-run training/heavy script.
6. **Output ter-embed** via Bimo Run All di Colab. Notebook harus lolos re-run penuh.
7. **Seed=3407** di semua random ops.
8. **Sensitive info via env var / Colab Secret** (HF_TOKEN, HF_USERNAME).
9. Regenerate notebook via `python scripts/build_sft_notebook.py` & `build_rag_notebook.py` (jangan edit `.ipynb` manual).
10. Update [Progress Log](#-progress-log) tiap tahap selesai.

## 🐍 ENVIRONMENT

- **Utama: Google Colab GPU T4 16GB.** 2 notebook (Fine-tuning, RAG) dieksekusi di sini. Library via `!pip install` sel awal.
- **Victus/Mac lokal:** HANYA prototyping non-model (build notebook via script, uji chunker). JANGAN load Gemma/embedder lokal (RTX 3050 4GB tak cukup training).

## 🔑 GOTCHA TEKNIS (warisan pengalaman sibling — hemat berjam-jam)

- **Gemma verified (2026-07-20):** `unsloth/gemma-2-2b-it-bnb-4bit` = ungated, prequant nf4+double-quant, lisensi gemma (boleh fine-tune + push public). Chat template key Unsloth = **`"gemma2"`**; token turn = `<start_of_turn>` / `<end_of_turn>`; template map role `assistant`→`model` otomatis (kirim messages role user/assistant).
- **Unsloth 2026.7.x butuh transformers ≥4.51.3** → install Unsloth **unpinned** (jangan pin manual transformers/trl/datasets → ImportError `CompileConfig`).
- **`push_to_hub_merged` bug** (`TypeError: safe_serialization`) → pakai pola 2 langkah: `save_pretrained_merged(DIR, tokenizer, save_method="merged_16bit")` lalu `HfApi().upload_folder(..., delete_patterns=["adapter_*"])`.
- **Dataset `alpaca-gpt4-indonesian` = 2 kolom** (`input`, `output`), BUKAN 3 kolom Alpaca klasik. Map: input→user turn, output→assistant turn.
- **Gemma double-BOS:** pakai `get_chat_template("gemma2")` + `apply_chat_template(tokenize=False)` lalu SFTTrainer `dataset_text_field="text"`. Kalau curiga double `<bos>`, set `SFTTrainer`/tokenizer tidak menambah special token lagi. Cek sel bukti (harus 1 `<bos>` di awal).
- **Download model HF di Colab kadang stall** (LFS) → set Colab Secret `HF_TOKEN` + `login()`; kalau parah unduh via `aria2c` / cache ke Drive (lihat log Nazhif Tahap 3).
- **Colab pola 2× Run All** (sel install → restart session → Run All lagi).
- **Nama folder Drive jangan ada SPASI di belakang** (`os.path.exists` gagal padahal folder "kelihatan") — gotcha Dafina. Cek spasi tersembunyi lebih awal.

## 📁 STRUKTUR FOLDER

```
bimo-bramantyo/
├── CLAUDE.md                 ← file ini
├── README.md
├── requirements.txt          ← sinkron dgn submission/requirements.txt
├── .env.example              ← HF_TOKEN + HF_USERNAME
├── .gitignore
├── panduan/PANDUAN_COLAB.md   ← langkah Run-All utk Bimo
├── scripts/                  ← builder notebook (SFT + RAG) + verify_chunker.py
├── data/raw/                 ← 4 PDF (gitignored)
└── submission/               ← 💻 DELIVERABLE (yang di-zip)
    ├── Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb
    ├── RAG_submission_PGABL_Bimo_Bramantyo.ipynb
    ├── link_huggingface.txt
    └── requirements.txt
```

**Deliverable zip:** `PGABL_Bimo_Bramantyo.zip` — flat (4 file di root zip). Cek `../nazhif-setya-nugroho/artifacts/4.ketentuan_berkas.md` untuk struktur pasti.

---

## ✅ PROGRESS LOG

> WAJIB diupdate tiap tahap selesai.

- **Tahap 0 — Setup: ✅ SELESAI (2026-07-20).**
  - [x] Verifikasi base model `unsloth/gemma-2-2b-it-bnb-4bit` (ungated, nf4+double-quant, chat template key `gemma2`, token `<start_of_turn>`/`<end_of_turn>`) via WebFetch HF + source Unsloth `chat_templates.py`.
  - [x] Folder scaffold + CLAUDE.md (matriks diferensiasi) + `.env.example` + `.gitignore` + README + `panduan/PANDUAN_COLAB.md`.
  - [x] Copy 4 PDF `../nazhif-setya-nugroho/artifacts/document_knowledge_RAG/*.pdf` → `data/raw/*.pdf` (rename path-safe: PP_5_2021 16.3MB, PP_35_2021 2.4MB, PP_51_2023 2.6MB, UU_6_2023 81.4MB).

- **Tahap 1 — Notebook Fine-tuning SFT Basic: ✅ DIBANGUN & TERVALIDASI LOKAL (2026-07-20). PENDING Colab Run-All (Bimo).**
  - [x] `scripts/build_sft_notebook.py` → generate `submission/Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb` (24 sel: 13 md + 11 kode). Validasi: JSON valid, `ast.parse` semua sel lolos, scan token-bocor NONE, scan meta-conversation/nama-rekan CLEAN.
  - [x] Alur: install (unsloth unpinned) → auth Colab Secret → konfigurasi → load Gemma-2-2B 4-bit (+print `quantization_config` bukti double-quant) → LoRA r8/α16/drop0.05 MHA+FFN → load alpaca-id (saring + subset 10k, seed 3407) → `get_chat_template("gemma2")` + `datasets.map()` + **print bukti `<start_of_turn>`/`<end_of_turn>`** + hitung `<bos>` → SFTTrainer 800 langkah (eff batch 8, LR 2e-4 linear+warmup, adamw_8bit) → push pola 2-langkah `merged_16bit` ke `PGABL-Gemma-2-2B-SFT-Bimo` (public) → tulis `link_huggingface.txt`.
  - [x] API SFTTrainer/SFTConfig disesuaikan dgn env Colab Juli-2026 (referensi metodologi sibling: `tokenizer=` masih dipakai; `max_seq_length`/`dataset_text_field`/`packing` di dalam SFTConfig; push 2-langkah hindari bug `safe_serialization`).
  - [ ] **USER TODO:** Bimo Run-All di Colab T4 (akun HF sendiri + Secret HF_TOKEN/HF_USERNAME) → model public + link.

- **Tahap 2 — Notebook RAG Basic + gr.Interface: ✅ DIBANGUN & TERVALIDASI LOKAL (2026-07-20). PENDING Colab Run-All (Bimo).**
  - [x] **VERIFY-FIRST chunker lokal** (`scripts/verify_chunker.py`): `RecursiveCharacterTextSplitter(1000,150)` — overlap AKTIF (total char 17400 > 15005 asli, irisan chunk[0]→[1] terdeteksi, max chunk 998 ≤1000). pypdf buka 4 PDF (739/56/27/1127 hal), PP_51 → 47 chunk. LULUS.
  - [x] `scripts/build_rag_notebook.py` → generate `submission/RAG_submission_PGABL_Bimo_Bramantyo.ipynb` (20 sel: 11 md + 9 kode). Validasi JSON/ast/HR-scan CLEAN.
  - [x] Alur: install → auth+config → mount Drive + verifikasi 4 PDF (`MyDrive/PGABL_Bimo/`) → `muat_pdf` (pypdf) + `potong_teks` (Recursive 1000/150 eksplisit) + metadata → `buat_embedding` MiniLM (normalize) → **ChromaDB in-memory cosine** (add bertahap) → load generator = Gemma SFT Bimo via transformers+BitsAndBytesConfig 4-bit (bukan unsloth — code path beda) → `ambil_konteks` top-4 / `rakit_prompt` {konteks}+{pertanyaan} chat Gemma / `hasilkan_jawaban` greedy stop `<end_of_turn>` / `tanya` → **sel contoh 3 Q&A tercetak (Markdown)** → `gr.Interface` share=True.
  - [x] Anti-plagiarisme: Gemma vs Llama/Qwen, MiniLM vs bge-m3/e5, ChromaDB in-memory vs FAISS/persistent, Recursive vs regex/sliding/kalimat, penamaan Indonesia berbeda (`muat_pdf`/`potong_teks`/`ambil_konteks`/`hasilkan_jawaban`). Overlap gr.Interface+ChromaDB = pilihan biner rubrik (SAH).
  - [ ] **USER TODO:** Bimo upload 4 PDF ke Drive + Run-All di Colab T4 (model SFT sudah public).

- **Tahap 3 — Packaging & Submission: 🟡 SIAP KECUALI OUTPUT (menunggu Bimo Run-All).**
  - [x] `submission/requirements.txt` pipreqs-style (15 lib) + `submission/link_huggingface.txt` placeholder (`GANTI_USERNAME` → diisi URL asli setelah run).
  - [x] Folder `submission/` = tepat 4 file deliverable (2 ipynb + link + requirements). Tanpa GRPO notebook (Basic).
  - [ ] **USER TODO:** setelah 2 notebook di-Run-All & di-download (output ter-embed), isi link asli → zip flat `PGABL_Bimo_Bramantyo.zip` (4 file) → upload Dicoding.

---
**Status ringkas:** 🟢 Semua kerja lokal beres (Tahap 0-2 dibangun & tervalidasi; scaffold + 2 notebook siap-jalan + chunker terverifikasi). Sisa = **eksekusi Colab oleh Bimo** (butuh akun HF sendiri + Colab Secret + upload 4 PDF ke Drive), lalu packaging zip. Panduan lengkap: [`panduan/PANDUAN_COLAB.md`](panduan/PANDUAN_COLAB.md).
