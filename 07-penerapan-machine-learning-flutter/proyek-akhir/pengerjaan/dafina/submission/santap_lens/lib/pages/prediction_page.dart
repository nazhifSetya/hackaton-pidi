import 'dart:io';

import 'package:flutter/material.dart';

import '../components/guess_meter.dart';
import '../components/photo_frame.dart';
import '../inference/dish_guess.dart';
import '../state/recognition_controller.dart';
import '../state/recognition_state.dart';

/// Halaman prediksi: menampilkan foto, menjalankan inferensi LiteRT, lalu
/// menyajikan nama makanan + tingkat keyakinan (Kriteria 2 & 3).
class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key, required this.photo});

  final File photo;

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final RecognitionController _controller = RecognitionController();

  @override
  void initState() {
    super.initState();
    _controller.classify(widget.photo);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hasil Pengenalan')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
          children: [
            PhotoFrame(file: widget.photo, aspectRatio: 4 / 3),
            const SizedBox(height: 24),
            ValueListenableBuilder<RecognitionState>(
              valueListenable: _controller.state,
              builder: (context, state, _) => _ResultView(
                state: state,
                onRetry: () => _controller.classify(widget.photo),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ResultView extends StatelessWidget {
  const _ResultView({required this.state, required this.onRetry});

  final RecognitionState state;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    switch (state.status) {
      case RecognitionStatus.idle:
      case RecognitionStatus.working:
        return const _BusyView();
      case RecognitionStatus.failure:
        return _FailureView(
          message: state.message ?? 'Terjadi kesalahan tak terduga.',
          onRetry: onRetry,
        );
      case RecognitionStatus.success:
        final best = state.best;
        if (best == null) {
          return _FailureView(
            message: 'Model tidak menghasilkan tebakan.',
            onRetry: onRetry,
          );
        }
        return _SuccessView(best: best, alternatives: state.alternatives);
    }
  }
}

/// Indikator "sedang memproses" berbentuk baris (spinner + teks) dalam kartu
/// lembut — sengaja bukan kolom spinner-di-tengah.
class _BusyView extends StatelessWidget {
  const _BusyView();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22),
      decoration: BoxDecoration(
        color: scheme.primaryContainer.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 26,
            height: 26,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              color: scheme.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              'SantapLens sedang menebak makananmu…',
              style: TextStyle(color: scheme.onPrimaryContainer),
            ),
          ),
        ],
      ),
    );
  }
}

class _SuccessView extends StatelessWidget {
  const _SuccessView({required this.best, required this.alternatives});

  final DishGuess best;
  final List<DishGuess> alternatives;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(child: GuessMeter(value: best.probability)),
        const SizedBox(height: 20),
        Text(
          'Kemungkinan besar ini:',
          textAlign: TextAlign.center,
          style: text.labelLarge?.copyWith(color: scheme.onSurfaceVariant),
        ),
        const SizedBox(height: 4),
        Text(
          best.name,
          textAlign: TextAlign.center,
          style: text.headlineSmall?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 4),
        Text(
          'Keyakinan ${best.percentText}',
          textAlign: TextAlign.center,
          style: text.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
        ),
        if (alternatives.isNotEmpty) ...[
          const SizedBox(height: 28),
          Text('Kemungkinan lain', style: text.titleSmall),
          const SizedBox(height: 8),
          for (final guess in alternatives) _AlternativeTile(guess: guess),
        ],
        const SizedBox(height: 20),
        Text(
          'Model AIY Food V1 mengenali 2.023 jenis makanan dari seluruh dunia. '
          'Skor yang tampak kecil itu wajar karena jumlah kelasnya sangat banyak.',
          style: text.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
        ),
      ],
    );
  }
}

class _AlternativeTile extends StatelessWidget {
  const _AlternativeTile({required this.guess});

  final DishGuess guess;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          Icon(Icons.circle, size: 8, color: scheme.primary),
          const SizedBox(width: 10),
          Expanded(child: Text(guess.name)),
          Text(
            guess.percentText,
            style: TextStyle(color: scheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}

/// Kartu kegagalan bergaya banner: header (ikon + judul sebaris), pesan, lalu
/// tombol ulang di kanan — sengaja beda dari blok error terpusat.
class _FailureView extends StatelessWidget {
  const _FailureView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return Card(
      elevation: 0,
      color: scheme.surfaceContainerHighest,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(color: scheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: scheme.error),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Waduh, gagal mengenali',
                    style: text.titleMedium?.copyWith(color: scheme.error),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: text.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: OutlinedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Coba ulang'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
