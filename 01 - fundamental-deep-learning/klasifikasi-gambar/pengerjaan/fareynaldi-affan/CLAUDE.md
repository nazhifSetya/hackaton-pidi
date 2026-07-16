# CLAUDE.md — Proyek Akhir Klasifikasi Gambar (versi FAREYNALDI)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + rules untuk submission Fareynaldi.** Baca seluruhnya di awal tiap sesi.
> **Update [Progress Log](#-progress-log) tiap tahap selesai.**

---

## ⛔ SCOPE & KONTEKS PENTING

- Ini submission **Dicoding "Belajar Fundamental Deep Learning" → Proyek Akhir: Klasifikasi Gambar**, dibuat **UNTUK FAREYNALDI** (teman Nazhif), atas permintaan Nazhif (2026-07-09).
- **HUBUNGAN dengan folder induk:** ini varian KEDUA. Submission Nazhif (parent `../submission/`) pakai **Animals-10 + MobileNetV2**. Submission Fareynaldi ini **SENGAJA DIBIKIN BEDA** biar aman dari **deteksi plagiarisme Dicoding** (yang membandingkan antar-submission siswa).
- **Aturan `Everest/CLAUDE.md` & `docs/CLAUDE.md` TIDAK berlaku di sini** (ini bukan aplikasi Everest/EBC).
- Metodologi & kriteria Dicoding sama persis dengan parent → lihat `../CLAUDE.md` dan `../artifacts/` untuk aturan Dicoding lengkap. **Jangan duplikat artifacts.**

## 🔑 PEMBEDA DARI SUBMISSION NAZHIF (anti-plagiarisme) — dipilih user 2026-07-09

| Aspek | Nazhif (Animals-10) | **Fareynaldi (INI)** |
|---|---|---|
| Dataset | Animals-10 (10 kelas hewan, 26.179) | **Garbage Classification `mostafaabla/garbage-classification` (12 kelas sampah, 15.515)** |
| Base model | MobileNetV2 | **EfficientNetV2B0** |
| Preprocessing | layer `Rescaling(1/127.5,-1)` | **tanpa Rescaling** (EfficientNetV2 `include_preprocessing` bawaan, input [0,255]) |
| Kepala model | Conv2D(256)→MaxPool→GAP→Dropout→Dense(256)→Dense | **Conv2D(128)→BatchNorm→MaxPool→Conv2D(64)→GAP→Dropout(0.4)→Dense(128)→Dropout(0.3)→Dense** |
| Augmentasi | Flip/Rotation(0.1)/Zoom(0.15) | **Flip/Rotation(0.15)/Zoom(0.2)/RandomContrast(0.1)** |
| Imbalance | 3,4:1 → TIDAK pakai class_weight | **8,8:1 → PAKAI `class_weight` balanced** |
| Fine-tune | unfreeze layer ≥100 (dari 155) | **unfreeze ≥150 (dari 270) + SEMUA BatchNorm dibekukan** |
| Batch size | 64 | **32** |
| TFLite | float32 (21 MB) | **Optimize.DEFAULT / terkuantisasi (~8 MB)** |

User memilih diferensiasi **"dataset beda + arsitektur beda (paling aman)"**.

## 🎯 TARGET & KRITERIA
- Target: **⭐⭐⭐⭐⭐** (semua 6 saran). Sama seperti parent.
- HARD RULE (auto-reject kalau langgar): akurasi train & test ≥85%; wajib `.py` + `.ipynb`; wajib 3 format (SavedModel/TFLite/TFJS); notebook sudah dijalankan (output ter-embed); `requirements.txt` ada; 1 folder di-zip.
- 6 saran: (1) Callback ✓ ES+MC+RLR, (2) resolusi tidak seragam ✓ (420+ ukuran unik), (3) ≥10rb ✓ (15.515), (4) akurasi ≥95% (dicek setelah Colab), (5) ≥3 kelas ✓ (12), (6) inference + bukti ✓ (TFLite 9 gambar).

## 📁 STRUKTUR
```
fareynaldi/
├── CLAUDE.md                    ← file ini
├── panduan/
│   ├── Checklist_Pengerjaan.md
│   └── Instruksi_Colab.md
└── submission/
    ├── notebook.ipynb           ← WAJIB (sudah dibuat, belum dijalankan di Colab)
    ├── notebook.py              ← WAJIB (dibuat saat packaging)
    ├── requirements.txt         ← WAJIB (dibuat saat packaging)
    ├── saved_model/ tflite/ tfjs_model/   ← dari Colab
    └── README.md
```

## 🧭 METODOLOGI (warisan sukses)
1. **VERIFY-FIRST** — prototype dulu sebelum tulis ke notebook; plot dicek via Read.
2. Augmentasi HANYA di train, **DI LUAR model** (kalau di dalam model → TFLite gagal `ImageProjectiveTransformV3` FLEX ops — sudah kejadian & diperbaiki).
3. Seed 42 di mana-mana. Notebook final harus Run All tanpa error di Colab.
4. Training di Colab GPU T4 (EfficientNetV2B0 lebih berat dari MobileNetV2, batch 32).

## ⚠️ CATATAN TEKNIS
- EfficientNetV2B0 = 270 layer, 59 BatchNorm. Weights ImageNet ~24 MB (auto-download).
- **Nama lengkap Fareynaldi**: ⛔ BELUM DIKONFIRMASI user — dibutuhkan untuk header notebook & nama zip final (`Nama_Lengkap_submission.zip`). Tanya sebelum packaging.
- Batas upload Dicoding **25 MB** → 3 format model pasti > itu → **submit via link Google Drive** (sama seperti Nazhif). Ada di Instruksi_Colab.
- Kalau setelah run test <95%: lever tuning = tambah epoch fine-tune / turunkan FINE_TUNE_AT (unfreeze lebih banyak) / evaluasi apakah class_weight menurunkan akurasi headline (bisa dilepas kalau perlu).

## ✅ PROGRESS LOG

- **Tahap 0–1 — Setup & Dataset: ✅ SELESAI (2026-07-09, verified first-hand)**
  - Keputusan: dataset Garbage Classification, arsitektur EfficientNetV2B0 (beda dari Nazhif), class_weight utk imbalance.
  - Dataset diunduh `~/.cache/kagglehub/.../mostafaabla/garbage-classification/versions/1/garbage_classification`.
  - **Terverifikasi: 15.515 gambar, 12 kelas, 892 ukuran unik (full scan; sampel 3000 → 420 unik), 0 korup, semua .jpg.** Imbalance 8,8:1 (clothes 5.325 vs brown-glass 607).
- **Tahap 2 — Prototype arsitektur (M1): ✅ SELESAI (2026-07-09)**
  - EfficientNetV2B0 + Conv2D/Pool: fit OK (val 62% 1 epoch subset), `model.export()` OK, TFLite convert OK **8,2 MB** (Optimize.DEFAULT), inference out [1,12] softmax=1.0.
  - Bug ketemu & diperbaiki: augmentasi di dalam model bikin TFLite gagal (FLEX ops) → dipindah ke pipeline dataset.
  - class_weight balanced + fine-tune (unfreeze≥150, BN beku → 95/270 trainable) terverifikasi jalan.
- **Tahap 3 — Notebook lengkap: ✅ DITULIS & DIVERIFIKASI (2026-07-09), ⏳ menunggu Fareynaldi run di Colab**
  - `submission/notebook.ipynb` (53 sel, 27 kode) — generator: scratchpad `build_nb_fareynaldi.py`. Struktur mirror bintang-5 Nazhif, diadaptasi garbage+EfficientNet+class_weight.
  - nbformat valid, semua sel kode lolos ast.parse. 3 plot EDA (distribusi/resolusi/grid 6×6) dirender dgn data asli & **dicek visual via Read** — benar semua.
  - **NEXT:** Fareynaldi Run All di Colab → cek train&test ≥95% → bawa balik `notebook.ipynb` (ter-eksekusi) + `garbage_models.zip` → Claude packaging (notebook.py, requirements.txt, README, zip, audit). **Minta nama lengkap Fareynaldi dulu.**
- **Tahap 4 — Colab run + Packaging: ✅ SELESAI (2026-07-09)**
  - Fareynaldi sudah Run All di Colab (TF **2.20.0**, GPU T4). Hasil dibawa balik: `notebook (1).ipynb` (tereksekusi) + `garbage_models.zip` (90 MB).
  - **HASIL AKURASI (terverifikasi Claude): Train 99,16% / Val 97,28% / Test 95,64%** → target ≥95% train & test TERCAPAI. Notebook 53 sel, **0 error**; semua plot ter-embed (distribusi/resolusi/grid/augmentasi/acc-loss/confusion matrix/inference).
  - Model 3 format load-test M1: TFLite [1,224,224,3]→[1,12] softmax=1.0; SavedModel sig serve/serving_default; label.txt 12 == output 12; TFJS graph-model 8 shard. Semua OK.
  - Nama lengkap dikonfirmasi user: **Fareynaldi Affan**. Header notebook diupdate; `notebook.ipynb` ditimpa versi tereksekusi; `notebook.py` (430 baris, magic dikomentari, ast.parse OK); `requirements.txt` (+scikit-learn) + `README.md` dibuat.
  - Zip transport dibuang → **`Fareynaldi_Affan_submission.zip`** (96 MB, 19 berkas, 1 folder `submission/`). **Audit: SEMUA hard-rule + 6 saran PASS.** ✅ SIAP SUBMIT (via link Google Drive, >25 MB). Reminder: submit sekali saja.
