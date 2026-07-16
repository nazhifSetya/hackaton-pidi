# CLAUDE.md — Proyek Akhir: Klasifikasi Gambar (Deep Learning)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md) · Status semua proyek & lokasi artefak berat → [`/_meta/STATUS.md`](../../../../_meta/STATUS.md).


> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu tahap.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Fundamental Deep Learning" → Proyek Akhir: Klasifikasi Gambar**. Lokasinya kebetulan di dalam `Everest/docs/hackaton_PIDI/`, **TAPI sama sekali TIDAK berhubungan dengan aplikasi Everest (EBC).**
- **Aturan dari `Everest/CLAUDE.md` dan `docs/CLAUDE.md` TIDAK BERLAKU di sini.** Abaikan semua hal soal backoffice-service/Sequelize/Hoppscotch/CLIK/dll. **Jangan** sentuh/ubah file di luar folder project ini.
- Project ini **self-contained**. Semua yang relevan ada di folder ini.
- Ini proyek KEDUA dari kelas yang sama. Proyek pertama (**Analisis Sentimen PLN Mobile**) **LULUS ⭐⭐⭐⭐⭐** — referensi metodologi sukses: `../proyek analisis sentimen/CLAUDE.md` (baca bagian METODOLOGI + pelajaran verify-first).

---

## 👤 USER & GAYA KERJA

- **Nama user:** Nazhif Setya Nugroho → dipakai di nama file bila perlu: `Nazhif_Setya_Nugroho`.
- **Email:** dev@kalachakra.io
- **Konteks:** User junior developer, sudah menyelesaikan proyek NLP pertamanya (analisis sentimen).
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia yang simpel**, mudah dimengerti junior.
  - **Pelan-pelan, step-by-step.** Jelaskan _kenapa_ tiap langkah, bukan cuma _apa_.
  - **Teliti terhadap detail kecil.**
  - **Jangan asumsi.** Kalau ambigu, **tanya dulu** pakai AskUserQuestion sebelum nulis kode.
- **Target nilai yang disepakati:** **BINTANG 5 (⭐⭐⭐⭐⭐)** — terapkan **SEMUA 6 saran** penilaian.

---

## 🎯 INTI PROYEK (apa yang dikerjakan)

Membangun model **CNN klasifikasi gambar** (Keras Sequential + Conv2D + Pooling), lalu mengonversi model ke **3 format**: **SavedModel, TF-Lite, TFJS**.

**Alur:** pilih & unduh dataset → EDA → split train/val/test → augmentasi (train only) → training CNN + callback → evaluasi (akurasi & loss plot) → konversi 3 format → inference + bukti → packaging.

---

## 🧩 KEPUTUSAN YANG SUDAH DIKUNCI (jangan diubah tanpa konfirmasi user)

| Aspek | Keputusan | Catatan |
|---|---|---|
| **Dataset** | **Animals-10** (Kaggle `alessiocorrado99/animals10`) | **26.179 gambar, 10 kelas hewan** (folder bahasa Italia → rename Inggris), resolusi ASLI tidak seragam (terverifikasi: 156 ukuran unik dari sampel 400), GPL-2.0, 614 MB, unduh anonim via `kagglehub.dataset_download("alessiocorrado99/animals10")`. Bukti publik 97–99,5% dgn transfer learning. Catatan: ~5-10% label noise, kelas tak seimbang (spider ~4,8rb vs elephant ~1,4rb) |
| **Environment** | **Google Colab GPU (T4)** untuk training; M1 lokal untuk persiapan/packaging | Konversi TFJS paling mulus di Colab; tensorflowjs rewel di M1 |
| **Target nilai** | ⭐⭐⭐⭐⭐ (SEMUA 6 saran) | |
| **Arsitektur** | **Transfer learning: MobileNetV2 (pre-trained, frozen/fine-tune) DI DALAM Sequential + layer Conv2D + Pooling di atasnya** — dipilih user 2026-07-09 | Kriteria Sequential+Conv2D+Pooling terpenuhi literal; rute terbukti 96–98% di Animals-10; kejar train & test ≥95% |

---

## 📁 STRUKTUR FOLDER

```
proyek_akhir/
├── CLAUDE.md                       ← file ini (memory + rules)
├── artifacts/                      ← 📦 INSTRUKSI ASLI DICODING — READ-ONLY
│   ├── 1.pengantar.md ... 5.lainnya.md + image*.png
├── panduan/
│   └── Checklist_Pengerjaan.md     ← 📋 tracker progres (update tiap tahap)
└── submission/                     ← 💻 FILE KERJA + OUTPUT (yang nanti di-zip)
    ├── notebook.ipynb                  ← notebook utama (WAJIB, sudah dijalankan)
    ├── notebook.py                     ← export .py dari notebook (WAJIB — reject kalau tidak ada!)
    ├── requirements.txt                ← (WAJIB)
    ├── saved_model/                    ← saved_model.pb + variables/
    ├── tflite/                         ← model.tflite + label.txt
    ├── tfjs_model/                     ← model.json + group1-shard*.bin
    └── README.md                       ← opsional (disarankan template Dicoding)
```

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `artifacts/2.kriteria.md`, `artifacts/4.ketentuan_berkas_submission.md`, `artifacts/5.lainnya.md`.

1. **Akurasi training DAN testing set ≥ 85%** (di bawah itu → reject).
2. **WAJIB lampirkan KEDUA file `.py` dan `.ipynb`** (sering kelupaan → reject).
3. **WAJIB simpan model dalam 3 format: SavedModel, TF-Lite, TFJS.** Kurang satu → reject.
4. **Notebook `.ipynb` WAJIB sudah dijalankan** → semua output ter-embed.
5. **Semua kriteria wajib diterapkan:** dataset ≥1.000 gambar, bukan RPS/X-Ray, split train/test/val, Sequential+Conv2D+Pooling, plot akurasi & loss.
6. **`requirements.txt` wajib ada.**
7. Kirim dalam **1 folder di-zip** (.zip/.rar). Bahasa: **Python**.
8. **Jangan submit berkali-kali** (review ±3 hari kerja).

---

## 📊 KRITERIA & PENILAIAN (peta ke bintang 5)

**Kriteria Utama (wajib, kalau tak penuhi = reject):**
1. Dataset bebas, min **1.000 gambar**, BUKAN Rock-Paper-Scissors / X-Ray.
2. Split **train / test / validation**.
3. Model **Sequential + Conv2D + Pooling**.
4. Akurasi train & test **min 85%**.
5. **Plot akurasi & loss** model.
6. Simpan ke **SavedModel + TF-Lite + TFJS**.

**Saran (untuk naik bintang) — target: TERAPKAN SEMUA 6:**
| Saran | Isi | Cara kita penuhi |
|---|---|---|
| 1 | Implementasi **Callback** | EarlyStopping + ModelCheckpoint (+ ReduceLROnPlateau) |
| 2 | Gambar dataset asli **resolusi tidak seragam** | syarat pemilihan dataset + buktikan di EDA (print beberapa ukuran) |
| 3 | Dataset **≥ 10.000 gambar** | syarat pemilihan dataset |
| 4 | Akurasi train & test **≥ 95%** | arsitektur + (opsional) transfer learning dalam Sequential |
| 5 | **≥ 3 kelas** | syarat pemilihan dataset |
| 6 | **Inference** pakai salah satu format (TF-Lite/TFJS/SavedModel) + bukti | cell inference TF-Lite di notebook dgn output ter-embed |

**Skala bintang (dari `artifacts/image.png`):**
- ⭐⭐⭐ = kriteria utama penuh, tanpa saran
- ⭐⭐⭐⭐ = kriteria utama + **min 3 saran**
- ⭐⭐⭐⭐⭐ = kriteria utama + **SEMUA saran** ← **TARGET**

---

## 🧭 METODOLOGI KERJA (warisan sukses 2 proyek sebelumnya)

1. **VERIFY-FIRST (wajib).** Sebelum menulis logika ke notebook: prototype dulu. Untuk plot, simpan PNG ke scratchpad/`/tmp/` lalu **lihat pakai Read tool**. Baru tulis ke notebook setelah yakin benar.
2. **Kerjakan bertahap** dan tuntaskan tiap tahap sebelum lanjut. Update checklist + progress log tiap tahap selesai.
3. **Notebook final harus dieksekusi penuh tanpa error** (di Colab: Run All; output ter-embed).
4. **Reproducibility:** set seed (`tf.keras.utils.set_random_seed(42)`) di split & training.
5. **Augmentasi HANYA pada train set** (tips resmi Dicoding — jaga konsistensi test set).
6. Karena training di **Colab** dan Claude di **M1**: Claude siapkan notebook + instruksi; user Run All di Colab; hasil (.ipynb ter-output + folder model) dibawa balik ke lokal untuk packaging. Verifikasi logika berat tetap diprototype dulu seadanya di M1 (CPU, subset kecil) sebelum dikirim ke Colab.

---

## 🔑 CATATAN TEKNIS PENTING

- **Keras 3 / TF ≥2.16:** `model.save()` → `.keras` format; untuk **SavedModel** pakai `model.export("saved_model/")` (atau `tf.saved_model.save`). TF-Lite: `tf.lite.TFLiteConverter.from_saved_model()`. TFJS: `tensorflowjs_converter --input_format=tf_saved_model` (atau dari keras). Cek kompatibilitas versi di Colab saat pengerjaan.
- **tensorflowjs** sering bentrok dependency dgn TF terbaru → install di sel terpisah SETELAH training & export selesai, atau pin versi. Jangan sampai merusak runtime sebelum training.
- **Bukti resolusi tidak seragam (saran #2):** sertakan cell EDA yang mencetak ukuran (width×height) sampel gambar / set ukuran unik — ini bukti eksplisit untuk reviewer.
- **≥95% train & test:** pastikan tidak overfitting (gap train-test kecil). Kalau CNN murni mentok, pakai transfer learning (base pre-trained) DI DALAM Sequential + tambah Conv2D/Pooling layer agar kriteria 4 tetap terpenuhi secara literal.
- **label.txt** untuk folder `tflite/` (sesuai struktur template Dicoding).
- **requirements.txt** dibuat dari library yang benar-benar dipakai (pipreqs-style), bukan pip freeze seluruh Colab.

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap tahap selesai.** Format: apa yang dikerjakan + status verifikasi.

- **Tahap 0 — Perencanaan & Setup: ✅ SELESAI (2026-07-09)**
  - Instruksi Dicoding dibaca semua; dipindah ke `artifacts/`. Folder `panduan/` + `submission/` dibuat.
  - Keputusan dikunci: target ⭐⭐⭐⭐⭐, training di **Google Colab GPU**, dataset **Animals-10** (dipilih user dari hasil riset 4 agen web).
  - Hasil riset: yang gugur karena resolusi seragam = Intel Image (150×150), Sports-100 & Vegetable (224×224), Fruits-360 (100×100), PlantVillage (256×256), CIFAR-10. Food-101 gugur (95% tak realistis). Dataset Indonesia (makanan/batik/rempah) semua <10rb. Finalis: Animals-10 / Garbage-12 / Fruit&Veg-Disease → Animals-10 menang karena bukti akurasi ≥95% paling tebal.
  - ⚠️ Intel dari riset: reviewer Dicoding BENERAN memeriksa resolusi tidak seragam (ada kasus submission mengakali dgn resize acak). EDA kita wajib menampilkan bukti ukuran asli beragam.
- **Tahap 1 — Dataset (unduh & verifikasi): ✅ SELESAI (2026-07-09, terverifikasi first-hand)**
  - Venv M1 dibuat (`.venv/`, 3.10.20) + kagglehub/pillow/pandas/matplotlib/seaborn/tensorflow/jupyter.
  - Animals-10 diunduh ke `~/.cache/kagglehub/datasets/alessiocorrado99/animals10/versions/2` (struktur: `raw-img/<kelas-italia>/`, plus `translate.py` kamus Italia→Inggris bawaan dataset).
  - **Angka terverifikasi: 26.179 gambar, 10 kelas, 1.002 ukuran (w,h) unik (lebar 169–640, tinggi 105–640), 0 file korup.** Ekstensi: 24.209 .jpeg / 1.919 .jpg / 51 .png.
  - Distribusi per kelas: cane 4.863, ragno 4.821, gallina 3.098, cavallo 2.623, farfalla 2.112, mucca 1.866, scoiattolo 1.862, pecora 1.820, gatto 1.668, elefante 1.446 → imbalance ~3,4:1 (pertimbangkan class_weight).
  - Kamus rename: cane=dog, cavallo=horse, elefante=elephant, farfalla=butterfly, gallina=chicken, gatto=cat, mucca=cow, pecora=sheep, ragno=spider, scoiattolo=squirrel.
- **Tahap 2–6 — EDA + notebook lengkap: ✅ DITULIS & DIVERIFIKASI (2026-07-09), ⏳ menunggu user run di Colab**
  - EDA diprototype di M1, plot dicek visual via Read (distribusi kelas / bukti resolusi 374 ukuran unik / grid contoh per kelas). Semua benar.
  - **Pipeline end-to-end diprototype di M1 (subset 50/kelas):** split 80/10/10 ✓, augmentasi train-only ✓, model Sequential[Rescaling→MobileNetV2 frozen→Conv2D(256)→MaxPool→GAP→Dropout→Dense] (5,27jt param) ✓, fit ✓ (1 epoch val 84%!), `model.export()` SavedModel ✓, TFLite convert+inference ✓ (21 MB, prediksi benar). TF M1 = 2.21.0.
  - Pencegahan crash Colab: seluruh 26.179 gambar lolos `tf.io.decode_image` (0 gagal; hanya warning iCCP PNG kosmetik).
  - **`submission/notebook.ipynb` dibuat (49 sel, 27 kode)** — generator: scratchpad `build_notebook.py`. Struktur: header→setup(seed 42)→kagglehub download→EDA(3 visual+narasi)→split 80/10/10+rename EN→pipeline+augmentasi(train only)+train_eval_ds jujur→model→callbacks(ES/MC/RLR)→training 2 fase (frozen 8 epoch lr1e-3 → fine-tune layer≥100 s.d. 15 epoch lr1e-5)→evaluasi(train/val/test + plot acc&loss 2 fase + classification report + confusion matrix)→export SavedModel→TFLite+label.txt→TFJS (install PALING AKHIR)→inference TFLite 9 gambar→kesimpulan→zip model.
  - Notebook tervalidasi nbformat + sintaks Python semua sel (ast.parse).
  - Instruksi user: `panduan/Instruksi_Colab.md` (upload→T4 GPU→Run All→cek ≥95%→unduh .ipynb tereksekusi + animals10_models.zip→taruh di submission/).
  - **NEXT:** user run di Colab → bawa balik hasil → Claude packaging (Tahap 7: notebook.py via nbconvert, requirements.txt, README, susun folder, zip, audit final).
  - Keputusan teknis dicatat: class_weight TIDAK dipakai dulu (imbalance 3,4:1 tergolong ringan; memaksimalkan akurasi headline) — kalau test <95% setelah run, opsi tuning: class_weight / unfreeze lebih banyak / epoch tambah.
- **Tahap 7 — Packaging & Audit Final: ✅ SELESAI (2026-07-09)**
  - User sudah Run All di Colab (TF **2.20.0**, GPU T4). Hasil dibawa balik: `notebook.ipynb` (5,4 MB, output ter-embed) + `animals10_models.zip`.
  - **HASIL AKURASI (terverifikasi Claude dari output notebook): Train 98,13% / Val 96,94% / Test 96,61%** → target ≥95% train & test TERCAPAI, gap train-test ~1,5% (tidak overfitting). Notebook 49 sel, **0 error**; plot acc/loss + confusion matrix + inference grid semua ter-embed.
  - Model 3 format di-extract & **load-test di M1**: TFLite input[1,224,224,3]→output[1,10] invoke OK softmax=1.0; SavedModel load OK (sig serve/serving_default); label.txt 10 kelas == output 10 (COCOK).
  - `notebook.py` di-generate via nbconvert (nbconvert keluarkan `.txt` → rename; 3 baris magic Colab `%pip`/`!tensorflowjs_converter` dikomentari agar valid Python — ast.parse OK).
  - `requirements.txt` (tensorflow==2.20.0 + kagglehub/tensorflowjs/numpy/matplotlib/seaborn/scikit-learn/Pillow — pandas TIDAK dipakai, tidak dimasukkan) + `README.md` template Dicoding dibuat.
  - Zip transport `animals10_models.zip` dibuang; folder disusun & di-zip → **`Nazhif_Setya_Nugroho_submission.zip`** (80 MB, 16 berkas, 1 folder `submission/`).
  - **Audit final: SEMUA hard-rule + 6 saran PASS.** ✅ SIAP SUBMIT. (Reminder hard-rule #8: jangan submit berkali-kali; review ±3 hari kerja.)
