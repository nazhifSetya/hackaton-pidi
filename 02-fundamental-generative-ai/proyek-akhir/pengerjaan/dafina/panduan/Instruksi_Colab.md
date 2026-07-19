# 🚀 Panduan Menjalankan di Google Colab — BFGAI Dafina (target Basic ⭐⭐⭐)

> Notebook & `logic.py` sudah aku isi lengkap. Tugas Dafina di sini **cuma menjalankan** di Colab GPU T4, **cek hasil gambar**, dan **rekam video** app. Ikuti urutannya pelan-pelan.

## 🧰 Yang perlu disiapkan dulu
1. **Akun Google** (untuk Google Colab) — gratis.
2. **Akun + token Ngrok** (untuk membuka app Streamlit ke internet):
   - Buka **ngrok.com** → Sign up pakai Google.
   - Masuk menu **"Your Authtoken"** → **Copy** token-nya (nanti dipakai di Notebook Streamlit cell 16).
3. Model Stable Diffusion **diunduh otomatis** dari Hugging Face saat run (tidak perlu akun HF, model publik). Total ±10 GB — muat di Colab T4 (16 GB VRAM).

> ⚠️ **PENTING soal runtime:** di Colab klik **Runtime → Change runtime type → pilih `T4 GPU` → Save.** Kalau tidak pakai GPU, model akan super lambat / gagal.

---

## 📓 BAGIAN A — Notebook Pipeline (Kriteria 1 & 2)

File: `Pipeline_submission_BFGAI_Dafina_Meira_Rizkia.ipynb`

1. Buka **colab.research.google.com** → **File → Upload notebook** → pilih file Pipeline di atas.
2. Set runtime **T4 GPU** (lihat peringatan di atas).
3. Klik **Runtime → Run all**. Biarkan jalan. Perkiraan **±8–12 menit** (sebagian besar untuk unduh 2 model). 
   - Beberapa sel di tengah memang **sengaja kosong** (itu bagian Skilled/Advanced yang tidak kita kerjakan untuk target Basic) — normal, dilewati cepat.
4. **Cek 3 gambar hasil ini** (bandingkan dengan gambar contoh Dicoding):

   | Sel | Variabel | Harus mirip | Ciri yang benar |
   |---|---|---|---|
   | **6** | `img_simple` | `image-13` | Astronot **kartun flat/2D**, garis tegas, warna rata |
   | **8** | `img_advanced` | `image-14` | Astronot **3D semi-realistis** (lebih nyata, bukan kartun) |
   | **29** | `img_inpaint` | `image-15` | Ada **satelit rusak** yang JELAS di kanan astronot |

5. **Screenshot ketiga hasil itu, kirim ke aku (chat Claude Code).** Aku akan bandingkan dengan target. Kalau belum pas, aku kasih angka baru untuk di-tuning (lihat tabel "Kalau hasil belum pas" di bawah).
6. Kalau ketiga gambar sudah oke → **File → Download → Download .ipynb**. Ganti file lama di folder `submission/` dengan yang baru (yang sudah ada output gambarnya).

### 🔧 Kalau hasil belum pas (tuning — ganti angka lalu Run ulang sel terkait)
| Masalah | Sel | Ubah |
|---|---|---|
| `img_advanced` masih terlihat kartun/flat | 8 | naikkan `guidance_scale=10.0` → coba `12.0` lalu `14.0` |
| `img_advanced` berantakan/aneh | 8 | turunkan `guidance_scale` → `8.0` |
| `img_simple` malah realistis (harusnya kartun) | 6 | (jarang) tambah kata di depan prompt: `"flat 2d cartoon illustration, ..."` |
| **Satelit tidak muncul** di sel 29 | 29 | naikkan `guidance_scale=18.0` → `20.0`, atau `num_inference_steps=55` → `65` |
| Satelit muncul tapi menimpa astronot | 27 | geser mask: ubah `x0 = int(W * 0.52)` → `0.58` |

> Ganti angka → klik sel itu → **Runtime → Run after** (atau Ctrl+Enter untuk sel itu + sel setelahnya yang bergantung). Tidak perlu run ulang dari awal (model sudah termuat).

---

## 🖥️ BAGIAN B — Notebook Streamlit (Kriteria 3) + rekam video

File: `Streamlit_submission_BFGAI_Dafina_Meira_Rizkia.ipynb`

1. Upload ke Colab, set runtime **T4 GPU**.
2. **Sebelum Run:** buka **cell 16**, ganti `"YOUR_AUTHENTICATION_KEY"` dengan **token ngrok Dafina** (dari persiapan tadi).
3. Klik **Runtime → Run all**. 
   - Cell 2 install library (±2–3 menit). Cell 6–13 menulis `logic.py` & `app.py`. Cell 16 menyalakan Streamlit + tunggu 20 detik. Cell 18 mencetak **URL publik** (bentuknya `https://xxxx.ngrok-free.app`).
   - Cell 21 sengaja tidak menutup tunnel (aman kalau Run all).
4. **Klik URL** yang tercetak di cell 18 → tab baru terbuka.
   - Pertama kali akan **loading model ±3–5 menit** (ada tulisan "Loading models..."). Sabar, tunggu sampai muncul tampilan **"StudioAI"** dengan panel kiri (Input) & kanan (Output).
5. **REKAM VIDEO (1–5 menit)** — cukup tampilkan fitur **Basic**:
   - Tunjuk kolom **Prompt** & **Negative Prompt** (ketik contoh, mis. prompt: `an astronaut on the moon, earth in background, cartoon style`).
   - Tunjuk slider **Quality Steps** & **Creativity (CFG)** di panel kiri (sidebar).
   - Klik tombol **🚀 Initialize Generation**.
   - Tunggu proses → **gambar hasil muncul** di panel kanan (Visual Output). Ini bagian WAJIB (bukti gambar tampil di layar).
   - Selesai. Video cukup ±1–2 menit.
   > Rekam layar pakai: Windows **Xbox Game Bar** (`Win + G`) atau HP/aplikasi rekam layar lain. Simpan sebagai **`video_demo_aplikasi_BFGAI.mp4`**.
   > Tab **EDIT** (inpaint/outpaint) **tidak perlu** ditunjukkan (itu fitur Advanced, di luar target Basic).
6. Setelah rekaman selesai → **File → Download → Download .ipynb** (semua sel sudah ada output).

> ⚠️ **JANGAN commit token ngrok ke GitHub (repo ini publik!).** Setelah download, beri tahu aku — token di cell 16 akan aku kembalikan ke `YOUR_AUTHENTICATION_KEY` sebelum di-zip/commit (output tetap ada, aman).

---

## 📦 BAGIAN C — Setelah 2 notebook jalan & video siap
Kabari aku. Aku yang akan:
- Sanitasi token ngrok di notebook Streamlit.
- Buat `requirements.txt`.
- Susun **zip flat** `BFGAI_Dafina_Meira_Rizkia.zip` (4 file: 2 ipynb + mp4 + requirements.txt).
- Update STATUS + commit.

Lalu Dafina tinggal **upload zip ke Dicoding**. 🎉

---

### ❓ Kalau ada error
- **`ngrok` limit / tunnel error** → jalankan cell 21 manual (hapus `#` pada `ngrok.kill()`), lalu jalankan ulang cell 16 & 18.
- **App error "image_to_url"** → berarti versi streamlit salah; pastikan cell 2 tidak diubah (harus `streamlit==1.29.0`).
- **OOM / CUDA out of memory** → klik tombol **🧹 Flush RAM** di app, atau Runtime → Restart, lalu Run all lagi.
- **Model gagal diunduh** → Run ulang sel load model (cell 4 & 25 di Pipeline; cell 16 di Streamlit memicu load saat app dibuka).
