"""Kriteria 4 — Penyajian model + eksporter metrik Prometheus.

Aplikasi Flask tunggal yang menjalankan dua peran sekaligus:
  * menyajikan model klasifikasi spesies penguin (endpoint POST /predict)  -> bukti serving
  * memaparkan metrik dalam format Prometheus (GET /metrics)               -> bahan monitoring

Lima metrik dipublikasikan (melebihi minimal tiga untuk tingkat Basic):
  1. penguin_api_requests_total        (Counter)   jumlah request per endpoint & status
  2. penguin_inference_latency_seconds (Histogram) durasi pemrosesan tiap request
  3. penguin_predictions_total         (Counter)   jumlah prediksi per spesies
  4. penguin_service_cpu_percent       (Gauge)     pemakaian CPU proses layanan
  5. penguin_service_memory_percent    (Gauge)     pemakaian memori sistem

Jalankan:  python "3.prometheus_exporter.py"   (layanan aktif di port 8501)
"""
from pathlib import Path
from time import perf_counter

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

SERVICE_PORT = 8501
MODEL_DIR = Path(__file__).resolve().parent / "model"

# Urutan fitur harus sama persis dengan dataset hasil preprocessing (tanpa kolom target).
FEATURES = [
    "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g",
    "sex", "island_Biscoe", "island_Dream", "island_Torgersen",
]
SPECIES_NAMES = {0: "Adelie", 1: "Chinstrap", 2: "Gentoo"}

penguin_model = mlflow.pyfunc.load_model(str(MODEL_DIR))
print(f"Model dimuat dari: {MODEL_DIR}")

service = Flask(__name__)

# ── Registri metrik Prometheus ────────────────────────────────
REQ_TOTAL = Counter(
    "penguin_api_requests_total", "Jumlah request API",
    ["endpoint", "method", "status"],
)
INFER_LATENCY = Histogram(
    "penguin_inference_latency_seconds", "Durasi pemrosesan request (detik)",
    ["endpoint"],
)
PRED_TOTAL = Counter(
    "penguin_predictions_total", "Jumlah prediksi per spesies", ["species"],
)
CPU_PERCENT = Gauge("penguin_service_cpu_percent", "Pemakaian CPU (persen)")
MEM_PERCENT = Gauge("penguin_service_memory_percent", "Pemakaian memori (persen)")


def refresh_resource_gauges():
    CPU_PERCENT.set(psutil.cpu_percent(interval=None))
    MEM_PERCENT.set(psutil.virtual_memory().percent)


@service.before_request
def mark_start():
    request._t0 = perf_counter()


@service.after_request
def record_metrics(response):
    elapsed = perf_counter() - getattr(request, "_t0", perf_counter())
    INFER_LATENCY.labels(endpoint=request.path).observe(elapsed)
    REQ_TOTAL.labels(
        endpoint=request.path, method=request.method, status=response.status_code
    ).inc()
    refresh_resource_gauges()
    return response


@service.route("/")
def home():
    contoh = pd.DataFrame(
        [[0.55, -1.10, 1.20, 1.05, 1, 1, 0, 0]], columns=FEATURES
    )
    kode = int(penguin_model.predict(contoh)[0])
    return f"""
    <html><head><title>Penguin Species Serving</title></head>
    <body style="font-family: system-ui; max-width: 640px; margin: 2rem auto;">
      <h1>Layanan Model Spesies Penguin Aktif</h1>
      <p>Model Gradient Boosting siap melakukan inferensi.</p>
      <p>Contoh prediksi sampel &rarr; kelas <b>{kode}</b> ({SPECIES_NAMES[kode]})</p>
      <ul>
        <li><code>POST /predict</code> &mdash; inferensi (kirim JSON berisi "data")</li>
        <li><code>GET  /metrics</code> &mdash; metrik Prometheus</li>
        <li><code>GET  /health</code> &mdash; status layanan</li>
      </ul>
    </body></html>
    """


@service.route("/health")
def health():
    return jsonify(status="ok", model="gradient_boosting_penguins")


@service.route("/predict", methods=["POST"])
def predict():
    body = request.get_json(force=True)
    rows = body.get("data") or body.get("instances")
    frame = pd.DataFrame(rows, columns=FEATURES)
    hasil = [int(p) for p in penguin_model.predict(frame)]
    for kode in hasil:
        PRED_TOTAL.labels(species=SPECIES_NAMES.get(kode, str(kode))).inc()
    return jsonify(
        predictions=hasil,
        labels=[SPECIES_NAMES.get(k, str(k)) for k in hasil],
    )


@service.route("/metrics")
def metrics():
    refresh_resource_gauges()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    service.run(host="0.0.0.0", port=SERVICE_PORT)
