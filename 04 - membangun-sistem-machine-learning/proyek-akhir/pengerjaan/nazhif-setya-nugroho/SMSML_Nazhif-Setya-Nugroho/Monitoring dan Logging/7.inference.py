"""Kriteria 4 — Generator inferensi untuk membangkitkan traffic ke model serving.

Mengirim permintaan POST /predict berulang kali menggunakan baris-baris dari
dataset hasil preprocessing, sehingga metrik Prometheus (request count, latensi,
prediksi per kelas, dsb.) terisi dan bisa divisualisasikan di Grafana.

Jalankan:  python 7.inference.py            (loop terus sampai Ctrl+C)
           python 7.inference.py --n 200    (kirim 200 request lalu berhenti)
"""
import argparse
import os
import time

import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "model_data.csv")
ENDPOINT = "http://localhost:8000/predict"

FEATURE_COLUMNS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=0, help="jumlah request (0 = tak terbatas)")
    parser.add_argument("--delay", type=float, default=0.5, help="jeda antar request (detik)")
    args = parser.parse_args()

    df = pd.read_csv(DATA_PATH)[FEATURE_COLUMNS]

    i = 0
    while args.n == 0 or i < args.n:
        row = df.sample(1).values.tolist()
        try:
            resp = requests.post(ENDPOINT, json={"data": row}, timeout=5)
            print(f"[{i}] status={resp.status_code} -> {resp.json()}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{i}] error: {exc}")
        i += 1
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
