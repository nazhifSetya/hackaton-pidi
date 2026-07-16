"""
scraping_shopee.py
==================
Scraping ulasan aplikasi Shopee (com.shopee.id) dari Google Play Store
untuk proyek Analisis Sentimen (Dicoding - Belajar Fundamental Deep Learning).

STRATEGI SCRAPING:
- STRATIFIED per rating bintang (1-5) dengan **boost bintang 3** untuk kelas netral.
  Verify-first API (2026-07-12) menunjukkan rating rata-rata Shopee = 4,57 dan
  bintang 5 mendominasi 83,19% (15,36 juta dari 18,46 juta rating). Tanpa
  stratifikasi, kelas NEGATIF (bintang 1-2) dan NETRAL (bintang 3) akan
  tenggelam. Boost bintang 3 lebih besar (15rb vs 12rb bintang polar) karena
  netral biasanya kelas paling minoritas & sulit (pelajaran Fareynaldi).
- Semua bintang punya jauh lebih banyak dari target: bintang 1 = 1,34jt,
  bintang 2 = 237rb, bintang 3 = 386rb, bintang 4 = 1,14jt, bintang 5 = 15,36jt.
  Jadi target `{1:12rb, 2:8rb, 3:15rb, 4:8rb, 5:12rb}` (≈ 55rb) sangat aman.
- Sort = NEWEST supaya menangkap ulasan terbaru, termasuk lonjakan seputar
  kenaikan biaya Gratis Ongkir XTRA (2 Mei 2026) & gangguan teknis 2026.
- Kolom identitas pengguna (userName, userImage) DIBUANG demi privasi.

OUTPUT: dataset_shopee_reviews.csv (dataset mentah hasil scraping)

Menjalankan:  .venv\\Scripts\\python.exe submission\\scraping_shopee.py
"""

import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

# ── Konfigurasi ──────────────────────────────────────────────────────────────
APP_ID = "com.shopee.id"          # package id Shopee di Google Play
LANG = "id"                       # bahasa ulasan: Indonesia
COUNTRY = "id"                    # negara: Indonesia
# Target per bintang — bintang 3 di-boost supaya kelas netral cukup
PER_STAR = {1: 12_000, 2: 8_000, 3: 15_000, 4: 8_000, 5: 12_000}
PAGE_SIZE = 200                   # jumlah ulasan per request (batas wajar API)
# Simpan CSV di folder yang sama dengan skrip ini (submission/), apa pun cwd-nya
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "dataset_shopee_reviews.csv")


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
