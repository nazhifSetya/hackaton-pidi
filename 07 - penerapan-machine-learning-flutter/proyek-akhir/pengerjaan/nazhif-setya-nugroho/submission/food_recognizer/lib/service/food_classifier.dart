import 'dart:io';

import 'package:flutter/services.dart';
import 'package:image/image.dart' as img_lib;
import 'package:tflite_flutter/tflite_flutter.dart';

class FoodPrediction {
  final String label;
  final double confidence;

  FoodPrediction(this.label, this.confidence);
}

class FoodClassifier {
  static const String _modelPath = 'assets/models/aiy_food_v1.tflite';
  static const String _labelsPath = 'assets/models/aiy_food_V1_labels.txt';
  static const int _inputSize = 224;

  Interpreter? _interpreter;
  List<String>? _labels;

  Future<void> load() async {
    _interpreter = await Interpreter.fromAsset(_modelPath);
    final labelsRaw = await rootBundle.loadString(_labelsPath);
    _labels = labelsRaw
        .split('\n')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
  }

  bool get isLoaded => _interpreter != null && _labels != null;

  Future<FoodPrediction> classify(File imageFile) async {
    if (!isLoaded) {
      throw StateError('Model belum dimuat. Panggil load() dulu.');
    }

    final bytes = await imageFile.readAsBytes();
    final decoded = img_lib.decodeImage(bytes);
    if (decoded == null) {
      throw StateError('Gambar tidak bisa dibaca.');
    }

    final resized = img_lib.copyResize(
      decoded,
      width: _inputSize,
      height: _inputSize,
    );

    // Model AIY food V1: input uint8 [1,224,224,3], output uint8 [1,2024].
    final input = Uint8List(1 * _inputSize * _inputSize * 3);
    var idx = 0;
    for (var y = 0; y < _inputSize; y++) {
      for (var x = 0; x < _inputSize; x++) {
        final pixel = resized.getPixel(x, y);
        input[idx++] = pixel.r.toInt();
        input[idx++] = pixel.g.toInt();
        input[idx++] = pixel.b.toInt();
      }
    }

    final inputTensor = input.reshape([1, _inputSize, _inputSize, 3]);
    final output = List.filled(1 * _labels!.length, 0)
        .reshape([1, _labels!.length]);

    _interpreter!.run(inputTensor, output);

    final probs = (output[0] as List).cast<num>();
    // Skip index 0 (__background__) supaya tidak dominan.
    var bestIdx = 1;
    var bestVal = probs[1];
    for (var i = 2; i < probs.length; i++) {
      if (probs[i] > bestVal) {
        bestVal = probs[i];
        bestIdx = i;
      }
    }

    // Output uint8 quantized → confidence 0..255 → normalize ke 0..1.
    final confidence = bestVal.toDouble() / 255.0;
    return FoodPrediction(_labels![bestIdx], confidence);
  }

  void dispose() {
    _interpreter?.close();
    _interpreter = null;
    _labels = null;
  }
}
