import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../parts/photo_card.dart';
import '../vision/meal_vision_engine.dart';
import 'insight_view.dart';

/// Layar utama (Kriteria 1): pengguna menjepret atau memilih foto makanan,
/// lalu menekan "Kenali Makanan" untuk pindah ke layar hasil.
///
/// Foto terpilih disiarkan lewat [StreamController] dan dirender ulang oleh
/// [StreamBuilder] — bukan lewat `setState`.
class SnapView extends StatefulWidget {
  const SnapView({super.key});

  @override
  State<SnapView> createState() => _SnapViewState();
}

class _SnapViewState extends State<SnapView> {
  final ImagePicker _picker = ImagePicker();
  final StreamController<File?> _shot = StreamController<File?>.broadcast();
  final MealVisionEngine _engine = MealVisionEngine();

  @override
  void initState() {
    super.initState();
    // Muat model lebih awal supaya prediksi pertama tak menunggu lama.
    unawaited(_engine.prime());
  }

  @override
  void dispose() {
    _shot.close();
    _engine.shutdown();
    super.dispose();
  }

  Future<void> _grab(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(source: source, imageQuality: 92);
      if (picked != null) _shot.add(File(picked.path));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sumber gambar tidak bisa dibuka.')),
      );
    }
  }

  void _openInsight(File photo) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => InsightView(photo: photo, engine: _engine),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    return Scaffold(
      appBar: AppBar(title: const Text('PindaiRasa')),
      body: SafeArea(
        child: StreamBuilder<File?>(
          stream: _shot.stream,
          initialData: null,
          builder: (context, snap) {
            final photo = snap.data;
            return ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Text('Pindai makanan, kenali namanya', style: text.titleLarge),
                const SizedBox(height: 6),
                Text(
                  'Ambil foto dari kamera atau pilih dari galeri, lalu biarkan '
                  'model AIY Food V1 menebaknya.',
                  style: text.bodyMedium,
                ),
                const SizedBox(height: 20),
                if (photo == null)
                  const _EmptySlot()
                else
                  PhotoCard(photo: photo),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _grab(ImageSource.camera),
                        icon: const Icon(Icons.photo_camera_outlined),
                        label: const Text('Kamera'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _grab(ImageSource.gallery),
                        icon: const Icon(Icons.collections_outlined),
                        label: const Text('Galeri'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: photo == null ? null : () => _openInsight(photo),
                  icon: const Icon(Icons.travel_explore),
                  label: const Text('Kenali Makanan'),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

/// Bingkai kosong ketika belum ada foto terpilih.
class _EmptySlot extends StatelessWidget {
  const _EmptySlot();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      height: 260,
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: scheme.outlineVariant),
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.restaurant_menu, size: 56, color: scheme.primary),
            const SizedBox(height: 8),
            const Text('Belum ada foto'),
          ],
        ),
      ),
    );
  }
}
