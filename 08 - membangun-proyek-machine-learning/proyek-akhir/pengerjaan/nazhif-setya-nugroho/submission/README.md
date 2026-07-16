<div align="center">

# 💻 Folder Submission (Tempat Kode)

**Folder ini khusus untuk file pengerjaan kamu** — notebook, model, dan dataset hasil.
Sengaja dipisah dari [`../panduan/`](../panduan/Checklist_Pengerjaan.md) (dokumentasi) dan [`../artifact/`](../artifact/) (bahan asli dari Dicoding).

</div>

---

## 🚀 Cara mulai

1. **Salin** template dari `artifact/` ke folder ini, lalu **rename** sesuai namamu:
   - `artifact/Template_Clustering/[Clustering]_...ipynb` → `[Clustering]_Submission_Akhir_BMLP_Nama_Kamu.ipynb`
   - `artifact/Template_Klasifikasi/[Klasifikasi]_...ipynb` → `[Klasifikasi]_Submission_Akhir_BMLP_Nama_Kamu.ipynb`
2. Kerjakan ngikutin [`../panduan/Checklist_Pengerjaan.md`](../panduan/Checklist_Pengerjaan.md).
3. File model (`.h5`) dan CSV hasil akan otomatis muncul di sini saat notebook dijalankan.

---

## 📦 Isi akhir folder (yang nanti di-zip)

```
submission/
├── [Clustering]_Submission_Akhir_BMLP_Nama_Kamu.ipynb   ✅ wajib
├── [Klasifikasi]_Submission_Akhir_BMLP_Nama_Kamu.ipynb  ✅ wajib
├── model_clustering.h5                                   ✅ wajib
├── decision_tree_model.h5                                ✅ wajib
├── data_clustering.csv                                   ✅ wajib
├── PCA_model_clustering.h5                               🟣 opsional (Advanced K3)
├── explore_<Algoritma>_classification.h5                🔵 opsional (Skilled K5)
├── tuning_classification.h5                              🟣 opsional (Advanced K5)
└── data_clustering_inverse.csv                           🟣 opsional (Advanced K4)
```

> ⚠️ Saat submit: masukkan **semua file di atas** ke dalam 1 folder, lalu **zip** jadi `BMLP_Nama-kamu.zip`. Struktur di dalam zip = **flat** (tanpa subfolder).
