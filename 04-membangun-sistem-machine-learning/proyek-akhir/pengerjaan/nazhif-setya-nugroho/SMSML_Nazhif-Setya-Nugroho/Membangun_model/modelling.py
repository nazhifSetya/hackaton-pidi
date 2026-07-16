"""Kriteria 2 (Basic) — Melatih model klasifikasi diabetes dengan MLflow autolog.

Tracking disimpan secara lokal (./mlruns) sehingga dapat dibuka lewat MLflow
Tracking UI di http://127.0.0.1:5000 (jalankan: `mlflow ui`).
"""
import os
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ── Konfigurasi tracking lokal ────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
mlflow.set_tracking_uri("file:" + os.path.join(BASE_DIR, "mlruns"))
mlflow.set_experiment("Diabetes_Classification")

# ── Load dataset hasil preprocessing (siap latih) ─────────────
data_path = os.path.join(BASE_DIR, "diabetes_preprocessing.csv")
df = pd.read_csv(data_path)

X = df.drop(columns=["Outcome"])
y = df["Outcome"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Autolog: mencatat parameter, metrik, dan artefak model ────
mlflow.sklearn.autolog()

with mlflow.start_run(run_name="RandomForest_autolog"):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    print(f"Train accuracy: {train_acc:.4f}")
    print(f"Test accuracy : {test_acc:.4f}")

print("Selesai. Buka MLflow UI dengan: mlflow ui  (lalu akses http://127.0.0.1:5000)")
