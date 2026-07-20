import 'package:flutter/material.dart';

/// Warna benih (seed) khas SantapLens: oranye hangat bernuansa rempah/makanan.
/// Sengaja berbeda dari tema proyek anggota lain (ungu & hijau).
const Color kSantapSeed = Color(0xFFF57C00);

/// Membangun [ThemeData] Material 3 untuk seluruh aplikasi.
ThemeData santapLensTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: kSantapSeed,
    brightness: Brightness.light,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: scheme.surface,
    appBarTheme: AppBarTheme(
      centerTitle: false,
      elevation: 0,
      backgroundColor: scheme.surface,
      foregroundColor: scheme.onSurface,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        minimumSize: const Size.fromHeight(52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
      ),
    ),
  );
}
