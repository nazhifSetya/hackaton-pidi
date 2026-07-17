import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'detail_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final ImagePicker _picker = ImagePicker();
  File? _pickedPhoto;
  bool _loading = false;

  Future<void> _grab(ImageSource src) async {
    setState(() => _loading = true);
    try {
      final xf = await _picker.pickImage(source: src, imageQuality: 88);
      if (!mounted) return;
      if (xf != null) {
        setState(() => _pickedPhoto = File(xf.path));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal mengambil gambar: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _openDetail() {
    final file = _pickedPhoto;
    if (file == null) return;
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => DetailScreen(photo: file)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Food Scan App')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
          child: Column(
            children: [
              _PreviewCard(file: _pickedPhoto, tint: cs.primaryContainer),
              const SizedBox(height: 20),
              _SourceButtons(
                busy: _loading,
                onCamera: () => _grab(ImageSource.camera),
                onGallery: () => _grab(ImageSource.gallery),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: FilledButton.icon(
                  onPressed: _pickedPhoto == null ? null : _openDetail,
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Identifikasi Makanan'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PreviewCard extends StatelessWidget {
  const _PreviewCard({required this.file, required this.tint});

  final File? file;
  final Color tint;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: tint.withValues(alpha: 0.35),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: tint, width: 1.2),
        ),
        clipBehavior: Clip.antiAlias,
        child: file == null
            ? const _EmptyPreview()
            : Image.file(file!, fit: BoxFit.cover),
      ),
    );
  }
}

class _EmptyPreview extends StatelessWidget {
  const _EmptyPreview();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.photo_camera_outlined, size: 96),
          SizedBox(height: 12),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 24),
            child: Text(
              'Foto makanan belum dipilih.\nAmbil dari kamera atau galeri.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }
}

class _SourceButtons extends StatelessWidget {
  const _SourceButtons({
    required this.busy,
    required this.onCamera,
    required this.onGallery,
  });

  final bool busy;
  final VoidCallback onCamera;
  final VoidCallback onGallery;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: busy ? null : onCamera,
            icon: const Icon(Icons.photo_camera),
            label: const Text('Kamera'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: busy ? null : onGallery,
            icon: const Icon(Icons.image_outlined),
            label: const Text('Galeri'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ),
      ],
    );
  }
}
