# PROMPT UNTUK SESSION BARU — Proyek Analisis Sentimen **MyTelkomsel** (submission untuk Fareynaldi)

> Paste seluruh isi di bawah ini ke sesi Claude Code baru (atau cukup bilang ke sesi baru: "baca `PROMPT_untuk_session_baru.md` di folder ini dan kerjakan").

---

## 🎯 TUGAS

Bangun submission Dicoding **"Belajar Fundamental Deep Learning → Proyek Analisis Sentimen"** dengan tema **MyTelkomsel**, meniru proyek **PLN Mobile** yang sudah **LULUS ⭐⭐⭐⭐⭐**, **PLUS menerapkan saran reviewer** (sebagai latihan belajar hal baru). Target: **⭐⭐⭐⭐⭐ lagi**, tapi dengan kode yang lebih matang.

- Submission ini dibuat **untuk teman non-teknis bernama Fareynaldi** (submission-nya atas nama dia). Yang menjalankan sesi = **Nazhif** (teknis).
- **Kerjakan SEMUA di folder ini** (`.../proyek analisis sentimen/fareynaldi/`). Self-contained. Jangan sentuh/ubah proyek PLN di folder induk (`../`) — itu cuma **referensi**.

---

## 📚 LANGKAH 0 (WAJIB) — Baca referensi dulu, JANGAN mulai coding sebelum ini

Proyek PLN Mobile ada di folder induk (`../`) dan sudah tembus ⭐⭐⭐⭐⭐. **Baca dulu, karena di situ tersimpan metodologi & pelajaran mahal yang tidak boleh diulangi kesalahannya:**

1. **`../CLAUDE.md`** — BACA PENUH. Perhatikan khusus:
   - §🔑 CATATAN TEKNIS PENTING (bug net-weight lexicon, kenapa "agreement labeling" CACAT, dua kolom teks, dll)
   - §✅ PROGRESS LOG (evolusi labeling: agreement→V4→strict-neutral, dan angka tiap skema)
2. **`../submission/`** — notebook pemenang (`pelatihan_analisis_sentimen.ipynb`), `scraping_pln_mobile.py`, struktur folder, `kamus/` (lexicon InSet + slang), `indobert_victus/` (paket IndoBERT).
3. **`../panduan/Checklist_Pengerjaan.md`** — tracker bertingkat.
4. **`../artifacts/`** — **kriteria & aturan Dicoding (SAMA untuk submission ini)**. Baca `2.kriteria_utama.md`, `3.penilaian.md`, `4.ketentuan_berkas_submission.md`, `5.lainnya.md`.
5. **`../Feedback_Reviewer_Dicoding.md`** — **saran reviewer yang harus kita terapkan kali ini**.

> Gunakan proyek PLN sebagai **cetak biru metodologi**, bukan untuk di-copy datanya. Semua dibuat fresh untuk MyTelkomsel.

---

## 🗣️ GAYA KOMUNIKASI (WAJIB)

- **Bahasa Indonesia simpel, step-by-step, jelaskan _kenapa_ tiap langkah** (bukan cuma _apa_).
- **Jangan asumsi.** Kalau ambigu (threshold, nama kolom, pilihan model), **tanya dulu** pakai AskUserQuestion.
- Teliti detail kecil. User (Nazhif) teknis, tapi submission untuk teman non-teknis → tetap jelas & rapi.

---

## 📱 TEMA (dikunci): MyTelkomsel

- **Package Google Play:** `com.telkomsel.telkomselcm` (aplikasi utama — BUKAN varian "Basic").
- **Konteks trending 2026:** keluhan berulang **crash/force close massal pasca-update versi 8.6** (app makin berat, susah login); Telkomsel 150 juta+ pelanggan → basis review sangat besar.
- **Kenapa bagus:** rating agregat **~3,94** (jauh lebih tercampur dari PLN yang 4,89). Artinya distribusi bintang lebih seimbang → **kelas netral (bintang 3) lebih banyak & 3 kelas lebih alami** dibanding PLN. Ini kabar baik: kemungkinan besar **tidak perlu netral se-ekstrem PLN**.
- **Aman etika:** aplikasi self-care operator seluler (beli pulsa/paket, cek kuota, bayar tagihan). Tidak menyentuh politik/SARA/judi/pinjol/dewasa/tokoh.
- **VERIFY dulu via API** (seperti proyek PLN): cek rating, jumlah review, contoh ulasan, sebelum scraping penuh. Kalau ternyata package/volume berbeda, laporkan ke user.

---

## 🧭 METODOLOGI (warisan sukses PLN — ulangi persis)

1. **VERIFY-FIRST (paling penting).** Sebelum menulis logika apa pun ke notebook: prototype ke **data asli** lewat script `.venv/bin/python`. Untuk plot → simpan PNG ke `/tmp/` lalu **lihat pakai Read tool**. **Selalu cek INFERENCE + generalisasi ke data asli, bukan cuma angka test-accuracy.**
2. **8 Tahap berurutan:** scraping → EDA → preprocessing → pelabelan hybrid → 4 skema pelatihan → evaluasi → inference → packaging. Tuntaskan & update checklist tiap tahap.
3. **Environment split:** M1 (mayoritas: scraping, EDA, preprocessing, SVM/BiLSTM/CNN, inference) + **GPU untuk IndoBERT** (Victus atau Google Colab — tanya user). pyenv 3.10.x + venv `.venv/`, jalankan via `.venv/bin/python`.
4. **4 skema** (variasi algoritma + fitur + split): **SVM+TF-IDF**, **BiLSTM+Embedding**, **CNN+Embedding**, **IndoBERT**. Kejar ≥1 skema **>92% train & test** (saran #2), sisanya ≥85%.
5. **Reproducibility:** `random_state=42` di semua split & model. `class_weight='balanced'`.
6. **Output di-embed** via nbclient/nbconvert (kernel venv, cwd=folder submission). Notebook WAJIB sudah dijalankan tanpa error.
7. Buat **`fareynaldi/CLAUDE.md`** sendiri (memory + hard-rules + progress log) & **`fareynaldi/panduan/Checklist_Pengerjaan.md`**.

---

## ⛔ HARD LESSONS DARI PLN — JANGAN DIULANGI

1. **Pelabelan HARUS JUJUR (bukan angka semu).**
   - ❌ JANGAN pakai **"agreement filter"** (ambil hanya baris rating==lexicon). Di PLN itu kasih **test 90% TAPI cuma 52% di data asli + inference SALAH** (menyaring contoh keluhan → model tak belajar pola negatif). Angka tinggi tapi model tidak bekerja.
   - ✅ PAKAI: **polar dari rating murni** (bintang **1**=negatif, **5**=positif; buang bintang 2 & 4 yang ambigu di batas) + **netral = bintang 3 dengan skor lexicon rendah**. Untuk MyTelkomsel (netral lebih banyak), **tune threshold netral** (mis. `|lex net| ≤ 1` atau `≤ 2`, atau `=0` kalau perlu genjot akurasi) via verify-first sampai dapat: ≥10rb data, 3 kelas cukup seimbang, semua skema ≥85%, ≥1 skema >92%, **DAN inference benar**.
2. **Net-weight lexicon InSet.** InSet punya ~1.142 kata di **kedua** file (positif & negatif) dgn bobot berlawanan. Hitung **net = bobot_positif + bobot_negatif per kata**. JANGAN `dict.update()` (bikin negatif menimpa positif → skor semua jadi negatif = bug fatal).
3. **Cek generalisasi + inference SEBELUM percaya test accuracy.** Test tinggi bisa menipu kalau label bias.
4. **Stratified scrape per bintang** supaya 3 kelas terwakili (walau MyTelkomsel lebih seimbang, tetap stratified biar aman).
5. **Preprocessing teks DULU, baru pelabelan** (reviewer juga menekankan ini).
6. **Dua kolom teks:** `text_clean` (clean+normalisasi slang, TANPA stem) untuk DL/IndoBERT & scoring lexicon; `text_stemmed` (clean+slang+stopword+stem) untuk TF-IDF/SVM.

---

## 🆕 SARAN REVIEWER — TERAPKAN KALI INI (ini inti "belajar hal baru")

Dari `../Feedback_Reviewer_Dicoding.md`. Terapkan sebanyak mungkin (konfirmasi cakupan ke user):

1. **MPStemmer** ganti Sastrawi untuk stemming → **jauh lebih cepat** (`pip install mpstemmer`). Ini paling relevan (di PLN stemming makan ~13 menit). Tetap pakai **cache per-kata unik**.
2. **sklearn `Pipeline`** — rangkai `TfidfVectorizer → LinearSVC` dalam satu Pipeline (lebih rapi, anti langkah terlewat).
3. **Cross-validation** (`StratifiedKFold`, mis. 5-fold) untuk cek overfitting/robustness minimal di skema klasik.
4. **Metrik lengkap per kelas** (Precision/Recall/F1) + **Confusion Matrix** tiap skema (sudah standar di PLN — pertahankan).
5. **Error Analysis** — ambil sampel yang **salah klasifikasi**, analisis polanya (sarkasme, negasi, slang) di text cell.
6. **XAI**: **SHAP atau LIME** untuk menyorot kata paling berpengaruh + **PCA/t-SNE** untuk visualisasi fitur. (Word cloud sudah kita lakukan di PLN — pertahankan.)
7. **NRCLex** — analisis **emosi** (anger, joy, sadness, dll) sebagai bonus perspektif (opsional, `pip install NRCLex`; catatan: NRCLex berbasis Inggris, jadi ini eksploratif/tambahan saja).
8. **Preprocessing/scaling/encoding SETELAH `train_test_split`** untuk mencegah **data leak** ke test set (khususnya untuk fit TF-IDF/tokenizer → `fit` hanya di train, `transform` di test).
9. **Kode bersih:** hapus import yang tidak dipakai, tambah **docstring** tiap fungsi, dan deskripsi di **text cell**.
10. **Data augmentation** (opsional): synonym replacement / random insertion untuk memperkaya kelas minoritas.

---

## 📦 DELIVERABLES (4 wajib + pendukung)

Struktur seperti PLN (`fareynaldi/submission/`):
- `pelatihan_analisis_sentimen.ipynb` (WAJIB, sudah dijalankan, output ter-embed)
- `scraping_mytelkomsel.py` (WAJIB)
- `requirements.txt` (WAJIB)
- `dataset_mytelkomsel_reviews.csv` (WAJIB, hasil scraping)
- pendukung: `dataset_..._labeled.csv`, `kamus/` (boleh copy dari `../submission/kamus/`), paket IndoBERT GPU.
- **Nama file** pakai nama lengkap Fareynaldi → **konfirmasi dulu** ke user.
- Zip lean di akhir (tanpa model besar), notebook + 3 file wajib + pendukung.

---

## ❓ TANYA KE USER DI AWAL (pakai AskUserQuestion, sebelum coding)

1. **Nama lengkap Fareynaldi** (untuk penamaan file, mis. `Fareynaldi_Xxx`).
2. **Environment IndoBERT**: pakai **Victus RTX 3050** (punya Nazhif, sudah terbukti) atau **Google Colab GPU** (lebih mudah, tanpa setup lokal)?
3. **Cakupan saran reviewer**: terapkan **SEMUA** (maksimal belajar, notebook lebih panjang) atau **inti saja** (MPStemmer + Pipeline + cross-val + error analysis + SHAP/LIME)?
4. Konfirmasi **tema MyTelkomsel** & target **⭐⭐⭐⭐⭐**.

Setelah dikonfirmasi → mulai Tahap 0 (buat CLAUDE.md + checklist + setup venv), lalu Tahap 1 dst. **Verify-first di tiap tahap.** Semangat! 🚀
