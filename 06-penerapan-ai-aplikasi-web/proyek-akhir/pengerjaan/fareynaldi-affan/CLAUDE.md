# CLAUDE.md — Proyek Akhir RootFacts App · Anggota: **Fareynaldi Affan**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol → [`/CLAUDE.md`](../../../../CLAUDE.md).

> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi.

---

## ⛔ SCOPE

- Proyek: submission Dicoding **"Belajar Penerapan AI di Aplikasi Web"** — **RootFacts App** (Vanilla JS: Computer Vision TF.js + Generative AI Transformers.js, PWA offline-first, deploy Netlify). Semua ML jalan **di browser**, tak ada server.
- **Nama di submission:** **Fareynaldi Affan**.
- **Target nilai:** **BASIC (⭐⭐⭐ lulus, 2 pt/kriteria)** — sesuai default repo (kejar minimal).
- Self-contained di folder ini. Aturan CLAUDE.md proyek lain TIDAK berlaku.

---

## 🚧 ANTI-PLAGIARISME — WAJIB (HARD RULE #4 repo)

Teman satu tim (**Nazhif**) mengerjakan submission RootFacts yang sama di
[`../nazhif-setya-nugroho/`](../nazhif-setya-nugroho/). Starter Dicoding **identik** untuk semua
(model TM 18 sayuran fixed, HTML/CSS/UI-handler/utils sama = memang bawaan starter, boleh sama).
Yang **WAJIB berbeda = kode yang KITA isi** (service + app.js + sw.js). Instruksi Dicoding sendiri
mendukung "pendekatan/logika berbeda". **JANGAN menyamakan / menyalin dari folder Nazhif.**

**Titik differensiasi yang sudah diterapkan (jaga tetap beda kalau revisi):**

| Aspek | Nazhif | Fareynaldi (folder ini) |
|---|---|---|
| Model LLM (K2) | `SmolLM2-135M-Instruct`, pipeline `text-generation`, chat messages, dtype q4 | **`Xenova/LaMini-Flan-T5-248M`**, pipeline **`text2text-generation`**, prompt instruksi tunggal (bukan chat), dtype **q8** |
| Ekstraksi output | ambil turn assistant terakhir dari array | `generated_text` string langsung |
| Detect loop (app.js) | `while` + `createDelay` | **recursive `setTimeout` scheduler** (`runScan`/`scanTimer`) |
| Argmax (detection) | manual for-loop | `scores.indexOf(Math.max(...scores))` |
| Resize preprocess | `resizeNearestNeighbor` + `.div(127.5)` | `resizeBilinear` + `.mul(1/127.5)`, via method `toInputTensor()` |
| Model paths | konstanta modul `MODEL_URL` | field objek `this.paths.{graph,meta}` |
| sw.js | cache `pages/cdn-libs/hf-models`, REVISION `v2.0.0` | cache `rf-pages/rf-vendor/rf-llm-model/...`, BUILD `ff-2026-07-16`, helper `stamp()` |
| Log prefix | `[RootFacts]` | `[RootFacts·FA]` |
| Ikon | sprout | **wortel** (tetap tema hijau #16a34a) |
| Script TF.js di index.html | di `<head>` | di bawah body sebelum modul app.js |
| config threshold | `0` | `40` (indikator; loop tetap tak nge-gate) |

---

## 🎯 YANG DIBANGUN (Basic, 2 pt/kriteria)

- **K1 Deteksi Sayuran (CV):** kamera `getUserMedia` streaming + model TF.js Teachable Machine (18 label, 224px) + label prediksi tampil otomatis.
- **K2 Fun Fact (GenAI):** label → prompt Inggris dinamis → `LaMini-Flan-T5-248M` text2text → fun fact unik per sayuran tampil di UI.
- **K3 Offline + Deploy:** deploy Netlify, `manifest.json` valid (ikon 192/512), Service Worker Workbox precache app shell **+ model TF.js** → app + deteksi jalan offline. URL di `STUDENT.txt`.

**TIDAK dikejar (Skilled/Advanced):** FPS limit UI, loading %, copy binding, tone persona, backend adaptif WebGPU/WebGL, ESLint. HTML elemen fitur itu dibiarkan ada tapi tak di-wire.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

1. AI hanya **TensorFlow.js + Transformers.js**. Jangan tambah MediaPipe/ONNX-Runtime/dll.
2. **Jangan ganti pre-trained model** di `model/` (TM 18 label bawaan).
3. **Jangan minify JS.**
4. **Jangan plagiat** — beda dari starter lain & beda dari folder Nazhif (lihat tabel di atas).
5. Web app, bukan notebook. Struktur folder starter (`assets/js/{core,services,ui}/`) dipertahankan; boleh tambah `sw.js` di root.
6. **URL Netlify WAJIB** di `STUDENT.txt` (kosong = reject K3).
7. **Manifest valid** (ikon + nama terdeteksi DevTools) & **Service Worker aktif** & **app buka offline**.
8. **Kamera wajib** minta izin & tampil. **Fun fact wajib dinamis** per sayuran.
9. Zip flat (file di root zip, tanpa wrapper `root-facts/`, tanpa `node_modules`).

---

## 📁 STRUKTUR & DELIVERABLE

```
fareynaldi-affan/
├── CLAUDE.md                 ← file ini
├── panduan/Deploy_Netlify.md ← langkah deploy + zip untuk user
├── scratchpad/make_icons.py  ← generator ikon wortel (Pillow)
└── submission/root-facts/    ← app yang diedit → di-zip
    ├── index.html  manifest.json  sw.js  STUDENT.txt
    ├── assets/{css,icons,js/{core,services,ui}}
    └── model/ (metadata.json, model.json, weights.bin) — JANGAN diubah
```

**Zip final:** `RootFacts_Fareynaldi_Affan.zip` = isi `submission/root-facts/` flat.

---

## 🔑 CATATAN TEKNIS

- **TF.js:** `tf@4.22.0` (CDN jsdelivr, sesuai tips modul). Load `tf.loadLayersModel('./model/model.json')`, metadata untuk labels + imageSize. Normalisasi ke [-1,1].
- **Transformers.js:** `@huggingface/transformers@3.7.5` (ESM import). `pipeline('text2text-generation','Xenova/LaMini-Flan-T5-248M',{dtype:'q8'})`. Prompt: `Write one short and interesting fun fact about the vegetable ${label}. Mention ${label} in the answer.` params `max_new_tokens:90, temperature:0.5, top_p:0.9, do_sample:true, repetition_penalty:1.2`. Menyebut label dua kali bikin model kecil tetap fokus. Kunjungan pertama unduh ~150 MB dari HF, lalu tercache.
- **Workbox 7** (`workbox-sw` CDN googleapis). Precache 17 file (app shell + 4 ikon + 3 model TF.js). Runtime: NetworkFirst (navigasi), CacheFirst (font files, vendor CDN, HF model), StaleWhileRevalidate (font css, fallback same-origin).
- **Dev server (Mac):** `npx serve@14 . -l 5188 --cors` dari `submission/root-facts`.

---

## ✅ PROGRESS LOG

- **Tahap 0 — Setup: ✅ (2026-07-16, Mac M1)** — folder `submission/panduan/scratchpad` disiapkan; starter Dicoding di-copy dari `artifact/template/root-facts-starter/` ke `submission/root-facts/`. Node v24 + npm 11 di Mac.

- **Tahap 1 — K1 (Camera + TF.js): ✅ (2026-07-16)**
  - `detection.service.js`: paths via `this.paths`, `toInputTensor()` (resizeBilinear + mul(1/127.5)), argmax `indexOf(Math.max)`, dispose input+output di finally.
  - `camera.service.js`: `loadCameras()` warmup getUserMedia lalu enumerate; `buildConstraints()` facingMode + 1280×720; `waitUntilReady()` event `loadeddata`.
  - `index.html`: script `tfjs@4.22.0` ditaruh sebelum modul app.js di bawah body.
  - **Verifikasi (Chrome DevTools MCP):** TF.js 4.22.0 backend webgl; model load, 18 label; predict canvas sintetis → `{Soybean, 86%, isValid:true}`; tensor input/output ter-dispose.

- **Tahap 2 — K2 (Transformers.js LaMini-Flan-T5): ✅ (2026-07-16)**
  - `facts.service.js`: import CDN `@huggingface/transformers@3.7.5`, pipeline `text2text-generation` `Xenova/LaMini-Flan-T5-248M` dtype q8. `sanitizeLabel()` (NFKD + whitelist huruf/spasi + cap 40 char + lowercase) untuk mitigasi prompt injection. Fallback string kalau output kosong.
  - **Verifikasi:** load sukses; awalnya prompt+temp 0.8 kadang halusinasi off-topic (Spinach→spaghetti) → prompt diperbaiki jadi "Mention {label}" + temperature 0.5 → uji 5 label (carrot/spinach/potato/onion/corn) **semua menyebut sayuran benar & berbeda** = dinamis ✅.

- **Tahap 3 — K3 (PWA + SW Workbox): ✅ (2026-07-16)**
  - `manifest.json`: `start_url` `./index.html` + `scope ./`, ikon 192 (any) + 512 (any + maskable).
  - `sw.js` (BARU): helper `stamp()`, BUILD `ff-2026-07-16`, precache 17 file (app shell + 4 ikon + 3 model TF.js), 6 route runtime (NetworkFirst navigasi; CacheFirst font/vendor/HF; SWR font-css/fallback). skipWaiting + clients.claim.
  - `app.js`: bindings toggle/cameraChange, `registerServiceWorker()`, init flow camera→TF.js→T5→enable button, `runScan()` recursive setTimeout (cancel-safe via `currentLoopId` Symbol), regenerate fun fact hanya saat label berubah.
  - Ikon wortel (Pillow, `scratchpad/make_icons.py`) di `assets/icons/` (192/512/apple-touch/favicon), tema hijau #16a34a maskable-safe.
  - **Verifikasi:** manifest 3 ikon semua 200; SW activated scope root; precache `workbox-precache-v2` = **17 file**; cache `rf-llm-model`(3)/`rf-vendor`(5)/`transformers-cache`(6)/`rf-font-*`. **OFFLINE (emulate network Offline) → reload → UI render penuh + deteksi (Soybean 84%) + fun fact keduanya jalan dari cache** ✅. UI wiring `showResults` update DOM benar. Console **0 error** (cuma warn kosmetik apple-mobile-web-app-capable + info SharedArrayBuffer).

- **Tahap 4 — Deploy + Packaging: ⏳ MENUNGGU USER**
  - Kode siap & terverifikasi lokal. `STUDENT.txt` masih kosong.
  - **NEXT (user Fareynaldi):** deploy Netlify Drop (akun sendiri) → isi `STUDENT.txt` `APP_URL=` → zip flat `RootFacts_Fareynaldi_Affan.zip` (lihat [`panduan/Deploy_Netlify.md`](panduan/Deploy_Netlify.md)) → upload Dicoding.
