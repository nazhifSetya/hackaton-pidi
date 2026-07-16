# Panduan Deploy Netlify + Zip Submission — Root Facts App

> Target: **BASIC (⭐⭐⭐ lulus)** — kejar 2 pt per kriteria. 3 langkah singkat: **coba lokal → deploy Netlify → zip & upload**.

---

## ✅ Status Implementasi (yang sudah selesai agent)

| Kriteria | Status | Bukti |
|---|---|---|
| K1 — Kamera + TF.js deteksi 18 label sayuran | ✅ Basic done | `detector.predict()` verified return `{className, confidence}` di CDP test |
| K2 — Transformers.js SmolLM2-135M-Instruct fun fact dinamis | ✅ Basic done | Carrot vs Spinach hasilkan fun fact BERBEDA (verified) |
| K3 — Manifest valid + SW Workbox precache + offline works | ✅ Basic done | Server dimatikan → reload page → app tetap muncul lengkap |

Yang masih perlu **user** (Nazhif) lakukan: langkah 1 (test kamera real), langkah 2 (deploy Netlify), langkah 3 (zip + upload Dicoding).

---

## LANGKAH 1 — Coba di Browser Real (dengan kamera Victus)

Agent sudah verifikasi via automated headless browser (tanpa kamera nyata). Sekarang test dgn webcam Victus:

```powershell
cd d:\Kalachakra\docs\hackaton_PIDI\belajar-penerapan-ai-di-aplikasi-web\proyek_akhir\submission\root-facts
npx serve@14 . -l 5173 --cors
```

Buka **Chrome/Edge** di `http://localhost:5173/`.

**Checklist test manual:**

1. [ ] Header awalnya "Memuat model..." → "Memuat AI..." → "Siap" (butuh ~30-60 detik pertama untuk download model SmolLM2 ~90 MB dari HuggingFace CDN — cache setelah itu).
2. [ ] Klik tombol scan hijau di bawah kamera. Browser tanya izin kamera → **Allow**.
3. [ ] Video webcam muncul. Arahkan ke sayuran real (atau HP tampilin gambar sayuran dari internet).
4. [ ] Tunggu 1-3 detik. Card hasil muncul dengan:
   - **Nama sayuran** terdeteksi (18 label: Beetroot, Paprika, Cabbage, Carrot, Cauliflower, Chilli, Corn, Cucumber, Eggplant, Garlic, Ginger, Lettuce, Onion, Peas, Potato, Turnip, Soybean, Spinach)
   - **Confidence %** (bar hijau)
   - **Fun fact text** (bahasa Inggris, ~1-2 kalimat, unik per sayuran)
5. [ ] Buka **DevTools > Application > Manifest** → cek nama, icon 192/512 muncul, `display: standalone`.
6. [ ] **Application > Service Workers** → status "activated and is running", scope `http://localhost:5173/`.
7. [ ] **Application > Cache Storage** → ada 3 cache: `workbox-precache-v2-...` (14 file), `transformers-cache` (5 file model), `cdn-libs` (2 file wasm).
8. [ ] **DevTools > Network > Offline** → reload page → app tetap muncul (bukan blank), fitur AI tetap jalan karena model juga sudah cached.

> **Tips deteksi:** README menyebut model dilatih dengan data sederhana. Test di **tempat terang** dengan **latar polos**. Kalau salah tebak, itu wajar (fokus penilaian Dicoding = alur kode, bukan akurasi model).

---

## LANGKAH 2 — Deploy ke Netlify

Cara termudah = **drag-drop** (tanpa perlu install CLI atau setup git).

1. Buka **https://app.netlify.com/drop** di browser (login/register dulu kalau belum — pakai email atau GitHub).
2. Buka **File Explorer**, navigate ke folder:
   ```
   d:\Kalachakra\docs\hackaton_PIDI\belajar-penerapan-ai-di-aplikasi-web\proyek_akhir\submission\root-facts
   ```
3. **Drag folder `root-facts`** langsung ke halaman Netlify Drop (area besar bertulisan "Drag and drop your site output folder here").
4. Tunggu ±20 detik. Netlify auto-generate URL: `https://<random-nama-lucu>.netlify.app`.
5. **Klik URL** → cek app buka & jalan. Kamera akan minta izin (Netlify HTTPS = kamera bisa jalan; localhost juga, tapi bukan HTTP lain).
6. (Opsional) Klik "Site settings" → rename ke sesuatu yang manusiawi: `rootfacts-nazhif` (URL final: `https://rootfacts-nazhif.netlify.app`).

**Verifikasi post-deploy:**
- [ ] Buka URL Netlify di Chrome incognito → app muncul, kamera minta izin, deteksi jalan
- [ ] DevTools > Application > Manifest OK
- [ ] DevTools > Application > Service Workers OK (status activated)
- [ ] DevTools > Network > Offline → reload → tetap muncul

---

## LANGKAH 3 — Isi STUDENT.txt

Copy URL Netlify final, paste ke:

```
d:\Kalachakra\docs\hackaton_PIDI\belajar-penerapan-ai-di-aplikasi-web\proyek_akhir\submission\root-facts\STUDENT.txt
```

Formatnya:
```
APP_URL=https://rootfacts-nazhif.netlify.app
```

> **PENTING:** kalau `STUDENT.txt` kosong / tanpa URL yang valid → K3 auto-reject 0 pt → submission GAGAL.

---

## LANGKAH 4 — Zip untuk Upload Dicoding

Dicoding minta folder proyek di-zip. **Isi zip harus flat** (file di root zip, bukan wrapped `root-facts/xxx`).

**Cara termudah — PowerShell (Windows):**

```powershell
cd d:\Kalachakra\docs\hackaton_PIDI\belajar-penerapan-ai-di-aplikasi-web\proyek_akhir
Compress-Archive -Path 'submission\root-facts\*' -DestinationPath 'RootFacts_Nazhif_Setya_Nugroho.zip' -Force
```

Verifikasi isi zip (opsional):
```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::OpenRead("$PWD\RootFacts_Nazhif_Setya_Nugroho.zip").Entries | Select-Object FullName -First 20
```

Harus muncul: `index.html`, `manifest.json`, `sw.js`, `STUDENT.txt`, `assets/...`, `model/...` — TIDAK ada folder wrapper `root-facts/` di depan.

---

## LANGKAH 5 — Upload ke Dicoding

Login Dicoding → kelas "Belajar Penerapan AI di Aplikasi Web" → menu Submission → upload `RootFacts_Nazhif_Setya_Nugroho.zip`.

**Review ±3 hari kerja.** Jangan submit berkali-kali (memperlama antrian).

---

## 🚨 Checklist Anti-Reject

Sebelum upload, pastikan:

- [ ] `STUDENT.txt` isi `APP_URL=<url_netlify_hidup>`
- [ ] URL Netlify dibuka di incognito browser lain jalan (bukan cuma di komputer sendiri)
- [ ] Di URL Netlify: DevTools > Application > Manifest tampilkan icon + nama
- [ ] Di URL Netlify: DevTools > Application > Service Worker status "activated"
- [ ] Di URL Netlify: Network throttling ke Offline → reload → app tetap muncul (bukan blank/404)
- [ ] Kamera minta izin & video muncul
- [ ] Label nama sayuran muncul di UI setelah deteksi
- [ ] Fun fact text muncul (bahasa Inggris OK, bukan hardcoded — coba 2 sayuran berbeda hasilkan teks berbeda)
- [ ] Zip flat (isi di root, bukan wrapped folder)
- [ ] JS tidak di-minify (biarkan source apa adanya)
- [ ] Tidak pakai library AI selain TensorFlow.js + Transformers.js

---

## 🎯 Nilai Ekspektasi

Dengan implementasi ini, target realistis:

| Kriteria | Level tercapai | Poin |
|---|---|---|
| K1 Deteksi Sayuran | **Basic** (streaming + model load + label tampil) | 2 |
| K2 Fun Fact AI | **Basic** (label → prompt dinamis → teks unik) | 2 |
| K3 Offline + Deploy | **Basic**+ (manifest lengkap + SW + precache + offline works — bahkan model AI ikut cached) | 2 |

**Total: 6 / 3 = 2.0 → ⭐⭐⭐ (Basic, LULUS)**

Kalau reviewer nilai K3 lebih (karena installable + offline model bonus): bisa naik ke ⭐⭐⭐+ tapi TIDAK dijanjikan (target awal cuma Basic).

**Yang tidak dikejar (Skilled/Advanced):** FPS limit dari UI, loading %, copy button binding, tone persona, backend adaptive WebGPU/WebGL, ESLint, precache model file secara eksplisit.

---

## Kalau Ada Masalah

- **Model AI tidak load / status stuck "Memuat AI...":** cek internet Netlify (SmolLM2 didownload dari huggingface.co pertama kali). Setelah cached, tidak butuh internet lagi.
- **Kamera "NotAllowedError":** browser blokir → klik icon 🔒 di address bar → Site settings → Camera → Allow.
- **Kamera "NotReadableError":** kamera dipakai app lain (Zoom, Meet, OBS). Tutup app lain, reload.
- **Prediksi selalu label yg sama / confidence rendah:** wajar untuk model TM sederhana. Lighting terang + latar polos. Fokus penilaian = kode, bukan akurasi.
- **Netlify URL 404 setelah drag-drop:** pastikan folder yang di-drag = `root-facts/` (bukan folder `submission/` yang ada wrapper `root-facts` di dalamnya). Netlify butuh `index.html` di root situs.
