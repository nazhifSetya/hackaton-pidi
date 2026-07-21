import 'package:flutter/material.dart';

import 'palette.dart';
import 'views/snap_view.dart';

void main() {
  runApp(const PindaiRasaApp());
}

/// Akar aplikasi PindaiRasa — pindai foto makanan, tebak namanya.
class PindaiRasaApp extends StatelessWidget {
  const PindaiRasaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PindaiRasa',
      debugShowCheckedModeBanner: false,
      theme: buildPindaiTheme(),
      home: const SnapView(),
    );
  }
}
