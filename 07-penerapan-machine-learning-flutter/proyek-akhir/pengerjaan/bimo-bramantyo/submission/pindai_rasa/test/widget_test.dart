// Uji unit ringkas untuk PindaiRasa: memastikan LabelScore mengubah skor byte
// ternormalisasi (0..1) menjadi persen yang benar. Sengaja bebas plugin supaya
// `flutter test` berjalan tanpa perangkat/emulator.

import 'package:flutter_test/flutter_test.dart';
import 'package:pindai_rasa/vision/label_score.dart';

void main() {
  test('LabelScore memformat keyakinan sebagai persen', () {
    const hit = LabelScore('NASI GORENG', 0.8123);

    expect(hit.percent, 81);
    expect(hit.percentLabel, '81.2%');
  });
}
