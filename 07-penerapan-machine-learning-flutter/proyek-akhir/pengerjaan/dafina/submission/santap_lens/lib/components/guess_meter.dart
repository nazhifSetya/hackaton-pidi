import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Pengukur melingkar (arc gauge) yang menampilkan tingkat keyakinan model
/// dalam persen. Dipakai di halaman prediksi sebagai identitas visual
/// SantapLens — sengaja berbeda dari progress bar linear anggota lain.
class GuessMeter extends StatelessWidget {
  const GuessMeter({super.key, required this.value, this.diameter = 150});

  /// Nilai keyakinan 0..1.
  final double value;
  final double diameter;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final theme = Theme.of(context);
    final clamped = value.clamp(0.0, 1.0);

    return SizedBox(
      width: diameter,
      height: diameter,
      child: CustomPaint(
        painter: _ArcPainter(
          value: clamped,
          track: scheme.primary.withValues(alpha: 0.15),
          progress: scheme.primary,
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '${(clamped * 100).round()}%',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: scheme.primary,
                ),
              ),
              Text(
                'keyakinan',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: scheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ArcPainter extends CustomPainter {
  _ArcPainter({
    required this.value,
    required this.track,
    required this.progress,
  });

  final double value;
  final Color track;
  final Color progress;

  @override
  void paint(Canvas canvas, Size size) {
    const stroke = 12.0;
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.shortestSide - stroke) / 2;
    final arcRect = Rect.fromCircle(center: center, radius: radius);

    final trackPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = stroke
      ..color = track;

    final progressPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeWidth = stroke
      ..color = progress;

    // Mulai dari puncak (−90°), memutar searah jarum jam.
    const start = -math.pi / 2;
    const full = 2 * math.pi;
    canvas.drawArc(arcRect, start, full, false, trackPaint);
    canvas.drawArc(arcRect, start, full * value, false, progressPaint);
  }

  @override
  bool shouldRepaint(_ArcPainter old) =>
      old.value != value || old.progress != progress || old.track != track;
}
