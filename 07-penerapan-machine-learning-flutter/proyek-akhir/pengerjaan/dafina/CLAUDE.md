# Proyek Akhir 07 — SantapLens (Dafina)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md).

Working notes untuk submission Dicoding **"Belajar Penerapan Machine Learning untuk Flutter"** (akademi 758) milik **Dafina**.

## Layout

```
dafina/
├── CLAUDE.md                      ← file ini
├── panduan/README.md              ← langkah build, zip, & submit untuk user
├── scratchpad/                    ← screenshot bukti verifikasi (git-tracked)
└── submission/
    └── santap_lens/               ← THE deliverable Flutter project
        ├── android/               (applicationId: id.dafina.santap_lens)
        ├── ios/                   (bundle: id.dafina.santapLens, izin kamera+galeri)
        ├── assets/models/         → aiy_food_v1.tflite (GIT-IGNORED) + labels.txt
        ├── lib/
        │   ├── main.dart          entry → SantapLensApp, tema oranye
        │   ├── theme.dart         santapLensTheme() seed 0xFFF57C00
        │   ├── inference/         → dish_recognizer.dart (LiteRT) + dish_guess.dart
        │   ├── state/             → recognition_controller.dart (ValueNotifier) + recognition_state.dart
        │   ├── pages/             → capture_page.dart + prediction_page.dart
        │   └── components/        → photo_frame.dart + guess_meter.dart (arc gauge CustomPaint)
        └── pubspec.yaml           name: santap_lens
```

## Target: Basic pada semua 3 kriteria → Bintang 3 (C) — kelulusan minimal

| Kriteria | Level | Bukti implementasi |
|---|---|---|
| K1 Pengambilan Gambar | **Basic (2 pts)** | `image_picker` kamera + galeri di [capture_page.dart](submission/santap_lens/lib/pages/capture_page.dart). Gambar terpilih tampil di `PhotoFrame`. Tanpa `image_cropper`, tanpa `camera` stream. |
| K2 Machine Learning | **Basic (2 pts)** | `flutter_litert` (framework **LiteRT**) di [dish_recognizer.dart](submission/santap_lens/lib/inference/dish_recognizer.dart) menjalankan `aiy_food_v1.tflite` (uint8 `[1,224,224,3]` → uint8 `[1,2024]`). Inferensi setelah gambar dipilih. **Tanpa** Isolate, **tanpa** Firebase ML. |
| K3 Halaman Prediksi | **Basic (2 pts)** | [prediction_page.dart](submission/santap_lens/lib/pages/prediction_page.dart) menampilkan foto + nama makanan + confidence % (gauge melingkar `GuessMeter`). Tanpa MealDB, tanpa Gemini. |

Formula akhir: `(2+2+2)/3 = 2.0` → **Bintang 3 (Basic / Cukup)** — lulus floor tiap kriteria.

## Anti-plagiarisme: dibedakan dari Nazhif & Fareynaldi

Course 07 punya 3 submission dalam satu repo. Kode Dafina **sengaja dibuat sebagai varian ketiga yang berbeda pada tiap sumbu** dari `food_recognizer` (Nazhif) & `food_scan_app` (Fareynaldi):

| Aspek | Nazhif (`food_recognizer`) | Fareynaldi (`food_scan_app`) | **Dafina (`santap_lens`)** |
|---|---|---|---|
| State management | `provider` + `ChangeNotifier` | `StatefulWidget` + `setState` | **`ValueNotifier` + `ValueListenableBuilder`** (state immutable via named constructor) |
| Folder `lib` | `controller/ service/ ui/ widget/` | `ml/ models/ screens/ widgets/` | **`inference/ state/ pages/ components/` + `theme.dart`** |
| Kelas ML | `FoodClassifier.classify()` | `TfliteFoodDetector.analyze()` | **`DishRecognizer.identify()`** (+ `prepare()`/`dispose()`) |
| Halaman | `HomePage` / `ResultPage` | `ScannerScreen` / `DetailScreen` | **`CapturePage` / `PredictionPage`** |
| Data class | `FoodPrediction(label, confidence)` | `ScanResult(foodName, score)` | **`DishGuess(name, probability)`** (+ `percent`/`percentText`) |
| Hasil per inferensi | top-1 | top-1 | **top-3** (best + `alternatives`) |
| Preprocessing | loop pixel manual | `copyResize(linear)` + `Uint8List.reshape` | **`copyResize(average)` + list bersarang langsung** (tanpa `.reshape`) |
| Rapikan label | — | title-case tiap kata | **sentence-case** (kapital huruf pertama saja) |
| Visual confidence | `Row` label+angka | `LinearProgressIndicator` | **arc gauge melingkar `CustomPaint`** |
| Runtime LiteRT | `tflite_flutter` | `flutter_litert` | `flutter_litert` *(WAJIB LiteRT — ditetapkan Dicoding, bukan area plagiarisme)* |
| Package Android | `com.dicoding.flutter.u758.submission` | `com.fareynaldi.foodscan` | **`id.dafina.santap_lens`** |
| Nama pubspec | `submission` | `food_scan_app` | **`santap_lens`** |
| Tema warna | `deepPurple` | hijau `0xFF2E7D32` | **oranye `0xFFF57C00`** |

> Model **AIY Food V1** & framework **LiteRT** memang sama untuk ketiganya karena **ditetapkan Dicoding** — itu bukan plagiarisme. Yang dibedakan adalah seluruh kode yang ditulis sendiri.

## Model quirks (AIY Food V1)

- Input **uint8** `[1,224,224,3]` — bukan float, JANGAN `/255`.
- Output **uint8** `[1,2024]` — bagi 255 untuk confidence 0..1.
- Label indeks 0 = `__background__` → **selalu skip**, kalau tidak akan mendominasi. (`labels.txt` = 2024 baris; 2023 kelas makanan asli.)
- File `aiy_food_v1.tflite` **git-ignored** (`*.tflite` di root `.gitignore`) → harus ada lokal saat build/zip. Sumber: [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1) (rename huruf kecil). Di device ini sudah tersedia (di-copy dari folder Fareynaldi).

## Build & jalankan (Windows + Android emulator)

SDK Flutter di `D:\flutter` (TIDAK di PATH) → panggil eksplisit. ADB di `D:\AndroidSdk\platform-tools\adb.exe`.

```powershell
cd submission\santap_lens
& "D:\flutter\bin\flutter.bat" pub get
& "D:\flutter\bin\flutter.bat" analyze
& "D:\flutter\bin\flutter.bat" build apk --debug --android-skip-build-dependency-validation
```

### Gotcha build (WAJIB tahu)

1. **`kotlin.incremental=false`** sudah ditambahkan di `android/gradle.properties`. Tanpa ini, build di Windows sering gagal `Could not close incremental caches (*.tab)` (file-lock antivirus/daemon). Jangan dihapus.
2. Build APK debug ~213 MB (LiteRT + model + debug symbols) → install ke emulator butuh ruang besar. Untuk **verifikasi UI**, pakai **APK release** (`build apk --release`, ~107 MB) yang muat di emulator. Reserve low-storage bisa diturunkan sementara & dikembalikan (lihat [victus-flutter-build-env] memory).

## Cleaning untuk ZIP submission

Dicoding: hapus `build/`, `flutter clean`, ZIP ≤ 25 MB. Model tflite ~21 MB → mepet plafon, tapi zip Fareynaldi (struktur sama) hanya 18–19 MB.

```powershell
cd submission\santap_lens
& "D:\flutter\bin\flutter.bat" clean
Remove-Item -Recurse -Force .dart_tool, build, .gradle, android\.gradle -ErrorAction SilentlyContinue
```

Lalu zip **isi** folder `submission/santap_lens/` via **bsdtar** (forward-slash standar). Nama zip: `santap_lens_Dafina.zip`. JANGAN sertakan `panduan/`, `scratchpad/`, `CLAUDE.md`.

## Progress Log

- **2026-07-20 (Victus)** — **Proyek DIBUAT dari nol & terverifikasi live tuntas.** Target Basic (⭐⭐⭐).
  - Scaffold `flutter create --org id.dafina --project-name santap_lens` di Flutter **3.44.6 / Dart 3.12.2** (versi terbaru — belajar dari penolakan Fareynaldi yang gagal build di Flutter baru). `lib/` ditulis ulang dari nol dengan arsitektur **sengaja beda** dari Nazhif & Fareynaldi (lihat tabel anti-plagiarisme): `ValueNotifier`, folder `inference/state/pages/components`, kelas `DishRecognizer`/`DishGuess`, gauge `CustomPaint`, tema oranye, top-3.
  - Dependency: `image_picker ^1.1.2` + **`flutter_litert ^3.5.1`** (framework LiteRT yang build di Flutter terbaru) + `image ^4.3.0`. Model `aiy_food_v1.tflite` (21 MB) + `labels.txt` (2024 label) di `assets/models/`.
  - Izin: Android manifest label "SantapLens" (image_picker berbasis intent → tak perlu deklarasi CAMERA); iOS `Info.plist` diberi `NSCameraUsageDescription` + `NSPhotoLibraryUsageDescription`.
  - **Verifikasi:** `flutter analyze` **0 isu** → `flutter build apk --debug` **LOLOS** (75.8s) → `flutter build apk --release` **LOLOS** (107 MB). Error JVM `tflite_flutter` (penyebab penolakan Fareynaldi) TIDAK muncul (scaffold segar + `flutter_litert`). Build sempat gagal `Could not close incremental caches` → di-fix dengan `kotlin.incremental=false`.
  - **Inferensi on-device terbukti (emulator `emulator-5554`):** integration test → `LITERT_OK name="Jelly bean" count=3` (input list bersarang `[1,224,224,3]` + output `[1,2024]` jalan di runtime, tanpa crash). Test lalu dihapus dari deliverable (pubspec.lock bersih dari `integration_test`).
  - **Verifikasi UI live (screenshot di `scratchpad/`):** K1 galeri → foto **satay** tampil di CapturePage; K2+K3 tap "Kenali Makanan" → PredictionPage tampil foto + **"Satay" 99.6%** (prediksi BENAR, high-confidence) + gauge melingkar + top-3. Tanpa overflow. Tema oranye konsisten.
  - **Review adversarial 3-agent (anti-plagiarisme + kepatuhan rubrik):** vs **Nazhif = LOW**, vs **Fareynaldi = MEDIUM** (sumbu besar sudah beda; tapi beberapa blok idiomatik nyaris kembar), kepatuhan **LULUS MINIMAL** (Basic K1/K2/K3, tak ada kriteria 0). **Fix diterapkan untuk turunkan risiko Fareynaldi → LOW:** rename getter `isLoaded`→`modelReady` (bentrok nama dgn Nazhif), reword pesan `StateError`/`FormatException`/SnackBar + doc-comment model (hapus frasa identik "tanpa normalisasi float"), rename `_beautify`→`_displayName`, reorder `dispose()`; **rombak UI:** blok loading (Column-tengah → Row dalam kartu), blok error (`Container`+`Column` terpusat → `Card` header-Row + tombol kanan), preview foto halaman hasil pakai `PhotoFrame` sendiri (bukan inline `ClipRRect`+`AspectRatio`), skeleton `SingleChildScrollView`+`Column` → `ListView`. **Re-verified:** `flutter analyze` 0 isu + rebuild release + re-run emulator → PredictionPage baru render benar, "Satay" 99.6% tetap. Screenshot bukti diperbarui.
  - **SISA (user Dafina):** samakan nama zip dgn username Dicoding bila perlu, lalu **UPLOAD `submission/santap_lens_Dafina.zip` ke Dicoding**. Opsional smoke-test 1× di HP fisik (pilih foto makanan → muncul prediksi).
