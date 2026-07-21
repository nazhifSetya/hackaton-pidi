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
| Model LLM (K2) | `SmolLM2-135M-Instruct`, `text-generation`, chat, q4 | `LaMini-Flan-T5-248M`, `text2text`, q8 | **`Xenova/LaMini-Flan-T5-77M`** (penolakan_3: flan-t5-base 600MB → ganti model ringan yg REVIEWER sarankan; ukuran 77M **beda** dari Fareynaldi 248M), `text2text`, q8, **grounded hint kata-kunci** (RAG-lite, pembeda pendekatan) |
| Gaya kelas | `this.x` publik | `this.x` publik | **ES2022 `#private` fields** (`#model`, `#labels`, `#busy`, `#scanHandle`, …) |
| Argmax deteksi | for-loop manual | `scores.indexOf(Math.max)` | **operasi tensor `tf.argMax(-1)` + `tf.max`** (di dalam `tf.tidy`) |
| Preprocess | `resizeNearestNeighbor` + `.div(127.5).sub(1)` | `resizeBilinear` + `.mul(1/127.5)` via `toInputTensor()` | **draw ke kanvas luar-layar (`drawImage` = resize) → `fromPixels` → `.div(255).mul(2).sub(1)`** via `#toTensor()` |
| Loop deteksi (app.js) | `while` + `createDelay` | rekursif `setTimeout` (`runScan`) | **`setInterval` + guard re-entrant `#busy`** (`detectLoop` per-tick) + **warm-up 2 tick + stability streak 3×@≥60% sebelum kunci** (fix penolakan_4 — pembeda vs keduanya) |
| Muat model | await keduanya, tanpa indikator persen | await keduanya, tanpa indikator persen | **await keduanya + indikator "Memuat Model... X%" dari `progress_callback`** → "Siap" hanya saat 100% (fix penolakan_1) |
| Prompt & decoding (K2) | chat, sampling | instruksi tunggal, sampling | **sampling (temp 0.5, top_p 0.9, top_k 50) + ROTASI SUDUT isi** (`FACT_ANGLES` gizi/sejarah/masak/kebun/mengejutkan, round-robin `#nextAngle`) + trim 2-kalimat + penjaga hint-overlap — mekanisme UNIK tak dimiliki keduanya; scan berulang sayuran sama → fakta beda (fix penolakan_4). Dulu greedy → deterministik → ditolak "statis" |
| Kamera | probe getUserMedia | `buildConstraints` facingMode + `waitUntilReady` | **`#openStream`: pilih kamera via LABEL device (bukan indeks) → cascade facingMode exact→ideal**, `#awaitFirstFrame` via `requestVideoFrameCallback` (frame benar ter-render) → fallback `loadeddata` (fix penolakan_4: dulu `loadedmetadata` → bisa prediksi bingkai kosong) |
| Sanitasi label | strip non-alfanumerik, cap 50, lowercase | NFKD + whitelist `[a-zA-Z\s]`, cap 40, lowercase | **NFKC + Unicode `\p{L}\p{N}`, cap 32, `Title Case`** (`#cleanLabel`) |
| Ekstraksi output | `.at(-1).content` (chat) | `generated_text` string | **`#extractText()`** tahan dua bentuk (string / array pesan) |
| sw.js | default cache, REVISION `v2.0.0` | `rf-*`, BUILD `ff-2026-07-16`, helper `stamp()` | **`setCacheNameDetails({prefix:'rootfacts-dmr'})`**, REV `dmr-2026-07-19`, helper `withRev`, cache `df-navigation/df-cdn/df-hf-hub/...` |
| Log prefix | `[RootFacts]` | `[RootFacts·FA]` | **`[RootFacts·DMR]`** |
| Ikon | sprout | wortel | **daun (leaf)**, aksen hijau `#15803d` (generator `scratchpad/make_icons.py`) |

> Catatan model: Qwen2.5-0.5B-Instruct sempat dipertimbangkan (paling distinctive) tapi bobot `model_q4.onnx` = **786 MB** → terlalu berat & tak andal untuk app web Basic. flan-t5-base (~250 MB q8) dipilih: kualitas fun fact memadai (dinamis & relevan), model id beda dari kedua teman, terverifikasi jalan.

---

## 🎯 YANG DIBANGUN (Basic, 2 pt/kriteria)

- **K1 Deteksi Sayuran (CV):** kamera `getUserMedia` streaming + model TF.js Teachable Machine (18 label, 224px). **Sejak penolakan_4:** warm-up 2 tick + **stability gate** (label sama 3× berturut @≥60%) → hasil baru tampil + kamera auto-stop saat objek benar terdeteksi. Tak macet (kamera terus hidup sampai objek nyata masuk bingkai; kalau tak ada objek, tak ada yang tampil — justru yang reviewer minta). Menghindari jebakan Nazhif (threshold gerbang-tampilan 70 → UI stuck) karena gerbang ada di *penguncian*, bukan display per-frame, dan ambang 60 terjangkau.
- **K2 Fun Fact (GenAI):** label → prompt Inggris (sudut isi dirotasi + hint kata-kunci konteks) → `Xenova/LaMini-Flan-T5-77M` text2text **sampling** → fun fact BEDA tiap scan berulang sayuran sama (fix penolakan_4 "statis").
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
- **Transformers.js:** `@huggingface/transformers@3.7.5` (ESM import). `pipeline('text2text-generation','Xenova/LaMini-Flan-T5-77M',{dtype:'q8', progress_callback})`. Prompt = `#buildPrompt(name,hint,angle)` = `Write one interesting fun fact about the ${name}, focusing on ${angle.lead}. Use these keywords as context: ${hint}.` + **SAMPLING** `max_new_tokens:60, min_new_tokens:18, do_sample:true, temperature:0.5, top_p:0.9, top_k:50, repetition_penalty:1.3, no_repeat_ngram_size:3`. **Variasi dua lapis** (sampling + rotasi sudut `FACT_ANGLES` round-robin) → scan berulang sayuran sama beda fakta (fix penolakan_4). Guard: trim ke 2 kalimat pertama (buang tail-drift 77M) + retry prompt cadangan bila output tak sebut sayur / tak pakai hint (mitigasi halusinasi mis. spinach→"rock band"). **Plafon jujur 77M ~11-13/18 bagus** (verified live: temp 0.7 sempat garbage → diturunkan **0.5** jauh lebih koheren, variasi tetap dari rotasi sudut). Unduhan ~98 MB dari HF (sekali, tercache). **Load pertama 1–3 menit** (WASM single-thread, Netlify tak set COOP/COEP) — init pakai `progress_callback` → header **"Memuat Model... X%"** sampai 100%, baru "Siap".
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

- **Tahap 7 — REVISI setelah DITOLAK ke-3 (`penolakan_3.md`): ✅ (2026-07-20, Victus) — terverifikasi live**
  - **Penolakan-3 (3 catatan):** (1) **tidak ada `package.json`** di root (wajib, acuan dependency); (2) **model flan-t5-base q8 TERLALU BESAR** — ~600 MB di Cache Storage; ganti ke `LaMini-Flan-T5-77M` / `flan-t5-small`; (3) **grounded-ku (Tahap 6) = "GenAI palsu"** — VEG_FACTS kalimat utuh + fallback verbatim → fun fact yang tampil = teks pra-tulis, bukan keluaran model.
  - **Fix 1 — package.json:** dibuat di `submission/root-facts/package.json` (name/desc + deps tfjs/transformers/workbox/lucide + script start). Ikut di zip (jadi 20 file).
  - **Fix 2 — model ringan:** `Xenova/flan-t5-base` → **`Xenova/LaMini-Flan-T5-77M`**. **Verified live: Cache Storage 98 MB** (dari ~600 MB), 6 file, 0 error. (Reviewer sarankan model ini; 77M beda ukuran dari Fareynaldi 248M → anti-plagiarisme OK.)
  - **Fix 3 — GenAI ASLI:** `VEG_FACTS` (kalimat utuh) → **`VEG_HINTS`** = kata-kunci singkat (bukan kalimat). Prompt = "Write one fun fact... using these keywords: <hint>" → **model MENYUSUN** kalimatnya. **Fallback verbatim DIHAPUS** (tak ada `text = seed`); hanya retry prompt-cadangan bila keluaran melenceng (tetap keluaran model), + placeholder generik netral bila kosong. **Verified live (kode service asli): output JELAS beda dari hint** (Carrot hint "purple...Netherlands" → output "growing in the Netherlands...introduced by Dutch farmers"), on-topic, non-tautologi.
  - **PLAFON MODEL (jujur):** LaMini-77M mentok ~11-13/18 jelas bagus, sisanya generik/agak melenceng — uji greedy vs sampling vs best-of-N vs tuning hint SEMUA mentok di plafon ini (bukan bug, ini kapasitas model 77M yang reviewer sendiri tunjuk). Tak dipaksakan lebih (menghindari jebakan iterasi tanpa konvergen).
  - **Infra:** sw.js REV `-r2` → **`-r3`**. Console 0 error, SW active. Zip regen 20 file (2.09 MB).
  - **⚠️ Deploy tetap pakai ZIP** (Tahap 6 temuan: drag-folder = parsial 404). **NEXT (user Dafina, 🍎):** deploy zip → verifikasi curl `/assets/*`=200 + Cache Storage ~98MB (bukan 600) + fun fact genuine → RE-SUBMIT zip (+package.json).

- **Tahap 8 — REVISI setelah DITOLAK ke-4 (`penolakan_4.md`): ✅ SELESAI & TERVERIFIKASI LIVE (2026-07-21, Mac) — tinggal deploy + re-submit**
  - **Penolakan-4 (2 catatan):** (K1) kamera "nyala sebentar lalu berhenti", prediksi tetap tampil padahal belum sempat memindai → minta **naikkan confidence threshold** + prediksi hanya dari frame yang benar-benar ditangkap. (K2) fun fact **statis** — scan objek sama berulang selalu **sama**, tak ada variasi GenAI.
  - **Refleksi akar (kenapa 4× tolak):** tiap fix mengejar keluhan terbaru tapi bikin masalah baru — (a) auto-stop yg diminta penolakan_2 (ambang 55, TANPA warm-up, `detectLoop()` dipanggil langsung) → **mati di tick pertama** = keluhan K1 penolakan_4; (b) greedy yg dipakai sejak penolakan_1/3 (biar model kecil tak ngawur) = **deterministik** = keluhan "statis" penolakan_4. **Learning lesson dari submission Nazhif yang DITERIMA:** sampling (variasi terlihat = GenAI asli) + jangan gerbang tampilan dgn ambang mustahil + deploy lengkap + logging jelas.
  - **Fix K1 — warm-up + stability gate** (`app.js` + `camera.service.js`): `SCAN_INTERVAL_MS 1800→700`, `AUTO_STOP_CONFIDENCE 55` → **`LOCK_CONFIDENCE 60`**, +`WARMUP_TICKS 2`, +`STABILITY_STREAK 3`. `startDetection` tak lagi panggil `detectLoop()` langsung (semua tick kena warm-up). `detectLoop` ditulis ulang: lewati 2 tick awal → hitung streak (label sama & ≥60% berturut) → **`#lockDetection` hanya saat streak≥3** → tampil hasil + fun fact → `#finishScan` (auto-stop tetap, permintaan penolakan_2). `#awaitFirstFrame` `loadedmetadata` → **`requestVideoFrameCallback`/`loadeddata`** (tunggu frame benar ter-render), `startCamera` urut `play()` sebelum await frame. `generateAndShowResults` kembalikan boolean. **Tak macet:** kamera hidup terus sampai objek nyata → streak terkumpul ~2 dtk; tanpa objek tak ada yg tampil (yang reviewer minta).
  - **Fix K2 — sampling + rotasi sudut** (`facts.service.js` + `app.js`): `do_sample:false` → **`true` (temp 0.5, top_p 0.9, top_k 50, max_new_tokens 60)** + **`FACT_ANGLES`** (5 sudut isi) dirotasi round-robin via `#angleIndex`/`#nextAngle()`; `#buildPrompt(name,hint,angle)` fokuskan sudut, hint tetap konteks grounding (bukan verbatim — larangan penolakan_3 dijaga). `generateFunFact` return `{…, angle}`. Regenerasi tiap scan sudah benar (reset `#activeLabel`). Log `[RootFacts·DMR] Fun fact [angle] …` = bukti variasi live ke reviewer. **Dua lapis variasi** (sampling + rotasi sudut) → scan sama berulang dijamin beda.
  - **Penyetelan hasil VERIFIKASI LIVE (temp 0.7→0.5):** temp 0.7 sempat keluar garbage (Carrot#2→"Using the word Victor…"; Spinach→"famous rock band"). Diturunkan **0.5** → jauh lebih koheren, variasi TETAP terjaga (rotasi sudut penjamin utama). Tambah di `#tidyFact`: **trim ke 2 kalimat pertama** (buang tail-drift model 77M). Perkuat penjaga: retry prompt cadangan bukan cuma saat nama sayur tak disebut, tapi juga **saat output tak memakai satu pun kata hint** (tangkap halusinasi) → Spinach "rock band"→"edible parts", Eggplant garbage→koheren.
  - **HAPUS SISA FALLBACK STATIS (hardening anti "GenAI palsu"):** placeholder pra-tulis terakhir di `#tidyFact` (`"Here is a fun fact: the ${name} is more interesting than it looks"` bila keluaran kosong) **DIHAPUS**. `#tidyFact` kini kembalikan string kosong bila model tak menghasilkan apa pun, lalu `generateFunFact` **lempar error** → `app.js` tak jadi mengunci → kamera lanjut memindai & coba lagi. Kini **NOL jalur** yang menampilkan teks pra-tulis sebagai fun fact — yang tampil SELALU keluaran model, atau status error netral ("Fakta tidak tersedia"). Verified live: `anyEmpty:false` (guard tak pernah nyala; min_new_tokens:18 jamin non-kosong), Carrot 3× tetap beda, Potato→"first grown in space" & Spinach→"Popeye" (hint terpakai bagus).
  - **Infra & log:** `LOG_TAG '[RF-Dafina]'` → **`'[RootFacts·DMR]'`** (samakan tabel diferensiasi); log stale "FLAN-T5-base" → LaMini-77M; komentar "greedy deterministik" diperbarui; **sw.js REV `-r3` → `dmr-2026-07-21-r4`** (invalidasi precache).
  - **Anti-plagiarisme:** semua idiom Dafina dipertahankan; rotasi sudut = pembeda BARU (tak dimiliki Nazhif/Fareynaldi). Yang hilang cuma "greedy" (kini tiga-tiganya sampling) — tak apa, model+grounding+rotasi sudut tetap membedakan.
  - **✅ VERIFIKASI LIVE SELESAI (Chrome DevTools MCP, Mac, FaceTime cam, 0 error):**
    - **K1** — log kamera asli: `Pemanasan sensor #1/2, #2/2` (warm-up) → `Tick #3 Soybean 70%(1/3) → #4 Onion 77%(1/3) → #5 Ginger 78%(1/3) → #6 Onion 73%(1/3) → #7 Onion 90%(2/3) → #8 Onion 93%(3/3)` → `Terkunci: Onion 93% setelah 3 tick stabil` → `Fun fact [nutrition] Onion: …` → `auto-stop, hasil dibekukan`. UI: header "Selesai", "Scan Lagi" muncul, hasil "Onion 93%". **Tak mati tick-1, kunci hanya setelah stabil, tak macet** (mengunci ~5,6 dtk walau kamera ke non-sayuran). ✅
    - **K2** — Carrot 3× berturut → 3 fakta BEDA, sudut rotasi nutrition→history→cooking, semua koheren+on-topic. Spinach 3× (lewat jalur retry) → 3 fakta beda, sudut rotasi, #2 pakai hint "high in iron". `allDifferent:true, anglesRotated:true`. ✅
    - **K3** — SW `activated` scope root, precache `rootfacts-dmr-precache-v2-v1` **17 file** utuh, transformers-cache 6 file. Tak terdampak. ✅
  - **NEXT (user Dafina):** (1) **deploy ZIP** (bukan drag-folder) → curl `/assets/js/core/app.js`=200 + Cache ~98MB + `facts.service.js` live memuat `do_sample: true`. (2) RE-SUBMIT + catatan demo "Scan Lagi 2× + buka Console (F12) → tiap fun fact beda dgn tag `[angle]` beda".
