# 📘 PANDUAN COLAB — Fine-tune IndoBERT (Skema 4)

**Untuk siapa:** Bimo Bramantyo — Proyek Analisis Sentimen Shopee (Dicoding Fundamental DL).
**Tujuan:** Menjalankan Skema 4 (IndoBERT fine-tune) di **Google Colab GPU T4** karena laptop lokal tidak punya GPU.

**Estimasi waktu total:** 20-30 menit (setup 5 mnt + training 15-25 mnt).

---

## 🎯 Yang akan kamu dapat

Dua file JSON hasil fine-tune yang nanti aku load ke notebook lokal:
- `indobert_metrics.json` — akurasi train + test + F1 + classification report.
- `indobert_history.json` — loss & acc per epoch (untuk plot kurva belajar).

Target: **train & test > 92%** → memenuhi saran #2 Dicoding.

---

## 🚀 Langkah step-by-step

### 1. Buka Colab

- Ke [https://colab.research.google.com/](https://colab.research.google.com/) dan login dengan akun Google.
- Klik **File → New notebook**.

### 2. Ganti runtime ke GPU T4 (WAJIB)

- Menu bar: **Runtime → Change runtime type**
- **Hardware accelerator:** pilih **T4 GPU**.
- Klik **Save**.

Verifikasi runtime GPU (jalankan di cell pertama):

```python
!nvidia-smi
```

Kamu harus lihat `Tesla T4` dan `15360 MiB` VRAM. Kalau muncul error/kosong, ulangi step 2.

### 3. Upload file yang dibutuhkan

Di sidebar kiri Colab, klik **📁 Files** → drag & drop dua file dari komputermu:
- `dataset_shopee_labeled.csv` (dari folder `submission/`)
- `indobert_train_colab.py` (dari folder `submission/indobert_colab/`)

Atau jalankan cell ini untuk upload:

```python
from google.colab import files
uploaded = files.upload()   # pilih kedua file dari komputermu
```

### 4. Install library

Jalankan cell ini:

```python
!pip install -q transformers==4.44.2 datasets==2.20.0 accelerate==0.33.0 scikit-learn pandas numpy torch
```

### 5. Jalankan skrip fine-tune

Cell terakhir — tinggal panggil skripnya:

```python
!python indobert_train_colab.py
```

Kamu akan lihat progress seperti:
```
Device: cuda
  GPU  : Tesla T4
  VRAM : 15.8 GB
Load labeled: 24,570 baris
Split 80/20 -> train 19,656  test 4,914
Load tokenizer + model: indobenchmark/indobert-base-p1
=== Training 3 epoch ===
  ep1 step 100/1229 loss=0.6xxx acc=0.7xxx
  ...
[epoch 1] train loss=0.4xxx acc=0.8xxx | val loss=0.3xxx acc=0.9xxx
...
=== FINAL EVALUATION ===
Train accuracy : 0.97xx
Test  accuracy : 0.92xx  ← target >92% ✅
F1-macro       : 0.85xx
[SAVED] indobert_metrics.json
[SAVED] indobert_history.json
```

**Training memakan 15-25 menit** — jangan tutup tab Colab.

### 6. Download hasil

Setelah skrip selesai, jalankan cell ini untuk download 2 file JSON:

```python
from google.colab import files
files.download("indobert_metrics.json")
files.download("indobert_history.json")
```

Simpan kedua file di folder `submission/indobert_colab/` di laptopmu.

### 7. Kabari aku

Setelah kedua file JSON tersimpan di lokasi yang benar, ping aku (Claude) — aku akan re-run notebook untuk embed hasil IndoBERT ke `pelatihan_analisis_sentimen.ipynb`.

---

## ⚠️ Troubleshooting

### GPU tidak keluar / VRAM kurang
- Cek: **Runtime → Change runtime type → T4 GPU** sudah dipilih.
- Kalau muncul "GPU quota exceeded", tunggu 30-60 menit atau ganti akun.

### Session terputus / disconnected
- Colab free tier disconnect kalau tab idle > 30 menit atau session > 12 jam.
- Solusi cepat: pindah keyboard dari tab Colab tiap ~20 menit.
- Kalau disconnect di tengah training, ulangi dari step 5.

### OOM (Out of Memory)
- Edit `indobert_train_colab.py`: turunkan `BATCH_SIZE` dari `16` → `8` (dan tambah `gradient_accumulation_steps=2` kalau perlu).

### Akurasi jauh dari target (mis. test < 88%)
- Cek `dataset_shopee_labeled.csv` yang di-upload sudah versi terbaru (24.570 baris, kolom `text_clean`, `label`).
- Coba naikkan `EPOCHS` dari `3` → `4`.

---

## 📊 Config yang dipakai

| Parameter | Nilai | Alasan |
|---|---|---|
| Model | `indobenchmark/indobert-base-p1` | Standar Indonesian BERT (Fareynaldi terbukti) |
| `max_len` | 128 | Rata2 ulasan 15 kata; 128 cukup untuk 99% |
| `batch_size` | 16 | Aman untuk T4 15GB (bisa 32 kalau max_len 64) |
| `epochs` | 3 | BERT fine-tune biasanya cukup 2-4 epoch |
| `learning_rate` | 2e-5 | Standar untuk fine-tune BERT |
| `warmup` | 10% steps | Linear scheduler dgn warmup |
| `fp16` | True | Percepat training di T4 (~2x) |
| Input teks | `text_clean` | Preprocessed clean+slang, TANPA stem |

---

## 🎁 Bonus: kalau mau simpan model

Kalau mau simpan model fine-tuned untuk dipakai inference nanti (opsional, tidak untuk zip submission):

```python
model.save_pretrained("indobert_shopee_finetuned/")
tokenizer.save_pretrained("indobert_shopee_finetuned/")

# Compress dan download
!tar czf indobert_shopee.tar.gz indobert_shopee_finetuned/
files.download("indobert_shopee.tar.gz")
```

Ukuran model IndoBERT ~500 MB. **JANGAN masukin ke zip submission** — cukup metrics JSON.

Semangat! 🚀
