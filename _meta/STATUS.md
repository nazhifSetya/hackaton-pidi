# 📊 STATUS.md — Dashboard Lintas Device (Hackaton PIDI 2026)

> **Sumber kebenaran status semua proyek.** Baca ini tiap **awal sesi** (setelah `git pull`), update tiap **akhir sesi** (sebelum `git push`). Protokol lengkap: [`/CLAUDE.md`](../CLAUDE.md).

**Terakhir di-update:** `2026-07-20` · **oleh device:** `Victus (Windows)` · **oleh:** 07 SantapLens (Dafina) — **DIBUAT dari nol & terverifikasi live tuntas.** App Flutter pengenal makanan (AIY Food V1 + LiteRT `flutter_litert`, Basic ⭐⭐⭐). Build debug+release LOLOS di Flutter 3.44.6 (error JVM `tflite_flutter` tak muncul), inferensi on-device benar ("Satay" 99.6%), K1/K2/K3 verified live emulator. Sengaja dibedakan dari Nazhif & Fareynaldi (review 3-agent: vs Nazhif LOW, vs Fareynaldi MEDIUM→fix→LOW). Zip `santap_lens_Dafina.zip` (19.75 MB) siap upload. · _(sebelumnya: 02 BFGAI Dafina — DITOLAK (K1+K2) → REVISI notebook siap; Dafina Run All Pipeline di Colab → verifikasi visual → re-zip → resubmit.)_

---

<!-- HANDOFF:START -->
## 🎯 FOKUS SAAT INI / HANDOFF

> Isi ulang bagian ini tiap akhir sesi: apa yang barusan dikerjakan, di device apa, dan apa langkah berikutnya untuk device yang lanjut. Ini yang pertama dibaca device berikutnya.

- **Device terakhir aktif:** Victus (Windows) — **06 RootFacts (Dafina): DITOLAK reviewer (K2) → DIPERBAIKI & re-verified** (2026-07-19). Penolakan `penolakan_1.md`: fun fact tak muncul, stuck "Memuat fakta menarik" karena model Transformers.js diunduh di **latar** (desain app-first saya) padahal header sudah "Siap". Fix persis saran reviewer: init muat LLM **sampai tuntas** + header **"Memuat Model... X%"** (via `progress_callback`) → "Siap" hanya saat 100% → tombol scan nonaktif s/d siap → scan langsung tampil fakta. Plus perbaikan kualitas: prompt `Tell me an interesting fun fact about the vegetable {name}` + **greedy** (sampling bikin flan-t5-base ngawur 3/8 → greedy 17/18 sebut sayuran). Verified CDP: header 6%→99%→Siap (tombol nonaktif s/d Siap), scan→fun fact muncul (spinner hilang, tak stuck), 7-8/8 relevan, 0 error. Zip regen. **SISA (user Dafina, 🍎): REDEPLOY kode baru ke Netlify → (kalau URL baru, update STUDENT.txt) → re-zip → RE-SUBMIT.** Sebelumnya device ini: **07 Food Scan App (Fareynaldi): DITOLAK reviewer → DIPERBAIKI & re-verified** (2026-07-19). Penolakan BUKAN karena fitur salah: di env reviewer (Flutter terbaru) **build GAGAL** karena plugin `tflite_flutter` usang bentrok JVM (`compileDebugJavaWithJavac` 1.8 vs `compileDebugKotlin` 21) → K1/K2/K3 auto "Perlu diperbaiki". Fix **persis saran reviewer**: (1) `flutter upgrade` 3.35.5 → **3.44.6** (Dart **3.12.2**); (2) `pubspec` `sdk ^3.12.2` + `tflite_flutter ^0.11.0` → **`flutter_litert ^3.5.1`** (fork API source-compatible, cuma 1 baris import di `tflite_food_detector.dart`); README disesuaikan. **Verified di Victus:** `flutter analyze` 0 isu → `flutter build apk --debug` **LOLOS (exit 0)** di 3.44.6 (error JVM lenyap) → integration test emulator API 36.1 (`warmUp`+`analyze` → `LITERT_OK "Waffle"`, All tests passed) = `flutter_litert` load model AIY + inferensi jalan di runtime Android. Zip regen via bsdtar (forward-slash, cruft dibuang) → **`food_scan_app_Fareynaldi.zip` = 18.83 MB** (git-tracked, isi terverifikasi). SDK Flutter di `D:\flutter` (bukan di PATH). **SISA: user tinggal RE-SUBMIT zip ke Dicoding** (opsional smoke-test manual sekali di HP: pilih foto makanan → muncul prediksi). 🎮 Sebelumnya device ini: **06 RootFacts (Dafina) DIBUAT & terverifikasi lokal** (2026-07-19): app RootFacts Basic (Vanilla JS: CV TensorFlow.js + GenAI Transformers.js **flan-t5-base** + PWA Workbox, deploy Netlify). Dibuat dari nol, **sengaja dibedakan dari Nazhif & Fareynaldi** (anti-plagiarisme): ES2022 `#private` fields, argmax via `tf.argMax`, preprocess via kanvas `drawImage`+`div(255).mul(2).sub(1)`, loop `setInterval`+guard `#busy`, **app-first** (kamera aktif dulu, LLM dimuat di latar via `#factReady`), `sw.js` `setCacheNameDetails` prefix `rootfacts-dmr`, ikon **daun**. Model flan-t5-base dipilih (Qwen2.5-0.5B ditolak krn `model_q4.onnx` = 786 MB terlalu berat). **K1 (predict+0-leak+offline), K2 (load+generate 4 fun fact dinamis/relevan), K3 (SW active+precache 17+manifest+offline reload+deteksi offline) semua terverifikasi live via Chrome DevTools MCP, 0 error.** App-first tombol aktif seketika + LLM latar "FLAN-T5-base siap". **SISA (user Dafina, 🍎):** deploy Netlify Drop → isi `STUDENT.txt APP_URL=` → zip flat `RootFacts_Dafina_Meira_Rizkia.zip` → upload. Panduan: `dafina/panduan/Deploy_Netlify.md`, detail `dafina/CLAUDE.md`. Sebelumnya device ini: **02 BFGAI (Dafina) DIBUAT** (2026-07-19): submission Image Generation SD1.5, target **Basic ⭐⭐⭐**. Folder `pengerjaan/dafina/` dibuat dari nol (Nazhif sudah punya versi sendiri — kode Dafina SENGAJA dibedakan: penamaan/struktur/mask-numpy/wording prompt beda; anti-plagiarisme). **Pipeline notebook** K1+K2 Basic terisi (7 sel: generate_simple/advanced_image + inpaint_engine, mirror model `stable-diffusion-v1-5/*`, seed 222/9). **Streamlit notebook** `logic.py` diisi LENGKAP + patch model mirror + patch kompat app.py (`use_column_width`, canvas `.copy()`) + pin streamlit 1.29.0. Semua lolos `ast.parse`, JSON valid, belum di-run. **SISA (butuh Dafina, ⛅ online):** Run All 2 notebook di **Colab T4** → screenshot 3 gambar (img_simple≈image-13 / img_advanced≈image-14 / img_inpaint≈image-15) kirim ke Claude buat verifikasi+tuning → isi token ngrok → rekam video Basic → Claude packaging zip. Panduan: `pengerjaan/dafina/panduan/Instruksi_Colab.md`. ⚠️ Titik risiko: K1 advanced (recipe guidance-rendah/tinggi belum diverifikasi Dicoding). Sebelumnya: 04 SMSML (Dafina) selesai (2 repo PUBLIC + CI hijau, tinggal upload zip). Dataset **Palmer Penguins** + **GradientBoosting** + MLflow autolog + Flask serving + Prometheus + Grafana (Docker) — sengaja beda dari Nazhif (Pima/RF) & Fareynaldi (Titanic/LogReg) untuk anti-plagiarisme. K1 notebook Run All 0-error, K2 model dilatih + 2 screenshot MLflow (auto-browser), K3 Workflow-CI lengkap (belum push), K4 stack jalan + 6 screenshot (serving/Prometheus×4/Grafana dashboard "Dafina Meira Rizkia"). Zip 798KB siap. **2 repo GitHub `dafina1907` PUBLIC + push + CI Actions hijau; 2 .txt sudah URL asli; zip di-regen. SISA: user tinggal UPLOAD zip ke Dicoding.** Detail: `pengerjaan/dafina/panduan/PANDUAN.md`. Sebelumnya: 03 PGABL (Dafina) skeleton (2026-07-19).
- **Yang paling mendesak (open action, urut prioritas):**
  0. **06 RootFacts (Dafina)** — 🔁 **DITOLAK (K2) → DIPERBAIKI, siap RE-SUBMIT** (2026-07-19), target Basic. Penolakan: fun fact stuck "Memuat fakta menarik" (model diunduh di latar/app-first). Fix: init muat LLM tuntas + header **"Memuat Model... X%"** → "Siap" + prompt/greedy (kualitas 17/18). Verified CDP. Zip regen. **Sisa: user REDEPLOY kode baru ke Netlify (`cerulean-lolly-3c6913` atau baru) → kalau URL baru update `STUDENT.txt` → re-zip → RE-SUBMIT.** 🍎 Panduan: `dafina/panduan/Deploy_Netlify.md`.
  1. **02 BFGAI (Nazhif)** — DITOLAK reviewer, revisi v3 sudah siap. Perlu **Run All notebook di Colab T4** → regenerate zip → **re-submit**. ⛅ butuh online.
  2. **02 BFGAI (Dafina)** — 🔁 **DITOLAK reviewer (penolakan_1.md) → REVISI notebook, PUTARAN 2** (2026-07-20), target Basic. Penolakan: **K1** simple terlalu realistis (harus **kartun**, image-3); **K2** satelit inpaint belum jelas (image-6). K3 Streamlit **LOLOS**. **Run Colab #1 (verified):** advanced ✅ realistis (trik negative anti-cartoon+guidance 12), satelit ✅ jelas — TAPI simple ❌ chibi/vektor kebablasan & mask nimpa astronot (astronot hilang). **Fix v2** (`scratchpad/fix_penolakan1_v2.py`): MOON_PROMPT buang "flat 2d"/"full body/wide shot" → sisakan "cartoon style" (kartun moderat); mask x0 0.45→0.57 (geser kanan, astronot selamat → astronot+satelit dua-duanya tampak ≈image-6). **Sisa (butuh Dafina, ⛅ Colab): Run All #2 → cek 4 sel → kirim Claude → download ber-output → re-zip → resubmit.** Panduan: `dafina/panduan/REVISI_penolakan_1.md` (PUTARAN 2). Zip belum diregenerate.
  2. **06 RootFacts (Nazhif)** — DITOLAK 2×, kedua koreksi sudah beres & live terverifikasi. Tinggal **re-submit zip** ke Dicoding.
  3. **05 Asclepius GCP (Nazhif)** — ⛔ TERBLOKIR: butuh `gcloud auth login` + billing account sebelum deploy Phase 3-7. Backend sudah OK lokal.
  4. **03 PGABL (Fareynaldi)** — skeleton notebook siap, belum pernah Run All. Perlu akun HF + Colab Secret → Run All di Colab T4.
  5. **03 PGABL (Dafina)** — ✅ **SELESAI DIKERJAKAN**. K1 SFT + K2 RAG + K3 antarmuka semua Run All & terverifikasi (model `dafina1907/PGABL-Qwen2.5-1.5B-SFT-Dafina` public). **Sisa: user tinggal upload `dafina/PGABL_Dafina_Meira_Rizkia.zip` (49 KB, flat 4 file) ke Dicoding.**
  6. **06 RootFacts (Fareynaldi)** — kode Basic SELESAI & terverifikasi lokal (Mac). Tinggal **user deploy Netlify (akun Fareynaldi)** → isi `STUDENT.txt` → zip `RootFacts_Fareynaldi_Affan.zip` → upload. Panduan di folder proyek.
  7. **07 Food Scan App (Fareynaldi)** — 🔁 **DITOLAK → DIPERBAIKI, siap RE-SUBMIT** (2026-07-19). Build gagal di Flutter terbaru krn `tflite_flutter` usang → di-fix ke Flutter **3.44.6/Dart 3.12.2** + **`flutter_litert ^3.5.1`**. Build APK LOLOS + inferensi terverifikasi (emulator API 36.1). **Zip regen:** `submission/food_scan_app_Fareynaldi.zip` = **18.83 MB** (forward-slash). Tinggal user **RE-SUBMIT ke Dicoding** (opsional smoke-test 1× di HP).
  8. **07 SantapLens (Dafina)** — ✅ **DIBUAT dari nol & terverifikasi live** (2026-07-20), target Basic. App Flutter pengenal makanan (AIY Food V1 + LiteRT `flutter_litert`; tema oranye, `ValueNotifier`, gauge `CustomPaint`, top-3 — sengaja beda dari `food_recognizer`/Nazhif & `food_scan_app`/Fareynaldi). Build debug+release LOLOS di Flutter **3.44.6** (error JVM `tflite_flutter` TAK muncul krn scaffold segar + `flutter_litert`; sempat gagal `Could not close incremental caches` → fix `kotlin.incremental=false`). Inferensi on-device benar ("Satay" 99.6%), K1 galeri+kamera / K2 LiteRT / K3 halaman hasil verified live emulator. Review 3-agent: anti-plagiarisme vs Nazhif **LOW**, vs Fareynaldi **MEDIUM→fix→LOW** (rework blok loading/error/skeleton + reword pesan/komentar + rename getter), kepatuhan **LULUS MINIMAL**. **Zip `submission/santap_lens_Dafina.zip` (19.75 MB, git-tracked) siap — user tinggal UPLOAD ke Dicoding** (opsional smoke-test 1× di HP). 🎮 Detail: `dafina/CLAUDE.md`, panduan `dafina/panduan/README.md`.
- **Menunggu review Dicoding (jangan submit ulang):** 01-klasifikasi (Nazhif, Dafina, Fareynaldi), 01-analisis (Dafina, Fareynaldi, Bimo), 04 (Nazhif, Fareynaldi), 07 (Nazhif), 09 (Nazhif).
- **⚠️ Artefak yang cuma ada di SATU device (risiko sync):** zip final **01-klasifikasi/dafina**, **01-klasifikasi/bimo**, & **01-analisis/dafina** hanya ada di **Victus** (belum di Mac). Kalau mau upload dari Mac → regenerate dulu. Lihat tabel artefak di bawah.
<!-- HANDOFF:END -->

---

## Legenda status

| Simbol | Arti |
|---|---|
| ✅ | **Diterima** reviewer Dicoding (selesai) |
| 📤 | **Sudah dipaket** — terkirim / menunggu review (JANGAN submit ulang) |
| 🔁 | **Ditolak → revisi siap re-submit** |
| 🚧 | **Sedang dikerjakan** (belum tuntas) |
| ⛔ | **Terblokir** (nunggu sesuatu di luar kode) |

Device: 🍎 = jalan cukup di Mac lokal · 🎮 = butuh Victus (GPU lokal) · ⛅ = butuh online (Colab/Cloud)

---

## Ringkasan cepat

- **Total:** 24 folder pengerjaan (9 course, 4 anggota) — +1: `07 SantapLens (Dafina)` dibuat 2026-07-20.
- **✅ Diterima:** 3 (semua Nazhif, semua ⭐⭐⭐⭐⭐) — `01 analisis-sentimen`, `03 PGABL`, `08 BMLP`.
- **🔁 Ditolak→siap resubmit:** 3 — `02 BFGAI`, `06 RootFacts`, `07 Food Scan (Fareynaldi)`.
- **📤 Menunggu review / upload:** 9.
- **🚧 Sedang dikerjakan:** 4 — `03 PGABL (Fareynaldi)`, `06 RootFacts (Fareynaldi)`, `06 RootFacts (Dafina)` (kode + verifikasi live done, tinggal user deploy Netlify + upload). (`03 PGABL (Dafina)` & `04 SMSML (Dafina)` → 📤 selesai, tinggal upload zip.)
- **⛔ Terblokir:** 1 — `05 Asclepius GCP` (gcloud auth + billing).

---

## Matriks status per course × anggota

| # | Course | Tema / anggota | Status | Bintang | Dev | Langkah berikutnya |
|---|---|---|---|---|---|---|
| 01 | fundamental-deep-learning · **klasifikasi-gambar** | Animals-10 CNN — **Nazhif** | 📤 | target ⭐⭐⭐⭐⭐ | ⛅🍎 | Upload zip 82MB / tunggu review |
| 01 | · klasifikasi-gambar | TF Flowers — **Dafina** | 📤 | target ⭐⭐⭐ | 🎮 | Upload zip (⚠️ zip cuma di Victus) |
| 01 | · klasifikasi-gambar | Garbage 12-kelas EffNetV2 — **Fareynaldi** | 📤 | target ⭐⭐⭐⭐⭐ | ⛅🍎 | Upload zip 96MB ke Drive → submit link |
| 01 | · klasifikasi-gambar | Fruits-360 10 kelas — **Bimo** | 📤 | target ⭐⭐⭐ (Train/Test 100%) | 🎮 | Upload zip 38.5MB (⚠️ zip cuma di Victus) |
| 01 | fundamental-deep-learning · **analisis-sentimen** | PLN Mobile 4-skema — **Nazhif** | ✅ | ⭐⭐⭐⭐⭐ | 🍎🎮 | **SELESAI** |
| 01 | · analisis-sentimen | Shopee 4-skema — **Bimo** | 📤 | ⭐⭐⭐⭐ (Skilled) | ⛅🍎 | Upload zip / tunggu review |
| 01 | · analisis-sentimen | DANA SVM+TF-IDF — **Dafina** | 📤 | target ⭐⭐⭐ | 🍎 | Upload zip (⚠️ zip cuma di Victus) |
| 01 | · analisis-sentimen | MyTelkomsel 4-skema — **Fareynaldi** | 📤 | target ⭐⭐⭐⭐⭐ | 🎮🍎 | Upload zip 6.6MB / tunggu review |
| 02 | fundamental-generative-ai | BFGAI Streamlit SD1.5 — **Nazhif** | 🔁 | target ⭐⭐⭐⭐⭐ | ⛅ | Run All v3 di Colab → regen zip → **re-submit** |
| 02 | fundamental-generative-ai | BFGAI Streamlit SD1.5 — **Dafina** | 📤 | target ⭐⭐⭐ (Basic) | ⛅ | ✅ K1+K2+K3 Run & terverifikasi. Zip `BFGAI_Dafina_Meira_Rizkia.zip` (5 MB) siap — **upload ke Dicoding** |
| 03 | pengembangan-generative-ai-llm | PGABL chatbot legal RAG — **Nazhif** | ✅ | ⭐⭐⭐⭐⭐ | ⛅ | **SELESAI** |
| 03 | pengembangan-generative-ai-llm | PGABL versi Basic — **Fareynaldi** | 🚧 | target ⭐⭐⭐ | ⛅ | Akun HF + Colab Secret → Run All 2 notebook |
| 03 | pengembangan-generative-ai-llm | PGABL versi Basic (Qwen+FAISS) — **Dafina** | 📤 | target ⭐⭐⭐ | ⛅ | ✅ Semua kriteria jalan & terverifikasi. Zip `PGABL_Dafina_Meira_Rizkia.zip` (49 KB) siap — **upload ke Dicoding** |
| 04 | membangun-sistem-machine-learning | SMSML Pima diabetes — **Nazhif** | 📤 | — | 🍎 | Cek status review di dashboard Dicoding |
| 04 | membangun-sistem-machine-learning | SMSML Titanic — **Fareynaldi** | 📤 | — | 🍎 | Cek review; pastikan `Workflow-CI` ke-push GitHub |
| 04 | membangun-sistem-machine-learning | SMSML Palmer Penguins — **Dafina** | 📤 | target ⭐⭐⭐ (Basic) | 🎮 | K1–K4 done, 2 repo `dafina1907` PUBLIC + CI hijau, zip siap. **Tinggal user upload zip ke Dicoding** |
| 05 | penerapan-machine-learning-google-cloud | Asclepius Hapi TF.js GCP — **Nazhif** | ⛔ | target ⭐⭐⭐⭐⭐ | ⛅🍎 | `gcloud auth login` + billing → deploy Phase 3-7 |
| 06 | penerapan-ai-aplikasi-web | RootFacts PWA TF.js — **Nazhif** | 🔁 | target ⭐⭐⭐ (Basic) | 🍎 | **Re-submit** (koreksi-2 sudah beres, live sehat) |
| 06 | penerapan-ai-aplikasi-web | RootFacts PWA (LaMini-Flan-T5) — **Fareynaldi** | 🚧 | target ⭐⭐⭐ (Basic) | 🍎 | Kode Basic done+verified lokal. **User deploy Netlify → STUDENT.txt → zip → upload** |
| 06 | penerapan-ai-aplikasi-web | RootFacts PWA (flan-t5-base) — **Dafina** | 🔁 | target ⭐⭐⭐ (Basic) | 🍎 | **Ditolak K2 → diperbaiki** (progress % + greedy). User **REDEPLOY Netlify → re-zip → RE-SUBMIT** |
| 07 | penerapan-machine-learning-flutter | Food Recognizer TFLite — **Nazhif** | 📤 | target ⭐⭐⭐ | 🎮 | Verifikasi zip ter-upload / tunggu review |
| 07 | penerapan-machine-learning-flutter | Food Scan App (litert) — **Fareynaldi** | 🔁 | target ⭐⭐⭐ (Basic) | 🎮 | DITOLAK (build gagal `tflite_flutter`) → fix Flutter 3.44.6 + `flutter_litert`. Build+inferensi verified. Zip 18.83MB. **RE-SUBMIT** |
| 07 | penerapan-machine-learning-flutter | SantapLens (litert) — **Dafina** | 📤 | target ⭐⭐⭐ (Basic) | 🎮 | ✅ DIBUAT & verified live (build LOLOS 3.44.6, "Satay" 99.6%, K1/K2/K3). Zip `santap_lens_Dafina.zip` 19.75MB siap — **upload ke Dicoding** |
| 08 | membangun-proyek-machine-learning | BMLP Clustering+Klasifikasi — **Nazhif** | ✅ | ⭐⭐⭐⭐⭐ (4.0) | 🍎 | **SELESAI** |
| 09 | openshop-restful-api | OpenShop Django REST — **Nazhif** | 📤 | — | 🍎 | Konfirmasi zip ter-upload / cek review |

---

## Di mana artefak berat hidup (KRITIS untuk sync — git TIDAK bawa ini)

> Model/dataset/`.venv` di-`.gitignore`. Kalau pindah device dan butuh artefak ini, ambil dari lokasi berikut (atau regenerate).

| Proyek | Artefak berat | Lokasi |
|---|---|---|
| 03 PGABL (Nazhif) | Model SFT & GRPO (merged_16bit) | **HuggingFace** [PGABL-Llama-3.2-3B-SFT](https://huggingface.co/nazhifsetya-merpati/PGABL-Llama-3.2-3B-SFT) · [PGABL-Llama-3.2-3B-GRPO](https://huggingface.co/nazhifsetya-merpati/PGABL-Llama-3.2-3B-GRPO). Bobot+ChromaDB cache di **Google Drive** `MyDrive/PGABL/models` (~10GB) |
| 02 BFGAI (Nazhif) | SD1.5 + inpainting (~10GB) | Di-pull runtime dari HF (`stable-diffusion-v1-5/*`, `CIDAS/clipseg-*`). Video demo di `submission/video_demo_aplikasi_BFGAI.mp4` |
| 06 RootFacts (Nazhif) | Model TM (in-repo) + SmolLM2-135M | TF.js Teachable Machine ada di `submission/root-facts/model/` (ikut git). LLM di-download runtime dari HF CDN. Live: [lively-gecko-2d2054.netlify.app](https://lively-gecko-2d2054.netlify.app/) |
| 06 RootFacts (Fareynaldi) | Model TM (in-repo) + LaMini-Flan-T5-248M | TF.js Teachable Machine ikut git di `pengerjaan/fareynaldi-affan/submission/root-facts/model/`. LLM (`Xenova/LaMini-Flan-T5-248M`, text2text) di-download runtime dari HF Hub. Belum deploy (nunggu user). |
| 05 Asclepius (Nazhif) | Model TF.js graph (~14MB) + test images | Git-ignored lokal; re-download dari release Dicoding. Target GCS `gs://submissionmlgc-nazhifsetya-model` |
| 01-klasifikasi (Nazhif) | SavedModel/TFLite/TFJS (~82MB zip) | Lokal di `submission/` + zip di root (git-ignored). Dataset via `kagglehub` on-the-fly |
| 01-klasifikasi (Dafina) | Zip 45MB + saved_model/tfjs | **HANYA di Victus** (`d:\`) — belum ada di Mac ⚠️ |
| 01-klasifikasi (Bimo) | Zip 38.5MB + saved_model/tflite/tfjs | **HANYA di Victus** (`d:\`) — belum ada di Mac ⚠️. Dataset Fruits-360 via git sparse-checkout on-the-fly di notebook |
| 01-klasifikasi (Fareynaldi) | Zip 96MB + saved_model/tflite/tfjs | Lokal `submission/`; belum di-upload ke Drive |
| 01-analisis (Nazhif) | *.keras/*.joblib + IndoBERT + CSV | Lokal `submission/` (git-ignored, tak ada mirror). IndoBERT dilatih di Victus |
| 01-analisis (Dafina) | Zip final 1.5MB | **HANYA di Victus** — belum di Mac ⚠️ |
| 01-analisis (Fareynaldi/Bimo) | IndoBERT weights | Fareynaldi: dilatih di Victus (folder `indobert_victus/`, bukan bobot). Bimo: dilatih di Colab, hanya JSON metrik disimpan |
| 07 Food Recognizer (Nazhif) | `aiy_food_v1.tflite` (~24MB) | **Git-ignored** (`*.tflite` di root `.gitignore`). Dari Kaggle. Perlu re-download tiap device. |
| 07 Food Scan App (Fareynaldi) | `aiy_food_v1.tflite` (~24MB) | **Git-ignored**. Sama dari [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1). Rename ke `aiy_food_v1.tflite` (huruf kecil), taruh di `submission/food_scan_app/assets/models/`. |
| 07 SantapLens (Dafina) | `aiy_food_v1.tflite` (21MB) | **Git-ignored** (`*.tflite`). Model sama dari [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1); taruh di `submission/santap_lens/assets/models/`. **TAPI** model ikut di dalam **zip git-tracked** `submission/santap_lens_Dafina.zip` (19.75MB) — jadi aman lintas device via zip. |
| 04, 08, 09 (Nazhif/Fareynaldi) | Model kecil (<2MB) | Ikut git di `submission/` — aman lintas device |

---

## Catatan detail per-proyek

### ✅ Sudah diterima (SELESAI)
- **01 analisis-sentimen / Nazhif** — PLN Mobile, 4 skema (SVM/BiLSTM/CNN/IndoBERT), ⭐⭐⭐⭐⭐. IndoBERT dilatih di Victus.
- **03 PGABL / Nazhif** — chatbot legal SLM (Llama-3.2-3B QLoRA+GRPO) + RAG + Gradio, Advanced 4pts semua kriteria. Model di HF.
- **08 BMLP / Nazhif** — Clustering K-Means + Klasifikasi DT/RF, Advanced 4.0 semua 5 kriteria. Jalan penuh di Mac.

### 🔁 Ditolak → revisi siap re-submit
- **02 BFGAI / Nazhif** — Streamlit SD1.5 (Text-to-Image + Inpaint/Outpaint + UI). v1 ditolak (K1&K2), sudah revisi ke v3 "SIAP RESUBMIT". **Perlu Run All di Colab T4** dulu buat verifikasi visual + regen zip.
- **06 RootFacts / Nazhif** — web app Vanilla JS (CV TF.js + GenAI Transformers.js, PWA, Netlify). Ditolak 2×, kedua koreksi RESOLVED, live site 0-error. Tinggal re-submit.

### 🚧 Sedang dikerjakan
- **06 RootFacts / Dafina** — target **Basic ⭐⭐⭐**. Web app Vanilla JS (CV TensorFlow.js + GenAI Transformers.js **flan-t5-base** text2text, PWA Workbox offline-first, Netlify). Dibuat dari nol 2026-07-19 di Victus, **sengaja dibedakan dari Nazhif (SmolLM2-135M/sprout) & Fareynaldi (LaMini-Flan-T5-248M/wortel)** untuk anti-plagiarisme: model **flan-t5-base**, ES2022 `#private` fields, argmax `tf.argMax`, preprocess kanvas `drawImage`+`div(255).mul(2).sub(1)`, loop `setInterval`+guard `#busy`, **app-first** (kamera dulu, LLM di latar `#factReady`), `sw.js` prefix `rootfacts-dmr` + `setCacheNameDetails`, ikon **daun** `#15803d`. Qwen2.5-0.5B-Instruct ditolak (786 MB terlalu berat). Loop deteksi TIDAK menggerbang confidence (belajar dari penolakan Nazhif). **Verifikasi live Chrome DevTools MCP (0 error):** K1 TF.js 4.22.0+18 label+predict+8× tanpa leak+deteksi offline; K2 flan-t5-base load+generate 4 fun fact dinamis & mostly-relevan + sanitasi anti-injection; K3 SW active+precache `rootfacts-dmr-precache` 17 file+manifest 4 ikon installable+offline reload app shell+deteksi. Zip **belum** dibuat. **SISA (user Dafina, 🍎):** deploy Netlify → `STUDENT.txt` → zip flat → upload. Detail `dafina/CLAUDE.md`, panduan `dafina/panduan/Deploy_Netlify.md`.
- **02 BFGAI / Dafina** — target **Basic ⭐⭐⭐**. Submission Image Generation (Text-to-Image + Inpainting + Streamlit UI) di atas SD1.5. Dibuat dari nol 2026-07-19 di Victus; **sengaja dibedakan dari Nazhif** (anti-plagiarisme): penamaan var (`txt2img`/`inpaint`/`MOON_PROMPT`), struktur fungsi, **mask via numpy** (bukan ImageDraw), preview overlay merah, wording prompt beda — walau model/seed/template dikunci Dicoding (sama untuk semua). Fokus diferensiasi di **Pipeline notebook** (blank-slate); Streamlit blank-fill jawabannya seragam (bukan area plagiarisme). **Pipeline** K1+K2 Basic terisi (sel 1/4/6/8/25/27/29), sel Skilled/Advanced dibiarkan kosong. **Streamlit** `logic.py` diisi penuh (biar app robust, tetap grade Basic) + patch mirror model + patch kompat app.py + pin streamlit 1.29.0. Model SD1.5+inpaint (~10GB) di-pull runtime dari HF mirror `stable-diffusion-v1-5/*` (publik, tanpa token). **✅ SELESAI Run All Colab & terverifikasi visual (2026-07-19, ~7 iterasi tuning K1):** K1 `img_simple`/`img_advanced` = astronot wide-shot berdiri di bulan (≈image-3/4; prompt TANPA kata gaya biar wide-shot bukan portrait, simple g7.5 / advanced g9.0-60steps); K2 satelit rusak + panel surya muncul jelas di kanan astronot (≈image-15; mask ke tanah kosong + inpaint g20 + negative anti-tanah). K3 app Streamlit jalan via ngrok, video demo 2:06 (semua komponen Basic + bonus scheduler/batch) → `.mp4` 3.12 MB. Token ngrok disanitasi. **Zip flat `BFGAI_Dafina_Meira_Rizkia.zip` (5.04 MB, 4 file) SIAP — sisa: user tinggal UPLOAD ke Dicoding.** Pelajaran resep final di `dafina/CLAUDE.md`.
- **03 PGABL / Fareynaldi** — target Basic. 2 notebook skeleton lolos syntax, **belum Run All**. Butuh akun HF sendiri + Colab Secret (HF_TOKEN, HF_USERNAME) + upload 4 PDF ke Drive, lalu Run All (SFT ~90-120mnt, baru RAG). Victus 4GB VRAM TIDAK cukup → wajib Colab T4.
- **04 SMSML / Dafina** — target Basic (⭐⭐⭐). Proyek MLOps 4 kriteria, dibuat & dijalankan penuh lokal di Victus (2026-07-19). Stack sengaja dibedakan dari Nazhif (Pima diabetes, RandomForest) & Fareynaldi (Titanic, LogisticRegression): dataset **Palmer Penguins** (klasifikasi 3 spesies), model **GradientBoostingClassifier**, `pathlib`+`main()`, experiment `Penguins_Species_Classification`, exporter metrik `penguin_*` di port 8501. K1 notebook Run All 0-error → `penguins_preprocessing.csv` (333×9). K2 autolog, akurasi uji 1.0, 2 screenshot MLflow. K3 `Workflow-CI` (MLProject+ci.yml) belum push. K4 Flask serving + Prometheus (4 metrik) + Grafana (Docker, dashboard "Dafina Meira Rizkia" 5 panel) — 6 screenshot auto-browser. Zip 798KB di `submission/`. **2 repo GitHub PUBLIC pushed + CI hijau:** [Eksperimen_SML](https://github.com/dafina1907/Eksperimen_SML_Dafina-Meira-Rizkia) & [Workflow-CI](https://github.com/dafina1907/Workflow-CI) (akun `dafina1907`, Actions SUCCESS 1m8s). 2 .txt sudah berisi URL asli, zip di-regen. **SISA: user tinggal UPLOAD `submission/SMSML_Dafina-Meira-Rizkia.zip` ke Dicoding** (+ opsional samakan nama dashboard Grafana ke username Dicoding). Detail: `dafina/panduan/PANDUAN.md` & `dafina/CLAUDE.md`.
- **03 PGABL / Dafina** — target Basic, submission independen. Stack sengaja dibedakan dari Nazhif & Fareynaldi (anti-plagiarisme): base **Qwen2.5-1.5B-Instruct** (ChatML, Apache-2.0) + embedder **multilingual-e5-base** + **FAISS** + chunker **berbasis-kalimat** (700/120) + interface **loop `input()`**. 2 notebook skeleton terverifikasi (JSON/syntax/HR-14/anti-plagiarisme/chunker). **K1 SFT ✅ RUN & VERIFIED (2026-07-19)**: user Run All di Colab (akun HF `dafina1907`), model `dafina1907/PGABL-Qwen2.5-1.5B-SFT-Dafina` merged_16bit public (model.safetensors 3.09 GB, tag qwen2, verified) — HR-5 terpenuhi. **K2 RAG + K3 antarmuka juga ✅ RUN & VERIFIED**: notebook RAG 380 KB, output ter-embed, tanya-jawab `input()` 4×, audit HR1-14 PASS. **Zip flat `dafina/PGABL_Dafina_Meira_Rizkia.zip` (49 KB) SIAP — sisa: user upload ke Dicoding.** Gotcha lapangan: folder Drive sempat bernama `PGABL_Dafina ` (ada SPASI di belakang) → rename hapus spasi baru kebaca. Detail + panduan di `dafina/panduan/PANDUAN_COLAB.md`.

### 📤 Baru selesai — siap upload
- **07 Food Scan App / Fareynaldi** — target Basic (⭐⭐⭐). Flutter app di `submission/food_scan_app/`, package `com.fareynaldi.foodscan`, tema hijau. **Sengaja dibedakan struktur** dari `food_recognizer` (Nazhif) untuk anti-plagiarisme (folder `ml/models/screens/widgets`, kelas `TfliteFoodDetector.analyze()` + `ScanResult`, tanpa provider). Fully verified 2026-07-17 di HP Samsung SM-S721B: kamera OK, galeri OK, inferensi TFLite jalan (Rendang → "Rendang" 18%, Sedaap → "Ramen" 5.5%). Screenshot bukti di `scratchpad/`. **⚠️ DITOLAK reviewer (2026-07-19)** — bukan fitur salah, tapi **build gagal di Flutter terbaru**: `tflite_flutter` usang bentrok JVM (Java 8 vs Kotlin 21) → K1/K2/K3 auto "Perlu diperbaiki". **DIPERBAIKI persis saran reviewer:** `flutter upgrade` → **3.44.6/Dart 3.12.2**, `pubspec sdk ^3.12.2` + **`tflite_flutter`→`flutter_litert ^3.5.1`** (API source-compatible, 1 baris import). Re-verified di Victus: `flutter build apk --debug` LOLOS (exit 0) + integration test emulator API 36.1 (inferensi `flutter_litert` jalan, All tests passed). Zip regen via bsdtar (cruft dibuang, forward-slash) → **`submission/food_scan_app_Fareynaldi.zip` = 18.83 MB**. **Siap RE-SUBMIT** (detail lengkap di `fareynaldi/CLAUDE.md` Progress Log 2026-07-19).

### ⛔ Terblokir
- **05 Asclepius / Nazhif** — backend Hapi TF.js untuk deteksi kanker, deploy ke GCP (Cloud Run + Storage + Firestore + App Engine). Backend **sudah lolos 4 skenario Postman lokal**. Deploy Phase 3-7 nunggu `gcloud auth login` + billing account (`nazhif.nugroho@gmail.com`), region `asia-southeast2`. Panduan di `DEPLOY-NOTES.md`.

### 📤 Menunggu review (jangan submit ulang)
- **01 klasifikasi / Nazhif** — Animals-10 CNN, notebook Colab 0-error (Test 96.61%), zip 82MB siap.
- **01 klasifikasi / Dafina** — TF Flowers 5 kelas (Test 86.72%), lokal Victus CPU. ⚠️ zip cuma di Victus.
- **01 klasifikasi / Fareynaldi** — Garbage 12 kelas EfficientNetV2B0 (Test 95.64%), zip 96MB perlu upload Drive.
- **01 klasifikasi / Bimo** — Fruits-360 10 kelas buah (Train/Test 100%), lokal Victus CPU, MobileNetV2 frozen + Conv2D. Split anti-bocor (Test folder bawaan). 3 format + zip 38.5MB. ⚠️ zip cuma di Victus.
- **01 analisis / Bimo** — Shopee 4-skema, dapat ⭐⭐⭐⭐ Skilled (target 5, test 90.66%). IndoBERT di Colab.
- **01 analisis / Dafina** — DANA SVM+TF-IDF (Test 91.41%). ⚠️ zip cuma di Victus.
- **01 analisis / Fareynaldi** — MyTelkomsel 4-skema (IndoBERT test 92.78%), zip 6.6MB. IndoBERT di Victus.
- **04 SMSML / Nazhif** — Pima diabetes, MLflow+CI+Prometheus/Grafana. Repo: `github.com/nazhifSetya/Workflow-CI`, `Eksperimen_SML_Nazhif-Setya-Nugroho`.
- **04 SMSML / Fareynaldi** — Titanic, MLflow LogisticRegression + CI + monitoring. Repo `github.com/fareynaldi/*`.
- **07 Food Recognizer / Nazhif** — Flutter TFLite AIY Food V1, "shipped as Basic". Build di Windows + Android emulator.
- **09 OpenShop / Nazhif** — Django 4.2 + DRF CRUD produk + soft-delete + Postman. Jalan di Mac.

---

## Yang belum punya CLAUDE.md per-proyek (memory tipis)

Folder ini belum punya `CLAUDE.md` sendiri — konteks disimpulkan dari README/kode. Kalau nanti dikerjakan lagi, pertimbangkan bikin `CLAUDE.md` biar nyambung lintas device:
`04/nazhif`, `04/fareynaldi`, `05/nazhif`, `09/nazhif`.

---

**Cara update file ini:** ubah baris proyek yang digarap + isi ulang blok **FOKUS SAAT INI / HANDOFF** + ganti stempel **Terakhir di-update** di atas. Lalu commit+push.
