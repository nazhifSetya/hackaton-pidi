# Klasifikasi Gambar Buah 🍌🍓🍊 — Bimo Bramantyo

Submission Proyek Akhir kelas **Belajar Fundamental Deep Learning** (Dicoding).
Model CNN untuk mengenali **10 jenis buah** menggunakan dataset **Fruits-360**.

## Ringkasan

| Aspek | Detail |
|---|---|
| Dataset | [Fruits-360](https://github.com/Horea94/Fruit-Images-Dataset) — 10 kelas buah |
| Jumlah gambar | 6.399 (train 4.070 / val 721 / test 1.608) |
| Kelas | Avocado, Banana, Kiwi, Lemon, Mango, Orange, Pineapple, Raspberry, Strawberry, Watermelon |
| Arsitektur | Sequential: Rescaling → MobileNetV2 (frozen) → Conv2D → MaxPooling → GlobalAveragePooling → Dropout → Dense |
| Akurasi | **Training 100% / Testing 100%** (syarat ≥85% terpenuhi) |
| Format model | SavedModel, TF-Lite, TensorFlow.js |

## Struktur Berkas

```
notebook.ipynb      # notebook utama (sudah dijalankan, output ter-embed)
notebook.py         # versi script Python
requirements.txt    # daftar dependensi
README.md           # file ini
saved_model/        # format 1: SavedModel
tflite/             # format 2: model.tflite + label.txt
tfjs_model/         # format 3: model.json + shard .bin
```

## Cara Menjalankan

1. Buat virtual environment & install dependensi:
   ```
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```
2. Jalankan `notebook.ipynb` di Jupyter.

Dataset diunduh otomatis oleh notebook langsung dari GitHub menggunakan **git sparse-checkout**
(hanya 10 kelas yang diunduh, tanpa perlu akun Kaggle).

## Metodologi Singkat

- **Split anti-bocor:** Fruits-360 memotret satu buah yang diputar 360°, sehingga gambar dalam
  satu kelas sangat mirip. Untuk menghindari kebocoran data, train+validation diambil dari folder
  `Training/` (85%/15%), sedangkan test memakai folder `Test/` bawaan (sesi pemotretan berbeda).
- **Transfer learning:** MobileNetV2 (pra-latih ImageNet) dibekukan sebagai ekstraktor fitur, hanya
  *head* (Conv2D + Dense) yang dilatih → cepat di CPU.
- **Callback:** EarlyStopping (memantau `val_accuracy`) agar training berhenti otomatis saat optimal.
- **Inferensi:** dibuktikan menggunakan model TF-Lite pada gambar test acak.

## Catatan Teknis (TensorFlow.js di Windows)

Paket `tensorflowjs` memiliki dependensi (`tensorflow_decision_forests`, `jax`) yang tidak tersedia
sebagai wheel di Windows. Karena model ini adalah CNN (bukan decision forest / JAX), dependensi
tersebut tidak diperlukan untuk konversi. Paket dipasang tanpa dependensi opsional tersebut, dan
konversi SavedModel → TFJS berjalan normal.
