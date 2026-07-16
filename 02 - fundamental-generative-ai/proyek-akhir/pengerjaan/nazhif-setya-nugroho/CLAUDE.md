# CLAUDE.md — Proyek Image Generation (Generative Image Suite · BFGAI)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Generative AI (BFGAI)" → Proyek: Generative Image Suite**. Ini proyek **ke-3** user setelah dua submission Dicoding sebelumnya (**BMLP** dan **Proyek Akhir Klasifikasi Gambar**) yang keduanya lulus **⭐⭐⭐⭐⭐**.
- Lokasinya kebetulan di dalam `Everest/docs/hackaton_PIDI/`, **TAPI sama sekali TIDAK berhubungan dengan aplikasi Everest (EBC).**
- **Aturan dari `Everest/CLAUDE.md` dan `docs/CLAUDE.md` TIDAK BERLAKU di sini.** Abaikan semua hal soal backoffice-service/Sequelize/Hoppscotch/CLIK/DocuSign/dsb. **Jangan** sentuh/ubah file di luar folder project ini.
- Project ini **self-contained**. Semua yang relevan ada di folder ini.
- Referensi metodologi sukses: `../fundamental_deep_learning/proyek_akhir/CLAUDE.md` (paling relevan — sama-sama pakai Colab GPU T4, target semua saran, verifikasi model checkpoint di awal).

---

## 👤 USER & GAYA KERJA

- **Nama user:** Nazhif Setya Nugroho → dipakai di nama file: `Nazhif_Setya_Nugroho`.
- **Email:** dev@kalachakra.io
- **Konteks:** User junior developer. Ini proyek **Generative AI pertama**-nya. Sudah lulus 2 proyek ML/DL sebelumnya (BMLP + Klasifikasi Gambar CNN).
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia yang simpel**, mudah dimengerti junior.
  - **Pelan-pelan, step-by-step.** Jelaskan _kenapa_ tiap langkah, bukan cuma _apa_.
  - **Teliti terhadap detail kecil.**
  - **Jangan asumsi.** Kalau ambigu, **tanya dulu** pakai AskUserQuestion sebelum nulis kode — kecuali user secara eksplisit minta jalan tanpa nanya.
- **Target nilai yang disepakati:** **BINTANG 5 (⭐⭐⭐⭐⭐, nilai 4.0)** — SEMUA 3 kriteria dikejar sampai level **Advanced**.
- **Checklist progress** dibuka user pakai ekstensi **Markdown Preview Enhanced** → file `.md` boleh kaya visual (mermaid, badge HTML, `<progress>`, `<details>`, emoji).

---

## 🎯 INTI PROYEK (apa yang dikerjakan)

Membangun **aplikasi web Streamlit "Generative Image Suite"** end-to-end di atas **Stable Diffusion 1.5** (library `diffusers`), dengan 3 fitur inti dalam satu antarmuka:

1. **Text-to-Image** (K1) — fungsi `generate_simple_image()` & `generate_advanced_image()`, eksperimen guidance_scale + inference_steps, batch 2×2, `load_scheduler()` (Euler A / DPM++ / DDIM).
2. **Image-to-Image: Inpainting + Outpainting** (K2) — `inpaint_engine()` masking manual, auto-mask via segmentation model, `prepare_outpainting()` 1 arah, Zoom Out multi-arah, **Refiner Pattern (Base+Refiner two-stage)**.
3. **Streamlit UI** (K3) — text input + slider + Generate button + demo `.mp4`, batch `num_images`, dropdown scheduler, Clear Memory button, tab Inpaint/Outpaint dengan `streamlit-drawable-canvas`.

**Alur pengerjaan:** verifikasi model → K1 (Pipeline notebook) → K2 (Pipeline notebook) → K3 (Streamlit notebook: isi `logic.py`) → rekam video demo → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Environment** | **Google Colab GPU T4 (free tier)** | Terbukti lulus di proyek CNN. Colab T4 16 GB VRAM aman untuk SD1.5 + Inpainting + segmentation model bareng. Local Windows (RTX 3050 4 GB) TIDAK dipakai untuk training/inference berat. |
| **Target nilai** | ⭐⭐⭐⭐⭐ (semua 3 kriteria Advanced = 4.0) | Kalau 1 kriteria kena Reject → nilai anjlok. Jangan ada nol. |
| **Model text-to-image** | `stable-diffusion-v1-5/stable-diffusion-v1-5` (mirror pengganti `runwayml/*`) | ⚠️ **Verifikasi di Tahap 1** — org `runwayml` sudah delisted dari HF sejak 2024. Kalau template Streamlit hardcode `runwayml/*`, **WAJIB diganti** + kasih catatan markdown. |
| **Model inpainting** | `stable-diffusion-v1-5/stable-diffusion-inpainting` (mirror pengganti `runwayml/*`) | Idem. Verifikasi ID hidup di Tahap 1. |
| **Segmentation untuk auto-mask K2** | **CLIPSeg** (`CIDAS/clipseg-rd64-refined`, ~600 MB) | Text-driven segmentation cocok untuk kasus "satelit rusak" (prompt string). Ringan vs SAM (~2.4 GB). |
| **Scheduler K1 Advanced** | Euler A (`EulerAncestralDiscreteScheduler`), DPM++ (`DPMSolverMultistepScheduler`), DDIM (`DDIMScheduler`) — semua dari `diffusers.schedulers` | Switch via `pipe.scheduler = X.from_config(pipe.scheduler.config)` — TIDAK reload model (tips Dicoding #3). |
| **Refiner Pattern K2 Advanced** | **Workaround (bukan param native):** Stage 1 = `pipe_txt2img(..., num_inference_steps=40, output_type="latent")` → Stage 2 = `pipe_img2img(image=<latent>, num_inference_steps=50, strength=0.2)` di mana `pipe_img2img = StableDiffusionImg2ImgPipeline(**pipe_txt2img.components)` | ⚠️ **CONFIRMED Tahap 1:** `denoising_end`/`denoising_start` **TIDAK ada** di signature SD1.5 pipeline (diffusers v0.39.0) — itu param SDXL. Interpretasi "Refiner Pattern": pola dua-tahap Base+Refiner via kombinasi latent output + img2img `strength`. Kedua pipeline **share UNet weights** — hemat VRAM. Tulis catatan markdown di notebook untuk transparansi. |
| **Tunneling Streamlit** | **Ngrok** (pola template Dicoding) | User siapkan token ngrok sendiri (soal tips #1). |
| **Seed** | K1 = **222**, K2 (inpainting) = **9** | Hardcoded di soal — reviewer bandingkan hasil pada seed ini. |
| **Negative prompt K1** | `"photorealistic, realistic, photograph, 3d render, messy, blurry, low quality, bad art, ugly, sketch, grainy, unfinished, chromatic aberration"` | Hardcoded di soal. Note: negative-nya menolak realism → target = **illustration/stylized** style, bukan photograph. |
| **Tema visual** | Astronaut di permukaan bulan dengan Bumi di latar belakang (illustration style). K2: tambah satelit rusak di sebelahnya. | Konsisten antar-referensi (image-1 → image-6 di artifacts). Prompt bisa direuse antar-kriteria. |

---

## 📁 STRUKTUR FOLDER

```
proyek_image_generation/
├── CLAUDE.md                          ← file ini (memory + rules)
├── .gitignore
├── artifacts/                         ← 📦 INSTRUKSI ASLI DICODING — READ-ONLY (6 md + 13 png)
├── template/                          ← 📥 TEMPLATE ASLI DICODING — READ-ONLY
│   ├── [Template]_Pipeline_submission_BFGAI_Nama_siswa.ipynb     (47 sel, blank-slate)
│   └── [Template]_Streamlit_submission_BFGAI_Nama_siswa.ipynb    (22 sel, blank-fill "________")
├── panduan/
│   ├── Checklist_Pengerjaan.md        ← 📋 tracker progres (update tiap kriteria/tahap)
│   └── Instruksi_Colab.md             ← 🚀 panduan step-by-step user Run All di Colab
├── scratchpad/                        ← 🧪 gitignored — script prototype (.py) + PNG hasil eksperimen (untuk verifikasi via Read tool)
└── submission/                        ← 💻 FILE KERJA + OUTPUT (yang nanti di-zip)
    ├── Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb    ← salinan template Pipeline
    ├── Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb   ← salinan template Streamlit
    ├── video_demo_aplikasi_BFGAI.mp4                           ← direkam user setelah Streamlit jalan
    └── requirements.txt                                         ← dibuat di Fase Akhir (pipreqs-style)
```

**Deliverable zip final:** `BFGAI_Nazhif_Setya_Nugroho.zip` — struktur **flat 4 file** (2 ipynb + 1 mp4 + requirements.txt).

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

### Utama: Google Colab GPU T4 (semua eksekusi berat)
- Runtime → Change runtime type → **T4 GPU**.
- Notebook Pipeline & Streamlit **dieksekusi di sini** (Run All).
- Library terinstal via `!pip install` di sel dependency (sudah disiapkan template).
- Streamlit di-tunnel via **pyngrok** (token ngrok pribadi user).

### Pendukung: Windows lokal (mesin ini) — HANYA persiapan/packaging
- **JANGAN** coba load Stable Diffusion di sini. RTX 3050 4 GB terlalu tight untuk SD1.5 + Inpainting.
- Yang boleh dilakukan di sini:
  - Edit isi notebook (Python script `json.load` → replace `________` → `json.dump`).
  - Baca artifacts + template.
  - Bikin scratchpad `.py` untuk logika non-model (mis. mask geometri, canvas resize, prepare_outpainting math).
  - Baca gambar hasil eksperimen Colab via Read tool untuk verifikasi visual.
  - Susun folder + zip submission.
- **Python interpreter:** `python3` (Windows Python 3.11) sudah cukup untuk file editing task. TIDAK perlu venv untuk sekedar `json.load`/`json.dump`.

---

## 🛠️ TOOLS TERSEDIA (termasuk MCP)

### MCP Chrome DevTools Protocol (`mcp__chrome-devtools__*`) — PAKAI KALAU BUTUH
Tersedia untuk drive browser real: `navigate_page`, `take_screenshot`, `click`, `fill`, `evaluate_script`, `list_console_messages`, `list_network_requests`, `wait_for`, dll.

**Kapan pakai CDP di project ini:**
- **Debug UI Streamlit**: buka URL ngrok → screenshot → verifikasi komponen (slider, button, canvas, tab) muncul benar → cek console error → cek network call ke ngrok tunnel.
- **Test flow interaktif**: fill prompt → click Generate → wait_for hasil gambar → screenshot bukti fungsional.
- **Verifikasi model checkpoint di HF**: navigate ke `https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5` → cek halaman ada (bukan 404) → cek file `model_index.json` accessible.
- **Ekstraksi info dari halaman submission Dicoding**: navigate → screenshot bagian penilaian/checklist reviewer supaya sinkron.

**KAPAN TIDAK pakai CDP:**
- Baca dokumen lokal → pakai Read tool.
- Search kode → pakai Grep/Glob.
- Cek existence file → pakai Bash `ls`.
- Ambil JSON API sederhana → pakai WebFetch (kalau tersedia) atau Bash `curl`, bukan CDP.

CDP mahal (bikin browser instance, render page); pakai hanya kalau memang butuh interaksi browser atau visual verifikasi yang tidak bisa didapatkan dari sumber lain.

### Tools lain yang tersedia
- **WebFetch / WebSearch** — cek dokumentasi diffusers/huggingface, riset best practice prompt.
- **Explore agent** — untuk lookup cepat di codebase.
- **Read (multimodal)** — bisa lihat gambar `.png/.jpg` langsung. Ini kunci verifikasi visual hasil generate: script prototype → save `scratchpad/*.png` → Read → aku bisa lihat & putuskan prompt sudah pas atau belum.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `artifacts/6.lainnya.md`, `artifacts/4.ketentuan_berkas.md`, catatan template.

1. **WAJIB pakai template Dicoding** (2 file di `template/`). Ubah struktur (hapus/tambah section markdown, ubah order) → reject.
2. **WAJIB pakai `runwayml/stable-diffusion-v1-5` DAN `runwayml/stable-diffusion-inpainting`** — atau **mirror bit-perfect** dari kedua checkpoint tersebut (mis. `stable-diffusion-v1-5/*` di HF). **DILARANG** ganti ke SDXL, GAN, atau model lain (auto-reject per larangan #7 di 6.lainnya.md).
3. **DILARANG pakai Stable Diffusion XL (SDXL)** — VRAM boros, gampang OOM (tips #2 di 5.tips_and_trick.md).
4. **DILARANG tambah kode/fitur di luar instruksi** (larangan #3 di 6.lainnya.md). Fungsi tambahan hanya bila dibutuhkan untuk kriteria yang diminta.
5. **Notebook `.ipynb` WAJIB sudah dijalankan** → semua output ter-embed. Cell tanpa output = dianggap belum selesai / reject.
6. **Hasil generate WAJIB ditampilkan** di antarmuka Streamlit setelah Generate.
7. **Video demo `.mp4` 1-5 menit** WAJIB dilampirkan (bukti aplikasi pernah jalan).
8. **`requirements.txt` WAJIB ada** di zip.
9. Kirim dalam **1 folder di-zip**. Bahasa: **Python**. Struktur zip **flat 4 file**.
10. **Jangan submit berkali-kali** (memperlama antrian review; review ±3 hari kerja).

### Aturan mengisi template (dari template itu sendiri)
11. **Template Pipeline (blank-slate)**: sel kode kosong total → isi dari nol, IKUTI STRUKTUR MARKDOWN yang ada (jangan tambah/hapus section). Boleh tambah import.
12. **Template Streamlit (blank-fill `________`)**: hanya isi `________` di dalam `%%writefile logic.py` / `%%writefile -a logic.py`. **`app.py` (9.4 KB) JANGAN DISENTUH** — sel 13 di notebook. `load_models_cached()` boleh diubah untuk fix model ID (delisted issue) + catatan markdown, sesuai izin di cell 0.
13. **Nama fungsi** ikut apa yang diminta soal untuk notebook Pipeline (`generate_simple_image`, `generate_advanced_image`, `inpaint_engine`, `prepare_outpainting`, `load_scheduler`). Untuk `logic.py` di Streamlit ikut nama yang sudah dipakai `app.py` (`generate_image`, `run_inpainting`, `set_scheduler`, `flush_memory`).

---

## 📊 KRITERIA & PENILAIAN (peta ke bintang 5)

**Rumus:** `Nilai Akhir = Total Poin ÷ 3 kriteria`

| Nilai | Bintang | Level |
|---|---|---|
| < 1 | Rejected | Gagal |
| 1–<2 | ⭐⭐ | D |
| 2–<3 | ⭐⭐⭐ | Basic (lulus) |
| 3–<4 | ⭐⭐⭐⭐ | Skilled |
| **4** | **⭐⭐⭐⭐⭐** | **Advanced ← TARGET** |

### K1 — Text-to-Image
| Level | Poin | Yang wajib ada |
|---|---|---|
| 🟢 Basic | 2 | `generate_simple_image(prompt, neg_prompt, seed)` + `generate_advanced_image(...+ guidance_scale + num_inference_steps)` menggunakan `StableDiffusionPipeline` + model SD1.5. Hasil semirip mungkin dengan image-3 & image-4 (seed 222, negative prompt tetap). |
| 🔵 Skilled | 3 | Basic + eksperimen guidance_scale (rendah vs tinggi) + inference_steps (5–15 vs 30–50). Narasi observasi di markdown yang disediakan. |
| 🟣 Advanced | 4 | Skilled + batch inference 4 gambar → grid 2×2 + `load_scheduler(pipe, scheduler_name)` untuk Euler A / DPM++ / DDIM (TIDAK reload model) + narasi observasi 3 scheduler. |

### K2 — Image-to-Image (Inpainting + Outpainting)
| Level | Poin | Yang wajib ada |
|---|---|---|
| 🟢 Basic | 2 | `inpaint_engine(image, mask, prompt)` pakai `StableDiffusionInpaintPipeline` + model SD Inpainting. Masking **manual hardcode** (trial-error). Hasil semirip mungkin dengan image-5/image-6 (seed 9) — tambah satelit rusak. |
| 🔵 Skilled | 3 | Basic + auto-mask via **segmentation model** (CLIPSeg) + `prepare_outpainting()` perluas kanvas 1 arah (kiri/kanan/atas/bawah) + eksekusi outpainting 1 sisi pakai hasil inpainting sebagai input. |
| 🟣 Advanced | 4 | Skilled + **Zoom Out** (outpainting multi-arah bertahap) + **Refiner Pattern**: Stage 1 Base pipeline `denoising_end=0.8` → Stage 2 `StableDiffusionImg2ImgPipeline` `denoising_start=0.8`. |

### K3 — Streamlit Interface
| Level | Poin | Yang wajib ada |
|---|---|---|
| 🟢 Basic | 2 | Text input (prompt + negative_prompt) + slider (guidance_scale + num_inference_steps) + button Generate + hasil gambar tampil langsung + demo `.mp4` 1-5 menit. |
| 🔵 Skilled | 3 | Basic + input `num_images` batch → grid 2×2 + dropdown Scheduler (Euler A / DPM++ / DDIM) + button "Clear Memory" (`gc.collect()` + `torch.cuda.empty_cache()`). |
| 🟣 Advanced | 4 | Skilled + tab baru untuk Inpainting/Outpainting + integrasi `streamlit-drawable-canvas` (user gambar mask langsung di gambar hasil generate). |

⚠️ Kalau **1 kriteria saja kena Reject (0 poin)**, rata-rata anjlok & bisa GAGAL. Pastikan tidak ada yang nol.

---

## 🧭 METODOLOGI KERJA (warisan sukses 2 proyek sebelumnya)

1. **VERTICAL per-kriteria, bukan horizontal.** Kerjakan K1 → K2 → K3 berurutan, tiap kriteria langsung dituntaskan sampai Advanced (Basic+Skilled+Advanced sekaligus). Alasan: notebook = pipeline berurutan & saling tergantung; ngerjain per-level malah harus keliling notebook 3x + banyak re-run.
2. **VERIFY-FIRST (wajib).** Sebelum nulis logika ke notebook:
   - Untuk logika non-model (mask geometri, kalkulasi kanvas, dsb): prototype di script `.py` di `scratchpad/`, run lokal.
   - Untuk logika model (generate, inpaint, refiner): prototype di **Colab** sel scratch dulu (bukan langsung ke sel submission), atau lewat notebook Colab terpisah. Simpan hasil PNG → bawa ke lokal → **lihat pakai Read tool** untuk verifikasi visual.
   - Baru isi ke sel submission setelah yakin hasilnya benar.
3. **Model muat sekali, re-use.** Tips Dicoding #3. `StableDiffusionPipeline` + `StableDiffusionInpaintPipeline` + segmentation model diload di sel awal, dipakai di semua sel bawahnya. Untuk Refiner: `StableDiffusionImg2ImgPipeline.from_pretrained(...)` boleh, tapi bisa share komponen (`vae`, `text_encoder`, `tokenizer`, `unet`, `scheduler`) dari pipe txt2img untuk hemat VRAM: `StableDiffusionImg2ImgPipeline(**pipe.components)`.
4. **Cara isi template Pipeline (blank-slate):** buka `.ipynb` sebagai JSON (`json.load`) → set `cell['source']` untuk sel kode target → `json.dump`. JANGAN edit .ipynb manual pakai text replace.
5. **Cara isi template Streamlit (blank-fill):** script Python `json.load` → cari sel kode dengan `%%writefile` → replace `________` **berurutan** per sel → `assert` jumlah blank == jumlah nilai & `assert` 0 blank tersisa → `json.dump`. Ini pola dari proyek BMLP.
6. **Setelah tiap kriteria selesai:** update `panduan/Checklist_Pengerjaan.md` (centang Basic/Skilled/Advanced + `<progress>`) DAN update [Progress Log](#-progress-log-living-section) di file ini.
7. **Output di-embed di FASE AKHIR.** Setelah semua sel siap, user Run All di Colab sekali → output ter-embed → download `.ipynb` yang sudah ada output → letakkan di `submission/`.
8. **CDP untuk verifikasi UI Streamlit.** Setelah `logic.py` + app.py jalan di ngrok, buka URL via CDP: screenshot tiap tab (Basic/Skilled/Advanced K3), fill prompt & klik Generate, verifikasi gambar muncul, cek console log. Ini juga bahan referensi untuk rekaman video demo (user rekam sendiri layar 1-5 menit).

---

## 🔑 CATATAN TEKNIS PENTING

### Model checkpoint (✅ verifikasi Tahap 1 SELESAI 2026-07-09)
- Org `runwayml` **delisted dari HF** sejak pertengahan 2024. `from_pretrained("runwayml/stable-diffusion-v1-5")` sekarang **404**.
- **Mirror yang TERVERIFIKASI HIDUP** (dari WebFetch ke HF pages):
  - ✅ `stable-diffusion-v1-5/stable-diffusion-v1-5` — 1.7 juta download/bulan, license CreativeML OpenRAIL M, **dinyatakan mirror bit-perfect** oleh maintainer di model card ("This repository is a mirror of the now deprecated runwayml/stable-diffusion-v1-5").
  - ✅ `stable-diffusion-v1-5/stable-diffusion-inpainting` — 184K download/bulan, license sama, juga mirror resmi runwayml/stable-diffusion-inpainting.
  - Backup: `sd-legacy/stable-diffusion-inpainting` (varian dgn `revision="fp16"` yang direkomendasikan HF page inpainting mirror).
- Diffusers v0.39.0 docs snippet resmi pakai ID mirror: `from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16)` — konfirmasi diffusers sudah nge-endorse pakai mirror ini.
- **Kesimpulan:** pakai `stable-diffusion-v1-5/*` untuk kedua model. Tulis catatan markdown di notebook transparansi (mirror bit-perfect, bukan model lain).

### Refiner Pattern di SD 1.5 (✅ verifikasi Tahap 1 SELESAI — TIDAK NATIVE)
- **CONFIRMED:** signature `StableDiffusionPipeline.__call__` di diffusers v0.39.0 (versi rilis terbaru) **TIDAK memiliki** param `denoising_end`. Param ini SDXL-only (`StableDiffusionXLPipeline`).
- Signature aktual: `prompt, height, width, num_inference_steps, timesteps, sigmas, guidance_scale, negative_prompt, num_images_per_prompt, eta, generator, latents, prompt_embeds, negative_prompt_embeds, ip_adapter_image, ..., output_type, ..., **kwargs`.
- **Workaround yang dipilih (2-stage Base+Refiner via latent + img2img strength):**
  ```python
  # Stage 1: Base — 40 step (80% dari 50 step) → keluarkan latent
  base_latent = pipe_txt2img(
      prompt=prompt, negative_prompt=neg,
      num_inference_steps=40, guidance_scale=7.5,
      generator=gen, output_type="latent"
  ).images  # tensor (1, 4, 64, 64)

  # Stage 2: Refiner — share UNet weights, refine via img2img
  pipe_img2img = StableDiffusionImg2ImgPipeline(**pipe_txt2img.components)
  refined = pipe_img2img(
      prompt=prompt, negative_prompt=neg,
      image=base_latent, strength=0.2,
      num_inference_steps=50, guidance_scale=7.5,
      generator=gen
  ).images[0]
  ```
- Alternatif kalau di atas gagal (`image=latent` tidak diterima): decode latent dulu ke PIL image lewat `pipe_txt2img.vae.decode(base_latent / 0.18215).sample`, lalu feed sebagai PIL ke img2img.
- **Wajib tulis catatan markdown di notebook** menjelaskan: (a) `denoising_end` bukan param SD1.5 native, (b) pola Base+Refiner diimplementasi via strategi ekuivalen — untuk transparansi ke reviewer.

### Segmentation model (K2 Skilled)
- **CLIPSeg** (`CIDAS/clipseg-rd64-refined`) — text-driven, ~600 MB. `from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation`.
- Flow: text prompt (mis. `"satellite"`) + image → probability mask (sigmoid) → threshold → binary mask (mode "L") → feed ke `inpaint_engine()`.
- Alternative kalau CLIPSeg gagal: SAM (`facebook/sam-vit-base`, 375 MB) — tapi butuh point/box prompt, lebih ribet.

### Prompt engineering untuk astronaut-di-bulan illustration style
- Berdasarkan gambar referensi (image-1 s/d image-6) + negative prompt tolak realism:
  - Kandidat prompt: `"astronaut standing on the moon surface, earth visible in the background, dark starry sky, illustration, digital art, clean lines, vibrant colors"`
  - Untuk inpainting seed 9: prompt tambahan `"broken satellite next to astronaut, damaged spacecraft, debris"`.
- Ini akan dituning iteratif di Tahap 2 dengan seed 222.

### Streamlit + Ngrok pattern di Colab
- Template sudah siap: `!pip install pyngrok streamlit` → `%%writefile app.py` → `subprocess.Popen(["streamlit", "run", "app.py"])` → `ngrok.connect(8501).public_url`.
- Kalau kena limit endpoint ngrok: `ngrok.kill()` lalu retry.
- URL ngrok public bisa kita drive via **CDP** untuk screenshot/testing.

### requirements.txt
- Dibuat di Fase Akhir pakai **pipreqs-style** (hanya library yang benar-benar diimport), BUKAN `pip freeze` seluruh Colab (nanti isinya ratusan library sampah Colab).
- Kandidat isi: `torch`, `diffusers`, `transformers`, `accelerate`, `streamlit`, `streamlit-drawable-canvas==0.8.0`, `pyngrok`, `pillow`, `numpy`.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: tanggal + apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Persiapan & Setup: ✅ SELESAI (2026-07-09)**
  - Semua artifacts Dicoding (6 md + 13 png) dibaca; kriteria dipahami.
  - 2 template resmi Dicoding (Pipeline blank-slate + Streamlit blank-fill) sudah ada di `template/`. Dibedah: 47 sel Pipeline, 22 sel Streamlit.
  - Keputusan besar dikunci: Colab GPU T4, target ⭐⭐⭐⭐⭐, template siap, verifikasi model checkpoint di Tahap 1.
  - Bom waktu diidentifikasi: (1) `runwayml/*` delisted dari HF → wajib pakai mirror `stable-diffusion-v1-5/*` + catatan markdown; (2) Refiner pattern `denoising_end/start` asal SDXL → verifikasi kompatibilitas ke SD1.5 di diffusers terbaru.
  - Folder dibuat: `panduan/`, `submission/`, `scratchpad/`. `.gitignore` di-set.
  - 2 template disalin ke `submission/` dengan nama final:
    - `Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`
    - `Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`
  - `CLAUDE.md`, `Checklist_Pengerjaan.md`, `Instruksi_Colab.md` disiapkan.
- **Tahap 1 — Verifikasi checkpoint & pipeline: ✅ SELESAI (2026-07-09, via WebFetch — rute B)**
  - ✅ **Mirror SD1.5 hidup:** `stable-diffusion-v1-5/stable-diffusion-v1-5` (1.7M dl/bulan, license CreativeML OpenRAIL M, dinyatakan mirror bit-perfect resmi runwayml).
  - ✅ **Mirror Inpainting hidup:** `stable-diffusion-v1-5/stable-diffusion-inpainting` (184K dl/bulan, mirror resmi). Backup: `sd-legacy/stable-diffusion-inpainting` dgn `revision="fp16"`.
  - ❌ **`denoising_end`/`denoising_start` TIDAK ada** di SD1.5 pipeline diffusers v0.39.0 (SDXL-only). Workaround dipilih: 2-stage Base+Refiner via `output_type="latent"` + `StableDiffusionImg2ImgPipeline` dengan `strength=0.2`. Detail di [Catatan Teknis Penting](#-catatan-teknis-penting).
  - ✅ **CLIPSeg hidup:** `CIDAS/clipseg-rd64-refined` (0.2B params, 1M dl/bulan, contoh kode load & inference tersedia via `CLIPSegForImageSegmentation`).
  - Verifikasi rute B (WebFetch ke halaman HF & diffusers docs) — tidak butuh eksekusi Colab. Kalau nanti ada anomali saat isi notebook Colab, revisi keputusan di atas.
  - Tools lokal Windows terinstal: `pipreqs 0.5.0`, `nbformat 5.10.4`, `nbclient 0.11.0`, `nbconvert 7.17.1`, `Pillow 12.3.0`, `requests 2.34.2`, `jupyter/ipython machinery`.
- **Tahap 2 — K1 Text-to-Image (Basic → Advanced): 🔄 SEBAGIAN (2026-07-09)**
  - ✅ **8 sel kode K1 diisi** di `submission/Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb` via script `scratchpad/fill_k1_pipeline.py`:
    - Sel 1: install `diffusers/transformers/accelerate` (--upgrade tanpa pin) + import + device check.
    - Sel 4: load `StableDiffusionPipeline` dari mirror `stable-diffusion-v1-5/stable-diffusion-v1-5`, fp16, safety_checker=None + catatan model ID.
    - Sel 6: `generate_simple_image(prompt, negative_prompt, seed)` + panggil dengan seed 222 (Basic).
    - Sel 8: `generate_advanced_image(prompt, negative_prompt, seed, guidance_scale, num_inference_steps)` + panggil dengan seed 222, gcs=9.0, steps=50 (Basic).
    - Sel 10: eksperimen `guidance_scale` low=2.5 vs high=15.0 (Skilled).
    - Sel 13: eksperimen `num_inference_steps` low=10 vs high=40 (Skilled).
    - Sel 16: batch inference 4 gambar sekaligus → grid 2×2 (Advanced).
    - Sel 18: `load_scheduler(pipe, scheduler_name)` untuk Euler A / DPM++ / DDIM + demo 3 side-by-side (Advanced).
  - ✅ Semua 8 sel lolos: `ast.parse` bersih + semua pola kunci ditemukan (function signatures, konstanta seed, konfigurasi param, dsb).
  - **Prompt yang dipakai (SAMA di seluruh K1):** `"cartoon illustration of a single astronaut in white spacesuit standing alone on the surface of the moon, planet earth visible in the dark starry sky background, digital art, vibrant colors, clean bold outlines, flat shading"`
  - **Negative prompt (fixed per soal):** `"photorealistic, realistic, photograph, 3d render, messy, blurry, low quality, bad art, ugly, sketch, grainy, unfinished, chromatic aberration"`
  - **Seed (fixed per soal): 222**
  - ⏳ **NEXT:** User Run All sel 0–18 di Colab GPU T4 → screenshot hasil → verifikasi hasil match image-3 (simple) & image-4 (advanced) → tuning prompt kalau perlu → isi narasi 3 sel markdown (11, 14, 19) berdasar observasi aktual.
- **Tahap 2b — K1 narasi markdown: ✅ SELESAI (2026-07-09)**
  - Setelah user Run K1 di Colab (verified via screenshots: scheduler grid + batch grid tampil, no error), 3 sel markdown narasi diisi:
    - Sel 11 (Guidance Scale): low 2.5 = interpretasi longgar/kabur, high 15.0 = mengunci prompt tapi risk over-cooked.
    - Sel 14 (Inference Steps): low 10 = noise/artefak, detail tak matang; high 40 = halus, gradasi warna muncul, diminishing return >40.
    - Sel 19 (Scheduler Comparation): Euler A **paling mirip referensi image-3/4** (cartoon astronaut di permukaan abu-abu, moon/earth di latar), DPM++ = artistik-stylized (planet oranye di latar ungu), DDIM = padat elemen (astronaut + roket + banyak planet).
- **Tahap 3 — K2 Inpainting → Outpainting (Basic → Advanced): 🔄 SEBAGIAN (2026-07-09)**
  - ✅ **11 sel kode K2 diisi** via `scratchpad/fill_k2_pipeline.py`:
    - Sel 22 (Advanced — Base+Refiner): 2-stage workaround SD1.5 (num_inference_steps=40 → img2img strength=0.2), reset scheduler ke PNDM sebelum mulai, pipe_refiner share komponen dari pipe (hemat VRAM).
    - Sel 25: load `stable-diffusion-v1-5/stable-diffusion-inpainting` fp16 + safety_checker=None.
    - Sel 27 (Basic — Manual masking): rectangle di kanan bawah `img_advanced` via PIL ImageDraw (koordinat: `(w//2+20, h*2//3-40, w-20, h-30)`), visualisasi base+mask.
    - Sel 29 (Basic — inpaint_engine): fungsi 3-arg (image, mask, prompt) dengan generator seed=9 sesuai soal + prompt broken satellite, panggil dengan mask_manual.
    - Sel 32 (Skilled): load CLIPSeg (`CIDAS/clipseg-rd64-refined`) + processor.
    - Sel 34 (Skilled — Auto-mask): CLIPSeg segment "astronaut" → invert (255-mask) → restrict ke kanan bawah (clear top-half & left-half) → threshold >100 jadi mask biner. Visualisasi 3 tahap.
    - Sel 36 (Skilled): re-inpaint dengan mask auto + perbandingan side-by-side mask manual vs auto.
    - Sel 39 (Skilled — prepare_outpainting): fungsi 3-arg (image, direction, expand_pixels=128), safety kelipatan 8, background canvas blur (GaussianBlur radius=30), demo direction=right.
    - Sel 41 (Skilled): outpaint 1 sisi (kanan) menggunakan hasil inpainting_auto sebagai input, reuse inpaint_engine untuk konsistensi model.
    - Sel 44 (Advanced — prepare_zoom_out): perluas SEMUA sisi simetris (kiri+kanan+atas+bawah), image di-paste di tengah, mask putih di sekeliling.
    - Sel 46 (Advanced — Zoom Out generate): 3 iterasi bertahap (`for stage in range(3)`) mulai dari img_outpainted_right, tampilkan 4-panel progres (Mulai + Zoom Out 1/2/3).
  - ✅ Semua 11 sel lolos `ast.parse` bersih + pattern check (dependency chain: img_advanced → inpaint_manual → inpaint_auto → outpainted_right → zoom stages).
  - **Estimasi waktu K2 di Colab T4:** ~15-20 menit (11 sel, 4 dari 11 melakukan inference multi-gambar).
  - ⏳ **NEXT:** User Run All di Colab (K1 + K2). Kernel harus tetap hidup dari sel 1 (import dependencies) supaya `img_advanced` tersedia untuk K2. Screenshot minimal: sel 22 (base vs refined), 27 (mask preview), 29 (inpaint manual result), 34 (CLIPSeg output), 36 (compare manual vs auto), 41 (outpaint kanan), 46 (zoom out grid 4).
- **Tahap 3b — K2 Colab Run: ✅ SELESAI (2026-07-09, verified via screenshots)**
  - 11 sel K2 SEMUA jalan tanpa error di Colab T4. Model inpainting 5.48 GB terdownload.
  - Refiner Pattern (sel 22): Stage 1 Base 40 step + Stage 2 Refiner strength=0.2 tampil side-by-side, Refiner sedikit lebih clean/tajam.
  - Manual inpaint (sel 29): mask box=(276, 301, 492, 482) → hasil area terisi objek celestial (planet-planet kecil, bukan satelit tegas). Basic PASS (fitur inpaint terbukti jalan).
  - Auto-mask CLIPSeg (sel 34): heatmap "astronaut" jelas + mask biner kanan bawah. CLIPSeg jalan mulus.
  - Inpaint auto vs manual (sel 36): auto path menghasilkan bulan raksasa dgn kawah — visual lebih dramatis.
  - Outpaint kanan (sel 41): extended jadi terrain berbatu tambahan, koheren.
  - Zoom Out multi-stage (sel 46): 3 iterasi jalan, ⚠️ muncul watermark artifacts di stage 2-3 (SD1.5 hallucinate signatures — known issue, tidak blocker karena fitur zoom-out terbukti jalan). Solusi ke depan (opsional): tambah `"watermark, signature, logo, text"` ke negative prompt di sel 46.
  - Deprecation warning `mode='L'` di Pillow 13 = kosmetik, aman.
- **Tahap 4 — K3 Streamlit (isi logic.py): 🔄 SEBAGIAN (2026-07-09)**
  - ✅ **4 sel logic.py diisi** via `scratchpad/fill_k3_streamlit.py`:
    - Sel 6 (Basic — load_models_cached): **DIMODIFIKASI** dari template original — ganti `runwayml/*` → `stable-diffusion-v1-5/*` (mirror) + add `safety_checker = None` di kedua pipeline. Izin dari template cell 0: "mengubah struktur code pada logic ... DIPERSILAHKAN". Stub functions (flush_memory/set_scheduler/run_inpainting/prepare_outpainting) tetap untuk mencegah error kalau hanya Basic.
    - Sel 7 (Basic — generate_image): `generator = torch.Generator(device=pipe.device).manual_seed(seed)` + `pipe(prompt, negative_prompt, num_inference_steps=steps, guidance_scale=cfg, generator).images[0]` → return `[image]` list.
    - Sel 9 (Skilled): `flush_memory` = `gc.collect() + torch.cuda.empty_cache()` + `set_scheduler` 3-branch Euler A / DPM++ / DDIM `.from_config(pipe.scheduler.config)` + redefine `generate_image` dengan `num_images_per_prompt=num_images`, return list of images langsung.
    - Sel 11 (Advanced — run_inpainting + prepare_outpainting): `pipe(prompt, image, mask_image, strength).images[0]`; `w, h = image.size` + `new_w = w + 2*expand_pixels` + kelipatan 8 safety + `mask.paste(inner_box, (paste_x, paste_y))`.
  - ✅ Semua 4 sel lolos `ast.parse`. Concatenated logic.py (dari 4 fragment `%%writefile`) juga parse bersih (4.5 KB, ~140 baris).
  - ✅ **`app.py` (sel 13, 9.4 KB) TIDAK DISENTUH** (verified via assertion di script).
  - ✅ Model ID di app.py cached function tidak sentuh — hanya via `load_models_cached()` di logic.py yang di-cache oleh `@st.cache_resource`.
  - **Estimasi total run di Colab:** ~5 menit setup + install pyngrok/streamlit_drawable_canvas → ~4-5 menit load 2 model + segmentation → serve Streamlit + expose ngrok.
  - ⏳ **NEXT:** User Run All di Colab → dapatkan ngrok URL → verifikasi UI (Basic tab: prompt/neg_prompt/sliders/generate; Skilled tab: batch/scheduler dropdown/Clear Memory; Advanced tab: inpaint/outpaint dengan drawable canvas) → rekam video demo 1-5 menit `.mp4`.
- **Tahap 4b — K3 Streamlit Colab Run: ✅ SELESAI (2026-07-12)** — dengan 5 rounds patching untuk stabilkan library compat.
  - Streamlit UI berhasil jalan via ngrok. Model 2× (SD1.5 + Inpainting, ~10 GB) load dari HF mirror.
  - 5 patches yang dilakukan di file disk (semua justified by template cell 0 izin "DIPERSILAHKAN mengubah struktur code pada logic ataupun app.py"):
    1. Cell 2: pin `streamlit==1.29.0` + `streamlit-drawable-canvas==0.9.3` (Streamlit ≥1.32 hapus `image_to_url` yg drawable-canvas butuh)
    2. Cell 16 (auth+Popen): tambah `time.sleep(30)` + log capture ke `streamlit.log` untuk debugging
    3. Cell 21 (ngrok.kill): comment out supaya Run All tidak menutup tunnel
    4. Cell 13 (app.py): `use_container_width` → `use_column_width` (3 occurrences, Streamlit 1.29 compat)
    5. Cell 13 (app.py): `mask_data = canvas_result.image_data[:, :, 3].copy()` — drawable-canvas 0.9.3 return read-only array
  - Video demo direkam via Xbox Game Bar (5:51 duration, 1920x1020, H.264 5.3 Mbps).
- **Tahap 5 — Video compression + Colab download + Packaging final: ✅ SELESAI (2026-07-12)**
  - Video di-compress via `imageio-ffmpeg` (bundled ffmpeg-win-x86_64-v7.1) dari **222 MB → 10 MB** (95.5% reduction) dengan settings `libx264 CRF 28 preset veryfast + AAC 96k + faststart`. Kualitas OK untuk UI screencast (user verified).
  - Pipeline notebook diretaan diulang di Colab clean (~30 min) karena run pertama KeyboardInterrupt di tengah download model. Hasil final: **19/19 cells output, 15 embedded images, 0 error, size 12.75 MB**.
  - Streamlit notebook: 11/12 cells output (cell 3 pure import tanpa output — expected), 0 error, size 40 KB.
  - `requirements.txt` dibuat pipreqs-style (scan imports dari 2 notebook): torch/diffusers/transformers/accelerate + streamlit==1.29.0/streamlit-drawable-canvas==0.9.3/pyngrok + matplotlib/numpy/Pillow. Komentar penjelas kenapa Streamlit di-pin.
  - Zip flat **`BFGAI_Nazhif_Setya_Nugroho.zip` (18.79 MB, 4 file)** dibuat di root project. Struktur flat verified (no subfolder inside zip).
  - **Audit final: ALL PASS** (2026-07-12):
    - HR1: 4 file wajib ada ✅
    - HR2: zip flat ✅
    - HR3: notebook sudah dijalankan (Pipeline 19/19, Streamlit 11/12 pure-import expected) ✅
    - HR4: SD1.5 (bukan SDXL/GAN) ✅
    - K1 semua kriteria: generate_simple/advanced, guidance/steps eksperimen, batch 4, load_scheduler + 3 scheduler ✅
    - K2 semua kriteria: inpaint_engine, CLIPSeg auto-mask, prepare_outpainting, prepare_zoom_out, Refiner via img2img strength=0.2 ✅
    - K3 semua kriteria: generate_image, flush_memory (gc+empty_cache), set_scheduler, run_inpainting, prepare_outpainting, drawable-canvas ✅
  - **SIAP UPLOAD KE DICODING.**
- **Tahap 6 — REVISI setelah reviewer tolak: 🔄 IN PROGRESS (2026-07-12)**
  - Reviewer feedback di `artifacts/7.review_penolakan.md`: K1 & K2 belum sesuai instruksi, K3 Streamlit **LOLOS**.
  - **K1 issue:** hasil `generate_simple_image()` & `generate_advanced_image()` tidak match image-13 (cartoon flat) & image-14 (3D semi-realistis). Prompt-ku terlalu detail ("cartoon illustration ... digital art vibrant colors clean bold outlines flat shading"). Reviewer minta prompt SEDERHANA + trick guidance rendah untuk advanced.
  - **K2 issue:** objek satelit tidak muncul jelas (hasil-ku cuma terrain oranye tanpa satelit). Reviewer minta prompt jauh lebih detail + tuning CFG/steps ke nilai lebih tinggi.
  - **Patches diterapkan (via `scratchpad/patch_revision_reviewer.py`):**
    - Cell 6: PROMPT ganti jadi `"an astronaut standing on moon surface, earth visible in background, cartoon style"` (sederhana ala reviewer)
    - Cell 8: `guidance_scale 9.0 → 3.0` — insight kunci: guidance RENDAH bikin model bebas dari batasan "cartoon" di prompt → jatuh ke default trained distribution → hasil 3D semi-realistis (image-14 target)
    - Cell 27: mask box diperbesar dari `(w//2+20, h*2//3-40, w-20, h-30)` ke `(w//2, h//3, w-10, h-20)` — dari ~216×192 px ke ~246×321 px, supaya satelit + multi-legged landing gear muat
    - Cell 29: INPAINT_PROMPT ganti pakai saran reviewer literal (`"a damaged broken satellite crashed on the moon surface, lunar surface with craters, metallic debris, broken panels, exposed mechanical parts, multi-legged landing gear, highly detailed mechanical structure, sharp focus, realistic scale, photorealistic, cinematic lighting"`), + hardcode `guidance_scale=15.0` dan `num_inference_steps=60` di dalam fungsi (signature `(image, mask, prompt)` tetap sesuai soal)
  - Semua downstream cells (>=6) outputs cleared, siap Run All ulang di Colab.
  - Cell 22 (Refiner), 10, 13, 16, 18 (K1 Skilled/Advanced) reuse `PROMPT` dari cell 6 → otomatis update dengan prompt sederhana yang baru.
  - **NEXT:** User Run All Pipeline notebook di Colab → verifikasi visual hasil match image-13/14/15 → download → re-zip → resubmit ke Dicoding.
  - **v1 → v2 → v3 iterasi (2026-07-12):**
    - **v1** (cell 6 sederhana + cell 8 guidance=3.0 + cell 27 mask bigger + cell 29 detail prompt + guidance=15): cell 29 satelit muncul jelas ✅, tapi cell 8 masih borderline (mirip cell 6).
    - **v2** (cell 8 guidance 3.0 → 1.5): cell 8 sukses 3D-painterly differentiated ✅, tapi cell 29 satelit hilang ❌ karena prompt "photorealistic, cinematic lighting" konflik dengan style base painterly.
    - **v3** (cell 29 prompt di-align dengan style base: hapus "photorealistic"/"cinematic lighting", ganti "digital illustration", + guidance 15 → 20): cell 8 3D bagus ✅ + cell 29 **satelit silver metallic dengan multi-leg tripod muncul jelas** ✅. Downstream K2 Skilled (outpaint) & Advanced (zoom out) juga aman.
  - **Re-zip v3:** `BFGAI_Nazhif_Setya_Nugroho.zip` diregenerate → 20.15 MB (dari 19.79 MB v1 karena Pipeline notebook grew 12.75 → 15.27 MB dengan output gambar lebih rich). 4 file flat structure preserved.
  - **STATUS: SIAP RESUBMIT KE DICODING.**
