import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_litert/flutter_litert.dart';
import 'package:image/image.dart' as pix;

import 'label_score.dart';

/// Otak pengenalan makanan PindaiRasa — memuat lalu menjalankan model
/// **AIY Food V1** (Google) melalui runtime **LiteRT**.
///
/// Sifat model (kuantisasi uint8) yang wajib dipatuhi:
/// - Input tensor `[1, 224, 224, 3]` berisi byte RGB mentah `0..255` — TIDAK
///   dinormalisasi menjadi pecahan.
/// - Output `[1, 2024]` berisi skor byte; dibagi 255 menjadi keyakinan `0..1`.
/// - Skor pada indeks 0 (`__background__`) dibuang lebih dulu; jika disertakan,
///   ia kerap mendominasi dan menyembunyikan tebakan makanan yang benar.
class MealVisionEngine {
  MealVisionEngine({
    this.assetModel = 'assets/models/aiy_food_v1.tflite',
    this.assetLabels = 'assets/models/labels.txt',
    this.side = 224,
    this.keep = 5,
  });

  final String assetModel;
  final String assetLabels;
  final int side;
  final int keep;

  Interpreter? _core;
  List<String> _vocab = const <String>[];

  /// Bernilai true begitu interpreter dan kosakata label siap dipakai.
  bool get armed => _core != null && _vocab.isNotEmpty;

  /// Memuat interpreter LiteRT + kosakata label satu kali saja. Boleh dipanggil
  /// lebih awal (mis. ketika layar dibuka) supaya prediksi pertama terasa
  /// instan; panggilan berikutnya menjadi no-op.
  Future<void> prime() async {
    _core ??= await Interpreter.fromAsset(assetModel);
    if (_vocab.isEmpty) {
      final blob = await rootBundle.loadString(assetLabels);
      _vocab = <String>[
        for (final line in blob.split('\n'))
          if (line.trim().isNotEmpty) line.trim(),
      ];
    }
  }

  /// Memindai [photo] lalu mengembalikan [keep] tebakan teratas dari yang
  /// paling yakin. Otomatis memanggil [prime] bila belum siap; melempar
  /// [FormatException] bila berkas foto tak terbaca.
  Future<List<LabelScore>> predict(File photo) async {
    if (!armed) {
      await prime();
    }

    final bitmap = await pix.decodeImageFile(photo.path);
    if (bitmap == null) {
      throw const FormatException('Berkas foto tidak dapat dibaca PindaiRasa.');
    }

    final input = _packInput(bitmap);
    final slots = _core!.getOutputTensor(0).shape.last;
    final output = <List<int>>[List<int>.filled(slots, 0)];

    _core!.run(input, output);

    return _shortlist(output.first);
  }

  /// Menutup interpreter dan melepas kosakata. Panggil saat tak dipakai lagi.
  void shutdown() {
    _core?.close();
    _core = null;
    _vocab = const <String>[];
  }

  /// Menata [source] menjadi tensor `[1, side, side, 3]`. Piksel diambil dari
  /// buffer datar `getBytes` (urutan RGB), lalu disusun ulang jadi list
  /// bersarang — beda jalur dari iterasi `getPixel` per titik.
  List<List<List<List<int>>>> _packInput(pix.Image source) {
    final scaled = pix.copyResize(
      source,
      width: side,
      height: side,
      interpolation: pix.Interpolation.cubic,
    );

    final flat = scaled.getBytes(order: pix.ChannelOrder.rgb);

    final grid = List.generate(
      side,
      (row) => List.generate(
        side,
        (col) {
          final at = (row * side + col) * 3;
          return <int>[flat[at], flat[at + 1], flat[at + 2]];
        },
        growable: false,
      ),
      growable: false,
    );

    return <List<List<List<int>>>>[grid];
  }

  /// Menyaring skor byte mentah menjadi [keep] [LabelScore] teratas, sambil
  /// melewati indeks latar (0) dan label di luar jangkauan kosakata.
  List<LabelScore> _shortlist(List<int> raw) {
    final ranked = <MapEntry<int, int>>[];
    for (var i = 1; i < raw.length; i++) {
      ranked.add(MapEntry(i, raw[i]));
    }
    ranked.sort((a, b) => b.value.compareTo(a.value));

    final picks = <LabelScore>[];
    for (final entry in ranked) {
      if (picks.length >= keep) break;
      if (entry.key >= _vocab.length) continue;
      final word = _capsLabel(_vocab[entry.key]);
      if (word.isEmpty) continue;
      picks.add(LabelScore(word, (entry.value / 255.0).clamp(0.0, 1.0)));
    }
    return picks;
  }

  /// `mango_sticky_rice` menjadi `MANGO STICKY RICE` — huruf kapital penuh
  /// sebagai gaya khas PindaiRasa.
  String _capsLabel(String raw) {
    return raw
        .replaceAll('_', ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim()
        .toUpperCase();
  }
}
