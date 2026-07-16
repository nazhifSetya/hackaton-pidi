# 🚀 Instruksi Colab — Cara Menjalankan Notebook di Google Colab

> **Panduan ini muncul dulu di Tahap 1 (verifikasi) dan dipakai ulang di Fase Akhir (Run All final).**
> Ikuti berurutan. Kalau ada error atau bingung — screenshot lalu tanya Claude.

---

## 📋 Prasyarat (siapkan sebelum buka Colab)

- [ ] Akun Google (login di browser)
- [ ] Akun **Ngrok** — daftar gratis di [ngrok.com](https://ngrok.com) → login → copy **Your Authtoken** (dari dashboard)
- [ ] Notebook yang mau dijalankan sudah ada di komputer lokal:
  - `submission/Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`
  - `submission/Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`

---

## 🎯 Tahap 1 — Verifikasi 3 Bom Waktu (dijalankan SEBELUM isi notebook)

Sebelum kerja substansi, kita cek dulu apa 3 hal ini jalan di Colab terbaru. Kalau ada yang gagal → siapkan workaround dulu.

### Langkah 1.1 — Buka Colab baru

1. Buka [colab.research.google.com](https://colab.research.google.com)
2. Klik **File → New notebook** (bikin notebook kosong sementara, ini bukan submission)
3. Klik **Runtime → Change runtime type → GPU → T4 GPU → Save**
4. Verifikasi GPU: buat sel baru, ketik `!nvidia-smi`, run → harus muncul "Tesla T4".

### Langkah 1.2 — Cek mirror model SD 1.5

Sel baru:
```python
!pip install -q diffusers transformers accelerate

from diffusers import StableDiffusionPipeline
import torch

# Coba mirror pertama
try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "stable-diffusion-v1-5/stable-diffusion-v1-5",
        torch_dtype=torch.float16
    ).to("cuda")
    print("✅ Mirror SD1.5 hidup:", "stable-diffusion-v1-5/stable-diffusion-v1-5")
    del pipe
    torch.cuda.empty_cache()
except Exception as e:
    print("❌ Mirror gagal:", str(e)[:300])
```

**Yang diharapkan:** `✅ Mirror SD1.5 hidup`. Kalau gagal, screenshot error → tanya Claude untuk mirror alternatif (`sd-legacy/stable-diffusion-v1-5` / `botp/stable-diffusion-v1-5`).

### Langkah 1.3 — Cek mirror model Inpainting

Sel baru:
```python
from diffusers import StableDiffusionInpaintPipeline
import torch

try:
    pipe_ip = StableDiffusionInpaintPipeline.from_pretrained(
        "stable-diffusion-v1-5/stable-diffusion-inpainting",
        torch_dtype=torch.float16
    ).to("cuda")
    print("✅ Mirror Inpainting hidup")
    del pipe_ip
    torch.cuda.empty_cache()
except Exception as e:
    print("❌ Mirror Inpainting gagal:", str(e)[:300])
```

### Langkah 1.4 — Cek Refiner Pattern (`denoising_end` / `denoising_start` di SD1.5)

Sel baru:
```python
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
import torch, inspect

pipe = StableDiffusionPipeline.from_pretrained(
    "stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16
).to("cuda")

sig = inspect.signature(pipe.__call__)
has_denoise_end = "denoising_end" in sig.parameters
print("denoising_end supported by SD1.5 txt2img:", has_denoise_end)

pipe_img2img = StableDiffusionImg2ImgPipeline(**pipe.components)
sig2 = inspect.signature(pipe_img2img.__call__)
has_denoise_start = "denoising_start" in sig2.parameters
print("denoising_start supported by SD1.5 img2img:", has_denoise_start)
```

**Yang diharapkan:** dua-duanya `True`. Kalau `False` → beri tahu Claude, kita siapkan workaround manual step-cut.

### Langkah 1.5 — Cek CLIPSeg (untuk auto-mask K2 Skilled)

Sel baru:
```python
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
import torch

processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined").to("cuda")
print("✅ CLIPSeg load OK, params:", sum(p.numel() for p in model.parameters()))
```

Setelah semua PASS → **screenshot hasil ke Claude** → kita lanjut Tahap 2 (isi notebook Pipeline).

---

## 🎯 Fase Akhir — Run All Notebook Submission di Colab

Setelah Claude selesai isi seluruh notebook Pipeline + Streamlit, tugasmu = Run All di Colab & bawa hasil balik.

### Langkah A — Upload Notebook Pipeline ke Colab

1. Buka [colab.research.google.com](https://colab.research.google.com)
2. **File → Upload notebook** → pilih `submission/Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`
3. **Runtime → Change runtime type → T4 GPU → Save**
4. **Runtime → Run all** (Ctrl+F9)
5. Tunggu semua sel selesai (biasanya 15-30 menit untuk seluruh eksperimen K1+K2)
6. Verifikasi: semua sel yang harusnya keluar gambar → ada gambar; tidak ada sel merah / traceback
7. **File → Download → Download .ipynb** → simpan overwrite ke `submission/Pipeline_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`

### Langkah B — Upload Notebook Streamlit ke Colab

1. **File → Upload notebook** → pilih `submission/Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`
2. Sebelum Run All, buka sel **`auth_token = "YOUR_AUTHENTICATION_KEY"`** dan **ganti dengan token ngrok pribadimu**
3. **Runtime → Run all**
4. Tunggu sampai muncul URL public dari ngrok (mis. `https://xxxx.ngrok-free.app`)
5. **Buka URL itu di tab baru** → verifikasi UI muncul & bisa Generate

### Langkah C — Rekam Video Demo

Selagi Streamlit jalan di ngrok:
1. Buka aplikasi screen recorder (Windows: Xbox Game Bar `Win+G`, atau OBS Studio)
2. Rekam layar 1-5 menit, tampilkan:
   - Isi prompt & negative prompt → klik Generate → tunggu gambar muncul (Basic)
   - Ganti scheduler dropdown → generate lagi (Skilled)
   - Buka tab Inpainting/Outpainting → gambar mask di canvas → generate (Advanced)
   - Klik Clear Memory
3. Simpan format **`.mp4`** → letakkan di `submission/video_demo_aplikasi_BFGAI.mp4`

### Langkah D — Download Notebook Streamlit

Setelah rekaman selesai:
1. Kembali ke Colab
2. Jalankan sel `ngrok.kill()` untuk tutup tunnel
3. **File → Download → Download .ipynb** → simpan overwrite ke `submission/Streamlit_submission_BFGAI_Nazhif_Setya_Nugroho.ipynb`

### Langkah E — Kabari Claude

Kabari Claude "sudah run all + video sudah direkam" — Claude bikin `requirements.txt` + zip flat 4 file + audit final.

---

## 🐛 Troubleshooting Umum

| Gejala | Sebab | Solusi |
|---|---|---|
| `403` / `404` saat `from_pretrained` | Model ID delisted | Ganti ke mirror lain — konfirmasi ke Claude |
| **CUDA OOM** saat load kedua pipeline | VRAM T4 mulai penuh | `torch.cuda.empty_cache()` antara load; atau load 1 model di 1 waktu |
| Ngrok error `authtoken invalid` | Token salah / expired | Ambil ulang di dashboard ngrok.com |
| Ngrok error `endpoint limit` | Sudah pernah connect | Run sel `ngrok.kill()` dulu, baru retry |
| Streamlit URL 502 Bad Gateway | Streamlit belum siap | Tunggu 30 detik setelah `subprocess.Popen` sebelum `ngrok.connect` |
| Colab disconnect saat sel jalan lama | Idle timeout | Klik area sel tiap ~10 menit; atau Colab Pro |
| Grid 2×2 tidak keluar | Batch inference salah param | `pipe(..., num_images_per_prompt=4)` bukan `num_images` |

---

## 📸 Bukti bantuan (kalau Claude perlu debug)

Kalau ada error yang aneh, kirim ke Claude:
1. **Screenshot** error message lengkap (jangan cuma pesan singkat)
2. **Output `!pip list | grep -E 'diffusers|transformers|torch'`** — versi library
3. **Output `!nvidia-smi`** — status GPU/VRAM

Claude bisa juga langsung buka URL ngrok via MCP CDP untuk lihat UI-nya sendiri (screenshot, cek console error) — beritahu URL-nya kalau perlu.
