# PANDUAN Submission — 04 SMSML / Bimo Bramantyo

Target: **Basic (Bintang 3)** — 2 pts di tiap kriteria. Stack: Wine recognition + SVC (Pipeline).

Semua kode & artefak sudah dibuat dan diverifikasi lokal di Victus. Yang tersisa
adalah langkah yang **butuh akun/keputusan Bimo**. Ikuti urutan di bawah.

---

## 1. Push 2 repository GitHub (WAJIB PUBLIC, akun Bimo sendiri)

Repo Kriteria 1 dan 3 harus publik di **akun GitHub Bimo** (bukan akun rekan —
demi anti-plagiarisme). Dua folder ini yang jadi isi repo:

- `Eksperimen_SML_Bimo-Bramantyo/`  → repo **Eksperimen_SML_Bimo-Bramantyo**
- `Workflow-CI/`                     → repo **Workflow-CI**

### Langkah (PowerShell / terminal), setelah login GitHub Bimo

Login dulu sebagai Bimo:
```
gh auth login
```
(atau siapkan Personal Access Token scope `repo` + `workflow`.)

Lalu jalankan helper (dari folder `bimo-bramantyo/`):
```
python panduan/push_repos.py <username_github_bimo>
```
Skrip ini membuat 2 repo publik, mem-push isinya, dan mengaktifkan Actions.
> Kalau mau manual, lihat perintah di bawah bagian "Manual push".

### Setelah push
1. Buka tab **Actions** di repo `Workflow-CI` → pastikan run **hijau (success)**.
   (Workflow auto-jalan saat push ke `main`.)
2. Buka kedua file link dan ganti `<USERNAME_GITHUB_BIMO>` dengan username asli:
   - `Eksperimen_SML_Bimo-Bramantyo.txt`
   - `Workflow-CI.txt`
3. Pastikan kedua repo **Public** (Settings → General → Danger Zone bila perlu).

---

## 2. Kriteria 4 — nama dashboard Grafana = username Dicoding

Screenshot Grafana memakai dashboard bernama **`bimo`** (sesuai username Dicoding
yang kamu sebutkan). Jika username Dicoding aslinya berbeda, beri tahu supaya
dashboard + screenshot diganti agar tidak ditolak reviewer.

---

## 3. Upload ke Dicoding

Berkas final: `submission/SMSML_Bimo-Bramantyo.zip` (struktur flat sesuai
ketentuan; TIDAK zip-in-zip). Isi:
```
SMSML_Bimo-Bramantyo/
├── Eksperimen_SML_Bimo-Bramantyo.txt
├── Membangun_model/{modelling.py, wine_preprocessing.csv, requirements.txt,
│                     screenshoot_dashboard.jpg, screenshoot_artifak.jpg}
├── Workflow-CI.txt
└── Monitoring dan Logging/{1.bukti_serving.jpg, 2.prometheus.yml,
      3.prometheus_exporter.py, 4.bukti monitoring Prometheus/,
      5.bukti monitoring Grafana/, 7.inference.py, model/, 8.serving_stack/}
```
Upload zip tersebut ke halaman submission Dicoding.

---

## Menjalankan ulang (opsional, untuk regen artefak/screenshot)

```
# aktifkan env
python -m venv .venv           # jika belum ada
.\.venv\Scripts\pip install mlflow==2.19.0 scikit-learn==1.5.2 pandas==2.2.3 "numpy<2.2" flask prometheus_client psutil requests jupyter nbconvert

# K2: latih + MLflow UI
cd Membangun_model
..\.venv\Scripts\python modelling.py
..\.venv\Scripts\python -m mlflow ui      # buka http://127.0.0.1:5000 → screenshot

# K4: serving + monitoring
cd "..\Monitoring dan Logging"
..\.venv\Scripts\python "3.prometheus_exporter.py"    # jendela 1 (port 8010)
..\.venv\Scripts\python "7.inference.py"              # jendela 2 (bangkitkan traffic)
cd 8.serving_stack && docker compose up -d            # Prometheus :9090, Grafana :3000
# Grafana: http://localhost:3000 (login anonim admin) → dashboard "bimo"
```

## Manual push (bila tidak pakai helper)

```
# Repo Kriteria 1
cd Eksperimen_SML_Bimo-Bramantyo
git init -b main
git add -A
git commit -m "Kriteria 1: eksperimen & preprocessing Wine recognition"
gh repo create Eksperimen_SML_Bimo-Bramantyo --public --source=. --push

# Repo Kriteria 3
cd ../Workflow-CI
git init -b main
git add -A
git commit -m "Kriteria 3: MLflow Project + GitHub Actions CI"
gh repo create Workflow-CI --public --source=. --push
```
