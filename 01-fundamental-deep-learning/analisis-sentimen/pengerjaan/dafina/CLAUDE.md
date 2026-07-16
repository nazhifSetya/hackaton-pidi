# CLAUDE.md — Proyek Analisis Sentimen · **DANA (e-wallet)** · submission utk **Dafina**

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Analisis Sentimen**, tema **DANA (aplikasi e-wallet)**, atas nama **Dafina**.
- **Self-contained di folder ini** (`.../proyek analisis sentimen/dafina/`). Folder induk (`../`) berisi 3 submission teman yang sudah SELESAI (Nazhif ⭐⭐⭐⭐⭐, Fareynaldi ⭐⭐⭐⭐⭐, Bimo ⭐⭐⭐⭐) → **REFERENSI metodologi saja, JANGAN diubah.**
- Aturan Everest/EBC (backoffice-service, Sequelize, CLIK, dll di `docs/CLAUDE.md`) **TIDAK berlaku di sini.**
- **Ini iterasi ke-4 dari trio submission tim, dengan pendekatan BERBEDA:** teman-teman kejar ⭐⭐⭐⭐⭐ (level Ambisius, banyak saran diterapkan, IndoBERT di Colab). **Dafina cukup KRITERIA BATAS BAWAH (⭐⭐⭐)** — semua proses lokal di Victus, tanpa Colab, tanpa deep learning, tanpa XAI. Prinsip: **lulus dulu dengan risiko minimum, kode ringkas dan cepat.**

---

## 👤 USER & GAYA KERJA

- **Pemilik submission:** **Dafina** — dipakai di semua nama file: `Dafina`. (Nama lengkap **menyusul** — sementara cukup `Dafina`.)
- **Konteks:** Mahasiswa Dicoding, level pemula. Proyek Deep Learning / NLP pertamanya. Tiga teman timnya (Nazhif, Fareynaldi, Bimo) sudah selesai proyek serupa dengan tema berbeda.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia simpel, mudah dimengerti pemula.**
  - **Pelan-pelan, step-by-step.** Jelaskan **kenapa** tiap langkah, bukan cuma **apa**.
  - **Teliti detail kecil.**
  - **Jangan asumsi.** Kalau ambigu (threshold, nama kolom, pilihan model), **tanya dulu** pakai AskUserQuestion.
  - Kalau tunjukkan pattern kode dari proyek Nazhif/Fareynaldi/Bimo, sertakan **path file + line number** supaya Dafina bisa buka sendiri di editor.
- **Target nilai:** **⭐⭐⭐ (Pass)** — kriteria utama saja, tanpa saran wajib. Kalau tanpa effort tambahan naik ke ⭐⭐⭐⭐ (mis. saran #3 3-kelas dan saran #6 inference murah), bagus — **tapi jangan over-engineer**. Fokus lulus dulu dengan risiko minimum.

---

## 🎯 INTI PROYEK

Model **analisis sentimen klasik** (klasifikasi teks) dari **ulasan Bahasa Indonesia aplikasi DANA** di Google Play Store, di-**scraping mandiri**.

**Alur (SEDERHANA, 6 tahap):** scraping → EDA singkat → preprocessing teks → pelabelan hybrid → 1 skema pelatihan (SVM+TF-IDF) → inference singkat → packaging.

> **Bandingkan dengan teman-teman (JANGAN ditiru semua):** Nazhif/Fareynaldi/Bimo pakai 4 skema (SVM+BiLSTM+CNN+IndoBERT) + XAI + Error Analysis + NRCLex. Dafina **cukup 1 skema SVM+TF-IDF** — sudah cukup memenuhi kriteria wajib "algoritma pelatihan ML" + akurasi ≥85%.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Tema** | Sentimen ulasan **DANA** (`id.dana`) | E-wallet — domain berbeda dari 3 tema tim (PLN utility, MyTelkomsel telco, Shopee e-commerce). Kosakata: `saldo, transfer, topup, tarik tunai, biaya admin, gagal, error, refund, promo`. |
| **Sumber data** | Google Play Store via `google-play-scraper` (lang=`id`, country=`id`) | Scraping mandiri = wajib. DILARANG pakai dataset open-source jadi. |
| **Strategi scrape** | **Stratified per bintang 1-5**, target `{1:1500, 2:1000, 3:1500, 4:1000, 5:1500}` ≈ **6.500** | Aman >3.000 (kriteria wajib #1). Kalau ⭐2/⭐3 langka, kompensasi via ⭐1/⭐5 hingga total 6.500. |
| **Pelabelan** | **Hybrid rating-murni + lex netral**: neg=⭐1, pos=⭐5, buang ⭐2 & ⭐4; netral=⭐3 dgn `\|lex net\|=0` (strict, pola Nazhif). Lexicon **net-weight** InSet (WAJIB). | Netral bisa kecil (struktural, mirip Nazhif 662 & Bimo 1.106) — tidak apa-apa, model tetap belajar polar dgn baik. |
| **Skema pelatihan** | **1 skema SAJA**: SVM (LinearSVC) + TF-IDF, split 80/20 | Kriteria wajib "algoritma pelatihan ML" + test ≥85%. SVM+TF-IDF terbukti mudah lolos ≥85% di 3 tema tim (PLN 92%, MyTelkomsel 91%, Shopee 88%). |
| **Kelas** | **3 kelas** (negatif/netral/positif) | Bonus murah — otomatis penuhi saran #3. |
| **Target nilai** | **⭐⭐⭐ (Pass) — kriteria utama** + saran #3 (3 kelas) & mungkin #4 (≥10rb kalau scrape membesar) & #6 (inference murah). **JANGAN kejar saran #1 (DL), #2 (>92%), #5 (3 skema)** — over-engineer. | |
| **Environment** | **100% lokal Victus** (Windows + RTX 3050, tapi TIDAK pakai GPU/CUDA — semua CPU) | Lihat §ENVIRONMENT. TIDAK ADA Colab. |

---

## 📁 STRUKTUR FOLDER

```
dafina/
├── CLAUDE.md                       ← file ini (memory + rules)
├── .python-version                 ← pin Python 3.10.x (untuk uv)
├── .venv/                          ← virtual env Windows lokal (JANGAN di-commit/zip)
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang di-zip)
    ├── scraping_dana.py                ← kode scraping (WAJIB)
    ├── dataset_dana_reviews.csv        ← dataset mentah hasil scraping (WAJIB)
    ├── dataset_dana_labeled.csv        ← dataset berlabel (pendukung)
    ├── pelatihan_analisis_sentimen.ipynb  ← notebook utama (WAJIB, sudah di-run)
    ├── requirements.txt                ← (WAJIB)
    └── kamus/                          ← lexicon InSet (net-weight) + slang (salin dari `../../submission/kamus/`)
```

> **Referensi (JANGAN diubah):**
> - `../submission/` (notebook PLN pemenang Nazhif ⭐⭐⭐⭐⭐)
> - `../CLAUDE.md`, `../Feedback_Reviewer_Dicoding.md`
> - `../fareynaldi/submission/`, `../fareynaldi/CLAUDE.md`
> - `../bimo_bramantyo/submission/`, `../bimo_bramantyo/CLAUDE.md`

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

### Windows lokal Victus (100% di sini — TANPA Colab)

- **Python:** 3.10.x, di-pin via `.python-version` untuk `uv`.
- **Package manager:** **uv** (super cepat). Kalau belum ada: `pip install --user uv` atau `winget install --id=astral-sh.uv`.
- **Bikin venv:** `uv venv .venv --python 3.10`
- **Aktifkan (PowerShell):** `. .venv\Scripts\Activate.ps1`
- **Jalankan Python:** `.venv\Scripts\python.exe <script>` atau setelah aktivasi cukup `python <script>`.
- **Library MINIMAL (jauh lebih ringkas dari Bimo):**
  ```powershell
  uv pip install google-play-scraper pandas numpy scikit-learn Sastrawi matplotlib seaborn wordcloud jupyter ipykernel joblib
  ```
  > **TIDAK PERLU:** tensorflow, torch, transformers, mpstemmer, nrclex, shap, lime — karena tidak pakai DL/IndoBERT/XAI. Stemming pakai **Sastrawi** biasa (lebih lambat tapi cukup untuk 6.500 baris; MPStemmer opsional kalau ingin cepat).
- **Semua tugas di Victus:** scraping, EDA singkat, preprocessing, pelabelan, 1 skema SVM+TF-IDF, inference sederhana, packaging.
- **CPU cukup.** Tidak butuh GPU/CUDA. RTX 3050 idle.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `../artifacts/2.kriteria_utama.md`, `../artifacts/4.ketentuan_berkas_submission.md`, `../artifacts/5.lainnya.md`.

1. **WAJIB lampirkan kode & proses scraping.** Tanpa itu → reject.
2. **Akurasi testing set model yang dinilai ≥ 85%.** Di bawah itu → reject.
3. **WAJIB 4 berkas kriteria utama:** notebook `.ipynb`, kode scraping `.py`/`.ipynb`, `requirements.txt`, dataset `.csv`/`.json`.
4. **DILARANG pakai dataset open-source yang sudah jadi.** Harus scraping sendiri.
5. **Notebook `.ipynb` WAJIB sudah dijalankan** → output ter-embed tanpa reviewer perlu run ulang.
6. **Kalau ada cell inference:** output WAJIB kategorikal (negatif/netral/positif) + bukti (tampilan output di notebook).
7. **WAJIB Accuracy & F1-Score pada testing set** untuk model yang dinilai.
8. Kirim dalam **1 folder di-zip**. Bahasa: **Python**.
9. **Jangan submit berkali-kali** (memperlama antrian; review ±3 hari kerja).

---

## 📊 PETA SARAN → BINTANG (fokus BATAS BAWAH)

**Kriteria Utama (WAJIB — kalau tidak → ditolak, tanpa nilai):**
1. Data hasil scraping mandiri, **min 3.000 sampel**. → **Target: 6.500** ✅ aman.
2. Ekstraksi fitur + pelabelan data. → **TF-IDF + hybrid label** ✅.
3. Pakai algoritma ML. → **SVM (LinearSVC)** ✅.
4. Akurasi testing **min 85%**. → **SVM+TF-IDF terbukti 88-92% di 3 tema tim** ✅.

**Skala bintang:**
- ⭐ = kriteria utama, tapi kode banyak diperbaiki / terindikasi plagiat
- ⭐⭐ = kriteria utama, tapi kode perlu diperbaiki
- ⭐⭐⭐ = **kriteria utama, tanpa saran** ← **TARGET UTAMA**
- ⭐⭐⭐⭐ = kriteria utama + min 3 saran
- ⭐⭐⭐⭐⭐ = kriteria utama + SEMUA 6 saran

**Saran (JANGAN semua dikejar — pilih yang MURAH saja):**
| Saran | Isi | Rencana Dafina | Alasan |
|---|---|---|---|
| 1 | Deep learning | ❌ SKIP | Butuh tensorflow/torch, waktu training lama. Over-engineer. |
| 2 | Train & test **>92%** | ❌ SKIP | SVM+TF-IDF di DANA belum tentu tembus 92% tanpa tuning. Risiko waktu. |
| 3 | ≥3 kelas | ✅ APPLY | Murah — labeling hybrid otomatis 3 kelas. |
| 4 | ≥10.000 sampel | 🟡 OPTIONAL | Scrape 6.500 dulu (aman). Kalau mau naikkan, target `{1:2rb, 2:1.5rb, 3:3rb, 4:1.5rb, 5:2rb}` ≈ 10rb. Murah — 5-10 menit tambah scrape. |
| 5 | 3 skema | ❌ SKIP | Butuh 2 model tambahan (mis. LR, RF, MultinomialNB) + hyper-tuning tiap skema. Effort tinggi. |
| 6 | Inference kategorikal + bukti | ✅ APPLY | Murah — 1 fungsi `predict(teks)` + 3-5 kalimat uji. |

> **Peta realistis:** dengan (3) + (6) diterapkan = **⭐⭐⭐** (karena hanya 2 saran; ⭐⭐⭐⭐ butuh min 3 saran). Kalau scrape naik ke ≥10rb → tambah saran (4) = **3 saran = ⭐⭐⭐⭐**. **Keputusan default:** tetap 6.500 dan ⭐⭐⭐, hemat waktu.

---

## 🧭 METODOLOGI (WARISAN sukses PLN/MyTelkomsel/Shopee, disederhanakan)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype ke **data asli** lewat script `.venv\Scripts\python.exe` (output prototype JANGAN masuk folder submission — pakai scratchpad `d:\tmp\` atau `%TEMP%`). Plot → simpan PNG ke `%TEMP%` lalu **lihat pakai Read tool**. **Selalu cek INFERENCE pada 3-5 kalimat asli**, bukan cuma test-accuracy.
2. **6 Tahap berurutan** (Tahap 0 → 6, bukan 8 seperti teman-teman), tuntaskan tiap tahap sebelum lanjut. Update checklist + progress log tiap tahap selesai.
3. **Output di-embed** via `jupyter nbconvert --execute --inplace` (kernel venv, cwd=folder submission), tanpa error.
4. **Privasi:** buang kolom identitas (`userName`, `userImage`); jangan tampilkan data pribadi di contoh ulasan.
5. **Reproducibility:** `SEED=42` di split & model. `class_weight='balanced'`.

---

## 🔑 CATATAN TEKNIS PENTING (pelajaran mahal dari tim — JANGAN diulangi)

### ⚠️ AGREEMENT / STRONG-DENOISE FILTER = TRAP (TIGA KALI TERJADI!)
- **Nazhif (PLN):** rating==lexicon → test 90% TAPI generalisasi 52% + inference SALAH. DITOLAK.
- **Fareynaldi (MyTelkomsel):** wajib-ada-kata-kamus → SVM test 95,5% TAPI keluhan implisit salah jadi netral. DITOLAK.
- **Bimo (Shopee):** cek eksplisit, tidak masuk trap.
- ✅ **Yang benar:** polar dari rating **murni** (⭐1=neg, ⭐5=pos, buang ⭐2 & ⭐4), netral=⭐3 dgn `|lex net|` rendah. Lexicon **hanya menyaring netral**, TIDAK menyentuh polar → tak ada bias. **Selalu cek inference sebelum percaya test accuracy.**

### ⚠️ NET-WEIGHT lexicon (WAJIB — bug fatal kalau salah)
InSet punya ~1.081-1.142 kata di **kedua** file (`inset_positive.tsv` & `inset_negative.tsv`) dgn bobot berlawanan (mis. `baik` +3/−1, `membantu` +4/−4, `cepat` +3/−3). Cara benar:
```python
net_weight = pos_dict.get(word, 0) + neg_dict.get(word, 0)
```
**JANGAN pakai `.update()`** — bikin bobot negatif menimpa positif → skor semua negatif → bug fatal.

### 📝 Domain-specific DANA (perhatian khusus)
- **Kosakata e-wallet:** `saldo, transfer, topup, tarik tunai, biaya admin, gagal, error, refund, promo, cashback, qris, kirim uang, isi saldo, biaya, potongan`.
- **Risiko utama:** keluhan tercampur **"aplikasi DANA" vs "biaya admin/potongan"**. Kata `biaya`/`potongan`/`admin` sering di ulasan ⭐1 (marah karena potongan biaya) — sentimen ke fitur/kebijakan, bukan app itu sendiri. Tapi untuk sentimen 3-kelas tidak masalah — model belajar polar keluhan → tetap masuk kelas negatif.
- **InSet lexicon di domain DANA:** kata `saldo`, `transfer`, `promo`, `admin` netral secara umum — kemungkinan kurang bising dibanding PLN (`mati listrik`). Verify dulu di Tahap 4.
- **Rating DANA di Play Store:** biasanya ~4,5+ (skew positif) — mirip pola Shopee/MyTelkomsel. Stratified per-bintang WAJIB.

### 🧵 Dua kolom teks (tetap dipakai, walau simple)
- `text_clean` = clean + normalisasi slang (**TANPA stem**) → untuk **scoring lexicon** (kata utuh cocok lexicon).
- `text_stemmed` = clean + slang + stopword + stem **Sastrawi** → untuk **TF-IDF/SVM**.
- Stem pakai **cache per-kata unik** (sekali saja, hemat waktu). Sastrawi ~1-2 menit untuk 6.500 baris (tolerable, tidak seperti PLN 55rb yang 13 menit).

### 🚧 Anti data-leak (basic — jangan skip)
- `train_test_split` **DULU**, baru `fit` TF-IDF di **train saja**, `transform` di test.
- Preprocessing teks umum (clean/slang/stem) boleh sebelum split — yang kritikal adalah **fit TfidfVectorizer**.

### 💡 Alasan pilih SVM+TF-IDF (bukan DL)
- **Bukti empiris tim:** SVM+TF-IDF selalu 88-92% di 3 tema tim — sudah lulus kriteria ≥85% dgn margin nyaman.
- **Cepat:** training <1 menit di CPU Victus (tidak butuh GPU).
- **Sederhana:** tidak ada tuning hyperparameter kompleks (default LinearSVC + `class_weight='balanced'` sudah cukup).
- **Reviewer familiar:** SVM+TF-IDF adalah baseline klasik yang selalu diterima.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Perencanaan & Setup: ✅ SELESAI (2026-07-15)**
  - **uv 0.11.28** sudah terpasang di user site-packages Windows (`C:\Users\Admin Kalachakra\AppData\Roaming\Python\Python311\Scripts\uv.exe`).
  - `.python-version` = `3.10`; venv dibuat via `uv venv .venv --python 3.10` → **Python 3.10.20** aktif.
  - Library minimal terpasang: `pandas 2.3.3, numpy 2.2.6, sklearn 1.7.2, google-play-scraper, Sastrawi, matplotlib, seaborn, wordcloud, jupyter, ipykernel, joblib, nbconvert`.
  - **Smoke test OK:** semua import lolos; Sastrawi `membantu → bantu`.
  - **Kernel Jupyter `dafina_dana`** terdaftar di `%APPDATA%\jupyter\kernels\dafina_dana`.
  - Lexicon disalin ke `submission/kamus/`: `inset_negative.tsv` (81 KB) + `inset_positive.tsv` (41 KB) + `slang_words.csv` (3 MB).
  - **Verify-first API DANA (`id.dana`) TERVERIFIKASI:**
    - Title: `DANA Dompet Digital Indonesia` · Score **4.6852** · Installs 100 jt+
    - Ratings **10.289.706** · Text reviews **2.318.030**
    - Histogram: ⭐1 **455.432 (4,4%)** · ⭐2 120.304 (1,2%) · ⭐3 **217.286 (2,1%)** · ⭐4 621.468 (6,0%) · ⭐5 **8.875.212 (86,3%)** → skew positif ekstrem (mirip Shopee/MyTelkomsel).
    - Semua bintang punya jauh > target 1.500 (⭐2 paling langka 120rb; ⭐5 dominan 8,9jt). Stratified aman.
  - **Sample per bintang inspeksi manual (3 tiap):** domain e-wallet jelas (`saldo, transfer, kirim uang, verifikasi, dana cicil, iklan, error, loading, jaringan, dana plus, akun, update, apk`). **⭐3 sarat keluhan** (login gagal, jaringan bermasalah) → netral murni langka → strict `|lex|=0` cocok. ⭐4 & ⭐5 bercampur (ada sarkastik & keluhan implisit) → tetap pakai rating-murni untuk polar tanpa denoise (batas bawah, jangan over-engineer).
- **Tahap 1 — Scraping: ✅ SELESAI (2026-07-15)** — `submission/scraping_dana.py` (stratified per bintang, sort NEWEST, privasi userName/userImage dibuang, docstring lengkap).
  - **Hasil: 6.500 ulasan unik** (persis target — 0 duplikat reviewId, 0 null di `content`/`score`/`reviewId`/`at`).
  - Distribusi: ⭐1: 1500 · ⭐2: 1000 · ⭐3: 1500 · ⭐4: 1000 · ⭐5: 1500 (persis PER_STAR).
  - **Rentang tanggal: 2026-05-30 → 2026-07-14** (~6 minggu, ulasan terkini).
  - Panjang teks median per bintang: ⭐1: 12 · ⭐2: 12 · ⭐3: 9 · ⭐4: 3 · ⭐5: 2 kata → **negatif lebih panjang** (marah detail), positif pendek (pujian "mantap"/"bagus") — pola konsisten dgn 3 tema tim.
  - CSV **2,13 MB** (jauh lebih ringan dari Shopee 21 MB — sesuai skala batas bawah). 9 kolom aman privasi.
  - Contoh ⭐1: "sangat mengecewakan. dana cicil..." | ⭐3: "sering bermasalah" | ⭐5: "sangat membantu dan mudah" — 3 kelas jelas.
- **Tahap 2 — EDA singkat: ✅ SELESAI (2026-07-15)** — 2 plot terverifikasi visual (bar chart distribusi bintang + wordcloud 2 kelas neg/pos). Top-words per kelas: NEG=`dana, saldo, apk, uang, cicil, padahal, akun, qris`; POS=`sangat, bagus, mantap, membantu, mudah, cepat`. Duplikat content 20,4% (tidak di-drop, konsisten pola tim).
- **Tahap 3 — Preprocessing: ✅ SELESAI (2026-07-15)** — pipeline clean → slang(4.330) → stopword(123) → Sastrawi stem dgn cache per-kata unik (5.017 kata unik, ~2,9 menit di CPU). Mean kata: text_clean 11,5 → text_stemmed 8,3. Kosong text_stemmed 177 baris (2,7%) — dibuang di label. Sample verifikasi manual OK (`bgt→banget, pdhl→padahal, sedetik→detik`).
- **Tahap 4 — Pelabelan BINARY: ✅ SELESAI (2026-07-15)** — **PIVOT ke binary** setelah verify-first sweep threshold gagal stabil.
  - Sempat coba `|lex|=0` strict-neutral (Nazhif pattern): SVM test 85,36% dgn seed 42, TAPI stabilitas 5-seed jelek (mean 83,36%, min 81,58% — di bawah 85% wajib!) → risiko cherry-pick tinggi.
  - Sweep threshold `|lex| ∈ {0,1,2,3,5}`: hanya `=0` yg lolos 85% (seed 42). Yg lain drop ke 79%-68%.
  - **FINAL BINARY:** ⭐1=negatif, ⭐5=positif; buang ⭐2/⭐3/⭐4. **2.909 sampel** (neg 1.498 / pos 1.411). Stabilitas 5-seed: **mean 88,90%, min 86,94%, std 1,71%** — semua >85% ✅.
  - Trade-off: kehilangan saran #3 (≥3 kelas), tapi bintang tetap ⭐⭐⭐ (saran #3 sendirian tidak cukup untuk ⭐⭐⭐⭐ yg butuh min 3 saran). Sesuai target batas bawah.
  - `submission/dataset_dana_labeled.csv` disimpan (0,71 MB, 8 kolom).
- **Tahap 5 — 1 Skema SVM+TF-IDF + Inference: ✅ SELESAI (2026-07-15)** — `submission/pelatihan_analisis_sentimen.ipynb` (27 sel, 14 code + 13 markdown, 0,52 MB).
  - Notebook di-generate via `nbformat` + di-execute via `jupyter nbconvert --execute --inplace` (kernel `dafina_dana`).
  - **Test Accuracy: 91,41%** ✅✅ (jauh di atas 85% wajib, margin ~6%).
  - Train Accuracy: 97,03%. F1-macro test: 91,38%. Config: `TfidfVectorizer(ngram=(1,2), max_features=20000, min_df=2)` + `LinearSVC(C=1.0, class_weight='balanced')` + split 80/20 anti-leak.
  - Classification report: neg P=0,896 R=0,943 F1=0,919 (300 support) · pos P=0,936 R=0,883 F1=0,909 (282 support) — seimbang.
  - Confusion matrix diagonal dominan: 283 TN / 17 FP / 33 FN / 249 TP.
  - Inference 8 kalimat DANA-domain: **7/8 masuk akal** (1 miss: "top up saldo lancar dan cashback" → negatif, kemungkinan bias kata "top" di training). Output kategorikal (`negatif`/`positif`) → saran #6 terpenuhi.
  - 3 plot embedded (distribusi + wordcloud + confusion matrix), 0 error, 16 total outputs.
- **Tahap 6 — Packaging: ✅ SELESAI (2026-07-15)** — `dafina/Proyek_Analisis_Sentimen_DANA_Dafina.zip` (**1,54 MB, 8 file dalam 1 folder root**).
  - Isi: 4 wajib (notebook `.ipynb`, `scraping_dana.py`, `requirements.txt`, `dataset_dana_reviews.csv`) + 1 pendukung (`dataset_dana_labeled.csv`) + 3 kamus (`inset_neg/pos.tsv`, `slang_words.csv`).
  - `requirements.txt` versi terverifikasi (11 paket, CPU-only, tanpa TF/PyTorch).
- **🏆 HASIL AKHIR: ⭐⭐⭐ (Pass)** — kriteria utama penuh:
  - ✅ K1 Scraping mandiri ≥3.000: **6.500 unik**
  - ✅ K2 Ekstraksi fitur (TF-IDF) + pelabelan (rating-binary)
  - ✅ K3 Algoritma ML: SVM (LinearSVC)
  - ✅ K4 Akurasi test ≥85%: **91,41%** (margin +6,41%)
  - Bonus saran #6 (inference kategorikal + bukti 8 kalimat) diterapkan — tidak cukup untuk naik bintang (butuh min 3 saran), tapi memperkuat kelayakan submission.
- **SISA: user upload zip ke Dicoding** (jangan submit berkali-kali; review ±3 hari kerja).
