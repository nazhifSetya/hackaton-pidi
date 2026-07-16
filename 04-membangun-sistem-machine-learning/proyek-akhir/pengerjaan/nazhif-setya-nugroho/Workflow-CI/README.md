# Workflow-CI — Diabetes Classification

Kriteria 3 (Membuat Workflow CI) — kelas *Membangun Sistem Machine Learning* (Dicoding).

CI menggunakan **MLflow Project** untuk melakukan re-training model klasifikasi
diabetes (Pima Indians Diabetes) secara otomatis melalui **GitHub Actions** setiap
kali ada `push` ke branch `main` atau dijalankan manual (`workflow_dispatch`).

## Struktur

```
Workflow-CI/
├── .github/workflows/ci.yml     # workflow GitHub Actions
└── MLProject/
    ├── MLProject                # definisi MLflow Project
    ├── conda.yaml               # dependencies
    ├── modelling.py             # entry point training (autolog)
    └── diabetes_preprocessing.csv
```

## Menjalankan secara lokal

```bash
cd MLProject
mlflow run . --env-manager=local --experiment-name "Diabetes_Classification_CI"
```
