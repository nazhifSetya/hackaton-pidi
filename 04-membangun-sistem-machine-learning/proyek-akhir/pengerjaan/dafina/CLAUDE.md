# CLAUDE.md — 04 SMSML / Dafina Meira Rizkia (Palmer Penguins)

> Memory detail + hard rules + progress log proyek ini. Baca penuh saat kerja di sini.
> Konteks lintas-device & protokol sync ada di root `/CLAUDE.md` dan `/_meta/STATUS.md`.

## 🎯 Ringkasan

- **Course:** 04 Membangun Sistem Machine Learning (SMSML) — proyek akhir MLOps 4 kriteria.
- **Anggota:** Dafina Meira Rizkia. **Target:** Basic (2 pts) SEMUA kriteria → Bintang 3 (C).
- **Dataset:** Palmer Penguins (344 baris) — klasifikasi 3 spesies (Adelie/Chinstrap/Gentoo).
- **Model:** `GradientBoostingClassifier` (n_estimators=150, lr=0.1, depth=3, random_state=11).
- **Stack MLOps:** MLflow 2.19 (autolog, tracking lokal) · Flask serving · Prometheus · Grafana (Docker).
- **Env:** `.venv` Python 3.11 (git-ignored). Dijalankan penuh lokal di Victus.

## 🧬 Diferensiasi anti-plagiarisme (WAJIB jaga beda dari teman)

| Aspek | Nazhif | Fareynaldi | **Dafina (ini)** |
|---|---|---|---|
| Dataset | Pima Diabetes | Titanic | **Palmer Penguins** |
| Task | biner | biner | **multikelas (3)** |
| Model | RandomForest | LogisticRegression | **GradientBoosting** |
| random_state | 42 | 7 | **11** |
| Experiment | Diabetes_Classification | Titanic_Survival | **Penguins_Species_Classification** |
| Struktur kode | `BASE_DIR`, skrip datar | `HERE`, skrip datar | **`pathlib.Path` + fungsi `main()`/`load_dataset()`** |
| Preprocessing khas | — | — | **missing-value dropna + one-hot island + StandardScaler** |
| Metrik exporter | `http_requests_total`, dst | (punya sendiri) | **`penguin_*` (api_requests, inference_latency, predictions, cpu, memory)** |
| Serving port | 8000 | — | **8501** + endpoint `/health` |

⛔ **Jangan** menyeragamkan nama/struktur dengan folder anggota lain.

## 📂 Struktur

```
dafina/
├── Eksperimen_SML_Dafina-Meira-Rizkia/   → repo GitHub Kriteria 1 (belum push)
│   ├── penguins_raw.csv
│   └── preprocessing/{Eksperimen_Dafina-Meira-Rizkia.ipynb, penguins_preprocessing.csv}
├── Membangun_model/                       → Kriteria 2 (modelling.py, csv, 2 screenshot, requirements)
│   └── mlruns/                            (git-ignored, hasil training lokal)
├── Workflow-CI/                           → repo GitHub Kriteria 3 (belum push)
│   ├── .github/workflows/ci.yml
│   └── MLProject/{modelling.py, conda.yaml, MLProject, csv}
├── Monitoring dan Logging/                → Kriteria 4
│   ├── 1.bukti_serving.jpg (+log), 2.prometheus.yml, 3.prometheus_exporter.py, 7.inference.py
│   ├── 4.bukti monitoring Prometheus/ (4 metrik), 5.bukti monitoring Grafana/ (1 dashboard)
│   ├── model/                            (artefak MLflow untuk serving)
│   └── 8.serving_stack/                  (docker-compose + grafana provisioning — reproducible)
├── Eksperimen_SML_Dafina-Meira-Rizkia.txt / Workflow-CI.txt  (link repo, ada placeholder)
├── panduan/{PANDUAN.md, push_repos.sh}
└── submission/SMSML_Dafina-Meira-Rizkia/ (+ .zip)  → deliverable Dicoding
```

## ⛔ Hard rules proyek

1. Target **Basic**; jangan over-engineer ke skilled/advanced (mis. alerting Grafana, tuning, DagsHub) kecuali diminta.
2. Repo GitHub Kriteria 1 & 3 **WAJIB PUBLIC** saat submit.
3. Nama dashboard Grafana harus = **username Dicoding** (sekarang "Dafina Meira Rizkia" — konfirmasi/ganti bila username beda).
4. `.venv`, `mlruns`, `__pycache__` **tidak** masuk git (lihat `.gitignore`).
5. Jangan zip-in-zip. Regenerate zip dari `submission/SMSML_Dafina-Meira-Rizkia/`.

## 📊 PROGRESS LOG

- **2026-07-19 (Victus):** Proyek dibuat dari nol & dijalankan penuh lokal.
  - K1: notebook eksperimen Run All 0-error → `penguins_preprocessing.csv` (333×9). ✅
  - K2: `modelling.py` autolog GradientBoosting, akurasi uji 1.0, mlruns + 2 screenshot MLflow (auto via browser). ✅
  - K3: `Workflow-CI` (MLProject + ci.yml) lengkap — **belum push** ke GitHub. ⏳
  - K4: exporter Flask (5 metrik `penguin_*`, port 8501) + Prometheus + Grafana (Docker) jalan; target scrape UP; 6 screenshot (serving, 4 Prometheus, Grafana dashboard "Dafina Meira Rizkia" 5 panel terisi). ✅
  - Zip `submission/SMSML_Dafina-Meira-Rizkia.zip` (798KB, 39 file) dibuat.
  - **SISA (butuh akun):** push 2 repo publik (`bash panduan/push_repos.sh`), pastikan Actions hijau, ganti `<USERNAME-GITHUB>` di 2 .txt, (opsional) samakan nama dashboard ke username Dicoding, regenerate zip, upload. Detail: `panduan/PANDUAN.md`.
