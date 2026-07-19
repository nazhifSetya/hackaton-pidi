"""
Builder: generate submission/RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb

Karakter implementasi (BASIC tier, ditulis independen):
- Loader PDF pypdf per-halaman.
- Chunker berbasis-KALIMAT (greedy packing) dengan overlap ekor eksplisit,
  bukan sliding window karakter dan bukan regex per-pasal.
- Embedder open-source multilingual-e5-base (wajib prefix query:/passage:).
- Vector store FAISS (IndexFlatIP atas vektor ter-normalisasi = cosine),
  indeks disimpan lokal.
- Retriever top-k dense. Generator = model K1 (Qwen SFT) dari Hugging Face.
- Antarmuka Kriteria 3 = loop input() interaktif + IPython.display.Markdown
  (opsi Basic selain Gradio).

Regenerate:  python scripts/build_rag_notebook.py
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(source)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _lines(source),
    }


def _lines(text: str) -> list:
    text = dedent(text).strip("\n")
    rows = text.split("\n")
    return [r + "\n" for r in rows[:-1]] + [rows[-1]]


cells: list = []

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
cells.append(md("""
    # Sistem RAG Asisten Legal Cipta Kerja — Submission PGABL

    **Notebook ini:** *Kriteria 2 (Sistem RAG)* + *Kriteria 3 (Antarmuka)* — tier Basic.

    Alur pipeline:

    1. Muat empat PDF regulasi Cipta Kerja (PP 5/2021, PP 35/2021, PP 51/2023,
       UU 6/2023) dengan `pypdf`.
    2. Pecah teks menjadi potongan **berbasis kalimat** — kalimat utuh dirangkai
       sampai mendekati `UKURAN_CHUNK=700` karakter, dengan `OVERLAP_CHUNK=120`
       karakter yang dibawa dari ekor potongan sebelumnya (ditulis eksplisit,
       bukan default library).
    3. Ubah potongan menjadi vektor memakai embedder open-source
       `intfloat/multilingual-e5-base`.
    4. Simpan vektor pada indeks **FAISS** lokal (`IndexFlatIP` atas vektor
       ter-normalisasi = kemiripan cosine).
    5. Panggil kembali model hasil fine-tuning (notebook K1) dari Hugging Face
       sebagai generator, lalu susun prompt `konteks + pertanyaan`.
    6. Bungkus pipeline dalam **loop `input()` interaktif** dengan keluaran rapi
       melalui `IPython.display.Markdown`.
"""))

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 0. Persiapan Lingkungan

    - Runtime Google Colab **T4 GPU** (free tier).
    - Colab Secret yang dibutuhkan:
        - `HF_TOKEN` (peran Read cukup untuk menarik model), aktifkan *Notebook access*.
        - `HF_USERNAME` — pemilik repositori model K1 hasil fine-tuning.
    - Empat PDF regulasi sudah diunggah ke Google Drive pada folder
      `MyDrive/PGABL_Dafina/data/raw/` dengan nama `PP_5_2021.pdf`,
      `PP_35_2021.pdf`, `PP_51_2023.pdf`, `UU_6_2023.pdf`.
    - **Jalankan notebook K1 lebih dulu** sehingga repositori model SFT tersedia.
"""))

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
cells.append(code("""
    !pip install -q --upgrade pip
    !pip install -q pypdf sentence-transformers faiss-cpu
    !pip install -q transformers accelerate peft bitsandbytes huggingface_hub
"""))

# ---------------------------------------------------------------------------
# Auth + konstanta
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 1. Autentikasi dan Konstanta Pipeline

    Kredensial diambil dari Colab Secrets. Seluruh angka penting pipeline (ukuran
    potongan, overlap, top-k, id model) dikumpulkan dalam satu blok agar mudah
    ditelaah reviewer.
"""))

cells.append(code("""
    import os, random
    import numpy as np
    from google.colab import userdata
    from huggingface_hub import login

    HF_TOKEN = userdata.get("HF_TOKEN")
    HF_USERNAME = userdata.get("HF_USERNAME")
    assert HF_TOKEN and HF_USERNAME, "Set HF_TOKEN & HF_USERNAME pada Colab Secrets."
    os.environ["HF_TOKEN"] = HF_TOKEN
    login(token=HF_TOKEN, add_to_git_credential=False)

    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)

    # ----- Parameter pipeline (BASIC) -----
    UKURAN_CHUNK = 700            # karakter maksimum per potongan (rubric max 5000)
    OVERLAP_CHUNK = 120          # overlap EKSPLISIT dari ekor potongan sebelumnya
    ID_EMBEDDER = "intfloat/multilingual-e5-base"
    PREFIX_PASSAGE = "passage: "  # e5 wajib prefix untuk dokumen
    PREFIX_QUERY = "query: "      # e5 wajib prefix untuk kueri
    TOP_K = 3
    DIR_INDEKS = "/content/faiss_store"

    REPO_SFT = f"{HF_USERNAME}/PGABL-Qwen2.5-1.5B-SFT-Dafina"

    print("Model generator :", REPO_SFT)
    print("Ukuran / overlap:", UKURAN_CHUNK, "/", OVERLAP_CHUNK)
    print("Top-K           :", TOP_K)
"""))

# ---------------------------------------------------------------------------
# Sumber PDF via Drive
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 2. Siapkan Sumber PDF dari Google Drive

    Notebook memverifikasi keempat berkas hadir sebelum melanjutkan. Bila ada
    yang hilang, proses berhenti dengan pesan yang jelas.
"""))

cells.append(code("""
    from google.colab import drive
    drive.mount("/content/drive", force_remount=False)

    FOLDER_PDF = "/content/drive/MyDrive/PGABL_Dafina/data/raw"
    DAFTAR_PDF = [
        ("PP_5_2021",  "PP_5_2021.pdf"),
        ("PP_35_2021", "PP_35_2021.pdf"),
        ("PP_51_2023", "PP_51_2023.pdf"),
        ("UU_6_2023",  "UU_6_2023.pdf"),
    ]

    for kode, berkas in DAFTAR_PDF:
        jalur = os.path.join(FOLDER_PDF, berkas)
        assert os.path.exists(jalur), f"PDF hilang: {jalur} (unggah dulu ke Drive)."
        print(f"[OK] {kode:<12} {os.path.getsize(jalur) / 1e6:6.2f} MB")
"""))

# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 3. Ekstraksi Teks per Halaman

    `pypdf` cepat dan stabil untuk PDF ber-*text layer*. Untuk tiap halaman kita
    simpan asal regulasi dan nomor halaman; keduanya dipakai kembali saat
    menampilkan rujukan jawaban.
"""))

cells.append(code("""
    from pypdf import PdfReader

    def baca_halaman(jalur_pdf, kode_dok):
        pembaca = PdfReader(jalur_pdf)
        keluaran = []
        for nomor, halaman in enumerate(pembaca.pages, start=1):
            teks = (halaman.extract_text() or "").strip()
            if teks:
                keluaran.append({"dok": kode_dok, "hal": nomor, "teks": teks})
        return keluaran

    daftar_halaman = []
    for kode, berkas in DAFTAR_PDF:
        isi = baca_halaman(os.path.join(FOLDER_PDF, berkas), kode)
        daftar_halaman.extend(isi)
        print(f"{kode:<12} halaman berteks: {len(isi)}")

    print("Total halaman terekstrak:", len(daftar_halaman))
"""))

# ---------------------------------------------------------------------------
# Chunker berbasis kalimat
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 4. Pemotongan Berbasis Kalimat (Overlap Eksplisit)

    Alih-alih memotong buta per sekian karakter, teks dipecah dulu menjadi
    kalimat, lalu kalimat-kalimat utuh dirangkai secara serakah (*greedy*)
    hingga panjang gabungan mendekati `UKURAN_CHUNK`. Saat sebuah potongan
    ditutup, beberapa kalimat terakhirnya (berjumlah minimal `OVERLAP_CHUNK`
    karakter) dibawa ke awal potongan berikutnya sebagai overlap. Dengan begitu
    tidak ada kalimat yang terpotong di tengah, dan besar overlap tetap
    ditentukan **eksplisit**.
"""))

cells.append(code("""
    import re

    def pecah_kalimat(teks):
        teks = re.sub(r"\\s+", " ", teks).strip()
        bagian = re.split(r"(?<=[.?!;])\\s+", teks)
        return [b.strip() for b in bagian if b.strip()]

    def rangkai_potongan(kalimat, ukuran, overlap):
        potongan, penyangga = [], []
        for kal in kalimat:
            calon = " ".join(penyangga + [kal])
            if penyangga and len(calon) > ukuran:
                potongan.append(" ".join(penyangga))
                # susun overlap dari ekor penyangga (>= overlap karakter)
                ekor, total = [], 0
                for k in reversed(penyangga):
                    if total >= overlap:
                        break
                    ekor.insert(0, k)
                    total += len(k) + 1
                # bila ekor = seluruh penyangga (kalimat sangat panjang), buang
                # overlap supaya proses tetap maju
                penyangga = [] if len(ekor) >= len(penyangga) else ekor
            penyangga.append(kal)
        if penyangga:
            potongan.append(" ".join(penyangga))
        return potongan

    korpus = []
    for baris in daftar_halaman:
        for urut, isi in enumerate(
            rangkai_potongan(pecah_kalimat(baris["teks"]), UKURAN_CHUNK, OVERLAP_CHUNK)
        ):
            korpus.append({
                "id": f"{baris['dok']}-h{baris['hal']:04d}-p{urut:02d}",
                "teks": isi,
                "dok": baris["dok"],
                "hal": baris["hal"],
            })

    print("Jumlah potongan:", len(korpus))
    print("Contoh id      :", korpus[0]["id"])
    panjang = [len(c["teks"]) for c in korpus]
    print(f"Panjang chunk  : min {min(panjang)} | "
          f"rata2 {sum(panjang) // len(panjang)} | max {max(panjang)}")
"""))

cells.append(md("""
    ### Bukti overlap antar-potongan

    Untuk membuktikan overlap benar-benar aktif, kita cari dua potongan
    berurutan dari halaman yang sama lalu bandingkan ekor potongan pertama
    dengan awal potongan kedua — sebagian kalimat akan tampak muncul di keduanya.
"""))

cells.append(code("""
    for i in range(len(korpus) - 1):
        if korpus[i]["dok"] == korpus[i + 1]["dok"] and korpus[i]["hal"] == korpus[i + 1]["hal"]:
            print("Potongan A id:", korpus[i]["id"])
            print("  ...ekor A :", korpus[i]["teks"][-140:])
            print("Potongan B id:", korpus[i + 1]["id"])
            print("  awal B    :", korpus[i + 1]["teks"][:140])
            break
"""))

# ---------------------------------------------------------------------------
# Embedder
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 5. Embedder `multilingual-e5-base`

    Model e5 multibahasa mendukung Bahasa Indonesia dan mensyaratkan prefiks
    khusus: `"passage: "` untuk dokumen dan `"query: "` untuk kueri. Vektor
    dinormalisasi agar produk-dalam (inner product) setara dengan cosine.
"""))

cells.append(code("""
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(ID_EMBEDDER, device="cuda")
    DIMENSI = embedder.get_sentence_embedding_dimension()
    print("Embedder dimuat:", ID_EMBEDDER, "| dimensi:", DIMENSI)

    teks_passage = [PREFIX_PASSAGE + c["teks"] for c in korpus]
    matriks = embedder.encode(
        teks_passage,
        batch_size=32,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype("float32")
    print("Bentuk matriks embedding:", matriks.shape)
"""))

# ---------------------------------------------------------------------------
# FAISS store
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 6. Simpan ke Indeks FAISS Lokal

    `IndexFlatIP` melakukan pencarian *exact* berbasis produk-dalam. Karena
    vektor sudah ternormalisasi, skornya identik dengan cosine similarity.
    Indeks beserta metadata potongan disimpan ke disk sebagai basis data vektor
    lokal.
"""))

cells.append(code("""
    import json
    import faiss

    indeks = faiss.IndexFlatIP(DIMENSI)
    indeks.add(matriks)
    print("Vektor dalam indeks:", indeks.ntotal)

    os.makedirs(DIR_INDEKS, exist_ok=True)
    faiss.write_index(indeks, os.path.join(DIR_INDEKS, "regulasi.faiss"))
    with open(os.path.join(DIR_INDEKS, "korpus.json"), "w", encoding="utf-8") as f:
        json.dump(korpus, f, ensure_ascii=False)
    print("Indeks + metadata tersimpan di:", DIR_INDEKS)
"""))

# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 7. Retriever Top-K Dense

    Kueri diberi prefiks `"query: "`, di-embed, lalu dicari `TOP_K` tetangga
    terdekat pada indeks FAISS. Skor produk-dalam langsung menjadi nilai
    kemiripan (semakin mendekati 1 semakin relevan).
"""))

cells.append(code("""
    def cari(pertanyaan, k=TOP_K):
        vektor = embedder.encode(
            [PREFIX_QUERY + pertanyaan],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")
        skor, indeks_hit = indeks.search(vektor, k)
        hasil = []
        for nilai, pos in zip(skor[0], indeks_hit[0]):
            if pos < 0:
                continue
            item = korpus[pos]
            hasil.append({
                "teks": item["teks"],
                "dok": item["dok"],
                "hal": item["hal"],
                "skor": float(nilai),
            })
        return hasil

    for peringkat, hit in enumerate(cari("ketentuan upah kerja lembur"), start=1):
        print(f"[{peringkat}] {hit['dok']} hal-{hit['hal']} (skor={hit['skor']:.3f})")
        print("   ", hit["teks"][:170].replace("\\n", " "), "...")
"""))

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 8. Muat Generator — Model K1 dari Hugging Face

    Model hasil SFT (`PGABL-Qwen2.5-1.5B-SFT-Dafina`) dipanggil kembali dalam
    mode 4-bit `bitsandbytes` supaya ringan di VRAM T4. Tokenizer Qwen sudah
    membawa template ChatML sehingga format prompt konsisten dengan pelatihan.
"""))

cells.append(code("""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    kuantisasi = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tok_gen = AutoTokenizer.from_pretrained(REPO_SFT, token=HF_TOKEN)
    if tok_gen.pad_token_id is None:
        tok_gen.pad_token = tok_gen.eos_token

    generator = AutoModelForCausalLM.from_pretrained(
        REPO_SFT,
        quantization_config=kuantisasi,
        device_map="auto",
        token=HF_TOKEN,
    )
    generator.eval()
    print("Generator siap:", REPO_SFT)
"""))

# ---------------------------------------------------------------------------
# RAG function
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 9. Fungsi RAG — `konteks + pertanyaan -> jawaban`

    Prompt disusun dari instruksi sistem singkat, blok konteks (tiga potongan
    teratas), lalu pertanyaan. Model diarahkan menjawab hanya berdasarkan
    konteks dan mengaku bila informasi tidak tersedia. Prompt dirender ke teks
    dulu melalui template ChatML, baru di-tokenisasi — cara ini menghindari
    perbedaan tipe kembalian `apply_chat_template` antar-versi transformers.
"""))

cells.append(code("""
    INSTRUKSI_SISTEM = (
        "Anda adalah asisten hukum untuk tim legal perusahaan. Jawablah dalam "
        "Bahasa Indonesia yang jelas dan hanya berdasarkan bagian KONTEKS. Jika "
        "konteks tidak memuat jawabannya, sampaikan bahwa informasi tidak "
        "tersedia pada dokumen yang diberikan."
    )

    def susun_konteks(potongan):
        blok = []
        for nomor, hit in enumerate(potongan, start=1):
            blok.append(
                f"[Rujukan {nomor} - {hit['dok']} halaman {hit['hal']}]\\n{hit['teks']}"
            )
        return "\\n\\n".join(blok)

    @torch.inference_mode()
    def tanya_regulasi(pertanyaan):
        potongan = cari(pertanyaan, k=TOP_K)
        konteks = susun_konteks(potongan)
        pesan = [
            {"role": "system", "content": INSTRUKSI_SISTEM},
            {"role": "user",
             "content": f"KONTEKS:\\n{konteks}\\n\\nPERTANYAAN: {pertanyaan}"},
        ]
        prompt = tok_gen.apply_chat_template(
            pesan, tokenize=False, add_generation_prompt=True,
        )
        masukan = tok_gen(prompt, return_tensors="pt").to(generator.device)
        keluaran = generator.generate(
            **masukan,
            max_new_tokens=400,
            do_sample=False,
            repetition_penalty=1.15,
            pad_token_id=tok_gen.pad_token_id,
        )
        jawaban = tok_gen.decode(
            keluaran[0][masukan["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()
        rujukan = [
            f"{h['dok']} halaman {h['hal']} (skor {h['skor']:.2f})" for h in potongan
        ]
        return {"jawaban": jawaban, "rujukan": rujukan}
"""))

# ---------------------------------------------------------------------------
# Demo batch (selalu jalan saat Run All)
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 10. Uji Beberapa Pertanyaan Contoh

    Empat pertanyaan berikut menjadi *sanity check* pipeline end-to-end. Setiap
    jawaban dan daftar rujukannya ditampilkan rapi dengan
    `IPython.display.Markdown` sehingga reviewer bisa memverifikasi grounding
    ke dokumen.
"""))

cells.append(code("""
    from IPython.display import Markdown, display

    pertanyaan_contoh = [
        "Bagaimana ketentuan upah kerja lembur bagi pekerja?",
        "Apa yang dimaksud Perizinan Berusaha Berbasis Risiko?",
        "Sebutkan komponen dalam formula penetapan upah minimum.",
        "Apa hak pekerja yang mengalami pemutusan hubungan kerja?",
    ]

    for q in pertanyaan_contoh:
        hasil = tanya_regulasi(q)
        rujukan_md = "\\n".join(f"- {r}" for r in hasil["rujukan"])
        display(Markdown(
            f"### ❓ {q}\\n\\n{hasil['jawaban']}\\n\\n**Rujukan:**\\n{rujukan_md}\\n\\n---"
        ))
"""))

# ---------------------------------------------------------------------------
# K3 interface: input() loop
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 11. Antarmuka Interaktif (`input()` Loop)

    Sesuai opsi Basic pada Kriteria 3, antarmuka dibuat sebagai *Interactive
    Python Loop*: pengguna mengetik pertanyaan, jawaban dirender dengan
    `IPython.display.Markdown`. Ketik `keluar` (atau `exit`) untuk mengakhiri
    sesi. Blok `try/except` menjaga sel tetap berakhir rapi bila dijalankan pada
    lingkungan tanpa masukan interaktif.
"""))

cells.append(code("""
    from IPython.display import Markdown, display

    def sesi_tanya_jawab():
        print("Asisten Legal Cipta Kerja — ketik 'keluar' untuk berhenti.\\n")
        while True:
            try:
                pertanyaan = input("Pertanyaan Anda: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\\nSesi diakhiri.")
                break
            if pertanyaan.lower() in {"keluar", "exit", "quit", ""}:
                print("Sesi diakhiri.")
                break
            hasil = tanya_regulasi(pertanyaan)
            rujukan_md = "\\n".join(f"- {r}" for r in hasil["rujukan"])
            display(Markdown(
                f"**Jawaban:**\\n\\n{hasil['jawaban']}\\n\\n"
                f"**Rujukan:**\\n{rujukan_md}"
            ))

    sesi_tanya_jawab()
"""))

# ---------------------------------------------------------------------------
# Ringkasan
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 12. Ringkasan Pipeline

    | Komponen | Pilihan |
    |----------|---------|
    | Loader PDF | `pypdf.PdfReader` per-halaman |
    | Chunker | Berbasis kalimat, `ukuran=700`, `overlap=120` (eksplisit) |
    | Embedder | `intfloat/multilingual-e5-base` (open-source, prefix query/passage) |
    | Vector store | FAISS `IndexFlatIP` (cosine), disimpan lokal |
    | Retriever | Top-`3` dense |
    | Generator | `PGABL-Qwen2.5-1.5B-SFT-Dafina` (hasil notebook K1) |
    | Antarmuka | Loop `input()` + `IPython.display.Markdown` |

    Pipeline ini memenuhi seluruh butir Basic pada Kriteria 2 dan Kriteria 3.
"""))

# ---------------------------------------------------------------------------
# Serialise
# ---------------------------------------------------------------------------
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "accelerator": "GPU",
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Notebook RAG ditulis: {OUT}")
print(f"Jumlah cell: {len(cells)}")
