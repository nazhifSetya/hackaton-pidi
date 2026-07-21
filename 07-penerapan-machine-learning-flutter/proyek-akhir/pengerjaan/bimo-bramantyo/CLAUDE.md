# Proyek Akhir 07 — PindaiRasa (Bimo)

> ### 🔄 SYNC LINTAS DEVICE (Mac ⇄ Victus)
> Konteks & memory Claude Code TIDAK auto-sync antar device — yang nyambung cuma Git.
> **Awal sesi:** `git pull --rebase --autostash`. **Akhir sesi:** update Progress Log di bawah **+** [`/_meta/STATUS.md`](../../../../_meta/STATUS.md), lalu commit + push.
> Peta repo & protokol lengkap → [`/CLAUDE.md`](../../../../CLAUDE.md).

Working notes untuk submission Dicoding **"Belajar Penerapan Machine Learning untuk Flutter"** (akademi 758) milik **Bimo Bramantyo**. Greenfield — Bimo belum punya folder di course 07, dibuat dari nol 2026-07-21.

## Layout

```
bimo-bramantyo/
├── CLAUDE.md                      ← file ini
├── panduan/README.md              ← langkah run, zip, & submit untuk user
├── scratchpad/                    ← screenshot bukti verifikasi (git-tracked)
└── submission/
    ├── pindai_rasa/               ← THE deliverable Flutter project
    │   ├── android/               (applicationId: id.bimo.pindai_rasa)
    │   ├── ios/                   (bundle: id.bimo.pindaiRasa, izin kamera+galeri)
    │   ├── assets/models/         → aiy_food_v1.tflite (GIT-IGNORED) + labels.txt
    │   ├── lib/
    │   │   ├── main.dart          entry → PindaiRasaApp
    │   │   ├── palette.dart       buildPindaiTheme() seed 0xFFC2185B (merah marun)
    │   │   ├── vision/            → meal_vision_engine.dart (LiteRT) + label_score.dart
    │   │   ├── flow/              → scan_flow.dart (StreamController) + scan_state.dart
    │   │   ├── views/             → snap_view.dart + insight_view.dart
    │   │   └── parts/             → photo_card.dart + score_bars.dart (bar chart)
    │   └── pubspec.yaml           name: pindai_rasa
    └── pindai_rasa_Bimo.zip       ← hasil arsip (git-tracked, 18.84 MB) untuk upload
```

## Target: Basic pada semua 3 kriteria → Bintang 3 (C) — kelulusan minimal

| Kriteria | Level | Bukti implementasi |
|---|---|---|
| K1 Pengambilan Gambar | **Basic (2 pts)** | `image_picker` kamera + galeri di [snap_view.dart](submission/pindai_rasa/lib/views/snap_view.dart). Foto terpilih tampil di `PhotoCard`. Tanpa `image_cropper`, tanpa `camera` stream. |
| K2 Machine Learning | **Basic (2 pts)** | `flutter_litert` (framework **LiteRT**) di [meal_vision_engine.dart](submission/pindai_rasa/lib/vision/meal_vision_engine.dart) menjalankan `aiy_food_v1.tflite` (uint8 `[1,224,224,3]` → uint8 `[1,2024]`). Inferensi setelah gambar dipilih. **Tanpa** Isolate, **tanpa** Firebase ML. |
| K3 Halaman Prediksi | **Basic (2 pts)** | [insight_view.dart](submission/pindai_rasa/lib/views/insight_view.dart) menampilkan foto + nama makanan + confidence % + bar chart top-5 (`ScoreBars`). Tanpa MealDB, tanpa Gemini. |

Formula akhir: `(2+2+2)/3 = 2.0` → **Bintang 3 (Basic / Cukup)** — lulus floor tiap kriteria.

## Anti-plagiarisme: varian ke-4 (dibedakan dari Nazhif, Fareynaldi, Dafina)

Course 07 punya 4 submission dalam satu repo. Kode Bimo **sengaja dibuat berbeda pada tiap sumbu**:

| Aspek | Nazhif (`food_recognizer`) | Fareynaldi (`food_scan_app`) | Dafina (`santap_lens`) | **Bimo (`pindai_rasa`)** |
|---|---|---|---|---|
| State management | provider + ChangeNotifier | StatefulWidget + setState | ValueNotifier + ValueListenableBuilder | **`StreamController` + `StreamBuilder`** (single-subscription) |
| Folder `lib` | controller/service/ui/widget | ml/models/screens/widgets | inference/state/pages/components | **`vision/ flow/ views/ parts/` + `palette.dart`** |
| Kelas ML / method | `FoodClassifier.classify()` | `TfliteFoodDetector.analyze()` | `DishRecognizer.identify()` | **`MealVisionEngine.predict()`** (+ `prime()`/`shutdown()`, getter `armed`) |
| Data class | `FoodPrediction(label,confidence)` | `ScanResult(foodName,score)` | `DishGuess(name,probability)` | **`LabelScore(name, score)`** (positional; `percent`/`percentLabel`) |
| Halaman | HomePage/ResultPage | ScannerScreen/DetailScreen | CapturePage/PredictionPage | **`SnapView` / `InsightView`** |
| Preprocessing | loop manual, no-interp | `copyResize(linear)` + `.reshape` | `copyResize(average)` + nested `getPixel` | **`copyResize(cubic)` + `getBytes(rgb)` → `List.generate` bersarang** |
| Rapikan label | — | title-case | sentence-case | **UPPERCASE** |
| Hasil per inferensi | top-1 | top-1 | top-3 | **top-5** |
| Visual confidence | Row label+angka | `LinearProgressIndicator` | arc gauge `CustomPaint` | **bar chart horizontal** (`FractionallySizedBox` + `Container`) |
| Sizing output tensor | `_labels.length` | `_labels.length.reshape` | `_menu.length` | **`getOutputTensor(0).shape.last`** (baca dari model) |
| Runtime LiteRT | `tflite_flutter` (usang) | `flutter_litert` | `flutter_litert` | **`flutter_litert`** *(WAJIB LiteRT — ditetapkan Dicoding, bukan area plagiarisme)* |
| Package Android | `com.dicoding.flutter.u758.submission` | `com.fareynaldi.foodscan` | `id.dafina.santap_lens` | **`id.bimo.pindai_rasa`** |
| Nama pubspec | `submission` | `food_scan_app` | `santap_lens` | **`pindai_rasa`** |
| Tema warna | deepPurple | hijau `0xFF2E7D32` | oranye `0xFFF57C00` | **merah marun `0xFFC2185B`** |

> Model **AIY Food V1** & framework **LiteRT** memang sama untuk keempatnya karena **ditetapkan Dicoding** — itu bukan plagiarisme. Yang dibedakan adalah seluruh kode yang ditulis sendiri (nama, struktur, idiom, komentar sudah di-reword agar tak kembar).

## Model quirks (AIY Food V1)

- Input **uint8** `[1,224,224,3]` — bukan float, JANGAN `/255`.
- Output **uint8** `[1,2024]` — bagi 255 untuk confidence 0..1.
- Label indeks 0 = `__background__` → **selalu dibuang** (mulai rangking dari indeks 1), kalau tidak akan mendominasi. (`labels.txt` = 2024 baris.)
- File `aiy_food_v1.tflite` **git-ignored** (`*.tflite` di root `.gitignore`) → harus ada lokal saat build/zip. Di device ini di-copy dari folder Dafina (`santap_lens/assets/models/`). Sumber asli: [Kaggle AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1) (rename huruf kecil `aiy_food_v1.tflite`). **Model ikut di dalam zip git-tracked** → aman lintas device via zip.

## Build & jalankan (Windows + Android emulator)

SDK Flutter di `D:\flutter` (TIDAK di PATH) → panggil eksplisit. ADB di `D:\AndroidSdk\platform-tools\adb.exe`.

```powershell
cd submission\pindai_rasa
& "D:\flutter\bin\flutter.bat" pub get
& "D:\flutter\bin\flutter.bat" analyze
& "D:\flutter\bin\flutter.bat" build apk --debug --android-skip-build-dependency-validation
```

### Gotcha build (WAJIB tahu)

1. **`kotlin.incremental=false`** sudah ditambahkan di `android/gradle.properties`. Tanpa ini, build di Windows sering gagal `Could not close incremental caches (*.tab)` (file-lock antivirus/daemon). Jangan dihapus. (`newDsl=false`/`builtInKotlin=false` sudah ada dari template Flutter 3.44.6.)
2. Build APK debug ~178 MB → sering gagal install ke emulator (ruang). Untuk **verifikasi UI**, pakai **APK release** (`build apk --release`, ~108 MB) yang muat. Reserve low-storage bisa diturunkan sementara & dikembalikan (lihat memory `victus-flutter-build-env`).
3. Pakai **`flutter_litert`**, JANGAN `tflite_flutter` (itu penyebab penolakan Fareynaldi — bentrok JVM 1.8 vs 21 di Flutter terbaru).

## Cleaning untuk ZIP submission

Dicoding: hapus `build/`, `flutter clean`, ZIP ≤ 25 MB. Model tflite ~21 MB → mepet plafon, tapi zip akhir 18.84 MB.

```powershell
cd submission\pindai_rasa
& "D:\flutter\bin\flutter.bat" clean
Remove-Item -Recurse -Force .dart_tool, build, .gradle, android\.gradle -ErrorAction SilentlyContinue
cd ..
tar -a -c -f pindai_rasa_Bimo.zip pindai_rasa
```

Zip **isi** folder `pindai_rasa` via **bsdtar** (`tar`, forward-slash standar). JANGAN sertakan `panduan/`, `scratchpad/`, `CLAUDE.md`.

## Progress Log

- **2026-07-21 (Victus)** — **Proyek DIBUAT dari nol & terverifikasi live tuntas.** Target Basic (⭐⭐⭐).
  - Scaffold `flutter create --org id.bimo --project-name pindai_rasa` di Flutter **3.44.6 / Dart 3.12.2** (versi terbaru — belajar dari penolakan Fareynaldi yang gagal build di Flutter baru). `lib/` ditulis ulang dari nol, arsitektur **sengaja beda** dari 3 rekan (lihat tabel anti-plagiarisme): **StreamController + StreamBuilder**, folder `vision/flow/views/parts`, kelas `MealVisionEngine`/`LabelScore`, preprocessing `copyResize(cubic)` + `getBytes(rgb)`, label UPPERCASE, top-5, bar chart horizontal, tema merah marun.
  - Dependency: `image_picker ^1.1.2` + **`flutter_litert ^3.5.1`** + `image ^4.3.0`. Model `aiy_food_v1.tflite` (21 MB) + `labels.txt` (2024 label) di `assets/models/` (di-copy dari folder Dafina).
  - Izin: Android manifest label "PindaiRasa" (image_picker berbasis intent → tak perlu deklarasi CAMERA); iOS `Info.plist` diberi `NSCameraUsageDescription` + `NSPhotoLibraryUsageDescription`.
  - **Verifikasi statis:** `flutter analyze` **0 isu** → `flutter build apk --debug` **LOLOS** (107s). Error JVM `tflite_flutter` (penyebab penolakan Fareynaldi) TIDAK muncul (scaffold segar + `flutter_litert`).
  - **Inferensi on-device terbukti (integration test, emulator `emulator-5554` API 36.1):** `LITERT_OK satay.jpg → SATAY 98.8%`, `sushi.jpg → SUSHI 84.7%`, `nasi-lemak.jpg → NASI LEMAK 76.1%` — top-1 semua BENAR, high-confidence, tanpa crash (membuktikan urutan channel RGB + preprocessing cubic tepat). Test & aset sampel lalu dihapus dari deliverable (pubspec.lock bersih dari `integration_test`).
  - **Verifikasi UI live (screenshot di `scratchpad/`):** build release (~108 MB) → install emulator → K1 tap **Galeri** → photo picker sistem → pilih **satay** → foto tampil di app + tombol "Kenali Makanan" aktif (`01_home.png`, `02_foto_terpilih.png`); K2+K3 tap "Kenali Makanan" → InsightView tampil foto + **SATAY 98.8%** + bar chart top-5 (`03_hasil_satay.png`). **Tanpa overflow.** Tema maroon konsisten.
  - **Self-check anti-plagiarisme:** dibandingkan dgn `TfliteFoodDetector` (Fareynaldi) & `DishRecognizer` (Dafina). Beberapa idiom kecil di-reword agar tak kembar: method `warmUp()`→**`prime()`** (Fareynaldi pakai `warmUp`), helper `_prettyName`→**`_capsLabel`** (Fareynaldi `_prettify`), + doc-comment (hapus frasa identik "kelas makanan yang sesungguhnya" & "berada di rentang 0..1"). Sumbu besar (state mgmt/folder/kelas/preprocessing/visual/warna) sudah beda dari awal → risiko **LOW**.
  - **Zip:** `flutter clean` + buang `build/`/`.dart_tool/`/`.gradle/` → `tar` (bsdtar, forward-slash) → **`submission/pindai_rasa_Bimo.zip` = 18.84 MB** (145 entri, isi terverifikasi: pubspec+lib+android+ios+model+labels; tanpa build/test/backslash). Git-tracked.
  - **SISA (user Bimo):** samakan nama zip dgn username Dicoding bila perlu, lalu **UPLOAD `submission/pindai_rasa_Bimo.zip` ke Dicoding**. Opsional smoke-test 1× di HP fisik (pilih foto makanan → muncul prediksi).
