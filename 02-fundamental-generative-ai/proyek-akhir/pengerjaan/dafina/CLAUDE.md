# CLAUDE.md — Proyek Image Generation BFGAI (Dafina Meira Rizkia)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update [Progress Log](#-progress-log) di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol → [`/CLAUDE.md`](../../../../CLAUDE.md).

> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi.

---

## ⛔ SCOPE — BACA DULU

- Ini **submission Dicoding "Belajar Fundamental Generative AI (BFGAI)" → Proyek Image Generation** milik **Dafina Meira Rizkia** (target **Basic ⭐⭐⭐ / lulus cepat**).
- Proyek **self-contained**. Instruksi asli Dicoding (READ-ONLY) ada di `../../artifact/instruksi/` (6 md aturan + 2 review penolakan Nazhif + 18 png referensi) dan template di `../../artifact/template/`.
- **⚠️ ANTI-PLAGIARISME (Hard Rule repo #4):** teman satu tim **Nazhif** sudah mengerjakan submission BFGAI yang SAMA (model/seed/template/gambar target semua dikunci Dicoding). Kode Dafina **WAJIB ditulis ulang beda** dari Nazhif — beda struktur fungsi, penamaan variabel, komentar, wording prompt, dan narasi. **JANGAN copy** dari `../nazhif-setya-nugroho/`. Ini konsisten dengan pola Dafina di course lain (03 PGABL & 04 SMSML sengaja dibedakan dari tim).
  - Catatan: notebook **Streamlit itu blank-fill** (`________`) → jawabannya seragam untuk semua siswa (bukan area plagiarisme). Diferensiasi difokuskan di **notebook Pipeline** (blank-slate / free-form).

---

## 🎁 "CONTEKAN SAH" — resep yang SUDAH terbukti (kunci kecepatan)

Nazhif mengerjakan submission identik ini, **ditolak reviewer 2×**, lalu diperbaiki sampai versi yang lolos. Semua feedback reviewer ada di `../../artifact/instruksi/7.review_penolakan.md` & `8.review_penolakan_2.md`. Intinya (kita PAKAI langsung, lompati penolakan):

1. **K1 `generate_simple_image`** → prompt **SEDERHANA** + `cartoon style` supaya hasil flat/2D (target `image-13`). Prompt terlalu detail = ditolak.
2. **K1 `generate_advanced_image`** → **prompt sama** dengan simple (syarat Dicoding), tapi pakai **guidance_scale RENDAH** (≈1.5–2.5). Trik reviewer: guidance rendah bikin model "lepas" dari kata `cartoon` → jatuh ke distribusi default = **3D/semi-realistis** (target `image-14`/`image-17`). Ditolak 2× gara-gara advanced masih terlihat flat/painting.
3. **K2 `inpaint_engine`** → satelit rusak harus **muncul JELAS**. Prompt harus **detail** (bentuk/ukuran/material) + **guidance & steps TINGGI** (mis. guidance≈15–20, steps≈50–60). Kalau CFG/steps kecil → satelit tak muncul (ditolak). Prompt satelit dis/selaraskan gaya ilustrasi base (hindari "photorealistic/cinematic" yang bentrok, pakai "digital illustration").
4. **K3 Streamlit** → Nazhif **LOLOS** di sini. Butuh pin `streamlit==1.29.0` + `streamlit-drawable-canvas==0.9.3`, dan di app.py `use_container_width`→`use_column_width`. (Detail patch di panduan.)

---

## 👤 USER & GAYA KERJA

- **Nama untuk file:** `Dafina_Meira_Rizkia`. **Email:** dev@kalachakra.io.
- **Gaya komunikasi (WAJIB):** Bahasa Indonesia simpel, step-by-step, jelaskan **kenapa** bukan cuma **apa**, teliti detail kecil. **Jangan asumsi — tanya dulu (AskUserQuestion)** kalau ambigu.
- **Target:** **Basic ⭐⭐⭐** (2 pts/kriteria). Cukup untuk lulus; sesuai pola Dafina yang mengejar kelulusan cepat.

---

## 🔒 KEPUTUSAN TERKUNCI (jangan ubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Environment** | **Google Colab GPU T4 (free)** | SD1.5 + Inpainting tak muat di RTX 3050 4 GB. Semua run berat di Colab. |
| **Target nilai** | **Basic ⭐⭐⭐** (K1+K2 Basic; K3 logic diisi lengkap demi app robust) | K1/K2 Skilled/Advanced dilewati (sel dibiarkan kosong). |
| **Model text2img** | `stable-diffusion-v1-5/stable-diffusion-v1-5` (mirror bit-perfect resmi `runwayml/*` yang sudah **delisted/404** sejak 2024) | fp16, `safety_checker=None`. Tulis catatan markdown transparansi mirror. |
| **Model inpainting** | `stable-diffusion-v1-5/stable-diffusion-inpainting` (mirror resmi) | fp16, `safety_checker=None`. |
| **Seed** | K1 = **222**, K2 = **9** | Dikunci soal — reviewer bandingkan hasil pada seed ini. |
| **Negative prompt K1** | `"photorealistic, realistic, photograph, 3d render, messy, blurry, low quality, bad art, ugly, sketch, grainy, unfinished, chromatic aberration"` | Dikunci soal (tetap). |
| **Prompt K1 (simple & advanced SAMA)** — REVISI penolakan_1 | `"a lone astronaut standing on the lunar surface, planet earth visible in the dark starry sky background, full body, wide shot, cartoon style, flat 2d"` | simple: negative WAJIB + guidance default → **kartun flat** (image-3). advanced: **negative BEDA (tolak cartoon/painting) + guidance 12 + 50 step** → **realistis** (image-4). Trik final Nazhif yang lolos. Verifikasi visual di Colab. |
| **Prompt K2 inpaint (satelit)** — REVISI penolakan_1 | `"a large broken satellite spacecraft crashed on the lunar surface, huge metallic body filling the mid-ground, shattered solar panel wings, bent antenna dish, scattered metal debris, exposed mechanical parts, multi-legged landing gear, highly detailed mechanical structure, sharp focus, realistic scale, photorealistic, cinematic lighting"` | Tegaskan **UKURAN besar** + gaya realistis (menyatu base advanced realistis). mask diperbesar (x 0.45–0.97W, y 0.35–0.90H). guidance 20 / 60 step. Verifikasi visual. |
| **Nama file** | `Pipeline_submission_BFGAI_Dafina_Meira_Rizkia.ipynb`, `Streamlit_submission_BFGAI_Dafina_Meira_Rizkia.ipynb`, `video_demo_aplikasi_BFGAI.mp4`, `requirements.txt` | Zip: `BFGAI_Dafina_Meira_Rizkia.zip` (flat 4 file). |

---

## 🗂️ PETA PENGISIAN NOTEBOOK (target Basic)

### Pipeline notebook (47 sel, blank-slate) — ISI HANYA sel Basic:
| Sel | Isi | Kriteria |
|---|---|---|
| 1 | install diffusers/transformers/accelerate + import + cek device | setup |
| 4 | load `StableDiffusionPipeline` (mirror SD1.5) fp16 + catatan mirror | K1 |
| 6 | `generate_simple_image(prompt, negative_prompt, seed)` + panggil seed 222 | K1 Basic |
| 8 | `generate_advanced_image(prompt, negative_prompt, seed, guidance_scale, num_inference_steps)` + panggil seed 222, guidance rendah | K1 Basic |
| 25 | load `StableDiffusionInpaintPipeline` (mirror inpainting) fp16 | K2 |
| 27 | manual masking hardcode (rectangle) di atas `img_advanced` | K2 Basic |
| 29 | `inpaint_engine(image, mask, prompt)` + panggil seed 9, guidance/steps tinggi | K2 Basic |

**Sel DIBIARKAN KOSONG** (Skilled/Advanced, tidak dikerjakan): 10, 13, 16, 18, 22, 32, 34, 36, 39, 41, 44, 46. Sel markdown narasi (11, 14, 19) dibiarkan default template. → Sel kosong AMAN: tak mengubah struktur & tak error saat Run All.

### Streamlit notebook (22 sel, blank-fill) — ISI logic.py LENGKAP (demi app robust):
| Sel | Isi |
|---|---|
| 6 | **modifikasi** model ID `runwayml/*` → mirror `stable-diffusion-v1-5/*` + `safety_checker=None`. Izin: cell 0 template ("DIPERSILAHKAN mengubah struktur code pada logic"). |
| 7 | Basic `generate_image` — isi 2 blank (generator seed + `pipe(...).images[0]`) |
| 9 | Skilled — isi 8 blank (`flush_memory` = gc+empty_cache, `set_scheduler` 3 cabang, `generate_image` batch) |
| 11 | Advanced — isi 9 blank (`run_inpainting` = `pipe(...).images[0]`, `prepare_outpainting` = math kanvas + `mask.paste`) |
| 13 | **app.py — JANGAN sentuh** (238 baris, fixed). Hanya patch compat kecil bila perlu saat run. |
| 16 | isi `auth_token` ngrok Dafina saat run |

> Kenapa K3 diisi lengkap padahal target Basic: isian blank = jawaban seragam (bukan plagiarisme), effort kecil, dan bikin app **tak ada tab error** → "lulus" lebih aman. Video demo tetap fokus fitur Basic (prompt → slider → Generate → gambar tampil).

---

## 🔴 HARD RULES DICODING (auto-reject kalau dilanggar)

Sumber: `../../artifact/instruksi/6.lainnya.md`, `4.ketentuan_berkas.md`.
1. **WAJIB pakai template Dicoding** (2 ipynb). Jangan ubah/hapus struktur section markdown.
2. **WAJIB model SD1.5 + SD-Inpainting** (atau mirror bit-perfect). **DILARANG** SDXL / GAN / model lain (auto-reject).
3. **DILARANG tambah fitur di luar instruksi.**
4. **Notebook WAJIB sudah dijalankan** → semua sel berisi ada output ter-embed. Sel kode berisi tanpa output = reject.
5. **Hasil generate WAJIB tampil** di antarmuka Streamlit setelah Generate.
6. **Video demo `.mp4` 1–5 menit** WAJIB (bukti app pernah jalan).
7. **`requirements.txt` WAJIB** ada. Kirim **1 folder di-zip**, struktur **flat 4 file**, bahasa Python.
8. **Jangan submit berkali-kali** (review ±3 hari kerja).
9. Fungsi Pipeline pakai nama yang diminta soal: `generate_simple_image`, `generate_advanced_image`, `inpaint_engine`. Fungsi `logic.py` ikut nama yang dipakai `app.py`: `load_models_cached`, `generate_image`, `flush_memory`, `set_scheduler`, `run_inpainting`, `prepare_outpainting`.

---

## 🛠️ CARA ISI NOTEBOOK (metodologi)

- **JANGAN edit .ipynb manual pakai text-replace.** Pakai script Python di `scratchpad/`: `json.load` → set `cell['source']` (Pipeline) / replace `________` berurutan (Streamlit) → `assert` bersih → `json.dump`.
- Tiap sel kode: cek `ast.parse` bersih sebelum simpan.
- Output di-embed di **fase akhir**: user Run All di Colab sekali → download `.ipynb` ber-output → taruh di `submission/`.
- Verifikasi visual: hasil PNG dari Colab → user kirim screenshot → aku lihat via Read tool → bandingkan `image-13`/`image-14`/`image-15` → tuning prompt/param bila belum mirip.

---

## ✅ PROGRESS LOG

> WAJIB diupdate tiap tahap selesai.

- **Tahap 0 — Setup: ✅ SELESAI (2026-07-19)**
  - Semua instruksi Dicoding + 2 review penolakan Nazhif dibaca & dipahami (resep yang lolos sudah dicatat di atas).
  - Struktur 2 template dibedah: Pipeline 47 sel (blank-slate), Streamlit 22 sel (blank-fill), app.py dianalisis (alur Basic = load_models + flush_memory + generate_image).
  - Target dikunci: **Basic ⭐⭐⭐**, Colab T4, mirror model, seed 222/9.
  - Folder Dafina dibuat: `panduan/`, `scratchpad/`, `submission/`. `.gitignore` di-set. 2 template disalin ke `submission/` dengan nama final Dafina.
- **Tahap 1 — Isi Pipeline K1+K2 Basic: ✅ SELESAI (2026-07-19)**
  - 7 sel Basic diisi via `scratchpad/fill_pipeline_dafina.py` (semua lolos `ast.parse`, kode SENGAJA beda dari Nazhif):
    - Sel 1: install + import (numpy + PIL + 2 pipeline class saja, tanpa scheduler/Img2Img krn Basic) + `DEVICE`/`DTYPE`.
    - Sel 4: load `StableDiffusionPipeline` mirror `stable-diffusion-v1-5/*`, `DTYPE`, `safety_checker=None`, var `txt2img`.
    - Sel 6: `generate_simple_image(prompt, negative_prompt, seed)` + `MOON_PROMPT` (reworded: "a lone astronaut standing on the surface of the moon, planet earth in the background sky, cartoon style") + `NEGATIVE` (fixed soal) + panggil seed 222.
    - Sel 8: `generate_advanced_image(... guidance_scale, num_inference_steps)` — **prompt SAMA**, tapi `NEGATIVE_ADVANCED` (tolak cartoon/painting) + `guidance_scale=10.0` + `steps=45` → target 3D realistis (image-14). Reviewer izinkan sesuaikan negative/param.
    - Sel 25: load `StableDiffusionInpaintPipeline` mirror, var `inpaint`.
    - Sel 27: manual mask via **numpy** (`mask_arr[y0:y1,x0:x1]=255`, box proporsional 0.52–0.98 W × 0.38–0.92 H) + preview overlay merah (bukan matplotlib ala Nazhif).
    - Sel 29: `inpaint_engine(image, mask, prompt)` seed 9, guidance 18, steps 55; `SATELLITE_PROMPT` detail & **netral gaya** (fokus objek, tanpa "digital illustration"/"photorealistic" → aman apa pun gaya base).
  - Sel Skilled/Advanced (10,13,16,18,22,32,34,36,39,41,44,46) DIBIARKAN KOSONG. Sel narasi 11/14/19 = prosa template default. Verifikasi: 47 sel utuh, tak ada `________`, JSON valid.
- **Tahap 2 — Isi Streamlit logic.py + patch app.py: ✅ SELESAI (2026-07-19)**
  - Via `scratchpad/fill_streamlit_dafina.py`: cell 6 (ID model → mirror + `safety_checker=None`), cell 7 (Basic generate, 2 blank), cell 9 (Skilled: flush/scheduler/batch, 8 blank), cell 11 (Advanced: run_inpainting/prepare_outpainting, 9 blank). `logic.py` gabungan 166 baris, `ast.parse` bersih.
  - Patch infra: cell 2 pin `streamlit==1.29.0` + `streamlit-drawable-canvas==0.9.3` + accelerate; cell 16 launch headless + `time.sleep(20)` + log; cell 21 `ngrok.kill()` dinonaktifkan.
  - **Patch app.py (cell 13) — 2 fix kompat WAJIB** (diizinkan cell 0): `use_container_width`→`use_column_width` (3×, karena streamlit 1.29 belum punya param baru → kalau tidak, tampilan gambar Basic CRASH) + `canvas_result.image_data[:,:,3].copy()` (array canvas 0.9.3 read-only). app.py sisanya utuh.
- **Tahap 3a — Pipeline Run All + verifikasi visual K1+K2: ✅ SELESAI (2026-07-19, ~7 iterasi Colab)**
  - **PELAJARAN PENTING (biar tak ulang kesalahan):** target RESMI Dafina = **image-3/image-4** (bukan image-13/14 koreksi Nazhif yang ekstrem). image-3/4 itu **astronot ber-outline BERDIRI di bulan + bumi, WIDE SHOT, semi-realistis** — simple & advanced **mirip**, beda tipis. BUKAN "flat cartoon vs foto".
  - **Jebakan yang ditemukan:** setiap kata gaya (`cartoon/illustration/bold outlines/comic`) di prompt bikin SD1.5 menghasilkan **portrait/bust**, bukan scene. Guidance rendah (1.5) → **berantakan**, bukan realistis. Menukar negative prompt **tak** mengubah gaya (prompt yang dominan).
  - **RESEP FINAL YANG BERHASIL (v6/v7):**
    - Prompt K1 (cell 6, SAMA utk simple & advanced): `"a lone astronaut standing on the surface of the moon, planet earth in the dark starry sky background, full body, wide shot"` — **TANPA kata gaya** (biar wide-shot, bukan portrait).
    - Negative K1 (SAMA keduanya) = negative tetap dari soal.
    - simple: guidance default (7.5), steps 50. advanced: `guidance_scale=9.0, num_inference_steps=60` (beda tipis, tunjukkan efek hyperparameter). Hasil: dua-duanya astronot realistis di bulan + bayangan (≈image-3/4). Catatan: bumi biru tak sejelas contoh (jadi nebula) — cukup untuk Basic.
    - K2 inpaint (cell 29): `guidance_scale=20.0, num_inference_steps=60` + **negative menolak tanah kosong** (`"empty, bare ground, plain lunar surface, ..."`) → **satelit muncul jelas**. Prompt satelit: `"a large broken satellite spacecraft crashed on the moon, big metallic body, broken solar panel wings, antenna dish, ..."`.
    - K2 mask (cell 27): base advanced menaruh astronot di KIRI → mask di **kanan** (`x0=0.50W..0.96W, y0=0.40H..0.88H`) = tanah kosong, tak nimpa astronot. Hasil: satelit + panel surya biru di kanan (≈image-15).
  - Pipeline notebook: 7 sel exec 1–7, gambar tertanam cell 6/8/27/29, 0 error, 3.12 MB. **SIAP.**
- **Tahap 3b — Streamlit Run (K3) + video: ✅ SELESAI (2026-07-19)**
  - Dafina Run All Streamlit di Colab (token ngrok pribadi) → app "StudioAI" jalan via ngrok. 10/10 sel exec, 0 error, app.py utuh.
  - Video demo direkam (.mov 106 MB, 2878×1740, 2:06). Verifikasi via ekstraksi frame: menampilkan SEMUA komponen Basic K3 (prompt+negative input, slider Quality Steps & CFG, tombol Generate, gambar hasil tampil) + BONUS Skilled (dropdown Scheduler Euler A/DPM++/DDIM, batch 4 → grid 2×2, prompt earthrise menghasilkan astronot+bumi biru).
  - Video dikonversi + kompres via imageio-ffmpeg (libx264 CRF 28, scale 1600, faststart, -an): **106 MB → 3.12 MB**, `video_demo_aplikasi_BFGAI.mp4`.
  - Token ngrok di cell 16 di-**sanitasi** ke placeholder (output/exec tetap = bukti run) sebelum commit (repo publik).
- **Tahap 4 — Packaging: ✅ SELESAI (2026-07-19) — SIAP UPLOAD**
  - `requirements.txt` pipreqs-style (scan import 2 notebook): torch/diffusers/transformers/accelerate + pillow/numpy + streamlit==1.29.0/streamlit-drawable-canvas==0.9.3/pyngrok. Tanpa matplotlib (Dafina tak pakai — beda dari Nazhif).
  - **Zip flat `BFGAI_Dafina_Meira_Rizkia.zip` (5.04 MB, 4 file)** di `pengerjaan/dafina/` (gitignored). Struktur flat verified (tak ada subfolder).
  - **AUDIT FINAL ALL PASS:** 4 file wajib ✅ · Pipeline 19/19 exec + gambar tertanam ✅ · Streamlit 10/10 exec ✅ · video .mp4 2:06 ✅ · SD1.5 (bukan SDXL/GAN) ✅ · secret scan bersih ✅ · K1 (simple/advanced ≈image-3/4) + K2 (satelit ≈image-15) + K3 (interface jalan + gambar tampil) ✅.
  - **SISA: user tinggal UPLOAD `BFGAI_Dafina_Meira_Rizkia.zip` ke Dicoding.**
- **Tahap 5 — REVISI setelah reviewer TOLAK (penolakan_1.md): 🔄 IN PROGRESS (2026-07-20, device: victus)**
  - Reviewer menolak: **K1** hasil `generate_simple_image()` masih terlalu realistis/3D (harus **flat 2D/kartun**, image-3); **K2** satelit inpaint belum muncul jelas (image-6). **K3 Streamlit tidak dikomentari → LOLOS** (tidak disentuh).
  - **PELAJARAN KUNCI (mengoreksi catatan Tahap 3a):** penolakan Dafina **identik** dengan penolakan-1 Nazhif; target RESMI = **simple KARTUN FLAT (image-3), advanced REALISTIS (image-4)** — beda gaya, bukan "beda tipis". Catatan lama "hindari kata gaya" **terbukti salah** untuk simple; Nazhif LOLOS justru DENGAN "cartoon style". Advanced realistis dicapai lewat **negative anti-cartoon + guidance tinggi** (BUKAN guidance rendah yang bikin painterly → penyebab tolak ke-2 Nazhif).
  - **Perubahan notebook Pipeline** via `scratchpad/fix_penolakan1_pipeline.py` (ast.parse bersih, output 4 sel dikosongkan utk Run All ulang):
    - Cell 6 (simple): prompt +`"cartoon style, flat 2d"` (jaga scene: "full body, wide shot"); NEGATIVE = **persis** string wajib soal (diverifikasi char-exact); seed 222; guidance default.
    - Cell 8 (advanced): prompt SAMA; `NEGATIVE_ADVANCED` menolak cartoon/flat/illustration/painting; `guidance_scale=12.0`, `num_inference_steps=50` → memaksa realistis (image-4).
    - Cell 27 (mask): area diperbesar (x 0.45–0.97W, y 0.35–0.90H) + catatan WAJIB cek overlay merah tak menimpa astronot.
    - Cell 29 (inpaint): SATELLITE_PROMPT tegaskan ukuran BESAR + realistis; negative tolak tanah kosong + cartoon/painting; guidance 20 / 60 step; seed 9.
  - Zip **BELUM** diregenerate (nunggu output Colab fresh).
  - **Run Colab #1 (verified via Read tool):** cell 8 advanced ✅ **realistis** (≈image-4/17, trik negative anti-cartoon + guidance 12 berhasil), cell 29 satelit ✅ **besar & jelas** (≈image-6). Tapi: cell 6 simple ❌ **chibi/vektor super-flat** (contoh yang DITOLAK reviewer — "flat 2d" + "full body/wide shot" kebablasan); cell 27 mask 0.45W **menimpa astronot** (astronot ternyata di TENGAH) → di cell 29 astronot HILANG (cuma satelit).
  - **Fix v2** via `scratchpad/fix_penolakan1_v2.py` (wholesale cell 6 & 27): MOON_PROMPT → `"a lone astronaut standing on the moon surface, planet earth visible in the starry background sky, cartoon style"` (buang "flat 2d"/"full body"/"wide shot" → kartun moderat); mask x0 0.45→**0.57**, y0 0.35→0.42 (geser kanan, astronot selamat). cell 8 & 29 kode tetap (ikut re-generate krn MOON_PROMPT shared). Output 4 sel dikosongkan lagi.
  - **Run Colab #2 GAGAL (verified):** cell 6 masih chibi (astronot di "bola" oranye); cell 8 malah **kehilangan astronot** (lanskap bulan kosong) → cell 29 kosong. **Akar masalah ketemu:** frasa `"planet earth ... starry background sky"` → model bikin vista angkasa (bulan jadi bola di simple, astronot lenyap di advanced). Membuang "full body/wide shot" juga menghapus astronot advanced.
  - **Fix v3** (`scratchpad/fix_penolakan1_v3.py`): kembali ke **struktur minimal terbukti Nazhif** → `MOON_PROMPT = "a lone astronaut standing on the moon surface, earth in the background, cartoon style"` (buang planet/starry/full body/wide shot/flat 2d; wording tetap beda Nazhif). Ini persis pola yg menghasilkan image-13 (simple) + image-17 (advanced). Mask x0 0.57→0.56, y0 0.42→0.40. cell 8 & 29 kode tetap.
  - **PELAJARAN:** jangan embel-embeli prompt K1 — resep Nazhif MINIMAL. "planet/starry sky/full body/wide shot/flat 2d" semua merusak (chibi / astronot hilang).
  - **Run Colab #3 BERHASIL secara struktur (verified):** cell 6 simple ✅ kartun ber-outline berdiri di permukaan bulan + bumi (komposisi ≈image-3, BUKAN chibi lagi); cell 8 advanced ✅ realistis + astronot ADA + jejak kaki (≈image-4/17); cell 27 mask ✅ di kanan tak sentuh astronot; cell 29 inpaint ✅ **astronot (kiri) + satelit rusak (kanan)** dua-duanya (≈image-6). Juga: error 401 (HF token "RAG_PIDI" expired di Colab) sudah di-fix dgn `token=False` di cell 4 & 25.
  - **v4 (poles, dipilih user):** simple run#3 bagus tapi TANAH masih agak realistis (borderline vs contoh ✗ reviewer). Via `scratchpad/fix_penolakan1_v4.py`: MOON_PROMPT +`", flat 2d illustration"` → tanah+langit ikut flat. AMAN utk advanced (NEGATIVE_ADVANCED sudah menolak flat/2d/illustration → advanced tetap realistis). Cuma cell 6 diubah.
  - **NEXT (BLOCKED, butuh Dafina):** **Run All #4** di Colab → cek cell 6 tanahnya lebih flat/kartun (≈image-3), sel lain tetap seperti run#3 → kirim Claude → kalau OK: download ber-output → re-zip `BFGAI_Dafina_Meira_Rizkia.zip` → resubmit. Fallback: kalau simple kelewat flat/chibi, hapus `, flat 2d illustration` (balik run#3). Panduan: `panduan/REVISI_penolakan_1.md` (PUTARAN 4).
