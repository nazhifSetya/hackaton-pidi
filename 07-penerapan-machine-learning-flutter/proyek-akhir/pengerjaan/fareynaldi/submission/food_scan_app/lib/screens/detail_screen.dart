import 'dart:io';

import 'package:flutter/material.dart';

import '../ml/tflite_food_detector.dart';
import '../models/scan_result.dart';
import '../widgets/result_card.dart';

class DetailScreen extends StatefulWidget {
  const DetailScreen({super.key, required this.photo});

  final File photo;

  @override
  State<DetailScreen> createState() => _DetailScreenState();
}

enum _Phase { loading, done, error }

class _DetailScreenState extends State<DetailScreen> {
  final TfliteFoodDetector _detector = TfliteFoodDetector();

  _Phase _phase = _Phase.loading;
  ScanResult? _result;
  String _errorText = '';

  @override
  void initState() {
    super.initState();
    _kickOff();
  }

  Future<void> _kickOff() async {
    try {
      await _detector.warmUp();
      final r = await _detector.analyze(widget.photo);
      if (!mounted) return;
      setState(() {
        _result = r;
        _phase = _Phase.done;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorText = e.toString();
        _phase = _Phase.error;
      });
    }
  }

  @override
  void dispose() {
    _detector.release();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Hasil Deteksi')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: AspectRatio(
                  aspectRatio: 4 / 3,
                  child: Image.file(widget.photo, fit: BoxFit.cover),
                ),
              ),
              const SizedBox(height: 20),
              _buildBody(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBody() {
    switch (_phase) {
      case _Phase.loading:
        return const _LoadingBlock();
      case _Phase.error:
        return _ErrorBlock(message: _errorText, onRetry: _retry);
      case _Phase.done:
        return ResultCard(result: _result!);
    }
  }

  void _retry() {
    setState(() {
      _phase = _Phase.loading;
      _errorText = '';
      _result = null;
    });
    _kickOff();
  }
}

class _LoadingBlock extends StatelessWidget {
  const _LoadingBlock();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 32),
      child: Column(
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Menganalisis gambar…'),
        ],
      ),
    );
  }
}

class _ErrorBlock extends StatelessWidget {
  const _ErrorBlock({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.errorContainer,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Icon(Icons.error_outline, color: cs.onErrorContainer, size: 36),
          const SizedBox(height: 8),
          Text(
            'Gagal menjalankan model.',
            style: TextStyle(
              color: cs.onErrorContainer,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: cs.onErrorContainer),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('Coba lagi'),
          ),
        ],
      ),
    );
  }
}
