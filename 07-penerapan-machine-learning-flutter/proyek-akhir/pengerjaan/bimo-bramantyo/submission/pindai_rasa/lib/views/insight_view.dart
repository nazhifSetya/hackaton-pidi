import 'dart:io';

import 'package:flutter/material.dart';

import '../flow/scan_flow.dart';
import '../flow/scan_state.dart';
import '../parts/photo_card.dart';
import '../parts/score_bars.dart';
import '../vision/meal_vision_engine.dart';

/// Layar hasil (Kriteria 3): menampilkan foto yang dipindai, nama makanan
/// teratas, keyakinannya, serta rincian lima tebakan teratas.
///
/// Inferensi (Kriteria 2) dijalankan lewat [ScanFlow] dan statusnya diikuti
/// dengan [StreamBuilder].
class InsightView extends StatefulWidget {
  const InsightView({super.key, required this.photo, required this.engine});

  final File photo;
  final MealVisionEngine engine;

  @override
  State<InsightView> createState() => _InsightViewState();
}

class _InsightViewState extends State<InsightView> {
  late final ScanFlow _flow;

  @override
  void initState() {
    super.initState();
    _flow = ScanFlow(widget.engine);
    // Mulai pemindaian segera setelah layar dibuka.
    _flow.run(widget.photo);
  }

  @override
  void dispose() {
    _flow.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hasil Pindai')),
      body: SafeArea(
        child: StreamBuilder<ScanState>(
          stream: _flow.updates,
          initialData: _flow.last,
          builder: (context, snap) {
            final state = snap.data ?? ScanState.scanning();
            return ListView(
              padding: const EdgeInsets.all(20),
              children: [
                PhotoCard(photo: widget.photo),
                const SizedBox(height: 20),
                _statusBody(context, state),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _statusBody(BuildContext context, ScanState state) {
    switch (state.stage) {
      case ScanStage.scanning:
        return const Padding(
          padding: EdgeInsets.symmetric(vertical: 40),
          child: Center(
            child: Column(
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 12),
                Text('Memindai makanan…'),
              ],
            ),
          ),
        );
      case ScanStage.failed:
        return _Notice(text: state.note ?? 'Terjadi kesalahan.');
      case ScanStage.ready:
        final text = Theme.of(context).textTheme;
        final scheme = Theme.of(context).colorScheme;
        final top = state.top!;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Kemungkinan besar', style: text.labelLarge),
            const SizedBox(height: 4),
            Text(
              top.name,
              style: text.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: scheme.primary,
              ),
            ),
            const SizedBox(height: 4),
            Text('Keyakinan ${top.percentLabel}', style: text.titleMedium),
            const Divider(height: 32),
            Text('Lima tebakan teratas', style: text.titleSmall),
            const SizedBox(height: 12),
            ScoreBars(scores: state.results),
          ],
        );
    }
  }
}

/// Kartu pemberitahuan sederhana untuk kondisi gagal.
class _Notice extends StatelessWidget {
  const _Notice({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: scheme.error),
            const SizedBox(width: 12),
            Expanded(child: Text(text)),
          ],
        ),
      ),
    );
  }
}
