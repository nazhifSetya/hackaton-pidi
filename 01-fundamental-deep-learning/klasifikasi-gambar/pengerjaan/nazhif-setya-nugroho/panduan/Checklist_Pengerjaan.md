# 📋 Checklist Pengerjaan — Proyek Klasifikasi Gambar (Animals-10)

> Update file ini setiap satu tahap selesai. Status: ⬜ belum / 🔄 sedang / ✅ selesai.

## Tahap 0 — Perencanaan & Setup ✅
- [x] Baca semua instruksi Dicoding (`artifacts/`)
- [x] Kunci target: ⭐⭐⭐⭐⭐ (semua 6 saran)
- [x] Kunci environment: training di Google Colab GPU, persiapan/packaging di M1
- [x] Riset dataset (4 agen web) → **Animals-10** dipilih user
- [x] Buat CLAUDE.md + struktur folder

## Tahap 1 — Dataset: unduh & verifikasi ✅
- [x] Setup venv M1 (`.venv/`, pyenv 3.10.20; kagglehub, pillow, pandas, matplotlib, tensorflow, jupyter)
- [x] Unduh Animals-10 via `kagglehub` → `~/.cache/kagglehub/datasets/alessiocorrado99/animals10/versions/2`
- [x] Verifikasi first-hand: **26.179 gambar** (✓ ≥10rb), **10 kelas** (✓ ≥3), **1.002 ukuran (w,h) unik** di seluruh dataset (✓ jelas tidak seragam; lebar 169–640, tinggi 105–640)
- [x] Scan integritas 26.179 file: **0 korup**. Ekstensi: 24.209 jpeg / 1.919 jpg / 51 png
- [x] Distribusi kelas dicatat (cane/anjing 4.863 … elefante/gajah 1.446) → perlu penanganan imbalance
- [ ] Rename folder Italia → Inggris (dilakukan di notebook/Colab, bukan di cache lokal)

## Tahap 2 — EDA ✅ (prototype M1 diverifikasi visual + sudah ditulis ke notebook)
- [x] Distribusi jumlah gambar per kelas (bar chart) — diverifikasi visual via Read
- [x] **Bukti resolusi tidak seragam** (scatter w×h + 12 ukuran tersering) — 374 ukuran unik dari 2.000 sampel; ada foto raksasa ~5.400×3.600 ← saran #2
- [x] Grid contoh gambar per kelas — isi kelas benar semua
- [x] Ditulis ke notebook + narasi temuan (imbalance 3,4:1, resolusi beragam, format campuran)

## Tahap 3 — Preprocessing & Split ✅ (logika diverifikasi via prototype M1; eksekusi penuh di Colab)
- [x] Split **train / validation / test 80/10/10** per kelas (stratified, seed 42) + rename folder Italia→Inggris
- [x] Augmentasi **HANYA di train** (RandomFlip/Rotation/Zoom) + sel visualisasi asli-vs-augmentasi
- [x] Pipeline `image_dataset_from_directory` 224×224 batch 64 (resize saat load, file asli utuh)
- [x] `train_eval_ds` terpisah (tanpa augmentasi/shuffle) utk ukur akurasi train yang jujur
- [x] Pencegahan crash: SEMUA 26.179 gambar lolos `tf.io.decode_image` (0 gagal)

## Tahap 4 — Model & Training ✅ SELESAI (run Colab 2026-07-09, TF 2.20.0 GPU T4)
- [x] Model **Sequential + [Rescaling → MobileNetV2(frozen) → Conv2D(256) → MaxPooling2D → GAP → Dropout → Dense]** — prototype jalan di M1 (1 epoch subset: val 84%)
- [x] **Callback**: EarlyStopping + ModelCheckpoint + ReduceLROnPlateau ← saran #1
- [x] Training 2 fase: feature extraction (8 epoch, lr 1e-3) → fine-tune layer ≥100 (s.d. 15 epoch, lr 1e-5)
- [x] **HASIL: Train 98,13% / Val 96,94% / Test 96,61% → ≥95% TERCAPAI** ← saran #4 (gap train-test ~1,5%, tidak overfitting)
- [x] Plot akurasi & loss gabungan 2 fase + garis target 95% ← kriteria wajib
- [x] Classification report + confusion matrix (pantau kelas minoritas)

## Tahap 5 — Konversi 3 Format ✅ di notebook / ⏳ eksekusi di Colab
- [x] **SavedModel** via `model.export()` — terverifikasi jalan di M1 (TF 2.21)
- [x] **TF-Lite** dari SavedModel + `label.txt` — terverifikasi jalan di M1 (21 MB)
- [x] **TFJS** via `tensorflowjs_converter` — install PALING AKHIR (setelah training) agar aman
- [x] Sel zip `animals10_models.zip` utk bawa hasil balik ke M1

## Tahap 6 — Inference + Bukti ✅ di notebook / ⏳ eksekusi di Colab
- [x] Sel inference TF-Lite: 9 gambar test acak → grid prediksi vs label asli + confidence — pola terverifikasi di M1 ← saran #6

## Tahap 7 — Packaging ✅ SELESAI (2026-07-09)
- [x] Notebook `.ipynb` FULL dijalankan di Colab (Run All, 0 error, output ter-embed) — diverifikasi Claude
- [x] Export `.py` dari notebook (nbconvert; magic Colab dikomentari agar valid Python; ast.parse OK)
- [x] `requirements.txt` (tensorflow==2.20.0 + kagglehub/tensorflowjs/numpy/matplotlib/seaborn/scikit-learn/Pillow)
- [x] README.md (template Dicoding: dataset/arsitektur/hasil/format/cara jalan)
- [x] Model 3 format di-extract & load-test lokal (TFLite invoke OK softmax=1.0, SavedModel signatures OK, label 10=output 10)
- [x] Susun struktur folder → **`Nazhif_Setya_Nugroho_submission.zip`** (80 MB, 16 berkas, 1 folder)
- [x] Audit final: semua hard-rule + 6 saran PASS

## Peta 6 Saran (⭐⭐⭐⭐⭐)
| # | Saran | Status |
|---|---|---|
| 1 | Callback | ✅ ES + ModelCheckpoint + ReduceLROnPlateau |
| 2 | Resolusi asli tidak seragam | ✅ EDA cetak ukuran (1.002 ukuran unik) |
| 3 | ≥10.000 gambar | ✅ by design (26.179) |
| 4 | Akurasi train & test ≥95% | ✅ Train 98,13% / Test 96,61% |
| 5 | ≥3 kelas | ✅ by design (10 kelas) |
| 6 | Inference + bukti | ✅ inference TFLite 9 gambar (output ter-embed) |
