# 🚀 PANDUAN COLAB — PGABL Bimo (Basic)

Langkah menjalankan 2 notebook di **Google Colab T4** sampai jadi zip siap upload Dicoding.
Ikuti urut. Notebook Fine-tuning WAJIB duluan (menghasilkan model), baru RAG.

---

## 0. Persiapan sekali di awal (±10 menit)

1. **Akun Hugging Face (punya Bimo sendiri).** Kalau belum punya, daftar di https://huggingface.co.
2. **Buat token HF scope Write:** Settings → Access Tokens → New token → tipe **Write** → copy.
3. **Catat username HF** (mis. `bimo123`). Ini dipakai untuk nama repo model.
4. **Simpan 2 Colab Secret** (di setiap notebook: klik ikon 🔑 di sidebar kiri Colab → Add new secret, aktifkan "Notebook access"):
   - `HF_TOKEN` = token Write tadi.
   - `HF_USERNAME` = username HF Bimo.
   > ⚠️ Jangan pernah ketik token langsung di sel notebook. Wajib lewat Secret (kalau ketahuan hardcode → auto-reject Dicoding).
5. **Upload 4 PDF regulasi ke Google Drive.** Buat folder `MyDrive/PGABL_Bimo/` lalu upload:
   `PP_5_2021.pdf`, `PP_35_2021.pdf`, `PP_51_2023.pdf`, `UU_6_2023.pdf`.
   (Sumber ada di `data/raw/` folder proyek ini.)
   > ⚠️ Pastikan nama folder Drive **tanpa spasi di belakang** (`PGABL_Bimo`, bukan `PGABL_Bimo `) — spasi tersembunyi bikin path gagal terbaca.

---

## 1. Notebook Fine-tuning (K1) — `Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb`

1. Upload notebook ke Colab (File → Upload notebook).
2. **Runtime → Change runtime type → T4 GPU → Save.**
3. Pastikan Colab Secret `HF_TOKEN` & `HF_USERNAME` aktif untuk notebook ini (ikon 🔑).
4. **Runtime → Run all.**
   - Sel pertama meng-install Unsloth dkk. Kalau Colab minta **restart session** setelah install → klik restart, lalu **Run all lagi** (pola 2× Run All normal).
5. Tunggu training **800 steps** (± 45–90 menit di T4). Jangan tutup tab.
6. Di akhir, model di-push ke `https://huggingface.co/<username>/PGABL-Phi-3.5-mini-SFT-Bimo`.
   - **Verifikasi:** buka link itu → pastikan **Public** + ada file `model-0000x-of-0000x.safetensors` (model utuh, bukan cuma `adapter_*`).
7. Sel terakhir menuliskan `link_huggingface.txt`. Catat URL-nya.
8. **File → Download → Download .ipynb** (yang SUDAH ada output) → nanti timpa file di `submission/`.

**Kalau OOM (VRAM habis):** di sel SFTTrainer turunkan `per_device_train_batch_size` 2→1 (dan naikkan `gradient_accumulation_steps` 4→8 supaya efektif tetap 8). **JANGAN turunkan `max_steps` di bawah 800.**

---

## 2. Notebook RAG (K2 + interface) — `RAG_submission_PGABL_Bimo_Bramantyo.ipynb`

1. Upload ke Colab, **Runtime T4**, aktifkan Secret `HF_TOKEN` & `HF_USERNAME`.
2. Pastikan model SFT dari langkah 1 sudah **Public** (RAG me-load model itu dari HF).
3. **Runtime → Run all** (restart + Run all lagi kalau diminta).
4. Cek hasil:
   - Sel loader: 4 PDF terbaca (ada `[OK]` semua).
   - Sel chunk: jumlah chunk per PDF tampil.
   - Sel **contoh Q&A**: 2–3 pertanyaan hukum dijawab (output tercetak rapi) — ini bukti output ter-embed.
   - Sel terakhir: `gr.Interface` muncul, bisa diketik pertanyaan → keluar jawaban.
5. **File → Download → Download .ipynb** (SUDAH ada output) → timpa file di `submission/`.

> Kalau download model dari HF **nge-hang** (LFS lambat): jalankan ulang sel load model; kalau parah, ganti runtime (Disconnect and delete runtime) lalu Run all lagi.

---

## 3. Packaging & Upload (±5 menit)

1. Taruh 2 notebook yang SUDAH ada output ke folder `submission/`:
   - `Fine-tuning_submission_PGABL_Bimo_Bramantyo.ipynb`
   - `RAG_submission_PGABL_Bimo_Bramantyo.ipynb`
2. Pastikan `submission/link_huggingface.txt` berisi URL model asli (Public).
3. Pastikan `submission/requirements.txt` ada.
4. **Zip flat** (4 file langsung di root zip, tanpa subfolder) → `PGABL_Bimo_Bramantyo.zip`.
   - Windows: pilih 4 file → klik kanan → Send to → Compressed (zipped) folder → rename.
5. **Upload zip ke Dicoding.**

### ✅ Checklist sebelum upload
- [ ] 2 notebook sudah **dijalankan penuh** (semua sel ada output).
- [ ] Sel bukti chat template menampilkan `<start_of_turn>` / `<end_of_turn>`.
- [ ] Repo HF **Public** & berisi model `merged_16bit` (bukan adapter).
- [ ] `link_huggingface.txt` berisi URL benar (tidak private / salah ketik).
- [ ] Tidak ada token/rahasia ke-hardcode di notebook.
- [ ] Zip **flat**, 4 file (2 ipynb + link_huggingface.txt + requirements.txt), tanpa GRPO notebook.
