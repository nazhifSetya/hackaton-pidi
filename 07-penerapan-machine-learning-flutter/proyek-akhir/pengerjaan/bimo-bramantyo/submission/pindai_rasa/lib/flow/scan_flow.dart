import 'dart:async';
import 'dart:io';

import '../vision/meal_vision_engine.dart';
import 'scan_state.dart';

/// Menjembatani [MealVisionEngine] dengan UI lewat sebuah [Stream].
///
/// Alih-alih `setState` atau `ChangeNotifier`, PindaiRasa menyiarkan tiap
/// perubahan status melalui [StreamController]; layar cukup mendengarkannya
/// dengan `StreamBuilder`. Controller bertipe single-subscription sehingga
/// kejadian yang dipancarkan sebelum pendengar melekat tetap tersampaikan
/// berurutan.
class ScanFlow {
  ScanFlow(this._engine);

  final MealVisionEngine _engine;
  final StreamController<ScanState> _channel = StreamController<ScanState>();

  ScanState _last = ScanState.scanning();

  /// Aliran status untuk `StreamBuilder`.
  Stream<ScanState> get updates => _channel.stream;

  /// Status terakhir — dipakai sebagai `initialData` agar frame pertama sudah
  /// menggambarkan kondisi kini.
  ScanState get last => _last;

  /// Menjalankan satu pemindaian penuh atas [photo].
  Future<void> run(File photo) async {
    _emit(ScanState.scanning());
    try {
      final hits = await _engine.predict(photo);
      if (hits.isEmpty) {
        _emit(ScanState.failed('Tak ada makanan yang cukup meyakinkan.'));
      } else {
        _emit(ScanState.ready(hits));
      }
    } catch (err) {
      _emit(ScanState.failed('Gagal memindai: $err'));
    }
  }

  void _emit(ScanState state) {
    _last = state;
    if (!_channel.isClosed) _channel.add(state);
  }

  /// Menutup aliran. Panggil dari `dispose()` layar.
  Future<void> close() => _channel.close();
}
