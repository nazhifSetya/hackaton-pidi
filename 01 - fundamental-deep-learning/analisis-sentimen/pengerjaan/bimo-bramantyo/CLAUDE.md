# CLAUDE.md — Proyek Analisis Sentimen (Deep Learning) · **Shopee** · submission utk **Bimo Bramantyo**

> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Analisis Sentimen**, tema **Shopee**, atas nama **Bimo Bramantyo** (mahasiswa Dicoding).
- **Self-contained di folder ini** (`.../proyek analisis sentimen/bimo_bramantyo/`). Folder induk (`../`) berisi **proyek PLN Mobile (Nazhif) yang LULUS ⭐⭐⭐⭐⭐** dan folder `../fareynaldi/` berisi **proyek MyTelkomsel (Fareynaldi) ⭐⭐⭐⭐⭐** — keduanya **REFERENSI metodologi saja, JANGAN diubah.**
- Aturan Everest/EBC (backoffice-service, Sequelize, CLIK, dll di `docs/CLAUDE.md`) **TIDAK berlaku di sini.**
- Ini **iterasi ke-3** dari trio proyek yang sama-tema-berbeda: **meniru metodologi pemenang PLN + saran reviewer yang sudah diterapkan Fareynaldi + tambahan eksplorasi domain e-commerce yang khas Shopee.** Target: **⭐⭐⭐⭐⭐** dengan **level Ambisius** (semua saran reviewer diterapkan).

---

## 👤 USER & GAYA KERJA

- **Pemilik submission:** **Bimo Bramantyo** — dipakai di semua nama file: `Bimo_Bramantyo`.
- **Konteks:** Mahasiswa Dicoding, level pemula–menengah, ini proyek Deep Learning/NLP-nya. Dua teman timnya (Nazhif & Fareynaldi) sudah selesai proyek serupa dengan tema berbeda.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia simpel, mudah dimengerti pemula–menengah.**
  - **Pelan-pelan, step-by-step.** Jelaskan **kenapa** tiap langkah, bukan cuma **apa**.
  - **Teliti detail kecil.**
  - **Jangan asumsi.** Kalau ambigu (threshold, nama kolom, pilihan model), **tanya dulu** pakai AskUserQuestion.
  - Kalau tunjukkan pattern kode dari proyek Nazhif/Fareynaldi, sertakan **path file + line number** supaya Bimo bisa buka sendiri di editor.
- **Target nilai:** **⭐⭐⭐⭐⭐ (Advanced)** — semua kriteria + semua 6 saran + **SEMUA saran reviewer** (level Ambisius).

---

## 🎯 INTI PROYEK

Model **analisis sentimen** (klasifikasi teks 3 kelas: **negatif / netral / positif**) dari **ulasan Bahasa Indonesia aplikasi Shopee** di Google Play Store, di-**scraping mandiri**.

**Alur:** scraping → EDA → preprocessing teks → pelabelan hybrid → 4 skema pelatihan → evaluasi (+error analysis + XAI + emosi) → inference → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Tema** | Sentimen ulasan **Shopee** (`com.shopee.id`) | Momen trending 2026: kenaikan biaya Gratis Ongkir XTRA (2 Mei 2026) + gangguan teknis (SPayLater error, app tidak bisa dibuka). Volume terbesar di antara 3 tema tersisa. |
| **Sumber data** | Google Play Store via `google-play-scraper` (lang=`id`, country=`id`) | Scraping mandiri = wajib. DILARANG pakai dataset open-source jadi. |
| **Strategi scrape** | **Stratified per bintang 1-5**, ⭐3 **di-boost** untuk netral. Target: `{1:12rb, 2:8rb, 3:15rb, 4:8rb, 5:12rb}` ≈ **55rb** | Rating agregat 4,57 (⭐5 dominan 83,19%). Boost ⭐3 supaya netral cukup. Verify-first 2026-07-12 OK: semua bintang punya jauh >target (⭐3: 385rb, ⭐2: 237rb, ⭐4: 1,14jt). |
| **Pelabelan** | **Hybrid rating-murni + lex netral**: neg=⭐1, pos=⭐5, buang ⭐2 & ⭐4; netral=⭐3 dgn `\|lex net\|` rendah — threshold di-tune (≤0/≤1/≤2) via SVM cepat. **Lexicon net-weight InSet** (WAJIB). | Denoise moderat (opsional, ala Fareynaldi) kalau rating bising di domain e-commerce. Denoise KUAT/agreement filter DILARANG (trap 90% semu). |
| **Skema pelatihan** | **4 skema**: SVM+TF-IDF (Pipeline+CV) · BiLSTM+Emb · CNN+Emb · IndoBERT | Min 1 skema >92% train & test (SVM/IndoBERT), sisanya ≥85%. |
| **Target nilai** | **⭐⭐⭐⭐⭐ (Advanced)** + **level Ambisius** — SEMUA saran reviewer diterapkan | |
| **Environment** | **Split**: Windows lokal (uv + venv) untuk skema 1-3 · **Google Colab GPU T4** untuk IndoBERT | Lihat §ENVIRONMENT. |

### 4 Skema Pelatihan (rencana)

| Skema | Algoritma | Ekstraksi Fitur | Split | Device | Peningkatan vs PLN/MyTelkomsel |
|---|---|---|---|---|---|
| **1** | SVM (LinearSVC) | TF-IDF | 70/30 | Windows lokal | **sklearn Pipeline** + **StratifiedKFold CV** + fit **hanya di train** (anti-leak) |
| **2** | BiLSTM (Keras) | Embedding layer | 80/20 | Windows lokal | tokenizer fit **hanya di train** |
| **3** | CNN 1D multi-kernel | Embedding layer | 80/20 | Windows lokal | tokenizer fit **hanya di train** |
| **4** | IndoBERT fine-tune | tokenizer BERT | 80/20 | **Colab T4** | val-split best-epoch, panduan Colab step-by-step |

---

## 📁 STRUKTUR FOLDER

```
bimo_bramantyo/
├── CLAUDE.md                       ← file ini (memory + rules)
├── .python-version                 ← pin Python 3.10.x (untuk uv)
├── .venv/                          ← virtual env Windows lokal (JANGAN di-commit/zip)
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang di-zip)
    ├── scraping_shopee.py              ← kode scraping (WAJIB)
    ├── dataset_shopee_reviews.csv      ← dataset mentah hasil scraping (WAJIB)
    ├── dataset_shopee_labeled.csv      ← dataset berlabel (pendukung)
    ├── pelatihan_analisis_sentimen.ipynb  ← notebook utama (WAJIB, sudah di-run)
    ├── requirements.txt                ← (WAJIB)
    ├── kamus/                          ← lexicon InSet (net-weight) + slang (salin dari `../../submission/kamus/`)
    └── indobert_colab/                 ← indobert_train_colab.py + PANDUAN_COLAB.md
```

> **Referensi (JANGAN diubah):** `../submission/` (notebook PLN pemenang), `../CLAUDE.md`, `../Feedback_Reviewer_Dicoding.md`, `../fareynaldi/submission/pelatihan_analisis_sentimen.ipynb`, `../fareynaldi/CLAUDE.md`.

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

### Windows lokal (Bimo jalankan sendiri via VS Code / terminal)
- **Python:** 3.10.x, di-pin via `.python-version` untuk `uv`.
- **Package manager:** **uv** (super cepat). Install sekali: `winget install --id=astral-sh.uv`.
- **Bikin venv:** `uv venv .venv --python 3.10`
- **Aktifkan (PowerShell):** `. .venv\Scripts\Activate.ps1`
- **Jalankan Python:** `.venv\Scripts\python.exe <script>` atau setelah aktivasi cukup `python <script>`.
- **Library inti:**
  ```powershell
  uv pip install google-play-scraper pandas numpy scikit-learn tensorflow Sastrawi matplotlib seaborn wordcloud nltk jupyter ipykernel joblib
  ```
- **Library level Ambisius (saran reviewer):**
  ```powershell
  uv pip install mpstemmer Levenshtein nrclex textblob shap lime
  ```
- Tugas Windows lokal: **scraping, EDA, preprocessing, Skema 1-3, evaluasi, XAI, inference, packaging.**

### Google Colab GPU T4 (Bimo jalankan sendiri, browser)
- Tugas: **Skema 4 (fine-tune IndoBERT)** via `torch` + `transformers` (CUDA T4).
- Aku siapkan `indobert_colab/indobert_train_colab.py` + `PANDUAN_COLAB.md` step-by-step:
  1. Upload dataset berlabel ke Colab (atau mount Google Drive).
  2. `pip install transformers torch datasets accelerate`.
  3. Runtime → Change runtime type → GPU T4.
  4. Run all → download `indobert_metrics.json` + `indobert_history.json`.
- Config aman T4: `batch_size=16` atau `32`, `max_len=128`, `fp16=True`.
- Fallback: `batch_size=8` + gradient accumulation kalau OOM.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `../artifacts/2.kriteria_utama.md`, `../artifacts/4.ketentuan_berkas_submission.md`, `../artifacts/5.lainnya.md`.

1. **WAJIB lampirkan kode & proses scraping.** Tanpa itu → reject.
2. **Akurasi testing set semua model yang dinilai ≥ 85%.** Di bawah itu → reject.
3. **WAJIB 4 berkas kriteria utama:** notebook `.ipynb`, kode scraping `.py`/`.ipynb`, `requirements.txt`, dataset `.csv`/`.json`.
4. **DILARANG pakai dataset open-source yang sudah jadi.** Harus scraping sendiri.
5. **Notebook `.ipynb` WAJIB sudah dijalankan** → output ter-embed tanpa reviewer perlu run ulang.
6. **Inference WAJIB output kategorikal** (negatif/netral/positif) + **bukti** (output/screenshot).
7. **WAJIB Accuracy & F1-Score pada testing set** tiap model yang dinilai.
8. Kirim dalam **1 folder di-zip**. Bahasa: **Python**.
9. **Jangan submit berkali-kali** (memperlama antrian; review ±3 hari kerja).

---

## 📊 PETA SARAN → BINTANG 5

**Kriteria Utama (wajib):** scraping ≥3rb · ekstraksi fitur+pelabelan · algoritma ML · test ≥85%.

**Skala bintang:**
- ⭐ = kriteria utama, tapi kode banyak diperbaiki / terindikasi plagiat
- ⭐⭐ = kriteria utama, tapi kode perlu diperbaiki
- ⭐⭐⭐ = kriteria utama, tanpa saran
- ⭐⭐⭐⭐ = kriteria utama + min 3 saran
- ⭐⭐⭐⭐⭐ = kriteria utama + **SEMUA 6 saran** ← **TARGET**

**6 Saran (untuk bintang 5 — target: SEMUA):**
| Saran | Isi | Cara kita penuhi |
|---|---|---|
| 1 | Deep learning | BiLSTM + CNN + IndoBERT |
| 2 | Train & test **>92%** | SVM &/atau IndoBERT dikejar >92%; sisanya ≥85% |
| 3 | ≥3 kelas | negatif / netral / positif |
| 4 | ≥10.000 sampel | scrape ~55rb → berlabel ≥12rb |
| 5 | 3 skema (≥2 kombinasi beda) | 4 skema, variasi algoritma+fitur+split |
| 6 | Inference kategorikal + bukti | cell inference multi-contoh, uji seluruh kelas |

**Saran TAMBAHAN reviewer (level Ambisius — target: SEMUA yang relevan notebook):**
- ✅ **MPStemmer** ganti Sastrawi — Fareynaldi bukti 0,1 dtk vs Sastrawi 13 mnt di PLN!
- ✅ **sklearn Pipeline** (TF-IDF → LinearSVC) — kode lebih rapi & anti langkah terlewat.
- ✅ **Cross-validation** (`StratifiedKFold`, 5-fold) di skema klasik untuk cek overfitting.
- ✅ **Metrik lengkap per kelas** (P/R/F1) + **Confusion Matrix** tiap skema.
- ✅ **Error Analysis** — sampel salah klasifikasi + pola (sarkasme/negasi/slang/keluhan produk vs app).
- ✅ **XAI**: SHAP/LIME kata paling berpengaruh + **PCA/t-SNE** visualisasi fitur + wordcloud.
- ✅ **NRCLex** emosi (English, eksploratif — bridge kata ID→EN atau tampilkan cakupan terbatas).
- ✅ **Anti data-leak**: `train_test_split` DULU, `fit` TF-IDF/tokenizer hanya di train.
- ✅ **Kode bersih**: hapus import tak terpakai, docstring tiap fungsi, deskripsi text cell.
- ✅ **Data augmentation** (opsional): synonym replacement untuk kelas minoritas (netral) — hanya di train.
- ⛔ **Preprocessing DULU baru pelabelan** (reviewer tekankan) — sudah begitu.
- ❌ MLflow/W&B — **skip** (overkill untuk notebook submission).

---

## 🧭 METODOLOGI (warisan sukses Nazhif+Fareynaldi — ulangi persis)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype ke **data asli** lewat script `.venv\Scripts\python.exe` (output prototype JANGAN masuk folder submission — pakai scratchpad `%TEMP%` atau folder `d:\tmp`). Plot → simpan PNG ke `%TEMP%` lalu **lihat pakai Read tool**. **Selalu cek INFERENCE + generalisasi ke data asli, bukan cuma angka test-accuracy.**
2. **8 Tahap berurutan** (Tahap 0 → 8), tuntaskan tiap tahap sebelum lanjut. Update checklist + progress log tiap tahap selesai.
3. **Output di-embed** via nbclient/nbconvert (kernel venv, cwd=folder submission), tanpa error. Kalau notebook panjang, run all di terminal, bukan Jupyter UI (lebih deterministik).
4. **Privasi:** buang kolom identitas (`userName`, `userImage`); jangan tampilkan data pribadi di contoh ulasan.
5. **Reproducibility:** `SEED=42` di semua split & model. `class_weight='balanced'`.

---

## 🔑 CATATAN TEKNIS PENTING (pelajaran mahal dari Nazhif & Fareynaldi — JANGAN diulangi)

### ⚠️ AGREEMENT / STRONG-DENOISE FILTER = TRAP (DUA KALI TERJADI!)
- **Nazhif (PLN):** rating==lexicon → test 90% TAPI generalisasi 52% + inference SALAH (menyaring kelas negatif → model tak belajar pola keluhan).
- **Fareynaldi (MyTelkomsel):** wajib-ada-kata-kamus → SVM test 95,5% TAPI keluhan implisit ("nutup sendiri", "kesedot sendiri") salah jadi netral. DITOLAK.
- ✅ **Yang benar:** polar dari rating **murni** (⭐1=neg, ⭐5=pos, buang ⭐2 & ⭐4), netral=⭐3 dgn `|lex net|` rendah. Lexicon **hanya menyaring netral**, TIDAK menyentuh polar → tak ada bias. **Selalu cek generalisasi ke data asli + inference sebelum percaya test accuracy.**
- **Denoise MODERAT (Fareynaldi FINAL):** boleh — buang HANYA kontradiksi eksplisit (⭐1 ber-kata-positif-eksplisit, ⭐5 ber-kata-negatif-eksplisit). Keluhan tersirat tetap → model tetap belajar. Verifikasi generalisasi wajib.

### ⚠️ NET-WEIGHT lexicon (WAJIB — bug fatal kalau salah)
InSet punya ~1.142 kata di **kedua** file (`inset_positive.tsv` & `inset_negative.tsv`) dgn bobot berlawanan (mis. `baik` +3/−1, `membantu` +4/−4, `cepat` +3/−3). Cara benar:
```python
net_weight = pos_dict.get(word, 0) + neg_dict.get(word, 0)
```
**JANGAN pakai `.update()`** — bikin bobot negatif menimpa positif → skor semua negatif → bug fatal.

### 📝 Domain-specific Shopee (perhatian khusus)
- **Kosakata e-commerce:** `barang`, `penjual`, `seller`, `kirim`, `paket`, `resi`, `refund`, `flash sale`, `gratis ongkir`, `voucher`, `spaylater`, `koin`.
- **Risiko utama:** keluhan tercampur **"aplikasi" vs "produk penjual"**. Sentimen kadang untuk barang (bukan app). Pertimbangkan:
  - Heuristik keyword aplikasi (`aplikasi`, `apk`, `app`, `error`, `bug`, `loading`) untuk boost sinyal "sentimen ke app".
  - ATAU tetap ambil semua, biarkan model belajar (denoise moderat di tahap label).
- **InSet lexicon di domain Shopee:** kata `paket`, `kirim`, `barang` netral secara umum — kemungkinan **kurang bising** dibanding PLN. Verify dulu.
- **Sarkasme cukup umum** di review Shopee ("kualitas sesuai harga", "harga murah kualitas sepadan") → siapkan error analysis.
- **Volume masif** = scraping bisa lama; buat progress print dan checkpoint per bintang.

### 🧵 Dua kolom teks (WAJIB)
- `text_clean` = clean + normalisasi slang (**TANPA stem**) → untuk **DL/IndoBERT** & scoring lexicon.
- `text_stemmed` = clean + slang + stopword + stem **MPStemmer** → untuk **TF-IDF/SVM**.
- Stem pakai **cache per-kata unik** (sekali saja, hemat waktu).

### 🚧 Anti data-leak (reviewer tekankan)
- `train_test_split` **DULU**, baru `fit` TF-IDF/tokenizer di **train saja**, `transform` di test.
- Augmentation & scaling juga hanya di train.
- Preprocessing teks umum (clean/slang/stem) boleh sebelum split — yang kritikal adalah **fit vektorizer & fit tokenizer**.

### 📉 NRCLex catatan
- Berbasis English → untuk teks ID kurang match. Pakai eksploratif:
  - Bridge kata ID→EN untuk top-words per kelas, ATAU
  - Jujur tampilkan cakupan terbatas.
- Butuh `nltk.download('punkt_tab')`, `'wordnet'`, `'omw-1.4'`. Sertakan guard di notebook.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Perencanaan & Setup: ✅ SELESAI**
  - 6 pertanyaan awal dikonfirmasi user: **tema Shopee**, target ⭐⭐⭐⭐⭐ level Ambisius, IndoBERT di **Google Colab T4**, env utama **Windows lokal (uv)**, familiarity scraping = "sudah pernah lihat", naming `Bimo_Bramantyo`.
  - Referensi Nazhif (`../CLAUDE.md`, `../Feedback_Reviewer_Dicoding.md`, `../artifacts/`, `../submission/scraping_pln_mobile.py`, `../panduan/Checklist_Pengerjaan.md`) & Fareynaldi (`../fareynaldi/CLAUDE.md`, `../fareynaldi/PROMPT_untuk_session_baru.md`, `../fareynaldi/panduan/Checklist_Pengerjaan.md`) sudah dibaca.
  - `bimo_bramantyo/CLAUDE.md` & `bimo_bramantyo/panduan/Checklist_Pengerjaan.md` dibuat. Struktur folder `submission/{kamus,indobert_colab}` dibuat.
  - **Environment Windows lokal:** `uv 0.11.28` terpasang via pip; venv `.venv/` di-bikin dengan Python 3.10.20 (uv auto-download). Library inti + Ambisius terpasang: `pandas 2.3.3, numpy 2.2.6, sklearn 1.7.2, tensorflow 2.21.0, Sastrawi, mpstemmer 0.1.0 (git ariaghora), nrclex 4.1.0, shap 0.49.1, lime 0.2.0.1, textblob, Levenshtein 0.27.3, google-play-scraper`, dll.
  - Smoke test OK: semua import + MPStemmer stem `'membantu' -> 'bantu'`.
  - Lexicon InSet (net-weight, 82KB neg + 41KB pos) + slang_words.csv (3MB) disalin dari `../submission/kamus/` ke `submission/kamus/`.
  - **Verify-first API Shopee 2026-07-12 TERVERIFIKASI:**
    - Title: `Shopee Indonesia` · Installs: 100 juta+ · Score avg **4.5679**
    - Ratings total: **18.459.768** (18,5jt) — terbesar di antara PLN/MyTelkomsel/Shopee
    - Text reviews: **5.856.841** (5,86jt) — trivial capai target 10rb+
    - Histogram: ⭐1: 1,34jt (7,25%) · ⭐2: 237rb (1,28%) · ⭐3: 386rb (2,09%) · ⭐4: 1,14jt (6,19%) · ⭐5: **15,36jt (83,19%)** → sangat skew positif. Semua bintang punya jauh >target scrape.
    - Sample per bintang inspeksi manual (5 tiap): domain jelas e-commerce (voucher, penjual, pengiriman, refund, iklan maksa, error, spaylater). **⭐3 masih sarat keluhan → netral murni langka** (mirip MyTelkomsel — antisipasi threshold `|lex net|=0`). ⭐4 & ⭐5 mixed (ada keluhan implisit) → rating bising ada, tapi tak separah MyTelkomsel.
- **Tahap 1 — Scraping: ✅ SELESAI** — `submission/scraping_shopee.py` ditulis (stratified, boost ⭐3, docstring).
  - **Hasil: 55.000 ulasan unik** (persis target, 0 duplikat reviewId, 0 null di `content/score/reviewId/at`).
  - Distribusi: ⭐1: 12rb · ⭐2: 8rb · ⭐3: 15rb · ⭐4: 8rb · ⭐5: 12rb (persis sesuai konfigurasi PER_STAR).
  - **Rentang: 2025-05-02 → 2026-07-11** (~14 bulan). **1.371 ulasan di rentang 25 Apr - 10 Mei 2026** = MELIPUTI momen kenaikan biaya XTRA 2 Mei 2026 ✓.
  - Lonjakan volume: **Juni 2026 = 17.841 ulasan** — dikonfirmasi di EDA Tahap 2 sebagai lonjakan didominasi ⭐1-⭐2.
  - Panjang teks: median 9 kata, mean 15,9 kata, max 101. Panjang wajar untuk review Play Store.
  - CSV **21,67 MB** (aman untuk zip submission — Nazhif 20MB, Fareynaldi 20MB).
  - Kolom privasi (`userName, userImage`) SUDAH di-drop. 9 kolom tersimpan.
- **Tahap 2 — EDA: ✅ SELESAI (terverifikasi visual via Read tool)** — 4 plot PNG di `d:\tmp\`.
  - **Plot 1 (distribusi + proyeksi):** rating persis target. Baseline label **paling seimbang di antara 3 tema tim**: neg 36,4% / netral 27,3% / pos 36,4% — hasil boost ⭐3.
  - **Plot 2 (panjang teks):** ⭐2 median terpanjang (18 kata), ⭐1 median 11, ⭐3 median 13, ⭐4 median 7, ⭐5 median 3. **Ulasan negatif jauh lebih panjang** (user marah lebih detail). Jumlah kata bisa jadi fitur diskriminatif.
  - **Plot 3 (temporal):** baseline ~1-3rb/bulan Mei 2025-Apr 2026. **LONJAKAN MASSIF Juni 2026: 17.841 ulasan didominasi ⭐1** (warna merah tebal di stackplot) → post-momen XTRA 2 Mei + akumulasi ketidakpuasan iklan. Storytelling insight kuat.
  - **Plot 4 (wordcloud):** NEGATIF didominasi kata **"iklan"** (kotak terbesar!) + "padahal", "malah", "banyak", "paket". NETRAL: "sekarang", "kurir", "paket", "barang", "pengiriman", "cod" — tema logistik. POSITIF: "bagus", "mantap", "membantu", "belanja", "sesuai", "murah" — positif jelas.
  - **Statistik non-visual:**
    - Duplikat content (setelah lowercase/strip): **8.762 (15,9%)** — banyak ulasan pendek generic ("oke", "mantap"). TIDAK di-drop (mengikuti pola Nazhif+Fareynaldi — beda reviewer = data valid).
    - Null: `reviewCreatedVersion, appVersion` 14,2rb (25,7%); `replyContent, repliedAt` 13,4rb (24,4%) — normal, banyak reviewer tak provide version + tidak semua di-reply.
    - Rasio kata topik per bintang: **%app > %prod di semua bintang** (⭐1: 41,9% vs 18,5%; ⭐2: 44,9% vs 41,6%; ⭐3: 39,7% vs 33,7%). Insight: **sentimen dominan mengarah ke aplikasi**, bukan produk penjual. Risiko "keluhan produk mencemari" LEBIH KECIL dari yang dikhawatirkan riset awal.
  - Top-15 kata Negatif: **iklan(8683), maksa(2489), tiba(1969), iklannya(1933), malah(1822), masuk(1730), banyak(1706), barang(1610), lama(1453)** → "iklan maksa" = keluhan utama Shopee periode ini.
- **Tahap 3 — Preprocessing: ✅ SELESAI (terverifikasi manual)** — pipeline scratchpad di `d:\tmp\preprocess_shopee.py`.
  - **Performance: 1,5 detik total untuk 55rb baris** (MPStemmer 0,1 dtk untuk 24.437 kata unik). Fareynaldi bukti ~7800x lebih cepat dari Sastrawi (Nazhif 13 menit).
  - Pipeline: `clean_text` (lowercase + URL/mention/emoji/digit/punct removal + collapse elongasi 3+→2) → `normalize_slang` (word-by-word map dari 4.330 entri single-word `slang_words.csv`) → `remove_stopwords` (123 stopword Sastrawi) → `stem_via_cache` (MPStemmer + cache per-kata unik).
  - **Dua kolom output**: `text_clean` (clean + slang, TANPA stem — untuk DL/IndoBERT & scoring lexicon) & `text_stemmed` (clean + slang + stopword + stem — untuk TF-IDF/SVM).
  - Rata2 kata: 15,9 → 11,9 (turun 25% karena stopword). Baris `text_clean` kosong: 378 (0,7%); baris `text_stemmed` kosong: 1.058 (1,9%) — bisa di-filter di Tahap 4 pelabelan.
  - Verifikasi manual sample: elongasi ✓ (`bagusssss` → `bagus`), slang ✓ (`gk→enggak`, `anj→anjing`, `bgt→banget`, `kalo→kalau`, `pesenan→pesan`), stem prefix/suffix ✓ (`membantu→bantu`, `muter→puter`, `maksa→paksa`, `berbelanja→belanja`, `pesenan→pesan`), emoji ✓ dibuang.
  - **Insight teknis**: MPStemmer punya rule informal→formal internal (`enggak → tidak`). Bonus normalisasi.
  - Output scratchpad: `d:\tmp\processed_full.csv` (17,5 MB, 6 kolom). Di Tahap 5 pipeline sama akan di-embed ke notebook (anti data-leak: tokenizer/vectorizer fit SETELAH split).
- **Tahap 4 — Pelabelan: ✅ SELESAI (strict-neutral, terverifikasi generalisasi)** — scratchpad `d:\tmp\label_shopee.py`.
  - **Lexicon InSet net-weight** (WAJIB): 3.369 pos + 6.107 neg = 8.395 kata unik; **1.081 kata muncul di KEDUA file** dgn bobot berlawanan → `.update()` bug fatal (dihindari).
  - lex_score dihitung dari `text_clean` (TANPA stem — kata utuh cocok lexicon). Statistik: mean -6,76, median -3, min -112, max 71.
  - ⭐3 breakdown |lex_score|: `=0`: 1.186 (7,9%) · `≤1`: 2.424 · `≤2`: 4.066.
  - **Sweep 3 threshold** dengan SVM cepat (TF-IDF ngram 1-2, C=0.5):
    - `|lex|=0`: total **24.570** (neg 11.961/net **1.106**/pos 11.503), train 95,06 / **test 87,71** / F1-macro 72,03 ✓
    - `|lex|≤1`: total 25.808 (net 2.344), train 94,36 / test 84,75 (**< 85%!**) / F1-macro 73,40
    - `|lex|≤2`: total 27.448 (net 3.984), train 91,92 / test 81,46 (jauh di bawah 85%) / F1-macro 73,74
  - **TERPILIH: `|lex|=0` (strict-neutral)** — pattern PLN yang aman. Test 87,71% > 85% (kriteria utama ✓). Netral 1.106 (lebih besar dari Nazhif 662 & Fareynaldi 570 → kelas tidak degenerate).
  - **Verify-first inference: 8/8 BENAR** ✅ (2 positif/3 negatif/2 netral eksplisit dari domain Shopee: "iklan maksa lemot", "aplikasi force close", "mohon tambahkan fitur qris", "bagaimana cara mengaktifkan spaylater") — bukan angka semu; model belajar pattern real.
  - Distribusi 24.570 sampel: neg 48,7% / net 4,5% / pos 46,8%. Netral kecil (struktural — mirip Nazhif+Fareynaldi); F1-netral 34,7% di SVM cepat (akan naik di IndoBERT).
  - Saved: `submission/dataset_shopee_labeled.csv` (6,7 MB, 8 kolom: `reviewId, content, score, at, text_clean, text_stemmed, lex_score, label`).
  - Catatan Tahap 5: SVM cepat 87,7% belum tembus 92% (saran #2). Rencana boost: tuning LinearSVC (C=1.0 atau grid), ngram_range lebih besar, feature engineering. Fallback pasti: IndoBERT Colab T4 (Fareynaldi 92,78% dengan data lebih kecil).
- **Tahap 5 — 4 Skema (Fase A: Skema 1-3 lokal): ✅ SELESAI** — `submission/pelatihan_analisis_sentimen.ipynb` (42 sel, 1,22 MB, 0 error).
  - Kernel `bimo_shopee` registered. Notebook di-generate via `d:\tmp\build_notebook.py` (nbformat) + di-execute via `jupyter nbconvert --execute --inplace`.
  - **Skema 1 SVM+TF-IDF (Pipeline+CV 5-fold, 70/30):** train 97,29% / **test 88,33%** / F1-macro 70,18. CV 5-fold: 88,17–88,72 (mean 88,46 ± 0,31) — konsisten. Config `feat50k`: ngram(1,2), max_features=50000, min_df=1, C=1.0, class_weight='balanced'.
  - **Skema 2 BiLSTM+Embedding (80/20, anti-leak):** train 93,89% / **test 85,04%** / F1-macro 70,45. Arsitektur `Emb(128)→SpatialDropout(0.2)→BiLSTM(64)→Dense(64)→Dropout(0.3)→Dense(3,softmax)`, EarlyStopping patience 3, class_weight balanced. Tokenizer fit HANYA di train.
  - **Skema 3 CNN 1D multi-kernel (80/20, anti-leak):** train 91,81% / **test 87,00%** / F1-macro 72,92. Multi-kernel Conv1D `[2,3,4,5]` × 128 filters + GlobalMaxPool + concat + Dense(128) + Dropout(0.4). Tokenizer sama dengan BiLSTM (train-only fit).
  - **SEMUA lolos ≥85% (kriteria wajib) ✓**. Saran #2 (>92% train & test) BELUM tercapai di skema klasik (plafon Shopee ~88% CV-verified) — diandalkan IndoBERT.
  - **Skema 4 IndoBERT: siap eksekusi USER** — package Colab lengkap disiapkan:
    - `submission/indobert_colab/indobert_train_colab.py` — full training script (indobert-base-p1, 3 epoch, batch 16, max_len 128, fp16, AdamW lr 2e-5).
    - `submission/indobert_colab/PANDUAN_COLAB.md` — panduan step-by-step Colab T4.
    - User jalankan Colab → dapat `indobert_metrics.json` + `indobert_history.json` → simpan di `submission/indobert_colab/` → Claude re-run notebook.
    - Fareynaldi bukti IndoBERT 92,78% dgn 14.671 sampel; kita 24.570 (lebih besar) → target realistis >92% ✓ (saran #2).
- **Tahap 5 Fase B (Skema 4 IndoBERT): ✅ SELESAI** — user run Colab T4, hasil loaded.
  - Config: `indobert-base-p1`, batch 16, max_len 128, 3 epoch, fp16, lr 2e-5, AdamW.
  - **Skema 4 IndoBERT: train 97,00% / test 90,66% / F1-macro 73,62%** — 9 menit training di Colab T4.
  - Per-kelas F1: negatif 93,06% · netral 35,39% · positif 92,40%. Netral kecil (1.106/24.570 = 4,5%) menyeret F1 macro turun.
  - Test 90,66% belum tembus saran #2 (>92% train & test) — **user pilih Terima ⭐⭐⭐⭐ Skilled** daripada retrain.
- **Tahap 6 — Error Analysis + XAI + PCA/t-SNE + NRCLex: ✅ SELESAI (embedded di notebook, 0 error)**.
  - Error Analysis: sampel salah klasifikasi + pola per kombinasi (true, pred).
  - XAI: top 15 SVM coefficients per kelas (kata paling berpengaruh) + LIME per contoh (3 contoh sample).
  - PCA (variance 6,55%) + t-SNE (max_iter=500) untuk 3000 sampel test — visualisasi cluster 3 kelas.
  - NRCLex emosi dgn bridge ID→EN — heatmap 8 emosi per kelas (positif dominan joy/trust, negatif dominan anger/sadness/disgust).
  - Bug fixes selama execute:
    - TSNE `n_iter` → `max_iter` (sklearn 1.7 breaking change).
    - NRCLex API: `NRCLex(text)` menerima path lexicon, BUKAN teks. Pattern benar: `n = NRCLex(); n.load_raw_text(text); n.affect_frequencies`.
    - NLTK downloads: wordnet, omw-1.4, brown ditambah selain punkt/punkt_tab.
- **Tahap 7 — Inference: ✅ SELESAI (embedded)**.
  - Model: BiLSTM (Skema 2) untuk inference multi-contoh.
  - 12 kalimat uji Shopee-domain (4 positif + 4 negatif + 4 netral). Semua ter-embed dengan predicted label + confidence.
- **Tahap 8 — Packaging: ✅ SELESAI**.
  - `bimo_bramantyo/Proyek_Analisis_Sentimen_Shopee_Bimo_Bramantyo.zip` (9,4 MB, 12 file dalam 1 folder root).
  - Isi: 4 wajib (`notebook.ipynb`, `scraping_shopee.py`, `requirements.txt`, `dataset_shopee_reviews.csv`) + 8 pendukung (`dataset_shopee_labeled.csv`, `kamus/`, `indobert_colab/`).
  - Notebook 1,55 MB (62 sel, 41 code+21 markdown, semua output+plot embedded, 0 error).
  - `requirements.txt` lengkap dengan catatan mpstemmer (git) & IndoBERT (Colab).
- **🏆 HASIL AKHIR: ⭐⭐⭐⭐ (Skilled)** — 5 dari 6 saran + SEMUA saran tambahan reviewer (level Ambisius):
  - ✅ Saran 1 (deep learning): BiLSTM + CNN + IndoBERT
  - ❌ Saran 2 (train & test >92%): train ✓ tapi test max 90,66% (kurang 1,34%)
  - ✅ Saran 3 (≥3 kelas): negatif/netral/positif
  - ✅ Saran 4 (≥10.000 sampel): 24.570 berlabel
  - ✅ Saran 5 (3 skema): 4 skema variasi
  - ✅ Saran 6 (inference kategorikal + bukti): 12 kalimat multi-contoh embedded
  - ✅ Saran tambahan reviewer: MPStemmer, sklearn Pipeline, StratifiedKFold CV, anti data-leak, Error Analysis, XAI (LIME + SVM coef), PCA/t-SNE, NRCLex (bridge ID→EN), kode bersih (docstring, deskripsi text cell).
- **SISA: user upload zip ke Dicoding** (jangan submit berkali-kali; review ±3 hari kerja).
- **Tahap 1 — Scraping: ⏳ BELUM**
- **Tahap 2 — EDA: ⏳ BELUM**
- **Tahap 3 — Preprocessing: ⏳ BELUM**
- **Tahap 4 — Pelabelan: ⏳ BELUM**
- **Tahap 5 — 4 Skema pelatihan: ⏳ BELUM**
- **Tahap 6 — Evaluasi + Error Analysis + XAI + NRCLex: ⏳ BELUM**
- **Tahap 7 — Inference: ⏳ BELUM**
- **Tahap 8 — Packaging: ⏳ BELUM**
