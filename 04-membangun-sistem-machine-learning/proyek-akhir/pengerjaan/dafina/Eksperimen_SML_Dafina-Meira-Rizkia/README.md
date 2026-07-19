# Eksperimen SML — Klasifikasi Spesies Palmer Penguins

**Nama:** Dafina Meira Rizkia
**Kelas:** Membangun Sistem Machine Learning (Dicoding)

Repository ini memenuhi **Kriteria 1** proyek akhir: eksplorasi dan preprocessing
dataset secara manual mengikuti Template Eksperimen MSML.

## Struktur

```
Eksperimen_SML_Dafina-Meira-Rizkia/
├── penguins_raw.csv                 # dataset mentah (344 baris)
└── preprocessing/
    ├── Eksperimen_Dafina-Meira-Rizkia.ipynb   # notebook: data loading, EDA, preprocessing
    └── penguins_preprocessing.csv             # hasil preprocessing (333 baris, siap latih)
```

## Alur notebook

1. **Data Loading** — memuat `penguins_raw.csv`.
2. **EDA** — distribusi kelas, pemeriksaan nilai kosong, sebaran & korelasi fitur,
   komposisi fitur kategorikal.
3. **Data Preprocessing** — membuang nilai kosong, encoding `island` (one-hot) & `sex`
   (biner), label-encode target `species`, standardisasi fitur numerik.
4. **Menyimpan** dataset siap latih ke `penguins_preprocessing.csv`.

Dataset: Palmer Penguins (Horst, Hill & Gorman, 2020).
