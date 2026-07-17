import 'package:flutter/material.dart';

import 'screens/scanner_screen.dart';

void main() {
  runApp(const FoodScanApp());
}

class FoodScanApp extends StatelessWidget {
  const FoodScanApp({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF2E7D32),
      brightness: Brightness.light,
    );

    return MaterialApp(
      title: 'Food Scan App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: scheme,
        useMaterial3: true,
        appBarTheme: AppBarTheme(
          backgroundColor: scheme.primary,
          foregroundColor: scheme.onPrimary,
          centerTitle: true,
        ),
      ),
      home: const ScannerScreen(),
    );
  }
}
