import 'package:flutter/material.dart';

import '../vision/label_score.dart';

/// Diagram batang horizontal untuk beberapa tebakan teratas. Tiap baris memuat
/// nama makanan, sebuah batang selebar keyakinannya, dan angka persen.
///
/// Sengaja disusun dari [FractionallySizedBox] di atas [Container] — bukan
/// `LinearProgressIndicator` maupun gauge melingkar.
class ScoreBars extends StatelessWidget {
  const ScoreBars({super.key, required this.scores});

  final List<LabelScore> scores;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var i = 0; i < scores.length; i++)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: _Bar(
              score: scores[i],
              tint: i == 0
                  ? scheme.primary
                  : scheme.primary.withValues(alpha: 0.4),
            ),
          ),
      ],
    );
  }
}

class _Bar extends StatelessWidget {
  const _Bar({required this.score, required this.tint});

  final LabelScore score;
  final Color tint;

  @override
  Widget build(BuildContext context) {
    final track = Theme.of(context).colorScheme.surfaceContainerHighest;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                score.name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
            const SizedBox(width: 8),
            Text(score.percentLabel),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: Container(
            height: 10,
            color: track,
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: score.score.clamp(0.03, 1.0),
              child: Container(color: tint),
            ),
          ),
        ),
      ],
    );
  }
}
