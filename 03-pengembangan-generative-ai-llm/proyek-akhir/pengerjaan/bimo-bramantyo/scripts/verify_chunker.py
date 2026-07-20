"""
VERIFY-FIRST logika non-model untuk notebook RAG (dijalankan lokal).

Tujuan: membuktikan strategi chunking yang akan dipakai di notebook benar-benar
menghasilkan potongan dengan overlap yang aktif, SEBELUM di-Run di Colab.

Uji:
  1. RecursiveCharacterTextSplitter(1000, 150) pada teks sintetis -> overlap aktif.
  2. pypdf membuka keempat PDF regulasi (jumlah halaman) + ekstraksi 1 PDF kecil.

Jalankan: python scripts/verify_chunker.py
"""
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

DIR_PDF = Path(__file__).resolve().parents[1] / "data" / "raw"
UKURAN, OVERLAP = 1000, 150

pemotong = RecursiveCharacterTextSplitter(
    chunk_size=UKURAN,
    chunk_overlap=OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# --- Uji 1: overlap aktif pada teks sintetis --------------------------------
kalimat = ("Pasal {n} ayat ini mengatur ketentuan mengenai hak dan kewajiban "
           "pekerja serta pemberi kerja sesuai Undang-Undang Cipta Kerja. ")
teks = "".join(kalimat.format(n=i) for i in range(1, 120))

potongan = pemotong.split_text(teks)
total_char = sum(len(p) for p in potongan)

print("=== Uji 1: chunker sintetis ===")
print("Panjang teks asli :", len(teks))
print("Jumlah potongan   :", len(potongan))
print("Panjang max chunk :", max(len(p) for p in potongan))
print("Total char chunk  :", total_char, "(harus > asli karena overlap)")

assert len(potongan) > 1, "Teks panjang harus terpotong jadi banyak chunk."
assert total_char > len(teks), "Overlap tidak aktif (total char tidak melebihi asli)."
assert max(len(p) for p in potongan) <= UKURAN + 50, "Ada chunk jauh melebihi ukuran."

# bukti overlap eksplisit antar dua chunk pertama (ada irisan teks)
ekor = potongan[0][-OVERLAP:]
irisan = any(ekor[k:] and potongan[1].startswith(ekor[k:]) for k in range(len(ekor)))
print("Overlap chunk[0]->chunk[1] terdeteksi:", irisan)
assert irisan, "Tidak ada irisan teks antar chunk berurutan."
print("Uji 1 LULUS.\n")

# --- Uji 2: pypdf membaca 4 PDF ---------------------------------------------
print("=== Uji 2: pypdf membaca PDF ===")
berkas = ["PP_5_2021.pdf", "PP_35_2021.pdf", "PP_51_2023.pdf", "UU_6_2023.pdf"]
for nama in berkas:
    jalur = DIR_PDF / nama
    ada = jalur.exists()
    n_hal = len(PdfReader(str(jalur)).pages) if ada else 0
    print(f"  {'[OK]' if ada else '[--]'} {nama:<16} halaman: {n_hal}")
    assert ada, f"PDF hilang: {nama}"

# ekstraksi + chunk 1 PDF kecil sebagai sanity
reader = PdfReader(str(DIR_PDF / "PP_51_2023.pdf"))
isi = "\n".join((h.extract_text() or "") for h in reader.pages)
chunk_pp51 = pemotong.split_text(isi)
print("\nPP_51_2023: panjang teks", len(isi), "-> jumlah chunk", len(chunk_pp51))
print("Contoh chunk[0] (180 char):")
print(chunk_pp51[0][:180].replace("\n", " "), "...")
assert len(chunk_pp51) > 1
print("\nUji 2 LULUS. Semua verifikasi non-model beres.")
