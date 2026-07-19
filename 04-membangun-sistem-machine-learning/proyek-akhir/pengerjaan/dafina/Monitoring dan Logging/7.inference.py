"""Kriteria 4 — Skrip inferensi untuk menguji layanan model yang sedang berjalan.

Mengirim beberapa sampel ke endpoint /predict milik eksporter (port 8501),
sekaligus menghasilkan lalu lintas request agar metrik Prometheus terisi.

Jalankan setelah `3.prometheus_exporter.py` aktif:
    python 7.inference.py
"""
from time import sleep

import requests

ENDPOINT = "http://127.0.0.1:8501/predict"

# Setiap baris: [bill_length, bill_depth, flipper_length, body_mass,
#                sex, island_Biscoe, island_Dream, island_Torgersen]
# Nilai numerik sudah dalam skala standar (mengikuti StandardScaler saat preprocessing).
SAMPEL = [
    [-0.89, 0.78, -1.42, -0.56, 1, 0, 0, 1],   # cenderung Adelie
    [0.68, 0.82, -0.35, -0.72, 0, 0, 1, 0],    # cenderung Chinstrap
    [1.15, -1.05, 1.28, 1.640, 1, 1, 0, 0],    # cenderung Gentoo
    [-0.42, 0.35, -0.98, -0.30, 0, 0, 0, 1],
]


def main():
    print(f"Mengirim {len(SAMPEL)} sampel ke {ENDPOINT} ...\n")
    for i, baris in enumerate(SAMPEL, start=1):
        resp = requests.post(ENDPOINT, json={"data": [baris]}, timeout=10)
        resp.raise_for_status()
        out = resp.json()
        print(f"Sampel {i}: kelas={out['predictions'][0]} "
              f"({out['labels'][0]})")
        sleep(0.5)
    print("\nSelesai. Metrik prediksi kini terekam di Prometheus (/metrics).")


if __name__ == "__main__":
    main()
