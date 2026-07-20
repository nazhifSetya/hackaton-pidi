import 'dart:io';

import 'package:flutter/material.dart';

/// Bingkai foto membulat: menampilkan placeholder bila [file] null, atau
/// gambar yang dipilih pengguna bila tersedia.
class PhotoFrame extends StatelessWidget {
  const PhotoFrame({super.key, required this.file, this.aspectRatio = 1});

  final File? file;
  final double aspectRatio;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return AspectRatio(
      aspectRatio: aspectRatio,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: scheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: scheme.outlineVariant, width: 1.5),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: file == null
              ? _Placeholder(scheme: scheme)
              : Image.file(file!, fit: BoxFit.cover),
        ),
      ),
    );
  }
}

class _Placeholder extends StatelessWidget {
  const _Placeholder({required this.scheme});

  final ColorScheme scheme;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.restaurant_menu, size: 72, color: scheme.primary),
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Text(
              'Belum ada foto. Jepret atau pilih makanan untuk dikenali.',
              textAlign: TextAlign.center,
              style: TextStyle(color: scheme.onSurfaceVariant),
            ),
          ),
        ],
      ),
    );
  }
}
