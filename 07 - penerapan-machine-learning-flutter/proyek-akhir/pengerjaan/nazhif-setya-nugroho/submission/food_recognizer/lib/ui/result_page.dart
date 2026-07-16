import 'dart:io';

import 'package:flutter/material.dart';
import 'package:submission/service/food_classifier.dart';
import 'package:submission/widget/classification_item.dart';

class ResultPage extends StatelessWidget {
  final File imageFile;

  const ResultPage({super.key, required this.imageFile});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Result Page'),
      ),
      body: SafeArea(child: _ResultBody(imageFile: imageFile)),
    );
  }
}

class _ResultBody extends StatefulWidget {
  final File imageFile;

  const _ResultBody({required this.imageFile});

  @override
  State<_ResultBody> createState() => _ResultBodyState();
}

class _ResultBodyState extends State<_ResultBody> {
  final FoodClassifier _classifier = FoodClassifier();
  FoodPrediction? _prediction;
  String? _error;

  @override
  void initState() {
    super.initState();
    Future.microtask(_runInference);
  }

  Future<void> _runInference() async {
    try {
      await _classifier.load();
      final result = await _classifier.classify(widget.imageFile);
      if (!mounted) return;
      setState(() => _prediction = result);
    } catch (e) {
      if (!mounted) return;
      setState(() => _error = e.toString());
    }
  }

  @override
  void dispose() {
    _classifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.file(widget.imageFile, fit: BoxFit.cover),
            ),
          ),
          const SizedBox(height: 16),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Terjadi kesalahan:\n$_error',
                style: const TextStyle(color: Colors.red),
                textAlign: TextAlign.center,
              ),
            )
          else if (_prediction == null)
            const ClassificatioinItemShimmer()
          else
            ClassificatioinItem(
              item: _prediction!.label,
              value:
                  '${(_prediction!.confidence * 100).toStringAsFixed(2)}%',
            ),
        ],
      ),
    );
  }
}
