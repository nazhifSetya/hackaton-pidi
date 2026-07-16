"""Kriteria 4 — Pembangkit traffic inferensi untuk model Titanic.

Mengirim permintaan POST /invocations berulang memakai baris acak dari dataset
yang sudah diproses, agar metrik Prometheus terisi dan bisa divisualisasikan
di Grafana.

Contoh:
  python 7.inference.py            # loop tak terbatas (Ctrl+C untuk berhenti)
  python 7.inference.py --n 300    # kirim 300 request lalu berhenti
"""
import argparse
import os
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "model_data.csv")
URL = "http://localhost:8000/invocations"

FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked_Q", "Embarked_S"]


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0, help="jumlah request (0 = tak terbatas)")
    ap.add_argument("--delay", type=float, default=0.4, help="jeda antar request (detik)")
    args = ap.parse_args()

    df = pd.read_csv(DATA)[FEATURES]

    sent = 0
    while args.n == 0 or sent < args.n:
        rows = df.sample(1).values.tolist()
        try:
            r = requests.post(URL, json={"data": rows}, timeout=5)
            print(f"[{sent}] {r.status_code} -> {r.json()}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{sent}] gagal: {exc}")
        sent += 1
        time.sleep(args.delay)


if __name__ == "__main__":
    run()
