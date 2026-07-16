"""Kriteria 4 — Model serving + Prometheus exporter.

Satu aplikasi Flask yang:
  - menyajikan model (endpoint POST /predict)  -> bukti serving
  - mengekspos metrik Prometheus (GET /metrics) -> bahan monitoring
  - halaman status (GET /) untuk bukti serving

Metrik yang diekspos (6, lebih dari minimal 3):
  1. http_requests_total              (Counter)   jumlah request per endpoint/status
  2. http_request_duration_seconds    (Histogram) latensi request
  3. http_requests_in_progress        (Gauge)     request yang sedang diproses
  4. model_predictions_total          (Counter)   jumlah prediksi per kelas
  5. system_cpu_usage_percent         (Gauge)     penggunaan CPU
  6. system_memory_usage_percent      (Gauge)     penggunaan memori
"""
import os
import time

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model")

FEATURE_COLUMNS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]

# ── Muat model sekali saat startup ────────────────────────────
model = mlflow.pyfunc.load_model(MODEL_PATH)
print(f"Model dimuat dari: {MODEL_PATH}")

app = Flask(__name__)

# ── Definisi metrik Prometheus ────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP request",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Latensi request (detik)", ["endpoint"],
)
IN_PROGRESS = Gauge(
    "http_requests_in_progress", "Jumlah request yang sedang diproses",
)
PREDICTION_COUNT = Counter(
    "model_predictions_total", "Total prediksi per kelas", ["predicted_class"],
)
CPU_USAGE = Gauge("system_cpu_usage_percent", "Penggunaan CPU (persen)")
MEM_USAGE = Gauge("system_memory_usage_percent", "Penggunaan memori (persen)")


def _update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    MEM_USAGE.set(psutil.virtual_memory().percent)


@app.before_request
def _before():
    request._start_time = time.time()
    IN_PROGRESS.inc()


@app.after_request
def _after(response):
    latency = time.time() - getattr(request, "_start_time", time.time())
    endpoint = request.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint, http_status=response.status_code
    ).inc()
    IN_PROGRESS.dec()
    _update_system_metrics()
    return response


@app.route("/")
def index():
    # Contoh prediksi untuk membuktikan model melayani permintaan.
    sample = pd.DataFrame([[0.64, 0.87, -0.03, 0.67, -0.18, 0.17, 0.47, 1.43]],
                          columns=FEATURE_COLUMNS)
    pred = int(model.predict(sample)[0])
    label = "Diabetes" if pred == 1 else "Tidak Diabetes"
    return f"""
    <html><head><title>Diabetes Model Serving</title></head>
    <body style="font-family: sans-serif; padding: 2rem;">
      <h1>✅ Model Serving Aktif</h1>
      <p>Model klasifikasi diabetes (RandomForest) siap melayani permintaan.</p>
      <p><b>Contoh prediksi:</b> input sampel &rarr; <b>{pred}</b> ({label})</p>
      <ul>
        <li><code>POST /predict</code> — inferensi model</li>
        <li><code>GET /metrics</code> — metrik Prometheus</li>
      </ul>
    </body></html>
    """


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True)
    rows = payload.get("data", payload.get("instances"))
    df = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    preds = model.predict(df)
    preds = [int(p) for p in preds]
    for p in preds:
        PREDICTION_COUNT.labels(predicted_class=str(p)).inc()
    return jsonify({"predictions": preds})


@app.route("/metrics")
def metrics():
    _update_system_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
