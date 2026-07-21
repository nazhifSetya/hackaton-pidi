import 'dart:io';

import 'package:flutter/material.dart';

/// Menampilkan foto terpilih di dalam bingkai bersudut membulat dengan tinggi
/// tetap. Dipakai di layar tangkap maupun layar hasil.
class PhotoCard extends StatelessWidget {
  const PhotoCard({super.key, required this.photo, this.height = 260});

  final File photo;
  final double height;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(18),
      child: Image.file(
        photo,
        height: height,
        width: double.infinity,
        fit: BoxFit.cover,
      ),
    );
  }
}
