# 📋 Checklist Pengerjaan — BFGAI Dafina (target Basic ⭐⭐⭐)

> Centang tiap item selesai. Sumber kebenaran status detail → [`../CLAUDE.md`](../CLAUDE.md) Progress Log.

## Tahap penyiapan (oleh Claude)
- [x] Baca semua instruksi Dicoding + 2 review penolakan Nazhif (resep lolos dicatat)
- [x] Scaffold folder + salin 2 template + `.gitignore` + `CLAUDE.md`
- [x] Isi Pipeline notebook — **K1 Basic** (sel 1, 4, 6, 8)
- [x] Isi Pipeline notebook — **K2 Basic** (sel 25, 27, 29)
- [x] Isi Streamlit notebook — `logic.py` lengkap + patch model mirror + patch kompat `app.py`
- [x] Tulis panduan Colab

## Tahap eksekusi (oleh Dafina di Colab T4)
- [ ] **Pipeline** Run All → cek `img_simple` (≈image-13), `img_advanced` (≈image-14), `img_inpaint` (≈image-15)
- [ ] Kirim screenshot 3 gambar ke Claude → verifikasi / tuning
- [ ] Download Pipeline `.ipynb` ber-output → taruh di `submission/`
- [ ] **Streamlit** isi token ngrok (cell 16) → Run All → buka URL
- [ ] Rekam **video demo Basic** (prompt + slider + Generate + gambar tampil) → `video_demo_aplikasi_BFGAI.mp4`
- [ ] Download Streamlit `.ipynb` ber-output → taruh di `submission/`

## Tahap packaging (oleh Claude)
- [ ] Sanitasi token ngrok di notebook Streamlit
- [ ] Buat `requirements.txt`
- [ ] Zip flat `BFGAI_Dafina_Meira_Rizkia.zip` (4 file)
- [ ] Audit final Hard Rules + update STATUS + commit

## Tahap submit (oleh Dafina)
- [ ] Upload zip ke Dicoding

---

## ✅ Peta kriteria Basic (yang dikejar)

### K1 — Text-to-Image (2 pts)
- [ ] `generate_simple_image(prompt, negative_prompt, seed)` pakai `StableDiffusionPipeline` + SD1.5 ✔ *(kode siap, tinggal run)*
- [ ] `generate_advanced_image(...)` + `guidance_scale` + `num_inference_steps` ✔ *(kode siap)*
- [ ] Seed **222**, negative prompt tetap, prompt **sama** di kedua fungsi ✔
- [ ] Hasil mirip contoh (simple=flat, advanced=3D) → **verifikasi visual saat run**

### K2 — Image-to-Image (2 pts)
- [ ] `inpaint_engine(image, mask, prompt)` pakai `StableDiffusionInpaintPipeline` ✔ *(kode siap)*
- [ ] Masking **manual hardcode** (trial & error) ✔ *(numpy box)*
- [ ] Seed **9**, ada **broken satellite** jelas → **verifikasi visual saat run**

### K3 — Streamlit (2 pts)
- [ ] Text input prompt + negative prompt ✔ *(ada di app.py)*
- [ ] Slider `guidance_scale` + `num_inference_steps` ✔
- [ ] Tombol **Generate** ✔
- [ ] Gambar hasil **tampil langsung** ✔ → **buktikan di video**
- [ ] Video `.mp4` 1–5 menit → **direkam Dafina**

> Catatan: `logic.py` sengaja diisi penuh (termasuk fungsi scheduler/inpaint) supaya app tidak error, tapi **grade target tetap Basic** — video cukup menampilkan alur Basic.
