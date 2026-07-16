import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:submission/ui/result_page.dart';

class HomeController extends ChangeNotifier {
  final ImagePicker _picker = ImagePicker();
  File? _selectedImage;

  File? get selectedImage => _selectedImage;

  Future<void> pickFromCamera() async {
    final picked = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 90,
    );
    if (picked != null) {
      _selectedImage = File(picked.path);
      notifyListeners();
    }
  }

  Future<void> pickFromGallery() async {
    final picked = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 90,
    );
    if (picked != null) {
      _selectedImage = File(picked.path);
      notifyListeners();
    }
  }

  void goToResultPage(BuildContext context) {
    if (_selectedImage == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ResultPage(imageFile: _selectedImage!),
      ),
    );
  }
}
