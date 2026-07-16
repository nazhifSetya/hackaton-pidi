# Workflow-CI — Titanic Survival

Kriteria 3 (Membuat Workflow CI) — kelas *Membangun Sistem Machine Learning* (Dicoding).

Continuous Integration menggunakan **MLflow Project** untuk melatih ulang model
prediksi keselamatan penumpang Titanic secara otomatis lewat **GitHub Actions**
setiap ada `push` ke `main` atau saat dijalankan manual (`workflow_dispatch`).

## Struktur

```
Workflow-CI/
├── .github/workflows/ci.yml
└── MLProject/
    ├── MLProject
    ├── conda.yaml
    ├── modelling.py
    └── titanic_preprocessing.csv
```

## Menjalankan lokal

```bash
cd MLProject
mlflow run . --env-manager=local --experiment-name "Titanic_Survival_CI"
```
