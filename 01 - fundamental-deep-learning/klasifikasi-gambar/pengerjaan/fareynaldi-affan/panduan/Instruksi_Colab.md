# 🚀 Instruksi Menjalankan di Google Colab — Fareynaldi (Garbage Classification)

Notebook `submission/notebook.ipynb` sudah siap, tapi **wajib dijalankan di Google Colab (GPU T4)** karena butuh GPU untuk melatih 15.515 gambar. Ikuti langkah ini pelan-pelan.

## Langkah menjalankan

1. Buka <https://colab.research.google.com> → **File → Upload notebook** → pilih `notebook.ipynb`.
2. **Aktifkan GPU:** menu **Runtime → Change runtime type → Hardware accelerator → T4 GPU → Save.**
3. **Jalankan semua:** menu **Runtime → Run all.**
   - Sel awal mengunduh dataset via `kagglehub` (~240 MB) — otomatis, tanpa login.
   - Training 2 fase (feature extraction lalu fine-tuning) makan waktu ± **20–40 menit** di T4. Sabar, jangan tutup tab.
4. **Cek hasil** di sel Evaluasi (bagian 8):
   - Target: **Train & Test ≥ 95%** → muncul tulisan `>> Target akurasi train & test >= 95% TERCAPAI`.
   - Kalau di antara 85–95%: masih lulus tapi belum bintang penuh — kabari Nazhif/Claude untuk tuning.
5. **Pastikan tidak ada sel yang error** (semua sel ada output, tidak ada tulisan merah `Traceback`).

## Yang harus diunduh & dibawa balik

Setelah Run All selesai tanpa error, ambil DUA hal:

1. **Notebook yang sudah tereksekusi:** menu **File → Download → Download .ipynb** (ini versi dengan semua output ter-embed — WAJIB, jangan pakai yang belum dijalankan).
2. **File model:** di panel **Files** (ikon folder kiri), cari **`garbage_models.zip`** → klik kanan → **Download**.

Taruh KEDUA file itu di folder `fareynaldi/submission/`, lalu kabari Claude untuk lanjut **packaging** (bikin `notebook.py`, `requirements.txt`, `README.md`, susun folder, zip).

## ⚠️ Penting soal submit

- **Batas upload Dicoding cuma 25 MB.** File model 3 format (SavedModel + TFLite + TFJS) pasti lebih besar dari itu.
- **Solusi (direkomendasikan Dicoding):** upload zip final ke **Google Drive**, set share **"Anyone with the link → Viewer"**, lalu di Dicoding pilih **"Gunakan link"** dan tempel link-nya. Tes link di jendela incognito dulu (pastikan bisa diunduh tanpa login).
- **Submit sekali saja** — review Dicoding makan ±3 hari kerja.

## Kalau akurasi < 95% setelah run (opsi tuning)
- Tambah epoch fine-tuning (`EPOCHS_PHASE2`).
- Turunkan `FINE_TUNE_AT` (mis. 100) supaya lebih banyak layer EfficientNet ikut dilatih.
- Coba lepas `class_weight` (kadang menaikkan akurasi headline walau kelas minoritas sedikit turun).
- Kabari Claude — jangan utak-atik sendiri kalau ragu.
