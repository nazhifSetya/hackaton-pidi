# Panduan Submission — Food Recognizer App

Panduan singkat untuk build, uji, dan submit proyek akhir kelas *Belajar Penerapan Machine Learning untuk Flutter* (Dicoding).

## 1. Struktur folder

```
proyek_akhir/
├── submission/food_recognizer/   ← proyek Flutter (yang di-ZIP dan di-upload)
├── assets_source/                 ← sumber model + sampel gambar makanan (jangan ikut di-ZIP)
├── panduan/                       ← folder ini
└── scratchpad/                    ← screenshot uji (jangan ikut di-ZIP)
```

## 2. Persiapan environment

- Flutter stable, SDK Dart ≥ 3.7.
- Android SDK + emulator (mis. `emulator-5554`). Path `adb` di komputer ini: `D:\AndroidSdk\platform-tools\adb.exe`.
- Ruang bebas emulator (`adb shell df /data`) minimal **~500 MB** karena debug APK ~178 MB.

## 3. Build & install ke emulator

```powershell
cd submission/food_recognizer
flutter pub get
flutter build apk --debug --android-skip-build-dependency-validation

& "D:\AndroidSdk\platform-tools\adb.exe" install -r build/app/outputs/flutter-apk/app-debug.apk
```

Kalau muncul `Requested internal only, but not enough space`:
1. `adb shell pm list packages -3` — cari paket lama yang bisa dihapus (mis. instalasi submission sebelumnya `com.dicoding.flutter.u758.submission`).
2. `adb uninstall <package>` untuk membebaskan ruang.
3. `adb shell pm trim-caches 999999999999`.
4. Coba install ulang.

## 4. Uji aplikasi (jalur golden path)

1. Buka aplikasi **Food Recognizer** di emulator.
2. Push satu sampel gambar ke device:
   ```powershell
   & "D:\AndroidSdk\platform-tools\adb.exe" push `
     "../assets_source/sample_images/nasi-lemak.jpg" "/sdcard/Download/nasi-lemak.jpg"
   & "D:\AndroidSdk\platform-tools\adb.exe" shell `
     "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/Download/nasi-lemak.jpg"
   ```
3. Di aplikasi: tap **Galeri** → pilih `nasi-lemak.jpg` → tap **Done** → tap **Analyze**.
4. Halaman **Result Page** akan menampilkan gambar + label (mis. `Nasi lemak`) + confidence (`69.02%`).
5. Untuk uji kamera: tap **Kamera**, izinkan permission, ambil foto (emulator memakai virtual scene).

## 5. Cek kriteria yang tercapai

| Kriteria | Target | Bukti dalam proyek |
|---|---|---|
| K1 Pengambilan Gambar | Basic (2 pts) | `image_picker` camera + gallery di `lib/controller/home_controller.dart`. |
| K2 Machine Learning | Basic (2 pts) | LiteRT via `tflite_flutter` menjalankan `aiy_food_v1.tflite` di `lib/service/food_classifier.dart`. |
| K3 Halaman Prediksi | Basic (2 pts) | `lib/ui/result_page.dart` menampilkan gambar + nama makanan + confidence. |

Nilai akhir: `(2+2+2)/3 = 2.0` → **Bintang 3 (C, Cukup)** — lulus dengan aman.

Kalau ingin naik ke Skilled/Advanced (image_cropper, Isolate, MealDB, Gemini, Firebase ML), lihat catatan di `proyek_akhir/CLAUDE.md` seksi terakhir.

## 6. Bersih-bersih sebelum ZIP

```powershell
cd submission/food_recognizer
flutter clean
Remove-Item -Recurse -Force .dart_tool, build -ErrorAction SilentlyContinue
```

Pastikan **tidak ada** folder `build/` dan `.dart_tool/`. Model tflite (~24 MB) tetap disertakan di `assets/models/`.

## 7. Kompres jadi ZIP

Dari folder `proyek_akhir/submission/`:

```powershell
Compress-Archive -Path food_recognizer -DestinationPath food_recognizer.zip -Force
Get-Item food_recognizer.zip | Select-Object Name, Length
```

- Ukuran ZIP harus **≤ 25 MB** (Dicoding).
- ZIP hanya berisi folder `food_recognizer/` — bukan `assets_source/`, `panduan/`, `scratchpad/`, atau `starter.zip`/`assets.zip`.

## 8. Upload

Login ke [dicoding.com/academysubmissions/my](https://www.dicoding.com/academysubmissions/my) dan unggah `food_recognizer.zip`. Reviewer menilai dalam ~3 hari kerja.

## Referensi

- Instruksi resmi: `07 - Penutup/04 - Submission Food Recognizer App.md`
- Model: [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1)
- Sampel gambar: [dicodingacademy/assets](https://github.com/dicodingacademy/assets/raw/refs/heads/main/flutter_ml/assets/assets.zip)
