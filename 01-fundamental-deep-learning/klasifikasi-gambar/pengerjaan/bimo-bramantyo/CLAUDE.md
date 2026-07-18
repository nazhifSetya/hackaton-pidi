# CLAUDE.md — Proyek Akhir Klasifikasi Gambar · **Fruits-360 (10 buah)** · submission utk **Bimo Bramantyo**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Akhir: Klasifikasi Gambar**, tema **Buah (Fruits-360, 10 kelas)**, atas nama **Bimo Bramantyo**.
- **Self-contained di folder ini** (`.../klasifikasi-gambar/pengerjaan/bimo-bramantyo/`). Folder sibling berisi kerjaan anggota lain — **REFERENSI metodologi saja, JANGAN diubah, JANGAN disamakan** (anti-plagiarisme Dicoding):
  - `../nazhif-setya-nugroho/` → Animals-10 + MobileNetV2, Colab GPU, ⭐⭐⭐⭐⭐
  - `../fareynaldi-affan/` → Garbage-12 + EfficientNetV2B0, Colab GPU, ⭐⭐⭐⭐⭐
  - `../dafina/` → TF Flowers + MobileNetV2 frozen, lokal CPU, ⭐⭐⭐
- **Dataset Bimo (buah) sengaja BEDA** dari animals/garbage/flowers teman-temannya. Kode & metodologi juga dibedakan.
- Aturan Everest/EBC (backoffice-service, Sequelize, dll) **TIDAK berlaku di sini.**

---

## 👤 USER & GAYA KERJA

- **Pemilik submission:** **Bimo Bramantyo** — dipakai di semua nama file: `Bimo_Bramantyo`.
- **Konteks:** Mahasiswa Dicoding, level pemula–menengah. Proyek NLP-nya (Analisis Sentimen Shopee) sudah selesai. Tiga teman tim (Nazhif, Fareynaldi, Dafina) sudah selesai proyek klasifikasi gambar dengan tema berbeda.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia simpel, mudah dimengerti pemula–menengah.**
  - **Pelan-pelan, step-by-step.** Jelaskan **kenapa** tiap langkah, bukan cuma **apa**.
  - **Teliti detail kecil.**
  - **Jangan asumsi.** Kalau ambigu, **tanya dulu** pakai AskUserQuestion.
  - Kalau tunjukkan pattern kode dari proyek teman, sertakan **path file + line number**.
- **Target nilai:** **⭐⭐⭐ (Pass)** — kriteria utama saja. **JANGAN over-engineer.** Fokus lulus dengan risiko minimum & waktu training kecil (pilihan user 2026-07-18).

---

## 🎯 INTI PROYEK

Membangun model **CNN klasifikasi gambar** (**Keras Sequential + Conv2D + Pooling**) yang mengenali **10 jenis buah**, lalu mengonversi model ke **3 format wajib: SavedModel, TF-Lite, TFJS** — semua **berjalan di Victus (Windows lokal, CPU)** tanpa Colab.

**Alur (SEDERHANA, 7 tahap):** setup env → download dataset → EDA singkat → split train/val/test → train model → evaluasi + save 3 format → inference bukti → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Dataset** | **Fruits-360** subset **10 kelas** (Banana, Strawberry, Orange, Pineapple, Watermelon, Kiwi, Lemon, Avocado, Raspberry, Mango) | Sumber: GitHub `Horea94/Fruit-Images-Dataset` (URL publik, **TANPA Kaggle**). Ambil via **blobless sparse-checkout** (hemat bandwidth). Gambar 100×100 RGB `.jpg`. Total ~6.399 (Training ~4.791 + Test ~1.608). |
| **Split** | **Train+Val dari folder `Training/`** (stratified 85/15, seed 42) · **Test dari folder `Test/` bawaan** | ⚠️ Fruits-360 = 1 buah difoto berputar 360° → gambar sangat mirip. Pakai split bawaan (Test = sesi foto beda) supaya TIDAK bocor & akurasi jujur. **Beda metodologi dari Dafina** (dia split acak 1 folder). |
| **Environment** | **100% Victus lokal (Windows + CPU)**. TIDAK ADA Colab/GPU. Python **3.11.9** venv (`python -m venv`, **bukan uv** — uv tidak terpasang di device ini). | tensorflow-cpu cukup: MobileNetV2 frozen + dataset kecil 100×100 → training cepat. |
| **Arsitektur** | **Sequential[Rescaling → MobileNetV2(frozen) → Conv2D(32,3) → MaxPool → GlobalAveragePooling → Dropout(0.2) → Dense(10, softmax)]** | Hyperparam SENGAJA beda dari Dafina (dia 160×160, Conv2D(64), Dense(128) hidden). Bimo: input **100×100** (native, tanpa upscaling), Conv2D(32), tanpa Dense hidden. Layer Conv2D+MaxPool wajib kriteria #4. |
| **Training** | 1 fase: base frozen, `Adam(1e-3)`, batch 32, max 12 epoch + **EarlyStopping** (monitor `val_accuracy`, patience 3, restore_best_weights) | Callback minimum (ES). Fruits-360 clean → biasanya >95% cepat, tapi target tetap ≥85%. |
| **Target nilai** | **⭐⭐⭐ (Pass) — kriteria utama.** Bonus saran gratis yang otomatis masuk: #1 callback ES, #5 ≥3 kelas (10 kelas), #6 inference. **JANGAN kejar #3 (≥10rb gambar) atau #4 (≥95% dipaksakan).** | |

---

## 📁 STRUKTUR FOLDER

```
bimo-bramantyo/
├── CLAUDE.md                       ← file ini (memory + rules)
├── .venv/                          ← virtual env Windows lokal (JANGAN di-commit/zip; di-gitignore)
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang di-zip)
    ├── notebook.ipynb              ← notebook utama (WAJIB, sudah di-run)
    ├── notebook.py                 ← WAJIB (via nbconvert saat packaging)
    ├── requirements.txt            ← WAJIB
    ├── README.md                   ← opsional (rekomendasi Dicoding)
    ├── saved_model/                ← format 1 (WAJIB)
    ├── tflite/                     ← format 2 (WAJIB): model.tflite + label.txt
    └── tfjs_model/                 ← format 3 (WAJIB): model.json + shards
```

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `../../artifact/instruksi/2.kriteria.md`, `4.ketentuan_berkas_submission.md`, `5.lainnya.md`.

1. **Akurasi training DAN testing set ≥ 85%** (di bawah itu → reject).
2. **WAJIB lampirkan KEDUA file `.py` dan `.ipynb`** (sering kelupaan → reject).
3. **WAJIB simpan model dalam 3 format: SavedModel, TF-Lite, TFJS.** Kurang satu → reject.
4. **Notebook `.ipynb` WAJIB sudah dijalankan** → semua output ter-embed.
5. **Kriteria wajib:** dataset ≥1.000 gambar, BUKAN RPS/X-Ray, split train/test/val, Sequential+Conv2D+Pooling, plot akurasi & loss.
6. **`requirements.txt` wajib ada.**
7. Kirim dalam **1 folder di-zip**. Bahasa: **Python**.
8. **Jangan submit berkali-kali** (review ±3 hari kerja).

---

## 📊 KRITERIA UTAMA → status target

1. Dataset bebas, min **1.000 gambar**, BUKAN RPS/X-Ray. → **Fruits-360 ~6.399** ✅
2. Split **train/test/validation**. → Training→train+val (85/15) + Test bawaan ✅
3. Model **Sequential + Conv2D + Pooling**. → Sequential + MobileNetV2 + Conv2D + MaxPool ✅
4. Akurasi train & test **min 85%**. → Fruits-360 clean, MobileNetV2 frozen biasanya ≫85% ✅
5. **Plot akurasi & loss**. → matplotlib subplot ✅
6. Simpan **SavedModel + TF-Lite + TFJS**. → 3 format ✅

**Bonus saran** yang MASUK gratis (bukan dikejar): #1 Callback (ES), #5 ≥3 kelas (10 kelas), #6 Inference + bukti. **SKIP:** #2 resolusi non-seragam (Fruits-360 seragam 100×100), #3 ≥10rb, #4 ≥95%.

---

## 🔑 CATATAN TEKNIS PENTING (pelajaran mahal dari tim — JANGAN diulangi)

### ⚠️ Augmentasi HARUS DI LUAR model, bukan di dalam Sequential
- Pelajaran Fareynaldi: augmentasi di dalam model → **TFLite gagal `ImageProjectiveTransformV3` FLEX ops**.
- ✅ Benar: augmentasi via `ds.map(...)` di pipeline dataset. Model TIDAK punya augmentation layers.
- **Catatan Bimo:** Fruits-360 sudah bersih & seragam → augmentasi ringan/opsional (RandomFlip saja cukup, atau skip demi kesederhanaan ⭐⭐⭐).

### ⚠️ TFJS install PALING AKHIR + isolasi
- Pelajaran Dafina: `tensorflowjs` di Windows butuh `tensorflow_decision_forests` yang **tidak punya binary Windows** → install gagal. Solusi Dafina: **venv isolated `.venv-tfjs`** dgn `tensorflowjs==4.22.0` + patch manual TFDF `op_dynamic.py`.
- **Rencana Bimo:** ekspor SavedModel + TFLite dulu (aman) → konversi TFJS PALING AKHIR di venv terpisah. Kalau macet, ikuti solusi Dafina (path patch ada di CLAUDE.md Dafina Tahap 0).

### 🖼️ Ukuran input 100×100
- Fruits-360 native 100×100. MobileNetV2 minimal input 96×96 → 100×100 aman tanpa upscaling. **Beda dari Dafina (160×160).**

### 🚧 label.txt untuk folder `tflite/`
- 10 baris nama kelas urut alfabet (= urutan output softmax).

---

## 🧭 METODOLOGI

1. **VERIFY-FIRST (wajib).** Sebelum tulis logika ke notebook: prototype ke data asli via `.venv\Scripts\python.exe` (output prototype ke `d:\tmp\`, JANGAN ke folder submission). Plot → simpan PNG ke `%TEMP%`/`d:\tmp` lalu lihat pakai Read.
2. **7 Tahap berurutan** (Tahap 0 → 7). Tuntaskan tiap tahap. Update checklist + progress log.
3. **Output di-embed** via `jupyter nbconvert --execute --inplace` (kernel venv, cwd=folder submission), tanpa error.
4. **Reproducibility:** `tf.keras.utils.set_random_seed(42)` di awal notebook.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Setup env Victus: ✅ SELESAI (2026-07-18)**
  - venv `.venv/` Python 3.11.9 via `python -m venv` (uv tidak ada di device ini).
  - Install: `tensorflow 2.21.0, pillow 12.3.0, numpy 2.4.6, matplotlib 3.11.1, seaborn 0.13.2, scikit-learn 1.9.0, jupyter, ipykernel, nbconvert`. Kernel `bimo_fruits` terdaftar.
  - **TFJS di Windows (pelajaran baru):** `tensorflowjs` terbaru narik `uvloop` (via flax→orbax) yang TIDAK support Windows → gagal build. Versi 4.22.0 pun sama. **SOLUSI:** install `tensorflowjs==4.22.0 --no-deps` di **main venv** + `tf-keras tensorflow-hub`, lalu **PATCH 2 file** agar import opsional: `tf_saved_model_conversion_v2.py` (baris 28: `import tensorflow_decision_forests` → try/except) & `converters/__init__.py` (import `jax_conversion` → try/except). TFDF & jax tidak dibutuhkan untuk CNN. **Verified: konversi SavedModel→TFJS berhasil.**
- **Tahap 1 — Dataset Fruits-360: ✅ SELESAI (2026-07-18)**
  - Blobless sparse-checkout dari `github.com/Horea94/Fruit-Images-Dataset` → `d:\tmp\Fruit-Images-Dataset`. 10 kelas, ~6.399 gambar 100×100.
- **Tahap 2-4 — EDA + Split + Pipeline: ✅ SELESAI (2026-07-18)**
  - Split: Training→train(4.070)+val(721) stratified 85/15 seed 42; Test bawaan→test(1.608). Anti-bocor (folder Test = sesi foto beda).
  - EDA: distribusi per kelas, grid contoh, ukuran gambar konfirmasi seragam 100×100.
  - Pipeline `image_dataset_from_directory` 100×100 batch 32 + `train_eval_ds` (tanpa shuffle utk akurasi jujur).
- **Tahap 5 — Notebook + Model + Training: ✅ SELESAI (2026-07-18)** — `submission/notebook.ipynb` (34 sel, 5 plot embedded, 0 error, 2,27 MB).
  - Model Sequential: `Rescaling → MobileNetV2(frozen 2,26jt) → Conv2D(32) → MaxPool → GAP → Dropout(0.2) → Dense(10)`. Total 2,63jt, trainable 369rb.
  - Training: EarlyStopping monitor `val_accuracy` patience 3, max 12 epoch (berhenti epoch ~4). Waktu ~1-2 menit CPU.
  - **HASIL: Train 100% / Test 100%** → kriteria #4 (≥85%) TERCAPAI ✅ (Fruits-360 clean + split Test terpisah = angka jujur).
- **Tahap 6 — Inference TFLite: ✅ SELESAI (embedded)** — grid 3×3, 9/9 correct, confidence ~100%. Saran #6 terpenuhi.
- **Tahap 7 — Packaging: ✅ SELESAI (2026-07-18)** — `Proyek_Akhir_Klasifikasi_Buah_Bimo_Bramantyo.zip` (**38,53 MB, 14 file, 1 folder root, separator `/` aman lintas OS**).
  - Isi: notebook.ipynb + notebook.py (valid ast.parse) + requirements.txt + README.md + saved_model/ (22 MB) + tflite/ (model.tflite 9,9 MB + label.txt) + tfjs_model/ (model.json + 3 shards, 10 MB).
- **🏆 HASIL AKHIR: ⭐⭐⭐ (Pass) — kriteria utama penuh:** K1 dataset 6.399 (>1.000, buah, bukan RPS/X-Ray) · K2 split train/val/test · K3 Sequential+Conv2D+Pooling · K4 Train & Test 100% (>85%) · K5 plot acc/loss · K6 3 format. Bonus otomatis: #1 callback ES, #5 10 kelas, #6 inference 9/9.
- **SISA: user upload zip ke Dicoding** (jangan submit berkali-kali; review ±3 hari kerja). Zip belum di-commit ke Git (artefak berat).
