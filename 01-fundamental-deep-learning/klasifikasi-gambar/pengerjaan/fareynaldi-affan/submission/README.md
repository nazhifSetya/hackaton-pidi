# Proyek Akhir: Klasifikasi Gambar — Garbage Classification ♻️

Submission kelas **Belajar Fundamental Deep Learning** (Dicoding).
Model **CNN (Keras Sequential + transfer learning EfficientNetV2B0)** untuk mengklasifikasikan gambar sampah ke **12 kategori**, lalu diekspor ke **3 format**: SavedModel, TF-Lite, dan TFJS.

**Penulis:** Fareynaldi Affan

---

## Dataset

- **Garbage Classification** ([Kaggle `mostafaabla/garbage-classification`](https://www.kaggle.com/datasets/mostafaabla/garbage-classification)) — diunduh via `kagglehub`.
- **15.515 gambar**, **12 kelas**: battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass.
- **Resolusi asli tidak seragam** (ratusan ukuran unik; lebar 51–888, tinggi 100–936) — dibuktikan di sel EDA.
- Split **train / validation / test = 80 / 10 / 10** (stratified per kelas, seed 42).
- **Augmentasi hanya pada train set** (RandomFlip / Rotation / Zoom / Contrast), diterapkan di pipeline dataset (bukan di dalam model, agar konversi TF-Lite tidak bermasalah).
- **Imbalance ~8,8 : 1** (clothes 5.325 vs brown-glass 607) ditangani dengan **`class_weight`** balanced.

## Arsitektur Model

`Sequential`:
`EfficientNetV2B0 (pre-trained ImageNet, tanpa Rescaling — normalisasi internal) → Conv2D(128) → BatchNormalization → MaxPooling2D → Conv2D(64) → GlobalAveragePooling2D → Dropout(0.4) → Dense(128) → Dropout(0.3) → Dense(12, softmax)`

**Training 2 fase:** feature extraction (base frozen, lr 1e-3) → fine-tuning (unfreeze layer ≥150, BatchNorm tetap beku, lr 1e-5).
**Callback:** EarlyStopping + ModelCheckpoint + ReduceLROnPlateau.

## Hasil

| Set | Akurasi | Loss |
|---|---|---|
| Train | **99,16 %** | 0,0328 |
| Validation | 97,28 % | 0,1107 |
| Test | **95,64 %** | 0,1816 |

> Melampaui kriteria wajib (≥85 %) dan saran bintang-5 (≥95 % train & test). Plot akurasi & loss serta confusion matrix ada di notebook.

## Format Model yang Disimpan

| Format | Lokasi |
|---|---|
| SavedModel | `saved_model/` |
| TF-Lite | `tflite/model.tflite` (+ `tflite/label.txt`) |
| TensorFlow.js | `tfjs_model/` (`model.json` + 8 shard `.bin`) |

**Inference** didemokan memakai model **TF-Lite** pada 9 gambar test acak (sel inference di notebook).

## Struktur Berkas

```
submission/
├── notebook.ipynb      notebook utama (sudah dijalankan, output ter-embed)
├── notebook.py         export skrip Python dari notebook
├── requirements.txt    dependensi
├── README.md           berkas ini
├── saved_model/        format SavedModel
├── tflite/             model.tflite + label.txt
└── tfjs_model/         model.json + shard .bin
```

## Cara Menjalankan

Notebook dibuat & dijalankan di **Google Colab (GPU T4)**.

1. Buka `notebook.ipynb` di Google Colab.
2. Runtime → Change runtime type → **T4 GPU**.
3. Runtime → **Run all**. Dataset terunduh otomatis via `kagglehub`.

Dependensi (jika menjalankan lokal): `pip install -r requirements.txt`.
