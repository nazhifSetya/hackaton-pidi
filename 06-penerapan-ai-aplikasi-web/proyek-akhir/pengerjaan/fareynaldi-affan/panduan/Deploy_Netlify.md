# Panduan Deploy Netlify + Zip Submission — Root Facts App (Fareynaldi)

> Target: **BASIC (⭐⭐⭐ lulus)** — 2 pt per kriteria. Alur: **coba lokal → deploy Netlify → isi STUDENT.txt → zip → upload**.

---

## ✅ Status Implementasi (sudah selesai & terverifikasi via browser test)

| Kriteria | Status | Bukti (Chrome DevTools MCP, Mac M1) |
|---|---|---|
| K1 — Kamera + TF.js deteksi 18 label sayuran | ✅ Basic | `detector.predict()` return `{className, confidence}`; TF.js 4.22.0, 18 label termuat |
| K2 — Transformers.js **LaMini-Flan-T5-248M** fun fact dinamis | ✅ Basic | 5 sayuran → 5 fun fact berbeda & menyebut sayuran yang benar |
| K3 — Manifest valid + SW Workbox precache + offline | ✅ Basic (+model cached) | Precache 17 file; network Offline → reload → app + deteksi + fun fact tetap jalan |

Sisanya butuh **user**: langkah 1 (test webcam nyata), langkah 2 (deploy Netlify pakai akun sendiri), langkah 3–5 (STUDENT.txt + zip + upload).

---

## LANGKAH 1 — Coba di Browser dengan Kamera Nyata

Agent sudah verifikasi lewat automated browser (tanpa kamera fisik). Test manual dengan webcam:

```bash
cd "/Users/nazhifnugroho/Documents/Kalachakra-dev/hackaton-pidi/06-penerapan-ai-aplikasi-web/proyek-akhir/pengerjaan/fareynaldi-affan/submission/root-facts"
npx serve@14 . -l 5188 --cors
```

Buka **Chrome/Edge** di `http://localhost:5188/`.

**Checklist:**
1. [ ] Header: "Memuat model..." → "Memuat AI..." → "Siap" (unduh model T5 ~150 MB dari HuggingFace di kunjungan pertama, lalu tercache).
2. [ ] Klik tombol scan → izinkan kamera (**Allow**).
3. [ ] Video muncul; arahkan ke sayuran (atau gambar sayuran di HP).
4. [ ] Card hasil muncul: **nama sayuran** + **confidence %** + **fun fact** (Inggris, 1 kalimat, unik per sayuran).
5. [ ] **DevTools > Application > Manifest**: nama + ikon 192/512 muncul, `display: standalone`.
6. [ ] **Application > Service Workers**: "activated and running", scope `http://localhost:5188/`.
7. [ ] **Application > Cache Storage**: `workbox-precache-v2-...` (17 file), `transformers-cache`, `rf-vendor`, `rf-llm-model`.
8. [ ] **Network > Offline** → reload → app tetap muncul, deteksi + fun fact tetap jalan.

> **Tips:** model dilatih sederhana → test di tempat **terang**, latar **polos**. Salah tebak = wajar (penilaian Dicoding fokus ke alur kode, bukan akurasi).

---

## LANGKAH 2 — Deploy ke Netlify (drag-drop)

1. Buka **https://app.netlify.com/drop** (login/register — email atau GitHub, pakai **akun Fareynaldi**).
2. Finder → folder:
   `.../pengerjaan/fareynaldi-affan/submission/root-facts`
3. **Drag folder `root-facts`** ke area Netlify Drop.
4. Tunggu ±20 detik → dapat URL `https://<nama-acak>.netlify.app`.
5. Klik URL → cek app buka & jalan (HTTPS Netlify = kamera bisa jalan).
6. (Opsional) Site settings → rename mis. `rootfacts-fareynaldi`.

**Verifikasi post-deploy (incognito):** Manifest OK · Service Worker activated · Offline reload tetap muncul · kamera minta izin · label + fun fact muncul.

---

## LANGKAH 3 — Isi STUDENT.txt

File: `.../submission/root-facts/STUDENT.txt`

```
APP_URL=https://rootfacts-fareynaldi.netlify.app
```

> **PENTING:** `STUDENT.txt` kosong / tanpa URL valid → K3 auto-reject 0 pt → GAGAL.

---

## LANGKAH 4 — Zip (isi flat, tanpa wrapper)

macOS (dari folder `submission/root-facts`, biar file di root zip):

```bash
cd "/Users/nazhifnugroho/Documents/Kalachakra-dev/hackaton-pidi/06-penerapan-ai-aplikasi-web/proyek-akhir/pengerjaan/fareynaldi-affan/submission/root-facts"
zip -r -X "../../RootFacts_Fareynaldi_Affan.zip" . -x ".DS_Store" -x "*/.DS_Store"
```

Zip tersimpan di folder `pengerjaan/fareynaldi-affan/`. Isi root zip harus: `index.html`, `manifest.json`, `sw.js`, `STUDENT.txt`, `assets/...`, `model/...` — **tanpa** folder wrapper `root-facts/`.

Cek isi:
```bash
unzip -l "/Users/nazhifnugroho/Documents/Kalachakra-dev/hackaton-pidi/06-penerapan-ai-aplikasi-web/proyek-akhir/pengerjaan/fareynaldi-affan/RootFacts_Fareynaldi_Affan.zip" | head -20
```

---

## LANGKAH 5 — Upload ke Dicoding

Login Dicoding → kelas "Belajar Penerapan AI di Aplikasi Web" → Submission → upload `RootFacts_Fareynaldi_Affan.zip`. Review ±3 hari kerja; jangan submit berulang.

---

## 🚨 Checklist Anti-Reject

- [ ] `STUDENT.txt` isi `APP_URL=<url_netlify_hidup>`
- [ ] URL Netlify jalan di incognito (bukan cuma di komputer sendiri)
- [ ] Manifest tampilkan ikon + nama; SW "activated"; Offline reload tetap muncul
- [ ] Kamera minta izin & video muncul; label sayuran muncul
- [ ] Fun fact muncul & berbeda antar sayuran (bukan hardcoded)
- [ ] Zip flat; JS tidak di-minify
- [ ] AI hanya pakai TensorFlow.js + Transformers.js; model TM bawaan tidak diganti

---

## 🎯 Nilai Ekspektasi

| Kriteria | Level | Poin |
|---|---|---|
| K1 Deteksi Sayuran | Basic | 2 |
| K2 Fun Fact AI (LaMini-Flan-T5) | Basic | 2 |
| K3 Offline + Deploy | Basic (+model cached) | 2 |

**Total: 6 / 3 = 2.0 → ⭐⭐⭐ (Basic, LULUS).**

Skilled/Advanced tidak dikejar: FPS limit UI, loading %, copy binding, tone persona, backend adaptif WebGPU/WebGL, ESLint.

---

## Kalau Ada Masalah

- **Status stuck "Memuat AI...":** kunjungan pertama unduh T5 (~150 MB) dari huggingface.co; butuh internet sekali, lalu tercache.
- **Kamera NotAllowedError:** klik 🔒 di address bar → Camera → Allow.
- **Kamera NotReadableError:** kamera dipakai app lain (Zoom/Meet/OBS) → tutup, reload.
- **Prediksi label sama terus:** wajar untuk model TM sederhana; terang + latar polos.
- **Netlify 404:** pastikan yang di-drag folder `root-facts` (ada `index.html` di root situs), bukan `submission/`.
