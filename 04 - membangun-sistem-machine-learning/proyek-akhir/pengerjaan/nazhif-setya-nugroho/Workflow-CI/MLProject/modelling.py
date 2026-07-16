"""Kriteria 3 — Entry point MLflow Project untuk re-training model diabetes di CI.

Dijalankan lewat `mlflow run . --env-manager=local` (lihat file MLProject).
MLflow `run` sudah membuat run aktif secara otomatis, sehingga script cukup
mengaktifkan autolog agar parameter, metrik, dan artefak model tercatat ke run
tersebut (tanpa memanggil start_run/set_experiment yang akan bentrok).
"""
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Dataset hasil preprocessing berada di direktori project yang sama.
df = pd.read_csv("diabetes_preprocessing.csv")
X = df.drop(columns=["Outcome"])
y = df["Outcome"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Autolog mencatat parameter, metrik, dan artefak model ke run aktif.
mlflow.sklearn.autolog()

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

test_acc = model.score(X_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")
print("Model berhasil dilatih dan dicatat oleh MLflow (autolog).")
