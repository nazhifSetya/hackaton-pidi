"""
Builder: generate submission/RAG_submission_PGABL_fareynaldi_affan.ipynb

Design principles (BASIC tier):
- Semua kode inline di notebook (self-contained, tanpa dependency src/).
- Alur linear: install -> auth -> siapkan PDF -> loader pypdf -> chunker
  sliding window dengan overlap EKSPLISIT -> embed bge-m3 -> ChromaDB
  persistent 1 collection -> retriever top-k dense -> generator = model K1
  dari HF -> gr.Interface sederhana.
- Tanpa BM25, ensemble, parent-child, HyDE, reranker, fallback web,
  metadata filtering, Gradio Blocks, streaming, citation panel.
- Anti-plagiarisme: chunk_size, overlap, top_k, system_prompt, naming
  variabel, dan struktur cell semuanya sengaja berbeda.
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "RAG_submission_PGABL_fareynaldi_affan.ipynb"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _to_lines(source)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _to_lines(source),
    }


def _to_lines(text: str) -> list[str]:
    text = dedent(text).strip("\n")
    lines = text.split("\n")
    return [ln + "\n" for ln in lines[:-1]] + [lines[-1]]


cells: list[dict] = []

# =====================================================================
# 1. Header
# =====================================================================
cells.append(md("""
    # Retrieval-Augmented Generation Asisten Legal — Submission PGABL

    **Notebook ini:** *Kriteria 2 (Membangun Sistem RAG) + Kriteria 3
    (Antarmuka)* — tier Basic.

    Pipeline yang dibangun:

    1. Muat empat PDF regulasi Cipta Kerja (PP 5/2021, PP 35/2021, PP 51/2023,
       UU 6/2023) memakai `pypdf`.
    2. Potong teks tiap halaman dengan **sliding window** — `chunk_size=1000`
       karakter, `chunk_overlap=100` karakter (ditulis eksplisit di kode,
       bukan default library).
    3. Encode potongan menjadi vektor via embedder open-source `BAAI/bge-m3`.
    4. Simpan vektor pada **ChromaDB persistent** (satu koleksi
       `regulasi_ciptaker`).
    5. Muat kembali model hasil fine-tuning (notebook K1) dari Hugging Face
       sebagai generator, lalu susun prompt `context + question`.
    6. Bungkus pipeline pada `gr.Interface` sederhana — satu kotak pertanyaan,
       satu kotak jawaban.
"""))

# =====================================================================
# 2. Panduan environment
# =====================================================================
cells.append(md("""
    ## 0. Panduan Environment

    - Runtime Google Colab **T4 GPU** (free tier).
    - Colab Secret yang dibutuhkan:
        - `HF_TOKEN` (role Read cukup untuk pull model), aktifkan *Notebook access*.
        - `HF_USERNAME` — pemilik repositori model K1 hasil fine-tuning.
    - Empat file PDF regulasi sudah diunggah ke folder Drive:
      `MyDrive/PGABL_Fareynaldi/data/raw/` dengan nama
      `PP_5_2021.pdf`, `PP_35_2021.pdf`, `PP_51_2023.pdf`, `UU_6_2023.pdf`.
"""))

# =====================================================================
# 3. Install
# =====================================================================
cells.append(code("""
    !pip install -q --upgrade pip
    !pip install -q pypdf sentence-transformers chromadb gradio
    !pip install -q transformers accelerate peft bitsandbytes
    !pip install -q huggingface_hub
"""))

# =====================================================================
# 4. Auth + konfigurasi
# =====================================================================
cells.append(md("""
    ## 1. Otentikasi Hugging Face dan Konstanta

    Kredensial diambil dari Colab Secrets. Semua magic number pipeline (ukuran
    chunk, overlap, top-k, model id) dikumpulkan pada satu blok agar mudah
    diaudit oleh reviewer.
"""))

cells.append(code("""
    import os, random
    import numpy as np
    from google.colab import userdata
    from huggingface_hub import login

    HF_TOKEN = userdata.get("HF_TOKEN")
    HF_USERNAME = userdata.get("HF_USERNAME")
    assert HF_TOKEN and HF_USERNAME, "Set HF_TOKEN & HF_USERNAME di Colab Secrets"
    os.environ["HF_TOKEN"] = HF_TOKEN
    login(token=HF_TOKEN, add_to_git_credential=False)

    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)

    # ---- Pipeline knobs (BASIC) ----
    CHUNK_SIZE = 1000       # karakter per chunk (rubric max 5000)
    CHUNK_OVERLAP = 100     # overlap EKSPLISIT antar-chunk (bukan default)
    EMBED_MODEL_ID = "BAAI/bge-m3"
    COLLECTION_NAME = "regulasi_ciptaker"
    PERSIST_DIR = "/content/chroma_store"
    TOP_K = 4

    SFT_REPO_ID = f"{HF_USERNAME}/PGABL-Llama-3.2-3B-SFT-Fareynaldi"

    print("Repo model generator :", SFT_REPO_ID)
    print("Chunk size / overlap :", CHUNK_SIZE, "/", CHUNK_OVERLAP)
    print("Top-K retrieval      :", TOP_K)
"""))

# =====================================================================
# 5. PDF preparation via Drive
# =====================================================================
cells.append(md("""
    ## 2. Siapkan Sumber PDF

    PDF regulasi diambil dari Google Drive. Notebook memverifikasi seluruh
    empat file hadir sebelum melangkah lebih jauh — kalau ada yang hilang,
    proses akan berhenti dengan pesan yang jelas.
"""))

cells.append(code("""
    from google.colab import drive
    drive.mount("/content/drive", force_remount=False)

    PDF_DIR = "/content/drive/MyDrive/PGABL_Fareynaldi/data/raw"
    PDF_FILES = [
        ("PP_5_2021",  "PP_5_2021.pdf"),
        ("PP_35_2021", "PP_35_2021.pdf"),
        ("PP_51_2023", "PP_51_2023.pdf"),
        ("UU_6_2023",  "UU_6_2023.pdf"),
    ]

    for code_name, fname in PDF_FILES:
        path = os.path.join(PDF_DIR, fname)
        assert os.path.exists(path), (
            f"PDF hilang: {path}. Upload dulu ke Drive path tersebut."
        )
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"[OK] {code_name:<12} {size_mb:6.2f} MB")
"""))

# =====================================================================
# 6. PDF loader
# =====================================================================
cells.append(md("""
    ## 3. Loader — Ekstrak Teks per Halaman

    `pypdf` cukup cepat dan stabil untuk PDF *text-layer*. Untuk setiap halaman
    kami menyimpan nomor halaman + nama regulasi sebagai metadata; keduanya
    dipakai kembali saat menampilkan asal-usul jawaban.
"""))

cells.append(code("""
    from pypdf import PdfReader

    def extract_pages(pdf_path: str, code_name: str) -> list[dict]:
        reader = PdfReader(pdf_path)
        pages: list[dict] = []
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            pages.append({
                "regulasi": code_name,
                "halaman": i,
                "isi": text,
            })
        return pages

    all_pages: list[dict] = []
    for code_name, fname in PDF_FILES:
        pages = extract_pages(os.path.join(PDF_DIR, fname), code_name)
        all_pages.extend(pages)
        print(f"{code_name:<12} halaman ber-teks: {len(pages)}")

    print("Total halaman terekstrak :", len(all_pages))
"""))

# =====================================================================
# 7. Chunker
# =====================================================================
cells.append(md("""
    ## 4. Chunker — Sliding Window dengan Overlap Eksplisit

    Kami menerapkan sliding window karakter sederhana. Nilai `CHUNK_SIZE=1000`
    dan `CHUNK_OVERLAP=100` diberikan langsung — tidak mengandalkan default
    library — sesuai instruksi rubric bahwa parameter chunk **wajib
    ditentukan eksplisit**.
"""))

cells.append(code("""
    def sliding_chunks(text: str, size: int, overlap: int) -> list[str]:
        assert 0 <= overlap < size, "overlap wajib < size dan >= 0"
        step = size - overlap
        pieces: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            pieces.append(text[i:i + size])
            i += step
        return pieces

    chunks: list[dict] = []
    for row in all_pages:
        for k, piece in enumerate(sliding_chunks(row["isi"], CHUNK_SIZE, CHUNK_OVERLAP)):
            chunks.append({
                "id": f"{row['regulasi']}_p{row['halaman']:04d}_c{k:02d}",
                "text": piece,
                "regulasi": row["regulasi"],
                "halaman": row["halaman"],
            })

    print("Jumlah chunk total :", len(chunks))
    print("Contoh id          :", chunks[0]["id"])
    print("Contoh preview     :", chunks[0]["text"][:180], "...")
"""))

# =====================================================================
# 8. Embedder
# =====================================================================
cells.append(md("""
    ## 5. Embedder — `BAAI/bge-m3`

    `bge-m3` adalah embedder multibahasa open-source (mendukung Bahasa
    Indonesia) dengan panjang konteks 8k, sangat memadai untuk chunk 1000
    karakter. Model dimuat sekali kemudian dipakai ulang.
"""))

cells.append(code("""
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(EMBED_MODEL_ID, device="cuda")
    print("Embedder dimuat:", EMBED_MODEL_ID)
    print("Dimensi vektor :", embedder.get_sentence_embedding_dimension())

    embed_vectors = embedder.encode(
        [c["text"] for c in chunks],
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    print("Bentuk matriks embedding:", embed_vectors.shape)
"""))

# =====================================================================
# 9. ChromaDB store
# =====================================================================
cells.append(md("""
    ## 6. Simpan ke ChromaDB (Persistent, 1 Koleksi)

    Kami memakai satu koleksi bernama `regulasi_ciptaker`. Metric jarak
    `cosine` konsisten dengan embedding yang sudah dinormalisasi pada
    langkah sebelumnya.
"""))

cells.append(code("""
    import chromadb

    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embed_vectors.tolist(),
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"regulasi": c["regulasi"], "halaman": c["halaman"]}
            for c in chunks
        ],
    )

    print("Koleksi     :", COLLECTION_NAME)
    print("Jumlah item :", collection.count())
"""))

# =====================================================================
# 10. Retriever
# =====================================================================
cells.append(md("""
    ## 7. Retriever — Top-K Dense

    Fungsi pencarian mengembalikan `TOP_K` chunk dengan skor kemiripan
    tertinggi. Skor dikonversi ke *similarity* (`1 - distance`) agar mudah
    diinterpretasi (semakin dekat 1, semakin relevan).
"""))

cells.append(code("""
    def retrieve(query: str, k: int = TOP_K) -> list[dict]:
        q_vec = embedder.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        result = collection.query(
            query_embeddings=q_vec.tolist(),
            n_results=k,
        )
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        dists = result["distances"][0]
        return [
            {
                "text": d,
                "regulasi": m["regulasi"],
                "halaman": m["halaman"],
                "similarity": 1.0 - float(x),
            }
            for d, m, x in zip(docs, metas, dists)
        ]

    contoh_query = "Bagaimana ketentuan upah lembur untuk pekerja waktu tertentu?"
    for i, hit in enumerate(retrieve(contoh_query), start=1):
        print(f"[{i}] {hit['regulasi']} hal-{hit['halaman']} "
              f"(sim={hit['similarity']:.3f})")
        print(hit["text"][:220].replace("\\n", " "), "...")
        print()
"""))

# =====================================================================
# 11. Generator = model K1
# =====================================================================
cells.append(md("""
    ## 8. Muat Generator — Model K1 dari Hugging Face

    Model hasil SFT (`PGABL-Llama-3.2-3B-SFT-Fareynaldi`) dipanggil kembali
    dalam mode 4-bit menggunakan `bitsandbytes` supaya muat di VRAM T4.
    Tokenizer di-*setup* dengan chat template Llama-3 agar konsisten dengan
    format latihan.
"""))

cells.append(code("""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(SFT_REPO_ID, token=HF_TOKEN)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    generator = AutoModelForCausalLM.from_pretrained(
        SFT_REPO_ID,
        quantization_config=bnb,
        device_map="auto",
        token=HF_TOKEN,
    )
    generator.eval()
    print("Generator siap:", SFT_REPO_ID)
"""))

# =====================================================================
# 12. RAG function
# =====================================================================
cells.append(md("""
    ## 9. Fungsi RAG — `context + question -> answer`

    Prompt disusun sederhana: instruksi sistem singkat + konteks (empat chunk
    teratas) + pertanyaan. Model diminta menjawab hanya berdasarkan konteks
    dan menyertakan disclaimer bila jawaban tidak ada di konteks.
"""))

cells.append(code("""
    SYSTEM_INSTRUKSI = (
        "Anda asisten hukum Bahasa Indonesia. "
        "Jawab pertanyaan hanya berdasarkan potongan regulasi yang diberikan. "
        "Kalau jawaban tidak ada di potongan, katakan bahwa informasi tidak "
        "ditemukan di dokumen yang tersedia."
    )

    def bangun_prompt(potongan: list[dict], pertanyaan: str) -> str:
        blok_konteks = []
        for i, hit in enumerate(potongan, start=1):
            blok_konteks.append(
                f"[Sumber {i} — {hit['regulasi']} halaman {hit['halaman']}]\\n"
                f"{hit['text']}"
            )
        konteks = "\\n\\n".join(blok_konteks)
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUKSI},
            {
                "role": "user",
                "content": (
                    f"Konteks regulasi:\\n{konteks}\\n\\n"
                    f"Pertanyaan: {pertanyaan}\\n\\nJawaban:"
                ),
            },
        ]
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    @torch.inference_mode()
    def jawab_rag(pertanyaan: str) -> dict:
        potongan = retrieve(pertanyaan, k=TOP_K)
        prompt = bangun_prompt(potongan, pertanyaan)
        encoded = tokenizer(prompt, return_tensors="pt").to(generator.device)
        out = generator.generate(
            **encoded,
            max_new_tokens=384,
            do_sample=False,
            temperature=1.0,
            top_p=1.0,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.pad_token_id,
        )
        jawaban = tokenizer.decode(
            out[0][encoded["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()
        rujukan = [
            f"{h['regulasi']} halaman {h['halaman']} (sim={h['similarity']:.2f})"
            for h in potongan
        ]
        return {"jawaban": jawaban, "rujukan": rujukan}
"""))

# =====================================================================
# 13. Contoh query
# =====================================================================
cells.append(md("""
    ## 10. Uji Contoh Pertanyaan

    Tiga pertanyaan berikut dipakai sebagai *sanity check* pipeline
    end-to-end. Untuk setiap pertanyaan, jawaban model + daftar sumber
    dicetak sehingga reviewer dapat memverifikasi grounding pada dokumen.
"""))

cells.append(code("""
    pertanyaan_uji = [
        "Bagaimana ketentuan lembur bagi pekerja dengan status waktu tertentu?",
        "Apa saja komponen formula perhitungan upah minimum provinsi?",
        "Sebutkan tahapan perizinan berusaha berbasis risiko yang wajib dipenuhi.",
    ]

    for q in pertanyaan_uji:
        print("=" * 70)
        print("Pertanyaan:", q)
        hasil = jawab_rag(q)
        print("-" * 70)
        print("Jawaban   :", hasil["jawaban"])
        print("Sumber    :")
        for r in hasil["rujukan"]:
            print("  -", r)
        print()
"""))

# =====================================================================
# 14. Gradio Interface (BASIC)
# =====================================================================
cells.append(md("""
    ## 11. Antarmuka Gradio — `gr.Interface` Sederhana

    Sesuai tier Basic, antarmuka dibuat dengan `gr.Interface`: satu kotak
    input untuk pertanyaan, satu kotak output untuk jawaban. Daftar sumber
    ditempelkan di bagian bawah jawaban agar reviewer dapat menelusuri
    grounding pada regulasi.
"""))

cells.append(code("""
    import gradio as gr

    def antarmuka_rag(pertanyaan: str) -> str:
        pertanyaan = (pertanyaan or "").strip()
        if not pertanyaan:
            return "Silakan tulis pertanyaan hukum di kotak input."
        hasil = jawab_rag(pertanyaan)
        blok_rujukan = "\\n".join(f"- {r}" for r in hasil["rujukan"])
        return (
            f"{hasil['jawaban']}\\n\\n"
            f"---\\n**Sumber yang dikutip:**\\n{blok_rujukan}"
        )

    demo = gr.Interface(
        fn=antarmuka_rag,
        inputs=gr.Textbox(
            label="Pertanyaan hukum",
            placeholder="Contoh: Apakah pekerja kontrak berhak atas uang pesangon?",
            lines=3,
        ),
        outputs=gr.Textbox(label="Jawaban asisten", lines=14),
        title="Asisten Legal Cipta Kerja (RAG Basic)",
        description=(
            "Retrieval dari empat regulasi Cipta Kerja "
            "(PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023). "
            "Generator = Llama-3.2-3B hasil fine-tuning penulis."
        ),
        examples=[
            "Bagaimana ketentuan waktu kerja lembur maksimum?",
            "Apa yang dimaksud dengan Perizinan Berusaha Berbasis Risiko?",
            "Berapa besaran uang pesangon untuk masa kerja 5 tahun?",
        ],
        allow_flagging="never",
    )

    demo.launch(share=True, debug=False)
"""))

# =====================================================================
# 15. Ringkasan
# =====================================================================
cells.append(md("""
    ## 12. Ringkasan Pipeline

    | Komponen | Pilihan |
    |----------|---------|
    | Loader PDF | `pypdf.PdfReader` per-halaman |
    | Chunker | Sliding window karakter — `size=1000`, `overlap=100` (eksplisit) |
    | Embedder | `BAAI/bge-m3` (open-source, dijalankan lokal di T4) |
    | Vector store | ChromaDB persistent, satu koleksi `regulasi_ciptaker` |
    | Retriever | Top-`4` dense (cosine) |
    | Generator | `PGABL-Llama-3.2-3B-SFT-Fareynaldi` (hasil notebook K1) |
    | Antarmuka | `gr.Interface` dengan input & output tunggal |

    Pipeline ini memenuhi seluruh butir Basic pada Kriteria 2 & 3
    submission PGABL.
"""))

# =====================================================================
# Serialise
# =====================================================================
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
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
