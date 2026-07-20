import 'package:flutter/material.dart';

import 'pages/capture_page.dart';
import 'theme.dart';

void main() {
  runApp(const SantapLensApp());
}

/// Root aplikasi **SantapLens**.
///
/// SantapLens mengenali jenis makanan dari sebuah foto menggunakan model
/// klasifikasi AIY Food V1 (Google) yang dijalankan langsung di perangkat
/// (on-device) lewat LiteRT.
class SantapLensApp extends StatelessWidget {
  const SantapLensApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SantapLens',
      debugShowCheckedModeBanner: false,
      theme: santapLensTheme(),
      home: const CapturePage(),
    );
  }
}
