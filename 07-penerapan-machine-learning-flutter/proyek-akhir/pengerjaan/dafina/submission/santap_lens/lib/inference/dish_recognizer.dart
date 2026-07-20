import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_litert/flutter_litert.dart';
import 'package:image/image.dart' as img_lib;

import 'dish_guess.dart';

/// Mesin inferensi SantapLens berbasis **LiteRT**.
///
/// Model **AIY Food V1** (Google) memakai kuantisasi uint8: nilai piksel RGB
/// `0..255` dimasukkan apa adanya (skala byte, bukan pecahan `0..1`). Bentuk
/// input `[1, 224, 224, 3]`, keluaran `[1, 2024]` berisi skor `0..255` yang
/// dibagi 255 untuk memperoleh keyakinan. Kelas pertama (`__background__`,
/// indeks 0) dilewati supaya tidak menutupi kelas makanan yang sesungguhnya.
class DishRecognizer {
  DishRecognizer({
    this.modelPath = 'assets/models/aiy_food_v1.tflite',
    this.labelPath = 'assets/models/labels.txt',
    this.inputSize = 224,
    this.topK = 3,
  });

  final String modelPath;
  final String labelPath;
  final int inputSize;
  final int topK;

  Interpreter? _interpreter;
  final List<String> _menu = <String>[];

  /// True ketika interpreter & daftar menu sudah tersedia di memori.
  bool get modelReady => _interpreter != null && _menu.isNotEmpty;

  /// Memuat interpreter LiteRT dan daftar label. Aman dipanggil berulang kali
  /// (hanya benar-benar memuat pada panggilan pertama).
  Future<void> prepare() async {
    _interpreter ??= await Interpreter.fromAsset(modelPath);
    if (_menu.isEmpty) {
      final rawLabels = await rootBundle.loadString(labelPath);
      for (final line in rawLabels.split('\n')) {
        final cleaned = line.trim();
        if (cleaned.isNotEmpty) _menu.add(cleaned);
      }
    }
  }

  /// Menjalankan inferensi pada [photo] lalu mengembalikan hingga [topK]
  /// tebakan teratas, terurut dari probabilitas tertinggi.
  Future<List<DishGuess>> identify(File photo) async {
    if (!modelReady) {
      throw StateError('DishRecognizer belum siap; jalankan prepare() dulu.');
    }

    final picture = await img_lib.decodeImageFile(photo.path);
    if (picture == null) {
      throw const FormatException('Foto gagal didekode oleh SantapLens.');
    }

    final tensorIn = _buildInputTensor(picture);
    final outputLength = _menu.length;
    final tensorOut = <List<int>>[List<int>.filled(outputLength, 0)];

    _interpreter!.run(tensorIn, tensorOut);

    return _rankGuesses(tensorOut.first);
  }

  /// Melepas interpreter & mengosongkan menu. Panggil saat halaman ditutup.
  void dispose() {
    _menu.clear();
    _interpreter?.close();
    _interpreter = null;
  }

  /// Menyusun tensor input `[1, size, size, 3]` sebagai list bersarang berisi
  /// nilai byte RGB (uint8) — dibangun langsung, bukan dari buffer datar yang
  /// di-`reshape`.
  List<List<List<List<int>>>> _buildInputTensor(img_lib.Image source) {
    final square = img_lib.copyResize(
      source,
      width: inputSize,
      height: inputSize,
      interpolation: img_lib.Interpolation.average,
    );

    final frame = List.generate(
      inputSize,
      (y) => List.generate(inputSize, (x) {
        final pixel = square.getPixel(x, y);
        return <int>[pixel.r.toInt(), pixel.g.toInt(), pixel.b.toInt()];
      }),
    );

    return <List<List<List<int>>>>[frame];
  }

  /// Mengubah skor mentah uint8 menjadi daftar [DishGuess] teratas, sambil
  /// melewati indeks 0 (`__background__`).
  List<DishGuess> _rankGuesses(List<int> rawScores) {
    final candidates = <MapEntry<int, int>>[];
    for (var i = 1; i < rawScores.length; i++) {
      candidates.add(MapEntry(i, rawScores[i]));
    }
    candidates.sort((a, b) => b.value.compareTo(a.value));

    final guesses = <DishGuess>[];
    for (final entry in candidates.take(topK)) {
      final label =
          entry.key < _menu.length ? _menu[entry.key] : 'Tidak dikenal';
      guesses.add(
        DishGuess(
          name: _displayName(label),
          probability: (entry.value / 255.0).clamp(0.0, 1.0),
        ),
      );
    }
    return guesses;
  }

  /// Mengubah label mentah menjadi teks tampilan: `mango_sticky_rice` menjadi
  /// `Mango sticky rice` (hanya huruf pertama kalimat yang dikapitalkan).
  String _displayName(String raw) {
    final spaced = raw.replaceAll('_', ' ').replaceAll(RegExp(r'\s+'), ' ').trim();
    if (spaced.isEmpty) return 'Tidak dikenal';
    return spaced[0].toUpperCase() + spaced.substring(1);
  }
}
