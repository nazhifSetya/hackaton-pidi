Halo dafina_meira_rizkl6s,

Terima kasih telah meluangkan waktu dan usaha Anda dalam mengerjakan serta mengirimkan tugas Proyek Image Generation. Kami sangat menghargai dedikasi Anda dalam mengikuti seluruh rangkaian pembelajaran di kelas ini.

Setelah kami melakukan peninjauan secara menyeluruh terhadap proyek yang Anda kirimkan, kami menemukan bahwa masih terdapat beberapa kriteria wajib yang belum sepenuhnya terpenuhi. Oleh karena itu, submission ini belum dapat kami nyatakan lulus pada tahap ini.

Kami berharap umpan balik berikut dapat membantu Anda melakukan perbaikan dan meningkatkan kualitas proyek Anda.

Kriteria 1: Melakukan Image Generation (Text-to-Image)

Berdasarkan peninjauan kami, gambar yang dihasilkan dari fungsi generate_simple_image() masih terlihat terlalu realistis dan menyerupai 3D render. Sesuai dengan instruksi submission untuk pemenuhan level Basic, gambar yang dihasilkan seharusnya memiliki gaya visual ilustrasi 2D atau kartun (flat), bukan 3D atau foto realistis.
Saran Perbaikan:
Sesuaikan kembali prompt yang kamu gunakan agar secara eksplisit meminta gaya ilustrasi. Sebagai contoh: "an astronaut standing on moon surface, earth visible in background, cartoon style, flat 2D".
Pastikan kamu menyertakan negative prompt wajib yang telah ditentukan pada instruksi untuk menekan hasil yang mengarah ke realistis. Ketikkan secara persis: "photorealistic, realistic, photograph, 3d render, messy, blurry, low quality, bad art, ugly, sketch, grainy, unfinished, chromatic aberration". (Kata kunci seperti photorealistic dan 3d render di sini sangat penting).
Tetap gunakan seed yang sama (yaitu seed=222) agar hasil generate tetap konsisten dan sesuai dengan ekspektasi penilaian.
Gambar untuk fungsi generate_simple_image()
![alt text](image.png)

Gambar untuk fungsi generate_advanced_image().

![alt text](image-1.png)

![alt text](image-2.png)
![alt text](image-3.png)

Kriteria 2: Menyempurnakan Gambar Melalui Image-to-Image

Hasil generate fungsi inpainting belum menampilkan object broken satelit secara jelas yang diharapkan sesuai contoh gambar pada instruksi.
Cobalah untuk memperbaiki prompt dengan menambahkan detail seperti besar atau kecilnya object dan sebagainya, kemudian lakukan tuning config scale dan step dari kecil hingga besar,
Saran Prompt:

 prompt_satellite = (
    "A damaged and broken satellite crashed on the lunar surface, "
    "surrounded by craters, metallic debris, shattered panels, and exposed mechanical components. "
    "The wreckage features multi-legged landing gear and highly detailed structures. "
    "Sharp focus, realistic scale, photorealistic style, cinematic lighting, "
    "ultra-detailed mechanical textures."
)

Pada model inpainting berbasis diffusion (misalnya Stable Diffusion), dua parameter utama yang sangat berpengaruh adalah:

CFG Scale (Guidance Scale)
Sampling Steps
Kalau keduanya terlalu kecil, hasil inpainting sering:
Tidak muncul sama sekali
Perubahannya sangat halus
Mask terabaikan
Output terlihat seperti gambar asli tanpa modifikasi
Inpainting : Gambar yang diharapkan

![alt text](image-4.png)

Kami mendorong Anda untuk memperbaiki proyek ini dengan mengacu pada catatan di atas, lalu melakukan submit ulang setelah seluruh kriteria terpenuhi. Jangan berkecil hati, setiap proses revisi adalah bagian penting dalam membangun pemahaman yang lebih kuat tentang bagaimana Generative AI dirancang dan diimplementasikan secara end-to-end.

Jika Anda memiliki pertanyaan, silakan kunjungi forum diskusi. Dengan senang hati kami akan membantu Anda.

Tetap semangat dan terus eksplorasi dunia Generative AI!