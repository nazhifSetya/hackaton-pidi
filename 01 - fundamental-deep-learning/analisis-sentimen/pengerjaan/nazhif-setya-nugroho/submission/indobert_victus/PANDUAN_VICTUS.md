# 🎮 Panduan Menjalankan IndoBERT di HP Victus (RTX 3050) — Skema 4

> **Kenapa di Victus?** Fine-tune IndoBERT butuh GPU (CUDA). MacBook M1 tidak punya CUDA,
> jadi bagian ini kamu jalankan sendiri di Victus. Nanti hasilnya (2 file JSON) dikirim
> balik ke M1 untuk digabung ke notebook.

---

## Yang kamu butuhkan
- 2 file dari folder ini: **`indobert_train_victus.py`** + **`requirements_victus.txt`**
- 1 file dataset dari M1: **`dataset_pln_labeled.csv`** (saya kasih setelah tahap labeling)
- Taruh ketiganya di **satu folder** yang sama di Victus.

---

## Langkah-langkah (Windows PowerShell / CMD)

### 1. Cek GPU terdeteksi
```powershell
nvidia-smi
```
Pastikan muncul "NVIDIA GeForce RTX 3050" + versi CUDA (mis. CUDA 12.x).

### 2. Buat virtual environment (Python 3.10/3.11)
```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
```

### 3. Install PyTorch versi CUDA (WAJIB pakai index CUDA, jangan yang CPU)
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```
Cek CUDA aktif:
```powershell
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```
Harus `True NVIDIA GeForce RTX 3050`.

### 4. Install sisa library
```powershell
pip install -r requirements_victus.txt
```

### 5. Jalankan training
```powershell
python indobert_train_victus.py
```
- Perkiraan waktu: ±15–40 menit (tergantung jumlah data & epoch).
- Kamu akan lihat progress loss per step + akurasi per epoch.
- Di akhir muncul ringkasan: `TEST acc=... f1=...`.

---

## Kalau kena error "CUDA out of memory"
VRAM 4GB memang mepet. Buka `indobert_train_victus.py`, ubah salah satu:
1. `BATCH = 4`  (paling ampuh; effective batch tetap 16 via grad-accum)
2. atau `MAX_LEN = 96`
3. atau ganti `MODEL_NAME = "indobenchmark/indobert-lite-base-p1"` (model lebih kecil, tetap IndoBERT)

Lalu jalankan ulang langkah 5.

> **Fallback total (kalau Victus bermasalah):** upload `indobert_train_victus.py` + `dataset_pln_labeled.csv`
> ke **Google Colab** (Runtime → GPU T4 gratis), install requirements, jalankan. Sama saja hasilnya.

---

## Yang dikirim balik ke M1 (untuk di-embed ke notebook)
Setelah selesai, kirim balik **2 file** ini:
- ✅ `indobert_metrics.json`  (accuracy & F1 train+test, classification report, confusion matrix)
- ✅ `indobert_history.json`  (metrik training)

Claude akan pakai file itu untuk menampilkan hasil Skema 4 di notebook utama.
(Folder `indobert_pln_model/` = model tersimpan, opsional — besar, tidak wajib dikirim.)
