# Proyek Akhir Klasifikasi Gambar — TF Flowers

**Submission:** Dafina · Dicoding · Belajar Fundamental Deep Learning

## Ringkasan

Model **CNN klasifikasi gambar** untuk mengenali 5 jenis bunga (**daisy, dandelion, roses, sunflowers, tulips**) menggunakan dataset **TF Flowers** (3.670 gambar) yang diunduh langsung dari URL publik TensorFlow.

## Dataset

- **Nama:** TF Flowers (Google's official dataset)
- **URL publik:** `http://download.tensorflow.org/example_images/flower_photos.tgz`
- **Total gambar:** 3.670 (≥1.000 kriteria wajib ✓)
- **Kelas (5):** daisy · dandelion · roses · sunflowers · tulips
- **Resolusi:** tidak seragam (ratusan ukuran unik dalam sampel — foto asli dari web)
- **Split:** 80% train (2.934) / 10% val (367) / 10% test (369), stratified per kelas, `seed=42`

## Arsitektur Model

Sequential CNN dengan transfer learning:
```
Input(160,160,3)
 → Rescaling(1/127.5, -1)     # normalisasi input untuk MobileNetV2
 → MobileNetV2 (frozen)        # base pretrained ImageNet
 → Conv2D(64, 3x3, ReLU)       # kepala CNN kustom
 → MaxPooling2D
 → GlobalAveragePooling2D
 → Dense(128, ReLU)
 → Dropout(0.3)
 → Dense(5, softmax)
```

- **Total params:** ~2,7 juta (frozen ~2,3 juta + trainable ~400 ribu)
- **Optimizer:** Adam (lr=1e-3)
- **Loss:** sparse_categorical_crossentropy
- **Callback:** EarlyStopping (monitor `val_accuracy`, patience 5, restore best weights)
- **Max epoch:** 15 (biasanya berhenti lebih awal)
- **Augmentasi:** RandomFlip + RandomRotation, HANYA di training set, DI LUAR model

## Hasil Evaluasi

| Split | Accuracy | Loss |
|---|---:|---:|
| Train | 93,93% | 0,17 |
| Validation | 88,01% | 0,40 |
| Test | **86,72%** | 0,40 |

**Kriteria wajib #5 (train & test ≥ 85%): TERCAPAI ✓**

Inference TF-Lite pada 9 gambar test acak: 9/9 prediksi benar.

## Format Model (3 wajib)

| Format | Path | Ukuran |
|---|---|---:|
| SavedModel | `saved_model/` | ~25 MB |
| TF-Lite | `tflite/model.tflite` (+ `label.txt`) | ~11,4 MB |
| TFJS | `tfjs_model/` (`model.json` + shards) | ~11,4 MB |

## Environment

- **Python:** 3.10.20
- **TensorFlow:** 2.21.0 (CPU-only, native Windows)
- **Perangkat:** Windows 11, dijalankan **100% lokal (CPU)** tanpa Colab/GPU
- **Waktu training:** ~5 menit di CPU laptop

**Catatan konversi TFJS:** `tensorflowjs` versi terbaru (4.22.0) memerlukan `tensorflow_decision_forests` yang tidak tersedia di Windows native. Karena itu:
1. Training dilakukan di venv utama (`.venv`) dengan TensorFlow 2.21 CPU.
2. Konversi TFJS dijalankan lewat `subprocess` yang memanggil `tensorflowjs_converter.exe` dari venv terisolasi (`.venv-tfjs`) yang telah di-patch (menonaktifkan pemuatan `.so` decision forests yang tidak kompatibel Windows).
3. Alternatif: jalankan di WSL2 atau Linux/Colab yang mendukung `tensorflow_decision_forests` native.

## Cara Menjalankan

1. Buat venv Python 3.10 dan install:
   ```
   uv pip install -r requirements.txt
   ```
   (`tensorflow-cpu` dipakai training/inference; `tensorflowjs` opsional, hanya untuk konversi TFJS di venv terisolasi.)

2. Jalankan notebook:
   ```
   jupyter nbconvert --to notebook --execute --inplace notebook.ipynb
   ```

3. Output akan menghasilkan folder `saved_model/`, `tflite/`, dan `tfjs_model/` (3 format wajib).

## Struktur Submission

```
Proyek_Akhir_Flowers_Dafina/
├── notebook.ipynb           # WAJIB — notebook utama (sudah dijalankan, output ter-embed)
├── notebook.py              # WAJIB — export .py dari notebook
├── requirements.txt         # WAJIB — dependency list
├── README.md                # rekomendasi Dicoding
├── saved_model/             # WAJIB — format 1 (SavedModel)
│   ├── saved_model.pb
│   ├── fingerprint.pb
│   ├── variables/
│   └── assets/
├── tflite/                  # WAJIB — format 2 (TF-Lite)
│   ├── model.tflite
│   └── label.txt
└── tfjs_model/              # WAJIB — format 3 (TFJS)
    ├── model.json
    └── group1-shard*.bin
```

## Kriteria Wajib Dicoding — semua terpenuhi

1. ✅ Dataset ≥ 1.000 gambar (TF Flowers 3.670) & bukan RPS/X-Ray
2. ✅ Split train / validation / test
3. ✅ Sequential + Conv2D + Pooling
4. ✅ Akurasi train & test ≥ 85% (Train 93,93% · Test 86,72%)
5. ✅ Plot akurasi & loss
6. ✅ 3 format model tersimpan (SavedModel + TF-Lite + TFJS)
