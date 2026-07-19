"""
Builder: generate submission/Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb

Karakter implementasi (BASIC tier, ditulis independen):
- Base model keluarga Qwen (Qwen2.5-1.5B-Instruct, lisensi Apache-2.0) dengan
  chat template ChatML -> special token <|im_start|> / <|im_end|>.
- Alur linear satu eksperimen (tanpa hyperparameter search / eval split).
- Semua konstanta ditaruh di satu blok agar notebook self-contained.
- Push pola dua langkah (save_pretrained_merged + HfApi.upload_folder) untuk
  menghindari bug safe_serialization pada push_to_hub_merged Unsloth mutakhir.

Regenerate:  python scripts/build_sft_notebook.py
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "Fine-tuning_submission_PGABL_Dafina_Meira_Rizkia.ipynb"


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
    # Fine-tuning SLM Qwen2.5-1.5B — Submission PGABL

    **Proyek:** Asisten AI tim legal berbasis SLM hasil fine-tuning + RAG.
    **Notebook ini:** *Kriteria 1 — Fine-tuning LLM Anda Sendiri* (tier Basic).

    Ringkasan tahap yang dijalankan notebook:

    1. Muat model dasar `unsloth/Qwen2.5-1.5B-Instruct` pada mode **QLoRA 4-bit**
       (double quantization, tipe kuantisasi `nf4`, komputasi `bfloat16`).
    2. Sisipkan adapter **LoRA** pada dua komponen komputasi utama Transformer:
       Multi-Head Attention (`q_proj, k_proj, v_proj, o_proj`) dan Feed-Forward
       Network (`gate_proj, up_proj, down_proj`).
    3. Ambil dataset instruksi Bahasa Indonesia `Ichsan2895/alpaca-gpt4-indonesian`,
       ubah ke format percakapan **ChatML** lewat `datasets.map()`, lalu cetak
       satu baris hasil pemetaan lengkap dengan token spesialnya.
    4. Latih dengan `SFTTrainer` sebanyak **800 langkah**.
    5. Gabungkan (merge) adapter ke bobot dasar, lalu unggah sebagai repositori
       Hugging Face publik dengan format `merged_16bit`.

    Model keluaran inilah yang nanti dipanggil sebagai generator pada pipeline
    RAG di notebook kedua.
"""))

# ---------------------------------------------------------------------------
# Panduan environment
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 0. Persiapan Lingkungan

    - **Runtime:** Google Colab, pilih `Runtime -> Change runtime type -> T4 GPU`
      (free tier, 16 GB VRAM). GPU lokal 4-8 GB umumnya tidak cukup untuk melatih
      model 1,5 miliar parameter selama 800 langkah.
    - **Colab Secrets** (ikon gembok pada sidebar kiri):
        - `HF_TOKEN` — token Hugging Face beperan **Write** untuk mengunggah model.
        - `HF_USERNAME` — nama akun Hugging Face pemilik repositori.
      Aktifkan sakelar *Notebook access* pada kedua secret.
    - **Reproduksibilitas:** seluruh operasi acak diberi seed `42`.
    - Bila di tengah instalasi Colab meminta *restart session*, jalankan
      `Runtime -> Restart session` lalu **Run all** dari awal.
"""))

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
cells.append(code("""
    # Stack Unsloth + TRL sengaja dibiarkan tanpa pin versi manual. Rilis Unsloth
    # terbaru menuntut transformers >= 4.51 sehingga pin manual pada transformers
    # / trl / datasets kerap memicu ImportError (CompileConfig) di Colab. Unsloth
    # dipasang lebih dulu agar ia yang menentukan versi transformers yang cocok.
    !pip install -q --upgrade pip
    !pip install -q "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" trl peft accelerate bitsandbytes datasets huggingface_hub
"""))

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 1. Autentikasi Hugging Face

    Kredensial dibaca dari Colab Secrets sehingga tidak pernah tertulis eksplisit
    pada notebook. Bila salah satu secret belum diisi, sel di bawah berhenti
    dengan pesan yang jelas.
"""))

cells.append(code("""
    import os
    from google.colab import userdata
    from huggingface_hub import login, whoami

    HF_TOKEN = userdata.get("HF_TOKEN")
    HF_USERNAME = userdata.get("HF_USERNAME")

    assert HF_TOKEN, "Colab Secret 'HF_TOKEN' belum di-set."
    assert HF_USERNAME, "Colab Secret 'HF_USERNAME' belum di-set."

    os.environ["HF_TOKEN"] = HF_TOKEN
    login(token=HF_TOKEN, add_to_git_credential=False)
    print("Terautentikasi sebagai :", whoami(token=HF_TOKEN).get("name"))
    print("Pemilik repositori     :", HF_USERNAME)
"""))

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 2. Parameter Pelatihan

    Nilai-nilai berikut disetel supaya 800 langkah pelatihan aman berjalan pada
    Colab T4 untuk Qwen2.5-1.5B mode 4-bit. Panjang urutan 1024 token menampung
    mayoritas pasangan instruksi-jawaban pada dataset.
"""))

cells.append(code("""
    import random
    import numpy as np
    import torch

    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    MODEL_DASAR = "unsloth/Qwen2.5-1.5B-Instruct"
    PANJANG_URUTAN = 1024
    PERINGKAT_LORA = 8
    ALPHA_LORA = 32
    DROPOUT_LORA = 0.05
    LAJU_BELAJAR = 2e-4
    JUMLAH_LANGKAH = 800
    BATCH_PER_GPU = 2
    AKUMULASI_GRADIEN = 8          # effective batch = 2 x 8 = 16
    UKURAN_SUBSET = 8000

    NAMA_REPO = "PGABL-Qwen2.5-1.5B-SFT-Dafina"
    REPO_TUJUAN = f"{HF_USERNAME}/{NAMA_REPO}"

    print("Model dasar      :", MODEL_DASAR)
    print("Repositori tujuan:", REPO_TUJUAN)
    print("Akselerator      :",
          torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
"""))

# ---------------------------------------------------------------------------
# Load model
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 3. Muat Model Dasar (QLoRA 4-bit)

    `FastLanguageModel.from_pretrained` dengan `load_in_4bit=True` sudah
    mengaktifkan kuantisasi `nf4` + double quantization secara internal, sehingga
    bobot 1,5 miliar parameter muat nyaman pada VRAM 16 GB.
"""))

cells.append(code("""
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_DASAR,
        max_seq_length=PANJANG_URUTAN,
        dtype=None,              # auto -> bfloat16 di T4
        load_in_4bit=True,       # QLoRA (nf4 + double quant otomatis)
    )
    print("Model 4-bit dimuat:", MODEL_DASAR)
    print("Panjang urutan    :", PANJANG_URUTAN)
"""))

# ---------------------------------------------------------------------------
# LoRA
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 4. Pasang Adapter LoRA (MHA + FFN)

    Adapter LoRA ditempatkan pada tujuh proyeksi agar menyentuh **kedua**
    komponen komputasi utama: Multi-Head Attention (`q, k, v, o`) dan
    Feed-Forward Network (`gate, up, down`). Peringkat kecil (r=8) dengan
    `alpha=32` memberi skala pembaruan yang memadai untuk membentuk gaya jawaban
    formal Bahasa Indonesia tanpa memberatkan VRAM.
"""))

cells.append(code("""
    model = FastLanguageModel.get_peft_model(
        model,
        r=PERINGKAT_LORA,
        lora_alpha=ALPHA_LORA,
        lora_dropout=DROPOUT_LORA,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",    # Multi-Head Attention
            "gate_proj", "up_proj", "down_proj",         # Feed-Forward Network
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=SEED,
    )

    dilatih = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Parameter dilatih : {dilatih:,}")
    print(f"Parameter total   : {total:,}")
    print(f"Porsi dilatih     : {dilatih / total:.4%}")
"""))

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 5. Muat Dataset Instruksi Bahasa Indonesia

    `Ichsan2895/alpaca-gpt4-indonesian` hanya memiliki dua kolom: `input`
    (instruksi/pertanyaan) dan `output` (jawaban). Baris yang terlalu pendek
    disaring supaya model belajar pola jawaban yang bermakna, lalu diambil
    sub-sampel acak sebanyak `UKURAN_SUBSET` baris — cukup untuk memenuhi 800
    langkah dengan effective batch 16.
"""))

cells.append(code("""
    from datasets import load_dataset

    sumber = load_dataset("Ichsan2895/alpaca-gpt4-indonesian", split="train")
    print("Baris mentah :", len(sumber), "| kolom:", sumber.column_names)

    def layak(baris):
        masuk = baris.get("input")
        keluar = baris.get("output")
        return (
            isinstance(masuk, str) and len(masuk.strip()) >= 8
            and isinstance(keluar, str) and len(keluar.strip()) >= 25
        )

    tersaring = sumber.filter(layak)
    ambil = min(UKURAN_SUBSET, len(tersaring))
    data_latih = tersaring.shuffle(seed=SEED).select(range(ambil))

    print("Setelah disaring :", len(tersaring))
    print("Dipakai melatih  :", len(data_latih))
    print("Cuplikan input   :", data_latih[0]["input"][:110], "...")
"""))

# ---------------------------------------------------------------------------
# Chat template ChatML + bukti special token
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 6. Terapkan Chat Template ChatML (Bukti Special Token)

    Qwen2.5-Instruct memakai format **ChatML**. Kita atur template lewat
    `unsloth.chat_templates.get_chat_template(chat_template="qwen-2.5")`, lalu
    setiap baris dipetakan dengan `datasets.map()` menjadi kolom `text`. Cetakan
    di bawah harus memperlihatkan token spesial ChatML — `<|im_start|>` dan
    `<|im_end|>` — sebagai bukti template benar-benar diterapkan sebelum melatih.
"""))

cells.append(code("""
    from unsloth.chat_templates import get_chat_template

    tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

    def ke_format_chatml(baris):
        percakapan = [
            {"role": "user", "content": baris["input"]},
            {"role": "assistant", "content": baris["output"]},
        ]
        teks = tokenizer.apply_chat_template(
            percakapan,
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": teks}

    data_terformat = data_latih.map(
        ke_format_chatml,
        remove_columns=data_latih.column_names,
    )

    contoh = data_terformat[0]["text"]
    print("=" * 72)
    print("SATU BARIS DATASET SETELAH PEMETAAN CHAT TEMPLATE (ChatML)")
    print("=" * 72)
    print(contoh)
    print("=" * 72)

    token_wajib = ["<|im_start|>", "<|im_end|>"]
    for tok in token_wajib:
        tanda = "ADA" if tok in contoh else "TIDAK ADA"
        print(f"[{tanda}] token spesial {tok}")
"""))

# ---------------------------------------------------------------------------
# SFTTrainer config
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 7. Susun SFTTrainer

    `SFTTrainer` membaca kolom `text` hasil pemetaan. Effective batch =
    `BATCH_PER_GPU * AKUMULASI_GRADIEN = 2 * 8 = 16`. Optimizer
    `paged_adamw_8bit` menekan pemakaian VRAM untuk state optimizer, dan
    penjadwal `cosine` menurunkan laju belajar secara halus hingga langkah ke-800.
"""))

cells.append(code("""
    from trl import SFTTrainer, SFTConfig

    argumen = SFTConfig(
        output_dir="/content/keluaran_sft",
        per_device_train_batch_size=BATCH_PER_GPU,
        gradient_accumulation_steps=AKUMULASI_GRADIEN,
        max_steps=JUMLAH_LANGKAH,
        learning_rate=LAJU_BELAJAR,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=25,
        optim="paged_adamw_8bit",
        weight_decay=0.01,
        seed=SEED,
        report_to="none",
        max_seq_length=PANJANG_URUTAN,
        dataset_text_field="text",
        packing=False,
        save_strategy="no",
    )

    pelatih = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=data_terformat,
        args=argumen,
    )
    print("SFTTrainer siap.")
    print("Effective batch :", BATCH_PER_GPU * AKUMULASI_GRADIEN)
    print("Total langkah   :", JUMLAH_LANGKAH)
"""))

# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 8. Jalankan Pelatihan

    Perkiraan durasi pada Colab T4 sekitar 60-90 menit untuk 800 langkah. Selama
    nilai `loss` menurun konsisten dan tidak muncul error CUDA out-of-memory,
    ketentuan Basic Kriteria 1 sudah terpenuhi.
"""))

cells.append(code("""
    statistik = pelatih.train()
    print("Pelatihan selesai.")
    print("Langkah terakhir :", pelatih.state.global_step)
    print("Loss terakhir    :", pelatih.state.log_history[-1].get("loss"))
"""))

# ---------------------------------------------------------------------------
# Merge + push
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 9. Merge Adapter dan Unggah ke Hugging Face

    Adapter LoRA digabungkan ke bobot dasar agar model bisa langsung dipakai
    inferensi tanpa PEFT. Pengunggahan memakai pola dua langkah
    (`save_pretrained_merged` lalu `HfApi().upload_folder`) untuk menghindari
    `TypeError: safe_serialization` yang muncul pada `push_to_hub_merged` versi
    Unsloth terbaru. `delete_patterns` memastikan tidak ada berkas adapter yang
    tertinggal di repositori.
"""))

cells.append(code("""
    from huggingface_hub import HfApi, create_repo

    DIR_MERGED = "/content/qwen_sft_merged"

    model.save_pretrained_merged(
        DIR_MERGED,
        tokenizer,
        save_method="merged_16bit",
    )
    print("Model tergabung disimpan di:", DIR_MERGED)

    api = HfApi()
    create_repo(repo_id=REPO_TUJUAN, private=False, exist_ok=True, token=HF_TOKEN)
    api.upload_folder(
        folder_path=DIR_MERGED,
        repo_id=REPO_TUJUAN,
        token=HF_TOKEN,
        commit_message="SFT Qwen2.5-1.5B merged_16bit - PGABL Dafina",
        delete_patterns=["adapter_config.json", "adapter_model.safetensors"],
    )
    url_model = f"https://huggingface.co/{REPO_TUJUAN}"
    print("Model terunggah:", url_model)
"""))

# ---------------------------------------------------------------------------
# link_huggingface.txt
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 10. Catat Tautan Repositori

    Berkas `link_huggingface.txt` menjadi bagian deliverable — memuat URL model
    hasil fine-tuning yang akan dipanggil kembali pada notebook RAG.
"""))

cells.append(code("""
    berkas_tautan = "/content/link_huggingface.txt"
    with open(berkas_tautan, "w", encoding="utf-8") as f:
        f.write(url_model + "\\n")

    print("Isi", berkas_tautan, ":")
    print(open(berkas_tautan, encoding="utf-8").read())
"""))

# ---------------------------------------------------------------------------
# Ringkasan
# ---------------------------------------------------------------------------
cells.append(md("""
    ## 11. Ringkasan

    | Item | Nilai |
    |------|-------|
    | Model dasar | `unsloth/Qwen2.5-1.5B-Instruct` (QLoRA 4-bit, nf4 + double quant) |
    | Adapter LoRA | r=8, alpha=32, dropout=0.05 pada `q,k,v,o,gate,up,down` (MHA + FFN) |
    | Dataset | `Ichsan2895/alpaca-gpt4-indonesian` (sub-sampel 8.000 baris) |
    | Chat template | ChatML (`get_chat_template("qwen-2.5")` + `datasets.map()`) |
    | Langkah latih | 800 (effective batch 16, penjadwal cosine) |
    | Metode unggah | `merged_16bit` via `save_pretrained_merged` + `HfApi.upload_folder` |
    | Keluaran | Repositori HF publik + `link_huggingface.txt` |

    Model publik ini dipanggil kembali sebagai *generator* pada notebook
    `RAG_submission_PGABL_Dafina_Meira_Rizkia.ipynb`.
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
print(f"Notebook Fine-tuning ditulis: {OUT}")
print(f"Jumlah cell: {len(cells)}")
