# Proyek Akhir — Food Recognizer Playbook

Working notes for future sessions on the Dicoding submission `Belajar Penerapan Machine Learning untuk Flutter`.

## Layout

```
proyek_akhir/
├── a758-machine-learning-flutter-submission/  Upstream starter clone (reference only)
├── assets_source/                             Model + sample food images (source of truth)
│   ├── model/                                 aiy_food_v1.tflite + labels
│   └── sample_images/                         beef-bourguignon, nasi-lemak, satay, sushi, etc.
├── assets.zip                                 Original Dicoding sample bundle
├── starter.zip                                Original Dicoding starter bundle
├── model_download/                            Raw Kaggle model download
├── panduan/                                   User-facing submission guide (ID)
├── scratchpad/                                Ephemeral screenshots for UI verification
└── submission/food_recognizer/                THE deliverable Flutter project
```

## Submission scope (shipped as Basic on all three kriteria — target grade Bintang 3 / C)

| Kriteria | Level | Evidence |
|---|---|---|
| K1 Pengambilan Gambar | **Basic (2pts)** | `image_picker` camera + gallery in `lib/controller/home_controller.dart`. No `image_cropper`, no `camera` stream. |
| K2 Machine Learning | **Basic (2pts)** | `tflite_flutter` in `lib/service/food_classifier.dart` running `assets/models/aiy_food_v1.tflite` (AIY Food V1, uint8 [1,224,224,3] → uint8 [1,2024]). No Isolate/`compute`, no Firebase ML. |
| K3 Halaman Prediksi | **Basic (2pts)** | `lib/ui/result_page.dart` shows picked image + label + confidence %. No MealDB, no Gemini. |

Final formula: `(2+2+2)/3 = 2.0` → **Bintang 3 (C, Basic, Cukup)** — passes floor on every kriteria.

## Model quirks (AIY Food V1)

- Input: **uint8** `[1,224,224,3]`, not float. No `/255` normalization.
- Output: **uint8** `[1,2024]` quantized probabilities → divide by 255 for 0..1 confidence.
- Label index 0 is `__background__` — always skip it, otherwise it dominates on anything not-food.
- Labels file: `aiy_food_V1_labels.txt` (note capital V in filename — Kaggle download quirk).

## Build / run on Windows + Android emulator

```powershell
# 1. Ensure emulator running
& "D:/AndroidSdk/platform-tools/adb.exe" devices

# 2. Build debug APK (from submission/food_recognizer/)
flutter build apk --debug --android-skip-build-dependency-validation

# 3. Install
& "D:/AndroidSdk/platform-tools/adb.exe" install -r build/app/outputs/flutter-apk/app-debug.apk
```

### Space trap on the shared emulator

Debug APK is ~178 MB (LiteRT + model + debug symbols). Emulator `/data` needs ~2× the APK size for install or you'll hit `Requested internal only, but not enough space`. Check with `adb shell df /data`; free space by uninstalling stale packages (`com.dicoding.flutter.u758.submission` is safe if this project is what installed it) and running `pm trim-caches`.

### Screenshot gotcha on Windows

`adb exec-out screencap -p > file.png` from PowerShell CRLF-mangles the PNG. From Git Bash it works. Always `file <path>` to verify — a broken PNG shows as `data`, a good one as `PNG image data, WxH, ...`. If mangled, delete and retake from Bash.

### Coordinate math for `adb shell input tap`

`adb screencap` returns the device-native resolution (1080×2400 on this emulator). The Read tool may downscale for display and prints a "multiply by X" hint — always multiply back before tapping. `input tap` expects device coords.

## Cleaning for ZIP submission

Dicoding requires: no `build/`, run `flutter clean`, keep ZIP ≤ 25 MB. **But** the tflite model alone is ~24 MB — very close to the ceiling. Do NOT include `assets_source/`, `panduan/`, `scratchpad/`, the original zips, or `a758-machine-learning-flutter-submission/` in the delivered ZIP. Only zip the contents of `submission/food_recognizer/` (post-clean).

```powershell
cd submission/food_recognizer
flutter clean
Remove-Item -Recurse -Force .dart_tool, build -ErrorAction SilentlyContinue
# then zip the folder from its parent
```

## If someone asks to push to Skilled/Advanced

Rough map of what would need to land:
- **K1 Skilled**: add `image_cropper` after pick in `HomeController.pickFrom*`.
- **K1 Advanced**: add `camera` package + live inference screen.
- **K2 Skilled**: move `classify()` work off the platform thread — cheapest path is `flutter/foundation`'s `compute()` around the preprocess+`interpreter.run` block. Isolate needs to load its own interpreter (interpreters aren't thread-safe).
- **K2 Advanced**: `firebase_ml_model_downloader` + `firebase_core`. Requires `google-services.json` and adjusting `android/app/build.gradle.kts`. Must include `firebase_options.dart`.
- **K3 Skilled**: MealDB — `https://www.themealdb.com/api/json/v1/1/search.php?s=<label>` + a details lookup by `idMeal`.
- **K3 Advanced**: Gemini via `google_generative_ai` with structured output (kalori/karbo/lemak/serat/protein in grams). User can supply their own key at runtime.
