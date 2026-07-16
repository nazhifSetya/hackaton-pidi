"""
scraping_mytelkomsel.py
========================
Scraping ulasan aplikasi MyTelkomsel (com.telkomsel.telkomselcm) dari Google Play
Store untuk proyek Analisis Sentimen (Dicoding - Belajar Fundamental Deep Learning).

STRATEGI SCRAPING (STRATIFIED per rating bintang 1-5):
- Rata-rata rating MyTelkomsel ~4,38 sehingga ulasan positif (bintang 5) tetap
  mendominasi (~77%). Kalau diambil acak, kelas NEGATIF (bintang 1) & NETRAL
  (bintang 3) akan tenggelam. Dengan mengambil per bintang secara terpisah,
  ketiga kelas sentimen terwakili cukup banyak.
- Bintang 3 (calon kelas NETRAL) di-boost lebih besar karena setelah pelabelan
  hybrid hanya sebagian kecil bintang-3 yang lolos jadi netral murni (skor lexicon
  rendah). Pool lebih besar => kelas netral lebih sehat.
- Sort = NEWEST supaya menangkap ulasan terbaru, termasuk lonjakan keluhan
  "aplikasi berat/lemot/error pasca-update" yang jadi momen trending 2026.
- Kolom identitas pengguna (userName, userImage) DIBUANG demi privasi.

OUTPUT: dataset_mytelkomsel_reviews.csv  (dataset mentah hasil scraping)

Menjalankan:  python scraping_mytelkomsel.py
"""

import os
import time
import pandas as pd
from google_play_scraper import reviews, Sort

# ── Konfigurasi ──────────────────────────────────────────────────────────────
APP_ID = "com.telkomsel.telkomselcm"   # package id MyTelkomsel di Google Play
LANG = "id"                            # bahasa ulasan: Indonesia
COUNTRY = "id"                         # negara: Indonesia
PAGE_SIZE = 200                        # jumlah ulasan per request (batas wajar API Play)

# Target per bintang. Bintang 3 (netral) sengaja lebih besar (lihat docstring).
STAR_TARGETS = {1: 12000, 2: 8000, 3: 18000, 4: 8000, 5: 12000}

# Simpan CSV di folder yang sama dengan skrip ini (submission/), apa pun cwd-nya
OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dataset_mytelkomsel_reviews.csv"
)


def scrape_by_star(star, target):
    """Ambil hingga `target` ulasan untuk satu nilai bintang, lewat pagination.

    Args:
        star (int): nilai bintang yang difilter (1..5).
        target (int): jumlah maksimum ulasan yang ingin dikumpulkan.

    Returns:
        list[dict]: daftar ulasan mentah dari google-play-scraper (maks `target`).
    """
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
    """Scrape semua bintang, bersihkan duplikat & kolom PII, simpan ke CSV."""
    all_reviews = []
    for star, target in STAR_TARGETS.items():
        print(f"Scraping ulasan bintang {star} (target {target}) ...")
        all_reviews.extend(scrape_by_star(star, target))

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
