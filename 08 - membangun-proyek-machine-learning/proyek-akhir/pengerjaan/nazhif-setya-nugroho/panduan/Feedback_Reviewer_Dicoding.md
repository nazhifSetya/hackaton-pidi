<div align="center">

# 🏆 Feedback Reviewer Dicoding — BMLP

### Membangun Proyek Machine Learning · **LULUS**

<span style="background:#7c3aed;color:#fff;padding:4px 16px;border-radius:8px;font-weight:bold;font-size:16px;">NILAI AKHIR: ADVANCED (4.0) ⭐⭐⭐⭐⭐</span>

_Nazhif Setya Nugroho_

</div>

---

## 📊 Hasil Penilaian per Kriteria

| Kriteria | Level | Poin |
| :--- | :---: | :---: |
| K1 — Memuat Dataset dan Melakukan EDA | 🟣 **Advanced** | 4 pts |
| K2 — Pembersihan dan Pra Pemrosesan Data | 🟣 **Advanced** | 4 pts |
| K3 — Membangun Model Clustering | 🟣 **Advanced** | 4 pts |
| K4 — Menuliskan Interpretasi Cluster | 🟣 **Advanced** | 4 pts |
| K5 — Membangun Model Klasifikasi | 🟣 **Advanced** | 4 pts |
| **NILAI AKHIR** | **🟣 Advanced** | **4.0** |

> **Catatan skema Mastery-Grading (dari reviewer):** penilaian berjenjang — jika kriteria **Skilled tidak terpenuhi**, penerapan **Advanced tidak dianggap sah**. Karena nilai kita Advanced valid di semua kriteria, berarti Basic + Skilled + Advanced semuanya **terpenuhi dengan benar**. ✅

---

## 💬 Catatan dari Reviewer

> Hallo Nazhif Setya!, Selamat, kami dengan senang hati mengumumkan bahwa Anda telah berhasil menyelesaikan tugas **Membangun Proyek Machine Learning**. Dengan memanfaatkan semua teori dan praktik yang telah Anda pelajari, Anda berhasil membangun proyek machine learning yang menarik dengan menerapkan pendekatan **supervised** dan **unsupervised learning**. Ini adalah pencapaian yang patut dibanggakan!
>
> Kami telah meninjau proyek yang Anda kirimkan, dan kami sangat terkesan dengan kualitas serta kesesuaian dengan berbagai kriteria yang telah ditetapkan. Namun, untuk membuat karya Anda semakin luar biasa, kami ingin memberikan beberapa saran dan catatan yang mungkin berguna bagi Anda untuk kedepannya.

### Overall Review

> **Good Job!** Kamu berhasil menerapkan semua kriteria basic dan mengerjakan submission ini dengan sangat baik.

---

## 💡 Additional Tips (saran pengembangan ke depan)

Tips dari reviewer ini **bukan kekurangan submission** (kita sudah Advanced) — ini arahan biar skill makin tajam di proyek berikutnya.

### 1. Eksplorasi Model Clustering Selain KMeans
KMeans bukan satu-satunya algoritma clustering. Coba:
- **DBSCAN** — bagus untuk cluster bentuk tidak beraturan + mengabaikan noise.
- **Agglomerative Clustering** — cocok untuk hierarki & cluster yang tumpang tindih.
- **Gaussian Mixture Model (GMM)** — untuk cluster dengan distribusi berbeda-beda.

### 2. Seleksi Fitur untuk Model Clustering
- **Correlation Matrix** — hilangkan fitur dengan korelasi tinggi (redundan).
- **Variance Threshold** — hilangkan fitur dengan variasi sangat rendah.
- **SelectKBest / Mutual Information** — pilih fitur paling relevan.

### 3. Evaluasi Clustering Selain Silhouette Score
- **Davies-Bouldin Index** (semakin kecil semakin baik).
- **Calinski-Harabasz Score** (semakin besar semakin baik).
- **Dendrogram** (jika pakai hierarchical clustering).

### 4. Seleksi Fitur untuk Model Klasifikasi
- **Recursive Feature Elimination (RFE)**.
- **Feature Importance** dari Random Forest.
- **Chi-Square Test** untuk fitur kategorikal.
- → mempercepat training & meningkatkan akurasi.

### 5. Handling Imbalance pada Target Klasifikasi
- **SMOTE / ADASYN** — oversampling data minoritas.
- **Class Weighting** (mis. `class_weight='balanced'`).
- **Undersampling** data mayoritas bila perlu.

### 6. Tambahkan Evaluasi ROC Curve & AUC Score
- **ROC Curve** — trade-off True Positive Rate vs False Positive Rate.
- **AUC** — seberapa baik model membedakan antar kelas (berguna saat data tidak seimbang).

### 7. Visualisasi Data Interaktif
- Gunakan **Plotly** / **Bokeh** untuk grafik yang bisa di-zoom, hover detail, & filter dinamis.

### 8. Jadikan Proyek Ini Portfolio
- Upload ke **GitHub** + tambahkan **README** (penjelasan proyek + insight utama).
- Sertakan link **dashboard** publik bila ada (mis. Looker Studio).
- Simpan versi **Jupyter Notebook / PDF** agar mudah dibagikan (mis. saat interview).

---

## 🎓 Penutup dari Reviewer

> Overall, kamu mengerjakan submission ini dengan sangat baik. Selanjutnya kamu dapat terus mengasah skill machine learning pada kelas selanjutnya yaitu **Belajar Pengembangan Machine Learning**. Semangat!
>
> Tetap semangat untuk meraih karier sebagai **Machine Learning Engineer**, ya!
>
> _Salam,_
> **Dicoding Reviewer**

---

<div align="center">

### ✅ Status Proyek: **SELESAI & LULUS — Advanced (4.0)**

_Langkah lanjut yang disarankan: kelas **Belajar Pengembangan Machine Learning**._

</div>
