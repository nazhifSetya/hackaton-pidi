/// Sepasang nama makanan dan skor keyakinannya untuk satu tebakan model.
///
/// [name] sudah dikapitalkan untuk tampil; [score] bernilai 0 hingga 1.
class LabelScore {
  const LabelScore(this.name, this.score);

  final String name;
  final double score;

  /// Keyakinan sebagai bilangan bulat persen, mis. 37.
  int get percent => (score * 100).round();

  /// Keyakinan siap tampil dengan satu desimal, mis. "37.4%".
  String get percentLabel => '${(score * 100).toStringAsFixed(1)}%';
}
