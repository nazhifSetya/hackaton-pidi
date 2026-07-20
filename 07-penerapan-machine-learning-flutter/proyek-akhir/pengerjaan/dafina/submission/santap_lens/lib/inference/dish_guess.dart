/// Satu kandidat hasil pengenalan makanan dari model.
///
/// [name] adalah nama makanan siap tampil, sedangkan [probability] berada di
/// rentang 0..1 (skor byte model yang sudah diskalakan).
class DishGuess {
  const DishGuess({required this.name, required this.probability});

  final String name;
  final double probability;

  /// Persentase dibulatkan, mis. `42`.
  int get percent => (probability * 100).round();

  /// Persentase satu angka desimal untuk ditampilkan, mis. `"42.3%"`.
  String get percentText => '${(probability * 100).toStringAsFixed(1)}%';
}
