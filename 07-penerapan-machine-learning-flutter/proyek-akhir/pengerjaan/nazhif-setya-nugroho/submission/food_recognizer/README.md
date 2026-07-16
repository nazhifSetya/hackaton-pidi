# Food Recognizer App

Submission akhir kelas *Belajar Penerapan Machine Learning untuk Flutter* (Dicoding).

Aplikasi Flutter untuk mengklasifikasi gambar makanan menggunakan model LiteRT [AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1) (2024 kelas makanan).

## Fitur

- **Ambil gambar** dari kamera atau galeri (`image_picker`).
- **Klasifikasi on-device** dengan LiteRT (`tflite_flutter`) — tanpa koneksi internet.
- **Halaman hasil** menampilkan gambar, nama makanan, dan confidence score.

## Struktur

```
lib/
├── main.dart
├── controller/home_controller.dart   Provider — state gambar terpilih + navigasi
├── service/food_classifier.dart      LiteRT interpreter + preprocess uint8 [1,224,224,3]
├── ui/
│   ├── home_page.dart                Tombol Kamera / Galeri / Analyze
│   └── result_page.dart              Inferensi + tampilan label + confidence
└── widget/classification_item.dart   Item hasil klasifikasi + shimmer

assets/models/
├── aiy_food_v1.tflite                Model (~24 MB, uint8 quantized)
└── aiy_food_V1_labels.txt            2024 label (index 0 = __background__)
```

## Menjalankan

```bash
flutter pub get
flutter run
```

## Build APK

```bash
flutter build apk --debug --android-skip-build-dependency-validation
```

APK: `build/app/outputs/flutter-apk/app-debug.apk`.

## Catatan model

Model AIY Food V1 menerima input **uint8** (bukan float) `[1,224,224,3]` dan mengeluarkan probabilitas **uint8** `[1,2024]`. Confidence dinormalisasi dengan pembagian 255. Index 0 (`__background__`) dilewati agar tidak mendominasi hasil.
