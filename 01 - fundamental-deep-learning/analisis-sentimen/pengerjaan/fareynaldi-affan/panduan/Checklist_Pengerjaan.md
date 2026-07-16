<div align="center">

# 📋 Checklist Pengerjaan — Proyek Analisis Sentimen

### Deep Learning · Ulasan **MyTelkomsel** (Google Play Store) · submission utk **Fareynaldi**

<span style="background:#e11d48;color:#fff;padding:3px 12px;border-radius:6px;font-weight:bold;">DICODING · Fundamental Deep Learning</span>
<span style="background:#16a34a;color:#fff;padding:3px 12px;border-radius:6px;font-weight:bold;">Target: ⭐⭐⭐⭐⭐</span>
<span style="background:#7c3aed;color:#fff;padding:3px 12px;border-radius:6px;font-weight:bold;">+ SEMUA saran reviewer</span>

_Centang `- [ ]` → `- [x]` tiap item selesai._

</div>

---

## 🧭 Cara Pakai

> 1. Kerjakan **berurutan Tahap 1 → 8**. Tiap tahap tuntas dulu.
> 2. **Kriteria Utama = wajib** (kalau tidak → submission **ditolak**).
> 3. **Saran 1–6 + saran tambahan reviewer** = target **SEMUA** → ⭐⭐⭐⭐⭐ dengan kode matang.
> 4. Notebook `.ipynb` **wajib sudah di-run** (output ter-embed).

---

## 🎯 Keputusan Proyek (dikunci)

| Aspek | Pilihan |
| :--- | :--- |
| 🎬 Tema | Sentimen **MyTelkomsel** (`com.telkomsel.telkomselcm`) — trending: app berat/error pasca-update |
| 🌐 Sumber data | Google Play Store — `google-play-scraper` (lang=id, country=id) |
| ⚖️ Strategi scrape | **Stratified per bintang**, ⭐3 di-boost (`{1:12k,2:8k,3:18k,4:8k,5:12k}`) — rata2 4,38 |
| 🏷️ Pelabelan | **Hybrid**: rating murni (⭐1 neg, ⭐5 pos) + netral ⭐3 lex-rendah (net-weight InSet) |
| 🧠 Skema | SVM+TF-IDF (Pipeline+CV) · BiLSTM · CNN · IndoBERT |
| 🖥️ Device | M1 (skema 1–3 + pipeline) · Victus RTX 3050 (IndoBERT) |
| 🆕 Saran reviewer | MPStemmer · Pipeline · CV · error analysis · SHAP/LIME · PCA/t-SNE · NRCLex · anti-leak · docstring · augment |

---

## 📊 Dashboard Progres

| Tahap | Nama | Status |
| :-: | :--- | :-: |
| 0 | Perencanaan & Setup environment | ✅ |
| 1 | Scraping data (58.000 ulasan stratified) | ✅ |
| 2 | EDA (4 plot terverifikasi) | ✅ |
| 3 | Preprocessing (MPStemmer, 0,1 dtk) | ✅ |
| 4 | Pelabelan hybrid (denoise moderat, 14.671) | ✅ |
| 5 | 4 Skema (SVM 90,9 / BiLSTM 90,0 / CNN 89,8 / **IndoBERT 92,78**) | ✅ |
| 6 | Evaluasi + Error Analysis + XAI + NRCLex | ✅ |
| 7 | Inference (8/8 benar) | ✅ |
| 8 | Packaging (zip 6,6 MB) | ✅ |

> ## 🏆 SELESAI — semua kriteria + **6 saran** + saran tambahan reviewer → **⭐⭐⭐⭐⭐**
> Notebook dieksekusi (0 error, 12 gambar ter-embed). **IndoBERT train 97,41% / test 92,78% (>92% ✓)**. Zip: `Proyek_Analisis_Sentimen_MyTelkomsel_Fareynaldi_Affan.zip`. **Sisa: upload ke Dicoding** (jangan submit berkali-kali).

_Legenda: ⏳ belum · 🚧 jalan · ✅ selesai_

---

## ✅ TAHAP 0 — Perencanaan & Setup

- [x] 4 pertanyaan awal dikonfirmasi user (tema/target/IndoBERT/scope/nama).
- [x] Referensi PLN dibaca (CLAUDE.md, feedback, artifacts, notebook pemenang dibedah).
- [x] Verify-first API MyTelkomsel (skor 4,38 · 12,1jt ratings · 2,93jt reviews · histogram).
- [x] Folder `fareynaldi/{submission,panduan,kamus,indobert_victus}` + salin kamus.
- [x] Library baru terpasang & smoke-test (MPStemmer, NRCLex, SHAP, LIME).
- [x] `scraping_mytelkomsel.py` ditulis.
- [ ] Kernel Jupyter venv terdaftar (untuk Run All notebook).

---

## ✅ TAHAP 1 — Scraping · _Kriteria Utama 1 + Saran 4_

- [ ] Jalankan `scraping_mytelkomsel.py` → `dataset_mytelkomsel_reviews.csv`.
- [ ] Verifikasi **jumlah ≥ 10.000** & distribusi per bintang.
- [ ] Cek kualitas: teks Bahasa Indonesia, ada pos/netral/negatif; 0 null pada content.
- [ ] Dataset mentah tersimpan di `submission/`.

---

## ✅ TAHAP 2 — EDA

- [ ] Distribusi rating bintang + proyeksi label (bar chart).
- [ ] Distribusi panjang teks per kelas (histogram + boxplot).
- [ ] Analisis temporal (lonjakan volume).
- [ ] Wordcloud per kelas.
- [ ] Cek missing value & duplikat.

---

## ✅ TAHAP 3 — Preprocessing Teks Indonesia · _Kriteria Utama 2 + saran MPStemmer/anti-leak_

- [ ] **Cleaning**: lowercase, buang URL/mention/emoji/angka/tanda baca, collapse huruf berulang.
- [ ] **Normalisasi slang** (kamus alay → baku).
- [ ] **Stopword removal** (Sastrawi) + **Stemming (MPStemmer)** dgn cache per-kata unik.
- [ ] Dua kolom siap: `text_clean` (DL/lexicon) & `text_stemmed` (TF-IDF/SVM).
- [ ] (Preprocessing DILAKUKAN sebelum pelabelan — sesuai reviewer.)

---

## ✅ TAHAP 4 — Pelabelan Hybrid (3 kelas) · _Kriteria Utama 2 + Saran 3_

- [ ] Muat lexicon InSet **net-weight** (pos+neg per kata, bukan `.update()`).
- [ ] Polar dari rating murni: ⭐1=negatif, ⭐5=positif; buang ⭐2 & ⭐4.
- [ ] Netral = ⭐3 dgn |lex net| rendah — **tune threshold** (≤1/≤2/=0) via SVM cepat.
- [ ] Distribusi akhir 3 kelas dicek (≥10rb total, netral cukup sehat).
- [ ] `dataset_mytelkomsel_labeled.csv` disimpan.

---

## ✅ TAHAP 5 — 4 Skema Pelatihan · _Kriteria Utama 3 + Saran 1,2,5 + anti-leak/Pipeline/CV_

> Min 1 skema **>92% train & test**; sisanya **≥85%**. **Split DULU, fit vektorizer/tokenizer hanya di train.**

- [ ] **Skema 1** — SVM + TF-IDF, split 70/30, **sklearn Pipeline** + **StratifiedKFold CV** _(kandidat >92%)_.
- [ ] **Skema 2** — BiLSTM + Embedding, split 80/20, tokenizer fit train-only.
- [ ] **Skema 3** — CNN 1D + Embedding, split 80/20, tokenizer fit train-only.
- [ ] **Skema 4** — IndoBERT fine-tune (di Victus) _(portfolio)_.

---

## ✅ TAHAP 6 — Evaluasi + Peningkatan Reviewer · _Kriteria Utama 4 + Saran 2_

- [ ] Tiap skema: **Accuracy + F1-Score** (testing set) — **WAJIB** — + **Confusion Matrix**.
- [ ] Tabel perbandingan 4 skema + bar chart (garis 85% & 92%).
- [ ] **Error Analysis**: sampel salah klasifikasi + pola (sarkasme/negasi/slang).
- [ ] **XAI**: SHAP/LIME kata paling berpengaruh + **PCA/t-SNE** visualisasi fitur.
- [ ] **NRCLex** emosi per kelas (eksploratif).
- [ ] Semua skema dinilai **≥ 85%** (≥1 skema **>92%**).

---

## ✅ TAHAP 7 — Inference + Bukti · _Saran 6_

- [ ] Cell inference: input kalimat → output **kategorikal** (negatif/netral/positif).
- [ ] Uji **beberapa contoh tiap kelas** (reviewer minta uji seluruh kelas).
- [ ] Bukti output ter-embed di notebook.

---

## 🏁 TAHAP 8 — Packaging & Submit

- [ ] `requirements.txt` dibuat.
- [ ] **Run All** notebook → tanpa error, output ter-embed.
- [ ] 4 berkas wajib: notebook + `scraping_mytelkomsel.py` + `requirements.txt` + dataset `.csv`.
- [ ] Nama file pakai nama lengkap **Fareynaldi** (konfirmasi dulu).
- [ ] Zip **1 folder** (lean, tanpa model besar).
- [ ] Review mandiri (semua checklist Dicoding).
- [ ] Upload — **jangan submit berkali-kali**.

---

## 🚫 Larangan Keras (Auto-Reject)

- [ ] ✋ Tidak melampirkan kode & proses scraping.
- [ ] ✋ Akurasi model < 85%.
- [ ] ✋ Tidak melampirkan 4 berkas kriteria utama.
- [ ] ✋ Pakai dataset open-source jadi.
- [ ] ✋ Notebook belum di-run (output kosong).
- [ ] ✋ Inference tidak kategorikal / tanpa bukti.

---

<div align="center">

### 🎯 Semua tercentang → siap submit ⭐⭐⭐⭐⭐

</div>
