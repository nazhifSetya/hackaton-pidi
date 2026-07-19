# Panduan Deploy Netlify + Zip Submission — RootFacts App (Dafina Meira Rizkia)

> Target: **BASIC (⭐⭐⭐ lulus)** — 2 pt per kriteria. Alur: **coba lokal → deploy Netlify → isi STUDENT.txt → zip → upload**.

---

## ✅ Status Implementasi (sudah selesai & terverifikasi via browser test, Victus)

| Kriteria | Status | Bukti (Chrome DevTools) |
|---|---|---|
| K1 — Kamera + TF.js deteksi 18 label sayuran | ✅ Basic | TF.js 4.22.0, 18 label termuat, `predict()` return `{className, confidence}`; 8× predict → 0 memory leak |
| K2 — Transformers.js **flan-t5-base** fun fact dinamis | ✅ Basic | model load + generate 4 sayuran → fun fact **berbeda & relevan** per sayuran |
| K3 — Manifest valid + SW Workbox precache + offline | ✅ Basic (+model cached) | precache **17 file**; network Offline → reload → app + **deteksi** tetap jalan |

Sisanya butuh **kamu (Dafina)**: langkah 1 (test webcam nyata), langkah 2 (deploy Netlify akun sendiri), langkah 3–5 (STUDENT.txt + zip + upload).

---

## LANGKAH 1 — Coba di Browser dengan Kamera Nyata

```powershell
cd "d:\Kalachakra\hackaton-pidi\06-penerapan-ai-aplikasi-web\proyek-akhir\pengerjaan\dafina\submission\root-facts"
npx serve@14 . -l 5190 --cors
```

Buka **Chrome/Edge** di `http://localhost:5190/`.

**Checklist:**
1. [ ] Header: "Memuat model..." → **"Siap"** (cepat, hanya menunggu TF.js). Tombol scan langsung aktif.
2. [ ] Klik tombol scan → izinkan kamera (**Allow**). Video muncul.
3. [ ] Arahkan ke sayuran (atau gambar sayuran di HP). Card hasil muncul: **nama sayuran** + **confidence %**.
4. [ ] **Fun fact** muncul (Inggris, 1 kalimat, unik per sayuran). ⏳ **Kunjungan pertama:** model bahasa flan-t5-base (~250 MB) diunduh dari HuggingFace di latar belakang → fun fact pertama bisa butuh **1–3 menit**; setelahnya cepat & tercache. Selama itu kartu fakta menampilkan spinner "Memuat fakta menarik...".
5. [ ] **DevTools > Application > Manifest**: nama + ikon 192/512 muncul, `display: standalone`.
6. [ ] **Application > Service Workers**: "activated and running", scope `http://localhost:5190/`.
7. [ ] **Application > Cache Storage**: `rootfacts-dmr-precache-...` (17 file), `df-cdn`, `transformers-cache`.
8. [ ] **Network > Offline** → reload → app tetap muncul, deteksi tetap jalan (fakta butuh model sudah tercache).

> **Tips:** model dilatih sederhana → test di tempat **terang**, latar **polos**. Salah tebak = wajar (penilaian Dicoding fokus ke alur kode, bukan akurasi).

---

## LANGKAH 2 — Deploy ke Netlify (drag-drop)

1. Buka **https://app.netlify.com/drop** (login/register — email atau GitHub, pakai **akun Dafina**).
2. File Explorer → folder:
   `d:\Kalachakra\hackaton-pidi\06-penerapan-ai-aplikasi-web\proyek-akhir\pengerjaan\dafina\submission\root-facts`
3. **Drag folder `root-facts`** ke area Netlify Drop.
4. Tunggu ±20 detik → dapat URL `https://<nama-acak>.netlify.app`.
5. Klik URL → cek app buka & jalan (HTTPS Netlify = kamera bisa jalan). Sabar tunggu model bahasa di kunjungan pertama.
6. (Opsional) Site settings → rename mis. `rootfacts-dafina`.

**Verifikasi post-deploy (incognito):** Manifest OK · Service Worker activated · Offline reload tetap muncul · kamera minta izin · label + fun fact muncul.

---

## LANGKAH 3 — Isi STUDENT.txt

File: `...\dafina\submission\root-facts\STUDENT.txt`

```
APP_URL=https://rootfacts-dafina.netlify.app
```

> **PENTING:** `STUDENT.txt` kosong / tanpa URL valid → K3 auto-reject 0 pt → GAGAL.

---

## LANGKAH 4 — Zip (isi flat, tanpa wrapper)

PowerShell (dari dalam folder `root-facts`, biar file di root zip):

```powershell
cd "d:\Kalachakra\hackaton-pidi\06-penerapan-ai-aplikasi-web\proyek-akhir\pengerjaan\dafina\submission\root-facts"
if (Test-Path "..\..\RootFacts_Dafina_Meira_Rizkia.zip") { Remove-Item "..\..\RootFacts_Dafina_Meira_Rizkia.zip" }
Compress-Archive -Path * -DestinationPath "..\..\RootFacts_Dafina_Meira_Rizkia.zip" -Force
```

Zip tersimpan di folder `pengerjaan/dafina/`. Isi root zip harus: `index.html`, `manifest.json`, `sw.js`, `STUDENT.txt`, `assets/...`, `model/...` — **tanpa** folder wrapper `root-facts/`, **tanpa** file `_*test*.html`.

Cek isi:
```powershell
Expand-Archive -Path "d:\Kalachakra\hackaton-pidi\06-penerapan-ai-aplikasi-web\proyek-akhir\pengerjaan\dafina\RootFacts_Dafina_Meira_Rizkia.zip" -DestinationPath "$env:TEMP\cek_zip" -Force
Get-ChildItem "$env:TEMP\cek_zip" | Select-Object Name
```
Pastikan `index.html` ada di paling atas (bukan di dalam subfolder).

---

## LANGKAH 5 — Upload ke Dicoding

Login Dicoding → kelas "Belajar Penerapan AI di Aplikasi Web" → Submission → upload `RootFacts_Dafina_Meira_Rizkia.zip`. Review ±3 hari kerja; jangan submit berulang.

---

## 🚨 Checklist Anti-Reject

- [ ] `STUDENT.txt` isi `APP_URL=<url_netlify_hidup>`
- [ ] URL Netlify jalan di incognito (bukan cuma di komputer sendiri)
- [ ] Manifest tampilkan ikon + nama; SW "activated"; Offline reload tetap muncul
- [ ] Kamera minta izin & video muncul; label sayuran muncul
- [ ] Fun fact muncul & berbeda antar sayuran (bukan hardcoded)
- [ ] Zip flat; JS tidak di-minify; **tidak ada `_*test*.html`** di zip
- [ ] AI hanya pakai TensorFlow.js + Transformers.js; model TM bawaan tidak diganti

---

## 🎯 Nilai Ekspektasi

| Kriteria | Level | Poin |
|---|---|---|
| K1 Deteksi Sayuran | Basic | 2 |
| K2 Fun Fact AI (flan-t5-base) | Basic | 2 |
| K3 Offline + Deploy | Basic (+model cached) | 2 |

**Total: 6 / 3 = 2.0 → ⭐⭐⭐ (Basic, LULUS).**

Skilled/Advanced tidak dikejar: FPS limit UI, loading %, copy binding, tone persona, backend adaptif WebGPU/WebGL, ESLint.

---

## Kalau Ada Masalah

- **Fun fact lama muncul / spinner lama:** kunjungan pertama unduh flan-t5-base (~250 MB) dari huggingface.co; butuh internet sekali, lalu tercache. Kamera & label tetap jalan selama nunggu (desain app-first).
- **Kamera NotAllowedError:** klik 🔒 di address bar → Camera → Allow.
- **Kamera NotReadableError:** kamera dipakai app lain (Zoom/Meet/OBS) → tutup, reload.
- **Prediksi label sama terus:** wajar untuk model TM sederhana; terang + latar polos.
- **Netlify 404:** pastikan yang di-drag folder `root-facts` (ada `index.html` di root situs), bukan `submission/`.
