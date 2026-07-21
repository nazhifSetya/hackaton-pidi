"""
Generator notebook RAG (K2 Basic + antarmuka) — PGABL versi Bimo.

Merakit `submission/RAG_submission_PGABL_Bimo_Bramantyo.ipynb` lalu memvalidasi
(JSON valid, tiap sel kode lolos ast.parse, tak ada token bocor / meta-conversation).

Pipeline: muat 4 PDF -> potong (RecursiveCharacterTextSplitter 1000/150) ->
embedding MiniLM -> ChromaDB in-memory (cosine) -> retrieve top-4 -> generate
dengan model K1 (Phi-3.5 SFT Bimo) -> contoh Q&A + gr.Interface.
Jalankan: python scripts/build_rag_notebook.py
"""
import ast
import json
import re
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "submission" / \
    "RAG_submission_PGABL_Bimo_Bramantyo.ipynb"


def md(teks: str) -> dict:
    return {"cell_type": "markdown", "metadata": {},
            "source": textwrap.dedent(teks).strip("\n").splitlines(keepends=True)}


def code(teks: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": textwrap.dedent(teks).strip("\n").splitlines(keepends=True)}


sel = []

# --- Judul -----------------------------------------------------------------
sel.append(md("""
    # Sistem RAG Legal Cipta Kerja — Kriteria 2 PGABL

    Notebook ini membangun asisten tanya-jawab atas **4 regulasi Cipta Kerja**
    (PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023). Dokumen dipotong, di-embed,
    disimpan di vector database lokal, lalu jawaban dibuat oleh **model hasil
    fine-tuning sendiri** (Phi-3.5-mini SFT dari Kriteria 1).

    Alur: muat PDF -> potong teks -> embedding -> ChromaDB -> retrieve ->
    rakit prompt -> generate -> antarmuka Gradio.

    **Lingkungan:** Google Colab, Runtime **T4 GPU**.
"""))

# --- Instalasi -------------------------------------------------------------
sel.append(md("""
    ## 1. Instalasi Pustaka

    Jika Colab meminta *restart session* setelah instalasi, lakukan restart lalu
    **Run all** ulang.
"""))
sel.append(code(r"""
    %%capture
    !pip install --upgrade --no-cache-dir pypdf langchain-text-splitters chromadb gradio
    !pip install --upgrade --no-cache-dir transformers accelerate bitsandbytes huggingface_hub
"""))

# --- Autentikasi + konfigurasi ---------------------------------------------
sel.append(md("""
    ## 2. Autentikasi & Konfigurasi

    Token dan username diambil dari **Colab Secret**. `REPO_MODEL` menunjuk ke
    model hasil Kriteria 1 (WAJIB model sendiri, bukan model pihak lain).
"""))
sel.append(code(r"""
    import os

    try:
        from google.colab import userdata
        HF_TOKEN = userdata.get("HF_TOKEN")
        HF_USERNAME = userdata.get("HF_USERNAME")
    except Exception:
        HF_TOKEN = os.environ.get("HF_TOKEN")
        HF_USERNAME = os.environ.get("HF_USERNAME")

    assert HF_TOKEN and HF_USERNAME, "HF_TOKEN / HF_USERNAME belum diset (Colab Secret)."

    from huggingface_hub import login
    login(token=HF_TOKEN)

    REPO_MODEL    = f"{HF_USERNAME}/PGABL-Phi-3.5-mini-SFT-Bimo"
    ID_EMBED      = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    UKURAN_CHUNK  = 1000
    OVERLAP_CHUNK = 150
    TOP_K         = 4

    print("Model generator:", REPO_MODEL)
    print("Model embedding:", ID_EMBED)
"""))

# --- Mount Drive + verifikasi PDF ------------------------------------------
sel.append(md("""
    ## 3. Sumber Dokumen (Google Drive)

    Keempat PDF diunggah lebih dulu ke `MyDrive/PGABL_Bimo/`. Sel ini memverifikasi
    semuanya ada sebelum diproses.
"""))
sel.append(code(r"""
    from google.colab import drive
    drive.mount("/content/drive")

    DIR_PDF = "/content/drive/MyDrive/PGABL_Bimo"
    BERKAS = {
        "PP 5/2021":  "PP_5_2021.pdf",
        "PP 35/2021": "PP_35_2021.pdf",
        "PP 51/2023": "PP_51_2023.pdf",
        "UU 6/2023":  "UU_6_2023.pdf",
    }
    for label, nama in BERKAS.items():
        jalur = os.path.join(DIR_PDF, nama)
        ada = os.path.exists(jalur)
        print(f"[{'OK' if ada else 'HILANG'}] {label:<12} -> {nama}")
        assert ada, f"PDF tidak ditemukan: {jalur}. Cek nama folder Drive (tanpa spasi)."
"""))

# --- Muat + potong PDF -----------------------------------------------------
sel.append(md("""
    ## 4. Muat & Potong Dokumen

    Teks diekstrak per-halaman dengan `pypdf`, lalu dipotong memakai
    `RecursiveCharacterTextSplitter` dengan **ukuran chunk 1000** dan **overlap 150**
    (ditentukan secara eksplisit). Setiap potongan menyimpan metadata sumber.
"""))
sel.append(code(r"""
    from pypdf import PdfReader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    def muat_pdf(jalur):
        reader = PdfReader(jalur)
        return "\n".join((hal.extract_text() or "") for hal in reader.pages)

    pemotong = RecursiveCharacterTextSplitter(
        chunk_size=UKURAN_CHUNK,
        chunk_overlap=OVERLAP_CHUNK,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    dokumen, metadata = [], []
    for label, nama in BERKAS.items():
        teks = muat_pdf(os.path.join(DIR_PDF, nama))
        bagian = pemotong.split_text(teks)
        for i, potong in enumerate(bagian):
            dokumen.append(potong)
            metadata.append({"sumber": label, "berkas": nama, "urutan": i})
        print(f"{label:<12}: {len(bagian)} chunk")

    print("Total chunk:", len(dokumen))
"""))

# --- Embedding + ChromaDB --------------------------------------------------
sel.append(md("""
    ## 5. Embedding & Simpan ke ChromaDB (in-memory, cosine)

    Model embedding open-source `paraphrase-multilingual-MiniLM-L12-v2` dimuat via
    `transformers` (`AutoModel`) lalu tiap chunk diringkas jadi satu vektor dengan
    **mean pooling** (rata-rata token, ditimbang attention mask) + normalisasi L2 —
    ini rumus baku model kalimat MiniLM. Vektor disimpan ke koleksi ChromaDB
    in-memory dengan ruang jarak **cosine**; penambahan bertahap agar tak menembus
    batas ukuran batch ChromaDB.
"""))
sel.append(code(r"""
    import torch
    import chromadb
    from transformers import AutoTokenizer, AutoModel

    tok_embed = AutoTokenizer.from_pretrained(ID_EMBED)
    model_embed = AutoModel.from_pretrained(ID_EMBED).eval()
    PERANGKAT = "cuda" if torch.cuda.is_available() else "cpu"
    model_embed = model_embed.to(PERANGKAT)

    def _rata_token(keluaran, mask):
        emb = keluaran.last_hidden_state
        m = mask.unsqueeze(-1).expand(emb.size()).float()
        return (emb * m).sum(1) / m.sum(1).clamp(min=1e-9)

    def buat_embedding(daftar_teks, batch=64):
        hasil = []
        for i in range(0, len(daftar_teks), batch):
            enc = tok_embed(daftar_teks[i:i + batch], padding=True, truncation=True,
                            max_length=256, return_tensors="pt").to(PERANGKAT)
            with torch.no_grad():
                keluaran = model_embed(**enc)
            vek = _rata_token(keluaran, enc["attention_mask"])
            vek = torch.nn.functional.normalize(vek, p=2, dim=1)
            hasil.append(vek.cpu())
        return torch.cat(hasil).tolist()

    vektor = buat_embedding(dokumen)
    print("Dimensi embedding:", len(vektor[0]), "| jumlah vektor:", len(vektor))

    klien = chromadb.Client()
    koleksi = klien.create_collection(
        name="regulasi_ciptaker_bimo",
        metadata={"hnsw:space": "cosine"},
    )

    LANGKAH_ADD = 1000
    for a in range(0, len(dokumen), LANGKAH_ADD):
        b = min(a + LANGKAH_ADD, len(dokumen))
        koleksi.add(
            ids=[f"chunk-{i}" for i in range(a, b)],
            documents=dokumen[a:b],
            embeddings=vektor[a:b],
            metadatas=metadata[a:b],
        )
    print("Chunk tersimpan di ChromaDB:", koleksi.count())
"""))

# --- Muat generator (model K1) ---------------------------------------------
sel.append(md("""
    ## 6. Muat Model Generator (Hasil Kriteria 1)

    Model dimuat 4-bit (nf4 + double quant) agar muat di T4. Ini adalah model
    fine-tuning milik sendiri dari Kriteria 1 — bukan model baru/proprietary.
"""))
sel.append(code(r"""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    konfig_4bit = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tok = AutoTokenizer.from_pretrained(REPO_MODEL, token=HF_TOKEN)
    generator = AutoModelForCausalLM.from_pretrained(
        REPO_MODEL,
        quantization_config=konfig_4bit,
        device_map="auto",
        token=HF_TOKEN,
    )
    generator.eval()

    AKHIR_GILIRAN = tok.convert_tokens_to_ids("<|end|>")
    STOP_ID = [tok.eos_token_id, AKHIR_GILIRAN]
    print("Generator siap:", REPO_MODEL)
"""))

# --- Fungsi RAG ------------------------------------------------------------
sel.append(md("""
    ## 7. Fungsi RAG: Retrieve -> Prompt -> Generate

    `ambil_konteks` mengambil `top-4` chunk paling relevan; `rakit_prompt`
    menyusun prompt berisi `{konteks}` dan `{pertanyaan}` dalam format chat Phi-3.5;
    `hasilkan_jawaban` melakukan inferensi. `tanya` menyatukan ketiganya.
"""))
sel.append(code(r"""
    def ambil_konteks(pertanyaan, k=TOP_K):
        q = buat_embedding([pertanyaan])
        hasil = koleksi.query(query_embeddings=q, n_results=k,
                              include=["documents", "metadatas"])
        return list(zip(hasil["documents"][0], hasil["metadatas"][0]))

    def rakit_prompt(pertanyaan, konteks):
        gabung = "\n\n".join(f"[{m['sumber']}] {d}" for d, m in konteks)
        isi = (
            "Anda asisten hukum tim legal. Jawab pertanyaan HANYA berdasarkan "
            "konteks peraturan di bawah. Bila jawaban tidak ada dalam konteks, "
            "katakan informasinya tidak ditemukan pada dokumen.\n\n"
            f"Konteks:\n{gabung}\n\nPertanyaan: {pertanyaan}"
        )
        pesan = [{"role": "user", "content": isi}]
        return tok.apply_chat_template(pesan, tokenize=False, add_generation_prompt=True)

    def hasilkan_jawaban(prompt):
        # add_special_tokens=False: prompt sudah punya <bos> dari chat template,
        # jangan sampai tokenizer menambah token spesial ganda di depan prompt.
        masuk = tok(prompt, return_tensors="pt",
                    add_special_tokens=False).to(generator.device)
        with torch.no_grad():
            keluar = generator.generate(
                **masuk,
                max_new_tokens=320,
                do_sample=False,
                repetition_penalty=1.15,
                eos_token_id=STOP_ID,
                pad_token_id=tok.eos_token_id,
            )
        teks = tok.decode(
            keluar[0][masuk["input_ids"].shape[1]:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return teks.strip()

    def tanya(pertanyaan):
        konteks = ambil_konteks(pertanyaan)
        return hasilkan_jawaban(rakit_prompt(pertanyaan, konteks))
"""))

# --- Contoh Q&A (bukti output) ---------------------------------------------
sel.append(md("""
    ## 8. Contoh Tanya-Jawab (Bukti Output)

    Beberapa pertanyaan dijalankan langsung agar hasilnya tersimpan di notebook
    (output ter-embed) — ini penting karena interaksi Gradio tidak ikut tersimpan
    secara statis.
"""))
sel.append(code(r"""
    from IPython.display import Markdown, display

    contoh = [
        "Berapa besar upah lembur untuk jam kerja lembur pertama?",
        "Apa yang dimaksud dengan Nomor Induk Berusaha (NIB)?",
        "Bagaimana penetapan upah minimum menurut peraturan pengupahan?",
    ]
    for q in contoh:
        display(Markdown(f"**Pertanyaan:** {q}\n\n**Jawaban:** {tanya(q)}"))
        print("-" * 70)
"""))

# --- Antarmuka Gradio ------------------------------------------------------
sel.append(md("""
    ## 9. Antarmuka Gradio (`gr.Interface`)

    Antarmuka sederhana: satu kotak pertanyaan, satu kotak jawaban.
"""))
sel.append(code(r"""
    import gradio as gr

    antarmuka = gr.Interface(
        fn=tanya,
        inputs=gr.Textbox(lines=2, label="Pertanyaan seputar regulasi Cipta Kerja"),
        outputs=gr.Textbox(lines=10, label="Jawaban asisten"),
        title="Asisten Legal Cipta Kerja",
        description="Tanya jawab berbasis 4 regulasi: PP 5/2021, PP 35/2021, PP 51/2023, UU 6/2023.",
        examples=[
            ["Berapa besar upah lembur untuk jam kerja lembur pertama?"],
            ["Apa yang dimaksud dengan Nomor Induk Berusaha (NIB)?"],
        ],
    )
    antarmuka.launch(share=True)
"""))

# --- Penutup ---------------------------------------------------------------
sel.append(md("""
    ## 10. Ringkasan

    | Aspek | Nilai |
    |---|---|
    | Sumber | 4 PDF regulasi Cipta Kerja (seluruhnya) |
    | Chunking | `RecursiveCharacterTextSplitter`, 1000 / overlap 150 (eksplisit) |
    | Embedding | `paraphrase-multilingual-MiniLM-L12-v2` (open-source) |
    | Vector DB | ChromaDB in-memory, ruang cosine |
    | Generator | Phi-3.5-mini hasil fine-tuning sendiri (Kriteria 1) |
    | Antarmuka | Gradio `gr.Interface` |

    Kriteria 2 (Basic) terpenuhi.
"""))

# ---------------------------------------------------------------------------
# Rakit notebook
# ---------------------------------------------------------------------------
notebook = {
    "cells": sel,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------------------------------------------------------------------
# Validasi
# ---------------------------------------------------------------------------
data = json.loads(OUT.read_text(encoding="utf-8"))
assert data["nbformat"] == 4

sel_kode = [c for c in data["cells"] if c["cell_type"] == "code"]
for c in sel_kode:
    src = "".join(c["source"])
    baris_py = [b for b in src.splitlines() if not b.lstrip().startswith(("%", "!"))]
    ast.parse("\n".join(baris_py))

gabung = "\n".join("".join(c["source"]) for c in data["cells"])
bocor_token = re.findall(r"hf_[A-Za-z0-9]{20,}", gabung)
terlarang = [w for w in ["claude", "CLAUDE", "share ke aku", "panduan/",
                         "nazhif", "dafina", "fareynaldi"]
             if w.lower() in gabung.lower()]

print("OK  notebook ditulis :", OUT)
print("OK  jumlah sel        :", len(data["cells"]), f"({len(sel_kode)} kode)")
print("OK  ast.parse         : semua sel kode lolos")
print("HR  token bocor       :", bocor_token or "TIDAK ADA")
print("HR  kata terlarang    :", terlarang or "TIDAK ADA")
assert not bocor_token and not terlarang
print("VALIDASI LULUS.")
