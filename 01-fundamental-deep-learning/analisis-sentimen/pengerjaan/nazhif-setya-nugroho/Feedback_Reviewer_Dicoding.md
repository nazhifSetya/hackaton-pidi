Catatan dari Reviewer

Hallo nazhif_setyaf0tp!, Selamat! Kamu telah berhasil menyelesaikan tugas untuk Proyek Analisis Sentimen. Dengan demikian kamu telah berhasil membuat proyek analisis sentimen.

Terima kasih telah sabar menunggu. Kami membutuhkan waktu untuk bisa memberikan feedback yang komprehensif. Untuk meningkatkan kualitas project submission yang dikirimkan, kamu dapat menerapkan beberapa saran berikut:
![alt text](image.png)

Proyek yang Anda kirimkan sudah bagus dan memenuhi berbagai ketentuan. Kamu juga telah menerapkan seluruh saran diantaranya :

Menggunakan algoritma deep learning.
Akurasi pada training set dan testing set di atas 92%.
Dataset yang digunakan untuk melatih model minimal memiliki tiga kelas.
Memiliki jumlah data minimal 10.000 sampel data.
Melakukan 3 percobaan skema pelatihan yang berbeda.
Melakukan inference atau testing dalam file .ipynb atau .py yang menghasilkan output berupa kelas kategorikal (contoh: negatif, netral, dan positif).
Namun, agar lebih sempurna lagi, Anda bisa perhatikan beberapa saran dan catatan dari kami.

[Proses Stemming]

Jika kamu merasa proses stemming yang kamu terapkan saat ini memakan waktu yang terlalu lama hingga akhirnya memutuskan untuk tidak melakukan stemming sama sekali saat prapemrosesan teks, kamu bisa mencoba library alternatif MPStemmer untuk proses stemming pada teks berbahasa Indonesia. Library ini unggul dari segi kecepatan pemrosesan stemming teks jika dibandingkan dengan library lain seperti PySastrawi atau NLTK. Kamu bisa mempelajarinya lebih lanjut di sini: Stemming with MPStemmer.
Additional Tips

Selalu perhatikan import yang tidak pernah digunakan agar kode yang sudah ditulis menjadi lebih bersih
Analisis Emosi (Emotion Analysis). Selain analisis sentimen, kamu dapat mencoba analisis emosi dengan package NRCLex. NRCLex mampu mengklasifikasikan teks ke dalam delapan kategori emosi: anger, anticipation, disgust, fear, joy, sadness, surprise, dan trust. Hal ini bisa memberikan perspektif tambahan pada data. Untuk memulai, gunakan perintah pip install NRCLex lalu eksplorasi dokumentasinya di GitHub.

Tambahkan dokumentasi pada setiap fungsi atau modul untuk memudahkan pemahaman. Kamu juga bisa menambahkan deskripsi dengan menggunakan text cell.

Saat mendefinisikan dictionary yang sangat panjang akan lebih baik jika dictionary tersebut disimpan pada file txt untuk meningkatkan keterbacaan kode.

Saat melakukan pengujian dengan data baru pastikan untuk menguji seluruh kelas yang ada dan sebaiknya menggunakan beberapa contoh input untuk memastikan keabsahan model
Gunakan Pipeline dari Scikit-learn atau TensorFlow untuk mengotomatisasi alur kerja dari preprocessing hingga evaluasi model, sehingga lebih efisien dan tidak ada langkah yang terlewat.
Lakukan Cross-Validation untuk menghindari overfitting dan memastikan model bekerja dengan baik pada data baru.
Gunakan metrik evaluasi yang lengkap, tidak hanya akurasi, tetapi juga Precision, Recall, F1-Score per kelas, dan tampilkan Confusion Matrix.
Lakukan analisis kesalahan (Error Analysis) dengan memilih sampel teks yang salah klasifikasi, dan pelajari pola kesalahan seperti sarkasme, negasi, atau penggunaan slang.
Perkaya data menggunakan teknik augmentation (synonym replacement, back-translation, random insertion) dan preprocessing lanjutan (lemmatization vs. stemming, normalisasi slang, emoji handling).
Selalu utamakan prapemrosesan teks terlebih dahulu sebelum kamu melakukan pelabelan sentimen hingga pemodelan sentimen. Hal ini berguna untuk mencegah adanya pelabelan yang keliru terhadap satu atau lebih baris teks yang akan kamu analisis dari segi polarisasi sentimennya sebagai akibat dari membaca karakter/kata yang seharusnya tidak dianggap sebagai sentimen, atau bahkan terjadi error terkait inkompatibilitas tipe data saat mendapatkan skor polarisasinya.
Akan lebih baik lagi jika kamu melakukan prapemrosesan tingkat lanjut seperti undersampling, normalisasi (scaling), dan encoding setelah proses splitting dataset untuk menghindari kemungkinan kebocoran data (data leak) pada data test.
Tingkatkan interpretabilitas dan visualisasi model dengan menerapkan XAI (seperti SHAP atau LIME) untuk menyorot kata paling berpengaruh; gunakan PCA atau t-SNE untuk visualisasi fitur; dan buat word cloud untuk insight tambahan.
Gunakan alat seperti MLflow atau Weights & Biases untuk melacak eksperimen, hyperparameter, dan hasil model, sehingga lebih mudah memahami apa yang telah dicoba dan mana yang berhasil.
Pantau performa model menggunakan metrik yang sesuai serta visualisasi hasil agar lebih mudah dianalisis dan ditingkatkan.
Dengan mengikuti saran-saran tersebut, kamu akan semakin mengasah keterampilan dan pengetahuan dalam pengembangan model Machine Learning. Terus semangat dan jangan ragu untuk bereksperimen!

Overall, kamu sudah mengerjakan submission ini dengan sangat baik! Well done! Tetap semangat menyelesaikan kelas Belajar Fundamental Deep Learning.

Silakan berkunjung ke forum diskusi untuk mengasah kembali penguasaan ilmu kamu dan membuat ilmu kamu bisa semakin bermanfaat dengan membantu developer yang lain.

Terima kasih telah membantu misi kami. Kesuksesan developer Indonesia adalah energi bagi kami. Jika memiliki pertanyaan terkait hasil submission, silakan mengikuti prosedur berikut.

Salam

Dicoding Reviewer
