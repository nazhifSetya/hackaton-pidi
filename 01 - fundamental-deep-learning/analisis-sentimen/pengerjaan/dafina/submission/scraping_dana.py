"""
scraping_dana.py
================
Scraping ulasan aplikasi DANA (id.dana) dari Google Play Store
untuk proyek Analisis Sentimen (Dicoding - Belajar Fundamental Deep Learning).

STRATEGI SCRAPING:
- STRATIFIED per rating bintang (1-5) target ~6.500 ulasan total.
  Verify-first API (2026-07-15) menunjukkan rating rata-rata DANA = 4,6852
  dan bintang 5 mendominasi 86,3% (8,88 juta dari 10,29 juta rating).
  Tanpa stratifikasi, kelas NEGATIF (bintang 1-2) dan NETRAL (bintang 3)
  akan tenggelam.
- Semua bintang punya jauh lebih banyak dari target: bintang 1 = 455rb,
  bintang 2 = 120rb, bintang 3 = 217rb, bintang 4 = 621rb, bintang 5 = 8,88jt.
  Jadi target {1:1500, 2:1000, 3:1500, 4:1000, 5:1500} = 6.500 total sangat
  aman untuk kriteria wajib >=3.000 sampel.
- Sort = NEWEST agar menangkap ulasan terbaru (isu terkini domain e-wallet:
  iklan mengganggu, dana cicil, error setelah update).
- Kolom identitas pengguna (userName, userImage) DIBUANG demi privasi.

OUTPUT: dataset_dana_reviews.csv (dataset mentah hasil scraping)

Menjalankan:  .venv\\Scripts\\python.exe submission\\scraping_dana.py
"""

import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

# Konfigurasi
APP_ID = "id.dana"                # package id DANA di Google Play
LANG = "id"                       # bahasa ulasan: Indonesia
COUNTRY = "id"                    # negara: Indonesia
# Target per bintang - stratified merata; polar sedikit di-boost supaya
# kelas negatif & positif seimbang; bintang 3 tetap 1.500 untuk pool netral.
PER_STAR = {1: 1_500, 2: 1_000, 3: 1_500, 4: 1_000, 5: 1_500}
PAGE_SIZE = 200                   # jumlah ulasan per request (batas wajar API)
# Simpan CSV di folder yang sama dengan skrip ini (submission/), apa pun cwd-nya
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "dataset_dana_reviews.csv")


def scrape_by_star(star: int, target: int) -> list:
    """Ambil hingga `target` ulasan untuk satu nilai bintang, lewat pagination."""
    collected = []
    token = None
    while len(collected) < target:
        batch, token = reviews(
            APP_ID,
            lang=LANG,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=min(PAGE_SIZE, target - len(collected)),
            filter_score_with=star,
            continuation_token=token,
        )
        if not batch:
            break
        collected.extend(batch)
        print(f"  bintang {star}: terkumpul {len(collected)}")
        if token is None:      # tidak ada halaman berikutnya
            break
        time.sleep(0.5)        # jeda sopan agar tidak membebani server
    return collected[:target]


def main():
    all_reviews = []
    for star, target in PER_STAR.items():
        print(f"Scraping ulasan bintang {star} (target {target:,}) ...")
        all_reviews.extend(scrape_by_star(star, target))

    df = pd.DataFrame(all_reviews)

    # Buang kolom identitas pengguna demi privasi
    df = df.drop(columns=["userName", "userImage"], errors="ignore")
    # Buang duplikat berdasarkan reviewId (jaga-jaga jika ada tumpang tindih)
    df = df.drop_duplicates(subset=["reviewId"]).reset_index(drop=True)

    df.to_csv(OUTPUT, index=False)

    print("\n=== SELESAI ===")
    print(f"Total ulasan unik : {len(df):,}")
    print("Distribusi rating bintang:")
    print(df["score"].value_counts().sort_index())
    print("Rentang tanggal   :", df["at"].min(), "->", df["at"].max())
    print("File tersimpan     :", OUTPUT)


if __name__ == "__main__":
    main()
