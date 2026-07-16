"""Kriteria 4 — Serving model Titanic + Prometheus exporter.

Aplikasi Flask yang melayani inferензi model (POST /invocations) sekaligus
mengekspos metrik Prometheus (GET /metrics). Halaman status (GET /) dipakai
sebagai bukti serving.

Metrik yang diekspos (6 metrik berbeda, > minimal 3):
  1. titanic_inference_requests_total   (Counter)   request per endpoint & status
  2. titanic_inference_latency_seconds  (Summary)   latensi inferensi
  3. titanic_survival_predictions_total (Counter)   prediksi per kelas (0/1)
  4. service_inflight_requests          (Gauge)     request yang sedang diproses
  5. service_cpu_percent                (Gauge)     penggunaan CPU
  6. service_memory_percent             (Gauge)     penggunaan memori
"""
import os
import time
from functools import wraps

import mlflow.pyfunc
import pandas as pd
import psutil
from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Summary, generate_latest

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, "model")

FEATURES = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked_Q", "Embarked_S"]

titanic_model = mlflow.pyfunc.load_model(MODEL_DIR)
print("Model Titanic dimuat dari:", MODEL_DIR)

app = Flask(__name__)

REQUESTS = Counter(
    "titanic_inference_requests_total", "Jumlah request per endpoint",
    ["endpoint", "status"],
)
LATENCY = Summary(
    "titanic_inference_latency_seconds", "Latensi pemrosesan request", ["endpoint"],
)
PREDICTIONS = Counter(
    "titanic_survival_predictions_total", "Jumlah prediksi per kelas", ["label"],
)
INFLIGHT = Gauge("service_inflight_requests", "Request yang sedang diproses")
CPU = Gauge("service_cpu_percent", "Penggunaan CPU (persen)")
MEM = Gauge("service_memory_percent", "Penggunaan memori (persen)")


def observed(endpoint):
    """Decorator: catat latensi, jumlah request, inflight, dan metrik sistem."""
    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            INFLIGHT.inc()
            start = time.time()
            status = "200"
            try:
                return fn(*args, **kwargs)
            except Exception:
                status = "500"
                raise
            finally:
                LATENCY.labels(endpoint=endpoint).observe(time.time() - start)
                REQUESTS.labels(endpoint=endpoint, status=status).inc()
                INFLIGHT.dec()
                CPU.set(psutil.cpu_percent(interval=None))
                MEM.set(psutil.virtual_memory().percent)
        return inner
    return outer


@app.route("/")
@observed("/")
def home():
    sample = pd.DataFrame([[-0.83, 1.36, -0.57, 0.43, -0.47, -0.50, -0.31, 0.62]],
                          columns=FEATURES)
    pred = int(titanic_model.predict(sample)[0])
    status = "Selamat" if pred == 1 else "Tidak Selamat"
    return f"""
    <html><head><title>Titanic Survival Serving</title></head>
    <body style="font-family: system-ui; padding: 2rem;">
      <h1>&#128674; Titanic Survival Model — Serving Aktif</h1>
      <p>Model Logistic Regression siap memprediksi keselamatan penumpang.</p>
      <p><b>Contoh inferensi:</b> sampel penumpang &rarr; kelas <b>{pred}</b> ({status})</p>
      <ul>
        <li><code>POST /invocations</code> &mdash; inferensi (JSON: {{"data": [[...8 fitur...]]}})</li>
        <li><code>GET /metrics</code> &mdash; metrik Prometheus</li>
      </ul>
    </body></html>
    """


@app.route("/invocations", methods=["POST"])
@observed("/invocations")
def invocations():
    payload = request.get_json(force=True)
    rows = payload.get("data") or payload.get("instances")
    batch = pd.DataFrame(rows, columns=FEATURES)
    result = [int(p) for p in titanic_model.predict(batch)]
    for label in result:
        PREDICTIONS.labels(label=str(label)).inc()
    return jsonify({"predictions": result})


@app.route("/metrics")
def metrics():
    CPU.set(psutil.cpu_percent(interval=None))
    MEM.set(psutil.virtual_memory().percent)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
