# 🚀 Panduan Menjalankan PGABL (Dafina) di Google Colab

> Panduan step-by-step dari **nol** sampai **siap upload Dicoding**. Ikuti berurutan.
> Ditujukan untuk pemula — tiap langkah dijelaskan **kenapa**-nya, bukan cuma **apa**-nya.

---

## 🗺️ Gambaran Besar (baca dulu 1 menit)

Ada **2 notebook** yang dijalankan **berurutan** (wajib SFT dulu, baru RAG):

| Urutan | Notebook | Isi | Estimasi |
|---|---|---|---|
| 1️⃣ | `Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb` | K1: melatih model (SFT) → push ke Hugging Face | ~60–90 menit |
| 2️⃣ | `RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb` | K2+K3: sistem RAG + antarmuka tanya-jawab | ~15–25 menit |

**Kenapa SFT dulu?** Notebook RAG memanggil model hasil SFT dari Hugging Face. Kalau modelnya belum ada, RAG gagal.

**Kenapa harus Colab (bukan laptop Victus)?** Melatih model 1,5 miliar parameter butuh VRAM besar. RTX 3050 (4 GB) tidak cukup; Colab kasih **GPU T4 (16 GB) gratis**.

**Alur besar:**
```
Daftar akun HF → Setup Colab → Run SFT → (model di HF) → Upload 4 PDF ke Drive → Run RAG → Zip → Upload Dicoding
```

---

## BAGIAN 1 — Daftar Akun Hugging Face (punya Dafina sendiri) 🔑

> **Kenapa akun sendiri?** Demi anti-plagiarisme Dicoding: token & repo model **wajib milik Dafina**, bukan meminjam akun Nazhif/Fareynaldi. Kalau pakai akun orang lain, bisa dianggap kolusi.

### 1.1 Buat akun
1. Buka **https://huggingface.co/join**
2. Isi **Email**, **Password**, lalu **Username**.
   - ⚠️ **Catat username ini baik-baik** — nanti jadi nilai `HF_USERNAME`. Username muncul di URL profilmu: `huggingface.co/<username>`.
3. Cek email → klik link verifikasi.

### 1.2 Buat Access Token (peran **Write**)
1. Login → klik foto profil (kanan atas) → **Settings**.
2. Menu kiri → **Access Tokens** → tombol **+ Create new token**.
3. Pilih tipe **Write** (atau *Fine-grained* dengan izin write ke repo).
   - **Kenapa Write?** Karena kita akan **meng-upload (push)** model ke akunmu. Token *Read* tidak bisa membuat/menulis repo.
4. Beri nama bebas (mis. `colab-pgabl`) → **Create token**.
5. **Copy token** yang muncul (bentuknya `hf_xxxxxxxx...`).
   - ⚠️ Token ini **hanya tampil sekali**. Simpan sementara di notepad. Kalau hilang, tinggal buat token baru.

> 🔒 **JANGAN** menempel token ini ke dalam kode notebook atau commit ke Git. Kita pakai **Colab Secret** (Bagian 2.3). Token bocor = auto-reject + akun berisiko.

Sekarang kamu punya **dua hal**: `HF_USERNAME` (username) dan `HF_TOKEN` (`hf_...`).

---

## BAGIAN 2 — Setup Colab ⚙️

### 2.1 Buka notebook di Colab
Cara paling gampang (**upload file**):
1. Buka **https://colab.research.google.com**
2. Menu **File → Upload notebook**.
3. Pilih file dari laptop:
   `...\pengerjaan\dafina\submission\Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb`

*(Alternatif: File → Open notebook → tab GitHub → tempel `nazhifSetya/hackaton-pidi` → pilih notebook → lalu **Save a copy in Drive** supaya bisa dijalankan.)*

### 2.2 Aktifkan GPU T4
1. Menu **Runtime → Change runtime type**.
2. **Hardware accelerator → T4 GPU** → **Save**.
   - **Kenapa?** Tanpa GPU, training tidak jalan / super lambat.

### 2.3 Set Colab Secrets (2 secret)
1. Klik ikon **🔑 (kunci)** di sidebar kiri Colab.
2. Tambah 2 secret:

| Name | Value | Notebook access |
|---|---|---|
| `HF_TOKEN` | token `hf_...` dari Bagian 1.2 | **ON** ✅ |
| `HF_USERNAME` | username HF-mu | **ON** ✅ |

   - ⚠️ Pastikan toggle **Notebook access** kedua secret **menyala**, kalau tidak notebook tak bisa baca.
   - **Kenapa Secret?** Supaya token tidak pernah tertulis di kode (aman + memenuhi aturan Dicoding).

---

## BAGIAN 3 — Jalankan Notebook 1: Fine-tuning (SFT) 🏋️

Klik **Runtime → Run all**. Notebook jalan dari atas ke bawah. Berikut yang terjadi + **output yang harus kamu lihat**:

| Section | Yang terjadi | Output yang benar |
|---|---|---|
| **0 + install** | Pasang Unsloth dkk (~3–5 mnt) | Banyak log pip. **Kadang muncul "RESTART SESSION"** |
| **1. Autentikasi** | Login ke HF | `Terautentikasi sebagai : <username-mu>` |
| **2. Parameter** | Set konstanta + cek GPU | `Akselerator : Tesla T4` |
| **3. Muat model** | Download Qwen2.5-1.5B 4-bit (~2–3 mnt) | `Model 4-bit dimuat: ...Qwen2.5-1.5B-Instruct` |
| **4. LoRA** | Pasang adapter | `Porsi dilatih : ~1–3%` |
| **5. Dataset** | Download data Bahasa Indonesia | `Dipakai melatih : 8000` |
| **6. Chat template** | Format ChatML + **bukti token** | Harus terlihat `<\|im_start\|>`, `<\|im_end\|>` + `[ADA] token spesial ...` |
| **7. SFTTrainer** | Siapkan pelatih | `Total langkah : 800` |
| **8. Training** | **Latih 800 langkah (~60–90 mnt)** | Tabel `loss` yang **menurun** bertahap |
| **9. Merge + push** | Gabung & upload model (~5–10 mnt) | `Model terunggah: https://huggingface.co/...` |
| **10. Link** | Tulis `link_huggingface.txt` | Cetak URL model |

### ⚠️ Kalau muncul "RESTART SESSION" setelah sel install
Ini **normal** untuk Unsloth. Lakukan:
1. **Runtime → Restart session**.
2. Setelah restart, **Runtime → Run all** lagi (dari atas).
   - **Kenapa?** Unsloth mengganti sebagian library, perlu restart supaya versi baru terpakai. Ini "pola 2× Run All".

### ⏳ Saat training (Section 8)
- Butuh 60–90 menit. **Jangan tutup tab, jangan biarkan laptop sleep** — Colab memutus sesi kalau idle terlalu lama.
- Nilai `loss` harus **turun** perlahan (mis. dari ~2.0 ke ~1.x). Kalau turun konsisten & tidak ada error `CUDA out of memory`, **kriteria Basic sudah aman**.

### ✅ Bukti WAJIB yang harus ada (Section 6)
Rubrik mensyaratkan **satu baris dataset terformat dengan token spesial tercetak**. Di notebook ini itu di Section 6 — pastikan kamu lihat `<|im_start|>` dan `<|im_end|>`. Kalau bagian ini error, jangan lanjut — beri tahu saya.

### 🔎 Verifikasi hasil push
Setelah Section 9, buka URL yang tercetak (`https://huggingface.co/<username>/PGABL-Qwen2.5-1.5B-SFT-Dafina`). Di tab **Files** harus ada file bobot model utuh: untuk model 1,5 B ini biasanya **satu file `model.safetensors` (~3 GB)** (model lebih besar bisa terpecah `model-00001-of-000XX.safetensors`). Yang penting **BUKAN** cuma `adapter_model.safetensors` (itu berarti gagal merge).
- **Kenapa penting?** Rubrik wajib model `merged_16bit` (bobot penuh), bukan cuma adapter LoRA. Notebook sudah mengurus ini otomatis (pola dua langkah + hapus adapter).

---

## BAGIAN 4 — Upload 4 PDF ke Google Drive 📄

Notebook RAG membaca 4 PDF regulasi dari **Drive** (bukan dari repo).

Cukup **satu folder** (tidak perlu bertingkat):

1. Buka **https://drive.google.com** (login akun Google yang **sama** dengan yang dipakai di Colab).
2. Di **My Drive**, klik **+ New → New folder** → beri nama **persis** `PGABL_Dafina` → **Create**.
   - ⚠️ Nama persis `PGABL_Dafina` (huruf besar/kecil diperhatikan). Pastikan folder ada di **My Drive**, **bukan** di dalam "Colab Notebooks" atau "Shared with me".
3. **Klik dua kali** masuk ke folder `PGABL_Dafina`, lalu upload **4 PDF langsung ke dalamnya** (klik **+ New → File upload**, atau seret-lepas). Ambil dari laptop di `...\pengerjaan\dafina\data\raw\`:
   - `PP_5_2021.pdf`
   - `PP_35_2021.pdf`
   - `PP_51_2023.pdf`
   - `UU_6_2023.pdf`
   - ⚠️ Nama file **harus persis** seperti di atas (notebook mencarinya berdasarkan nama ini).
4. Hasil akhir: keempat PDF berada langsung di `MyDrive/PGABL_Dafina/` (tanpa subfolder).

> **Kenapa lewat Drive?** File PDF besar (UU 6/2023 ~82 MB) tidak disimpan di Git. Drive tempat paling praktis agar Colab bisa membacanya.

---

## BAGIAN 5 — Jalankan Notebook 2: RAG + Antarmuka 💬

> Jalankan **hanya setelah** Notebook 1 selesai (model sudah ada di Hugging Face).

1. Upload/buka `RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb` di Colab.
2. Pastikan **T4 GPU** aktif + **Secret HF_TOKEN & HF_USERNAME** sudah ada (Bagian 2).
3. **Runtime → Run all**. Yang terjadi:

| Section | Yang terjadi | Output benar |
|---|---|---|
| install | Pasang pypdf, sentence-transformers, faiss, dll | log pip |
| **2. PDF Drive** | Minta izin **Mount Drive** → cek 4 PDF | Muncul popup izin Drive → *Allow*. Lalu `[OK] PP_5_2021 ...` |
| **3. Loader** | Ekstrak teks per halaman | `Total halaman terekstrak: ...` |
| **4. Chunker** | Potong berbasis kalimat + **bukti overlap** | `Jumlah potongan: ...` + contoh ekor/awal yang sama |
| **5. Embedder** | Muat e5-base + encode semua potongan | progress bar `Batches: 100%` |
| **6. FAISS** | Bangun indeks vektor lokal | `Vektor dalam indeks: ...` |
| **7. Retriever** | Uji pencarian | daftar `[1] PP_35 hal-.. (skor=..)` |
| **8. Generator** | Muat model SFT Dafina dari HF | `Generator siap: ...SFT-Dafina` |
| **10. Demo** | 4 pertanyaan contoh dijawab | 4 blok jawaban + rujukan |
| **11. `input()` loop** | **Antarmuka interaktif** | kotak input muncul |

### 💬 Di sel antarmuka (Section 11)
- Muncul kotak `Pertanyaan Anda:`. **Ketik minimal 2–3 pertanyaan**, tekan Enter tiap kali, lihat jawaban + rujukan muncul.
  - Contoh: *"Bagaimana ketentuan upah lembur?"*, *"Apa itu perizinan berbasis risiko?"*
- Ketik **`keluar`** lalu Enter untuk mengakhiri.
  - **Kenapa harus ketik beberapa pertanyaan?** Supaya transkrip tanya-jawab **ter-embed** di notebook sebagai bukti antarmuka berfungsi (reviewer tidak menjalankan ulang).

> ℹ️ **Wajar kalau jawaban model kadang kurang tajam** — modelnya kecil (1,5 B) dan target kita Basic. Yang dinilai = pipeline RAG **berjalan** (retrieval → prompt → generate → tampil), bukan kesempurnaan jawaban.

---

## BAGIAN 6 — Packaging & Upload Dicoding 📦

### 6.1 Download hasil dari Colab
Untuk **tiap** notebook (yang sudah selesai Run All, **output masih tampil**):
- Menu **File → Download → Download .ipynb**.
- Simpan menimpa file di `...\pengerjaan\dafina\submission\`.
- ⚠️ Pastikan yang di-download adalah versi yang **sudah ada outputnya** (jangan yang kosong).

### 6.2 Ambil link Hugging Face
- Di Colab Notebook 1, panel **Files** (ikon folder kiri) → cari `/content/link_huggingface.txt` → download; **atau**
- Cukup edit file `submission/link_huggingface.txt` di laptop: ganti `<HF_USERNAME>` dengan username asli, jadi:
  `https://huggingface.co/<username-asli>/PGABL-Qwen2.5-1.5B-SFT-Dafina`

### 6.3 Zip **flat** (4 file, tanpa subfolder)
Isi zip harus **persis 4 file di root** (bukan folder di dalam folder):
```
PGABL_Dafina_Meira_Rizkia.zip
├── Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb
├── RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb
├── link_huggingface.txt
└── requirements.txt
```
Cara di Windows: masuk folder `submission/`, **pilih ke-4 file** (Ctrl+klik), klik kanan → **Send to → Compressed (zipped) folder** → rename `PGABL_Dafina_Meira_Rizkia.zip`.
- ⚠️ Pilih **file-nya**, bukan foldernya — kalau folder yang di-zip, isinya jadi bertingkat (melanggar aturan).

*(Kalau mau, minta saya buatkan zip-nya otomatis setelah 2 notebook selesai di-download.)*

### 6.4 Checklist final sebelum upload
- [ ] 2 notebook `.ipynb` **ada outputnya** (tidak kosong)
- [ ] Section 6 SFT: token `<|im_start|>`/`<|im_end|>` terlihat
- [ ] Repo HF **publik** + ada `model-*.safetensors` (bukan cuma adapter)
- [ ] `link_huggingface.txt` berisi URL asli (bukan `<HF_USERNAME>`)
- [ ] Zip **flat** 4 file
- [ ] Upload ke halaman submission Dicoding

---

## 🆘 Troubleshooting

| Masalah | Solusi |
|---|---|
| `AssertionError: HF_TOKEN belum di-set` | Cek Secret di ikon 🔑 + toggle **Notebook access** ON |
| Muncul minta **Restart session** | Restart → Run all lagi (normal untuk Unsloth) |
| `CUDA out of memory` | Runtime → Restart, jalankan ulang. Kalau tetap: turunkan `BATCH_PER_GPU` ke 1 di Section 2 — **JANGAN** turunkan `JUMLAH_LANGKAH` (minimal 800) |
| Download model dari HF **stall/lama** | Restart runtime & ulang; koneksi HF kadang lambat. Pastikan `HF_TOKEN` benar |
| Sesi Colab terputus saat training | Harus **Run all ulang** (versi Basic tanpa checkpoint). Jalankan saat koneksi stabil, tab jangan ditutup |
| `PDF hilang: ...` di Notebook 2 | Cek folder Drive persis `MyDrive/PGABL_Dafina/` (4 PDF langsung di dalamnya, tanpa subfolder) + nama file persis |
| Repo HF isinya cuma `adapter_*` | Ulangi Section 9 SFT (notebook sudah pakai pola merge + `delete_patterns`). Kalau masih, beri tahu saya |

---

## 📌 Ringkas 1 Layar

1. Daftar HF → catat **username** + buat token **Write** (`hf_...`).
2. Colab: upload Notebook 1 → **T4 GPU** → set Secret `HF_TOKEN` + `HF_USERNAME`.
3. **Run all** Notebook 1 (~60–90 mnt) → cek model muncul di HF.
4. Upload 4 PDF ke Drive `MyDrive/PGABL_Dafina/` (satu folder, tanpa subfolder).
5. **Run all** Notebook 2 → di sel `input()` ketik 2–3 pertanyaan lalu `keluar`.
6. Download 2 notebook (ada output) + link → **zip flat 4 file** → upload Dicoding.

> Ada yang error di tengah jalan? Screenshot pesan error + section berapa, nanti saya bantu.
