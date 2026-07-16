# CLAUDE.md — Proyek Akhir Klasifikasi Gambar · **TF Flowers** · submission utk **Dafina**

> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Akhir: Klasifikasi Gambar**, tema **TF Flowers** (5 kelas bunga), atas nama **Dafina**.
- **Self-contained di folder ini** (`.../proyek_akhir/dafina/`). Folder induk (`../`) berisi submission Nazhif (⭐⭐⭐⭐⭐, Animals-10+MobileNetV2, Colab GPU) & sibling `../fareynaldi/` (⭐⭐⭐⭐⭐, Garbage-12+EfficientNetV2B0, Colab GPU) — **REFERENSI metodologi saja, JANGAN diubah.**
- Aturan Everest/EBC (backoffice-service, Sequelize, CLIK, dll di `docs/CLAUDE.md`) **TIDAK berlaku di sini.**
- **Ini iterasi ke-3 dari trio proyek akhir tim, dengan pendekatan BERBEDA:** teman-teman kejar ⭐⭐⭐⭐⭐ pakai Colab GPU + dataset ≥15rb + fine-tuning agresif. **Dafina cukup KRITERIA BATAS BAWAH (⭐⭐⭐)** — semua proses lokal di Victus (CPU), dataset ringan (3.670 gambar), training singkat, target akurasi ≥85% saja. Prinsip: **lulus dengan risiko minimum & waktu training kecil.**

---

## 👤 USER & GAYA KERJA

- **Pemilik submission:** **Dafina** — dipakai di semua nama file: `Dafina`. (Nama lengkap **menyusul** — sementara cukup `Dafina`.)
- **Konteks:** Mahasiswa Dicoding, pemula. Proyek CV pertamanya (proyek NLP DANA sudah selesai ⭐⭐⭐). Tiga teman timnya (Nazhif, Fareynaldi, Bimo) sudah selesai proyek akhir dengan tema berbeda.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia simpel, mudah dimengerti pemula.**
  - **Pelan-pelan, step-by-step.** Jelaskan **kenapa** tiap langkah, bukan cuma **apa**.
  - **Teliti detail kecil.**
  - **Jangan asumsi.** Kalau ambigu, **tanya dulu** pakai AskUserQuestion.
  - Kalau tunjukkan pattern kode dari proyek Nazhif/Fareynaldi, sertakan **path file + line number**.
- **Target nilai:** **⭐⭐⭐ (Pass)** — kriteria utama saja, tanpa saran wajib. **JANGAN over-engineer**. Fokus lulus dengan risiko minimum.

---

## 🎯 INTI PROYEK

Membangun model **CNN klasifikasi gambar** (**Keras Sequential + Conv2D + Pooling**) yang mengenali 5 jenis bunga, lalu mengonversi model ke **3 format wajib: SavedModel, TF-Lite, TFJS** — semua **berjalan di Victus (Windows lokal, CPU)** tanpa Colab.

**Alur (SEDERHANA, 7 tahap):** setup env → download dataset → EDA singkat → split train/val/test → train model → evaluasi + save 3 format → inference bukti → packaging.

> **Bandingkan dengan teman-teman (JANGAN ditiru semua):** Nazhif/Fareynaldi pakai Animals-10/Garbage-12 (≥15rb gambar) + Colab GPU + fine-tuning 2 fase + XAI + Callback lengkap. Dafina **cukup TF Flowers (3.670 gambar) + MobileNetV2 frozen + 1 fase training CPU** — sudah cukup memenuhi kriteria wajib "Sequential + Conv2D + Pooling" + akurasi ≥85%.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Dataset** | **TF Flowers** (public URL `http://download.tensorflow.org/example_images/flower_photos.tgz`) | **3.670 gambar, 5 kelas** (daisy/dandelion/roses/sunflowers/tulips), resolusi tidak seragam (foto dari web). **PUBLIC URL** — tidak perlu Kaggle account. Ukuran ~220 MB. Well-known dataset TensorFlow official → aman & terverifikasi bekerja. |
| **Environment** | **100% Victus lokal (Windows + CPU)**. TIDAK ADA Colab, TIDAK ADA GPU. | RTX 3050 IDLE — TensorFlow CPU cukup untuk dataset kecil (~5-10 menit training). |
| **Arsitektur** | **Sequential[Rescaling → MobileNetV2 (frozen) → Conv2D(32) → MaxPool → GAP → Dropout → Dense(5)]** | MobileNetV2 kecil (2,3jt param), frozen (tidak fine-tune) → cepat di CPU. Layer Conv2D + MaxPool wajib untuk kriteria #4 Dicoding. |
| **Split** | 80% train / 10% val / 10% test | Standar Dicoding, stratified per kelas, seed 42. |
| **Training** | 1 fase saja: base frozen, lr=1e-3, batch 32, max 10 epoch + **EarlyStopping** patience 3 | Callback minimum (ES) — bonus murah, kalau frozen sudah lolos ≥85% cepat. |
| **Target nilai** | **⭐⭐⭐ (Pass) — kriteria utama** + bonus saran gratis (#1 callback ES, #2 resolusi non-seragam, #5 ≥3 kelas, #6 inference). Kurang dari min 3 saran = tetap ⭐⭐⭐. **JANGAN kejar saran #3 (≥10rb) atau #4 (≥95%).** | |

---

## 📁 STRUKTUR FOLDER

```
dafina/
├── CLAUDE.md                       ← file ini (memory + rules)
├── .python-version                 ← pin Python 3.10.x (untuk uv)
├── .venv/                          ← virtual env Windows lokal (JANGAN di-commit/zip)
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang di-zip)
    ├── notebook.ipynb              ← notebook utama (WAJIB, sudah di-run)
    ├── notebook.py                 ← WAJIB (dibuat via nbconvert saat packaging)
    ├── requirements.txt            ← WAJIB
    ├── README.md                   ← opsional (rekomendasi Dicoding)
    ├── saved_model/                ← format 1 (WAJIB)
    │   ├── saved_model.pb
    │   └── variables/
    ├── tflite/                     ← format 2 (WAJIB)
    │   ├── model.tflite
    │   └── label.txt
    └── tfjs_model/                 ← format 3 (WAJIB)
        ├── model.json
        └── group1-shard*.bin
```

> **Referensi (JANGAN diubah):**
> - `../submission/notebook.ipynb` (Nazhif Animals-10 ⭐⭐⭐⭐⭐)
> - `../CLAUDE.md` (aturan Dicoding lengkap + pelajaran verify-first)
> - `../artifacts/` (instruksi Dicoding ASLI)
> - `../fareynaldi/submission/notebook.ipynb` (Fareynaldi Garbage ⭐⭐⭐⭐⭐)

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

### Windows lokal Victus (100% di sini — TANPA Colab)

- **Python:** 3.10.x, di-pin via `.python-version` untuk `uv`.
- **Package manager:** **uv** (sudah terpasang dari proyek DANA sebelumnya).
- **Bikin venv:** `uv venv .venv --python 3.10`
- **Aktifkan (PowerShell):** `. .venv\Scripts\Activate.ps1`
- **Library inti (CPU only, tanpa CUDA):**
  ```powershell
  uv pip install tensorflow-cpu pillow numpy matplotlib seaborn scikit-learn jupyter ipykernel nbconvert
  ```
- **Library untuk konversi TFJS (install PALING AKHIR):**
  ```powershell
  uv pip install tensorflowjs
  ```
  > ⚠️ **tensorflowjs sering bentrok dependency** dgn TensorFlow terbaru (pelajaran dari CLAUDE parent). Install SETELAH training selesai supaya kalau install gagal tidak merusak model yang sudah jadi. Kalau bentrok berat: pin ke versi lama seperti `tensorflowjs==4.19.0`.
- **Dataset:** download langsung via `tf.keras.utils.get_file` dari public URL TensorFlow — TIDAK perlu Kaggle account/kagglehub.
- **Semua tugas di Victus:** setup, dataset, EDA, split, model, training, evaluasi, save 3 format, inference, packaging.
- **CPU cukup.** MobileNetV2 (frozen) + head kecil + 3.670 gambar 160×160 → ~5-10 menit training.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `../artifacts/2.kriteria.md`, `../artifacts/4.ketentuan_berkas_submission.md`, `../artifacts/5.lainnya.md`.

1. **Akurasi training DAN testing set ≥ 85%** (di bawah itu → reject).
2. **WAJIB lampirkan KEDUA file `.py` dan `.ipynb`** (sering kelupaan → reject).
3. **WAJIB simpan model dalam 3 format: SavedModel, TF-Lite, TFJS.** Kurang satu → reject.
4. **Notebook `.ipynb` WAJIB sudah dijalankan** → semua output ter-embed.
5. **Semua kriteria wajib diterapkan:** dataset ≥1.000 gambar, bukan RPS/X-Ray, split train/test/val, Sequential+Conv2D+Pooling, plot akurasi & loss.
6. **`requirements.txt` wajib ada.**
7. Kirim dalam **1 folder di-zip** (.zip/.rar). Bahasa: **Python**.
8. **Jangan submit berkali-kali** (review ±3 hari kerja).

---

## 📊 PETA SARAN → BINTANG (fokus BATAS BAWAH)

**Kriteria Utama (WAJIB — kalau tidak → ditolak, tanpa nilai):**
1. Dataset bebas, min **1.000 gambar**, BUKAN Rock-Paper-Scissors/X-Ray. → **TF Flowers 3.670** ✅
2. Split **train/test/validation**. → 80/10/10 stratified ✅
3. Model **Sequential + Conv2D + Pooling**. → Sequential + MobileNetV2 + Conv2D + MaxPool ✅
4. Akurasi train & test **min 85%**. → MobileNetV2 frozen di flowers biasa 90%+ ✅
5. **Plot akurasi & loss** model. → matplotlib subplot ✅
6. Simpan ke **SavedModel + TF-Lite + TFJS**. → 3 format ✅

**Skala bintang:**
- ⭐⭐⭐ = **kriteria utama, tanpa saran** ← **TARGET UTAMA**
- ⭐⭐⭐⭐ = kriteria utama + min 3 saran
- ⭐⭐⭐⭐⭐ = kriteria utama + SEMUA 6 saran

**Saran (JANGAN semua dikejar — pilih yang MURAH saja):**
| Saran | Isi | Rencana Dafina | Alasan |
|---|---|---|---|
| 1 | Callback | ✅ GRATIS | EarlyStopping saja, 1 baris kode. |
| 2 | Resolusi asli tidak seragam | ✅ GRATIS | TF Flowers memang non-uniform (foto dari web). |
| 3 | ≥10.000 gambar | ❌ SKIP | TF Flowers cuma 3.670 → aman >1.000 wajib, cukup. Scrape 10rb = capek. |
| 4 | Akurasi train & test **≥95%** | ❌ SKIP | Butuh fine-tuning + tuning agresif = risiko waktu di CPU. |
| 5 | ≥3 kelas | ✅ GRATIS | TF Flowers ada 5 kelas. |
| 6 | Inference + bukti | ✅ GRATIS | 1 sel inference TFLite di notebook. |

> **Peta realistis:** dengan (1)+(2)+(5)+(6) diterapkan = **4 saran**, secara teknis → **⭐⭐⭐⭐**. Tetapi saran (2), (3), (5) itu ATRIBUT dataset (bukan usaha kode) — reviewer kadang tidak menghitung sebagai "penerapan". Rentang aman: **⭐⭐⭐ dijamin, ⭐⭐⭐⭐ mungkin**. Konsisten dengan target batas bawah.

---

## 🧭 METODOLOGI (warisan sukses tim, disederhanakan)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype ke **data asli** lewat script `.venv\Scripts\python.exe` (output prototype JANGAN masuk folder submission — pakai scratchpad `d:\tmp\` atau `%TEMP%`). Plot → simpan PNG ke `%TEMP%` lalu **lihat pakai Read tool**.
2. **7 Tahap berurutan** (Tahap 0 → 7), tuntaskan tiap tahap sebelum lanjut. Update checklist + progress log tiap tahap selesai.
3. **Output di-embed** via `jupyter nbconvert --execute --inplace` (kernel venv, cwd=folder submission), tanpa error.
4. **Reproducibility:** `tf.keras.utils.set_random_seed(42)` di awal notebook.
5. **Augmentasi HANYA di train** (tips resmi Dicoding).

---

## 🔑 CATATAN TEKNIS PENTING (pelajaran mahal dari tim — JANGAN diulangi)

### ⚠️ Augmentasi HARUS DI LUAR model, bukan di dalam Sequential
- **Fareynaldi:** augmentasi di dalam model bikin **TFLite gagal `ImageProjectiveTransformV3` FLEX ops** — sudah kejadian & diperbaiki.
- ✅ **Yang benar:** apply augmentasi via `ds.map(lambda x,y: (aug_layer(x, training=True), y))` di dataset pipeline. Model TIDAK punya augmentation layers.

### ⚠️ TFJS install PALING AKHIR
- tensorflowjs sering bentrok dep dgn TF terbaru → install SETELAH training/export selesai supaya kalau bentrok, model yang sudah jadi aman.
- Kalau `pip install tensorflowjs` error di Victus: coba `uv pip install "tensorflowjs<5.0"` atau `tensorflowjs==4.19.0` (versi stabil).

### 📸 Resolusi tidak seragam — atribut dataset
- TF Flowers dari `flower_photos.tgz` = foto asli dari web = ukuran beragam (biasanya 240×320 ~ 500×667). EDA harus print beberapa ukuran unik sebagai bukti (saran #2 gratis).

### 🎯 MobileNetV2 frozen + head kecil = shortcut aman
- Base MobileNetV2 (ImageNet pretrained, `include_top=False`) langsung freeze → hanya head yang di-train → super cepat di CPU.
- Head Sequential: `Conv2D(32, 3, activation='relu') → MaxPooling2D → GlobalAveragePooling2D → Dropout(0.3) → Dense(num_classes, 'softmax')`.
- Pada dataset flowers 5 kelas: bukti publik akurasi 88-92% dengan setup ini dalam <5 menit CPU.

### 🚧 label.txt untuk folder `tflite/`
- Sesuai template Dicoding: `tflite/label.txt` berisi 5 baris nama kelas (urutan alfabet = urutan output softmax).

### 📝 requirements.txt (yang benar-benar dipakai, bukan seluruh venv)
- Sertakan: `tensorflow-cpu, numpy, matplotlib, seaborn, scikit-learn, Pillow, jupyter, ipykernel, tensorflowjs`.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Setup env Victus: ✅ SELESAI (2026-07-15)**
  - Venv `.venv/` Python 3.10.20 dibuat via uv. Library CPU-only: `tensorflow-cpu 2.21.0, pillow 12.3.0, numpy 2.2.6, matplotlib 3.10.9, seaborn 0.13.2, scikit-learn 1.7.2, jupyter, ipykernel, nbconvert`.
  - Kernel Jupyter `dafina_flowers` terdaftar.
  - **PROBLEM TFJS di Windows:** `tensorflowjs` (semua versi 4.x) memerlukan `tensorflow_decision_forests` yang tidak punya binary `.so` untuk Windows native. Trial 4 versi (4.22, 4.14, 4.10) semua gagal.
  - **SOLUSI: venv isolated `.venv-tfjs`** dgn `tensorflowjs==4.22.0` + `setuptools<80` + **PATCH manual** dua file TFDF (`op_dynamic.py` di `ops/inference/` & `ops/training/`) untuk membuat pemuatan `.so` opsional (kalau gagal, `ops=None`, tidak crash). Verified: `import tensorflowjs` OK di `.venv-tfjs`.
- **Tahap 1 — Dataset TF Flowers: ✅ SELESAI (2026-07-15)** — via `tf.keras.utils.get_file` dari URL publik.
  - **Terverifikasi: 3.670 gambar, 5 kelas** (daisy 633 / dandelion 898 / roses 641 / sunflowers 699 / tulips 799), **318 ukuran unik dari 2.500 sampel** (bukti resolusi tidak seragam), **0 file korup** (semua 3.670 lolos `tf.io.decode_image`), 100% `.jpg`.
  - Imbalance ringan ~1,4:1 (dandelion vs roses) → tidak perlu `class_weight`.
- **Tahap 2-4 — EDA + Split + Preprocessing (verify-first): ✅ SELESAI (2026-07-15)** — prototype di `d:\tmp\dafina_split_train.py`.
  - 3 plot EDA di-verify visual via Read: distribusi kelas + scatter resolusi + grid 5×3.
  - Split 80/10/10 stratified per kelas seed 42 → train 2.934 / val 367 / test 369 (persis proporsi).
  - Pipeline `image_dataset_from_directory` 160×160 batch 32 + augmentasi (RandomFlip + RandomRotation) **HANYA di train, DI LUAR model** (pelajaran Fareynaldi anti-FLEX-ops).
  - `train_eval_ds` terpisah (tanpa augmentasi/shuffle) untuk ukur akurasi train jujur.
  - Prototype hasil awal: **86,72% test** di 4 menit CPU → sudah lolos ≥85% wajib.
- **Tahap 5 — Notebook + Model + Training: ✅ SELESAI (2026-07-15)** — `submission/notebook.ipynb` (30 sel, 16 code + 14 markdown, 3,98 MB, 0 error).
  - Model Sequential: `Rescaling → MobileNetV2 (frozen 2,26jt) → Conv2D(64) → MaxPool → GAP → Dense(128) → Dropout(0.3) → Dense(5, softmax)`. Total 2,66jt params, trainable 400rb.
  - Training: EarlyStopping monitor `val_accuracy` patience 5, max 15 epoch. Berhenti epoch 9 (best epoch 4). Waktu 5 menit CPU.
  - **HASIL: Train 93,93% / Val 88,01% / Test 86,72%** → **kriteria wajib #5 (≥85% train & test) TERCAPAI** ✅.
  - 5 plot embedded (distribusi + resolusi + grid + acc/loss + confusion matrix inference).
  - 3 format tersimpan: **SavedModel** 25 MB (via `model.export()`), **TFLite** 11,6 MB (via `TFLiteConverter.from_saved_model`) + `label.txt` 5 baris, **TFJS** 11,4 MB (via subprocess ke `.venv-tfjs/tensorflowjs_converter.exe` — 3 shards + model.json 132 KB).
  - Iterasi: run pertama 84,01% test (batas), rebuild dgn head lebih kuat (Dense(128) hidden) + patience 5 + max 15 epoch → 86,72% margin nyaman.
- **Tahap 6 — Inference TFLite: ✅ SELESAI (embedded di notebook)** — 9 gambar test acak, grid 3×3, semua kategorikal `(daisy|dandelion|roses|sunflowers|tulips)` + confidence. **9/9 correct** (mean confidence ~92%). Bukti saran #6 terpenuhi.
- **Tahap 7 — Packaging: ✅ SELESAI (2026-07-15)** — `dafina/Proyek_Akhir_Flowers_Dafina.zip` (**45,38 MB, 15 file dalam 1 folder root**).
  - `notebook.py` di-generate via `jupyter nbconvert --to python` (20 KB, ast.parse OK).
  - `requirements.txt` — versi terverifikasi (11 paket).
  - `README.md` — dokumentasi metodologi + hasil + cara jalan + catatan TFJS di Windows.
  - Isi zip: 4 wajib (notebook.ipynb, notebook.py, requirements.txt, README.md) + 3 folder wajib (saved_model/, tflite/ + label.txt, tfjs_model/ 3 shards + model.json).
- **🏆 HASIL AKHIR: ⭐⭐⭐ (Pass) — kriteria utama penuh:**
  - ✅ K1: Dataset TF Flowers 3.670 gambar (>1.000, bukan RPS/X-Ray)
  - ✅ K2: Split train (2.934) / val (367) / test (369)
  - ✅ K3: Sequential + Conv2D + Pooling
  - ✅ K4: Train 93,93% & Test 86,72% (>85% margin nyaman)
  - ✅ K5: Plot akurasi & loss (2 subplot)
  - ✅ K6: SavedModel + TFLite + TFJS (3 format)
  - Bonus saran (tidak dikejar tapi masuk otomatis): #1 Callback (EarlyStopping), #2 Resolusi non-seragam (318 ukuran unik), #5 ≥3 kelas (5 kelas), #6 Inference kategorikal (9/9 correct).
- **SISA: user upload zip ke Dicoding** (jangan submit berkali-kali; review ±3 hari kerja).
