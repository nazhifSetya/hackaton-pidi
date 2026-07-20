# SantapLens

Aplikasi Flutter yang menebak jenis makanan dari sebuah foto. Cukup ambil foto
dari kamera atau pilih dari galeri, lalu SantapLens menampilkan nama makanan
beserta tingkat keyakinannya.

Submission proyek akhir kelas **Belajar Penerapan Machine Learning untuk
Flutter** (Dicoding) — target nilai **Bintang 3 (Basic)**.

## Cara kerja

Gambar yang dipilih di-decode dan di-resize ke 224×224, lalu diumpankan ke
model klasifikasi **AIY Food V1** (Google) yang berjalan **on-device** melalui
runtime **LiteRT** (`flutter_litert`). Model mengembalikan skor untuk 2.023
jenis makanan; SantapLens menampilkan tiga tebakan teratas.

## Kriteria yang dipenuhi (semua Basic)

| Kriteria | Implementasi |
|---|---|
| Pengambilan gambar | `image_picker` (kamera & galeri); foto tampil di halaman. |
| Machine learning | Model AIY Food V1 dijalankan via LiteRT; inferensi setelah gambar diambil. |
| Halaman prediksi | Foto + nama makanan + keyakinan (%) pada arc gauge. |

## Menjalankan

```bash
flutter pub get
flutter run
```

> Model `assets/models/aiy_food_v1.tflite` (± 21 MB) diperoleh dari
> [Kaggle — AIY Food V1](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-food-v1).

## Struktur `lib/`

```
lib/
├── main.dart              Entry + MaterialApp (tema oranye)
├── theme.dart             Definisi ThemeData
├── inference/             DishRecognizer (LiteRT) + DishGuess
├── state/                 RecognitionController (ValueNotifier) + RecognitionState
├── pages/                 CapturePage + PredictionPage
└── components/            PhotoFrame + GuessMeter (arc gauge)
```
