import '../inference/dish_guess.dart';

/// Fase siklus hidup proses pengenalan pada halaman prediksi.
enum RecognitionStatus { idle, working, success, failure }

/// Potret status pengenalan yang di-observe oleh UI. Objek bersifat *immutable*
/// dan dibuat lewat named constructor sesuai fase-nya.
class RecognitionState {
  const RecognitionState._(this.status, this.guesses, this.message);

  const RecognitionState.idle()
      : this._(RecognitionStatus.idle, const <DishGuess>[], null);

  const RecognitionState.working()
      : this._(RecognitionStatus.working, const <DishGuess>[], null);

  const RecognitionState.success(List<DishGuess> guesses)
      : this._(RecognitionStatus.success, guesses, null);

  const RecognitionState.failure(String message)
      : this._(RecognitionStatus.failure, const <DishGuess>[], message);

  final RecognitionStatus status;
  final List<DishGuess> guesses;
  final String? message;

  /// Tebakan teratas, atau null bila belum ada hasil.
  DishGuess? get best => guesses.isEmpty ? null : guesses.first;

  /// Tebakan selain yang teratas (untuk daftar "kemungkinan lain").
  List<DishGuess> get alternatives =>
      guesses.length > 1 ? guesses.sublist(1) : const <DishGuess>[];
}
