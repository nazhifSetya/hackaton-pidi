# Panduan Submission — Food Scan App (Fareynaldi)

Kelas Dicoding: **Belajar Penerapan Machine Learning untuk Flutter**.
Target nilai: **Bintang 3 (Basic / Cukup)** — lulus dengan aman.

---

## 1. Prasyarat

| Item | Versi / catatan |
|---|---|
| Flutter SDK | ≥ 3.7 (`flutter --version`) |
| Android Studio | terpasang + Android SDK + emulator API 30+ |
| Java | JDK 17 (Flutter sudah nge-set otomatis dari `flutter config`) |
| Model | `aiy_food_v1.tflite` (~24 MB) — **HARUS di-download manual**, tidak masuk Git |

---

## 2. Download model AIY Food V1

Model **tidak dicommit ke Git** (`*.tflite` di `.gitignore` root). Ambil dari Kaggle:

1. Buka https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1
2. Klik **Download** (butuh login Kaggle gratis). Format: TFLite.
3. Extract file berisi `1.tflite` (atau `aiy_vision_classifier_food_V1_1.tflite` — nama tergantung versi).
4. **Rename** file `.tflite` tersebut menjadi `aiy_food_v1.tflite` (huruf kecil `v`).
5. Taruh di:

```
submission/food_scan_app/assets/models/aiy_food_v1.tflite
```

File `labels.txt` sudah ada di folder yang sama (ikut Git).

Verifikasi:

```powershell
dir submission\food_scan_app\assets\models\
# Harus muncul 2 file: aiy_food_v1.tflite (~24 MB) dan labels.txt
```

---

## 3. Install dependency

```powershell
cd submission\food_scan_app
flutter pub get
```

---

## 4. Jalankan di emulator / device

```powershell
# Cek emulator terhubung
flutter devices

# Build & install debug APK
flutter run
```

Alternatif build manual:

```powershell
flutter build apk --debug --android-skip-build-dependency-validation
& "D:\AndroidSdk\platform-tools\adb.exe" install -r build\app\outputs\flutter-apk\app-debug.apk
```

### Uji manual (checklist)

- [ ] App terbuka, judul "Food Scan App", background hijau.
- [ ] Tombol **Kamera** meminta izin, lalu buka kamera bawaan, foto tersimpan & tampil di preview.
- [ ] Tombol **Galeri** meminta izin, lalu buka galeri, gambar tampil di preview.
- [ ] Tombol **Identifikasi Makanan** aktif setelah gambar dipilih; klik → pindah ke halaman detail.
- [ ] Halaman detail memuat model & menampilkan nama makanan + persentase confidence.
- [ ] Coba beberapa gambar (nasi lemak, sushi, burger) — hasil masuk akal.

---

## 5. Cleaning sebelum zip

Dicoding menolak proyek yang masih membawa folder `build/` atau `.dart_tool/`. ZIP wajib ≤ 25 MB.

```powershell
cd submission\food_scan_app
flutter clean
Remove-Item -Recurse -Force .dart_tool, build -ErrorAction SilentlyContinue
```

---

## 6. Buat ZIP submission

Dari `pengerjaan/fareynaldi/submission/`:

```powershell
cd submission
Compress-Archive -Path food_scan_app -DestinationPath food_scan_app_Fareynaldi.zip -Force
Get-Item food_scan_app_Fareynaldi.zip | Select-Object Name, @{n='SizeMB';e={[math]::Round($_.Length/1MB,2)}}
```

**Target:** ukuran < 25 MB. Kalau > 25 MB, cek lagi folder `build/`, `.dart_tool/`, atau aset duplikat.

---

## 7. Upload ke Dicoding

1. Buka halaman submission kelas *Belajar Penerapan Machine Learning untuk Flutter*.
2. Upload `food_scan_app_Fareynaldi.zip`.
3. Isi form yang diminta.
4. Tunggu review (max 3 hari kerja).

---

## 8. Kalau ditolak

- **K1 rejected** → cek: izin kamera/galeri di `AndroidManifest.xml` & `Info.plist`, tombol jalan tanpa error.
- **K2 rejected** → cek: file `.tflite` benar-benar ada di `assets/models/`, terdaftar di `pubspec.yaml` bagian `flutter/assets`. Coba `flutter clean && flutter pub get` lagi.
- **K3 rejected** → pastikan halaman detail menampilkan **foto + nama + confidence %** semuanya.

Bug umum: emulator kehabisan storage saat install APK (`Requested internal only, but not enough space`) — bersihkan `pm trim-caches` atau uninstall app lama.
