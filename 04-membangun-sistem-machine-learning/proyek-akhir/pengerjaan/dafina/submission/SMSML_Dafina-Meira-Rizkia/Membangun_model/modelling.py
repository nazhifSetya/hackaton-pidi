"""Kriteria 2 (Basic) — Pelatihan model klasifikasi spesies penguin.

Model dilatih memakai Gradient Boosting dan dilacak dengan MLflow autolog.
Seluruh artefak disimpan pada tracking store lokal (folder ./mlruns) sehingga
dapat ditinjau melalui MLflow Tracking UI di http://127.0.0.1:5000
(jalankan perintah `mlflow ui` dari folder ini).
"""
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

RANDOM_STATE = 11
PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "penguins_preprocessing.csv"
TARGET = "species"


def load_dataset(path: Path):
    """Membaca dataset hasil preprocessing lalu memisahkan fitur dan target."""
    frame = pd.read_csv(path)
    features = frame.drop(columns=[TARGET])
    labels = frame[TARGET]
    return features, labels


def main():
    # Arahkan MLflow ke tracking store lokal berbasis file.
    mlflow.set_tracking_uri((PROJECT_DIR / "mlruns").as_uri())
    mlflow.set_experiment("Penguins_Species_Classification")

    features, labels = load_dataset(DATA_FILE)
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    # Autolog mencatat parameter, metrik evaluasi, dan artefak model otomatis.
    mlflow.sklearn.autolog()

    with mlflow.start_run(run_name="gradient_boosting_penguins"):
        classifier = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=3,
            random_state=RANDOM_STATE,
        )
        classifier.fit(X_train, y_train)

        skor_latih = classifier.score(X_train, y_train)
        skor_uji = classifier.score(X_test, y_test)
        print(f"Akurasi data latih : {skor_latih:.4f}")
        print(f"Akurasi data uji   : {skor_uji:.4f}")

    print("Pelatihan selesai. Tinjau hasil dengan `mlflow ui` di http://127.0.0.1:5000")


if __name__ == "__main__":
    main()
