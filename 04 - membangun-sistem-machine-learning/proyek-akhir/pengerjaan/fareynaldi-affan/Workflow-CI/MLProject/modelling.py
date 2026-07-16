"""Kriteria 3 — Entry point MLflow Project untuk re-training model Titanic di CI.

Dipanggil via `mlflow run . --env-manager=local`. MLflow `run` sudah membuat run
aktif, jadi cukup mengaktifkan autolog (tanpa start_run/set_experiment manual
yang akan bentrok). Nama experiment di-set lewat argumen CLI.
"""
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

frame = pd.read_csv("titanic_preprocessing.csv")
X = frame.drop(columns=["Survived"])
y = frame["Survived"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=7, stratify=y
)

mlflow.sklearn.autolog()

model = LogisticRegression(max_iter=1000, random_state=7)
model.fit(X_train, y_train)

print(f"Akurasi uji: {model.score(X_test, y_test):.4f}")
print("Model Titanic berhasil dilatih dan dicatat oleh MLflow (autolog).")
