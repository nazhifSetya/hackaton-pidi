import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../components/photo_frame.dart';
import 'prediction_page.dart';

/// Halaman utama: pengguna mengambil foto makanan (kamera / galeri) lalu
/// melanjutkan ke halaman prediksi. Memenuhi Kriteria 1 (pengambilan gambar
/// via `image_picker` + gambar tampil di halaman).
class CapturePage extends StatefulWidget {
  const CapturePage({super.key});

  @override
  State<CapturePage> createState() => _CapturePageState();
}

class _CapturePageState extends State<CapturePage> {
  final ImagePicker _imagePicker = ImagePicker();
  File? _snapshot;
  bool _picking = false;

  Future<void> _acquire(ImageSource source) async {
    if (_picking) return;
    setState(() => _picking = true);
    try {
      final captured = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1600,
        imageQuality: 90,
      );
      if (!mounted) return;
      if (captured != null) {
        setState(() => _snapshot = File(captured.path));
      }
    } on Exception catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Foto tidak jadi diambil. Coba lagi ya.')),
      );
    } finally {
      if (mounted) setState(() => _picking = false);
    }
  }

  void _continueToPrediction() {
    final photo = _snapshot;
    if (photo == null) return;
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => PredictionPage(photo: photo)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SantapLens'),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: Icon(Icons.eco_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Foto makananmu, biar SantapLens yang menebak namanya.',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 16),
              Expanded(
                child: Center(child: PhotoFrame(file: _snapshot)),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed:
                          _picking ? null : () => _acquire(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt_outlined),
                      label: const Text('Kamera'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _picking
                          ? null
                          : () => _acquire(ImageSource.gallery),
                      icon: const Icon(Icons.collections_outlined),
                      label: const Text('Galeri'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              FilledButton.icon(
                onPressed: _snapshot == null ? null : _continueToPrediction,
                icon: const Icon(Icons.travel_explore),
                label: const Text('Kenali Makanan'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
