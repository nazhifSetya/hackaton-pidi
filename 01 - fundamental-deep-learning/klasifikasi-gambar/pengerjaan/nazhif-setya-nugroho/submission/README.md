# Proyek Akhir: Klasifikasi Gambar — Animals-10

Submission kelas **Belajar Fundamental Deep Learning** (Dicoding).
Model **CNN (Keras Sequential + transfer learning MobileNetV2)** untuk mengklasifikasikan gambar ke **10 kelas hewan**, lalu diekspor ke **3 format**: SavedModel, TF-Lite, dan TFJS.

**Penulis:** Nazhif Setya Nugroho — dev@kalachakra.io

---

## Dataset

- **Animals-10** ([Kaggle `alessiocorrado99/animals10`](https://www.kaggle.com/datasets/alessiocorrado99/animals10)) — diunduh via `kagglehub`.
- **26.179 gambar**, **10 kelas**: butterfly, cat, chicken, cow, dog, elephant, horse, sheep, spider, squirrel.
- **Resolusi asli tidak seragam** (1.002 ukuran unik; lebar 169–640, tinggi 105–640) — dibuktikan di sel EDA.
- Split **train / validation / test = 80 / 10 / 10** (stratified per kelas, seed 42).
- **Augmentasi hanya pada train set** (RandomFlip / Rotation / Zoom).

## Arsitektur Model

`Sequential`:
`Rescaling → MobileNetV2 (pre-trained ImageNet) → Conv2D(256) → MaxPooling2D → GlobalAveragePooling2D → Dropout → Dense(10, softmax)`

**Training 2 fase:** feature extraction (base frozen, lr 1e-3) → fine-tuning (unfreeze layer ≥100, lr 1e-5).
**Callback:** EarlyStopping + ModelCheckpoint + ReduceLROnPlateau.

## Hasil

| Set | Akurasi | Loss |
|---|---|---|
| Train | **98,13 %** | 0,0601 |
| Validation | 96,94 % | 0,1181 |
| Test | **96,61 %** | 0,1364 |

> Melampaui kriteria wajib (≥85 %) dan saran bintang-5 (≥95 % train & test). Plot akurasi & loss serta confusion matrix ada di notebook.

## Format Model yang Disimpan

| Format | Lokasi |
|---|---|
| SavedModel | `saved_model/` |
| TF-Lite | `tflite/model.tflite` (+ `tflite/label.txt`) |
| TensorFlow.js | `tfjs_model/` (`model.json` + 5 shard `.bin`) |

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
