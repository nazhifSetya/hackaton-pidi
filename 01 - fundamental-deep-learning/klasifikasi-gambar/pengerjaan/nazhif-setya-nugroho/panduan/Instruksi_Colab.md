# 🚀 Instruksi Menjalankan Notebook di Google Colab

> File yang dijalankan: `submission/notebook.ipynb`
> Estimasi total waktu: **±45–75 menit** (unduh dataset ~5 mnt, salin & split ~5 mnt, training 2 fase ~30–60 mnt, konversi & inference ~5 mnt).

## Langkah-langkah

1. **Buka Colab** → https://colab.research.google.com → `File > Upload notebook` → pilih `submission/notebook.ipynb`.

2. **Aktifkan GPU** → menu `Runtime > Change runtime type` → Hardware accelerator: **T4 GPU** → Save.

3. **Run All** → menu `Runtime > Run all` (atau Ctrl+F9). Biarkan berjalan sampai selesai.
   - Sel pertama akan menampilkan `GPU: [PhysicalDevice(...)]` — kalau kosong `[]`, berarti GPU belum aktif, ulangi langkah 2 lalu `Runtime > Restart and run all`.
   - Training fase 1 (8 epoch) lalu fase 2 fine-tuning (sampai 15 epoch, biasanya berhenti lebih awal karena EarlyStopping).

4. **Cek hasil bagian 8.1 (Evaluasi)** — pastikan muncul:
   ```
   >> Target akurasi train & test >= 95% TERCAPAI
   ```
   Kalau yang muncul "Kriteria minimal 85%..." (belum 95%), **berhenti di sini dan kabari saya** — jangan submit dulu, kita tuning bareng.

5. **Cek bagian 10 (Inference)** — grid 9 gambar dengan prediksi; idealnya 8-9/9 benar (hijau).

6. **Unduh 2 file ini dari Colab:**
   - **Notebook yang sudah tereksekusi**: `File > Download > Download .ipynb` → timpa/simpan sebagai `notebook.ipynb`.
   - **`animals10_models.zip`** (berisi saved_model/, tflite/, tfjs_model/): dari panel **Files** (ikon folder di kiri) → klik titik tiga → Download. Ukurannya bisa ±100–200 MB.

7. **Taruh kedua file itu di folder `submission/`** di laptop (timpa `notebook.ipynb` lama), lalu kabari saya → saya lanjutkan packaging (export `.py`, `requirements.txt`, README, susun struktur, zip final).

## Kalau ada error

- **Error saat `pip install tensorflowjs` / `tensorflowjs_converter`** (bagian 9.3): jangan panik — training & TF-Lite sudah selesai dan aman. Screenshot errornya, kirim ke saya.
- **Runtime terputus di tengah training**: model terbaik tersimpan di `best_model.keras` (ModelCheckpoint), tapi paling sederhana: `Runtime > Restart and run all` ulang dari awal.
- **Sesi habis / lambat**: pastikan pakai T4 (gratisan cukup), jangan buka tab Colab lain yang aktif.

## Kenapa desainnya begini? (ringkas)

- **kagglehub** tanpa API key → tidak perlu upload kaggle.json.
- **Augmentasi hanya di train** → sesuai tips resmi Dicoding, test set tetap murni.
- **Akurasi train diukur tanpa augmentasi** → angka yang dilaporkan jujur.
- **tensorflowjs di-install paling akhir** → kalau dependency-nya bentrok, training yang sudah jalan tidak terpengaruh.
- **Seed 42 di mana-mana** → hasil bisa direproduksi.
