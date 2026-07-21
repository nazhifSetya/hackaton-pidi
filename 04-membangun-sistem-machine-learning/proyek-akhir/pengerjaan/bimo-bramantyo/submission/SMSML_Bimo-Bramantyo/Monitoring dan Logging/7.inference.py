"""Kriteria 4 — Skrip inferensi untuk menguji layanan model yang berjalan.

Mengirim sejumlah sampel fitur kimia anggur ke endpoint /predict milik eksporter
(port 8010) sekaligus membangkitkan lalu lintas request agar metrik Prometheus
terisi. Nilai fitur dikirim dalam skala ASLI (penskalaan ditangani pipeline model).

Jalankan setelah `3.prometheus_exporter.py` aktif:
    python 7.inference.py
"""
from time import sleep

import requests

ENDPOINT = "http://127.0.0.1:8010/predict"

# Urutan: [alcohol, malic_acid, ash, alcalinity_of_ash, magnesium, total_phenols,
#          flavanoids, nonflavanoid_phenols, proanthocyanins, color_intensity,
#          hue, od280_od315_of_diluted_wines, proline]
SAMPEL = [
    [14.23, 1.71, 2.43, 15.6, 127.0, 2.80, 3.06, 0.28, 2.29, 5.64, 1.04, 3.92, 1065.0],
    [13.20, 1.78, 2.14, 11.2, 100.0, 2.65, 2.76, 0.26, 1.28, 4.38, 1.05, 3.40, 1050.0],
    [12.37, 0.94, 1.36, 10.6, 88.0, 1.98, 0.57, 0.28, 0.42, 1.95, 1.05, 1.82, 520.0],
    [13.71, 5.65, 2.45, 20.5, 95.0, 1.68, 0.61, 0.52, 1.06, 7.70, 0.64, 1.74, 740.0],
    [12.29, 1.61, 2.21, 20.4, 103.0, 1.10, 1.02, 0.37, 1.46, 3.05, 0.906, 1.82, 870.0],
]


def main():
    print(f"Mengirim {len(SAMPEL)} sampel ke {ENDPOINT} ...\n")
    for i, baris in enumerate(SAMPEL, start=1):
        resp = requests.post(ENDPOINT, json={"data": [baris]}, timeout=10)
        resp.raise_for_status()
        out = resp.json()
        print(f"Sampel {i}: kelas={out['predictions'][0]} ({out['labels'][0]})")
        sleep(0.5)
    print("\nSelesai. Metrik prediksi kini terekam & siap di-scrape Prometheus.")


if __name__ == "__main__":
    main()
