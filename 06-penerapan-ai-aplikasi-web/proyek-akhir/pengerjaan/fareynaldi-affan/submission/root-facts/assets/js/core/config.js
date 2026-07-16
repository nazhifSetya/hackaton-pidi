export const APP_CONFIG = {
  // Ambang hanya sebagai indikator UI; alur Basic selalu menampilkan tebakan
  // teratas agar label muncul walau kondisi kamera kurang ideal.
  detectionConfidenceThreshold: 40,
  analyzingDelay: 2000,
  funFactGenerationDelay: 2000,
  detectionRetryInterval: 100
};

export const UI_CONFIG = {
  fadeAnimation: 'fadeIn 0.5s ease-out forwards',
  confidenceThresholds: {
    excellent: 90,
    good: 80
  }
};
