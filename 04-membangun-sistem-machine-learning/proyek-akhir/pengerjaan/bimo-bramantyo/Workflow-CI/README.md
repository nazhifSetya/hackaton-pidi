# Workflow-CI — Klasifikasi Kultivar Anggur (Bimo Bramantyo)

Repositori Kriteria 3 proyek akhir **Membangun Sistem Machine Learning**.
Berisi MLflow Project untuk melatih ulang model klasifikasi kultivar anggur
(*Wine recognition*) secara otomatis lewat GitHub Actions.

## Struktur

```
Workflow-CI/
├── .github/workflows/ci.yml     # workflow CI (trigger: push ke main & manual)
└── MLProject/
    ├── MLProject                # definisi entry point MLflow Project
    ├── conda.yaml               # dependency environment
    ├── modelling.py             # skrip pelatihan (Pipeline StandardScaler + SVC RBF)
    └── wine_preprocessing.csv   # dataset siap latih (hasil Kriteria 1)
```

## Cara kerja CI

Setiap `push` ke branch `main` atau saat dijalankan manual (`workflow_dispatch`),
GitHub Actions akan:

1. Menyiapkan Python 3.11 + dependency (`mlflow`, `scikit-learn`, `pandas`, `numpy`).
2. Menjalankan `mlflow run . --env-manager=local` di folder `MLProject`, yang
   melatih ulang model dan mencatat parameter/metrik/artefak via MLflow autolog.
3. Mengunggah folder `mlruns` sebagai artefak build (`anggur-mlruns`).

## Menjalankan secara lokal

```bash
cd MLProject
mlflow run . --env-manager=local --experiment-name "Klasifikasi_Kultivar_Anggur_CI"
```
