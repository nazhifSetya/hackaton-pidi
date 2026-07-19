// Konfigurasi aplikasi. `detectionConfidenceThreshold` di sini murni acuan
// tampilan bar kepercayaan; app.js sengaja TIDAK memakainya sebagai syarat
// menampilkan label, karena webcam sungguhan sering menghasilkan skor rendah
// dan pengguna tetap harus melihat tebakan teratas.
export const APP_CONFIG = {
  detectionConfidenceThreshold: 25,
  analyzingDelay: 1800,
  funFactGenerationDelay: 1800,
  detectionRetryInterval: 120
};

export const UI_CONFIG = {
  fadeAnimation: 'fadeIn 0.5s ease-out forwards',
  confidenceThresholds: {
    excellent: 90,
    good: 80
  }
};
