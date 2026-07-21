"""Workflow CI (Kriteria 3) — entry point MLflow Project untuk re-training.

Dipanggil oleh `mlflow run .` pada GitHub Actions setiap workflow terpantik.
Model (Pipeline StandardScaler + SVC RBF) dilatih ulang, dengan autolog MLflow
menuju tracking store lokal (folder ./mlruns pada runner) yang kemudian
diarsipkan sebagai artefak build.
"""
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

DIREKTORI = Path(__file__).resolve().parent
BERKAS_DATA = DIREKTORI / "wine_preprocessing.csv"
KOLOM_TARGET = "target_kultivar"
ACAK = 17


def bangun_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("penskalaan", StandardScaler()),
            ("svc", SVC(kernel="rbf", C=10.0, gamma="scale",
                        probability=True, random_state=ACAK)),
        ]
    )


def main():
    # Lokasi tracking sengaja disamakan dengan default `mlflow run` (./mlruns
    # pada folder proyek) agar tidak terjadi ketidakcocokan run.
    mlflow.set_tracking_uri((DIREKTORI / "mlruns").as_uri())
    mlflow.set_experiment("Klasifikasi_Kultivar_Anggur_CI")

    tabel = pd.read_csv(BERKAS_DATA)
    X = tabel.drop(columns=[KOLOM_TARGET])
    y = tabel[KOLOM_TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=ACAK, stratify=y
    )

    mlflow.sklearn.autolog()
    with mlflow.start_run(run_name="ci_svc_rbf_anggur"):
        model = bangun_pipeline()
        model.fit(X_train, y_train)
        print(f"Akurasi latih: {model.score(X_train, y_train):.4f}")
        print(f"Akurasi uji  : {model.score(X_test, y_test):.4f}")

    print("Re-training CI selesai.")


if __name__ == "__main__":
    main()
