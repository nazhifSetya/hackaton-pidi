# 📋 Checklist Pengerjaan — Fareynaldi (Garbage Classification)

> Status: ⬜ belum / 🔄 sedang / ✅ selesai. Dibuat beda dari submission Nazhif (anti-plagiarisme).

## Tahap 0 — Setup ✅
- [x] Keputusan dikunci: dataset Garbage Classification, base EfficientNetV2B0, class_weight (beda dari Nazhif: Animals-10 + MobileNetV2)
- [x] Target ⭐⭐⭐⭐⭐ (semua 6 saran), training Colab GPU

## Tahap 1 — Dataset ✅ (verified first-hand)
- [x] Unduh `mostafaabla/garbage-classification` via kagglehub
- [x] Verifikasi: **15.515 gambar** (✓ ≥10rb), **12 kelas** (✓ ≥3), **892 ukuran unik** (✓ resolusi beragam), **0 korup**
- [x] Imbalance dicatat: **8,8:1** (clothes 5.325 vs brown-glass 607) → pakai class_weight

## Tahap 2 — Prototype arsitektur (M1) ✅
- [x] EfficientNetV2B0 + Conv2D(128)+BN+MaxPool+Conv2D(64)+GAP+Dropout+Dense — fit OK
- [x] Bug augmentasi-di-dalam-model (TFLite FLEX ops) ditemukan & diperbaiki (augmentasi → pipeline)
- [x] class_weight + fine-tune (unfreeze≥150 + BN beku) terverifikasi
- [x] SavedModel export + TFLite convert (8,2 MB) + inference terverifikasi

## Tahap 3 — Notebook ✅ ditulis / ⏳ MENUNGGU RUN COLAB
- [x] EDA: distribusi kelas + bukti resolusi (420+ unik) + grid 6×6 — dirender & dicek visual
- [x] Split train/val/test 80/10/10 (seed 42, stratified per kelas)
- [x] Augmentasi train-only (Flip/Rotation0.15/Zoom0.2/Contrast0.1) di pipeline
- [x] Model Sequential + EfficientNetV2B0 + Conv2D + Pooling
- [x] Callback ES + ModelCheckpoint + ReduceLROnPlateau (saran #1)
- [x] class_weight balanced (imbalance handling)
- [x] Training 2 fase (frozen 8 epoch lr1e-3 → fine-tune ≤15 epoch lr1e-5)
- [x] **HASIL train & test ≥95%** (saran #4) — Train 99,16% / Val 97,28% / Test 95,64% ✅
- [x] Plot akurasi & loss (kriteria wajib) + classification report + confusion matrix
- [x] Konversi 3 format: SavedModel + TFLite(+label.txt) + TFJS
- [x] Inference TFLite 9 gambar (saran #6)

## Tahap 4 — Packaging ✅ SELESAI (2026-07-09)
- [x] Notebook `.ipynb` FULL dijalankan di Colab (TF 2.20.0, 0 error, output ter-embed) — diverifikasi Claude
- [x] Export `.py` dari notebook (magic dikomentari, ast.parse OK, 430 baris)
- [x] `requirements.txt` (tensorflow==2.20.0 + scikit-learn/kagglehub/tensorflowjs/numpy/matplotlib/seaborn/Pillow)
- [x] README.md
- [x] Nama lengkap dikonfirmasi user: **Fareynaldi Affan** → zip **`Fareynaldi_Affan_submission.zip`** (96 MB, 19 berkas)
- [x] Model 3 format load-test lokal OK (TFLite softmax=1.0, SavedModel sig OK, label 12=output 12, TFJS 8 shard)
- [x] Audit final: semua hard-rule + 6 saran PASS
- [ ] **(giliran Fareynaldi)** Upload zip ke Google Drive (>25 MB) → share "Anyone with link" → submit link di Dicoding

## Peta 6 Saran (⭐⭐⭐⭐⭐)
| # | Saran | Status |
|---|---|---|
| 1 | Callback | ✅ ES+MC+RLR |
| 2 | Resolusi tidak seragam | ✅ 892 ukuran unik |
| 3 | ≥10.000 gambar | ✅ 15.515 |
| 4 | Akurasi ≥95% | ✅ Train 99,16% / Test 95,64% |
| 5 | ≥3 kelas | ✅ 12 kelas |
| 6 | Inference + bukti | ✅ TFLite 9 gambar |
