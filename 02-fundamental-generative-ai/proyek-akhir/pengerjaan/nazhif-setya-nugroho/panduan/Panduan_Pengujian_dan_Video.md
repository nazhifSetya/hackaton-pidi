# 🎬 Panduan Pengujian Aplikasi + Rekam Video Demo

> Dokumen ini menjelaskan **step-by-step** cara menguji aplikasi Streamlit StudioAI + merekam video demo `.mp4` untuk submission BFGAI.
> Semua parameter, dropdown, dan tombol di UI dijelaskan supaya kamu paham apa fungsinya, bukan cuma "klik-klik".

---

## 📑 Daftar Isi

1. [Pra-syarat](#-pra-syarat)
2. [Alur Rekaman (script per menit)](#-alur-rekaman-script-per-menit)
3. [Penjelasan Semua Parameter di Sidebar](#-penjelasan-semua-parameter-di-sidebar)
4. [Penjelasan Semua Metode Scheduler](#-penjelasan-semua-metode-scheduler)
5. [Penjelasan Tab GENERATE](#-penjelasan-tab-generate)
6. [Penjelasan Tab EDIT (Inpainting + Outpainting)](#-penjelasan-tab-edit-inpainting--outpainting)
7. [Tips Perekaman Video](#-tips-perekaman-video)
8. [Setelah Rekaman Selesai](#-setelah-rekaman-selesai)
9. [Troubleshooting Cepat](#-troubleshooting-cepat)

---

## ✅ Pra-syarat

Sebelum mulai, pastikan:

- [ ] Colab Streamlit notebook sudah **Run All sampai selesai** tanpa error
- [ ] URL ngrok sudah **terbuka & responsif** (tidak `ERR_NGROK_3200`)
- [ ] Halaman **StudioAI** sudah muncul (bukan lagi `Running get_models()`)
- [ ] Tab GENERATE aktif secara default
- [ ] **Screen recorder siap**:
  - Windows: `Win+G` (Xbox Game Bar) — cek dulu dengan Win+Alt+R apa langsung rekam
  - Atau **OBS Studio** kalau sudah terpasang
- [ ] File demo target: `submission/video_demo_aplikasi_BFGAI.mp4`
- [ ] **Prompt astronaut** siap di clipboard (untuk copy-paste ke UI):

```
cartoon illustration of a single astronaut in white spacesuit standing alone on the surface of the moon, planet earth visible in the dark starry sky background, digital art, vibrant colors, clean bold outlines, flat shading
```

- [ ] **Negative prompt** siap di clipboard:

```
photorealistic, realistic, photograph, 3d render, messy, blurry, low quality, bad art, ugly, sketch, grainy, unfinished, chromatic aberration
```

---

## 🎥 Alur Rekaman (script per menit)

Total target durasi: **3-4 menit** (soal minta 1-5 menit).

### Sebelum tekan record — smoke test (1x, tidak direkam)

Test dulu dengan default prompt supaya yakin backend jalan:
1. Klik tombol **🚀 Initialize Generation** (biarkan default "a cute robot in a futuristic city, 8k, masterpiece")
2. Tunggu ~30 detik → panel kanan "Visual Output" harus tampil 1 gambar
3. Kalau muncul → hapus dulu (tidak perlu — akan ter-replace waktu record), lanjut ke rekaman
4. Kalau error → screenshot + lihat sesi Troubleshooting

### Setelah smoke test PASS — tekan record

Buka Xbox Game Bar (`Win+G`) → tombol Capture → ⚫ Start recording.

#### Segmen 1: **K3 Basic** (durasi ±45 detik)

| Waktu | Aksi | Bukti kriteria |
|---|---|---|
| 0:00-0:05 | Kamera fokus ke URL ngrok di address bar + judul "StudioAI: Creating Amazing Paint with Stable Diffusion" | Aplikasi live via ngrok |
| 0:05-0:15 | Scroll sidebar dari atas ke bawah tunjukkan: Parameters section, Quality Steps slider, Creativity CFG slider, Seed Control | UI komponen ada |
| 0:15-0:25 | Klik text-area **Prompt** → hapus default → paste prompt astronaut (dari clipboard) | Text input prompt ✅ |
| 0:25-0:32 | Klik text-input **Negative Prompt** → hapus default → paste negative prompt | Text input negative prompt ✅ |
| 0:32-0:38 | Set slider **Quality Steps = 30**, slider **Creativity CFG = 7.50**, **Seed Control = 222** | Slider hyperparameter ✅ |
| 0:38-0:40 | Klik tombol **🚀 Initialize Generation** | Tombol Generate ✅ |
| 0:40-1:00 | Tunggu spinner "Processing Image..." → gambar astronaut muncul di panel kanan | Gambar hasil ditampilkan langsung ✅ |

#### Segmen 2: **K3 Skilled** (durasi ±1:00 menit)

| Waktu | Aksi | Bukti kriteria |
|---|---|---|
| 1:00-1:10 | Naikkan slider **Batch Size (Jumlah Gambar)** dari 1 → **4** | num_images input ✅ |
| 1:10-1:20 | Buka dropdown **Scheduler** → tunjukkan opsi: Euler A, DPM++, DDIM → pilih **DPM++** | Dropdown scheduler ✅ |
| 1:20-1:25 | Klik **🚀 Initialize Generation** | |
| 1:25-1:55 | Tunggu proses batch → 4 gambar tampil di panel kanan dalam **grid 2×2** | Batch inference grid 2×2 ✅ |
| 1:55-2:00 | Klik tombol **🧹 Flush RAM** di sidebar bawah → toast "Memory Cleared!" muncul | Clear Memory button ✅ |

#### Segmen 3: **K3 Advanced — Inpainting** (durasi ±1:00 menit)

| Waktu | Aksi | Bukti kriteria |
|---|---|---|
| 2:00-2:10 | Klik tab **⚒ EDIT** di atas | Tab baru untuk edit ✅ |
| 2:10-2:15 | Pilih radio **Inpainting (Edit Objek)** (default) | Mode selection ✅ |
| 2:15-2:20 | Section "Draw Mask" muncul dengan **canvas menampilkan gambar hasil generate** (base image) | streamlit-drawable-canvas ✅ |
| 2:20-2:35 | Klik & drag di canvas — coret area **di kanan bawah astronaut** untuk menandai tempat inpaint | Drawable canvas berfungsi ✅ |
| 2:35-2:45 | Di panel kanan "Settings": ubah **Prompt Baru** jadi `broken satellite spacecraft`, biarkan Strength = 0.85 | Prompt input inpaint ✅ |
| 2:45-2:50 | Klik **⚡ Execute Inpainting** | |
| 2:50-3:00 | Tunggu "Processing Inpainting..." → hasil dengan satelit muncul menggantikan gambar sebelumnya | Inpainting hasil ✅ |

#### Segmen 4: **K3 Advanced — Outpainting/Zoom Out** (durasi ±30 detik, opsional bonus)

| Waktu | Aksi | Bukti kriteria |
|---|---|---|
| 3:00-3:05 | Ubah radio ke **Outpainting (Zoom Out)** | Mode kedua ✅ |
| 3:05-3:15 | Section muncul: kiri = gambar asli, kanan = form dengan prompt "wide angle view..." | Outpaint UI ✅ |
| 3:15-3:20 | Klik **🔍 Zoom Out (Expand)** | |
| 3:20-3:45 | Tunggu spinner → gambar diperluas 128px ke semua sisi (zoom out effect) | Outpaint hasil ✅ |

#### Stop Recording

Tekan `Win+G` lagi → tombol stop (kotak merah). File `.mp4` masuk ke `C:\Users\<username>\Videos\Captures\`.

---

## 🎛 Penjelasan Semua Parameter di Sidebar

Semua parameter di sidebar kiri berlaku untuk **tab GENERATE saja**. Tab EDIT punya kontrol tersendiri.

### 📊 Quality Steps (default: 30, range 15-50)

**Alias teknis:** `num_inference_steps`

**Apa artinya:** berapa iterasi model melakukan proses **denoising** (menghilangkan noise dari latent random). Stable Diffusion mulai dari noise acak → tiap step mengurangi noise sedikit → akhirnya jadi gambar.

**Efek nilai:**
- **Rendah (15-20):** cepat (~5-10 detik), tapi hasil kadang masih "mentah" — detail tidak matang, kadang muncul noise/artefak.
- **Sedang (25-35):** sweet spot untuk kualitas vs kecepatan. Kebanyakan use case cukup di sini.
- **Tinggi (40-50):** hasil paling halus, gradasi warna optimal. Tapi peningkatan dari 40 → 50 seringkali diminishing return (nyaris tidak berbeda).

**Aturan praktis:** kalau pakai scheduler cepat seperti DPM++, 20 step sudah bagus. Kalau pakai Euler A, 30+ step lebih aman.

### 🎨 Creativity (CFG) (default: 7.50, range 1.00-20.00)

**Alias teknis:** `guidance_scale` atau `classifier-free guidance scale`

**Apa artinya:** seberapa "keras" model harus mengikuti prompt. Ini controlling weight antara "creative interpretation" (bebas) vs "prompt fidelity" (patuh).

**Efek nilai:**
- **Rendah (1-3):** model sangat bebas berinterpretasi. Hasilnya bisa artistik dan surprising, tapi kadang menyimpang dari deskripsi prompt.
- **Sedang (5-8):** balance yang paling umum. Prompt diikuti tapi model tetap punya ruang berkreasi. **7.5 = default kebanyakan pipeline SD 1.5**.
- **Tinggi (12-20):** model sangat patuh prompt. Hasilnya tegas & sesuai deskripsi, TAPI sering **over-saturated** (warna terlalu jenuh, kaku, gambar terasa "hangus").

**Aturan praktis:** untuk illustration/cartoon, 7-10 optimal. Untuk photorealistic (yang kita hindari di project ini), 5-8. Kalau prompt panjang dan detail, boleh naik ke 10-12.

### 🎲 Seed Control (default: 42)

**Alias teknis:** `random_seed` untuk `torch.Generator`

**Apa artinya:** angka yang menentukan **noise awal** yang jadi titik mulai denoising. Seed sama + prompt sama + param sama = hasil identik (reproducible). Seed beda = komposisi & gaya beda.

**Efek nilai:**
- Tidak ada nilai "lebih baik" — semua seed valid.
- Untuk demo BFGAI, soal minta **seed 222** untuk K1 dan **seed 9** untuk K2 (soal test reproducibility).

**Aturan praktis:** eksperimen dengan beberapa seed dulu untuk cari yang komposisinya kamu suka. Setelah ketemu → catat seed itu → orang lain bisa reproduce hasilmu.

### 🚀 Advanced section

#### Scheduler dropdown (default: Euler A, pilihan: Euler A / DPM++ / DDIM)

Lihat section [Penjelasan Semua Metode Scheduler](#-penjelasan-semua-metode-scheduler) di bawah untuk detail.

#### Batch Size / Jumlah Gambar (default: 1, range 1-4)

**Alias teknis:** `num_images_per_prompt`

**Apa artinya:** berapa gambar yang di-generate sekaligus dari prompt yang sama. Setiap gambar dalam batch akan punya **noise awal berbeda** (meskipun seed sama), jadi menghasilkan variasi.

**Efek nilai:**
- **1:** 1 gambar. Cepat, cocok untuk iterasi prompt.
- **2-4:** grid perbandingan untuk cari yang paling cocok. **VRAM T4 (16 GB) sanggup hingga 4 batch** untuk SD 1.5.

**Aturan praktis:** untuk eksplorasi kreatif, set 4. Kalau sudah tahu prompt-nya pas, set 1 supaya lebih cepat.

### 🧹 Flush RAM button (bawah sidebar)

**Alias teknis:** memanggil `logic.flush_memory()` yang eksekusi:
```python
gc.collect()
torch.cuda.empty_cache()
```

**Apa artinya:** membersihkan garbage collector Python + PyTorch VRAM cache. Berguna kalau setelah banyak generate (mis. 5-6 kali batch), VRAM mulai penuh dan operasi selanjutnya lambat / OOM.

**Kapan pakai:**
- Sebelum load gambar baru untuk inpaint (memastikan VRAM cukup)
- Setelah error OOM (kalau terjadi)
- Sekedar cleanup rutin antara sesi

**Efek:** VRAM free naik 2-4 GB tergantung workload sebelumnya. Kalau tidak ada masalah performa, tidak perlu dipanggil.

---

## ⚙️ Penjelasan Semua Metode Scheduler

Scheduler adalah algoritma yang menentukan **bagaimana** denoising step dijalankan — pola timestep, cara sampling noise, urutan reduce noise, dll. Dengan prompt & seed & step count yang sama, scheduler berbeda menghasilkan **gambar yang berbeda**.

Aplikasi StudioAI menyediakan 3 scheduler:

### 🌀 Euler A (Euler Ancestral Discrete Scheduler)

**Karakteristik:**
- **Ancestral sampling** = menambahkan sedikit noise stokastik di tiap step (bukan deterministic).
- Hasil terasa "hidup" dan variatif — bagus untuk illustration style dengan flat shading.
- **Butuh lebih banyak step** (~30+) untuk konvergen ke hasil bagus.
- Kalau step terlalu rendah (<15), hasil bisa nyaris berbeda per-run meskipun seed sama.

**Kapan pakai:**
- Illustration/cartoon style (project kita)
- Ketika ingin variasi natural antar batch
- Portrait & artistic scenes

**Match ke referensi:** dari eksperimen K1, **Euler A menghasilkan output paling dekat ke image-3/image-4** (cartoon astronaut).

### 🚀 DPM++ (DPM-Solver++ Multistep Scheduler)

**Karakteristik:**
- Solver konvergen cepat berbasis diffusion ODE.
- **20-30 step di DPM++ ≈ 40-50 step di scheduler standar** (hemat waktu).
- Deterministic — tidak ada noise stokastik, seed sama → hasil identik selalu.
- Cocok untuk production workflow yang butuh reproducibility ketat.

**Kapan pakai:**
- Batch inference banyak gambar (hemat total waktu)
- Prompt yang sudah stabil dan ingin production output cepat
- Kalau butuh reproducibility 100%

**Trade-off:** hasilnya kadang lebih "kaku" karena tidak ada variasi stokastik.

### 🎯 DDIM (Denoising Diffusion Implicit Model)

**Karakteristik:**
- Scheduler original dari paper Stable Diffusion — solid dan predictable.
- Deterministic (seperti DPM++) tapi lebih lambat konvergen.
- **Butuh 40-50 step** untuk hasil optimal.
- Sering menghasilkan gambar dengan **lebih banyak detail** dan elemen tambahan.

**Kapan pakai:**
- Ketika butuh reproducibility & tidak masalah dengan durasi
- Scene yang kompleks dengan banyak objek
- Debugging (karena deterministic + well-established behavior)

**Efek visual dari eksperimen K1:** DDIM cenderung menambah elemen tak diminta prompt (mis. roket, planet ekstra) — cocok untuk scene komposit, kurang optimal untuk match ke referensi minimalis.

### Ringkasan pilih scheduler:

| Kebutuhan | Rekomendasi |
|---|---|
| Match image-3/image-4 (illustration style) | **Euler A** |
| Batch banyak, hemat waktu | **DPM++** |
| Scene kompleks, deterministic | **DDIM** |

---

## 🎨 Penjelasan Tab GENERATE

### Layout

```
┌─ Input Blueprint (kiri) ──────┬─ Visual Output (kanan) ──┐
│  ┌── Form ────────────────┐   │  ┌──────────────────┐    │
│  │ Prompt textarea        │   │  │ Gambar hasil     │    │
│  │ Negative Prompt input  │   │  │ generate         │    │
│  │ [🚀 Initialize        │   │  │                  │    │
│  │  Generation]           │   │  │ Kalau batch>1:   │    │
│  └────────────────────────┘   │  │ grid 2×2 dgn     │    │
│                                │  │ tombol Select    │    │
└────────────────────────────────┴──────────────────────────┘
```

### Flow

1. User isi prompt + negative prompt
2. Klik **🚀 Initialize Generation** → button submit form
3. `logic.generate_image()` dipanggil dengan semua param dari sidebar
4. Hasil disimpan ke `st.session_state['generated_images']` (list)
5. Kalau batch = 1: `st.session_state['current_image']` = gambar itu
6. Kalau batch > 1: 4 gambar tampil grid, user klik "Select Img N" → `current_image` = gambar dipilih
7. `current_image` inilah yang dipakai di tab EDIT sebagai base

### Kenapa perlu Select Img N?

Karena tab EDIT butuh 1 base image (bukan grid). Kalau batch > 1, user harus memilih dulu mana yang mau di-inpaint/outpaint.

---

## ✂️ Penjelasan Tab EDIT (Inpainting + Outpainting)

Tab ini punya 2 mode via radio button:

### Mode 1: 🎨 Inpainting (Edit Objek)

**Konsep:** mengganti area tertentu di gambar dengan konten baru sesuai prompt.

**Layout:**
```
┌─ Draw Mask (kiri) ────────────┬─ Settings (kanan) ─────┐
│  Canvas menampilkan gambar    │  Prompt Baru: [input]  │
│  base + kuas putih di atasnya │  Strength: [slider]    │
│  User coret area yg mau       │  [⚡ Execute Inpaint]  │
│  di-inpaint                    │                        │
└────────────────────────────────┴────────────────────────┘
```

**Parameter di panel Settings:**

- **Prompt Baru (Ganti jadi apa?):** deskripsi konten yang ingin muncul di area masking. Contoh: `"broken satellite"`, `"red sports car"`, `"tree"`.

- **Strength (Seberapa kuat perubahannya?)** default 0.85, range 0.1-1.0:
  - **Rendah (0.1-0.3):** perubahan halus, tekstur asli sebagian dipertahankan (bagus untuk "touch up").
  - **Sedang (0.5-0.7):** perubahan jelas tapi mempertahankan komposisi lingkungan (blend natural).
  - **Tinggi (0.8-1.0):** area masking benar-benar diganti dengan konten baru. **0.85 = default** cocok untuk kebanyakan use case.

**Cara kerja teknis:**

1. Canvas capture gambar coretan sebagai alpha channel
2. Alpha channel dikonversi jadi mask putih-hitam (mode "L")
3. Mask di-resize match gambar asli
4. Di-pertegas via `ImageFilter.MaxFilter(15)` (menebalkan)
5. Diserahkan ke `logic.run_inpainting(pipe, image, mask, prompt, strength)`
6. Model SD Inpainting generate konten baru hanya di area putih mask
7. Hasil di-set jadi `current_image` yang baru → bisa di-inpaint lagi berulang

### Mode 2: 🔍 Outpainting (Zoom Out)

**Konsep:** memperluas kanvas gambar ke semua arah, model generate area baru yang "menyambung" ke gambar asli.

**Layout:**
```
┌─ Original (kiri) ──────────────┬─ Expansion (kanan) ───┐
│  Gambar asli utuh              │  Info: expand 128px    │
│                                │  Prompt Deskriptif:    │
│                                │  [textarea]            │
│                                │  [🔍 Zoom Out]         │
└────────────────────────────────┴────────────────────────┘
```

**Parameter:**

- **Prompt Deskriptif:** deskripsi UTUH gambar setelah expansion. Contoh: `"wide angle view of astronaut on moon with earth in background, detailed lunar landscape, 8k"`. Model butuh konteks lengkap agar area baru koheren dengan pusat.

- **Expand size:** hardcoded **128 px** ke SEMUA arah (kiri+kanan+atas+bawah). Total kanvas jadi lebih besar 256 px di kedua dimensi.

**Cara kerja teknis:**

1. `logic.prepare_outpainting(image, expand_pixels=128)`:
   - Kanvas baru = ukuran + 256px x 256px, safe kelipatan 8
   - Background = image asli di-resize ke ukuran baru + GaussianBlur radius 50 (jadi buram)
   - Image asli di-paste di tengah kanvas (posisi center)
   - Mask = putih (255) di seluruh kanvas, hitam (0) di area image asli
2. `logic.run_inpainting(pipe, canvas, mask, prompt, strength=1.0)`:
   - Strength 1.0 = area putih di-generate full dari nol
   - Area hitam (image asli) tetap tidak berubah
3. Hasil = image asli di tengah + konten baru di sekelilingnya

**Tips:** prompt harus deskriptif untuk seluruh scene, bukan hanya area baru. Model tidak tahu "area yang mau diperluas" — dia hanya tahu "generate konten sesuai prompt di area putih mask".

---

## 📹 Tips Perekaman Video

### Setting recorder

- **Resolusi:** minimal 1080p (Full HD)
- **FPS:** 30 fps cukup
- **Audio:** tidak perlu (video demo mute OK, reviewer hanya lihat visual)
- **Cursor:** tampilkan (biar reviewer lihat interaksi klik)
- **Format:** `.mp4` (H.264) — sesuai instruksi

### Persiapan sebelum record

1. **Close semua tab yang tidak perlu** (kecuali StudioAI + Colab). Ini biar taskbar bersih.
2. **Zoom browser 90%** kalau layar kamu 1080p — biar tab GENERATE + EDIT visible utuh tanpa scroll banyak.
3. **Test cursor position** — canvas drawable perlu drag yang smooth, latih dulu 1x sebelum record.
4. **Cek disk space** — video ~5 menit di 1080p bisa 500-800 MB. Pastikan drive tujuan Videos/Captures cukup.
5. **Silent notifications** — matikan sementara Windows notification, Discord, WhatsApp, dll.

### Selama record

- **Bicaranya minimal** (kalau ada audio) — hanya jelaskan yang penting, atau mute total.
- **Pause 2-3 detik** setelah tiap aksi (klik, isi input, generate) sebelum lanjut → biar reviewer sempat baca layar.
- **Kalau salah** (mis. salah paste prompt) — jangan panik. Lanjutkan, hapus, ulang. Reviewer paham ini demo real-time.
- **Kalau spinner Streamlit lama** — biarkan sampai selesai, jangan skip. Reviewer perlu lihat progression.

### Perekam alternatif (kalau Xbox Game Bar tidak jalan)

- **OBS Studio** (free): [obsproject.com](https://obsproject.com)
  - Setup: Display Capture → recording target folder + format .mp4
  - Tombol: `Start Recording` di kanan bawah
- **ShareX** (free): screenshot + screen recorder ringan
- **Bandicam** (trial): populer untuk gaming recording

---

## 📤 Setelah Rekaman Selesai

### 1. Cek file video

- Buka `C:\Users\<username>\Videos\Captures\`
- File terbaru = video kamu
- **Play** untuk verifikasi: audio (kalau ada) + visual jelas + semua segmen ter-capture

### 2. Rename & pindah

Nama file HARUS **persis** sesuai instruksi Dicoding:
- Rename: `video_demo_aplikasi_BFGAI.mp4`
- Pindah ke: `d:\Kalachakra\docs\hackaton_PIDI\proyek_image_generation\submission\`

### 3. Cek ukuran file

- Kalau > 100 MB → OK saja, Dicoding accept sampai ~200 MB per file
- Kalau > 200 MB → kompres pakai **HandBrake** (free) → Fast 1080p30 preset, kualitas menurun sedikit tapi file jauh lebih kecil (~50-100 MB)

### 4. Download notebook dari Colab

- Di Colab, tab `Streamlit_submission_BFGAI...ipynb`
- **File → Download → Download .ipynb**
- Ini akan memberi kamu notebook dengan **outputs ter-embed** (yang direview Dicoding)
- **Replace** file di disk: `d:\Kalachakra\docs\hackaton_PIDI\proyek_image_generation\submission\Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`

### 5. Kabari Claude

Katakan "sudah semua" — Claude akan:
- Bikin `requirements.txt` (pipreqs-style)
- Zip flat 4 file jadi `BFGAI_Nazhif_Setya_Nugroho.zip`
- Audit final sebelum kamu upload ke Dicoding

---

## 🔧 Troubleshooting Cepat

### Halaman ngrok show `ERR_NGROK_3200: offline`
- **Penyebab:** Streamlit belum siap ATAU cell `ngrok.kill()` sudah dijalankan.
- **Fix:** re-run cell `public_url = ngrok.connect(8501).public_url` di Colab (dapat URL baru), TAPI jangan run cell `ngrok.kill()`.

### Halaman muat lama di "Running get_models()"
- **Normal.** Load 2 model SD 1.5 (~10 GB total) butuh 5-8 menit pertama kali. Jangan refresh.

### Canvas di tab EDIT kosong (tidak menampilkan gambar)
- **Penyebab:** Belum generate gambar dulu di tab GENERATE.
- **Fix:** Kembali ke tab GENERATE → generate 1 gambar → baru ke tab EDIT.

### Error `AttributeError: module 'streamlit.elements.image' has no attribute 'image_to_url'`
- **Penyebab:** Streamlit versi terlalu baru untuk drawable-canvas.
- **Fix:** Sudah di-patch di sel 2 (pin Streamlit 1.29.0). Kalau muncul lagi berarti pin gagal — jalankan `!pip install -q "streamlit==1.29.0"` lalu restart runtime.

### Error `TypeError: ImageMixin.image() got an unexpected keyword argument 'use_container_width'`
- **Penyebab:** app.py memakai param Streamlit modern tapi kita pakai 1.29.
- **Fix:** Sudah di-patch di sel 13 (`use_container_width` → `use_column_width`). Kalau masih muncul di Colab, jalankan `!sed -i 's/use_container_width/use_column_width/g' app.py` lalu restart streamlit.

### VRAM out of memory saat batch inference
- **Fix:**
  1. Klik **🧹 Flush RAM** button
  2. Kurangi Batch Size ke 2
  3. Kalau tetap OOM, restart runtime Colab → run ulang

### Generate hasilnya blank / abu-abu / hitam total
- **Penyebab:** safety_checker (NSFW filter) menge-blackout. Kita sudah `safety_checker = None` di logic.py, jadi tidak seharusnya terjadi. Kalau tetap terjadi → hasil dari base model corrupt.
- **Fix:** ganti prompt, generate ulang.

### Tab EDIT crash setelah upload gambar mask besar
- **Penyebab:** mask terlalu banyak coretan → alpha channel > memory.
- **Fix:** klik **🧹 Flush RAM** → tab EDIT → refresh page (F5) → coba coret lebih sederhana.

---

## 🎯 Ringkasan Alur untuk Cepat Ingat

```
1. Smoke test (1 generate default, tidak direkam)
   ↓
2. Buka Xbox Game Bar (Win+G) → Start Recording
   ↓
3. Segmen K3 Basic (0:00-1:00)
   - URL + judul → prompt astronaut → generate 1 → tunggu hasil
   ↓
4. Segmen K3 Skilled (1:00-2:00)
   - Batch 4 → scheduler DPM++ → generate → grid 2×2 → Flush RAM
   ↓
5. Segmen K3 Advanced Inpaint (2:00-3:00)
   - Tab EDIT → Inpainting → coret canvas → prompt satellite → Execute
   ↓
6. Segmen K3 Advanced Outpaint (3:00-3:45, bonus)
   - Radio Outpainting → prompt utuh → Zoom Out → tunggu
   ↓
7. Stop Recording (Win+G → tombol stop)
   ↓
8. Rename video jadi video_demo_aplikasi_BFGAI.mp4 → pindah ke submission/
   ↓
9. Download notebook dari Colab → replace file di disk
   ↓
10. Kabari Claude → Fase Akhir (requirements.txt + zip)
```

Selamat merekam! 🎬
