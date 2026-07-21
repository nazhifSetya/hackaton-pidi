import '../vision/label_score.dart';

/// Tahapan hidup satu sesi pemindaian.
enum ScanStage { scanning, ready, failed }

/// Potret status pemindaian yang dialirkan lewat [Stream] ke UI.
///
/// Immutable: tiap perubahan diwakili instance baru, bukan mutasi in-place.
class ScanState {
  const ScanState._(this.stage, this.results, this.note);

  /// Model sedang bekerja.
  factory ScanState.scanning() =>
      const ScanState._(ScanStage.scanning, <LabelScore>[], null);

  /// Pemindaian selesai membawa daftar tebakan.
  factory ScanState.ready(List<LabelScore> results) =>
      ScanState._(ScanStage.ready, results, null);

  /// Pemindaian gagal disertai [note] alasan.
  factory ScanState.failed(String note) =>
      ScanState._(ScanStage.failed, const <LabelScore>[], note);

  final ScanStage stage;
  final List<LabelScore> results;
  final String? note;

  /// Tebakan terbaik (indeks 0) bila tersedia.
  LabelScore? get top => results.isEmpty ? null : results.first;
}
