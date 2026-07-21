import 'package:flutter/material.dart';

/// Warna benih PindaiRasa — merah marun hangat. Sengaja lain dari tema rekan
/// setim (ungu / hijau / oranye) demi identitas yang berbeda.
const Color kMaroonSeed = Color(0xFFC2185B);

/// Membangun tema Material 3 untuk seluruh aplikasi dari [kMaroonSeed].
ThemeData buildPindaiTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: kMaroonSeed,
    brightness: Brightness.light,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    appBarTheme: AppBarTheme(
      backgroundColor: scheme.primary,
      foregroundColor: scheme.onPrimary,
      centerTitle: true,
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    ),
  );
}
