"""Kriteria 2 (Basic) — Melatih model prediksi keselamatan Titanic dengan
MLflow autolog. Tracking disimpan lokal (./mlruns) dan dapat dibuka melalui
MLflow Tracking UI pada http://127.0.0.1:5000 (`mlflow ui`).
"""
import os

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

HERE = os.path.dirname(os.path.abspath(__file__))
mlflow.set_tracking_uri("file:" + os.path.join(HERE, "mlruns"))
mlflow.set_experiment("Titanic_Survival")

dataset = pd.read_csv(os.path.join(HERE, "titanic_preprocessing.csv"))
X = dataset.drop(columns=["Survived"])
y = dataset["Survived"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=7, stratify=y
)

# Autolog merekam parameter, metrik, dan artefak model ke MLflow.
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="LogReg_autolog"):
    clf = LogisticRegression(max_iter=1000, random_state=7)
    clf.fit(X_train, y_train)

    acc_train = clf.score(X_train, y_train)
    acc_test = clf.score(X_test, y_test)
    print(f"Akurasi latih : {acc_train:.4f}")
    print(f"Akurasi uji   : {acc_test:.4f}")

print("Selesai. Jalankan `mlflow ui` lalu buka http://127.0.0.1:5000")
