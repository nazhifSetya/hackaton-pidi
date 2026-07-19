# Workflow-CI — Re-training Model Spesies Penguin

**Nama:** Dafina Meira Rizkia
**Kelas:** Membangun Sistem Machine Learning (Dicoding)

Repository ini memenuhi **Kriteria 3** proyek akhir: workflow CI berbasis
**MLflow Project** + **GitHub Actions** yang melatih ulang model setiap kali
trigger terpantik (push ke `main` atau `workflow_dispatch`).

## Struktur

```
Workflow-CI/
├── .github/workflows/ci.yml     # workflow GitHub Actions
└── MLProject/
    ├── MLProject                # definisi entry point MLflow Project
    ├── conda.yaml               # environment
    ├── modelling.py             # skrip pelatihan (Gradient Boosting + autolog)
    └── penguins_preprocessing.csv
```

## Cara kerja CI

1. Checkout repo & setup Python 3.11.
2. Pasang dependency (`mlflow`, `scikit-learn`, `pandas`, `numpy`).
3. Jalankan `mlflow run . --env-manager=local` di folder `MLProject`.
4. Arsipkan folder `mlruns` sebagai artifact GitHub Actions.

Menjalankan secara lokal:

```
cd MLProject
mlflow run . --env-manager=local
```
