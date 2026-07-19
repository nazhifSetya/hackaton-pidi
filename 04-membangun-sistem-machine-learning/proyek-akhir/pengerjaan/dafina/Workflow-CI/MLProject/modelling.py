"""Workflow CI (Kriteria 3) — entry point MLflow Project untuk re-training.

Dipanggil oleh `mlflow run .` pada GitHub Actions. Model Gradient Boosting
dilatih ulang setiap workflow terpantik, dengan autolog MLflow menuju tracking
store lokal (folder ./mlruns pada runner).
"""
from pathlib import Path

import mlflow
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

RANDOM_STATE = 11
HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "penguins_preprocessing.csv"
TARGET = "species"


def main():
    mlflow.set_tracking_uri((HERE / "mlruns").as_uri())
    mlflow.set_experiment("Penguins_Species_CI")

    data = pd.read_csv(DATA_FILE)
    X = data.drop(columns=[TARGET])
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    mlflow.sklearn.autolog()
    with mlflow.start_run(run_name="ci_gradient_boosting"):
        model = GradientBoostingClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=3, random_state=RANDOM_STATE
        )
        model.fit(X_train, y_train)
        print(f"Akurasi latih: {model.score(X_train, y_train):.4f}")
        print(f"Akurasi uji  : {model.score(X_test, y_test):.4f}")

    print("Re-training CI selesai.")


if __name__ == "__main__":
    main()
