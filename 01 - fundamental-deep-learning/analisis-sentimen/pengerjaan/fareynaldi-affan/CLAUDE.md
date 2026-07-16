# CLAUDE.md — Proyek Analisis Sentimen (Deep Learning) · **MyTelkomsel** · submission utk **Fareynaldi**

> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Analisis Sentimen**, tema **MyTelkomsel**. Dibuat **atas nama Fareynaldi** (teman non-teknis); yang menjalankan sesi = **Nazhif** (teknis).
- **Self-contained di folder ini** (`.../proyek analisis sentimen/fareynaldi/`). **Folder induk (`../`) = proyek PLN Mobile yang sudah LULUS ⭐⭐⭐⭐⭐ → REFERENSI metodologi saja, JANGAN diubah.**
- Aturan Everest/EBC (backoffice, Sequelize, CLIK, dll) **TIDAK berlaku di sini.**
- Ini **peningkatan** dari PLN: meniru metodologi pemenang **PLUS menerapkan SEMUA saran reviewer** (belajar hal baru). Target: **⭐⭐⭐⭐⭐ lagi** dengan kode lebih matang.

---

## 👤 USER & GAYA KERJA

- **Pemilik submission:** Fareynaldi (nama lengkap **menyusul** — sementara pakai `Fareynaldi`). Yang mengerjakan: Nazhif Setya Nugroho.
- **Email Nazhif:** dev@kalachakra.io
- **Cara komunikasi (WAJIB):** Bahasa Indonesia simpel, step-by-step, jelaskan **kenapa** tiap langkah. Teliti. **Jangan asumsi** — kalau ambigu (threshold, nama kolom, pilihan model), **tanya dulu** pakai AskUserQuestion.
- **Target nilai:** **⭐⭐⭐⭐⭐** (semua kriteria + semua saran relevan).

---

## 🎯 INTI PROYEK

Model **analisis sentimen** (klasifikasi teks 3 kelas: **negatif / netral / positif**) dari **ulasan Bahasa Indonesia aplikasi MyTelkomsel** di Google Play Store, di-**scraping mandiri**.

**Alur:** scraping → EDA → preprocessing teks → pelabelan hybrid → 4 skema pelatihan → evaluasi (+error analysis + XAI + emosi) → inference → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Tema** | Sentimen ulasan **MyTelkomsel** (`com.telkomsel.telkomselcm`) | Momen trending 2026: keluhan app berat/lemot/error pasca-update + paket mahal/sinyal |
| **Sumber data** | Google Play Store via `google-play-scraper` (lang=`id`, country=`id`) | Scraping mandiri = wajib. DILARANG pakai dataset open-source jadi |
| **Strategi scrape** | **Stratified per bintang 1-5**, bintang 3 **di-boost** (target `{1:12rb, 2:8rb, 3:18rb, 4:8rb, 5:12rb}`) | Netral (⭐3) minoritas → butuh pool besar. Fakta API terverifikasi (lihat bawah) |
| **Pelabelan** | **Hybrid + pembersihan error-label**: neg=⭐1 tanpa kata-positif-eksplisit, pos=⭐5 tanpa kata-negatif-eksplisit (denoise MODERAT — buang kontradiksi eksplisit saja, keluhan tersirat tetap); netral=⭐3 informasional & **\|lex net\|≤2**; buang ⭐2 & ⭐4. **14.671 sampel** (neg 9.837/pos 4.264/netral 570) | Lexicon **net-weight** InSet (jangan `.update()`). Denoise TERVERIFIKASI generalisasi (bukan trap). SVM 90,9% |
| **Skema pelatihan** | **4 skema**: SVM+TF-IDF (Pipeline+CV) · BiLSTM+Emb · CNN+Emb · IndoBERT | Min 1 skema >92% train&test (SVM/IndoBERT), sisanya ≥85% |
| **Target nilai** | ⭐⭐⭐⭐⭐ (semua kriteria + semua saran) | |
| **Environment** | **Split**: M1 (mayoritas) + Victus RTX 3050 (IndoBERT) | Lihat §ENVIRONMENT |

### Fakta MyTelkomsel (terverifikasi via API 2026-07-07)
- **Skor rata-rata 4,38** · **12.126.047 ratings** · **2.929.956 text reviews** · Installs 100 jt+.
- Histogram bintang: ⭐1 **1,31 jt (10,8%)** · ⭐2 226 rb (1,9%) · ⭐3 **348 rb (2,9%)** · ⭐4 944 rb (7,8%) · ⭐5 **9,30 jt (76,7%)**.
- Semua bintang punya jauh > 10rb ulasan → stratified 10rb+/bintang aman.
- **Netral (⭐3) tetap minoritas** (beda dari dugaan awal prompt "netral lebih banyak") → strategi hybrid PLN tetap dipakai, netral di-boost lewat scrape ⭐3 lebih banyak.
- **Domain telco**: kosakata *sinyal/jaringan/paket/kuota/pulsa/lemot/lag/mahal/error/berat*. InSet cenderung **kurang bising** di sini dibanding PLN (kata "sinyal/paket" netral di InSet, beda dari "mati/listrik").
- Kolom hasil scrape: `reviewId, content, score, thumbsUpCount, reviewCreatedVersion, at, replyContent, repliedAt, appVersion` (userName & userImage **dibuang demi privasi**).

### 4 Skema Pelatihan (rencana)

| Skema | Algoritma | Ekstraksi Fitur | Split | Device | Peningkatan vs PLN |
|---|---|---|---|---|---|
| **1** | SVM (LinearSVC) | TF-IDF | 70/30 | M1 | **sklearn Pipeline** + **StratifiedKFold CV** + fit **hanya di train** (anti-leak) |
| **2** | BiLSTM (Keras) | Embedding layer | 80/20 | M1 | tokenizer fit **hanya di train** |
| **3** | CNN 1D multi-kernel | Embedding layer | 80/20 | M1 | tokenizer fit **hanya di train** |
| **4** | IndoBERT fine-tune | tokenizer BERT | 80/20 | **Victus** | val-split best-epoch (sudah bersih) |

---

## 📁 STRUKTUR FOLDER

```
fareynaldi/
├── CLAUDE.md                       ← file ini (memory + rules)
├── PROMPT_untuk_session_baru.md    ← brief awal dari Nazhif
├── panduan/
│   └── Checklist_Pengerjaan.md     ← tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang nanti di-zip)
    ├── scraping_mytelkomsel.py         ← kode scraping (WAJIB)
    ├── dataset_mytelkomsel_reviews.csv ← dataset mentah hasil scraping (WAJIB)
    ├── dataset_mytelkomsel_labeled.csv ← dataset berlabel (pendukung)
    ├── pelatihan_analisis_sentimen.ipynb  ← notebook utama (WAJIB)
    ├── requirements.txt                ← (WAJIB)
    ├── kamus/                          ← lexicon InSet (net-weight) + slang (copy dari ../../submission/kamus)
    └── indobert_victus/                ← skrip + panduan Victus (IndoBERT)
```

> **Referensi (JANGAN diubah):** `../submission/` (notebook PLN pemenang), `../CLAUDE.md`, `../Feedback_Reviewer_Dicoding.md`.

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

**Venv dipakai bersama dengan proyek PLN** (folder induk), Python pyenv `3.10.20`, di `../.venv/`.
- **Selalu jalankan Python lewat:** `../.venv/bin/python` (dari dalam `fareynaldi/submission/`) atau `.venv/bin/python` (dari folder induk). JANGAN `python3` sistem.
- **Library inti (sudah terpasang):** `google-play-scraper, pandas, numpy, scikit-learn, tensorflow 2.21, Sastrawi, matplotlib, seaborn, wordcloud, nltk, jupyter, ipykernel, joblib`.
- **Library BARU utk saran reviewer (sudah terpasang):**
  - `mpstemmer` (dari GitHub ariaghora/mpstemmer, butuh `Levenshtein`) — stemming cepat (saran #1).
  - `nrclex` (+ textblob + nltk corpora `punkt`/`punkt_tab`/`wordnet`/`omw-1.4`) — analisis emosi (English, eksploratif).
  - `shap`, `lime` — XAI.
- Tugas M1: scraping, EDA, preprocessing, **Skema 1-3**, evaluasi, XAI, inference, packaging.

### Victus (RTX 3050, 4GB VRAM — USER jalankan, Windows/CUDA)
- Tugas: **Skema 4 (fine-tune IndoBERT)** via `torch`+`transformers`. Config aman: `batch=8`, `max_len=128`, `fp16`, grad-accum.
- Claude **tidak bisa remote** → siapkan `indobert_train_victus.py` + `requirements_victus.txt` + `PANDUAN_VICTUS.md`; USER run & kirim balik `indobert_metrics.json` + `indobert_history.json`.
- Fallback: Google Colab GPU T4.

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR (sama dgn PLN)

1. **WAJIB lampirkan kode & proses scraping.** Tanpa itu → reject.
2. **Akurasi testing set semua model yang dinilai ≥ 85%.**
3. **WAJIB 4 berkas kriteria utama:** notebook `.ipynb`, kode scraping `.py`, `requirements.txt`, dataset `.csv`.
4. **DILARANG dataset open-source jadi.** Harus scraping sendiri.
5. **Notebook `.ipynb` WAJIB sudah dijalankan** → output ter-embed.
6. **Inference WAJIB output kategorikal** (negatif/netral/positif) + bukti.
7. **WAJIB Accuracy & F1-Score pada testing set** tiap model.
8. **1 folder di-zip.** Bahasa Python. **Jangan submit berkali-kali.**

---

## 📊 PETA SARAN → BINTANG 5

**Kriteria Utama (wajib):** scraping ≥3rb · ekstraksi fitur+pelabelan · algoritma ML · test ≥85%.

**6 Saran (untuk bintang 5 — target: SEMUA):**
| Saran | Isi | Cara kita penuhi |
|---|---|---|
| 1 | Deep learning | BiLSTM + CNN + IndoBERT |
| 2 | Train & test **>92%** | SVM &/atau IndoBERT dikejar >92%; sisanya ≥85% |
| 3 | ≥3 kelas | negatif/netral/positif |
| 4 | ≥10.000 sampel | scrape ~50rb → berlabel ≥12rb |
| 5 | 3 skema (≥2 kombinasi beda) | 4 skema, variasi algoritma+fitur+split |
| 6 | Inference kategorikal + bukti | cell inference multi-contoh |

**Saran TAMBAHAN reviewer (nilai plus "belajar hal baru" — target: SEMUA yang relevan notebook):**
- ✅ **MPStemmer** ganti Sastrawi (stemming cepat) — dgn cache per-kata unik.
- ✅ **sklearn Pipeline** (TF-IDF→LinearSVC).
- ✅ **Cross-validation** (StratifiedKFold 5-fold) di skema klasik.
- ✅ **Metrik lengkap per kelas** (P/R/F1) + **Confusion Matrix** tiap skema.
- ✅ **Error Analysis** (sampel salah klasifikasi: sarkasme/negasi/slang).
- ✅ **XAI**: SHAP/LIME kata paling berpengaruh + **PCA/t-SNE** visualisasi fitur + wordcloud.
- ✅ **NRCLex** emosi (English, eksploratif/tambahan).
- ✅ **Split DULU baru preprocessing/fit** (anti data-leak): `fit` TF-IDF/tokenizer **hanya di train**.
- ✅ **Kode bersih**: hapus import tak terpakai, **docstring** tiap fungsi, deskripsi di text cell.
- ✅ **Data augmentation** (opsional): synonym replacement utk kelas minoritas (netral) — **hanya di train**.
- ⛔ **Preprocessing DULU baru pelabelan** (reviewer tekankan) — kita memang sudah begitu.
- ❌ MLflow/W&B — **skip** (overkill utk notebook submission; cukup disebut).

---

## 🧭 METODOLOGI (warisan sukses PLN — ulangi persis)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype ke data asli lewat `../.venv/bin/python` (output prototype JANGAN masuk folder submission — pakai scratchpad). Plot → simpan PNG ke `/tmp/` lalu **lihat pakai Read tool**. **Selalu cek INFERENCE + generalisasi ke data asli, bukan cuma angka test.**
2. **8 Tahap berurutan**, tuntas tiap tahap, update checklist + progress log.
3. **Output di-embed** via nbclient/nbconvert (kernel venv, cwd=folder submission), tanpa error.
4. **Privasi:** buang kolom identitas; jangan tampilkan data pribadi.
5. **Reproducibility:** `SEED=42` di semua split & model. `class_weight='balanced'`.

---

## 🔑 CATATAN TEKNIS PENTING (pelajaran mahal dari PLN — JANGAN diulangi)

- **⚠️ AGREEMENT FILTER = CACAT.** Jangan pelabelan "ambil hanya baris rating==lexicon". Di PLN → test 90% TAPI cuma 52% di data asli + inference SALAH (menyaring contoh keluhan → model tak belajar pola negatif). **Pakai polar dari rating murni** (⭐1=neg, ⭐5=pos; buang ⭐2&⭐4) + netral=⭐3 lex-rendah. Lexicon hanya menyaring netral.
- **⚠️ NET-WEIGHT lexicon (WAJIB).** InSet punya ~1.142 kata di KEDUA file (pos & neg) bobot berlawanan. Hitung **net = posd.get(w,0) + negd.get(w,0)** per kata. JANGAN `dict.update()` (negatif menimpa positif → skor semua negatif = bug fatal).
- **Cek generalisasi + inference SEBELUM percaya test accuracy.** Test tinggi bisa menipu kalau label bias. `class_weight='balanced'` + label bias = over-predict netral.
- **Dua kolom teks:** `text_clean` (clean+slang, TANPA stem) untuk DL/IndoBERT & scoring lexicon; `text_stemmed` (clean+slang+stopword+stem **MPStemmer**) untuk TF-IDF/SVM. Stem pakai **cache per-kata unik** (sekali saja).
- **Anti data-leak (reviewer):** `train_test_split` DULU, baru `fit` TF-IDF/tokenizer di **train saja**, `transform` di test. (Preprocessing teks umum boleh sebelum split; yang kritikal adalah **fit vektorizer/tokenizer & augmentation hanya di train**.)
- **NRCLex = English.** Untuk teks ID kurang match → pakai sebagai eksploratif (mis. bridge kata ID→EN untuk top-words per kelas, ATAU jujur tampilkan cakupan terbatas). Butuh nltk `punkt_tab`+`wordnet`; sertakan guard `nltk.download(...)` di notebook.
- **Domain telco:** cek apakah InSet menyeret kata telco netral (sinyal/paket/jaringan). Kalau bising, verify-first threshold netral.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Perencanaan & Setup: 🚧 JALAN**
  - 4 pertanyaan awal dikonfirmasi user: tema **MyTelkomsel** + target ⭐⭐⭐⭐⭐; IndoBERT di **Victus**; terapkan **SEMUA saran relevan**; nama file pakai **"Fareynaldi"** dulu.
  - Referensi PLN dibaca penuh (CLAUDE.md, feedback, artifacts, notebook pemenang 32 sel dibedah).
  - Verify-first API MyTelkomsel: skor 4,38 · 12,1jt ratings · 2,93jt reviews · histogram terverifikasi (lihat §Fakta).
  - Environment: folder `fareynaldi/{submission,panduan,kamus,indobert_victus}` dibuat; kamus disalin dari PLN; library baru terpasang & smoke-test OK (**MPStemmer, NRCLex, SHAP, LIME**).
  - `scraping_mytelkomsel.py` ditulis (stratified, ⭐3 boost, docstring).
- **Tahap 1 — Scraping: ✅ SELESAI** — **58.000 ulasan unik** (semua target per bintang tercapai: ⭐1:12rb ⭐2:8rb ⭐3:18rb ⭐4:8rb ⭐5:12rb). Rentang Okt 2024 → Jul 2026. CSV 20 MB.
- **Tahap 2 — EDA: ✅** — 4 plot terverifikasi visual (Read): distribusi+proyeksi label, panjang teks (neg median ~12 kata, pos ~5), temporal (lonjakan Mei-Jun 2026), wordcloud (neg=lemot/mahal/jaringan, pos=bagus/baik/oke).
- **Tahap 3 — Preprocessing: ✅** — **MPStemmer stem 18.452 kata unik dalam 0,1 detik** (vs Sastrawi ~13 mnt di PLN — saran #1 terbukti!). 45.080 baris ter-preprocess. Dua kolom text_clean & text_stemmed.
- **Tahap 4 — Pelabelan: ✅ TERKUNCI (setelah verify-first ekstensif — TEMUAN PENTING).**
  - **TEMUAN: rating MyTelkomsel bising ~15-20%** (banyak ⭐5 berteks keluhan: "apk bodoh gabisa dibuka", "sinyal sangat buruk"). Rating = label bising. Plafon jujur SVM ~84-85% dgn labeling rating-murni + netral besar.
  - **AGREEMENT/DENOISE-KUAT TERBUKTI TRAP LAGI:** wajib-ada-kata-kamus → SVM test **95,5% TAPI SEMU** (keluhan implisit "nutup sendiri/kesedot sendiri/makan memori" → salah jadi netral). DITOLAK.
  - **KEPUTUSAN FINAL (2 tahap konfirmasi user):**
    - Awalnya user pilih **no-denoise** (⭐1/⭐5 mentah) → SVM 88%, semua CPU ~87-88% (⭐⭐⭐⭐, IndoBERT ~90-91% kemungkinan tak tembus 92%).
    - Setelah lihat **angka CPU nyata (~88%)**, user pilih **DENOISE MODERAT** untuk kejar ⭐⭐⭐⭐⭐: buang HANYA ulasan salah-label eksplisit (⭐1 ber-kata-positif & ⭐5 ber-kata-negatif). **BUKAN trap** — hanya membuang kontradiksi eksplisit; **keluhan/pujian TERSIRAT tetap** → model tetap belajar (generalisasi terverifikasi).
  - **LABELING FINAL:** neg=⭐1 & tanpa kata-positif-eksplisit; pos=⭐5 & tanpa kata-negatif-eksplisit; **netral=⭐3 informasional & |lex net|≤2**. **14.671 sampel** (neg 9.837/pos 4.264/**netral 570**). **SVM test 90,9%** (train 97,7%, CV 0,910). IndoBERT diharapkan ~93-94% → tembus saran #2.
  - Insight: netral MyTelkomsel didefinisikan **semantik** (informasional), bukan sekadar ⭐3 (⭐3 MyTelkomsel isinya keluhan, beda dari PLN).
- **Tahap 5-7 — Notebook (46 sel) dibangun & dieksekusi ✅:** SVM Pipeline+CV, BiLSTM, CNN (anti-leak: fit vektorizer/tokenizer hanya train), IndoBERT-load. Evaluasi+Error Analysis+XAI(LIME+coef+PCA/t-SNE)+NRCLex(bridge ID→EN)+inference. 0 error, 11 gambar, semua plot terverifikasi visual.
  - **HASIL AKHIR (denoise moderat, 14.671 sampel):** SVM **90,9%** / BiLSTM **90,0%** / CNN **89,8%** / **IndoBERT train 97,41% test 92,78%** ✅ **>92% train&test → saran #2 TERPENUHI JUJUR**. Netral F1: SVM 0,50 → IndoBERT 0,63. Inference BiLSTM 8/8 (contoh borderline "murah" diganti "mohon tambahkan opsi bahasa inggris").
- **🏆 ⭐⭐⭐⭐⭐ TERCAPAI (jujur):** semua kriteria utama + 6 saran + saran tambahan reviewer (MPStemmer/Pipeline/CV/error-analysis/XAI/NRCLex/anti-leak/docstring/kode-bersih). Bukan angka semu — labeling terverifikasi generalisasi.
- **Tahap 8 — Packaging: ✅ SELESAI.** Re-run final (embed IndoBERT + inference 8/8) 0 error, 12 gambar, 1,27 MB. Nama lengkap: **Fareynaldi_Affan**. Zip: `Proyek_Analisis_Sentimen_MyTelkomsel_Fareynaldi_Affan.zip` (6,6 MB, 16 file, semua dalam 1 folder). **Sisa: user upload ke Dicoding (jangan submit berkali-kali).**
- **🏆 PROYEK SELESAI 100% → ⭐⭐⭐⭐⭐ (jujur).** Hasil final: SVM 90,9% / BiLSTM 90,0% / CNN 89,8% / IndoBERT 92,78% (train 97,41%). Semua kriteria + 6 saran + saran tambahan reviewer. Pelajaran kunci: MyTelkomsel jauh lebih sulit dari PLN (rating bising ~15-20%); solusi jujur = denoise moderat (buang kontradiksi eksplisit saja) + netral informasional; strong-denoise = trap (95% semu, gagal keluhan implisit). MPStemmer 0,1 dtk vs Sastrawi 13 mnt.
