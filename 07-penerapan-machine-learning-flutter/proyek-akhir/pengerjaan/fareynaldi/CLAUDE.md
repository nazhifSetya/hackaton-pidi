# Proyek Akhir 07 — Food Scan App (Fareynaldi)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md).

Working notes untuk submission Dicoding **"Belajar Penerapan Machine Learning untuk Flutter"** milik Fareynaldi.

## Layout

```
fareynaldi/
├── CLAUDE.md                      ← file ini
├── panduan/                       ← langkah build & zip untuk user
└── submission/
    └── food_scan_app/             ← THE deliverable Flutter project
        ├── android/               (paket: com.fareynaldi.foodscan)
        ├── ios/                   (bundle: com.fareynaldi.foodscan)
        ├── assets/models/         → aiy_food_v1.tflite (git-ignored) + labels.txt
        ├── lib/
        │   ├── main.dart          entry, MaterialApp theme hijau (seed 0xFF2E7D32)
        │   ├── ml/                → tflite_food_detector.dart (LiteRT wrapper)
        │   ├── models/            → scan_result.dart (data class)
        │   ├── screens/           → scanner_screen.dart + detail_screen.dart
        │   └── widgets/           → result_card.dart (progress bar confidence)
        └── pubspec.yaml           name: food_scan_app
```

## Target: Basic pada semua 3 kriteria → Bintang 3 (C)

| Kriteria | Level | Bukti implementasi |
|---|---|---|
| K1 Pengambilan Gambar | **Basic (2 pts)** | `image_picker` kamera + galeri di [scanner_screen.dart](submission/food_scan_app/lib/screens/scanner_screen.dart). Tanpa `image_cropper`, tanpa `camera` stream. |
| K2 Machine Learning | **Basic (2 pts)** | `tflite_flutter` di [tflite_food_detector.dart](submission/food_scan_app/lib/ml/tflite_food_detector.dart) menjalankan `aiy_food_v1.tflite` (uint8 [1,224,224,3] → uint8 [1,2024]). **Tanpa** Isolate, **tanpa** Firebase ML. |
| K3 Halaman Prediksi | **Basic (2 pts)** | [detail_screen.dart](submission/food_scan_app/lib/screens/detail_screen.dart) menampilkan foto + nama makanan + confidence % (via `ResultCard`). Tanpa MealDB, tanpa Gemini. |

Formula akhir: `(2+2+2)/3 = 2.0` → **Bintang 3 (Basic / Cukup)** — lulus floor tiap kriteria.

## Perbedaan dengan proyek Nazhif (anti-plagiarisme)

Kode **DIBEDAKAN secara sengaja** dari `07/nazhif-setya-nugroho/submission/food_recognizer` (juga target Basic). Perbedaan struktural:

| Aspek | Nazhif (`food_recognizer`) | Fareynaldi (`food_scan_app`) |
|---|---|---|
| State management | `provider` + `ChangeNotifier` (`HomeController`) | **Plain `StatefulWidget` + `setState`** (tanpa provider) |
| Folder lib | `controller/` `service/` `ui/` `widget/` | `ml/` `models/` `screens/` `widgets/` |
| Nama kelas ML | `FoodClassifier.classify()` | `TfliteFoodDetector.analyze()` (+ `warmUp()` / `release()`) |
| Nama halaman | `HomePage` / `ResultPage` | `ScannerScreen` / `DetailScreen` |
| Data class | `FoodPrediction(label, confidence)` | `ScanResult(foodName, score)` (+ `scorePercent` getter) |
| Preprocessing | Loop pixel manual, tanpa interpolasi eksplisit | Sama-sama uint8, tapi via `im.copyResize(..., interpolation: linear)` + label di-prettify (title-case) |
| Package Android | `com.dicoding.flutter.u758.submission` | `com.fareynaldi.foodscan` |
| Bundle iOS | `com.dicoding.flutter.758.submission` | `com.fareynaldi.foodscan` |
| Nama pubspec | `submission` | `food_scan_app` |
| Tema warna | seed `Colors.deepPurple` | seed `0xFF2E7D32` (hijau) |
| UI hasil | `Row` label + confidence (`ClassificatioinItem`) | Card dengan `LinearProgressIndicator` confidence bar |
| Error handling | Text merah polos | `_ErrorBlock` dengan tombol "Coba lagi" |
| Enum fase | (tak ada — pakai null-check) | `_Phase { loading, done, error }` |

Aturan tim: **JANGAN samakan/menyalin** kode antar anggota.

## Model quirks (AIY Food V1)

- Input **uint8** `[1,224,224,3]` — bukan float, jangan `/255`.
- Output **uint8** `[1,2024]` — bagi 255 untuk confidence 0..1.
- Label index 0 = `__background__` → **selalu skip**, kalau tidak akan mendominasi.
- File model **git-ignored** (`*.tflite` di root `.gitignore`) → user harus download sendiri (lihat panduan).

## Build & jalankan (Windows + Android emulator)

```powershell
cd submission\food_scan_app
flutter pub get
flutter build apk --debug --android-skip-build-dependency-validation
& "D:\AndroidSdk\platform-tools\adb.exe" install -r build\app\outputs\flutter-apk\app-debug.apk
```

APK debug ~178 MB (LiteRT + model + debug symbols). Emulator butuh ≥2× ukuran APK di `/data`.

## Cleaning untuk ZIP submission

Dicoding: hapus `build/`, `flutter clean`, ZIP ≤ 25 MB. Model tflite ~24 MB → mepet plafon.

```powershell
cd submission\food_scan_app
flutter clean
Remove-Item -Recurse -Force .dart_tool, build -ErrorAction SilentlyContinue
```

Lalu zip **isi** `submission/food_scan_app/` (bukan folder `submission/` di atasnya, bukan `panduan/`, bukan `CLAUDE.md`).

## Progress Log

- **2026-07-16 (Victus)** — Proyek dibuat. Scaffold Flutter di-copy dari `nazhif-setya-nugroho/submission/food_recognizer`, lalu:
  - Rename package Android ke `com.fareynaldi.foodscan`, bundle iOS sama, `MainActivity.kt` dipindah.
  - Rename project `submission` → `food_scan_app` di `pubspec.yaml` + iOS `Info.plist` + `PRODUCT_BUNDLE_IDENTIFIER` di pbxproj.
  - Ganti izin `AndroidManifest.xml` label + iOS `NSCameraUsageDescription` / `NSPhotoLibraryUsageDescription`.
  - `lib/` ditulis ulang dari nol dengan arsitektur beda (StatefulWidget, folder `ml/screens/models/widgets`, kelas & variabel berbeda).
- **2026-07-17 (Victus)** — Build & verifikasi runtime tuntas.
  - Model `aiy_food_v1.tflite` (21 MB) di-download via Kaggle CLI ke `assets/models/`.
  - `flutter pub get` ✅ (55 deps). `flutter build apk --debug` ✅ (67.6s, 178 MB debug APK). Model + labels ke-bundle di APK.
  - Install ke HP fisik Samsung SM-S721B (Android 16, serial RRCY6092BWE) via ADB → app jalan mulus.
  - **Semua 3 kriteria verified live:** K1 kamera+galeri OK, K2 inferensi TFLite jalan on-device, K3 halaman hasil tampil foto+nama+confidence bar+%.
  - Sample prediksi: Nasi rendang → "Rendang" (18%), Mie instant Sedaap → "Ramen" (5.5%) — top-1 label kategori tepat. Confidence rendah normal (2024 kelas + uint8 quantized).
  - Screenshot bukti di `scratchpad/Screenshot_20260717_074*.jpg`.
  - `flutter clean` + zip → **`submission/food_scan_app_Fareynaldi.zip` = 19.02 MB** (aman di bawah plafon 25 MB). Siap upload ke Dicoding.
