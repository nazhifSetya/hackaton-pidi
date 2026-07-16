"""
scraping_pln_mobile.py
=======================
Scraping ulasan aplikasi PLN Mobile (com.icon.pln123) dari Google Play Store
untuk proyek Analisis Sentimen (Dicoding - Belajar Fundamental Deep Learning).

STRATEGI SCRAPING:
- STRATIFIED per rating bintang (1-5). Alasan: rata-rata rating PLN Mobile
  ~4,89 sehingga ulasan positif sangat mendominasi. Kalau diambil acak, kelas
  NEGATIF (bintang 1-2) & NETRAL (bintang 3) akan tenggelam. Dengan mengambil
  jumlah yang setara per bintang, ketiga kelas sentimen terwakili cukup banyak.
- Sort = NEWEST supaya menangkap ulasan terbaru, termasuk lonjakan ulasan
  pasca pemadaman listrik serentak Jakarta (April 2026) yang jadi momen trending.
- Kolom identitas pengguna (userName, userImage) DIBUANG demi privasi.

OUTPUT: dataset_pln_reviews.csv  (dataset mentah hasil scraping)

Menjalankan:  python scraping_pln_mobile.py
"""

import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

# ── Konfigurasi ──────────────────────────────────────────────────────────────
APP_ID = "com.icon.pln123"   # package id PLN Mobile di Google Play
LANG = "id"                  # bahasa ulasan: Indonesia
COUNTRY = "id"               # negara: Indonesia
PER_STAR = 10000             # target ulasan per bintang -> maksimal 50.000 total
PAGE_SIZE = 200              # jumlah ulasan per request (batas wajar API Play)
# Simpan CSV di folder yang sama dengan skrip ini (submission/), apa pun cwd-nya
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_pln_reviews.csv")


def scrape_by_star(star):
    """Ambil hingga PER_STAR ulasan untuk satu nilai bintang, lewat pagination."""
    collected = []
    token = None
    while len(collected) < PER_STAR:
        batch, token = reviews(
            APP_ID,
            lang=LANG,
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=min(PAGE_SIZE, PER_STAR - len(collected)),
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
    return collected[:PER_STAR]


def main():
    all_reviews = []
    for star in [1, 2, 3, 4, 5]:
        print(f"Scraping ulasan bintang {star} ...")
        all_reviews.extend(scrape_by_star(star))

    df = pd.DataFrame(all_reviews)

    # Buang kolom identitas pengguna demi privasi
    df = df.drop(columns=["userName", "userImage"], errors="ignore")
    # Buang duplikat berdasarkan reviewId (jaga-jaga jika ada tumpang tindih)
    df = df.drop_duplicates(subset=["reviewId"]).reset_index(drop=True)

    df.to_csv(OUTPUT, index=False)

    print("\n=== SELESAI ===")
    print("Total ulasan unik :", len(df))
    print("Distribusi rating bintang:")
    print(df["score"].value_counts().sort_index())
    print("Rentang tanggal   :", df["at"].min(), "->", df["at"].max())
    print("File tersimpan     :", OUTPUT)


if __name__ == "__main__":
    main()
