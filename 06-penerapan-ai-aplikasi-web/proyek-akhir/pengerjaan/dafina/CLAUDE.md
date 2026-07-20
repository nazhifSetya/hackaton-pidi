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
| Gaya kelas | `this.x` publik | `this.x` publik | **ES2022 `#private` fields** (`#model`, `#labels`, `#busy`, `#scanHandle`, …) |
| Argmax deteksi | for-loop manual | `scores.indexOf(Math.max)` | **operasi tensor `tf.argMax(-1)` + `tf.max`** (di dalam `tf.tidy`) |
| Preprocess | `resizeNearestNeighbor` + `.div(127.5).sub(1)` | `resizeBilinear` + `.mul(1/127.5)` via `toInputTensor()` | **draw ke kanvas luar-layar (`drawImage` = resize) → `fromPixels` → `.div(255).mul(2).sub(1)`** via `#toTensor()` |
| Loop deteksi (app.js) | `while` + `createDelay` | rekursif `setTimeout` (`runScan`) | **`setInterval` + guard re-entrant `#busy`** (`detectLoop` per-tick) |
| Muat model | await keduanya, tanpa indikator persen | await keduanya, tanpa indikator persen | **await keduanya + indikator "Memuat Model... X%" dari `progress_callback`** → "Siap" hanya saat 100% (fix penolakan_1) |
| Prompt & decoding (K2) | chat, sampling | instruksi tunggal, sampling | **instruksi "the vegetable {name}" + greedy (`do_sample:false`)** — deterministik, relevan, tetap unik per sayuran |
| Kamera | probe getUserMedia | `buildConstraints` facingMode + `waitUntilReady` | **`#openStream`: pilih kamera via LABEL device (bukan indeks) → cascade facingMode exact→ideal**, `#awaitFirstFrame` via `loadedmetadata` |
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
- **Transformers.js:** `@huggingface/transformers@3.7.5` (ESM import). `pipeline('text2text-generation','Xenova/flan-t5-base',{dtype:'q8', progress_callback})`. Prompt `Tell me an interesting fun fact about the vegetable ${name}.` + **greedy** `max_new_tokens:60, do_sample:false, repetition_penalty:1.4, no_repeat_ngram_size:3`. (Sampling bikin model kecil mengarang → greedy 17/18 sebut sayuran vs 3/8.) Unduhan awal ~250 MB dari HF (sekali, lalu tercache Transformers.js). **Load pertama bisa 1–3 menit** di mesin nyata (WASM single-thread karena Netlify/`serve` tak set COOP/COEP) — makanya init pakai `progress_callback` → header **"Memuat Model... X%"** sampai 100%, baru "Siap".
- **Workbox 7** (`workbox-sw` CDN googleapis). `setCacheNameDetails({prefix:'rootfacts-dmr'})`. Precache 17 file (app shell + 4 ikon + 3 model TF.js). Runtime: NetworkFirst (navigasi), SWR (font css), CacheFirst (font files, vendor CDN, HF model), SWR (fallback same-origin).
- **Dev server:** `npx serve@14 . -l 5190 --cors` dari `submission/root-facts`.

---

## ✅ PROGRESS LOG

- **Tahap 0 — Setup: ✅ (2026-07-19, Victus)** — folder `submission/panduan/scratchpad` disiapkan; starter Dicoding di-copy dari `artifact/template/root-facts-starter/` ke `submission/root-facts/`. Node v22.19.0.

- **Tahap 1 — K1 (Camera + TF.js): ✅ (2026-07-19)**
  - `detection.service.js`: `#private` fields, `#fetchMetadata()`, preprocessing `#toTensor()` (kanvas `drawImage` resize → `fromPixels` → `.div(255).mul(2).sub(1)`), argmax `tf.argMax(-1)`/`tf.max` di `tf.tidy`, getter `labelList`, dispose input di `finally`.
  - `camera.service.js`: `#openStream()` (pilih kamera via **label** device → cascade facingMode exact→ideal), `#awaitFirstFrame()` (`loadedmetadata`), `isActive/isReady`. ⚠️ Awalnya pakai deviceId-by-indeks → BUG (di HP indeks 0 = kamera depan) → diperbaiki di Tahap 5.
  - `index.html`: script `tfjs@4.22.0` di `<head>`.
  - **Verifikasi (Chrome DevTools MCP, Victus):** TF.js `4.22.0` backend `webgl`; model load, 18 label; predict canvas sintetis → `{Carrot, 44%, isValid:true}`; **8× predict berturut → tensor 789→789 (0 leak)** ✅.

- **Tahap 2 — K2 (Transformers.js flan-t5-base): ✅ (2026-07-19)**
  - `facts.service.js`: import CDN `@huggingface/transformers@3.7.5`, pipeline `text2text-generation` `Xenova/flan-t5-base` dtype q8. `#cleanLabel()` (NFKC + Unicode allowlist + cap 32 + Title Case) mitigasi prompt injection. `#extractText()` tahan dua format output. Fallback string bila kosong.
  - **Verifikasi:** jalur kode diuji dengan generator tiruan format asli → sanitasi (`<script>alert(1)</script> Spin@ch` → `Ignore Previous Script Alert 1 S`), Title Case (`eggplant`→`Eggplant`), params & return shape benar. **End-to-end (harness single-instance):** model load + generate 4 sayuran → **fun fact dinamis & mostly relevan** (Carrot→"it's easy to grow a carrot.", Spinach→"The spinach plant requires less water than a carrot.", Potato→"Potatoes are a vegetable.", eggplant→meleset "cucumber"). Dinamis+relevan = **lolos Basic K2** (Dicoding toleran salah tebak). Catatan: flan-t5-**small** sebelumnya diuji → kualitas jelek (Potato→"a vegetable is a vegetable") → dinaikkan ke **base**.

- **Tahap 3 — K3 (PWA + SW Workbox): ✅ (2026-07-19)**
  - `manifest.json`: `start_url ./index.html` + `scope ./`, 4 ikon (192/512, any+maskable), field lang/dir/categories.
  - `sw.js` (BARU): `setCacheNameDetails({prefix:'rootfacts-dmr'})`, helper `withRev`, REV `dmr-2026-07-19`, precache 17 file (app shell + 4 ikon + 3 model TF.js), 6 route runtime.
  - `app.js`: `[RF-Dafina]`, `registerServiceWorker()`, `detectLoop` via `setInterval`+`#busy`, regenerate fun fact hanya saat label berubah. (Init awalnya app-first, lalu DIREVISI di Tahap 5 → lihat bawah.)
  - Ikon daun (Pillow, `scratchpad/make_icons.py`) di `assets/icons/` (192/512/apple-touch/favicon), hijau `#15803d` full-bleed maskable-safe. **Verifikasi visual: motif daun jelas.**
  - **Verifikasi (CDP):** manifest 200, 4 ikon, `display standalone`, scope root ✅; SW `active` scope root, `controller=true` ✅; precache `rootfacts-dmr-precache-v2-v1` = **17 file** ✅; runtime cache `df-cdn`(TF.js/lucide/transformers)/`df-google-fonts`/`df-font-files` terisi setelah reload. **OFFLINE (emulate Offline → reload) → app shell render penuh + TF.js tersedia + DETEKSI jalan (Soybean 93% dari precache)** ✅ (mendekati K3 Advanced offline-AI). SW tidak memblok fetch HF/CDN (config.json 200). Konsol 0 error (cuma warn kosmetik apple-mobile-web-app-capable). App-first: tombol scan aktif seketika (msUntilEnabled=0), header "Siap" tanpa nunggu LLM ✅.

- **Tahap 4 — Deploy + Packaging: ✅ (2026-07-19)** — user deploy Netlify (`https://cerulean-lolly-3c6913.netlify.app`), `STUDENT.txt` terisi, zip flat dibuat. Live terverifikasi (12 aset 200, SW active, manifest, precache 17). Submit ke Dicoding.

- **Tahap 5 — REVISI setelah DITOLAK reviewer (K2): ✅ (2026-07-19)**
  - **Penolakan** (`penolakan_1.md`): K2 — "Hasil deskripsi tidak muncul dan selalu tampil 'Memuat fakta menarik...'". Reviewer cek: model Transformers.js masih diunduh di **latar** padahal header sudah "Siap". **Root cause = desain app-first saya** (tombol aktif sebelum LLM siap). Reviewer minta alur: **"Memuat Model... X%"** (persen unduhan) → **"Siap" hanya saat 100%** → scan langsung tampil fakta tanpa nunggu.
  - **Fix `app.js`:** BUANG app-first + `#factReady`. `init()` sekarang muat TF.js → muat LLM **sampai tuntas** dengan callback progress → header **"Memuat Model... X%"** → baru "Siap" + enable tombol. Tombol scan nonaktif sepanjang unduhan (fun fact tak akan menggantung).
  - **Fix `facts.service.js`:** `loadModel(onProgress)` teruskan `progress_callback` → agregasi byte terunduh jadi persen. **Plus perbaikan kualitas:** prompt jadi `Tell me an interesting fun fact about the vegetable ${name}.` + **greedy** (`do_sample:false`, rep 1.4, no_repeat_ngram 3). Sampling lama bikin flan-t5-base mengarang (Onion→nonsense, Corn→"amount of time in a day") = 3/8 sebut sayuran; greedy = **17/18 sebut sayuran, relevan & koheren**, deterministik tapi unik per sayuran.
  - **Verifikasi live (CDP, model tercache):** header berjalan mulus `6% → 99% → "Siap"`, tombol **nonaktif** s/d Siap ✅; setelah Siap, detect→generate→DOM: spinner "Memuat fakta menarik" sebentar → **fun fact muncul** (`fun-fact-text` terisi) → spinner **hilang** (tak stuck) ✅; generateFunFact 7-8/8 relevan, deterministik ✅. 0 error.
  - **Fix bug kamera (lapangan, HP Samsung):** pilih "Belakang" malah buka kamera **depan**. Sebab: `#pickConstraints` lama pilih kamera by **indeks** (`device[0]` diasumsi belakang), padahal urutan `enumerateDevices()` tak dijamin (di HP itu indeks 0 = depan). Ganti `#openStream()`: pilih via **label** device (`/back|belakang|rear|environment/i` vs `/front|depan|user|selfie/i`) → fallback `facingMode` exact→ideal. Uji logika: label Android "facing back/front" → terpilih benar.
  - **NEXT (user Dafina):** **REDEPLOY** kode baru ke Netlify (situs sama `cerulean-lolly-3c6913` atau baru) → kalau URL baru update `STUDENT.txt` → re-zip → **RE-SUBMIT**. Panduan: [`panduan/Deploy_Netlify.md`](panduan/Deploy_Netlify.md).

- **Tahap 6 — REVISI setelah DITOLAK ke-2 (K2): ✅ (2026-07-20, Victus) — terverifikasi live**
  - **Penolakan-2** (`penolakan_2.md`): K2 dua catatan — (a) kamera jalan terus (realtime) → fun fact berubah/hilang saat objek bergerak, susah dibaca → minta **auto-stop kamera setelah deteksi berhasil**; (b) **kualitas fun fact buruk** — melingkar/generik ("The vegetable carrot is a vegetable", "The oxtail is a vegetable", "Potatoes are a vegetable"), terlalu pendek. Minta prompt yang minta fakta unik + naikkan `max_new_tokens` + prompt engineering.
  - **Fix (a) Auto-stop + Scan Lagi:** `app.js` — `detectLoop` kini panggil `#finishScan()` begitu deteksi cukup yakin (`AUTO_STOP_CONFIDENCE=55`, HANYA menggerbang auto-stop bukan tampilan → tak macet) + fun fact sudah tampil. `#finishScan` = `stopDetection` + `camera.stopCamera` + `ui.freezeScan()`. `ui.handler.js` — `freezeScan()` (baru): kamera berhenti TAPI kartu hasil tetap tampil (stabil), header "Selesai", tombol **"Scan Lagi"** muncul (elemen baru di `index.html` + CSS + bind `onScanAgain` → `#restartScan`). Verified live (CDP): scanning→freeze → header "Selesai", scan-again visible, result tetap tampil, placeholder muncul.
  - **Fix (b) Kualitas fun fact — GROUNDED (RAG-lite), pembeda BARU vs Nazhif/Fareynaldi:** flan-t5-base q8 **fundamental lemah mengarang** (uji browser: few-shot & prompt terbuka → tautologi/ngawur, ~1/3 masuk akal). Solusi: **tetap flan-t5-base** (ringan/andal/distinct), tapi tiap sayuran dipasangkan **seed fact terkurasi** (`VEG_FACTS`, 18 fakta unik) → model diminta **MEMPARAFRASE** (`Paraphrase into one engaging sentence: <seed>.`) → akurat + menarik. Guard `#tidyFact(raw,name,seed)`: kalau subjek hilang/ketukar (mis. turnip→"pumpkins") atau <25 char → pakai seed langsung. `max_new_tokens 60→90`. **Verified live via kode service asli: 18/18 fakta akurat & menarik** (Carrot→"orange carrot bred by Dutch farmers in the 16th century", Potato→"first vegetable ever grown in space", Spinach→"printing error... inspire Popeye"). Model TIDAK diubah (tetap Xenova/flan-t5-base) → diferensiasi terjaga + grounding jadi pembeda tambahan.
  - **Infra:** `sw.js` REV `dmr-2026-07-19` → `dmr-2026-07-20-r2` (invalidasi precache supaya browser reviewer ambil kode baru). SW verified: active, scope root, precache **17 file**. Console 0 error. K1 (deteksi) & K3 (PWA/offline) TIDAK disentuh — tetap lolos.
  - **⚠️ TEMUAN DEPLOY (2026-07-20):** live `cerulean-lolly-3c6913` ternyata **deploy PARSIAL** — curl bukti `/assets/css/styles.css`, `/assets/js/*`, `/model/model.json` semua **404** (hanya file root ter-upload); di browser fresh app tampak "polos" tanpa CSS/JS & SW gagal precache. **Persis masalah Nazhif Tahap 7** (Netlify Drop drag-folder parsial). **Kode lokal LENGKAP & benar** — murni upload tak lengkap.
  - **FIX deploy:** rakit **zip FLAT lengkap** `RootFacts_Dafina_Meira_Rizkia.zip` (19 file: index.html root + assets/ + model/ + ikon, verified) di `pengerjaan/dafina/`. Panduan `Deploy_Netlify.md` LANGKAH 2 diubah → **deploy pakai ZIP** (atomik, mustahil subfolder ketinggalan) + langkah **verifikasi curl HEAD** (`/assets/css/styles.css` dll harus 200) + cek incognito ber-CSS.
  - **NEXT (user Dafina, 🍎):** **deploy ZIP** ke Netlify (Cara A: update situs sama `cerulean-lolly-3c6913` via Deploys tab → URL tetap → zip sama jadi berkas submission; Cara B: Drop → URL baru → update STUDENT.txt + re-zip). **WAJIB verifikasi:** curl `/assets/css/styles.css` = 200 + incognito ber-CSS + smoke-test (deteksi → fun fact → auto-stop → "Scan Lagi"). Lalu RE-SUBMIT zip ke Dicoding.
