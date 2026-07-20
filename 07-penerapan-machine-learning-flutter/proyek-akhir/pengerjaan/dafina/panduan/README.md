# Panduan SantapLens (Dafina) — Submission Flutter 07

Aplikasi **SantapLens**: foto makanan → aplikasi menebak namanya pakai model
**AIY Food V1** yang jalan on-device lewat **LiteRT**. Target nilai: **Bintang 3
(Basic)** — cukup untuk lulus.

Semua kode sudah dibuat & **diverifikasi jalan** di Victus (build lolos +
inferensi benar "Satay" 99.6% di emulator). Yang tersisa untukmu cuma
**mengecek sekali & upload zip**.

---

## 0. Prasyarat (sudah beres di Victus)

- Flutter **3.44.6** (Dart 3.12.2) di `D:\flutter` (tidak di PATH → panggil `& "D:\flutter\bin\flutter.bat"`).
- Model `assets/models/aiy_food_v1.tflite` (21 MB) **sudah ada** di folder proyek. (File ini git-ignored — kalau pindah device, download ulang dari [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1), rename huruf kecil `aiy_food_v1.tflite`, taruh di `submission/santap_lens/assets/models/`.)

## 1. (Opsional) Coba jalankan sendiri di HP / emulator

```powershell
cd 07-penerapan-machine-learning-flutter\proyek-akhir\pengerjaan\dafina\submission\santap_lens
& "D:\flutter\bin\flutter.bat" pub get
& "D:\flutter\bin\flutter.bat" run
```

Alur uji: buka app → tekan **Kamera** (foto makanan) atau **Galeri** (pilih foto
makanan) → foto muncul → tekan **Kenali Makanan** → halaman hasil menampilkan
nama makanan + persen keyakinan.

> Catatan: model mengenali **2.023 jenis makanan dunia**, jadi persen keyakinan
> yang tampak kecil itu **wajar** (bukan bug). Untuk foto makanan yang jelas
> (mis. satay, sushi), nama top-1 biasanya tepat.

## 2. Bersihkan proyek sebelum zip (WAJIB)

Dicoding menolak kalau ada folder `build/` atau zip > 25 MB.

```powershell
cd 07-penerapan-machine-learning-flutter\proyek-akhir\pengerjaan\dafina\submission\santap_lens
& "D:\flutter\bin\flutter.bat" clean
Remove-Item -Recurse -Force .dart_tool, build, .gradle, "android\.gradle" -ErrorAction SilentlyContinue
```

## 3. Buat ZIP

Zip **isi** folder `santap_lens` (bukan folder `submission/` di atasnya, dan
**jangan** ikutkan `panduan/`, `scratchpad/`, `CLAUDE.md`).

Cara paling aman (Git Bash, path forward-slash standar):

```bash
cd .../pengerjaan/dafina/submission
tar -C . -a -c -f santap_lens_Dafina.zip santap_lens
```

Zip target **± 18–19 MB** (di bawah plafon 25 MB). File sudah dibuatkan di
`submission/santap_lens_Dafina.zip`.

## 4. Cek isi ZIP

Pastikan berisi: `pubspec.yaml`, `lib/`, `android/`, `ios/`,
`assets/models/aiy_food_v1.tflite` + `labels.txt`, **TANPA** `build/`,
`.dart_tool/`, `.gradle/`.

## 5. Upload ke Dicoding

Submit `santap_lens_Dafina.zip` di halaman submission kelas 758. (Boleh ganti
nama zip agar cocok dengan username Dicoding-mu bila diminta.)

---

## Ringkasan kriteria yang dipenuhi (Basic / ⭐⭐⭐)

| Kriteria | Cara dipenuhi |
|---|---|
| **K1 Pengambilan Gambar** | `image_picker` — tombol **Kamera** & **Galeri**; foto terpilih tampil di halaman. |
| **K2 Machine Learning** | Model AIY Food V1 dijalankan via **LiteRT** (`flutter_litert`); inferensi setelah foto dipilih. |
| **K3 Halaman Prediksi** | Halaman hasil: foto + nama makanan + keyakinan % (gauge melingkar). |

Tanpa fitur crop/camera-stream/Isolate/Firebase ML/MealDB/Gemini — semua itu
untuk nilai lebih tinggi, tidak diperlukan untuk lulus.
