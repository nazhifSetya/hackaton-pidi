# Food Scan App

Proyek akhir Dicoding **Belajar Penerapan Machine Learning untuk Flutter** — oleh **Fareynaldi**.

Aplikasi Flutter yang mengklasifikasikan gambar makanan menggunakan model TFLite [AIY Vision Classifier Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1).

## Fitur (Target: Basic pada 3 kriteria)

1. **Pengambilan gambar** dari kamera atau galeri (`image_picker`).
2. **Inferensi ML** on-device menggunakan LiteRT (`tflite_flutter`).
3. **Halaman hasil** menampilkan foto, nama makanan, dan persentase confidence.

## Struktur

```
lib/
├── main.dart                       Entry + tema Material 3
├── ml/tflite_food_detector.dart    Wrapper LiteRT (warmUp / analyze / release)
├── models/scan_result.dart         Data class
├── screens/scanner_screen.dart     Halaman utama (pick image)
├── screens/detail_screen.dart      Halaman hasil (inferensi)
└── widgets/result_card.dart        Kartu hasil dengan confidence bar
```

## Menjalankan

```bash
flutter pub get
flutter run
```

Butuh file `assets/models/aiy_food_v1.tflite` (~24 MB). Download dari Kaggle, taruh di path tersebut. Lihat `panduan/README.md` di folder induk untuk langkah lengkap.
