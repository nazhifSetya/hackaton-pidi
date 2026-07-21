"""Kriteria 4 — layanan inferensi kultivar anggur berikut eksportir metriknya.

Berkas ini menjalankan satu aplikasi Flask yang: (a) memuat model Pipeline
(StandardScaler + SVC RBF) dan melayani permintaan prediksi lewat POST /predict,
lalu (b) menerbitkan sejumlah metrik dalam format teks Prometheus di GET /metrics.

Berbeda dengan pola middleware global, instrumentasi di sini ditanam langsung
pada tiap handler: durasi diukur memakai context manager bawaan Histogram
(`.time()`), penghitung permintaan dinaikkan di akhir handler, sedangkan
pemakaian CPU/RAM baru dibaca ketika endpoint /metrics dipanggil (saat scrape).

Metrik yang diterbitkan (cukup untuk tingkat Basic yang meminta minimal tiga):
    anggur_permintaan_total            counter   lalu lintas per endpoint/metode/status
    anggur_inferensi_durasi_seconds    histogram sebaran waktu proses per endpoint
    anggur_prediksi_total              counter   akumulasi prediksi tiap kultivar
    anggur_cpu_persen                  gauge     beban CPU mesin saat di-scrape
    anggur_memori_persen               gauge     pemakaian RAM saat di-scrape

Menjalankan:  python "3.prometheus_exporter.py"   ->  layanan di http://127.0.0.1:8010
"""
import os

import mlflow.pyfunc
import pandas as pd
import psutil
from flask import Flask, Response, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

ALAMAT_PORT = 8010
LOKASI_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

# Ke-13 fitur harus disusun persis seperti kolom dataset hasil preprocessing.
KOLOM_FITUR = (
    "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
    "total_phenols", "flavanoids", "nonflavanoid_phenols", "proanthocyanins",
    "color_intensity", "hue", "od280_od315_of_diluted_wines", "proline",
)
LABEL_KULTIVAR = {0: "Kultivar_0", 1: "Kultivar_1", 2: "Kultivar_2"}


def daftar_metrik():
    """Membuat dan mengembalikan lima objek metrik Prometheus dalam satu dict."""
    return {
        "permintaan": Counter(
            "anggur_permintaan_total",
            "Total permintaan API dikelompokkan endpoint/metode/status",
            ["endpoint", "method", "status"],
        ),
        "durasi": Histogram(
            "anggur_inferensi_durasi_seconds",
            "Waktu pemrosesan permintaan dalam detik",
            ["endpoint"],
        ),
        "prediksi": Counter(
            "anggur_prediksi_total",
            "Akumulasi hasil prediksi per kultivar",
            ["kultivar"],
        ),
        "cpu": Gauge("anggur_cpu_persen", "Beban CPU mesin (persen)"),
        "memori": Gauge("anggur_memori_persen", "Pemakaian RAM mesin (persen)"),
    }


model = mlflow.pyfunc.load_model(LOKASI_MODEL)
print(f"[serving] model termuat dari {LOKASI_MODEL}")

app = Flask(__name__)
M = daftar_metrik()


def naikkan_permintaan(endpoint: str, kode_status: int):
    """Menaikkan penghitung permintaan untuk satu endpoint."""
    M["permintaan"].labels(endpoint=endpoint, method=request.method,
                           status=kode_status).inc()


@app.get("/")
def beranda():
    return (
        "<html><head><title>Serving Kultivar Anggur</title></head>"
        "<body style='font-family:system-ui;max-width:640px;margin:2rem auto'>"
        "<h1>Layanan Model Kultivar Anggur Aktif</h1>"
        "<p>Model Pipeline (StandardScaler + SVC RBF) siap melakukan inferensi.</p>"
        "<ul>"
        "<li><code>POST /predict</code> &mdash; kirim JSON {\"data\": [[13 fitur]]}</li>"
        "<li><code>GET /metrics</code> &mdash; metrik Prometheus</li>"
        "<li><code>GET /health</code> &mdash; status layanan</li>"
        "</ul></body></html>"
    )


@app.get("/health")
def health():
    naikkan_permintaan("/health", 200)
    return jsonify(status="ok", model="svc_rbf_anggur")


@app.post("/predict")
def prediksi():
    muatan = request.get_json(force=True)
    contoh = muatan.get("data") or muatan.get("instances")
    bingkai = pd.DataFrame(contoh, columns=list(KOLOM_FITUR))

    with M["durasi"].labels(endpoint="/predict").time():
        keluaran = [int(nilai) for nilai in model.predict(bingkai)]

    for kode in keluaran:
        M["prediksi"].labels(kultivar=LABEL_KULTIVAR.get(kode, str(kode))).inc()
    naikkan_permintaan("/predict", 200)
    return jsonify(
        predictions=keluaran,
        labels=[LABEL_KULTIVAR.get(k, str(k)) for k in keluaran],
    )


@app.get("/metrics")
def metrics():
    # Nilai sumber daya sengaja dibaca hanya saat scrape agar tidak membebani
    # setiap permintaan prediksi.
    M["cpu"].set(psutil.cpu_percent(interval=None))
    M["memori"].set(psutil.virtual_memory().percent)
    naikkan_permintaan("/metrics", 200)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=ALAMAT_PORT)
