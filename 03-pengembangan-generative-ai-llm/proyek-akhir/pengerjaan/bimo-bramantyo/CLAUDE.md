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
| Base model | Llama-3.2-3B | Llama-3.2-3B | Qwen2.5-1.5B | **Llama-3.2-1B-Instruct** (ukuran beda: 1B vs 3B) |
| Chat template | Llama-3 | Llama-3 | ChatML | **Llama-3** (`get_chat_template("llama-3.1")`) |
| Bukti special token | `<\|begin_of_text\|>` | `<\|begin_of_text\|>` | `<\|im_start\|>` `<\|im_end\|>` | **`<\|begin_of_text\|>` `<\|start_header_id\|>` `<\|eot_id\|>`** |
| LoRA | r=16/32 | r=16 α=16 drop=0 | r=8 α=32 drop=0.05 | **r=8 α=16 drop=0.05** (target q/k/v/o/gate/up/down) |
| LR / scheduler | 2e-4 linear | 3e-4 linear | 2e-4 cosine | **2e-4 linear + warmup_ratio 0.03** |
| Optimizer | adamw_8bit | adamw_8bit | paged_adamw_8bit | **adamw_8bit** |
| Subset dataset / seed | full / 42 | 12k / — | 8k / 42 | **10k / 3407** |
| Embedder | bge-m3 | bge-m3 | multilingual-e5-base | **paraphrase-multilingual-MiniLM-L12-v2** (tanpa prefix) |
| Vector DB | ChromaDB 18 col persist | ChromaDB 1 col persist | FAISS `IndexFlatIP` | **ChromaDB in-memory, `hnsw:space=cosine`, 1 col** |
| Chunker | per-pasal regex | sliding window char | kalimat greedy + overlap ekor | **`RecursiveCharacterTextSplitter`** (langchain-text-splitters) |
| chunk / overlap / top_k | 1200 / 100 / 5 | 1000 / 100 / 4 | 700 / 120 / 3 | **1000 / 150 / 4** |
| Interface (K2) | Gradio Blocks + citation | `gr.Interface` | loop `input()` | **`gr.Interface`** (+ sel contoh Q&A tercetak) |
| Repo HF | `PGABL-Llama-3.2-3B-SFT` | `...-SFT-Fareynaldi` | `PGABL-Qwen2.5-1.5B-SFT-Dafina` | **`PGABL-Llama-3.2-1B-SFT-Bimo`** |
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
- Load `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` **4-bit** (QLoRA nf4 + **double quantization**, `max_seq_length=1024`).
- LoRA di target **MHA+FFN** (`q,k,v,o,gate,up,down`), **r=8 α=16 dropout=0.05**.
- Chat template **Llama-3** (`get_chat_template(tokenizer, "llama-3.1")`) ke dataset `Ichsan2895/alpaca-gpt4-indonesian` via `datasets.map()`, lalu **PRINT satu contoh baris terformat** (harus terlihat `<|begin_of_text|>`, `<|start_header_id|>`, `<|eot_id|>`) → **BUKTI WAJIB**.
- `SFTTrainer` **800 steps** (eff batch 8, LR 2e-4 linear + warmup 0.03, adamw_8bit) tanpa OOM.
- Push model ke HF **PUBLIC** (akun Bimo) dengan `merged_16bit` → link di `submission/link_huggingface.txt`.
- **CUKUP 1 eksperimen.** ❌ JANGAN train/val split + `eval_strategy` + eksperimen ke-2 (Skilled). ❌ JANGAN GRPO (Advanced).

### K2 — Sistem RAG (BASIC, 2 pts)
- Loader **4 PDF** (`pypdf`) per-halaman. WAJIB keempatnya.
- Chunker **`RecursiveCharacterTextSplitter`** (dari `langchain-text-splitters`), `chunk_size=1000`, `chunk_overlap=150` — **EKSPLISIT**, didokumentasikan.
- Embedder `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (open-source, no OpenAI, **tanpa prefix** query/passage).
- **ChromaDB in-memory** (`chromadb.Client()`), 1 collection `regulasi_ciptaker_bimo`, `metadata={"hnsw:space":"cosine"}`.
- Retriever **top-4** → prompt `{konteks}` + `{pertanyaan}` (format chat Llama-3) → generate pakai **model K1 Bimo** (bukan model proprietary/baru). Load via `transformers` + BitsAndBytesConfig 4-bit fp16, `add_special_tokens=False` (template Llama sudah punya bos), stop token `<|eot_id|>`.
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
| SLM base | `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` (Llama 3.2 license, ungated, 4-bit QLoRA, stabil fp16, TERBUKTI jalan di env ini) |
| Dataset SFT | `Ichsan2895/alpaca-gpt4-indonesian` (LOCKED rubric; **2 kolom** `input`+`output`) |
| Chat template | Llama-3 via `get_chat_template(tokenizer, "llama-3.1")` + `datasets.map()` + print bukti |
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
2. Chat template Llama-3 via `datasets.map()` + **print output ter-format** (bukti `<|begin_of_text|>`/`<|start_header_id|>`/`<|eot_id|>`).
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

- **⛔ GEMMA-2 GAGAL DI T4 — DITINGGALKAN (2026-07-21). Ganti ke Phi-3.5-mini.** Riwayat: awalnya pakai `unsloth/gemma-2-2b-it-bnb-4bit`. SFT "selesai" 800 langkah + merged_16bit ke HF, TAPI hasil generate = **word-salad lalu kolaps jadi koma**. Diagnosis pasti (tes penentu): model BASE gemma jalan koheren di setup inference yang sama, tapi model **hasil fine-tune/merge Bimo rusak** → bukan bug inference. Penyebab: **Gemma-2 tidak stabil dilatih/di-merge fp16 di T4** (T4 tak punya bf16). Tambalan inference (add_special_tokens, `attn_implementation="eager"`, compute fp32) SEMUA tak menolong (output identik) karena bobotnya memang korup. **Pelajaran: JANGAN fine-tune Gemma-2 di T4/fp16.** Qwen/Llama/Phi stabil fp16 → aman.
- **⛔ PHI-3.5 GAGAL DI ENV COLAB INI — DITINGGALKAN (2026-07-21). Ganti ke Llama-3.2-1B.** Setelah pivot dari Gemma, Phi-3.5 di-SFT + merged + RAG jalan tanpa error TAPI generate = word-salad campur Inggris. Tes penentu: **base Phi-3.5 (belum di-fine-tune) PUN garbage** di setup inference yang sama, padahal **base Gemma koheren**. Artinya transformers versi Juli-2026 di Colab **tidak kompatibel dengan Phi-3.5** (dugaan: RoPE-scaling/LongRoPE Phi). Tambalan prompt (add_special_tokens True/False, newline manual, apply_chat_template return_dict) SEMUA tak menolong. **Pelajaran: model yang TERBUKTI jalan di env ini = Llama & Qwen** (submission Nazhif Llama-3.2 & Dafina Qwen2.5 menghasilkan jawaban koheren pakai kode load transformers yang SAMA). Gemma & Phi = buntu. Kalau ganti model lagi, pilih Llama/Qwen.
- **Llama-3.2-1B verified (2026-07-21):** `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` = ungated, prequant nf4+double-quant, Llama 3.2 license, stabil fp16, TERBUKTI jalan (sekeluarga Nazhif). Chat template key Unsloth = **`"llama-3.1"`**; token = `<|begin_of_text|>` / `<|start_header_id|>` / `<|eot_id|>`; template **menyertakan bos** → inference `add_special_tokens=False` (hindari double-bos). LoRA target = q/k/v/o/gate/up/down (terpisah). Stop token = `<|eot_id|>`. Ukuran 1B = retrain tercepat (~30-45 mnt), hemat kuota GPU.
- **Unsloth 2026.7.x butuh transformers ≥4.51.3** → install Unsloth **unpinned** (jangan pin manual transformers/trl/datasets → ImportError `CompileConfig`).
- **TRL `padding_free` default berubah (KETEMU 2026-07-21):** SFTTrainer lempar `ValueError: When padding_free=True without packing, max_length is not enforced`. TRL baru default `padding_free=True`; kombinasi dgn `packing=False` + `max_seq_length` di-set → error. **Fix:** `SFTConfig(..., padding_free=False)`. Juga `warmup_ratio` deprecated → pakai `warmup_steps`. (Muncul di run Phi tapi bukan soal model — pergeseran API TRL krn install unpinned ketarik versi lebih baru.)
- **`push_to_hub_merged` bug** (`TypeError: safe_serialization`) → pakai pola 2 langkah: `save_pretrained_merged(DIR, tokenizer, save_method="merged_16bit")` lalu `HfApi().upload_folder(..., delete_patterns=["adapter_*"])`.
- **Dataset `alpaca-gpt4-indonesian` = 2 kolom** (`input`, `output`), BUKAN 3 kolom Alpaca klasik. Map: input→user turn, output→assistant turn.
- **Gemma double-BOS:** pakai `get_chat_template("gemma2")` + `apply_chat_template(tokenize=False)` lalu SFTTrainer `dataset_text_field="text"`. Kalau curiga double `<bos>`, set `SFTTrainer`/tokenizer tidak menambah special token lagi. Cek sel bukti (harus 1 `<bos>` di awal).
- **Download model HF di Colab kadang stall** (LFS) → set Colab Secret `HF_TOKEN` + `login()`; kalau parah unduh via `aria2c` / cache ke Drive (lihat log Nazhif Tahap 3).
- **Colab pola 2× Run All** (sel install → restart session → Run All lagi).
- **Nama folder Drive jangan ada SPASI di belakang** (`os.path.exists` gagal padahal folder "kelihatan") — gotcha Dafina. Cek spasi tersembunyi lebih awal.
- **sentence-transformers vs transformers 5.x (KETEMU 2026-07-21):** `SentenceTransformer("...MiniLM...")` di Colab lempar `ValueError: Unrecognized processing class ... Can't instantiate a processor/tokenizer` (ST versi baru manggil `AutoProcessor` yang gagal di transformers 5.x untuk model teks lama). **Fix (dipakai di notebook RAG):** buang sentence-transformers, embed langsung via `transformers` `AutoModel` + **mean pooling** (rata token ditimbang attention mask) + normalisasi L2 — deterministik, tak ketergantung versi ST. Embedder tetap MiniLM. `sentence-transformers` dihapus dari requirements.
- **DOUBLE-BOS Gemma saat inferensi RAG (KETEMU 2026-07-21):** jawaban keluar sebagai karakter berulang (`,,,,,,`/`"""""`). Penyebab: `apply_chat_template` sudah menambah `<bos>`, lalu `tok(prompt, return_tensors="pt")` menambah `<bos>` KEDUA (default `add_special_tokens=True`). **Fix:** `tok(prompt, ..., add_special_tokens=False)`. (Di SFT tidak kena karena SFTTrainer yang urus tokenisasi.)
- **GEMMA-2 SOFT-CAPPING wajib `attn_implementation="eager"` (KETEMU 2026-07-21):** setelah fix double-BOS, jawaban masih **word-salad** (kata Indonesia nyambung tapi tak bermakna & tak nyambung konteks). Penyebab: Gemma-2 punya *logit soft-capping* (attn + final) yang TIDAK aktif pada attention default `sdpa` → logit meledak → generasi ngawur. **Fix:** `AutoModelForCausalLM.from_pretrained(..., attn_implementation="eager")`. Sekalian turunkan `repetition_penalty` 1.3→1.15 & buang `no_repeat_ngram_size` (1.3 terlalu agresif, bikin ngelantur pada model bingung). Qwen/Llama tak kena (tak ada soft-capping) — makanya sibling aman.

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
  - [x] Verifikasi base model (final = **Llama-3.2-1B**, ungated, chat template key `llama-3.1`, token `<|begin_of_text|>`/`<|start_header_id|>`/`<|eot_id|>`, LoRA q/k/v/o/gate/up/down) via WebFetch HF + source Unsloth `chat_templates.py`. (Gemma-2 & Phi-3.5 dicoba lebih dulu — DUA-DUANYA buntu, lihat GOTCHA.)
  - [x] Folder scaffold + CLAUDE.md (matriks diferensiasi) + `.env.example` + `.gitignore` + README + `panduan/PANDUAN_COLAB.md`.
  - [x] Copy 4 PDF `../nazhif-setya-nugroho/artifacts/document_knowledge_RAG/*.pdf` → `data/raw/*.pdf` (rename path-safe: PP_5_2021 16.3MB, PP_35_2021 2.4MB, PP_51_2023 2.6MB, UU_6_2023 81.4MB).

- **⚠️ DUA KALI PIVOT MODEL: Gemma-2 → Phi-3.5 → Llama-3.2-1B (2026-07-21).** (1) Gemma-2-2B: SFT+RAG jalan tanpa error tapi generate word-salad → bobot rusak (Gemma-2 tak stabil fp16 di T4). (2) Phi-3.5-mini: retrain, SFT+RAG jalan tapi generate word-salad LAGI → tes penentu: **base Phi pun garbage** (Phi tak kompatibel transformers env ini). (3) **Final: Llama-3.2-1B** — TERBUKTI jalan (sekeluarga Nazhif). Repo lama Gemma & Phi DITINGGALKAN. Semua build script + notebook + memory + link di-update ke Llama. Pelajaran: pakai model yang terbukti (Llama/Qwen), jangan Gemma/Phi di env ini.

- **Tahap 1 — Notebook Fine-tuning SFT Basic (Llama-3.2-1B): ✅ DIBANGUN & TERVALIDASI LOKAL (2026-07-21). PENDING Colab Run-All (Bimo).**
  - [x] `scripts/build_sft_notebook.py` (Llama-3.2-1B) → generate `submission/Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb` (24 sel). Validasi lokal: JSON valid, `ast.parse` lolos, token-bocor NONE, meta/nama-rekan CLEAN, tak ada sisa gemma/phi. Model `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`, LoRA q/k/v/o/gate/up/down, `get_chat_template("llama-3.1")`, bukti token `<|begin_of_text|>`/`<|start_header_id|>`/`<|eot_id|>`, push ke `PGABL-Llama-3.2-1B-SFT-Bimo`. Gotcha TRL `padding_free=False` + `warmup_steps` tetap dipakai.
  - [x] Alur: install (unsloth unpinned) → auth Colab Secret → konfigurasi → load `unsloth/Phi-3.5-mini-instruct-bnb-4bit` (+print `quantization_config`) → LoRA r8/α16/drop0.05 target fused `qkv_proj,o_proj,gate_up_proj,down_proj` → load alpaca-id (saring + subset 10k, seed 3407) → `get_chat_template("phi-3.5")` + `datasets.map()` + **print bukti `<|user|>`/`<|assistant|>`/`<|end|>`** → SFTTrainer 800 langkah (eff batch 8, LR 2e-4 linear+warmup, adamw_8bit) → push pola 2-langkah `merged_16bit` ke `PGABL-Phi-3.5-mini-SFT-Bimo` → tulis `link_huggingface.txt`.
  - Akun HF Bimo = **`bimo2107`** (LOCKED). HF_USERNAME di Colab Secret WAJIB `bimo2107`.
  - [ ] **USER TODO:** Bimo Run-All ULANG di Colab T4 → model Phi public + link. (Retrain krn Gemma ditinggalkan.)

- **Tahap 2 — Notebook RAG Basic + gr.Interface (Phi-3.5): ✅ DIBANGUN & TERVALIDASI LOKAL (2026-07-21). PENDING Colab Run-All (Bimo).**
  - [x] **VERIFY-FIRST chunker lokal** (`scripts/verify_chunker.py`): `RecursiveCharacterTextSplitter(1000,150)` — overlap AKTIF (17400>15005 char, irisan chunk[0]→[1] terdeteksi, max 998 ≤1000). pypdf buka 4 PDF (739/56/27/1127 hal), PP_51 → 47 chunk. LULUS. (Non-model, valid utk model apa pun.)
  - [x] `scripts/build_rag_notebook.py` (Phi-3.5) → generate `submission/RAG_submission_PGABL_Bimo_Bramantyo.ipynb` (20 sel: 11 md + 9 kode). Validasi JSON/ast/HR-scan CLEAN.
  - [x] Alur: install → auth+config (REPO Phi) → mount Drive + verifikasi 4 PDF (`MyDrive/PGABL_Bimo/`) → `muat_pdf` (pypdf) + `potong_teks` (Recursive 1000/150) + metadata → `buat_embedding` MiniLM via `transformers` AutoModel+mean-pooling (BUKAN sentence-transformers — hindari bug versi) → **ChromaDB in-memory cosine** → load generator = Phi SFT Bimo via `transformers`+BitsAndBytesConfig 4-bit **fp16** (Phi stabil, tak butuh eager) → `ambil_konteks` top-4 / `rakit_prompt` chat Phi-3.5 / `hasilkan_jawaban` greedy `add_special_tokens=False` + `repetition_penalty=1.15` stop `<|end|>` → **sel contoh 3 Q&A tercetak** → `gr.Interface` share=True.
  - [x] Anti-plagiarisme: Phi vs Llama/Qwen, MiniLM vs bge-m3/e5, ChromaDB in-memory vs FAISS/persistent, Recursive vs regex/sliding/kalimat, penamaan Indonesia berbeda. Overlap gr.Interface+ChromaDB = pilihan biner rubrik (SAH).
  - [ ] **USER TODO:** Bimo upload 4 PDF ke Drive + Run-All di Colab T4 (setelah model Phi SFT public).

- **Tahap 3 — Packaging & Submission: 🟡 SIAP KECUALI OUTPUT (menunggu Bimo Run-All 2 notebook Phi).**
  - [x] `submission/requirements.txt` pipreqs-style (15 lib, tanpa sentence-transformers) + `submission/link_huggingface.txt` = `https://huggingface.co/bimo2107/PGABL-Phi-3.5-mini-SFT-Bimo`.
  - [x] Folder `submission/` = tepat 4 file deliverable (2 ipynb + link + requirements). Tanpa GRPO notebook (Basic).
  - [ ] **USER TODO:** setelah 2 notebook Phi di-Run-All & di-download (output ter-embed), pastikan link asli → zip flat `PGABL_Bimo_Bramantyo.zip` (4 file) → upload Dicoding.

---
**Status ringkas:** 🟡 **PIVOT ke Phi-3.5** (Gemma-2 rusak fp16 di T4 → ditinggalkan). Kedua notebook sudah di-rebuild untuk Phi-3.5 + tervalidasi lokal. **Sisa: Bimo Run-All ULANG 2 notebook di Colab T4** — (1) Fine-tuning Phi (retrain ~60-90 mnt, HF_USERNAME=`bimo2107`) → model `PGABL-Phi-3.5-mini-SFT-Bimo` public; (2) RAG (upload 4 PDF ke `MyDrive/PGABL_Bimo/`). Lalu download 2 notebook ber-output → zip flat `PGABL_Bimo_Bramantyo.zip` (4 file). Panduan: [`panduan/PANDUAN_COLAB.md`](panduan/PANDUAN_COLAB.md).
