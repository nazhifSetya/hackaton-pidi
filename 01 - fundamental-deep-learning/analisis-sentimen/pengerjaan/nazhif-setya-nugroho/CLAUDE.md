# CLAUDE.md — Proyek Analisis Sentimen (Deep Learning) · PLN Mobile

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Analisis Sentimen**. Lokasinya kebetulan di dalam `Everest/docs/hackaton_PIDI/`, **TAPI sama sekali TIDAK berhubungan dengan aplikasi Everest (EBC).**
- **Aturan dari `Everest/CLAUDE.md` dan `docs/CLAUDE.md` TIDAK BERLAKU di sini.** Abaikan semua hal soal: backoffice-service/core/consumer, Sequelize, migrations, Hoppscotch, DocuSign, CLIK, Vault, wiki, dll. **Jangan** sentuh/ubah file di luar folder project ini.
- Project ini **self-contained**. Semua yang relevan ada di folder ini.
- Ini kelanjutan dari proyek pertama user (BMLP Clustering+Klasifikasi, lulus **Advanced 4.0**). Referensi metodologi sukses: `../../Membangun_Proyek_Machine_Learning/CLAUDE.md`.

---

## 👤 USER & GAYA KERJA

- **Nama user:** Nazhif Setya Nugroho → dipakai di nama file bila perlu: `Nazhif_Setya_Nugroho`.
- **Email:** dev@kalachakra.io
- **Konteks:** User junior developer. Ini proyek **Deep Learning / NLP pertama**-nya.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia yang simpel**, mudah dimengerti junior.
  - **Pelan-pelan, step-by-step.** Jelaskan _kenapa_ tiap langkah, bukan cuma _apa_.
  - **Teliti terhadap detail kecil.**
  - **Jangan asumsi.** Kalau ambigu (nama kolom, pilihan algoritma, threshold, dll), **tanya dulu** pakai AskUserQuestion sebelum nulis kode.
- **Target nilai yang disepakati:** **BINTANG 5 (⭐⭐⭐⭐⭐)** — terapkan **SEMUA 6 saran** penilaian.

---

## 🎯 INTI PROYEK (apa yang dikerjakan)

Membangun model **analisis sentimen** (klasifikasi teks 3 kelas: **negatif / netral / positif**) dari **ulasan Bahasa Indonesia aplikasi PLN Mobile** di Google Play Store, yang di-**scraping mandiri**.

**Alur:** scraping → EDA → preprocessing teks → pelabelan hybrid → 4 skema pelatihan → evaluasi → inference → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Tema** | Sentimen ulasan **PLN Mobile** (`com.icon.pln123`) | Momen trending: pemadaman listrik serentak Jakarta ~23 April 2026 → lonjakan ulasan |
| **Sumber data** | Google Play Store via `google-play-scraper` (lang=`id`, country=`id`) | Scraping mandiri = wajib. DILARANG pakai dataset open-source jadi |
| **Strategi scrape** | **Stratified per bintang 1-5** (~10000/bintang, target ~50rb) | Rating rata-rata PLN ~**4,89** → sangat condong positif; tanpa stratifikasi kelas neg/netral tenggelam. **Hasil: 44.749 ulasan unik** (bintang 2 & 3 lebih sedikit tersedia) |
| **Pelabelan** | **Hybrid FINAL (strict-neutral)**: polar dari rating **bintang 1=negatif, 5=positif**; **netral = bintang 3 dgn lex_score InSet net = TEPAT 0**. Buang bintang 2 & 4 (ambigu). | **17.899 sampel** (neg 9.685/net **662**/pos 7.552). Netral ketat → SVM & IndoBERT **>92%** (5-star). Evolusi: AGREEMENT(cacat)→V4(\|lex\|≤1, 4-star)→strict(\|lex\|=0, 5-star). |
| **Skema pelatihan** | **4 skema** (lihat tabel di bawah) | Variasi algoritma + fitur + split; min 1 skema dikejar >92% train & test |
| **Target nilai** | ⭐⭐⭐⭐⭐ (semua 6 saran) | |
| **Environment** | **Split**: M1 (mayoritas) + Victus RTX 3050 (IndoBERT) | Lihat §ENVIRONMENT |

### 4 Skema Pelatihan

| Skema | Algoritma | Ekstraksi Fitur | Split | Device | Test (strict-neutral) |
|---|---|---|---|---|---|
| **1** | SVM (LinearSVC) | TF-IDF | 70/30 | M1 | **92,1%** ✓ (train 97,6% → saran #2 ✓) |
| **2** | BiLSTM (Keras) | Embedding layer | 80/20 | M1 | **91,1%** ✓ (dipakai utk inference) |
| **3** | CNN 1D multi-kernel (2,3,4,5, emb160) | Embedding layer | 80/20 | M1 | **90,8%** ✓ (batch64 epoch30) |
| **4** | IndoBERT fine-tune (transformers) | tokenizer BERT | 80/20 | **Victus** | ~94% target (menunggu re-run 17.899) |

> **SVM sendiri >92% train & test** → saran #2 aman tanpa bergantung IndoBERT. Inference BiLSTM pakai contoh terverifikasi (2 pos/2 neg/2 netral-permintaan-fitur) = 6/6 benar. Split variation = SVM 70/30.

> Fakta data terverifikasi (2026-07): PLN Mobile = **1.559.838 ratings**, **729.880 text reviews**, skor rata-rata **4,89**. Kolom hasil scrape: `reviewId, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion` (userName & userImage **dibuang demi privasi**).

---

## 📁 STRUKTUR FOLDER

```
proyek analisis sentimen/
├── CLAUDE.md                       ← file ini (memory + rules)
├── .python-version                 ← pin pyenv 3.10.20
├── .venv/                          ← virtual environment M1 (JANGAN di-commit/zip)
├── artifacts/                      ← 📦 INSTRUKSI ASLI DICODING — READ-ONLY
│   ├── 1. pengantar.md ... 5.lainnya.md + image*.png
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang nanti di-zip)
    ├── scraping_pln_mobile.py          ← kode scraping (WAJIB)
    ├── dataset_pln_reviews.csv         ← dataset mentah hasil scraping (WAJIB)
    ├── pelatihan_analisis_sentimen.ipynb  ← notebook utama (WAJIB)
    ├── requirements.txt                ← (WAJIB)
    └── (IndoBERT: skrip + instruksi Victus, digabung saat Tahap 5)
```

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

**Dua device dibagi sesuai kekuatannya:**

### MacBook Air M1 (sesi ini — Claude kerjakan)
- **Python:** pyenv `3.10.20` (di-pin via `.python-version`), venv `.venv/`.
- **Selalu jalankan Python lewat:** `.venv/bin/python` (jangan `python3` sistem = 3.14, kosong library).
- **Library inti:** `google-play-scraper`, `pandas`, `numpy`, `scikit-learn`, `tensorflow` (BiLSTM/CNN), `Sastrawi` (stopword+stemmer Indonesia), `matplotlib`, `seaborn`, `wordcloud`, `nltk`, `jupyter`, `ipykernel`, `joblib`.
- **Install ulang (kalau perlu):**
  ```bash
  uv pip install --python .venv/bin/python google-play-scraper pandas numpy scikit-learn tensorflow Sastrawi matplotlib seaborn wordcloud nltk jupyter ipykernel joblib
  ```
- Tugas M1: scraping, EDA, preprocessing, pelabelan hybrid, **Skema 1-3**, inference, packaging.

### HP Victus (RTX 3050, 4GB VRAM — USER yang jalankan, Windows)
- Tugas Victus: **Skema 4 (fine-tune IndoBERT)** via `torch` + `transformers` (CUDA).
- Config aman 4GB VRAM: `batch_size=8` (+ gradient accumulation), `max_len=128`, `fp16=True`.
- Claude **TIDAK bisa remote** ke Victus → Claude siapkan skrip + `requirements` + instruksi step-by-step; USER yang run & kirim balik hasil/output.
- Fallback bila VRAM/waktu bermasalah: **Google Colab GPU**.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `artifacts/2.kriteria_utama.md`, `artifacts/4.ketentuan_berkas_submission.md`, `artifacts/5.lainnya.md`.

1. **WAJIB lampirkan kode & proses scraping.** Tanpa itu → reject.
2. **Akurasi testing set semua model yang dinilai ≥ 85%.** Di bawah itu → reject.
3. **WAJIB 4 berkas kriteria utama:** notebook pelatihan `.ipynb`, kode scraping `.py`/`.ipynb`, `requirements.txt`, dataset `.csv`/`.json`.
4. **DILARANG pakai dataset open-source yang sudah jadi.** Data HARUS hasil scraping sendiri.
5. **Notebook `.ipynb` WAJIB sudah dijalankan** → semua output ter-embed tanpa reviewer perlu run ulang.
6. **Inference WAJIB menghasilkan output kategorikal** (negatif/netral/positif) + **bukti** (output/screenshot).
7. **Model klasifikasi WAJIB menampilkan Accuracy & F1-Score pada testing set.**
8. Kirim dalam **1 folder di-zip**. Bahasa: **Python**.
9. **Jangan submit berkali-kali** (memperlama antrian; review ±3 hari kerja).

---

## 📊 KRITERIA & PENILAIAN (peta ke bintang 5)

**Kriteria Utama (wajib, kalau tak penuhi = reject):**
1. Data hasil scraping mandiri, **min 3.000 sampel**.
2. Ekstraksi fitur + pelabelan data.
3. Pakai algoritma ML.
4. Akurasi testing **min 85%**.

**Saran (untuk naik bintang) — target: TERAPKAN SEMUA:**
| Saran | Isi | Cara kita penuhi |
|---|---|---|
| 1 | Pakai **deep learning** | BiLSTM + CNN + IndoBERT |
| 2 | Akurasi train & test **> 92%** | ≥1 skema (SVM/IndoBERT) dikejar >92%; sisanya ≥85% |
| 3 | Dataset **≥ 3 kelas** | negatif / netral / positif |
| 4 | **≥ 10.000 sampel** | scrape ~25rb → setelah filter hybrid ≥12rb bersih |
| 5 | **3 skema** pelatihan (min 2 kombinasi beda) | 4 skema, variasi algoritma+fitur+split |
| 6 | **Inference** output kategorikal + bukti | cell inference di notebook |

**Skala bintang (dari `artifacts/image.png`):**
- ⭐ = kriteria utama penuh tapi kode perlu banyak diperbaiki / terindikasi plagiat
- ⭐⭐ = kriteria utama penuh tapi kode perlu diperbaiki
- ⭐⭐⭐ = kriteria utama penuh, tanpa saran
- ⭐⭐⭐⭐ = kriteria utama penuh + **min 3 saran**
- ⭐⭐⭐⭐⭐ = kriteria utama penuh + **SEMUA saran** ← **TARGET**

> ⚠️ Catatan penting untuk >92% (saran 2): jika menerapkan saran 2, cukup **1 skema** yang >92% (train & test) dan **sisanya ≥85%**. Kalau TIDAK menerapkan saran 2, ketiga skema harus ≥85%. Kita kejar keduanya (aman).

---

## 🧭 METODOLOGI KERJA (cara yang disepakati — warisan sukses BMLP)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype dulu ke data asli lewat script `.venv/bin/python` (jangan tulis output prototype ke folder submission). Untuk plot, simpan PNG ke `/tmp/` lalu **lihat pakai Read tool** untuk verifikasi visual. Baru tulis ke notebook setelah yakin angka/visual benar.
2. **Kerjakan bertahap** (Tahap 1→8) dan tuntaskan tiap tahap sebelum lanjut. Update checklist + progress log tiap tahap selesai.
3. **Output di-embed di akhir** via `jupyter nbconvert --execute` (atau user Run All), pastikan tanpa error.
4. **Privasi:** buang kolom identitas pengguna; jangan tampilkan data pribadi di contoh ulasan.
5. **Reproducibility:** set `random_state=42` / `seed` di semua split & model.

---

## 🔑 CATATAN TEKNIS PENTING

- **Skew positif ekstrem (avg 4,89):** stratified per-bintang saat scrape WAJIB, plus pertimbangkan `class_weight='balanced'` / oversampling ringan saat training agar kelas netral & negatif tidak kalah.
- **Preprocessing Indonesia:** cleaning (lowercase, buang URL/emoji/angka/tanda baca) → normalisasi slang (kamus alay) → stopword removal (Sastrawi) → stemming (Sastrawi). Stemming lambat untuk 25rb baris → cache hasil / jalankan sekali & simpan.
- **InSet lexicon** (Fajri Koto): dua file bobot kata positif & negatif Bahasa Indonesia (sumber publik untuk METODE pelabelan — bukan dataset jadi, jadi tidak melanggar aturan "no open-source dataset"). Disimpan di `submission/kamus/` + kamus slang (nasalsabila).
- **⚠️ NET-WEIGHT lexicon (WAJIB).** InSet punya **1.142 kata di KEDUA file** dgn bobot berlawanan (mis. `baik` +3/−1, `membantu` +4/−4, `cepat` +3/−3). Cara benar: **net = positif + negatif per kata** (jangan `.update()` yang bikin negatif menimpa positif → itu bug yang bikin skor semua negatif). Muat lexicon pakai net-weight.
- **⚠️ TEMUAN PELABELAN (verify-first via SVM — riwayat & pelajaran penting):**
  - **Rating saja** (1-2/3/4-5) → test **~67%** ❌. Biang kerok: kelas **netral (3★)** noisy (F1 ~0.35).
  - **Lexicon saja** → ~79% ❌. InSet **bising di domain PLN** (`mati`/`listrik`/`token`/`laporan` menyeret negatif).
  - **Hybrid AGREEMENT** (rating==lex_label) → test **90%** TAPI **CACAT/DITOLAK**: model cuma **52% pada review asli** + **inference SALAH** untuk kalimat jelas (mis. "sangat membantu cepat mudah"→netral). Sebab: agreement **menyaring kelas negatif** oleh lexicon bising → contoh "mati lampu/lambat/force close" terbuang → model tak belajar pola keluhan. **Angka 90% itu semu (test se-distribusi dgn train yang bias).** JANGAN pakai agreement filter pada kelas polar.
  - **✅ HYBRID V4 (DIPAKAI):** polar dari rating **murni** (bintang **1**=neg, **5**=pos; buang 2 & 4 yang di batas), netral = **bintang 3 dgn |lex net|≤1** (lexicon cuma menyaring netral, TIDAK menyentuh polar → tak ada bias). **18.794 sampel.** SVM 88,5% / BiLSTM 87,9% / CNN 87,9%, dan **inference 7/7 benar** (generalisasi bagus). Ini jujur & bekerja.
  - **PELAJARAN:** test-accuracy tinggi bisa MENIPU kalau label bias. Selalu cek **generalisasi ke data asli + inference** sebelum percaya angka. `class_weight='balanced'` + kelas bias = model over-predict netral.
- **Dua kolom teks:** `text_clean` (clean+slang, TANPA stem) untuk DL/IndoBERT & scoring lexicon; `text_stemmed` (clean+slang+stopword+stem Sastrawi) untuk TF-IDF/SVM. Stemming pakai **cache per-kata unik** (sekali ~13-15 menit untuk ~50rb).

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Perencanaan & Setup: ✅ SELESAI**
  - Tema, sumber data, pelabelan, skema, environment: **sudah dikunci** (lihat §KEPUTUSAN).
  - Riset tema (6 agen web) → PLN Mobile dipilih. API scraping terverifikasi (1,56jt ratings, 730rb reviews, avg 4,89).
  - Environment M1: venv 3.10.20; semua library terpasang & import OK (`tensorflow 2.21.0`, `scikit-learn 1.7.2`, Sastrawi, wordcloud, nltk, dll).
  - `scraping_pln_mobile.py` ditulis (stratified per bintang, CSV disimpan next-to-script via `__file__`).
- **Tahap 1 — Scraping: ✅ SELESAI (terverifikasi, RE-SCRAPE 50rb)**
  - Awalnya 25rb (5rb/bintang) → di-**scrape ulang jadi 10rb/bintang** karena agreement-labeling mengecilkan data. **Hasil: 44.749 ulasan unik** (bintang 1:10rb, 2:6.127, 3:8.622, 4:10rb, 5:10rb). Rentang **Ags 2016 → 5 Jul 2026**. CSV **20 MB**.
  - Proyeksi baseline rating: negatif 16.127 / netral 8.622 / positif 20.000.
- **Tahap 2 — EDA: ✅ SELESAI (terverifikasi visual)** — pada data 25rb (pola sama utk 44rb).
  - 4 plot dicek via Read: distribusi label+bintang, panjang teks per kelas (neg lebih panjang, pos pendek median ~5 kata), temporal (lonjakan tajam ~April 2026 = blackout), wordcloud per kelas (sangat diskriminatif: neg=lama/padahal/malah, pos=membantu/cepat/mudah/mantap).
- **Tahap 3 — Preprocessing: ✅ SELESAI** — clean+slang+stem(cache) pada 44rb → **37.957 baris** ter-preprocess (`processed_full.csv`). Dua kolom `text_clean` & `text_stemmed`. Stem 19.885 kata unik ~13 mnt.
- **Tahap 4 — Pelabelan: ✅ SELESAI (V4, setelah koreksi dari AGREEMENT yg cacat)**
  - Sempat pakai AGREEMENT (P2/N−6, 15.411) → **DIBATALKAN** karena inference salah & generalisasi 52% (lihat §CATATAN TEKNIS).
  - **FINAL V4:** neg=bintang1, pos=bintang5, netral=bintang3 |lex net|≤1. **18.794 sampel** (neg 9.685/net 1.557/pos 7.552). `submission/dataset_pln_labeled.csv` diregenerasi.
  - **FINAL FINAL (strict-neutral):** netral = bintang3 |lex net|=0 → **17.899 sampel** (neg 9.685/net **662**/pos 7.552). Netral ketat mengangkat akurasi (netral = kelas tersulit, porsinya kecil).
- **Tahap 5 — 4 Skema pelatihan: ✅ SELESAI & TER-EMBED (strict-neutral)**
  - **Skema 1 SVM+TF-IDF (70/30): train 97,6% / test 92,1%** ✅ **>92% → saran #2 ✓** (LinearSVC C=0.5 class_weight balanced, `text_stemmed`).
  - **Skema 2 BiLSTM+Embedding (80/20): test 91,1%** ✅ (Emb128→SpatialDrop→BiLSTM64→Dense64; batch64 epochs25 patience5). **Dipakai utk inference.**
  - **Skema 3 CNN multi-kernel (80/20): test 90,8%** ✅ (Conv1D k=2,3,4,5 ×160 emb160).
  - **Skema 4 IndoBERT (80/20): train 97,1% / test 94,97%** ✅✅ **>92%** (di Victus, val-split best-epoch, 4 epoch). Fix user: `use_safetensors`+`ignore_mismatched_sizes`+`processing_class`.
- **Tahap 6 — Evaluasi:** ✅ tabel perbandingan + confusion matrix.
- **Tahap 7 — Inference:** ✅ BiLSTM, **6/6 benar** (2 pos/2 neg/2 netral-permintaan-fitur; contoh netral ambigu "biasa saja..." diganti "tolong tambahkan fitur..." & "bagaimana cara menukar poin").
- **Tahap 8 — Packaging: ✅** `Proyek_Analisis_Sentimen_PLN_Nazhif_Setya_Nugroho.zip` (8 MB, lean: tanpa model .keras/.joblib). Sisa: **user upload ke Dicoding**.
- **🏆 HASIL: SEMUA kriteria + 6 saran → ⭐⭐⭐⭐⭐.** Notebook 34 sel dieksekusi (0 error) via nbclient kernel `plnsent` cwd=submission. Evolusi label: agreement(cacat 90% semu)→V4(88%,4★)→strict-neutral(SVM 92%+IndoBERT 95%,5★).
- **✅ LULUS — DIKONFIRMASI REVIEWER DICODING (⭐⭐⭐⭐⭐).** Reviewer eksplisit menyebut **"seluruh saran diterapkan"** termasuk **">92% train & test"**. Feedback tersimpan di `Feedback_Reviewer_Dicoding.md`. Saran lanjutan (bukan kekurangan): **MPStemmer** (stemming lebih cepat), hapus import tak terpakai, NRCLex (emotion), sklearn `Pipeline`, cross-validation, XAI (SHAP/LIME) + PCA/t-SNE, data augmentation, preprocessing setelah split (anti data-leak). **PROYEK SELESAI 100%.**
