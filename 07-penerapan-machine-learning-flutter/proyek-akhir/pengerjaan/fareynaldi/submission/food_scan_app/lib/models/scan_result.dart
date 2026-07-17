class ScanResult {
  final String foodName;
  final double score;

  const ScanResult({required this.foodName, required this.score});

  String get scorePercent => '${(score * 100).toStringAsFixed(1)}%';
}
