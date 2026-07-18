# 📋 Checklist Pengerjaan — Klasifikasi Gambar Buah (Bimo Bramantyo)

Target: **⭐⭐⭐ (Pass)** — kriteria utama saja. Dataset: Fruits-360 (10 kelas buah). Env: Victus lokal CPU.
**STATUS: ✅ SELESAI SEMUA (2026-07-18). Sisa: user upload zip ke Dicoding.**

## Tahap 0 — Setup Environment
- [x] venv `.venv/` Python 3.11.9 (`python -m venv`)
- [x] Install tensorflow + pillow numpy matplotlib seaborn scikit-learn jupyter ipykernel nbconvert
- [x] Daftarkan kernel Jupyter `bimo_fruits`
- [x] tensorflowjs==4.22.0 (--no-deps + patch TFDF & jax opsional) → konversi TFJS verified

## Tahap 1 — Dataset
- [x] Download Fruits-360 (sparse-checkout GitHub, tanpa Kaggle)
- [x] Pilih 10 kelas → Training ~4.791 + Test ~1.608
- [x] QC: 100×100 seragam, 0 korup

## Tahap 2 — EDA
- [x] Distribusi jumlah gambar per kelas (bar chart)
- [x] Grid contoh gambar tiap kelas
- [x] Cek ukuran gambar (100×100 seragam)

## Tahap 3 — Split train/val/test
- [x] Train+Val dari `Training/` (stratified 85/15, seed 42) → 4.070 / 721
- [x] Test dari `Test/` bawaan → 1.608

## Tahap 4 — Preprocessing pipeline
- [x] `image_dataset_from_directory` 100×100 batch 32
- [x] Rescaling di dalam model; augmentasi tidak dipakai (dataset sudah bervariasi via rotasi)

## Tahap 5 — Model + Training
- [x] Prototype verify-first → akurasi ≥85% (100%)
- [x] notebook.ipynb: Sequential(MobileNetV2 frozen + Conv2D + MaxPool + GAP + Dropout + Dense)
- [x] Train max 12 epoch + EarlyStopping
- [x] Plot akurasi & loss (2 subplot)
- [x] Confusion matrix + classification report

## Tahap 6 — Simpan 3 format + inference
- [x] SavedModel (`model.export()`) 22 MB
- [x] TFLite + label.txt 9,9 MB
- [x] TFJS (model.json + 3 shards) 10 MB
- [x] Inference bukti (grid 3×3, 9/9 correct)

## Tahap 7 — Packaging
- [x] notebook.ipynb sudah di-run (5 plot embedded, 0 error)
- [x] notebook.py via nbconvert (ast.parse OK)
- [x] requirements.txt
- [x] README.md
- [x] Zip 1 folder root, separator `/` → `Proyek_Akhir_Klasifikasi_Buah_Bimo_Bramantyo.zip` 38,53 MB

## Verifikasi Akhir (HARD RULES)
- [x] Akurasi train & test ≥85% (100% / 100%)
- [x] .ipynb + .py keduanya ada
- [x] 3 format model lengkap
- [x] requirements.txt ada
- [x] 1 folder zip, path pakai `/` (aman lintas OS)
