# CLAUDE.md — Proyek ML BMLP (Clustering + Klasifikasi)

> **File ini = memory + HARD rules untuk project ini.** Baca SELURUHNYA di awal tiap sesi sebelum mengerjakan apa pun.
> **Update bagian [Progress Log](#-progress-log-living-section) setiap kali menyelesaikan satu kriteria.** Ini sumber kebenaran status pengerjaan.

---

## ⛔ SCOPE — BACA INI DULU

- Project ini adalah **submission Dicoding "Belajar Membangun Machine Learning Project" (BMLP)**. Lokasinya kebetulan di dalam `Everest/docs/hackaton_PIDI/`, **TAPI sama sekali TIDAK berhubungan dengan aplikasi Everest (EBC).**
- **Aturan dari `Everest/CLAUDE.md` dan `docs/CLAUDE.md` TIDAK BERLAKU di sini.** Abaikan semua hal soal: backoffice-service/core/consumer, Sequelize, migrations, schema.sql, Hoppscotch, DocuSign, CLIK, Vault, wiki claude-obsidian, dll. **Jangan** sentuh/ubah file di luar folder project ini.
- Project ini **self-contained**. Semua yang relevan ada di folder ini.

---

## 👤 USER & GAYA KERJA

- **Nama user:** Nazhif Setya Nugroho → dipakai di nama file: `Nazhif_Setya_Nugroho`.
- **Email:** dev@kalachakra.io
- **Konteks:** Ini **proyek Machine Learning PERTAMA** user. Dia junior developer.
- **Cara komunikasi (WAJIB):**
  - **Bahasa Indonesia yang simpel**, mudah dimengerti junior.
  - **Pelan-pelan, step-by-step.** Jelaskan _kenapa_ tiap langkah dilakukan, bukan cuma _apa_.
  - **Teliti terhadap detail kecil.** User secara eksplisit minta ini.
  - **Jangan asumsi.** Kalau ambigu (nama field, pilihan algoritma, dll), **tanya dulu** pakai AskUserQuestion sebelum nulis kode.
- **Target nilai yang disepakati:** **ADVANCED / SEMPURNA (⭐⭐⭐⭐⭐, nilai 4.0)** — semua 5 kriteria dikejar sampai level Advanced.
- **Pembagian kerja K2–K5 (DISEPAKATI — pilihan "campur"):** Claude **isi blank + verifikasi logika via prototype** (script `.venv/bin/python` ke data asli) lalu **jelaskan tiap isian + kenapa**; **USER yang MENJALANKAN cell sendiri** di VSCode (kernel `bmlp-venv`) untuk lihat output asli & belajar nge-run notebook. → **Claude TIDAK auto-embed output lagi** (kecuali user minta); output ter-embed saat USER run & save. Untuk K3, Claude tetap prototype dulu untuk pastikan silhouette score bagus sebelum user run.
- **Checklist progress** dibuka user pakai ekstensi **Markdown Preview Enhanced** → file `.md` boleh kaya visual (mermaid, badge HTML, `<progress>`, `<details>`, emoji).

---

## 🎯 INTI PROYEK (apa yang dikerjakan)

Membangun **2 notebook** yang nyambung berurutan, pakai dataset transaksi bank **tanpa label**:

1. **Notebook Clustering (unsupervised):** EDA → preprocessing → K-Means → hasilkan kolom label bernama **`Target`** → export CSV.
2. **Notebook Klasifikasi (supervised):** pakai data ber-`Target` dari langkah 1 → latih model untuk memprediksi `Target`.

Yang dinilai: kemampuan menggabungkan unsupervised + supervised dalam satu alur.

---

## 📁 STRUKTUR FOLDER

```
Membangun_Proyek_Machine_Learning/
├── CLAUDE.md                  ← file ini (memory + rules)
├── .python-version            ← pin pyenv: 3.10.20
├── .venv/                     ← virtual environment lokal (JANGAN di-commit/zip)
├── artifact/                  ← 📦 BAHAN ASLI DICODING — READ-ONLY, jangan diubah
│   ├── Dataset/               ← bank_transactions_data_edited.csv (+ .xlsx)
│   ├── Instruksi/             ← 6 file .md instruksi + gambar (sumber kebenaran kriteria)
│   ├── Template_Clustering/   ← template asli (.ipynb + .py)
│   └── Template_Klasifikasi/  ← template asli (.ipynb + .py)
├── panduan/
│   └── Checklist_Pengerjaan.md ← 📋 tracker progres (update tiap kriteria selesai)
└── submission/                ← 💻 FILE KERJA + OUTPUT (yang nanti di-zip)
    ├── README.md
    ├── [Clustering]_Submission_Akhir_BMLP_Nazhif_Setya_Nugroho.ipynb   (83 cells)
    └── [Klasifikasi]_Submission_Akhir_BMLP_Nazhif_Setya_Nugroho.ipynb
```

---

## 🐍 ENVIRONMENT (HARD — cara menjalankan)

- **Python:** pyenv `3.10.20` (di-pin via `.python-version`). scikit-learn 1.7.0 butuh Python ≥ 3.10.
- **Virtual env:** `.venv/` (dibuat dari pyenv 3.10.20).
- **Selalu jalankan Python lewat:** `.venv/bin/python` (jangan `python3` sistem — itu 3.14 & kosong library).
- **Library terinstall (versi terverifikasi jalan bareng):**
  - `scikit-learn==1.7.0` ← **DIPIN sesuai anjuran Dicoding** (jangan diubah)
  - `yellowbrick==1.5` (untuk `KElbowVisualizer`) — **sudah diverifikasi kompatibel dengan sklearn 1.7.0**
  - `pandas`, `numpy`, `matplotlib`, `seaborn`, `joblib`, `jupyter`, `openpyxl`
- **Install ulang (kalau perlu):**
  ```bash
  uv pip install --python .venv/bin/python "scikit-learn==1.7.0" pandas numpy matplotlib seaborn yellowbrick jupyter joblib openpyxl
  ```
- **Smoke test environment sudah LULUS** (KElbowVisualizer + KMeans + silhouette_score jalan).
- **Kernel Jupyter terdaftar:** `bmlp-venv` (display: "Python (BMLP .venv)") → menunjuk ke `.venv`. Dipakai untuk run notebook di VSCode/nbclient.
- **Cara embed output per kriteria (tanpa Run All penuh):** eksekusi sebagian cell via nbclient lalu tulis balik output-nya:
  ```python
  import nbformat, copy; from nbclient import NotebookClient
  nb = nbformat.read(path, as_version=4); sub = copy.deepcopy(nb); sub.cells = sub.cells[:N]
  NotebookClient(sub, timeout=600, kernel_name="bmlp-venv", resources={"metadata":{"path":"submission/"}}).execute()
  for i in range(N): nb.cells[i] = sub.cells[i]
  nbformat.write(nb, path)
  ```

---

## 🔴 HARD RULES — AUTO-REJECT KALAU DILANGGAR

Sumber: `artifact/Instruksi/5.ketentuan_berkas_submission.md` & catatan "Penting" di tiap template.

### Aturan mengisi template
1. **Isi HANYA bagian `________`** yang berada di antara `### MULAI CODE ###` dan `### SELESAI CODE ###`.
2. **JANGAN tambah `import`** library/function baru. Semua sudah disediakan di cell import paling atas. (Boleh nambah baris kode di area MULAI/SELESAI bila instruksi memang minta >1 model, mis. model klasifikasi tambahan.)
3. **JANGAN ubah/hapus cell teks (markdown)** bawaan. Cuma kerjakan cell kode.
4. **Variabel utama HARUS tetap `df`** dari awal sampai akhir — jangan ganti nama.
5. **WAJIB pakai template** yang disediakan (jangan bikin dari nol).
6. **Setiap cell yang harusnya keluar output WAJIB ada output-nya** → **Run All** sebelum submit. Cell tanpa output = dianggap belum selesai / reject.
7. **JANGAN tambah cell/line kode yang tidak diminta.**

### Aturan spesifik kriteria
8. **Kriteria 1 (EDA): DILARANG pakai `print()` / `display()`.** Cukup ekspresi polos sebagai baris terakhir cell (mis. `df.head()`) biar Jupyter auto-tampilkan. `print(df.head())` → REJECT.
9. **Nama kolom label hasil clustering HARUS persis `Target`.**
10. **Model klasifikasi WAJIB menampilkan Accuracy & F1-Score pada testing set.**
11. Klasifikasi **WAJIB pakai label `Target`** hasil clustering (bukan label lain).

### Nama file output (HARUS PERSIS)
12. Jalankan `joblib.dump()` dengan nama **tepat**:
    - `model_clustering.h5` (wajib)
    - `decision_tree_model.h5` (wajib)
    - `PCA_model_clustering.h5` (Advanced K3)
    - `explore_<NamaAlgoritma>_classification.h5` (Skilled K5)
    - `tuning_classification.h5` (Advanced K5)
13. Export data: `data_clustering.csv` (wajib), `data_clustering_inverse.csv` (Advanced K4).

### Larangan teknologi
14. **DILARANG pakai AutoML:** PyCaret, Auto-sklearn, TPOT, H2O Driverless AI, Microsoft Azure AutoML, Google Cloud AutoML, DataRobot, RapidMiner Auto Model, Amazon SageMaker Autopilot, IBM Watson AutoAI.

### Lain-lain
15. **Jangan submit berkali-kali** (memperlama antrian review; review ±3 hari kerja).
16. Dataset **WAJIB dari Google Drive/URL yang disediakan**, BUKAN dari Kaggle (datanya beda).

---

## 🧭 METODOLOGI KERJA (cara yang disepakati)

1. **VERTICAL per-kriteria, bukan horizontal.** Kerjakan K1 → K2 → K3 → K4 → K5 berurutan, dan **tiap kriteria langsung dituntaskan sampai Advanced** (Basic+Skilled+Advanced sekaligus). Alasan: notebook = pipeline berurutan & saling tergantung; ngerjain per-level (semua Basic dulu, baru Skilled, dst) malah harus keliling notebook 3x + banyak re-run. (Lihat diskusi di histori.)
2. **VERIFY-FIRST (wajib).** Sebelum nulis ke notebook:
   - Prototype logika kriteria itu ke **data asli** lewat script `.venv/bin/python` (jangan tulis output prototype ke folder submission).
   - Untuk plot, simpan PNG ke `/tmp/` lalu **lihat pakai Read tool** untuk verifikasi visual (mis. cek label tidak overlap untuk Advanced).
   - Baru isi blank setelah yakin angkanya/visualnya benar.
3. **Cara mengisi blank notebook (anti-corrupt):** pakai script Python yang `json.load` notebook → ganti `________` **berurutan** per cell → `assert` jumlah blank == jumlah nilai & `assert` 0 blank tersisa → `json.dump` balik. JANGAN edit JSON pakai string-replace manual yang rapuh.
4. **Cek isi cell dulu sebelum mengisi.** Baca source asli tiap cell (lewat script) untuk tahu nama variabel & struktur yang diharapkan template.
5. **Setelah tiap kriteria selesai:** update `panduan/Checklist_Pengerjaan.md` (centang Basic/Skilled/Advanced + dashboard + `<progress>`) DAN update [Progress Log](#-progress-log-living-section) di file ini.
6. **Output di-embed di AKHIR.** Notebook tidak bisa `Run All` sampai SEMUA blank terisi (cell kosong → error). Jadi: verifikasi tiap kriteria via prototype dulu; baru di **FASE AKHIR** jalankan `Run All` sekali untuk embed semua output.
   - Perkiraan command final (konfirmasi/registrasi kernel saat FASE AKHIR):
     ```bash
     .venv/bin/python -m ipykernel install --user --name bmlp-venv   # sekali, kalau perlu
     .venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace \
       --ExecutePreprocessor.timeout=600 \
       "submission/[Clustering]_Submission_Akhir_BMLP_Nazhif_Setya_Nugroho.ipynb"
     ```

---

## 📋 5 KRITERIA + PETA CELL + SYARAT LEVEL

Penilaian bertingkat: **Reject(0) → Basic(2) → Skilled(3) → Advanced(4)**. Level atas mencakup syarat level bawah. Sumber lengkap: `artifact/Instruksi/2.kriteria_utama.md`.

### Notebook CLUSTERING (83 cells) — K1–K4

| Kriteria | Level | Cell | Tugas |
|---|---|---|---|
| **K1 EDA** | 🟢 | 7,8,10,12 | load `pd.read_csv(url)`, `head()`, `info()`, `describe()` |
| | 🔵 | 14,17 | matriks korelasi (`.corr()`+`sns.heatmap`), histogram numerik (`sns.histplot`, grid 2×3) |
| | 🟣 | 21 | viz informatif (boxplot) — **label tidak overlap** (`plt.xticks(rotation=45)`) |
| **K2 Preprocessing** | 🟢 | 23,26,28,31,33,36,39 | `isnull().sum()`, `duplicated().sum()`, `dropna()`, `drop_duplicates()`, **drop kolom ID/Address/Date**, `LabelEncoder()`, `columns.tolist()` (cell 39 kode lengkap, tinggal run) |
| | 🔵 | 43,46 | handling outlier (metode **drop**), `StandardScaler()` |
| | 🟣 | 50 | **binning** 1–2 fitur numerik + encode hasil binning (`LabelEncoder`) |
| **K3 Model Clustering** | 🟢 | 52,53,56,58 | `describe()` (pastikan pakai data preprocessed), Elbow (`KElbowVisualizer`), `KMeans`, `joblib.dump(..., "model_clustering.h5")` |
| | 🔵 | 60,61 | `silhouette_score`, visualisasi hasil clustering |
| | 🟣 | 65,66 | `PCA`, `joblib.dump(model,"PCA_model_clustering.h5")` |
| **K4 Interpretasi** | 🟢 | 69,72,73 | analisis deskriptif per cluster (mean/min/max), ubah nama kolom → **`Target`**, simpan **`data_clustering.csv`**. Cell 70 (markdown) = tempat **menulis narasi** karakteristik cluster. |
| | 🔵 | 75,76,77 | `inverse_transform()` numerik, inverse encoded→kategori, analisis deskriptif data inverse (numerik+kategorikal). Cell 78 = narasi. |
| | 🟣 | 80,81 | periksa data inverse, simpan **`data_clustering_inverse.csv`** |

> ⚠️ **Kolom drop di K2 (cell 33):** logika template = list comprehension `'id'/'ip'/'date' in col.lower()`, jadi yang kebuang **7 kolom**: `TransactionID`, `AccountID`, `PreviousTransactionDate`, `DeviceID`, `IP Address`, `MerchantID`, `TransactionDate` (termasuk **PreviousTransactionDate** karena ada kata "date"). Sisa **9 kolom**. Catatan: nama kolomnya **`IP Address`** (pakai spasi). Cell 39 blank-nya pakai **`____` (4 underscore)**, bukan 8.
>
> 📊 **Hasil pipeline K2 (terverifikasi):** dropna 2537→2156, drop_duplicates →2135, drop kolom →9 kolom, LabelEncoder 4 kolom kategorikal (TransactionType/Location/Channel/CustomerOccupation), outlier IQR →1945 baris, StandardScaler (mean≈0), binning `CustomerAge`→`AgeGroup` (qcut 3 grup Muda/Dewasa/Tua, distribusi 639/669/637). **Final dataset preprocessed = (1945, 10).**

### Notebook KLASIFIKASI — K5

| Kriteria | Level | Tugas |
|---|---|---|
| **K5 Klasifikasi** | 🟢 | load data hasil clustering (`pd.read_csv`), `head()`, `train_test_split` (X=`df.drop('Target',axis=1)`, y=`Target`, `stratify=y`, `random_state=42`), Decision Tree + `fit`, `joblib.dump(..., 'decision_tree_model.h5')` |
| | 🔵 | model lain (mis. `RandomForestClassifier`) + `fit`, `classification_report` semua model (Acc/Precision/Recall/F1), `joblib.dump(new_model, 'explore_<Algo>_classification.h5')` |
| | 🟣 | hyperparameter tuning (`GridSearchCV`/`RandomizedSearchCV`), `classification_report` model tuned, `joblib.dump(new_model_tuned, 'tuning_classification.h5')` |

> 🔑 **DEPENDENSI K4→K5 (PENTING karena kita ambil Advanced):** Karena K4 dikerjakan sampai **Advanced** (menghasilkan `data_clustering_inverse.csv`), maka di K5:
> - Load **`data_clustering_inverse.csv`** (bukan `data_clustering.csv`).
> - **WAJIB** isi cell "(OPSIONAL) Feature Encoding: One Hot Encoding" (`pd.get_dummies(df, columns=..., drop_first=True)`) karena data inverse masih punya kolom kategorikal asli.
> - Variabel split-nya jadi `df_encoded` (lihat template Klasifikasi).

---

## 📊 FORMULA NILAI

```
Nilai Akhir = Total Poin ÷ 5 kriteria
```

| Nilai | Bintang | Huruf | Level |
|---|---|---|---|
| < 1 | Rejected | E | Gagal |
| 1–<2 | ⭐⭐ | D | Below Basic |
| 2–<3 | ⭐⭐⭐ | C | Basic (lulus) |
| 3–<4 | ⭐⭐⭐⭐ | B | Skilled |
| **4** | **⭐⭐⭐⭐⭐** | **A** | **Advanced ← TARGET** |

⚠️ Kalau **1 kriteria saja kena Reject (0)**, rata-rata anjlok & bisa gagal. **Jangan ada yang nol.**

---

## 📦 PACKAGING & SUBMIT (FASE AKHIR)

- Pastikan kedua notebook sudah **Run All** (semua cell ada output, tanpa error).
- Kumpulkan ke **1 folder**, lalu **zip** (struktur **flat**, tanpa subfolder). Nama: `BMLP_Nazhif_Setya_Nugroho.zip`.
- **Isi wajib:** 2 notebook `.ipynb`, `model_clustering.h5`, `decision_tree_model.h5`, `data_clustering.csv`.
- **Isi opsional (karena target Advanced, sertakan semua):** `PCA_model_clustering.h5`, `explore_<Algo>_classification.h5`, `tuning_classification.h5`, `data_clustering_inverse.csv`.
- **JANGAN** ikut-zip `.venv/`, `artifact/`, `panduan/`, `__pycache__`, `.python-version`.

---

## 📌 FAKTA DATASET (terverifikasi)

- Sumber load: URL Google Sheets di cell 7 notebook Clustering (`pd.read_csv(url)`) — **terbukti bisa diakses**.
- Shape mentah: **(2537, 16)**. (Markdown "INFORMASI DATASET" di notebook menyebut 2512 — itu deskripsi dataset Kaggle asli; versi "edited" sengaja ditambah data kotor.)
- **16 kolom**: 5 numerik + 11 object.
  - **Numerik (5):** `TransactionAmount`, `CustomerAge`, `TransactionDuration`, `LoginAttempts`, `AccountBalance`.
  - **Object (11):** `TransactionID`, `AccountID`, `PreviousTransactionDate`, `TransactionType`, `Location`, `DeviceID`, `IP Address`, `MerchantID`, `Channel`, `CustomerOccupation`, `TransactionDate`.
- **Data sengaja kotor** (untuk K2): **403 nilai missing + 21 baris duplikat**. Setelah dibersihkan mendekati ~2512 baris.

---

## 🔗 FILE KUNCI

- Kriteria lengkap & level → `artifact/Instruksi/2.kriteria_utama.md`
- Aturan berkas + urutan cell wajib + larangan → `artifact/Instruksi/5.ketentuan_berkas_submission.md`
- Tabel penilaian → `artifact/Instruksi/3.ketentuan_penilaian.md`
- Pengantar + alur → `artifact/Instruksi/1.Pengantar.md`
- Tips urutan kerja (diagram) → `artifact/Instruksi/4.tips_and_trick.md`
- Review mandiri (checklist Dicoding) → `artifact/Instruksi/6.review_mandiri.md`
- Tracker progres (selalu update) → `panduan/Checklist_Pengerjaan.md`

---

## ✅ PROGRESS LOG (living section)

> **WAJIB diupdate tiap kriteria selesai.** Format: tanggal (jika relevan) + apa yang dikerjakan + status verifikasi.

- **FASE 0 — Persiapan: ✅ SELESAI**
  - Dataset tersedia di `artifact/Dataset/`.
  - Template disalin & di-rename ke `submission/` (Clustering + Klasifikasi, atas nama Nazhif_Setya_Nugroho).
  - Environment lokal siap: pyenv 3.10.20 → `.venv` → scikit-learn 1.7.0 + yellowbrick + jupyter. Smoke test lulus.
  - Aturan template dipahami & akan dipatuhi ketat.
- **K1 — EDA: ✅ SELESAI (Basic+Skilled+Advanced)**
  - Cell terisi: 7 (`pd.read_csv(url)`), 8 (`head`), 10/12 (`df.info()`/`df.describe()`), 14 (`corr`+`heatmap`), 17 (`histplot`+`ax=axes[i]`), 21 (`boxplot` x=`CustomerOccupation` y=`TransactionAmount` + `xticks(rotation=45)`).
  - Diverifikasi via prototype ke data asli + cek visual plot (boxplot & histogram rapi, label tidak overlap). Semua blank K1 = 0 tersisa.
  - ✅ Output K1 SUDAH di-embed ke notebook (cell 0–21 dieksekusi via nbclient kernel `bmlp-venv`): head/info/describe + 3 grafik tampil.
  - Sisa blank: K2=37, K3=32, K4=22 (Clustering) + K5=46 (Klasifikasi).
- **K2 — Preprocessing: ✅ SELESAI (Basic+Skilled+Advanced)**
  - Cell terisi: 23 (`isnull().sum()`), 26 (`duplicated().sum()`), 28 (`dropna`), 31 (`drop_duplicates`), 33 (drop 7 kolom id/ip/date), 36 (`LabelEncoder` 4 kolom), 39 (`df.columns.tolist()`), 43 (outlier IQR drop), 46 (`StandardScaler`), 50 (binning `AgeGroup`).
  - Diverifikasi via prototype ke data asli (pipeline penuh jalan, final 1945×10). Semua blank K2 = 0 tersisa.
  - ⏳ Output belum di-embed (USER yang run sendiri di VSCode sesuai kesepakatan "campur").
- **K3 — Model Clustering: ✅ SELESAI (Basic+Skilled+Advanced)**
  - Cell terisi: 52 (`df.copy()`+`describe()`), 53 (Elbow `KElbowVisualizer` metric=silhouette → **k=2**), 56 (`KMeans(n_clusters=2, random_state=42)`), 58 (`joblib.dump(model,"model_clustering.h5")`), 60 (`silhouette_score` = **0.572**), 61 (viz PCA 2D + scatterplot hue=Cluster), 65 (PCA n=2 + KMeans baru `kmeans_pca`), 66 (`joblib.dump(kmeans_pca,"PCA_model_clustering.h5")`).
  - **Diverifikasi end-to-end** (eksekusi cell asli 0–66 via nbclient): no error, silhouette 0.5720, Elbow+cluster viz render, kedua `.h5` ter-generate. PCA 2 komponen = 97.1% variance.
  - **k=2** konsisten dgn template (`palette n_colors=2`). ⏳ Output belum di-embed (USER yang run).
- **K4 — Interpretasi: ✅ SELESAI (Basic+Skilled+Advanced)**
  - Cell terisi: 69 (`groupby('Cluster').agg(mean/min/max)`), 70 (narasi scaled), 72 (rename Cluster→**Target**), 73 (`to_csv data_clustering.csv`), 75 (`scaler.inverse_transform`), 76 (`encoder.inverse_transform` per kolom), 77 (agg numerik+mode kategorikal), 78 (narasi inverse + rekomendasi), 80 (cek df_inverse), 81 (`to_csv data_clustering_inverse.csv`).
  - **Temuan cluster (terverifikasi):** 2 cluster seimbang (980/965). Profil NUMERIK nyaris identik; pembeda utama = KATEGORIKAL (Location Charlotte vs Tucson, Occupation Doctor vs Student, AgeGroup Dewasa vs Muda). Narasi ditulis jujur sesuai data.
  - **NOTEBOOK CLUSTERING SELESAI 100%** — Full Run All terverifikasi (nbclient, no error). `data_clustering.csv` (1945×11) & `data_clustering_inverse.csv` (1945×11, kategorikal masih `object`/string) + 2 `.h5` ter-generate. ⏳ Output belum di-embed (USER yang Run All & save).
- **K5 — Klasifikasi: ✅ SELESAI (Basic+Skilled+Advanced)**
  - Cell terisi: 4 (`pd.read_csv("data_clustering_inverse.csv")`), 5 (head), 7 (One Hot `pd.get_dummies` → 56 fitur), 9 (`train_test_split` test_size=0.2 stratify=y), 11 (`DecisionTreeClassifier`), 12 (save `decision_tree_model.h5`), 15 (`RandomForestClassifier`), 16 (`classification_report` 2 model), 17 (save `explore_RandomForest_classification.h5`), 19 (`GridSearchCV` tuning RF), 20 (report tuned), 21 (save `tuning_classification.h5`).
  - **Diverifikasi end-to-end** (nbclient, no error): DT/RF/Tuned semuanya **Acc=1.00, F1=1.00** (wajar: Target turunan dari fitur yg sama, terutama Location). 3 model `.h5` ter-generate. Algoritma kedua = RandomForest; tuning = GridSearchCV.
  - ⏳ Output belum di-embed (USER yang Run All & save).
- **🏁 SEMUA 5 KRITERIA SELESAI (semua Advanced).** Proyeksi nilai = 20/5 = **4.0 ⭐⭐⭐⭐⭐**.
- **🏆 HASIL AKHIR: LULUS — ADVANCED (4.0) ⭐⭐⭐⭐⭐** (semua 5 kriteria Advanced valid). Feedback reviewer tersimpan di `panduan/Feedback_Reviewer_Dicoding.md`. **PROYEK SELESAI 100%.** (Saran lanjut reviewer: kelas "Belajar Pengembangan Machine Learning".)
- **FASE AKHIR — Packaging: ✅ SELESAI** (sudah di-upload & lulus)
  - KEDUA notebook sudah Run All + save oleh user: 0 blank tersisa, output ter-embed (verified: Clustering 2.2MB, Klasifikasi 130KB).
  - 9 file submission lengkap di `submission/`. Zip flat dibuat: **`BMLP_Nazhif_Setya_Nugroho.zip`** (di root project, 4.9MB, 9 file, tanpa .venv/artifact/panduan/README/.DS_Store).
  - **SISA: user upload zip ke Dicoding** (+ cek review-mandiri Dicoding, jangan submit berkali-kali, review ±3 hari kerja).
  - Kalau zip perlu dibuat ulang: `zip -j -X BMLP_Nazhif_Setya_Nugroho.zip submission/<9 file>` (lihat daftar di PACKAGING).
