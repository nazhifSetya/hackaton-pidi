# CLAUDE.md — Asisten Legal Cipta Kerja (PGABL) — versi **Dafina (MINIMAL/BASIC)**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> Update bagian [Progress Log](#-progress-log) tiap satu tahap selesai.

---

## ⛔ SCOPE & TARGET

- Proyek: submission akhir Dicoding **"Pengembangan Generative AI Berbasis LLM (PGABL)"** — Asisten AI tim legal (SLM fine-tuned + RAG) untuk 4 regulasi Cipta Kerja.
- **Pemilik submission: Dafina Meira Rizkia** (rekan tim). Submission **TERPISAH** & independen.
- **TARGET NILAI: KRITERIA MINIMAL / BASIC saja (⭐⭐⭐ lulus).** BUKAN Skilled, BUKAN Advanced. Tujuan: cukup lulus, hemat waktu & compute.
- Proyek **self-contained** di folder ini. Aturan CLAUDE.md proyek lain (Everest/EBC/analisis-sentimen dll) TIDAK berlaku.
- **Nama untuk deliverable:** `Dafina_Meira_Rizkia` → file `..._PGABL_Dafina_Meira_Rizkia.ipynb`, zip `PGABL_Dafina_Meira_Rizkia.zip`.

## 🔴 ATURAN #1 — ANTI-PLAGIARISME (WAJIB, jangan dilanggar)

Ada **DUA** versi sibling di repo yang harus dijaga jaraknya:
- **Nazhif (Advanced, sudah DITERIMA):** [`../nazhif-setya-nugroho/`](../nazhif-setya-nugroho/)
- **Fareynaldi (Basic):** [`../fareynaldi-affan/`](../fareynaldi-affan/)

**Baca kedua versi HANYA untuk memahami rubrik + metodologi + gotcha teknis — DILARANG COPY-PASTE kode/notebook.** Dicoding mengecek kemiripan antar-submission; kalau notebook Dafina mirip salah satu → semua submission bisa kena reject/flag kolusi.

**Strategi diferensiasi Dafina = pilih opsi Basic yang SAH tapi BERBEDA dari kedua sibling.** Rubrik memang menyediakan pilihan di tier Basic (model boleh Llama/Qwen/Mistral/Gemma/Phi; vector DB boleh ChromaDB **atau FAISS**; interface boleh Gradio **atau loop `input()`**). Dafina ambil jalur yang berbeda — bukan obfuscation, tapi implementasi yang genuinely lain.

### 📊 MATRIKS DIFERENSIASI (jantung anti-plagiarisme — jaga tetap benar)

| Aspek | Nazhif (Advanced) | Fareynaldi (Basic) | **Dafina (Basic)** |
|---|---|---|---|
| Base model | Llama-3.2-3B | Llama-3.2-3B | **Qwen2.5-1.5B-Instruct** (Apache-2.0) |
| Chat template | Llama-3 | Llama-3 | **ChatML** (`get_chat_template("qwen-2.5")`) |
| Bukti special token | `<\|begin_of_text\|>` dll | `<\|begin_of_text\|>` dll | **`<\|im_start\|>`, `<\|im_end\|>`** |
| LoRA | r=16/32 | r=16 α=16 drop=0 | **r=8 α=32 drop=0.05** |
| LR / scheduler | 2e-4 linear | 3e-4 linear | **2e-4 cosine + warmup_ratio** |
| Optimizer | adamw_8bit | adamw_8bit | **paged_adamw_8bit** |
| Effective batch | — | 8 (2×4) | **16 (2×8)** |
| Subset dataset | full/2000 | 12k | **8k** |
| Embedder | bge-m3 | bge-m3 | **multilingual-e5-base** (prefix query/passage) |
| Vector DB | ChromaDB 18 col | ChromaDB 1 col | **FAISS `IndexFlatIP`** |
| Chunker | per-pasal regex | sliding window char | **berbasis-kalimat greedy + overlap ekor** |
| chunk / overlap | 1200 / 100 | 1000 / 100 | **700 / 120** |
| top_k | 5 | 4 | **3** |
| Interface (K3) | Gradio Blocks + citation | `gr.Interface` | **loop `input()` + `IPython.display.Markdown`** |
| Repo HF | `PGABL-Llama-3.2-3B-SFT` | `...-SFT-Fareynaldi` | **`PGABL-Qwen2.5-1.5B-SFT-Dafina`** |
| Gaya penamaan | campuran | Inggris (`retrieve`,`trainer`) | **Indonesia** (`cari`,`pelatih`,`tanya_regulasi`) |

- Akun & token Hugging Face **milik Dafina sendiri** (bukan akun Nazhif/Fareynaldi).
- 4 PDF regulasi = knowledge base yang DISEDIAKAN (sama untuk semua peserta) → boleh dipakai (bukan plagiarisme). Sumber: `../nazhif-setya-nugroho/artifacts/document_knowledge_RAG/*.pdf` → copy ke `data/raw/` dengan rename path-safe.

## 👤 USER & GAYA KERJA

- **Nama:** Dafina Meira Rizkia — dipakai di nama file submission (`_Dafina_Meira_Rizkia`).
- **Komunikasi (WAJIB):** Bahasa Indonesia simpel, pelan-pelan, step-by-step, jelaskan **KENAPA** tiap langkah. Teliti detail.
- **ASK, DON'T ASSUME:** kalau ambigu (username HF, dsb), TANYA dulu SEBELUM nulis kode.

---

## 🎯 YANG DIBANGUN — hanya tier BASIC tiap kriteria

### K1 — SLM Fine-tuning (BASIC, 2 pts)
- Load `unsloth/Qwen2.5-1.5B-Instruct` **4-bit** (QLoRA double quantization, `nf4`, compute `bfloat16`).
- LoRA di target **MHA+FFN** (`q,k,v,o,gate,up,down`), r=8 α=32.
- Chat template **ChatML** (`get_chat_template(tokenizer, "qwen-2.5")`) ke dataset `Ichsan2895/alpaca-gpt4-indonesian` via `datasets.map()`, lalu **PRINT satu contoh baris terformat** (harus terlihat `<|im_start|>` & `<|im_end|>`) → **BUKTI WAJIB**.
- `SFTTrainer` **800 steps** (effective batch 16, cosine) tanpa OOM.
- Push model ke HF **PUBLIC** (akun Dafina) dengan `merged_16bit` → link di `submission/link_huggingface.txt`.
- **CUKUP 1 eksperimen.** ❌ JANGAN train/val split + `eval_strategy` + eksperimen ke-2 (Skilled). ❌ JANGAN GRPO (Advanced).

### K2 — Sistem RAG (BASIC, 2 pts)
- Loader **4 PDF** (`pypdf`) per-halaman.
- Chunker **berbasis-kalimat**: rangkai kalimat utuh sampai ≈`chunk_size=700`, overlap `120` dari ekor chunk sebelumnya — **EKSPLISIT** (bukan default library), didokumentasikan.
- Embedder `intfloat/multilingual-e5-base` (open-source, no OpenAI) — **wajib prefix** `query: ` / `passage: `.
- **FAISS `IndexFlatIP`** atas vektor ter-normalisasi (= cosine), indeks disimpan lokal — CUKUP 1 indeks.
- Retriever **top-3 dense** → prompt `{konteks}` + `{pertanyaan}` → generate pakai **model K1** (bukan model proprietary).
- ❌ JANGAN: metadata filtering, ensemble BM25, parent-child, HyDE, reranker, threshold, DDG fallback (semua Skilled/Advanced).

### K3 — Antarmuka (BASIC, 2 pts)
- Loop `input()` interaktif + `IPython.display.Markdown` (opsi Basic selain Gradio). Ada juga sel demo batch 4 pertanyaan (selalu jalan saat Run All → output ter-embed).
- ❌ JANGAN `gr.Blocks` + chat history + citation panel + streaming (Skilled/Advanced).

---

## 📋 KEPUTUSAN TERKUNCI (jangan diubah tanpa konfirmasi Dafina)

| Aspek | Keputusan |
|---|---|
| Target nilai | **BASIC (⭐⭐⭐ lulus)** — semua kriteria cukup Basic |
| Environment berat | **Google Colab T4 16 GB** (free tier) |
| SLM base | `unsloth/Qwen2.5-1.5B-Instruct` (Apache-2.0, 4-bit QLoRA) |
| Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` (LOCKED rubric; **2 kolom** `input`+`output`) |
| Chat template | ChatML via `get_chat_template("qwen-2.5")` + `datasets.map()` + print bukti |
| SFT | SFTTrainer 800 steps (cosine, eff batch 16), push `merged_16bit` HF public |
| Embedding | `intfloat/multilingual-e5-base` (open-source, prefix query/passage) |
| Vector DB | FAISS `IndexFlatIP`, 1 indeks lokal |
| Chunking | berbasis-kalimat, `chunk_size 700`, overlap `120` **eksplisit** |
| RAG source | HANYA 4 PDF disediakan |
| Interface | loop `input()` + `IPython.display.Markdown` |
| Env var | HF_TOKEN + HF_USERNAME via `google.colab.userdata` / Colab Secret — **NO hardcode** |
| Seed | 42 |
| Bahasa | Python 3.11 |

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

1. Dataset SFT WAJIB `Ichsan2895/alpaca-gpt4-indonesian`.
2. Chat template ChatML via `datasets.map()` + **print output ter-format** (bukti `<|im_start|>`/`<|im_end|>`).
3. QLoRA **4-bit double quantization** (bukan 8-bit/fp16 penuh).
4. SFTTrainer **min 800 steps** tanpa OOM (kalau OOM: turunkan batch/max_seq, JANGAN turunkan step).
5. Model WAJIB `save`/`push` **merged_16bit** ke HF **Public** (akun Dafina), link di `link_huggingface.txt`.
6. Chunk size ≤5000, **overlap EKSPLISIT** (documented) → 700/120.
7. Embedding **open-source** (e5-base), no OpenAI.
8. RAG source HANYA 4 PDF disediakan.
9. Token/API key via **env var / Colab Secret** — TIDAK boleh hardcoded/committed.
10. Notebook `.ipynb` WAJIB **sudah dijalankan penuh** (output ter-embed) sebelum zip.
11. `requirements.txt` **pipreqs-style** (hanya library dipakai), BUKAN pip freeze.
12. **Zip flat** — no subfolder di dalam zip. Bahasa Python.
13. **DILARANG AutoML / No-Code / UI-tool instan.**
14. **TIDAK BOLEH meta-conversation di deliverable** (notebook/submission): dilarang "share ke aku", kata "Claude", referensi CLAUDE.md/panduan/nama rekan. Notebook harus profesional & self-contained untuk reviewer Dicoding.

---

## 🧭 METODOLOGI KERJA (playbook — WAJIB ikut)

1. **VERTICAL per-kriteria:** K1 (SFT) → tuntas → K2 (RAG) → K3 (interface). Notebook = pipeline berurutan.
2. **VERIFY-FIRST:** logika non-model (chunker berbasis-kalimat) di-prototype & uji lokal SEBELUM masuk notebook (sudah dilakukan via `scratchpad/verify_dafina.py`: overlap aktif + guard anti-infinite-loop terbukti). Logika model (embed/generate) → prototype di Colab.
3. **Model muat SEKALI, cache di memory** (e5 + LLM). Jangan reload per query.
4. **Config-driven:** magic number di `configs/*.yaml`. Notebook submission = self-contained (konstanta di-inline; TIDAK import `src/`/`configs/` saat Run All).
5. **Colab = Dafina yang jalanin.** Agent **produce file lalu STOP** — jangan auto-run training/heavy script.
6. **Output ter-embed** via user Run All di Colab. Notebook harus lolos re-run penuh.
7. **Seed=42** di semua random ops.
8. **Sensitive info via env var / Colab Secret** (HF_TOKEN, HF_USERNAME).
9. Regenerate notebook via `python scripts/build_sft_notebook.py` & `build_rag_notebook.py` (jangan edit `.ipynb` manual).
10. Update [Progress Log](#-progress-log) tiap tahap selesai.

## 🐍 ENVIRONMENT

- **Utama: Google Colab GPU T4 16GB.** 2 notebook (Fine-tuning, RAG) dieksekusi di sini. Library via `!pip install` sel awal.
- **Victus/Mac lokal:** HANYA prototyping non-model (build notebook via script, uji chunker). JANGAN load Qwen/e5 lokal (RTX 3050 4GB tak cukup training).

## 🔑 GOTCHA TEKNIS (warisan pengalaman Nazhif — hemat berjam-jam)

- **Unsloth 2026.7.x butuh transformers ≥4.51.3** → install Unsloth **unpinned** (jangan pin manual transformers/trl/datasets → ImportError `CompileConfig`).
- **`push_to_hub_merged` bug** (`TypeError: safe_serialization`) → pakai pola 2 langkah: `save_pretrained_merged(DIR, tokenizer, save_method="merged_16bit")` lalu `HfApi().upload_folder(..., delete_patterns=["adapter_*"])`.
- **Dataset `alpaca-gpt4-indonesian` = 2 kolom** (`input`, `output`), BUKAN 3 kolom Alpaca klasik.
- **`apply_chat_template(return_tensors="pt")`** di transformers 5.x kadang balikin dict → di notebook RAG kita render prompt ke **string** dulu (`tokenize=False`) baru `tokenizer(prompt, return_tensors="pt")` (hindari gotcha).
- **e5 wajib prefix**: dokumen `"passage: "`, kueri `"query: "` — kalau lupa, retrieval drop.
- **Download model HF di Colab kadang stall** → set Colab Secret `HF_TOKEN` + `login()`; kalau parah, unduh via `aria2c` / cache ke Drive (lihat log Nazhif).
- **Colab pola 2× Run All** (sel install → restart session → Run All lagi).
- **Qwen2.5 = ChatML**: token spesial `<|im_start|>` / `<|im_end|>` (beda dari Llama-3). Ini yang dicek di sel bukti.

## 📁 STRUKTUR FOLDER

```
dafina/
├── CLAUDE.md                 ← file ini
├── README.md
├── requirements.txt          ← sinkron dgn submission/requirements.txt
├── .env.example              ← HF_TOKEN + HF_USERNAME
├── .gitignore
├── configs/                  ← config-driven (model/training/rag)
├── src/{data,rag}/           ← placeholder modular
├── scripts/                  ← builder notebook (SFT + RAG)
├── notebooks/                ← (kosong; notebook kerja opsional)
├── data/{raw,processed}/     ← 4 PDF (gitignored) + output
├── outputs/samples/          ← hasil verify
└── submission/               ← 💻 DELIVERABLE (yang di-zip)
    ├── Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb
    ├── RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb
    ├── link_huggingface.txt
    └── requirements.txt
```

**Deliverable zip:** `PGABL_Dafina_Meira_Rizkia.zip` — flat (4 file di root zip). Cek `../nazhif-setya-nugroho/artifacts/4.ketentuan_berkas.md` untuk struktur pasti.

---

## ✅ PROGRESS LOG

> WAJIB diupdate tiap tahap selesai.

- **Tahap 0 — Setup: ✅ SELESAI (2026-07-19).**
  - [x] Folder scaffold (`configs/`, `src/`, `scripts/`, `data/`, `outputs/`, `submission/`) + `.gitignore` + `.env.example` + `README.md`.
  - [x] Verifikasi base model: `unsloth/Qwen2.5-1.5B-Instruct` **Apache-2.0**, ungated, ChatML, kompatibel Unsloth 4-bit (via WebFetch HF). Dipilih varian **1.5B** (bukan 3B yang berlisensi qwen-research/non-komersial) demi lisensi bersih untuk push repo publik + lebih ringan/cepat di T4.
  - [x] Config skeleton (`configs/{model,training,rag}_config.yaml`) — nilai Basic Dafina (LoRA r8/α32, SFT 800 step LR 2e-4 cosine, e5-base, FAISS, chunk 700/overlap 120, top-k 3).

- **Tahap 1 — Notebook Fine-tuning SFT Basic: ✅ RUN & VERIFIED (2026-07-19).** Model live & public di HF: `dafina1907/PGABL-Qwen2.5-1.5B-SFT-Dafina` — file `model.safetensors` **3.09 GB** (merged_16bit penuh, BUKAN adapter) + config/tokenizer/chat_template.jinja, tag `qwen2`, VERIFIED. HR-5 terpenuhi. `link_huggingface.txt` lokal sudah diisi URL asli.
  - [x] `submission/Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb` di-generate via `scripts/build_sft_notebook.py` (24 cell: 13 md + 11 code, JSON valid, syntax 0-error).
  - [x] Alur linear single-experiment: setup → auth → load Qwen 4-bit (QLoRA nf4 + double quant) → LoRA MHA+FFN 7 target → load alpaca-id (subset 8k) → `get_chat_template("qwen-2.5")` + `datasets.map()` + **print bukti `<|im_start|>`/`<|im_end|>`** → `SFTTrainer` 800 step (eff batch 16, cosine, paged_adamw_8bit) → push pola 2-langkah `merged_16bit` → tulis `link_huggingface.txt`.
  - [x] Anti-plagiarisme diverifikasi (lihat matriks): Qwen vs Llama, ChatML vs Llama-3, r8/α32, cosine, paged_adamw, penamaan variabel Indonesia. HR-14 scan CLEAN.
  - [x] **DONE (2026-07-19)**: user Run All di Colab T4 (akun HF `dafina1907`, HF_USERNAME=`dafina1907`). Training 800 step sukses, merge + push `merged_16bit` ke HF public terverifikasi via UI HF (model.safetensors 3.09 GB, tag qwen2, VERIFIED).
  - [ ] **USER TODO tersisa**: download notebook SFT (yang SUDAH ada output) dari Colab → timpa file lokal `submission/` (Colab "Save failed" = gagal autosave ke Drive, BUKAN gagal training; wajib download manual).

- **Tahap 2 — Notebook RAG Basic + input() loop: ✅ RUN & VERIFIED (2026-07-19).** Notebook RAG di-Run All di Colab T4 (380 KB, 13/13 code cell tereksekusi, output ter-embed). Terverifikasi: tak ada token bocor, tak ada sel error, semua tahap ada bukti (PDF [OK]→chunk→embed e5→FAISS→retrieval skor→jawaban→antarmuka input() 4× tanya-jawab), HR-14 bersih.
  - [x] `submission/RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb` di-generate via `scripts/build_rag_notebook.py` (28 cell: 15 md + 13 code, JSON valid, syntax 0-error).
  - [x] Alur: setup + secrets → mount Drive & verify 4 PDF di `MyDrive/PGABL_Dafina/` → pypdf per-halaman → **chunker berbasis-kalimat `700/120` (EKSPLISIT)** + sel bukti overlap → embed `e5-base` (prefix passage/query) → **FAISS `IndexFlatIP` disimpan lokal** → retriever top-3 → generator = Qwen SFT dari HF (4-bit) → demo batch 4 query (Markdown) → **loop `input()` interaktif** (EOFError-safe).
  - [x] Chunker di-VERIFY lokal (`scratchpad/verify_dafina.py`): 3 kasus (normal/kalimat-panjang/kosong) → overlap terbukti, tidak infinite-loop, chunk terbatas.
  - [x] Anti-plagiarisme: e5 vs bge-m3, FAISS vs ChromaDB, chunker kalimat vs char-window/regex, `input()` loop vs Gradio, penamaan Indonesia. HR-14 scan CLEAN.
  - [x] **DONE (2026-07-19)**: user upload 4 PDF ke Drive `MyDrive/PGABL_Dafina/` + Run All di Colab T4. Sel `input()` loop diisi 3-4 pertanyaan hukum + `keluar` → transkrip ter-embed.
  - **Gotcha lapangan (teratasi, catat untuk sibling):** (1) mount Drive basi → butuh runtime fresh; (2) `force_remount=True` malah `ValueError: mount failed` di runtime fresh → dikembalikan ke `drive.mount("/content/drive")` biasa (paling andal); (3) **BIANG UTAMA = nama folder Drive ketik dgn SPASI di belakang (`PGABL_Dafina `)** → `os.path.exists` gagal padahal folder "kelihatan" → rename hapus spasi → langsung kebaca. Cek spasi tersembunyi lebih awal!

- **Tahap 3 — Packaging & Submission: ✅ SELESAI (2026-07-19) — ZIP SIAP UPLOAD.**
  - [x] 2 notebook tereksekusi (output ter-embed) di `submission/`: Fine-tuning (198 KB) + RAG (380 KB). Catatan: Colab download SFT pakai underscore (`Fine_tuning`) → di-rename ke hyphen (`Fine-tuning`) sesuai rubrik.
  - [x] `link_huggingface.txt` = URL asli `https://huggingface.co/dafina1907/PGABL-Qwen2.5-1.5B-SFT-Dafina`.
  - [x] `submission/requirements.txt` pipreqs-style (13 lib). **No gradio, no chromadb** (beda stack dari Fareynaldi).
  - [x] Audit HR1-14 SEMUA PASS: HR-5 model merged_16bit public (model.safetensors 3.09 GB, tag qwen2, verified via UI HF), HR-9 no token leak (scan bersih), HR-10 output ter-embed (kedua notebook), HR-14 meta-conversation bersih, HR-11 requirements pipreqs.
  - [x] **Zip flat dibuat**: `dafina/PGABL_Dafina_Meira_Rizkia.zip` (49 KB) — verified 4 file di root, NOL subfolder (HR-12).
  - [ ] **USER TODO tersisa**: upload `PGABL_Dafina_Meira_Rizkia.zip` ke Dicoding.

---
**Status ringkas:** ✅ SELESAI DIKERJAKAN. K1 SFT + K2 RAG + K3 antarmuka semua Run All di Colab & terverifikasi (output ter-embed, HR1-14 pass, anti-plagiarisme aman vs Nazhif/Fareynaldi). Model publik di HF (`dafina1907`). Zip flat `PGABL_Dafina_Meira_Rizkia.zip` (49 KB) siap. Blocker terakhir = user upload zip ke Dicoding.
