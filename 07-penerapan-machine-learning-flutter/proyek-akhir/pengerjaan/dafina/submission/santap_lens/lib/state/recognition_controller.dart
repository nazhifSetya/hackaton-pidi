import 'dart:io';

import 'package:flutter/foundation.dart';

import '../inference/dish_recognizer.dart';
import 'recognition_state.dart';

/// Menjembatani [DishRecognizer] dengan UI lewat [ValueNotifier].
///
/// Sengaja memakai pola `ValueNotifier` + `ValueListenableBuilder` — bukan
/// `setState` polos maupun paket `provider` — supaya arsitekturnya berbeda dari
/// proyek anggota tim lain.
class RecognitionController {
  RecognitionController({DishRecognizer? engine})
      : _engine = engine ?? DishRecognizer();

  final DishRecognizer _engine;

  /// Sumber kebenaran status yang di-observe oleh halaman prediksi.
  final ValueNotifier<RecognitionState> state =
      ValueNotifier<RecognitionState>(const RecognitionState.idle());

  /// Memuat model (bila perlu) lalu menjalankan inferensi pada [photo].
  Future<void> classify(File photo) async {
    state.value = const RecognitionState.working();
    try {
      await _engine.prepare();
      final guesses = await _engine.identify(photo);
      state.value = RecognitionState.success(guesses);
    } catch (error) {
      state.value = RecognitionState.failure(error.toString());
    }
  }

  /// Melepas notifier & resource model.
  void dispose() {
    _engine.dispose();
    state.dispose();
  }
}
