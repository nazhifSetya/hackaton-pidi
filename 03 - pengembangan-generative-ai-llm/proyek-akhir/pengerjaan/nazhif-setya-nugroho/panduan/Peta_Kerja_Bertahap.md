# Peta Kerja Bertahap — Fine-tuned Chatbot Tim Legal berbasis RAG

**Nama Proyek**: PGABL Nazhif Setya Nugroho
**Level Target**: Advanced ⭐⭐⭐⭐⭐
**Environment**: Colab T4 (utama) + Windows 11 PowerShell (dev/prototyping)
**Total Estimasi**: ~28–43 jam kerja aktif + waktu training

> **Root proyek (absolute path):**
> `d:\Kalachakra\docs\hackaton_PIDI\Pengembangan Generative AI berbasis_LLM\Fine-tuned_Chatbot_Tim_Legal_berbasis_RAG\`
>
> Selanjutnya path relatif dari root ini disingkat sebagai `./`.

---

## Tahap 0 — Persiapan Environment & Repo (est. ~2h) ⏳

**Tujuan**: Menyiapkan environment reproducible di dua platform (Colab T4 + Windows 11) supaya seluruh tahap berikutnya tidak macet karena masalah dependency atau token. Tahap ini bukan opsional — junior dev sering gagal di Tahap 2/3 karena skip environment hygiene di awal.

**Dependencies**: —

**Deliverable**:
- `./configs/{model_config,training_config,grpo_config,rag_config,paths}.yaml` (5 file)
- `./src/{data,rag,finetune,eval,ui}/__init__.py` (folder skeleton)
- `./.env.example` template secrets
- `./data/raw/{PP_5_2021,PP_35_2021,PP_51_2023,UU_6_2023}.pdf` (copy dari `artifacts/document_knowledge_RAG/` dgn rename)
- `./notebooks/00_setup_verify.ipynb`
- Google Drive mount: `/content/drive/MyDrive/PGABL/` (mirror struktur lokal untuk Colab)
- HF token & WANDB token tersimpan di Colab `userdata`

**Langkah kerja**:

1. **Copy 4 PDF ke `data/raw/`** (PowerShell):
   ```powershell
   New-Item -ItemType Directory -Force data\raw | Out-Null
   Copy-Item "artifacts\document_knowledge_RAG\PP Nomor 5 Tahun 2021.pdf"  data\raw\PP_5_2021.pdf
   Copy-Item "artifacts\document_knowledge_RAG\PP Nomor 35 Tahun 2021.pdf" data\raw\PP_35_2021.pdf
   Copy-Item "artifacts\document_knowledge_RAG\PP Nomor 51 Tahun 2023.pdf" data\raw\PP_51_2023.pdf
   Copy-Item "artifacts\document_knowledge_RAG\UU Nomor 6 Tahun 2023.pdf"  data\raw\UU_6_2023.pdf
   ```
   _KENAPA rename: nama asli pakai spasi + "Nomor" (kurang path-safe). `PP_5_2021.pdf` = path-friendly, konsisten dgn kode Python._
2. **Buat `configs/*.yaml` skeleton** — semua magic number di sini, config-driven. Contoh minimal `configs/model_config.yaml`:
   ```yaml
   base_model_id: unsloth/Llama-3.2-3B-Instruct
   max_seq_length: 2048
   load_in_4bit: true
   quant:
     bnb_4bit_compute_dtype: bfloat16
     bnb_4bit_quant_type: nf4
     double_quant: true
   lora:
     r: 16
     alpha: 32
     dropout: 0.05
     target_modules: [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
     bias: none
   ```
3. **Buat `src/` skeleton**: `data/`, `rag/`, `finetune/`, `eval/`, `ui/` (5 subfolder), tiap subfolder ada `__init__.py` (bisa kosong). Modul .py aktual diisi bertahap di Tahap 1-5.
4. **Buat `.env.example`**:
   ```
   HF_TOKEN=your_hf_write_token_here
   WANDB_API_KEY=your_wandb_key_here
   ```
5. **Setup Colab notebook `notebooks/00_setup_verify.ipynb`**:
   - **Cell 1** — Load secrets:
     ```python
     from google.colab import userdata
     HF_TOKEN = userdata.get('HF_TOKEN')
     WANDB_TOKEN = userdata.get('WANDB_API_KEY')
     ```
     _KENAPA: jangan pernah hardcode token — kena leak kalau di-push._
   - **Cell 2** — Mount Drive:
     ```python
     from google.colab import drive
     drive.mount('/content/drive')
     ```
   - **Cell 3** — Verify GPU: `!nvidia-smi` (harus tampil Tesla T4 ~15GB free).
   - **Cell 4** — Install stack pinned:
     ```
     !pip install -q "unsloth[colab-new]"
     !pip install -q "trl==0.12.0" "transformers==4.46.3" "datasets==3.1.0" "accelerate==1.1.1"
     !pip install -q "chromadb==0.5.20" "sentence-transformers==3.3.1" "FlagEmbedding"
     !pip install -q "ragas==0.2.6" "gradio==5.7.1"
     !pip install -q pypdf pdfplumber duckduckgo-search langdetect rouge-score
     ```
     _KENAPA versi di-pin: Unsloth+TRL sering breaking-change, pin = reproducible._
   - **Cell 5** — Verify:
     ```python
     import torch
     assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))
     from unsloth import FastLanguageModel
     from trl import SFTTrainer, GRPOTrainer
     print("OK — env ready")
     ```
6. **Login HF & WANDB**:
   ```python
   from huggingface_hub import login; login(token=HF_TOKEN)
   import wandb; wandb.login(key=WANDB_TOKEN)
   ```
7. **Verify checkpoint hidup via WebFetch**: pastikan 4 model masih accessible di HF:
   - `unsloth/Llama-3.2-3B-Instruct`
   - `BAAI/bge-m3`
   - `BAAI/bge-reranker-v2-m3`
   - `Ichsan2895/alpaca-gpt4-indonesian`

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] `!nvidia-smi` menunjukkan Tesla T4 dgn ≥14GB free memory
- [ ] `torch.cuda.is_available()` → True; `torch.__version__` ≥ 2.4
- [ ] `from unsloth import FastLanguageModel` tidak error
- [ ] `from trl import SFTTrainer, GRPOTrainer` tidak error
- [ ] 4 PDF ada di `data/raw/` dgn nama persis: `PP_5_2021.pdf`, `PP_35_2021.pdf`, `PP_51_2023.pdf`, `UU_6_2023.pdf`
- [ ] `git status` bersih (semua tracked/ignored, no accidentally-committed PDF)
- [ ] Token HF & WANDB terverifikasi via `HfApi().whoami()` + `wandb.login()`
- [ ] 5 file YAML di `configs/` ada isinya (bukan kosong)

**Risiko / gotchas**:
- Colab session timeout 12h → **Mitigasi**: semua checkpoint SFT/GRPO auto-save ke Drive, bukan `/content/` ephemeral.
- Unsloth version mismatch dgn TRL → **Mitigasi**: pin exact version di atas, jangan `pip install --upgrade`.
- HF token dgn scope Read-only tidak bisa push → **Mitigasi**: generate token dgn scope **Write**, verify via `HfApi().whoami()`.
- Windows PowerShell tidak punya `!` command → **Mitigasi**: dev di PowerShell pakai `python -m pip install`, notebook Colab pakai `!pip`.

**Definition of Done**:
- Semua checkpoint ✅
- Screenshot `!nvidia-smi` disimpan di `outputs/setup_evidence/gpu_verify.png`
- Update CLAUDE.md Progress Log Tahap 0: `✅ SELESAI (tanggal)` — note "Env siap, stack pinned, 4 PDF verified"

---

## Tahap 1 — Data Preparation (est. ~4–6h) ⏳

**Tujuan**: Menyiapkan 3 dataset independen: (a) SFT dataset untuk fine-tuning, (b) PDF chunks untuk RAG, (c) test-set kurasi untuk evaluasi retrieval. Pemisahan tegas antara (a) dan (b) penting — SFT hanya mengajarkan **format & bahasa**, sedangkan legal knowledge murni dari RAG. Ini design decision inti proyek.

**Dependencies**: Tahap 0 selesai (env + PDF ready)

**Deliverable**:
- `data/processed/sft/{train,val}.jsonl` (dari alpaca-gpt4-indonesian)
- `data/processed/pdfs/{PP_5_2021,PP_35_2021,PP_51_2023,UU_6_2023}/chunks.json`
- `data/test_set/legal_qa_testset.jsonl` (30–50 Q&A)
- `notebooks/01_dataset_prep.ipynb`
- `src/data/loaders.py`, `src/data/cleaners.py`, `src/data/formatters.py`
- `src/rag/chunker.py` (reuse untuk Tahap 3)

### Tahap 1a — SFT Dataset (est. ~1–2h)

**Langkah kerja**:
1. Load `Ichsan2895/alpaca-gpt4-indonesian` via `datasets.load_dataset()`. _KENAPA dataset ini: format instruction-following Indonesian native, cocok mengajarkan Llama-3.2-3B ikut instruksi dalam Bahasa Indonesia (base model kuat di EN, lemah di ID instruction-following)._
2. **EDA sample**: print 3 sample acak, cek kolom — dataset ini punya **2 kolom** (`input`, `output`), BUKAN 3 kolom Alpaca klasik (instruction/input/output). `input` = prompt gabungan instruction+context (max ~4.5k char), `output` = jawaban (max ~6k char). Total ~49,969 rows. Hitung `len(ds)`, distribusi panjang `input` (histogram 10 bin), panjang `output` (max/min/mean/median). Filter outlier: `input < 5 char` atau `output < 20 char` (Tahap sample kotor).
3. **Split 90/10 stratified** by panjang `input` bucket (short/medium/long/very_long, boundaries [100, 500, 1500]) dgn `seed=42`. _KENAPA stratified: distribusi panjang harus konsisten antara train & eval supaya eval_loss meaningful._
4. **Mapping ke Llama-3 chat template**:
   ```python
   def format_prompt(example):
       # Dataset hanya 2 kolom (input, output) — bukan Alpaca 3-kolom klasik
       messages = [
           {"role":"system", "content":"Anda adalah asisten AI yang membantu."},
           {"role":"user", "content":example['input']},
           {"role":"assistant", "content":example['output']}
       ]
       return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}
   ```
5. **Verifikasi special tokens** di output ter-format:
   - `<|begin_of_text|>` di awal
   - `<|start_header_id|>system<|end_header_id|>` … `<|eot_id|>`
   - `<|start_header_id|>user<|end_header_id|>` … `<|eot_id|>`
   - `<|start_header_id|>assistant<|end_header_id|>` … `<|eot_id|>`
   _KENAPA verifikasi manual: kalau template salah, SFT loss akan tinggi permanent dan model tidak akan pernah output stop-token dgn benar._
6. Save ke JSONL `train.jsonl` + `val.jsonl` di `data/processed/sft/`.

### Tahap 1b — PDF Preparation untuk RAG (est. ~2–3h)

**Langkah kerja**:
1. **Test loader per PDF** di dev script Windows (`scripts/01_verify_pdf_loader.py`):
   - `pypdf` dulu untuk `PP_51_2023.pdf` (27 hlm, good text) — cek apakah teks terekstrak clean.
   - `pdfplumber` untuk `PP_5_2021.pdf`, `PP_35_2021.pdf`, `UU_6_2023.pdf` — karena OCR mixed, pdfplumber lebih robust untuk layout.
   - _KENAPA test dulu per-PDF: setiap PDF punya karakter berbeda (halaman scan vs text native), pilih parser terbaik dulu sebelum bulk-process._
2. **Cleaner** (`src/data/cleaners.py`):
   - Regex hapus header `PRESIDEN\s+REPUBLIK\s+INDONESIA` dan variasinya.
   - Hapus footer `SK\s+No\s+\d+\s*[A-Z]?`.
   - Normalisasi digit OCR: dalam context angka (regex `(?<=\d)[Ol](?=\d)`) → replace `O→0`, `l→1`. _KENAPA hati-hati regex: jangan replace `O` di kata biasa spt "Orang"._
   - Rekonstruksi kata terpotong antar halaman: kalau baris terakhir hlm N berakhir `-` dan baris pertama hlm N+1 lowercase → join tanpa `-`.
   - Filter section "Cukup jelas" dari Penjelasan — deteksi via header `Pasal X\nCukup jelas.` → skip. _KENAPA: "Cukup jelas" = low-signal, akan mengotori retrieval dgn noise._
3. **Chunker** (`src/rag/chunker.py`) — 2 strategi:
   - **PerPasalChunker (flat)** untuk PP 35/2021 & PP 51/2023: regex `^Pasal\s+\d+` → split, 1 chunk = 1 Pasal utuh. Kalau pasal > 800 char → split lagi dgn overlap 100.
   - **HierarchicalChunker (parent-child)** untuk PP 5/2021 & UU 6/2023:
     - Parent chunk = 2000 char per BAB/klaster
     - Child chunk = 800 char overlap 100 (sub-chunk dari parent) dgn `parent_id` link
     - _KENAPA hierarchical: PP 5/2021 punya pasal-pasal panjang lintas Bab, retrieval per-child (800 char) lebih presisi, generation pakai parent (2000 char) untuk konteks cukup._
4. **Metadata extraction** per chunk:
   ```python
   {
     "chunk_id": "UU_6_2023_klaster_ketenagakerjaan_pasal_88_child_2",
     "text": "...",
     "metadata": {
       "pdf_source": "UU_6_2023",
       "bab": "IV",
       "bagian": "Kedua",
       "pasal": "88",
       "ayat": null,
       "jenis": "batang_tubuh",  # atau "penjelasan"
       "klaster": "ketenagakerjaan",  # hanya UU 6/2023
       "uu_sektor_asal": "UU 13/2003",  # hanya UU 6/2023
       "parent_id": "UU_6_2023_pasal_88_parent",
       "token_count": 234
     }
   }
   ```
5. **Khusus UU 6/2023** (1127 hlm/85 MB):
   - Deteksi 15 klaster via regex header `KLASTER\s+([A-Z\s]+)` di daftar isi.
   - _KENAPA wajib klaster-based collection: 1 collection ChromaDB dgn 15 klaster akan lambat retrieve, split per-klaster = filtering cepat via metadata + collection kecil._
   - Kalau pdfplumber gagal di hlm scan → fallback ke `pytesseract` OCR untuk hlm tersebut saja (jangan seluruh file). _KENAPA: OCR 1127 hlm makan >2 jam._
6. Save chunks per PDF ke `data/processed/pdfs/<PDF_NAME>/chunks.json`.

### Tahap 1c — Test Set Kurasi (est. ~1h)

**Langkah kerja**:
1. Baca sample 5–10 pasal dari tiap PDF (via Read output Tahap 1b), formulate pertanyaan realistis yg legal team benaran akan tanyakan.
2. Struktur JSONL:
   ```json
   {
     "id": "Q001",
     "question": "Berapa hak lembur staf admin menurut regulasi terbaru?",
     "ground_truth_pasal": "Pasal 78",
     "ground_truth_pdf": "PP_35_2021",
     "ground_truth_answer": "Upah lembur untuk 1 jam pertama...",
     "difficulty": "easy",
     "type": "single_pdf"
   }
   ```
3. Distribusi target:
   - 5–10 Q per single PDF (total 20–40)
   - 15–20 Q crossing 2+ PDF (mis. "Bagaimana relasi PP 5/2021 dgn UU 6/2023 klaster perizinan?")
   - Total minimal 30, target 50
4. _KENAPA butuh manual review: LLM-generated test-set = leakage risk (model bisa saja hafal pattern dari training). Manual = ground truth reliable._

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] `len(train_ds)` + `len(val_ds)` == `len(original_ds)` dan rasio ~90/10
- [ ] Print 1 sample `train.jsonl` menampilkan 4 special tokens Llama-3 lengkap
- [ ] Untuk tiap PDF: `chunks.json` ada, count chunks masuk akal (PP 51/2023 ~27 chunks per-pasal, UU 6/2023 ratusan)
- [ ] Print sample 3 chunk dari UU 6/2023 → metadata `klaster` + `pasal` + `parent_id` terisi non-null
- [ ] Print sample 3 chunk dari PP 5/2021 → child chunk 200–300 token, parent 900–1100 token
- [ ] File testset punya minimal 30 baris, dgn ≥1 entry `type=cross_pdf`
- [ ] Manual spot-check: 3 Q&A random di test-set → jawab benar berdasarkan PDF (bukan hallucinated)

**Risiko / gotchas**:
- PDF scan-heavy pypdf return string kosong → **Mitigasi**: fallback ke pdfplumber, kalau masih kosong → pytesseract OCR per-halaman.
- Regex "Pasal N" tidak match karena OCR noise ("Pasal l" alih-alih "Pasal 1") → **Mitigasi**: apply normalisasi digit OCR **sebelum** chunker.
- Test-set bias ke pertanyaan mudah → **Mitigasi**: paksa min 30% pertanyaan `difficulty=hard` (mis. minta angka spesifik, cross-reference antar Pasal).
- Alpaca-gpt4-indonesian punya sample kotor / hate speech → **Mitigasi**: filter length outlier (`instruction < 5 char` atau `output < 20 char`) sebelum split.

**Definition of Done**:
- Semua checkpoint ✅
- Update CLAUDE.md Progress Log Tahap 1: "Tahap 1 ✅ SELESAI (tanggal), N sample SFT, M chunks total, K Q&A testset"

---

## Tahap 2 — Fine-tuning K1 (est. ~6–10h + 4–6h training wait) ⏳

**Tujuan**: Menghasilkan 2 model di HF Hub: (a) `Nazhif/PGABL-Llama-3.2-3B-SFT` hasil SFT, (b) `Nazhif/PGABL-Llama-3.2-3B-GRPO` hasil GRPO on top of SFT. Model SFT mengajarkan format instruksi Indonesia; GRPO menambahkan reasoning `<think>` + language reward. **Model tidak menghafal isi PDF** — legal knowledge murni dari RAG (Tahap 3).

**Dependencies**: Tahap 1a done (`train.jsonl`, `val.jsonl`)

**Deliverable**:
- `notebooks/02_finetune_sft.ipynb` (Basic + Skilled) → nanti rename `Fine-tuning_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- `notebooks/03_finetune_grpo.ipynb` → nanti rename `GRPO_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- HF Public repo: `Nazhif/PGABL-Llama-3.2-3B-SFT` (merged 16-bit)
- HF Public repo: `Nazhif/PGABL-Llama-3.2-3B-GRPO` (merged 16-bit)
- W&B run report links di CLAUDE.md
- Loss curve + reward curve screenshot di `outputs/finetune_evidence/`

### Tahap 2a — K1 Basic SFT (est. ~2–3h + 1–2h training)

**Langkah kerja**:
1. Load model via Unsloth 4-bit:
   ```python
   from unsloth import FastLanguageModel
   model, tokenizer = FastLanguageModel.from_pretrained(
       "unsloth/Llama-3.2-3B-Instruct",
       max_seq_length=2048,
       load_in_4bit=True,
   )
   ```
   _KENAPA Unsloth: 2× lebih cepat + 60% less VRAM vs vanilla PEFT, mandatory untuk T4._
2. Attach LoRA:
   ```python
   model = FastLanguageModel.get_peft_model(
       model, r=16, lora_alpha=32, lora_dropout=0.05,
       target_modules=["q_proj","k_proj","v_proj","o_proj",
                       "gate_proj","up_proj","down_proj"],
       bias="none", use_gradient_checkpointing="unsloth",
   )
   ```
   _KENAPA target modules MHA+FFN: rubric Skilled butuh LoRA di MHA + FFN, FFN adaptation lebih powerful untuk domain shift EN→ID._
3. SFTTrainer config:
   - `per_device_train_batch_size=2`, `gradient_accumulation_steps=4` (effective batch 8)
   - `max_steps=800` untuk MVP (~1 epoch pada dataset ~6400 sample)
   - `learning_rate=2e-4`, `warmup_steps=5`, `lr_scheduler_type="cosine"`
   - `optim="adamw_8bit"`, `fp16=True`, `logging_steps=10`
   - `output_dir="/content/drive/MyDrive/PGABL/checkpoints/sft_basic"` — _KENAPA Drive: session-safe_
4. `trainer.train()` → tunggu ~1–2 jam.
5. Merge LoRA + push to hub:
   ```python
   model.push_to_hub_merged("Nazhif/PGABL-Llama-3.2-3B-SFT",
                             tokenizer, save_method="merged_16bit", token=HF_TOKEN)
   ```
   _KENAPA merged_16bit: kompatibel dgn semua downstream loader (Unsloth reload, vLLM, transformers)._

### Tahap 2b — K1 Skilled Experiments (est. ~2–3h + 2h training)

**Langkah kerja**:
1. Konfigurasi eval selama training:
   - `eval_strategy="steps"`, `eval_steps=100`, `per_device_eval_batch_size=2`
   - Pass `eval_dataset=val_ds`
2. **Eksperimen 1 (baseline)**: setting Tahap 2a (LR 2e-4, rank 16, grad_accum 4).
3. **Eksperimen 2 (variasi)**: pilih 1 dari:
   - LR 5e-5 (lebih konservatif — cek apakah eval_loss lebih smooth)
   - LoRA rank 32 alpha 64 (kapasitas lebih besar — cek overfit)
   - grad_accum 8 (effective batch 16 — cek apakah loss lebih stabil)
   _KENAPA cukup 2 eksperimen: T4 mahal, focus pada perbandingan yang informative bukan grid search._
4. Log semua ke W&B dgn `run_name=exp_baseline` vs `exp_variasi`.
5. Post-training: plot **train_loss vs eval_loss** side-by-side dari 2 run → identifikasi overfit point (eval loss naik saat train loss turun).
6. Pilih pemenang berdasarkan lowest eval_loss + no divergence → jadikan base untuk Tahap 2c.
7. Tulis 1 paragraf analisis di notebook: "Eksperimen 2 rank 32 overfit di step 500, baseline lebih generalizable karena…"

### Tahap 2c — K1 Advanced GRPO (est. ~2–4h + 2–3h training)

**Langkah kerja**:
1. Load SFT winner dari HF (bukan dari checkpoint lokal — bukti reproducibility).
2. Attach LoRA baru (rank 16, same target modules) — GRPO tuning di atas SFT.
3. **Prompt template GRPO** untuk memancing `<think>`:
   ```
   <|start_header_id|>system<|end_header_id|>
   Anda adalah asisten hukum. Selalu berpikir dulu di dalam <think>...</think>
   sebelum memberikan jawaban akhir dalam Bahasa Indonesia.
   <|start_header_id|>user<|end_header_id|>
   {question}
   ```
4. **4 Reward Functions**:
   - `format_reward_func(completions, **kwargs)`:
     ```python
     pattern = r"<think>.*?</think>"
     return [1.0 if re.search(pattern, c, re.DOTALL) else 0.0 for c in completions]
     ```
   - `reasoning_length_reward(completions, **kwargs)`:
     Extract text dalam `<think>...</think>`, hitung char length. Return sigmoid:
     ```python
     def score(l):
         # peak di 300, gentle di 100-500
         return 1.0 / (1.0 + ((l-300)/150)**2)
     ```
     _KENAPA sigmoid bukan linear: hindari model jadi verbose berlebihan atau terlalu pendek._
   - `correctness_reward(completions, ground_truth, **kwargs)`:
     Extract text setelah `</think>`, hitung `rouge_scorer.RougeScorer(['rougeL']).score(gt, ans).fmeasure`. Kalau punya BLEU juga → weighted average 0.6*ROUGE + 0.4*BLEU.
     _KENAPA ROUGE-L untuk QA: cocok untuk answer overlap tanpa strict word order._
   - `language_reward_func(completions, **kwargs)`:
     Pakai `langdetect.detect_langs()` → return prob('id'). Kalau `id` prob >0.7 → 1.0; `<0.3` → -0.5 penalty; between → linear.
     _KENAPA penalty EN: base model tendency EN, harus dipaksa ID._
5. **GRPO Config**:
   - `num_generations=4` (T4 constraint — 8 OOM)
   - `max_completion_length=384` (mitigasi OOM saat generate 4 sample sekaligus)
   - `max_prompt_length=512`
   - `beta=0.04` (KL divergence weight — default GRPO)
   - `learning_rate=5e-6` (GRPO stability, jangan 2e-4)
   - `max_steps=300` (GRPO expensive, 300 sudah kelihatan pattern)
   - Reward weights:
     ```python
     reward_funcs=[format_reward_func, reasoning_length_reward,
                   correctness_reward, language_reward_func]
     reward_weights=[0.3, 0.15, 0.4, 0.15]
     ```
6. Train, push_to_hub_merged sebagai `Nazhif/PGABL-Llama-3.2-3B-GRPO`.
7. **Test case wajib**:
   ```python
   prompt = "Berapa hak lembur staf admin menurut PP 35/2021?"
   # tanpa context (fine-tune tidak tahu isi PDF, jadi jawaban boleh generik)
   ```
   Output harus mengandung `<think>` block + jawaban ID. **Correctness angka tidak dievaluasi di sini** — itu tugas Tahap 3 dgn RAG.

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] W&B project `PGABL-SFT` ada minimal 2 run dgn eval_loss tercatat
- [ ] Loss curve screenshot: train & eval keduanya menurun, tidak diverging
- [ ] HF repo `Nazhif/PGABL-Llama-3.2-3B-SFT` accessible public, `config.json` shows `Llama-3.2-3B` merged
- [ ] HF repo `Nazhif/PGABL-Llama-3.2-3B-GRPO` accessible public
- [ ] Inference SFT: prompt Indonesian → output Indonesian (bukan English/campuran)
- [ ] Inference GRPO: prompt di atas → output regex-matchable `<think>.*?</think>` + jawaban Bahasa Indonesia
- [ ] GRPO reward trajectory di W&B: reward mean naik dari step 0 → step 300 (bukan flat/diverge)

**Risiko / gotchas**:
- OOM di GRPO num_generations=4 → **Mitigasi**: turunkan `max_completion_length` ke 256, atau `max_prompt_length` ke 384.
- Reward hacking (model output `<think></think>` kosong untuk dapat format reward) → **Mitigasi**: `reasoning_length_reward` peak di 300 char, kosong = skor 0.
- Model output EN karena base model bias → **Mitigasi**: bobot `language_reward` 0.15 cukup untuk paksa ID; kalau masih EN, naikkan ke 0.25.
- Session Colab timeout mid-training → **Mitigasi**: `save_steps=100` ke Drive; kalau disconnected, resume dari checkpoint terakhir.
- `push_to_hub_merged` gagal karena free HF storage limit → **Mitigasi**: hapus dulu previous experimental repos; merged 16-bit 3B ~6GB, cukup di free tier.

**Definition of Done**:
- Semua checkpoint ✅
- Link W&B run + link HF SFT + link HF GRPO ter-log di CLAUDE.md
- Screenshot loss curve + reward curve di `outputs/finetune_evidence/`
- Update CLAUDE.md: "Tahap 2 ✅ SELESAI (tanggal), SFT eval_loss=X.XX, GRPO reward mean final=Y.YY"

---

## Tahap 3 — RAG Pipeline K2 (est. ~8–12h) ⏳

**Tujuan**: Membangun modular RAG dgn 3 tingkat kompleksitas (Basic → Skilled → Advanced) sebagai layer terpisah supaya mudah swap komponen (mis. ganti reranker) dan mudah eval per-layer. Karakter RAG modular = scalable ke domain lain (bukan sekadar kejar rubric).

**Dependencies**: Tahap 1b done (chunks JSON), Tahap 2c done (GRPO model)

**Deliverable**:
- `notebooks/04_rag_pipeline.ipynb` → nanti rename `RAG_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- `src/rag/{loader,chunker,embedder,vector_store,retriever,reranker,hyde,fallback,generator,pipeline}.py`
- ChromaDB persist directory: `data/chroma_db/` (dgn subdirs per collection)

### Tahap 3a — K2 Basic RAG (est. ~2–3h)

**Langkah kerja**:
1. **Loader** (`src/rag/loader.py`): reuse hasil Tahap 1b, cukup load `chunks.json` per PDF.
2. **Embedder** (`src/rag/embedder.py`):
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer("BAAI/bge-m3", device="cuda")
   embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
   ```
   _KENAPA BGE-M3: multilingual, mendukung ID native, dense+sparse+colbert built-in, SOTA cross-lingual retrieval._
3. **Vector Store** (`src/rag/vector_store.py`):
   ```python
   import chromadb
   client = chromadb.PersistentClient(path="data/chroma_db/")
   # 3 collection per PP + 15 collection per klaster UU 6/2023
   collection_pp5 = client.get_or_create_collection("pp_5_2021", metadata={"hnsw:space":"cosine"})
   # dst
   ```
   _KENAPA per klaster untuk UU 6/2023: 15 klaster × ratusan chunk = collection lebih kecil, filtering metadata + semantic search jadi cepat._
4. **Ingest**: loop chunks → embed → `collection.add(ids, embeddings, documents, metadatas)`.
5. **Simple retrieval + generation** (Basic tier):
   ```python
   def rag_basic(query):
       q_emb = embedder.encode([query])
       results = collection.query(query_embeddings=q_emb, n_results=5)
       context = "\n\n".join(results['documents'][0])
       prompt = f"Konteks:\n{context}\n\nPertanyaan: {query}\n\nJawaban:"
       return llm.generate(prompt)
   ```
6. Test dgn 3 query manual, print retrieved chunks + jawaban.

### Tahap 3b — K2 Skilled (est. ~3–4h)

**Langkah kerja**:
1. **Metadata filtering di retrieval**:
   ```python
   collection.query(query_embeddings=q_emb, n_results=10,
                    where={"klaster": "ketenagakerjaan"})
   ```
   _KENAPA: kalau query eksplisit tentang ketenagakerjaan, filter dulu → kandidat lebih relevan. Kalau query ambigu → skip filter._
2. **Query routing sederhana**: keyword-based classifier (regex `lembur|upah|karyawan` → klaster ketenagakerjaan). _KENAPA jangan LLM-based routing di tier Skilled: expensive per query, keyword sudah cukup untuk MVP._
3. **Ensemble Retriever (BM25 + Dense)**:
   ```python
   from rank_bm25 import BM25Okapi
   bm25 = BM25Okapi([chunk['text'].split() for chunk in all_chunks])
   # dense score dari ChromaDB (normalize 0-1)
   # ensemble score = 0.5 * bm25_norm + 0.5 * dense_norm
   ```
   _KENAPA hybrid: BM25 catch keyword-exact match (nomor Pasal, istilah "PKWT"), dense catch semantic ("hak libur" ≈ "cuti"). Komplementer._
4. **Parent-Child Retriever** (untuk PDF hierarchical):
   - Retrieve dari child collection (800 char, presisi tinggi)
   - Ambil `parent_id`, lookup parent chunk (2000 char) untuk generation
   - _KENAPA: presisi + context window optimal._
5. **Sitasi di prompt**:
   ```
   Konteks:
   [Sumber 1: UU 6/2023 - Klaster Ketenagakerjaan - Pasal 88]
   {text}

   [Sumber 2: PP 35/2021 - Pasal 15]
   {text}

   Pertanyaan: {query}
   Instruksi: Jawab dgn menyebut nomor Sumber (mis. "[Sumber 1]") setiap kali mengutip.
   ```
6. Test 3 query dari test-set Tahap 1c → verify jawaban menyebut `[Sumber X]`.

### Tahap 3c — K2 Advanced (est. ~3–5h)

**Langkah kerja**:
1. **HyDE** (`src/rag/hyde.py`):
   ```python
   def hyde_query(question, llm):
       prompt = (f"Bayangkan Anda advokat senior. Tulis 2 versi jawaban singkat "
                 f"(2-3 kalimat masing-masing) untuk pertanyaan berikut. "
                 f"Fokus pada terminologi hukum Indonesia.\n\nPertanyaan: {question}")
       hallucinated = llm.generate(prompt, max_new_tokens=300)
       # embed hallucinated (bukan question) untuk retrieval
       return hallucinated
   ```
   _KENAPA HyDE: query legal user sering pendek/awam ("berapa hak lembur"); hallucinated answer punya vocabulary hukum ("upah lembur", "waktu istirahat mingguan") yang lebih match ke corpus embedding space._
2. **Reranker** (`src/rag/reranker.py`):
   ```python
   from sentence_transformers import CrossEncoder
   reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cuda")
   # retrieve Top-20 via ensemble+HyDE
   pairs = [(question, doc) for doc in top20_docs]
   scores = reranker.predict(pairs)
   # rerank → ambil Top-5
   ```
   _KENAPA rerank: bi-encoder retrieval fast tapi kurang presisi; cross-encoder rerank pada 20 kandidat → boost hit@5._
3. **Threshold gating + DuckDuckGo fallback** (`src/rag/fallback.py`):
   ```python
   max_score = max(rerank_scores)
   if max_score < 0.3:
       # fallback ke web search
       from duckduckgo_search import DDGS
       results = DDGS().text(f"regulasi Indonesia {query}", max_results=5)
       context = "\n".join([r['body'] for r in results])
       flag_source = "web_fallback"
   else:
       context = top5_docs
       flag_source = "local_rag"
   ```
   _KENAPA threshold 0.3 (empirical BGE-reranker range 0-1 setelah sigmoid): di bawah itu, chunk tidak related — jawab dari cache PDF akan hallucinate; better fallback web + flag ke user._
4. **Pipeline orchestrator** (`src/rag/pipeline.py`):
   ```python
   def rag_advanced(question, tier="advanced"):
       if tier == "advanced":
           q_expanded = hyde_query(question, llm)
       else:
           q_expanded = question
       candidates = ensemble_retrieve(q_expanded, k=20, filter=router(question))
       ranked = rerank(question, candidates, top_k=5)
       if max(ranked.scores) < 0.3:
           context, source = ddg_fallback(question)
       else:
           context, source = build_context_with_citation(ranked)
       answer = generator(question, context)
       return {"answer": answer, "sources": ranked.sources, "flag": source}
   ```
5. Test 5 query dari test-set: 3 in-domain (harus local_rag), 2 out-of-domain (harus web_fallback).

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] ChromaDB `list_collections()` menunjukkan 3 PP + 15 klaster UU 6/2023 = 18 collection
- [ ] `collection.count()` untuk masing-masing > 0
- [ ] Basic RAG: query "Berapa hak lembur" → retrieved Top-5 mengandung minimal 1 chunk dgn `pasal=78` di metadata
- [ ] Skilled RAG: output jawaban mengandung string `[Sumber` (regex `\[Sumber\s+\d+`)
- [ ] Skilled Parent-Child: log retrieval → child chunk yang di-retrieve, parent chunk yang dipakai di context (bukti dua chunk berbeda ukuran)
- [ ] Advanced HyDE: print hallucinated text yang dipakai retrieval, verifikasi berbeda dari original question
- [ ] Advanced Reranker: print sebelum rerank (Top-20 order) vs sesudah rerank (Top-5 order berbeda)
- [ ] Advanced Fallback: query "resep rendang" (out-of-domain) → `flag=web_fallback`
- [ ] Query in-domain → `flag=local_rag`

**Risiko / gotchas**:
- BGE-M3 model download 2GB → **Mitigasi**: cache ke Drive `/content/drive/MyDrive/PGABL/models/bge-m3/`, symlink saat load.
- ChromaDB persistent path di `/content/` hilang saat session end → **Mitigasi**: symlink `data/chroma_db/` ke `/content/drive/MyDrive/PGABL/chroma_db/`.
- HyDE hallucinated malah confuse retrieval (kalau LLM output gibberish) → **Mitigasi**: kalau `len(hallucinated) < 50` char, fallback pakai original question.
- Reranker CrossEncoder slow (Top-20 × 384 token = ~2-3s) → **Mitigasi**: batch predict, `batch_size=8`.
- DuckDuckGo rate-limit → **Mitigasi**: try-except → return gracefully "Maaf, tidak menemukan informasi. Silakan hubungi tim legal."
- Threshold 0.3 mungkin salah untuk BGE-reranker-v2-m3 (default output logits, bukan sigmoid) → **Mitigasi**: run sample 10 query, plot distribution score → tune threshold empirical (bisa 0.5 kalau logits).

**Definition of Done**:
- Semua checkpoint ✅
- Screenshot Gradio-like test output (query + retrieved sources + answer + flag) untuk 5 query
- Update CLAUDE.md: "Tahap 3 ✅ SELESAI (tanggal), 18 collections, HyDE+Reranker+Fallback working, threshold=X"

---

## Tahap 4 — Evaluasi (est. ~3–5h) ⏳

**Tujuan**: Membuktikan bahwa Advanced RAG memang lebih baik dari Basic/Skilled dgn metric objektif (retrieval hit@k) + subjektif (RAGAs LLM-judge). Tanpa eval, klaim "Advanced" tidak defensible.

**Dependencies**: Tahap 1c (test-set) + Tahap 3 (3 tier RAG) done

**Deliverable**:
- `src/eval/retrieval_metrics.py`
- `src/eval/ragas_eval.py`
- `notebooks/05_eval.ipynb`
- `outputs/eval_reports/eval_YYYYMMDD.json`
- `docs/benchmark.md` (comparison table ready-to-paste ke submission)

**Langkah kerja**:
1. **Retrieval metrics** (`src/eval/retrieval_metrics.py`):
   - `hit@k`: apakah `ground_truth_pasal` ada dalam metadata Top-k retrieved
   - `MRR`: 1 / rank_of_first_correct
   - `NDCG@5`: standard formula
   - Loop test-set (30–50 Q&A), hitung per-tier (Basic/Skilled/Advanced):
     ```python
     for q in testset:
         retrieved = pipeline(q['question'], tier='advanced')['sources']
         retrieved_pasals = [s['metadata']['pasal'] for s in retrieved]
         hit_at_1 = q['ground_truth_pasal'] == retrieved_pasals[0]
         # dst
     ```
2. **RAGAs eval** (`src/eval/ragas_eval.py`):
   - Metric: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
   - LLM judge = fine-tuned GRPO Llama-3.2-3B (self-judge)
   - _KENAPA self-judge: butuh judge Indonesia native + tidak bergantung API external (GPT-4 mahal + rate limit)_
   - **Dokumentasikan bias potensial**: "Self-judge cenderung generous ke jawaban model sendiri; skor RAGAs harus dilihat sbg upper-bound. Retrieval hit@k = objective metric utama."
3. **Comparison table** (`docs/benchmark.md`):
   ```
   | Tier     | hit@1 | hit@3 | hit@5 | MRR  | NDCG@5 | Faithfulness | AnsRelevancy |
   |----------|-------|-------|-------|------|--------|--------------|--------------|
   | Basic    | 0.42  | 0.63  | 0.75  | 0.55 | 0.67   | 0.71         | 0.65         |
   | Skilled  | 0.55  | 0.75  | 0.85  | 0.68 | 0.78   | 0.79         | 0.72         |
   | Advanced | 0.68  | 0.85  | 0.92  | 0.78 | 0.87   | 0.85         | 0.80         |
   ```
   (angka contoh — real number dari run)
4. **Analisis 1 paragraf** di `benchmark.md`:
   - "Advanced meningkatkan hit@1 dari 0.42 → 0.68 (+62% relatif) berkat HyDE + Reranker."
   - "Fallback DuckDuckGo dipicu di X% dari test-set — sesuai design (out-of-domain query)."
   - "Faithfulness gap Basic vs Advanced 0.71 → 0.85 signifikan → RAG lebih grounded."
5. Save raw hasil `.json` per query untuk audit trail.

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] `eval_YYYYMMDD.json` ada, structure per-query dgn `hit@1..5`, `mrr`, `ragas_scores` terisi
- [ ] Comparison table 3 tier × 7 metric complete (tidak ada NaN)
- [ ] Advanced tier menang di ≥5 dari 7 metric (kalau tidak, ada bug atau design issue → investigate)
- [ ] Sample 3 query dgn skor RAGAs rendah → manual review, konfirmasi memang jawaban buruk (bukan judge error)
- [ ] `benchmark.md` punya paragraf analisis + bias disclosure

**Risiko / gotchas**:
- RAGAs versi 0.2.x breaking-change dari 0.1.x → **Mitigasi**: pin ragas==0.2.6, ikuti doc `Evaluate` API baru.
- Self-judge terlalu generous, semua tier dapat 0.9+ → **Mitigasi**: dokumentasikan explicit di analisis, tekankan hit@k sbg objective anchor.
- Test-set terlalu mudah, semua tier 100% → **Mitigasi**: check di Tahap 1c bahwa min 30% `difficulty=hard`; kalau perlu tambah 10 pertanyaan tricky.
- RAGAs butuh async LLM call → butuh wrapper Llama sbg `LangchainLLMWrapper` atau custom → **Mitigasi**: sample RAGAs docs untuk custom judge integration.

**Definition of Done**:
- Semua checkpoint ✅
- `docs/benchmark.md` ready-to-paste ke `RAG_submission_*.ipynb` final markdown cell
- Update CLAUDE.md: "Tahap 4 ✅ SELESAI (tanggal), Advanced hit@1=X, faithfulness=Y, biaya inference per query = Z detik"

---

## Tahap 5 — Interface Gradio K3 (est. ~3–4h) ⏳

**Tujuan**: Bangun UI Gradio yang bisa didemo ke reviewer + tim legal internal. Citation panel wajib supaya user (legal team) bisa verifikasi jawaban ke sumber asli.

**Dependencies**: Tahap 3c done, Tahap 4 done (biar bisa embed benchmark di UI info tab)

**Deliverable**:
- `src/ui/gradio_app.py` (main Gradio app)
- `notebooks/06_ui_test.ipynb` (untuk demo Colab dgn share=True)
- Screenshot UI di `outputs/ui_evidence/`

**Langkah kerja**:
1. **Load sekali di startup** (MODEL LOAD SEKALI rule):
   ```python
   # Module-level singleton
   print("Loading model...")
   MODEL, TOKENIZER = load_grpo_model()
   print("Loading ChromaDB...")
   CHROMA = load_chromadb_client()
   print("Loading BGE embedder...")
   EMBEDDER = load_bge_m3()
   print("Loading reranker...")
   RERANKER = load_bge_reranker()
   ```
   _KENAPA: kalau load per-request → 30s+ latency + OOM setelah beberapa request._
2. **Gradio Blocks layout**:
   ```python
   with gr.Blocks(theme=gr.themes.Soft()) as demo:
       gr.Markdown("# PGABL Legal Chatbot — Kalachakra Tim Legal")
       with gr.Row():
           with gr.Column(scale=3):
               chatbot = gr.Chatbot(height=500, type="messages")
               msg = gr.Textbox(placeholder="Tanyakan regulasi...")
               with gr.Row():
                   send_btn = gr.Button("Kirim", variant="primary")
                   clear_btn = gr.Button("Clear")
           with gr.Column(scale=2):
               gr.Markdown("### Sumber Rujukan")
               citation_panel = gr.Dataframe(
                   headers=["Rank", "Sumber", "Pasal", "Score", "Snippet"],
                   interactive=False
               )
               source_flag = gr.Textbox(label="Source Type", interactive=False)
   ```
3. **Streaming output** pakai `TextIteratorStreamer`:
   ```python
   def respond(message, history):
       result = rag_pipeline(message)
       # streaming generation
       streamer = TextIteratorStreamer(TOKENIZER, skip_prompt=True)
       thread = Thread(target=MODEL.generate, kwargs=dict(..., streamer=streamer))
       thread.start()
       partial = ""
       for token in streamer:
           partial += token
           yield partial, result['citations_df'], result['flag']
   ```
   _KENAPA streaming: legal query bisa panjang (300+ token), streaming UX >> block-wait._
4. **Citation panel** menampilkan Top-5 dari result:
   ```python
   df = [[i+1, s['pdf_source'], s['pasal'], f"{s['score']:.3f}", s['text'][:200]+"..."]
         for i, s in enumerate(result['sources'])]
   ```
5. **CDP screenshot** untuk verifikasi UI:
   - Jalankan `demo.launch(share=True)` di Colab
   - Ambil `share_url`
   - Via `mcp__chrome-devtools__navigate_page` ke share_url
   - `mcp__chrome-devtools__take_screenshot` → save ke `outputs/ui_evidence/gradio_ui.png`
6. **Test golden path**: query "Berapa upah lembur menurut PP 35/2021?" → verify jawaban muncul streaming + citation panel terisi dgn PP_35_2021 di Rank 1.
7. **Test edge case out-of-domain**: query "Resep rendang" → verify `source_flag=web_fallback` atau graceful decline.

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] `python -m src.ui.gradio_app` (Windows) atau `demo.launch(share=True)` (Colab) start tanpa error
- [ ] Model load hanya 1× (cek log — no reload per request)
- [ ] Golden path query: jawaban muncul streaming (bukan block) + citation dgn 5 rows
- [ ] Edge case query out-of-domain: flag benar (web_fallback atau decline)
- [ ] Screenshot UI tersimpan di `outputs/ui_evidence/gradio_ui.png` menunjukkan Chatbot + Citation panel side-by-side
- [ ] Latency < 15s untuk query in-domain (retrieval + rerank + generate)

**Risiko / gotchas**:
- Gradio 5.x breaking-change dari 4.x untuk `Chatbot(type="messages")` → **Mitigasi**: pin gradio==5.7.1, ikuti doc 5.x.
- Share link Colab timeout 72h → **Mitigasi**: dokumentasikan cara re-launch di notebook.
- TextIteratorStreamer conflict dgn Unsloth optimized generate → **Mitigasi**: `FastLanguageModel.for_inference(model)` mode dulu, kalau streamer error, fallback ke non-streaming.
- ChromaDB reload dari Drive lambat (~30s) → acceptable, hanya 1× di startup.

**Definition of Done**:
- Semua checkpoint ✅
- Screenshot UI + share link ter-log di CLAUDE.md
- Update CLAUDE.md: "Tahap 5 ✅ SELESAI (tanggal), UI runs, latency=X sec/query"

---

## Tahap 6 — Packaging & Submission (est. ~2h) ⏳

**Tujuan**: Konversi artifact dev ke bentuk submission yang persis sesuai konvensi filename + zip structure, plus verifikasi zero-error execution.

**Dependencies**: Tahap 2, 3, 4, 5 selesai

**Deliverable**:
- `submission/Fine-tuning_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- `submission/RAG_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- `submission/GRPO_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
- `submission/link_huggingface.txt`
- `submission/requirements.txt`
- `PGABL_Nazhif_Setya_Nugroho.zip` (flat, 5 file di root)

**Langkah kerja**:
1. **Notebook cleanup**:
   - Copy `notebooks/02_finetune_sft.ipynb` → `submission/Fine-tuning_submission_PGABL_Nazhif_Setya_Nugroho.ipynb`
   - Copy `notebooks/04_rag_pipeline.ipynb` → `submission/RAG_submission_...ipynb`
   - Copy `notebooks/03_finetune_grpo.ipynb` → `submission/GRPO_submission_...ipynb`
   - Cleanup cell scratch (yg tidak reproducible, mis. print debug)
   - Tambah markdown intro tiap notebook: judul, nama, tanggal, level target, ringkasan pendekatan
   - Tambah markdown penjelasan di antara code block ("Cell berikut load model karena ...")
   - Inline kode dari `src/*.py` ke notebook via JSON manipulation:
     ```python
     import json
     with open("submission/RAG_submission_...ipynb") as f:
         nb = json.load(f)
     for cell in nb['cells']:
         if cell['cell_type']=='code' and '________' in ''.join(cell['source']):
             # replace dgn kode dari src/rag/chunker.py, dst
             ...
     assert '________' not in json.dumps(nb), "Ada blank yg belum terisi"
     with open("submission/RAG_submission_...ipynb", 'w') as f:
         json.dump(nb, f, indent=2)
     ```
   _KENAPA inline kode: reviewer harus bisa Run All tanpa external module `src/`._
2. **Re-run penuh** untuk verifikasi zero-error:
   ```powershell
   jupyter nbconvert --execute --to notebook --inplace `
     submission/Fine-tuning_submission_*.ipynb
   ```
   Ulangi untuk RAG & GRPO notebook.
   _KENAPA: pastikan output cell konsisten dgn code, tidak ada cell yg pernah error tapi output tersimpan._
3. **Generate requirements.txt**:
   ```powershell
   pip install pipreqs
   pipreqs .\src .\submission --force --savepath submission\requirements.txt
   ```
   Manual review: pastikan versi ter-pin (Tahap 0), tambahkan yg missing (`unsloth`, `trl`), hapus yg extraneous.
4. **Isi `link_huggingface.txt`**:
   ```
   SFT Model: https://huggingface.co/Nazhif/PGABL-Llama-3.2-3B-SFT
   GRPO Model: https://huggingface.co/Nazhif/PGABL-Llama-3.2-3B-GRPO
   ```
5. **Buat ZIP flat**:
   ```powershell
   Compress-Archive -Path submission\* -DestinationPath PGABL_Nazhif_Setya_Nugroho.zip -Force
   ```
   _KENAPA `submission\*` (bukan `submission\`): supaya isi zip flat, tidak ada nested folder `submission/`._
6. **Manual verify zip**:
   ```powershell
   Expand-Archive PGABL_Nazhif_Setya_Nugroho.zip -DestinationPath tmp_verify -Force
   Get-ChildItem tmp_verify  # harus 5 file, no subfolder
   Remove-Item tmp_verify -Recurse
   ```

**Checkpoint verifikasi (VERIFY-FIRST)**:
- [ ] 3 notebook re-run via `nbconvert --execute` exit code 0
- [ ] `requirements.txt` mencakup semua library kritikal: unsloth, trl, transformers, datasets, chromadb, sentence-transformers, ragas, gradio, pypdf, pdfplumber, duckduckgo-search, langdetect, rouge-score
- [ ] `link_huggingface.txt` link accessible public (buka di browser incognito)
- [ ] `PGABL_Nazhif_Setya_Nugroho.zip` size wajar (< 20MB — notebook + txt files only, no model weights)
- [ ] Unzip test: persis 5 file di root, tidak ada folder nested, filename persis sesuai konvensi
- [ ] Filename pattern lengkap regex-matchable: `^(Fine-tuning|RAG|GRPO)_submission_PGABL_Nazhif_Setya_Nugroho\.ipynb$`

**Risiko / gotchas**:
- `nbconvert --execute` re-run gagal karena Drive path tidak tersedia di local Windows → **Mitigasi**: parametrize path via env var, atau execute final di Colab langsung.
- `pipreqs` miss library yg di-import via string (mis. `chromadb.PersistentClient`) → **Mitigasi**: manual audit, cross-check dgn stack di Tahap 0.
- ZIP dibuat dari PowerShell menghasilkan `\` path separator → biasanya OK, tapi kalau reviewer di Linux → **Mitigasi**: test unzip di WSL / Linux VM sebelum submit.
- HF model repo accidentally private → **Mitigasi**: cek settings repo, set Public.
- Notebook size besar (embed image / large output) → **Mitigasi**: `nbstripout` untuk clean output kalau size >5MB per notebook.

**Definition of Done**:
- Semua checkpoint ✅
- ZIP final di root proyek: `PGABL_Nazhif_Setya_Nugroho.zip`
- Update CLAUDE.md Progress Log ✅ SELESAI dgn tanggal + link submission form
- Final commit git dgn tag `v1.0-submission`

---

## Cross-Reference Antar Tahap

| Dari | Ke | Artifact yang dibawa |
|---|---|---|
| Tahap 0 | Semua | Env pinned, token, folder struktur |
| Tahap 1a | Tahap 2 | `train.jsonl`, `val.jsonl` untuk SFT |
| Tahap 1b | Tahap 3a | `chunks.json` per PDF untuk ingest ChromaDB |
| Tahap 1c | Tahap 4 | `legal_qa_testset.jsonl` untuk hit@k |
| Tahap 2a | Tahap 2b | Base config untuk eksperimen variasi |
| Tahap 2b winner | Tahap 2c | SFT model sbg starting point GRPO |
| Tahap 2c | Tahap 3, 5 | GRPO model untuk generator RAG + Gradio UI |
| Tahap 3c | Tahap 4 | 3 tier pipeline untuk comparison eval |
| Tahap 4 | Tahap 6 | `benchmark.md` embed ke RAG_submission notebook |
| Tahap 5 screenshot | Tahap 6 | Bukti UI untuk melampirkan (opsional di notebook markdown) |

---

## Timeline Realistis (Junior Dev + T4 Constraint)

| Tahap | Est. Waktu Aktif | Wait Time (training/re-run) | Cumulative |
|---|---|---|---|
| 0 | 2h | 0 | 2h |
| 1 | 4–6h | 0 | 6–8h |
| 2 | 6–10h | 4–6h (training) | 16–24h |
| 3 | 8–12h | 1h (embed + ingest) | 25–37h |
| 4 | 3–5h | 0.5h (RAGAs run) | 28.5–42.5h |
| 5 | 3–4h | 0 | 31.5–46.5h |
| 6 | 2h | 0.5h (nbconvert) | 34–49h |

Kalau kerja **4h/hari fokus** → **9–13 hari kalender**. Buffer 20% untuk gotchas → **11–16 hari**.
