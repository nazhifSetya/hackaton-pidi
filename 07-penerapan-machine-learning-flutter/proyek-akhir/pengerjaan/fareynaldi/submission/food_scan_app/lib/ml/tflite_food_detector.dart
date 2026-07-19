import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/services.dart' show rootBundle;
import 'package:image/image.dart' as im;
import 'package:flutter_litert/flutter_litert.dart';

import '../models/scan_result.dart';

/// Wrapper untuk model AIY Food V1 (LiteRT).
///
/// Model spec (dari Kaggle):
/// - Input : uint8 [1, 224, 224, 3]  → tanpa normalisasi float
/// - Output: uint8 [1, 2024]         → probabilitas terkuantisasi (0..255)
/// - Label index 0 = "__background__" → dilewati agar tidak mendominasi
class TfliteFoodDetector {
  TfliteFoodDetector({
    this.modelAsset = 'assets/models/aiy_food_v1.tflite',
    this.labelAsset = 'assets/models/labels.txt',
    this.imageSide = 224,
  });

  final String modelAsset;
  final String labelAsset;
  final int imageSide;

  Interpreter? _tflite;
  List<String> _labels = const [];

  bool get ready => _tflite != null && _labels.isNotEmpty;

  Future<void> warmUp() async {
    _tflite ??= await Interpreter.fromAsset(modelAsset);
    if (_labels.isEmpty) {
      final raw = await rootBundle.loadString(labelAsset);
      _labels = raw
          .split(RegExp(r'\r?\n'))
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .toList(growable: false);
    }
  }

  Future<ScanResult> analyze(File picture) async {
    if (!ready) {
      throw StateError('Detector belum siap. Panggil warmUp() lebih dulu.');
    }

    final decoded = await im.decodeImageFile(picture.path);
    if (decoded == null) {
      throw const FormatException('Gambar tidak dapat dibaca.');
    }

    final buffer = _toInputBuffer(decoded);
    final reshapedInput = buffer.reshape([1, imageSide, imageSide, 3]);
    final rawOutput = List<int>.filled(_labels.length, 0)
        .reshape([1, _labels.length]);

    _tflite!.run(reshapedInput, rawOutput);

    final scores = (rawOutput[0] as List).cast<num>();
    final bestIndex = _argmaxSkippingBackground(scores);
    final confidence = scores[bestIndex].toDouble() / 255.0;

    return ScanResult(
      foodName: _prettify(_labels[bestIndex]),
      score: confidence.clamp(0.0, 1.0),
    );
  }

  Uint8List _toInputBuffer(im.Image source) {
    final resized = im.copyResize(
      source,
      width: imageSide,
      height: imageSide,
      interpolation: im.Interpolation.linear,
    );

    final pixels = Uint8List(imageSide * imageSide * 3);
    var cursor = 0;
    for (var row = 0; row < imageSide; row++) {
      for (var col = 0; col < imageSide; col++) {
        final px = resized.getPixel(col, row);
        pixels[cursor++] = px.r.toInt();
        pixels[cursor++] = px.g.toInt();
        pixels[cursor++] = px.b.toInt();
      }
    }
    return pixels;
  }

  int _argmaxSkippingBackground(List<num> probs) {
    // Index 0 = __background__ → dilewati agar tidak selalu menang di gambar
    // yang bukan makanan (default confident dari model).
    var winner = 1;
    var winnerScore = probs[1];
    for (var i = 2; i < probs.length; i++) {
      if (probs[i] > winnerScore) {
        winnerScore = probs[i];
        winner = i;
      }
    }
    return winner;
  }

  String _prettify(String rawLabel) {
    final parts = rawLabel.replaceAll('_', ' ').split(' ');
    return parts
        .where((p) => p.isNotEmpty)
        .map((p) => p[0].toUpperCase() + p.substring(1))
        .join(' ');
  }

  void release() {
    _tflite?.close();
    _tflite = null;
    _labels = const [];
  }
}
