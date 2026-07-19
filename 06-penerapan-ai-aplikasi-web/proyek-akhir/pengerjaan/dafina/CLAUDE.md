# CLAUDE.md — Proyek Akhir RootFacts App · Anggota: **Dafina Meira Rizkia**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol → [`/CLAUDE.md`](../../../../CLAUDE.md).

> **File ini = memory + HARD rules proyek ini.** Baca SELURUHNYA di awal tiap sesi.

---

## ⛔ SCOPE

- Proyek: submission Dicoding **"Belajar Penerapan AI di Aplikasi Web"** — **RootFacts App** (Vanilla JS: Computer Vision TF.js + Generative AI Transformers.js, PWA offline-first, deploy Netlify). Semua ML jalan **di browser**, tak ada server.
- **Nama di submission:** **Dafina Meira Rizkia**.
- **Target nilai:** **BASIC (⭐⭐⭐ lulus, 2 pt/kriteria)** — sesuai default repo (kejar minimal & lulus andal).
- Self-contained di folder ini. Aturan CLAUDE.md proyek lain TIDAK berlaku.

---

## 🚧 ANTI-PLAGIARISME — WAJIB (HARD RULE #4 repo)

Dua teman satu tim mengerjakan submission RootFacts yang SAMA:
- **Nazhif** → [`../nazhif-setya-nugroho/`](../nazhif-setya-nugroho/)
- **Fareynaldi** → [`../fareynaldi-affan/`](../fareynaldi-affan/)

Starter Dicoding **identik** untuk semua (model TM 18 sayuran fixed; HTML/CSS/`utils.js`/`ui.handler.js`/struktur folder = bawaan starter, **boleh sama**). Yang **WAJIB berbeda = kode yang KITA isi**: `detection`/`camera`/`facts` service + `app.js` + `sw.js`. **JANGAN menyalin dari folder Nazhif/Fareynaldi.**

**Titik diferensiasi Dafina (approach ke-3 — beda dari KEDUANYA). Jaga tetap beda kalau revisi:**

| Aspek | Nazhif | Fareynaldi | **Dafina (folder ini)** |
|---|---|---|---|
| Model LLM (K2) | `SmolLM2-135M-Instruct`, `text-generation`, chat, q4 | `LaMini-Flan-T5-248M`, `text2text`, q8 | **`Xenova/flan-t5-base`**, `text2text-generation`, **q8**, prompt gaya **tanya-jawab** |
| Gaya kelas | `this.x` publik | `this.x` publik | **ES2022 `#private` fields** (`#model`, `#labels`, `#busy`, `#factReady`, …) |
| Argmax deteksi | for-loop manual | `scores.indexOf(Math.max)` | **operasi tensor `tf.argMax(-1)` + `tf.max`** (di dalam `tf.tidy`) |
| Preprocess | `resizeNearestNeighbor` + `.div(127.5).sub(1)` | `resizeBilinear` + `.mul(1/127.5)` via `toInputTensor()` | **draw ke kanvas luar-layar (`drawImage` = resize) → `fromPixels` → `.div(255).mul(2).sub(1)`** via `#toTensor()` |
| Loop deteksi (app.js) | `while` + `createDelay` | rekursif `setTimeout` (`runScan`) | **`setInterval` + guard re-entrant `#busy`** (`detectLoop` per-tick) |
| Muat model | await keduanya baru enable tombol | await keduanya baru enable tombol | **app-first: TF.js dulu → tombol AKTIF; LLM dimuat di LATAR (`#factReady`)**, fun fact muncul saat siap |
| Kamera | probe getUserMedia | `buildConstraints` facingMode + `waitUntilReady` | **enumerasi device → `deviceId {exact}` bila >1 kamera** (fallback facingMode), `#awaitFirstFrame` via `loadedmetadata` |
| Sanitasi label | strip non-alfanumerik, cap 50, lowercase | NFKD + whitelist `[a-zA-Z\s]`, cap 40, lowercase | **NFKC + Unicode `\p{L}\p{N}`, cap 32, `Title Case`** (`#cleanLabel`) |
| Ekstraksi output | `.at(-1).content` (chat) | `generated_text` string | **`#extractText()`** tahan dua bentuk (string / array pesan) |
| sw.js | default cache, REVISION `v2.0.0` | `rf-*`, BUILD `ff-2026-07-16`, helper `stamp()` | **`setCacheNameDetails({prefix:'rootfacts-dmr'})`**, REV `dmr-2026-07-19`, helper `withRev`, cache `df-navigation/df-cdn/df-hf-hub/...` |
| Log prefix | `[RootFacts]` | `[RootFacts·FA]` | **`[RootFacts·DMR]`** |
| Ikon | sprout | wortel | **daun (leaf)**, aksen hijau `#15803d` (generator `scratchpad/make_icons.py`) |

> Catatan model: Qwen2.5-0.5B-Instruct sempat dipertimbangkan (paling distinctive) tapi bobot `model_q4.onnx` = **786 MB** → terlalu berat & tak andal untuk app web Basic. flan-t5-base (~250 MB q8) dipilih: kualitas fun fact memadai (dinamis & relevan), model id beda dari kedua teman, terverifikasi jalan.

---

## 🎯 YANG DIBANGUN (Basic, 2 pt/kriteria)

- **K1 Deteksi Sayuran (CV):** kamera `getUserMedia` streaming + model TF.js Teachable Machine (18 label, 224px) + label prediksi tampil otomatis. **Loop TIDAK menggerbang confidence** (selalu tampilkan prediksi teratas) — belajar dari penolakan Nazhif (threshold 70 → UI stuck).
- **K2 Fun Fact (GenAI):** label → prompt Inggris dinamis (tanya-jawab) → `flan-t5-base` text2text → fun fact unik per sayuran tampil di UI.
- **K3 Offline + Deploy:** deploy Netlify, `manifest.json` valid (ikon 192/512 any+maskable), Service Worker Workbox precache **17 file** = app shell + **ikon** + **model TF.js** → app + deteksi jalan offline. URL di `STUDENT.txt`.

**TIDAK dikejar (Skilled/Advanced):** FPS limit UI, loading %, copy binding, tone persona, backend adaptif WebGPU/WebGL, ESLint. Elemen HTML fitur itu dibiarkan ada tapi tak di-wire.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

1. AI hanya **TensorFlow.js + Transformers.js**. Jangan tambah MediaPipe/ONNX-Runtime/dll manual.
2. **Jangan ganti pre-trained model** di `model/` (TM 18 label bawaan).
3. **Jangan minify JS.**
4. **Jangan plagiat** — beda dari starter lain & beda dari folder Nazhif **dan** Fareynaldi (lihat tabel di atas).
5. Web app, bukan notebook. Struktur folder starter (`assets/js/{core,services,ui}/`) dipertahankan; boleh tambah `sw.js` di root + `assets/icons/`.
6. **URL Netlify WAJIB** di `STUDENT.txt` (kosong = reject K3).
7. **Manifest valid** (ikon + nama terdeteksi DevTools) & **Service Worker aktif** & **app buka offline**.
8. **Kamera wajib** minta izin & tampil. **Fun fact wajib dinamis** per sayuran.
9. Zip flat (file di root zip, tanpa wrapper `root-facts/`, tanpa `node_modules`, tanpa `_*test*.html` scratch).

---

## 📁 STRUKTUR & DELIVERABLE

```
dafina/
├── CLAUDE.md                 ← file ini
├── panduan/Deploy_Netlify.md ← langkah deploy + zip untuk user
├── scratchpad/make_icons.py  ← generator ikon daun (Pillow)
└── submission/root-facts/    ← app yang diedit → di-zip
    ├── index.html  manifest.json  sw.js  STUDENT.txt
    ├── assets/{css,icons,js/{core,services,ui}}
    └── model/ (metadata.json, model.json, weights.bin) — JANGAN diubah
```

**Zip final:** `RootFacts_Dafina_Meira_Rizkia.zip` = isi `submission/root-facts/` flat.

---

## 🔑 CATATAN TEKNIS

- **TF.js:** `tf@4.22.0` (CDN jsdelivr, di `<head>`). `tf.loadLayersModel('./model/model.json')`, metadata untuk labels + imageSize. Normalisasi ke [-1,1]: `x/255*2-1`.
- **Transformers.js:** `@huggingface/transformers@3.7.5` (ESM import). `pipeline('text2text-generation','Xenova/flan-t5-base',{dtype:'q8'})`. Prompt tanya-jawab, `max_new_tokens:70, temperature:0.7, top_p:0.95, do_sample:true, repetition_penalty:1.3`. Unduhan awal ~250 MB dari HF (sekali, lalu tercache Transformers.js). **Load pertama bisa 1–3 menit** di mesin nyata (WASM single-thread karena Netlify/`serve` tak set COOP/COEP) — makanya app-first: kamera jalan dulu, fun fact menyusul.
- **Workbox 7** (`workbox-sw` CDN googleapis). `setCacheNameDetails({prefix:'rootfacts-dmr'})`. Precache 17 file (app shell + 4 ikon + 3 model TF.js). Runtime: NetworkFirst (navigasi), SWR (font css), CacheFirst (font files, vendor CDN, HF model), SWR (fallback same-origin).
- **Dev server:** `npx serve@14 . -l 5190 --cors` dari `submission/root-facts`.

---

## ✅ PROGRESS LOG

- **Tahap 0 — Setup: ✅ (2026-07-19, Victus)** — folder `submission/panduan/scratchpad` disiapkan; starter Dicoding di-copy dari `artifact/template/root-facts-starter/` ke `submission/root-facts/`. Node v22.19.0.

- **Tahap 1 — K1 (Camera + TF.js): ✅ (2026-07-19)**
  - `detection.service.js`: `#private` fields, `#fetchMetadata()`, preprocessing `#toTensor()` (kanvas `drawImage` resize → `fromPixels` → `.div(255).mul(2).sub(1)`), argmax `tf.argMax(-1)`/`tf.max` di `tf.tidy`, getter `labelList`, dispose input di `finally`.
  - `camera.service.js`: `#pickConstraints()` (deviceId eksak bila >1 kamera, fallback facingMode), `#awaitFirstFrame()` (`loadedmetadata`), `isActive/isReady`.
  - `index.html`: script `tfjs@4.22.0` di `<head>`.
  - **Verifikasi (Chrome DevTools MCP, Victus):** TF.js `4.22.0` backend `webgl`; model load, 18 label; predict canvas sintetis → `{Carrot, 44%, isValid:true}`; **8× predict berturut → tensor 789→789 (0 leak)** ✅.

- **Tahap 2 — K2 (Transformers.js flan-t5-base): ✅ (2026-07-19)**
  - `facts.service.js`: import CDN `@huggingface/transformers@3.7.5`, pipeline `text2text-generation` `Xenova/flan-t5-base` dtype q8. `#cleanLabel()` (NFKC + Unicode allowlist + cap 32 + Title Case) mitigasi prompt injection. `#extractText()` tahan dua format output. Fallback string bila kosong.
  - **Verifikasi:** jalur kode diuji dengan generator tiruan format asli → sanitasi (`<script>alert(1)</script> Spin@ch` → `Ignore Previous Script Alert 1 S`), Title Case (`eggplant`→`Eggplant`), params & return shape benar. **End-to-end (harness single-instance):** model load + generate 4 sayuran → **fun fact dinamis & mostly relevan** (Carrot→"it's easy to grow a carrot.", Spinach→"The spinach plant requires less water than a carrot.", Potato→"Potatoes are a vegetable.", eggplant→meleset "cucumber"). Dinamis+relevan = **lolos Basic K2** (Dicoding toleran salah tebak). Catatan: flan-t5-**small** sebelumnya diuji → kualitas jelek (Potato→"a vegetable is a vegetable") → dinaikkan ke **base**.

- **Tahap 3 — K3 (PWA + SW Workbox): ✅ (2026-07-19)**
  - `manifest.json`: `start_url ./index.html` + `scope ./`, 4 ikon (192/512, any+maskable), field lang/dir/categories.
  - `sw.js` (BARU): `setCacheNameDetails({prefix:'rootfacts-dmr'})`, helper `withRev`, REV `dmr-2026-07-19`, precache 17 file (app shell + 4 ikon + 3 model TF.js), 6 route runtime.
  - `app.js`: `[RootFacts·DMR]`, `registerServiceWorker()`, init **app-first** (TF.js → enable → LLM di latar via `#factReady`), `detectLoop` via `setInterval`+`#busy`, regenerate fun fact hanya saat label berubah.
  - Ikon daun (Pillow, `scratchpad/make_icons.py`) di `assets/icons/` (192/512/apple-touch/favicon), hijau `#15803d` full-bleed maskable-safe. **Verifikasi visual: motif daun jelas.**
  - **Verifikasi (CDP):** manifest 200, 4 ikon, `display standalone`, scope root ✅; SW `active` scope root, `controller=true` ✅; precache `rootfacts-dmr-precache-v2-v1` = **17 file** ✅; runtime cache `df-cdn`(TF.js/lucide/transformers)/`df-google-fonts`/`df-font-files` terisi setelah reload. **OFFLINE (emulate Offline → reload) → app shell render penuh + TF.js tersedia + DETEKSI jalan (Soybean 93% dari precache)** ✅ (mendekati K3 Advanced offline-AI). SW tidak memblok fetch HF/CDN (config.json 200). Konsol 0 error (cuma warn kosmetik apple-mobile-web-app-capable). App-first: tombol scan aktif seketika (msUntilEnabled=0), header "Siap" tanpa nunggu LLM ✅.

- **Tahap 4 — Deploy + Packaging: ⏳ MENUNGGU USER**
  - Kode siap & terverifikasi lokal. `STUDENT.txt` masih kosong (`APP_URL=`).
  - **NEXT (user Dafina):** deploy Netlify Drop (akun sendiri) → isi `STUDENT.txt` `APP_URL=` → zip flat `RootFacts_Dafina_Meira_Rizkia.zip` (lihat [`panduan/Deploy_Netlify.md`](panduan/Deploy_Netlify.md)) → upload Dicoding. ⚠️ Pastikan `_*test*.html` scratch TIDAK ikut zip (sudah dihapus).
