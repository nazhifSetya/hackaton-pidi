"""Kriteria 2 (Basic) — Pelatihan model klasifikasi kultivar anggur.

Model dibangun sebagai sebuah Pipeline scikit-learn yang menggabungkan
StandardScaler dan Support Vector Classifier (kernel RBF), lalu dilacak dengan
MLflow *autolog*. Seluruh artefak (parameter, metrik, model) disimpan pada
tracking store lokal berbasis berkas di folder ./mlruns sehingga bisa ditinjau
lewat MLflow Tracking UI:

    mlflow ui        # buka http://127.0.0.1:5000

Catatan: penskalaan ditanam di dalam Pipeline (bukan pada berkas hasil
preprocessing) agar model yang tersimpan langsung menerima nilai fitur asli.
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

KONFIG = {
    "berkas_data": DIREKTORI / "wine_preprocessing.csv",
    "kolom_target": "target_kultivar",
    "nama_eksperimen": "Klasifikasi_Kultivar_Anggur",
    "acak": 17,
    "porsi_uji": 0.2,
    "svc": {"kernel": "rbf", "C": 10.0, "gamma": "scale"},
}


def muat_dataset(berkas: Path):
    """Membaca CSV siap latih dan memisahkan matriks fitur dari label target."""
    tabel = pd.read_csv(berkas)
    fitur = tabel.drop(columns=[KONFIG["kolom_target"]])
    target = tabel[KONFIG["kolom_target"]]
    return fitur, target


def bangun_pipeline() -> Pipeline:
    """Merangkai penskalaan fitur dan SVC menjadi satu estimator utuh."""
    penyetel = KONFIG["svc"]
    return Pipeline(
        steps=[
            ("penskalaan", StandardScaler()),
            (
                "svc",
                SVC(
                    kernel=penyetel["kernel"],
                    C=penyetel["C"],
                    gamma=penyetel["gamma"],
                    probability=True,
                    random_state=KONFIG["acak"],
                ),
            ),
        ]
    )


def jalankan():
    # Tracking store lokal berbasis berkas (folder ./mlruns di samping skrip ini).
    mlflow.set_tracking_uri((DIREKTORI / "mlruns").as_uri())
    mlflow.set_experiment(KONFIG["nama_eksperimen"])

    fitur, target = muat_dataset(KONFIG["berkas_data"])
    X_latih, X_uji, y_latih, y_uji = train_test_split(
        fitur,
        target,
        test_size=KONFIG["porsi_uji"],
        random_state=KONFIG["acak"],
        stratify=target,
    )

    # Autolog merekam parameter, metrik pelatihan, dan artefak model otomatis.
    mlflow.sklearn.autolog()

    with mlflow.start_run(run_name="svc_rbf_anggur"):
        model = bangun_pipeline()
        model.fit(X_latih, y_latih)

        akurasi_latih = model.score(X_latih, y_latih)
        akurasi_uji = model.score(X_uji, y_uji)
        mlflow.log_metric("akurasi_latih_manual", akurasi_latih)
        mlflow.log_metric("akurasi_uji_manual", akurasi_uji)
        print(f"Akurasi data latih : {akurasi_latih:.4f}")
        print(f"Akurasi data uji   : {akurasi_uji:.4f}")

    print("Pelatihan selesai. Tinjau via `mlflow ui` -> http://127.0.0.1:5000")


if __name__ == "__main__":
    jalankan()
