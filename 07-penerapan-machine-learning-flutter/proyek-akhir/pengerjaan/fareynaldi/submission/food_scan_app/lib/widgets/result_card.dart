import 'package:flutter/material.dart';

import '../models/scan_result.dart';

class ResultCard extends StatelessWidget {
  const ResultCard({super.key, required this.result});

  final ScanResult result;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: cs.outlineVariant),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Prediksi teratas',
            style: text.labelLarge?.copyWith(color: cs.onSurfaceVariant),
          ),
          const SizedBox(height: 6),
          Text(
            result.foodName,
            style: text.headlineSmall?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 16),
          _ConfidenceBar(value: result.score, color: cs.primary),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Confidence',
                style: text.bodyMedium?.copyWith(color: cs.onSurfaceVariant),
              ),
              Text(
                result.scorePercent,
                style: text.titleMedium?.copyWith(fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ConfidenceBar extends StatelessWidget {
  const _ConfidenceBar({required this.value, required this.color});

  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: LinearProgressIndicator(
        value: value.clamp(0.0, 1.0),
        minHeight: 10,
        color: color,
        backgroundColor: color.withValues(alpha: 0.15),
      ),
    );
  }
}
