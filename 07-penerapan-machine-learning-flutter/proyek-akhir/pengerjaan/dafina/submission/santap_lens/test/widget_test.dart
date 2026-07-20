// Smoke test dasar untuk SantapLens.
//
// Memastikan halaman awal (CapturePage) ter-render dengan judul & tombol utama.

import 'package:flutter_test/flutter_test.dart';

import 'package:santap_lens/main.dart';

void main() {
  testWidgets('Halaman awal menampilkan judul & tombol utama',
      (WidgetTester tester) async {
    await tester.pumpWidget(const SantapLensApp());

    expect(find.text('SantapLens'), findsOneWidget);
    expect(find.text('Kenali Makanan'), findsOneWidget);
  });
}
