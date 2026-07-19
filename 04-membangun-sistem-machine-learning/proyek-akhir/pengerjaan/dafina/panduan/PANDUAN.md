# Panduan Proyek Akhir SMSML — Dafina Meira Rizkia

Target: **Basic (2 pts) di keempat kriteria** → nilai akhir Bintang 3 (C, "Basic").
Dataset: **Palmer Penguins** (klasifikasi 3 spesies). Model: **Gradient Boosting** + MLflow.

> Stack sengaja dibedakan dari Nazhif (Pima diabetes, RandomForest) dan Fareynaldi
> (Titanic, LogisticRegression) demi aturan anti-plagiarisme Dicoding. Lihat matriks
> diferensiasi di `../CLAUDE.md`.

---

## ✅ Yang SUDAH selesai & terverifikasi lokal (Victus)

| Kriteria | Status | Bukti |
|---|---|---|
| **1** Eksperimen | ✅ notebook Run All 0-error | `Eksperimen_SML_.../preprocessing/Eksperimen_Dafina-Meira-Rizkia.ipynb` + `penguins_preprocessing.csv` (333×9) |
| **2** Model MLflow | ✅ dilatih (akurasi uji 1.0) + autolog | `Membangun_model/modelling.py`, `mlruns/`, `screenshoot_dashboard.jpg`, `screenshoot_artifak.jpg` |
| **3** Workflow CI | ✅ file lengkap (belum push) | `Workflow-CI/` (MLProject + ci.yml) |
| **4** Monitoring | ✅ serving + Prometheus + Grafana + screenshot | `Monitoring dan Logging/` (5 screenshot: 1 serving, 4 Prometheus, 1 Grafana) |

Zip siap: `submission/SMSML_Dafina-Meira-Rizkia.zip`.

---

## ⏳ Yang MASIH perlu kamu lakukan (butuh akun)

### A. Push 2 repository GitHub PUBLIC (Kriteria 1 & 3)

1. Pastikan `gh` login sebagai akun yang diinginkan:
   ```
   gh auth status
   # kalau mau ganti ke akun Dafina:  gh auth login
   ```
2. Jalankan helper (dari Git Bash):
   ```
   bash panduan/push_repos.sh
   ```
   Skrip ini membuat repo `Eksperimen_SML_Dafina-Meira-Rizkia` dan `Workflow-CI`
   (PUBLIC) lalu push. URL hasil akan tercetak.
3. **Cek GitHub Actions** di repo `Workflow-CI` → tab *Actions* harus **hijau**
   minimal 1× (workflow jalan otomatis setelah push). Kalau merah, buka lognya.

### B. Ganti placeholder username di 2 file `.txt`

Buka dan ganti `<USERNAME-GITHUB>` dengan username asli:
- `Eksperimen_SML_Dafina-Meira-Rizkia.txt`
- `Workflow-CI.txt`

### C. (Opsional) Ganti nama dashboard Grafana ke username Dicoding

Screenshot Grafana saat ini berjudul **"Dafina Meira Rizkia"**. Rubric mewajibkan
nama dashboard = **username akun Dicoding**. Jika username Dicoding-mu BUKAN
"Dafina Meira Rizkia", ulangi langkah monitoring (lihat bagian "Menjalankan ulang")
dengan judul yang benar, lalu ambil ulang screenshot Grafana.

### D. Regenerate zip (setelah A & B)

```
cd submission
python -c "import shutil; shutil.make_archive('SMSML_Dafina-Meira-Rizkia','zip',root_dir='.',base_dir='SMSML_Dafina-Meira-Rizkia')"
```
Lalu upload `submission/SMSML_Dafina-Meira-Rizkia.zip` ke Dicoding.
**Jangan zip-in-zip.**

---

## 🔁 Menjalankan ulang semua (lokal, Victus)

Environment: `.venv` (Python 3.11). Aktifkan dep bila perlu:
```
python -m venv .venv
./.venv/Scripts/python -m pip install -r Membangun_model/requirements.txt flask prometheus_client psutil seaborn matplotlib jupyter nbconvert requests
```

1. **Notebook (Kriteria 1):**
   ```
   cd Eksperimen_SML_Dafina-Meira-Rizkia/preprocessing
   ../../.venv/Scripts/python -m nbconvert --to notebook --execute --inplace Eksperimen_Dafina-Meira-Rizkia.ipynb
   ```
2. **Latih model (Kriteria 2):**
   ```
   cd Membangun_model
   ../.venv/Scripts/python modelling.py
   ../.venv/Scripts/mlflow ui --port 5000        # buka http://127.0.0.1:5000 untuk screenshot
   ```
   Salin artefak model terbaru ke `Monitoring dan Logging/model/` (dari
   `mlruns/<exp>/<run>/artifacts/model`).
3. **Serving + Monitoring (Kriteria 4):**
   ```
   # terminal 1 — layanan model:
   cd "Monitoring dan Logging"
   ../.venv/Scripts/python "3.prometheus_exporter.py"        # port 8501
   # terminal 2 — Prometheus + Grafana:
   cd "Monitoring dan Logging/8.serving_stack"
   docker compose up -d                                       # Prometheus :9090, Grafana :3000
   # generate traffic:
   ../.venv/Scripts/python ../7.inference.py
   ```
   - Grafana: http://127.0.0.1:3000 (anonymous admin). Dashboard "Dafina Meira Rizkia"
     auto ter-provision.
   - Prometheus: http://127.0.0.1:9090/query
   - Teardown: `docker compose down`.

---

## 📌 Catatan penilaian (kenapa Basic aman)

- **K1 Basic:** notebook manual dengan data loading + EDA + preprocessing. ✔
- **K2 Basic:** Scikit-Learn + MLflow **autolog**, tracking lokal (127.0.0.1), 2 screenshot valid. ✔
- **K3 Basic:** folder `MLProject` + workflow CI GitHub Actions yang melatih model saat trigger. ✔
  (bonus: artifact upload — tetap aman untuk Basic).
- **K4 Basic:** serving lokal + Prometheus **4 metrik** (≥3) + Grafana metrik sama +
  nama dashboard = kredensial. ✔ (Alerting = skilled, sengaja TIDAK dikejar.)
